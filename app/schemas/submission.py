from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from app.routes.genres import GENRES

# Mapping id -> nama genre, dipakai buat cek genre_ids yang dikirim user valid atau enggak
VALID_GENRE_IDS = {genre["id"] for genre in GENRES}


class SubmissionCreate(BaseModel):
    """Schema buat validasi data submit novel baru dari user."""

    title: str = Field(..., min_length=3, max_length=255)
    synopsis: str = Field(..., min_length=20, max_length=2000)
    cover_url: str
    genre_ids: List[int] = Field(..., min_length=1, max_length=5)
    status: str = "pending"
    chapter_title: Optional[str] = None
    chapter_content: Optional[str] = None

    # Pastikan semua genre_id yang dikirim user beneran ada di list genre yang valid
    @field_validator("genre_ids")
    @classmethod
    def validate_genre_ids(cls, genre_ids: List[int]) -> List[int]:
        invalid_ids = [gid for gid in genre_ids if gid not in VALID_GENRE_IDS]

        if invalid_ids:
            raise ValueError(f"Genre id tidak valid: {invalid_ids}")

        return genre_ids


class SubmissionResubmit(BaseModel):
    """Schema buat validasi data submit ulang novel dari user."""

    title: Optional[str] = Field(None, min_length=3, max_length=255)
    synopsis: Optional[str] = Field(None, min_length=20, max_length=2000)
    cover_url: Optional[str] = None
    genre_ids: Optional[List[int]] = None

    @field_validator("genre_ids")
    @classmethod
    def validate_genre_ids(cls, v):
        if v is None:
            return v
        invalid = [gid for gid in v if gid not in VALID_GENRE_IDS]
        if invalid:
            raise ValueError(f"Genre id tidak valid: {invalid}")
        return v


class SubmissionUpdate(BaseModel):
    title: Optional[str] = None
    synopsis: Optional[str] = None
    cover_url: Optional[str] = None
    genre_ids: Optional[List[int]] = None
    chapter_title: Optional[str] = None
    chapter_content: Optional[str] = None
