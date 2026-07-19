from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChapterBase(BaseModel):
    title: str
    content: str
    chapter_number: int

class ChapterCreate(ChapterBase):
    story_id: int

class ChapterResponse(ChapterBase):
    id: int
    story_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
