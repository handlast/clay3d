# 《无声的边境》 score: 96 BPM, 4/4, A minor, built on the A–C–B motif. Sparse -> layered -> climax -> silence.
import sys, math, functools, wave, numpy as np
sys.path.insert(0, "/workspace/work/sf"); sys.path.insert(0, "/workspace/sfx")
from samp import piano as _piano, gm as _gm, SR
from sfx import sfx
from cues import *
N = int(SR * (DUR + 0.5)); MIX = np.zeros((N, 2)); VERB = np.zeros((N, 2))
rng = np.random.default_rng(3)
@functools.lru_cache(maxsize=None)
def _pk(name):
    return np.abs(_gm(name, 57, 1.0, 100)).max() + 1e-6
@functools.lru_cache(maxsize=None)
def gm(name, m, dur, vel=90, attack=None, release=0.4):
    return _gm(name, m, dur, vel, attack=attack, release=release) / _pk(name) * 0.3
def add(y, t0, g=1.0, wet=0.3, pan=0.0):
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = np.asarray(y)
    if y.ndim == 1: y = np.stack([y, y], 1)
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    MIX[i:i + len(y)] += y; VERB[i:i + len(y)] += y * wet
def bt(b): return b * BEAT          # beat index -> seconds
A2, C3, B2, E2, F2, G2, A1 = 45, 48, 47, 40, 41, 43, 33
tt = lambda d: np.arange(int(d * SR)) / SR

# ---------------- sound design ----------------
def drone(t0, t1, f=55.0, g=1.0):
    t = tt(t1 - t0); env = np.minimum(1, t / 3) * np.minimum(1, (t1 - t0 - t) / 3)
    y = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.003 * t) + 0.25 * np.sin(2 * np.pi * f * 3.01 * t)) * env
    y *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.11 * t); add(y * 0.10, t0, g, wet=0.4)
def thud(t0, g=1.0):
    t = tt(0.9); f = 34 + 40 * np.exp(-t * 18); y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    n = np.convolve(rng.standard_normal(len(t)), np.ones(60) / 60, "same") * np.exp(-t * 20) * 0.6
    add((y + n) * 0.5, t0, g, wet=0.5)
def grains(t0, d=0.6, g=1.0, n=14):
    for k in range(n):
        tk = t0 + rng.uniform(0, d) ** 1.5; L = int(0.006 * SR); c = rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4))
        c = np.convolve(c, [1, -1], "same"); add(c * 0.08 * rng.uniform(0.3, 1), tk, g, wet=0.15, pan=rng.uniform(-0.7, 0.7))
def rustle(t0, t1, g=1.0):
    t = tt(t1 - t0); n = rng.standard_normal(len(t)); n = np.convolve(n, [1, -1.6, 0.7], "same")
    am = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 7.3 * t) * np.sin(2 * np.pi * 3.1 * t))
    env = np.minimum(1, t / 1.5) * np.minimum(1, (t1 - t0 - t) / 1.5); add(n * am * env * 0.022, t0, g, wet=0.1)
def click(t0, g=1.0):
    L = int(0.012 * SR); c = rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 6)); c = np.convolve(c, [1, -0.9], "same")
    add(c * 0.12, t0, g, wet=0.2, pan=rng.uniform(-0.5, 0.5))
def amb(t0, t1, g=1.0, start=10.0):
    y = sfx(273, start=start, dur=t1 - t0, norm=True); env = np.minimum(1, np.arange(len(y)) / SR / 2) * np.minimum(1, (len(y) / SR - np.arange(len(y)) / SR) / 2)
    add(y * env * 0.10, t0, g, wet=0.05)
def wind(t0, t1, g=1.0):
    y = sfx(184, start=20.0, dur=t1 - t0, norm=True); n = len(y); e = np.minimum(1, np.arange(n) / SR / 2.5) * np.minimum(1, (n - np.arange(n)) / SR / 2.5)
    y = np.convolve(y, np.ones(12) / 12, "same"); add(y * e * 0.09, t0, g, wet=0.1)
def boom(t0, g=1.0, which=209):
    add(sfx(which, dur=6.0) * 0.55, t0, g, wet=0.2)

# ---------------- instruments ----------------
def strings_chord(t0, notes, d, vel=70, g=1.0, inst="Slow Strings"):
    for m in notes: add(gm(inst, m, d, vel, attack=0.6, release=1.2), t0, g * 0.5, wet=0.45)
def cello(t0, m, d, vel=85, g=1.0): add(gm("Cello", m, d, vel, attack=0.15, release=0.8), t0, g * 0.8, wet=0.35, pan=-0.2)
def bass(t0, m, d, vel=85, g=1.0): add(gm("Tuba", m, d, vel, attack=0.2, release=0.6), t0, g * 0.25, wet=0.3); add(gm("Cello", m, d, vel, attack=0.1, release=0.6), t0, g * 0.45, wet=0.3)
def horns(t0, m, d, vel=85, g=1.0):
    add(gm("French Horns", m, d, vel, attack=0.12, release=0.8), t0, g * 0.6, wet=0.45, pan=0.15)
def trombones(t0, m, d, vel=90, g=1.0): add(gm("Trombone", m, d, vel, attack=0.06, release=0.5), t0, g * 0.45, wet=0.4, pan=-0.1)
def stacc(t0, m, vel=95, g=1.0, inst="Fast Strings"): add(gm(inst, m, 0.16, vel, release=0.12), t0, g * 0.55, wet=0.25)
def taiko(t0, vel=100, g=1.0): add(gm("Taiko Drum", 36, 0.9, vel, release=0.5), t0, g * 0.9, wet=0.35)
def timp(t0, m=A1 + 12, vel=100, g=1.0, roll=0.0):
    if roll:
        n = int(roll / 0.06)
        for k in range(n): add(gm("Timpani", m, 0.3, int(40 + 60 * k / n)), t0 + k * 0.06, g * 0.5, wet=0.4)
    else: add(gm("Timpani", m, 1.6, vel, release=1.0), t0, g * 0.9, wet=0.4)
def pno(t0, m, d=2.0, vel=55, g=1.0): add(_piano(m, d, vel), t0, g * 3.2, wet=0.5)
def choir(t0, notes, d, vel=60, g=1.0):
    for m in notes: add(gm("Concert Choir", m, d, vel, attack=1.2, release=1.5), t0, g * 0.25, wet=0.6)

AM, FM, EM, CM, DM, GM = [45, 52, 57, 60], [41, 48, 53, 57], [40, 47, 52, 56], [36, 48, 52, 55], [38, 50, 53, 57], [43, 50, 55, 59]
PROG = [AM, FM, EM, AM]
def motif(t0, base, fn, step=2, last=4, **kw):     # A–C–B
    fn(t0, base, bt(step), **kw); fn(t0 + bt(step), base + 3, bt(step), **kw); fn(t0 + bt(2 * step), base + 2, bt(last), **kw)

# ---------------- 0–15: under the ground ----------------
drone(0.0, 16.0, 55.0, 1.0); amb(0.0, 36.0, 0.9)
for st in STEPS: thud(st, 0.9); grains(st + 0.03, 0.4, 0.8, 18)
grains(11.2, 3.5, 0.5, 30)
add(gm("Contrabass" if False else "Cello", A1, 10.0, 60, attack=3.0, release=3.0), 4.0, 0.35, wet=0.6)

# ---------------- 15–35: an empire across continents ----------------
drone(14.0, 36.0, 55.0, 0.6)
for k, ch in enumerate(PROG * 2):
    strings_chord(15.0 + k * BAR, ch, BAR + 0.2, 52 + 3 * k, 0.9)
for r in range(3):
    motif(17.5 + r * 2 * BAR * 1.0 + (0 if r < 2 else 0), 57, cello, step=2, last=4, vel=72 + 6 * r)
motif(30.0, 69, lambda t, m, d, **k: add(gm("Violin", m, d, 60, attack=0.3, release=1.0), t, 0.35, wet=0.55), step=2, last=4)

# ---------------- 35–55: the border ----------------
for k, ch in enumerate([AM, FM, DM, EM, AM, FM, DM, EM]):
    strings_chord(35.0 + k * BAR, [n - 12 for n in ch[:2]] + ch[2:], BAR + 0.2, 60, 0.9)
    bass(35.0 + k * BAR, ch[0] - 12 if ch[0] > 40 else ch[0], BAR, 80, 0.9)
for k in range(8):
    taiko(35.0 + k * BAR, 80 + 3 * k, 0.6); timp(35.0 + k * BAR + bt(3), A1 + 12 if k % 2 == 0 else E2, 70, 0.5)
motif(40.0, 57, horns, step=2, last=4, vel=70); motif(50.0, 57, horns, step=2, last=4, vel=80)
amb(36.0, 60.0, 0.6, start=40.0)

# ---------------- 55–75: first contact ----------------
add(gm("Tremolo Strings", A2, 5.0, 55, attack=1.5, release=0.3), 55.0, 0.35, wet=0.4)
add(gm("Tremolo Strings", B2, 5.0, 55, attack=1.5, release=0.3), 55.0, 0.25, wet=0.4)
for k in range(4): taiko(55.0 + k * bt(2), 70 + 5 * k, 0.5)
# TOUCH: everything stops; only a high suspended harmonic + antenna ticks
add(gm("Violin", 81, 4.6, 40, attack=1.0, release=0.5), TOUCH + 0.2, 0.3, wet=0.7)
for k in range(10): click(TOUCH + 0.15 + k * 0.42 + rng.uniform(0, 0.1), 0.35)
# BITE
boom(BITE, 1.0, 209); timp(BITE, A1 + 12, 120, 0.8); click(BITE, 1.2); click(BITE + 0.04, 1.0)
for b in range(int((75 - BITE - 0.6) / bt(0.5))):
    tb = BITE + 0.6 + b * bt(0.5); seq = [57, 60, 59, 57]
    stacc(tb, seq[b % 4] - 12, 80 + min(30, b), 0.8 + 0.01 * b)
for k in range(4): strings_chord(BITE + k * BAR, [n - 12 for n in [AM, FM, EM, AM][k][:2]], BAR, 65, 0.8)
rustle(BITE + 0.5, 75.0, 0.8)
for k in range(30): click(BITE + 0.6 + rng.uniform(0, 9.5), 0.5)

# ---------------- 75–110: countless small battlefields ----------------
rustle(75.0, 110.0, 1.0)
for k in range(110): click(75.0 + rng.uniform(0, 35), rng.uniform(0.3, 0.8))
for k in range(int((110 - 75) / BAR)):
    t0 = 75.0 + k * BAR; ch = [AM, FM, DM, EM][k % 4]; inten = k / 13.0
    strings_chord(t0, [n - 12 for n in ch[:2]] + ch[2:], BAR + 0.1, int(65 + 30 * inten), 0.9)
    bass(t0, ch[0] - 12 if ch[0] > 40 else ch[0], bt(2), 90, 0.9); bass(t0 + bt(2), ch[0] - 12 if ch[0] > 40 else ch[0], bt(2), 90, 0.8)
    for s in range(8):      # staccato ostinato on the motif
        stacc(t0 + s * bt(0.5), [57, 60, 59, 57, 52, 57, 60, 59][s] - 12, int(85 + 30 * inten), 0.8 + 0.3 * inten)
    # drums: sparse -> 8ths -> 16th fills
    pat = [0, 2.5] if k < 4 else ([0, 1.5, 2, 3] if k < 9 else [0, 0.5, 1.5, 2, 2.5, 3, 3.5])
    for p in pat: taiko(t0 + bt(p), int(85 + 35 * inten), 0.7 + 0.3 * inten)
    timp(t0, A1 + 12 if k % 2 == 0 else E2, int(80 + 30 * inten), 0.5 + 0.3 * inten)
    if k >= 10: timp(t0 + bt(3), E2, 100, 0.6, roll=bt(1) if k % 2 else 0)
for r, t0 in enumerate([80.0, 87.5, 92.5, 97.5, 102.5, 105.0]):
    motif(t0, 57 if r < 3 else 60 - 3, horns, step=2, last=4, vel=80 + 8 * r, g=0.8 + 0.12 * r)
    if r >= 2: motif(t0, 45, trombones, step=2, last=4, vel=90 + 6 * r, g=0.6 + 0.1 * r)
choir(100.0, [57, 60, 64], BAR * 4, 70, 0.9)
timp(107.5, A1 + 12, 120, 0.8, roll=2.2)

# ---------------- 110–134: the cost ----------------
strings_chord(110.0, [33, 45], BAR * 4, 55, 0.9); strings_chord(120.0, [29, 41], BAR * 2, 50, 0.8); strings_chord(125.0, [28, 40], BAR * 2, 45, 0.8)
strings_chord(130.0, [33, 45], BAR * 2, 42, 0.7)
for k, (tb, m) in enumerate([(111.25, 69), (112.5, 72), (113.75, 71), (117.5, 64), (118.75, 67), (120.0, 65), (123.75, 69), (125.0, 72), (126.25, 71), (130.0, 64)]):
    pno(tb, m, 3.0, 50 - k, 1.0)
wind(110.0, 134.5, 0.5); drone(111.0, 134.0, 55.0, 0.3)

# ---------------- 134–152.5: the next encounter ----------------
amb(134.0, 152.5, 0.7, start=60.0); wind(134.0, 152.5, 0.7)
strings_chord(134.0, [45, 52], BAR * 3, 40, 0.7); strings_chord(141.5, [41, 48], BAR * 2, 38, 0.6)
pno(139.0, 57, 3, 40); pno(140.25, 60, 3, 40); pno(141.5, 59, 3, 38)
# final motif: A – C – B, the B hangs unresolved through the cut, then only wind
add(gm("Cello", 57, bt(2), 70, attack=0.2, release=0.6), 143.75, 0.8, wet=0.5); pno(143.75, 69, 2.5, 48)
add(gm("Cello", 60, bt(2), 70, attack=0.2, release=0.6), 145.0, 0.8, wet=0.5); pno(145.0, 72, 2.5, 48)
add(gm("Cello", 59, 4.5, 68, attack=0.2, release=2.0), 146.25, 0.8, wet=0.6); pno(146.25, 71, 5.0, 46)
add(gm("Violin", 83, 4.5, 30, attack=1.0, release=2.0), 146.25, 0.12, wet=0.8)

# ---------------- mix ----------------
def reverb(x, sec=2.6, dec=2.4):
    n = int(sec * SR); t = np.arange(n) / SR; ir = rng.standard_normal(n) * np.exp(-t * dec); ir = np.convolve(ir, np.ones(10) / 10, "same"); ir /= np.abs(ir).sum() ** 0.5 * 9
    sz = 1 << int(np.ceil(np.log2(len(x) + n))); return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.55
# duck everything except the touch-silence (60–65): kill drum tails there
i0, i1 = int(TOUCH * SR), int((BITE - 0.02) * SR)
MIX[i0:i1] *= 1.0
MIX = MIX[: int(DUR * SR)]
MIX = np.tanh(MIX / np.abs(MIX).max() * 1.6); MIX /= np.abs(MIX).max() / 0.9
with wave.open("/workspace/work/border/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 5) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR) - 4, 5)]
print("RMS/5s:", " ".join(f"{i*5}:{v:.0f}" for i, v in enumerate(r)))
