# 《果冻蛙》BGM — "Sulawesi Rain-Night Gamelan": pelog-flavoured (E F G B C), 120 BPM 4/4, 10% swing.
# Colotomic gamelan layer: Vibraphone balungan (quarter notes), Celeste peking (8ths), Kalimba bonang imbal (interlocking 16ths),
# synthesized gong ageng / kempul / kenong (inharmonic beating partials), kendang on bongo/conga; suling = Pan Flute / Shakuhachi.
# Rainforest night: continuous filtered rain bed + drips, frog chorus (synth croaks), jelly 'wobble' bloops, foam bubble pops.
# ADAPTIVE: every time comes from cues.py. BIG1 = 0.0 s and BIG2 ("一种新的飞蛙！") are the ONLY two big hits; bar origin resets at BIG2.
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
S16 = BEAT / 4; SW = 0.10 * S16
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


# ---------------- gamelan / rainforest SFX ----------------
def gong(t0, g=1.0, f=55.0, dur=5.0):
    t = tt_(dur); y = np.zeros_like(t)
    for k, (m, a, dk) in enumerate(((1.0, 1.0, 0.6), (1.005, 0.6, 0.6), (2.02, 0.45, 1.0), (2.96, 0.25, 1.6), (4.1, 0.12, 2.4), (5.4, 0.06, 3.0))):
        y += a * np.sin(2 * np.pi * f * m * t + k) * np.exp(-t * dk)
    y *= np.minimum(1, t / 0.012) * (1 + 0.15 * np.sin(2 * np.pi * 3.2 * t) * np.exp(-t))
    add(mono(y * 0.32), t0, g, wet=0.5, human=False)
def kempul(t0, g=1.0, f=110.0): gong(t0, 0.55 * g, f, 2.4)
def kenong(t0, g=1.0, f=330.0):
    t = tt_(1.6); y = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * d) for m, a, d in ((1, 1, 2.2), (2.7, 0.3, 5), (4.2, 0.15, 8)))
    add(mono(y * np.minimum(1, t / 0.004) * 0.12), t0, g, pan=0.2, wet=0.35, human=False)
def rainbed(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); nz = rng.standard_normal(n)
    hp = nz - np.convolve(nz, np.ones(6) / 6, "same"); lp = np.convolve(nz, np.ones(40) / 40, "same") * 3
    env = 0.8 + 0.2 * np.sin(2 * np.pi * 0.13 * np.arange(n) / SR)
    y = (hp * 0.5 + lp * 0.5) * env * 0.035
    fd = int(0.6 * SR); y[:fd] *= np.linspace(0, 1, fd); y[-fd:] *= np.linspace(1, 0, fd)
    add(np.stack([y, np.roll(y, 977)], 1), t0, g, human=False)
def drip(t0, g=1.0, f=None):
    f = f or rng.uniform(1400, 2600); t = tt_(0.12); ff = f * (1 + 0.6 * np.exp(-t * 60))
    add(mono(np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t * 45) * 0.18), t0, g, pan=rng.uniform(-0.6, 0.6), wet=0.4, human=False)
def drips(t0, t1, rate=1.5, g=1.0):
    tt = t0
    while True:
        tt += rng.exponential(1 / rate)
        if tt >= t1: break
        drip(tt, g * rng.uniform(0.4, 1.0))
def chorus(t0, t1, g=1.0, dens=6):
    tt = t0
    while True:
        tt += rng.exponential(1 / dens)
        if tt >= t1: break
        croak(tt, g * rng.uniform(0.3, 0.9), rng.uniform(380, 720))
def wobble(t0, g=1.0, d=0.5, f0=260):
    t = tt_(d); f = f0 * (1 + 0.35 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 5)) * (1 + 0.3 * t)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * np.minimum(1, t / 0.01)
    add(mono(y * 0.22), t0, g, wet=0.3, human=False)
def bubbles(t0, n=6, g=1.0, span=0.6):
    for j in range(n): bloop(t0 + rng.uniform(0, span), 0.35 * g, rng.uniform(500, 900), rng.uniform(1200, 2000), 0.07)

# ---------------- music parts (pelog-ish E F G B C) ----------------
BAL = [[67, 71, 72, 71, 67, 65, 64, 65], [64, 65, 67, 71, 72, 71, 67, 64], [71, 72, 76, 72, 71, 67, 65, 67], [72, 71, 67, 65, 64, 65, 67, 64]]
def beat_iter(t0, t1):
    """quarter-note grid from the current bar origin: (time, beat index within an 8-beat gatra, gatra number)"""
    out = []; o = origin(t0); b0 = int(math.floor((t0 - o) / BEAT)) - 1
    for b in range(max(-16, b0), b0 + 400):
        tt = o + b * BEAT
        if tt > t1 + 0.05: break
        if t0 - 1e-4 <= tt < t1 - 1e-4 and origin(tt) == o: out.append((tt, b % 8, b // 8))
    return out
def balungan(t0, t1, g=1.0):
    for tt, k, gt in beat_iter(t0, t1):
        m = BAL[gt % 4][k]; add(gm("Vibraphone", m - 12, 0.45, 104 if k % 2 else 92, 0.3), tt, 0.30 * g, pan=-0.15, wet=0.35)
def peking(t0, t1, g=1.0):
    for tt, k, gt in beat_iter(t0, t1):
        m = BAL[gt % 4][k]; n2 = BAL[gt % 4][(k + 1) % 8]
        add(gm("Celeste", m + 12, 0.2, 90, 0.2), tt, 0.16 * g, pan=0.3, wet=0.3); add(gm("Celeste", m + 12, 0.2, 76, 0.2), tt + BEAT / 2 + SW, 0.12 * g, pan=0.3, wet=0.3)
def bonang(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        gt = int((tt - origin(tt)) // (8 * BEAT)); bi = int(((tt - origin(tt)) // BEAT) % 8)
        m = BAL[gt % 4][bi]; n2 = BAL[gt % 4][(bi + 1) % 8]
        if k % 4 in (0, 2): add(gm("Kalimba", (m if k % 4 == 0 else n2) + 12, 0.18, 92, 0.15), tt, 0.20 * g, pan=-0.35, wet=0.2)
        else: add(gm("Kalimba", (n2 if k % 4 == 1 else m) + 19 - 7, 0.15, 74, 0.15), tt, 0.13 * g, pan=0.35, wet=0.2)
def colotomy(t0, t1, g=1.0):
    for tt, k, gt in beat_iter(t0, t1):
        if k == 7: gong(tt, 0.38 * g, 55 if gt % 2 else 61.7, 4.0)
        elif k == 3: kempul(tt, 0.55 * g, 110 if gt % 2 == 0 else 123.5)
        elif k in (1, 5): kenong(tt, 0.7 * g, 330 if k == 1 else 392)
KEND = {0: (64, 100), 3: (62, 70), 6: (63, 90), 8: (61, 80), 10: (60, 70), 11: (62, 60), 14: (63, 95)}
def kendang(t0, t1, g=1.0, kick=True):
    for tt, k, b in sixteenths(t0, t1):
        if k in KEND: n, v = KEND[k]; add(drum(n, v), tt, 0.32 * g, pan=-0.1 if n > 62 else 0.15, wet=0.12)
        if kick and k in (0, 8): add(drum(36, 96), tt, 0.38 * g)
        if kick and k in (4, 12): add(drum(39, 64), tt, 0.10 * g, wet=0.2)
        add(drum(70, 60 if k % 4 == 0 else 34), tt, 0.13 * g, pan=0.3)
def bassline(t0, t1, g=1.0):
    for tt, k, gt in beat_iter(t0, t1):
        if k % 2 == 0:
            m = BAL[gt % 4][k] % 12 + 36
            if m > 43: m -= 12
            add(gm("Fretless Bass", m, BEAT * 1.8, 108 if k == 0 else 92, 0.1), tt, 0.55 * g)
SUL = [[(0, 79, 4), (4, 77, 2), (6, 76, 2), (8, 79, 3), (11, 83, 1), (12, 84, 4)], [(0, 83, 3), (3, 79, 1), (4, 77, 4), (8, 76, 4), (12, 77, 2), (14, 79, 2)],
       [(0, 83, 4), (4, 84, 2), (6, 88, 2), (8, 84, 3), (11, 83, 1), (12, 79, 4)], [(0, 77, 2), (2, 79, 2), (4, 76, 4), (8, 77, 3), (11, 79, 1), (12, 76, 4)]]
def suling(t0, t1, g=1.0, inst="Pan Flute", dn=0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m, du in SUL[b % 4]:
            if pos == k: add(gm(inst, m - 12 + dn, du * S16 * 0.95, 100 if k % 4 == 0 else 88, 0.2), tt, 0.30 * g, pan=0.05, wet=0.5, echo=0.25)
def groove(t0, t1, g=1.0, mel=True, drums=True, kick=True, bon=True, pek=True, inst="Pan Flute"):
    balungan(t0, t1, g); colotomy(t0, t1, g); bassline(t0, t1, 0.9 * g)
    if pek: peking(t0, t1, g)
    if bon: bonang(t0, t1, 0.9 * g)
    if drums: kendang(t0, t1, g, kick)
    if mel: suling(t0, t1, g, inst)
def mar(t0, m, g=1.0): add(gm("Marimba", m, 0.35, 110, 0.2), t0, 0.4 * g, wet=0.25)
def glock(t0, m, g=1.0): add(gm("Glockenspiel", m, 0.4, 95, 0.3), t0, 0.26 * g, wet=0.35, echo=0.3)
def big(t0, g=1.0):
    boom(t0, 1.1 * g, 1.3); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 120), t0, 0.45 * g, wet=0.35)
    gong(t0, 1.3 * g, 55, 5.0); add(drum(64, 127), t0, 0.5 * g)
    for j, m in enumerate((64, 65, 67, 71, 72, 76, 79)): add(gm("Kalimba", m + 12, 0.25, 120, 0.2), t0 + 0.02 + j * 0.03, 0.28 * g, wet=0.3)
    for m in (52, 59, 64, 71): add(gm("Vibraphone", m, 0.8, 120, 0.4), t0, 0.22 * g, wet=0.4)
    add(gm("Fretless Bass", 28, 0.8, 127, 0.15), t0, 0.9 * g)

# ---------------- arrangement (butterfly) ----------------
def nx(k): return nxt(k)
drips(0.0, DUR, 0.6, 0.5)
# 1 hook — BIG1: three butterflies pop in; flutter pops
big(0.0, 1.0); whoosh(0.0, 1.0, 0.9, 300)
for i in range(3): popfx(-0.0 + 0.12 * i + 0.15, 0.6, 900 + 200 * i, 400)
for i in range(3): ding(0.9 + i * 0.6, 0.35, 2637 + 300 * i)
th = T["one"]; bonang(0.4, th, 0.7); balungan(0.4, th, 0.6)
# 2 one — drawer: pins tick, odometer roll
tl = T["one"]; groove(tl, nx("one"), 0.75, mel=False, drums=False)
for i in range(9): tick(tl + 0.15 + i * 0.12, 0.35, 2400 + 60 * i)
for i in range(16): tick(tl + 0.6 + 2.2 * (i / 16) ** 0.7, 0.2, 3000)
# 3 q — mystery: clock + riser into BIG2
tq = T["q"]; bonang(tq, SIL0, 0.6); clock(tq, SIL0, 0.7)
for i in range(3): bloop(tq + 0.3 + i * 0.25, 0.5, 300, 900, 0.2)
riser(tq + 0.3, SIL0, 0.9); add(gm("Reverse Cymbal", 60, 1.4, 110), SIL0 - 1.4, 0.25)
# 4 BIG2 — UV on: full groove; three glows = three rising slides
org(BIG2)
big(BIG2, 1.0)
for i in range(3): slide(BIG2 + 0.15 + i * 0.35, 500 + 150 * i, 1200 + 200 * i, 0.4, 0.35); glock(BIG2 + 0.2 + i * 0.35, 88 + 3 * i)
groove(BIG2, T["nm"], 1.0); ching(BIG2 + 1.2, 0.7)
# 5 nm — spectrometer: three pin dings + beeps
tn_ = T["nm"]; groove(tn_, nx("nm"), 0.8, mel=False, kick=False)
for j in range(3): ding(tn_ + 0.4 + j * 0.55, 0.5, [2637, 2349, 1976][j]); add(gm("Square Lead", [84, 82, 77][j], 0.08, 90), tn_ + 0.4 + j * 0.55, 0.05)
# 6 cat — munching: woodblock chews
tc_ = T["cat"]; groove(tc_, nx("cat"), 0.8, mel=True)
for j in range(8): add(drum(76 + j % 2, 100), tc_ + 1.6 + j * 0.2, 0.22)
for j in range(5): popfx(tc_ + 1.8 + j * 0.3, 0.3, 1600, 900)
# 7 marks — three lenses: marimba notes, the 'nothing' gets a boing
tm = T["marks"]; groove(tm, nx("marks"), 0.8, mel=False)
for i in range(3): mar(tm + 0.6 + i * 0.9, [64, 67, 71][i], 0.7)
boing(tm + 3.1, 0.5, 0.6, 200, 0.4, 7)
# 8 sepp — old book: quill scratches, ≠ stamp
ts = T["sepp"]; balungan(ts, nx("sepp"), 0.6); suling(ts, nx("sepp"), 0.6, "Shakuhachi"); peking(ts, nx("sepp"), 0.5)
for j in range(10): add(drum(70, 70), ts + 0.5 + j * 0.2, 0.15)
add(drum(41, 110), ts + 2.4, 0.3); popfx(ts + 0.1, 0.5, 900, 300)
# 9 no — heads shake: tom pairs; timeline roll
tno = T["no"]; groove(tno, nx("no"), 0.7, mel=False, kick=False)
for i in range(4): add(drum(45, 100), tno + 0.4 + i * 0.15, 0.2)
roll(tno + 0.5, tno + 3.4, 0.5)
# 10 y2001 — second slot: flutter whoosh, stamp
ty = T["y2001"]; groove(ty, nx("y2001"), 0.85, mel=True)
whoosh(ty + 0.2, 1.0, 0.6, 400); add(drum(41, 100), ty + 1.8, 0.3); ding(ty + 1.9, 0.6, 3136)
# 11 dna — barcode beeps, check
td = T["dna"]; groove(td, nx("dna"), 0.85, mel=False)
for i in range(3):
    for j in range(4): add(gm("Square Lead", 84 + i * 2, 0.05, 90), td + 0.5 + i * 0.4 + j * 0.07, 0.05)
ding(td + 2.4, 0.7, 3520); ching(td + 2.5, 0.6)
# 12 name — hide: soft suling, peek pop
tn = T["name"]; balungan(tn, nx("name"), 0.6); colotomy(tn, nx("name"), 0.7); suling(tn, nx("name"), 0.7, "Shakuhachi", -12)
slide(tn + 0.8, 800, 400, 0.8, 0.3); popfx(tn + 2.8, 0.5, 1200, 600)
# 13 same — one forest: groove + three X ticks
tsm = T["same"]; groove(tsm, nx("same"), 0.85, mel=True, kick=False)
for j in range(3): add(drum(76, 110), tsm + 1.6 + j * 0.3, 0.3)
# 14 end — back to the trio; final gong
FINAL = DUR - 1.4
te = T["end"]; groove(te, FINAL, 0.75, mel=True, kick=False)
for i in range(3): slide(te + 0.8 + i * 0.4, 600, 1100, 0.3, 0.2)
gong(FINAL, 1.0, 55, 4.0)
for j, m in enumerate((40, 52, 59, 64, 67, 71, 76)): add(gm("Vibraphone" if m > 50 else "Fretless Bass", m, 1.2, 105, 0.5), FINAL + j * 0.02, 0.35, wet=0.4)
add(gm("Pan Flute", 76, 1.3, 100, 0.4), FINAL, 0.25, wet=0.6)

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
with wave.open("/workspace/work/butterfly/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG1 %.2f BIG2 %.2f" % (BPM, DUR, BIG1, BIG2))
