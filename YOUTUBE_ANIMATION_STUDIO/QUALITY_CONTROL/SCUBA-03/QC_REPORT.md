# QC REPORT — SCUBA-03 "His Lifeline Snapped 100 m Under the North Sea" (Chris Lemons, 2012)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 32 MB; 50.83 s (scuba band 40-65 s); -14.6 LUFS; true peak -1.2 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 19 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_onyx). Expected.

## Review cycle
- v1 FAIL (overlays only — the rendered frames are fine, no re-render needed). Edits in `SCRIPTS/SCUBA-03/script.json`:
  1. **S19 (0:48.2-0:50.8) stray "~":** the stamp read "~3 WEEKS LATER"; in the mono stamp font the tilde reads as leftover
     markup (same class as the MURDER-02 "MLIAOI~" defect). S19 overlay[0] (stamp) `text` "~3 WEEKS LATER" ->
     "ABOUT 3 WEEKS LATER" (keeps the approximation from FACTCHECK L19; y 300 unchanged).
  2. **S03 (0:06.1-0:08.5) overlay on overlay + duplicated text:** the stamp "NORTH SEA / 18 SEP 2012" (y 300) is typed inside
     the map card, directly under the map's own "NORTH SEA / off Aberdeen" title. S03 overlay[1] (stamp): `text` ->
     "18 SEPTEMBER 2012", `params.y` 300 -> 1420 (below the captions, over open night sea).
  - Test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:07.5 and 0:50.2: clean.
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC.

## Editorial checks (frames every 2 s + spot frames at 0:04.5, 0:07.5, 0:29.5, 0:40)
- Hook: the umbilical whips and parts over the diver, "LIFELINE CUT" + line 1 inside 1 s. PASS
- Numbers match FACTCHECK: bailout "(EST.)", depth gauge stops at 91 m ("nearly a hundred metres"), 18 Sep 2012, DSV Bibby
  Topaz on screen only, "TIME WITHOUT MAIN GAS (REPORTED)" to 30:00 for "around half an hour". No hot water on the umbilical
  card, no breath count, no Lemons quotes. PASS
- Survival theory is labelled THEORY on S16/S17 and followed by "UNPROVEN"; no overlay asserts the cold as the cause. PASS
- Divers are faceless helmeted figures / silhouettes; the unresponsive Lemons and the rescue breaths in the bell are shown as
  profile silhouettes with no injury detail; no real faces. PASS
- Name cards (Lemons, Yuasa, Allcock) sit below the captions at y 1420 and do not collide. PASS
- Ends on S01's set intact for the loop. PASS

## Known minor weaknesses (accepted)
- S02: the timer is drawn over the big yellow helmet (legible thanks to the stroke); the helmet fills the top of the frame.
- S11: the timer label and digits sit over the DSV's dive tower.
- S15: "BREATHING" (y 420) butts against the 3D wall panel inside the bell.
- S08: the parting flash is a near white-out for ~0.5 s (by design).
- S05/S06: the ship is small in frame; foam patches are chunky; S12 rescuer mostly out of frame.
- S04: the diver is small in the wide shot.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
