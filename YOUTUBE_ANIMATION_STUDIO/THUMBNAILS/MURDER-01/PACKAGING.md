# MURDER-01 — Packaging (Dyatlov Pass)

Shorts feed shows no thumbnail: **frame 1 + line 1 are the real packaging** (S01: torch beam finding the slit in an orange tent wall, VO "Nine hikers cut their own tent open."). Title/thumbnail below matter for search, the channel grid and related-video links.

## Titles (30–60 chars, searchable noun up front, no unsupported claims)

| # | Title | Chars | Use |
|---|---|---|---|
| A (primary) | Dyatlov Pass: Why They Cut Their Tent From Inside | 49 | Search noun first + the core mystery. |
| B | Nine Hikers Cut Their Tent Open From the Inside | 47 | Concept title; pure curiosity gap for feed/related links. |
| C | Dyatlov Pass: Can Disney's Frozen Code Explain It? | 50 | Twist-led; question framing because the study doesn't claim a solution. |

Rejected: "Science Finally Solved Dyatlov Pass" (the authors explicitly say it isn't solved — would fail the satisfaction test and our fact-check).

## Thumbnail / chosen-frame concepts (1080x1920 custom thumbnail; ≤3 words)

**Concept 1 — "CUT FROM INSIDE" (primary)**
- Composition: orange tent fills the lower-middle third at a slight Dutch angle on blue moonlit snow; a single vertical slit glows warm from a torch inside; snow streaks across frame.
- Focal subject: the glowing slit (brightest pixel area, centred upper-middle).
- Colour contrast: saturated orange/warm amber vs. deep blue/cyan night — complementary.
- Text: **CUT FROM INSIDE** (3 words), white Anton with dark stroke, top third; "INSIDE" in murder-red.
- One visual idea: a tent opened the wrong way.
- Curiosity gap: why would anyone slash their own shelter in a blizzard? The image states the anomaly without explaining it.

**Concept 2 — "FROZEN?"**
- Composition: split frame — top half the wireframe slope from S12 (cyan lines on black), bottom half the same slope in 3D snow with a cracked slab poised above a tiny orange tent; crack line glowing red.
- Focal subject: the red crack line above the tent.
- Colour contrast: cyan/black digital vs. white/blue snow, single red accent.
- Text: **FROZEN?** (1 word) centred on the split line.
- One visual idea: a cartoon's snow code aimed at a real mystery.
- Curiosity gap: what does a Disney movie have to do with nine deaths in 1959? Viewer must watch for the link.

## Shorts description (paste-ready)

In February 1959, nine experienced hikers left their tent on Kholat Syakhl in the northern Urals after cutting it open from the inside. In 2021, Johan Gaume (EPFL) and Alexander Puzrin (ETH Zürich) modelled a delayed slab avalanche — using snow-simulation code adapted from Disney's Frozen. It's a model, not a final answer. What do you think happened?

Sources: Gaume & Puzrin, Communications Earth & Environment 2, 10 (2021), doi:10.1038/s43247-020-00081-8 · TASS / RFE/RL on the 2020 prosecutors' conclusion · National Geographic (2021). Animated dramatisation; no real footage.

In memory of the nine members of the Dyatlov group.

Hashtags (max 2): #DyatlovPass #unsolvedmysteries

## Related video link

Point to MURDER-02 (Somerton Man) — same *Cold File* series, "science reopens an old case" pairing. Once a *Cold File* playlist exists, link the playlist's best performer instead.

## Pinned comment (optional)

"The 2021 study explains the slab — not the long walk into the trees. Which part still bothers you most?"

## Final thumbnails

Hero stills are purpose-built compositions in `BLENDER_PROJECTS/MURDER-01/thumbs_shots.py` (`THUMB_A`, `THUMB_B`; the video source `shots.py` is untouched). They were rendered at 1080x1920 with EEVEE at 16 samples to `hero_THUMB_A/0020.png` and `hero_THUMB_B/0020.png`, then composed by `PIPELINE/thumbnail.py` from `thumbs.json`. Both are stylised 3D recreations: no real photos, no people, no bodies, no weapons, nothing suggesting aliens or an attacker.

| Thumbnail | Files | Text | Pairs with title |
|---|---|---|---|
| **A: "CUT FROM INSIDE"** | `thumb_A.png` (9:16), `thumb_A_16x9.png` | CUT FROM INSIDE (3 words, white, orange glow) | **A**: "Dyatlov Pass: Why They Cut Their Tent From Inside" (also B) |
| **B: "FROZEN?"** | `thumb_B.png` (9:16), `thumb_B_16x9.png` | FROZEN? (1 word, cyan) | **C**: "Dyatlov Pass: Can Disney's Frozen Code Explain It?" |

**A: the gash in the tent.** The orange canvas tent sits on blue moonlit snow at night. On the downhill roof a single long slit is open, with its flaps pushed *outward*, and warm lantern light pours out of it. The tent is empty and no one is in frame.
- The one idea: a shelter opened the wrong way, from the inside.
- Curiosity gap: why would anyone slash their own tent open in a blizzard? The image shows only the documented fact (the cut), and the Short's hook and VO answer with the evidence and the 2021 model.
- Contrast: one hot orange stripe (the brightest area, centre frame) against cold blue snow and a dark sky. Orange against blue is complementary. The text sits in the top band, above the subject.

**B: the slope becomes a simulation.** The small lit tent sits on real snow. Directly above it the slope turns into a cyan simulation wireframe, crossed by one red crack line just uphill of the tent (where a slab would release in the Gaume & Puzrin model).
- The one idea: a computer model aimed at the slope above the tent.
- Curiosity gap: what does *Frozen* have to do with a 1959 mystery? Title C explains the link ("Disney's Frozen code"). The question mark and the question-form title keep it honest, since the authors say the model is not a final answer. The image shows a hypothesis drawn as a diagram, not an event.
- Contrast: cyan grid on black, a red accent line and a warm tent on blue-white snow. Cyan type sits on the dark sky.

**Recommended pick: A**, with title A, at upload. It matches the Short's frame 1 and line 1 (S01: the light finding the slit, "Nine hikers cut their own tent open."), so search and channel-grid viewers get exactly what the cover promised. It reads at grid size from one bright stripe, and it states only an established fact. **B** is the alternate. Shorts have no Test & Compare, so keep B (with title C) as the cover for a long-form or "science reopens the case" cut, where Test & Compare can test A against B. Do not re-upload this Short to test it.

Note for the 16:9 versions: B's 16:9 crop (`focus_16x9` 0.56) keeps the crack and the tent but places the word over the grid. It is legible because of the black stroke, but A is the stronger landscape image.
