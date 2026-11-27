# SCUBA-02 — Animation notes

Builders: `BLENDER_PROJECTS/SCUBA-02/shots.py` + shared `PIPELINE/blender/lib_scuba.py`
(Ocean-modifier sea with facing-ratio colour, foam, capillary bump and glowing underside; gradient sky with sun disc;
dive catamaran; foam wake ribbon; surface swimmers with BCD collar + pushed-up mask; caustic ground; god rays;
BCD vest, wetsuit, dive slate, seaweed). The Lonergans are faceless figures; no bodies, no sharks.

## Shots
| Shot | Built | Deviations / why | Known weaknesses |
|---|---|---|---|
| S01 | Golden-hour open sea, camera just above the swell (deterministic bob), two swimmers backs-to-camera, sun glitter path, dive boat tiny on the horizon receding with a wake. | Golden hour (per art brief) instead of "high afternoon". | Sea reads smooth at phone size; boat is a speck. |
| S02/S10 | Aerial turquoise reef/water with caustic pattern drifting under the map card. | 3D only a background: the map overlay is the shot. | — |
| S03 | Bright reef: caustic sand, coral_field, two fish schools, two divers gliding with bubble trails, god rays, glowing surface; lateral track. | — | Stylised/pastel corals; caustic network a bit strong. |
| S04 | Dive-boat aft deck from above: seated faceless passengers, tank racks, crew with clipboard; tally marks appear one by one; crane down to the clipboard. | — | Hard white deck slightly hot. |
| S05 | Side-on boat; two figures jump off and splash; translucent "ghost" duplicates appear back on deck = counted twice. | Labels: "ONE ACCOUNT" -> "DISPUTED" (allowed set). | Ghosts pale against the bright sky. |
| S06 | Drone aerial: boat accelerates along an arc toward the top of frame, foam wake. | Overlay text "ALL ABOARD ✓" -> "'ALL ABOARD'" (✓ glyph missing in Anton = tofu). | Wake is a gentle curve, not a full arc. |
| S07 | Top-down crane from two heads (foam rings) to specks in a darkening sea; lens 50 -> 28. | — | — |
| S08 | Cabin: porthole daylight slat on a lone dive bag on a bench, dust motes, crew silhouette walks in and looks. | — | Crew figure mostly off the push-in framing. |
| S09/S16 | Top-down table: wallet + two generic passports (no names) / two blank cards slide in under the document overlay. | — | Mostly covered by the paper overlay by design. |
| S11 | Overcast grey-teal sea, low tracking aerial, aircraft shadow shape crossing. | — | Shadow reads a little like a small aircraft. |
| S12 | Grey beach, wash sliding in/out with foam line, BCD vest in the wash, wetsuit in seaweed further on; dolly + rack focus. | Label "FOUND" -> "DOCUMENTED FACT". | — |
| S13 | Dive slate with illegible scribbles + pencil on cord, low sun, blowing sand, shallow DOF. | Label "REPORTED" -> "DISPUTED". | — |
| S14 | Empty sunset sea, horizon centred, locked-off imperceptible push. | — | — |
| S15 | Underwater looking up: surface glow and god rays fade, water darkens; tilt up. | Label "UNKNOWN" -> "DRAMATISATION" (allowed set; the visual is dramatised). | — |
| S17 | Same deck in morning light: two crew count independently, green 3D ticks pop above each clipboard; arc. | Overlay text "COUNT 1 ✓ / COUNT 2 ✓" -> "COUNT 1  OK / COUNT 2  OK" in green (glyph). | Mannequin-like figures. |
| S18 | Return to S01: camera, ocean time and bob phase computed so the last frame equals S01 frame 1 (boat hidden = empty horizon). | — | — |

## Script fixes
S04 label "REPORTED" -> "EYEWITNESS CLAIM"; S05 "ONE ACCOUNT" -> "DISPUTED"; S12 "FOUND" -> "DOCUMENTED FACT";
S13 "REPORTED" -> "DISPUTED"; S15 "UNKNOWN" -> "DRAMATISATION"; S06/S17 ✓ removed (missing glyph).

## Engine notes (also apply to SCUBA-01)
- EEVEE Next world volumes absorb the sun entirely (infinite path) -> `lib_scuba.world_volume()` now makes a big volume cube.
- Area lights inside volumes show as glowing rectangles -> shots set `volume_factor = 0` on area lights (`_finish`).
- Ocean surfaces have `visible_shadow = False` so they don't shadow the underwater scene.
