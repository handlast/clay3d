# 《吃了见手青，会看见小人？》BGM — reggae (one drop / steppers), ~85.7 BPM, bars start at G0 so both big hits (0.4, 20.0) land on a downbeat.
# Real samples: GeneralUser GS (Clean Guitar skank, Tonewheel Organ bubble, Finger Bass, Harmonica melody, Brass stabs, drums) + Salamander piano.
# Two big hits only (HOOK_HIT, SOUP_HIT); everything else light: rimshot, woodblock, marimba pops, dub echo, one dub siren.
import sys, math, wave, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import piano, gm, drum, SR
from cues import *
_gm, _drum = gm, drum
LV = {"Marimba": 0.12, "Melodic Tom": 0.15}
def gm(name, *a, **k): return _gm(name, *a, **k) * LV.get(name, 1.0)
def drum(note, *a, **k): return _drum(note, *a, **k) * (0.25 if note in (76, 77) else 1.0)
N = int(SR * DUR); MIX = np.zeros((N, 2)); DUB = np.zeros((N, 2)); KICKS = []
rng = np.random.default_rng(7)
SW = 0.38   # swung offbeat position inside a 0.7 s beat (straight = 0.35)
def add(y, t0, g=1.0, pan=0.0, bus=None, human=True):
    if human: g *= 1 + rng.uniform(-0.1, 0.1); t0 += rng.uniform(-0.006, 0.006)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    (MIX if bus is None else bus)[i:i + len(y)] += y
def kick(t0, g=1.0): add(drum(36, 112), t0, 0.95 * g); KICKS.append(t0)

# A minor: Am | Dm | G | Em  (one chord per bar); skank voicings high, bass roots low
CH = [("Am", 45, (69, 72, 76)), ("Dm", 38, (69, 74, 77)), ("G", 43, (67, 71, 74)), ("Em", 40, (67, 71, 76))]
def bar_of(t): return int(math.floor((t - G0) / BAR + 1e-6))
def chord(t): return CH[bar_of(t) % 4]
def bars(t0, t1):
    b0 = bar_of(t0 + 0.01); b1 = bar_of(t1 - 0.01)
    return [G0 + b * BAR for b in range(b0, b1 + 1) if G0 + b * BAR >= t0 - 0.01 and G0 + b * BAR < t1 - 0.01]

def drums(t0, t1, style="drop", g=1.0, hats=True):
    for tb in bars(t0, t1):
        for i in range(4):
            tt = tb + i * BEAT
            if style == "drop" and i == 2: kick(tt, g); add(drum(37, 115), tt, 0.7 * g, bus=DUB)
            if style == "step":
                kick(tt, 0.85 * g)
                if i == 2: add(drum(38, 100), tt, 0.5 * g); add(drum(37, 110), tt, 0.4 * g, bus=DUB)
            if hats:
                add(drum(42, 80), tt, 0.28 * g, pan=0.3); add(drum(42, 60), tt + SW, 0.2 * g, pan=0.3)
                if i == 3 and rng.random() < 0.5: add(drum(46, 70), tt + SW, 0.22 * g, pan=0.3)
        if rng.random() < 0.35:   # little rim fill on the last 16ths
            for k in range(3): add(drum(37, 70 + k * 12), tb + 3 * BEAT + 0.35 + k * 0.117, 0.3 * g)
def skank(t0, t1, g=1.0):   # guitar chop on beats 2 & 4, organ bubble on every offbeat
    for tb in bars(t0, t1):
        _, _, v = chord(tb + 0.01)
        for i in (1, 3):
            for m in v: add(gm("Clean Guitar", m, 0.11, 100, release=0.04), tb + i * BEAT, 0.22 * g, pan=-0.35, bus=DUB)
            add(drum(42, 50), tb + i * BEAT, 0.08 * g)
        for i in range(4):
            m = v[0] - 12 if i % 2 == 0 else v[1] - 12
            add(gm("Tonewheel Organ", m, 0.16, 85, release=0.05), tb + i * BEAT + SW, 0.18 * g, pan=0.3)
            if i % 2 == 1:
                for mm in v: add(gm("Tonewheel Organ", mm - 12, 0.12, 80, release=0.04), tb + i * BEAT, 0.08 * g, pan=0.3)
BASSLINE = [(0.0, 0, 0.55), (1.0, 0, 0.3), (1.0 + SW / BEAT, 7, 0.3), (2.0, 12, 0.5), (3.0, 10, 0.25), (3.0 + SW / BEAT, 7, 0.3)]
def bass(t0, t1, g=1.0, drop1=False):
    for tb in bars(t0, t1):
        r = chord(tb + 0.01)[1]; minor = chord(tb + 0.01)[0] in ("Am", "Dm", "Em")
        for pos, iv, dur in BASSLINE:
            if drop1 and pos == 0.0: continue
            if iv == 10 and not minor: iv = 9
            add(gm("Finger Bass", r + iv - 12 + 12, dur * BEAT * 2, 105, release=0.06), tb + pos * BEAT, 0.75 * g)
# harmonica melody (A minor pentatonic A C D E G), 2-bar phrases, 起承转合; leaps ≤ 4th, phrase ends on a chord tone
MEL = [[(0, 76), (0.5 + SW / BEAT - 0.5, 74), (1.5, 72), (2.0, 69), (3.0, 72)],
       [(0.5, 74), (1.0, 76), (2.0, 79), (2.5 + SW / BEAT - 0.5, 76), (3.5, 74)],
       [(0, 72), (1.0, 74), (1.5, 76), (2.0, 74), (3.0, 72), (3.5, 69)],
       [(0.5, 67), (1.0, 69), (2.0, 71), (3.0, 67)]]
def melody(t0, t1, g=1.0, oct=0, vel=92):
    for j, tb in enumerate(bars(t0, t1)):
        for pos, m in MEL[bar_of(tb + 0.01) % 4]:
            add(gm("Harmonica", m + oct, 0.5, vel, release=0.12), tb + pos * BEAT, 0.32 * g, pan=0.1, bus=DUB if pos >= 3 else None)
def stab(t0, g=1.0):
    for m in (57, 64, 69, 72, 76): add(gm("Brass Section", m, 0.35, 120, release=0.12), t0, 0.22 * g)
def big(t0, g=1.0):
    kick(t0, 1.3 * g); add(drum(49, 125), t0, 0.75 * g); add(drum(57, 110), t0 + 0.02, 0.4 * g)
    stab(t0, 1.3 * g); add(gm("Brass Section", 81, 0.5, 120), t0 + 0.35, 0.18 * g, bus=DUB)
    add(gm("Finger Bass", 33, 1.4, 127, release=0.3), t0, 1.0 * g)
    for m in (45, 57): add(piano(m, 1.4, 115), t0, 0.45 * g)
def pop(t0, m=81, g=1.0): add(gm("Marimba", m, 0.25, 100), t0, 0.3 * g); add(drum(76, 100), t0, 0.35 * g, bus=DUB)
def siren(t0, dur=1.4, g=1.0):   # classic dub siren: sine with LFO sweep
    tt = np.arange(int(dur * SR)) / SR
    f = 700 + 400 * np.sign(np.sin(2 * np.pi * 3.0 * tt)) * (tt / dur) + 300 * tt / dur
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.12 * np.minimum(1, tt * 20) * np.minimum(1, (dur - tt) * 4)
    add(np.stack([y, y * 0.8], 1), t0, g, bus=DUB)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(4) / 4, "same") * (tt / (t1 - t0)) ** 2.5 * 0.09
    add(np.stack([y, y], 1), t0, g, human=False)

# ---------------- arrangement ----------------
for i, m in enumerate([57, 60, 62, 64, 67, 69]): add(gm("Harmonica", m, 0.2, 80 + i * 6), i * 0.06, 0.25)   # pickup run into the hit
big(HOOK_HIT)
drums(HOOK_HIT, YUN, "step", 1.0); skank(HOOK_HIT, YUN); bass(HOOK_HIT, YUN)
# Yunnan + bruise: classic one drop, melody enters
drums(YUN - 0.3, MAP, "drop"); skank(YUN - 0.3, MAP); bass(YUN - 0.3, MAP, drop1=True); melody(6.0, MAP, 0.9)
add(gm("Harmonica", 81, 0.4, 100), YUN_HIT, 0.25); siren(YUN_HIT + 0.2, 1.2, 0.8)
for h in WOK_POP: pop(h, 84)
add(gm("Melodic Tom", 50, 0.4, 100), TOUCH, 0.35); pop(NAME_HIT, 88)
# map: steppers push, a pop per pin
drums(MAP - 0.3, RULER, "step", 0.9); skank(MAP - 0.3, RULER); bass(MAP - 0.3, RULER)
for i, h in enumerate(PINS): pop(h, [76, 79, 84][i])
add(gm("Harmonica", 88, 0.6, 105), FAR_HIT, 0.25)
# ruler + kinds: breakdown — bass + skank only, a marimba count-up
skank(RULER - 0.3, TABLE, 0.9); bass(RULER - 0.3, TABLE, 0.9, drop1=True)
for i in range(10): add(gm("Marimba", [69, 72, 74, 76, 79, 81, 84, 86, 88, 91][i], 0.12, 90), SIZE_HITS[1] + i * 0.07, 0.2)
pop(SIZE_HITS[0], 79); pop(KIND_HITS[0], 84); pop(KIND_HITS[1], 86)
# table: sneaky — rim + dub echo only, slide-whistle-ish fall, riser into silence
for k in range(int((SIL0 - TABLE) / BEAT)): add(drum(37, 90), TABLE + k * BEAT, 0.35, bus=DUB)
skank(TABLE - 0.3, SIL0 - 0.1, 0.6)
tt = np.arange(int(0.6 * SR)) / SR; y = np.sin(2 * np.pi * np.cumsum(1200 * np.exp(-tt * 3) + 200) / SR) * 0.12 * np.exp(-tt * 2)
add(np.stack([y, y], 1), FALL, 1.0)
riser(RISERS[0][0], SIL0)
# soup: big hit 2, steppers + melody an octave up
big(SOUP_HIT, 1.1)
drums(SOUP_HIT, ARCH, "step"); skank(SOUP_HIT, ARCH); bass(SOUP_HIT, ARCH); melody(SOUP_HIT, ARCH, 1.0, 12, 100)
for i in range(7): add(gm("Marimba", 84 + [0, 2, 4, 7, 9, 12, 14][i], 0.15, 90), SOUP_HIT + 0.55 + i * 0.11, 0.18)
pop(MOUTH_HIT, 88)
# archive + DNA: one drop, darker (no melody), dub-heavy
drums(ARCH - 0.3, LAB, "drop"); skank(ARCH - 0.3, LAB, 0.9); bass(ARCH - 0.3, LAB, drop1=True)
pop(ARCH_HIT, 76); add(gm("Melodic Tom", 43, 0.5, 110), HOF_HIT, 0.4); add(drum(76, 110), HOF_HIT + 0.15, 0.4)
pop(DNA_HIT, 81); stab(SAME_HIT, 0.6)
# lab: breakdown — bass alone + organ bubble, a tom per X
skank(LAB - 0.3, BRAIN, 0.7); bass(LAB - 0.3, BRAIN, 0.9, drop1=True)
for i, h in enumerate(XS): add(gm("Melodic Tom", [52, 48, 45][i], 0.4, 110), h, 0.4)
siren(Q_HIT, 1.3, 0.7); add(gm("Harmonica", 88, 0.6, 100), Q_HIT, 0.22)
# brain: groove back with melody
drums(BRAIN - 0.3, SAFE, "drop"); skank(BRAIN - 0.3, SAFE); bass(BRAIN - 0.3, SAFE); melody(BRAIN - 0.3, SAFE, 0.9)
for h in BRAIN_TAGS: pop(h, 84)
stab(BRAIN_HIT, 0.5)
# safe: steppers, light horn accent (not a big hit)
drums(SAFE - 0.3, OUTRO, "step", 0.95); skank(SAFE - 0.3, OUTRO); bass(SAFE - 0.3, OUTRO); stab(SAFE_HIT, 0.7)
melody(SAFE + 1.0, OUTRO, 0.8, 12, 90)
# outro: one drop, soft, melody, final chord
drums(OUTRO - 0.3, DUR - 2.0, "drop", 0.7); skank(OUTRO - 0.3, DUR - 1.0, 0.8); bass(OUTRO - 0.3, DUR - 2.0, 0.8, drop1=True)
for h in BUBS: pop(h, 84, 0.8)
for m in (45, 57, 64, 69, 72): add(piano(m, 2.0, 70), DUR - 2.0, 0.35)
for m in (69, 72, 76): add(gm("Clean Guitar", m, 1.5, 80), DUR - 2.0, 0.15)

# ---------------- mix: dub delay bus (dotted 8th, feedback, low-passed), reverb, silence, glue ----------------
dl = int(BEAT * 0.75 * SR); fb = 0.45
echo = DUB.copy()
for k in range(1, 5):
    sh = dl * k
    if sh >= N: break
    e = DUB[:-sh] * (fb ** k)
    e = np.cumsum(e, axis=0); e[3:] = (e[3:] - e[:-3]) / 3; e[:3] /= 3   # crude low-pass per repeat
    if k % 2: e = e[:, ::-1]                                              # ping-pong
    echo[sh:] += e
MIX += echo
def reverb(x):
    n = int(1.6 * SR); tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt * 3.6); ir = np.convolve(ir, np.ones(6) / 6, "same"); ir /= np.abs(ir).sum() ** 0.5 * 14
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x * 0.9 + np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)] * 0.26
MIX = np.stack([reverb(MIX[:, 0]), reverb(MIX[:, 1])], 1)
for a, b in SILENCES:
    i0, i1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.05 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] = 0
MIX = np.tanh(MIX / np.abs(MIX).max() * 1.6); MIX /= np.abs(MIX).max() / 0.85
fo = int(0.4 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
print("ok")
