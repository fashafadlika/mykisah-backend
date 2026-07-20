from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportOut


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


from app.models.user import User
from app.models.notification import Notification
from app.models.story import Story

@router.post("/", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def create_report(report_in: ReportCreate, db: Session = Depends(get_db)):
    # Simpan laporan baru dari user
    new_report = Report(**report_in.dict())
    db.add(new_report)
    
    # Ambil judul novel agar pesan notifikasi lebih informatif
    story = db.query(Story).filter(Story.id == new_report.novel_id).first()
    story_title = f'"{story.title}"' if story else f"ID {new_report.novel_id}"
    
    # Buat notifikasi untuk semua admin
    admins = db.query(User).filter(User.role == "admin").all()
    for admin in admins:
        notif = Notification(
            user_id=admin.id,
            story_id=new_report.novel_id,
            type="new_report",
            message=f"Ada laporan baru untuk Novel {story_title} dengan kategori '{new_report.reason_category}'."
        )
        db.add(notif)
        
    db.commit()
    db.refresh(new_report)
    return new_report


@router.get("/", response_model=list[ReportOut])
def get_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Ambil semua laporan dengan pagination sederhana
    return db.query(Report).offset(skip).limit(limit).all()


from app.dependencies import get_current_user

@router.post("/{report_id}/reject", status_code=status.HTTP_200_OK)
def reject_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Pastikan yang mengakses adalah admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang bisa mengakses ini!"
        )

    # 2. Cari report berdasarkan id
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laporan tidak ditemukan!"
        )

    # 3. Hapus report
    db.delete(report)
    db.commit()

    return {
        "success": True,
        "message": "Laporan berhasil ditolak/dihapus."
    }
