from fastapi import APIRouter, Depends
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/users/me")
def read_users_me(current_user = Depends(get_current_user)):
    # Sekarang current_user adalah objek model User
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "bio": current_user.bio,
        "avatar_url": current_user.profile_picture # Mapping kolom DB ke JSON API
    }