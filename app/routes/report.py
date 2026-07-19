from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportOut


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.post("/", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def create_report(report_in: ReportCreate, db: Session = Depends(get_db)):
    # Simpan laporan baru dari user
    new_report = Report(**report_in.dict())
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report


@router.get("/", response_model=list[ReportOut])
def get_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Ambil semua laporan dengan pagination sederhana
    return db.query(Report).offset(skip).limit(limit).all()
