# QC REPORT — CAVE-04 "Stuck Upside Down With No Way to Back Out" (John Jones, Nutty Putty Cave 2009)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 32 MB; 51.29 s (cave band 50-72 s, near the lower edge); -14.7 LUFS; true peak -1.3 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 17 shots rendered (1273 frames).
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_onyx). Expected.

## Review cycle
- v1 FAIL:
  1. **S11 (anchor gives way, 0:29.3-0:31.7) — needs a shot re-render.** From ~0:30.5 to the end of the shot the frame is an
     oval cloud of chunky white specks on black: the dust burst fills the frame in front of the anchor, the anchor/pulley/rock
     chunk are not visible falling, and only a stray slack-rope curve remains. The key beat ("an anchor gave way") reads as a
     particle blob (same defect class as CAVE-01 S12 v1). Fix: finer, sparser dust kept away from the lens and behind/around the
     tearing anchor so the falling anchor + pulley stay readable; keep the hard shake. Re-render S11 (~58 frames), then re-assemble.
     Frames checked at 0:29.5, 0:30.2, 0:30.8, 0:31.3.
  2. **S14 timer label (fixed in script.json).** The timer read "ABOUT 27 HRS" while the narration says "After more than 27
     hours" — FACTCHECK.md #13 explicitly changed "about 27" to "more than 27" (sources give ~27 h and "nearly 28 hours").
     Changed `SCRIPTS/CAVE-04/script.json` S14 overlay[0] (type timer) `text` "ABOUT" -> "MORE THAN" (params unchanged; reads
     "MORE THAN / 27 HRS"). Overlay-only; needs re-assembly.
- Next: re-render S11, re-assemble (picks up the S14 overlay), re-QC.

## Editorial checks (frames every 2 s + spot frames)
- Hook: line 1 over the crack with the boots/legs inside 1.5 s. PASS (weak image, see below).
- John Jones appears only as boots/legs, a faceless figure from behind, gloved hands and a grey diagram outline; his death is a
  lamp icon going out. No body, no face, no injury. PASS
- Overlays clear of the captions: "CAN'T TURN / CAN'T BACK OUT", "UPSIDE DOWN", "HOPE" at y 420; cards at 760/900; stamps at 300. PASS
- "reports say" hedge kept in L11 and no overlay asserts the failed part; "DECEMBER 2009" stamp backed by FACTCHECK #15;
  S13 timer marked "(APPROX.)". PASS
- Fact labels: DOCUMENTED FACT / DRAMATISATION on the relevant shots. PASS
- Ends on the flush concrete slab at dawn with "IN MEMORY OF JOHN EDWARD JONES". PASS

## Known minor weaknesses (accepted)
- S01: the legs read as pale rectangular posts and the dust reads like stars; the hook image is abstract.
- S02: the 3D red "X" at the bottom of the crack touches the caption ("BACK") at 0:04.5.
- S08: the last ~1 s (0:24-0:25) looking into the crack is almost black.
- S14: the IN MEMORY card sits over the diagram crack/outline figure.
- S15 (0:40.7-0:43.8): very dark; the crawling rescuer reads as a pale mannequin shape.
- S04: the cave opening barely reads in the night shot; the stamp carries the beat.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).

## Shot fixes (v2)
- **S11 (anchor gives way)** — `BLENDER_PROJECTS/CAVE-04/shots.py` S11:
  - Dust burst replaced: 700 fine specks (radius 0.0009, was 2500 x 0.0015 in a 0.6 m sphere) in a tight 0.16 m shell at the bolt,
    growing to 1.25x only; it stays >= 0.55 m from the lens and never sits between the lens and the falling anchor. No blob.
  - Anchor fall slowed into a readable tumble (A -> -0.4 m at fail+6, -1.0 m at fail+15, into the crack by the end).
  - Lighting: a small key light parented to the anchor (bolt/pulley/rock chunk stay lit all the way down), plus a fill and a rim on
    the fall path / slack rope; the work lamp no longer dips to near-dark after the failure.
  - Camera (lens 30): holds on the bolt until the failure, then tilts/pulls back to follow the falling anchor into the crack; hard shake kept.
  - Verified: single frames 20/32/33/36/40/45/50/52/61 at 540 px (/tmp/fix_CAVE-04_S11*), preview S11 clean (no error log). Frame count 61 unchanged.
- Needs: production re-render of S11, then re-assembly (also picks up the S14 timer overlay).
