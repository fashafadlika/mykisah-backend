from sqlalchemy import Column, Integer, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

class ReviewAction(str, enum.Enum):
    approved = "approved"
    rejected = "rejected"

class StoryReview(Base):
    __tablename__ = "story_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(Enum(ReviewAction), nullable=False)
    note = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())

    story = relationship("Story", backref="reviews")
    admin = relationship("User", backref="story_reviews")
