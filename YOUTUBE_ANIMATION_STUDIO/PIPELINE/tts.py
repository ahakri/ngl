"""Narration synthesis with word-level timings (Kokoro neural TTS).

Usage: /opt/ttsenv/bin/python tts.py <script.json> <out_dir>
script.json: {"voice": "am_michael", "speed": 1.0, "lines": [{"id": "L1", "text": "...", "pause_after": 0.3}, ...]}
Outputs: out_dir/narration.wav (24 kHz mono) and out_dir/timings.json:
  {"duration": s, "lines": [{"id","start","end","text","words":[{"w","start","end"}]}]}

Word timings: each line is synthesised separately (exact line boundaries); inside a line,
leading/trailing silence is trimmed by energy and the voiced span is distributed across
words proportionally to their phoneme counts, then snapped to the nearest low-energy gap.
"""
import json, re, sys, os
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

MODEL = "/opt/tts/kokoro-v1.0.onnx"
VOICES = "/opt/tts/voices-v1.0.bin"
SR = 24000


def voiced_span(x, thr_db=-38):
    win = int(0.01 * SR)
    n = len(x) // win
    if n == 0:
        return 0, len(x)
    e = np.sqrt((x[: n * win].reshape(n, win) ** 2).mean(1) + 1e-12)
    db = 20 * np.log10(e / (np.abs(x).max() + 1e-9))
    idx = np.where(db > thr_db)[0]
    if len(idx) == 0:
        return 0, len(x)
    return idx[0] * win, min(len(x), (idx[-1] + 1) * win)


def energy_env(x):
    win = int(0.01 * SR)
    n = len(x) // win
    return np.sqrt((x[: n * win].reshape(n, win) ** 2).mean(1) + 1e-12), win


def word_weights(k, words):
    w = []
    for word in words:
        clean = re.sub(r"[^\w'\-]", "", word)
        if not clean:
            w.append(0.5)
            continue
        if re.fullmatch(r"[\d,\.]+", clean):  # numbers are spoken long
            w.append(3.0 * len(clean.replace(",", "")))
            continue
        try:
            ph = k.tokenizer.phonemize(clean, "en-us")
            w.append(max(1.0, len(ph.replace(" ", ""))))
        except Exception:
            w.append(max(1.0, len(clean) * 0.8))
    return np.array(w, dtype=float)


def synth(script, out_dir):
    k = Kokoro(MODEL, VOICES)
    voice = script.get("voice", "am_michael")
    speed = float(script.get("speed", 1.0))
    os.makedirs(out_dir, exist_ok=True)
    chunks, lines_out, t = [], [], float(script.get("lead_in", 0.15))
    chunks.append(np.zeros(int(t * SR), dtype=np.float32))
    for ln in script["lines"]:
        text = ln["text"].strip()
        audio, sr = k.create(text, voice=ln.get("voice", voice), speed=ln.get("speed", speed), lang="en-us")
        assert sr == SR
        a, b = voiced_span(audio)
        audio = audio[max(0, a - int(0.03 * SR)): b + int(0.06 * SR)]
        a2, b2 = voiced_span(audio)
        words = text.split()
        wts = word_weights(k, words)
        span = (b2 - a2) / SR
        cum = np.concatenate([[0], np.cumsum(wts)]) / wts.sum() * span + a2 / SR
        # snap internal boundaries to local energy minima (+-60 ms)
        env, win = energy_env(audio)
        for i in range(1, len(cum) - 1):
            c = int(cum[i] * SR / win)
            lo, hi = max(0, c - 6), min(len(env), c + 7)
            if hi > lo:
                cum[i] = (lo + int(np.argmin(env[lo:hi]))) * win / SR
        cum = np.maximum.accumulate(cum)
        wl = [{"w": w, "start": round(t + cum[i], 3), "end": round(t + cum[i + 1], 3)} for i, w in enumerate(words)]
        dur = len(audio) / SR
        lines_out.append({"id": ln.get("id"), "start": round(t, 3), "end": round(t + dur, 3), "text": text, "words": wl})
        chunks.append(audio.astype(np.float32))
        pause = float(ln.get("pause_after", 0.22))
        chunks.append(np.zeros(int(pause * SR), dtype=np.float32))
        t += dur + pause
    tail = float(script.get("tail", 0.6))
    chunks.append(np.zeros(int(tail * SR), dtype=np.float32))
    y = np.concatenate(chunks)
    y = y / (np.abs(y).max() + 1e-9) * 0.89
    sf.write(os.path.join(out_dir, "narration.wav"), y, SR)
    res = {"duration": round(len(y) / SR, 3), "voice": voice, "lines": lines_out}
    with open(os.path.join(out_dir, "timings.json"), "w") as f:
        json.dump(res, f, indent=1)
    return res


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        sc = json.load(f)
    r = synth(sc, sys.argv[2])
    print("narration", r["duration"], "s,", len(r["lines"]), "lines")
