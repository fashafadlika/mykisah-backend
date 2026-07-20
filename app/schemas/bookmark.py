from pydantic import BaseModel
from datetime import datetime

class StoryNestedResponse(BaseModel):
    id: int
    title: str
    synopsis: str | None = None  # Menggunakan str atau None jika teks sinopsis kosong
    cover_url: str | None = None # Menggunakan str atau None jika belum ada cover
    status: str                  # Menampung nilai dari enum status ('draft', 'published', dll)

    class Config:
        from_attributes = True

class BookmarkBase(BaseModel):
    user_id: int
    story_id: int

class BookmarkCreate(BookmarkBase):
    pass

class BookmarkResponse(BookmarkBase):
    id: int
    created_at: datetime
    story: StoryNestedResponse

    class Config:
        from_attributes = True  

class BookmarkCreateResponse(BookmarkBase):
    id: int
    created_at: datetime
    story: StoryNestedResponse

    class Config:
        from_attributes = True
