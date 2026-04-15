from fastapi import APIRouter, Depends, HTTPException

from app.repositories.factory import get_repository
from app.schemas.common import LoginRequest, RefreshTokenRequest
from app.security.auth import get_current_user, manager
from app.services.seed import DEFAULT_DATA
from app.utils.responses import ok

router = APIRouter(prefix='/auth', tags=['auth'])


def _merge_user_profile(matched: dict) -> dict:
    repository = get_repository()
    employee = next((item for item in repository.list('employees') if str(item.get('employee_no') or item.get('employeeNo') or '').strip() == str(matched.get('employeeNo') or '').strip()), None)
    if not employee:
        return matched
    return {
        **matched,
        'hire_date': employee.get('hire_date', ''),
        'resignation_date': employee.get('resignation_date', ''),
        'political_status': employee.get('political_status', ''),
        'status': employee.get('status', ''),
        'phone': employee.get('phone', ''),
        'email': employee.get('email', ''),
        'gender': employee.get('gender', ''),
        'birth_date': employee.get('birth_date', ''),
        'ethnicity': employee.get('ethnicity', ''),
        'education': employee.get('education', ''),
        'graduate_school': employee.get('graduate_school', ''),
        'major': employee.get('major', ''),
        'job_level': employee.get('job_level', ''),
        'report_to': employee.get('report_to', ''),
        'work_location': employee.get('work_location', ''),
        'probation_end_date': employee.get('probation_end_date', ''),
        'contract_type': employee.get('contract_type', ''),
        'contract_sign_date': employee.get('contract_sign_date', ''),
        'contract_end_date': employee.get('contract_end_date', ''),
        'current_address': employee.get('current_address', ''),
        'emergency_contact': employee.get('emergency_contact', ''),
        'emergency_contact_phone': employee.get('emergency_contact_phone', ''),
        'id_card_attachments': employee.get('id_card_attachments', []),
        'education_certificate_attachments': employee.get('education_certificate_attachments', []),
        'labor_contract_attachments': employee.get('labor_contract_attachments', []),
        'medical_report_attachments': employee.get('medical_report_attachments', []),
    }


@router.post('/login')
def login(payload: LoginRequest):
    matched = next(
        (
            item for item in DEFAULT_DATA['users']
            if item['username'] == payload.username and item['password'] == payload.password and item['role'] == payload.role
        ),
        None,
    )
    if not matched:
        raise HTTPException(status_code=401, detail='用户名、密码或角色不正确')

    access_token = manager.create_access_token(payload.username, payload.role)
    refresh_token = manager.create_refresh_token(payload.username, payload.role)
    return ok({
        'token': access_token,
        'refreshToken': refresh_token,
        'user': _merge_user_profile({
            'name': matched['name'],
            'role': matched['role'],
            'department': matched['department'],
            'employeeNo': matched['employeeNo'],
            'position': matched['position'],
        }),
    }, '登录成功')


@router.post('/refresh')
def refresh_token(payload: RefreshTokenRequest):
    decoded = manager.decode_token(payload.refresh_token)
    if decoded.get('type') != 'refresh' or manager.is_refresh_token_revoked(decoded):
        raise HTTPException(status_code=401, detail='Refresh Token 无效')
    access_token = manager.create_access_token(decoded['sub'], decoded['role'])
    refresh_token = manager.create_refresh_token(decoded['sub'], decoded['role'])
    manager.revoke_refresh_token(payload.refresh_token)
    return ok({'token': access_token, 'refreshToken': refresh_token}, 'Token 刷新成功')


@router.post('/logout')
def logout(payload: RefreshTokenRequest, user=Depends(get_current_user)):
    manager.revoke_refresh_token(payload.refresh_token)
    return ok(message='退出登录成功')


@router.get('/me')
def me(user=Depends(get_current_user)):
    matched = next((item for item in DEFAULT_DATA['users'] if item['username'] == user['username']), None)
    return ok(_merge_user_profile(matched) if matched else None)
