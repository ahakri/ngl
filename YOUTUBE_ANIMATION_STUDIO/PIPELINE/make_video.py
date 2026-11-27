"""Orchestrates one Short end-to-end, resumable (skips finished stages/frames).
Usage: python3 make_video.py <ID> [tts|timing|preview|render|compose|all] [--res 540] [--retime]
  tts: narrates in the studio voice (studio_config.json); timing-locked if AUDIO/<ID>/timings_ref.json exists.
  preview: renders 3 stills per shot at 270x480 -> QUALITY_CONTROL/<ID>/contact_sheet.png
"""
import json, os, sys, subprocess, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FPS = 24
BPY = "/opt/bpyenv/bin/python"
TTSPY = "/opt/ttsenv/bin/python"


def P(*a):
    return os.path.join(ROOT, *a)


def studio_cfg():
    cfg = os.path.join(HERE, "studio_config.json")
    return json.load(open(cfg)) if os.path.exists(cfg) else {}


def studio_voice(default=None):
    """Single source of truth for the channel narrator (PIPELINE/studio_config.json)."""
    return studio_cfg().get("voice") or default


def tts(id_, retime=False):
    """Narrate a script in the studio voice.
    If AUDIO/<ID>/timings_ref.json exists the narration is timing-locked to it (line starts and shot timing unchanged,
    so rendered frames, shots.py animation and overlay cue times stay valid). `retime=True` drops the lock and lays the
    lines out naturally (then shots must be re-previewed/re-rendered)."""
    sc = json.load(open(P("SCRIPTS", id_, "script.json")))
    adir = P("AUDIO", id_)
    os.makedirs(adir, exist_ok=True)
    ns = studio_cfg().get("natural_speed") or {}
    base = ns.get(id_.split("-")[0]) if isinstance(ns, dict) else ns
    tj = {"voice": studio_voice(sc.get("voice", "am_adam")), "speed": base or sc.get("speed", 1.0), "lines": sc["lines"]}
    json.dump(tj, open(os.path.join(adir, "tts_input.json"), "w"))
    ref = os.path.join(adir, "timings_ref.json")
    if retime and os.path.exists(ref):
        os.remove(ref)
    cmd = [TTSPY, os.path.join(HERE, "tts.py"), os.path.join(adir, "tts_input.json"), adir]
    locked = os.path.exists(ref)
    if locked:
        cmd += ["--ref", ref]
    subprocess.run(cmd, check=True)
    if not locked:  # first narration of a script: its timing becomes the reference that animation is built against
        import shutil
        shutil.copyfile(os.path.join(adir, "timings.json"), ref)


def timing(id_):
    sc = json.load(open(P("SCRIPTS", id_, "script.json")))
    # shot timing always comes from the timing reference when one exists (timing lock), so re-voicing can never
    # move a shot boundary or change a rendered shot's frame count
    ref = P("AUDIO", id_, "timings_ref.json")
    tm = json.load(open(ref if os.path.exists(ref) else P("AUDIO", id_, "timings.json")))
    lstart = {l["id"]: l["start"] for l in tm["lines"]}
    shots = sc["shots"]
    starts = []
    for i, s in enumerate(shots):
        if i == 0:
            starts.append(0.0)
        elif s.get("lines"):
            starts.append(max(starts[-1] + 0.5, lstart[s["lines"][0]] - 0.08))
        else:
            starts.append(None)
    # shots without lines (pure visual beats) split the gap with the previous shot
    for i, v in enumerate(starts):
        if v is None:
            nxt = next((starts[j] for j in range(i + 1, len(starts)) if starts[j] is not None), tm["duration"])
            starts[i] = (starts[i - 1] + nxt) / 2
    res = {"duration": tm["duration"], "shots": {}}
    for i, s in enumerate(shots):
        end = starts[i + 1] if i + 1 < len(shots) else tm["duration"]
        res["shots"][s["id"]] = {"start": round(starts[i], 3), "duration": round(end - starts[i], 3),
                                 "frames": int(math.ceil((end - starts[i]) * FPS)) + 2}
    json.dump(res, open(P("AUDIO", id_, "shot_timing.json"), "w"), indent=1)
    return res


def render(id_, res=540, only=None, preview=False):
    st = json.load(open(P("AUDIO", id_, "shot_timing.json")))
    for sid, s in st["shots"].items():
        if only and sid not in only:
            continue
        n = s["frames"]
        if preview:
            out = P("QUALITY_CONTROL", id_, "preview", sid)
            frames = ",".join(str(x) for x in sorted({1, max(1, n // 2), n}))
            cmd = [BPY, os.path.join(HERE, "blender", "render_shot.py"), "--", id_, sid, str(n), "--res", "270", "--frames", frames, "--out", out]
        else:
            out = P("RENDERS", id_, sid)
            if len(glob.glob(os.path.join(out, "*.png"))) >= n:
                continue
            cmd = [BPY, os.path.join(HERE, "blender", "render_shot.py"), "--", id_, sid, str(n), "--res", str(res), "--save"]
        r = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "EGL_PLATFORM": "surfaceless"})
        last = [l for l in r.stdout.splitlines() if l.startswith("RENDERED")]
        if r.returncode != 0 or not last:
            err = (r.stderr or "")[-1500:] + (r.stdout or "")[-800:]
            os.makedirs(P("QUALITY_CONTROL", id_), exist_ok=True)
            open(P("QUALITY_CONTROL", id_, f"render_error_{sid}.log"), "w").write(err)
            print("FAILED", sid, err[-400:])
        else:
            print(last[0], flush=True)
    if preview:
        contact_sheet(id_)


def contact_sheet(id_):
    from PIL import Image, ImageDraw
    st = json.load(open(P("AUDIO", id_, "shot_timing.json")))
    tiles = []
    for sid in st["shots"]:
        fs = sorted(glob.glob(P("QUALITY_CONTROL", id_, "preview", sid, "*.png")))
        tiles.append((sid, fs))
    cols = 6
    tw, th = 270, 480
    rows = math.ceil(len(tiles) / cols)
    sheet = Image.new("RGB", (cols * tw, rows * (th + 30)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, (sid, fs) in enumerate(tiles):
        x, y = (i % cols) * tw, (i // cols) * (th + 30)
        if fs:
            im = Image.open(fs[len(fs) // 2]).convert("RGB").resize((tw, th))
            sheet.paste(im, (x, y + 30))
        d.text((x + 6, y + 6), sid, fill=(255, 255, 0))
    sheet.save(P("QUALITY_CONTROL", id_, "contact_sheet.png"))


if __name__ == "__main__":
    id_ = sys.argv[1]
    stage = sys.argv[2] if len(sys.argv) > 2 else "all"
    res = int(sys.argv[sys.argv.index("--res") + 1]) if "--res" in sys.argv else 540
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    if stage in ("tts", "all"):
        tts(id_, retime="--retime" in sys.argv)
    if stage in ("timing", "all", "tts"):
        print(json.dumps(timing(id_))[:300])
    if stage == "preview":
        render(id_, only=only, preview=True)
    if stage in ("render", "all"):
        render(id_, res=res, only=only)
    if stage in ("compose", "all"):
        sys.path.insert(0, HERE)
        import compose
        print(compose.compose(id_))
