"""6-agent: admin-bot orqali ogohlantiradi, tahrirlashni qabul qiladi va kanalga chiqaradi."""
import datetime
import html
import json
import time

import requests

import config


def _api(method, files=None, **params):
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/{method}"
    for attempt in range(4):
        if files:
            data = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in params.items()}
            handles = {k: open(v, "rb") for k, v in files.items()}
            try:
                r = requests.post(url, data=data, files=handles, timeout=300)
            finally:
                for h in handles.values():
                    h.close()
        else:
            r = requests.post(url, json=params, timeout=60)
        res = r.json()
        if res.get("ok"):
            return res["result"]
        retry = res.get("parameters", {}).get("retry_after")
        if retry:
            time.sleep(retry + 1)
            continue
        raise RuntimeError(f"Telegram xatosi ({method}): {res}")
    raise RuntimeError(f"Telegram ({method}) javob bermadi")


# ---------- Post matnlari ----------

def e(s):
    return html.escape(str(s), quote=False)


def _dialogue_html(lesson):
    rows = []
    for line in lesson["dialogue"]:
        if line["speaker"] == config.FRENCH_GIRL:
            row = f"🇫🇷 <b>{e(line['speaker'])}:</b> <i>{e(line['text'])}</i>"
            if line.get("uz"):
                row += f"\n      ↳ {e(line['uz'])}"
        else:
            row = f"🇺🇿 <b>{e(line['speaker'])}:</b> {e(line['text'])}"
        rows.append(row)
    return "\n\n".join(rows)


def _phrases_html(lesson):
    return "\n".join(
        f"• <b>{e(p['fr'])}</b> [{e(p.get('pron', ''))}] — {e(p.get('uz', ''))}"
        for p in lesson["key_phrases"]
    )


def _footer():
    return f"\n\n{config.HASHTAG}\n{e(config.CHANNEL_TAG)}"


def full_text(lesson):
    return (
        f"🇫🇷🇺🇿 <b>{e(config.RUBRIC)}</b>\n"
        f"<b>{e(lesson['title_uz'])}</b>\n\n"
        f"{_dialogue_html(lesson)}\n\n"
        f"📌 <b>Yodda tuting:</b>\n{_phrases_html(lesson)}\n\n"
        f"💡 {e(lesson['tip_uz'])}"
        + _footer()
    )


def short_caption(lesson, limit=1024):
    """Rasm/video ostidagi matn (Telegram chegarasi — 1024 belgi)."""
    text = (
        f"🇫🇷🇺🇿 <b>{e(lesson['title_uz'])}</b>\n\n"
        f"{_phrases_html(lesson)}\n\n"
        f"💡 {e(lesson['tip_uz'])}"
        + _footer()
    )
    if len(text) > limit:
        text = (f"🇫🇷🇺🇿 <b>{e(lesson['title_uz'])}</b>\n\n{_phrases_html(lesson)}" + _footer())
    return text[:limit]


# ---------- Yuborish ----------

def send_package(chat_id, pkg):
    """pkg: {"kind": "text_audio"|"photo"|"video", "lesson": ..., "files": {...}}"""
    lesson, kind, files = pkg["lesson"], pkg["kind"], pkg["files"]
    if kind == "text_audio":
        _api("sendMessage", chat_id=chat_id, text=full_text(lesson), parse_mode="HTML")
        if files.get("audio"):
            _api("sendAudio", files={"audio": files["audio"]}, chat_id=chat_id,
                 title=lesson["title_uz"], performer=f"{config.UZBEK_GIRL} & {config.FRENCH_GIRL}",
                 caption=f"🎧 {e(lesson['title_uz'])}\n{e(config.CHANNEL_TAG)}", parse_mode="HTML")
    elif kind == "photo":
        _api("sendPhoto", files={"photo": files["photo"]}, chat_id=chat_id,
             caption=short_caption(lesson), parse_mode="HTML")
    elif kind == "video":
        _api("sendVideo", files={"video": files["video"]}, chat_id=chat_id,
             caption=short_caption(lesson), parse_mode="HTML", supports_streaming=True,
             width=1080, height=1920)


def _admin():
    if not config.ADMIN_CHAT_ID:
        raise RuntimeError("ADMIN_CHAT_ID topilmadi (GitHub Secrets'ga qo'shing)")
    return int(config.ADMIN_CHAT_ID)


def _notify(text, **extra):
    return _api("sendMessage", chat_id=_admin(), text=text, parse_mode="HTML", **extra)


def _now():
    return datetime.datetime.now(config.TZ)


def _sleep_until(moment):
    while True:
        left = (moment - _now()).total_seconds()
        if left <= 0:
            return
        time.sleep(min(left, 30))


def _fresh_offset():
    """Eski xabarlarni o'tkazib yuborish uchun."""
    updates = _api("getUpdates", offset=-1, timeout=0)
    return updates[-1]["update_id"] + 1 if updates else None


def run(pkg, publish_at, rebuild, dry_run=False):
    """
    publish_at — kanalga chiqish vaqti.
    rebuild(lesson, instruction) -> yangi pkg (tahrirdan keyin).
    dry_run=True — kanalga chiqarmaydi, faqat adminga ko'rsatadi.
    """
    preview_at = publish_at - datetime.timedelta(minutes=config.PREVIEW_MINUTES)
    _sleep_until(preview_at)

    # Kechikib ishga tushgan bo'lsa ham, admin kamida 5 daqiqa ko'rsin
    deadline = max(publish_at, _now() + datetime.timedelta(minutes=5))
    offset = _fresh_offset()
    token = f"edit:{int(time.time())}"

    _notify(f"🔔 <b>{deadline:%H:%M}</b> da kanalga chiqadigan post:")
    send_package(_admin(), pkg)
    issues = pkg.get("issues") or []
    note = ("\n\n🔎 Sifat nazorati tuzatgan joylar:\n" + "\n".join(f"• {e(i)}" for i in issues[:6])) if issues else ""
    button_msg = _notify(
        f"Hammasi to'g'rimi? Agar hech narsa bosmasangiz, post <b>{deadline:%H:%M}</b> da "
        f"avtomatik chiqadi.{note}",
        reply_markup={"inline_keyboard": [[{"text": "✏️ Tahrirlash", "callback_data": token}]]},
    )

    instruction, waiting_text = None, False
    while _now() < deadline and instruction is None:
        timeout = int(max(1, min(25, (deadline - _now()).total_seconds())))
        params = {"timeout": timeout, "allowed_updates": ["message", "callback_query"]}
        if offset:
            params["offset"] = offset
        for upd in _api("getUpdates", **params):
            offset = upd["update_id"] + 1
            cq = upd.get("callback_query")
            if cq and cq.get("data") == token and cq["from"]["id"] == _admin():
                _api("answerCallbackQuery", callback_query_id=cq["id"])
                _api("editMessageReplyMarkup", chat_id=_admin(),
                     message_id=button_msg["message_id"], reply_markup={"inline_keyboard": []})
                _notify("✍️ Nimani o'zgartiray? Bitta xabarda yozib yuboring.\n"
                        f"({config.EDIT_WAIT_MINUTES} daqiqa kutaman, keyin eski variant chiqadi.)")
                waiting_text = True
                deadline = max(deadline, _now() + datetime.timedelta(minutes=config.EDIT_WAIT_MINUTES))
                continue
            msg = upd.get("message")
            if waiting_text and msg and msg["chat"]["id"] == _admin() and msg.get("text"):
                instruction = msg["text"]
                break

    if instruction:
        _notify("⏳ Tuzatyapman, tayyor bo'lishi bilan qayta so'ramasdan kanalga chiqaraman.")
        try:
            pkg = rebuild(pkg["lesson"], instruction)
        except Exception as exc:  # tuzatish ishlamasa — eski variant chiqadi
            _notify(f"⚠️ Tuzatib bo'lmadi ({e(exc)}). Asl variant chiqariladi.")

    _sleep_until(publish_at)
    if dry_run:
        _notify("🧪 Sinov rejimi: kanalga chiqarilmadi. Yuqoridagi post shunday ko'rinadi.")
        if instruction:
            send_package(_admin(), pkg)
        return pkg
    send_package(config.CHANNEL_ID, pkg)
    _notify(f"✅ Post kanalga chiqdi: {e(config.CHANNEL_TAG)}")
    return pkg


def report_error(text):
    try:
        _notify(f"❌ Xatolik: {e(text)[:3500]}")
    except Exception:
        pass
