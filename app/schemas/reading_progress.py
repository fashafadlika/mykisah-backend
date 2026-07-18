# schemas/reading_progress.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import TypeVar, Generic, Optional, Any

T = TypeVar("T")

# Schema respons generik untuk Reading Progress
class BaseResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    errors: Optional[Any] = None

# Respons sukses
class SuccessResponse(BaseResponse[T]):
    success: bool = True
    errors: Optional[Any] = None

# Respons error
class ErrorResponse(BaseResponse[None]):
    success: bool = False
    data: Optional[None] = None


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
