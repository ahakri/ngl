# MURDER-06 Animation notes (Mary Celeste, 1872 / Conan Doyle, 1884)

Files: `BLENDER_PROJECTS/MURDER-06/shots.py`, `render.json` (S02/S08/S15 at 4 TAA samples: volume speckle). New builders appended to
`PIPELINE/blender/lib_murder.py` (nothing existing changed): `mat_hull`, `mat_canvas_sail`, `brigantine` (lofted tapered hull with
white band, plank deck, rail, deckhouse, hatches, fore/main masts, 4 yards with set/furled square sails, gaff sail, jib, bowsprit,
rigging, stern davits with empty swinging falls, wheel, MARY CELESTE on the transom), `ship_bob`, `swell_sea` (grid + Wave modifier,
keyed so bake_static keeps it live), `barrel_mesh` (optionally open/empty), `barrel_stacks` (linked copies, ALCOHOL stencils),
`sounding_rod`, `deck_pump` (intact / dismantled), `lifeboat`, `deerstalker`, `legend_grade` (Blender 5 compositor group: sepia
multiply + cold grey-green blend + animated grain + vignette; keyable sockets).
Ship layout: bow +X, waterline z=0, deck z=1.5. Preview rounds: 3 (rounds 2-3 with --only).

script.json overlay fixes (narration untouched): FOLKLORE label added to S03 (legend cabin); text overlays at y 1400 -> 1470
(S02, S05, S08); cards -> y 1420 (S06, S13, S17); map text one line; S09 depth gauge rounds to integers, so 0->42 "in" with text
"WATER IN HOLD (3.5 FT)" (a 0->3.5 ft gauge would have shown "4ft").

| Shot | Built | Notes |
|---|---|---|
| S01/S19 | Brigantine drifts out of thinning fog in swell, wheel turning on its own, empty davits; low push. S19 ends on S01 frame 1 (ship phase, wave offset, fog). | |
| S02 | LEGEND cabin, sepia + grain: breakfast table, teapot, cups, eggs, loaf, steam, MARIE CELESTE board; dolly. | Steam wisps are soft volume columns (a bit blocky). |
| S03 | Steam freezes, grade animates sepia -> cold grey, lamp flickers out, name board flickers. | |
| S04 | Dim swell + fog plate with a distant ship under the map. | |
| S05 | Stern: MARY CELESTE on the transom, crane up to the empty davits with swinging cut falls. | |
| S06 | Storeroom: shelves of sacks and casks, water barrels; lantern POV pan. | |
| S07 | Hold aisle between tiers of lying barrels (ALCOHOL stencils), open empty barrels + a tipped one, wet floor, hatch shaft, lanterns; dolly. | |
| S08 | Deck: sounding rod with coiled line beside an open pump-well; tilt down + push. | Fog speckle at 2 samples -> 4 in render.json. |
| S09 | Cyan diagram, hull CROSS-SECTION (not side view: a 31 m side profile is a thin sliver in 9:16), inner water rises to a red 3.5 FT mark while the outer sea line stays; outline turns green (floating). | Deviation noted. |
| S10 | Legend cabin crash push into the steaming cup. | |
| S11 | Warm desk plate with a generic magazine page (no facsimile) under the document overlay. | |
| S12 | Victorian desk, seated faceless writer from behind, lamp, manuscript; arc ends on a lit deerstalker on a side table. | |
| S13 | Legend props pop out one by one, grade sepia -> cold, skylight up, drips. | |
| S14 | THEORY: low angle in the hold, faint green fume haze, hatch slams open at 2.9 s with pale light burst + shake. | |
| S15 | THEORY: dismantled deck pump, parts on deck, sloshing pump well, 20 deg orbit. | |
| S16 | DRAMATISATION: lifeboat with four faceless silhouettes in fog; ship under full sail pulls away, fog thickens. | |
| S17 | Dusk calm sea, lantern on a plank bobbing, reflection; push. | |
| S18 | Helmsman's view from aft: wheel turning by itself, rolling fog, deckhouse beyond. | Wheel handles long; background is mostly the deckhouse wall. |

No real portraits; all people faceless silhouettes. Legend scenes graded sepia + FOLKLORE; record scenes cold grey-green.
Weakest: S02/S10 steam (blocky), S18 (plain background), S09 diagram is simple, S06 sacks read a bit like loaves.
