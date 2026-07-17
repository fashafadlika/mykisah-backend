import random 
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks 
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date, timedelta 

from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from passlib.context import CryptContext


from app.utils import send_otp_email 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

class UserRegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    birthdate: Optional[str] = None

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    data: UserRegisterSchema, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    # Cek email sudah/belum terdaftar di database
    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terdaftar!"
        )
    
    # Username sudah/belum terdaftar di database
    existing_username = db.query(User).filter(User.username == data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username sudah digunakan!"
        )
    
    # Enkripsi Password
    hashed_password = pwd_context.hash(data.password)

    # Parsing Tanggal Lahir
    parsed_birthdate = None
    if data.birthdate:
        try:
            parsed_birthdate = datetime.strptime(data.birthdate, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format tanggal lahir salah! Harus YYYY-MM-DD."
            )
        
    # --- PROSES PEMBUATAN OTP ---
    # Generate 6 digit angka acak
    otp_code = str(random.randint(100000, 999999)) 
    # Atur waktu kedaluwarsa (5 menit dari sekarang)
    otp_expired_at = datetime.now() + timedelta(minutes=5)
        
    # Membuat data user baru
    new_user = User(
        username=data.username,
        email=data.email,
        password=hashed_password,
        birthdate=parsed_birthdate,
        is_verified=False,
        otp_code=otp_code,             
        otp_expired_at=otp_expired_at  
    )

    # Simpan ke database
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  
        
        # --- KIRIM EMAIL SETELAH DATA BERHASIL DISIMPAN ---
        # Email akan dikirim di belakang layar sehingga respons API tetap cepat
        background_tasks.add_task(send_otp_email, new_user.email, otp_code)

    except Exception as e:
        db.rollback()  
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menyimpan ke database: {str(e)}"
        )

    # Respon sukses
    return {
        "success": True,
        "message": f"User {new_user.username} berhasil didaftarkan! Silakan cek email untuk verifikasi OTP.",
        "data": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "birthdate": str(new_user.birthdate) if new_user.birthdate else None
        }
    }