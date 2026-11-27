# HAUNT-07 Animation notes (Blue Bell Hill, A229)

Files: `BLENDER_PROJECTS/HAUNT-07/shots.py`, `render.json` (S01, S12 at 4 TAA samples: headlight pools in fog are speckly).
New builders appended to `PIPELINE/blender/lib_haunted.py` (nothing above changed): `bbh_z`, `_strip`, `bbh_road` (6% grade dual
carriageway, 2x7.3 m carriageways, hard shoulder, central steel barrier, verge crash barriers, bare woods on rising banks, sparse
sodium lamps, tilted ground fog), `coat_figure` (generic faceless figure, plain knee-length light coat; NOT pale_woman()),
`windscreen_rig` (driver's-eye rig: dash, pillars, wipers, rear-view mirror, headlights, rain), `box_car` (badge-less 1970s saloon /
1990s hatchback / police with blue lamp), `hazard_blink`, `blue_flash`, `custodian_helmet`, `mat_tartan`, `blanket` (flat, liftable
corner flap), `_tri_bm`, `hand_torch`. Preview rounds: 3 (round 1 full, rounds 2-3 with --only) + single-still checks of S01/S12.

Rules kept: no body anywhere; impact = jolt + intended cut to black (S01 f34-40); the blanket is laid flat and lifted empty, never over
a shape; the figure is a generic pale coat silhouette, in frame ~0.5 s in S01 and small in the mirror in S12; no signage or plates.

script.json overlay fixes (narration untouched): S03 label y 200 -> 120 and stamp y 300 -> 215 (collided with the map title), map
`land` = rough Kent outline instead of a full square, route points end on the hill pin; S11 document y -> 100 (default paper reached
into the caption band 1150-1400).

| Shot | Built | Notes |
|---|---|---|
| S01 | Windscreen POV at 50 km/h up the left lane; figure steps out of the hard shoulder f20, jolt f34, black f34-40, braking POV on an empty road. | Intended black frames f34-40. |
| S02 | Same POV stopped; wipers sweep once (f10-28); hazards tick from f14 (dash tell-tale + amber spill); tiny settle + push. | |
| S03 | High drone looking down the hill, one hatchback's lights crawling up, sodium pools. | Dark; mostly under the map card. |
| S04 | Badge-less brown 1970s saloon askew on the hard shoulder, driver's door open, faceless man looking back down the road; low push. | Man ~20-25% frame height. |
| S05 | Blanket settles flat on the wet road in the stopped car's reversing light; the car then pulls away up the hill and its light goes. | Deviation: no hands (they read as dark sausages); nothing under the blanket. |
| S06 | Police saloon with a pulsing blue lamp; two constables (helmets) with torches walk in; one bends and lifts the corner: empty. Driver waits by the barrier. | Blanket smallish in frame. |
| S07 | Defocused lateral plate along the verge barrier (timeline overlay). | No 3D car icons (would fight the 2D timeline). |
| S08 | Red 1990s hatchback with hazards on the hard shoulder; driver walks back down the shoulder sweeping a torch; handheld follow from behind and above; heavy rain. | Darkest shot; the torch pool sits ahead of the figure. |
| S09 | High crane up and away: the torch sweeps the empty carriageway, then lowers (f44+). | Driver tiny by design. |
| S10 | Corkboard under a lamp: VANISHING HITCHHIKER, PHANTOM ON THE ROAD, simple world map with pins on six continents joined by red string; pan. | |
| S11 | Defocused desk (folder "A229", newspaper, cup, lamp) under the document overlay. | |
| S12 | Driver POV at 60-70 mm: road ahead, tilt up to the rear-view mirror (f52-74); the mirror shows the red-lit road behind; the coat figure appears standing in the lane at f80. | The mirror image is two static pre-renders made at build time (EEVEE has no off-screen mirror reflections), written to BLENDER_PROJECTS/HAUNT-07/tex/mirror_<pid>_a/b.png. The folder grows by two small PNGs per build; safe to clear between renders. |
| S13 | S01 POV with no figure, ending exactly at S01 frame 1 (loop). | |

Weakest: S08 (very dark, figure mostly silhouette), S09 (dark wide), S03 (dark, under map), S06 (blanket small).
