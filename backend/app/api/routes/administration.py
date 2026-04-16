from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.repositories.factory import get_repository
from app.schemas.common import AssetPayload, AssetRequestPayload, GeneralRequestPayload, OfficeSupplyRequestPayload
from app.security.auth import require_roles
from app.utils.responses import ok

router = APIRouter(prefix='/administration', tags=['administration'])


def _parse_datetime(value: str):
    try:
        return datetime.fromisoformat(str(value).replace(' ', 'T')) if value else None
    except ValueError:
        return None


def _time_overlaps(start_at: str, end_at: str, other_start: str, other_end: str) -> bool:
    start = _parse_datetime(start_at)
    end = _parse_datetime(end_at)
    other_start_dt = _parse_datetime(other_start)
    other_end_dt = _parse_datetime(other_end)
    if not all([start, end, other_start_dt, other_end_dt]):
        return False
    return max(start, other_start_dt) < min(end, other_end_dt)


def _validate_general_resource_conflict(repository, payload: GeneralRequestPayload):
    resource_types = {'公章使用', '会议室申请', '会议室预约', '用车申请'}
    if payload.request_type not in resource_types:
        return
    rows = repository.list('general_requests')
    active_rows = [row for row in rows if row.get('request_type') == payload.request_type and row.get('status') in {'待审批', '待人事行政审批', '待经理审批', '已通过'}]

    if payload.request_type == '公章使用':
        occupied = next((row for row in active_rows if row.get('resource_code') == payload.resource_code), None)
        if occupied:
            raise HTTPException(status_code=400, detail='当前印章已有待处理或生效中的使用申请，请稍后再试')
        return

    conflict = next((
        row for row in active_rows
        if row.get('resource_code') == payload.resource_code
        and _time_overlaps(payload.start_at, payload.end_at, row.get('start_at', ''), row.get('end_at', ''))
    ), None)
    if conflict:
        label = '会议室' if payload.request_type in {'会议室申请', '会议室预约'} else '车辆'
        raise HTTPException(status_code=400, detail=f'{label}在该时间段已被占用，请调整时间后重试')


@router.get('/summary')
def get_administration_summary(user=Depends(require_roles('employee', 'hr', 'boss'))):
    repository = get_repository()
    rows = repository.list('assets')
    return ok({
        'records': rows,
        'low_stock_items': len([row for row in rows if row.get('status') == '低库存']),
        'repair_tickets': len([row for row in rows if row.get('status') == '待维修']),
        'meeting_rooms': 2,
        'vehicles': 1,
    })


@router.post('/assets')
def create_asset(payload: AssetPayload, user=Depends(require_roles('hr'))):
    document = get_repository().upsert('assets', payload.model_dump())
    return ok(document, '资产已创建')


@router.get('/office-supply-requests')
def get_office_supply_requests(user=Depends(require_roles('employee', 'hr', 'boss'))):
    repository = get_repository()
    rows = repository.list('office_supply_requests')
    if user['role'] == 'employee':
        employee = next((item for item in repository.list('users') if item['username'] == user['username']), None)
        employee_no = employee.get('employeeNo') if employee else ''
        rows = [row for row in rows if row.get('employee_no') == employee_no]
    rows.sort(key=lambda item: item.get('created_at', ''), reverse=True)
    return ok(rows)


@router.post('/office-supply-requests')
def create_office_supply_request(payload: OfficeSupplyRequestPayload, user=Depends(require_roles('employee'))):
    repository = get_repository()
    employee = next((item for item in repository.list('employees') if (item.get('employee_no') or item.get('employeeNo')) == payload.employee_no), None)
    applicant_name = employee.get('name') if employee else payload.employee_no
    applicant_department = employee.get('department') if employee else ''
    document = repository.upsert('office_supply_requests', {
        **payload.model_dump(),
        'type': '办公用品领用',
        'status': '待审批',
        'approver': '于浩',
        'start_at': payload.needed_by or '',
        'end_at': payload.needed_by or '',
        'leave_type': '办公用品领用',
    })
    repository.upsert('approvals', {
        'category': '资产审批',
        'applicant': applicant_name,
        'applicant_name': applicant_name,
        'applicant_employee_no': payload.employee_no,
        'applicant_department': applicant_department,
        'type': '办公用品领用',
        'duration': f'{payload.item_name} {payload.quantity} 件',
        'status': '待审批',
        'level': '人事行政',
        'assigned_to': 'admin.hr',
        'source_id': document['id'],
        'apply_time': document.get('created_at'),
        'reason': payload.reason,
        'detail_content': payload.reason,
        'related_info': [
            {'label': '用品名称', 'value': payload.item_name},
            {'label': '申请数量', 'value': payload.quantity},
            {'label': '需求时间', 'value': payload.needed_by or '尽快'},
        ],
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
    return ok({'request': document}, '办公用品领用申请已提交')


@router.get('/asset-requests')
def get_asset_requests(user=Depends(require_roles('employee', 'hr', 'boss'))):
    repository = get_repository()
    rows = repository.list('asset_requests')
    if user['role'] == 'employee':
        employee = next((item for item in repository.list('users') if item['username'] == user['username']), None)
        employee_no = employee.get('employeeNo') if employee else ''
        rows = [row for row in rows if row.get('employee_no') == employee_no]
    rows.sort(key=lambda item: item.get('created_at', ''), reverse=True)
    return ok(rows)


@router.post('/asset-requests')
def create_asset_request(payload: AssetRequestPayload, user=Depends(require_roles('employee'))):
    repository = get_repository()
    asset_rows = repository.list('assets')
    asset_row = next((item for item in asset_rows if item.get('code') == payload.asset_code or item.get('asset') == payload.asset_name or item.get('name') == payload.asset_name), None)
    if not asset_row:
        raise HTTPException(status_code=404, detail='资产不存在')
    available_count = len([item for item in asset_row.get('details', []) if item.get('status') in {'闲置', '库存', '可用'}])
    if available_count <= 0:
        raise HTTPException(status_code=400, detail='当前资产库存不足，暂不可领用')
    if payload.quantity > available_count:
        raise HTTPException(status_code=400, detail=f'当前最多可领用 {available_count} 件')

    employee = next((item for item in repository.list('employees') if (item.get('employee_no') or item.get('employeeNo')) == payload.employee_no), None)
    applicant_name = employee.get('name') if employee else payload.employee_no
    applicant_department = employee.get('department') if employee else ''
    document = repository.upsert('asset_requests', {
        **payload.model_dump(),
        'type': payload.request_type,
        'status': '待审批',
        'approver': '于浩',
        'start_at': payload.needed_by or '',
        'end_at': payload.needed_by or '',
        'leave_type': payload.request_type,
        'asset_type': asset_row.get('type', ''),
    })
    repository.upsert('approvals', {
        'category': '资产审批',
        'applicant': applicant_name,
        'applicant_name': applicant_name,
        'applicant_employee_no': payload.employee_no,
        'applicant_department': applicant_department,
        'type': payload.request_type,
        'duration': f'{payload.asset_name} {payload.quantity} 件',
        'status': '待审批',
        'level': '人事行政',
        'assigned_to': 'admin.hr',
        'source_id': document['id'],
        'apply_time': document.get('created_at'),
        'reason': payload.reason,
        'detail_content': payload.reason,
        'related_info': [
            {'label': '资产编码', 'value': payload.asset_code or asset_row.get('code', '')},
            {'label': '资产名称', 'value': payload.asset_name},
            {'label': '资产类型', 'value': asset_row.get('type', '')},
            {'label': '申请数量', 'value': payload.quantity},
            {'label': '可用库存', 'value': available_count},
            {'label': '需求时间', 'value': payload.needed_by or '尽快'},
        ],
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
    return ok({'request': document}, f'{payload.request_type}已提交')


@router.get('/general-requests')
def get_general_requests(user=Depends(require_roles('employee', 'hr', 'boss', 'manager'))):
    repository = get_repository()
    rows = repository.list('general_requests')
    if user['role'] == 'employee':
        employee = next((item for item in repository.list('users') if item['username'] == user['username']), None)
        employee_no = employee.get('employeeNo') if employee else ''
        rows = [row for row in rows if row.get('employee_no') == employee_no]
    rows.sort(key=lambda item: item.get('created_at', ''), reverse=True)
    return ok(rows)


@router.post('/general-requests')
def create_general_request(payload: GeneralRequestPayload, user=Depends(require_roles('employee'))):
    repository = get_repository()
    _validate_general_resource_conflict(repository, payload)
    employee = next((item for item in repository.list('employees') if (item.get('employee_no') or item.get('employeeNo')) == payload.employee_no), None)
    applicant_name = employee.get('name') if employee else payload.employee_no
    applicant_department = employee.get('department') if employee else ''

    category_map = {
        '公章使用': '行政审批',
        '会议室申请': '行政审批',
        '会议室预约': '行政审批',
        '用车申请': '行政审批',
        '转正申请': '人事审批',
        '调岗申请': '人事审批',
        '离职申请': '人事审批',
        '薪酬异动': '人事审批',
        '加班申请': '人事审批',
    }
    level_map = {
        '公章使用': '人事行政',
        '会议室申请': '人事行政',
        '会议室预约': '人事行政',
        '用车申请': '人事行政',
        '转正申请': 'hr',
        '调岗申请': 'manager',
        '离职申请': 'hr',
        '薪酬异动': 'boss',
        '加班申请': 'manager',
    }
    chain_map = {
        '转正申请': ['hr', 'boss'],
        '调岗申请': ['manager', 'hr'],
        '离职申请': ['manager', 'hr'],
        '薪酬异动': ['manager', 'boss'],
        '加班申请': ['manager', 'hr'],
    }

    document = repository.upsert('general_requests', {
        **payload.model_dump(),
        'type': payload.request_type,
        'leave_type': payload.request_type,
        'status': '待审批',
        'approver': '于浩' if category_map.get(payload.request_type) == '行政审批' else '王嘉铭',
        'title': payload.title or payload.resource_name or payload.request_type,
    })

    related_info = []
    if payload.resource_code:
        related_info.append({'label': '资源编码', 'value': payload.resource_code})
    if payload.resource_name:
        related_info.append({'label': '资源名称', 'value': payload.resource_name})
    if payload.quantity:
        related_info.append({'label': '申请数量', 'value': payload.quantity})
    if payload.start_at:
        related_info.append({'label': '开始时间', 'value': payload.start_at})
    if payload.end_at:
        related_info.append({'label': '结束时间', 'value': payload.end_at})
    if payload.days:
        related_info.append({'label': '时长/天数', 'value': payload.days})
    if payload.needed_by:
        related_info.append({'label': '需求时间', 'value': payload.needed_by})
    for key, value in (payload.meta or {}).items():
        if value not in ['', None]:
            related_info.append({'label': key, 'value': value})

    approval_chain = chain_map.get(payload.request_type, [level_map.get(payload.request_type, 'hr')])
    current_level = approval_chain[0]
    repository.upsert('approvals', {
        'category': category_map.get(payload.request_type, '综合审批'),
        'applicant': applicant_name,
        'applicant_name': applicant_name,
        'applicant_employee_no': payload.employee_no,
        'applicant_department': applicant_department,
        'type': payload.request_type,
        'duration': payload.title or payload.resource_name or payload.request_type,
        'status': '待审批',
        'level': current_level,
        'approval_chain': approval_chain,
        'current_step': 0,
        'assigned_to': 'admin.hr' if current_level in {'人事行政', 'hr'} else 'manager' if current_level == 'manager' else 'boss',
        'source_id': document['id'],
        'apply_time': document.get('created_at'),
        'reason': payload.reason,
        'detail_content': payload.reason,
        'related_info': related_info,
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
    return ok({'request': document}, f'{payload.request_type}已提交')
