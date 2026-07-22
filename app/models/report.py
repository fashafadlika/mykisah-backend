from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id              = Column(Integer, primary_key=True, index=True)
    story_id        = Column(Integer, index=True)
    reporter_id     = Column(Integer, index=True, nullable=True)
    reason          = Column(String(100), nullable=False)
    message         = Column(Text, nullable=True)
    status          = Column(String(20), default="pending")
    reviewed_by     = Column(Integer, nullable=True)
    reviewed_at     = Column(DateTime(timezone=True), nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
