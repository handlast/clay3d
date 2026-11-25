# BGM composition rules ("structural beauty"), audit of 《冲不走的鱼》 BGM, v2 plan

Written 2026-11-04. Scope: **composition and form only, not mixing** (mixing notes are in `notes.md` in this folder). Target: 60–80 s Douyin science shorts, BGM built in numpy with the GM sampler (`/workspace/work/sf/samp.py`), arrangement written in code (`/workspace/work/exostoma/music.py`, timeline in `cues.py`).

Why the mixing A/B sounded the same: the current track's problems are in the notes, not the processing. It uses one 2-bar 16th-note scale run that loops about 10 times without developing. Nothing in it is a hook you could hum. Cadences are not tied to the picture. The texture changes about every 2 bars, but the tune never changes. Mixing cannot fix any of that.

Units used below: at 108 BPM, 1 beat = 0.556 s, 1 bar = 2.222 s, 2 bars = 4.44 s, 8 bars = 17.8 s. "st" = semitones.

---

## (a) Rules we can encode (numbers + sources)

Each rule has the number to encode and its source. "Engineering choice" marks a number I picked to make a qualitative source codeable. It is not a measured statistic.

**R1. Write themes as 8-bar sentences: 2 + 2 + 4 bars (proportion 1:1:2).** Bars 1–2 hold the basic idea (BI). Bars 3–4 repeat it, either exactly, transposed, or re-harmonized (this is the *presentation*). Bars 5–8 are the *continuation*: it gains energy and drives to a cadence. At slower tempi a sentence can be 1+1+2 bars, at faster ones 4+4+8. The period is the alternative form: antecedent (4 bars, weak ending) plus consequent (4 bars, strong ending).
*Encode:* 32 bars after the reveal = 4 themes of 8 bars (A sentence, B period, C development, D final sentence).
Sources: Schoenberg, *Fundamentals of Musical Composition* ("an immediate repetition is the simplest solution, and is characteristic of the sentence structure"), https://ia800508.us.archive.org/27/items/a.-schoenberg-fundamentals-of-musical-composition/A.Schoenberg-Fundamentals%20of%20Musical%20Composition_text.pdf ; Mount, *Fundamentals, Function, and Form* ch. 35 (2+2+4, plus the 1+1+2 and 4+4+8 variants), https://milnepublishing.geneseo.edu/fundamentals-function-form/chapter/35-sentences-and-periods/ ; Caplin's formal functions (2-bar basic idea, 8-bar theme), https://en.wikipedia.org/wiki/William_Caplin

**R2. The motif is 2 bars long, has 5–10 notes, a distinctive rhythm, and at least one rest or long note.** Store it as **scale degrees + relative rhythm, never as MIDI pitches**, so every transformation stays in the mode. Folk-song phrases average 9.5 notes (SD 3.4).
*Encode:* `MOTIF = [(onset16, degree, dur16), ...]`, 8–10 events over 32 sixteenth-note steps. No more than 8 consecutive 16th-note onsets.
Sources: Tierney, Russo & Patel 2011, PNAS (Essen corpus: 9.5 notes/phrase, range 8.9 st), https://www.pnas.org/doi/full/10.1073/pnas.1103882108 ; harmony-engine README (motif = 2-bar cell, 4–7 notes, one leap, stored as degrees; MIT), https://github.com/kentog751/harmony-engine

**R3. Continuation = fragmentation + acceleration.** After the presentation, break the BI into 1-bar units, then ½-bar units, sequenced. Also speed up the harmonic rhythm and/or the surface rhythm toward the cadence. Film-theme sentences use at least one of three accelerations: fragmentation, faster harmonic rhythm, or faster surface rhythm. "By far most" use fragmentation.
*Encode:* continuation bars 5–6 = 1-bar fragment ×2 (sequence up one scale step). Bar 7 = ½-bar fragment ×2 with 2 chords in the bar. Bar 8 = cadence, ending on a long note.
Sources: Caplin (continuation "fragments the initial idea by breaking it into one-bar motives and thereby accelerating movement toward the cadence"), Wikipedia link above; Richards 2016, "Film Music Themes: Analysis and Corpus Study," MTO 22.1, ¶14, https://mtosmt.org/issues/mto.16.22.1/mto.16.22.1.richards.html

**R4. Every lead bar must come from the motif through one named operator.** Allowed operators: repeat, tonal sequence (transpose by scale steps), inversion (mirror the degrees around the tonic), augmentation (durations ×2), diminution (×½), fragmentation (first bar, or the last 3 notes), plus extension or ornament. No free, unrelated melodies.
*Encode:* `derive(motif, op, arg)` returns note events. Lead tracks may only call `derive`. Log which operator each bar used.
Sources: Ithaca College handout, Basic Developmental Techniques, https://musictech.ithaca.edu/MusicTech/Form/Handouts/DevTech.html ; Open Music Theory, motive transformations, https://viva.pressbooks.pub/openmusictheory/chapter/foundational-concepts/ ; harmony-engine ("every bar of melody is that cell as a statement, a sequence up a third, an inversion, a rhythmic augmentation, or a fragment of its last three notes").

**R5. The basic idea has to come back.** The most common film-theme types are the ones that restate the BI. That repetition is how a leitmotif becomes familiar. Across 482 Oscar-nominated main themes, 74% are "grammatical" themes (sentence, period, clause, composite), and basic sentences and periods are the most common types.
*Encode, as a story arc:* foreshadow (a fragment in the hook) → full statement at BIG2 → developed in the middle (inversion or augmentation) → full restatement at the ending, with one variation (octave doubling, augmented last note).
Source: Richards 2016, ¶59–62, ¶69, link above.

**R6. Contour: an ordinary arch, plus one unusual interval.** Earworm tunes have *more common* global contours, and *less common* average slopes between turning points (unusual leaps or intervals). They also have faster tempi (mean 124 vs 116 BPM). The rise-then-fall arch is the most common contour.
*Encode:* each 2-bar phrase peaks in its middle third, and the first and last notes sit below the mean pitch. Each motif contains one "signature" interval. In D phrygian dominant that is the augmented 2nd **E♭→F♯ (+3 st)** used as a melodic step.
Sources: Jakubowski, Finkel, Stewart & Müllensiefen 2016/17, *Psychology of Aesthetics, Creativity, and the Arts*, http://www.doc.gold.ac.uk/~mas03dm/papers/JakubowskiFinkelStewartMullensiefen_earworms_2016.pdf ; Tierney et al. 2011 (arch and descending contours most common, P<0.0001).

**R7. Keep the line smooth: mostly small intervals, and change direction after a big leap.** Human song is strongly biased toward small intervals. Its interval-compression ratio (mean |interval| of the shuffled melody ÷ mean |interval| of the real one) has a median of 1.46. In 100 Western folk melodies, **79.6%** of intervals larger than 6 st are followed by a change of direction, against 44.5% for smaller intervals. Phrase range averages 8.9 st (SD 3.7).
*Encode:* interval-compression ratio ≥ 1.4. At least 65% of intervals ≤ 2 st, counting the aug-2nd E♭–F♯ as a scale step. Any interval > 6 st is followed by an opposite-direction step. Range ≤ 12 st per 2-bar phrase and ≤ 15 st per 8-bar theme.
Sources: Tierney et al. 2011; Huron & Royal 1996, "What is melodic accent?", *Music Perception* 13(4), p. 510, https://www.academia.edu/17380217/What_is_melodic_accent_Converging_evidence_from_musical_practice ; von Hippel & Huron 2000 (reversal is largely a range effect, so a range cap gets you most of it), https://doi.org/10.2307/40285901

**R8. Lengthen phrase-final notes, and breathe.** In 36,313 folk phrases, phrase-final notes average **1.58×** the phrase's mean note length, against 0.93× for other notes.
*Encode:* the last note of every 2-bar phrase is ≥ 1.5× that phrase's mean note length, followed by a rest of ≥ 2 sixteenths in the lead. The rest is the space where an answer or SFX goes.
Source: Tierney et al. 2011.

**R9. Rank cadences, and tie them to cuts.** In a period, the second phrase must end more conclusively than the first. Otherwise it is just a repeated phrase. In flamenco/phrygian-dominant harmony, the **♭II chord plays the dominant's role** (vii can substitute). The paradigmatic cadence is the Andalusian **iv–III–♭II–I**, which in D is Gm–F–E♭–D. V7 is essentially absent.
*Encode:*
- Weak ending (half cadence) = phrase ends on E♭, or on D with the melody on A.
- Strong ending = E♭→D with the melody landing on D on a downbeat.
- Strongest = Gm–F–E♭–D over the last 2 bars.
- At most one strong cadence per 8 bars. Place cadences at section boundaries: the cadence's arrival downbeat sits on, or within 1 beat of, a picture cut.

Sources: Mount ch. 35 (period definition), link above; Manuel 2016, "Flamenco Jazz: An Analytical Study," *Journal of Jazz Studies* 11(2), pp. 36 and 58–59, https://academicworks.cuny.edu/cgi/viewcontent.cgi?article=1324&context=jj_pubs

**R10. Use only chords from the mode, put chord tones on strong beats, and speed up the harmony at cadences.**
- Chord vocabulary for D phrygian dominant: D (or D7), E♭, F (flamenco uses both thirds over the tonic), Gm, B♭, Cm. **Never C major**, because its E♮ is outside the mode.
- Melody notes on beats 1 and 3 are chord tones ≥ 75% of the time (engineering choice, based on how two generators handle downbeats). Other strong-beat notes must step to a chord tone.
- Harmonic rhythm: 1 chord per bar by default, 1 chord per 2 bars in calm sections, 2 per bar in continuations and cadences.

Sources: Manuel 2016 (chord set; flamenco melodies use the raised or lowered third by context); harmony-engine (legality gate; "one chord per bar, two bars per chord when calm, half a bar at cadences"); GenreGrid README ("targets chord tones on downbeats"; GPL-3.0), https://github.com/TwDover/GenreGrid ; Caplin ("accelerating the rate of harmonic change").

**R11. Hypermeter: change things only on 2/4/8-bar boundaries.** In EDM, layers are "most often introduced, changed and removed after 2, 4, 8, 16 or 32 bars". The basic unit is 2 or 4 bars.
*Encode:*
- Add or remove layers only on downbeats of even bars, measured from the bar grid that starts at BIG2.
- Phrase boundaries every 4 bars, theme boundaries every 8.
- If a picture cut lands off the grid, either pad the cue to a 2-beat multiple (see v2), or treat the cut as a pickup and make the musical change on the next downbeat. The impact SFX stays on the cut.

Source: Solberg 2014, "Waiting for the Bass to Drop," *Dancecult* 6(1), p. 66, https://dj.dancecult.net/index.php/dancecult/article/download/451/457

**R12. Energy arc = vertical layering plus a break routine.** Raise intensity by adding layers in a fixed order: bass and pad → hand percussion → kick → arpeggio → lead → full groove. A break routine runs breakdown (bass and kick removed) → build (layers re-enter; the snare or hand drum subdivides 4ths→8ths→16ths, the "drum-roll effect") → drop (bass and kick return). The second build-and-drop is more intense than the first.
*Encode:*
- Each section gets a level L0–L5, so the arc is a list of numbers. Neighbouring levels differ by ≤ 2, except at the 2 accents.
- The overall shape is: high (hook) → low → peak (BIG2) → dip → rise → highest density at the final statement.
- In our format only 2 accents are allowed, so later builds arrive on a *texture* (full groove plus the motif), never on another hit.

Sources: Solberg 2014, pp. 66–68 and 78 (break routine, drum-roll subdivision, bass/kick removal); Sweet, *Writing Interactive Music for Video Games*, ch. 9 "Vertical Remixing" (layers added or removed for intensity), https://www.oreilly.com/library/view/writing-interactive-music/9780133563528/ch09.html ; harmony-engine (fixed layer entry order "because that order is what a listener perceives as a build"; drums removed the bar before a lift).

**R13. Change budget: statement, repetition, then change.** The sentence's 1:1:2 shape is the "rule of three" in miniature: say it, say it again, then change it. At the arrangement level, make one meaningful change at a time (sound, harmony, melody, rhythm, or form) every 4 bars. Use "unique events" sparingly, because too many of them become predictable themselves.
*Encode:*
- No 4-bar span without at least one change in melody, harmony, or layers.
- No 2-bar span with more than one category changing, except at the 2 accents.
- No more than one non-diegetic "unique" stinger per 8 bars. SFX tied to on-screen events don't count.

Sources: Mount ch. 35; DeSantis, *Making Music* (Ableton), "Creating Variation 2: Mutation Over Generations" (one meaningful change per generation), https://makingmusic.ableton.com/creating-variation-2-mutation-over-generations , and "Unique Events", https://makingmusic.ableton.com/unique-events ; Solberg 2014 ("with variation, but not too much").

**R14. One lead at a time; use call and response.** An antecedent and consequent work as question and answer. A second melodic voice should answer in the lead's rests rather than play its own unrelated line on top.
*Encode:*
- A `lead_owner[bar]` array says which instrument owns the lead in each bar.
- A second voice may only (a) answer inside the owner's rests, (b) double the owner's line at the octave or a 3rd or 6th, or (c) sustain long notes.
- Arpeggios get louder during lead rests and quieter while the lead plays.

Sources: Mount ch. 35 ("the antecedent poses a question and the consequent provides the answer"); GenreGrid README ("arpeggio call-and-response — boosts arpeggio velocity during melody rests").

Repos that encode similar rules (for reading only; no code was copied):
- kentog751/harmony-engine (MIT, JS): motif-as-degrees, development operators, 4+4 question/answer, fixed layer-entry order.
- TwDover/GenreGrid (GPL-3.0, Python/FastAPI): phrase roles (statement, restatement, contrast, climax, resolution) planned before any notes are written, and "exactly one high point" per section.
- RangoonRen/abundant-music (MIT fork of the Abundant Music procedural generator), https://github.com/RangoonRen/abundant-music , not inspected in depth.

---

## (b) Audit of the current exostoma BGM (`music.py` + `cues.py`, read-only)

What it is now: 108 BPM, D phrygian dominant over a D drone. `PROG = D D E♭ D D C E♭ D` (1 chord per bar, 8-bar loop). The sitar lead alternates two 1-bar patterns, `RIFF` and `RIFF2`, every bar (`alt` = always `RIFF2`). The flute/shakuhachi `FL` is a separate 4-bar loop. Kalimba plays arpeggios. The bar grid restarts at BIG2 (8.733 s). Sections after BIG2 start at bars 0, 1.75, 3.75, 5.75, 7.75, 9.75, 11.25, 13.25, 15.25, 17.25, 19.25, 21.5, 23.5, 25.75, 28 (end at 30.75). Measured from the code and from `bgm.wav`:

| Rule | Result | Evidence | What to change |
|---|---|---|---|
| R1 8-bar sentence/period form | **FAIL** | No form above 2 bars. The lead is a 2-bar loop; the chords are an 8-bar loop that ignores the sections. | Build 4 themes of 8 bars after BIG2 (see v2). |
| R2 2-bar motif with rhythmic identity | **FAIL** | `RIFF` = 13 onsets per bar of nearly continuous 16ths (a scale up and down), with no rests. `RIFF2` = 10 onsets. Nothing to hum. | One 9-note motif with a short–short–long rhythm and a rest. |
| R3 continuation fragments and accelerates | **FAIL** | RIFF/RIFF2 just alternate; no fragmentation; harmonic rhythm fixed at 1 per bar. | Bars 5–8 of each theme: 1-bar → ½-bar fragments, 2 chords per bar at the cadence. |
| R4 every lead bar derived from the motif | **FAIL** | `FL` is unrelated material (same scale, different contour). Kalimba is chord arpeggios only. | Generate every lead with `derive(MOTIF, op)`. |
| R5 BI recurs as an arc | **FAIL** | Reveal and ending play the identical sitar riff plus the identical flute loop. "stay" has one sitar note (D5) and no motif. Nothing is foreshadowed or developed. | Foreshadow → state → develop → restate with a variation. |
| R6 common arch + one signature interval | **PARTIAL** | RIFF is an up-down arch within each bar, but as a scale run: generic contour and generic slope. The aug-2nd E♭–F♯ is buried mid-run. | Put E♭→F♯ at a rhythmically exposed spot in the motif. |
| R7 smooth line, range | **PASS (mostly)** | Intervals ≤ 2 st: RIFF 75%, RIFF2 56%, FL 62%. Nearly all are scale steps. Range 12 st (riff) and 14 st (flute). One 11-st jump at the RIFF→RIFF2 bar seam is followed by a reversal. | Keep. Trim the range to ≤ 12 st per phrase. |
| R8 long phrase-final notes, breaths | **FAIL** | RIFF ends on a 16th, RIFF2 on an 8th, and they join seamlessly, so the lead never breathes. FL3 has one half note (partial). | Final note ≥ 1.5× the mean note length, plus a rest. |
| R9 ranked cadences tied to cuts | **FAIL** | The E♭→D cadence falls wherever the bar counter puts it (bars 6→7 of each 8), not at sections. "catfish" cuts on beat 4 of the resolution bar. No weak-then-strong pairs. | Place half and full cadences on section boundaries. Gm–F–E♭–D only at theme ends. |
| R10 in-mode chords, chord tones on strong beats | **FAIL** | `CH["C"] = C E G`: the E♮ is out of the mode and clashes with the sitar's E♭ (deg 1) in bar 5 of every cycle. On beats 1 and 3, **11 of 28 riff notes (39%) are non-chord tones**, including semitone clashes: A against the E♭ chord's B♭ (bars 2 and 6) and F♯ against the C chord's G (bar 5). | Replace C with Cm (vii) or B♭. Keep non-chord strong-beat notes ≤ 25%, all stepping to chord tones. |
| R11 changes on 2/4/8-bar grid | **FAIL** | 12 of 15 section starts fall mid-bar: beat 4 at 1.75, 3.75, …, 25.75; beat 2 at 11.25–19.25; beat 3 at 21.5 and 23.5. So the kick drops out (catfish) or comes back (latin) off the downbeat. Layers change about every 2 bars (14 changes in 31 bars). | Pad cues to 2-beat multiples, or quantize music changes to the next downbeat. |
| R12 energy arc | **PARTIAL** | Has a breakdown (catfish/nameq, −20 to −24 dB), a build (nose riser) and a drop (BIG2). After BIG2, section RMS zig-zags: −16.4, −15.6, −15.7, −19.9, −23.8, −19.2, −17.2, −19.7, −19.7, −17.2, −17.1, −17.1, −20.5, −16.4 dB. There is no rising second half, and the ending is no louder or denser than "flat". **A third big accent at FINAL** (taiko + sub + crash + chord hit at `end`+8 beats) breaks the 2-accent rule. | Make the final statement the densest point. Replace the FINAL hit with a held cadence chord (no taiko, sub or crash). |
| R13 change budget | **FAIL (inverted)** | Texture changes every 2 bars, but the melody never changes. That is busy and static at once. About 46 SFX calls (about 60 events counting loops) in 77 s. | Change one category every 4 bars, with the melody leading the changes. |
| R14 one lead at a time | **FAIL** | Flute FL plays on top of the sitar riff for about 4 bars (fins→catfish) and about 3.6 bars (end): two independent leads at once. Kalimba arpeggios run under the shakuhachi lead in "sense". | Use a `lead_owner` per bar; second voices only answer or double. |
| Constraint: no silent gaps | PASS (borderline) | Lowest 0.25-s window after 0 s: −36 dBFS at 7.25 s (the "q" suspense) and −29.6 at the tape stop. No digital silence. | Keep the q section above about −30 dBFS: drone plus the motif cell. |
| Constraint: 2 accents only | **FAIL** | Accents at 0 s and BIG2 are correct; FINAL adds a third. | Remove the third. |

The main failures are R2–R5 (no motif and no development), R10 (the C-major chord and 39% strong-beat clashes), R11 (changes off the bar grid), and R12/R14 (no final climax, overlapping leads, a third accent).

---

## (c) Plan for a v2 BGM (same 108 BPM, D phrygian dominant, sitar/dulcimer/flute/hand drums, no vocals, accents only at 0 s and BIG2, no gaps)

### Timeline (choose one)
- **Option A (recommended): pad each POST segment in `cues.py` up to a multiple of 2 beats.** Segment lengths in beats become reveal 8, flat 8, fins 8, barbel 8, catfish 8, nameq 6, nose 8, latin 8, sense 8, murky 8, where 10, rare 8, ident 10, card 10, end 12. That is **128 beats = exactly 32 bars after BIG2**; DUR goes from 77.07 to **79.84 s** (still within 80 s). Every cut then lands on beat 1 or beat 3.
- **Option B:** keep `cues.py` as is. Run the music on its own 8-bar grid from BIG2. SFX and picture hits stay on the cuts; each layer or harmony change moves to the nearest downbeat (≤ ±2 beats).

Bar map for Option A (bars from BIG2): reveal 0, flat 2, fins 4, barbel 6 | catfish 8, nameq 10, nose 11.5, latin 13.5 | sense 15.5, murky 17.5, where 19.5, rare 22 | ident 24, card 26.5, end 29 → 32.

### The motif M (2 bars; degrees of D phrygian dominant, 0 = D4; positions on a 16th grid)
- Bar 1: `0:D(2) 2:E♭(2) 4:F♯(6) 10:G(2) 12:A(4)`
- Bar 2: `0:G(3) 3:F♯(1) 4:E♭(4) 8:D(6)`, then rest for 2 sixteenths
- Intervals: +1, **+3**, +1, +2 | −2, −1, **−3**, −1. That is an arch peaking on A in the middle third, with the aug-2nd signature going up and then coming down (R6). All intervals are ≤ 3 st and the range is 7 st (R7). It has 9 notes (R2). The final D lasts 6 sixteenths, 1.8× the mean of 3.3 (R8). Its strong-beat notes are D, F♯, A / G(→F♯), E♭(→D) over D–D, which is either chord tones or stepwise appoggiaturas (R10).

### Form, harmony and energy (L = layer level 0–5)
| Time / section | Bars | Level | Lead (operator on M) | Harmony | Notes |
|---|---|---|---|---|---|
| hook 0–3.73 | pre | **L5, ACCENT 1** | sitar: bar 1 of M only (foreshadow), then tape stop | D | Groove as now |
| stay 3.73–7.07 | pre | L2 | sitar, soft: first 5 notes of M at ×2 augmentation | D drone | Hand drums + water |
| q 7.07–8.73 | pre | L1→L2 | dulcimer: cell D–E♭–F♯ repeated, 8ths → 16ths (drum-roll effect) | D → E♭ (pickup) | Riser; stay ≥ −30 dBFS |
| **A** reveal / flat / fins / barbel | 0–8 | **L5, ACCENT 2** → L4 | Sentence in sitar: M (D–D) · M a tonal step up (E♭–D, last note adjusted to D) · bar 1 of M ×2, sequenced up (Gm, F) · ½-bar cell ×2 → cadence | D D │ E♭ D │ Gm F │ E♭+Cm │ **Gm–F–E♭–D** cadence lands bar 8 = catfish cut | Full groove; flute silent |
| **B** catfish / nameq / nose / latin | 8–16 | L2 → L3 → L4 | Period. Antecedent (8–12): kalimba plays M at ×2 augmentation, ending weak on E♭ at nameq. Consequent (12–16): sitar plays bar 1, flute answers with bar 2 (call and response), strong ending on D | 2 bars per chord: D │ Cm │ D │ E♭ ‖ D │ Gm │ E♭ │ D | Breakdown (no kick) → nose build: hand-drum subdivision, bass back, **no hit** → latin: kick back on the bar-14 downbeat |
| **C** sense / murky / where | 16–24 | L3 → L4 | Development. Shakuhachi/flute plays the **inversion** of M (D C B♭ A G …) in half-time. At "where", sitar plays M a 3rd higher (starting on F♯) | Calm: D │ B♭ │ Cm │ E♭ ‖ D │ Gm │ F │ E♭ (half cadence) | One lead per bar; kalimba only during lead rests |
| **D** ident / card / end | 24–32 | L4 → L3 → **L5 (no accent)** | ident: fragments get shorter (1 bar → ½ bar), 2 chords per bar. card: one "breath", kick out 2 bars, dulcimer holds the cell. end: **full restatement of M** with sitar + flute in octaves, final E♭→D at ×2 augmentation | ident: Gm F │ E♭ Cm … end: D │ E♭ │ **Gm–F │ E♭–D** | Densest arrangement of the piece. Final D chord sustained and faded. **No taiko, sub or crash** (keeps 2 accents) |

### Checks to run in code before rendering
1. Interval-compression ratio of the lead ≥ 1.4; ≥ 65% of intervals ≤ 2 st; range ≤ 12 st per phrase.
2. Strong-beat non-chord tones ≤ 25%; no pitch class 4 (E♮) anywhere.
3. Every lead bar carries a `derive` operator tag; `lead_owner` has one owner per bar.
4. Layer changes only at even-bar downbeats (Option A) or snapped to the nearest downbeat (Option B).
5. Short-term level ≥ −30 dBFS in every 0.25-s window after 0.1 s; exactly 2 impact events (0 s, BIG2).
6. The final section has the highest note density and layer count.

Open items: none of this has been heard yet. Melodic decisions such as the motif notes should be judged by ear on a 2-bar render first. The 75% strong-beat chord-tone threshold and the "one change per 4 bars" budget are engineering choices built from qualitative sources, as marked above.
