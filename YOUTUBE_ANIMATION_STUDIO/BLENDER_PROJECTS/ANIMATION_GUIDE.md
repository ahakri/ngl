# Animation Director Guide (shots.py authoring)

## Contract
- Write `BLENDER_PROJECTS/<ID>/shots.py`: one function per shot id in script.json: `def S01(L, n): ...` where `L` is
  `PIPELINE/blender/studio_lib.py` (already reset: empty scene, EEVEE, 540x960 final / 270x480 preview, 24 fps) and `n` = frame count
  (from `AUDIO/<ID>/shot_timing.json`). Build everything: environment, characters, lights, FX, camera (must set scene camera via L.camera).
  Animate across frames 1..n. Return None (or {"engine": "CYCLES", "samples": 24} only if EEVEE can't do it — avoid, it's 3x slower).
- Category-specific reusable builders go in `PIPELINE/blender/lib_<category>.py` (lib_cave.py, lib_scuba.py, lib_murder.py, lib_haunted.py).
  Import them in shots.py via `import importlib, sys; sys.path.insert(0, <PIPELINE/blender>)`. Do NOT edit studio_lib.py
  (shared, other agents run concurrently). If you need a fix there, write a wrapper in your lib file and note it in your report.
- Keep each shot's own scene light: ≤ ~6k extra particle tetrahedra, ≤ ~150 bubbles, ≤ 3 water/fog volumes. Call `L.bake_static()` at the end
  of each shot builder (after animating) — it applies modifiers on non-animated meshes.
- Render cost budget ≈ 3.5 s/frame at final settings. Do not add Cycles shots.

## Visual language
- Vertical 9:16: compose for the centre column; keep the subject in the upper-middle third. Bottom 35% is covered by captions/UI from y≈1150px
  (of 1920) down — never put the key visual detail there. Top-left/top-right corners host overlays.
- Every shot must MOVE: camera push/pull/orbit/track or subject motion (diver swims, light sweeps, figure walks, silt drifts, door swings).
  Use `L.handheld(cam, n, amp=0.01..0.04)` for underwater sway / tension.
- Lighting: dark but readable. In black water/rooms always add `L.cam_light(cam, energy=30..120)` or a motivated fill so surfaces read.
  Torch beams: diver torch is a spot in `char_diver`; volume (`L.water_volume`) makes beams visible.
- Cave: teal-black water, warm-white torches, silt, guidelines. Scuba: bluer/brighter, caustics near surface, fish, wreck steel.
  Murder: cold desaturated night/dawn, practical warm lamps, maps/timelines/evidence as overlays. Haunted: fog, single warm practical, flicker, slow push-ins, one carefully timed reveal.
- Real people = faceless silhouettes (`char_figure` / `char_diver`). Never depict bodies or injuries; imply with light, silhouettes, objects.
- Overlays (2D) come from script.json `overlay` entries (PIPELINE/overlays.py). Check each overlay's params match overlays.py signatures
  (e.g. depth needs `from`/`to`; timer `from`/`to`/`fmt` in mmss|hours|int; map `points`/`land`; timeline `events`; document `style`/`title`;
  label text must be one of DOCUMENTED FACT / EYEWITNESS CLAIM / FOLKLORE / DRAMATISATION / DISPUTED / THEORY; card `header`). Fix script.json
  overlay params in place where they don't match (keep the narrative intent). Don't change narration text.

## Workflow (bounded)
1. Read script.json + STORYBOARD.md + shot_timing.json. Write shots.py (+ lib file).
2. Preview: `cd PIPELINE && python3 make_video.py <ID> preview` (3 stills per shot at 270x480, ~3 min) → open
   `QUALITY_CONTROL/<ID>/contact_sheet.png` with the Read tool and inspect. Errors land in `QUALITY_CONTROL/<ID>/render_error_<SHOT>.log`.
   Single shot: `python3 make_video.py <ID> preview --only S03`. Delete `QUALITY_CONTROL/<ID>/preview/<SHOT>` before re-previewing a shot.
3. Fix composition/lighting/readability. Max 3 preview rounds per video. Each shot must clearly read as what the storyboard describes.
4. Write `QUALITY_CONTROL/<ID>/ANIMATION_NOTES.md`: per shot what was built, deviations from storyboard and why, known weaknesses.
5. Do NOT run full renders (the director runs a single render queue). Do not commit.
6. When a video passes preview, create the empty marker file `BLENDER_PROJECTS/<ID>/READY` (the render queue picks it up automatically). Finish video A fully (READY) before starting video B.
