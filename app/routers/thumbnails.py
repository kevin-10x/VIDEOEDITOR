from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.utils.file_utils import validate_video_upload, save_upload
from app.models.schemas import ThumbnailResponse
from app.processors.thumbnail_processor import generate_thumbnails
from app.core.config import settings
import uuid
from pathlib import Path

router = APIRouter(prefix="/thumbnails", tags=["thumbnails"])


@router.post("/generate", response_model=ThumbnailResponse)
async def create_thumbnails(
    file: UploadFile = File(...),
    count: int = Query(default=settings.THUMBNAIL_COUNT, ge=1, le=20),
):
    ext = await validate_video_upload(file)
    content = await file.read()

    uid = uuid.uuid4().hex[:8]
    filename = f"{Path(file.filename).stem}_{uid}{ext}"
    saved_path = save_upload(content, filename)

    try:
        result = generate_thumbnails(saved_path, count=count)
        return ThumbnailResponse(
            filename=filename,
            thumbnails=result["thumbnails"],
            total_count=result["total_count"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
