from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from models.bookmark import Bookmark

# Akses langsung ke database untuk tabel bookmarks — query CRUD murni tanpa business logic.
class BookmarkRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, bookmark_id: int) -> Optional[Bookmark]:
        result = await db.execute(select(Bookmark).filter(Bookmark.id == bookmark_id))
        return result.scalars().first()

    @staticmethod
    async def check_exists(db: AsyncSession, user_id: int, story_id: int) -> Optional[Bookmark]:
        result = await db.execute(
            select(Bookmark).filter(
                Bookmark.user_id == user_id, 
                Bookmark.story_id == story_id
            )
        )
        return result.scalars().first()

    @staticmethod
    async def add(db: AsyncSession, user_id: int, story_id: int) -> Bookmark:
        db_bookmark = Bookmark(user_id=user_id, story_id=story_id)
        db.add(db_bookmark)
        await db.commit()
        await db.refresh(db_bookmark)
        return db_bookmark

    @staticmethod
    async def remove(db: AsyncSession, bookmark_id: int) -> bool:
        result = await db.execute(delete(Bookmark).filter(Bookmark.id == bookmark_id))
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20) -> Sequence[Bookmark]:
        result = await db.execute(
            select(Bookmark)
            .filter(Bookmark.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
