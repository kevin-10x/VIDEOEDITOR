import subprocess
import json
from pathlib import Path
from app.core.config import settings
from app.utils.ffmpeg_helpers import extract_audio, get_video_duration


_model = None


def _get_model():
    global _model
    if _model is None:
        _model = whisper.load_model(settings.WHISPER_MODEL_SIZE)
    return _model


def generate_srt(segments: list[dict]) -> str:
    lines = []
    for i, seg in enumerate(segments, 1):
        start = _format_srt_time(seg["start"])
        end = _format_srt_time(seg["end"])
        text = seg["text"].strip()
        lines.append(f"{i}")
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def _format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def transcribe_video(video_path: str) -> dict:
    model = _get_model()
    audio_path = extract_audio(video_path, str(Path(video_path).with_suffix(".wav")))

    result = model.transcribe(
        audio_path,
        language="en",
        verbose=False,
        word_timestamps=True,
    )

    duration = get_video_duration(video_path)

    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": round(seg["start"], 3),
            "end": round(seg["end"], 3),
            "text": seg["text"],
        })

    return {
        "segments": segments,
        "srt_content": generate_srt(segments),
        "total_duration": duration,
    }


def check_whisper() -> bool:
    try:
        import whisper
        return True
    except ImportError:
        return False
