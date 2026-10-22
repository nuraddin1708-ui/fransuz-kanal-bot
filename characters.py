"""Qahramonlar pozalari kutubxonasini yaratadi: assets/characters/<ism>_<poza>.png

Asos — siz tasdiqlagan stikerlar (claire_talk.png, shohista_talk.png). Gemini ularni namuna qilib,
config.POSES dagi har bir pozani chizadi (billing kerak). Bor pozalar qayta chizilmaydi.
Actions → Run workflow → slot: characters.

Pozalarni o'zingiz chizdirsangiz: assets/raw/<ism>_<poza>.png (yashil fonda) qilib yuklang —
bot ularni stikerga aylantiradi, Gemini'siz.
"""
import tempfile
from pathlib import Path

from PIL import Image

import artist
import config
import style

RAW = style.ROOT / "assets" / "raw"


def from_uploads():
    made = []
    for f in sorted(RAW.glob("*")) if RAW.exists() else []:
        if f.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        img = style.key_green(Image.open(f))
        out = style.CHARS / f"{f.stem.lower()}.png"
        style.outline(img.crop(img.getbbox()), width=2).save(out)
        made.append(out)
    return made


def generate():
    style.CHARS.mkdir(parents=True, exist_ok=True)
    made = from_uploads()
    tmp = Path(tempfile.mkdtemp(prefix="poses_"))
    for name in (config.UZBEK_GIRL, config.FRENCH_GIRL):
        if not (style.CHARS / f"{name.lower()}_talk.png").exists():
            print(f"{name}: asosiy stiker (…_talk.png) yo'q — o'tkazib yuborildi")
            continue
        for tag, action in config.POSES.items():
            out = style.CHARS / f"{name.lower()}_{tag}.png"
            if out.exists():
                continue
            try:
                artist.pose_sticker(name, action, tmp / f"{name}_{tag}.png")
                (tmp / f"{name}_{tag}.png").replace(out)
                made.append(out)
                print(f"Tayyor: {out.name}")
            except Exception as exc:
                print(f"{out.name} chizilmadi: {exc}")
    return made
