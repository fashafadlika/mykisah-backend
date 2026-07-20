from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routes import stories
from routes import genres
from routes import submissions
from search_service.search_routes import router as search_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MyKisah - Story Service")

# Konfigurasi CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Saat produksi, ganti "*" dengan URL frontend (misal: "http://127.0.0.1:8000")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from routes import chapters

app.include_router(stories.router)
app.include_router(genres.router)
app.include_router(chapters.router)
app.include_router(submissions.router)
app.include_router(search_router)

@app.get("/")
def root():
    return {"message": "Story Service is running"}