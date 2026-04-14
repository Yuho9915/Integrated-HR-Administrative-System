from sqlmodel import SQLModel, Session, create_engine

from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.sqlite_url, echo=False, connect_args={'check_same_thread': False})


def create_sqlite_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_sqlite_session() -> Session:
    return Session(engine)
