from app.core.config import get_settings
from app.services.database import MongoAdapter, SQLiteAdapter

settings = get_settings()


def get_database_adapter():
    if settings.db_driver.lower() == 'mongodb':
        return MongoAdapter()
    return SQLiteAdapter()
