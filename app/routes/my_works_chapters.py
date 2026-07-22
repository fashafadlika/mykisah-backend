from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.story import Story, Chapter
from app.models.user import User
from app.models.bookmark import Bookmark
from app.models.notification import Notification
from app.dependencies import get_current_user
from app.schemas.submission import ChapterCreate, ChapterUpdate, ChapterResponse

router = APIRouter(
    prefix="/my-works",
    tags=["My Works - Chapters"],
)


# ─── Helper ──────────────────────────────────────────────────────────────────

def _get_owned_story(story_id: int, current_user: User, db: Session) -> Story:
    """Ambil cerita berdasarkan ID, pastikan milik user yang sedang login."""
    story = db.query(Story).filter(Story.id == story_id).first()

    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cerita tidak ditemukan.",
        )

    if story.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kamu tidak punya akses ke cerita ini.",
        )

    return story


def _serialize_chapter(chapter: Chapter) -> dict:
    """Ubah objek Chapter menjadi dict rapi untuk response API."""
    return {
        "id": chapter.id,
        "story_id": chapter.story_id,
        "title": chapter.title,
        "content": chapter.content,
        "chapter_number": chapter.chapter_number,
        "cover_url": chapter.cover_url,
        "created_at": chapter.created_at.isoformat() if chapter.created_at else None,
        "updated_at": chapter.updated_at.isoformat() if chapter.updated_at else None,
    }


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/{story_id}/chapters", status_code=status.HTTP_200_OK)
def get_chapters(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ambil semua chapter dari cerita milik user.
    Diurutkan berdasarkan nomor chapter secara ascending.
    """
    _get_owned_story(story_id, current_user, db)

    chapters = (
        db.query(Chapter)
        .filter(Chapter.story_id == story_id)
        .order_by(Chapter.chapter_number.asc())
        .all()
    )

    return {
        "success": True,
        "message": "Daftar chapter berhasil diambil.",
        "data": [_serialize_chapter(ch) for ch in chapters],
    }


@router.post("/{story_id}/chapters", status_code=status.HTTP_201_CREATED)
def add_chapter(
    story_id: int,
    payload: ChapterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Tambah chapter baru ke cerita yang sudah published.
    Nomor chapter dihitung otomatis berdasarkan chapter terakhir + 1.
    """
    story = _get_owned_story(story_id, current_user, db)

    if story.status != "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Hanya cerita yang sudah published yang bisa ditambahkan chapter baru (status saat ini: {story.status}).",
        )

    # Hitung nomor chapter berikutnya
    last_chapter = (
        db.query(Chapter)
        .filter(Chapter.story_id == story_id)
        .order_by(Chapter.chapter_number.desc())
        .first()
    )
    next_chapter_number = (last_chapter.chapter_number + 1) if last_chapter else 1

    try:
        new_chapter = Chapter(
            story_id=story_id,
            title=payload.title,
            content=payload.content,
            chapter_number=next_chapter_number,
            cover_url=payload.cover_url,
        )
        db.add(new_chapter)
        db.commit()
        db.refresh(new_chapter)
        
        # Kirim notifikasi ke semua user yang bookmark novel ini
        bookmarks = db.query(Bookmark).filter(Bookmark.story_id == story_id).all()
        for bookmark in bookmarks:
            notif = Notification(
                user_id=bookmark.user_id,
                story_id=story_id,
                chapter_id=new_chapter.id,
                type="new_chapter",
                message=f"Novel '{story.title}' yang kamu bookmark baru saja merilis bab baru: {payload.title}. Baca sekarang!"
            )
            db.add(notif)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menyimpan chapter: {str(e)}",
        )

    return {
        "success": True,
        "message": f"Chapter {next_chapter_number} berhasil ditambahkan.",
        "data": _serialize_chapter(new_chapter),
    }


@router.put("/{story_id}/chapters/{chapter_id}", status_code=status.HTTP_200_OK)
def update_chapter(
    story_id: int,
    chapter_id: int,
    payload: ChapterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Edit judul atau isi chapter. Hanya pemilik cerita yang bisa mengubah.
    Minimal satu field harus diisi.
    """
    _get_owned_story(story_id, current_user, db)

    chapter = (
        db.query(Chapter)
        .filter(Chapter.id == chapter_id, Chapter.story_id == story_id)
        .first()
    )

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter tidak ditemukan.",
        )

    if payload.title is None and payload.content is None and payload.cover_url is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimal satu field (title, content, atau cover_url) harus diisi.",
        )

    try:
        if payload.title is not None:
            chapter.title = payload.title
        if payload.content is not None:
            chapter.content = payload.content
        if payload.cover_url is not None:
            chapter.cover_url = payload.cover_url

        db.commit()
        db.refresh(chapter)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengupdate chapter: {str(e)}",
        )

    return {
        "success": True,
        "message": "Chapter berhasil diperbarui.",
        "data": _serialize_chapter(chapter),
    }


@router.delete("/{story_id}/chapters/{chapter_id}", status_code=status.HTTP_200_OK)
def delete_chapter(
    story_id: int,
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Hapus chapter dari cerita. Hanya pemilik cerita yang bisa menghapus.
    Setelah dihapus, nomor chapter yang tersisa tidak diurutkan ulang.
    """
    _get_owned_story(story_id, current_user, db)

    chapter = (
        db.query(Chapter)
        .filter(Chapter.id == chapter_id, Chapter.story_id == story_id)
        .first()
    )

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter tidak ditemukan.",
        )

    try:
        db.delete(chapter)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menghapus chapter: {str(e)}",
        )

    return {
        "success": True,
        "message": "Chapter berhasil dihapus.",
    }
