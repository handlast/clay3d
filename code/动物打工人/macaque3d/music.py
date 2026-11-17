# 《动物打工人 No.01》BGM (template from mantis) — "Hide & Seek in the Fern": E minor sneaky pizzicato + marimba + clock ticks, 120 BPM 4/4, ADAPTIVE (all times from cues.py).
# 0–3 s: countdown tick-tock + light pizz hits (no big hit). BIG1 = 3.0 s (butt wiggle) and BIG2 (extinct) are the ONLY two big hits.
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

# ---------------- music parts: "Jungle Office Funk" D dorian, 120 BPM ----------------
PROG = ["Dm7", "G7", "Dm7", "A7"]
CH = {"Dm7": (62, 65, 69, 72), "G7": (59, 62, 65, 67), "A7": (61, 64, 67, 69), "Bb": (58, 62, 65, 69)}
ROOT = {"Dm7": 38, "G7": 43, "A7": 45, "Bb": 46}
def chord_of(b): return PROG[b % 4]
BASSL = [(0, 0, 3), (3, 0, 1), (6, 12, 1), (7, 10, 1), (8, 7, 2), (10, 0, 1), (11, 3, 1), (14, 5, 2)]
def bass(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, iv, du in BASSL:
            if pos == k: add(gm("Finger Bass", ROOT[chord_of(b)] + iv, du * S16 * 0.9, 110 if k == 0 else 92, 0.05), tt, 0.55 * g)
CLAV = [2, 3, 6, 10, 11, 14]
def clav(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k in CLAV:
            for j, m in enumerate(CH[chord_of(b)][1:]): add(gm("Clavinet", m, S16 * 0.6, 88 if k % 4 == 2 else 70, 0.04), tt + j * 0.003, 0.09 * g, pan=-0.3)
def bongo(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k in (0, 3, 6, 8, 11, 14): add(drum(60 if k in (0, 8) else 61, 100 if k in (0, 8) else 80), tt, 0.35 * g, pan=0.35)
        if k in (4, 12): add(drum(63, 90), tt, 0.3 * g, pan=-0.2)
MEL = [[(0, 74, 2), (2, 77, 2), (4, 81, 3), (8, 79, 2), (10, 77, 2), (12, 74, 4)],
       [(0, 79, 3), (3, 77, 1), (4, 74, 2), (6, 71, 2), (8, 74, 6), (14, 77, 2)],
       [(0, 81, 2), (2, 84, 2), (4, 81, 2), (6, 77, 2), (8, 79, 4), (12, 77, 4)],
       [(0, 76, 2), (2, 79, 2), (4, 81, 2), (6, 85, 2), (8, 84, 4), (12, 81, 4)]]
def melody(t0, t1, g=1.0, up=0, inst="Marimba"):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m, du in MEL[b % 4]:
            if pos == k: add(gm(inst, m + up, du * S16, 105 if k % 4 == 0 else 90, 0.15), tt, (0.36 if inst == "Marimba" else 0.3) * g, pan=0.2, wet=0.25)
def kit(t0, t1, style="full", g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if style == "full":
            if k in (0, 7, 10): add(drum(36, 100), tt, 0.5 * g)
            if k in (4, 12): add(drum(38, 92), tt, 0.3 * g, wet=0.1)
        if k % 2 == 0: add(drum(42, 64 if k % 4 == 0 else 44), tt, 0.2 * g, pan=-0.3)
        if style == "lite" and k in (4, 12): add(drum(37, 85), tt, 0.25 * g)
def groove(t0, t1, g=1.0, mel=True, up=0, style="full", inst="Marimba"):
    bass(t0, t1, g); clav(t0, t1, g); bongo(t0, t1, g); kit(t0, t1, style, g)
    if mel: melody(t0, t1, g, up, inst)
def mar(t0, m, g=1.0): add(gm("Marimba", m, 0.35, 110, 0.2), t0, 0.5 * g, wet=0.25)
def kal(t0, m, g=1.0): add(gm("Kalimba", m, 0.4, 105, 0.3), t0, 0.4 * g, wet=0.3)
def glock(t0, m, g=1.0): add(gm("Glockenspiel", m, 0.4, 95, 0.3), t0, 0.28 * g, wet=0.35, echo=0.3)
def wood(t0, g=1.0, hi=True): add(drum(76 if hi else 77, 100), t0, 0.35 * g, pan=0.25 if hi else -0.25)
def epch(t0, ch, d=1.8, g=1.0):
    for j, m in enumerate(CH[ch]): add(gm("Tine Electric Piano", m, d, 72, 0.4), t0 + j * 0.01, 0.16 * g, wet=0.3)
def big(t0, g=1.0):
    boom(t0, 1.0 * g, 1.2); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 118), t0, 0.5 * g, wet=0.35)
    for m in (50, 57, 62, 65, 69): add(gm("Brass Section", m, 0.45, 122, 0.15), t0, 0.3 * g, wet=0.3)
    for m in (62, 69, 74): add(gm("Muted Trumpet", m, 0.35, 118, 0.15), t0 + 0.01, 0.25 * g, wet=0.3)
    for j, m in enumerate((69, 74, 77, 81, 86)): add(gm("Marimba", m, 0.3, 120, 0.2), t0 + 0.02 + j * 0.035, 0.32 * g, wet=0.3)
    add(gm("Finger Bass", 26, 0.7, 127, 0.15), t0, 0.9 * g)

# ---------------- arrangement ----------------
# 0–3 s hook: two monkeys bicker (bonk per bounce) + bongo patter + clav; riser into BIG1 (no big hit at 0)
whoosh(0.0, 0.3, 1.0, 600); popfx(0.02, 0.7, 1500, 500); mar(0.02, 74, 0.8)
bongo(0.0, BIG1, 0.9); clav(0.0, BIG1, 0.7); bass(0.0, BIG1, 0.6)
for j in range(8): add(gm("Melodic Tom", [50, 53][j % 2], 0.2, 100), 0.17 + j * math.pi / 9, 0.13, pan=-0.3 + 0.6 * (j % 2))
boing(0.6, 0.5, 0.4, 260, 0.5, 9); riser(1.6, BIG1 - 0.05, 0.8)
# BIG1: grooming / friends reveal
big(BIG1, 0.85); ding(BIG1 + 0.1, 0.6, 2637); chirp(BIG1 + 0.9, 0.5)
groove(BIG1, T["who"], 0.95, up=0)
for j in range(5): glock(BIG1 + 0.05 + j * 0.07, [86, 89, 93, 96, 98][j], 0.35)
# who: lite groove, pop per monkey, odometer ticks
bass(T["who"], T["timer"], 0.8); bongo(T["who"], T["timer"], 0.8); kit(T["who"], T["timer"], "lite", 0.7)
for i in range(5): popfx(T["who"] + 0.15 + i * 0.22, 0.6, 1100 + 120 * i); kal(T["who"] + 0.6 + i * 0.22, [74, 77, 81, 84, 86][i], 0.6)
for j in range(20): tick(T["who"] + 0.2 + 2.4 * (j / 20) ** 0.8, 0.45, 3400)
ding(T["who"] + 2.6, 0.45, 2349); chirp(T["who"] + 3.3, 0.4)
# timer: stopwatch tick-tock + bass/clav only
for j, tt in enumerate(np.arange(T["timer"], T["q"] - 0.01, BEAT)): wood(tt, 0.9, j % 2 == 0)
bass(T["timer"], T["q"], 0.75); clav(T["timer"], T["q"], 0.8)
popfx(T["timer"] + 0.1, 0.5); slide(T["timer"] + 0.8, 300, 900, 1.6, 0.5); slide(T["timer"] + 1.15, 300, 700, 1.6, 0.4)
ding(T["timer"] + 2.2, 0.4, 3136)
# q: breakdown – kalimba question motif, heartbeat, riser; dip at SIL0
for b in range(int((SIL0 - T["q"]) / BEAT)): add(drum(36, 70), T["q"] + b * BEAT, 0.28)
for j, m in enumerate([74, 77, 79, 81]): kal(T["q"] + 0.5 + j * 0.25, m, 0.6)
boing(T["q"] + 0.6, 0.4, 0.4, 350, 0.3, 5); boing(T["q"] + 0.85, 0.35, 0.4, 420, 0.3, 5); boing(T["q"] + 1.1, 0.3, 0.4, 500, 0.3, 5)
riser(T["q"] + 0.8, SIL0, 1.0); add(gm("Reverse Cymbal", 60, 1.4, 110), SIL0 - 1.4, 0.25)
# BIG2: friends win – bar origin reset
org(BIG2)
big(BIG2, 0.9)
groove(BIG2, T["rank"], 1.0, up=12)
for i in range(4): glock(BIG2 + 0.3 + i * 0.18, [86, 89, 93, 98][i], 0.5)
for i in range(3): ding(T["bond"] + 0.7 + i * 0.3, 0.3, [2349, 2794, 3136][i])
# rank: groove continues, hop slides
groove(T["rank"], T["mate"], 0.9, up=0, inst="Kalimba")
slide(T["rank"] + 0.5, 400, 900, 0.45, 0.7); slide(T["rank"] + 1.5, 500, 1200, 0.45, 0.7); ding(T["rank"] + 2.0, 0.55, 3136)
# mate: groove, bars rise, +20% ding
groove(T["mate"], T["fight"], 0.85, up=12)
slide(T["mate"] + 0.2, 200, 600, 1.0, 0.6); ding(T["mate"] + 1.4, 0.6, 3520); glock(T["mate"] + 1.5, 98, 0.5)
# fight: jungle toms + bass, no melody; "≠" boing
bass(T["fight"], T["why"], 0.8); bongo(T["fight"], T["why"], 0.9); kit(T["fight"], T["why"], "lite", 0.6)
for j in range(10): add(gm("Melodic Tom", [48, 52][j % 2], 0.2, 100), T["fight"] + 0.1 + j * math.pi / 9, 0.12, pan=-0.3 + 0.6 * (j % 2))
boing(T["fight"] + 2.2, 0.7, 0.6, 200, 0.6, 6); popfx(T["fight"] + 2.6, 0.5)
# why: sneaky – woodblock per stare, heartbeat
for b in range(int((T["card"] - T["why"]) / BEAT)): add(drum(36, 72), T["why"] + b * BEAT, 0.3)
bass(T["why"], T["card"], 0.6)
for i in range(4): wood(T["why"] + 0.6 + i * 0.35, 1.0, i % 2 == 0); whoosh(T["why"] + 0.6 + i * 0.35, 0.3, 0.5, 700)
popfx(T["why"] + 2.0, 0.5, 900, 300)
# card: calm – EP chords + kalimba, no drums
for j, ch in enumerate(["Dm7", "Bb", "G7", "A7"]): epch(T["card"] + j * 1.0, ch, 1.0)
glock(T["card"] + 0.1, 86); glock(T["card"] + 0.2, 93, 0.6)
# end: groove returns (lite), answer pops, final chord
FINAL = DUR - 1.4
groove(T["end"], FINAL, 0.75, style="lite")
popfx(T["end"] + 0.8, 0.6); popfx(T["end"] + 1.2, 0.6, 1400); boing(T["end"] + 3.4, 0.5, 0.5, 240, 0.5, 7)
for j, m in enumerate((38, 50, 57, 62, 65, 69, 74)): add(gm("Marimba" if m > 45 else "Finger Bass", m, 1.2, 105, 0.5), FINAL + j * 0.02, 0.4, wet=0.35)
add(drum(36, 100), FINAL, 0.5); add(drum(49, 70), FINAL, 0.2, wet=0.4)

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
with wave.open("/workspace/work/macaque3d/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG1 %.2f BIG2 %.2f" % (BPM, DUR, BIG1, BIG2))
