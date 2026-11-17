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

# HOOK 0-2.6
for tk in HOOK_TOUCH: add(wood(1000), tk)
add(chomp(1.6), HOOK_SNAP); add(boom(), HOOK_SNAP); add(crash(), HOOK_SNAP, 1.2); add(kick(), HOOK_SNAP)
for k in range(4):
    tk = HOOK_SNAP + k * BEAT; add(kick(), tk); add(bass(40 if k < 3 else 43), tk)
    if k % 2: add(snare(), tk)
    add(stab([64, 67, 71], g=1.1 if k == 0 else 0.6), tk)
add(stab([60, 64, 67, 72], d=0.9, g=1.2), 2.0)

# sneaky part 2.6-19.5 : E minor pizzicato + clock
motif = [52, None, 55, None, 59, None, 58, 55]  # E G B Bb G
for b in range(int((19.5 - 3.0) / BEAT)):
    t0 = 3.0 + b * BEAT; m = motif[b % 8]
    if m is not None: add(pluck(m + (0 if t0 < 12 else 1 if t0 < 14 else 2 if t0 < 16.5 else 3)), t0, 1.0, -0.2 if b % 2 else 0.2)
    add(tick(), t0, 1, 0.4)
for t0, m, d in ((3.0, 40, 4.0), (7.0, 43, 2.5), (9.5, 40, 2.5), (12.0, 41, 2.0), (14.0, 42, 2.5), (16.5, 43, 3.0)): add(reed(m, d), t0)
for tk in [T1] + T2 + [T3, T4] + WIND: add(wood(900), tk)
add(pluck(47, g=0.6), FORGET); add(pluck(46, g=0.6), FORGET + 0.3)
add(chomp(1.3), SNAP2); add(kick(), SNAP2); add(stab([64, 67, 71], g=0.8), SNAP2)
add(stab([65, 68, 72], g=0.7), T3); add(stab([66, 69, 73], g=0.8), T4)
for k in range(12):  # heartbeat accelerating 14-19.5
    tk = 14.0 + 5.3 * (1 - (1 - k / 12) ** 1.6)
    add(kick(), tk, 0.5); add(kick(), tk + 0.15, 0.3)
add(riser(RISER[1] - RISER[0]), RISER[0])

# BURST 20-39
add(chomp(2.0), BURST); add(boom(), BURST); add(crash(), BURST, 1.3); add(stab([52, 59, 64, 67, 71], d=1.0, g=1.6), BURST)
prog = [40, 40, 36, 38]
def arp(m, g=1.0):
    t = T(0.12); y = saw(hz(m), t); y = np.convolve(y, np.ones(4) / 4, 'same')
    return y * np.exp(-t * 22) * 0.03 * g
def tom(m, g=1.0):
    t = T(0.3); ph = 2 * np.pi * np.cumsum(hz(m) * (1 + 0.6 * np.exp(-t * 30))) / SR
    return np.sin(ph) * np.exp(-t * 10) * 0.2 * g
def shimmer(d):
    t = T(d); return hp(hp(noise(d))) * 0.012 * np.minimum(1, t / 0.5) * np.minimum(1, (d - t) / 0.5)
def pop(f): t = T(0.07); return np.sin(2 * np.pi * f * (1 + 2 * t) * t) * np.exp(-t * 60) * 0.1
for b in range(int((OUTRO - BURST) / BEAT)):
    t0 = BURST + b * BEAT; bar = int(b // 4); root = prog[bar % 4]
    if t0 < 24.0 or t0 >= 35.0:          # full groove
        add(kick(), t0, 0.9 if b % 2 == 0 else 0.6)
        if b % 2 == 1: add(snare(), t0)
        add(hat(1.0), t0 + 0.25); add(hat(0.6), t0)
        add(bass(root if b % 4 != 3 else root + 7), t0)
        add(pluck(motif[b % 8] + 12 if motif[b % 8] else root + 24, g=0.7), t0 + 0.25, pan=0.3)
        if b % 4 == 0: add(stab([root + 24, root + 27 if root in (40, 38) else root + 28, root + 31], d=1.2, g=0.6), t0)
    elif t0 < 30.0:                      # breakdown: rain & wind, no drums
        if b % 2 == 0: add(pluck(motif[b % 8] + 12 if motif[b % 8] else 64, g=0.8), t0, pan=-0.3)
        if b % 4 == 0: add(reed(root, 1.9, 0.8), t0)
        add(hat(0.25), t0 + 0.25)
    else:                                # build: four-on-floor + rising 16th arps
        add(kick(), t0, 0.9); add(hat(0.8), t0 + 0.25); add(bass(root), t0)
        if b % 2 == 1: add(snare(), t0, 0.7)
        step = int((t0 - 30.0) / 1.0)
        for k in range(4):
            add(arp([64, 67, 71, 76][k] + step, 0.9), t0 + k * 0.125, pan=0.4 if k % 2 else -0.4)
add(shimmer(6.0), 24.0, 1.0)
add(riser(1.2), 24.6, 0.6)  # wind whoosh
for k, m in enumerate([50, 47, 45, 43, 40, 38, 36, 35]): add(tom(m), PUMP[0] - 1.0 + k * 0.125)
for k in range(16): add(pop(1500 + 140 * (k % 5)), PUMP[0] + 0.3 + k * 0.23, pan=np.sin(k) * 0.5)
for t0 in (22.0, 38.0):
    for k, m in enumerate([50, 47, 43, 40]): add(tom(m, 0.8), t0 + 1.0 + k * 0.125)
for tk in WIND: add(wood(1400, 0.8), tk)
for k in range(30): add(wood(900 + 20 * k, 0.5), FLOOD[0] + k * (FLOOD[1] - FLOOD[0]) / 30)
add(crash(), PUMP[0], 0.7)

# OUTRO
add(crash(), OUTRO, 0.6)
for m in (40, 52, 55, 59, 64): add(piano(m, 4.5, 1.5), OUTRO)
add(reed(40, 4.5), OUTRO)
add(wood(900), LAST_SNAP - 0.35); add(chomp(1.6), LAST_SNAP); add(boom(), LAST_SNAP, 0.6)

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
g2 = np.ones(N); i0, i1 = int(20.4 * SR), int(39.0 * SR); g2[i0:i1] = 1.7; g2[int(20.0*SR):i0] = np.linspace(1, 1.7, i0 - int(20.0*SR))
st *= g2[:, None]
st = np.tanh(st / np.abs(st).max() * 2.2)
st /= np.abs(st).max() / 0.85
with wave.open('bgm.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
