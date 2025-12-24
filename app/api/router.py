from fastapi import APIRouter

from app.api.v1.router import router as v1_router
from app.api.v1.endpoints.frontend import router as frontend_router

router = APIRouter()

# Подключаем роутеры разных версий API
router.include_router(v1_router, prefix="/api/v1")

# Подключаем фронтенд страницы без префикса (/, /login, /register и т.д.)
router.include_router(frontend_router, tags=["frontend"])
