"""Umumiy sozlamalar. Kalitlar bu yerda YO'Q — ular GitHub Secrets'dan keladi."""
import datetime
import os

TZ = datetime.timezone(datetime.timedelta(hours=5))  # Toshkent / Xiva vaqti

# --- Kalitlar (GitHub Secrets) ---
BOT_TOKEN = os.environ.get("BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")  # ixtiyoriy: faqat «Tahrirlash» uchun

# --- Ochiq sozlamalar (GitHub Variables) ---
def _channel(raw):
    """«https://t.me/kanal» yoki «kanal» yozilgan bo'lsa ham «@kanal» qiladi."""
    raw = (raw or "").strip()
    if raw.startswith("-100") or raw.lstrip("-").isdigit():
        return raw
    raw = raw.replace("https://", "").replace("http://", "").replace("t.me/", "").strip("/@ ")
    return "@" + raw if raw else "@Uzbekcha_Fransuzcha"


def _voice(raw):
    """Voice ID oldiga yoki ortiga ortiqcha so'z yozilgan bo'lsa ham, faqat ID'ni oladi."""
    parts = [p for p in (raw or "").replace(",", " ").split() if len(p) >= 18 and p.isalnum()]
    return parts[0] if parts else ""


CHANNEL_ID = _channel(os.environ.get("CHANNEL_ID"))
CHANNEL_TAG = os.environ.get("CHANNEL_TAG") or CHANNEL_ID
# Ovozlar akkauntdagi ishlaydigan ovozlar: Shohista — «Gulnora» (o'zbekcha), Claire — «Sarah».
# Boshqasini qo'yish uchun GitHub Variables'ga VOICE_SHOHISTA_ID / VOICE_CLAIRE_ID qo'shing.
VOICE_SHOHISTA = _voice(os.environ.get("VOICE_SHOHISTA_ID")) or "6Fkh9WgMXOqBcOWxX91f"
VOICE_CLAIRE = _voice(os.environ.get("VOICE_CLAIRE_ID")) or "EXAVITQu4vr4xnSDxMaL"
ELEVEN_MODEL = os.environ.get("ELEVEN_MODEL") or "eleven_v3"

GEMINI_TEXT_MODELS = [m for m in [os.environ.get("GEMINI_TEXT_MODEL"),
                      "gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"] if m]
GEMINI_IMAGE_MODELS = []  # bu versiyada rasm Gemini'siz chiziladi

# --- Rubrika ---
RUBRIC = "Fransuzchani o'zbekchada gapirgandek gapiring"
HASHTAG = "#fransuzcha_ozbekchadek"
FRENCH_GIRL = "Claire"
UZBEK_GIRL = "Shohista"

# --- Jadval: slot -> (soat, post turi) ---
SLOTS = {
    "morning": (9, "text_audio"),   # 09:00 — matn + audio
    "noon": (14, "photo"),          # 14:00 — kartochkali post
    "evening": (18, "video"),       # 18:00 — video
}
PREVIEW_MINUTES = 10    # chiqishdan necha daqiqa oldin adminga ko'rsatiladi
EDIT_WAIT_MINUTES = 15  # «Tahrirlash» bosilgach, ko'rsatma kutish vaqti
LOW_STOCK_WARNING = 15  # shuncha dars qolganda ogohlantiradi
