# SCUBA-05 — Animation notes

Builders: `BLENDER_PROJECTS/SCUBA-05/shots.py` + new functions appended to `PIPELINE/blender/lib_scuba.py`
(tech_diver (sidemount + 4 stage cylinders/side, yellow fins), pose_upright, mat_rope, descent_line, depth_tag,
stage_tank, mat_reveal_z (bottom-up draw-on), lattice_tower (Eiffel wireframe), backdrop_z (Z-gradient backdrop),
mat_xray, restyle, diagram_grid, splash_drops, foam_patch, paper (redaction bars), magnifier, rubber_stamp,
submarine_outline). Existing functions untouched. Gabr is a faceless stylised diver; no logos (generic record card).
Preview rounds: 3 (round 2 = --only 15 shots, round 3 = --only S01,S03,S13,S18). Preview ~12-20 s per 3 stills.
render.json: S13, S16 at 4 samples (night-sea glints, soft desk shadows).

| Shot | Built | Deviations / why | Known weaknesses |
|---|---|---|---|
| S01 | Head-first descent beside the white line; world scrolls up (rope, tags, marine snow) for speed; god rays, bubbles streaming up, gradient turquoise above / black below. | Camera side-on, looking down ~25 deg (top-down view hid the diver behind fins/tanks). | Diver ~40% of frame, upper half. |
| S02 | Low angle up the rope: diver hanging, backlit against turquoise; small bright "surface" pinprick; slow push, single breath bubbles. | — | Diver not fully silhouetted (soft top light). |
| S03 | f1-43 aerial of coast (under map card); f44 cut: Sinai shore + hills, turquoise reef band, deep blue sea, dive boat; diver on starboard gunwale, back-roll at f62, splash + foam. | Stamp overlay start 1.8 s (was colliding with the map title). | Boat cabin dominates; diver ~20% of frame. |
| S04 | Diver upright on the line, 90 deg orbit; ghost line-art submarine (camera-parented) draws on, red strike, slides away. | — | Sub partially behind the diver. |
| S05 | Side-on ruler: ticks + 100/200/300 m plates pass on the spoken words; fish early; world/volume/sun drain blue->indigo->black; torch cone remains. | Plates on the left (depth gauge is on the right). | — |
| S06 | Macro: rope diagonal (camera roll), numbered tags scroll up, glove slides past, hard torch, backscatter. | — | Glove reads as blocky. |
| S07 | Black void, rope + weight, "332 m" tag; glove pinches and pulls it off toward camera; lens snap 42->55 mm; shake at gauge stop f34; bubble burst. | — | Hand mostly dark. |
| S08 | 1 unit = 10 m: emissive rope 0..-332 m, surface line + tiny boat, teal lattice tower (330 m) draws on bottom-up while the camera pulls back from the tiny diver to the whole column. | Rope thickness grows with the pull-back so it stays visible. | Tower top visually touches the surface line (2 m difference is invisible at scale - overlay carries the numbers). |
| S09 | Broken-axis bar chart (axis starts at 300 m): grey 2005 318.25 grows, yellow 2014 332.35 grows past a dashed mark line. | Card overlay y 1150 -> 1420; label DOCUMENTED -> DOCUMENTED FACT. | — |
| S10 | Diver at the bottom looking up; camera tilts ~70 deg up the rope following the torch beam into black; tiny surface pinprick; torch dims. | — | Dark by design. |
| S11 | X-ray figure on teal grid; gas dots appear, yellow up-arrow draws, dots swell into white bubbles, red X stamps at f74 + shake. | Text/X/hit SFX moved 2.3 s -> 3.05 s to land on "The bends". | — |
| S12 | Brighter blue: diver steps up the line stop by stop (30/27/24/21 m plates), spent stages float up, fresh stages descend on a supply line, 2 support divers (red fins) behind; light brightens. | Timeline overlay y 1250 -> 1560. | Support divers small. |
| S13 | Night sea: moored dive boat with warm windows/deck lights + crew silhouettes, moon; diver's head and torch break the surface at f50 with boil bubbles + splash. | — | Window reflections smear the foreground water; diver only visible from f46. |
| S14 | Dark desk, cold top light: anonymous printouts slide in, redaction bars draw on. | Document overlay y 600 -> 420. Label DISPUTED kept. | Mostly covered by the document overlay. |
| S15 | Desk: depth tag, dive-profile log (fast drop, long staircase up), rope diagram; magnifier visits each. | — | No lens distortion (EEVEE). |
| S16 | Rubber stamp slams on a "332.35 m" report at f12 (shake), leaves green CONFIRMED box, lifts away. | Card y -> 1420; label -> DOCUMENTED FACT. | — |
| S17 | Tag "330 m" on the deep rope glints in the torch; torch clicks off at f24, faint ghost light holds. | — | — |
| S18 | S01 set; scroll ends at 0 and camera ends exactly on S01 frame 1 (loop). | — | Bubbles/particles not identical at the loop seam. |

## Script fixes (overlay params)
Labels DOCUMENTED -> DOCUMENTED FACT (S06/S09/S16); S09/S16 card y 1420; S12 timeline y 1560; S14 document y 420;
S03 stamp start 1.8; S11 text start + hit SFX 3.05. Narration untouched.
