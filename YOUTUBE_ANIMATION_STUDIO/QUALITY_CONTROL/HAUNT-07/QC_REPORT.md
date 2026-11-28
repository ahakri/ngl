# QC REPORT — HAUNT-07 "Drivers Keep Reporting They Hit Her" (Blue Bell Hill, Kent)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render 46079759846)
- 1080x1920, 24 fps, H.264 ~5.1 Mbps, 31 MB; 48.33 s (haunted band 35-60 s); -14.6 LUFS; **true peak -0.9 dBTP (auto FAIL,
  ceiling -1.0)**. Re-assembly for the true peak was already requested (ci_render_request.json, reuse_frames, 01:38 UTC).
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 13 shots rendered (1191 frames).
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original bm_george). Expected.

## Review cycle
- v1 FAIL (true peak + overlays — the rendered frames are fine, no re-render needed). Edits in `SCRIPTS/HAUNT-07/script.json`:
  1. **S03 (0:04.4-0:09.0):** the DOCUMENTED FACT badge (y 120) is drawn over the map title ("DOCUMENTED FACT|UE BELL HILL",
     frame 0:06.5). S03 overlay[2] (label) `params.y` 120 -> 1420 (below the captions, over the dark road).
  2. **S10 (0:32.2-0:36.3) 2D card on the 3D corkboard:** the "WHAT SCEPTICS SAY / A road-ghost story told worldwide
     (folklorists)" card covers the red-string map sheet and repeats the caption ("told on roads worldwide"); the 3D cards
     VANISHING HITCHHIKER / PHANTOM ON THE ROAD already carry the beat (same class as HAUNT-04/05/06 S11). S10 overlay[0] (card)
     **removed**; the FOLKLORE badge stays.
  3. **S11 (0:36.3-0:40.5):** the DISPUTED badge (y 200) covers the start of the LOCAL ACCOUNTS document's first line
     ("DISPUTED|GHTINGS BEGAN", frame 0:37.8). S11 overlay[1] (label) `params.y` 200 -> 1420.
  - Test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:06.5 and 0:39.0: clean.
  - **Important:** these script.json edits were made after the 01:38 re-assembly request, so that run (true peak only) will not
    include them unless they are committed first. **Needs one more re-assembly** (with the -1 dBTP ceiling) that picks up these
    overlays; then re-run qc_check and re-QC at 0:06.5, 0:34, 0:37.8.
  - The frames themselves are fine: once the overlay fixes and true peak are in, the verdict is expected to be PASS pending a
    look at the re-assembled file.

## Editorial checks (frames every 2 s + spot frames at 0:06.5, 0:16.5, 0:20, 0:33, 0:34.5, 0:35.8, 0:37.8)
- Hook: a pale figure in the headlights + line 1 ("A driver says he hit a girl on this hill") inside 1 s; EYEWITNESS CLAIM +
  DRAMATISATION badges. PASS
- Every sighting beat is badged EYEWITNESS CLAIM; the sceptic beat FOLKLORE; the start date DISPUTED (struck-through 1930s?/
  1960s?/1970s? -> "NOBODY AGREES"); "None of these reports has ever been confirmed" on S12. PASS
- No impact, no injury, no body: the girl is a distant silhouette, the blanket scene is a dark shape under a torch. PASS
- "1974 / bricklayer" and "NOVEMBER 1992 / motorists" match the narration. PASS
- Ends on the headlights at the hill (loop to S01). PASS

## Known minor weaknesses (accepted)
- S05-S09 (0:14.7-0:32.2) are very dark; the police/blanket beats read mostly from the captions and badges.
- S10 (0:34.5): during the pan, a third 3D card peeks out behind the VANISHING HITCHHIKER card ("PH" over "SHING") for ~1 s.
- S12: rain streaks and bokeh make the frame busy but readable.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
