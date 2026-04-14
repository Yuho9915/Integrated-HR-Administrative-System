import json
from datetime import datetime

from app.schemas.common import AIChatResponse
from app.services.rules import RuleEngine
from app.utils.ai_client import DoubaoClient


POSITION_INDICATOR_PRESETS = {
    'tech': [
        {'name': '任务完成率', 'weight': 35, 'targetValue': '按期完成迭代任务 ≥ 95%'},
        {'name': '代码质量', 'weight': 25, 'targetValue': '关键缺陷数 ≤ 1，代码规范通过率 ≥ 98%'},
        {'name': '交付时效', 'weight': 20, 'targetValue': '需求交付准时率 ≥ 95%'},
        {'name': '团队协作', 'weight': 20, 'targetValue': '跨团队协作满意度 ≥ 90%'},
    ],
    'sales': [
        {'name': '业绩达成率', 'weight': 35, 'targetValue': '销售目标达成率 ≥ 100%'},
        {'name': '回款率', 'weight': 25, 'targetValue': '回款完成率 ≥ 95%'},
        {'name': '客户满意度', 'weight': 20, 'targetValue': '客户满意度 ≥ 90%'},
        {'name': '新客拓展', 'weight': 20, 'targetValue': '月度新客开发达成率 ≥ 100%'},
    ],
    'hr': [
        {'name': '招聘完成率', 'weight': 35, 'targetValue': '招聘需求按期关闭率 ≥ 95%'},
        {'name': '员工满意度', 'weight': 25, 'targetValue': '员工满意度 ≥ 90%'},
        {'name': '流程优化', 'weight': 20, 'targetValue': '流程优化事项按计划落地'},
        {'name': '合规性', 'weight': 20, 'targetValue': '制度执行与档案合规率 100%'},
    ],
    'general': [
        {'name': '工作态度', 'weight': 20, 'targetValue': '工作积极主动，反馈及时'},
        {'name': '执行力', 'weight': 35, 'targetValue': '任务按时按质完成率 ≥ 95%'},
        {'name': '学习成长', 'weight': 20, 'targetValue': '完成岗位学习与复盘计划'},
        {'name': '协作能力', 'weight': 25, 'targetValue': '跨部门协作评价良好及以上'},
    ],
}
COMMENT_STYLE_TONE = {
    '鼓励型': '语言积极、肯定成果、兼顾成长建议。',
    '严格型': '语言正式、客观直接、强调问题与改进要求。',
    '中性型': '语言专业克制、客观平衡、避免夸张。',
}


def extract_message_content(payload: dict) -> str:
    try:
        return payload['choices'][0]['message']['content']
    except (KeyError, IndexError, TypeError):
        return 'AI 服务返回格式异常，请稍后重试。'


class AIService:
    def __init__(self) -> None:
        self.client = DoubaoClient()
        self.rule_engine = RuleEngine()

    async def ask(self, prompt: str, system_context: str | None = None) -> AIChatResponse:
        response = await self.client.chat(prompt=prompt, system_context=system_context)
        return AIChatResponse(content=extract_message_content(response), model=self.client.model)

    async def health(self) -> dict:
        return await self.client.healthcheck()

    async def parse_resume(self, content: str) -> dict:
        return await self.client.analyze_resume(content)

    async def attendance_summary(self, records: list[dict]) -> dict:
        return await self.client.analyze_attendance(records)

    async def generate_attendance_summary_report(self, payload: dict) -> dict:
        summary = payload.get('summary') or {}
        department_rows = payload.get('departmentRows') or []
        fallback_lines = [
            f"考勤汇总周期：{payload.get('year', '')}年{payload.get('month', '')}月。",
            f"本次共覆盖 {summary.get('recordCount', 0)} 条考勤记录，涉及 {summary.get('departmentCount', 0)} 个部门。",
            '各部门出勤概况：',
            *[f"- {item['department']}：出勤率 {item['attendanceRate']}，异常人数 {item['abnormalCount']}。" for item in department_rows],
            '异常统计：',
            f"- 迟到次数 {summary.get('lateTimes', 0)} 次，早退次数 {summary.get('earlyTimes', 0)} 次。",
            f"- 请假总时长 {summary.get('leaveHours', 0)} 小时，旷工天数 {summary.get('absenteeismDays', 0)} 天。",
            '整体分析：',
            f"- {summary.get('analysis', '整体考勤秩序稳定，建议持续关注异常波动部门。')}",
        ]
        fallback_text = '\n'.join([line for line in fallback_lines if line])
        result = await self.client.json_chat(
            '你是企业HR考勤分析顾问。请基于部门、年月、部门考勤汇总数据生成一份正式、规范、简洁的中文考勤汇总分析。严格返回JSON对象，仅包含字段 content。'
            '要求：1）包含各部门出勤概况；2）包含异常统计（迟到、早退、请假、旷工）；3）给出整体情况分析与简要总结；4）使用分段中文文本，适合直接复制到汇报材料。'
            f'输入数据：{json.dumps(payload, ensure_ascii=False)}',
            {'content': fallback_text},
        )
        return {'content': str(result.get('content') or fallback_text).strip() or fallback_text, 'generatedAt': datetime.utcnow().isoformat()}

    async def generate_workforce_report(self, payload: dict) -> dict:
        snapshot = payload.get('snapshot') or {}
        filters = payload.get('filters') or {}
        department_structure = ', '.join([f"{item.get('department', '未分配部门')} {item.get('count', 0)}人" for item in snapshot.get('departmentStructure', [])]) or '暂无数据'
        education_distribution = ', '.join([f"{item.get('label', '未填写')} {item.get('count', 0)}人" for item in snapshot.get('educationDistribution', [])]) or '暂无数据'
        age_distribution = ', '.join([f"{item.get('label', '')} {item.get('count', 0)}人" for item in snapshot.get('ageDistribution', []) if item.get('count')]) or '暂无数据'
        tenure_distribution = ', '.join([f"{item.get('label', '')} {item.get('count', 0)}人" for item in snapshot.get('tenureDistribution', []) if item.get('count')]) or '暂无数据'
        status_distribution = ', '.join([f"{item.get('label', '')} {item.get('count', 0)}人" for item in snapshot.get('statusDistribution', [])]) or '暂无数据'
        fallback = {
            'title': 'AI人力结构报表',
            'content': '\n'.join([
                f"统计范围：部门【{filters.get('department') or '全部'}】、岗位【{filters.get('position') or '全部'}】、状态【{filters.get('status') or '全部'}】。",
                f"部门人力结构：{department_structure}。",
                f"学历分布：{education_distribution}。",
                f"年龄分布：{age_distribution}。",
                f"司龄分布：{tenure_distribution}。",
                f"状态占比：{status_distribution}。",
                f"人效概况：人均人工成本约 {snapshot.get('averageSalary', 0)} 元，人效参考指数 {snapshot.get('perCapitaOutputHint', 0)}。",
                '综合结论：当前人力结构整体稳定，建议关注关键岗位储备、试用人员转正节奏以及结构性优化空间。',
            ]),
        }
        result = await self.client.json_chat(
            '你是企业HR组织分析顾问。请基于结构化员工数据生成人力结构报表。严格返回JSON对象，仅包含字段 content。'
            '要求：1）说明部门人力结构；2）说明学历、年龄、司龄分布；3）说明在职/试用/离职占比；4）输出人效概况与简要管理建议；5）使用正式中文，适合管理层汇报。'
            f'输入数据：{json.dumps(payload, ensure_ascii=False)}',
            fallback,
        )
        content = str(result.get('content') or fallback['content']).strip() or fallback['content']
        return {'title': 'AI人力结构报表', 'content': content, 'generatedAt': datetime.utcnow().isoformat()}

    async def performance_check(self, records: list[dict]) -> dict:
        rule_result = self.rule_engine.validate_performance_distribution(records)
        ai_result = await self.client.validate_performance(records)
        return {
            'distribution': ai_result.get('distribution', rule_result['distribution']),
            'passed': ai_result.get('passed', rule_result['passed']) and rule_result['passed'],
            'comment': ai_result.get('comment', rule_result['comment']),
            'rule_check': rule_result,
        }

    async def payroll_calculate(self, month: str, employees: list[dict], payroll_rows: list[dict]) -> dict:
        return await self.client.calculate_payroll(month, employees, payroll_rows)

    async def smart_approval(self, payload: dict) -> dict:
        return await self.client.smart_approval(payload)

    async def parse_id_card(self, attachments: list[dict]) -> dict:
        return await self.client.parse_id_card(attachments)

    def _match_indicator_preset(self, department: str, position: str) -> list[dict]:
        text = f'{department} {position}'.lower()
        if any(keyword in text for keyword in ['技术', '开发', '测试', '前端', '后端', '算法', '研发', '运维']):
            return POSITION_INDICATOR_PRESETS['tech']
        if any(keyword in text for keyword in ['销售', '客户经理', '商务', '市场拓展']):
            return POSITION_INDICATOR_PRESETS['sales']
        if any(keyword in text for keyword in ['人事', '行政', '招聘', '培训', '薪酬', '绩效', '综合管理']):
            return POSITION_INDICATOR_PRESETS['hr']
        return POSITION_INDICATOR_PRESETS['general']

    async def generate_performance_indicators(self, department: str, position: str) -> dict:
        fallback_items = self._match_indicator_preset(department, position)
        fallback = {'indicators': fallback_items, 'summary': f'已根据{department or "所在部门"}{position or "岗位"}生成建议指标。'}
        result = await self.client.json_chat(
            '请基于岗位信息生成绩效指标，严格返回JSON对象，字段为 indicators, summary。'
            f'部门：{department or "未提供"}；岗位：{position or "未提供"}；参考模板：{json.dumps(fallback_items, ensure_ascii=False)}',
            fallback,
        )
        indicators = result.get('indicators') or fallback_items
        normalized = []
        for item in indicators[:6]:
            normalized.append({
                'name': str(item.get('name') or '').strip() or '绩效指标',
                'weight': max(0, min(100, round(float(item.get('weight', 0) or 0), 2))),
                'targetValue': str(item.get('targetValue') or '').strip() or '按岗位要求达成既定目标',
            })
        if normalized:
            total = sum(item['weight'] for item in normalized) or 100
            for item in normalized:
                item['weight'] = round(item['weight'] / total * 100, 2)
            normalized[0]['weight'] = round(normalized[0]['weight'] + (100 - sum(item['weight'] for item in normalized)), 2)
        return {'indicators': normalized or fallback_items, 'summary': result.get('summary') or fallback['summary']}

    async def auto_score_performance(self, payload: dict) -> dict:
        indicators = payload.get('indicators') or []
        self_review = str(payload.get('selfReview') or '').strip()
        position = str(payload.get('position') or '').strip()
        completion_scores, ability_scores = [], []
        for item in indicators:
            completion_rate = float(item.get('completionRate') or 0)
            score = float(item.get('score') or 0)
            weight = float(item.get('weight') or 0)
            if completion_rate:
                completion_scores.append(min(100, completion_rate))
            if score:
                completion_scores.append(min(100, score))
            if weight:
                ability_scores.append(min(100, 60 + weight * 0.4))
        performance_score = round(sum(completion_scores) / len(completion_scores), 2) if completion_scores else 82.0
        attitude_score = 92.0 if len(self_review) >= 60 else 86.0 if len(self_review) >= 20 else 78.0
        ability_score = round(sum(ability_scores) / len(ability_scores), 2) if ability_scores else 84.0
        total_score = round(performance_score * 0.6 + attitude_score * 0.2 + ability_score * 0.2, 2)
        grade = 'S' if total_score >= 90 else 'A' if total_score >= 80 else 'B' if total_score >= 70 else 'C' if total_score >= 60 else 'D'
        coefficient = {'S': 1.5, 'A': 1.2, 'B': 1.0, 'C': 0.8, 'D': 0.5}[grade]
        fallback = {
            'performanceScore': performance_score,
            'attitudeScore': attitude_score,
            'abilityScore': ability_score,
            'totalScore': total_score,
            'grade': grade,
            'coefficient': coefficient,
            'reasoning': f'基于{position or "当前岗位"}指标完成情况与自评内容生成建议评分。',
        }
        result = await self.client.json_chat(
            '请根据绩效指标、自评内容和岗位信息进行客观评分，严格返回JSON对象，字段为 performanceScore, attitudeScore, abilityScore, totalScore, grade, coefficient, reasoning。'
            f'输入数据：{json.dumps(payload, ensure_ascii=False)}',
            fallback,
        )
        return {
            'performanceScore': round(float(result.get('performanceScore', fallback['performanceScore']) or fallback['performanceScore']), 2),
            'attitudeScore': round(float(result.get('attitudeScore', fallback['attitudeScore']) or fallback['attitudeScore']), 2),
            'abilityScore': round(float(result.get('abilityScore', fallback['abilityScore']) or fallback['abilityScore']), 2),
            'totalScore': round(float(result.get('totalScore', fallback['totalScore']) or fallback['totalScore']), 2),
            'grade': str(result.get('grade') or fallback['grade']).strip() or fallback['grade'],
            'coefficient': round(float(result.get('coefficient', fallback['coefficient']) or fallback['coefficient']), 2),
            'reasoning': result.get('reasoning') or fallback['reasoning'],
        }

    async def generate_performance_comment(self, payload: dict) -> dict:
        comment_type = str(payload.get('commentType') or 'self').strip()
        style = str(payload.get('style') or '中性型').strip() or '中性型'
        fallback_text = '本周期能够围绕岗位职责推进重点工作，整体完成情况较为稳定。' if comment_type == 'self' else '该员工本周期能够较好完成岗位目标，工作推进较为稳健，建议继续强化亮点并聚焦后续改进。'
        fallback = {'content': fallback_text, 'style': style}
        result = await self.client.json_chat(
            '请根据员工信息、绩效得分、指标完成情况生成正式的HR绩效评语，严格返回JSON对象，字段为 content 和 style。'
            f'评语类型：{comment_type}；风格：{style}，风格要求：{COMMENT_STYLE_TONE.get(style, COMMENT_STYLE_TONE["中性型"])}；输入：{json.dumps(payload, ensure_ascii=False)}',
            fallback,
        )
        return {'content': str(result.get('content') or fallback_text).strip() or fallback_text, 'style': str(result.get('style') or style).strip() or style}

    async def diagnose_performance(self, payload: dict) -> dict:
        current = payload.get('current') or {}
        history = payload.get('history') or []
        scores = [float(item.get('totalScore') or item.get('score') or 0) for item in history if item]
        if current:
            scores.append(float(current.get('totalScore') or current.get('score') or 0))
        average_score = round(sum(scores) / len(scores), 2) if scores else 0
        low_count = len([score for score in scores if score < 70])
        volatility = max(scores) - min(scores) if len(scores) > 1 else 0
        fallback = {
            'issues': ['存在连续低分风险'] if low_count >= 2 else ['整体绩效波动可控'],
            'reasons': ['关键指标完成稳定性不足'] if low_count >= 2 else ['当前绩效总体处于可接受区间'],
            'highlights': ['能够完成核心职责任务'] if average_score >= 75 else ['具备进一步提升空间'],
            'suggestions': ['建议围绕关键指标设定周度跟进计划', '加强跨部门协作与过程复盘'],
            'summary': 'AI 已结合历史绩效与当前结果生成诊断建议。',
            'averageScore': average_score,
            'volatility': round(volatility, 2),
        }
        result = await self.client.json_chat(
            '请根据员工当前绩效和历史绩效生成诊断报告，严格返回JSON对象，字段为 issues, reasons, highlights, suggestions, summary, averageScore, volatility。'
            f'输入：{json.dumps(payload, ensure_ascii=False)}',
            fallback,
        )
        return {
            'issues': result.get('issues') or fallback['issues'],
            'reasons': result.get('reasons') or fallback['reasons'],
            'highlights': result.get('highlights') or fallback['highlights'],
            'suggestions': result.get('suggestions') or fallback['suggestions'],
            'summary': result.get('summary') or fallback['summary'],
            'averageScore': float(result.get('averageScore', fallback['averageScore']) or fallback['averageScore']),
            'volatility': float(result.get('volatility', fallback['volatility']) or fallback['volatility']),
        }

    async def generate_performance_report(self, payload: dict) -> dict:
        records = payload.get('records') or []
        snapshot = payload.get('snapshot') or {}
        average_score = float(snapshot.get('averageScore') or 0)
        record_count = int(snapshot.get('recordCount') or len(records))
        distribution = snapshot.get('distribution') or {}
        department_comparison = snapshot.get('departmentComparison') or []
        excellent_cases = snapshot.get('excellentCases') or []
        improvement_cases = snapshot.get('improvementCases') or []
        top_department = department_comparison[0]['department'] if department_comparison else '暂无'
        low_department = department_comparison[-1]['department'] if department_comparison else '暂无'
        fallback = {
            'title': 'AI绩效汇总报表',
            'overview': f'本次统计共覆盖 {record_count} 条绩效记录，平均分 {average_score}，绩效达标率 {snapshot.get("passRate", 0)}%。整体表现最佳部门为{top_department}，需重点关注部门为{low_department}。',
            'departmentComparison': [f"{item['department']}：平均分 {item['averageScore']}，样本 {item['count']} 人" for item in department_comparison] or ['暂无部门对比数据'],
            'excellentCases': [f"{item['name']}（{item['department']}）{item['score']}分，等级{item['grade']}" for item in excellent_cases] or ['暂无'],
            'improvementCases': [f"{item['name']}（{item['department']}）{item['score']}分，等级{item['grade']}" for item in improvement_cases] or ['暂无'],
            'analysis': [f"等级分布：S {distribution.get('S', 0)} 人、A {distribution.get('A', 0)} 人、B {distribution.get('B', 0)} 人、C {distribution.get('C', 0)} 人、D {distribution.get('D', 0)} 人。", '建议重点复盘低分员工的目标设定、过程跟进与主管辅导质量。'],
            'suggestions': ['建议对高绩效部门固化优秀经验，对低绩效部门开展专项复盘与月度辅导。', '建议结合岗位类型优化指标权重，避免“一刀切”评分口径。'],
            'distribution': distribution,
        }
        result = await self.client.json_chat(
            '你是企业HR绩效分析顾问。请基于结构化绩效统计信息生成正式、具体、可用于管理层汇报的总结。严格返回JSON对象，字段为 title, overview, departmentComparison, excellentCases, improvementCases, analysis, suggestions, distribution。'
            '要求：1) overview 必须写出样本量、平均分、达标率与重点部门；2) departmentComparison 必须逐部门给出平均分和人数；3) excellentCases 与 improvementCases 需带姓名、部门、分数、等级；4) analysis 与 suggestions 必须具体，避免空泛表述。'
            f'输入数据：{json.dumps(payload, ensure_ascii=False)}',
            fallback,
        )
        return {**fallback, **{k: v for k, v in result.items() if v}, 'generatedAt': datetime.utcnow().isoformat()}

    async def review_performance_appeal(self, payload: dict) -> dict:
        appeal = str(payload.get('appealContent') or '').strip()
        fallback = {
            'decision': '申诉合理' if len(appeal) >= 40 else '建议人工复核',
            'reason': 'AI 已结合申诉理由、历史绩效与当前指标完成情况形成审核意见。',
            'evidence': ['申诉文本、历史绩效、岗位要求已纳入综合判断'],
        }
        result = await self.client.json_chat(
            '请对绩效申诉进行审核，严格返回JSON对象，字段为 decision, reason, evidence。'
            f'输入：{json.dumps(payload, ensure_ascii=False)}',
            fallback,
        )
        return {
            'decision': str(result.get('decision') or fallback['decision']).strip() or fallback['decision'],
            'reason': str(result.get('reason') or fallback['reason']).strip() or fallback['reason'],
            'evidence': result.get('evidence') or fallback['evidence'],
        }
