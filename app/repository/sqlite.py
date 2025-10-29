from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.db.models import User
from app.repository.base import BaseRepo


class DatabaseRepo(BaseRepo):
    def __init__(self, db: Session):
        self.db = db

    def save_user(self, user: User) -> int:
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user.id
        except Exception:
            self.db.rollback()
            raise

    def check_user_exists(self, email: str) -> bool:
        return self.db.query(User).filter(User.email == email).first() is not None

    def authenticate_user(self, email: str, password: str) -> User | None:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user