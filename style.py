"""Kanal uslubi: skotch-yorliqlar, oq hoshiyali stikerlar, ranglar.

Namuna: issiq to'q sariq o'zbek xonadoni foni, oq hoshiyali qahramon-stikerlar,
qiyshiq yopishtirilgan yorliqlar (oq/sariq/yashil/to'q sariq), ensiz qalin katta harflar.
"""
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
CHARS = ROOT / "assets" / "characters"

W, H = 1080, 1920

# Yorliq ranglari: (fon, matn)
WHITE = ((250, 248, 242), (20, 20, 20))
YELLOW = ((250, 204, 21), (20, 20, 20))
GREEN = ((22, 150, 72), (255, 255, 255))
ORANGE = ((226, 96, 38), (255, 255, 255))
BLACK = ((22, 22, 22), (250, 204, 21))
NAVY = (14, 32, 92)
PAPER = (233, 231, 226)

_FONTS = [
    ROOT / "assets" / "fonts" / "Oswald.ttf",
    Path("/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]
_REGULAR = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


def font(size, bold=True):
    if not bold:
        return ImageFont.truetype(str(_REGULAR), size)
    for f in _FONTS:
        if f.exists():
            fnt = ImageFont.truetype(str(f), size)
            try:
                fnt.set_variation_by_name("Bold")  # Oswald o'zgaruvchan shrift
            except Exception:
                pass
            return fnt
    return ImageFont.load_default(size)


def _wrap(text, fnt, max_w):
    # Fransuzcha « ? » « ! » oldidagi bo'sh joy qatorni uzmasin
    for mark in ("?", "!", ":", ";", "»"):
        text = text.replace(f" {mark}", f"\u00a0{mark}")
    text = text.replace("« ", "«\u00a0")
    words, lines, cur = [w for w in text.split(" ") if w], [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if fnt.getlength(test) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def tape(text, colors=WHITE, size=54, max_w=900, upper=True, angle=None, seed=None):
    """Bitta yorliq: yirtiq chetli rangli tasma ustida matn, biroz qiyshiq."""
    rnd = random.Random(seed if seed is not None else text)
    bg, fg = colors
    fnt = font(size)
    text = text.upper() if upper else text
    lines = _wrap(text, fnt, max_w - 60)
    asc, desc = fnt.getmetrics()
    lh = asc + desc + 6
    tw = int(max(fnt.getlength(l) for l in lines))
    pad_x, pad_y = 30, 14
    w, h = tw + 2 * pad_x, lh * len(lines) + 2 * pad_y
    img = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    # Yirtiq chetlar
    pts, x0, y0 = [], 20, 20
    for y in range(0, h + 1, 8):
        pts.append((x0 + rnd.randint(-4, 5), y0 + y))
    for y in range(h, -1, -8):
        pts.append((x0 + w + rnd.randint(-5, 4), y0 + y))
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).polygon([(x + 4, y + 6) for x, y in pts], fill=(0, 0, 0, 90))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(5)))
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill=bg + (255,))
    for i, line in enumerate(lines):
        lw = fnt.getlength(line)
        d.text((x0 + (w - lw) / 2, y0 + pad_y + i * lh), line, font=fnt, fill=fg)
    if angle is None:
        angle = rnd.uniform(-2.2, 2.2)
    return img.rotate(angle, resample=Image.BICUBIC, expand=True)


def stack(canvas, tapes, top, gap=10, center_x=None):
    """Yorliqlarni ustma-ust markazga joylashtiradi, oxirgi y ni qaytaradi."""
    cx = center_x or canvas.width // 2
    y = top
    for t in tapes:
        canvas.alpha_composite(t, (int(cx - t.width / 2), int(y)))
        y += t.height - 20 + gap
    return y


def brand(canvas, tag, subtitle):
    """Chap yuqoridagi kichik brend yorliqlari (namunadagi «RAIS BUVA / HAYOT SAHNASI» kabi)."""
    a = tape(tag, BLACK, size=30, angle=0)
    b = tape(subtitle, YELLOW, size=26, angle=0)
    canvas.alpha_composite(a, (30, 50))
    canvas.alpha_composite(b, (30, 50 + a.height - 22))


# ---------- Stikerlar ----------

def key_green(img):
    """Yashil (#00FF00) fonni shaffof qiladi va yashil sachrashni tozalaydi."""
    img = img.convert("RGBA")
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if g > 120 and g > r * 1.35 and g > b * 1.35:
                px[x, y] = (0, 0, 0, 0)
            elif g > max(r, b):  # chetdagi yashil tus
                px[x, y] = (r, max(r, b), b, a)
    return img


def outline(img, width=14):
    """Oq hoshiya va yumshoq soya — stiker ko'rinishi."""
    img = img.crop(img.getbbox())
    pad = width + 20
    base = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    base.paste(img, (pad, pad))
    alpha = base.getchannel("A").point(lambda v: 255 if v > 40 else 0)
    grown = alpha
    step = 5
    for _ in range(max(1, width // 2)):
        grown = grown.filter(ImageFilter.MaxFilter(step))
    grown = grown.filter(ImageFilter.GaussianBlur(1)).point(lambda v: 255 if v > 100 else 0)
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow.putalpha(grown.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.35)))
    white = Image.new("RGBA", base.size, (255, 255, 255, 255))
    white.putalpha(grown)
    out = Image.new("RGBA", base.size, (0, 0, 0, 0))
    out.alpha_composite(shadow, (4, 8))
    out.alpha_composite(white)
    out.alpha_composite(base)
    return out


_STICKERS = {}


def sticker_path(name, pose=0):
    """assets/characters/<ism>_<poza>.png. pose — nomi («laugh») yoki raqam. Yo'q bo'lsa — boshqa poza."""
    files = sorted(f for f in CHARS.glob(f"{name.lower()}_*.png") if not f.stem.endswith("_b")) if CHARS.exists() else []
    if not files:
        return None
    if isinstance(pose, str):
        exact = [f for f in files if f.stem == f"{name.lower()}_{pose}"]
        fallback = [f for f in files if f.stem.endswith("_talk")] or files
        return (exact or fallback)[0]
    return files[pose % len(files)]


def sticker(name, pose=0):
    path = sticker_path(name, pose)
    if path is None:
        return None
    if path not in _STICKERS:
        _STICKERS[path] = Image.open(path).convert("RGBA")
    return _STICKERS[path]


def fit(img, max_w, max_h):
    k = min(max_w / img.width, max_h / img.height)
    return img.resize((int(img.width * k), int(img.height * k)), Image.LANCZOS)


def cover(img, w=W, h=H):
    """Rasmni kadrga to'ldirib kesadi."""
    img = img.convert("RGBA")
    k = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * k) + 1, int(img.height * k) + 1), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def warm_fallback(w=W, h=H):
    """Fon rasmi yaratilmasa: issiq to'q sariq gradient."""
    img = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(img)
    top, bottom = (120, 62, 20), (214, 120, 44)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3)) + (255,))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((w * 0.2, -h * 0.15, w * 0.8, h * 0.3), fill=(255, 210, 120, 120))
    return Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(120)))


def paper(w=W, h=H):
    """Yakuniy kadr foni: och kulrang qog'oz."""
    img = Image.new("RGBA", (w, h), PAPER + (255,))
    noise = Image.effect_noise((w // 4, h // 4), 18).resize((w, h)).convert("L")
    tint = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    tint.putalpha(ImageChops.invert(noise).point(lambda v: int(v * 0.06)))
    return Image.alpha_composite(img, tint)
