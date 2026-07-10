import subprocess
import json
from pathlib import Path
from app.core.config import settings


def get_video_duration(video_path: str) -> float:
    cmd = [
        settings.FFPROBE_PATH,
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def get_video_info(video_path: str) -> dict:
    cmd = [
        settings.FFPROBE_PATH,
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)


def extract_audio(video_path: str, output_path: str, fmt: str = "wav") -> str:
    output = Path(output_path).with_suffix(f".{fmt}")
    cmd = [
        settings.FFMPEG_PATH,
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le" if fmt == "wav" else "libmp3lame",
        "-ar", "16000",
        "-ac", "1",
        "-y",
        str(output),
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return str(output)


def extract_frame(video_path: str, timestamp: float, output_path: str) -> str:
    cmd = [
        settings.FFMPEG_PATH,
        "-ss", str(timestamp),
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",
        "-y",
        str(output_path),
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path


def run_ffmpeg(args: list[str]) -> subprocess.CompletedProcess:
    cmd = [settings.FFMPEG_PATH] + args
    return subprocess.run(cmd, capture_output=True, text=True)


def check_ffmpeg() -> bool:
    try:
        result = subprocess.run(
            [settings.FFMPEG_PATH, "-version"],
            capture_output=True, text=True, timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def check_ffprobe() -> bool:
    try:
        result = subprocess.run(
            [settings.FFPROBE_PATH, "-version"],
            capture_output=True, text=True, timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False
