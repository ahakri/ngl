# QC REPORT — SCUBA-08 "Shackleton's Ship Was Found a Century Later, 3 km Down" (Endurance, Weddell Sea)

VERDICT: FAIL (v1, 2026-11-28) — audio only; frames PASS, verdict pending the re-assembled file

## Automated (QC_AUTO.json, CI render 46089116417)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 33 MB; 50.38 s (scuba band 40-65 s); -14.5 LUFS; **true peak +0.7 dBTP (auto FAIL, ceiling
  -1.0)** — this run predates the 0.80 true-peak limiter fix.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 14 shots rendered.
- Narrator: am_adam (studio voice).

## Review cycle
- v1 FAIL (true peak only). The rendered frames and overlays are fine: no script.json change, no re-render.
  - **Needs re-assembly** from the existing frames with the current limiter (true peak <= -1.0 dBTP), then re-run qc_check.
    If the re-assembled QC_AUTO.json is PASS, the verdict can go straight to PASS (v2) after a quick contact-sheet check.

## Editorial checks (frames every 2 s + spot frames at 0:09.5, 0:15.8, 0:29.8, 0:30.6, 0:33, 0:40)
- Hook: the ENDURANCE stern lettering + star + "SANK 1915" + line 1 inside 1 s ("You can still read its name"). PASS
- Numbers match FACTCHECK: 28 men survived (counter 0 -> 28, DOCUMENTED FACT), 1915 -> 2022, 2019 search, Endurance22 expedition,
  5 March 2022, "ABOUT 4 MILES" from Worsley's position, 3,008 m, upright and intact, Antarctic Treaty Historic Site and
  Monument No. 93, funeral 5 March 1922 / found 5 March 2022. PASS
- The wood-eater line is attributed ("Experts: ..."), matching FACTCHECK #13 (attributed). PASS
- Crew are distant silhouettes; nothing taken from the wreck is shown. PASS
- Ends on the stern lettering with the funeral/found dates, looping to S01. PASS

## Known minor weaknesses (accepted)
- S03: the "WEDDELL SEA / 1915" stamp repeats the S02 map title.
- S12: the tube-shaped "wood-eater" creatures are shown on the seabed while the line says they do not live there (reads as an
  illustration of "elsewhere"; the card carries the meaning).
- S09 (0:29.1-0:31.1) is short and dark; the stamp and badge carry the date.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
