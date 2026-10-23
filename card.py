"""Rasm o'rniga dizaynli kartochkalar (Gemini'siz, bepul)."""
from PIL import Image, ImageDraw, ImageFont

import config

from pathlib import Path

_HERE = Path(__file__).resolve().parent / "assets" / "fonts"
_SYS = Path("/usr/share/fonts/truetype/dejavu")
FONT = str(_HERE / "DejaVuSans.ttf" if (_HERE / "DejaVuSans.ttf").exists() else _SYS / "DejaVuSans.ttf")
FONT_BOLD = str(_HERE / "DejaVuSans-Bold.ttf" if (_HERE / "DejaVuSans-Bold.ttf").exists()
                else _SYS / "DejaVuSans-Bold.ttf")

NAVY = (22, 38, 84)
NAVY_2 = (34, 64, 132)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
GOLD = (255, 205, 80)
SOFT = (200, 214, 240)
FR_BLUE, FR_RED = (0, 85, 164), (239, 65, 53)
UZ_BLUE, UZ_GREEN = (0, 153, 181), (30, 181, 58)


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def _wrap(draw, text, font, width):
    lines, line = [], ""
    for word in text.split():
        test = f"{line} {word}".strip()
        if draw.textlength(test, font=font) <= width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _text(draw, xy, text, font, fill, width, spacing=1.25, center=False):
    """Matnni o'rab yozadi va pastki y koordinatasini qaytaradi."""
    x, y = xy
    size = font.size if hasattr(font, "size") else 20
    for line in _wrap(draw, text, font, width):
        lx = x + (width - draw.textlength(line, font=font)) / 2 if center else x
        draw.text((lx, y), line, font=font, fill=fill)
        y += int(size * spacing)
    return y


def _fit(draw, text, path, start, minimum, width, max_lines):
    """Matn berilgan qatorlar soniga sig'guncha shriftni kichraytiradi."""
    size = start
    while size > minimum:
        font = _font(path, size)
        if len(_wrap(draw, text, font, width)) <= max_lines:
            return font
        size -= 4
    return _font(path, minimum)


def _background(w, h):
    img = Image.new("RGB", (w, h), NAVY)
    draw = ImageDraw.Draw(img)
    for y in range(h):  # yumshoq gradient
        t = y / h
        c = tuple(int(NAVY[i] * (1 - t) + NAVY_2[i] * t) for i in range(3))
        draw.line([(0, y), (w, y)], fill=c)
    # tepada Fransiya bayrog'i ranglari, pastda O'zbekiston bayrog'i ranglari
    third = w // 3
    for i, c in enumerate((FR_BLUE, WHITE, FR_RED)):
        draw.rectangle([i * third, 0, (i + 1) * third, 14], fill=c)
    for i, c in enumerate((UZ_BLUE, WHITE, UZ_GREEN)):
        draw.rectangle([0, h - 42 + i * 14, w, h - 28 + i * 14], fill=c)
    return img, draw


def _header(draw, w, title):
    draw.text((60, 50), config.RUBRIC.upper(), font=_font(FONT_BOLD, 26), fill=GOLD)
    font = _fit(draw, title, FONT_BOLD, 62, 40, w - 120, 3)
    return _text(draw, (60, 100), title, font, WHITE, w - 120, 1.2)


def _footer(draw, w, h):
    tag = config.CHANNEL_TAG
    f = _font(FONT_BOLD, 30)
    draw.text(((w - draw.textlength(tag, font=f)) / 2, h - 100), tag, font=f, fill=SOFT)


def photo_card(lesson, out_path):
    """14:00 dagi post uchun 1080x1350 kartochka: asosiy iboralar."""
    w, h = 1080, 1350
    img, draw = _background(w, h)
    y = _header(draw, w, lesson["title_uz"]) + 30

    phrases = lesson["key_phrases"][:4]
    box_h = (h - 200 - y - 30 * len(phrases)) // max(1, len(phrases))
    box_h = min(box_h, 250)
    for p in phrases:
        draw.rounded_rectangle([50, y, w - 50, y + box_h], radius=28, fill=CREAM)
        fy = _text(draw, (90, y + 26), p["fr"], _fit(draw, p["fr"], FONT_BOLD, 54, 34, w - 180, 2),
                   NAVY, w - 180, 1.15)
        fy = _text(draw, (90, fy + 4), f"[{p.get('pron', '')}]", _font(FONT, 34), FR_RED, w - 180)
        _text(draw, (90, fy + 4), p.get("uz", ""), _font(FONT, 34), (60, 70, 90), w - 180)
        y += box_h + 30
    _footer(draw, w, h)
    img.save(out_path)
    return out_path


def line_card(lesson, line, out_path):
    """Video uchun 1080x1920 kadr: bitta dialog qatori."""
    w, h = 1080, 1920
    img, draw = _background(w, h)
    _header(draw, w, lesson["title_uz"])

    is_fr = line["speaker"] == config.FRENCH_GIRL
    color = FR_BLUE if is_fr else UZ_GREEN
    name = line["speaker"]
    nf = _font(FONT_BOLD, 48)
    nw = draw.textlength(name, font=nf)
    top = 560
    draw.rounded_rectangle([60, top, 60 + nw + 60, top + 84], radius=42, fill=color)
    draw.text((90, top + 14), name, font=nf, fill=WHITE)

    box_top, box_bottom = top + 120, h - 220
    draw.rounded_rectangle([50, box_top, w - 50, box_bottom], radius=36, fill=CREAM)
    main_font = _fit(draw, line["text"], FONT_BOLD, 80, 44, w - 180, 7)
    sub_font = _fit(draw, line.get("uz", ""), FONT, 56, 36, w - 180, 4)
    main_h = len(_wrap(draw, line["text"], main_font, w - 180)) * int(main_font.size * 1.25)
    sub_h = 0
    if is_fr and line.get("uz"):
        sub_h = 90 + len(_wrap(draw, line["uz"], sub_font, w - 180)) * int(sub_font.size * 1.25)
    y0 = box_top + max(50, (box_bottom - box_top - main_h - sub_h) // 2)  # markazga
    y = _text(draw, (90, y0), line["text"], main_font, NAVY, w - 180, 1.25, center=True)
    if sub_h:
        draw.line([(140, y + 35), (w - 140, y + 35)], fill=SOFT, width=4)
        _text(draw, (90, y + 75), line["uz"], sub_font, (60, 70, 90), w - 180, 1.25, center=True)
    _footer(draw, w, h)
    img.save(out_path)
    return out_path
