# services/reading_progress_service.py

from sqlalchemy.orm import Session
from models.reading_progress import ReadingProgress
from schemas.reading_progress import ReadingProgressCreate


def upsert_progress(db: Session, data: ReadingProgressCreate) -> tuple[ReadingProgress, bool]:
    """
    Insert jika belum ada, update jika sudah ada (upsert per user+story).
    Return: (ReadingProgress object, is_new: bool)
    is_new=True  → record baru dibuat (HTTP 201)
    is_new=False → record yang ada diperbarui (HTTP 200)
    """
    existing = db.query(ReadingProgress).filter(
        ReadingProgress.user_id == data.user_id,
        ReadingProgress.story_id == data.story_id
    ).first()

    if existing:
        existing.chapter_id = data.chapter_id
        # last_read_at diperbarui otomatis oleh onupdate=func.now()
        db.commit()
        db.refresh(existing)
        return existing, False
    else:
        new_progress = ReadingProgress(
            user_id=data.user_id,
            story_id=data.story_id,
            chapter_id=data.chapter_id
        )
        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)
        return new_progress, True


def get_user_progress(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> list[ReadingProgress]:
    """
    Ambil semua reading progress milik user, diurutkan terbaru dulu (last_read_at DESC).
    """
    return (
        db.query(ReadingProgress)
        .filter(ReadingProgress.user_id == user_id)
        .order_by(ReadingProgress.last_read_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_progress_by_id(db: Session, progress_id: int) -> ReadingProgress | None:
    """Ambil satu record berdasarkan ID. Return None jika tidak ditemukan."""
    return db.query(ReadingProgress).filter(ReadingProgress.id == progress_id).first()


def delete_progress(db: Session, progress: ReadingProgress) -> None:
    """Hapus record dari database."""
    db.delete(progress)
    db.commit()
