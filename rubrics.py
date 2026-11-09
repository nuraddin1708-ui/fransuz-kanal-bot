"""Hafta rubrikalari, testlar, kun iborasi va seriya matni.

14:00 — hafta kuniga qarab:
  Du: Bilasizmi? (fakt)      Se: Test (3)        Chor: O'zbek vs Fransuz
  Pay: Test (3)              Ju: Talaffuz mashqi Sha: Katta test (10)
  Yak: Hafta takrorlash
09:00 — Kun iborasi (bugungi qismdan), 18:00 — Seriya (video).
"""
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw

import card
import config

ROOT = Path(__file__).resolve().parent
FACTS = ROOT / "data" / "facts.json"
FARQLAR = ROOT / "data" / "farqlar.json"

WEEKDAY_RUBRIC = {0: "fact", 1: "quiz", 2: "farq", 3: "quiz", 4: "talaffuz", 5: "bigquiz", 6: "takror"}
RUBRIC_NAMES = {"fact": "Bilasizmi?", "quiz": "Test", "farq": "O'zbek vs Fransuz",
                "talaffuz": "Talaffuz mashqi", "bigquiz": "Katta test", "takror": "Hafta takrorlash"}


def e(s):
    import html
    return html.escape(str(s), quote=False)


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


# ---------- Tarixdan foydalanish ----------

def seen_lessons(history, lessons):
    """Kanalda chiqqan darslar — chiqish tartibida, takrorsiz."""
    by_id = {l["id"]: l for l in lessons}
    order = []
    for h in history:
        i = h.get("id")
        if i in by_id and not h.get("skipped") and i not in order:
            order.append(i)
    return [by_id[i] for i in order]


def next_item(items, history, rubric, skip=()):
    used = {h.get("item") for h in history if h.get("rubric") == rubric} | set(skip)
    rest = [it for it in items if it["id"] not in used]
    return rest[0] if rest else items[(len(used)) % len(items)]  # tugasa — boshidan aylanadi


# ---------- Testlar ----------

def make_quiz(lessons_pool, all_lessons, n, seed):
    """O'tilgan darslar iboralaridan Telegram test-savollari tuzadi."""
    rnd = random.Random(seed)
    phrases = [p for l in lessons_pool for p in l["key_phrases"]]
    everything = [p for l in all_lessons for p in l["key_phrases"]]
    rnd.shuffle(phrases)
    polls, used = [], set()
    for p in phrases:
        if len(polls) >= n:
            break
        if p["fr"] in used:
            continue
        used.add(p["fr"])
        ask_meaning = len(polls) % 2 == 0
        key = "uz" if ask_meaning else "fr"
        right = p[key]
        others = sorted({q[key] for q in everything if q[key] != right and q["fr"] != p["fr"]})
        rnd.shuffle(others)
        # uzunligi va so'zlar soni o'xshash variantlar — to'g'ri javob ko'zga tashlanmasin
        others.sort(key=lambda o: abs(len(o) - len(right)) + 6 * abs(len(o.split()) - len(right.split())))
        near = others[:10]
        rnd.shuffle(near)
        opts = [right] + near[:3]
        rnd.shuffle(opts)
        if ask_meaning:
            question = f"«{p['fr']}» nima degani?"
        else:
            question = f"«{p['uz']}» fransuzcha qanday bo'ladi?"
        polls.append({
            "question": question[:290],
            "options": [o[:100] for o in opts],
            "correct": opts.index(right),
            "explanation": f"{p['fr']} [{p.get('pron', '')}] — {p['uz']}"[:195],
        })
    return polls


# ---------- Kartochkalar ----------

def _rubric_header(draw, w, label, title):
    lf = card._font(card.FONT_BOLD, 34)
    lw = draw.textlength(label.upper(), font=lf)
    draw.rounded_rectangle([50, 44, 50 + lw + 44, 100], radius=28, fill=card.FR_RED)
    draw.text((72, 52), label.upper(), font=lf, fill=card.WHITE)
    font = card._fit(draw, title, card.FONT_BOLD, 60, 40, w - 120, 3)
    return card._text(draw, (56, 130), title, font, card.WHITE, w - 112, 1.2)


def _word_box(draw, w, y, word):
    draw.rounded_rectangle([50, y, w - 50, y + 170], radius=28, fill=card.GOLD)
    f1 = card._fit(draw, word["fr"], card.FONT_BOLD, 52, 34, w - 180, 1)
    draw.text((90, y + 22), word["fr"], font=f1, fill=card.NAVY)
    draw.text((90, y + 100), f"[{word.get('pron', '')}]  —  {word.get('uz', '')}"[:60],
              font=card._font(card.FONT, 34), fill=(60, 50, 20))


def fact_card(fact, out_path, photo=None):
    w, h = 1080, 1350
    img, draw = card._background(w, h)
    y = _rubric_header(draw, w, "Bilasizmi?", fact["title"]) + 25
    if photo:
        import photos
        band = 360
        pic = photos.cover(Image.open(photo).convert("RGB"), w - 100, band)
        mask = Image.new("L", pic.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, pic.width, pic.height], radius=28, fill=255)
        img.paste(pic, (50, y), mask)
        y += band + 25
    box_bottom = h - 170 - 190
    draw.rounded_rectangle([50, y, w - 50, box_bottom], radius=28, fill=card.CREAM)
    tf = card._fit(draw, fact["text"], card.FONT, 44 if photo else 56, 30, w - 180, 7 if photo else 11)
    card._text(draw, (90, y + 30), fact["text"], tf, card.NAVY, w - 180, 1.3)
    _word_box(draw, w, box_bottom + 20, fact["word"])
    card._footer(draw, w, h)
    card._watermark(img, w, h).save(out_path)
    return out_path


def versus_card(item, out_path):
    w, h = 1080, 1350
    img, draw = card._background(w, h)
    y = _rubric_header(draw, w, "O'zbek vs Fransuz", item["theme"]) + 30
    side_h = 330
    for label, text, color in (("FRANSIYADA", item["fr"], card.FR_BLUE),
                               ("O'ZBEKISTONDA", item["uz"], card.UZ_GREEN)):
        draw.rounded_rectangle([50, y, w - 50, y + side_h], radius=28, fill=card.CREAM,
                               outline=color, width=8)
        lf = card._font(card.FONT_BOLD, 34)
        lw = draw.textlength(label, font=lf)
        draw.rounded_rectangle([80, y - 26, 80 + lw + 40, y + 28], radius=26, fill=color)
        draw.text((100, y - 20), label, font=lf, fill=card.WHITE)
        tf = card._fit(draw, text, card.FONT_BOLD, 46, 30, w - 180, 5)
        card._text(draw, (90, y + 55), text, tf, card.NAVY, w - 180, 1.3)
        y += side_h + 50
    _word_box(draw, w, y, item["phrase"])
    card._footer(draw, w, h)
    card._watermark(img, w, h).save(out_path)
    return out_path


def list_card(title, label, rows, out_path):
    """rows: [(fr, pron, uz)] — hafta takrorlash kartochkasi."""
    w, h = 1080, 1350
    img, draw = card._background(w, h)
    y = _rubric_header(draw, w, label, title) + 25
    rows = rows[:7]
    row_h = min(125, (h - 170 - y) // max(1, len(rows)) - 12)
    for i, (fr, pron, uz) in enumerate(rows, 1):
        draw.rounded_rectangle([50, y, w - 50, y + row_h], radius=22, fill=card.CREAM)
        nf = card._font(card.FONT_BOLD, 40)
        draw.text((78, y + row_h / 2 - 24), str(i), font=nf, fill=card.FR_RED)
        ff = card._fit(draw, fr, card.FONT_BOLD, 40, 26, w - 230, 1)
        draw.text((140, y + 14), fr, font=ff, fill=card.NAVY)
        draw.text((140, y + row_h - 46), f"[{pron}]  {uz}"[:58], font=card._font(card.FONT, 28),
                  fill=(60, 70, 90))
        y += row_h + 12
    card._footer(draw, w, h)
    card._watermark(img, w, h).save(out_path)
    return out_path


# ---------- Ovoz ----------

def phrases_audio(phrases, workdir, slow=True):
    """Har ibora: fransuzcha (sekin) ×2, keyin o'zbekcha ma'nosi."""
    import voice
    clips = []
    for i, p in enumerate(phrases):
        a = voice.speak_edge(p["fr"], config.FRENCH_GIRL, Path(workdir) / f"p{i}_a.mp3",
                             rate="-25%" if slow else "-8%")
        b = voice.speak_edge(p["fr"], config.FRENCH_GIRL, Path(workdir) / f"p{i}_b.mp3", rate="-8%")
        c = voice.speak_edge(p["uz"], config.UZBEK_GIRL, Path(workdir) / f"p{i}_c.mp3")
        clips += [a, b, c]
    out = Path(workdir) / "phrases.mp3"
    voice.concat(clips, out, pause=0.8)
    return str(out)


# ---------- Post paketlari ----------

def _footer():
    import publisher
    return publisher._footer()


def phrase_of_day(lesson, episode, workdir):
    p = lesson["key_phrases"][0]
    import growth
    text = (
        f"{growth.hook()}\n\n"
        f"☀️ <b>Kun iborasi</b>\n\n"
        f"🇫🇷 <b>{e(p['fr'])}</b>\n"
        f"🗣 [{e(p.get('pron', ''))}]\n"
        f"🇺🇿 {e(p['uz'])}\n\n"
        f"🎧 Audioni tinglang va baland ovozda 3 marta takrorlang!\n\n"
        f"📺 Bugun <b>18:00</b> da <b>Seriya #{episode}</b>: Shohista va Claire bu iborani "
        f"«{e(lesson['title_uz'])}» qismida ishlatadi — o'tkazib yubormang!"
        + _footer()
    )
    pkg = {"kind": "message", "lesson": lesson, "text": text, "files": {}, "issues": []}
    try:
        pkg["files"]["audio"] = phrases_audio([p], workdir)
        pkg["audio_title"] = f"Kun iborasi: {p['fr']}"
    except Exception as exc:
        pkg["issues"].append(f"Ovoz qo'shilmadi: {str(exc)[:150]}")
    return pkg


def serial_caption(lesson, episode, prev_lesson, next_lesson, limit=1024):
    import publisher
    parts = [f"📺 <b>Seriya #{episode}</b> · {e(lesson['title_uz'])}"]
    if prev_lesson:
        parts.append(f"⏮ Oldingi qismda: «{e(prev_lesson['title_uz'])}»")
    parts.append("")
    parts.append(publisher._phrases_html(lesson))
    if next_lesson:
        parts.append("")
        parts.append(f"⏭ <b>Davomi ertaga 18:00 da:</b> «{e(next_lesson['title_uz'])}»")
    import growth
    goal = growth.goal_line()
    if goal:
        parts += ["", goal]
    text = "\n".join(parts) + _footer()
    if len(text) > limit and goal:  # sig'masa — maqsad qatorisiz
        text = "\n".join(parts[:-2]) + _footer()
    return text[:limit]


def build_noon(rubric, history, lessons, workdir, now, skip=()):
    """14:00 rubrikasi uchun paket. Natija: (pkg, tarix_yozuvi)."""
    import photos
    workdir = Path(workdir)
    seen = seen_lessons(history, lessons)
    entry = {"rubric": rubric}
    if rubric in ("quiz", "bigquiz") and len(seen) < 2:
        rubric = "fact"  # hali dars kam — test o'rniga fakt
        entry = {"rubric": rubric}

    if rubric == "fact":
        item = next_item(_load(FACTS), history, "fact", skip)
        entry["item"] = item["id"]
        found = photos.find({"image_query": item.get("image_query"), "topic": item["title"]}, workdir)
        path = fact_card(item, workdir / "fact.png", photo=found[0] if found else None)
        cap = (f"💡 <b>Bilasizmi?</b> {e(item['title'])}\n\n{e(item['text'])}\n\n"
               f"🇫🇷 <b>{e(item['word']['fr'])}</b> [{e(item['word']['pron'])}] — {e(item['word']['uz'])}"
               + _footer())
        return {"kind": "photo", "lesson": None, "caption": cap[:1024], "files": {"photo": str(path)},
                "issues": [], "item": item["id"]}, entry

    if rubric == "farq":
        item = next_item(_load(FARQLAR), history, "farq", skip)
        entry["item"] = item["id"]
        path = versus_card(item, workdir / "farq.png")
        p = item["phrase"]
        cap = (f"😄 <b>O'zbek vs Fransuz:</b> {e(item['theme'])}\n\n"
               f"🇫🇷 {e(item['fr'])}\n🇺🇿 {e(item['uz'])}\n\n"
               f"📌 <b>{e(p['fr'])}</b> [{e(p['pron'])}] — {e(p['uz'])}\n\n"
               f"Sizningcha, yana qanday farqlar bor? 🤔" + _footer())
        return {"kind": "photo", "lesson": None, "caption": cap[:1024], "files": {"photo": str(path)},
                "issues": [], "item": item["id"]}, entry

    if rubric in ("quiz", "bigquiz"):
        n = 10 if rubric == "bigquiz" else 3
        pool = seen[-7:] if rubric == "bigquiz" else seen[-4:]
        polls = make_quiz(pool, lessons, n, seed=f"{now:%Y-%m-%d}-{len(skip)}")
        title = "🏆 <b>Katta test!</b> 10 tadan 10 tasini topa olasizmi?" if rubric == "bigquiz" else \
                "🧠 <b>Test vaqti!</b> 3 tadan 3 tasini topa olasizmi?"
        intro = (f"{title}\n\nJavobni belgilang — to'g'ri yoki noto'g'riligini darhol ko'rasiz. "
                 f"Natijangizni do'stingiz bilan solishtiring — testni unga ham yuboring! 😉" + _footer())
        entry["item"] = f"{now:%Y-%m-%d}"
        return {"kind": "polls", "lesson": None, "text": intro, "polls": polls, "files": {},
                "issues": []}, entry

    week = seen[-7:]
    rows = [(l["key_phrases"][0]["fr"], l["key_phrases"][0].get("pron", ""), l["key_phrases"][0]["uz"])
            for l in week]
    entry["item"] = f"{now:%Y-%m-%d}"

    if rubric == "talaffuz":
        phrases = [l["key_phrases"][0] for l in seen[-5:]]
        lines = "\n".join(f"{i}. <b>{e(p['fr'])}</b> [{e(p.get('pron', ''))}] — {e(p['uz'])}"
                          for i, p in enumerate(phrases, 1))
        text = (f"🎧 <b>Talaffuz mashqi</b>\n\nHaftaning iboralari. Audioni yoqing: har ibora avval "
                f"sekin, keyin oddiy tezlikda aytiladi — ortidan takrorlang!\n\n{lines}" + _footer())
        pkg = {"kind": "message", "lesson": None, "text": text, "files": {}, "issues": [],
               "audio_title": "Talaffuz mashqi"}
        try:
            pkg["files"]["audio"] = phrases_audio(phrases, workdir)
        except Exception as exc:
            pkg["issues"].append(f"Ovoz qo'shilmadi: {str(exc)[:150]}")
        return pkg, entry

    # takror (yakshanba)
    path = list_card("Shu hafta o'rgangan iboralarimiz", "Hafta takrorlash", rows, workdir / "takror.png")
    lines = "\n".join(f"{i}. <b>{e(fr)}</b> [{e(pr)}] — {e(uz)}" for i, (fr, pr, uz) in enumerate(rows, 1))
    cap = (f"📚 <b>Hafta takrorlash</b>\n\n{lines}\n\nQaysi biri eng foydali bo'ldi? "
           f"Ertaga yangi hafta — yangi qismlar! 🎬" + _footer())
    return {"kind": "photo", "lesson": None, "caption": cap[:1024], "files": {"photo": str(path)},
            "issues": []}, entry
