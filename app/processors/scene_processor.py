import subprocess
import os
import json
from pathlib import Path
from app.core.config import settings
from app.utils.ffmpeg_helpers import get_video_duration


def detect_scene_transitions(video_path: str) -> dict:
    duration = get_video_duration(video_path)
    transitions = []

    tmp_dir = Path(settings.UPLOAD_DIR) / "_scene_tmp"
    tmp_dir.mkdir(exist_ok=True)

    fps = 2.0
    subprocess.run(
        [
            settings.FFMPEG_PATH, "-i", str(video_path),
            "-vf", f"fps={fps}", "-q:v", "3", "-y",
            str(tmp_dir / "frame_%06d.jpg"),
        ],
        capture_output=True, check=True,
    )

    frames = sorted(tmp_dir.glob("frame_*.jpg"))

    if len(frames) < 2:
        _cleanup(tmp_dir)
        return {"transitions": [], "total_scenes": 1}

    prev_data = None
    for i, frame_path in enumerate(frames):
        with open(frame_path, "rb") as f:
            curr_data = f.read()

        timestamp = i / fps

        if prev_data is not None:
            diff_score = _compute_frame_diff(prev_data, curr_data)

            if diff_score > settings.SCENE_CHANGE_THRESHOLD:
                prev_frame_name = f"before_{timestamp:.1f}.jpg"
                curr_frame_name = f"after_{timestamp:.1f}.jpg"

                prev_out = str(tmp_dir / prev_frame_name)
                curr_out = str(tmp_dir / curr_frame_name)

                if not os.path.exists(prev_out) and i > 0:
                    prev_t = (i - 1) / fps
                    subprocess.run(
                        [
                            settings.FFMPEG_PATH, "-ss", str(prev_t), "-i", str(video_path),
                            "-vframes", "1", "-q:v", "2", "-y", prev_out,
                        ],
                        capture_output=True,
                    )
                subprocess.run(
                    [
                        settings.FFMPEG_PATH, "-ss", str(timestamp), "-i", str(video_path),
                        "-vframes", "1", "-q:v", "2", "-y", curr_out,
                    ],
                    capture_output=True,
                )

                transitions.append({
                    "timestamp": round(timestamp, 2),
                    "frame_before": prev_frame_name,
                    "frame_after": curr_frame_name,
                    "intensity": round(min(diff_score / 100.0, 1.0), 3),
                })

        prev_data = curr_data

    _cleanup(tmp_dir)

    filtered = _filter_transitions(transitions)

    return {
        "transitions": filtered,
        "total_scenes": len(filtered) + 1,
    }


def _compute_frame_diff(data1: bytes, data2: bytes) -> float:
    if len(data1) != len(data2):
        max_len = max(len(data1), len(data2))
        data1 = data1.ljust(max_len)
        data2 = data2.ljust(max_len)

    total = 0
    for b1, b2 in zip(data1, data2):
        total += abs(b1 - b2)

    return (total / len(data1)) / 255.0 * 100


def _filter_transitions(transitions: list[dict]) -> list[dict]:
    if not transitions:
        return []

    filtered = [transitions[0]]
    for t in transitions[1:]:
        if t["timestamp"] - filtered[-1]["timestamp"] >= settings.SCENE_MIN_GAP:
            filtered.append(t)

    return filtered


def _cleanup(tmp_dir: Path):
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)
