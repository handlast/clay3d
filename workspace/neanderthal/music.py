# 《7.5万年前的命案》BGM — "Stone-Age detective, 7/4 swing": D minor, 107.14 BPM, 7/4 (5 bars = 19.6 s, 0.4 s & 20.0 s on bar lines).
# Borrowed from the seahorse BGM: 16th swing 20%, laid-back snare, boom-bap loop, detective line-cliche bass, stop-times, hits only at 0.4/20.0.
# All samples replaced: Tine Electric Piano hook through a slow vibrato+chorus bus (Balatro-ish tipsy wobble), Fretless Bass line cliche,
# Xylophone = bone-clue notes, Clarinet = detective sigh, synth SFX layer: bone crack, magnifier ding, polaroid, ruler ticks,
# puzzle clicks, calendar flips, cave drips, drill rumble. No vinyl / vibraphone / muted trumpet.
# Drum loop grouped 4+3 per 7/4 bar: "K . S . | K K S" with a stumble (offbeat kick + ghost snares) on bar B; 2-bar loop, open hats every 4th bar.
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import piano as _piano, gm as _gm, drum as _drum, SR
from cues import *
# measured peaks @vel100: Tine EP 1.3-1.44, Fretless .79, Xylophone 4.37, Clarinet .78, Brass Section 1.47, Synth Brass 1 1.16, Celeste .56, hat42 1.27, woodblock 4.8
LV = {"Tine Electric Piano": 0.6, "Fretless Bass": 1.0, "Xylophone": 0.19, "Clarinet": 1.1, "Brass Section": 0.55, "Synth Brass 1": 0.7, "Celeste": 1.4, "Reverse Cymbal": 4.0}
DLV = {42: 0.6, 46: 0.9, 76: 0.17, 77: 0.17}
@functools.lru_cache(maxsize=None)
def gm(name, m, dur=0.5, vel=100, release=0.2, decay=None): return _gm(name, m, dur, vel, release=release, decay=decay) * LV.get(name, 1.0)
@functools.lru_cache(maxsize=None)
def drum(n, vel=100): return _drum(n, vel) * DLV.get(n, 1.0)
@functools.lru_cache(maxsize=None)
def piano(m, dur=0.4, vel=60): return _piano(m, dur, vel) * 12
N = int(SR * DUR); MIX = np.zeros((N, 2)); VERB = np.zeros((N, 2)); ECHO = np.zeros((N, 2)); EPB = np.zeros((N, 2))
rng = np.random.default_rng(23)
def add(y, t0, g=1.0, pan=0.0, wet=0.0, echo=0.0, human=True, bus=None):
    if human: g *= 1 + rng.uniform(-0.06, 0.06); t0 += rng.uniform(-0.003, 0.003)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    (MIX if bus is None else bus)[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet
    if echo: ECHO[i:i + len(y)] += y * echo
def mono(y): return np.stack([y, y], 1)
tt_ = lambda d: np.arange(int(d * SR)) / SR
S16 = BEAT / 4; SW = 0.2 * S16; LAY = 0.012   # 16th swing + laid-back snare
NB = 28                                        # 16ths per 7/4 bar
# ---------------- grid ----------------
def bar_of(t): return int(math.floor((t - G0) / BAR + 1e-6))
def ph(b): return b if b < 5 else b - 5      # restart the 2-/4-bar cycle on the 20.0 s downbeat
def sixteenths(t0, t1):
    out = []
    for b in range(max(0, bar_of(t0) - 1), bar_of(t1) + 2):
        for k in range(NB):
            tt = G0 + b * BAR + k * S16
            if t0 - 1e-4 <= tt < t1 - 1e-4: out.append((tt + (SW if k % 2 else 0), k, b))
    return out
# ---------------- synth one-shots ----------------
def boom(t0, g=1.0, dur=1.1):
    t = tt_(dur); f = 36 + 80 * np.exp(-t * 16)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2) * 0.9), t0, g, human=False)
def thump(t0, g=1.0, f0=52):
    t = tt_(0.3); f = f0 + 40 * np.exp(-t * 30)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12) * 0.8), t0, g, human=False)
def tick(t0, g=1.0, f=3200):
    t = tt_(0.04); y = np.sin(2 * np.pi * f * t) * np.exp(-t * 160) + rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.4
    add(mono(y * 0.35), t0, g, pan=0.2, human=False)
def click(t0, g=1.0):
    t = tt_(0.03); add(mono(rng.standard_normal(len(t)) * np.exp(-t * 300) * 0.5), t0, g, human=False)
def whoosh(t0, d=0.35, g=1.0, f0=400):
    n = int(d * SR); t = np.arange(n) / SR
    nz = rng.standard_normal(n); k = max(2, int(SR / f0 / 2))
    y = nz - np.convolve(nz, np.ones(k) / k, "same"); y = np.convolve(y, np.ones(3) / 3, "same")
    add(mono(y * np.sin(np.pi * t / d) ** 2 * 0.12), t0, g, human=False)
def popfx(t0, g=1.0, f0=1200, f1=300):
    t = tt_(0.09); f = f1 + (f0 - f1) * np.exp(-t * 60)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.32), t0, g, human=False)
def ding(t0, g=1.0, f=2637):   # magnifier glint
    t = tt_(1.2); y = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t * 3) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6))
    add(mono(y * np.exp(-t * 3.5) * np.minimum(1, t / 0.002) * 0.16), t0, g, wet=0.6, echo=0.4, human=False)
def crack(t0, g=1.0):          # bone crack: sharp bandpassed noise snap + tiny body
    t = tt_(0.12); nz = rng.standard_normal(len(t))
    hp = nz - np.convolve(nz, np.ones(6) / 6, "same")
    y = hp * np.exp(-t * 70) * 0.8 + np.sin(2 * np.pi * (900 * np.exp(-t * 20) + 300) * t) * np.exp(-t * 50) * 0.4
    add(mono(y * 0.6), t0, g, wet=0.2, human=False)
    t2 = tt_(0.05); add(mono(rng.standard_normal(len(t2)) * np.exp(-t2 * 200) * 0.25), t0 + 0.035, g, human=False)
def drip(t0, g=1.0, f=900):    # cave water drop
    t = tt_(0.25); fr = f * (1 + 1.2 * (1 - np.exp(-t * 40)))
    add(mono(np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 28) * 0.22), t0, g, pan=rng.uniform(-0.5, 0.5), wet=0.9, echo=0.3, human=False)
def rumble(t0, t1, g=1.0):     # drill / digging rumble with chug
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T = t1 - t0
    y = np.convolve(rng.standard_normal(n), np.ones(40) / 40, "same") * 6
    y *= (0.55 + 0.45 * np.sin(2 * np.pi * 18 * t) ** 2) * np.minimum(1, t / 0.05) * np.minimum(1, (T - t) / 0.15)
    add(mono(y * 0.12), t0, g, human=False)
def shutter(t0, g=1.0):        # polaroid: click + motor whirr
    for dt, gg in ((0, 1.0), (0.06, 0.7)):
        t = tt_(0.05); y = np.convolve(rng.standard_normal(len(t)), np.ones(4) / 4, "same") * np.exp(-t * 120)
        add(mono(y * 0.9), t0 + dt, g * gg, human=False)
    t = tt_(0.45); y = np.sign(np.sin(2 * np.pi * 140 * t)) * 0.3 + np.convolve(rng.standard_normal(len(t)), np.ones(3) / 3, "same") * 0.2
    add(mono(y * np.sin(np.pi * t / 0.45) * 0.08), t0 + 0.12, g, pan=0.2, human=False)
def flip(t0, g=1.0):           # calendar page
    t = tt_(0.09); nz = rng.standard_normal(len(t)); y = nz - np.convolve(nz, np.ones(10) / 10, "same")
    add(mono(y * np.sin(np.pi * t / 0.09) ** 2 * 0.22), t0, g, pan=rng.uniform(-0.3, 0.3), human=False)
def pour(t0, d=0.8, g=1.0):    # soaking plants: soft water + bubbles
    n = int(d * SR); t = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(12) / 12, "same") * np.sin(np.pi * t / d) * 0.25
    add(mono(y), t0, g, wet=0.3, human=False)
    for j in range(6): popfx(t0 + 0.1 + j * d / 7, 0.25 * g, 1500 + 200 * j, 600)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T = t1 - t0
    y = np.convolve(rng.standard_normal(n), np.ones(5) / 5, "same") * (t / T) ** 2.5 * 0.07
    f = 180 * (1600 / 180) ** (t / T); y += np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / T) ** 2 * 0.04
    add(mono(y), t0, g, human=False)
def glide_note(name, m, dur, semis, gl, vel=105):
    y = gm(name, m, dur + 0.3, vel, 0.08)
    n = len(y); t = np.arange(n) / SR
    rate = 2 ** (-semis * np.clip(1 - t / gl, 0, 1) / 12)
    p = np.cumsum(rate); p = p[p < n - 1]; i = p.astype(int); f = (p - i)[:, None]
    return y[i] * (1 - f) + y[i + 1] * f
# ---------------- parts (16th positions 0..27 in a 7/4 bar; beats at 0,4,8,12 | 16,20,24) ----------------
DM9 = (53, 57, 60, 64); B_HD = (53, 57, 59, 62); BBMAJ = (53, 57, 58, 62); A7B9 = (52, 55, 58, 61)
COMP_A = [(0, DM9), (10, DM9), (18, B_HD)]
COMP_B = [(0, BBMAJ), (8, A7B9), (16, DM9), (22, A7B9)]
# line cliche down: D D A | C# . C | B B Bb A   //   Bb Bb F | A . E C# | D D A F (glide A->D every 2 bars)
BASS_A = [(0, 38, 3), (3, 38, 1), (6, 45, 2), (8, 37, 3), (11, 37, 1), (12, 36, 4), (16, 35, 3), (19, 35, 1), (20, 34, 4), (24, 33, 4)]
BASS_B = [(0, 34, 3), (3, 34, 1), (6, 41, 2), (8, 33, 3), (11, 33, 1), (12, 40, 2), (14, 37, 2), (16, 38, 3), (19, 38, 1), (20, 45, 2), (22, 41, 2), (24, 40, 2), (26, 37, 2)]
HOOK_A = [(0, 74, 2), (2, 77, 2), (4, 76, 1), (5, 74, 3), (8, 69, 4), (14, 72, 2), (16, 74, 2), (18, 76, 2), (20, 77, 3), (24, 76, 2), (26, 73, 2)]
HOOK_B = [(0, 74, 3), (3, 70, 1), (4, 69, 4), (10, 65, 2), (12, 64, 4), (16, 69, 2), (18, 72, 1), (19, 74, 1), (20, 77, 2), (22, 76, 6)]
SIGH = [(16, 77, 2), (18, 76, 2), (20, 74, 2), (22, 73, 6)]
def drums(t0, t1, style="loop", g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        A_ = ph(b) % 2 == 0; opn = ph(b) % 4 == 3
        if style in ("loop", "lite"):
            kick = (0, 7, 10, 16, 20) if A_ else (0, 3, 10, 15, 16, 19)
            if style == "lite": kick = (0, 16)
            if k in kick: add(drum(36, 115 if k in (0, 16) else 96), tt, (0.85 if style == "loop" else 0.55) * g)
            if k in (4, 12, 24): add(drum(38, 112 if k != 24 else 118), tt + LAY, (0.62 if style == "loop" else 0.4) * g, wet=0.18)
            if style == "loop":
                if (k == 14 and A_) or (k in (7, 26, 27) and not A_): add(drum(38, 45), tt + LAY, 0.16 * g)   # ghosts = the stumble
                if k == 22 and A_: add(drum(37, 85), tt, 0.3 * g, pan=-0.2)
            if k % 2 == 0:
                if opn and k in (2, 6, 10, 14, 18, 22, 26): add(drum(46, 80), tt, 0.22 * g, pan=0.3)
                else: add(drum(42, 92 if k % 4 == 0 else 62), tt, 0.25 * g, pan=0.3)
            elif style == "loop" and k == 27 and A_: add(drum(42, 50), tt, 0.16 * g, pan=0.3)
        elif style == "hats":
            if k % 2 == 0: add(drum(42, 80 if k % 4 == 0 else 55), tt, 0.22 * g, pan=0.3)
            if k in (4, 12, 24): add(drum(37, 80), tt, 0.25 * g)
def bass(t0, t1, g=1.0, glide=True):
    for tt, k, b in sixteenths(t0, t1):
        A_ = ph(b) % 2 == 0; pat = BASS_A if A_ else BASS_B
        if glide and not A_ and k >= 24:
            if k == 24: add(glide_note("Fretless Bass", 38, S16 * 4, 5, S16 * 3.2), tt, 0.95 * g)
            continue
        for pos, m, du in pat:
            if pos == k: add(gm("Fretless Bass", m, du * S16 * 0.92, 112 if pos in (0, 16) else 98, 0.06), tt, 0.95 * g)
def keys(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m, du in (HOOK_A if ph(b) % 2 == 0 else HOOK_B):
            if pos == k: add(gm("Tine Electric Piano", m, du * S16 + 0.12, 100, 0.3), tt, 0.42 * g, pan=-0.12, wet=0.22, echo=0.35, bus=EPB)
def comp(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, ch in (COMP_A if ph(b) % 2 == 0 else COMP_B):
            if pos == k:
                for m in ch: add(gm("Tine Electric Piano", m - 12, 0.24, 72, 0.12), tt, 0.16 * g, pan=0.12, wet=0.15, bus=EPB)
def sigh(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if ph(b) % 4 != 3: continue
        for pos, m, du in SIGH:
            if pos == k: add(gm("Clarinet", m, du * S16 * 0.95, 96, 0.15), tt, 0.3 * g, pan=0.25, wet=0.35, echo=0.2)
def groove(t0, t1, g=1.0, drums_=True, kp=True, sg=True, cp=True):
    if drums_: drums(t0, t1, "loop", g)
    bass(t0, t1, g)
    if kp: keys(t0, t1, g)
    if sg: sigh(t0, t1, g)
    if cp: comp(t0, t1, g)
def big(t0, g=1.0):
    boom(t0, 1.2 * g, 1.3); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 127), t0, 0.65 * g, wet=0.35); add(drum(57, 110), t0 + 0.01, 0.35 * g, pan=0.4)
    add(drum(38, 127), t0, 0.5 * g, wet=0.3)
    for m in (50, 57, 62, 65, 69): add(gm("Brass Section", m, 0.3, 124, 0.12), t0, 0.32 * g, wet=0.35)
    for m in (62, 69, 74): add(gm("Synth Brass 1", m, 0.25, 120, 0.1), t0, 0.35 * g, wet=0.2)
    add(gm("Fretless Bass", 26, 0.7, 127, 0.15), t0, 1.1 * g)
    crack(t0, 0.9 * g)
def xy(t0, m, g=1.0, du=0.3): add(gm("Xylophone", m, du, 105, 0.2), t0, 0.5 * g, wet=0.25)
def cel(t0, m, g=1.0, du=0.5): add(gm("Celeste", m, du, 100, 0.4), t0, 0.4 * g, wet=0.4, echo=0.3)
def clar(t0, m, du, g=1.0): add(gm("Clarinet", m, du, 96, 0.2), t0, 0.32 * g, wet=0.4, echo=0.2)

# ---------------- arrangement ----------------
whoosh(0.02, 0.36, 1.2, 300); add(drum(38, 70), HOOK_HIT - 2 * S16, 0.3); add(drum(38, 90), HOOK_HIT - S16, 0.4)
big(HOOK_HIT)
groove(HOOK_HIT, CAVE, 1.0, sg=False)
whoosh(ZOOM[0], ZOOM[1] - ZOOM[0], 0.9, 200)
# (tape stop 2.08 -> 2.36 applied after the mix; ding + drill fill the gap until the loop re-enters at 2.64)
groove(LOOP_IN, STOP1[0])
drums_fill = [add(drum(37, 90), LOOP_IN - S16 * j, 0.25) for j in (1, 2)]
crack(FOUND, 0.6); xy(FOUND, 62)
click(LAMP, 1.2); thump(LAMP, 0.3, 120)
for j, m in enumerate([74, 77, 81, 86]): cel(GLOW + j * S16, m, 0.6, 0.3)
popfx(SCAP_TAG, 0.6)
shutter(PHOTO, 1.0)
for i, h in enumerate(FIELDS):
    for j in range(3): click(h + j * 0.045, 0.7)
    xy(h, [69, 72, 74, 77][i], 0.7)
popfx(NEAN_TAG, 0.6)
for i, h in enumerate(CHECKS): add(drum(76 + i % 2, 100), h, 0.5); xy(h, [74, 77, 81][i], 0.6)
ding(LENS, 1.0)
whoosh(RULER - 0.25, 0.3, 0.9)
for h in TICKS: tick(h, 0.9, 3600)
xy(MM15, 86, 0.9); popfx(MM15, 0.8)
for t_ in (CAVE + 0.4, THIN + 0.9, PROFILE - 0.3): drip(t_, 0.8, 800 + rng.uniform(0, 400))
# stop-time 1: drums drop, fretless holds, clarinet "hm?"
add(gm("Fretless Bass", 38, 0.6, 110, 0.1), STOP1[0], 0.9)
clar(STOP1[0] + BEAT * 0.5, 69, 0.3); clar(STOP1[0] + BEAT, 74, 0.45)
# suspects: heartbeat kick + clock + riser only (+ spotlight clunks)
for tt, k, b in sixteenths(SUSP, SIL0):
    if k % 2 == 0: tick(tt, 0.55 if k % 4 == 0 else 0.3, 3200 if k % 4 == 0 else 2500)
    fast = tt >= SPOTS[2] - 1e-3
    if k in ((0, 4, 8, 12, 16, 20, 24) if fast else (0, 8, 16, 24)): thump(tt, 0.85); thump(tt + 0.13, 0.45, 60)
for i, h in enumerate(SPOTS): click(h, 1.2); thump(h, 0.4, 90); xy(h, [57, 60, 63, 66][i], 0.6)
for j, m in enumerate([72, 70, 69]): clar(SCRATCH + j * BEAT * 0.5, m, 0.25, 0.9)
for j in range(4): add(drum(77, 70), SCRATCH + 0.05 + j * 0.09, 0.25)
riser(RISERS[0][0], SIL0, 1.1)
add(gm("Reverse Cymbal", 60, 1.6, 110), SIL0 - 1.6, 0.8)
# 20.0 second big hit -> full band
big(BIG2, 1.1)
groove(BIG2, STOP2[0])
crack(STONE, 0.6); xy(STONE, 61, 0.7); xy(STONE + 0.06, 67, 0.5)
popfx(WOODH, 0.9, 900, 250); xy(WOODH, 74, 0.7)
ding(MATCH, 0.9); xy(MATCH, 81, 0.6); popfx(TEST_TAG, 0.5)
whoosh(ZOOMB - 0.3, 0.35, 1.0); popfx(EXIT_TAG, 0.6)
whoosh(PATH2, 0.5, 0.9, 500); xy(ARROW2, 69, 0.6); xy(ARROW2 + S16, 74, 0.5)
for i, h in enumerate(PIECES): add(drum(76 + i % 2, 105), h, 0.55); click(h + 0.03, 0.8); xy(h, [74, 76, 77, 81][i], 0.55)
for j, m in enumerate([86, 81, 77, 74, 69, 65]): xy(DOWN + j * S16 * 0.5, m, 0.45, 0.15)
popfx(RIDGE_TAG, 0.5)
for j in range(8): tick(DASH[0] + j * (DASH[1] - DASH[0]) / 8, 0.5, 2800)
for dt in (0, 0.18): thump(HEART + dt, 0.9 if dt == 0 else 0.55, 58)
for dt in (0, 0.18): thump(AIM + dt + BEAT, 0.6 if dt == 0 else 0.35, 58)
popfx(MAYBE, 0.4)
# stop-time 2 (before the twist): heartbeat + one clarinet note
add(gm("Fretless Bass", 33, 0.5, 105, 0.1), STOP2[0], 0.8)
thump(STOP2[0] + BEAT * 0.5, 0.7, 58); thump(STOP2[0] + BEAT * 0.5 + 0.18, 0.4, 58)
clar(STOP2[0] + BEAT * 0.5, 73, 0.35, 0.8)
# twist + care: drums out, only Rhodes + fretless (softer), gentle SFX
bass(TWIST, CARD, 0.8); keys(TWIST, CARD, 0.75); comp(TWIST, CARD, 0.8)
crack(CRACK, 0.5); add(drum(77, 90), CRACK, 0.3); popfx(TILT, 0.5, 700, 300)
for j in range(6): click(CALC + 0.1 + j * 0.12, 0.35); cel(CALC + 0.1 + j * 0.12, [69, 72, 74, 76, 77, 81][j], 0.25, 0.2)
for h in FLIPS: flip(h, 0.9)
xy(YEAR, 81, 0.6); cel(YEAR, 86, 0.6, 0.6)
pour(BOWL, 0.9, 1.0); popfx(HAND, 0.5)
for j, m in enumerate([77, 81, 86]): cel(HEARTS + j * S16 * 2, m, 0.6, 0.5)
popfx(SOFT_TAG, 0.4)
# card: groove comes back (lite)
drums(CARD, OUTRO, "lite", 0.7); bass(CARD, OUTRO, 0.85); keys(CARD, OUTRO, 0.75); comp(CARD, OUTRO, 0.8)
popfx(CARD, 0.6); cel(CARD, 81, 0.6, 0.4)
for i, h in enumerate(CHIPS): xy(h, [74, 77, 81][i], 0.55); popfx(h, 0.4)
# outro: quiet, minor chord, cave drips
bass(OUTRO, FINAL, 0.8, glide=False); keys(OUTRO, FINAL, 0.6)
thump(STONE_UP, 0.4, 70)
for m in (38, 50, 57, 62, 65, 69, 76): add(piano(m, 1.8, 66), FINAL, 0.15, wet=0.45)
for m in (65, 69, 72, 76): add(gm("Tine Electric Piano", m, 1.6, 80, 0.6), FINAL, 0.2, wet=0.4, bus=EPB)
add(gm("Fretless Bass", 38, 1.4, 100, 0.4), FINAL, 0.6); add(drum(49, 55), FINAL, 0.14, wet=0.4)
popfx(BUB, 0.5)
for t_ in (OUTRO + 0.3, FINAL + 0.7, FINAL + 1.3): drip(t_, 0.7, 700 + rng.uniform(0, 300))

# ---------------- mix ----------------
def reverb(x, sec=1.8, dec=3.0):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * dec); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
def moddelay(x, base, depth, rate, phase=0.0):
    t = np.arange(len(x)) / SR
    p = np.arange(len(x)) - (base + depth * np.sin(2 * np.pi * rate * t + phase)) * SR
    p = np.clip(p, 0, len(x) - 2); i = p.astype(int); f = p - i
    return x[i] * (1 - f) + x[i + 1] * f
# Rhodes bus: gentle vibrato (~10 cents @1.1 Hz) + slow chorus copies L/R (~15 cents @0.55 Hz) = the tipsy sway
ep = np.stack([moddelay(EPB[:, c], 0.0008, 0.0008, 1.1) for c in (0, 1)], 1)
ch = np.stack([moddelay(EPB[:, 0], 0.012, 0.0025, 0.55), moddelay(EPB[:, 1], 0.014, 0.0025, 0.55, math.pi)], 1)
MIX += ep * 0.8 + ch * 0.38
# echo: dotted-8th ping-pong, 3 repeats
d = int(3 * S16 * SR)
for r in range(1, 4):
    sh = ECHO[: N - d * r] * (0.42 ** r)
    if r % 2: MIX[d * r:, 0] += sh[:, 1] * 0.8; MIX[d * r:, 1] += sh[:, 0] * 0.3
    else: MIX[d * r:, 0] += sh[:, 1] * 0.3; MIX[d * r:, 1] += sh[:, 0] * 0.8
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
# tape stop on the hook groove (2.08 -> 2.36 s); the gap to 2.64 is filled by ding + drill (added after)
ts0, ts1 = HOOK_STOP, CAVE
i0, i1 = int(ts0 * SR), int(ts1 * SR); n = i1 - i0
rate = np.linspace(1, 0.02, n) ** 1.4; p = i0 + np.cumsum(rate); p = np.clip(p, 0, N - 2); ii = p.astype(int); ff = (p - ii)[:, None]
seg = MIX[ii] * (1 - ff) + MIX[ii + 1] * ff; seg *= np.linspace(1, 0.3, n)[:, None]
MIX[i0:i1] = seg; j1 = int(LOOP_IN * SR) - 200; MIX[i1:j1] *= 0.15
POST = MIX.copy(); MIX[:] = 0; VERB[:] = 0; ECHO[:] = 0
ding(LENS_IN + 0.04, 1.2, 3136); rumble(CAVE, DIG[1], 1.0); click(CAVE, 1.0)
add(gm("Fretless Bass", 33, 0.2, 100, 0.05), LOOP_IN - 2 * S16, 0.8, human=False)
d2 = int(3 * S16 * SR)
for r in range(1, 3): MIX[d2 * r:] += ECHO[: N - d2 * r] * (0.4 ** r)
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
MIX += POST
for a, b in SILENCES:
    i0, i1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.04 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] = 0
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.2); MIX /= np.abs(MIX).max() / 0.85
fo = int(0.8 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("/workspace/work/neanderthal/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
pk = [20 * np.log10(np.sqrt((MIX[int(i * SR / 4):int((i + 1) * SR / 4)] ** 2).mean()) + 1e-9) for i in range(int(DUR * 4))]
print("loudest 0.25s:", sorted([(round(v, 1), i / 4) for i, v in enumerate(pk)])[-6:])
print("ok BPM %.2f  bar %.3fs" % (BPM, BAR))
