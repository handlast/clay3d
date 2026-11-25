# 《云南长出“菌中霸王龙”？》BGM — "jungle giant march": D minor pentatonic, 98 BPM.
# Taiko + timpani groove, bouncy tuba "giant steps", pan-flute melody (Yunnan colour), dulcimer/koto arps, marimba & agogo pops.
# Two big hits only (HOOK_HIT, FAM_HIT); the asteroid gets a timpani roll + low boom, not a full hit.
import sys, math, wave, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import piano, gm, drum, SR
from cues import *
_gm = gm
LV = {"Taiko Drum": 0.2, "Marimba": 0.11, "Koto": 0.2, "Agogo": 0.35, "Melodic Tom": 0.15, "Orchestra Hit": 0.5}
def gm(name, *a, **k): return _gm(name, *a, **k) * LV.get(name, 1.0)
N = int(SR * DUR); MIX = np.zeros((N, 2)); VERB = np.zeros((N, 2))
rng = np.random.default_rng(5)
def add(y, t0, g=1.0, pan=0.0, wet=0.0, human=True):
    if human: g *= 1 + rng.uniform(-0.08, 0.08); t0 += rng.uniform(-0.005, 0.005)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    MIX[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet
# Dm | Bb | C | Am   (one chord per bar)
CH = [("Dm", 38, (62, 65, 69)), ("Bb", 34, (62, 65, 70)), ("C", 36, (60, 64, 67)), ("Am", 33, (60, 64, 69))]
def bar_of(t): return int(math.floor((t - G0) / BAR + 1e-6))
def chord(t): return CH[bar_of(t) % 4]
def bars(t0, t1):
    b0 = bar_of(t0 + 0.01); b1 = bar_of(t1 - 0.01)
    return [G0 + b * BAR for b in range(b0, b1 + 1) if t0 - 0.01 <= G0 + b * BAR < t1 - 0.01]
def boom(t0, g=1.0, dur=0.9):
    tt = np.arange(int(dur * SR)) / SR; f = 40 + 70 * np.exp(-tt * 18)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.5) * 0.9; add(np.stack([y, y], 1), t0, g, human=False)

def drums(t0, t1, style="march", g=1.0):
    for tb in bars(t0, t1):
        for i in range(4):
            tt = tb + i * BEAT
            if style == "march":
                if i in (0, 2): add(gm("Taiko Drum", 45, 0.6, 115), tt, 0.7 * g, wet=0.3)
                if i in (1, 3): add(drum(38, 90), tt, 0.4 * g, wet=0.2); add(drum(39, 80), tt, 0.25 * g)
                add(drum(42, 70), tt, 0.22 * g, pan=0.3); add(drum(42, 50), tt + BEAT / 2, 0.16 * g, pan=0.3)
                if i == 3: add(gm("Taiko Drum", 50, 0.3, 90), tt + BEAT * 0.5, 0.35 * g)
            elif style == "steps":   # giant footsteps: taiko on 1 and 3 only + shaker
                if i in (0, 2): add(gm("Taiko Drum", 43, 0.7, 110), tt, 0.75 * g, wet=0.4)
                add(drum(70, 60), tt + BEAT / 2, 0.2 * g, pan=-0.3)
            elif style == "tribal":
                add(gm("Taiko Drum", 45 if i % 2 == 0 else 50, 0.4, 105), tt, 0.55 * g)
                add(gm("Taiko Drum", 52, 0.2, 80), tt + BEAT * 0.75, 0.3 * g)
                add(drum(42, 60), tt + BEAT / 2, 0.18 * g, pan=0.3); add(gm("Agogo", 72 if i % 2 else 67, 0.2, 90), tt + BEAT / 2, 0.2 * g, pan=-0.4)
def tuba(t0, t1, g=1.0):   # bouncy root-fifth
    for tb in bars(t0, t1):
        r = chord(tb + 0.01)[1] + 12
        for pos, iv in [(0, 0), (1.5, 7), (2, 0), (3, 7)]: add(gm("Tuba", r + iv, 0.35, 105, release=0.08), tb + pos * BEAT, 0.5 * g)
def arps(t0, t1, g=1.0, inst="Dulcimer"):
    for tb in bars(t0, t1):
        _, _, v = chord(tb + 0.01); seq = [v[0], v[1], v[2], v[1] + 12, v[2] + 12, v[1] + 12, v[2], v[1]]
        for k, m in enumerate(seq): add(gm(inst, m + 12, 0.25, 85), tb + k * BEAT / 2, 0.2 * g, pan=0.3 * (1 if k % 2 else -1), wet=0.3)
MEL = [[(0, 74), (1, 77), (1.5, 79), (2, 81), (3, 79)],
       [(0, 77), (1, 74), (2, 77), (2.5, 79), (3, 77)],
       [(0, 76), (1, 72), (1.5, 74), (2, 76), (3, 79)],
       [(0, 81), (1.5, 79), (2, 76), (3, 74)]]
def flute(t0, t1, g=1.0, oct=0, inst="Pan Flute"):
    for tb in bars(t0, t1):
        for pos, m in MEL[bar_of(tb + 0.01) % 4]: add(gm(inst, m + oct, 0.5, 100, release=0.15), tb + pos * BEAT, 0.3 * g, pan=0.1, wet=0.45)
def pop(t0, m=84, g=1.0, inst="Marimba"): add(gm(inst, m, 0.3, 105), t0, 0.35 * g, wet=0.3)
def tick(t0, m): add(gm("Marimba", m, 0.2, 100), t0, 0.3); add(drum(76, 90), t0, 0.15)
def big(t0, g=1.0):
    boom(t0, 1.2 * g, 1.3); add(gm("Taiko Drum", 41, 1.0, 127), t0, 0.9 * g, wet=0.4); add(drum(49, 120), t0, 0.55 * g, wet=0.3)
    add(gm("Orchestra Hit", 62, 0.8, 120), t0, 0.5 * g, wet=0.3)
    for m in (50, 57, 62, 65, 69): add(gm("Brass Section", m, 0.7, 118, release=0.2), t0, 0.22 * g, wet=0.4)
    for m in (38, 50): add(piano(m, 1.5, 115), t0, 0.4 * g)
def roll(t0, t1, g=1.0):
    n = int((t1 - t0) / 0.05)
    for k in range(n): add(gm("Timpani", 38, 0.2, 60 + int(60 * k / n)), t0 + k * 0.05, 0.25 * g * (0.3 + 0.7 * k / n), human=False)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(5) / 5, "same") * (tt / (t1 - t0)) ** 2.5 * 0.08; add(np.stack([y, y], 1), t0, g, human=False)

# ---------------- arrangement ----------------
roll(0.0, HOOK_HIT, 0.8); big(HOOK_HIT)
drums(HOOK_HIT, SIZE, "march"); tuba(HOOK_HIT, SIZE); flute(HOOK_HIT, SIZE, 1.0, 12)
# size + scale: giant steps, tuba, marimba ticks per ruler mark, agogo per bottle
drums(SIZE - 0.05, REC, "steps"); tuba(SIZE - 0.05, REC, 0.9)
for i, h in enumerate(RTICKS): tick(h, [74, 77, 79, 81][i])
pop(CASE_HIT, 86, 0.8, "Xylophone" if False else "Marimba")
add(gm("Melodic Tom", 45, 0.5, 110), KG_HIT, 0.4); pop(KG_HIT + 0.05, 89)
for i, h in enumerate(BOTTLES): add(gm("Agogo", [67, 72, 74, 79][i], 0.2, 100), h, 0.35)
# record: march + flute, brass fanfare for the crown (light)
drums(REC - 0.05, LOOK, "march"); tuba(REC - 0.05, LOOK); flute(REC - 0.05, LOOK)
for h in RIVALS: pop(h, 79)
for k, m in enumerate([69, 74, 77, 81]): add(gm("Brass Section", m, 0.25, 100), CROWN_HIT + k * 0.08, 0.15)
# look: dulcimer arps + steps, a pop per stage
drums(LOOK - 0.05, DNA, "steps", 0.8); arps(LOOK - 0.05, DNA); tuba(LOOK - 0.05, DNA, 0.7)
for i, h in enumerate(GROW): pop(h, [81, 84, 86][i])
# DNA: koto alone, then riser, silence
arps(DNA - 0.05, SIL0 - 0.3, 1.2, "Dulcimer"); riser(RISERS[0][0], SIL0); roll(RISERS[0][0] + 0.3, SIL0, 0.6)
# new family: big hit 2, tribal groove + flute up an octave
big(FAM_HIT, 1.1)
drums(FAM_HIT, EXT, "tribal"); tuba(FAM_HIT, EXT); flute(FAM_HIT, EXT, 1.0, 12); arps(NAME - 0.05, EXT, 0.7)
for i, h in enumerate(NAME_HITS): add(gm("Koto", [74, 77, 81][i], 0.4, 110), h, 0.4, wet=0.4)
# extinction: drums out, timpani roll into impact boom, falling tom
tuba(EXT - 0.05, ROCK_HIT - 0.3, 0.6); roll(EXT + 0.3, ROCK_HIT, 0.9)
boom(ROCK_HIT, 1.0, 1.4); add(gm("Timpani", 33, 1.0, 120), ROCK_HIT, 0.5, wet=0.5); add(drum(49, 100), ROCK_HIT, 0.35, wet=0.5)
add(gm("Melodic Tom", 50, 0.4, 100), DINO_FALL - 0.15, 0.2); add(gm("Melodic Tom", 41, 0.6, 110), DINO_FALL, 0.25)
# rise: koto + flute soft, steps return, marimba run on sprout
arps(RISE - 0.05, LIFE, 1.0, "Dulcimer"); flute(RISE - 0.05, LIFE, 1.2, 0, "Shakuhachi"); drums(SPROUT_HIT, LIFE, "steps", 0.7)
for k in range(6): add(gm("Marimba", [62, 65, 67, 69, 72, 74][k], 0.2, 95), SPROUT_HIT + k * 0.08, 0.3)
pop(UP_HIT, 86)
# double life: sneaky pizz + steps, tree dies (low pizz), burst (taiko + marimba)
drums(LIFE - 0.05, GENE, "steps", 0.8); tuba(LIFE - 0.05, GENE, 0.7)
for k in range(int((TREE_DIE - LIFE) / (BEAT / 2))): add(gm("Pizzicato Strings", [62, 65][k % 2], 0.2, 90), LIFE + k * BEAT / 2, 0.3, pan=-0.3)
pop(INSIDE_HIT, 81); add(gm("Pizzicato Strings", 45, 0.4, 120), TREE_DIE, 0.5)
add(gm("Taiko Drum", 45, 0.5, 120), BURST_HIT, 0.6); pop(BURST_HIT, 86)
# genes: march + dulcimer, brass lift on "省下来长个子"
drums(GENE - 0.05, YUN, "march", 0.9); tuba(GENE - 0.05, YUN); arps(GENE - 0.05, YUN, 0.8)
pop(GENE_HIT, 79); pop(GENE_HIT + 0.3, 74)
for k, m in enumerate([69, 74, 77, 81]): add(gm("Brass Section", m, 0.25, 100), BIG_HIT2 + k * 0.07, 0.15)
# yunnan: tribal groove + flute
drums(YUN - 0.05, OUTRO, "tribal", 0.9); tuba(YUN - 0.05, OUTRO); flute(YUN - 0.05, OUTRO, 1.0, 12)
for k in range(8): add(gm("Marimba", 74 + [0, 3, 5, 7, 10, 12, 15, 17][k], 0.15, 90), YUN_HIT + k * 0.08, 0.22)
pop(YUN2_HIT, 89)
# outro: steps, flute, final chord
drums(OUTRO - 0.05, DUR - 2.4, "steps", 0.7); flute(OUTRO - 0.05, DUR - 2.2, 0.9); tuba(OUTRO - 0.05, DUR - 2.4, 0.6)
for h in BUBS: pop(h, 86, 0.7)
for m in (38, 50, 57, 62, 65, 69): add(piano(m, 2.2, 70), DUR - 2.2, 0.3, wet=0.3)
add(gm("Taiko Drum", 41, 0.8, 100), DUR - 2.2, 0.5, wet=0.5)

# ---------------- mix ----------------
def reverb(x):
    n = int(2.0 * SR); tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt * 3.0); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
for a, b in SILENCES:
    i0, i1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.05 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] = 0
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.8); MIX /= np.abs(MIX).max() / 0.85
fo = int(0.4 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
print("ok")
