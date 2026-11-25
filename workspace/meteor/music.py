# METEOR BGM = muppet engine cloned 1:1 (harmony, hook, bass line, groove, swing, structure); ONLY timbres/samples swapped.
# origin: 《这条“海马”是冒牌货？》BGM — "detective noir / trip-hop busting an impostor": C minor, 97.96 BPM (8 bars = 19.6 s).
# 2-bar boom-bap loop (GM kick / swung snare / rim / closed hats) + vinyl crackle; Acoustic Bass "detective step" line cliche
# (C-Bb-A | Ab - G - B-D, glide G->C every 4th bar); Vibraphone hook with dub echo; Muted Trumpet answers; light piano stabs.
# Big hits ONLY at 0.4 s and 20.0 s (boom + brass stab + crash + scratch). Everything else = light SFX.
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import piano as _piano, gm as _gm, drum as _drum, SR
from cues import *
N = int(SR * DUR)
# measured peaks @vel100: Acoustic Bass .79, Vibraphone .41, Muted Trumpet .65, Brass 1.47, Orch Hit 1.55, hat42 1.27, woodblock 4.8, piano .04
LV = {"Acoustic Bass": 1.0, "Vibraphone": 2.0, "Muted Trumpet": 1.2, "Brass Section": 0.55, "Orchestra Hit": 0.5, "Pizzicato Strings": 1.0}
DLV = {42: 0.6, 46: 0.9, 76: 0.17, 77: 0.17}
SWAP = {"Acoustic Bass": "Fretless Bass", "Vibraphone": "Glockenspiel", "Muted Trumpet": "Ocarina", "Brass Section": "French Horns",
        "Orchestra Hit": "Timpani", "Pizzicato Strings": "Orchestral Harp", "Reverse Cymbal": "Reverse Cymbal"}
KIT = "Room"   # was Standard 1
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
    t = tt_(1.2); n = np.convolve(rng.standard_normal(len(t)), np.ones(60) / 60, "same") * 6
    y = (n + 0.6 * np.sin(2 * np.pi * 48 * t)) * np.minimum(1, t / 0.02) * np.exp(-t * 3.5)
    add(mono(y * 0.25), t0, g, wet=0.5, echo=0.4, human=False)
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
# ---------------- parts ----------------
CHORD_A = (51, 55, 58, 62)        # Cm(add9) mid voicing for piano
CHORD_B1 = (54, 56, 60, 63)       # Ab7
CHORD_B2 = (53, 56, 59, 62)       # G7(b9)
BASS_A = [(0, 36, 3), (3, 36, 1), (6, 39, 2), (8, 34, 3), (11, 34, 1), (12, 33, 4)]          # C . C Eb | Bb . A   (line cliche down)
BASS_B = [(0, 32, 3), (3, 32, 1), (6, 39, 2), (8, 31, 3), (11, 31, 1), (12, 35, 2), (14, 38, 2)]  # Ab . Eb | G . B D -> C
HOOK_A = [(0, 79, 2), (2, 75, 1), (3, 74, 1), (4, 75, 2), (7, 72, 3), (12, 71, 2), (14, 72, 2)]
HOOK_B = [(0, 72, 2), (2, 68, 2), (6, 67, 4), (12, 71, 1), (13, 74, 1), (14, 77, 2)]
TPT_B = [(8, 79, 1), (9, 78, 1), (10, 77, 1), (11, 75, 4)]
def drums(t0, t1, style="loop", g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        A_ = b % 2 == 0; opn = b % 4 == 3
        if style in ("loop", "lite"):
            kick = (0, 7, 10) if A_ else (0, 3, 10, 15)
            if k in kick: add(drum(36, 115 if k == 0 else 98), tt, (0.85 if style == "loop" else 0.55) * g)
            if k in (4, 12): add(drum(38, 112), tt + 0.012, (0.62 if style == "loop" else 0.4) * g, wet=0.18)
            if style == "loop":
                if (k == 14 and A_) or (k == 7 and not A_): add(drum(38, 45), tt, 0.16 * g)   # ghost
                if k == 6 and not A_: add(drum(37, 85), tt, 0.3 * g, pan=-0.2)
            if k % 2 == 0:
                if opn and k in (2, 6, 10, 14): add(drum(46, 80), tt, 0.24 * g, pan=0.3)
                else: add(drum(42, 92 if k % 4 == 0 else 62), tt, 0.26 * g, pan=0.3)
            elif style == "loop" and k in (15,) and A_: add(drum(42, 50), tt, 0.16 * g, pan=0.3)
        elif style == "hats":
            if k % 2 == 0: add(drum(42, 80 if k % 4 == 0 else 55), tt, 0.24 * g, pan=0.3)
            if k in (4, 12): add(drum(37, 80), tt, 0.25 * g)
def bass(t0, t1, g=1.0, glide=True):
    for tt, k, b in sixteenths(t0, t1):
        A_ = b % 2 == 0; pat = BASS_A if A_ else BASS_B
        if glide and b % 4 == 3 and k >= 12:
            if k == 12: add(glide_note("Acoustic Bass", 36, S16 * 4, 5, S16 * 3.2), tt, 0.95 * g)
            continue
        for pos, m, du in pat:
            if pos == k: add(gm("Acoustic Bass", m, du * S16 * 0.92, 112 if pos == 0 else 98, 0.06), tt, 0.95 * g)
def vibes(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m, du in (HOOK_A if b % 2 == 0 else HOOK_B):
            if pos == k: add(gm("Vibraphone", m, du * S16 + 0.15, 96, 0.4), tt, 0.32 * g, pan=-0.15, wet=0.25, echo=0.45)
def trumpet(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if b % 4 != 3: continue
        for pos, m, du in TPT_B:
            if pos == k: add(gm("Muted Trumpet", m, du * S16 * 0.95, 100, 0.12), tt, 0.32 * g, pan=0.25, wet=0.35, echo=0.25)
def comp(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        A_ = b % 2 == 0
        hits = [(0, CHORD_A), (10, CHORD_A)] if A_ else [(0, CHORD_B1), (8, CHORD_B2)]
        for pos, ch in hits:
            if pos == k:
                for m in ch: add(piano(m, 0.22, 58), tt, 0.24 * g, pan=0.1, wet=0.2)
def groove(t0, t1, g=1.0, drums_=True, vib=True, tpt=True, cp=True):
    if drums_: drums(t0, t1, "loop", g)
    bass(t0, t1, g)
    if vib: vibes(t0, t1, g)
    if tpt: trumpet(t0, t1, g)
    if cp: comp(t0, t1, g)
def big(t0, g=1.0):
    boom(t0, 1.2 * g, 1.3); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 127), t0, 0.65 * g, wet=0.35); add(drum(57, 110), t0 + 0.01, 0.35 * g, pan=0.4)
    add(drum(38, 127), t0, 0.5 * g, wet=0.3)
    for m in (48, 55, 60, 63, 67): add(gm("Brass Section", m, 0.42, 124, 0.15), t0, 0.32 * g, wet=0.35)
    add(gm("Orchestra Hit", 60, 0.5, 120), t0, 0.3 * g, wet=0.3)
    add(gm("Acoustic Bass", 24 + 12, 0.6, 127, 0.15), t0, 1.0 * g)
    scratch(t0 + 0.05, g=0.9 * g)
def pluck(t0, m, g=1.0): add(gm("Pizzicato Strings", m, 0.25, 105), t0, 0.5 * g, wet=0.2)
def vib1(t0, m, g=1.0, du=0.4): add(gm("Vibraphone", m, du, 100, 0.4), t0, 0.35 * g, wet=0.35, echo=0.4)

# ---------------- arrangement (muppet section map -> seal beats) ----------------
def b(k): return qb(k)
SAME = b(5); CHECKS = [b(7), b(8.5), b(10)]; STOP1 = (b(22), b(24)); CT = b(24.5); ZZZ = (b(26), b(28)); COUNT = [b(28), b(29), b(30)]
SHUTTER = b(31); RISERS = [(b(26), b(31))]; SILENCES = [(SIL0, BIG2)]; STOP2 = (b(50), b(52)); LOST = b(62); ALIVE = b(69); OUTRO = b(86); FINAL = b(92)
scratch(0.02, strokes=((0.09, 0.12), (0.09, -0.12), (0.06, 0.1), (0.06, -0.1), (0.04, 0.08)), g=0.45)
add(drum(38, 70), HOOK_HIT - 2 * S16, 0.3); add(drum(38, 90), HOOK_HIT - S16, 0.4)
big(HOOK_HIT)
groove(HOOK_HIT, HOOK_STOP, 1.0, tpt=False)
groove(SAME, STOP1[0])
for i, h in enumerate(CHECKS): add(drum(37, 100), h, 0.45); vib1(h, [72, 75, 79][i], 0.9)     # 9 seals popping
whoosh(T["who"] - 0.3, 0.4, 1.4); popfx(at("who", 2.6), 0.7); pluck(at("who", 2.6), 48, 1.0)  # swim -> stop
for j, m in enumerate([67, 66, 65]): add(gm("Muted Trumpet", m, 0.28, 95, 0.1), T["sperm"] + j * BEAT * 0.5, 0.36, wet=0.3)
add(gm("Muted Trumpet", 64, 0.9, 95, 0.3), T["sperm"] + BEAT * 1.5, 0.36, wet=0.3)            # sinking line
add(gm("Acoustic Bass", 36, 0.5, 110, 0.1), STOP1[0], 0.9)
for j in range(3): pluck(STOP1[0] + j * BEAT, [72, 75, 79][j], 0.8)
add(drum(36, 120), STOP1[1], 0.8); click(STOP1[1], 1.0); add(drum(49, 70), STOP1[1], 0.18, wet=0.4)
for tt, k, bb in sixteenths(CT, SIL0):
    if k % 2 == 0: tick(tt, 0.6 if k % 4 == 0 else 0.35, 3200 if k % 4 == 0 else 2500)
    fast = tt >= COUNT[0] - 1e-3
    if k in ((0, 4, 8, 12) if fast else (0, 8)): thump(tt, 0.85); thump(tt + 0.13, 0.45, 60)
ctbuzz(ZZZ[0], ZZZ[1] + BEAT * 0.5, 0.6)
for i, h in enumerate(COUNT): add(piano([36, 37, 38][i], 0.3, 90), h, 0.35); tick(h, 1.0, 4000)
riser(RISERS[0][0], SIL0, 1.4)
add(gm("Reverse Cymbal", 60, 1.6, 110), SIL0 - 1.6, 1.0)
shutter(SHUTTER, 1.0)
big(BIG2, 1.1)
groove(BIG2, STOP2[0])
for h in (at("reveal", 0), at("reveal", 0.4), at("reveal", 0.8), at("reveal", 1.1)): popfx(h, 0.6, 900, 200)
add(drum(37, 110), at("how", 1.6), 0.5); pluck(at("how", 1.6), 67); popfx(at("how", 2.9), 0.6)
for j, m in enumerate([60, 63, 67, 70, 72, 75, 79]): vib1(at("xray", 1.6) + j * 0.15 * 1, m, 0.75, 0.25)
popfx(at("xray", 3.6), 0.6)
add(gm("Acoustic Bass", 31, 0.5, 110, 0.1), STOP2[0], 0.9)          # blue whale: stop-time + sonar
sonar(STOP2[0], 1.0); pluck(at("swim", 1.3), 55, 0.7); popfx(at("swim", 1.3), 0.5)
add(glide_note("Acoustic Bass", 36, BEAT, 7, BEAT * 0.8), STOP2[1] - BEAT, 0.9)
add(drum(36, 110), STOP2[1], 0.6)
groove(STOP2[1], LOST)
for i in range(3): popfx(at("gene", 0.8 * i), 0.7); vib1(at("gene", 0.8 * i), [84, 87, 91][i], 0.7, 0.4)
bass(LOST, ALIVE, 0.9, glide=True)                                     # stormy ocean: bass + sonar only
for h in (LOST, LOST + 2 * BEAT, LOST + 4 * BEAT): sonar(h, 1.0)
whoosh(at("why", 0.8), 1.2, 0.8, 150, 900); add(drum(37, 110), at("why", 0.8), 0.5); popfx(at("why", 3.2), 0.7)
drums(ALIVE, T["card"], "hats"); bass(ALIVE, T["card"], 0.9); vibes(ALIVE, T["card"], 0.7)
pluck(at("order", 2.6), 60, 0.8); popfx(at("order", 2.6), 0.6); vib1(at("order", 3.9), 91, 0.9, 0.6)
popfx(T["card"], 0.7); vib1(T["card"], 84, 0.8, 0.5); vib1(T["card"] + 0.09, 91, 0.6, 0.6); add(drum(81, 90), T["card"], 0.3, wet=0.4)
drums(T["card"], OUTRO, "lite", 0.8); bass(T["card"], OUTRO, 0.85, glide=False); vibes(T["card"], OUTRO, 0.6)
for i in range(3): popfx(at("card", 2.5 + i * 2.6), 0.5)
drums(OUTRO, FINAL, "lite", 0.8); bass(OUTRO, FINAL, 0.85, glide=False)
sonar(OUTRO + BEAT, 0.6); vib1(at("end", 3.5), 96, 0.7, 0.3); add(drum(81, 80), at("end", 3.5), 0.25)
for m_ in (36, 48, 55, 62, 63, 67, 70): add(piano(m_, 1.6, 70), FINAL, 0.16, wet=0.4)
for m_ in (75, 79): vib1(FINAL, m_, 0.4, 1.2)
add(gm("Acoustic Bass", 36, 1.2, 100, 0.4), FINAL, 0.6); add(drum(36, 95), FINAL, 0.6); add(drum(49, 60), FINAL, 0.18, wet=0.4)

# ---------------- mix ----------------
def reverb(x, sec=1.8, dec=3.0):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * dec); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
# dub echo: dotted-8th ping-pong, 3 repeats
d = int(3 * S16 * SR)
for r in range(1, 4):
    sh = ECHO[: N - d * r] * (0.45 ** r)
    if r % 2: MIX[d * r:, 0] += sh[:, 1] * 0.8; MIX[d * r:, 1] += sh[:, 0] * 0.3
    else: MIX[d * r:, 0] += sh[:, 1] * 0.3; MIX[d * r:, 1] += sh[:, 0] * 0.8
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
# tape stop on the hook groove (2.24 s -> 2.85 s), then quiet until the loop drops in
ts0, ts1 = qb(3), HOOK_STOP
i0, i1 = int(ts0 * SR), int(ts1 * SR); n = i1 - i0
rate = np.linspace(1, 0.02, n) ** 1.4; p = i0 + np.cumsum(rate); p = np.clip(p, 0, N - 2); ii = p.astype(int); ff = (p - ii)[:, None]
seg = MIX[ii] * (1 - ff) + MIX[ii + 1] * ff; seg *= np.linspace(1, 0.3, n)[:, None]
MIX[i0:i1] = seg; j1 = int(SAME * SR) - 200; MIX[i1:j1] *= 0.0
# vinyl crackle bed (not in the hard silence)
cr = np.convolve(rng.standard_normal(N), np.ones(6) / 6, "same") * 0.004
pops = np.zeros(N); idx = rng.integers(0, N, int(DUR * 7)); pops[idx] = rng.uniform(-1, 1, len(idx)) * 0.12
pops = np.convolve(pops, np.exp(-np.arange(60) / 8), "same")
hum = np.sin(2 * np.pi * 0.55 * np.arange(N) / SR) * 0.5 + 1
sea = np.convolve(rng.standard_normal(N), np.ones(30) / 30, "same") * 0.006 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.12 * np.arange(N) / SR))
bub = np.zeros(N)
for i_ in rng.integers(0, N - 4000, int(DUR * 3)):
    tb = np.arange(2500) / SR; fb = rng.uniform(900, 1800) * (1 + 1.5 * (1 - np.exp(-tb * 40)))
    bub[i_:i_ + 2500] += np.sin(2 * np.pi * np.cumsum(fb) / SR) * np.exp(-tb * 60) * 0.05
MIX += mono(sea * hum)
add(gm("Glockenspiel", 79, 0.5, 80, 0.4), HOOK_STOP + 0.1, 0.25, wet=0.5, echo=0.6, human=False)   # lone question after the stop
for a, b in SILENCES:
    i0, i1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.04 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] = 0
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.2); MIX /= np.abs(MIX).max() / 0.85
fo = int(0.8 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("/workspace/work/meteor/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
pk = [20 * np.log10(np.sqrt((MIX[int(i * SR / 4):int((i + 1) * SR / 4)] ** 2).mean()) + 1e-9) for i in range(int(DUR * 4))]
print("loudest 0.25s:", sorted([(round(v, 1), i / 4) for i, v in enumerate(pk)])[-6:])
print("ok BPM %.2f" % BPM)
