import subprocess
import time
from pathlib import Path
from app.core.config import settings


def enhance_voice(video_path: str) -> dict:
    start_time = time.time()

    output_path = str(
        settings.OUTPUT_DIR / f"{Path(video_path).stem}_enhanced{Path(video_path).suffix}"
    )

    noise_level = settings.VOICE_ENHANCE_NOISE_LEVEL
    afn_strength = settings.VOICE_ENHANCE_STRENGTH

    cmd = [
        settings.FFMPEG_PATH,
        "-i", str(video_path),
        "-af",
        ",".join([
            "highpass=f=80",
            "lowpass=f=8000",
            f"afftdn=nf={int(noise_level * 100)}:nr={afn_strength}:nt=w",
            "loudnorm=I=-16:TP=-1.5:LRA=11",
            "acompressor=threshold=-20dB:ratio=4:attack=5:release=50",
            "deesser=s=medium",
            "equalizer=f=3000:t=q:w=1:g=2",
            "equalizer=f=200:t=q:w=1:g=-2",
        ]),
        "-c:v", "copy",
        "-y",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    elapsed = time.time() - start_time

    if result.returncode != 0:
        raise RuntimeError(f"Voice enhancement failed: {result.stderr}")

    return {
        "output_file": Path(output_path).name,
        "processing_time": round(elapsed, 2),
    }


def get_audio_filters() -> dict:
    return {
        "noise_reduction": "afftdn",
        "equalization": "highpass + lowpass + equalizer",
        "normalization": "loudnorm",
        "compression": "acompressor",
        "de-essing": "deesser",
    }
