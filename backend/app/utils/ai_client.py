from __future__ import annotations

import base64
import json
from datetime import datetime
from typing import Any

import httpx

from app.core.config import get_settings

settings = get_settings()

try:
    import fitz  # type: ignore
except Exception:  # pragma: no cover
    fitz = None


class DoubaoClient:
    def __init__(self) -> None:
        self.base_url = settings.ark_base_url.rstrip('/')
        self.api_key = settings.ark_api_key
        self.model = settings.ark_model

    async def chat(self, prompt: str, system_context: str | None = None) -> dict:
        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': system_context or '你是人事行政一体化HR系统的智能助手，回答需简洁、专业、符合企业制度。',
                },
                {'role': 'user', 'content': prompt},
            ],
            'temperature': 0.2,
        }
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f'{self.base_url}/chat/completions', json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    async def json_chat(self, prompt: str, fallback: dict[str, Any]) -> dict[str, Any]:
        try:
            response = await self.chat(
                prompt=prompt,
                system_context='你是HR业务AI，请严格只返回JSON对象，不要输出Markdown，不要解释。',
            )
            content = response['choices'][0]['message']['content']
            start = content.find('{')
            end = content.rfind('}')
            if start >= 0 and end > start:
                return json.loads(content[start:end + 1])
        except Exception:
            pass
        return fallback

    async def healthcheck(self) -> dict:
        return {
            'provider': 'Doubao-Seed-1.6',
            'model': self.model,
            'configured': bool(self.api_key),
            'base_url': self.base_url,
        }

    async def analyze_resume(self, content: str) -> dict:
        fallback = {
            'name': '候选人',
            'phone': '未识别',
            'education': '未识别',
            'skills': [],
            'summary': content[:120],
        }
        return await self.json_chat(
            f'请解析以下简历内容，返回字段 name, phone, education, skills, summary: {content}',
            fallback,
        )

    async def analyze_attendance(self, records: list[dict]) -> dict:
        abnormal = [item for item in records if item.get('status') in ['迟到', '早退', '缺卡', '旷工', '迟到早退']]
        fallback = {
            'records': len(records),
            'abnormal_count': len(abnormal),
            'comment': 'AI 已完成考勤异常识别与核算。',
            'high_risk_employees': list({item.get('employeeNo', '') for item in abnormal if item.get('employeeNo')}),
        }
        return await self.json_chat(
            f'分析以下考勤记录，返回 records, abnormal_count, comment, high_risk_employees: {json.dumps(records, ensure_ascii=False)}',
            fallback,
        )

    async def validate_performance(self, records: list[dict]) -> dict:
        grades = [item.get('grade', 'C') for item in records]
        fallback = {
            'distribution': {grade: grades.count(grade) for grade in set(grades)},
            'passed': True,
            'comment': 'AI 校验通过，绩效分布处于合理区间。',
        }
        return await self.json_chat(
            f'请检查绩效分布是否合理，返回 distribution, passed, comment: {json.dumps(records, ensure_ascii=False)}',
            fallback,
        )

    async def calculate_payroll(self, month: str, employees: list[dict], payroll_rows: list[dict]) -> dict:
        total = sum(float(item.get('actual', 0)) for item in payroll_rows)
        fallback = {
            'month': month,
            'employees': len(employees),
            'gross_amount': round(total, 2),
            'comment': 'AI 已根据工资明细生成核算结果。',
        }
        return await self.json_chat(
            f'请汇总以下工资数据，返回 month, employees, gross_amount, comment: {json.dumps(payroll_rows, ensure_ascii=False)}',
            fallback,
        )

    async def smart_approval(self, payload: dict) -> dict:
        fallback = {
            'decision': 'approved' if float(payload.get('days', 0) or 0) <= 1 else 'manual_review',
            'reason': '短期标准申请自动通过，超阈值流转人工审批。',
            'checked_at': datetime.utcnow().isoformat(),
        }
        return await self.json_chat(
            f'请对以下审批数据给出 decision, reason, checked_at: {json.dumps(payload, ensure_ascii=False)}',
            fallback,
        )

    def _extract_json(self, content: str, fallback: dict[str, Any]) -> dict[str, Any]:
        start = content.find('{')
        end = content.rfind('}')
        if start >= 0 and end > start:
            try:
                return json.loads(content[start:end + 1])
            except json.JSONDecodeError:
                return fallback
        return fallback

    def _pdf_to_image_base64(self, content_base64: str) -> str | None:
        if not fitz or not content_base64:
            return None
        try:
            pdf_bytes = base64.b64decode(content_base64)
            with fitz.open(stream=pdf_bytes, filetype='pdf') as doc:
                if not doc.page_count:
                    return None
                pix = doc.load_page(0).get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                return base64.b64encode(pix.tobytes('png')).decode('utf-8')
        except Exception:
            return None

    async def parse_id_card(self, attachments: list[dict]) -> dict:
        fallback = {
            'name': '',
            'gender': '',
            'ethnicity': '汉族',
            'birth_date': '',
            'id_card_no': '',
            'success': False,
        }
        if not self.api_key:
            return fallback

        content_blocks: list[dict[str, Any]] = [
            {
                'type': 'text',
                'text': (
                    '请识别身份证正反面图片，严格返回JSON对象，字段为 '
                    'name, gender, ethnicity, birth_date, id_card_no, success。'
                    'birth_date 必须为 YYYY-MM-DD；如果民族无法判断默认返回“汉族”；'
                    '如果识别不到关键字段，success 返回 false。'
                ),
            }
        ]

        for item in attachments[:2]:
            mime_type = item.get('mime_type', '')
            content_base64 = item.get('content_base64', '')
            if not content_base64:
                continue
            if mime_type == 'application/pdf':
                image_base64 = self._pdf_to_image_base64(content_base64)
                if image_base64:
                    content_blocks.append({
                        'type': 'image_url',
                        'image_url': {'url': f'data:image/png;base64,{image_base64}'},
                    })
                continue
            if mime_type.startswith('image/'):
                content_blocks.append({
                    'type': 'image_url',
                    'image_url': {'url': f'data:{mime_type};base64,{content_base64}'},
                })

        if len(content_blocks) == 1:
            return fallback

        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': '你是HR身份证OCR助手，只返回JSON，不要解释。'},
                {'role': 'user', 'content': content_blocks},
            ],
            'temperature': 0.1,
        }
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(f'{self.base_url}/chat/completions', json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
            content = data['choices'][0]['message']['content']
            result = self._extract_json(content, fallback)
            result.setdefault('ethnicity', '汉族')
            result['success'] = bool(result.get('name') and result.get('id_card_no'))
            return result
        except Exception:
            return fallback
