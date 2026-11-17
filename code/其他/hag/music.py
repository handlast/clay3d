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

def squelch(g=1.0):
    t = T(0.35); f = 180 + 500 * np.exp(-t * 12)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 0.18 + np.convolve(noise(0.35), np.ones(60) / 60, 'same') * np.exp(-t * 10) * 0.3) * g
def gulp(): t = T(0.18); return np.sin(2 * np.pi * np.cumsum(500 - 1800 * t) / SR) * np.exp(-t * 18) * 0.12
PROG = [38, 35, 40, 33]  # 宫 羽 商 徵 (D gong pentatonic: D E F# A B)
CH = {38: (50, 57, 62, 64, 69), 35: (47, 54, 59, 62, 66), 40: (52, 59, 64, 66, 71), 33: (45, 52, 57, 59, 64)}
PENTA = [62, 64, 66, 69, 71, 74, 76, 78, 81, 83, 86]
def zheng(t0, up=True, g=1.0, n=11):
    seq = PENTA[:n] if up else PENTA[:n][::-1]
    for k, mm in enumerate(seq): add(pluck(mm, 1.2, 0.8 * g), t0 + k * 0.035, pan=-0.5 + k / n)
MOT = [74, 76, 81, None, 78, 76, 74, 71]
def groove(t0, t1, g=1.0, half=False):
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
        add(bass(root), tb, g)
        if b % 4 == 0: add(stab(list(CH[root][1:4]), d=1.6, g=0.35 * g), tb, 0.0)
        m = MOT[b % 8]
        add(pluck(m if m else root + 31, g=0.7 * g), tb + 0.25, pan=0.3)
def hit(t0, g=1.0, chord=(50, 57, 62, 64, 69)):
    add(boom(), t0, g); add(crash(), t0, g); add(kick(), t0, g); add(stab(list(chord), d=0.9, g=1.3 * g), t0)
hit(BURST, 1.2); add(squelch(1.5), BURST); zheng(BURST + 0.05)
for k in range(5): add(bubble(300 + 90 * k), BURST + 0.1 + k * 0.08)
groove(1.0, NOJAW - 0.5, 0.8)
add(stab([47, 54, 59], d=0.5), NOTEEL); add(wood(600), NOTEEL + 0.25)
hit(NOJAW, 0.9, (47, 54, 59, 62, 66)); add(gulp(), NOJAW + 0.1)
groove(SHARK, BITE - 1.0, 0.7, half=True); add(riser(1.5), 8.0)
add(chomp(1.5), BITE); hit(BITE, 0.8, (52, 59, 64, 66, 71))
add(squelch(1.6), SLIME_IN); hit(SLIME_IN, 1.0)
for k in range(8): add(bubble(250 + 50 * k), SLIME_IN + 0.3 + k * 0.15, pan=np.sin(k) * 0.6)
add(gulp(), SPIT); add(gulp(), SPIT + 0.2); hit(SPIT, 0.7)
groove(SPIT + 0.5, VOL, 0.9)
add(wood(1000), PINCH)
for k in range(14): add(bubble(200 + 40 * k), FILL[0] + k * (FILL[1] - FILL[0]) / 14)
groove(VOL, SEVEN, 0.7, half=True); hit(SEVEN, 1.0); zheng(SEVEN, n=6); add(bell(81, 1.0), SEVEN); groove(SEVEN + 0.5, STUCK, 0.9)
add(drone(38, 3.0), STUCK); add(reed(38, 3.0), STUCK)
for k in range(6): add(tom(45 - k, 0.8), STUCK + 1.5 + k * 0.17)
add(riser(0.5), 22.0)
zheng(KNOT); hit(KNOT, 1.4, (50, 57, 62, 64, 66, 69, 74))
for b in range(int((SLIDE[1] - SLIDE[0]) / 0.125)): add(arp(PENTA[(b % 8) + (b // 8) % 3], 0.6), SLIDE[0] + b * 0.125)
add(squelch(1.0), CLEAN); zheng(CLEAN, up=False); hit(CLEAN, 1.2, (50, 57, 62, 64, 69, 76)); add(bell(86, 1.0), CLEAN); groove(CLEAN + 0.5, FEED, 1.0)
groove(FEED, KNOT2, 0.7, half=True); add(chomp(1.5), CHOMP); add(stab([50, 57], g=0.8), CHOMP)
add(riser(1.0), 32.0)
for k in range(6): add(tom(50 + k, 0.7), KNOT2 + 0.6 + k * 0.18)
hit(TEAR, 1.1); add(squelch(1.0), TEAR); groove(TEAR + 0.5, TRUCK, 1.0)
groove(TRUCK, FLIP - 0.5, 0.8)
add(riser(1.5), 36.0); add(revsweep(0.5), FLIP - 0.5)
hit(FLIP, 1.2, (47, 54, 59, 62, 66)); add(boom(), FLIP + 0.3, 0.7)
add(squelch(1.8), SPLAT); zheng(SPLAT, up=False); hit(SPLAT, 1.3)
for k in range(10): add(bubble(200 + 60 * k), SPLAT + 0.2 + k * 0.1, pan=np.sin(k) * 0.6)
groove(SPLAT + 0.5, OUTRO, 1.0)
add(crash(), OUTRO, 0.5)
for m in (38, 50, 57, 62, 64): add(piano(m, 4.5, 1.3), OUTRO)
for k, mm in enumerate((62, 64, 66, 69, 71, 74)): add(pluck(mm, 1.5, 1.0), BUB1 + 0.5 + k * 0.5, pan=0.2)
for t0 in (BUB1, BUB2, BUB2 + 1.0, BUB2 + 1.8): add(pop(1300), t0, 1.5); add(pop(1700), t0 + 0.05, 1.0)
add(reed(38, 5.5), OUTRO); add(boom(), LAST, 0.5); add(stab([50, 57, 62], d=0.8), LAST)

def reverb(x):
    n = int(1.4 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 4); ir = np.convolve(ir, np.ones(5) / 5, 'same'); ir /= np.abs(ir).sum() ** 0.5 * 14
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x * 0.85 + np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)] * 0.45
L = reverb(L); R = reverb(R)
st = np.stack([L, R], 1)
for a, b in SILENCES: st[int(a * SR):int(b * SR)] *= 0.0
st = np.tanh(st / np.abs(st).max() * 2.2); st /= np.abs(st).max() / 0.85
with wave.open('bgm.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
