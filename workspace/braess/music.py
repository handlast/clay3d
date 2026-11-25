exec(open('instr.py').read())
# ---- 《布雷斯悖论》: black-key pentatonic (TRANS=4), state-driven by congestion. Two big hits (HOOK_HIT, SHORT_HIT) + soft outro.
# New long tones: soft detuned-sine piano pad, slow attack, mid register, strictly chord tones, cut at every chord change.
PL = np.zeros(N); PR = np.zeros(N)      # pad bus (side-chained to kicks)
KICKS = []
_add = add
hrng = np.random.default_rng(5)
def add(sig, t0, g=1.0, pan=0.0, human=True):  # humanize: +-10% velocity, +-6 ms timing
    if human: g *= 1 + hrng.uniform(-0.1, 0.1); t0 += hrng.uniform(-0.006, 0.006)
    _add(sig, max(0, t0), g, pan)
def kk(t0, g=1.0):
    add(kick(), t0, g); KICKS.append(t0)
def lerp(a, b, k): return a + (b - a) * k

def jam(t):  # 0..1 congestion = tension parameter (density, dissonance, filter)
    if t < HOOK_END: return 0.5
    if t < MODEL: return 0.25
    if t < SIL0: return lerp(0.3, 0.75, (t - MODEL) / (SIL0 - MODEL))
    if t < FIRST: return 0.4
    if t < ALL: return lerp(0.45, 1.0, (t - FIRST) / (ALL - FIRST))
    if t < BACK: return 0.95
    if t < CLOSE_HIT: return 0.75
    if t < OUTRO: return 0.25
    return 0.1
def lowpass(y, k):
    n = max(1, int(k)); return np.convolve(y, np.ones(n) / n, 'same')

# fixed harmonic frame: one chord per 2 bars (4 s), 宫-羽-商-徵 cycle
PROG = ["gong", "yu", "shang", "zhi"]
def chord_at(t): return PROG[int(t // 4.0) % 4]

def softpad(ms, d, bright=0.5, g=1.0):
    t = T(d); y = np.zeros(len(t)); ph = hrng.uniform(0, 6.28, 16)
    for i, m in enumerate(ms):
        f = hz(m)
        for j, c in enumerate((-0.0035, 0.0, 0.0035)):
            y += np.sin(2 * np.pi * f * (1 + c) * t + ph[(i * 3 + j) % 16]) * (0.8 if c else 1.0)
        y += 0.12 * bright * np.sin(2 * np.pi * 2 * f * t)
    att = np.clip(t / 0.6, 0, 1); rel = np.clip((d - t) / 0.35, 0, 1)
    env = (att * att * (3 - 2 * att)) * (rel * rel * (3 - 2 * rel))
    return lowpass(y * env, 2 + (1 - bright) * 6) * 0.0075 * g
def pad_span(t0, t1, g=1.0):  # lay pad chords on the 4-s grid between t0 and t1, cut at changes
    t = t0
    while t < t1 - 0.05:
        nxt = min(t1, (math.floor(t / 4.0) + 1) * 4.0)
        cc = CH[chord_at(t + 0.01)]
        ms = [cc[1], cc[2], cc[3]]                 # mid register: root+5th+octave area, chord tones only
        sig = softpad(ms, nxt - t + 0.05, 1 - jam(t) * 0.6, g)
        i = int(t * SR); s = sig[: N - i]
        PL[i:i + len(s)] += s * 1.0; PR[i:i + len(s)] += s * 0.92
        t = nxt
import math

PHR = [[50, None, 54, 57, None, 54, 50, None], [50, None, 54, 57, None, 59, 57, None],   # 起 承
       [62, None, 59, 57, 54, None, 57, None], [54, None, 50, None, 47, None, 50, None]]  # 转 合 (落回主音)
def sneak(t0, t1, lift=0, g=1.0):
    nb = int((t1 - t0) / BEAT + 1e-6)
    for b in range(nb):
        tb = t0 + b * BEAT; p = jam(tb)
        m = PHR[(b // 8) % 4][b % 8]
        if m: add(lowpass(pluck(m + lift, 0.9, g), 1 + (1 - p) * 6), tb, 1.0, -0.2 if b % 2 else 0.2)
        add(tick(), tb, 1.0, 0.4)
        if hrng.random() < p * 0.8: add(pluck((m or 57) + 12 + lift, 0.4, 0.45 * g), tb + 0.25, pan=0.35)
        if p > 0.75 and b % 4 == 2: add(pluck(56 + lift, 0.5, 0.3 * g), tb + 0.125, pan=-0.4)  # rub
def full(t0, t1, g=1.0):
    for b in range(int((t1 - t0) / BEAT + 1e-6)):
        tb = t0 + b * BEAT; cc = CH[chord_at(tb)]; m = PHR[(b // 8) % 4][b % 8]
        kk(tb, (0.8 if b % 2 == 0 else 0.5) * g)
        if b % 2 == 1: add(snare(), tb, 0.5 * g)
        if hrng.random() < 0.25: add(hat(0.5), tb + 0.375, g)
        add(hat(0.8), tb + 0.25, g)
        add(bass(cc[0] if b % 4 != 3 else cc[0] + 7), tb, 0.8 * g)
        add(pluck((m + 12) if m else cc[3], g=0.6 * g), tb + 0.25, pan=0.3)
def big(t0, chord, g=1.0):
    add(boom(), t0, g, human=False); add(crash(), t0, g, human=False); kk(t0, g); add(stab(list(CH[chord][1:]), d=1.2, g=1.2 * g), t0, human=False)
def honk(t0, g=1.0, m=66):  # cartoon car horn: two soft detuned squares, filtered
    t = T(0.18); f = hz(m)
    y = np.sign(np.sin(2 * np.pi * f * t)) + np.sign(np.sin(2 * np.pi * f * 1.26 * t))
    add(lowpass(y, 14) * np.exp(-t * 8) * np.minimum(1, t / 0.01) * 0.025 * g, t0, pan=hrng.uniform(-0.5, 0.5))

# 0-3.5 hook: BIG 1 on the barrier slam
add(riser(0.3), 0.0, 0.8)
for k in range(3): honk(0.02 + k * 0.08, 0.8, 66 + k)
big(HOOK_HIT, "gong", 1.2); zheng(HOOK_HIT + 0.55, g=0.8)
for k in range(6):
    tk = HOOK_HIT + 0.5 + k * BEAT; kk(tk, 0.5); add(bass(38), tk, 0.6); add(hat(0.8), tk + 0.25)
pad_span(0.8, HOOK_END, 0.9)
# 3.5-12.5 cases: sneaky plucks + clock; light SFX per beat
sneak(NYC, MODEL); pad_span(NYC, MODEL, 0.8)
add(wood(1000), NYC_HIT); add(tom(45, 0.6), NYC_HIT); honk(NYC_HIT + 0.3, 0.6)
add(pop(900), NYC2_HIT, 1.2); for_ = [add(pluck(m, 0.5, 0.55), NYC2_HIT + 0.05 + i * 0.06) for i, m in enumerate([62, 66, 69, 74])]
add(tom(40, 0.8), SEOUL_HIT); fizz(SEOUL_HIT, 1.0, 0.8); add(wood(700), SEOUL_HIT + 0.9)
add(wood(1200), WHY_HIT); add(pop(600), WHY_HIT + 0.6, 1.0)
# 12.5-19.5 model: each road a pluck, rules = woodblocks; jam rises; heartbeat + riser into silence
pad_span(MODEL, SIL0, 0.9)
sneak(MODEL, SPLIT)
for i, h in enumerate(ROADS): add(pluck(PENTA[2 + i * 2], 0.8, 0.7), h); add(pop(800 + i * 300), h)
for i, h in enumerate(RULE_HITS): add(wood(900 + i * 300), h)
add(crash(), SPLIT_HIT, 0.25); add(stab([62, 66, 69], 1.4, 0.45), SPLIT_HIT)
for i in range(9):
    tk = SPLIT + 0.2 + 1.85 * (1 - (1 - i / 9) ** 1.6); add(kick(), tk, 0.45); add(kick(), tk + 0.14, 0.28)
add(riser(1.1), 18.9, 0.9)
# 20.0 BIG 2: shortcut appears, then groove
big(SHORT_HIT, "zhi", 1.3); zheng(SHORT_HIT + 0.1)
full(SHORT_HIT + 0.5, FIRST); pad_span(SHORT_HIT + 0.3, FIRST, 0.8)
# 22.5-27.5 everybody switches: density driven by jam, horns multiply
add(wood(1300), FIRST_HIT); add(stab([66, 69, 74], 1.0, 0.4), FIRST_HIT)
sneak(FIRST, ALL); pad_span(FIRST, ALL, 0.8)
tt = RUSH; k = 0
while tt < ALL:
    honk(tt, 0.4 + 0.5 * jam(tt), [66, 69, 71, 74][k % 4]); tt += 0.5 * (1 - 0.7 * (tt - RUSH) / (ALL - RUSH)); k += 1
for b in range(int((ALL - RUSH) / BEAT)): kk(RUSH + b * BEAT, 0.35 + 0.1 * b / 5)
# 27.8 80 min: tom + wood + dissonant rub, no big boom
add(tom(38, 0.9), ALL_HIT); add(wood(500), ALL_HIT); add(pluck(56, 0.8, 0.6), ALL_HIT + 0.05); add(pluck(62, 0.8, 0.6), ALL_HIT + 0.05)
pad_span(ALL, CLOSE, 0.7)
sneak(ALL + 0.5, BACK, lift=-12)
# 31-35.5 breakdown: no drums; heartbeat; ticking clock
add(pop(500), BACK_HIT, 1.2); add(tom(42, 0.7), BACK_HIT)
for i in range(int((CLOSE - BACK) / 0.25)): add(wood(1200 if i % 2 else 900, 0.35), BACK + i * 0.25)
add(wood(800), NASH_HIT); add(pluck(56, 0.6, 0.4), NASH_HIT + 0.9); add(tom(40, 0.6), NASH_HIT + 0.9)
add(riser(0.5), 35.4, 0.7)
# 35.9 relief: soft crash + chord + shimmer, arp push
add(crash(), CLOSE_HIT, 0.35); add(stab([62, 66, 69, 74], 1.6, 0.8), CLOSE_HIT); add(shimmer(1.6), CLOSE_HIT, 1.2)
pad_span(CLOSE_HIT, OUTRO, 0.9)
add(pop(1400), CLOSE_HIT + 0.9, 1.2); for_ = [add(pluck(m, 0.5, 0.5), CLOSE_HIT + 0.95 + i * 0.05) for i, m in enumerate([74, 78, 81, 86])]
for b in range(int((NAME - 37.0) / BEAT)):
    t0 = 37.0 + b * BEAT; kk(t0, 0.55); add(hat(0.7), t0 + 0.25); add(bass(CH[chord_at(t0)][0]), t0, 0.6)
    for k in range(4): add(arp([62, 66, 69, 74][k] + (b // 2) % 3 * 2, 0.55), t0 + k * 0.125, pan=0.4 if k % 2 else -0.4)
# 39-44 name + real-world: light groove
add(wood(1000), NAME_HIT); add(stab([64, 69, 71, 76], 1.4, 0.7), NAME_HIT)
full(NAME + 0.5, 43.4, 0.7)
add(wood(1100), REAL2_HIT); add(wood(1300), REAL2_HIT + 0.35)
for k, m in enumerate([62, 59, 57, 54, 50, 47, 45, 42]): add(tom(m - 12, 0.55), 43.0 + k * 0.125)
# outro: soft piano chord, pops per bubble
add(crash(), OUTRO, 0.3)
for m_ in (38, 50, 57, 62, 66): add(piano(m_, 3.5, 1.0), OUTRO)
pad_span(OUTRO, DUR - 0.3, 0.7)
for i, t0 in enumerate(BUBS): add(pop(1300), t0, 1.2); add(pluck(PENTA[i + 2], 1.2, 0.7), t0)
zheng(47.0, n=5, g=0.5)

# ---- mix: side-chain pad to kicks, delay on plucks bus (whole mix, light), reverb, glue
tt_ = np.arange(N) / SR; duck = np.ones(N)
for k0 in KICKS:
    i = int(k0 * SR); n = min(N - i, int(0.3 * SR))
    if n > 0: duck[i:i + n] = np.minimum(duck[i:i + n], 1 - 0.45 * np.exp(-np.arange(n) / SR * 12))
L += PL * duck; R += PR * duck
dl = int(0.375 * SR)
L[dl:] += R[:-dl] * 0.18; R[dl:] += L[:-dl] * 0.18
def reverb(x):
    n = int(1.6 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 3.5); ir = np.convolve(ir, np.ones(5) / 5, 'same'); ir /= np.abs(ir).sum() ** 0.5 * 14
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x * 0.85 + np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)] * 0.45
L = reverb(L); R = reverb(R)
st = np.stack([L, R], 1)
for a, b in SILENCES: st[int(a * SR):int(b * SR)] *= 0.0
st = np.tanh(st / np.abs(st).max() * 2.2); st /= np.abs(st).max() / 0.85
with wave.open('bgm.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
