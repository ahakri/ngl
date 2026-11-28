# QC REPORT — CAVE-07 "The Man Who Wrote Cave Diving's Rules Tried for 1,000 ft" (Sheck Exley, Zacatón, 1994)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 38 MB; 57.25 s (cave band 50-72 s); -14.6 LUFS; true peak -1.3 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 17 shots rendered (1415 frames).
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_michael). Expected.

## Review cycle
- v1 FAIL (overlays only — the rendered frames are fine, no re-render needed). Edits in `SCRIPTS/CAVE-07/script.json`:
  1. **S14 (0:46.5-0:49.1) the key line never appears.** The INCIDENT document types at 30 cps and is still on line 3 when the
     shot fades: "CAUSE: ~~NARCOSIS?~~" is half typed and "HPNS?" and "UNDETERMINED" (the point of L14 "never determined")
     never show (frames 0:47.5, 0:48.7). S14 overlay[0] (document) added `"cps": 100` (all four lines complete at ~1.2 s of
     the 2.66 s shot; struck-through markup renders correctly).
  2. **S06 (0:16.6-0:20.4) overlay on the 3D log list.** The "CAVE DIVES LOGGED" counter and "FIRST EVER" are drawn straight over
     the rendered DIVE 09xx rows, so the rows read "DIVE 0997 1,000 SUMP" / "DIVE 099 FIRST EVER CAVE" (frames 0:17.2-0:20.2);
     the counter also duplicates the 3D list, which itself ends on "DIVE 1000". S06 overlay[0] (counter) **removed**; "FIRST
     EVER" `params.y` 800 -> 1450 and `"start": 2.0` (appears below the captions once the list has stopped scrolling, on the
     empty teal area under "DIVE 1000").
  3. **S09 (0:30.2-0:35.1) invented number without a label.** The "GAS RESERVE" counter runs 100 -> 40 with no unit and no source;
     FACTCHECK #10 marks the gas-consumption mechanism as REPORTED and gives no figure. Added a DRAMATISATION badge
     (`{"type": "label", "text": "DRAMATISATION", "params": {"y": 200}}`) so the gauge reads as illustrative. (Alternative if
     the editor prefers: remove the GAS RESERVE counter.)
  - Test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:19.2, 0:31.0, 0:47.9, 0:48.4: clean, text complete.
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC at 0:19.5, 0:31, 0:48.

## Editorial checks (frames every 2 s + spot frames at 0:17.2, 0:18.0, 0:18.8, 0:19.2, 0:19.8, 0:20.2, 0:31, 0:34.5, 0:36.5, 0:47.5, 0:48.7, 0:49.8)
- Hook: two lights dropping into the shaft + "TARGET 1,000 FT" gauge + line 1 inside 1 s. PASS
- Numbers match FACTCHECK: 925 ft turn for Bowden; "WORLD RECORD (since broken)"; "First published 1979"; age 45; Sheck Exley
  Award (NSS Cave Diving Section) for 1,000 safe cave dives. Exley's own depth is never stated (FACTCHECK note). PASS
- Exley's death: a light that never comes back, the line hauled up with an outline figure wrapped in it; no body detail. PASS
- Cause of death shown as struck-through guesses + "UNDETERMINED" (after fix 1). PASS
- Ends on the counter "SAFE CAVE DIVES 1,000" over the shaft, looping to the opening. PASS

## Known minor weaknesses (accepted)
- S03: the map card's land shape is abstract; "TAMAULIPAS, MEXICO" stamp fine.
- S10: "WORLD RECORD" sits over the upper shaft diagram (legible thanks to the stroke).
- S07: the SAFETY HANDBOOK paper is mostly empty (short text on a large page).
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
