from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.database import get_db
from app.models.story import Story, StoryGenre
from app.models.user import User
from app.models.notification import Notification
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


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_submission(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Cek jumlah submission pending user, batasi biar gak spam submit
    pending_count = (
        db.query(Story)
        .filter(Story.user_id == current_user.id, Story.status == "pending")
        .count()
    )
    if pending_count >= MAX_PENDING_SUBMISSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maksimal {MAX_PENDING_SUBMISSIONS} submission pending dalam antrian!"
        )

    # 2. Simpan story baru + genre-nya + notifikasi ke admin, dalam 1 transaksi
    try:
        new_story = Story(
            user_id=current_user.id,
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

        # Cari semua admin, kirim notifikasi ke masing-masing
        admins = db.query(User).filter(User.role == "admin").all()
        db.add_all([
            Notification(
                user_id=admin.id,
                story_id=new_story.id,
                type="new_submission",
                message=f"{current_user.username} mengirim novel baru: {new_story.title}",
                is_read=False,
            )
            for admin in admins
        ])

        db.commit()
        db.refresh(new_story)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menyimpan submission: {str(e)}"
        )

    return {
        "success": True,
        "message": "Novel berhasil disubmit, menunggu review admin.",
        "data": _serialize_story(new_story, current_user.username, db)
    }


@router.get("/pending", status_code=status.HTTP_200_OK)
def get_pending_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ambil semua submission milik user yang berstatus pending
    stories = (
        db.query(Story)
        .filter(Story.user_id == current_user.id, Story.status == "pending")
        .order_by(desc(Story.submitted_at))
        .all()
    )

    return {
        "success": True,
        "message": "Berhasil mengambil submission pending.",
        "data": [_serialize_story(s, current_user.username, db) for s in stories]
    }


@router.get("/history", status_code=status.HTTP_200_OK)
def get_submission_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ambil semua submission milik user yang sudah diproses (published/rejected)
    stories = (
        db.query(Story)
        .filter(
            Story.user_id == current_user.id,
            Story.status.in_(["published", "rejected"])
        )
        .order_by(desc(Story.submitted_at))
        .all()
    )

    return {
        "success": True,
        "message": "Berhasil mengambil riwayat submission.",
        "data": [_serialize_story(s, current_user.username, db) for s in stories]
    }


# PENTING: route dinamis ini harus di bawah /pending dan /history,
# supaya FastAPI gak salah tangkep "pending"/"history" sebagai story_id
@router.get("/{story_id}", status_code=status.HTTP_200_OK)
def get_submission_detail(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Cari submission berdasarkan id, pastikan punya user yang login
    story = (
        db.query(Story)
        .filter(Story.id == story_id, Story.user_id == current_user.id)
        .first()
    )
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission tidak ditemukan!"
        )

    return {
        "success": True,
        "message": "Detail submission berhasil diambil.",
        "data": _serialize_story(story, current_user.username, db)
    }