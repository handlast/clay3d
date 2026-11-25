# 《冲不走的鱼》BGM v2 (structure rules: /workspace/work/distill_music/structure.md) — one 2-bar motif M, 8-bar sentence/period themes, flamenco cadences.
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

# ================= HARMONY (D phrygian dominant; F natural on every non-D chord, as in flamenco) =================
SC = [62, 63, 66, 67, 69, 70, 72]
CH = {"D": (50, 54, 57, 62), "Eb": (51, 55, 58, 63), "F": (53, 57, 60, 65), "Gm": (50, 55, 58, 62), "Bb": (50, 53, 58, 62), "Cm": (48, 51, 55, 60)}
ROOT = {"D": 38, "Eb": 39, "F": 41, "Gm": 43, "Bb": 46, "Cm": 36}
PCS = {k: {m % 12 for m in v} for k, v in CH.items()}
def bt(bar): return BIG2 + bar * BAR
HAR = [(-99, "D"), (-0.25, "Eb"),                                                    # pre-BIG2: D drone, Eb pickup on q's last beat
       (0, "D"), (2, "Eb"), (3, "D"), (4, "Gm"), (5, "F"), (6, "Gm"), (6.5, "F"), (7, "Eb"),          # A: sentence -> iv-III-bII-I into bar 8
       (8, "D"), (10, "Cm"), (11, "D"), (12, "D"), (13, "Gm"), (14, "Eb"), (15.5, "D"),              # B: period (weak on A, strong E♭→D)
       (16, "Bb"), (17, "Gm"), (18, "F"), (19, "D"), (21, "Bb"), (22, "D"), (23, "Eb"),               # C: development, half cadence on E♭
       (24, "Gm"), (24.5, "F"), (25, "Eb"), (25.5, "Cm"), (26, "Eb"), (27, "D"), (28.5, "Eb"),        # D: fragmentation, breath
       (29, "D"), (30, "Gm"), (31, "Gm"), (31.5, "F"), (32, "Eb"), (32.5, "D")]                       # final statement, strongest cadence
def ch(tt):
    b = (tt - BIG2) / BAR + 1e-6; c = "D"
    for b0, name in HAR:
        if b >= b0: c = name
    return c
def chord(b): return ch(org(0) + b * BAR)  # legacy
def pitch(dg, chn, base=0):
    o, r = divmod(dg, 7); pc = SC[r] - (1 if (r == 2 and chn != "D") else 0); return pc + 12 * o + base
G = {"sitar": 2.0, "dulc": 1.4, "flute": 1.6, "bass": 1.1, "kal": 1.3, "drone": 0.9}
# ================= MOTIF and its operators (positions/lengths in 16ths) =================
M1 = [(0, 0, 2), (2, 1, 2), (4, 2, 6), (10, 3, 2), (12, 4, 4)]          # D Eb F# . G A   (arch up, aug-2nd Eb->F#)
M2 = [(0, 3, 3), (3, 2, 1), (4, 1, 4), (8, 0, 6)]                       # G F# Eb D        (down, long final, rest)
def seq(ev, n): return [(p, d + n, l) for p, d, l in ev]
def inv(ev): return [(p, -d, l) for p, d, l in ev]
def aug(ev, k=2): return [(p * k, d, l * k) for p, d, l in ev]
def frag(ev, n): return ev[:n]
def at16(ev, off): return [(p + off, d, l) for p, d, l in ev]
def last(ev, d=None, l=None): p, d0, l0 = ev[-1]; return ev[:-1] + [(p, d0 if d is None else d, l0 if l is None else l)]
HALF = lambda n: last(seq(frag(M1, 3), n), l=4)
LOG = []   # (time, pos16_in_bar, pitch, chord, inst)
def lead(t0, ev, inst, base=0, g=1.0, vel=104, tag="", strong=True):
    for p, d, l in ev:
        tt = t0 + p * S16 + (0.02 * BEAT if p % 2 else 0); c = ch(tt + 1e-3); m = pitch(d, c, base)
        if inst == "Sitar": add(gmn("Sitar", m, S16 * l * 1.15, vel, 0.3), tt, 0.32 * g * G["sitar"], pan=0.15, wet=0.25, echo=0.12, bus="mel")
        elif inst == "Kalimba": add(gmn("Kalimba", m, S16 * l + 0.3, vel, 0.4), tt, 0.3 * g * G["kal"], pan=0.2, wet=0.4, echo=0.25, bus="mel")
        elif inst == "Dulcimer": add(gmn("Dulcimer", m, S16 * l * 1.3, vel, 0.3), tt, 0.2 * g * G["dulc"], pan=-0.2, wet=0.35, bus="mel")
        else: add(gmn(inst, m, S16 * l * 1.02, vel, 0.3), tt, 0.26 * g * G["flute"], pan=-0.1, wet=0.45, echo=0.2, bus="mel")
        if strong: LOG.append((tt, round(((tt - org(tt)) / S16)) % 16, m, c, inst, tag))
# ================= accompaniment (chord-aware) =================
def drone(t0, t1, g=1.0):
    pat = [50, 57, 62, 62]
    for tt, k, b in grid(t0, t1, 1): add(gmn("Sitar", pat[k % 4] - 12, BEAT * 1.6, 70, 0.5), tt, 0.16 * g * G["drone"], pan=-0.3 + 0.2 * (k % 2), wet=0.3)
def dulc(t0, t1, g=1.0):
    for tt, k, b in grid(t0, t1, 4):
        c = CH[ch(tt)]; m = (c + tuple(x + 12 for x in c))[[0, 2, 4, 6, 7, 5, 3, 1][k % 8]] + 12
        add(gmn("Dulcimer", m, S16 * 2, 62 + 18 * (k % 4 == 0), 0.2), tt, 0.1 * g * G["dulc"], pan=-0.35 + 0.7 * ((k % 8) / 7), wet=0.3)
def bass(t0, t1, g=1.0):
    pat = [(0, 0), (3, 0), (6, 12), (8, 0), (11, 0), (14, -5)]
    for tt, k, b in grid(t0, t1, 4):
        for s_, iv in pat:
            if s_ == k % 16: add(gmn("Finger Bass", ROOT[ch(tt)] + iv, S16 * 2.2, 110, 0.12), tt, 0.5 * g * G["bass"])
def hands(t0, t1, g=1.0, style="full"):
    for tt, k, b in grid(t0, t1, 4):
        kk = k % 16
        if style in ("full", "build") and kk in (0, 6, 10) or (style == "half" and kk == 0): add(dr(36, 120), tt, 0.85 * g)
        if style in ("full", "build", "half") and kk in (4, 12): add(dr(39, 105), tt, 0.35 * g, wet=0.2); add(dr(38, 70), tt, 0.25 * g)
        if kk in (2, 7, 9, 14): add(dr(63, 95), tt, 0.32 * g, pan=0.3)
        if kk in (3, 11): add(dr(64, 100), tt, 0.38 * g, pan=-0.2)
        if kk in (1, 5, 13): add(dr(62, 70), tt, 0.25 * g, pan=0.35)
        add(dr(70, 60 + 25 * (kk % 4 == 2)), tt, 0.13 * g, pan=-0.4)
        if style == "build":   # drum-roll subdivision: 8ths in first half of bar, 16ths in second
            if (kk < 8 and kk % 2 == 0) or kk >= 8: add(dr(38, 45 + 4 * kk), tt, 0.16 * g * (0.4 + kk / 16))
def kal(t0, t1, g=1.0):
    for tt, k, b in grid(t0, t1, 2):
        c = CH[ch(tt)]; m = (c[1:] + (c[1] + 12, c[2] + 12))[k % 5] + 12
        add(gmn("Kalimba", m, 0.6, 80, 0.4), tt, 0.2 * g * G["kal"], pan=0.3 * math.sin(k), wet=0.4, echo=0.3)
def taiko(t0, g=1.0): add(gmn("Taiko Drum", 36, 1.5, 127, 0.8), t0, 0.9 * g, wet=0.35)
def sub(t0, g=1.0, dur=1.2):
    t = tt_(dur); f = 34 + 70 * np.exp(-t * 14)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) * 0.8, t0, g, human=False)
def chordhit(t0, c="D", g=1.0):
    for m in CH[c]: add(gmn("Sitar", m, 1.2, 120, 0.6), t0, 0.22 * g, wet=0.4, bus="mel"); add(gmn("Dulcimer", m + 12, 1.0, 110, 0.6), t0, 0.12 * g, wet=0.5)
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


# =============== ARRANGEMENT v2 (bars counted from BIG2; every lead bar is a named operator on M) ===============
water(0, BIG2, 0.10)
# hook: L5 + ACCENT 1. Lead: foreshadow M1 only, then tape stop
big(HOOK_HIT, 1.0); hands(HOOK_HIT, HOOK_STOP, 1.0); bass(HOOK_HIT, HOOK_STOP); drone(HOOK_HIT, HOOK_STOP, 0.7); dulc(HOOK_HIT, HOOK_STOP, 0.8)
lead(HOOK_HIT, M1, "Sitar", tag="M1 foreshadow"); lead(HOOK_HIT + BAR, frag(M2, 2), "Sitar", tag="M2 frag")
for t0 in (HOOK_HIT + 0.05, HOOK_HIT + 0.55, HOOK_HIT + 1.3): s_whoosh(t0 + 0.3); s_bub(t0 + 0.6, 0.2)
# stay: L2. M1's first 4 notes at x2 augmentation, soft
drone(T["stay"], T["q"], 1.0); hands(T["stay"], T["q"], 0.6, "none"); bass(T["stay"], T["q"], 0.55)
lead(T["stay"], aug(frag(M1, 4)), "Sitar", g=0.75, vel=90, tag="aug frag")
s_whoosh(at("stay", 1.5) + 0.3); s_twinkle(at("stay", 1), 0.25)
# q: L1->L2. dulcimer cell D-Eb-F#, 8ths then 16ths (drum-roll effect), riser
drone(T["q"], BIG2, 0.8); riser(T["q"] + BEAT, BIG2 - BEAT / 4, 0.6); s_pop(T["q"] + 0.08, 0.4)
cell = [0, 1, 2]; tq = T["q"]
for i in range(3): lead(tq + i * S8, [(0, cell[i % 3], 2)], "Dulcimer", g=0.9, vel=95, strong=False)
for i in range(5): lead(tq + 3 * S8 + i * S16, [(0, cell[i % 3] + (i // 3), 1)], "Dulcimer", g=1.0, vel=105, strong=False)
# ---- A (bars 0-8): reveal/flat/fins/barbel. L5 ACCENT 2 -> L4. 8-bar sentence, sitar owns the lead
big(BIG2, 1.1); s_splash(BIG2 + 0.01, 0.5)
hands(bt(0), bt(8), 1.0); bass(bt(0), bt(8)); drone(bt(0), bt(8), 0.5); dulc(bt(0), bt(8), 0.7)
lead(bt(0), M1, "Sitar", tag="BI"); lead(bt(1), M2, "Sitar", tag="BI")
lead(bt(2), seq(M1, 1), "Sitar", tag="seq+1"); lead(bt(3), last(seq(M2, 1), d=0), "Sitar", tag="seq+1 (ends D)")
lead(bt(4), seq(M1, 3), "Sitar", tag="frag-1bar seq+3"); lead(bt(5), seq(M1, 2), "Sitar", tag="frag-1bar seq+2")
lead(bt(6), HALF(3), "Sitar", tag="half frag"); lead(bt(6.5), HALF(2), "Sitar", tag="half frag")
lead(bt(7), [(0, 3, 4), (4, 2, 4), (8, 1, 8)], "Sitar", tag="cadence (M2 aug frag)")
s_kal(at("reveal", 1.5)); s_pop(at("reveal", 2))
s_pop(at("flat", 0.3), 0.3); s_pop(at("flat", 0.6), 0.25); s_pop(at("flat", 1.0), 0.3); s_deny(at("flat", 2.2), 0.35); s_whoosh(at("flat", 3), 0.25)
for i in range(4): s_pop(at("fins", 0.4 + i * 0.25), 0.28); s_snap(at("fins", 2 + i * 0.25), 0.22)
s_kal(at("barbel", 1.5), 0.3); s_pop(at("barbel", 2), 0.3)
# ---- B (bars 8-16): catfish/nameq/nose/latin. Period. Breakdown -> spotlight -> build -> kick back on bar 14
hands(bt(8), bt(10), 0.6, "none"); bass(bt(8), bt(10), 0.8); drone(bt(8), bt(10), 0.6)
drone(bt(10), bt(11.5), 1.5); hands(bt(10), bt(11.5), 0.35, "none"); bass(bt(10), bt(11.5), 0.45)
lead(bt(8), aug(M1), "Kalimba", base=12, tag="antecedent aug(M1)"); lead(bt(10), last(aug(M2), d=4), "Kalimba", base=12, tag="antecedent aug(M2), weak end on A")
hands(bt(11.5), bt(14), 0.8, "build"); bass(bt(11.5), bt(14), 0.9); drone(bt(11.5), bt(14), 0.6); riser(bt(12.5), bt(14) - S16, 0.5)
lead(bt(12), M1, "Sitar", tag="consequent call"); lead(bt(13), M2, "Flute", base=12, tag="answer")
hands(bt(14), bt(16), 1.0); bass(bt(14), bt(16)); dulc(bt(14), bt(16), 0.7); drone(bt(14), bt(16), 0.5)
lead(bt(14), seq(M1, 1), "Sitar", tag="call seq+1"); lead(bt(15), M2, "Flute", base=12, tag="answer, strong E♭→D")
s_pop(at("catfish", 0.3)); s_deny(at("catfish", 1.0)); s_pop(at("catfish", 1.7)); s_snap(at("catfish", 2.4), 0.45)
s_twinkle(at("nameq", 1.4), 0.4)
s_pop(at("nose", 1.1), 0.25); s_snap(at("nose", 3.2), 0.45); s_pop(at("nose", 3.3), 0.3)
s_pop(at("latin", 0.3)); s_pop(at("latin", 1.2), 0.25); s_kal(at("latin", 2.4), 0.4)
# ---- C (bars 16-24): sense/murky/where/rare. Development: inversion at half-time (shakuhachi), then M a 3rd up (sitar)
hands(bt(16), bt(20), 0.85, "half"); bass(bt(16), bt(20), 0.85); drone(bt(16), bt(20), 0.7)
lead(bt(16), aug(inv(M1)), "Shakuhachi", tag="inv aug"); lead(bt(18), aug(inv(M2)), "Shakuhachi", tag="inv aug")
for b_ in (17.5, 19.5): kal(bt(b_), bt(b_ + 0.5), 0.5)       # kalimba only in the shakuhachi's rests
hands(bt(20), bt(24), 0.95); bass(bt(20), bt(24)); dulc(bt(20), bt(24), 0.7); drone(bt(20), bt(24), 0.5)
lead(bt(20), seq(M1, 2), "Sitar", tag="seq+2 (3rd up)"); lead(bt(21), seq(M2, 2), "Sitar", tag="seq+2")
lead(bt(22), M1, "Sitar", tag="BI"); lead(bt(23), [(0, 3, 4), (4, 2, 4), (8, 1, 8)], "Sitar", tag="half cadence on E♭")
s_pop(at("sense", 1.5)); s_pop(at("sense", 2.3)); s_bub(at("sense", 0.5), 0.2); s_bub(at("murky", 1), 0.2); s_kal(at("murky", 2.5), 0.4)
s_pop(at("where", 0.3), 0.2); s_pop(at("where", 0.5), 0.2); s_pop(at("where", 1.6), 0.35); s_pop(at("where", 1.7), 0.3); s_pop(at("where", 2.8), 0.25)
s_arp(at("rare", 0.5), 0.3); water(T["rare"], T["ident"], 0.08)
# ---- D (bars 24-33): ident/card/end. Fragmentation -> breath -> fullest restatement, no third accent
hands(bt(24), bt(27), 0.9, "build"); bass(bt(24), bt(27)); dulc(bt(24), bt(27), 0.6); drone(bt(24), bt(27), 0.5)
lead(bt(24), HALF(3), "Sitar", tag="half frag"); lead(bt(24.5), HALF(2), "Sitar", tag="half frag")
lead(bt(25), HALF(1), "Sitar", tag="half frag"); lead(bt(25.5), HALF(6), "Sitar", tag="half frag")
lead(bt(26), [(0, 3, 2), (2, 4, 2), (4, 2, 2), (6, 3, 2), (8, 1, 8)], "Sitar", tag="quarter frags -> E♭")
for i in range(3): s_pop(at("ident", 0.8 + i * 0.9), 0.3); s_snap(at("ident", 1.1 + i * 0.9), 0.4)
hands(bt(27), bt(29), 0.55, "none"); bass(bt(27), bt(29), 0.75); drone(bt(27), bt(29), 0.8)
for j in range(4): lead(bt(27) + j * BEAT * 2, [(0, 0, 2), (2, 1, 2), (4, 2, 4)], "Dulcimer", g=0.9, tag="cell")
s_whoosh(T["card"] + 0.05, 0.2); s_pop(T["card"] + 0.12, 0.35)
for i in range(3): s_pop(at("card", 1.2 + i * 0.6), 0.22)
FINAL = bt(32.5)
hands(bt(29), FINAL, 1.0); bass(bt(29), FINAL); dulc(bt(29), FINAL, 0.8); drone(bt(29), DUR, 0.6); kal(bt(29), bt(32), 0.45)
for inst, base, gg in (("Sitar", 0, 1.0), ("Flute", 12, 0.7)):
    lead(bt(29), M1, inst, base, gg, tag="final BI"); lead(bt(30), M2, inst, base, gg, tag="final BI")
    lead(bt(31), HALF(3), inst, base, gg, tag="half frag"); lead(bt(31.5), HALF(2), inst, base, gg, tag="half frag")
    lead(bt(32), [(0, 1, 8), (8, 0, 22)], inst, base, gg, tag="final E♭→D aug")
chordhit(FINAL, "D", 0.8)       # held cadence chord, no taiko/sub/crash (keeps the 2-accent rule)
water(T["end"], DUR, 0.10)
for t0 in (T["end"] + 0.4, T["end"] + 1.6, T["end"] + 2.8): s_whoosh(t0 + 0.3, 0.22)
s_pop(at("end", 2), 0.25)
# ---- structure checks
nonc = [(round(t, 2), p, m, c, tag) for t, p, m, c, i, tag in LOG if p in (0, 8) and (m % 12) not in PCS[c]]
strong = [x for x in LOG if x[1] in (0, 8)]
print("strong-beat lead notes %d, non-chord %d (%.0f%%)" % (len(strong), len(nonc), 100 * len(nonc) / max(1, len(strong))))
for x in nonc: print("  nonchord", x)
print("E-natural notes:", sum(1 for x in LOG if x[2] % 12 == 4))
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
