# FINAL REPORT — YouTube Animation Studio (Shorts)

Prepared by: Production Manager · Snapshot: 2026-11-27 ~16:22 UTC (after `python3 PROJECT_TRACKER/update_tracker.py`).
Rule used for this report: a deliverable counts as done only if its file exists on disk. A video counts as finished only if `FINAL_VIDEOS/<ID>.mp4` exists **and** `QUALITY_CONTROL/<ID>/QC_REPORT.md` says `VERDICT: PASS`.

---

## 1. Executive summary

| Metric | Count | Evidence |
|---|---|---|
| Concepts | **100** = 4 × 20 ranked (completion criterion) + 20 reserve (5 per niche) | `VIDEO_IDEAS/{CAVE_DIVING,SCUBA_DIVING,MURDER_MYSTERY,HAUNTED}_20/concepts.json` (20 each), `VIDEO_IDEAS/RESERVE_20/*_reserve.json` (5 each) |
| Why 80 + 20 | The brief asks for "exactly 20 per category" (= 80) and also "exactly 100 total". Resolution: each category file keeps exactly 20; the 20 extras live in a separate reserve pool (IDs `*-R1..R5`). | `PROJECT_TRACKER/BLOCKERS.md` |
| Scripted (script + storyboard + packaging + fact-check) | **28** (7 per niche, ranks 1–7, see the CAVE-07 note in §4) | `SCRIPTS/<ID>/{SCRIPT.md,script.json}`, `STORYBOARDS/<ID>/STORYBOARD.md`, `THUMBNAILS/<ID>/PACKAGING.md`, `QUALITY_CONTROL/<ID>/FACTCHECK.md` |
| Fact-check | 28/28 files. **26 VERIFIED**, **2 PROVISIONAL** (SCUBA-06: L03, L05; MURDER-05: L17). Both have verified fallback lines. **All checks are based on search snippets** (no full pages could be fetched). | `QUALITY_CONTROL/<ID>/FACTCHECK.md` |
| Narration (TTS) + shot timing | 28/28 | `AUDIO/<ID>/{narration.wav,timings.json,shot_timing.json}` |
| Animated (shots.py written, preview contact sheet, `READY` flag) | **23** (2 rendered + 21 in the render queue) | `BLENDER_PROJECTS/<ID>/{shots.py,READY}`, `QUALITY_CONTROL/<ID>/{ANIMATION_NOTES.md,contact_sheet.png}` |
| Rendered **and** QC PASS | **2** | `FINAL_VIDEOS/HAUNT-01.mp4` (56.5 s, QC PASS v1) · `FINAL_VIDEOS/MURDER-01.mp4` (67.5 s, QC PASS v2) |
| Currently rendering | CAVE-01 (started 16:03 UTC; 5 of 19 shots begun at snapshot) | `PROJECT_TRACKER/render_queue.log`, `RENDERS/CAVE-01/` |
| Thumbnails (PNG) | **2 videos** (HAUNT-01, MURDER-01): A/B at 1080×1920 + 1280×720 + comparison sheet. Text packaging (titles + thumbnail concepts) exists for all 28. | `THUMBNAILS/<ID>/thumb_{A,B}{,_16x9}.png`, `thumb_sheet.png`; `THUMBNAILS/<ID>/PACKAGING.md` |

Bottom line: research, strategy, the 100-concept library, the 28-video scripted slate and the full production pipeline are done. **Only 2 of 28 scripted Shorts are finished and QC-passed.** 21 more are animated and queued. CPU-only rendering (~1.3–2 h per Short) is the bottleneck.

---

## 2. Status by phase and against the completion criteria

### 2a. The 9 phases (tracker phase keys P1–P9)

Note: the `phases` block in `PROJECT_TRACKER/tracker.json` is **stale**: it still shows P1–P3 "in_progress" and P4–P9 "todo". The per-video data (`STATUS.md`, `MASTER_SPREADSHEET.csv`) is current. The statuses below come from the files on disk.

| Phase | Status | Evidence |
|---|---|---|
| P1 Research (algorithm + 4 niches) | DONE | `RESEARCH/YOUTUBE_ALGORITHM/{ALGORITHM_REPORT.md,SHORTS_STRATEGY.md,sources.md}`; `RESEARCH/<NICHE>/{RESEARCH_REPORT.md,reference_videos.csv}` ×4 |
| P2 Format templates | DONE | "FORMAT TEMPLATE" section at the end of each `RESEARCH/<NICHE>/RESEARCH_REPORT.md` |
| P3 Concepts (80 + 20 reserve) | DONE | `VIDEO_IDEAS/*_20/{CONCEPTS.md,concepts.json}`, `VIDEO_IDEAS/RESERVE_20/` |
| P4 Selection | DONE, but the reasoning is only implicit | Slate = top 7 by score per niche (`MASTER_SPREADSHEET.csv` rank/total). No separate selection memo. |
| P5 Scripts + storyboards | DONE for the 28-video slate (28/100 concepts) | `SCRIPTS/*/`, `STORYBOARDS/*/` |
| P6 Assets / animation | PARTIAL: 23/28 | `PIPELINE/blender/{studio_lib,lib_cave,lib_scuba,lib_murder,lib_haunted}.py`, `BLENDER_PROJECTS/<ID>/shots.py`. Missing: CAVE-07, SCUBA-07, MURDER-06, MURDER-07, HAUNT-07 |
| P7 Render + edit | PARTIAL: 2/28 final, 1 rendering, 20 queued | `FINAL_VIDEOS/`, `render_queue.log` |
| P8 QC | PARTIAL: 2/28 PASS. Fact-check QC is 28/28. | `QUALITY_CONTROL/{HAUNT-01,MURDER-01}/QC_REPORT.md` |
| P9 Report | DONE (this file) | `PROJECT_TRACKER/FINAL_REPORT.md` |

### 2b. Completion criteria

| Criterion | Verdict | Evidence / gap |
|---|---|---|
| Exactly 20 concepts per category | **MET** | 4 × `concepts.json` with 20 entries each, plus a 20-concept reserve to reach 100 total |
| Competitor research per niche | **MET** (evidence quality is limited) | 4 reports + CSVs: cave 29 refs, scuba 24, murder 23, haunted 29. 103 of 105 rows are marked `unverified`. Only 13 rows are Shorts. |
| YouTube strategy | **MET** | `RESEARCH/YOUTUBE_ALGORITHM/SHORTS_STRATEGY.md`: runtime bands per niche, hook rules, cadence of 4–5/week, metric thresholds, compliance checklist. Numbers are tagged [HYPOTHESIS]. |
| Evidence for selections | **PARTIAL** | Every concept has 5-axis scores and `why_potential`. Gaps: 13 of 20 murder concepts and 0 of 5 murder reserve concepts have an empty `references` list. CAVE-07 (rank 8) was scripted instead of CAVE-08 (rank 7, also scored 73), and no reason is recorded. There is no written selection memo. |
| Scripts | **MET for the slate** (28). NOT MET for "all 100" | `RESUME_HERE.md` says to keep expanding until all 100 are scripted |
| Storyboards | **MET for the slate** (28) | `STORYBOARDS/<ID>/STORYBOARD.md` |
| Original animation assets | **PARTIAL** (23/28) | All assets are procedural code. There are no stock assets, AI images or samples; the `CHARACTERS/`, `ENVIRONMENTS/` and `ANIMATIONS/` folders are empty by design. The code is about 32k lines in `PIPELINE/blender/*.py` + `BLENDER_PROJECTS/*/shots.py`. Also: `QUALITY_CONTROL/SAMPLER/studio_sampler.jpg` |
| Rendered, QC'd videos | **PARTIAL** (2/28) | HAUNT-01, MURDER-01 |
| Tracker | **MET** (one stale block) | `STATUS.md`, `MASTER_SPREADSHEET.csv/.xlsx`, `tracker.json` (the phases block is stale), `BLOCKERS.md`, `RESUME_HERE.md` |
| Final report | **MET** | This file |

---

## 3. Production pipeline

| Stage | Tool | File |
|---|---|---|
| Environment bootstrap | uv venvs: `/opt/bpyenv` (bpy), `/opt/ttsenv` (kokoro-onnx); apt packages for EGL/Mesa, espeak-ng, sox and fonts | `PIPELINE/setup_env.sh` |
| Narration | Kokoro neural TTS (ONNX, 24 kHz, voices such as am_michael/bm_george). Word timings come from per-line synthesis plus energy trimming and phoneme-weighted word spans. | `PIPELINE/tts.py` |
| Shot timing | Shot starts are snapped to the narration line starts | `make_video.py <ID> timing` → `AUDIO/<ID>/shot_timing.json` |
| 3D animation | Blender 5.0 `bpy`, headless, **EEVEE on CPU** (llvmpipe/EGL surfaceless), 24 fps. Frames render at 540×960 and are upscaled in compose; preview renders at 270×480. Cycles is optional per shot. | `PIPELINE/blender/render_shot.py`, `studio_lib.py`, `lib_<niche>.py`, `BLENDER_PROJECTS/<ID>/shots.py` (guide: `BLENDER_PROJECTS/ANIMATION_GUIDE.md`) |
| Audio | Procedural, original music beds + SFX (numpy, 48 kHz). No samples and no licensed audio. | `PIPELINE/audio.py` |
| Compose | Per-niche grade (gain/lift/saturation/contrast/vignette/grain) and upscale to 1080×1920. Pillow overlays: stamps, depth gauges, timers, maps, timelines, documents, fact badges. Overlays are moved out of the caption band automatically. Word-synced ASS captions via libass. Transitions. x264 CRF 21 / max 5 Mbps; AAC 192k; `loudnorm I=-14 TP=-1.5`. | `PIPELINE/compose.py`, `overlays.py`, fonts in `PIPELINE/fonts/` |
| Render queue | A daemon renders and composes any `READY` project whose final file is missing or older than its flag, then runs QC. `FAILED` flag on error. Exits after 4 h idle. | `PIPELINE/render_queue.sh` → `PROJECT_TRACKER/render_queue.log` |
| Automated QC | Checks resolution, fps, niche duration band, LUFS, true peak, black/frozen/silent segments and missing shots. Writes a 2-second frame grid. | `PIPELINE/qc_check.py` → `QC_AUTO.json`, `qc_frames.png` |
| Thumbnails | Compositor from rendered frames: 9:16 + 16:9, text, glow, vignette, A/B sheet | `PIPELINE/thumbnail.py` + `THUMBNAILS/<ID>/thumbs.json` |
| Tracker | Rebuilds STATUS/CSV/XLSX from disk | `PROJECT_TRACKER/update_tracker.py` |

How to run it (from `YOUTUBE_ANIMATION_STUDIO/`):
```bash
bash PIPELINE/setup_env.sh                                   # restore toolchain after container recycle
cd PIPELINE
python3 make_video.py <ID> tts                               # narration + word timings
python3 make_video.py <ID> timing                            # shot_timing.json
python3 make_video.py <ID> preview                           # 270x480 stills -> QUALITY_CONTROL/<ID>/contact_sheet.png
touch ../BLENDER_PROJECTS/<ID>/READY                         # hand off to the queue
pgrep -f render_queue.sh || setsid nohup ./render_queue.sh >/dev/null 2>&1 &   # queue: render(--res 540) -> compose -> qc
# manual equivalents:
EGL_PLATFORM=surfaceless python3 make_video.py <ID> render --res 540 [--only S03,S07]
python3 make_video.py <ID> compose      # or: python3 compose.py <ID> [--preview]
python3 qc_check.py <ID>
python3 thumbnail.py <ID>               # needs THUMBNAILS/<ID>/thumbs.json
cd .. && python3 PROJECT_TRACKER/update_tracker.py
```

---

## 4. Per-video table (all 28 scripted videos)

Runtime is the measured narration-driven length (`AUDIO/<ID>/shot_timing.json`). FC = fact-check: V = VERIFIED, P = PROVISIONAL (all snippet-based). Anim: READY = shots.py done and queued; — = not started. Thumb: PNG = rendered A/B thumbnails; MD = text concept only (`PACKAGING.md`).

| ID | Title (script) | Runtime | FC | Anim | Render | QC | Thumb | Notable weaknesses (from ANIMATION_NOTES / QC_REPORT / FACTCHECK) |
|---|---|---|---|---|---|---|---|---|
| CAVE-01 | He Went 270 m Down to Bring a Body Home | 65.9 s | V | READY | **rendering** | — | MD | S19 sunrise pit mostly in shadow; Shaw's age and Dreyer details omitted (single-source) |
| CAVE-02 | 13 Trapped 4 km Inside a Flooded Cave | 62.7 s | V | READY | queued | — | MD | S16 is the weakest shot (divers read as dark shapes); S15 abstract/clinical; search budget ran out (some side facts left unchecked, not narrated) |
| CAVE-03 | Under the Ice, the Only Way Out Was Deeper | 60.3 s | V | READY | queued | — | MD | S13 silhouettes barely read (beams only); victims unnamed and cause of 2nd death left unstated on purpose |
| CAVE-04 | Stuck Upside Down With No Way to Back Out | 51.3 s | V (re-check) | READY | queued | — | MD | S01 legs read stiff (weakest); S04 cave opening reads weakly; sensitive subject (body left in cave) |
| CAVE-05 | Air for One Diver. There Were Two. | 58.6 s | V | READY | queued | — | MD | S01 bodies read as dark masses; S02 reflection sits in caption third; 48 vs 60 h discrepancy (majority figure used) |
| CAVE-06 | It Looks Like a Pond. Divers Call It Everest. | 61.2 s | V (death count DISPUTED, floor of 10 verified) | READY | queued | — | MD | S12 weakest (foreground diver); flat fins; sign text and 260 ft are single-wire/REPORTED |
| CAVE-07 | The Man Who Wrote Cave Diving's Rules Tried for 1,000 ft | 57.2 s | V | — | — | — | MD | Not animated. Concept rank 8; scripted ahead of CAVE-08 (rank 7, also scored 73) with no recorded reason |
| SCUBA-01 | He Survived 60 Hours Inside a Sunken Ship | 51.9 s | V | READY | queued | — | MD | S05 darkest shot; S03 "world tipping" subtle; NatGeo confirmed only via snippets |
| SCUBA-02 | The Dive Boat Left Without Them | 62.6 s | V | READY | queued | — | MD | Runtime 62.6 s is near the top of the scuba band (40–65 s); S01 boat a speck; corals pastel |
| SCUBA-03 | His Lifeline Snapped 100 m Under the North Sea | 50.8 s | V (recheck L09 advised) | READY | queued | — | MD | S06 foam chunky; L09 rests on Lemons' own account plus one rescue description |
| SCUBA-04 | A Humpback Closed Its Mouth Around Him | 49.3 s | V | READY | queued | — | MD | S13 foam ring reads as a flat plate |
| SCUBA-05 | He Dived 332 m. Getting Back Took Nearly 15 Hours | 51.9 s | V (Guinness status re-check pending) | READY | queued | — | MD | S06 glove blocky; record contested in 2020 (GWR upheld it); re-check before upload |
| SCUBA-06 | 462 Stitches, Then He Went Back In | 57.8 s | **P** (L03 breath-hold, L05 eyes) | READY | queued | — | MD | S05 eye close-up relit without a re-preview (3-round limit); gloves and hands blocky; Fox's current status not checked |
| SCUBA-07 | Sponge Divers Found a 2,000-Year-Old Machine | 53.9 s | V | — | — | — | MD | Not animated |
| MURDER-01 | Nine Hikers Cut Their Tent Open From the Inside | 67.5 s | V | done | **FINAL** `FINAL_VIDEOS/MURDER-01.mp4` (44 MB) | **PASS v2** | **PNG** | No cloth sim on the canvas; tetra snow particles; true peak −0.4 dBTP is above the −1 dBTP spec, but qc_check does not enforce it |
| MURDER-02 | The Dead Man With 'Tamam Shud' in a Hidden Pocket | 72.7 s | V (**coroner status time-sensitive**) | READY | queued | — | MD | S12 plate very dark; bust is primitive; code overlay prints literal "[crossed out]"; S19 has no surf |
| MURDER-03 | He Hijacked a Plane, Then Jumped Into the Night | 74.1 s | V | READY | queued | — | MD | S18 hangar reads poorly; S22 low-poly forest; 4 shots are plates under overlays |
| MURDER-04 | The Zodiac's Cipher Was Cracked After 51 Years | 74.4 s | V (re-check) | READY | queued | — | MD | S14 decode letters small on a phone; S06 panels small; flat screen textures |
| MURDER-05 | Footprints Led to the Farm. None Led Away. | 66.4 s | **P** (L17 main suspect) | READY | queued | — | MD | S13 blocky cattle; S11/S04 dark; S12 rigid smoke; check the "Cäzilia" glyph |
| MURDER-06 | The Ghost Ship's Creepiest Detail Was Fiction | 75.0 s | V (L13 wording caveat) | — | — | — | MD | Not animated. Doyle story text not read directly (Gutenberg fetch blocked) |
| MURDER-07 | The Oldest Cold Case: Shot in the Back 5,300 Years Ago | 61.7 s | V | — | — | — | MD | Not animated |
| HAUNT-01 | The Voice on the Enfield Tapes | 56.5 s | V | done | **FINAL** `FINAL_VIDEOS/HAUNT-01.mp4` (58 MB) | **PASS v1** | **PNG** | Whip transitions smear for ~0.2 s; tape-notes document sparse; S06 recorder deck dark |
| HAUNT-02 | The Real Room 217 | 50.8 s | V (1974 date conflict noted) | READY | queued | — | MD | S11 icon crude; S06 shimmer |
| HAUNT-03 | Don't Stop for Her on Archer Avenue | 47.5 s | V (claims labelled) | READY | queued | — | MD | S07 car reads as a flat silhouette; search budget ran out |
| HAUNT-04 | The Ghost on the Raynham Hall Staircase | 57.3 s | V (claims labelled) | READY | queued | — | MD | S07 flash dish is a flat grey disc; S12 figure has partial transparency and no motion blur |
| HAUNT-05 | The Tunnel Built to Hide the Dead | 48.5 s | V (NRHP primary source pending) | READY | queued | — | MD | S02 facade reads as a flat grid; S01 gurney outline-only at small size |
| HAUNT-06 | The Woman on the Gravestone (1991) | 46.9 s | V | READY | queued | — | MD | S13 figure reads as a mannequin |
| HAUNT-07 | Drivers Keep Reporting They Hit Her | 48.3 s | V (as labelled claims) | — | — | — | MD | Not animated. Witness accounts come only from folklore/paranormal-research writing |

Queue order after CAVE-01 (by READY timestamp): MURDER-02, HAUNT-02, CAVE-03, SCUBA-01, SCUBA-02, HAUNT-03, SCUBA-03, CAVE-02, HAUNT-04, SCUBA-04, CAVE-04, HAUNT-05, HAUNT-06, MURDER-03, SCUBA-05, MURDER-04, SCUBA-06, CAVE-05, CAVE-06, MURDER-05. No `FAILED` flags and no `render_error_*.log` on disk.

Runtime vs strategy bands (`SHORTS_STRATEGY.md` §2): MURDER-03, MURDER-04 and MURDER-06 (74–75 s) are inside the 55–80 s band but at its long end. HAUNT-01 and HAUNT-04 (56–57 s) are slightly over the 35–55 s start band; qc_check uses 35–60 s.

---

## 5. Research quality and honesty

- **youtube.com is unreachable** from the container, and so are Wikipedia, Social Blade and Playboard (DNS-blocked). No YouTube page was ever opened.
- **View counts are mostly unverified**: 103 of 105 reference rows across the 4 `reference_videos.csv` files are marked `unverified`, with the snippet source named. No URL, view count or date was invented (brief rule). Only 13 references are Shorts; long-form references are used as evidence of topic demand only.
- A shared **web-search budget of ~200 calls per turn** ran out during research (cave report §0) and during several fact-checks (CAVE-02, SCUBA-03/04, HAUNT-03/04). Leftover items were dropped from narration, not guessed.
- **Fact-checks are snippet-based**: 28/28 files state that no full page was read; the rule was ≥2 independent sources per narrated claim, otherwise an on-screen REPORTED/DISPUTED/EYEWITNESS CLAIM label or removal. Each file lists its removed claims (2–10 per video).
- Thresholds in the strategy are explicitly **[HYPOTHESIS]** and need recalibration after ~20 uploads.
- **Spec contradiction**: "exactly 20 per category" (80) vs "exactly 100 total". Resolved as 4 × 20 ranked + `VIDEO_IDEAS/RESERVE_20/` (5 per niche) = 100 (`BLOCKERS.md`).
- Score calibration: niche means are 68–75 and the maximum is 84. No concept exceeds 85, in line with the brief's anti-inflation rule.
- Ethics measures that are implemented: faceless stylised figures; no gore; fact badges on every claim shot in paranormal videos; recordings described but not played (HAUNT-01); private house number withheld; uncharged suspects not named (MURDER-05).
- Minor: `BLOCKERS.md` says SCUBA-06 is provisional on "1 line"; the fact-check actually lists 2 lines (L03, L05).

---

## 6. Blockers and risks

| Risk | Detail | Mitigation / status |
|---|---|---|
| Usage limit | 2026-11-27 ~09:00–12:00 UTC: the 5-hour account limit was hit with 12 concurrent agents. Worker restarts killed the queue mid-HAUNT-01. | Resumed 12:38. Run ≤4–5 agents. The queue is launched with `setsid`. The queue is restart-safe because finished frames are skipped. |
| CPU render throughput | No GPU; EEVEE on llvmpipe. HAUNT-01 took ~2 h 05 m (12:38→14:43); MURDER-01 took ~1 h 20 m (14:43→16:03). Shots take 1–19 min each. | About 20–40 h of wall time for the 21 queued videos. Frames render at 540p and are upscaled, which costs sharpness. A GPU or render farm would cut this sharply. |
| GitHub file sizes | Final MP4s are committed directly, without LFS: HAUNT-01.mp4 is 57.7 MB and MURDER-01.mp4 is 44.3 MB. GitHub warns above 50 MB and rejects above 100 MB. 28 finals ≈ 1.3–1.6 GB of repo bloat. | Frames, `*_preview.mp4`, `.blend` files and mix.wav are gitignored. Recommend Git LFS or external storage for the finals. |
| Local disk | `RENDERS/` holds about 0.8 GB of PNG frames per finished video (HAUNT-01 760 MB, MURDER-01 778 MB) | Prune RENDERS after QC PASS |
| Inauthentic-content policy | The TTS + procedural pipeline could be judged repetitive by YouTube (`SHORTS_STRATEGY.md` §1.5, §13) | Use a distinct story and assets per video; vary voices and music |
| Stale tracker phases | The `tracker.json` phases block does not reflect reality | Update P1–P9 statuses |
| QC gap | `qc_check.py` does not fail on true peak above −1 dBTP (MURDER-01 is −0.4) | Add a TP check, or a limiter after AAC encoding |
| Font licences | Only `OFL_Anton.txt` is shipped; Oswald and Bebas Neue are also OFL but their licence files are missing | Add licence files |

---

## 7. What remains, next steps, and upload checklist

### Remaining work
1. Render, compose and QC the 21 queued videos (CAVE-01 in progress). Each needs a human/director `QC_REPORT.md` and thumbnails (`thumbs.json` + `thumbnail.py`).
2. Animate the 5 videos that are scripted but not animated: CAVE-07, SCUBA-07, MURDER-06, MURDER-07, HAUNT-07 (shots.py → preview → READY).
3. Script the next concepts by rank (CAVE-08 first, then ranks 8+ per niche), toward the RESUME_HERE goal of all 100.
4. Clear the 2 PROVISIONAL fact-checks (below).
5. Housekeeping: refresh the tracker.json phases block, enforce true peak in QC, set up Git LFS, prune RENDERS.

### Recommended next steps (priority order)
1. Keep the queue running with ≤4–5 agents. While it renders, write QC reports for each video as it finishes, and produce thumbnails in the same pass.
2. Fix the known cosmetic weaknesses **before** their queue slot comes up (re-touching READY re-renders): MURDER-02 "[crossed out]" literal text and dark S12; MURDER-04 S14 letter size; CAVE-02 S16; CAVE-03 S13.
3. Publish order by finished score: MURDER-01 (84) and HAUNT-01 (78) can go out now, after their pre-upload checks. Follow the strategy's 4–5/week cadence, rotating niches.

### Pre-upload checklist (per video)
- [ ] Open the snippet-only key sources in a normal browser (Wikipedia, NatGeo, FBI, SPR, etc.) and confirm every narrated line. Every FACTCHECK.md is snippet-based.
- [ ] **MURDER-02**: search "Somerton Man coroner finding" / Coroners Court of SA. If a finding is published, rewrite L18 + S18 and title variant B. The on-screen stamp says "status checked Nov 2026".
- [ ] **SCUBA-05**: re-check the Guinness "deepest scuba dive" record status (`"deepest scuba dive" Guinness record 2026`) and confirm Gabr still holds 332.35 m.
- [ ] **SCUBA-06**: run the 2 pending searches (breath-hold 1963; eye-gouge release). If either fails, swap in the verified fallback line from FACTCHECK.md.
- [ ] **MURDER-05**: confirm L17 (2007 Fürstenfeldbruck students' unnamed main suspect) via SZ/Merkur/BR. Otherwise use the contingency line in SCRIPT.md.
- [ ] **SCUBA-03**: add one more primary source for L09 (BBC 2019 or the *Last Breath* documentary).
- [ ] **HAUNT-05**: open the NRHP nomination or Filson resource for the tunnel description, and confirm the LiveScience article behind the 6,000–8,000 estimate.
- [ ] **HAUNT-01**: open the SPR / Wikipedia pages (the QC report flags this before upload).
- [ ] **HAUNT-02**: resolve the 1974 date conflict (King's late-September account vs Britannica).
- [ ] Title: use the primary title from `THUMBNAILS/<ID>/PACKAGING.md` (rejected titles are listed there); keep it 30–60 characters with the searchable noun first.
- [ ] Upload a custom thumbnail (A, keep B for testing); check that frame 1 + line 1 work as the feed "thumbnail".
- [ ] Description: list sources from SCRIPT.md, mark dramatisation, and include a note that the narration is AI-voiced. Altered/synthetic disclosure = No (stylised animation, no realistic real person) per `SHORTS_STRATEGY.md` §13.
- [ ] Audio: confirm no licensed music (all procedural) and loudness of about −14 LUFS.
- [ ] Ethics pass: faceless figures, no gore, labels on every disputed or paranormal claim, no uncharged private persons named.
- [ ] After upload, track viewed-vs-swiped, APV and engaged views against `SHORTS_STRATEGY.md` §12, and recalibrate the runtime bands after 5+ uploads per niche.


---
## Addendum — 2026-11-27 18:15 UTC (supersedes the counts above where they differ)
- **Narrator voice changed by the owner** to Kokoro `am_adam` ("Voice 03" of AUDIO/VOICE_SAMPLER). All 28 scripted Shorts were re-voiced
  with the timing lock (line starts and shot timing unchanged; 28/28 shot_timing.json files byte-identical before/after), so no animation
  or render was invalidated. Trade-off: in six Shorts first timed with a slower voice (HAUNT-01, HAUNT-04, HAUNT-07, SCUBA-02, SCUBA-06,
  SCUBA-07) most lines now end 0.2–0.5 s early, i.e. pauses between lines are ~0.25 s longer than designed.
- **Finished + QC PASS: 3** — HAUNT-01, MURDER-01 (both re-assembled in the new voice, no re-render) and CAVE-01 (one shot re-rendered
  after a visual QC fail). All three: -14.2 to -14.6 LUFS, true peak <= -1.1 dBTP.
- **Animated and READY: 28 of 28 scripted** (slates 1–4). Render queue order continues with MURDER-02.
- **Slate 5 scripting in progress** (CAVE-08, SCUBA-08, MURDER-08, HAUNT-10).
- Fact-checks: 28/28 VERIFIED (SCUBA-06 and MURDER-05 resolved; SCUBA-06 S03's unverified on-screen "no tank / breath-hold" claim removed).
- Fixed since the report: true-peak limiter + QC rule, font licence files, tracker phases, selection notes for CAVE-07/HAUNT-10.
- Still true: narration delivery has not been auditioned by ear inside this container (no audio playback) — owner listening is the check.
