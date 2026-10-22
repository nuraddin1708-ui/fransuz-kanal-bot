"""Umumiy sozlamalar. Kalitlar bu yerda YO'Q — ular GitHub Secrets'dan keladi."""
import datetime
import os

TZ = datetime.timezone(datetime.timedelta(hours=5))  # Toshkent / Xiva vaqti

# --- Kalitlar (GitHub Secrets) ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

# --- Ochiq sozlamalar (GitHub Variables) ---
CHANNEL_ID = os.environ.get("CHANNEL_ID") or "@Uzbekcha_Fransuzcha"
CHANNEL_TAG = os.environ.get("CHANNEL_TAG") or "@Uzbekcha_Fransuzcha"
VOICE_SHOHISTA = os.environ.get("VOICE_SHOHISTA", "")
VOICE_CLAIRE = os.environ.get("VOICE_CLAIRE", "")

# Birinchisi ishlamasa (yopilgan bo'lsa), bot keyingisiga o'zi o'tadi
GEMINI_TEXT_MODELS = [m for m in [os.environ.get("GEMINI_TEXT_MODEL"),
                      "gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"] if m]
GEMINI_IMAGE_MODELS = [m for m in [os.environ.get("GEMINI_IMAGE_MODEL"),
                       "gemini-3.1-flash-image", "gemini-nano-banana-2.1",
                       "gemini-3.1-flash-lite-image", "gemini-3-pro-image"] if m]
ELEVEN_MODEL = os.environ.get("ELEVEN_MODEL") or "eleven_v3"

# --- Rubrika ---
RUBRIC = "Fransuzchani o'zbekchada gapirgandek gapiring"
HASHTAG = "#fransuzcha_ozbekchadek"
FRENCH_GIRL = os.environ.get("FRENCH_GIRL") or "Claire"
UZBEK_GIRL = "Shohista"

CHARACTERS_EN = (
    f"{UZBEK_GIRL}: a young Uzbek woman in a traditional Uzbek national dress made of "
    "khan-atlas ikat silk, with an embroidered doppi (skullcap), long dark braids, warm smile. "
    f"{FRENCH_GIRL}: a young French woman with light-brown wavy hair, casual elegant "
    "Parisian style (striped top, light jacket)."
)

# --- Jadval: slot -> (soat, post turi) ---
SLOTS = {
    "morning": (9, "text_audio"),   # 09:00 — matn + audio
    "noon": (14, "photo"),          # 14:00 — rasmli post
    "evening": (18, "video"),       # 18:00 — video
}
PREVIEW_MINUTES = 10   # chiqishdan necha daqiqa oldin adminga ko'rsatiladi
EDIT_WAIT_MINUTES = 15 # «Tahrirlash» bosilgach, ko'rsatma kutish vaqti
