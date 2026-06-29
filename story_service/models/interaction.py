from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Like(Base):
    """Satu pengguna hanya bisa like satu cerita satu kali (unique constraint di DB)."""
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # --- Relationships ---
    user = relationship("User", back_populates="likes")
    story = relationship("Story", back_populates="likes")


class Bookmark(Base):
    """Satu pengguna hanya bisa bookmark satu cerita satu kali (unique constraint di DB)."""
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # --- Relationships ---
    user = relationship("User", back_populates="bookmarks")
    story = relationship("Story", back_populates="bookmarks")


class Comment(Base):
    """Komentar pembaca terhadap sebuah cerita (per proposal: komentar di level cerita)."""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    story = relationship("Story", back_populates="comments")
    user = relationship("User", back_populates="comments")