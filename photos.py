"""Mavzuga mos rasm: faqat CC0 va jamoat mulki (public domain) — manba yozish shart emas.

Manbalar: Openverse (Flickr, Wikimedia va boshqalar) → Wikimedia Commons. Kalit kerak emas.
Ishlatilgan rasmlar data/used_images.json da saqlanadi — takrorlanmaydi.
"""
import html
import json
import random
import re
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent
USED = ROOT / "data" / "used_images.json"
UA = {"User-Agent": "FransuzKanalBot/1.0 (https://github.com/nuraddin1708-ui/fransuz-kanal-bot)"}
MIN_W = 900


def _used():
    try:
        return set(json.loads(USED.read_text(encoding="utf-8")))
    except Exception:
        return set()


def _mark(url):
    used = _used()
    used.add(url)
    USED.parent.mkdir(exist_ok=True)
    USED.write_text(json.dumps(sorted(used), ensure_ascii=False, indent=0), encoding="utf-8")


def _clean(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def _openverse(query):
    r = requests.get("https://api.openverse.org/v1/images/", headers=UA, timeout=25, params={
        "q": query, "license": "cc0,pdm", "page_size": 20, "mature": "false"})
    r.raise_for_status()
    out = []
    for it in r.json().get("results", []):
        if (it.get("width") or 0) < MIN_W:
            continue
        lic = f"{(it.get('license') or '').upper()} {it.get('license_version') or ''}".strip()
        lic = {"PDM 1.0": "Public Domain", "CC0 1.0": "CC0"}.get(lic, "CC " + lic if lic else "")
        out.append({"url": it["url"], "author": _clean(it.get("creator")) or "noma'lum",
                    "license": lic, "source": it.get("source") or "Openverse"})
    return out


def _commons(query):
    r = requests.get("https://commons.wikimedia.org/w/api.php", headers=UA, timeout=25, params={
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
        "gsrsearch": f"{query} filetype:bitmap", "gsrlimit": 20, "prop": "imageinfo",
        "iiprop": "url|extmetadata|size", "iiurlwidth": 1600})
    r.raise_for_status()
    out = []
    for page in (r.json().get("query", {}).get("pages") or {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        lic = _clean((meta.get("LicenseShortName") or {}).get("value"))
        ok = lic.lower().startswith(("cc0", "public domain", "pd"))
        if not ok or (info.get("width") or 0) < MIN_W:
            continue
        out.append({"url": info.get("thumburl") or info.get("url"),
                    "author": _clean((meta.get("Artist") or {}).get("value"))[:60] or "noma'lum",
                    "license": lic, "source": "Wikimedia Commons"})
    return out


def find(lesson, workdir):
    """(rasm_yo'li, muallif_yozuvi) yoki None qaytaradi. Hech qachon xato tashlamaydi."""
    query = lesson.get("image_query") or lesson.get("topic", "")
    used = _used()
    for source in (_openverse, _commons):
        try:
            items = [i for i in source(query) if i["url"] not in used]
        except Exception as exc:
            print(f"Rasm qidirish ({source.__name__}) ishlamadi: {exc}")
            continue
        random.shuffle(items)
        for it in items[:6]:
            try:
                r = requests.get(it["url"], headers=UA, timeout=30)
                r.raise_for_status()
                im = Image.open(BytesIO(r.content)).convert("RGB")
                if im.width < MIN_W * 0.8:
                    continue
                im.thumbnail((1920, 1920))
                path = Path(workdir) / "topic_photo.jpg"
                im.save(path, quality=90)
                _mark(it["url"])
                # CC0 / jamoat mulki: manba ko'rsatish shart emas
                return str(path), ""
            except Exception as exc:
                print(f"Rasm yuklanmadi: {exc}")
    return None


def cover(im, w, h):
    """Rasmni w×h ga to'liq to'ldiradi (ortiqchasini qirqadi)."""
    k = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * k + 0.5), int(im.height * k + 0.5)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))
