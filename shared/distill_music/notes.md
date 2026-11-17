# BGM pipeline: open-source review (2026-11-04)

Scope: improve the code-generated BGM for 60–80 s Douyin shorts (numpy + GM sampler `/workspace/work/sf/samp.py`, hand-written arrangement as in `/workspace/work/exostoma/music.py`, Sonniss SFX, ffmpeg loudnorm -15 LUFS). Limits: 2 cores, no GPU, each command under 120 s, no English vocals, two big accents only, no silent gaps.

How the current mix works (from exostoma/music.py): MIX/MEL/FX buses → one noise-IR FFT reverb (1.8 s) → 3-tap ping-pong echo → normalize → DUCK applied only at the two big hits → `tanh(1.8x)` soft-clip on the whole mix → loudnorm. Humanize is ±3 ms / ±6 % gain on every note. There's no EQ, no per-bus compression, no kick-keyed ducking, and chord stabs are fixed root-position voicings (`CH` dict). The `tanh` stage does most of the loudness work, so it flattens transients. That's the main thing to fix.

## 1. Ranked shortlist

| # | Project | License | Installs here? | Verdict |
|---|---|---|---|---|
| 1 | **spotify/pedalboard** (github.com/spotify/pedalboard, 6.4k★, pushed 2026-11-03) | GPL-3.0 (JUCE/Rubber Band inside) | **Yes**: `pip install --target /workspace/.pylib --no-deps pedalboard` (0.9.26, aarch64 cp312 wheel, needs only the numpy already there). Tested. | **ADOPT** |
| 2 | **Euclidean rhythms + swing from TidalCycles/Strudel** (strudel.cc/learn/time-modifiers; github.com/tidalcycles/strudel is archived, code moved to codeberg.org/uzu/strudel) | Strudel AGPL-3.0, Tidal GPL-3.0 | Not a Python library. Reimplement the idea in about 3 lines (no code copied) | **ADOPT (idea only)** |
| 3 | **Voice-leading** (Strudel `voicing()` / music21 idea); done as a 15-line brute-force in demo.py | — (our own code) | n/a | **ADOPT (own code)** |
| 4 | **csteinmetz1/pyloudnorm** (MIT, pure-python, needs scipy) | MIT | Pure wheel, but pulls scipy (~40 MB). ffmpeg `ebur128` already does the job | **MAYBE**: only if we want per-section LUFS inside Python |
| 5 | **DawDreamer** (DBraun/DawDreamer; Faust + sampler + VST host) | GPL-3.0 | aarch64 cp312 wheel exists (0.9.0). Not installed (large) | **MAYBE**: only if we later want Faust synths. Pedalboard covers our FX needs |
| 6 | **sergree/matchering 2.0.6** (reference mastering: matches RMS, frequency response, peak, stereo width to a reference track) | GPL-3.0 | Pure wheel, but needs scipy + statsmodels + resampy, and 4 GB RAM per README. Last release 2022-10 | **SKIP for now**: needs a licensed reference track per style. Its 4 targets are easy to check ourselves (rules R9–R10) |
| 7 | **FluidSynth + pyfluidsynth** (FluidSynth/fluidsynth LGPL-2.1, pyfluidsynth MIT) | LGPL / MIT | **No**: no libfluidsynth on the box, not root (uid 1000), and pyfluidsynth is only a ctypes wrapper | **SKIP**: samp.py already plays GeneralUser GS. The real gap is SF2 *initial attenuation* + filter envelopes, which we patch by hand (known per-preset gain table) |
| 8 | **pretty_midi / mido / music21 / musicpy** | MIT / MIT / BSD-3 / LGPL-2.1 | All pure-python and pip-able | **SKIP**: we don't use MIDI files. Theory needs are tiny (scale degrees, voice-leading), already in-house. music21 is heavy for what it gives |

Not evaluated in depth: SuperCollider and Sonic Pi (need a running server/GUI, so they don't fit the sandbox), audiomentations (MIT, built for ML augmentation, not mixing).

### What each one gives us concretely

**pedalboard (adopt).** Built-in `HighpassFilter`, `LowpassFilter`, `PeakFilter`, `LowShelfFilter`, `Compressor(threshold_db, ratio, attack_ms, release_ms)`, `Reverb(room_size, damping, wet_level, dry_level, width)`, `Delay`, `Chorus`, `Limiter`, `Gain`, `Mix` (parallel chains), `PitchShift`. It releases the GIL and is fast: the whole 10 s demo, including sampler rendering, ran in **3.7–4.7 s wall**. A 75 s track's FX chain adds well under 5 s.
  - **Watch out:** there's **no sidechain input** on `Compressor`. Sidechain ducking stays a numpy gain curve keyed from kick times, which our `duck()` already does. Extend it to every kick (R3).
  - **Watch out:** JUCE `Limiter` makes up gain to 0 dBFS, so put `Gain(-1.5)` after it to get a ceiling.
  - Input layout is `(channels, samples)` float32. Our buffers are `(samples, 2)`, so transpose (`P()` helper in demo.py).
  - It replaces: the noise-IR reverb (gives HPF'd send + damping + width), `tanh` (gives glue comp + limiter), and adds per-bus EQ, which we have none of today.

**Euclid / swing (adopt idea).** `euclid(k,n,rot)`: pattern[i] = (i·k mod n) < k, then rotate. Rhythms worth using: (3,8) tresillo, (5,8) cinquillo, (3,16,rot 14) samba (all three from the Strudel docs), plus (5,16), (7,16) for shakers/congas. Strudel `swingBy(x, n)` delays the 2nd half of each of n slices by x·(half-slice); `swing` = 1/3. Our current fixed `0.02·BEAT` 16th push equals swingBy(0.08, 8). That's very light, which is fine for funk. Use 1/3 only for shuffle styles. Value for us: we can generate varied percussion layers per section from two integers instead of hand-written slot lists, and change the rotation in the build section to create motion without adding accents.

**Voice-leading (adopt, own code).** Pick the inversion of each chord (pitch classes) inside MIDI 55–74, span ≤ 12, that minimizes total semitone movement from the previous voicing. That's the closest-voicing rule Strudel's `voicing()` and the usual music21 recipes use. Cost: microseconds per chord. It removes the "parallel root-position block" sound of the `CH` dict.

**matchering (skip, but steal its targets).** It matches four things: RMS, frequency response, peak amplitude, stereo width. We can measure crest factor and side/mid (as in demo.py `stats()`) against a reference we like, without the dependency.

## 2. Rules to add to the music workflow (numbers)

R1. **No `tanh` on the full mix.** Master chain = LowShelf 80 Hz +1 dB → HPF 25 Hz → `Compressor(-14 dB, 2:1, 10 ms attack, 150 ms release)` aiming for 1–3 dB gain reduction → Gain to taste → `Limiter(-1.5 dB, 80 ms)` → `Gain(-1.5)`. Then ffmpeg loudnorm I=-15 TP=-1.5 as now.

R2. **Per-bus high-pass, so only kick and bass own the lows:** kick HPF 30 Hz, bass HPF 35 / LPF 5 kHz, perc HPF 150 Hz, chord/mid instruments (dulcimer, kalimba, piano comp) HPF 200 Hz, lead (sitar/flute) HPF 180 Hz, reverb send HPF 300 Hz + LPF 8 kHz.

R3. **Kick-keyed ducking on every kick, not just the 2 big hits:** bass and reverb return −6 dB, chords −3 dB (√ of the curve), lead and SFX 0 dB. Envelope: 5 ms attack, 30 ms hold, release ≈ ¼ beat (139 ms at 108 BPM; scale as 15/BPM s). The big-hit duck stays as is (depth 0.4, 0.9 s release).

R4. **Humanize scaled by beat position:** on-beat ±4 ms, off-beat ±8 ms; velocity ±8 %; off-beats ×0.85. Never humanize the kick on the 0 s hit or the reveal hit. Those stay sample-exact with the picture.

R5. **Chord strum spread 10–15 ms between voices, low to high**, plus voice-leading (range 55–74, span ≤ 12 semitones, minimal total movement). Pan chord voices −0.35 / 0 / +0.35.

R6. **Stereo:** kick, bass, sub and the reveal hit centred. Percussion pans within ±0.5, lead ±0.15, reverb width 1.0. Target side/mid of the final mix −20 to −15 dB. Current method measured −22.9 dB, new chain −18.0 dB. Use constant-power pan (cos/sin), not the linear attenuation in `add()`.

R7. **Lead bus compression** `Compressor(-18 dB, 3:1, 10 ms, 120 ms)` + presence `PeakFilter(2.5 kHz, +2 dB, Q 0.8)`. **Bass** `Compressor(-20 dB, 4:1, 5 ms, 80 ms)`.

R8. **One shared reverb send** `Reverb(room_size 0.55, damping 0.5, wet 1, dry 0)` at return ×0.35. Send levels: lead 0.25, chords 0.35, perc 0.08, bass/kick 0.

R9. **Keep the transients:** crest factor (peak − RMS) of the pre-loudnorm mix ≥ 10 dB. Demo: before 10.3 dB, after 11.4 dB at ~0.5 LU lower integrated loudness and the same peak. Under 9 dB means you're over-squashing.

R10. **Section contrast via arrangement, not level:** keep each section's short-term loudness within ±3 LU of the track average, except the 2.5 s post-hook stop and breakdowns (−6 LU allowed). Never drop below −30 LUFS short-term, so there are no silent gaps. Check with `ffmpeg -af ebur128` on 2 s windows.

R11. **Percussion layers from Euclid:** hi conga (5,16,rot 2), low conga (3,16,rot 3), shaker 16ths or (7,16). Change only the rotation (+1 step) when entering a build section. Accent/velocity +25 on the "and" of beats for shakers, as now.

## 3. Demo

- `/workspace/work/distill_music/demo.py`: run with `PYTHONPATH=/workspace/.pylib python3 demo.py` (about 4–6 s wall). Reuses samp.py (Sitar, Finger Bass, Dulcimer, GM drums) and the exostoma riff/bass/kick pattern at 108 BPM, D phrygian-dominant.
- `/workspace/work/distill_music/demo.wav`: 10.0 s A/B.
  - **0–4.9 s BEFORE:** the current method: hand-written congas, root-position chords, noise-IR reverb, `tanh` master.
  - **5.0–10 s AFTER:** Euclidean congas, voice-led strummed dulcimer, humanize R4, per-bus EQ R2, kick sidechain R3, pedalboard reverb send R8, glue comp + limiter R1.
  - The 0.1 s silence at 4.9 s only separates A from B. It isn't part of the technique.
- Measured: BEFORE −9.3 LUFS, peak −1.4 dBFS, crest 10.3 dB, side/mid −22.9 dB. AFTER −9.8 LUFS, peak −1.5 dBFS, crest 11.4 dB, side/mid −18.0 dB.
- `spec.png` is a spectrogram sanity check.
- Not verified: the result has been measured but nobody has listened to it, so judge B vs A by ear before adopting.

## Licensing note
pedalboard is GPL-3.0. Using it as a tool to render audio puts no licence on the output WAV/MP4. GPL only matters if we redistribute code that links it. Same for matchering and DawDreamer.
