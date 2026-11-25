import numpy as np, wave
from cues import *
SR = 44100; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def T(d): return np.arange(int(d * SR)) / SR
def add(sig, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i < 0: return
    s = sig[: N - i] * g
    L[i:i + len(s)] += s * (1 - max(pan, 0)); R[i:i + len(s)] += s * (1 + min(pan, 0))
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

def tom(m, g=1.0):
    t = T(0.3); ph = 2 * np.pi * np.cumsum(hz(m) * (1 + 0.6 * np.exp(-t * 30))) / SR
    return np.sin(ph) * np.exp(-t * 10) * 0.2 * g
def shimmer(d):
    t = T(d); return hp(hp(noise(d))) * 0.012 * np.minimum(1, t / 0.5) * np.minimum(1, (d - t) / 0.5)
def pop(f): t = T(0.07); return np.sin(2 * np.pi * f * (1 + 2 * t) * t) * np.exp(-t * 60) * 0.1
def arp(m, g=1.0):
    t = T(0.12); y = saw(hz(m), t); y = np.convolve(y, np.ones(4) / 4, 'same')
    return y * np.exp(-t * 22) * 0.03 * g
def shaker(d=0.6, g=1.0):
    t = T(d); return hp(hp(noise(d))) * (0.5 + 0.5 * np.sin(2 * np.pi * 18 * t)) * np.exp(-t * 3) * 0.06 * g
def thud(g=1.0): add(kick(), 0, 0)  # placeholder
def drop_hit(t0, g=1.0):
    add(kick(), t0, 1.0 * g); add(wood(420, 0.9 * g), t0); add(tom(40, 0.6 * g), t0)
def fold_gliss(t0, g=1.0, up=False):
    seq = [84, 81, 79, 76, 74, 72] if not up else [72, 74, 76, 79, 81, 84]
    for i, m in enumerate(seq): add(pluck(m, 0.5, 0.7 * g), t0 + i * 0.03, 1, 0.4 if i % 2 else -0.4)
def bell(m, d=1.5, g=1.0):
    t = T(d); f = hz(m)
    y = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3) + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 6)
    return y * np.exp(-t * 2.5) * np.minimum(1, t / 0.002) * 0.05 * g

def didge(m, d, g=1.0):
    t = T(d); f = hz(m)
    y = saw(f, t) * (0.6 + 0.4 * np.sin(2 * np.pi * 3.0 * t)) ; y = np.convolve(y, np.ones(10) / 10, 'same')
    return y * np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.4) * 0.05 * g
def revsweep(d):
    y = riser(d); return y
def buzz(d, g=1.0):
    t = T(d); y = saw(140 + 20 * np.sin(2 * np.pi * 6 * t), t) * (0.5 + 0.5 * np.sin(2 * np.pi * 30 * t))
    return y * np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.3) * 0.02 * g
def bubble(f): t = T(0.12); return np.sin(2 * np.pi * np.cumsum(f * (1 + 3 * t)) / SR) * np.exp(-t * 30) * 0.07

PROG = [40, 36, 43, 38]   # E C G D (E minor-ish)
MOT = [64, None, 67, 71, 69, None, 67, 64]
def groove(t0, t1, g=1.0, shift=0, half=False, stabs=True):
    nb = int((t1 - t0) / BEAT + 1e-6)
    for b in range(nb):
        tb = t0 + b * BEAT; root = PROG[(b // 4) % 4]
        if half:
            if b % 4 == 0: add(kick(), tb, 0.9 * g)
            if b % 4 == 2: add(snare(), tb, g)
        else:
            add(kick(), tb, (0.9 if b % 2 == 0 else 0.6) * g)
            if b % 2 == 1: add(snare(), tb, g)
        add(hat(1.0), tb + 0.25, g); add(hat(0.5), tb, g)
        add(bass(root if b % 4 != 3 else root + 7), tb, g)
        m = MOT[b % 8]
        add(pluck((m if m else root + 31) + shift, g=0.7 * g), tb + 0.25, pan=0.3)
        if stabs and b % 4 == 0: add(stab([root + 24, root + 27 if root in (40, 38) else root + 28, root + 31], d=1.2, g=0.5 * g), tb)
def hit(t0, g=1.0, chord=(52, 59, 64, 67, 71)):
    add(boom(), t0, g); add(crash(), t0, g); add(kick(), t0, g); add(stab(list(chord), d=1.0, g=1.4 * g), t0)

# HOOK
add(wood(1100), 0.0); hit(MORPH, 1.2); fold = None
for k in range(5):
    tk = MORPH + 0.5 + k * BEAT; add(kick(), tk); add(bass(40), tk)
    if k % 2: add(snare(), tk)
add(stab([64, 67, 71, 76], d=0.9, g=1.0), 2.5)
# TREE: lab arps
for b in range(int((MASTO - TREE0) / 0.25)):
    tb = TREE0 + b * 0.25
    add(arp([64, 71, 67, 74][b % 4] + (0 if tb < TERM_IN else 2), 0.7), tb, pan=0.3 if b % 2 else -0.3)
    if b % 4 == 0 and tb >= GROW[0]: add(kick(), tb, 0.6); add(bass(40 if tb < 8 else 43), tb)
    if b % 8 == 4 and tb >= GROW[0]: add(snare(), tb, 0.6)
add(drone(40, 11, 1.0), TREE0)
add(bell(88, 1.0), TERM_IN); add(stab([64, 68, 71], g=1.0), STAMP1); add(riser(1.2), 10.8); hit(ORDER_X, 1.0)
# MASTO: didgeridoo + toms
add(didge(28, 8.5, 1.4), MASTO); add(didge(28, 5.5, 1.4), XRAY)
for b in range(int((REW - MASTO) / BEAT)):
    tb = MASTO + b * BEAT
    add(tom([45, 40, 43, 40][b % 4], 0.8), tb); add(hat(0.6), tb + 0.25)
    if b % 4 == 0: add(kick(), tb, 0.7)
    if tb >= EGG: add(pluck(MOT[b % 8] - 12 if MOT[b % 8] else 52, g=0.7), tb + 0.25)
add(stab([64, 67, 71], g=1.2), SAME); add(bell(83, 1.0), SAME); add(riser(1.0), 21.5)
hit(XRAY, 0.9, (52, 59, 64, 66, 71)); add(shimmer(5.0), XRAY)
for k in range(12): add(bubble(600 + 90 * k), XRAY + 0.8 + k * 0.4, pan=np.sin(k) * 0.5)
# REWIND 1: ticks accelerating + reverse risers
for k in range(30):
    tk = REW + 4.3 * (1 - (1 - k / 30) ** 1.7); add(tick(), tk, 2.0); add(wood(800 + 30 * k, 0.4), tk)
add(riser(4.0), REW + 0.3); add(drone(40, 4.5), REW)
# DINO: heavy footsteps
for k in range(5): add(boom(), DINO + k * 0.5, 0.35); add(tom(31, 1.0), DINO + k * 0.5)
add(riser(1.5), 33.5)
hit(IMPACT, 1.6, (40, 47, 52, 55, 59)); add(boom(), IMPACT + 0.1, 1.0); add(crash(), IMPACT + 0.2, 1.4)
add(drone(40, 5.0, 1.2), IMPACT)
add(stab([64, 68, 71, 76], d=1.0, g=1.4), SURVIVE); add(bell(88, 1.0), SURVIVE)
groove(SURVIVE + 0.5, REW2, 0.9)
# REWIND 2
for k in range(24):
    tk = REW2 + 3.3 * (1 - (1 - k / 24) ** 1.7); add(tick(), tk, 2.0); add(wood(900 + 40 * k, 0.4), tk)
add(riser(3.3), REW2 + 0.3)
add(stab([64, 67, 71, 74], d=1.0, g=1.3), 43.6); add(bell(84, 1.2), 43.6); add(bell(91, 1.2), 43.9)
# BACT: bubbly half-time
groove(BACT, EGGS2 - 1.0, 0.8, half=True, stabs=False)
for k in range(30): add(bubble(500 + 70 * (k % 9)), BACT + k * 0.2, pan=np.sin(k * 1.7) * 0.6)
for k in range(10): add(bell(76 + [0, 3, 7, 10, 12][k % 5], 0.6, 0.6), RECYCLE + 0.5 + k * 0.1)
hit(GLU, 0.8, (52, 59, 64, 67, 71)); add(riser(1.0), 51.0)
for k in range(16): add(pop(1200 + 60 * k), EGGS2 + 0.3 + k * (PASS - EGGS2 - 0.3) / 16)
hit(PASS, 1.0, (48, 55, 60, 64, 67)); groove(PASS + 0.5, 57.0, 1.0, shift=0)
add(riser(1.0), 57.0)
# CARB: deep pads + buzz
hit(CARB, 1.0, (40, 47, 52, 55, 59)); add(drone(28, 8.0, 1.5), CARB); add(drone(40, 8.0, 1.0), CARB)
groove(CARB + 1.0, BIGFLY, 0.7, half=True)
add(buzz(3.2, 1.5), BIGFLY); hit(BIGFLY, 0.8)
groove(BIGFLY + 0.5, OUTRO, 1.0, shift=2)
# OUTRO
add(crash(), OUTRO, 0.6)
for m in (40, 52, 55, 59, 64): add(piano(m, 5.0, 1.5), OUTRO)
for i, m in enumerate([64, 67, 71, 76]): add(bell(m, 1.4, 0.7), OUTRO + 0.6 + i * 0.4)
add(reed(40, 5.5), OUTRO); add(wood(1000), LAST - 0.3); add(boom(), LAST, 0.6); add(stab([52, 59, 64], d=0.8), LAST)

def reverb(x):
    n = int(1.5 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 4); ir = np.convolve(ir, np.ones(5) / 5, 'same'); ir /= np.abs(ir).sum() ** 0.5 * 14
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x * 0.85 + np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)] * 0.45
L = reverb(L); R = reverb(R)
st = np.stack([L, R], 1)
for a, b in SILENCES: st[int(a * SR):int(b * SR)] *= 0.0
st = np.tanh(st / np.abs(st).max() * 2.2)
st /= np.abs(st).max() / 0.85
with wave.open('bgm.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
