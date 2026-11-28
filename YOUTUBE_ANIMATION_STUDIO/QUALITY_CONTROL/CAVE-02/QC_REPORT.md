# QC REPORT — CAVE-02 "13 Trapped 4 km Inside a Flooded Cave" (Tham Luang, 2018)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 39 MB; 62.70 s (cave band 50-72 s); -14.5 LUFS; true peak -1.1 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 20 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_michael). Expected.

## Review cycle
- v1 FAIL (overlays only — the rendered frames are fine, no re-render needed). Edits in `SCRIPTS/CAVE-02/script.json`:
  1. **S08 (0:22.3-0:27.1) overlay collision:** the stamp "2 JULY 2018 / JOHN VOLANTHEN + RICK STANTON (UK)" (y 170) is typed
     straight across the map title "THAM LUANG" and its subtitle line; both are unreadable for the whole shot. S08 overlay[1]
     (stamp) `params.y` 170 -> 1420 (over the contour background below the captions).
  2. **S08 stray "~":** the map subtitle read "~4 KM: ENTRANCE TO LEDGE". S08 overlay[0] (map) `text` ->
     "THAM LUANG\nABOUT 4 KM: ENTRANCE TO LEDGE" (matches "about four kilometres" in L01 / FACTCHECK #2).
  - Test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:25.8: clean.
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC.

## Editorial checks (frames every 2 s + spot frames at 0:27.4, 0:28.2, 0:28.9, 0:45)
- Hook: flooded passage + "KM INSIDE (APPROX.)" counter, line 1 inside 1 s; torch breaks the surface by 0:06. PASS
- The boys and coach are faceless silhouettes (no names, no ages); Saman Kunan is a distant silhouette from behind, his death a
  torch glow fading on an empty line; IN MEMORY card (S13) and closing "IN MEMORY OF SAMAN KUNAN" (S19). No body. PASS
- Sedation shown as DOCUMENTED FACT + DISPUTED with "HOW DEEPLY SEDATED: DISPUTED"; no ketamine/doctor named. PASS
- Dates match FACTCHECK: 23 June, 2 July, 6 July, 8/9/10 July (4 / 4 / 4 + coach). "13 IN · 13 OUT" middle dot renders. PASS
- Labels: DOCUMENTED FACT on fact shots, DRAMATISATION on recreations (S06, S09, S16). PASS
- Ends on S01's flooded passage for the loop. PASS

## Known minor weaknesses (accepted)
- S15 (0:42.5-0:46.2): the sedated child + mask reads as abstract spheres and a bowl; clinical and hard to parse.
- S16: the divers carrying a boy read as dark shapes behind a bright torch (weakest shot per the animation notes).
- S09 (0:27.1-0:29.1): very dark; the last ~0.8 s is a flat green silt-out.
- S14: the diagram's "FLOODED" label is cropped at the left edge during the pan.
- S03/S04: the 13 figures are small; S05 jungle is low-poly blobs.
- S15: "HOW DEEPLY SEDATED: DISPUTED" sits over the 3D figure.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
