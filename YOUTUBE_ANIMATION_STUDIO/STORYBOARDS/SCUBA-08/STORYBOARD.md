# SCUBA-08 — Storyboard (Shackleton's Ship Was Found a Century Later, 3 km Down)

Vertical 9:16, 1080x1920, 24 fps. 14 shots, measured 50.7 s. Mood `scuba`. Captions: burned-in, word-synced, centred at y≈1240 (keep all text overlays out of y 1150–1400), accent words = `emphasis`. Overlays avoid the bottom 20% and right 15% (Shorts UI). Shot times come from a scratch TTS measurement; the pipeline derives the real durations from its own render.

**Build notes.** Sets: (1) the deep wreck = lib_murder `brigantine()` re-rigged as a three-masted barquentine (masts broken for the wreck), dark silt-dusted `mat_hull()`, gold `text3d('ENDURANCE')` arced across the counter stern with an extruded five-point star beneath (both are on the real stern: E4, E5); studio_lib `seabed()`; lib_scuba `world_volume()` near-black; two drone lamps + lib_scuba `beam_cone()`; `particle_cloud()` marine snow; (2) 1915 pack ice = the same ship upright and rigged, lib_cave `ice_sheet()` slabs and noise-displaced pressure-ridge chunks, lib_murder `dawn_sky()`, `snowfall()`; crew = lib_murder `hiker()` silhouettes (tiny, faceless) and three `lifeboat()` hulls on the floe; (3) 2019 under-ice = lib_cave `ice_sheet()` seen from below + yellow torpedo robot (new simple prop); (4) 2022 icebreaker = lib_scuba `dsv()` re-dressed (red hull, white block) in broken sea ice; (5) drone = new simple prop (yellow rounded box body, four thruster pods, two lamps); (6) maps/timeline/cards via overlays. Metres for depth (sources give 3,008 m); miles for the offset (sources give "about four miles").

## S01 · 0.0–4.0 s (4.0 s) · other:deep_wreck_stern

- **Visual:** COLD OPEN, moving at frame 1. Pitch-black water three kilometres down. Two hard drone lamps sweep from the left across the curved wooden stern of a sailing ship: gold capital letters reading ENDURANCE arc across it, a five-pointed star beneath them. Pale sea anemones dot the planks; marine snow drifts through the beams.
- **Camera:** 35 mm, slow lateral slide + push toward the letters, as if from a hovering underwater drone
- **Characters:** —
- **Environment:** other:deep_wreck_stern
- **Build (lib_scuba (+ lib_murder ship, lib_cave ice)):** Ship = lib_murder `brigantine(sails='none')` re-rigged as a three-masted barquentine (third mast added, masts broken off for the wreck), `mat_hull()` darkened and silt-dusted; name = `text3d('ENDURANCE')` on a curve following the counter stern, gold metallic material; star = extruded five-point polygon below it; anemones = small instanced cones/blobs; seabed = studio_lib `seabed()` dark grey; `world_volume(color=(0.02,0.05,0.08), density=0.05)`; lamps = 2 spots + lib_scuba `beam_cone()`; `particle_cloud()` marine snow.
- **Lighting:** two cool-white drone lamps only (beams visible in the water); everything else black
- **FX:** marine snow, volumetric_water
- **On-screen text / overlays:** [text] SANK 1915 (y=380)
- **SFX:** underwater_amb@0.0s(g0.5), sonar@0.3s(g0.3), sting@1.6s(g0.4)
- **Music:** Low pulse enters (0.45).
- **Transition in:** cut
- **Narration (L01):** "This ship sank in 1915. You can still read its name."

## S02 · 4.0–8.2 s (4.2 s) · map

- **Visual:** Map card over a slow drift along the dark hull (S01 set, defocused): the Antarctic coast and peninsula, a route line running south into the Weddell Sea, a pin dropping on the wreck site.
- **Camera:** 2.5D map card; background drifts
- **Characters:** —
- **Environment:** map
- **Build (lib_scuba (+ lib_murder ship, lib_cave ice)):** S01 set at a wider angle, rendered soft behind the overlay.
- **Lighting:** background drone lamps; map card self-lit
- **FX:** —
- **On-screen text / overlays:** [map] WEDDELL SEA
- **SFX:** whoosh@0.0s(g0.35), click@1.6s(g0.3)
- **Music:** Pulse lifts (0.55).
- **Transition in:** whip
- **Narration (L02):** "It's Ernest Shackleton's Endurance, three kilometres under the Weddell Sea."

## S03 · 8.2–10.7 s (2.5 s) · other:pack_ice_1915

- **Visual:** 1915. A three-masted wooden ship sits locked in a white plain of pack ice under a low, pale sun. Pressure ridges heave up against the hull; the hull lists and timbers bend; a yard snaps and swings.
- **Camera:** 50 mm, slow push from the ice toward the straining hull; slight shake on the snap
- **Characters:** —
- **Environment:** other:pack_ice_1915
- **Build (lib_scuba (+ lib_murder ship, lib_cave ice)):** Same ship model, upright and rigged; pack ice = lib_cave `ice_sheet()` slabs + noise-displaced box chunks keyed with `key_loc()` pressing on the hull; hull list via rotation keys; lib_murder `dawn_sky()` (pale) + sun; lib_murder `snowfall()` light.
- **Lighting:** low pale sun, long blue shadows, cold sky
- **FX:** drifting snow, ice chips
- **On-screen text / overlays:** [stamp] WEDDELL SEA / 1915 (y=300)
- **SFX:** wind@0.0s(g0.35), creak@0.4s(g0.45), metal_groan@1.2s(g0.35), hit@2.0s(g0.35)
- **Music:** Tension (0.6).
- **Transition in:** cut
- **Narration (L03):** "Pack ice trapped it for months, then crushed it."

## S04 · 10.7–13.6 s (3.0 s) · other:pack_ice_1915

- **Visual:** Dusk on the ice. In the foreground, a long line of tiny faceless figures and three small wooden boats on the floe watch from a distance as, far behind them, the ship's stern tilts up and slides down through a gap in the ice.
- **Camera:** 35 mm wide, locked, slow push
- **Characters:** crew x28 (tiny faceless silhouettes, generic)
- **Environment:** other:pack_ice_1915
- **Build (lib_scuba (+ lib_murder ship, lib_cave ice)):** lib_murder `hiker()` silhouettes x28 (instanced, 1.75 m, dark coats); three lib_murder `lifeboat(people=0)` hulls on the ice; ship from S03 keyed sinking (rotation + z) into a gap cut with lib_cave `ice_sheet(hole=...)`; `dawn_sky()`.
- **Lighting:** dim pink-grey dusk, flat light, ship silhouetted
- **FX:** blowing snow
- **On-screen text / overlays:** [counter] MEN WHO SURVIVED 0→28 (y=330); [label] DOCUMENTED FACT (y=200)
- **SFX:** metal_groan@0.2s(g0.3), wind@0.0s(g0.3)
- **Music:** Swells, then settles (0.5).
- **Transition in:** cut
- **Narration (L04):** "It sank, but all 28 men on board survived."

## S05 · 13.6–16.4 s (2.8 s) · timeline

- **Visual:** Pattern interrupt: a timeline draws across dark water: 1915 'sank' on the left, a long empty stretch, 2022 'found' on the right, highlighted.
- **Camera:** 2.5D graphic, slow push
- **Characters:** —
- **Environment:** timeline
- **Build (lib_scuba (+ lib_murder ship, lib_cave ice)):** Overlay over a dark `world_volume()` backdrop with slow marine snow (S01 set, no ship in frame).
- **Lighting:** graphic
- **FX:** —
- **On-screen text / overlays:** [timeline] OVER A CENTURY: 1915 → 2022 (y=900)
- **SFX:** whoosh@0.1s(g0.35)
- **Music:** Thins (0.45).
- **Transition in:** whip
- **Narration (L05):** "The ship wasn't seen again for over a century."

## S06 · 16.4–20.9 s (4.4 s) · other:under_sea_ice

- **Visual:** 2019, under the sea ice, seen from below: a long yellow torpedo-shaped robot glides away beneath the milky-white underside of the ice; its single lamp shrinks into the blue-black and does not come back.
- **Camera:** 28 mm, low angle looking up at the ice ceiling, locked; robot exits frame
- **Characters:** —
- **Environment:** other:under_sea_ice
- **Build (lib_scuba (+ lib_murder ship, lib_cave ice)):** lib_cave `ice_sheet(z=0, size=40)` seen from below (milky underside); robot = cylinder body (3.5 m, yellow) + cone nose + cross tail fins + one spot lamp, `key_loc()` away; lib_scuba `world_volume(color=(0.05,0.2,0.35))`.
- **Lighting:** faint blue light filtering through the ice; robot lamp
- **FX:** particles, volumetric_water
- **On-screen text / overlays:** [stamp] 2019 (y=300)
- **SFX:** underwater_amb@0.0s(g0.4), sonar@0.4s(g0.3), static@2.0s(g0.3)
- **Music:** Low (0.45).
- **Transition in:** cut
- **Narration (L06):** "A 2019 search lost its underwater robot and was called off."

## S07 · 20.9–25.4 s (4.5 s) · other:icebreaker_sea_ice

- **Visual:** 2022, aerial: a red-hulled icebreaker with a white superstructure grinds slowly through broken white sea ice under a heavy overcast sky, leaving a dark lane of open water behind it.
- **Camera:** high 35 mm drone, slow tracking alongside and ahead of the bow
- **Characters:** —
- **Environment:** other:icebreaker_sea_ice
- **Build (lib_scuba (+ lib_murder ship, lib_cave ice)):** lib_scuba `dsv(length=134, hull=(0.55,0.06,0.05), house=(0.9,0.9,0.88), floods=False)` re-dressed as an icebreaker (red hull, white accommodation block, no dive tower); sea ice = lib_cave `ice_sheet()` tiles broken into floes + dark water lane (lib_scuba `ocean()` calm); lib_scuba `sky_gradient()` grey.
- **Lighting:** flat overcast polar light
- **FX:** ice floes, light snow
- **On-screen text / overlays:** [stamp] 2022 / ENDURANCE22 EXPEDITION (y=300)
- **SFX:** wind@0.0s(g0.35), rumble@0.3s(g0.35), creak@1.2s(g0.3)
- **Music:** Lifts (0.55).
- **Transition in:** cut
- **Narration (L07):** "In 2022, a new expedition went back, aboard an icebreaker."

## S08 · 25.4–29.3 s (4.0 s) · other:deep_descent

- **Visual:** A yellow box-shaped underwater drone with four thruster pods and two lamps descends through black water; marine snow streams upward past it; its lamps point down into nothing.
- **Camera:** 35 mm, camera sinks with the drone, slight sway
- **Characters:** —
- **Environment:** other:deep_descent
- **Build (lib_scuba (+ lib_murder ship, lib_cave ice)):** New simple prop: hybrid AUV/ROV = rounded box body 3.5 x 1 x 0.6 m (yellow), four cylinder thruster pods, two spot lamps with `beam_cone()`, small sensor dome; `particle_cloud()` marine snow keyed upward; `world_volume()` near-black.
- **Lighting:** drone lamps only; faint blue fill
- **FX:** marine snow, volumetric_water, bubbles (thrusters)
- **On-screen text / overlays:** [depth] 0→3008 m
- **SFX:** underwater_amb@0.0s(g0.45), sonar@0.6s(g0.35), riser@1.0s(g0.3)
- **Music:** Tension builds (0.65), then drops for the pause.
- **Transition in:** cut
- **Narration (L08):** "Its underwater drone searched the seabed, three kilometres down."

## S09 · 29.3–31.3 s (2.0 s) · other:deep_wreck_bow

- **Visual:** MID-POINT TURN. In the drone's lamps, the black resolves into the wooden bow of a ship rising out of the seabed: planks, a rail, a broken mast stump. The lamps stop and hold on it.
- **Camera:** 35 mm drone POV, slow approach, then hold
- **Characters:** —
- **Environment:** other:deep_wreck_bow
- **Build (lib_scuba (+ lib_murder ship, lib_cave ice)):** S01 wreck from the bow; lamps parented to the camera; `scanlines(cam, strength=0.15)` for a subtle drone-feed look.
- **Lighting:** two drone lamps pooling on the hull; black beyond
- **FX:** marine snow, volumetric_water
- **On-screen text / overlays:** [stamp] 5 MARCH 2022 (y=300); [label] DOCUMENTED FACT (y=200)
- **SFX:** sonar@0.0s(g0.4), hit@0.5s(g0.4)
- **Music:** Hit on 'found' (0.75).
- **Transition in:** flash
- **Narration (L09):** "On March 5th, it found her."

## S10 · 31.3–34.8 s (3.4 s) · map

- **Visual:** Map card zoomed into the search area: a small marker for the position recorded by the ship's captain in 1915, a line drawing about four miles south, a pin on the wreck.
- **Camera:** 2.5D map card
- **Characters:** —
- **Environment:** map
- **Build (lib_scuba (+ lib_murder ship, lib_cave ice)):** Overlay over the S07 sea-ice aerial (softened).
- **Lighting:** graphic
- **FX:** —
- **On-screen text / overlays:** [map] ABOUT 4 MILES
- **SFX:** click@0.3s(g0.3), whoosh@1.2s(g0.25)
- **Music:** Pulse (0.6).
- **Transition in:** cut
- **Narration (L10):** "About four miles from the position her captain had recorded."

## S11 · 34.8–38.0 s (3.2 s) · wreck

- **Visual:** Wide reveal: the whole ship sits upright on the grey seabed, hull intact, masts broken and fallen across the deck, rigging draped; the drone lamps travel slowly along its length.
- **Camera:** 24 mm, slow orbit at mid-height, drone-lamp light travelling along the hull
- **Characters:** —
- **Environment:** wreck
- **Build (lib_scuba (+ lib_murder ship, lib_cave ice)):** S01 ship full length, upright, slight list, masts as broken cylinders on deck, `L.cam_light()` blue fill; studio_lib `seabed()`.
- **Lighting:** two moving lamps plus a faint blue fill so the silhouette reads
- **FX:** marine snow, volumetric_water
- **On-screen text / overlays:** [text] 3,008 M (y=380); [label] DOCUMENTED FACT (y=200)
- **SFX:** underwater_amb@0.0s(g0.4), riser@0.4s(g0.25)
- **Music:** Wonder (0.65).
- **Transition in:** cut
- **Narration (L11):** "Upright, intact, 3,008 metres down."

## S12 · 38.0–42.5 s (4.5 s) · other:wreck_macro

- **Visual:** Macro along the wooden rail and deck planks: the wood is whole and sharp-edged; sea anemones and small pale animals cling to it. A card slides in.
- **Camera:** 85 mm macro, slow slide along the rail
- **Characters:** —
- **Environment:** other:wreck_macro
- **Build (lib_scuba (+ lib_murder ship, lib_cave ice)):** Close set: plank boxes with wood material + bevel, rail cylinder, instanced anemone blobs (pink/white emissive-lite); lamp spot raking.
- **Lighting:** one lamp raking across the grain
- **FX:** marine snow
- **On-screen text / overlays:** [card] WHY IT SURVIVED: Experts: the wood-eaters that / wreck ships elsewhere / aren't found here (y=820)
- **SFX:** underwater_amb@0.0s(g0.35), click@0.6s(g0.2)
- **Music:** Holds (0.6).
- **Transition in:** cut
- **Narration (L12):** "Experts say the creatures that eat wooden wrecks elsewhere don't live in these waters."

## S13 · 42.5–46.2 s (3.8 s) · wreck

- **Visual:** The drone lamps slowly pull away and up; the ship sinks back into darkness, untouched. A card slides in.
- **Camera:** 35 mm, slow pull-back and rise
- **Characters:** —
- **Environment:** wreck
- **Build (lib_scuba (+ lib_murder ship, lib_cave ice)):** S11 set; camera dolly back + rise; `key_energy()` dims the lamps by distance.
- **Lighting:** lamps fading with distance; black
- **FX:** marine snow
- **On-screen text / overlays:** [card] PROTECTED: Antarctic Treaty Historic Site / and Monument No. 93 / Nothing may be removed (y=820)
- **SFX:** underwater_amb@0.0s(g0.35)
- **Music:** Fades toward a silence beat (0.1).
- **Transition in:** cut
- **Narration (L13):** "Today it's a protected monument. Nothing may be taken."

## S14 · 46.2–50.7 s (4.4 s) · other:deep_wreck_stern

- **Visual:** LOOP FRAME: back on the stern, the gold ENDURANCE letters and the star caught again in the drone lamps, ending on the S01 framing so a replay flows into 'This ship sank in 1915'.
- **Camera:** 35 mm, same slide + push as S01, ending on S01's first-frame pose
- **Characters:** —
- **Environment:** other:deep_wreck_stern
- **Build (lib_scuba (+ lib_murder ship, lib_cave ice)):** S01 set and camera path; final frame = S01 frame 1.
- **Lighting:** two drone lamps
- **FX:** marine snow, volumetric_water
- **On-screen text / overlays:** [text] FUNERAL: 5 MARCH 1922 / FOUND: 5 MARCH 2022 (y=380)
- **SFX:** sting@0.3s(g0.35), underwater_amb@0.0s(g0.4)
- **Music:** Returns to the opening level (0.45) for the loop.
- **Transition in:** cut
- **Narration (L14):** "And it was found 100 years to the day after Shackleton's funeral."

## Timing checks

- Line 1 starts at 0.15 s; "sank in 1915" lands by ~1.6 s and "read its name" by ~3.8 s, with the ENDURANCE letters lit in frame 1 and "SANK 1915" on screen. Frame 1 moves (lamps sweeping, camera sliding).
- New information every ≤4.5 s: Shackleton/Endurance/3 km (≈4.1 s) → trapped and crushed (≈8.3 s) → all 28 survived (≈10.8 s) → over a century (≈13.7 s) → 2019 failure (≈16.5 s) → 2022 icebreaker (≈21.0 s) → drone at 3 km (≈25.4 s) → **turn (≈29.4 s): found** → four miles (≈31.3 s) → upright/intact/3,008 m (≈34.8 s) → no wood-eaters (≈38.0 s) → protected (≈42.4 s) → funeral payoff (≈46.2 s).
- Pattern interrupts: deep wreck → map → 1915 ice → timeline → under-ice → aerial icebreaker → descent → wreck → map → wreck → macro → wreck.
- Silence beats: after L08 (0.5 s, before the find) and after L13 (0.6 s, before the payoff). Two max.
- Payoff in the last 8 s: L13 (protected) + L14 (100 years to the day).
- Loop: S14 ends on S01's framing of the stern letters; L14's payoff hands back to L01 "This ship sank in 1915" (a visual loop; the lines are not forced to rhyme).
- Overlay safety: map titles single-line (WEDDELL SEA, ABOUT 4 MILES; map cards are lifted out of the caption band by compose's avoid_captions(), as in earlier maps); timeline y=900; cards at y=820 (S12: header + 3 rows, ends ≈1116; S13: header + 3 rows, ends ≈1116); counters/stamps/labels/text in the upper third; depth gauge on the right edge (y 300–1000). Nothing in y 1150–1400.
- Overlays only state what the narration states: "OVER A CENTURY" (not 107 years); the S12 card attributes the no-wood-eaters explanation to experts, as L12 does; the S14 dates restate L14.
