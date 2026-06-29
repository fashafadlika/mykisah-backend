from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from models.report import ReportStatus


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------
class ReportCreate(BaseModel):
    reason: str
    description: Optional[str] = None


class ReportStatusUpdate(BaseModel):
    """Dipakai admin di tahap Review Report -> Acc Report (approve/reject)."""
    status: ReportStatus


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class ReporterBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class StoryBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reporter: ReporterBrief
    story: StoryBrief
    reason: str
    description: Optional[str] = None
    status: ReportStatus
    created_at: datetime