import asyncio
from app.utils.ai_client import DoubaoClient
from app.services.seed import build_attachments

async def main():
    client = DoubaoClient()
    data = build_attachments('EMP-TEST')['id_card_attachments']
    result = await client.parse_id_card(data)
    print(result)

asyncio.run(main())
