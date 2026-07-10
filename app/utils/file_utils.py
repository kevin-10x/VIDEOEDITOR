import os
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import settings


async def validate_video_upload(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{ext}'. Allowed: {settings.ALLOWED_VIDEO_EXTENSIONS}",
        )

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f}MB). Max: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    await file.seek(0)
    return ext


def save_upload(content: bytes, filename: str) -> str:
    file_path = settings.UPLOAD_DIR / filename
    file_path.write_bytes(content)
    return str(file_path)


def output_path(filename: str, suffix: str, subdir: str = "") -> str:
    stem = Path(filename).stem
    out_dir = settings.OUTPUT_DIR / subdir if subdir else settings.OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    return str(out_dir / f"{stem}{suffix}")


def unique_filename(original: str, suffix: str) -> str:
    stem = Path(original).stem
    ext = Path(original).suffix
    return f"{stem}_{suffix}{ext}"
