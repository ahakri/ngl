# QC REPORT — HAUNT-06 "The Woman on the Gravestone (1991)" (Bachelor's Grove Cemetery)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render)
- 1080x1920, 24 fps, H.264 ~5 Mbps, 30 MB; 46.90 s (haunted band 35-60 s); -14.5 LUFS; true peak -1.3 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps, no missing frames; all 14 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_onyx). Expected.

## Review cycle
- v1 FAIL:
  1. **S10 (0:33.0-0:36.4) — needs a shot re-render.** The 3D list-page labels are doubled: "#3" is printed twice with an
     offset, and the revealed caption under frame #5 reads as two overlapping copies ("#5"/"#3" and "Bachelor's Grove, 1991"
     twice), i.e. duplicated/garbled text (two text objects at the same spot, frame 0:35.5). Keep one label per frame; check
     the caption under #5 reads cleanly. Re-render S10 (~82 frames), then re-assemble. (The 2D "#5" overlay at y 1040 is fine.)
  2. **S11 (0:36.4-0:40.3) duplicated text (fixed in script.json).** The 2D card "WHAT SCEPTICS SAY / Double exposure? Two images,
     one frame" repeats the 3D corkboard heading "WHAT SCEPTICS SAY" and covers the two merging sheets.
     `SCRIPTS/HAUNT-06/script.json` S11 overlay[1] (card) **removed**; the DISPUTED badge stays.
  3. **S02 (0:05.0-0:08.1) (fixed):** the DOCUMENTED FACT badge (y 200) is drawn over the map subtitle "near Midlothian,
     Illinois". S02 overlay[0] (label) `params.y` 200 -> 1420.
  4. **S09 (0:28.8-0:33.0) (fixed):** the DOCUMENTED FACT badge (y 200) is hidden behind "THE 1991 PHOTO" document (only "DO"
     shows). S09 overlay[0] (label) `params.y` 200 -> 1420.
  - Item 3 test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:06.5: clean.
- Next: re-render S10, re-assemble (picks up the S02/S09/S11 overlays), re-QC.

## Editorial checks (frames every 2 s + spot frames at 0:32.6, 0:35.5, 0:44.6)
- Hook: the empty checkered gravestone in infrared, "10 AUGUST 1991" + line 1 inside 1 s; DOCUMENTED FACT + DRAMATISATION
  "recreation, not the photo". PASS
- The real 1991 photo is never shown: S08's print stays plain grey; S09 is a typed description; the S13 figure is a generic
  faceless translucent mannequin with the DRAMATISATION badge. PASS
- Labels follow FACTCHECK: phantom farmhouse / lights = FOLKLORE; GRS equipment and "nobody saw anyone" = EYEWITNESS CLAIM;
  double exposure and "nobody has proved it" = DISPUTED. PASS
- Removed items absent: no Sun-Times claim, no photographer name, no "passed every test", no pond/mob legends, no headstone
  names, no identity legends. PASS
- "#5" ranking ties to the Mental Floss list per FACTCHECK L10. PASS
- Ends on the S01 framing for the loop ("All we know is that on ..."). PASS

## Known minor weaknesses (accepted)
- S02: the map is a plain green square with a diagonal line.
- S03/S05: low contrast, dark night shots; investigators are small silhouettes behind the GRS card.
- S08: the darkroom is abstract red trays only.
- S13: the seated figure reads as a mannequin (by design, generic).
- S04: the vanishing farmhouse is small in the fog.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).

## Shot fixes (v2)
- **S10 doubled "#3" / "#5 Bachelor's Grove, 1991"** — cause: the 3D labels floated 11 mm off the page and the warm lamp's crisp
  shadow printed a second, offset copy of every label. `BLENDER_PROJECTS/HAUNT-06/shots.py` S10: rank numbers and the #5 caption
  now lie 1 mm off the paper with `visible_shadow = False`; the sliding paper occluder that reveals the caption casts no shadow either.
- Verified: frames 20/62/84 at 540 px (/tmp/fix_HAUNT-06_S10): "#2", "#3", "#4", "#5" and "Bachelor's Grove, 1991" each render
  once, legibly; preview S10 clean. Frame count 84 unchanged.
- Needs: production re-render of S10, then re-assembly (also picks up the S02/S09/S11 overlay fixes).
