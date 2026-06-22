from fastapi import FastAPI

from database import Base, engine
from routes import auth
from routes import profile

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MyKisah - Users Service")

app.include_router(auth.router)
app.include_router(profile.router)


@app.get("/")
def root():
    return {"message": "Users Service is running"}

