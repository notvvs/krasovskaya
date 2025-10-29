from datetime import datetime, timezone, timedelta

import jwt
from fastapi import HTTPException

from app.core.config import settings


class JWTClient:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM

    def create_access_token(self, data: dict, expires_minutes=settings.ACCESS_EXPIRE_MINUTES):
        payload = data.copy()
        payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        payload["type"] = "access"
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: dict, expires_days=settings.REFRESH_EXPIRE_DAYS):
        payload = data.copy()
        payload["exp"] = datetime.now(timezone.utc) + timedelta(days=expires_days)
        payload["type"] = "refresh"
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str):
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh-токен истёк")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Некорректный токен")
