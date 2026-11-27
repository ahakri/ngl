# HAUNT-10 — Storyboard (The Staircase That Leads Into the Ceiling)

Vertical 9:16, 1080x1920, 24 fps. 13 shots, measured 47.7 s. Mood `haunted`. Captions: burned-in, word-synced, centred at y≈1240 (keep all text overlays out of y 1150–1400), accent words = `emphasis`. Overlays avoid the bottom 20% and right 15% (Shorts UI). Shot times come from a scratch TTS measurement; the pipeline derives the real durations from its own render.

**Build notes.** Sets: (1) the staircase room = one straight steep flight (lib_haunted `manor_staircase()` stripped down, or `step_pos()` boxes + turned rail) in `mat_oak()`, papered walls via `wall_with_openings()` + `mat_wallpaper()` recoloured to a muted Victorian pattern, a ceiling plane that cuts the top step, `gas_lamp()`, `dust()`, thin `room_fog()`; S09 reuses it as a cut-away with a later floor keyed in above the flight; (2) the mansion = generic rambling Queen Anne mass built from studio_lib `house_exterior()` blocks + lib_murder `gable_box()` wings, turret cylinders with cone roofs, a seven-level tower for S08 whose top three levels are separate chunks; it must not be a replica of the real house; (3) the 1880s farmhouse = studio_lib `house_exterior()` + orchard (`leafy_trees()` small) + lib_murder `fence()`; (4) parlour = table, cloth, `candle()`, two faceless seated silhouettes, a wall rack of generic rifles and `orb()`-based wisps; (5) door to nowhere = upper-floor exterior wall with an outward door and no balcony, garden + mist below. Figures: lib_haunted `figure()` (dress=True for Sarah; plain for workers/visitors), `coat_figure()` for the S12 dramatisation. No real logos or signage.

## S01 · 0.0–2.7 s (2.7 s) · room

- **Visual:** COLD OPEN, moving at frame 1. A narrow Victorian staircase of dark varnished wood with a turned handrail rises steeply between papered walls and ends flush against a plaster ceiling: the top step meets the ceiling with nowhere to go. Dust hangs in the light of one wall gas lamp.
- **Camera:** 28 mm, low from the bottom step, slow tilt and push up the flight toward the ceiling
- **Characters:** —
- **Environment:** room
- **Build (lib_haunted (+ studio_lib houses, lib_murder props)):** Stair = lib_haunted `manor_staircase(return_flight=False, hall=False)` stripped to one straight flight (or 14 `step_pos()` boxes + rail cylinders) in `mat_oak()`; walls = `wall_with_openings()` with a muted Victorian `mat_wallpaper()` recolour; ceiling plane cutting the top step; `gas_lamp()`; `dust()`; `room_fog()` thin.
- **Lighting:** one warm gas-lamp glow, deep shadow above; faint cool fill
- **FX:** dust motes, light flicker
- **On-screen text / overlays:** [label] DOCUMENTED FACT (y=200)
- **SFX:** creak@0.3s(g0.3), sting@1.6s(g0.35)
- **Music:** Room tone; low drone enters (0.35).
- **Transition in:** cut
- **Narration (L01):** "This staircase climbs straight into the ceiling."

## S02 · 2.7–5.3 s (2.7 s) · room

- **Visual:** The camera arrives at the top step: the ceiling plaster is inches from the lens. The gas lamp below dips and recovers; a draught stirs the dust.
- **Camera:** 28 mm, slow push to the ceiling, slight roll
- **Characters:** —
- **Environment:** room
- **Build (lib_haunted (+ studio_lib houses, lib_murder props)):** S01 set; `flicker_lamp()`-style dip on the gas lamp via `key_energy()`.
- **Lighting:** gas lamp from below; shadows climbing the walls
- **FX:** dust motes, flicker
- **On-screen text / overlays:** [label] FOLKLORE (y=200)
- **SFX:** door_creak@0.5s(g0.25)
- **Music:** Drone (0.4).
- **Transition in:** cut
- **Narration (L02):** "Legend says it was built to confuse ghosts."

## S03 · 5.3–8.6 s (3.2 s) · house_exterior

- **Visual:** Dusk: a sprawling Victorian mansion (generic, not a replica) of turrets, gables and bay windows rambling across a lawn behind a low hedge; a few windows glow amber. The camera pushes in over the hedge.
- **Camera:** 35 mm, slow push-in at eye level
- **Characters:** —
- **Environment:** house_exterior
- **Build (lib_haunted (+ studio_lib houses, lib_murder props)):** Mansion = several studio_lib `house_exterior()` blocks + lib_murder `gable_box()` wings joined irregularly, two turret cylinders with cone roofs, bay boxes; window glow via lib_murder `window_keys()`; lib_murder `dawn_sky()` violet variant; hedge boxes.
- **Lighting:** violet dusk sky; warm window glow
- **FX:** light mist
- **On-screen text / overlays:** [stamp] SAN JOSE, CALIFORNIA (y=300); [label] DOCUMENTED FACT (y=200)
- **SFX:** wind@0.0s(g0.25), creak@1.6s(g0.2)
- **Music:** Drone builds (0.45).
- **Transition in:** cut
- **Narration (L03):** "Winchester Mystery House, San Jose, California."

## S04 · 8.6–11.6 s (3.1 s) · other:orchard_farmhouse_1880s

- **Visual:** Daylight, the 1880s: a modest two-storey farmhouse among young fruit trees in a flat valley. A faceless woman's silhouette in a long dark Victorian dress stands at the gate, looking at it.
- **Camera:** 35 mm, slow lateral move along the fence
- **Characters:** Sarah Winchester (faceless silhouette, long dark dress; not a likeness)
- **Environment:** other:orchard_farmhouse_1880s
- **Build (lib_haunted (+ studio_lib houses, lib_murder props)):** studio_lib `house_exterior()` (two-storey gabled); orchard = small lib_haunted `leafy_trees()`; lib_murder `fence()` with a gate; figure = lib_haunted `figure(dress=True)` (faceless, dark).
- **Lighting:** soft warm sun, long shadows
- **FX:** dust in sunlight
- **On-screen text / overlays:** [stamp] 1880s (y=300); [label] DOCUMENTED FACT (y=200)
- **SFX:** wind@0.0s(g0.2), footsteps@1.2s(g0.2)
- **Music:** Warm pad (0.4).
- **Transition in:** cut
- **Narration (L04):** "Rifle heiress Sarah Winchester bought a farmhouse here."

## S05 · 11.6–16.4 s (4.7 s) · other:construction_timelapse

- **Visual:** Time-lapse from a fixed hilltop view: the farmhouse sprouts wings, towers and gables; scaffolding appears and vanishes; days flicker into nights. A timeline draws across the sky.
- **Camera:** 35 mm, locked wide, very slow push
- **Characters:** —
- **Environment:** other:construction_timelapse
- **Build (lib_haunted (+ studio_lib houses, lib_murder props)):** S04 house + S03 mansion parts popping in with `key_vis`/scale keys; scaffolds = thin box lattices; sun rotation keyed.
- **Lighting:** cycling day/night light
- **FX:** dust, scaffold pop-ins
- **On-screen text / overlays:** [timeline] ADDED TO FOR DECADES: 1880s → 1922 (y=900); [label] DOCUMENTED FACT (y=200)
- **SFX:** click@0.2s(g0.25), whoosh@1.0s(g0.3)
- **Music:** Pulse (0.45).
- **Transition in:** whip
- **Narration (L05):** "She kept adding to it for decades, until she died in 1922."

## S06 · 16.4–20.9 s (4.6 s) · room

- **Visual:** A candlelit parlour: a round table under a dark cloth, a single candle, two faceless seated silhouettes facing each other. On the wall behind, a rack of generic lever-action rifles (no markings); pale wisps drift out of the dark around them and fade.
- **Camera:** 50 mm, slow orbit around the table toward the rifle rack
- **Characters:** medium (faceless silhouette, legend figure), Sarah (faceless silhouette, long dark dress)
- **Environment:** room
- **Build (lib_haunted (+ studio_lib houses, lib_murder props)):** Room = lib_haunted `wall_with_openings()` + `mat_wallpaper()`; table = cylinder + cloth; `candle()`; two lib_haunted `seated_woman()`-style seated silhouettes (dark material, alpha 1, faceless); rifles = simple low-poly generic lever-action shapes on a wall rack; wisps = lib_haunted `orb()` variants stretched into soft emissive streaks with alpha fades.
- **Lighting:** one candle, deep shadows, faint cold rim light
- **FX:** candle smoke, dust
- **On-screen text / overlays:** [label] FOLKLORE (y=200); [label] DRAMATISATION (y=290)
- **SFX:** heartbeat@0.2s(g0.25), door_creak@1.5s(g0.2)
- **Music:** Drone thickens (0.5).
- **Transition in:** cut
- **Narration (L06):** "A medium supposedly warned her about the ghosts of Winchester rifle victims."

## S07 · 20.9–24.9 s (3.9 s) · house_exterior

- **Visual:** Night: lantern light on the half-built mansion; faceless carpenters' silhouettes hammer on scaffolding as a new gable rises. The legend's endless building.
- **Camera:** 35 mm, slow crane up the scaffold
- **Characters:** carpenters x3 (faceless silhouettes)
- **Environment:** house_exterior
- **Build (lib_haunted (+ studio_lib houses, lib_murder props)):** S03 mansion with a scaffold lattice; lib_murder `lantern()` x3; carpenters = lib_haunted `figure()` with simple hammer swing keys.
- **Lighting:** warm lanterns, dark blue night
- **FX:** sawdust, lantern flicker
- **On-screen text / overlays:** [label] FOLKLORE (y=200)
- **SFX:** hit@0.2s(g0.3), hit@0.9s(g0.25), hit@1.6s(g0.3)
- **Music:** Pulse (0.55), then cut for the turn.
- **Transition in:** cut
- **Narration (L07):** "To escape them, the story goes, she had to keep building forever."

## S08 · 24.9–29.5 s (4.7 s) · house_exterior

- **Visual:** MID-POINT TURN. Day, the mansion's tall central tower and upper floors shudder; chimneys topple and the top storeys crumble inward in a cloud of dust; the camera shakes hard.
- **Camera:** 35 mm, low angle, heavy shake
- **Characters:** —
- **Environment:** house_exterior
- **Build (lib_haunted (+ studio_lib houses, lib_murder props)):** S03 mansion with a seven-level tower (stacked boxes + cupola); top three levels as separate chunks keyed falling with rotation; `dust()` burst + lib_murder `cloud_volume()`-style puff; camera shake via `handheld()` high amplitude.
- **Lighting:** flat morning light, dust haze
- **FX:** dust cloud, falling debris
- **On-screen text / overlays:** [stamp] SAN JOSE, 1906 (y=300); [label] DOCUMENTED FACT (y=200)
- **SFX:** rumble@0.0s(g0.6), boom@0.8s(g0.5)
- **Music:** Hit; music cuts to drone (0.3).
- **Transition in:** flash
- **Narration (L08):** "In 1906, an earthquake cut the house from seven floors to four."

## S09 · 29.5–33.4 s (3.9 s) · room

- **Visual:** Back to the staircase, now in flat daylight and cut away like a dollhouse: the ceiling lifts off to show a later floor built right over the top of the old flight. A card slides in.
- **Camera:** 2.5D-feel orthographic side view, slow pull-back
- **Characters:** —
- **Environment:** room
- **Build (lib_haunted (+ studio_lib houses, lib_murder props)):** S01 staircase in a sectioned box room (front wall hidden); upper floor slab + a second room keyed up into place over the flight; flat area light.
- **Lighting:** even daylight; no flicker
- **FX:** —
- **On-screen text / overlays:** [card] THE PRACTICAL ANSWER: Stairs left over from / remodeling (likely) (y=820); [label] THEORY (y=200)
- **SFX:** whoosh@0.1s(g0.3), click@0.9s(g0.25)
- **Music:** Lighter, rational (0.35).
- **Transition in:** cut
- **Narration (L09):** "And the stairs into the ceiling? Likely leftovers from remodeling."

## S10 · 33.4–38.2 s (4.8 s) · document

- **Visual:** A plain typed index card slides onto a desk under a lamp: the biographer's name and the finding.
- **Camera:** top-down 50 mm, slight push
- **Characters:** —
- **Environment:** document
- **Build (lib_haunted (+ studio_lib houses, lib_murder props)):** lib_murder `desk()` + `desk_lamp()` under the overlay; generic card (no book cover reproduced).
- **Lighting:** warm desk lamp
- **FX:** —
- **On-screen text / overlays:** [document] SARAH WINCHESTER: BIOGRAPHER: MARY JO IGNOFFO / EVIDENCE FOR THE / GHOST STORY: / NONE FOUND (y=70); [label] DOCUMENTED FACT (y=200)
- **SFX:** typewriter@0.3s(g0.3)
- **Music:** Holds (0.3).
- **Transition in:** cut
- **Narration (L10):** "Her biographer, Mary Jo Ignoffo, found no evidence for the ghost story."

## S11 · 38.2–41.7 s (3.5 s) · house_exterior

- **Visual:** 1920s daytime: the mansion's front gate with a small ticket booth; a short line of faceless visitors in hats and coats; two boxy vintage cars parked by the hedge.
- **Camera:** 35 mm, slow lateral dolly along the queue
- **Characters:** visitors x5 (faceless silhouettes, 1920s hats and coats)
- **Environment:** house_exterior
- **Build (lib_haunted (+ studio_lib houses, lib_murder props)):** S03 mansion by day; booth = box + awning (blank signboard, no real logo); lib_haunted `box_car()` x2 restyled boxy; visitors = lib_haunted `figure(coat=True)` with hat discs.
- **Lighting:** bright flat day
- **FX:** —
- **On-screen text / overlays:** [stamp] 1923 (y=300); [label] DOCUMENTED FACT (y=200)
- **SFX:** footsteps@0.2s(g0.3), click@1.4s(g0.25)
- **Music:** Thins out (0.25) toward silence.
- **Transition in:** cut
- **Narration (L11):** "Soon after she died, the house opened to paying visitors."

## S12 · 41.7–44.5 s (2.8 s) · house_exterior

- **Visual:** DEAD-AIR REVEAL. Night: from inside an upstairs room, a visitor's lantern lights an exterior door; it swings open onto nothing, a sheer drop to the dark garden. In the silence, the lantern beam finds a pale, faceless figure standing far below, looking up. Then it is gone.
- **Camera:** 28 mm POV at the doorway, slow tilt down into the drop
- **Characters:** visitor (lantern only), pale figure (generic, faceless, plain coat; dramatisation, not Sarah Winchester)
- **Environment:** house_exterior
- **Build (lib_haunted (+ studio_lib houses, lib_murder props)):** Upper-floor wall of the S03 mansion with `door_slab()` opening outward onto air (no balcony); garden below = ground plane + hedges + mist; figure = lib_haunted `coat_figure()` (pale, faint glow) visible for ~0.6 s, then `key_vis` off.
- **Lighting:** one lantern; moonlight on the garden
- **FX:** mist, dust
- **On-screen text / overlays:** [text] THE DOOR TO NOWHERE (y=420); [label] DRAMATISATION (y=200)
- **SFX:** door_creak@0.3s(g0.45), wind@1.0s(g0.3), sting@2.6s(g0.35)
- **Music:** Silence (0.0) for ~1 s, then a single sting.
- **Transition in:** cut
- **Narration (L12):** "The ghost story sold the tickets."

## S13 · 44.5–47.7 s (3.2 s) · room

- **Visual:** LOOP FRAME: back at the bottom of the staircase in gas-lamp light; the camera settles into S01's first-frame position, so a replay flows into 'This staircase climbs straight into the ceiling.'
- **Camera:** 28 mm, slow settle into S01's start pose
- **Characters:** —
- **Environment:** room
- **Build (lib_haunted (+ studio_lib houses, lib_murder props)):** S01 set and camera; final frame = S01 frame 1.
- **Lighting:** gas lamp, as S01
- **FX:** dust motes
- **On-screen text / overlays:** —
- **SFX:** creak@0.4s(g0.25)
- **Music:** Drone returns quietly (0.35) to match the opening.
- **Transition in:** cut
- **Narration (L13):** "Whatever the truth, one thing hasn't changed."

## Timing checks

- Line 1 starts at 0.15 s; "staircase … into the ceiling" lands by ~2.4 s, with the stair-to-ceiling already in frame 1 and the camera already tilting up the flight.
- New information every ≤4.8 s: the legend (≈2.8 s) → place (≈5.4 s) → Sarah Winchester, farmhouse (≈8.7 s) → decades of building, 1922 (≈11.7 s) → the medium and the rifle ghosts (≈16.5 s) → endless building (≈21.0 s) → **turn (≈24.9 s): 1906, seven floors to four** → remodeling (≈29.6 s) → the biographer (≈33.5 s) → tourism (≈38.3 s) → the ghost story sold tickets (≈41.8 s) → dead air → loop (≈44.6 s).
- Labels: every shot except the loop frame carries a badge (DOCUMENTED FACT / FOLKLORE / THEORY / DRAMATISATION); S06 carries FOLKLORE + DRAMATISATION.
- Silence: one dead-air beat after L12 (1.0 s, music at 0) for the door-to-nowhere reveal, under the 1.2 s QC silence flag; other pauses ≤0.4 s.
- Sceptic beat (template 40–45 s) runs from 30 to 45 s here: remodeling (THEORY card), the biographer's finding, the tourist marketing.
- Loop: L13 "Whatever the truth, one thing hasn't changed." → L01 "This staircase climbs straight into the ceiling." S13 ends on S01's first frame.
- Overlay safety: stamps at y=300, labels at y=200/290, timeline y=900, card y=820 (header + 2 rows, ends ≈1054), document y=70 (ends ≈1142), text y=420. Nothing in y 1150–1400.
- Overlays only state what the narration states: "Stairs left over from remodeling (likely)" keeps L09's hedge; the biographer card says "EVIDENCE FOR THE GHOST STORY: NONE FOUND" (L10); the S04 stamp "1880s" avoids the disputed exact year (1884 vs 1886); S08 "SAN JOSE, 1906" and S11 "1923" match L08 and L11 ("soon after she died": 1922 → 1923).
