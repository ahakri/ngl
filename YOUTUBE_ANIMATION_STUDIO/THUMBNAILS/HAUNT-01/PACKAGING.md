# HAUNT-01 — Packaging: The Voice on the Enfield Tapes

Series: **Recorded Claim**. Rules: SHORTS_STRATEGY §10 (titles 30–60 characters, noun first, framing word for claims, 0–2 hashtags). The title complements the spoken hook ("In 1977, investigators left a tape recorder running in this bedroom") rather than repeating it.

## Titles (A = recommended)

| # | Title | Chars | Why |
|---|---|---|---|
| A | The Enfield Tapes: The Voice Said It Died Here | 46 | Searchable case name first. "Said" is the honest framing word, and the claim is the curiosity gap. |
| B | Enfield Poltergeist: She Admitted 2% Was Faked | 46 | Sceptic-framing hook (a 2026 trend per the research). The documented admission is the gap: which 2%? |
| C | The Real Conjuring 2 Case, as the Tapes Recorded It | 51 | Pop-culture anchor for search. Promises the documented version. |

Avoid: "TRUE", "REAL GHOST CAUGHT ON TAPE", or any title implying that we play the recording.

## Thumbnail / cover-frame concepts (custom Shorts thumbnail for search, channel grid and related links)

**Concept 1: "THE TAPES" (recommended)**
- Composition: 9:16. The bedroom at night, shot low from the floor. The reel-to-reel recorder (box + two reels) sits in the lower third, sharp, with its red REC lamp glowing. Behind it, out of focus, the wooden chair stands askew, away from the wall.
- Focal subject: the red REC lamp and the reels.
- Colour contrast: near-black blue room; a single saturated red point; pale-green caption accent.
- Text: **THE TAPES** (2 words), upper third, white with a dark stroke.
- The one visual idea: a machine is listening in an empty child's room.
- Curiosity gap: what did it record? The chair hints that something moved.

**Concept 2: "2%"**
- Composition: split vertical. The top 60% is the empty bedroom with a rumpled bed, one lamp and the chair out of place. The bottom 40% is a pale-green waveform crossing the frame.
- Focal subject: a huge "2%" stamped over the waveform like a case-file stamp.
- Colour contrast: cold blue scene, warm lamp, pale-green waveform, white "2%" with a red stamp border.
- Text: **2% FAKED?** (2 words).
- The one visual idea: she admitted a little was faked, so what about the rest?
- Curiosity gap: names the sceptic fact while leaving the other 98% open. It builds trust and still pulls the viewer in.

(Do not use the real Graham Morris photos, the real recording, or any face.)

## Shorts description (≤ 3 lines visible)

> In 1977, investigators recorded more than 180 hours of tape in a house in Enfield, London: the case behind The Conjuring 2. Every claim in this Short is labelled DOCUMENTED, EYEWITNESS CLAIM, FOLKLORE or DRAMATISATION. The real recording is described, not played.
>
> Sources: Society for Psychical Research (Psi Encyclopedia), Playfair, *This House Is Haunted* (1980), and Janet Hodgson's later interviews (1980, 2016). Full list pinned in comments.
>
> #poltergeist #enfield

Pinned comment: the source list from QUALITY_CONTROL/HAUNT-01/FACTCHECK.md (E1, E2, E5, E6, E16), plus the question "Which 2% do you think it was?" (a comment driver tied to the content).

## Related-video link target
- Until the series exists: HAUNT-02 (The Real Room 217), the other launch Short in the "Recorded Claim" series.
- Later: the best-performing Recorded Claim Short, or an Enfield long-form if this Short reaches ≥2× the channel median for engaged views.

## Playlist
"Recorded Claim: haunted cases, labelled".

## Final thumbnails

Hero stills are purpose-built compositions in `BLENDER_PROJECTS/HAUNT-01/thumbs_shots.py` (`THUMB_A`, `THUMB_B`; the video source `shots.py` is untouched). They were rendered at 1080x1920 with EEVEE at 16 samples to `hero_THUMB_A/0020.png` and `hero_THUMB_B/0020.png`, then composed by `PIPELINE/thumbnail.py` from `thumbs.json`. Both scenes are stylised 3D recreations: no real photos, no real recording and no faces.

| Thumbnail | Files | Text | Pairs with title |
|---|---|---|---|
| **A: "THE TAPES"** | `thumb_A.png` (9:16), `thumb_A_16x9.png` | THE TAPES (2 words, white, red glow) | **A**: "The Enfield Tapes: The Voice Said It Died Here" (also works with C) |
| **B: "2% FAKED?"** | `thumb_B.png` (9:16), `thumb_B_16x9.png` | 2% FAKED? (2 words, yellow) | **B**: "Enfield Poltergeist: She Admitted 2% Was Faked" |

**A: the chair and the listening machine.** A low, tight shot inside the dark child's bedroom. The wooden chair stands askew, away from the wall, in the centre. Right behind it, the reel-to-reel recorder's red REC lamp is the only warm light, and it washes the chair back red against the cold blue window.
- The one idea: a machine is recording an empty room, and the chair is not where a chair should be.
- Curiosity gap: *what did the tape pick up?* The title supplies the claim ("the voice said…") with the honest word "said". The image only shows a recorder and a chair, so nothing is presented as proven, and the video pays it off (the tapes are described and the claim is labelled).
- Contrast: one saturated red point on a near-black blue room, with white type at the top, above the subject.

**B: the shadow and its source.** A knocked-over lamp throws a head-and-shoulders shadow onto the yellow wallpaper. The cause is deliberately left in frame: a chair with a jumper hung on its back (the same dramatisation as S09).
- The one idea: something that *looks like* a figure turns out, when you look again, to be a chair.
- Curiosity gap: "2% FAKED?" plus the title's documented admission raises the question: which 2%, and what about the rest? The image mirrors the sceptic framing, because the "ghost" has a visible ordinary cause. This builds trust instead of implying proof.
- Contrast: a warm yellow pool of light, a hard black silhouette, a cold blue window, and yellow type on black.

**Recommended pick: A**, with title A, at upload. It names the searchable artefact ("tapes" plus "Enfield" in the title), and it reads instantly at channel-grid size because of the single red light. It also matches the Short's own cold open (S01 and S14), so a viewer arriving from search gets what the cover promised. **B** is the alternate. Shorts have no Test & Compare, so use B (with title B) as the packaging of a *different* Recorded Claim Short with a sceptic angle, or as the cover if a long-form Enfield cut is made, where Test & Compare can test A against B. Do not re-upload this Short to test it.

Composer changes made for this pass (backwards compatible): the vignette mask was inverted and blacked out the centre of every thumbnail, and it is now a proper radial edge-darken. New optional keys: `exposure`, `vignette`, `text_glow`, `zoom_16x9` and `focus_16x9`.
