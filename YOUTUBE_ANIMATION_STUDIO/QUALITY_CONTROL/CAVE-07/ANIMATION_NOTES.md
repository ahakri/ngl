# CAVE-07 Animation Notes (Sheck Exley and Jim Bowden, Zacatón, April 1994)

Builders: `BLENDER_PROJECTS/CAVE-07/shots.py`. Three functions were appended to `PIPELINE/blender/lib_cave.py` (no existing function changed): `grass_island`, `wildflower`, `tripod`.
Preview rounds: 2 full, plus 1 `--only` round (S01, S04, S09, S11, S12, S15, S16, S17).
`render.json`: S09 and S11 at 4 samples (volumetric glow around the backlight and the daylight disc).

No body is modelled anywhere. The loss is shown four ways: Exley's light dims to nothing (S02), an empty line runs down into black beside Bowden's rising light (S11), a diagram dot wrapped in a line coil (S13), and a coil of white line resting on rock (S13 insert).

Recurring sets:
- **Shaft:** `shaft()` limestone tube, teal `water()` volume, two white descent lines 2.4 m apart, rising sulphur-tinted specks. Exley = yellow fins, sidemount tanks, yellow helmet. Bowden = orange fins, back-mounted doubles, orange helmet.
- **Ranchland cenote:** `crater(R=18)`, olive scrub (`bushes`, `florida_woods` canopies), a dark pool with `grass_island` mats.
- **Ledge inside the cenote:** a 20 m radius sunlit wall (`shaft` used as an inward-facing wall), `ledge`, `water_surface` with lowered specular, floating islands.
- **Section diagram:** `xsection` with the built-in outline hidden. Open side outlines stop at 1,040 ft, and a dashed arc with a "?" marks the unknown bottom. There is a ruler in feet, two lines, a cyan dot (Exley) and an orange dot (Bowden).

| Shot | Built | Deviations / weaknesses |
|---|---|---|
| S01 | Oblique top-down into the shaft. Two head-down divers on two lines; warm and cool beam cones drop into black; bubbles and specks rise past the sinking camera. | The diver bodies sit at the frame edges and read mostly as dark shapes; the beams carry the shot. |
| S02 | Side view in black. Two lights descend; Exley's light (left) and its beam key down to 0 while he keeps sinking. Bowden's light slows and starts back up. | The lines are dimmed so the lights stay the subject. |
| S03 | Mid-morning drone descent over olive scrub toward the round hole, with dark water and grass islands. The map card shows 0 to 2.9 s, then the date stamp. | The ground reads a little sandy. |
| S04 | Bowden seated on the ledge edge (fins over the water), a stage cylinder across his thighs, right hand working the valve. Sunlit warm wall behind. 35 mm arc. | **Kneel changed to a seated pose** (the kneel read as floating). He is front-lit by the sun rather than "in shadow"; a warm wall rim keeps the separation. |
| S05 | Exley waist-deep from behind, hands behind his head pulling the mask strap, sidemount tanks visible, ripples, sun glint on the water, low push-in. | The torso reads as a dark egg shape (stylised rig). |
| S06 | Dark-teal ledger: "DIVE 0967 ... DIVE 1000" rows scroll up under the counter; DIVE 1000 (gold) settles at about y 1000. | None |
| S07 | Wet rock slab, top-down 50 mm, slight roll; a warm torch beam sweeps across; a line coil and a torch prop sit below the document. | Mostly covered by the document overlay, by design. |
| S08 | Section: two dots descend 160 to 700 ft on separate lines, light trails grow behind them, and the camera pans down. | The ruler labels are small at 540 px. |
| S09 | Bowden in 3/4 view beside his line in black water: orange helmet, glowing wrist gauge near the mask (needle sinking), heavy exhale bubbles, torch down, cyan rim. Handheld push. | The backlight makes a bright volumetric glow on the right. 4 samples. |
| S10 | Section: the orange dot reaches 925, holds, and rises; a gold flag plus "925 FT" pops at 925; the cyan dot keeps sinking toward the "?". | None |
| S11 | Looking up the shaft: the daylight opening sits in the upper third and Bowden's light rises along his line. Exley's line runs down past the camera, empty. | The opening reads as a pale blob (it is the cenote mouth). 4 samples. |
| S12 | Overcast ledge: haul tripod with pulley, three faceless haulers lean back hand over hand, a coil builds behind them, and two clipped tanks rise out of the water (one with a yellow band). | The water at grazing angle reflects a pale sky. The figures are mannequins. |
| S13 | Section: the cyan dot, wrapped in a spinning line coil, rises from 900 to 300 ft. Hard cut at frame 41 to a macro of a white line coil on wet rock. | Abstract by design, per the storyboard. |
| S14 | S07 slab re-lit cool blue with a slate and a stage tank (behind the incident document). | Covered by the document. |
| S15 | Dusk crane down to the rim: a small yellow wildflower sways at the lip, with the dark pool and grass islands below. | No memorial invented. |
| S16 | Generic modern diver (white helmet and fins) seated on the ledge edge clipping a reel to a new line, then sliding in (ripples). Over-the-shoulder camera. | The body shape is stylised. |
| S17 | S01 set with one generic diver on one line. The camera ends on S01's frame-1 pose (loop). | None |

Script.json overlay fixes:
- S03: the map and the stamp overlapped (map title at y 360, stamp at 300). The map now shows 0 to 2.9 s and the stamp from 2.9 s.
- S07: document `y` set to 90, and S14 to 100. The 1,000 px paper's default position reached into the caption band (y 1150 to 1400).
