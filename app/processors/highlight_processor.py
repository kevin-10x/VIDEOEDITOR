import subprocess
import json
import os
from pathlib import Path
from app.core.config import settings
from app.utils.ffmpeg_helpers import get_video_duration


def detect_highlights(video_path: str) -> dict:
    duration = get_video_duration(video_path)
    audio_path = str(Path(video_path).with_suffix(".wav"))

    subprocess.run(
        [
            settings.FFMPEG_PATH, "-i", str(video_path),
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "-y", audio_path,
        ],
        capture_output=True, check=True,
    )

    audio_data = _load_audio_data(audio_path)
    volume_segments = _compute_volume_segments(audio_data, segment_duration=0.5)
    raw_volumes = [vs["volume"] for vs in volume_segments]
    normalized_volumes = _normalize_to_zero_one(raw_volumes)
    for vs, nv in zip(volume_segments, normalized_volumes):
        vs["volume"] = nv

    motion_scores = _compute_motion_scores(video_path, sample_rate=2)

    highlights = _score_and_select_highlights(
        volume_segments, motion_scores, duration
    )

    os.remove(audio_path)
    return {
        "highlights": highlights,
        "total_duration": duration,
    }


def _load_audio_data(path: str) -> list[float]:
    import wave
    import struct

    with wave.open(path, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        samples = struct.unpack(f"<{len(frames) // 2}h", frames)

    return [abs(s) / 32768.0 for s in samples]


def _normalize_to_zero_one(values: list[float]) -> list[float]:
    if not values:
        return values
    max_val = max(values) if values else 1.0
    if max_val == 0:
        return values
    return [v / max_val for v in values]


def _compute_volume_segments(audio_data: list[float], segment_duration: float = 0.5) -> list[dict]:
    sample_rate = 16000
    segment_size = int(sample_rate * segment_duration)
    segments = []

    for i in range(0, len(audio_data), segment_size):
        chunk = audio_data[i : i + segment_size]
        if not chunk:
            break
        rms = (sum(s**2 for s in chunk) / len(chunk)) ** 0.5
        timestamp = i / sample_rate
        segments.append({"timestamp": timestamp, "volume": rms})

    return segments


def _compute_motion_scores(video_path: str, sample_rate: float = 2.0) -> list[dict]:
    duration = get_video_duration(video_path)
    scores = []
    prev_data = None
    t = 0.0

    tmp_dir = Path(settings.UPLOAD_DIR) / "_motion_tmp"
    tmp_dir.mkdir(exist_ok=True)

    while t < duration:
        frame_path = str(tmp_dir / f"frame_{int(t*1000)}.jpg")
        subprocess.run(
            [
                settings.FFMPEG_PATH, "-ss", str(t), "-i", str(video_path),
                "-vframes", "1", "-q:v", "5", "-y", frame_path,
            ],
            capture_output=True,
        )

        if os.path.exists(frame_path):
            with open(frame_path, "rb") as f:
                curr_data = f.read()

            if prev_data is not None:
                min_len = min(len(prev_data), len(curr_data))
                if min_len > 0:
                    total_diff = sum(abs(a - b) for a, b in zip(prev_data[:min_len], curr_data[:min_len]))
                    motion = total_diff / (min_len * 255.0)
                else:
                    motion = 0.0
                scores.append({"timestamp": t, "motion": min(motion, 1.0)})
            else:
                scores.append({"timestamp": t, "motion": 0.0})
            prev_data = curr_data
            os.remove(frame_path)

        t += 1.0 / sample_rate

    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return scores


def _score_and_select_highlights(
    volume_segments: list[dict],
    motion_scores: list[dict],
    total_duration: float,
) -> list[dict]:
    combined = {}
    for vs in volume_segments:
        t = round(vs["timestamp"], 1)
        combined[t] = {"volume": vs["volume"], "motion": 0.0, "score": 0.0}

    for ms in motion_scores:
        t = round(ms["timestamp"], 1)
        if t in combined:
            combined[t]["motion"] = ms["motion"]
        else:
            combined[t] = {"volume": 0.0, "motion": ms["motion"], "score": 0.0}

    for t, data in combined.items():
        data["score"] = 0.6 * data["volume"] + 0.4 * data["motion"]

    if not combined:
        return []

    sorted_times = sorted(combined.keys())
    highlighted_regions = []
    current_region = None

    for t in sorted_times:
        score = combined[t]["score"]
        if score >= settings.HIGHLIGHT_THRESHOLD:
            if current_region is None:
                current_region = {"start": t, "end": t, "max_score": score}
            else:
                if t - current_region["end"] <= 2.0:
                    current_region["end"] = t
                    current_region["max_score"] = max(current_region["max_score"], score)
                else:
                    _finalize_region(current_region, highlighted_regions)
                    current_region = {"start": t, "end": t, "max_score": score}
        else:
            if current_region is not None:
                _finalize_region(current_region, highlighted_regions)
                current_region = None

    if current_region is not None:
        _finalize_region(current_region, highlighted_regions)

    highlighted_regions.sort(key=lambda r: r["score"], reverse=True)

    results = []
    for region in highlighted_regions[:10]:
        results.append({
            "start": round(region["start"], 2),
            "end": round(region["end"], 2),
            "score": round(region["score"], 3),
            "label": _score_label(region["score"]),
        })

    return results


def _finalize_region(region: dict, regions: list):
    region["end"] += 0.5
    dur = region["end"] - region["start"]
    if dur < settings.HIGHLIGHT_MIN_DURATION:
        region["end"] = region["start"] + settings.HIGHLIGHT_MIN_DURATION
    if dur > settings.HIGHLIGHT_MAX_DURATION:
        region["end"] = region["start"] + settings.HIGHLIGHT_MAX_DURATION
    regions.append(region)


def _score_label(score: float) -> str:
    if score >= 0.8:
        return "high_energy"
    elif score >= 0.6:
        return "energetic"
    elif score >= 0.4:
        return "moderate"
    return "calm"
