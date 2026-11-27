# Blockers

- youtube.com not reachable from container: reference view counts come from search snippets/third-party pages and are flagged when unverified.
- No GPU: EEVEE runs on llvmpipe software GL, Cycles on 4 CPU cores. Render budget limits how many shorts are fully rendered per night.
- SPEC CONTRADICTION: the brief requires "exactly 20" concepts in each of 4 categories (= 80) and "exactly 100" concepts in total. Resolution:
  each category file keeps exactly 20 ranked concepts (completion criteria), plus VIDEO_IDEAS/RESERVE_20/ holds 20 extra concepts
  (5 per niche, IDs CAVE-R1..R5, SCUBA-R1..R5, MURDER-R1..R5, HAUNT-R1..R5) so the library totals exactly 100.
- RESOLVED: CAVE-04 (Nutty Putty) fact-check completed (16 claims, ≥2 sources each).
- RESOLVED: MURDER-04 (Zodiac 340) fact-check VERIFIED.
- 2026-11-27 ~09:00–12:00 UTC: account 5-hour usage limit hit (12 concurrent agents). All agents paused; the worker restarts killed the render queue mid HAUNT-01. Resumed 12:38 UTC. Mitigation: ≤4–5 concurrent agents; render queue now launched with setsid so it survives worker restarts.
- SCUBA-06 (Rodney Fox: lines L03, L05) and MURDER-05 (Hinterkaifeck: line L17) fact-checks are PROVISIONAL ( verified fallback wording exists). CAVE-05/06 scripting completed after resume (VERIFIED).
- 2026-11-27: QC found true peak -0.4 dBTP on MURDER-01 (spec -1). Fixed: alimiter after loudnorm in compose; qc_check now fails on TP > -1; HAUNT-01/MURDER-01 audio re-muxed (-1.4 dBTP).
