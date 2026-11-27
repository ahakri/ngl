# SCUBA DIVING — Niche Research Report (Agent 3)

Date: 2026-11-27. Deliverable for the RESEARCH → ANALYZE stages. Companion data: `reference_videos.csv` (24 rows).

## 0. Method & data honesty

- youtube.com, Social Blade, Invidious/Piped and noembed were **not reachable** from this container (proxy 403 / DNS fail). General WebFetch also failed. All figures come from **web-search snippets** of third-party indexes (rosetta.to, vidIQ, socialcounts.org, thetvdb.com, si.edu) and press articles (dailyO, PetaPixel, Green Matters, LADbible, UNILAD Tech, NPR, Oceana).
- Every view count is a **snapshot of unknown date** unless a date is given. Anything not seen in a snippet is written `unverified`. No URL was invented: the 5 YouTube URLs in the CSV use video IDs that appeared in an indexed page's URL or embed (the source is named in `evidence_source`). All other rows have `url = unverified`.
- The shared search budget (200 calls per turn, across all agents) ran out partway through this task. Several concept facts are from standard references and are flagged **NEEDS FACT-CHECK** in `CONCEPTS.md`.

## 1. Who actually makes this content (verified vs. assumed)

| Creator (as briefed) | Status | What we found |
|---|---|---|
| MetaBallStudios | **Verified** | Spanish animator Álvaro Gracia Montoya. *Ocean DEPTH Comparison* (ID Q5C7sqVe2Vg) was covered by Nerdist, FlowingData, BGR and Mental Floss in 2021, UNILAD Tech in 2024 and LADbible in 2025. It is evergreen and long-form, but no view count could be found. |
| Zack D. Films | **Verified (most relevant Shorts reference)** | 29.3M subs and ~81B views (vidIQ, 2026-10-21). It led Tubefilter's global Top 50 in Oct 2026. Its Mariana Trench depth simulation has **45M views / 2.1M likes** (Green Matters). It has also animated Michael Packard's whale engulfment (LADbible, Dec 2024) and a "body effects as you dive deeper" Short (UNILAD Tech, Aug 2025). |
| MrBallen | **Verified** | Diving horror is a recurring sub-genre for him: *The Caribbean Disaster* ~6.0M, *This hole has killed 16 people* 5.6M, *Top 4 claustrophobic diving stories* 2.6M (rosetta.to). He also runs a podcast series, *The Final Descent* Vol. I–IV. |
| Thoughty2 | **Verified** | Chris Lemons video 1.2M (2023-11-14). Alvarenga sea-survival video 1.2M. |
| Weird History | **Verified** | *True Story Behind 'Open Water'* (Lonergans), 2020-11-06. Snapshots show 418K and 1.8M. |
| AiTelly | **Verified (format outlier)** | Titan implosion animation: 6.5M views in ~12 days and 10M+ later, from a ~267K-sub channel. It was **made in Blender by two people in ~12 h**. |
| Ocean Ramsey | **Verified** | Real freediver and shark conservationist (@oceanramseysharks: 334K subs, 161M views, vidIQ Nov 2026). She films real footage and does not animate. Her 2019 "Deep Blue" swim went viral; the shark's identity is disputed. |
| Fascinating Horror | **Verified** | *The Byford Dolphin Accident* (2024). Calm narration over reconstructions. |
| "Real Science" | **Not verified** | No diving-story video was found. Treat as unconfirmed. |
| "Bedtime Stories" | **Not verified for diving** | Horror channel (~1.04M subs per vidIQ, July 2025). No diving episode was found. |
| "Oddities" | **Not verified** | Nothing found. Do not cite. |
| IMR Scary Tales | Partially verified | *3 True Scuba Diving Horror Stories Animated* exists (recapio summary). Views unknown. It is a direct animated competitor. |

## 2. Outliers (view velocity vs. channel size)

1. **AiTelly, Titan implosion**: ~37× channel size. Three things drove it: a news peg, a technical "how exactly did it happen" promise, and clean 3D. It is the closest analogue to our Blender pipeline.
2. **Zack D. Films, Mariana Trench**: 45M on a 29M channel, about 1.5×. That is strong even for the biggest Shorts channel. Depth-descent ladders are a proven Shorts mechanic.
3. **MetaBallStudios, Ocean Depth Comparison**: kept getting re-covered by the press for 4+ years. Scale and depth comparisons are evergreen.
4. **MrBallen, Caribbean Disaster**: 6M, the top diving story found. It is a "trapped underwater by physics" story with a known-outcome tension.
5. **Underperformer contrast**: Smithsonian Channel's *Make It Out Alive: USS Indianapolis* full episode had **4,456 views** (si.edu). It had a strong subject but a generic title, long-form packaging and no hook. Packaging decides results, not the topic alone.

## 3. What the hits have in common

### Storytelling structure
- **Situation → violation → clock → resolution or unknown.** The best stories have a *countdown*: air left, hours in a pocket, a boat sailing away, minutes without gas.
- **A single impossible fact anchors the whole video**: "60 hours at the bottom of the sea", "30 minutes with no gas", "the boat left without them", "inside a whale's mouth".
- **Physical stakes the viewer can feel**: depth and pressure, darkness, cold, a narrowing air pocket. Depth-ladder videos turn the abstract number into felt danger by naming a body effect at each step.

### First 2 / 5 / 15 seconds (Shorts)
- **0–2 s**: the frame already shows the danger, with no logo or intro: a diver in black water, a capsized hull, an empty sea with two heads. The opening line is the impossible fact or a direct question: "This man spent 60 hours at the bottom of the Atlantic, and lived."
- **2–5 s**: one concrete detail that makes it real, such as a name, a year, a depth or "he was the ship's cook". A depth or time counter appears on screen.
- **5–15 s**: the clock is set ("his air pocket was shrinking"), and an open loop promises the twist ("and the divers who found him weren't looking for survivors").

### Reveal cadence
- Something new arrives every **3–5 s**: a counter tick, a camera move, a new fact. Depth-ladder formats reveal every 2–4 s.
- Hold the "how did he survive" mechanism until **~60–70 %** of runtime. Deliver the emotional payoff at **~85 %**.

### Narration and visuals
- Narration states the fact; the visual shows the **consequence**. For example, "4 feet of air" pairs with a slowly rising waterline. Captions are word-synced, with key numbers in a colour.
- Depth and time HUD overlays (metres, hours, bar of pressure) act as the second storyteller and as a retention device.
- Sound: low drone, muffled regulator breathing and bubble bursts. Hard cut to silence at the reveal.

### Cliffhangers and endings
- Mid-video turn: "But the divers weren't there to rescue anyone." (Okene) / "The headcount was wrong." (Lonergans)
- Endings that work: (a) a quiet survival fact, such as "He went back to diving three weeks later" (Lemons); (b) an unresolved mystery with the evidence stated, such as "Their bodies were never found" (Lonergans); (c) a loop line that recuts into frame 1.
- Endings that fail: moralising, a long call to action, or speculative gore.

### Thumbnails (long-form; Shorts use a strong first frame)
- One tiny figure in a huge dark volume. Scale contrast is the theme of the niche.
- A single bright light source, such as a torch beam or a lit hatch, against deep blue or black.
- One number or a 2–3 word label ("60 HOURS", "NO AIR", "LEFT BEHIND"). A red or yellow accent on teal or black.
- Shorts: the first frame does the thumbnail's job because the Shorts feed autoplays it.

### Titles and curiosity gaps
- Patterns seen: "The Incredible Survival Story Scientists Can't Explain", "This hole has killed 16 people", "True Story Behind 'Open Water'", "What happened to the DIVER at…".
- Formula: **[impossible fact] + [withheld mechanism]**. Examples: "He survived 60 hours underwater. Here's how." / "The boat counted wrong."

### Emotional triggers
Claustrophobia and thalassophobia, abandonment, awe at scale, survival against the odds, unexplained mysteries, respect for the dead.

### Hits vs. average
| Hits | Average |
|---|---|
| One impossible fact in line 1 | Background or context first |
| A visible clock (air, hours, depth) | Chronological narration with no stakes |
| Physical mechanism explained (air pocket, decompression, gas) | A "miracle" left unexplained |
| A named real person with a precise date and place | Generic "a diver once…" |
| Specific, curiosity-gap title | Descriptive, brand-style title (Smithsonian: 4.4K) |
| Visuals show scale and darkness | Talking head or stock B-roll |

## 4. Implications for our pipeline
- Our toolchain (Blender procedural wrecks and reefs, volumetric fog, caustics, particles, low-poly divers) matches the winning look: dark volume, one light, small figure, HUD counters. AiTelly shows that Blender-only explainers can break out.
- Never reuse real rescue or death footage (Okene, Lipski). Animate only, with stylised divers.
- Stories with a **mechanism** (air pocket, decompression, gas reserve, whale anatomy) suit our animation best, because we can *show* physics that real footage can't.

## 5. Ethics notes specific to this niche
- Real deaths (Lonergans, Blue Hole victims, USS Indianapolis crew): no depictions of death or of bodies. Use "never found" and "lost" language, and state uncertainty.
- Yuri Lipski (Dahab 2000): his death was recorded on his own camera. **Do not describe or recreate the footage.** If the Blue Hole is covered, frame it as a site-safety story and do not centre one victim.
- Disputed topics (Yonaguni, Baltic Sea anomaly, the Deep Blue shark ID) must carry on-screen labels: DISPUTED / CLAIM / SCIENTIFIC CONSENSUS.

---

## FORMAT TEMPLATE — SCUBA SHORT (~60 s, 9:16, 30 fps)

| Time | Beat | Narration job | Visual job | Retention device |
|---|---|---|---|---|
| 0.0–2.0 s | **Cold-open impossible fact** | One sentence containing the number ("60 hours", "30 minutes", "left behind") | Danger already on screen: small diver or figure in dark volume, one light source | The fact itself; captions pop word by word |
| 2–6 s | **Anchor** | Who, when, where in ≤12 words | Map pin or date card slides in; depth/time HUD appears | HUD counter starts |
| 6–15 s | **Clock set and stakes** | What is running out (air, time, daylight, the boat) | Waterline, gauge or boat on the horizon moving | Open loop: "but…" |
| 15–25 s | **Escalation 1** | First complication, with a sensory detail (cold, dark, sound) | Camera push-in; silt or bubbles; lights flicker | New fact every 3–4 s |
| 25–35 s | **Escalation 2 / mid-turn** | Twist ("the divers weren't looking for survivors") | Cut to a second POV (rescuers, the boat, the surface) | Pattern break: perspective switch |
| 35–45 s | **Mechanism reveal** | How the physics works (air pocket, decompression, gas reserve) | Cutaway diagram or x-ray view, with a labelled callout | "Aha" payoff |
| 45–55 s | **Resolution or unknown** | The outcome, stated factually; uncertainty labelled | Light from the surface, or an empty sea | Emotional beat; music drops out |
| 55–60 s | **Loop line** | A final line that rhymes with line 1 ("…and that is why the first diver almost swam away") | Last frame matches the opening frame's composition | Seamless loop back to 0 s |

Production notes: target runtime 55–65 s. Use word-synced burned-in captions with depth and time numbers in accent yellow. Use the am_onyx or bm_george voice at ~165 wpm. Keep the end screen card under 1 s, or skip it.
