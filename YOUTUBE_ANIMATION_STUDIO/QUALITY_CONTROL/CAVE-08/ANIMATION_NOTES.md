# CAVE-08 Animation Notes (Jacob's Well, Wimberley, Texas: 1979 and 2000)

Builders: `BLENDER_PROJECTS/CAVE-08/shots.py`, plus functions appended to `PIPELINE/blender/lib_cave.py` (no existing function changed): `catmull`, `tube_along`, `creek_rock_mat`, `clear_water_mat`, `well_mouth`, `gravel_mat`, `pebble_floor_mat`, `gravel_field`, `park_sign`, `rebar_grate`, `flood_water`, `swimmer_float`, `rock_room`, `time_rings`. `lib_scuba.hand` is reused in S16.
Preview rounds: 3 (2 full, 1 targeted on S02, S07, S10, S11, S16, S17). No `render.json` (no shot needed extra samples at preview; S15 shows some shadow speckle and is the first candidate for 4 samples if final QC complains).

No victims are depicted or named beyond the script's memorial line. Swimmers and divers are generic faceless rigs. The loss is two lights going out (S08) and a dot dimming to an ember (S14). The 1981 flood is surface water only. The 2000 find is two beams on a dark gap plus a gloved hand. S11 shows the recovery divers backing away; nobody is near the gravel. The grate, sign and diagram are generic (no logos, not traced from a survey). No time of day is implied in S07.

Sets:
- **Creek:** heightfield limestone bed coloured by world height (`creek_rock_mat`: grass on banks, aqua tint under the waterline, blue glow fading with depth in the shaft), `well_mouth` (r 1.9 m, one mesh with rolled lip), blended clear-water sheet with faint glints, cypress (`florida_woods`) and bank bushes, east-side rock ledge.
- **Shaft and bend:** `tube_along` (vertical ~9 m, bending into an inclined passage), sand at the bend.
- **Angled passage:** sloped `passage` with a 50 degree bend at y 14-16, silt floor, tilted water volume.
- **Gravel restriction:** `passage` with floor/ceiling profiles (room, 32 degree slope, 0.4 m slot), Voronoi pebble bed plus `gravel_field` pebbles.
- **Section:** `xsection` from a variable-width band (shaft, four swells, pinches), marks at 30 FT and 100 FT only, dashed tail past chamber 4, "SCHEMATIC, NOT TO SCALE" as a camera-parented note.
- **Fourth chamber:** `rock_room` (pale) with a doorway, low `passage` gap, cracked floor heightfield.

| Shot | Built | Deviations / weaknesses |
|---|---|---|
| S01 | Drone from 8.5 m / 39 degrees down to 7.5 m straight over the mouth; two back-floating swimmers (red, yellow) with ripple rings; cypress banks. Moving at frame 1. | Starts lower and flatter than the storyboard's 12 m / 45 degrees so trees are in frame. The hole reads teal-blue, not black at the core. Bed is pale; shade patches read blue. |
| S02 | Inside the shaft: starts looking up at the bright surface sheet, sinks and tilts down to the sand and the dark opening. Four narrow daylight spots plus a wide one. | Storyboard said "straight down"; the tilt was needed to show the bright circle. The swimmers' legs are tiny at the edge of the disc. Walls read mottled/cloudy. |
| S03 | At the bend, looking down the passage; three particle streams and a floor layer moving up the passage. | **Weak.** Dark and plain; the upwelling reads only as drifting specks. |
| S04 | High, defocused aerial of the creek behind the map card. | Background only. |
| S05 | Section: dot and trail go down the shaft through chambers 1-4 (cover plates hide each chamber until the dot nears; numbers appear), dashed tail pops last; mild push-in. | Diagram is mirrored (chambers step down-left) and the push is mild, to stay clear of the depth gauge. Depth labels are small. |
| S06 | Top-down wet slab, line coil, torch prop, warm sweeping spot, drip rings. | Almost entirely under the paper overlay. Torch cone is soft and large. |
| S07 | Tracking behind and above the 1979 pair (single tanks, blue/white fins, handheld lights), bubbles, short-lived silt puffs, cyan rim. | Divers are seen from behind and are mid-size; fins dominate. |
| S08 | Down the passage: the pair recede round the bend, torches keyed off at frame 30, a lingering glow fades, faint teal walls remain. | Lights are small in frame. |
| S09 | POV in the low slot: pebble floor, ceiling close, camera-mounted torch, slot narrowing ahead. | Ceiling reads soft. |
| S10 | Slope into the slot: five pebbles tick loose, then 34 pebbles and a 900-pebble sheet slide from frame 25, brown plume grows and the beam dims. | Medium shot, not a true macro. The slide is subtle in stills; the plume carries it. |
| S11 | Two recovery divers (doubles, orange/white fins) approach, hold, back away; 12 pebbles trickle; plume at the slot. | **Weakest.** Rear three-quarter view; divers read as fins and tanks. Retreat end positions were changed after the last preview (see below). |
| S12 | Rebar grate in a concrete collar over a dark pocket in the wall; torch sweeps across; bar shadows inside. | Collar is boxy. |
| S13 | Flooded creek: brown displaced water with flowing foam streaks, rain, eight drifting branches, grey sky, one soft double flash at frames 15-19. | Far water reflects the sky as pale grey. Flash frame not previewed. |
| S14 | Same section pushed in on chamber 4; cyan dot dims to an orange ember; camera-parented 1979-2000 strip with a marker eased like the counter overlay. | Year labels are small. |
| S15 | Behind diver D in the low gap; diver C sweeps the pale chamber beyond. | Fins are flat slabs close to the lens; some shadow speckle. |
| S16 | Two torch pools converge on a narrow dark crack; gloved hand settles beside it; silt only at the sides. | Pools are bright; the crack is thin. |
| S17 | Plain NO SCUBA DIVING sign on the ledge, creek and far bank behind, ripple rings. | The well mouth is not clearly visible behind the sign. End camera key changed after the last preview (see below). |
| S18 | Rises from over the mouth to S01's exact frame-1 pose; water, rings and swimmer bob are phase-matched to S01. | Shows both swimmers (storyboard: one) so the loop frame matches. |

Script.json overlay fix: S06 `DISPUTED` label y 200 -> 610 (it covered the first line of the paper).

Changed after the last preview, not seen rendered: S17 end camera key (smaller pan so the sign stays in frame); S11 divers' retreat end positions (stop farther from the lens). Both build without errors.
