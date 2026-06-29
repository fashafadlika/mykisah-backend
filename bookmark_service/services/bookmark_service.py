from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from repository.bookmark_repo import BookmarkRepository
from models.bookmark import Bookmark
from typing import Sequence

# Business logic bookmark — validasi kepemilikan & duplikat sebelum panggil repository.
class BookmarkService:
    @staticmethod
    async def add_bookmark(db: AsyncSession, user_id: int, story_id: int) -> Bookmark:
        # Business logic: Cek apakah bookmark sudah ada
        existing = await BookmarkRepository.check_exists(db, user_id, story_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Story sudah ditambahkan ke bookmarks sebelumnya."
            )
        
        return await BookmarkRepository.add(db, user_id, story_id)

    @staticmethod
    async def remove_bookmark(db: AsyncSession, bookmark_id: int, user_id: int) -> bool:
        # Business logic: Cek apakah bookmark ada
        bookmark = await BookmarkRepository.get_by_id(db, bookmark_id)
        if not bookmark:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bookmark tidak ditemukan."
            )
        
        # Business logic: Cek kepemilikan bookmark (Authorization)
        if bookmark.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Anda tidak memiliki akses untuk menghapus bookmark ini."
            )
            
        return await BookmarkRepository.remove(db, bookmark_id)

    @staticmethod
    async def get_user_bookmarks(
        db: AsyncSession, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 20
    ) -> Sequence[Bookmark]:
        return await BookmarkRepository.get_by_user(db, user_id, skip, limit)
