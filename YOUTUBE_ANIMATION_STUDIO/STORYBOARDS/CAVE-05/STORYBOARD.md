# CAVE-05 — Storyboard (Air for One Diver. There Were Two.)

Vertical 9:16, 1080x1920, 24 fps. 17 shots, est. 65.8 s. Captions: burned-in word-synced, 1–4 words per chunk, centre-upper safe zone, cyan accent on `emphasis` words. Keep overlays out of bottom 20% / right 15% (Shorts UI).
Shot times are estimates from narration timing; the pipeline derives real durations from TTS.

**Build notes.** Three recurring sets keep the render budget low: (1) flooded passage = `tunnel()` along a gently curving path, `rock_mat`, `silt_mat` floor, `water()` volume tinted brown-green (murky, density 0.08–0.12), `line()` guideline; (2) air bell (see S02); (3) 2.5D cross-section = `xsection()` + `glow_dot()` + `dotted_path()`. Divers: `diver()` Gràcia = yellow fins, Mascaró = orange fins, rescuers = white fins; all faceless, masked. Sa Piqueta is a sump-and-air-bell cave; no real survey map is reproduced, the section is schematic and labelled as such.

## S01 · 0.0–4.1 s (4.1 s) · cave_tunnel

- **Visual:** COLD OPEN, frame 1 already moving. Murky flooded passage, brown-green water. Two divers hang face to face over a silt floor, torch cones crossing. Between them a cut guideline end drifts slack. One diver taps his pressure gauge (gauge face reads generic low, no number).
- **Camera:** Slow push-in 35 mm at mid-water between the two divers, handheld drift (amp 0.02); rack from gauge to the slack line.
- **Characters:** diver_A Gràcia (yellow fins, back-mounted twins, helmet torch), diver_B Mascaró (orange fins, helmet torch)
- **Environment:** cave_tunnel
- **Build (lib_cave):** `tunnel()` radius 2.2 m + `water(color brown-green, density 0.1)` + `line()` cut end animated with `drift()`; two `diver()`.
- **Lighting:** Two warm-white torch spots (22 deg) cutting a dense brown volume; no ambient.
- **FX:** silt, volumetric_water, torch_cone
- **On-screen text / overlays:** [label] REPORTED; [text] AIR FOR 1
- **SFX:** underwater_amb@0.0s(g0.5), breath@0.15s(g0.6), sting@1.6s(g0.5)
- **Music:** Low drone enters at 0.0 (curve 0.5).
- **Transition in:** cut
- **Narration (L01):** "Air for one diver to get out. There were two."

## S02 · 4.1–7.1 s (3.0 s) · other:air_bell_chamber

- **Visual:** A head and helmet torch break the black water surface inside a low rock dome. Ripples spread; drips fall from the ceiling; breath vapour in the torch beam. Nothing else: rock, water, one light.
- **Camera:** Water-level 28 mm, lens half an inch above the surface, slow pull-back revealing how small the dome is.
- **Characters:** diver_A Gràcia (yellow fins, masked, faceless)
- **Environment:** other:air_bell_chamber
- **Build (lib_cave):** Air-bell kit: `shaft()` with cap (low rock dome ~4 m wide, ~2.5 m headroom) + `floor(ripples=True)` as the black water surface + `rocks()` ledge + `cloud()` drips/vapour; `diver(rebreather=False)` with back-mounted twin cylinders, upper body only above the waterline; `world_black()`.
- **Lighting:** Helmet torch only; warm bounce off wet rock; everything outside the dome black.
- **FX:** ripples, drips, breath_vapour
- **On-screen text / overlays:** —
- **SFX:** bubbles@0.0s(g0.5), breath@0.4s(g0.6), creak@1.6s(g0.2)
- **Music:** Drone holds.
- **Transition in:** cut
- **Narration (L02):** "So one stayed behind, inside the rock."

## S03 · 7.1–10.8 s (3.7 s) · map

- **Visual:** Pattern interrupt. Stylised map card of Mallorca (land blob on grid). Route line draws from Palma to the east side; pin drops near Manacor.
- **Camera:** Overlay card over a dark, slow-drifting silt background; card scales 0.95 → 1.0.
- **Characters:** —
- **Environment:** map
- **Build (lib_cave):** 2D overlay only (`map` + `stamp`); background = reuse S01 passage render, defocused.
- **Lighting:** Graphic.
- **FX:** —
- **On-screen text / overlays:** [map] SA PIQUETA · NEAR MANACOR, MALLORCA; [stamp] 15 APRIL 2017
- **SFX:** whoosh@0.0s(g0.5), click@2.2s(g0.4)
- **Music:** Pulse added (curve 0.6).
- **Transition in:** whip
- **Narration (L03):** "Mallorca, Spain. April 2017. The cave of Sa Piqueta."

## S04 · 10.8–14.1 s (3.3 s) · cave_tunnel

- **Visual:** Rewind. Clearer teal water: the two divers swim side by side along a white survey line; one writes on a slate, the other reels line. Name cards pop beside each diver.
- **Camera:** Side-tracking 28 mm alongside the divers, slow.
- **Characters:** diver_A Gràcia (yellow fins, slate), diver_B Mascaró (orange fins, reel)
- **Environment:** cave_tunnel
- **Build (lib_cave):** S01 tunnel set with `water(density 0.04, teal)`; `line()` survey line; slate = thin box prop.
- **Lighting:** Two torch cones in clearer water; faint cyan ambient.
- **FX:** particles_dust, torch_cone
- **On-screen text / overlays:** [stamp] SURVEY DIVE; [text] XISCO GRÀCIA; [text] GUILLEM MASCARÓ
- **SFX:** underwater_amb@0.0s(g0.4), breath@0.5s(g0.4)
- **Music:** Pulse (curve 0.6).
- **Transition in:** cut
- **Narration (L04):** "Xisco Gràcia and Guillem Mascaró were mapping it."

## S05 · 14.1–17.1 s (3.0 s) · cave_tunnel

- **Visual:** The line snaps at a sharp rock edge; the loose end whips away into a rising silt cloud and the water turns brown. Cut-in: a generic pressure gauge needle sinks toward the red.
- **Camera:** Quick push onto the snapping line (35 mm), then insert 50 mm on the gauge.
- **Characters:** diver_A Gràcia (hands, gauge)
- **Environment:** cave_tunnel
- **Build (lib_cave):** S01 set, `water()` density keyed 0.04 → 0.12 with `key_input`; line split into two `curve()` halves, one animated away; gauge = disc + needle props.
- **Lighting:** Torch cones fragmenting in silt; water goes teal → brown.
- **FX:** silt_cloud, torch_cone
- **On-screen text / overlays:** [label] DOCUMENTED FACT
- **SFX:** hit@0.0s(g0.5), rumble@0.2s(g0.4), click@1.4s(g0.4)
- **Music:** Pulse rises (curve 0.65).
- **Transition in:** cut
- **Narration (L05):** "Their guideline broke. Their gas ran low."

## S06 · 17.1–22.0 s (4.9 s) · cave_tunnel

- **Visual:** Close two-shot: yellow-fin diver unclips a cylinder and pushes it into the orange-fin diver's hands. The orange-fin diver turns and swims away; his torch shrinks into the brown water until it is a dot, then gone.
- **Camera:** Tight 40 mm over Gràcia's shoulder; hold as the other torch recedes (focus stays on the receding light).
- **Characters:** diver_A Gràcia (yellow fins), diver_B Mascaró (orange fins, receding)
- **Environment:** cave_tunnel
- **Build (lib_cave):** S01 set; cylinder = simple capsule prop parented then re-parented to diver_B; `move_along()` for exit.
- **Lighting:** Gràcia's torch on the handover; the receding torch is the only other light.
- **FX:** silt, torch_cone
- **On-screen text / overlays:** —
- **SFX:** breath@0.0s(g0.6), click@0.8s(g0.4), bubbles@1.5s(g0.4)
- **Music:** Pulse thins (curve 0.65).
- **Transition in:** cut
- **Narration (L06):** "Gràcia gave his partner his remaining gas and sent him for help."

## S07 · 22.0–26.8 s (4.9 s) · other:cross_section_2.5D

- **Visual:** Schematic side-section: entrance pool at left, a long flooded passage, a small dome of air far right. Orange dot travels left toward the entrance; cyan dot rises into the dome and stops. A dotted ruler along the passage counts the distance.
- **Camera:** Locked diagram; slow pan right-to-left following the orange dot, then snap back to the cyan dot.
- **Characters:** diver_dot Gràcia (cyan), diver_dot Mascaró (orange)
- **Environment:** other:cross_section_2.5D
- **Build (lib_cave):** `xsection()` with a hand-drawn poly; `glow_dot()` ×2; `dotted_path()` ruler; `move_along()` for the orange dot.
- **Lighting:** Graphic; black background, cyan rock outline, air dome filled pale grey.
- **FX:** —
- **On-screen text / overlays:** [text] ~900 M FROM · THE ENTRANCE; [label] DOCUMENTED FACT; [text] SCHEMATIC, NOT TO SCALE
- **SFX:** sonar@0.0s(g0.4), click@1.6s(g0.4)
- **Music:** Pulse (curve 0.7).
- **Transition in:** whip
- **Narration (L07):** "Then he waited alone in an air pocket, about 900 metres in."

## S08 · 26.8–31.8 s (4.9 s) · other:air_bell_chamber

- **Visual:** Gràcia sits on a rock ledge at the water's edge, helmet torch dimmed to a faint glow. He cups water to his mouth. The air in the beam is hazy and slow; then the torch clicks off and the frame drops to near-black (≤1 s), only drips audible.
- **Camera:** Medium 35 mm from across the water, slow push; hold through the blackout.
- **Characters:** diver_A Gràcia (seated, mask pushed up, faceless silhouette)
- **Environment:** other:air_bell_chamber
- **Build (lib_cave):** Air-bell kit: `shaft()` with cap (low rock dome ~4 m wide, ~2.5 m headroom) + `floor(ripples=True)` as the black water surface + `rocks()` ledge + `cloud()` drips/vapour; `diver(rebreather=False)` with back-mounted twin cylinders, upper body only above the waterline; `world_black()`. `pose_upright_kneel()` for the seated pose; `key_energy()` on the helmet light.
- **Lighting:** Dim torch (energy keyed 1500 → 200 → 0); faint cyan rim on wet rock so the frame is never pure black for > 1 s.
- **FX:** haze, drips, breath_vapour
- **On-screen text / overlays:** [text] CO₂ ↑; [label] DOCUMENTED FACT
- **SFX:** breath@0.0s(g0.5), click@2.4s(g0.5), breath@2.8s(g0.7)
- **Music:** Drone drops to a single low note (curve 0.75).
- **Transition in:** cut
- **Narration (L08):** "Fresh water to drink. Almost no light. Air thick with carbon dioxide."

## S09 · 31.8–36.7 s (4.9 s) · other:air_bell_chamber

- **Visual:** MID-POINT TURN. Near-black dome. Every second, the torch clicks on for a beat, sweeps the empty water where his partner left, and clicks off. The water stays flat. No light comes.
- **Camera:** POV from the ledge, 24 mm, static between flashes; tiny drift.
- **Characters:** —
- **Environment:** other:air_bell_chamber
- **Build (lib_cave):** Air-bell set; `flicker()` on helmet light with fixed pattern; floor ripples off (mirror-flat water).
- **Lighting:** Strobe-like torch flashes (on 0.4 s / off 0.6 s) — no faster than 2 Hz (photosensitivity).
- **FX:** flicker, drips
- **On-screen text / overlays:** [timer] HOURS UNDERGROUND 6→30 (hours)
- **SFX:** heartbeat@0.0s(g0.5), click@0.4s(g0.3), click@1.4s(g0.3), click@2.4s(g0.3)
- **Music:** Drone swells (curve 0.85).
- **Transition in:** cut
- **Narration (L09):** "Hours went by. He began to believe his partner hadn't made it."

## S10 · 36.7–41.5 s (4.9 s) · other:surface_drill_site + cross_section_2.5D

- **Visual:** Night on the dry scrub above the cave: a simple drill tower prop with two work lights and a generator. Camera tilts down through the ground into a schematic cut-away: the drill bore descends, stops short; the air dome sits below it, unreached.
- **Camera:** 28 mm crane down from the rig, transition through the ground plane into the 2.5D section (match on the bore line).
- **Characters:** figure x2 (faceless silhouettes, hard hats)
- **Environment:** other:surface_drill_site + cross_section_2.5D
- **Build (lib_cave):** `ground()` + `bushes()` + drill tower = 4 cylinders + box; `sky_world()` night; then `xsection()` bore line.
- **Lighting:** Sodium-orange work lights, blue night sky; section is graphic.
- **FX:** dust, particles
- **On-screen text / overlays:** [label] DOCUMENTED FACT; [text] DRILL: FAILED
- **SFX:** rumble@0.0s(g0.6), metal_groan@1.0s(g0.4), hit@2.6s(g0.5)
- **Music:** Pulse returns (curve 0.9).
- **Transition in:** cut
- **Narration (L10):** "Above him, rescuers tried to drill down through the rock. It failed."

## S11 · 41.5–45.7 s (4.1 s) · cave_tunnel

- **Visual:** Two rescue divers (white fins) enter the passage; their torches stop dead a metre ahead in brown water. One holds a hand up to his mask; the hand vanishes in the murk.
- **Camera:** From behind the rescuers, 24 mm; slow push that gains nothing (the frame stays brown).
- **Characters:** rescuer_1 (white fins, twin tanks), rescuer_2 (white fins)
- **Environment:** cave_tunnel
- **Build (lib_cave):** S01 tunnel, `water(density 0.25, brown)`; two `diver()` with white fins.
- **Lighting:** Torch cones that turn into a flat brown glow.
- **FX:** volumetric_water_dense, silt
- **On-screen text / overlays:** [text] VISIBILITY: ~0
- **SFX:** underwater_amb@0.0s(g0.5), breath@0.3s(g0.5)
- **Music:** Peak tension (curve 0.9), then cut to 0.25.
- **Transition in:** cut
- **Narration (L11):** "Divers tried to swim in. The water was too murky."

## S12 · 45.7–48.6 s (2.9 s) · other:air_bell_chamber

- **Visual:** Inside the dome, the rock walls seem to breathe (slow scale wobble); faint soft glows pulse under the water and fade before they resolve. Abstract, no figures.
- **Camera:** Slow 360-deg rotation from the centre of the dome, 20 mm, slight lens breathing.
- **Characters:** —
- **Environment:** other:air_bell_chamber
- **Build (lib_cave):** Air-bell set; `glow_dot()` ×3 below the surface with `key_energy` pulses; wall object `key_scale` ±2%.
- **Lighting:** Low cyan glows under the surface pulsing (slow, ≤1 Hz) then dying.
- **FX:** warp, glow_pulse
- **On-screen text / overlays:** [label] DRAMATISATION; [timer] HOURS UNDERGROUND 30→45 (hours)
- **SFX:** static@0.0s(g0.25), riser@0.5s(g0.3)
- **Music:** Silence beat #1 (curve 0.25).
- **Transition in:** flash
- **Narration (L12):** "The bad air made him hallucinate."

## S13 · 48.6–52.9 s (4.3 s) · other:air_bell_chamber

- **Visual:** From the ledge: under the black water, a single white glow grows, sharpening into a torch beam pointed up. Ripples lit from below.
- **Camera:** Low 35 mm aimed at the water, slow push-in; the glow fills the lower third.
- **Characters:** —
- **Environment:** other:air_bell_chamber
- **Build (lib_cave):** Air-bell set; spot light under `floor()` water plane with `key_loc` rising; `caustics_light`.
- **Lighting:** One underwater spot (rescuer torch) rising; caustic ripples on the dome ceiling.
- **FX:** caustics, ripples
- **On-screen text / overlays:** [timer] HOURS UNDERGROUND 45→60 (hours)
- **SFX:** bubbles@0.4s(g0.5), riser@0.6s(g0.6)
- **Music:** Build (curve 0.5 → 0.9).
- **Transition in:** cut
- **Narration (L13):** "Then, around hour 60, a light rose through the water."

## S14 · 52.9–54.5 s (1.6 s) · other:air_bell_chamber

- **Visual:** A rescuer's helmet and torch break the surface: same composition as S02 (head at the waterline, ripples), but now the torch faces Gràcia on the ledge.
- **Camera:** Mirror of S02 framing, 28 mm water-level, quick push.
- **Characters:** rescuer_1 (white fins, masked, faceless)
- **Environment:** other:air_bell_chamber
- **Build (lib_cave):** Air-bell kit: `shaft()` with cap (low rock dome ~4 m wide, ~2.5 m headroom) + `floor(ripples=True)` as the black water surface + `rocks()` ledge + `cloud()` drips/vapour; `diver(rebreather=False)` with back-mounted twin cylinders, upper body only above the waterline; `world_black()`.
- **Lighting:** Two torches now; the dome is lit for the first time.
- **FX:** ripples, bubbles, drips
- **On-screen text / overlays:** —
- **SFX:** bubbles@0.0s(g0.7), sting@0.1s(g0.5)
- **Music:** Silence beat #2, then hit (curve 1.0).
- **Transition in:** flash
- **Narration (L14):** "It was real."

## S15 · 54.5–57.1 s (2.6 s) · other:air_bell_chamber

- **Visual:** Wide: two rescuers in the water beside the ledge, one passing a regulator up to Gràcia. All three torches up; the dome finally visible: wet rock, a tiny ledge, the flat lake.
- **Camera:** Wide 20 mm from the far side of the dome, slow crane up.
- **Characters:** diver_A Gràcia (yellow fins), rescuer_1, rescuer_2
- **Environment:** other:air_bell_chamber
- **Build (lib_cave):** Air-bell kit: `shaft()` with cap (low rock dome ~4 m wide, ~2.5 m headroom) + `floor(ripples=True)` as the black water surface + `rocks()` ledge + `cloud()` drips/vapour; `diver(rebreather=False)` with back-mounted twin cylinders, upper body only above the waterline; `world_black()`. Three `diver()`s.
- **Lighting:** Three torch cones; warm bounce.
- **FX:** ripples, breath_vapour
- **On-screen text / overlays:** [stamp] 17 APRIL 2017 · FOUND ALIVE; [label] DOCUMENTED FACT
- **SFX:** breath@0.0s(g0.5), bubbles@0.8s(g0.4)
- **Music:** Warm pad (curve 1.0 → 0.8).
- **Transition in:** cut
- **Narration (L15):** "Rescue divers had found him. Alive."

## S16 · 57.1–61.3 s (4.2 s) · other:surface_entrance_night

- **Visual:** Reveal. Night at the cave entrance on the surface: emergency vehicle lights (generic blue/amber, no markings) on rock and scrub; a lone figure in a wetsuit (orange fin in hand) stands at the entrance watching the water.
- **Camera:** Low 28 mm from behind the figure, slow dolly-in.
- **Characters:** figure Mascaró (silhouette, wetsuit, orange fin in hand), figures x3 (rescue team silhouettes)
- **Environment:** other:surface_entrance_night
- **Build (lib_cave):** `ground()` + `rocks()` + small pool; `char_figure` silhouettes; point lights keyed for beacons.
- **Lighting:** Blue/amber rotating lights (slow, ≤2 Hz), night sky.
- **FX:** dust
- **On-screen text / overlays:** [label] DOCUMENTED FACT
- **SFX:** wind@0.0s(g0.4), footsteps@0.8s(g0.3)
- **Music:** Pad (curve 0.7).
- **Transition in:** cut
- **Narration (L16):** "His partner had made it out, and raised the alarm."

## S17 · 61.3–65.8 s (4.4 s) · other:air_bell_chamber

- **Visual:** The empty air bell: still water, the ledge, drips, lit by a single torch beam from below the surface. Last 0.5 s matches the S01/S02 framing so the loop back to 'Air for one diver…' is seamless.
- **Camera:** Slow pull-back 28 mm at water level; final frame = S02 composition.
- **Characters:** —
- **Environment:** other:air_bell_chamber
- **Build (lib_cave):** Air-bell kit: `shaft()` with cap (low rock dome ~4 m wide, ~2.5 m headroom) + `floor(ripples=True)` as the black water surface + `rocks()` ledge + `cloud()` drips/vapour; `diver(rebreather=False)` with back-mounted twin cylinders, upper body only above the waterline; `world_black()`.
- **Lighting:** Single torch from below; ripples.
- **FX:** ripples, drips
- **On-screen text / overlays:** —
- **SFX:** underwater_amb@0.0s(g0.3), bubbles@1.8s(g0.4)
- **Music:** Resolve to drone (curve 0.4).
- **Transition in:** cut
- **Narration (L17):** "Air for one diver to get out. Both came home."

## Retention map

- 0–1.5 s: stake line ('Air for one diver') over moving silt + two torches; 'AIR FOR 1' text at ~1.6 s.
- ~5 s: the air-bell surfacing shot (thumbnail frame).
- ~8 s: map pattern-interrupt (Mallorca); ~18 s: guideline snaps.
- ~23 s: cross-section reveals the distance (diver dots split).
- ~28–37 s: near-black light-ration beat (≤1 s of black, torch click); hours counter starts; MID-POINT TURN at ~33 s (he believes his partner is dead).
- ~37–46 s: two failed rescue attempts (drill, murky water) — new info every ~4 s.
- ~46 s: hallucination (DRAMATISATION label), silence beat #1; ~53 s: the light that is real, flash cut, silence beat #2.
- Final 9 s: partner reveal (pays off the mid-point), then loop line into L01; last frame matches S02 composition.
