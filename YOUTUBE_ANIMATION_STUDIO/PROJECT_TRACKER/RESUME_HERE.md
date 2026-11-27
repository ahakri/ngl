# RESUME HERE (read first after any interruption)

Owner is away; work is fully autonomous. On every wake-up:
1. `bash YOUTUBE_ANIMATION_STUDIO/PIPELINE/setup_env.sh` (restores Blender bpy, Kokoro TTS, fonts if the container was recycled).
2. Ensure the render queue daemon runs: `pgrep -f render_queue.sh || (cd PIPELINE && nohup ./render_queue.sh >/dev/null 2>&1 &)`. Then read `PROJECT_TRACKER/tracker.json` + `STATUS.md`; pick the next non-done task in phase order; never redo a `done` item.
3. Keep agents busy: research → concepts → scripts → storyboards → animation → render → edit → QC → improve.
4. Commit + push to branch `claude/adoring-maxwell-qk4kas` after every meaningful deliverable.
5. Bounded retries: max 3 QC cycles per deliverable, then log in BLOCKERS.md and move on.

Completion criteria: see PROJECT_BRIEF.md + master prompt section 11. When the selected slate is rendered and QC'd, expand the slate (next-best concepts) until all 100 have scripts, then keep rendering by rank.
