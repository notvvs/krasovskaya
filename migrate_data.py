"""
Скрипт для миграции данных из SQLite в PostgreSQL

Использование:
    python migrate_data.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, User

# SQLite соединение
SQLITE_URL = "sqlite:///./app.db"
sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SQLiteSession = sessionmaker(bind=sqlite_engine)

# PostgreSQL соединение (из settings)
from app.core.config import settings
from app.db.session import engine as pg_engine, SessionLocal as PGSession

def migrate_users():
    """Мигрирует пользователей из SQLite в PostgreSQL"""

    # Создаем таблицы в PostgreSQL
    print("Создаем таблицы в PostgreSQL...")
    Base.metadata.create_all(bind=pg_engine)

    # Получаем данные из SQLite
    sqlite_session = SQLiteSession()
    users = sqlite_session.query(User).all()

    if not users:
        print("В SQLite нет пользователей для миграции")
        sqlite_session.close()
        return

    print(f"Найдено {len(users)} пользователей в SQLite")

    # Переносим в PostgreSQL
    pg_session = PGSession()
    try:
        for user in users:
            # Создаем новый объект User с теми же данными
            new_user = User(
                id=user.id,
                username=user.username,
                email=user.email,
                hashed_password=user.hashed_password,
                is_verified=user.is_verified
            )
            pg_session.merge(new_user)  # merge вместо add для обработки конфликтов

        pg_session.commit()
        print(f"Успешно перенесено {len(users)} пользователей в PostgreSQL")

    except Exception as e:
        pg_session.rollback()
        print(f"Ошибка при миграции: {e}")
        raise
    finally:
        pg_session.close()
        sqlite_session.close()

if __name__ == "__main__":
    print("Начинаем миграцию данных из SQLite в PostgreSQL...")
    print(f"PostgreSQL URL: {settings.DATABASE_URL.replace(settings.DB_PASSWORD.get_secret_value(), '***')}")

    confirm = input("Продолжить? (yes/no): ")
    if confirm.lower() == 'yes':
        migrate_users()
        print("Миграция завершена!")
    else:
        print("Миграция отменена")
