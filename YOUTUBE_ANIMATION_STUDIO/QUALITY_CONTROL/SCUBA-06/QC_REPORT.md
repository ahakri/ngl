# QC REPORT — SCUBA-06 "462 Stitches, Then He Went Back In" (Rodney Fox, Aldinga Beach 1963)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 36 MB; 57.29 s (scuba band 40-65 s); -14.4 LUFS; true peak -1.2 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 18 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original bm_george). Expected.

## Review cycle
- v1 FAIL (overlay only — the rendered frames are fine, no re-render needed):
  1. **S15 (0:43.3-0:45.9) overlay asserts what the narration hedged.** The big yellow "FIRST FOOTAGE" states it flatly, while
     the line is "Some of the first footage of its kind" — FACTCHECK L15 hedged it to "some of the first" on purpose.
     `SCRIPTS/SCUBA-06/script.json` S15 overlay[0] (text) `text` "FIRST FOOTAGE" -> "AMONG THE FIRST" (y 430, size 100, colour
     unchanged; fits the frame width).
  - **Needs re-assembly** from the existing frames (no re-render), then re-QC.

## Editorial checks (frames every 2 s + spot frames at 0:22.4, 0:44.8, 0:47.9)
- Hook: from below, the great white rising toward Fox at the surface, "GREAT WHITE" + line 1 inside 1 s. PASS
- No blood, no wounds, no gore: the bite is a white flash and a silt bloom (S04), the rescue is silhouettes hauling a dark
  figure (S08); injuries and stitches appear only as an abstract line-art torso diagram (S09/S10), as FACTCHECK allows. PASS
- "Seized ... around the chest" (no "nearly in half"); no "breath-hold / NO TANK" claim on screen (removed after the fact-check);
  eye-poke beat now VERIFIED. PASS
- Numbers/dates: 8 DEC 1963 Aldinga Beach, 462 stitches, timeline 1963 / 1960s first cage / 1976+ cage trips; Ron Taylor
  credited; FOX SHARK RESEARCH FOUNDATION card. No present-tense claims about Fox. PASS
- Fox and divers are faceless silhouettes; the tagged shark in S17 is calm (conservation framing). PASS
- Ends on S01's set for the loop. PASS

## Known minor weaknesses (accepted)
- S02: the "SOUTH AUSTRALIA / 8 DEC 1963" stamp is small white mono on the pale sky (low contrast).
- S07 (0:21.6-0:23.3): the belt-knot close-up reads as blocky dark shapes and a white rod.
- S03: only shot of the attack sequence with a DRAMATISATION badge; S04-S08 recreations carry none.
- S11: the figure is blocky; sun-glint smear on the water. S16: the cage beside the boat barely reads.
- S01/S18: the water is pale and hazy.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
