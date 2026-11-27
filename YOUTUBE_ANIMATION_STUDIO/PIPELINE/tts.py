"""Narration synthesis with word-level timings (Kokoro neural TTS).

Usage: /opt/ttsenv/bin/python tts.py <script.json> <out_dir> [--ref <timings_ref.json>]
  --ref: timing-lock mode (re-voice without changing line start times / shot timing; see synth()).
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


def render_line(k, text, voice, speed):
    """Synthesise one line and trim it to the voiced span (+30 ms lead, +60 ms tail)."""
    audio, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
    assert sr == SR
    a, b = voiced_span(audio)
    return audio[max(0, a - int(0.03 * SR)): b + int(0.06 * SR)].astype(np.float32)


def word_times(k, text, audio, t):
    """Word timings inside a trimmed line clip that starts at absolute time t."""
    a2, b2 = voiced_span(audio)
    words = text.split()
    wts = word_weights(k, words)
    span = (b2 - a2) / SR
    cum = np.concatenate([[0], np.cumsum(wts)]) / wts.sum() * span + a2 / SR
    env, win = energy_env(audio)  # snap internal boundaries to local energy minima (+-60 ms)
    for i in range(1, len(cum) - 1):
        c = int(cum[i] * SR / win)
        lo, hi = max(0, c - 6), min(len(env), c + 7)
        if hi > lo:
            cum[i] = (lo + int(np.argmin(env[lo:hi]))) * win / SR
    cum = np.maximum.accumulate(cum)
    return [{"w": w, "start": round(t + cum[i], 3), "end": round(t + cum[i + 1], 3)} for i, w in enumerate(words)]


def synth(script, out_dir, ref=None):
    """Natural mode (ref=None): lines are laid end to end with their pauses.
    Timing-lock mode (ref = an earlier timings dict): every line is re-synthesised (e.g. in a new voice) at a speed
    fitted to the reference line's duration and placed at the reference start time, so shot timings, rendered
    frames and overlay cue times stay valid. Lines missing from the reference fall back to natural placement."""
    k = Kokoro(MODEL, VOICES)
    voice = script.get("voice", "am_adam")
    speed = float(script.get("speed", 1.0))
    os.makedirs(out_dir, exist_ok=True)
    lines = script["lines"]
    lines_out, fit_log = [], []
    if ref is None:
        chunks, t = [], float(script.get("lead_in", 0.15))
        chunks.append(np.zeros(int(t * SR), dtype=np.float32))
        for ln in lines:
            text = ln["text"].strip()
            audio = render_line(k, text, ln.get("voice", voice), ln.get("speed", speed))
            dur = len(audio) / SR
            lines_out.append({"id": ln.get("id"), "start": round(t, 3), "end": round(t + dur, 3), "text": text,
                              "words": word_times(k, text, audio, t)})
            chunks.append(audio)
            pause = float(ln.get("pause_after", 0.22))
            chunks.append(np.zeros(int(pause * SR), dtype=np.float32))
            t += dur + pause
        chunks.append(np.zeros(int(float(script.get("tail", 0.6)) * SR), dtype=np.float32))
        y = np.concatenate(chunks)
    else:
        rl = ref["lines"]
        rid = {r["id"]: i for i, r in enumerate(rl)}
        total = float(ref["duration"])
        y = np.zeros(int(total * SR) + 2 * SR, dtype=np.float32)
        prev_end = -1.0
        for ln in lines:
            text = ln["text"].strip()
            i = rid.get(ln.get("id"))
            if i is None:
                raise SystemExit(f"line {ln.get('id')} not in timing reference; re-time this video (tts --retime)")
            r = rl[i]
            # keep the reference start; only slide later if the previous (speed-clamped) line is still speaking
            t0 = max(r["start"], prev_end + 0.05)
            target = r["end"] - r["start"] - (t0 - r["start"])
            nxt = rl[i + 1]["start"] if i + 1 < len(rl) else total
            gap = max(0.0, nxt - r["end"])
            hi = target + 0.02 + min(0.08, max(0.0, gap - 0.06))
            lo = target - 0.14
            sp = float(ln.get("speed", speed))
            audio = render_line(k, text, voice, sp)
            d = len(audio) / SR
            for _ in range(5):
                if lo <= d <= hi:
                    break
                # clamp: below ~0.90 the read drags (line simply ends a little early instead); above 1.30 it sounds rushed
                sp2 = min(1.30, max(0.90, sp * d / max(0.2, target - 0.04)))
                if abs(sp2 - sp) < 1e-3:
                    break
                sp = sp2
                audio = render_line(k, text, voice, sp)
                d = len(audio) / SR
            over = (t0 + d) - nxt + 0.02  # overrun into the next line's slot (that line then starts late)
            prev_end = t0 + d
            fit_log.append({"id": ln.get("id"), "speed": round(sp, 3), "target": round(target, 3), "dur": round(d, 3),
                            "overrun": round(max(0.0, over), 3)})
            a = int(t0 * SR)
            y[a: a + len(audio)] += audio[: max(0, len(y) - a)]
            lines_out.append({"id": ln.get("id"), "start": round(t0, 3), "end": round(t0 + d, 3), "text": text,
                              "words": word_times(k, text, audio, t0)})
        y = y[: int(total * SR)]
    y = y / (np.abs(y).max() + 1e-9) * 0.89
    sf.write(os.path.join(out_dir, "narration.wav"), y, SR)
    res = {"duration": round(len(y) / SR, 3), "voice": voice, "lines": lines_out}
    if ref is not None:
        res["duration"] = ref["duration"]
        res["timing_locked"] = True
        res["fit"] = fit_log
    with open(os.path.join(out_dir, "timings.json"), "w") as f:
        json.dump(res, f, indent=1)
    return res


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        sc = json.load(f)
    ref = None
    if "--ref" in sys.argv:
        with open(sys.argv[sys.argv.index("--ref") + 1]) as f:
            ref = json.load(f)
    r = synth(sc, sys.argv[2], ref)
    msg = f"narration {r['duration']} s, {len(r['lines'])} lines, voice {r['voice']}"
    if r.get("fit"):
        sp = [x["speed"] for x in r["fit"]]
        bad = [x for x in r["fit"] if x["overrun"] > 0.03]
        msg += f" | timing-locked: speed {min(sp):.2f}-{max(sp):.2f} (median {sorted(sp)[len(sp)//2]:.2f})"
        if bad:
            msg += f" | CHECK {[(x['id'], x['speed'], x['overrun']) for x in bad]}"
    print(msg)
