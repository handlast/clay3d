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



PENTA = [62, 64, 66, 69, 71, 74, 76, 78, 81, 83, 86]
# 宫 D, 商 E, 角 F#, 徵 A, 羽 B — chords from pentatonic tones only
CH = {"gong": (38, 50, 57, 62, 66, 69), "shang": (40, 52, 59, 64, 69, 71), "jue": (42, 54, 62, 66, 69, 74),
      "zhi": (45, 57, 64, 69, 71, 76), "yu": (47, 54, 59, 62, 66, 71)}
ORDER = ["gong", "shang", "jue", "zhi", "yu"]
def zheng(t0, up=True, g=1.0, n=11):
    seq = PENTA[:n] if up else PENTA[:n][::-1]
    for k, mm in enumerate(seq): add(pluck(mm, 1.2, 0.8 * g), t0 + k * 0.035, pan=-0.5 + k / n)
def wobble_bell(m, t0, wob, g=1.0, d=1.6):
    t = T(d); f = hz(m) * (1 + wob * 0.03 * np.sin(2 * np.pi * 5 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = (np.sin(ph) + 0.4 * np.sin(2.76 * ph)) * np.exp(-t * 2.5) * 0.25 * g
    add(y, t0)
MOT = [74, None, 69, 71, None, 69, 66, 62]
def groove(t0, t1, chord, g=1.0, half=False, wob=0.0):
    nb = int((t1 - t0) / BEAT + 1e-6); cc = CH[chord]
    for b in range(nb):
        tb = t0 + b * BEAT
        if half:
            if b % 4 == 0: add(kick(), tb, 0.8 * g)
        else:
            add(kick(), tb, (0.9 if b % 2 == 0 else 0.45) * g)
            if b % 2 == 1: add(snare(), tb, 0.6 * g)
        add(hat(0.6), tb + 0.25, g)
        add(bass(cc[0]), tb, 0.8 * g)
        if b % 4 == 0: add(stab(list(cc[2:5]), d=1.8, g=0.3 * g), tb)
        m = MOT[b % 8]
        if m: wobble_bell(m, tb, wob, 0.5 * g, 0.8); add(pluck(m - 12, g=0.4 * g), tb + 0.25, pan=-0.3)
def hit(t0, chord, g=1.0):
    add(boom(), t0, g); add(crash(), t0, 0.6 * g); add(kick(), t0, g); add(stab(list(CH[chord][1:]), d=1.0, g=1.1 * g), t0)

hit(HOOK_HIT, "gong", 1.3); zheng(HOOK_HIT + 0.05)
groove(1.0, WHO, "gong", 0.7, half=True)
hit(WHO_HIT, "zhi", 0.9); groove(WHO_HIT + 0.1, 6.5, "zhi", 0.8)
add(riser(1.0), 6.5)
for k in range(9):
    ts = DAY0 + k * DDUR; tb = DHITS[k]; ch = ORDER[k % 5]; wob = k / 8
    groove(ts, ts + DDUR, ch, 0.8 + k * 0.03, half=(k in (0, 3, 6)), wob=wob)
    hit(tb, ch, 0.9 + (0.4 if k == 2 else 0))
    wobble_bell(PENTA[k + 1], tb + 0.05, wob * 2, 1.4, 2.0)
    if k == 2: zheng(tb + 0.1); zheng(tb + 0.6, up=False)
    if k == 8:
        for j in range(6): add(pluck(PENTA[8 - j], 0.8, 0.7), tb + j * 0.28)
add(riser(1.0), 35.3)
# sleep: music box lullaby in gong mode
LUL = [74, 71, 69, 66, 69, 62, None, 64, 66, 69, 66, 64, 62]
for i, mm in enumerate(LUL):
    if mm: add(bell(mm + 12, 0.8, 0.9), SLEEP_HIT + i * 0.3)
for m_ in CH["gong"]: add(piano(m_, 3.5, 0.6), SLEEP_HIT)
hit(GUIN_HIT, "yu", 1.1); groove(GUIN_HIT + 0.1, OUTRO, "shang", 0.8)
add(crash(), OUTRO, 0.5)
for m_ in (38, 50, 57, 62, 66): add(piano(m_, 3.5, 1.2), OUTRO)
for i, t0 in enumerate((BUB1, BUB1 + 0.6, BUB2, BUB2 + 0.7)): add(pop(1300), t0, 1.5); add(pluck(PENTA[i + 2], 1.2, 0.9), t0)
zheng(47.0, n=5); add(boom(), 47.0, 0.4); add(stab([50, 57, 62, 64, 69], d=0.8), 47.0)
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
