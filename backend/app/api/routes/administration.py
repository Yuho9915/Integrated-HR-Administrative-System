from fastapi import APIRouter, Depends

from app.repositories.factory import get_repository
from app.schemas.common import AssetPayload
from app.security.auth import require_roles
from app.utils.responses import ok

router = APIRouter(prefix='/administration', tags=['administration'])


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
