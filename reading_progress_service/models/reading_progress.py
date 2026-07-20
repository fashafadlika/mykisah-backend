# models/reading_progress.py

from sqlalchemy import Column, Integer, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func
from database import Base


class ReadingProgress(Base):
    """
    Menyimpan progress baca terakhir user per cerita.
    Unique per (user_id, story_id) — di-upsert setiap kali user membuka chapter baru.
    """
    __tablename__ = "reading_progress"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)
    story_id = Column(Integer, index=True, nullable=False)
    chapter_id = Column(Integer, nullable=False)
    last_read_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "story_id", name="uq_user_story_progress"),
    )
