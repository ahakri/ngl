# CAVE-07 — Storyboard (The Man Who Wrote Cave Diving's Rules Tried for 1,000 ft)

Vertical 9:16, 1080x1920, 24 fps. 17 shots, est. 60.6 s. Mood `cave`. Captions: burned-in, word-synced, centred at y≈1240 (keep all text overlays out of y 1150–1400), accent words = `emphasis`. Overlays avoid the bottom 20% and right 15% (Shorts UI). Shot times are estimates; the pipeline derives real durations from TTS.

**Build notes.** Sets: (1) the shaft = `shaft(z_top=0, z_bot=-300, radius_fn≈8–12 m bell-shaped)` + `water()` teal with a faint yellow-green particle tint (Zacatón is a warm, mineral-rich spring; tint is atmosphere only, not narrated); (2) ranchland rim = `crater(R≈55)` + `sky_world()` + `bushes()`, floating grass islands as green discs; (3) 2.5D section = `xsection()` + `glow_dot()` + `dotted_path()` (bottom drawn dashed with '?', because in 1994 it was unknown); (4) rock ledge staging area = `rocks()` + `water_surface()`. Divers: `diver()` faceless; Exley = yellow fins + sidemount `tank()`s, Bowden = orange fins + back-mounted tanks. Feet throughout (sources in feet). No body is ever modelled; the recovery is a line, a pulley, tanks and a diagram coil.

## S01 · 0.0–3.6 s (3.6 s) · other:vertical_cenote_shaft

- **Visual:** COLD OPEN, camera already sinking at frame 1. Looking straight down a vast vertical flooded shaft: teal-black water, rough limestone walls. Two torch cones (one warm-white, one slightly cooler) side by side, 3 m apart, each following its own white guideline, dropping away into black. Fine sulphur-tinted particles drift upward past camera.
- **Camera:** top-down 20 mm, slow sink following the two lights, slight handheld sway
- **Characters:** diver_A (Exley: yellow fins, sidemount tanks, helmet torch, faceless), diver_B (Bowden: orange fins, back-mounted tanks, helmet torch, faceless)
- **Environment:** other:vertical_cenote_shaft
- **Build (lib_cave):** `shaft(z_top=0, z_bot=-120, radius_fn≈9 m, rough=0.45)` + `water(color teal, density 0.05)`; two `diver()` with `move_along()` on two straight `line()` guidelines; `cloud()` yellow-green specks drifting up.
- **Lighting:** two torch beam_cones only + faint teal ambient from above
- **FX:** particles_dust (yellow-green tint), volumetric_water, bubbles
- **On-screen text / overlays:** [depth] TARGET 1,000 FT
- **SFX:** underwater_amb@0.0s(g0.5), bubbles@0.2s(g0.4), sting@1.2s(g0.45)
- **Music:** Low drone enters (0.45).
- **Transition in:** cut
- **Narration (L01):** "Two divers dropped into this hole, chasing 1,000 feet."

## S02 · 3.6–5.9 s (2.3 s) · other:vertical_cenote_shaft

- **Visual:** Side view, wider: the two lights descending on parallel lines. Hard match: the left light (Exley) dims slowly to nothing while the right light keeps going. No figure detail, just lights in black.
- **Camera:** locked 28 mm side-on, tiny push-in
- **Characters:** diver_A (Exley: yellow fins, sidemount tanks, helmet torch, faceless), diver_B (Bowden: orange fins, back-mounted tanks, helmet torch, faceless)
- **Environment:** other:vertical_cenote_shaft
- **Build (lib_cave):** Same shaft set; `key_energy()` on the left torch spot + beam fade.
- **Lighting:** two torches; left keyed down to 0 over the shot
- **FX:** volumetric_water, particles_dust
- **On-screen text / overlays:** —
- **SFX:** heartbeat@0.3s(g0.35)
- **Music:** Drone holds; thin out.
- **Transition in:** cut
- **Narration (L02):** "Only one came back up."

## S03 · 5.9–10.4 s (4.5 s) · other:mexican_ranchland_cenote

- **Visual:** Daylight. Drone view over flat scrubby ranchland: a near-perfect round hole with sheer rock walls and dark green-blue water some way below the rim; small floating grass islands on the surface. Map card follows: Mexico outline, pin in Tamaulipas.
- **Camera:** high 24 mm drone, slow descent toward the water; overlay map slides in mid-shot
- **Characters:** —
- **Environment:** other:mexican_ranchland_cenote
- **Build (lib_cave):** `crater(R=55, depth=20, pool_mat=dark teal)` + `sky_world()` + `sun_from(sun_dir(40, 110))` + `bushes(count=120)`; floating islands = a few flat noise-displaced green discs on the water.
- **Lighting:** hard mid-morning sun, warm; deep shadow inside the hole
- **FX:** heat haze (subtle)
- **On-screen text / overlays:** [map] ZACATÓN; [stamp] TAMAULIPAS, MEXICO / 6 APRIL 1994 (y=300)
- **SFX:** wind@0.0s(g0.35), whoosh@1.6s(g0.35)
- **Music:** Drone + light pulse (0.6).
- **Transition in:** cut
- **Narration (L03):** "Zacatón, Mexico. April 1994. Nobody knew how deep it went."

## S04 · 10.4–12.5 s (2.1 s) · other:cenote_rim_staging

- **Visual:** At the water's edge inside the cenote: a faceless diver silhouette with back-mounted tanks and orange fins kneels on a rock ledge checking a stage cylinder. Name stamp on screen.
- **Camera:** 35 mm slow arc left around the diver, waist height
- **Characters:** diver_B (Bowden: orange fins, back-mounted tanks, helmet torch, faceless)
- **Environment:** other:cenote_rim_staging
- **Build (lib_cave):** `diver(fins=orange, rebreather=False)` + `pose_upright_kneel()`; `tank()` stage on the ledge; `water_surface()`; rock ledge from `rocks()`.
- **Lighting:** warm bounce from the sunlit wall, diver in shadow (rim-lit)
- **FX:** water ripples
- **On-screen text / overlays:** [text] JIM BOWDEN (y=420)
- **SFX:** click@0.5s(g0.35)
- **Music:** Pulse.
- **Transition in:** cut
- **Narration (L04):** "One diver was Jim Bowden."

## S05 · 12.5–16.5 s (4.0 s) · other:cenote_rim_staging

- **Visual:** A second faceless diver, yellow fins, sidemount tanks, stands waist-deep at the ledge and pulls on a mask strap; we see him from behind, against the bright water. Name card pops.
- **Camera:** 28 mm push-in from behind, low angle
- **Characters:** diver_A (Exley: yellow fins, sidemount tanks, helmet torch, faceless)
- **Environment:** other:cenote_rim_staging
- **Build (lib_cave):** `diver(fins=YELLOW, rebreather=False)` with two `tank()` sidemounted; `rim_light()`; `water_surface()`.
- **Lighting:** backlit by sunlit water; rim light on tanks
- **FX:** water ripples, sun glints
- **On-screen text / overlays:** [text] SHECK EXLEY (y=420); [label] DOCUMENTED FACT (y=200)
- **SFX:** sting@0.1s(g0.4)
- **Music:** Pulse; slight lift (0.65).
- **Transition in:** cut
- **Narration (L05):** "The other was Sheck Exley, a legend of cave diving."

## S06 · 16.5–20.2 s (3.7 s) · other:dive_log_card

- **Visual:** Graphic beat: a counter races from 0 to 1,000 over a dark teal background of drifting silt; tick marks like log-book lines scroll behind it.
- **Camera:** 2.5D, slow push
- **Characters:** —
- **Environment:** other:dive_log_card
- **Build (lib_cave):** Background = dark teal `water()` slab + `cloud()`; `text()` log lines ("DIVE 0997 / 0998 / 0999") scroll up as 3D text planes.
- **Lighting:** flat graphic; faint caustic shimmer
- **FX:** particles_dust
- **On-screen text / overlays:** [counter] CAVE DIVES LOGGED (y=380); [text] FIRST EVER (y=800)
- **SFX:** click@0.0s(g0.3), riser@0.4s(g0.35)
- **Music:** Pulse builds (0.7).
- **Transition in:** whip
- **Narration (L06):** "The first person ever to log 1,000 cave dives."

## S07 · 20.2–25.5 s (5.3 s) · document

- **Visual:** A plain generic paperback-style card (no real cover art) slides up on a dark wet rock surface, title typed on. A torch beam sweeps across it.
- **Camera:** top-down 50 mm, slight rotation
- **Characters:** —
- **Environment:** document
- **Build (lib_cave):** Rock slab `floor()` with wet `rock_mat`; `dive_torch()` sweeping via key_loc; document is a 2D overlay (generic, not the real cover).
- **Lighting:** single torch beam sweep, warm
- **FX:** drips
- **On-screen text / overlays:** [document] Basic Cave Diving: / A Blueprint for Survival /  / First published 1979
- **SFX:** typewriter@0.4s(g0.3)
- **Music:** Pulse holds.
- **Transition in:** cut
- **Narration (L07):** "His cave-diving safety manual was titled Basic Cave Diving: A Blueprint for Survival."

## S08 · 25.5–29.9 s (4.5 s) · other:cenote_cross_section

- **Visual:** Pattern interrupt: animated side-section of the cenote (narrow at the top, bell-shaped below, bottom drawn as a dashed '?'). Two cyan dots descend on two separate vertical guide lines; a depth bar runs on the right.
- **Camera:** 2.5D orthographic, slow vertical pan down following the dots
- **Characters:** two diver dots (cyan = Exley, orange = Bowden)
- **Environment:** other:cenote_cross_section
- **Build (lib_cave):** `xsection(poly=cenote profile, depth_to_z)` + `dotted_path()` for the unknown bottom; two `glow_dot()` with `move_along()` on two `line()`s.
- **Lighting:** graphic (emissive outlines)
- **FX:** —
- **On-screen text / overlays:** [depth] 
- **SFX:** sonar@0.2s(g0.35), bubbles@1.0s(g0.25)
- **Music:** Pulse (0.75).
- **Transition in:** cut
- **Narration (L08):** "They went down on separate lines, each alone in the dark."

## S09 · 29.9–34.0 s (4.1 s) · cave_tunnel

- **Visual:** Deep in the shaft: Bowden's faceless silhouette hangs beside his line, wrist gauge glowing; bubbles stream up fast. A gas timer drains on screen.
- **Camera:** 35 mm close side angle, slow push, handheld tension
- **Characters:** diver_B (Bowden: orange fins, back-mounted tanks, helmet torch, faceless)
- **Environment:** cave_tunnel
- **Build (lib_cave):** `shaft()` close wall section + `diver(fins=orange)`; `bubble_trail()`; small emissive disc on the wrist.
- **Lighting:** his torch + gauge glow only; black around
- **FX:** bubbles (heavy), particles_dust
- **On-screen text / overlays:** [depth] BOWDEN; [timer] GAS RESERVE (y=330)
- **SFX:** breath@0.0s(g0.5), bubbles@0.3s(g0.5), heartbeat@1.2s(g0.35)
- **Music:** Pulse tightens (0.8).
- **Transition in:** cut
- **Narration (L09):** "Around 925 feet, Bowden was burning gas faster than planned."

## S10 · 34.0–38.0 s (3.9 s) · other:cenote_cross_section

- **Visual:** Back to the section: Bowden's orange dot stops at 925 and starts back up; a small record flag pops at that depth. Exley's cyan dot keeps sinking past it on the other line.
- **Camera:** 2.5D orthographic, slight zoom out
- **Characters:** two diver dots
- **Environment:** other:cenote_cross_section
- **Build (lib_cave):** Same `xsection()`; orange `glow_dot` reverses (`move_along` keys); flag = small `text()` + triangle `flat_poly()`.
- **Lighting:** graphic
- **FX:** —
- **On-screen text / overlays:** [text] WORLD RECORD (y=520); [text] (since broken) (y=620)
- **SFX:** hit@0.4s(g0.4)
- **Music:** Pulse peaks (0.9), then drops.
- **Transition in:** cut
- **Narration (L10):** "He turned back, and set a world depth record."

## S11 · 38.0–41.0 s (3.0 s) · other:vertical_cenote_shaft

- **Visual:** MID-POINT TURN. Looking up from deep in the shaft toward a faint teal glow of daylight far above. Bowden's single light rises slowly away. No second light ever enters the frame. Hold in near-silence.
- **Camera:** upward 18 mm, locked, extremely slow push
- **Characters:** diver_B (Bowden: orange fins, back-mounted tanks, helmet torch, faceless) (tiny, ascending)
- **Environment:** other:vertical_cenote_shaft
- **Build (lib_cave):** `shaft()` tall; camera at z=-250 pointing +Z; emissive disc at top; one `glow_dot` + spot moving up.
- **Lighting:** faint daylight disc far above; one torch rising
- **FX:** particles_dust, volumetric_water
- **On-screen text / overlays:** [label] DOCUMENTED FACT (y=200)
- **SFX:** rumble@0.0s(g0.25)
- **Music:** Music drops to near-silence (0.1).
- **Transition in:** cut
- **Narration (L11):** "Exley's light never came back up."

## S12 · 41.0–44.6 s (3.7 s) · other:cenote_rim_staging

- **Visual:** Daylight, three days later (stamp). Faceless support-team silhouettes on the rock ledge haul a white guideline hand over hand out of the water; a pulley on a tripod; tanks clipped to the line come up first.
- **Camera:** 35 mm low angle along the line toward the haulers, slow dolly
- **Characters:** support team x3 (faceless silhouettes)
- **Environment:** other:cenote_rim_staging
- **Build (lib_cave):** `figure()` x3 with simple haul poses (keyed arms); `pulley()` on a tripod; `line()` with `grow_curve()` reversed; `tank()` x2 on the line.
- **Lighting:** flat overcast-ish daylight; muted
- **FX:** drips off the line, water ripples
- **On-screen text / overlays:** [stamp] 9 APRIL 1994 / 3 DAYS LATER (y=300)
- **SFX:** creak@0.3s(g0.3), footsteps@1.0s(g0.2)
- **Music:** Sparse low pad (0.3).
- **Transition in:** fade_black
- **Narration (L12):** "Three days later, his team hauled up his line."

## S13 · 44.6–48.6 s (3.9 s) · other:cenote_cross_section

- **Visual:** Respectful abstraction, NO body: on the section diagram the guideline is drawn coiling tightly around the cyan dot as both rise together to the surface. Cut-in insert: a coil of white line resting on wet rock.
- **Camera:** 2.5D slow pull-up; then 50 mm macro on the coil
- **Characters:** cyan dot (abstract)
- **Environment:** other:cenote_cross_section
- **Build (lib_cave):** `xsection()` + `helix()` around the `glow_dot` path; insert = `line()` coil (helix flattened) on `rocks()`.
- **Lighting:** graphic; insert = soft daylight
- **FX:** —
- **On-screen text / overlays:** [label] DOCUMENTED FACT (y=200)
- **SFX:** sting@0.2s(g0.3)
- **Music:** Pad (0.3).
- **Transition in:** cut
- **Narration (L13):** "Exley came up with it, wrapped in the line."

## S14 · 48.6–51.9 s (3.4 s) · document

- **Visual:** A plain incident card slides in; the CAUSE field is struck through and replaced by 'UNDETERMINED'. Wet rock behind.
- **Camera:** top-down 50 mm, slight push
- **Characters:** —
- **Environment:** document
- **Build (lib_cave):** Document overlay over the S07 rock slab (re-lit cooler).
- **Lighting:** cool torch light
- **FX:** —
- **On-screen text / overlays:** [document] ZACATON, 6 APR 1994 / DIVER: S. EXLEY, 45 / CAUSE: ~~NARCOSIS? HPNS?~~ / UNDETERMINED
- **SFX:** typewriter@0.3s(g0.3)
- **Music:** Pad.
- **Transition in:** cut
- **Narration (L14):** "The cause of his death was never determined."

## S15 · 51.9–53.5 s (1.5 s) · other:mexican_ranchland_cenote

- **Visual:** Dusk at the rim: the round hole, still water far below, long shadows; a single small wildflower moves in the wind at the edge (no memorial invented).
- **Camera:** 24 mm slow crane down to the rim edge
- **Characters:** —
- **Environment:** other:mexican_ranchland_cenote
- **Build (lib_cave):** S03 set re-lit (`sun_from(sun_dir(6, 280))`), `bushes()`; flower = small emissive-free plane cluster.
- **Lighting:** warm low dusk sun, blue shadow
- **FX:** wind in grass
- **On-screen text / overlays:** [text] SHECK EXLEY / APRIL 1994 (y=420)
- **SFX:** wind@0.0s(g0.35)
- **Music:** Pad swells gently (0.45).
- **Transition in:** cut
- **Narration (L15):** "He was 45."

## S16 · 53.5–57.5 s (4.0 s) · other:cenote_rim_staging

- **Visual:** Present day, daylight: the S04 ledge with a different, generic modern diver (white fins, faceless) clipping a reel to a new line and sliding into the water. The award card slides in.
- **Camera:** 35 mm slow push over the diver's shoulder toward the water
- **Characters:** generic modern diver (white fins, faceless, not Exley)
- **Environment:** other:cenote_rim_staging
- **Build (lib_cave):** S04 set; `diver(fins=white)`; reel = small cylinder + `line()`.
- **Lighting:** clean daylight, sunlit wall bounce
- **FX:** water ripples, sun glints
- **On-screen text / overlays:** [card] NSS Cave Diving Section (y=820)
- **SFX:** click@0.4s(g0.3), bubbles@1.4s(g0.3)
- **Music:** Pad lifts (0.5).
- **Transition in:** cut
- **Narration (L16):** "Today, cave divers can earn an award in his name."

## S17 · 57.5–60.6 s (3.1 s) · other:vertical_cenote_shaft

- **Visual:** LOOP FRAME: back to the S01 composition, top-down into the shaft; a single torch cone (the generic diver) sinks slowly into the dark on one line while a counter ticks to 1,000. The final frame matches frame 1 so a replay cuts cleanly into 'Two divers dropped into this hole'.
- **Camera:** top-down 20 mm, same sink as S01
- **Characters:** generic modern diver (white fins, faceless)
- **Environment:** other:vertical_cenote_shaft
- **Build (lib_cave):** S01 set reused with one diver; camera ends on S01 frame-1 transform.
- **Lighting:** one torch cone; teal ambient
- **FX:** particles_dust, volumetric_water
- **On-screen text / overlays:** [counter] SAFE CAVE DIVES (y=380)
- **SFX:** underwater_amb@0.0s(g0.45), bubbles@0.5s(g0.3)
- **Music:** Drone settles to 0.45 (matches S01 start level for the loop).
- **Transition in:** cut
- **Narration (L17):** "It's for logging 1,000 safe cave dives."

## Timing checks

- Line 1 starts at 0.0 s; "1,000 feet" lands by ~2.5 s, "two divers … hole" by ~1.2 s. Frame 1 is moving (sinking camera, rising particles).
- New information every ~3–5 s: place/date (≈7 s) → Bowden (≈11 s) → Exley twist (≈14 s) → 1,000 dives (≈18 s) → rule book (≈22 s) → separate lines (≈27 s) → 925 ft/gas (≈31 s) → record (≈35 s) → **turn (≈38 s)** → 3 days later (≈41 s) → wrapped (≈45 s) → undetermined (≈48 s) → age → award payoff (≈53–60 s).
- Pattern interrupts: 3D shaft → map → staging → counter graphic → document → section diagram → 3D → section → document → 3D. Max ~4.5 s per shot, each with a camera move.
- Silence beats: after L11 (0.7 s) and after L13 (0.5 s) — two max.
- Loop: S17 ends on the S01 composition (single light sinking); not a verbal loop (the story's ending is a death, so a grammatical loop would trivialise it).
- Overlay safety: all text overlays y ≤ ~1060 (cards at y=820, 172 px tall; counters at y=380); captions sit at y≈1240.
