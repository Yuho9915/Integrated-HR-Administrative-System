from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = '人事行政一体化HR系统'
    app_env: str = 'development'
    app_host: str = '0.0.0.0'
    app_port: int = 8000
    cors_origins: list[str] | str = ['http://localhost:5173']

    db_driver: str = 'sqlite'
    sqlite_path: str = './data/hr_system.db'
    mongodb_uri: str = 'mongodb://localhost:27017'
    mongodb_db: str = 'hr_system'

    jwt_secret: str = 'yuho-hr-system-secret'
    jwt_algorithm: str = 'HS256'
    jwt_expire_minutes: int = 1440

    ark_base_url: str = 'https://ark.cn-beijing.volces.com/api/v3'
    ark_api_key: str = ''
    ark_model: str = 'Yuho/ep-20260121115833-nw6t4'

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return value

    @property
    def sqlite_url(self) -> str:
        path = Path(self.sqlite_path)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[2] / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return f'sqlite:///{path.as_posix()}'


@lru_cache
def get_settings() -> Settings:
    return Settings()
