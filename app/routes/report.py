from fastapi import APIRouter, Depends, status
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
