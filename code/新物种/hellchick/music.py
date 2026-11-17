# 《地狱鸡》BGM — "Hell Creek Hoedown": G major bluegrass, 120 BPM 4/4, ADAPTIVE: built entirely from cues.py (text-driven timeline).
# Banjo forward rolls + Fiddle lead (original tune) + Acoustic Bass boom (root-fifth) + Steel Guitar chop on 2&4 + brush kit/woodblock clip-clop.
# Tuba stomps for the T-rex, pizzicato tiptoe for the menu, riser + fiddle tremolo for the jaw scan, 0.5 s silence, big hit at BIG2.
# Self-made SFX (numpy): chicken "bok/bagawk", crunch chewing, juicy squish, stone rattle, seed bloop, slide whistle, dings.
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import gm as _gm, drum as _drum, SR
from cues import *
LV = {"Banjo": 0.17, "Fiddle": 0.15, "Acoustic Bass": 0.8, "Steel Guitar": 1.0, "Harmonica": 1.0, "Tuba": 1.1, "Pizzicato Strings": 1.0,
      "Wood Block": 0.16, "Reverse Cymbal": 4.0, "Brass Section": 0.55}
DLV = {42: 0.6, 46: 0.9, 76: 0.16, 77: 0.16}
@functools.lru_cache(maxsize=None)
def gm(name, m, dur=0.5, vel=100, release=0.2): return _gm(name, m, dur, vel, release=release) * LV.get(name, 1.0)
@functools.lru_cache(maxsize=None)
def drum(n, vel=100): return _drum(n, vel) * DLV.get(n, 1.0)
@functools.lru_cache(maxsize=None)
def brush(n, vel=100): return _gm("Brush", n, 1.0, vel, release=0.05, bank=128) * {36: 0.55, 42: 0.6}.get(n, 1.0)
N = int(SR * DUR); MIX = np.zeros((N, 2)); VERB = np.zeros((N, 2)); ECHO = np.zeros((N, 2))
rng = np.random.default_rng(7)
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
S16 = BEAT / 4; SW = 0.12 * S16; B2 = K2 // 4
def ph(b): return b if b < B2 else b - B2
def sixteenths(t0, t1):
    out = []; b0 = int(math.floor((t0 - G0) / BAR)) - 1
    for b in range(b0, b0 + 200):
        s0 = G0 + b * BAR
        if s0 > t1 + 0.1: break
        for k in range(16):
            tt = s0 + k * S16
            if t0 - 1e-4 <= tt < t1 - 1e-4: out.append((tt + (SW if k % 2 else 0), k, b))
    return out
PROG = ["G", "G", "C", "G", "G", "D7", "G", "G"]
CH = {"G": (55, 59, 62, 67), "C": (55, 60, 64, 67), "D7": (54, 57, 60, 62)}
ROOT = {"G": 43, "C": 36, "D7": 38}; FIFTH = {"G": 38, "C": 43, "D7": 45}
def chord_of(b): return PROG[ph(b) % 8]
MEL = [[(0, 74, 2), (2, 71, 2), (4, 67, 2), (6, 71, 2), (8, 74, 4), (12, 79, 4)],
       [(0, 78, 2), (2, 79, 2), (4, 81, 2), (6, 79, 2), (8, 76, 2), (10, 74, 2), (12, 71, 4)],
       [(0, 72, 2), (2, 76, 2), (4, 79, 2), (6, 76, 2), (8, 84, 4), (12, 83, 2), (14, 81, 2)],
       [(0, 79, 4), (4, 74, 2), (6, 71, 2), (8, 67, 6), (14, 69, 2)],
       [(0, 71, 2), (2, 74, 2), (4, 79, 3), (7, 78, 1), (8, 79, 2), (10, 81, 2), (12, 83, 4)],
       [(0, 81, 2), (2, 78, 2), (4, 74, 2), (6, 78, 2), (8, 81, 2), (10, 84, 2), (12, 83, 2), (14, 81, 2)],
       [(0, 79, 2), (2, 74, 2), (4, 71, 2), (6, 74, 2), (8, 72, 2), (10, 71, 2), (12, 69, 2), (14, 66, 2)],
       [(0, 67, 6), (6, 74, 2), (8, 71, 2), (10, 69, 2), (12, 67, 4)]]
def fiddle(t0, t1, g=1.0, up=0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m, du in MEL[ph(b) % 8]:
            if pos == k:
                dur = du * S16
                add(gm("Fiddle", m + up, dur * 0.95, 105 if k % 4 == 0 else 92, 0.12), tt, 0.55 * g, pan=-0.15, wet=0.2)
                if du >= 4: add(gm("Fiddle", m + up - 12 + 7 if m + up - 5 > 60 else m + up + 7, dur * 0.9, 70, 0.12), tt + 0.01, 0.15 * g, pan=0.2, wet=0.2)
ROLL = [0, 1, 2, 0, 1, 2, 0, 1]        # forward roll over chord tones (3 strings)
def banjo(t0, t1, g=1.0, every=1):
    for tt, k, b in sixteenths(t0, t1):
        if k % 2 == 0 or every == 1:
            if every == 2 and k % 2: continue
            ch = CH[chord_of(b)]; tones = (ch[1] + 12, ch[2] + 12, ch[3] + 12) if k % 8 < 6 else (ch[2] + 12, ch[3] + 12, ch[1] + 24)
            m = tones[ROLL[(k // (1 if every == 1 else 2)) % 8]]
            add(gm("Banjo", m - 12, 0.18, 96 if k % 4 == 0 else 78, 0.06), tt, 0.42 * g, pan=0.25, wet=0.1)
def chop(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k in (4, 12):
            for j, m in enumerate(CH[chord_of(b)]): add(gm("Steel Guitar", m, 0.09, 100, 0.04), tt + j * 0.006, 0.35 * g, pan=-0.3)
def bass(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        c = chord_of(b)
        if k == 0: add(gm("Acoustic Bass", ROOT[c], BEAT * 0.9, 112, 0.05), tt, 0.95 * g)
        if k == 8: add(gm("Acoustic Bass", FIFTH[c], BEAT * 0.9, 105, 0.05), tt, 0.9 * g)
        if k == 14 and ph(b) % 2 == 1: add(gm("Acoustic Bass", FIFTH[c] + 2, BEAT * 0.4, 90, 0.05), tt, 0.6 * g)
def kit(t0, t1, style="full", g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if style in ("full", "lite"):
            if k in (0, 8): add(brush(36, 110), tt, 0.85 * g)
            if k in (4, 12): add(brush(38, 105), tt, 0.65 * g, wet=0.15)
            if k % 2 == 0: add(brush(42, 80 if k % 4 == 0 else 55), tt, 0.28 * g, pan=0.3)
        if style == "full" and k % 4 == 2: add(drum(77, 90), tt, 0.4 * g, pan=-0.35)       # clip-clop
        if style == "full" and k % 4 == 0 and k: add(drum(76, 80), tt, 0.3 * g, pan=0.35)
        if style == "shaker": add(drum(82, 85 if k % 4 == 2 else 55), tt, 0.2 * g, pan=-0.3)
def groove(t0, t1, g=1.0, fid=True, up=0, style="full"):
    kit(t0, t1, style, g); bass(t0, t1, g); banjo(t0, t1, g); chop(t0, t1, g)
    if fid: fiddle(t0, t1, g, up)
TIP = [(0, 67), (4, 71), (8, 74), (12, 71)]
def tiptoe(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m in TIP:
            if pos == k: add(gm("Pizzicato Strings", m - (0 if ph(b) % 2 else 2), 0.15, 95, 0.1), tt, 0.45 * g, pan=0.2, wet=0.25, echo=0.2)
        if k in (2, 10): add(drum(77, 80), tt, 0.25 * g, pan=-0.3)
# ---------------- SFX ----------------
def boom(t0, g=1.0, dur=1.1):
    t = tt_(dur); f = 36 + 80 * np.exp(-t * 16)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2) * 0.9), t0, g, human=False)
def thump(t0, g=1.0, f0=52):
    t = tt_(0.3); f = f0 + 40 * np.exp(-t * 30)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12) * 0.8), t0, g, human=False)
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
def cluck(t0, g=1.0, kind="bok"):        # synthetic chicken: buzzy glottal source + two vowel formants
    d = {"bok": 0.09, "bagawk": 0.32}[kind]; t = tt_(d)
    if kind == "bok": f = 520 - 160 * t / d
    else: f = np.where(t < 0.1, 480, 480 + 520 * np.minimum(1, (t - 0.1) / 0.08)) * (1 + 0.02 * np.sin(2 * np.pi * 30 * t))
    phs = np.cumsum(f) / SR; y = np.zeros(len(t))
    for h in range(1, 14):
        fh = f * h; amp = np.exp(-((fh - 900) / 350) ** 2) + 0.6 * np.exp(-((fh - 2200) / 500) ** 2) + 0.15
        y += np.sin(2 * np.pi * phs * h) * amp / h ** 0.3
    env = np.minimum(1, t / 0.006) * np.minimum(1, (d - t) / 0.03)
    y = y * env + rng.standard_normal(len(t)) * np.exp(-t * 200) * 0.6
    add(mono(y * 0.05), t0, g, wet=0.15, human=False)
def bagawk(t0, g=1.0):
    cluck(t0, g); cluck(t0 + 0.12, 0.9 * g); cluck(t0 + 0.24, g, "bagawk")
def crunch(t0, g=1.0, d=0.12):
    n = int(d * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for j in range(9):
        i = int(rng.uniform(0, 0.75) * n); L = int(0.012 * SR)
        seg = rng.standard_normal(min(L, n - i)) * np.exp(-np.arange(min(L, n - i)) / SR * 300)
        y[i:i + len(seg)] += seg * rng.uniform(0.4, 1)
    y = y - np.convolve(y, np.ones(6) / 6, "same")
    add(mono(y * np.exp(-t * 12) * 0.35), t0, g, human=False)
def squish(t0, g=1.0):
    t = tt_(0.25); f = 300 + 900 * (t / 0.25) ** 0.5
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10) * 0.2 + np.convolve(rng.standard_normal(len(t)), np.ones(12) / 12, "same") * np.exp(-t * 14) * 0.9
    add(mono(y * 0.5), t0, g, wet=0.2, human=False)
def rattle(t0, d, g=1.0):
    n = int(d * SR)
    for j in range(int(d * 22)):
        tt = t0 + rng.uniform(0, d); L = tt_(0.03)
        y = np.sin(2 * np.pi * rng.uniform(1500, 3200) * L) * np.exp(-L * 180) * 0.25 + rng.standard_normal(len(L)) * np.exp(-L * 300) * 0.2
        add(mono(y), tt, g * rng.uniform(0.4, 1), pan=rng.uniform(-0.3, 0.3), human=False)
def bloop(t0, g=1.0, f0=300, f1=900):
    t = tt_(0.14); f = f0 * (f1 / f0) ** (t / 0.14)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.14) * 0.3), t0, g, wet=0.3, human=False)
def slide(t0, f0, f1, d=0.4, g=1.0):
    t = tt_(d); f = f0 * (f1 / f0) ** (t / d) * (1 + 0.01 * np.sin(2 * np.pi * 6 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.2 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    add(mono(y * np.sin(np.pi * t / d) ** 0.5 * 0.12), t0, g, wet=0.3, human=False)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T_ = t1 - t0
    y = np.convolve(rng.standard_normal(n), np.ones(5) / 5, "same") * (t / T_) ** 2.5 * 0.07
    f = 180 * (1600 / 180) ** (t / T_); y += np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / T_) ** 2 * 0.04
    add(mono(y), t0, g, human=False)
def stomp(t0, g=1.0): add(gm("Tuba", 31, 0.35, 120, 0.1), t0, 0.9 * g); thump(t0, 0.7 * g, 45)
def big(t0, g=1.0):
    boom(t0, 1.2 * g, 1.3); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 127), t0, 0.6 * g, wet=0.35); add(drum(57, 110), t0 + 0.01, 0.3 * g, pan=0.4)
    add(brush(38, 127), t0, 0.6 * g, wet=0.3)
    for m in (55, 59, 62, 67, 71, 74): add(gm("Banjo", m, 0.4, 120, 0.2), t0 + (m - 55) * 0.003, 0.35 * g, wet=0.3)
    for m in (55, 62, 67): add(gm("Brass Section", m, 0.35, 120, 0.12), t0, 0.32 * g, wet=0.3)
    add(gm("Fiddle", 79, 0.5, 120, 0.2), t0, 0.5 * g, wet=0.3)
    add(gm("Acoustic Bass", 31, 0.7, 127, 0.15), t0, 1.2 * g)

# ---------------- arrangement (all times from cues) ----------------
whoosh(0.02, 0.36, 1.2, 300)
for j, m in enumerate([62, 67, 71]): add(gm("Banjo", m, 0.15, 100, 0.05), HOOK_HIT - (3 - j) * S16, 0.4)
big(HOOK_HIT); crunch(HOOK_HIT + 0.02, 1.2); squish(HOOK_HIT + 0.05, 0.6)
groove(HOOK_HIT, HOOK_STOP + 0.3)
for h in (qb(1), qb(2), qb(3)): crunch(h, 0.8)
cluck(qb(1.5), 0.9); cluck(qb(2.5), 0.9)
# (tape stop HOOK_STOP -> HOOKCUT applied after mix)
nm = T["name"]
# 6600 万年前 / chewing: solo banjo roll + crunches
banjo(HOOKCUT, nm, 0.8, every=2)
for j in range(4): crunch(HOOKCUT + 0.15 + j * BEAT * 0.5, 0.45)
big_name = nm
add(drum(36, 110), nm, 0.7); add(drum(49, 90), nm, 0.3, wet=0.3); bagawk(nm + 0.05, 1.1)
banjo(nm, T["site"], 0.9); bass(nm, T["site"], 0.9); kit(nm, T["site"], "lite", 0.7)
for b in (1.5, 2.5): popfx(at("name", b), 0.6); add(gm("Harmonica", 74 + int(b * 2), 0.2, 100), at("name", b), 0.5, wet=0.2)
groove(T["site"], T["neigh"], 0.9, fid=False)
fiddle(T["size"], T["neigh"], 0.9)
for b, m in ((0, 79), (0.5, 83)): popfx(at("site", b), 0.5); ding(at("site", b), 0.4, 1568 if m == 79 else 1976)
slide(at("site", 1), 1500, 600, 0.5, 0.8); thump(at("site", 1.6), 0.6, 80)
add(gm("Brass Section", 43, 0.4, 110), at("site", 2.5), 0.4, wet=0.2); add(drum(57, 90), at("site", 2.5), 0.25, wet=0.3)
popfx(at("size", 1), 0.6); cluck(at("size", 1.1), 0.5)
for j in range(5): tick(at("size", 0.5) + j * 0.15, 0.4, 2600)
thump(at("size", 2.5), 0.8, 70); ding(at("size", 2.6), 0.5, 2093)
for b in (0.5, 1.5, 3, 4): crunch(at("beak", b), 0.5)
popfx(at("beak", 1), 0.6); add(drum(57, 90), at("beak", 1.3), 0.25)
add(gm("Harmonica", 79, 0.3, 100), at("beak", 3), 0.5, wet=0.2)
# T-rex: band stops, tuba stomps
for b in range(4): stomp(at("neigh", b), 1.0)
add(gm("Tuba", 26, 0.9, 120, 0.3), at("neigh", 2), 0.6); boom(at("neigh", 2), 0.4, 0.8)
cluck(at("neigh", 1.5), 0.8); cluck(at("neigh", 1.75), 0.8)
# menu: pizzicato tiptoe + bass
tiptoe(T["menu"], T["jaw"], 1.0); bass(T["menu"], T["jaw"], 0.7)
for b in (0.5, 1.5): ding(at("menu", b), 0.45, 2349)
slide(at("menu", 3.5), 500, 1300, 0.45, 0.9); popfx(at("menu", 4), 0.5, 600, 200)
# jaw: shaker, pedal bass, fiddle tremolo, scanner ticks, riser into silence
kit(T["jaw"], SIL0, "shaker", 1.0)
for tt, k, b in sixteenths(T["jaw"], SIL0):
    if k % 4 == 0: add(gm("Acoustic Bass", 38, BEAT * 0.8, 108, 0.05), tt, 0.85)
    if k % 2 == 0: tick(tt, 0.3, 3400)
    if k % 2 == 0: add(gm("Fiddle", 74 if k % 4 == 0 else 75, S16 * 1.8, 80, 0.05), tt, 0.25, wet=0.3)
riser(T["jaw"], SIL0, 1.0); add(gm("Reverse Cymbal", 60, 1.6, 110), SIL0 - 1.6, 0.6)
# BIG2 -> full band, fiddle up an octave for the reveal
big(BIG2, 1.1); bagawk(BIG2 + 0.1, 1.2)
groove(BIG2, T["f1"], 1.0, up=12)
popfx(at("reveal", 1), 0.6)
groove(T["f1"], T["rare"], 0.85)
for j in range(int((nxt("f1") - T["f1"] - 0.5) / 0.25)): crunch(T["f1"] + 0.5 + j * 0.25, 0.4)
popfx(at("f1", 1), 0.5)
slide(at("f2", 1), 400, 1100, 0.45, 1.0); slide(at("f2", 3.5), 1100, 500, 0.4, 0.6); slide(at("f2", 4.5), 400, 900, 0.3, 0.6)
ding(at("f2", 0.5), 0.5, 2637)
for b in (1, 2, 3, 4, 5): squish(at("f3", b), 0.8)
for i in range(3): popfx(T[["f1", "f2", "f3"][i]], 0.5, 1000 + 200 * i)
# rare: breakdown (banjo + bass), dings for cards, flourish for the 3/3 card
banjo(T["rare"], T["stone"], 0.8, every=2); bass(T["rare"], T["stone"], 0.8)
for b in (0.5, 1.5): popfx(at("rare", b), 0.6); ding(at("rare", b), 0.35, 1760)
for j in range(3): ding(at("rare", 5 + j * 0.3), 0.45, [2093, 2637, 3136][j])
for j, m in enumerate([67, 71, 74, 79, 83]): add(gm("Fiddle", m, 0.15, 110, 0.05), at("rare", 4.5) + j * S16, 0.4, wet=0.3)
add(drum(49, 100), at("rare", 4.5), 0.3, wet=0.3); cluck(at("rare", 4.6), 0.7)
# stone: lite kit + rattling stomach
kit(T["stone"], T["fruit"], "lite", 0.8); bass(T["stone"], T["fruit"], 0.8); chop(T["stone"], T["fruit"], 0.8)
rattle(at("stone", 1), at("stone", 5.5) - at("stone", 1), 0.8)
for j in range(6): crunch(at("stone", 6) + j * 0.25, 0.5)
bagawk(at("stone", 6), 0.8)
# fruit + seed: full hoedown again
groove(T["fruit"], T["card"], 0.9)
for b, f in ((0.5, 1568), (3, 1976), (4, 2349)): popfx(at("fruit", b), 0.6); ding(at("fruit", b), 0.35, f)
squish(at("fruit", 5.5), 0.5)
for i in range(5): bloop(at("seed", 1 + i * 1.6), 0.6, 250 + i * 40, 700 + i * 60)
add(gm("Brass Section", 43, 0.3, 115), at("seed", 5), 0.45); add(gm("Brass Section", 42, 0.5, 110), at("seed", 5.5), 0.4)
# card: lite groove, chips pop
kit(T["card"], T["end"], "lite", 0.7); bass(T["card"], T["end"], 0.8); banjo(T["card"], T["end"], 0.7, every=2); chop(T["card"], T["end"], 0.7)
for i in range(3): popfx(at("card", 0.6 + i * 0.6), 0.6); add(gm("Harmonica", [74, 79, 83][i], 0.2, 100), at("card", 0.6 + i * 0.6), 0.45, wet=0.2)
ding(at("card", 2.6), 0.6, 3136)
# end: full band, then final G chord + bagawk
FINAL = at("end", 8)
groove(T["end"], FINAL, 0.9)
for m in (43, 55): add(gm("Acoustic Bass" if m < 50 else "Banjo", m, 1.5, 115, 0.5), FINAL, 0.9)
for j, m in enumerate((55, 59, 62, 67, 71, 74, 79)): add(gm("Banjo", m, 1.0, 110, 0.4), FINAL + j * 0.025, 0.35, wet=0.3)
add(gm("Fiddle", 79, 1.2, 110, 0.5), FINAL, 0.45, wet=0.3); add(brush(49, 90), FINAL, 0.3, wet=0.4); add(drum(36, 110), FINAL, 0.7)
bagawk(FINAL + 0.6, 1.0)

# ---------------- mix ----------------
def reverb(x, sec=1.6, dec=3.2):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * dec); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
d = int(3 * S16 * SR)
for r in range(1, 4):
    sh = ECHO[: N - d * r] * (0.4 ** r)
    MIX[d * r:, 0] += sh[:, 1] * (0.8 if r % 2 else 0.3); MIX[d * r:, 1] += sh[:, 0] * (0.3 if r % 2 else 0.8)
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
# tape stop HOOK_STOP -> HOOKCUT
i0, i1 = int(HOOK_STOP * SR), int(HOOKCUT * SR); n = i1 - i0
rate = np.linspace(1, 0.02, n) ** 1.4; p = i0 + np.cumsum(rate); p = np.clip(p, 0, N - 2); ii = p.astype(int); ff = (p - ii)[:, None]
seg = MIX[ii] * (1 - ff) + MIX[ii + 1] * ff; seg *= np.linspace(1, 0.3, n)[:, None]
MIX[i0:i1] = seg; MIX[i1:int((HOOKCUT + 0.08) * SR)] *= np.linspace(0.3, 1, int(0.08 * SR))[:, None]
for a, b in SILENCES:
    i0, i1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.04 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] = 0
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.2); MIX /= np.abs(MIX).max() / 0.85
fo = int(0.8 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("/workspace/work/hellchick/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG2 %.2f" % (BPM, DUR, BIG2))
