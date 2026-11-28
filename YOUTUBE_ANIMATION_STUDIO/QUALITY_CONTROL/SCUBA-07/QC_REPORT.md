# QC REPORT — SCUBA-07 "Sponge Divers Found a 2,000-Year-Old Machine" (Antikythera mechanism)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 35 MB; 53.88 s (scuba band 40-65 s); -14.7 LUFS; true peak -1.2 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 14 shots rendered (1327 frames).
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original bm_george). Expected.

## Review cycle
- v1 FAIL (overlay only, cosmetic — the rendered frames are fine, no re-render needed):
  1. **S13 (0:45.3-0:49.6) clipped text + stray "~".** The timeline's end labels run off the frame: the first label "~100 BC" touches
     the left edge with a leftover-markup tilde, and the last sub-label "astronomical clocks" is cut at the right edge
     ("astronomical clock", frames 0:47.5, 0:49.0) — same class as HAUNT-05 S03. `SCRIPTS/SCUBA-07/script.json` S13 overlay[0]
     (timeline) `params.events` -> `[["100 BC", "approx."], ["...", ""], ["1300s", "clocks"]]` (both ends now fit inside the frame;
     "approx." keeps the approximation — FACTCHECK #1/#13: wreck c. 70-60 BC, mechanism possibly older; 14th-century clocks).
  - Test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:48.0 and 0:49.0: clean.
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC at 0:49.

## Editorial checks (frames every 2 s + spot frames at 0:07.0, 0:44.0, 0:47.5, 0:49.0)
- Hook: the corroded lump on the seabed + "2,000 YEARS OLD" + line 1 inside 1 s; gears revealed at 0:05. PASS
- Numbers match FACTCHECK: ~50 m depth gauge ("around 50 metres"), 1900 storm / 1901 salvage, "1 diver dead (the bends) /
  2 divers paralysed", Athens 1902, 2005 CT scans, Sun + Moon positions / eclipse prediction, ">1,000 years". PASS
- The dead diver is not depicted; helmet divers are faceless mannequins. PASS
- Ends on the lump on the dark seabed, looping to S01. PASS

## Known minor weaknesses (accepted)
- S03 (0:05.3-0:10.5): the map card is semi-transparent; two crew silhouettes show through it.
- S12 (0:41.9-0:45.3): the WHAT IT DID card covers the bottom edge of the bronze dial.
- S13: a 3D gear and the clock are cropped at the frame edges during the move.
- S10: the CT-scan reveal is a bright white oval for ~2 s (by design).
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
