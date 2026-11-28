# QC REPORT — HAUNT-05 "The Tunnel Built to Hide the Dead" (Waverly Hills Sanatorium)

VERDICT: PASS (v2, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 31 MB; 48.50 s (haunted band 35-60 s); -14.6 LUFS; true peak -1.2 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 14 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_onyx). Expected.

## Review cycle
- v1 FAIL (overlays only — the rendered frames are fine, no re-render needed). Edits in `SCRIPTS/HAUNT-05/script.json`:
  1. **S10 (0:34.6-0:37.9) overlay on the 3D number:** "6,000 - 8,000" (text, y 1060) is drawn straight over the struck-through
     3D "63,000", so both numbers mash together. S10 overlay[1] (text) `params.y` 1060 -> 1450 (below the captions).
  2. **S11 (0:37.9-0:40.9) duplicated text:** the 2D card "WHAT SCEPTICS SAY / The building now sells ghost tours" repeats the
     3D corkboard heading "WHAT SCEPTICS SAY" and covers the 3D "PAID GHOST TOURS" ticket card. S11 overlay[1] (card)
     **removed**; the DOCUMENTED FACT badge stays.
  3. **S06 (0:20.1-0:24.7):** the DOCUMENTED FACT badge (y 200) is hidden behind the 1961 document (only "DO" shows). S06
     overlay[0] (label) `params.y` 200 -> 1420.
  4. **S03 (0:07.3-0:12.5) clipped text + stray "~":** the timeline sub-labels "small TB hospital, ~50 beds" and "five-storey
     building" run off the left/right frame edges ("l TB hospital, ~50 beds", "five-storey buildi"). S03 overlay[1]
     (timeline) `params.events` subs -> "TB hospital" / "five storeys" (both fit inside the frame).
  - Test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:11.9, 0:23.6, 0:37.1: clean.
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC.
- v2: re-assembled from the existing frames. PASS. QC_AUTO fresh: 48.50 s, -14.7 LUFS, true peak -1.6 dBTP. Frames checked at 0:11.9 (timeline subs "TB hospital" / "five storeys" inside the frame), 0:23.6 (S06 badge below the captions), 0:36.0 ("6,000 - 8,000" below the captions, struck 63,000 clear) and 0:39.5 (S11 card gone; PAID GHOST TOURS ticket visible). qc_frames skimmed: nothing new.

## Editorial checks (frames every 2 s)
- Hook: the empty gurney rolling down the tunnel, "THE BODY CHUTE" + line 1 ("reportedly") inside 1 s; THEORY + DRAMATISATION. PASS
- No patients, no bodies, no body shapes: the gurney is always empty, the orderly is a faceless mannequin. PASS
- "63,000" is FOLKLORE, counted then struck through in 3D; "6,000-8,000" carries DOCUMENTED FACT (historians' estimate). PASS
- Removed claims absent: no 1945 death count, no Room 502, no "Timmy" or floor for the boy, no winch, no WWII shelter. PASS
- Sightings = EYEWITNESS CLAIM (+ FOLKLORE for the ball boy); echo explanation = THEORY; ball roll = DRAMATISATION. PASS
- Ends on the S01 tunnel framing for the loop. PASS

## Known minor weaknesses (accepted)
- S07/S09/S12/S13 corridors are very dark; the shadow figure in S07 barely reads.
- S06: the lit bays are flat panels; the 1961 document covers most of the building.
- S02/S03: the facade is a stylised grid; S03 timeline sits over the building.
- S04: counter label "TUNNEL LENGTH, APPROX. FEET" overlaps the lamp line (legible).
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
