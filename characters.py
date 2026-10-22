"""Qahramon-stikerlarni bir marta yaratadi: assets/characters/<ism>_<n>.png

Actions → Run workflow → slot: characters. Natija botda sizga ko'rsatiladi va repoga saqlanadi.
Yoqmasa, qayta ishga tushiring (eskilari almashtiriladi). O'zingiz chizdirgan rasmlarni ham
assets/ papkasiga qo'yishingiz mumkin — ular namuna sifatida olinadi.
"""
import tempfile
from pathlib import Path

from PIL import Image

import artist
import config
import gemini
import style

POSES = [
    "standing, smiling and talking, one hand gesturing openly",
    "standing, explaining something cheerfully with the index finger raised",
]

LOOKS = {
    config.UZBEK_GIRL: (
        "a young Uzbek woman in a traditional Uzbek national dress made of bright khan-atlas ikat silk, "
        "embroidered doppi skullcap, long dark braids, warm kind smile"
    ),
    config.FRENCH_GIRL: (
        "a young French woman with light-brown wavy shoulder-length hair, Breton striped top, "
        "light beige jacket, red beret, friendly smile"
    ),
}


def _prompt(name, pose):
    return (
        f"{config.STYLE_EN} Full-body character sticker of {LOOKS[name]}, {pose}. "
        "Whole figure visible from head to shoes, facing the viewer, centered. "
        "Plain solid pure green (#00FF00) background, flat, no shadow on the background, "
        "nothing else in the picture. No text."
    )


def generate():
    style.CHARS.mkdir(parents=True, exist_ok=True)
    refs = artist._references()
    made = []
    tmp = Path(tempfile.mkdtemp(prefix="chars_"))
    for name in (config.UZBEK_GIRL, config.FRENCH_GIRL):
        for i, pose in enumerate(POSES):
            raw = tmp / f"{name}_{i}.png"
            prompt = _prompt(name, pose)
            if refs:
                prompt = "Keep the character looking exactly like in the reference images. " + prompt
            try:
                gemini.image(prompt, raw, aspect="9:16", references=refs)
            except Exception as exc:
                print(f"Gemini ishlamadi ({name}), Pollinations: {exc}")
                artist._pollinations(_prompt(name, pose), raw, "9:16")
            img = style.key_green(Image.open(raw))
            # Katta rasmda piksel-piksel ishlash sekin — avval kichraytiramiz
            img = style.fit(img, 900, 1600)
            out = style.CHARS / f"{name.lower()}_{i + 1}.png"
            style.outline(img).save(out)
            made.append(out)
            print(f"Tayyor: {out}")
    return made
