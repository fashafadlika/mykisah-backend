from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models.story import StoryStatus
from schemas.genre import GenreResponse

class StoryBase(BaseModel):
    title: str
    synopsis: Optional[str] = None
    cover_url: Optional[str] = None

class StoryCreate(StoryBase):
    user_id: int
    genre_ids: Optional[List[int]] = []

class StoryUpdate(BaseModel):
    title: Optional[str] = None
    synopsis: Optional[str] = None
    cover_url: Optional[str] = None
    genre_ids: Optional[List[int]] = None

class StoryResponse(StoryBase):
    id: int
    user_id: int
    status: StoryStatus
    reject_message: Optional[str] = None
    
    submitted_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    genres: List[GenreResponse] = []

    class Config:
        from_attributes = True