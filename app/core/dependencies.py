from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.repository.postgres import DatabaseRepo
from app.services.email_service import EmailClient
from app.services.jwt_client import JWTClient


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения асинхронной сессии БД."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_repo(db: AsyncSession = Depends(get_db)) -> DatabaseRepo:
    """Dependency для получения репозитория."""
    return DatabaseRepo(db)


def get_jwt_client() -> JWTClient:
    return JWTClient()


def get_email_client() -> EmailClient:
    return EmailClient()