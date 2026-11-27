# CAVE-08 — Storyboard (The Swimming Hole That Hid a Diver for 21 Years)

Vertical 9:16, 1080x1920, 24 fps. 18 shots, measured 58.7 s. Mood `cave`. Captions: burned-in, word-synced, centred at y≈1240 (keep all text overlays out of y 1150–1400), accent words = `emphasis`. Overlays avoid the bottom 20% and right 15% (Shorts UI). Shot times come from a scratch TTS measurement; the pipeline derives the real durations from its own render.

**Build notes.** Sets: (1) creek swimming hole = `heightfield()` pale limestone creek bed + `florida_woods()` cypress banks + round mouth (`shaft()` r≈2 m dropping into black) + `water_surface()` and `glow_disc()` for the blue, `sky_world()` + hard sun; swimmers = `figure()` in bright suits, waist-deep, faceless, generic (they stand for 'the swimming hole', not a dated scene; no one jumps from the ledge); (2) vertical shaft + bend = `shaft()` + `water()` + start of a `passage()`; (3) angled passage, squeeze and gravel slope = `passage()` (low half_h) + `rocks()` pebbles + `cloud()` / `noisy_volume()` silt; (4) 2.5D side-section = `xsection()` + `text()` chamber numbers + `glow_dot()` (generic; not traced from the JWEP survey); (5) small pale fourth chamber = inward-facing `shaft()` room + short low `passage()`; (6) creek in flood = S01 terrain + brown fast `water_surface()` + `rain()`. Divers: `diver()` faceless; the 1979 pair = single tanks, blue/white fins, handheld lights; recovery divers = doubles, black suits. Feet throughout (US site and sources). No remains or body shapes anywhere. The S17 sign is generic (no agency logo).

## S01 · 0.0–3.7 s (3.7 s) · other:texas_creek_swimming_hole

- **Visual:** COLD OPEN, moving at frame 1. Bright summer day over a shallow limestone creek bed shaded by tall cypress trees. In the middle of a pale rock shelf, a round hole about 4 m across glows deep blue, fading to black at its centre. Two faceless swimmers float at the hole's rim, feet dangling over the dark. The camera is already dropping and tilting toward the mouth.
- **Camera:** 24 mm drone, descending from ~12 m to ~4 m above the water while tilting from 45° to straight down
- **Characters:** swimmer_A (red swimsuit, faceless, generic), swimmer_B (yellow swimsuit, faceless, generic)
- **Environment:** other:texas_creek_swimming_hole
- **Build (lib_cave):** Creek bed = `heightfield()` with a pale limestone `rock_mat()` and a round opening; `shaft(z_top=0, z_bot=-12, radius≈2 m, rough=0.4)` drops into black below it; `water_surface()` (clear teal, low wave_scale) + `glow_disc()` under the surface for the blue; cypress banks = `florida_woods()`; `sky_world()` + `sun_from(sun_dir(55, 120))`; swimmers = `figure()` posed upright, cut at the waterline, bright suit materials, gentle `key_loc()` bob; `drip_rings()` around them.
- **Lighting:** hard high sun from upper left, dappled cypress shade; cyan glow inside the hole, black core
- **FX:** sun glints, ripple rings
- **On-screen text / overlays:** [text] 21 YEARS (y=420)
- **SFX:** wind@0.0s(g0.25), sting@1.9s(g0.4)
- **Music:** Low drone enters (0.45).
- **Transition in:** cut
- **Narration (L01):** "A diver stayed missing under this swimming hole for 21 years."

## S02 · 3.7–6.6 s (3.0 s) · other:vertical_spring_shaft

- **Visual:** Underwater, looking straight down the vertical shaft: bright aqua daylight from the mouth above fades to teal-black below. The two swimmers' legs hang as dark silhouettes against the bright circle at the top of frame. Grey limestone walls slide upward as the camera sinks; at the bottom the shaft bends away into a dark, angled opening.
- **Camera:** 20 mm, straight down, continuous sink; last second pitches toward the bend
- **Characters:** swimmer_A / swimmer_B (legs only, silhouettes at the surface)
- **Environment:** other:vertical_spring_shaft
- **Build (lib_cave):** `shaft(z_top=0, z_bot=-14, radius_fn≈2.0–2.6 m)` + `water(color=(0.35,0.75,0.72), density=0.03)`; `cloud()` fine specks; sun spot through the mouth for rays; legs = S01 `figure()`s seen from below; the bend = start of a `passage()` at z≈-9.
- **Lighting:** daylight shafts from above (god rays) fading to black; faint cyan fill
- **FX:** volumetric_water, fine silt, god rays
- **On-screen text / overlays:** [depth] 0→30 ft
- **SFX:** underwater_amb@0.0s(g0.5), bubbles@0.3s(g0.3)
- **Music:** Drone (0.5).
- **Transition in:** cut
- **Narration (L02):** "Thirty feet down, the well turns into a flooded cave."

## S03 · 6.6–9.1 s (2.4 s) · other:spring_vent

- **Visual:** At the bend below the shaft: sand grains and fine silt on the floor shiver and lift, carried by clear water flowing up and out of a dark opening deeper down. A steady stream of particles rises past the lens toward the light.
- **Camera:** 28 mm low, slow push toward the dark opening; particles stream toward camera
- **Characters:** —
- **Environment:** other:spring_vent
- **Build (lib_cave):** `passage()` mouth (half_w 1.4, half_h 1.0) angling down; floor `silt_mat()`; `cloud()` particle sheets with `drift()` / `key_loc()` upward motion; `cam_fill()`.
- **Lighting:** dim teal from above; black opening; particles catch a soft cyan fill
- **FX:** rising particles (upwelling), silt shimmer
- **On-screen text / overlays:** —
- **SFX:** rumble@0.2s(g0.2), bubbles@0.8s(g0.2)
- **Music:** Drone holds (0.5).
- **Transition in:** cut
- **Narration (L03):** "The water wells up from an aquifer below."

## S04 · 9.1–11.8 s (2.8 s) · map

- **Visual:** Map card over a slow, wide aerial of the creek and its cypress banks (S01 set from ~60 m, defocused): a simplified Texas outline, a route line drawing in from the north-east toward the Hill Country, a pin dropping on Wimberley.
- **Camera:** 2.5D map card; background aerial drifts slowly
- **Characters:** —
- **Environment:** map
- **Build (lib_cave):** S01 set rendered wide and soft behind the overlay (`aim_cam()` high, lens 35 mm).
- **Lighting:** background daylight, map card self-lit
- **FX:** —
- **On-screen text / overlays:** [map] JACOB'S WELL
- **SFX:** whoosh@0.0s(g0.35), click@1.5s(g0.3)
- **Music:** Light pulse joins (0.55).
- **Transition in:** whip
- **Narration (L04):** "This is Jacob's Well, in Wimberley, Texas."

## S05 · 11.8–14.5 s (2.7 s) · other:cave_cross_section

- **Visual:** Pattern interrupt: animated side-section of the cave. A short vertical entrance shaft (~30 ft) drops from the creek surface, then a passage angles down through four chambers that pop in one after another, numbered 1 to 4, the last one deepest. A cyan diver dot travels down the passage; a depth ruler in feet runs on the right.
- **Camera:** 2.5D orthographic, slow pan down following the dot
- **Characters:** cyan diver dot (abstract)
- **Environment:** other:cave_cross_section
- **Build (lib_cave):** `xsection(poly=[entrance shaft 0–30 ft, angled passage, chambers 1–4 down to ~120–137 ft], depth_to_z)`; chamber numbers = `text()` with `pop_in()`; `glow_dot()` + `move_along()`; `dotted_path()` trail. Generic diagram (not traced from a survey map).
- **Lighting:** graphic: emissive outlines on dark rock
- **FX:** —
- **On-screen text / overlays:** [depth] 0→100 ft 'AND DEEPER'
- **SFX:** sonar@0.2s(g0.35)
- **Music:** Pulse (0.55).
- **Transition in:** cut
- **Narration (L05):** "Its chambers drop more than a hundred feet."

## S06 · 14.5–18.1 s (3.7 s) · document

- **Visual:** A paper note slides up over a wet rock slab lit by a dive torch; the counts are typed, then each is struck through, ending on NO AGREED COUNT. A coil of guideline and a torch lie on the rock.
- **Camera:** top-down 50 mm, slight rotation
- **Characters:** —
- **Environment:** document
- **Build (lib_cave):** Slab = flattened `rocks()` boulder with wet `rock_mat()`; `line()` coil; `dive_torch()` prop; warm spot sweep keyed with `key_energy()`.
- **Lighting:** single warm torch beam sweeping the slab
- **FX:** drips
- **On-screen text / overlays:** [document] JACOB'S WELL: DIVERS WHO DIED HERE: / ~~9?~~ / ~~12?~~ / ~~MORE?~~ / NO AGREED COUNT (y=70); [label] DISPUTED (y=200)
- **SFX:** typewriter@0.3s(g0.3)
- **Music:** Pulse (0.6).
- **Transition in:** cut
- **Narration (L06):** "Divers have died in them. Nobody even agrees how many."

## S07 · 18.1–21.8 s (3.7 s) · cave_tunnel

- **Visual:** Inside the angled passage below the shaft: two faceless divers with single back-mounted tanks and handheld lights glide side by side down the slope; their two beams sweep the walls; fin kicks lift small puffs of silt.
- **Camera:** 35 mm, tracking behind and slightly above the pair
- **Characters:** diver_A (blue fins, single tank, handheld light, faceless, generic), diver_B (white fins, single tank, handheld light, faceless, generic)
- **Environment:** cave_tunnel
- **Build (lib_cave):** `passage(length=30, z_fn=slope down)`; two `diver(tanks='single', rebreather=False, beam_len=6)` with `move_along()`; handheld `dive_torch()`; `cloud()` puffs keyed with `key_scale()`.
- **Lighting:** their two torches only; very dim teal ambient
- **FX:** silt puffs, bubbles, volumetric_water
- **On-screen text / overlays:** [stamp] 1979 (y=300); [label] DOCUMENTED FACT (y=200)
- **SFX:** bubbles@0.2s(g0.4), breath@0.5s(g0.35)
- **Music:** Drone + pulse (0.6).
- **Transition in:** cut
- **Narration (L07):** "In 1979, two young divers went in together."

## S08 · 21.8–23.8 s (2.0 s) · cave_tunnel

- **Visual:** Looking down the same passage from above: the two lights shrink away around a bend and disappear. Their glow lingers on the silt for a moment, then the frame is black except for faint teal walls. Nothing comes back.
- **Camera:** 35 mm locked, very slow push
- **Characters:** diver_A / diver_B (lights only, receding)
- **Environment:** cave_tunnel
- **Build (lib_cave):** S07 set; divers `move_along()` out of frame; `key_energy()` fades their spots and `beam_cone()` strengths to 0.
- **Lighting:** two receding torches, then near-black
- **FX:** silt settling, volumetric_water
- **On-screen text / overlays:** —
- **SFX:** heartbeat@0.2s(g0.3), rumble@0.6s(g0.2)
- **Music:** Thins out (0.4).
- **Transition in:** cut
- **Narration (L08):** "Neither came back up."

## S09 · 23.8–26.4 s (2.6 s) · other:gravel_restriction

- **Visual:** POV squeeze: the camera pushes forward through a low, flat slot. The rock ceiling is inches above a floor of pebbles, and the torch beam shows the gap narrowing ahead.
- **Camera:** POV 18 mm, slow forward push, slight handheld
- **Characters:** —
- **Environment:** other:gravel_restriction
- **Build (lib_cave):** `passage(half_w=1.2, half_h=0.35, floor_flat=0.6)` underwater (or `crawl_set(ceiling=0.45)` flooded with `water()`); `rocks(count≈300, size=(0.02, 0.08))` as gravel; spot parented to the camera.
- **Lighting:** one torch from the camera position; everything else black
- **FX:** silt, volumetric_water
- **On-screen text / overlays:** —
- **SFX:** breath@0.0s(g0.45), creak@0.8s(g0.25)
- **Music:** Tension rises (0.65).
- **Transition in:** cut
- **Narration (L09):** "Deeper in, the passages squeeze down tight."

## S10 · 26.4–29.0 s (2.6 s) · other:gravel_restriction

- **Visual:** Macro on a steep gravel slope at the mouth of the slot: pebbles tick loose one by one, then a small slide pours down into the gap and throws up a brown silt plume that swallows the torch beam.
- **Camera:** 50 mm macro, locked, slight push
- **Characters:** —
- **Environment:** other:gravel_restriction
- **Build (lib_cave):** `rocks()` pebbles on a tilted plane; slide = groups of pebbles keyed with `key_loc()` down-slope (staggered starts); plume = `noisy_volume()` brown + `cloud()` with `key_scale()` growth.
- **Lighting:** single torch beam raking across the slope
- **FX:** gravel slide, silt plume
- **On-screen text / overlays:** —
- **SFX:** rumble@0.3s(g0.45), hit@1.2s(g0.3)
- **Music:** Tension (0.7).
- **Transition in:** cut
- **Narration (L10):** "And the floor is loose gravel that can slide."

## S11 · 29.0–32.6 s (3.6 s) · other:gravel_restriction

- **Visual:** Two faceless recovery divers with bright lights approach the slope at the slot. Gravel trickles and silt boils up into their beams; after a moment their lights pull back the way they came. No one is shown trapped.
- **Camera:** 35 mm side angle, slow lateral move
- **Characters:** recovery_diver_A (black suit, orange fins, faceless), recovery_diver_B (black suit, white fins, faceless)
- **Environment:** other:gravel_restriction
- **Build (lib_cave):** S10 slope; two `diver(tanks='doubles')` with `move_along()` in, hold, then back out; `cloud()` silt keyed denser.
- **Lighting:** their two strong beams; silt glowing in the light
- **FX:** silt, bubbles, gravel trickle
- **On-screen text / overlays:** —
- **SFX:** breath@0.0s(g0.4), bubbles@0.6s(g0.35), rumble@1.5s(g0.3)
- **Music:** Holds (0.7).
- **Transition in:** cut
- **Narration (L11):** "Recovery divers went in after them, but couldn't bring them out."

## S12 · 32.6–36.6 s (4.0 s) · other:cave_grate

- **Visual:** A dark side opening in the passage wall is blocked by a crude grate of welded rebar bars set in a rough grey concrete collar. A diver's torch beam passes across it; silt drifts through the bars.
- **Camera:** 35 mm, slow push toward the grate, slight handheld
- **Characters:** diver hand torch (beam only)
- **Environment:** other:cave_grate
- **Build (lib_cave):** New simple prop: grid of 0.02 m cylinders (rebar, rusty `rock_mat()` tint) welded in a 1.2 x 0.9 m frame, set in a noise-displaced box collar (concrete grey); `passage()` side opening; spot sweep with `key_loc()`.
- **Lighting:** one torch beam sweeping; dim teal ambient
- **FX:** silt, volumetric_water
- **On-screen text / overlays:** —
- **SFX:** click@0.4s(g0.3), underwater_amb@0.0s(g0.35)
- **Music:** Holds (0.65).
- **Transition in:** cut
- **Narration (L12):** "One of the recovery divers then built a grate to keep others out."

## S13 · 36.6–41.2 s (4.6 s) · other:creek_flood

- **Visual:** The creek in flood: fast brown water churns over the limestone shelf, hiding the well's mouth completely; rain lashes the surface and broken branches race past. Nothing else is shown.
- **Camera:** 28 mm low over the water, handheld, slow pan with the current
- **Characters:** —
- **Environment:** other:creek_flood
- **Build (lib_cave):** S01 creek `heightfield()`; `water_surface(color brown, flow=(0, 3.0), wave_scale 3.0, bump 0.5)` raised over the shelf; `rain()`; branch sticks (`curve()` + bevel) keyed downstream; `world_black()` swapped for a grey sky.
- **Lighting:** dark overcast, flat grey light, rain streaks
- **FX:** rain, turbulent water, debris
- **On-screen text / overlays:** [stamp] 1981 (y=300)
- **SFX:** rumble@0.0s(g0.4), thunder@0.6s(g0.35), wind@0.0s(g0.3)
- **Music:** Swell (0.75).
- **Transition in:** cut
- **Narration (L13):** "In 1981, a flood carried one of the young divers back out."

## S14 · 41.2–44.7 s (3.5 s) · other:cave_cross_section

- **Visual:** MID-POINT TURN. Back to the side-section: one cyan dot sits motionless in the deepest (fourth) chamber and slowly dims to a faint ember while a counter climbs to 21. Then near-silence.
- **Camera:** 2.5D orthographic, slow push in on the deepest chamber
- **Characters:** cyan dot (abstract)
- **Environment:** other:cave_cross_section
- **Build (lib_cave):** S05 `xsection()`; `glow_dot()` strength keyed down with `key_input()`; camera push.
- **Lighting:** graphic; the dot's glow fades
- **FX:** —
- **On-screen text / overlays:** [counter] YEARS MISSING 0→21 (y=380)
- **SFX:** sting@0.0s(g0.3), heartbeat@1.8s(g0.25)
- **Music:** Drops to near-silence after 'For 21 years' (0.08).
- **Transition in:** cut
- **Narration (L14):** "The other stayed lost."
- **Narration (L15):** "For 21 years."

## S15 · 44.7–48.4 s (3.7 s) · other:fourth_chamber

- **Visual:** Bright modern lights: two faceless recovery divers squeeze through a tight gap into a small chamber with pale, smooth, undisturbed limestone walls; their beams fan across it.
- **Camera:** 28 mm, slow push following the second diver through the gap
- **Characters:** recovery_diver_C (black suit, yellow fins, faceless), recovery_diver_D (black suit, white fins, faceless)
- **Environment:** other:fourth_chamber
- **Build (lib_cave):** Small chamber = `shaft()` used as an inward-facing room (radius≈3 m, height 3 m) with a pale `rock_mat()`; gap = short `passage(half_h=0.4)`; two `diver(tanks='doubles')` + `beam_cone()`.
- **Lighting:** two strong canister lights; pale walls bounce soft light
- **FX:** silt, bubbles, volumetric_water
- **On-screen text / overlays:** [stamp] 2000 (y=300)
- **SFX:** bubbles@0.2s(g0.35), sonar@1.0s(g0.25)
- **Music:** Returns gently (0.35).
- **Transition in:** fade_black
- **Narration (L16):** "In 2000, a recovery team pushed into the fourth chamber."

## S16 · 48.4–50.6 s (2.2 s) · other:fourth_chamber

- **Visual:** The two beams converge on a narrow dark gap in the chamber floor; silt drifts slowly through the light. One diver rests a gloved hand on the rock beside it. Nothing else is shown. A small memorial line fades in.
- **Camera:** 50 mm, slow push down toward the gap
- **Characters:** recovery_diver_C / recovery_diver_D (hands and lights only)
- **Environment:** other:fourth_chamber
- **Build (lib_cave):** S15 set; `crack_floor_z()`-style slot modelled as a narrow boolean-free gap (two offset floor slabs); diver hand from `diver()` rig posed with `pose_upright_kneel()`.
- **Lighting:** two beams pooled on the floor; everything else dark
- **FX:** silt, volumetric_water
- **On-screen text / overlays:** [label] DOCUMENTED FACT (y=200); [text] KENT MAUPIN  ·  MARK BRASHIER / 1979 (y=860)
- **SFX:** sting@0.3s(g0.25)
- **Music:** Soft (0.3).
- **Transition in:** cut
- **Narration (L17):** "And there, at last, they found him."

## S17 · 50.6–55.3 s (4.6 s) · other:texas_creek_swimming_hole

- **Visual:** Present day, daylight at the rock ledge beside the hole: a plain park sign on a post reads NO SCUBA DIVING; behind it the calm blue mouth. A card slides in.
- **Camera:** 35 mm, slow arc past the sign toward the water
- **Characters:** —
- **Environment:** other:texas_creek_swimming_hole
- **Build (lib_cave):** S01 set at eye level; `warning_sign(lines=('NO', 'SCUBA', 'DIVING'), face_emit=0.05)` re-dressed as a plain park sign (no agency logo) on the `ledge()`.
- **Lighting:** clean midday sun; blue glow from the hole
- **FX:** ripples, sun glints
- **On-screen text / overlays:** [card] TODAY: No scuba diving, except / the Jacob's Well Exploration Project (y=820)
- **SFX:** wind@0.0s(g0.25), click@0.5s(g0.25)
- **Music:** Lifts (0.5).
- **Transition in:** cut
- **Narration (L18):** "Today, scuba diving here is banned, except for one exploration team."

## S18 · 55.3–58.7 s (3.5 s) · other:texas_creek_swimming_hole

- **Visual:** LOOP FRAME: the camera rises back into the S01 drone position: sunlit creek, cypress shade, the round blue mouth with a swimmer floating at its rim. The final frame matches frame 1, so a replay flows into 'A diver stayed missing under this swimming hole…'.
- **Camera:** 24 mm drone, rising and tilting up; ends on S01's first-frame pose
- **Characters:** swimmer_A (red swimsuit, faceless, generic)
- **Environment:** other:texas_creek_swimming_hole
- **Build (lib_cave):** S01 set and camera path reversed; ends exactly on S01 frame 1.
- **Lighting:** hard high sun; cyan glow in the hole
- **FX:** sun glints, ripple rings
- **On-screen text / overlays:** —
- **SFX:** wind@0.0s(g0.25), bubbles@0.2s(g0.2)
- **Music:** Back to the opening level (0.45) for the loop.
- **Transition in:** cut
- **Narration (L19):** "And from up top, it still looks like a swimming hole."

## Timing checks

- Line 1 starts at 0.15 s; 'missing … swimming hole' lands by ~1.8 s and '21 years' by ~3.4 s, with '21 YEARS' on screen from frame 1. Frame 1 moves (descending, tilting drone).
- New information every ≤4.6 s: flooded cave at 30 ft (≈3.8 s) → aquifer (≈6.7 s) → place (≈9.1 s) → >100 ft (≈11.9 s) → disputed toll (≈14.6 s) → 1979 (≈18.2 s) → neither returned (≈21.9 s) → squeeze (≈23.9 s) → gravel (≈26.4 s) → **turn (≈29.1 s): recovery fails** → grate (≈32.6 s) → 1981 flood (≈36.7 s) → **21 years (≈41.3–44.1 s)** → 2000 (≈44.8 s) → found (≈48.5 s) → banned today (≈50.7 s) → loop (≈55.4 s).
- Pattern interrupts: surface → shaft → map → section diagram → document → 3D cave → squeeze/gravel macro → grate → surface flood → section diagram → chamber → surface.
- Silence beats: after L08 (0.75 s) and after L15 (0.75 s, music near 0). Two max.
- Payoff in the last 8 s: L18 (banned, one team) + L19 loop line.
- Loop: L19 '…it still looks like a swimming hole.' → L01 'A diver stayed missing under this swimming hole for 21 years.' S18 ends on S01's frame-1 drone pose.
- Overlay safety: map title single-line (JACOB'S WELL; the map card itself reaches y≈1330 and is lifted ~200 px by compose's avoid_captions(), as in earlier maps); document y=70 (paper + shadow end ≈1142); card y=820 (header + 2 rows, ends ≈1054); memorial text y=860 (2 lines, ends ≈950); counters, stamps and labels in the upper third; depth gauges on the right edge (y 300–1000). Nothing in y 1150–1400.
- Overlays only state what the narration states: no death-toll number is asserted (struck-through question marks), no cause of death, no names in the 2000 shot except the shared memorial line.
