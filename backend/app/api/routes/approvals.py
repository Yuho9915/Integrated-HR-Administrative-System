from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.repositories.factory import get_repository
from app.schemas.common import BatchDecisionRequest, DecisionRequest
from app.security.auth import require_roles
from app.utils.responses import ok

router = APIRouter(prefix='/approvals', tags=['approvals'])

LEVEL_TO_USER = {
    'manager': 'manager',
    '经理': 'manager',
    'hr': 'admin.hr',
    '人事行政': 'admin.hr',
}

LEVEL_TO_LABEL = {
    'manager': '经理审批',
    '经理': '经理审批',
    'hr': '人事行政审批',
    '人事行政': '人事行政审批',
}


def _now_iso() -> str:
    return datetime.utcnow().isoformat()



def _resolve_level_label(level: str) -> str:
    return LEVEL_TO_LABEL.get(level, str(level or '审批中'))



def _resolve_username_by_level(level: str) -> str:
    return LEVEL_TO_USER.get(level, '')



def _resolve_user_display(repository, username: str) -> str:
    if not username:
        return ''
    user = next((item for item in repository.list('users') if item.get('username') == username), None)
    return user.get('name') if user else username



def _build_initial_history(row: dict, repository) -> list[dict]:
    applicant_name = row.get('applicant_name') or row.get('applicant') or '申请人'
    applicant_no = row.get('applicant_employee_no') or row.get('applicant_employeeNo') or row.get('applicant') or ''
    submit_time = row.get('apply_time') or row.get('created_at') or row.get('updated_at') or _now_iso()
    history = [
        {
            'node': '提交申请',
            'approver': applicant_name,
            'approver_username': row.get('created_by') or applicant_no,
            'time': submit_time,
            'result': '已提交',
            'comment': row.get('reason') or f"{row.get('type') or '审批'}申请已提交",
        }
    ]
    if row.get('status') in {'已通过', '已驳回', '已撤销'}:
        handler = row.get('handled_by', '')
        history.append({
            'node': _resolve_level_label(row.get('level', '')),
            'approver': _resolve_user_display(repository, handler) or handler or '审批人',
            'approver_username': handler,
            'time': row.get('updated_at') or submit_time,
            'result': row.get('status'),
            'comment': row.get('comment') or '',
        })
    return history



def _normalize_related_info(row: dict) -> list[dict]:
    related = row.get('related_info') or {}
    if isinstance(related, list):
        return related
    if isinstance(related, dict):
        return [{'label': str(key), 'value': value} for key, value in related.items() if value not in [None, '']]
    if related:
        return [{'label': '关联信息', 'value': related}]
    base = []
    if row.get('applicant_department'):
        base.append({'label': '所属部门', 'value': row['applicant_department']})
    if row.get('duration'):
        base.append({'label': '时长/数量', 'value': row['duration']})
    if row.get('level'):
        base.append({'label': '当前审批层级', 'value': _resolve_level_label(row['level'])})
    return base



def _normalize_approval(row: dict, repository) -> dict:
    approval_chain = row.get('approval_chain') or ([row.get('level')] if row.get('level') else [])
    current_step = row.get('current_step', 0)
    level = row.get('level') or (approval_chain[current_step] if current_step < len(approval_chain) else '')
    applicant = row.get('applicant') or row.get('applicant_name') or ''
    applicant_name = row.get('applicant_name') or applicant
    applicant_no = row.get('applicant_employee_no') or row.get('applicant_employeeNo') or ''
    if applicant and not applicant_name:
        applicant_name = applicant
    history = row.get('history') or _build_initial_history({**row, 'level': level}, repository)
    assigned_to = row.get('assigned_to') or _resolve_username_by_level(level)
    return {
        **row,
        'applicant': applicant_name,
        'applicant_name': applicant_name,
        'applicant_employee_no': applicant_no,
        'apply_time': row.get('apply_time') or row.get('created_at') or row.get('updated_at') or _now_iso(),
        'reason': row.get('reason') or f"{row.get('type') or '审批'}申请",
        'related_info': _normalize_related_info({**row, 'level': level}),
        'detail_content': row.get('detail_content') or row.get('duration') or '暂无明细内容',
        'history': history,
        'approval_chain': approval_chain,
        'current_step': current_step,
        'level': level,
        'level_label': _resolve_level_label(level),
        'assigned_to': assigned_to,
    }



def _can_view(row: dict, user: dict) -> bool:
    if row.get('assigned_to') == user['username']:
        return True
    if row.get('handled_by') == user['username']:
        return True
    return any(item.get('approver_username') == user['username'] for item in row.get('history', []))



def _require_visible(row: dict, user: dict):
    if not _can_view(row, user):
        raise HTTPException(status_code=403, detail='不可查看他人审批记录')



def _require_operable(row: dict, user: dict):
    _require_visible(row, user)
    if row.get('status') != '待审批':
        raise HTTPException(status_code=400, detail='仅待审批记录可操作')
    if row.get('assigned_to') != user['username']:
        raise HTTPException(status_code=403, detail='当前审批人不可操作该记录')



def _next_leave_status(level: str) -> str:
    if not level:
        return '已通过'
    return f"待{_resolve_level_label(level).replace('审批', '')}审批"



def _sync_leave_status(repository, row: dict, status: str, user: dict):
    if not row.get('source_id'):
        return
    if row.get('category') == '资产审批' and row.get('type') in {'办公用品领用', '资产领用', '办公设备领用'}:
        resource = 'office_supply_requests' if row.get('type') == '办公用品领用' else 'asset_requests'
        request_row = repository.get(resource, row['source_id'])
        if not request_row:
            return
        repository.upsert(resource, {**request_row, 'status': status, 'approver': user['username']})
        return
    if row.get('type') in {'公章使用', '会议室申请', '会议室预约', '用车申请', '转正申请', '调岗申请', '离职申请', '薪酬异动', '加班申请'}:
        request_row = repository.get('general_requests', row['source_id'])
        if not request_row:
            return
        repository.upsert('general_requests', {**request_row, 'status': status, 'approver': user['username']})
        return
    if row.get('category') != '人事审批':
        return
    if row.get('type') == '补卡申请':
        supplement_row = repository.get('supplements', row['source_id'])
        if not supplement_row:
            return
        repository.upsert('supplements', {**supplement_row, 'status': status, 'approver': user['username']})
        return
    leave_row = repository.get('leaves', row['source_id'])
    if not leave_row:
        return
    repository.upsert('leaves', {**leave_row, 'status': status, 'approver': user['username']})



def _apply_decision(repository, row: dict, payload: DecisionRequest, user: dict) -> dict:
    normalized = _normalize_approval(row, repository)
    _require_operable(normalized, user)
    if payload.decision == '已驳回' and not str(payload.comment or '').strip():
        raise HTTPException(status_code=400, detail='驳回时请填写审批意见')

    history = list(normalized.get('history', []))
    history.append({
        'node': normalized.get('level_label') or _resolve_level_label(normalized.get('level', '')),
        'approver': _resolve_user_display(repository, user['username']) or user['username'],
        'approver_username': user['username'],
        'time': _now_iso(),
        'result': payload.decision,
        'comment': (payload.comment or '').strip(),
    })

    approval_chain = normalized.get('approval_chain') or []
    current_step = int(normalized.get('current_step', 0) or 0)
    next_step = current_step + 1
    has_next = payload.decision == '已通过' and next_step < len(approval_chain)

    if has_next:
        next_level = approval_chain[next_step]
        updated = repository.upsert('approvals', {
            **normalized,
            'status': '待审批',
            'comment': (payload.comment or '').strip(),
            'handled_by': user['username'],
            'history': history,
            'current_step': next_step,
            'level': next_level,
            'assigned_to': _resolve_username_by_level(next_level),
        })
        _sync_leave_status(repository, normalized, _next_leave_status(next_level), user)
        return _normalize_approval(updated, repository)

    updated = repository.upsert('approvals', {
        **normalized,
        'status': payload.decision,
        'comment': (payload.comment or '').strip(),
        'handled_by': user['username'],
        'history': history,
    })
    _sync_leave_status(repository, normalized, payload.decision, user)
    return _normalize_approval(updated, repository)


@router.get('/overview')
def get_approval_overview(
    status: str = Query('', alias='status'),
    approval_type: str = Query('', alias='type'),
    user=Depends(require_roles('manager', 'hr')),
):
    repository = get_repository()
    rows = [_normalize_approval(row, repository) for row in repository.list('approvals')]
    rows = [row for row in rows if _can_view(row, user)]
    if status:
        rows = [row for row in rows if row.get('status') == status]
    if approval_type:
        rows = [row for row in rows if row.get('type') == approval_type]
    rows.sort(key=lambda item: item.get('apply_time') or item.get('updated_at') or '', reverse=True)
    grouped = {
        'human_resources': len([row for row in rows if row.get('category') == '人事审批']),
        'administration': len([row for row in rows if row.get('category') == '行政审批']),
        'assets': len([row for row in rows if row.get('category') == '资产审批']),
        'general': len([row for row in rows if row.get('category') == '综合审批']),
        'records': rows,
    }
    return ok(grouped)


@router.get('/{approval_id}')
def get_approval_detail(approval_id: str, user=Depends(require_roles('manager', 'hr'))):
    repository = get_repository()
    row = repository.get('approvals', approval_id)
    if not row:
        raise HTTPException(status_code=404, detail='审批记录不存在')
    normalized = _normalize_approval(row, repository)
    _require_visible(normalized, user)
    return ok(normalized)


@router.post('/batch-decision')
def batch_decide_approval(payload: BatchDecisionRequest, user=Depends(require_roles('manager', 'hr'))):
    repository = get_repository()
    updated_rows = []
    for approval_id in payload.ids:
        row = repository.get('approvals', approval_id)
        if not row:
            raise HTTPException(status_code=404, detail='存在审批记录不存在')
        updated_rows.append(_apply_decision(repository, row, DecisionRequest(decision=payload.decision, comment=payload.comment), user))
    return ok({'count': len(updated_rows), 'records': updated_rows}, '批量审批处理成功')


@router.post('/{approval_id}/decision')
def decide_approval(approval_id: str, payload: DecisionRequest, user=Depends(require_roles('manager', 'hr'))):
    repository = get_repository()
    row = repository.get('approvals', approval_id)
    if not row:
        raise HTTPException(status_code=404, detail='审批记录不存在')
    updated = _apply_decision(repository, row, payload, user)
    return ok(updated, '审批处理成功')
