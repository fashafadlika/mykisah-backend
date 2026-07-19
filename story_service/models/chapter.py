from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    chapter_number = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    story = relationship("Story", back_populates="chapters")
