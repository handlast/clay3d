# 《冲不走的鱼》BGM — "whitewater raga-funk": sitar riff + conga/tabla-style hand drums + dulcimer (santoor) ripples + bansuri-ish flute,
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
# D phrygian dominant: D Eb F# G A Bb C
SC = [62, 63, 66, 67, 69, 70, 72]
def deg(i, base=0): o, r = divmod(i, 7); return SC[r] + 12 * o + base
PROG = ["D", "D", "Eb", "D", "D", "C", "Eb", "D"]   # bVII-bII cadences over the drone
CH = {"D": (50, 54, 57, 62), "Eb": (51, 55, 58, 63), "C": (48, 52, 55, 60)}
ROOT = {"D": 38, "Eb": 39, "C": 36}
def chord(b): return PROG[b % 8]
G = {"sitar": 2.0, "dulc": 1.4, "flute": 1.6, "bass": 1.1, "kal": 1.3, "drone": 0.9}
# ---- instruments
def drone(t0, t1, g=1.0):   # tanpura-like: plucked Sitar D2-A2-D3-D3 cycle, every beat
    pat = [50, 57, 62, 62]
    for tt, k, b in grid(t0, t1, 1): add(gmn("Sitar", pat[k % 4] - 12, BEAT * 1.6, 70, 0.5), tt, 0.22 * g * G["drone"], pan=-0.3 + 0.2 * (k % 2), wet=0.3)
RIFF = [(0, 0, 1), (1, 1, 1), (2, 2, 1), (3, 3, 2), (6, 4, 1), (7, 3, 1), (8, 4, 2), (10, 6, 1), (11, 5, 1), (12, 4, 1), (13, 3, 1), (14, 2, 1), (15, 1, 1)]
RIFF2 = [(0, 7, 2), (2, 6, 1), (3, 4, 1), (4, 5, 2), (6, 4, 1), (7, 3, 1), (8, 2, 3), (11, 1, 1), (12, 2, 2), (14, 0, 2)]
def sitar(t0, t1, g=1.0, alt=False):
    for tt, k, b in grid(t0, t1, 4):
        for (s, dg, ln) in (RIFF2 if (alt or b % 2) else RIFF):
            if s == k:
                m = deg(dg, -12) + (1 if chord(b) == "Eb" and dg % 7 == 0 else 0)
                add(gmn("Sitar", m, S16 * ln * 1.3, 104, 0.25), tt, 0.3 * g * G["sitar"], pan=0.15, wet=0.25, echo=0.15, bus="mel")
def dulc(t0, t1, g=1.0):   # santoor-like 16th ripples on chord tones
    for tt, k, b in grid(t0, t1, 4):
        c = CH[chord(b)]; m = (c + tuple(x + 12 for x in c))[[0, 2, 4, 6, 7, 5, 3, 1][k % 8]] + 12
        add(gmn("Dulcimer", m, S16 * 2, 70 + 20 * (k % 4 == 0), 0.2), tt, 0.13 * g * G["dulc"], pan=-0.35 + 0.7 * ((k % 8) / 7), wet=0.3)
FL = [[(0, 4, 3), (3, 5, 1), (4, 4, 2), (6, 3, 2), (8, 2, 4), (12, 1, 2), (14, 2, 2)],
      [(0, 3, 2), (2, 4, 2), (4, 6, 4), (8, 7, 2), (10, 6, 2), (12, 4, 4)],
      [(0, 7, 3), (3, 6, 1), (4, 4, 2), (6, 5, 2), (8, 4, 2), (10, 3, 2), (12, 2, 4)],
      [(0, 1, 2), (2, 2, 2), (4, 0, 8), (12, -1, 2), (14, 0, 2)]]
def flute(t0, t1, g=1.0, inst="Flute"):
    for tt, k, b in grid(t0, t1, 4):
        for s, dg, ln in FL[b % 4]:
            if s == k: add(gmn(inst, deg(dg, 12), S16 * ln * 1.05, 96, 0.3), tt, 0.26 * g * G["flute"], wet=0.45, echo=0.25, bus="mel")
def bass(t0, t1, g=1.0):
    pat = [(0, 0), (3, 0), (6, 7), (8, 0), (11, 0), (14, 10)]
    for tt, k, b in grid(t0, t1, 4):
        for s, iv in pat:
            if s == k: add(gmn("Finger Bass", ROOT[chord(b)] + (12 if iv == 7 else iv if iv < 7 else -2), S16 * 2.2, 110, 0.12), tt, 0.5 * g * G["bass"])
def hands(t0, t1, g=1.0, style="full"):   # conga/bongo tabla-ish + kick/clap + shaker
    for tt, k, b in grid(t0, t1, 4):
        kk = k % 16
        if style in ("full", "build") and kk in (0, 6, 10) or (style == "half" and kk == 0): add(dr(36, 120), tt, 0.85 * g)
        if style in ("full", "build", "half") and kk in (4, 12): add(dr(39, 105), tt, 0.35 * g, wet=0.2); add(dr(38, 70), tt, 0.25 * g)
        if kk in (2, 7, 9, 14): add(dr(63, 95), tt, 0.32 * g, pan=0.3)          # open hi conga ("na")
        if kk in (3, 11): add(dr(64, 100), tt, 0.38 * g, pan=-0.2)              # low conga ("ge")
        if kk in (1, 5, 13): add(dr(62, 70), tt, 0.25 * g, pan=0.35)            # mute conga ("ti")
        add(dr(70, 60 + 25 * (kk % 4 == 2)), tt, 0.13 * g, pan=-0.4)             # maracas 16ths
        if style == "build" and kk >= 8: add(dr(38, 50 + 4 * kk), tt, 0.18 * g * (kk - 7) / 8)
def groove(t0, t1, g=1.0, lead="sitar", style="full", dl=True):
    hands(t0, t1, g, style); bass(t0, t1, g); drone(t0, t1, 0.7 * g)
    if dl: dulc(t0, t1, g)
    if lead == "sitar": sitar(t0, t1, g)
    elif lead == "sitar2": sitar(t0, t1, g, alt=True)
    elif lead: flute(t0, t1, g, lead)
def kal(t0, t1, g=1.0):
    for tt, k, b in grid(t0, t1, 2):
        c = CH[chord(b)]; m = (c[1:] + (c[1] + 12, c[2] + 12))[k % 5] + 12
        add(gmn("Kalimba", m, 0.6, 90, 0.4), tt, 0.25 * g * G["kal"], pan=0.3 * math.sin(k), wet=0.4, echo=0.3, bus="mel")
def taiko(t0, g=1.0): add(gmn("Taiko Drum", 36, 1.5, 127, 0.8), t0, 0.9 * g, wet=0.35)
def sub(t0, g=1.0, dur=1.2):
    t = tt_(dur); f = 34 + 70 * np.exp(-t * 14)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) * 0.8, t0, g, human=False)
def chordhit(t0, ch="D", g=1.0):
    for m in CH[ch]: add(gmn("Sitar", m, 1.2, 120, 0.6), t0, 0.22 * g, wet=0.4, bus="mel"); add(gmn("Dulcimer", m + 12, 1.0, 110, 0.6), t0, 0.12 * g, wet=0.5)
# ---- SFX helpers (Sonniss)
_vr = np.random.default_rng(3)
def V(): return float(2 ** (_vr.uniform(-1, 1) / 12))     # +-1 semitone variation for repeats
def s_pop(t0, g=0.35): addfx(sfx(111, pitch=V()), t0, g, pan=0.1)
def s_snap(t0, g=0.4): addfx(sfx(109, pitch=V()), t0, g)
def s_deny(t0, g=0.45): addfx(sfx(119), t0, g)
def s_whoosh(t0, g=0.32): addfx(sfx(71, dur=0.9, pitch=V()), t0, g, pan=0.2)
def s_bub(t0, g=0.3): addfx(sfx(94, pitch=V()), t0, g, pan=-0.2)
def s_kal(t0, g=0.35): addfx(sfx(92, pitch=V()), t0, g, wet=0.3)
def s_arp(t0, g=0.3): addfx(sfx(118), t0, g, wet=0.3)
def s_twinkle(t0, g=0.3): addfx(sfx(127), t0, g, wet=0.3)
def s_boom(t0, g=0.8): addfx(sfx(209, dur=2.5, fade=0.3), t0, g, wet=0.2)
def s_splash(t0, g=0.55): addfx(sfx(70), t0, g, wet=0.3)
def water(t0, t1, g=0.12):
    y = sfx(274, start=10.0, dur=t1 - t0 + 0.5, fade=0.4)
    addfx(y, t0, g, peak=False)
def big(t0, g=1.0):
    taiko(t0, g); sub(t0, 1.0 * g); s_boom(t0, 0.75 * g); add(dr(49, 127), t0, 0.45 * g, wet=0.4); add(dr(36, 127), t0, 0.8 * g)
    chordhit(t0, "D", g); duck(t0 + 0.02, 0.4, 0.9)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; u = t / (t1 - t0)
    nz = rng.standard_normal(n); y = nz - np.convolve(nz, np.ones(6) / 6, "same")
    add(y * u ** 2 * 0.07, t0, g, human=False)
    for j in range(int((t1 - t0) / S16)): add(gmn("Sitar", 62 + j, S16, 80, 0.1), t0 + j * S16, 0.12 * g * (0.4 + 0.6 * j * S16 / (t1 - t0)), bus="mel")

# =============== ARRANGEMENT (all times from cues) ===============
# hook: full groove + big hit, tape-stop into stay
big(HOOK_HIT, 1.0); groove(HOOK_HIT, HOOK_STOP, 1.0, "sitar")
for t0, *_ in [(HOOK_HIT + 0.05,), (HOOK_HIT + 0.55,), (HOOK_HIT + 1.3,)]: s_whoosh(t0 + 0.3); s_bub(t0 + 0.6, 0.2)
water(0, BIG2, 0.10)
# stay: drone + hand drums only, water, one swept fish
drone(T["stay"], T["q"], 1.0); hands(T["stay"], T["q"], 0.6, "none"); bass(T["stay"], T["q"], 0.6)
s_whoosh(at("stay", 1.5) + 0.3); s_twinkle(at("stay", 1), 0.25); add(gmn("Sitar", 74, 1.0, 100, 0.5), at("stay", 0.5), 0.25, wet=0.5, bus="mel")
# q: suspense riser, short gap before BIG2 (1/4 beat, no black silence)
drone(T["q"], BIG2 - BEAT / 4, 0.8); riser(T["q"], BIG2 - BEAT / 4, 1.0); s_pop(T["q"] + 0.08, 0.4)
# BIG2 reveal
big(BIG2, 1.1); s_splash(BIG2 + 0.01, 0.5)
groove(BIG2, T["catfish"], 1.0, "sitar")
s_kal(at("reveal", 1.5)); s_pop(at("reveal", 2))
# flat
s_pop(at("flat", 0.3), 0.3); s_pop(at("flat", 0.6), 0.25); s_pop(at("flat", 1.0), 0.3); s_deny(at("flat", 2.2), 0.35); s_whoosh(at("flat", 3), 0.25)
# fins (4 pads pop then glow) — lead switches to flute
for i in range(4): s_pop(at("fins", 0.4 + i * 0.25), 0.28); s_snap(at("fins", 2 + i * 0.25), 0.22)
flute(T["fins"], T["catfish"], 0.8, "Flute")
# barbel
s_kal(at("barbel", 1.5), 0.3); s_pop(at("barbel", 2), 0.3)
# catfish: breakdown (no kick): kalimba + bass + hands lite
kal(T["catfish"], T["nameq"], 1.0); bass(T["catfish"], T["nameq"], 0.8); hands(T["catfish"], T["nameq"], 0.6, "none")
s_pop(at("catfish", 0.3)); s_deny(at("catfish", 1.0)); s_pop(at("catfish", 1.7)); s_snap(at("catfish", 2.4), 0.45)
# nameq: spotlight — drums out, drone + twinkle
drone(T["nameq"], T["nose"], 1.8); s_twinkle(at("nameq", 1.4), 0.4); kal(T["nameq"], T["nose"], 1.1); hands(T["nameq"], T["nose"], 0.35, "none")
# nose: build back in with riser as the barbel grows
hands(T["nose"], T["latin"], 0.8, "build"); bass(T["nose"], T["latin"], 0.9); drone(T["nose"], T["latin"], 0.7)
riser(at("nose", 0.5), at("nose", 3.2), 0.7); s_pop(at("nose", 1.1), 0.25); s_snap(at("nose", 3.2), 0.45); s_pop(at("nose", 3.3), 0.3)
# latin: full groove alt riff
groove(T["latin"], T["sense"], 0.95, "sitar2")
s_pop(at("latin", 0.3)); s_pop(at("latin", 1.2), 0.25); s_kal(at("latin", 2.4), 0.4)
# sense + murky: half-time with flute (shakuhachi breathy)
groove(T["sense"], T["where"], 0.85, "Shakuhachi", "half", dl=False); kal(T["sense"], T["murky"], 0.5)
s_pop(at("sense", 1.5)); s_pop(at("sense", 2.3)); s_bub(at("sense", 0.5), 0.2); s_bub(at("murky", 1), 0.2); s_kal(at("murky", 2.5), 0.4)
# where + rare: full groove, sitar
groove(T["where"], T["ident"], 0.95, "sitar")
s_pop(at("where", 0.3), 0.2); s_pop(at("where", 0.5), 0.2); s_pop(at("where", 1.6), 0.35); s_pop(at("where", 1.7), 0.3); s_pop(at("where", 2.8), 0.25)
s_arp(at("rare", 0.5), 0.3); water(T["rare"], T["ident"], 0.08)
# ident: build with checks
groove(T["ident"], T["card"], 0.9, "sitar2", "build")
for i in range(3): s_pop(at("ident", 0.8 + i * 0.9), 0.3); s_snap(at("ident", 1.1 + i * 0.9), 0.4)
# card: lite
hands(T["card"], T["end"], 0.6, "half"); bass(T["card"], T["end"], 0.8); dulc(T["card"], T["end"], 0.8); kal(T["card"], T["end"], 0.6)
s_whoosh(T["card"] + 0.05, 0.2); s_pop(T["card"] + 0.12, 0.35)
for i in range(3): s_pop(at("card", 1.2 + i * 0.6), 0.22)
# end: full + final chord, ring out
FINAL = at("end", 8)
groove(T["end"], FINAL, 0.95, "sitar"); flute(T["end"], FINAL, 0.6, "Flute"); water(T["end"], DUR, 0.10)
for k_, t0 in enumerate((T["end"] + 0.4, T["end"] + 1.6, T["end"] + 2.8)): s_whoosh(t0 + 0.3, 0.22)
s_pop(at("end", 2), 0.25)
taiko(FINAL, 0.9); sub(FINAL, 0.6); chordhit(FINAL, "D", 1.2); add(dr(49, 110), FINAL, 0.35, wet=0.5)
add(gmn("Sitar", 74, 2.5, 110, 1.5), FINAL + BEAT, 0.3, wet=0.6, echo=0.4, bus="mel")

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
MIX[i0:i1] = seg; MIX[i1:int((HOOKCUT + 0.08) * SR)] *= np.linspace(0.3, 1, int(0.08 * SR))[:, None]
MIX = MIX / (np.abs(MIX).max() + 1e-9)
MIX = MIX * DUCK[:, None] + FX * 0.9
MIX = np.tanh(MIX * 1.8); MIX /= np.abs(MIX).max() / 0.85
MIX = MIX[: int(SR * DUR)]
fo = int(1.2 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
with wave.open("/workspace/work/exostoma/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG2 %.2f" % (BPM, DUR, BIG2))
