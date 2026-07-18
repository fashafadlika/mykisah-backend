# routes/reading_progress.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.reading_progres import ReadingProgress
from app.schemas.reading_progress import ReadingProgressCreate, ReadingProgressResponse, SuccessResponse

router = APIRouter(
    prefix="/reading-progress",
    tags=["reading-progress"]
)


@router.post("/")
def upsert_reading_progress(data: ReadingProgressCreate, db: Session = Depends(get_db)):
    """
    Simpan atau update chapter terakhir yang dibaca user.
    Insert jika belum ada; update jika sudah ada (upsert per user+story).
    HTTP 201 jika record baru, HTTP 200 jika update.
    """
    existing = db.query(ReadingProgress).filter(
        ReadingProgress.user_id == data.user_id,
        ReadingProgress.story_id == data.story_id
    ).first()

    if existing:
        existing.chapter_id = data.chapter_id
        # last_read_at diperbarui otomatis oleh onupdate=func.now()
        db.commit()
        db.refresh(existing)
        progress = existing
        is_new = False
    else:
        progress = ReadingProgress(
            user_id=data.user_id,
            story_id=data.story_id,
            chapter_id=data.chapter_id
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
        is_new = True

    http_status = status.HTTP_201_CREATED if is_new else status.HTTP_200_OK

    return JSONResponse(
        status_code=http_status,
        content=SuccessResponse(
            message="Reading progress berhasil disimpan.",
            data=ReadingProgressResponse.model_validate(progress).model_dump(mode="json")
        ).model_dump()
    )


@router.get("/user/{user_id}", response_model=SuccessResponse[List[ReadingProgressResponse]])
def get_reading_progress(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Ambil daftar cerita yang pernah dibaca user (untuk Profile Page).
    Diurutkan berdasarkan last_read_at terbaru (terbaru di atas).
    """
    progress_list = (
        db.query(ReadingProgress)
        .filter(ReadingProgress.user_id == user_id)
        .order_by(ReadingProgress.last_read_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    data = [ReadingProgressResponse.model_validate(p) for p in progress_list]

    return SuccessResponse(
        message="Daftar reading progress berhasil diambil.",
        data=data
    )


@router.delete("/{progress_id}", response_model=SuccessResponse[None])
def delete_reading_progress(
    progress_id: int,
    user_id: int = Query(..., description="ID user yang meminta penghapusan (untuk validasi kepemilikan)"),
    db: Session = Depends(get_db)
):
    """
    Hapus satu reading progress. Hanya pemilik yang boleh menghapus.
    """
    progress = db.query(ReadingProgress).filter(ReadingProgress.id == progress_id).first()
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading progress tidak ditemukan."
        )

    if progress.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki akses untuk menghapus data ini."
        )

    db.delete(progress)
    db.commit()

    return SuccessResponse(
        message="Reading progress berhasil dihapus.",
        data=None
    )
