"""1-agent: rubrika bo'yicha internetdan izlab, dars-maqola tayyorlaydi."""
import json

import config
import gemini

SCHEMA = f"""{{
  "topic": "short topic name in Uzbek (e.g. 'Kafeda buyurtma berish')",
  "title_uz": "catchy post title in Uzbek",
  "dialogue": [
    {{"speaker": "{config.FRENCH_GIRL}", "lang": "fr", "text": "what she says in French", "uz": "Uzbek translation", "shot": "frame description in English", "bg": "short place id, e.g. cafe", "pose_{config.FRENCH_GIRL.lower()}": "talk", "pose_{config.UZBEK_GIRL.lower()}": "listen"}},
    {{"speaker": "{config.UZBEK_GIRL}", "lang": "uz", "text": "Shohista, in Uzbek, repeats the French phrase, gives its reading in Uzbek letters in «...» and explains the meaning", "shot": "frame description in English", "bg": "cafe", "pose_{config.FRENCH_GIRL.lower()}": "cup", "pose_{config.UZBEK_GIRL.lower()}": "point_up"}}
  ],
  "key_phrases": [{{"fr": "French phrase", "pron": "reading in Uzbek Latin letters", "uz": "meaning"}}],
  "tip_uz": "one short practical tip in Uzbek",
  "image_scene": "one-sentence scene description in English for an illustration (place, action, mood)"
}}"""

RULES = f"""
Rubric: «{config.RUBRIC}» — a Telegram channel teaching French to Uzbek speakers.
Format: a conversation between {config.FRENCH_GIRL} (French girl, speaks only French)
and {config.UZBEK_GIRL} (Uzbek girl in national dress). {config.FRENCH_GIRL} says something
useful in French; {config.UZBEK_GIRL} teaches the audience: repeats it, writes how to read it
with Uzbek Latin letters (o', g', sh, ch; use ö/ü only when unavoidable) and explains it simply.
Requirements:
- 4 to 8 dialogue lines, alternating speakers, starting with {config.FRENCH_GIRL}.
- Everyday, practical French (A1–A2 level). French must be 100% correct, with accents.
- Uzbek must be in Latin script, natural and friendly, correct apostrophes (o', g').
- 2 to 4 key_phrases taken from the dialogue.
- Every dialogue line has its own "shot": one English sentence describing THAT video frame like a
  film storyboard — the exact place, what each girl is doing, her facial emotion, and props that
  show the meaning of the phrase (e.g. ordering coffee → café counter, cup, menu; surprise → wide
  eyes). Consecutive shots continue one small story but change angle, action or props.
- "bg": a short English id of the place; lines in the same place share the same id.
- "pose_<name>" for BOTH girls on every line: choose the pose that best matches that moment,
  only from this list: {", ".join(config.POSES)}. Vary poses between lines; the speaker
  usually talks/explains, the listener reacts (laugh, surprised, think, listen...).
- Do not repeat any topic from the "already used" list.
- Answer with ONLY the JSON object, no other text.
"""


def make_lesson(slot, used_topics):
    extra = {
        "text_audio": "This lesson will be read aloud as audio — keep sentences short and clear.",
        "photo": "This lesson becomes a picture post — keep it compact (4 lines of dialogue).",
        "video": "This lesson becomes a short vertical video — 4 to 6 short lines.",
    }[slot]
    prompt = (
        "Search the web for real, commonly used French expressions and good beginner lesson "
        "ideas, then write ONE new lesson.\n"
        f"{RULES}\n{extra}\n"
        f"Already used topics: {json.dumps(used_topics[-60:], ensure_ascii=False)}\n\n"
        f"JSON format:\n{SCHEMA}"
    )
    lesson = gemini.ask(prompt, want_json=True, search=True)
    validate(lesson)
    return lesson


def revise(lesson, instruction):
    """Admin «Tahrirlash» orqali yozgan ko'rsatma bo'yicha darsni tuzatadi."""
    prompt = (
        f"{RULES}\nHere is a lesson JSON:\n{json.dumps(lesson, ensure_ascii=False)}\n\n"
        f"The channel admin asked for this change (in Uzbek): «{instruction}»\n"
        "Apply the change carefully, keep everything else correct, and return the full "
        f"updated lesson as ONLY JSON in the same format:\n{SCHEMA}"
    )
    new = gemini.ask(prompt, want_json=True)
    validate(new)
    return new


def validate(lesson):
    for key in ("topic", "title_uz", "dialogue", "key_phrases", "tip_uz", "image_scene"):
        if not lesson.get(key):
            raise ValueError(f"Darsda '{key}' yo'q")
    if len(lesson["dialogue"]) < 2:
        raise ValueError("Dialog juda qisqa")
    for line in lesson["dialogue"]:
        if not {"speaker", "lang", "text"} <= line.keys():
            raise ValueError(f"Dialog qatori noto'g'ri: {line}")
