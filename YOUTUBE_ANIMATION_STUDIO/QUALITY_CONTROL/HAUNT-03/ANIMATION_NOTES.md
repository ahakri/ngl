# HAUNT-03 — Animation notes (shots.py + PIPELINE/blender/lib_haunted.py, "ARCHER AVENUE sets" section)

Preview rounds used: 3 (round 2 = S01,S04,S06,S07,S08,S10,S13,S14; round 3 = S01,S04,S06,S08,S14).
New lib functions (append-only, HAUNT-01/02 untouched): `bare_forest` (all trees in one mesh), `_tube`, `ground_box`, `mat_gravel`,
`mat_verge`, `mat_limestone`, `archer_road`, `pale_woman`, `set_alpha`, `car_1930s` (+police light bar), `police_flash`,
`cemetery_gates` (bent bars + scorch prints option), `headstone_row`, `dance_hall`, `wire_globe`.
Each shot uses one fog volume (S08 adds a small animated fog bank).

| Shot | Built | Deviation / why | Known weaknesses |
|---|---|---|---|
| S01 | Driver POV in the right lane, wet road, bare woods both sides, low fog, headlight spots on the camera, drizzle on a moving rig. Pale woman on the right verge, 50 m ahead at frame 1. | Speed is 7.5 m/s, not 12, so she stays in frame (about 2.5% of frame height at frame 1, about 10% at the end). No car hood: it read as a black wedge. | The headlight pool on the near road is noisy and bright at bottom-left (caption zone). She is very small at frame 1. |
| S02 | Same road with no figure, DOF fully blurred, under the map card. | — | — |
| S03 | Dance hall: six arched amber windows, canopy, BALLROOM sign, gravel lot, two parked 1930s cars, thin fog. Low lateral dolly left, 35 mm. | — | — |
| S05 | Same hall, closer. The doors open (f1-16), warm spill. A man (dark, cap) and the pale woman walk out toward the parked car. Static, then 5% push. | — | The cap is the HAUNT-01 peaked-cap shape, not a flat cap. |
| S06 | Car interior from the driver's seat, 15 mm: dash with two amber dials, pale passenger sitting upright. The world outside (road and trees) slides past the side window. | The steering wheel and gloves sit just outside the frame: the passenger is about 90 degrees off the wheel. No glass panes (cost). | Mannequin-like close-up of the figure. Little parallax visible outside. The slowest shot. |
| S07 | The car drives in along the cemetery road and brakes (red tail and brake light), gates to the right. Low pan, 28 mm. | — | The car reads as a long flat silhouette. |
| S08 | Over the car roof and open rear-hinged door: she crosses from in front of the bonnet to the verge and vanishes at f39 inside a fog bank that thickens and then thins. Tiny push after. | She starts already in front of the car: a full road crossing in 1.6 s would mean running. Vanishes 1.25 s before the end. | The car roof fills the bottom 40% (caption zone). She is small. |
| S09 | Three-quarter arc 15 degrees, 50 mm. Woman behind the bars with arms forward. Police car pulls in off-frame right; red/blue 2 Hz light rakes the scene. | The police car stays off-frame: at 50 mm it cannot share the frame with the gate. | The arms read as reaching rather than gripping. |
| S10 | Handheld torch POV from the side: tilts from the spear tips in fog down to two bowed bars with dark palm smudges. Red/blue spill fades. | Oblique angle so the bend reads in profile. | The smudges read as blobs, not clear palms. |
| S11 | Corkboard: WHAT SCEPTICS SAY + a card sliding in with a truck icon, reverse arrow and fence. Desk lamp, push. | — | — |
| S12 | Wireframe globe rotating 20 degrees over stars (covered by the document overlay). | — | — |
| S13 | Three blank round-topped headstones in fog. Lateral dolly with DOF, then a still hold for the last 22 frames (dead air). | — | Stones are near-silhouettes. |
| S14 | S04 framing with the bars bent. Headlight sweep f20-42. Faint figure (alpha 0.3) from the last second. 2% push. | S04/S14 framing is closer than the first draft (10.5 m). | The figure is very faint at preview size (intended). |
| S15 | Same as S01 (loop). | — | — |

Render cost: preview ran 4-7 s/frame at 270 px while the render queue was running, so timings are unreliable. S06 is the heaviest. If it is over budget, reduce `o_trees`.
