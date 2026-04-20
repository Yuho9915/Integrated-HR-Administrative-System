from fastapi import APIRouter, Depends, HTTPException

from app.repositories.factory import get_repository
from app.schemas.common import LeavePayload
from app.security.auth import require_roles
from app.services.rules import RuleEngine
from app.utils.responses import ok

router = APIRouter(prefix='/leaves', tags=['leaves'])
rule_engine = RuleEngine()


ACTIVE_LEAVE_STATUSES = {'待经理审批', '待审批', '已通过'}


def _normalize_text(value) -> str:
    return str(value or '').strip()


def _ensure_no_duplicate_leave(repository, payload: LeavePayload):
    duplicate = next((
        row for row in repository.list('leaves')
        if (row.get('employee_no') == payload.employee_no or row.get('employeeNo') == payload.employee_no)
        and row.get('leave_type') == payload.leave_type
        and _normalize_text(row.get('start_at')) == _normalize_text(payload.start_at)
        and _normalize_text(row.get('end_at')) == _normalize_text(payload.end_at)
        and float(row.get('days') or 0) == float(payload.days)
        and _normalize_text(row.get('reason')) == _normalize_text(payload.reason)
        and row.get('status') in ACTIVE_LEAVE_STATUSES
    ), None)
    if duplicate:
        raise HTTPException(status_code=400, detail='请勿重复提交相同的请假申请')


@router.get('')
def get_leave_list(user=Depends(require_roles('employee', 'manager', 'hr'))):
    repository = get_repository()
    rows = repository.list('leaves')
    if user['role'] == 'employee':
        employee = next((item for item in repository.list('users') if item['username'] == user['username']), None)
        employee_no = employee.get('employeeNo') if employee else ''
        rows = [row for row in rows if row.get('employee_no') == employee_no or row.get('employeeNo') == employee_no]
    return ok(rows)


@router.post('')
async def create_leave(payload: LeavePayload, user=Depends(require_roles('employee', 'hr'))):
    validation = rule_engine.validate_leave(payload.leave_type, payload.days)
    if not validation['valid']:
        raise HTTPException(status_code=400, detail=validation['reason'])
    repository = get_repository()
    _ensure_no_duplicate_leave(repository, payload)
    employee = next((item for item in repository.list('employees') if (item.get('employee_no') or item.get('employeeNo')) == payload.employee_no), None)
    applicant_name = employee.get('name') if employee else payload.employee_no
    applicant_department = employee.get('department') if employee else ''
    document = repository.upsert('leaves', {
        **payload.model_dump(),
        'status': '待经理审批',
        'approver': '王嘉铭',
        'approval_chain': validation['rule']['approval_chain'],
        'pay_rate': validation['rule']['pay_rate'],
    })
    repository.upsert('approvals', {
        'category': '人事审批',
        'applicant': applicant_name,
        'applicant_name': applicant_name,
        'applicant_employee_no': payload.employee_no,
        'applicant_department': applicant_department,
        'type': payload.leave_type,
        'duration': f'{payload.days}天',
        'status': '待审批',
        'level': validation['rule']['approval_chain'][0],
        'approval_chain': validation['rule']['approval_chain'],
        'current_step': 0,
        'assigned_to': 'manager',
        'source_id': document['id'],
        'apply_time': document.get('created_at'),
        'reason': payload.reason,
        'related_info': [
            {'label': '开始时间', 'value': payload.start_at},
            {'label': '结束时间', 'value': payload.end_at},
            {'label': '请假天数', 'value': f'{payload.days}天'},
            {'label': '审批链路', 'value': ' → '.join(validation['rule']['approval_chain'])},
        ],
        'detail_content': payload.reason,
        'history': [
            {
                'node': '提交申请',
                'approver': applicant_name,
                'approver_username': payload.employee_no,
                'time': document.get('created_at'),
                'result': '已提交',
                'comment': payload.reason,
            }
        ],
    })
    return ok({'leave': document}, '请假申请已提交')
