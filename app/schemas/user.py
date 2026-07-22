from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: str
    birthdate: Optional[date] = None

class UserProfileResponse(BaseModel):
    id: int
    email: str
    username: Optional[str] = None
    birthdate: Optional[str] = None
    bio: Optional[str] = None
    # Kita map 'profile_picture' (DB) ke 'avatar_url' (Flutter)
    avatar_url: Optional[str] = Field(alias="profile_picture")
    role: Optional[str] = None

    class Config:
        from_attributes = True 
        populate_by_name = True 

class UserUpdate(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
 
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

