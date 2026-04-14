from datetime import datetime
from io import BytesIO
from zipfile import BadZipFile

from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from app.repositories.factory import get_repository
from app.schemas.common import PerformanceCheckPayload
from app.security.auth import require_roles
from app.services.ai_service import AIService
from app.services.rules import RuleEngine
from app.utils.responses import ok

router = APIRouter(prefix='/performance', tags=['performance'])
ai_service = AIService()
rule_engine = RuleEngine()

CYCLE_OPTIONS = ['月度', '季度', '年度']
STATUS_OPTIONS = ['待自评', '待审核', '已完成', '驳回']
WEIGHTS = {'performance': 0.6, 'attitude': 0.2, 'ability': 0.2}
GRADE_CONFIG = {
    'S': {'min': 90, 'coef': 1.5},
    'A': {'min': 80, 'coef': 1.2},
    'B': {'min': 70, 'coef': 1.0},
    'C': {'min': 60, 'coef': 0.8},
    'D': {'min': 0, 'coef': 0.5},
}
IMPORT_HEADERS = {
    'employeeNo': ['工号'],
    'name': ['姓名'],
    'department': ['部门'],
    'position': ['岗位'],
    'cycleType': ['绩效周期'],
    'assessmentYear': ['考核年份'],
    'assessmentMonth': ['考核月份'],
    'performanceScore': ['业绩指标得分'],
    'attitudeScore': ['工作态度得分'],
    'abilityScore': ['能力表现得分'],
    'totalScore': ['综合总分'],
    'grade': ['绩效等级'],
    'coefficient': ['绩效系数'],
    'selfReview': ['员工自评'],
    'managerReview': ['上级评价'],
    'status': ['考核状态'],
    'remark': ['备注'],
}


def _normalize_text(value) -> str:
    if value is None:
        return ''
    return str(value).strip()


def _to_number(value, default: float = 0.0) -> float:
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return default


def _to_int(value, default: int | None = None) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _grade_from_score(score: float) -> str:
    for name, cfg in GRADE_CONFIG.items():
        if score >= cfg['min']:
            return name
    return 'D'


def _coefficient_from_grade(grade: str) -> float:
    return float(GRADE_CONFIG.get(grade, GRADE_CONFIG['D'])['coef'])


def _calculate_total_score(record: dict) -> float:
    return round(
        _to_number(record.get('performanceScore')) * WEIGHTS['performance']
        + _to_number(record.get('attitudeScore')) * WEIGHTS['attitude']
        + _to_number(record.get('abilityScore')) * WEIGHTS['ability'],
        2,
    )


def _build_period(cycle_type: str, year: int, month: int | None) -> str:
    if cycle_type == '月度' and month:
        return f'{year}-{str(month).zfill(2)}'
    if cycle_type == '季度' and month:
        return f'{year}年Q{month}'
    return str(year)


def _employee_lookup(repository) -> dict[str, dict]:
    employees = repository.list('employees')
    return {
        _normalize_text(item.get('employee_no') or item.get('employeeNo')): item
        for item in employees
        if _normalize_text(item.get('employee_no') or item.get('employeeNo'))
    }


def _actor_profile(repository, user: dict, employee_map: dict[str, dict]) -> dict:
    matched = next((item for item in repository.list('users') if item.get('username') == user['username']), {})
    employee_no = _normalize_text(matched.get('employeeNo'))
    employee = employee_map.get(employee_no, {})
    return {
        'employeeNo': employee_no,
        'department': employee.get('department') or matched.get('department', ''),
    }


def _hydrate_performance_record(item: dict, employee_map: dict[str, dict]) -> dict:
    employee_no = _normalize_text(item.get('employeeNo') or item.get('employee_no'))
    employee = employee_map.get(employee_no, {})
    cycle_type = _normalize_text(item.get('cycleType') or item.get('periodType')) or '月度'
    assessment_year = _to_int(item.get('assessmentYear') or item.get('year'), datetime.utcnow().year) or datetime.utcnow().year
    assessment_month = _to_int(item.get('assessmentMonth') or item.get('month'))
    total_score = _to_number(item.get('totalScore') or item.get('score'))
    if total_score == 0 and any([item.get('performanceScore'), item.get('attitudeScore'), item.get('abilityScore')]):
        total_score = _calculate_total_score(item)
    grade = _normalize_text(item.get('grade')) or _grade_from_score(total_score)
    return {
        **item,
        'employeeNo': employee_no or item.get('employeeNo', ''),
        'name': item.get('name') or employee.get('name', ''),
        'department': item.get('department') or employee.get('department', ''),
        'position': item.get('position') or employee.get('position', ''),
        'cycleType': cycle_type if cycle_type in CYCLE_OPTIONS else '月度',
        'assessmentYear': assessment_year,
        'assessmentMonth': assessment_month,
        'performanceScore': _to_number(item.get('performanceScore')),
        'attitudeScore': _to_number(item.get('attitudeScore')),
        'abilityScore': _to_number(item.get('abilityScore')),
        'totalScore': total_score,
        'score': total_score,
        'grade': grade if grade in GRADE_CONFIG else _grade_from_score(total_score),
        'coefficient': _to_number(item.get('coefficient'), _coefficient_from_grade(grade)),
        'indicators': item.get('indicators') or [],
        'selfReview': _normalize_text(item.get('selfReview')),
        'managerReview': _normalize_text(item.get('managerReview')),
        'status': _normalize_text(item.get('status')) or '待自评',
        'reviewer': _normalize_text(item.get('reviewer')),
        'remark': _normalize_text(item.get('remark')),
        'period': _build_period(cycle_type, assessment_year, assessment_month),
    }


def _validate_row(row: dict) -> None:
    if not row.get('employeeNo'):
        raise HTTPException(status_code=400, detail='工号不能为空')
    if not 0 <= _to_number(row.get('totalScore')) <= 100:
        raise HTTPException(status_code=400, detail='综合总分必须在0-100之间')
    if row.get('cycleType') == '月度' and not row.get('assessmentMonth'):
        raise HTTPException(status_code=400, detail='月度绩效必须选择考核月份')
    if row.get('cycleType') != '月度':
        row['assessmentMonth'] = None
    if row.get('status') not in STATUS_OPTIONS:
        raise HTTPException(status_code=400, detail='考核状态不合法')
    if row.get('grade') not in GRADE_CONFIG:
        raise HTTPException(status_code=400, detail='绩效等级不合法')
    if _to_number(row.get('coefficient')) <= 0:
        raise HTTPException(status_code=400, detail='绩效系数不合法')


def _scope_rows(rows: list[dict], user: dict, actor: dict) -> list[dict]:
    if user['role'] == 'employee':
        return [row for row in rows if row.get('employeeNo') == actor.get('employeeNo')]
    if user['role'] == 'manager':
        return [row for row in rows if row.get('department') == actor.get('department')]
    return rows


def _filter_rows(rows: list[dict], keyword: str = '', department: str = '', position: str = '', cycle_type: str = '', assessment_year: int | None = None, assessment_month: int | None = None, status: str = '') -> list[dict]:
    text = _normalize_text(keyword).lower()
    result = []
    for row in rows:
        if text and text not in str(row.get('employeeNo', '')).lower() and text not in str(row.get('name', '')).lower():
            continue
        if department and row.get('department') != department:
            continue
        if position and row.get('position') != position:
            continue
        if cycle_type and row.get('cycleType') != cycle_type:
            continue
        if assessment_year is not None and row.get('assessmentYear') != assessment_year:
            continue
        if assessment_month is not None and row.get('assessmentMonth') != assessment_month:
            continue
        if status and row.get('status') != status:
            continue
        result.append(row)
    return result


def _log_ai_action(repository, action: str, user: dict, payload: dict, result: dict) -> None:
    repository.upsert('ai_logs', {
        'module': 'performance',
        'action': action,
        'operator': user.get('username', ''),
        'role': user.get('role', ''),
        'payload': payload,
        'result': result,
        'loggedAt': datetime.utcnow().isoformat(),
    })


def _performance_history(repository, employee_no: str, current_id: str | None = None) -> list[dict]:
    employee_map = _employee_lookup(repository)
    rows = [_hydrate_performance_record(item, employee_map) for item in repository.list('performance')]
    history = [row for row in rows if row.get('employeeNo') == employee_no and row.get('id') != current_id]
    history.sort(key=lambda item: (item.get('assessmentYear', 0), item.get('assessmentMonth') or 0), reverse=True)
    return history[:6]


def _forbidden(detail: str = '当前角色无访问权限') -> HTTPException:
    return HTTPException(status_code=403, detail=detail)


def _ensure_record_scope(row: dict | None, user: dict, actor: dict, detail: str = '当前角色无访问权限') -> None:
    if row and not _scope_rows([row], user, actor):
        raise _forbidden(detail)


def _ensure_roles(user: dict, roles: tuple[str, ...], detail: str) -> None:
    if user.get('role') not in roles:
        raise _forbidden(detail)


def _ai_can_generate_indicators(user: dict) -> None:
    _ensure_roles(user, ('manager', 'hr'), '仅部门经理与HR可使用AI生成考核指标')


def _ai_can_auto_score(user: dict) -> None:
    _ensure_roles(user, ('manager', 'hr'), '仅部门经理与HR可使用AI智能评分')


def _ai_can_diagnose(user: dict) -> None:
    _ensure_roles(user, ('manager', 'hr', 'boss'), '当前角色无权限使用AI绩效异常诊断')


def _ai_can_generate_report(user: dict) -> None:
    _ensure_roles(user, ('manager', 'hr', 'boss'), '当前角色无权限生成AI绩效汇总报表')


def _ai_can_review_appeal(user: dict) -> None:
    _ensure_roles(user, ('manager', 'hr', 'boss'), '当前角色无权限使用AI申诉审核')


def _build_report_snapshot(rows: list[dict]) -> dict:
    scores = [float(item.get('totalScore') or item.get('score') or 0) for item in rows]
    average_score = round(sum(scores) / len(scores), 2) if scores else 0
    pass_count = len([score for score in scores if score >= 70])
    distribution = {grade: 0 for grade in ['S', 'A', 'B', 'C', 'D']}
    department_summary: dict[str, dict] = {}
    for row in rows:
        grade = _normalize_text(row.get('grade')) or _grade_from_score(float(row.get('totalScore') or row.get('score') or 0))
        if grade in distribution:
            distribution[grade] += 1
        dept = _normalize_text(row.get('department')) or '未分配部门'
        bucket = department_summary.setdefault(dept, {'department': dept, 'count': 0, 'totalScore': 0.0, 'employees': []})
        score = float(row.get('totalScore') or row.get('score') or 0)
        bucket['count'] += 1
        bucket['totalScore'] += score
        bucket['employees'].append({'name': row.get('name', ''), 'score': round(score, 2), 'grade': grade, 'position': row.get('position', '')})
    department_comparison = []
    for item in department_summary.values():
        avg = round(item['totalScore'] / item['count'], 2) if item['count'] else 0
        department_comparison.append({'department': item['department'], 'count': item['count'], 'averageScore': avg})
    department_comparison.sort(key=lambda item: item['averageScore'], reverse=True)
    sorted_rows = sorted(rows, key=lambda item: float(item.get('totalScore') or item.get('score') or 0), reverse=True)
    excellent_cases = [
        {
            'name': item.get('name', ''),
            'department': item.get('department', ''),
            'score': round(float(item.get('totalScore') or item.get('score') or 0), 2),
            'grade': item.get('grade', ''),
        }
        for item in sorted_rows[:3]
    ]
    improvement_cases = [
        {
            'name': item.get('name', ''),
            'department': item.get('department', ''),
            'score': round(float(item.get('totalScore') or item.get('score') or 0), 2),
            'grade': item.get('grade', ''),
        }
        for item in sorted(rows, key=lambda item: float(item.get('totalScore') or item.get('score') or 0))[:3]
    ]
    return {
        'recordCount': len(rows),
        'averageScore': average_score,
        'passRate': round((pass_count / len(rows) * 100), 2) if rows else 0,
        'distribution': distribution,
        'departmentComparison': department_comparison,
        'excellentCases': excellent_cases,
        'improvementCases': improvement_cases,
    }


@router.get('/options')
def get_performance_options(user=Depends(require_roles('employee', 'manager', 'hr', 'boss'))):
    repository = get_repository()
    return ok({
        'cycleOptions': CYCLE_OPTIONS,
        'statusOptions': STATUS_OPTIONS,
        'weights': WEIGHTS,
        'gradeConfig': GRADE_CONFIG,
        'employeeOptions': [
            {
                'employeeNo': _normalize_text(item.get('employee_no') or item.get('employeeNo')),
                'name': item.get('name', ''),
                'department': item.get('department', ''),
                'position': item.get('position', ''),
            }
            for item in repository.list('employees')
            if _normalize_text(item.get('employee_no') or item.get('employeeNo'))
        ],
        'approverOptions': [
            {'username': item.get('username', ''), 'name': item.get('name', ''), 'role': item.get('role', '')}
            for item in repository.list('users')
        ],
    })


@router.get('/list')
def get_performance_list(
    keyword: str = '',
    department: str = '',
    position: str = '',
    cycleType: str = '',
    assessmentYear: int | None = None,
    assessmentMonth: int | None = None,
    status: str = '',
    page: int = 1,
    pageSize: int = 10,
    user=Depends(require_roles('employee', 'manager', 'hr', 'boss')),
):
    repository = get_repository()
    employee_map = _employee_lookup(repository)
    actor = _actor_profile(repository, user, employee_map)
    rows = [_hydrate_performance_record(item, employee_map) for item in repository.list('performance')]
    rows = _filter_rows(_scope_rows(rows, user, actor), keyword, department, position, cycleType, assessmentYear, assessmentMonth, status)
    rows.sort(key=lambda item: (item.get('assessmentYear', 0), item.get('assessmentMonth') or 0, item.get('updated_at', '')), reverse=True)
    total = len(rows)
    start = max(page - 1, 0) * pageSize
    return ok({'records': rows[start:start + pageSize], 'total': total, 'page': page, 'pageSize': pageSize})


@router.get('/summary')
def get_performance_summary(user=Depends(require_roles('employee', 'manager', 'hr', 'boss'))):
    repository = get_repository()
    employee_map = _employee_lookup(repository)
    actor = _actor_profile(repository, user, employee_map)
    rows = [_hydrate_performance_record(row, employee_map) for row in repository.list('performance')]
    rows = _scope_rows(rows, user, actor)
    return ok({'records': rows, 'cycle': '2026-04', 'rules': rule_engine.validate_performance_distribution(rows)})


@router.get('/{record_id}/detail')
def get_performance_detail(record_id: str, user=Depends(require_roles('employee', 'manager', 'hr', 'boss'))):
    repository = get_repository()
    record = repository.get('performance', record_id)
    if not record:
        raise HTTPException(status_code=404, detail='绩效记录不存在')
    employee_map = _employee_lookup(repository)
    actor = _actor_profile(repository, user, employee_map)
    row = _hydrate_performance_record(record, employee_map)
    if not _scope_rows([row], user, actor):
        raise HTTPException(status_code=403, detail='当前角色无访问权限')
    return ok(row)


@router.post('/create')
def create_performance(payload: dict = Body(...), user=Depends(require_roles('hr', 'boss'))):
    repository = get_repository()
    employee_map = _employee_lookup(repository)
    row = _hydrate_performance_record(payload, employee_map)
    if row.get('employeeNo') not in employee_map:
        raise HTTPException(status_code=400, detail='工号不存在，无法关联员工档案')
    if _to_number(row.get('totalScore')) == 0 and any([row.get('performanceScore'), row.get('attitudeScore'), row.get('abilityScore')]):
        row['totalScore'] = _calculate_total_score(row)
        row['score'] = row['totalScore']
        row['grade'] = row.get('grade') or _grade_from_score(row['totalScore'])
        row['coefficient'] = row.get('coefficient') or _coefficient_from_grade(row['grade'])
    _validate_row(row)
    return ok(repository.upsert('performance', row), '绩效创建成功')


@router.put('/{record_id}')
def update_performance(record_id: str, payload: dict = Body(...), user=Depends(require_roles('hr', 'boss'))):
    repository = get_repository()
    current = repository.get('performance', record_id)
    if not current:
        raise HTTPException(status_code=404, detail='绩效记录不存在')
    current_no = _normalize_text(current.get('employeeNo') or current.get('employee_no'))
    target_no = _normalize_text(payload.get('employeeNo') or payload.get('employee_no'))
    if target_no and target_no != current_no:
        raise HTTPException(status_code=400, detail='编辑时不允许修改工号')
    employee_map = _employee_lookup(repository)
    row = _hydrate_performance_record({**current, **payload, 'id': record_id, 'employeeNo': current_no}, employee_map)
    if _to_number(row.get('totalScore')) == 0 and any([row.get('performanceScore'), row.get('attitudeScore'), row.get('abilityScore')]):
        row['totalScore'] = _calculate_total_score(row)
        row['score'] = row['totalScore']
    _validate_row(row)
    return ok(repository.upsert('performance', row), '绩效更新成功')


@router.delete('/{record_id}')
def delete_performance(record_id: str, user=Depends(require_roles('hr', 'boss'))):
    repository = get_repository()
    if not repository.delete('performance', record_id):
        raise HTTPException(status_code=404, detail='绩效记录不存在')
    return ok(message='绩效删除成功')


@router.get('/export')
def export_performance(
    keyword: str = '',
    department: str = '',
    position: str = '',
    cycleType: str = '',
    assessmentYear: int | None = None,
    assessmentMonth: int | None = None,
    status: str = '',
    user=Depends(require_roles('hr', 'boss')),
):
    repository = get_repository()
    employee_map = _employee_lookup(repository)
    actor = _actor_profile(repository, user, employee_map)
    rows = [_hydrate_performance_record(item, employee_map) for item in repository.list('performance')]
    rows = _filter_rows(_scope_rows(rows, user, actor), keyword, department, position, cycleType, assessmentYear, assessmentMonth, status)
    return ok({
        'fileName': f"绩效报表_{cycleType or '全部'}_{assessmentYear or '全部'}_{assessmentMonth or '全部'}",
        'records': [
            {
                '工号': item.get('employeeNo', ''),
                '姓名': item.get('name', ''),
                '部门': item.get('department', ''),
                '岗位': item.get('position', ''),
                '绩效周期': item.get('cycleType', ''),
                '考核年份': item.get('assessmentYear', ''),
                '考核月份': item.get('assessmentMonth', ''),
                '业绩指标得分': item.get('performanceScore', 0),
                '工作态度得分': item.get('attitudeScore', 0),
                '能力表现得分': item.get('abilityScore', 0),
                '综合总分': item.get('totalScore', 0),
                '绩效等级': item.get('grade', ''),
                '绩效系数': item.get('coefficient', 0),
                '考核状态': item.get('status', ''),
                '备注': item.get('remark', ''),
            }
            for item in rows
        ],
    })


def _match_headers(headers: list[str]) -> dict[str, str]:
    result = {}
    for field, aliases in IMPORT_HEADERS.items():
        for alias in aliases:
            if alias in headers:
                result[field] = alias
                break
    return result


def _parse_import(content: bytes, cycle_type: str, assessment_year: int, assessment_month: int | None) -> dict:
    workbook = load_workbook(filename=BytesIO(content), data_only=True)
    rows = list(workbook.active.iter_rows(values_only=True))
    if not rows:
        return {'records': [], 'errors': [{'row': '', 'message': 'Excel内容为空'}], 'matched_fields': {}, 'total_count': 0, 'success_count': 0, 'error_count': 1}
    headers = [str(cell).strip() if cell is not None else '' for cell in rows[0]]
    mapping = _match_headers(headers)
    missing = [field for field in IMPORT_HEADERS if field not in mapping and field != 'assessmentMonth']
    if missing:
        return {'records': [], 'errors': [{'row': '', 'message': f"缺少字段: {', '.join(missing)}"}], 'matched_fields': mapping, 'total_count': 0, 'success_count': 0, 'error_count': 1}
    records, errors = [], []
    for row_index, row in enumerate(rows[1:], start=2):
        payload = {}
        for field, header in mapping.items():
            index = headers.index(header)
            payload[field] = row[index] if index < len(row) else None
        employee_no = _normalize_text(payload.get('employeeNo'))
        if not employee_no:
            errors.append({'row': row_index, 'employeeNo': '', 'message': '工号不能为空'})
            continue
        records.append({
            'employeeNo': employee_no,
            'name': _normalize_text(payload.get('name')),
            'department': _normalize_text(payload.get('department')),
            'position': _normalize_text(payload.get('position')),
            'cycleType': _normalize_text(payload.get('cycleType')) or cycle_type,
            'assessmentYear': _to_int(payload.get('assessmentYear'), assessment_year),
            'assessmentMonth': _to_int(payload.get('assessmentMonth'), assessment_month),
            'performanceScore': _to_number(payload.get('performanceScore')),
            'attitudeScore': _to_number(payload.get('attitudeScore')),
            'abilityScore': _to_number(payload.get('abilityScore')),
            'totalScore': _to_number(payload.get('totalScore')),
            'grade': _normalize_text(payload.get('grade')),
            'coefficient': _to_number(payload.get('coefficient')),
            'selfReview': _normalize_text(payload.get('selfReview')),
            'managerReview': _normalize_text(payload.get('managerReview')),
            'status': _normalize_text(payload.get('status')) or '待自评',
            'remark': _normalize_text(payload.get('remark')),
            'indicators': [],
        })
    return {'records': records, 'errors': errors, 'matched_fields': mapping, 'total_count': len(records) + len(errors), 'success_count': len(records), 'error_count': len(errors)}


@router.post('/import/parse')
async def parse_performance_import(
    file: UploadFile = File(...),
    cycleType: str = Query(default='月度'),
    assessmentYear: int = Query(default=datetime.utcnow().year),
    assessmentMonth: int | None = Query(default=None),
    user=Depends(require_roles('hr', 'boss')),
):
    if not file.filename or not file.filename.lower().endswith('.xlsx'):
        raise HTTPException(status_code=400, detail='仅支持 .xlsx 文件')
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail='上传文件为空')
    try:
        repository = get_repository()
        employee_map = _employee_lookup(repository)
        parsed = _parse_import(content, cycleType, assessmentYear, assessmentMonth)
        rows, errors = [], list(parsed['errors'])
        for item in parsed['records']:
            row = _hydrate_performance_record(item, employee_map)
            if row.get('employeeNo') not in employee_map:
                errors.append({'row': '', 'employeeNo': row.get('employeeNo', ''), 'message': '工号不存在，无法关联员工档案'})
                continue
            if _to_number(row.get('totalScore')) == 0 and any([row.get('performanceScore'), row.get('attitudeScore'), row.get('abilityScore')]):
                row['totalScore'] = _calculate_total_score(row)
                row['score'] = row['totalScore']
                row['grade'] = row.get('grade') or _grade_from_score(row['totalScore'])
                row['coefficient'] = row.get('coefficient') or _coefficient_from_grade(row['grade'])
            rows.append(row)
        parsed.update({'records': rows, 'errors': errors, 'success_count': len(rows), 'error_count': len(errors), 'total_count': len(rows) + len(errors)})
        return ok({'fileName': file.filename, 'parsed': parsed}, '绩效文件解析完成')
    except (InvalidFileException, BadZipFile) as exc:
        raise HTTPException(status_code=400, detail='Excel 文件格式异常，请上传 .xlsx 模板文件') from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'绩效文件解析失败: {exc}') from exc


@router.post('/import/confirm')
def confirm_performance_import(payload: dict = Body(...), user=Depends(require_roles('hr', 'boss'))):
    repository = get_repository()
    employee_map = _employee_lookup(repository)
    stored = []
    for item in payload.get('records') or []:
        row = _hydrate_performance_record(item, employee_map)
        if not row.get('employeeNo'):
            continue
        _validate_row(row)
        stored.append(repository.upsert('performance', row))
    repository.upsert('performance_imports', {
        'cycleType': payload.get('cycleType', '月度'),
        'assessmentYear': payload.get('assessmentYear'),
        'assessmentMonth': payload.get('assessmentMonth'),
        'importedCount': len(stored),
        'errors': payload.get('errors') or [],
        'status': '已导入',
    })
    return ok({'records': stored}, '绩效导入成功')


@router.post('/check')
async def check_performance_payload(payload: PerformanceCheckPayload, user=Depends(require_roles('manager', 'hr', 'boss'))):
    normalized = []
    repository = get_repository()
    employee_map = _employee_lookup(repository)
    for item in payload.records:
        row = _hydrate_performance_record(item, employee_map)
        score = _to_number(row.get('totalScore') or row.get('score'))
        grade = row.get('grade') or _grade_from_score(score)
        normalized.append({**row, 'grade': grade, 'score': score})
        if row.get('employeeNo'):
            repository.upsert('performance', {**row, 'grade': grade, 'score': score, 'period': payload.cycle})
    result = await ai_service.performance_check(normalized)
    return ok(result, 'AI 校验完成')


@router.post('/ai/generate-indicators')
async def generate_ai_indicators(payload: dict = Body(...), user=Depends(require_roles('employee', 'manager', 'hr', 'boss'))):
    repository = get_repository()
    _ai_can_generate_indicators(user)
    employee_map = _employee_lookup(repository)
    actor = _actor_profile(repository, user, employee_map)
    target_employee_no = _normalize_text(payload.get('employeeNo'))
    if user.get('role') == 'manager':
        if not target_employee_no:
            raise _forbidden('部门经理生成AI考核指标时必须指定本部门员工')
        target_row = _hydrate_performance_record({'employeeNo': target_employee_no}, employee_map)
        _ensure_record_scope(target_row, user, actor, '部门经理仅可为本部门员工生成AI考核指标')
    try:
        result = await ai_service.generate_performance_indicators(_normalize_text(payload.get('department')), _normalize_text(payload.get('position')))
        _log_ai_action(repository, 'generate-indicators', user, payload, result)
        return ok(result, 'AI 指标生成完成')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'AI 指标生成失败: {exc}') from exc


@router.post('/ai/auto-score')
async def auto_score_ai(payload: dict = Body(...), user=Depends(require_roles('employee', 'manager', 'hr', 'boss'))):
    repository = get_repository()
    _ai_can_auto_score(user)
    employee_map = _employee_lookup(repository)
    actor = _actor_profile(repository, user, employee_map)
    target_row = None
    if payload.get('employeeNo'):
        target_row = _hydrate_performance_record(payload, employee_map)
        _ensure_record_scope(target_row, user, actor)
    try:
        result = await ai_service.auto_score_performance(payload)
        _log_ai_action(repository, 'auto-score', user, payload, result)
        return ok(result, 'AI 智能评分完成')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'AI 智能评分失败: {exc}') from exc


@router.post('/ai/generate-comment')
async def generate_ai_comment(payload: dict = Body(...), user=Depends(require_roles('employee', 'manager', 'hr', 'boss'))):
    repository = get_repository()
    employee_map = _employee_lookup(repository)
    actor = _actor_profile(repository, user, employee_map)
    comment_type = _normalize_text(payload.get('commentType')) or 'self'
    target_employee_no = _normalize_text(payload.get('employeeNo'))
    target_row = _hydrate_performance_record(payload, employee_map) if target_employee_no else None

    if user.get('role') == 'employee':
        if comment_type != 'self' or target_employee_no != actor.get('employeeNo'):
            raise _forbidden('员工仅可生成本人自评')
    elif user.get('role') == 'manager':
        if comment_type != 'manager':
            raise _forbidden('部门经理仅可生成本部门下属上级评语')
        _ensure_record_scope(target_row, user, actor, '部门经理仅可生成本部门下属上级评语')
    else:
        raise _forbidden('当前角色无权限生成AI绩效评语')

    try:
        result = await ai_service.generate_performance_comment(payload)
        _log_ai_action(repository, 'generate-comment', user, payload, result)
        return ok(result, 'AI 评语生成完成')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'AI 评语生成失败: {exc}') from exc


@router.post('/ai/diagnose')
async def diagnose_ai_performance(payload: dict = Body(...), user=Depends(require_roles('employee', 'manager', 'hr', 'boss'))):
    repository = get_repository()
    _ai_can_diagnose(user)
    employee_map = _employee_lookup(repository)
    actor = _actor_profile(repository, user, employee_map)
    current = None
    if payload.get('recordId'):
        current_record = repository.get('performance', payload['recordId'])
        if current_record:
            current = _hydrate_performance_record(current_record, employee_map)
    _ensure_record_scope(current, user, actor)
    employee_no = _normalize_text(payload.get('employeeNo') or (current or {}).get('employeeNo') or actor.get('employeeNo'))
    history = _performance_history(repository, employee_no, (current or {}).get('id')) if employee_no else []
    if user.get('role') == 'manager':
        history = _scope_rows(history, user, actor)
    ai_payload = {**payload, 'current': current or payload.get('current') or {}, 'history': history}
    try:
        result = await ai_service.diagnose_performance(ai_payload)
        repository.upsert('performance_ai_reports', {'employeeNo': employee_no, 'recordId': (current or {}).get('id', ''), 'type': 'diagnose', 'report': result})
        _log_ai_action(repository, 'diagnose', user, payload, result)
        return ok(result, 'AI 诊断报告生成完成')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'AI 诊断失败: {exc}') from exc


@router.post('/ai/generate-report')
async def generate_ai_report(payload: dict = Body(...), user=Depends(require_roles('employee', 'manager', 'hr', 'boss'))):
    repository = get_repository()
    _ai_can_generate_report(user)
    employee_map = _employee_lookup(repository)
    actor = _actor_profile(repository, user, employee_map)
    filters = payload or {}
    rows = [_hydrate_performance_record(item, employee_map) for item in repository.list('performance')]
    rows = _filter_rows(_scope_rows(rows, user, actor), filters.get('keyword', ''), filters.get('department', ''), filters.get('position', ''), filters.get('cycleType', ''), filters.get('assessmentYear'), filters.get('assessmentMonth'), filters.get('status', ''))
    snapshot = _build_report_snapshot(rows)
    try:
        result = await ai_service.generate_performance_report({**filters, 'records': rows, 'snapshot': snapshot})
        repository.upsert('performance_ai_reports', {'type': 'summary-report', 'filters': filters, 'report': result, 'snapshot': snapshot, 'scopeRole': user.get('role')})
        _log_ai_action(repository, 'generate-report', user, filters, result)
        return ok(result, 'AI 部门报表生成完成')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'AI 报表生成失败: {exc}') from exc


@router.post('/ai/appeal-review')
async def review_ai_appeal(payload: dict = Body(...), user=Depends(require_roles('employee', 'manager', 'hr', 'boss'))):
    repository = get_repository()
    _ai_can_review_appeal(user)
    employee_map = _employee_lookup(repository)
    actor = _actor_profile(repository, user, employee_map)
    current = None
    if payload.get('recordId'):
        record = repository.get('performance', payload['recordId'])
        if record:
            current = _hydrate_performance_record(record, employee_map)
    _ensure_record_scope(current, user, actor)
    employee_no = _normalize_text(payload.get('employeeNo') or (current or {}).get('employeeNo'))
    history = _performance_history(repository, employee_no, (current or {}).get('id')) if employee_no else []
    if user.get('role') == 'manager':
        history = _scope_rows(history, user, actor)
    try:
        result = await ai_service.review_performance_appeal({**payload, 'current': current or {}, 'history': history})
        repository.upsert('performance_ai_reports', {'employeeNo': employee_no, 'recordId': (current or {}).get('id', ''), 'type': 'appeal-review', 'report': result})
        _log_ai_action(repository, 'appeal-review', user, payload, result)
        return ok(result, 'AI 申诉审核完成')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'AI 申诉审核失败: {exc}') from exc


