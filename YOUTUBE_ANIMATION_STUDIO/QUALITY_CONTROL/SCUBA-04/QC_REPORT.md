# QC REPORT — SCUBA-04 "A Humpback Closed Its Mouth Around Him" (Michael Packard, Cape Cod 2021)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 31 MB; 49.29 s (scuba band 40-65 s); -14.5 LUFS; true peak -1.2 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 17 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_michael). Expected.

## Review cycle
- v1 FAIL:
  1. **S01 (hook, 0:00-0:04.7) — needs a shot re-render.** The narration lands "The next, everything went black" at ~0:02.8-0:04,
     but the frame never goes black: after the f65 "blackout" the sand, the rock and the diver (tank highlight, yellow mask
     rim, limbs) stay clearly lit in dim green until the cut (frames 0:02.9, 0:03.3, 0:03.9). The humpback also never reads
     before that (only a shadow). The key beat of the hook does not match its line. Fix: at f65 the occluder must really kill
     the light — world/ambient + caustic/sun + bounce off (or a hard cut to a near-black frame with only the faint bubble leak),
     so 0:02.8-0:04.7 is essentially black. Re-render S01 (113 frames), keep frame 1 unchanged (S17 loops onto it), then
     re-assemble.
  2. **S11 (0:28.7-0:30.6) stray "~" (fixed in script.json).** "THROAT ~ FIST-SIZED" — the tilde (already a fallback for "≈")
     reads as leftover markup. `SCRIPTS/SCUBA-04/script.json` S11 overlay[0] (text) `text` -> "THROAT ABOUT FIST-SIZED\n(EXPERT
     ESTIMATE)" (y 1420, size, colour unchanged).
  3. **S02 (0:04.7-0:07.2) overlay on overlay + duplicated text (fixed in script.json).** The stamp "PROVINCETOWN, MA / 11 JUN
     2021" (y 300) is typed inside the map card, on top of the route's end pin, repeating the map subtitle "Provincetown,
     Massachusetts". S02 overlay[1] (stamp): `text` -> "11 JUNE 2021", `params.y` 300 -> 1420 (below the captions).
  - Items 2-3 test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:06.5 and 0:29.9: clean.
- Next: re-render S01, re-assemble (picks up the S02/S11 overlays), re-QC.

## Editorial checks (frames every 2 s + spot frames at 0:02.5, 0:02.9, 0:03.3, 0:03.9, 0:04.2, 0:05.5, 0:06.8, 0:30)
- Never says or shows "swallowed"; "CAN'T SWALLOW" carries DOCUMENTED FACT; "Experts think ... by accident" carries THEORY
  with "AN ACCIDENT?"; his thoughts (shark, his sons) carry EYEWITNESS CLAIM; timer "(HIS ESTIMATE)". PASS
- No direct quotes, no sons' ages, no dislocated knee / broken leg; injury card "SOFT-TISSUE DAMAGE / NO BROKEN BONES
  (REPORTED)" matches FACTCHECK L16. PASS
- Packard and Mayo are faceless figures; no injury shown. PASS
- Name cards at y 1420 clear of the captions; depth gauge in feet (0-45 ft). PASS
- S10/S11 x-ray diagrams (throat vs fist vs diver) read clearly. PASS
- Ends on the S01 set with the whale's shadow sweeping the sand (loop). PASS

## Known minor weaknesses (accepted)
- S02: the map subtitle "Provincetown, Massachusetts" is blue on the pale-teal background (low contrast).
- S05/S08/S09 inside the mouth are very dark; the diver's head reads large.
- S13: the foam ring around the breaching head reads as a flat plate.
- S07: the fish school is faint; S03 diver small in the wide.
- S11: the fist icon is blocky.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
