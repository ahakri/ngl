# QC REPORT — HAUNT-01 "The Enfield Tapes"

VERDICT: PASS (v1, 2026-11-27)

## Automated (PIPELINE/qc_check.py → QC_AUTO.json)
- 1080x1920, 24 fps, H.264 8 Mbps cap, AAC 192k; duration 56.5 s (haunted band 35–60 s).
- Integrated loudness ≈ -14 LUFS (Shorts target), true peak < -1 dBFS.
- No black segments mid-video, no frozen segments, no silence gaps; all 15 shots fully rendered (1,355 frames).

## Visual / editorial review (director, qc_frames.png every 2 s)
- Hook: frame 1 is the bedroom with recorder; "ENFIELD, 1977" + line 1 land inside 1.5 s. PASS
- Every claim shot carries a fact badge (DOCUMENTED FACT / EYEWITNESS CLAIM / DRAMATISATION). PASS
- Sceptic beat present (spoon-bending camera, SPR ventriloquism suspicion, ~2% admission). PASS
- Recording described, not reproduced ("[ RECORDING DESCRIBED, NOT PLAYED ]"). PASS
- No real faces; all people are faceless silhouettes; house number withheld. PASS
- Captions word-synced, no overlay collisions after caption-avoidance fix. PASS
- Loop ending returns to the opening bedroom framing. PASS
- Fact-check: QUALITY_CONTROL/HAUNT-01/FACTCHECK.md (snippet-based; open SPR/Wikipedia pages before upload).

## Known minor weaknesses (accepted, not blocking)
- Whip transitions blend 3 offset copies; looks smeary for ~0.2 s on the evidence-board cut.
- Investigators' tape-notes document is sparse ("Voice") during its typewriter reveal.
- Recorder macro deck is dark; second reel partly cropped (S06).

## Re-voice (2026-11-27, owner's choice: narrator voice am_adam, "Voice 03")
- Narration re-synthesised in am_adam with the timing lock (AUDIO/HAUNT-01/timings_ref.json): every line starts at its original time, so
  picture, shot cuts and overlay cues are unchanged; captions rebuilt from the new word timings; video re-assembled from the existing frames.
- Automated QC after re-voice: PASS (-14.5 LUFS, -1.1 dBTP); caption timing consistency check: 0 problems.
- VERDICT stays PASS. Not machine-checkable here: pronunciation and delivery of the new voice were not auditioned by ear in this
  container (no audio playback) — owner to confirm by listening.
