from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional


# ── Request: dikirim Flutter ke backend ──

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: str
    birthdate: Optional[date] = None


class VerifyOTP(BaseModel):
    email: EmailStr
    otp_code: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ── Response: dikirim backend ke Flutter ──

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    birthdate: Optional[date] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str

    class Config:
        from_attributes = True
        populate_by_name = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ResendOTP(BaseModel):
    email: EmailStr