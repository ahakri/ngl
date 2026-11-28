# QC REPORT — MURDER-06 "The Ghost Ship's Creepiest Detail Was Fiction" (Mary Celeste, 1872)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 47 MB; 75.04 s (murder band 55-82 s); -14.5 LUFS; true peak -1.1 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 19 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_michael). Expected.

## Review cycle
- v1 FAIL (overlays only — the rendered frames are fine, no re-render needed). Edits in `SCRIPTS/MURDER-06/script.json`:
  1. **S05 (0:16.3-0:19.0):** "LIFEBOAT: GONE" (text, y 1470) is drawn over the 3D transom lettering "MARY CELESTE", so the
     ship's name — the subject of the line — is unreadable under it. S05 overlay[0] `params.y` 1470 -> 420 (sky/sail area).
  2. **S09 (0:28.7-0:32.4):** "STILL SEAWORTHY" (y 1450) sits on the hull cross-section's bottom curve and its "3.5 FT" water
     line. S09 overlay[1] `params.y` 1450 -> 1650 (open sea area below the diagram).
  3. **S11 (0:34.6-0:40.9):** the DOCUMENTED FACT badge (y 200) is covered by the Cornhill Magazine document (only "DO" shows).
     S11 overlay[1] (label) `params.y` 200 -> 1420.
  4. **S06 (0:19.0-0:21.5) stray "~":** card text "~6 months of food and water" -> "6 months of food and water" (narration and
     FACTCHECK L06: "six-month supply").
  - Test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:17.6, 0:18.3, 0:31.5, 0:38.0: clean.
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC.

## Editorial checks (frames every 2 s + spot frames at 0:18.3, 0:31.5, 0:70.1)
- Hook: the brigantine drifting out of fog with nobody aboard, line 1 inside 1 s; DOCUMENTED FACT. PASS
- The legend is boxed as FOLKLORE (sepia breakfast set, "THE LEGEND", "FICTION", "MARIE CELESTE" board) and kept apart from the
  record (DOCUMENTED FACT on the 1872 facts). "Doyle invented the tea" is not claimed; the card says "added in later
  retellings". PASS
- Theories (fumes / broken pump) carry THEORY with question marks; the lifeboat departure carries DRAMATISATION with "may have". PASS
- Dropped details absent (red-oak barrels, chronometer/sextant, piracy/mutiny rulings); crew as "Briggs family + seven crew". PASS
- No bodies: the lost are a faceless lifeboat silhouette and a lantern on a plank; names only on the NEVER FOUND card. PASS
- Numbers/dates: 4 DEC 1872 Dei Gratia, 1,701 barrels, 3.5 FT (42 in), Cornhill January 1884, 25 NOV -> 4 DEC "9 DAYS". PASS
- Ends on the S01 drifting-ship frame for the loop. PASS

## Known minor weaknesses (accepted)
- S05: the caption still crosses the 3D "MARY CELESTE" lettering for ~1 s while the camera is on the transom.
- S02/S10: the tea steam reads as blocky soft columns.
- S04 map: plain dark polygon for the Azores; the Dei Gratia stamp carries it.
- S18: the "Sources in description" stamp is small grey mono on the grey deck (low contrast).
- S13: sepia-to-cold grade leaves the frame very dark.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
