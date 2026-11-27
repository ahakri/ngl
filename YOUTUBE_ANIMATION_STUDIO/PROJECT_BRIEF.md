# YOUTUBE ANIMATION STUDIO — Project Brief & Agent Handoff Spec

This file is the contract every agent works from. Read it before writing anything.

## Format decision: YouTube SHORTS
The owner stated these videos are for **YouTube Shorts**. Therefore:
- Aspect 9:16 vertical, 1080x1920 delivery, 24 or 30 fps.
- Target runtime 45–75 s (Shorts may run up to 3 min since Oct 2024; research decides the sweet spot per niche).
- Hook must land in the first 1–2 s (Shorts feed swipe decision), not 15 s. The "15-second hook" field in concepts is written as: 0–2 s visual+line, 2–6 s escalation, 6–15 s stakes.
- Loopability (ending that flows into the opening) is a known Shorts retention technique — evaluate it per story.
- Burned-in captions (word-synced) are standard in the niche; all videos carry them.
- Long-form reference videos are still valid evidence for *topic demand*; Shorts references are evidence for *format*.

## Animation reality (what the pipeline can actually produce)
Toolchain verified in this container: Blender 5.0 (bpy, Python 3.11, headless, Cycles + EEVEE on CPU, no GPU), Kokoro neural TTS (24 kHz; studio narrator voice = am_adam, set in PIPELINE/studio_config.json), ffmpeg, sox, numpy, Pillow.
- 3D procedural environments: caves, wrecks, reefs, rooms, corridors, forests, roads, houses, maps, evidence boards.
- Characters: stylised/low-poly procedural divers and silhouettes with simple rigs (walk/swim/turn). No photoreal faces.
- Effects: volumetric fog, particles (silt, bubbles, dust), flashlight cones, caustics, lightning, flicker.
- 2.5D motion graphics: animated maps, timelines, text callouts, document reveals.
- No AI image generation, no stock footage, no real photos of victims.
Concepts must list scenes that fit this reality; score "Animation feasibility" honestly against it.

## Ethics & accuracy rules
- Real people: do not invent dialogue, motives or facts. Mark anything uncertain as "reported", "alleged", "disputed".
- Murder/mystery: no graphic gore, respect victims, no naming of uncharged private individuals as suspects. Living suspects only as stated in court/official records.
- Paranormal: every claim labelled as DOCUMENTED FACT / EYEWITNESS CLAIM / FOLKLORE / DRAMATISATION.
- Never fabricate a YouTube URL, view count, or upload date. If a number could not be confirmed from a fetched page or search snippet, write `unverified` and say where the figure came from. youtube.com itself is NOT reachable from this container; use web search results, Social Blade, news articles, and other indexed pages.

## Shared file conventions
- Research reports: `RESEARCH/<NICHE>/RESEARCH_REPORT.md` + `RESEARCH/<NICHE>/reference_videos.csv`
  (csv columns: `title,creator,url,views,upload_date,channel_subs,format(short|long),evidence_source,notes`)
- Concepts: `VIDEO_IDEAS/<NICHE>_20/CONCEPTS.md` (human) + `VIDEO_IDEAS/<NICHE>_20/concepts.json` (machine).
- Concept IDs: CAVE-01..20, SCUBA-01..20, MURDER-01..20, HAUNT-01..20 (numbered by rank after scoring, 01 = best).
- concepts.json: list of objects with keys:
  `id, number, category, working_title, alt_title, subject, why_potential, references (list of {title,creator,url,views,note}), duration_s, hook_15s, structure (list of beats), retention_moments (list), thumbnail_concept, animation_style, scenes (list), sources (list of urls/citations), difficulty (Low|Medium|High), scores {demand, story, packaging, retention, feasibility}, total, rank, fact_labels (paranormal only, optional)`
- Scores: each axis 0–20, total 0–100. Calibrate: a typical good idea ≈ 65–75; >85 needs explicit evidence (multiple strong performing references). Do not inflate.

## Pipeline stages (tracked in PROJECT_TRACKER/tracker.json)
RESEARCH → ANALYZE → GENERATE → EVALUATE → SELECT → SCRIPT → STORYBOARD → ANIMATE → EDIT → QC → IMPROVE
Max 3 QC retry cycles per deliverable; after that, log a blocker in `PROJECT_TRACKER/BLOCKERS.md` and move on.
