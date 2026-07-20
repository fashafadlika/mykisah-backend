from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app.models.story import Story, Chapter, StoryView, StoryGenre, ChapterView
from app.models.user import User
from app.models.bookmark import Bookmark
from app.routes.genres import GENRES

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
    # Query: Ambil story berdasarkan chapter yang paling baru dibuat (group by untuk MySQL compatibility)
    latest_query = db.query(Story)\
        .join(Chapter, Story.id == Chapter.story_id)\
        .filter(Story.status == 'published')\
        .group_by(Story.id)\
        .order_by(desc(func.max(Chapter.created_at)))\
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

# PENTING: route /search harus di atas /{story_id} agar FastAPI tidak salah baca "search" sebagai story_id
@router.get("/search")
def search_stories(
    query: Optional[str] = Query(None),
    genre_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    # Base: hanya story yang sudah published
    q = db.query(Story).filter(Story.status == "published")

    if query:
        q = q.filter(Story.title.ilike(f"%{query}%"))

    if genre_name:
        # Cari genre_id dari list hardcoded GENRES
        genre_id = next((g["id"] for g in GENRES if g["name"].lower() == genre_name.lower()), None)
        if genre_id is None:
            return []  # genre tidak dikenal → hasil kosong
        q = q.join(StoryGenre, Story.id == StoryGenre.story_id).filter(StoryGenre.genre_id == genre_id)

    stories = q.all()

    # Mapping id → name untuk lookup genre setiap story
    genre_map = {g["id"]: g["name"] for g in GENRES}

    return [
        {
            "id": s.id,
            "title": s.title,
            "user_id": s.user_id,
            "cover_url": s.cover_url,
            "synopsis": s.synopsis or "",
            "genres": [
                {"name": genre_map.get(sg.genre_id, "Unknown")}
                for sg in db.query(StoryGenre).filter(StoryGenre.story_id == s.id).all()
            ],
        }
        for s in stories
    ]


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


@router.get("/{story_id}/chapters")
def get_story_chapters(story_id: int, db: Session = Depends(get_db)):
    # Pastikan novel ada
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Novel tidak ditemukan")

    # Ambil semua chapter dari cerita ini
    chapters = db.query(Chapter).filter(Chapter.story_id == story_id).order_by(Chapter.chapter_number.asc()).all()

    result = []
    for ch in chapters:
        views_count = db.query(func.count(ChapterView.id)).filter(ChapterView.chapter_id == ch.id).scalar() or 0
        result.append({
            "id": ch.id,
            "story_id": ch.story_id,
            "title": ch.title,
            "content": ch.content,
            "chapter_number": ch.chapter_number,
            "views_count": views_count,
            "created_at": ch.created_at.isoformat() if ch.created_at else None,
            "updated_at": ch.updated_at.isoformat() if ch.updated_at else None
        })
    return result


@router.post("/chapters/{chapter_id}/view")
def record_chapter_view(chapter_id: int, user_id: int, db: Session = Depends(get_db)):
    """Catat view chapter (unik per user). Tidak bisa di-spam."""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter tidak ditemukan")

    # Cek apakah user sudah pernah membaca chapter ini
    existing = db.query(ChapterView).filter(
        ChapterView.chapter_id == chapter_id,
        ChapterView.user_id == user_id
    ).first()

    if existing:
        # Sudah pernah baca — tidak tambah view lagi
        views_count = db.query(func.count(ChapterView.id)).filter(ChapterView.chapter_id == chapter_id).scalar() or 0
        return {"success": True, "already_viewed": True, "views_count": views_count}

    # Tambah record view baru
    new_view = ChapterView(chapter_id=chapter_id, user_id=user_id)
    db.add(new_view)
    db.commit()

    views_count = db.query(func.count(ChapterView.id)).filter(ChapterView.chapter_id == chapter_id).scalar() or 0
    return {"success": True, "already_viewed": False, "views_count": views_count}
