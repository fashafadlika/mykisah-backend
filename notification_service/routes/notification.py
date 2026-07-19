from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models.notification import Notification
from schemas.notification import NotificationCreate, NotificationResponse

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)


class BulkNotificationItem(BaseModel):
    user_id: int
    story_id: Optional[int] = None
    chapter_id: Optional[int] = None
    type: str
    message: str
    is_read: bool = False


class BulkNotificationCreate(BaseModel):
    notifications: List[BulkNotificationItem]


@router.get("/{user_id}", response_model=List[NotificationResponse])
def get_notifications(user_id: int, db: Session = Depends(get_db)):
    """
    Get all notifications for a specific user
    """
    notifications = db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()
    return notifications

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    """
    Create a new notification. This should be called by other microservices.
    """
    db_notification = Notification(
        user_id=notification.userId,
        story_id=notification.storyId,
        chapter_id=notification.chapterId,
        type=notification.type,
        message=notification.message,
        is_read=notification.isRead
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def create_bulk_notifications(payload: BulkNotificationCreate, db: Session = Depends(get_db)):
    """
    Create multiple notifications at once.
    Called internally by story_service when a user submits a story for review.
    """
    created = []
    for item in payload.notifications:
        db_notification = Notification(
            user_id=item.user_id,
            story_id=item.story_id,
            chapter_id=item.chapter_id,
            type=item.type,
            message=item.message,
            is_read=item.is_read,
        )
        db.add(db_notification)
        created.append(db_notification)
    db.commit()
    return {"created": len(created)}

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    """
    Mark a notification as read
    """
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db_notification.is_read = True
    db.commit()
    db.refresh(db_notification)
    return db_notification
