# HAUNT-07 — Storyboard (Drivers Keep Reporting They Hit Her)

Vertical 9:16, 1080x1920, 24 fps. 13 shots, est. 50.0 s. Mood `haunted`. Captions: burned-in, word-synced, centred at y≈1240 (keep all text overlays out of y 1150–1400), accent words = `emphasis`. Overlays avoid the bottom 20% and right 15% (Shorts UI). Shot times are estimates; the pipeline derives real durations from TTS.

**Build notes.** One road set does almost everything: `archer_road()` widened to a dual carriageway (two lanes each way, central barrier boxes, crash barrier on the verge), `mat_wet_road`, `bare_forest()` on both verges, `streetlamp()` with long dark gaps, studio_lib fog + `rain()`. Three car props: S01/S02/S12/S13 windscreen interior (no make), S03 1970s saloon (generic, adapted from `car_1930s()` proportions), S07 1990s hatchback (box-car). `police_flash()` for S05. Evidence board/desk = `evidence_board()` + `pinned_card()`.
**The figure (S01, S12):** `figure(coat=True)` — NOT `pale_woman()`, whose long dress would read as period/bridal and imply the 1965 legend. Pale material, emission 0.15, faceless head, shoulder-length hair sphere optional. Seen for <0.5 s in S01 and small in the mirror in S12. It represents the claim, not any real person.
No real place signage, no real number plates. Kent road signs, if any, are blank.

## S01 · 0.0–3.9 s (3.9 s) · road_night

- **Visual:** COLD OPEN, moving at frame 1. Driver's POV through a windscreen (dashcam-style framing, wiper at rest, dark bonnet edge at bottom): headlights rake up the wet hill road. A pale faceless figure steps out from the verge into the beams at ~1.0 s; 2-frame white flash on the 'thump'. The figure is in frame for under 0.5 s.
- **Camera:** POV 24 mm, forward dolly at ~50 km/h feel, subtle road shake
- **Characters:** the figure (generic, faceless, pale; plain knee-length light coat, NOT a dress, veil or period clothing; modelled on nobody)
- **Environment:** road_night
- **Build (lib_haunted):** `archer_road()` re-dressed as a dual carriageway (wider, crash barrier boxes, `mat_wet_road`), `bare_forest()` verges, `streetlamp()` x2; car interior = dashboard box + windscreen frame; headlights = 2 spots; figure = `figure(coat=True)` with pale emissive material, `walk()` 3 steps; flash = 2-frame exposure spike.
- **Lighting:** headlight cones only + one distant sodium lamp
- **FX:** rain (light), ground fog, windscreen droplets
- **On-screen text / overlays:** [label] EYEWITNESS CLAIM (y=200); [label] DRAMATISATION (y=290)
- **SFX:** wind@0.0s(g0.3), hit@1.1s(g0.6), static@1.15s(g0.2)
- **Music:** None; road tone only.
- **Transition in:** cut
- **Narration (L01):** "A driver says he hit a girl on this hill."

## S02 · 3.9–5.5 s (1.5 s) · road_night

- **Visual:** Same POV a beat later, the car now stopped: the headlights light an empty stretch of wet road; nothing on the tarmac; the wipers sweep once and the hazard lights start to tick.
- **Camera:** POV 24 mm, locked, tiny settle after the stop; slow push
- **Characters:** —
- **Environment:** road_night
- **Build (lib_haunted):** S01 set and camera, car stopped; wiper keyed one sweep; amber emissive hazard keys.
- **Lighting:** headlight cones, amber hazard blink
- **FX:** rain (light), ground fog, windscreen droplets
- **On-screen text / overlays:** [label] EYEWITNESS CLAIM (y=200)
- **SFX:** click@0.2s(g0.3), wind@0.0s(g0.3)
- **Music:** Low drone enters (0.3).
- **Transition in:** cut
- **Narration (L02):** "Then she vanished."

## S03 · 5.5–9.2 s (3.7 s) · road_night

- **Visual:** Night dual carriageway climbing a wooded chalk hill: wet asphalt, white dashes, crash barrier, bare trees close on both verges, thin ground fog, sodium streetlamps spaced far apart (dark gaps between). High drone view looking down the hill, a single car's headlights crawling up it. Map card follows: Kent, Medway towns and Maidstone, pin on Blue Bell Hill.
- **Camera:** high 35 mm drone, slow descending push; map slides in at mid-shot
- **Characters:** one car (lights only)
- **Environment:** road_night
- **Build (lib_haunted):** Same road set, long section; `streetlamp()` x6; car = generic modern saloon block with headlight spots.
- **Lighting:** sodium pools, moonless sky, fog glow
- **FX:** ground fog
- **On-screen text / overlays:** [map] BLUE BELL HILL; [stamp] A229, KENT (y=300); [label] DOCUMENTED FACT (y=200)
- **SFX:** wind@0.0s(g0.35), whoosh@1.4s(g0.3)
- **Music:** Low drone enters (0.4).
- **Transition in:** cut
- **Narration (L03):** "Blue Bell Hill, Kent, on the A229 near Maidstone."

## S04 · 9.2–14.4 s (5.2 s) · road_night

- **Visual:** 1970s re-creation: a boxy 1970s saloon (generic, no badge) stopped askew on the hard shoulder, headlights on, driver's door open; a faceless man in a work jacket stands frozen beside the car looking back at the dark road. Nothing visible on the road yet.
- **Camera:** 35 mm low, slow push from the verge toward the car
- **Characters:** the driver (faceless man, work jacket)
- **Environment:** road_night
- **Build (lib_haunted):** `car_1930s()` body re-proportioned to a 1970s saloon (longer, lower, flat bonnet) or a new box-car prop; `figure(coat=True)` work jacket; tail-light emissive red.
- **Lighting:** headlights, red tail-light glow, one far sodium lamp
- **FX:** ground fog, exhaust vapour
- **On-screen text / overlays:** [label] EYEWITNESS CLAIM (y=200); [stamp] 1974 (y=300)
- **SFX:** door_creak@0.2s(g0.3), heartbeat@1.5s(g0.3)
- **Music:** Drone (0.5).
- **Transition in:** cut
- **Narration (L04):** "In 1974, a local bricklayer reported hitting a young girl here at night."

## S05 · 14.4–18.8 s (4.5 s) · road_night

- **Visual:** Close on the wet tarmac in the headlight beam: a tartan blanket is laid down over a small shape at the edge of frame (only the blanket's edge and hands placing it are seen). Then the car pulls away, the blanket left alone in the beam's fading light.
- **Camera:** 50 mm close, ground level; static then tail-light pull-away reflected on the road
- **Characters:** the driver (hands only)
- **Environment:** road_night
- **Build (lib_haunted):** Blanket = subdivided plane with tartan procedural texture, shape-keyed settle (or cloth-free drape over a low box); hands = `figure()` arms; car light keys.
- **Lighting:** headlights, then red tail-light receding, darkness
- **FX:** light rain on puddles
- **On-screen text / overlays:** [label] EYEWITNESS CLAIM (y=200)
- **SFX:** footsteps@0.0s(g0.25), door_creak@1.8s(g0.3)
- **Music:** Drone holds.
- **Transition in:** cut
- **Narration (L05):** "He covered her with a blanket and went for the police."

## S06 · 18.8–23.5 s (4.7 s) · road_night

- **Visual:** Blue flashing light washes over the same patch of road. Two faceless officer silhouettes with torches walk in; the torch beams find the blanket lying flat on the tarmac. Empty. One officer lifts a corner: nothing beneath.
- **Camera:** 35 mm, slow push to the blanket, torch beams crossing frame
- **Characters:** officers x2 (faceless, 1970s police coats and helmets as silhouettes), the driver (faceless)
- **Environment:** road_night
- **Build (lib_haunted):** `police_flash()` on a parked car; `figure(coat=True, cap=True)` x2 with torch spots; blanket corner lifted via keyframed vertex group/shape key.
- **Lighting:** police blue flash + two torch cones
- **FX:** ground fog, light rain
- **On-screen text / overlays:** [label] EYEWITNESS CLAIM (y=200)
- **SFX:** footsteps@0.0s(g0.3), sting@2.4s(g0.4)
- **Music:** Drone thins (0.35).
- **Transition in:** cut
- **Narration (L06):** "When he came back with officers, only the blanket was there."

## S07 · 23.5–25.7 s (2.2 s) · timeline

- **Visual:** Pattern interrupt: a timeline line draws from 1974 to 1992 over a dark road plate; small red car icons pop along it.
- **Camera:** 2.5D lateral pan
- **Characters:** —
- **Environment:** timeline
- **Build (lib_haunted):** Overlay over a dimmed, blurred S02 plate.
- **Lighting:** graphic
- **FX:** —
- **On-screen text / overlays:** [timeline] REPORTS (y=900)
- **SFX:** whoosh@0.0s(g0.35), click@1.0s(g0.3)
- **Music:** Drone rises (0.55).
- **Transition in:** whip
- **Narration (L07):** "And he wasn't the last."

## S08 · 25.7–30.5 s (4.8 s) · road_night

- **Visual:** 1990s re-creation: a modern hatchback stopped on the hard shoulder with hazard lights blinking; the faceless driver walks back along the barrier with a small torch, sweeping the verge and the road; rain heavier.
- **Camera:** 35 mm handheld following the driver from behind
- **Characters:** driver (faceless, 1990s jacket)
- **Environment:** road_night
- **Build (lib_haunted):** Hatchback = box-car prop; hazard lights = amber emissive keyed 1.5 Hz; `handheld()`; `rain()`.
- **Lighting:** amber hazard blinks + torch + far sodium lamp
- **FX:** rain, ground fog
- **On-screen text / overlays:** [label] EYEWITNESS CLAIM (y=200); [stamp] NOVEMBER 1992 (y=300)
- **SFX:** footsteps@0.0s(g0.3), click@0.3s(g0.2), wind@0.0s(g0.3)
- **Music:** Drone (0.6).
- **Transition in:** cut
- **Narration (L08):** "In November 1992, motorists again reported running down a young woman here."

## S09 · 30.5–33.6 s (3.0 s) · road_night

- **Visual:** Wide from above: the torch beam sweeping a long empty stretch of wet road. Nothing. The beam stops, lowers.
- **Camera:** high 28 mm crane up and away
- **Characters:** driver (tiny, faceless)
- **Environment:** road_night
- **Build (lib_haunted):** S07 set; crane keys with `cam_move()`.
- **Lighting:** single torch; hazard blink
- **FX:** rain, ground fog
- **On-screen text / overlays:** [label] EYEWITNESS CLAIM (y=200)
- **SFX:** wind@0.0s(g0.35)
- **Music:** Drone thins (0.4).
- **Transition in:** cut
- **Narration (L09):** "No trace of her was ever found."

## S10 · 33.6–38.0 s (4.5 s) · other:evidence_board

- **Visual:** Sceptic beat: an evidence board under a desk lamp. Pinned cards: 'VANISHING HITCHHIKER', 'PHANTOM ON THE ROAD', and a small world map with pins on several continents joined by string.
- **Camera:** 35 mm slow pan across the cards
- **Characters:** —
- **Environment:** other:evidence_board
- **Build (lib_haunted):** `evidence_board()` + `pinned_card()` x3; map card = plane with simple continent shapes; red string curves.
- **Lighting:** warm desk lamp, dark room
- **FX:** dust
- **On-screen text / overlays:** [card] A road-ghost story told / worldwide (folklorists) (y=820); [label] FOLKLORE (y=200)
- **SFX:** click@0.2s(g0.25)
- **Music:** Near-silence (0.25).
- **Transition in:** cut
- **Narration (L10):** "Sceptics call it a classic folk tale, told on roads worldwide."

## S11 · 38.0–41.7 s (3.7 s) · document

- **Visual:** Paper card with three conflicting start-dates typed and struck through in turn; the last line reads 'NOBODY AGREES'.
- **Camera:** top-down 50 mm, slight push
- **Characters:** —
- **Environment:** document
- **Build (lib_haunted):** Document overlay over the S09 desk (defocused).
- **Lighting:** desk lamp
- **FX:** —
- **On-screen text / overlays:** [document] SIGHTINGS BEGAN: / ~~1930s?~~ / ~~1960s?~~ / ~~1970s?~~ / NOBODY AGREES; [label] DISPUTED (y=200)
- **SFX:** typewriter@0.3s(g0.3)
- **Music:** Drone very low (0.2).
- **Transition in:** cut
- **Narration (L11):** "Even local accounts disagree on when the sightings began."

## S12 · 41.7–46.0 s (4.3 s) · road_night

- **Visual:** DEAD-AIR REVEAL: driver's POV again, a normal night drive while the line is spoken; then, in the 1.2 s of silence after it, but the camera tilts to the rear-view mirror. The road behind is red with tail-light glow. In the mirror, small and still, the pale faceless figure stands in the lane behind the car. She does not move. Generic figure, plain coat.
- **Camera:** POV 50 mm locked on the mirror, slowest push
- **Characters:** the figure (generic, faceless, pale; plain knee-length light coat, NOT a dress, veil or period clothing; modelled on nobody)
- **Environment:** road_night
- **Build (lib_haunted):** Mirror = rounded box with reflective plane rendered as an inset (second camera render composited, or a real mirror material on EEVEE with screen-space reflections); figure = `figure(coat=True)`, pale emissive 0.15, 30 m behind.
- **Lighting:** red tail-light glow behind; dashboard dim
- **FX:** ground fog, rain on rear window
- **On-screen text / overlays:** [label] DRAMATISATION (y=200)
- **SFX:** creak@0.6s(g0.3)
- **Music:** Drone cuts to silence after the line (dead air); one creak.
- **Transition in:** cut
- **Narration (L12):** "None of these reports has ever been confirmed."

## S13 · 46.0–50.0 s (4.0 s) · road_night

- **Visual:** LOOP FRAME: back to the S01 windscreen POV, identical framing and speed, headlights raking up the empty wet road; ends exactly on S01's frame 1 so the replay continues seamlessly into 'A driver says he hit a girl...'.
- **Camera:** POV 24 mm, same forward dolly as S01 start
- **Characters:** —
- **Environment:** road_night
- **Build (lib_haunted):** S01 set and camera path (first ~2 s), no figure.
- **Lighting:** headlight cones + distant sodium lamp
- **FX:** rain (light), ground fog, windscreen droplets
- **On-screen text / overlays:** —
- **SFX:** wind@0.0s(g0.3)
- **Music:** Road tone only (matches S01).
- **Transition in:** cut
- **Narration (L13):** "So if someone steps into your headlights on this hill..."

## Timing checks

- Line 1 starts at 0.0 s; "hit a girl" lands by ~1.6 s while the figure steps into the beams (~1.0 s). Frame 1 is moving (POV dolly).
- New information every ~3–5 s: vanished (≈3 s) → place (≈5 s) → 1974 bricklayer (≈9 s) → blanket/police (≈14 s) → only the blanket (≈19 s) → **turn (≈23 s): "he wasn't the last"** → 1992 (≈24 s) → no trace (≈29 s) → sceptics (≈32 s) → dating disputed (≈36 s) → never confirmed (≈39 s) → dead-air mirror reveal (≈42 s) → loop (≈44 s).
- Silence beats: 0.45 s after L06 and the 1.2 s dead air after L12 (S12) — two max.
- Loop: L13 "So if someone steps into your headlights on this hill..." → L01 "A driver says he hit a girl on this hill." S13 ends on S01 frame 1.
- Overlay safety: labels y=200/290, stamps y=300, card y=820 (ends ≈1054), timeline y=900, document centred upper; captions sit at y≈1240.
