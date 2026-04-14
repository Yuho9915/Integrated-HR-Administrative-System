from typing import Any

from pymongo.errors import PyMongoError
from sqlmodel import select

from app.db.base import DatabaseAdapter
from app.db.mongodb import get_mongo_database
from app.db.sqlite import get_sqlite_session
from app.models.entities import AttendanceRecord, Employee, LeaveApplication

RESOURCE_MODEL_MAP = {
    'employees': Employee,
    'attendance_records': AttendanceRecord,
    'leave_applications': LeaveApplication,
}


class SQLiteAdapter(DatabaseAdapter):
    def healthcheck(self) -> dict[str, Any]:
        with get_sqlite_session() as session:
            session.exec(select(Employee).limit(1))
        return {'driver': 'sqlite', 'status': 'connected'}

    def list_collection(self, resource: str) -> list[dict[str, Any]]:
        model = RESOURCE_MODEL_MAP[resource]
        with get_sqlite_session() as session:
            rows = session.exec(select(model)).all()
            return [row.model_dump() for row in rows]

    def create_record(self, resource: str, payload: dict[str, Any]) -> dict[str, Any]:
        model = RESOURCE_MODEL_MAP[resource]
        with get_sqlite_session() as session:
            instance = model(**payload)
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance.model_dump()


class MongoAdapter(DatabaseAdapter):
    def healthcheck(self) -> dict[str, Any]:
        get_mongo_database().command('ping')
        return {'driver': 'mongodb', 'status': 'connected'}

    def list_collection(self, resource: str) -> list[dict[str, Any]]:
        documents = list(get_mongo_database()[resource].find({}, {'_id': 0}))
        return documents

    def create_record(self, resource: str, payload: dict[str, Any]) -> dict[str, Any]:
        collection = get_mongo_database()[resource]
        collection.insert_one(payload)
        return payload


def safe_healthcheck(adapter: DatabaseAdapter) -> dict[str, Any]:
    try:
        return adapter.healthcheck()
    except PyMongoError as exc:
        return {'driver': 'mongodb', 'status': 'error', 'detail': str(exc)}
    except Exception as exc:
        return {'driver': 'sqlite', 'status': 'error', 'detail': str(exc)}
