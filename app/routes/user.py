from fastapi import APIRouter, Depends
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"message": "Ini adalah data rahasia", "user": current_user}