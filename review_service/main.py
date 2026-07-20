from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routes import review

# Inisialisasi tabel di database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MyKisah - Review Service")

# Konfigurasi CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review.router)

@app.get("/")
def root():
    return {"message": "Review Service is running"}
