# 《天蛾的超声干扰器》BGM — 80s synthwave spy thriller, A minor (Am-F-Dm-E), 116 BPM 4/4. ADAPTIVE: built only from cues.py.
# Synth Bass 2 16th octaves, gated Polysynth offbeats, Crystal arp, Saw Lead spy motif; sonar pings, genital-scale rasps, radar static.
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
PROG = ["Am", "F", "Dm", "E"]
CH = {"Am": (57, 60, 64, 67), "F": (53, 57, 60, 64), "Dm": (50, 57, 60, 65), "E": (52, 56, 59, 62)}
ROOT = {"Am": 33, "F": 29, "Dm": 38, "E": 28}
def chord_of(b): return PROG[ph(b) % 4]
MELO = [[(0, 69, 2), (2, 72, 1), (3, 71, 1), (4, 69, 2), (6, 64, 2)],
        [(0, 65, 2), (2, 69, 1), (3, 72, 1), (4, 76, 3), (7, 74, 1)],
        [(0, 74, 2), (2, 72, 1), (3, 69, 1), (4, 65, 2), (6, 69, 2)],
        [(0, 68, 3), (3, 71, 1), (4, 74, 2), (6, 76, 2)]]
def bass(t0, t1, g=1.0, simple=False):
    for tt, k, b in sixteenths(t0, t1):
        if simple and k % 4: continue
        r = ROOT[chord_of(b)] + (12 if k % 2 else 0)
        add(gmn("Synth Bass 2", r, S16 * 0.8, 115 if k % 4 == 0 else 95, 0.03), tt, 0.77 * g * (1.0 if k % 4 == 0 else 0.75))
def pads(t0, t1, g=1.0):
    for tt, e, b in eighths(t0, t1):
        if e % 2 == 1:
            for m in CH[chord_of(b)]: add(gmn("Polysynth", m, S8 * 0.55, 90, 0.08), tt, 0.33 * g, pan=-0.2, wet=0.35, bus="mel")
def strings(t0, t1, g=1.0):
    for tt, e, b in eighths(t0, t1):
        if e == 0:
            for m in CH[chord_of(b)]: add(gmn("Synth Strings 1", m + 12, BAR * 0.98, 70, 0.5), tt, 0.25 * g, pan=0.25, wet=0.4, bus="mel")
def arp(t0, t1, g=1.0, oct_=24):
    for tt, k, b in sixteenths(t0, t1):
        ch = CH[chord_of(b)]; m = ch[[0, 1, 2, 3, 2, 1, 2, 3][k % 8]] + oct_
        add(gmn("Crystal", m, S16 * 1.5, 80, 0.15), tt, 0.35 * g, pan=0.35 * math.sin(k * 0.8), echo=0.25, bus="mel")
def lead(t0, t1, g=1.0, up=0):
    for tt, e, b in eighths(t0, t1):
        for pos, m, du in MELO[ph(b) % 4]:
            if pos == e:
                add(gmn("Saw Lead", m + up, du * S8 * 0.9, 105, 0.12), tt, 2.0 * g, pan=-0.05, wet=0.3, echo=0.3, bus="mel")
                add(gmn("Square Lead", m + up - 12, du * S8 * 0.9, 90, 0.12), tt, 0.6 * g, pan=0.15, bus="mel")
def kit(t0, t1, style="full", g=1.0):
    g *= 0.7
    for tt, k, b in sixteenths(t0, t1):
        e = k // 2; on8 = k % 2 == 0
        if style in ("full", "lite") and on8 and e % 2 == 0: add(drum(36, 120), tt, 0.85 * g)
        if style == "half" and k == 0: add(drum(36, 120), tt, 0.85 * g)
        if style in ("full", "lite") and on8 and e in (2, 6): add(drum(38, 110), tt, 0.4 * g, wet=0.45); add(drum(39, 100), tt, 0.35 * g, wet=0.45)
        if style == "half" and k == 8: add(drum(38, 110), tt, 0.4 * g, wet=0.5); add(drum(39, 100), tt, 0.35 * g, wet=0.5)
        if style in ("full", "half", "hat"): add(drum(42, 100 if k % 4 == 0 else (75 if on8 else 55)), tt, 1.0 * g, pan=0.3)
        if style == "lite" and on8: add(drum(42, 80), tt, 0.8 * g, pan=0.3)
        if style == "full" and k % 4 == 2: add(drum(46, 70), tt, 0.12 * g, pan=-0.3)
        if style == "soft" and k == 0: add(drum(36, 95), tt, 0.55 * g)
def groove(t0, t1, g=1.0, ld=True, up=0, style="full", ar=True):
    kit(t0, t1, style, g); bass(t0, t1, g); pads(t0, t1, g)
    if ar: arp(t0, t1, g)
    if ld: lead(t0, t1, g, up)
def big(t0, g=1.0):
    boom(t0, 1.2 * g, 1.3); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 127), t0, 0.6 * g, wet=0.35); add(drum(57, 110), t0 + 0.01, 0.3 * g, pan=0.4)
    for m in (57, 64, 69, 72): add(gmn("Synth Brass 1", m, 0.8, 125, 0.3), t0, 0.22 * g, wet=0.35, bus="mel")
    add(gmn("Orchestra Hit", 69, 0.6, 125, 0.2), t0, 0.35 * g, wet=0.35)
    add(gmn("Synth Bass 2", 21, 0.9, 127, 0.2), t0, 0.9 * g)
def stab(t0, g=1.0, ch="Am"):
    for m in CH[ch]: add(gmn("Synth Brass 1", m + 12, 0.25, 110, 0.15), t0, 0.12 * g, wet=0.3, bus="mel")
# --- themed sfx ---
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
# hook: bat pings -> BIG hit (moth jams) -> full groove -> tape stop
for j in range(5): batping(-0.05 + j * 0.09, 0.8, pan=-0.4)
big(HOOK_HIT); rasp(HOOK_HIT, "cont", 0.7, 1.2); static(HOOK_HIT + 0.15, 1.0, 0.9)
groove(HOOK_HIT, HOOK_STOP + 0.3, 1.0)
# chase: bass pulse + arp, sonar pings on every beat
kit(HOOKCUT, T["ping"], "hat", 0.8); bass(HOOKCUT, T["ping"], 0.85); arp(HOOKCUT, T["ping"], 0.8); strings(HOOKCUT, T["ping"], 0.8)
for b in range(1, 6): batping(at("chase", b), 0.7, pan=-0.3); batping(at("chase", b) + 0.08, 0.4, pan=-0.3)
# ping: half-time, call + echo
kit(T["ping"], T["lock"], "half", 0.8); bass(T["ping"], T["lock"], 0.8, simple=True); pads(T["ping"], T["lock"], 0.8)
for t0 in (at("ping", 0.3), at("ping", 4)):
    for j in range(3): batping(t0 + j * 0.1, 0.9, pan=-0.4)
    for j in range(3): batping(t0 + 0.6 + j * 0.1, 0.45, 4200, 1500, pan=0.4)
popfx(at("ping", 0.3), 0.4); popfx(at("ping", 1.6), 0.4, 900, 400); ding(at("ping", 4.5), 0.35, 1760)
# lock: accelerating beeps -> solid tone
kit(T["lock"], T["q"], "hat", 0.8); bass(T["lock"], T["q"], 0.9)
tb = at("lock", 0.3); gap = 0.32
while tb < at("lock", 2):
    beep(tb, 1500, 0.06, 0.9); tb += gap; gap = max(0.07, gap * 0.78)
beep(at("lock", 2), 1500, 0.5, 0.8); stab(at("lock", 2), 0.8, "E")
# q: heartbeat + riser into BIG2
for b in range(0, 3): heart(at("q", b), 0.8)
riser(T["lock"], BIG2, 1.0); add(gm("Reverse Cymbal", 60, 1.6, 110), BIG2 - 1.6, 0.45)
# BIG2: the counter-attack
big(BIG2, 1.1); rasp(BIG2, "cont", 0.9, 1.3); static(BIG2 + 0.2, 1.2, 0.8)
for j in range(4): rasp(BIG2 + j * 0.45, "cont", 0.35, 0.7)
groove(BIG2, T["jam"], 1.0, up=12)
# jam: static + whoosh miss
groove(T["jam"], T["organ"], 0.85, ld=False, style="lite")
static(T["jam"], 1.4, 0.6); whoosh(at("jam", 1.5), 0.8, 1.2, 300); whoosh(at("jam", 2.6), 0.3, 0.9, 900)
# organ: breakdown, arp + strings, no drums
arp(T["organ"], T["scale"], 0.9); strings(T["organ"], T["scale"], 1.0); bass(T["organ"], T["scale"], 0.6, simple=True)
for b in (1.5, 2.5, 3.5): ding(at("organ", b), 0.3, 2093)
popfx(at("organ", 1), 0.5); popfx(at("organ", 3), 0.4)
# scale: microscope pops
kit(T["scale"], T["way"], "soft", 0.8); arp(T["scale"], T["way"], 0.9); bass(T["scale"], T["way"], 0.7, simple=True); pads(T["scale"], T["way"], 0.7)
for i in range(15): popfx(at("scale", 1.2) + i * 0.08, 0.35, 1400 + 40 * i, 600)
ding(at("scale", 3), 0.35, 2637)
# way: three cards, tom pops
groove(T["way"], T["w1"], 0.85, ld=False, style="lite")
for i in range(3): add(drum(45 + 3 * i, 110), at("way", 1 + i), 0.12); stab(at("way", 1 + i), 0.6, chord_of(0))
# w1: scale-on-scale bursts
kit(T["w1"], T["w1b"], "half", 0.8); bass(T["w1"], T["w1b"], 0.8); pads(T["w1"], T["w1b"], 0.7)
tt0 = T["w1"] + 0.1
while tt0 < T["w1b"] - 0.3: rasp(tt0, "burst", 0.45, 0.9); tt0 += 0.7
# w1b: startle / yuck
groove(T["w1b"], T["w2"], 0.75, ld=False, style="lite", ar=False)
boing(at("w1b", 0.3), 0.6); stab(at("w1b", 0.35), 0.6, "E"); bloop(at("w1b", 3.5), 0.6, 600, 200); popfx(at("w1b", 3.6), 0.4)
# w2: spines, continuous
groove(T["w2"], T["w3"], 0.8, ld=False, style="half")
tt0 = T["w2"] + 0.1
while tt0 < T["w3"] - 0.3: rasp(tt0, "cont", 0.4, 0.7); tt0 += 0.7
# w3: bumps, new discovery
groove(T["w3"], T["jam2"], 0.8, ld=False, style="half")
tt0 = T["w3"] + 0.1
while tt0 < T["jam2"] - 0.3: rasp(tt0, "fine", 0.4, 0.7, pan=-0.2); tt0 += 0.7
ding(at("w3", 4), 0.45, 3136); stab(at("w3", 4), 0.6, "Am")
# jam2: full groove, verdict
groove(T["jam2"], T["count"], 0.9)
static(at("jam2", 3.5), 0.8, 0.6); popfx(at("jam2", 3.6), 0.5)
# count: ticks as moths light up
groove(T["count"], T["evo"], 0.8, ld=False, style="lite")
for j in range(24): tick(at("count", 2.5) + j * 0.045, 0.22, 2400 + 60 * j)
ding(at("count", 4.6), 0.4, 2637)
# evo: breakdown, star dings
strings(T["evo"], T["lose"], 1.0); kit(T["evo"], T["lose"], "soft", 0.9); bass(T["evo"], T["lose"], 0.7, simple=True); arp(T["evo"], T["lose"], 0.6)
for j in range(7): ding(at("evo", 0.6 + j * 0.45), 0.35 if j < 4 else 0.18, [1760, 2093, 2349, 2637, 3136, 3520, 3951][j])
# lose: daybreak, gear falls
groove(T["lose"], T["card"], 0.8, ld=True, style="lite", ar=False)
slide(at("lose", 3), 900, 200, 1.0, 0.6); clang(at("lose", 5), 0.6)
# card
kit(T["card"], T["end"], "lite", 0.7); bass(T["card"], T["end"], 0.8); arp(T["card"], T["end"], 0.8); strings(T["card"], T["end"], 0.8)
whoosh(T["card"] + 0.02, 0.25, 0.8, 900); popfx(T["card"] + 0.1, 0.6); ding(at("card", 1.5), 0.35, 2637)
# end
FINAL = at("end", 8)
groove(T["end"], FINAL, 0.95)
for j in range(4): rasp(T["end"] + j * 1.2, "cont", 0.3, 0.4)
for m in (45, 57, 60, 64, 69): add(gmn("Synth Brass 1", m + 12, 1.6, 110, 0.6), FINAL, 0.18, wet=0.4, bus="mel"); add(gmn("Synth Strings 1", m + 12, 2.0, 80, 0.6), FINAL, 0.12, wet=0.4, bus="mel")
add(gmn("Synth Bass 2", 33, 1.4, 120, 0.4), FINAL, 0.9); add(drum(36, 120), FINAL, 0.9); add(drum(49, 100), FINAL, 0.4, wet=0.4)
batping(FINAL + 1.0, 0.5); batping(FINAL + 1.1, 0.3)

# tape wow / flutter on the melodic bus (the Balatro wobble)
tt__ = np.arange(N) / SR
off = (0.0035 * np.sin(2 * np.pi * 0.45 * tt__) + 0.0006 * np.sin(2 * np.pi * 5.3 * tt__)) * SR
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
with wave.open("/workspace/work/moth/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG2 %.2f" % (BPM, DUR, BIG2))
