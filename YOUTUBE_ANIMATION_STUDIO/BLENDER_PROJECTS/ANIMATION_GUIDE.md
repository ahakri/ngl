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
- Render cost target ≤ 6 s/frame at final settings (540 px, 2 samples). Do not add Cycles shots.

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

## Lessons learned from slates 1–4 (mandatory — each one cost a QC fail or a re-render)
**Timing lock.** Narration and shot timing are frozen (`AUDIO/<ID>/timings_ref.json`). Never run `make_video.py <ID> tts`, never edit narration text;
build every shot to the frame count in `AUDIO/<ID>/shot_timing.json`. You may edit only overlay params / sfx offsets in script.json.

**Particles.** Radius <= 0.008 everywhere; in close-ups <= 0.004 and NO particles within ~0.5 m of the camera (near particles render as big
confetti squares — CAVE-01 S12 failed final QC for this even though the preview stills looked fine). Never put particle clouds in front of key content.

**Readability.** Rim-light every silhouette against its background or beam. No shot may be an empty gradient, a blob, or an unintended black
frame; check frame 1 is not inside geometry; key subjects >= ~30% of frame height in key beats; consecutive shots must differ visibly.
Preview stills only sample 3 frames: for any shot with a timed event (flash, reveal, cut-to-black) render one extra still on that frame.

**Overlays.** Labels only: DOCUMENTED FACT / EYEWITNESS CLAIM / FOLKLORE / DRAMATISATION / DISPUTED / THEORY. Colours are RGB lists, never words.
The caption band is y 1150–1400 (of 1920): place text/cards above ~1080 or below ~1420 (compose auto-shifts intruders up, but do it right).
Map titles are single-line. `document` overlays support `~~struck~~` text; set `y` so the paper stays out of the caption band.
Glyphs: Anton lacks some symbols (bullet dot, check mark, "approximately" sign) — use plain ASCII words instead; always look at the rendered overlay.
**An overlay is a claim.** Never assert on screen anything the narration hedged, labelled or dropped in the fact-check (SCUBA-06 lost a
"NO TANK / BREATH-HOLD" overlay for this). Recreated scenes of real people carry a DRAMATISATION label.

**EEVEE on CPU (Blender 5).** A world volume blocks the sun: use a large volume cube instead. Area lights inside water need `volume_factor = 0`.
EEVEE cannot reflect things behind the camera (mirror shots need a pre-rendered still on a plane). Thousands of shadow-casting objects are ~5x
slower: forests use `lib_murder.fast_conifers` (no shadows). One moderate fog/water volume per shot. Production renders use 2 TAA samples; list
only genuinely speckly shots in `BLENDER_PROJECTS/<ID>/render.json` as `{"samples": {"S0X": 4}}`. Target <= 6 s/frame at 540 px.

**Shared libraries.** `PIPELINE/blender/lib_cave.py`, `lib_scuba.py`, `lib_murder.py`, `lib_haunted.py` are rendered from by queued videos:
append new functions only, never change an existing function's behaviour. Per-build generated textures go under `BLENDER_PROJECTS/<ID>/tex/`.

**Respect.** Real people are faceless figures; no bodies, wounds or remains — imply with light, objects, diagrams. Do not name victims beyond the script.
