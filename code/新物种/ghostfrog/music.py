# 《叶中幽灵蛙》BGM — "Cloud-forest Ghost Huayno": E minor (Em-D-C-B7), 120 BPM 4/4 with a huayno long-short lilt, 12% swing.
# Pan Flute lead + Recorder answers, Nylon-guitar 'charango' tremolo strums, Pizzicato stealth line, Marimba ostinato,
# Acoustic Bass, bombo (kick + floor tom), maracas, wood-block night ticks, synthesized ghost 'whoo' glides.
# ADAPTIVE: every time comes from cues.py. BIG1 = 0.0 s (the eye opens) and BIG2 ("一个新物种！") are the ONLY two big hits.
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
S16 = BEAT / 4; SW = 0.12 * S16
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


# ---------------- frog / ghost SFX ----------------
def flip(t0, g=1.0):
    t = tt_(0.12); y = rng.standard_normal(len(t)) * np.exp(-t * 40) * np.sin(np.pi * t / 0.12)
    add(mono(np.convolve(y, np.ones(4) / 4, "same") * 0.18), t0, g, pan=rng.uniform(-0.3, 0.3), human=False)
def roll(t0, t1, g=1.0):
    n = int((t1 - t0) / 0.0625)
    for j in range(n): add(drum(38, 60 + int(50 * j / max(1, n))), t0 + j * 0.0625, (0.12 + 0.3 * j / max(1, n)) * g, wet=0.15)
def whoo(t0, d=1.4, g=1.0, f0=520, f1=330, pan=0.0):
    """ghostly 'whooo': breathy sine glide with slow vibrato + filtered noise"""
    t = tt_(d); f = f0 * (f1 / f0) ** (t / d) * (1 + 0.012 * np.sin(2 * np.pi * 5.2 * t))
    ph = np.cumsum(f) / SR; y = np.sin(2 * np.pi * ph) + 0.25 * np.sin(4 * np.pi * ph)
    nz = np.convolve(rng.standard_normal(len(t)), np.ones(30) / 30, "same") * 3
    env = np.sin(np.pi * np.minimum(1, t / d)) ** 1.5
    add(mono((y * 0.7 + nz * 0.3) * env * 0.12), t0, g, pan=pan, wet=0.7, echo=0.3, human=False)
def croak(t0, g=1.0, f=180):
    t = tt_(0.16); ph = np.cumsum(f * (1 + 0.3 * np.exp(-t * 30))) / SR
    y = np.sign(np.sin(2 * np.pi * ph)) * (0.5 + 0.5 * np.sin(2 * np.pi * 38 * t)) * np.exp(-t * 14)
    add(mono(np.convolve(y, np.ones(6) / 6, "same") * 0.1), t0, g, pan=0.2, wet=0.2, human=False)
def moo(t0, g=1.0, f=110):
    t = tt_(1.1); ff = f * (1 + 0.25 * np.sin(np.pi * t / 1.1)) ; ph = np.cumsum(ff) / SR; saw = 2 * (ph % 1) - 1
    y = np.convolve(saw, np.ones(18) / 18, "same") * np.sin(np.pi * t / 1.1) ** 0.6
    add(mono(y * 0.16), t0, g, pan=-0.2, wet=0.3, human=False)
def clop(t0, g=1.0): add(drum(77, 90), t0, 0.25 * g, pan=rng.uniform(-0.4, 0.4))
def crack(t0, g=1.0):
    for j in range(4): tick(t0 + j * 0.03, 0.5 * g, 2600 - 300 * j)
def ching(t0, g=1.0):
    for f in (3520, 4186, 5274): ding(t0, 0.35 * g, f)

# ---------------- music parts (E minor huayno) ----------------
PROG = ["Em", "D", "C", "B7"]
CH = {"Em": (52, 55, 59, 64), "D": (50, 54, 57, 62), "C": (48, 52, 55, 60), "B7": (47, 51, 54, 57)}
ROOT = {"Em": 40, "D": 38, "C": 36, "B7": 35}
def chord_of(b): return PROG[b % 4]
BASSL = [(0, 0, 3), (3, 7, 1), (4, 7, 2), (6, 12, 2), (8, 0, 3), (11, 7, 1), (12, 7, 2), (14, 5, 2)]
def bass(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, iv, du in BASSL:
            if pos == k: add(gm("Acoustic Bass", ROOT[chord_of(b)] + iv, du * S16 * 0.9, 112 if k in (0, 8) else 88, 0.05), tt, 0.6 * g)
STRUM = (0, 3, 4, 7, 8, 11, 12, 14, 15)
def charango(t0, t1, g=1.0, trem=False):
    for tt, k, b in sixteenths(t0, t1):
        if k in STRUM or trem:
            acc = k in (0, 4, 8, 12)
            for j, m in enumerate(CH[chord_of(b)]): add(gm("Nylon Guitar", m + 12, 0.14, 92 if acc else 70, 0.06), tt + j * (0.005 if k % 2 == 0 else -0.004) + 0.012, 0.12 * g, pan=-0.3)
def pizz(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k % 2 == 0:
            c = CH[chord_of(b)]; m = [c[0], c[2], c[1] + 12, c[2]][(k // 2) % 4]
            add(gm("Pizzicato Strings", m, 0.2, 100 if k % 8 == 0 else 80, 0.1), tt, 0.28 * g, pan=0.25, wet=0.25)
def marimba(t0, t1, g=1.0, up=0):
    for tt, k, b in sixteenths(t0, t1):
        if k in (0, 3, 6, 8, 11, 14):
            c = CH[chord_of(b)]; m = [c[0], c[1], c[2], c[3]][[0, 3, 6, 8, 11, 14].index(k) % 4] + 12 + up
            add(gm("Marimba", m, 0.3, 104 if k in (0, 8) else 86, 0.2), tt, 0.26 * g, pan=0.15, wet=0.2)
MEL = [[(0, 76, 3), (3, 79, 1), (4, 79, 2), (6, 76, 2), (8, 74, 3), (11, 76, 1), (12, 71, 4)],
       [(0, 74, 3), (3, 78, 1), (4, 78, 2), (6, 74, 2), (8, 69, 4), (12, 74, 4)],
       [(0, 72, 3), (3, 76, 1), (4, 76, 2), (6, 79, 2), (8, 76, 3), (11, 74, 1), (12, 72, 4)],
       [(0, 71, 3), (3, 75, 1), (4, 75, 2), (6, 78, 2), (8, 75, 3), (11, 71, 1), (12, 71, 4)]]
def panflute(t0, t1, g=1.0, up=0, inst="Pan Flute"):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m, du in MEL[b % 4]:
            if pos == k: add(gm(inst, m + up, du * S16 * 0.95, 104 if k % 4 == 0 else 92, 0.18), tt, 0.32 * g, pan=-0.1, wet=0.45, echo=0.25)
REC = [[(8, 83, 2), (10, 81, 2), (12, 79, 4)], [(8, 81, 2), (10, 78, 2), (12, 76, 4)], [(8, 79, 2), (10, 76, 2), (12, 72, 4)], [(8, 78, 2), (10, 75, 2), (12, 71, 4)]]
def recorder(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m, du in REC[b % 4]:
            if pos == k: add(gm("Recorder", m, du * S16 * 0.9, 90, 0.15), tt, 0.22 * g, pan=0.3, wet=0.5, echo=0.3)
def kit(t0, t1, style="full", g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if style == "full":
            if k in (0, 8): add(drum(36, 100), tt, 0.42 * g)
            if k in (3, 11): add(drum(41, 96), tt, 0.26 * g, wet=0.1)       # bombo answer (huayno long-short)
            if k in (4, 12): add(drum(39, 70), tt, 0.10 * g, wet=0.2)
        if style in ("full", "lite"):
            add(drum(70, 70 if k % 4 == 0 else 40), tt, 0.18 * g, pan=-0.3)   # maracas / chajchas
        if style in ("tick", "lite"):
            if k % 4 == 0: add(drum(76 if (k // 4) % 2 == 0 else 77, 86), tt, 0.22 * g, pan=0.25)
def groove(t0, t1, g=1.0, mel=True, up=0, style="full", rec=False, mar=True):
    bass(t0, t1, g); charango(t0, t1, g); kit(t0, t1, style, g)
    if mar: marimba(t0, t1, 0.8 * g)
    if mel: panflute(t0, t1, g, up)
    if rec: recorder(t0, t1, g)
def mar(t0, m, g=1.0): add(gm("Marimba", m, 0.35, 110, 0.2), t0, 0.4 * g, wet=0.25)
def glock(t0, m, g=1.0): add(gm("Glockenspiel", m, 0.4, 95, 0.3), t0, 0.26 * g, wet=0.35, echo=0.3)
def big(t0, g=1.0):
    boom(t0, 1.1 * g, 1.3); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 120), t0, 0.5 * g, wet=0.35); add(drum(41, 120), t0 + 0.01, 0.5 * g)
    add(gm("Timpani", 40, 0.8, 120, 0.3), t0, 0.5 * g, wet=0.3)
    for m in (52, 59, 64, 67, 71): add(gm("Pan Flute", m + 12, 0.5, 118, 0.2), t0, 0.16 * g, wet=0.4)
    for j, m in enumerate((64, 67, 71, 76, 79, 83)): add(gm("Marimba", m, 0.3, 120, 0.2), t0 + 0.02 + j * 0.035, 0.3 * g, wet=0.3)
    add(gm("Acoustic Bass", 28, 0.7, 127, 0.15), t0, 0.9 * g)

# ---------------- arrangement ----------------
def nx(k): return nxt(k)
# 1 hook — BIG1: the eye opens; ghost whoo; leaves fly
big(0.0, 1.0); whoo(0.05, 1.6, 1.2, 700, 380); whoosh(0.05, 1.2, 1.0, 250)
for j in range(10): flip(0.08 + j * 0.11, 0.6)
slide(0.1, 900, 1500, 0.5, 0.5)
pizz(0.0, T["leaf"], 0.9); kit(0.0, T["leaf"], "tick", 0.9); bass(0.0, T["leaf"], 0.7)
whoo(2.4, 1.2, 0.5, 400, 300, 0.3); ding(3.9, 0.4, 2637)
# 2 leaf — stealth: pizz + ticks, leaves settle (soft flips), eye circles = two glock blinks
tl = T["leaf"]; pizz(tl, nx("leaf"), 0.9); kit(tl, nx("leaf"), "tick", 0.8); bass(tl, nx("leaf"), 0.6)
for i in range(9): flip(tl + 0.3 + i * 0.18 + 0.7, 0.4)
glock(tl + 2.6, 88, 0.7); glock(tl + 2.75, 91, 0.6)
# 3 night — clock ticks + walking stealth bass + recorder; eye-shine ding
tn = T["night"]; clock(tn, nx("night"), 0.8); pizz(tn, nx("night"), 0.8); bass(tn, nx("night"), 0.7); recorder(tn, nx("night"), 0.8)
croak(tn + 1.2, 0.5, 200); croak(tn + 1.35, 0.4, 220); croak(tn + 3.4, 0.5, 190)
ding(tn + 2.65, 0.6, 3136); ding(tn + 2.8, 0.5, 3136)
# 4 q — mystery: ticking, '?' bloop, roll + riser into BIG2
tq = T["q"]; clock(tq, SIL0, 0.8); pizz(tq, SIL0, 0.7)
bloop(tq + 0.6, 0.6, 300, 900, 0.25); popfx(tq + 1.25, 0.6)
roll(tq + 1.2, SIL0, 0.9); riser(tq + 0.5, SIL0, 0.9); add(gm("Reverse Cymbal", 60, 1.4, 110), SIL0 - 1.4, 0.25)
# 5 BIG2 — full huayno
org(BIG2)
big(BIG2, 1.0); whoo(BIG2 + 0.3, 1.0, 0.5, 500, 800)
for i in range(8): popfx(BIG2 + 0.05 + i * 0.06, 0.3, 900 + 120 * i)
groove(BIG2, T["eye"], 1.0, rec=True); ching(BIG2 + 0.9, 0.8)
# 6 eye — brush paints: two upward glides, reticulation ticks, sclera ding
te = T["eye"]; groove(te, nx("eye"), 0.75, mel=False, style="lite")
slide(te + 0.4, 400, 800, 1.1, 0.5); slide(te + 1.7, 500, 1000, 1.1, 0.5)
for j in range(10): tick(te + 3.0 + j * 0.1, 0.5, 2400 + 120 * j)
ding(te + 4.3, 0.6, 2637); popfx(te + 4.4, 0.5)
# 7 name — cards slide in (whoosh), '+' pop, merge ding
tm = T["name"]; groove(tm, nx("name"), 0.8, mel=True, up=12, style="lite", mar=False)
whoosh(tm + 0.1, 0.4, 0.6); whoosh(tm + 0.7, 0.4, 0.6); popfx(tm + 1.4, 0.6); whoosh(tm + 2.6, 0.5, 0.5); ching(tm + 3.0, 0.7)
# 8 ghost — ghostly whoos over a lite groove
tg = T["ghost"]; groove(tg, nx("ghost"), 0.8, mel=True, style="lite")
whoo(tg + 0.2, 1.5, 0.6, 600, 420, -0.3); whoo(tg + 2.0, 1.4, 0.5, 520, 700, 0.3)
slide(tg + 1.6, 300, 600, 0.8, 0.4); popfx(tg + 3.0, 0.5); ding(tg + 3.1, 0.4, 2093)
# 9 skin — magnifier stealth, flip-over boing, belly ding
ts = T["skin"]; pizz(ts, nx("skin"), 0.9); bass(ts, nx("skin"), 0.7); kit(ts, nx("skin"), "tick", 0.8)
whoosh(ts + 0.4, 0.4, 0.5)
for j in range(8): tick(ts + 0.8 + j * 0.2, 0.4, 3000 + 80 * j)
whoosh(ts + 2.7, 0.8, 0.7); boing(ts + 3.4, 0.5, 0.6, 160, 0.4, 6); ding(ts + 3.9, 0.5, 2349)
# 10 size — ruler: rising marimba scale while the bar grows; coin ching
tz = T["size"]; groove(tz, nx("size"), 0.75, mel=False, style="lite")
for j, m in enumerate((64, 66, 67, 69, 71, 72, 74, 76, 78, 79)): mar(tz + 1.0 + j * 0.16, m, 0.5)
ding(tz + 2.65, 0.6, 3136); ching(tz + 3.05, 0.9)
# 11 sex — two pops, rising arrow slide
tx = T["sex"]; groove(tx, nx("sex"), 0.8, mel=True, style="lite", mar=False)
popfx(tx + 0.1, 0.6, 1000); popfx(tx + 0.4, 0.6, 1300); slide(tx + 1.0, 500, 750, 0.4, 0.5)
# 12 hole — tension: heartbeat + '!' sting, slide-whistle dive, quiet chamber
th_ = T["hole"]; bass(th_, nx("hole"), 0.6); kit(th_, nx("hole"), "tick", 0.6)
for j in range(5): add(drum(36, 80), th_ + 0.2 + j * 0.45, 0.25); add(drum(36, 60), th_ + 0.38 + j * 0.45, 0.15)
add(gm("Pizzicato Strings", 76, 0.2, 120), th_ + 1.3, 0.4); add(gm("Pizzicato Strings", 77, 0.2, 120), th_ + 1.3, 0.3)
popfx(th_ + 1.3, 0.7, 1800, 900); slide(th_ + 2.2, 1400, 300, 1.3, 0.7)
whoo(th_ + 3.6, 1.2, 0.4, 380, 300)
# 13 four — report in: one marimba note + pop per frog, groove returns
tf = T["four"]; groove(tf, nx("four"), 0.9, rec=True)
for i in range(4): popfx(tf + 0.15 + i * 0.35, 0.5, 900 + 150 * i); mar(tf + 0.15 + i * 0.35, [64, 67, 71, 76][i], 0.6)
ching(tf + 1.85, 0.6)
# 14 genus — drawer clicks accelerate, 4 new drawers ding
tgn = T["genus"]; groove(tgn, nx("genus"), 0.8, mel=False)
for i in range(27): tick(tgn + 1.0 * (i / 27) ** 0.7, 0.35, 2200 + 30 * i)
for i in range(4): ding(tgn + 1.6 + i * 0.4, 0.5, [2637, 2960, 3136, 3520][i])
# 15 devel — egg -> tadpole crossed out -> froglet hop
tdv = T["devel"]; groove(tdv, nx("devel"), 0.8, mel=True, style="lite")
bloop(tdv + 0.6, 0.4, 400, 700); add(gm("Pizzicato Strings", 64, 0.2, 110), tdv + 2.3, 0.4); popfx(tdv + 2.5, 0.6, 600, 200)
crack(tdv + 2.8, 1.0); boing(tdv + 2.9, 0.5, 0.5, 220, 0.4, 8)
# 16 card — sparkle, soft
tc = T["card"]; charango(tc, nx("card"), 0.7); bass(tc, nx("card"), 0.6); kit(tc, nx("card"), "lite", 0.6); recorder(tc, nx("card"), 0.8)
glock(tc + 0.1, 88); glock(tc + 0.2, 91, 0.6); crack(tc + 0.9, 0.6); boing(tc + 2.0, 0.4, 0.5, 220, 0.4, 8)
# 17 map — pin ping, zoom whoosh, altitude rise
tp = T["map"]; groove(tp, nx("map"), 0.8, mel=True, up=0, style="lite", rec=False)
ding(tp + 0.6, 0.6, 3520); whoosh(tp + 1.4, 1.8, 0.6, 500); slide(tp + 3.5, 300, 900, 1.1, 0.5); ding(tp + 4.6, 0.4, 2637)
# 18 cows — pasture: cowbell, moo, hoof clops
tw = T["cows"]; groove(tw, nx("cows"), 0.85, rec=True)
for j in range(int((nx("cows") - tw) / BEAT)): add(drum(56, 80), tw + j * BEAT, 0.12, pan=0.3)
moo(tw + 0.6, 0.8, 105); moo(tw + 2.2, 0.6, 120)
for j in range(14): clop(tw + 1.8 + j * 0.16, 0.8)
# 19 end — back to the litter: groove, ghost whoo as the body fades, final chord
FINAL = DUR - 1.4
groove(T["end"], T["end"] + 2.6, 0.75); pizz(T["end"] + 2.6, FINAL, 0.6); whoo(T["end"] + 2.6, 1.6, 0.6, 600, 360)
for j, m in enumerate((40, 52, 59, 64, 67, 71, 76)): add(gm("Marimba" if m > 50 else "Acoustic Bass", m, 1.2, 105, 0.5), FINAL + j * 0.02, 0.45, wet=0.35)
add(gm("Pan Flute", 76, 1.3, 100, 0.4), FINAL, 0.3, wet=0.6); add(drum(36, 100), FINAL, 0.5); add(drum(49, 70), FINAL, 0.2, wet=0.4)

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
with wave.open("/workspace/work/ghostfrog/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG1 %.2f BIG2 %.2f" % (BPM, DUR, BIG1, BIG2))
