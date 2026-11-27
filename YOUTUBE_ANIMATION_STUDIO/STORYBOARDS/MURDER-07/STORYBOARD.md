# MURDER-07 — Storyboard (The Oldest Cold Case: Shot in the Back 5,300 Years Ago)

Vertical 9:16, 1080x1920, 24 fps. 17 shots, est. 68.3 s. Mood `murder`. Captions: burned-in, word-synced, centred at y≈1240 (keep all text overlays out of y 1150–1400), accent words = `emphasis`. Overlays avoid the bottom 20% and right 15% (Shorts UI). Shot times are estimates; the pipeline derives real durations from TTS.

**Build notes.** Sets: (1) glacier saddle = `mountains()` + `heightfield()` with `mat_snow`, `dawn_sky()`, `snowfall()`; (2) ice slab macro (blue transmissive material, meltwater `glass_drops()`), with a low-poly brown mannequin form under it — never readable beyond a shoulder line, no face, no hands; (3) lab desk / radiology lightbox / CT room: `desk()`, `hanging_lamp()`, `monitor()`, new lightbox prop (box + emissive panel); (4) evidence board: `evidence_board()`, `paper_card()`, `red_string()`; (5) artefact turntable on black.
**X-ray line art (new):** stylised blue-white curves for ribs, scapula and clavicle drawn with `curve_draw()`, arrowhead as a small emissive triangle. Not traced from the real radiographs. Artery = one thin red line. No wound imagery.
Metres for altitude (European site).

## S01 · 0.0–2.9 s (2.9 s) · mountain_snow

- **Visual:** COLD OPEN, moving at frame 1. Macro over a sheet of glacier ice in flat dawn light: meltwater beads run down; under the cloudy blue ice a dark brown shape is just readable (a shoulder line, nothing more). A thin red evidence-tag string lies across the ice.
- **Camera:** 85 mm slow lateral glide + push across the ice surface
- **Characters:** Ötzi (stylised: faceless dark-brown mannequin form, partly under translucent ice; never shown in detail)
- **Environment:** mountain_snow
- **Build (lib_murder):** Ice sheet = thick slab with `mat_snow` variant (blue SSS/transmission, noise bump); body = low-poly mannequin shape, brown matte, under the slab; `glass_drops()` meltwater; `red_string()` across.
- **Lighting:** cold dawn, blue ice subsurface glow, low warm rim from the horizon
- **FX:** meltwater drips, snow drift
- **On-screen text / overlays:** [counter] YEARS COLD (y=330)
- **SFX:** wind@0.0s(g0.4), sting@0.9s(g0.45)
- **Music:** Low drone + pulse (0.5).
- **Transition in:** cut
- **Narration (L01):** "This cold case is 5,300 years old."

## S02 · 2.9–8.1 s (5.2 s) · mountain_snow

- **Visual:** Wide glacier saddle under a clear sky. Two small faceless hikers in 1991-style jackets crest the snow and stop, one pointing down at a dark gully of meltwater and rock.
- **Camera:** wide 28 mm, slow push past a boulder
- **Characters:** hiker_A (red jacket, faceless), hiker_B (blue jacket, faceless)
- **Environment:** mountain_snow
- **Build (lib_murder):** `mountains()` + `heightfield()` saddle with `mat_snow`; two `hiker()` with walk keys; rocky gully = scattered `rounded_box` rocks + dark wet patch.
- **Lighting:** bright high-altitude sun, deep blue shadows
- **FX:** snow drift, sun glare
- **On-screen text / overlays:** [stamp] 19 SEPTEMBER 1991 (y=300); [label] DOCUMENTED FACT (y=420)
- **SFX:** footsteps@0.0s(g0.35), wind@0.0s(g0.35)
- **Music:** Pulse holds.
- **Transition in:** cut
- **Narration (L02):** "September 1991. Two German hikers spot a body melting out of a glacier."

## S03 · 8.1–12.9 s (4.8 s) · map

- **Visual:** Map card: northern Italy / western Austria outline, a dashed border line, pin dropping on the Tisenjoch / Ötztal Alps just on the Italian side. Behind the card, the mountain range rendered in dusk tones.
- **Camera:** 2.5D map zoom with slight parallax
- **Characters:** —
- **Environment:** map
- **Build (lib_murder):** Map overlay over `mountains()` plate at dusk (`dawn_sky()` tones); border = dashed line in the card (route points double as the border trace).
- **Lighting:** graphic over mountain plate
- **FX:** —
- **On-screen text / overlays:** [map] ÖTZTAL ALPS; [stamp] ITALY / AUSTRIA BORDER / 3,210 M (y=300)
- **SFX:** whoosh@0.0s(g0.35), click@1.6s(g0.35)
- **Music:** Pulse.
- **Transition in:** whip
- **Narration (L03):** "High in the Ötztal Alps, on the border of Italy and Austria."

## S04 · 12.9–17.4 s (4.5 s) · mountain_snow

- **Visual:** Recovery scene (no body detail): faceless figures in rescue jackets kneel around the gully with ice axes; a small helicopter shape waits on the snow in the background; a body-bag-shaped dark bundle is kept out of focus and mostly hidden behind kneeling figures.
- **Camera:** 50 mm over-shoulder, rack focus from an ice axe in the foreground to the group
- **Characters:** recovery team x3 (faceless)
- **Environment:** mountain_snow
- **Build (lib_murder):** Same saddle set; `hiker()` x3 in kneel pose; simple helicopter = rounded boxes + rotor planes; `snowfall()`.
- **Lighting:** overcast afternoon, flat
- **FX:** snowfall (light)
- **On-screen text / overlays:** [card] Recent climber death? (y=820)
- **SFX:** wind@0.0s(g0.35), click@1.2s(g0.3)
- **Music:** Drone; slight tension.
- **Transition in:** cut
- **Narration (L04):** "At first, everyone assumed it was a climber who'd died recently."

## S05 · 17.4–21.1 s (3.7 s) · other:lab_desk

- **Visual:** Lab desk under a hanging lamp: a tiny sealed sample vial; a monitor shows a date readout spinning backwards from 1991 through AD 0 to 3300 BC.
- **Camera:** 35 mm push from the vial to the monitor
- **Characters:** —
- **Environment:** other:lab_desk
- **Build (lib_murder):** `desk()` + `hanging_lamp()` + `test_tube()` + `monitor()` with `mat_screen` emissive counter texture.
- **Lighting:** practical warm lamp + cool monitor glow
- **FX:** dust motes
- **On-screen text / overlays:** [counter] YEARS BEFORE 1991 (y=330); [text] c. 3300 BC (y=760)
- **SFX:** typewriter@0.0s(g0.25), hit@1.8s(g0.45)
- **Music:** Hit on '3300 BC'.
- **Transition in:** cut
- **Narration (L05):** "Then radiocarbon dating put his life around 3300 BC."

## S06 · 21.1–25.2 s (4.1 s) · mountain_snow

- **Visual:** Back on the glacier at golden hour, pull-out from the ice sheet (S01) to reveal the whole remote pass, tiny in the landscape. Name card.
- **Camera:** crane up and back, 24 mm
- **Characters:** Ötzi (stylised: faceless dark-brown mannequin form, partly under translucent ice; never shown in detail) (tiny, under ice, unreadable)
- **Environment:** mountain_snow
- **Build (lib_murder):** S01 ice slab placed in the S02 saddle; camera crane keys.
- **Lighting:** golden hour, long shadows
- **FX:** snow drift
- **On-screen text / overlays:** [title] ÖTZI (y=520); [label] DOCUMENTED FACT (y=200)
- **SFX:** riser@0.0s(g0.35)
- **Music:** Swell (0.65).
- **Transition in:** cut
- **Narration (L06):** "Europe's oldest known natural human mummy. They named him Ötzi."

## S07 · 25.2–30.0 s (4.8 s) · other:artifact_turntable

- **Visual:** Museum-style turntable: a copper-bladed axe on a wooden haft, a small flint dagger with wooden handle, and a long plain yew bow stave (unfinished: no nocks), each lit and rotating in turn; a deerskin quiver beside them.
- **Camera:** 50 mm, three quick slides (1.3 s each) between artefacts
- **Characters:** —
- **Environment:** other:artifact_turntable
- **Build (lib_murder):** Simple props: axe = cylinder haft + copper wedge (metallic orange); dagger = flint wedge (chipped noise) + wood handle; bow = long tapered cylinder (1.82 m, yew orange-brown); quiver = rounded tube, brown leather; `slam_in()` / spin keys.
- **Lighting:** black background, warm key, rim light
- **FX:** —
- **On-screen text / overlays:** [card] copper axe / flint dagger / unfinished yew bow (y=820)
- **SFX:** click@0.0s(g0.3), click@1.3s(g0.3), click@2.6s(g0.3)
- **Music:** Pulse (0.6).
- **Transition in:** cut
- **Narration (L07):** "He carried a copper axe, a flint dagger and an unfinished bow."

## S08 · 30.0–33.9 s (3.8 s) · other:evidence_board

- **Visual:** Evidence board in a dim office: a card 'CAUSE OF DEATH' with a big red question mark; a timeline strip 1991 → 2001 with the years between empty.
- **Camera:** 35 mm slow push, slight handheld
- **Characters:** —
- **Environment:** other:evidence_board
- **Build (lib_murder):** `evidence_board()` + `paper_card()` with '?'; `desk_lamp()`.
- **Lighting:** desk lamp warm, room dark
- **FX:** dust motes
- **On-screen text / overlays:** [timeline] CAUSE OF DEATH? (y=900)
- **SFX:** heartbeat@0.6s(g0.3)
- **Music:** Thins (0.45).
- **Transition in:** cut
- **Narration (L08):** "But for ten years, nobody knew how he died."

## S09 · 33.9–38.7 s (4.8 s) · other:xray_lightbox_room

- **Visual:** MID-POINT TURN. A dark radiology room: a film is clipped onto a lightbox, which flickers on. The film shows a clean, stylised line-art chest and shoulder (ribs, shoulder blade) in blue-white; the camera drifts toward the upper left shoulder area.
- **Camera:** 50 mm slow push toward the left shoulder region of the film
- **Characters:** —
- **Environment:** other:xray_lightbox_room
- **Build (lib_murder):** Lightbox = box with emissive front panel (`mat_screen`); film = `image_plane()`-style plane with procedural line-art (curves for ribs/scapula via `curve_draw()`), no real radiograph traced.
- **Lighting:** lightbox glow only
- **FX:** flicker on
- **On-screen text / overlays:** [stamp] BOLZANO, 2001 (y=300)
- **SFX:** click@0.0s(g0.4), static@0.1s(g0.2)
- **Music:** Music drops to near silence.
- **Transition in:** cut
- **Narration (L09):** "In 2001, a new X-ray caught something in his left shoulder."

## S10 · 38.7–42.3 s (3.7 s) · other:xray_lightbox_room

- **Visual:** Extreme close-up on the film: a small, sharp triangular shape glows brighter than everything else in the shoulder area and a red circle draws around it (L10). The line-art then morphs in-shot into a clean diagram: a faceless outline figure seen from behind, a dotted line arcing in from behind and below to the left shoulder, an impact dot. No blood, no wound (L11).
- **Camera:** macro snap-zoom (0.3 s), hold; then pull back as the art morphs to the diagram
- **Characters:** outline figure (generic, faceless)
- **Environment:** other:xray_lightbox_room
- **Build (lib_murder):** Emissive triangle in the line-art plane; red circle = `curve_draw()` ring; morph = cross-fade of curve sets into the outline figure (`hiker()` silhouette with emissive edge) + `arrow()` dotted path.
- **Lighting:** lightbox glow; arrowhead emissive; then flat graphic
- **FX:** glow pulse
- **On-screen text / overlays:** [text] ARROWHEAD (y=400); [label] DOCUMENTED FACT (y=200)
- **SFX:** hit@0.0s(g0.55), whoosh@1.8s(g0.4)
- **Music:** Single low hit, then pulse returns low (0.5).
- **Transition in:** flash
- **Narration (L10, L11):** "A flint arrowhead." "He'd been shot from behind."

## S11 · 42.3–46.5 s (4.2 s) · document

- **Visual:** An older, yellowed film labelled 26 SEP 1991 slides onto the lightbox next to the 2001 one; the same small shape is faintly there. A red circle appears on the old film too.
- **Camera:** 35 mm lateral move between the two films
- **Characters:** —
- **Environment:** document
- **Build (lib_murder):** Second film plane, sepia tint; same line-art at lower contrast.
- **Lighting:** lightbox glow; older film warmer
- **FX:** —
- **On-screen text / overlays:** [card] Looking for fractures, / not arrows (reported) (y=820)
- **SFX:** click@0.0s(g0.3), sting@1.4s(g0.4)
- **Music:** Pulse (0.6).
- **Transition in:** cut
- **Narration (L12):** "Looking back, it was visible on an X-ray from 1991."

## S12 · 46.5–49.4 s (2.9 s) · other:ct_scan_room

- **Visual:** A CT scanner ring rotates around a covered, faceless form (sheet over it, no features); slices flicker on a side monitor.
- **Camera:** 28 mm arc around the scanner
- **Characters:** covered form (no features)
- **Environment:** other:ct_scan_room
- **Build (lib_murder):** Scanner = torus + box bed; covered form = cloth-like rounded box; `monitor()` with `scanlines()`.
- **Lighting:** cool clinical light; monitor glow
- **FX:** scanlines
- **On-screen text / overlays:** [stamp] 2007: CT SCANS (y=300)
- **SFX:** rumble@0.0s(g0.3)
- **Music:** Build (0.65).
- **Transition in:** cut
- **Narration (L13):** "In 2007, new CT scans looked closer."

## S13 · 49.4–53.4 s (4.1 s) · other:ct_scan_room

- **Visual:** Monitor fills the frame: a clean 3D-style diagram of collarbone and shoulder in blue-white; a thin red line (the artery) runs beneath the collarbone; the arrowhead sits against it and the red line breaks.
- **Camera:** push into the monitor, 50 mm, then slow orbit of the diagram
- **Characters:** —
- **Environment:** other:ct_scan_room
- **Build (lib_murder):** `monitor()` with emissive diagram built from `curve_draw()` curves; red artery curve with a gap keyed open.
- **Lighting:** monitor glow
- **FX:** scanlines
- **On-screen text / overlays:** [text] ARTERY (y=780)
- **SFX:** click@0.2s(g0.3), sting@1.6s(g0.35)
- **Music:** Build (0.7).
- **Transition in:** cut
- **Narration (L14):** "The arrow had torn a major artery under his collarbone."

## S14 · 53.4–56.9 s (3.5 s) · mountain_snow

- **Visual:** Dramatised, restrained: the glacier pass at dusk 5,300 years ago, no ice yet: a lone faceless figure sits down against a rock, seen from far behind; snow begins to fall. The figure is a small silhouette; nothing else is shown.
- **Camera:** very wide 35 mm, locked, slow push
- **Characters:** Ötzi (faceless silhouette, from far behind)
- **Environment:** mountain_snow
- **Build (lib_murder):** `mountains()` + saddle `heightfield()` without ice slab; `hiker()` in `seated_pose()`; `snowfall()`.
- **Lighting:** dusk blue, faint warm horizon
- **FX:** snowfall (light), wind
- **On-screen text / overlays:** [label] DRAMATISATION (y=200)
- **SFX:** wind@0.0s(g0.4)
- **Music:** Silence beat, then low pad (0.3).
- **Transition in:** fade_black
- **Narration (L15):** "Researchers concluded he most likely bled to death."

## S15 · 56.9–60.6 s (3.7 s) · other:artifact_turntable

- **Visual:** Still life on dark stone: einkorn grain ears, a strip of dried meat, a sprig of herbs, a small fire glow off-frame; an ibex silhouette is drawn on in white line-art above.
- **Camera:** 50 mm slow slide
- **Characters:** —
- **Environment:** other:artifact_turntable
- **Build (lib_murder):** Props: grain = small instanced ellipsoids on stalks; meat strip = flattened rounded box; ibex = `glow_poly()` line-art; point light flicker for fire.
- **Lighting:** warm firelight from the side
- **FX:** embers (few)
- **On-screen text / overlays:** [card] ibex, red deer, einkorn wheat (y=820)
- **SFX:** click@0.2s(g0.25)
- **Music:** Pad (0.4).
- **Transition in:** cut
- **Narration (L16):** "Shortly before, he'd eaten a hearty meal, including ibex."

## S16 · 60.6–64.2 s (3.6 s) · other:evidence_board

- **Visual:** Evidence board again: the 'CAUSE OF DEATH' card is now answered ('ARROW'), but a new card 'SHOOTER: UNKNOWN' is pinned beside it; a red string leads from the arrowhead card to an empty space.
- **Camera:** 35 mm push to the empty space at the end of the string
- **Characters:** —
- **Environment:** other:evidence_board
- **Build (lib_murder):** `evidence_board()` + `paper_card()`s + `red_string()`.
- **Lighting:** desk lamp warm, deep shadow
- **FX:** dust motes
- **On-screen text / overlays:** [document] CAUSE: ~~UNKNOWN~~ ARROW / SHOOTER: UNKNOWN / MOTIVE: UNKNOWN (y=420)
- **SFX:** heartbeat@0.4s(g0.3)
- **Music:** Pad; drops out at the end (0.5 s silence).
- **Transition in:** cut
- **Narration (L17):** "Who shot him, and why, is still unknown."

## S17 · 64.2–68.3 s (4.1 s) · other:museum_cold_cell

- **Visual:** LOOP: a small cold cell behind a thick viewing window, frost on the glass, blue light; inside only a vague dark form on a steel tray (unreadable). The camera pushes toward the frost until it fills the frame, matching the S01 ice texture so the replay cuts cleanly. Memorial card in small text.
- **Camera:** 50 mm push to the frosted glass, ending on the S01 ice macro framing
- **Characters:** Ötzi (stylised: faceless dark-brown mannequin form, partly under translucent ice; never shown in detail) (unreadable through frost)
- **Environment:** other:museum_cold_cell
- **Build (lib_murder):** Room box with window frame (rounded box + glass `mat_glass`-type) and frost texture (noise alpha); final frame = S01 ice surface macro.
- **Lighting:** cold blue cell light
- **FX:** frost, cold haze
- **On-screen text / overlays:** [stamp] SOUTH TYROL MUSEUM / OF ARCHAEOLOGY, BOLZANO (y=300); [text] ÖTZI  c. 3300 BC (y=980)
- **SFX:** wind@0.0s(g0.3)
- **Music:** Drone back to 0.5 (matches S01 for the loop).
- **Transition in:** cut
- **Narration (L18):** "Today, he's kept on ice in a museum in Bolzano."

## Timing checks

- Line 1 starts at 0.0 s; "5,300 years" lands by ~1.8 s, with the counter racing to 5,300 from frame 1. Frame 1 moves (glide over ice, meltwater).
- New information every ~3–5 s: 1991 hikers (≈3 s) → border (≈7 s) → modern-death assumption (≈12 s) → 3300 BC (≈16 s) → oldest mummy/name (≈20 s) → kit (≈24 s) → ten years unknown (≈29 s) → **turn (≈34 s): 2001 X-ray** → arrowhead (≈39 s) → shot from behind (≈41 s) → visible since 1991 (≈43 s) → 2007 CT (≈47 s) → artery (≈50 s) → bled to death (≈54 s) → last meal (≈57 s) → open question (≈61 s) → loop (≈65 s).
- Theory ladder of the template is compressed into the evidence board (S08 → S16): one documented answer (arrow), one open question (shooter).
- Silence beats: after L09 (0.6 s, before the arrowhead) and after L17 (0.5 s).
- Loop: L18 "…kept on ice in a museum in Bolzano." → L01 "This cold case is 5,300 years old." S17 ends on the S01 ice macro.
- Overlay safety: cards at y=820 (ends ≤1116), timeline y=900, document scrap at y=420, memorial text at y=980 (60 px), all clear of the caption band (1150–1400).
