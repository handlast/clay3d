# WEB-BUG BGM — 'creepy-cute web tango' in D minor, 97.96 BPM: habanera bass (pizz + bassoon), harpsichord comp,
# plucked-web harp motif (each silk thread = a note), claves/maracas, music box. Big hits ONLY at 0.4 s and BIG2. No vocals.
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import piano as _piano, gm as _gm, drum as _drum, SR
from cues import *
N = int(SR * DUR)
# measured peaks @vel100: Acoustic Bass .79, Vibraphone .41, Muted Trumpet .65, Brass 1.47, Orch Hit 1.55, hat42 1.27, woodblock 4.8, piano .04
LV = {"Acoustic Bass": 1.0, "Vibraphone": 2.0, "Pizzicato Strings": 1.0, "Bassoon": 1.0, "Harpsichord": 1.0, "Orchestral Harp": 1.0, "Music Box": 1.0, "Brass Section": 0.55}
DLV = {42: 0.6, 46: 0.9, 76: 0.17, 77: 0.17, 75: 0.3, 70: 0.5}
SWAP = {}
KIT = "Room"
@functools.lru_cache(maxsize=None)
def _pk_inst(name, new):
    a = np.abs(_gm(name, 60, 0.5, 100, release=0.2)).max(); b = np.abs(_gm(new, 60, 0.5, 100, release=0.2)).max() + 1e-6; return a / b
@functools.lru_cache(maxsize=None)
def gm(name, m, dur=0.5, vel=100, release=0.2, decay=None):
    new = SWAP.get(name, name)
    return _gm(new, m, dur, vel, release=release, decay=decay) * _pk_inst(name, new) * LV.get(name, 1.0)
@functools.lru_cache(maxsize=None)
def _pk_dr(n):
    a = np.abs(_drum(n, 100)).max(); b = np.abs(_drum(n, 100, kit=KIT)).max() + 1e-6; return a / b
@functools.lru_cache(maxsize=None)
def drum(n, vel=100): return _drum(n, vel, kit=KIT) * _pk_dr(n) * DLV.get(n, 1.0)
_EPK = None
@functools.lru_cache(maxsize=None)
def piano(m, dur=0.4, vel=60):   # piano stabs -> Chorused Tine EP, matched to the piano's peak
    global _EPK
    if _EPK is None: _EPK = np.abs(_piano(60, 0.4, 60)).max() * 12 / (np.abs(_gm("Tine Electric Piano", 60, 0.4, 60)).max() + 1e-6)
    return _gm("Tine Electric Piano", m, dur, vel) * _EPK
N = int(SR * DUR); MIX = np.zeros((N, 2)); VERB = np.zeros((N, 2)); ECHO = np.zeros((N, 2))
rng = np.random.default_rng(11)
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
S16 = BEAT / 4; SW = 0.2 * S16   # 16th swing
# ---------------- grid ----------------
def bar_of(t): return int(math.floor((t - G0) / BAR + 1e-6))
def sixteenths(t0, t1):
    out = []
    b0 = max(0, bar_of(t0) - 1)
    for b in range(b0, bar_of(t1) + 2):
        for k in range(16):
            tt = G0 + b * BAR + k * S16
            if t0 - 1e-4 <= tt < t1 - 1e-4: out.append((tt + (SW if k % 2 else 0), k, b))
    return out
# ---------------- synth one-shots ----------------
def boom(t0, g=1.0, dur=1.1):
    t = tt_(dur); f = 38 + 80 * np.exp(-t * 16)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2) * 0.9), t0, g, human=False)
def thump(t0, g=1.0, f0=52):
    t = tt_(0.3); f = f0 + 40 * np.exp(-t * 30)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12) * 0.8), t0, g, human=False)
def tick(t0, g=1.0, f=3200):
    t = tt_(0.04); y = np.sin(2 * np.pi * f * t) * np.exp(-t * 160) + rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.4
    add(mono(y * 0.35), t0, g, pan=0.2, human=False)
def click(t0, g=1.0):
    t = tt_(0.03); add(mono(rng.standard_normal(len(t)) * np.exp(-t * 300) * 0.5), t0, g, human=False)
def whoosh(t0, d=0.35, g=1.0, f0=400, f1=2400):
    n = int(d * SR); t = np.arange(n) / SR
    nz = rng.standard_normal(n); k = max(2, int(SR / f0 / 2))
    y = nz - np.convolve(nz, np.ones(k) / k, "same"); y = np.convolve(y, np.ones(3) / 3, "same")
    add(mono(y * np.sin(np.pi * t / d) ** 2 * 0.12), t0, g, human=False)
def popfx(t0, g=1.0, f0=1200, f1=300):
    t = tt_(0.09); f = f1 + (f0 - f1) * np.exp(-t * 60)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.32), t0, g, human=False)
def sonar(t0, g=1.0):
    t = tt_(0.5); f = 2400 * np.exp(-t * 6) + 300
    n = np.random.RandomState(int(t0 * 100)).randn(len(t)) * 0.15
    y = (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + n) * np.minimum(1, t / 0.01) * np.exp(-t * 7)
    add(mono(y * 0.35), t0, g, wet=0.5, echo=0.3, human=False)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T = t1 - t0
    y = np.convolve(rng.standard_normal(n), np.ones(5) / 5, "same") * (t / T) ** 2.5 * 0.07
    f = 180 * (1600 / 180) ** (t / T); y += np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / T) ** 2 * 0.04
    add(mono(y), t0, g, human=False)
def ctbuzz(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T = t1 - t0
    ph = np.cumsum(np.full(n, 110.0) * (1 + 0.5 * t / T)) / SR
    y = (2 * (ph % 1) - 1) * 0.5 + np.convolve(rng.standard_normal(n), np.ones(3) / 3, "same") * 0.3
    y *= (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t)) * np.minimum(1, t / 0.05) * np.minimum(1, (T - t) / 0.05)
    add(mono(y * 0.07), t0, g, pan=-0.2, human=False)
def shutter(t0, g=1.0):
    for dt, gg in ((0, 1.0), (0.07, 0.7)):
        t = tt_(0.05); y = np.convolve(rng.standard_normal(len(t)), np.ones(4) / 4, "same") * np.exp(-t * 120)
        add(mono(y * 0.9), t0 + dt, g * gg, human=False)
def drawer_fx(t0, g=1.0):
    n = int(0.3 * SR); t = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(30) / 30, "same") * 3 * (0.5 + 0.5 * np.sin(2 * np.pi * 38 * t) ** 2) * np.sin(np.pi * t / 0.3)
    add(mono(y * 0.25), t0 - 0.3, g, human=False)
    click(t0, 1.4 * g); click(t0 + 0.05, 0.9 * g); thump(t0, 0.5 * g, 90)
# record scratch: a rich "ahh" source read with a back-and-forth hand motion, fader-gated
_src_t = np.arange(int(0.8 * SR)) / SR
_f0 = 1400 * (1 - 0.7 * (_src_t / 0.8)); _ph = np.cumsum(_f0) / SR
_SRC = (np.sin(2 * np.pi * _ph) * 0.4 + np.convolve(rng.standard_normal(len(_src_t)), np.ones(8) / 8, "same") * 1.2)
_SRC *= 0.25
def scratch(t0, strokes=((0.11, 0.18), (0.11, -0.18), (0.08, 0.14), (0.08, -0.14)), g=1.0):
    pos = 0.3; out = []
    for d, amt in strokes:
        n = int(d * SR); u = np.arange(n) / n
        p = pos + amt * (0.5 - 0.5 * np.cos(np.pi * u))
        idx = np.clip(p * SR, 0, len(_SRC) - 2); i = idx.astype(int); f = idx - i
        seg = (_SRC[i] * (1 - f) + _SRC[i + 1] * f) * np.sin(np.pi * u) ** 0.5 * np.abs(np.gradient(p)) * SR / 1.6
        out.append(seg); pos += amt
    y = np.concatenate(out); y = np.clip(y, -1, 1)
    add(mono(y * 0.35), t0, g, pan=0.15, wet=0.15, human=False)
def glide_note(name, m, dur, semis, gl, vel=105):
    """note that slides up from m-semis to m over the first gl seconds"""
    y = gm(name, m, dur + 0.3, vel, 0.08)
    n = len(y); t = np.arange(n) / SR
    rate = 2 ** (-semis * np.clip(1 - t / gl, 0, 1) / 12)
    p = np.cumsum(rate); p = p[p < n - 1]; i = p.astype(int); f = (p - i)[:, None]
    return y[i] * (1 - f) + y[i + 1] * f


# ---------------- web pluck: string harmonic with a little bend (a silk thread being plucked) ----------------
def silk(t0, m=81, g=1.0, d=0.6, pan=0.0):
    f = 440 * 2 ** ((m - 69) / 12); n = int(d * SR); t = np.arange(n) / SR
    ff = f * (1 + 0.03 * np.exp(-t * 25))
    ph = np.cumsum(ff) / SR
    y = (np.sin(2 * np.pi * ph) + 0.35 * np.sin(4 * np.pi * ph) + 0.12 * np.sin(6 * np.pi * ph)) * np.exp(-t * 6) * np.minimum(1, t / 0.002)
    add(mono(y * 0.12), t0, g, pan=pan, wet=0.35, echo=0.3, human=False)
def gulp(t0, g=1.0):
    t = tt_(0.12); f = 300 + 500 * (t / 0.12)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.12) * 0.3), t0, g, human=False)
# ---------------- parts (D minor) ----------------
PROG = [(50, 53, 57, 62), (50, 55, 58, 62), (49, 52, 55, 58), (50, 53, 57, 60)]   # Dm  Gm/D  A7(b9-ish dim)  Dm7
ROOT = [38, 43, 33, 38]
def bassline(t0, t1, g=1.0):     # habanera: 1 . . x  x . x .  (16ths 0,3,4,6 then 8.. mirror)
    for tt, k, b in sixteenths(t0, t1):
        r = ROOT[b % 4]
        pat = {0: r, 3: r + 7, 4: r + 12, 6: r + 7, 8: r, 11: r + 7, 12: r + 12, 14: r + 10}
        if k in pat:
            add(gm("Pizzicato Strings", pat[k] + 12, 0.22, 104 if k in (0, 8) else 88), tt, 0.5 * g, pan=-0.1)
            if k in (0, 8): add(gm("Bassoon", pat[k], 0.35, 96, 0.06), tt, 0.35 * g)
TANGO = [(0, 74, 3), (3, 73, 1), (4, 74, 2), (6, 77, 2), (8, 76, 3), (11, 74, 1), (12, 73, 4)]
TANGO2 = [(0, 81, 2), (2, 79, 2), (4, 77, 2), (6, 76, 2), (8, 74, 3), (11, 73, 1), (12, 69, 4)]
def lead(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if b % 4 not in (0, 2): continue
        for pos, m, du in (TANGO if b % 4 == 0 else TANGO2):
            if pos == k: add(gm("Harpsichord", m, du * S16 * 0.95, 96, 0.1), tt, 0.3 * g, pan=0.2, wet=0.2)
def webhook(t0, t1, g=1.0):     # plucked threads answer: 4 rising silk notes
    for tt, k, b in sixteenths(t0, t1):
        if b % 4 in (1, 3) and k in (2, 5, 8, 11): silk(tt, [81, 84, 86, 89][(k - 2) // 3] - (5 if b % 4 == 3 else 0), 0.9 * g, pan=(k - 6) / 12)
def comp(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k in (4, 12):
            for m in PROG[b % 4]: add(gm("Harpsichord", m, 0.12, 70, 0.05), tt, 0.12 * g, pan=-0.2)
def drums(t0, t1, style="loop", g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if style == "loop":
            if k in (0, 8): add(drum(36, 100), tt, 0.55 * g)
            if k in (4, 12): add(drum(37, 90), tt, 0.35 * g)
        if style in ("loop", "lite"):
            if k in (0, 3, 6, 8, 11, 14): add(drum(75, 90), tt, 0.4 * g, pan=0.25)
        if k % 2 == 0: add(drum(70, 70 if k % 4 == 0 else 45), tt, 0.3 * g, pan=-0.3)
def sparkle(t0, m=84, g=1.0): add(gm("Glockenspiel", m, 0.4, 90, 0.3), t0, 0.22 * g, wet=0.35, echo=0.4)
def groove(t0, t1, g=1.0, wh=True, ld=True):
    drums(t0, t1, "loop", g); bassline(t0, t1, g); comp(t0, t1, g)
    if ld: lead(t0, t1, g)
    if wh: webhook(t0, t1, g)
def big(t0, g=1.0):
    boom(t0, 1.0 * g, 1.2); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 120), t0, 0.6 * g, wet=0.35)
    for m in (38, 50, 57, 62, 65, 69): add(gm("Brass Section", m, 0.4, 120, 0.15), t0, 0.3 * g, wet=0.3)
    for j, m in enumerate((74, 77, 81, 86, 89)): silk(t0 + j * 0.03, m, 1.2 * g, 0.8, pan=(j - 2) / 4)
def pluck(t0, m, g=1.0): add(gm("Pizzicato Strings", m, 0.25, 105), t0, 0.5 * g, wet=0.2)
def creep(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k in (0, 3, 8, 11): pluck(tt, [50, 51, 50, 49][(k // 4) % 4], 0.7 * g)
        if k % 4 == 2: silk(tt, 93 - (k % 8), 0.35 * g, 0.3, pan=0.4)

# ---------------- arrangement ----------------
big(HOOK_HIT)
for i in range(5): silk(0.3 + i * 0.25, [86, 89, 93, 89, 98][i], 0.7, 0.4, pan=(i - 2) / 3)
groove(HOOK_HIT, HOOK_STOP, 1.0, wh=False)
add(gm("Music Box", 86, 0.6, 85, 0.4), HOOK_STOP + 0.1, 0.3, wet=0.5, echo=0.5, human=False)
creep(HOOK_STOP + BEAT, T["who"])                                   # salt grain vs bug: tiny steps
for h in (T["q"] + 0.2, T["q"] + 0.8): popfx(h, 0.6)
tick(T["q"] + 1.4, 0.9, 4200); tick(T["q"] + 2.0, 0.9, 4200)
groove(T["who"], T["egg"], 0.95)
shutter(T["who"] + 1.4, 0.7)
sparkle(T["sperm"] + 0.1, 86); sparkle(T["sperm"] + 0.2, 93, 0.7)
creep(T["egg"], SIL0, 0.9)
riser(T["egg"] + 1.0, SIL0, 1.2)
add(gm("Reverse Cymbal", 60, 1.4, 110), SIL0 - 1.4, 0.9)
big(BIG2, 1.1)
for i in range(4): gulp(BIG2 + 0.3 + i * 0.15, 0.6)
groove(BIG2, T["swim"])
for i in range(5): gulp(T["how"] + 0.8 + i * 0.5, 0.6); silk(T["how"] + 0.8 + i * 0.5, 84 + i * 2, 0.5)
add(glide_note("Bassoon", 50, 1.2, -5, 1.0), T["xray"] + 0.2, 0.4)   # molting: bassoon sag
for i in range(6): gulp(T["xray"] + 1.3 + i * 0.12, 0.45)
# circling: harp swirl over light groove
drums(T["swim"], T["gene"], "lite", 0.9); bassline(T["swim"], T["gene"], 0.9)
for j in range(8): add(gm("Orchestral Harp", [62, 65, 69, 74, 77, 74, 69, 65][j], 0.4, 90), T["swim"] + 0.3 + j * BEAT * 0.5, 0.03, wet=0.3)
for j in range(8): add(gm("Orchestral Harp", [62, 65, 69, 74, 77, 74, 69, 65][j], 0.4, 90), T["swim"] + 0.3 + (8 + j) * BEAT * 0.5, 0.025, wet=0.3)
# size gap: big bassoon + tiny glock
add(gm("Bassoon", 38, 1.0, 110, 0.2), T["gene"], 0.5); sparkle(at("gene", 1.0), 98, 0.8)
creep(T["gene"], T["why"], 0.7)
groove(T["why"], T["card"], 0.95, ld=True)
for i in range(3): popfx(T["why"] + 0.3 + i * 0.6, 0.6)
sparkle(T["card"], 86); sparkle(T["card"] + 0.09, 93, 0.7)
drums(T["card"], T["end"], "lite", 0.8); bassline(T["card"], T["end"], 0.8); comp(T["card"], T["end"], 0.8)
for i in range(3): popfx(at("card", 1.5 + i * 1.6), 0.5)
drums(T["end"], DUR - 1.6, "lite", 0.7); bassline(T["end"], DUR - 1.6, 0.8); lead(T["end"], DUR - 1.6, 0.7)
silk(T["end"] + 0.8, 86, 0.8); silk(T["end"] + 1.0, 81, 0.6)
FINAL = DUR - 1.6
for m_ in (38, 50, 57, 62, 65, 69): add(piano(m_, 1.4, 70), FINAL, 0.16, wet=0.4)
for j, m in enumerate((74, 77, 81, 86)): silk(FINAL + j * 0.06, m, 0.7, 0.9)
add(drum(36, 95), FINAL, 0.5); add(drum(49, 60), FINAL, 0.15, wet=0.4)
SILENCES = [(SIL0, BIG2)]
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
for a_, b_ in SILENCES:
    i0, i1 = int(a_ * SR), int(b_ * SR); fade = np.linspace(1, 0, int(0.04 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] *= 0.15
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.0); MIX /= np.abs(MIX).max() / 0.85
fo = int(0.8 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("/workspace/work/webbug/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f" % BPM)
