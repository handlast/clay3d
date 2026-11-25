import numpy as np, wave
SR = 44100
BAR = 10 / 3; BEAT = BAR / 4
NB = 45; DUR = NB * BAR + 0.0
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def hz(m): return 440 * 2 ** ((m - 69) / 12)
# D major: I vi IV V
CH = [[62, 66, 69, 73], [59, 62, 66, 69], [55, 59, 62, 66], [57, 61, 64, 69]]
def chord(b): return CH[b % 4]

def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N: return
    s = sig[: N - i] * gain
    L[i:i + len(s)] += s * (1 - pan) ** 0.5 if pan > 0 else s
    R[i:i + len(s)] += s * (1 + pan) ** 0.5 if pan < 0 else s

def piano(m, dur=3.0, soft=1.0):
    t = np.arange(int(dur * SR)) / SR; f = hz(m); y = np.zeros_like(t)
    for k in range(1, 7):
        y += (1 / k ** 1.6) * np.sin(2 * np.pi * f * k * t * (1 + 0.0004 * k)) * np.exp(-t * (1.2 + 1.1 * k))
    att = np.minimum(1, t / 0.012)
    return y * att * 0.22 * soft

def bell(m, dur=3.0):
    t = np.arange(int(dur * SR)) / SR; f = hz(m)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 1.6) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 4) + 0.12 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 8)
    return y * np.minimum(1, t / 0.004) * 0.10

def pad(ms, dur):
    t = np.arange(int(dur * SR)) / SR; y = np.zeros_like(t)
    for m in ms:
        f = hz(m)
        for d in (-0.003, 0, 0.003):
            y += np.sin(2 * np.pi * f * (1 + d) * t + rng.uniform(0, 6)) + 0.15 * np.sin(4 * np.pi * f * (1 + d) * t)
    env = np.minimum(1, t / 0.9) * np.minimum(1, (dur - t) / 0.9)
    return y * env * (1 + 0.08 * np.sin(2 * np.pi * 0.25 * t)) * 0.012

def bass(m, dur=3.2):
    t = np.arange(int(dur * SR)) / SR; f = hz(m)
    y = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return y * np.minimum(1, t / 0.02) * np.exp(-t * 0.9) * 0.12

def tick(gain=1.0):
    n = int(0.06 * SR); t = np.arange(n) / SR
    y = rng.standard_normal(n); y = np.convolve(y, np.ones(18) / 18, 'same')
    return (y * np.exp(-t * 90) + 0.6 * np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 70)) * 0.05 * gain

for b in range(NB):
    t0 = b * BAR; c = chord(b)
    if b <= 6:  # hook: sparse piano
        add(piano(c[0] - 12, 3.4), t0, 0.9)
        add(piano(c[2], 2.5, 0.6), t0 + 2 * BEAT, 0.7, 0.2)
        if b in (2, 3):  # spread: a note per beat, synced with infection
            for k in range(4): add(piano(c[k % 4] + 12, 1.5, 0.55), t0 + k * BEAT, 0.8, -0.3); add(tick(), t0 + k * BEAT)
        if b == 4: add(bell(c[3] + 12), t0, 1.0)
        if b == 6: add(piano(c[3] + 12, 2.5, 0.6), t0 + 3 * BEAT, 0.7)
    elif b == 33:
        pass  # full silence
    elif b == 44:
        add(pad(CH[0], 6.0), t0, 1.0); add(piano(50, 5), t0); add(piano(66, 5, 0.7), t0 + 0.05); add(piano(69, 5, 0.6), t0 + 0.1); add(bell(74, 5), t0 + 0.2)
    else:
        add(pad(c, BAR + 1.0), t0 - 0.3, 1.0)
        add(bass(c[0] - 24), t0, 1.0)
        add(tick(0.8), t0)
        if 41 <= b <= 43:
            add(piano(c[0], 3), t0, 0.8); add(piano(c[2] + 12, 2.5, 0.6), t0 + 2 * BEAT, 0.7)
            continue
        if b >= 34:
            for k in range(8): add(piano(c[k % 4] + (12 if k >= 4 else 0), 1.6, 0.6), t0 + k * BEAT / 2, 0.7, 0.3 if k % 2 else -0.3)
        else:
            for k in range(4): add(piano(c[k], 2.0, 0.65), t0 + k * BEAT, 0.8, 0.25 if k % 2 else -0.25)
        if b >= 18: add(bell(c[3] + 12 if b % 2 == 0 else c[2] + 12), t0, 0.9)
        if b in (7, 9, 13, 18, 28, 34, 36): add(bell(c[0] + 24), t0, 1.1)  # chapter bloom

def reverb(x):
    n = int(2.4 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 2.6); ir = np.convolve(ir, np.ones(6) / 6, 'same'); ir /= np.abs(ir).sum() ** 0.5 * 12
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
    return x * 0.75 + y * 0.6
L = reverb(L); R = reverb(R)
st = np.stack([L, R], 1); st /= np.abs(st).max() / 0.7
fade = np.ones(N); k = int(1.5 * SR); fade[-k:] = np.linspace(1, 0, k) ** 2; st *= fade[:, None]
with wave.open('bgm.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok', DUR)
