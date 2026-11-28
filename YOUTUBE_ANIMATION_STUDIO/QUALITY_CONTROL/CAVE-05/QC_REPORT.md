# QC REPORT — CAVE-05 "Air for One Diver. There Were Two." (Xisco Gràcia, Sa Piqueta, Mallorca, 2017)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~4.9 Mbps, 36 MB; 58.58 s (cave band 50-72 s); -14.5 LUFS; true peak -1.2 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 17 shots rendered (1447 frames).
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_michael). Expected.

## Review cycle
- v1 FAIL (overlays only, cosmetic — the rendered frames are fine, no re-render needed). Edits in `SCRIPTS/CAVE-05/script.json`:
  1. **S07 (0:20.8-0:25.0) stray "~":** text "~900 M FROM\nTHE ENTRANCE" -> "ABOUT 900 M FROM\nTHE ENTRANCE" (matches L07 "about
     900 metres in"; same tilde class as MURDER-02/SCUBA-03).
  2. **S11 (0:37.9-0:41.2) stray "~":** text "VISIBILITY: ~0" -> "VISIBILITY: NEAR ZERO" (size 84 still fits the width).
  - Test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:22.6 and 0:39.5: clean.
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC at 0:22.6 and 0:39.5.

## Editorial checks (frames every 2 s + spot frames at 0:00.3, 0:00.9, 0:01.5, 0:02.2, 0:12.5, 0:21.5, 0:22.6, 0:24.5, 0:39.5, 0:50.5)
- Hook: two divers' crossed torch beams + "AIR FOR 1" + line 1 inside 2 s. PASS
- Gràcia is a faceless helmeted figure; the hallucination beat is labelled DRAMATISATION; no injury detail. PASS
- Hours counter 21 -> 29 -> 44 -> 57 -> 60 matches "around hour 60"; "17 APRIL 2017 / FOUND ALIVE". PASS
- Cross-section is marked "SCHEMATIC, NOT TO SCALE"; "DRILL: FAILED" matches L10. PASS
- Ends on the two tanks / "Both came home", looping to the opening line. PASS

## Known minor weaknesses (accepted)
- S04 (0:10.7-0:13.8): the 2D names "XISCO GRÀCIA / GUILLEM MASCARÓ" (y 1000/1080, pushed up by the caption guard) sit right
  above the caption that says the same names, over the diver scene.
- S07: the 3D "ENTRANCE" label is partly behind the 2D "SCHEMATIC, NOT TO SCALE" line at ~0:22.
- S09/S13/S14: long stretches of near-black frame with only the hours counter (by design: alone in the dark).
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
