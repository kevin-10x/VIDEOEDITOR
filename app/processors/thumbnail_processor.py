import subprocess
import os
from pathlib import Path
from app.core.config import settings
from app.utils.ffmpeg_helpers import get_video_duration


def generate_thumbnails(video_path: str, count: int = None) -> dict:
    count = count or settings.THUMBNAIL_COUNT
    duration = get_video_duration(video_path)
    filename = Path(video_path).stem

    out_dir = settings.OUTPUT_DIR / "thumbnails" / filename
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamps = _get_timestamps(duration, count)
    thumbnails = []

    for i, ts in enumerate(timestamps):
        thumb_path = str(out_dir / f"thumb_{i:03d}.jpg")
        subprocess.run(
            [
                settings.FFMPEG_PATH,
                "-ss", str(ts),
                "-i", str(video_path),
                "-vframes", "1",
                "-vf", f"scale={settings.THUMBNAIL_WIDTH}:{settings.THUMBNAIL_HEIGHT}:force_original_aspect_ratio=decrease,pad={settings.THUMBNAIL_WIDTH}:{settings.THUMBNAIL_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
                "-q:v", "2",
                "-y",
                thumb_path,
            ],
            capture_output=True, check=True,
        )
        thumbnails.append(f"thumb_{i:03d}.jpg")

    return {
        "thumbnails": thumbnails,
        "total_count": len(thumbnails),
    }


def _get_timestamps(duration: float, count: int) -> list[float]:
    if count == 1:
        return [duration / 2]

    interval = duration / (count + 1)
    return [interval * (i + 1) for i in range(count)]
