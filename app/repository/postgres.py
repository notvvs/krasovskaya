from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.security import verify_password
from app.db.models import User, SoilAnalysis
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
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def authenticate_user(self, email: str, password: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    async def verify_user(self, email: str):
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if not user:
            return None
        user.is_verified = True
        await self.db.commit()
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email without password check"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    # Soil Analysis methods
    async def save_soil_analysis(self, analysis: SoilAnalysis) -> int:
        """Save soil analysis to database"""
        try:
            self.db.add(analysis)
            await self.db.commit()
            await self.db.refresh(analysis)
            return analysis.id
        except Exception:
            await self.db.rollback()
            raise

    async def get_soil_analysis_by_id(self, analysis_id: int, user_id: int) -> SoilAnalysis | None:
        """Get soil analysis by ID for specific user"""
        result = await self.db.execute(
            select(SoilAnalysis).where(
                SoilAnalysis.id == analysis_id,
                SoilAnalysis.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_user_soil_analyses(self, user_id: int, limit: int = 50, offset: int = 0) -> list[SoilAnalysis]:
        """Get all soil analyses for a user"""
        result = await self.db.execute(
            select(SoilAnalysis)
            .where(SoilAnalysis.user_id == user_id)
            .order_by(desc(SoilAnalysis.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def delete_soil_analysis(self, analysis_id: int, user_id: int) -> bool:
        """Delete soil analysis"""
        analysis = await self.get_soil_analysis_by_id(analysis_id, user_id)
        if not analysis:
            return False

        try:
            await self.db.delete(analysis)
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            raise

    async def count_user_analyses(self, user_id: int) -> int:
        """Count total analyses for a user"""
        result = await self.db.execute(
            select(SoilAnalysis).where(SoilAnalysis.user_id == user_id)
        )
        return len(list(result.scalars().all()))