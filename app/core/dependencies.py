from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.repository.postgres import DatabaseRepo
from app.services.email_service import EmailClient
from app.services.jwt_client import JWTClient
from app.services.redis_client import RedisClient
from app.db.models import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения асинхронной сессии БД."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_repo(db: AsyncSession = Depends(get_db)) -> DatabaseRepo:
    """Dependency для получения репозитория."""
    return DatabaseRepo(db)


async def get_jwt_client() -> JWTClient:
    return JWTClient()


async def get_email_client() -> EmailClient:
    return EmailClient()

async def get_redis_client() -> RedisClient:
    return RedisClient()


async def get_current_user(
    authorization: str = Header(...),
    repo: DatabaseRepo = Depends(get_repo),
    jwt_client: JWTClient = Depends(get_jwt_client)
) -> User:
    """Get current user from JWT token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.replace("Bearer ", "")
    payload = jwt_client.decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Get user by email
    user = await repo.get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    return user