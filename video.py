"""2-agent: o'zimizning qisqa vertikal video (namunadagi uslubda).

Fon — issiq o'zbek xonadoni; pastda oq hoshiyali Claire va Shohista stikerlari, gapirayotgani
yengil tebranadi; tepada skotch-yorliqlar ko'rinishidagi fransuzcha matn va o'zbekcha tarjima;
oxirida qog'oz fonda «Yodda tuting» kartasi.
Boshqa odamlarning videolari ishlatilmaydi (mualliflik huquqi), hamma narsa o'zimizniki.
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

import artist
import config
import style
import voice

FPS = 25
OUTRO_SECONDS = 4.5


def _ffmpeg(*args, cwd=None):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True, cwd=cwd)


def _encode_args():
    return ["-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "128k"]


def _captions(line, title=None):
    """Bitta qator uchun shaffof qatlam: brend yorliqlari + matn yorliqlari."""
    layer = Image.new("RGBA", (style.W, style.H), (0, 0, 0, 0))
    style.brand(layer, "UZBEKCHA FRANSUZCHA", f"{config.UZBEK_GIRL} & {config.FRENCH_GIRL}")
    tapes = []
    if title:
        tapes.append(style.tape(title, style.ORANGE, size=60, max_w=940))
    if line["lang"] == "fr":
        tapes.append(style.tape(f"«{line['text']}»", style.WHITE, size=58, max_w=980, upper=False))
        if line.get("uz"):
            tapes.append(style.tape(line["uz"], style.YELLOW, size=52, max_w=960))
    else:
        tapes.append(style.tape(f"{config.UZBEK_GIRL} o'rgatadi", style.GREEN, size=36, max_w=700))
        size = 46 if len(line["text"]) < 140 else 40
        tapes.append(style.tape(line["text"], style.WHITE, size=size, max_w=1000, upper=False))
    style.stack(layer, tapes, top=190)
    return layer


def _outro(lesson, out_png):
    img = style.paper()
    d = ImageDraw.Draw(img)
    style.stack(img, [style.tape("Yodda tuting", style.GREEN, size=60, angle=-1.5)], top=170)
    x0, y0, x1 = 110, 360, style.W - 110
    phrases = lesson["key_phrases"][:4]
    y1 = y0 + 120 + 250 * len(phrases)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x0 + 6, y0 + 12, x1 + 6, y1 + 12), 48, fill=(0, 0, 0, 70))
    img.alpha_composite(shadow.filter(style.ImageFilter.GaussianBlur(14)))
    d.rounded_rectangle((x0, y0, x1, y1), 48, fill=style.NAVY + (255,))
    big, mid, small = style.font(64), style.font(46, bold=False), style.font(44, bold=False)
    y = y0 + 70
    for p in phrases:
        d.text((x0 + 60, y), p["fr"][:28], font=big, fill=style.YELLOW[0])
        d.text((x0 + 60, y + 88), f"[{p.get('pron', '')}]"[:36], font=mid, fill=(255, 255, 255))
        d.text((x0 + 60, y + 148), p.get("uz", "")[:36], font=small, fill=(170, 200, 255))
        y += 250
    style.stack(img, [style.tape("Obuna bo'ling!", style.YELLOW, size=64, angle=1.5),
                      style.tape(config.CHANNEL_TAG, style.BLACK, size=40, upper=False, angle=0)],
                top=y1 + 60)
    img.convert("RGB").save(out_png)
    return out_png


def _clip(bg, layer_png, audio, out_path, stickers, speaker_idx, dur):
    """bg ustida sekin harakat, stikerlar (gapirayotgani tebranadi) va yorliqlar."""
    inputs = ["-loop", "1", "-i", str(bg)]
    graph = [f"[0:v]scale=1188:2112,crop=1080:1920:x='54+44*sin(t*0.45)':y='96-40*sin(t*0.35)'[v0]"]
    last = "v0"
    for i, (png, x, y) in enumerate(stickers):
        inputs += ["-loop", "1", "-i", str(png)]
        amp = 12 if i == speaker_idx else 0
        graph.append(f"[{last}][{i + 1}:v]overlay=x={x}:y='{y}+{amp}*sin(2*PI*1.8*t)'[v{i + 1}]")
        last = f"v{i + 1}"
    n = len(stickers) + 1
    inputs += ["-loop", "1", "-i", str(layer_png), "-i", str(audio)]
    graph.append(f"[{n}:v]format=rgba,fade=in:st=0:d=0.3:alpha=1[cap]")
    graph.append(f"[{last}][cap]overlay=0:0,format=yuv420p[out]")
    _ffmpeg(*inputs, "-filter_complex", ";".join(graph), "-map", "[out]", "-map", f"{n + 1}:a",
            "-af", "apad", "-t", f"{dur:.2f}", *_encode_args(), str(out_path))
    return out_path


def _place_stickers(workdir):
    """Stikerlarni o'lchab, faylga saqlaydi: [(png, x, y), ...] — Claire chapda, Shohista o'ngda."""
    out = []
    for i, name in enumerate([config.FRENCH_GIRL, config.UZBEK_GIRL]):
        img = style.sticker(name)
        if img is None:
            return []
        img = style.fit(img, 560, 1020)
        x = 10 if i == 0 else style.W - img.width - 10
        y = style.H - img.height - 30
        path = workdir / f"st_{i}.png"
        img.save(path)
        out.append((path, x, y))
    return out


def make(lesson, workdir, clips=None, images=None):
    workdir = Path(workdir).resolve()
    stickers = _place_stickers(workdir)
    if images is None:
        if stickers:  # qahramonlar alohida — fon odamlarsiz
            images = [artist.background(lesson, workdir / "bg.png")]
        else:         # stikerlar hali yo'q — qahramonlar fon rasmining o'zida
            images = [artist.draw(lesson, workdir / "bg.png", aspect="9:16")]
    if clips is None:
        clips, _ = voice.speak_dialogue(lesson, workdir)

    parts = []
    for i, (line, audio) in enumerate(zip(lesson["dialogue"], clips)):
        layer = workdir / f"cap_{i:02d}.png"
        _captions(line, title=lesson["title_uz"] if i == 0 else None).save(layer)
        speaker_idx = 0 if line["speaker"] == config.FRENCH_GIRL else 1
        dur = voice.duration(audio) + 0.6
        parts.append(_clip(images[i % len(images)], layer, audio, workdir / f"part_{i:02d}.mp4",
                           stickers, speaker_idx, dur))

    outro_png = _outro(lesson, workdir / "outro.png")
    outro = workdir / "part_99.mp4"
    _ffmpeg("-loop", "1", "-i", str(outro_png), "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-vf", "scale=1080:1920,fade=in:st=0:d=0.4", "-t", str(OUTRO_SECONDS),
            *_encode_args(), str(outro))
    parts.append(outro)

    listing = workdir / "parts.txt"
    listing.write_text("".join(f"file '{Path(p).name}'\n" for p in parts), encoding="utf-8")
    out = workdir / "video.mp4"
    _ffmpeg("-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy",
            "-movflags", "+faststart", str(out), cwd=workdir)
    return out
