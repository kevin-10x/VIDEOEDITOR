from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.file_utils import validate_video_upload, save_upload, output_path
from app.models.schemas import SubtitleResponse, SubtitleSegment
from app.processors.subtitle_processor import transcribe_video
from app.core.config import settings
from pathlib import Path
import uuid

router = APIRouter(prefix="/subtitles", tags=["subtitles"])


@router.post("/generate", response_model=SubtitleResponse)
async def generate_subtitles(file: UploadFile = File(...)):
    ext = await validate_video_upload(file)
    content = await file.read()

    uid = uuid.uuid4().hex[:8]
    filename = f"{Path(file.filename).stem}_{uid}{ext}"
    saved_path = save_upload(content, filename)

    try:
        result = transcribe_video(saved_path)
        return SubtitleResponse(
            filename=filename,
            segments=[SubtitleSegment(**s) for s in result["segments"]],
            srt_content=result["srt_content"],
            total_duration=result["total_duration"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-srt")
async def generate_srt_file(file: UploadFile = File(...)):
    ext = await validate_video_upload(file)
    content = await file.read()

    uid = uuid.uuid4().hex[:8]
    filename = f"{Path(file.filename).stem}_{uid}{ext}"
    saved_path = save_upload(content, filename)

    try:
        result = transcribe_video(saved_path)
        srt_path = output_path(filename, ".srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(result["srt_content"])
        return {"srt_file": Path(srt_path).name, "content": result["srt_content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
