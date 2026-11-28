# QC REPORT — CAVE-06 "It Looks Like a Pond. Divers Call It Everest." (Eagle's Nest Sink, Florida)

VERDICT: PASS (v2, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 39 MB; 61.20 s (cave band 50-72 s); -14.6 LUFS; true peak -1.1 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 16 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_michael). Expected.

## Review cycle
- v1 FAIL (overlays only — the rendered frames are fine, no re-render needed):
  1. **S05 (0:12.4-0:17.1):** the quoted nickname "EVEREST OF CAVE DIVING" (text overlay, y 250) is drawn right on top of the
     map's subtitle "HERNANDO COUNTY, FLORIDA" (the map title/subtitle sit above the card at ~y 150/230 after the caption
     shift), so both lines are garbled. Fix in `SCRIPTS/CAVE-06/script.json`: S05 overlay[1] (type text) `params.y` 250 -> 1420
     (below the caption band 1150-1340, over the empty defocused Ballroom; start 2.0 s and size 54 unchanged).
  2. **S14 (0:50.0-0:55.0):** the EYEWITNESS CLAIM badge (y 200) covers the rendered "CHIMNEY" diagram label as the camera
     pushes in (0:53-0:55: "CHIMNEY" half-hidden under the badge). Fix in script.json: S14 overlay[1] (type label) `params.y`
     200 -> 1420 (clean dark area left of the tunnel, below the captions). Badge text unchanged.
  - Both placements were test-composited with PIPELINE/overlays.py + compose.avoid_captions on frames 0:15.4 and 0:53.5: clean.
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC.
- v2: re-assembled from the existing frames. PASS. QC_AUTO fresh: 61.20 s, -14.7 LUFS, true peak -1.6 dBTP. Frames checked at 0:15.4, 0:16.9 ("EVEREST OF CAVE DIVING" now below the captions; map title/subtitle clean) and 0:53.5, 0:54.7 (EYEWITNESS CLAIM badge below the captions, "CHIMNEY" label uncovered). Accepted: at 0:54.7 the camera push crops the rendered "CHIMNEY" label at the left edge (framing, not an overlay). qc_frames skimmed: nothing new.

## Editorial checks (frames every 2 s + spot frames at 0:01.8, 0:14.5, 0:16.9, 0:27.5, 0:43.5, 0:53.5, 0:55.5, 0:59)
- Hook: drone top-down on the pond, "DIVERS DEAD SINCE 1981" counter to 10 with the DISPUTED badge, line 1 inside 1 s. PASS
- Count framed as "at least ten" (narration) with DISPUTED badge; sign wording carries EYEWITNESS CLAIM (REPORTED per
  FACTCHECK #8); 260 ft carries EYEWITNESS CLAIM (#15); "CAUSE: UNCLEAR" matches L15; no cause speculation on screen. PASS
- No victims named anywhere on screen; no bodies — the recovery is two dim dots on the schematic; figures in S11 are faceless. PASS
- Warning sign is generic (no agency branding); "SCHEMATIC, NOT TO SCALE" on the section. PASS
- Timeline 1981 / 1999 CLOSED / 2003 REOPENED reads cleanly; "OCTOBER 2016" stamp. PASS
- Ends with "IN MEMORY OF EVERY DIVER LOST AT EAGLE'S NEST" and rises to S01's first frame for the loop. PASS

## Known minor weaknesses (accepted)
- S08: the caption "PREVENT YOUR DEATH." sits directly under the sign's own "GO NO FARTHER" line (rendered text), so the sign
  reads cramped for ~3 s; legible.
- S12 (0:42.4-0:46.5): the foreground diver is an abstract silver cylinder + fin in the caption third; the two torch dots carry
  the beat.
- S13: the "DUE BACK" timer runs 45:00 -> 70:00 (illustrative per FACTCHECK #13); the bubble rings are subtle.
- S14 end: the push-in crops the "CHIMNEY" label at the top edge.
- S02: trees are low-poly blobs; S11 crouch poses are stiff.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
