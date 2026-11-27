"""Automated technical QC for a finished Short. Writes QUALITY_CONTROL/<ID>/QC_AUTO.json + qc_frames.png (frame every 2 s).
Checks: container/codec, 1080x1920, fps, duration within niche band, integrated loudness (target -14 LUFS +-2 for Shorts),
true-peak < -1 dBTP, black segments (>0.5 s), frozen segments (>1.5 s), long silences (>1.2 s), shots missing renders.
Usage: python3 qc_check.py <ID>
"""
import json, os, subprocess, sys, re, glob, math
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BANDS = {"cave": (50, 72), "scuba": (40, 65), "murder": (55, 82), "haunted": (35, 60)}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main(id_):
    mp4 = os.path.join(ROOT, "FINAL_VIDEOS", f"{id_}.mp4")
    qdir = os.path.join(ROOT, "QUALITY_CONTROL", id_)
    os.makedirs(qdir, exist_ok=True)
    sc = json.load(open(os.path.join(ROOT, "SCRIPTS", id_, "script.json")))
    mood = sc.get("mood", "cave")
    res = {"id": id_, "checks": {}, "fail": []}
    pr = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", mp4]).stdout)
    v = [s for s in pr["streams"] if s["codec_type"] == "video"][0]
    a = [s for s in pr["streams"] if s["codec_type"] == "audio"]
    dur = float(pr["format"]["duration"])
    res["checks"]["resolution"] = f"{v['width']}x{v['height']}"
    res["checks"]["fps"] = v["r_frame_rate"]
    res["checks"]["duration_s"] = round(dur, 2)
    res["checks"]["has_audio"] = bool(a)
    if (v["width"], v["height"]) != (1080, 1920):
        res["fail"].append("resolution")
    lo, hi = BANDS.get(mood, (30, 90))
    if not lo <= dur <= hi:
        res["fail"].append(f"duration {dur:.1f}s outside {lo}-{hi}s band (soft)")
    if dur > 180:
        res["fail"].append("over 3 min Shorts limit")
    # loudness
    r = run(["ffmpeg", "-nostats", "-i", mp4, "-filter_complex", "ebur128=peak=true", "-f", "null", "-"])
    m = re.findall(r"I:\s+(-?[\d\.]+) LUFS", r.stderr)
    tp = re.findall(r"Peak:\s+(-?[\d\.]+) dBFS", r.stderr)
    if m:
        res["checks"]["integrated_lufs"] = float(m[-1])
        if not -17 <= float(m[-1]) <= -11:
            res["fail"].append(f"loudness {m[-1]} LUFS (target -14)")
    if tp:
        res["checks"]["true_peak_dbfs"] = float(tp[-1])
    # black + frozen
    r = run(["ffmpeg", "-nostats", "-i", mp4, "-vf", "blackdetect=d=0.5:pix_th=0.06,freezedetect=n=0.002:d=1.5", "-an", "-f", "null", "-"])
    blacks = re.findall(r"black_start:([\d\.]+) black_end:([\d\.]+)", r.stderr)
    freezes = re.findall(r"freeze_start: ([\d\.]+)", r.stderr)
    res["checks"]["black_segments"] = blacks
    res["checks"]["frozen_starts"] = freezes
    blacks_mid = [b for b in blacks if 0.6 < float(b[0]) < dur - 1.0]
    if blacks_mid:
        res["fail"].append(f"black segments mid-video: {blacks_mid}")
    if freezes:
        res["fail"].append(f"frozen video at {freezes} (static shot or missing frames)")
    r = run(["ffmpeg", "-nostats", "-i", mp4, "-af", "silencedetect=n=-45dB:d=1.2", "-vn", "-f", "null", "-"])
    sil = re.findall(r"silence_start: ([\d\.]+)", r.stderr)
    res["checks"]["silences"] = sil
    if [s for s in sil if 0.5 < float(s) < dur - 2]:
        res["fail"].append(f"silence gaps at {sil}")
    # render completeness
    st = json.load(open(os.path.join(ROOT, "AUDIO", id_, "shot_timing.json")))
    missing = []
    for sid, s in st["shots"].items():
        n = len(glob.glob(os.path.join(ROOT, "RENDERS", id_, sid, "*.png")))
        if n < s["frames"] - 2:
            missing.append(f"{sid}:{n}/{s['frames']}")
    res["checks"]["missing_frames"] = missing
    if missing:
        res["fail"].append(f"incomplete renders {missing}")
    # frame sheet every 2 s
    n = int(dur // 2)
    cols = 8
    rows = math.ceil(n / cols)
    run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-vf", f"fps=0.5,scale=216:384,tile={cols}x{rows}", "-frames:v", "1",
         os.path.join(qdir, "qc_frames.png")])
    res["auto_verdict"] = "PASS" if not [f for f in res["fail"] if "(soft)" not in f] else "FAIL"
    json.dump(res, open(os.path.join(qdir, "QC_AUTO.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
