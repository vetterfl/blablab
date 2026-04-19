from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    default_model = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    presets = relationship("Preset", back_populates="user", cascade="all, delete-orphan")


class Preset(Base):
    __tablename__ = "presets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    slug = Column(String, nullable=False)
    label = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    model = Column(String, nullable=True)
    subject_field = Column(Boolean, default=False)
    position = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="presets")

    __table_args__ = (
        UniqueConstraint("user_id", "slug", name="uq_user_slug"),
    )
