# 《如果一口吞下肉包子》BGM — real samples: Salamander Grand Piano + GeneralUser GS (pad, pizz, marimba, bass, drums, timpani)
# F# major pentatonic (black keys F# G# A# C# D#). Fixed frame: one chord per 2 bars (4 s): 宫 F# / 羽 D#m / 商 G#sus / 徵 C#sus.
# Two big hits only: GULP_HIT (0.5 s) and CT_HIT (20 s); light soft end. Tension parameter p(t) drives density.
import sys, math, wave, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import piano, gm, drum, SR
from cues import *
_gm, _drum = gm, drum
LV = {"Marimba": 0.12, "Melodic Tom": 0.15}      # GeneralUser presets differ ~10x in level (initial attenuation not applied)
def gm(name, *a, **k): return _gm(name, *a, **k) * LV.get(name, 1.0)
def drum(note, *a, **k): return _drum(note, *a, **k) * (0.25 if note in (76, 77) else 1.0)
N = int(SR * DUR); MIX = np.zeros((N, 2)); PAD = np.zeros((N, 2)); KICKS = []
rng = np.random.default_rng(11)
def add(y, t0, g=1.0, pan=0.0, bus=None, human=True):
    if human: g *= 1 + rng.uniform(-0.1, 0.1); t0 += rng.uniform(-0.006, 0.006)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    (MIX if bus is None else bus)[i:i + len(y)] += y
def kick(t0, g=1.0): add(drum(36, 110), t0, 0.9 * g); KICKS.append(t0)

CH = {"gong": (42, (66, 70, 73)), "yu": (39, (63, 66, 70)), "shang": (44, (68, 73, 75)), "zhi": (37, (61, 66, 68))}
PROG = ["gong", "yu", "shang", "zhi"]
def chord(t): return CH[PROG[int(t // 4.0) % 4]]
def p(t):  # tension
    if t < HOOK_END: return 0.6
    if t < STUCK: return 0.25
    if t < CRACKLE: return 0.45
    if t < HEART: return 0.6
    if t < CT: return lerp(0.7, 1.0, (t - HEART) / (CT - HEART))
    if t < WHY: return 0.8
    if t < SAFE: return 0.55
    if t < RARE: return 0.35
    if t < ADV: return 0.3
    if t < OUTRO: return 0.5
    return 0.2
def lerp(a, b, k): return a + (b - a) * k

def pad(t0, t1, g=1.0):   # Warm Pad, mid register chord tones, slow attack, cut at each chord change
    t = t0
    while t < t1 - 0.05:
        nx = min(t1, (math.floor(t / 4.0) + 1) * 4.0)
        for m in chord(t + 0.01)[1]:
            add(gm("Warm Pad", m, nx - t - 0.12, 80, attack=0.6, release=0.3), t, 0.16 * g, bus=PAD)
        t = nx

# 4-bar piano phrase (8ths). 起 承 转 合, leaps <= major 3rd, phrase ends on chord tone.
PH = [[73, None, 70, None, 66, 68, 70, None], [70, None, 73, None, 75, None, 73, None],
      [78, None, 75, 73, None, 70, 68, None], [66, None, 68, None, 66, None, None, None]]
def piano_phrase(t0, bars=4, vel=58, g=1.0, oct=0):
    for b in range(bars):
        for k, m in enumerate(PH[b % 4]):
            if m: add(piano(m + oct, 0.45, vel + rng.integers(-8, 8)), t0 + b * 2.0 + k * 0.25, 0.5 * g, pan=0.15)
def groove(t0, t1, g=1.0, half=False, hats=True, bass=True, snare=True):
    nb = int(round((t1 - t0) / BEAT))
    for b in range(nb):
        tb = t0 + b * BEAT; bass_m = chord(tb + 0.01)[0]
        if half:
            if b % 4 == 0: kick(tb, 0.8 * g)
        else:
            if b % 2 == 0: kick(tb, g)
            elif snare: add(drum(38, 90), tb, 0.45 * g)
        if hats:
            add(drum(42, 70), tb, 0.25 * g, pan=0.3); add(drum(42, 50), tb + 0.25, 0.18 * g, pan=0.3)
            if rng.random() < 0.15 * p(tb): add(drum(42, 45), tb + 0.375, 0.12 * g, pan=0.3)   # probabilistic fill
        if bass and (b % 2 == 0 or not half):
            add(gm("Finger Bass", bass_m, 0.4, 100, release=0.08), tb, 0.55 * g)
def pizz(t0, t1, g=1.0):   # sneaky ostinato
    nb = int(round((t1 - t0) / 0.25))
    for k in range(nb):
        tb = t0 + k * 0.25; cc = chord(tb + 0.01)[1]
        if k % 4 in (0, 3) or rng.random() < 0.25 * p(tb):
            add(gm("Pizzicato Strings", cc[k % 3] - 12, 0.25, 95, release=0.1), tb, 0.5 * g, pan=-0.3)
        if k % 2 == 0: add(drum(42, 40), tb, 0.12 * g, pan=0.35)   # tick
def big(t0, g=1.0):
    kick(t0, 1.2 * g); add(drum(49, 120), t0, 0.7 * g)
    add(gm("Timpani", 42, 1.5, 127, release=0.5), t0, 0.9 * g)
    for m in (30, 42, 54): add(piano(m, 1.6, 115), t0, 0.55 * g)
    for m in chord(t0)[1]: add(piano(m, 1.2, 100), t0, 0.35 * g)

# ---------------- arrangement ----------------
# hook: "啊——呜" rising pentatonic piano run into the gulp
for i, m in enumerate([54, 58, 61, 66, 70]): add(piano(m, 0.3, 60 + i * 8), i * 0.09, 0.45)
big(GULP_HIT)
t = np.arange(int(0.5 * SR)) / SR   # gulp: low downward bloop
gulp = np.sin(2 * np.pi * np.cumsum(180 * np.exp(-t * 5) + 60) / SR) * np.exp(-t * 6) * 0.5
add(np.stack([gulp, gulp], 1), GULP_HIT + 0.05, 0.8)
pad(1.0, HOOK_END, 0.8)
# case + bun: light groove + piano phrase (the motif)
groove(CASE, STUCK, 0.7, snare=False); pad(CASE, STUCK); piano_phrase(CASE, 3)
for h in (CASE_HIT, AGE_HIT, RULER): add(gm("Marimba", 78, 0.3, 90), h, 0.25)
add(gm("Marimba", 82, 0.3, 100), CUT, 0.3); add(drum(76, 100), CUT + 0.2, 0.5)
# stuck: half time, tense, water "glug" pops
groove(STUCK, CRACKLE, 0.8, half=True, snare=False); pad(STUCK, CRACKLE, 0.9)
for h in WATER: add(gm("Marimba", 66, 0.2, 80), h + 0.5, 0.25); add(drum(77, 90), h + 0.5, 0.4)
# crackle: drums out, pizz ostinato + woodblock crackles
pizz(CRACKLE, HEART); pad(CRACKLE, HEART, 0.8)
PEN = [66, 68, 70, 73, 75, 78, 80, 82, 85]
for i, h in enumerate(CRK): add(gm("Marimba", PEN[i % len(PEN)] + 12, 0.15, 100), h, 0.18, pan=(i % 2) * 0.6 - 0.3); add(drum(76, 110), h, 0.35)
# heart: lub-dub kicks on BEATS + side-stick "咔嚓", pizz continues, riser into silence
pizz(HEART, CT - 0.5, 0.8); pad(HEART, CT, 0.9)
for h in BEATS: kick(h, 0.75); kick(h + 0.14, 0.45); add(drum(37, 120), h + 0.02, 0.6)
rs = np.arange(int(1.0 * SR)) / SR
rise = np.convolve(rng.standard_normal(len(rs)), np.ones(4) / 4, "same") * (rs / 1.0) ** 2.5 * 0.08
add(np.stack([rise, rise], 1), CT - 1.0, 1.0)
# CT reveal: big hit 2, then full groove + piano phrase an octave up
big(CT_HIT, 1.1)
groove(CT_HIT, WHY, 1.0); pad(CT_HIT + 0.3, WHY); piano_phrase(CT_HIT + 0.5, 2, 70, 1.0, 12)
add(gm("Marimba", 85, 0.3, 100), CT_LBL, 0.3)
# why: sneaky pizz + ticks, one marimba note per step
pizz(WHY, SAFE, 0.9); pad(WHY, SAFE, 0.8)
for i, h in enumerate((W1, W2, W3)): add(gm("Marimba", [70, 73, 78][i], 0.3, 100), h, 0.3); add(gm("Melodic Tom", [45, 48, 52][i], 0.4, 100), h, 0.3)
# safe + days: light groove, marimba climbs one step per day
groove(SAFE, RARE, 0.7, snare=True); pad(SAFE, RARE, 0.9)
for h in (D2, D3): add(gm("Marimba", 78, 0.3, 100), h, 0.3)
for i, h in enumerate(DAYS): add(gm("Marimba", PEN[i] , 0.25, 90 + i * 3), h, 0.28, pan=0.2)
# rare + asthma: breakdown (no drums), piano phrase sparse, pad
pad(RARE, ADV, 1.2); piano_phrase(RARE, 3, 62, 1.5)
add(gm("Marimba", 85, 0.4, 100), RARE_HIT, 0.25); add(gm("Marimba", 78, 0.4, 100), ASTH_HIT, 0.25)
# advice: groove back in, then outro soft: pad + piano + bubble pops, light end chord
groove(ADV, OUTRO, 0.85); pad(ADV, OUTRO); piano_phrase(ADV, 2, 60)
pad(OUTRO, DUR - 0.6, 1.0); piano_phrase(OUTRO + 0.2, 1, 55, 1.0)
for h in (BUB1, BUB1 + 0.6, BUB2, BUB2 + 0.7): add(gm("Marimba", 82, 0.15, 90), h, 0.22); add(drum(76, 80), h, 0.25)
for m in (54, 66, 70, 73): add(piano(m, 1.8, 62), DUR - 2.2, 0.4)

# ---------------- mix: sidechain pad to kicks, delay, reverb, silence, glue ----------------
duck = np.ones(N)
for k0 in KICKS:
    i = int(k0 * SR); n = min(N - i, int(0.3 * SR))
    if n > 0: duck[i:i + n] = np.minimum(duck[i:i + n], 1 - 0.45 * np.exp(-np.arange(n) / SR * 12))
MIX += PAD * duck[:, None]
dl = int(0.375 * SR); MIX[dl:, 0] += MIX[:-dl, 1] * 0.12; MIX[dl:, 1] += MIX[:-dl, 0] * 0.12
def reverb(x):
    n = int(1.8 * SR); tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt * 3.2); ir = np.convolve(ir, np.ones(6) / 6, "same"); ir /= np.abs(ir).sum() ** 0.5 * 14
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x * 0.88 + np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)] * 0.32
MIX = np.stack([reverb(MIX[:, 0]), reverb(MIX[:, 1])], 1)
for a, b in SILENCES:
    i0, i1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.05 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] = 0
MIX = np.tanh(MIX / np.abs(MIX).max() * 1.6); MIX /= np.abs(MIX).max() / 0.85
fo = int(0.4 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
print("ok")
