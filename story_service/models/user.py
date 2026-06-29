from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    avatar_url = Column(String(255), nullable=True)
    bio = Column(String(255), nullable=True)
    role = Column(String(20), nullable=False, default="user") 
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Relationship ke tabel-tabel milik stories_service.
    # back_populates di-set di masing-masing model terkait (story.py, dll).
    stories = relationship("Story", back_populates="author")