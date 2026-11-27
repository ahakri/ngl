# HAUNT-05 — Animation notes (shots.py + PIPELINE/blender/lib_haunted.py, "WAVERLY HILLS sets")

Preview rounds used: 3 (round 1 = all shots; round 2 = S01, S06, S07, S08, S10, S12, S13; round 3 = S06).
New lib functions (append-only): `mat_streaked`, `chute_tunnel`, `chute_world`, `gurney`, `roll_along`, `bare_forest_z`, `hill_z`,
`hill_ground`, `_porch_block`, `sanatorium`, `mat_peeling`, `porch_corridor`, `moon_floor_point`, `rubber_ball`, `ticket_icon`.
The sets are stylised and are not likenesses. Each shot uses one fog volume. render.json sets 4 samples for S01 and S14 (fog and point-light speckle).

| Shot | Built | Deviation / why | Known weaknesses |
|---|---|---|---|
| S01 | Tunnel tilted 12 degrees down. Steps on the left, rails and cable on the right, gutter, cage lamps every 6 m, lamp 7 dead. Empty gurney with a folded sheet rolls away and speeds up. Blue spill from the top doorway. 24 mm follow push. | — | The gurney reads mostly as a frame outline at preview size. Light speckle in the fog. |
| S02 | Five-storey sun-porch range (30 bays per floor), taller entrance block, wings angled back 30 degrees, hill with a 15-degree slope, trees, ground fog. One faint fourth-floor bay. Crane up from behind near branches, 35 mm. | — | The facade reads as a flat grid. Dusk sky is a plain colour. |
| S03 | Same set, darker. Focus racks from the near branches to the building at about 50-62% of the shot (the "1926" beat). 5% push. | — | Fits under the timeline overlay. |
| S04 | 100 m tunnel from the bottom. 50 mm, pedestal up 1 m plus push. The lamps recede to a small blue doorway. A few drips. | 100 m modelled instead of 152 m. At 50 mm the length still reads. | — |
| S05 | Mid-tunnel, side three-quarter view. A pale-coated faceless orderly walks backwards down the steps beside the gurney, stops, and lifts his head toward the top (toward the camera). Pendant bulb swings. 5% push after the stop. | The camera is inside the tunnel on the steps side. A true side-on view does not fit in a 2.4 m tube. | The arm reach to the gurney is approximate. |
| S06 | Closer on the bays, 50 mm lateral dolly. Seven faint warm bays switch off floor by floor, bottom to top. Sky and moon dim. | — | Lit bays are flat panels. |
| S07 | Corridor 30 m long and 3 m wide. Open sun-porch bays on the right throw moon stripes. Doors on the left, some ajar. Debris. Flashlight on the camera. A pure-black figure walks across the lit end doorway at frames 53-79. | 30 m instead of 40 m so the far figure is not microscopic. | The figure is still small. Walls are very dark outside the flashlight pool. |
| S08 | Floor level, 10 cm, 50 mm, DOF on the red ball in a moon stripe. A flashlight sweeps in and settles on it. | — | The near floor goes grey and soft while the beam passes. |
| S09 | Dim corridor (moon at about 20%), slow push. Sits behind the 63,000 counter. | — | Deliberately dark. |
| S10 | Same corridor, which slowly brightens. A 3D "63,000" in pale green (Anton font, at the counter's height), with a red strike drawn across it at frames 4-11. | The script.json S10 text overlay "6,000 - 8,000" moved from y=1150 to y=1060 to stay above the captions. | — |
| S11 | Corkboard: WHAT SCEPTICS SAY card, then a second card slides in with a red ticket icon and PAID GHOST TOURS. Desk lamp, push. | — | — |
| S12 | Wide, locked-off corridor. The stripe is empty. The moon dims slightly (cloud) and dust drifts. 0.5% creep. | Camera at 1.0 m, 2.6 m from the stripe (storyboard: 1.6 m). This keeps the ball's stop point above the caption zone and large enough to see. | The ball is still small (r = 3.5 cm). |
| S13 | Same framing. The ball rolls in from about 7 m, decelerates across the stripes, and stops back in its stripe. 2% push. | Stops about 2.6 m from the lens (not 1 m) so it is not in the caption zone. | The roll is faster than "slow" because the shot is 1.8 s. |
| S14 | S01 framing and push, with a small gurney jolt at the cut. | — | — |
