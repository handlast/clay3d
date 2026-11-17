# 《戳一下就闪绿光》BGM (copied engine from croc) (structure rules: /workspace/work/distill_music/structure.md) — one 2-bar motif M, 8-bar sentence/period themes, flamenco cadences.
# v1 — "whitewater raga-funk": sitar riff + conga/tabla-style hand drums + dulcimer (santoor) ripples + bansuri-ish flute,
# D phrygian-dominant over a D drone, 108 BPM 4/4. Real SFX from Sonniss GDC 2026 (/workspace/sfx). ADAPTIVE: built only from cues.py.
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf"); sys.path.insert(0, "/workspace/sfx")
from samp import gm as _gm, drum as _drum, SR
from sfx import sfx
from cues import *
N = int(SR * (DUR + 0.2)); MIX = np.zeros((N, 2)); MEL = np.zeros((N, 2)); VERB = np.zeros((N, 2)); ECHO = np.zeros((N, 2)); DUCK = np.ones(N)
rng = np.random.default_rng(11)
def add(y, t0, g=1.0, pan=0.0, wet=0.0, echo=0.0, human=True, bus=None):
    if y.ndim == 1: y = np.stack([y, y], 1)
    if human: g *= 1 + rng.uniform(-0.06, 0.06); t0 += rng.uniform(-0.003, 0.003)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    (MEL if bus == "mel" else MIX)[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet
    if echo: ECHO[i:i + len(y)] += y * echo
FX = np.zeros((N, 2))   # sfx bus: not ducked
def addfx(y, t0, g=1.0, pan=0.0, wet=0.0, peak=True):
    """align sample by its loudest point to t0 (distilled rule), small random pitch handled by caller"""
    if peak and len(y): t0 -= min(np.argmax(np.abs(y)) / SR, 0.25)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g; y2 = np.stack([y * (1 - max(pan, 0)), y * (1 + min(pan, 0))], 1)
    FX[i:i + len(y)] += y2
    if wet: VERB[i:i + len(y)] += y2 * wet
def duck(t0, depth=0.4, rel=0.6):
    i = int(t0 * SR); n = int(rel * SR); env = 1 - (1 - depth) * np.exp(-np.arange(n) / (n / 4))
    DUCK[i:i + n] = np.minimum(DUCK[i:i + n], env[: max(0, min(n, N - i))])
_PK = {}
@functools.lru_cache(maxsize=None)
def gmn(name, m, dur=0.5, vel=100, release=0.2, bank=0):
    if (name, bank) not in _PK: _PK[(name, bank)] = np.abs(_gm(name, 60, 0.5, 100, release=0.2, bank=bank)).max() + 1e-6
    return _gm(name, m, dur, vel, release=release, bank=bank) / _PK[(name, bank)] * 0.5
@functools.lru_cache(maxsize=None)
def dr(n, vel=100):
    y = _drum(n, vel); return y / (np.abs(y).max() + 1e-6) * 0.5
tt_ = lambda d: np.arange(int(d * SR)) / SR
S8 = BEAT / 2; S16 = BEAT / 4
def org(t0): return BIG2 if t0 >= BIG2 - 1e-4 else G0
def grid(t0, t1, div=4):
    O = org(t0); out = []; b0 = int(math.floor((t0 - O) / BAR)) - 1
    for b in range(b0, b0 + 300):
        s0 = O + b * BAR
        if s0 > t1 + 0.1: break
        for k in range(div * BPB):
            tt = s0 + k * BEAT / div + (0.02 * BEAT if (div == 4 and k % 2) else 0)
            if t0 - 1e-4 <= tt < t1 - 1e-4: out.append((tt, k, b))
    return out


# ================= HARMONY: E dorian "deep-sea alarm lounge-funk" (vibraphone / tine EP / fretless / celesta / crystal / sonar), 100 BPM =================
SC = [64, 66, 67, 69, 71, 73, 74]
CH = {"Em7": (52, 55, 59, 62), "A7": (57, 61, 64, 67), "C": (55, 60, 64, 71), "D": (54, 57, 62, 66), "Bm7": (54, 57, 59, 62)}
ROOT = {"Em7": 40, "A7": 45, "C": 48, "D": 50, "Bm7": 47}
PCS = {k: {m % 12 for m in v} | ({2} if k == "Em7" else set()) for k, v in CH.items()}
def bt(bar): return BIG2 + bar * BAR
LOOP = ["Em7", "A7", "C", "D"]
HAR = [(-99, "Em7"), (-3.5, "Em7"), (-2.25, "C"), (-1.5, "D"), (-0.75, "D")]
for b in range(0, 36): HAR.append((b, LOOP[b % 4]))
for b0, c in ((9, "Bm7"), (21, "Bm7"), (26, "C"), (27, "Bm7"), (28, "C"), (29, "D"), (33, "Em7"), (34, "Em7")): HAR.append((b0, c))
HAR.sort(key=lambda x: x[0])
def ch(tt):
    b = (tt - BIG2) / BAR + 1e-6; c = "Em7"
    for b0, name in HAR:
        if b >= b0: c = name
    return c
def pitch(dg, base=0): o, r = divmod(dg, 7); return SC[r] + 12 * o + base
G = {"vib": 1.5, "ep": 0.9, "bass": 1.2, "cel": 1.0, "siren": 0.5}
# ---- motif family: one cell (rise E-G-B then step down) fitted per chord; every strong note (16th pos 0/8) is a chord tone
PH = {"Em7": [(0, 0, 2), (2, 2, 2), (4, 4, 4), (8, 6, 2), (10, 4, 2), (12, 2, 4)],      # E G B | D B G
      "A7":  [(0, 5, 3), (3, 4, 1), (4, 3, 4), (8, 0, 6)],                               # C# B A | E
      "C":   [(0, 2, 2), (2, 4, 2), (4, 7, 4), (8, 4, 2), (10, 3, 2), (12, 2, 4)],      # G B E' | B A G
      "D":   [(0, 1, 2), (2, 3, 2), (4, 6, 4), (8, 6, 4), (12, 8, 4)],                   # F# A D' | D F#'
      "Bm7": [(0, 4, 4), (4, 6, 2), (6, 4, 2), (8, 3, 6), (14, 1, 2)]}                  # B D B | A F#
def inv(ev): return [(p, 4 - (d - 4), l) for p, d, l in ev]
def aug(ev): return [(p * 2, d, l * 2) for p, d, l in ev]
LOG = []
def lead(t0, ev, inst, base=0, g=1.0, vel=104, tag="", strong=True):
    for p, d, l in ev:
        tt = t0 + p * S16 + (0.02 * BEAT if p % 2 else 0); c = ch(tt + 1e-3); m = pitch(d, base)
        if inst == "Vibraphone": add(gmn("Vibraphone", m, S16 * l + 0.4, vel, 0.5), tt, 0.3 * g * G["vib"], pan=0.12, wet=0.35, echo=0.2, bus="mel")
        elif inst == "Celeste": add(gmn("Celeste", m, S16 * l + 0.3, vel, 0.4), tt, 0.26 * g * G["cel"], pan=-0.2, wet=0.45, echo=0.3, bus="mel")
        elif inst == "Square Lead": add(gmn("Square Lead", m, S16 * l * 0.95, vel, 0.1), tt, 0.12 * g * G["siren"], wet=0.3, echo=0.2, bus="mel")
        else: add(gmn(inst, m, S16 * l, vel, 0.3), tt, 0.24 * g, wet=0.3, echo=0.15, bus="mel")
        if strong: LOG.append((tt, round(((tt - org(tt)) / S16)) % 16, m, c, inst, tag))
def phrase(b0, nb, inst, base=0, g=1.0, op=None, vel=104, step=1, tag=""):
    for j in range(0, nb, step):
        t0 = bt(b0 + j); ev = PH[ch(t0 + 1e-3)]
        if op: ev = op(ev)
        lead(t0, [e for e in ev if e[0] < 16 * step], inst, base, g, vel, tag)
# ================= accompaniment =================
def fbass(t0, t1, g=1.0, busy=True):       # fretless funk line: root on 1, octave pop, approach note
    for tt, k, b in grid(t0, t1, 4):
        c = ch(tt + 1e-3); r = ROOT[c]; kk = k % 16
        pat = {0: r, 3: r, 6: r + 12, 8: r + 7, 11: r + 10, 14: r - 1 if busy else None} if busy else {0: r, 8: r + 7}
        m = pat.get(kk)
        if m is None: continue
        add(gmn("Fretless Bass", m, S16 * (3 if kk in (0, 8) else 1.6), 100, 0.1), tt, 0.42 * g * G["bass"])
def ep(t0, t1, g=1.0):                     # tine EP offbeat stabs
    for tt, k, b in grid(t0, t1, 2):
        if k % 2 == 1 and k % 8 != 7:
            for j, m in enumerate(CH[ch(tt + 1e-3)]): add(gmn("Tine Electric Piano", m + 12, S8 * 0.8, 80, 0.2), tt + j * 0.006, 0.07 * g * G["ep"], pan=-0.3, wet=0.25)
def cel(t0, t1, g=1.0):                    # celesta 16th arpeggio = bioluminescent sparkle
    for tt, k, b in grid(t0, t1, 4):
        c = CH[ch(tt + 1e-3)]; m = (c[0] + 24, c[1] + 24, c[2] + 24, c[3] + 12)[k % 4]
        add(gmn("Celeste", m, 0.3, 60 + 16 * (k % 4 == 0), 0.3), tt, 0.1 * g * G["cel"], pan=0.4 * math.sin(k * 0.7), wet=0.4, echo=0.2)
def kit(t0, t1, g=1.0, style="full"):
    for tt, k, b in grid(t0, t1, 4):
        kk = k % 16
        if style in ("full", "build") and kk in (0, 7, 10) or (style == "half" and kk == 0): add(dr(36, 112), tt, 0.62 * g)
        if style in ("full", "build") and kk in (4, 12) or (style == "half" and kk == 8): add(dr(37, 100), tt, 0.32 * g, wet=0.15)
        if style != "none" and kk % 2 == 0: add(dr(42, 50 + 25 * (kk % 4 == 2)), tt, 0.13 * g, pan=0.35)
        if style == "full" and kk == 14: add(dr(46, 70), tt, 0.1 * g, pan=0.35)
        if kk % 2 == 1: add(dr(82, 50), tt, 0.08 * g, pan=-0.4)
        if style == "build" and kk >= 8: add(dr(38, 45 + 4 * kk), tt, 0.14 * g * (0.4 + kk / 16))
def band(t0, t1, g=1.0, style="full", arp=False):
    kit(t0, t1, g, style); fbass(t0, t1, g); ep(t0, t1, g)
    if arp: cel(t0, t1, g * 0.8)
def ping(t0, g=1.0, f=1350):
    t = tt_(1.2); y = np.sin(2 * np.pi * f * t) * np.exp(-t * 5) * 0.35 + np.sin(2 * np.pi * f * 2.01 * t) * np.exp(-t * 9) * 0.08
    add(y, t0, g, wet=0.6, echo=0.5, human=False)
def taiko(t0, g=1.0): add(gmn("Taiko Drum", 36, 1.5, 127, 0.8), t0, 0.9 * g, wet=0.35)
def sub(t0, g=1.0, dur=1.2):
    t = tt_(dur); f = 34 + 70 * np.exp(-t * 14)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) * 0.8, t0, g, human=False)
def chordhit(t0, c="Em7", g=1.0):
    for m in CH[c]: add(gmn("Vibraphone", m + 12, 1.6, 120, 0.8), t0, 0.22 * g, wet=0.5, bus="mel"); add(gmn("Tine Electric Piano", m, 1.6, 110, 0.8), t0, 0.14 * g, wet=0.5)
_vr = np.random.default_rng(3)
def V(): return float(2 ** (_vr.uniform(-1, 1) / 12))
def s_pop(t0, g=0.35): addfx(sfx(111, pitch=V()), t0, g, pan=0.1)
def s_snap(t0, g=0.4): addfx(sfx(109, pitch=V()), t0, g)
def s_deny(t0, g=0.45): addfx(sfx(119), t0, g)
def s_whoosh(t0, g=0.32): addfx(sfx(71, dur=0.9, pitch=V()), t0, g, pan=0.2)
def s_bub(t0, g=0.3): addfx(sfx(94, pitch=V()), t0, g, pan=-0.2)
def s_twinkle(t0, g=0.3): addfx(sfx(127), t0, g, wet=0.3)
def s_shimmer(t0, g=0.3): addfx(sfx(143, dur=1.5, fade=0.4), t0, g, wet=0.3)
def s_glass(t0, g=0.3): addfx(sfx(152, dur=1.2, fade=0.3, pitch=V()), t0, g, wet=0.3)
def s_boom(t0, g=0.8): addfx(sfx(209, dur=2.5, fade=0.3), t0, g, wet=0.2)
def s_drop(t0, g=0.4): addfx(sfx(70, pitch=V()), t0, g, wet=0.3)
def click(t0, g=0.25): addfx(sfx(149, pitch=V()), t0, g)
def thunk(t0, g=0.4): addfx(sfx(165), t0, g)
def flashsnd(t0, n=3, per=0.4, g=0.3):
    for i in range(n): add(gmn("Crystal", 88 - (i % 2) * 5, 0.5, 100, 0.3), t0 + i * per, 0.22 * g * (1 - 0.15 * i), wet=0.5, echo=0.3, bus="mel")
def amb(t0, t1, g=0.06): addfx(sfx(117, dur=t1 - t0 + 0.5, fade=0.4), t0, g, peak=False)
def big(t0, g=1.0):
    taiko(t0, g); sub(t0, 1.0 * g); s_boom(t0, 0.75 * g); add(dr(49, 127), t0, 0.45 * g, wet=0.4); add(dr(36, 127), t0, 0.8 * g)
    chordhit(t0, "Em7", g); duck(t0 + 0.02, 0.4, 0.9)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; u = t / (t1 - t0)
    nz = rng.standard_normal(n); y = nz - np.convolve(nz, np.ones(6) / 6, "same")
    add(y * u ** 2 * 0.07, t0, g, human=False)
    for j in range(int((t1 - t0) / S16)): add(gmn("Celeste", 76 + (j % 7) * 2, S16, 80, 0.1), t0 + j * S16, 0.12 * g * (0.4 + 0.6 * j * S16 / (t1 - t0)), bus="mel")
def siren(t0, t1, g=1.0):        # two-tone B-E alarm in quarter notes, quiet, square lead
    for tt, k, b in grid(t0, t1, 1):
        m = 71 if k % 2 == 0 else 76
        add(gmn("Square Lead", m, BEAT * 0.9, 90, 0.1), tt, 0.07 * g, pan=0.3 * (1 if k % 2 else -1), wet=0.3)
# =============== ARRANGEMENT (bars from BIG2) ===============
amb(0, DUR, 0.05)
# hook: ACCENT 1 + three crystal blinks, tape-stop
big(HOOK_HIT, 1.0); band(HOOK_HIT, HOOK_STOP, 1.0, arp=True); flashsnd(0.02, 3, 0.45, 1.0)
lead(HOOK_HIT, PH["Em7"], "Vibraphone", tag="hook M")
# deep: descending sonar pings, bass only
for j in range(int((T["q"] - T["deep"]) / (2 * BEAT))): ping(T["deep"] + j * 2 * BEAT, 0.5, 1350 - j * 120)
fbass(T["deep"], T["q"], 0.6, busy=False); kit(T["deep"], T["q"], 0.4, "none")
s_bub(at("deep", 3.2), 0.3); s_pop(at("deep", 3.3), 0.3)
riser(T["q"] + BEAT * 0.5, BIG2 - BEAT / 4, 0.6); s_pop(T["q"] + 0.05, 0.35)
# ---- A (0-9): reveal..rov: ACCENT 2, full groove, vibes sentence
big(BIG2, 1.1)
band(bt(0), bt(9), 1.0)
phrase(0, 4, "Vibraphone", tag="A1"); phrase(4, 4, "Vibraphone", base=12, g=0.8, tag="A2 8va")
phrase(8, 1, "Celeste", base=12, tag="A tail")
s_shimmer(BIG2 + 0.05, 0.25); s_pop(at("reveal", 2), 0.3)
s_deny(at("notcoral", 1), 0.3); s_pop(at("notcoral", 2), 0.3)
for i in range(8): s_pop(at("host", 2) + i * 0.12, 0.12)
s_pop(at("host", 0.8), 0.3); s_pop(at("size", 0.6), 0.3); click(at("size", 3), 0.3); click(at("size", 4), 0.3)
s_whoosh(at("rov", 1.5), 0.25); ping(at("rov", 0.5), 0.4)
# ---- poke (9-10): breakdown, sonar, held breath
kit(bt(9), bt(10), 0.35, "none"); fbass(bt(9), bt(10), 0.6, busy=False)
ping(bt(9), 0.6); ping(bt(9) + 2 * BEAT, 0.5)
riser(bt(9) + 2 * BEAT, bt(10) - S16, 0.45)
# ---- flash (10) light hit (not a 3rd big accent): crystal blinks + celesta arp groove (B 10-17.5)
flashsnd(T["flash"], 5, 0.4, 1.3); s_glass(T["flash"], 0.3)
band(bt(10), bt(17.5), 0.95, arp=True)
phrase(10, 4, "Vibraphone", tag="B call"); phrase(14, 3, "Celeste", base=12, g=0.9, tag="B answer")
for i in range(3): s_twinkle(at("spread", 0.5) + i * 0.5, 0.15)
s_pop(at("spread", 2.5), 0.3); click(at("first", 0.3), 0.3); s_pop(at("first", 3), 0.35)
click(at("lab", 1), 0.3); s_drop(at("lab", 4) + 0.3, 0.3); s_pop(at("lab", 0.2), 0.25)
# ---- C (17.5-22.5): nm/self/why: half-time, inverted motif augmented on celesta
kit(bt(17.5), bt(22.5), 0.65, "half"); fbass(bt(17.5), bt(22.5), 0.8, busy=False); ep(bt(17.5), bt(22.5), 0.7)
phrase(18, 3, "Celeste", base=12, g=0.85, tag="C celesta"); phrase(21, 1, "Vibraphone", base=-12, g=1.1, tag="C low vib")
s_shimmer(at("nm", 1.5), 0.25); s_pop(at("nm", 3), 0.25)
s_pop(at("self", 0.3), 0.25); s_whoosh(at("self", 1), 0.15); s_deny(at("self", 4.6), 0.3)
s_pop(at("why", 0.2), 0.3); s_pop(at("why", 2.5), 0.25)
# ---- alarm (22.5-26): build drums + quiet siren + crystal blinks; eat: chase groove
band(bt(22.5), bt(24.5), 1.0, "build"); siren(at("alarm", 2), bt(24.5), 1.0)
flashsnd(at("alarm", 2), 6, 0.38, 1.0); thunk(at("alarm", 2), 0.35)
s_whoosh(at("alarm", 4), 0.3)
band(bt(24.5), bt(26), 1.0, arp=True); phrase(25, 1, "Vibraphone", base=12, g=0.85, tag="chase 8va")
s_whoosh(at("eat", 0.5), 0.3); s_pop(at("eat", 2.8), 0.3)
# ---- D (26-30): maybe/card: breath, kalimba-ish celesta cells, sonar
fbass(bt(26), bt(30), 0.85, busy=False); kit(bt(26), bt(30), 0.6, "half"); ep(bt(27.5), bt(30), 0.6); cel(bt(27.5), bt(30), 0.8)
phrase(26, 2, "Celeste", base=12, g=0.6, vel=88, tag="D soft")
ping(bt(26), 0.4); thunk(at("maybe", 0.3), 0.3); s_pop(at("maybe", 2), 0.25)
s_whoosh(T["card"] + 0.05, 0.2); s_pop(T["card"] + 0.12, 0.3)
for i in range(3): s_pop(at("card", 1.2 + i * 0.8), 0.2)
# ---- E (30-34.5): top10 + end: fullest final statement, no third accent, hold tonic
band(bt(30), bt(33), 1.1, arp=True)
phrase(30, 3, "Vibraphone", tag="final"); phrase(30, 3, "Celeste", base=12, g=0.6, tag="final dbl")
s_shimmer(at("top10", 0.5), 0.3); s_pop(at("top10", 2), 0.3)
FINAL = bt(33)
lead(FINAL, [(0, 0, 16)], "Vibraphone", tag="final tonic"); chordhit(FINAL, "Em7", 0.8); fbass(FINAL, FINAL + BEAT * 0.5, 0.9, busy=False)
flashsnd(at("end", 1.6), 3, 0.4, 1.0); s_pop(T["end"] + 0.05, 0.3)
ping(FINAL + 2 * BEAT, 0.35)
# ---- structure checks
nonc = [(round(t, 2), p, m, c, tag) for t, p, m, c, i, tag in LOG if p in (0, 8) and (m % 12) not in PCS[c]]
strong = [x for x in LOG if x[1] in (0, 8)]
print("strong-beat lead notes %d, non-chord %d (%.0f%%)" % (len(strong), len(nonc), 100 * len(nonc) / max(1, len(strong))))
for x in nonc: print("  nonchord", x)
# ---------------- mix ----------------
tt__ = np.arange(N) / SR   # gentle wow on melodic bus
off = (0.0009 * np.sin(2 * np.pi * 0.4 * tt__) + 0.0004 * np.sin(2 * np.pi * 5.1 * tt__)) * SR
idx = np.clip(np.arange(N) - 200 + off, 0, N - 2); i_ = idx.astype(int); f_ = (idx - i_)[:, None]
MIX += MEL[i_] * (1 - f_) + MEL[i_ + 1] * f_
def reverb(x, sec=1.8, dec=3.0):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * dec); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
d = int(3 * S16 * SR)
for r in range(1, 4):
    sh = ECHO[: N - d * r] * (0.4 ** r)
    MIX[d * r:, 0] += sh[:, 1] * (0.8 if r % 2 else 0.3); MIX[d * r:, 1] += sh[:, 0] * (0.3 if r % 2 else 0.8)
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
# tape stop HOOK_STOP -> HOOKCUT (music only)
i0, i1 = int(HOOK_STOP * SR), int(HOOKCUT * SR); n = i1 - i0
rate = np.linspace(1, 0.02, n) ** 1.4; p = i0 + np.cumsum(rate); p = np.clip(p, 0, N - 2); ii = p.astype(int); ff = (p - ii)[:, None]
seg = MIX[ii] * (1 - ff) + MIX[ii + 1] * ff; seg *= np.linspace(1, 0.3, n)[:, None]
MIX[i0:i1] = seg; i2 = int((HOOKCUT + 0.08) * SR); MIX[i1:i2] *= np.linspace(0.3, 1, i2 - i1)[:, None]
MIX = MIX / (np.abs(MIX).max() + 1e-9)
MIX = MIX * DUCK[:, None] + FX * 0.9
MIX = np.tanh(MIX * 1.8); MIX /= np.abs(MIX).max() / 0.85
MIX = MIX[: int(SR * DUR)]
fo = int(1.2 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
with wave.open("/workspace/work/glow/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG2 %.2f" % (BPM, DUR, BIG2))
