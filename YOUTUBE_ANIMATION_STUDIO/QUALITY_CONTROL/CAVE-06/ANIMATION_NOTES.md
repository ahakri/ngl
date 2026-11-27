# CAVE-06 Animation Notes (Eagle's Nest sinkhole, Florida)

Builders: `BLENDER_PROJECTS/CAVE-06/shots.py`, plus functions appended to `PIPELINE/blender/lib_cave.py` (no pre-existing function was changed):
- `hooded_icon`, `warning_sign`, `florida_woods`, `pond_mat`.
- `air_bell` gained an optional `hole_r` (default 0; CAVE-05 is unaffected).
- `upright_head_kit` and `glow_disc` are shared with CAVE-05.

Preview rounds: 2 full and 1 targeted (S01, S06, S08, S12, S14, S15), plus a single-frame timing check at 540 px (S12 5.3 s, S01 3.4 s, S04 5.9 s per frame).
`render.json`: S04 at 4 samples (volumetric beam).

No victims are depicted or named. The 2016 divers appear only as two torches going down (S12) and two dim grey dots (S14). Divers are generic faceless rigs (blue, green fins). The warning sign is a generic recreation with no agency name or logo.

Sets:
- **Pond exterior:** radius 7 m blackwater pond with duckweed (`pond_mat`), a bank heightfield with a rounded sand entry tongue, about 200 live-oak/cypress trees (trunk plus canopy blobs), palmetto understory, cypress knees. Time of day comes from `_sky`.
- **Chimney:** narrow `shaft` (r about 1.25 m) under the pond with a green-lit volume.
- **Ballroom:** `air_bell` 32 x 28 m with an open crown, the chimney above it, a debris mound, a green daylight spot, cool ambient points.
- **Section:** a single `xsection` polygon (pond, chimney, ellipse Ballroom, stepped tunnel), a debris-mound fill, CHIMNEY/BALLROOM labels.

| Shot | Built | Deviations / weaknesses |
|---|---|---|
| S01 | Top-down 28 mm drone over the pond, dense canopy, sand entry slope, morning sun; descending push with slight roll. | The sand slope reads pale. |
| S02 | Low 35 mm dolly along the bank: cypress knees, duckweed, a speck skimming, a yellow dive line tied to an exposed root running into the water. Rack focus from near to line. | Trees are low-poly blobs. |
| S03 | Top-down over the water, then through the surface (water hidden at frame 17), then following a head-down diver (blue fins) down the green-lit Chimney, torch below. | The fins are flat paddles. |
| S04 | Ballroom: the diver under the chimney mouth, torch beam into nothing; pull-back and tilt down to the debris mound far below with a green daylight shaft. | Frame 1 is dark around the diver. 4 samples. |
| S05 | Same Ballroom, heavily defocused, behind the map card. | Background only. |
| S06 | Section: pond, Chimney, Ballroom (with debris mound), stepped tunnel; a cyan dot and trail travel the route; downward pan. | Schematic, not to scale (on-screen text). |
| S07 | POV torch (camera-mounted spot plus beam) sweeps the debris slope with sticks and silt, stops dead on the sign on a pipe stake, push. | The sign is still smallish at the end of the shot. |
| S08 | Sign close-up, 50 mm: STOP! (red), hooded skull-and-scythe pictogram, PREVENT YOUR DEATH! / GO NO FARTHER. One torch flicker at frame 40. Slow push. | None |
| S09 | Dusk pond, tree silhouettes against an orange horizon, slow lateral drift (behind the timeline). | None |
| S10 | Dawn pond over the water: a dive line tied to the root again, low mist, slow push. | None |
| S11 | Afternoon, low sun behind: three faceless figures on the sand bank (one standing with a cylinder, two crouched working valves), cylinders lying around; camera low over the water, dolly-in. | The crouch pose is stiff. The figures are about 25% of frame height. |
| S12 | Under the pond, looking straight down the Chimney: a hovering diver (green fins) in the foreground, two torch lights shrinking into the dark below. | **Weakest.** The foreground diver sits in the lower (caption) third. |
| S13 | Locked-off over the still pond from the bank: bubble rings and pops grow sparse, then stop (last at frame 50). Sun, sky and colour fade toward evening. | The rings are subtle at preview size. |
| S14 | Same section: route trail to the deep tunnel, a white marker ring, two dim grey dots fading in, then dimming. Slow push to the marker. | None |
| S15 | Deep blue-black passage, guideline, hanging silt, a single camera-mounted torch sweeping and finding nothing, slow push. | The walls are only lightly readable. |
| S16 | Starts underwater looking up at the bright surface (dark duckweed blotches, dive line), crosses the surface at frame 15, rises to S01's exact first-frame pose (shake ramps to 0) for the loop. | None |

Script.json overlay fixes:
- S05 "EVEREST OF CAVE DIVING" y 1420 → 250 (caption band and the map subtitle).
- S06 "SCHEMATIC, NOT TO SCALE" y 1180 → 1080.
- S08 and S14 label `REPORTED` → `EYEWITNESS CLAIM` (REPORTED is not an allowed label; these are single-source press/recovery accounts per FACTCHECK).
