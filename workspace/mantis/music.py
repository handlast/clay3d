# 《叶子屁股螳螂》BGM — "Hide & Seek in the Fern": E minor sneaky pizzicato + marimba + clock ticks, 120 BPM 4/4, ADAPTIVE (all times from cues.py).
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
# ---------------- music parts (E minor, sneaky) ----------------
PROG = ["Em", "Em", "C", "B7"]
CH = {"Em": (52, 55, 59, 64), "C": (52, 55, 60, 64), "B7": (51, 54, 57, 59), "Am": (52, 57, 60, 64)}
ROOT = {"Em": 40, "C": 36, "B7": 35, "Am": 45}
def chord_of(b): return PROG[b % 4]
SNEAK = [(0, 0), (3, 3), (4, 7), (6, 8), (8, 7), (11, 3), (12, 0), (14, -1)]     # pizz tiptoe (semitones over root)
def pizz(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, iv in SNEAK:
            if pos == k:
                r = ROOT[chord_of(b)] + 12
                add(gm("Pizzicato Strings", r + iv, 0.2, 100 if k % 4 == 0 else 84), tt, 0.42 * g, pan=-0.15, wet=0.2)
def bass(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        r = ROOT[chord_of(b)]
        if k == 0: add(gm("Acoustic Bass", r, BEAT * 0.8, 108, 0.05), tt, 0.6 * g)
        if k == 8: add(gm("Acoustic Bass", r + 7, BEAT * 0.8, 100, 0.05), tt, 0.5 * g)
MEL = [[(0, 76, 2), (2, 79, 2), (4, 81, 2), (6, 79, 2), (8, 76, 4), (12, 74, 2), (14, 71, 2)],
       [(0, 76, 3), (3, 74, 1), (4, 71, 4), (8, 67, 2), (10, 69, 2), (12, 71, 4)],
       [(0, 72, 2), (2, 76, 2), (4, 79, 2), (6, 84, 2), (8, 83, 4), (12, 79, 4)],
       [(0, 78, 2), (2, 75, 2), (4, 71, 2), (6, 75, 2), (8, 78, 6), (14, 81, 2)]]
def marimba(t0, t1, g=1.0, up=0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m, du in MEL[b % 4]:
            if pos == k: add(gm("Marimba", m + up, du * S16, 105 if k % 4 == 0 else 92, 0.15), tt, 0.38 * g, pan=0.2, wet=0.25)
def comp(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k in (4, 12):
            for j, m in enumerate(CH[chord_of(b)]): add(gm("Marimba", m, 0.15, 80, 0.1), tt + j * 0.004, 0.12 * g, pan=-0.25)
def kit(t0, t1, style="full", g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if style == "full":
            if k in (0, 10): add(drum(36, 100), tt, 0.5 * g)
            if k in (4, 12): add(drum(37, 95), tt, 0.35 * g, wet=0.1)
        if style in ("full", "lite"):
            if k % 2 == 0: add(drum(70, 70 if k % 4 == 0 else 45), tt, 0.25 * g, pan=-0.3)
            if k in (2, 7, 10, 15): add(drum(76 if k % 4 == 2 else 77, 90), tt, 0.25 * g, pan=0.3)
def groove(t0, t1, g=1.0, mel=True, up=0, style="full"):
    pizz(t0, t1, g); bass(t0, t1, g); comp(t0, t1, g); kit(t0, t1, style, g)
    if mel: marimba(t0, t1, g, up)
def mar(t0, m, g=1.0): add(gm("Marimba", m, 0.35, 110, 0.2), t0, 0.5 * g, wet=0.25)
def glock(t0, m, g=1.0): add(gm("Glockenspiel", m, 0.4, 95, 0.3), t0, 0.28 * g, wet=0.35, echo=0.3)
def big(t0, g=1.0):
    boom(t0, 1.1 * g, 1.3); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 120), t0, 0.55 * g, wet=0.35); add(drum(57, 110), t0 + 0.01, 0.3 * g, pan=0.4)
    for m in (40, 52, 59, 64, 67, 71): add(gm("Pizzicato Strings", m, 0.4, 125, 0.2), t0, 0.35 * g, wet=0.3)
    for m in (52, 59, 64): add(gm("Brass Section", m, 0.4, 120, 0.15), t0, 0.32 * g, wet=0.3)
    for j, m in enumerate((64, 67, 71, 76, 79, 83)): add(gm("Marimba", m, 0.3, 120, 0.2), t0 + 0.02 + j * 0.035, 0.35 * g, wet=0.3)
    add(gm("Acoustic Bass", 28, 0.7, 127, 0.15), t0, 1.0 * g)

# ---------------- arrangement ----------------
# 0–3 s: countdown — tick-tock clock, light pizz tiptoe, marimba note per digit (no big hit)
whoosh(0.0, 0.3, 1.0, 600)
clock(0.0, BIG1)
for i, c in enumerate(COUNT):
    mar(c, [71, 74, 78][i], 0.9); popfx(c, 0.5, 1400, 500); add(drum(75, 100), c, 0.3)
for j in range(12): add(gm("Pizzicato Strings", [52, 55, 57, 58, 59, 58, 57, 55][j % 8], 0.18, 90), j * 0.25, 0.32, pan=-0.1, wet=0.15)
riser(1.8, BIG1 - 0.05, 0.8)
# BIG1: butt wiggle reveal
big(BIG1, 0.85); boing(BIG1 + 0.02, 1.2, 0.9, 170, 0.6, 7); boing(BIG1 + 1.6, 0.6, 0.5, 220, 0.5, 7)
groove(BIG1, T["lobes"], 0.95, up=12)
# lobes: one marimba note per highlighted flap (top -> tip), lite kit
pizz(T["lobes"], T["bird"], 0.8); bass(T["lobes"], T["bird"], 0.8); kit(T["lobes"], T["bird"], "lite", 0.8)
for i in range(7): mar(T["lobes"] + 0.6 + i * 0.22, [64, 67, 71, 74, 76, 79, 83][i], 0.7)
popfx(at("lobes", 0.7), 0.5); popfx(at("lobes", 1.2), 0.5); glock(T["lobes"] + 2.2, 88, 0.7)
# bird: band drops to pizz tiptoe; chirps, "?" boing, gnat buzz, snap
pizz(T["bird"], T["amber"], 0.9); kit(T["bird"], T["amber"], "lite", 0.6)
whoosh(T["bird"], 0.5, 0.9, 300); chirp(T["bird"] + 0.5, 1.0); boing(T["bird"] + 0.85, 0.5, 0.4, 400, 0.3, 5); chirp(T["bird"] + 1.5, 0.8)
whoosh(T["bird"] + 2.0, 0.6, 0.8, 300); buzz(T["bird"] + 1.8, T["bird"] + 2.9, 1.0); snap(T["bird"] + 2.85, 1.0); mar(T["bird"] + 3.0, 83, 0.6)
# amber: resin drip bloop, glass glock shimmer, odometer ticks speeding up
bloop(T["amber"] + 0.1, 1.0, 600, 200, 0.3); bloop(T["amber"] + 0.5, 0.8, 500, 160, 0.4)
bass(T["amber"], T["q"], 0.7); comp(T["amber"], T["q"], 0.8)
for j in range(16): tick(T["amber"] + 0.6 + 1.6 * (j / 16) ** 0.8, 0.6, 3600)
glock(T["amber"] + 2.2, 88); glock(T["amber"] + 2.3, 95, 0.7); popfx(T["amber"] + 2.3, 0.5)
# q: heartbeat clock + riser, brief dip at SIL0
clock(T["q"], SIL0, 0.9); pizz(T["q"], SIL0, 0.6)
for b in range(int((SIL0 - T["q"]) / BEAT)): add(drum(36, 70), T["q"] + b * BEAT, 0.3)
boing(T["q"] + 0.3, 0.4, 0.4, 350, 0.3, 5)
riser(T["q"] + 0.5, SIL0, 1.0); add(gm("Reverse Cymbal", 60, 1.4, 110), SIL0 - 1.4, 0.25)
# BIG2: extinct!  bar origin reset here
org(BIG2)
big(BIG2, 0.9)
groove(BIG2, T["none"], 1.0, up=0)
add(gm("Tuba", 40, 0.4, 110), at("big2", 3.2), 0.6); add(gm("Tuba", 39, 0.4, 110), at("big2", 3.6), 0.6); add(gm("Tuba", 38, 1.0, 110), at("big2", 4.0), 0.6)
slide(BIG2 + 1.6, 600, 200, 0.6, 0.8); rattle(BIG2 + 1.9, 1.2, 0.6)
# none: lite, pops for each mantis and bubble
pizz(T["none"], T["match"], 0.85); bass(T["none"], T["match"], 0.8); kit(T["none"], T["match"], "lite", 0.7)
for i in range(3): popfx(T["none"] + 0.2 + i * 0.25, 0.5, 1000 + 200 * i); mar(T["none"] + 1.2 + i * 0.2, [76, 79, 83][i], 0.4)
glock(T["none"] + 2.0, 88, 0.6)
# match: full groove + dings on checks
groove(T["match"], T["first"], 0.85)
for i in range(3): ding(T["match"] + 1.2 + i * 0.9, 0.5, [2093, 2637, 3136][i])
# first: full groove, melody up, crown ding
groove(T["first"], T["rear"], 0.9, up=12)
ding(T["first"] + 1.6, 0.6, 3136); glock(T["first"] + 1.7, 95, 0.6)
# rear: breakdown — pizz + bass only, boings on wiggles, whoosh on arrow
pizz(T["rear"], T["card"], 0.8); bass(T["rear"], T["card"], 0.7)
boing(T["rear"] + 0.5, 0.8, 0.8, 200, 0.6, 5); boing(T["rear"] + 2.6, 0.6, 0.6, 240, 0.5, 5); whoosh(T["rear"] + 1.9, 0.6, 0.8, 500)
# card: lite + glock sparkle
kit(T["card"], T["end"], "lite", 0.7); pizz(T["card"], T["end"], 0.7); comp(T["card"], T["end"], 0.8); bass(T["card"], T["end"], 0.7)
glock(T["card"] + 0.1, 88); glock(T["card"] + 0.2, 95, 0.6)
for i in range(2): popfx(T["card"] + 1.2 + i * 0.5, 0.5)
# end: clock tick-tock back (match the hook), light groove, final chord
FINAL = DUR - 1.4
clock(T["end"], FINAL, 0.8); pizz(T["end"], FINAL, 0.75); marimba(T["end"], FINAL, 0.6)
boing(T["end"] + 1.2, 0.6, 0.6, 200, 0.5, 7); popfx(T["end"] + 0.2, 0.6)
for j, m in enumerate((40, 52, 59, 64, 67, 71, 76)): add(gm("Marimba" if m > 50 else "Acoustic Bass", m, 1.2, 105, 0.5), FINAL + j * 0.02, 0.4, wet=0.35)
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
with wave.open("/workspace/work/mantis/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG1 %.2f BIG2 %.2f" % (BPM, DUR, BIG1, BIG2))
