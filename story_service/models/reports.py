from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class ReportStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Report(Base):
    """
    Laporan dari pembaca terhadap sebuah cerita (konten tidak pantas,
    plagiarisme, spam, dll). Ditinjau oleh admin lewat flow:
    List Report -> Review Report -> Acc Report (approve/reject).
    """
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    reason = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.pending)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # --- Relationships ---
    reporter = relationship("User", back_populates="reports")
    story = relationship("Story", back_populates="reports")