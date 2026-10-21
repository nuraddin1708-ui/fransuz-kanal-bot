"""2-agent: o'zimizning qisqa vertikal video — rasm + ovoz + fransuzcha/o'zbekcha subtitr.

Boshqa odamlarning videolari ishlatilmaydi (mualliflik huquqi), hamma narsa o'zimizniki.
"""
import subprocess
import textwrap
from pathlib import Path

import config
import artist, voice

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _subtitle(line):
    main = textwrap.fill(line["text"], 34)
    sub = textwrap.fill(line.get("uz", ""), 38) if line["lang"] == "fr" and line.get("uz") else ""
    return line["speaker"], main, sub


def _clip(image, audio, line, out_path, workdir):
    name, main, sub = _subtitle(line)
    (workdir / "name.txt").write_text(name, encoding="utf-8")
    (workdir / "main.txt").write_text(main, encoding="utf-8")
    (workdir / "sub.txt").write_text(sub or " ", encoding="utf-8")
    color = "0x2E6BD9" if line["speaker"] == config.FRENCH_GIRL else "0x1F9D6B"
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "drawbox=x=0:y=ih-640:w=iw:h=640:color=black@0.6:t=fill,"
        f"drawtext=fontfile={FONT_BOLD}:textfile={workdir/'name.txt'}:expansion=none:"
        f"fontsize=46:fontcolor=white:box=1:boxcolor={color}@0.95:boxborderw=14:x=60:y=h-600,"
        f"drawtext=fontfile={FONT_BOLD}:textfile={workdir/'main.txt'}:expansion=none:"
        "fontsize=52:fontcolor=white:line_spacing=14:x=(w-text_w)/2:y=h-500,"
        f"drawtext=fontfile={FONT}:textfile={workdir/'sub.txt'}:expansion=none:"
        "fontsize=42:fontcolor=0xFFD54A:line_spacing=12:x=(w-text_w)/2:y=h-250"
    )
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(image), "-i", str(audio),
        "-vf", vf, "-af", "apad=pad_dur=0.6", "-c:v", "libx264", "-preset", "veryfast",
        "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "25", "-c:a", "aac", "-ar", "44100",
        "-ac", "2", "-shortest", str(out_path),
    ], check=True)
    return out_path


def make(lesson, workdir, clips=None, images=None):
    workdir = Path(workdir).resolve()
    if images is None:
        images = [
            artist.draw(lesson, workdir / "v1.png", aspect="9:16"),
            artist.draw(lesson, workdir / "v2.png", aspect="9:16",
                        variant="Close-up view of the two girls, slightly different angle."),
        ]
    if clips is None:
        clips, _ = voice.speak_dialogue(lesson, workdir)
    parts = []
    for i, (line, audio) in enumerate(zip(lesson["dialogue"], clips)):
        img = images[i % len(images)]
        parts.append(_clip(img, audio, line, workdir / f"part_{i:02d}.mp4", workdir))
    listing = workdir / "parts.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    out = workdir / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(listing), "-c", "copy", "-movflags", "+faststart", str(out)],
                   check=True, cwd=workdir)
    return out
