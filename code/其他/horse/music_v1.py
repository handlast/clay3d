import numpy as np, wave
from cues import *
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
VO = L  # voice line times from cues
PENTA = [0, 2, 4, 7, 9]
def pm(k, base=62): return base + PENTA[k % 5] + 12 * (k // 5)
def zheng(m, d=1.6, g=1.0):  # guzheng-ish KS pluck with bend
    f = hz(m); n = int(SR / f); buf = rng.uniform(-1, 1, n); out = np.zeros(int(d * SR))
    for i in range(len(out)):
        out[i] = buf[i % n]; buf[i % n] = 0.5 * (buf[i % n] + buf[(i + 1) % n]) * 0.997
    t = T(d); return out * np.exp(-t * 1.8) * 0.12 * g
def taiko(g=1.0):
    t = T(0.8); ph = 2 * np.pi * np.cumsum(55 + 90 * np.exp(-t * 25)) / SR
    return (np.sin(ph) * np.exp(-t * 5) + hp(noise(0.8)) * np.exp(-t * 40) * 0.3) * 0.5 * g
def gong(d=4.0, g=1.0):
    t = T(d); y = sum(np.sin(2 * np.pi * f * t + 3 * np.sin(2 * np.pi * f * 0.5 * t) * np.exp(-t)) / (k + 1) for k, f in enumerate([110, 163, 237, 311]))
    return y * np.exp(-t * 1.0) * np.minimum(1, t / 0.01) * 0.12 * g
def erhu(m, d, g=1.0):
    t = T(d); f = hz(m) * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.3))
    y = saw(1, t * 0) if False else np.sin(2 * np.pi * np.cumsum(f) / SR)
    y = y + 0.5 * np.sin(2 * 2 * np.pi * np.cumsum(f) / SR) + 0.25 * np.sin(3 * 2 * np.pi * np.cumsum(f) / SR)
    return y * np.minimum(1, t / 0.15) * np.minimum(1, (d - t) / 0.3) * 0.03 * g
def fire_whoosh(d=1.5, g=1.0):
    t = T(d); y = np.convolve(noise(d), np.ones(30) / 30, 'same')
    return y * np.sin(np.pi * t / d) * 0.25 * g

BPM = 96; BT = 60 / BPM
# hook: impact + driving taiko
add(fire_whoosh(0.6, 1.5), 0.0); add(sub_drop(), FM.H_BOOM); add(boom(), FM.H_BOOM); add(gong(4, 1.4), FM.H_BOOM); add(crash(), FM.H_BOOM, 1.2)
for k in range(int((FM.H_Q - 0.4) / (BT / 2))):
    t0 = FM.H_BOOM + 0.6 + k * BT / 2
    if t0 > FM.H_Q - 0.2: break
    add(taiko(0.9 if k % 4 == 0 else 0.45), t0, 1, (-0.2 if k % 2 else 0.2))
    if k % 2 == 0: add(zheng(pm([5, 7, 8, 7, 5, 4, 2, 4][(k // 2) % 8]), 0.8, 0.8), t0)
add(stab([50, 57, 62], 0.6, 1.4), FM.H_NUM - 0.3); add(boom(), FM.H_NUM - 0.3, 0.8)
for k in range(5): add(pclick(1400 - k * 150, 0.08, 0.8), FM.H_NUM - 0.2 + k * 0.08)
add(wood(800), FM.H_Q); add(wood(1000), FM.H_Q + 0.15); add(wood(1200), FM.H_Q + 0.3)
# body groove: soft taiko + guzheng pentatonic + erhu pads, quieter under voice
mel = [0, 2, 4, 2, 5, 4, 2, 1, 0, 2, 3, 4, 7, 5, 4, 2]
t0 = FM.B0; k = 0
while t0 < FM.I0:
    sec_soft = (FM.E0 <= t0 < FM.F0) or (FM.G0 + 0 <= t0 < FM.G_TWIST)
    if k % 4 == 0: add(taiko(0.55), t0)
    if k % 4 == 2: add(taiko(0.3), t0)
    add(hat(0.5), t0 + BT / 2)
    if k % 2 == 0 and not sec_soft: add(zheng(pm(mel[(k // 2) % 16] + (2 if t0 > FM.F0 else 0)), 1.2, 0.55), t0, 1, 0.3)
    if k % 2 == 1: add(zheng(pm(mel[(k // 2 + 3) % 16]) - 12, 0.9, 0.35), t0, 1, -0.3)
    t0 += BT; k += 1
for a, b, m in ((FM.B0, FM.D0, 50), (FM.D0, FM.F0, 48), (FM.F0, FM.G0, 51), (FM.G0, FM.I0, 50)):
    add(erhu(m + 12, b - a, 0.7), a); add(drone(m - 12, b - a, 0.5), a)
# reveals
for h in [FM.B_BING, FM.B_WU]: add(zheng(74, 1.8, 1.2), h); add(gong(2.5, 0.5), h)
for k in range(10): add(pclick(1800 + 80 * k, 0.06, 0.5), FM.B_60 + k * 0.28)
add(riser(1.4), FM.B_FIRE + 0.2); add(fire_whoosh(1.6, 1.4), FM.B_FIRE + 0.1); add(boom(), FM.B_FIRE + 1.6); add(gong(4, 1.2), FM.B_FIRE + 1.6); add(stab([50, 57, 62, 66], 0.8, 1.3), FM.B_FIRE + 1.6)
for k in range(21): add(wood(700 + 15 * k, 0.6), FM.D_COUNT + 1.0 + k * 2.6 / 21)
add(boom(), FM.D_JIE + 0.2); add(gong(3.5, 1.3), FM.D_JIE + 0.2); add(fire_whoosh(1.5, 1.3), FM.D_JIE)
add(taiko(1.2), FM.D_JK); add(taiko(1.0), FM.D_JK + 0.3); add(fire_whoosh(2, 1.2), FM.D_JK + 0.5)
for i in range(2): add(taiko(1.1), FM.D_JK + 0.8 + i * 0.6); add(stab([48, 55, 60], 0.4, 0.8), FM.D_JK + 0.8 + i * 0.6)
add(taiko(1.4), FM.E_SEAL); add(wood(400, 1.5), FM.E_SEAL); add(crash(), FM.E_SEAL, 0.5)
for i in range(10): add(pclick(1100 + 90 * i, 0.07, 0.6), FM.E_ANY + 0.5 + i * 0.28)
add(gong(3, 0.7), FM.F0); add(fire_whoosh(1.8, 1.4), FM.F_OSH + 2.2); add(boom(), FM.F_OSH + 2.4, 0.8)
for i in range(5): add(pop(700 + i * 120), FM.F_RUM + 0.8 + i * 0.25)
add(stab([49, 56, 61], 0.6, 1.2), FM.G_BAR + 2.9); add(boom(), FM.G_BAR + 2.9, 0.9)
add(riser(0.8), FM.G_TWIST - 0.8); add(gong(3, 1.0), FM.G_TWIST); add(stab([55, 62, 67, 71], 0.8, 1.2), FM.G_TWIST)
for i in range(10): add(pop(900 + 60 * i), FM.G_SHIFT + 1.4 + i * 0.12)
add(stab([55, 59, 62, 67], 0.6, 1.0), FM.G_PLUS + 0.3); add(zheng(79, 1.5, 1.0), FM.H0 + 1.6)
# outro: big finish
add(boom(), FM.I0); add(gong(5, 1.4), FM.I0); add(crash(), FM.I0, 1.0)
for k in range(int((FM.DUR - FM.I0 - 1.5) / (BT / 2))):
    t0 = FM.I0 + k * BT / 2
    add(taiko(0.8 if k % 4 == 0 else 0.4), t0)
    if k % 2 == 0: add(zheng(pm([5, 7, 9, 7, 8, 7, 5, 4][(k // 2) % 8]), 1.0, 0.7), t0)
for m in (50, 57, 62, 66, 69): add(piano(m, 3.0, 1.0), FM.DUR - 3.3)
add(gong(3.2, 1.0), FM.DUR - 3.3)

def reverb(x):
    n = int(1.8 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 3.5); ir = np.convolve(ir, np.ones(5) / 5, 'same'); ir /= np.abs(ir).sum() ** 0.5 * 14
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x * 0.85 + np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)] * 0.5
LL = reverb(LL); R = reverb(R)
st = np.stack([LL, R], 1); st = np.tanh(st / np.abs(st).max() * 1.8); st /= np.abs(st).max() / 0.9
# voice track + ducking
v = np.zeros(N)
for i, (a, b) in enumerate(VO):
    w = wave.open(f'vo/{i + 1}.wav'); x = np.frombuffer(w.readframes(w.getnframes()), '<i2') / 32768
    j = int(a * SR); v[j:j + len(x)] += x[: N - j]
env = np.convolve((np.abs(v) > 0.01).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
duck = 1 - 0.55 * np.clip(env * 3, 0, 1)
mixd = st * duck[:, None] * 0.55 + v[:, None] * 1.0
mixd /= np.abs(mixd).max() / 0.95
with wave.open('mix.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mixd * 32767).astype('<i2').tobytes())
print('ok', N / SR)
