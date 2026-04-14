import json
from datetime import datetime
from typing import Any
from uuid import uuid4

from pymongo.errors import PyMongoError
from sqlmodel import select

from app.db.mongodb import get_mongo_database
from app.db.sqlite import get_sqlite_session
from app.models.entities import DocumentRecord


class Repository:
    def __init__(self, driver: str):
        self.driver = driver.lower()

    def _serialize(self, payload: dict[str, Any]) -> dict[str, Any]:
        return json.loads(json.dumps(payload, ensure_ascii=False, default=str))

    def list(self, resource: str) -> list[dict[str, Any]]:
        if self.driver == 'mongodb':
            return list(get_mongo_database()[resource].find({}, {'_id': 0}))

        with get_sqlite_session() as session:
            rows = session.exec(select(DocumentRecord).where(DocumentRecord.resource == resource)).all()
            return [json.loads(row.payload) for row in rows]

    def get(self, resource: str, record_id: str) -> dict[str, Any] | None:
        items = self.list(resource)
        for item in items:
            if item.get('id') == record_id:
                return item
        return None

    def upsert(self, resource: str, payload: dict[str, Any]) -> dict[str, Any]:
        document = self._serialize(payload)
        document.setdefault('id', str(uuid4()))
        document['updated_at'] = datetime.utcnow().isoformat()
        document.setdefault('created_at', document['updated_at'])

        if self.driver == 'mongodb':
            get_mongo_database()[resource].replace_one({'id': document['id']}, document, upsert=True)
            return document

        with get_sqlite_session() as session:
            existing = session.exec(select(DocumentRecord).where(DocumentRecord.id == document['id'])).first()
            payload_text = json.dumps(document, ensure_ascii=False)
            if existing:
                existing.resource = resource
                existing.payload = payload_text
                existing.updated_at = datetime.utcnow()
            else:
                session.add(DocumentRecord(id=document['id'], resource=resource, payload=payload_text))
            session.commit()
        return document

    def delete(self, resource: str, record_id: str) -> bool:
        if self.driver == 'mongodb':
            result = get_mongo_database()[resource].delete_one({'id': record_id})
            return result.deleted_count > 0

        with get_sqlite_session() as session:
            row = session.exec(
                select(DocumentRecord).where(DocumentRecord.id == record_id, DocumentRecord.resource == resource)
            ).first()
            if not row:
                return False
            session.delete(row)
            session.commit()
            return True

    def health(self) -> dict[str, Any]:
        try:
            if self.driver == 'mongodb':
                get_mongo_database().command('ping')
                return {'driver': 'mongodb', 'status': 'connected'}

            with get_sqlite_session() as session:
                session.exec(select(DocumentRecord).limit(1))
            return {'driver': 'sqlite', 'status': 'connected'}
        except PyMongoError as exc:
            return {'driver': 'mongodb', 'status': 'error', 'detail': str(exc)}
        except Exception as exc:
            return {'driver': 'sqlite', 'status': 'error', 'detail': str(exc)}
