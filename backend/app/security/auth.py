from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings

settings = get_settings()
security = HTTPBearer(auto_error=False)


class TokenManager:
    def __init__(self) -> None:
        self.revoked_refresh_tokens: set[str] = set()

    def create_access_token(self, username: str, role: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        payload = {'sub': username, 'role': role, 'type': 'access', 'exp': expire}
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    def create_refresh_token(self, username: str, role: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
        payload = {'sub': username, 'role': role, 'type': 'refresh', 'jti': str(uuid4()), 'exp': expire}
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

    def revoke_refresh_token(self, token: str) -> None:
        payload = self.decode_token(token)
        self.revoked_refresh_tokens.add(payload['jti'])

    def is_refresh_token_revoked(self, payload: dict) -> bool:
        return payload.get('jti') in self.revoked_refresh_tokens


manager = TokenManager()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='未登录或登录已失效')
    try:
        payload = manager.decode_token(credentials.credentials)
        if payload.get('type') != 'access':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token 类型错误')
        return {'username': payload['sub'], 'role': payload['role']}
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token 已过期') from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token 无效') from exc


def require_roles(*roles: str):
    def dependency(user: dict = Depends(get_current_user)) -> dict:
        if user['role'] not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='当前角色无访问权限')
        return user

    return dependency
