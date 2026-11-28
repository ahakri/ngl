# QC REPORT — MURDER-03 "He Hijacked a Plane, Then Jumped Into the Night" (D.B. Cooper, 1971)

VERDICT: FAIL (v1, 2026-11-28)

## Automated (QC_AUTO.json, CI render) — auto_verdict FAIL
- 1080x1920, 24 fps, H.264 ~5 Mbps, 47 MB; 74.08 s (murder band 55-82 s); -14.6 LUFS; true peak -1.3 dBTP.
- **Black segment mid-video 0:28.375-0:29.208 (0.83 s)** -> auto FAIL. No frozen segments, no silence gaps, no missing frames;
  all 23 shots rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing (voice_original am_onyx). Expected.

## Review cycle
- v1 FAIL:
  1. **S10 (0:28.2-0:30.2) — needs a shot re-render (auto FAIL).** "And stepped off into the dark": the first ~1 s is an almost
     pure black frame with rain streaks; the falling silhouette is a few pixels and the forest does not read until the striped
     canopy opens (~0:29.4). Lift the fill / bring the first lightning flash forward so the figure dropping away from the stair
     reads from frame 1 and no frame sits under the black-detect threshold. Re-render S10 (~47 frames).
  2. **S16 (0:48.7-0:52.5) duplicated text — script.json fixed + shot re-render.** The 2D "WASHED DOWNSTREAM?" and "BURIED?"
     texts repeat the 3D corkboard cards with the same words. Removed from `SCRIPTS/MURDER-03/script.json` (S16 overlay[1]
     "WASHED DOWNSTREAM?" and overlay[2] "BURIED?"; THEORY badge and red "UNPROVEN" stay). The 3D cards themselves are cropped
     at the frame edges ("ASHED NSTREA", "BURIE"), so **re-render S16 with a wider framing / cards moved inward** so both cards
     read in full (~91 frames). If S16 cannot be re-rendered, restore the two 2D texts instead (accepting the duplication).
  3. **S20 (0:61.1-0:65.1) (fixed in script.json).** The DOCUMENTED FACT badge (y 200) sits under the CASE FILE document, and the
     document's typewriter (30 cps) is still on "Evidence" when the shot fades, so "preserved for history" never appears.
     S20 overlay[0] (document) added `"cps": 50`; S20 overlay[1] (label) `params.y` 200 -> 1420.
  4. **S14 (0:40.5-0:44.9) stray "~" (fixed).** Card text "~$5,800 in $20 bills" -> "About $5,800 in $20 bills" (matches L14).
  5. **S18 (0:54.6-0:59.0) dated header the fact-check avoided (fixed).** Card header "FAA ORDER, 1972" -> "FAA ORDER"
     (FACTCHECK L18-L19: only two secondary sources, "kept the wording general and gave no exact date").
  - Items 2-3 test-composited with PIPELINE/overlays.py + compose.avoid_captions at 0:51.2 and 0:64.1: clean.
- Next: re-render S10 and S16, re-assemble (picks up the S14/S16/S18/S20 overlays), re-run qc_check, re-QC.

## Editorial checks (frames every 2 s + spot frames at 0:15.8, 0:17.5, 0:28.6, 0:29.6, 0:38.5, 0:60, 0:64.5, 0:66.3)
- Hook: open airstair under the 727 tail, line 1 inside 1.5 s, the silhouette drops on "jumped". PASS
- The hijacker is a faceless silhouette; no FBI sketch, seal, letterhead or real note wording (note marked "(paraphrase)",
  case file "(recreation)"); the boy at Tena Bar is a faceless distant silhouette, unnamed. PASS
- No suspect is named; the suspect wall is blank cards; "SUSPECTS CONSIDERED 800" and "CHARGED: 0" match FACTCHECK L21. PASS
- Drop zone vs Tena Bar = DISPUTED ("estimates vary"); how the money got there = THEORY + "UNPROVEN"; FBI view "probably
  didn't survive" = THEORY. PASS
- Numbers: $200,000 / $20 bills / 4 parachutes / 36 passengers (majority figure on screen only) / approx. 8:13 PM /
  10 Feb 1980 / $194,200 still missing / July 2016. PASS
- Ends on S01's set with "All anyone knows for sure is this." for the loop. PASS

## Known minor weaknesses (accepted)
- S05 (1.7 s shot): "I HAVE A BOMB" is fully typed for only ~0.5 s.
- S06: the parachute "dust puffs" read as white square flecks around the packs (not over them).
- S13: the sand sweep is a grey blur with coarse triangular grains for the first ~1 s.
- S19: "COOPER VANE" title sits over the 3D vane; S21 red "CHARGED: 0" on the busy card wall (legible with the stroke).
- S03/S08/S15 maps are plain dark coast shapes; S11 trees are low-poly cones.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).

## Shot fixes (v2)
- **S10 black frames (auto FAIL)** — `BLENDER_PROJECTS/MURDER-03/shots.py` S10: moon 1.6 -> 4.0 on the cloud deck, brighter cloud
  colour, an extra lightning flash on frame 2 (plus the existing one at the canopy), stair spill light 12000 -> 30000 W / 16 deg,
  lens 24 -> 30, and a slower first drop (z -4.5 -> -15 by the canopy, was -6 -> -28) so the lit silhouette reads from frame 1.
  Rendered frames 1/6/12/18/24/30/36/49: 60-96 % of pixels above luma 30 (was ~0 % in the first second), still a dark night storm.
- **S16 cropped theory cards** — S16: cards moved inward and up (WASHED DOWNSTREAM? at x -0.55, BURIED? at x +0.55, above the
  red "UNPROVEN" overlay at y 1100), Tena Bar photo raised to z 1.75, "?" card moved below the caption band; camera lens 35 -> 28
  and aimed a little lower. Both cards and the photo read in full in frames 2/45/93; no 2D duplicate texts needed.
- Verified: single frames at 540 px (/tmp/fix_MURDER-03_S10*, /tmp/fix_MURDER-03_S16), previews S10 and S16 clean. Frame counts 49/93 unchanged.
- Needs: production re-render of S10 and S16, re-assembly, re-run qc_check.
