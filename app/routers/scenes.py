from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.file_utils import validate_video_upload, save_upload
from app.models.schemas import SceneTransitionResponse, SceneTransition
from app.processors.scene_processor import detect_scene_transitions
import uuid
from pathlib import Path

router = APIRouter(prefix="/scenes", tags=["scenes"])


@router.post("/detect-transitions", response_model=SceneTransitionResponse)
async def detect_transitions(file: UploadFile = File(...)):
    ext = await validate_video_upload(file)
    content = await file.read()

    uid = uuid.uuid4().hex[:8]
    filename = f"{Path(file.filename).stem}_{uid}{ext}"
    saved_path = save_upload(content, filename)

    try:
        result = detect_scene_transitions(saved_path)
        return SceneTransitionResponse(
            filename=filename,
            transitions=[SceneTransition(**t) for t in result["transitions"]],
            total_scenes=result["total_scenes"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
