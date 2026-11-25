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

# HOOK
add(hum(0.5), 0.0, 1.5)
for z in HOOK_ZAP: add(zap(0.2, 1.4), z)
add(sub_drop(), HOOK_BOOM); add(boom(), HOOK_BOOM); add(plasma_roar(2.2, 1.6), HOOK_BOOM); add(crash(), HOOK_BOOM, 1.4); add(kick(), HOOK_BOOM)
for k in range(4):
    tk = HOOK_BOOM + k * BEAT; add(kick(), tk); add(bass(40 if k < 3 else 43), tk)
    if k % 2: add(snare(), tk)
    add(stab([64, 67, 71], g=1.2 if k == 0 else 0.6), tk)
add(stab([60, 64, 67, 72], d=0.9, g=1.2), 2.0)
# 2.6-12: sneaky pizz + hits
motif = [52, None, 55, None, 59, None, 58, 55]
for b in range(int((12.0 - 2.6) / BEAT)):
    t0 = 2.6 + b * BEAT; m = motif[b % 8]
    if m is not None: add(pluck(m + (0 if t0 < 6 else 2 if t0 < 9 else 4)), t0, 1.0, -0.2 if b % 2 else 0.2)
    add(tick(), t0, 1, 0.4)
    if b % 2 == 0: add(kick(), t0, 0.35)
for t0, m, d in ((2.6, 40, 3.4), (6.0, 42, 3.0), (9.0, 44, 3.0)): add(reed(m, d), t0)
for h in MYTH_HITS[:2]: add(wood(900), h)
add(stab([63, 66, 70], d=0.6, g=1.0), MYTH_HITS[2]); add(kick(), MYTH_HITS[2])
add(wood(700), 6.4); add(wood(760), 6.7); add(wood(820), WHOLE_TOUCH)
add(zap(0.3, 1.2), WHOLE_ZAP); add(plasma_roar(1.2), WHOLE_ZAP); add(boom(), WHOLE_ZAP, 0.6)
add(pop(800), 9.3); add(pop(900), 9.35)
for k in range(10): add(tick(), BEAD_SALT + k * 0.04, 1.5)
add(zap(0.3, 1.2), BEAD_ZAP); add(plasma_roar(1.0), BEAD_ZAP); add(boom(), BEAD_ZAP, 0.5)
add(stab([64, 68, 71, 76], d=0.9, g=1.3), ANSWER); add(kick(), ANSWER); add(crash(), ANSWER, 0.6)
# 12-19.5 resonance build
add(hum(7.5), 12.0, 1.2)
for k, h in enumerate(BOUNCE):
    add(wobble(40 + k * 2, 19.5 - h, 1 + k * 0.4), h); add(tom(50 + k * 3), h); add(pop(1200 + 300 * k), h)
for k in range(14):
    tk = 13.0 + 6.4 * (1 - (1 - k / 14) ** 1.6); add(kick(), tk, 0.5); add(kick(), tk + 0.15, 0.3)
add(riser(RISER[1] - RISER[0]), RISER[0])
# 20-39
add(sub_drop(), BURST); add(boom(), BURST); add(plasma_roar(3.0, 2.0), BURST); add(crash(), BURST, 1.4); add(stab([52, 59, 64, 67, 71], d=1.0, g=1.6), BURST)
prog = [40, 40, 36, 38]
for b in range(int((OUTRO - BURST) / BEAT)):
    t0 = BURST + b * BEAT; bar = b // 4; root = prog[bar % 4]
    if t0 < 24.0 or t0 >= 35.0:
        add(kick(), t0, 0.9 if b % 2 == 0 else 0.6)
        if b % 2 == 1: add(snare(), t0)
        add(hat(1.0), t0 + 0.25); add(hat(0.6), t0); add(bass(root if b % 4 != 3 else root + 7), t0)
        add(pluck(motif[b % 8] + 12 if motif[b % 8] else root + 24, g=0.7), t0 + 0.25, pan=0.3)
        if b % 4 == 0: add(stab([root + 24, root + 27 if root in (40, 38) else root + 28, root + 31], d=1.2, g=0.6), t0)
        if b % 2 == 0 and t0 < 24: add(zap(0.12, 0.5), t0 + 0.25)
    elif t0 < 30.0:
        if b % 2 == 0: add(pluck(motif[b % 8] + 12 if motif[b % 8] else 64, g=0.8), t0, pan=-0.3)
        if b % 4 == 0: add(reed(root, 1.9, 0.8), t0)
        add(hat(0.3), t0 + 0.25)
    else:
        add(kick(), t0, 0.9); add(hat(0.8), t0 + 0.25); add(bass(root), t0)
        if b % 2 == 1: add(snare(), t0, 0.7)
        step = int((t0 - 30.0) / 1.0)
        for k in range(4): add(arp([64, 67, 71, 76][k] + step, 0.9), t0 + k * 0.125, pan=0.4 if k % 2 else -0.4)
for i, h in enumerate(EGG_HITS):
    if i == 1: add(pluck(47, g=0.9), h); add(pluck(46, g=0.9), h + 0.3)
    else: add(zap(0.3, 1.0), h); add(boom(), h, 0.5); add(stab([64, 67, 71], g=0.9), h)
for i, h in enumerate(SPEC_HITS): add(pop(900 + 250 * i), h); add(crash(), h, 0.25)
for k, m in enumerate([50, 47, 45, 43, 40, 38, 36, 35]): add(tom(m), NANO[0] - 1.0 + k * 0.125)
for k in range(12): add(pop(1500 + 140 * (k % 5)), NANO[0] + 0.5 + k * 0.25, pan=np.sin(k) * 0.5)
for t0 in (22.0, 38.0):
    for k, m in enumerate([50, 47, 43, 40]): add(tom(m, 0.8), t0 + 1.0 + k * 0.125)
add(crash(), OUTRO, 0.6)
for m in (40, 52, 55, 59, 64): add(piano(m, 4.5, 1.5), OUTRO)
add(reed(40, 4.5), OUTRO); add(hum(4.5), OUTRO + 0.5)
add(zap(0.3, 1.3), LAST_ZAP - 0.2); add(plasma_roar(1.0, 1.4), LAST_ZAP); add(boom(), LAST_ZAP, 0.7)

def reverb(x):
    n = int(1.5 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 4); ir = np.convolve(ir, np.ones(5) / 5, 'same'); ir /= np.abs(ir).sum() ** 0.5 * 14
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x * 0.85 + np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)] * 0.45
L = reverb(L); R = reverb(R)
st = np.stack([L, R], 1)
st[int(SILENCE[0] * SR):int(SILENCE[1] * SR)] *= 0.0
g2 = np.ones(N); i0, i1 = int(20.4 * SR), int(39.0 * SR); g2[i0:i1] = 1.6; g2[int(20.0 * SR):i0] = np.linspace(1, 1.6, i0 - int(20.0 * SR))
st *= g2[:, None]
st = np.tanh(st / np.abs(st).max() * 2.2); st /= np.abs(st).max() / 0.85
with wave.open('bgm.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
