"""Gemini API bilan ishlash (matn, internet qidiruvi, rasm)."""
import base64
import json
import time
from pathlib import Path

import requests

import config

URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _post(models, body):
    """Ro'yxatdagi modellarni navbat bilan sinaydi: 404/400 bo'lsa keyingisiga o'tadi."""
    errors = []
    for model in models:
        try:
            return _post_one(model, body)
        except ModelUnavailable as exc:
            errors.append(str(exc))
    raise RuntimeError("Hech bir Gemini modeli ishlamadi — " + " | ".join(errors))


class ModelUnavailable(RuntimeError):
    pass


def _post_one(model, body, retries=3):
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY topilmadi (GitHub Secrets'ga qo'shing)")
    last = None
    for attempt in range(retries):
        r = requests.post(
            URL.format(model=model),
            headers={"x-goog-api-key": config.GEMINI_API_KEY},
            json=body,
            timeout=180,
        )
        if r.status_code == 200:
            return r.json()
        last = f"{r.status_code}: {r.text[:500]}"
        if r.status_code == 429 and "quota" in r.text.lower() and attempt == retries - 1:
            raise ModelUnavailable(f"{model}: limit tugagan (429)")
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(10 * (attempt + 1))
            continue
        if r.status_code == 404 or (r.status_code == 400 and "model" in r.text.lower()):
            raise ModelUnavailable(f"{model}: {r.status_code}")
        break
    raise RuntimeError(f"Gemini xatosi ({model}) — {last}")


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
        data = _post(config.GEMINI_TEXT_MODELS, body)
    except RuntimeError:
        if not search:
            raise
        # Internet qidiruvi limitga tushsa — qidiruvsiz yozadi
        return ask(prompt, want_json=want_json, search=False)
    parts = data["candidates"][0]["content"].get("parts", [])
    text = "".join(p.get("text", "") for p in parts)
    return _extract_json(text) if want_json else text


def image(prompt, out_path, aspect="4:5", references=()):
    """Nano Banana orqali rasm yaratadi va faylga saqlaydi."""
    parts = []
    for ref in references:
        mime = "image/png" if str(ref).endswith(".png") else "image/jpeg"
        parts.append({"inlineData": {"mimeType": mime,
                                     "data": base64.b64encode(Path(ref).read_bytes()).decode()}})
    parts.append({"text": prompt})
    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect},
        },
    }
    data = _post(config.GEMINI_IMAGE_MODELS, body)
    for p in data["candidates"][0]["content"].get("parts", []):
        blob = p.get("inlineData") or p.get("inline_data")
        if blob:
            Path(out_path).write_bytes(base64.b64decode(blob["data"]))
            return out_path
    raise RuntimeError("Gemini rasm qaytarmadi")
