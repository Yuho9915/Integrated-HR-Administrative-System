from fastapi import APIRouter, Depends, HTTPException

from app.repositories.factory import get_repository
from app.schemas.common import SupplementPayload
from app.security.auth import require_roles
from app.services.ai_service import AIService
from app.services.rules import RuleEngine
from app.utils.responses import ok

router = APIRouter(prefix='/supplements', tags=['supplements'])
ai_service = AIService()
rule_engine = RuleEngine()


@router.get('')
def get_supplement_list(user=Depends(require_roles('employee', 'manager', 'hr', 'boss'))):
    repository = get_repository()
    rows = repository.list('supplements')
    if user['role'] == 'employee':
        employee = next((item for item in repository.list('users') if item['username'] == user['username']), None)
        employee_no = employee.get('employeeNo') if employee else ''
        rows = [row for row in rows if row.get('employee_no') == employee_no or row.get('employeeNo') == employee_no]
    return ok(rows)


@router.post('')
async def create_supplement(payload: SupplementPayload, user=Depends(require_roles('employee', 'hr'))):
    repository = get_repository()
    existing = [
        row for row in repository.list('supplements')
        if (row.get('employee_no') == payload.employee_no or row.get('employeeNo') == payload.employee_no)
        and str(row.get('date', '')).startswith(payload.date[:7])
    ]
    if len(existing) >= 3:
        raise HTTPException(status_code=400, detail='每月最多只能申请3次补卡')

    employee = next((item for item in repository.list('employees') if (item.get('employee_no') or item.get('employeeNo')) == payload.employee_no), None)
    applicant_name = employee.get('name') if employee else payload.employee_no
    applicant_department = employee.get('department') if employee else ''
    validation = rule_engine.validate_leave('补卡申请', 1)

    document = repository.upsert('supplements', {
        **payload.model_dump(),
        'leave_type': '补卡申请',
        'start_at': f'{payload.date} {payload.time}',
        'end_at': f'{payload.date} {payload.time}',
        'days': 0,
        'status': '待人事审批',
        'approver': '于浩',
        'approval_chain': validation['rule']['approval_chain'],
        'pay_rate': validation['rule']['pay_rate'],
    })
    approval = await ai_service.smart_approval(document)
    repository.upsert('approvals', {
        'category': '人事审批',
        'applicant': applicant_name,
        'applicant_name': applicant_name,
        'applicant_employee_no': payload.employee_no,
        'applicant_department': applicant_department,
        'type': '补卡申请',
        'duration': payload.time,
        'status': '待审批',
        'level': validation['rule']['approval_chain'][0],
        'approval_chain': validation['rule']['approval_chain'],
        'current_step': 0,
        'assigned_to': 'admin.hr',
        'source_id': document['id'],
        'apply_time': document.get('created_at'),
        'reason': payload.reason,
        'related_info': [
            {'label': '补卡日期', 'value': payload.date},
            {'label': '补卡时间', 'value': payload.time},
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
    return ok({'supplement': document, 'ai': approval}, '补卡申请已提交')
