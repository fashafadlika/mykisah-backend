from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.story import Story, Chapter, StoryView

router = APIRouter(
    prefix="/stories",
    tags=["Stories"]
)

@router.get("/popular")
def get_popular_stories(limit: int = 10, db: Session = Depends(get_db)):
    # Query: Ambil story, hitung jumlah view, gabungkan, urutkan dari terbanyak
    popular_query = db.query(
        Story, 
        func.count(StoryView.id).label('total_views')
    ).outerjoin(StoryView, Story.id == StoryView.story_id)\
     .filter(Story.status == 'published')\
     .group_by(Story.id)\
     .order_by(desc('total_views'))\
     .limit(limit).all()

    # Susun data menjadi dictionary agar mudah diubah menjadi JSON
    result = []
    for story, total_views in popular_query:
        result.append({
            "id": story.id,
            "title": story.title,
            "cover_url": story.cover_url,
            "synopsis": story.synopsis,
            "views": total_views
        })
        
    return {
        "success": True,
        "message": "Berhasil mengambil novel terpopuler",
        "data": result
    }

@router.get("/latest")
def get_latest_stories(limit: int = 10, db: Session = Depends(get_db)):
    # Query: Ambil story berdasarkan chapter yang paling baru dibuat
    latest_query = db.query(Story)\
        .join(Chapter, Story.id == Chapter.story_id)\
        .filter(Story.status == 'published')\
        .order_by(desc(Chapter.created_at))\
        .distinct(Story.id)\
        .limit(limit).all()

    result = []
    for story in latest_query:
        result.append({
            "id": story.id,
            "title": story.title,
            "cover_url": story.cover_url,
            "synopsis": story.synopsis,
            "views": 0 
        })
        
    return {
        "success": True,
        "message": "Berhasil mengambil update novel terbaru",
        "data": result
    }