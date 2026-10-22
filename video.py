"""2-agent: o'zimizning qisqa vertikal video (namunadagi uslubda, jonli montaj bilan).

Har bir gap — alohida kadr: mavzuga mos fon, shu gapga mos pozadagi Claire va Shohista
stikerlari, tepada skotch-yorliqlar. Montaj: kadrlar surilib almashadi, kamera sekin suzadi,
qahramonlar sakrab chiqadi va poza almashganda «pop» qiladi, gapirayotgani tebranadi,
yorliqlar uchib kiradi, «pop»/«vush» tovushlari, pastda progress chizig'i, oxirida
animatsiyali «Yodda tuting» kartasi. Kadrlar Python'da chiziladi va ffmpeg'ga uzatiladi.
Boshqa odamlarning videolari ishlatilmaydi (mualliflik huquqi), hamma narsa o'zimizniki.
"""
import math
import random
import struct
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import artist
import config
import style
import voice

FPS = 25
W, H = style.W, style.H
GAP = 0.45            # gaplar orasidagi pauza (soniya)
TRANSITION = 0.35     # kadr almashish davomiyligi
OUTRO_SECONDS = 5.0
SR = 44100
MUSIC = style.ROOT / "assets" / "music"


def _clamp(x):
    return max(0.0, min(1.0, x))


def ease_out_cubic(p):
    p = _clamp(p)
    return 1 - (1 - p) ** 3


def ease_out_back(p, k=1.7):
    p = _clamp(p)
    return 1 + (k + 1) * (p - 1) ** 3 + k * (p - 1) ** 2


# ---------- Fonlar ----------

def _backgrounds(lesson, workdir):
    """Har bir gap uchun fon: 1) assets/backgrounds/<bg>.png, 2) Gemini chizgan sahna, 3) kutubxona, 4) gradient."""
    folder = style.ROOT / "assets" / "backgrounds"
    library = sorted(p for p in folder.glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg")) if folder.exists() else []
    images, cache, can_draw = [], {}, True
    for i, line in enumerate(lesson["dialogue"]):
        key = line.get("bg") or line.get("shot") or str(i)
        if key not in cache:
            path = next((p for p in library if p.stem.lower() == str(line.get("bg", "")).lower()), None)
            if path is None and can_draw:
                try:
                    path = artist.shot(lesson, line, workdir / f"shot_{i:02d}.png", with_characters=False)
                except Exception as exc:
                    print(f"Kadr foni chizilmadi: {exc}")
                    can_draw = False
            if path is None and library:
                path = library[(len(cache) + random.Random(lesson["topic"]).randint(0, 99)) % len(library)]
            if path is None:
                path = workdir / "bg_fallback.png"
                style.warm_fallback().convert("RGB").save(path)
            cache[key] = style.cover(Image.open(path), int(W * 1.12), int(H * 1.12)).convert("RGB")
        images.append(cache[key])
    return images


# ---------- Qahramonlar ----------

def _poses(lesson, workdir):
    """Har bir gap uchun [(Claire, Shohista)] stikerlari — gapga mos poza."""
    names = (config.FRENCH_GIRL, config.UZBEK_GIRL)
    out, cache = [], {}
    for i, line in enumerate(lesson["dialogue"]):
        pair = []
        for name in names:
            speaking = line["speaker"] == name
            tag = line.get(f"pose_{name.lower()}") or ("talk" if speaking else "listen")
            img = None
            if config.UNIQUE_POSES and line.get("shot"):  # har kadr uchun yangi poza chizish (pullik)
                try:
                    img = artist.pose_sticker(name, f"{line['shot']} ({'speaking' if speaking else 'listening'})",
                                              workdir / f"pose_{i}_{name}.png")
                except Exception as exc:
                    print(f"Poza chizilmadi ({name}): {exc}")
            if img is None:
                img = style.sticker(name, tag)
            if img is None:
                return []
            key = (name, id(img) if not isinstance(img, Path) else str(img))
            if key not in cache:
                im = Image.open(img).convert("RGBA") if isinstance(img, (str, Path)) else img
                cache[key] = style.fit(im, 560, 1020)
            pair.append(cache[key])
        out.append(pair)
    return out


# ---------- Yorliqlar ----------

def _tapes(line, title=None):
    tapes = []
    if title:
        tapes.append(style.tape(title, style.ORANGE, size=62, max_w=900))
    if line["lang"] == "fr":
        tapes.append(style.tape(f"«{line['text']}»", style.WHITE, size=62, max_w=920, upper=False))
        if line.get("uz"):
            tapes.append(style.tape(line["uz"], style.YELLOW, size=54, max_w=900))
    else:
        tapes.append(style.tape(f"{config.UZBEK_GIRL} o'rgatadi", style.GREEN, size=38, max_w=700))
        size = 48 if len(line["text"]) < 120 else 42
        tapes.append(style.tape(line["text"], style.WHITE, size=size, max_w=920, upper=False))
    return tapes


def _tape_positions(tapes, top=200, gap=10):
    out, y = [], top
    for t in tapes:
        out.append(((W - t.width) // 2, y))
        y += t.height - 20 + gap
    return out


# ---------- Tovush ----------

def _synth(events, total, path):
    """«pop» va «vush» effektlari: [(vaqt, tur), ...] — kutubxonasiz, oddiy Python."""
    n = int(total * SR) + SR
    buf = [0.0] * n
    rnd = random.Random(7)
    for t0, kind in events:
        s0 = int(t0 * SR)
        if kind == "pop":
            for i in range(int(0.09 * SR)):
                if s0 + i >= n:
                    break
                tt = i / SR
                buf[s0 + i] += 0.35 * math.sin(2 * math.pi * (1300 - 7000 * tt) * tt) * math.exp(-tt * 45)
        else:  # whoosh
            length, lp = int(0.32 * SR), 0.0
            for i in range(length):
                if s0 + i >= n:
                    break
                lp += 0.08 * (rnd.uniform(-1, 1) - lp)
                buf[s0 + i] += 0.5 * lp * math.sin(math.pi * i / length) ** 2
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 32000)) for v in buf))
    return path


def _mix_audio(clips, starts, sfx, total, out):
    inputs, parts = [], []
    for i, (clip, st) in enumerate(zip(clips, starts)):
        inputs += ["-i", str(clip)]
        ms = int(st * 1000)
        parts.append(f"[{i}:a]aresample={SR},aformat=channel_layouts=stereo,adelay={ms}|{ms}[d{i}]")
    k = len(clips)
    inputs += ["-i", str(sfx)]
    parts.append(f"[{k}:a]aresample={SR},aformat=channel_layouts=stereo,volume=0.6[sfx]")
    labels, n = "".join(f"[d{i}]" for i in range(k)) + "[sfx]", k + 1
    music = sorted(MUSIC.glob("*.mp3")) if MUSIC.exists() else []
    if music:  # o'zingiz qo'ygan, litsenziyasi toza musiqa
        inputs += ["-stream_loop", "-1", "-i", str(music[0])]
        parts.append(f"[{k + 1}:a]aresample={SR},aformat=channel_layouts=stereo,volume=0.10,"
                     f"afade=t=out:st={max(0, total - 1.5):.2f}:d=1.5[mus]")
        labels, n = labels + "[mus]", n + 1
    parts.append(f"{labels}amix=inputs={n}:normalize=0:duration=longest,atrim=0:{total:.2f}[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(parts),
                    "-map", "[a]", "-c:a", "aac", "-b:a", "160k", str(out)], check=True)
    return out


# ---------- Yakuniy kadr ----------

def _outro_layers(lesson):
    phrases = lesson["key_phrases"][:4]
    card = Image.new("RGBA", (W - 180, 160 + 250 * len(phrases)), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((26, 32, card.width - 14, card.height - 8), 48, fill=(0, 0, 0, 80))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(card).rounded_rectangle((20, 20, card.width - 20, card.height - 20), 48, fill=style.NAVY + (255,))
    big, mid, small = style.font(66), style.font(46, bold=False), style.font(44, bold=False)
    rows = []
    for p in phrases:
        row = Image.new("RGBA", (card.width - 120, 240), (0, 0, 0, 0))
        d = ImageDraw.Draw(row)
        d.text((0, 0), p["fr"][:26], font=big, fill=style.YELLOW[0])
        d.text((0, 92), f"[{p.get('pron', '')}]"[:36], font=mid, fill=(255, 255, 255))
        d.text((0, 152), p.get("uz", "")[:36], font=small, fill=(170, 200, 255))
        rows.append(row)
    return {
        "paper": style.paper(), "card": card, "rows": rows,
        "head": style.tape("Yodda tuting", style.GREEN, size=64, angle=-1.5),
        "sub": style.tape("Obuna bo'ling!", style.YELLOW, size=68, angle=1.5),
        "tag": style.tape(config.CHANNEL_TAG, style.BLACK, size=42, upper=False, angle=0),
    }


def _outro_pop_time(layers):
    return 0.8 + len(layers["rows"]) * 0.35


def _outro_frame(L, t):
    f = L["paper"].copy()
    head, card, sub, tag = L["head"], L["card"], L["sub"], L["tag"]
    f.alpha_composite(head, ((W - head.width) // 2, int(150 - (1 - ease_out_back(t / 0.4)) * 300)))
    cy = 330 + int((1 - ease_out_cubic((t - 0.2) / 0.5)) * H)
    if t > 0.2:
        f.alpha_composite(card, (90, cy))
        for i, row in enumerate(L["rows"]):
            a = ease_out_cubic((t - 0.6 - i * 0.35) / 0.3)
            if a > 0:
                r = row.copy()
                r.putalpha(r.getchannel("A").point(lambda v: int(v * a)))
                f.alpha_composite(r, (170 + int((1 - a) * 60), cy + 90 + i * 250))
    s = ease_out_back((t - _outro_pop_time(L)) / 0.35)
    if s > 0.01:
        yb = 330 + card.height + 30
        im = sub.resize((max(1, int(sub.width * s)), max(1, int(sub.height * s))))
        f.alpha_composite(im, ((W - im.width) // 2, yb + (sub.height - im.height) // 2))
        f.alpha_composite(tag, ((W - tag.width) // 2, yb + sub.height))
    return f


# ---------- Asosiy ----------

def make(lesson, workdir, clips=None, images=None):
    workdir = Path(workdir).resolve()
    lines = lesson["dialogue"]
    if clips is None:
        clips, _ = voice.speak_dialogue(lesson, workdir)
    poses = _poses(lesson, workdir)
    bgs = images or _backgrounds(lesson, workdir)

    # Vaqt jadvali
    starts, ends, t = [], [], 0.6
    for clip in clips:
        d = voice.duration(clip)
        starts.append(t)
        ends.append(t + d)
        t += d + GAP
    outro_start = t
    total = outro_start + OUTRO_SECONDS
    seg_starts = [0.0] + [e + GAP * 0.5 for e in ends[:-1]]

    tapes = [_tapes(line, lesson["title_uz"] if i == 0 else None) for i, line in enumerate(lines)]
    positions = [_tape_positions(tp) for tp in tapes]
    outro = _outro_layers(lesson)

    # Tovush effektlari
    events = []
    for i in range(len(lines)):
        if i == 0 or bgs[i] is not bgs[i - 1]:
            events.append((seg_starts[i], "whoosh"))
        events += [(seg_starts[i] + 0.12 + j * 0.16, "pop") for j in range(len(tapes[i]))]
    events += [(outro_start, "whoosh"), (outro_start + _outro_pop_time(outro), "pop")]
    audio = _mix_audio(clips, starts, _synth(events, total, workdir / "sfx.wav"), total, workdir / "audio.m4a")

    out = workdir / "video.mp4"
    proc = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(audio),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(out),
    ], stdin=subprocess.PIPE)

    brand = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    style.brand(brand, "UZBEKCHA FRANSUZCHA", f"{config.UZBEK_GIRL} & {config.FRENCH_GIRL}")
    brand = brand.crop(brand.getbbox())

    def bg_crop(img, prog):
        dx = int((img.width - W) * prog)
        dy = int((img.height - H) * (0.6 - 0.4 * prog))
        return img.crop((dx, dy, dx + W, dy + H))

    last_frame = None
    for fi in range(int(total * FPS)):
        tt = fi / FPS
        if tt >= outro_start:
            frame = _outro_frame(outro, tt - outro_start).convert("RGB")
            lt = tt - outro_start
            if lt < TRANSITION and last_frame is not None:  # oxirgi kadr chapga surilib ketadi
                p = ease_out_cubic(lt / TRANSITION)
                mixed = Image.new("RGB", (W, H))
                mixed.paste(last_frame, (int(-W * 0.35 * p), 0))
                mixed.paste(frame, (int(W * (1 - p)), 0))
                frame = mixed
            proc.stdin.write(frame.tobytes())
            continue

        i = max(k for k in range(len(lines)) if seg_starts[k] <= tt)
        local = tt - seg_starts[i]
        seg_len = (seg_starts[i + 1] if i + 1 < len(lines) else outro_start) - seg_starts[i]

        # Fon: sekin suzish + yangi fonga surilib o'tish
        prog = _clamp(local / max(seg_len, 0.1))
        cur = bg_crop(bgs[i], prog if i % 2 == 0 else 1 - prog)
        if i > 0 and bgs[i] is not bgs[i - 1] and local < TRANSITION:
            p = ease_out_cubic(local / TRANSITION)
            frame = Image.new("RGB", (W, H))
            frame.paste(bg_crop(bgs[i - 1], 1.0 if (i - 1) % 2 == 0 else 0.0), (int(-W * 0.35 * p), 0))
            frame.paste(cur, (int(W * (1 - p)), 0))
        else:
            frame = cur.copy()
        frame = frame.convert("RGBA")

        # Qahramonlar: boshida sakrab chiqadi, poza almashsa «pop», gapirayotgani tebranadi
        speaker = 0 if lines[i]["speaker"] == config.FRENCH_GIRL else 1
        for k, st in enumerate(poses[i] if poses else []):
            scale = ease_out_back((tt - 0.1 - k * 0.15) / 0.45)
            changed = i > 0 and poses[i - 1][k] is not st
            if changed:
                scale = min(scale, 0.85 + 0.15 * ease_out_back((local - 0.05) / 0.3, 2.5))
            if scale <= 0.01:
                continue
            img = st if scale > 0.999 else st.resize((max(1, int(st.width * scale)), max(1, int(st.height * scale))))
            x = (10 if k == 0 else W - st.width - 10) + (st.width - img.width) // 2
            y = H - img.height - 30
            if k == speaker and starts[i] <= tt <= ends[i]:
                y -= int(abs(math.sin(2 * math.pi * 2.1 * tt)) * 16)
            else:
                y -= int(math.sin(2 * math.pi * 0.5 * tt + k) * 4)
            frame.alpha_composite(img, (x, y))

        # Yorliqlar navbat bilan uchib kiradi
        frame.alpha_composite(brand, (30, 50))
        for j, (tp, (x, y)) in enumerate(zip(tapes[i], positions[i])):
            p = (local - 0.12 - j * 0.16) / 0.35
            if p > 0:
                side = -1 if j % 2 == 0 else 1
                frame.alpha_composite(tp, (x + int((1 - ease_out_back(p, 1.3)) * side * W * 0.8), y))

        ImageDraw.Draw(frame).rectangle((0, H - 10, int(W * tt / total), H), fill=style.YELLOW[0] + (255,))
        last_frame = frame.convert("RGB")
        proc.stdin.write(last_frame.tobytes())

    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg video yig'a olmadi")
    return out
