from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.notification import Notification
from schemas.notification import NotificationCreate, NotificationResponse

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)

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
