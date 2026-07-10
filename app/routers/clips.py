from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
from app.utils.file_utils import validate_video_upload, save_upload
from app.models.schemas import ShortClipResponse, ShortClip
from app.processors.clip_processor import create_short_clips
import uuid
from pathlib import Path

router = APIRouter(prefix="/clips", tags=["clips"])


@router.post("/create", response_model=ShortClipResponse)
async def create_short_form_clips(
    file: UploadFile = File(...),
    start_time: float = Form(default=0.0),
    duration: Optional[int] = Form(default=None),
    max_clips: int = Form(default=5, ge=1, le=20),
    content_type: str = Form(default="auto"),
):
    ext = await validate_video_upload(file)
    content = await file.read()

    uid = uuid.uuid4().hex[:8]
    filename = f"{Path(file.filename).stem}_{uid}{ext}"
    saved_path = save_upload(content, filename)

    try:
        result = create_short_clips(
            video_path=saved_path,
            start_time=start_time,
            duration=duration,
            max_clips=max_clips,
            content_type=content_type,
        )
        return ShortClipResponse(
            filename=filename,
            clips=[ShortClip(**c) for c in result["clips"]],
            total_clips=result["total_clips"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
