# MURDER-07 Animation notes (Oetzi, the oldest cold case)

Files: `BLENDER_PROJECTS/MURDER-07/shots.py` (no render.json: no speckly shots after the ice moved to BLENDED alpha).
New builders appended to `PIPELINE/blender/lib_murder.py` (nothing above changed): `mat_glacier_ice`, `abstract_form`, `ice_sheet`,
`melt_beads`, `ice_axe`, `helicopter`, `kneel_pose`, `glow_lines` (many polylines in one curve), `key_strength`, `circle_pts`,
`xray_back_lines` (original stylised back-view chest art), `arrowhead`, `lightbox`, `film_sheet`, `ct_gantry`, `copper_axe`,
`flint_dagger`, `bow_stave`, `quiver`, `einkorn_ear`, `meat_strip`, `herb_sprig`, `ibex_outline`, `side_figure_outline`, `traveller`, `pose_keys`.
Preview rounds: 3 (round 1 full, rounds 2-3 with --only) plus single-still checks of S15/S01/S06 (540 px: ~6-8 s incl. compile).

Body rule: Oetzi is never shown. S01/S06 = an unreadable dark lump deep under cloudy ice; S04 has NO body bundle (team kneels around
the gully); S12 has NO covered form (a sealed grey storage case on the CT table instead); S17 cell contents hidden by frost; S14 =
distant traveller silhouette, labelled DRAMATISATION. X-ray/CT art is original line art, back view (patient's left = viewer's left).

script.json overlay fixes (narration untouched): S03 stamp y 300 -> 170 (collided with the map title), map `land` = rough outline
(was a full square) and `points` = border trace with pin on the Tisenjoch (pin index 3); S04 card y 820 -> 1420 and S15 card y 820 -> 1420
(cards covered the key subject); S05 text y 760 -> 940 (covered the monitor readout); S08 timeline events 3300 BC (died) -> 1991 (found) -> 2001 (?).

| Shot | Built | Notes |
|---|---|---|
| S01 | 85 mm glide over glacier ice at dawn, meltwater beads (6 sliding), red evidence string + tag, vague dark lump under ice. | Lump is a soft dark band only. |
| S02 | Bright saddle, background range, gully with dark meltwater + rim rocks; red/blue hikers walk in, stop, turn, A points; push past a boulder. | Hikers ~22-28% height at the end. |
| S03 | Dusk aerial Alps plate (mostly under the map card). | |
| S04 | Overcast; 2 rescuers + 1 dark-jacket kneel round the gully, standby figure, helicopter with idling rotor; rack focus from ice axe on a rock to the group. | Deviation: no body bundle. Kneel poses blocky. |
| S05 | Lab desk, hanging lamp, two vials, monitor "RADIOCARBON DATE" stepping AD 1991 -> 3300 BC (red) by f44 with progress bar; push vial -> monitor. | |
| S06 | Golden hour; crane from the ice patch in the gully out to the whole pass. | Lump unreadable as specified. |
| S07 | Three black turntables: copper axe, flint dagger, yew stave + quiver; quick slides at f26-31 and f56-61; warm key + cool rim. | |
| S08 | Board: CAUSE OF DEATH card, red ?, Tisenjoch / FOUND cards, strings, lamp; slow push. | |
| S09 | Lightbox flickers on (never black), back-view chest art, arrowhead faint top-left; push to the left shoulder. | |
| S10 | Snap-zoom (7 f) to the arrowhead, pulse + red ring draws; at 1.6 s art fades to a faceless side-profile outline, dashed trajectory from behind/below, impact dot; pull back. | Deviation: side profile instead of back view so "from behind" reads. |
| S11 | Double lightbox; warm 26 SEP 1991 film slides in beside the 2001 one; red ring draws on the old film; lateral move. | |
| S12 | CT room: gantry with glowing bore and spinning markers, case slides in, side monitor flicks slices; 28 mm arc. | Deviation: case, not covered form. |
| S13 | Push through a monitor bezel into a 3D line diagram: clavicle, ribs, scapula, humerus; red artery splits at f36-42 as the arrowhead seats; slow orbit. | |
| S14 | Dusk ridge, traveller (cap, cape, bow stave, axe) walks away and slows, turns and sits against a rock; snow starts f30. | DRAMATISATION; figure ~20% height (restrained). |
| S15 | Dark stone: einkorn ears, two dried-meat strips, herb sprig, flickering off-frame fire, few embers; ibex line art draws on above. | Ibex horns touch the top edge at the end. |
| S16 | Board: CAUSE OF DEATH ARROW, SHOOTER UNKNOWN, drawn arrowhead card; red string to an empty pin + faint empty slot; push to the empty slot. | |
| S17 | Museum wall, steel-framed window with frost, blue cell, haze; push until frost fills the frame (matches S01 ice for the loop). | Tray barely visible behind frost (by intent). |

Weakest: S04 (blocky kneel poses), S12 (simple gantry), S14 (small silhouette), S15 (ibex at top edge at the end).
