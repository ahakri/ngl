#!/usr/bin/env bash
# Render + assemble + auto-QC one Short on a CI runner (or any machine with the toolchain on PATH).
# Usage: ci_render.sh <ID> [comma-separated shots to re-render]
# Needs: python (3.11 with bpy, numpy, pillow), ffmpeg, mesa EGL (software GL), DejaVu fonts. Narration is NOT regenerated here:
# AUDIO/<ID>/narration.wav + timings are committed, and shot timing comes from timings_ref.json.
set -uo pipefail
ID="$1"; RERENDER="${2:-}"
cd "$(dirname "$0")"
export EGL_PLATFORM=surfaceless
PY="${STUDIO_PY:-python3}"
export STUDIO_BPY="${STUDIO_BPY:-$PY}"
T0=$(date +%s)
if [ -n "$RERENDER" ]; then for s in ${RERENDER//,/ }; do rm -rf "../RENDERS/$ID/$s"; done; fi
$PY make_video.py "$ID" timing > /dev/null || { echo "timing failed"; exit 1; }
$PY make_video.py "$ID" render --res 540
T1=$(date +%s)
MISSING=$($PY - "$ID" <<'PYEOF'
import json, glob, os, sys
id_ = sys.argv[1]
st = json.load(open(f"../AUDIO/{id_}/shot_timing.json"))
bad = [f"{k}:{len(glob.glob(f'../RENDERS/{id_}/{k}/*.png'))}/{v['frames']}" for k, v in st["shots"].items()
       if len(glob.glob(f"../RENDERS/{id_}/{k}/*.png")) < v["frames"]]
print(",".join(bad))
PYEOF
)
if [ -n "$MISSING" ]; then
  echo "INCOMPLETE SHOTS: $MISSING"; ls ../QUALITY_CONTROL/$ID/render_error_*.log 2>/dev/null | head; tail -n 30 ../QUALITY_CONTROL/$ID/render_error_*.log 2>/dev/null
  exit 2
fi
$PY compose.py "$ID" || { echo "compose failed"; exit 3; }
$PY qc_check.py "$ID" > /tmp/qc_$ID.json || { echo "qc failed to run"; exit 4; }
T2=$(date +%s)
mkdir -p ../PROJECT_TRACKER/ci_runs
$PY - "$ID" "$((T1-T0))" "$((T2-T1))" <<'PYEOF'
import json, os, sys
id_, render_s, post_s = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
qc = json.load(open(f"/tmp/qc_{id_}.json"))
st = json.load(open(f"../AUDIO/{id_}/shot_timing.json"))
frames = sum(v["frames"] for v in st["shots"].values())
out = {"id": id_, "run_id": os.environ.get("GITHUB_RUN_ID"), "sha": os.environ.get("GITHUB_SHA"),
       "render_seconds": render_s, "assemble_qc_seconds": post_s, "frames": frames,
       "seconds_per_frame": round(render_s / max(1, frames), 2), "auto_verdict": qc["auto_verdict"], "fail": qc["fail"],
       "duration_s": qc["checks"].get("duration_s"), "lufs": qc["checks"].get("integrated_lufs"),
       "true_peak": qc["checks"].get("true_peak_dbfs")}
json.dump(out, open(f"../PROJECT_TRACKER/ci_runs/{id_}.json", "w"), indent=1)
print(json.dumps(out))
PYEOF
