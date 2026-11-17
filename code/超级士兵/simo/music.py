# SIMO BGM — drift phonk, C# minor (phrygian flavour), 122.45 BPM: 808 cowbell riff, distorted sliding 808 bass,
# hard kick, clap on 2&4, hat rolls (16th/32nd/triplet), sub drops on scene cuts. Big hits ONLY at 0.4 s and BIG2. No vocals.
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
S16 = BEAT / 4; SW = 0.0   # 16th swing
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



# ---------------- phonk synths ----------------
def cowbell(t0, m=73, g=1.0, d=0.32, pan=0.0):
    f = 440 * 2 ** ((m - 69) / 12); t = tt_(d)
    sq = lambda fr: np.sign(np.sin(2 * np.pi * fr * t))
    y = (sq(f) + 0.75 * sq(f * 1.481)) * (np.exp(-t * 14) * 0.7 + 0.3 * np.exp(-t * 4))
    y = np.convolve(y, np.array([1, -0.6]), "same")       # thin it like an 808 cowbell
    add(mono(np.tanh(y * 0.8) * 0.13), t0, g, pan=pan, wet=0.18, echo=0.22, human=False)
def b808(t0, m=37, d=0.5, g=1.0, slide_to=None, slide_at=0.6):
    t = tt_(d); f0 = 440 * 2 ** ((m - 69) / 12)
    f = np.full_like(t, f0)
    if slide_to is not None:
        f1 = 440 * 2 ** ((slide_to - 69) / 12); k = np.clip((t / d - slide_at) / (1 - slide_at), 0, 1); f = f0 * (f1 / f0) ** (k * k * (3 - 2 * k))
    f = f * (1 + 0.8 * np.exp(-t * 60))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, (d - t) / 0.03) * np.minimum(1, t / 0.003)
    y = np.tanh(y * 3.2) * 0.42
    add(mono(y), t0, g, human=False)
def kick(t0, g=1.0):
    t = tt_(0.35); f = 48 + 160 * np.exp(-t * 38)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9); y = np.tanh(y * 2.5) * 0.6
    add(mono(y), t0, g, human=False)
def clap(t0, g=1.0):
    t = tt_(0.25); n = rng.standard_normal(len(t))
    env = sum(np.exp(-np.clip(t - o, 0, None) * 60) * (t >= o) for o in (0, 0.011, 0.022)) + 0.5 * np.exp(-t * 14)
    y = np.convolve(n, np.array([1, -1]), "same") * env * 0.14
    add(np.stack([y, np.roll(y, 40)], 1), t0, g, wet=0.25, human=False)
def hat(t0, g=1.0, op=False):
    t = tt_(0.18 if op else 0.05); n = rng.standard_normal(len(t)); n = np.convolve(n, np.array([1, -1, 0.5]), "same")
    add(mono(n * np.exp(-t * (14 if op else 70)) * 0.06), t0, g, pan=0.15, human=False)
def subdrop(t0, g=1.0):
    t = tt_(1.2); f = 70 * np.exp(-t * 1.6) + 30
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.5) * 0.7), t0, g, human=False)
def icewind(t0, t1, g=1.0):
    d = t1 - t0; t = tt_(d); n = rng.standard_normal(len(t))
    n = np.convolve(n, np.ones(30) / 30, "same") * (0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * t)) * np.minimum(1, t / 0.5) * np.minimum(1, (d - t) / 0.5)
    add(mono(n * 0.5), t0, g, wet=0.4, human=False)
# riff: C#m phrygian (C# D E F# G# A B), 2-bar cowbell phrase on 16ths
RIFF = [(0, 73), (3, 73), (6, 76), (8, 73), (10, 74), (12, 73), (14, 71),
        (16, 73), (19, 73), (22, 80), (24, 78), (26, 76), (28, 74), (30, 73)]
RIFF2 = [(0, 85), (2, 83), (3, 85), (6, 80), (8, 81), (10, 80), (12, 78), (14, 76),
         (16, 73), (19, 76), (22, 78), (24, 80), (26, 81), (28, 80), (30, 78)]
BASSP = [(0, 37, 6, None), (6, 37, 4, 38), (10, 37, 6, None), (16, 33, 6, None), (22, 33, 4, 35), (26, 37, 6, 25)]
def grid(t0, t1):
    for tt, k, b in sixteenths(t0, t1): yield tt, k + 16 * (b % 2), b
def drums(t0, t1, g=1.0, rolls=True, full=True):
    for tt, k, b in grid(t0, t1):
        kk = k % 16
        if full and kk in (0, 10) or (full and k == 23): kick(tt, g)
        if kk in (4, 12): clap(tt, g)
        if kk % 2 == 0: hat(tt, 0.8 * g)
        if rolls and k >= 28:                      # 32nd / triplet roll into the bar
            for j in range(2 if k % 2 == 0 else 3): hat(tt + j * S16 / (2 if k % 2 == 0 else 3), 0.6 * g)
        if kk == 14 and b % 4 == 3: hat(tt, 0.7 * g, op=True)
def bass(t0, t1, g=1.0):
    for tt, k, b in grid(t0, t1):
        for pos, m, d16, sl in BASSP:
            if k == pos: b808(tt, m, d16 * S16, g, slide_to=sl)
def bells(t0, t1, g=1.0, alt=False):
    for tt, k, b in grid(t0, t1):
        for pos, m in (RIFF2 if alt else RIFF):
            if k == pos: cowbell(tt, m, g, pan=(-0.2 if k % 4 else 0.2))
def phonk(t0, t1, g=1.0, alt=False, full=True):
    drums(t0, t1, g, full=full); bass(t0, t1, g); bells(t0, t1, g, alt)
def big(t0, g=1.0):
    boom(t0, 1.0 * g, 1.3); kick(t0, 1.3 * g); subdrop(t0, 0.8 * g); add(drum(49, 120), t0, 0.5 * g, wet=0.35)
    whoosh(t0 - 0.35, 0.35, 0.6 * g)

# ---------------- arrangement ----------------
big(HOOK_HIT)
icewind(0, T["who"], 0.9)
phonk(HOOK_HIT, HOOK_STOP, 1.0)
for t_ in (T["q"], T["who"]): subdrop(t_, 0.35)
bells(HOOK_STOP, T["who"], 1.4); drums(HOOK_STOP, T["who"], 1.0, rolls=False, full=False)
for tt, k, b in grid(HOOK_STOP, T["who"]):
    if k in (0, 16): b808(tt, 37 if k == 0 else 33, BAR * 0.9, 0.6)   # half-drop: bells + claps only
phonk(T["who"], T["egg"], 0.95)
# egg: filtered tension — only bells + rising hats, bass out
bells(T["egg"], SIL0, 1.4)
for tt, k, b in grid(T["egg"], SIL0):
    if k in (0, 16): b808(tt, 37 if k == 0 else 33, BAR * 0.9, 0.6)
    if k % 8 == 4: clap(tt, 0.8)
for tt, k, b in grid(T["egg"], SIL0):
    hat(tt, 1.0 + 1.0 * (tt - T["egg"]) / (SIL0 - T["egg"]))
riser(T["egg"] + 1.0, SIL0, 1.1)
big(BIG2, 1.15)
phonk(BIG2, T["gene"], 1.0, alt=True)
for t_ in (T["how"], T["xray"], T["swim"]): subdrop(t_, 0.3)
phonk(T["gene"], T["order"], 0.95)
# order: the wound — beat cuts, wind + lone bell, then rebuild for the card
icewind(T["order"], T["card"], 0.8)
for j in range(4): cowbell(T["order"] + 0.3 + j * BEAT * 2, [73, 72, 71, 68][j], 1.6, d=0.6); b808(T["order"] + 0.3 + j * BEAT * 2, 25, BEAT * 1.8, 0.5)
subdrop(T["order"], 0.6)
phonk(T["card"], T["end"], 0.9, alt=True)
phonk(T["end"], DUR - 1.6, 0.85)
FINAL = DUR - 1.6
kick(FINAL, 1.0); subdrop(FINAL, 0.6); cowbell(FINAL, 73, 0.9, d=1.0); add(drum(49, 70), FINAL, 0.2, wet=0.4)
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
with wave.open("/workspace/work/simo/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f" % BPM)
