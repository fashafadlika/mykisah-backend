from pydantic import BaseModel, field_validator
from typing import List, Optional, Literal
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


# ─── Submission schemas (used by /submissions/ router) ───────────────────────

class SubmissionCreate(BaseModel):
    """Payload sent by Flutter when user presses Draft or Publish."""
    title: str
    synopsis: Optional[str] = None
    cover_url: Optional[str] = ""
    genre_ids: List[int]
    status: Literal["draft", "pending"] = "pending"
    # First chapter (required when status == "pending", optional for draft)
    chapter_title: Optional[str] = None
    chapter_content: Optional[str] = None

    @field_validator("genre_ids")
    @classmethod
    def at_least_one_genre(cls, v: List[int]) -> List[int]:
        if not v:
            raise ValueError("Minimal 1 genre harus dipilih")
        return v


class SubmissionUpdate(BaseModel):
    """Payload for editing a draft or rejected story."""
    title: Optional[str] = None
    synopsis: Optional[str] = None
    cover_url: Optional[str] = None
    genre_ids: Optional[List[int]] = None
    chapter_title: Optional[str] = None
    chapter_content: Optional[str] = None


class SubmissionResponse(StoryResponse):
    """Extends StoryResponse with author info for the frontend."""
    author_username: Optional[str] = None
    # chapter info of the first chapter if present
    chapter_title: Optional[str] = None
    chapter_content: Optional[str] = None