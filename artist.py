"""3-agent: post uchun rasm yaratadi.

Navbat: 1) Gemini (Nano Banana) → 2) Pollinations (bepul) → 3) o'zimiz chizgan karta (har doim ishlaydi).
"""
import textwrap
import time
import urllib.parse
from pathlib import Path

import requests

import config
import gemini

ASSETS = Path(__file__).resolve().parent / "assets"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SIZES = {"4:5": (1080, 1350), "9:16": (1080, 1920), "1:1": (1080, 1080)}


def _references():
    """assets/ papkasidagi qahramonlar rasmlari — qahramonlar har doim bir xil ko'rinsin."""
    if not ASSETS.exists():
        return []
    return sorted(p for p in ASSETS.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg"))[:3]


def _prompt(lesson, variant):
    return (
        "Warm, bright, high-quality digital illustration for an educational Telegram post. "
        f"Characters: {config.CHARACTERS_EN} "
        f"Scene: {lesson['image_scene']} {variant} "
        "The two young women are talking and smiling, friendly atmosphere. "
        "Modest, family-friendly clothing. No text, no letters, no logos, no watermarks."
    )


def draw(lesson, out_path, aspect="4:5", variant=""):
    prompt = _prompt(lesson, variant)
    refs = _references()
    try:
        p = ("Keep the characters looking exactly like in the reference images. " + prompt) if refs else prompt
        return gemini.image(p, out_path, aspect=aspect, references=refs)
    except Exception as exc:
        print(f"Gemini rasm chiza olmadi, bepul variantga o'tamiz: {exc}")
    try:
        return _pollinations(prompt, out_path, aspect)
    except Exception as exc:
        print(f"Pollinations ishlamadi, karta chizamiz: {exc}")
    return card(lesson, out_path, aspect)


def _pollinations(prompt, out_path, aspect):
    w, h = SIZES.get(aspect, (1080, 1350))
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt[:900])
           + f"?width={w}&height={h}&nologo=true&model=flux&seed={int(time.time()) % 100000}")
    for attempt in range(3):
        r = requests.get(url, timeout=180)
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
            Path(out_path).write_bytes(r.content)
            return out_path
        time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"Pollinations {r.status_code}: {r.text[:200]}")


def card(lesson, out_path, aspect="4:5"):
    """Internet kerak emas: gradient fon ustida mavzu va asosiy iboralar."""
    from PIL import Image, ImageDraw, ImageFont

    w, h = SIZES.get(aspect, (1080, 1350))
    img = Image.new("RGB", (w, h))
    top, bottom = (0, 85, 164), (239, 65, 53)  # fransuz bayrog'i ranglari
    px = img.load()
    for y in range(h):
        t = y / h
        c = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(w):
            px[x, y] = c
    d = ImageDraw.Draw(img)
    big, mid, small = (ImageFont.truetype(FONT_BOLD, 64), ImageFont.truetype(FONT_BOLD, 46),
                       ImageFont.truetype(FONT, 38))
    y = 90
    d.text((70, y), f"{config.FRENCH_GIRL} & {config.UZBEK_GIRL}", font=small, fill=(255, 230, 150))
    y += 80
    for line in textwrap.wrap(lesson["title_uz"], 26):
        d.text((70, y), line, font=big, fill="white")
        y += 80
    y += 40
    for p in lesson["key_phrases"][:4]:
        d.rounded_rectangle((50, y, w - 50, y + 210), radius=30, fill=(255, 255, 255))
        d.text((80, y + 25), p["fr"][:34], font=mid, fill=(0, 60, 130))
        d.text((80, y + 90), f"[{p.get('pron', '')}]"[:44], font=small, fill=(200, 40, 40))
        d.text((80, y + 145), p.get("uz", "")[:44], font=small, fill=(40, 40, 40))
        y += 240
    d.text((70, h - 90), config.CHANNEL_TAG, font=small, fill="white")
    img.save(out_path)
    return out_path
