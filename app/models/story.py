from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    synopsis = Column(Text)
    cover_url = Column(String(255))
    status = Column(Enum('draft', 'pending', 'published', 'rejected', name="story_status_enum"), default='draft')

    # kolom tambahan yang tadinya belum ada, dipakai di alur submission & review admin
    reject_message = Column(Text, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    chapters = relationship("Chapter", back_populates="story")
    views = relationship("StoryView", back_populates="story")
    bookmarks = relationship("Bookmark", back_populates="story", cascade="all, delete-orphan")
      # kolom tambahan yang tadinya belum ada, dipakai di alur submission & review admin
    genres = relationship("StoryGenre", back_populates="story", cascade="all, delete-orphan")
    reviews = relationship("StoryReview", back_populates="story", cascade="all, delete-orphan")


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"))
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    chapter_number = Column(Integer, nullable=False)
    cover_url = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    story = relationship("Story", back_populates="chapters")
    chapter_views = relationship("ChapterView", back_populates="chapter", cascade="all, delete-orphan")


class ChapterView(Base):
    """Menyimpan siapa saja yang sudah pernah membaca chapter ini (unik per user-chapter)."""
    __tablename__ = "chapter_views"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    viewed_at = Column(DateTime, default=datetime.now(timezone.utc))

    chapter = relationship("Chapter", back_populates="chapter_views")

    __table_args__ = (
        UniqueConstraint("chapter_id", "user_id", name="uq_chapter_user_view"),
    )



class StoryView(Base):
    __tablename__ = "story_views"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    viewed_at = Column(DateTime, default=datetime.now(timezone.utc))

    story = relationship("Story", back_populates="views")


# Tabel pivot: relasi many-to-many antara story dan genre (genre_id merujuk ke GENRES hardcoded)
class StoryGenre(Base):
    __tablename__ = "story_genres"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"))
    genre_id = Column(Integer, nullable=False)  # bukan FK karena genre bukan tabel, cuma hardcoded list

    story = relationship("Story", back_populates="genres")


# Histori review admin: siapa yang approve/reject, kapan, dan catatannya
class StoryReview(Base):
    __tablename__ = "story_reviews"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"))
    admin_id = Column(Integer, ForeignKey("users.id"))
    action = Column(Enum('approved', 'rejected', name="review_action_enum"), nullable=False)
    note = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.now(timezone.utc))

    story = relationship("Story", back_populates="reviews")