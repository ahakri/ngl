# MURDER-03 Animation notes (D.B. Cooper / Tena Bar)

Files: `BLENDER_PROJECTS/MURDER-03/shots.py`; new builders appended to `PIPELINE/blender/lib_murder.py` (MURDER-01/02 functions untouched):
`jet727` (stylised 727, no livery: lofted fuselage with red cheat-line + warm window dots in one shader, swept wings, T-tail,
three tail engines, hinged ventral airstair with glowing opening, optional Cooper vane, beacon), `stair_anim`, `beacon_blink`,
`rain` (seamless looping streak prisms, CYCLES-modifier loop), `cloud_volume` (noise storm cloud with drift), `lightning`
(sun + world-strength strobes), `storm_sky`, `parachute`, `mat_bill`/`bill_brick`/`loose_bills` (generic green paper, no
currency art), `rounded_box`, `parachute_pack`, `money_bag`, `cabin_727`, `mat_wet_apron`, `flood_mast`, `boarding_stairs`,
`riverbank`, `driftwood`, `rotten_bundle`, `glow_poly`/`rect_pts`, `hangar`, `suspect_wall`, `red_string`, `glass_drops`,
`bokeh_lights`, `fast_conifers` (vertex-list forest; casts no shadows by default - thousands of shadow casters cost ~5x render time).
Jet layout: nose +X, tail -X, stair hinge at local (-14, 0, -1.78). Preview rounds used: 3 (rounds 2-3 with --only).

| Shot | Built | Deviations / notes |
|---|---|---|
| S01 | Low angle under the 727 tail in rain: open airstair with warm spill, suited silhouette with chest bag on the lowest step; leans and drops on "jumped" (f56), stair springs up and settles, lightning flash, beacon, cloud deck + ceiling, handheld push. | Jet is static; rain/cloud stream past to sell flight. |
| S02 | Freefall: silhouette (arms spread, coat flapping) with khaki bag on the chest, rain + cloud streaming upward, 5 generic bills tumbling, orbiting camera, lightning rim. | Whole figure in frame (torso-only read as a blob). |
| S03 | Rain-on-glass plate: drops mesh + trickling drops, defocused city/airport bokeh. | Plate under the map card. |
| S04 | 1970s cabin (orange/brown seats, round windows, overhead strip). Hijacker seated on the aisle extends a note; uniformed attendant (navy silhouette) reaches and takes it; DOF on the note, dolly. | Camera from across the aisle (rear-facing dolly put the attendant in front of the hijacker). |
| S05 | Dark briefcase on the aisle seat under a single top spot, motes, cabin dim, slow push. | - |
| S06 | Top-down dark desk: four parachute packs (olive/white) slam in on the 4 beats with dust puffs + micro shake, banded bill bricks. | Red under-rim is subtle. |
| S07 | Wet apron at night: 727 under sodium masts, front door glowing, boarding stair, 9 passengers walking away, courier with bag toward the tail, rain, truck right. | Light sodium haze. |
| S08 | Above the moonlit cloud tops: small 727 with blinking beacon heading away (map plate). | - |
| S09 | Aft-quarter tracking view: airstair hinges down 0-35 deg with warm spill, lightning backlight every ~1.5 s, rain, cloud deck. | Changed from pure side view (wing hid the stair). |
| S10 | Straight down from the stair: silhouette falls away, striped canopy blooms (f22) with a lightning flash, cloud with gaps over dark forest, slow roll. | Forest below is very dark by design. |
| S11 | Overcast grey-green forest: three searchers in ochre rain jackets with torches walk in a line; camera cranes down from tree height. | Short shot; trees are low-poly cones. |
| S12 | Winter daylight Tena Bar: rippled sand bar, grey river, far wooded shore, kneeling child silhouette sweeping sand, parent carrying driftwood behind, mist, push-in. | - |
| S13 | Macro top-down: sand mound sweeps away (shape key) revealing three swollen, mould-edged bundles with perished bands, falling grains, rack focus. | Bundles are generic (no banknote art). |
| S14 | Desk: generic bill fragment with placeholder serial, microfilm strip of placeholder serials; highlight bar scans to the match, red link + rings draw on, push-in. | - |
| S15 | Moonlit winding river through dark forest from above (map plate). | - |
| S16 | Cork board: "TENA BAR, 1980" rendered photo card; WASHED DOWNSTREAM? / BURIED? / ? cards slam in on the beats, red strings draw to the photo. | - |
| S17 | Night rain over forested hills, tilt from cloud ceiling to treetops, faint lightning. | - |
| S18 | Dim hangar under the 727 tail: vane flips into the airflow, stair tries to drop and is blocked (twitches), blueprint airflow lines + arrows + vane box draw on, small orbit. | Weakest read: the stair/vane are small; relies on the card. |
| S19 | Macro on the vane: paddle snaps into place, glows red, red outline draws round it, blue blueprint lines fade. | Out of context (black) by design. |
| S20 | Dark desk: manila NORJAK folder, ledger, lamp (document plate). | Mostly covered by the document. |
| S21 | Huge wall of ~540 faceless suspect cards, cold lamp, fast pull-back. | - |
| S22 | Dawn forest clearing with ferns and a short line of fading footprints, ground push then crane above endless treetops. | Trees are crude at ground level; dark. |
| S23 | Same set as S01: silhouette walks down the stair to the lowest step; camera ends exactly on S01 frame-1 framing (loop). | - |

Overlay params checked against overlays.py: all valid, no changes needed.

Render cost: measured ~7-10 s/frame at 540 with the machine at load 13-15 (render queue + other agents); expect ~3-4 s isolated.
Heaviest: S01/S23/S09 (two cloud volumes + rain), S22.

Known weaknesses: figures are the house mannequin silhouettes; S18 hangar read; S22 forest low-poly; S03/S08/S15/S20 are plates under overlays.
