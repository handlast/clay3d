# 《住在海里的蜘蛛》BGM — "Island calypso swing": F major, 104.08 BPM, 4/4 (8 bars 4/4 + 1 bar 2/4 = 19.6 s -> 0.4 s & 20.0 s on bar lines).
# Steel Drums lead (original melody, tremolo rolls on long notes) + Nylon Guitar calypso strum + Finger Bass (root / fifth calypso pattern)
# + Brush kit, shaker & cabasa, light cowbell; Kalimba/Pizzicato tiptoe for the night + hunt breakdowns.
# 16th swing 20%, laid-back brush snare. Big hits only at 0.4 / 20.0; silence 19.42-20.0. Event SFX: Seashore wave sample,
# synthetic wave crash, door clicks ("咔哒"), water pour, empty-cup drip ("滴"), stopwatch ticks, slide whistle, coin ding, ball bounce.
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import piano as _piano, gm as _gm, drum as _drum, SR
from cues import *
# measured peaks @vel100: Steel Drums .79, Nylon Guitar 3.1, Finger Bass .77, Kalimba .69, Pizzicato .78, Marimba 7.6, Xylophone 4.46, Seashore 1.0
LV = {"Steel Drums": 1.0, "Nylon Guitar": 0.25, "Finger Bass": 1.0, "Kalimba": 1.1, "Pizzicato Strings": 1.0, "Marimba": 0.11, "Xylophone": 0.18,
      "Seashore": 0.8, "Brass Section": 0.55, "Reverse Cymbal": 4.0, "Celeste": 1.4}
DLV = {42: 0.6, 46: 0.9, 76: 0.17, 77: 0.17, 45: 0.17, 47: 0.17, 50: 0.17}
@functools.lru_cache(maxsize=None)
def gm(name, m, dur=0.5, vel=100, release=0.2, decay=None): return _gm(name, m, dur, vel, release=release, decay=decay) * LV.get(name, 1.0)
@functools.lru_cache(maxsize=None)
def drum(n, vel=100): return _drum(n, vel) * DLV.get(n, 1.0)
@functools.lru_cache(maxsize=None)
def brush(n, vel=100): return _gm("Brush", n, 1.0, vel, release=0.05, bank=128) * {36: 0.55, 42: 0.6}.get(n, 1.0)
@functools.lru_cache(maxsize=None)
def piano(m, dur=0.4, vel=60): return _piano(m, dur, vel) * 12
N = int(SR * DUR); MIX = np.zeros((N, 2)); VERB = np.zeros((N, 2)); ECHO = np.zeros((N, 2))
rng = np.random.default_rng(31)
def add(y, t0, g=1.0, pan=0.0, wet=0.0, echo=0.0, human=True):
    if human: g *= 1 + rng.uniform(-0.06, 0.06); t0 += rng.uniform(-0.003, 0.003)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    MIX[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet
    if echo: ECHO[i:i + len(y)] += y * echo
def mono(y): return np.stack([y, y], 1)
tt_ = lambda d: np.arange(int(d * SR)) / SR
S16 = BEAT / 4; SW = 0.2 * S16; LAY = 0.012
# ---------------- grid: bars 0-7 4/4, bar 8 = 2/4 (18.85-20.0), bars 9+ 4/4 from 20.0 ----------------
def bar_start(b):
    if b < 9: return G0 + b * BAR
    return G1 + (b - 9) * BAR
def bar_len(b): return 8 if b == 8 else 16
def ph(b): return b if b < 9 else b - 9          # restart the 8-bar cycle on the 20.0 s downbeat
def sixteenths(t0, t1):
    out = []
    for b in range(-1, 40):
        s0 = bar_start(b)
        if s0 > t1 + 0.1: break
        for k in range(bar_len(b)):
            tt = s0 + k * S16
            if t0 - 1e-4 <= tt < t1 - 1e-4: out.append((tt + (SW if k % 2 else 0), k, b))
    return out
# ---------------- harmony + parts ----------------
PROG = ["F", "Bb", "C7", "F", "Dm", "Gm", "C7", "F"]
CH = {"F": (53, 57, 60, 65), "Bb": (53, 58, 62, 65), "C7": (52, 55, 58, 60), "Dm": (50, 53, 57, 62), "Gm": (50, 55, 58, 62)}
ROOT = {"F": 41, "Bb": 34, "C7": 36, "Dm": 38, "Gm": 43}
FIFTH = {"F": 48, "Bb": 41, "C7": 43, "Dm": 45, "Gm": 38}
def chord_of(b): return "C7" if b == 8 else PROG[ph(b) % 8]
MEL = [[(0, 72, 2), (2, 77, 2), (4, 81, 3), (7, 79, 1), (8, 77, 2), (10, 81, 2), (12, 84, 4)],
       [(0, 82, 2), (2, 81, 2), (4, 79, 2), (6, 77, 2), (8, 74, 3), (11, 77, 1), (12, 79, 4)],
       [(0, 79, 2), (2, 76, 1), (3, 79, 1), (4, 82, 3), (7, 81, 1), (8, 79, 2), (10, 76, 2), (12, 72, 4)],
       [(0, 77, 3), (3, 77, 1), (4, 81, 2), (6, 77, 2), (8, 72, 6), (14, 74, 1), (15, 76, 1)],
       [(0, 77, 2), (2, 81, 2), (4, 86, 3), (7, 84, 1), (8, 81, 2), (10, 77, 2), (12, 74, 4)],
       [(0, 79, 2), (2, 82, 2), (4, 86, 2), (6, 82, 2), (8, 79, 3), (11, 77, 1), (12, 74, 4)],
       [(0, 76, 2), (2, 79, 2), (4, 82, 2), (6, 84, 2), (8, 82, 2), (10, 79, 2), (12, 76, 2), (14, 79, 2)],
       [(0, 77, 4), (4, 72, 2), (6, 77, 2), (8, 81, 6)]]
HARM = {72: 69, 74: 70, 76: 72, 77: 74, 79: 76, 81: 77, 82: 79, 84: 81, 86: 82}   # diatonic third below
def pan_note(t0, m, du16, g=1.0, harm=True):
    dur = du16 * S16
    if du16 >= 4:   # steel-pan tremolo roll on long notes
        n = int(dur / (S16 / 2))
        for j in range(n): add(gm("Steel Drums", m, S16 * 0.6, 112 if j == 0 else 86, 0.12), t0 + j * S16 / 2, 0.5 * g * (1 if j == 0 else 0.75), pan=-0.1, wet=0.2, echo=0.15 if j == 0 else 0)
    else:
        add(gm("Steel Drums", m, dur * 0.9, 112, 0.15), t0, 0.5 * g, pan=-0.1, wet=0.2, echo=0.18)
    if harm and m in HARM: add(gm("Steel Drums", HARM[m], dur * 0.85, 92, 0.12), t0 + 0.004, 0.22 * g, pan=0.25, wet=0.2)
def lead(t0, t1, g=1.0, harm=True):
    for tt, k, b in sixteenths(t0, t1):
        if b == 8: continue
        for pos, m, du in MEL[ph(b) % 8]:
            if pos == k: pan_note(tt, m, du, g, harm)
def strum(t0, ch, g=1.0, vel=88, up=False):
    notes = [ch[0] - 12 + 12, ch[1], ch[2], ch[3]] if not up else list(reversed(ch[1:]))
    for j, m in enumerate(notes): add(gm("Nylon Guitar", m, 0.22, vel, 0.1), t0 + j * 0.009, 0.32 * g, pan=0.22, wet=0.12)
def guitar(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k in (0, 6, 8, 12, 14): strum(tt, CH[chord_of(b)], g, 92 if k in (0, 8) else 70, up=k in (6, 14))
def bass(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        c = chord_of(b)
        pat = {0: ROOT[c], 6: FIFTH[c], 8: ROOT[c], 12: ROOT[c] + 12 if c != "Gm" else ROOT[c], 14: FIFTH[c]}
        if b == 8: pat = {0: 36, 4: 43}
        if k in pat: add(gm("Finger Bass", pat[k], S16 * (2 if k in (0, 8) else 1.6), 112 if k in (0, 8) else 96, 0.06), tt, 0.95 * g)
def drums(t0, t1, style="full", g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if style in ("full", "lite"):
            if k in (0, 8): add(brush(36, 110), tt, 0.9 * g)
            if style == "full" and k == 11 and ph(b) % 2: add(brush(36, 80), tt, 0.5 * g)
            if k in (4, 12): add(brush(38, 105), tt + LAY, 0.7 * g, wet=0.15)
            if style == "full" and k in (7, 15) and ph(b) % 2 == 0: add(brush(38, 50), tt + LAY, 0.25 * g)
            if k % 2 == 0: add(brush(42, 80 if k % 4 == 0 else 55), tt, 0.3 * g, pan=0.3)
            if style == "full" and k in (6, 14): add(drum(56, 70), tt, 0.1 * g, pan=-0.35)
        if style in ("full", "lite", "shaker"):
            add(drum(82, 85 if k % 4 == 2 else 55), tt, (0.22 if style != "lite" else 0.16) * g, pan=-0.3)
        if style == "full" and k % 4 == 0: add(drum(69, 60), tt, 0.12 * g, pan=0.4)
def groove(t0, t1, g=1.0, ld=True, dr="full"):
    drums(t0, t1, dr, g); bass(t0, t1, g); guitar(t0, t1, g)
    if ld: lead(t0, t1, g)
TIP = [(0, 72), (2, 77), (4, 79), (6, 81), (8, 79), (10, 77), (12, 76), (14, 74)]
def tiptoe(t0, t1, g=1.0, inst="Pizzicato Strings"):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m in TIP:
            if pos == k and (k % 4 == 0 or ph(b) % 2): add(gm(inst, m - (12 if inst == "Pizzicato Strings" else 0), 0.15, 95, 0.1), tt, 0.4 * g, pan=0.2, wet=0.25, echo=0.2)
# ---------------- SFX ----------------
def boom(t0, g=1.0, dur=1.1):
    t = tt_(dur); f = 36 + 80 * np.exp(-t * 16)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2) * 0.9), t0, g, human=False)
def thump(t0, g=1.0, f0=52):
    t = tt_(0.3); f = f0 + 40 * np.exp(-t * 30)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12) * 0.8), t0, g, human=False)
def tick(t0, g=1.0, f=3200):
    t = tt_(0.04); y = np.sin(2 * np.pi * f * t) * np.exp(-t * 160) + rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.4
    add(mono(y * 0.35), t0, g, pan=0.2, human=False)
def click(t0, g=1.0):
    t = tt_(0.03); add(mono(rng.standard_normal(len(t)) * np.exp(-t * 300) * 0.5), t0, g, human=False)
def latch(t0, g=1.0):          # door "咔哒": two woody clicks + tiny body
    for dt, f, gg in ((0, 1800, 1.0), (0.07, 1300, 0.8)):
        t = tt_(0.06); y = np.sin(2 * np.pi * f * t) * np.exp(-t * 90) * 0.5 + np.convolve(rng.standard_normal(len(t)), np.ones(3) / 3, "same") * np.exp(-t * 250) * 0.5
        add(mono(y * 0.6), t0 + dt, g * gg, wet=0.1, human=False)
    thump(t0 + 0.07, 0.35 * g, 110)
def whoosh(t0, d=0.35, g=1.0, f0=400):
    n = int(d * SR); t = np.arange(n) / SR
    nz = rng.standard_normal(n); k = max(2, int(SR / f0 / 2))
    y = nz - np.convolve(nz, np.ones(k) / k, "same"); y = np.convolve(y, np.ones(3) / 3, "same")
    add(mono(y * np.sin(np.pi * t / d) ** 2 * 0.12), t0, g, human=False)
def popfx(t0, g=1.0, f0=1200, f1=300):
    t = tt_(0.09); f = f1 + (f0 - f1) * np.exp(-t * 60)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.32), t0, g, human=False)
def ding(t0, g=1.0, f=2637):
    t = tt_(1.2); y = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t * 3) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6))
    add(mono(y * np.exp(-t * 3.5) * np.minimum(1, t / 0.002) * 0.16), t0, g, wet=0.6, echo=0.4, human=False)
def coinfx(t0, g=1.0):
    ding(t0, 0.7 * g, 1976); ding(t0 + 0.08, 0.9 * g, 2637)
def drip(t0, g=1.0, f=900, pan=None):
    t = tt_(0.25); fr = f * (1 + 1.2 * (1 - np.exp(-t * 40)))
    add(mono(np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 28) * 0.22), t0, g, pan=rng.uniform(-0.4, 0.4) if pan is None else pan, wet=0.9, echo=0.3, human=False)
def crash_wave(t0, g=1.0, d=1.6):   # synthetic surf crash: lowpassed noise burst with long tail
    n = int(d * SR); t = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(18) / 18, "same") * 4
    y *= np.minimum(1, t / 0.03) * np.exp(-t * 2.4) * (1 + 0.3 * np.sin(2 * np.pi * 3 * t))
    add(np.stack([y, np.roll(y, 300)], 1) * 0.35, t0, g, wet=0.4, human=False)
def surf(t0, d, g=1.0): add(gm("Seashore", 60, min(d, 1.0), 100, 0.6), t0, g, human=False)
def swell(t0, d, g=1.0, per=2.6):   # gentle synthetic surf: lowpassed noise with slow swells
    n = int(d * SR); t = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(24) / 24, "same") * 4
    env = (0.25 + 0.75 * np.sin(np.pi * ((t / per) % 1)) ** 3) * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.8)
    add(np.stack([y * env, np.roll(y, 500) * env], 1) * 0.12, t0, g, wet=0.3, human=False)
def pour(t0, d=0.8, g=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(10) / 10, "same") * np.minimum(1, t / 0.1) * np.minimum(1, (d - t) / 0.1) * (0.8 + 0.2 * np.sin(2 * np.pi * 7 * t)) * 0.3
    add(np.stack([y, np.roll(y, 200)], 1), t0, g, wet=0.3, human=False)
    for j in range(int(d * 9)): popfx(t0 + 0.05 + j / 9 + rng.uniform(0, 0.05), 0.18 * g, rng.uniform(1300, 2200), 600)
def slide(t0, f0, f1, d=0.4, g=1.0):   # slide whistle
    t = tt_(d); f = f0 * (f1 / f0) ** (t / d) * (1 + 0.01 * np.sin(2 * np.pi * 6 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.2 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    add(mono(y * np.sin(np.pi * t / d) ** 0.5 * 0.12), t0, g, wet=0.3, human=False)
def scream(t0, g=1.0, d=0.7):   # cartoon "aaah": sawtooth-ish vowel sweep with vibrato
    t = tt_(d); f = 520 + 380 * np.minimum(1, t / 0.12) + 18 * np.sin(2 * np.pi * 9 * t)
    ph_ = 2 * np.pi * np.cumsum(f) / SR
    y = sum(np.sin(ph_ * h) / h * (1.6 if h in (2, 3) else 1) for h in range(1, 8))
    add(mono(y * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.15) * 0.07), t0, g, wet=0.3, human=False)
def bounce(t0, g=1.0): thump(t0, 0.8 * g, 90); click(t0, 0.5 * g)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T = t1 - t0
    y = np.convolve(rng.standard_normal(n), np.ones(5) / 5, "same") * (t / T) ** 2.5 * 0.07
    f = 180 * (1600 / 180) ** (t / T); y += np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / T) ** 2 * 0.04
    add(mono(y), t0, g, human=False)
def rumble(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T = t1 - t0
    y = np.convolve(rng.standard_normal(n), np.ones(40) / 40, "same") * 6
    y *= (0.55 + 0.45 * np.sin(2 * np.pi * 14 * t) ** 2) * np.minimum(1, t / 0.05) * np.minimum(1, (T - t) / 0.15)
    add(mono(y * 0.08), t0, g, human=False)
def xy(t0, m, g=1.0, du=0.3): add(gm("Xylophone", m, du, 105, 0.2), t0, 0.5 * g, wet=0.25)
def kal(t0, m, g=1.0, du=0.4): add(gm("Kalimba", m, du, 100, 0.3), t0, 0.45 * g, wet=0.3, echo=0.25)
def pn(t0, m, g=1.0, du=0.25): add(gm("Steel Drums", m, du, 115, 0.2), t0, 0.5 * g, wet=0.25, echo=0.2)
def big(t0, g=1.0):
    boom(t0, 1.2 * g, 1.3); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 127), t0, 0.6 * g, wet=0.35); add(drum(57, 110), t0 + 0.01, 0.3 * g, pan=0.4)
    add(brush(38, 127), t0, 0.6 * g, wet=0.3)
    for m in (65, 69, 72, 77, 81): add(gm("Steel Drums", m, 0.5, 125, 0.25), t0, 0.32 * g, wet=0.35)
    for m in (53, 60, 65): add(gm("Brass Section", m, 0.3, 120, 0.12), t0, 0.3 * g, wet=0.3)
    add(gm("Finger Bass", 29, 0.7, 127, 0.15), t0, 1.1 * g)
    crash_wave(t0, 0.9 * g)

# ---------------- arrangement ----------------
surf(0.0, 0.5, 0.8); whoosh(0.02, 0.36, 1.2, 300)
for j, m in enumerate([72, 77, 81]): pn(HOOK_HIT - (3 - j) * S16 * 0.66, m, 0.6, 0.1)
big(HOOK_HIT); latch(HOOK_HIT + 0.02, 1.0)
groove(HOOK_HIT, NIGHT)
popfx(QLINE, 0.6)
# (tape stop 2.13 -> 2.42 applied after the mix; lamp click + surf fill the gap until 2.71)
# night: sneaky tiptoe, brushes lite, bass; no steel lead
drums(LOOP_IN, FAMILY, "lite", 0.8); bass(LOOP_IN, FAMILY, 0.9); tiptoe(LOOP_IN, FAMILY, 1.0)
for j in range(6): tick(NIGHT + 0.5 + j * BEAT, 0.25, 4200)          # crickets-ish
for j, m in enumerate([84, 79, 76, 72]): xy(LEGS + j * S16 * 0.5, m, 0.5, 0.15)
add(drum(77, 90), LEGS, 0.3)
scream(SCREAM, 1.0, 0.75); add(drum(49, 90), SCREAM, 0.3, wet=0.3); thump(SCREAM, 0.5, 70)
popfx(QUOTE, 0.6); for_q = [kal(QUOTE + j * S16 * 2, m, 0.6) for j, m in enumerate([77, 81, 84])]
# family -> door: full calypso
groove(FAMILY, TEST)
add(drum(37, 90), FAMILY - S16, 0.3)
popfx(TARAN, 0.6, 700, 200); kal(KIN_TAG, 84, 0.5); kal(KIN_TAG + S16, 89, 0.5)
for i, h in enumerate(INLAND): xy(h, [74, 77][i], 0.5); popfx(h, 0.4)
popfx(SEA, 0.6); surf(SEA, 0.8, 0.35); pn(SEA, 84, 0.5)
popfx(CARD1, 0.6); kal(CARD1, 81, 0.5)
for j in range(8): xy(TIDE_UP - 0.2 + j * 0.03, 65 + [0, 2, 4, 5, 7, 9, 11, 12][j], 0.4, 0.12)
surf(TIDE_UP - 0.1, 0.9, 0.35)
for j in range(8): xy(TIDE_DN - 0.1 + j * 0.03, 77 - [0, 2, 4, 5, 7, 9, 11, 12][j], 0.4, 0.12)
crash_wave(SOUTH, 0.45)
rumble(WORMS, NODIG - 0.1, 1.0)
add(drum(76, 100), NODIG, 0.5); popfx(NODIG, 0.5, 500, 200)
slide(MOVEIN - 0.05, 1400, 500, 0.55, 1.0)
for j in range(6): tick(RULER - 0.2 + j * 0.05, 0.5, 3600)
pn(RULER, 89, 0.5)
for j in range(5): drip(LINING + j * 0.06, 0.25, 1500 + j * 120)
for i, h in enumerate(ING): popfx(h, 0.6, 900 + 200 * i, 300); kal(h, [72, 77, 81][i], 0.5)
for m in (77, 81, 84): pn(FORM, m, 0.4, 0.4)
coinfx(COIN, 0.9)
whoosh(HIDE - 0.1, 0.4, 0.7); ding(FIND, 0.7, 3136)
# test: drums drop to shaker; bass pedals on C; water pour + stopwatch + riser
drums(TEST, SIL0, "shaker", 1.0)
for tt, k, b in sixteenths(TEST, SIL0):
    if k % 4 == 0: add(gm("Finger Bass", 36, S16 * 2, 108, 0.05), tt, 0.85)
    fast = tt >= TIMER[0] + (TIMER[1] - TIMER[0]) * 0.5
    if (k % 2 == 0) or (fast and tt >= TIMER[0]): tick(tt, 0.4 if k % 4 == 0 else 0.25, 3000 if k % 4 == 0 else 2400)
pour(POUR[0], POUR[1] - POUR[0], 1.0)
riser(RISERS[0][0], SIL0, 1.0)
add(gm("Reverse Cymbal", 60, 1.6, 110), SIL0 - 1.6, 0.6)
pn(ASK, 79, 0.5); pn(ASK + S16, 82, 0.5)
# 20.0 s big hit -> full band
big(BIG2, 1.1); latch(BIG2, 0.6)
groove(BIG2, HUNT)
drip(DRIP, 1.4, 1100, pan=0.0)
for i, h in enumerate(LAYERS): popfx(h, 0.5); kal(h, [72, 77, 81][i], 0.45)
for i, h in enumerate(BOUNCE): xy(h, [84, 88, 91][i], 0.5, 0.15); drip(h, 0.35, 1300 + i * 150)
for h in PULL: add(gm("Finger Bass", 29, 0.3, 120, 0.05), h, 0.6); thump(h, 0.5, 60)
latch(SEAL, 0.9); add(drum(75, 100), SEAL, 0.35)
# hunt: breakdown (STOP1) then half groove
bass(HUNT, TINY, 0.9); tiptoe(HUNT, TINY, 0.9, "Kalimba")
drums(PREY[0], TINY, "lite", 0.8); guitar(PREY[0], TINY, 0.8)
latch(OPEN, 0.6)
for i, h in enumerate(PREY): add(drum([45, 47, 50][i], 110), h, 0.5); popfx(h, 0.6, 1400, 400); add(drum(76, 100), h + 0.05, 0.3)
# tiny -> name: full groove again
groove(TINY, CARD)
for i, h in enumerate(ISL): pn(h, [81, 84][i], 0.5); popfx(h, 0.4)
coinfx(SUM, 0.7)
for h in COURTS: bounce(h, 1.0); bounce(h + 0.22, 0.5)
for j in range(8): click(NAME + 0.1 + j * 0.06, 0.25)
crash_wave(WALL, 0.6); surf(WALL - 0.1, 1.0, 0.35)
for j, m in enumerate([77, 81, 84, 89]): pn(MEAN + j * S16, m, 0.4, 0.2)
pn(PCT_HIT, 89, 0.5); add(drum(49, 90), PCT_HIT, 0.25, wet=0.3)
# card: lite groove
drums(CARD, OUTRO, "lite", 0.8); bass(CARD, OUTRO, 0.9); guitar(CARD, OUTRO, 0.85); lead(CARD, OUTRO, 0.7)
popfx(CARD, 0.6)
for i, h in enumerate(CHIPS): kal(h, [77, 81, 84][i], 0.5); popfx(h, 0.4)
# outro: guitar + pan, door latch, final chord, waves
guitar(OUTRO, FINAL, 0.8); bass(OUTRO, FINAL, 0.8); lead(OUTRO, FINAL, 0.6, harm=False)
END2 = FINAL + 2 * BAR
latch(SHUT, 0.9)
for m in (65, 69, 72, 77): pan_note(FINAL, m, 8, 0.45, harm=False)
strum(FINAL, CH["F"], 0.9, 90); add(gm("Finger Bass", 29, 1.6, 110, 0.4), FINAL, 0.7); add(brush(49, 70), FINAL, 0.2, wet=0.4)
swell(OUTRO, DUR - OUTRO, 0.9)
# tail tag: soft guitar + shaker + pan echo of the hook, fading
for tt, k, b in sixteenths(FINAL + BAR, END2):
    if k in (0, 6, 8, 12, 14): strum(tt, CH[chord_of(b)], 0.6, 72, up=k in (6, 14))
    if k % 4 == 2: add(drum(82, 60), tt, 0.12, pan=-0.3)
for j, (pos, m) in enumerate([(0, 72), (2, 77), (4, 81), (8, 84)]): pn(FINAL + BAR + pos * S16, m, 0.3, 0.3)
for j, m in enumerate([77, 81]): pn(END2 + j * S16 * 2, m, 0.3, 0.6)
drip(END2 + BAR * 0.5, 0.6, 1000, pan=0.0)

# ---------------- mix ----------------
def reverb(x, sec=1.8, dec=3.0):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * dec); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
d = int(3 * S16 * SR)
for r in range(1, 4):
    sh = ECHO[: N - d * r] * (0.4 ** r)
    if r % 2: MIX[d * r:, 0] += sh[:, 1] * 0.8; MIX[d * r:, 1] += sh[:, 0] * 0.3
    else: MIX[d * r:, 0] += sh[:, 1] * 0.3; MIX[d * r:, 1] += sh[:, 0] * 0.8
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
# tape stop on the hook groove (2.13 -> 2.42 s)
ts0, ts1 = HOOK_STOP, NIGHT
i0, i1 = int(ts0 * SR), int(ts1 * SR); n = i1 - i0
rate = np.linspace(1, 0.02, n) ** 1.4; p = i0 + np.cumsum(rate); p = np.clip(p, 0, N - 2); ii = p.astype(int); ff = (p - ii)[:, None]
seg = MIX[ii] * (1 - ff) + MIX[ii + 1] * ff; seg *= np.linspace(1, 0.3, n)[:, None]
MIX[i0:i1] = seg; j1 = int(LOOP_IN * SR) - 200; MIX[i1:j1] *= 0.15
POST = MIX.copy(); MIX[:] = 0; VERB[:] = 0; ECHO[:] = 0
click(LAMP_IN + 0.02, 1.2); ding(LAMP_IN + 0.06, 0.8, 3136); surf(NIGHT - 0.05, 1.2, 0.5)
add(gm("Finger Bass", 36, 0.2, 100, 0.05), LOOP_IN - 2 * S16, 0.8, human=False)
for r in range(1, 3): MIX[d * r:] += ECHO[: N - d * r] * (0.4 ** r)
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
MIX += POST
for a, b in SILENCES:
    i0, i1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.04 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] = 0
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.2); MIX /= np.abs(MIX).max() / 0.85
fo = int(0.8 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("/workspace/work/trapdoor/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
pk = [20 * np.log10(np.sqrt((MIX[int(i * SR / 4):int((i + 1) * SR / 4)] ** 2).mean()) + 1e-9) for i in range(int(DUR * 4))]
print("loudest 0.25s:", sorted([(round(v, 1), i / 4) for i, v in enumerate(pk)])[-6:])
print("ok BPM %.2f  bar %.3fs" % (BPM, BAR))
