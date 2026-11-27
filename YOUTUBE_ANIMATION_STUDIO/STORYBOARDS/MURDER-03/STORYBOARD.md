# MURDER-03: Storyboard

D.B. Cooper: the Northwest Orient Flight 305 hijacking (24 Nov 1971) and the Tena Bar money find (10 Feb 1980). Series: *Cold File*.

Beat map:
- cold open 0–6 s
- orientation and hijack 6–24 s
- jump 24–32 s
- **mid-point turn 32.5 s (1980 riverbank, colour flips from storm blue to winter daylight)**
- evidence and twist 37–53 s
- payoff: Cooper vane 55–61 s
- status 61–67 s
- open question and comment prompt 67–71 s
- open question S22, loop line 71–74 s, back to frame 1

Timings come from a Kokoro test render (am_onyx, speed 1.06): total narration **74.2 s**. Shot boundaries are the start of each shot's first line (the pipeline's `timing()` rule). 9:16, 1080x1920, 24 fps. Captions are burned in (red accent, `emphasis` words highlighted). Keep overlays out of the bottom 20 % and right 15 %.

**Reusable prop: STYLISED 727** (built from primitives: exterior in S01, S07, S09, S18, S19, S23; cabin interior in S04)
- Fuselage: a cylinder (r 1.9 m, 40 m) with a tapered nose cone and tail cone, navy-grey metal, red cheat-line. No airline logo or livery.
- Engines: three short cylinders clustered at the tail.
- Tail and wings: a T-tail of thin boxes on a swept fin, and swept wings made from bevelled boxes.
- **Ventral aft airstair:** a hinged stepped box ramp under the tail cone. Animate its hinge X rotation 0 to -35 deg.
- Rain: fast diagonal particle_cloud streaks. Storm: fog_volume cloud deck with flicker lightning.
- Parachute (S10): a half-sphere canopy mesh with thin line cylinders to the figure.
- Forest (S10, S11, S22): forest builder with conifers as stacked cones.
- Riverbank (S12, S13): ground plane with sand material and ripple displacement beside a flat water plane.

No real photos, no FBI composite sketch, no faces. Every human is a faceless `char_figure` silhouette. Banknotes are generic green rectangles, never real currency art. Serial numbers are placeholders.


## S01  ·  0.0–3.4 s  (3.4 s)  ·  transition in: cut

- **Narration:** L01 "He opened the back door of a jetliner in flight. And jumped."
- **Visual:** Frame 1 already moving: underside of the tail of the stylised 727 at night in heavy rain. Stylised Boeing 727 built from primitives: fuselage = cylinder (r 1.9 m, 40 m) with tapered cone nose and tail cone, dark navy-grey metal with a red cheat-line stripe (no airline logo), three rear engines = short cylinders clustered at the tail, T-tail = thin boxes on top of a swept fin, swept wings = flattened bevelled boxes. Ventral airstair = hinged box ramp (0.9 m wide, 6 m long, stepped bump-map) dropping from under the tail cone, open, with a warm cabin-light spill above it. A faceless suited silhouette stands on the lowest step of the open airstair, coat flapping, a small bag strapped to the chest; on 'jumped' he drops out of frame downward and the stairs bounce up.
- **Environment:** other:night sky / jet exterior
- **Camera:** low angle from behind/below the tail, 28mm, slow push-in from frame 1, handheld amp 0.03 (turbulence), slight roll
- **Characters:** hijacker silhouette (char_figure, coat=True, dark suit, faceless, no glasses detail)
- **Lighting:** black-blue night; warm sodium cabin spill through the stair opening; lightning flash (flicker) on 'jumped'
- **FX:** rain streaks (particle_cloud, fast diagonal), cloud fog_volume below the jet
- **On-screen text / overlays:** [label] DOCUMENTED FACT
- **SFX:** wind @+0.0s g0.7, rumble @+0.0s g0.5, thunder @+2.2s g0.6
- **Music level:** 0.55 → 0.57 (original/royalty-free dark ambient pad; no licensed music)

## S02  ·  3.4–6.1 s  (2.7 s)  ·  transition in: cut

- **Narration:** L02 "With two hundred thousand dollars in ransom."
- **Visual:** Close tracking shot of a canvas money bag (rounded box mesh, khaki cloth, drawstring) tumbling through rain and cloud, strapped to the dark silhouette's torso (only torso + arm visible, no face). A couple of $20-style green paper rectangles (plain, no real banknote artwork) flutter past camera.
- **Environment:** other:night sky freefall
- **Camera:** tracking freefall, 35mm, camera rotates slowly around the bag; motion blur
- **Characters:** hijacker silhouette (torso only)
- **Lighting:** dark blue ambient, lightning rim light from above
- **FX:** rain particles, cloud fog_volume, paper bill particles (3-5 flat planes)
- **On-screen text / overlays:** [counter] RANSOM (USD)
- **SFX:** whoosh @+0.0s g0.7, wind @+0.0s g0.6
- **Music level:** 0.57 → 0.58 (original/royalty-free dark ambient pad; no licensed music)

## S03  ·  6.1–10.2 s  (4.1 s)  ·  transition in: whip

- **Narration:** L03 "November 24th, 1971. Flight three-oh-five."
- **Visual:** Map card: stylised Pacific Northwest coastline; a route line draws north from PORTLAND to SEATTLE; pin on Seattle. Date stamp types on.
- **Environment:** map
- **Camera:** 2D overlay over a darkened rain-on-window background plate (slow zoom)
- **Characters:** none
- **Lighting:** n/a (overlay); background plate dim blue-grey
- **FX:** rain drops on glass in background plate
- **On-screen text / overlays:** [map] FLIGHT 305 / Portland to Seattle; [stamp] 24 NOVEMBER 1971 / NORTHWEST ORIENT FLIGHT 305
- **SFX:** boom @+0.0s g0.5, typewriter @+0.2s g0.4
- **Music level:** 0.58 → 0.60 (original/royalty-free dark ambient pad; no licensed music)

## S04  ·  10.2–14.4 s  (4.2 s)  ·  transition in: cut

- **Narration:** L04 "A passenger ticketed as Dan Cooper handed a flight attendant a note."
- **Visual:** Low-poly 727 cabin (corridor builder re-skinned: narrow aisle, rows of box seats in muted 1970s orange/brown, small round windows with rain). Rear-row faceless suited silhouette extends an arm; a folded paper note passes into the hand of a second silhouette in a flight attendant's uniform (char_figure, lighter colour). Focus pulls to the note.
- **Environment:** other:aircraft cabin interior
- **Camera:** aisle-level 50mm, slow dolly toward the rear row; rack focus to the note
- **Characters:** hijacker silhouette (dark suit), flight attendant silhouette (light uniform, faceless)
- **Lighting:** warm overhead cabin light, cool window light, soft
- **FX:** subtle cabin haze
- **On-screen text / overlays:** [text] 'DAN COOPER'; [card] "D.B." came later - a press mix-up
- **SFX:** click @+0.2s g0.3, rumble @+0.0s g0.3
- **Music level:** 0.60 → 0.62 (original/royalty-free dark ambient pad; no licensed music)

## S05  ·  14.4–16.2 s  (1.7 s)  ·  transition in: cut

- **Narration:** L05 "It claimed he had a bomb."
- **Visual:** Document reveal: a small torn note card slides up (paraphrase only, not the real wording). Behind it, the cabin plate blurs; a dark briefcase on the seat is lit by a single overhead spot.
- **Environment:** document
- **Camera:** 2D overlay over blurred cabin plate; slow push on the briefcase behind
- **Characters:** none
- **Lighting:** single top-light on the briefcase, rest dark
- **FX:** dust motes in light
- **On-screen text / overlays:** [document] (paraphrase) / I HAVE A BOMB; [label] DOCUMENTED FACT
- **SFX:** hit @+0.0s g0.7, heartbeat @+0.4s g0.4
- **Music level:** 0.62 → 0.63 (original/royalty-free dark ambient pad; no licensed music)

## S06  ·  16.2–19.0 s  (2.8 s)  ·  transition in: cut

- **Narration:** L06 "He'd demanded that cash. And four parachutes."
- **Visual:** Top-down on a dark table: four parachute packs (rounded boxes with harness straps, olive and white) slam down one after another in time with the words, next to a stack of banded green bill-bricks.
- **Environment:** other:evidence table
- **Camera:** top-down 35mm, tiny push-in each time a pack lands
- **Characters:** none
- **Lighting:** hard top-light, red rim from below
- **FX:** dust puff on each impact
- **On-screen text / overlays:** [card] $200,000 in $20 bills / 4 parachutes
- **SFX:** hit @+0.0s g0.5, hit @+0.6s g0.5, hit @+1.2s g0.5, hit @+1.8s g0.6
- **Music level:** 0.63 → 0.64 (original/royalty-free dark ambient pad; no licensed music)

## S07  ·  19.0–21.8 s  (2.8 s)  ·  transition in: cut

- **Narration:** L07 "In Seattle, he swapped the passengers for the cash."
- **Visual:** Rain-soaked airport apron at night (ground plane, wet roughness 0.1, yellow taxi line). The stylised 727 sits under floodlights, front door open; a line of small faceless silhouettes walks down a boarding stair away from the jet while a single figure carries a bag toward the tail.
- **Environment:** road_night
- **Camera:** wide 35mm from the apron, slow truck right, reflections in the puddles
- **Characters:** passenger silhouettes x8-10 (anim_walk), courier silhouette with bag
- **Lighting:** orange sodium floodlights, wet reflections, rain backlit
- **FX:** rain particles, light fog_volume
- **On-screen text / overlays:** [stamp] SEATTLE-TACOMA AIRPORT / 36 PASSENGERS RELEASED
- **SFX:** footsteps @+0.2s g0.4, rumble @+0.0s g0.4
- **Music level:** 0.64 → 0.66 (original/royalty-free dark ambient pad; no licensed music)

## S08  ·  21.8–24.4 s  (2.6 s)  ·  transition in: whip

- **Narration:** L08 "Then he ordered the jet south, toward Mexico."
- **Visual:** Same map card style: route line now draws SOUTH from Seattle, past Portland, dashed toward the bottom edge with 'RENO (refuel) / MEXICO' label off-card. A small jet icon rides the line.
- **Environment:** map
- **Camera:** 2D overlay over dark cloud plate, slow drift down
- **Characters:** none
- **Lighting:** n/a
- **FX:** clouds drifting in background
- **On-screen text / overlays:** [map] HEADING SOUTH / toward Mexico, via Reno to refuel
- **SFX:** whoosh @+0.0s g0.6, rumble @+0.3s g0.5
- **Music level:** 0.66 → 0.67 (original/royalty-free dark ambient pad; no licensed music)

## S09  ·  24.4–28.2 s  (3.8 s)  ·  transition in: cut

- **Narration:** L09 "Over southwest Washington, in a storm, he lowered the rear stairs."
- **Visual:** Side view of the stylised 727 flying through rain cloud; the ventral airstair under the tail slowly hinges down, spilling a wedge of warm light into the rain. Lightning backlights the cloud deck.
- **Environment:** other:night sky / jet exterior
- **Camera:** parallel tracking shot, 50mm, jet left-to-right, slow push toward the tail
- **Characters:** none
- **Lighting:** dark storm blue; lightning flicker every ~1.5 s; warm stair light
- **FX:** rain streaks, cloud fog_volume (thick)
- **On-screen text / overlays:** [stamp] APPROX. 8:13 PM / SW WASHINGTON
- **SFX:** metal_groan @+0.4s g0.6, wind @+0.0s g0.6, thunder @+1.5s g0.5
- **Music level:** 0.67 → 0.69 (original/royalty-free dark ambient pad; no licensed music)

## S10  ·  28.2–30.2 s  (1.9 s)  ·  transition in: cut

- **Narration:** L10 "And stepped off into the dark."
- **Visual:** Looking straight down: a tiny silhouette falls away from camera into black cloud; a parachute canopy (half-sphere mesh, pale fabric) blooms; through a cloud break, an endless dark forest (forest builder, dense conifers as cone stacks) far below.
- **Environment:** forest
- **Camera:** top-down from the stair, 24mm, camera holds while figure shrinks; slow rotation
- **Characters:** hijacker silhouette under canopy
- **Lighting:** almost black; faint moon/cloud glow; canopy lit by one lightning flash
- **FX:** rain, cloud fog_volume parting
- **On-screen text / overlays:** —
- **SFX:** whoosh @+0.0s g0.8, wind @+0.2s g0.5
- **Music level:** 0.69 → 0.69 (original/royalty-free dark ambient pad; no licensed music)

## S11  ·  30.2–32.4 s  (2.3 s)  ·  transition in: cut

- **Narration:** L11 "No trace of him was ever found."
- **Visual:** Daylight-grey overcast: low aerial over wet conifer forest and a river bend; three faceless searcher silhouettes in a line push through ferns with torches; nothing found. On-screen card covers the search.
- **Environment:** forest
- **Camera:** low drone pass over the treetops, 35mm, then tilt down to the searchers
- **Characters:** searcher silhouettes x3 (anim_walk, rain jackets)
- **Lighting:** flat overcast grey-green, torch cones in mist
- **FX:** fog_volume in the trees, drizzle
- **On-screen text / overlays:** [label] DOCUMENTED FACT; [card] Ground searches of SW Washington / No body, no Cooper
- **SFX:** footsteps @+0.0s g0.4, wind @+0.0s g0.3
- **Music level:** 0.69 → 0.50 (original/royalty-free dark ambient pad; no licensed music)

## S12  ·  32.4–37.6 s  (5.2 s)  ·  transition in: flash

- **Narration:** L12 "In 1980, an eight-year-old smoothed sand for a campfire by the Columbia River."
- **Visual:** MID-POINT TURN — colour flips from storm blue to pale winter daylight. A wide sandy riverbank (ground plane with sand material + ripples) beside a broad grey river; a small child silhouette kneels, sweeping sand flat with his hands; a parent silhouette in the background stacks driftwood.
- **Environment:** other:riverbank
- **Camera:** wide 35mm, slow push toward the kneeling child
- **Characters:** child silhouette (small char_figure, faceless), adult silhouette (background)
- **Lighting:** low cold winter sun, long shadows, soft haze over the water
- **FX:** light mist over the river
- **On-screen text / overlays:** [stamp] 10 FEBRUARY 1980 / TENA BAR, COLUMBIA RIVER
- **SFX:** wind @+0.0s g0.3, sting @+0.0s g0.6
- **Music level:** 0.50 → 0.87 (original/royalty-free dark ambient pad; no licensed music)

## S13  ·  37.6–40.6 s  (2.9 s)  ·  transition in: cut

- **Narration:** L13 "Under the sand: three rotting bundles of twenties."
- **Visual:** Macro: sand slides away to reveal three blackened, swollen bundles of green paper (stacked thin planes, edges frayed, darker at corners), held by perished rubber bands. Generic bills only — no real banknote design.
- **Environment:** other:riverbank macro
- **Camera:** macro 85mm, top-down rack focus as sand pours off
- **Characters:** none
- **Lighting:** low raking winter sun, wet sand sparkle
- **FX:** falling sand grains (particle_cloud tan)
- **On-screen text / overlays:** [label] DOCUMENTED FACT
- **SFX:** hit @+0.0s g0.6, riser @+0.2s g0.4
- **Music level:** 0.87 → 0.89 (original/royalty-free dark ambient pad; no licensed music)

## S14  ·  40.6–45.0 s  (4.5 s)  ·  transition in: cut

- **Narration:** L14 "About five thousand eight hundred dollars. The serial numbers matched the ransom."
- **Visual:** Evidence card: a recovered bill fragment on the left, a 1971 ransom-list microfilm strip on the right; serial-number rows highlight and a red line connects them, then a red MATCH stamp. Serial numbers are placeholders (e.g. L0000000A), not real ones.
- **Environment:** other:evidence board
- **Camera:** 2D overlay, push-in on the matching rows
- **Characters:** none
- **Lighting:** n/a
- **FX:** —
- **On-screen text / overlays:** [card] ~$5,800 in $20 bills / Serials on the 1971 ransom list; [title] MATCH
- **SFX:** typewriter @+0.0s g0.4, hit @+1.6s g0.8
- **Music level:** 0.89 → 0.92 (original/royalty-free dark ambient pad; no licensed music)

## S15  ·  45.0–48.8 s  (3.8 s)  ·  transition in: whip

- **Narration:** L15 "But that sandbar sits miles from where investigators think he jumped."
- **Visual:** Map card: the estimated flight path is a thin dashed line north-south; a soft red oval marks the presumed drop zone; the route line draws from the drop zone to a pin on Tena Bar further south-west on the river, with a '~20 MI?' tag.
- **Environment:** map
- **Camera:** 2D overlay over dark river plate
- **Characters:** none
- **Lighting:** n/a
- **FX:** —
- **On-screen text / overlays:** [map] DROP ZONE vs. TENA BAR / estimates vary; [label] DISPUTED
- **SFX:** boom @+0.0s g0.4
- **Music level:** 0.92 → 0.94 (original/royalty-free dark ambient pad; no licensed music)

## S16  ·  48.8–52.6 s  (3.8 s)  ·  transition in: cut

- **Narration:** L16 "Washed downstream? Buried? Nobody has proven how it got there."
- **Visual:** Evidence board (dark cork wall): two theory cards pin on in time with the words; a third card reads '?'. Red string links them to a photo-style card of the sandbar (rendered, not a photo).
- **Environment:** other:evidence board
- **Camera:** slow push-in, 35mm, slight handheld
- **Characters:** none
- **Lighting:** single desk lamp, warm, deep shadows
- **FX:** dust
- **On-screen text / overlays:** [label] THEORY; [text] WASHED DOWNSTREAM?; [text] BURIED?; [text] UNPROVEN
- **SFX:** hit @+0.1s g0.4, hit @+1.3s g0.4, hit @+2.4s g0.6
- **Music level:** 0.94 → 0.88 (original/royalty-free dark ambient pad; no licensed music)

## S17  ·  52.6–54.7 s  (2.1 s)  ·  transition in: cut

- **Narration:** L17 "The rest has never been found."
- **Visual:** Callback to S02: the empty sky over the dark forest at night, rain; no figure, no bag. A counter subtracts the find from the ransom.
- **Environment:** other:night sky freefall
- **Camera:** slow tilt down from cloud to treetops, 35mm
- **Characters:** none
- **Lighting:** dark blue, faint moon
- **FX:** rain, fog_volume
- **On-screen text / overlays:** [counter] STILL MISSING (USD)
- **SFX:** wind @+0.0s g0.5, heartbeat @+0.3s g0.4
- **Music level:** 0.88 → 0.83 (original/royalty-free dark ambient pad; no licensed music)

## S18  ·  54.7–59.2 s  (4.5 s)  ·  transition in: cut

- **Narration:** L18 "After copycats, the FAA had seven-twenty-sevens fitted with a stair lock."
- **Visual:** Clean technical cutaway: the stylised 727 tail in a dim hangar; a small spring-loaded paddle (thin box on a hinge) under the fuselage flips into the airflow line, and the airstair attempts to drop but is blocked. Blueprint-blue line overlay draws the paddle.
- **Environment:** other:jet exterior, hangar
- **Camera:** side 50mm, slow orbit 20 deg around the tail
- **Characters:** none
- **Lighting:** cool hangar top-lights, blue blueprint lines
- **FX:** faint dust
- **On-screen text / overlays:** [card] Spring-loaded vane blocks the / rear stairs from opening in flight; [label] DOCUMENTED FACT
- **SFX:** click @+1.0s g0.6, metal_groan @+1.2s g0.4
- **Music level:** 0.83 → 0.72 (original/royalty-free dark ambient pad; no licensed music)

## S19  ·  59.2–61.2 s  (2.0 s)  ·  transition in: cut

- **Narration:** L19 "They call it the Cooper vane."
- **Visual:** Macro on the vane itself: the small hinged paddle under the 727 fuselage snaps flat against the closed airstair as a red outline draws round it; blueprint lines fade out.
- **Environment:** other:jet exterior, macro
- **Camera:** macro 85mm, quick push-in then hold
- **Characters:** none
- **Lighting:** cool hangar light, red outline glow
- **FX:** faint dust
- **On-screen text / overlays:** [title] COOPER VANE
- **SFX:** hit @+0.2s g0.6
- **Music level:** 0.72 → 0.68 (original/royalty-free dark ambient pad; no licensed music)

## S20  ·  61.2–65.2 s  (4.0 s)  ·  transition in: cut

- **Narration:** L20 "In 2016, the FBI stopped actively investigating."
- **Visual:** Document reveal: a neutral recreated case-file cover (no real FBI seal or letterhead) with 'NORJAK' typed; a rubber stamp slams 'ACTIVE INVESTIGATION ENDED - JULY 2016'.
- **Environment:** document
- **Camera:** 2D overlay over a dark desk plate, slight push
- **Characters:** none
- **Lighting:** n/a
- **FX:** —
- **On-screen text / overlays:** [document] CASE: NORJAK (Northwest hijacking) / Status: active investigation ended, / July 2016 / Evidence preserved for history; [label] DOCUMENTED FACT
- **SFX:** typewriter @+0.4s g0.5, hit @+2.0s g0.7
- **Music level:** 0.68 → 0.60 (original/royalty-free dark ambient pad; no licensed music)

## S21  ·  65.2–67.2 s  (2.0 s)  ·  transition in: cut

- **Narration:** L21 "No one was ever charged."
- **Visual:** Evidence board wall of faceless suspect cards (blank silhouettes, no names, no likenesses) - dozens of them; the camera pulls back to show the wall is huge; none is marked.
- **Environment:** other:evidence board
- **Camera:** fast pull-back, 24mm
- **Characters:** none
- **Lighting:** single cold lamp, long shadows
- **FX:** dust
- **On-screen text / overlays:** [counter] SUSPECTS CONSIDERED; [text] CHARGED: 0
- **SFX:** whoosh @+0.0s g0.4, hit @+1.0s g0.6
- **Music level:** 0.60 → 0.56 (original/royalty-free dark ambient pad; no licensed music)

## S22  ·  67.2–71.3 s  (4.1 s)  ·  transition in: cut

- **Narration:** L22 "Did he die in those woods, or walk out?" L23 "Where do you think he landed?"
- **Visual:** Dawn in the conifer forest, mist on the ground; an empty clearing where a faint line of footprints fades out after a few metres. Deliberately ambiguous: no body, no canopy, no figure. On the question (about 2.4 s in) the camera rises above the canopy to endless treetops.
- **Environment:** forest
- **Camera:** slow ground-level push through the trees, 24mm, then crane up above the canopy for the question
- **Characters:** none
- **Lighting:** blue-grey dawn, god rays through fog
- **FX:** fog_volume, drips
- **On-screen text / overlays:** [label] THEORY; [card] FBI view: he probably didn't survive / No body has ever been found; [text] WHERE DID / HE LAND?
- **SFX:** wind @+0.0s g0.4, footsteps @+0.6s g0.2
- **Music level:** 0.56 → 0.55 (original/royalty-free dark ambient pad; no licensed music)

## S23  ·  71.3–74.2 s  (2.9 s)  ·  transition in: cut

- **Narration:** L24 "All anyone knows for sure is this."
- **Visual:** Loop frame: same framing as S01 — underside of the 727 tail in rain, airstair open, warm spill; the suited silhouette steps back onto the bottom stair, matching frame 1.
- **Environment:** other:night sky / jet exterior
- **Camera:** matches S01: low angle 28mm, push-in, handheld
- **Characters:** hijacker silhouette
- **Lighting:** as S01
- **FX:** rain streaks, cloud fog_volume
- **On-screen text / overlays:** —
- **SFX:** wind @+0.0s g0.6, rumble @+0.0s g0.4
- **Music level:** 0.55 → 0.55 (original/royalty-free dark ambient pad; no licensed music)
