from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class GenreBase(BaseModel):
    name: str

class GenreCreate(GenreBase):
    pass

class GenreResponse(GenreBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True