from sqlalchemy import func, desc
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from app.database import get_db
from app.models.story import Story, StoryGenre, StoryReview, Chapter, StoryView, ChapterView
from app.models.report import Report
from app.models.user import User
from app.models.notification import Notification
from app.models.takedown import StoryTakedown
from app.dependencies import get_current_user
from app.routes.genres import GENRES

router = APIRouter(
    prefix="/admin/stories",
    tags=["Admin Review"]
)

GENRE_MAP = {genre["id"]: genre["name"] for genre in GENRES}


class RejectPayload(BaseModel):
    note: str = Field(..., min_length=5, max_length=500)


class ArchivePayload(BaseModel):
    reason: Optional[str] = Field(None, min_length=5, max_length=1000)
    report_id: Optional[int] = None


# Pastikan yang manggil endpoint ini memang admin, bukan user biasa
def _require_admin(current_user: User) -> None:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang bisa mengakses ini!"
        )


# Ambil 1 story berdasarkan id, pastikan statusnya masih pending (belum direview)
def _get_pending_story(db: Session, story_id: int) -> Story:
    story = db.query(Story).filter(Story.id == story_id).first()

    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission tidak ditemukan!"
        )

    if story.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Submission ini sudah direview sebelumnya (status: {story.status})!"
        )

    return story


# Ubah 1 object Story jadi dict rapi buat response API
def _serialize_story(story: Story, author: User, db: Session) -> dict:
    genre_ids = (
        db.query(StoryGenre.genre_id)
        .filter(StoryGenre.story_id == story.id)
        .all()
    )
    genre_names = [GENRE_MAP.get(genre_id, "Unknown") for (genre_id,) in genre_ids]

    username = author.username if author else "Unknown"
    avatar_url = author.profile_picture if author and author.profile_picture else None

    return {
        "id": story.id,
        "title": story.title,
        "synopsis": story.synopsis,
        "cover_url": story.cover_url,
        "author_username": username,
        "author_avatar_url": avatar_url,
        "status": story.status,
        "reject_message": story.reject_message,
        "genres": genre_names,
        "submitted_at": story.submitted_at.isoformat() if story.submitted_at else None,
        "published_at": story.published_at.isoformat() if story.published_at else None,
    }


@router.get("/pending", status_code=status.HTTP_200_OK)
def get_all_pending_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Pastikan yang akses admin
    _require_admin(current_user)

    # 2. Ambil semua submission pending dari SEMUA user, buat direview admin satu-satu
    stories = (
        db.query(Story)
        .filter(Story.status == "pending")
        .order_by(desc(Story.submitted_at))
        .all()
    )

    result = []
    for story in stories:
        author = db.query(User).filter(User.id == story.user_id).first()
        result.append(_serialize_story(story, author, db))

    return {
        "success": True,
        "message": "Berhasil mengambil semua submission pending.",
        "data": result
    }

@router.get("/history", status_code=status.HTTP_200_OK)
def get_review_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Pastikan yang akses admin
    _require_admin(current_user)

    # 2. Ambil semua submission yang SUDAH diproses (published/rejected) dari semua user
    stories = (
        db.query(Story)
        .filter(Story.status.in_(["published", "rejected"]))
        .order_by(desc(Story.submitted_at))
        .all()
    )

    result = []
    for story in stories:
        author = db.query(User).filter(User.id == story.user_id).first()
        result.append(_serialize_story(story, author, db))

    return {
        "success": True,
        "message": "Berhasil mengambil riwayat review.",
        "data": result
    }


@router.post("/{story_id}/approve", status_code=status.HTTP_200_OK)
def approve_submission(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Pastikan yang akses admin
    _require_admin(current_user)

    # 2. Ambil story, pastikan masih pending
    story = _get_pending_story(db, story_id)

    # 3. Update status story jadi published + isi tanggal publish
    try:
        story.status = "published"
        story.published_at = func.now()

        # 4. Catat histori review
        db.add(StoryReview(
            story_id=story.id,
            admin_id=current_user.id,
            action="approved",
            note=None,
            reviewed_at=func.now(),
        ))

        # 5. Kirim notifikasi ke user pemilik novel
        db.add(Notification(
            user_id=story.user_id,
            story_id=story.id,
            type="story_approved",
            message=f"Novel kamu '{story.title}' telah disetujui dan sudah bisa dibaca!",
            is_read=False,
        ))

        db.commit()
        db.refresh(story)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menyetujui submission: {str(e)}"
        )

    author = db.query(User).filter(User.id == story.user_id).first()

    return {
        "success": True,
        "message": f"Novel '{story.title}' berhasil disetujui.",
        "data": _serialize_story(story, author, db)
    }


@router.post("/{story_id}/reject", status_code=status.HTTP_200_OK)
def reject_submission(
    story_id: int,
    payload: RejectPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Pastikan yang akses admin
    _require_admin(current_user)

    # 2. Ambil story, pastikan masih pending
    story = _get_pending_story(db, story_id)

    # 3. Update status story jadi rejected + simpan alasan penolakan
    try:
        story.status = "rejected"
        story.reject_message = payload.note

        # 4. Catat histori review
        db.add(StoryReview(
            story_id=story.id,
            admin_id=current_user.id,
            action="rejected",
            note=payload.note,
            reviewed_at=func.now(),
        ))

        # 5. Kirim notifikasi ke user pemilik novel
        db.add(Notification(
            user_id=story.user_id,
            story_id=story.id,
            type="story_rejected",
            message=f"Novel kamu '{story.title}' ditolak. Alasan: {payload.note}",
            is_read=False,
        ))

        db.commit()
        db.refresh(story)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menolak submission: {str(e)}"
        )

    author = db.query(User).filter(User.id == story.user_id).first()

    return {
        "success": True,
        "message": f"Novel '{story.title}' telah ditolak.",
        "data": _serialize_story(story, author, db)
    }


@router.get("/{story_id}", status_code=status.HTTP_200_OK)
def get_submission_detail_for_admin(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Pastikan yang akses admin
    _require_admin(current_user)

    # 2. Ambil story berdasarkan id, pastikan ada
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission tidak ditemukan!"
        )

    # 3. Hitung total chapter dan ambil daftar chapternya (preview, tanpa content)
    chapters_data = (
        db.query(Chapter.id, Chapter.chapter_number, Chapter.title)
        .filter(Chapter.story_id == story.id)
        .order_by(Chapter.chapter_number.asc())
        .all()
    )

    chapters_list = [
        {
            "id": c.id,
            "chapter_number": c.chapter_number,
            "title": c.title
        }
        for c in chapters_data
    ]

    # 4. Serialisasi data story dan gabungkan dengan detail chapter
    author = db.query(User).filter(User.id == story.user_id).first()

    story_data = _serialize_story(story, author, db)
    story_data["total_chapters"] = len(chapters_list)
    story_data["chapters"] = chapters_list

    return {
        "success": True,
        "message": "Detail submission berhasil diambil.",
        "data": story_data
    }


@router.delete("/{story_id}", status_code=status.HTTP_200_OK)
def delete_story_by_admin(
    story_id: int,
    payload: Optional[ArchivePayload] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)

    story = db.query(Story).filter(Story.id == story_id).first()

    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Novel tidak ditemukan."
        )

    try:
        # 0. Kirim notifikasi ke penulis (gunakan 0 agar dikirim walau story dihapus)
        # Note: Notification harus tetap bisa diinsert walau story_id mengarah ke novel yang akan dihapus.
        # Karena story_id di Notification bisa ondelete="SET NULL" atau kita jadikan NULL.
        takedown_reason = (payload.reason if payload and payload.reason else "Dilakukan penghapusan oleh admin.")
        db.add(Notification(
            user_id=story.user_id,
            story_id=None, # Jangan gunakan story.id karena story akan di hard delete dan bisa melanggar ForeignKey
            type="story_taken_down",
            message=(
                f"Novel kamu '{story.title}' telah dihapus permanen (takedown) oleh admin. "
                f"Alasan: {takedown_reason}"
            ),
            is_read=False,
        ))

        # 1. Hapus report terkait
        from app.models.report import Report
        db.query(Report).filter(Report.story_id == story.id).delete(synchronize_session=False)

        # 2. Hapus chapter views terkait
        from app.models.story import Chapter, ChapterView, StoryView
        chapters = db.query(Chapter).filter(Chapter.story_id == story.id).all()
        chapter_ids = [ch.id for ch in chapters]
        if chapter_ids:
            db.query(ChapterView).filter(ChapterView.chapter_id.in_(chapter_ids)).delete(synchronize_session=False)
            
        # 3. Hapus data chapter, takedowns, dan story views
        db.query(Chapter).filter(Chapter.story_id == story.id).delete(synchronize_session=False)
        db.query(StoryView).filter(StoryView.story_id == story.id).delete(synchronize_session=False)
        db.query(StoryTakedown).filter(StoryTakedown.story_id == story.id).delete(synchronize_session=False)
        
        # 4. Hapus story (bookmarks, genres, reviews terhapus otomatis karena cascade delete-orphan)
        db.delete(story)
        db.commit()

        return {
            "success": True,
            "message": f"Novel '{story.title}' berhasil dihapus secara permanen."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menghapus novel: {str(e)}"
        )