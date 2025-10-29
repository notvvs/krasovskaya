import secrets

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_repo, get_jwt_client, get_email_client
from app.core.security import hash_password
from app.db.models import User
from app.repository.postgres import DatabaseRepo
from app.schemas.user import UserRegisterSchema, UserLoginSchema
from app.services.email_service import EmailClient
from app.services.jwt_client import JWTClient

router = APIRouter()


@router.post("/register")
async def register(creds: UserRegisterSchema, repo: DatabaseRepo = Depends(get_repo), email_client: EmailClient = Depends(get_email_client)):
    """Регистрация нового пользователя"""
    # Проверяем существование пользователя
    if await repo.check_user_exists(creds.email):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    # Создаем нового пользователя
    new_user = User(
        username=creds.username,
        email=creds.email,
        hashed_password=hash_password(creds.password),
        is_verified=False
    )

    verify_code = ''.join(secrets.choice('0123456789') for _ in range(6))

    await email_client.send_email(
        to_email=creds.email,
        subject="Подтверждение регистрации",
        body=f"Ваш код подтверждения: {verify_code}"
    )

    user_id = await repo.save_user(new_user)

    return {
        "message": "Код подтверждения отправлен",
        "email": creds.email
    }

@router.post("/login")
async def login(creds: UserLoginSchema, repo: DatabaseRepo = Depends(get_repo), jwt_client: JWTClient = Depends(get_jwt_client)):
    """Вход в систему"""
    user = await repo.authenticate_user(creds.email, creds.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверные данные")

    # Проверяем, подтвержден ли email
    # if not user.is_verified:
    #     raise HTTPException(status_code=403, detail="Email не подтвержден")

    # Создаем токены с email пользователя
    access_token = jwt_client.create_access_token(data={"sub": user.email})
    refresh_token = jwt_client.create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

