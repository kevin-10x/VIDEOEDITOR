from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from app.core.config import settings
from app.utils.ffmpeg_helpers import check_ffmpeg
from app.processors.subtitle_processor import check_whisper
from app.models.schemas import HealthResponse
from app.routers import subtitles, highlights, scenes, thumbnails, voice, clips
import uuid

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Video Editor API - Auto subtitles, highlights, scene detection, thumbnails, voice enhancement, and short-form clips",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(subtitles.router, prefix=settings.API_PREFIX)
app.include_router(highlights.router, prefix=settings.API_PREFIX)
app.include_router(scenes.router, prefix=settings.API_PREFIX)
app.include_router(thumbnails.router, prefix=settings.API_PREFIX)
app.include_router(voice.router, prefix=settings.API_PREFIX)
app.include_router(clips.router, prefix=settings.API_PREFIX)


@app.get("/", tags=["root"])
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "endpoints": {
            "subtitles": f"{settings.API_PREFIX}/subtitles/generate",
            "highlights": f"{settings.API_PREFIX}/highlights/detect",
            "scenes": f"{settings.API_PREFIX}/scenes/detect-transitions",
            "thumbnails": f"{settings.API_PREFIX}/thumbnails/generate",
            "voice": f"{settings.API_PREFIX}/voice/enhance",
            "clips": f"{settings.API_PREFIX}/clips/create",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        ffmpeg_available=check_ffmpeg(),
        whisper_available=check_whisper(),
    )


@app.post(f"{settings.API_PREFIX}/upload", tags=["upload"])
async def upload_video(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {ext}")

    content = await file.read()
    uid = uuid.uuid4().hex[:8]
    filename = f"{Path(file.filename).stem}_{uid}{ext}"
    file_path = settings.UPLOAD_DIR / filename
    file_path.write_bytes(content)

    return {
        "filename": filename,
        "original_name": file.filename,
        "size_bytes": len(content),
        "path": str(file_path),
    }


@app.get(f"{settings.API_PREFIX}/download/{{filename}}", tags=["download"])
async def download_file(filename: str):
    file_path = settings.OUTPUT_DIR / filename
    if file_path.exists():
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/octet-stream",
        )
    return JSONResponse(status_code=404, content={"detail": "File not found"})
