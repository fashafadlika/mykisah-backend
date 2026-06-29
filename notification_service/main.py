from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routes import notification

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MyKisah - Notification Service")

# Configure CORS so the frontend can communicate with this service
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notification.router)

@app.get("/")
def root():
    return {"message": "Notification Service is running"}
