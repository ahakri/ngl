# SCUBA-06 — Animation notes

Builders: `BLENDER_PROJECTS/SCUBA-06/shots.py` + new functions appended to `PIPELINE/blender/lib_scuba.py`
(great_white: lofted countershaded body, dorsal/pectoral/caudal fins on a tail pivot, small black eyes, gills, mouth
line; gw_swim; spearfisher: 1963 breath-hold diver, no tank, snorkel, weight belt, long fins, speargun (scuba=True for
the cage shots); float_buoy; dinghy; shark_cage; film_housing; polyline; torso_diagram; film_grain). Existing
functions untouched (SCUBA-05 additions also live there). studio_lib.shark not used: its ellipsoid body read as a blob.
NO WOUNDS anywhere: the attack is a whip pan + white flash frame + churned bubbles/silt; injuries are an abstract
line diagram (ribs flicker red, lung outline shrinks, stitch ticks). People are faceless silhouettes.
Preview rounds: 3 (round 2 = --only 14 shots, round 3 = --only S01,S04,S05,S06,S13,S14,S17,S18).
render.json: S08, S11 at 4 samples (sea glints).

| Shot | Built | Deviations / why | Known weaknesses |
|---|---|---|---|
| S01 | From 6 m below: Fox silhouetted at the bright surface with float + line; great white rises from the bottom of frame toward him; push-in. | — | Water reads pale/hazy (bright surface glow). |
| S02 | f1-45 aerial (under map card); f46 water-line view: Aldinga beach + ochre cliffs, reef band, dinghies with figures, competition floats, swimmers. | Stamp start 1.9 s (after the map). | Elements small; flat water. |
| S03 | Half-over/half-under: Fox breathing at the surface (chest rises), duck-dive at f49, camera follows below; line-art tank icon + red strike at "no tank". | Breath-hold timer y 1250 -> 1450. | Fox small at the waterline before the dive. |
| S04 | Side-on: Fox gliding down over sand/rocks/weed; shark whips in from the left, white flash frames f17-19 at contact, Fox gone; shark exits; churned bubbles + silt bloom; shake. | — | — |
| S05 | ECU on the shark's eye; silhouette hand reaches in and touches it (f40); shark peels away, camera pulls back 50->24 mm, Fox tumbles free in bubbles. | — | Eye close-up overexposed in round 3; lights lowered afterwards (cam fill 30->10, rim 120->40) WITHOUT a re-preview (3-round bound). Hand reads blocky. |
| S06 | Looking up: orange float on the surface, taut line down out of frame; shark rises, seizes the float (f33) and drags it under; camera tilts down with the line. | — | — |
| S07 | Close on the belt from above-side: two dark gloves work the knot, line jitters taut, slips loose at f31 and whips away; strong handheld. | Camera above the hips (from below the bright surface washed the frame). | Gloves blocky; belt ring reads large. |
| S08 | Day surface: wooden dinghy arrives L->R, two crew silhouettes lean over and haul the dark figure up over the gunwale. | — | — |
| S09 | Line-art torso on black: patient's-left ribs flicker red one by one, left lung outline deflates. | Label DOCUMENTED -> DOCUMENTED FACT. | — |
| S10 | Same diagram: stitch ticks draw across chest and down the left arm in sync with the 462 counter; shake at f98. | — | — |
| S11 | Warm late light; faceless figure waist-deep from behind looking out to sea; slow push. | — | Figure blocky; sun-glint smear on the water. |
| S12 | Lobster boat + davit: cage swings, drops (splash f20), camera dips under to watch it sink on its wire. | — | Short shot (43 f). |
| S13 | Inside the cage (stylised 2.4 m tall so the diver fits): Fox on scuba grips the bars; shark crosses L->R outside. | Cage taller than 1.8 m spec (diver + fins would not fit). | Fox mostly head/arm in frame. |
| S14 | Over-the-shoulder of a second diver with a boxy cine housing; shark approaches and turns. | — | Housing at frame edge. |
| S15 | Camera POV through bars: sepia-teal water, film grain/vignette overlay, gate-weave handheld; shark passes close and turns. | — | Grain intentionally noisy. |
| S16 | Time-lapse: modern dive boat with cage alongside off a rocky coast; sun swings/warms, boat leaves and returns. | Timeline y 1250 -> 1560. | Cage barely visible. |
| S17 | Calm shark (small satellite tag on the dorsal) passes a cage; camera tracks parallel; camera-parented corner brackets, pulsing dot, "TRACKING" readout. | Card y 1150 -> 1420. | Front/rear body seam ring visible near the tail. |
| S18 | S01 set; camera and shark end exactly on S01 frame 1 (loop). | — | Shark only a nose at the bottom until the end. |

## Script fixes (overlay params)
S03 timer y 1450; S09 label DOCUMENTED FACT; S16 timeline y 1560; S17 card y 1420; S02 stamp start 1.9. Narration untouched.
