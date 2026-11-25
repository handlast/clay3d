# MURPHY BGM — DJ / drift phonk, 133.3 BPM (BEAT 0.45, from cues), F# minor phrygian.
# 808 cowbell melody (+ ping-pong delay), heavy distorted 808 with glides, Memphis-style chopped drums (stutter slices of the drum bus,
# triplet hat rolls, cowbell-ish clap), saturated master. Big accents ONLY at 0 s and BIG2; everything else = light sfx. No vocals.
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import drum as _drum, SR
from cues import *
N = int(SR * DUR) + SR
MIX = np.zeros((N, 2)); DR = np.zeros((N, 2)); VERB = np.zeros((N, 2)); ECHO = np.zeros((N, 2))
rng = np.random.default_rng(31)
def add(y, t0, g=1.0, pan=0.0, wet=0.0, echo=0.0, bus=None):
    bus = MIX if bus is None else bus
    i = int(max(0, t0) * SR)
    if i >= N: return
    if y.ndim == 1: y = np.stack([y, y], 1)
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    bus[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet
    if echo: ECHO[i:i + len(y)] += y * echo
tt_ = lambda d: np.arange(int(d * SR)) / SR
S16 = BEAT / 4
def hz(m): return 440 * 2 ** ((m - 69) / 12)
ORG = [0.0, BIG2]
def origin(t): return max([o for o in ORG if o <= t + 1e-6] or [0.0])
def grid(t0, t1):
    """(time, step 0..31 in a 2-bar phrase, bar index) — 16ths, bar origin resets at BIG2."""
    out = []; o = origin(t0); b0 = int(math.floor((t0 - o) / BAR)) - 1
    for b in range(max(b0, 0), b0 + 400):
        s0 = o + b * BAR
        if s0 > t1 + 0.1: break
        for k in range(16):
            tt = s0 + k * S16
            if t0 - 1e-4 <= tt < t1 - 1e-4 and origin(tt) == o: out.append((tt, k + 16 * (b % 2), b))
    return out
# ---------------- instruments ----------------
def cowbell(t0, m=78, g=1.0, d=0.3, pan=0.0):
    f = hz(m); t = tt_(d)
    sq = lambda fr: np.sign(np.sin(2 * np.pi * fr * t))
    y = (sq(f) + 0.7 * sq(f * 1.5)) * (np.exp(-t * 16) * 0.75 + 0.25 * np.exp(-t * 4))
    y = np.convolve(y, np.array([0.6, 1, -0.7]), "same")
    add(np.tanh(y * 1.1) * 0.12, t0, g, pan=pan, wet=0.15, echo=0.35)
def b808(t0, m=30, d=0.5, g=1.0, slide_to=None, slide_at=0.55):
    t = tt_(d); f0 = hz(m); f = np.full_like(t, f0)
    if slide_to is not None:
        f1 = hz(slide_to); k = np.clip((t / d - slide_at) / (1 - slide_at), 0, 1); f = f0 * (f1 / f0) ** (k * k * (3 - 2 * k))
    f = f * (1 + 1.2 * np.exp(-t * 55))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, (d - t) / 0.03) * np.minimum(1, t / 0.002)
    y = np.tanh(y * 4.5) * 0.38 + 0.08 * np.tanh(np.sin(4 * np.pi * np.cumsum(f) / SR) * 6)   # distorted + growl harmonic
    add(y, t0, g)
def kick(t0, g=1.0, bus=None):
    t = tt_(0.32); f = 50 + 190 * np.exp(-t * 42)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10); y = np.tanh(y * 3.0) * 0.55
    y[:int(0.004 * SR)] += rng.standard_normal(int(0.004 * SR)) * 0.25
    add(y, t0, g, bus=DR if bus is None else bus)
def snare(t0, g=1.0):
    t = tt_(0.22); n = rng.standard_normal(len(t))
    env = sum(np.exp(-np.clip(t - o, 0, None) * 55) * (t >= o) for o in (0, 0.009, 0.018)) + 0.6 * np.exp(-t * 16)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.5
    y = (np.convolve(n, np.array([1, -1]), "same") * 0.16 + body * 0.25) * env
    add(np.stack([y, np.roll(y, 50)], 1), t0, g, wet=0.2, bus=DR)
def hat(t0, g=1.0, op=False):
    t = tt_(0.16 if op else 0.04); n = np.convolve(rng.standard_normal(len(t)), np.array([1, -1.2, 0.5]), "same")
    add(n * np.exp(-t * (16 if op else 85)) * 0.06, t0, g, pan=0.18, bus=DR)
def boom(t0, g=1.0):
    t = tt_(1.4); f = 36 + 90 * np.exp(-t * 14)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.8) * 0.9, t0, g)
def subdrop(t0, g=1.0):
    t = tt_(1.2); f = 70 * np.exp(-t * 1.6) + 28
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.5) * 0.7, t0, g)
def whoosh(t0, d=0.35, g=1.0):
    n = int(d * SR); t = np.arange(n) / SR; nz = rng.standard_normal(n)
    y = nz - np.convolve(nz, np.ones(12) / 12, "same")
    add(y * np.sin(np.pi * t / d) ** 2 * 0.1, t0, g)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T_ = t1 - t0
    y = np.convolve(rng.standard_normal(n), np.ones(4) / 4, "same") * (t / T_) ** 2.5 * 0.07
    y += np.sin(2 * np.pi * np.cumsum(200 * (1800 / 200) ** (t / T_)) / SR) * (t / T_) ** 2 * 0.035
    add(y, t0, g)
def tick(t0, g=1.0, f=3000):
    t = tt_(0.04); add((np.sin(2 * np.pi * f * t) * np.exp(-t * 150)) * 0.3, t0, g, pan=0.2)
def popfx(t0, g=1.0, f0=1300, f1=320):
    t = tt_(0.09); f = f1 + (f0 - f1) * np.exp(-t * 60)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.3, t0, g)
def thump(t0, g=1.0, f0=60):
    t = tt_(0.3); f = f0 + 40 * np.exp(-t * 30)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12) * 0.7, t0, g)
def pew(t0, g=1.0):
    """light MG 'pop' (restrained, not a realistic gunshot): short filtered noise + low knock."""
    t = tt_(0.12); n = np.convolve(rng.standard_normal(len(t)), np.ones(3) / 3, "same")
    y = n * np.exp(-t * 70) * 0.25 + np.sin(2 * np.pi * np.cumsum(120 + 300 * np.exp(-t * 50)) / SR) * np.exp(-t * 30) * 0.35
    add(np.tanh(y * 2) * 0.3, t0, g, wet=0.15)
def ding(t0, g=1.0):
    t = tt_(1.2); y = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dc) * aa for f, dc, aa in ((1568, 3, 0.5), (2349, 5, 0.3), (3136, 8, 0.15)))
    add(y * 0.22, t0, g, wet=0.5, echo=0.3)
def heart(t0, g=1.0): thump(t0, 0.8 * g, 50); thump(t0 + 0.16, 0.55 * g, 46)
def crash(t0, g=1.0): add(_drum(49, 110), t0, 0.45 * g, wet=0.35)
# ---------------- patterns (F# phrygian: F# G A B C# D E) ----------------
RIFF = [(0, 78), (3, 78), (6, 81), (8, 78), (10, 79), (12, 78), (14, 76),
        (16, 78), (19, 78), (22, 85), (24, 83), (26, 81), (28, 79), (30, 78)]
RIFF2 = [(0, 90), (2, 88), (3, 90), (6, 85), (8, 86), (10, 85), (12, 83), (14, 81),
         (16, 78), (19, 81), (22, 83), (24, 85), (26, 86), (28, 85), (30, 83)]
BASSP = [(0, 30, 6, None), (6, 30, 4, 31), (10, 30, 6, None), (16, 26, 6, None), (22, 26, 4, 28), (26, 30, 6, 18)]
def drums(t0, t1, g=1.0, full=True, rolls=True):
    for tt, k, b in grid(t0, t1):
        kk = k % 16
        if full and (kk in (0, 10) or k == 23 or k == 27): kick(tt, g)
        if kk in (4, 12): snare(tt, g)
        if kk % 2 == 0: hat(tt, 0.8 * g)
        if rolls and k >= 28:
            n_ = 3 if k % 2 else 2
            for j in range(n_): hat(tt + j * S16 / n_, 0.55 * g)
        if kk == 14 and b % 4 == 3: hat(tt, 0.7 * g, op=True)
def bass(t0, t1, g=1.0):
    for tt, k, b in grid(t0, t1):
        for pos, m, d16, sl in BASSP:
            if k == pos: b808(tt, m, d16 * S16, g, slide_to=sl)
def bells(t0, t1, g=1.0, alt=False):
    for tt, k, b in grid(t0, t1):
        for pos, m in (RIFF2 if alt else RIFF):
            if k == pos: cowbell(tt, m, g, pan=(-0.25 if k % 4 else 0.25))
def phonk(t0, t1, g=1.0, alt=False, full=True):
    drums(t0, t1, g, full=full); bass(t0, t1, g); bells(t0, t1, g, alt)
CHOPS = []   # Memphis chops: (at, src, len, n) — stutter a slice of the drum bus
def chop_bars(t0, t1, every=2):
    for tt, k, b in grid(t0, t1):
        if k % 16 == 12 and b % every == every - 1: CHOPS.append((tt, tt - 3 * BEAT, S16 / 2, 8))
def big(t0, g=1.0):
    boom(t0, g); kick(t0, 1.4 * g, bus=MIX); subdrop(t0, 0.8 * g); crash(t0, g); whoosh(t0 - 0.35, 0.35, 0.6 * g)

# ---------------- arrangement (all times from cues) ----------------
END = DUR - 1.4
big(0.0, 1.15); phonk(0.0, T["who"], 1.0); pew_ts = [k * 0.14 for k in range(22)]
for p in pew_ts: pew(p, 0.35)
# who: bass + bells, no kick (intro of the person)
bells(T["who"], T["attack"], 1.0, alt=True); drums(T["who"], T["attack"], 0.6, full=False, rolls=False)
for tt, k, b in grid(T["who"], T["attack"]):
    if k in (0, 16): b808(tt, 30 if k == 0 else 26, BAR * 0.9, 0.55)
popfx(T["who"] + 1.0, 0.7); for_ = [tick(T["who"] + 1.8 + j * 0.09, 0.4, 2400 + 120 * j) for j in range(9)]
# attack: full groove, tank tally pops
phonk(T["attack"], T["retreat"], 1.0); chop_bars(T["attack"], T["retreat"])
for i in range(6): popfx(T["attack"] + 0.4 + i * 0.22, 0.5, 900, 260)
# retreat: half-time, artillery whistles -> thumps (light)
bells(T["retreat"], T["hit"], 0.9); drums(T["retreat"], T["hit"], 0.7, full=False)
for tt, k, b in grid(T["retreat"], T["hit"]):
    if k in (0, 16): b808(tt, 30, BAR * 0.9, 0.6, slide_to=29, slide_at=0.8)
for s0 in ARTY: whoosh(s0 - 0.6, 0.6, 0.5); thump(s0, 0.6, 55)
# hit: build + riser into the silence before BIG2
phonk(T["hit"], SIL0, 1.0, alt=True); thump(HIT_T, 1.0, 48); whoosh(HIT_T - 0.2, 0.25, 0.5)
riser(T["hit"] + 1.0, SIL0, 1.1)
for j in range(4): tick(SIL0 - (4 - j) * BEAT, 0.9, 2600 + 300 * j)
# BIG2 — 他却爬了上去
big(BIG2, 1.25); phonk(BIG2, T["danger"], 1.0)
# danger: drop the drums, heartbeat + filtered bells + long 808
bells(T["danger"], T["mg"], 0.7)
for j in range(int((T["mg"] - T["danger"]) / (BEAT * 2)) + 1): heart(T["danger"] + j * BEAT * 2, 0.9)
b808(T["danger"], 30, T["mg"] - T["danger"] - 0.05, 0.6, slide_to=25, slide_at=0.7)
# mg: phonk full, MG pops ON the beat grid (卡点)
phonk(T["mg"], T["three"], 1.0, alt=True); chop_bars(T["mg"], T["three"], 1)
for b in MG_BURSTS:
    for j in range(3): pew(b + j * S16 / 2, 0.5)
# three: arrows on beats, half-time drums
bells(T["three"], T["waver"], 1.0); drums(T["three"], T["waver"], 0.8, full=False)
for tt, k, b in grid(T["three"], T["waver"]):
    if k in (0, 16): b808(tt, 30 if k == 0 else 33, BAR * 0.9, 0.6)
for s0 in THREE_ARROWS: popfx(s0, 0.8, 700, 200); tick(s0 + 0.05, 0.4)
# waver: full phonk; bursts and enemy steps alternate on the beat
phonk(T["waver"], T["hour"], 1.0); chop_bars(T["waver"], T["hour"])
for b in WAVER_BURSTS:
    for j in range(3): pew(b + j * S16 / 2, 0.45)
for s0 in WAVER_STEPS: thump(s0, 0.45, 80); add(_drum(45, 90), s0, 0.12)
# hour: clock ticks + ammo pops, bass only
bells(T["hour"], T["counter"], 0.7, alt=True)
for tt, k, b in grid(T["hour"], T["counter"]):
    if k % 4 == 0: tick(tt, 0.5, 3200)
    if k in (0, 16): b808(tt, 30 if k == 0 else 26, BAR * 0.9, 0.6)
for s0 in AMMO_OUT: popfx(s0, 0.45, 1600, 500)
# counter: groove back, marching snare
phonk(T["counter"], T["cite"], 0.95, alt=True)
for tt, k, b in grid(T["counter"], T["cite"]):
    if k % 4 == 2: snare(tt, 0.25)
# cite / medal: lighter groove, highlighter swoosh, medal ding
phonk(T["cite"], T["medal"], 0.8, full=False); whoosh(T["cite"] + 1.5, 0.5, 0.5)
phonk(T["medal"], T["scared"], 0.85); ding(T["medal"] + 0.55, 0.9); popfx(T["medal"] + 1.4, 0.5)
# scared: breakdown — no drums, soft cowbell, wind-like noise bed via riser at low gain
bells(T["scared"], T["friends"], 0.5)
for tt, k, b in grid(T["scared"], T["friends"]):
    if k in (0, 16): b808(tt, 26, BAR * 0.95, 0.4)
# friends: rebuild; end: full, then a single tail hit
phonk(T["friends"], T["end"], 0.9, full=False); riser(T["friends"] + 0.5, T["end"], 0.6)
phonk(T["end"], END, 0.9, alt=True); chop_bars(T["end"], END)
for s0 in (T["end"] + 0.6, T["end"] + 1.6): popfx(s0, 0.6, 900, 300)
kick(END, 1.0, bus=MIX); subdrop(END, 0.5); cowbell(END, 78, 0.9, d=1.0)
SILENCES = [(SIL0, BIG2)]
# ---------------- Memphis chops on the drum bus ----------------
for at_, src, ln, n in CHOPS:
    i0 = int(src * SR); L = int(ln * SR); i1 = int(at_ * SR)
    if i0 < 0 or i1 + n * L >= N: continue
    sl = DR[i0:i0 + L].copy() * np.hanning(L)[:, None] ** 0.3
    DR[i1:i1 + n * L] *= 0.25
    for j in range(n): DR[i1 + j * L:i1 + (j + 1) * L] += sl * (1 - 0.08 * j)
MIX += np.tanh(DR * 1.6) / 1.2
# ---------------- mix ----------------
def reverb(x, sec=1.4, dec=3.4):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * dec); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
d_ = int(3 * S16 * SR)
for r in range(1, 4):
    sh = ECHO[: N - d_ * r] * (0.45 ** r)
    MIX[d_ * r:, 0] += sh[:, 1] * (0.8 if r % 2 else 0.3); MIX[d_ * r:, 1] += sh[:, 0] * (0.3 if r % 2 else 0.8)
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
for a_, b_ in SILENCES:
    i0, i1 = int(a_ * SR), int(b_ * SR); fade = np.linspace(1, 0, int(0.04 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] *= 0.12
MIX = MIX[: int(DUR * SR)]
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.4); MIX /= np.abs(MIX).max() / 0.85     # saturated master
fo = int(0.8 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("/workspace/work/murphy/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
print("ok BPM %.2f dur %.2f chops %d" % (BPM, len(MIX) / SR, len(CHOPS)))
