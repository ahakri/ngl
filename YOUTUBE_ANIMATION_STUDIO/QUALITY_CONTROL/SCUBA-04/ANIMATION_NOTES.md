# SCUBA-04 — Animation notes

Builders: `BLENDER_PROJECTS/SCUBA-04/shots.py` + new lib functions in `PIPELINE/blender/lib_scuba.py`
(humpback: lofted body with lid/baleen underside, hinged lower jaw + pleated throat pouch, pectorals, fluke, tubercles;
whale_swim, jaw_keys; lobster_boat; lobster; bubbles_at; exposure/emit/energy keys; shake). SCUBA-01/02 functions untouched.
No gore: the mouth interior is soft dark tissue, baleen curtains, light slit, pooled bubbles. People are faceless.
Preview rounds: 3 (round 3 = --only S01,S15,S16,S17); S15/S16 final boat-deck fix verified with single-frame test renders.

| Shot | Built | Deviations / why | Known weaknesses |
|---|---|---|---|
| S01 | Packard horizontal on caustic sand reaching for a lobster by a rock; humpback descends from above, jaw opening; f65 hard black (occluder sphere + sun/caustics off, faint leak light on bubbles) + 4-frame shake. | Blackout at f65 (2.7 s) to land on "The next, everything went black" (word timings) rather than the 55% mark. | Whale only reads as darkening/shadow before the black; lobster small. |
| S02 | Aerial green water + sand, lobster boat (under map card). | — | Background only. |
| S03 | Split-level "tank" section: boat bobbing on sunny surface, Packard descends feet-first in green water with bubble bursts, sun shafts; camera tilts down. | Name card y -> 1420. | Diver small in the wide. |
| S04 | Imagined shark flashing past in black water, lit from below, whip-pan, motion blur. | — | — |
| S05 | Mouth interior: Packard silhouette (rim from the lip slit), pats arms, reaches to the soft wall; bubbles pool on the roof. | — | Head reads big; very dark by design. |
| S06 | Pull-back from the closed lips to the whole whale (throat distended), soft glow marker, fish, shafts. | Pull-back 15 m (24 m left the water volume). | Glow marker faint. |
| S07 | Side wide: humpback rises at an angle, jaw drops, engulfs the fish school + diver (hidden on entry), sand puff. | Text y -> 1420. | Fish school faint. |
| S08 | Close orbit on head/regulator inside the mouth, rhythmic bubbles, valve glint, pooled bubbles. | — | — |
| S09 | Curled diver, slit flickers, room sways; heartbeat beat. | — | Dark. |
| S10 | X-ray diagram: whale standing snout-up (fits 9:16), edge-glow line art, mouth cavity, tiny diver, pulsing red throat; zoom to throat. | Whale vertical instead of horizontal profile (frame is portrait). | — |
| S11 | Close diagram: red fist-sized throat ring, fist icon pops beside it, diver x-ray outline far wider below. | Overlay "≈" -> "~" (glyph safety); y -> 1420. | Fist icon blocky. |
| S12 | Mouth interior tilts 25 deg up (whale rising), slit brightens; timer overlay. | — | — |
| S13 | Bright surface: whale head breaches (pleats, tubercles), foam ring, splash droplets, mist; head swings; lips part with light. | — | Foam ring reads as a flat plate. |
| S14 | Jaw opens, Packard tumbles out (hidden until ejection), foam/bubbles/splash, whale rolls and sinks; 2-frame exposure flash. | — | Tumble pose a bit stiff. |
| S15 | Boat motors in bow-first; Mayo (cap) leans over the gunwale; Packard hauled up the hull. | Name card y -> 1420. | — |
| S16 | Aft deck: Packard seated against the bulwark, mask/fins/tank beside him, warm sun, boat rock. | Card y 1200 -> 150. | — |
| S17 | S01 set, camera ends exactly on S01 frame 1; whale passes overhead so its shadow sweeps the sand at the end. | Shadow instead of visible body (top of frame is ~7 deg above horizon in this framing). | — |

## Script fixes
S03/S07/S11/S15 text y 1250 -> 1420; S16 card y 1200 -> 150; S11 "≈" -> "~". Narration untouched.
