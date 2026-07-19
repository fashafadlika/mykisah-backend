from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.chapter import Chapter
from models.story import Story
from schemas.chapter import ChapterResponse

router = APIRouter(prefix="/stories", tags=["chapters"])

@router.get("/{story_id}/chapters", response_model=List[ChapterResponse])
def get_chapters_by_story(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
        
    chapters = db.query(Chapter).filter(Chapter.story_id == story_id).order_by(Chapter.chapter_number).all()
    return chapters

@router.get("/chapters/{chapter_id}", response_model=ChapterResponse)
def get_chapter_by_id(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter
