from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    userId: int = Field(alias="user_id")
    storyId: Optional[int] = Field(None, alias="story_id")
    chapterId: Optional[int] = Field(None, alias="chapter_id")
    type: str
    message: str
    isRead: bool = Field(False, alias="is_read")

    class Config:
        populate_by_name = True

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    createdAt: datetime = Field(alias="created_at")

    class Config:
        from_attributes = True
        populate_by_name = True
