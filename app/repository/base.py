from abc import ABC, abstractmethod

from app.db.models import User


class BaseRepo(ABC):
    @abstractmethod
    def save_user(self, user: User) -> int:
        """Сохранить пользователя и вернуть его ID"""
        pass

    @abstractmethod
    def check_user_exists(self, email: str) -> bool:
        """Проверить существование пользователя по email"""
        pass