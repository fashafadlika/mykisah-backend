# routes/reading_progress.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.reading_progress import ReadingProgressCreate, ReadingProgressResponse
from schemas.base import SuccessResponse
from services import reading_progress_service as svc

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
    progress, is_new = svc.upsert_progress(db, data)
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
    progress_list = svc.get_user_progress(db, user_id, skip, limit)
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
    progress = svc.get_progress_by_id(db, progress_id)
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

    svc.delete_progress(db, progress)

    return SuccessResponse(
        message="Reading progress berhasil dihapus.",
        data=None
    )
