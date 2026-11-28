# QC REPORT — MURDER-05 "Footprints Led to the Farm. None Led Away." (Hinterkaifeck, 1922)

VERDICT: PASS (v2, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 42 MB; 66.38 s (murder band 55-82 s); -14.5 LUFS; true peak -1.1 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 20 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_onyx). Expected.

## Review cycle
- v1 FAIL (overlays only — the rendered frames are fine, no re-render needed). Edits in `SCRIPTS/MURDER-05/script.json`:
  1. **S05 (0:15.6-0:18.6):** the EYEWITNESS CLAIM badge (y 200) covers the first typed line of the newspaper document
     ("A Munich paper." hidden under the badge). S05 overlay[1] (label) `params.y` 200 -> 1420 (dark wood below the captions).
  2. **S15 (0:45.1-0:49.4) duplicated text:** the red 2D "NO ONE CONVICTED" (text, y 1450) repeats the 3D red "NO CONVICTION"
     stamp across the suspect board (and the caption "convicted"). S15 overlay[1] (type text "NO ONE CONVICTED") **removed**;
     the "SUSPECTS LOOKED AT (100+)" counter stays.
  - S05 placement test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:17.8: clean.
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC.
- v2: re-assembled from the existing frames. PASS. QC_AUTO fresh: 66.38 s, -14.6 LUFS, true peak -1.1 dBTP. Frames checked at 0:17.8 (EYEWITNESS CLAIM badge below the captions; "A Munich paper." line visible) and 0:47.0 (2D "NO ONE CONVICTED" gone; 3D NO CONVICTION stamp + 100+ counter only). qc_frames skimmed: nothing new.

## Editorial checks (frames every 2 s + spot frames at 0:17.5, 0:19.5, 0:47, 0:57.5)
- Hook: footprints in the snow toward the lit farmhouse, line 1 inside 1.5 s. PASS
- No bodies, no violence, no weapon anywhere: S09 ("all six ... were killed") is the dark farmhouse exterior; the victims
  appear only as names on the IN MEMORY card (no ages, no circumstances). "Cäzilia" umlaut renders correctly. PASS
- Pre-crime beats carry EYEWITNESS CLAIM; S03 SOURCE card "Known from neighbours' later statements"; smoke and cattle =
  EYEWITNESS CLAIM; S17 suspect card "Not publicly named (out of respect for relatives, per reports)" keeps the hedge. PASS
- No overlay names a suspect or uses dropped claims (footprints ending at the barn, "lived in the attic", 3 vs 4 days —
  the S14 card says "several days"). PASS
- Timeline "31 MAR / 1-3 APR / 4 APR found" and the 2007 Fürstenfeldbruck stamp match FACTCHECK. PASS
- Ends with "WHY STAY?" + comment prompt, "Sources in description", and loops to the snow footprints. PASS

## Known minor weaknesses (accepted)
- S02: the map is an abstract hexagon with a red line; the title + "MARCH 1922 / UPPER BAVARIA" stamp carry the place.
- S05: the newspaper document is a large mostly empty sheet (two short lines).
- S12: the chimney smoke is a blocky column of white squares; "SMOKE." text sits on the roof line.
- S14: the 3D evidence cards are cropped at frame edge ("AD EATEN", "ATTLE FED"); the CONCLUSION card restates the narration.
- S17: the caption crosses the 3D suspect note in the spotlight.
- S04 (attic, 0:14-0:15.6) is very dark.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
