import subprocess
from pathlib import Path
from app.core.config import settings
from app.utils.ffmpeg_helpers import get_video_duration
from app.processors.highlight_processor import detect_highlights


def create_short_clips(
    video_path: str,
    start_time: float = 0.0,
    duration: int = None,
    max_clips: int = 5,
    content_type: str = "auto",
) -> dict:
    duration = duration or settings.SHORT_FORM_DEFAULT_DURATION
    duration = min(duration, settings.SHORT_FORM_MAX_DURATION)

    filename = Path(video_path).stem
    out_dir = settings.OUTPUT_DIR / "short_clips" / filename
    out_dir.mkdir(parents=True, exist_ok=True)

    video_duration = get_video_duration(video_path)

    if content_type == "auto":
        highlights = detect_highlights(video_path)
        segments = highlights["highlights"][:max_clips]
    else:
        segments = _segment_by_duration(video_path, start_time, duration, max_clips)

    clips = []
    for i, seg in enumerate(segments):
        clip_start = seg["start"]
        clip_duration = seg["end"] - seg["start"]

        clip_start = max(0, clip_start)
        if clip_start + clip_duration > video_duration:
            clip_duration = video_duration - clip_start

        clip_path = str(out_dir / f"clip_{i:03d}.mp4")

        cmd = [
            settings.FFMPEG_PATH,
            "-ss", str(clip_start),
            "-i", str(video_path),
            "-t", str(clip_duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            "-y",
            clip_path,
        ]

        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0:
            clips.append({
                "start": round(clip_start, 2),
                "end": round(clip_start + clip_duration, 2),
                "score": seg.get("score", 0.0),
                "output_file": f"clip_{i:03d}.mp4",
            })

    return {
        "clips": clips,
        "total_clips": len(clips),
    }


def _segment_by_duration(
    video_path: str, start_time: float, duration: int, max_clips: int
) -> list[dict]:
    video_duration = get_video_duration(video_path)
    segments = []
    t = start_time

    while t < video_duration and len(segments) < max_clips:
        end = min(t + duration, video_duration)
        segments.append({"start": t, "end": end, "score": 1.0})
        t = end

    return segments
