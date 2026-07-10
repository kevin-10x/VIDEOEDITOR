from pydantic import BaseModel
from typing import Optional


class SubtitleSegment(BaseModel):
    start: float
    end: float
    text: str


class SubtitleResponse(BaseModel):
    filename: str
    segments: list[SubtitleSegment]
    srt_content: str
    total_duration: float


class Highlight(BaseModel):
    start: float
    end: float
    score: float
    label: str


class HighlightResponse(BaseModel):
    filename: str
    highlights: list[Highlight]
    total_duration: float


class SceneTransition(BaseModel):
    timestamp: float
    frame_before: str
    frame_after: str
    intensity: float


class SceneTransitionResponse(BaseModel):
    filename: str
    transitions: list[SceneTransition]
    total_scenes: int


class ThumbnailResponse(BaseModel):
    filename: str
    thumbnails: list[str]
    total_count: int


class VoiceEnhanceResponse(BaseModel):
    filename: str
    output_file: str
    processing_time: float


class ShortClipRequest(BaseModel):
    start_time: float = 0.0
    duration: Optional[int] = None
    max_clips: int = 5
    content_type: str = "auto"


class ShortClip(BaseModel):
    start: float
    end: float
    score: float
    output_file: str


class ShortClipResponse(BaseModel):
    filename: str
    clips: list[ShortClip]
    total_clips: int


class HealthResponse(BaseModel):
    status: str
    version: str
    ffmpeg_available: bool
    whisper_available: bool


class ErrorResponse(BaseModel):
    detail: str
    error_code: str
