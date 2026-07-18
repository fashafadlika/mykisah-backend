from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import TypeVar, Generic, Optional, Any

T = TypeVar("T")

# Schema respons generik untuk Bookmark
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


# Schema input saat membuat bookmark — hanya butuh story_id (user_id ditambah di BookmarkCreate).
class BookmarkBase(BaseModel):
    story_id: int

# Payload lengkap untuk membuat bookmark baru.
class BookmarkCreate(BookmarkBase):
    user_id: int

# Schema output bookmark yang dikembalikan ke client.
class BookmarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    story_id: int
    created_at: datetime
