from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.file_utils import validate_video_upload, save_upload
from app.models.schemas import HighlightResponse, Highlight
from app.processors.highlight_processor import detect_highlights
from app.core.config import settings
import uuid
from pathlib import Path

router = APIRouter(prefix="/highlights", tags=["highlights"])


@router.post("/detect", response_model=HighlightResponse)
async def detect_video_highlights(
    file: UploadFile = File(...),
    threshold: float = settings.HIGHLIGHT_THRESHOLD,
):
    ext = await validate_video_upload(file)
    content = await file.read()

    uid = uuid.uuid4().hex[:8]
    filename = f"{Path(file.filename).stem}_{uid}{ext}"
    saved_path = save_upload(content, filename)

    try:
        settings.HIGHLIGHT_THRESHOLD = threshold
        result = detect_highlights(saved_path)
        return HighlightResponse(
            filename=filename,
            highlights=[Highlight(**h) for h in result["highlights"]],
            total_duration=result["total_duration"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
