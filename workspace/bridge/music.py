# 《断桥》 score + sound design. 96 BPM, 4/4, 96 bars, A minor (Am–Dm–F–E). Defenders' theme A4–C5–B4 (1,1,2 beats).
# writes stems: music.wav, sfx.wav  (mixed later with loudnorm)
import sys, math, functools, wave, numpy as np
sys.path.insert(0, "/workspace/work/sf"); sys.path.insert(0, "/workspace/sfx")
from samp import piano as _piano, gm as _gm, SR
from sfx import sfx
from cues import *
N = int(SR * (DUR + 0.5))
MUS = np.zeros((N, 2)); MV = np.zeros((N, 2)); FX = np.zeros((N, 2)); FV = np.zeros((N, 2))
rng = np.random.default_rng(7)
@functools.lru_cache(maxsize=None)
def _pk(name): return np.abs(_gm(name, 57, 1.0, 100)).max() + 1e-6
@functools.lru_cache(maxsize=None)
def gm(name, m, dur, vel=90, attack=None, release=0.4): return _gm(name, m, dur, vel, attack=attack, release=release) / _pk(name) * 0.3
def _add(buf, vb, y, t0, g, wet, pan):
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = np.asarray(y, float)
    if y.ndim == 1: y = np.stack([y, y], 1)
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    buf[i:i + len(y)] += y; vb[i:i + len(y)] += y * wet
def add(y, t0, g=1.0, wet=0.3, pan=0.0): _add(MUS, MV, y, t0, g, wet, pan)
def fx(y, t0, g=1.0, wet=0.15, pan=0.0): _add(FX, FV, y, t0, g, wet, pan)
def bt(b): return b * BEAT
def bar(k): return k * BAR
tt = lambda d: np.arange(int(d * SR)) / SR
UNDER = [(10, 20), (87.6, 110), (130, 140), (173.3, 176.6), (180, 200), (203.3, 206.6), (210, 220)]
def under(t): return any(a <= t < b for a, b in UNDER)

# ---------------- instruments ----------------
AM, DM, FM, EM = [45, 52, 57, 60], [38, 50, 53, 57], [41, 48, 53, 57], [40, 47, 52, 56]
PROG = [AM, DM, FM, EM]
def strings(t0, notes, d, vel=60, g=1.0, inst="Slow Strings"):
    for m in notes: add(gm(inst, m, d, vel, attack=0.7, release=1.2), t0, g * 0.5, wet=0.45)
def trem(t0, notes, d, vel=60, g=1.0):
    for m in notes: add(gm("Tremolo Strings", m, d, vel, attack=0.4, release=0.4), t0, g * 0.4, wet=0.4)
def cello(t0, m, d, vel=85, g=1.0): add(gm("Cello", m, d, vel, attack=0.12, release=0.7), t0, g * 0.8, wet=0.35, pan=-0.2)
def cbass(t0, m, d, vel=85, g=1.0): add(gm("Cello", m, d, vel, attack=0.1, release=0.6), t0, g * 0.7, wet=0.3)
def stacc(t0, m, vel=95, g=1.0): add(gm("Fast Strings", m, 0.17, vel, release=0.12), t0, g * 0.55, wet=0.25)
def pizz(t0, m, vel=80, g=1.0, pan=0.0): add(gm("Pizzicato Strings", m, 0.5, vel, release=0.3), t0, g * 0.6, wet=0.35, pan=pan)
def koto(t0, m, vel=75, g=1.0): add(gm("Koto", m, 1.4, vel, release=0.8), t0, g * 0.5, wet=0.45, pan=0.25)
def horns(t0, m, d, vel=85, g=1.0): add(gm("French Horns", m, d, vel, attack=0.12, release=0.8), t0, g * 0.6, wet=0.45, pan=0.15)
def tbn(t0, m, d, vel=90, g=1.0): add(gm("Trombone", m, d, vel, attack=0.06, release=0.5), t0, g * 0.45, wet=0.4, pan=-0.1)
def tuba(t0, m, d, vel=90, g=1.0): add(gm("Tuba", m, d, vel, attack=0.08, release=0.5), t0, g * 0.35, wet=0.3)
def taiko(t0, vel=100, g=1.0): add(gm("Taiko Drum", 36, 0.9, vel, release=0.5), t0, g * 0.9, wet=0.35)
def bdrum(t0, vel=100, g=1.0): add(gm("Taiko Drum", 31, 1.2, vel, release=0.7), t0, g * 0.9, wet=0.3)
def timp(t0, m=45, vel=100, g=1.0, roll=0.0):
    if roll:
        n = int(roll / 0.06)
        for k in range(n): add(gm("Timpani", m, 0.3, int(40 + 60 * k / n)), t0 + k * 0.06, g * 0.5, wet=0.4)
    else: add(gm("Timpani", m, 1.6, vel, release=1.0), t0, g * 0.9, wet=0.4)
def pno(t0, m, d=2.0, vel=55, g=1.0): add(_piano(m, d, vel), t0, g * 3.2, wet=0.5)
def drone(t0, t1, f=55.0, g=1.0):
    t = tt(t1 - t0); env = np.minimum(1, t / 3) * np.minimum(1, (t1 - t0 - t) / 3)
    y = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.003 * t) + 0.25 * np.sin(2 * np.pi * f * 3.01 * t)) * env
    add(y * 0.10 * (0.8 + 0.2 * np.sin(2 * np.pi * 0.11 * t)), t0, g, wet=0.4)
def pulse(t0, t1, g=1.0):      # low sub pulse on every beat (underground)
    k = 0
    while t0 + bt(k) < t1:
        t = tt(0.5); y = np.sin(2 * np.pi * np.cumsum(38 + 25 * np.exp(-t * 20)) / SR) * np.exp(-t * 7); add(y * 0.35, t0 + bt(k), g, wet=0.3); k += 1
def breath(t0, d, g=1.0):
    t = tt(d); n = np.convolve(rng.standard_normal(len(t)), np.ones(40) / 40, "same"); env = np.sin(np.pi * t / d) ** 2
    add(n * env * 0.5, t0, g, wet=0.6)
def motif(t0, base, fn, **kw):    # A–C–B : 1,1,2 beats
    fn(t0, base, bt(1), **kw); fn(t0 + bt(1), base + 3, bt(1), **kw); fn(t0 + bt(2), base + 2, bt(2) + 0.4, **kw)

# ---------------- ch1 0–30: crisis approaching ----------------
drone(0.0, 31.0, 55.0, 1.0)
add(gm("Cello", 33, 12.0, 55, attack=3.0, release=3.0), 0.5, 0.35, wet=0.6)
for k, (tb, m) in enumerate([(2.5, 57), (7.5, 52), (20.0, 57), (25.0, 53)]): pno(tb, m, 3.5, 40)
motif(bar(6), 69, lambda t, m, d, **k: pno(t, m, d + 1.0, 46))          # 15.0 s: the theme, lightly
motif(bar(10), 57, lambda t, m, d, **k: koto(t, m, 62))                  # 25 s, plucked
for tb in (15.0, 20.0, 22.5, 27.5): taiko(tb, 55, 0.45)                  # distant low drum
strings(bar(8), [45, 52], bar(4), 40, 0.7)

# ---------------- ch2 30–60: the army advances ----------------
for k in range(12):
    t0 = bar(12 + k); ch = PROG[k % 4]
    strings(t0, [ch[0] - 12 if ch[0] > 40 else ch[0], ch[1], ch[2]], BAR + 0.1, 55 + 2 * k, 0.8)
    for b in range(4): bdrum(t0 + bt(b), 70 + 2 * k + (12 if b == 0 else 0), 0.55 + 0.02 * k)
    for s in range(8): stacc(t0 + bt(s * 0.5), [45, 45, 48, 45, 47, 45, 48, 47][s] - (0 if k < 6 else 0), 70 + 3 * k, 0.55 + 0.03 * k)
    cbass(t0, 33 if ch is AM else ch[0] - 12 if ch[0] > 40 else ch[0], BAR, 80, 0.6)
    if k >= 8: tbn(t0, (ch[0] - 12 if ch[0] > 40 else ch[0]) + 12, bt(3), 80 + 4 * (k - 8), 0.7); tuba(t0, ch[0] - 12 if ch[0] > 40 else ch[0], bt(3), 85, 0.6)
motif(bar(14), 57, cello, vel=78)
motif(bar(18), 57, horns, vel=70, g=0.7)

# ---------------- ch3 60–90: the narrow bridge, then the hidden way ----------------
for k in range(8):            # 60–80: steady drum, bridge fight
    t0 = bar(24 + k); ch = PROG[k % 4]
    strings(t0, [ch[0] - 12 if ch[0] > 40 else ch[0], ch[1]], BAR + 0.1, 62, 0.7)
    for b in range(4): bdrum(t0 + bt(b), 72 if b else 92, 0.55)
    for s in range(8): stacc(t0 + bt(s * 0.5), [45, 48, 47, 45][s % 4], 78, 0.55)
    if k >= 4:
        for s in range(4): pizz(t0 + bt(s) + bt(0.5), [69, 72, 71, 69][s], 70, 0.7, pan=0.3)
motif(bar(26), 57, horns, vel=72, g=0.6)
pulse(80.0, 90.0, 0.8); breath(80.5, 4.5, 0.6); breath(85.5, 4.0, 0.5)
for s in range(16): pizz(80.0 + bt(s), [57, 60, 59, 57, 52, 57, 60, 59][s % 8], 62, 0.7, pan=-0.3 + 0.6 * (s % 2))
add(gm("Cello", 33, 10.0, 60, attack=1.0, release=1.5), 80.0, 0.5, wet=0.5)

# ---------------- ch4 90–120: decapitation strike ----------------
for k in range(12):
    t0 = bar(36 + k); ch = PROG[k % 4]
    strings(t0, [ch[0] - 12 if ch[0] > 40 else ch[0], ch[0] if ch[0] < 45 else ch[0] - 12 + 7], BAR + 0.1, 55 + 2 * k, 0.75)    # low long notes
    for s in range(8): pizz(t0 + bt(s * 0.5), [69, 72, 71, 69, 64, 69, 72, 71][s] + (0 if k < 6 else 0), 60 + 2 * k, 0.6, pan=0.35 if s % 2 else -0.35)
    if k < 8: pulse(t0, t0 + BAR, 0.6)
    if k >= 8:                 # 110: ground drums return (cross-cutting)
        for b in range(4): bdrum(t0 + bt(b), 80 + (15 if b == 0 else 0), 0.6)
        for s in range(8): stacc(t0 + bt(s * 0.5), [45, 48, 47, 45][s % 4], 85, 0.65)
motif(bar(40), 45, cello, vel=80)
add(gm("Tremolo Strings", 45, 4.0, 70, attack=0.1, release=0.4), 101.0, 0.35, wet=0.4)   # nest breached

# ---------------- ch5 120–150: resolve ----------------
for k in range(12):
    t0 = bar(48 + k); ch = PROG[k % 4]; inten = k / 11
    trem(t0, [ch[0] - 12 if ch[0] > 40 else ch[0], ch[1], ch[2]], BAR + 0.1, int(55 + 25 * inten), 0.55 + 0.2 * inten)
    pat = [0, 1, 2, 3] if k < 6 else [0, 1, 1.5, 2, 3, 3.5]
    if 4 <= k < 8: pat = [0, 2, 3]       # 130–140: underground, sparser
    for p in pat: bdrum(t0 + bt(p), int(85 + 30 * inten), 0.6 + 0.3 * inten)
    for s in range(8): stacc(t0 + bt(s * 0.5), [45, 48, 47, 45, 45, 48, 47, 52][s] + (12 if k >= 8 and s % 2 else 0), int(80 + 30 * inten), 0.6 + 0.3 * inten)
    if k % 2 == 0: tbn(t0 + bt(1), 57, bt(0.5), 95, 0.7); tbn(t0 + bt(1.5), 57, bt(0.5), 95, 0.6); tbn(t0 + bt(3), 60, bt(1), 100, 0.7)
    timp(t0, 45 if k % 2 == 0 else 40, int(80 + 30 * inten), 0.6)
for k in range(8):   # 140→: rising line
    stacc(140.0 + k * bt(2), 57 + [0, 2, 3, 5, 7, 8, 10, 12][k], 90, 0.45); horns(140.0 + k * bt(2), 57 + [0, 2, 3, 5, 7, 8, 10, 12][k], bt(2), 70 + 3 * k, 0.32)

# ---------------- ch6 150–180: the break ----------------
for k in range(4):       # 150–160: keep stacking, drums accelerate, cut one beat before 160
    t0 = bar(60 + k); ch = [AM, FM, EM, EM][k]
    trem(t0, [ch[0] - 12 if ch[0] > 40 else ch[0], ch[1], ch[2], ch[3]], BAR + (0.0 if k < 3 else -bt(1)), 95, 1.0)
    sub = [0.5, 0.5, 0.25, 0.25][k]; n = int(4 / sub)
    for s in range(n):
        tb = t0 + bt(s * sub)
        if tb >= TBREAK - bt(1) - 0.01: break
        bdrum(tb, 90 + 3 * k + (20 if s * sub % 1 == 0 else 0), 0.75 + 0.05 * k); stacc(tb, 40 + (12 if s % 2 else 0), 100, 0.75)
    tbn(t0, 52 if k < 2 else 52, BAR - (bt(1) if k == 3 else 0), 100, 0.8); horns(t0, 64 + (1 if k == 1 else 0) - (4 if k >= 2 else 0) + 4, BAR - (bt(1) if k == 3 else 0), 95, 0.7)
timp(157.5, 40, roll=1.2, g=0.8)
# 160.0: silence ~1.5 s (only the snap + water in the sfx stem); low strings creep back
strings(161.6, [33, 45], 8.0, 45, 0.8); add(gm("Cello", 33, 8.0, 55, attack=2.0, release=2.0), 161.6, 0.5, wet=0.5)
for k in range(4):       # 170–180: short strings + low drum, quieter than before
    t0 = 170.0 + bar(k)
    for b in (0, 2): bdrum(t0 + bt(b), 70, 0.45)
    for s in range(8): stacc(t0 + bt(s * 0.5), [45, 48, 47, 45][s % 4], 70, 0.45)
    strings(t0, [PROG[k][0] - 12 if PROG[k][0] > 40 else PROG[k][0], PROG[k][1]], BAR, 50, 0.6)

# ---------------- ch7 180–210: escort and counterattack ----------------
for k in range(12):
    t0 = bar(72 + k); ch = PROG[k % 4]
    strings(t0, [ch[0] - 12 if ch[0] > 40 else ch[0], ch[1], ch[2]], BAR + 0.1, 65, 0.8)
    soft = 0.45 if 4 <= k < 8 else 1.0           # 190–200: drums drop while 断须 holds
    if k < 8:
        for b in range(4): bdrum(t0 + bt(b), 80 + (15 if b == 0 else 0), 0.6 * soft)
    else:
        bdrum(t0, 115, 0.85); taiko(t0, 100, 0.6)  # 200→: only the downbeat
    cbass(t0, ch[0] - 12 if ch[0] > 40 else ch[0], BAR, 80, 0.6)
for r, t0 in enumerate((182.5, 187.5)): motif(t0, 45, cello, vel=82); motif(t0, 57, horns, vel=72, g=0.6)
motif(192.5, 69, lambda t, m, d, **k: pno(t, m, d + 1, 50))                # the theme alone while he holds
motif(195.0, 57, lambda t, m, d, **k: add(gm("Cello", m, d, 60, attack=0.2, release=0.8), t, 0.6, wet=0.5))
for r, t0 in enumerate((200.0, 202.5, 205.0, 207.5)):
    motif(t0, 57, horns, vel=88 + 4 * r, g=0.8); motif(t0, 45, tbn, vel=92, g=0.6); motif(t0, 45, cello, vel=85)

# ---------------- ch8 210–240: withdrawal ----------------
strings(210.0, [33, 45, 52], bar(4), 40, 0.45); strings(220.0, [29, 41, 48], bar(2), 38, 0.42); strings(225.0, [28, 40, 47], bar(2), 36, 0.4)
strings(230.0, [33, 45], bar(4), 34, 0.38)
for tb, m, v in [(211.25, 57, 44), (215.0, 52, 40), (221.25, 53, 40), (226.25, 52, 38)]: pno(tb, m, 3.0, v)
motif(212.5, 69, lambda t, m, d, **k: pno(t, m, d + 1.2, 48))
motif(222.5, 69, lambda t, m, d, **k: pno(t, m, d + 1.2, 44))
add(gm("Cello", 57, bt(1), 66, attack=0.2, release=0.6), 232.5, 0.8, wet=0.5); pno(232.5, 69, 2.5, 46)
add(gm("Cello", 60, bt(1), 66, attack=0.2, release=0.6), 232.5 + bt(1), 0.8, wet=0.5); pno(232.5 + bt(1), 72, 2.5, 46)
add(gm("Cello", 59, 6.0, 64, attack=0.2, release=2.5), 232.5 + bt(2), 0.8, wet=0.6); pno(232.5 + bt(2), 71, 7.0, 44)   # B hangs
add(gm("Violin", 83, 6.0, 28, attack=1.2, release=2.5), 232.5 + bt(2), 0.12, wet=0.8)

# ================= sound design (separate stem) =================
def thud(t0, g=1.0):
    t = tt(0.9); f = 34 + 40 * np.exp(-t * 18); y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    n = np.convolve(rng.standard_normal(len(t)), np.ones(60) / 60, "same") * np.exp(-t * 20) * 0.6
    fx((y + n) * 0.5, t0, g, wet=0.5)
def click(t0, g=1.0):
    L = int(0.012 * SR); c = rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 6)); c = np.convolve(c, [1, -0.9], "same")
    fx(c * 0.12, t0, g, wet=0.2, pan=rng.uniform(-0.6, 0.6))
def crawl(t0, t1, dens=20, g=1.0):
    for k in range(int((t1 - t0) * dens)):
        tk = t0 + rng.uniform(0, t1 - t0); L = int(0.004 * SR); c = rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)); c = np.convolve(c, [1, -1], "same")
        fx(c * 0.05 * rng.uniform(0.3, 1), tk, g, wet=0.1, pan=rng.uniform(-0.8, 0.8))
def rustle(t0, t1, g=1.0):
    t = tt(t1 - t0); n = rng.standard_normal(len(t)); n = np.convolve(n, [1, -1.6, 0.7], "same")
    am = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 1.3 * t) * np.sin(2 * np.pi * 0.7 * t))
    env = np.minimum(1, t / 1.0) * np.minimum(1, (t1 - t0 - t) / 1.0); fx(n * am * env * 0.02, t0, g, wet=0.1)
def bed(idx, t0, t1, g=1.0, start=0.0, fade=1.5):
    d = t1 - t0; y = sfx(idx, start=start, dur=d, norm=True); n = len(y); tt_ = np.arange(n) / SR
    env = np.minimum(1, tt_ / fade) * np.minimum(1, (d - tt_) / fade); fx(y * env, t0, g, wet=0.05)
def bite(t0, g=1.0): click(t0, 1.2 * g); click(t0 + 0.03, 0.8 * g); fx(sfx(80, dur=0.25, norm=True) * 0.12, t0, g * 0.5, wet=0.2)
def chew(t0, t1, g=1.0):
    for k in range(int((t1 - t0) * 7)):
        tk = t0 + k / 7 + rng.uniform(0, 0.05); click(tk, 0.6 * g)
        if rng.random() < 0.25: fx(sfx(85, start=rng.uniform(0, 1.5), dur=0.18, norm=True) * 0.08, tk, g, wet=0.2)
# ch1
for k in range(8): thud(0.6 + k * 1.2 + rng.uniform(0, 0.3), 0.35 + 0.05 * k)
rustle(0.0, 10.0, 1.0); rustle(20.0, 30.0, 0.7); crawl(0, 10, 10, 0.7); crawl(10, 20, 25, 0.6); crawl(20, 30, 8)
fx(sfx(85, start=0.2, dur=0.8, norm=True) * 0.12, 27.3, 1.0, wet=0.3)            # fibre creak
bed(273, 0.0, 10.0, 0.06, start=5.0); bed(273, 20.0, 80.0, 0.06, start=15.0)
# ch2
crawl(30, 60, 45, 1.0); rustle(30, 60, 0.9)
bite(42.7, 1.0); bite(44.2, 0.8); bite(45.6, 0.8)
for k in range(40): click(30 + rng.uniform(0, 30), rng.uniform(0.3, 0.8))
for k in range(6): fx(sfx(163, start=rng.uniform(0, 3), dur=0.4, norm=True) * 0.05, 53 + k * 0.9, 1.0, wet=0.2)   # bridge tremble
# ch3
crawl(60, 80, 55, 1.0); rustle(60, 80, 1.0); chew(72.4, 80.0, 1.0)
for k in range(60): click(60 + rng.uniform(0, 20), rng.uniform(0.4, 1.0))
for tk in (75.5, 78.2): fx(sfx(85, start=1.0, dur=0.4, norm=True) * 0.15, tk, 1.0, wet=0.2)
crawl(80, 87.6, 12, 0.8); crawl(87.6, 100, 18, 0.9)
# ch4
for k in range(30): fx(np.convolve(rng.standard_normal(int(0.05 * SR)), np.ones(30) / 30, "same") * 0.15 * np.exp(-np.arange(int(0.05 * SR)) / 600), 90 + rng.uniform(0, 20), 1.0, wet=0.3)  # soil trickles
bite(94.6, 0.8); bite(101.9, 0.9); bite(102.7, 0.8); bite(103.6, 0.8)
crawl(100, 120, 40, 1.0); rustle(110, 120, 0.8); chew(116.6, 120.0, 0.9)
# rain
R0 = 120.0
bed(326, R0, 136.0, 0.20, start=2.0, fade=6.0); bed(271, 128.0, 241.0, 0.30, start=1.0, fade=6.0)
# ch5–6
crawl(120, 160, 50, 1.0); chew(140.0, 150.0, 1.0); chew(154.6, 157.0, 1.1)
for k in range(50): click(120 + rng.uniform(0, 40), rng.uniform(0.4, 1.0))
for tk in (157.3, 158.1, 158.8, 159.4): fx(sfx(85, start=rng.uniform(0, 1), dur=0.35, norm=True) * 0.2, tk, 1.0, wet=0.3)   # last fibres strain
fx(sfx(83, dur=2.0, norm=True) * 0.9, TBREAK, 1.0, wet=0.35)                      # THE SNAP
fx(sfx(153, dur=3.5, norm=True) * 0.5, TBREAK + 0.45, 1.0, wet=0.3); fx(sfx(70, dur=2.0, norm=True) * 0.3, TBREAK + 0.6, 1.0, wet=0.3)
bed(186, TBREAK + 0.3, 186.0, 0.35, start=3.0, fade=2.0)                           # water
crawl(170, 180, 25, 0.8)
# ch7
fx(sfx(105, dur=4.0, norm=True) * 0.25, 181.0, 1.0, wet=0.3)
for k in range(40): fx(np.convolve(rng.standard_normal(int(0.06 * SR)), np.ones(25) / 25, "same") * 0.2 * np.exp(-np.arange(int(0.06 * SR)) / 700), 181 + rng.uniform(0, 5.5), 1.0, wet=0.3)
for k in range(24): fx(np.convolve(rng.standard_normal(int(0.06 * SR)), np.ones(25) / 25, "same") * 0.18 * np.exp(-np.arange(int(0.06 * SR)) / 700), 196 + rng.uniform(0, 3.5), 1.0, wet=0.3)
bite(192.0, 1.0); bite(195.4, 1.0); bite(179.0, 0.6); bite(180.5, 0.6)
crawl(180, 210, 35, 0.9)
for k in range(40): click(200 + rng.uniform(0, 6), rng.uniform(0.4, 1.0))
# ch8
for k in range(14): fx(sfx(70, start=0.0, dur=0.3, norm=True) * 0.04, 210.5 + k * 0.7 + rng.uniform(0, 0.3), 1.0, wet=0.5)   # drips
bed(273, 220.0, 240.0, 0.07, start=40.0, fade=4.0)
# underground: muffle the rain bed (simple ducking of the fx stem high band)
env = np.ones(N)
for a, b in UNDER: env[int(a * SR):int(b * SR)] = 0.35
env = np.convolve(env, np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")

# ---------------- reverb + write ----------------
def reverb(x, sec=2.6, dec=2.4):
    n = int(sec * SR); t = np.arange(n) / SR; ir = rng.standard_normal(n) * np.exp(-t * dec); ir = np.convolve(ir, np.ones(10) / 10, "same"); ir /= np.abs(ir).sum() ** 0.5 * 9
    sz = 1 << int(np.ceil(np.log2(len(x) + n))); return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
MUS += np.stack([reverb(MV[:, 0]), reverb(MV[:, 1])], 1) * 0.55
FX += np.stack([reverb(FV[:, 0], 1.5, 4), reverb(FV[:, 1], 1.5, 4)], 1) * 0.4
# hard silence for the break: 160.0–161.5 music only
i0, i1 = int((TBREAK - bt(1)) * SR), int((TBREAK + 1.55) * SR)
fade_n = int(0.05 * SR); MUS[i0:i0 + fade_n] *= np.linspace(1, 0, fade_n)[:, None]; MUS[i0 + fade_n:i1] = 0
MUS[i1:i1 + int(0.6 * SR)] *= np.linspace(0, 1, int(0.6 * SR))[:, None]
FX *= env[:, None] ** 0.6
# end
L = int(DUR * SR); MUS = MUS[:L]; FX = FX[:L]
fo = int(5.0 * SR); MUS[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5; FX[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
MUS = np.tanh(MUS / np.abs(MUS).max() * 1.5); MUS /= np.abs(MUS).max() / 0.9
FX = np.tanh(FX / np.abs(FX).max() * 1.2); FX /= np.abs(FX).max() / 0.9
def wr(path, X):
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(X, -1, 1) * 32767).astype("<i2").tobytes())
wr("/workspace/work/bridge/music.wav", MUS); wr("/workspace/work/bridge/sfx.wav", FX)
r = lambda X: " ".join(f"{i*10}:{20*np.log10(np.sqrt((X[int(i*10*SR):int((i+1)*10*SR)]**2).mean())+1e-9):.0f}" for i in range(24))
print("MUS", r(MUS)); print("FX ", r(FX))
