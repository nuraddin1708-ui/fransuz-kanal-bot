"""Gemini API bilan ishlash (matn, internet qidiruvi, rasm).

Model nomlari tez-tez o'zgaradi, shuning uchun bot kalitingizga ochiq modellar ro'yxatini
o'zi so'rab oladi va eng mosini tanlaydi. Variables'da GEMINI_TEXT_MODEL / GEMINI_IMAGE_MODEL
berilgan bo'lsa, avval o'shalar sinab ko'riladi.
"""
import base64
import json
import re
import time
from functools import lru_cache
from pathlib import Path

import requests

import config

BASE = "https://generativelanguage.googleapis.com/v1beta"
URL = BASE + "/models/{model}:generateContent"


class ModelUnavailable(RuntimeError):
    pass


def _key():
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY topilmadi (GitHub Secrets'ga qo'shing)")
    return config.GEMINI_API_KEY


def _version(name):
    m = re.search(r"gemini-(\d+(?:\.\d+)?)", name)
    return float(m.group(1)) if m else 0.0


@lru_cache(maxsize=1)
def _available():
    """Kalitga ochiq, generateContent qo'llaydigan modellar nomlari."""
    names, token = [], None
    for _ in range(10):
        params = {"pageSize": 1000}
        if token:
            params["pageToken"] = token
        r = requests.get(BASE + "/models", params=params,
                         headers={"x-goog-api-key": _key()}, timeout=60)
        if r.status_code != 200:
            raise RuntimeError(f"Gemini modellar ro'yxati olinmadi — {r.status_code}: {r.text[:300]}")
        data = r.json()
        for m in data.get("models", []):
            if "generateContent" in m.get("supportedGenerationMethods", []):
                names.append(m["name"].removeprefix("models/"))
        token = data.get("nextPageToken")
        if not token:
            break
    return names


def _skip(name):
    return any(w in name for w in ("tts", "audio", "live", "embedding", "robotics",
                                   "computer-use", "thinking", "gemma", "learnlm"))


def text_models():
    names = [n for n in _available() if "gemini" in n and "image" not in n and not _skip(n)]
    # Bepul rejimda limiti kattaroq bo'lgani uchun flash modellar oldinda, yangilari birinchi
    flash = sorted((n for n in names if "flash" in n), key=lambda n: (-_version(n), "lite" in n, "preview" in n))
    rest = sorted((n for n in names if "flash" not in n), key=lambda n: (-_version(n), "preview" in n))
    return config.GEMINI_TEXT_MODELS + flash + rest


def image_models():
    names = [n for n in _available() if "image" in n and "gemini" in n and not _skip(n)]
    names.sort(key=lambda n: (-_version(n), "pro" in n, "preview" in n))
    return config.GEMINI_IMAGE_MODELS + names


def _post(models, body):
    """Ro'yxatdagi modellarni navbat bilan sinaydi: ishlamasa keyingisiga o'tadi."""
    errors, seen = [], set()
    for model in models:
        if model in seen:
            continue
        seen.add(model)
        try:
            return _post_one(model, body)
        except ModelUnavailable as exc:
            errors.append(str(exc))
        if len(seen) >= 6:
            break
    raise RuntimeError("Hech bir Gemini modeli ishlamadi — " + " | ".join(errors))


def _post_one(model, body, retries=3):
    last = None
    for attempt in range(retries):
        r = requests.post(URL.format(model=model), headers={"x-goog-api-key": _key()},
                          json=body, timeout=180)
        if r.status_code == 200:
            return r.json()
        last = f"{r.status_code}: {r.text[:300]}"
        if r.status_code == 429:
            # Bepul limit tugagan bo'lsa (yoki model bepul emas) — kutmasdan keyingi modelga
            if "quota" in r.text.lower() or "free_tier" in r.text.lower():
                raise ModelUnavailable(f"{model}: limit / bepul emas (429)")
            time.sleep(15 * (attempt + 1))
            continue
        if r.status_code in (500, 502, 503, 504):
            time.sleep(10 * (attempt + 1))
            continue
        if r.status_code in (400, 403, 404):
            raise ModelUnavailable(f"{model}: {last}")
        break
    raise ModelUnavailable(f"{model}: {last}")


def _extract_json(text):
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"Javobda JSON yo'q: {text[:300]}")
    return json.loads(text[start:end + 1])


def ask(prompt, want_json=False, search=False):
    """Matnli so'rov. search=True bo'lsa, Gemini internetdan qidiradi."""
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    if search:
        body["tools"] = [{"google_search": {}}]
    elif want_json:
        body["generationConfig"] = {"responseMimeType": "application/json"}
    try:
        data = _post(text_models(), body)
        parts = data["candidates"][0]["content"].get("parts", [])
        text = "".join(p.get("text", "") for p in parts)
        return _extract_json(text) if want_json else text
    except (RuntimeError, ValueError, KeyError):
        if not search:
            raise
        # Internet qidiruvi ishlamasa yoki JSON buzilsa — qidiruvsiz yozadi
        return ask(prompt, want_json=want_json, search=False)


def image(prompt, out_path, aspect="4:5", references=()):
    """Nano Banana orqali rasm yaratadi va faylga saqlaydi."""
    parts = []
    for ref in references:
        mime = "image/png" if str(ref).lower().endswith(".png") else "image/jpeg"
        parts.append({"inlineData": {"mimeType": mime,
                                     "data": base64.b64encode(Path(ref).read_bytes()).decode()}})
    parts.append({"text": prompt})
    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"aspectRatio": aspect},
        },
    }
    data = _post(image_models(), body)
    for p in data["candidates"][0]["content"].get("parts", []):
        blob = p.get("inlineData") or p.get("inline_data")
        if blob:
            Path(out_path).write_bytes(base64.b64decode(blob["data"]))
            return out_path
    raise RuntimeError("Gemini rasm qaytarmadi")
