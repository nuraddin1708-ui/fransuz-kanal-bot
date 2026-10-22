"""Bosh boshqaruvchi: 6 agentni ketma-ket ishga tushiradi.

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

import config
import artist, publisher, quality, researcher, video, voice

HISTORY = Path(__file__).parent / "data" / "history.json"


def load_history():
    if not HISTORY.exists():  # data/ papkasi yuklanmagan bo'lsa ham ishlaydi
        HISTORY.parent.mkdir(exist_ok=True)
        HISTORY.write_text("[]", encoding="utf-8")
    return json.loads(HISTORY.read_text(encoding="utf-8"))


def save_history(entry):
    hist = load_history()
    hist.append(entry)
    HISTORY.parent.mkdir(exist_ok=True)
    HISTORY.write_text(json.dumps(hist[-500:], ensure_ascii=False, indent=1), encoding="utf-8")


def pick_slot(now):
    manual = os.environ.get("SLOT", "").strip()
    if manual:
        return manual
    if now.hour < 11:
        return "morning"
    if now.hour < 16:
        return "noon"
    return "evening"


def build(kind, lesson, issues, workdir):
    """Dars matnidan tayyor post (fayllar bilan) yasaydi."""
    workdir = Path(workdir)
    files = {}
    if kind == "text_audio":
        _, files["audio"] = voice.speak_dialogue(lesson, workdir)            # 4-agent
    elif kind == "photo":
        files["photo"] = artist.draw(lesson, workdir / "post.png")           # 3-agent
    elif kind == "video":
        files["video"] = video.make(lesson, workdir)                          # 2-agent (+3, +4)
    return {"kind": kind, "lesson": lesson, "issues": issues, "files": {k: str(v) for k, v in files.items()}}


def main():
    now = datetime.datetime.now(config.TZ)
    slot = pick_slot(now)
    hour, kind = config.SLOTS[slot]
    test = os.environ.get("TEST", "").strip() in ("1", "true", "yes")

    if os.environ.get("SLOT"):  # qo'lda ishga tushirilgan — 12 daqiqadan keyin chiqadi
        publish_at = now + datetime.timedelta(minutes=config.PREVIEW_MINUTES + 2)
    else:
        publish_at = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if publish_at < now - datetime.timedelta(hours=2):
            sys.exit("Bu slot vaqti allaqachon o'tib ketgan.")

    workdir = Path(tempfile.mkdtemp(prefix=f"{slot}_"))
    used = [h["topic"] for h in load_history()]

    print(f"[{slot}] 1-agent: dars tayyorlanmoqda…")
    lesson = researcher.make_lesson(kind, used)
    print(f"[{slot}] 5-agent: sifat nazorati…")
    lesson, issues = quality.check(lesson)
    print(f"[{slot}] Media tayyorlanmoqda ({kind})…")
    pkg = build(kind, lesson, issues, workdir)

    def rebuild(old_lesson, instruction):
        new_lesson = researcher.revise(old_lesson, instruction)
        new_lesson, new_issues = quality.check(new_lesson, rounds=1)
        new_dir = Path(tempfile.mkdtemp(prefix=f"{slot}_edit_"))
        return build(kind, new_lesson, new_issues, new_dir)

    print(f"[{slot}] 6-agent: adminga ko'rsatish va chiqarish ({publish_at:%H:%M})…")
    final = publisher.run(pkg, publish_at, rebuild, dry_run=test)

    if not test:
        save_history({"date": f"{now:%Y-%m-%d}", "slot": slot, "topic": final["lesson"]["topic"]})
    print("Tayyor ✅")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        traceback.print_exc()
        HISTORY.parent.mkdir(exist_ok=True)
        (HISTORY.parent / "last_error.txt").write_text(
            f"{datetime.datetime.now(config.TZ):%Y-%m-%d %H:%M}\n{traceback.format_exc()}", encoding="utf-8")
        publisher.report_error(f"{type(exc).__name__}: {exc}")
        sys.exit(1)
