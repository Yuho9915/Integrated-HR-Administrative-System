from pymongo import MongoClient

from app.core.config import get_settings

settings = get_settings()
client = MongoClient(settings.mongodb_uri)
mongo_db = client[settings.mongodb_db]


def get_mongo_database():
    return mongo_db
