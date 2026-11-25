# 《9900万年前，蜥蜴就会断尾逃命？》BGM — "surf-rock chase + 8-bit": E minor (harmonic, D# on the B chord), 146.9 BPM.
# Tremolo-picked clean guitar lead with spring reverb, walking pick bass, surf drums (snare push / floor-tom gallop),
# slide-whistle wiggles, square-wave 8-bit blips, celeste + music box + heartbeat for the amber mystery.
# Two big hits only (HOOK_HIT 0.4 s = bar 0, BIG 20.0 s = bar 12); the rest are light pops / blips.
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import piano, gm as _gm, drum as _drum, SR
from cues import *
# per-preset level (measured peaks: Clean Guitar 2.7, Marimba 7.6, Wood Block 4.8, Xylophone 4.1, Taiko 3.9 ... target ~0.8)
LV = {"Clean Guitar": 0.3, "Overdrive Guitar": 0.9, "Distortion Guitar": 0.55, "Muted Guitar": 0.2, "Pick Bass": 0.7,
      "Celeste": 1.4, "Music Box": 0.9, "Marimba": 0.11, "Xylophone": 0.19, "Glockenspiel": 1.0, "Wood Block": 0.17,
      "Pizzicato Strings": 1.0, "Timpani": 0.8, "Taiko Drum": 0.2}
DLV = {40: 0.55, 42: 0.6, 76: 0.17, 77: 0.17, 41: 0.17, 43: 0.17}
@functools.lru_cache(maxsize=None)
def gm(name, m, dur=0.5, vel=100, release=0.3, decay=None): return _gm(name, m, dur, vel, release=release, decay=decay) * LV.get(name, 1.0)
@functools.lru_cache(maxsize=None)
def drum(n, vel=100): return _drum(n, vel) * DLV.get(n, 1.0)
N = int(SR * DUR); MIX = np.zeros((N, 2)); VERB = np.zeros((N, 2)); SPRING = np.zeros((N, 2))
rng = np.random.default_rng(7)
def add(y, t0, g=1.0, pan=0.0, wet=0.0, spring=0.0, human=True):
    if human: g *= 1 + rng.uniform(-0.06, 0.06); t0 += rng.uniform(-0.004, 0.004)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    MIX[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet
    if spring: SPRING[i:i + len(y)] += y * spring
def mono(y): return np.stack([y, y], 1)
# ---------------- harmony ----------------
CH = [("Em", 40, (64, 67, 71)), ("C", 36, (64, 67, 72)), ("D", 38, (66, 69, 74)), ("B", 35, (63, 66, 71))]
def bar_of(t): return int(math.floor((t - G0) / BAR + 1e-6))
def chord(t): return CH[bar_of(t) % 4]
def beats(t0, t1, sub=1):
    k0 = math.ceil((t0 - G0) / (BEAT / sub) - 1e-6); out = []
    while True:
        tt = G0 + k0 * BEAT / sub
        if tt >= t1 - 1e-6: break
        if tt >= -1e-6: out.append((tt, k0 % (4 * sub)))
        k0 += 1
    return out
# ---------------- synths ----------------
def square(f, dur, g=0.12, duty=0.5, f1=None):
    n = int(dur * SR); tt = np.arange(n) / SR
    ff = f if f1 is None else f * (f1 / f) ** (tt / dur)
    ph = np.cumsum(np.full(n, 1.0) * ff) / SR % 1
    y = np.where(ph < duty, 1.0, -1.0) * g * np.minimum(1, (dur - tt) / 0.02) * np.minimum(1, tt / 0.003)
    return mono(y)
def blip(t0, notes, step=0.06, g=1.0, dur=0.07):
    for k, m in enumerate(notes): add(square(440 * 2 ** ((m - 69) / 12), dur, 0.08 * g, 0.25), t0 + k * step, pan=0.15, wet=0.15, human=False)
def whistle(t0, path, dur, g=1.0):   # slide whistle: piecewise glide over freq path (Hz)
    n = int(dur * SR); tt = np.arange(n) / SR
    f = np.interp(tt, np.linspace(0, dur, len(path)), path) * (1 + 0.012 * np.sin(2 * np.pi * 6 * tt))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.25 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    env = np.minimum(1, tt / 0.03) * np.minimum(1, (dur - tt) / 0.06)
    add(mono(y * env * 0.12 * g), t0, wet=0.3, human=False)
def boom(t0, g=1.0, dur=1.0):
    tt = np.arange(int(dur * SR)) / SR; f = 38 + 80 * np.exp(-tt * 16)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.2) * 0.9), t0, g, human=False)
def thump(t0, g=1.0, f0=55):
    tt = np.arange(int(0.25 * SR)) / SR; f = f0 + 30 * np.exp(-tt * 30)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14) * 0.7), t0, g, human=False)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(4) / 4, "same") * (tt / (t1 - t0)) ** 2.5 * 0.07; add(mono(y), t0, g, human=False)
# ---------------- parts ----------------
def drums(t0, t1, style="surf", g=1.0):
    for tt, k in beats(t0, t1, 2):   # 8th-note grid, k = 0..7
        if style in ("surf", "hot"):
            if k in (0, 4, 5): add(drum(36, 110), tt, 0.75 * g)
            if k in (2, 6): add(drum(38, 105), tt, 0.5 * g, wet=0.15); add(drum(40, 70), tt, 0.25 * g)
            if k == 7: add(drum(38, 55), tt, 0.18 * g)   # ghost push
            add(drum(42, 80 if k % 2 == 0 else 60), tt, 0.25 * g, pan=0.3)
            if style == "hot":
                for j in range(2): add(drum(41 if (k + j) % 2 else 43, 95), tt + j * BEAT / 4, 0.32 * g, pan=-0.25)
        elif style == "light":
            if k in (0, 4): add(drum(36, 95), tt, 0.55 * g)
            add(drum(42, 70 if k % 2 == 0 else 50), tt, 0.22 * g, pan=0.3)
            if k in (2, 6): add(drum(37, 80), tt, 0.25 * g)   # rimshot
        elif style == "hats":
            add(drum(42, 70 if k % 2 == 0 else 50), tt, 0.22 * g, pan=0.3)
            if k in (2, 6): add(drum(39, 80), tt, 0.22 * g)
def bass(t0, t1, g=1.0, eighth=False):
    for tt, k in beats(t0, t1):
        _, r, _ = chord(tt + 0.01); nr = chord(tt + BAR - k * BEAT + 0.01)[1]
        m = [r, r + (3 if r == 40 else 4), r + 7, nr + 1][k]
        add(gm("Pick Bass", m, BEAT * 0.8, 105, 0.05), tt, 0.85 * g)
        if eighth: add(gm("Pick Bass", m + (12 if k % 2 else 0), BEAT * 0.4, 85, 0.04), tt + BEAT / 2, 0.55 * g)
MEL = [[(0, 76, 1), (1, 79, .5), (1.5, 78, .5), (2, 76, 1), (3, 71, 1)],
       [(0, 72, 1), (1, 76, .5), (1.5, 79, .5), (2, 76, 1), (3, 72, .5), (3.5, 74, .5)],
       [(0, 74, 1), (1, 78, .5), (1.5, 81, .5), (2, 79, 1), (3, 78, 1)],
       [(0, 75, 1.5), (1.5, 78, .5), (2, 83, 1), (3, 71, 1)]]
MEL_B = [[(0, 71, 2), (2, 67, 2)], [(0, 72, 2), (2, 76, 2)], [(0, 74, 2), (2, 78, 2)], [(0, 75, 2), (2, 71, 2)]]
def trem(t0, m, dur, g=1.0, inst="Clean Guitar", vel=100, oct=0):
    n = max(1, int(round(dur / (BEAT / 4))))   # 16th-note tremolo picking
    for j in range(n):
        acc = 1.0 if j == 0 else (0.8 if j % 2 == 0 else 0.68)
        add(gm(inst, m + oct, BEAT / 4 * 0.9, vel, 0.04), t0 + j * BEAT / 4, 0.42 * g * acc, pan=-0.1, spring=0.5, wet=0.1)
def lead(t0, t1, g=1.0, mel=MEL, inst="Clean Guitar", oct=0):
    b0 = bar_of(t0 + 0.01)
    for b in range(b0, bar_of(t1 - 0.01) + 1):
        tb = G0 + b * BAR
        for pos, m, du in mel[b % 4]:
            ts = tb + pos * BEAT
            if t0 - 0.01 <= ts < t1 - 0.05: trem(ts, m, min(du * BEAT, t1 - ts), g, inst, oct=oct)
def chug(t0, t1, g=1.0, offbeat=False):
    for tt, k in beats(t0, t1, 2):
        if offbeat and k % 2 == 0: continue
        _, r, v = chord(tt + 0.01)
        for m in (r + 12, r + 19): add(gm("Muted Guitar", m, BEAT * 0.35, 95, 0.03), tt, 0.3 * g, pan=0.35, spring=0.2)
def stab(t0, g=1.0, root=40):
    for m in (root, root + 7, root + 12, root + 19): add(gm("Distortion Guitar", m, 0.9, 120, 0.25), t0, 0.35 * g, pan=0.2, wet=0.25)
def pop(t0, m=84, g=1.0, inst="Marimba"): add(gm(inst, m, 0.3, 105), t0, 0.5 * g, wet=0.25)
def wood(t0, hi=True, g=1.0): add(drum(76 if hi else 77, 100), t0, 0.5 * g)
def big(t0, g=1.0):
    boom(t0, 1.2 * g, 1.3); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 127), t0, 0.7 * g, wet=0.35); add(drum(57, 110), t0, 0.4 * g, pan=0.4)
    stab(t0, 1.6 * g); add(gm("Taiko Drum", 41, 1.0, 127), t0, 0.8 * g, wet=0.3)
def snareroll(t0, t1, g=1.0):
    n = int((t1 - t0) / 0.045)
    for k in range(n): add(drum(38, 50 + int(70 * k / n)), t0 + k * 0.045, 0.35 * g * (0.25 + 0.75 * k / n), human=False)
def wiggle(t0, g=1.0, base=900):   # slide-whistle "wee-oo-wee" for the twitching tail
    whistle(t0, [base, base * 1.6, base * 0.9, base * 1.5, base * 0.8], 0.45, g)
def musicbox(t0, t1, g=1.0):
    for tt, k in beats(t0, t1, 2):
        _, _, v = chord(tt + 0.01); seq = [v[0], v[1], v[2], v[1] + 12, v[2] + 12, v[1] + 12, v[2], v[1]]
        add(gm("Music Box", seq[k] + 12, 0.4, 85, 0.2), tt, 0.35 * g, pan=0.3 * (1 if k % 2 else -1), wet=0.4)
CEL = [(0, 76), (1.5, 79), (3, 83), (4, 81), (5.5, 78), (7, 75)]
def celeste(t0, t1, g=1.0):
    b0 = bar_of(t0 + 0.01)
    for b in range(b0, bar_of(t1 - 0.01) + 1, 2):
        tb = G0 + b * BAR
        for pos, m in CEL:
            ts = tb + pos * BEAT
            if t0 <= ts < t1 - 0.1: add(gm("Celeste", m, 0.8, 95, 0.3), ts, 0.45 * g, wet=0.5)
def heartbeat(t0, t1, g0=0.4, g1=1.0):
    for tt, k in beats(t0, t1):
        if k % 2 == 0:
            gg = lerp_(g0, g1, (tt - t0) / (t1 - t0)); thump(tt, gg); thump(tt + 0.17, gg * 0.7, 48)
def lerp_(a, b, k): return a + (b - a) * max(0, min(1, k))
def pizz(t0, t1, g=1.0):
    line = [64, 67, 69, 70, 71, 70, 69, 67]
    for tt, k in beats(t0, t1, 2):
        if k % 2 == 0 or k == 7: add(gm("Pizzicato Strings", line[k] + (0 if bar_of(tt) % 2 == 0 else -5), 0.25, 95), tt, 0.5 * g, pan=-0.2, wet=0.2)

# ---------------- arrangement ----------------
# 0 - 0.4 pickup: snare roll + falling guitar gliss into hit 1
snareroll(0.0, HOOK_HIT, 0.8)
for j, m in enumerate([83, 81, 79, 78, 76, 74, 71]): add(gm("Clean Guitar", m, 0.06, 100, 0.03), 0.02 + j * 0.05, 0.35, spring=0.5)
big(HOOK_HIT)
drums(HOOK_HIT + 0.01, TWIST, "surf"); bass(HOOK_HIT, TWIST); lead(HOOK_HIT, TWIST); chug(HOOK_HIT, TWIST, 0.8)
for h in WIGS0: wiggle(h, 0.8, 1000)
blip(SMUG, [88, 91, 95], 0.05, 0.9)
# 3.5 - 7.5 twist: light kit + bass walk, slide whistles on wiggles, sneaky muted skank
drums(TWIST, Q, "light"); bass(TWIST, Q, 0.9); chug(TWIST, Q, 0.9, offbeat=True)
for h in WIGS: wiggle(h, 1.0, 850)
blip(HUH, [76, 81], 0.09, 1.0, 0.09)
for k in range(6): add(gm("Pizzicato Strings", [71, 72, 74, 76, 78, 79][k], 0.15, 100), SNEAK + k * BEAT / 2, 0.45, pan=0.3)
# 7.5 - 11.5 question: drums out, 8-bit rewind arps + wood block ticks
add(gm("Glockenspiel", 88, 0.6, 110), QMARK, 0.45, wet=0.4); blip(QMARK, [83, 86, 90], 0.07, 1.0)
for tt, k in beats(Q, AMBER - 0.2, 4):
    _, _, v = chord(tt + 0.01); seq = [v[2] + 12, v[1] + 12, v[0] + 12, v[2]]
    add(square(440 * 2 ** ((seq[k % 4] - 69) / 12), 0.08, 0.1, 0.25), tt, pan=-0.2 if k % 2 else 0.2, wet=0.1, human=False)
for tt, k in beats(Q, AMBER - 0.2):
    _, r, _ = chord(tt + 0.01); add(gm("Pick Bass", r, BEAT * 0.6, 95, 0.05), tt, 1.0) if k in (0, 2) else None
for h in ROLL: wood(h, True, 0.9); add(square(900, 0.25, 0.05, 0.5, 300), h + 0.05, human=False)
for tt, k in beats(Q + 0.3, AMBER - 0.2, 2):
    if k % 2 == 1: add(drum(42, 60), tt, 0.3, pan=0.3)
# 11.5 - 19.5 amber mystery: celeste + music box + growing heartbeat
add(gm("Glockenspiel", 76, 1.0, 110), AMBER_HIT, 0.4, wet=0.5)
for j, m in enumerate([64, 71, 76, 79, 83, 88]): add(gm("Celeste", m, 0.6, 100, 0.3), AMBER_HIT + j * 0.05, 0.4, wet=0.5)
musicbox(AMBER_HIT, SIL0 - 0.9); celeste(AMBER_HIT + 0.3, TWIG + 0.2)
heartbeat(AMBER_HIT, SIL0 - 0.2, 0.35, 1.0)
pop(FINGER + 0.2, 79)
for j in range(12): add(gm("Xylophone", 64 + [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19][j], 0.12, 90), AMBER_HIT + 0.4 + j * (RULER - AMBER_HIT - 0.45) / 12, 0.3, human=False)
pop(RULER, 88); add(gm("Glockenspiel", 88, 0.5, 110), RULER, 0.4, wet=0.4)
whistle(MAG - 0.4, [400, 700], 0.4, 0.5)
for j, m in enumerate([76, 79, 83, 86, 88, 91]): add(gm("Music Box", m, 0.5, 100, 0.2), SCALES + j * 0.06, 0.45, wet=0.4)
blip(SCALES + 0.35, [88, 95], 0.08, 0.9)
whistle(JUMP, [500, 1700], 0.3, 1.1); pop(JUMP + 0.02, 84); wood(JUMP + 0.15, False, 0.7)
riser(RISERS[0][0], SIL0); snareroll(RISERS[0][0] + 0.2, SIL0, 0.7)
# 20.0 hit 2, then full surf groove (lead + overdrive octave double)
big(BIG, 1.1)
drums(BIG + 0.01, FLOWER, "surf"); bass(BIG, FLOWER); lead(BIG, FLOWER); lead(BIG, FLOWER, 0.5, inst="Overdrive Guitar", oct=-12); chug(BIG, FLOWER, 0.7)
blip(SCAN, [81, 88, 81, 88], 0.07, 1.0); blip(TAIL3D, [76, 79, 83, 88, 91], 0.05, 1.0)
# 24 - 28.5 petals: light kit, sustained tremolo counter-line, marimba per petal
drums(FLOWER, CLEAN, "light"); bass(FLOWER, CLEAN); lead(FLOWER, CLEAN, 0.8, MEL_B)
for j, h in enumerate(PETALS): pop(h, [76, 79, 81, 83, 86, 88][j], 0.9)
pop(MODERN + 0.2, 83, 0.9, "Xylophone"); blip(MATCH, [88, 88, 95], 0.09, 1.0, 0.08)
# 28.5 - 32.5 clean vs torn: surf groove, 8-bit correct / buzzer, guitar run on SELF
drums(CLEAN, OLD, "surf", 0.9); bass(CLEAN, OLD); lead(CLEAN, OLD, 0.9); chug(CLEAN, OLD, 0.6)
blip(TICK, [88, 95], 0.08, 1.1, 0.12)
add(square(110, 0.18, 0.07, 0.5), CROSS, human=False); add(square(98, 0.25, 0.07, 0.5), CROSS + 0.2, human=False)
for j, m in enumerate([88, 86, 83, 81, 79, 76, 74, 71]): add(gm("Clean Guitar", m, 0.06, 105, 0.03), SELF + j * BEAT / 4, 0.38, spring=0.5)
# 32.5 - 36.5 breakdown: no kick, bass + hats + offbeat skank; level-up on UPG
drums(OLD, MYST, "hats"); bass(OLD, MYST, 0.9); chug(OLD, MYST, 1.0, offbeat=True)
wood(OLD_HIT, True); add(gm("Pizzicato Strings", 52, 0.4, 110), OLD_LAB, 0.6); add(gm("Pizzicato Strings", 47, 0.5, 110), OLD_LAB + 0.2, 0.6)
blip(UPG, [76, 80, 83, 88, 92, 95], 0.045, 1.1); add(gm("Glockenspiel", 88, 0.6, 110), UPG + 0.3, 0.4, wet=0.4)
# 36.5 - 41 mystery: pizz sneak + slowing tick-tock, no drums
pizz(MYST, NOW - 0.3, 1.4)
tk = MYST + 0.1; gap = 0.25; hi = True
while tk < NOW - 0.3: wood(tk, hi, 0.75); hi = not hi; tk += gap; gap *= 1.045
for j, h in enumerate(CARDS): pop(h, [79, 83, 86][j], 0.9)
add(gm("Timpani", 40, 0.8, 100), MYST_HIT, 0.6, wet=0.4); add(gm("Celeste", 83, 0.8, 100), MYST_HIT + 0.1, 0.4, wet=0.5); add(gm("Celeste", 82, 0.8, 100), MYST_HIT + 0.35, 0.4, wet=0.5)
snareroll(NOW - 0.45, NOW, 0.6)
# 41 - 44 hottest: gallop toms, 8th bass, lead + overdrive double, light power stabs on downbeats
drums(NOW, OUTRO, "hot", 0.9); bass(NOW, OUTRO, 0.9, eighth=True); lead(NOW, OUTRO, 0.9); lead(NOW, OUTRO, 0.4, inst="Overdrive Guitar", oct=-12)
for tt, k in beats(NOW, OUTRO):
    if k == 0: stab(tt, 0.3, chord(tt + 0.01)[1] + (12 if chord(tt + 0.01)[1] < 38 else 0))
pop(NOW_HIT, 84, 0.8); wiggle(FLICK, 0.9, 950); wiggle(FLICK + 0.12, 0.6, 1300); add(drum(49, 90), YEARS, 0.3, wet=0.3)
# 44 - 46 outro: tremolo final note, strummed Em, blips on bubbles
trem(OUTRO, 76, BEAT * 2, 0.8); trem(OUTRO + BEAT * 2, 71, BEAT * 2, 0.7)
add(drum(36, 100), OUTRO, 0.6); add(drum(42, 70), OUTRO + BEAT, 0.2)
blip(BUBS[0], [88, 92, 95], 0.05, 0.8); pop(BUBS[1], 88, 0.8); add(drum(57, 80), BUBS[2], 0.25, wet=0.4)
for j, m in enumerate([40, 47, 52, 55, 59, 64]): add(gm("Clean Guitar", m, 1.6, 95, 0.4), BUBS[2] + j * 0.025, 0.3, spring=0.6, wet=0.3)
add(gm("Pick Bass", 40, 1.2, 100, 0.3), BUBS[2], 0.8)

# ---------------- mix ----------------
def conv(x, ir):
    sz = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
def hall_ir():
    n = int(1.8 * SR); tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt * 3.2); ir = np.convolve(ir, np.ones(8) / 8, "same"); return ir / (np.abs(ir).sum() ** 0.5 * 10)
def spring_ir():   # drippy spring: decaying noise + dense echo taps every 33 ms with a metallic ring
    n = int(1.6 * SR); tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt * 4.0) * 0.6
    for k in range(1, 40): i = int(k * 0.033 * SR); ir[i:i + 40] += np.hanning(40) * 0.9 ** k * 3
    ir *= 1 + 0.5 * np.sin(2 * np.pi * 2400 * tt)
    return ir / (np.abs(ir).sum() ** 0.5 * 9)
h, s = hall_ir(), spring_ir()
MIX += np.stack([conv(VERB[:, 0], h), conv(VERB[:, 1], h)], 1) * 0.5
MIX += np.stack([conv(SPRING[:, 0], s), conv(SPRING[:, 1], s * 0.95)], 1) * 0.55
for a, b in SILENCES:
    i0, i1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.04 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] = 0
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.6); MIX /= np.abs(MIX).max() / 0.88
fo = int(0.5 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * math.log10(max(1e-6, float(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean())))) for i in range(0, int(DUR), 2)]
print("rms/2s dB:", " ".join(f"{i*2}:{v:.0f}" for i, v in enumerate(r)))
print("ok")
