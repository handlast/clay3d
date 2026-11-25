# 《FBI 的 UFO 档案》BGM — Pachelbel Canon progression (D A Bm F#m G D G A), 80 BPM, one cycle = 16 beats = 12 s.
# A true canon: voice B plays what voice A played one cycle earlier, voice C two cycles earlier; voices enter one by one,
# then a fixed drum beat + finger bass lock in as the story climbs. Three big hits only (0 s, Roswell 21 s, climax 156 s).
# Real samples: Salamander piano + GeneralUser GS (pizzicato, celeste, violin, music box, finger bass, drums, timpani).
import sys, math, wave, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import piano, gm, drum, SR
from cues2 import *
_gm, _drum = gm, drum
LV = {"Marimba": 0.12, "Melodic Tom": 0.15, "Celeste": 0.6, "Music Box": 0.5}
def gm(name, *a, **k): return _gm(name, *a, **k) * LV.get(name, 1.0)
def drum(note, *a, **k): return _drum(note, *a, **k) * (0.25 if note in (76, 77) else 1.0)
N = int(SR * DUR); MIX = np.zeros((N, 2)); KICKS = []
rng = np.random.default_rng(7)
def add(y, t0, g=1.0, pan=0.0, human=True):
    if human: g *= 1 + rng.uniform(-0.1, 0.1); t0 += rng.uniform(-0.006, 0.006)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    MIX[i:i + len(y)] += y
def kick(t0, g=1.0): add(drum(36, 110), t0, 0.9 * g); KICKS.append(t0)

GROUND = [50, 45, 47, 42, 43, 38, 43, 45]                       # D A B F# G D G A
V1 = [(i * 2, 2, m) for i, m in enumerate([78, 76, 74, 73, 71, 69, 71, 73])]
V2 = [(i, 1, m) for i, m in enumerate([74, 78, 81, 79, 78, 74, 78, 76, 74, 71, 74, 81, 79, 83, 81, 79])]
V3 = [(i * 0.5, 0.5, m) for i, m in enumerate([74, 73, 74, 62, 61, 69, 64, 66, 62, 74, 73, 71, 73, 78, 81, 83,
                                                 79, 78, 76, 79, 78, 76, 74, 73, 71, 69, 67, 66, 64, 67, 66, 64])]
CHORD = [(62, 66, 69), (61, 64, 69), (62, 66, 71), (61, 66, 69), (62, 67, 71), (62, 66, 69), (62, 67, 71), (61, 64, 69)]
ASEQ = [None, V1, V2, V3, V2, V3, V1, V2, V3, V2, V3, V1, V2, V3, V2, V3, V1, V1]   # voice A, cycle by cycle
def cyc(c): return c * CYC
def line(c, seq, inst, g, oct=0, pan=0.0, vel=70, t0=None, t1=None):
    if seq is None: return
    for b, du, m in seq:
        t = cyc(c) + b * BEAT
        if (t0 is not None and t < t0) or (t1 is not None and t >= t1): continue
        dur = du * BEAT * 0.95
        if inst == "piano": y = piano(m + oct, dur, vel + rng.integers(-6, 6))
        elif inst == "Violin": y = gm("Violin", m + oct, dur, vel + 10, attack=0.08, release=0.25)
        else: y = gm(inst, m + oct, dur, vel + 20, release=0.15)
        add(y, t, g, pan)
def ground(c, g=1.0, t0=None, t1=None, vel=60):
    for k, m in enumerate(GROUND):
        t = cyc(c) + k * 2 * BEAT
        if (t0 is not None and t < t0) or (t1 is not None and t >= t1): continue
        add(piano(m, 2 * BEAT * 0.95, vel), t, 0.5 * g); add(piano(m + 12, 2 * BEAT * 0.95, vel - 10), t, 0.3 * g)
def bass(c, g=1.0, eighth=False, t0=None, t1=None):
    for k in range(16 if not eighth else 32):
        b = k * (1 if not eighth else 0.5); t = cyc(c) + b * BEAT
        if (t0 is not None and t < t0) or (t1 is not None and t >= t1): continue
        m = GROUND[int(b // 2)] - 12 if GROUND[int(b // 2)] > 40 else GROUND[int(b // 2)]
        add(gm("Finger Bass", m + 12, BEAT * (0.9 if not eighth else 0.45), 100, release=0.06), t, 0.6 * g)
def beat(c, g=1.0, half=False, t0=None, t1=None, hats=True):
    for b in range(16):
        t = cyc(c) + b * BEAT
        if (t0 is not None and t < t0) or (t1 is not None and t >= t1): continue
        if half:
            if b % 4 == 0: kick(t, 0.8 * g)
            if b % 4 == 2: add(drum(38, 85), t, 0.4 * g)
        else:
            if b % 2 == 0: kick(t, g)
            if b % 4 == 1: kick(t + BEAT * 0.5, 0.6 * g)
            if b % 2 == 1: add(drum(38, 95), t, 0.5 * g)
        if hats:
            add(drum(42, 70), t, 0.22 * g, pan=0.3); add(drum(42, 45), t + BEAT / 2, 0.15 * g, pan=0.3)
            if rng.random() < 0.12: add(drum(42, 40), t + BEAT * 0.75, 0.1 * g, pan=0.3)
def tick(c, g=1.0, t0=None, t1=None):   # clock / teletype tick on 8ths
    for k in range(32):
        t = cyc(c) + k * BEAT / 2
        if (t0 is not None and t < t0) or (t1 is not None and t >= t1): continue
        add(drum(42, 40), t, 0.1 * g, pan=0.35)
def big(t0, g=1.0):
    kick(t0, 1.2 * g); add(drum(49, 120), t0, 0.7 * g); add(gm("Timpani", 38, 1.6, 127, release=0.5), t0, 0.9 * g)
    for m in (26, 38, 50): add(piano(m, 1.8, 115), t0, 0.5 * g)
    for m in (62, 66, 69, 74): add(piano(m, 1.4, 100), t0, 0.3 * g)
def riser(t1, dur=2.0, g=1.0):
    n = int(dur * SR); s = np.arange(n) / SR
    x = np.convolve(rng.standard_normal(n), np.ones(4) / 4, "same") * (s / dur) ** 2.5 * 0.08
    add(np.stack([x, x], 1), t1 - dur, g, human=False)
def sparkle(t0, notes, step=0.09, g=0.4):
    for i, m in enumerate(notes): add(gm("Celeste", m, 0.3, 90), t0 + i * step, g, pan=0.4 * math.sin(i))

# ---------------- arrangement v2 (10-s cycles) ----------------
P, PI, CE = "piano", "Pizzicato Strings", "Celeste"
def verdict(t0):   # stamp: low tom + soft kick + woodblock
    kick(t0, 0.8); add(gm("Melodic Tom", 38, 0.5, 120), t0, 0.5); add(drum(76, 110), t0 + 0.12, 0.4)
big(HIT0); ground(0, 0.8, t0=2.0); tick(0, 0.8, t0=3.0); sparkle(3.0, [81, 86, 90, 93]); sparkle(6.5, [93, 90, 86, 81, 78])
for i in range(5): add(gm("Marimba", [74, 78, 81, 86, 90][i], 0.3, 100), 7.0 + i * 0.5, 0.3)
ground(1); line(1, ASEQ[1], PI, 0.55, pan=-0.3, t1=ROS - 0.2); riser(ROS, 1.0); big(ROS, 0.9); line(1, ASEQ[1], PI, 0.55, pan=-0.3, t0=ROS + 1.2)
for k in range(16): add(drum(76, 90), 16.6 + k * 0.17, 0.3, pan=0.3)
ground(2); line(2, ASEQ[2], PI, 0.5, pan=-0.3); line(2, ASEQ[1], P, 0.5, pan=0.15); tick(2, 0.8)
ground(3); line(3, ASEQ[3], PI, 0.45, pan=-0.3); line(3, ASEQ[2], P, 0.45, pan=0.15); tick(3, 0.9)
for c in (4, 5):
    ground(c, 0.75); line(c, ASEQ[c], PI, 0.45, pan=-0.3); line(c, ASEQ[c - 1], P, 0.42, pan=0.15); line(c, ASEQ[c - 2], CE, 0.5, 12, pan=0.35); tick(c, 0.9)
    if c == 5: bass(c, 0.8)
for h in (43.2, 47.2, 54.2): add(gm("Marimba", 81, 0.3, 100), h, 0.3); add(gm("Marimba", 85, 0.3, 100), h + 0.15, 0.3)
ground(6, 0.75); bass(6, 0.8, t1=69.0); line(6, ASEQ[6], PI, 0.45, pan=-0.3, t1=69.0); line(6, ASEQ[5], P, 0.42, pan=0.15, t1=69.0); line(6, ASEQ[4], CE, 0.45, 12, pan=0.35, t1=69.0)
add(drum(77, 110), TOILET, 0.6); add(gm("Melodic Tom", 50, 0.4, 110), TOILET + 0.12, 0.4); add(gm("Melodic Tom", 43, 0.5, 110), TOILET + 0.3, 0.4)
for c in (7, 8):
    ground(c, 0.7); bass(c, 0.9); beat(c, 0.8 if c == 7 else 0.9, half=True)
    line(c, ASEQ[c], PI, 0.45, pan=-0.3); line(c, ASEQ[c - 1], P, 0.45, pan=0.15); line(c, ASEQ[c - 2], CE, 0.45, 12, pan=0.35)
ground(9, 0.8, t1=92.5); bass(9, 0.8, t1=91.5); beat(9, 0.9, half=True, t1=91.5); line(9, ASEQ[8], P, 0.45, pan=0.15, t1=91.5)
ground(9, 0.8, t0=94.0)
for b in range(0, 16, 2):
    if cyc(9) + b * BEAT >= 94: kick(cyc(9) + b * BEAT, 0.5); kick(cyc(9) + b * BEAT + 0.16, 0.3)
ground(10, 0.8); line(10, ASEQ[10], P, 0.45, pan=0.15); line(10, ASEQ[9], CE, 0.45, 12, pan=0.35)
for b in range(0, 16, 2): kick(cyc(10) + b * BEAT, 0.6); kick(cyc(10) + b * BEAT + 0.16, 0.35)
for i, h in enumerate(STAR_OUT): add(gm("Celeste", [93, 90, 88, 86, 85, 83, 81, 78][i], 0.25, 80), h, 0.35)
riser(CLIMAX, 2.0, 1.2); big(CLIMAX, 1.2)
for c in (11, 12):
    ground(c, 0.7); bass(c, 1.0, eighth=True); beat(c, 1.0)
    line(c, ASEQ[c], PI, 0.45, pan=-0.3); line(c, ASEQ[c - 1], P, 0.5, pan=0.15); line(c, ASEQ[c - 2], CE, 0.45, 12, pan=0.35)
    line(c, V1, "Violin", 0.35, 12 if c == 12 else 0, pan=-0.1, vel=85); line(c, V3, "Music Box", 0.4, 12, pan=0.45)
add(gm("Square Lead", 93, 0.12, 70, release=0.05), THERM + 0.3, 0.12); add(gm("Square Lead", 93, 0.12, 70, release=0.05), THERM + 0.5, 0.12)
add(drum(49, 100), NEWSHIT, 0.4); add(drum(57, 100), REVEAL, 0.45)
ground(13, 0.8); bass(13, 0.8); beat(13, 0.7, half=True, t1=137.0); beat(13, 0.85, t0=137.0)
line(13, ASEQ[13], PI, 0.4, pan=-0.3); line(13, ASEQ[12], P, 0.5, pan=0.15); line(13, V1, "Violin", 0.3, 12, pan=-0.1, vel=80, t0=137.0)
ground(14, 0.8, t1=147.5); bass(14, 0.6, t1=145.0); beat(14, 0.6, half=True, t1=145.0); line(14, V1, P, 0.5, pan=0.15, t1=147.5); line(14, V2, CE, 0.35, 12, pan=0.35, t1=145)
for m in (38, 50, 62, 66, 69, 74, 78): add(piano(m, 3.0, 70), 147.5, 0.35)
for v in VERDICTS: verdict(v)
SILENCES = []
# ---------------- mix: sidechain-ish duck on kicks, delay, reverb, silences, glue ----------------
duck = np.ones(N)
for k0 in KICKS:
    i = int(k0 * SR); n = min(N - i, int(0.25 * SR))
    if n > 0: duck[i:i + n] = np.minimum(duck[i:i + n], 1 - 0.18 * np.exp(-np.arange(n) / SR * 14))
MIX *= duck[:, None]
dl = int(BEAT * 0.75 * SR); MIX[dl:, 0] += MIX[:-dl, 1] * 0.12; MIX[dl:, 1] += MIX[:-dl, 0] * 0.12
def reverb(x):
    n = int(2.0 * SR); tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt * 3.0); ir = np.convolve(ir, np.ones(6) / 6, "same"); ir /= np.abs(ir).sum() ** 0.5 * 14
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x * 0.86 + np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)] * 0.34
MIX = np.stack([reverb(MIX[:, 0]), reverb(MIX[:, 1])], 1)
for a, b in SILENCES:
    i0, i1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.08 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] = 0
MIX = np.tanh(MIX / np.abs(MIX).max() * 1.6); MIX /= np.abs(MIX).max() / 0.85
fo = int(1.0 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("bgm2.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
print("ok")
