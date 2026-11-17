# 《蜘蛛睡觉也会做梦抽腿？》BGM — "spider lullaby hop": music-box lullaby over a lo-fi brush groove, 98 BPM, D major.
# Night/lullaby sections: Music Box melody, Celeste + Kalimba, Pizzicato bass, brush kit, vinyl crackle, clock tick.
# REM sections: half-time 808 + crunchy (bit-crushed) snare, 16th pizzicato ostinato, darting L/R kalimba.
# Only two big hits (HOOK_HIT 0.4, REM_HIT 20.0); every other cue is a light pluck / glock / woodblock.
import sys, math, wave, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import piano, gm, drum, SR
from cues import *
_gm, _drum = gm, drum
LV = {"Orchestral Harp": 0.2, "Concert Choir": 0.13, "Xylophone": 0.18, "Celeste": 1.5, "Vibraphone": 1.5}
def gm(name, *a, **k): return _gm(name, *a, **k) * LV.get(name, 1.0)
def drum(note, vel=100, kit="Standard 1"):
    y = _drum(note, vel, kit=kit)
    return y * (0.5 if (kit in ("Brush", "Jazz") and note == 36) else 1.0) * (0.6 if note == 42 else 1.0)
N = int(SR * DUR); MIX = np.zeros((N, 2)); VERB = np.zeros((N, 2))
rng = np.random.default_rng(3)
def add(y, t0, g=1.0, pan=0.0, wet=0.0, human=True):
    if human: g *= 1 + rng.uniform(-0.08, 0.08); t0 += rng.uniform(-0.005, 0.005)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    MIX[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet

# D major lullaby: D | Bm | G | A (one chord per bar)
CH = [("D", 50, (62, 66, 69)), ("Bm", 47, (62, 66, 71)), ("G", 43, (62, 67, 71)), ("A", 45, (61, 64, 69))]
def bar_of(t): return int(math.floor((t - G0) / BAR + 1e-6))
def chord(t): return CH[bar_of(t) % 4]
def bars(t0, t1):
    b0 = bar_of(t0 + 0.01); b1 = bar_of(t1 - 0.01)
    return [G0 + b * BAR for b in range(b0, b1 + 1) if t0 - 0.01 <= G0 + b * BAR < t1 - 0.01]
SWG = 0.56   # lazy lo-fi swing for the off-8th (straight = 0.5)

def crunch(y, amt=5.0, bits=5):
    y = np.tanh(y * amt) / np.tanh(amt); q = 2 ** bits
    return np.round(y * q) / q
def boom(t0, g=1.0, dur=0.7):   # 808 sub
    tt = np.arange(int(dur * SR)) / SR
    f = 46 + 90 * np.exp(-tt * 22)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 4.5) * 0.9
    add(np.stack([y, y], 1), t0, g, human=False)

def groove(t0, t1, style="lofi", g=1.0):
    for tb in bars(t0, t1):
        for i in range(4):
            tt = tb + i * BEAT
            if style == "lofi":
                if i in (0, 2) or (i == 3 and rng.random() < 0.3): add(drum(36, 100, "Jazz"), tt + (BEAT * SWG if i == 3 else 0), 0.7 * g)
                if i in (1, 3): add(drum(38, 85, "Brush"), tt, 0.55 * g, wet=0.3)
                add(drum(42, 70), tt, 0.25 * g, pan=0.35); add(drum(42, 50), tt + BEAT * SWG, 0.18 * g, pan=0.35)
            elif style == "rem":   # half time: boom on 1, crunchy snare on 3, hats in 16ths
                if i == 0: boom(tt, 0.8 * g); add(drum(36, 110, "808/909"), tt, 0.6 * g)
                if i == 2: add(crunch(drum(38, 120, "Room")), tt, 0.32 * g, wet=0.25)
                if i == 3 and rng.random() < 0.5: boom(tt + BEAT * 0.5, 0.5 * g)
                for k in range(4): add(drum(42, 60 + (20 if k == 0 else 0), "808/909"), tt + k * BEAT / 4, 0.5 * g, pan=0.3 * (1 if k % 2 else -1))
            elif style == "soft":
                if i == 0: add(drum(36, 80, "Jazz"), tt, 0.5 * g)
                add(drum(70, 60), tt + BEAT * SWG, 0.2 * g, pan=-0.3)   # maracas
def pizz_bass(t0, t1, g=1.0, walk=True):
    for tb in bars(t0, t1):
        r = chord(tb + 0.01)[1]
        pat = [(0, 0), (1, 7), (2, 12), (3, 7)] if walk else [(0, 0), (2, 7)]
        for pos, iv in pat: add(gm("Pizzicato Strings", r + iv, 0.4, 105), tb + pos * BEAT, 0.5 * g, pan=-0.1)
        add(gm("Acoustic Bass", r - 12 + 12, 0.9, 95, release=0.1), tb, 0.45 * g)
def pizz16(t0, t1, g=1.0):   # REM ostinato
    for tb in bars(t0, t1):
        _, r, v = chord(tb + 0.01)
        seq = [v[0], v[1] + 12, v[2], v[1] + 12]
        for k in range(16): add(gm("Pizzicato Strings", seq[k % 4], 0.15, 90 + (20 if k % 4 == 0 else 0)), tb + k * BEAT / 4, 0.22 * g, pan=0.25)
def kal_arp(t0, t1, g=1.0, dart=False):
    for tb in bars(t0, t1):
        _, _, v = chord(tb + 0.01)
        notes = [v[0] + 12, v[1] + 12, v[2] + 12, v[1] + 12, v[0] + 24, v[2] + 12, v[1] + 12, v[2] + 12]
        for k, m in enumerate(notes):
            add(gm("Kalimba", m, 0.3, 85), tb + k * BEAT / 2 + (BEAT / 2 * (SWG - 0.5) * 2 if k % 2 else 0), 0.28 * g,
                pan=(0.7 if k % 2 else -0.7) if dart else 0.2, wet=0.3)
def celeste(t0, t1, g=1.0):   # soft broken chords, no long pads
    for tb in bars(t0, t1):
        _, _, v = chord(tb + 0.01)
        for k in range(8): add(gm("Celeste", v[k % 3] + 12, 0.35, 70), tb + k * BEAT / 2, 0.16 * g, pan=-0.3, wet=0.4)
MEL = [[(0, 78), (1, 76), (1.5, 74), (2, 76), (3, 78)],
       [(0, 81), (1.5, 78), (2, 74), (3, 76)],
       [(0, 74), (1, 71), (1.5, 74), (2, 79), (3, 78)],
       [(0, 76), (1, 73), (2, 76), (2.5, 78), (3, 76)]]
def box(t0, t1, g=1.0, oct=0, inst="Music Box"):
    for tb in bars(t0, t1):
        for pos, m in MEL[bar_of(tb + 0.01) % 4]:
            add(gm(inst, m + oct, 0.6, 95), tb + pos * BEAT, 0.3 * g, pan=0.15, wet=0.5)
def tick(t0, t1, g=1.0):   # clock: tick-tock each beat
    k = 0; tt = G0 + math.ceil((t0 - G0) / BEAT) * BEAT
    while tt < t1:
        add(drum(75 if k % 2 == 0 else 76, 70), tt, 0.18 * g, pan=-0.4); k += 1; tt += BEAT
def pop(t0, m=86, g=1.0, inst="Glockenspiel"): add(gm(inst, m, 0.4, 100), t0, 0.32 * g, wet=0.4)
def pluck(t0, m, g=1.0): add(gm("Pizzicato Strings", m, 0.3, 115), t0, 0.5 * g); add(gm("Kalimba", m + 12, 0.3, 100), t0, 0.25 * g, wet=0.3)
def beep(t0, f=1320, dur=0.22, g=1.0):
    tt = np.arange(int(dur * SR)) / SR
    y = np.sign(np.sin(2 * np.pi * f * tt)) * 0.07 * np.minimum(1, tt * 200) * np.minimum(1, (dur - tt) * 60)
    add(np.stack([y, y], 1), t0, g, human=False)
def harp_gliss(t0, up=True, g=1.0, n=12):
    sc = [62, 64, 66, 69, 71, 74, 76, 78, 81, 83, 86, 88]
    for k, m in enumerate(sc[:n] if up else sc[:n][::-1]): add(gm("Orchestral Harp", m, 0.6, 90), t0 + k * 0.045, 0.35 * g, wet=0.5)
def big(t0, g=1.0):
    boom(t0, 1.2 * g, 1.2); add(drum(36, 127), t0, 0.8 * g); add(drum(49, 120), t0, 0.6 * g, wet=0.3); add(drum(57, 100), t0 + 0.02, 0.3 * g)
    for m in (38, 50, 57, 62, 66, 69): add(piano(m, 1.6, 118), t0, 0.32 * g, wet=0.3)
    for m in (62, 66, 69, 74): add(gm("Concert Choir", m, 0.9, 110, release=0.4), t0, 0.35 * g, wet=0.5)
    for k, m in enumerate([86, 90, 93, 98]): add(gm("Glockenspiel", m, 0.4, 110), t0 + 0.08 + k * 0.07, 0.25 * g, wet=0.5)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR
    y = np.convolve(rng.standard_normal(n), np.ones(5) / 5, "same") * (tt / (t1 - t0)) ** 2.5 * 0.08
    add(np.stack([y, y], 1), t0, g, human=False)
    for k in range(10): add(gm("Music Box", 74 + k * 2, 0.2, 80 + k * 4), t0 + (t1 - t0) * (1 - 0.8 ** (k + 1)) / (1 - 0.8 ** 10), 0.2 * g)

# ---------------- arrangement ----------------
for k, m in enumerate([74, 78, 81, 86, 90]): add(gm("Music Box", m, 0.3, 90), 0.02 + k * 0.07, 0.25)   # wind-up sparkle
big(HOOK_HIT)
groove(HOOK_HIT, LAB, "rem", 0.9); pizz16(HOOK_HIT, LAB, 0.9); box(HOOK_HIT, LAB, 1.0, 12)
# lab: clock ticking, pizz bass, celeste — curious & quiet
tick(LAB, BRUSH); pizz_bass(LAB - 0.05, BRUSH, 0.8, walk=False); celeste(LAB - 0.05, BRUSH)
pop(LAB_HIT, 81); pop(CAMS[0], 86, 0.7, "Xylophone"); pop(CAMS[1], 88, 0.7, "Xylophone"); pop(NAME_HIT, 93)
# brush: lo-fi groove enters, one pluck per leg climbing the scale
groove(BRUSH - 0.05, HAM, "soft"); pizz_bass(BRUSH - 0.05, HAM, 0.7, walk=False)
for i, h in enumerate(LEGS): pluck(h, [62, 64, 66, 69, 71, 74, 76, 78][i])
add(drum(81, 100), TOOTH_HIT, 0.4, wet=0.4); pop(TOOTH_HIT, 90)
# hammock: harp gliss for the silk, music-box melody, falling tom on the flip
groove(HAM - 0.05, CHECK, "lofi", 0.8); pizz_bass(HAM - 0.05, CHECK); box(HAM - 0.05, CHECK); harp_gliss(SILK_HIT)
add(gm("Melodic Tom", 55, 0.4, 100), FLIP_HIT - 0.1, 0.15); add(gm("Melodic Tom", 48, 0.5, 105), FLIP_HIT, 0.18)
# checklist: steady groove, a rising glock tick per criterion
groove(CHECK - 0.05, DEEP, "lofi"); pizz_bass(CHECK - 0.05, DEEP); celeste(CHECK - 0.05, DEEP, 0.8)
for i, h in enumerate(TICKS): pop(h, [81, 83, 86, 88, 90][i]); add(drum(75, 90), h, 0.25)
# deep sleep: music box alone, clock slows, riser, silence
box(DEEP - 0.05, SIL0 - 0.2, 0.8, 0); tick(DEEP, SIL0 - 0.6, 0.7); riser(RISERS[0][0], SIL0)
# REM: big hit 2, half-time 808 + crunchy snare, 16th pizz, darting kalimba
big(REM_HIT, 1.1)
groove(REM_HIT, SOUND, "rem"); pizz16(REM_HIT, SOUND); box(REM_HIT, EYE, 1.0, 12)
kal_arp(EYE - 0.05, SOUND, 1.0, dart=True); pop(EYE_HIT, 93)
# sound test: drums out, beeps, then the lullaby carries on ("still asleep")
celeste(SOUND - 0.05, REB, 0.7); pizz_bass(SOUND - 0.05, REB, 0.6, walk=False)
for h in HONK: beep(h); beep(h + 0.12, 990)
box(DEAF_HIT - 0.05, REB, 0.9); add(drum(81, 90), DEAF_HIT, 0.35, wet=0.4)
# rebound: night 1 stutters (woodblock pokes), night 2 cosy groove, glock gliss on "sleeps longer"
tick(REB, NIGHT2, 1.0); pizz_bass(REB - 0.05, NIGHT2, 0.6, walk=False)
for h in POKES: add(drum(76, 110), h, 0.45); add(gm("Pizzicato Strings", 74, 0.2, 120), h, 0.35)
groove(NIGHT2 - 0.05, PROOF, "lofi", 0.8); pizz_bass(NIGHT2 - 0.05, PROOF); box(NIGHT2 - 0.05, PROOF, 0.8)
harp_gliss(LONG_HIT, True, 0.8)
# proof: groove full (no big hit), kalimba arps, stacked glock on the stamp
groove(PROOF - 0.05, DREAM); pizz_bass(PROOF - 0.05, DREAM); kal_arp(PROOF - 0.05, DREAM); box(PROOF - 0.05, DREAM, 0.9, 12)
add(drum(49, 80), PROOF_HIT, 0.3, wet=0.3); pop(PROOF_HIT, 86); pop(PROOF_HIT + 0.08, 90); pop(STAGE_HIT, 81); pop(STAGE_HIT + 0.3, 88)
# dream: floaty — harp, music box, soft maracas only; question motif
groove(DREAM - 0.05, OLD, "soft", 1.0); celeste(DREAM - 0.05, OLD, 1.3); box(DREAM - 0.05, OLD, 1.2); kal_arp(DREAM - 0.05, OLD, 0.6); harp_gliss(DREAM_HIT, True, 0.7)
for k, m in enumerate([81, 83, 86, 90]): pop(Q_HIT + k * 0.12, m, 0.7, "Vibraphone")
# old: lo-fi groove back
groove(OLD - 0.05, OUTRO); pizz_bass(OLD - 0.05, OUTRO); kal_arp(OLD - 0.05, OUTRO, 0.8)
pop(OLD_HIT, 81, 0.8, "Xylophone"); pop(OLD2_HIT, 86)
# outro: music box lullaby, soft, final chord
box(OUTRO - 0.05, DUR - 2.0, 0.9); groove(OUTRO - 0.05, DUR - 2.4, "soft", 0.7); pizz_bass(OUTRO - 0.05, DUR - 2.4, 0.6, walk=False)
for h in BUBS: pop(h, 88, 0.6)
for m in (38, 50, 57, 62, 66, 69): add(piano(m, 2.2, 66), DUR - 2.2, 0.3, wet=0.3)
add(gm("Music Box", 86, 1.2, 80), DUR - 2.2, 0.25, wet=0.6)

# ---------------- mix: vinyl crackle, reverb send, silence, glue ----------------
crack = np.zeros(N); idx = rng.integers(0, N, int(DUR * 25)); crack[idx] = rng.uniform(-1, 1, len(idx)) * 0.05
crack = np.convolve(crack, [1, -0.6, 0.2], "same") + np.convolve(rng.standard_normal(N), np.ones(30) / 30, "same") * 0.004
MIX += np.stack([crack, np.roll(crack, 37)], 1)
def reverb(x):
    n = int(2.2 * SR); tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt * 2.8); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
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
