# HAUNT-10 Animation notes (the staircase into the ceiling; Winchester Mystery House)

Files: `BLENDER_PROJECTS/HAUNT-10/shots.py`, `render.json` (S06/S08/S12 at 4 TAA samples: volumes). New builders appended to
`PIPELINE/blender/lib_haunted.py` (block "HAUNT-10 ... builders"; nothing above changed): `papered_stairwell`, `qa_block`, `qa_turret`,
`mansion_mats`, `rambling_mansion` (gabled blocks, 3 turrets, bays, chimneys, 7-level tower with separate levels), `grow_in`, `scaffold`,
`lever_rifle_rack`, `seat_pose`, `hat_on`, `vintage_car`, `picket_fence`, `ticket_booth`, `wisp` (unused in the end) + private `_hbox`, `_mesh_mats`.
Reused: gas_lamp, candle, figure / coat_figure, door_slab, wall_with_openings, bare_forest, leafy_trees, wood_chair; lib_murder dawn/night sky,
lantern, desk, lamp, book, `legend_grade` (sepia compositor) and `shake`.
Preview rounds: 3 (1 full, 2 with --only) + one extra still of S12 f48 (the figure is only visible f38-59).
Everything is generic: the mansion is not a replica, the booth board is blank, rifles are unmarked, Sarah Winchester is a small faceless
silhouette (S04, S06), the S12 figure is a plain pale coat figure badged DRAMATISATION.

script.json overlay edits (narration untouched): S05 timeline y 900 -> 980 (off the house); S09 card y 820 -> 1420 (it covered the cut-away);
S10 document `start` 0.5 (card slide reads first) and S10 label y 200 -> 1430 (it sat on the paper's text); S12 text y 420 -> 330 (it covered the door).

| Shot | Built | Notes / deviations |
|---|---|---|
| S01 / S13 | Narrow flight between walls, runner, handrails, newel, wall gas lamp with dip; tilt/push up to where the top tread meets the ceiling. S13 is a linear settle ending on S01 f1. | WEAKEST: in all three rounds the wallpaper rendered as harsh speckle and the ceiling junction is soft behind lamp glare. Wallpaper was swapped for a plain low-contrast paper AFTER the last preview (not seen rendered). |
| S02 | At the top step, plaster close to the lens, lamp dips f28-36, 5 deg roll. | Abstract framing; same unseen wallpaper change. |
| S03 | Dusk, whole mansion with amber windows behind a hedge, bare trees, mist; push in. | Lawn is near black; house wider than frame (intended "too many rooms"). |
| S04 | Daylight farmhouse core with porch, picket fence and gate, young orchard; small woman in a long dress at the gate from behind; lateral move. | Orchard trees are sparse and mostly off frame. |
| S05 | High fixed view: wings, tower levels and turrets pop up in order, scaffolds appear and vanish, 6 day/night cycles, windows glow at night. | House small in the top third (timeline sits below it); lawn is a big flat field. |
| S06 | SEPIA legend: round table, candle, two seated faceless figures, rack of five generic rifles, three soft pale volume wisps; slow orbit. | Wisps are soft ovals (one reads as a blob at mid shot). |
| S07 | SEPIA legend: night scaffold, three carpenters hammering by lanterns, a gable grows from 62% to full; crane up. | Lantern pools clip to white; figures small. |
| S08 | Day, low angle: seven-level tower shudders, cap and top three levels topple from f20, debris, dust volume; heavy shake. End = four levels. | Dust is a soft box-ish cloud; chimneys do not fall. |
| S09 | Orthographic cut-away (no near wall): an upper floor with joists, room, bed and window lowers onto the flight f16-46; red box blinks on the buried top steps. | Stair side reads as a solid stringer mass. |
| S10 | Desk, lamp, index card with grey bars slides in, book. | Under the document overlay from 0.5 s. |
| S11 | Day: hedge and gate, blank booth, five hatted visitors shuffling forward, two boxy cars, house with a four-level tower. | Booth is a pale mottled box at frame right; visitors' feet touch the caption band. |
| S12 | From the garden: blank wall, one door 4 m up opens outward f8-30 with lantern light, beam swings down and finds a pale coat figure f38-59, then it is gone; slow tilt down. | Deviation from the storyboard POV-from-inside (brief asked for the door seen from outside). Door ~13% of frame height, figure small. |

Weakest: S01/S13/S02 (stairwell: speckled paper in previews, fix unseen), S06 (wisps), S05 (small house), S12 (small door and figure).
Unseen after the last preview: plain wallpaper in `papered_stairwell` (S01, S02, S13; S09 too).
