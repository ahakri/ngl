# RESUME HERE (read first after any interruption)

Owner is away; work is fully autonomous. On every wake-up:
1. `bash YOUTUBE_ANIMATION_STUDIO/PIPELINE/setup_env.sh` (restores Blender bpy, Kokoro TTS, fonts if the container was recycled).
2. Ensure the render queue daemon runs: `pgrep -f render_queue.sh || (cd PIPELINE && nohup ./render_queue.sh >/dev/null 2>&1 &)`. Then read `PROJECT_TRACKER/tracker.json` + `STATUS.md`; pick the next non-done task in phase order; never redo a `done` item.
3. Keep agents busy: research → concepts → scripts → storyboards → animation → render → edit → QC → improve.
4. Commit + push to branch `claude/adoring-maxwell-qk4kas` after every meaningful deliverable.
5. Bounded retries: max 3 QC cycles per deliverable, then log in BLOCKERS.md and move on.

Completion criteria: see PROJECT_BRIEF.md + master prompt section 11. When the selected slate is rendered and QC'd, expand the slate (next-best concepts) until all 100 have scripts, then keep rendering by rank.

Narrator: the owner chose Kokoro voice `am_adam` (sampler voice 03) on 2026-11-27. It is enforced by `PIPELINE/studio_config.json`.
Animated videos are timing-locked (`AUDIO/<ID>/timings_ref.json`): `make_video.py <ID> tts` re-voices without moving shot boundaries;
finished videos are updated with `python3 PIPELINE/compose.py <ID>` (no re-render) followed by `python3 PIPELINE/qc_check.py <ID>`.

## Keeping renders alive (read this on every wake-up)
- The machine stops ~5 minutes after the last tracked task ends; the detached render queue dies with it. On every wake-up:
  1. `pgrep -f render_queue.sh || (cd PIPELINE && setsid nohup ./render_queue.sh >/dev/null 2>&1 < /dev/null &)`
  2. start a tracked background watcher with the 2-hour maximum timeout (a loop that waits for the next DONE/FAIL line in
     `PROJECT_TRACKER/render_queue.log`), so the machine stays up.
- Preferred path: the GitHub Actions render farm. To render videos there, list them in `PROJECT_TRACKER/ci_claimed.txt` (local queue skips them)
  and push a change to `PROJECT_TRACKER/ci_render_request.json` (`{"requests": [{"id": "HAUNT-02"}, ...]}`; add `"reuse_frames": true` and
  `"rerender": ["S12"]` to re-assemble / partly re-render from the frames artifact of an earlier run). Each job commits
  `FINAL_VIDEOS/<ID>.mp4`, `QUALITY_CONTROL/<ID>/QC_AUTO.json`, `qc_frames.png` and `PROJECT_TRACKER/ci_runs/<ID>.json` to the branch:
  `git pull --no-rebase --no-edit origin claude/adoring-maxwell-qk4kas` before committing locally.
- After a video arrives: look at `QUALITY_CONTROL/<ID>/qc_frames.png`, fix overlay issues in script.json, re-assemble (locally if the frames
  are here, otherwise via a CI request with reuse_frames), then write `QUALITY_CONTROL/<ID>/QC_REPORT.md` with `VERDICT: PASS`.
- Go easy on agents: each animation agent uses a large share of a 5-hour usage window. Rendering and QC come first.

## PAUSED by the owner — 2026-11-28 02:05 UTC
- Hourly heartbeat disabled (trigger "Studio overnight heartbeat"), local render queue stopped, no agents running.
- 20 of 32 Shorts finished (QC PASS). Still pending, already requested on the CI render farm before the pause (results land on the branch by
  themselves): re-assembly of SCUBA-05, CAVE-02, CAVE-03, CAVE-05, CAVE-07, SCUBA-07, HAUNT-07, SCUBA-08; MURDER-03 S16 re-render;
  first renders of MURDER-07, MURDER-08, HAUNT-10. On resume: `git pull`, review those with QC, re-enable the heartbeat.
