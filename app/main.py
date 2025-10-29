from fastapi import FastAPI

from app.api.v1.endpoints import users
from app.db.session import Base, engine

# Создаем таблицы при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI(title="JWT Auth API", version="1.0.0")

# Подключаем роутеры
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

