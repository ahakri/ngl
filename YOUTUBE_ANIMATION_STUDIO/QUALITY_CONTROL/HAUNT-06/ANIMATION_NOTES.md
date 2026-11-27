# HAUNT-06 — Animation notes (shots.py + PIPELINE/blender/lib_haunted.py, "BACHELOR'S GROVE sets")

Preview rounds used: 3 (round 1 = all shots; round 2 = S01-S09, S13; round 3 = S02).
New lib functions (append-only): `grove_mats` (natural or infrared palette), `hero_stone`, `leafy_trees`, `grove_clearing`
(headstones, broken and toppled foreground stones, flattened patch, grass tufts, pond with reeds, summer trees), `seated_woman`,
`chainlink`, `farmhouse`, `orb`, `slr_camera`, `tripod`, `gloved_hand`.
The infrared grade is made with materials and light, not the compositor: black sky, near-white grass and foliage, one white key from
camera left. The 1991 photograph is never imitated. The seated figure is our own pose (turned three-quarters, head turned away, hands
in lap) and appears only in S13, labelled DRAMATISATION. render.json sets 4 samples for S04 and S05 (fog speckle).

| Shot | Built | Deviation / why | Known weaknesses |
|---|---|---|---|
| S01 | Infrared clearing: blank checkerboard hero stone, about 21 stones, white tufts and crowns, pond off to the back-left, flattened patch in front of the stone. 35 mm push from 6.0 m to 4.0 m. | The camera is closer than first drafted so the stone reads. | Grass tufts are low-poly spikes. The flattened patch reads as a disc. |
| S02 | Night lane of broken asphalt between leafy trees, ending at a chain-link fence with the gate swung open, stones beyond. Moon back-glow, handheld walk-in. | — | Dark. The fence reads mostly at the end of the shot. |
| S03 | Natural night, low 0.5 m dolly right past the stub, split slab, flat stone and empty base. Hero stone small in the background. | — | Low contrast. |
| S04 | Dense fog between trees. Three drifting blue-white orbs. A pale farmhouse with a warm porch light shrinks to 60% and fades to nothing by 85% of the shot while the camera pushes. | — | Fog speckle (4 samples in render.json). |
| S05 | Three faceless investigators with flashlights (volumetric cones). One holds a meter with a rapidly flickering red LED. All turn toward the hero stone around 55% of the shot. Over-the-shoulder, 35 mm, handheld. | The camera was pulled back from a tight OTS: up close the foreground figure was a black blob. | Speckle. The figures are simple mannequins. |
| S06 | 85 mm macro: generic SLR (no brand) on a tripod tilting up to level, with a gloved hand on the body. Plain "IR" canister on the stone ledge beside it. 15-degree orbit, DOF. | On a tripod, per the brief (the storyboard has it hand-held). | The ledge box is large in the bottom of frame (the caption area). |
| S07 | Viewfinder POV: 3D black mask with a portrait gate, focusing circle and split line over the infrared stone. Small drift, then still. Flash pop at 72%. | — | — |
| S08 | Darkroom: red safelight, bench, three trays with rippling liquid. The middle print is plain grey, never an image. Push across, DOF. | — | Abstract (red trays only). |
| S09 | Infrared stone closer, 50 mm, slow push (under the document card). | — | — |
| S10 | Generic list spread: header bars, six grey frames #1-#6. Frame #5 lights up and its caption "Bachelor's Grove, 1991" is revealed. Drift and zoom to #5. | The script.json "#5" text overlay moved from y=1150 to y=1040. | — |
| S11 | Corkboard: WHAT SCEPTICS SAY card. Two translucent sheets (empty stone outline; vague generic pale seated shape) slide together and merge. | — | — |
| S12 | S01 end framing, locked off. The fog creeps. | — | — |
| S13 | Same framing plus the seated translucent faceless figure (alpha 0.5, emission 0.2), fading up over 24 frames. 2% push. | — | The figure reads as a mannequin. |
| S14 | S01 start, with the same push speed. | — | — |
