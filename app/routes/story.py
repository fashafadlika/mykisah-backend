from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app.models.story import Story, Chapter, StoryView
from app.models.user import User
from app.models.bookmark import Bookmark

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

@router.get("/{story_id}")
def get_story_detail(story_id: int, db: Session = Depends(get_db)):
    # 1. Ambil data story utama
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Novel tidak ditemukan")

    # 2. Ambil nama penulis dari relasi User
    author = db.query(User).filter(User.id == story.user_id).first()
    author_username = author.username if author else "Unknown Author"

    # 3. Hitung statistik total views dan total bookmarks (stars)
    views_count = db.query(func.count(StoryView.id)).filter(StoryView.story_id == story_id).scalar()
    stars_count = db.query(func.count(Bookmark.id)).filter(Bookmark.story_id == story_id).scalar()
    
    # 4. Ambil semua list chapter yang dimiliki oleh novel ini
    chapters = db.query(Chapter).filter(Chapter.story_id == story_id).order_by(Chapter.chapter_number.asc()).all()
    total_chapters = len(chapters)

    # 5. Kembalikan response terstruktur untuk Flutter
    return {
        "success": True,
        "message": "Detail novel berhasil diambil",
        "data": {
            "id": story.id,
            "title": story.title,
            "synopsis": story.synopsis,
            "cover_url": story.cover_url,
            "author_username": author_username,
            "views": views_count,
            "stars": stars_count,
            "total_chapters": total_chapters,
            "chapters": [
                {
                    "id": ch.id,
                    "title": ch.title,
                    "chapter_number": ch.chapter_number,
                    "created_at": ch.created_at.isoformat() if ch.created_at else None
                } for ch in chapters
            ]
        }
    }