# SCUBA-03 — Animation notes

Builders: `BLENDER_PROJECTS/SCUBA-03/shots.py` + new functions appended to `PIPELINE/blender/lib_scuba.py`
(manifold, dsv, diving_bell, lift_wire, tube/tube_keys (keyframable NURBS tubes), umbilical, mat_drain (glow draining
from a point), bubbles_at, kneel/curl_pose, bailout_valve, emit/energy/exposure keys, shake, no_shadow).
Existing SCUBA-01/02 functions untouched. All people faceless; the umbilical is a stylised glowing cyan tube.
Preview rounds: 3 (round 3 = --only S09,S18). Preview render ~4-6 s/frame at 270 px on a loaded machine.

| Shot | Built | Deviations / why | Known weaknesses |
|---|---|---|---|
| S01 | Lemons (yellow hard hat, bailout bottle) kneeling on the manifold roof, low angle; umbilical (2 tubes) whips at f20-33, parts at f34: flash + bubble burst, upper end recoils, lower goes slack, glow drains outward from the break, helmet light dies. | Helmet light starts ON and dies with the snap (matches S08/S19). | Diver ~25% of frame height. |
| S02 | 3/4 rear over-the-shoulder on the bailout bottle + chrome valve, DOF on valve, rhythmic exhalation bursts, dead umbilical stub. | — | Helmet fills the top of frame. |
| S03 | Moonlit night sea from above + distant rig lights (under the map card). | — | Background only. |
| S04 | Lemons standing at a manifold handwheel, helmet light on, intact glowing umbilical rising to the bell far above; tilt down. | Name card y 1250 -> 1420 (clear of captions at 1240). | Diver small in the wide. |
| S05 | Storm night sea, stylised DSV (hull, accommodation block, helideck, dive tower, crane, sodium floods); bridge windows green -> flashing red + red alarm light; push + punch-in. | — | Rain barely reads; ship small in frame. |
| S06 | Top-down: DSV drifts left->right off a dashed yellow target outline through whitecaps. | — | Foam patches chunky. |
| S07 | Close on the roof corner: umbilical swept sideways, catches and bends sharply around the corner; strain glow; silt puff. | Card y 1200 -> 150. | — |
| S08 | Same set: part at f4 (flash ball + light spike, recoil, glow drain, bubble burst, helmet light dies, 6-frame shake), then near-black. | — | Mostly dark by design. |
| S09 | Diver hand-over-hand along a sloped grab rail onto the roof, then curls; orbiting camera following him. | Lit brighter than "near-black" so the silhouette reads on phones. | — |
| S10 | Curled diver, close on bailout valve; last bubbles thin out and stop; exposure fades to -3.2 stops. | — | — |
| S11 | Split-level "tank" cross-section: night surface/sky with DSV above, water volume below, bell (lamps) descending on its wire, dashed vertical position marker. | — | Ship cropped at frame left. |
| S12 | Yuasa (red hat) swims in from upper-left, torch spot + beam cone finds Lemons curled on the roof. | Camera to the rescuer's side (beam reads better than straight over the shoulder). Name card y -> 1420. | Rescuer mostly out of frame (red helmet at edge). |
| S13 | Low angle up at the bell's glowing hatch; Yuasa tows limp Lemons upward; warm spot down from the hatch. | — | — |
| S14 | Bell interior cutaway: half shell + dome, floor, bench, gas panel, lamp, trunk water; Lemons lying, Allcock kneeling at his head, head lowering rhythmically (profile). | Lemons lying (not slumped) so both silhouettes read. Name card y -> 1420. | — |
| S15 | Same set: chest rises twice, Allcock sits back, lamp brightens ~30%, lens 44->58. | — | Push reveals cut edge of the set at frame right. |
| S16 | Blue water-field diagram, x-ray glow outline figure, thermometer bar drains red->blue, frost shimmer. | — | — |
| S17 | Same figure; warm head glow cools/dims, O2-demand gauge needle falls; camera rises toward the head. | Thermometer dropped (gauge needs the space). Text y -> 1420. | — |
| S18 | Empty roof, severed stub drifting with a faint cyan tip. | Higher camera than S01 so the stub on the roof reads. | — |
| S19 | S01 set intact (light on, umbilical glowing); camera ends exactly on S01 frame 1 (loop). | — | — |

## Script fixes (overlay params)
S04/S12/S14/S17 text y 1250 -> 1420; S07 card y 1200 -> 150. Narration untouched.
