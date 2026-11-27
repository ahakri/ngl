"""Render one shot of a video with Blender (bpy).
Usage: /opt/bpyenv/bin/python render_shot.py <ID> <SHOT> <nframes> [--res 540] [--step 1] [--samples 8] [--engine EEVEE|CYCLES] [--save]
Shot builders live in BLENDER_PROJECTS/<ID>/shots.py as functions  def S01(L, n): ...  (L = studio_lib).
A builder must create everything incl. camera, and may return a dict (e.g. {"engine": "CYCLES"}).
"""
import sys, os, importlib.util, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import studio_lib as L
import bpy

ap = argparse.ArgumentParser()
ap.add_argument("id"); ap.add_argument("shot"); ap.add_argument("nframes", type=int)
ap.add_argument("--res", type=int, default=540); ap.add_argument("--step", type=int, default=1)
ap.add_argument("--samples", type=int, default=2); ap.add_argument("--engine", default="BLENDER_EEVEE")
ap.add_argument("--save", action="store_true"); ap.add_argument("--out", default=None)
ap.add_argument("--frames", default=None, help="comma list of frames to render (preview)")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

spec = importlib.util.spec_from_file_location("shots", os.path.join(ROOT, "BLENDER_PROJECTS", args.id, "shots.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
fn = getattr(mod, args.shot)
L.reset(res=(args.res, args.res * 16 // 9), engine=args.engine, samples=args.samples)
n = args.nframes
L.set_range(n)
cfg = fn(L, n) or {}
if cfg.get("engine") and cfg["engine"] != bpy.context.scene.render.engine:
    bpy.context.scene.render.engine = cfg["engine"]
    if cfg["engine"] == "CYCLES":
        bpy.context.scene.cycles.samples = cfg.get("samples", 24); bpy.context.scene.cycles.use_denoising = True
L.set_range(n)
_e = bpy.context.scene.eevee
if args.res >= 540 and bpy.context.scene.render.engine == "BLENDER_EEVEE":  # production speed profile
    _e.taa_render_samples = min(_e.taa_render_samples, args.samples)
    try:
        _e.volumetric_tile_size = "8"; _e.volumetric_samples = min(_e.volumetric_samples, 24)
    except Exception:
        pass
out = args.out or os.path.join(ROOT, "RENDERS", args.id, args.shot)
if args.save:
    L.save_blend(os.path.join(ROOT, "BLENDER_PROJECTS", args.id, "blend", f"{args.shot}.blend"))
t = time.time()
if args.frames:
    s = bpy.context.scene
    os.makedirs(out, exist_ok=True)
    for f in [int(x) for x in args.frames.split(",")]:
        s.frame_set(f); s.render.filepath = os.path.join(out, f"{f:04d}.png"); bpy.ops.render.render(write_still=True)
else:
    L.render_frames(out, 1, n, args.step)
print(f"RENDERED {args.id} {args.shot} n={n} in {time.time()-t:.1f}s")
