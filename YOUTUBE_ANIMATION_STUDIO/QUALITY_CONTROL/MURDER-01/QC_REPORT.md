# QC REPORT — MURDER-01 "Nine Hikers Cut Their Tent Open" (Dyatlov Pass)

VERDICT: PASS (v2, 2026-11-27)

## Automated (QC_AUTO.json)
- 1080x1920, 24 fps, H.264 ≤5 Mbps, 44 MB; 67.5 s (murder band 55–82 s); ≈ -14 LUFS; no black/frozen/silent gaps; all 21 shots fully rendered.

## Review cycle
- v1 FAIL (cosmetic): map subtitle overlapped captions (S03); duplicate 2D text over the 3D theory board (S07/S08) cluttered the frame.
- Fix: overlays.py map subtitle moved between title and card; removed duplicate S07/S08 text overlays (3D cards/stamps carry them). Re-composed from existing renders.
- v2: PASS.

## Editorial checks
- Hook lands in 1.5 s ("Nine hikers cut their own tent open. From the inside."). PASS
- Theories stamped THEORY / NO EVIDENCE, not "ruled out"; 2021 model labelled THEORY; scientists' "not solved" caveat kept. PASS
- No bodies, injuries described only in text card; hikers faceless. PASS
- Ends on comment prompt + loop back to the tent. PASS

## Re-voice (2026-11-27, owner's choice: narrator voice am_adam, "Voice 03")
- Narration re-synthesised in am_adam with the timing lock (AUDIO/MURDER-01/timings_ref.json): every line starts at its original time, so
  picture, shot cuts and overlay cues are unchanged; captions rebuilt from the new word timings; video re-assembled from the existing frames.
- Automated QC after re-voice: PASS (-14.2 LUFS, -1.4 dBTP); caption timing consistency check: 0 problems.
- VERDICT stays PASS. Not machine-checkable here: pronunciation and delivery of the new voice were not auditioned by ear in this
  container (no audio playback) — owner to confirm by listening.
