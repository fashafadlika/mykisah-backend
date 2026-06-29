from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.review import ReviewAction

class ReviewCreate(BaseModel):
    action: ReviewAction
    note: Optional[str] = None

class UserMinimalResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class StoryPendingResponse(BaseModel):
    id: int
    title: str
    synopsis: Optional[str] = None
    cover_url: Optional[str] = None
    status: str
    submitted_at: Optional[datetime] = None
    author: Optional[UserMinimalResponse] = None

    class Config:
        from_attributes = True

class StoryReviewResponse(BaseModel):
    id: int
    story_id: int
    admin_id: int
    action: str
    note: Optional[str] = None
    reviewed_at: datetime

    class Config:
        from_attributes = True
