from sqlalchemy import Column, Integer, ForeignKey
from database import Base

class StoryGenre(Base):
    __tablename__ = "story_genres"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id", ondelete="CASCADE"), nullable=False)
