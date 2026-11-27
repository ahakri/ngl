"""Procedural, fully original music beds and sound effects (no samples, no licensed audio).

All functions return float32 numpy arrays at SR=48000 (mono unless noted).
CLI: python3 audio.py build-library <out_dir>   -> renders SFX library wavs for preview/QC.
"""
import numpy as np, wave, os, sys, json

SR = 48000
rng = np.random.default_rng(7)


def t_arr(d):
    return np.arange(int(d * SR)) / SR


def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    s_len = max(0, n - a - d - r)
    e = np.concatenate([np.linspace(0, 1, a, False), np.linspace(1, s, d, False), np.full(s_len, s), np.linspace(s, 0, r)])
    return np.pad(e, (0, max(0, n - len(e))))[:n]


def lowpass(x, fc):
    """One-pole cascaded x4 lowpass (cheap, smooth)."""
    a = np.exp(-2 * np.pi * fc / SR)
    y = x.astype(np.float64)
    for _ in range(4):
        out = np.empty_like(y)
        acc = 0.0
        # vectorised IIR via lfilter-like recursion
        b0 = 1 - a
        for i in range(len(y)):
            acc = b0 * y[i] + a * acc
            out[i] = acc
        y = out
    return y.astype(np.float32)


def fft_filter(x, lo=0, hi=None, tilt=0.0):
    """Zero-phase band filter in the frequency domain (fast for offline rendering)."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f)
    if lo:
        m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi:
        m *= 1 / (1 + (f / hi) ** 4)
    if tilt:
        m *= (np.maximum(f, 20) / 1000.0) ** tilt
    return np.fft.irfft(X * m, n).astype(np.float32)


def noise(d):
    return rng.standard_normal(int(d * SR)).astype(np.float32)


def norm(x, peak=0.9):
    m = np.abs(x).max()
    return (x / m * peak).astype(np.float32) if m > 0 else x


def fade(x, fi=0.01, fo=0.05):
    x = x.copy()
    a, b = int(fi * SR), int(fo * SR)
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def simple_reverb(x, room=0.6, decay=2.2, wet=0.35):
    """Convolution with synthetic exponentially decaying noise IR."""
    ir_len = int(decay * SR)
    ir = rng.standard_normal(ir_len).astype(np.float32) * np.exp(-np.linspace(0, 6.9 / room * 0.6, ir_len)).astype(np.float32)
    ir = fft_filter(ir, lo=120, hi=6000)
    ir /= np.sqrt((ir ** 2).sum())
    n = len(x) + ir_len
    nfft = 1 << (n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]
    return ((1 - wet) * x + wet * y * 0.5).astype(np.float32)

# ----------------------------------------------------------------------------- SFX

def sfx_bubbles(d=1.5, density=18, pitch=1.0):
    y = np.zeros(int(d * SR), np.float32)
    for _ in range(int(density * d)):
        st = rng.integers(0, max(1, len(y) - 4000))
        dur = rng.uniform(0.02, 0.08)
        tt = t_arr(dur)
        f0 = rng.uniform(300, 1400) * pitch
        f = f0 * (1 + 2.5 * tt / dur)  # rising chirp = bubble
        b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / (dur * 0.35))
        e = min(len(y), st + len(b)); y[st:e] += b[: e - st].astype(np.float32) * rng.uniform(0.2, 0.7)
    return fade(norm(y, 0.7))


def sfx_breath_cycle(inhale=1.1, exhale=1.6, gap=0.2, depth=1.0):
    """Regulator breathing: hissy inhale through 2nd stage, bubbly exhale."""
    a = noise(inhale)
    a = fft_filter(a, lo=1500, hi=7000) * env_adsr(len(a), 0.15, 0.2, 0.8, 0.3)
    hiss = np.sin(2 * np.pi * 3400 * t_arr(inhale)) * 0.04 * env_adsr(len(a), 0.2, 0.1, 0.8, 0.3)
    inh = a * 0.5 + hiss
    ex = fft_filter(noise(exhale), lo=100, hi=1200) * env_adsr(int(exhale * SR), 0.05, 0.3, 0.6, 0.5) * 0.6
    ex = ex + sfx_bubbles(exhale, density=40, pitch=0.6) * 0.8
    y = np.concatenate([inh, np.zeros(int(gap * SR), np.float32), ex, np.zeros(int(gap * SR), np.float32)])
    return norm(y, 0.6 * depth)


def sfx_heartbeat(bpm=70, d=4.0):
    y = np.zeros(int(d * SR), np.float32)
    per = 60 / bpm
    k = 0
    while k * per < d:
        for off, amp in ((0, 1.0), (0.18, 0.7)):
            st = int((k * per + off) * SR)
            tt = t_arr(0.15)
            b = np.sin(2 * np.pi * (55 - 60 * tt) * tt) * np.exp(-tt * 28) * amp
            y[st: st + len(b)] += b[: max(0, len(y) - st)]
        k += 1
    return norm(fft_filter(y, hi=200), 0.9)


def sfx_boom(d=3.0, f0=45):
    tt = t_arr(d)
    tone = np.sin(2 * np.pi * (f0 + 40 * np.exp(-tt * 6)) * tt) * np.exp(-tt * 1.6)
    nz = fft_filter(noise(d), hi=400) * np.exp(-tt * 3) * 0.6
    return norm(simple_reverb((tone + nz).astype(np.float32), decay=2.5, wet=0.3), 0.95)


def sfx_hit(d=1.2):
    """Short cinematic impact (sub + transient)."""
    tt = t_arr(d)
    sub = np.sin(2 * np.pi * (60 * np.exp(-tt * 3) + 30) * tt) * np.exp(-tt * 4)
    tr = fft_filter(noise(d), lo=800) * np.exp(-tt * 60)
    return norm((sub + tr * 0.6).astype(np.float32), 0.95)


def sfx_whoosh(d=0.9, up=True):
    n = noise(d)
    tt = t_arr(d)
    e = np.sin(np.pi * tt / d) ** 2
    x = fft_filter(n, lo=300, hi=5000) * e
    return fade(norm(x.astype(np.float32), 0.6), 0.01, 0.1)


def sfx_riser(d=3.0):
    tt = t_arr(d)
    f = 80 * (2 ** (tt / d * 3))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * (tt / d) ** 2
    nz = fft_filter(noise(d), lo=2000) * (tt / d) ** 3 * 0.5
    return norm((tone * 0.5 + nz).astype(np.float32), 0.7)


def sfx_rumble(d=5.0):
    x = fft_filter(noise(d), lo=20, hi=120)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * t_arr(d))
    return fade(norm(x * lfo, 0.8), 0.5, 1.0)


def sfx_creak(d=1.6, f0=180):
    tt = t_arr(d)
    f = f0 + 60 * np.sin(2 * np.pi * 0.7 * tt) + 30 * rng.standard_normal(len(tt)).cumsum() / SR * 30
    pulses = (np.sin(2 * np.pi * np.cumsum(f) / SR) > 0.97).astype(np.float32)
    x = fft_filter(pulses, lo=200, hi=3000) * env_adsr(len(tt), 0.1, 0.2, 0.8, 0.4)
    return norm(simple_reverb(x, decay=1.5, wet=0.4), 0.7)


def sfx_static(d=1.0):
    x = fft_filter(noise(d), lo=800, hi=9000)
    crack = (rng.random(len(x)) > 0.998).astype(np.float32) * 3
    return norm((x * 0.5 + crack).astype(np.float32), 0.6)


def sfx_thunder(d=5.0):
    tt = t_arr(d)
    cr = fft_filter(noise(d), lo=200, hi=4000) * np.exp(-tt * 8)
    rb = fft_filter(noise(d), hi=180) * np.exp(-tt * 0.8)
    return norm(simple_reverb((cr * 0.6 + rb).astype(np.float32), decay=3, wet=0.4), 0.95)


def sfx_footsteps(n=6, interval=0.55, surface="wood"):
    d = n * interval + 0.5
    y = np.zeros(int(d * SR), np.float32)
    for k in range(n):
        st = int((k * interval + rng.uniform(-0.03, 0.03)) * SR)
        tt = t_arr(0.12)
        hi = 3000 if surface == "gravel" else 1500
        b = fft_filter(noise(0.12), lo=80, hi=hi) * np.exp(-tt * 40)
        b += np.sin(2 * np.pi * 90 * tt) * np.exp(-tt * 30) * 0.5
        st = max(0, st); e = min(len(y), st + len(b)); y[st:e] += b[: e - st] * rng.uniform(0.6, 1.0)
    return norm(simple_reverb(y, decay=1.0, wet=0.25), 0.6)


def sfx_door_creak(d=2.2):
    return sfx_creak(d, f0=120)


def sfx_click(d=0.08):
    tt = t_arr(d)
    return norm((fft_filter(noise(d), lo=2000) * np.exp(-tt * 200)).astype(np.float32), 0.6)


def sfx_typewriter(n=12, interval=0.07):
    y = np.zeros(int((n * interval + 0.2) * SR), np.float32)
    for k in range(n):
        c = sfx_click()
        st = int(k * interval * SR)
        e = min(len(y), st + len(c)); y[st:e] += c[: e - st] * rng.uniform(0.4, 0.8)
    return y


def sfx_underwater_amb(d=10.0):
    x = fft_filter(noise(d), lo=30, hi=500)
    lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.11 * t_arr(d))
    b = sfx_bubbles(d, density=1.5, pitch=0.5) * 0.3
    return fade(norm((x * lfo + b).astype(np.float32), 0.5), 1.0, 1.0)


def sfx_wind(d=10.0):
    x = fft_filter(noise(d), lo=200, hi=1500)
    lfo = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 0.07 * t_arr(d) + 1)) ** 2
    return fade(norm((x * lfo).astype(np.float32), 0.5), 1.0, 1.0)


def sfx_metal_groan(d=3.0):
    tt = t_arr(d)
    f = 70 + 25 * np.sin(2 * np.pi * 0.4 * tt) + 10 * np.sin(2 * np.pi * 3.1 * tt)
    tone = sum(np.sin(2 * np.pi * np.cumsum(f * k) / SR) / k for k in (1, 2.03, 3.1, 4.4))
    x = tone * env_adsr(len(tt), 0.5, 0.3, 0.8, 0.8)
    return norm(simple_reverb(fft_filter(x.astype(np.float32), hi=1200), decay=3, wet=0.5), 0.8)


def sfx_sonar_ping(d=2.5):
    tt = t_arr(d)
    x = np.sin(2 * np.pi * 1450 * tt) * np.exp(-tt * 3)
    return norm(simple_reverb(x.astype(np.float32), decay=2.0, wet=0.5), 0.6)


def sfx_tone_sting(d=2.5, f=110, dissonant=True):
    """Musical sting: low cluster stab."""
    tt = t_arr(d)
    fs = [f, f * 1.5, f * (1.06 if dissonant else 2)]
    x = sum(np.sin(2 * np.pi * ff * tt) for ff in fs) * np.exp(-tt * 1.2)
    return norm(simple_reverb(x.astype(np.float32), decay=2.5, wet=0.45), 0.8)


SFX = {
    "bubbles": sfx_bubbles, "breath": sfx_breath_cycle, "heartbeat": sfx_heartbeat, "boom": sfx_boom, "hit": sfx_hit,
    "whoosh": sfx_whoosh, "riser": sfx_riser, "rumble": sfx_rumble, "creak": sfx_creak, "static": sfx_static,
    "thunder": sfx_thunder, "footsteps": sfx_footsteps, "door_creak": sfx_door_creak, "click": sfx_click,
    "typewriter": sfx_typewriter, "underwater_amb": sfx_underwater_amb, "wind": sfx_wind, "metal_groan": sfx_metal_groan,
    "sonar": sfx_sonar_ping, "sting": sfx_tone_sting,
}

# ----------------------------------------------------------------------------- music

SCALES = {"minor": [0, 2, 3, 5, 7, 8, 10], "phrygian": [0, 1, 3, 5, 7, 8, 10], "dorian": [0, 2, 3, 5, 7, 9, 10]}


def pad_voice(freq, d, detune=0.004, bright=1500):
    tt = t_arr(d)
    x = np.zeros(len(tt), np.float32)
    for dt in (-detune, 0, detune):
        f = freq * (1 + dt)
        saw = 2 * ((tt * f) % 1) - 1
        x += saw.astype(np.float32)
    return fft_filter(x / 3, hi=bright)


def music_bed(duration, mood="cave", seed=1, intensity_curve=None):
    """Evolving dark ambient score. mood in {cave, scuba, murder, haunted}.
    intensity_curve: list of (time_s, 0..1) to shape tension (filter + pulse level)."""
    global rng
    rng = np.random.default_rng(seed)
    cfg = {
        "cave": dict(root=41.2, scale="phrygian", bright=900, pulse_bpm=0, chord_len=8, shimmer=0.15),
        "scuba": dict(root=55.0, scale="dorian", bright=2200, pulse_bpm=0, chord_len=6, shimmer=0.35),
        "murder": dict(root=49.0, scale="minor", bright=1400, pulse_bpm=96, chord_len=4, shimmer=0.1),
        "haunted": dict(root=46.25, scale="phrygian", bright=1100, pulse_bpm=0, chord_len=7, shimmer=0.25),
    }[mood]
    d = duration + 1.0
    n = int(d * SR)
    y = np.zeros(n, np.float32)
    sc = SCALES[cfg["scale"]]
    prog = [0, 5, 3, 6] if mood != "murder" else [0, 5, 6, 4]
    L = cfg["chord_len"]
    k = 0
    while k * L < d:
        deg = prog[k % len(prog)]
        notes = [sc[deg % 7] + 12 * (deg // 7), sc[(deg + 2) % 7] + 12 * ((deg + 2) // 7), sc[(deg + 4) % 7] + 12 * ((deg + 4) // 7)]
        seg = min(L + 2.0, d - k * L)
        st = int(k * L * SR)
        chord = np.zeros(int(seg * SR), np.float32)
        for i, nt in enumerate(notes):
            f = cfg["root"] * 2 ** ((nt + 12 * (1 + (i > 0))) / 12)
            chord += pad_voice(f, seg, bright=cfg["bright"]) * (0.5 if i else 0.7)
        chord *= env_adsr(len(chord), 1.5, 0.5, 0.85, 2.0)
        y[st: st + len(chord)] += chord[: n - st]
        k += 1
    # sub drone
    tt = t_arr(d)
    y += (np.sin(2 * np.pi * cfg["root"] * tt) * 0.5).astype(np.float32)
    # shimmer (high filtered noise swells)
    sh = fft_filter(noise(d), lo=3000, hi=9000) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * tt)) * cfg["shimmer"]
    y += sh.astype(np.float32)
    # intensity envelope
    inten = np.ones(n, np.float32) * 0.6
    if intensity_curve:
        xs = [p[0] for p in intensity_curve]
        ys = [p[1] for p in intensity_curve]
        inten = np.interp(tt, xs, ys).astype(np.float32)
    # tension pulse (murder: ticking bass; others: slow heartbeat-like pulses at high intensity)
    if cfg["pulse_bpm"]:
        per = 60 / cfg["pulse_bpm"]
        pulse = np.zeros(n, np.float32)
        j = 0
        while j * per < d:
            s0 = int(j * per * SR)
            seg_t = t_arr(0.25)
            b = np.sin(2 * np.pi * cfg["root"] * 2 * seg_t) * np.exp(-seg_t * 14)
            pulse[s0: s0 + len(b)] += b[: n - s0].astype(np.float32)
            j += 1
        y += pulse * 0.6 * inten
    else:
        hb = sfx_heartbeat(bpm=58, d=d) * 0.35
        hb = np.pad(hb, (0, max(0, n - len(hb))))[:n]
        y += hb * np.clip((inten - 0.55) * 2.5, 0, 1)
    y = y * (0.55 + 0.45 * inten)
    y = simple_reverb(y, decay=3.5, wet=0.35)
    return fade(norm(y, 0.8), 1.5, 2.0)[: int(duration * SR)]

# ----------------------------------------------------------------------------- mixing

def place(track, clip, at, gain=1.0):
    st = int(at * SR)
    if st >= len(track):
        return
    e = min(len(track), st + len(clip))
    track[st:e] += clip[: e - st] * gain


def read_wav(path):
    with wave.open(path) as w:
        sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
        x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(1)
    if sr != SR:
        idx = np.arange(0, len(x), sr / SR)
        x = np.interp(idx, np.arange(len(x)), x).astype(np.float32)
    return x


def write_wav(path, x, stereo=None):
    x = np.clip(x, -1, 1)
    if stereo is not None:
        data = np.stack([x, stereo], 1)
        ch = 2
    else:
        data = x
        ch = 1
    with wave.open(path, "w") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((data * 32767).astype(np.int16).tobytes())


def mix(duration, narration_wav, mood, sfx_events, music_curve=None, seed=1, music_gain=0.32, out=None):
    """sfx_events: list of {"name", "at", "gain", "args"}. Ducks music under narration."""
    n = int(duration * SR)
    narr = read_wav(narration_wav)
    narr = np.pad(narr, (0, max(0, n - len(narr))))[:n]
    mus = music_bed(duration, mood, seed=seed, intensity_curve=music_curve)
    mus = np.pad(mus, (0, max(0, n - len(mus))))[:n]
    # sidechain-style duck from narration envelope
    win = int(0.05 * SR)
    envn = np.convolve(np.abs(narr), np.ones(win) / win, mode="same")
    duck = 1 - 0.55 * np.clip(envn / (envn.max() + 1e-9) * 4, 0, 1)
    duck = np.convolve(duck, np.ones(int(0.2 * SR)) / int(0.2 * SR), mode="same")
    sfx = np.zeros(n, np.float32)
    for ev in sfx_events:
        fn = SFX[ev["name"]]
        clip = fn(**ev.get("args", {}))
        place(sfx, clip, ev["at"], ev.get("gain", 0.6))
    L = narr * 1.0 + mus * music_gain * duck + sfx * 0.8
    # gentle stereo width: decorrelate music/sfx slightly
    R = narr * 1.0 + np.roll(mus, int(0.012 * SR)) * music_gain * duck + np.roll(sfx, int(0.006 * SR)) * 0.8
    peak = max(np.abs(L).max(), np.abs(R).max())
    L, R = L / peak * 0.92, R / peak * 0.92
    if out:
        write_wav(out, L.astype(np.float32), R.astype(np.float32))
    return L, R


if __name__ == "__main__":
    if sys.argv[1] == "build-library":
        od = sys.argv[2]
        os.makedirs(od, exist_ok=True)
        for k, fn in SFX.items():
            write_wav(os.path.join(od, f"{k}.wav"), fn())
        for mood in ("cave", "scuba", "murder", "haunted"):
            write_wav(os.path.join(od, f"music_{mood}.wav"), music_bed(30, mood, intensity_curve=[(0, 0.4), (20, 1.0), (30, 0.6)]))
        print("library written to", od)
