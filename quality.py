"""5-agent: sifat nazorati — fransuzcha, talaffuz, o'zbekcha imlo va mazmunni tekshiradi."""
import json

import gemini, researcher

PROMPT = """You are a strict editor for a Telegram channel that teaches French to Uzbek speakers.
Check this lesson JSON:
1. French: grammar, spelling, accents, natural usage. Fix every mistake.
2. "pron": the reading in Uzbek Latin letters must match real French pronunciation.
3. Uzbek: Latin script, correct spelling and apostrophes (o', g'), natural and friendly.
4. Translations ("uz") must match the French meaning.
5. Content must be polite, family-friendly, and not political or religious.
Return ONLY this JSON:
{"approved": true/false, "issues": ["short list of problems found, in Uzbek"],
 "fixed": <the full corrected lesson JSON, same format>}

Lesson:
"""


def check(lesson, rounds=2):
    """Tuzatilgan darsni va topilgan muammolar ro'yxatini qaytaradi."""
    all_issues = []
    for _ in range(rounds):
        try:
            result = gemini.ask(PROMPT + json.dumps(lesson, ensure_ascii=False), want_json=True)
        except Exception as exc:  # nazorat ishlamasa ham post chiqaveradi
            print(f"Sifat nazorati ishlamadi: {exc}")
            break
        issues = result.get("issues") or []
        all_issues += issues
        fixed = result.get("fixed")
        if fixed:
            try:
                researcher.validate(fixed)
                lesson = fixed
            except ValueError:
                pass
        if result.get("approved") and not issues:
            break
    return lesson, all_issues
