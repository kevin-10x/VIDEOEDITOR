from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.file_utils import validate_video_upload, save_upload
from app.models.schemas import VoiceEnhanceResponse
from app.processors.voice_processor import enhance_voice, get_audio_filters
import uuid
from pathlib import Path

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/enhance", response_model=VoiceEnhanceResponse)
async def enhance_audio(file: UploadFile = File(...)):
    ext = await validate_video_upload(file)
    content = await file.read()

    uid = uuid.uuid4().hex[:8]
    filename = f"{Path(file.filename).stem}_{uid}{ext}"
    saved_path = save_upload(content, filename)

    try:
        result = enhance_voice(saved_path)
        return VoiceEnhanceResponse(
            filename=filename,
            output_file=result["output_file"],
            processing_time=result["processing_time"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filters")
async def list_filters():
    return get_audio_filters()
