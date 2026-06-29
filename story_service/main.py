from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routes import stories
from routes import genres

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MyKisah - Story Service")

# Konfigurasi CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Saat produksi, ganti "*" dengan URL frontend (misal: "http://localhost:3000")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stories.router)
app.include_router(genres.router)

@app.get("/")
def root():
    return {"message": "Story Service is running"}