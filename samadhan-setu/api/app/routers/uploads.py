import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app import models
from app.config import settings
from app.deps import get_current_user

router = APIRouter(prefix="/uploads", tags=["uploads"])

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
ALLOWED_MIME_PREFIXES = ("image/", "application/pdf")


@router.post("")
def upload_file(file: UploadFile, current_user: models.User = Depends(get_current_user)):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    if file.content_type is None or not any(file.content_type.startswith(p) for p in ALLOWED_MIME_PREFIXES):
        raise HTTPException(status_code=422, detail={"detail": "Unsupported file type", "code": "BAD_MIME"})

    contents = file.file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_MB:
        raise HTTPException(status_code=422, detail={"detail": "File too large", "code": "FILE_TOO_LARGE"})

    ext = Path(file.filename or "upload").suffix
    stored_name = f"{uuid.uuid4()}{ext}"
    (UPLOAD_DIR / stored_name).write_bytes(contents)

    return {
        "file_name": file.filename,
        "stored_name": stored_name,
        "mime_type": file.content_type,
        "size_bytes": len(contents),
        "url": f"/uploads/{stored_name}",
    }
