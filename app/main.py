from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import user
from app.routes import auth
from app.routes import notification
from app.routes import reading_progres
from app.database import engine, Base

# Import models agar terdaftar ke Base.metadata sebelum create_all
from app.models.notification import Notification       # noqa: F401
from app.models.reading_progres import ReadingProgress  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MyKisah API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(notification.router)
app.include_router(reading_progres.router)

@app.get("/")
def home():
    return {
        "status": "Active",
        "message": "MyKisah API"
    }