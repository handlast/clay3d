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

# ---------- quiet part 0-30 (D minor colour) ----------
def scream(d=1.1):
    t = T(d); f = 520 * (2.6 ** np.minimum(t / 0.25, 1)) * (1 + 0.04 * np.sin(2 * np.pi * 7 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = sum(np.sin(ph * k) / k for k in range(1, 9))
    return y * np.minimum(1, t / 0.02) * np.exp(-np.maximum(t - 0.6, 0) * 6) * 0.05
# HOOK BURST 0-2.5
add(crash(), 0.0, 1.3); add(boom(), 0.0); add(scream(), 0.02, 1.0, -0.1)
for k in range(5):
    tk = k * BEAT; add(kick(), tk)
    if k % 2: add(snare(), tk)
    add(stab([62, 65, 69, 74], g=1.2 if k == 0 else 0.7), tk)
    add(bass(38 if k < 4 else 46), tk)
for k in range(20): add(pclick(2000 + 90 * k, g=1.0), k * 0.125, pan=np.sin(k) * 0.6)
add(stab([58, 62, 65, 70], d=1.0, g=1.4), 2.0)
add(drone(38, 27.0), 2.5, 1.0); add(drone(45, 25), 4.5, 0.7)
notes = [74, 69, 72, 65, 69, 67, 64, 62]  # sparse, unresolved
for i, t0 in enumerate(np.arange(3.0, 27.0, 1.5)):
    if 12.2 < t0 < 16.6: continue
    add(piano(notes[i % 8]), t0, 0.9, -0.2 if i % 2 else 0.2)
for t0 in np.arange(6.0, 27.0, 0.5): add(hat(0.5), t0, 1, 0.3)
st_hook_end = 2.6  # soft clock tick
for i, tk in enumerate(COUNTER): add(pclick(2200 + 30 * i, g=0.9), tk, pan=np.sin(i) * 0.5)
for t0 in np.arange(23.0, 27.0, 0.75): add(kick(), t0, 0.35)  # heartbeat
for t0 in np.arange(23.2, 27.0, 0.75): add(kick(), t0, 0.22)
add(riser(RISER[1] - RISER[0]), RISER[0])
# 29.5-30 silence (nothing scheduled)

# ---------- burst 30-56 ----------
prog = [[50, 57, 62, 65], [46, 53, 58, 62], [41, 48, 53, 57], [48, 55, 60, 64]]  # Dm Bb F C
add(crash(), BURST); add(boom(), BURST, 0.8)
for b in range(15, 28):
    t0 = b * BAR; c = prog[b % 4]
    full = b < 19 or b >= 20
    for k in range(4):
        tk = t0 + k * BEAT
        add(kick(), tk)
        if k in (1, 3): add(snare(), tk)
    for k in range(16):
        tk = t0 + k * BEAT / 4
        add(hat(1.0 if k % 2 else 0.6), tk, 1, 0.35)
        # plant clicks as the lead percussion: syncopated pattern
        if k in (2, 3, 6, 9, 11, 14):
            add(pclick(2000 + 300 * (k % 5), g=1.1), tk, pan=-0.4 if k % 2 else 0.4)
    for k, off in enumerate((0, 0.75, 1.5, 2.5, 3.0, 3.5)):
        add(bass(c[0] - 12 + (12 if k == 3 else 0)), t0 + off * BEAT)
    for off in (0, 1.5, 3.0):
        add(stab([m + 12 for m in c], g=1.0 if full else 0.6), t0 + off * BEAT, pan=0.1)
    if b % 2 == 0: add(piano(c[3] + 24, 2.0, 1.2), t0)
for i, tk in enumerate(BUBBLES): add(pclick(3200 - 120 * i, g=1.2), tk + 0.25)
add(crash(), 46.0, 0.7)

# ---------- outro ----------
add(crash(), OUTRO, 0.8)
for m in (38, 50, 57, 62, 65, 69): add(piano(m, 4.0, 1.6), OUTRO)
add(drone(38, 4.0), OUTRO, 0.8)
add(pclick(3000, g=2.0), LAST_CLICK)

def reverb(x):
    n = int(1.8 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 3.5); ir = np.convolve(ir, np.ones(5) / 5, 'same'); ir /= np.abs(ir).sum() ** 0.5 * 14
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x * 0.85 + np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)] * 0.5
L = reverb(L); R = reverb(R)
st = np.stack([L, R], 1)
st[int(SILENCE[0] * SR):int(SILENCE[1] * SR)] *= 0.0  # hard silence before the drop
a, b, c = int(2.45 * SR), int(2.6 * SR), int(3.2 * SR)
env = np.ones(N); env[a:b] = np.linspace(1, 0.05, b - a); env[b:c] = np.linspace(0.05, 1, c - b) ** 3
pre = np.zeros(N); pre[:b] = 1  # only cut the hook's own tail: apply env fully
st *= env[:, None]
st /= np.abs(st).max() / 0.85
with wave.open('bgm.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
