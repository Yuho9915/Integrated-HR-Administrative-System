from fastapi import APIRouter, Depends

from app.repositories.factory import get_repository
from app.security.auth import require_roles
from app.utils.responses import ok

router = APIRouter(prefix='/reports', tags=['reports'])


@router.get('/summary')
def get_report_summary(user=Depends(require_roles('hr', 'boss'))):
    repository = get_repository()
    employees = repository.list('employees')
    attendance = repository.list('attendance')
    payroll = repository.list('payroll')
    charts = [
        {'name': '部门人数分布', 'value': f'总人数 {len(employees)} 人', 'tip': '支持导出 Excel/PDF'},
        {'name': '考勤异常统计', 'value': f'异常 {len([row for row in attendance if row.get("status") != "正常"])} 条', 'tip': '来自最新考勤导入'},
        {'name': '人力成本', 'value': f'¥{round(sum(float(row.get("actual", 0)) for row in payroll), 2)}', 'tip': '已自动汇总实发工资'},
    ]
    return ok({
        'charts': charts,
        'headcount': len(employees),
        'attendance_records': len(attendance),
        'payroll_records': len(payroll),
    })
