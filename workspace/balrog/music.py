# 《炎魔蟋蟀》BGM — Balatro-style 7/4 (4+3) casino jazz, darker cave flavour, E minor, 104 BPM. ADAPTIVE: built only from cues.py.
# Synth Bass + Fretless ostinato, Percussive Organ stabs, Tine EP pads, Polysynth lead doubled by vibes; melodic bus gets tape wow/flutter.
# English vocal chops via Piper TTS (sf/vox.py), lo-fi + drive, themed per scene. SFX: suction, gulp, armor clang, salt drips, ticks.
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
import vox
PROG = ["Em9", "Cmaj7", "Am9", "B7"]
CH = {"Em9": (55, 59, 62, 66), "Cmaj7": (55, 59, 60, 64), "Am9": (55, 59, 60, 64), "B7": (54, 57, 59, 63)}
ROOT = {"Em9": 40, "Cmaj7": 36, "Am9": 45, "B7": 35}
def chord_of(b): return PROG[ph(b) % 4]
BASS = [(0, 0, 2), (2, 12, 1), (3, 10, 1), (4, 7, 2), (6, 12, 1), (7, 0, 1), (8, 0, 2), (10, 7, 1), (11, 12, 1), (12, 10, 1), (13, 7, 1)]
MELO = [[(0, 71, 2), (2, 74, 1), (3, 76, 1), (4, 79, 3), (7, 78, 1), (8, 76, 2), (10, 74, 1), (11, 71, 3)],
        [(0, 72, 3), (3, 71, 1), (4, 67, 2), (6, 64, 2), (8, 67, 2), (10, 71, 4)],
        [(0, 69, 2), (2, 72, 1), (3, 76, 1), (4, 79, 2), (6, 81, 2), (8, 79, 3), (11, 76, 1), (12, 72, 2)],
        [(0, 75, 3), (3, 78, 1), (4, 81, 2), (6, 78, 2), (8, 75, 2), (10, 71, 2), (12, 69, 2)]]
def bass(t0, t1, g=1.0, simple=False):
    for tt, e, b in eighths(t0, t1):
        r = ROOT[chord_of(b)]
        for pos, iv, du in BASS:
            if pos == e and (not simple or pos in (0, 8)):
                add(gm("Synth Bass 1", r + iv, du * S8 * 0.9, 112 if pos in (0, 8) else 96, 0.05), tt, 0.7 * g)
                add(gm("Fretless Bass", r + iv, du * S8 * 0.9, 100, 0.05), tt, 0.35 * g)
def organ(t0, t1, g=1.0):
    for tt, e, b in eighths(t0, t1):
        if e in (1, 3, 6, 9, 12):
            for m in CH[chord_of(b)]: add(gm("Percussive Organ", m, S8 * (1.6 if e in (6, 12) else 0.8), 92, 0.08), tt, 0.32 * g, pan=-0.25, wet=0.2, bus="mel")
def ep(t0, t1, g=1.0):
    for tt, e, b in eighths(t0, t1):
        if e == 0:
            for m in CH[chord_of(b)]: add(gm("Tine Electric Piano", m + 12, BAR * 0.95, 70, 0.4), tt, 0.25 * g, pan=0.25, wet=0.4, bus="mel")
def lead(t0, t1, g=1.0, up=0):
    for tt, e, b in eighths(t0, t1):
        for pos, m, du in MELO[ph(b) % 4]:
            if pos == e:
                add(gm("Synth Calliope", m + up, du * S8 * 0.92, 105, 0.12), tt, 0.5 * g, pan=-0.1, wet=0.25, echo=0.15, bus="mel")
                add(gm("Vibraphone", m + up + 12, du * S8, 80, 0.3), tt, 0.25 * g, pan=0.2, wet=0.3, bus="mel")
def kit(t0, t1, style="full", g=1.0):
    for tt, e, b in eighths(t0, t1):
        if style in ("full", "lite"):
            if e in (0, 5, 8): add(drum(36, 118), tt, 0.85 * g)
            if e in (4, 11): add(drum(38, 105), tt, 0.45 * g, wet=0.2); add(drum(39, 90), tt, 0.25 * g, wet=0.2)
            if style == "full" and e in (7, 13): add(drum(37, 70), tt, 0.25 * g)
        if style in ("full", "lite", "hat"):
            add(drum(42, 95 if e in (0, 8) else 60), tt, 0.22 * g, pan=0.3)
        if style == "full" and e in (2, 10): add(drum(46, 70), tt, 0.18 * g, pan=-0.3)
        if style == "soft" and e in (0, 8): add(drum(36, 90), tt, 0.5 * g)
        if style == "soft": add(drum(53 if e in (0, 8) else 42, 70), tt, 0.15 * g, pan=0.3)
def groove(t0, t1, g=1.0, ld=True, up=0, style="full"):
    kit(t0, t1, style, g); bass(t0, t1, g); organ(t0, t1, g); ep(t0, t1, g)
    if ld: lead(t0, t1, g, up)
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
def chirp(t0, g=1.0, n=3, pan=0.0):
    for j in range(n):
        t = tt_(0.05); y = np.sin(2 * np.pi * 4300 * t) * np.sin(np.pi * t / 0.05) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 180 * t)))
        add(mono(y * 0.12), t0 + j * 0.07, g, pan=pan, wet=0.4, human=False)
def fireroar(t0, d=0.9, g=1.0):
    n = int(d * SR); t = np.arange(n) / SR; y = np.convolve(rng.standard_normal(n), np.ones(25) / 25, "same") * 6
    y *= np.minimum(1, t / 0.08) * np.exp(-t * 2.5) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t))
    add(mono(y * 0.25), t0, g, wet=0.3, human=False); boom(t0, 0.6 * g, 1.0)
fireroar(-0.1, 0.6, 1.0); whoosh(0.05, 0.3, 1.0, 300)
big(HOOK_HIT); popfx(HOOK_HIT + 0.3, 0.8, 1500, 800); chirp(HOOK_HIT + 0.4, 0.8)
groove(HOOK_HIT, HOOK_STOP + 0.3)
vo("Balrog?", qb(1.0), 1.0, "ryan", 0.8, 0.35, 2.0); vo("It's a cricket.", qb(2.4), 0.9, "lessac", 1.0)
# island: sea-breeze lite
kit(HOOKCUT, T["tunnel"], "lite", 0.8); bass(HOOKCUT, T["tunnel"], 0.8); ep(HOOKCUT, T["tunnel"], 0.9)
for tt, e, b in eighths(at("island", 1), at("island", 2.5)): tick(tt, 0.25, 2400 + 60 * e)
popfx(at("island", 3.5), 0.6); vo("Tiny island.", at("island", 2.5), 0.9, "lessac", 1.0)
# tunnel: footsteps into the dark
kit(T["tunnel"], T["walls"], "soft", 0.9); bass(T["tunnel"], T["walls"], 0.8, simple=True); organ(T["tunnel"], T["walls"], 0.7)
for b in range(2, 6): thump(at("tunnel", b), 0.4, 70)
for j in range(4): drip(at("tunnel", 2.5) + j * 0.6, 0.4, 900 + 120 * j, pan=0.4 * (-1) ** j)
vo("Twenty five meters deep.", at("tunnel", 4), 0.9, "ryan", 0.92)
# walls: crickets pop on, chirps
groove(T["walls"], T["dna"], 0.85, ld=False, style="hat")
for i in range(9): chirp(T["walls"] + 0.1 + i * 0.12, 0.5, 2, pan=0.6 * math.sin(i))
vo("Crickets everywhere!", at("walls", 1.5), 0.9, "lessac", 1.0)
# dna: scanner, riser into silence
kit(T["dna"], SIL0, "hat", 1.0); bass(T["dna"], SIL0, 0.7, simple=True)
for tt, e, b in eighths(T["dna"], SIL0): tick(tt, 0.2, 3800 if e % 2 else 3000)
vo("Check the DNA.", T["dna"] + 0.15, 0.9, "ryan", 0.92)
riser(T["dna"], SIL0, 1.0); add(gm("Reverse Cymbal", 60, 1.6, 110), BIG2 - 1.6, 0.45)
# BIG2
big(BIG2, 1.1); vo("New species!", BIG2 + 0.08, 1.2, "ryan", 0.85, 0.35, 2.2)
groove(BIG2, T["name"], 1.0, up=12); chirp(at("reveal", 1.5), 0.7)
# name: fire demon, dark
kit(T["name"], T["real"], "soft", 1.0); bass(T["name"], T["real"], 0.9); organ(T["name"], T["real"], 0.8)
fireroar(at("name", 0.5), 1.0, 0.9); vo("Named after a Balrog.", at("name", 1.8), 0.9, "lessac", 0.95)
# real: shrink to cricket
groove(T["real"], T["legs"], 0.8, ld=False)
slide(at("real", 2), 900, 300, 0.6, 0.7); popfx(at("real", 3), 0.7); chirp(at("real", 3.1), 0.7); vo("Totally harmless.", at("real", 3.3), 0.9, "ryan", 0.92)
# legs / grip
groove(T["legs"], T["genus"], 0.85)
vo("Long legs.", at("legs", 2), 0.9, "lessac", 1.0)
slide(at("grip", 2), 300, 900, 1.2, 0.6); vo("Hang on!", at("grip", 4), 1.0, "ryan", 0.9, 0.3, 1.8); thump(at("grip", 3.5), 0.6)
# genus: counting ticks
groove(T["genus"], T["fragile"], 0.85, ld=False)
for j in range(20): tick(T["genus"] + j * 0.08, 0.25, 2600 + 50 * j)
vo("Sixty eight.", at("genus", 3), 0.9, "lessac", 1.0); ding(at("genus", 4), 0.6, 2637)
# fragile: drips, dry-out
kit(T["fragile"], T["near"], "soft", 0.9); bass(T["fragile"], T["near"], 0.8, simple=True); ep(T["fragile"], T["near"], 0.9)
for j in range(5): drip(at("fragile", 0.5) + j * 0.45, 0.4, 1000 + 80 * j, pan=-0.3)
buzz(at("fragile", 5), 0.7); vo("Handle with care.", at("fragile", 5.2), 0.9, "ryan", 0.92)
# near
groove(T["near"], T["card"], 0.85)
popfx(at("near", 0.5), 0.5); popfx(at("near", 1), 0.5); ding(at("near", 3), 0.6, 3136); vo("Right next door.", at("near", 3.2), 0.9, "lessac", 1.0)
# card
kit(T["card"], T["end"], "lite", 0.7); bass(T["card"], T["end"], 0.8); organ(T["card"], T["end"], 0.9); ep(T["card"], T["end"], 0.8)
whoosh(T["card"] + 0.02, 0.25, 0.8, 900); popfx(T["card"] + 0.1, 0.6); vo("Remember this card.", at("card", 1.5), 0.9, "lessac", 0.95)
for j in range(6): tick(at("card", 0.3) + j * 0.05, 0.3, 4000)
# end
FINAL = at("end", 7)
groove(T["end"], FINAL, 0.9)
for m in (52, 59, 62, 66, 71): add(gm("Rock Organ", m, 1.6, 110, 0.6), FINAL, 0.3, wet=0.4, bus="mel"); add(gm("Tine Electric Piano", m + 12, 2.0, 80, 0.6), FINAL, 0.3, wet=0.4, bus="mel")
add(gm("Synth Bass 1", 28, 1.4, 120, 0.4), FINAL, 1.0); add(drum(36, 120), FINAL, 0.9); add(drum(49, 100), FINAL, 0.4, wet=0.4)
vo("Not so scary.", FINAL + 0.6, 1.0, "ryan", 0.9); chirp(FINAL + 1.6, 0.6)

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
with wave.open("/workspace/work/balrog/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG2 %.2f" % (BPM, DUR, BIG2))
