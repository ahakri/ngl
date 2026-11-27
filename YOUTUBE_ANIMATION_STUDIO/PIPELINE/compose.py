"""Final assembly: rendered shot frames -> graded, upscaled 1080x1920 frames + overlays + transitions,
word-synced captions (ASS via libass), mixed audio -> H.264 MP4.

Usage: python3 compose.py <ID> [--preview]   (run from studio root)
"""
import json, os, sys, subprocess, math, glob, re
import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
import overlays as OV
import audio as AU

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 24

GRADES = {  # gain RGB, lift RGB, saturation, contrast, vignette, grain
    "cave": dict(gain=(0.92, 1.02, 1.05), lift=(0.0, 0.008, 0.012), sat=0.9, con=1.08, vig=0.55, grain=0.035),
    "scuba": dict(gain=(0.9, 1.02, 1.08), lift=(0.0, 0.01, 0.02), sat=1.08, con=1.05, vig=0.35, grain=0.025),
    "murder": dict(gain=(1.0, 0.97, 0.96), lift=(0.01, 0.01, 0.015), sat=0.72, con=1.12, vig=0.5, grain=0.04),
    "haunted": dict(gain=(0.95, 1.0, 0.95), lift=(0.008, 0.012, 0.01), sat=0.6, con=1.1, vig=0.6, grain=0.045),
}
_vig = None


def vignette_mask(strength):
    global _vig
    if _vig is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
        _vig = r
    return (1 - strength * np.clip(_vig - 0.25, 0, 1) ** 1.6)[..., None]


def grade(arr, mood, rng):
    g = GRADES[mood]
    x = arr.astype(np.float32) / 255.0
    x = x * np.array(g["gain"], np.float32) + np.array(g["lift"], np.float32)
    lum = (x * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
    x = lum + (x - lum) * g["sat"]
    x = (x - 0.5) * g["con"] + 0.5
    x = x * vignette_mask(g["vig"])
    noise = rng.standard_normal((H // 2, W // 2, 1)).astype(np.float32)
    noise = np.repeat(np.repeat(noise, 2, 0), 2, 1)
    x = x + noise * g["grain"] * (0.6 + 0.4 * (1 - lum))
    return (np.clip(x, 0, 1) * 255).astype(np.uint8)


def shot_frame(id_, shot, k, cache):
    d = os.path.join(ROOT, "RENDERS", id_, shot)
    files = cache.get(shot)
    if files is None:
        files = sorted(glob.glob(os.path.join(d, "*.png")))
        cache[shot] = files
    if not files:
        return Image.new("RGB", (W, H), (0, 0, 0))
    im = Image.open(files[min(k, len(files) - 1)]).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    return im


CAP_TOP, CAP_BOT = 1150, 1340  # caption band (captions centred at y=1240)


def avoid_captions(o):
    """Shift an overlay frame up if its visible pixels intrude into the caption band."""
    bb = o.getbbox()
    if not bb or bb[3] <= CAP_TOP or bb[1] >= CAP_BOT:
        return o
    shift = bb[3] - (CAP_TOP - 20)
    shift = min(shift, max(0, bb[1] - 110))  # never push above the top safe margin
    if shift <= 0:
        return o
    out = Image.new("RGBA", o.size, (0, 0, 0, 0))
    out.alpha_composite(o.crop((0, shift, o.width, o.height)), (0, 0))
    return out


def ass_time(t):
    t = max(0, t)
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_captions(timings, script, path, mood):
    acc = OV.ACCENT.get(mood, (255, 220, 60))
    hl = "&H004DE1FF"  # yellow (BGR)
    accent = f"&H00{acc[2]:02X}{acc[1]:02X}{acc[0]:02X}"
    emph = set()
    for ln in script["lines"]:
        for w in ln.get("emphasis", []):
            emph.add(re.sub(r"[^\w]", "", w.lower()))
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Anton,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,7,3,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for ln in timings["lines"]:
        words = ln["words"]
        groups, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= 3 or re.search(r"[\.\,\?\!\;\:]$", w["w"]) or (len(" ".join(x["w"] for x in cur)) > 14 and len(cur) >= 2):
                groups.append(cur)
                cur = []
        if cur:
            groups.append(cur)
        for gi, g in enumerate(groups):
            g_end = groups[gi + 1][0]["start"] if gi + 1 < len(groups) else g[-1]["end"] + 0.15
            for wi, w in enumerate(g):
                st = w["start"]
                en = g[wi + 1]["start"] if wi + 1 < len(g) else g_end
                parts = []
                for wj, w2 in enumerate(g):
                    txt = w2["w"].upper().replace("{", "").replace("}", "")
                    key = re.sub(r"[^\w]", "", w2["w"].lower())
                    col = accent if key in emph else ("&H00FFFFFF")
                    if wj == wi:
                        col = hl if key not in emph else accent
                        parts.append(f"{{\\c{col}\\fscx108\\fscy108}}{txt}{{\\fscx100\\fscy100}}")
                    else:
                        parts.append(f"{{\\c{col}}}{txt}")
                pop = "{\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}" if wi == 0 else ""
                ev.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Cap,,0,0,0,,{{\\pos({W // 2},1240)}}{pop}" + " ".join(parts))
    with open(path, "w") as f:
        f.write(head + "\n".join(ev) + "\n")


def compose(id_, preview=False, until=None):
    sdir = os.path.join(ROOT, "SCRIPTS", id_)
    adir = os.path.join(ROOT, "AUDIO", id_)
    script = json.load(open(os.path.join(sdir, "script.json")))
    timings = json.load(open(os.path.join(adir, "timings.json")))
    st = json.load(open(os.path.join(adir, "shot_timing.json")))
    mood = script.get("mood", script.get("category", "cave"))
    dur = st["duration"]
    nfr = int(math.ceil(dur * FPS))
    if until:
        nfr = min(nfr, int(until * FPS))
    # audio mix
    sfx_events = []
    for sh in script["shots"]:
        t0 = st["shots"][sh["id"]]["start"]
        for e in sh.get("sfx", []):
            if e.get("name") in AU.SFX:
                ev = {"name": e["name"], "at": t0 + float(e.get("offset", 0)), "gain": float(e.get("gain", 0.5))}
                if e.get("args"):
                    ev["args"] = e["args"]
                sfx_events.append(ev)
    curve = script.get("music_curve")
    mix_path = os.path.join(adir, "mix.wav")
    AU.mix(dur, os.path.join(adir, "narration.wav"), mood, sfx_events, music_curve=curve, seed=hash(id_) % 1000, out=mix_path)
    ass = os.path.join(adir, "captions.ass")
    build_captions(timings, script, ass, mood)
    out_dir = os.path.join(ROOT, "FINAL_VIDEOS")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{id_}{'_preview' if preview else ''}.mp4")
    vf = f"ass={ass}:fontsdir={os.path.join(os.path.dirname(__file__), 'fonts')}"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", mix_path, "-vf", vf, "-c:v", "libx264", "-preset", "medium" if not preview else "veryfast", "-crf", "20" if not preview else "28",
           "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-t", f"{nfr / FPS:.3f}", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    rng = np.random.default_rng(1)
    cache = {}
    order = [s["id"] for s in script["shots"]]
    sh_by = {s["id"]: s for s in script["shots"]}
    for f in range(nfr):
        t = f / FPS
        cur = order[0]
        for sid in order:
            if st["shots"][sid]["start"] <= t + 1e-6:
                cur = sid
        s0 = st["shots"][cur]["start"]
        sdur = st["shots"][cur]["duration"]
        k = int(round((t - s0) * FPS))
        im = shot_frame(id_, cur, k, cache)
        arr = grade(np.asarray(im), mood, rng)
        # transitions
        tr = sh_by[cur].get("transition_in", "cut")
        lt = t - s0
        if tr == "fade_black" and lt < 0.4:
            arr = (arr.astype(np.float32) * (lt / 0.4)).astype(np.uint8)
        elif tr == "flash" and lt < 0.12:
            a = 1 - lt / 0.12
            arr = (arr.astype(np.float32) * (1 - a) + 255 * a).astype(np.uint8)
        elif tr == "whip" and lt < 0.18:
            sh = int((1 - lt / 0.18) * 260)
            arr = np.roll(arr, sh, axis=1)
            arr = ((arr.astype(np.float32) + np.roll(arr, 40, 1) + np.roll(arr, 80, 1)) / 3).astype(np.uint8)
        if f >= nfr - int(0.35 * FPS) and not script.get("loop_line"):
            a = (nfr - f) / (0.35 * FPS)
            arr = (arr.astype(np.float32) * a).astype(np.uint8)
        im = Image.fromarray(arr).convert("RGBA")
        for ov in sh_by[cur].get("overlay", []):
            o = OV.render_overlay(ov, lt, sdur, mood)
            if o is not None:
                im.alpha_composite(avoid_captions(o))
        p.stdin.write(im.convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    return out


if __name__ == "__main__":
    u = float(sys.argv[sys.argv.index("--until") + 1]) if "--until" in sys.argv else None
    print(compose(sys.argv[1], preview="--preview" in sys.argv, until=u))
