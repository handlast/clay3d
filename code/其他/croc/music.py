# 《鳄鱼妈妈贴地偷听》BGM (structure rules: /workspace/work/distill_music/structure.md) — one 2-bar motif M, 8-bar sentence/period themes, flamenco cadences.
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

# ================= HARMONY: G major, swampy bluegrass (banjo / harmonica / tuba oom-pah / steel-guitar chop / kalimba) =================
SC = [67, 69, 71, 72, 74, 76, 78]
CH = {"G": (55, 59, 62, 67), "C": (55, 60, 64, 67), "D": (54, 57, 62, 66), "D7": (54, 57, 60, 62), "Em": (55, 59, 64, 67), "Am": (57, 60, 64, 69)}
ROOT = {"G": 43, "C": 48, "D": 50, "D7": 50, "Em": 52, "Am": 45}
FIFTH = {"G": 50, "C": 43, "D": 45, "D7": 45, "Em": 47, "Am": 52}
PCS = {k: {m % 12 for m in v} for k, v in CH.items()}
def bt(bar): return BIG2 + bar * BAR
HAR = [(-99, "G"), (-3.5, "C"), (-3, "G"), (-1.2, "C"), (-0.5, "D"),
       (0, "G"), (1, "C"), (2, "D"), (3, "G"), (4, "Em"), (5, "C"), (6, "Am"), (6.5, "D"), (7, "D7"),     # A: sentence -> V7-I into guard
       (8, "G"), (9, "C"), (10, "D"), (11, "G"), (12, "C"), (12.5, "G"), (14.5, "D"),                    # B: call/response, breakdown on G, dominant build
       (16, "C"), (18, "G"), (19, "C"), (20, "D"), (21, "G"), (22, "Em"), (23, "C"), (24, "D"),  # C: inversion, restatement, half cadence
       (24.5, "C"), (25, "Am"), (25.5, "Em"), (26.5, "D"), (27, "G"), (28, "C"), (29, "G"),               # D: suspense, breath
       (29.5, "G"), (30.5, "C"), (31.5, "G"), (32.5, "D7"), (33.5, "G")]                                   # water build, final statement
def ch(tt):
    b = (tt - BIG2) / BAR + 1e-6; c = "G"
    for b0, name in HAR:
        if b >= b0: c = name
    return c
def pitch(dg, base=0): o, r = divmod(dg, 7); return SC[r] + 12 * o + base
G = {"banjo": 1.7, "harm": 1.3, "bass": 1.1, "kal": 1.3, "chop": 1.0, "roll": 1.0}
# ================= MOTIF M (G B D E D B | C B A G) and operators =================
M1 = [(0, 0, 2), (2, 2, 2), (4, 4, 4), (8, 7, 2), (10, 5, 2), (12, 4, 4)]   # G B D | G' E D  (leap of a 4th = signature)
M2 = [(0, 3, 3), (3, 2, 1), (4, 1, 4), (8, 0, 6)]
CAD = [(0, 4, 4), (4, 6, 2), (6, 5, 2), (8, 3, 4), (12, 1, 4)]       # D F# E C A over D7
def seq(ev, n): return [(p, d + n, l) for p, d, l in ev]
def inv(ev): return [(p, -d, l) for p, d, l in ev]
def aug(ev, k=2): return [(p * k, d, l * k) for p, d, l in ev]
def frag(ev, n): return ev[:n]
def last(ev, d=None, l=None): p, d0, l0 = ev[-1]; return ev[:-1] + [(p, d0 if d is None else d, l0 if l is None else l)]
HALF = lambda n: last(seq(frag(M1, 3), n), l=4)
LOG = []
def lead(t0, ev, inst, base=0, g=1.0, vel=104, tag="", strong=True):
    for p, d, l in ev:
        tt = t0 + p * S16 + (0.02 * BEAT if p % 2 else 0); c = ch(tt + 1e-3); m = pitch(d, base)
        if inst == "Banjo":
            add(gmn("Banjo", m, S16 * l * 1.2, vel, 0.25), tt, 0.32 * g * G["banjo"], pan=0.15, wet=0.2, echo=0.1, bus="mel")
            if l >= 4: add(gmn("Banjo", m, S16 * 2, vel - 20, 0.2), tt + S16 * 2, 0.16 * g * G["banjo"], pan=0.15, bus="mel")   # banjo re-pick on long notes
        elif inst == "Kalimba": add(gmn("Kalimba", m, S16 * l + 0.3, vel, 0.4), tt, 0.3 * g * G["kal"], pan=-0.2, wet=0.4, echo=0.25, bus="mel")
        else: add(gmn(inst, m, S16 * l * 1.0, vel, 0.25), tt, 0.24 * g * G["harm"], pan=-0.15, wet=0.35, echo=0.12, bus="mel")
        if strong: LOG.append((tt, round(((tt - org(tt)) / S16)) % 16, m, c, inst, tag))
# ================= accompaniment =================
def oompah(t0, t1, g=1.0):        # tuba root on 1, fifth on 3 (+ acoustic bass doubling)
    for tt, k, b in grid(t0, t1, 1):
        c = ch(tt + 1e-3); m = ROOT[c] if k % 4 in (0,) else (FIFTH[c] if k % 4 == 2 else None)
        if m is None: continue
        add(gmn("Tuba", m, BEAT * 0.8, 105, 0.1), tt, 0.4 * g * G["bass"]); add(gmn("Acoustic Bass", m, BEAT * 0.9, 100, 0.1), tt, 0.3 * g * G["bass"])
def walk(t0, t1, g=1.0):          # quarter-note walking bass for calm sections
    for tt, k, b in grid(t0, t1, 1):
        c = ch(tt + 1e-3); m = [ROOT[c], ROOT[c] + 4 - (c in ("Em", "Am")), FIFTH[c] + (12 if FIFTH[c] < ROOT[c] else 0), ROOT[c] + 2][k % 4]
        add(gmn("Acoustic Bass", m, BEAT * 0.9, 95, 0.1), tt, 0.42 * g * G["bass"])
def chop(t0, t1, g=1.0):          # steel-guitar chord chop on 2 and 4
    for tt, k, b in grid(t0, t1, 1):
        if k % 2 == 1:
            for j, m in enumerate(CH[ch(tt + 1e-3)]): add(gmn("Steel Guitar", m, BEAT * 0.35, 92, 0.08), tt + j * 0.008, 0.07 * g * G["chop"], pan=-0.35)
def roll(t0, t1, g=1.0):          # banjo forward roll, 8ths, chord tones (accompaniment, low velocity)
    for tt, k, b in grid(t0, t1, 2):
        c = CH[ch(tt + 1e-3)]; m = (c[0], c[1], c[3], c[1] + 12, c[2], c[3], c[1], c[2] + 12)[k % 8]
        add(gmn("Banjo", m, S8 * 1.5, 62 + 14 * (k % 4 == 0), 0.15), tt, 0.1 * g * G["roll"], pan=0.4, wet=0.15)
def kit(t0, t1, g=1.0, style="full"):
    for tt, k, b in grid(t0, t1, 4):
        kk = k % 16
        if style in ("full", "build") and kk in (0, 8) or (style == "half" and kk == 0): add(dr(36, 115), tt, 0.7 * g)
        if style in ("full", "build", "half") and kk in (4, 12): add(dr(39, 95), tt, 0.3 * g, wet=0.2); add(dr(38, 60), tt, 0.18 * g)
        if kk % 2 == 0: add(dr(70, 55 + 30 * (kk % 4 == 2)), tt, 0.16 * g, pan=-0.4)     # washboard-ish maracas 8ths
        if style == "full" and kk in (6, 14): add(dr(76 if kk == 6 else 77, 80), tt, 0.12 * g, pan=0.4)   # woodblock
        if style == "build" and kk >= 8: add(dr(38, 45 + 4 * kk), tt, 0.16 * g * (0.4 + kk / 16))
        if style == "build" and kk < 8 and kk % 2 == 0: add(dr(38, 45), tt, 0.07 * g)
def kal(t0, t1, g=1.0):
    for tt, k, b in grid(t0, t1, 2):
        c = CH[ch(tt + 1e-3)]; m = (c[1:] + (c[1] + 12, c[2] + 12))[k % 5] + 12
        add(gmn("Kalimba", m, 0.6, 76, 0.4), tt, 0.18 * g * G["kal"], pan=0.3 * math.sin(k), wet=0.4, echo=0.3)
def band(t0, t1, g=1.0, style="full", rl=True):
    kit(t0, t1, g, style); oompah(t0, t1, g); chop(t0, t1, g)
    if rl: roll(t0, t1, g)
def taiko(t0, g=1.0): add(gmn("Taiko Drum", 36, 1.5, 127, 0.8), t0, 0.9 * g, wet=0.35)
def sub(t0, g=1.0, dur=1.2):
    t = tt_(dur); f = 34 + 70 * np.exp(-t * 14)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) * 0.8, t0, g, human=False)
def chordhit(t0, c="D", g=1.0):
    for m in CH[c]: add(gmn("Banjo", m, 1.2, 120, 0.6), t0, 0.2 * g, wet=0.4, bus="mel"); add(gmn("Steel Guitar", m, 1.6, 110, 0.8), t0, 0.14 * g, wet=0.5)
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
    chordhit(t0, "G", g); duck(t0 + 0.02, 0.4, 0.9)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; u = t / (t1 - t0)
    nz = rng.standard_normal(n); y = nz - np.convolve(nz, np.ones(6) / 6, "same")
    add(y * u ** 2 * 0.07, t0, g, human=False)
    for j in range(int((t1 - t0) / S16)): add(gmn("Banjo", 62 + j, S16, 80, 0.1), t0 + j * S16, 0.12 * g * (0.4 + 0.6 * j * S16 / (t1 - t0)), bus="mel")


def egghatch(t0, g=0.3): addfx(sfx(63, pitch=V()), t0, g)
def scrape(t0, g=0.25): addfx(sfx(146, pitch=V()), t0, g)
def thunk(t0, g=0.5): addfx(sfx(165), t0, g)
def click(t0, g=0.25): addfx(sfx(149, pitch=V()), t0, g)
def boing(t0, g=0.3): addfx(sfx(121), t0, g)
def jungle(t0, t1, g=0.08):
    addfx(sfx(198, start=3.0, dur=t1 - t0 + 0.5, fade=0.4), t0, g, peak=False)
# =============== ARRANGEMENT (bars counted from BIG2; every lead bar = a named operator on M) ===============
jungle(0, BIG2, 0.09)
# hook: ACCENT 1, full band, banjo foreshadows M1, tape-stop
big(HOOK_HIT, 1.0); band(HOOK_HIT, HOOK_STOP, 1.0)
lead(HOOK_HIT, M1, "Banjo", tag="M1 foreshadow"); lead(HOOK_HIT + BAR, frag(M2, 2), "Banjo", tag="M2 frag")
boing(HOOK_HIT + 0.1, 0.25); s_whoosh(HOOK_HIT + 0.9, 0.2)
# stay (trail cam): sneaky walking bass + soft maracas, kalimba hums the first 4 notes of M1 at x2
walk(T["stay"], T["q"], 0.8); kit(T["stay"], T["q"], 0.5, "none")
lead(T["stay"], aug(frag(M1, 4)), "Kalimba", g=0.8, vel=86, tag="aug frag")
s_twinkle(at("stay", 0.5), 0.2)
# q: roll cell G-A-B in 8ths then 16ths, riser into BIG2
riser(T["q"] + BEAT * 0.5, BIG2 - BEAT / 4, 0.5); s_pop(T["q"] + 0.05, 0.4)
tq = T["q"]
for i in range(3): lead(tq + i * S8, [(0, i % 3, 2)], "Banjo", g=0.8, vel=92, strong=False)
for i in range(4): lead(tq + 3 * S8 + i * S16 * 1.0, [(0, 2 + i, 1)], "Banjo", g=0.9, vel=100, strong=False)
# ---- A (0-8): reveal/call/where/rule — ACCENT 2, sentence in banjo
big(BIG2, 1.1)
band(bt(0), bt(8), 1.0)
lead(bt(0), M1, "Banjo", tag="BI"); lead(bt(1), M2, "Banjo", tag="BI")
lead(bt(2), seq(M1, 4), "Banjo", tag="seq+4"); lead(bt(3), seq(M2, 4), "Banjo", tag="seq+4")
lead(bt(4), seq(M1, 5), "Banjo", tag="frag seq+5"); lead(bt(5), seq(M1, 3), "Banjo", tag="frag seq+3")
lead(bt(6), HALF(5), "Banjo", tag="half frag"); lead(bt(6.5), HALF(4), "Banjo", tag="half frag")
lead(bt(7), CAD, "Banjo", tag="cadence V7")
for i in range(4): s_pop(at("reveal", 1 + i * 0.4), 0.25)
s_kal(at("reveal", 3), 0.3); egghatch(at("reveal", 4), 0.2)
for i in range(4): egghatch(at("call", 0.3 + i * 0.7), 0.25); s_pop(at("call", 0.6 + i * 0.7), 0.2)
s_pop(at("where", 1.0), 0.3); s_snap(at("where", 1.5), 0.4); s_pop(at("where", 2.0), 0.25); click(at("where", 4), 0.35)
thunk(T["rule"] + 0.05, 0.5); s_pop(at("rule", 1.5), 0.3)
for j in range(12): click(at("rule", 2) + j * (3 * BEAT / 12), 0.12)
s_snap(at("rule", 5.2), 0.35)
# ---- B (8-16): guard/tilt1/tilt2/dig — call (banjo) and response (harmonica); breakdown; dominant build
band(bt(8), bt(12.5), 1.0)
lead(bt(8), M1, "Banjo", tag="call"); lead(bt(9), M2, "Harmonica", base=-12, tag="answer")
lead(bt(10), seq(M1, 4), "Banjo", tag="call seq+4"); lead(bt(11), seq(M2, 4), "Harmonica", base=-12, tag="answer seq+4")
lead(bt(12), HALF(3), "Banjo", tag="half frag (C)")
for i in range(4):
    t0 = at("guard", 0.3 + i * 0.9); s_pop(t0, 0.3); s_deny(t0 + 0.45, 0.25); s_whoosh(t0 + 0.7, 0.18)
for h in (at("tilt1", 1), at("tilt1", 3)): s_whoosh(h - 0.05, 0.28); s_snap(h + 0.12, 0.35)
s_pop(at("tilt1", 3.2), 0.3)
walk(bt(12.5), bt(14.5), 0.75); kit(bt(12.5), bt(14.5), 0.45, "none")
lead(bt(12.5), aug(frag(M1, 3)), "Kalimba", g=0.9, vel=88, tag="aug frag (breakdown)")
s_pop(at("tilt2", 3), 0.3)
kit(bt(14.5), bt(16), 0.85, "build"); oompah(bt(14.5), bt(16), 0.9); chop(bt(14.5), bt(16), 0.8)
lead(bt(14.5), HALF(4), "Banjo", tag="half frag"); lead(bt(15), HALF(4), "Banjo", tag="half frag")
lead(bt(15.5), [(0, 4, 2), (2, 5, 2), (4, 6, 4)], "Banjo", tag="quarter frag -> leading tone")
thunk(at("dig", 0.5), 0.4)
for j in range(6): scrape(at("dig", 0.6 + j * 0.6), 0.22)
s_twinkle(at("dig", 4.1), 0.3)
# ---- C (16-24.5): think/bumps/drop/vib — development: inversion at half-time (kalimba), restatement, harmonica sequence, half cadence
walk(bt(16), bt(18), 0.85); kit(bt(16), bt(18), 0.7, "half"); chop(bt(16), bt(18), 0.6)
lead(bt(16), aug(inv(M1)), "Kalimba", g=1.0, tag="inv aug")
for b_ in (16.75, 17.75): roll(bt(b_), bt(b_ + 0.25), 0.8)
s_pop(at("think", 0.3), 0.3); s_pop(at("think", 1.5), 0.25)
band(bt(18), bt(24.5), 0.95)
lead(bt(18), M1, "Banjo", tag="BI"); lead(bt(19), M2, "Banjo", tag="BI")
lead(bt(20), seq(M1, 4), "Banjo", tag="seq+4"); lead(bt(21), seq(M2, 4), "Banjo", tag="seq+4")
lead(bt(22), seq(M1, 5), "Harmonica", base=-12, tag="seq+5"); lead(bt(23), seq(M1, 3), "Harmonica", base=-12, tag="seq+3")
lead(bt(24), [(0, 4, 8)], "Harmonica", base=-12, tag="half cadence on D")
s_arp(at("bumps", 0.5), 0.3); s_pop(at("bumps", 1.5), 0.3); s_pop(at("bumps", 3), 0.25)
s_pop(at("drop", 0.3), 0.25); addfx(sfx(70, pitch=1.3), at("drop", 1.6), 0.35); s_pop(at("drop", 2.0), 0.25)
s_pop(at("vib", 0.4), 0.25); s_pop(at("vib", 1.5), 0.3); s_kal(at("vib", 3), 0.3)
# ---- D (24.5-34.5): maybe/card/water/end — suspense, breath, build, fullest final statement, no third accent
walk(bt(24.5), bt(27), 0.7); kit(bt(24.5), bt(27), 0.5, "none")
lead(bt(24.5), aug(M2), "Kalimba", base=12, g=0.9, tag="aug M2")
thunk(at("maybe", 0.3), 0.35); s_pop(at("maybe", 2), 0.25)
walk(bt(27), bt(29.5), 0.6); kal(bt(27), bt(29.5), 0.7)
for j in range(5): lead(bt(27) + j * BEAT * 2, [(0, 0, 2), (2, 1, 2), (4, 2, 4)], "Banjo", g=0.6, vel=88, tag="cell")
s_whoosh(T["card"] + 0.05, 0.2); s_pop(T["card"] + 0.12, 0.3)
for i in range(3): s_pop(at("card", 1.2 + i * 0.8), 0.22)
band(bt(29.5), bt(31.5), 0.95, "build")
lead(bt(29.5), HALF(0), "Banjo", tag="half frag"); lead(bt(30), HALF(2), "Banjo", tag="half frag")
lead(bt(30.5), HALF(3), "Banjo", tag="half frag"); lead(bt(31), [(0, 3, 2), (2, 4, 2), (4, 5, 2), (6, 6, 2)], "Banjo", tag="run-up")
for i in range(3): t0 = at("water", 0.5 + i * 0.9); boing(t0, 0.2); addfx(sfx(70, pitch=1.4 + 0.1 * i), t0 + 0.8, 0.3)
s_deny(at("water", 3.3), 0.3); s_kal(at("water", 3.8), 0.35); s_bub(at("water", 3.9), 0.3)
FINAL = bt(33.5)
band(bt(31.5), FINAL, 1.15); kal(bt(31.5), FINAL, 0.5)
for inst, base, gg in (("Banjo", 0, 1.0), ("Harmonica", -12, 0.8)):
    lead(bt(31.5), M1, inst, base, gg, tag="final BI"); lead(bt(32.5), CAD, inst, base, gg, tag="final V7")
    lead(FINAL, [(0, 0, 16)], inst, base, gg, tag="final tonic")
chordhit(FINAL, "G", 0.8); oompah(FINAL, FINAL + BEAT * 0.5, 0.9)
for i in range(3): s_pop(at("end", 0.6 + i * 0.5), 0.25)
s_twinkle(at("end", 2), 0.3); jungle(T["end"], DUR, 0.06)
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
MIX[i0:i1] = seg; MIX[i1:int((HOOKCUT + 0.08) * SR)] *= np.linspace(0.3, 1, int(0.08 * SR))[:, None]
MIX = MIX / (np.abs(MIX).max() + 1e-9)
MIX = MIX * DUCK[:, None] + FX * 0.9
MIX = np.tanh(MIX * 1.8); MIX /= np.abs(MIX).max() / 0.85
MIX = MIX[: int(SR * DUR)]
fo = int(1.2 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
with wave.open("/workspace/work/croc/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG2 %.2f" % (BPM, DUR, BIG2))
