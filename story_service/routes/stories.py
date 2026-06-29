from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.story import Story, StoryStatus
from models.genre import Genre
from models.story_genre import StoryGenre
from schemas.story import StoryResponse, StoryCreate, StoryUpdate

router = APIRouter(
    prefix="/stories",
    tags=["stories"]
)

@router.post("/", response_model=StoryResponse)
def create_story(story_in: StoryCreate, db: Session = Depends(get_db)):
    # Verify genres exist
    genres = []
    if story_in.genre_ids:
        genres = db.query(Genre).filter(Genre.id.in_(story_in.genre_ids)).all()
        if len(genres) != len(story_in.genre_ids):
            raise HTTPException(status_code=400, detail="One or more genres not found")

    new_story = Story(
        user_id=story_in.user_id,
        title=story_in.title,
        synopsis=story_in.synopsis,
        cover_url=story_in.cover_url,
        status=StoryStatus.draft
    )
    
    new_story.genres = genres
    
    db.add(new_story)
    db.commit()
    db.refresh(new_story)
    return new_story

@router.get("/", response_model=List[StoryResponse])
def explore_stories(
    search: Optional[str] = None,
    genre_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Story).filter(Story.status == StoryStatus.published)
    
    if search:
        query = query.filter(Story.title.ilike(f"%{search}%"))
        
    if genre_id:
        query = query.join(StoryGenre).filter(StoryGenre.genre_id == genre_id)
        
    stories = query.all()
    return stories

@router.get("/me", response_model=List[StoryResponse])
def get_my_stories(
    user_id: int, # Temporary dependency until Auth service is integrated
    status: Optional[StoryStatus] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Story).filter(Story.user_id == user_id)
    if status:
        query = query.filter(Story.status == status)
        
    return query.all()

@router.get("/{story_id}", response_model=StoryResponse)
def get_story(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.put("/{story_id}", response_model=StoryResponse)
def update_story(story_id: int, story_in: StoryUpdate, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
        
    update_data = story_in.dict(exclude_unset=True)
    
    if 'genre_ids' in update_data:
        genre_ids = update_data.pop('genre_ids')
        genres = db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
        if len(genres) != len(genre_ids):
            raise HTTPException(status_code=400, detail="One or more genres not found")
        story.genres = genres
        
    for field, value in update_data.items():
        setattr(story, field, value)
        
    db.commit()
    db.refresh(story)
    return story

@router.delete("/{story_id}")
def delete_story(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
        
    if story.status != StoryStatus.draft:
        raise HTTPException(status_code=400, detail="Only draft stories can be deleted")
        
    db.delete(story)
    db.commit()
    return {"message": "Story deleted successfully"}

@router.post("/{story_id}/submit", response_model=StoryResponse)
def submit_story(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
        
    if story.status != StoryStatus.draft:
        raise HTTPException(status_code=400, detail="Only draft stories can be submitted")
        
    story.status = StoryStatus.pending
    story.submitted_at = datetime.utcnow()
    
    db.commit()
    db.refresh(story)
    return story
