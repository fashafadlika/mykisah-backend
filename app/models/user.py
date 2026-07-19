from sqlalchemy import Column, Integer, String, Date, Text, Boolean, Enum, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

import enum


class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    birthdate = Column(Date, nullable=True)
    bio = Column(Text, nullable=True)
    profile_picture = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    otp_code = Column(String(10), nullable=True)
    otp_expired_at = Column(TIMESTAMP, nullable=True)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.user)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")