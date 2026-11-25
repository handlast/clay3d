# 《吼猴新种》BGM — "Amazon Roar Samba": G mixolydian, 120 BPM 4/4, 16% swing; Nylon guitar partido-alto comp + Finger Bass surdo line,
# Flute/Marimba hook, agogo + maracas + congas + cuíca, synthesized howler roars. ADAPTIVE: every time comes from cues.py.
# BIG1 = 0.0 s (the roar) and BIG2 ("会！…2 个新物种") are the ONLY two big hits; light sounds everywhere else.
# Bars run from G0 = 0 s; at BIG2 the bar origin is reset (org()).
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import gm as _gm, drum as _drum, SR
from cues import *
@functools.lru_cache(maxsize=None)
def _peak(name): return np.abs(_gm(name, 64, 0.5, 100, release=0.2)).max() + 1e-6
@functools.lru_cache(maxsize=None)
def gm(name, m, dur=0.5, vel=100, release=0.2): return _gm(name, m, dur, vel, release=release) * (0.5 / _peak(name))
@functools.lru_cache(maxsize=None)
def _dpk(n): return np.abs(_drum(n, 100)).max() + 1e-6
@functools.lru_cache(maxsize=None)
def drum(n, vel=100): return _drum(n, vel) * (0.6 / _dpk(n))
N = int(SR * DUR); MIX = np.zeros((N, 2)); VERB = np.zeros((N, 2)); ECHO = np.zeros((N, 2))
rng = np.random.default_rng(23)
def add(y, t0, g=1.0, pan=0.0, wet=0.0, echo=0.0, human=True):
    if human: g *= 1 + rng.uniform(-0.06, 0.06); t0 += rng.uniform(-0.003, 0.003)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    MIX[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet
    if echo: ECHO[i:i + len(y)] += y * echo
def mono(y): return np.stack([y, y], 1)
tt_ = lambda d: np.arange(int(d * SR)) / SR
S16 = BEAT / 4; SW = 0.16 * S16
ORG = [G0]
def org(t): ORG.append(t)
def origin(t): return max(o for o in ORG if o <= t + 1e-6) if t >= ORG[0] else ORG[0]
def sixteenths(t0, t1):
    out = []
    o = origin(t0); b0 = int(math.floor((t0 - o) / BAR)) - 1
    for b in range(max(-2, b0), b0 + 200):
        s0 = o + b * BAR
        if s0 > t1 + 0.1: break
        for k in range(16):
            tt = s0 + k * S16
            if t0 - 1e-4 <= tt < t1 - 1e-4 and origin(tt) == o: out.append((tt + (SW if k % 2 else 0), k, b))
    return out
# ---------------- SFX ----------------
def boom(t0, g=1.0, dur=1.1):
    t = tt_(dur); f = 38 + 80 * np.exp(-t * 16)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2) * 0.9), t0, g, human=False)
def tick(t0, g=1.0, f=3200):
    t = tt_(0.04); y = np.sin(2 * np.pi * f * t) * np.exp(-t * 160) + rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.4
    add(mono(y * 0.35), t0, g, pan=0.2, human=False)
def whoosh(t0, d=0.35, g=1.0, f0=400):
    n = int(d * SR); t = np.arange(n) / SR; nz = rng.standard_normal(n); k = max(2, int(SR / f0 / 2))
    y = nz - np.convolve(nz, np.ones(k) / k, "same"); y = np.convolve(y, np.ones(3) / 3, "same")
    add(mono(y * np.sin(np.pi * t / d) ** 2 * 0.12), t0, g, human=False)
def popfx(t0, g=1.0, f0=1200, f1=300):
    t = tt_(0.09); f = f1 + (f0 - f1) * np.exp(-t * 60)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.32), t0, g, human=False)
def ding(t0, g=1.0, f=2637):
    t = tt_(1.2); y = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t * 3) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6))
    add(mono(y * np.exp(-t * 3.5) * np.minimum(1, t / 0.002) * 0.16), t0, g, wet=0.6, echo=0.4, human=False)
def boing(t0, g=1.0, d=0.6, f0=180, depth=0.5, hz=11):
    t = tt_(d); f = f0 * (1 + depth * np.sin(2 * np.pi * hz * t) * np.exp(-t * 3)) * (1 + 0.6 * t)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    add(mono(y * np.exp(-t * 4) * np.minimum(1, t / 0.005) * 0.22), t0, g, wet=0.15, human=False)
def slide(t0, f0, f1, d=0.4, g=1.0):
    t = tt_(d); f = f0 * (f1 / f0) ** (t / d) * (1 + 0.01 * np.sin(2 * np.pi * 6 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.2 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    add(mono(y * np.sin(np.pi * t / d) ** 0.5 * 0.12), t0, g, wet=0.3, human=False)
def chirp(t0, g=1.0):
    for j in range(3):
        t = tt_(0.08); f = 3000 + 1500 * np.sin(np.pi * t / 0.08) + j * 200
        add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.08) * 0.12), t0 + j * 0.1, g, pan=-0.3, wet=0.2, human=False)
def buzz(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    ph = np.cumsum(220 * (1 + 0.04 * np.sin(2 * np.pi * 9 * t))) / SR
    y = (2 * (ph % 1) - 1) * (0.6 + 0.4 * np.sin(2 * np.pi * 31 * t)) * np.minimum(1, t / 0.05) * np.minimum(1, (t[-1] - t) / 0.05)
    add(mono(y * 0.03), t0, g, pan=0.4, human=False)
def snap(t0, g=1.0):
    add(drum(39, 110), t0, 0.6 * g); popfx(t0, 0.8 * g, 2000, 400)
def bloop(t0, g=1.0, f0=300, f1=900, d=0.18):
    t = tt_(d); f = f0 * (f1 / f0) ** (t / d)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) * 0.3), t0, g, wet=0.3, human=False)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T_ = t1 - t0
    y = np.convolve(rng.standard_normal(n), np.ones(5) / 5, "same") * (t / T_) ** 2.5 * 0.07
    f = 180 * (1600 / 180) ** (t / T_); y += np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / T_) ** 2 * 0.04
    add(mono(y), t0, g, human=False)
def rattle(t0, d, g=1.0):
    for j in range(int(d * 22)):
        tt = t0 + rng.uniform(0, d); L = tt_(0.03)
        y = np.sin(2 * np.pi * rng.uniform(1500, 3200) * L) * np.exp(-L * 180) * 0.25 + rng.standard_normal(len(L)) * np.exp(-L * 300) * 0.2
        add(mono(y), tt, g * rng.uniform(0.4, 1), pan=rng.uniform(-0.3, 0.3), human=False)
def clock(t0, t1, g=1.0):
    for j, tt in enumerate(np.arange(t0, t1 - 1e-6, BEAT)):
        add(drum(76 if j % 2 == 0 else 77, 100), tt, 0.35 * g, pan=0.25 if j % 2 else -0.25)

import random as _random
_TILES = [(c, r) for r in range(5) for c in range(6)]
_rr = _random.Random(5); _L = {tl: _rr.uniform(0, 1) for tl in _TILES}
for _k in ((1, 2), (2, 2), (4, 2), (4, 1)): _L[_k] = 9
LOSS_T = [(k, T["danger"] + 0.4 + v * 2.2) for k, v in _L.items() if v < 9]

def plink(t0, g=1.0):
    f = rng.uniform(1800, 3400); t = tt_(0.12)
    add(mono(np.sin(2 * np.pi * f * t * (1 - 0.3 * t)) * np.exp(-t * 45) * 0.12), t0, g, pan=rng.uniform(-0.6, 0.6), wet=0.4, human=False)
def hum(t0, t1, g=1.0, f=110):
    t = tt_(t1 - t0); y = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * t))
    y *= np.minimum(1, t / 0.2) * np.minimum(1, (t[-1] - t) / 0.2)
    add(mono(y * 0.03), t0, g, human=False)
def beep(t0, g=1.0, f=1760): t = tt_(0.09); add(mono(np.sin(2 * np.pi * f * t) * np.minimum(1, (0.09 - t) / 0.02) * 0.1), t0, g, pan=0.3, human=False)
def roll(t0, t1, g=1.0):
    n = int((t1 - t0) / 0.0625)
    for j in range(n): add(drum(38, 60 + int(50 * j / max(1, n))), t0 + j * 0.0625, (0.12 + 0.3 * j / max(1, n)) * g, wet=0.15)
# ---------------- music parts (A dorian, rainy frog funk) ----------------
PROG = ["Am7", "D9", "Am7", "G6"]
CH = {"Am7": (57, 60, 64, 67), "D9": (54, 57, 60, 64), "G6": (55, 59, 62, 64)}
ROOT = {"Am7": 45, "D9": 38, "G6": 43}
# ---------------- howler-specific SFX ----------------
def roar(t0, d=1.6, g=1.0, f=95, pan=0.0):
    """synth howler roar: growly saw + noise through a moving formant, slow swell, deep."""
    t = tt_(d); env = np.minimum(1, t / 0.12) * np.minimum(1, (d - t) / 0.35) * (0.8 + 0.2 * np.sin(2 * np.pi * 5.5 * t))
    ff = f * (1 + 0.18 * np.sin(np.pi * t / d)) * (1 + 0.02 * np.sin(2 * np.pi * 23 * t))
    ph = np.cumsum(ff) / SR; saw = 2 * (ph % 1) - 1
    nz = rng.standard_normal(len(t)); nz = np.convolve(nz, np.ones(12) / 12, "same")
    y = saw * 0.7 + nz * 0.5 * (0.5 + 0.5 * np.sin(2 * np.pi * ff * t))
    fc = 500 + 300 * np.sin(np.pi * t / d)
    out = np.zeros_like(y); a_ = 0.0
    k = np.exp(-2 * np.pi * fc / SR)
    for i in range(len(y)): a_ = (1 - k[i]) * y[i] + k[i] * a_; out[i] = a_
    out += 0.25 * np.sin(2 * np.pi * np.cumsum(ff * 0.5) / SR)
    add(mono(out * env * 0.5), t0, g, pan=pan, wet=0.35, human=False)
def cuica(t0, g=1.0, up=True):
    add(drum(79 if up else 78, 100), t0, 0.35 * g, pan=0.2)
def flip(t0, g=1.0):
    t = tt_(0.12); y = rng.standard_normal(len(t)) * np.exp(-t * 40) * np.sin(np.pi * t / 0.12)
    add(mono(np.convolve(y, np.ones(4) / 4, "same") * 0.18), t0, g, pan=rng.uniform(-0.3, 0.3), human=False)
def thunk(t0, g=1.0):
    add(drum(41, 110), t0, 0.5 * g); popfx(t0, 0.6 * g, 500, 120)
# ---------------- music parts (G mixolydian samba-funk) ----------------
PROG = ["G7", "F", "C", "D7"]
CH = {"G7": (55, 59, 62, 65), "F": (53, 57, 60, 65), "C": (52, 55, 60, 64), "D7": (54, 57, 60, 62)}
ROOT = {"G7": 43, "F": 41, "C": 36, "D7": 38}
def chord_of(b): return PROG[b % 4]
BASSL = [(0, 0, 3), (3, 7, 1), (4, 7, 2), (6, 0, 1), (8, 0, 3), (11, 7, 1), (12, 12, 2), (14, 7, 2)]
def bass(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, iv, du in BASSL:
            if pos == k: add(gm("Finger Bass", ROOT[chord_of(b)] + iv, du * S16 * 0.9, 112 if k in (0, 8) else 90, 0.05), tt, 0.55 * g)
COMP = (0, 3, 6, 8, 10, 13)      # partido-alto-ish guitar hits
def comp(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k in COMP:
            for j, m in enumerate(CH[chord_of(b)]): add(gm("Nylon Guitar", m + 12, 0.18, 84 if k % 4 else 96, 0.08), tt + j * 0.006, 0.16 * g, pan=-0.25)
MEL = [[(0, 79, 2), (2, 77, 2), (4, 74, 2), (6, 77, 2), (8, 79, 4), (14, 81, 2)],
       [(0, 81, 2), (2, 79, 1), (3, 77, 1), (4, 76, 4), (10, 72, 2), (12, 74, 4)],
       [(0, 76, 2), (2, 79, 2), (4, 84, 3), (7, 83, 1), (8, 81, 2), (10, 79, 2), (12, 76, 4)],
       [(0, 78, 3), (3, 79, 1), (4, 81, 2), (6, 78, 2), (8, 74, 6), (14, 77, 2)]]
def marimba(t0, t1, g=1.0, up=0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m, du in MEL[b % 4]:
            if pos == k: add(gm("Marimba", m + up, du * S16, 110 if k % 4 == 0 else 96, 0.2), tt, 0.32 * g, pan=0.2, wet=0.2, echo=0.12)
FLUTE = [[(0, 79, 6), (6, 77, 2), (8, 74, 8)], [(0, 81, 4), (4, 77, 4), (8, 76, 8)], [(0, 84, 4), (4, 83, 4), (8, 81, 2), (10, 79, 6)], [(0, 78, 6), (6, 79, 2), (8, 74, 8)]]
def flute(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m, du in FLUTE[b % 4]:
            if pos == k: add(gm("Flute", m, du * S16 * 0.95, 100, 0.15), tt, 0.30 * g, pan=-0.15, wet=0.4, echo=0.2)
def kit(t0, t1, style="full", g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if style == "full":
            if k in (0, 8): add(drum(36, 96), tt, 0.42 * g)
            if k in (4, 12): add(drum(41, 108 if k == 4 else 96), tt, 0.32 * g, wet=0.1)       # surdo accents
            if k in (4, 12): add(drum(38, 70), tt, 0.14 * g)
        if style in ("full", "lite"):
            add(drum(70, 70 if k % 4 == 0 else 42), tt, 0.20 * g, pan=-0.3)                         # maracas 16ths
            if k in (0, 3, 6, 10, 12): add(drum(67 if k in (0, 6, 12) else 68, 92), tt, 0.20 * g, pan=0.35)   # agogo
            if k in (7, 14): add(drum(63 if k == 7 else 62, 88), tt, 0.26 * g, pan=0.25)              # congas
        if style == "tick":
            if k % 4 == 0: add(drum(75, 90), tt, 0.25 * g, pan=0.2)
def groove(t0, t1, g=1.0, mel=True, up=0, style="full", fl=False):
    bass(t0, t1, g); comp(t0, t1, g); kit(t0, t1, style, g)
    if mel: marimba(t0, t1, g, up)
    if fl: flute(t0, t1, g)
def mar(t0, m, g=1.0): add(gm("Marimba", m, 0.35, 110, 0.2), t0, 0.4 * g, wet=0.25)
def glock(t0, m, g=1.0): add(gm("Glockenspiel", m, 0.4, 95, 0.3), t0, 0.26 * g, wet=0.35, echo=0.3)
def big(t0, g=1.0):
    boom(t0, 1.1 * g, 1.3); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 120), t0, 0.5 * g, wet=0.35); add(drum(41, 120), t0 + 0.01, 0.5 * g)
    add(gm("Timpani", 43, 0.8, 120, 0.3), t0, 0.5 * g, wet=0.3)
    for m in (55, 62, 67, 71, 74): add(gm("Brass Section", m, 0.35, 118, 0.15), t0, 0.22 * g, wet=0.3)
    for j, m in enumerate((67, 71, 74, 79, 83, 86)): add(gm("Marimba", m, 0.3, 120, 0.2), t0 + 0.02 + j * 0.035, 0.3 * g, wet=0.3)
    add(gm("Finger Bass", 31, 0.7, 127, 0.15), t0, 0.9 * g)

# ---------------- arrangement ----------------
TR = T["reveal"]
# BIG1 at 0: the roar + leaves
big(0.0, 1.0); roar(0.02, 1.8, 1.1, 92); roar(0.25, 1.5, 0.6, 130, 0.3); whoosh(0.05, 1.2, 1.0, 250)
for j in range(10): flip(0.1 + j * 0.13, 0.7)
groove(0.0, TR, 0.75, mel=False, style="lite")
cuica(2.3, 0.8); cuica(2.8, 0.6, False)
# reveal: rings ripple out across the canopy (one marimba per km mark)
groove(TR, T["why"], 0.95, up=0)
roar(TR + 0.1, 1.2, 0.45, 100, -0.3)
for i in range(6): mar(TR + 0.3 + 2.3 * i / 5, [67, 71, 74, 79, 83, 86][i], 0.6)
popfx(TR + 2.6, 0.7); ding(TR + 2.65, 0.5, 2637)
# why: call-and-response roars, groove
groove(T["why"], T["throat"], 0.9, fl=True)
roar(T["why"] + 0.3, 1.6, 0.45, 100, -0.5); roar(T["why"] + 2.2, 1.6, 0.45, 115, 0.5)
popfx(T["why"] + 1.0, 0.6, 900, 300)
# throat: breakdown — bass + shaker; resonance hum swells as the bulb glows
bass(T["throat"], T["q"], 0.75); kit(T["throat"], T["q"], "lite", 0.6)
whoosh(T["throat"] + 0.5, 0.6, 0.5, 300); hum(T["throat"] + 1.1, T["q"] - 0.2, 1.4, 98)
for j in range(4): boing(T["throat"] + 1.5 + j * 0.9, 0.35, 0.5, 120, 0.3, 4)
ding(T["throat"] + 2.4, 0.4, 2093)
# q: ticking checklist, roll + riser into BIG2
clock(T["q"], SIL0, 0.8)
for i in range(7): tick(T["q"] + 0.3 + i * 0.16, 0.7, 2600 + 120 * i)
roll(T["q"] + 1.0, SIL0, 0.9); riser(T["q"] + 0.6, SIL0, 0.9); add(gm("Reverse Cymbal", 60, 1.4, 110), SIL0 - 1.4, 0.25)
for j in range(3): roar(T["q"] + 0.2 + j * 0.55, 0.7, 0.18, 120 + 15 * j, [-0.6, 0.6, 0][j])
# BIG2
org(BIG2)
big(BIG2, 1.0); roar(BIG2 + 0.55, 1.1, 0.5, 105, -0.3); roar(BIG2 + 0.8, 1.1, 0.5, 125, 0.3)
for i in range(8): popfx(BIG2 + 0.05 + i * 0.06, 0.32, 900 + 120 * i)
groove(BIG2, T["gold"], 1.0, fl=True)
# gold: flute up, sparkle
groove(T["gold"], T["red"], 0.9, up=12)
glock(T["gold"] + 0.7, 86, 0.7); glock(T["gold"] + 0.9, 91, 0.5); popfx(T["gold"] + 1.0, 0.5)
# red: same groove, answer phrase
groove(T["red"], T["diff"], 0.9, fl=True)
glock(T["red"] + 0.7, 83, 0.6); popfx(T["red"] + 1.0, 0.5)
# diff: stealthy "spot the difference" — pizz-like muted guitar, ticks, ding per circle
bass(T["diff"], T["river"], 0.7); kit(T["diff"], T["river"], "tick", 0.8)
for j in range(int((T["river"] - T["diff"]) / S16 / 2)):
    if j % 2 == 0: add(gm("Muted Guitar", [55, 58, 62, 65][(j // 2) % 4], 0.12, 90), T["diff"] + j * 2 * S16, 0.16, pan=0.2)
for tt in (0.9, 1.1, 3.2, 3.5): ding(T["diff"] + tt, 0.4, 2637)
popfx(T["diff"] + 1.4, 0.6); slide(T["diff"] + 2.4, 400, 700, 0.3, 0.5); popfx(T["diff"] + 3.9, 0.6)
# river: flowing arp + water
groove(T["river"], T["dna"], 0.8, mel=False, style="lite"); flute(T["river"], T["dna"], 0.8)
for j in range(int((T["dna"] - T["river"]) / 0.25)): plink(T["river"] + j * 0.25 + 0.05, 0.4)
slide(T["river"] + 1.0, 600, 300, 1.2, 0.4)
# dna: tubes report in — accelerating glock ticks, ding at 86
groove(T["dna"], T["museum"], 0.85, mel=False)
tt0 = T["dna"] + 0.3
for i in range(0, 86, 4): tick(tt0 + 2.6 * (i / 86) ** 0.85, 0.5, 2200 + 20 * i)
ding(tt0 + 2.6, 0.7, 3136); popfx(tt0 + 2.62, 0.6)
# museum: quiet, curious — music-box-ish marimba, tweezers clicks, DNA sparkle
bass(T["museum"], T["genome"], 0.6); kit(T["museum"], T["genome"], "tick", 0.6)
for j, m in enumerate((79, 74, 71, 74, 79, 83, 81, 79)): mar(T["museum"] + 0.2 + j * 0.5, m, 0.45)
tick(T["museum"] + 1.45, 0.8, 3600); tick(T["museum"] + 1.5, 0.6, 3200)
for j in range(6): glock(T["museum"] + 2.9 + j * 0.1, [86, 88, 91, 93, 95, 98][j], 0.45)
# genome: scanner sweep, stamp
groove(T["genome"], T["y1941"], 0.9, up=12)
whoosh(T["genome"] + 1.0, 2.2, 0.5, 600); hum(T["genome"] + 1.0, T["genome"] + 3.2, 0.8, 196)
thunk(T["genome"] + 3.3, 0.9)
# y1941: timeline — clock ticks speed up, flipping pages
bass(T["y1941"], T["danger"], 0.75); kit(T["y1941"], T["danger"], "lite", 0.7)
for j in range(14): flip(T["y1941"] + 0.6 + j * 0.17, 0.5)
popfx(T["y1941"] + 0.2, 0.5); ding(T["y1941"] + 3.0, 0.5, 2637); ding(T["y1941"] + 3.2, 0.5, 3136)
# danger: minor colour, tiles flip (soft pops), hopeful bridge chime
for tt, k, b in sixteenths(T["danger"], T["card"]):
    if k in (0, 8): add(gm("Finger Bass", [40, 36, 38, 35][b % 4], 0.6, 96), tt, 0.5)
    if k in (0, 6, 12): add(gm("Nylon Guitar", [64, 60, 62, 59][b % 4] + 12, 0.3, 80), tt, 0.16)
for (c_, r_), v in LOSS_T: popfx(v, 0.25, 500, 200)
for j, m in enumerate((67, 71, 74, 79)): mar(T["danger"] + 3.0 + j * 0.2, m, 0.5)
# card: lite + sparkle
kit(T["card"], T["end"], "lite", 0.7); comp(T["card"], T["end"], 0.8); bass(T["card"], T["end"], 0.7)
glock(T["card"] + 0.1, 86); glock(T["card"] + 0.2, 91, 0.6)
# end: back to the canopy (matches the hook), two roars, final chord
FINAL = DUR - 1.4
groove(T["end"], FINAL, 0.8, fl=True)
roar(T["end"] + 0.4, 0.9, 0.35, 100, -0.4); roar(T["end"] + 1.5, 0.9, 0.35, 120, 0.4); popfx(T["end"] + 2.6, 0.6)
for j, m in enumerate((43, 55, 62, 65, 71, 74, 79)): add(gm("Marimba" if m > 50 else "Finger Bass", m, 1.2, 105, 0.5), FINAL + j * 0.02, 0.45, wet=0.35)
add(drum(36, 100), FINAL, 0.5); add(drum(49, 70), FINAL, 0.2, wet=0.4); cuica(FINAL + 0.5, 0.6)

# ---------------- mix ----------------
def reverb(x, sec=1.6, dec=3.2):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * dec); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
d_ = int(3 * S16 * SR)
for r in range(1, 3):
    sh = ECHO[: N - d_ * r] * (0.4 ** r)
    MIX[d_ * r:, 0] += sh[:, 1] * (0.8 if r % 2 else 0.3); MIX[d_ * r:, 1] += sh[:, 0] * (0.3 if r % 2 else 0.8)
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
i0, i1 = int(SIL0 * SR), int(BIG2 * SR); fade = np.linspace(1, 0, int(0.04 * SR))
MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] *= 0.1
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.0); MIX /= np.abs(MIX).max() / 0.85
fo = int(0.8 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("/workspace/work/howler/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG1 %.2f BIG2 %.2f" % (BPM, DUR, BIG1, BIG2))
