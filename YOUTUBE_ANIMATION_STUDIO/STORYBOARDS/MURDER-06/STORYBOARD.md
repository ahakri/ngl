# MURDER-06 — Storyboard

Mary Celeste, North Atlantic, 1872 / Conan Doyle, 1884. Series: *Cold File*. Beat map: cold open 0–2.5 s (ship, nobody aboard) · legend shown + promise 3–9 s · what was really found 9.5–31 s (map, lifeboat gone, food, barrels, sounding rod, water/seaworthy) · **mid-point turn 31.4 s ("So where did the warm tea come from?")** · twist: Doyle's 1884 story 34–48 s · theory ladder 48–60 s · memorial 60–65 s · comment prompt 65–67.5 s · loop line 68–72 s → frame 1 ("…Until she was… / Found sailing the Atlantic.").

Timings are **estimates** (193 words at 2.95 words/s + pauses) = **~71.7 s**; "1872"/"1884" are spoken as several words, so expect ~73–74 s (inside the 55–80 s band). Re-time from the real Kokoro render (am_michael @1.06). Shot boundary = start of the shot's first line. 9:16, 1080x1920, 24 fps. Captions burned in.

**Legend vs record grading rule:** every legend image (the breakfast cabin, S02, S03, S10, start of S13) is graded sepia + film grain and carries a FOLKLORE badge; every record image is cold grey-green. The viewer must never mistake the legend cabin for evidence.

**Ship build (primitives, reuse across shots):** two-masted brigantine ~31 m — box hull tapered at the bow (bmesh), tarred-wood material, plank deck, small deckhouse aft; foremast with three square sails on cylinder yards (two furled); mainmast with a fore-and-aft gaff sail; bowsprit; rigging as curves; stern davits as two bent cylinders with empty rope falls; wheel = torus + spokes. Sea = `lib_murder.sea` + `fog`. Barrels = bulged cylinders with torus hoops. Sounding rod = thin notched cylinder on a coiled line. Lifeboat (S16 dramatisation only) = half-ellipsoid hull. People only as tiny faceless `char_figure` silhouettes; no real portraits of the Briggs family.

## S01  ·  0.0–2.8 s  (2.8 s)  ·  transition in: cut

- **Narration:** L01 "Found sailing the Atlantic. Nobody on board."
- **Visual:** Ship (build once, reuse; all primitives): two-masted brigantine ~31 m. Hull = box 31x7.5x4 m tapered at bow via bmesh (bow vertices scaled to 0.15 width, raised sheer 0.6 m), dark tarred-wood material, white waterline stripe; deck = plane with plank texture; low deckhouse box 6x4x1.6 m aft of mainmast; foremast = cylinder 0.35 m dia x 26 m with three square-sail yards (cylinders) and square sails (subdivided planes, slight cloth bulge via shape key, two of them furled = thin rolled cylinders); mainmast = cylinder x 27 m with a fore-and-aft gaff sail (quad plane between boom and gaff cylinders); bowsprit cylinder; rigging = curve lines; stern davits = two curved bent cylinders with EMPTY falls hanging (thin rope curves). Frame 1 already moving: the brigantine glides out of a fog bank toward camera at a slight angle, sails half-set and slack, deck empty, the wheel (torus + spokes at the stern) turning slightly on its own. Sea surface swelling.
- **Environment:** other:open sea in fog
- **Camera:** low near-water angle, 35mm, slow push toward the bow, handheld amp 0.02 (boat-bob)
- **Characters:** none
- **Lighting:** overcast grey-green daylight (sun 0.6 soft, colour 0.75/0.85/0.8), thick fog
- **FX:** fog_volume density 0.05 drifting, sea spray particles at bow
- **On-screen text / overlays:** [label] DOCUMENTED FACT
- **SFX:** wind @+0.0s g0.5, creak @+0.4s g0.45, hit @+0.0s g0.5
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S02  ·  2.8–6.5 s  (3.6 s)  ·  transition in: cut

- **Narration:** L02 "You know the legend: warm tea, breakfast on the table."
- **Visual:** LEGEND VERSION (stylised, desaturated sepia grade + film-grain): a cosy cabin (studio_lib room 4x3 m, wood panels) with a table set for breakfast: plates (flat cylinders), cups with rising steam wisps, a teapot (sphere + spout cylinder). Clearly marked as the legend.
- **Environment:** room
- **Camera:** slow dolly across the table 50mm, steam in foreground
- **Characters:** none
- **Lighting:** warm lamp glow, sepia grade
- **FX:** steam wisps from cups (particle smoke, small)
- **On-screen text / overlays:** [label] FOLKLORE; [text] THE LEGEND
- **SFX:** click @+0.6s g0.3
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S03  ·  6.5–9.5 s  (3.1 s)  ·  transition in: cut

- **Narration:** L03 "Most of that is fiction. Even the name."
- **Visual:** Same cabin: the steam freezes, the image desaturates to grey and a red diagonal stamp hits: FICTION. A brass name board on the wall reading 'MARIE CELESTE' flickers.
- **Environment:** room
- **Camera:** static, slight zoom-in 3%
- **Characters:** none
- **Lighting:** lamp flickers out to cold grey
- **FX:** colour grade sepia -> grey, flicker
- **On-screen text / overlays:** [text] FICTION
- **SFX:** hit @+0.4s g0.6, static @+0.9s g0.3
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S04  ·  9.5–13.8 s  (4.3 s)  ·  transition in: whip

- **Narration:** L04 "December 1872, east of the Azores. Another crew spots a ship drifting."
- **Visual:** Map card: stylised North Atlantic: Portugal/Spain coast outline right, Azores dots left. A dotted line marks the brigantine's position east of the Azores; a second ship icon (the Dei Gratia) approaches from the west. Date stamp types on.
- **Environment:** map
- **Camera:** 2D overlay over dark sea plate, slow zoom
- **Characters:** none
- **Lighting:** background dim green-grey
- **FX:** fog in background plate
- **On-screen text / overlays:** [map] EAST OF THE AZORES / North Atlantic; [stamp] 4 DECEMBER 1872 / SPOTTED BY THE DEI GRATIA
- **SFX:** boom @+0.0s g0.5, typewriter @+0.3s g0.4
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S05  ·  13.8–16.2 s  (2.4 s)  ·  transition in: cut

- **Narration:** L05 "The Mary Celeste. Her lifeboat: gone."
- **Visual:** Stern of the brigantine: name board on the transom reads MARY CELESTE (text3d, painted white). Camera rises to the davits: two empty curved davit arms with cut rope ends swinging. No lifeboat.
- **Environment:** other:ship deck, stern
- **Camera:** crane up 35mm from transom name to empty davits
- **Characters:** none
- **Lighting:** overcast grey-green daylight (sun 0.6 soft, colour 0.75/0.85/0.8), thick fog
- **FX:** fog, rope swing (simple sine rotation)
- **On-screen text / overlays:** [text] LIFEBOAT: GONE; [label] DOCUMENTED FACT
- **SFX:** creak @+0.0s g0.5, wind @+0.0s g0.4
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S06  ·  16.2–19.1 s  (2.9 s)  ·  transition in: cut

- **Narration:** L06 "Six months of food and water still aboard."
- **Visual:** Small storeroom below deck: shelves (luggage_shelf builder) stacked with sacks, small casks and water barrels; a flashlight/lantern sweeps across them.
- **Environment:** other:ship galley / storeroom
- **Camera:** handheld 28mm lantern POV pan right
- **Characters:** none
- **Lighting:** lantern warm spot from camera, darkness
- **FX:** dust in beam
- **On-screen text / overlays:** [card] ~6 months of food and water
- **SFX:** creak @+0.3s g0.3
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S07  ·  19.1–22.1 s  (3.0 s)  ·  transition in: cut

- **Narration:** L07 "Seventeen hundred barrels of alcohol in the hold."
- **Visual:** Cargo hold: rows of barrels (cylinders with mid bulge via simple deform, dark oak with iron hoops = thin torus rings) stacked in tiers into darkness, stencilled 'ALCOHOL' on a few. Water glints on the floor between rows.
- **Environment:** other:cargo hold
- **Camera:** slow dolly down the aisle between barrel stacks, 24mm
- **Characters:** none
- **Lighting:** shafts of grey light from an open hatch + lantern
- **FX:** dust, water surface on floor (reflective plane, low ripple)
- **On-screen text / overlays:** [counter] BARRELS OF ALCOHOL; [label] DOCUMENTED FACT
- **SFX:** creak @+0.0s g0.35, underwater_amb @+0.0s g0.15
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S08  ·  22.1–26.8 s  (4.7 s)  ·  transition in: cut

- **Narration:** L08 "A sounding rod lay on deck, as if someone had checked for leaks."
- **Visual:** Close-up on the empty deck: an iron sounding rod (thin cylinder 1.2 m with notch marks, on a coiled line) lies on the planks next to an open pump-well cover. Camera tilts down to it.
- **Environment:** other:ship deck
- **Camera:** slow tilt-down + push 50mm
- **Characters:** none
- **Lighting:** overcast grey-green daylight (sun 0.6 soft, colour 0.75/0.85/0.8), thick fog
- **FX:** light fog, water droplets on deck
- **On-screen text / overlays:** [label] DOCUMENTED FACT; [text] SOUNDING ROD
- **SFX:** metal_groan @+0.2s g0.3, click @+0.8s g0.3
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S09  ·  26.8–31.3 s  (4.5 s)  ·  transition in: cut

- **Narration:** L09 "Three and a half feet of water below. Yet she was seaworthy."
- **Visual:** Cutaway diagram: the brigantine hull in side section (lib_murder.section_diagram style: flat-shaded, cyan line on black), a water level rises to a marked line at 3.5 ft in the hold, while the outer waterline stays normal. Then hull glows green: FLOATING.
- **Environment:** other:ship cross-section
- **Camera:** orthographic side view (lib_murder.ortho), slow zoom
- **Characters:** none
- **Lighting:** emissive diagram lines
- **FX:** water fill animation
- **On-screen text / overlays:** [depth] WATER IN HOLD; [text] STILL SEAWORTHY
- **SFX:** bubbles @+0.0s g0.3, sonar @+1.8s g0.3
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S10  ·  31.3–34.3 s  (3.0 s)  ·  transition in: flash

- **Narration:** L10 "So where did the warm tea come from?"
- **Visual:** MID-POINT TURN. Flash cut back to the sepia legend cabin, push straight into a steaming cup.
- **Environment:** room
- **Camera:** fast push-in 35mm -> 85mm into the cup
- **Characters:** none
- **Lighting:** sepia warm
- **FX:** steam
- **On-screen text / overlays:** [label] FOLKLORE
- **SFX:** riser @+0.0s g0.5, sting @+1.6s g0.5
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S11  ·  34.3–37.9 s  (3.6 s)  ·  transition in: whip

- **Narration:** L11 "In 1884, an anonymous magazine story renamed her Marie Celeste."
- **Visual:** Document reveal: a Victorian magazine page slides in (paper style), title block and dense columns of illegible placeholder text; a highlighted line shows the name 'MARIE CELESTE'. No real page facsimile reproduced; recreated generically.
- **Environment:** document
- **Camera:** top-down, slight rotation
- **Characters:** none
- **Lighting:** warm desk-lamp plate
- **FX:** paper grain
- **On-screen text / overlays:** [document] "...the Marie Celeste..." / (fictional story, published anonymously); [label] DOCUMENTED FACT
- **SFX:** whoosh @+0.0s g0.4, typewriter @+0.5s g0.35
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S12  ·  37.9–43.1 s  (5.1 s)  ·  transition in: cut

- **Narration:** L12 "Many readers took it as fact. The author: Arthur Conan Doyle, before Sherlock Holmes."
- **Visual:** Victorian writing desk (lib_murder.desk + desk_lamp + book props): a pen rests on a manuscript; a faceless silhouette (char_figure, seated, back to camera) at the desk. A deerstalker hat (simple cap + flaps from primitives) sits on a side table, catching the light at the end of the shot.
- **Environment:** other:study desk
- **Camera:** slow arc 40mm around the desk, ends on the hat
- **Characters:** writer silhouette (char_figure seated, back to camera, no face)
- **Lighting:** warm oil lamp + dark room
- **FX:** dust motes
- **On-screen text / overlays:** [title] CONAN DOYLE; [label] DOCUMENTED FACT
- **SFX:** hit @+1.6s g0.5
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S13  ·  43.1–47.9 s  (4.8 s)  ·  transition in: cut

- **Narration:** L13 "The cosy breakfast scenes came from retellings like these. Not from the ship."
- **Visual:** The sepia legend cabin (from S02) dissolves away piece by piece (objects scale to zero), revealing a neutral, empty grey cabin (no food, no props asserted as found; deliberately non-specific). Overlay: two columns LEGEND vs RECORD.
- **Environment:** room
- **Camera:** static 35mm, slight push
- **Characters:** none
- **Lighting:** sepia -> cold grey daylight from a skylight
- **FX:** dissolve of legend props, water drips
- **On-screen text / overlays:** [card] Warm tea, half-eaten meals: / added in later retellings; [label] FOLKLORE
- **SFX:** whoosh @+0.0s g0.4, rumble @+0.5s g0.25
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S14  ·  47.9–52.3 s  (4.5 s)  ·  transition in: whip

- **Narration:** L14 "The leading theories are ordinary." L15 "Alcohol fumes, and fear of an explosion."
- **Visual:** Opens on a THEORIES title over the barrel hold (L14), then: a translucent, faint wavering haze (volume with low density, slight green tint) drifts between barrels; a hatch overhead slams open (rotation key) with a burst of pale light. Theory visualisation only.
- **Environment:** other:cargo hold
- **Camera:** low 24mm looking up toward the hatch
- **Characters:** none
- **Lighting:** dim + flash of pale light through hatch at 2.9 s
- **FX:** vapour haze (volume_puff, green-tinted, low density), flash
- **On-screen text / overlays:** [label] THEORY; [title] THEORIES; [text] FUMES?
- **SFX:** hit @+0.0s g0.4, boom @+2.9s g0.5, whoosh @+2.9s g0.3
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S15  ·  52.3–55.7 s  (3.4 s)  ·  transition in: cut

- **Narration:** L16 "Or a broken pump, and fear she was sinking."
- **Visual:** Deck pump (two cylinders + lever) partly dismantled: parts lying beside it on the deck; water sloshing in the pump well. Theory visualisation only.
- **Environment:** other:ship deck
- **Camera:** close 50mm, slow orbit 20 deg
- **Characters:** none
- **Lighting:** overcast grey-green daylight (sun 0.6 soft, colour 0.75/0.85/0.8), thick fog
- **FX:** water slosh, fog
- **On-screen text / overlays:** [label] THEORY; [text] SINKING?
- **SFX:** metal_groan @+0.0s g0.4, creak @+0.9s g0.3
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S16  ·  55.7–60.2 s  (4.5 s)  ·  transition in: fade_black

- **Narration:** L17 "Either way, they may have taken the lifeboat, and lost the ship."
- **Visual:** DRAMATISATION: a small open lifeboat (half-ellipsoid hull, 6 m) with dim, faceless silhouettes floats in fog while the brigantine, sails filled, slowly pulls away and vanishes into the fog. No harm shown.
- **Environment:** other:open sea in fog
- **Camera:** from lifeboat level, 35mm, locked; ship recedes
- **Characters:** 8-10 tiny seated silhouettes in lifeboat (char_figure, no faces, low detail)
- **Lighting:** overcast grey-green daylight (sun 0.6 soft, colour 0.75/0.85/0.8), thick fog, fog thickening
- **FX:** fog_volume density rising 0.04 -> 0.08, spray
- **On-screen text / overlays:** [label] DRAMATISATION
- **SFX:** wind @+0.0s g0.5, creak @+0.6s g0.3
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S17  ·  60.2–65.1 s  (4.9 s)  ·  transition in: fade_black

- **Narration:** L18 "Captain Briggs, his wife Sarah, two-year-old Sophia and seven crew were never found."
- **Visual:** Respect card: calm grey sea at dusk, a single lantern (point light inside glass cylinder) floats/bobs on a small plank. Memorial overlay with the names.
- **Environment:** other:sea, memorial
- **Camera:** slow push 50mm
- **Characters:** none
- **Lighting:** dusk grey + warm lantern
- **FX:** light fog
- **On-screen text / overlays:** [card] Capt. Benjamin Briggs, Sarah Briggs, / Sophia Briggs (2) and seven crew; [label] DOCUMENTED FACT
- **SFX:** wind @+0.0s g0.3
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S18  ·  65.1–67.9 s  (2.8 s)  ·  transition in: cut

- **Narration:** L19 "Would you have left? Tell me below."
- **Visual:** The empty deck at the wheel, seen from behind: wheel turning by itself a few degrees, fog rolling across.
- **Environment:** other:ship deck
- **Camera:** slow push 35mm toward the wheel
- **Characters:** none
- **Lighting:** overcast grey-green daylight (sun 0.6 soft, colour 0.75/0.85/0.8), thick fog
- **FX:** fog
- **On-screen text / overlays:** [text] WOULD YOU LEAVE?; [stamp] Sources in description
- **SFX:** creak @+0.2s g0.4
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve

## S19  ·  67.9–71.7 s  (3.8 s)  ·  transition in: cut

- **Narration:** L20 "After the last log entry, nine days passed. Until she was..."
- **Visual:** LOOP FRAME: timeline tick '25 NOV last log entry -> 4 DEC found' flashes small, then the frame settles into S01's exact opening composition (ship emerging from fog) for a seamless cut to frame 1.
- **Environment:** other:open sea in fog
- **Camera:** matches S01 start, push
- **Characters:** none
- **Lighting:** as S01
- **FX:** fog_volume
- **On-screen text / overlays:** [timeline] 9 DAYS
- **SFX:** wind @+0.0s g0.5
- **Music:** original/royalty-free dark ambient pad; level follows script.json music_curve
