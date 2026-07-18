from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.database import get_db
from app.models.story import Story, StoryGenre
from app.models.user import User
from app.dependencies import get_current_user
from app.routes.genres import GENRES
from app.schemas.submission import SubmissionCreate

router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"]
)

# Mapping id -> nama genre, diambil dari data genre yang sudah ada di router genres
GENRE_MAP = {genre["id"]: genre["name"] for genre in GENRES}

MAX_PENDING_SUBMISSIONS = 5


# Ubah 1 object Story jadi dict rapi buat response API, termasuk ambil nama genre
def _serialize_story(story: Story, username: str, db: Session) -> dict:
    genre_ids = (
        db.query(StoryGenre.genre_id)
        .filter(StoryGenre.story_id == story.id)
        .all()
    )
    genre_names = [GENRE_MAP.get(genre_id, "Unknown") for (genre_id,) in genre_ids]

    return {
        "id": story.id,
        "title": story.title,
        "cover_url": story.cover_url,
        "author_username": username,
        "status": story.status,
        "reject_message": story.reject_message,
        "genres": genre_names,
        "submitted_at": story.submitted_at.isoformat() if story.submitted_at else None,
        "published_at": story.published_at.isoformat() if story.published_at else None,
    }


# Cek berapa banyak submission pending milik user, buat batasi spam submit
def _get_pending_count(db: Session, user_id: int) -> int:
    return (
        db.query(Story)
        .filter(Story.user_id == user_id, Story.status == "pending")
        .count()
    )


# Simpan story baru + relasi genre-nya ke database dalam 1 transaksi
def _create_story_with_genres(db: Session, user_id: int, payload: SubmissionCreate) -> Story:
    try:
        new_story = Story(
            user_id=user_id,
            title=payload.title,
            synopsis=payload.synopsis,
            cover_url=payload.cover_url,
            status="pending",
            submitted_at=func.now(),
        )
        db.add(new_story)
        db.flush()  # biar new_story.id kebentuk tanpa commit dulu

        db.add_all([
            StoryGenre(story_id=new_story.id, genre_id=genre_id)
            for genre_id in payload.genre_ids
        ])

        db.commit()
        db.refresh(new_story)
        return new_story

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Gagal menyimpan submission")


# Submit novel baru, otomatis status = pending, tunggu review admin
@router.post("/")
def create_submission(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if _get_pending_count(db, current_user.id) >= MAX_PENDING_SUBMISSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Maksimal {MAX_PENDING_SUBMISSIONS} submission pending dalam antrian",
        )

    new_story = _create_story_with_genres(db, current_user.id, payload)

    return {
        "success": True,
        "message": "Novel berhasil disubmit, menunggu review admin",
        "data": _serialize_story(new_story, current_user.username, db),
    }


# Ambil submission milik user login dengan status pending, buat tab "Pending"
@router.get("/pending")
def get_pending_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stories = (
        db.query(Story)
        .filter(Story.user_id == current_user.id, Story.status == "pending")
        .order_by(desc(Story.submitted_at))
        .all()
    )

    return {
        "success": True,
        "message": "Berhasil mengambil submission pending",
        "data": [_serialize_story(s, current_user.username, db) for s in stories],
    }


# Ambil submission milik user login yang sudah diproses (published/rejected), buat tab "History"
@router.get("/history")
def get_submission_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stories = (
        db.query(Story)
        .filter(
            Story.user_id == current_user.id,
            Story.status.in_(["published", "rejected"]),
        )
        .order_by(desc(Story.submitted_at))
        .all()
    )

    return {
        "success": True,
        "message": "Berhasil mengambil riwayat submission",
        "data": [_serialize_story(s, current_user.username, db) for s in stories],
    }


# PENTING: route dinamis ini harus di bawah /pending dan /history,
# supaya FastAPI gak salah tangkep "pending"/"history" sebagai story_id
# Ambil detail 1 submission spesifik milik user login, buat tombol "Details Novel"
@router.get("/{story_id}")
def get_submission_detail(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    story = (
        db.query(Story)
        .filter(Story.id == story_id, Story.user_id == current_user.id)
        .first()
    )

    if not story:
        raise HTTPException(status_code=404, detail="Submission tidak ditemukan")

    return {
        "success": True,
        "message": "Detail submission berhasil diambil",
        "data": _serialize_story(story, current_user.username, db),
    }