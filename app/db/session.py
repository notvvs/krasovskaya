from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# PostgreSQL БД
DATABASE_URL = settings.DATABASE_URL

# Асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    echo=False,  # Логирование SQL запросов (можно включить для отладки)
    future=True
)

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


# Базовый класс для моделей (SQLAlchemy 2.0 стиль)
class Base(DeclarativeBase):
    pass