from fastapi import APIRouter, Depends

from app.repositories.factory import get_repository
from app.schemas.common import AIChatRequest, IdCardParsePayload, ResumeParsePayload
from app.security.auth import require_roles
from app.services.ai_service import AIService
from app.utils.responses import ok

router = APIRouter(prefix='/ai', tags=['ai'])
service = AIService()


@router.get('/health')
async def ai_health(user=Depends(require_roles('employee', 'manager', 'hr'))):
    return ok(await service.health())


@router.post('/chat')
async def ai_chat(payload: AIChatRequest, user=Depends(require_roles('employee', 'manager', 'hr'))):
    result = await service.ask(prompt=payload.prompt, system_context=payload.system_context)
    return ok(result.model_dump())


@router.post('/resume/parse')
async def parse_resume(payload: ResumeParsePayload, user=Depends(require_roles('hr'))):
    return ok(await service.parse_resume(payload.content))


@router.post('/id-card/parse')
async def parse_id_card(payload: IdCardParsePayload, user=Depends(require_roles('hr'))):
    return ok(await service.parse_id_card(payload.attachments))
