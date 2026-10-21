"""3-agent: Gemini (Nano Banana) orqali post uchun rasm yaratadi."""
from pathlib import Path

import config
import gemini

ASSETS = Path(__file__).resolve().parent / "assets"


def _references():
    """assets/ papkasidagi qahramonlar rasmlari — qahramonlar har doim bir xil ko'rinsin."""
    if not ASSETS.exists():
        return []
    return sorted(p for p in ASSETS.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg"))[:3]


def draw(lesson, out_path, aspect="4:5", variant=""):
    refs = _references()
    prompt = (
        "Warm, bright, high-quality digital illustration for an educational Telegram post. "
        f"Characters: {config.CHARACTERS_EN} "
        f"Scene: {lesson['image_scene']} {variant} "
        "The two young women are talking and smiling, friendly atmosphere. "
        "Modest, family-friendly clothing. No text, no letters, no logos, no watermarks."
    )
    if refs:
        prompt = ("Keep the characters looking exactly like in the reference images. " + prompt)
    return gemini.image(prompt, out_path, aspect=aspect, references=refs)
