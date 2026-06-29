from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.story import Story, StoryStatus
from models.genre import Genre
from schemas.story import StoryResponse

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/stories", response_model=List[StoryResponse])
def search_stories(
    query: Optional[str] = None,
    genre_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    db_query = db.query(Story).filter(Story.status == StoryStatus.published)
    
    if query:
        db_query = db_query.filter(Story.title.ilike(f"%{query}%"))
        
    if genre_name:
        db_query = db_query.join(Story.genres).filter(Genre.name == genre_name)
        
    return db_query.all()
