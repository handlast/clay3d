import numpy as np, wave
from cues import DUR
SR = 44100; N = int(SR * DUR)
LL = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def T(d): return np.arange(int(d * SR)) / SR
def add(sig, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i < 0: return
    s = sig[: N - i] * g
    LL[i:i + len(s)] += s * (1 - max(pan, 0)); R[i:i + len(s)] += s * (1 + min(pan, 0))
def noise(d): return rng.standard_normal(int(d * SR))
def hp(y): return np.diff(y, prepend=0)

# "plant click": broadband transient + short resonant ring (pitched-down ultrasound, stylised)
def pclick(f=2600, d=0.09, g=1.0):
    t = T(d)
    ring = np.sin(2 * np.pi * f * t) * np.exp(-t * 90) + 0.5 * np.sin(2 * np.pi * f * 1.6 * t) * np.exp(-t * 140)
    tr = hp(noise(d)) * np.exp(-t * 400)
    return (ring * 0.6 + tr * 0.5) * 0.12 * g
def piano(m, d=2.5, g=1.0):
    t = T(d); f = hz(m)
    y = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1.2 + k * 0.8)) for k, a in ((1, 1), (2, .35), (3, .15), (4, .06)))
    return y * np.minimum(1, t / 0.004) * 0.07 * g
def drone(m, d, g=1.0):
    t = T(d); f = hz(m)
    y = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.003 * t) + 0.2 * np.sin(2 * np.pi * f * 1.498 * t)
    env = np.minimum(1, t / 2) * np.minimum(1, (d - t) / 1.5)
    return y * env * 0.035 * g
def boom():
    t = T(1.6); ph = 2 * np.pi * np.cumsum(38 + 60 * np.exp(-t * 8)) / SR
    return np.sin(ph) * np.exp(-t * 2.2) * 0.35
def kick():
    t = T(0.35); ph = 2 * np.pi * np.cumsum(48 + 110 * np.exp(-t * 28)) / SR
    return np.sin(ph) * np.exp(-t * 9) * 0.33
def snare():
    t = T(0.25); return (hp(noise(0.25)) * 0.5 * np.exp(-t * 18) + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.5) * 0.12
def hat(g=1.0): t = T(0.05); return hp(hp(noise(0.05))) * np.exp(-t * 90) * 0.025 * g
def saw(f, t):
    y = np.zeros_like(t)
    for k in range(1, 14): y += np.sin(2 * np.pi * f * k * t) / k * (-1) ** (k + 1)
    return y
def bass(m, d=0.45):
    t = T(d); y = saw(hz(m), t) * 0.6 + np.sin(2 * np.pi * hz(m) * t)
    return y * np.minimum(1, t / 0.004) * np.exp(-t * 4) * 0.09
def stab(ms, d=0.5, g=1.0):
    t = T(d); y = sum(saw(hz(m), t) + saw(hz(m) * 1.004, t) for m in ms)
    y = np.convolve(y, np.ones(6) / 6, 'same')
    return y * np.minimum(1, t / 0.003) * np.exp(-t * 5) * 0.02 * g
def riser(d):
    t = T(d); y = np.convolve(hp(noise(d)), np.ones(3) / 3, 'same') * (t / d) ** 2.5 * 0.07
    f = 200 * (8 ** (t / d)); y += np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 2 * 0.05
    return y
def crash(): t = T(2.2); return hp(hp(noise(2.2))) * np.exp(-t * 2) * 0.05

# ---------- flytrap instruments ----------
def pluck(m, d=0.9, g=1.0):  # Karplus-Strong pizzicato
    f = hz(m); n = int(SR / f); buf = rng.uniform(-1, 1, n); out = np.zeros(int(d * SR))
    for i in range(len(out)):
        out[i] = buf[i % n]; buf[i % n] = 0.5 * (buf[i % n] + buf[(i + 1) % n]) * 0.994
    return out * 0.09 * g
def wood(f=900, g=1.0):  # touch = woodblock
    t = T(0.12); return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.7 * t)) * np.exp(-t * 45) * 0.16 * g
def chomp(g=1.0):
    t = T(0.4); y = np.convolve(noise(0.4), np.ones(30) / 30, 'same') * np.exp(-t * 14) * 1.2
    ph = 2 * np.pi * np.cumsum(90 + 200 * np.exp(-t * 40)) / SR
    return (y + np.sin(ph) * np.exp(-t * 12)) * 0.3 * g
def reed(m, d, g=1.0):  # low bass-clarinet-ish
    t = T(d); f = hz(m)
    y = sum(np.sin(2 * np.pi * f * k * t) / k for k in (1, 3, 5, 7)) * (1 + 0.05 * np.sin(2 * np.pi * 5 * t))
    return y * np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.15) * 0.05 * g
def tick(): t = T(0.03); return hp(noise(0.03)) * np.exp(-t * 200) * 0.03

def zap(d=0.25, g=1.0):  # electric crackle
    t = T(d); y = noise(d) * (rng.random(len(t)) < 0.08) * 3
    y = hp(y) + np.sign(np.sin(2 * np.pi * 120 * t)) * 0.3
    return y * np.exp(-t * 10) * 0.12 * g
def plasma_roar(d=2.0, g=1.0):
    t = T(d); y = np.convolve(noise(d), np.ones(8) / 8, 'same') * (1 + 0.6 * np.sin(2 * np.pi * 60 * t))
    y += (rng.random(len(t)) < 0.01) * noise(d) * 2
    return y * np.minimum(1, t / 0.01) * np.exp(-t * 1.6) * 0.18 * g
def sub_drop():
    t = T(1.8); ph = 2 * np.pi * np.cumsum(30 + 120 * np.exp(-t * 3)) / SR
    return np.sin(ph) * np.exp(-t * 1.5) * 0.4
def wobble(m, d, g=1.0):  # resonance pulse
    t = T(d); f = hz(m)
    y = saw(f, t) * (0.5 + 0.5 * np.sin(2 * np.pi * 8 * t)); y = np.convolve(y, np.ones(10) / 10, 'same')
    return y * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.1) * 0.035 * g
def pop(f): t = T(0.07); return np.sin(2 * np.pi * f * (1 + 2 * t) * t) * np.exp(-t * 60) * 0.1
def arp(m, g=1.0):
    t = T(0.12); y = saw(hz(m), t); y = np.convolve(y, np.ones(4) / 4, 'same'); return y * np.exp(-t * 22) * 0.03 * g
def tom(m, g=1.0):
    t = T(0.3); ph = 2 * np.pi * np.cumsum(hz(m) * (1 + 0.6 * np.exp(-t * 30))) / SR; return np.sin(ph) * np.exp(-t * 10) * 0.2 * g
def hum(d): t = T(d); return (np.sin(2 * np.pi * 60 * t) + 0.5 * np.sin(2 * np.pi * 120 * t)) * 0.03

import film as FM
from cues import L as VO, VODIR
# ---------- new instruments ----------
_ks = {}
def zheng(m, d=1.2, g=1.0):
    key = (m, d)
    if key not in _ks:
        f = hz(m); n = int(SR / f); buf = rng.uniform(-1, 1, n); out = np.zeros(int(d * SR))
        for i in range(len(out)):
            out[i] = buf[i % n]; buf[i % n] = 0.5 * (buf[i % n] + buf[(i + 1) % n]) * 0.998
        t = T(d); _ks[key] = out * np.exp(-t * 2.0) * 0.13
    return _ks[key] * g
def taiko(g=1.0):
    t = T(0.7); ph = 2 * np.pi * np.cumsum(60 + 100 * np.exp(-t * 22)) / SR
    return (np.sin(ph) * np.exp(-t * 6) + hp(noise(0.7)) * np.exp(-t * 45) * 0.35) * 0.45 * g
def k808(m, d=0.6, g=1.0, slide=0):
    t = T(d); f = hz(m) * (1 + 1.5 * np.exp(-t * 35)) * (2 ** (slide * np.minimum(1, t / 0.12) / 12))
    y = np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * 2.2)
    return y * np.exp(-t * 3.2) * np.minimum(1, t / 0.002) * 0.3 * g
def clap(g=1.0):
    t = T(0.3); n = hp(noise(0.3)); env = sum(np.exp(-np.maximum(t - o, 0) * 60) * (t >= o) for o in (0, 0.01, 0.022)) + np.exp(-t * 14) * 0.6
    return np.convolve(n, [0.5, 0.5], 'same') * env * 0.07 * g
def hat16(g=1.0, open_=False):
    d = 0.25 if open_ else 0.045; t = T(d); return hp(hp(noise(d))) * np.exp(-t * (14 if open_ else 110)) * 0.03 * g
def suona(m, d, g=1.0):
    t = T(d); f = hz(m) * (1 + 0.012 * np.sin(2 * np.pi * 6 * t) * np.minimum(1, t / 0.15)) * (1 - 0.03 * np.exp(-t * 30))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = sum(np.sin(k * ph) * a for k, a in ((1, 1), (2, .7), (3, .55), (4, .4), (5, .3), (6, .2), (7, .12)))
    return np.tanh(y * 0.9) * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.05 + 0.0001).clip(0, 1) * 0.045 * g
def gong(d=4.0, g=1.0):
    t = T(d); y = sum(np.sin(2 * np.pi * f * t + 3 * np.sin(2 * np.pi * f * 0.5 * t) * np.exp(-t)) / (k + 1) for k, f in enumerate([110, 163, 237, 311]))
    return y * np.exp(-t * 1.0) * np.minimum(1, t / 0.01) * 0.12 * g
def whoosh(d=1.5, g=1.0):
    t = T(d); y = np.convolve(noise(d), np.ones(30) / 30, 'same'); return y * np.sin(np.pi * t / d) * 0.3 * g
def heart(g=1.0):
    t = T(0.25); return np.sin(2 * np.pi * np.cumsum(45 + 40 * np.exp(-t * 30)) / SR) * np.exp(-t * 14) * 0.35 * g

BPM = 100; B = 60 / BPM; S16 = B / 4
ROOTS_MIN = [38, 34, 36, 33]   # D, Bb, C, A
ROOTS_MAJ = [43, 38, 40, 36]   # G, D, E(m), C  -> brighter after twist
HOOK = [(0, 69, 2), (2, 72, 1), (3, 69, 1), (4, 67, 2), (6, 65, 1), (7, 67, 1), (8, 69, 3), (11, 74, 1), (12, 72, 2), (14, 69, 1), (15, 67, 1),
        (16, 69, 2), (18, 72, 1), (19, 74, 1), (20, 77, 2), (22, 74, 1), (23, 72, 1), (24, 74, 4), (28, 72, 2), (30, 69, 2)]
ZMEL = [62, 65, 67, 69, 72, 69, 67, 65, 62, 65, 67, 72, 74, 72, 69, 67]

def section(t):
    """returns mode for groove at time t"""
    if t < FM.B0: return "drop"
    if t < FM.B_FIRE: return "mystery"
    if t < FM.C_Q - 0.1: return "groove"
    if t < FM.C_MERGE + 0.8: return "build"
    if t < FM.D_JAIL: return "groove"
    if t < FM.D_JAIL + 1.2: return "stop"
    if t < FM.E0: return "half"
    if t < FM.E_TWIST: return "half"
    if t < FM.E_TWIST + 0.7: return "stop"
    if t < FM.F0: return "bright"
    if t < FM.F_TFR: return "heart"
    if t < FM.F_ALL + 2.4: return "rise"
    if t < FM.G0: return "drop"
    return "outro"

kick_times = []
step = 0; t = 0.0
while t < DUR - 2.2:
    m = section(t)
    bar = step // 16; pos = step % 16
    roots = ROOTS_MAJ if m == "bright" else ROOTS_MIN
    root = roots[bar % 4]
    if m in ("drop", "outro"):
        if pos in (0, 6, 10) or (pos == 14 and bar % 2): add(k808(root, 0.5 if pos else 0.9, 1.0, slide=(-5 if pos == 14 else 0)), t); kick_times.append(t)
        if pos in (4, 12): add(clap(1.1), t); add(taiko(0.6), t)
        if pos % 2 == 0 or (bar % 2 and pos in (13, 15)): add(hat16(0.9 if pos % 4 == 0 else 0.55), t, 1, 0.25)
        if pos == 14: add(hat16(0.6, True), t, 1, -0.25)
        if pos % 2 == 0: add(zheng(ZMEL[(step // 2) % 16] + 12, 0.6, 0.35), t, 1, -0.35)
    elif m == "groove":
        if pos in (0, 10): add(k808(root, 0.6, 0.8), t); kick_times.append(t)
        if pos in (4, 12): add(clap(0.7), t)
        if pos % 2 == 0: add(hat16(0.6 if pos % 4 == 0 else 0.35), t, 1, 0.25)
        if pos in (0, 3, 6, 8, 11, 14): add(zheng(ZMEL[(step // 2 + bar) % 16], 1.0, 0.55), t, 1, -0.3)
        if pos == 0: add(taiko(0.5), t)
    elif m == "half":
        if pos == 0: add(k808(root, 1.0, 0.8), t); kick_times.append(t); add(taiko(0.5), t)
        if pos == 8: add(clap(0.8), t)
        if pos % 2 == 0: add(hat16(0.45 if pos % 4 == 0 else 0.25), t, 1, 0.25)
        if pos in (0, 6, 12): add(zheng(ZMEL[(step // 3) % 16], 1.2, 0.5), t, 1, -0.3)
    elif m == "bright":
        if pos in (0, 7, 10): add(k808(root, 0.5, 0.8), t); kick_times.append(t)
        if pos in (4, 12): add(clap(0.8), t)
        add(hat16(0.5 if pos % 2 == 0 else 0.25), t, 1, 0.25)
        if pos % 2 == 0: add(zheng([67, 71, 74, 76, 79, 76, 74, 71][(step // 2) % 8], 0.8, 0.45), t, 1, -0.3)
    elif m == "mystery":
        if pos == 0: add(taiko(0.45), t); add(k808(26 + 12, 1.4, 0.5), t)
        if pos == 8 and bar % 2: add(taiko(0.25), t)
        if pos in (0, 5, 10): add(zheng([62, 63, 67, 69, 70, 69][(step // 5) % 6], 1.6, 0.45), t, 1, -0.2)
    elif m == "build":
        k = (t - FM.C_Q) / (FM.C_MERGE + 0.8 - FM.C_Q)
        if t > FM.C_ONE:
            div = 4 if k < 0.5 else (2 if k < 0.8 else 1)
            if pos % div == 0: add(taiko(0.3 + 0.6 * k), t); add(hat16(0.3 + 0.5 * k), t)
    elif m == "heart":
        if pos in (0, 3): add(heart(0.9 if pos == 0 else 0.6), t)
    elif m == "rise":
        k = cl_ = min(1, max(0, (t - FM.F_TFR) / (FM.F_ALL + 2.4 - FM.F_TFR)))
        if pos in (0, 3) : add(heart(0.8 + 0.4 * k), t)
        div = 4 if k < 0.4 else (2 if k < 0.75 else 1)
        if pos % div == 0: add(hat16(0.3 + 0.6 * k), t); 
        if pos % 4 == 0 and k > 0.3: add(taiko(0.3 + 0.7 * k), t)
        if pos == 0: add(zheng(62 + int(k * 10), 1.2, 0.6), t)
    step += 1; t += S16

# lead hook (suona) in drop sections only, gaps of voice preferred
def hook(t0, t1, g=1.0):
    k = 0
    while t0 + k * 32 * S16 < t1:
        for st, m, ln in HOOK:
            tt = t0 + (k * 32 + st) * S16
            if tt < t1 - 0.05: add(suona(m, ln * S16 * 0.95, g), tt, 1, 0.1)
        k += 1
hook(FM.H_BOOM + 0.0, FM.B0, 0.9)
hook(FM.F_ALL + 2.4, FM.G0, 1.0)
hook(FM.G0 + 0.0, DUR - 3.0, 0.7)
# pads
for a, b, ms in ((FM.B0, FM.C0, (50, 57)), (FM.D0, FM.E0, (50, 57)), (FM.E_TWIST + 0.7, FM.F0, (55, 62)), (FM.F_TFR, FM.F_ALL + 2.4, (50, 57, 62))):
    for mm in ms: add(drone(mm, b - a, 0.8), a)
add(riser(FM.F_ALL + 2.4 - FM.F_TFR), FM.F_TFR, 1.6)
# hits
def big(t0, g=1.0): add(boom(), t0, g); add(gong(4, g), t0); add(crash(), t0, g)
big(FM.H_BOOM, 1.3); add(whoosh(0.5, 1.5), 0.0)
add(stab([50, 57, 62], 0.6, 1.3), FM.H_NUM - 0.2); add(boom(), FM.H_NUM - 0.2, 0.8)
for i in range(6): add(pclick(1500 - 120 * i, 0.08, 0.8), FM.H_GONE + i * 0.12)
add(gong(3, 0.6), FM.B_GIRL)
add(whoosh(1.4, 1.5), FM.B_FIRE - 0.6); big(FM.B_FIRE, 1.0)
add(gong(2.5, 0.6), FM.B_STAGE)
for i in range(5): add(pop(600 + 110 * i), FM.B_RUM + 0.5 + i * 0.3)
for i in range(3): add(wood(900 + 200 * i), FM.C_Q + 0.12 * i)
add(zheng(74, 1.6, 1.3), FM.C_ONE); add(zheng(79, 1.6, 1.3), FM.C_ONE + 1.7)
add(riser(1.8), FM.C_MERGE - 1.0); big(FM.C_MERGE + 0.8, 1.1); add(stab([50, 57, 62, 66], 0.8, 1.2), FM.C_MERGE + 0.8)
add(stab([50, 57, 62], 0.5, 1.0), FM.D_JIE + 2.0); add(taiko(1.2), FM.D_JIE + 2.0)
for k in range(21): add(wood(700 + 18 * k, 0.5), FM.D_JIE + 2.2 + k * 2.5 / 21)
add(boom(), FM.D_JAIL, 1.0); add(taiko(1.4), FM.D_JAIL); add(clap(1.5), FM.D_JAIL)
add(taiko(1.3), FM.D_SEAL); add(wood(400, 1.6), FM.D_SEAL); add(crash(), FM.D_SEAL, 0.5)
add(stab([49, 56, 61], 0.6, 1.2), FM.E_BAR + 2.3); add(boom(), FM.E_BAR + 2.3, 0.9)
add(riser(0.7), FM.E_TWIST - 0.7); add(gong(3, 1.0), FM.E_TWIST + 0.7); add(stab([55, 62, 67, 71], 0.8, 1.2), FM.E_TWIST + 0.7)
for i in range(12): add(pop(900 + 50 * i), FM.E_SHIFT + 1.2 + i * 0.12)
add(stab([55, 59, 62, 67], 0.6, 1.0), FM.E_SHIFT + 2.5)
add(zheng(79, 1.5, 1.0), FM.F_NOW + 1.6); add(wood(500, 1.0), FM.F_EMPTY + 1.0); add(boom(), FM.F_EMPTY + 1.0, 0.6)
add(sub_drop(), FM.F_ALL + 2.4); big(FM.F_ALL + 2.4, 1.4); add(stab([50, 57, 62, 65], 0.9, 1.4), FM.F_ALL + 2.4)
for j in range(12): add(pclick(1200 + 60 * j, 0.06, 0.6), FM.F_ALL + j * 2.2 / 12)
for mm in (50, 57, 62, 65, 69): add(piano(mm, 3.2, 1.1), DUR - 3.2)
add(gong(3.2, 1.0), DUR - 3.2)

# sidechain on kicks
sc = np.ones(N)
for kt in kick_times:
    i = int(kt * SR); n = int(0.18 * SR)
    if i < N: sc[i:i + n] = np.minimum(sc[i:i + n], 0.55 + 0.45 * (np.arange(min(n, N - i)) / n))
def reverb(x):
    n = int(1.6 * SR); tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt * 3.8); ir = np.convolve(ir, np.ones(5) / 5, 'same'); ir /= np.abs(ir).sum() ** 0.5 * 14
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x * 0.88 + np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)] * 0.4
LL = reverb(LL); R = reverb(R)
st = np.stack([LL, R], 1)
st = np.tanh(st / np.abs(st).max() * 1.6); st /= np.abs(st).max() / 0.9
v = np.zeros(N)
for i, (a, b) in enumerate(VO):
    w = wave.open(f'{VODIR}/{i + 1}.wav'); x = np.frombuffer(w.readframes(w.getnframes()), '<i2') / 32768
    j = int(a * SR); v[j:j + len(x)] += x[: N - j]
env = np.convolve((np.abs(v) > 0.01).astype(float), np.ones(int(0.3 * SR)) / int(0.3 * SR), 'same')
duck = 1 - 0.45 * np.clip(env * 3, 0, 1)
mixd = st * duck[:, None] * 0.62 + v[:, None] * 1.0
mixd /= np.abs(mixd).max() / 0.95
with wave.open('mix.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mixd * 32767).astype('<i2').tobytes())
with wave.open('bgm_only.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 0.9 * 32767).astype('<i2').tobytes())
print('ok', N / SR, len(kick_times))
