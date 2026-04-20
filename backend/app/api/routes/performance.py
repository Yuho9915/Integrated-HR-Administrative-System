from datetime import datetime
from zipfile import BadZipFile

from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile
from openpyxl.utils.exceptions import InvalidFileException

from app.performance.ai_services import (
    auto_score,
    check_performance_payload as run_check_performance_payload,
    diagnose,
    generate_comment,
    generate_report,
    review_appeal,
)
from app.performance.constants import CYCLE_OPTIONS, GRADE_CONFIG, STATUS_OPTIONS, WEIGHTS
from app.performance.import_export import confirm_import_records, export_dataset, parse_import_result
from app.performance.mappers import (
    actor_profile,
    calculate_total_score,
    coefficient_from_grade,
    employee_lookup,
    grade_from_score,
    hydrate_performance_record,
    normalize_text,
    to_int,
    to_number,
)
from app.performance.permissions import ensure_record_scope, scope_rows
from app.performance.queries import filter_rows
from app.performance.validators import (
    assert_employee_submission_window,
    assert_no_duplicate_employee_submission,
    ensure_status_transition,
    validate_row,
)
from app.repositories.factory import get_repository
from app.schemas.common import PerformanceCheckPayload
from app.security.auth import require_roles
from app.services.ai_service import AIService
from app.services.rules import RuleEngine
from app.utils.responses import ok

router = APIRouter(prefix='/performance', tags=['performance'])
ai_service = AIService()
rule_engine = RuleEngine()


def __employee_edit_fields(payload: dict, current: dict) -> dict:
    return {
        'cycleType': payload.get('cycleType', current.get('cycleType')),
        'assessmentYear': payload.get('assessmentYear', current.get('assessmentYear')),
        'assessmentMonth': payload.get('assessmentMonth', current.get('assessmentMonth')),
        'monthlyWorkContent': payload.get('monthlyWorkContent', current.get('monthlyWorkContent')),
        'achievementHighlights': payload.get('achievementHighlights', current.get('achievementHighlights')),
        'selfReview': payload.get('selfReview', current.get('selfReview')),
        'remark': payload.get('remark', current.get('remark')),
        'status': payload.get('status') or '待经理审核',
    }


def __manager_edit_fields(payload: dict, user: dict, current: dict) -> dict:
    return {
        'performanceScore': payload.get('performanceScore', current.get('performanceScore')),
        'attitudeScore': payload.get('attitudeScore', current.get('attitudeScore')),
        'abilityScore': payload.get('abilityScore', current.get('abilityScore')),
        'totalScore': payload.get('totalScore', current.get('totalScore')),
        'grade': payload.get('grade', current.get('grade')),
        'coefficient': payload.get('coefficient', current.get('coefficient')),
        'managerReview': payload.get('managerReview', current.get('managerReview')),
        'reviewer': user.get('username'),
        'status': payload.get('status') or '待HR审核',
    }


def __hr_edit_fields(payload: dict, user: dict, current: dict) -> dict:
    return {
        'status': payload.get('status') or '已确认发布',
        'reviewer': user.get('username'),
        'remark': payload.get('remark', current.get('remark')),
    }


@router.get('/options')
def get_performance_options(user=Depends(require_roles('employee', 'manager', 'hr'))):
    repository = get_repository()
    return ok({
        'cycleOptions': CYCLE_OPTIONS,
        'statusOptions': STATUS_OPTIONS,
        'weights': WEIGHTS,
        'gradeConfig': GRADE_CONFIG,
        'employeeOptions': [
            {
                'employeeNo': normalize_text(item.get('employee_no') or item.get('employeeNo')),
                'name': item.get('name', ''),
                'department': item.get('department', ''),
                'position': item.get('position', ''),
            }
            for item in repository.list('employees')
            if normalize_text(item.get('employee_no') or item.get('employeeNo'))
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
    user=Depends(require_roles('employee', 'manager', 'hr')),
):
    repository = get_repository()
    employee_map = employee_lookup(repository)
    actor = actor_profile(repository, user, employee_map)
    rows = [hydrate_performance_record(item, employee_map) for item in repository.list('performance')]
    rows = filter_rows(scope_rows(rows, user, actor), keyword, department, position, cycleType, assessmentYear, assessmentMonth, status)
    rows.sort(key=lambda item: (item.get('assessmentYear', 0), item.get('assessmentMonth') or 0, item.get('updated_at', '')), reverse=True)
    total = len(rows)
    start = max(page - 1, 0) * pageSize
    return ok({'records': rows[start:start + pageSize], 'total': total, 'page': page, 'pageSize': pageSize})


@router.get('/summary')
def get_performance_summary(user=Depends(require_roles('employee', 'manager', 'hr'))):
    repository = get_repository()
    employee_map = employee_lookup(repository)
    actor = actor_profile(repository, user, employee_map)
    rows = [hydrate_performance_record(row, employee_map) for row in repository.list('performance')]
    rows = scope_rows(rows, user, actor)
    return ok({'records': rows, 'cycle': '2026-04', 'rules': rule_engine.validate_performance_distribution(rows)})


@router.get('/{record_id}/detail')
def get_performance_detail(record_id: str, user=Depends(require_roles('employee', 'manager', 'hr'))):
    repository = get_repository()
    record = repository.get('performance', record_id)
    if not record:
        raise HTTPException(status_code=404, detail='绩效记录不存在')
    employee_map = employee_lookup(repository)
    actor = actor_profile(repository, user, employee_map)
    row = hydrate_performance_record(record, employee_map)
    if not scope_rows([row], user, actor):
        raise HTTPException(status_code=403, detail='当前角色无访问权限')
    return ok(row)


@router.post('/create')
def create_performance(payload: dict = Body(...), user=Depends(require_roles('employee', 'manager', 'hr'))):
    repository = get_repository()
    employee_map = employee_lookup(repository)
    actor = actor_profile(repository, user, employee_map)

    if user.get('role') == 'employee':
        assert_employee_submission_window(payload)
        employee_no = actor.get('employeeNo')
        employee = employee_map.get(employee_no)
        if not employee:
            raise HTTPException(status_code=400, detail='当前员工档案不存在')
        assert_no_duplicate_employee_submission(repository, employee_no, to_int(payload.get('assessmentYear')) or datetime.utcnow().year, to_int(payload.get('assessmentMonth')) or datetime.utcnow().month)
        base_row = {
            'employeeNo': employee_no,
            'name': employee.get('name', ''),
            'department': employee.get('department', ''),
            'position': employee.get('position', ''),
            'cycleType': payload.get('cycleType') or '月度',
            'assessmentYear': payload.get('assessmentYear') or datetime.utcnow().year,
            'assessmentMonth': payload.get('assessmentMonth'),
            'status': '待经理审核',
            'reviewer': '',
            'performanceScore': 0,
            'attitudeScore': 0,
            'abilityScore': 0,
            'totalScore': 0,
            'grade': '',
            'coefficient': 0,
            'indicators': [],
            'managerReview': '',
        }
        row = hydrate_performance_record({**base_row, **_employee_edit_fields(payload, base_row)}, employee_map)
    else:
        row = hydrate_performance_record(payload, employee_map)
        if row.get('employeeNo') not in employee_map:
            raise HTTPException(status_code=400, detail='工号不存在，无法关联员工档案')
        if user.get('role') == 'manager' and row.get('department') != actor.get('department'):
            raise HTTPException(status_code=403, detail='部门经理仅可录入本部门绩效')

    validate_row(row)
    return ok(repository.upsert('performance', row), '绩效创建成功')


@router.put('/{record_id}')
def update_performance(record_id: str, payload: dict = Body(...), user=Depends(require_roles('employee', 'manager', 'hr'))):
    repository = get_repository()
    current = repository.get('performance', record_id)
    if not current:
        raise HTTPException(status_code=404, detail='绩效记录不存在')
    current_no = normalize_text(current.get('employeeNo') or current.get('employee_no'))
    target_no = normalize_text(payload.get('employeeNo') or payload.get('employee_no'))
    if target_no and target_no != current_no:
        raise HTTPException(status_code=400, detail='编辑时不允许修改工号')
    employee_map = employee_lookup(repository)
    actor = actor_profile(repository, user, employee_map)
    row = hydrate_performance_record(current, employee_map)
    ensure_record_scope(row, user, actor)

    if user.get('role') == 'employee':
        assert_employee_submission_window(payload)
        assert_no_duplicate_employee_submission(repository, current_no, to_int(payload.get('assessmentYear') or row.get('assessmentYear')) or datetime.utcnow().year, to_int(payload.get('assessmentMonth') or row.get('assessmentMonth')) or datetime.utcnow().month, record_id)
        if row.get('status') not in ('待员工提交', '经理退回修改', 'HR退回修改'):
            raise HTTPException(status_code=400, detail='当前状态下员工不可修改绩效内容')
        next_status = payload.get('status') or '待经理审核'
        ensure_status_transition(user, row.get('status'), next_status)
        row = hydrate_performance_record({**row, **_employee_edit_fields(payload, row), 'id': record_id, 'employeeNo': current_no}, employee_map)
    elif user.get('role') == 'manager':
        next_status = payload.get('status') or '待HR审核'
        if next_status == '待HR审核':
            required_scores = [payload.get('performanceScore', row.get('performanceScore')), payload.get('attitudeScore', row.get('attitudeScore')), payload.get('abilityScore', row.get('abilityScore'))]
            if any(value in (None, '') for value in required_scores):
                raise HTTPException(status_code=400, detail='部门经理提交前必须填写全部评分')
        ensure_status_transition(user, row.get('status'), next_status)
        row = hydrate_performance_record({**row, **_manager_edit_fields(payload, user, row), 'id': record_id, 'employeeNo': current_no}, employee_map)
        ensure_record_scope(row, user, actor, '部门经理仅可编辑本部门绩效')
    else:
        next_status = payload.get('status') or '已确认发布'
        ensure_status_transition(user, row.get('status'), next_status)
        row = hydrate_performance_record({**row, **_hr_edit_fields(payload, user, row), 'id': record_id, 'employeeNo': current_no}, employee_map)

    if any([row.get('performanceScore'), row.get('attitudeScore'), row.get('abilityScore')]):
        row['totalScore'] = calculate_total_score(row) if not to_number(payload.get('totalScore'), None) else to_number(row.get('totalScore'))
        row['score'] = row['totalScore']
        if row['totalScore'] > 0:
            row['grade'] = row.get('grade') or grade_from_score(row['totalScore'])
            row['coefficient'] = row.get('coefficient') or coefficient_from_grade(row['grade'])
    validate_row(row)
    return ok(repository.upsert('performance', row), '绩效更新成功')


@router.delete('/{record_id}')
def delete_performance(record_id: str, user=Depends(require_roles('hr'))):
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
    user=Depends(require_roles('hr')),
):
    repository = get_repository()
    employee_map = employee_lookup(repository)
    actor = actor_profile(repository, user, employee_map)
    return ok(export_dataset(repository, user, actor, keyword, department, position, cycleType, assessmentYear, assessmentMonth, status))


@router.post('/import/parse')
async def parse_performance_import(
    file: UploadFile = File(...),
    cycleType: str = Query(default='月度'),
    assessmentYear: int = Query(default=datetime.utcnow().year),
    assessmentMonth: int | None = Query(default=None),
    user=Depends(require_roles('hr')),
):
    if not file.filename or not file.filename.lower().endswith('.xlsx'):
        raise HTTPException(status_code=400, detail='仅支持 .xlsx 文件')
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail='上传文件为空')
    try:
        repository = get_repository()
        parsed = parse_import_result(content, cycleType, assessmentYear, assessmentMonth, repository)
        return ok({'fileName': file.filename, 'parsed': parsed}, '绩效文件解析完成')
    except (InvalidFileException, BadZipFile) as exc:
        raise HTTPException(status_code=400, detail='Excel 文件格式异常，请上传 .xlsx 模板文件') from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'绩效文件解析失败: {exc}') from exc


@router.post('/import/confirm')
def confirm_performance_import(payload: dict = Body(...), user=Depends(require_roles('hr'))):
    repository = get_repository()
    stored = confirm_import_records(payload, repository)
    return ok({'records': stored}, '绩效导入成功')


@router.post('/check')
async def check_performance_payload(payload: PerformanceCheckPayload, user=Depends(require_roles('manager', 'hr'))):
    repository = get_repository()
    result = await run_check_performance_payload(payload, repository, ai_service)
    return ok(result, 'AI 校验完成')


@router.post('/ai/auto-score')
async def auto_score_ai(payload: dict = Body(...), user=Depends(require_roles('employee', 'manager', 'hr'))):
    repository = get_repository()
    result = await auto_score(payload, user, repository, ai_service)
    return ok(result, 'AI 智能评分完成')


@router.post('/ai/generate-comment')
async def generate_ai_comment(payload: dict = Body(...), user=Depends(require_roles('employee', 'manager', 'hr'))):
    repository = get_repository()
    result = await generate_comment(payload, user, repository, ai_service)
    return ok(result, 'AI 评语生成完成')


@router.post('/ai/diagnose')
async def diagnose_ai_performance(payload: dict = Body(...), user=Depends(require_roles('employee', 'manager', 'hr'))):
    repository = get_repository()
    result = await diagnose(payload, user, repository, ai_service)
    return ok(result, 'AI 诊断报告生成完成')


@router.post('/ai/generate-report')
async def generate_ai_report(payload: dict = Body(...), user=Depends(require_roles('employee', 'manager', 'hr'))):
    repository = get_repository()
    result = await generate_report(payload, user, repository, ai_service)
    return ok(result, 'AI 部门报表生成完成')


@router.post('/ai/appeal-review')
async def review_ai_appeal(payload: dict = Body(...), user=Depends(require_roles('employee', 'manager', 'hr'))):
    repository = get_repository()
    result = await review_appeal(payload, user, repository, ai_service)
    return ok(result, 'AI 申诉审核完成')


