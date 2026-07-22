from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class StoryTakedown(Base):
    """
    Mencatat riwayat takedown novel oleh admin.
    Dibuat saat admin menerima laporan dan men-takedown novel.
    """
    __tablename__ = "story_takedowns"

    id          = Column(Integer, primary_key=True, index=True)
    story_id    = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    admin_id    = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reason      = Column(Text, nullable=False)
    report_id   = Column(Integer, nullable=True)
    taken_at    = Column(DateTime(timezone=True), server_default=func.now())
