# QC REPORT — HAUNT-04 "The Ghost on the Raynham Hall Staircase" (Brown Lady photograph, 1936)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 36 MB; 57.33 s (haunted band 35-60 s); -14.6 LUFS; true peak -1.3 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 14 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original bm_george). Expected.

## Review cycle
- v1 FAIL:
  1. **S11 (0:43.8-0:47.8) — needs a shot re-render.** The 3D "ONE PLATE" label under the red frame renders twice: a red
     "ONE PLATE" offset half behind a black "ONE PLATE" (0:46-0:47.8), so the word reads as a misregistered double. Keep one
     label (the red frame's own text, placed on or just under the frame, not stacked on the black one). Re-render S11
     (~96 frames), then re-assemble.
  2. **S11 duplicated text (fixed in script.json).** The 2D card "WHAT SCEPTICS SAY / Double exposure: two images on one plate"
     (y 1150, shifted up by the caption guard) repeats the 3D board heading "WHAT SCEPTICS SAY" in the same frame and covers
     the STAIRS/FIGURE sheets. `SCRIPTS/HAUNT-04/script.json` S11 overlay[1] (card) **removed**; the THEORY badge stays.
  3. **S09 (0:37.0-0:40.4) (fixed in script.json).** The DOCUMENTED FACT badge (y 200) is covered by the Country Life document
     (only "DO" shows), and the document's typewriter (30 cps) is still on "Reprinted: Life," when the shot ends, so the
     Life date never appears. S09 overlay[0] (label) `params.y` 200 -> 1420; S09 overlay[1] (document) added `"cps": 45`
     (text complete at ~2.3 s of the 3.38 s shot).
  - Item 3 test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:40.0: clean, full text visible.
- Next: re-render S11, re-assemble (picks up the S09/S11 overlays), re-QC.

## Editorial checks (frames every 2 s + spot frames at 0:35.5, 0:39.8, 0:46.5)
- Hook: push up the oak staircase with the veiled figure on the landing, line 1 inside 1 s; EYEWITNESS CLAIM + DRAMATISATION. PASS
- The real photograph is never shown: S08 carries "[ REAL PHOTO DESCRIBED, NOT SHOWN ]" over our own recreated negative; no
  real Country Life / Life mastheads (plain typed document). PASS
- Labels follow FACTCHECK: Dorothy Walpole identification = FOLKLORE (+ DOCUMENTED FACT for the 1726 date); Marryat and the
  photographers' accounts = EYEWITNESS CLAIM; tampering check "(reported)"; double exposure / grease / movement = THEORY;
  "Nobody has ever proved which" = DISPUTED. PASS
- No portrait of Dorothy (empty gilt frame); the Brown Lady is a faceless veiled recreation; Marryat a back silhouette. PASS
- Dropped claims absent ("Provand saw nothing", "most famous ghost photo", direct quote, starvation tale). PASS
- Ends on the S01 staircase with the faint figure for the loop. PASS

## Known minor weaknesses (accepted)
- S02: the house is flat grey in fog; the trees are lost.
- S04: Marryat is a large black over-the-shoulder shape; the corridor is very dark.
- S07: the flash dish is a flat grey disc; the blowout frame (0:32) is pure white for a few frames.
- S08: the red safelight shows as a bright dot in the developing tray.
- S10/S12: the cards (THE CHECK / OTHER THEORIES) restate the narration; S12's greasy lens reads as a blurred blob.
- S14: the figure close to camera is bright and large for the loop flash.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).

## Shot fixes (v2)
- **S11 "ONE PLATE" doubled** — cause: the raised red text/frame (5 cm off the board) cast a crisp black shadow from the desk
  lamp, which read as a second, offset black "ONE PLATE". `BLENDER_PROJECTS/HAUNT-04/shots.py` S11: the red frame and its
  "ONE PLATE" label now have `visible_shadow = False`, so the label renders once (red, just under the frame). Nothing else changed.
- Verified: frames 60/90 at 540 px (/tmp/fix_HAUNT-04_S11) show one clean red "ONE PLATE"; preview S11 clean. Frame count 99 unchanged.
- Needs: production re-render of S11, then re-assembly (also picks up the S09/S11 overlay fixes).
