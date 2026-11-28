# QC REPORT — SCUBA-05 "He Dived 332 m. Getting Back Took Nearly 15 Hours" (Ahmed Gabr, Dahab 2014)

VERDICT: FAIL (v2, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 33 MB; 51.96 s (scuba band 40-65 s); -14.5 LUFS; true peak -1.1 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 18 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_onyx). Expected.

## Review cycle
- v1 FAIL (overlays only — the rendered frames are fine, no re-render needed). Edits in `SCRIPTS/SCUBA-05/script.json`:
  1. **S07 (0:16.6-0:18.9) overlay on the 3D tag + duplicated text:** the depth gauge's "332m / RECORD DEPTH" readout lands
     on top of the 3D rope tag "332 m" (the gauge digits cover the tag's "m"). S07 depth overlay **removed** (overlay list now
     empty); the tag, the caption and S08's "332 m > 330 m" carry the number.
  2. **S09 (0:21.1-0:24.7) duplicated text:** the card "DEEPEST SCUBA DIVE / 2005 318.25 m / 2014 332.35 m" repeats the 3D bar
     chart, which already shows 2005 / 2014 / 318.25 / 332.35. Card **removed**; the DOCUMENTED FACT badge stays.
  3. **S12 (0:30.3-0:34.2) stray "~":** timeline sub-label "~15 h" -> "nearly 15 h" (`params.events[2][1]`).
  4. **S13 (0:34.2-0:37.4) overlay asserts the dropped figure:** the timer counted to "TOTAL 14 HRS" while the narration says
     "Nearly fifteen hours" (FACTCHECK L02/L13 replaced the concept's "14 hours" with "nearly 15"). Timer `text` "TOTAL" ->
     "NEARLY", `params.to` 14 -> 15 (ends on "NEARLY / 15 HRS").
  5. **S14 (0:37.4-0:41.1) overlays hidden:** the DISPUTED badge (y 200) and the "2020" stamp (default y 300) are both covered by
     the ANONYMOUS document (only "DIS" / "202" show). Badge `params.y` 200 -> 1420; stamp `params` {} -> {"y": 1530}
     (both below the captions).
  6. **S16 (0:42.9-0:46.4) duplicated text:** the card "REVIEW CONCLUDED / 332.35 m / CONFIRMED" repeats the 3D stamped report
     ("332.35 m" + green "CONFIRMED"). Card `params.header` -> "GUINNESS REVIEW", `text` -> "Record upheld" (GWR continues to
     recognise Gabr as record-holder, FACTCHECK L16-L17; y 1420 unchanged).
  - Test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:33.8, 0:37.35, 0:39.5, 0:45.5: clean.
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC.
- v2 FAIL (overlay only — re-assembly needed). QC_AUTO fresh: 51.96 s, -14.6 LUFS, true peak -1.6 dBTP.
  - Fixed: S07 depth overlay gone, 3D "332 m" tag clean (0:17.8); S09 duplicate card gone (0:23.0); S12 "nearly 15 h" (0:32.5); S14 DISPUTED badge + "2020" stamp below the captions (0:39.5); S16 card "GUINNESS REVIEW / Record upheld" (0:45.5).
  - **Still wrong — S13 timer (0:34.2-0:37.4).** The timer reads "NEARLY / 14 HRS" for the whole visible hold (frame 0:37.0) and only flips to 15 during the fade-out (0:37.2-0:37.35), because `ov_timer` truncates with int() and the ease only reaches `to` at the very end. Fixed in `SCRIPTS/SCUBA-05/script.json` S13 overlay[0] (timer) `params.to` 15 -> 15.9: it now shows "15 HRS" from ~1.9 s of the 3.28 s shot (checked with overlays.ease; never shows 16).
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC at 0:36.5.

## Editorial checks (frames every 2 s + spot frames at 0:04.4, 0:17.8, 0:32.5, 0:39.5)
- Hook: "DOWN" clock racing to 12:00 on the descent, then "UP ... NEARLY 15 HOURS"; line 1 inside 1 s. PASS
- Numbers match FACTCHECK: 12 min down, nearly 15 h up, 18 Sep 2014, 332 m (332.35 on the chart), 2005 Gomes mark 318.25 m
  (no name on screen, no Bernabé), "332 m > 330 m" for the Eiffel Tower, "dozens" of tanks (no count on screen). PASS
- The 2020 allegation is shown as an anonymous CLAIM with DISPUTED; the Guinness outcome is DOCUMENTED FACT. No critic
  identity, no Gabr counter-claims. PASS
- Divers are faceless silhouettes; the bends are an x-ray diagram with bubbles, no injury. PASS
- Ends on S01's set with "00:00" DOWN for the loop. PASS
- Pre-publish (from FACTCHECK): re-check the Guinness record page before upload ("The record stands").

## Known minor weaknesses (accepted)
- S02: the "UP" timer reaches "14 HRS" for ~0.2 s before "NEARLY 15 HOURS" replaces it.
- S05: the depth gauge (eased) runs ahead of the passing 100/200/300 m plates (e.g. "270m" beside the 200 m plate at 0:14).
- S17: the rope tag in frame reads "330 m" (partly under the caption) while the overlay says "332 m".
- S03: the map card is a plain dark polygon with almost no route; the stamp carries "RED SEA / 18 SEP 2014".
- S13: the surfacing diver's head is a dark blob; window reflections smear the foreground water.
- S06 glove is blocky; S18 loop seam particles differ slightly.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
