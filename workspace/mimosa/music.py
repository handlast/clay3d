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

CMOTIF = [72, None, 76, 79, 77, None, 76, 72]
PROG = [36, 41, 43, 45]
def groove(t0, t1, full=True, g=1.0, motif_shift=0):
    nb = int((t1 - t0) / BEAT + 1e-6)
    for b in range(nb):
        tb = t0 + b * BEAT; root = PROG[(b // 4) % 4]
        add(kick(), tb, (0.9 if b % 2 == 0 else 0.6) * g)
        if b % 2 == 1: add(snare(), tb, g)
        add(hat(1.0), tb + 0.25, g); add(hat(0.5), tb, g)
        add(bass(root if b % 4 != 3 else root + 7), tb, g)
        m = CMOTIF[b % 8]
        add(pluck((m if m else root + 31) + motif_shift, g=0.7 * g), tb + 0.25, pan=0.3)
        if full and b % 4 == 0: add(stab([root + 24, root + 28, root + 31], d=1.2, g=0.6 * g), tb)

# HOOK
drop_hit(HOOK_DROP, 1.4); add(boom(), HOOK_DROP); add(crash(), HOOK_DROP, 1.2); fold_gliss(HOOK_DROP + 0.02, 1.2)
for k in range(4):
    tk = HOOK_DROP + 0.38 + k * BEAT; add(kick(), tk); add(bass(36 if k < 3 else 43), tk)
    if k % 2: add(snare(), tk)
    add(stab([60, 64, 67], g=1.1 if k == 0 else 0.6), tk)
add(stab([60, 64, 67, 72], d=0.9, g=1.2), 2.0); fold_gliss(1.6, 0.6, up=True)

# 2.6-8.5 playful pizzicato
for b in range(int((MACH - 3.0) / BEAT)):
    t0 = 3.0 + b * BEAT; m = CMOTIF[b % 8]
    if t0 >= SUNLOSS: m = [72, None, 70, None, 67, None, 63, None][b % 8]
    if m: add(pluck(m - 12, g=0.9), t0, 1, -0.2 if b % 2 else 0.2)
    add(tick(), t0, 1, 0.4)
add(wood(1300, 1.0), POKE); fold_gliss(POKE, 1.2); add(stab([60, 64, 67], g=0.8), POKE)
for i, m in enumerate([67, 64, 60, 55]): add(piano(m, 1.5, 1.1), SUNLOSS + i * 0.18)
add(reed(36, 2.4), SUNLOSS)

# 8.5-19.5 drop machine
add(reed(36, 5.5), MACH); add(reed(38, 4.5), FAST0)
add(bell(79, 1.2, 1.0), MACH)
for i, h in enumerate(SLOW):
    drop_hit(h, 1.1)
    k = i + 1
    r = 1.0 if k <= 3 else max(0, 1 - (k - 3) / 10)
    if r > 0.05: fold_gliss(h + 0.02, r)
    add(pluck(60 + [0, 2, 4, 5, 7, 9][i], g=1.0), h + 0.25, pan=0.2)
for i, h in enumerate(FAST):
    add(wood(700 + 22 * i, 0.55), h, pan=0.3 if i % 2 else -0.3); add(hat(0.8), h)
    if i % 4 == 0: add(kick(), h, 0.7)
    if i % 2 == 0: add(arp(72 + (i // 4), 0.8), h + 0.06)
add(riser(RISER[1] - RISER[0]), RISER[0])

# BURST 20-23.5
add(boom(), BURST); add(crash(), BURST, 1.3); add(stab([48, 55, 60, 64, 67, 72], d=1.2, g=1.6), BURST); drop_hit(BURST, 1.3)
for i in range(4): add(bell(84 + [0, 4, 7, 12][i], 1.0, 0.8), BURST + 0.8 + i * 0.25)
groove(BURST, SHAKE, True, 1.0)
# SHAKE
add(shaker(0.9, 1.6), SHAKE); fold_gliss(SHAKE + 0.1, 1.3)
add(boom(), NOTTIRED, 0.7); add(stab([55, 59, 62, 67], d=0.8, g=1.3), NOTTIRED)
groove(NOTTIRED + 0.4, CAL0, False, 0.7)

# CAL 26-31.5 breakdown: day ticks
add(shimmer(5.5), CAL0); add(drone(48, 5.5, 1.0), CAL0); add(drone(55, 5.5, 0.8), CAL0)
for k in range(27):
    tk = CAL0 + 0.6 + (CAL1 - CAL0 - 0.6) * (k / 27) ** 0.8
    add(bell(72 + [0, 4, 7, 12, 7, 4][k % 6], 0.8, 0.6), tk, pan=0.3 if k % 2 else -0.3)
add(riser(1.0), CAL1)
add(boom(), DAY28); add(crash(), DAY28, 1.2); drop_hit(DAY28, 1.3); add(stab([48, 55, 60, 64, 67], d=1.0, g=1.5), DAY28)
groove(DAY28 + 0.5, DARK, True, 1.0, motif_shift=2)

# DARK 35-39 half-time
for b in range(8):
    tb = DARK + b * BEAT
    if b % 4 == 0: add(kick(), tb, 0.8)
    if b % 4 == 2: add(snare(), tb, 0.7)
    add(hat(0.4), tb + 0.25)
    add(pluck([69, 72, 76, 72, 74, 77, 81, 77][b] - 12, g=0.8), tb, pan=-0.3 if b % 2 else 0.3)
add(drone(45, 4.0, 0.9), DARK); add(bell(84, 1.0), DARK + 1.4); add(bell(88, 1.0), DARK + 1.8)

# OUTRO
add(crash(), OUTRO, 0.6)
for m in (48, 60, 64, 67, 72): add(piano(m, 4.5, 1.5), OUTRO)
add(reed(36, 4.5), OUTRO)
for i, m in enumerate([72, 76, 79, 84]): add(bell(m, 1.4, 0.7), OUTRO + 0.6 + i * 0.4)
drop_hit(LAST, 1.1); add(boom(), LAST, 0.6); fold_gliss(LAST + 0.6, 0.5, up=True)

def reverb(x):
    n = int(1.5 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 4); ir = np.convolve(ir, np.ones(5) / 5, 'same'); ir /= np.abs(ir).sum() ** 0.5 * 14
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x * 0.85 + np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)] * 0.45
L = reverb(L); R = reverb(R)
st = np.stack([L, R], 1)
st[int(SILENCE[0] * SR):int(SILENCE[1] * SR)] *= 0.0
a, b, c = int(2.45 * SR), int(2.6 * SR), int(3.0 * SR)
env = np.ones(N); env[a:b] = np.linspace(1, 0.05, b - a); env[b:c] = np.linspace(0.05, 1, c - b) ** 3
st *= env[:, None]
st = np.tanh(st / np.abs(st).max() * 2.2)
st /= np.abs(st).max() / 0.85
with wave.open('bgm.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
