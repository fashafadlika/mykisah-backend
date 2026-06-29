from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import report as models
from schemas import report as schemas

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

@router.post("/", response_model=schemas.ReportOut, status_code=status.HTTP_201_CREATED)
def create_report(report_in: schemas.ReportCreate, db: Session = Depends(get_db)):
    new_report = models.Report(**report_in.dict())
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

@router.get("/", response_model=list[schemas.ReportOut])
def get_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reports = db.query(models.Report).offset(skip).limit(limit).all()
    return reports
