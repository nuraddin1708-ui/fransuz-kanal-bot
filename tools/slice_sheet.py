"""ChatGPT'dagi 4×2 poza jadvalini alohida shaffof stikerlarga kesadi.

python tools/slice_sheet.py jadval.png shohista talk,talk_b,laugh,laugh_b,surprised,surprised_b,listen,listen_b
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "assets" / "new_characters"


def key_green(rgb):
    """Faqat chetga tutashgan yashil fonni olib tashlaydi — kiyimdagi yashil naqshlar qoladi."""
    a = np.asarray(rgb.convert("RGB")).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = (g > 110) & (g > r + 40) & (g > b + 40)
    from scipy import ndimage
    labels, _ = ndimage.label(green)
    edge_ids = set(np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))) - {0}
    bg = np.isin(labels, list(edge_ids))          # faqat chetga tutashgan yashil — fon
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    rgb8 = a.astype(np.uint8).copy()
    # fon bilan chegaradagi yashil tusni yumshatish (despill) — faqat chetdagi piksellarda
    edge = np.asarray(Image.fromarray(alpha).filter(ImageFilter.MinFilter(5))) == 0
    edge &= ~bg
    gch = rgb8[..., 1]
    lim = np.maximum(rgb8[..., 0], rgb8[..., 2])
    rgb8[..., 1] = np.where(edge & (gch > lim), lim, gch)
    im = Image.fromarray(np.dstack([rgb8, alpha]), "RGBA")
    al = im.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    im.putalpha(al)
    return im


def main(sheet, who, names, cols=4, rows=2):
    src = Image.open(sheet).convert("RGB")
    cw, ch = src.width / cols, src.height / rows
    names = names.split(",")
    OUT.mkdir(parents=True, exist_ok=True)
    for i, name in enumerate(names):
        if not name:
            continue
        c, r = i % cols, i // cols
        pad = 6  # katak chiziqlarini tashlab ketish
        cell = src.crop((int(c * cw) + pad, int(r * ch) + pad, int((c + 1) * cw) - pad, int((r + 1) * ch) - pad))
        im = key_green(cell)
        box = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
        im = im.crop(box)
        path = OUT / f"{who}_{name}.png"
        im.save(path)
        print(path.name, im.size)


if __name__ == "__main__":
    main(*sys.argv[1:4])
