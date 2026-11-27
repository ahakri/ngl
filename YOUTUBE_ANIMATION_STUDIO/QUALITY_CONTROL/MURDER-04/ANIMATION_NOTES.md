# MURDER-04 Animation notes (Zodiac "340" cipher)

Files: `BLENDER_PROJECTS/MURDER-04/shots.py`, `BLENDER_PROJECTS/MURDER-04/make_textures.py` (Pillow, system python3; writes
`BLENDER_PROJECTS/MURDER-04/tex/*.png`, already generated; shots.py regenerates missing files on demand). New builders appended to
`PIPELINE/blender/lib_murder.py`: `cipher_specs`, `cipher_grid` (20x17 individually keyframable glyph objects on aged paper, XZ plane),
`mat_glyph` + `set_glyph` (one shared material; per-glyph glow = keyframed object colour/alpha, so no per-glyph materials), `letter_obj`,
`hop_path` (down 1 / right 2 with wrap), `mat_screen` (scrolling / stepped-atlas emissive screen), `monitor`, `crt_tv` +
`mat_tv_screen` (picture + animated static + rolling band), `box_typewriter`, `hanging_lamp`, `coffee_cup`, `image_plane`.

All glyphs are illustrative stand-ins (Latin/Greek capitals, some mirrored or rotated, triangles, dots, slashes, boxes), generated from
a seed - not a reproduction of the 1969 sheet. Decoded letters on the grid use only the published first line
(I HOPE YOU ARE HAVING LOTS OF FUN IN TRYING TO CATCH ME) placed in reading order on the top rows; other cells are random letters.
Newspaper is a generic recreation ("THE EVENING PAPER", "RECREATION - 1969"); the solver program window is generic UI with the
plain text "AZdecrypt". No victims, places of death, weapons, handwriting, real envelopes, seals or likenesses.
Preview rounds used: 3 (rounds 2-3 with --only).

| Shot | Built | Deviations / notes |
|---|---|---|
| S01 | Macro 85 mm drift along row 5, eased pull-back to the full grid floating in black by 1.5 s; random glyphs pulse red; soft top light. | - |
| S02 | Grid rows blink white top to bottom while the camera tilts down the sheet. | - |
| S03 | 1969 newsroom: desks with box typewriters under hanging cone lamps, venetian blind with city glow, haze; clerk silhouette (shirt + tie) holds a plain envelope; the folded cipher sheet slides onto the lit desk; crane down. | Clerk mostly out of frame at the end (crane favours the sheet). |
| S04 | Dark drifting fog plate with faint distant lights (under the map). | - |
| S05 | Kitchen table: recreated newspaper + smaller stand-in cipher sheet, two cups, warm lamp; on "This one didn't" the paper whips away and the camera whips to the defocused 340 grid (red pulses). | - |
| S06 | Three stacked panels (red frames, black mask) each a solver silhouette at a glowing monitor (letter scroll / thumbnail mosaic / solver window); panels slide in left-right-left, slow push. | Stacked horizontal panels instead of vertical strips (vertical strips are too narrow in 9:16). Content is small. |
| S07-S09 | Over-the-shoulder monitor plates (letters / mosaic / solver window), light DOF, slow drift - under the map cards. | - |
| S10 | Sharp grid; white arrow sweeps row 1 lighting glyphs, turns red, shatters into red shards with a flash and micro-shake; push-in. | - |
| S11 | Grid splits into sections (rows 1-9, 10-18, 19-20), light dims, red path hops down 1 / right 2 (short glowing hop segments, no line across wraps), visited glyphs lift and slide into a re-ordered strip under the grid. | - |
| S12 | Modern monitor: thumbnail-grid mosaic flickers through atlas pages, push into the screen, solver shoulder silhouette. | Desk edge bright at frame bottom (under captions). |
| S13 | Over-the-shoulder on the solver window: gibberish candidate lines scroll, score bar climbs, warm lamp + screen glow, small orbit. | - |
| S14 | Split-flap decode line over a dim gibberish screen: cells flip through random letters; LOTS OF FUN resolves in red, the rest stays noise. | Weakest MURDER-04 shot: letters small at phone size. |
| S15 | Defocused grid plate with red pulses (under the telegram). | - |
| S16 | Grid flips column by column (right half) from symbols to amber letters, freezing at the halfway point; warm light grows. | Flip runs right-to-left so the left half stays symbols, as the storyboard asks. |
| S17 | Defocused half-flipped grid plate (under the decoded document). | - |
| S18 | Wood-veneer 1960s box TV alone in a dark room: grainy studio picture (two empty chairs, desk phone) with static and rolling band; push-in. | No people on the TV picture. |
| S19 | Tighter on the TV: big rotary phone icon + LIVE CALL-IN bar, static. | - |
| S20 | Decoded letter grid: glowing amber letters switch off one by one to grey, light cools, slow pull-back. | - |
| S21 | Dark desk plate: ZODIAC manila folder, typewriter, lamp (under the document). | - |
| S22 | Tilt down from the big grid: Z13 strip and Z32 block (stand-in glyphs) rise from the dark, red outlines draw on. | Z32 shown as 4x8. |
| S23 | Typewriter close-up plate with lamp; 13 stand-in glyphs appear one by one on a scrap on the desk (largely under the document). | - |
| S24 | Camera slides back into the S01 frame-1 macro framing (exact match) with red pulses - loop. | - |

Overlay param check against overlays.py: all valid, no changes needed.

Render cost: measured ~3 s/frame at 540 (S16, 688 glyph objects; S06) at load ~8.

Known weaknesses: S14 small letters; S06 panels small; screens are flat textures; solver figures are house mannequin silhouettes.
