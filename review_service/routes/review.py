from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from database import get_db
from models.story import Story, StoryStatus
from models.review import StoryReview, ReviewAction
from models.user import User
from core.auth import get_current_admin
from schemas.review import ReviewCreate, StoryPendingResponse, StoryReviewResponse

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.get("/pending", response_model=List[StoryPendingResponse])
def get_pending_stories(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Mendapatkan daftar semua cerita yang berstatus 'pending' (menunggu persetujuan).
    Hanya dapat diakses oleh Admin.
    """
    stories = db.query(Story).filter(Story.status == StoryStatus.pending).all()
    return stories

@router.post("/{story_id}", response_model=StoryReviewResponse)
def review_story(
    story_id: int,
    payload: ReviewCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Menolak atau menyetujui cerita.
    Hanya dapat diakses oleh Admin.
    """
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cerita tidak ditemukan"
        )
        
    if story.status != StoryStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cerita tidak dapat direview karena berstatus '{story.status}' (harus 'pending')"
        )
        
    now = datetime.now(timezone.utc)
    
    if payload.action == ReviewAction.approved:
        story.status = StoryStatus.published
        story.published_at = now
        story.reject_message = None
    elif payload.action == ReviewAction.rejected:
        if not payload.note:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Catatan penolakan (note) harus diisi jika cerita ditolak"
            )
        story.status = StoryStatus.rejected
        story.reject_message = payload.note
        
    review = StoryReview(
        story_id=story.id,
        admin_id=current_admin.id,
        action=payload.action,
        note=payload.note,
        reviewed_at=now
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    return review
