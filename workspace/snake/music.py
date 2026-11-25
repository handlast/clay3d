# 《蛇没有轮子，为什么能滚着逃命？》BGM — "rolling Drum & Bass": A minor (aeolian), 174.49 BPM (13 bars 4/4 + one 5/4 riser bar before 20.0).
# Beat = hand-built 2-bar breakbeat loop from GM kit one-shots (kick / snare / ghost snare / ride / hats), rendered per bar,
#        fill every 4th bar, slice-stutter every 8th bar.  Bass = numpy Reese (2 detuned saws + octave saw, FFT low-pass with
#        decaying envelope + slow wah LFO, tanh growl) + clean sub, 16th rolling pattern, kick sidechain ducking.
# Two big hits only (0.4 s, 20.0 s: sub drop + crash + Reese slide); 19.5-20 silent; SFX: wheel whoosh, tyre squeal, radar beep, gyro hum, swoosh.
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import gm as _gm, drum as _drum, SR
from cues import *
LV = {"Kalimba": 0.6, "Glockenspiel": 1.0, "Wood Block": 0.17}
DLV = {40: 0.55, 42: 0.6, 44: 1.4, 46: 0.75, 51: 0.9, 76: 0.17, 77: 0.17, 39: 0.85}
@functools.lru_cache(maxsize=None)
def gm(name, m, dur=0.5, vel=100, release=0.2): return _gm(name, m, dur, vel, release=release) * LV.get(name, 1.0)
@functools.lru_cache(maxsize=None)
def drum(n, vel=100): return _drum(n, vel) * DLV.get(n, 1.0)
N = int(SR * (DUR + 0.5))
DR = np.zeros((N, 2)); BS = np.zeros((N, 2)); MU = np.zeros((N, 2)); FX = np.zeros((N, 2)); VERB = np.zeros((N, 2))
KT = []          # kick times (for sidechain)
rng = np.random.default_rng(17)
def st(y): return np.stack([y, y], 1)
def tt_(d): return np.arange(int(d * SR)) / SR
def add(buf, y, t0, g=1.0, pan=0.0, wet=0.0, human=True):
    if human: g *= 1 + rng.uniform(-0.05, 0.05); t0 += rng.uniform(-0.003, 0.003)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    buf[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet
def lp(x, fc, order=4):          # zero-phase FFT low-pass (Butterworth magnitude)
    n = len(x); sz = 1 << int(np.ceil(np.log2(n + 64))); X = np.fft.rfft(x, sz); f = np.fft.rfftfreq(sz, 1 / SR)
    return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** (2 * order)), sz)[:n]
def bp(x, lo, hi): return lp(x, hi) - lp(x, lo)
# ---------------- grid ----------------
BARS = [G0 + 4 * k * BEAT for k in range(14)] + [G1 + n * BAR for n in range(20)]
def bar_len(b): return 20 if b == 13 else 16
def step_t(b, s): return BARS[b] + s * S16
def bar_at(t):
    for b in range(len(BARS) - 1, -1, -1):
        if BARS[b] <= t + 1e-6: return b
    return 0
CH = [33, 33, 29, 31]           # Am | Am | F | G  (A1 F1 G1 roots)
def root(b): return CH[(b if b < 14 else b - 14) % 4]
# ---------------- drums: 2-bar break ----------------
def kick(t0, g=1.0, vel=112):
    add(DR, drum(36, vel), t0, 0.9 * g); KT.append(t0)
    t = tt_(0.28); f = 48 + 70 * np.exp(-t * 35)
    add(DR, st(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) * 0.55), t0, g, human=False)
BREAK = [  # (step, kind, vel)  kind: K kick, S snare, g ghost snare
    [(0, "K", 115), (2, "K", 88), (4, "S", 120), (7, "g", 52), (9, "g", 58), (10, "K", 108), (12, "S", 118), (15, "g", 56)],
    [(0, "K", 115), (1, "g", 40), (4, "S", 120), (6, "g", 50), (9, "g", 55), (10, "K", 105), (11, "K", 92), (12, "S", 112), (14, "g", 60), (15, "S", 100)]]
def bar_events(b, fill=False):
    ev = list(BREAK[b % 2])
    if fill:
        ev = [e for e in ev if e[0] < 12] + [(12, "S", 115), (13, "S", 80), (14, "S", 95), (15, "S", 118), (14, "T", 100), (15, "T", 110)]
    return ev
def render_bar(b, style, ev):
    """render one bar into a temporary buffer (so it can be sliced); returns (buf, kick offsets)"""
    global DR
    L = int((bar_len(b) * S16 + 1.2) * SR); keep = DR; DR = np.zeros((L, 2)); kt0 = len(KT)
    for s, k, v in ev:
        tt = s * S16
        if k == "K": kick(tt, 1.0, v)
        elif k == "S":
            add(DR, drum(38, v), tt, 0.8 * v / 120, wet=0.12)
            if v >= 110: add(DR, drum(39, 100), tt, 0.35)
        elif k == "g": add(DR, drum(38, v), tt, 0.35 * v / 60, pan=-0.15)
        elif k == "T": add(DR, drum(45 if s == 14 else 43, v), tt, 0.4, pan=0.2)
    for s in range(bar_len(b)):
        tt = s * S16
        if style in ("full", "hook"):
            add(DR, drum(42, 92 if s % 2 == 0 else 52), tt, 0.32, pan=0.3)
            if s % 4 == 2: add(DR, drum(51, 85), tt, 0.28, pan=-0.3)
            if s == 14 and b % 2: add(DR, drum(46, 80), tt, 0.25, pan=0.3)
        elif style == "loop":
            if s % 2 == 0: add(DR, drum(42, 88 if s % 4 == 2 else 60), tt, 0.32, pan=0.3)
    buf = DR; DR = keep; kts = KT[kt0:]; del KT[kt0:]
    return buf, kts
def place_bar(b, style="full", fill=None, stutter=None, s0=0, s1=None, g=1.0):
    rb = b if b < 14 else b - 14
    fill = (rb % 4 == 3) if fill is None else fill; stutter = (rb % 8 == 7) if stutter is None else stutter
    ev = [e for e in bar_events(b, fill and not stutter) if s0 <= e[0] < (s1 or 99)]
    buf, kts = render_bar(b, style, ev)
    t0 = BARS[b]; i0 = int(t0 * SR)
    if stutter:   # slice the first 1/8 bar and re-trigger it across the second half (last two pitched up)
        sl = int(2 * S16 * SR); piece = buf[:sl].copy(); piece[-200:] *= np.linspace(1, 0, 200)[:, None]
        h = int(8 * S16 * SR); buf[h:] *= 0
        for j in range(4):
            p = piece if j < 2 else np.stack([np.interp(np.arange(int(sl / (1 + 0.25 * (j - 1)))) * (1 + 0.25 * (j - 1)), np.arange(sl), piece[:, c]) for c in (0, 1)], 1)
            o = h + j * sl; buf[o:o + len(p)] += p * (0.8 + 0.1 * j)
        kts = [k for k in kts if k < 8 * S16] + [8 * S16, 10 * S16]
    if s1 is not None: buf[int(s1 * S16 * SR):] *= 0
    if s0 > 0: buf[:max(0, int(s0 * S16 * SR) - 60)] *= 0
    add(DR, buf, t0, g, human=False); KT.extend(t0 + k for k in kts)
def drums(b0, b1, style="full", **k):
    for b in range(b0, b1): place_bar(b, style, **k)
def hats_only(t0, t1, g=1.0):
    b = bar_at(t0)
    while b < len(BARS) and BARS[b] < t1:
        for s in range(bar_len(b)):
            tt = step_t(b, s)
            if t0 - 1e-4 <= tt < t1 - 1e-4:
                if s % 2 == 0: add(DR, drum(42, 80 if s % 4 == 2 else 55), tt, 0.3 * g, pan=0.3)
                if s % 8 == 6: add(DR, drum(46, 70), tt, 0.18 * g, pan=0.3)
        b += 1
def claps(b0, b1, g=1.0):
    for b in range(b0, b1):
        for s in (4, 12): add(DR, drum(39, 110), step_t(b, s), 0.7 * g, wet=0.3)
        for s in (2, 6, 10, 14): add(DR, drum(42, 60), step_t(b, s), 0.22 * g, pan=0.3)
# ---------------- Reese bass ----------------
def saw(f, t): return 2 * ((f * t) % 1) - 1
def reese(m, dur, wah=0.5, glide=None, g=1.0):
    t = tt_(dur + 0.03); f0 = 440 * 2 ** ((m - 69) / 12)
    f = f0 if glide is None else f0 * 2 ** (glide * np.clip(t / dur, 0, 1) / 12)
    ph = np.cumsum(np.ones_like(t) * f) / SR
    x = sum(2 * ((ph * 2 ** (c / 1200)) % 1) - 1 for c in (-14, 14)) * 0.5 + 0.35 * (2 * ((ph * 2.003) % 1) - 1)
    lo = lp(x, 160 + 500 * wah); hi = lp(x, 1500 + 1800 * wah)
    e = np.exp(-t * 14); y = lo + (hi - lo) * e
    y = np.tanh(y * 1.8) * 0.5
    sub = np.sin(2 * np.pi * ph) * 0.55
    env = np.minimum(1, t / 0.004) * np.clip((dur + 0.03 - t) / 0.03, 0, 1)
    return np.stack([(y * 0.9 + sub) * env, (y * 1.1 + sub) * env], 1) * g   # slight L/R difference on the growl
ROLL = [(0, 0, 2), (3, 0, 1), (4, 12, 1), (6, 0, 2), (9, 0, 1), (10, 7, 1), (11, 0, 1), (12, 12, 1), (14, 10, 1), (15, 7, 1)]
ROLL_B = [(0, 0, 2), (3, 0, 1), (4, 12, 1), (6, 0, 2), (9, 3, 1), (10, 0, 1), (11, 12, 1), (12, 0, 2), (14, 3, 1), (15, -2, 1)]
def bassline(b0, b1, g=1.0, wah=None, s0=0, s1=None):
    for b in range(b0, b1):
        r = root(b); pat = ROLL if b % 2 == 0 else ROLL_B
        for s, iv, ln in pat:
            if s < s0 or (s1 is not None and s >= s1): continue
            tt = step_t(b, s); w = wah(tt) if wah else 0.45 + 0.35 * math.sin(2 * math.pi * (tt - G0) / (4 * BAR))
            add(BS, reese(r + 12 + iv, ln * S16 * 0.92, w), tt, 0.85 * g, human=False)
        if b == 13:   # 5/4 bar extra beat
            pass
def heartbeat(t0, t1, g=1.0):
    b = bar_at(t0)
    while b < len(BARS) and BARS[b] < t1:
        for s, gg in ((0, 1.0), (3, 0.6), (8, 0.9), (11, 0.55)):
            tt = step_t(b, s)
            if t0 <= tt < t1:
                t = tt_(0.32); f = 55 * (1 + 0.6 * np.exp(-t * 40))
                add(BS, st(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 0.75 * gg), tt, g, human=False)
        b += 1
# ---------------- melodic / sfx ----------------
def pluck(m, dur=0.4, g=1.0, bright=1.0):
    t = tt_(dur + 0.1); f = 440 * 2 ** ((m - 69) / 12)
    y = sum(np.sin(2 * np.pi * h * f * t) / h * np.exp(-t * (5 + h * 4 / bright)) for h in range(1, 12))
    return st(y * np.minimum(1, t / 0.002) * np.clip((dur + 0.1 - t) / 0.1, 0, 1) * 0.28 * g)
HOOK = [[(0, 76), (3, 79), (6, 81), (10, 79), (12, 76), (14, 74)], [(0, 72), (3, 74), (6, 76), (8, 69), (12, 79), (14, 81)]]
def lead(b0, b1, g=1.0, octup=False, s0=0):
    for b in range(b0, b1):
        for s, m in HOOK[b % 2]:
            if b == b0 and s < s0: continue
            tt = step_t(b, s)
            add(MU, pluck(m, 0.3, 1.0), tt, 0.9 * g, pan=-0.15, wet=0.2)
            add(MU, pluck(m, 0.3, 0.7), tt + 3 * S16, 0.3 * g, pan=0.35, wet=0.2)     # dotted-8th echo
            add(MU, gm("Kalimba", m + 12, 0.3, 100), tt, 0.35 * g, pan=0.2)
            if octup: add(MU, pluck(m + 12, 0.25, 1.2), tt, 0.35 * g, pan=0.25)
def stabs(b0, b1, g=1.0):   # sparse offbeat pluck chord in the verse
    for b in range(b0, b1):
        r = root(b) + 36
        for s in (6, 14):
            for iv in (0, 7, 15 if r % 12 == 9 else 16): add(MU, pluck(r + iv, 0.12, 0.8), step_t(b, s), 0.3 * g, pan=0.2, wet=0.25)
def noise(d): return rng.standard_normal(int(d * SR))
def whoosh(t0, d=0.5, f0=300, f1=3000, g=1.0, buf=None):
    x = noise(d); n = len(x); t = np.arange(n) / n
    y = bp(x, f0, f1) * np.sin(np.pi * t) ** 1.5
    lo = lp(x, f0 * 1.5) * np.sin(np.pi * t) ** 2
    yy = y * t + lo * (1 - t)
    add(buf if buf is not None else FX, st(yy * 0.35 * g), t0, human=False)
def wheel(t0, d, g=1.0):   # rolling "hoo-hoo": amplitude-modulated low band noise
    x = noise(d); t = np.arange(len(x)) / SR
    y = bp(x, 120, 900) * (0.55 + 0.45 * np.sin(2 * np.pi * 9 * t)) * np.sin(np.pi * t / d) ** 0.8
    add(FX, st(y * 0.5 * g), t0, human=False)
def squeal(t0, d=0.45, g=1.0):
    t = tt_(d); f = 2600 - 500 * t / d + 90 * np.sin(2 * np.pi * 37 * t)
    y = (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)) * np.minimum(1, t / 0.02) * np.clip((d - t) / 0.12, 0, 1)
    y += bp(noise(d), 2000, 5000) * 0.25 * np.exp(-t * 3)
    add(FX, st(y * 0.12 * g), t0, wet=0.2, human=False)
def beep(t0, d=0.09, f=2200, n=2, g=1.0):
    for j in range(n):
        t = tt_(d); y = np.where((f * t) % 1 < 0.5, 1.0, -1.0) * np.minimum(1, (d - t) / 0.01)
        add(FX, st(lp(y, 6000) * 0.07 * g), t0 + j * d * 1.6, wet=0.1, human=False)
def hum(t0, d=0.9, g=1.0):   # gyroscope
    t = tt_(d); f = 180 + 60 * (t / d)
    y = (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(6 * np.pi * np.cumsum(f) / SR)) * (0.7 + 0.3 * np.sin(2 * np.pi * 24 * t)) * np.sin(np.pi * t / d)
    add(FX, st(y * 0.13 * g), t0, wet=0.3, human=False)
def subdrop(t0, g=1.0, d=1.4):
    t = tt_(d); f = 30 + 70 * np.exp(-t * 3.5)
    add(FX, st(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) * 0.95), t0, g, human=False)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / n; x = noise(t1 - t0)
    y = (lp(x, 1500) * (1 - t) + bp(x, 1500, 9000) * t) * t ** 2.2 * 0.22
    f = 200 * 8 ** t; y += np.sin(2 * np.pi * np.cumsum(f) / SR) * t ** 2 * 0.05
    add(FX, st(y * g), t0, human=False)
def revcym(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / n
    add(FX, st(bp(noise(t1 - t0), 3000, 12000) * t ** 3 * 0.35 * g), t0, human=False)
def snareroll(t0, t1, g=1.0, step=None):
    tk = t0; k = 0; tot = max(1, int((t1 - t0) / (step or S16)))
    while tk < t1 - 1e-3:
        add(DR, drum(38, 50 + int(70 * k / tot)), tk, 0.45 * g * (0.3 + 0.7 * k / tot), human=False)
        tk += step or S16; k += 1
def big(t0, g=1.0):
    subdrop(t0, 1.1 * g); kick(t0, 1.2 * g, 127); add(DR, drum(49, 127), t0, 0.75 * g, wet=0.35); add(DR, drum(57, 110), t0, 0.45 * g, pan=0.4)
    add(BS, reese(57, 0.9, 0.9, glide=-24), t0, 0.8 * g, human=False)       # Reese slide A3 -> A1
    add(DR, drum(39, 127), t0, 0.5 * g, wet=0.4)
def pop(t0, m=84, g=1.0): add(FX, gm("Glockenspiel", m, 0.4, 105), t0, 0.35 * g, wet=0.3)
def wood(t0, hi=True, g=1.0): add(FX, drum(76 if hi else 77, 100), t0, 0.55 * g)
def spin(t0, d=1.0, g=1.0):   # dizzy "woo-woo"
    t = tt_(d); f = 600 * (1 + 0.35 * np.sin(2 * np.pi * 5 * t)) * (1 - 0.3 * t / d)
    add(FX, st(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) * 0.09 * g), t0, wet=0.3, human=False)

# ================= arrangement =================
# 0 - 0.4: reverse cymbal + snare roll into hit 1
revcym(0.0, HOOK_HIT, 1.0); snareroll(0.06, HOOK_HIT, 0.8, S16 / 2); whoosh(0.0, 0.45, 200, 4000, 0.8)
big(HOOK_HIT, 1.0)
# 0.4 - 2.72 hook frenzy: full break + Reese + ride, wheel roar; cut at BRAKE (tape stop later)
cut = int(27 - 0)   # 16th index of BRAKE inside bars 0..1 (27 = bar 1 step 11)
place_bar(0, "hook", fill=False, stutter=False, s0=1); place_bar(1, "hook", fill=True, stutter=False, s1=11)
bassline(0, 1, 1.0, s0=2); bassline(1, 2, 1.0, s1=11)
wheel(HOOK_HIT + 0.05, BRAKE - HOOK_HIT, 1.2)
for k in range(3): whoosh(HOOK_HIT + 0.2 + k * 0.7, 0.4, 400, 3000, 0.5)
# 3.15 pickup (ghost snares, steps 0-3 of bar 2), loop enters on the snare at CMP (bar 2 step 4)
for s in range(4): add(DR, drum(38, 45 + 15 * s), step_t(2, s), 0.3 + 0.12 * s, human=False)
place_bar(2, "loop", s0=4); drums(3, 8, "loop")
bassline(2, 8, 0.95, s0=4)
stabs(2, 8, 0.8)
for h in CRAWL_TICKS: wood(h, True, 0.6)
for k in range(5): wheel(CMP + 0.04 + k * 0.8, 0.7, 0.7)
pop(GAUGE, 84, 0.8); pop(X4, 88, 1.0)
for j, m in enumerate([69, 72, 76, 81, 84]): add(FX, pluck(m, 0.15, 1.2), X4 + j * S16 * 0.5, 0.45, wet=0.2, human=False)
# NUM: radar beeps + rising ticks with the counter
beep(BEEP1, 0.08, 2200, 2); beep(BEEP2, 0.08, 2600, 3, 1.2); pop(BEEP2 + 0.25, 93, 0.8)
nt = 12
for j in range(nt): add(FX, pluck(69 + j * 2 if j < 8 else 81 + (j - 8) * 2, 0.08, 1.3), COUNT[0] + j * (COUNT[1] - COUNT[0]) / nt, 0.35, human=False)
pop(NUM_TAG, 88, 0.7)
for k in range(2): wheel([NUM + 0.1, COUNT[0] + 0.2][k], [BEEP1 + 0.25 - NUM, BEEP2 + 0.1 - COUNT[0]][k], 0.8)
# 11.4 - 19.5: hats + bass heartbeat + riser (no break, no Reese)
hats_only(DIZ, SIL0 - 0.1, 1.25); heartbeat(DIZ, RISERS[0][0] + BAR, 1.35)
wood(AXLE_TAG, True, 0.8); wood(AXLE_TAG + S16 * 2, False, 0.6)
spin(SPIN, 1.4, 1.0)
for h in STARS: pop(h, 96, 0.6)
add(FX, gm("Glockenspiel", 81, 0.4, 100), DIZ_TAG, 0.3, wet=0.3); add(FX, gm("Glockenspiel", 80, 0.4, 100), DIZ_TAG + S16 * 2, 0.3, wet=0.3)
whoosh(HEADZ - 0.25, 0.35, 300, 2500, 0.5); pop(QMARK, 91, 0.9); pop(QMARK + S16 * 2, 86, 0.6)
riser(RISERS[0][0], SIL0, 1.0); snareroll(18.6, SIL0, 0.7, S16 / 2)
for k in range(8): add(BS, reese(33 + 12 + [0, 0, 3, 3, 5, 5, 7, 10][k], S16 * 0.9, 0.3 + 0.08 * k), RISERS[0][0] + 0.85 + k * S16 * 2, 0.5, human=False)
# 20.0: hit 2 then full DnB: break + Reese + hook lead
B20 = 14
big(BIG, 1.1)
drums(B20, B20 + 3, "full"); bassline(B20, B20 + 3, 1.0, s0=1); lead(B20 + 1, B20 + 3, 0.9)      # 20.0 - 24.13
hum(GYRO_HIT, 0.9, 1.0); pop(LEVEL, 88, 0.6); pop(HTAG, 84, 0.6)
# 24.13 - 28.94 FAST: Reese filter opens with speed, whoosh rising
drums(B20 + 3, B20 + 6, "full"); lead(B20 + 3, B20 + 6, 0.9)
bassline(B20 + 3, B20 + 6, 1.0, wah=lambda t: 0.3 + 0.7 * max(0, min(1, (t - SPEEDUP[0]) / (SPEEDUP[1] - SPEEDUP[0]))))
whoosh(SPEEDUP[0], SPEEDUP[1] - SPEEDUP[0], 200, 6000, 0.6); pop(LIFT_TAG, 88, 0.6); pop(FLAT_TAG, 91, 0.6)
# 28.94 - 33.75 STROKE: groove continues (bars 6.5 ..), swoosh per stroke
place_bar(B20 + 6, "full", s0=0); drums(B20 + 7, B20 + 10, "full"); bassline(B20 + 6, B20 + 10, 1.0); lead(B20 + 6, B20 + 10, 0.8)
for h in STROKES: whoosh(h - 0.05, 0.32, 500, 5000, 1.1)
# 33.75 - 37.19 BREAKDOWN: Reese + claps only
claps(B20 + 10, B20 + 12, 1.5); bassline(B20 + 10, B20 + 12, 1.25, wah=lambda t: 0.3)
place_bar(B20 + 12, "loop", fill=True, stutter=False, s0=8)   # half-bar fill back in (37.19 is bar 12 step 8)
bassline(B20 + 12, B20 + 13, 0.95, s0=0)
for s in (4,): add(DR, drum(39, 110), step_t(B20 + 12, s), 0.7, wet=0.3)
beep(RULER, 0.06, 1800, 1, 0.9); pop(IN_TAG, 93, 0.9); add(FX, pluck(81, 0.2, 1.2), IN_TAG + S16 * 2, 0.4, human=False)
for k in range(3): wheel(TRACK + 0.1 + k * 1.82, 1.6, 0.5)
# 37.19 - 44.07: full again, hottest at CONCL (octave lead)
drums(B20 + 13, B20 + 15, "full"); bassline(B20 + 13, B20 + 15, 1.0); lead(B20 + 12, B20 + 15, 0.85, s0=8)
add(FX, gm("Glockenspiel", 84, 0.4, 100), TAG_ROT, 0.3, wet=0.3); hum(TAG_STB, 0.6, 0.7); pop(DIVIDE, 88, 0.5)
drums(B20 + 15, B20 + 17, "full", fill=None); bassline(B20 + 15, B20 + 17, 1.05, wah=lambda t: 0.75); lead(B20 + 15, B20 + 17, 0.9, octup=True)
add(DR, drum(57, 90), CONCL, 0.25, wet=0.3); pop(EQ, 88, 0.7); pop(CONCL_TAG, 93, 0.8)
whoosh(CARD - 0.15, 0.3, 400, 4000, 0.6); add(FX, gm("Glockenspiel", 81, 0.5, 105), CARD, 0.35, wet=0.3)
for j, (dt, m) in enumerate([(0.25, 76), (0.55, 79), (0.9, 84)]):
    for iv in (0, 7): add(FX, pluck(m + iv - 12, 0.3, 1.1), CARD + dt, 0.4, wet=0.3, human=False)
# 44.07 outro: clean end — final kick + Reese tail, plucks on OK / bubble
kick(OUTRO, 1.0, 115); add(DR, drum(38, 110), OUTRO, 0.6, wet=0.3); add(BS, reese(45, 0.9, 0.5, glide=-12), OUTRO, 0.7, human=False)
for j, m in enumerate([69, 72, 76, 81]): add(MU, pluck(m, 0.5, 1.0), OUTRO + 0.05 + j * S16, 0.5, wet=0.4, human=False)
pop(OK, 88, 0.8); add(FX, gm("Kalimba", 84, 0.4, 100), OK + S16 * 2, 0.4, wet=0.3)
pop(BUB, 93, 0.8); add(MU, pluck(81, 0.9, 0.8), BUB + 0.3, 0.4, wet=0.5, human=False); add(MU, pluck(76, 0.9, 0.8), BUB + 0.3, 0.3, wet=0.5, human=False)

# ================= mix =================
def conv(x, ir):
    sz = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
n = int(1.4 * SR); t = np.arange(n) / SR
ir = rng.standard_normal(n) * np.exp(-t * 4.0); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
# sidechain: duck bass after every kick
KT = sorted(set(round(k, 4) for k in KT))
idx = np.zeros(N, dtype=np.int64) - 10 ** 9
for k in KT:
    i = int(k * SR)
    if 0 <= i < N: idx[i] = i
last = np.maximum.accumulate(idx); since = (np.arange(N) - last) / SR
sc = 1 - 0.72 * np.exp(-np.clip(since, 0, None) / 0.085) * np.clip(since / 0.004, 0, 1)
sc[since > 5] = 1.0
mix = DR * 0.95 + BS * sc[:, None] * 1.0 + MU * 0.9
mix += np.stack([conv(VERB[:, 0], ir), conv(VERB[:, 1], ir * 0.97)], 1) * 0.5
# tape stop at BRAKE (music only), then silence until the pickup
i0 = int(BRAKE * SR); TS = 0.28; nn = int(TS * SR)
rate = np.linspace(1, 0, nn) ** 1.3; pos = np.cumsum(rate)
seg = np.stack([np.interp(pos, np.arange(len(mix) - i0), mix[i0:, c]) for c in (0, 1)], 1) * np.linspace(1, 0.2, nn)[:, None]
iend = int(step_t(2, 0) * SR) - 50
mix[i0:iend] = 0; mix[i0:i0 + nn] = seg
squeal(BRAKE, 0.42, 1.0)
mix += FX[: len(mix)]
for a, b in SILENCES:
    j0, j1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.03 * SR))
    mix[j0:j0 + len(fade)] *= fade[:, None]; mix[j0 + len(fade):j1] = 0
mix = mix[: int(DUR * SR)]
mix = np.tanh(mix / np.abs(mix).max() * 2.2); mix /= np.abs(mix).max() / 0.89
fo = int(0.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
r = [20 * math.log10(max(1e-6, float(np.sqrt((mix[int(i * SR):int((i + 2) * SR)] ** 2).mean())))) for i in range(0, int(DUR), 2)]
print("rms/2s dB:", " ".join(f"{i*2}:{v:.0f}" for i, v in enumerate(r)))
print("peak", float(np.abs(mix).max()), "kicks", len(KT), "BPM", round(BPM, 2))
