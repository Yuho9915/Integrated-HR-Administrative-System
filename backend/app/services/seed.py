from datetime import datetime

from app.repositories.factory import get_repository

PNG_BASE64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4////fwAJ+wP9KobjigAAAABJRU5ErkJggg=='
PDF_BASE64 = 'JVBERi0xLjQKJcTl8uXrp/Og0MTGCjEgMCBvYmoKPDwvVHlwZS9DYXRhbG9nL1BhZ2VzIDIgMCBSPj4KZW5kb2JqCjIgMCBvYmoKPDwvVHlwZS9QYWdlcy9LaWRzIFszIDAgUl0vQ291bnQgMT4+CmVuZG9iagozIDAgb2JqCjw8L1R5cGUvUGFnZS9QYXJlbnQgMiAwIFIvTWVkaWFCb3ggWzAgMCA1OTUgODQyXS9Db250ZW50cyA0IDAgUi9SZXNvdXJjZXMgPDwvRm9udCA8PC9GMQogNSAwIFI+Pj4+Pj4KZW5kb2JqCjQgMCBvYmoKPDwvTGVuZ3RoIDY1Pj4Kc3RyZWFtCkJUCi9GMSAyNCBUZgoxMDAgNzAwIFRkCihIUiBBdHRhY2htZW50IFByZXZpZXcpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PC9UeXBlL0ZvbnQvU3VidHlwZS9UeXBlMS9CYXNlRm9udC9IZWx2ZXRpY2E+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDEwIDAwMDAwIG4gCjAwMDAwMDAwNjAgMDAwMDAgbiAKMDAwMDAwMDExNyAwMDAwMCBuIAowMDAwMDAwMjQzIDAwMDAwIG4gCjAwMDAwMDAzNTkgMDAwMDAgbiAKdHJhaWxlcgo8PC9TaXplIDYvUm9vdCAxIDAgUj4+CnN0YXJ0eHJlZgo0MjcKJSVFT0Y='


def build_attachments(employee_no: str) -> dict:
    return {
        'id_card_attachments': [
            {'name': f'{employee_no}-身份证正面.png', 'mime_type': 'image/png', 'size': 96, 'content_base64': PNG_BASE64},
            {'name': f'{employee_no}-身份证反面.png', 'mime_type': 'image/png', 'size': 96, 'content_base64': PNG_BASE64},
        ],
        'education_certificate_attachments': [
            {'name': f'{employee_no}-学历证书.pdf', 'mime_type': 'application/pdf', 'size': 512, 'content_base64': PDF_BASE64},
        ],
        'labor_contract_attachments': [
            {'name': f'{employee_no}-劳动合同.pdf', 'mime_type': 'application/pdf', 'size': 512, 'content_base64': PDF_BASE64},
        ],
        'medical_report_attachments': [
            {'name': f'{employee_no}-体检报告.pdf', 'mime_type': 'application/pdf', 'size': 512, 'content_base64': PDF_BASE64},
        ],
    }

DEFAULT_DATA = {
    'users': [
        {'id': 'user-employee', 'username': 'employee', 'password': '123456', 'name': '陈晓雨', 'role': 'employee', 'department': '市场部', 'employeeNo': 'EMP-1024', 'position': '招商主管'},
        {'id': 'user-manager', 'username': 'manager', 'password': '123456', 'name': '王嘉铭', 'role': 'manager', 'department': '运营中心', 'employeeNo': 'MGR-0201', 'position': '部门经理'},
        {'id': 'user-hr', 'username': 'admin.hr', 'password': '123456', 'name': '于浩', 'role': 'hr', 'department': '综合管理部', 'employeeNo': 'HR-0001', 'position': '人事行政专员'},
        {'id': 'user-boss', 'username': 'boss', 'password': '123456', 'name': '赵启明', 'role': 'boss', 'department': '总经办', 'employeeNo': 'CEO-0001', 'position': '总经理'},
    ],
    'employees': [
        {'id': 'emp-1', 'employee_no': 'HR-0001', 'name': '于浩', 'department': '综合管理部', 'position': '人事行政专员', 'role': 'hr', 'salary_base': 12000, 'performance_base': 2000, 'hire_date': '2024-01-01', 'resignation_date': '', 'status': '在职', 'id_card_no': '110101199001011234', 'phone': '13800000001', 'email': 'yuhao@hr.local', 'probation_end_date': '2024-04-01', 'emergency_contact': '于母', 'emergency_contact_phone': '13800001001', 'political_status': '中共党员', 'gender': '男', 'birth_date': '1990-01-01', 'registered_address': '北京市朝阳区', 'current_address': '北京市海淀区', 'ethnicity': '汉族', 'education': '本科', 'graduate_school': '中国人民大学', 'major': '人力资源管理', 'contract_type': '固定期限', 'contract_sign_date': '2024-01-01', 'contract_end_date': '2027-01-01', 'social_security_base': 12000, 'housing_fund_base': 12000, 'bank_account': '6222000000000001', 'bank_name': '招商银行北京分行', 'job_level': 'P4', 'report_to': '赵启明', 'work_location': '北京总部', 'id_card_attachments': [], 'education_certificate_attachments': [], 'labor_contract_attachments': [], 'medical_report_attachments': []},
        {'id': 'emp-2', 'employeeNo': 'DEV-0008', 'name': '张琳', 'department': '产品技术部', 'position': '前端工程师', 'role': 'employee', 'salary_base': 15000, 'performance_base': 3000, 'hire_date': '2024-03-12', 'resignation_date': '', 'political_status': '群众', 'status': '在职'},
        {'id': 'emp-3', 'employeeNo': 'OPS-1003', 'name': '周峰', 'department': '运营中心', 'position': '招商主管', 'role': 'employee', 'salary_base': 9800, 'performance_base': 1500, 'hire_date': '2025-05-10', 'resignation_date': '', 'political_status': '共青团员', 'status': '试用'},
        {'id': 'emp-4', 'employeeNo': 'FIN-0012', 'name': '李雯', 'department': '财务部', 'position': '会计', 'role': 'employee', 'salary_base': 10800, 'performance_base': 1800, 'hire_date': '2023-11-08', 'resignation_date': '', 'political_status': '群众', 'status': '在职'},
        {'id': 'emp-5', 'employeeNo': 'ADM-0007', 'name': '孙倩', 'department': '综合管理部', 'position': '行政专员', 'role': 'employee', 'salary_base': 8600, 'performance_base': 1200, 'hire_date': '2024-06-18', 'status': '在职'},
        {'id': 'emp-6', 'employeeNo': 'DEV-0015', 'name': '何俊', 'department': '产品技术部', 'position': '后端工程师', 'role': 'employee', 'salary_base': 16800, 'performance_base': 3200, 'hire_date': '2024-02-20', 'status': '在职'},
        {'id': 'emp-7', 'employeeNo': 'MKT-0021', 'name': '高媛', 'department': '市场部', 'position': '品牌专员', 'role': 'employee', 'salary_base': 9200, 'performance_base': 1400, 'hire_date': '2025-01-06', 'status': '试用'},
        {'id': 'emp-8', 'employeeNo': 'OPS-1011', 'name': '蒋涛', 'department': '运营中心', 'position': '招商主管', 'role': 'employee', 'salary_base': 10200, 'performance_base': 1600, 'hire_date': '2024-08-15', 'status': '在职'},
        {'id': 'emp-9', 'employeeNo': 'SAL-0009', 'name': '彭越', 'department': '销售部', 'position': '客户经理', 'role': 'employee', 'salary_base': 11000, 'performance_base': 2500, 'hire_date': '2023-09-12', 'status': '在职'},
        {'id': 'emp-10', 'employeeNo': 'DEV-0022', 'name': '郑航', 'department': '产品技术部', 'position': '测试工程师', 'role': 'employee', 'salary_base': 12600, 'performance_base': 1900, 'hire_date': '2024-10-09', 'status': '在职'},
        {'id': 'emp-11', 'employeeNo': 'HR-0006', 'name': '罗敏', 'department': '综合管理部', 'position': '招聘专员', 'role': 'employee', 'salary_base': 9700, 'performance_base': 1500, 'hire_date': '2024-04-03', 'status': '在职'},
        {'id': 'emp-12', 'employeeNo': 'FIN-0018', 'name': '韩雪', 'department': '财务部', 'position': '出纳', 'role': 'employee', 'salary_base': 8800, 'performance_base': 1200, 'hire_date': '2025-02-11', 'status': '试用'},
        {'id': 'emp-13', 'employeeNo': 'MKT-0025', 'name': '邵晴', 'department': '市场部', 'position': '招商主管', 'role': 'employee', 'salary_base': 10100, 'performance_base': 1600, 'hire_date': '2024-12-01', 'status': '在职'},
        {'id': 'emp-14', 'employeeNo': 'SAL-0014', 'name': '许诺', 'department': '销售部', 'position': '销售顾问', 'role': 'employee', 'salary_base': 9300, 'performance_base': 2100, 'hire_date': '2024-07-22', 'status': '在职'},
        {'id': 'emp-15', 'employeeNo': 'OPS-1019', 'name': '唐睿', 'department': '运营中心', 'position': '运营专员', 'role': 'employee', 'salary_base': 8900, 'performance_base': 1300, 'hire_date': '2025-03-17', 'status': '试用'},
        {'id': 'emp-16', 'employeeNo': 'DEV-0031', 'name': '顾晨', 'department': '产品技术部', 'position': '产品经理', 'role': 'employee', 'salary_base': 17200, 'performance_base': 3500, 'hire_date': '2023-12-05', 'status': '在职'},
        {'id': 'emp-17', 'employeeNo': 'ADM-0013', 'name': '梁悦', 'department': '综合管理部', 'position': '行政前台', 'role': 'employee', 'salary_base': 7800, 'performance_base': 1000, 'hire_date': '2025-01-25', 'status': '在职'},
        {'id': 'emp-18', 'employeeNo': 'MKT-0032', 'name': '马宁', 'department': '市场部', 'position': '新媒体运营', 'role': 'employee', 'salary_base': 9600, 'performance_base': 1500, 'hire_date': '2024-09-14', 'status': '在职'},
    ],
    'departments': [
        {'id': 'dept-1', 'name': '综合管理部'},
        {'id': 'dept-2', 'name': '产品技术部'},
        {'id': 'dept-3', 'name': '运营中心'},
        {'id': 'dept-4', 'name': '市场部'},
        {'id': 'dept-5', 'name': '销售部'},
        {'id': 'dept-6', 'name': '财务部'},
        {'id': 'dept-7', 'name': '总经办'},
    ],
    'positions': [
        {'id': 'pos-1', 'department': '综合管理部', 'name': '人事行政专员'},
        {'id': 'pos-2', 'department': '综合管理部', 'name': '行政专员'},
        {'id': 'pos-3', 'department': '综合管理部', 'name': '招聘专员'},
        {'id': 'pos-4', 'department': '综合管理部', 'name': '行政前台'},
        {'id': 'pos-5', 'department': '产品技术部', 'name': '前端工程师'},
        {'id': 'pos-6', 'department': '产品技术部', 'name': '后端工程师'},
        {'id': 'pos-7', 'department': '产品技术部', 'name': '测试工程师'},
        {'id': 'pos-8', 'department': '产品技术部', 'name': '产品经理'},
        {'id': 'pos-9', 'department': '运营中心', 'name': '部门经理'},
        {'id': 'pos-10', 'department': '运营中心', 'name': '招商主管'},
        {'id': 'pos-11', 'department': '运营中心', 'name': '运营专员'},
        {'id': 'pos-12', 'department': '市场部', 'name': '品牌专员'},
        {'id': 'pos-13', 'department': '市场部', 'name': '招商主管'},
        {'id': 'pos-14', 'department': '市场部', 'name': '新媒体运营'},
        {'id': 'pos-15', 'department': '销售部', 'name': '客户经理'},
        {'id': 'pos-16', 'department': '销售部', 'name': '销售顾问'},
        {'id': 'pos-17', 'department': '财务部', 'name': '会计'},
        {'id': 'pos-18', 'department': '财务部', 'name': '出纳'},
        {'id': 'pos-19', 'department': '总经办', 'name': '总经理'},
    ],
    'attendance': [
        {'id': 'att-1', 'employeeNo': 'HR-0001', 'name': '于浩', 'department': '综合管理部', 'month': '2026-04', 'date': '2026-04-01', 'checkIn': '08:58', 'checkOut': '18:06', 'status': '正常', 'lateMinutes': 0, 'earlyMinutes': 0, 'leaveType': '', 'overtimeHours': 0.5, 'workHours': 9.13, 'remark': '', 'type': '工作日'},
        {'id': 'att-2', 'employeeNo': 'DEV-0008', 'name': '张琳', 'department': '产品技术部', 'month': '2026-04', 'date': '2026-04-01', 'checkIn': '09:12', 'checkOut': '18:09', 'status': '迟到', 'lateMinutes': 12, 'earlyMinutes': 0, 'leaveType': '', 'overtimeHours': 1.0, 'workHours': 9.95, 'remark': '晨会延误', 'type': '工作日'},
        {'id': 'att-3', 'employeeNo': 'OPS-1003', 'name': '周峰', 'department': '运营中心', 'month': '2026-04', 'date': '2026-04-01', 'checkIn': '08:55', 'checkOut': '17:40', 'status': '早退', 'lateMinutes': 0, 'earlyMinutes': 20, 'leaveType': '', 'overtimeHours': 0, 'workHours': 8.75, 'remark': '外出回访提前离岗', 'type': '工作日'},
        {'id': 'att-4', 'employeeNo': 'FIN-0012', 'name': '李雯', 'department': '财务部', 'month': '2026-04', 'date': '2026-04-01', 'checkIn': '', 'checkOut': '', 'status': '请假', 'lateMinutes': 0, 'earlyMinutes': 0, 'leaveType': '事假', 'overtimeHours': 0, 'workHours': 0, 'remark': '请假半天', 'type': '工作日'},
        {'id': 'att-5', 'employeeNo': 'MKT-0021', 'name': '高媛', 'department': '市场部', 'month': '2026-04', 'date': '2026-04-01', 'checkIn': '09:01', 'checkOut': '18:02', 'status': '外勤', 'lateMinutes': 0, 'earlyMinutes': 0, 'leaveType': '', 'overtimeHours': 0, 'workHours': 9.02, 'remark': '客户拜访', 'type': '工作日'},
        {'id': 'att-6', 'employeeNo': 'SAL-0009', 'name': '彭越', 'department': '销售部', 'month': '2026-04', 'date': '2026-04-01', 'checkIn': '08:50', 'checkOut': '18:20', 'status': '出差', 'lateMinutes': 0, 'earlyMinutes': 0, 'leaveType': '', 'overtimeHours': 1.5, 'workHours': 10.5, 'remark': '苏州出差', 'type': '工作日'},
        {'id': 'att-7', 'employeeNo': 'DEV-0015', 'name': '何俊', 'department': '产品技术部', 'month': '2026-04', 'date': '2026-04-02', 'checkIn': '', 'checkOut': '', 'status': '旷工', 'lateMinutes': 0, 'earlyMinutes': 0, 'leaveType': '', 'overtimeHours': 0, 'workHours': 0, 'remark': '未提交请假', 'type': '工作日'},
        {'id': 'att-8', 'employeeNo': 'OPS-1011', 'name': '蒋涛', 'department': '运营中心', 'month': '2026-04', 'date': '2026-04-02', 'checkIn': '09:04', 'checkOut': '18:01', 'status': '正常', 'lateMinutes': 0, 'earlyMinutes': 0, 'leaveType': '', 'overtimeHours': 0, 'workHours': 8.95, 'remark': '', 'type': '工作日'},
        {'id': 'att-9', 'employeeNo': 'HR-0006', 'name': '罗敏', 'department': '综合管理部', 'month': '2026-04', 'date': '2026-04-02', 'checkIn': '09:08', 'checkOut': '18:10', 'status': '迟到', 'lateMinutes': 8, 'earlyMinutes': 0, 'leaveType': '', 'overtimeHours': 0.5, 'workHours': 9.03, 'remark': '地铁故障', 'type': '工作日'},
        {'id': 'att-10', 'employeeNo': 'MKT-0032', 'name': '马宁', 'department': '市场部', 'month': '2026-04', 'date': '2026-04-02', 'checkIn': '08:59', 'checkOut': '18:03', 'status': '正常', 'lateMinutes': 0, 'earlyMinutes': 0, 'leaveType': '', 'overtimeHours': 0.5, 'workHours': 9.07, 'remark': '', 'type': '工作日'}
    ],
    'leaves': [
        {'id': 'leave-1', 'employeeNo': 'FIN-0012', 'department': '财务部', 'leave_type': '事假', 'start_at': '2026-04-01 09:00', 'end_at': '2026-04-01 18:00', 'days': 1, 'reason': '家庭事务', 'status': '已通过', 'approver': '于浩'},
        {'id': 'leave-2', 'employeeNo': 'HR-0006', 'department': '综合管理部', 'leave_type': '病假', 'start_at': '2026-04-02 09:00', 'end_at': '2026-04-02 18:00', 'days': 1, 'reason': '发热就诊', 'status': '已通过', 'approver': '于浩'},
    ],
    'performance': [
        {'id': 'perf-1', 'employeeNo': 'EMP-1024', 'period': '2026-04', 'score': 88, 'grade': 'B+', 'reviewer': '王嘉铭', 'status': '已发布'},
        {'id': 'perf-2', 'employeeNo': 'OPS-1003', 'period': '2026-04', 'score': 82, 'grade': 'B', 'reviewer': '王嘉铭', 'status': '待复核'},
    ],
    'payroll': [
        {'id': 'pay-1', 'employeeNo': 'EMP-1024', 'month': '2026-04', 'basic': 9000, 'subsidy': 1200, 'performance': 1800, 'tax': 640, 'actual': 11360},
        {'id': 'pay-2', 'employeeNo': 'EMP-1024', 'month': '2026-03', 'basic': 9000, 'subsidy': 1200, 'performance': 2200, 'tax': 700, 'actual': 11700},
    ],
    'approvals': [
        {'id': 'approval-1', 'category': '人事审批', 'applicant': '陈晓雨', 'type': '病假', 'duration': '1天', 'status': '待审批', 'level': '经理'},
        {'id': 'approval-2', 'category': '资产审批', 'applicant': '周峰', 'type': '办公用品领用', 'duration': 'A4纸 2 箱', 'status': '待审批', 'level': '人事行政'},
    ],
    'assets': [
        {'id': 'asset-1', 'asset': '联想 ThinkBook 14', 'type': '固定资产', 'owner': '张琳', 'status': '使用中'},
        {'id': 'asset-2', 'asset': '投影仪 X2', 'type': '会议设备', 'owner': '行政库房', 'status': '待维修'},
        {'id': 'asset-3', 'asset': '打印纸 A4', 'type': '办公耗材', 'owner': '库存', 'status': '低库存'},
    ],
    'reports': [
        {'id': 'report-1', 'name': '部门人数分布', 'value': '运营中心 16 人', 'tip': '综合管理部 9 人 / 技术部 11 人'},
        {'id': 'report-2', 'name': '绩效等级分布', 'value': 'B档 45.8%', 'tip': 'A档占比控制在合理区间'},
        {'id': 'report-3', 'name': '耗材消耗', 'value': '本月 32 项', 'tip': '打印纸与墨盒为主要耗材'},
    ],
    'applications': [
        {'id': 'app-1', 'type': '事假', 'period': '2026-04-16 ~ 2026-04-17', 'status': '待经理审批', 'approver': '王嘉铭'},
        {'id': 'app-2', 'type': '办公用品领用', 'period': '2026-04-05', 'status': '已通过', 'approver': '综合管理部'},
    ],
}


def _replace_resource(repository, resource: str, items: list[dict]) -> None:
    for existing in repository.list(resource):
        record_id = existing.get('id')
        if record_id:
            repository.delete(resource, record_id)
    for item in items:
        repository.upsert(resource, item)


def _should_refresh_attendance(repository) -> bool:
    attendance_rows = repository.list('attendance')
    if not attendance_rows:
        return False
    legacy_employee_nos = {'EMP-1024'}
    return any(str(item.get('employeeNo') or '').strip() in legacy_employee_nos for item in attendance_rows)


def _should_refresh_leaves(repository) -> bool:
    leaves = repository.list('leaves')
    if not leaves:
        return False
    legacy_employee_nos = {'EMP-1024'}
    return any(str(item.get('employeeNo') or item.get('employee_no') or '').strip() in legacy_employee_nos for item in leaves)


def seed_data() -> None:
    repository = get_repository()
    for resource, items in DEFAULT_DATA.items():
        if resource == 'attendance':
            if _should_refresh_attendance(repository):
                _replace_resource(repository, resource, items)
                continue
        if resource == 'leaves':
            if _should_refresh_leaves(repository):
                _replace_resource(repository, resource, items)
                continue
        if repository.list(resource):
            continue
        for item in items:
            repository.upsert(resource, item)
