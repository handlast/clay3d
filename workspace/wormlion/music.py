# 《48年的蛆狮之谜》BGM — spaghetti-western desert ambush with Himalayan bells, D minor Andalusian (Dm-C-Bb-A), 100 BPM 4/4. ADAPTIVE: built only from cues.py.
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import gm as _gm, drum as _drum, SR
from cues import *
LV = {"Percussive Organ": 0.5, "Rock Organ": 0.7, "Synth Bass 1": 1.0, "Fretless Bass": 0.4, "Vibraphone": 1.0, "Polysynth": 0.45,
      "Synth Calliope": 0.25, "Accordion": 0.2, "Tine Electric Piano": 0.45, "Orchestra Hit": 0.5, "Reverse Cymbal": 4.0, "Synth Brass 1": 1.4}
DLV = {42: 0.6, 46: 0.9, 76: 0.16, 77: 0.16}
@functools.lru_cache(maxsize=None)
def gm(name, m, dur=0.5, vel=100, release=0.2): return _gm(name, m, dur, vel, release=release) * LV.get(name, 1.0)
@functools.lru_cache(maxsize=None)
def drum(n, vel=100): return _drum(n, vel) * DLV.get(n, 1.0)
@functools.lru_cache(maxsize=None)
def brush(n, vel=100): return _gm("Brush", n, 1.0, vel, release=0.05, bank=128) * {36: 0.55, 42: 0.6}.get(n, 1.0)
N = int(SR * DUR); MIX = np.zeros((N, 2)); MEL = np.zeros((N, 2)); VERB = np.zeros((N, 2)); ECHO = np.zeros((N, 2))
rng = np.random.default_rng(7)
def add(y, t0, g=1.0, pan=0.0, wet=0.0, echo=0.0, human=True, bus=None):
    if human: g *= 1 + rng.uniform(-0.06, 0.06); t0 += rng.uniform(-0.003, 0.003)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    (MEL if bus == "mel" else MIX)[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet
    if echo: ECHO[i:i + len(y)] += y * echo
def mono(y): return np.stack([y, y], 1)
tt_ = lambda d: np.arange(int(d * SR)) / SR
S8 = BEAT / 2; S16 = BEAT / 4; SW = 0.0; B2 = 0
def org(t0): return BIG2 if t0 >= BIG2 - 1e-4 else G0
def ph(b): return b if b < B2 else b - B2
def eighths(t0, t1):
    O = org(t0); out = []; b0 = int(math.floor((t0 - O) / BAR)) - 1
    for b in range(b0, b0 + 200):
        s0 = O + b * BAR
        if s0 > t1 + 0.1: break
        for e in range(2 * BPB):
            tt = s0 + e * S8 + (0.035 * S8 if e % 2 else 0)
            if t0 - 1e-4 <= tt < t1 - 1e-4: out.append((tt, e, b))
    return out
def sixteenths(t0, t1):
    O = org(t0); out = []; b0 = int(math.floor((t0 - O) / BAR)) - 1
    for b in range(b0, b0 + 200):
        s0 = O + b * BAR
        if s0 > t1 + 0.1: break
        for k in range(4 * BPB):
            tt = s0 + k * S16
            if t0 - 1e-4 <= tt < t1 - 1e-4: out.append((tt + (SW if k % 2 else 0), k, b))
    return out
_PK = {}
def gmn(name, m, dur=0.5, vel=100, release=0.2, g=1.0):
    if name not in _PK: _PK[name] = np.abs(_gm(name, 60, 0.5, 100, release=0.2)).max() + 1e-6
    return gm(name, m, dur, vel, release) / LV.get(name, 1.0) / _PK[name] * 0.5 * g
PROG = ["Dm", "C", "Bb", "A"]
CH = {"Dm": (50, 57, 62, 65), "C": (48, 55, 60, 64), "Bb": (46, 53, 58, 62), "A": (45, 52, 57, 61)}
ROOT = {"Dm": 38, "C": 36, "Bb": 34, "A": 33}
def chord_of(b): return PROG[ph(b) % 4]
MELO = [[(0, 74, 3), (3, 72, 1), (4, 74, 2), (6, 77, 2)],
        [(0, 76, 3), (3, 74, 1), (4, 72, 2), (6, 67, 2)],
        [(0, 70, 2), (2, 74, 1), (3, 77, 1), (4, 74, 2), (6, 70, 2)],
        [(0, 69, 4), (4, 73, 2), (6, 76, 2)]]
G = {"bass": 1.0, "strum": 1.8, "arp": 2.2, "twang": 3.2, "whistle": 2.2, "tpt": 2.2, "kick": 1.0, "rim": 1.0, "tamb": 1.0, "clave": 1.0, "bell": 2.0}
def bass(t0, t1, g=1.0, simple=False):
    for tt, e, b in eighths(t0, t1):
        r = ROOT[chord_of(b)]
        if e in (0, 4) or (not simple and e in (3, 7)):
            m = r if e == 0 else (r + 7 if e == 4 else (r + 5 if e == 3 else r - 1 + (2 if PROG[(ph(b) + 1) % 4] in ("Dm",) else 0)))
            add(gmn("Acoustic Bass", m, S8 * (1.8 if e in (0, 4) else 0.9), 110, 0.05), tt, 0.6 * g * G["bass"])
def strum(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k % 4 in (0, 2, 3):
            ch = CH[chord_of(b)]; up = k % 4 == 3
            for j, m in enumerate(ch if not up else ch[::-1]):
                add(gmn("Nylon Guitar", m + 12, S16 * 1.6, 92 if k % 4 == 0 else 70, 0.08), tt + j * 0.008, 0.18 * g * G["strum"], pan=-0.3, wet=0.2)
def arp(t0, t1, g=1.0):
    for tt, e, b in eighths(t0, t1):
        ch = CH[chord_of(b)]; m = ch[[0, 2, 3, 2, 1, 2, 3, 2][e]] + 12
        add(gmn("Nylon Guitar", m, S8 * 2.5, 85, 0.3), tt, 0.25 * g * G["arp"], pan=0.25, wet=0.4, echo=0.2)
def twang(m, tt, du, g):
    y = gmn("Clean Guitar", m, du, 110, 0.25)
    tr = 1 - 0.35 * (0.5 + 0.5 * np.sin(2 * np.pi * 6.5 * np.arange(len(y)) / SR))
    add(y * tr[:, None], tt, 0.45 * g * G["twang"], pan=0.1, wet=0.45, echo=0.45, bus="mel")
def lead(t0, t1, g=1.0, up=0, inst="twang"):
    for tt, e, b in eighths(t0, t1):
        for pos, m, du in MELO[ph(b) % 4]:
            if pos == e:
                if inst == "twang": twang(m + up - 12, tt, du * S8 * 0.95, g)
                elif inst == "whistle": add(gmn("Whistle", m + up, du * S8 * 0.9, 100, 0.15), tt, 0.4 * g * G["whistle"], wet=0.5, echo=0.35, bus="mel")
                else: add(gmn("Trumpet", m + up - 12, du * S8 * 0.9, 112, 0.15), tt, 0.45 * g * G["tpt"], wet=0.4, echo=0.2, bus="mel")
def kit(t0, t1, style="full", g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        on8 = k % 2 == 0
        if style in ("full", "lite", "gallop") and k in (0, 8): add(drum(36, 115), tt, 0.8 * g * G["kick"])
        if style == "half" and k == 0: add(drum(36, 110), tt, 0.8 * g * G["kick"])
        if style in ("full", "lite", "gallop") and k in (4, 12): add(drum(37, 105), tt, 0.5 * g * G["rim"], wet=0.3)
        if style == "half" and k == 8: add(drum(37, 105), tt, 0.5 * g * G["rim"], wet=0.4)
        if style in ("full", "gallop") and on8: add(drum(54, 90 if k % 4 == 0 else 65), tt, 0.3 * g * G["tamb"], pan=0.3)
        if style == "gallop" and k % 4 in (0, 2, 3): add(drum(76 if k % 4 == 0 else 77, 100), tt, 0.4 * g * G["clave"], pan=-0.35)
        if style in ("full", "lite") and k in (3, 6, 10): add(drum(75, 90), tt, 0.25 * g * G["clave"], pan=-0.3)
        if style == "soft" and k == 0: add(drum(36, 90), tt, 0.5 * g * G["kick"])
def groove(t0, t1, g=1.0, ld="twang", up=0, style="full", st=True):
    kit(t0, t1, style, g); bass(t0, t1, g)
    if st: strum(t0, t1, g)
    if ld: lead(t0, t1, g, up, ld)
def bowl(t0, g=1.0, f=220.0):
    t = tt_(4.0); y = sum(np.sin(2 * np.pi * f * h * t + 0.3 * np.sin(2 * np.pi * 4.7 * t)) * np.exp(-t * dc) * am for h, dc, am in ((1, 0.7, 1.0), (2.76, 1.1, 0.5), (5.4, 1.8, 0.25), (8.9, 3.0, 0.12)))
    y *= (1 + 0.15 * np.sin(2 * np.pi * 1.3 * t)) * np.minimum(1, t / 0.01)
    add(np.stack([y, np.roll(y, 400)], 1) * 0.06 * G["bell"], t0, g, wet=0.6, human=False)
def bell(t0, m=74, g=1.0): add(gmn("Tubular Bells", m, 2.0, 100, 1.0), t0, 0.25 * g * G["bell"], wet=0.6, echo=0.2, bus="mel")
def timp(t0, m=38, g=1.0): add(gmn("Timpani", m, 1.0, 120, 0.6), t0, 0.7 * g, wet=0.3)
def timproll(t0, t1, g=1.0):
    n = int((t1 - t0) / 0.06)
    for j in range(n): add(gmn("Timpani", 38, 0.3, 70 + int(50 * j / max(1, n)), 0.2), t0 + j * 0.06, 0.3 * g * (0.3 + 0.7 * j / max(1, n)), wet=0.3)
def big(t0, g=1.0):
    boom(t0, 1.1 * g, 1.3); timp(t0, 38, 1.2 * g); add(drum(49, 127), t0, 0.5 * g, wet=0.35); add(drum(36, 127), t0, 0.9 * g)
    for m in (62, 65, 69, 74): add(gmn("Trumpet", m, 0.7, 125, 0.3), t0, 0.22 * g, wet=0.35, bus="mel")
    add(gmn("Acoustic Bass", 26, 1.0, 127, 0.2), t0, 0.9 * g); whip(t0 - 0.02, 0.8 * g)
def whip(t0, g=1.0):
    t = tt_(0.12); y = rng.standard_normal(len(t)) * np.exp(-t * 60); y = y - np.convolve(y, np.ones(3) / 3, "same")
    add(mono(y * 0.5), t0, g, wet=0.4, human=False)
def sandhiss(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    y = rng.standard_normal(n); y = y - np.convolve(y, np.ones(4) / 4, "same")
    env = (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 1.7 * t))) * np.minimum(1, t / 0.2) * np.minimum(1, (t1 - t0 - t) / 0.2)
    grains = (rng.random(n) > 0.9993).astype(float); grains = np.convolve(grains, np.exp(-np.arange(200) / 30), "same")
    add(np.stack([y * env * 0.04 + grains * 0.15, np.roll(y, 500) * env * 0.04 + grains * 0.15], 1), t0, g, human=False)
def stepfx(t0, g=1.0, hi=True): add(drum(76 if hi else 77, 90), t0, 0.25 * g, pan=-0.2)
def stab(t0, g=1.0, ch="Dm"):
    for m in CH[ch]: add(gmn("Trumpet", m + 12, 0.25, 110, 0.15), t0, 0.1 * g, wet=0.3, bus="mel")
def batping(t0, g=1.0, f0=5200, f1=1800, pan=-0.3):
    t = tt_(0.06); f = f0 * (f1 / f0) ** (t / 0.06)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.06)
    add(mono(y * 0.16), t0, g, pan=pan, wet=0.5, echo=0.3, human=False)
def rasp(t0, kind="burst", d=0.6, g=1.0, pan=0.25):
    n = int(d * SR); t = np.arange(n) / SR; y = np.zeros(n)
    if kind == "burst":
        r2 = np.random.default_rng(int(t0 * 100))
        for c in range(4):
            c0 = r2.uniform(0, d * 0.8)
            for j in range(r2.integers(3, 7)):
                i = int((c0 + j * 0.012) * SR); L = min(int(0.006 * SR), n - i)
                if L > 0: y[i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / SR * 900)
    else:
        teeth = (np.sin(2 * np.pi * (180 if kind == "cont" else 260) * t) > 0.6).astype(float)
        y = rng.standard_normal(n) * (0.3 + 0.7 * teeth) * np.sin(np.pi * t / d) ** 0.5
    y = y - np.convolve(y, np.ones(5) / 5, "same")
    add(mono(y * 0.22), t0, g, pan=pan, wet=0.15, human=False)
def static(t0, d=0.6, g=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    y = np.round(rng.standard_normal(n) * 3) / 3 * (0.5 + 0.5 * (rng.random(n) > 0.995)) * np.minimum(1, (d - t) / 0.08)
    y = np.repeat(y[::6], 6)[:n]
    add(np.stack([y, np.roll(y, 300)], 1) * 0.07, t0, g, human=False)
def beep(t0, f=1500, d=0.07, g=1.0):
    t = tt_(d); y = np.sign(np.sin(2 * np.pi * f * t)) * np.minimum(1, (d - t) / 0.01)
    add(mono(np.convolve(y, np.ones(4) / 4, "same") * 0.06), t0, g, human=False)
def heart(t0, g=1.0): thump(t0, 0.7 * g, 48); thump(t0 + 0.18, 0.5 * g, 44)
def vo(*a, **k): return   # English vocal chops removed (user 2026-11-03: felt weird)
def _vo_unused(text, t0, g=1.0, voice="ryan", pitch=0.92, lofi=0.3, drive=1.6, pan=0.0, speed=1.0):
    y = vox.fx(vox.say(text, voice, speed), pitch, lofi, drive)
    add(mono(y) * 0.42, t0, g, pan=pan, wet=0.25, echo=0.2, human=False)
def boom(t0, g=1.0, dur=1.1):
    t = tt_(dur); f = 36 + 80 * np.exp(-t * 16)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2) * 0.9), t0, g, human=False)
def thump(t0, g=1.0, f0=52):
    t = tt_(0.3); f = f0 + 40 * np.exp(-t * 30)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12) * 0.8), t0, g, human=False)
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
def cluck(t0, g=1.0, kind="bok"):        # synthetic chicken: buzzy glottal source + two vowel formants
    d = {"bok": 0.09, "bagawk": 0.32}[kind]; t = tt_(d)
    if kind == "bok": f = 520 - 160 * t / d
    else: f = np.where(t < 0.1, 480, 480 + 520 * np.minimum(1, (t - 0.1) / 0.08)) * (1 + 0.02 * np.sin(2 * np.pi * 30 * t))
    phs = np.cumsum(f) / SR; y = np.zeros(len(t))
    for h in range(1, 14):
        fh = f * h; amp = np.exp(-((fh - 900) / 350) ** 2) + 0.6 * np.exp(-((fh - 2200) / 500) ** 2) + 0.15
        y += np.sin(2 * np.pi * phs * h) * amp / h ** 0.3
    env = np.minimum(1, t / 0.006) * np.minimum(1, (d - t) / 0.03)
    y = y * env + rng.standard_normal(len(t)) * np.exp(-t * 200) * 0.6
    add(mono(y * 0.05), t0, g, wet=0.15, human=False)
def bagawk(t0, g=1.0):
    cluck(t0, g); cluck(t0 + 0.12, 0.9 * g); cluck(t0 + 0.24, g, "bagawk")
def crunch(t0, g=1.0, d=0.12):
    n = int(d * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for j in range(9):
        i = int(rng.uniform(0, 0.75) * n); L = int(0.012 * SR)
        seg = rng.standard_normal(min(L, n - i)) * np.exp(-np.arange(min(L, n - i)) / SR * 300)
        y[i:i + len(seg)] += seg * rng.uniform(0.4, 1)
    y = y - np.convolve(y, np.ones(6) / 6, "same")
    add(mono(y * np.exp(-t * 12) * 0.35), t0, g, human=False)
def squish(t0, g=1.0):
    t = tt_(0.25); f = 300 + 900 * (t / 0.25) ** 0.5
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10) * 0.2 + np.convolve(rng.standard_normal(len(t)), np.ones(12) / 12, "same") * np.exp(-t * 14) * 0.9
    add(mono(y * 0.5), t0, g, wet=0.2, human=False)
def rattle(t0, d, g=1.0):
    n = int(d * SR)
    for j in range(int(d * 22)):
        tt = t0 + rng.uniform(0, d); L = tt_(0.03)
        y = np.sin(2 * np.pi * rng.uniform(1500, 3200) * L) * np.exp(-L * 180) * 0.25 + rng.standard_normal(len(L)) * np.exp(-L * 300) * 0.2
        add(mono(y), tt, g * rng.uniform(0.4, 1), pan=rng.uniform(-0.3, 0.3), human=False)
def bloop(t0, g=1.0, f0=300, f1=900):
    t = tt_(0.14); f = f0 * (f1 / f0) ** (t / 0.14)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.14) * 0.3), t0, g, wet=0.3, human=False)
def slide(t0, f0, f1, d=0.4, g=1.0):
    t = tt_(d); f = f0 * (f1 / f0) ** (t / d) * (1 + 0.01 * np.sin(2 * np.pi * 6 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.2 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    add(mono(y * np.sin(np.pi * t / d) ** 0.5 * 0.12), t0, g, wet=0.3, human=False)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T_ = t1 - t0
    y = np.convolve(rng.standard_normal(n), np.ones(5) / 5, "same") * (t / T_) ** 2.5 * 0.07
    f = 180 * (1600 / 180) ** (t / T_); y += np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / T_) ** 2 * 0.04
    add(mono(y), t0, g, human=False)
def drip(t0, g=1.0, f=900, pan=0.0):
    t = tt_(0.25); fr = f * (1 + 1.2 * (1 - np.exp(-t * 40)))
    add(mono(np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 28) * 0.22), t0, g, pan=pan, wet=0.9, echo=0.3, human=False)
def creak(t0, g=1.0, d=0.35, f0=70, f1=140):      # wood creak / muscle stretch: buzzy saw with stick-slip jitter
    t = tt_(d); f = f0 * (f1 / f0) ** (t / d) * (1 + 0.15 * (rng.random(len(t)) > 0.97))
    ph_ = np.cumsum(f) / SR; y = 2 * (ph_ % 1) - 1
    y = np.convolve(y, np.ones(8) / 8, "same") * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t)) * np.sin(np.pi * t / d)
    add(mono(y * 0.18), t0, g, wet=0.2, human=False)
def boing(t0, g=1.0):
    t = tt_(0.6); f = 220 * (1 + 0.5 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4))
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * 0.35), t0, g, wet=0.2, human=False)
def buzz(t0, g=1.0):
    t = tt_(0.3); y = np.sign(np.sin(2 * np.pi * 110 * t)) * 0.5 + np.sign(np.sin(2 * np.pi * 116 * t)) * 0.5
    add(mono(np.convolve(y, np.ones(10) / 10, "same") * np.minimum(1, (0.3 - t) / 0.05) * 0.12), t0, g, human=False)
def wind(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(30) / 30, "same") * 5
    env = (0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * t) ** 2) * np.minimum(1, t / 0.3) * np.minimum(1, (t1 - t0 - t) / 0.3)
    add(np.stack([y * env, np.roll(y, 900) * env], 1) * 0.08, t0, g, human=False)
def rumble(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T_ = t1 - t0
    y = np.convolve(rng.standard_normal(n), np.ones(60) / 60, "same") * 8 * np.minimum(1, t / 0.05) * np.minimum(1, (T_ - t) / 0.3)
    add(mono(y * 0.12), t0, g, human=False)
def whirr(t0, t1, g=1.0, rate=0.35):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(6) / 6, "same") - np.convolve(rng.standard_normal(n), np.ones(40) / 40, "same")
    p = np.sin(2 * np.pi * t / (1 / rate) / 1.0)
    env = (0.4 + 0.6 * (0.5 + 0.5 * np.sin(2 * np.pi * 2 * rate * t * 2.2))) * np.minimum(1, t / 0.3) * np.minimum(1, (t1 - t0 - t) / 0.2)
    add(np.stack([y * env * (1 + p) / 2, y * env * (1 - p) / 2], 1) * 0.12, t0, g, human=False)
def drip(t0, g=1.0, f=900, pan=0.0):
    t = tt_(0.25); fr = f * (1 + 1.2 * (1 - np.exp(-t * 40)))
    add(mono(np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 28) * 0.22), t0, g, pan=pan, wet=0.9, echo=0.3, human=False)
def creak(t0, g=1.0, d=0.35, f0=70, f1=140):      # wood creak / muscle stretch: buzzy saw with stick-slip jitter
    t = tt_(d); f = f0 * (f1 / f0) ** (t / d) * (1 + 0.15 * (rng.random(len(t)) > 0.97))
    ph_ = np.cumsum(f) / SR; y = 2 * (ph_ % 1) - 1
    y = np.convolve(y, np.ones(8) / 8, "same") * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t)) * np.sin(np.pi * t / d)
    add(mono(y * 0.18), t0, g, wet=0.2, human=False)
def boing(t0, g=1.0):
    t = tt_(0.6); f = 220 * (1 + 0.5 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4))
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * 0.35), t0, g, wet=0.2, human=False)
def buzz(t0, g=1.0):
    t = tt_(0.3); y = np.sign(np.sin(2 * np.pi * 110 * t)) * 0.5 + np.sign(np.sin(2 * np.pi * 116 * t)) * 0.5
    add(mono(np.convolve(y, np.ones(10) / 10, "same") * np.minimum(1, (0.3 - t) / 0.05) * 0.12), t0, g, human=False)
def wind(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(30) / 30, "same") * 5
    env = (0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * t) ** 2) * np.minimum(1, t / 0.3) * np.minimum(1, (t1 - t0 - t) / 0.3)
    add(np.stack([y * env, np.roll(y, 900) * env], 1) * 0.08, t0, g, human=False)
def rumble(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T_ = t1 - t0
    y = np.convolve(rng.standard_normal(n), np.ones(60) / 60, "same") * 8 * np.minimum(1, t / 0.05) * np.minimum(1, (T_ - t) / 0.3)
    add(mono(y * 0.12), t0, g, human=False)
def whirr(t0, t1, g=1.0, rate=0.35):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(6) / 6, "same") - np.convolve(rng.standard_normal(n), np.ones(40) / 40, "same")
    p = np.sin(2 * np.pi * t / (1 / rate) / 1.0)
    env = (0.4 + 0.6 * (0.5 + 0.5 * np.sin(2 * np.pi * 2 * rate * t * 2.2))) * np.minimum(1, t / 0.3) * np.minimum(1, (t1 - t0 - t) / 0.2)
    add(np.stack([y * env * (1 + p) / 2, y * env * (1 - p) / 2], 1) * 0.12, t0, g, human=False)
def big(t0, g=1.0):
    boom(t0, 1.2 * g, 1.3); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 127), t0, 0.6 * g, wet=0.35); add(drum(57, 110), t0 + 0.01, 0.3 * g, pan=0.4)
    add(gm("Orchestra Hit", 62, 0.6, 125, 0.2), t0, 0.6 * g, wet=0.35)
    for m in (50, 57, 62, 65, 69): add(gm("Rock Organ", m, 0.7, 120, 0.3), t0, 0.3 * g, wet=0.3, bus="mel")
    add(gm("Synth Bass 1", 26, 0.9, 127, 0.2), t0, 1.0 * g)
def clang(t0, g=1.0):
    t = tt_(0.6); y = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dcy) for f, dcy in ((830, 6), (1370, 8), (2210, 10), (3170, 14)))
    add(mono(y * 0.12), t0, g, wet=0.4, human=False)
def gulp(t0, g=1.0):
    t = tt_(0.25); f = 500 * np.exp(-t * 9) + 90
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10) * 0.5), t0, g, wet=0.2, human=False)
def suckfx(t0, g=1.0, d=0.45):
    n = int(d * SR); t = np.arange(n) / SR; y = rng.standard_normal(n)
    y = np.convolve(y, np.ones(4) / 4, "same") * (t / d) ** 2 * np.minimum(1, (d - t) / 0.03)
    add(mono(y * 0.25), t0 - d, g, wet=0.3, human=False)

# ---------------- arrangement (all times from cues) ----------------
sandhiss(0, HOOK_HIT + 0.2, 1.0); whoosh(0.0, 0.35, 1.0, 300)
big(HOOK_HIT); sandhiss(HOOK_HIT, HOOK_STOP, 0.6)
groove(HOOK_HIT, HOOK_STOP + 0.3, 1.0, ld="tpt", style="gallop")
# ant: footsteps
bass(T["ant"], T["slide"], 0.8, simple=True); kit(T["ant"], T["slide"], "half", 0.6)
for j, tt in enumerate(np.arange(T["ant"] + 0.1, at("ant", 2.5), 0.15)): stepfx(tt, 0.8, j % 2 == 0)
slide(at("ant", 2.5), 1400, 500, 0.6, 0.8); popfx(at("ant", 2.5), 0.5)
# slide: sand trickle, descending
sandhiss(T["slide"], T["bottom"], 1.2); kit(T["slide"], T["bottom"], "half", 0.8); bass(T["slide"], T["bottom"], 0.8); strum(T["slide"], T["bottom"], 0.6)
for j in range(3): slide(at("slide", 1 + j), 900 - j * 150, 400 - j * 80, 0.5, 0.5)
# bottom: dark drone, bowl, heartbeat
bowl(T["bottom"], 0.8, 110); rumble(T["bottom"], T["q"], 0.6)
for b in range(3): thump(at("bottom", b), 0.6, 46)
# q: timpani roll into BIG2
timproll(T["q"], BIG2, 1.0); riser(T["q"], BIG2, 0.8)
# BIG2
big(BIG2, 1.1); groove(BIG2, T["fam"], 1.0, ld="tpt", style="gallop")
# fam
groove(T["fam"], T["same"], 0.85, ld="whistle", style="lite")
ding(at("fam", 3), 0.45, 2349)
# same
groove(T["same"], T["y1978"], 0.85, ld="twang", style="full")
buzz(at("same", 1.5), 0.6); ding(at("same", 3.5), 0.45, 2637)
# 1978: sepia, no drums
arp(T["y1978"], T["wait"], 1.3); bass(T["y1978"], T["wait"], 0.8, simple=True)
bell(at("y1978", 0.1), 74); bowl(at("y1978", 1.5), 0.6, 220); bell(at("y1978", 3), 69, 0.8)
# wait: ticking years
arp(T["wait"], T["y2025"], 1.3); bass(T["wait"], T["y2025"], 0.9, simple=True); kit(T["wait"], T["y2025"], "soft", 0.9)
for j in range(46): tick(T["wait"] + (at("wait", 4) - T["wait"]) * (1 - (1 - j / 46) ** 0.5) * 1.0, 0.18, 2600)
# 2025: adventure gallop
groove(T["y2025"], T["newsp"], 0.95, ld="whistle", style="gallop")
whoosh(at("y2025", 2.5), 0.4, 0.8, 600); popfx(at("y2025", 3.3), 0.6)
# newsp: small accent
stab(T["newsp"], 0.9, "Dm"); timp(T["newsp"], 38, 0.6); ding(T["newsp"] + 0.05, 0.4, 2937)
groove(T["newsp"], T["size"], 0.85, ld="tpt", style="full")
# size
groove(T["size"], T["nofood"], 0.8, ld=None, style="lite")
slide(at("size", 0.5), 400, 700, 0.9, 0.5); slide(at("size", 2.5), 400, 1000, 1.3, 0.5)
# nofood
groove(T["nofood"], T["home"], 0.8, ld="twang", style="half")
popfx(at("nofood", 1), 0.5); bloop(at("nofood", 2.8), 0.5); buzz(at("nofood", 3.2), 0.5)
# home: rain + guitar + bells
wind(T["home"], T["pose"], 0.8); arp(T["home"], T["pose"], 0.9); bass(T["home"], T["pose"], 0.6, simple=True); kit(T["home"], T["pose"], "soft", 0.8)
for j in range(10): drip(T["home"] + 0.2 + j * 0.42, 0.25, 800 + 70 * (j % 4), pan=0.4 * (-1) ** j)
bell(at("home", 2), 77, 0.6)
# pose: poke + curl
groove(T["pose"], T["name"], 0.75, ld=None, style="lite")
popfx(at("pose", 1), 0.6, 900, 300); boing(at("pose", 1.6), 0.6); stab(at("pose", 2.5), 0.6, "A")
# name: Tibetan bowl + bells, gentle
bowl(T["name"], 0.9, 196); arp(T["name"], T["count"], 0.9); bass(T["name"], T["count"], 0.5, simple=True)
bell(at("name", 1), 74, 0.8); bell(at("name", 2.5), 81, 0.6)
# count
groove(T["count"], T["card"], 0.85, ld="twang", style="full")
for j in range(8): tick(at("count", 2) + j * 0.07, 0.25, 2600 + 80 * j)
ding(at("count", 2.6), 0.5, 2937)
# card
kit(T["card"], T["end"], "lite", 0.7); bass(T["card"], T["end"], 0.8); arp(T["card"], T["end"], 0.8)
whoosh(T["card"] + 0.02, 0.25, 0.8, 900); popfx(T["card"] + 0.1, 0.6); ding(at("card", 1.5), 0.35, 2637)
# end: full + Picardy D major
FINAL = at("end", 8)
groove(T["end"], FINAL, 0.95, ld="tpt", style="gallop")
for m in (50, 57, 62, 66, 69): add(gmn("Trumpet", m + 12, 1.6, 110, 0.6), FINAL, 0.16, wet=0.4, bus="mel"); add(gmn("Nylon Guitar", m + 12, 2.0, 90, 0.8), FINAL, 0.25, wet=0.4)
add(gmn("Acoustic Bass", 38, 1.4, 120, 0.4), FINAL, 0.9); timp(FINAL, 38, 1.0); add(drum(49, 100), FINAL, 0.4, wet=0.4); bowl(FINAL + 0.3, 0.6, 294)

# tape wow / flutter on the melodic bus (the Balatro wobble)
tt__ = np.arange(N) / SR
off = (0.0012 * np.sin(2 * np.pi * 0.45 * tt__) + 0.0006 * np.sin(2 * np.pi * 5.3 * tt__)) * SR
idx = np.clip(np.arange(N) - 300 + off, 0, N - 2); i_ = idx.astype(int); f_ = (idx - i_)[:, None]
MIX += MEL[i_] * (1 - f_) + MEL[i_ + 1] * f_
# ---------------- mix ----------------
def reverb(x, sec=1.6, dec=3.2):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * dec); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
d = int(3 * S16 * SR)
for r in range(1, 4):
    sh = ECHO[: N - d * r] * (0.4 ** r)
    MIX[d * r:, 0] += sh[:, 1] * (0.8 if r % 2 else 0.3); MIX[d * r:, 1] += sh[:, 0] * (0.3 if r % 2 else 0.8)
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
# tape stop HOOK_STOP -> HOOKCUT
i0, i1 = int(HOOK_STOP * SR), int(HOOKCUT * SR); n = i1 - i0
rate = np.linspace(1, 0.02, n) ** 1.4; p = i0 + np.cumsum(rate); p = np.clip(p, 0, N - 2); ii = p.astype(int); ff = (p - ii)[:, None]
seg = MIX[ii] * (1 - ff) + MIX[ii + 1] * ff; seg *= np.linspace(1, 0.3, n)[:, None]
MIX[i0:i1] = seg; MIX[i1:int((HOOKCUT + 0.08) * SR)] *= np.linspace(0.3, 1, int(0.08 * SR))[:, None]
for a, b in SILENCES:
    i0, i1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.04 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] = 0
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.2); MIX /= np.abs(MIX).max() / 0.85
fo = int(0.8 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("/workspace/work/wormlion/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG2 %.2f" % (BPM, DUR, BIG2))
