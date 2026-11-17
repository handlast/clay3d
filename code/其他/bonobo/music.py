# 《倭黑猩猩打猎，主力居然是母的？》BGM — "jungle tribal drums x trap queen entrance"
# A minor pentatonic (A C D E G), 140.8 BPM written as half-time trap (clap on beat 3 = 70.4 feel).
# Loop: 4-bar harmony Am - F - G - Em (808 roots A1 F1 G1 E1), 2-bar conga/bongo polyrhythm, 2-bar kalimba hook.
# Grid: 11 bars 4/4 + one 2/4 bar so 0.4 s (bar 0) and 20.0 s (bar 12) are both downbeats.
# Two big hits only (HOOK_HIT, BIG2): 808 boom + brass stab + crash. Everything else is light SFX.
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import gm as _gm, drum as _drum, SR
from cues import *
# per-preset level (measured peaks at vel 110: Kalimba 0.76, Marimba 8.4, Brass 1.6, Taiko 4.3, Glock 0.87, Wood Block 5.3)
LV = {"Kalimba": 1.0, "Marimba": 0.1, "Brass Section": 0.5, "Taiko Drum": 0.2, "Glockenspiel": 1.0, "Wood Block": 0.16,
      "Tinker Bell": 1.0, "Pizzicato Strings": 1.0}
@functools.lru_cache(maxsize=None)
def gm(name, m, dur=0.5, vel=100, release=0.3, decay=None): return _gm(name, m, dur, vel, release=release, decay=decay) * LV.get(name, 1.0)
# 808/909 kit: kick 36, clap 39, hats 42/46 (0.3/0.46 peak -> boosted), crash 49; Standard kit: congas/bongos/shaker/claves
@functools.lru_cache(maxsize=None)
def drum(n, vel=100, kit="Standard 1"):
    g = {("808/909", 42): 2.6, ("808/909", 46): 1.7, ("808/909", 49): 1.3}.get((kit, n), 1.0)
    return _drum(n, vel, kit=kit) * g
def k8(n, vel=100): return drum(n, vel, "808/909")
N = int(SR * DUR)
DRY = np.zeros((N, 2)); SCB = np.zeros((N, 2)); VERB = np.zeros((N, 2))
rng = np.random.default_rng(11)
KICKS = []
def add(y, t0, g=1.0, pan=0.0, wet=0.0, bus="sc", human=True):
    if human: g *= 1 + rng.uniform(-0.06, 0.06); t0 += rng.uniform(-0.003, 0.003)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    (DRY if bus == "dry" else SCB)[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet
def mono(y): return np.stack([y, y], 1)
def lerp_(a, b, k): return a + (b - a) * max(0, min(1, k))
def mf(m): return 440 * 2 ** ((m - 69) / 12)

# ---------------- grid ----------------
def bar_list():
    out = [(G0 + i * BAR, 4, i) for i in range(11)] + [(G0 + 44 * BEAT, 2, 11)]
    j = 0
    while G1 + j * BAR < DUR: out.append((G1 + j * BAR, 4, 12 + j)); j += 1
    return out
BARS = bar_list()
def bars_in(t0, t1): return [b for b in BARS if t0 - 1e-6 <= b[0] < t1 - 1e-6]
CH = [("Am", 33, (69, 72, 76)), ("F", 29, (65, 69, 72)), ("G", 31, (67, 71, 74)), ("Em", 28, (64, 67, 71))]
def chord_of(bi): return CH[bi % 4]
def ev(t0, t1, pattern, fn):
    """pattern: list of beat offsets inside a bar; fn(time, bar_index, offset) for each hit in [t0, t1)."""
    for tb, L, bi in bars_in(t0 - BAR, t1):
        for o in pattern:
            tt = tb + o * BEAT
            if o < L and t0 - 1e-6 <= tt < t1 - 1e-6: fn(tt, bi, o)

# ---------------- synths ----------------
def sub808(t0, dur, m0, m1=None, glide=0.06, g=1.0):
    n = int((dur + 0.03) * SR); tt = np.arange(n) / SR
    f0, f1 = mf(m0), mf(m1 if m1 is not None else m0)
    f = f1 + (f0 - f1) * np.exp(-tt / max(glide / 3, 1e-3)) if m1 is not None else np.full(n, f0)
    f = f * (1 + 0.6 * np.exp(-tt * 60))   # tiny pitch punch
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + 0.18 * np.sin(2 * ph)
    env = np.minimum(1, tt / 0.003) * np.exp(-tt * 1.1) * np.clip((dur + 0.03 - tt) / 0.03, 0, 1)
    y = np.tanh(y * env * 2.2) * 0.55
    add(mono(y), t0, g, bus="dry", human=False)
def kick(t0, g=1.0):
    KICKS.append(t0); add(k8(36, 120), t0, 0.75 * g, bus="dry", human=False)
    tt = np.arange(int(0.012 * SR)) / SR; add(mono(rng.standard_normal(len(tt)) * np.exp(-tt * 400) * 0.25), t0, g, bus="dry", human=False)
def clap(t0, g=1.0, wet=0.2): add(k8(39, 115), t0, 0.6 * g, wet=wet, bus="dry")
def hat(t0, g=1.0, open_=False, pan=0.25): add(k8(46 if open_ else 42, 90), t0, 0.32 * g, pan=pan)
def noise(n, smooth=1):
    x = rng.standard_normal(n)
    return np.convolve(x, np.ones(smooth) / smooth, "same") if smooth > 1 else x
def hp(x, k=0.97): y = np.copy(x); y[1:] = x[1:] - k * x[:-1]; return y
def rustle(t0, dur=0.6, g=1.0, pan=0.0):   # leaves: grainy high noise with random crackle envelope
    n = int(dur * SR); tt = np.arange(n) / SR
    grain = np.repeat(rng.uniform(0.2, 1.0, n // 300 + 1), 300)[:n]
    y = hp(noise(n)) * grain * np.sin(np.pi * tt / dur) ** 0.7 * 0.1
    add(mono(y), t0, g, pan=pan, wet=0.2, bus="dry", human=False)
def whoosh(t0, t1, g=1.0, up=True):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR; k = tt / (t1 - t0)
    out = np.zeros(n); x = noise(n); lp = 0.0
    a = (0.02 + 0.5 * k) if up else (0.5 - 0.45 * k)
    for i0 in range(0, n, 512):   # time-varying one-pole low-pass
        seg = x[i0:i0 + 512]; aa = a[i0]; o = np.empty_like(seg)
        for j, v in enumerate(seg): lp += aa * (v - lp); o[j] = lp
        out[i0:i0 + 512] = o
    add(mono(out * (k ** 2 if up else (1 - k)) * 0.25), t0, g, wet=0.3, bus="dry", human=False)
def twang(t0, g=1.0, f0=330):   # branch springing back: "boing"
    n = int(0.45 * SR); tt = np.arange(n) / SR
    f = f0 * (0.55 + 0.45 * np.exp(-tt * 8)) * (1 + 0.06 * np.sin(2 * np.pi * 22 * tt))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7) * 0.22
    add(mono(y), t0, g, wet=0.2, bus="dry", human=False)
def chirp(t0, g=1.0, pan=0.0, n_=4):   # monkey squeaks
    for j in range(n_):
        n = int(0.07 * SR); tt = np.arange(n) / SR
        f = 1400 + 1800 * (tt / 0.07) ** 0.6 + 200 * j
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.07) * 0.12
        add(mono(y), t0 + j * 0.085, g, pan=pan, wet=0.15, bus="dry", human=False)
def click(t0, g=1.0):   # counter "ka"
    n = int(0.018 * SR); tt = np.arange(n) / SR
    add(mono(hp(noise(n)) * np.exp(-tt * 300) * 0.35), t0, g, pan=0.2, bus="dry", human=False); add(drum(75, 100), t0, 0.18 * g, pan=0.2, bus="dry", human=False)
def flip(t0, g=1.0):    # calendar page: short swish + paper snap
    n = int(0.14 * SR); tt = np.arange(n) / SR
    add(mono(hp(noise(n), 0.8) * np.sin(np.pi * tt / 0.14) * 0.12), t0, g, pan=-0.2, bus="dry", human=False); click(t0 + 0.12, 0.5 * g)
def boom(t0, g=1.0, dur=1.6):
    tt = np.arange(int(dur * SR)) / SR; f = 41 + 90 * np.exp(-tt * 14)
    add(mono(np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 1.6) * 2.0) * 0.6), t0, g, bus="dry", human=False)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR; k = tt / (t1 - t0)
    f = 200 * 2 ** (3 * k); tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.05
    y = (hp(noise(n), 0.9) * 0.06 + tone) * k ** 2.2
    add(mono(y), t0, g, wet=0.3, bus="dry", human=False)
def ding(t0, m=88, g=1.0, pan=0.0): add(gm("Glockenspiel", m, 0.6, 105), t0, 0.4 * g, pan=pan, wet=0.4, bus="dry")
def kal(t0, m, g=1.0, dur=0.5, pan=0.0, wet=0.25): add(gm("Kalimba", m, dur, 105, 0.3), t0, 0.55 * g, pan=pan, wet=wet)
def brass(t0, g=1.0, notes=(57, 60, 64, 69)):
    for m in notes: add(gm("Brass Section", m, 0.5, 120, 0.25), t0, 0.32 * g, wet=0.3, bus="dry")
def big(t0, g=1.0):
    boom(t0, 1.1 * g); kick(t0, 1.2 * g); add(k8(49, 127), t0, 0.7 * g, wet=0.4, bus="dry"); add(drum(57, 110), t0, 0.35 * g, pan=-0.4, bus="dry")
    brass(t0, 1.3 * g); add(gm("Taiko Drum", 41, 1.0, 127), t0, 0.7 * g, wet=0.3, bus="dry")
    brass(t0 + BEAT * 0.75, 0.6 * g, (60, 64, 69))   # short "da-DAA" pickup tail, still part of the one accent

# ---------------- parts ----------------
# kick/808 patterns (beats) - A and B alternate; 808 note follows each kick
KPA = [0, 0.75, 1.5, 3.25]; KPB = [0, 1.5, 2.5, 3.5]
def trap(t0, t1, g=1.0, hats="16", eight=True, claps=True, kicks=True, gap=None):
    last = {}
    def k_(tt, bi, o):
        if gap and gap[0] <= tt < gap[1]: return
        if kicks: kick(tt, 0.9 * g)
        if eight:
            _, r, _ = chord_of(bi); pat = KPA if bi % 2 == 0 else KPB
            idx = pat.index(o); nxt = pat[idx + 1] if idx + 1 < len(pat) else 4
            dur = (nxt - o) * BEAT; m0 = r + (12 if (bi % 4 == 3 and o == 3.5) else 0)
            glide_from = last.get("m")
            if bi % 4 == 3 and o >= 3.25:   # every 4 bars: big slide up an octave into the next downbeat
                sub808(tt, dur, r, r + 12, glide=dur * 0.9, g=g)
            elif glide_from is not None and glide_from != r and o == 0:
                sub808(tt, dur, glide_from, r, glide=0.07, g=g)
            else: sub808(tt, dur, r, g=g)
            last["m"] = r
    for tb, L, bi in bars_in(t0 - BAR, t1):
        for o in (KPA if bi % 2 == 0 else KPB):
            tt = tb + o * BEAT
            if o < L and t0 - 1e-6 <= tt < t1 - 1e-6: k_(tt, bi, o)
    if claps: ev(t0, t1, [2], lambda tt, bi, o: None if gap and gap[0] <= tt < gap[1] else clap(tt, g))
    if hats:
        step = 0.5 if hats == "8" else 0.25
        def h_(tt, bi, o):
            if gap and gap[0] <= tt < gap[1]: return
            if bi % 2 == 1 and o >= 3: return    # roll slot
            hat(tt, g * (1.0 if (o * 4) % 2 == 0 else 0.6))
        ev(t0, t1, [i * step for i in range(int(4 / step))], h_)
        def roll(tt, bi, o):   # triplet 16th hat roll on beat 4 of every 2nd bar, swelling
            if bi % 2 == 1 and not (gap and gap[0] <= tt < gap[1]):
                for j in range(6): hat(tt + j * BEAT / 6, g * (0.45 + 0.12 * j), pan=0.25 - 0.1 * j)
        ev(t0, t1, [3], roll)
# 2-bar tribal polyrhythm on a 16th grid (32 steps): low conga 64, open hi conga 63, mute hi conga 62, bongos 60/61, shaker 70
CONGA = {64: [0, 6, 10, 16, 22, 26], 63: [3, 8, 12, 19, 24, 28, 30], 62: [2, 14, 18, 31], 60: [0, 3, 6, 16, 19, 22], 61: [10, 12, 26, 28]}
CLV = {64: 0.42, 63: 0.32, 62: 0.25, 60: 0.22, 61: 0.2}
def tribal(t0, t1, g=1.0, shaker=True, only=None):
    for tb, L, bi in bars_in(t0 - BAR, t1):
        for n_, steps in CONGA.items():
            if only and n_ not in only: continue
            for s in steps:
                if (s // 16) != bi % 2: continue
                o = (s % 16) / 4; tt = tb + o * BEAT
                if o < L and t0 - 1e-6 <= tt < t1 - 1e-6: add(drum(n_, 100), tt, CLV[n_] * g, pan={64: -0.3, 63: -0.15, 62: 0.1, 60: 0.35, 61: 0.4}[n_], wet=0.1)
        if shaker:
            for j in range(16):
                o = j / 4; tt = tb + o * BEAT
                if o < L and t0 - 1e-6 <= tt < t1 - 1e-6: add(drum(70, 80), tt, 0.12 * g * (1 if j % 2 else 0.6), pan=0.45)
# kalimba hook (2 bars per harmony pair; minor pentatonic), (beat, midi)
HOOK = [[(0, 76), (0.5, 69), (1, 72), (1.5, 76), (2, 74), (2.75, 72), (3, 69), (3.5, 67)],
        [(0, 69), (0.5, 72), (1, 76), (1.5, 79), (2, 76), (2.5, 74), (3, 72), (3.5, 74)],
        [(0, 74), (0.5, 67), (1, 69), (1.5, 74), (2, 76), (2.75, 74), (3, 72), (3.5, 69)],
        [(0, 67), (0.5, 76), (1, 74), (1.5, 76), (2, 79), (2.5, 76), (3, 74), (3.5, 72)]]
def hook(t0, t1, g=1.0, oct=0, sparse=False):
    for tb, L, bi in bars_in(t0 - BAR, t1):
        for o, m in HOOK[bi % 4]:
            if sparse and (o * 2) % 2: continue
            tt = tb + o * BEAT
            if o < L and t0 - 1e-6 <= tt < t1 - 1e-6: kal(tt, m + oct, g * (1.0 if o in (0, 2) else 0.8), pan=0.15 if (o * 2) % 2 else -0.1)
def marim(t0, t1, g=1.0):   # 3-3-2 chord-tone counter, low marimba
    for tb, L, bi in bars_in(t0 - BAR, t1):
        _, r, v = chord_of(bi)
        for k, o in enumerate([0, 0.75, 1.5, 2, 2.75, 3.5]):
            tt = tb + o * BEAT
            if o < L and t0 - 1e-6 <= tt < t1 - 1e-6: add(gm("Marimba", v[k % 3] - 12, 0.3, 100), tt, 0.5 * g, pan=-0.3, wet=0.15)
def heartbeat(times, g=1.0):
    for tt in times: add(drum(64, 110), tt, 0.55 * g, wet=0.2); add(drum(64, 80), tt + 0.16, 0.35 * g, wet=0.2); sub808(tt, 0.3, 21, g=0.5 * g)

# ---------------- arrangement ----------------
# 0 - 0.4: dive. leaves rustle + whoosh + snare-ish clap flam into hit 1
rustle(0.0, 0.45, 1.2); whoosh(0.0, HOOK_HIT, 1.2)
for j in range(4): clap(HOOK_HIT - 0.2 + j * 0.05, 0.25 + 0.15 * j, 0.1)
big(HOOK_HIT)
rustle(HOOK_HIT + 0.02, 0.9, 1.4, -0.3); rustle(HOOK_HIT + 0.1, 0.8, 1.0, 0.3)
trap(HOOK_HIT + 0.01, HOOK_STOP, 1.0, "16"); tribal(HOOK_HIT, HOOK_STOP, 0.9); hook(HOOK_HIT, HOOK_STOP, 1.0)
twang(LAND, 0.9, 420); ding(LAND + 0.05, 91, 0.6)
# 2.74 hard stop -> kalimba pickup into the hand-drum loop
for j, m in enumerate([67, 69, 72]): kal(HOOK_STOP + 0.15 + j * BEAT / 2, m, 0.8)
# 3.38 - 7.64 stereotype: hand drums only + soft kalimba (sparse), bongo pops for each painted figure
tribal(STEREO, CHIMP, 1.6); hook(STEREO, CHIMP, 0.9, sparse=True)
for j, h in enumerate(PAINT): add(drum(60, 115), h, 0.4, pan=0.3); kal(h, [79, 81, 84][j], 0.7, wet=0.4)
add(gm("Marimba", 52, 0.4, 110), QMARK, 0.7, wet=0.3); add(gm("Marimba", 51, 0.5, 110), QMARK + 0.18, 0.7, wet=0.3); add(drum(64, 120), QMARK, 0.5)
# 7.64 - 11.48 chimps: add 808 + light kick (no clap), group stomps on hops
trap(CHIMP, TEN, 0.75, hats=None, claps=False); tribal(CHIMP, TEN, 0.9); hook(CHIMP, TEN, 0.7)
for h in CHIMP_HOPS: add(gm("Taiko Drum", 45, 0.6, 110), h, 0.45, wet=0.2, bus="dry"); add(drum(64, 110), h + 0.08, 0.4)
ding(CHIMP_TAG, 86, 0.6); kal(MEAT_TAG, 81, 0.8); kal(MEAT_TAG + 0.12, 84, 0.7)
# 11.48 - 15.31 ten years: hats + claps join; calendar flips, counter clicks, ding at 415
trap(TEN, PIE, 0.85, hats="8"); tribal(TEN, PIE, 0.8, shaker=False); hook(TEN, PIE, 0.8)
ding(TENT, 84, 0.6)
for j in range(9): flip(CAL[0] + j * (CAL[1] - CAL[0]) / 9, 0.9)
nclk = 24
for j in range(nclk): click(CNT[0] + (CNT[1] - CNT[0]) * (1 - (1 - j / nclk) ** 1.6), 0.8)
ding(CNT[1], 88, 1.0); ding(CNT[1] + 0.08, 93, 0.7)
# 15.31 - 19.57 suspense: only hand-drum heartbeat + riser; pie spin "ding" on every heartbeat
hb = [qb(36 + i) for i in range(0, 10, 2)] + [qb(41 + i) for i in range(4)] + [qb(43.5), qb(44.5)]
heartbeat(hb, 1.0)
for j, h in enumerate(hb): ding(h + 0.02, [76, 79, 76, 81, 76, 79, 81, 84, 86, 88, 91][j % 11], 0.35 + 0.04 * j, pan=0.3 * (-1) ** j)
tribal(PIE, RISE[0], 0.8, shaker=False, only=(62,))
riser(RISE[0] - 1.0, SIL0, 1.2); whoosh(SIL0 - 0.9, SIL0, 0.8)
# 19.57 - 20.0 silence ; 20.0 hit 2 -> full trap drop (drop gap = beat 77 before bar 8 for the x3 triple hit)
big(BIG2, 1.1)
GAP = (qb(77) - 0.02, qb(78) - 0.02)
trap(BIG2 + 0.01, SHARE, 1.0, "16", gap=GAP); tribal(BIG2, SHARE, 0.75); hook(BIG2, SHARE, 1.0); marim(BIG2, SHARE, 0.8)
for j, h in enumerate(REV_TAGS): kal(h, [84, 81][j], 0.8, wet=0.4)
kal(INIT_TAG, 88, 0.7); kal(INIT_TAG + 0.1, 91, 0.6)
add(gm("Marimba", 45, 0.3, 110), NO_STEAL, 0.6); add(gm("Marimba", 44, 0.4, 110), NO_STEAL + 0.2, 0.6)
for h in BABY_STEPS[::2]: add(drum(61, 110), h, 0.3, pan=0.3)
ding(BABY_TAG, 91, 0.6)
for j, h in enumerate(SWINGS): twang(h - 0.05, 0.8, [300, 360, 420][j]); rustle(h - 0.1, 0.4, 0.9, 0.3 * (-1) ** j)
chirp(MONKEY_HIT - 0.05, 1.0, 0.35, 5)
ding(EQ, 84, 0.6); ding(EQ + 0.15, 84, 0.6, 0.3)
for j, h in enumerate(X3):   # "x3" triple hit inside the drum gap, landing on the bar line
    add(gm("Taiko Drum", 41, 0.6, 127), h, 0.6 + 0.15 * j, wet=0.3, bus="dry"); clap(h, 0.6 + 0.2 * j); sub808(h, 0.18, 33 + 12 * (j == 2), g=0.6)
for j, m in enumerate([69, 72, 74, 76, 79, 81]): kal(BARS3 + j * 0.05, m, 0.6)
# 36.19 - 39.6 breakdown: 808 + clap only, bells for "who eats first"
trap(SHARE, CULT, 0.95, hats=None, kicks=False)
for j, h in enumerate(BELLS): ding(h, [91, 88, 91, 88, 96][j], 0.8, 0.2 * (-1) ** j); add(gm("Tinker Bell", 84, 0.3, 100), h + 0.06, 0.25, wet=0.4)
riser(CULT - 1.2, CULT, 0.6)
# 39.6 - 42.58 two groups: full groove back; group A hoof clops (left), group B monkey chirps (right)
trap(CULT, HUMAN, 1.0, "16"); tribal(CULT, HUMAN, 0.8); hook(CULT, HUMAN, 0.95); marim(CULT, HUMAN, 0.7)
for j in range(4): add(gm("Wood Block", 77 - (j % 2), 0.2, 110), GROUPA + j * 0.11, 0.5, pan=-0.5)
chirp(GROUPB, 0.9, 0.5, 4); kal(CARD1, 81, 0.8, wet=0.4); kal(CARD1 + 0.1, 84, 0.7, wet=0.4)
ding(CULT_TAG, 88, 0.8); ding(CULT_TAG + 0.09, 93, 0.6, 0.3)
# 42.58 - 44.71 humans: lighter - kalimba hook + hand drums + 808 without hats
trap(HUMAN, OUTRO, 0.8, hats="8", claps=True, kicks=True); tribal(HUMAN, OUTRO, 0.7, shaker=False); hook(HUMAN, OUTRO, 0.9)
for j, m in enumerate([76, 79, 81, 84, 88]): kal(FEM_ADD + j * 0.05, m, 0.6, wet=0.4)
ding(ANC_TAG, 86, 0.5)
# 44.71 - 47 outro: clean ending (no long pad): last hook phrase, peace "ding", bubble pop, final clap + 808 glide down
hook(OUTRO, PEACE, 0.9); tribal(OUTRO, FINAL, 0.6, shaker=False, only=(64, 63))
ding(PEACE, 93, 0.8); kal(BUB, 84, 0.8)
kick(FINAL, 0.9); clap(FINAL, 0.7, 0.4); sub808(FINAL, 1.2, 33, 21, glide=1.0, g=0.9)
for j, m in enumerate([57, 64, 69, 72, 76]): kal(FINAL + j * 0.03, m, 0.7, 1.0, wet=0.4)

# ---------------- mix ----------------
duck = np.ones(N); tt = np.arange(int(0.35 * SR)) / SR; shape = 1 - 0.55 * np.exp(-tt / 0.09)
for k in KICKS:
    i = int(k * SR); seg = duck[i:i + len(shape)]; duck[i:i + len(shape)] = np.minimum(seg, shape[:len(seg)])
MIX = DRY + SCB * duck[:, None]
def conv(x, ir):
    sz = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
n = int(1.5 * SR); t_ = np.arange(n) / SR
ir = rng.standard_normal(n) * np.exp(-t_ * 3.6); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
MIX += np.stack([conv(VERB[:, 0], ir), conv(VERB[:, 1], ir * 0.97)], 1) * 0.5
for a, b in SILENCES:
    i0, i1 = int(a * SR), int(b * SR); fade = np.linspace(1, 0, int(0.03 * SR))
    MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] = 0
i0 = int(HOOK_STOP * SR); fade = np.linspace(1, 0, int(0.025 * SR))   # hard stop at 2.74 s

MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):int((HOOK_STOP + 0.14) * SR)] = 0
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.4); MIX /= np.abs(MIX).max() / 0.89
fo = int(0.4 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * math.log10(max(1e-6, float(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean())))) for i in range(0, int(DUR), 2)]
print("BPM %.2f" % BPM, "kicks", len(KICKS))
print("rms/2s dB:", " ".join(f"{i*2}:{v:.0f}" for i, v in enumerate(r)))
print("ok")
