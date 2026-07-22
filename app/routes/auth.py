import random 
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks 
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date, timedelta 
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.user import RoleEnum
from passlib.context import CryptContext
from app.utils import send_otp_email, create_access_token


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

class VerifyOTPSchema(BaseModel):
    email: EmailStr
    otp_code: str

class ResendOTPSchema(BaseModel):
    email: EmailStr

class ForgotPasswordSchema(BaseModel):
    email: EmailStr

class ResetPasswordSchema(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

@router.post("/verify-otp", status_code=status.HTTP_200_OK)
def verify_otp(data: VerifyOTPSchema, db: Session = Depends(get_db)):
    # 1. Cari user berdasarkan email
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan!"
        )

    # 2. Cek apakah akun sudah terverifikasi sebelumnya
    if user.is_verified:
        return {"success": True, "message": "Akun sudah terverifikasi sebelumnya."}

    # 3. Cek kecocokan kode OTP
    if user.otp_code != data.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP salah!"
        )

    # 4. Cek apakah OTP sudah kedaluwarsa
    if user.otp_expired_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP sudah kedaluwarsa! Silakan minta kode baru."
        )

    # 5. Jika semua cek lolos, ubah status verifikasi menjadi True
    try:
        user.is_verified = True
        user.otp_code = None        
        user.otp_expired_at = None  
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal memverifikasi akun."
        )

    return {
        "success": True,
        "message": "Verifikasi berhasil! Akun Anda sudah aktif."
    }

@router.post("/resend-otp", status_code=status.HTTP_200_OK)
def resend_otp(
    data: ResendOTPSchema, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    # 1. Cari user berdasarkan email
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email tidak ditemukan!"
        )

    # 2. Cek apakah user sebenarnya sudah terverifikasi
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Akun ini sudah terverifikasi. Silakan langsung login."
        )

    # 3. Generate ulang kode OTP baru & perbarui waktu kedaluwarsa (5 menit lagi)
    new_otp = str(random.randint(100000, 999999))
    user.otp_code = new_otp
    user.otp_expired_at = datetime.now() + timedelta(minutes=5)

    try:
        db.commit()
        # 4. Kirim ulang email di background task
        background_tasks.add_task(send_otp_email, user.email, new_otp)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengirim ulang OTP."
        )

    return {
        "success": True,
        "message": "Kode OTP baru telah dikirim ke email Anda."
    }

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
        otp_expired_at=otp_expired_at,
        role=RoleEnum.user,
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

@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(data: UserLoginSchema, db: Session = Depends(get_db)):
    # Cari user berdasarkan email
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email atau password salah!"
        )

    # Cek verifikasi password brypt
    if not pwd_context.verify(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email atau password salah!"
        )

    # KEAMANAN UTAMA: Blokir user jika belum verifikasi OTP
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akun Anda belum diverifikasi! Silakan verifikasi OTP terlebih dahulu."
        )

    # Buat JWT Token (berlaku misalnya 1 hari)
    access_token_expires = timedelta(days=1)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}, 
        expires_delta=access_token_expires
    )

    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role.value,
    }


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    data: ForgotPasswordSchema, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email tidak terdaftar!"
        )

    otp_code = str(random.randint(100000, 999999))
    user.otp_code = otp_code
    user.otp_expired_at = datetime.now() + timedelta(minutes=5)

    try:
        db.commit()
        background_tasks.add_task(send_otp_email, user.email, otp_code, True)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengirim OTP."
        )

    return {
        "success": True,
        "message": "Kode OTP untuk reset password telah dikirim ke email Anda."
    }


@router.post("/verify-reset-otp", status_code=status.HTTP_200_OK)
def verify_reset_otp(data: VerifyOTPSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan!"
        )

    if user.otp_code != data.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP salah!"
        )

    if user.otp_expired_at and user.otp_expired_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP sudah kedaluwarsa! Silakan minta kode baru."
        )

    return {
        "success": True,
        "message": "OTP valid. Silakan buat password baru."
    }


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(data: ResetPasswordSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan!"
        )

    if user.otp_code != data.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP salah atau sudah digunakan!"
        )

    if user.otp_expired_at and user.otp_expired_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP sudah kedaluwarsa!"
        )

    hashed_password = pwd_context.hash(data.new_password)
    user.password = hashed_password
    user.otp_code = None
    user.otp_expired_at = None

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mereset password."
        )

    return {
        "success": True,
        "message": "Password berhasil diubah! Silakan login dengan password baru."
    }