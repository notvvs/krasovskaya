from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.endpoints import users
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup: Создаем таблицы при запуске
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown: Закрываем соединения
    await engine.dispose()


app = FastAPI(
    title="JWT Auth API",
    version="1.0.0",
    lifespan=lifespan
)

# Подключаем роутеры
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host='0.0.0.0',
        port=8000,
        reload=False
    )