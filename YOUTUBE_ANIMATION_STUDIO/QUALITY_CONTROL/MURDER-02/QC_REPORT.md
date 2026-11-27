# QC REPORT — MURDER-02 "The Dead Man With 'Tamam Shud' in His Pocket" (Somerton Man)

VERDICT: PASS (v2, 2026-11-27)

## Automated (QC_AUTO.json, after the v2 re-assembly)
- 1080x1920, 24 fps, H.264 <=5 Mbps, 44 MB; 72.75 s (murder band 55-82 s); -14.4 LUFS; true peak -1.2 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps; all 22 shots fully rendered.
- Narrator: am_adam (studio voice), timing-locked.

## Review cycle
- v1 FAIL (cosmetic, overlays only — frames were fine):
  1. The code's crossed-out second line rendered as "MLIAOI~" on the document cards (S11, S20, S21): a text-wrapping change had
     broken the strike-through markup. Fixed in PIPELINE/overlays.py (layout is now markup-aware and the typewriter counts visible
     characters); the line is now a struck-through "MLIAOI", matching the 3D back cover in S10. Code text enlarged for phones.
  2. S13: 2D "SPY / LOST LOVE / SUICIDE" text duplicated the 3D theory cards and cluttered the board. Removed; the "NO PROOF" verdict
     stays, placed below the captions.
  3. S21: "WHAT DOES IT SAY?" overlapped the document. Moved below the captions.
- v2: re-assembled from the existing frames (no re-render). PASS. Frames checked at 0:34, 0:40, 0:42, 1:07, 1:10.

## Editorial checks (frames every 2 s)
- Hook: the rolled "Tamam Shud" scrap, line 1 inside 1.5 s. PASS
- The 2022 identification is framed as a PROPOSED identity: "NOT YET CONFIRMED", DISPUTED label, "Coronial investigation ongoing
  (status checked Nov 2026)". PASS — re-check the coroner's status before upload (see FACTCHECK.md).
- Spy / lost love / suicide are shown as theories with "NO PROOF". PASS
- The man is a tiny, distant, faceless figure at the seawall; no body detail; the bust is a plain plaster form. PASS
- Code is labelled "RECREATED"; phone number never shown. PASS
- Ends on a comment question and loops back to the scrap of paper. PASS

## Known minor weaknesses (accepted)
- S12 (inquest, 0:36-0:39) is very dark: the plaster bust barely reads, the inquest card carries the beat.
- S05 "LABELS: CUT OUT" is red on brown (low contrast); S10 repeats the caption wording as on-screen text.
- S01: the rolled strip is small in frame for the first second.
- Not machine-checkable here: narration delivery was not auditioned by ear (no audio playback in this container).
