from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import user, auth, story, bookmark, notification, reading_progres, genres, submission, admin_review, report, admin_dashboard, my_works_chapters, upload
from app.database import engine, Base
from app.models.bookmark import Bookmark
from app.models.story import Story, Chapter, StoryView, ChapterView
from app.models.report import Report
from app.models.user import User 

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
app.include_router(story.router)
app.include_router(bookmark.router)
app.include_router(genres.router)
app.include_router(submission.router)
app.include_router(admin_review.router)
app.include_router(report.router)
app.include_router(admin_dashboard.router)
app.include_router(my_works_chapters.router)
app.include_router(upload.router)

import os
# STATIC_DIR ada di root project (satu level di atas folder app/)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
STATIC_DIR = os.path.normpath(STATIC_DIR)
os.makedirs(os.path.join(STATIC_DIR, "covers"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def home():
    return {
        "status": "Active",
        "message": "MyKisah API"
    }