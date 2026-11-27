# Script + Storyboard + Packaging Spec (handoff to the animation pipeline)

Per selected video `<ID>` (e.g. CAVE-01) produce:

1. `SCRIPTS/<ID>/script.json` — machine file consumed by the pipeline (schema below).
2. `SCRIPTS/<ID>/SCRIPT.md` — readable narration script with timing estimates, fact labels, and a source list with the claim each source supports.
3. `STORYBOARDS/<ID>/STORYBOARD.md` — shot-by-shot board: per shot: visual description, camera, characters, environment, lighting, FX, on-screen text, SFX, music, transition, narration line(s) covered.
4. `THUMBNAILS/<ID>/PACKAGING.md` — ≥2 title variations, ≥2 thumbnail concepts (composition, focal subject, colour contrast, text ≤3 words or none, the one visual idea, why it creates a curiosity gap), Shorts description + hashtags, related-video link target.
5. `QUALITY_CONTROL/<ID>/FACTCHECK.md` — every factual claim in the narration → ≥2 sources (URL) or labelled reported/disputed/removed.

## Format rules (from RESEARCH/YOUTUBE_ALGORITHM/SHORTS_STRATEGY.md + niche FORMAT TEMPLATEs)
- Vertical Short. Runtime bands: cave 50–70 s, scuba 40–60 s, murder 55–80 s, haunted 35–55 s.
- Narration ≈150–165 wpm (Kokoro voice at speed ~1.05–1.1). So 60 s ≈ 150–160 words total.
- Frame 1 is already mid-story; line 1 lands within ~1.5 s and contains the strangest concrete detail or stakes. No "In this video", no greetings, no channel plugs.
- A new visual every 1.5–3 s (shots 2–5 s; camera moves inside shots count as change).
- Reveal new information at least every ~5–7 s; one mid-point turn; payoff in the last 8 s; optional loop line that flows back into line 1.
- Respect ethics in PROJECT_BRIEF.md (no gore, no invented dialogue/quotes for real people, label claims).

## Animation constraints (the pipeline: Blender procedural, PIPELINE/blender/studio_lib.py)
Available builders: cave_tunnel (flooded tube along a path), stalactites, boulders, guideline, water_volume, particle_cloud (silt/dust),
bubbles_stream, char_diver (stylised diver: sidemount/doubles/single tank, helmet torch), anim_swim, char_figure (faceless silhouette human, optional coat),
anim_walk, shark, seabed, coral_field, fish_school, shipwreck (steel hull, superstructure, broken), caustics_light, room (box room with door/window),
corridor (institutional hallway with doors + lamps), house_exterior (two-storey gabled house, lit windows), tree / forest (bare trees), road, ground,
fog_volume, table/bed/chair props, text3d, spot/point/area/sun lights, flicker (light flicker/blackouts), camera + cam_keys + handheld.
2D overlays (composited, PIL): date/location stamp, depth gauge, timer/counter, map with route line, timeline, document/letter reveal, evidence card, fact-label badge (DOCUMENTED / WITNESS CLAIM / FOLKLORE / DRAMATISATION).
Shots must be describable with those parts (new simple props are fine: describe them precisely). No real photos, no faces of real people.

## script.json schema
```json
{
  "id": "CAVE-01",
  "title": "...", "category": "cave|scuba|murder|haunted",
  "voice": "am_michael", "speed": 1.07, "mood": "cave|scuba|murder|haunted",
  "target_seconds": 60,
  "lines": [
    {"id": "L01", "text": "narration sentence(s)", "pause_after": 0.25, "shot": "S01", "emphasis": ["words", "to", "highlight"]}
  ],
  "shots": [
    {"id": "S01", "lines": ["L01"], "environment": "cave_tunnel|open_water|reef|wreck|room|corridor|house_exterior|road_night|forest|mountain_snow|map|timeline|document|other:<desc>",
     "description": "what we see, concretely", "camera": "move + lens + framing", "characters": ["diver_A (yellow fins)", ...],
     "lighting": "...", "fx": ["silt", "bubbles", ...], "overlay": [{"type": "stamp|depth|timer|map|timeline|document|label|text", "text": "...", "params": {}}],
     "sfx": [{"name": "bubbles|breath|heartbeat|boom|hit|whoosh|riser|rumble|creak|static|thunder|footsteps|door_creak|click|typewriter|underwater_amb|wind|metal_groan|sonar|sting", "offset": 0.0, "gain": 0.6}],
     "transition_in": "cut|fade_black|whip|flash"}
  ],
  "music_curve": [[0, 0.5], [30, 0.8], [55, 1.0], [60, 0.4]],
  "loop_line": "optional final line designed to flow into line 1"
}
```
`offset` in sfx is seconds from the shot start. Shot durations are derived automatically from the narration timing of their lines.
