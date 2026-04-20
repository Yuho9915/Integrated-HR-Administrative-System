from datetime import datetime

from fastapi import HTTPException

from app.performance.constants import GRADE_CONFIG, STATUS_OPTIONS
from app.performance.mappers import normalize_text, to_int, to_number


def validate_row(row: dict) -> None:
    if not row.get('employeeNo'):
        raise HTTPException(status_code=400, detail='工号不能为空')
    if row.get('cycleType') == '月度' and not row.get('assessmentMonth'):
        raise HTTPException(status_code=400, detail='月度绩效必须选择考核月份')
    if row.get('cycleType') != '月度':
        row['assessmentMonth'] = None
    if row.get('status') not in STATUS_OPTIONS:
        raise HTTPException(status_code=400, detail='考核状态不合法')
    if row.get('grade') and row.get('grade') not in GRADE_CONFIG:
        raise HTTPException(status_code=400, detail='绩效等级不合法')
    if row.get('coefficient') is not None and to_number(row.get('coefficient')) < 0:
        raise HTTPException(status_code=400, detail='绩效系数不合法')


def assert_employee_submission_window(payload: dict) -> None:
    cycle_type = normalize_text(payload.get('cycleType') or '月度') or '月度'
    if cycle_type != '月度':
        raise HTTPException(status_code=400, detail='当前仅支持按当月提交月度绩效')
    year = to_int(payload.get('assessmentYear'))
    month = to_int(payload.get('assessmentMonth'))
    now = datetime.utcnow()
    if year != now.year or month != now.month:
        raise HTTPException(status_code=400, detail='月度绩效仅允许提交当前自然月，不能提前或滞后提交')


def assert_no_duplicate_employee_submission(repository, employee_no: str, assessment_year: int, assessment_month: int, current_id: str | None = None) -> None:
    for item in repository.list('performance'):
        item_employee_no = normalize_text(item.get('employeeNo') or item.get('employee_no'))
        item_year = to_int(item.get('assessmentYear') or item.get('year'))
        item_month = to_int(item.get('assessmentMonth') or item.get('month'))
        item_id = item.get('id')
        if current_id and item_id == current_id:
            continue
        if item_employee_no == employee_no and item_year == assessment_year and item_month == assessment_month:
            raise HTTPException(status_code=400, detail='当前月份绩效已提交，不能重复提交')


def ensure_status_transition(user: dict, current_status: str, next_status: str) -> None:
    allowed = {
        'employee': {
            '待员工提交': {'待经理审核'},
            '经理退回修改': {'待经理审核'},
            'HR退回修改': {'待经理审核'},
        },
        'manager': {
            '待经理审核': {'待HR审核', '经理退回修改'},
            '待HR审核': {'待HR审核', '经理退回修改'},
        },
        'hr': {
            '待HR审核': {'已确认发布', 'HR退回修改'},
            '已确认发布': {'已确认发布'},
        },
    }
    role = user.get('role')
    if next_status not in allowed.get(role, {}).get(current_status, set()):
        raise HTTPException(status_code=400, detail='当前状态不允许执行该操作')
