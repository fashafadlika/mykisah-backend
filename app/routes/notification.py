from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)


@router.get("/me", status_code=status.HTTP_200_OK)
def get_my_notifications(
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Mulai query notifikasi milik user saat ini
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    # 2. Filter berdasarkan type jika disertakan
    if type:
        query = query.filter(Notification.type == type)

    # 3. Urutkan berdasarkan waktu dibuat terbaru
    notifications = query.order_by(Notification.created_at.desc()).all()

    # 4. Format hasil untuk response
    result = []
    for notif in notifications:
        result.append({
            "id": notif.id,
            "type": notif.type,
            "message": notif.message,
            "is_read": notif.is_read,
            "story_id": notif.story_id,
            "created_at": notif.created_at.isoformat() if notif.created_at else None,
        })

    return {
        "success": True,
        "message": "Berhasil mengambil notifikasi milik saya.",
        "data": result
    }


@router.get("/admin/submissions", status_code=status.HTTP_200_OK)
def get_admin_submission_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Pastikan yang mengakses adalah admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang bisa mengakses ini!"
        )

    # 2. Query notifikasi submission & report baru untuk admin ini
    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.type.in_(["new_submission", "new_report"])
        )
        .order_by(Notification.created_at.desc())
        .all()
    )

    # 3. Format hasil untuk response
    result = []
    for notif in notifications:
        result.append({
            "id": notif.id,
            "type": notif.type,
            "message": notif.message,
            "is_read": notif.is_read,
            "story_id": notif.story_id,
            "created_at": notif.created_at.isoformat() if notif.created_at else None,
        })

    return {
        "success": True,
        "message": "Berhasil mengambil notifikasi submission admin.",
        "data": result
    }


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
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a notification as read
    """
    db_notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db_notification.is_read = True
    db.commit()
    db.refresh(db_notification)
    return db_notification
