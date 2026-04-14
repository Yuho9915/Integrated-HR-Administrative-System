import asyncio
import json

from app.core.config import get_settings
from app.services.seed import build_attachments
import httpx

settings = get_settings()

async def main():
    attachments = build_attachments('EMP-TEST')['id_card_attachments']
    payload = {
        'model': settings.ark_model,
        'messages': [
            {'role': 'system', 'content': '你是HR身份证OCR助手，只返回JSON，不要解释。'},
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': '请识别身份证正反面图片，返回 name, gender, ethnicity, birth_date, id_card_no, success。'},
                    *[
                        {'type': 'image_url', 'image_url': {'url': f"data:{item['mime_type']};base64,{item['content_base64']}"}}
                        for item in attachments
                    ],
                ],
            },
        ],
        'temperature': 0.1,
    }
    headers = {
        'Authorization': f'Bearer {settings.ark_api_key}',
        'Content-Type': 'application/json',
    }
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(f"{settings.ark_base_url.rstrip('/')}/chat/completions", json=payload, headers=headers)
        print('status=', response.status_code)
        print(response.text)

asyncio.run(main())
