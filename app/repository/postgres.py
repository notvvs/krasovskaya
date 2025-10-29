from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import verify_password
from app.db.models import User
from app.repository.base import BaseRepo


class DatabaseRepo(BaseRepo):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_user(self, user: User) -> int:
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user.id
        except Exception:
            await self.db.rollback()
            raise

    async def check_user_exists(self, email: str) -> bool:
        result = await self.db.execute(
            select(User).filter(User.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def authenticate_user(self, email: str, password: str) -> User | None:
        result = await self.db.execute(
            select(User).filter(User.email == email)
        )
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user