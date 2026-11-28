# QC REPORT — HAUNT-02 "The Real Room 217" (Stanley Hotel, Elizabeth Wilson)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 32 MB; 50.79 s (haunted band 35-60 s); -14.5 LUFS; true peak -1.3 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 16 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_onyx). Expected.

## Review cycle
- v1 FAIL (overlays only — the rendered frames are fine, no re-render needed):
  1. **S11 (0:34.6-0:37.3) duplicated text.** The 2D card "WHAT THE RECORD SAYS / Survived the 1911 blast / Two broken ankles /
     Returned to work (years)" repeats, word for word, the 3D corkboard card that is already in frame (and adds a stray
     "(years)"). The DOCUMENTED FACT badge (y 200) also covers the start of the 3D card title ("WHAT T..."). Fix in
     `SCRIPTS/HAUNT-02/script.json`: S11 overlay[1] (type card, header "WHAT THE RECORD SAYS") **removed**; S11 overlay[0]
     (label DOCUMENTED FACT) `params.y` 200 -> 900 (corkboard gap between the two 3D cards).
  2. **S13 (0:39.4-0:42.9) overlay on the 3D card.** "SHE DIDN'T / DIE HERE" (text, y 520) is drawn straight over the 3D card
     "DIED HERE? NO." and its struck-through "DIED IN 217", so neither reads. Fix: S13 overlay[1] (type text) `params.y`
     520 -> 1450 (black area below the board and below the captions; text and size unchanged).
  - New placements test-composited with PIPELINE/overlays.py + compose.avoid_captions on frames 0:34.9, 0:36.5, 0:40.5: clean.
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC.

## Editorial checks (frames every 2 s + spot frames at 0:13.3, 0:14.6, 0:26.5, 0:36.5, 0:40.5, 0:43.3, 0:44.3, 0:45.3)
- Hook: corridor dolly to the ajar door, "ROOM 217" + line 1 inside 1 s. PASS
- Labels follow FACTCHECK: King's account = DOCUMENTED FACT; staff story / "still on shift" = FOLKLORE; suitcases/lights =
  EYEWITNESS CLAIM; recreations carry DRAMATISATION. 1911 details stay generic ("JUNE 1911"; no exact cause on screen). PASS
- Wilson is shown alive and faceless (S07 candle, S12 carrying linen); S08 shows only the ceiling hole and dust, no person,
  no injury; King is a faceless silhouette; no hotel or film logos. PASS
- "Survived / Two broken ankles / Returned to work" on the 3D card matches FACTCHECK L11-L12 (no years on screen). PASS
- "THE SHINING — novel, published 1977" scrap card in S04 reads cleanly. PASS
- Ends on the S01 composition with "But it started like this:" for the loop. PASS

## Known minor weaknesses (accepted)
- S02: the stamp "THE STANLEY HOTEL" is typed over the moon; low-poly mountains.
- S08: the falling plaster dust is coarse triangular specks in the light beam (below the hole, not over the subject).
- S13: the DOCUMENTED FACT badge sits on the bottom edge of the upper 3D note card.
- S03/S08/S12 stack two badges (DOCUMENTED FACT + DRAMATISATION) at y 200/290; busy but legible.
- S10: the ghostly chambermaid is very faint (by design).
- S11/S13 3D cards carry redaction-style black blocks that read as placeholder art.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
