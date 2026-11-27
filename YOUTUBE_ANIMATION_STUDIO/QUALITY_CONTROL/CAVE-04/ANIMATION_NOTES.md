# CAVE-04 Animation Notes (Nutty Putty Cave, 2009)

Builders: `BLENDER_PROJECTS/CAVE-04/shots.py`, plus new functions appended to `PIPELINE/blender/lib_cave.py` (no existing functions were changed): `clay_mat`, `crack_floor_z`, `crawl_ceiling_z`, `crawl_set`, `helmet`, `crawler`, `anim_crawl`, `outline_figure`, `arrow2d`, `x_mark`, `bolt_anchor`, `pulley`, `star_dome`, `sagebrush`, `hill_z`, `hill_set`. It also reuses the CAVE-02 additions (`figure`, `heightfield`, `passage`, `rim_figure_mat`, ...).
Preview rounds: 2 full and 1 targeted (S01, S04, S08, S11).
How John Jones is shown: only boots and lower legs while he is alive (S01), a faceless figure seen from behind (S05), gloved hands (S06), and a grey diagram outline (S02/S07/S09/S12/S14). No body is depicted. His death is shown only as the diagram lamp icon going dark and the outline fading (S14).

| Shot | Built | Deviations / weaknesses |
|---|---|---|
| S01 | Clay crawlway floor with a steep V crack (heightfield); legs and boots rising from the crack; his lamp glowing deep inside the crack; dust; push-in | **Weakest shot.** The legs read as stiff pale posts more than legs in coveralls. |
| S02 | Beige rock slab section: crawlway, then a crack angled steeply down; grey outline figure inverted at the narrow end (lamp dot on its helmet); down and up arrows with red X marks popping in; 5% zoom | None |
| S03 | Three prone faceless rescuers (helmet lamps, rope coils, pulley bag) crawl toward a floor-level camera; pull-back | The figures are small and distant. |
| S04 | Night: bare hill heightfield, star dome, sagebrush, red/blue/white vehicle glows and headlights at the bottom; crane down from uphill toward the opening | The cave opening reads weakly in the dark. |
| S05 | Dusk: faceless caver (red helmet, lamp on) seen from behind at the opening; crouches and drops in; warm rim light | The card was moved to y=900. |
| S06 | First-person tube that narrows and tilts down; helmet lamp; alternating gloved hands reach and pull; crawl bob | The glove shapes are simple ellipsoids. |
| S07 | Section: the outline figure slides along the crawlway, turns and slides head-first down the crack to the narrow end; dotted trail; camera follows down | None |
| S08 | Ceiling macro: the bolt is hammered in, then hanger, karabiner and pulley appear; rope pays out down into the crack; three framings | The pulley plates are oversized. The end frames looking into the crack are very dark. |
| S09 | Section: rope from the anchor to the figure's feet (animated curve point); the figure inches up; cyan progress line grows | None |
| S10 | Four seated faceless haulers in line (helmets and lamps), leaning back in sync on the rope through the ceiling pulley; warm fills; tracking shot down the line | Diagonal track instead of a pure side track, because the crawlway is too narrow for a side camera. |
| S11 | Cracks spread around the bolt; the anchor, a rock chunk and the pulley tear out and fall; taut rope swaps to a whipping slack rope; dust burst; the lamp flickers; 6-frame hard shake | Dust reads as fine specks. The macro framing is abstract. |
| S12 | Section: progress line drains; the figure slides back to the narrow end; an empty red anchor ring and slack rope | None |
| S13 | Dim crawlway: two figures resting against the walls, one working at the crack, flickering lamps, slack re-rig, rope coil; lateral dolly | Dark (intended); the figures are angular. |
| S14 | Section final state: the helmet lamp icon flickers, dims and goes out; the outline fades to a faint line; slow zoom-out | The card was moved to y=760. |
| S15 | Static floor camera at the crack: two rescuers crawl away; their lamps shrink and switch off; a rope coil remains in the foreground | None |
| S16 | Day: chute and grey pour into the opening while a fill plane rises; hard cut at 62% to a flush concrete slab; crane up | The pour stream is a simple tube. |
| S17 | Dawn: the concrete slab flush in the hillside among sagebrush moving in the wind; slow push-in | None |

Script.json overlay fixes: S05 card y 1150 → 900 (mood cave), S14 card y 1150 → 760 (mood cave). All labels use allowed values.
