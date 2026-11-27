# HAUNT-02 — Animation notes (shots.py + PIPELINE/blender/lib_haunted.py, "STANLEY HOTEL sets")

Preview rounds used: 2 (round 2 = S01, S02, S03, S05, S06, S08, S09, S12, S14, S15, S16 only).
Some fixes were made after round 2 and have NOT been previewed. A bpy ray-cast check (no render) confirmed that each camera
now has a clear view:
- S09/S15: the orbit start was moved off the wardrobe.
- S12: the camera start was moved in front of the corridor back wall.
- S14: the lighting was raised (sconces 0.3, lantern 160 W, camera fill 25).
- S05: the lighting was raised (sconces 0.12, spill 1.6, camera fill 20).

| Shot | Built | Deviation from storyboard / why | Known weaknesses |
|---|---|---|---|
| S01 | `hotel_corridor` (24 m, white panelled walls + wainscot, procedural dark-red/gold diamond carpet, brass twin-shade sconces at 30%, numbered doors in pairs with brass `text3d` numbers). Door 217 on the right is ajar, with a warm light slit and a spill wedge across the carpet. 24 mm dolly from frame 1. | — | The "217" numerals are small on a phone; the spill wedge carries the reveal. |
| S02 | `hotel_facade`: 44 m white 4-storey block, end pavilions, red hipped roofs, portico, cupola, 18x4 windows (2 lit), snowy slope, pines, displaced mountains, moon, fog, snow. Crane down + push, 35 mm. | Fog cards were removed (hard edges); a fog volume near the hotel only. | Low-poly mountains; the red roof reads dark at night. |
| S03 | Dream corridor: cold strobing sconces with blackouts, dutch 12 degrees, carpet-level handheld at 20 mm. Canvas fire hose grows toward the camera (bevel factor) with a brass nozzle riding the head. The running child is camera-invisible: only its shadow on the far wall. | — | The shadow on the far wall is subtle; the hose only reads in the second half. |
| S04 | `room217` at night: brass bed, wardrobe, desk + typewriter, closed suitcase on a rack, mountain view. Writer silhouette at the window with a cigarette ember (pulsing) and a smoke wisp. Push from behind the bed. | script.json: the document overlay is now `scrap` style and starts at 1.4 s, so the silhouette reads first. | — |
| S05 | Reverse angle from the far end; sconces nearly off, 217 spill. | Faint sconces (12%) kept for readability. | Changed after the last preview (brighter). Was too dark in round 2. |
| S06 | 1911 sepia room (sepia palette by material/light, not a grade), brass gas bracket + glass globe + animated-noise shimmer volume. 30 to 50 mm zoom-push toward the lamp. | — | Shimmer reads as grainy haze. |
| S07 | Same room: door swings open (f1-22), faceless chambermaid (long dress + apron) walks in holding a lit candle (flickering, brightest point). | — | Arm pose is stiff. |
| S08 | Flash: an emissive card in front of the lens fades over f1-9, plus a 60 kW light pulse. Then the dining room below: ragged boolean hole in the ceiling, light beam, falling plaster dust, debris, camera shake f1-15. No person shown. | — | — |
| S09 | Present-day room: suitcase CLOSED on the rack, desk lamp dips off twice, slow orbit (28 mm). | Orbit start moved after the last preview (see above). | Frame 1 was not re-previewed. |
| S10 | Corridor, 85 mm: semi-transparent (alpha 0.32) chambermaid beside a linen trolley at the far end, one sconce on, cold window. | — | Very faint by design. |
| S11 | Corkboard: "WHAT THE RECORD SAYS" card slams in (scale), 3 lines appear at f18/27/36, simple leg + bandage icon. | — | The icon is crude. |
| S12 | Daylight corridor: chambermaid silhouette walks away carrying a linen stack, follow dolly. | Camera start moved after the last preview. | The sepia-to-colour return is not animated (no per-shot grade). |
| S13 | Board: "DIED HERE? NO." card with a red strike through "DIED IN 217", push-in. | — | — |
| S14 | Tour group (guide with a flickering lantern + 4 coats) crosses door 217 left to right, perpendicular wide at 24 mm, and leaves the frame by f49 (last 0.9 s empty). | Shot across the corridor so the crossing reads left to right. | Lighting raised after the last preview (round 2 was black); unverified. The walk is brisk. |
| S15 | Exactly the S09 frame-1 composition: suitcase OPEN (lid back, empty red lining), 4 folded clothes squares on the bed, shoes paired by the rack. 3% lens push. | — | Follows the S09 camera fix. |
| S16 | S01 composition: 217 closed with a glow strip under the door that goes out at f36. At f52, door ajar + slit + spill switch on and the S01 dolly starts at S01 speed (loop). | — | — |
