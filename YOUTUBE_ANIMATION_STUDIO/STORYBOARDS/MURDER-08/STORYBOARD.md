# MURDER-08 — Storyboard (Who Put Bella in the Wych Elm? Nobody Ever Answered)

Vertical 9:16, 1080x1920, 24 fps. 20 shots, measured 66.8 s. Mood `murder`. Captions: burned-in, word-synced, centred at y≈1240 (keep all text overlays out of y 1150–1400), accent words = `emphasis`. Overlays avoid the bottom 20% and right 15% (Shorts UI). Shot times come from a scratch TTS measurement; the pipeline derives the real durations from its own render.

**Build notes.** Sets: (1) blackout brick wall + street = plane/facade with lib_haunted `mat_brick()` (sooty), `wall_with_openings()` (boarded windows), `streetlamp()` with a hood and flicker, `mat_wet_road()` cobbles, lib_murder `fog()`, `night_sky()`; chalk letters = `text3d()` with a rough chalk material (or lib_murder `letter_obj()` glyphs) revealed stroke by stroke in S11; (2) Hagley Wood = lib_haunted `bare_forest()` + sparse `leafy_trees()`, mist, dead-leaf ground; the hero wych elm = new simple prop (short ≈4 m, very thick ≈1.4 m trunk, noise-displaced cylinder with an open, jagged hollow top; inside = inward-facing cylinder for the S06 POV); (3) 1943 figures = lib_haunted `figure()` (boys with `cap=True`, height 1.4; constables with `custodian_helmet()`; detective with `coat=True`), all faceless; (4) evidence table and police office = lib_murder `desk()`, `desk_lamp()`, `case_folder()`, `box_typewriter()`; (5) evidence board = lib_murder `evidence_board()`, `paper_card()`, `slam_in()`, `red_string()`, `newspaper(masthead='')` + lib_scuba `rubber_stamp()`; (6) archive aisle = simple shelving + instanced boxes; (7) Wychbury Hill = `heightfield()` hill + new obelisk prop (tapered square shaft on a stepped plinth) with painted text. No remains are modelled anywhere.

## S01 · 0.0–2.0 s (2.0 s) · other:brick_wall_graffiti_1944

- **Visual:** COLD OPEN, moving at frame 1. Night, wartime blackout street. A soot-dark brick wall under one dim, hooded street lamp. Rough white chalk capitals fill the frame: WHO PUT BELLA DOWN THE WYCH ELM - HAGLEY WOOD. The lamp buzzes and dips; chalk dust glints.
- **Camera:** 50 mm, slow push-in across the letters, slight drift left
- **Characters:** —
- **Environment:** other:brick_wall_graffiti_1944
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** Wall = plane with lib_haunted `mat_brick()` (dark, sooty variant); chalk text = `text3d()` in a rough off-white emissive-lite material with a noise mask for chalk texture (or lib_murder `letter_obj()` glyphs); lamp = lib_haunted `streetlamp()` with a hood, energy flicker via `key_energy()`; lib_murder `fog()` thin.
- **Lighting:** one warm, weak street lamp from upper right; cold blue night fill
- **FX:** chalk dust motes, light fog
- **On-screen text / overlays:** —
- **SFX:** wind@0.0s(g0.25), sting@0.4s(g0.4)
- **Music:** Low murder drone enters (0.5).
- **Transition in:** cut
- **Narration (L01):** "Who put Bella down the Wych Elm?"

## S02 · 2.0–6.0 s (4.0 s) · other:brick_wall_graffiti_1944

- **Visual:** Wider: the whole wall belongs to an empty, boarded-up building on a narrow city street; taped windows, a sandbag stack. The chalk question sits at head height; the street is deserted.
- **Camera:** 28 mm, slow pull-back from the wall
- **Characters:** —
- **Environment:** other:brick_wall_graffiti_1944
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** S01 wall extended into a two-storey brick facade (lib_haunted `wall_with_openings()` with boarded windows); sandbags = rounded boxes; `streetlamp()`; lib_murder `night_sky()`.
- **Lighting:** street lamp pool; blue moonlight; dark windows
- **FX:** light fog
- **On-screen text / overlays:** [stamp] BIRMINGHAM, 1944 (y=300); [label] DOCUMENTED FACT (y=200)
- **SFX:** footsteps@0.6s(g0.2), wind@0.0s(g0.25)
- **Music:** Holds (0.5).
- **Transition in:** cut
- **Narration (L02):** "In 1944, someone wrote that on a wall in Birmingham."

## S03 · 6.0–9.5 s (3.4 s) · other:hagley_wood_dusk

- **Visual:** Woodland at dusk in early spring: mist between grey trunks, a carpet of dead leaves. The camera glides toward one squat, very thick old tree with a dark hollow where its crown should be.
- **Camera:** 35 mm, slow glide through the trees toward the old elm
- **Characters:** —
- **Environment:** other:hagley_wood_dusk
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** lib_haunted `bare_forest()` + `leafy_trees()` (sparse early leaf); the hero elm = new simple prop: short (≈4 m), very thick (≈1.4 m) trunk from a noise-displaced cylinder with a hollow top (inner cylinder, open rim, jagged edge), a few stubby branches; lib_murder `fog()`; dead-leaf ground plane.
- **Lighting:** fading blue dusk, low mist, no direct sun
- **FX:** mist, drifting leaves
- **On-screen text / overlays:** [text] UNIDENTIFIED (y=420)
- **SFX:** wind@0.0s(g0.3), creak@1.2s(g0.25)
- **Music:** Drone + low pulse (0.55).
- **Transition in:** cut
- **Narration (L03):** "It was about a real woman. Nobody knows who she was."

## S04 · 9.5–14.4 s (4.9 s) · map

- **Visual:** Map card over the woodland: the West Midlands as a simple shape, a line drawing from Birmingham south-west toward a wood, a pin dropping on Hagley Wood; then the date stamp.
- **Camera:** 2.5D map card; background woodland drifts
- **Characters:** —
- **Environment:** map
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** S03 woodland rendered soft behind the overlay.
- **Lighting:** map card self-lit
- **FX:** —
- **On-screen text / overlays:** [map] HAGLEY WOOD (0s–2.3s); [stamp] 18 APRIL 1943 (y=300, 2.3s→end)
- **SFX:** whoosh@0.0s(g0.35), typewriter@2.3s(g0.3)
- **Music:** Pulse (0.55).
- **Transition in:** whip
- **Narration (L04):** "April 1943. Four boys were out in Hagley Wood, in Worcestershire."

## S05 · 14.4–18.0 s (3.7 s) · other:hagley_wood_day

- **Visual:** Spring afternoon, dappled light. Four faceless boy silhouettes in 1940s caps and short trousers stand at the base of the squat elm; one has climbed onto it and leans over the dark opening at its top, peering down.
- **Camera:** 35 mm low angle from among the roots, slow push up toward the climbing boy
- **Characters:** boy_A (climbing, cap, faceless), boys_B–D (watching, faceless silhouettes)
- **Environment:** other:hagley_wood_day
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** Hero elm from S03 in daylight; boys = lib_haunted `figure(cap=True, height=1.4)` (faceless, dark); climber posed on the trunk with `pose_hold()`; sun + lib_haunted `leafy_trees()` canopy shadows.
- **Lighting:** soft afternoon sun through young leaves
- **FX:** dust in sunbeams, falling leaf
- **On-screen text / overlays:** [label] DOCUMENTED FACT (y=200)
- **SFX:** wind@0.0s(g0.2), creak@0.8s(g0.3)
- **Music:** Pulse continues (0.55).
- **Transition in:** cut
- **Narration (L05):** "One climbed an old wych elm and looked down into its hollow trunk."

## S06 · 18.0–20.0 s (2.0 s) · other:inside_hollow_trunk

- **Visual:** POV from deep inside the hollow, looking up: a ring of rough inner bark frames a disc of bright sky, and the boy's faceless silhouette leans into it, then jerks back out of view. Nothing inside the trunk is shown.
- **Camera:** 18 mm, locked looking straight up; tiny push
- **Characters:** boy_A (silhouette against the sky)
- **Environment:** other:inside_hollow_trunk
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** Interior = inward-facing noise-displaced cylinder (bark material) with an open top; camera at the bottom; sky = bright world; boy from S05 keyed out of the opening.
- **Lighting:** bright sky disc above; the trunk interior near-black
- **FX:** dust falling, a leaf drifting down
- **On-screen text / overlays:** —
- **SFX:** sting@0.2s(g0.45), heartbeat@0.8s(g0.3)
- **Music:** Hit, then near-silence (0.2).
- **Transition in:** cut
- **Narration (L06):** "In the dark, he saw a skull."

## S07 · 20.0–23.0 s (3.0 s) · other:hagley_wood_day

- **Visual:** Late afternoon: two 1940s police constables (faceless silhouettes, tall helmets) and a man in a long coat stand at the elm; a wooden ladder leans on the trunk; a canvas screen is being put up beside it. Nothing from inside the tree is shown.
- **Camera:** 50 mm, slow lateral move behind trunks
- **Characters:** constable_A / constable_B (faceless, helmets), detective (long coat, hat, faceless)
- **Environment:** other:hagley_wood_day
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** lib_haunted `figure()` x3 + `custodian_helmet()` on two; coat via `figure(coat=True)`; ladder = two cylinders + rungs; canvas screen = cloth-free plane on poles.
- **Lighting:** low gold sun, long shadows
- **FX:** mist
- **On-screen text / overlays:** —
- **SFX:** footsteps@0.2s(g0.3), creak@1.4s(g0.25)
- **Music:** Pulse (0.6).
- **Transition in:** cut
- **Narration (L07):** "Inside the tree, police found the skeleton of a woman."

## S08 · 23.0–26.6 s (3.6 s) · other:hagley_wood_day

- **Visual:** Time-lapse on the old elm: light sweeps from day to night and back, leaves fall, snow dusts the ground, leaves return; the trunk stays still and dark.
- **Camera:** 50 mm, locked on the trunk, very slow push
- **Characters:** —
- **Environment:** other:hagley_wood_day
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** S03 elm; sun angle and world colour keyed through two cycles; leaf particle bursts; lib_murder `snowfall()` short burst; ground material colour keyed (green → brown → white → green).
- **Lighting:** cycling day/night light; season colour shifts
- **FX:** falling leaves, light snow
- **On-screen text / overlays:** [counter] MONTHS DEAD (ESTIMATE) 0→18 (y=330)
- **SFX:** wind@0.0s(g0.3), rumble@0.5s(g0.2)
- **Music:** Pulse (0.6).
- **Transition in:** cut
- **Narration (L08):** "Investigators estimated she'd been dead about a year and a half."

## S09 · 26.6–29.6 s (3.0 s) · other:police_office_1943

- **Visual:** A plain height chart painted on a police-station wall: a flat, faceless grey outline of a woman slides in and stops at the 5 ft mark; a typed tag beside it fills in AGE: ABOUT 35 (EST.).
- **Camera:** 50 mm, slow push
- **Characters:** outline figure (flat grey silhouette, no face, no features)
- **Environment:** other:police_office_1943
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** Wall plane with painted ruler lines (emissive-lite white ticks every 6 in); outline = extruded 2D silhouette (flat grey, no features) keyed sliding in; small `paper_card()` tag.
- **Lighting:** cold overhead light, soft shadows
- **FX:** —
- **On-screen text / overlays:** [text] AGE: ABOUT 35 (EST.) / HEIGHT: 5 FT (y=420)
- **SFX:** click@0.2s(g0.3), typewriter@0.9s(g0.25)
- **Music:** Pulse (0.55).
- **Transition in:** cut
- **Narration (L09):** "She was probably about 35, and five feet tall."

## S10 · 29.6–32.5 s (2.9 s) · other:evidence_table_1943

- **Visual:** An evidence table under a desk lamp: a worn blue crepe-soled shoe, a thin gold ring on a folded cloth, a scrap of striped knitted fabric; each has a small paper tag. A card slides in.
- **Camera:** top-down 50 mm, slow rotation
- **Characters:** —
- **Environment:** other:evidence_table_1943
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** lib_murder `desk()` + `desk_lamp()`; shoe = simple lofted low shoe with a pale crepe sole; ring = torus (gold metallic); fabric = subdivided plane with a striped material; tags = small `paper_card()`s.
- **Lighting:** warm desk lamp pool, dark surroundings
- **FX:** dust motes
- **On-screen text / overlays:** [card] FOUND WITH HER: a shoe, a wedding ring, / scraps of clothing (y=820)
- **SFX:** click@0.3s(g0.3), typewriter@1.0s(g0.25)
- **Music:** Pulse (0.6).
- **Transition in:** cut
- **Narration (L10):** "There was a shoe, a wedding ring, and scraps of clothing."

## S11 · 32.5–34.6 s (2.1 s) · other:police_office_1943

- **Visual:** A police file on a desk: a typed record sheet; the NAME line stays blank as the typewriter carriage stops. A paper scrap slides up: NAME: UNKNOWN.
- **Camera:** 50 mm, slow push on the blank line
- **Characters:** —
- **Environment:** other:police_office_1943
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** lib_murder `case_folder(label='')` open on the S10 desk; lib_murder `box_typewriter()` in the background; lamp.
- **Lighting:** desk lamp; cold window light
- **FX:** —
- **On-screen text / overlays:** [document] NAME: UNKNOWN (y=420)
- **SFX:** typewriter@0.0s(g0.35), click@1.2s(g0.3)
- **Music:** Holds; thins (0.45).
- **Transition in:** cut
- **Narration (L11):** "But no one could put a name to her."

## S12 · 34.6–38.9 s (4.2 s) · other:brick_wall_graffiti_1944

- **Visual:** MID-POINT TURN. Night, a different brick wall: chalk letters write themselves stroke by stroke, HAGLEY WOOD BELLA, as if an invisible hand were drawing them; chalk dust falls.
- **Camera:** 35 mm, slow push, slight handheld
- **Characters:** —
- **Environment:** other:brick_wall_graffiti_1944
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** S01 materials on a second wall; letters revealed with a moving boolean-free mask (per-letter `key_vis`-style scale keys or lib_murder `curve_draw()` on stroke curves).
- **Lighting:** weak street lamp; cold night fill
- **FX:** chalk dust
- **On-screen text / overlays:** [stamp] 1944 (y=300)
- **SFX:** riser@0.0s(g0.3), click@0.4s(g0.2), hit@1.6s(g0.4)
- **Music:** Music swells (0.7).
- **Transition in:** flash
- **Narration (L12):** "Then, in 1944, the messages began, calling her Bella."

## S13 · 38.9–41.5 s (2.6 s) · other:blackout_street_night

- **Visual:** An empty wet street at night: a constable's torch beam sweeps across walls and doorways; chalk marks here and there; nobody in sight.
- **Camera:** 28 mm, slow pan following the torch beam
- **Characters:** constable (faceless silhouette with torch, mostly the beam)
- **Environment:** other:blackout_street_night
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** S02 street; lib_haunted `figure()` + `custodian_helmet()` + `hand_torch()`; lib_haunted `mat_wet_road()` on the cobbles; lib_murder `fog()`.
- **Lighting:** single hand-torch beam; faint lamp at the far end
- **FX:** fog, wet reflections
- **On-screen text / overlays:** —
- **SFX:** footsteps@0.0s(g0.35), wind@0.0s(g0.25)
- **Music:** Holds (0.6).
- **Transition in:** cut
- **Narration (L13):** "The writer of the messages was never found."

## S14 · 41.5–45.5 s (4.0 s) · other:evidence_board

- **Visual:** Evidence board under one hanging lamp: a paper card reading WITCHCRAFT? slams onto the cork beside a few blank question-mark cards.
- **Camera:** 50 mm, push-in on the card
- **Characters:** —
- **Environment:** other:evidence_board
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** lib_murder `evidence_board()` + `paper_card('WITCHCRAFT?', badge='THEORY')` + `slam_in()`; lib_murder `qmark_cards()` (blank, no names or faces).
- **Lighting:** single hanging lamp over the board
- **FX:** —
- **On-screen text / overlays:** [card] THEORY · 1945: A witchcraft ritual? / Suggested by an anthropologist (y=820); [label] THEORY (y=200)
- **SFX:** hit@0.3s(g0.4), whoosh@0.0s(g0.25)
- **Music:** Rhythmic pulse (0.65).
- **Transition in:** whip
- **Narration (L14):** "In 1945, an anthropologist suggested witchcraft."

## S15 · 45.5–47.8 s (2.3 s) · other:evidence_board

- **Visual:** Macro: a red rubber stamp comes down on the WITCHCRAFT? card and lifts away: DISMISSED.
- **Camera:** 85 mm macro, small shake on impact
- **Characters:** —
- **Environment:** other:evidence_board
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** Same board; lib_scuba `rubber_stamp()` keyed down and up; red 'DISMISSED' decal appears on impact.
- **Lighting:** board lamp
- **FX:** —
- **On-screen text / overlays:** [text] DISMISSED (y=520)
- **SFX:** hit@0.25s(g0.5)
- **Music:** Hit (0.6).
- **Transition in:** cut
- **Narration (L15):** "Investigators dismissed the idea."

## S16 · 47.8–52.6 s (4.8 s) · other:evidence_board

- **Visual:** A second card slams in beside the first: SPY RING?, with a red string to a generic folded newspaper pinned to the board (no real masthead).
- **Camera:** 50 mm, lateral move to the second card
- **Characters:** —
- **Environment:** other:evidence_board
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** Same board; `paper_card('SPY RING?')` + `slam_in()`; lib_murder `newspaper(masthead='')` pinned; `red_string()`.
- **Lighting:** board lamp
- **FX:** —
- **On-screen text / overlays:** [card] THEORY · 1953: A wartime spy ring? / Claimed in a letter to a paper (y=820); [label] THEORY (y=200)
- **SFX:** hit@0.3s(g0.4), click@1.4s(g0.25)
- **Music:** Pulse (0.65).
- **Transition in:** cut
- **Narration (L16):** "A 1953 letter to a local paper tied her to a wartime spy ring."

## S17 · 52.6–54.9 s (2.2 s) · other:evidence_board

- **Visual:** The stamp comes down on the second card: NEVER PROVEN. The lamp swings slightly.
- **Camera:** 85 mm macro on the card, small shake
- **Characters:** —
- **Environment:** other:evidence_board
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** Same board; `rubber_stamp()` keyed; lamp swing via rotation keys.
- **Lighting:** board lamp swinging
- **FX:** —
- **On-screen text / overlays:** [text] NEVER PROVEN (y=520)
- **SFX:** hit@0.2s(g0.5)
- **Music:** Hit, then drops (0.3).
- **Transition in:** cut
- **Narration (L17):** "That claim was never proven either."

## S18 · 54.9–59.1 s (4.2 s) · other:archive_shelf

- **Visual:** TWIST. A dim archive aisle: a long metal shelf of labelled boxes; one gap where a box should be, its paper label hanging. A document slides up listing what is missing.
- **Camera:** 35 mm, slow dolly along the shelf to the gap
- **Characters:** —
- **Environment:** other:archive_shelf
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** Shelving = box frames + cylinders; archive boxes = instanced boxes with paper labels; one gap; lib_haunted `flicker_lamp()`-style strip light.
- **Lighting:** cold strip light flickering once
- **FX:** dust motes
- **On-screen text / overlays:** [document] HAGLEY WOOD, 1943: SKELETON: MISSING / SKULL: MISSING / KEY CASE RECORDS: MISSING (y=70); [label] DOCUMENTED FACT (y=200)
- **SFX:** typewriter@0.4s(g0.3), rumble@2.0s(g0.2)
- **Music:** Near-silence after 'records' (0.1).
- **Transition in:** cut
- **Narration (L18):** "And today, even her skeleton is missing."
- **Narration (L19):** "So are key case records."

## S19 · 59.1–63.2 s (4.1 s) · other:wychbury_hill_obelisk

- **Visual:** Dusk on a grassy hilltop above the woods: a tall stone obelisk; painted letters on its weathered base read WHO PUT BELLA IN THE WITCH ELM. Wind moves the grass; the camera rises up the shaft. A small memorial line fades in.
- **Camera:** 24 mm, low then craning up the obelisk
- **Characters:** —
- **Environment:** other:wychbury_hill_obelisk
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** New simple prop: obelisk = tapered square shaft (≈25 m) on a stepped plinth, weathered stone material; painted text = `text3d()` with an off-white paint material on the plinth face; lib_cave `hill_set()`-style hill or `heightfield()`; lib_haunted `bare_forest()` in the valley; lib_murder `dawn_sky()` warm variant.
- **Lighting:** last orange light on the stone; blue valley below
- **FX:** wind in grass, mist in the valley
- **On-screen text / overlays:** [stamp] WYCHBURY OBELISK (y=300); [text] UNIDENTIFIED WOMAN / FOUND 18 APRIL 1943 (y=880)
- **SFX:** wind@0.0s(g0.4)
- **Music:** Returns quietly (0.45).
- **Transition in:** cut
- **Narration (L20):** "For decades, the question has kept reappearing on an obelisk near the wood."

## S20 · 63.2–66.8 s (3.6 s) · other:brick_wall_graffiti_1944

- **Visual:** LOOP FRAME: back to the S01 wall and lamp; the camera settles exactly into S01's first-frame composition on the chalk question, so a replay flows into 'Who put Bella down the Wych Elm?'.
- **Camera:** 50 mm, slow push ending on S01's first-frame pose
- **Characters:** —
- **Environment:** other:brick_wall_graffiti_1944
- **Build (lib_murder (+ lib_haunted figures/brick/street)):** S01 set and camera; final frame = S01 frame 1.
- **Lighting:** same weak street lamp
- **FX:** chalk dust motes, light fog
- **On-screen text / overlays:** —
- **SFX:** wind@0.0s(g0.25), sting@2.2s(g0.3)
- **Music:** Back to the opening level (0.5) for the loop.
- **Transition in:** cut
- **Narration (L21):** "More than 80 years on, all that's left is the question."

## Timing checks

- Line 1 starts at 0.15 s; the whole question lands by ~1.8 s and is already chalked on the wall in frame 1. Frame 1 moves (push-in, lamp flicker).
- New information every ≤4.9 s: Birmingham 1944 (≈2.1 s) → a real, unidentified woman (≈6.1 s) → April 1943, Hagley Wood (≈9.5 s) → the hollow (≈14.4 s) → the skull (≈18.1 s) → skeleton (≈20.1 s) → ~18 months (≈23.1 s) → ~35, 5 ft (≈26.7 s) → shoe/ring/clothes (≈29.7 s) → no name (≈32.6 s) → **turn (≈34.7 s): the messages begin** → writer never found (≈38.9 s) → witchcraft (≈41.6 s), dismissed (≈45.6 s) → spy ring (≈47.9 s), never proven (≈52.7 s) → **twist (≈54.9 s): skeleton and key records missing** → obelisk (≈59.2 s) → loop (≈63.3 s).
- Theory ladder (template beat) at 41–54 s: two THEORY cards, each closed at once by a stamp (DISMISSED / NEVER PROVEN); no theory is left standing as an answer, and nobody is named.
- Silence beats: after L06 (0.6 s) and after L19 (0.5 s, music near 0). Two max.
- Payoff in the last 8 s: the obelisk (L20) and the loop line (L21).
- Loop: L21 '…all that's left is the question.' → L01 'Who put Bella down the Wych Elm?'. S20 ends on S01's first frame (the chalk question on the wall).
- Overlay safety: map title single-line (HAGLEY WOOD); the map shows 0–2.3 s and the date stamp after it, so they never overlap (the map card is lifted out of the caption band by compose's avoid_captions(), as in earlier maps). Cards at y=820 (2 rows, end ≈1054); paper document y=70 (ends ≈1142); scrap document y=420; text overlays end by y≈966 (S19 memorial). Labels and stamps in the upper third. Nothing in y 1150–1400.
- Overlays only state what the narration states: 'AGE: ABOUT 35 (EST.)' keeps the estimate; theory cards say who proposed each idea and carry a THEORY badge; 'DISMISSED' and 'NEVER PROVEN' restate L15 and L17; the evidence log lists only what L18–L19 say is missing (the skeleton, incl. the skull, and key case records).
