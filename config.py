"""Umumiy sozlamalar. Kalitlar bu yerda YO'Q — ular GitHub Secrets'dan keladi."""
import datetime
import os

TZ = datetime.timezone(datetime.timedelta(hours=5))  # Toshkent / Xiva vaqti

# --- Kalitlar (GitHub Secrets) ---
BOT_TOKEN = os.environ.get("BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

# --- Ochiq sozlamalar (GitHub Variables) ---
CHANNEL_ID = os.environ.get("CHANNEL_ID") or "@Uzbekcha_Fransuzcha"
CHANNEL_TAG = os.environ.get("CHANNEL_TAG") or "@Uzbekcha_Fransuzcha"
VOICE_SHOHISTA = os.environ.get("VOICE_SHOHISTA", "")
VOICE_CLAIRE = os.environ.get("VOICE_CLAIRE", "")

# Bo'sh qoldirilsa, bot kalitingizga ochiq modellardan o'zi tanlaydi (gemini.py)
GEMINI_TEXT_MODELS = [m for m in [os.environ.get("GEMINI_TEXT_MODEL")] if m]
GEMINI_IMAGE_MODELS = [m for m in [os.environ.get("GEMINI_IMAGE_MODEL")] if m]
ELEVEN_MODEL = os.environ.get("ELEVEN_MODEL") or "eleven_v3"

# Bepul ovoz (Microsoft Edge). ElevenLabs kaliti va ovozlari berilsa, o'shanisi ishlatiladi.
EDGE_VOICE_SHOHISTA = os.environ.get("EDGE_VOICE_SHOHISTA") or "uz-UZ-MadinaNeural"
EDGE_VOICE_CLAIRE = os.environ.get("EDGE_VOICE_CLAIRE") or "fr-FR-DeniseNeural"

# --- Rubrika ---
RUBRIC = "Fransuzchani o'zbekchada gapirgandek gapiring"
HASHTAG = "#fransuzcha_ozbekchadek"
FRENCH_GIRL = os.environ.get("FRENCH_GIRL") or "Claire"
UZBEK_GIRL = "Shohista"

CHARACTERS_EN = (
    f"{UZBEK_GIRL}: a young Uzbek woman in a traditional Uzbek national dress made of "
    "khan-atlas ikat silk, with an embroidered doppi (skullcap), long dark braids, warm smile. "
    f"{FRENCH_GIRL}: a young French woman with a slightly plump, soft, chubby figure and round cheeks, "
    "light-brown wavy shoulder-length hair, red beret, Breton striped top under a light beige trench coat, "
    "red scarf, cheerful smile (classic Parisian style)."
)

# Namuna videodagi uslub: qo'lda chizilgan, qalin siyoh chiziqli, issiq ranglar
STYLE_EN = (
    "Hand-drawn cartoon illustration with bold ink outlines and warm watercolor shading, "
    "slightly caricatured friendly characters, warm golden-orange lamp light, cozy atmosphere, "
    "rich Uzbek details (suzani and ikat patterns, blue-and-white ceramics, carpets)."
)

# Qahramonlar pozalari kutubxonasi: assets/characters/<ism>_<poza>.png
# 1-agent har bir gap uchun shu ro'yxatdan mosini tanlaydi.
POSES = {
    "talk": "talking happily, one hand gesturing openly",
    "listen": "listening attentively with a warm smile, hands together",
    "point_up": "explaining, index finger raised like a teacher",
    "point_side": "pointing to the side at something with an open hand",
    "laugh": "laughing joyfully, eyes squinted, hand near mouth",
    "surprised": "surprised, eyes wide open, both hands raised",
    "think": "thinking, hand on chin, looking up",
    "wave": "waving hello with a big smile",
    "thumbs_up": "giving a thumbs up, proud smile",
    "shrug": "shrugging with a confused smile, palms up",
    "excited": "very excited, both fists up, cheerful",
    "shy": "shy smile, hands clasped, head slightly tilted",
    "cup": "holding a cup of tea or coffee with both hands, smiling",
    "phone": "looking at a smartphone in her hand",
    "book": "holding an open notebook, studying",
    "bag": "holding a shopping bag",
}
# Fonlar kutubxonasi: assets/backgrounds/<id>.png (PROMPTLAR.md dagi ro'yxat)
BACKGROUNDS = [
    "uy_mehmonxona",
    "uy_oshxona",
    "choyxona",
    "bozor",
    "registon",
    "cafe",
    "terrace",
    "pastry",
    "register",
    "restoran",
    "metro",
    "vokzal",
    "aeroport",
    "mehmonxona",
    "supermarket",
    "dorixona",
    "shifokor",
    "sinf",
    "kutubxona",
    "park",
    "kocha",
    "kiyim_dokoni",
    "pochta",
    "bank",
    "taksi",
    "dengiz",
    "muzey",
    "sena",
    "monmartr",
    "oshxona_pishirish",
    "yotoqxona",
    "tugilgan_kun",
    "toy",
    "avtobus",
    "ish_stoli",
    "qor",
]

# Har bir poza uchun «_b» varianti ham chiziladi — gapirganda qo'l va og'iz qimirlaydi
POSE_B = "the same pose, but the gesturing hand is moved to a different position and the mouth is open as if speaking"

# Har bir kadr uchun pozani noldan chizish (qimmatroq): Variables'da UNIQUE_POSES=1
UNIQUE_POSES = os.environ.get("UNIQUE_POSES", "").strip() in ("1", "true", "yes")

# --- Jadval: slot -> (soat, post turi) ---
SLOTS = {
    "morning": (9, "text_audio"),   # 09:00 — matn + audio
    "noon": (14, "photo"),          # 14:00 — rasmli post
    "evening": (18, "video"),       # 18:00 — video
}
PREVIEW_MINUTES = 10   # chiqishdan necha daqiqa oldin adminga ko'rsatiladi
EDIT_WAIT_MINUTES = 15 # «Tahrirlash» bosilgach, ko'rsatma kutish vaqti
