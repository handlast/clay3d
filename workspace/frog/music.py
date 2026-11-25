# 《爱吃蜗牛的小角蟾》BGM — "Rainy-night Frog Funk": A dorian, 120 BPM 4/4, 20% swing; Kalimba + Marimba + Finger Bass + congas/guiro,
# Pan Flute hook (Himalaya), synth frog croaks, rain plinks, gulp/crunch SFX. ADAPTIVE: every time comes from cues.py.
# 0–3 s: rain + croaks + countdown (no big hit). BIG1 = 3.0 s (X-ray shells) and BIG2 ("第一次！") are the ONLY two big hits.
# Bars run from G0 = 3.0 s; at BIG2 the bar origin is reset (org()). Other cues get light sounds: pops, woodblock, marimba, dings, boings.
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

def croak(t0, g=1.0, f=110, d=0.28, pulses=7, pan=0.0):
    t = tt_(d); ph = np.cumsum(f * (1 + 0.15 * np.sin(np.pi * t / d))) / SR
    saw = 2 * (ph % 1) - 1
    am = (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * pulses / d * t))) * np.sin(np.pi * t / d)
    y = np.convolve(saw * am, np.ones(6) / 6, "same")
    add(mono(y * 0.16), t0, g, pan=pan, wet=0.25, human=False)
def plink(t0, g=1.0):
    f = rng.uniform(1800, 3400); t = tt_(0.12)
    add(mono(np.sin(2 * np.pi * f * t * (1 - 0.3 * t)) * np.exp(-t * 45) * 0.12), t0, g, pan=rng.uniform(-0.6, 0.6), wet=0.4, human=False)
def rain(t0, t1, g=1.0, rate=7):
    for _ in range(int((t1 - t0) * rate)): plink(rng.uniform(t0, t1), g * rng.uniform(0.3, 1))
    n = int((t1 - t0) * SR); nz = rng.standard_normal(n); y = nz - np.convolve(nz, np.ones(6) / 6, "same")
    env = np.minimum(1, np.arange(n) / (0.3 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.3 * SR))
    add(mono(y * env * 0.012), t0, g, human=False)
def gulp(t0, g=1.0):
    bloop(t0, 1.1 * g, 520, 140, 0.22); bloop(t0 + 0.18, 0.8 * g, 380, 110, 0.2)
def crunch(t0, d=1.2, g=1.0):
    for j in range(int(d * 6)):
        tt = t0 + j / 6 + rng.uniform(-0.02, 0.02); L = tt_(0.06)
        y = rng.standard_normal(len(L)) * np.exp(-L * 70) * 0.25
        add(mono(np.convolve(y, np.ones(3) / 3, "same")), tt, g * rng.uniform(0.6, 1), human=False)
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
def chord_of(b): return PROG[b % 4]
BASSL = [(0, 0, 3), (3, 12, 1), (6, 10, 1), (7, 12, 2), (10, 7, 2), (12, 0, 1), (14, 3, 2)]
def bass(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, iv, du in BASSL:
            if pos == k: add(gm("Finger Bass", ROOT[chord_of(b)] + iv, du * S16 * 0.9, 110 if k == 0 else 92, 0.05), tt, 0.55 * g)
MEL = [[(0, 76, 2), (3, 79, 1), (4, 81, 2), (6, 79, 2), (8, 76, 3), (11, 74, 1), (12, 72, 4)],
       [(0, 74, 2), (2, 76, 2), (4, 78, 3), (7, 76, 1), (8, 74, 4), (14, 69, 2)],
       [(0, 76, 2), (2, 81, 2), (4, 84, 2), (6, 83, 2), (8, 81, 3), (11, 79, 1), (12, 76, 4)],
       [(0, 79, 3), (3, 76, 1), (4, 74, 2), (6, 71, 2), (8, 74, 6), (14, 76, 2)]]
def kalimba(t0, t1, g=1.0, up=0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m, du in MEL[b % 4]:
            if pos == k: add(gm("Kalimba", m + up, du * S16, 108 if k % 4 == 0 else 94, 0.2), tt, 0.5 * g, pan=0.2, wet=0.25, echo=0.15)
FLUTE = [[(0, 81, 6), (6, 79, 2), (8, 76, 8)], [(0, 74, 4), (4, 76, 4), (8, 78, 8)], [(0, 81, 4), (4, 84, 4), (8, 83, 2), (10, 81, 6)], [(0, 79, 6), (6, 76, 2), (8, 76, 8)]]
def flute(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m, du in FLUTE[b % 4]:
            if pos == k: add(gm("Pan Flute", m, du * S16 * 0.95, 100, 0.15), tt, 0.32 * g, pan=-0.15, wet=0.45, echo=0.2)
def comp(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k in (2, 6, 10, 14):
            for j, m in enumerate(CH[chord_of(b)]): add(gm("Marimba", m, 0.15, 84, 0.1), tt + j * 0.004, 0.13 * g, pan=-0.25)
def kit(t0, t1, style="full", g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if style == "full":
            if k in (0, 7, 10): add(drum(36, 100), tt, 0.5 * g)
            if k in (4, 12): add(drum(38, 90), tt, 0.28 * g, wet=0.1)
        if style in ("full", "lite"):
            if k % 2 == 0: add(drum(70, 70 if k % 4 == 0 else 45), tt, 0.22 * g, pan=-0.3)
            if k in (3, 6, 11, 14): add(drum(63 if k in (3, 11) else 62, 90), tt, 0.3 * g, pan=0.3)     # congas
            if k == 12: add(drum(73, 100), tt, 0.25 * g, pan=-0.2)                                      # short guiro = croak
def groove(t0, t1, g=1.0, mel=True, up=0, style="full", fl=False):
    bass(t0, t1, g); comp(t0, t1, g); kit(t0, t1, style, g)
    if mel: kalimba(t0, t1, g, up)
    if fl: flute(t0, t1, g)
def mar(t0, m, g=1.0): add(gm("Marimba", m, 0.35, 110, 0.2), t0, 0.5 * g, wet=0.25)
def glock(t0, m, g=1.0): add(gm("Glockenspiel", m, 0.4, 95, 0.3), t0, 0.28 * g, wet=0.35, echo=0.3)
def kal(t0, m, g=1.0): add(gm("Kalimba", m, 0.4, 110, 0.3), t0, 0.5 * g, wet=0.3)
def big(t0, g=1.0):
    boom(t0, 1.1 * g, 1.3); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 120), t0, 0.5 * g, wet=0.35); add(drum(47, 110), t0 + 0.01, 0.35 * g)
    add(gm("Timpani", 45, 0.8, 120, 0.3), t0, 0.5 * g, wet=0.3)
    for m in (57, 64, 69, 72, 76): add(gm("Brass Section", m, 0.35, 118, 0.15), t0, 0.22 * g, wet=0.3)
    for j, m in enumerate((69, 72, 76, 79, 81, 84)): add(gm("Kalimba", m, 0.3, 120, 0.2), t0 + 0.02 + j * 0.035, 0.4 * g, wet=0.3)
    add(gm("Finger Bass", 33, 0.7, 127, 0.15), t0, 0.9 * g)

# ---------------- arrangement ----------------
rain(0.0, BIG1, 1.0, 9)
croak(0.05, 1.0, 105, 0.32, 8); croak(1.4, 0.8, 120, 0.25, 6, 0.2)
clock(0.0, BIG1, 0.8)
for i, c in enumerate(COUNT):
    kal(c, [69, 72, 76][i], 0.9); add(drum(75, 100), c, 0.3)
for j in range(12): add(gm("Finger Bass", [45, 45, 48, 50, 52, 50, 48, 47][j % 8], 0.2, 90), j * 0.25, 0.32)
riser(1.8, BIG1 - 0.05, 0.8)
# BIG1: X-ray, three shells pop
big(BIG1, 0.85)
for i, tt in enumerate((BIG1 + 0.05, BIG1 + 0.35, BIG1 + 0.65)): popfx(tt, 0.7, 1300 + 250 * i, 400); glock(tt, [88, 91, 93][i], 0.8)
groove(BIG1, T["ct"], 0.95, up=12)
# ct: lite kit, scanner hum + beeps
bass(T["ct"], T["who"], 0.8); kit(T["ct"], T["who"], "lite", 0.8); comp(T["ct"], T["who"], 0.7)
whoosh(T["ct"] + 0.2, 0.9, 0.6, 300); hum(T["ct"] + 1.0, T["ct"] + 3.3, 1.0)
for j in range(6): beep(T["ct"] + 1.2 + j * 0.33, 0.7, 1760 if j % 2 else 2093)
ding(T["ct"] + 1.65, 0.5, 2637)
# who: full groove + pan flute, badge ding, name-plate pop, snail bassoon
groove(T["who"], T["name"], 0.9, fl=True)
ding(T["who"] + 0.4, 0.6, 3136); popfx(T["who"] + 1.4, 0.6); slide(T["who"] + 2.1, 300, 220, 0.5, 0.6)
# name: lite; card pop, "= 蜗牛" ding, love boing, snail hides (bassoon down)
bass(T["name"], T["q"], 0.75); kit(T["name"], T["q"], "lite", 0.7); kalimba(T["name"], T["q"], 0.6)
popfx(T["name"] + 0.1, 0.6); ding(T["name"] + 1.0, 0.6, 2637); boing(T["name"] + 1.4, 0.6, 0.5, 260, 0.4, 6)
add(gm("Bassoon", 50, 0.25, 100), T["name"] + 1.6, 0.35); add(gm("Bassoon", 45, 0.5, 100), T["name"] + 1.85, 0.35)
# q: drum roll + clock, dip before BIG2
clock(T["q"], SIL0, 0.8); roll(T["q"] + 0.4, SIL0, 1.0); boing(T["q"] + 0.3, 0.4, 0.4, 350, 0.3, 5)
riser(T["q"] + 0.5, SIL0, 0.9); add(gm("Reverse Cymbal", 60, 1.4, 110), SIL0 - 1.4, 0.25)
# BIG2: "第一次！" — bar origin reset
org(BIG2)
big(BIG2, 0.9)
for i in range(6): popfx(BIG2 + 0.05 + i * 0.06, 0.35, 900 + 120 * i)
gulp(BIG2 + 0.9, 1.0); crunch(BIG2 + 1.4, 0.6, 0.6)
for i in range(6): popfx(BIG2 + 2.6 + i * 0.08, 0.35, 700, 250)
groove(BIG2, T["other"], 1.0, fl=True)
# other: groove lite, croak + gulp for 黑斑蛙, check ding
bass(T["other"], T["kin"], 0.8); kit(T["other"], T["kin"], "lite", 0.8); kalimba(T["other"], T["kin"], 0.6)
croak(T["other"] + 0.2, 0.8, 95, 0.3, 7, -0.3); gulp(T["other"] + 0.65, 0.7); ding(T["other"] + 1.4, 0.5, 2637)
# kin: CT beeps, shell ding
groove(T["kin"], T["gulp"], 0.85, mel=False); comp(T["kin"], T["gulp"], 0.8)
for j in range(4): beep(T["kin"] + 1.6 + j * 0.1, 0.6, 2093)
ding(T["kin"] + 2.0, 0.6, 3136); glock(T["kin"] + 3.2, 93, 0.6)
# gulp: breakdown — bass only + "?" boing
bass(T["gulp"], T["jaw"], 0.75); add(drum(70, 60), T["gulp"], 0.1)
for j in range(int((T["jaw"] - T["gulp"]) / BEAT)): add(drum(42, 70), T["gulp"] + j * BEAT, 0.18, pan=0.3)
boing(T["gulp"] + 2.0, 0.6, 0.6, 200, 0.5, 6); slide(T["gulp"] + 2.4, 500, 250, 0.4, 0.6)
# jaw: creaky hinge slides in time with the jaw, pizz tiptoe
bass(T["jaw"], T["survey"], 0.7); kit(T["jaw"], T["survey"], "lite", 0.6)
for j in range(3): slide(T["jaw"] + 0.6 + j * 2.09, 180, 320, 0.5, 0.35)
ding(T["jaw"] + 0.4, 0.4, 2093); popfx(T["jaw"] + 2.2, 0.5)
# survey: journey — rain, flute, toms; tick per year flip
groove(T["survey"], T["five"], 0.85, mel=False, fl=True); rain(T["survey"], T["five"], 0.6, 5)
for j in range(5): add(drum(76, 100), T["survey"] + 0.3 + j * 0.6, 0.3); 
for j in range(14): plink(T["survey"] + 0.4 + j * 0.2, 0.6)
# five: pops ascending, full groove
groove(T["five"], T["double"], 1.0, up=12)
for i in range(5): popfx(T["five"] + 0.1 + i * 0.22, 0.6, 1000 + 150 * i); kal(T["five"] + 0.1 + i * 0.22, [69, 72, 74, 76, 79][i], 0.6)
# double: counter pops, ding at 11
groove(T["double"], T["card"], 0.9, fl=True)
for i in range(6): popfx(T["double"] + 0.1 + i * 0.08, 0.3, 800)
for i in range(5): mar(T["double"] + 1.4 + i * 0.2, [72, 74, 76, 79, 81][i], 0.6)
ding(T["double"] + 2.4, 0.6, 3136)
# card: lite + glock sparkle
kit(T["card"], T["end"], "lite", 0.7); comp(T["card"], T["end"], 0.8); bass(T["card"], T["end"], 0.7)
glock(T["card"] + 0.1, 88); glock(T["card"] + 0.2, 93, 0.6)
# end: rain + croak back (matches the hook), light groove, final chord
FINAL = DUR - 1.4
rain(T["end"], DUR, 0.7, 6); croak(T["end"] + 0.3, 0.8, 105, 0.3, 7)
kalimba(T["end"], FINAL, 0.6); bass(T["end"], FINAL, 0.6); popfx(T["end"] + 0.2, 0.6)
for j, m in enumerate((45, 57, 64, 67, 72, 76, 81)): add(gm("Kalimba" if m > 50 else "Finger Bass", m, 1.2, 105, 0.5), FINAL + j * 0.02, 0.45, wet=0.35)
add(drum(36, 100), FINAL, 0.5); add(drum(49, 70), FINAL, 0.2, wet=0.4); croak(FINAL + 0.6, 0.6, 100, 0.3, 7)
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
with wave.open("/workspace/work/frog/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG1 %.2f BIG2 %.2f" % (BPM, DUR, BIG1, BIG2))
