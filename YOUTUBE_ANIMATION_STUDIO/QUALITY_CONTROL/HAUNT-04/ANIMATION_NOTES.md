# HAUNT-04 — Animation notes (shots.py + PIPELINE/blender/lib_haunted.py, "RAYNHAM / MANOR sets" section)

Preview rounds: 3 full/partial runs (round 1 all shots, round 2 S03/S05/S06/S12, round 3 S05). Before round 1 there were also
four single-frame test renders of S01, used to chase the speckle noise and to make the plate image.
New lib functions (append-only): `_beam`, `_lathe`, `mat_oak`, `panelled_wall`, `leaded_window`, `manor_staircase`, `step_pos`,
`brown_lady`, `key_principled`, `flash_pop`, `plate_camera`, `flash_gun`, `oak_corridor`, `darkroom_tray`, `manor_exterior`,
`crisp_shadows` (smaller soft shadows; no shadows on camera-mounted lights).
Plate images: `BLENDER_PROJECTS/HAUNT-04/plate_negative.png` / `plate_positive.png` are OUR OWN render of the S01 staircase (flash frame,
figure on the landing), greyscale and inverted. The real 1936 photograph is never shown, traced or imitated. Our figure stands at the side
of the landing, in a three-quarter view from the left, not descending head-on.

| Shot | Built | Deviation / why | Known weaknesses |
|---|---|---|---|
| S01 | Oak staircase (14 steps to a half-landing + return flight, turned balusters, newels with ball finials, panelled walls, leaded landing window). Push from the foot, 35 mm. Flash at f8 decays over 10 frames. Translucent veiled figure on the landing glows with the flash and stays faintly after. | 14 steps, not 18, so the landing stays in frame at a readable size. | Speckle noise on the ceiling and floor (EEVEE at 2 TAA samples; reduced by turning off shadows on the lattice and balusters, not removed). |
| S02 | Generic symmetrical 3-storey house: pediment, shaped end gables, 13 window bays, gravel, lawn, daylight fog. Crane down + push, 40 mm. | — | Flat grey. The bare trees are lost in the fog. |
| S03 | Landing close-up: empty gilt frame with dark canvas (no likeness), brass sconce candle flickering. Lateral slide, 50 mm. | — | The first frames are mostly panelling. |
| S04 | Panelled corridor, man in a long coat (over the shoulder) with candle lamp + pistol. Figure at the far end. Muzzle flash f48 + smoke puff; figure gone at f54. | — | The man is a large black mass on the left. |
| S05 | Daylight: photographer behind the plate camera on its tripod, assistant (cap) with flash gun raised toward the stairs. Low 24 mm push. | The assistant stands to the right so he isn't hidden. | Floor/ceiling speckle. |
| S06 | POV up the stairs: rotating vapour volume thickens; veiled figure fades in (alpha 0 to 0.22) and comes down one step. | — | The vapour reads a little box-shaped. |
| S07 | 85 mm on the lens: gloved hand lifts the cap (f16-40). Cut at f46 to the flash dish; blowout f58-61 (60 kW burst). DOF rack. | — | The dish reads as a flat grey disc. The blowout is not in the preview stills. |
| S08 | Darkroom top-down: red safelight, enamel tray, rippling liquid, our negative fading in (f6 to about 55). | — | The red point light shows as a bright dot in the liquid. |
| S09 | Staircase fully DOF-blurred under the document. | — | — |
| S10 | Lightbox with our positive plate. A magnifier slides across; the camera follows. | — | — |
| S11 | Board: STAIRS (blue) and FIGURE (cream) semi-transparent sheets slide together (f10-48), then a red ONE PLATE frame appears (f52). | — | Once merged, the STAIRS sheet is mostly hidden. |
| S12 | 85 mm through a greasy lens disc (brass ring), then a rack focus to a semi-transparent man in a cap coming down the stairs. | No motion blur (cost); partial transparency only. | The man is small and faint. |
| S13 | S01 end framing, locked off, empty. | — | Speckle. |
| S14 | S13 framing. Flash at f6 shows the figure 3 steps from the bottom (f6-14). Then the camera eases back to the S01 start, with the figure faint on the landing (loop). | — | The close figure is only visible inside the flash (not in the preview stills). |

Render cost: preview ran about 4-9 s/frame at 270 px under shared load. Each shot has at most one small volume (haze, smoke or vapour).
S06/S12/S13/S14 are the heaviest.
