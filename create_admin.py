from sqlalchemy.orm import Session
from app.database import SessionLocal
# Import models to ensure they are registered in SQLAlchemy's Base metadata
from app.models.bookmark import Bookmark
from app.models.story import Story, Chapter, StoryView, StoryGenre, StoryReview
from app.models.user import User, RoleEnum
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    db = SessionLocal()
    try:
        # Konfigurasi admin baru
        email = "admin@mykisah.com"
        username = "admin"
        
        existing_admin = db.query(User).filter(User.email == email).first()
        if existing_admin:
            print(f"Admin dengan email {email} sudah ada.")
            return

        # Hash password 'admin123'
        hashed_password = pwd_context.hash("admin123")

        new_admin = User(
            username=username,
            email=email,
            password=hashed_password,
            is_verified=True,  # Langsung diverifikasi
            role=RoleEnum.admin  # Role admin
        )

        db.add(new_admin)
        db.commit()
        print(f"Akun Admin berhasil dibuat!")
        print(f"Email: {email}")
        print(f"Username: {username}")
        print(f"Password: admin123")
    except Exception as e:
        db.rollback()
        print(f"Gagal membuat admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
