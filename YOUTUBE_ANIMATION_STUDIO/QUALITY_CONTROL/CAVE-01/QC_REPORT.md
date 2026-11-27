# QC REPORT — CAVE-01 "He Went 270 m Down to Bring a Body Home" (Dave Shaw, Boesmansgat)

VERDICT: PASS (v2, 2026-11-27)

## Automated (QC_AUTO.json, after the v2 re-assembly)
- 1080x1920, 24 fps, H.264 <=5 Mbps, 43 MB; 65.96 s (cave band 50-72 s); -14.6 LUFS; true peak -1.2 dBTP.
- No black segments mid-video, no frozen segments, no silence gaps; all 19 shots fully rendered.
- Narrator: am_adam (studio voice), timing-locked to the original shot timing.

## Review cycle
- v1 FAIL (visual): S12 (silt-out, 0:38-0:43) — the particle burst expanded around the lens, so near particles read as large
  confetti squares instead of silt (same defect flagged at preview round 1; the first fix was not enough at final resolution).
- Fix: S12 burst rebuilt with finer particles kept >= ~0.5 m from the camera (the noisy volume does the silt-out); S12 re-rendered
  (118 frames) and the video re-assembled. Frames checked at 0:39, 0:41, 0:42.5.
- v2: PASS.

## Editorial checks (frames every 2 s + ending)
- Hook: line 1 ("He found a body 270 metres down. Then he went back for it.") over the torch-on-the-floor shot. PASS
- No body is shown anywhere: the lost diver is an abstract half-buried tank + fin shape; the recovery is lines and silhouettes. PASS
- Depth gauge, descent/ascent timers, cross-section diagrams and the "MEET @ 220 M" plan read clearly; "CO2 up-arrow" glyphs render. PASS
- Fact labels present on claim shots; case-report page highlights "extreme hypercapnia -> unconsciousness" (experts' conclusion). PASS
- Ends on the memorial card, then cuts back to the empty chamber floor for the loop. PASS

## Known minor weaknesses (accepted)
- S03/S09/S13: the "DOCUMENTED FACT" badge touches the top-left edge of the cross-section diagram.
- S09: "MEET @ 220 M" text sits over the two diver dots.
- S08: the dusk figures are stiff mannequins; S10 kneel reads as a hover.
- Not machine-checkable here: pronunciation/delivery of the narration was not auditioned by ear (no audio playback in this container).
