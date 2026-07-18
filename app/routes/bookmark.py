# Routes untuk endpoint bookmark — query DB, validasi bisnis, dan response langsung di sini.
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.bookmark import Bookmark
from app.schemas.bookmark import BookmarkCreate, BookmarkResponse, SuccessResponse

router = APIRouter(
    prefix="/bookmarks",
    tags=["bookmarks"]
)

@router.post("/", response_model=SuccessResponse[BookmarkResponse], status_code=status.HTTP_201_CREATED)
def add_bookmark(bookmark_in: BookmarkCreate, db: Session = Depends(get_db)):
    """
    Menambahkan bookmark baru untuk seorang user.
    """
    # Business logic: Cek apakah bookmark sudah ada
    existing = db.query(Bookmark).filter(
        Bookmark.user_id == bookmark_in.user_id,
        Bookmark.story_id == bookmark_in.story_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Story sudah ditambahkan ke bookmarks sebelumnya."
        )

    db_bookmark = Bookmark(user_id=bookmark_in.user_id, story_id=bookmark_in.story_id)
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)

    return SuccessResponse(
        message="Bookmark berhasil ditambahkan.",
        data=BookmarkResponse.model_validate(db_bookmark)
    )

@router.get("/user/{user_id}", response_model=SuccessResponse[List[BookmarkResponse]])
def get_user_bookmarks(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Mengambil daftar bookmark milik user (biasanya untuk Profile Page GridCard).
    """
    bookmarks = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    data_response = [BookmarkResponse.model_validate(b) for b in bookmarks]

    return SuccessResponse(
        message="Daftar bookmark berhasil diambil.",
        data=data_response
    )

@router.delete("/{bookmark_id}", response_model=SuccessResponse[None])
def remove_bookmark(
    bookmark_id: int,
    user_id: int = Query(..., description="ID user yang menghapus bookmark (untuk validasi kepemilikan)"),
    db: Session = Depends(get_db)
):
    """
    Menghapus bookmark berdasarkan ID bookmark dan validasi kepemilikan user.
    """
    # Business logic: Cek apakah bookmark ada
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
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

    db.delete(bookmark)
    db.commit()

    return SuccessResponse(
        message="Bookmark berhasil dihapus.",
        data=None
    )
