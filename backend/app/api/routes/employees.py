from base64 import b64decode
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from app.repositories.factory import get_repository
from app.schemas.common import DepartmentPayload, EmployeePayload, PositionPayload
from app.security.auth import require_roles
from app.services.ai_service import AIService
from app.services.seed import DEFAULT_DATA
from app.utils.responses import ok

router = APIRouter(prefix='/employees', tags=['employees'])
ai_service = AIService()
UNIQUE_FIELDS = {'id_card_no': '身份证号', 'phone': '手机号', 'email': '邮箱'}
ATTACHMENT_FIELDS = {
    'photo_attachment': '员工证件照',
    'id_card_attachments': '身份证附件',
    'education_certificate_attachments': '学历证书',
    'labor_contract_attachments': '劳动合同',
    'medical_report_attachments': '体检报告',
}


def _find_duplicate(repository, field: str, value: str, exclude_id: str | None = None):
    if field not in UNIQUE_FIELDS:
        raise HTTPException(status_code=400, detail='不支持的校验字段')
    target = (value or '').strip()
    if not target:
        return None
    for item in repository.list('employees'):
        if exclude_id and item.get('id') == exclude_id:
            continue
        if str(item.get(field, '')).strip() == target:
            return item
    return None


def _ensure_unique_fields(repository, payload: EmployeePayload, exclude_id: str | None = None):
    for field, label in UNIQUE_FIELDS.items():
        if _find_duplicate(repository, field, getattr(payload, field), exclude_id):
            raise HTTPException(status_code=400, detail=f'{label}已存在，不能重复')


def _get_attachment(employee: dict, field: str, index: int):
    if field not in ATTACHMENT_FIELDS:
        raise HTTPException(status_code=400, detail='不支持的附件字段')
    attachments = employee.get(field) or []
    if index < 0 or index >= len(attachments):
        raise HTTPException(status_code=404, detail='附件不存在')
    attachment = attachments[index]
    if not attachment.get('content_base64'):
        raise HTTPException(status_code=404, detail='附件内容不存在')
    return attachment


def _resolve_employee_by_identifier(repository, identifier: str) -> dict | None:
    target = str(identifier or '').strip()
    if not target:
        return None
    employee = repository.get('employees', target)
    if employee:
        return employee
    return next(
        (
            item for item in repository.list('employees')
            if str(item.get('employee_no') or item.get('employeeNo') or '').strip() == target
        ),
        None,
    )


def _ensure_employee_scope(user: dict, employee: dict):
    if user['role'] in ['hr', 'manager']:
        return
    if user['role'] == 'employee' and user['username'] == 'employee' and str(employee.get('employee_no') or employee.get('employeeNo') or '').strip() == 'EMP-1024':
        return
    raise HTTPException(status_code=403, detail='当前角色无访问权限')


def _build_employee_self_update_payload(current: dict, payload: EmployeePayload) -> dict:
    editable_fields = {
        'gender': payload.gender,
        'birth_date': payload.birth_date,
        'ethnicity': payload.ethnicity,
        'education': payload.education,
        'graduate_school': payload.graduate_school,
        'major': payload.major,
        'current_address': payload.current_address,
        'emergency_contact': payload.emergency_contact,
        'emergency_contact_phone': payload.emergency_contact_phone,
        'photo_attachment': payload.photo_attachment,
        'id_card_attachments': payload.id_card_attachments,
        'education_certificate_attachments': payload.education_certificate_attachments,
        'medical_report_attachments': payload.medical_report_attachments,
    }
    return {
        **current,
        **editable_fields,
    }


def _resolve_current_employee(user: dict, repository) -> dict | None:
    matched_user = next((item for item in DEFAULT_DATA['users'] if item['username'] == user['username']), None)
    employee_no = str((matched_user or {}).get('employeeNo') or '').strip()
    if not employee_no:
        return None
    return next(
        (
            item for item in repository.list('employees')
            if str(item.get('employee_no') or item.get('employeeNo') or '').strip() == employee_no
        ),
        None,
    )


def _normalize_text(value: str) -> str:
    return (value or '').strip()


def _get_organization_meta(repository) -> tuple[list[str], dict[str, list[str]]]:
    stored_departments = repository.list('departments')
    stored_positions = repository.list('positions')
    departments = {_normalize_text(item.get('name', '')) for item in stored_departments}
    positions_by_department: dict[str, set[str]] = {}

    for item in stored_positions:
        department = _normalize_text(item.get('department', ''))
        name = _normalize_text(item.get('name', ''))
        if not department or not name:
            continue
        departments.add(department)
        positions_by_department.setdefault(department, set()).add(name)

    for employee in repository.list('employees'):
        department = _normalize_text(employee.get('department', ''))
        position = _normalize_text(employee.get('position', ''))
        if not department:
            continue
        departments.add(department)
        if position:
            positions_by_department.setdefault(department, set()).add(position)

    department_list = sorted(departments)
    position_map = {department: sorted(positions) for department, positions in positions_by_department.items()}
    return department_list, position_map


def _pick_value(item: dict, *keys: str, default=''):
    for key in keys:
        value = item.get(key)
        if value not in (None, ''):
            return value
    return default


def _safe_date(value: str):
    try:
        return datetime.strptime(str(value), '%Y-%m-%d').date()
    except Exception:
        return None


def _calc_tenure_months(hire_date: str) -> int:
    start = _safe_date(hire_date)
    if not start:
        return 0
    today = datetime.utcnow().date()
    months = (today.year - start.year) * 12 + (today.month - start.month)
    if today.day < start.day:
        months -= 1
    return max(months, 0)


def _calc_age(birth_date: str) -> int | None:
    birth = _safe_date(birth_date)
    if not birth:
        return None
    today = datetime.utcnow().date()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    return age if age >= 0 else None


def _normalize_employee_record(item: dict) -> dict:
    return {
        'id': item.get('id'),
        'employee_no': _pick_value(item, 'employee_no', 'employeeNo'),
        'name': _pick_value(item, 'name'),
        'department': _pick_value(item, 'department'),
        'position': _pick_value(item, 'position'),
        'status': _pick_value(item, 'status', default='在职'),
        'education': _pick_value(item, 'education'),
        'hire_date': _pick_value(item, 'hire_date'),
        'birth_date': _pick_value(item, 'birth_date', 'birthDate'),
        'probation_end_date': _pick_value(item, 'probation_end_date', 'probationEndDate'),
        'contract_end_date': _pick_value(item, 'contract_end_date', 'contractEndDate'),
        'resignation_date': _pick_value(item, 'resignation_date', 'resignationDate'),
        'salary_base': float(_pick_value(item, 'salary_base', default=0) or 0),
        'performance_base': float(_pick_value(item, 'performance_base', default=0) or 0),
    }


def _filter_employee_records(records: list[dict], department: str = '', position: str = '', status: str = '', keyword: str = '') -> list[dict]:
    department = _normalize_text(department)
    position = _normalize_text(position)
    status = _normalize_text(status)
    keyword = _normalize_text(keyword).lower()
    filtered = []
    for item in records:
        employee = _normalize_employee_record(item)
        if department and employee['department'] != department:
            continue
        if position and employee['position'] != position:
            continue
        if status and employee['status'] != status:
            continue
        if keyword and keyword not in str(employee['name']).lower() and keyword not in str(employee['employee_no']).lower():
            continue
        filtered.append(employee)
    return filtered


def _bucket_distribution(values: list[int], ranges: list[tuple[str, tuple[int, int]]]) -> list[dict]:
    result = []
    for label, (start, end) in ranges:
        result.append({'label': label, 'count': len([value for value in values if start <= value <= end])})
    return result


def _is_valid_id_card(value: str) -> bool:
    return bool(value) and bool(__import__('re').match(r'^(\d{15}|\d{17}[\dXx])$', str(value).strip()))


def _is_valid_phone(value: str) -> bool:
    return bool(value) and bool(__import__('re').match(r'^\d{11}$', str(value).strip()))


def _is_valid_email(value: str) -> bool:
    return bool(value) and bool(__import__('re').match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', str(value).strip()))


def _is_valid_bank_account(value: str) -> bool:
    text = str(value or '').strip()
    return bool(text) and text.isdigit() and 12 <= len(text) <= 19


@router.get('')
def get_employee_list(user=Depends(require_roles('hr', 'manager'))):
    repository = get_repository()
    return ok(repository.list('employees'))


@router.get('/meta')
def get_employee_meta(user=Depends(require_roles('hr', 'manager'))):
    repository = get_repository()
    departments, positions = _get_organization_meta(repository)
    return ok({'departments': departments, 'positions': positions})


@router.post('/departments')
def create_department(payload: DepartmentPayload, user=Depends(require_roles('hr'))):
    repository = get_repository()
    name = _normalize_text(payload.name)
    if not name:
        raise HTTPException(status_code=400, detail='部门名称不能为空')
    departments, _ = _get_organization_meta(repository)
    if name in departments:
        raise HTTPException(status_code=400, detail='部门已存在')
    document = repository.upsert('departments', {'name': name})
    return ok(document, '部门创建成功')


@router.post('/positions')
def create_position(payload: PositionPayload, user=Depends(require_roles('hr'))):
    repository = get_repository()
    department = _normalize_text(payload.department)
    name = _normalize_text(payload.name)
    if not department:
        raise HTTPException(status_code=400, detail='所属部门不能为空')
    if not name:
        raise HTTPException(status_code=400, detail='岗位名称不能为空')
    departments, positions = _get_organization_meta(repository)
    if department not in departments:
        raise HTTPException(status_code=400, detail='所属部门不存在')
    if name in positions.get(department, []):
        raise HTTPException(status_code=400, detail='岗位已存在')
    document = repository.upsert('positions', {'department': department, 'name': name})
    return ok(document, '岗位创建成功')


@router.get('/check-unique')
def check_employee_unique(
    field: str = Query(...),
    value: str = Query(...),
    exclude_id: str | None = Query(default=None),
    user=Depends(require_roles('hr', 'boss', 'manager')),
):
    repository = get_repository()
    duplicate = _find_duplicate(repository, field, value, exclude_id)
    return ok({'field': field, 'value': value, 'duplicate': bool(duplicate)})


@router.post('/ai/health-check')
async def employee_ai_health_check(payload: dict, user=Depends(require_roles('hr'))):
    repository = get_repository()
    records = _filter_employee_records(
        repository.list('employees'),
        department=payload.get('department', ''),
        position=payload.get('position', ''),
        status=payload.get('status', ''),
        keyword=payload.get('keyword', ''),
    )
    today = datetime.utcnow().date()
    threshold = today + timedelta(days=30)
    issues = []
    for employee in records:
        contract_end = _safe_date(employee.get('contract_end_date'))
        if contract_end and today <= contract_end <= threshold:
            issues.append({
                'type': '合同即将到期',
                'level': 'warning',
                'name': employee['name'],
                'employeeNo': employee['employee_no'],
                'department': employee['department'],
                'position': employee['position'],
                'date': contract_end.isoformat(),
                'daysLeft': (contract_end - today).days,
                'message': f"{employee['name']}（{employee['employee_no']}）劳动合同将于 {contract_end.isoformat()} 到期，剩余 {(contract_end - today).days} 天。",
            })
        probation_end = _safe_date(employee.get('probation_end_date'))
        if probation_end and today <= probation_end <= threshold and employee.get('status') in {'试用', '在职'}:
            issues.append({
                'type': '试用期即将到期',
                'level': 'warning',
                'name': employee['name'],
                'employeeNo': employee['employee_no'],
                'department': employee['department'],
                'position': employee['position'],
                'date': probation_end.isoformat(),
                'daysLeft': (probation_end - today).days,
                'message': f"{employee['name']}（{employee['employee_no']}）试用期将于 {probation_end.isoformat()} 结束，剩余 {(probation_end - today).days} 天。",
            })
        id_card = employee.get('id_card_no')
        if not id_card:
            issues.append({'type': '身份证号缺失', 'level': 'risk', 'name': employee['name'], 'employeeNo': employee['employee_no'], 'department': employee['department'], 'position': employee['position'], 'date': '', 'daysLeft': 9999, 'message': f"{employee['name']}（{employee['employee_no']}）未填写身份证号，请尽快补齐。"})
        elif not _is_valid_id_card(id_card):
            issues.append({'type': '身份证号格式异常', 'level': 'risk', 'name': employee['name'], 'employeeNo': employee['employee_no'], 'department': employee['department'], 'position': employee['position'], 'date': '', 'daysLeft': 9999, 'message': f"{employee['name']}（{employee['employee_no']}）身份证号格式异常，请核对证件信息。"})
        phone = employee.get('phone')
        if not phone:
            issues.append({'type': '手机号缺失', 'level': 'risk', 'name': employee['name'], 'employeeNo': employee['employee_no'], 'department': employee['department'], 'position': employee['position'], 'date': '', 'daysLeft': 9999, 'message': f"{employee['name']}（{employee['employee_no']}）未填写手机号，请尽快补齐。"})
        elif not _is_valid_phone(phone):
            issues.append({'type': '手机号格式异常', 'level': 'risk', 'name': employee['name'], 'employeeNo': employee['employee_no'], 'department': employee['department'], 'position': employee['position'], 'date': '', 'daysLeft': 9999, 'message': f"{employee['name']}（{employee['employee_no']}）手机号格式异常，请核对联系方式。"})
        email = employee.get('email')
        if not email:
            issues.append({'type': '邮箱缺失', 'level': 'risk', 'name': employee['name'], 'employeeNo': employee['employee_no'], 'department': employee['department'], 'position': employee['position'], 'date': '', 'daysLeft': 9999, 'message': f"{employee['name']}（{employee['employee_no']}）未填写邮箱，请尽快补齐。"})
        elif not _is_valid_email(email):
            issues.append({'type': '邮箱格式异常', 'level': 'risk', 'name': employee['name'], 'employeeNo': employee['employee_no'], 'department': employee['department'], 'position': employee['position'], 'date': '', 'daysLeft': 9999, 'message': f"{employee['name']}（{employee['employee_no']}）邮箱格式异常，请核对邮箱信息。"})
        bank_account = employee.get('bank_account')
        if bank_account and not _is_valid_bank_account(bank_account):
            issues.append({'type': '银行卡号格式异常', 'level': 'risk', 'name': employee['name'], 'employeeNo': employee['employee_no'], 'department': employee['department'], 'position': employee['position'], 'date': '', 'daysLeft': 9999, 'message': f"{employee['name']}（{employee['employee_no']}）银行卡号格式异常，请核对银行账户信息。"})
    issues.sort(key=lambda item: (item['daysLeft'], item['type'], item['employeeNo']))
    return ok({'items': issues, 'total': len(issues), 'generatedAt': datetime.utcnow().isoformat()})


@router.post('/ai/workforce-report')
async def employee_ai_workforce_report(payload: dict, user=Depends(require_roles('hr'))):
    repository = get_repository()
    records = _filter_employee_records(
        repository.list('employees'),
        department=payload.get('department', ''),
        position=payload.get('position', ''),
        status=payload.get('status', ''),
        keyword=payload.get('keyword', ''),
    )
    department_counter = Counter(item['department'] or '未分配部门' for item in records)
    education_counter = Counter(item['education'] or '未填写' for item in records)
    tenure_values = [_calc_tenure_months(item.get('hire_date')) for item in records if item.get('hire_date')]
    age_values = [age for age in (_calc_age(item.get('birth_date')) for item in records) if age is not None]
    status_counter = Counter(item['status'] or '未标记' for item in records)
    salary_total = sum(float(item.get('salary_base') or 0) + float(item.get('performance_base') or 0) for item in records)
    snapshot = {
        'recordCount': len(records),
        'departmentFilter': payload.get('department', ''),
        'positionFilter': payload.get('position', ''),
        'statusFilter': payload.get('status', ''),
        'departmentStructure': [{'department': key, 'count': value} for key, value in department_counter.items()],
        'educationDistribution': [{'label': key, 'count': value} for key, value in education_counter.items()],
        'ageDistribution': _bucket_distribution(age_values, [('25岁以下', (0, 24)), ('25-30岁', (25, 30)), ('31-35岁', (31, 35)), ('36岁及以上', (36, 120))]),
        'tenureDistribution': _bucket_distribution(tenure_values, [('1年以内', (0, 11)), ('1-3年', (12, 35)), ('3-5年', (36, 59)), ('5年以上', (60, 999))]),
        'statusDistribution': [{'label': key, 'count': value} for key, value in status_counter.items()],
        'averageSalary': round(salary_total / len(records), 2) if records else 0,
        'perCapitaOutputHint': round((salary_total / len(records)) / 1000, 2) if records else 0,
    }
    result = await ai_service.generate_workforce_report({'filters': payload, 'snapshot': snapshot, 'records': records})
    return ok(result)


@router.get('/{employee_id}/attachments/{field}/{index}')
def preview_employee_attachment(employee_id: str, field: str, index: int, user=Depends(require_roles('employee', 'hr', 'manager'))):
    repository = get_repository()
    employee = _resolve_employee_by_identifier(repository, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail='员工不存在')
    _ensure_employee_scope(user, employee)
    return ok(_get_attachment(employee, field, index))


@router.get('/{employee_id}/attachments/{field}/{index}/download')
def download_employee_attachment(employee_id: str, field: str, index: int, user=Depends(require_roles('employee', 'hr', 'manager'))):
    repository = get_repository()
    employee = _resolve_employee_by_identifier(repository, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail='员工不存在')
    _ensure_employee_scope(user, employee)
    attachment = _get_attachment(employee, field, index)
    filename = attachment.get('name', 'attachment')
    safe_filename = ''.join(ch if ord(ch) < 128 else '_' for ch in filename) or 'attachment'
    encoded_filename = quote(filename)
    return Response(
        content=b64decode(attachment['content_base64']),
        media_type=attachment.get('mime_type', 'application/octet-stream'),
        headers={'Content-Disposition': f"attachment; filename=\"{safe_filename}\"; filename*=UTF-8''{encoded_filename}"},
    )


@router.post('')
def create_employee(payload: EmployeePayload, user=Depends(require_roles('hr'))):
    repository = get_repository()
    _ensure_unique_fields(repository, payload)
    document = repository.upsert('employees', payload.model_dump())
    return ok(document, '员工创建成功')


@router.put('/self/archive')
def update_my_archive(payload: EmployeePayload, user=Depends(require_roles('employee'))):
    repository = get_repository()
    employee = _resolve_current_employee(user, repository)
    if not employee:
        raise HTTPException(status_code=404, detail='员工不存在')
    document = repository.upsert(
        'employees',
        {
            'id': employee['id'],
            **_build_employee_self_update_payload(employee, payload),
            'created_at': employee.get('created_at'),
        },
    )
    return ok(document, '个人档案更新成功')


@router.put('/{employee_id}')
def update_employee(employee_id: str, payload: EmployeePayload, user=Depends(require_roles('hr'))):
    repository = get_repository()
    current = repository.get('employees', employee_id)
    if not current:
        raise HTTPException(status_code=404, detail='员工不存在')
    if payload.employee_no != current.get('employee_no', current.get('employeeNo')):
        raise HTTPException(status_code=400, detail='编辑时不允许修改工号')
    _ensure_unique_fields(repository, payload, employee_id)
    document = repository.upsert('employees', {'id': employee_id, **payload.model_dump(), 'created_at': current.get('created_at')})
    return ok(document, '员工更新成功')


@router.delete('/{employee_id}')
def delete_employee(employee_id: str, user=Depends(require_roles('hr'))):
    repository = get_repository()
    if not repository.delete('employees', employee_id):
        raise HTTPException(status_code=404, detail='员工不存在')
    return ok(message='员工删除成功')
