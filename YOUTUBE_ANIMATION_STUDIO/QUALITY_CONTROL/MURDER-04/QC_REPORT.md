# QC REPORT — MURDER-04 "The Zodiac's Cipher Was Cracked After 51 Years" (Z340, solved 2020)

VERDICT: PASS (v2, 2026-11-28)

## Automated (QC_AUTO.json, CI render) — auto_verdict FAIL
- 1080x1920, 24 fps, H.264 ~5 Mbps, 46 MB; 74.40 s (murder band 55-82 s); -14.5 LUFS; **true peak -0.9 dBTP (above the -1 dBTP
  ceiling) -> auto FAIL.** No black segments, no frozen segments, no silence gaps, no missing frames; all 24 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_michael). Expected.
- Audio fix: re-assemble with the final limiter/loudnorm true-peak ceiling at -1.0 dBTP (or lower the loudest SFX gain) — not a
  visual issue; the re-assembly below is needed anyway.

## Review cycle
- v1 FAIL (overlays + audio peak; the rendered frames are fine, no re-render needed). Edits in `SCRIPTS/MURDER-04/script.json`:
  1. **S05 (0:14.6-0:18.2) incomplete text + covered badge:** the "1969 - CIPHER No. 1" document lives 2.3 s but types at 30 cps,
     so "solved about a week later / by a Salinas couple" (the point of L05) never appears; the DOCUMENTED FACT badge (y 200)
     sits under the document. S05 overlay[0] (document) added `"cps": 80` (fully typed at ~1.6 s); overlay[1] (label)
     `params.y` 200 -> 1420.
  2. **S15 (0:43.6-0:46.6) incomplete text:** the FBI telegram is still on line 2 when the shot ends; "by private citizens" and
     "(paraphrase, 11 Dec 2020)" never show. S15 overlay[0] (document) added `"cps": 60` (complete at ~2.3 s of 2.99 s).
  3. **S17 (0:48.2-0:51.3) and S21 (0:61.0-0:64.0):** DOCUMENTED FACT badge (y 200) covered by the documents. overlay[1]
     (label) `params.y` 200 -> 1420 in both.
  4. **S24 (0:72.1-0:74.4):** the end stamp "In memory of the Zodiac's victims / Sources in description" (26 cps) finishes typing
     only as the video ends. S24 overlay[1] (stamp) added `"cps": 50`.
  - Test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:16.75, 0:46.2, 0:50.7, 0:73.95: clean, text complete.
  - **Needs re-assembly** (with the true-peak ceiling fixed), then re-run qc_check and re-QC.
- v2: re-assembled (true-peak limiter fixed). PASS. QC_AUTO fresh: 74.40 s, -14.7 LUFS, true peak -1.1 dBTP (<= -1.0). Frames checked at 0:16.75 (S05 document complete through "by a Salinas couple", badge below the captions), 0:18.0, 0:46.2 (S15 FBI telegram complete incl. "(paraphrase, 11 Dec 2020)"), 0:50.7 (S17 badge visible), 0:63.0, 0:63.85 (S21 badge visible) and 0:73.95 (S24 end stamp fully typed). Accepted minor: S21 document finishes "Status: OPEN" only in the last ~0.5 s of the shot. qc_frames skimmed: nothing new.

## Editorial checks (frames every 2 s + spot frames at 0:17.2, 0:42.8, 0:46.3, 0:59.8)
- Hook: macro drift on the 340 grid, line 1 inside 1 s, DOCUMENTED FACT. PASS
- No victims, no crime scenes, no weapons: the case is a map card + "At least five people killed / Case still open"; the end
  stamp is "In memory of the Zodiac's victims". The "37 victims" claim is absent. PASS
- No suspect is named; "SUSPECT: UNIDENTIFIED / No one has been charged / Status: OPEN" (recreation). PASS
- The three solvers are named on cards with the fact-checked roles (Van Eycke = programmer, not "warehouse worker");
  "DOWN 1 - RIGHT 2", "hundreds of thousands" (no 650,000 figure), AZdecrypt credited. PASS
- FBI statement shown as a paraphrase with date; the TV-caller link is THEORY / "LIKELY REFERENCE". PASS
- Decoded lines match the published plaintext; Z13/Z32 card (April/June 1970); "MY NAME IS -" with stand-in glyphs. PASS
- Ends on S01's macro framing for the loop. PASS

## Known minor weaknesses (accepted)
- S14: the split-flap line reads "IMQQLOTS-OFUFUNFS" — "LOTS OF FUN" is hard to pick out of the noise at phone size.
- S12: "HUNDREDS OF THOUSANDS OF READING ORDERS" sits over the busy mosaic (legible with the stroke).
- S17: the first decoded line wraps ("... LOTS / OF FUN").
- S04/S07-S09 maps are abstract polygons (locations carried by the titles).
- S06: the three solver panels are dark; the monitors carry the shot.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
