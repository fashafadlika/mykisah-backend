from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportBase(BaseModel):
    novel_id: int
    user_id: Optional[int] = None
    reason_category: str
    detail: Optional[str] = None

class ReportCreate(ReportBase):
    pass

class ReportOut(ReportBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
