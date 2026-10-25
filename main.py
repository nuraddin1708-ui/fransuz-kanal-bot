"""Bosh boshqaruvchi. Darslar lessons.json faylidan olinadi (Gemini kerak emas).

python main.py                    # vaqtga qarab slotni o'zi tanlaydi (GitHub jadvali)
SLOT=noon python main.py          # aniq slot: morning / noon / evening
SLOT=noon TEST=1 python main.py   # sinov: faqat adminga yuboradi, kanalga emas
"""
import datetime
import json
import os
import sys
import tempfile
import traceback
from pathlib import Path

import card
import config
import photos
import publisher
import video
import voice

ROOT = Path(__file__).parent
LESSONS = ROOT / "lessons.json"
HISTORY = ROOT / "data" / "history.json"


def load_lessons():
    return json.loads(LESSONS.read_text(encoding="utf-8"))


def load_history():
    if not HISTORY.exists():
        HISTORY.parent.mkdir(exist_ok=True)
        HISTORY.write_text("[]", encoding="utf-8")
    return json.loads(HISTORY.read_text(encoding="utf-8"))


def save_history(entry):
    hist = load_history()
    hist.append(entry)
    HISTORY.write_text(json.dumps(hist, ensure_ascii=False, indent=1), encoding="utf-8")


def unused_lessons(skip=()):
    used = {h.get("id") for h in load_history()} | set(skip)
    return [l for l in load_lessons() if l["id"] not in used]


def pick_slot(now):
    manual = os.environ.get("SLOT", "").strip()
    if manual:
        return manual
    if now.hour < 11:
        return "morning"
    if now.hour < 16:
        return "noon"
    return "evening"


def _log(text):
    """Oxirgi ishga tushirish haqida qisqa hisobot (GitHub'ga saqlanadi)."""
    try:
        path = ROOT / "data" / "last_run.txt"
        path.parent.mkdir(exist_ok=True)
        stamp = datetime.datetime.now(config.TZ).strftime("%Y-%m-%d %H:%M")
        path.write_text(f"{stamp} — {text}\n", encoding="utf-8")
    except Exception:
        pass


def build(kind, lesson, notes, workdir):
    """Darsdan tayyor post yasaydi. Ovoz ishlamasa ham post tayyor bo'ladi."""
    workdir = Path(workdir)
    notes = list(notes)
    files, clips = {}, None
    if kind in ("text_audio", "video"):
        try:
            clips, full = voice.speak_dialogue(lesson, workdir)
            if kind == "text_audio":
                files["audio"] = full
        except Exception as exc:
            notes.append(f"Ovoz qo'shilmadi: {str(exc)[:200]}")
        _log(f"{kind}: ovoz — {'OK' if clips else 'XATO: ' + notes[-1]}")
    photo, credit = None, ""
    if kind in ("photo", "video"):
        found = photos.find(lesson, workdir)
        if found:
            photo, credit = found
        else:
            notes.append("Mavzuga mos rasm topilmadi — oddiy dizayn ishlatildi.")
    if kind == "photo":
        files["photo"] = card.photo_card(lesson, workdir / "post.png", photo=photo, credit=credit)
    elif kind == "video":
        files["video"] = video.make(lesson, workdir, clips=clips, photo=photo, credit=credit)
    return {"kind": kind, "lesson": lesson, "issues": notes, "credit": credit,
            "files": {k: str(v) for k, v in files.items()}}


def revise_with_ai(lesson, instruction):
    import gemini
    prompt = (
        "You edit a French lesson for Uzbek speakers. Keep the same JSON structure and keys. "
        "French must be correct; Uzbek in Latin script. Apply the admin's request (in Uzbek): "
        f"«{instruction}». Return ONLY the full updated JSON.\n\n"
        + json.dumps(lesson, ensure_ascii=False)
    )
    new = gemini.ask(prompt, want_json=True)
    for key in ("title_uz", "dialogue", "key_phrases", "tip_uz"):
        if not new.get(key):
            raise ValueError(f"'{key}' yo'q")
    new["id"] = lesson["id"]
    return new


def main():
    now = datetime.datetime.now(config.TZ)
    slot = pick_slot(now)
    hour, kind = config.SLOTS[slot]
    test = os.environ.get("TEST", "").strip().lower() in ("1", "true", "yes")

    if os.environ.get("SLOT"):  # qo'lda ishga tushirilgan — 12 daqiqadan keyin chiqadi
        publish_at = now + datetime.timedelta(minutes=config.PREVIEW_MINUTES + 2)
    else:
        publish_at = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if publish_at < now - datetime.timedelta(hours=2):
            sys.exit("Bu slot vaqti allaqachon o'tib ketgan.")

    # Kuniga bitta mavzu: ertalab yangi dars olinadi, 14:00 va 18:00 da o'sha dars
    # boshqa formatda (kartochka, video) takrorlanadi — o'rganish mustahkam bo'ladi.
    today = f"{now:%Y-%m-%d}"
    todays = [h for h in load_history()
              if h.get("date") == today and h.get("id") and not h.get("skipped")]
    by_id = {l["id"]: l for l in load_lessons()}
    pool = unused_lessons()
    if todays and todays[-1]["id"] in by_id:
        lesson = by_id[todays[-1]["id"]]
    elif pool:
        lesson = pool[0]
    else:
        raise RuntimeError("Darslar tugadi! lessons.json fayliga yangi darslar qo'shing.")
    notes = []
    if len(pool) <= config.LOW_STOCK_WARNING:
        notes.append(f"Faqat {len(pool)} ta dars qoldi — yangi darslar qo'shish vaqti keldi.")

    print(f"[{slot}] Dars #{lesson['id']}: {lesson['topic']} ({kind})")
    pkg = build(kind, lesson, notes, tempfile.mkdtemp(prefix=f"{slot}_"))

    def rebuild(old_lesson, instruction):
        new_dir = tempfile.mkdtemp(prefix=f"{slot}_edit_")
        try:
            new_lesson = revise_with_ai(old_lesson, instruction)
            return build(kind, new_lesson, [], new_dir)
        except Exception:
            # AI ishlamasa — shu dars o'rniga keyingi darsni chiqaramiz
            rest = unused_lessons(skip=[old_lesson["id"]])
            if not rest:
                raise
            if not test:
                save_history({"date": f"{now:%Y-%m-%d}", "slot": slot, "id": old_lesson["id"],
                              "topic": old_lesson["topic"], "skipped": True})
            publisher._notify(
                f"ℹ️ Tahrirni avtomatik bajarib bo'lmadi. Bu dars o'rniga keyingisi chiqadi: "
                f"«{publisher.e(rest[0]['title_uz'])}».")
            return build(kind, rest[0], [], new_dir)

    final = publisher.run(pkg, publish_at, rebuild, dry_run=test)

    if not test:
        save_history({"date": f"{now:%Y-%m-%d}", "slot": slot, "id": final["lesson"]["id"],
                      "topic": final["lesson"]["topic"]})
    print("Tayyor ✅")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        traceback.print_exc()
        publisher.report_error(f"{type(exc).__name__}: {exc}")
        sys.exit(1)
