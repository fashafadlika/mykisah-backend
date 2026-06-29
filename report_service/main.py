from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import reports

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MyKisah - Report Service")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports.router)

@app.get("/")
def root():
    return {"message": "Report Service is running"}
