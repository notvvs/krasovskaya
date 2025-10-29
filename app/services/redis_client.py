import redis.asyncio as redis

from app.core.config import settings


class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )

    async def save_verify_code(self, email: str, verify_code: str):
        await self.redis.set(f'verification:{email}', verify_code, ex=300)

    async def get_verify_code(self, email: str):
        return await self.redis.get(f'verification:{email}')