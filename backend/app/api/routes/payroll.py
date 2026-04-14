from fastapi import APIRouter, Depends

from app.repositories.factory import get_repository
from app.schemas.common import PayrollCalculatePayload
from app.security.auth import require_roles
from app.services.ai_service import AIService
from app.services.rules import RuleEngine
from app.utils.responses import ok

router = APIRouter(prefix='/payroll', tags=['payroll'])
ai_service = AIService()
rule_engine = RuleEngine()


@router.get('/summary')
def get_payroll_summary(user=Depends(require_roles('employee', 'hr', 'boss'))):
    repository = get_repository()
    rows = repository.list('payroll')
    if user['role'] == 'employee':
        employee = next((item for item in repository.list('users') if item['username'] == user['username']), None)
        employee_no = employee.get('employeeNo') if employee else ''
        rows = [row for row in rows if row.get('employeeNo') == employee_no]
    return ok({'records': rows, 'month': '2026-04'})


@router.post('/calculate')
async def calculate_payroll(payload: PayrollCalculatePayload, user=Depends(require_roles('hr'))):
    repository = get_repository()
    employees = repository.list('employees')
    attendance_rows = repository.list('attendance')
    leave_rows = repository.list('leaves')
    performance_rows = repository.list('performance')
    payroll_rows = []

    for employee in employees:
        employee_no = employee.get('employeeNo')
        attendance = [row for row in attendance_rows if row.get('employeeNo') == employee_no]
        leaves = [row for row in leave_rows if row.get('employee_no') == employee_no or row.get('employeeNo') == employee_no]
        performance = next((row for row in performance_rows if row.get('employeeNo') == employee_no), None)
        payroll = rule_engine.calculate_salary(employee, attendance, leaves, performance)
        payroll_document = repository.upsert('payroll', {'employeeNo': employee_no, 'month': payload.month, **payroll})
        payroll_rows.append(payroll_document)

    ai_result = await ai_service.payroll_calculate(payload.month, employees, payroll_rows)
    repository.upsert('payroll_runs', ai_result)
    return ok({'summary': ai_result, 'records': payroll_rows}, 'AI 工资核算完成')
