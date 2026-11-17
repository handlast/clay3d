import math
exec(open('../braess/instr.py').read().replace('from cues import *', 'from cues import *'))
# ---- 火柴人摇摆：120 BPM 四踩洗脑 loop，黑键五声（TRANS=4）。大重音只在 0 秒和 26 秒（你气不气）。
hrng = np.random.default_rng(5); KICKS = []
PL = np.zeros(N); PR = np.zeros(N)
_add = add
def add(sig, t0, g=1.0, pan=0.0):
    g *= 1 + hrng.uniform(-0.1, 0.1); t0 += hrng.uniform(-0.005, 0.005); _add(sig, max(0, t0), g, pan)
def kk(t0, g=1.0): add(kick(), t0, g); KICKS.append(t0)
def lowpass(y, k): n = max(1, int(k)); return np.convolve(y, np.ones(n) / n, 'same')
CHS = [(50, 62, 66, 69), (47, 59, 62, 66), (52, 64, 69, 71), (45, 57, 64, 69)]  # 宫 羽 商 徵, one per bar (2 s)
def chord(t): return CHS[int(t // 2.0) % 4]
def clap(g=1.0):
    t = T(0.22); y = hp(noise(0.22)) * (np.exp(-t * 25) + 0.6 * np.exp(-((t - 0.012) % 0.011) * 300) * (t < 0.035))
    return lowpass(y, 2) * 0.11 * g
def ohat(g=1.0): t = T(0.18); return hp(hp(noise(0.18))) * np.exp(-t * 22) * 0.03 * g
def mari(m, g=1.0):
    t = T(0.6); f = hz(m)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.3 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30)) * np.minimum(1, t / 0.002) * 0.11 * g
def softpad(ms, d, g=1.0):
    t = T(d); y = np.zeros(len(t))
    for m in ms:
        for c in (-0.0035, 0, 0.0035): y += np.sin(2 * np.pi * hz(m) * (1 + c) * t + hrng.uniform(0, 6.3))
    a = np.clip(t / 0.5, 0, 1); r = np.clip((d - t) / 0.3, 0, 1)
    return lowpass(y * a * a * (3 - 2 * a) * r * r * (3 - 2 * r), 4) * 0.006 * g
def pad(t0, t1, g=1.0):
    t = t0
    while t < t1 - 0.05:
        nx = min(t1, (math.floor(t / 2.0) + 1) * 2.0); sig = softpad(chord(t + 0.01)[1:], nx - t + 0.04, g)
        i = int(t * SR); s = sig[:N - i]; PL[i:i + len(s)] += s; PR[i:i + len(s)] += s * 0.93; t = nx
HOOK = [74, None, 78, 81, 83, 81, 78, None, 81, None, 78, 76, 74, None, 76, None]   # 8ths over a bar
def groove(t0, t1, g=1.0, mel=True, extra=False):
    nb = int(round((t1 - t0) / BEAT))
    for b in range(nb):
        tb = t0 + b * BEAT; cc = chord(tb + 0.01)
        kk(tb, 0.9 * g)
        if b % 2 == 1: add(clap(), tb, 0.8 * g)
        add(ohat(), tb + BEAT / 2, 0.8 * g); add(hat(0.7), tb + BEAT * 0.75, g)
        add(bass(cc[0], 0.22), tb, 0.8 * g); add(bass(cc[0] + 12, 0.2), tb + BEAT / 2, 0.55 * g)
        if mel:
            for h in range(2):
                m = HOOK[(int(round((tb + h * BEAT / 2) / (BEAT / 2)))) % 16]
                if m: add(mari(m), tb + h * BEAT / 2, 0.75 * g, pan=0.2)
        if extra: add(pluck(cc[1 + b % 3] + 12, 0.5, 0.35 * g), tb + BEAT * 0.25, pan=-0.35)
def big(t0, g=1.0):
    add(boom(), t0, g, 0); add(crash(), t0, 0.7 * g); kk(t0, g); add(stab(list(chord(t0)[1:]), d=1.0, g=1.1 * g), t0)

big(HIT1)
groove(0.0, SCRATCH - BEAT, mel=False); pad(0.3, SCRATCH)
# "但其实" record-stop: pitch-down sweep, one beat of air, then back in
t = T(0.45); f = 900 * np.exp(-t * 6); add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) * 0.08, SCRATCH - BEAT)
add(wood(700), SCRATCH, 1.0); add(wood(1050), SCRATCH + 0.25, 0.8)
groove(SCRATCH + BEAT, 12.0); pad(SCRATCH + BEAT, 12.0)
groove(12.0, 18.0, extra=True); pad(12.0, 18.0)
groove(18.0, FREEZE - 0.0, mel=True); pad(18.0, FREEZE)
# freeze: music drops to a ticking clock + soft pad, a riser in the last second
for k in range(4): add(tick(), FREEZE + k * BEAT, 2.5); add(wood(1600, 0.4), FREEZE + k * BEAT + 0.02)
pad(FREEZE, HIT2 - 0.1, 0.7); add(riser(1.4), HIT2 - 1.4, 0.9)
big(HIT2, 1.1)
groove(HIT2, END, extra=True, g=1.05); pad(HIT2, END)
add(stab(list(chord(END)[1:]), d=0.6, g=0.6), END); add(mari(86), END, 0.8); add(mari(74), END + 0.25, 0.6)

duck = np.ones(N)
for k0 in KICKS:
    i = int(k0 * SR); n = min(N - i, int(0.28 * SR))
    if n > 0: duck[i:i + n] = np.minimum(duck[i:i + n], 1 - 0.5 * np.exp(-np.arange(n) / SR * 12))
L += PL * duck; R += PR * duck
dl = int(BEAT * 0.75 * SR); L[dl:] += R[:-dl] * 0.14; R[dl:] += L[:-dl] * 0.14
def reverb(x):
    n = int(1.2 * SR); tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt * 4); ir = np.convolve(ir, np.ones(5) / 5, 'same'); ir /= np.abs(ir).sum() ** 0.5 * 14
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x * 0.88 + np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[:len(x)] * 0.35
L = reverb(L); R = reverb(R)
st = np.stack([L, R], 1); st = np.tanh(st / np.abs(st).max() * 2.0); st /= np.abs(st).max() / 0.85
fo = int(0.4 * SR); st[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open('bgm.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
