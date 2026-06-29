from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Likes
# ---------------------------------------------------------------------------
class LikeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    story_id: int
    created_at: datetime


class LikeCountResponse(BaseModel):
    story_id: int
    likes_count: int
    is_liked_by_me: bool = False  # status like dari current_user, diisi manual di route


# ---------------------------------------------------------------------------
# Bookmarks
# ---------------------------------------------------------------------------
class BookmarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    story_id: int
    created_at: datetime


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------
class CommentCreate(BaseModel):
    content: str


class CommentUpdate(BaseModel):
    content: str


class CommenterBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    avatar_url: Optional[str] = None


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    story_id: int
    content: str
    user: CommenterBrief
    created_at: datetime
    updated_at: datetime