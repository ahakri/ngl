# CAVE-06 — Storyboard (It Looks Like a Pond. Divers Call It Everest.)

Vertical 9:16, 1080x1920, 24 fps. 16 shots, est. 66.3 s. Captions: burned-in word-synced, 1–4 words per chunk, centre-upper safe zone, cyan accent on `emphasis` words. Keep overlays out of bottom 20% / right 15% (Shorts UI).
Shot times are estimates from narration timing; the pipeline derives real durations from TTS.

**Build notes.** Sets: (1) surface = `crater(R≈5, depth≈2)` with a dark-green `pool_mat` + `sky_world()` + `bushes()` + studio_lib `forest()`/`tree()` (live oaks/cypress approximated with bare-tree builder + green canopy blobs); (2) the Chimney = `shaft()` narrow (r≈1.2 m) dropping out of the pool; (3) the Ballroom = huge `shaft()` cavern r≈20 m with `chamber_floor()` debris cone, `water()` and `beam_cone()`; (4) 2.5D section = `xsection()` + `glow_dot()`. Warning sign = flat panel on a pipe stake with `text()` + simple reaper silhouette (plane with alpha), generic, no agency logo. Feet are used throughout (US site; sources are in feet).

## S01 · 0.0–3.3 s (3.3 s) · other:florida_sinkhole_exterior

- **Visual:** COLD OPEN, camera already moving. Top-down drone view of a small, still, dark-green pond ringed by swamp woods and a sandy dive-entry slope. Morning light. Nothing about it looks dangerous.
- **Camera:** Top-down 28 mm, slow descending push toward the pond centre (pond fills the middle third).
- **Characters:** —
- **Environment:** other:florida_sinkhole_exterior
- **Build (lib_cave):** `crater(R=5, depth=2)` with green `pool_mat`; `bushes()`; studio_lib `forest()`; `sky_world()` + `sun_from(sun_dir(25, 120))`.
- **Lighting:** Soft morning sun, light haze; pond surface reflects sky.
- **FX:** mist, leaf_drift
- **On-screen text / overlays:** [counter] DIVERS DEAD SINCE 1981; [label] DISPUTED
- **SFX:** wind@0.0s(g0.35), sting@0.8s(g0.5)
- **Music:** Low drone enters (curve 0.5).
- **Transition in:** cut
- **Narration (L01):** "This pond has killed at least ten divers."

## S02 · 3.3–7.0 s (3.7 s) · other:florida_sinkhole_exterior

- **Visual:** Ground level at the water's edge: cypress knees, duckweed-green surface, a dragonfly-sized speck skims. A dive line tied to a root disappears into the water (the only hint).
- **Camera:** Low 35 mm dolly along the bank; rack focus from the bank to the line entering the water.
- **Characters:** —
- **Environment:** other:florida_sinkhole_exterior
- **Build (lib_cave):** Surface set close-up; `line()` from root into water; `floor(ripples=True)` for the pond surface.
- **Lighting:** Dappled sun through canopy.
- **FX:** mist, ripples
- **On-screen text / overlays:** [stamp] FLORIDA, USA
- **SFX:** wind@0.0s(g0.3), creak@1.2s(g0.2)
- **Music:** Drone holds.
- **Transition in:** cut
- **Narration (L02):** "From above, it's just a pond in the woods."

## S03 · 7.0–11.5 s (4.5 s) · other:vertical_shaft_descent

- **Visual:** Camera sinks through the green surface. Light dies fast. A single diver (blue fins) descends head-down through a narrow rock throat barely wider than his tanks, following the line.
- **Camera:** Continuous move from above water to below (water plane wipe), then top-down 20 mm following the diver.
- **Characters:** diver_A (blue fins, twin tanks, helmet torch, faceless)
- **Environment:** other:vertical_shaft_descent
- **Build (lib_cave):** `shaft(z_top=0, z_bot=-25, radius_fn≈1.2 m)` + `water(green→black)`; `diver()` with `move_along()`.
- **Lighting:** Green daylight from above fading to black; torch cone.
- **FX:** particles_dust, volumetric_water, bubbles
- **On-screen text / overlays:** [text] THE CHIMNEY
- **SFX:** whoosh@0.0s(g0.5), underwater_amb@0.3s(g0.5), bubbles@0.6s(g0.4)
- **Music:** Pulse added (curve 0.7).
- **Transition in:** cut
- **Narration (L03):** "Below, a narrow shaft called the Chimney drops into the dark."

## S04 · 11.5–16.1 s (4.6 s) · cave_tunnel

- **Visual:** THE REVEAL. The diver drops out of the shaft's mouth into a vast black chamber; his torch beam reaches nothing. A slow pull-back shows him as a speck at the ceiling, with a mound of debris rising from the floor far below.
- **Camera:** Wide 18 mm pull-back and tilt down, scale reveal; diver tiny in the upper third.
- **Characters:** diver_A (blue fins)
- **Environment:** cave_tunnel
- **Build (lib_cave):** `shaft()` r≈20 m cavern + `chamber_floor()` debris cone; `beam_cone()` on the diver light.
- **Lighting:** Torch cone + one faint shaft of green daylight from the chimney; volumetric.
- **FX:** volumetric_light_shafts, particles_dust
- **On-screen text / overlays:** [text] THE BALLROOM
- **SFX:** rumble@0.0s(g0.5), riser@0.8s(g0.4)
- **Music:** Open pad (curve 0.7).
- **Transition in:** cut
- **Narration (L04):** "Then it opens into a huge room divers call the Ballroom."

## S05 · 16.1–20.9 s (4.9 s) · map

- **Visual:** Pattern interrupt. Map card of Florida; route line draws south along the Gulf coast; pin drops north of Tampa near Weeki Wachee.
- **Camera:** Overlay card over a blurred Ballroom background.
- **Characters:** —
- **Environment:** map
- **Build (lib_cave):** 2D overlay only; background = S04 render defocused.
- **Lighting:** Graphic.
- **FX:** —
- **On-screen text / overlays:** [map] EAGLE'S NEST SINK · HERNANDO COUNTY, FLORIDA; [text] "EVEREST OF CAVE DIVING"
- **SFX:** whoosh@0.0s(g0.5), click@2.0s(g0.4)
- **Music:** Pulse (curve 0.6).
- **Transition in:** whip
- **Narration (L05):** "Florida's Eagle's Nest. Divers call it the Mount Everest of cave diving."

## S06 · 20.9–25.8 s (4.9 s) · other:cross_section_2.5D

- **Visual:** Schematic side-section: pond at top, thin chimney, the wide Ballroom, then tunnels stepping down and away. A cyan dot travels the route; a depth bar fills.
- **Camera:** Locked diagram; slow vertical pan downward with the dot.
- **Characters:** diver_dot (cyan)
- **Environment:** other:cross_section_2.5D
- **Build (lib_cave):** `xsection()` + `glow_dot()` + `move_along()`.
- **Lighting:** Graphic; black, cyan outline.
- **FX:** —
- **On-screen text / overlays:** [depth] 0 → 300 FT; [text] SCHEMATIC, NOT TO SCALE
- **SFX:** sonar@0.0s(g0.4)
- **Music:** Pulse (curve 0.75).
- **Transition in:** cut
- **Narration (L06):** "The cave runs on past the Ballroom, to about 300 feet deep."

## S07 · 25.8–30.7 s (4.9 s) · cave_tunnel

- **Visual:** The diver's torch sweeps the debris slope and lands on a square white sign on a pipe stake, a simple hooded-skeleton silhouette printed on it. Silt drifts across.
- **Camera:** POV 24 mm handheld; pan stops dead on the sign; slow push.
- **Characters:** —
- **Environment:** cave_tunnel
- **Build (lib_cave):** Ballroom floor set; sign = plane + cylinder stake; reaper = alpha-mask plane (simple drawn silhouette, generic).
- **Lighting:** Torch cone only.
- **FX:** silt, torch_cone
- **On-screen text / overlays:** [depth] 110 → 120 FT
- **SFX:** breath@0.0s(g0.5), heartbeat@1.2s(g0.5)
- **Music:** Drop to drone (curve 0.8).
- **Transition in:** cut
- **Narration (L07):** "120 feet down, there's a sign with the Grim Reaper on it."

## S08 · 30.7–34.7 s (3.9 s) · cave_tunnel

- **Visual:** MID-POINT TURN. Close-up of the sign face; lettering readable: STOP! / PREVENT YOUR DEATH! / GO NO FARTHER. Torchlight flickers across it once.
- **Camera:** Macro 50 mm, slow push; slight handheld.
- **Characters:** —
- **Environment:** cave_tunnel
- **Build (lib_cave):** Sign close-up; `text()` on the sign plane (generic font, no agency name or logo).
- **Lighting:** Torch cone; one flicker.
- **FX:** silt, flicker
- **On-screen text / overlays:** [label] REPORTED
- **SFX:** sting@0.0s(g0.4), breath@1.0s(g0.5)
- **Music:** Hold (curve 0.8).
- **Transition in:** cut
- **Narration (L08):** "It reads: Stop. Prevent your death. Go no farther."

## S09 · 34.7–39.1 s (4.5 s) · timeline

- **Visual:** Pattern interrupt. Timeline card over the dark pond surface: 1981 (first deaths counted), 1999 CLOSED.
- **Camera:** Overlay; background slow drift over the pond at dusk.
- **Characters:** —
- **Environment:** timeline
- **Build (lib_cave):** 2D overlay; background = S01 set at dusk, top-down.
- **Lighting:** Graphic.
- **FX:** —
- **On-screen text / overlays:** [timeline] 1981 deaths counted from / 1999 CLOSED
- **SFX:** click@0.3s(g0.4), hit@1.8s(g0.4)
- **Music:** Pulse (curve 0.6).
- **Transition in:** whip
- **Narration (L09):** "In 1999, partly over safety fears, it was closed to divers."

## S10 · 39.1–42.6 s (3.5 s) · timeline

- **Visual:** Timeline extends: 2003 REOPENED. Behind it, the pond at dawn with a dive line again tied to the root.
- **Camera:** Overlay; background slow push.
- **Characters:** —
- **Environment:** timeline
- **Build (lib_cave):** 2D overlay; background = S02 set.
- **Lighting:** Graphic; dawn background.
- **FX:** —
- **On-screen text / overlays:** [timeline] 1981 deaths counted from / 1999 CLOSED / 2003 REOPENED
- **SFX:** click@1.2s(g0.4)
- **Music:** Pause (curve 0.3).
- **Transition in:** cut
- **Narration (L10):** "Cave divers pushed back. It reopened in 2003."

## S11 · 42.6–45.9 s (3.3 s) · other:florida_sinkhole_exterior

- **Visual:** Afternoon at the bank: three faceless figures in wetsuits sort tanks beside the pond; long shadows.
- **Camera:** Wide 28 mm from across the pond, slow dolly-in.
- **Characters:** figure x3 (silhouettes, wetsuits, no faces, not named)
- **Environment:** other:florida_sinkhole_exterior
- **Build (lib_cave):** Surface set; three `char_figure` silhouettes + capsule tank props.
- **Lighting:** Low afternoon sun, rim light.
- **FX:** dust, leaf_drift
- **On-screen text / overlays:** [stamp] OCTOBER 2016
- **SFX:** wind@0.0s(g0.3), metal_groan@1.0s(g0.2)
- **Music:** Tension returns (curve 0.6).
- **Transition in:** fade_black
- **Narration (L11):** "October 2016. Three friends came to dive it."

## S12 · 45.9–50.0 s (4.1 s) · other:vertical_shaft_descent

- **Visual:** Under the pond: one diver hovers in the green light near the top of the Chimney; below him two torches shrink down the shaft into black.
- **Camera:** Top-down 24 mm from above the hovering diver, looking past his fins at the two lights going down.
- **Characters:** diver_C (green fins, stays shallow), diver_A (blue fins), diver_B (red fins)
- **Environment:** other:vertical_shaft_descent
- **Build (lib_cave):** S03 chimney set; three `diver()`s.
- **Lighting:** Green daylight top, two torch cones below.
- **FX:** particles_dust, bubbles
- **On-screen text / overlays:** —
- **SFX:** underwater_amb@0.0s(g0.5), bubbles@0.5s(g0.4)
- **Music:** Pulse (curve 0.8).
- **Transition in:** cut
- **Narration (L12):** "One stayed near the surface. Two experienced divers went deep."

## S13 · 50.0–54.5 s (4.5 s) · other:florida_sinkhole_exterior

- **Visual:** The pond surface from the bank, perfectly still; a trail of bubbles slows and stops. The timer turns red past 60 minutes. Light fades toward evening.
- **Camera:** Locked-off 35 mm, low over the water; light timelapse.
- **Characters:** —
- **Environment:** other:florida_sinkhole_exterior
- **Build (lib_cave):** Surface set; `bubbles_stream` keyed off; `sun` energy keyed down.
- **Lighting:** Afternoon to dusk transition.
- **FX:** bubbles, mist
- **On-screen text / overlays:** [timer] DUE BACK 2700→4200 (mmss)
- **SFX:** bubbles@0.0s(g0.3), heartbeat@1.0s(g0.5)
- **Music:** Silence beat #1 (curve 0.2).
- **Transition in:** cut
- **Narration (L13):** "They were due back within an hour. They never surfaced."

## S14 · 54.5–59.0 s (4.5 s) · other:cross_section_2.5D

- **Visual:** Section again: the cyan route line runs to a deep tunnel; two small dim grey dots sit close together at a marker. No bodies, no detail.
- **Camera:** Locked; slow push toward the marker.
- **Characters:** two dim dots (abstract)
- **Environment:** other:cross_section_2.5D
- **Build (lib_cave):** S06 `xsection()` reuse with a different camera; two `glow_dot()` keyed dim.
- **Lighting:** Graphic; the dots glow faintly then dim.
- **FX:** —
- **On-screen text / overlays:** [depth] 0 → 260 FT; [label] REPORTED
- **SFX:** sonar@0.0s(g0.4)
- **Music:** Low pad (curve 0.5).
- **Transition in:** cut
- **Narration (L14):** "Recovery divers found them the next morning, around 260 feet down."

## S15 · 59.0–62.3 s (3.3 s) · cave_tunnel

- **Visual:** A deep, empty tunnel: a guideline running into black, silt hanging in a single torch beam that sweeps and finds nothing.
- **Camera:** Slow push 35 mm down the line.
- **Characters:** —
- **Environment:** cave_tunnel
- **Build (lib_cave):** `tunnel()` + `line()`; torch from camera.
- **Lighting:** Single torch; deep blue-black.
- **FX:** silt, torch_cone
- **On-screen text / overlays:** [text] CAUSE: UNCLEAR
- **SFX:** underwater_amb@0.0s(g0.4), rumble@1.0s(g0.3)
- **Music:** Silence beat #2 (curve 0.3).
- **Transition in:** cut
- **Narration (L15):** "Exactly what went wrong is still unclear."

## S16 · 62.3–66.3 s (4.0 s) · other:florida_sinkhole_exterior

- **Visual:** Camera rises out of the water back to the top-down drone view of the calm green pond — same framing as S01 so the loop into 'This pond has killed at least ten divers' is seamless. Small memorial text fades in and out.
- **Camera:** Crane up through the surface to top-down 28 mm; final 0.5 s = S01 first-frame composition.
- **Characters:** —
- **Environment:** other:florida_sinkhole_exterior
- **Build (lib_cave):** S01 set and camera (shared keyframes for the loop).
- **Lighting:** Morning sun (matches S01).
- **FX:** mist
- **On-screen text / overlays:** [text] IN MEMORY OF EVERY DIVER · LOST AT EAGLE'S NEST
- **SFX:** wind@0.0s(g0.3)
- **Music:** Resolve (curve 0.4).
- **Transition in:** cut
- **Narration (L16):** "And from above, it still looks like a pond."

## Retention map

- 0–1.5 s: death toll over an ordinary-looking pond, camera already descending; counter 0 → 10.
- ~7–16 s: surface-to-chamber reveal (the shot the concept is built on).
- ~16 s: map pattern-interrupt; ~21 s: cross-section depth bar to 300 ft.
- ~26–35 s: the Grim Reaper sign = MID-POINT TURN; on-screen text reads the sign; silence beat after it.
- ~35–43 s: timeline pattern-interrupt (1981 / 1999 / 2003).
- ~43 s: October 2016 act; ~50 s: timer goes red, silence beat #1.
- ~59 s: 'still unclear' (silence beat #2), then loop line back to the pond (final frame = S01).
