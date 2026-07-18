from pydantic import BaseModel
from datetime import datetime

class BookmarkBase(BaseModel):
    user_id: int
    story_id: int

class BookmarkCreate(BookmarkBase):
    pass

class BookmarkResponse(BookmarkBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  
