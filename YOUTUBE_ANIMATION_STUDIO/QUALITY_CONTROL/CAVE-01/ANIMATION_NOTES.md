# CAVE-01 Animation Notes (Dave Shaw, Boesmansgat)

Builders: `BLENDER_PROJECTS/CAVE-01/shots.py` + shared `PIPELINE/blender/lib_cave.py`.
Preview rounds: 2 full and 2 targeted (S08/S10, then S08).

| Shot | Built | Deviations / weaknesses |
|---|---|---|
| S01 | Chamber floor (silt and boulders), abstract lost-diver marker (half-buried tank, two fin blades, low silt mound), torch sweeping left to right onto it, cyan back-rim light, volume water, fine silt, push-in | Torch pool is warm and bright. The lower 40% is dark, which is fine because captions sit there. |
| S02 | Shaw (black suit, yellow fins, rebreather box and counterlungs) hovering in trim, torch angled down onto the marker, two cyan rim lights, silt from fins, pull-back | None |
| S03 | 2.5D rock-slab section: crater, pool, throat, bell chamber, depth ruler. Cyan dot drops quickly, then a dotted ascent with deco-stop ticks; 5% lens zoom | The vertical scale is compressed to keep the floor above the caption zone. |
| S04 | Desert sinkhole (annular ground, rock pit, dark green pool), scrub, bare trees, dive platform and line, dawn sun, descending crane | Sun shadows are soft and short. |
| S05 | Vertical rock shaft, head-down descent beside a tagged shotline, torch into the black, cyan daylight from above, 5 deg roll | Fins sit close to the top edge. |
| S06 | Helmet-POV camera with its own torch, scan, then a fast pan that stops dead on a tapered fin blade in silt | No diver; this is POV by design. |
| S07 | Heavily defocused chamber behind the memorial card overlay | The overlay was changed to `card` (the document style `evidence_card` doesn't exist). |
| S08 | Rim at dusk: Shaw's silhouette at the edge, three team silhouettes, tank stack, coil, crate, dolly-in | The `char_figure` silhouettes are stiff. |
| S09 | Section diagram with cyan Shaw descending to the floor, orange Shirley stopping at 220, dashed rendezvous line popping on, pan down | None |
| S10 | Shaw kneels (upright pose) beside the marker, a dark bag unfolds, a floor lamp, silt lifts at the knees, 20 deg orbit, rim lights | The kneel reads more as hovering-crouched. |
| S11 | Pattern interrupt: two glass breathing-loop rings. Surface ring has sparse, fast gas; 270 m ring has packed, crawling gas that squeezes on each breath | The difference is clear at 1080 but subtle at preview size. |
| S12 | Close macro of the forearm, torch canister, and lines looped around them; jerky pulls; silt plume volume and fine particles swallow the beam; flicker; rising shake | A few particles still read as specks. |
| S13 | Same diagram: Shirley waiting at 220, cyan Shaw dot fades, red rendezvous line blinks, empty marker ring | None |
| S14 | Shirley (orange fins) descends past the 220 m tag and strobe into an open chamber, torch sweep, dutch tilt to 8 deg, DOF | No real edge blur; DOF stands in for it. |
| S15 | Helmet-cam UI: viewfinder brackets, crosshair, blinking REC dot, battery, animated static and scanlines over a green-tinted silt plume, slow zoom | The overlay "● REC" became "REC" (Anton has no ●). |
| S16 | 3D case-report page slides in and tilts flat, the highlight bar grows, push onto "EXTREME HYPERCAPNIA → UNCONSCIOUSNESS" | The document overlay was replaced by a DOCUMENTED FACT label so there aren't two pages. |
| S17 | Looking up the throat: cyan-lit rock tube, bright rippled surface disc, fake god rays, three haul lines with tags surging upward hand over hand | None |
| S18 | Two dark abstract shapes bound by white loops rise slowly against the bright opening | Very abstract by design. |
| S19 | Crane down into the sunrise pit and pool, then a hard cut (last 12 frames) to the S01 framing with the floor now empty (loop) | The pit is mostly in shadow, so the sunrise feel is weak. |

Script.json overlay fixes: depth `from/to/max`, timers `from/to/fmt/y` with start/duration sequencing, labels set to DOCUMENTED FACT, text colours as RGB lists, sizes as ints, a card for S07, and y positions kept clear of captions.
