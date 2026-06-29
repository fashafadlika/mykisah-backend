from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.genre import Genre
from schemas.genre import GenreResponse, GenreCreate

router = APIRouter(
    prefix="/genres",
    tags=["genres"]
)

@router.get("/", response_model=List[GenreResponse])
def get_genres(db: Session = Depends(get_db)):
    genres = db.query(Genre).all()
    return genres

@router.post("/", response_model=GenreResponse)
def create_genre(genre: GenreCreate, db: Session = Depends(get_db)):
    db_genre = db.query(Genre).filter(Genre.name == genre.name).first()
    if db_genre:
        raise HTTPException(status_code=400, detail="Genre already exists")
    new_genre = Genre(name=genre.name)
    db.add(new_genre)
    db.commit()
    db.refresh(new_genre)
    return new_genre
