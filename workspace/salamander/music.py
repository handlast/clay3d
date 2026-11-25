# 《有毒的火蝾螈，一照紫外灯居然会发光？》BGM — dark synthwave / Halloween neon club. A minor (Am F Dm E, harmonic E major), 110.2 BPM.
# Core 1-bar loop: four-on-the-floor kick + off-beat open hat + clap on 2/4 + soft 16th hats.
# Soul of the loop: 16th-note octave-jumping saw bass (numpy additive synthesis with a resonant 4-pole low-pass response and a
# pluck filter envelope) + 16th square/saw arp hook, both pumped by a hard kick sidechain.
# Global filter: muffled (~1 kHz hook, ~480 Hz mid) for the first 20 s, slams fully open at 20.0 s (the UV lamp switching on).
# Big hits only at 0.4 s and 20.0 s (sub boom + crash + saw stab). 19.456-20.0 hard silence.
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import gm as _gm, drum as _drum, SR
from cues import *
rng = np.random.default_rng(31)
N = int(SR * DUR)
BUS = {k: np.zeros((N, 2)) for k in ("drm", "bass", "arp", "lead", "stab", "fx", "verb", "dly")}
LOG = []
def add(bus, y, t0, g=1.0, pan=0.0, wet=0.0, dly=0.0):
    if y.ndim == 1: y = np.stack([y, y], 1)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    BUS[bus][i:i + len(y)] += y
    if wet: BUS["verb"][i:i + len(y)] += y * wet
    if dly: BUS["dly"][i:i + len(y)] += y * dly
LV = {"Music Box": 0.9, "Celeste": 1.2, "Glockenspiel": 1.0}
@functools.lru_cache(maxsize=None)
def gm(name, m, dur=0.5, vel=100, release=0.3): return _gm(name, m, dur, vel, release=release) * LV.get(name, 1.0)
@functools.lru_cache(maxsize=None)
def gdrum(n, vel=100): return _drum(n, vel) / max(1e-6, np.abs(_drum(n, vel)).max())   # normalised to peak 1
def mtof(m): return 440 * 2 ** ((m - 69) / 12)

# ---------------- harmony / grid ----------------
CH = [("Am", 33, (69, 72, 76)), ("F", 29, (65, 69, 72)), ("Dm", 38, (62, 65, 69)), ("E", 40, (64, 68, 71))]
def bar_of(t): return int(math.floor((t - G0) / BAR + 1e-6))
def chord(t):
    b = bar_of(t)
    return CH[0] if b <= 0 else CH[(b + 3) % 4]          # bar 0 (hook) = Am, then bar 9 (20.0 s) lands on Am again
def grid(t0, t1, sub=4):
    out = []; k = math.ceil((t0 - G0) / (BEAT / sub) - 1e-6)
    while True:
        tt = G0 + k * BEAT / sub
        if tt >= t1 - 1e-6: break
        if tt >= -1e-6: out.append((tt, k % (4 * sub)))
        k += 1
    return out

# ---------------- global filter + sidechain ----------------
def cutoff(t):
    if t < HOOK_STOP + 0.2: return 1000.0
    if t < SWITCH: return 480.0 * (1 + 0.5 * cl_((t - bar(6)) / (SWITCH - bar(6))))
    if t < BIG: return 480.0
    if bar(15) <= t < bar(17):
        f0 = bar(17) - BEAT
        return 1100.0 if t < f0 else 1100.0 * (9000 / 1100) ** ((t - f0) / BEAT)
    if t >= OUTRO: return 2600.0
    return 9000.0
def reso(t): return 2.6 if (t < BIG or bar(15) <= t < bar(17) - BEAT) else 1.3
def cl_(x): return max(0.0, min(1.0, x))
KICKS = []

# ---------------- additive band-limited oscillators through a resonant low-pass ----------------
def lp_mag(fr, fc, q):
    r = fr / fc
    return 1 / np.sqrt((1 - r ** 2) ** 2 + (r / q) ** 2) / np.sqrt((1 - r ** 2) ** 2 + (r / 0.707) ** 2)
@functools.lru_cache(maxsize=None)
def voice(m, dur, wave_="saw", fc=1000.0, q=1.3, env_amt=2.5, env_dec=0.07, det=0.0, sub=0.0, rel=0.02, vib=0.0, att=0.003):
    f = mtof(m); n = int((dur + rel) * SR); tt = np.arange(n) / SR
    fct = fc * (1 + env_amt * np.exp(-tt / env_dec))
    out = np.zeros(n)
    for dd in ((-det, det) if det else (0.0,)):
        ff = f * 2 ** (dd / 1200)
        inst = ff * (1 + vib * 0.006 * np.sin(2 * np.pi * 5.5 * tt) * np.clip((tt - 0.15) / 0.2, 0, 1))
        ph = 2 * np.pi * np.cumsum(inst) / SR
        kmax = int(min(15000, fc * (1 + env_amt) * 6) / ff) + 1
        ks = np.arange(1, kmax + 1)
        if wave_ == "sq": ks = ks[ks % 2 == 1]
        amp = (1 / ks)[:, None] * lp_mag(ks[:, None] * ff, fct[None, :], q)
        amp[(ks * ff) > 18000] = 0
        out += (amp * np.sin(ks[:, None] * ph[None, :])).sum(0)
    out /= (2 if det else 1)
    if sub: out += sub * np.sin(2 * np.pi * np.cumsum(np.full(n, f)) / SR)
    env = np.minimum(1, tt / att) * np.clip((dur + rel - tt) / rel, 0, 1)
    return out * env
def qfc(fc): return float(round(fc / 10) * 10) if fc < 2000 else float(round(fc / 100) * 100)

# ---------------- drums (synth, normalised so peak ~1 per hit) ----------------
def _norm(y): return y / np.abs(y).max()
def bandnoise(n, lo, hi, seed=0):
    x = np.random.default_rng(seed).standard_normal(n); X = np.fft.rfft(x); fr = np.fft.rfftfreq(n, 1 / SR)
    X[(fr < lo) | (fr > hi)] = 0; return _norm(np.fft.irfft(X, n))
@functools.lru_cache(maxsize=None)
def kick_s():
    tt = np.arange(int(0.42 * SR)) / SR; f = 46 + 130 * np.exp(-tt * 32)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7.5) + bandnoise(len(tt), 2000, 9000, 1) * np.exp(-tt * 400) * 0.35
    return _norm(np.tanh(y * 1.6))
@functools.lru_cache(maxsize=None)
def clap_s():
    n = int(0.35 * SR); tt = np.arange(n) / SR; nz = bandnoise(n, 900, 5000, 2)
    env = sum(np.where(tt >= o, np.exp(-(tt - o) * 140), 0) for o in (0, 0.011, 0.022)) + np.where(tt >= 0.03, 0.55 * np.exp(-(tt - 0.03) * 16), 0)
    return _norm(nz * env)
@functools.lru_cache(maxsize=None)
def ohat_s():
    n = int(0.3 * SR); tt = np.arange(n) / SR; return _norm(bandnoise(n, 6500, 16000, 3) * np.exp(-tt * 13))
@functools.lru_cache(maxsize=None)
def chat_s():
    n = int(0.07 * SR); tt = np.arange(n) / SR; return _norm(bandnoise(n, 8000, 17000, 4) * np.exp(-tt * 70))
@functools.lru_cache(maxsize=None)
def snare_s():
    n = int(0.22 * SR); tt = np.arange(n) / SR
    return _norm(bandnoise(n, 1200, 8000, 5) * np.exp(-tt * 24) + 0.6 * np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 30))
def kick(t0, g=1.0):
    add("drm", kick_s(), t0, 0.95 * g); KICKS.append(t0)
def groove(t0, t1, g=1.0, kick_on=True, clap_on=True, hats=True, ohat=True):
    for tt, k in grid(t0, t1, 4):          # 16th grid, k = 0..15
        if k % 4 == 0 and kick_on: kick(tt, g)
        if k in (4, 12) and clap_on: add("drm", clap_s(), tt, 0.55 * g, wet=0.12)
        if k % 4 == 2 and ohat: add("drm", ohat_s(), tt, 0.22 * g, pan=0.25)
        if hats and k % 2 == 1: add("drm", chat_s(), tt, (0.1 if k % 4 == 1 else 0.07) * g, pan=-0.3)
def fill(t0, t1, g=1.0):                   # snare roll: 16ths -> 32nds, rising
    n = int(round((t1 - t0) / (BEAT / 8)))
    for j in range(n): add("drm", snare_s(), t0 + j * BEAT / 8, (0.18 + 0.32 * j / n) * g, pan=0.1 * (-1) ** j, wet=0.1)
def boom(t0, g=1.0, dur=1.4):
    tt = np.arange(int(dur * SR)) / SR; f = 34 + 70 * np.exp(-tt * 14)
    add("fx", np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.6), t0, g)
def crash(t0, g=1.0): add("drm", gdrum(49, 120), t0, 0.5 * g, wet=0.3); add("drm", gdrum(57, 110), t0 + 0.005, 0.3 * g, pan=0.4)
def revcrash(t1, g=1.0, L=1.2):
    y = gdrum(49, 110)[: int(L * SR)][::-1] * np.linspace(0, 1, int(L * SR))[:, None] ** 2; add("fx", y, t1 - L, 0.45 * g, wet=0.3)
def heart(t0, g=1.0):
    for dt, f0, gg in ((0, 58, 1.0), (0.16, 50, 0.7)):
        tt = np.arange(int(0.3 * SR)) / SR; f = f0 + 40 * np.exp(-tt * 30)
        add("drm", np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 12), t0 + dt, 0.9 * g * gg)

# ---------------- synth parts ----------------
def bass(t0, t1, g=1.0):
    for tt, k in grid(t0, t1, 4):
        _, r, _ = chord(tt + 0.01); m = r + (12 if k % 2 else 0)
        y = voice(m, BEAT / 4 * 0.85, "saw", qfc(cutoff(tt)), reso(tt), 2.2, 0.06, 6.0, 0.6 if k % 2 == 0 else 0.0)
        add("bass", y, tt, (0.5 if k % 4 == 0 else 0.38) * g)
APAT = [0, 2, 3, 4, 3, 2, 0, 2, 1, 2, 3, 5, 4, 3, 2, 1]
def arp(t0, t1, g=1.0, oct=0, wave_="sq"):
    for tt, k in grid(t0, t1, 4):
        _, _, v = chord(tt + 0.01); ext = [v[0], v[1], v[2], v[0] + 12, v[1] + 12, v[2] + 12]
        m = ext[APAT[k]] + oct
        y = voice(m, BEAT / 4 * 0.7, wave_, qfc(cutoff(tt) * 1.3), reso(tt), 3.0, 0.05, 8.0)
        add("arp", y, tt, (0.2 if k % 4 == 0 else 0.15) * g, pan=0.25 * math.sin(k * 0.9), dly=0.35)
MEL = [[(0, 76, 1.5), (1.5, 74, .5), (2, 72, 1), (3, 69, 1)],
       [(0, 72, 1.5), (1.5, 74, .5), (2, 76, 1), (3, 77, 1)],
       [(0, 74, 1.5), (1.5, 72, .5), (2, 69, 1), (3, 77, 1)],
       [(0, 76, 1.5), (1.5, 74, .5), (2, 71, 1), (3, 68, 1)]]
def lead(t0, t1, g=1.0):
    for b in range(bar_of(t0 + 0.01), bar_of(t1 - 0.01) + 1):
        tb = G0 + b * BAR
        for pos, m, du in MEL[(b + 3) % 4]:
            ts = tb + pos * BEAT
            if t0 - 0.01 <= ts < t1 - 0.05:
                y = voice(m, du * BEAT * 0.92, "saw", qfc(min(cutoff(ts), 4200)), 1.6, 1.5, 0.12, 9.0, 0, 0.06, 1.0, 0.01)
                add("lead", y, ts, 0.16 * g, wet=0.3, dly=0.3)
def stab(t0, g=1.0, chord_=(57, 60, 64, 69, 72), fc=6000.0):
    for j, m in enumerate(chord_): add("stab", voice(m, 0.55, "saw", fc, 1.4, 2.0, 0.18, 12.0, 0, 0.35), t0, 0.12 * g, pan=0.4 * ((j % 2) * 2 - 1) * 0.6, wet=0.35)
def big(t0, g=1.0):
    boom(t0, 1.1 * g); kick(t0, 1.1 * g); crash(t0, 1.1 * g); stab(t0, 1.6 * g, (45, 57, 60, 64, 69, 72, 76))

# ---------------- sfx ----------------
def click(t0, g=1.0):   # light switch "ka-da"
    for dt, f, gg in ((0, 3200, 1.0), (0.05, 1900, 0.8)):
        n = int(0.04 * SR); tt = np.arange(n) / SR
        y = bandnoise(n, 2500, 12000, 7) * np.exp(-tt * 600) + 0.5 * np.sin(2 * np.pi * f * tt) * np.exp(-tt * 180)
        add("fx", y, t0 + dt, 0.45 * g * gg)
def neon(t0, g=1.0):    # tube starter flicker -> short hum, ~0.55 s, no sustained pad
    n = int(0.6 * SR); tt = np.arange(n) / SR
    buzz = sum(np.sin(2 * np.pi * 100 * k * tt) / k for k in range(1, 30)) + 0.3 * bandnoise(n, 3000, 9000, 8)
    gate = np.zeros(n)
    for a_, b_ in ((0, .03), (.07, .09), (.15, .19), (.24, .6)): gate[int(a_ * SR):int(b_ * SR)] = 1
    gate = np.convolve(gate, np.ones(80) / 80, "same") * np.exp(-np.maximum(0, tt - 0.24) * 6)
    add("fx", buzz * gate * 0.09, t0, g, pan=-0.2, wet=0.2)
    add("fx", np.sin(2 * np.pi * 4200 * tt[:4000]) * np.exp(-tt[:4000] * 60) * 0.15, t0 + 0.24, g, wet=0.3)
def drip(t0, g=1.0):
    n = int(0.25 * SR); tt = np.arange(n) / SR; f = 700 + 1500 * (1 - np.exp(-tt * 45))
    add("fx", np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 22) * 0.5, t0, g, wet=0.5)
def tick(t0, g=1.0, hi=True):
    n = int(0.03 * SR); tt = np.arange(n) / SR
    add("fx", (np.sin(2 * np.pi * (3100 if hi else 2400) * tt) * 0.6 + bandnoise(n, 4000, 12000, 9) * 0.4) * np.exp(-tt * 260), t0, 0.3 * g, pan=0.3 if hi else -0.3)
def bell(t0, m=96, g=1.0):  # firefly "ding": 2-op FM bell
    n = int(0.9 * SR); tt = np.arange(n) / SR; f = mtof(m)
    y = np.sin(2 * np.pi * f * tt + 2.0 * np.exp(-tt * 6) * np.sin(2 * np.pi * f * 3.5 * tt)) * np.exp(-tt * 5)
    add("fx", y * 0.22, t0, g, pan=-0.3, wet=0.5, dly=0.3)
def blip(t0, notes, step=0.06, g=1.0):
    for j, m in enumerate(notes): add("fx", voice(m, 0.07, "sq", 5000.0, 1.0, 0.0, 0.05), t0 + j * step, 0.09 * g, pan=0.2, wet=0.15)
def pluck(t0, m=81, g=1.0): add("fx", voice(m, 0.18, "saw", 900.0, 2.0, 5.0, 0.04, 8.0), t0, 0.14 * g, wet=0.3, dly=0.3)
def buzzer(t0, g=1.0):
    for f0 in (98, 104): add("fx", voice(int(round(12 * math.log2(f0 / 440) + 69)), 0.38, "sq", 2200.0, 1.0, 0.0), t0, 0.12 * g)
def zap(t0, g=1.0):
    n = int(0.28 * SR); tt = np.arange(n) / SR; f = 2400 * np.exp(-tt * 14) + 90
    y = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-tt * 8) * 0.18 + bandnoise(n, 2000, 10000, 10) * np.exp(-tt * 30) * 0.15
    add("fx", y, t0, g, wet=0.25)
def glitch(t0, g=1.0, seed=0):
    r2 = np.random.default_rng(seed); seg = int(0.022 * SR); out = []
    for j in range(9):
        f = r2.uniform(200, 2600); tt = np.arange(seg) / SR
        y = np.sign(np.sin(2 * np.pi * f * tt)) * (0.6 if j % 3 else 1.0)
        if j % 2: y = np.repeat(y[::12], 12)[:seg]            # sample-rate crush
        out.append(y * (1 - j / 12))
    y = np.concatenate(out); y = np.concatenate([y[: seg * 3]] * 2 + [y])   # stutter
    add("fx", y * 0.1, t0, g, pan=float(r2.uniform(-0.5, 0.5)))
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR; k = tt / (t1 - t0)
    nz = bandnoise(n, 400, 12000, 11) * k ** 2.5 * 0.12
    f = 110 * 2 ** (3 * k); saw = (2 * ((np.cumsum(f) / SR) % 1) - 1) * k ** 2 * 0.05
    add("fx", nz + saw, t0, g, wet=0.2)
def boing(t0, g=1.0):
    n = int(0.3 * SR); tt = np.arange(n) / SR; f = 500 + 500 * np.sin(np.pi * tt / 0.3) + 60 * np.sin(2 * np.pi * 18 * tt)
    add("fx", np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, (0.3 - tt) / 0.05) * 0.2, t0, g, wet=0.2)
def mbox(t0, m, g=1.0): add("fx", gm("Music Box", m, 0.5, 90, 0.4), t0, 0.5 * g, pan=0.25, wet=0.45)

# ================= arrangement =================
# 0 - 0.4: lights off "click" + sucking reverse swell + tube flicker into hit 1
click(LIGHT_OFF); revcrash(HOOK_HIT, 0.9, 0.35); neon(HOOK_HIT - 0.12, 1.0)
big(HOOK_HIT)
groove(HOOK_HIT + 0.01, HOOK_STOP); bass(HOOK_HIT, HOOK_STOP); arp(HOOK_HIT, HOOK_STOP)
# 2.58 hard stop (only reverb tails), 3.67 muffled loop comes in
groove(MEET, bar(5)); bass(MEET, bar(5)); arp(MEET, bar(5), 0.9)
fill(bar(4) - BEAT, bar(4), 0.9)                               # fill: end of the 4-bar phrase
for j, h in enumerate(MEET_TAGS): blip(h, [[81, 88], [64, 57], [76, 83], [88, 93, 88]][j], 0.06, 0.9)
for j, h in enumerate(PAPERS): add("fx", bandnoise(int(0.06 * SR), 2000, 9000, 20 + j) * np.exp(-np.arange(int(0.06 * SR)) / SR * 60) * 0.12, h)
pluck(LAB_STAMP, 76); pluck(LAB_STAMP + BEAT / 2, 81)
# bar 5 (11.28 - 13.47): drop bar -> drums + arp out, muffled bass only, question blips, buzzer on "0 papers"
bass(bar(5), bar(6), 0.9)
for j, h in enumerate(QMARKS): blip(h, [76 + 3 * j, 83 + 3 * j], 0.07, 0.8)
buzzer(ZERO); pluck(NONE_TAG, 69)
groove(bar(6), SWITCH); bass(bar(6), SWITCH); arp(bar(6), SWITCH)
revcrash(SWITCH, 0.6, 0.8)
# 15.64 - 19.46: heartbeat kick + clock tick + riser + countdown beeps (no bass, no arp)
for tt, k in grid(SWITCH, SIL0, 1):
    heart(tt, 0.55 + 0.45 * (tt - SWITCH) / (SIL0 - SWITCH))
for tt, k in grid(SWITCH, SIL0 - 0.05, 2): tick(tt, 0.9, k % 2 == 0)
for j, h in enumerate(COUNT): add("fx", voice(84 + 5 * (j == 2), 0.12, "sq", 3000.0, 1.0, 0.0, 0.05), h, 0.1, wet=0.2)
riser(RISERS[0][0], SIL0, 1.0)
# 19.456 - 20.0 silence. 20.0: switch click + tube + hit 2, filter wide open
click(BIG - 0.005, 1.1); neon(BIG, 1.2); big(BIG, 1.15)
groove(BIG + 0.01, bar(15)); bass(BIG, bar(15)); arp(BIG, bar(15), 1.0)
lead(bar(11), bar(13), 0.9)
for h in BURST_TAGS: blip(h, [88, 95], 0.06, 0.8)
drip(DRIP, 1.1); drip(DRIP + 0.18, 0.5)
tk = CLOCK0; gap = 0.12
while tk < CLOCK1: tick(tk, 0.8, int(tk * 100) % 2 == 0); tk += gap; gap = max(0.035, gap * 0.9)
pluck(VEN_STAMP, 81); pluck(VEN_STAMP + 0.1, 88)
for j, h in enumerate(FIREFLY): bell(h, [93, 96, 100][j], 0.9)
neon(UVON - 0.05, 0.6); zap(CONVERT, 0.6); blip(FLUO_TAG, [81, 88], 0.07, 0.7)
fill(bar(13) - BEAT, bar(13), 1.0); crash(bar(13), 0.5)
for j, h in enumerate(GLITCH): glitch(h, 1.0, j)
# bars 15-16 breakdown: bass + clap only, filter dips; bar 16 = drop bar (no drums), music box on the moon
groove(bar(15), bar(16), 0.9, kick_on=False, hats=False, ohat=False); bass(bar(15), bar(17), 0.95)
for tt, k in grid(bar(15), bar(16), 4):
    if k % 4 == 0: KICKS.append(tt)          # ghost sidechain keeps the pump without an audible kick
MB = [76, 72, 69, 72, 77, 76, 74, 72, 74, 72, 69, 65, 68, 71, 76, 74]
for j, (tt, k) in enumerate(grid(bar(15), bar(17) - BEAT, 2)): mbox(tt, MB[j % 16] + 12, 0.8)
for h in HEARTS: bell(h, 100, 0.5)
fill(bar(17) - BEAT, bar(17), 1.0)
# bars 17-18 predator: full loop + lead; zaps on the glow flashes
groove(bar(17), END); bass(bar(17), END); arp(bar(17), END); lead(bar(17), END, 1.0); crash(bar(17), 0.7)
zap(ZAP, 1.1); zap(ZAP2, 0.9); pluck(PRED_STAMP, 88)
# bar 19 ending: groove without clap, arp up an octave, firefly dots twinkle
groove(END, bar(20), 0.85, clap_on=False); bass(END, bar(20), 0.9); arp(END, bar(20), 0.9, 12)
for j in range(6): bell(DOTS0 + j * 0.27, [96, 100, 103, 108, 100, 96][j], 0.45)
pluck(END_STAMP, 81)
fill(bar(20) - BEAT, bar(20), 0.8)
# outro: soft closing hit, then a clean tail
kick(bar(20), 0.8); crash(bar(20), 0.45); stab(bar(20), 0.9, (57, 60, 64, 69))
arp(bar(20), OUTRO + BEAT * 2, 0.6, 12)
boing(WINK, 1.0); blip(BUB, [88, 93], 0.05, 0.8)
stab(FINAL, 0.7, (45, 57, 64, 69, 72)); add("bass", voice(33, 1.2, "saw", 600.0, 1.2, 1.0, 0.2, 6.0, 0.8, 0.4), FINAL, 0.45); bell(FINAL + 0.05, 93, 0.6)

# ================= mix =================
def conv(x, ir):
    sz = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
def hall_ir():
    n = int(2.0 * SR); tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt * 3.0); ir = np.convolve(ir, np.ones(6) / 6, "same"); return ir / (np.abs(ir).sum() ** 0.5 * 10)
# sidechain: hard pump on every kick (bass, arp; lead lighter)
env = np.ones(N); L = int(0.3 * SR); shape = 1 - 0.82 * (1 - np.minimum(1, np.arange(L) / L)) ** 1.6
for k in KICKS:
    i = int(k * SR); e = shape[: max(0, min(L, N - i))]; env[i:i + len(e)] = np.minimum(env[i:i + len(e)], e)
for b in ("bass", "arp"): BUS[b] *= env[:, None]
BUS["lead"] *= (0.55 + 0.45 * env)[:, None]; BUS["dly"] *= (0.4 + 0.6 * env)[:, None]
# ping-pong delay (dotted 8th)
D = int(0.75 * BEAT * SR); dl = BUS["dly"].mean(1); pp = np.zeros((N, 2))
for k in range(1, 6):
    s = dl[: N - k * D] * 0.45 ** k; pp[k * D:, k % 2] += s
RM = {k: round(20*math.log10(1e-9+float(np.sqrt((v[int(a_*SR):int(b_*SR)]**2).mean()))),1) for k, v in BUS.items() for a_, b_ in [(21, 32)]}; print("bus rms 21-32:", RM)
peaks = {k: float(np.abs(v).max()) for k, v in BUS.items()}
print("bus peaks:", {k: round(v, 2) for k, v in peaks.items()})
G = {"drm": 1.0, "bass": 0.8, "arp": 3.2, "lead": 3.0, "stab": 1.0, "fx": 1.1}
pre = np.ones(N); pre[int(MEET * SR):int(SWITCH * SR)] = 0.72     # muffled section sits lower so 20.0 s feels like a door opening
for b in ("drm", "bass", "arp"): BUS[b] *= pre[:, None]
MIX = sum(BUS[k] * G[k] for k in G) + pp * 0.8
h = hall_ir(); MIX += np.stack([conv(BUS["verb"][:, 0], h), conv(BUS["verb"][:, 1], h * 0.97)], 1) * 0.6
for a, b in SILENCES:
    i0, i1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.03 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] = 0
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.2); MIX /= np.abs(MIX).max() / 0.9
fo = int(0.6 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * math.log10(max(1e-6, float(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean())))) for i in range(0, int(DUR), 2)]
print("rms/2s dB:", " ".join(f"{i*2}:{v:.0f}" for i, v in enumerate(r)))
print("BPM %.2f kicks %d" % (BPM, len(KICKS)))
