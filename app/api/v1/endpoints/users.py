import secrets

from fastapi import APIRouter, Depends, HTTPException, Response, Request

from app.core.config import settings
from app.core.dependencies import get_repo, get_jwt_client, get_email_client, get_redis_client
from app.core.security import hash_password
from app.db.models import User
from app.repository.postgres import DatabaseRepo
from app.schemas.user import UserRegisterSchema, UserLoginSchema, UserVerifySchema, ResendCodeSchema
from app.services.email_service import EmailClient
from app.services.jwt_client import JWTClient
from app.services.redis_client import RedisClient

router = APIRouter()


@router.post("/register")
async def register(creds: UserRegisterSchema,
                   repo: DatabaseRepo = Depends(get_repo),
                   email_client: EmailClient = Depends(get_email_client),
                   redis: RedisClient = Depends(get_redis_client)):
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

    await repo.save_user(new_user)

    verify_code = ''.join(secrets.choice('0123456789') for _ in range(6))

    await redis.save_verify_code(creds.email, verify_code)

    await email_client.send_email(
        to_email=creds.email,
        subject="Подтверждение регистрации",
        body=f"Ваш код подтверждения: {verify_code}"
    )

    return {
        "message": "Код подтверждения отправлен",
        "email": creds.email
    }


@router.post("/login")
async def login(creds: UserLoginSchema,
                response: Response,
                repo: DatabaseRepo = Depends(get_repo),
                jwt_client: JWTClient = Depends(get_jwt_client)):
    """Вход в систему"""
    user = await repo.authenticate_user(creds.email, creds.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверные данные")

    # Проверяем, подтвержден ли email
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email не подтвержден")

    # Создаем токены с email пользователя (sub должен быть строкой по JWT спецификации)
    access_token = jwt_client.create_access_token(data={"sub": user.email, "email": user.email, "user_id": user.id})
    refresh_token = jwt_client.create_refresh_token(data={"sub": user.email, "email": user.email, "user_id": user.id})

    response.set_cookie(key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=False)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/verify")
async def verify(data: UserVerifySchema,
                 redis: RedisClient = Depends(get_redis_client),
                 repo: DatabaseRepo = Depends(get_repo)):
    user_code = data.verify_code
    correct_code = await redis.get_verify_code(data.email)

    if user_code == correct_code:
        await repo.verify_user(data.email)
        return {
            "message": "Пользователь подтвержден"
        }
    else:
        raise HTTPException(
            status_code=401, detail='Неверный код'
        )


@router.post("/resend-code")
async def resend_code(data: ResendCodeSchema,
                      redis: RedisClient = Depends(get_redis_client),
                      email_client: EmailClient = Depends(get_email_client)
                      ):

    verify_code = ''.join(secrets.choice('0123456789') for _ in range(6))

    await redis.save_verify_code(data.email, verify_code)

    await email_client.send_email(
        to_email=data.email,
        subject="Подтверждение регистрации",
        body=f"Ваш код подтверждения: {verify_code}"
    )

    return {
        'message': 'Код отправлен'
    }

@router.post("/refresh")
async def refresh_token(response: Response,
                        request: Request,
                        jwt_client: JWTClient = Depends(get_jwt_client)):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Токен отсутствует")

    payload = jwt_client.decode_token(refresh_token)
    user_email = payload.get('sub')  # email stored in sub
    user_id = payload.get('user_id')

    new_access_token = jwt_client.create_access_token(data={"sub": user_email, "email": user_email, "user_id": user_id})

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }