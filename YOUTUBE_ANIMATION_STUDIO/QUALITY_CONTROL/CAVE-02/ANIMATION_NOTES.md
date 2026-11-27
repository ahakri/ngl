# CAVE-02 Animation Notes (Tham Luang rescue, 2018)

Builders: `BLENDER_PROJECTS/CAVE-02/shots.py`, plus new functions appended to `PIPELINE/blender/lib_cave.py` (none of the existing functions were changed): `passage`, `water_surface`, `drip_rings`, `rim_figure_mat`, `pose_sit`, `figure`, `group13`, `rain`, `heightfield`, `jungle`, `cliff_with_mouth`, `dive_torch`, `tank`, `full_face_mask`, `wrapped_child`, `stretcher`, `work_light`, `topo_relief`, `clip_poly`, `flat_poly`, `bubble_trail`.
Preview rounds: 2 full and 1 targeted (S01, S05, S06, S16 to S20).

| Shot | Built | Deviations / weaknesses |
|---|---|---|
| S01 | Elliptical flooded passage, glossy rippled water, about a 0.6 m air gap, stalactites, drip rings, warm-lit empty mud slope far ahead, cyan bounce and a warm skim light, faint haze, dolly forward | The gap reads a little taller than 40 cm. Still dark at preview size. |
| S02 | Ledge chamber reverse: water glows green-white from below, the diver (yellow fins) rises through the surface, the helmet beam spills up onto the ceiling, boil rings, push-in | The diver's head is small in frame. The glow disc is large. |
| S03 | Over-the-shoulder from behind the chest-deep diver; the head torch sweeps up the slope onto 13 seated faceless figures (12 small, 1 taller) on the ledge; the front row raises arms; cyan back-rim | The figures are small at preview size. |
| S04 | From behind and above the group, looking down the slope into the torch: figures silhouetted against the beam, each fresnel-rim lights in turn (left to right, in time with the 0 to 13 counter), rack focus | The nearest figures are large and blobby. |
| S05 | Jungle limestone hillside: cliff with an arched mouth, mountain heightfield, canopy blobs, cliff vegetation, muddy stream, rain streaks, mist volume, crane down to the mouth | The jungle is low-poly blobs, and the cliff reads grey rather than wet green. |
| S06 | Inside the entrance looking out at bright daylight; 13 faceless walkers (with headlamp glows) file in, crossing left to right in silhouette; puddles, dust, haze | Walk cycles are basic. |
| S07 | Same kind of passage from inside: daylight at the far end fades while brown flood water (surface, a murk volume and foam) rises past the low lens | The lens goes under only in the last ~10% of the shot. |
| S08 | Dark topographic relief with glowing contours and a gold route, defocused behind the map overlay, push-in | None |
| S09 | Silty restriction; the diver (orange fins, sidemount) rolls sideways to pass along the guideline; a noisy silt volume swells toward the lens | The fins dominate the lower-left of the frame. Reads as dramatised. |
| S10 | High angle over the 13 seated figures at the water's edge; a dropped torch's beam skims the surface; cold fill; crane down | The card overlay was moved to y=300 so it doesn't cover the figures. |
| S11 | Murky green tunnel, guideline with clipped tanks, a dark diver swimming away with a single torch, back-rim | The diver is small and dark by design. |
| S12 | Same lock-off, empty; the distant torch glow fades to nothing | None |
| S13 | Lone guideline with an arrow marker, settling silt, faint fill, back wall | The card was moved to y=760. |
| S14 | Mountain-shaped rock slab with the cave as a band; flooded sumps as pulsing blue fills; a dotted route pops in from the ledge to the entrance; LEDGE / ENTRANCE / FLOODED labels; pan right to left | The diagram is schematic, not to scale. |
| S15 | Wrapped faceless small figure with breathing chest; a full-face mask lowered by gloved hands; hose to a small tank; cyan key and warm fill; 15 deg orbit | Abstract and clinical. The mask visor reads like a bowl. **Weak.** |
| S16 | Side tracking underwater: the yellow-fin diver carries a wrapped masked shape; a white-fin diver follows with a torch; bubble trails; rack focus | **Weakest shot.** The divers read as dark shapes with a bright torch; the carried shape is legible but small. |
| S17 | Night mouth with work lights and rain, heavily defocused behind the timeline | None |
| S18 | Night mouth, three tripod work lights, rain, haze; two stretcher teams (carriers plus an escort, rim-lit) walk out toward the camera; dolly back | The stretchers are small. |
| S19 | Dawn mouth, mist, a torch on a rock just inside, its beam pointing into the dark; push-in | The torch reads only as a small glow (the beam points away from the camera). |
| S20 | S01 set, camera dolly ends exactly on S01's frame-1 pose (shake ramps to 0) for the loop | None |

Script.json overlay fixes: S03/S15 text y 1250 → 1010 (clear of captions), S10 card y 1150 → 300 (mood cave), S13 card y 1150 → 760 (mood cave). All labels use allowed values.
