# MURDER-02 Animation notes (Somerton Man / Tamam Shud)

Files: `BLENDER_PROJECTS/MURDER-02/shots.py`, builders in `PIPELINE/blender/lib_murder.py` (desk, desk_lamp, rolled_scrap,
book, suitcase, luggage_shelf, folded_jacket, scissors, plaster_bust, tweezers, test_tube, dna_helix, tree_lines,
headstone, work_light, seawall, sea, surf_line, dawn_sky, seated_pose). Preview rounds: 1 full, 1 full, 1 partial (--only).

| Shot | Built | Deviations / notes |
|---|---|---|
| S01 / S22 | Macro on dark wood under a warm desk lamp: tiny rolled paper strip with sand grains; tweezers come down and drag the free end so it unrolls (shape key) to show "Tamam Shud" in serif. S22 pushes in and ends on S01 frame-1 framing (loop). | 60 mm instead of 85 mm so the strip fits. |
| S02 | Blurred macro plate of the unrolled strip under the scrap document overlay. | - |
| S03 | Pre-dawn beach plate (pink-grey sky, houses, pines, seawall, warm lamps), slow drift; map overlay on top. | - |
| S04 | Wide from the sand: seawall across frame, distant faceless seated silhouette (seated_pose: legs out, head bowed, < 8 % frame height), warm promenade lamps, mist, truck right. | - |
| S05 | Top-down on the desk: folded dark jacket + tie, stitched empty rectangle where the label was, scissors; slide toward the collar. | - |
| S06 / S07 | Station cloakroom: shelves of old suitcases, single flickering hanging lamp; one suitcase slides forward into the light. S07 close on the handle: empty tag string with only a torn stub left. | - |
| S08 | Hardback drops onto the desk, the strip slides in and lines up with the book edge; glowing match line; slight orbit. | Simplified the "snap into torn page" into an edge match. |
| S09 | Book cover close: recreated generic title THE RUBAIYAT OF OMAR KHAYYAM (gold serif, no publisher marks). | - |
| S10 | Book flips to the back cover; faint violet UV sweep brings up pencilled code lines; phone number is unreadable smudges only. | - |
| S11 / S20 / S21 | Code-page desk plates (back cover, soft focus) under the document overlays, progressively tighter. | - |
| S12 | Dim desk plate, featureless plaster bust in the dark background with a cold rim. | Weak plate; the inquest card carries the beat. |
| S13 | Cork board: SPY / LOST LOVE / SUICIDE cards slam in with THEORY badges, red strings to a blank silhouette card with "?". | - |
| S14 | Night cemetery: rows of headstones in ground fog, one plot taped off and lit by a tripod work light (flicker), crane down. No digging, no remains. | - |
| S15 | Lab bench: featureless plaster bust, tweezers lower a single hair into a glowing tube; push to the tube. | - |
| S16 | Emissive DNA double helix (spheres along two spirals + rungs) rotates, shrinks away, family-tree lines draw on converging on an empty name slot. | - |
| S17 / S18 | Same tree graphic: slot fills warm amber (cold to warm flip), push-in (S17); S18 shake on the stamp. | No photo of Webb, name only via overlay. |
| S19 | Sunrise, empty seawall, warm low sun, slow push along the wall. | Sea/wash not in frame (camera looks along the wall). |

Overlay label fixes in script.json: S11 `UNSOLVED` -> `DOCUMENTED FACT`; S16 `GENETIC GENEALOGY` -> `THEORY`.
Note: the code document overlays still print the literal text "[crossed out]" (overlays.py has no strikethrough).
Known weaknesses: S12 plate very dark; plaster bust is a simple primitive form; S19 has no visible surf; desk shots are warm-heavy.
