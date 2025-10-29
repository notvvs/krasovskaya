from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repository.sqlite import DatabaseRepo
from app.services.email_service import EmailClient
from app.services.jwt_client import JWTClient


def get_db() -> Generator[Session, None, None]:
    """Dependency для получения сессии БД."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_repo(db: Session = Depends(get_db)) -> DatabaseRepo:
    """Dependency для получения репозитория."""
    return DatabaseRepo(db)

def get_jwt_client() -> JWTClient:
    return JWTClient()

def get_email_client() -> EmailClient:
    return EmailClient()