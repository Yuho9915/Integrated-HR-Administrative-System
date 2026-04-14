from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class DocumentRecord(SQLModel, table=True):
    id: str = Field(primary_key=True)
    resource: str = Field(index=True)
    payload: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LoginAudit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    role: str
    login_at: datetime = Field(default_factory=datetime.utcnow)
