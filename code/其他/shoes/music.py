# 《穿鞋会改造你的骨头？》BGM — "footstep funk / street stomp": E dorian, 104.08 BPM.
# Drums = synthesized stomps + GM kick / hand clap / hats; Slap Bass 1 riff; Clavinet 16th chops; brass stab ONLY on the two big hits.
# Light SFX per on-screen action: sneaker squeak, pop, wood block, marimba / xylophone runs.
import sys, math, wave, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import piano, gm, drum, SR
from cues import *
_gm, _drum = gm, drum
LV = {"Slap Bass 1": 1.3, "Clavinet": 0.75, "Brass Section": 0.55, "Marimba": 0.1, "Xylophone": 0.18, "Wood Block": 0.17,
      "Vibraphone": 0.5, "Agogo": 0.33, "Orchestra Hit": 0.5}
DLV = {40: 0.55, 42: 0.6, 76: 0.17, 77: 0.17}
def gm(name, *a, **k): return _gm(name, *a, **k) * LV.get(name, 1.0)
def drum(n, *a, **k): return _drum(n, *a, **k) * DLV.get(n, 1.0)
N = int(SR * DUR); MIX = np.zeros((N, 2)); VERB = np.zeros((N, 2))
rng = np.random.default_rng(7)
S16 = BEAT / 4
def add(y, t0, g=1.0, pan=0.0, wet=0.0, human=True):
    if human: g *= 1 + rng.uniform(-0.07, 0.07); t0 += rng.uniform(-0.004, 0.004)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    MIX[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet
def st(y): return np.stack([y, y], 1)
tt_ = lambda d: np.arange(int(d * SR)) / SR
# ---------- synth one-shots ----------
def stomp(g=1.0, low=50):
    t = tt_(0.4); f = low + 100 * np.exp(-t * 30)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    nz = np.convolve(rng.standard_normal(len(t)), np.ones(24) / 24, "same") * np.exp(-t * 45) * 2.2
    return st((body + nz) * 0.7 * g)
def squeak(f0=2200, f1=3400, d=0.12):
    t = tt_(d); f = f0 + (f1 - f0) * (t / d) + 120 * np.sin(2 * np.pi * 45 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR; env = np.sin(np.pi * t / d) ** 0.7
    return st((np.sin(ph) + 0.3 * np.sin(2 * ph)) * env * 0.16)
def popfx(f0=1100, f1=320):
    t = tt_(0.09); f = f1 + (f0 - f1) * np.exp(-t * 60)
    return st(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.35)
def boing(f=200):
    t = tt_(0.5); fr = f * (1 + 0.45 * np.sin(2 * np.pi * 11 * t) * np.exp(-t * 4)) * (1 + 0.6 * t)
    return st(np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 5) * 0.3)
def sweep(t0, t1, f0, f1, g=0.1):
    t = tt_(t1 - t0); f = f0 * (f1 / f0) ** (t / (t1 - t0))
    add(st(np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / (t1 - t0)) * g), t0, human=False)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(5) / 5, "same") * (t / (t1 - t0)) ** 2.5 * 0.09; add(st(y), t0, g, human=False)
    sweep(t0, t1, 200, 1600, 0.05 * g)
def boom(t0, g=1.0, dur=0.9):
    t = tt_(dur); f = 40 + 70 * np.exp(-t * 18)
    add(st(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.5) * 0.9), t0, g, human=False)
# ---------- grid ----------
BARS = [G0 + n * BAR for n in range(8)] + [G1 + n * BAR for n in range(12)]
def bar_idx(t):
    bs = [b for b in BARS if b <= t + 1e-6]; return (BARS.index(bs[-1]) if bs else 0)
def sixteenths(t0, t1):
    out = []
    for bi, b in enumerate(BARS):
        for k in range(16):
            tt = b + k * S16
            if bi == 7 and k >= 8: continue   # the 2/4 bar 18.85-20.0
            if t0 - 1e-4 <= tt < t1 - 1e-4: out.append((tt, k, bi))
    return out
CH = [((64, 67, 71, 74), 40), ((61, 64, 67, 71), 45)]   # Em7 | A9(no root)
def chord(bi): return CH[bi % 2]
BASS_E = [(0, 0, .22), (3, 0, .1), (4, 12, .1), (6, 0, .1), (7, 10, .1), (10, 3, .1), (11, 5, .1), (12, 12, .1), (14, 7, .1), (15, 10, .08)]
BASS_A = [(0, 0, .22), (3, 0, .1), (4, 12, .1), (6, 0, .1), (7, 10, .1), (10, 4, .1), (11, 7, .1), (12, 12, .1), (14, 10, .1), (15, 7, .08)]
def drums(t0, t1, style="full", g=1.0):
    for tt, k, bi in sixteenths(t0, t1):
        if style in ("full", "open"):
            if k in (0, 10) or (k == 6 and bi % 2): add(drum(36, 110), tt, 0.8 * g)
            if k in (0, 8): add(stomp(), tt, 0.75 * g)
            if k in (4, 12): add(drum(39, 110), tt, 0.95 * g, wet=0.25); add(drum(40, 70), tt, 0.35 * g)
            if k in (7, 15): add(drum(38, 40), tt, 0.18 * g)
            if style == "open" and k in (2, 6, 10, 14): add(drum(46, 70), tt, 0.25 * g, pan=0.3)
            elif k == 14: add(drum(46, 75), tt, 0.25 * g, pan=0.3)
            else: add(drum(42, 95 if k % 2 == 0 else 55), tt, 0.3 * g, pan=0.3)
        elif style == "light":
            if k in (0, 8): add(stomp(), tt, 0.7 * g)
            if k in (4, 12): add(drum(39, 100), tt, 0.7 * g, wet=0.3)
            if k % 2 == 0: add(drum(42, 70), tt, 0.25 * g, pan=0.3)
        elif style == "scan":
            add(drum(42, 80 if k % 4 == 0 else 45), tt, 0.28 * g, pan=0.25)
            if k % 4 == 0: add(stomp(low=45), tt, 0.6 * g)
            if k % 4 == 1: add(stomp(low=55), tt + S16 * 0.3, 0.35 * g)
        elif style == "break":
            if k in (4, 12): add(drum(39, 110), tt, 0.95 * g, wet=0.35)
            if k == 15 and bi % 2: add(drum(39, 70), tt, 0.4 * g)
def bass(t0, t1, g=1.0, sparse=False):
    for tt, k, bi in sixteenths(t0, t1):
        root = chord(bi)[1]
        for pos, iv, du in (BASS_E if bi % 2 == 0 else BASS_A):
            if pos == k and (not sparse or pos in (0, 6, 10)):
                add(gm("Slap Bass 1", root + iv, du, 112 if iv == 12 else 100, release=0.04), tt, 0.55 * g)
def clavi(t0, t1, g=1.0):
    for tt, k, bi in sixteenths(t0, t1):
        if k in (2, 5, 7, 10, 13):
            for m in chord(bi)[0]: add(gm("Clavinet", m, 0.07, 95, release=0.03, decay=12), tt, 0.13 * g, pan=-0.35)
def big(t0, g=1.0):
    boom(t0, 1.1 * g, 1.2); add(drum(36, 127), t0, 1.0 * g); add(stomp(1.4), t0, 1.0 * g); add(drum(49, 120), t0, 0.6 * g, wet=0.3)
    add(drum(39, 127), t0, 0.7 * g, wet=0.3)
    for m in (52, 59, 62, 66, 67, 71): add(gm("Brass Section", m, 0.32, 122, release=0.12), t0, 0.3 * g, wet=0.35)
    for m in (52, 59, 62, 66, 67, 71): add(gm("Brass Section", m + 2, 0.12, 110, release=0.06), t0 - S16 * 1.0, 0.12 * g)
    add(gm("Slap Bass 1", 28, 0.5, 127, release=0.1), t0, 0.8 * g); add(gm("Orchestra Hit", 64, 0.6, 120), t0, 0.35 * g, wet=0.3)
def pop(t0, g=1.0, m=None, inst="Marimba"):
    add(popfx(), t0, 0.6 * g)
    if m: add(gm(inst, m, 0.25, 105), t0, 0.5 * g, wet=0.25)
def wb(t0, m=76, g=1.0): add(drum(m, 100), t0, 0.5 * g, wet=0.15)

# ---------------- arrangement ----------------
sweep(0.0, HOOK_HIT, 300, 1800, 0.08)
for k in (2, 1): add(drum(38, 70 + 20 * (2 - k)), HOOK_HIT - k * S16, 0.35)
big(HOOK_HIT)
drums(HOOK_HIT, BARS[1], "full"); bass(HOOK_HIT, BARS[1]); clavi(HOOK_HIT, BARS[1], 0.8)
for i, h in enumerate(HOOK_CLICKS): wb(h, 77); add(gm("Xylophone", [83, 86][i], 0.2, 110), h, 0.4)
# hard stop at bar 2 (2.71 s), a lone squeak, then talus scene creeps in
add(squeak(3000, 1800, 0.14), BARS[1] + BEAT * 0.5, 0.6)
drums(TALUS, EIF, "light"); bass(TALUS, EIF, 0.8, sparse=True)
for k, m in enumerate([76, 78, 79, 81, 83, 86, 88]): add(gm("Xylophone", m, 0.15, 95), TALUS_HIT + k * 0.035, 0.28)
add(gm("Vibraphone", 88, 0.8, 90), TALUS_HIT + 0.25, 0.3, wet=0.5)
for h in WEIGHT: add(stomp(1.1, 42), h, 0.42); add(drum(41, 100), h, 0.15)
pop(TAG_HIT, 1.0, 83)
# eiffel: full groove, a marimba note per strut pop
drums(EIF, REO, "full"); bass(EIF, REO); clavi(EIF, REO)
for i, h in enumerate(POPS): add(gm("Marimba", [64, 66, 67, 69, 71, 73, 74, 76, 78, 79, 81, 83][i], 0.25, 108), h, 0.55, pan=0.2 * (1 if i % 2 else -1), wet=0.2)
pop(EIF_TAGS[0], 0.8); pop(EIF_TAGS[1], 0.8)
# reorder: groove minus clavi, squeak on the force flip, xylophone climbs as each column turns
drums(REO, SCAN, "full", 0.9); bass(REO, SCAN, 0.9)
add(squeak(), FLIP, 0.9); add(squeak(2600, 3800, 0.08), FLIP + 0.12, 0.5)
for i, h in enumerate(GROUPS): add(gm("Xylophone", [76, 78, 79, 81, 83, 85, 86, 88][i], 0.2, 105), h, 0.45, pan=-0.6 + i * 0.17)
wb(GROUPS[-1], 76); pop(GROUPS[-1], 0.8)
# scan: hats + heartbeat stomps only, counting ticks, riser, then silence
drums(SCAN, SIL0, "scan", 1.35)
for tt, k, bi in sixteenths(*SHOE_CNT): add(gm("Xylophone", 91 if k % 2 else 88, 0.08, 80), tt, 0.16, pan=-0.4)
for tt, k, bi in sixteenths(*FOOT_CNT): wb(tt, 77 if k % 2 else 76, 0.55)
riser(RISERS[0][0], SIL0, 2.2)
# second big hit + full groove
big(BIG2, 1.1)
drums(BIG2, ALIVE, "full"); bass(BIG2, ALIVE); clavi(MEDIAL, ALIVE)
for i, h in enumerate(REV_TAGS): pop(h, 0.8, [79, 83][i])
for h in SHOD_HITS: add(stomp(1.2, 42), h, 0.5); add(squeak(1800, 2600, 0.1), h + 0.05, 0.35)
for i, h in enumerate(MED_HITS): pop(h, 0.8, [76, 81, 83][i])
add(gm("Vibraphone", 83, 0.6, 85), MED_HITS[1], 0.25, wet=0.5)
for i, h in enumerate(CLIMB): add(gm("Xylophone", [79, 83, 86][i], 0.2, 110), h, 0.45); wb(h, 77, 0.6)
add(squeak(3200, 1500, 0.22), SQUAT, 0.7); add(stomp(1.2, 45), SQUAT + 0.25, 0.8)
for h in SQ_BOB: pop(h, 0.6, 76)
# breakdown: bass + claps only, boing per squeeze
drums(ALIVE, ANC, "break"); bass(ALIVE, ANC, 1.0)
for i, h in enumerate(SQUEEZE): add(boing([180, 240, 200][i]), h, 0.9)
# ancient: groove back with open hats, a wood "tok" + marimba walk per footprint
drums(ANC, BAL, "open"); bass(ANC, BAL); clavi(ANC, BAL, 0.8)
for i, h in enumerate(PRINTS): wb(h, 77, 0.5); add(gm("Marimba", [64, 67, 69, 71, 74, 76, 79][i], 0.2, 100), h, 0.35, wet=0.2)
pop(FOSSIL, 0.8, 86)
# balance: lighter groove
drums(BAL, OUTRO, "light"); bass(BAL, OUTRO, 0.9)
for i, h in enumerate(BAL_DROP): pop(h, 0.9, [79, 76][i]); wb(h + 0.15, 76, 0.4)
for m in (64, 67, 71, 74): add(gm("Marimba", m, 0.4, 100), BAL_SET, 0.3, wet=0.3)
pop(BAL_TAG, 0.7, 83)
# outro: one more bar of light groove, then a clean final chord (not a big hit)
drums(OUTRO, FINAL, "light", 0.85); bass(OUTRO, FINAL, 0.85)
pop(BUB, 0.7, 81); add(squeak(2400, 3600, 0.08), WINK, 0.5); pop(WINK + 0.1, 0.5, 88)
for m in (40, 52, 59, 62, 66, 67, 71): add(piano(m, 1.4, 82), FINAL, 0.33, wet=0.35)
for m in CH[0][0]: add(gm("Clavinet", m, 0.2, 90, release=0.1, decay=6), FINAL, 0.13)
add(gm("Slap Bass 1", 40, 0.8, 110, release=0.3), FINAL, 0.6); add(drum(36, 100), FINAL, 0.7); add(stomp(), FINAL, 0.5); add(drum(49, 70), FINAL, 0.25, wet=0.4)

# ---------------- mix ----------------
def reverb(x):
    n = int(1.6 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 3.5); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
for a, b in SILENCES:
    i0, i1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.04 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] = 0
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.4); MIX /= np.abs(MIX).max() / 0.85
fo = int(0.5 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
pk=[20*np.log10(np.sqrt((MIX[int(i*SR/4):int((i+1)*SR/4)]**2).mean())+1e-9) for i in range(int(DUR*4))]
print("loudest 0.25s:", sorted([(round(v,1), i/4) for i,v in enumerate(pk)])[-6:])
print("ok BPM %.2f" % BPM)
