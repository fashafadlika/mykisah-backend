from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True, nullable=True) # Optional user ID if they are logged in
    reason_category = Column(String(100), nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
