"""2-agent: jonli vertikal video.

Kirish (mavzu) → dialog (ikkala qahramon ekranda, gapirayotgani qimirlaydi, gap pufakchasi)
→ yakun («Yodda tuting» + obuna). Ovoz bo'lmasa ham ishlaydi.
"""
import math
import re
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import card
import config

W, H, FPS = 1080, 1920, 15
INTRO_S, OUTRO_S, GAP_S, SILENT_S = 2.4, 4.0, 0.45, 4.5
CHAR_H = 900
CHAR_DIR = Path(__file__).resolve().parent / "assets" / "characters"

NAVY = card.NAVY
WHITE = (255, 255, 255)
FR_BLUE, UZ_GREEN, GOLD = card.FR_BLUE, card.UZ_GREEN, card.GOLD


# ---------- Qahramonlar ----------

def _load(name):
    p = CHAR_DIR / f"{name}.png"
    if not p.exists():
        return None
    im = Image.open(p).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * CHAR_H / im.height), CHAR_H), Image.LANCZOS)


def _dim(im):
    rgb = ImageEnhance.Brightness(im.convert("RGB")).enhance(0.72)
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


def _scaled(im, k):
    return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)


class Cast:
    """Qahramon rasmlari: har holat uchun [a, b] juftligi (og'iz/qo'l harakati)."""

    def __init__(self):
        sh = {}
        for pose in ("talk", "laugh", "surprised"):
            a, b = _load(f"shohista_{pose}"), _load(f"shohista_{pose}_b")
            if a:
                sh[pose] = [a, b or _scaled(a, 1.025)]
        cl = _load("claire_talk")
        self.ok = bool(sh) and cl is not None
        if not self.ok:
            return
        self.sh = sh
        self.cl = {"talk": [cl, _scaled(cl, 1.025)]}
        self.sh_idle = _dim(_scaled(sh["talk"][0], 0.93))
        self.cl_idle = _dim(_scaled(cl, 0.93))

    def frames(self, speaker, pose):
        if speaker == config.FRENCH_GIRL:
            return self.cl["talk"]
        return self.sh.get(pose) or self.sh["talk"]


def _pose(text):
    t = text.lower()
    if re.search(r"ha-ha|barakalla|zo'r|ajoyib|qiziq|kulgi", t):
        return "laugh"
    if re.search(r"voy|rostdan|hayron|diqqat|ehtiyot", t) or t.strip().endswith("?"):
        return "surprised"
    return "talk"


# ---------- Statik qatlamlar ----------

_PHOTO = {"bg": None, "pic": None, "credit": ""}


def _photo_bg():
    """Mavzu rasmi: xiralashtirilgan va qoraytirilgan to'liq ekran fon."""
    import photos
    bg = photos.cover(_PHOTO["pic"], W, H).filter(ImageFilter.GaussianBlur(16))
    shade = Image.new("RGB", (W, H), NAVY)
    img = Image.blend(bg, shade, 0.55)
    draw = ImageDraw.Draw(img)
    third = W // 3
    for i, c in enumerate((card.FR_BLUE, WHITE, card.FR_RED)):
        draw.rectangle([i * third, 0, (i + 1) * third, 14], fill=c)
    for i, c in enumerate((card.UZ_BLUE, WHITE, card.UZ_GREEN)):
        draw.rectangle([0, H - 42 + i * 14, W, H - 28 + i * 14], fill=c)
    return img


def _base(title):
    if _PHOTO["pic"] is not None:
        if _PHOTO["bg"] is None:
            _PHOTO["bg"] = _photo_bg()
        img = _PHOTO["bg"].copy()
        draw = ImageDraw.Draw(img)
    else:
        img, draw = card._background(W, H)
    draw.text((60, 50), config.RUBRIC.upper(), font=card._font(card.FONT_BOLD, 26), fill=GOLD)
    font = card._fit(draw, title, card.FONT_BOLD, 58, 40, W - 120, 2)
    card._text(draw, (60, 100), title, font, WHITE, W - 120, 1.2)
    tag = config.CHANNEL_TAG
    f = card._font(card.FONT_BOLD, 28)
    draw.text(((W - draw.textlength(tag, font=f)) / 2, H - 92), tag, font=f, fill=card.SOFT)
    if _PHOTO["credit"]:
        cf = card._font(card.FONT, 18)
        cr = _PHOTO["credit"][:100]
        draw.text(((W - draw.textlength(cr, font=cf)) / 2, H - 128), cr, font=cf, fill=(190, 200, 220))
    return img


def _bubble(img, line, side):
    """Gap pufakchasi: kim gapirsa, dumi o'sha tomonga qaraydi."""
    draw = ImageDraw.Draw(img)
    draw.ellipse([120, H - 210, W - 120, H - 150], fill=(16, 28, 64))  # sahna soyasi
    is_fr = line["speaker"] == config.FRENCH_GIRL
    color = FR_BLUE if is_fr else UZ_GREEN
    x0, x1, top = 50, W - 50, 300
    inner = x1 - x0 - 90
    main_font = card._fit(draw, line["text"], card.FONT_BOLD, 60, 36, inner, 6)
    main_lines = card._wrap(draw, line["text"], main_font, inner)
    sub = line.get("uz", "") if is_fr else ""
    sub_font = card._fit(draw, sub, card.FONT, 44, 30, inner, 3) if sub else None
    sub_lines = card._wrap(draw, sub, sub_font, inner) if sub else []
    h = 120 + len(main_lines) * int(main_font.size * 1.25)
    if sub_lines:
        h += 50 + len(sub_lines) * int(sub_font.size * 1.25)
    bottom = min(top + h, H - CHAR_H - 230)
    draw.rounded_rectangle([x0, top, x1, bottom], radius=40, fill=card.CREAM, outline=color, width=6)
    tx = 300 if side == "left" else W - 300
    draw.polygon([(tx - 40, bottom - 3), (tx + 40, bottom - 3), (tx, bottom + 60)], fill=card.CREAM)
    draw.line([(tx - 40, bottom), (tx, bottom + 60), (tx + 40, bottom)], fill=color, width=6)
    nf = card._font(card.FONT_BOLD, 40)
    name = line["speaker"]
    nw = draw.textlength(name, font=nf)
    draw.rounded_rectangle([x0 + 30, top - 34, x0 + 30 + nw + 50, top + 34], radius=34, fill=color)
    draw.text((x0 + 55, top - 25), name, font=nf, fill=WHITE)
    y = card._text(draw, (x0 + 45, top + 60), line["text"], main_font, NAVY, inner, 1.25, center=True)
    if sub_lines:
        draw.line([(x0 + 120, y + 18), (x1 - 120, y + 18)], fill=card.SOFT, width=4)
        card._text(draw, (x0 + 45, y + 42), sub, sub_font, (60, 70, 90), inner, 1.25, center=True)
    return img


PANEL = (60, 330, W - 60, 330 + 640)


def _intro(lesson):
    img = _base(lesson["title_uz"])
    d = ImageDraw.Draw(img)
    if _PHOTO["pic"] is not None:
        f1 = card._font(card.FONT_BOLD, 44)
        label = "Bugungi dars"
        d.text(((W - d.textlength(label, font=f1)) / 2, PANEL[3] + 60), label, font=f1, fill=GOLD)
        topic = lesson["topic"]
        f2 = card._fit(d, topic, card.FONT_BOLD, 92, 56, W - 160, 2)
        card._text(d, (80, PANEL[3] + 130), topic, f2, WHITE, W - 160, 1.15, center=True)
        return img
    f1 = card._font(card.FONT_BOLD, 44)
    label = "Bugungi dars"
    d.text(((W - d.textlength(label, font=f1)) / 2, 400), label, font=f1, fill=GOLD)
    topic = lesson["topic"]
    f2 = card._fit(d, topic, card.FONT_BOLD, 92, 56, W - 160, 2)
    card._text(d, (80, 480), topic, f2, WHITE, W - 160, 1.15, center=True)
    return img


def _outro(lesson):
    img = _base(lesson["title_uz"])
    d = ImageDraw.Draw(img)
    f = card._font(card.FONT_BOLD, 46)
    d.text((80, 300), "Yodda tuting:", font=f, fill=GOLD)
    y = 380
    for p in lesson["key_phrases"][:3]:
        d.rounded_rectangle([60, y, W - 60, y + 150], radius=28, fill=card.CREAM)
        ff = card._fit(d, p["fr"], card.FONT_BOLD, 46, 30, W - 180, 1)
        d.text((90, y + 18), p["fr"], font=ff, fill=NAVY)
        d.text((90, y + 80), f"[{p.get('pron', '')}]  {p.get('uz', '')}"[:60],
               font=card._font(card.FONT, 32), fill=(60, 70, 90))
        y += 170
    sub = "Obuna bo'ling!"
    fs = card._font(card.FONT_BOLD, 56)
    sw = d.textlength(sub, font=fs)
    d.rounded_rectangle([(W - sw) / 2 - 40, y + 20, (W + sw) / 2 + 40, y + 120], radius=50, fill=card.FR_RED)
    d.text(((W - sw) / 2, y + 35), sub, font=fs, fill=WHITE)
    lines = [f"Telegram: {config.CHANNEL_TAG}", f"Instagram: @{config.INSTAGRAM}"]
    fl = card._font(card.FONT_BOLD, 40)
    for i, s in enumerate(lines):
        d.text(((W - d.textlength(s, font=fl)) / 2, y + 160 + i * 64), s, font=fl, fill=WHITE)
    return img


# ---------- Ovoz ----------

def _to_wav(src, dst):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ar", "44100", "-ac", "1",
                    "-sample_fmt", "s16", str(dst)], check=True)
    with wave.open(str(dst)) as w:
        return w.getnframes() / w.getframerate()


def _silence(dst, seconds):
    with wave.open(str(dst), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(44100)
        w.writeframes(b"\x00\x00" * int(44100 * seconds))
    return seconds


# ---------- Yig'ish ----------

def make(lesson, workdir, clips=None, photo=None, credit=""):
    import photos as photos_mod
    workdir = Path(workdir).resolve()
    _PHOTO.update(bg=None, pic=Image.open(photo).convert("RGB") if photo else None, credit=credit or "")
    cast = Cast()
    lines = lesson["dialogue"]

    # 1) Ovoz va vaqtlar
    parts, durs = [], []
    parts.append(workdir / "a_intro.wav")
    _silence(parts[-1], INTRO_S + (0.6 if photo else 0))
    for i, line in enumerate(lines):
        wav = workdir / f"a_{i:02d}.wav"
        if clips:
            d = _to_wav(clips[i], wav)
        else:
            d = _silence(wav, SILENT_S)
        parts.append(wav); durs.append(d)
        gap = workdir / f"a_{i:02d}_gap.wav"; _silence(gap, GAP_S); parts.append(gap)
    parts.append(workdir / "a_outro.wav"); _silence(parts[-1], OUTRO_S)
    listing = workdir / "audio.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    audio = workdir / "audio.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c", "copy", str(audio)], check=True, cwd=workdir)

    # 2) Kadrlar — to'g'ridan-to'g'ri ffmpeg'ga uzatiladi
    out = workdir / "video.mp4"
    enc = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-i", str(audio), "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest",
        "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)

    def emit(frame, n=1):
        data = frame.convert("RGB").tobytes()
        for _ in range(n):
            enc.stdin.write(data)

    def kenburns(frame, t):
        x0, y0, x1, y1 = PANEL
        pw, ph = x1 - x0, y1 - y0
        k = 1.0 + 0.10 * min(1.0, t / INTRO_S)
        src = photos_mod.cover(_PHOTO["pic"], int(pw * k), int(ph * k))
        ox, oy = (src.width - pw) // 2, (src.height - ph) // 2
        pic = src.crop((ox, oy, ox + pw, oy + ph)).convert("RGBA")
        mask = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw, ph], radius=36, fill=255)
        pic.putalpha(mask)
        frame.alpha_composite(pic, (x0, y0))

    def scene(static, speaker=None, pose="talk", seconds=1.0, fade=0.0, overlay=None, show_cast=True):
        n = max(1, int(round(seconds * FPS)))
        base = card._watermark(static, W, H).convert("RGBA")
        for k in range(n):
            t = k / FPS
            frame = base.copy()
            if overlay:
                overlay(frame, t)
            if cast.ok and show_cast:
                talking = speaker is not None
                for who, cx in ((config.FRENCH_GIRL, 290), (config.UZBEK_GIRL, W - 290)):
                    if talking and who == speaker:
                        pair = cast.frames(who, pose)
                        im = pair[(k // 4) % 2]
                        bob = int(10 * abs(math.sin(t * 5.5)))
                    else:
                        im = cast.cl_idle if who == config.FRENCH_GIRL else cast.sh_idle
                        if not talking:  # kirish/yakun: ikkalasi ham yorqin, sekin tebranadi
                            im = cast.frames(who, "talk")[0]
                        bob = int(4 * math.sin(t * 2 + (0 if who == config.FRENCH_GIRL else 1.5)))
                    frame.alpha_composite(im, (int(cx - im.width / 2), H - 150 - im.height - bob))
            if fade and t < fade:
                frame = Image.blend(base, frame, 0.35 + 0.65 * t / fade)
            emit(frame)

    if _PHOTO["pic"] is not None:
        scene(_intro(lesson), None, seconds=INTRO_S + 0.6, overlay=kenburns, show_cast=False)
    else:
        scene(_intro(lesson), None, seconds=INTRO_S)
    for line, d in zip(lines, durs):
        side = "left" if line["speaker"] == config.FRENCH_GIRL else "right"
        static = _bubble(_base(lesson["title_uz"]), line, side)
        scene(static, line["speaker"], _pose(line["text"]) if side == "right" else "talk",
              seconds=d + GAP_S)
    scene(_outro(lesson), None, seconds=OUTRO_S, show_cast=False)

    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError("Video yig'ishda ffmpeg xatosi")
    return out
