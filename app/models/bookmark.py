from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base  

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) # users.id sesuai nama tabel User Anda
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False) # stories.id sesuai nama tabel Story Anda
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Hubungan antar tabel (Gunakan string untuk menghindari circular import)
    user = relationship("User", back_populates="bookmarks")
    story = relationship("Story", back_populates="bookmarks")