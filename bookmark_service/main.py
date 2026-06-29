# Entry point Bookmark Service — inisialisasi FastAPI app, CORS, router, dan global exception handler.
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from database import Base, engine
from routes.bookmarks import router as bookmarks_router
from schemas.base import ErrorResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MyKisah - Bookmark Service")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Router
app.include_router(bookmarks_router)

# --- Exception Handlers untuk Menjamin Response Konsisten ---

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Menangkap HTTPException (misal: 400 Bad Request, 404 Not Found, 403 Forbidden).
    """
    response_content = ErrorResponse(
        message=str(exc.detail),
        errors=None
    ).model_dump()

    return JSONResponse(
        status_code=exc.status_code,
        content=response_content
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Menangkap Validation Error (422 Unprocessable Entity) dari Pydantic.
    """
    # Parsing error detail menjadi format yang lebih rapi
    errors = []
    for err in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in err["loc"]),
            "message": err["msg"],
            "type": err["type"]
        })

    response_content = ErrorResponse(
        message="Request validation failed.",
        errors=errors
    ).model_dump()

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_content
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Menangkap general / server error lainnya (500 Internal Server Error).
    """
    # Catatan: Di production, error detail asli sebaiknya tidak dipaparkan ke user secara mentah.
    # Kita bisa simpan error di logger log.
    response_content = ErrorResponse(
        message="Terjadi kesalahan internal server.",
        errors=str(exc)
    ).model_dump()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_content
    )

@app.get("/")
def root():
    return {"message": "Bookmark Service is running"}
