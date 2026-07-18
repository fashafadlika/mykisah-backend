from fastapi import APIRouter

router = APIRouter(prefix="/genres", tags=["genres"])

@router.get("/")
async def get_genres():
    return [
        {"id": 1, "name": "Action"},
        {"id": 2, "name": "Romance"},
        {"id": 3, "name": "Drama"},
        {"id": 4, "name": "Thriller"},
        {"id": 5, "name": "Historical"},
        {"id": 6, "name": "Sci-Fi"},
        {"id": 7, "name": "Slice of Life"},
        {"id": 8, "name": "Fantasy"},
        {"id": 9, "name": "Mystery"},
        {"id": 10, "name": "Tragedy"}
    ]