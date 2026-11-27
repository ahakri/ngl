# SCUBA-07 — Storyboard (Sponge Divers Found a 2,000-Year-Old Machine)

Vertical 9:16, 1080x1920, 24 fps. 14 shots, est. 52.6 s. Mood `scuba`. Captions: burned-in, word-synced, centred at y≈1240 (keep all text overlays out of y 1150–1400), accent words = `emphasis`. Overlays avoid the bottom 20% and right 15% (Shorts UI). Shot times are estimates; the pipeline derives real durations from TTS.

**Build notes.** Sets: (1) dark plinth macro (S01–S02) with an x-ray emissive gear train inside a translucent lump; (2) stormy/calm sea with a wooden sponge boat (caïque: `dive_boat()` re-dressed: rounded wooden hull, single mast, furled sail, pump flywheel) and a rocky island; (3) seabed at ~50 m: amphorae (lathe), bronze arm, faceless marble figures, silt, god rays, no hull; (4) 1902 museum storeroom; (5) modern CT cabinet; (6) clean bronze gear-train reconstruction with a front dial (sun marker, half-silver moon ball, eclipse disc) and a spiral back dial.
**Helmet diver (new prop):** brass sphere helmet (r≈0.2 m, metallic gold-brown) with a round dark-glass faceplate (no face visible), breastplate ring, grey canvas suit (`wetsuit()` with matte canvas material), lead boots (boxes), `umbilical()` hose to the surface, exhaust bubbles via `bubbles_at()`. 1900 divers had no torches: lighting is daylight only.
**Gears (new prop):** cylinder + array-modified triangular teeth, 20–120 teeth; meshing rotations keyed with gear ratios. Generic reconstruction look, not a copy of any one published model.
Metres throughout (Greek site; sources in metres).

## S01 · 0.0–2.8 s (2.8 s) · other:museum_plinth_dark

- **Visual:** COLD OPEN, moving at frame 1. A fist-to-shoebox-sized lump of green-brown corroded bronze, crusted with calcareous growth, slowly rotates on a black plinth under a single cool spotlight. Faint caustic ripples play across it (memory of the sea).
- **Camera:** 85 mm macro orbit, slow push-in
- **Characters:** —
- **Environment:** other:museum_plinth_dark
- **Build (lib_scuba):** Lump = noise-displaced icosphere, `mat_paint` green/brown verdigris + bump; plinth = box; `caustic_into()` on the lump; `god_rays()` subtle.
- **Lighting:** one cool spot from above + soft teal rim; caustic gobo
- **FX:** caustics_light, dust motes
- **On-screen text / overlays:** [text] 2,000 YEARS OLD (y=360)
- **SFX:** underwater_amb@0.0s(g0.35), sting@0.6s(g0.4)
- **Music:** Low pulse enters (0.45).
- **Transition in:** cut
- **Narration (L01):** "This lump came off a 2,000-year-old shipwreck."

## S02 · 2.8–4.7 s (1.9 s) · other:xray_reveal

- **Visual:** X-RAY SWEEP: a bright scan line passes over the lump left to right; behind it the lump turns translucent blue-white and reveals interlocking toothed gear wheels inside, frozen.
- **Camera:** same macro, locked; scan line moves
- **Characters:** —
- **Environment:** other:xray_reveal
- **Build (lib_scuba):** `scanlines()` + lump material alpha keyed behind a moving boolean/mask plane; gear train = procedural gears (cylinder + array-modified teeth, 6–8 gears), emissive x-ray material.
- **Lighting:** emissive scan line; x-ray look (inverted, blue-white)
- **FX:** scanlines, glow
- **On-screen text / overlays:** —
- **SFX:** sonar@0.0s(g0.35), hit@0.9s(g0.4)
- **Music:** Hit on 'gears'.
- **Transition in:** cut
- **Narration (L02):** "Inside, there were gears."

## S03 · 4.7–9.2 s (4.5 s) · other:storm_sea_greek_island

- **Visual:** Stormy grey sea, dusk. A small wooden sponge boat with a single mast and furled sail runs toward the lee of a rocky island. Rain streaks; spray. Map card follows: Peloponnese and Crete outlines, route line, pin on Antikythera between them.
- **Camera:** wide 28 mm, low over the waves, tracking with the boat; map slides in at mid-shot
- **Characters:** sponge boat crew (tiny faceless silhouettes)
- **Environment:** other:storm_sea_greek_island
- **Build (lib_scuba):** `ocean()` with storm amplitude + `dive_boat()` re-dressed as a wooden caïque (mast cylinder, furled sail); island = displaced cliff mesh; studio_lib rain + lightning flash.
- **Lighting:** storm overcast, cold; lightning flash once
- **FX:** rain, spray, lightning
- **On-screen text / overlays:** [map] ANTIKYTHERA; [stamp] GREECE, 1900 (y=300)
- **SFX:** thunder@0.4s(g0.4), wind@0.0s(g0.4)
- **Music:** Storm swell (0.6).
- **Transition in:** cut
- **Narration (L03):** "In 1900, Greek sponge divers sheltered from a storm off Antikythera."

## S04 · 9.2–13.6 s (4.5 s) · wreck

- **Visual:** Blue-grey water at depth. A helmet diver descends on a weighted line onto a seabed slope; as silt settles, a jumble of amphorae and a bronze arm and shoulder of a statue emerge, plus pale marble figures half buried. No ship hull (the wood is long gone).
- **Camera:** 35 mm descending tilt-down from diver to seabed reveal
- **Characters:** helmet diver (faceless: brass helmet with dark faceplate, grey canvas suit, lead boots, air hose)
- **Environment:** wreck
- **Build (lib_scuba):** `seabed`/`mat_caustic_ground`; amphorae = lathe profiles (`_loft`), statue arm = `hand()` + tube forearm with bronze `mat_paint`; marble figures = faceless `swimmer()`/figure poses lying down, white stone material; helmet diver = new prop (see build notes) + `umbilical()` hose.
- **Lighting:** dim blue daylight from above, god rays; no torch (1900)
- **FX:** silt, bubbles from helmet exhaust, god_rays
- **On-screen text / overlays:** [depth] ; [label] DOCUMENTED FACT (y=200)
- **SFX:** bubbles@0.0s(g0.5), underwater_amb@0.0s(g0.5)
- **Music:** Pulse (0.65).
- **Transition in:** cut
- **Narration (L04):** "Around 50 metres down, they found a wreck full of statues."

## S05 · 13.6–18.4 s (4.8 s) · other:sponge_boat_deck

- **Visual:** On deck in the swell: two faceless crewmen turn the big flywheel of a hand air pump; the air hose snakes over the gunwale into the water. Cut-in: the brass helmet's dark faceplate below, bubbles streaming from the exhaust valve.
- **Camera:** 35 mm handheld on deck (2.5 s), then 50 mm close on the helmet underwater
- **Characters:** deck crew x2 (faceless), helmet diver (faceless: brass helmet with dark faceplate, grey canvas suit, lead boots, air hose)
- **Environment:** other:sponge_boat_deck
- **Build (lib_scuba):** `dive_boat()` deck + pump = box with wheel (torus) spun via `keys`; `umbilical()` over the side; helmet close-up = sphere + cylinder faceplate (dark glass) + `bubbles_at()`.
- **Lighting:** overcast day on deck; blue gloom below
- **FX:** spray, bubbles
- **On-screen text / overlays:** —
- **SFX:** creak@0.0s(g0.35), breath@1.8s(g0.45)
- **Music:** Pulse.
- **Transition in:** cut
- **Narration (L05):** "They worked in brass helmets, breathing air pumped down from the boat."

## S06 · 18.4–20.6 s (2.1 s) · timeline

- **Visual:** Timeline draws on over a grey sea plate: 1900 (found) → 1901 (salvage continues). Small helmet-diver icons drop in a row along the 1901 segment, one after another.
- **Camera:** 2.5D slow horizontal pan
- **Characters:** —
- **Environment:** timeline
- **Build (lib_scuba):** Background = `ocean()` plate, grey grade; icons = tiny helmet silhouettes (flat planes) popping in.
- **Lighting:** graphic over desaturated sea plate
- **FX:** —
- **On-screen text / overlays:** [timeline] THE SALVAGE (y=900)
- **SFX:** whoosh@0.0s(g0.3), bubbles@0.8s(g0.3)
- **Music:** Pulse (0.6).
- **Transition in:** whip
- **Narration (L06):** "The salvage ran into 1901."

## S07 · 20.6–24.4 s (3.8 s) · other:sponge_boat_deck

- **Visual:** Consequence, no injury shown: on deck a faceless diver sits slumped against the mast, helmet off beside him, a crewman's hand on his shoulder. Cut to one empty brass helmet resting on the wet deck.
- **Camera:** 35 mm slow push, then 50 mm locked on the empty helmet
- **Characters:** diver (faceless, seated), crewman (faceless)
- **Environment:** other:sponge_boat_deck
- **Build (lib_scuba):** `dive_boat()` deck; seated figure (`kneel()`/`curl_pose()` adapted to sitting); helmet prop on deck.
- **Lighting:** grey afternoon, desaturated
- **FX:** spray
- **On-screen text / overlays:** [card] 1 diver dead (the bends) / 2 divers paralysed (y=820)
- **SFX:** heartbeat@0.4s(g0.35), wind@0.0s(g0.3)
- **Music:** Thins out (0.4).
- **Transition in:** cut
- **Narration (L07):** "One diver died of the bends. Two were paralysed."

## S08 · 24.4–28.1 s (3.7 s) · other:sponge_boat_deck

- **Visual:** Basket hauled up dripping over the gunwale: a bronze statue arm, a marble head (faceless, weathered), amphora shards... and the small corroded lump from S01, which the camera finds and pushes into.
- **Camera:** 50 mm tracking with the basket, then rack focus + push to the lump
- **Characters:** crew hands
- **Environment:** other:sponge_boat_deck
- **Build (lib_scuba):** Basket = lattice tube; props reused from S04; lump reused from S01; `drips()`.
- **Lighting:** flat daylight
- **FX:** drips
- **On-screen text / overlays:** [label] DOCUMENTED FACT (y=200)
- **SFX:** metal_groan@0.2s(g0.3), click@1.5s(g0.3)
- **Music:** Pulse returns (0.55).
- **Transition in:** cut
- **Narration (L08):** "Among the bronze and marble came this corroded lump."

## S09 · 28.1–32.8 s (4.7 s) · other:museum_storeroom_1902

- **Visual:** MID-POINT TURN. A dim museum storeroom: wooden shelves, numbered trays. The lump lies in a tray; a crack runs across it and it splits into pieces with a dry snap. A desk lamp swings toward it: a single toothed gear wheel catches the light.
- **Camera:** 50 mm slow push; tiny shake on the split
- **Characters:** hand of a faceless curator (gloveless 1902 sleeve)
- **Environment:** other:museum_storeroom_1902
- **Build (lib_scuba):** Shelves = boxes; lump split = two pre-fractured halves keyed apart; one gear wheel (procedural) embedded in the face; lamp = `hanging_lamp`-style practical (scuba lib `energy_keys`).
- **Lighting:** warm lamp, dark room; dust in the beam
- **FX:** dust
- **On-screen text / overlays:** [stamp] ATHENS, 1902 (y=300)
- **SFX:** hit@0.6s(g0.5), sting@1.3s(g0.4)
- **Music:** Silence beat, then low hit.
- **Transition in:** cut
- **Narration (L09):** "In 1902, it split apart, and a gear wheel showed through."

## S10 · 32.8–36.9 s (4.1 s) · other:ct_scan_lab

- **Visual:** Modern lab: the fragment sits on a turntable inside a large grey X-ray CT cabinet; the turntable rotates; on a monitor, slices flicker past showing gear teeth and tiny lettering.
- **Camera:** 28 mm slow arc around the cabinet; cut-in on the monitor
- **Characters:** —
- **Environment:** other:ct_scan_lab
- **Build (lib_scuba):** Cabinet = rounded box with an opening; turntable cylinder spun; monitor = plane with `scanlines()` and an emissive gear-section texture (procedural rings).
- **Lighting:** cool white lab light; monitor glow
- **FX:** scanlines
- **On-screen text / overlays:** [stamp] 2005: CT SCANS (y=300)
- **SFX:** click@0.0s(g0.3), sonar@0.8s(g0.3)
- **Music:** Pulse builds (0.7).
- **Transition in:** cut
- **Narration (L10):** "In 2005, X-ray CT scans revealed hidden gears and inscriptions."

## S11 · 36.9–40.2 s (3.3 s) · other:gear_train_reconstruction

- **Visual:** The fragment dissolves into a clean reconstructed gear train floating in blue darkness: bronze gears meshing and turning together, a crank on the side turning them.
- **Camera:** 35 mm orbit around the turning gear train
- **Characters:** —
- **Environment:** other:gear_train_reconstruction
- **Build (lib_scuba):** Procedural gears (6–8, varying tooth counts) parented with driven rotations (ratio keys); bronze `mat_paint` metallic.
- **Lighting:** warm key on bronze, blue rim; caustic shimmer
- **FX:** caustics_light
- **On-screen text / overlays:** [text] A CALCULATOR / FOR THE SKY (y=360)
- **SFX:** click@0.0s(g0.35), riser@0.3s(g0.35)
- **Music:** Swell (0.8).
- **Transition in:** flash
- **Narration (L11):** "It was a geared calculator for the sky."

## S12 · 40.2–43.9 s (3.7 s) · other:gear_train_reconstruction

- **Visual:** Front face of the reconstruction: a dial with a small sun marker and a half-silver moon ball circling; the moon's pointer passes the sun's, and a dark disc slides over the sun marker (eclipse). Then a spiral back dial glows.
- **Camera:** 50 mm straight-on, slow push
- **Characters:** —
- **Environment:** other:gear_train_reconstruction
- **Build (lib_scuba):** Dial = disc with ring text; sun = emissive sphere; moon = half-black/half-silver sphere spinning; eclipse = dark disc keyed across; spiral = `draw_on_curve()` emissive.
- **Lighting:** bronze lit warm; eclipse moment dims the scene
- **FX:** glow
- **On-screen text / overlays:** [card] SUN + MOON POSITIONS / ECLIPSE PREDICTION (y=820)
- **SFX:** click@0.0s(g0.3), boom@1.6s(g0.3)
- **Music:** Peak (0.9).
- **Transition in:** cut
- **Narration (L12):** "It tracked the Sun and Moon, and predicted eclipses."

## S13 · 43.9–48.1 s (4.2 s) · timeline

- **Visual:** A timeline races from the mechanism (~100 BC) across an empty gap to a medieval astronomical clock icon (1300s). The gap is marked '1,000+ YEARS'.
- **Camera:** 2.5D horizontal pan
- **Characters:** —
- **Environment:** timeline
- **Build (lib_scuba):** Overlay over a dark blue gradient background with drifting particles; clock icon = simple 3D clock face.
- **Lighting:** graphic
- **FX:** —
- **On-screen text / overlays:** [timeline] 1,000+ YEARS (y=900)
- **SFX:** whoosh@0.2s(g0.4)
- **Music:** Holds (0.7), then drops.
- **Transition in:** whip
- **Narration (L13):** "Nothing this complex appears again for over a thousand years."

## S14 · 48.1–52.6 s (4.5 s) · other:storm_sea_greek_island

- **Visual:** LOOP: calm sea after the storm, the sponge boat at anchor in a cove; a diver's helmet breaks the surface and a hand lifts a single brown sponge. The camera sinks below the surface toward the dark seabed, ending on a dark green-brown shape in the silt that matches the S01 lump framing.
- **Camera:** 28 mm surface-level, then dip below the waterline and push down
- **Characters:** helmet diver (faceless: brass helmet with dark faceplate, grey canvas suit, lead boots, air hose)
- **Environment:** other:storm_sea_greek_island
- **Build (lib_scuba):** `ocean()` calm + `wavy_plane()` waterline split; sponge = small noise blob; final frame = S01 lump composition on seabed.
- **Lighting:** clear golden afternoon; then blue underwater
- **FX:** caustics_light, bubbles
- **On-screen text / overlays:** —
- **SFX:** bubbles@0.5s(g0.4), underwater_amb@1.2s(g0.35)
- **Music:** Pulse returns to 0.45 (matches S01 for the loop).
- **Transition in:** cut
- **Narration (L14):** "And the men who found it were only looking for sponges."

## Timing checks

- Line 1 starts at 0.0 s; "2,000-year-old shipwreck" lands by ~2.4 s, and the S01 overlay "2,000 YEARS OLD" is on screen from frame 1. Frame 1 is moving (orbiting macro + caustics).
- New information every ~3–4 s: gears (≈3 s) → 1900 storm (≈6 s) → 50 m, statues (≈10 s) → helmets (≈15 s) → death/paralysis (≈19 s) → lump (≈25 s) → **turn (≈29 s): gear shows** → 2005 scans (≈33 s) → calculator (≈37 s) → eclipses (≈40 s) → 1,000 years (≈44 s) → loop line (≈48 s).
- Pattern interrupts: macro → storm/map → seabed → deck → timeline → storeroom → lab → reconstruction → timeline → sea.
- Silence beats: after L07 (0.4 s) and after L09 (0.5 s).
- Loop: L14 "…only looking for sponges." → L01 "This lump came off a 2,000-year-old shipwreck." S14's last frame matches S01's lump framing.
- Overlay safety: card at y=820 (2 lines, ends y≈1054); timelines at y=900 (labels to ≈1030); the S07 card at y=820 (3 rows incl. header, ends ≈1054); stamps/text in the upper third.
