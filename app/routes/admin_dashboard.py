from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.database import get_db
from app.models.story import Story, Chapter
from app.models.user import User
from app.models.reading_progres import ReadingProgress
from app.models.report import Report
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/admin/dashboard",
    tags=["Admin Dashboard"]
)


# Pastikan yang manggil endpoint ini memang admin, bukan user biasa
def _require_admin(current_user: User) -> None:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang bisa mengakses ini!"
        )


@router.get("/stats", status_code=status.HTTP_200_OK)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Pastikan yang akses adalah admin
    _require_admin(current_user)

    # 2. Hitung semua statistik, query satu per satu agar mudah dibaca dan di-debug
    total_novels          = db.query(func.count(Story.id)).scalar()
    total_users           = db.query(func.count(User.id)).filter(User.role == "user").scalar()
    total_published       = db.query(func.count(Story.id)).filter(Story.status == "published").scalar()
    total_readers         = db.query(func.count(distinct(ReadingProgress.user_id))).scalar()
    total_chapters        = db.query(func.count(Chapter.id)).scalar()
    total_archived        = db.query(func.count(Story.id)).filter(Story.status == "rejected").scalar()
    total_pending         = db.query(func.count(Story.id)).filter(Story.status == "pending").scalar()
    total_reports_pending = db.query(func.count(Report.id)).scalar()

    return {
        "success": True,
        "message": "Statistik dashboard berhasil diambil.",
        "data": {
            "total_novels":          total_novels,
            "total_users":           total_users,
            "total_novel_published": total_published,
            "total_readers":         total_readers,
            "total_chapters":        total_chapters,
            "total_archived_novels": total_archived,
            "total_story_pending":   total_pending,
            "total_reports_pending": total_reports_pending,
        }
    }
