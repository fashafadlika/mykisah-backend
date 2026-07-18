from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
import datetime
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    story_id = Column(Integer, nullable=True)
    chapter_id = Column(Integer, nullable=True)
    type = Column(String(50), nullable=False)
    message = Column(String(255), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, server_default=func.now())
