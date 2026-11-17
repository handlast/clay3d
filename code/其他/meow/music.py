# MEOW BGM — 'cat-walk sneak jazz' in E minor, 97.96 BPM swung: brushed kit, pizzicato tiptoe walking bass,
# clarinet sneak line, celesta/music-box sparkles, and a synth 'meow' lead (pitch glide up-then-down, formant-ish brightness sweep).
# Big hits ONLY at 0.4 s and BIG2 (20.0 s). No vocals.
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import piano as _piano, gm as _gm, drum as _drum, SR
from cues import *
N = int(SR * DUR)
# measured peaks @vel100: Acoustic Bass .79, Vibraphone .41, Muted Trumpet .65, Brass 1.47, Orch Hit 1.55, hat42 1.27, woodblock 4.8, piano .04
LV = {"Acoustic Bass": 1.0, "Vibraphone": 2.0, "Pizzicato Strings": 1.0, "Clarinet": 1.0, "Celesta": 1.0, "Music Box": 1.0, "Brass Section": 0.55}
DLV = {42: 0.6, 46: 0.9, 76: 0.17, 77: 0.17}
SWAP = {}
KIT = "Brush"
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

# ---------------- meow synth ----------------
def meow_syn(f0=660, d=0.55, up=1.25, down=0.78, bright=1.0):
    n = int(d * SR); t = np.arange(n) / SR; u = t / d
    c = np.where(u < 0.35, 1 + (up - 1) * np.sin(np.pi / 2 * u / 0.35), up + (down - up) * ((u - 0.35) / 0.65) ** 1.3)
    vib = 1 + 0.012 * np.sin(2 * np.pi * 6 * t) * np.clip((u - 0.3) * 3, 0, 1)
    ph = np.cumsum(f0 * c * vib) / SR
    b = (np.sin(np.pi * np.clip(u * 1.15, 0, 1)) ** 0.8) * bright        # "m-e-o-w": open then close
    y = np.zeros(n)
    for k in range(1, 9):
        y += np.sin(2 * np.pi * k * ph) * np.exp(-(k - 1) / (0.6 + 3.2 * b)) / k ** 0.3
    env = np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.12) ** 1.2
    return mono(y * env * 0.16)
def meow(t0, m=76, g=1.0, d=0.5, pan=0.0, up=1.22, down=0.8):
    add(meow_syn(440 * 2 ** ((m - 69) / 12), d, up, down), t0, g, pan=pan, wet=0.3, echo=0.25)
def purr(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(40) / 40, "same") * 6 * (0.5 + 0.5 * np.sin(2 * np.pi * 26 * t)) ** 3
    y *= (0.6 + 0.4 * np.sin(2 * np.pi * 0.9 * t)) * np.minimum(1, t / 0.2) * np.minimum(1, (t1 - t0 - t) / 0.2)
    add(mono(y * 0.05), t0, g, human=False)
# ---------------- parts (E minor sneak) ----------------
EM9 = (52, 55, 59, 62, 66); AM7 = (57, 60, 64, 67); B7 = (51, 54, 57, 59, 63); CMAJ7 = (48, 52, 55, 59)
PROG = [EM9, AM7, CMAJ7, B7]                  # 1 chord / bar, 4-bar cycle
ROOT = [40, 45, 36, 35]
# tiptoe bass: root . 5 . | chromatic approach on beat 4
def bassline(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        r = ROOT[b % 4]; nxt_ = ROOT[(b + 1) % 4]
        pat = {0: r, 4: r + 7, 8: r + 12 if b % 2 else r + 10, 12: nxt_ + (1 if nxt_ < r + 6 else -1)}
        if k in pat:
            add(gm("Pizzicato Strings", pat[k] + 12, 0.25, 108 if k == 0 else 92), tt, 0.55 * g, pan=-0.1)
            add(gm("Acoustic Bass", pat[k], 0.3, 100, 0.05), tt, 0.7 * g)
SNEAK = [(0, 64, 1), (2, 67, 1), (3, 68, 1), (4, 71, 3), (8, 70, 1), (10, 67, 2), (12, 64, 4)]     # E G G# B . Bb G E
SNEAK2 = [(0, 72, 1), (2, 71, 1), (4, 69, 2), (6, 67, 2), (8, 66, 1), (10, 63, 2), (12, 64, 4)]
def clarinet(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if b % 4 not in (0, 2): continue
        for pos, m, du in (SNEAK if b % 4 == 0 else SNEAK2):
            if pos == k: add(gm("Clarinet", m, du * S16 * 0.9, 96, 0.08), tt, 0.32 * g, pan=0.2, wet=0.25)
def meowhook(t0, t1, g=1.0):       # the meow lead answers the clarinet in bars 2 & 4
    for tt, k, b in sixteenths(t0, t1):
        if b % 4 == 1 and k == 2: meow(tt, 76, 0.9 * g, 0.45); meow(tt + 4 * S16, 79, 0.8 * g, 0.4)
        if b % 4 == 3 and k == 2: meow(tt, 74, 0.9 * g, 0.4, up=1.18); meow(tt + 3 * S16, 71, 0.8 * g, 0.7, up=1.3, down=0.72)
def comp(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k in (6, 14) and (b % 2 == 0 or k == 6):
            for m in PROG[b % 4]: add(piano(m, 0.18, 52), tt, 0.2 * g, pan=-0.15, wet=0.2)
def drums(t0, t1, style="loop", g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if style == "loop":
            if k in (0, 10) or (k == 7 and b % 2): add(drum(36, 100), tt, 0.6 * g)
            if k in (4, 12): add(drum(38, 90), tt, 0.4 * g, wet=0.15)
        if style in ("loop", "lite", "hats"):
            if k % 4 == 0 or k % 4 == 3: add(drum(42, 70 if k % 4 == 0 else 50), tt, 0.24 * g, pan=0.3)
        if style == "lite" and k in (4, 12): add(drum(37, 70), tt, 0.25 * g)
def sparkle(t0, m=84, g=1.0): add(gm("Glockenspiel", m, 0.4, 90, 0.3), t0, 0.22 * g, wet=0.35, echo=0.4)
def groove(t0, t1, g=1.0, mh=True, cl=True):
    drums(t0, t1, "loop", g); bassline(t0, t1, g); comp(t0, t1, g)
    if cl: clarinet(t0, t1, g)
    if mh: meowhook(t0, t1, g)
def big(t0, g=1.0):
    boom(t0, 1.0 * g, 1.2); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 120), t0, 0.6 * g, wet=0.35)
    for m in (40, 52, 59, 64, 67, 71): add(gm("Brass Section", m, 0.4, 120, 0.15), t0, 0.3 * g, wet=0.3)
    meow(t0 + 0.02, 81, 1.4 * g, 0.75, up=1.3, down=0.75)
def pluck(t0, m, g=1.0): add(gm("Pizzicato Strings", m, 0.25, 105), t0, 0.5 * g, wet=0.2)
def tiptoe(t0, t1, g=1.0):          # sneaky pizz steps only
    for tt, k, b in sixteenths(t0, t1):
        if k in (0, 6, 8, 14): pluck(tt, [64, 67, 64, 63][(k // 4) % 4] - 12, 0.7 * g)
        if k % 4 == 0: tick(tt, 0.4, 2600)

# ---------------- arrangement ----------------
b = qb
big(HOOK_HIT)
for i in range(3): meow(0.15 + i * 0.7, [79, 81, 84][i], 0.9, 0.42)
groove(HOOK_HIT, HOOK_STOP, 1.0, mh=False)
add(gm("Music Box", 83, 0.6, 85, 0.4), HOOK_STOP + 0.1, 0.3, wet=0.5, echo=0.5, human=False)
tiptoe(HOOK_STOP + BEAT, T["q"] + 1.3)                              # sneaking up to the box
add(drum(39, 100), at("q", 1.3) if False else T["q"] + 1.3, 0.0)
click(T["q"] + 1.9, 1.4); thump(T["q"] + 1.9, 0.6, 90); sparkle(T["q"] + 1.95, 88)   # lid shut + lock
groove(T["q"] + 2.3, T["egg"], 0.95)
for i in range(4): popfx(T["who"] + 0.2 + i * 0.4, 0.45, 1400, 500)
popfx(T["sperm"] + 0.2, 0.6); popfx(T["sperm"] + 1.6, 0.6)
whoosh(T["sperm"] + 1.5, 0.4, 1.0)
tiptoe(T["egg"], SIL0, 0.9)                                         # question: just tiptoe + ticks
riser(T["egg"] + 1.0, SIL0, 1.2)
add(gm("Reverse Cymbal", 60, 1.4, 110), SIL0 - 1.4, 0.9)
big(BIG2, 1.1)
for j in range(4): meow(BIG2 + 0.6 + j * 0.42, [76, 79, 83, 88][j], 0.6, 0.35)
groove(BIG2, T["gene"])
for j, m in enumerate([72, 76, 79]): sparkle(at("how", 1.4) + j * 0.15, m + 12, 0.7)
for j in range(6): pluck(T["xray"] + j * 0.9, 71 if j % 2 == 0 else 64, 0.7)        # look owner <-> box
popfx(T["swim"] + 1.2, 0.6); sparkle(T["swim"] + 2.2, 91, 0.8)
# owner leaves: band drops, lonely music box + soft tiptoe
tiptoe(T["gene"], T["why"], 0.6)
for j, m in enumerate([76, 74, 71, 67]): add(gm("Music Box", m, 0.6, 80, 0.4), T["gene"] + 0.3 + j * BEAT, 0.28, wet=0.4, echo=0.4)
# caveat: bass + brushes only
drums(T["why"], T["order"], "hats", 0.9); bassline(T["why"], T["order"], 0.85)
meow(at("why", 1.0), 74, 0.6, 0.6, up=1.15, down=0.9)
popfx(T["why"] + 0.5, 0.6)
# dinner time: full band back
groove(T["order"], T["card"], 1.0, cl=False)
for j in range(3): tick(T["order"] + j * BEAT, 0.8, 4200)
sparkle(T["card"], 88); sparkle(T["card"] + 0.09, 95, 0.7)
drums(T["card"], T["end"], "lite", 0.8); bassline(T["card"], T["end"], 0.8); comp(T["card"], T["end"], 0.8)
for i in range(3): popfx(at("card", 1.5 + i * 1.6), 0.5)
purr(T["card"] + 0.5, T["end"], 0.8)
drums(T["end"], DUR - 1.6, "lite", 0.7); bassline(T["end"], DUR - 1.6, 0.8); clarinet(T["end"], DUR - 1.6, 0.8)
meow(T["end"] + 0.3, 79, 0.7, 0.45); meow(T["end"] + 1.1, 76, 0.6, 0.5)
FINAL = DUR - 1.6
for m_ in (40, 52, 59, 62, 66, 71): add(piano(m_, 1.4, 70), FINAL, 0.16, wet=0.4)
meow(FINAL + 0.05, 83, 0.8, 0.9, up=1.15, down=0.7)
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
with wave.open("/workspace/work/meow/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f" % BPM)
