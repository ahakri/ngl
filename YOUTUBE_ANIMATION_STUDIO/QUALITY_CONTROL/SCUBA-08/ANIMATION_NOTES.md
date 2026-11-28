# SCUBA-08 Animation Notes (Shackleton's Endurance: sank 1915, found 5 March 2022)

Builders: `BLENDER_PROJECTS/SCUBA-08/shots.py`, plus functions appended to `PIPELINE/blender/lib_scuba.py` (no existing function changed): `bq_hw`, `bq_top`, `mat_ship_wood`, `anemone`, `stern_name`, `barquentine`, `auv_torpedo`, `rov_drone`, `ice_floes`. Reused: lib_cave (camera keys, clouds, skies, `ice_sheet`, `beam_cone`), lib_murder (`mat_snow`, `lifeboat`), lib_scuba `dsv` (re-dressed as the icebreaker), `world_volume`.
Preview rounds: 3 (1 full, then S01/S04/S06/S11/S12/S13, then S11/S13/S14). No `render.json`.

Fact-check points held: the five-pointed star sits BELOW the ENDURANCE arc (the brief said "above"; the fact-check and script say beneath, so that was followed). Shackleton is not shown; the crew are 28 tiny faceless figures. The lamps never touch the wreck and pull away in S13. Ship, icebreaker and robots are generic, no logos or livery. No divers appear.

The ship is a new simple three-masted barquentine (lofted hull, flat stern, deckhouse) rather than the storyboard's re-rigged lib_murder brigantine, which carries another ship's name.

| Shot | Built | Deviations / weaknesses |
|---|---|---|
| S01 | Stern of the wreck: gold ENDURANCE arc with the star beneath, two lamps with visible beams sweeping across, anemones on the rail, slide and push. Moving at frame 1. | The stern is a flat transom, not a rounded counter. Marine snow is sparse and kept to the sides. |
| S02 | Defocused drift along the hull behind the map card. | Background only. |
| S03 | 1915: rigged ship in the pack, ice blocks pressing on the hull, list keyed 1 to 8 degrees, a foremast yard cock-bills at frame 45 with a shake. | Ridge blocks are plain faceted boxes and hide the lower hull. Snap frame not previewed on its own. |
| S04 | Dusk: 28 figures in a line and three boats on the floe; behind them the ship pitches bow-down and slides into a dark lead. | Figures are a stiff, even row. Boats barely read. Storyboard said stern tilts up: it does, as the bow goes under. |
| S05 | Empty seabed, lamp pool, marine snow, slow push (behind the timeline). | Background only. |
| S06 | Under the ice: yellow torpedo robot glides away beneath the milky ceiling; lamp keyed off at 80%. | **Weakest.** The robot is small after the first second; the lower half of the frame is plain dark water. |
| S07 | Aerial: red-hulled icebreaker (dsv without tower and crane) moving through polygon floes, dark lane and brash behind, light snow. | Floes are regular hexagon-like plates and do not part. The lane is mostly out of frame. A helideck ring is visible on the bow. |
| S08 | Yellow box drone with four pods, tilted nose-down, two lamp cones; snow streams upward; cool rim lights. | Reads as a plain yellow slab. |
| S09 | Bow of the wreck comes out of the dark as two lamps converge, then hold from frame 30. | Frame 1 is mostly dark seabed (flash transition covers it). No scanline effect. |
| S10 | Sea ice and the ship from 250 m, defocused, behind the map card. | Background only. |
| S11 | Whole ship upright on the seabed from the bow quarter, two lamps travelling along the hull, blue fill spots (no volume contribution). | Lit patch is small relative to the hull; fallen spars are hard to read at this size. |
| S12 | Deck planks and rail from above with anemones and small pale blobs, raking lamp, slow slide. | 85 mm slide over a small purpose-built set, not the ship model. Anemones are simple stalk-and-tentacle props. |
| S13 | S11 set: camera pulls back and rises while the lamps dim to 7%. | Ends nearly black by design; the blue fill keeps the hull faintly visible. |
| S14 | Stern again, arriving on S01's exact frame-1 camera pose and lamp aims. | None |

Script.json overlay edits: none (all params matched overlays.py and stayed clear of the caption band).

Changed after the last preview, not seen rendered: S02 and S09 were not re-previewed after the anemone restyle and the larger stern letters (both seen in S01/S14).
