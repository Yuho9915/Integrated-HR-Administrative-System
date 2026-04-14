from app.core.config import get_settings
from app.repositories.repository import Repository


settings = get_settings()


def get_repository() -> Repository:
    return Repository(settings.db_driver)
