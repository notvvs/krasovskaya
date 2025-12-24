from fastapi import APIRouter

from app.api.v1.endpoints import users, soil

router = APIRouter()

# Подключаем все API эндпоинты v1
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(soil.router, prefix="/soil", tags=["soil"])
