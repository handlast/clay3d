exec(open('instr.py').read())
def lerp(a, b, k): return a + (b - a) * k
# ---- 《憋喷嚏》: black-key pentatonic, state-driven by airway pressure. Two big hits (HOOK_HIT, PRESS_HIT) + soft outro.
_add = add
hrng = np.random.default_rng(3)
def add(sig, t0, g=1.0, pan=0.0, human=True):  # humanize: +-10% velocity, +-6 ms timing
    if human: g *= 1 + hrng.uniform(-0.1, 0.1); t0 += hrng.uniform(-0.006, 0.006)
    _add(sig, max(0, t0), g, pan)

def pressure(t):  # 0..1 tension parameter that drives density / dissonance / filter
    if t < CASE: return 0.2
    if t < POP: return lerp(0.25, 0.75, (t - CASE) / (POP - CASE))
    if t < LEAK: return lerp(0.75, 0.85, (t - POP) / (LEAK - POP))
    if t < PRESS: return lerp(0.6, 1.0, (t - LEAK) / (PRESS - LEAK))
    return 0.3

def lowpass(y, k):
    n = max(1, int(k)); return np.convolve(y, np.ones(n) / n, 'same')
PHR = [[50, None, 54, 57, None, 54, 50, None], [50, None, 54, 57, None, 59, 57, None],   # 起 承
       [62, None, 59, 57, 54, None, 57, None], [54, None, 50, None, 47, None, 50, None]]  # 转 合 (落回主音)
def sneak(t0, t1, lift=0, g=1.0):
    nb = int((t1 - t0) / BEAT + 1e-6)
    for b in range(nb):
        tb = t0 + b * BEAT; p = pressure(tb)
        ph = PHR[(b // 8) % 4]; m = ph[b % 8]
        if m: add(lowpass(pluck(m + lift, 0.9, g), 1 + (1 - p) * 6), tb, 1.0, -0.2 if b % 2 else 0.2)
        add(tick(), tb, 1.0, 0.4)
        if hrng.random() < p * 0.8: add(pluck((m or 57) + 12 + lift, 0.4, 0.45 * g), tb + 0.25, pan=0.35)  # density grows with pressure
        if p > 0.7 and b % 4 == 2: add(pluck(56 + lift, 0.5, 0.35 * g), tb + 0.125, pan=-0.4)  # sharp 2nd: dissonant rub
        if b % 8 == 0: add(reed(38 + lift, 4.0, 0.6 + 0.4 * p), tb)
def full(t0, t1, chord, g=1.0):
    cc = CH[chord]
    for b in range(int((t1 - t0) / BEAT + 1e-6)):
        tb = t0 + b * BEAT; ph = PHR[(b // 8) % 4]; m = ph[b % 8]
        add(kick(), tb, (0.8 if b % 2 == 0 else 0.5) * g)
        if b % 2 == 1: add(snare(), tb, 0.5 * g)
        if hrng.random() < 0.25: add(hat(0.5), tb + 0.375, g)  # probabilistic fill
        add(hat(0.8), tb + 0.25, g)
        add(bass(cc[0] if b % 4 != 3 else cc[0] + 7), tb, 0.8 * g)
        add(pluck((m + 12) if m else cc[3], g=0.6 * g), tb + 0.25, pan=0.3)
        if b % 4 == 0: add(stab(list(cc[2:5]), d=1.6, g=0.4 * g), tb)
def big(t0, chord, g=1.0):
    add(boom(), t0, g, human=False); add(crash(), t0, g, human=False); add(kick(), t0, g, human=False); add(stab(list(CH[chord][1:]), d=1.2, g=1.2 * g), t0, human=False)
def ahh(t0, d, g=1.0):  # "ah... ah..." inhale: rising breathy vowel
    t = T(d); f = 180 * (2 ** (t / d * 1.0)); ph = 2 * np.pi * np.cumsum(f) / SR
    y = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)) * (t / d) ** 1.5 * 0.05
    y += lowpass(noise(d), 4) * (t / d) ** 2 * 0.03
    add(y * g, t0, human=False)
def crackle(t0, g=1.0):
    for k in range(6): add(tick(), t0 + k * 0.018, 2.5 * g, pan=hrng.uniform(-0.5, 0.5))

# 0-3.5 hook: inhale -> clamp (BIG 1)
ahh(0.0, HOOK_HIT); add(riser(HOOK_HIT), 0.0, 0.7)
big(HOOK_HIT, "gong", 1.2); add(chomp(1.2), HOOK_HIT)
for k in range(5):  # trapped tremble: muffled toms
    add(tom(40 + k, 0.5), HOOK_HIT + 0.5 + k * 0.25)
add(reed(38, 2.4, 0.7), 1.1); add(pluck(62, 1.2, 0.6), 2.5); add(pluck(66, 1.2, 0.6), 3.0)
# 3.5-12.5 sneaky build, pressure drives density
sneak(CASE, LEAK)
add(wood(900), CASE_HIT); add(wood(1200), AGE_HIT); add(pop(900), AGE_HIT + 0.4)
add(pop(600), POP, 2.0); add(tom(52, 0.8), POP); fizz(POP, 0.6, 0.8)
add(wood(700), HOLE_HIT); add(tom(45, 0.7), HOLE_HIT); fizz(HOLE_HIT, 1.2, 0.6)
# 12.5-15.5 bubbles leaking, pitch descending
for j, h in enumerate(LEAKS): add(bubble(900 - j * 110), h, 1.3, pan=0.3 - j * 0.15); add(pluck(PENTA[8 - j], 0.6, 0.5), h)
# 15.5-19.5 chest: heartbeat accelerates, crackles, riser into silence
sneak(CHEST, PRESS - 1.0, lift=12, g=0.7)
for k in range(12):
    tk = CHEST + 0.4 + 3.4 * (1 - (1 - k / 12) ** 1.6); add(kick(), tk, 0.45); add(kick(), tk + 0.14, 0.28)
for h in CRACK: crackle(h)
add(riser(1.0), PRESS - 1.0); add(reed(40, 4.0, 0.9), CHEST)
# PRESS_HIT: BIG 2, then groove
big(PRESS_HIT, "zhi", 1.3); zheng(PRESS_HIT + 0.1)
full(PRESS_HIT + 0.5, TUBE, "zhi")
add(wood(1300), KPA); add(crash(), KPA, 0.35)
# 27-30.5 tube: drums drop, woodblock per day, rising plucks
add(reed(42, 3.4, 0.6), TUBE); add(shimmer(3.4), TUBE)
for i, h in enumerate(DAYS): add(wood(900 + i * 60, 0.8), h); add(pluck(PENTA[i + 1], 0.8, 0.5), h)
# 30.5-34 car: light groove + bass, engine buzz
full(CAR, MM, "shang", 0.6); add(buzz(3.4, 0.6), CAR); add(wood(1100), CAR_HIT)
# 34-37.5 2mm: breakdown
breakdown(MM, HEAL, "jue"); add(pop(1400), MM_HIT, 1.4)
# 37.5-41 heal: arps build
add(crash(), HEAL_HIT, 0.4); zheng(HEAL_HIT, g=0.6)
for b in range(int((ADV - HEAL) / BEAT)):
    t0 = HEAL + b * BEAT; add(kick(), t0, 0.6); add(hat(0.7), t0 + 0.25); add(bass(38), t0, 0.6)
    for k in range(4): add(arp([62, 66, 69, 74][k] + (b // 2) % 3 * 2, 0.6), t0 + k * 0.125, pan=0.4 if k % 2 else -0.4)
# 41-44.3 advice: groove, sneeze released = light pop, tom fill
full(ADV, 43.3, "gong", 0.7); add(wood(1000), ADV_HIT); ahh(ADV_HIT, 0.6, 0.6); add(pop(500), ADV_HIT + 0.6, 1.6); fizz(ADV_HIT + 0.6, 0.8, 0.7)
for k, m in enumerate([62, 59, 57, 54, 50, 47, 45, 42]): add(tom(m - 12, 0.7), 43.3 + k * 0.125)
# outro: soft landing
add(crash(), OUTRO, 0.4)
for m_ in (38, 50, 57, 62, 66): add(piano(m_, 3.5, 1.1), OUTRO)
for i, t0 in enumerate((BUB1, BUB1 + 0.6, BUB2, BUB2 + 0.7)): add(pop(1300), t0, 1.2); add(pluck(PENTA[i + 2], 1.2, 0.7), t0)
zheng(47.0, n=5, g=0.7)

def delay(x, dt=0.375, fb=0.3, mixk=0.18):
    y = x.copy(); n = int(dt * SR); tap = x.copy()
    for k in range(3):
        tap = np.concatenate([np.zeros(n), tap[:-n]]) * fb; y += tap * mixk / fb
    return y
def reverb(x):
    n = int(1.6 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 3.5); ir = np.convolve(ir, np.ones(5) / 5, 'same'); ir /= np.abs(ir).sum() ** 0.5 * 14
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x * 0.85 + np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)] * 0.5
L, R = delay(L, 0.375), delay(R, 0.5)
L = reverb(L); R = reverb(R)
st = np.stack([L, R], 1)
for a, b in SILENCES: st[int(a * SR):int(b * SR)] *= 0.0
st = np.tanh(st / np.abs(st).max() * 2.2); st /= np.abs(st).max() / 0.85
with wave.open('bgm.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
