# SCUBA-07 Animation Notes (Antikythera: sponge divers 1900–01, the corroded lump, CT scans 2005)

Builders: `BLENDER_PROJECTS/SCUBA-07/shots.py` (it also imports lib_cave for camera keys, rain, clouds and text).
New functions were appended to `PIPELINE/blender/lib_scuba.py` (no existing function changed): `mat_bronze`, `mat_verdigris`, `lump`, `split_halves`, `gear`, `mount`, `spin`, `amphora`, `helmet_diver`, `caique`, `air_pump`.
Preview rounds: 2 full, plus 1 `--only` round (S01, S03, S04, S08, S09, S10). After that, S09 got single-frame build checks of its last frame only (fixing the gear on the split face).
`render.json`: S02 at 4 samples (dithered x-ray transparency) and S04 at 4 samples (volume plus god rays).

People are faceless. Hard-hat divers wear a brass sphere helmet with a dark glass faceplate, and the crew are rim-lit silhouettes. The 1901 deaths and paralysis appear only as a slumped seated diver and an empty helmet; no injury is shown. The gears are a generic reconstruction look.

| Shot | Built | Deviations / weaknesses |
|---|---|---|
| S01 | Corroded green-brown lump (displaced icosphere with verdigris and crust) on a black plinth with faint caustic ripples, a cool top spot and a teal rim. 85 mm orbit and push. Frame 1 = the S14 end pose (loop). | The plinth caustic net is a little graphic. |
| S02 | Same macro, locked. A bright scan bar sweeps left to right; behind it the lump turns to x-ray line art (a world-X material threshold) and reveals six frozen gear outlines inside. Scanline overlay. | The x-ray lump is speckly (dither). 4 samples. |
| S03 | Storm: grey sea (Ocean modifier), wooden caïque with mast, slanted yard and furled sail, three crew silhouettes, rain, bow spray, a rocky island ahead. One lightning flash at frames 9–13 (sky + sun) under the map card. | The boat is mid-size in frame. |
| S04 | 50 m seabed in blue gloom: 13 encrusted amphorae, a bronze statue arm and shoulder, two pale faceless marble figures lying in the silt, a settling silt cloud, god rays. A hard-hat diver (air hose up, exhaust bubbles) lowers down the weighted line; the camera tilts from him to the wreck field. | No hull, per the storyboard. 4 samples. |
| S05 | Deck: two crewmen work the flywheels of a hand air pump; the hose runs over the gunwale. Hard cut at frame 60 to a 50 mm close-up of the brass helmet in blue gloom with exhaust bubbles. | The crew are mannequins. |
| S06 | Grey sea plate with the island; eight small helmet-diver icons drop in a row at y about 1085 (below the timeline, above the captions). | The icons are small. |
| S07 | Diver without helmet slumped against the mast, a crewman's hand on his shoulder, helmet on the deck beside him. Hard cut at frame 52 to an empty helmet on wet deck. | The card overlay covers the lower-middle of the frame; the subject sits above it. |
| S08 | Wicker basket rises out of the water, dripping, over the gunwale. It holds a bronze arm, a faceless marble head, an amphora shard and the lump. The camera tracks, then racks focus and pushes in to the lump. | The deck is bright. |
| S09 | 1902 storeroom: shelves with numbered trays. The lump splits at frame 15 (small shake); the left piece swings away. The desk lamp swings onto the tray, and the cut face of the right piece shows a bronze gear wheel catching the light. Dust in the beam. The curator's hand and sleeve rest at the tray. | The gear reads from about frame 60 on (end camera turns to the cut face). |
| S10 | Grey CT cabinet with a turntable rotating the fragment. 28 mm arc; hard cut at frame 80 to the monitor, where slices flicker (gear outlines plus dash "lettering") under scanlines. | The lettering is abstract dashes; no real inscription is invented. |
| S11 | The lump shrinks away as eight meshing bronze gears pop in (ratio-correct spin, plus a crank on the main axle) in blue darkness. 35 mm orbit. | None |
| S12 | Front dial: rings and ticks, a gold sun ball on its pointer, and a fast moon pointer with a half-silver ball that passes the sun. A dark disc covers the sun and the key light dims (eclipse). A gold spiral (back dial) then draws on over the face. | The spiral is drawn on the front face as a stand-in for the back dial. |
| S13 | Dark-blue gradient with motes. Spinning gear icon (left) and medieval clock face (right) in the upper third; the camera pans from the gear to the clock under the timeline overlay. | None |
| S14 | Golden calm cove, caïque at anchor. A brass helmet breaks the surface and a hand lifts a brown sponge (splashes). The camera dips under and sinks to the dark seabed, ending on the lump on a low silt mound at the S01 frame-1 pose (85 mm). | The hand's sleeve reads as a pole. |

Script.json overlay fix:
- S03: the map title (y 360) collided with the stamp (y 300). The map now shows 0 to 2.7 s and the stamp from 2.7 s.
