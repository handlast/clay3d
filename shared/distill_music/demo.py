# demo.py — A/B of the proposed BGM mix chain on a 2-bar loop (108 BPM, D phrygian-dominant, same GM sampler).
#   0-4.9 s  BEFORE: current method (sum buses -> noise-IR reverb -> normalize -> tanh(1.8x) -> normalize)
#   5-10 s   AFTER : same notes + Euclidean conga, voice-led chords, humanize, per-bus EQ,
#                    kick-keyed sidechain duck on bass+mid, pedalboard Reverb send (HPF'd), glue comp, limiter.
# run: PYTHONPATH=/workspace/.pylib python3 demo.py   (~10-20 s on 2 cores)
import sys, time, wave, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import gm, drum, SR
from pedalboard import (Pedalboard, HighpassFilter, LowpassFilter, LowShelfFilter, PeakFilter,
                        Compressor, Reverb, Limiter, Gain)
t_start = time.time()
BEAT = 60 / 108; S16 = BEAT / 4; BAR = 4 * BEAT; LOOP = 2 * BAR          # 4.44 s
N = int(SR * 5.0)
SC = [62, 63, 66, 67, 69, 70, 72]
def deg(i, base=0): o, r = divmod(i, 7); return SC[r] + 12 * o + base
RIFF = [(0, 0, 1), (1, 1, 1), (2, 2, 1), (3, 3, 2), (6, 4, 1), (7, 3, 1), (8, 4, 2), (10, 6, 1), (11, 5, 1), (12, 4, 1), (13, 3, 1), (14, 2, 1), (15, 1, 1)]
PROG = ["D", "Eb"]; ROOT = {"D": 38, "Eb": 39}
CHORD_PC = {"D": (2, 6, 9), "Eb": (3, 7, 10)}           # pitch classes

# ---------- technique helpers ----------
def euclid(k, n, rot=0):
    """Bjorklund/Toussaint: k onsets spread over n steps (same result as strudel euclid / Tidal (k,n,rot))."""
    pat = [((i * k) % n) < k for i in range(n)]          # bresenham form == bjorklund up to rotation
    return pat[rot % n:] + pat[:rot % n]

def voice_lead(prev, pcs, lo=55, hi=74):
    """choose the voicing of pitch classes pcs (one note each) inside [lo,hi] that minimizes total semitone movement from prev."""
    import itertools
    cands = [[m for m in range(lo, hi + 1) if m % 12 == pc] for pc in pcs]
    best = None
    for v in itertools.product(*cands):
        v = sorted(v)
        if v[-1] - v[0] > 12: continue                   # keep within an octave (close/open-ish)
        cost = sum(abs(a - b) for a, b in zip(v, prev)) if prev else abs(np.mean(v) - 64)
        if best is None or cost < best[0]: best = (cost, v)
    return best[1]

rng = np.random.default_rng(7)
def human(t, vel, on_beat):
    """timing jitter ±(4 ms on-beat, 8 ms off-beat), velocity ±8%, off-beats 15% softer."""
    j = 0.004 if on_beat else 0.008
    return t + rng.uniform(-j, j), vel * (1 + rng.uniform(-0.08, 0.08)) * (1.0 if on_beat else 0.85)

def norm(y, pk=0.5): return y / (np.abs(y).max() + 1e-9) * pk
def put(buf, y, t, g=1.0, pan=0.0):
    if y.ndim == 1: y = np.stack([y, y], 1)
    i = int(max(0, t) * SR)
    if i >= len(buf): return
    y = y[:len(buf) - i] * g
    # constant-power pan (-1..1)
    a = (pan + 1) * np.pi / 4; buf[i:i + len(y)] += y * np.array([np.cos(a), np.sin(a)]) * 1.414
    return i

def build(after):
    B = {k: np.zeros((N, 2)) for k in ("kick", "perc", "bass", "mid", "lead")}
    kicks = []
    prev = None
    for bar in range(3):
        b0 = bar * BAR; ch = PROG[bar % 2]
        for k in range(16):
            t = b0 + k * S16 + (0.02 * BEAT if k % 2 else 0)
            on = k % 4 == 0
            if t >= 5.0: break
            # kick 0,6,10 (as music.py)
            if k in (0, 6, 10):
                tt, v = human(t, 120, True) if after else (t, 120)
                put(B["kick"], norm(drum(36, int(min(127, v)))), tt, 0.85); kicks.append(tt)
            if k in (4, 12): put(B["perc"], norm(drum(39, 105)), t, 0.35)
            # conga: before = hand-written slots; after = euclid(5,16,rot 2) hi + euclid(3,16, rot 3) low
            if after:
                if euclid(5, 16, 2)[k]: tt, v = human(t, 95, on); put(B["perc"], norm(drum(63, int(v))), tt, 0.32, 0.4)
                if euclid(3, 16, 3)[k]: tt, v = human(t, 100, on); put(B["perc"], norm(drum(64, int(v))), tt, 0.38, -0.3)
            else:
                if k in (2, 7, 9, 14): put(B["perc"], norm(drum(63, 95)), t, 0.32, 0.3)
                if k in (3, 11): put(B["perc"], norm(drum(64, 100)), t, 0.38, -0.2)
            sh_v = 60 + 25 * (k % 4 == 2)
            tt, v = human(t, sh_v, on) if after else (t, sh_v)
            put(B["perc"], norm(drum(70, int(v))), tt, 0.13, -0.5 if after else -0.4)
            # bass
            for s, iv in [(0, 0), (3, 0), (6, 7), (8, 0), (11, 0), (14, 10)]:
                if s == k:
                    m = ROOT[ch] + (12 if iv == 7 else iv if iv < 7 else -2)
                    put(B["bass"], norm(gm("Finger Bass", m, S16 * 2.2, 110, release=0.12)), t, 0.55)
            # sitar riff
            for s, dg, ln in RIFF:
                if s == k:
                    tt, v = human(t, 104, on) if after else (t, 104)
                    put(B["lead"], norm(gm("Sitar", deg(dg, -12), S16 * ln * 1.3, int(min(127, v)), release=0.25)), tt, 0.55, 0.15)
        # mid: dulcimer chord stabs on beats 1 and 3, voice-led in AFTER, fixed root position in BEFORE
        v = voice_lead(prev, CHORD_PC[ch]) if after else ([62, 66, 69] if ch == "D" else [63, 67, 70])   # BEFORE: parallel root position
        if after: prev = v
        for beat in (0, 2):
            for j, m in enumerate(v):
                t = b0 + beat * BEAT + (0.012 * j if after else 0)     # 12 ms strum spread
                put(B["mid"], norm(gm("Dulcimer", m, BEAT * 1.5, 90, release=0.3)), t, 0.22, (-0.35 + 0.35 * j) if after else 0)
    return B, kicks

def noise_verb(x, sec=1.8, dec=3.0):   # current music.py reverb, for BEFORE
    n = int(sec * SR); t = np.arange(n) / SR
    ir = np.random.default_rng(11).standard_normal(n) * np.exp(-t * dec); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[:len(x)]

def before():
    B, _ = build(False)
    mix = sum(B.values()); wet = B["lead"] * 0.25 + B["mid"] * 0.3 + B["perc"] * 0.1
    mix += np.stack([noise_verb(wet[:, 0]), noise_verb(wet[:, 1])], 1) * 0.5
    mix /= np.abs(mix).max(); mix = np.tanh(mix * 1.8); return mix / np.abs(mix).max() * 0.85

def duck_env(kicks, depth_db=-6.0, att=0.005, hold=0.03, rel=0.14):
    """sidechain gain curve keyed from kick onsets: -6 dB, 5 ms attack, 30 ms hold, 140 ms release (≈1/4 beat at 108 BPM)."""
    g = np.ones(N); lo = 10 ** (depth_db / 20)
    a, h, r = int(att * SR), int(hold * SR), int(rel * SR)
    shape = np.concatenate([np.linspace(1, lo, a), np.full(h, lo), lo + (1 - lo) * (1 - np.exp(-np.arange(r) / (r / 4)))])
    for t in kicks:
        i = int(t * SR); seg = shape[:max(0, N - i)]; g[i:i + len(seg)] = np.minimum(g[i:i + len(seg)], seg)
    return g[:, None]

def P(board, x): return board(x.T.astype(np.float32), SR).T.astype(np.float64)

def after():
    B, kicks = build(True)
    d = duck_env(kicks)
    kick = P(Pedalboard([HighpassFilter(30), PeakFilter(60, 2.0, 1.0)]), B["kick"])
    bass = P(Pedalboard([HighpassFilter(35), LowpassFilter(5000), Compressor(-20, 4, 5, 80)]), B["bass"]) * d
    perc = P(Pedalboard([HighpassFilter(150), PeakFilter(400, -2.0, 1.0)]), B["perc"])
    mid = P(Pedalboard([HighpassFilter(200), PeakFilter(3000, -1.5, 1.0)]), B["mid"]) * np.sqrt(d)
    lead = P(Pedalboard([HighpassFilter(180), PeakFilter(2500, 2.0, 0.8), Compressor(-18, 3, 10, 120)]), B["lead"])
    # one shared reverb send: HPF 300 / LPF 8k before the verb so lows don't smear
    send = lead * 0.25 + mid * 0.35 + perc * 0.08
    verb = P(Pedalboard([HighpassFilter(300), LowpassFilter(8000), Reverb(room_size=0.55, damping=0.5, wet_level=1.0, dry_level=0.0, width=1.0)]), send)
    verb *= d                                            # duck the tail too: keeps the groove pumping
    mix = kick * 1.0 + bass * 0.9 + perc * 0.8 + mid * 0.8 + lead * 0.9 + verb * 0.35
    mix /= np.abs(mix).max() * 2.0                       # ~-6 dBFS headroom into the master
    master = Pedalboard([LowShelfFilter(80, 1.0, 0.7), HighpassFilter(25),
                         Compressor(threshold_db=-14, ratio=2.0, attack_ms=10, release_ms=150),  # glue: 1-3 dB GR
                         Gain(6.0), Limiter(threshold_db=-1.5, release_ms=80), Gain(-1.5)])   # JUCE Limiter makes up to 0 dBFS, so trim after for -1.5 dBTP-ish ceiling
    return P(master, mix)

A = before(); Bm = after()
fade = int(0.04 * SR); A[-fade:] *= np.linspace(1, 0, fade)[:, None]
out = np.concatenate([A[:int(4.9 * SR)], np.zeros((int(0.1 * SR), 2)), Bm])
with wave.open("/workspace/work/distill_music/demo.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes())
def stats(x, name):
    rms = 20 * np.log10(np.sqrt((x ** 2).mean())); pk = 20 * np.log10(np.abs(x).max())
    side = (x[:, 0] - x[:, 1]) / 2; mid_ = (x[:, 0] + x[:, 1]) / 2
    print(f"{name}: RMS {rms:.1f} dBFS  peak {pk:.1f}  crest {pk - rms:.1f} dB  side/mid {20*np.log10(np.sqrt((side**2).mean())/np.sqrt((mid_**2).mean())):.1f} dB")
stats(A, "BEFORE"); stats(Bm, "AFTER ")
print("euclid(5,16,2):", "".join("x" if e else "." for e in euclid(5, 16, 2)), " euclid(3,8):", "".join("x" if e else "." for e in euclid(3, 8)))
print(f"render {time.time() - t_start:.1f}s")
