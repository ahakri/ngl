# MURDER-08 Animation notes ("Who put Bella in the Wych Elm?", Hagley Wood 1943)

Files: `BLENDER_PROJECTS/MURDER-08/shots.py`, `render.json` (S06/S07/S13 at 4 TAA samples: volumes / noisy bark). New builders appended to
`PIPELINE/blender/lib_murder.py` (block "MURDER-08 ... builders"; nothing above it changed): `mat_sooty_brick`, `mat_cobbles`, `mat_chalk`,
`stroke_text` / `chalk_text` (own single-stroke capitals; static, or every stroke drawn on in writing order), `chalk_follow`, `chalk_dust`,
`hooded_lamp`, `sandbags`, `blackout_facade`, `mat_bark_old`, `wych_elm`, `hollow_interior`, `mat_season_ground`, `key_socket`, `obelisk`,
`archive_shelves`, `flat_figure`, `stamp_mark`, `wood_ladder`, `canvas_screen`, `plain_shoe`, `gold_ring`, `striped_scrap`, `paper_tag`,
`wind_grass`, `falling_leaves` (+ private `_bx`, `_taper_tube`). Reused: lib_haunted figures / helmet / hand torch / `bare_forest_z`,
lib_murder evidence board, cards, slam-in, strings, newspaper, desk, lamp, typewriter, case folder, snowfall; lib_scuba `rubber_stamp`.
Preview rounds: 3 (1 full, 2 and 3 with --only). Build-only dry runs (no render) were used to check framing numerically.

Respect rules as built: the woman is never shown. The elm's hollow and side cleft are unlit black faces - nothing is modelled inside the
tree in any shot; S06 looks only upward. Boys = four small faceless capped figures, always from behind, never named. S10 props are generic
(plain shoe, plain band, striped scrap, blank tags). No names, no suspects, no masthead on the cutting.

Wording: the brief's shorthand "WHO PUT BELLA IN THE WYCH ELM?" was NOT used on the brick wall; the fact-checked variants were:
S01/S20 "WHO PUT BELLA DOWN THE WYCH ELM - HAGLEY WOOD" (Birmingham 1944), S12 "HAGLEY WOOD BELLA" (written on stroke by stroke),
S19 "WHO PUT BELLA IN THE WITCH ELM" (obelisk). S13 shows the main question and a second "HAGLEY WOOD BELLA" in the torch beam.

script.json overlay edits (narration untouched): S15 text `start` 0.3 and S17 text `start` 0.25 (word lands with the stamp hit, not before it);
S18 document `start` 1.5 (the full-frame paper otherwise hid the shelf gap for the whole shot) and S18 label y 200 -> 1430 (it sat on the
paper's first line); S19 memorial text y 880 -> 1025 (it covered the painted question).

| Shot | Built | Notes / deviations |
|---|---|---|
| S01 / S20 | Sooty brick, chalk question in 5 lines above the caption band, hooded lamp from upper right with buzz + dip, motes, fog. Linear push; S20 ends exactly on S01 f1 (same per-frame speed, no handheld, lamp at base level on both frames). | Brick reads fairly warm under the lamp. |
| S02 | 28 mm pull-back: boarded two-storey front, taped upper windows, sandbag wall, wet setts, neighbours. | Text small by the end; left of frame dark. |
| S03 | Blue dusk glide (24 m -> 10.6 m) to the elm through mist; a few falling leaves. | WEAK: elm is low-contrast in the haze until the last third. |
| S04 | Under the map card, then four boys walk away into the wood, the elm far ahead right. | Plate hidden by the map until 2.3 s (by design). |
| S05 | Three boys watch from below, one climbs the bole and leans over the rim; push-in from behind. | Storyboard low-angle close view replaced by the brief's far-from-behind view. WEAK: climber is a small dark shape at the rim; standing boys are stiff. |
| S06 | Look-up POV in the hollow: dark wall, jagged rim, shoots, sky; boy leans in f1-15, jerks back f27-35; a leaf falls. | Camera 1.3 m below the rim (not the bottom) so the opening is ~45% of frame. Bark is grainy (4 samples). |
| S07 | Dusk search: constable with raised lantern at a ladder, second constable walks in with a lantern, detective in hat and coat, canvas screen; lateral move behind two foreground trunks. | Screen is already up (not being raised). Trunks cross at ~f15 and ~f60; a trunk sits at frame edge on f1/f75. |
| S08 | Locked time-lapse, 18 months: day/night x4, snow twice, green + leaves in summer, leaf fall twice; counter above the bole. | Leaves pop in over ~7 frames. |
| S09 | Dark painted height chart with pale 6-inch lines and 4/5/6 FT labels; flat grey outline slides in to the 5 ft line, red marker pops f24. | Chart is dark with pale lines (inverted from the storyboard) so the white overlay text reads. |
| S10 | Top-down blotter: shoe, plain ring on a pad, striped scrap, three tags, lamp; slow roll + push. | Shoe is simple; card overlay sits just under the props. |
| S11 | Record sheet with a printed NAME line left empty, open file, typewriter keys tap and carriage stops at f20. | NAME rule sits just under the scrap overlay; carriage is at the very top / partly out of frame. |
| S12 | Different wall (pier, tar dado, lamp from upper left): HAGLEY f6-34, WOOD f37-56, BELLA f60-92, chalk stick follows and drops, dust puffs. | f1 is a bare wall (under the flash transition). |
| S13 | Street along the front: constable enters right, torch beam sweeps from the second message over the main question to the door; far lamp. | Heavy blue haze; constable is large and close at the end. `moonwash13` volume scatter was switched off AFTER the last preview (not seen rendered). |
| S14 | Board, WITCHCRAFT? card (THEORY badge) slams in f8 among blank ? cards; push-in. | |
| S15 | 85 mm, stamp hits f7, DISMISSED impression upper right of the card. | Impression is small; the overlay carries the word. |
| S16 | SPY RING? slams f8, camera slides right, generic cutting pops f34, red string draws f38-52; dismissed card at left. | |
| S17 | Stamp f6, NEVER PROVEN lower right; lamp swings (moving light). | Same weakness as S15. |
| S18 | Archive aisle, dolly to the one empty slot with its hanging tag, strip light flickers f22-27; then the paper. | 3D is covered by the document from ~2 s. |
| S19 | Obelisk at dusk, painted question on the pedestal (f1-56), then crane/tilt up the shaft; wind grass. | Obelisk is a plain generic form; end frame loses the text (by design). |

Weakest: S03 (elm contrast), S05 (climber small), S13 (haze), S15/S17 (small impressions), S11 (carriage barely in frame).
Unseen after the last preview: (1) S13 `moonwash13.volume_factor = 0`; (2) a bug fix found while building HAUNT-10: `materials.clear()` on a new mesh
reset every face's material index, so in ALL three preview rounds multi-material meshes rendered in their first material only. Fixed in the lib block
(calls removed, indices verified numerically, build-only). Not seen rendered: street fronts now have dark glass, paper tape, plank boards, stone trim
and iron pipe instead of all-brick (S02, S13, edges of S01/S20); the elm's cleft and hollow are now the intended unlit black (S03-S05, S07, S08);
archive boxes get dark lids, paper labels and ink bars (S18); evidence tags get ink bars (S10); S12 unaffected.
