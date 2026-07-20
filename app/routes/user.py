from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserUpdate
import os
import uuid

router = APIRouter()

@router.get("/users/me")
def read_users_me(current_user = Depends(get_current_user)):
    # Sekarang current_user adalah objek model User
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "bio": current_user.bio,
        "avatar_url": current_user.profile_picture,
        "role": current_user.role.value,
    }

@router.patch("/users/me")
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_update.username is not None:
        new_username = user_update.username.strip()
        if not new_username:
            raise HTTPException(status_code=400, detail="Username tidak boleh kosong")
        # Periksa keunikan username
        existing_user = db.query(User).filter(User.username == new_username, User.id != current_user.id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username sudah digunakan oleh user lain")
        current_user.username = new_username
        
    if user_update.bio is not None:
        current_user.bio = user_update.bio.strip()
        
    if user_update.avatar_url is not None:
        current_user.profile_picture = user_update.avatar_url
        
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "bio": current_user.bio,
        "avatar_url": current_user.profile_picture,
        "role": current_user.role.value,
    }

@router.post("/users/upload-avatar")
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Mengunggah foto profil baru."""
    allowed_content_types = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    
    ext = os.path.splitext(file.filename or "avatar.jpg")[1].lower()
    
    if file.content_type not in allowed_content_types and ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Tipe file tidak didukung. Gunakan JPG, PNG, atau WebP."
        )

    # Validasi ukuran file (max 2 MB)
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Ukuran file terlalu besar. Maksimal 2 MB."
        )

    # Buat nama file unik
    unique_filename = f"{uuid.uuid4().hex}{ext}"

    # Tentukan folder upload untuk avatar
    avatar_dir = os.path.join(os.path.dirname(__file__), "..", "..", "static", "avatars")
    os.makedirs(avatar_dir, exist_ok=True)

    # Simpan file ke disk
    file_path = os.path.join(avatar_dir, unique_filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    # Dapatkan URL publik
    base_url = str(request.base_url)
    avatar_url = f"{base_url}static/avatars/{unique_filename}"

    return {"success": True, "url": avatar_url}

@router.get("/users/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Ambil informasi publik pengguna berdasarkan ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }
