# MURDER-05 — Storyboard

Hinterkaifeck farm, Upper Bavaria, 1922. Series: *Cold File*. Beat map: cold open 0–4 s (one-way footprints) · orientation 4–11 s · warnings 11–24 s (attic, newspaper, key, maid) · new maid / the night 24–35 s · **mid-point turn 34.9 s ("where it gets stranger")** · someone stayed 37–47 s (payoff 43.5 s) · investigation + 2007 review 47–60 s · unsolved + memorial 60–62 s · comment prompt 63–66 s · loop line → frame 1.

Timings are **estimates** (184 words at 2.95 words/s, the rate measured on MURDER-01's am_onyx @1.06 render, + scripted pauses) = **~68.7 s**; years are spoken as several words, so expect ~70 s. Re-time from the real Kokoro render. Shot boundary = start of the shot's first line. 9:16, 1080x1920, 24 fps. Captions burned in (red accent, `emphasis` words highlighted); keep overlays out of the bottom 20 % and right 15 %.

**Child-victim rule (hard):** two of the six victims were children. Nothing of the victims is shown or described beyond "all six people on the farm were killed" (L09). No bodies, no weapon, no barn interior where victims were found (S13 shows only the cattle stalls and trough), no reconstruction of the night. S09 is a locked-off exterior where a window goes dark — nothing more. Memorial card names all six without ages or circumstances.

**No suspects named.** The farmer and neighbour in S03 are anonymous silhouettes; S15/S17 use blank question-mark cards; the 2007 suspect is never named or hinted at.

**Set build (reuse across shots):** farmhouse = `studio_lib.house_exterior` (two-storey gabled) + attached barn wing (gabled box 14x7x5 m, plank material, large double door), snow ground = `lib_murder.heightfield` + `mat_snow`, roofs `mat_dusted`, forest = `lib_murder.conifer_forest`, footprints = `lib_murder.trail` + `print_decals` (boot-size prints), sky = `lib_murder.night_sky` + `moon`, snow = `lib_murder.snowfall`, fog = `lib_murder.fog`. Attic = `studio_lib.room` with two sloped roof planes + rafter boxes. Cattle = primitive boxes/cylinders. Overlay label `REPORTED` is not in `overlays.LABEL_COL` and renders in the default amber (intended).

## S01  ·  0.0–4.2 s  (4.2 s)  ·  transition in: cut

- **Narration:** L01 "Footprints in the snow led to the farm. None led away."
- **Visual:** Frame 1 already moving: ground-level view of a single line of boot prints (lib_murder.trail + print_decals, step 0.75 m, larger oval boot prints rx 0.09 ry 0.2, depth 0.06) running from a dark conifer tree line toward a barn wall with one lit window in the far background. Snow surface on either side is untouched. On 'None led away' the camera has reached the barn end: the prints stop at the wall; the snow beside them, back toward the trees, is clean.
- **Environment:** other:snow field at forest edge, night
- **Camera:** ground-level dolly forward along the prints, 28mm, starts mid-move, slight rise at end to reveal the barn wall; handheld amp 0.015
- **Characters:** none
- **Lighting:** cold blue moonlight (sun 0.35, colour 0.5/0.6/1.0), night_sky stars 0.6; one warm lit window (emission 3.0, 1.0/0.7/0.4)
- **FX:** snowfall light (lib_murder.snowfall, wind 0.4), fog_volume density 0.03 (colour 0.62/0.68/0.82)
- **On-screen text / overlays:** [label] REPORTED
- **SFX:** wind @+0.0s g0.5, footsteps @+0.0s g0.3, hit @+1.9s g0.55
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S02  ·  4.2–7.1 s  (3.0 s)  ·  transition in: whip

- **Narration:** L02 "Bavaria, March 1922. A lonely farm called Hinterkaifeck."
- **Visual:** Map card over a darkened, blurred plate of the farmstead: stylised outline of Bavaria, route line draws north from Munich, pin drops on Hinterkaifeck (between Ingolstadt and Schrobenhausen). Date stamp types on.
- **Environment:** map
- **Camera:** 2D overlay; background plate slow zoom 3%
- **Characters:** none
- **Lighting:** background plate dim blue
- **FX:** snowfall in background plate
- **On-screen text / overlays:** [map] HINTERKAIFECK / Upper Bavaria, Germany; [stamp] MARCH 1922 / UPPER BAVARIA
- **SFX:** boom @+0.0s g0.5, typewriter @+0.2s g0.4
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S03  ·  7.1–10.8 s  (3.6 s)  ·  transition in: cut

- **Narration:** L03 "The farmer, Andreas Gruber, reportedly told neighbours about the tracks."
- **Visual:** Farmstead set (build once, reuse): house = studio_lib house_exterior (two-storey gabled, 9x7 m, roof dusted with mat_dusted), barn = attached L-wing gabled box 14x7x5 m (dark wood plank material, mat_dusted roof, large double door), ground = heightfield with mat_snow, conifer_forest band 80 m behind, bare deciduous trees near yard. Wide establishing shot at night: the farmhouse and barn alone in a snowy clearing, forest behind, one lit window. A faceless char_figure silhouette in a long coat (the farmer, never shown in detail) stands at the yard gate facing a second silhouette at the fence line (a neighbour), both tiny in frame. No faces.
- **Environment:** house_exterior
- **Camera:** slow push-in, 50mm, from 60 m; figures lower third
- **Characters:** farmer silhouette (char_figure, coat, hat), neighbour silhouette (char_figure)
- **Lighting:** cold blue moonlight (sun 0.35, colour 0.5/0.6/1.0), night_sky stars 0.6; one warm lit window (emission 3.0, 1.0/0.7/0.4); lantern point light (warm, 40 W) at the gate
- **FX:** snowfall light (lib_murder.snowfall, wind 0.4), fog_volume density 0.03 (colour 0.62/0.68/0.82)
- **On-screen text / overlays:** [label] REPORTED; [card] Known from neighbours' later statements
- **SFX:** wind @+0.0s g0.5
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S04  ·  10.8–14.2 s  (3.4 s)  ·  transition in: cut

- **Narration:** L04 "He'd heard footsteps in the attic. He searched. Nobody."
- **Visual:** Attic: studio_lib room 8x5 m with the ceiling replaced by two sloped roof planes meeting at a ridge beam, exposed rafters (boxes 0.1x0.15 m every 0.8 m), hay bales (rounded boxes) and dust. A flashlight cone sweeps from the hatch in the floor across empty boards. On 'Nobody' the beam stops on an empty corner. Dust falls from a rafter as a creak plays.
- **Environment:** other:attic interior (room builder, gabled)
- **Camera:** POV from floor hatch, 24mm, handheld amp 0.03, slow pan left to right
- **Characters:** none
- **Lighting:** darkness + flashlight spot (warm, 900 W, 22 deg) from camera; faint moonlight slits between roof boards
- **FX:** dust particles in beam (particle_cloud), dust fall burst at 1.6 s
- **On-screen text / overlays:** [label] REPORTED
- **SFX:** creak @+0.4s g0.6, footsteps @+0.9s g0.35, sting @+2.4s g0.4
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S05  ·  14.2–17.4 s  (3.3 s)  ·  transition in: cut

- **Narration:** L05 "A Munich newspaper turned up that nobody had bought."
- **Visual:** Document reveal: a folded newspaper slides onto a dark wood kitchen table (lib_murder.desk + mat_wood_dark) under a single oil-lamp glow; overlay shows a generic masthead. No real newspaper name or real article text is reproduced.
- **Environment:** document
- **Camera:** top-down 50mm, slow rotate 4 deg
- **Characters:** none
- **Lighting:** warm oil-lamp point light (60 W) + deep shadow
- **FX:** dust motes
- **On-screen text / overlays:** [document] A Munich paper. / No one on the farm had bought it.; [label] REPORTED
- **SFX:** whoosh @+0.0s g0.4, click @+0.6s g0.3
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S06  ·  17.4–19.8 s  (2.3 s)  ·  transition in: cut

- **Narration:** L06 "Then a house key went missing."
- **Visual:** Close-up of an old wooden door with an iron lock plate; beside it a wall hook with two key outlines painted on the board but only ONE iron key hanging (key prop: torus bow + cylinder shaft + box bit). Camera racks focus to the empty outline.
- **Environment:** other:farmhouse door close-up
- **Camera:** static close-up 85mm with rack focus from key to empty outline
- **Characters:** none
- **Lighting:** moonlight through a window (cold), single warm practical off-frame
- **FX:** dust motes
- **On-screen text / overlays:** [text] 1 KEY MISSING
- **SFX:** click @+0.3s g0.5, rumble @+0.0s g0.25
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S07  ·  19.8–24.5 s  (4.7 s)  ·  transition in: fade_black

- **Narration:** L07 "Their previous maid had already quit. She'd heard noises in the attic too."
- **Visual:** A small faceless female silhouette (char_figure, shawl) with a bundle walks away from the farm down a snowy lane between bare trees; the lit farmhouse recedes behind her. Represents the previous maid leaving (earlier; date not specified on screen).
- **Environment:** road_night
- **Camera:** locked wide 35mm behind the figure, figure walks away from camera
- **Characters:** previous maid silhouette (char_figure, shawl, bundle) - anim_walk
- **Lighting:** cold blue moonlight (sun 0.35, colour 0.5/0.6/1.0), night_sky stars 0.6; one warm lit window (emission 3.0, 1.0/0.7/0.4)
- **FX:** snowfall light (lib_murder.snowfall, wind 0.4), fog_volume density 0.03 (colour 0.62/0.68/0.82)
- **On-screen text / overlays:** [label] EYEWITNESS CLAIM
- **SFX:** footsteps @+0.0s g0.3, wind @+0.0s g0.4
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S08  ·  24.5–28.2 s  (3.7 s)  ·  transition in: cut

- **Narration:** L08 "On March thirty-first, the new maid arrived. Her first day."
- **Visual:** Late afternoon, overcast: a different small silhouette with a suitcase (lib_murder.suitcase) walks TOWARD the farmhouse gate. Calendar overlay stamps 31 MARCH 1922.
- **Environment:** house_exterior
- **Camera:** slow lateral track 35mm, figure crosses frame left to right toward the gate
- **Characters:** new maid silhouette (char_figure, coat, suitcase) - anim_walk
- **Lighting:** dim grey dusk (dawn_sky preset, low strength 0.4), house windows warm
- **FX:** light snowfall
- **On-screen text / overlays:** [stamp] FRIDAY 31 MARCH 1922 / THE NEW MAID'S FIRST DAY; [label] DOCUMENTED FACT
- **SFX:** footsteps @+0.0s g0.3, typewriter @+0.3s g0.35
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S09  ·  28.2–32.1 s  (3.9 s)  ·  transition in: fade_black

- **Narration:** L09 "That night, all six people on the farm were killed."
- **Visual:** RESPECT BEAT. Same wide farm view as S03, now full night. The lit window goes dark (lamp off). Nothing else happens. No figures, no violence, no implied action. Hold.
- **Environment:** house_exterior
- **Camera:** locked-off wide 50mm, no movement
- **Characters:** none
- **Lighting:** cold blue moonlight (sun 0.35, colour 0.5/0.6/1.0), night_sky stars 0.6; one warm lit window (emission 3.0, 1.0/0.7/0.4); window emission animates 3.0 -> 0 at 1.2 s (flicker off, 2 flickers)
- **FX:** slow snowfall
- **On-screen text / overlays:** [label] DOCUMENTED FACT
- **SFX:** wind @+0.0s g0.35, heartbeat @+0.0s g0.25
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S10  ·  32.1–34.8 s  (2.7 s)  ·  transition in: cut

- **Narration:** L10 "No one found them for four days."
- **Visual:** Timeline overlay over a dim plate of the dark farmhouse: FRI 31 MAR -> SAT -> SUN -> MON -> TUE 4 APR (found). Days tick by.
- **Environment:** timeline
- **Camera:** 2D overlay; background slow lateral pan
- **Characters:** none
- **Lighting:** background dim blue
- **FX:** snowfall in plate
- **On-screen text / overlays:** [timeline] FOUR DAYS
- **SFX:** click @+0.3s g0.5, click @+1.0s g0.5, click @+1.7s g0.5
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S11  ·  34.8–37.1 s  (2.3 s)  ·  transition in: flash

- **Narration:** L11 "And that's where it gets stranger."
- **Visual:** MID-POINT TURN. Fast push from wide toward the dark farmhouse roof and its chimney. Hard flash at the start.
- **Environment:** house_exterior
- **Camera:** fast push-in 35mm -> 85mm crash zoom on the chimney, ends tight
- **Characters:** none
- **Lighting:** cold blue moonlight (sun 0.35, colour 0.5/0.6/1.0), night_sky stars 0.6; one warm lit window (emission 3.0, 1.0/0.7/0.4)
- **FX:** snowfall
- **On-screen text / overlays:** —
- **SFX:** riser @+0.0s g0.5, sting @+1.2s g0.55
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S12  ·  37.1–41.1 s  (4.0 s)  ·  transition in: cut

- **Narration:** L12 "Neighbours later said smoke rose from the chimney in those days."
- **Visual:** Grey daylight, a few days later: the house and barn in thin snow; a thin column of smoke rises from the chimney (volume_puff chain / smoke particle stream, grey). Two tiny silhouettes on the road in the foreground stop and look (visitors).
- **Environment:** house_exterior
- **Camera:** slow tilt up from road to chimney, 50mm
- **Characters:** two passer-by silhouettes (char_figure) in foreground
- **Lighting:** flat overcast day (sky grey-blue, sun 0.8 soft)
- **FX:** chimney smoke column (volume, rising), light fog
- **On-screen text / overlays:** [label] WITNESS CLAIM; [text] SMOKE.
- **SFX:** wind @+0.0s g0.4
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S13  ·  41.1–43.4 s  (2.3 s)  ·  transition in: cut

- **Narration:** L13 "Someone had been feeding the cattle."
- **Visual:** Barn interior: wooden stalls (boxes), low-poly cattle silhouettes (body = rounded box, head box, four cylinder legs; dark brown) calmly eating; a trough freshly filled with hay. No people, nothing else in the barn shown. Only the stall row and the trough are in frame.
- **Environment:** other:barn interior
- **Camera:** slow dolly along the trough, 35mm, trough edge in foreground
- **Characters:** 3 cattle silhouettes (primitive build)
- **Lighting:** grey daylight through plank gaps (volumetric shafts), dust
- **FX:** dust in light shafts, breath puffs from cattle
- **On-screen text / overlays:** [label] WITNESS CLAIM; [text] FED.
- **SFX:** creak @+0.2s g0.3, rumble @+0.0s g0.2
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S14  ·  43.4–47.3 s  (3.8 s)  ·  transition in: whip

- **Narration:** L14 "Investigators concluded the killer stayed on the farm for days."
- **Visual:** Evidence board (lib_murder.evidence_board) under a hanging lamp: three paper cards slam in one by one: SMOKE / CATTLE FED / BREAD EATEN, joined by red string to a central card: 'SOMEONE STAYED'.
- **Environment:** other:evidence board
- **Camera:** slow push-in 50mm; tiny shake on each slam (lib_murder.shake)
- **Characters:** none
- **Lighting:** single warm hanging lamp (220 W), dark surround
- **FX:** dust motes
- **On-screen text / overlays:** [card] Investigators concluded the perpetrator / remained at the farm for several days
- **SFX:** hit @+0.3s g0.5, hit @+1.0s g0.5, hit @+1.7s g0.5, boom @+2.4s g0.4
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S15  ·  47.3–51.6 s  (4.4 s)  ·  transition in: cut

- **Narration:** L15 "Police looked at more than a hundred suspects. Nobody was ever convicted."
- **Visual:** Same board, wider: dozens of blank grey suspect cards (no names, no faces; question-mark glyph only) fill the board; a counter climbs to 100+. A red rubber stamp hits: NO CONVICTION.
- **Environment:** other:evidence board
- **Camera:** pull back 50mm -> 35mm revealing the full board
- **Characters:** none
- **Lighting:** hanging lamp + cold fill
- **FX:** dust
- **On-screen text / overlays:** [counter] SUSPECTS LOOKED AT; [text] NO ONE CONVICTED
- **SFX:** typewriter @+0.0s g0.3, hit @+1.8s g0.6
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S16  ·  51.6–55.2 s  (3.6 s)  ·  transition in: cut

- **Narration:** L16 "In 2007, police students re-examined the files with modern methods."
- **Visual:** Desk scene (lib_murder.desk, desk_lamp): a thick case-file folder opens; a modern laptop-shaped box with glowing screen sits beside old yellowed papers (paper_card props). Stamp '2007'.
- **Environment:** other:archive desk
- **Camera:** slow overhead push 50mm
- **Characters:** none
- **Lighting:** desk lamp warm + cold screen glow
- **FX:** dust motes
- **On-screen text / overlays:** [stamp] 2007 - POLICE ACADEMY / FUERSTENFELDBRUCK; [label] DOCUMENTED FACT
- **SFX:** typewriter @+0.2s g0.35, click @+1.0s g0.4
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S17  ·  55.2–60.3 s  (5.1 s)  ·  transition in: cut

- **Narration:** L17 "They reportedly narrowed it to one main suspect, but never named that person publicly."
- **Visual:** Back to the board: all grey suspect cards slide away except ONE, which stays face-down. A sheet of black paper slides over it. No name ever appears.
- **Environment:** other:evidence board
- **Camera:** push-in to the single card, 85mm
- **Characters:** none
- **Lighting:** lamp narrows to a spot on the single card
- **FX:** dust
- **On-screen text / overlays:** [label] REPORTED; [card] Not publicly named / (out of respect for relatives, per reports)
- **SFX:** whoosh @+0.2s g0.4, sting @+1.6s g0.45
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S18  ·  60.3–62.7 s  (2.4 s)  ·  transition in: fade_black

- **Narration:** L18 "Officially, the case is still unsolved."
- **Visual:** Respect card: a simple stone memorial (lib_murder.headstone, kind 0, plus a thin iron cross on top) stands in snow at the edge of the field, a small lantern beside it. Memorial overlay with the six names.
- **Environment:** other:snow field, memorial
- **Camera:** slow push-in 50mm
- **Characters:** none
- **Lighting:** lantern warm point light + moonlight
- **FX:** light snowfall
- **On-screen text / overlays:** [card] Andreas & Cäzilia Gruber / Viktoria Gabriel, Cäzilia & Josef / Maria Baumgartner; [label] DOCUMENTED FACT
- **SFX:** wind @+0.0s g0.35
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S19  ·  62.7–66.2 s  (3.5 s)  ·  transition in: cut

- **Narration:** L19 "Why would anyone stay? Tell me what you think."
- **Visual:** Wide night shot of the farm from the forest edge, behind a tree trunk in foreground (the point of view of the tracks' origin). The barn is dark. Question text holds.
- **Environment:** house_exterior
- **Camera:** slow push from behind tree trunk, 35mm
- **Characters:** none
- **Lighting:** cold blue moonlight (sun 0.35, colour 0.5/0.6/1.0), night_sky stars 0.6; all windows dark (emission 3.0, 1.0/0.7/0.4)
- **FX:** snowfall light (lib_murder.snowfall, wind 0.4), fog_volume density 0.03 (colour 0.62/0.68/0.82)
- **On-screen text / overlays:** [text] WHY STAY?; [stamp] Sources in description
- **SFX:** wind @+0.0s g0.45, creak @+1.4s g0.25
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S20  ·  66.2–68.7 s  (2.5 s)  ·  transition in: cut

- **Narration:** L20 "And it all began in the snow."
- **Visual:** LOOP FRAME: framing, lighting and dolly identical to S01's first frame (ground level at the first prints by the tree line) so the cut back to frame 1 is seamless.
- **Environment:** other:snow field at forest edge, night
- **Camera:** matches S01 start, dolly forward
- **Characters:** none
- **Lighting:** as S01
- **FX:** snowfall light (lib_murder.snowfall, wind 0.4), fog_volume density 0.03 (colour 0.62/0.68/0.82)
- **On-screen text / overlays:** —
- **SFX:** wind @+0.0s g0.5
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve
