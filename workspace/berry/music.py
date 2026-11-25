import numpy as np, wave
from cues import *
SR = 44100; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(11)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
# A major: I V vi IV
CH = [[57, 61, 64], [52, 56, 59], [54, 57, 61], [50, 54, 57]]
PENT = [69, 71, 73, 76, 78, 81, 83, 85, 88, 90, 93, 95]  # A major pentatonic, high

def add(sig, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i < 0: return
    s = sig[: N - i] * g
    L[i:i + len(s)] += s * (1 - max(pan, 0)); R[i:i + len(s)] += s * (1 + min(pan, 0))

def T(d): return np.arange(int(d * SR)) / SR
def marimba(m, d=0.6):
    t = T(d); f = hz(m)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.35 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t * 28) + 0.1 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 60)
    return y * np.minimum(1, t / 0.002) * 0.16
def glock(m, d=1.4):
    t = T(d); f = hz(m)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 3) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 7) + 0.15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 14)
    return y * np.minimum(1, t / 0.001) * 0.09
def bass(m, d=0.45):
    t = T(d); f = hz(m)
    y = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + 0.1 * np.sin(6 * np.pi * f * t)
    return y * np.minimum(1, t / 0.005) * np.exp(-t * 5) * 0.17
def kick(): t = T(0.25); ph = 2 * np.pi * np.cumsum(50 + 90 * np.exp(-t * 30)) / SR; return np.sin(ph) * np.exp(-t * 14) * 0.22
def noise(d, smooth=1):
    y = rng.standard_normal(int(d * SR))
    if smooth > 1: y = np.convolve(y, np.ones(smooth) / smooth, 'same')
    return y
def hp(y): return np.diff(y, prepend=0)
def clap():
    t = T(0.18); y = hp(noise(0.18)) * 0.5
    env = np.exp(-t * 30) + 0.6 * np.exp(-np.maximum(t - 0.012, 0) * 40) * (t > 0.012) + 0.5 * np.exp(-np.maximum(t - 0.024, 0) * 25) * (t > 0.024)
    return y * env * 0.05
def shaker(g=1.0): t = T(0.06); return hp(hp(noise(0.06))) * np.exp(-t * 60) * 0.012 * g
def tickk(): t = T(0.03); return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 200) * 0.06
def sweep(f0, f1, d=0.45, g=0.08):
    t = T(d); f = f0 * (f1 / f0) ** (t / d); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.sin(np.pi * t / d) ** 0.5 * g
def riser(d): t = T(d); y = hp(noise(d, 2)); return y * (t / d) ** 2 * 0.05
def crash(): t = T(1.5); return hp(hp(noise(1.5))) * np.exp(-t * 3) * 0.03
def thud(): t = T(0.2); return np.sin(2 * np.pi * 110 * t) * np.exp(-t * 25) * 0.15

def silent(t):  # stop-time windows: groove muted
    return (STOP1 <= t < TITLE) or (STOP2 <= t < HIT2) or (BREAK3[0] <= t < HIT3) or t >= END
def groove(b0, b1, g=1.0):
    pat = [1, 0, 1, 1, 0, 1, 0, 1]
    for b in range(b0, b1):
        c = CH[b % 4]; t0 = b * BAR
        arp = [c[0] + 12, c[1] + 12, c[2] + 12, c[1] + 12, c[0] + 24, c[2] + 12, c[1] + 12, c[2] + 12]
        for k in range(8):
            tk = t0 + k * BEAT / 2
            if silent(tk): continue
            if pat[k]: add(marimba(arp[k]), tk, 0.9 * g, 0.25 if k % 2 else -0.25)
            add(shaker(0.8 if k % 2 else 0.5), tk, g, 0.4)
        for k in range(4):
            tk = t0 + k * BEAT
            if silent(tk): continue
            if k in (0, 2): add(kick(), tk, g)
            if k in (1, 3): add(clap(), tk, g, -0.1)
        for tk, m in [(t0, c[0] - 12), (t0 + 1.25 * BEAT, c[0] - 12), (t0 + 2 * BEAT, c[2] - 24)]:
            if not silent(tk): add(bass(m), tk, g)

# ---- hook 0-8
add(sweep(300, 1200, 0.18, 0.1), 0.0); add(glock(81), 0.0, 1.2)
for k in range(6):
    tk = k * BEAT
    if tk < 3: add(marimba(CH[0][k % 3] + 12), tk, 0.6)
for i, tk in enumerate(HOOK_SEEDS): add(glock(PENT[i]), tk, 1.0, -0.4 + 0.08 * i)
for i in range(4): add(marimba(PENT[7 - i * 2] - 12), ROLL_IN + i * 0.25, 0.8)  # roll in, falling
add(marimba(57), 7.0, 0.8); add(tickk(), 7.25)
# ---- title + groove
add(crash(), TITLE); add(glock(81), TITLE, 1.2); add(glock(85), TITLE, 1.0); add(glock(88), TITLE, 0.9)
groove(4, 43)
# ---- section cues
for i in range(7): add(marimba(PENT[9 - i]), REWIND[0] + i * 0.2, 0.7)
for i, tk in enumerate(PISTILS): add(glock(PENT[(i * 5) % 12]), tk, 0.45, rng.uniform(-0.5, 0.5))
for i, tk in enumerate(POLLEN): add(glock(PENT[2 + i % 8]), tk, 0.7)
add(sweep(250, 900, 0.6, 0.09), SWELL)
for i, tk in enumerate(SIGNAL): add(glock(PENT[4 + i]), tk, 0.8)
for i, tk in enumerate(BUMPS): add(sweep(300, 700, 0.18, 0.07), tk)
for tk in GRAY: add(thud(), tk)
add(sweep(600, 250, 0.4, 0.06), DENT)
add(riser(RISER2[1] - RISER2[0]), RISER2[0])
add(crash(), HIT2); add(glock(81), HIT2); add(glock(88), HIT2)
for k in range(8): add(tickk(), BREAK3[0] + k * BEAT)
for i, tk in enumerate(PLUCK): add(glock(PENT[11 - i]), tk, 0.6)
add(sweep(200, 600, 0.9, 0.05), BRUSH); add(riser(HIT3 - BRUSH), BRUSH)
add(crash(), HIT3); add(sweep(250, 1000, 0.7, 0.09), HIT3)
for c in (69, 73, 76, 81): add(glock(c + 12), HIT3, 0.8)
for i, tk in enumerate(CHART): add(glock(PENT[i]), tk, 0.6)
for i in range(6): add(marimba(PENT[i] - 12), GAUGE[0] + i * 0.5, 0.7)
t = BEE[0]; i = 0
while t < BEE[1]:
    add(marimba(PENT[5 + (i % 2)] - 12, 0.2), t, 0.45, np.sin(i * 0.3) * 0.6); t += 0.0625; i += 1
for i in range(6): add(marimba(PENT[8 - i] - 12), COLD[0] + i * 0.5, 0.7)
add(glock(88), CHECK); add(glock(93), CHECK + 0.125)
for i, tk in enumerate(FINALE): add(glock(PENT[i % 12] + (12 if i >= 12 else 0)), tk, 0.7)
# ---- ending chord
for m in (45, 57, 61, 64, 69, 73, 76): add(marimba(m, 2.0), END, 0.8)
for m in (81, 85, 88): add(glock(m, 4.0), END, 1.0)
add(crash(), END)

def reverb(x):
    n = int(1.4 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 4.5); ir = np.convolve(ir, np.ones(5) / 5, 'same'); ir /= np.abs(ir).sum() ** 0.5 * 14
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x * 0.85 + np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)] * 0.45
L = reverb(L); R = reverb(R)
st = np.stack([L, R], 1); st /= np.abs(st).max() / 0.8
k = int(2.0 * SR); st[-k:] *= (np.linspace(1, 0, k) ** 2)[:, None]
with wave.open('bgm.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
