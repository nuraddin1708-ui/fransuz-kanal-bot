"""Vertikal video: har bir dialog qatori — alohida kartochka + ovoz (bo'lsa)."""
import subprocess
from pathlib import Path

import card

SILENT_SECONDS = 4.5  # ovoz bo'lmasa, har kadr shuncha turadi


def _clip(image, audio, out_path):
    base = ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(image)]
    if audio:
        cmd = base + ["-i", str(audio), "-af", "apad=pad_dur=0.6", "-shortest"]
    else:
        cmd = base + ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", str(SILENT_SECONDS)]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            "-r", "25", "-c:a", "aac", "-ar", "44100", "-ac", "2", str(out_path)]
    subprocess.run(cmd, check=True)
    return out_path


def make(lesson, workdir, clips=None):
    workdir = Path(workdir).resolve()
    parts = []
    for i, line in enumerate(lesson["dialogue"]):
        img = card.line_card(lesson, line, workdir / f"frame_{i:02d}.png")
        audio = clips[i] if clips else None
        parts.append(_clip(img, audio, workdir / f"part_{i:02d}.mp4"))
    listing = workdir / "parts.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    out = workdir / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(listing), "-c", "copy", "-movflags", "+faststart", str(out)],
                   check=True, cwd=workdir)
    return out
