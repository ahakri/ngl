# SCUBA-01 — Animation notes

Builders: `BLENDER_PROJECTS/SCUBA-01/shots.py` + shared `PIPELINE/blender/lib_scuba.py`
(tug hull, inverted compartment, water surface, hands, rescue diver, chamber, beams, scanlines, ocean...).
Okene is always a faceless dark `char_figure` silhouette. No bodies, no crew casualties shown.

## Shots
| Shot | Built | Deviations / why | Known weaknesses |
|---|---|---|---|
| S01 | Inverted compartment (lib `inverted_compartment`: overhead deck grating, hanging toilet, upside-down basin, pipes, door opening to the overhead), water volume to 1.2 m + reflective rippled surface, Okene treading water with head/shoulders in the pocket and a hand on the basin, floating flashlight with beam into the water, debris + drips, slow push. | Built upside-down in world space with an upright camera (same read as "camera roll 180", simpler lighting). Cutaway open front. | Figure is small-ish; most of the lower frame is murk (caption zone anyway). |
| S02 | Night/dawn ocean (Ocean modifier), lofted tug (black/red hull, white deckhouse, lit windows, funnels, winch, fenders), rolls over past 90 deg and settles keel-up; spray + rain. | Map overlay limited to the first 1.9 s (`duration`) so the capsize (second half) is not hidden by the 900 px map card. | Rain reads a bit like stars. |
| S03 | Upright toilet compartment (same builder flipped), camera parented to the rolling room, hanging bulb counter-rotated so it swings in frame, bucket + water sheet slide, door slams, bulb flickers and dies. | — | The "world tipping" is subtle at preview size; relies on bulb swing + sliding props. |
| S04 | Capsized tug sinking keel-up onto a silty bed, bubble trails, silt burst on landing (~2.4 s), camera tilts down. | Volume as a big cube (world volume absorbed the sun completely in EEVEE Next). | — |
| S05 | Custom inverted corridor (doors reaching the overhead, dead lamps on the bottom), water to near the top, POV under the surface with Okene's hand + flickering torch, warm glint at the end doorway. | Own corridor geometry instead of `L.corridor` (needed inverted doors + end doorway). | Darkest shot of the video; reads mostly as "dark flooded passage". |
| S06 | Flat blueprint cutaway: inverted hull section, flooded interior, warm air pocket, black figure, yellow bracket drawing on waterline->overhead; ortho camera, slight push. | — | — |
| S07 | Close at the waterline: head profile, breath vapour puffs, neck ripple rings, drips; pocket light drifts warm->sickly. | — | Head is a plain sphere (faceless by design). |
| S08 | Wreck keel-up on the bed, marine snow, sparse fish school, very slow pull-back. | — | — |
| S09 | Two helmeted divers (lib `rescue_diver`: yellow/white hard hats, umbilicals) descending a down-line toward the hull, torch beams (spot + fake beam cones). | High oblique instead of pure top-down so the divers read as figures. | Divers read thin at phone size; beams carry the shot. |
| S10 | Diver A tracks along the hull side, torch sweeping the deckhouse portholes, silt kicked up. | Telegram card moved to y=150 (was centred over the diver). | — |
| S11 | Helmet-cam POV in a flooded closed compartment: scanlines/vignette plane on the camera, blinking REC dot, torch sweep finds a hand coming down from the air pocket. | Desaturated look done in-scene (no compositor in the pipeline). Timecode text dropped (rendered as bars). | Monitor look is mild; overlay "HELMET CAM" does the labelling. |
| S12 | Same set, slow push; diver glove with orange cuff reaches from frame bottom-right toward the still hand. | — | Glove is dark; reads mainly by the cuff. |
| S13 | Real-render close-up: Okene's hand from above closes on the glove (finger curl rig), snap zoom (lens 40->62), torch flare, bubble burst. | — | Stylised block hands. |
| S14 | Air pocket wide, diver helmet surfaces beside Okene, ripple rings, warm torch bounce, slow arc. | — | — |
| S15/S16 | X-ray body (fresnel glow), gas dots fill (S15) then swell; arrow up, red X pop with shake (S16). | — | — |
| S17 | Night deck: white decompression chamber (porthole glow, hatch with wheel), hatch swings shut, two hard-hat crew silhouettes, sodium floods, steam, rain, push toward the porthole. | Camera from the hatch end so crew + porthole share the frame. | — |
| S18 | Defocused air-pocket background under the timeline overlay, slow pan. | Label "EXPERT ESTIMATE" -> "THEORY" (allowed label set). | — |
| S19 | Air pocket, diver torch settles onto Okene. | — | — |
| S20 | S01 set + rescue diver pushing in from below the waterline; camera ends exactly on S01's first frame (loop). | — | — |

## Script fixes (overlay params)
- S02 map: `duration: 1.9`. S09 timer `y: 430` (clear of the stamp). S10 document `y: 150`.
- S15 label "DOCUMENTED" -> "DOCUMENTED FACT"; S18 label -> "THEORY".

## Render cost
Contended machine (load 15+ on 4 cores) made timing unreliable: ~10 s/frame at 270 px, first frame +50 s shader compile.
Interior volume shots are the heaviest. `lib_scuba.setup()` uses raytracing off, volumetric tile 8 / 24 samples to keep cost down.
