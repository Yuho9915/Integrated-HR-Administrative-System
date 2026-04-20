from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.db.sqlite import create_sqlite_tables

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version='1.0.0',
    summary='人事行政一体化HR系统后端服务',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', *[origin for origin in settings.cors_origins if origin != 'http://localhost:5173']],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
def on_startup() -> None:
    if settings.db_driver.lower() == 'sqlite':
        create_sqlite_tables()


@app.get('/')
def root() -> dict:
    return {
        'message': '人事行政一体化HR系统 API 已启动',
        'environment': settings.app_env,
        'database_driver': settings.db_driver,
    }


app.include_router(api_router)
