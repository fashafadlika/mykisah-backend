from datetime import datetime
from pydantic import BaseModel, ConfigDict

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
