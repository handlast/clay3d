# 《章鱼越狱三步法》BGM (copied engine from croc) (structure rules: /workspace/work/distill_music/structure.md) — one 2-bar motif M, 8-bar sentence/period themes, flamenco cadences.
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



# ================= HARMONY: A dorian "underwater spy heist" E minor surf-spy: clean guitar twang lead, fretless, vibes, bongos, 112 BPM =================
SC = [64, 66, 67, 69, 71, 73, 74]
CH = {"Am7": (52, 55, 59, 62), "D7": (57, 61, 64, 67), "F": (48, 52, 55, 60), "G": (50, 54, 57, 62), "Em7": (47, 50, 54, 57)}
ROOT = {"Am7": 40, "D7": 45, "F": 48, "G": 50, "Em7": 47}
PCS = {k: {m % 12 for m in v} for k, v in CH.items()}
def bt(bar): return BIG2 + bar * BAR
LOOP = ["Am7", "Am7", "D7", "D7"]
HAR = [(-99, "Am7"), (-1.0, "F"), (-0.5, "G")]
for b in range(0, 46): HAR.append((b, LOOP[b % 4]))
for b0, c in ((12, "F"), (13, "G"), (21, "F"), (21.5, "G"), (22, "Am7"), (25, "F"), (26, "G"), (27, "Am7"), (34, "F"), (35, "G"), (35.5, "Am7"), (39, "F"), (39.5, "G"), (40.5, "Am7"), (42, "F"), (42.5, "G"), (43, "Am7")): HAR.append((b0, c))
HAR.sort(key=lambda x: x[0])
def ch(tt):
    b = (tt - BIG2) / BAR + 1e-6; c = "Am7"
    for b0, name in HAR:
        if b >= b0: c = name
    return c
def pitch(dg, base=0): o, r = divmod(dg, 7); return SC[r] + 12 * o + base
G = {"mar": 1.3, "clav": 0.8, "bass": 1.2, "pz": 1.0}
# motif: hop up (A C E), slip down chromatic-ish (G E D) ; strong notes chord tones
PH = {"Am7": [(0, 7, 2), (2, 9, 2), (4, 11, 3), (7, 10, 1), (8, 9, 2), (10, 7, 2), (12, 6, 4)],
      "D7":  [(0, 10, 2), (2, 9, 2), (4, 8, 4), (8, 7, 2), (10, 6, 2), (12, 3, 4)],
      "F":   [(0, 9, 2), (2, 10, 2), (4, 12, 4), (8, 9, 4), (12, 10, 4)],
      "G":   [(0, 8, 2), (2, 10, 2), (4, 13, 4), (8, 10, 4), (12, 8, 4)],
      "Em7": [(0, 6, 2), (2, 8, 2), (4, 11, 4), (8, 8, 4), (12, 6, 4)]}
LOG = []
def lead(t0, ev, inst, base=0, g=1.0, vel=104, tag="", strong=True):
    for p, d, l in ev:
        tt = t0 + p * S16 + (0.02 * BEAT if p % 2 else 0); c = ch(tt + 1e-3); m = pitch(d, base)
        if inst == "Marimba": add(gmn("Clean Guitar", m - 12, S16 * l + 0.15, vel, 0.25), tt, 0.4 * g * G["mar"], pan=0.12, wet=0.35, echo=0.25, bus="mel")
        elif inst == "Pizzicato Strings": add(gmn("Pizzicato Strings", m, S16 * l, vel, 0.2), tt, 0.3 * g * G["pz"], pan=-0.2, wet=0.3, bus="mel")
        else: add(gmn(inst, m, S16 * l, vel, 0.3), tt, 0.22 * g, wet=0.3, echo=0.15, bus="mel")
        if strong: LOG.append((tt, round(((tt - org(tt)) / S16)) % 16, m, c, inst, tag))
def phrase(b0, nb, inst, base=0, g=1.0, vel=104, tag=""):
    for j in range(nb):
        t0 = bt(b0 + j); lead(t0, PH[ch(t0 + 1e-3)], inst, base, g, vel, tag)
def sbass(t0, t1, g=1.0, busy=True):
    for tt, k, b in grid(t0, t1, 4):
        c = ch(tt + 1e-3); r = ROOT[c]; kk = k % 16
        pat = {0: r, 3: r + 12, 6: r, 7: r + 12, 10: r + 10, 12: r + 7, 14: r + 12} if busy else {0: r, 8: r + 7}
        m = pat.get(kk)
        if m is None: continue
        add(gmn("Fretless Bass", m, S16 * (2.5 if kk in (0, 8) else 1.2), 105, 0.08), tt, 0.4 * g * G["bass"])
def clav(t0, t1, g=1.0):
    for tt, k, b in grid(t0, t1, 4):
        kk = k % 16
        if kk in (2, 5, 6, 10, 13, 14):
            for j, m in enumerate(CH[ch(tt + 1e-3)][1:]): add(gmn("Vibraphone", m + 12, S16 * 0.9, 80 + 10 * (kk in (6, 14)), 0.2), tt + j * 0.004, 0.09 * g * G["clav"], pan=-0.3)
def kit(t0, t1, g=1.0, style="full"):
    for tt, k, b in grid(t0, t1, 4):
        kk = k % 16
        if style in ("full", "build") and kk in (0, 6, 10) or (style == "half" and kk == 0): add(dr(36, 112), tt, 0.6 * g)
        if style in ("full", "build") and kk in (4, 12) or (style == "half" and kk == 8): add(dr(38, 100), tt, 0.34 * g, wet=0.12)
        if style != "none" and kk % 2 == 0: add(dr(42, 50 + 25 * (kk % 4 == 2)), tt, 0.13 * g, pan=0.35)
        if style == "full" and kk == 14: add(dr(46, 70), tt, 0.1 * g, pan=0.35)
        if style != "none" and kk in (3, 7, 11, 13, 15): add(dr(60 + kk % 2, 80), tt, 0.16 * g, pan=-0.3)
        if style == "build" and kk >= 8: add(dr(38, 45 + 4 * kk), tt, 0.14 * g * (0.4 + kk / 16))
def band(t0, t1, g=1.0, style="full"):
    kit(t0, t1, g, style); sbass(t0, t1, g); clav(t0, t1, g)
def taiko(t0, g=1.0): add(gmn("Taiko Drum", 36, 1.5, 127, 0.8), t0, 0.9 * g, wet=0.35)
def sub(t0, g=1.0, dur=1.2):
    t = tt_(dur); f = 34 + 70 * np.exp(-t * 14)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) * 0.8, t0, g, human=False)
def chordhit(t0, c="Am7", g=1.0):
    for m in CH[c]: add(gmn("Vibraphone", m + 12, 1.4, 120, 0.6), t0, 0.25 * g, wet=0.4, bus="mel"); add(gmn("Clean Guitar", m, 1.0, 110, 0.4), t0, 0.15 * g, wet=0.4)
def slide(t0, up=False, g=1.0, dur=0.55):   # slide whistle (synth): the 'slip' sound
    t = tt_(dur); f0, f1 = (500, 1500) if up else (1700, 420)
    f = f0 * (f1 / f0) ** (t / dur); vib = 1 + 0.01 * np.sin(2 * np.pi * 6 * t)
    y = np.sin(2 * np.pi * np.cumsum(f * vib) / SR) * np.minimum(1, t / 0.03) * np.exp(-t * 1.5) * 0.25
    add(y, t0, g, wet=0.3, human=False)
def step_hit(t0, n, g=1.0):
    add(gmn("Vibraphone", 76 + 3 * n, 0.8, 115, 0.4), t0, 0.35 * g, wet=0.4, bus="mel"); add(dr(76, 110), t0, 0.3 * g)
def plink(t0, n=6, per=S16, g=1.0, base=81):
    for i in range(n): add(gmn("Pizzicato Strings", base - (i % 3) * 3 + (i // 3) * 2, 0.2, 100, 0.1), t0 + i * per, 0.22 * g, pan=0.3 * math.sin(i), bus="mel")
_vr = np.random.default_rng(3)
def V(): return float(2 ** (_vr.uniform(-1, 1) / 12))
def s_pop(t0, g=0.35): addfx(sfx(111, pitch=V()), t0, g, pan=0.1)
def s_deny(t0, g=0.45): addfx(sfx(119), t0, g)
def s_whoosh(t0, g=0.32): addfx(sfx(71, dur=0.9, pitch=V()), t0, g, pan=0.2)
def s_bub(t0, g=0.3): addfx(sfx(94, pitch=V()), t0, g, pan=-0.2)
def s_boing(t0, g=0.3): addfx(sfx(121, pitch=V()), t0, g)
def s_dizzy(t0, g=0.25): addfx(sfx(98, dur=1.4, fade=0.3), t0, g)
def s_boom(t0, g=0.8): addfx(sfx(209, dur=2.5, fade=0.3), t0, g, wet=0.2)
def s_drop(t0, g=0.4): addfx(sfx(70, pitch=V()), t0, g, wet=0.3)
def click(t0, g=0.25): addfx(sfx(149, pitch=V()), t0, g)
def thunk(t0, g=0.4): addfx(sfx(165), t0, g)
def big(t0, g=1.0):
    taiko(t0, g); sub(t0, 1.0 * g); s_boom(t0, 0.75 * g); add(dr(49, 127), t0, 0.45 * g, wet=0.4); add(dr(36, 127), t0, 0.8 * g)
    chordhit(t0, "Am7", g); duck(t0 + 0.02, 0.4, 0.9)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; u = t / (t1 - t0)
    nz = rng.standard_normal(n); y = nz - np.convolve(nz, np.ones(6) / 6, "same")
    add(y * u ** 2 * 0.07, t0, g, human=False)
    for j in range(int((t1 - t0) / S16)): add(gmn("Pizzicato Strings", 69 + (j % 7) * 2, S16, 90, 0.1), t0 + j * S16, 0.18 * g * (0.4 + 0.6 * j * S16 / (t1 - t0)), bus="mel")
# =============== ARRANGEMENT (bars from BIG2) ===============
# hook: ACCENT 1, squeeze sounds, tape stop
big(HOOK_HIT, 1.0); band(HOOK_HIT, HOOK_STOP, 1.0); slide(0.55, True, 0.7, 0.7); s_pop(1.3, 0.4)
lead(HOOK_HIT, PH["Am7"], "Marimba", tag="hook M")
sbass(T["q"], BIG2, 0.6, busy=False); plink(T["q"] + 0.1, 4, S8, 0.8)
riser(T["q"] + BEAT, BIG2 - BEAT / 4, 0.6); s_pop(T["q"] + 0.05, 0.35)
# ---- A (0-13.5): reveal..who
big(BIG2, 1.1)
band(bt(0), bt(13.5), 1.0)
phrase(0, 4, "Marimba", tag="A1"); phrase(4, 4, "Marimba", base=12, g=0.7, tag="A2 8va"); phrase(8, 4, "Pizzicato Strings", base=12, tag="A3"); phrase(12, 1, "Marimba", tag="A tail")
s_pop(at("reveal", 2), 0.3); s_pop(at("soft", 0.4), 0.3); s_boing(at("soft", 1), 0.2); s_pop(at("soft", 4), 0.25)
s_pop(at("brain", 0.3), 0.25); s_pop(at("brain", 1.5), 0.3); click(at("eyes", 0.5), 0.3); s_pop(at("eyes", 2.2), 0.3); s_pop(at("eyes", 4), 0.3)
s_pop(at("box", 0.3), 0.3); click(at("box", 2), 0.3); click(at("box", 5), 0.3)
for i in range(3): s_pop(at("who", 0.3 + i * 0.4), 0.2)
for i in range(4): s_pop(at("who", 2 + i * 0.4), 0.18)
# ---- B (13.5-22.5): steps: sneaky half-time, each step = vib hit; s3 pull = slide up
kit(bt(13.5), bt(18), 0.6, "half"); sbass(bt(13.5), bt(18), 0.8, busy=False); clav(bt(15), bt(18), 0.6)
s_pop(at("big", 0.3), 0.3); s_pop(at("big", 2), 0.25)
step_hit(T["s1"], 1); slide(at("s1", 0.4), True, 0.35, 0.9)
step_hit(T["s2"], 2); slide(at("s2", 0.4), True, 0.35, 0.9)
band(bt(18), bt(22.5), 1.0, "build"); step_hit(T["s3"], 3)
thunk(at("s3", 0.6), 0.35); slide(at("s3", 2), True, 0.9, 0.8); s_pop(at("s3", 4.2), 0.45)
phrase(19, 2, "Marimba", base=12, g=0.8, tag="pull")
for i in range(6): click(at("fast", i * 0.5), 0.2)
s_pop(at("fast", 0.5), 0.35)
# ---- C (22.5-27): narrow hole, 4 steps: drums drop, tension
kit(bt(22.5), bt(25.5), 0.45, "none"); sbass(bt(22.5), bt(27), 0.7, busy=False)
s_pop(at("small", 0.3), 0.3); s_deny(at("small", 0.6), 0.25); s_pop(at("small", 2), 0.3)
for i in range(8): s_pop(at("s4a", 1.0 + i * 0.35), 0.15)
step_hit(T["s4b"], 4); band(bt(25.5), bt(27), 0.9, "build"); slide(at("s4b", 0.5), True, 0.6, 3.6); s_pop(at("s4b", 4.6), 0.5)
# ---- D (27-35.5): maya / why / robot
band(bt(27), bt(35.5), 0.95)
phrase(27, 4, "Pizzicato Strings", base=12, g=0.9, tag="maya"); phrase(31, 4, "Marimba", tag="robot")
s_pop(at("maya", 0.3), 0.3); s_deny(at("maya", 3), 0.25); s_pop(at("why", 0.3), 0.3); thunk(at("why", 2.5), 0.3)
s_pop(at("robot", 0.3), 0.3); s_pop(at("robot", 3), 0.25)
# ---- E (35.5-40.5): card
sbass(bt(35.5), bt(40.5), 0.8, busy=False); kit(bt(35.5), bt(40.5), 0.55, "half"); clav(bt(36.5), bt(40.5), 0.5)
phrase(35.5, 4, "Marimba", g=0.6, vel=88, tag="card")
s_whoosh(T["card"] + 0.05, 0.2); s_pop(T["card"] + 0.12, 0.3)
for i in range(4): s_pop(at("card", 1.2 + i * 1.6), 0.2)
# ---- F (40.5-43.5): end
band(bt(40.5), bt(43), 1.1); phrase(40.5, 2, "Marimba", tag="final")
s_pop(T["end"] + 0.05, 0.3); slide(at("end", 1.8), True, 0.7, 0.8); s_pop(at("end", 2.9), 0.4)
FINAL = bt(43) - 0.3
chordhit(FINAL, "Am7", 0.7)
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
with wave.open("/workspace/work/octo/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG2 %.2f" % (BPM, DUR, BIG2))
