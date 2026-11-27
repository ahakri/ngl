# HAUNT-01 — Animation notes (shots.py + PIPELINE/blender/lib_haunted.py)

Preview rounds used: 3 (round 3 = only shots S03, S05, S06, S07, S09, S10, S11).

| Shot | Built | Deviation from storyboard / why | Known weaknesses |
|---|---|---|---|
| S01 | `enfield_bedroom` (3.3x3.6 m, floral wallpaper shader, brown carpet, sash window + curtains, two beds with rumpled duvets, cabinet, lamp off, recorder with spinning reels + red REC lamp, chair at position A), moon spot + room fog + dust. Doorway push-in, 26 mm, moving from frame 1. | Recorder sits on a low cabinet between the beds, not on the floor by the door: on the floor it fell into the caption zone (bottom 35%). | REC lamp is small at phone size; soft-shadow noise at 4 samples. |
| S02 | 3 x `semi_pair` (brick, gable roof, chimney, garden walls), wet road, sodium `streetlamp`, fog, drizzle. Lateral dolly right, 35 mm. | — | Ground-floor windows sit in the caption zone; street reads a little bright/orange. |
| S03 | Same street, house body cut back so the downstairs-left window shows a lit hallway; mother silhouette (coat, phone at ear, cord to table phone) behind a net curtain. Static then push, 50 mm. | — | The phone handset is tiny at preview size. |
| S04 | Living room (green wallpaper, sofa, TV, pendant bulb with 2 dips), backlit officer with peaked cap in the doorway; chair slides 1.1 m. Locked-off, 24 mm. | — | Some volumetric noise near the ceiling. |
| S05 | Narrow hall, open front door, cold street light + fog spill, warm bulb; two investigators walk in toward the camera (B carries the recorder). Low camera on the stairs, handheld. | — | The carried recorder is small and hard to read. |
| S06 | Macro on the recorder (70 mm, f/2.2, orbit about 22 degrees): reels turning, REC lamp, VU needle. | 70 mm instead of 85 mm so both reels fit the 9:16 frame. On the cabinet, not on the carpet (matches S01). | The second reel is partly out of frame. |
| S07 | Bedroom: chair toppled, chest of drawers face-down, duvet on the floor, lamp flicker with 2 blackouts (f12-16, f22-27). Whip pan (f1-6) then handheld. | — | Chest is a plain dark box close to the camera. |
| S08 | 3D oscilloscope: procedural jagged waveform (not from the real tape) + glow trace, graticule, scanline sweep, faint bed behind. Scrolls right-to-left, slight zoom. | — | Bed silhouette is barely visible (deliberate). |
| S09 | High-corner 20 mm. A lamp knocked to the floor throws the chair's shadow onto the wall above the right bed. A jumper hung on the chair makes it read as a head and shoulders. Slow tilt down. | Added a jumper on the chair so the shadow reads as a seated man. script.json: the document overlay now starts at 1.5 s so the shadow reads first. | The overlay later covers most of the frame (as scripted). The storyboard asks for the waveform overlay to continue small here; overlays.py has no waveform type, so it is not shown. |
| S10 | Corkboard, pinned cards with 3D text, red string, bent-spoon icon; spoon card slides in (f1-13). Slow push. | — | — |
| S11 | Same board, push onto the VENTRILOQUISM? card (head + sound-wave icon). | — | — |
| S12 | Desk + generic newspaper page with the headline "ABOUT 2% WAS FAKED / 2016 INTERVIEW" (no real masthead), drift up, DOF. | script.json: the "2%" overlay now starts at 2.2 s (on "about two per cent"). | The document overlay covers most of it (as scripted). |
| S13 | Bedroom, chair B against the wall, REC off, reels still. Closer doorway framing on the chair corner (30 mm), slow push. | Not "S01 framing +10% wider": a tighter shared framing for S13/S14 makes the chair change readable (director note). | — |
| S14 | Exactly S13's end framing (match-cut). Chair back at position A in a moonlight kick; REC lamp, VU and reels switch on at f18. 3% lens push. | See S13. | — |
| S15 | Same as S01 start, same push speed (loop). | — | — |

Render cost: preview ran about 6-10 s/frame at 270 px while the machine was under heavy shared load (load average about 20), so the timings are not reliable. The scenes use at most 2 volumes and at most about 1.8k particles. The bedroom room-fog volume is the main cost. If final frames go over budget, lower the `room_fog` density or remove it first.
