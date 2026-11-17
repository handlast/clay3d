import numpy as np, wave
from cues import *
SR = 44100; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
TRANS = 4  # D-pentatonic -> black keys F# G# A# C# D#
def hz(m): return 440 * 2 ** ((m + TRANS - 69) / 12)
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
def stab(ms, d=0.5, g=1.0):  # piano chord on the black keys
    n = int(d * SR); y = np.zeros(n)
    for m in ms:
        p = piano(m, max(d, 1.2), 1.0)[:n]; y[:len(p)] += p
    return y * 2.6 * g
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


def burp(t0, g=1.0):  # toad croak/vomit: low wobbling saw
    t = T(0.7); f = 70 + 30 * np.sin(2 * np.pi * 9 * t) + 60 * np.exp(-t * 4)
    y = saw(1, t) * 0  # placeholder
    ph = 2 * np.pi * np.cumsum(f) / SR; y = np.sign(np.sin(ph)) * 0.5 + np.sin(ph)
    y = np.convolve(y, np.ones(20) / 20, 'same') * np.exp(-t * 3) * np.minimum(1, t / 0.02) * 0.12 * g
    add(y, t0)
def gulp(t0, g=1.0):
    t = T(0.25); ph = 2 * np.pi * np.cumsum(500 * np.exp(-t * 12) + 90) / SR
    add(np.sin(ph) * np.exp(-t * 14) * 0.25 * g, t0)
def fizz(t0, d=1.5, g=1.0):
    t = T(d); add(hp(noise(d)) * np.exp(-t * 2.5) * 0.05 * g, t0)
def walk(t0, t1, g=1.0):
    k = 0; tt = t0
    while tt < t1: add(tick(), tt, 1.2 * g, pan=0.3 if k % 2 else -0.3); tt += 0.125; k += 1
def tongue_sfx(t0): add(pop(700), t0, 1.8); add(pop(1100), t0 + 0.05, 1.2)


# ---- v2: flytrap-style. Only 2 big hits (0 s bang, 19.8 s vomit) + small outro; everything else light SFX. ----
def soft(t0, ms, g=0.6): add(stab(ms, d=1.4, g=g), t0)
MOT2 = [50, None, 54, None, 57, None, 59, 57]   # D-penta numbers (TRANS shifts to black keys)
def sneak(t0, t1, lift=0):
    for b in range(int((t1 - t0) / BEAT + 1e-6)):
        tb = t0 + b * BEAT; m = MOT2[b % 8]
        if m: add(pluck(m + lift), tb, 1.0, -0.2 if b % 2 else 0.2)
        add(tick(), tb, 1.0, 0.4)
def full(t0, t1, chord, g=1.0):
    cc = CH[chord]
    for b in range(int((t1 - t0) / BEAT + 1e-6)):
        tb = t0 + b * BEAT
        add(kick(), tb, (0.8 if b % 2 == 0 else 0.5) * g)
        if b % 2 == 1: add(snare(), tb, 0.55 * g)
        add(hat(0.8), tb + 0.25, g)
        add(bass(cc[0] if b % 4 != 3 else cc[0] + 7), tb, 0.8 * g)
        m = MOT2[b % 8]; add(pluck((m + 12) if m else cc[3], g=0.6 * g), tb + 0.25, pan=0.3)
        if b % 4 == 0: soft(tb, list(cc[2:5]), 0.45 * g)
def breakdown(t0, t1, chord):
    cc = CH[chord]
    for b in range(int((t1 - t0) / BEAT + 1e-6)):
        tb = t0 + b * BEAT; m = MOT2[b % 8]
        if b % 2 == 0: add(pluck((m or 62) + 12, g=0.7), tb, pan=-0.3)
        if b % 4 == 0: add(reed(cc[0], 1.9, 0.7), tb)
        add(hat(0.25), tb + 0.25)
def big(t0, chord, g=1.0):
    add(boom(), t0, g); add(crash(), t0, g); add(kick(), t0, g); add(stab(list(CH[chord][1:]), d=1.2, g=1.2 * g), t0)

# hook 0-3.5
add(wood(1000), 0.1); tongue_sfx(HOOK_HIT - 0.05); gulp(GULP, 1.2)
big(BANG0, "gong", 1.2); fizz(BANG0, 1.2); add(tom(45, 0.8), BANG0 + 0.45)
for k in range(3):
    tk = BANG0 + 0.5 + k * BEAT; add(kick(), tk, 0.6); add(bass(38), tk, 0.7)
    if k % 2: add(snare(), tk, 0.5)
# sneaky part 3.5-13.5 (pluck + clock, reed drone rising)
sneak(3.5, 13.5)
for t0, m, dd in ((3.5, 38, 2.4), (5.7, 40, 2.4), (8.0, 42, 3.0), (11.0, 45, 2.5)): add(reed(m, dd, 0.8), t0)
add(wood(900), WHO_HIT); soft(WHO_HIT, [62, 66, 69], 0.5)
for k in range(4): add(pop(800 + k * 150), MIX + 0.2 + k * 0.2, 0.8)
add(wood(1300), MIX_HIT); fizz(MIX_HIT, 0.8, 0.8); add(tom(50, 0.6), MIX_HIT)
fizz(SPRAY_HIT, 1.8, 0.9)
for k in range(9): add(pluck(PENTA[k], 0.4, 0.45), SPRAY_HIT + 0.1 * k)
add(wood(900), LAB_HIT); walk(LAB_HIT + 0.8, SWAL, 0.6)
# swallow + tension 13.5-19.8
tongue_sfx(SWAL_HIT - 0.05); gulp(SWAL_HIT + 0.5, 1.4)
add(reed(38, 6.0, 0.9), SWAL)
for k in range(12):  # heartbeat accelerating
    tk = 14.6 + 4.8 * (1 - (1 - k / 12) ** 1.6); add(kick(), tk, 0.45); add(kick(), tk + 0.15, 0.28)
for j, b in enumerate(BANGS): add(tom(47 + j * 3, 0.7), b); fizz(b, 0.5, 0.7)  # muffled bangs inside
add(riser(1.05), 18.4)
burp(VOMIT_HIT - 0.7, 0.4)
# VOMIT: the second (and last) big hit, then groove
big(VOMIT_HIT, "zhi", 1.3); burp(VOMIT_HIT, 1.2); zheng(VOMIT_HIT + 0.1)
full(20.3, 26.5, "zhi")
for i in range(43): add(pop(1100 + (i % 5) * 140), STAT_HIT + 1.6 * (1 - (1 - (i + 1) / 43) ** (1 / 3)), 0.35, pan=np.sin(i) * 0.4)
# clock: drums drop out, woodblock tick-tock
for k in range(int((CLOCK_HIT - CLOCK) / 0.25)): add(wood(1200 if k % 2 else 900, 0.45), CLOCK + k * 0.25)
add(reed(40, 2.2, 0.7), CLOCK); add(crash(), CLOCK_HIT, 0.5); soft(CLOCK_HIT, [64, 69, 71], 0.6)
full(CLOCK_HIT + 0.4, ALIVE, "shang", 0.8)
# alive: breakdown, then build with arps on the 562-day lift
breakdown(ALIVE, OLD_HIT, "jue"); add(shimmer(3.4), ALIVE, 1.0)
for j in range(16): add(pluck(PENTA[j % 11], 0.5, 0.35), ALIVE_HIT + 0.6 + j * 0.06)
add(crash(), OLD_HIT, 0.5); zheng(OLD_HIT + 0.05, g=0.7)
for b in range(int((CTRL - OLD_HIT) / BEAT)):
    t0 = OLD_HIT + b * BEAT; add(kick(), t0, 0.7); add(hat(0.7), t0 + 0.25); add(bass(38), t0, 0.7)
    for k in range(4): add(arp([62, 66, 69, 74][k] + (b // 2) % 3 * 2, 0.6), t0 + k * 0.125, pan=0.4 if k % 2 else -0.4)
# ctrl: half time, descending plucks as the disarmed beetle dissolves
add(wood(900), CTRL_HIT); sneak(CTRL, SIZE, lift=-12)
for j in range(5): add(pluck(PENTA[6 - j], 1.0, 0.5), CTRL_HIT + 0.6 + j * 0.3)
# size: light groove, tom fill into outro
add(wood(1100), SIZE_HIT); full(SIZE, 43.3, "gong", 0.7); burp(SIZE_HIT + 1.0, 0.4)
for k, m in enumerate([62, 59, 57, 54, 50, 47, 45, 42]): add(tom(m - 12, 0.7), 43.3 + k * 0.125)
# outro
add(crash(), OUTRO, 0.4)
for m_ in (38, 50, 57, 62, 66): add(piano(m_, 3.5, 1.1), OUTRO)
for i, t0 in enumerate((BUB1, BUB1 + 0.6, BUB2, BUB2 + 0.7)): add(pop(1300), t0, 1.2); add(pluck(PENTA[i + 2], 1.2, 0.7), t0)
zheng(47.0, n=5, g=0.7)
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
