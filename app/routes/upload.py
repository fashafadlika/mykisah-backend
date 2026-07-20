import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Request
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

# Folder penyimpanan gambar cover
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "static", "covers")


@router.post("/cover", status_code=status.HTTP_200_OK)
async def upload_cover(request: Request, file: UploadFile = File(...)):
    """
    Upload gambar cover novel.
    Menerima file gambar (jpg, jpeg, png, webp) dan menyimpannya ke folder static/covers/.
    Mengembalikan URL publik file yang bisa disimpan sebagai cover_url di database.
    """
    # Validasi tipe file (baik lewat content_type maupun ekstensi file)
    allowed_content_types = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    
    ext = os.path.splitext(file.filename or "cover.jpg")[1].lower()
    
    if file.content_type not in allowed_content_types and ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipe file tidak didukung. Gunakan JPG, PNG, atau WebP."
        )

    # Validasi ukuran file (max 5 MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ukuran file terlalu besar. Maksimal 5 MB."
        )

    # Buat nama file unik untuk menghindari konflik
    ext = os.path.splitext(file.filename or "cover.jpg")[1] or ".jpg"
    unique_filename = f"{uuid.uuid4().hex}{ext}"

    # Pastikan direktori upload ada
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Simpan file ke disk
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    # Return URL publik file secara dinamis sesuai host pemanggil (localhost, emulator 10.0.2.2, atau ngrok)
    base_url = str(request.base_url)
    cover_url = f"{base_url}static/covers/{unique_filename}"

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Cover berhasil diupload.",
            "cover_url": cover_url,
        }
    )
