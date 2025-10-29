from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# PostgreSQL БД
DATABASE_URL = settings.DATABASE_URL

# Движок
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    echo=False  # Логирование SQL запросов (можно включить для отладки)
)

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Базовый класс для моделей (SQLAlchemy 2.0 стиль)
class Base(DeclarativeBase):
    pass