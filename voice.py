"""4-agent: dialogni audioga aylantiradi.

Bepul: Microsoft Edge ovozlari (edge-tts) — o'zbekcha Madina va fransuzcha Denise.
ElevenLabs kaliti va VOICE_SHOHISTA / VOICE_CLAIRE berilgan bo'lsa, ElevenLabs ishlatiladi.
"""
import asyncio
import subprocess
import time
from pathlib import Path

import requests

import config

URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128"
FALLBACK_MODEL = "eleven_multilingual_v2"


def _voice_for(speaker):
    voice = config.VOICE_CLAIRE if speaker == config.FRENCH_GIRL else config.VOICE_SHOHISTA
    if not voice:
        raise RuntimeError("VOICE_SHOHISTA / VOICE_CLAIRE o'rnatilmagan (GitHub Variables)")
    return voice


def _use_eleven():
    return bool(config.ELEVENLABS_API_KEY and config.VOICE_SHOHISTA and config.VOICE_CLAIRE)


def speak(text, speaker, out_path):
    if _use_eleven():
        try:
            return speak_eleven(text, speaker, out_path)
        except RuntimeError as exc:
            print(f"ElevenLabs ishlamadi, bepul ovozga o'tamiz: {exc}")
    return speak_edge(text, speaker, out_path)


def speak_edge(text, speaker, out_path):
    import edge_tts

    voice = config.EDGE_VOICE_CLAIRE if speaker == config.FRENCH_GIRL else config.EDGE_VOICE_SHOHISTA
    last = None
    for attempt in range(3):
        try:
            asyncio.run(edge_tts.Communicate(text, voice).save(str(out_path)))
            return out_path
        except Exception as exc:
            last = exc
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"Edge ovozi ishlamadi ({voice}) — {last}")


def speak_eleven(text, speaker, out_path):
    models = [config.ELEVEN_MODEL] + ([FALLBACK_MODEL] if config.ELEVEN_MODEL != FALLBACK_MODEL else [])
    last = None
    for model in models:
        for attempt in range(3):
            r = requests.post(
                URL.format(voice=_voice_for(speaker)),
                headers={"xi-api-key": config.ELEVENLABS_API_KEY},
                json={"text": text, "model_id": model},
                timeout=120,
            )
            if r.status_code == 200:
                Path(out_path).write_bytes(r.content)
                return out_path
            last = f"{r.status_code}: {r.text[:300]}"
            if r.status_code in (429, 500, 502, 503):
                time.sleep(8 * (attempt + 1))
                continue
            break  # boshqa model bilan urinib ko'ramiz
    raise RuntimeError(f"ElevenLabs xatosi — {last}")


def speak_dialogue(lesson, workdir):
    """Har bir qator uchun alohida mp3 va hammasi birlashgan mp3 qaytaradi."""
    workdir = Path(workdir)
    clips = []
    for i, line in enumerate(lesson["dialogue"]):
        clips.append(speak(line["text"], line["speaker"], workdir / f"line_{i:02d}.mp3"))
    full = workdir / "dialog.mp3"
    concat(clips, full)
    return clips, full


def concat(clips, out_path, pause=0.5):
    """Qatorlar orasiga qisqa pauza qo'yib, bitta audio qiladi."""
    inputs, filters = [], []
    for i, clip in enumerate(clips):
        inputs += ["-i", str(clip)]
        filters.append(f"[{i}:a]apad=pad_dur={pause}[a{i}]")
    joined = "".join(f"[a{i}]" for i in range(len(clips)))
    graph = ";".join(filters) + f";{joined}concat=n={len(clips)}:v=0:a=1[out]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph,
                    "-map", "[out]", "-b:a", "128k", str(out_path)], check=True)
    return out_path


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())
