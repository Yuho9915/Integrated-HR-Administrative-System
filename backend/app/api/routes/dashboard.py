from fastapi import APIRouter, Depends

from app.repositories.factory import get_repository
from app.security.auth import require_roles
from app.utils.responses import ok

router = APIRouter(prefix='/dashboard', tags=['dashboard'])


@router.get('/summary')
def get_dashboard_summary(user=Depends(require_roles('employee', 'manager', 'hr'))):
    repository = get_repository()
    employees = repository.list('employees')
    payroll = repository.list('payroll')
    approvals = repository.list('approvals')
    attendance = repository.list('attendance')
    abnormal = len([row for row in attendance if row.get('status') != '正常'])
    return ok({
        'cards': [
            {'label': '总人数', 'value': str(len(employees)), 'tip': '当前在档员工'},
            {'label': '待审批事项', 'value': str(len([row for row in approvals if row.get('status') == '待审批'])), 'tip': '四类审批统一入口'},
            {'label': '考勤异常', 'value': str(abnormal), 'tip': '自动判定迟到/早退/缺卡/旷工'},
            {'label': '数据库驱动', 'value': repository.driver, 'tip': '支持 SQLite / MongoDB 切换'},
        ]
    })
