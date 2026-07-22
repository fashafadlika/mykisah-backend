from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db 
from app.models.bookmark import Bookmark 
from app.schemas.bookmark import BookmarkCreate, BookmarkResponse, BookmarkCreateResponse
from app.models.user import User
from app.models.story import Story

router = APIRouter(
    prefix="/bookmarks",
    tags=["Bookmarks"]
)

@router.post("/", response_model=BookmarkCreateResponse, status_code=status.HTTP_201_CREATED)
def add_bookmark(bookmark: BookmarkCreate, db: Session = Depends(get_db)):
    # 1. Cek apakah User ada
    user_exists = db.query(User).filter(User.id == bookmark.user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")

    # 2. Cek apakah Story ada
    story_exists = db.query(Story).filter(Story.id == bookmark.story_id).first()
    if not story_exists:
        raise HTTPException(status_code=404, detail="Novel tidak ditemukan.")

    # 3. Validasi duplikasi (kode lama Anda)
    existing_bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == bookmark.user_id,
        Bookmark.story_id == bookmark.story_id
    ).first()
    
    if existing_bookmark:
        raise HTTPException(status_code=400, detail="Story ini sudah ada di dalam bookmark Anda.")
    
    # 4. Buat bookmark baru
    db_bookmark = Bookmark(**bookmark.model_dump())
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)

    # Memuat relasi story agar sesuai dengan schema respon
    db_bookmark = db.query(Bookmark).options(joinedload(Bookmark.story)).filter(Bookmark.id == db_bookmark.id).first()
    return db_bookmark


@router.delete("/{bookmark_id}", status_code=status.HTTP_200_OK)
def remove_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    """
    Endpoint untuk menghapus bookmark berdasarkan ID Bookmark.
    """
    db_bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not db_bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark tidak ditemukan."
        )
    
    db.delete(db_bookmark)
    db.commit()
    return {"status": "success", "message": "Bookmark berhasil dihapus."}


@router.get("/user/{user_id}", response_model=List[BookmarkResponse])
def get_user_bookmarks(user_id: int, db: Session = Depends(get_db)):
    """
    Endpoint untuk mengambil seluruh daftar bookmark milik user tertentu.
    """
    bookmarks = (
        db.query(Bookmark)
        .options(joinedload(Bookmark.story))
        .filter(Bookmark.user_id == user_id)
        .all()
    )
    return bookmarks
