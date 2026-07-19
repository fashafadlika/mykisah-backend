from database import SessionLocal
from models.notification import Notification
import datetime

def fix_db():
    db = SessionLocal()
    try:
        # Cari notifikasi yang created_at nya None (kosong)
        notifications = db.query(Notification).filter(Notification.created_at.is_(None)).all()
        for n in notifications:
            n.created_at = datetime.datetime.utcnow()
        db.commit()
        print(f"Berhasil memperbaiki {len(notifications)} data yang error!")
    except Exception as e:
        print("Error:", e)
    finally:
        db.close()

if __name__ == "__main__":
    fix_db()
