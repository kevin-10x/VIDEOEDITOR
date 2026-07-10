import os
from pathlib import Path


class Settings:
    PROJECT_NAME: str = "Video Editor API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    OUTPUT_DIR: Path = BASE_DIR / "outputs"

    MAX_UPLOAD_SIZE_MB: int = 500
    ALLOWED_VIDEO_EXTENSIONS: list[str] = [
        ".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv", ".m4v"
    ]

    WHISPER_MODEL_SIZE: str = os.getenv("WHISPER_MODEL_SIZE", "base")
    FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "ffmpeg")
    FFPROBE_PATH: str = os.getenv("FFPROBE_PATH", "ffprobe")

    HIGHLIGHT_MIN_DURATION: float = 3.0
    HIGHLIGHT_MAX_DURATION: float = 30.0
    HIGHLIGHT_THRESHOLD: float = 0.5

    SCENE_CHANGE_THRESHOLD: float = 27.0
    SCENE_MIN_GAP: float = 0.5

    SHORT_FORM_MAX_DURATION: int = 60
    SHORT_FORM_DEFAULT_DURATION: int = 30

    THUMBNAIL_COUNT: int = 5
    THUMBNAIL_WIDTH: int = 1280
    THUMBNAIL_HEIGHT: int = 720

    VOICE_ENHANCE_NOISE_LEVEL: float = 0.21
    VOICE_ENHANCE_STRENGTH: int = 10

    CORS_ORIGINS: list[str] = ["*"]

    def __init__(self):
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
