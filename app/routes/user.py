from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User

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