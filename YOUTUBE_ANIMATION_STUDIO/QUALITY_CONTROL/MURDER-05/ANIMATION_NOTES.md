# MURDER-05 Animation notes (Hinterkaifeck, 1922)

Files: `BLENDER_PROJECTS/MURDER-05/shots.py`, `render.json` (S04/S13 at 4 TAA samples: volumes). New builders appended to
`PIPELINE/blender/lib_murder.py` (existing functions untouched): `mat_planks`, `gable_box`, `farmstead` (studio_lib.house_exterior with
porch + door-overlapping window removed, dusted roof, chimney, window frames, attached 14x7x5 m plank barn wing with braced double door,
one lit window with keyable emission + spill light), `window_keys`, `fence`, `lantern`, `cow`, `iron_key`, `qmark_cards`, `pop_in`,
`newspaper` (generic "ZEITUNG" masthead, grey bars only), `oil_lamp`, `laptop`, `case_folder`.
World: house at origin facing -Y, barn on +X, lit window x=3; boot prints (step 0.75, rx 0.09, ry 0.2, depth 0.06) from the south tree
line to the barn wall at (7.2,-3.95), none leading away. Fine 5 cm heightfield strip for the near prints + core decals; wide shots show decals.
Forests = fast_conifers (no shadows). Preview rounds: 3 (rounds 2-3 with --only).

script.json overlay fixes (narration untouched): label REPORTED -> EYEWITNESS CLAIM (S01, S03, S04, S05), REPORTED -> DOCUMENTED FACT (S17,
2007 review), WITNESS CLAIM -> EYEWITNESS CLAIM (S12, S13); cards moved to y 1420 (S03, S14, S17, S18) and S06 text to y 1470 to keep
out of 1150-1400; map text reduced to one line (subtitle would sit at y~1390); counter text "SUSPECTS LOOKED AT (100+)".

| Shot | Built | Notes |
|---|---|---|
| S01/S20 | Ground-level linear dolly along one line of boot prints to the barn wall; lit house window left; prints end at the wall. S20 ends on S01 frame 1. | Moon raised above spec (1.0 vs 0.35) for readability. |
| S02 | Defocused wide farm plate under the map, 3% zoom. | |
| S03 | Wide night establishing push; farmer (hat, coat, lantern) at the gate, neighbour silhouette at the fence. | Figures tiny as storyboarded. |
| S04 | Gabled attic from the floor hatch: rafters, ridge beam, hay bales, moonlight slits, gable vent; warm beam sweeps and stops on the empty far corner; dust falls at 1.6 s. | Still dark by design. |
| S05 | Top-down kitchen table, folded generic newspaper slides in under an oil lamp, cup, bread. | Mostly under the document overlay. |
| S06 | Plank door + iron lock plate; key board with two painted outlines, one iron key; rack focus to the empty outline (85 mm). | |
| S07 | Previous maid (shawl, long skirt, bundle) walks away down a tree-lined lane; warm farm light from behind the camera throws her long shadow forward. | Deviation: farmhouse is implied by its light (behind camera) - a 9:16 frame can't hold both the house and a figure walking away from camera. |
| S08 | Dusk, three warm windows; new maid with suitcase tracked left to right toward the gate. | |
| S09 | RESPECT BEAT: locked-off S03 framing; the window flickers twice and goes dark at 1.2 s. Nothing else (snowfall only). | |
| S10 | Dark farm lateral pan (timeline plate). | |
| S11 | Crash push 35->85 mm (expo ease-in) to the chimney on the dark roof. | Ends tight on chimney + roof; dark. |
| S12 | Overcast day; two passers-by walk, stop, look up; tilt up to a pale smoke column from the chimney. | Smoke is a stylised volume column (somewhat rigid). |
| S13 | Barn stall row only: three primitive cows eating from a fresh hay trough, plank-gap daylight, dust; dolly along the trough. | Cows are blocky; breath puffs omitted (volume budget). No other barn content. |
| S14 | Board: SMOKE / CATTLE FED / BREAD EATEN slam in (f8/25/42), then SOMEONE STAYED (f58) + red strings, micro shakes. | |
| S15 | 47 blank grey "?" cards pop in, NO CONVICTION red stamp hits at 1.8 s, pull back 50->35 mm. | |
| S16 | Archive desk: manila case file opens, laptop with abstract glowing screen, yellowed pages, desk lamp, overhead push. | |
| S17 | Cards slide off, one face-down card stays; spot narrows; black sheet slides over it with a "NOT NAMED" tag. No name anywhere. | |
| S18 | Rounded memorial stone + iron cross in snow, lantern, slow push. | |
| S19 | From the south tree line past a trunk toward the dark farm, prints in the snow (50 mm). | Farm small in frame (wide by intent). |

Child-victim rule: no victims, bodies, weapons, interiors where victims were found, or reconstruction. Memorial card names only.
Weakest: S13 (blocky cattle), S11 (dark end frame), S12 (rigid smoke column), S04 (dark).
