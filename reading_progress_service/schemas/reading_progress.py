# schemas/reading_progress.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReadingProgressCreate(BaseModel):
    """Payload untuk membuat atau mengupdate reading progress."""
    user_id: int
    story_id: int
    chapter_id: int


class ReadingProgressResponse(BaseModel):
    """Schema output yang dikembalikan ke client."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    story_id: int
    chapter_id: int
    last_read_at: datetime
