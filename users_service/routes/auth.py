import random
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user import UserRegister, VerifyOTP, UserLogin, TokenResponse, ResendOTP
from core.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.email == payload.email) | (User.username == payload.username)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email atau username sudah digunakan",
        )

    otp_code = generate_otp()
    otp_expired_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    new_user = User(
        email=payload.email,
        password=hash_password(payload.password),
        username=payload.username,
        birthdate=payload.birthdate,
        is_verified=False,
        otp_code=otp_code,
        otp_expired_at=otp_expired_at,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # TODO: ganti print ini dengan kirim email beneran nanti
    print(f"[OTP] Kode untuk {payload.email}: {otp_code}")

    return {"message": "Registrasi berhasil, cek OTP untuk verifikasi", "email": new_user.email}


@router.post("/verify-otp")
def verify_otp(payload: VerifyOTP, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Akun sudah terverifikasi")

    if user.otp_code != payload.otp_code:
        raise HTTPException(status_code=400, detail="Kode OTP salah")

    now = datetime.now(timezone.utc)
    expired_at = user.otp_expired_at
    if expired_at.tzinfo is None:
        expired_at = expired_at.replace(tzinfo=timezone.utc)
    if now > expired_at:
        raise HTTPException(status_code=400, detail="Kode OTP sudah expired")

    user.is_verified = True
    user.otp_code = None
    user.otp_expired_at = None
    db.commit()

    return {"message": "Verifikasi berhasil, silakan login"}


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Email atau password salah")

    if not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Email atau password salah")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Akun belum diverifikasi, cek OTP")

    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token)

@router.post("/resend-otp")
def resend_otp(payload: ResendOTP, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Akun sudah terverifikasi")
    
    now = datetime.now(timezone.utc)

    #Cooldown otp_expired_at = waktu_kirim + 10 menit
    if user.otp_expired_at:
        expired_at = user.otp_expired_at
        if expired_at.tzinfo is None:
            expired_at = expired_at.replace(tzinfo=timezone.utc)
        last_sent_at = expired_at - timedelta(minutes=10)
        cooldown_until = last_sent_at + timedelta(seconds=60)
        if now < cooldown_until:
            remaining = int((cooldown_until - now).total_seconds())
            raise HTTPException(
                status_code=429,
                detail=f"Tunggu {remaining} detik sebelum minta OTP baru",
            )
        
    otp_code = generate_otp()
    otp_expired_at = now +timedelta(minutes=10)

    user.otp_code = otp_code
    user.otp_expired_at = otp_expired_at
    db.commit()

    print(f"[OTP] Kode baru untuk {payload.email}: {otp_code}")

    return {"message": "OTP baru sudah dikirim, cek email kamu"}