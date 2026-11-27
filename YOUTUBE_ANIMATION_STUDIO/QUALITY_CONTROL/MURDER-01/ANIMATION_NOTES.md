# MURDER-01 Animation notes (Dyatlov Pass / 2021 slab model)

Files: `BLENDER_PROJECTS/MURDER-01/shots.py`, builders in `PIPELINE/blender/lib_murder.py`.
World layout for all 3D slope shots: tent at origin, ridge along X, slope rises toward +Y (20 deg), tent sits on a
platform cut into the slope (uphill cut wall), slit on the downhill (-Y) roof panel, tracks run downhill to a conifer
tree line. Preview rounds used: 3 (round 3 re-rendered only the shots changed after round 2).

| Shot | Built | Deviations / notes |
|---|---|---|
| S01 | 3/4 medium-close of the half-buried canvas tent: roof panel with a cut slit and two hinged, fluttering flaps; warm interior light leaks through; torch spot sweeps in from the left and settles on the slit; snow, low fog, push-in, handheld. | Storyboard asked for an extreme close-up; pulled back so the tent shape (ridge, gable, snow banks) reads on a phone. |
| S02 | High-res snow patch with three trails of shallow sock/barefoot prints carved into the heightfield, ground-level dolly with tilt-up into fog, raking moon. | - |
| S03 | Aerial ridged mountain range at night (plate under the map card), stars, slow drift. | Mostly covered by the map overlay. |
| S04 | Low-oblique drone glide down the slope following three dotted track lines from the glowing tent to the snow-dusted tree line. | Changed from top-down to oblique per director note (top-down read flat). |
| S05 | Lateral pan from above the camp looking downhill at the tracks and tree line (timeline plate). | Tent removed from plate (read as a black box). |
| S06 | Nine grey marker poles with small flags down the slope, each switching on a warm point light in sequence; tree line; slow push. | - |
| S07/S08 | Cork evidence board, hanging lamp; three paper cards slam in (ALIENS / WEAPONS TEST / ATTACK, yellow THEORY badges); S08 red NO EVIDENCE x2 and UNPROVEN stamps thump on with small dust puffs and camera shake. | - |
| S09 | Blurred (DOF) tent-with-snow plate under the document overlay. | - |
| S10 | Side view of the slope with the tent; emissive horizontal line, slope line and angle arc draw on. | - |
| S11 | Three particle swirls collapse into a settled layer over a glowing grid that shifts blue to cyan; fast push then settle. | - |
| S12 | Wireframe slope terrain, orange tent marker with expanding ring, bright scan band sweeping across the wireframe, 40 deg orbit. | - |
| S13 | Ortho cross-section (snow layer on dark ground with ridge); notch wedge lifts out, red cut outline draws, tent block drops in; zoom. | Wedge is lifted away rather than boolean-carved. |
| S14 | Same section: wind-blown particle stream + arrows flow over the ridge, blue wind-slab wedge grows (shape key). | - |
| S15 | Red crown/base crack lines appear, slab slides down and slumps into the notch, tent block squashes, shake. | - |
| S16 | 3D side view: snow slab slides down onto the tent gable, tent sags, small particle burst + volumetric snow puff, handheld + shake. | Camera side-on (not from downslope) so the slide reads. |
| S17 | Aftermath: tent sagged under the slab, scattered snow chunks, settling snow, haze, pull-back. | - |
| S18 | Inside the dark tent: warm torch on canvas, slit flaps fall open revealing moonlit snow; five faceless hiker silhouettes step out one after another. | - |
| S19 | 85 mm from uphill: four tiny silhouettes walk into a fogged conifer tree line. | Conifers instead of bare trees (matches the real cedar forest). |
| S20 | Medium close on the slit, warm torch resting on it, slow push. | - |
| S21 | Same set as S01; push-in ends exactly on S01 frame-1 camera/torch for the loop. | - |

Overlay param fixes in script.json: S12 label `SCIENTIFIC MODEL` -> `THEORY`; S16 label `SIMULATION (DRAMATISATION)` -> `DRAMATISATION`.

Known weaknesses: canvas is a plain sagging mesh (no cloth sim); snow flakes are tetra particles (fine at 540p, can look
faceted on near flakes); S03 mountains are low-poly-ish; S05/S09 are deliberately plain plates behind overlays.
