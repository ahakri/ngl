# QC REPORT — CAVE-03 "Under the Ice, the Only Way Out Was Deeper" (Plura / Steinugleflåget, Norway, 2014)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 40 MB; 60.29 s (cave band 50-72 s); -14.4 LUFS; true peak -1.2 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 18 shots rendered (1492 frames).
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_michael). Expected.

## Review cycle
- v1 FAIL (overlays only — the rendered frames are fine, no re-render needed). All edits in `SCRIPTS/CAVE-03/script.json`:
  1. **S02 (0:03.2-0:08.3) depth gauge on the diagram:** the 2D depth gauge (right-hand bar) runs straight through the rendered
     "STEINUGLEFLÅGET" label, and its "109m / SQUEEZE" pointer lands on the glowing exit chamber at the end of the route, not on
     the squeeze (the red circle at the bottom of the U) — it labels the wrong place. S02 overlay[1] (type depth) **removed**;
     the squeeze depth is still shown by S08's gauge (0:24-0:25.8, "110m" at the squeeze) and the caption ("over 100 metres").
  2. **S02 stray "~":** stamp line "~2 KM THROUGH THE MOUNTAIN" -> "ABOUT 2 KM THROUGH THE MOUNTAIN" (FACTCHECK #3: about two
     kilometres; same tilde class as MURDER-02/SCUBA-03).
  3. **S07 (0:20.7-0:24.1) stray "~":** text "~2 °C" -> "ABOUT 2 °C" (FACTCHECK #8: typical value).
  4. **Fact labels contradict FACTCHECK/SCRIPT.md.** S08 (team one reached the squeeze), S10 (buddy's light signalling / stuck,
     tangled) and S14 (no way forward) are survivors' accounts marked REPORTED in FACTCHECK #10/#13 and SCRIPT.md ("On-screen
     REPORTED badge on S08/S10"), but they carried green DOCUMENTED FACT badges. Changed the label overlay text to
     "EYEWITNESS CLAIM" on S08, S10 and S14 (y 200 unchanged). S07's two-hour gap (BBC-only, FACTCHECK #9 "kept with a REPORTED
     label") had no badge: added `{"type": "label", "text": "EYEWITNESS CLAIM", "params": {"y": 200}, "start": 1.8}` to S07
     (appears with "+2 HRS: TEAM TWO").
  - Test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:07.5, 0:21.0, 0:23.8, 0:25.0: clean, text fits.
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC (check 0:07.5, 0:21, 0:23.8, 0:25, 0:31, 0:42.5).

## Editorial checks (frames every 2 s + spot frames at 0:04.5, 0:07.5, 0:15, 0:16.8, 0:19.5, 0:21.5, 0:22, 0:23.8, 0:25, 0:52, 0:54.8, 0:58)
- Hook: the triangular ice hole + line 1 inside 1 s; the route diagram follows at 0:03. PASS
- No bodies: the victims are lights and dark silhouettes only; the stuck diver is a light behind a tangle. No faces. PASS
- Victims not named; the second death's cause is not narrated or shown. PASS
- "OFFICIAL RECOVERY FAILED / DIVING BANNED IN PLURA" card matches FACTCHECK #16 (The Local). PASS
- Ends on the ice hole (loop) with "PART 2 →". PASS — but see below.

## Known minor weaknesses (accepted)
- **S18 "PART 2 →"** points to CAVE-10 (the recovery), which is not produced yet. Either hold CAVE-03's upload until CAVE-10 is
  live, or pin a comment ("Part 2 coming") at upload. Not an overlay fault.
- S05 (0:14.5-0:17.3): the rendered map's "NORWAY" label is cropped at the left edge as the camera pushes in ("RWAY").
- S06 (0:19.5): the caption "AND CLIMB OUT" sits on the 3D squeeze circle/label.
- S13 (0:37-0:41): very dark; only the torch beam and guideline read.
- S17: the police-tape scene is soft/blurred behind the NOTICE card (by design).
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
