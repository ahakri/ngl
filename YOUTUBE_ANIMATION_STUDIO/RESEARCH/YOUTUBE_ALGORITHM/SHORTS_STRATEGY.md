# Shorts Strategy — Animated Story Channel (cave diving / scuba / murder-mystery / haunted)
Agent 1, 2026-11-27. Evidence base: `ALGORITHM_REPORT.md` (section refs as §x). Tags: [OFFICIAL] / [CREATOR RESEARCH] / [HYPOTHESIS]. **All numeric thresholds are [HYPOTHESIS] starting points** unless tagged otherwise; recalibrate after the first 20 uploads against our own channel medians.

## 1. Core principles (why)
1. Feed Shorts have no thumbnail click; the swipe decision is the "click". Optimise the **first frame + first line** like a thumbnail. (§1.5, §4) [OFFICIAL basis + HYPOTHESIS]
2. Relative watch time (% viewed) matters more for short videos. Shorter-but-complete beats longer-but-leaky. (§1.4) [OFFICIAL]
3. YouTube optimises for satisfaction (surveys). No clickbait that the video doesn't pay off. (§1.3) [OFFICIAL]
4. Public view count is inflated since Mar 2025 (first-frame); judge on **engaged views, viewed-vs-swiped, APV**. (§2) [OFFICIAL]
5. TTS + procedural pipeline is at risk of "inauthentic content" judgement → every Short must be visibly distinct, researched, and editorially voiced. (§3) [OFFICIAL policy + HYPOTHESIS]

## 2. Target runtime band per niche [HYPOTHESIS, informed by Galloway 50–60 s finding and Adobe <30 s survey; no data exists for 60–180 s]
| Niche | Start band | Hard cap until data | Rationale |
|---|---|---|---|
| Cave diving incidents | 50–70 s | 90 s | Needs geography + mistake + consequence; maps/line diagrams carry exposition fast. |
| Scuba stories | 40–60 s | 75 s | Single-moment stories (encounter, equipment failure) resolve quicker. |
| Murder/mystery | 55–80 s | 120 s | Case setup + clue + twist; consider 2–3 part series instead of exceeding 90 s. |
| Haunted/paranormal | 35–55 s | 75 s | Atmosphere + one claim + unresolved ending; shortest band, best loop candidates. |
Rule: only lengthen a niche's band after 5+ uploads at the current band show APV ≥ channel median **and** viewed-vs-swiped ≥ channel median. Avoid licensed music entirely (a claimed Short >60 s is blocked globally [OFFICIAL]).

## 3. Hook rules (0–3 s)
1. **Frame 1 is content**: no logo, intro, fade from black, or title card. Start mid-action (light cone in silt, flashlight on a door, evidence photo slamming onto board). [HYPOTHESIS]
2. **Line 1 lands by 1.5 s** and states stakes or anomaly in ≤12 words: "This diver had 4 minutes of air and the exit was gone." Avoid "Did you know…" / "Wait for it". [HYPOTHESIS]
3. **Visual + verbal + text agree**: the on-screen caption of line 1 is the hook; large, center-upper third. [HYPOTHESIS]
4. 2–6 s: escalate (new fact or complication); 6–15 s: define what the viewer will get (the "why/what happened"). (Matches PROJECT_BRIEF.) 
5. Motion within first 0.5 s (camera push, particles, light flicker) — a static first frame reads like a still image. [HYPOTHESIS]
6. Real-case Shorts: hook must be factually defensible (labels "reported/alleged" in narration where needed). Satisfaction > shock. [OFFICIAL basis §1.3 + ethics brief]

## 4. Narration pace & script length
- **150–165 WPM** for Kokoro narration (vendor guidance 140–160 WPM [CREATOR RESEARCH]; slightly faster acceptable for tension). Test: render at 1.0 and 1.08 speed; pick the one that stays intelligible on phone speakers.
- Script word budget ≈ runtime_s × 2.5 (e.g., 60 s ≈ 150 words) minus ~10% for SFX beats/pauses. [HYPOTHESIS]
- Sentences ≤14 words; one idea per sentence; proper nouns introduced once with on-screen spelling.
- Tension beats: allow 0.4–0.8 s silence with SFX before reveals (max 2 per Short). [HYPOTHESIS]

## 5. Cut frequency / visual change
- New shot or significant visual change every **1.5–3 s** (camera move, cut, overlay, map zoom). Never hold a static frame >4 s. [HYPOTHESIS; common creator practice, no study found]
- "Pattern interrupt" every ~8–12 s: a new visual mode (3D scene → map → evidence card → back). Use the retention graph to find dips and place interrupts there in later videos.
- Pipeline note: procedural Blender shots can be reused across videos only with distinct framing/lighting; repeated identical shots across uploads increases inauthentic-content risk. [HYPOTHESIS based on §3]

## 6. Captions
- Burned-in, word-synced, 1–4 words per caption chunk, centered in the safe zone (avoid bottom ~20% and right ~15% where Shorts UI overlays sit). [HYPOTHESIS; UI overlay positions vary by device]
- High-contrast (white with dark stroke/shadow); highlight keyword per line (one accent color per niche: cave = cyan, scuba = teal, murder = red, haunted = pale green). 
- Also upload a clean SRT (accessibility, search). Evidence on captions is vendor-grade and not Shorts-specific (§6), so keep but don't over-design. [CREATOR RESEARCH + HYPOTHESIS]

## 7. Endings & loops
- Default ending: **payoff in the last 3–5 s, then cut hard** — no "subscribe" outro, no fade. [HYPOTHESIS]
- Loop ending where the story allows: last line grammatically flows into the first line (e.g., end "...and that's why nobody goes past the restriction." → opening "This diver had 4 minutes of air."). Best fits haunted (unresolved) and cave (return to entry point). Replays count as public views and add watch time [OFFICIAL/CREATOR RESEARCH]; their weight in ranking is unknown.
- Don't fake a loop on true-crime case endings if it disrespects the victim or muddles facts — clean payoff instead.
- Optional series hook in final 2 s on-screen only ("Part 2 on channel") — test against control.

## 8. Series / playlist strategy
- Build **named series** per niche (e.g., "Line Lost" cave incidents, "Dead Air" scuba, "Cold File" murder, "Recorded Claim" paranormal) with consistent opening visual grammar so returning viewers recognise them. [HYPOTHESIS]
- One playlist per series; add every Short. Multi-part cases (murder) as Part 1/2/3 posted 24–48 h apart, each standalone-satisfying with a cliffhanger.
- Use the **related video link** on each Short to point to Part 1 / the next part / the best-performing Short in that series (later: the long-form). [OFFICIAL feature]
- Watch the Studio announcement for a native Shorts series/episodes feature (reported 2026, unverified) and adopt if available.

## 9. Posting cadence
- Start at **4–5 Shorts/week** (rotate niches so each gets ~1/week) for 8 weeks, never trading quality for volume (YouTube: volume alone doesn't change reach, low-quality spam can hurt [OFFICIAL, reported]). [HYPOTHESIS for the number]
- After 8 weeks: double down on the niche(s) with best medians; drop a niche to 1 per 2 weeks if it is bottom quartile on both viewed-vs-swiped and APV for 6+ uploads.
- Post time: irrelevant early; later use Studio "When your viewers are on YouTube". Don't delete/re-upload underperformers (Sherman: not a good strategy).
- Consider channel focus: 4 niches dilute the audience signal. [HYPOTHESIS] Underwater (cave+scuba) and dark (murder+haunted) are two clusters; if the first 20 uploads show one cluster clearly winning, consider a second channel for the other.

## 10. Title rules for Shorts
- 30–60 characters, readable in the feed overlay; front-load the noun people search ("Cave diver", "Blue Hole", case name). [HYPOTHESIS + vidIQ title/search claim]
- Title ≠ the spoken hook verbatim; it complements it (hook = moment, title = topic).
- 0–2 hashtags max, only niche-specific (#cavediving, #truecrime); #shorts unnecessary (no verified effect).
- No fabricated claims; for paranormal include framing words ("claimed", "reported") when it's an eyewitness claim.
- Set a **custom Shorts thumbnail / chosen frame at upload** (feed ignores it; search, channel grid and related-video links show it). Readable title card frame, 1–3 words, high contrast. [OFFICIAL feature, rollout varies]
- Test & Compare is not available for Shorts [OFFICIAL]; A/B by posting variants only across different stories, never re-uploading the same video.

## 11. Long-form later
- Trigger [HYPOTHESIS]: any topic whose Short reaches ≥2× channel median engaged views **and** comments ask for "more/full story" → produce a 8–15 min long-form deep dive (same Blender assets, horizontal re-render).
- Link: every Short in that topic gets its related video link pointed at the long-form; long-form end screen points to the series playlist.
- Keep Shorts ≤ ~55% of total output once long-form starts (AIR correlation finding, not causal [CREATOR RESEARCH]).
- Long-form uses thumbnail/title A/B (Test & Compare) — available there, unlike Shorts.

## 12. Metrics to watch in YouTube Studio & decision thresholds
All thresholds are [HYPOTHESIS] and expressed relative to the channel's rolling median of last 20 Shorts (absolute industry benchmarks conflict wildly, §4). First 20 uploads: collect only, no kills.
| Metric (Studio) | Read at | Action threshold |
|---|---|---|
| **Viewed vs swiped away** (Shorts) [OFFICIAL metric] | 48 h & 7 d | < median −10 pts → rework first 2 s style (frame 1, line 1) for next uploads in that niche. Vendor folklore "~70% viewed" is NOT a known cutoff. |
| **Average percentage viewed (APV)** | 7 d | < median −15% → cut length band by 10 s for that niche. ≥ median +15% for 5 uploads → allowed to extend band by 10 s. |
| **Audience retention curve** | 7 d | Any drop >15 pts within 1 s outside the first 3 s = a dead beat → log timestamp + cause in QC notes. Spikes >100% = rewatched moment → reuse that device. |
| **Engaged views** (Advanced mode) | 7 d / 28 d | Primary success KPI (not public views). Topic winner = ≥2× median. |
| Subscribers gained per 1k engaged views | 28 d | Series with highest ratio get priority slots. |
| Likes, comments, shares per 1k engaged views | 7 d | Shares are the strongest audience signal for us [HYPOTHESIS]; comments asking for more → long-form/part-2 candidate. |
| Traffic source (Shorts feed vs search vs channel) | 28 d | If search >15% for a niche → invest in searchable titles/custom thumbnails there. |
| New vs casual vs regular viewers | monthly | Rising casual+regular share = series working. (No effect on reach per YouTube [OFFICIAL].) |
| "Shown in feed" growth curve | 1–7 d | Flat after a few hundred/thousand = normal stall per Sherman; don't re-upload. |
Kill rule [HYPOTHESIS]: a niche/format is paused if 6 consecutive uploads are below median on both viewed-vs-swiped and APV.

## 13. Compliance checklist per upload
- Original script with cited sources; no near-duplicate structure/assets vs previous 10 uploads (inauthentic-content risk).
- No licensed music; SFX/music owned or royalty-free with license logged.
- Altered/synthetic disclosure: animation = not required [OFFICIAL]; answer "Yes" only if any realistic depiction of a real person/voice is synthesised (we should not do that).
- Real-case ethics per PROJECT_BRIEF (reported/alleged labels, no gore, no naming uncharged private persons).
