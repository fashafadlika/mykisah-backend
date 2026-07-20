from sqlalchemy import Column, Integer, DateTime, func
from database import Base

# Model ORM untuk tabel `bookmarks` — menyimpan relasi user_id & story_id yang di-bookmark.
class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)
    story_id = Column(Integer, index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
