# Cave Diving Niche — Research Report (Agent 2)

Date: 2026-11-27. Evidence file: `reference_videos.csv` (29 rows: 6 Shorts, 23 long-form).

## 0. Method and limits (read first)
- youtube.com, Wikipedia, Playboard, TheTVDB, Social Blade and fandom pages could **not be fetched** from this container (DNS blocked). All figures come from **search-engine snippets** of vidIQ, Playboard, Rosetta, Know Your Meme, TheTVDB and a fan wiki. Each CSV row names its snippet source.
- The shared web-search budget (200 calls per turn, all agents) ran out partway through this task. Some creator attributions and most per-video view counts for Shorts are therefore `unverified`.
- Labels used here: **[DATA]** = a figure from a tracker snippet. **[OBSERVED]** = a pattern seen in titles or snippets across several references. **[HYPOTHESIS]** = my inference, to be tested with our own analytics.

## 1. Who actually covers cave diving (verification of the brief's list)

| Creator | Covers cave diving? | Evidence |
|---|---|---|
| **FatalBreakdown** (~250K subs, 57 videos, 45.5M views) | **Yes, core niche.** 3D-animated reconstructions of caving and diving disasters. | vidIQ [DATA] |
| **Scary Interesting** (~2.05M subs, ~395M views) | **Yes, heavily.** Narrated with reconstructions; recurring "Cave Diving Gone Wrong" / "Cave Exploring Gone WRONG" episodes. | vidIQ, Playboard, TheTVDB snippets |
| **MrBallen** | **Yes, occasionally.** The Shaft ("This hole has killed 16 people", 7.1M), Bushman's Hole (covered per LADbible), New Mexico Blue Hole. Narrator-to-camera. | Rosetta, LADbible snippets |
| **DIVE TALK** (~433K subs, ~92M views) | **Yes.** Expert reactions; accident breakdowns are among its most popular videos (Mel Magazine). | vidIQ, Social Blade, Mel Magazine snippets |
| **Zack D. Films** | **Yes, at least one Short.** "Tham Luang Cave Rescue (explained)", 0:51, reported at 60M views (fan wiki, unverified). Also animated Nutty Putty (per LADbible). | fan wiki snippet, LADbible |
| "Cave Stories" (animation series, reuploaded to Dailymotion) | **Yes.** Animated incidents such as The Shaft and Ease Gill; YouTube channel size unknown. | Dailymotion and recapio snippets |
| Fascinating Horror (1.46M subs) | **No cave-diving video found.** | vidIQ/Playboard returned none |
| Plainly Difficult (~1.1M subs) | **No cave-diving video found.** | none returned |
| Wendigoon | **No cave-diving video found.** | none returned |
| Lazy Masquerade / Disturbing Things / Bedtime Stories | **No cave-diving video found.** | TheTVDB listings showed none |

**Takeaway:** the long-form niche is concentrated in a few channels (Scary Interesting, FatalBreakdown, MrBallen, Dive Talk). Animated cave-diving Shorts are much less saturated: we found only a few Shorts, mostly generic narrated slideshows. The one confirmed 3D-animated big hit in Shorts format is Zack D. Films' Tham Luang.

## 2. Outliers and what they tell us
1. **FatalBreakdown, Nutty Putty: 13.09M views on a 250K-sub channel (~52x subs).** It gained 3.2M views in its first 3 weeks (Know Your Meme). The format is a 3D reconstruction of a body stuck in a tight space. Claustrophobia rendered literally on screen is the single strongest proven trigger. [DATA]
2. **FatalBreakdown, Paria (5.03M, ~20x subs).** Divers were sucked into a pipe: a "pulled into a tube" physics hazard that is easy to show in 3D. [DATA]
3. **Dive Talk, "Bodies found at World's Deadliest Dive Site" (9.15M, ~21x subs).** The triggers are body recovery plus a superlative place. [DATA]
4. **MrBallen, The Shaft (7.1M).** A harmless-looking hole in a paddock that "killed N people". The trigger is a mundane entrance with lethal depths below. [DATA]
5. **Zack D. Films, Tham Luang (60M, unverified).** A rescue with hope. It shows that not every hit is a death story. [DATA, unverified]
6. Within FatalBreakdown, **true cave-diving cases (Jacob's Well 1.51M) earn about 1/9 of Nutty Putty's views.** Dry entrapment beats underwater technical stories when the viewer needs no explanation of the danger. [DATA → HYPOTHESIS]

## 3. Storytelling structure (long-form leaders, adapted to Shorts)

### Cold open vs chronological [OBSERVED]
- Leaders **open on the place or the danger, not the person.** Titles and descriptions lead with the hazard: "Dead end traps cave divers", "Sucked into an oil pipe", "Caver's Only Light Breaks 1000 Feet Into Cave". Description openers state the setting ("On February 6th 2014, five divers cut a triangular hole in the ice...").
- Long-form then runs **chronologically** after a 1–2 line cold open. Shorts have no room for that. Our template uses an **in-media-res cold open** (the moment of failure), a **rewind** ("12 minutes earlier..."), and a **forward run**.

### First 2 / 5 / 15 seconds (Shorts adaptation) [HYPOTHESIS built on the observed title formulas]
- **0–2 s:** one image of the hazard (silt cloud swallowing a light, a line ending in nothing, a gauge needle) plus a line of 12 words or fewer stating resource and stakes. Example: "He was 270 metres down. His exit was 12 hours away."
- **2–5 s:** a complication that makes it worse ("...and he'd just found the body he came for").
- **5–15 s:** what we will learn ("This is why he never came back"). Include one map or depth card showing scale.

### How background is introduced [OBSERVED]
- Background arrives **as a dependency of the danger, never as biography first.** Depth is explained because it sets decompression time. Narrowness is explained because it means no turning around. Shorts should spend at most 1 sentence on a person ("50-year-old Australian pilot, Dave Shaw").
- **Cross-sections and depth bars** do the explaining (Scary Interesting, FatalBreakdown). A side-section of the cave with a moving diver dot is the genre's core visual. It is also the cheapest thing for our Blender pipeline to make.

### Reveal frequency
- Long-form: a new complication every ~60–90 s. **Shorts: a new fact or turn every 6–10 s** (6–8 turns in 60 s), matching the studio rule of a pattern interrupt every 8–12 s. [HYPOTHESIS]

### Narration and visual interplay [OBSERVED in FatalBreakdown/Zack D.; HYPOTHESIS for us]
- Narration is sparse and declarative. Visuals carry the dread: slow push-ins, light cones, particles.
- Visuals should run **one beat ahead** of narration (show the silt rising before the line "visibility dropped to zero").
- Numbers on screen: depth (m and ft), air remaining (bar or minutes), and time-in-cave counters. A **ticking counter** is the strongest retention device in the niche (air, decompression clock, hours trapped).

### Cliffhangers and endings
- Long-form ends on the aftermath: body recovered, cave sealed, rules changed. The Nutty Putty "cave sealed with concrete, body still inside" ending is widely repeated in coverage (LADbible, HowStuffWorks). [OBSERVED]
- **Shorts ending options:** (a) **hard factual payoff** (most real cases), or (b) **loop**: the last line returns to the entrance ("...and the entrance still looks like an ordinary pond."), flowing into the first frame. Cave stories loop naturally because they start and end at the same small hole. Don't force a loop on a death if it trivialises it.

### Thumbnail / cover-frame composition [OBSERVED from titles; Shorts covers are less important but the first frame acts as the thumbnail in feed]
- One diver silhouette, small, against a huge dark void or a tight squeeze. A single light source. A text overlay of at most 3 words or a number ("270 M", "4 MIN AIR"). A red line or arrow marking the danger point.

### Title structures and curiosity gaps [OBSERVED]
| Pattern | Example from references |
|---|---|
| [Visceral outcome] \| The [Place] [Incident] | "Dead end traps cave divers \| The Jacob's Well Diving Tragedy" |
| Place + kill count | "This hole has killed 16 people" |
| Single failure + depth | "Caver's Only Light Breaks 1000 Feet Into Cave", "BROKEN ROPE WHILE CAVE DIVING" |
| Mistake framing | "These Cave Divers Made a Horrifying Mistake" |
| Resource countdown | "Divers Trapped in a Cave With Only 5 Minutes of Oxygen Left" |
| Ironic quote | "'We Know What We're Doing' - The Mount Gambier Cave Diving Disaster" |
| Fake-discovery clickbait (avoid) | "Divers Finally Reached the Bottom of Jacob's Well — What Their Cameras Found..." |

### Emotional triggers ranked by evidence
1. **Entrapment / claustrophobia** (Nutty Putty 13M, Paria 5M, Floyd Collins 2M). Strongest.
2. **Body recovery / the dead left behind** (Dive Talk 9.15M, Shaw/Dreyer covered across many formats).
3. **Mundane entrance, lethal below** (The Shaft 7.1M, Eagle's Nest "Mount Everest of cave diving").
4. **Rescue against odds** (Tham Luang 60M, unverified). Hope plus a clock.
5. **Lost line / silt-out / light failure** (Scary Interesting titles). These work best inside one of the above, not alone.
6. **Air running out** (countdown titles). The best on-screen device, but rarely a hook on its own.

### What separates hits from average videos [HYPOTHESIS from the outlier set]
- Hits have **one physically intuitive danger** that needs no technical knowledge: stuck upside down, sucked into a pipe, the hole killed 16. Average videos need jargon (rebreather CO2, deco obligations) before the danger lands.
- Hits **show the space** in 3D or cross-section. Average videos rely on stock footage or stills.
- Hits make the **outcome or stakes clear from the title**. They sell how and why, not whether.
- Low performers open generically ("Cave diving is one of the most insane sports...", from a Plura Short) instead of on a specific moment.

## 4. Gaps and opportunities for us
- **Animated Shorts on true cave-diving incidents are thin.** Long-form covers the famous cases repeatedly, while Shorts coverage is mostly slideshow or narration. This is room for our 3D cross-section format. [HYPOTHESIS]
- Underused: **survival stories** (Xisco Gràcia's ~60 h in an air bell, 2017) and **discoveries** (Hoyo Negro's 12,000-year-old girl, Hranice depth). These broaden beyond death content and are safer for brand and advertisers.
- Ethics edge: several competitors re-use real death footage (Shaw helmet-cam, Lipski). **We never reproduce or trace it.** Reconstruct with stylised divers and no faces, and say "based on the recovered camera, as reported".

## 5. FORMAT TEMPLATE — CAVE DIVING SHORT (target 55–65 s; studio band 50–70 s, cap 90 s)

| Time | Beat | Visual (Blender-feasible) | Audio / text |
|---|---|---|---|
| 0.0–1.5 s | **Cold-open moment** | Mid-action: light cone in a silt cloud / gauge / line ending. Camera already moving at frame 1. | Line 1 (≤12 words): resource + stakes. Caption is the same line. |
| 1.5–5 s | **Complication** | Second angle: the same diver from a wider or tighter shot. | Line 2: the twist that makes it worse. |
| 5–10 s | **Promise + scale** | Cut to an animated side-section of the cave with a diver dot and depth bar (m/ft). | "This is [Place], and this is what happened." Place name spelled on screen. |
| 10–15 s | **Rewind** | Surface/entrance shot: pond, hole, ice. Calm, daylight. "[X] HOURS EARLIER" card. | One line on who (max 1 sentence) and why they were there. |
| 15–30 s | **Descent / rules** | Diver dot moves along the section. Cut to the 3D tunnel every ~2.5 s. Line reel unspooling. | 2–3 facts that set up the danger (depth, restriction, gas plan). One tension pause of 0.5 s or less. |
| 30–42 s | **The failure** | The key physical moment: silt-out, tangle, squeeze, light fail. Counter appears (air / time). | The core turn. SFX swell, then near-silence. |
| 42–52 s | **Consequence / race** | Counter ticking. Cross-section shows the distance to the exit. | What they did, what happened (factual and labelled: "reported"). |
| 52–60 s | **Payoff** | Aftermath: recovery line, plaque/sign, sealed entrance, rescued diver surfacing. | One-sentence outcome plus one-line "why it matters" (rule changed, record, legacy). |
| 60–63 s | **Loop / hard cut** | If ethical, the final frame matches the frame-1 composition (entrance or light). | Loop line flowing into line 1, or a hard cut. No subscribe outro. |

Rules: a visual change every 1.5–3 s; a pattern interrupt (3D ↔ cross-section ↔ document/map card) every 8–12 s; at most 2 silence beats; ~140–150 words at 150–165 WPM; cyan caption accent (studio standard); no real footage, photos or faces of real people; labels "reported/disputed" spoken where facts are contested.

## 6. Sources (search snippets used)
- vidIQ: FatalBreakdown (vidiq.com/youtube-stats/channel/@fatal_breakdown/), Scary Interesting (vidiq.com/youtube-stats/channel/@scaryinteresting/), DIVE TALK (vidiq.com/youtube-stats/channel/@divetalk/), Fascinating Horror, Plainly Difficult.
- Rosetta: rosetta.to/u/mrballen/this-hole-has-killed-16-people
- Know Your Meme: knowyourmeme.com/memes/nutty-putty-cave-incident
- Zack D. Films fan wiki: zackdfilms.fandom.com/wiki/Tham_Luang_Cave_Rescue_%F0%9F%98%A8(explained)
- Playboard search listings (caver; DIVE TALK channel), Social Blade (DIVE TALK, Scary Interesting, Plainly Difficult)
- Mel Magazine: melmagazine.com/en-us/story/cave-diving-youtube (Dive Talk profile)
- LADbible (Nutty Putty and Bushman's Hole coverage), National Geographic (Eagle's Nest deaths), AOL (Eagle's Nest), Divernet (Shaw CO2 blackout; *Dave Not Coming Back*), divers24.com (Plura misinformation contest)
