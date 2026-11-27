# CAVE-05 Animation Notes (Xisco Gràcia, Sa Piqueta air pocket, 2017)

Builders: `BLENDER_PROJECTS/CAVE-05/shots.py`, plus new functions appended to `PIPELINE/blender/lib_cave.py` (no existing function was changed): `air_bell`, `ledge`, `glow_disc`, `gauge`, `drill_rig`, `beacon`, `pose_edge_sit`, `upright_head_kit`.
Preview rounds: 3 full, plus a single-frame timing check at 540 px (S01, S11, S09 flash frame: about 5 s/frame at 2 TAA samples).
`render.json`: S01 and S13 at 4 samples (speckle on the lit ceiling and in the volumetric beam).

Recurring sets:
- **Flooded passage:** `passage` + silt `floor` + `water` volume (murky brown 0.06 to 0.085, teal 0.03, zero-visibility 0.55).
- **Air bell:** `air_bell` dome + `ledge` + a rough, low-specular `water_surface` (glow from below via `glow_at`), stalactites, drip rings, air haze.
- **Cross-section:** `xsection` + an elliptical dome polygon.

Upright divers use `upright_head_kit`, which adds a helmet, a mask facing the belly side and a helmet lamp. Gràcia is yellow, Mascaró orange and the rescuers white.

| Shot | Built | Deviations / weaknesses |
|---|---|---|
| S01 | Murky passage. Two upright divers face to face (yellow and orange helmets), torch beams crossing at chest height. A gauge sits in front of Gràcia with a glove tapping it. Two slack cut ends of the guideline sway. Push-in with handheld drift; rack focus from gauge to line. | The bodies read as dark masses; only the helmets and beams pop. 4 samples. |
| S02 | Air bell. Gràcia's helmet rises through a glowing patch of water; boil rings; the helmet beam sweeps the ceiling; vapour in the beam. Water-level pull-back. | Water reflection of the lit ceiling sits in the bottom (caption) third. |
| S03 | Defocused passage, distant torch, guideline, drifting silt (behind the map card). | Background only. |
| S04 | Clear teal passage, wide set. Both divers swim side by side; Gràcia holds a slate and pencil, Mascaró a reel; the survey line grows from the reel. Side tracking, 20 mm. | The divers are mid-size and dark against the teal. |
| S05 | Line taut over a rock edge snaps (flash, whip, sag), a silt cloud swells, and the water turns teal to brown (keyed volume). Hard cut at frame 41 to a 50 mm insert of a generic gauge (no numbers) whose needle sinks into the red. | The rock reads as a boulder more than a blade edge. |
| S06 | Over Gràcia's shoulder: a stage cylinder travels from his side into Mascaró's hands (child-of switch), Mascaró turns and swims away, and his torch shrinks to a dot, then is gone (frame 92). | **Weak.** The handover is small; the orange fins dominate during the turn. |
| S07 | Section: entrance shaft (left), long flooded passage, air dome (pale grey) on the right. The orange dot travels to the entrance with a dotted ruler trailing it; the cyan dot rises into the dome. The camera pans right to left, then snaps back. | Black background, per the storyboard. |
| S08 | Gràcia seated on the ledge edge (faceless rim figure, yellow helmet, mask pushed up), feet in the water; his right hand cups water to his mouth. Helmet lamp keyed 600 to 200, click-off at frame 58 (the sfx click). A cyan wash and rim keep the frame readable after the click. Slow push. | The figure is a stylised mannequin. |
| S09 | POV from the ledge. Four 0.4 s torch flashes at 1 Hz, in sync with the sfx clicks at frames 10, 34, 58 and 82, each sweeping a different patch of flat water. A faint cyan wash between flashes. | The preview stills (1/49/98) all fall in the dark gaps; the flash frame was checked separately. |
| S10 | Night scrub: drill tower under sodium work lights, crew in hard hats, dust. The crane-down cuts at frame 45 to a section matched on the bore line: the bore grows, stops short (red X, frame 62), and the air dome with a cyan dot sits below, unreached. | None |
| S11 | Zero-visibility brown murk. A near rescuer (white helmet, from behind) raises a hand to his mask, then reaches into the murk; a second rescuer and two torch glows fade at about 2 m. | The raised hand barely reads. |
| S12 | DRAMATISATION: the dome breathes (scale keys of about 2%), three coloured glows pulse under the surface (at most 1 Hz, fading), noisy fog thickens, 120 deg rotation, lens breathing. | Abstract by design; dark-blue overall. |
| S13 | Low on the ledge: a glow under the water grows and tightens, an underwater spot rises and throws a volumetric beam up into the haze, lit drip rings. | Stepping in the volumetric beam; 4 samples. |
| S14 | The rescuer's white helmet surfaces in the foreground; his torch finds Gràcia on the ledge, who raises an arm. Water-level push. | The water reflection blob sits in the caption zone. |
| S15 | Wide 24 mm: two rescuers chest-deep beside the ledge, a regulator hose passed up, three torches, vapour, crane up. | Busy, with hot spots on the wall. The rescuers read as round shapes. |
| S16 | Night surface entrance: a pit with a pool, rocks, garrigue scrub, stars. Generic blue/blue/amber beacons (0.8 Hz, unmarked). Mascaró from behind with an orange fin in hand; a 3-person team with headlamps across the pit. Dolly-in. | The pool itself is barely visible. |
| S17 | Empty bell: tank left on the ledge, an underwater torch beam rising. The camera ends exactly on S02's frame-1 pose (glow at the same spot) for the loop. | None |

Script.json overlay fixes:
- S01 label `REPORTED` → `EYEWITNESS CLAIM` (REPORTED is not an allowed label).
- S07 "SCHEMATIC, NOT TO SCALE" y 1180 → 300 (it was in the caption band).
- S08 `CO₂ ↑` → `CO2 RISING` (glyphs).
- S12 label y 200 → 450 (it collided with the timer at 250).
