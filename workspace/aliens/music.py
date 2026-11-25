# 《历史课没讲的一天》BGM — "Retro-sci-fi Hijaz groove in 7/4"
# D Phrygian-dominant (Hijaz: D Eb F# G A Bb C), 107.14 BPM, 7/4 grouped 4+3 (5 bars = 19.6 s -> 0.4 s & 20.0 s on bar lines),
# 16th swing 20%. Real-sample band (GeneralUser GS): Sitar lead + Oboe answer (call & response), Fretless Bass (+ Synth Bass 1 sub
# in the dino section), darbuka built from GM congas/rim + Brush kit swishes, 7/4 hand claps, Kalimba/Celeste sparkles, Whistle.
# SELF-MADE SAMPLES (numpy-synthesised, written to samples/*.wav, sliced by onset detection and played back chop-style on the grid):
#   alien_babble (FM "bi-bo-bu" syllables)  theremin (UFO glide phrase)  laser (FM zap)  stone (grind)  roar (synth dino)  shutter.
import sys, os, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import piano as _piano, gm as _gm, drum as _drum, SR
from cues import *
HERE = os.path.dirname(os.path.abspath(__file__))
LV = {"Sitar": 0.9, "Oboe": 1.0, "Fretless Bass": 1.0, "Synth Bass 1": 0.6, "Kalimba": 0.8, "Celeste": 1.0, "Whistle": 0.8,
      "Reverse Cymbal": 4.0, "Brass Section": 0.5, "Pizzicato Strings": 0.9}
DLV = {41: 0.17, 76: 0.2, 77: 0.2}
@functools.lru_cache(maxsize=None)
def gm(name, m, dur=0.5, vel=100, release=0.2): return _gm(name, m, dur, vel, release=release) * LV.get(name, 1.0)
@functools.lru_cache(maxsize=None)
def drum(n, vel=100, kit="Standard 1"): return _drum(n, vel, kit=kit) * DLV.get(n, 1.0)
@functools.lru_cache(maxsize=None)
def piano(m, dur=0.4, vel=60): return _piano(m, dur, vel) * 12
N = int(SR * DUR); MIX = np.zeros((N, 2)); VERB = np.zeros((N, 2)); ECHO = np.zeros((N, 2))
rng = np.random.default_rng(42)
def add(y, t0, g=1.0, pan=0.0, wet=0.0, echo=0.0, human=True):
    if y.ndim == 1: y = np.stack([y, y], 1)
    if human: g *= 1 + rng.uniform(-0.06, 0.06); t0 += rng.uniform(-0.003, 0.003)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    MIX[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet
    if echo: ECHO[i:i + len(y)] += y * echo
tt_ = lambda d: np.arange(int(d * SR)) / SR
S16 = BEAT / 4; SW = 0.2 * S16; NB = 28
def bar_of(t): return int(math.floor((t - G0) / BAR + 1e-6))
def ph(b): return b if b < 5 else b - 5
def sixteenths(t0, t1):
    out = []
    for b in range(max(-1, bar_of(t0) - 1), bar_of(t1) + 2):
        for k in range(NB):
            tt = G0 + b * BAR + k * S16
            if t0 - 1e-4 <= tt < t1 - 1e-4: out.append((tt + (SW if k % 2 else 0), k, b))
    return out
def lp(x, k): return np.convolve(x, np.ones(k) / k, "same")
def norm(y, p=0.8): return y / (np.abs(y).max() + 1e-9) * p

# ================= SELF-MADE SAMPLES =================
def mk_babble():
    """8 alien syllables: FM-voiced chirps with formant-ish ring mod, gaps between -> sliced later by onset detection."""
    out = []
    for i, (f0, f1, d) in enumerate([(520, 900, .14), (900, 380, .12), (300, 620, .16), (700, 700, .09), (1100, 500, .18), (420, 980, .13), (640, 300, .2), (860, 1300, .11)]):
        t = tt_(d); f = f0 * (f1 / f0) ** (t / d)
        ph_ = 2 * np.pi * np.cumsum(f) / SR
        y = np.sin(ph_ + 2.2 * np.sin(ph_ * 2.01)) * (0.6 + 0.4 * np.sin(2 * np.pi * 38 * t))
        y *= np.sin(np.pi * t / d) ** 0.6
        out += [y, np.zeros(int(0.07 * SR))]
    return norm(np.concatenate(out))
def mk_theremin():
    """UFO theremin phrase: sine + 2nd harmonic, wide vibrato, portamento between 5 notes (Hijaz)."""
    notes = [74, 78, 79, 75, 74]; d = 0.45; n = int(d * SR * len(notes)); t = np.arange(n) / SR
    m = np.repeat(notes, int(d * SR)).astype(float)[:n]
    m = lp(np.pad(m, (2000, 2000), mode="edge"), 4000)[2000:-2000]   # glide
    f = 440 * 2 ** ((m - 69) / 12) * 2 ** (0.35 * np.sin(2 * np.pi * 6.2 * t) / 12)
    p = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(p) + 0.25 * np.sin(2 * p) + 0.08 * np.sin(3 * p)
    env = np.ones(n); a = int(0.05 * SR); env[:a] = np.linspace(0, 1, a)
    for k in range(1, len(notes)): env[int(k * d * SR) - 600:int(k * d * SR) + 600] *= 0.35   # soft dips = slice points
    env[-a:] = np.linspace(1, 0, a)
    return norm(y * env)
def mk_laser():
    out = []
    for f0 in (3200, 2400, 4200):
        t = tt_(0.22); f = f0 * np.exp(-t * 14) + 180
        p = 2 * np.pi * np.cumsum(f) / SR
        out += [np.sin(p + 1.5 * np.sin(p * 0.5)) * np.exp(-t * 9), np.zeros(int(0.08 * SR))]
    return norm(np.concatenate(out))
def mk_stone():
    n = int(1.2 * SR); t = np.arange(n) / SR
    nz = rng.standard_normal(n); y = lp(nz, 30) * 8
    y *= (0.5 + 0.5 * (np.sin(2 * np.pi * 23 * t) > 0.2))          # crunchy grains
    y += np.sin(2 * np.pi * (55 + 6 * np.sin(2 * np.pi * 3 * t)) * t) * 0.4
    y *= np.minimum(1, t / 0.05) * np.minimum(1, (1.2 - t) / 0.2)
    return norm(y)
def mk_roar():
    n = int(1.1 * SR); t = np.arange(n) / SR
    f = 70 + 30 * np.sin(np.pi * t / 1.1) + 6 * np.sin(2 * np.pi * 9 * t)
    p = 2 * np.pi * np.cumsum(f) / SR
    saw = sum(np.sin(k * p) / k for k in range(1, 18))
    growl = lp(rng.standard_normal(n), 6) * (0.5 + 0.5 * np.sin(2 * np.pi * 31 * t))
    y = saw * (1 + 0.6 * growl)
    fm = lambda fc, bw: np.sin(2 * np.pi * fc * t) * np.exp(-0) # placeholder formant carrier
    y = y - lp(y, 3) * 0.5 + lp(y, 12)                              # crude formant tilt
    y *= np.minimum(1, t / 0.08) * np.minimum(1, (1.1 - t) / 0.35)
    return norm(y)
def mk_shutter():
    out = []
    for gg in (1.0, 0.6):
        t = tt_(0.05); out += [lp(rng.standard_normal(len(t)), 3) * np.exp(-t * 130) * gg, np.zeros(int(0.05 * SR))]
    return norm(np.concatenate(out))
def save_wav(path, y):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
class Sampler:
    """chop sampler: onset-detected slices of a self-made source, triggered with pitch shift / reverse."""
    def __init__(s, name, y, thresh=0.12, min_gap=0.05):
        os.makedirs(os.path.join(HERE, "samples"), exist_ok=True); save_wav(os.path.join(HERE, "samples", name + ".wav"), y)
        env = lp(np.abs(y), int(0.006 * SR)); env /= env.max()
        on = np.where((env[1:] >= thresh) & (env[:-1] < thresh))[0]; cuts = []
        for o in on:
            if not cuts or o - cuts[-1] > min_gap * SR: cuts.append(max(0, o - int(0.003 * SR)))
        if len(cuts) < 2: cuts = list(range(0, len(y), len(y) // 5))
        s.sl = [y[a:b] for a, b in zip(cuts, cuts[1:] + [len(y)])]
        fd = int(0.004 * SR)
        for z in s.sl: z[-fd:] *= np.linspace(1, 0, min(fd, len(z)))
        s.name = name
    def play(s, i, t0, semis=0.0, g=1.0, rev=False, pan=0.0, wet=0.0, echo=0.0, whole=False):
        y = np.concatenate(s.sl) if whole else s.sl[i % len(s.sl)]
        if rev: y = y[::-1]
        if semis:
            r = 2 ** (semis / 12); p = np.arange(0, len(y) - 1, r); ii = p.astype(int); y = y[ii] * (1 - (p - ii)) + y[ii + 1] * (p - ii)
        add(y * 0.5, t0, g, pan=pan, wet=wet, echo=echo)
BAB = Sampler("alien_babble", mk_babble()); THR = Sampler("theremin", mk_theremin(), 0.5, 0.25); LZR = Sampler("laser", mk_laser())
STO = Sampler("stone", mk_stone(), 0.3, 0.4); ROA = Sampler("roar", mk_roar(), 0.3, 0.5); SHU = Sampler("shutter", mk_shutter())

# ================= synth one-shots =================
def boom(t0, g=1.0, dur=1.1):
    t = tt_(dur); f = 36 + 80 * np.exp(-t * 16)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2) * 0.9, t0, g, human=False)
def thump(t0, g=1.0, f0=52):
    t = tt_(0.3); f = f0 + 40 * np.exp(-t * 30)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12) * 0.8, t0, g, human=False)
def whoosh(t0, d=0.35, g=1.0, f0=400):
    n = int(d * SR); t = np.arange(n) / SR; nz = rng.standard_normal(n); k = max(2, int(SR / f0 / 2))
    y = lp(nz - lp(nz, k), 3); add(y * np.sin(np.pi * t / d) ** 2 * 0.12, t0, g, human=False)
def popfx(t0, g=1.0, f0=1200, f1=300):
    t = tt_(0.09); f = f1 + (f0 - f1) * np.exp(-t * 60)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.32, t0, g, human=False)
def ding(t0, g=1.0, f=2637):
    t = tt_(1.0); y = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
    add(y * np.exp(-t * 4) * 0.15, t0, g, wet=0.6, echo=0.4, human=False)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T = t1 - t0
    y = lp(rng.standard_normal(n), 5) * (t / T) ** 2.5 * 0.07
    f = 180 * (1600 / 180) ** (t / T); y += np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / T) ** 2 * 0.04
    add(y, t0, g, human=False)
def rewind_squeal(t0, d, g=1.0):   # tape-rewind chatter
    n = int(d * SR); t = np.arange(n) / SR
    f = 600 + 2400 * (t / d) + 300 * np.sin(2 * np.pi * 13 * t)
    y = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.05 + lp(rng.standard_normal(n), 2) * 0.03
    add(y * np.sin(np.pi * t / d), t0, g, human=False)
def buzzer(t0, g=1.0):
    for j, f in enumerate((220, 165)):
        t = tt_(0.22); y = np.sign(np.sin(2 * np.pi * f * t)) * 0.12 * np.minimum(1, (0.22 - t) / 0.03)
        add(lp(y, 6), t0 + j * 0.24, g, human=False)
def scribble(t0, d, g=1.0):
    n = int(d * SR); t = np.arange(n) / SR; nz = rng.standard_normal(n)
    y = (nz - lp(nz, 4)) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 7 * t))) * 0.05
    add(y, t0, g, pan=0.15, human=False)
def rev_note(name, m, t_end, dur=0.6, g=1.0, vel=100):   # reversed sample, peaks right at t_end
    y = gm(name, m, dur, vel, 0.05)[::-1]; add(y, t_end - len(y) / SR, g, wet=0.3, human=False)

# ================= band parts (16th positions in a 7/4 bar: beats 0,4,8,12 | 16,20,24) =================
# Hijaz on D: D=62 Eb=63 F#=66 G=67 A=69 Bb=70 C=72 D=74
SIT_A = [(0, 74, 2), (2, 75, 1), (3, 74, 1), (4, 78, 2), (6, 79, 2), (8, 81, 3), (11, 79, 1), (12, 78, 2), (14, 75, 2), (16, 74, 3), (20, 69, 2), (22, 70, 2), (24, 74, 3)]
OBO_B = [(0, 81, 2), (2, 82, 2), (4, 81, 2), (6, 79, 2), (8, 78, 4), (12, 75, 2), (14, 78, 2), (16, 74, 4), (20, 70, 2), (22, 69, 2), (24, 66, 2), (26, 69, 2)]
BASS_A = [(0, 38, 3), (3, 38, 1), (6, 45, 2), (8, 39, 2), (10, 38, 2), (12, 42, 4), (16, 43, 3), (19, 42, 1), (20, 39, 2), (22, 38, 2), (24, 45, 2), (26, 39, 2)]
BASS_B = [(0, 34, 3), (3, 34, 1), (6, 38, 2), (8, 36, 4), (12, 33, 4), (16, 38, 3), (19, 38, 1), (20, 39, 2), (22, 42, 2), (24, 45, 2), (26, 42, 2)]
CHOP_A = [(6, 0, 0), (14, 3, 2), (22, 5, -2), (27, 1, 5)]           # (pos, babble slice, semitones)
CHOP_B = [(7, 2, 0), (13, 4, 3), (21, 6, -3), (25, 7, 0), (26, 7, 2)]
def darbuka(t0, t1, g=1.0, heavy=False, lite=False):
    for tt, k, b in sixteenths(t0, t1):
        A_ = ph(b) % 2 == 0
        doum = (0, 8, 16) if A_ else (0, 6, 16, 18)
        tek = (4, 10, 12, 20, 24, 26) if A_ else (4, 10, 12, 20, 24, 25, 26, 27)
        if lite: doum = (0, 16); tek = (4, 12, 20, 24)
        if k in doum:
            add(drum(36, 112 if k in (0, 16) else 92), tt, 0.7 * g); add(drum(64, 105), tt, 0.35 * g, pan=-0.15)
            if heavy: add(drum(41, 118), tt, 0.9 * g); add(drum(36, 127), tt, 0.4 * g)
        if k in tek: add(drum(63 if k in (4, 20) else 62, 110 if k in (4, 12, 20) else 85), tt, 0.38 * g, pan=0.2)
        if k in (6, 14, 22) and not lite: add(drum(37, 70), tt, 0.22 * g, pan=-0.25)
        if k in (12, 24): add(drum(38, 90, "Brush"), tt + 0.01, 0.45 * g, wet=0.15)
        if k % 2 == 0 and not lite: add(drum(42, 80 if k % 4 == 0 else 50, "Brush"), tt, 0.2 * g, pan=0.35)
        if k == 2 and ph(b) % 4 == 3 and not lite: add(drum(54, 70), tt, 0.25 * g, pan=0.4)
def bass(t0, t1, g=1.0, sub=False):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m, du in (BASS_A if ph(b) % 2 == 0 else BASS_B):
            if pos == k:
                add(gm("Fretless Bass", m, du * S16 * 0.92, 112 if pos in (0, 16) else 98, 0.06), tt, 0.95 * g)
                if sub: add(gm("Synth Bass 1", m - 12, du * S16 * 0.9, 110, 0.05), tt, 0.7 * g)
def lead(t0, t1, g=1.0, both=False, rev=False):
    for tt, k, b in sixteenths(t0, t1):
        A_ = ph(b) % 2 == 0
        if A_ or both:
            for pos, m, du in SIT_A:
                if pos == k:
                    if rev: rev_note("Sitar", m, tt + du * S16, du * S16 + 0.2, 0.55 * g)
                    else: add(gm("Sitar", m, du * S16 + 0.15, 108, 0.25), tt, 0.5 * g, pan=-0.15, wet=0.2, echo=0.25)
        if not A_ or both:
            for pos, m, du in OBO_B:
                if pos == k:
                    if rev: rev_note("Oboe", m - 12, tt + du * S16, du * S16 + 0.2, 0.5 * g)
                    else: add(gm("Oboe", m - 12, du * S16 * 0.95, 100, 0.12), tt, 0.42 * g, pan=0.18, wet=0.25)
def chops(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, i, sm in (CHOP_A if ph(b) % 2 == 0 else CHOP_B):
            if pos == k: BAB.play(i, tt, sm, 0.55 * g, pan=0.3 * (1 if k % 2 else -1), echo=0.15)
def claps(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k in (0, 8, 16, 24): add(drum(39, 112), tt, 0.5 * g, wet=0.25)
        elif k in (12, 20): add(drum(39, 70), tt, 0.25 * g, wet=0.25)
def heartbeat(t0, t1, g=1.0, fast_from=None):
    for tt, k, b in sixteenths(t0, t1):
        fast = fast_from is not None and tt >= fast_from
        if k in ((0, 4, 8, 12, 16, 20, 24) if fast else (0, 8, 16, 24)): thump(tt, 0.85 * g); thump(tt + 0.14, 0.45 * g, 60)
def groove(t0, t1, g=1.0, heavy=False, both=False, ch=True):
    darbuka(t0, t1, g, heavy); bass(t0, t1, g, sub=heavy); lead(t0, t1, g, both)
    if ch: chops(t0, t1, g)
def big(t0, g=1.0):
    boom(t0, 1.2 * g, 1.3); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 127), t0, 0.6 * g, wet=0.35); add(drum(57, 110), t0 + 0.01, 0.3 * g, pan=0.4)
    for m in (50, 57, 62, 66, 69): add(gm("Brass Section", m, 0.3, 124, 0.12), t0, 0.32 * g, wet=0.35)
    add(gm("Sitar", 74, 0.6, 127, 0.3), t0, 0.6 * g, wet=0.3); add(gm("Fretless Bass", 26, 0.7, 127, 0.15), t0, 1.1 * g)
    LZR.play(0, t0, -5, 0.9 * g, wet=0.2)
def kal(t0, m, g=1.0): add(gm("Kalimba", m, 0.4, 105, 0.3), t0, 0.5 * g, wet=0.3, echo=0.25)
def cel(t0, m, g=1.0): add(gm("Celeste", m, 0.5, 100, 0.4), t0, 0.35 * g, wet=0.4, echo=0.3)

# ================= arrangement =================
whoosh(0.02, 0.36, 1.2, 300); THR.play(0, 0.0, 0, 0.5)
big(HOOK_HIT)
groove(HOOK_HIT, REWIND, 1.0, ch=False)
# (tape stop 2.08 -> 2.36 applied after the mix; clock tick + rewind squeal fill the gap)
# --- rewind: reversed sounds ---
rewind_squeal(REWIND, LOOP_IN - REWIND + 0.3, 1.0)
add(gm("Reverse Cymbal", 60, 1.2, 110), POD - 1.2, 0.6)
darbuka(LOOP_IN, DATE, 0.7, lite=True); bass(LOOP_IN, DATE, 0.8); lead(LOOP_IN, DATE, 0.9, rev=True)
for j in range(4): BAB.play(j, LOOP_IN + j * BEAT * 0.5, 0, 0.35, rev=True, echo=0.2)
whoosh(POD - 0.1, 0.4, 1.0, 600); THR.play(4, POD - 0.05, 12, 0.35, rev=True)
thump(POD_LAND, 0.9, 70); add(drum(77, 100), POD_LAND, 0.4)
popfx(DOOR_OPEN, 0.8, 900, 200); whoosh(DOOR_OPEN, 0.25, 0.6, 1500)
for j, (i, sm) in enumerate(((0, 0), (1, 2), (5, 5))): BAB.play(i, STEP + j * S16 * 2, sm, 0.6)
for j, m in enumerate((74, 78, 81)): kal(HANDS + j * S16, m, 0.8)
# --- date / selfie / flag: full groove ---
groove(DATE, DINO)
for j, m in enumerate((81, 86)): cel(HEART1 + j * S16 * 2, m, 0.7)
SHU.play(0, SNAP, 0, 1.4); SHU.play(1, SNAP + 0.06, 0, 1.0); ding(SNAP2, 0.6, 3136)
thump(PLANT, 0.7, 80); add(drum(76, 100), PLANT, 0.4)
for j, (i, sm) in enumerate(((4, 0), (2, 3), (6, -2), (3, 5), (0, 2), (7, 0))): BAB.play(i, CLAIM + j * S16, sm, 0.7, echo=0.1)
# --- dinos: heavier low end ---
groove(DINO, PHARAOH, 1.0, heavy=True)
add(drum(41, 110), PEEK, 0.9); thump(PEEK, 0.6, 45)
ROA.play(0, ROAR, 0, 1.0, wet=0.3, whole=True); ROA.play(0, ROAR, -7, 0.5, whole=True)
THR.play(2, PTERO, 7, 0.4); whoosh(PTERO, 0.4, 1.0, 900); popfx(STEAL, 0.8, 1500, 500)
for j, m in enumerate((75, 74)): kal(WAIT + j * BEAT * 0.5, m, 0.8)
# --- standoff: drums out, only 7/4 claps + heartbeat ---
claps(PHARAOH, SIL0, 0.9); heartbeat(PHARAOH, SIL0, 0.9, fast_from=FLEET)
for tt, k, b in sixteenths(PHARAOH, SIL0):
    if k in (0, 16): add(gm("Fretless Bass", 38 if k == 0 else 39, 0.4, 105, 0.1), tt, 0.7)
thump(LAND, 0.8, 60); whoosh(PHARAOH, 0.3, 0.8, 500)
LZR.play(1, AIM, 5, 0.35); popfx(AIM, 0.5, 600, 1600)
for i, h in enumerate(GLARE): LZR.play(2, h, 3 * i, 0.25); add(gm("Oboe", [63, 66, 69][i], 0.25, 100, 0.1), h, 0.35, wet=0.3)
for i, h in enumerate(FLEET_HITS): THR.play(i, h - 0.1, -5 + 2 * i, 0.4, wet=0.4, echo=0.2)
riser(RISERS[0][0], SIL0, 1.1); add(gm("Reverse Cymbal", 60, 1.6, 110), SIL0 - 1.6, 0.8)
# --- 20.0 s big hit -> full band ---
big(BIG2, 1.1); STO.play(0, BIG2 + 0.02, 0, 0.6, whole=True)
groove(BIG2, STONE, 1.0, both=True)
add(drum(49, 100), FALL, 0.3, wet=0.3)
for i, h in enumerate(TRAILS): THR.play(i, h - 0.2, -8 - 3 * i, 0.35, rev=False, wet=0.3)
for j, m in enumerate((74, 75, 74)): kal(Q_HIT + j * S16 * 2, m, 0.8)
SHU.play(0, CLICK, 0, 1.4); SHU.play(1, CLICK + 0.06, 0, 1.0); popfx(FREEZE, 0.6, 1800, 900)
# --- stone pretends: lite + whistle ---
darbuka(STONE, EXAM, 0.6, lite=True); bass(STONE, EXAM, 0.8)
for j, (m, du) in enumerate(((74, 0.25), (79, 0.25), (78, 0.25), (75, 0.5), (74, 0.5))):
    add(gm("Whistle", m + 12, du * 0.9, 100, 0.1), WHISTLE + sum(x[1] for x in ((74, 0.25), (79, 0.25), (78, 0.25), (75, 0.5))[:j]), 0.35, wet=0.3)
for j in range(3): add(drum(76 + j % 2, 90), STARE + j * S16 * 2, 0.3)
STO.play(0, BUSTED, 0, 0.8, whole=True); add(drum(77, 110), BUSTED, 0.4)
# --- exam: lite groove, pencil, buzzer ---
darbuka(EXAM, OUTRO, 0.6, lite=True); bass(EXAM, OUTRO, 0.8); lead(EXAM, OUTRO, 0.6)
scribble(WRITE, REDX - 0.3 - WRITE, 1.0); buzzer(REDX, 1.0); popfx(REDX2, 0.7)
# --- outro: light final hit, soft ending ---
for m in (50, 62, 66, 69, 74): add(gm("Sitar", m, 1.2, 100, 0.6), FINAL, 0.3, wet=0.4)
for m in (62, 66, 69): add(gm("Oboe", m, 0.8, 90, 0.4), FINAL, 0.25, wet=0.4)
add(gm("Fretless Bass", 38, 1.4, 100, 0.4), FINAL, 0.7); add(drum(49, 60), FINAL, 0.18, wet=0.4); kal(FINAL, 86, 0.6)
darbuka(FINAL + BAR * 0.5, DUR - 1.0, 0.35, lite=True)
ding(WINK, 0.7, 3520); BAB.play(7, WINK + 0.3, 5, 0.4)
THR.play(4, DUR - 2.4, 0, 0.3, wet=0.5)

# ================= mix =================
def reverb(x, sec=1.6, dec=3.2):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = lp(rng.standard_normal(n) * np.exp(-t * dec), 8); ir /= np.abs(ir).sum() ** 0.5 * 10
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
def fx_bus():
    global MIX
    d = int(3 * S16 * SR)
    for r in range(1, 4):
        sh = ECHO[: N - d * r] * (0.4 ** r)
        if r % 2: MIX[d * r:, 0] += sh[:, 1] * 0.8; MIX[d * r:, 1] += sh[:, 0] * 0.3
        else: MIX[d * r:, 0] += sh[:, 1] * 0.3; MIX[d * r:, 1] += sh[:, 0] * 0.8
    MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
fx_bus()
# tape stop on the hook groove (2.08 -> 2.36)
i0, i1 = int(HOOK_STOP * SR), int(REWIND * SR); n = i1 - i0
rate = np.linspace(1, 0.02, n) ** 1.4; p = i0 + np.cumsum(rate); p = np.clip(p, 0, N - 2); ii = p.astype(int); ff = (p - ii)[:, None]
seg = MIX[ii] * (1 - ff) + MIX[ii + 1] * ff; seg *= np.linspace(1, 0.3, n)[:, None]
MIX[i0:i1] = seg
POST = MIX.copy(); MIX[:] = 0; VERB[:] = 0; ECHO[:] = 0
for j in range(4): add(drum(76 + j % 2, 100), CLOCK_IN + 0.02 + j * 0.07, 0.3, human=False)   # clock ticks during the stop
fx_bus(); MIX += POST
for a, b in SILENCES:
    i0, i1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.04 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] = 0
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.2); MIX /= np.abs(MIX).max() / 0.85
fo = int(0.8 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open(os.path.join(HERE, "bgm.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("slices:", {s.name: len(s.sl) for s in (BAB, THR, LZR, STO, ROA, SHU)})
print("silence max", np.abs(MIX[int((SIL0 + 0.05) * SR):int(BIG2 * SR)]).max(), "ok BPM %.2f bar %.3f" % (BPM, BAR))
