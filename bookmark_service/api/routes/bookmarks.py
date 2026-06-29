from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api.dependencies import get_db
from schemas.bookmark import BookmarkCreate, BookmarkResponse
from schemas.base import SuccessResponse
from services.bookmark_service import BookmarkService

router = APIRouter(
    prefix="/bookmarks",
    tags=["bookmarks"]
)

@router.post("/", response_model=SuccessResponse[BookmarkResponse], status_code=status.HTTP_201_CREATED)
async def add_bookmark(
    bookmark_in: BookmarkCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Menambahkan bookmark baru untuk seorang user.
    """
    bookmark = await BookmarkService.add_bookmark(
        db=db,
        user_id=bookmark_in.user_id,
        story_id=bookmark_in.story_id
    )
    
    # Bungkus dalam SuccessResponse
    return SuccessResponse(
        message="Bookmark berhasil ditambahkan.",
        data=BookmarkResponse.model_validate(bookmark)
    )

@router.get("/user/{user_id}", response_model=SuccessResponse[List[BookmarkResponse]])
async def get_user_bookmarks(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Mengambil daftar bookmark milik user (biasanya untuk Profile Page GridCard).
    """
    bookmarks = await BookmarkService.get_user_bookmarks(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    
    # Validasi item list menggunakan BookmarkResponse
    data_response = [BookmarkResponse.model_validate(b) for b in bookmarks]
    
    return SuccessResponse(
        message="Daftar bookmark berhasil diambil.",
        data=data_response
    )

@router.delete("/{bookmark_id}", response_model=SuccessResponse[None])
async def remove_bookmark(
    bookmark_id: int,
    user_id: int = Query(..., description="ID user yang menghapus bookmark (untuk validasi kepemilikan)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Menghapus bookmark berdasarkan ID bookmark dan validasi kepemilikan user.
    """
    await BookmarkService.remove_bookmark(
        db=db,
        bookmark_id=bookmark_id,
        user_id=user_id
    )
    
    return SuccessResponse(
        message="Bookmark berhasil dihapus.",
        data=None
    )
