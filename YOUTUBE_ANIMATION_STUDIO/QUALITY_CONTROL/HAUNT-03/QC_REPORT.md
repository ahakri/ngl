# QC REPORT — HAUNT-03 "Don't Stop for Her on Archer Avenue" (Resurrection Mary)

VERDICT: PASS (v2, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 30 MB; 47.50 s (haunted band 35-60 s); -14.5 LUFS; true peak -1.4 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 15 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_onyx). Expected.

## Review cycle
- v1 FAIL (overlays only — the rendered frames are fine, no re-render needed). All edits in `SCRIPTS/HAUNT-03/script.json`:
  1. **S02 (0:05.0-0:07.6):** the DOCUMENTED FACT badge (y 200) is drawn over the map subtitle "south-west of Chicago"
     ("DOCUMENTED FAC|south-west..."). S02 overlay[0] (label) `params.y` 200 -> 1420 (below the captions).
  2. **S11 (0:31.1-0:34.2):** the 2D card "THE CEMETERY'S ANSWER" (y 1150, shifted up by the caption guard) sits on top of the
     3D corkboard card ("REVERSED INTO THE FENCE" + truck icon) and repeats it. S11 overlay[1] (card): `params.y` 1150 -> 1450
     (below the captions, over the bottom margin of the 3D card) and `text` "A truck backed into the fence.\nNo evidence of a
     ghost." -> "No evidence of a ghost." (the truck/fence half is already on the 3D card; header unchanged; the remaining line
     is the officials' statement per FACTCHECK L11 / R1).
  3. **S12 (0:34.2-0:38.2):** the FOLKLORE badge (y 200) is hidden behind the "VANISHING HITCHHIKER" paper (only "FO" shows),
     and the paper's typewriter (30 cps) is still typing the last line ("Told across ma...") when the shot fades out.
     S12 overlay[0] (label) `params.y` 200 -> 1420; S12 overlay[1] (document) added `"size": 42, "cps": 45` (text now complete
     at ~2.9 s of the 4.06 s shot, and the first line no longer wraps).
  - All three test-composited with PIPELINE/overlays.py + compose.avoid_captions on frames 0:06.5, 0:32.8, 0:37.2: clean.
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC.
- v2: re-assembled from the existing frames. PASS. QC_AUTO fresh: 47.50 s, -14.6 LUFS, true peak -1.7 dBTP. Frames checked at 0:06.5 (badge below the captions, map subtitle clear), 0:32.8 ("THE CEMETERY'S ANSWER / No evidence of a ghost." below the 3D truck card, no overlap) and 0:37.2, 0:37.9 (FOLKLORE badge visible; Vanishing Hitchhiker paper fully typed, last line complete). qc_frames skimmed: nothing new.

## Editorial checks (frames every 2 s + spot frames at 0:06.5, 0:15, 0:32.8, 0:37.8)
- Hook: driver POV on the wet road, pale figure on the verge, line 1 inside 1 s. PASS
- Every legend beat is labelled: Palus = EYEWITNESS CLAIM ("He said"), 1976 bars = DISPUTED, cemetery statement = DOCUMENTED
  FACT, legend type = FOLKLORE; recreations carry DRAMATISATION. "marks like handprints" only, no "scorched". PASS
- No candidate "Mary" is named or pictured; S13 shows blank headstones. No house number on the address card. PASS
- Mary is a faceless pale mannequin; Palus a faceless silhouette; cemetery gate is generic. No death imagery. PASS
- No overlay asserts the dropped beats (hit-and-run, "she points at the gates", Damen-house outcome). PASS
- Ends on S01's road for the loop ("But on Archer Avenue, ..."). PASS

## Known minor weaknesses (accepted)
- S02: the map is a plain green square with a diagonal line; it gives no sense of Chicago (the title does the work).
- S05: the DRAMATISATION badge touches the "B" of the 3D BALLROOM sign.
- S06: the address card overlaps the passenger mannequin's arm.
- S01/S15: the woman on the verge is tiny (~2.5% of frame) for the first seconds.
- S10: the handprint smudges read as blobs; S13 headstones are near-silhouettes.
- S08: the vanish frames (0:21-0:23) are very dark.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
