from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user
from app.routes import auth
from app.routes import story
from app.database import engine, Base
from app.models.story import Story, Chapter, StoryView 



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
app.include_router(story.router)

@app.get("/")
def home():
    return {
        "status": "Active",
        "message": "MyKisah API"
    }