# Distilled: GitHub motion-graphics agent skills → our Pillow pipeline

Research date 2026-11-04. Every fact below comes from a file I downloaded and read (raw copies in
`/workspace/work/distill/raw/f/`). Code library: `/workspace/work/distill/easing.py` (55-check self-test passes).

Our pipeline (the baseline, and the rules that win any conflict): Python + Pillow drawing every frame (1.5× supersample,
LANCZOS down), numpy BGM + SF2 samples, ffmpeg mux; 9:16 1080×1920, no narration, Chinese captions, dark backgrounds,
abstract cartoon characters with exaggerated faces, flat fills + highlights/glow, **no dark outlines, no offset
drop-shadow text**, **only 2 big accents (0 s and BIG2)**, shake ~8 px big / 1.5 px small, zoom ~4 %, caption dwell
≥ max(1.5 s, chars/4 s), `cues.py` drives picture and music, chunked renders on 2 cores with a 120 s command limit.

---

## A. Per repo: concrete techniques (with sources)

### 1. remotion-dev/skills (`skills/remotion-best-practices`)
- **Always clamp interpolation.** `interpolate()` is not clamped by default and overshoots outside its range; set
  `extrapolateLeft/Right: "clamp"`. House entrance ease is `Easing.bezier(0.16, 1, 0.3, 1)`; "push with no bounce"
  is `Easing.spring({damping: 200})`. — https://raw.githubusercontent.com/remotion-dev/skills/main/skills/remotion-best-practices/remotion-markup/timing.md
- **Perceptual scale.** Linear scale looks like it slows as it grows; use `output: 'perceptual-scale'` (geometric
  interpolation) for every scale animation. Same file.
- **Posterize** (`posterize: 3` samples every 3rd frame) as a deliberate stylistic choice; multiple keyframes with
  n−1 easings per segment. Same file.
- **Transitions vs overlays.** A transition overlaps both scenes and *shortens* the timeline; an overlay (e.g. a
  seeded light leak, `seed` picks the pattern, reveal in first half/retract in second) sits on the cut *without*
  shortening it. — …/remotion-markup/transitions.md, …/remotion-markup/light-leaks.md
- **Motion blur = sub-frame averaging.** `HtmlInCanvasMotionBlur` captures fractional frames and averages pixels;
  `shutterAngle` default 180 (0–360), `samples` default 8 (1–64). — …/remotion-markup/motion-blur.md
- **Captions live with their clip.** Keep each clip's captions inside the same sequence as its picture so trimming /
  retiming moves both together (our `cues.py` already does this). — …/remotion-captions/display-captions.md

### 2. Mort1d/motion-graphics-skills (`skills/motion-graphics`)
- **Easing vocabulary:** entrances `outExpo`/`outCubic`; exits `inExpo` (accelerates away); wipes `inOutSine` ≥ 0.3 s
  (faster reads as a flash cut); linear only for continuous drift/parallax/rotation. **Springs give weight**: four
  feels — snap, base, heavy (big type, logo: no overshoot), play (mascots). "Type never bounces." A value that
  retargets is a **sum of springs** (`track()`) so it never jerks. — https://raw.githubusercontent.com/Mort1d/motion-graphics-skills/main/skills/motion-graphics/references/story-and-motion.md §4
- **Stagger** 1/8–1/4 beat apart in reading order; **cut on motion** (enter already moving, leave accelerating);
  **one read at a time** (never start the next read inside the current one's window); text holds ≥ 0.6 s per 3 words;
  "cut on downbeats, not on every beat"; **flashes/shakes are spice — biggest hits only**; camera slow push 2–6 %
  through holds. Same §4.
- **Depth/detail:** 3–4 layers each at its own speed; every drawn surface = base gradient + material texture (grain)
  + one edge (highlight); far layers get only grain at 40–60 %; hero text ≥ 1.8× next text and 2.5× smallest; one
  accent word per statement. Same file §6–§7.
- **Sound sync craft:** a hard cut may lead its beat by a frame or two (light before sound); place a sample by its
  loudest point ("a whoosh peaks 0.7 s in: started on its cue it lands late"); `gap()` silence ⅛–½ beat before the
  biggest hit; never two whooshes at once; repeated sounds vary (± a semitone, `rate 0.92–1.08`); end card ring-out
  ≥ 1.5 s; sidechain duck bed under kicks/hits; −14 LUFS, true peak ≤ −1 dBTP. — …/references/sound-design.md §8–§9
- **QA & determinism:** frame is a pure function of `t`; `verify` renders the same frames forward, backward and
  shuffled and fails anything not a function of t; QA flags `flash` (empty frames between scenes), `pop` (one frame
  unlike both neighbours), `edges` (text cut by frame), `hook` (still opening). — …/SKILL.md step 5 & 7
- **Critique loop:** score 1–10 on hook (2 s) · phone readability · motion · variety (new every 2–4 s) ·
  composition · accuracy · sound sync; write the three worst problems with time + evidence + fix; repeat until all
  ≥ 8. — …/SKILL.md step 7, …/assets/template/REVIEW.md

### 3. charlie947/motion-graphics-skills ("rules from rejected drafts")
- **Vox explainer review rules:** sound is not optional (low bed, a hit on each new shot, a lift on the last line);
  cards/objects moving in depth, not lone lines; symmetric grids; the opening line must promise what's coming and
  show the first surprise within 5 s; "if the first 3 seconds would not stop your own thumb, rebuild them"; say
  "looks like", never "is", when research only shows similarity; "one reason", not "the reason". —
  https://raw.githubusercontent.com/charlie947/motion-graphics-skills/main/skills/vox-explainer/SKILL.md
- **Texture recipe:** halftone + paper grain + fine film grain over the whole frame, colour fringing at frame edges
  only, soft vignette; optional "animate on twos" stepped motion. Same file (build brief).
- **Editor's check:** capture one frame from the middle of every shot; check cut-off text, overlapping cards,
  misspelt names, any fact not in the fact list. Same file step 4–5.
- **Reel export contract:** H.264 high, CRF 18, yuv420p, `color_range tv`, bt709 primaries/trc/colorspace, AAC,
  `-movflags +faststart`; a silent AAC track if no sound; ffprobe must show h264 / 1080×1920 / yuv420p / tv / bt709 +
  one aac; logos over footage go on their own dark rounded tile. —
  https://raw.githubusercontent.com/charlie947/motion-graphics-skills/main/skills/reel-export/SKILL.md
- **"Fix one thing at a time"** prompt: name one defect, keep motion/timing/loop exactly, report what changed. —
  https://raw.githubusercontent.com/charlie947/motion-graphics-skills/main/prompts/polish.md
- **Effects catalogue principle:** every hold keeps "something small living" so it never looks frozen; one object
  changes shape rather than fading into another; results stage in, never pop in together. —
  …/skills/motion-effects/references/effects.md

### 4. kevinbadi/claude-motion-skills = mirror of iart-ai/motion-skills (+ iart-ai/tiktok-video-skills, kinetic-typography-skills)
- **Deliver-and-verify toolkit:** `contact-sheet.sh` (ffmpeg `hstack` start|mid|end), `seek-shot.sh` (freeze at t),
  `probe-mp4.sh` (assert WxH, codec h264, fps ±0.5, duration). —
  https://raw.githubusercontent.com/kevinbadi/claude-motion-skills/master/tools/verify/README.md (+ the three .sh files)
- **Retention pacing:** hook text on screen by frame 1 (muted viewers), frame 0 is the best frame — never a fade-up
  from black; one open gap only; **uneven cuts** read as momentum; **punch-in** spring (damping 13, stiffness 220,
  scale 1→1.1) as the cheapest pattern interrupt; retention-curve debugging table (cliff 0–2 s = hook; flat-then-drop
  mid = cuts too sparse → 2–4 s); seamless loop by easing the last 0.5 s back to frame 0. —
  https://raw.githubusercontent.com/iart-ai/tiktok-video-skills/main/skills/short-form-video/references/retention-pacing.md
- **Safe zones** 1080×1920: universal centre 900×1400; TikTok top ~108, bottom ~320, right ~120 (TikTok Ads bottom
  ~370). Same file §5.
- **Captions:** 1–4 words per page; per-word spring pop (damping 12, mass 0.6, scale 0.6→1 with micro-overshoot);
  one active-word highlight colour, never animate every word's colour at once; 56–80 px, ~62–70 % down; "black
  stroke 2–6 px + soft shadow". —
  https://raw.githubusercontent.com/iart-ai/tiktok-video-skills/main/skills/caption-animation/SKILL.md
- **Kinetic type timing:** per-fragment 400–600 ms; stagger lines 60–100 ms, words 40–70 ms, chars 20–40 ms; cap the
  total reveal near ~800 ms; mask reveal (rise from translateY 110 % under a clip) is the robust workhorse; blur-in
  for premium. — https://raw.githubusercontent.com/iart-ai/kinetic-typography-skills/main/skills/kinetic-typography/SKILL.md

### 5. haidrrrry/claude-remotion-skill (`remotion-motion-graphics`)
- **10 non-negotiables:** never linear (always clamp); entrances animate 2–3 props (opacity + translateY + scale),
  never a lone fade; stagger 3–6 frames; **exits exist and are faster than entrances (~10 vs ~20 frames)**; 5-layer
  stack (bg mesh → assets → graphics/type → colour grade → grain + vignette); Ken Burns on stills; **idle elements
  breathe** (on screen > 2 s → sin micro-motion); timing derived from fps; one theme object; render → extract →
  look → fix. — https://raw.githubusercontent.com/haidrrrry/claude-remotion-skill/main/remotion-motion-graphics/SKILL.md
- **Spring presets** (theme.ts): snappy {damping 14, stiffness 160, mass 0.6}, smooth {20, 90, 1}, bouncy {11, 170,
  0.7}; eases out = bezier(0.16,1,0.3,1), inOut = (0.83,0,0.17,1), in (exits only) = (0.7,0,0.84,0). —
  …/remotion-motion-graphics/assets/theme.ts
- **Concrete numbers:** breathe `1 + sin(frame/22)·0.015`, float `sin(frame/30)·3 px`; grain opacity 0.05 with the
  noise tile offset every frame (`frame·7, frame·13`); vignette radial transparent 56 % → rgba(0,0,0,.22); grade
  overlay hero colour soft-light 0.18–0.25 on dark; exit = last 12→2 frames, ease-in, −42 px. —
  …/references/motion-patterns.md §6, 7, 11, 12
- **Design rules:** hero colour on at most one element per frame, glow on the hero only ("more than one glowing
  element = Vegas"); HIT → hold 15–20 frames → build → HIT; never > 90 frames without a new element; ≥ 3 moments of
  stillness (contrast reads expensive); SFX start 2–3 frames before the visual lands; music bed ~0.2–0.3 under SFX;
  preview suspicious motion at 0.25×. — …/references/design-rules.md
- **Failure mode:** emoji as icons break the palette (≈ our "Noto SC subset has no ⚡" lesson). SKILL.md.

### 6. jabezpauls/edu-video-generator (`skills/educational-video`)
- **One word-level cue grid** shared by picture and sound: named cues `s03.start`, `s03.w12`, `s03.<word>#2`,
  `s03.p2`; lead 0.4 s before first word, tail 0.6 s, min scene 1.5 s; **`HIT_LEAD = 0.06` s — visuals start this
  much before a cue so they read on it**; `cues` command derives the SFX plan from beats + scene changes. —
  https://raw.githubusercontent.com/jabezpauls/edu-video-generator/main/skills/educational-video/scripts/grid.py
- **Closed-form springs** with presets as (response s, damping ratio): snappy (0.22, 0.8) ~1.5 % overshoot, default
  (0.4, 0.86), heavy (0.5, 1.0) none, playful (0.5, 0.45) ~20 %; `settle()` gives run time; normalised so α=1 → 1.0
  exactly. — …/templates/manim/springs.py
- **Motion rules:** springs only, linear only for typing/scrolls/slow pushes; `playful` for characters only, never
  type; a pure opacity fade is never the enter/exit of a primary element; **swaps are sequential** (outgoing gone
  before incoming lands, ≤ 1 frame overlap at ≥ 95 % gone); content the story has moved past **recedes (dims)**
  instead of vanishing; masked words start ≥ 140 % of size below the mask; seeded randomness only; banned: centred
  title on gradient, everything fading, crossfades, spins, glitches, light leaks, bouncy easing on read text; holds
  carry a micro push 1.00→1.03–1.06. — …/references/motion-rules.md
- **Shorts:** hook ≤ 3 s, ≤ 7 words, frame 0 already shows something; 5–8 scenes; one visual event every 2–4 s;
  review warns at **3 s without movement, fails at 5 s**; platform UI top 14 %, bottom 20 %, right 12 %; recap
  restates the hook's idea in the same words. — …/references/shorts.md
- **Verify loop:** render-in-the-loop (max 5 minimal patches), ≤ 6 frames per scene at start/beat boundaries/end, vision
  critic JSON {overlap, safe-area, legibility, composition, beat-timing}, max 3 fix passes, critic exhaustion =
  soft fail (keep best, list warnings); critique rubric with 20 named failure modes (e.g. "frame 0 empty", "two things
  animate at once", "blank handoff between scenes", "numbers on screen disagree with narration"). —
  …/references/verify-loop.md, …/references/critique.md

### 7. Yusuke710/manim-skill + NousResearch hermes-agent `skills/creative/manim-video`
- **Timeline lint without rendering** (Yusuke710): a stub module simulates scene time and reports overlapping
  subtitles, overflows past a subtitle's end, subtitles past scene end; exit codes 0/1/2; tolerance 0.01 s. —
  https://raw.githubusercontent.com/Yusuke710/manim-skill/main/skills/manim-skill/tools/lint-subtitles.py
- **Selective re-render** (Yusuke710): one class per scene so feedback "[0:07] Scene3: label overlaps" re-renders only
  that scene; extract that exact frame (`ffmpeg -ss 7 … -vframes 1`) and look before touching code; low-res 15 fps
  iteration. — …/skills/manim-skill/SKILL.md
- **Pacing table** (hermes): new concept label 1.0 s anim + 1.0 s pause; key insight "aha" 2.5 s + 3.0 s pause;
  supporting annotation 0.8 s + 0.5 s; transition 0.5 s + 0.3 s; dramatic pause before the key reveal; vary tempo
  (slow build for core, quick succession for details); "identical pacing throughout" is a named failure. —
  https://raw.githubusercontent.com/NousResearch/hermes-agent/main/skills/creative/manim-video/references/animation-design-thinking.md
- **Opacity layering** (hermes): primary 1.0, context 0.4, structure (grids/axes) 0.15; "breathing room — a 2-second
  pause after a key reveal is never wasted"; geometry before algebra (show the thing, then name it — matches our
  "先演后命名"). — https://raw.githubusercontent.com/NousResearch/hermes-agent/main/skills/creative/manim-video/SKILL.md

Skipped/notes: kevinbadi/claude-motion-skills contains only README + verify tools (it mirrors iart-ai/motion-skills,
whose packs live in separate repos); I read iart-ai/tiktok-video-skills and kinetic-typography-skills for the
kinetic-type/TikTok content. Nothing failed to download.

---

## B. Ranked "steal-worthy" upgrades for the Pillow pipeline

All sketches use `easing.py` (`from easing import *`). Time `t` in seconds; cues from `cues.py`.

### 1. Spring presets instead of ad-hoc eases (highest value, near-zero cost)
**What:** closed-form damped-oscillator step response, normalised (`spring_u`) or released at a cue (`spring_at`).
Presets: `heavy` (critical, big keywords/titles, no overshoot), `snappy` (4 % peak, captions/labels/UI),
`bouncy` (16 % peak, **characters only**), `smooth` (overdamped, camera/cards), `punch` (punch-in).
**Why:** every repo names linear/fixed curves as the #1 "cheap AI video" tell; a spring accelerates, overshoots a hair,
stops → reads as weight.
```python
s = spring_at(t, T['jaw'], 0.0, 1.0, preset='bouncy')     # character jaw snap
y = lerp(y0, y1, spring_u(prog(t, T['kw'], 0.6), 'heavy'))  # keyword slides in, no bounce
```
**Conflict:** none. Note Mort1d/jabezpauls: "type never bounces" → use `heavy`/`snappy` on text, `bouncy` on faces.

### 2. Enter/exit envelope: 3 properties in, exit 2× faster, sequential swaps
**What:** `enter_exit(t, t_in, t_out)` → alpha (snaps on in ~4 frames), dy (spring rise), scale (0.94→1); exit
accelerates away (ease-in) in half the entrance time. Caption N+1 lands only after caption N is ≥ 95 % gone.
**Why:** lone fades read amateur (haidrrrry, jabezpauls); faster exits keep momentum; overlapping captions break
"one read at a time".
```python
def draw_caption(img, text, t, t_in, t_out):
    e = enter_exit(t, t_in, t_out, d_in=0.30, rise=36, s0=0.94, preset='snappy')
    if e['alpha'] <= 0: return
    D.text_pill(img, text, cx=540, cy=1350 + e['dy'], scale=e['scale'], alpha=e['alpha'])
# cues.py: assert next['t_in'] >= cur['t_out'] - 1/30
```
**Conflict:** the exit window must sit *after* the dwell: dwell = t_out − d_out − (t_in + d_in) ≥ max(1.5, chars/4).
Our dwell rule wins; lengthen the cue, never shorten the dwell.

### 3. Stagger helper for keyword / caption chunks
**What:** `stagger(i, n, total, gap)` → (start, dur). Chinese: per-character 30–40 ms for ≤ 6-char keywords; for
captions, 2–4-character chunks at 50–70 ms; cap total reveal ≈ 0.8 s (iart kinetic-typography).
**Why:** "nothing enters simultaneously" (haidrrrry); reading-order stagger guides the eye.
```python
chars = list(kw)
for i, ch in enumerate(chars):
    st, d = stagger(i, len(chars), 0.6, gap=0.035)
    k = spring_u(prog(t, T0 + st, d), 'heavy')
    draw_char(img, ch, x0 + adv[i], y0 + 60 * (1 - k), alpha=clamp01(k * 3))
```
**Conflict:** dwell is measured from the **last** char landing, not the first.

### 4. Per-chunk caption pop + one highlighted key term (no outline)
**What:** split each caption into 1–4-word pages (CJK: 2–6 chars); each chunk pops 0.85→1 with `snappy`; the
single key term gets the accent colour + soft glow, never more than one per line.
**Why:** iart caption-animation: word-level pop + one active highlight drives watch time; Mort1d: one accent word per
statement.
```python
for chunk, (t0, hot) in zip(chunks, times):
    p = spring_at(t, t0, 0.85, 1.0, 'snappy'); a = clamp01((t - t0) * 8)
    col = ACCENT if hot else WHITE
    if hot: glow(img, chunk_bbox, ACCENT, radius=18, alpha=0.35*a)   # glow, not stroke
    D.text(img, chunk, pos, fill=col, scale=p, alpha=a)
```
**Conflict (flag):** iart prescribes "2–6 px solid black outline + soft drop shadow". **Our rule wins: no dark outlines,
no offset shadow** — use our dark rounded caption pill + glow for separation.

### 5. Idle "breathing" on anything on screen > 2 s
**What:** `breathe(t, amp=0.012–0.02, hz≈0.3–0.5, phase)` scale and `bob(t, px=2–4, hz≈0.3)`; random-but-seeded
phase per element so they never move in lockstep; hold scenes add a micro push 1.00→1.03 (jabezpauls).
**Why:** lets long caption dwells (our 1.5 s+ rule) stay alive; review tools warn at 3 s without movement, fail at 5 s
(jabezpauls); "a frozen frame reads as a slide" (Mort1d).
```python
sc = breathe(t, 0.015, 0.42, phase=hash(name) % 7)
dy = bob(t, 3, 0.31, phase=1.3)
draw_char(img, cx, cy + dy, scale=base_scale * sc)
```
**Conflict:** keep it below our "元素自身的高频抖动压到 1/3" line: breathing is slow (< 0.6 Hz), not jitter.

### 6. Frame-QA script: contact sheet + phone view + automatic lints
**What:** `qa.py` that (a) renders stills at every cue and at ±0.1 s around every scene change via `film.py test`,
tiles them with `contact_sheet(frames, cols=6, thumb_w=270)` (≈ phone view); (b) lints from cues + cheap 1/4-res
renders: **motionless run** (mean abs frame diff < 0.5 for > 3 s), **pop** (one frame differs from both neighbours
far more than they differ from each other), **flash/blank** (frame ≈ background except intended white flash),
**safe-zone** (text bbox outside x 180–900 / y < 1440), **dwell** (our chars/4 rule), **determinism** (render frame k
cold and after k+50; must be byte-equal); (c) writes a REVIEW.md with 1–10 scores and the three worst problems with
time + evidence + fix.
**Why:** every repo makes "render → look → fix" mandatory; Mort1d's QA catches flash/pop/edges/hook automatically;
cheap on our 2 cores (quarter-res frames).
```python
def motionless_runs(frames, fps=30, thr=0.5, max_s=3.0):
    d = [np.abs(np.asarray(a, np.int16) - np.asarray(b, np.int16)).mean() for a, b in zip(frames, frames[1:])]
    run = 0; bad = []
    for i, v in enumerate(d):
        run = run + 1 if v < thr else 0
        if run == int(max_s * fps): bad.append(i / fps)
    return bad
def pops(frames, k=4.0):
    a = [np.asarray(f, np.int16) for f in frames]
    return [i for i in range(1, len(a) - 1)
            if np.abs(a[i]-a[i-1]).mean() > k*np.abs(a[i+1]-a[i-1]).mean() + 2]
```
**Conflict:** a pop at BIG2 / the 0 s hit is intended — whitelist those two cue times and the 0.1 s white flash.

### 7. Film grain + vignette as the last layer (after LANCZOS down)
**What:** `vignette(grain(frame, 0.03–0.04, seed=frame_idx), 0.22, 0.56)`; grain is luminance-weighted so the dark
background stays clean; seeded by frame index so chunks render identically in any order.
**Why:** haidrrrry's 5-layer stack ends with grain + vignette; Mort1d: "every surface: base + texture + edge"; it
removes the sterile flat-vector look and hides 8-bit banding on dark gradients (better H.264 too).
```python
frame = big.resize((1080, 1920), Image.LANCZOS)
frame = vignette(grain(frame, 0.035, seed=fi), strength=0.2)
```
Cost measured: ~0.10–0.14 s/frame at 1080×1920 (first call builds caches) → ~2.5 min CPU for 45 s @30 fps; fits
our 2-segment-per-command chunks (82 frames ≈ +10 s per segment). Apply grain only to the final 1080 frame, never
the 1.5× canvas.
**Conflict:** none (flat fills stay flat; grain is a film layer). Keep strength ≤ 0.04 so glows stay clean.

### 8. Sum-of-springs camera (`track`) + perceptual zoom
**What:** drive `cam(t)` zoom/pan from `track(t, [(t0,v0),(t1,v1)…], 'smooth')` so a new target mid-move keeps
velocity; interpolate zoom with `perceptual_scale(u, 1.00, 1.04)`; impact zoom = `punch`-preset spring capped at 4 %.
**Why:** Mort1d & jabezpauls: retargets must never restart a spring (jerks); remotion: linear scale looks like it
decelerates.
```python
z = track(t, [(0, 1.0), (T['BIG2'], 1.04), (T['BIG2'] + 0.5, 1.0)], 'smooth')
dx, dy = shake(t, T['BIG2'], amp=8, dur=0.35, seed=2)
```
**Conflict (flag):** Mort1d suggests shakes of 10–25 px and a 2–6 % push "through every hold". **Ours win: 8 px on the
two big hits, ~4 % impact zoom.** Also note: the brief says "1.5 px small shake", but the skill's latest rule
(2026-11-03) says small beats get **no** shake/zoom at all — reconcile in the skill (I assumed the newer rule).

### 9. Sub-frame motion blur only on whips/slams
**What:** `subframe_blur(draw_fn, t, fps=30, samples=3–4, shutter=0.5)` averages renders across half a frame
(remotion shutterAngle 180). Only on frames where something travels > ~30 px/frame (haidrrrry) — the 0 s slam,
BIG2, scene whips — never on text being read, fades or slow drifts (Mort1d).
**Why:** sells speed and removes strobing on the two big accents.
```python
if T['BIG2'] - 0.05 <= t <= T['BIG2'] + 0.25:
    frame = subframe_blur(lambda tt: render_frame(tt), t, samples=4)
```
Cost: ×4 on ~10 frames per accent ≈ +30 frame-renders total; budget in that chunk.
**Conflict:** none; keep captions out of the blurred layer (draw them after the blur).

### 10. Audio–picture sync rules for `music.py`
**What:** (a) visuals land `HIT_LEAD`≈1–2 frames (0.03–0.06 s) **before** the cue (jabezpauls, Mort1d "light before
sound"); (b) place samples by their loudest point, not their start (compute peak offset once per SF2 sample);
(c) whooshes start before the landing so they peak on it (haidrrrry: 2–3 frames early); (d) a short `gap()` of
⅛–½ beat silence right before BIG2; (e) repeated light SFX vary ±1 semitone or rate 0.92–1.08; never two whooshes at
once; (f) duck the bed 0.35–0.45 under each hit; (g) ring-out ≥ 1.5 s after the last hit.
```python
def place(buf, smp, t_cue, gain=1.0):
    pk = int(np.argmax(np.abs(smp)))
    i0 = int(t_cue * SR) - pk
    buf[max(i0,0):i0+len(smp)] += gain * smp[max(-i0,0):]
semis = [0, 1, -1, 2, 0, -2]           # deterministic variation for repeated pops
```
**Conflict (flag):** Mort1d puts "hits on every beat" and a riser+boom+crash stack on reveals; **ours: only two big
accents, light SFX (wood block, pluck, pop, tom) elsewhere** (user 2026-10-23). The `gap()` before BIG2 must be a
sub-beat breath, not the "black-screen silence" the user rejected on 2026-11-03.

### 11. Attention hierarchy: one hero, opacity layering, recede-don't-vanish
**What:** per frame exactly one hero element at full brightness + glow; context at 0.4, structure (grids, labels,
background props) at 0.15 (hermes); the hero keyword ≥ 1.8× the next text size (Mort1d); past content dims to 0.4
instead of disappearing when the story still needs it (jabezpauls).
**Why:** in a busy multi-layer frame (our flytrap formula) the eye needs one target; "more than one glowing element
= Vegas" (haidrrrry).
```python
LAYER_ALPHA = {'hero': 1.0, 'context': 0.4, 'struct': 0.15}
def recede(t, t_done, a_from=1.0, a_to=0.4): return lerp(a_from, a_to, ease_out_cubic(prog(t, t_done, 0.4)))
```
**Conflict:** none.

### 12. Export + loudness contract and an ffprobe gate
**What:** `-c:v libx264 -profile:v high -crf 16–18 -pix_fmt yuv420p -color_range tv -colorspace bt709
-color_primaries bt709 -color_trc bt709 -movflags +faststart`, AAC; gate script asserts h264, 1080×1920, 30 fps,
yuv420p, tv/bt709, one aac stream, frame count = duration × 30. Loudness target −14 LUFS, true peak ≤ −1 dBTP.
**Why:** untagged files can wash out on upload (charlie947); faststart starts playback immediately; we already check
frame count with `-count_packets`.
**Conflict (flag):** our music currently normalises to −15 LUFS; −14 is the platform-normalised norm (Mort1d,
jabezpauls). Consider −14 with the true-peak limiter; low risk either way.

### 13. Hook & first-frame rules as a lint (bonus)
**What:** in `cues.py` assert: hook text visible at frame 1 (alpha > 0.5 by t = 0.05), no fade-up from black, frame 0
= the best/most striking frame, hook ≤ 7 words/≈12 Chinese chars, one open question only; optional seamless loop by
easing the last 0.5 s toward frame 0 (iart).
**Why:** retention cliffs at 0–2 s are the hook (iart table); jabezpauls fails "frame 0 empty"; matches our 0 s accent.
**Conflict:** none.

Rejected as off-style: Vox "stepped motion on twos" and torn paper (charlie947), light leaks (jabezpauls bans them;
we already have a 0.1 s white flash as our overlay), blur-in type (costly with Pillow GaussianBlur per glyph).

---

## C. 草稿：可追加到 vibe-knowledge-film 的「动效细节」补充规则

```
## 动效细节（2026-11-04 调研开源动效 skill 后整理，冲突时以上面已有规则为准）
工具库：work/distill/easing.py（spring/overshoot/stagger/envelope/breathe/shake/grain/vignette/contact_sheet，自带自测）。
### 缓动
- 不用线性缓动，进度一律先 clamp 到 0–1。线性只用于持续漂移、旋转、视差。
- 动作统一用弹簧：大字/关键词用 heavy（不回弹）；字幕和标签用 snappy（约 4% 过冲）；角色表情、跳动用 bouncy（约 16%）；镜头和卡片用 smooth。文字不弹。
- 缩放用几何插值（perceptual_scale），否则放大会显得越来越慢。
- 一个值会多次改目标（镜头、指针）时，用 track() 把几段弹簧叠起来，中途改目标不会顿。
### 进场、退场
- 进场同时动 2–3 个属性（透明度 + 上移 + 缩放 0.94→1），主体不能只靠淡入淡出。
- 退场时长约为进场的一半，用加速的 ease-in。
- 字幕换句要排队：上一句至少消失 95% 后，下一句才落地，最多重叠 1 帧。停留时长从最后一个字落地算到开始退场。
- 关键词逐字出：每字间隔 30–40ms，整句展开不超过约 0.8 秒；字幕按 2–6 字一块弹出。
- 讲过但后面还要用的东西降到 0.4 透明度，不直接删掉。
### 画面层级
- 每帧只有一个主角：亮度 1.0 并加 glow；陪衬 0.4；网格、背景道具 0.15。同一帧只能有一个发光体。
- 主关键词字号至少是同屏第二大文字的 1.8 倍。每句只给一个词上强调色。
- 字幕高亮靠强调色 + glow + 深色胶囊底，不加描边和投影（外部 skill 推荐的黑描边不采用）。
### 不能有死帧
- 在屏上超过 2 秒的元素都要有呼吸：缩放 ±1.5%，0.3–0.5Hz；上下浮动 2–4px。每个元素的相位错开。
- 安静段整体慢推 1.00→1.03。连续 3 秒画面几乎不动就算不合格。
- 呼吸是慢动作，不算抖动，元素高频抖动仍然压到 1/3。
### 质感
- 最后一层（LANCZOS 缩小到 1080 之后）加胶片颗粒 grain(0.03–0.04, seed=帧号) 和暗角 vignette(0.2)。种子用帧号，分段渲染结果一致。每帧多花约 0.12 秒。
- 运动模糊只加在 0 秒和 BIG2 两个大重音、每帧位移超过 30px 的快速动作上（subframe_blur 取 4 个样本），字幕画在模糊层之后。
### 音画同步
- 画面落点比 cue 早 1–2 帧；音效按样本最响的那一点对齐 cue，不按样本开头对齐。
- BIG2 前留 ⅛–½ 拍的短暂停顿就够，不要黑屏静音。
- 重复出现的轻音效每次变化一点：±1 个半音，或速度 0.92–1.08。同一时刻不叠两个 whoosh。
- 最后一个音结束后留 ≥1.5 秒余音。重音处把铺底音乐压低到 0.35–0.45。
### 交付前质检（qa.py）
- 每个 cue 出一张图，每次切场的 ±0.1 秒各出一张，拼成 270px 宽的手机视图 contact sheet，逐张看。
- 自动检查以下几项：连续 3 秒不动、单帧跳变（0 秒、BIG2、白闪除外）、空帧、文字超出安全区（x 180–900，y<1440）、字幕停留不达标。同一帧冷启动渲染和顺序渲染的结果必须一模一样。
- 按开头、手机可读、动效、变化频率、构图、准确、音画同步打 1–10 分，写下最差的三处（时间 + 证据 + 改法）。改完再打分，全部 ≥8 才渲全片。一次只改一处。
- 导出要带 bt709 和 tv range 标记，yuv420p，加 +faststart。ffprobe 核对编码、分辨率、帧数 = 时长×30。
```
(38 rule lines.)
