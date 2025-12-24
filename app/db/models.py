from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    is_verified: Mapped[bool] = mapped_column(default=False)

    # Relationship to soil analyses
    soil_analyses: Mapped[list["SoilAnalysis"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class SoilAnalysis(Base):
    __tablename__ = "soil_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    # Image info
    image_filename: Mapped[str]
    image_path: Mapped[str]

    # Analysis results
    soil_type: Mapped[str] = mapped_column(index=True)
    confidence: Mapped[float]

    # Soil information (JSON stored as TEXT)
    description: Mapped[str] = mapped_column(Text)
    characteristics: Mapped[str] = mapped_column(Text)
    recommended_crops: Mapped[str] = mapped_column(Text)
    recommendations: Mapped[str] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    # Relationship to user
    user: Mapped["User"] = relationship(back_populates="soil_analyses")