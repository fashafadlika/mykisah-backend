from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class ReadingHistory(Base):
    """
    Menyimpan posisi terakhir baca pengguna (chapter terakhir dibuka),
    supaya saat aplikasi dibuka kembali pengguna bisa lanjut tanpa
    mencari ulang. Idealnya unique per (user_id, story_id) -> upsert.
    """
    __tablename__ = "reading_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    last_read_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    user = relationship("User", back_populates="reading_histories")
    story = relationship("Story", back_populates="reading_histories")
    chapter = relationship("Chapter", back_populates="reading_histories")


class StoryView(Base):
    """
    Log setiap kali sebuah cerita dilihat, untuk kebutuhan analytics
    (cerita trending, jam ramai, dsb). user_id boleh null kalau
    yang melihat belum login.
    """
    __tablename__ = "story_views"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    viewed_at = Column(TIMESTAMP, server_default=func.now())

    # --- Relationships ---
    story = relationship("Story", back_populates="story_views")
    user = relationship("User", back_populates="story_views")