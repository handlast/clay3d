# 《斩首：最后一道防线》 score + sound design. 96 BPM 4/4, 22 bars, A minor. Defenders' theme A4–C5–B4 (short, short, long).
# stems: music.wav, sfx.wav. Music hard-silent 37.5–38.5 (collapse sounds stay in sfx).
import sys, math, functools, wave, numpy as np
sys.path.insert(0, "/workspace/work/sf"); sys.path.insert(0, "/workspace/sfx")
from samp import piano as _piano, gm as _gm, SR
from sfx import sfx
from cues import *
N = int(SR * (DUR + 0.5))
MUS = np.zeros((N, 2)); MV = np.zeros((N, 2)); FX = np.zeros((N, 2)); FV = np.zeros((N, 2))
rng = np.random.default_rng(17)
@functools.lru_cache(maxsize=None)
def _pk(name): return np.abs(_gm(name, 57, 1.0, 100)).max() + 1e-6
@functools.lru_cache(maxsize=None)
def gm(name, m, dur, vel=90, attack=None, release=0.4): return _gm(name, m, dur, vel, attack=attack, release=release) / _pk(name) * 0.3
def _add(buf, vb, y, t0, g, wet, pan):
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = np.asarray(y, float)
    if y.ndim == 1: y = np.stack([y, y], 1)
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    buf[i:i + len(y)] += y; vb[i:i + len(y)] += y * wet
def add(y, t0, g=1.0, wet=0.3, pan=0.0): _add(MUS, MV, y, t0, g, wet, pan)
def fx(y, t0, g=1.0, wet=0.15, pan=0.0): _add(FX, FV, y, t0, g, wet, pan)
def bt(b): return b * BEAT
def bar(k): return k * BAR
tt = lambda d: np.arange(int(d * SR)) / SR

AM, DM, FM, EM = [45, 52, 57, 60], [38, 50, 53, 57], [41, 48, 53, 57], [40, 47, 52, 56]
PROG = [AM, DM, FM, EM]
def strings(t0, notes, d, vel=60, g=1.0, inst="Slow Strings", attack=0.6):
    for m in notes: add(gm(inst, m, d, vel, attack=attack, release=1.0), t0, g * 0.5, wet=0.45)
def trem(t0, notes, d, vel=60, g=1.0):
    for m in notes: add(gm("Tremolo Strings", m, d, vel, attack=0.3, release=0.4), t0, g * 0.4, wet=0.4)
def cello(t0, m, d, vel=85, g=1.0): add(gm("Cello", m, d, vel, attack=0.15, release=0.8), t0, g * 0.8, wet=0.4, pan=-0.15)
def stacc(t0, m, vel=95, g=1.0): add(gm("Fast Strings", m, 0.16, vel, release=0.1), t0, g * 0.55, wet=0.25)
def pizz(t0, m, vel=70, g=1.0): add(gm("Pizzicato Strings", m, 0.5, vel, release=0.3), t0, g * 0.6, wet=0.4, pan=0.2)
def taiko(t0, vel=100, g=1.0): add(gm("Taiko Drum", 36, 0.9, vel, release=0.5), t0, g * 0.9, wet=0.35)
def bdrum(t0, vel=100, g=1.0): add(gm("Taiko Drum", 31, 1.2, vel, release=0.7), t0, g * 0.9, wet=0.3)
def timp(t0, m=45, vel=100, g=1.0): add(gm("Timpani", m, 1.6, vel, release=1.0), t0, g * 0.9, wet=0.4)
def pno(t0, m, d=2.0, vel=55, g=1.0): add(_piano(m, d, vel), t0, g * 3.2, wet=0.55)
def drone(t0, t1, f=55.0, g=1.0):
    t = tt(t1 - t0); env = np.minimum(1, t / 2) * np.minimum(1, (t1 - t0 - t) / 1.0)
    y = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.003 * t) + 0.2 * np.sin(2 * np.pi * f * 3.01 * t)) * env
    add(y * 0.10, t0, g, wet=0.4)
def heart(t0, g=1.0):      # lub-dub sub
    for d, a in ((0.0, 1.0), (0.18, 0.6)):
        t = tt(0.45); y = np.sin(2 * np.pi * np.cumsum(42 + 30 * np.exp(-t * 25)) / SR) * np.exp(-t * 9); add(y * 0.42 * a, t0 + d, g, wet=0.2)
def pulse(t0, t1, g=1.0, step=1.0):
    k = 0
    while t0 + bt(k * step) < t1:
        t = tt(0.4); y = np.sin(2 * np.pi * np.cumsum(40 + 22 * np.exp(-t * 20)) / SR) * np.exp(-t * 8); add(y * 0.3, t0 + bt(k * step), g, wet=0.25); k += 1

# 0–10: approach. heartbeat bass, big drum, crawling (sfx)
drone(0.0, 20.0, 55.0, 0.9)
add(gm("Cello", 33, 10.0, 70, attack=0.05, release=2.0), 0.0, 0.5, wet=0.5)
timp(0.0, 33, 120, 1.0); bdrum(0.0, 120, 1.0)
for k in range(16): heart(0.6 + bt(k), 0.7 + 0.02 * k)
for k in range(4): bdrum(bar(k + 1) - bt(0.5) if k else bar(1), 85 + 5 * k, 0.6)
# 5–10 war drums
for k in range(16):
    tb = 5.0 + bt(k * 0.5)
    taiko(tb, 70 + 25 * (k % 4 == 0), 0.55 + 0.1 * (k % 2 == 0))
for k in range(8): taiko(5.0 + bt(k) + bt(0.25), 55, 0.35)
trem(5.0, [45, 52], 5.0, 55, 0.7)
pizz(bar(3) + bt(2), 69, 45); pizz(bar(3) + bt(3), 72, 45); pizz(bar(3) + bt(4), 71, 50)    # theme hinted, plucked and quiet
# 10–20: infiltration. drums back, short strings and low pulse
pulse(10.0, 20.0, 0.9, 1.0)
for k in range(32):
    tb = 10.0 + bt(k * 0.5); ch = PROG[int(tb // BAR) % 4]
    stacc(tb, ch[0] if k % 2 == 0 else ch[1], 60 + 10 * (k % 4 == 0), 0.55)
strings(10.0, [33, 45], 5.0, 50, 0.7); strings(15.0, [38, 50], 5.0, 52, 0.7)
add(gm("Cello", 57, 1.2, 60, attack=0.05), 12.8, 0.35, wet=0.6); add(gm("Cello", 60, 1.2, 60, attack=0.05), 13.43, 0.35, wet=0.6)   # theme half-shown
# 15–20 low drum returns, gaps shrinking
gaps = [1.25, 1.0, 0.85, 0.7, 0.6, 0.5, 0.45, 0.4, 0.35, 0.3, 0.3, 0.25, 0.25]; tb = 15.0
for i, gp in enumerate(gaps):
    if tb >= 20.9: break
    bdrum(tb, 75 + 3 * i, 0.55 + 0.03 * i); tb += gp
# 21.0 sharp hit, drums stop half a beat
timp(21.0, 45, 127, 1.1); taiko(21.0, 127, 1.0)
for m in (57, 64, 69): stacc(21.0, m, 120, 0.9)
# 21.3–30: drums and high strings surge
t0 = 21.0 + bt(0.5)
k = 0
while t0 + bt(k * 0.5) < 30.0:
    tb = t0 + bt(k * 0.5); taiko(tb, 75 + 30 * (k % 4 == 0), 0.6); k += 1
for k in range(14):
    tb = 21.3 + bt(k * 0.5) * 2; ch = PROG[int(tb // BAR) % 4]
    for m in ch[1:3]: stacc(tb, m + 12, 85, 0.45)
for i, m in enumerate([69, 71, 72, 74, 76]): trem(21.3 + i * 1.7, [m, m + 12], 1.9, 60 + 6 * i, 0.55)
strings(21.3, [33, 40, 45], 8.7, 60, 0.8)
# 30–37.5: no way out. high strings climb, low drum denser
for i, m in enumerate([76, 77, 79, 80, 81]): strings(30.0 + i * 1.5, [m, m - 12], 1.7, 70 + 5 * i, 0.55, inst="Fast Strings", attack=0.3)
strings(30.0, [33, 45], 7.5, 65, 0.8)
tb = 30.0; gp = 0.62
while tb < 37.4:
    bdrum(tb, int(min(120, 80 + (tb - 30) * 6)), 0.6 + (tb - 30) * 0.04); tb += gp; gp = max(0.16, gp * 0.9)
add(gm("Tremolo Strings", 88, 7.0, 70, attack=4.0), 30.5, 0.25, wet=0.5)
# 38.5–45: double bass / cello returns, theme slowly, no victory
drone(38.5, 55.0, 55.0, 0.6)
add(gm("Cello", 33, 6.5, 65, attack=1.2, release=2.0), 38.5, 0.6, wet=0.5)
cello(40.0, 57, bt(1) + 0.1, 70); cello(40.0 + bt(1), 60, bt(1) + 0.1, 72); cello(40.0 + bt(2), 59, bt(3), 74)
strings(40.0, [45, 52, 57], 5.0, 50, 0.6); strings(42.5, [38, 50, 53], 2.5, 48, 0.6)
pno(41.25, 69, 3.0, 40)
# 45–55: piano, faint strings, drips; final theme with the last note hanging on B
strings(45.0, [41, 48, 57], 5.0, 42, 0.5); strings(50.0, [40, 47, 56], 5.5, 42, 0.55)
pno(45.0, 57, 3.5, 34); pno(47.5, 53, 3.5, 32); pno(50.0, 52, 3.0, 32)
pno(51.25, 69, 1.0, 50); pno(51.25 + bt(1), 72, 1.0, 50); pno(51.25 + bt(2), 71, 4.5, 56); pno(51.25 + bt(2), 52, 4.5, 34)

# ================= sound design =================
def thud(t0, g=1.0):
    t = tt(0.9); f = 34 + 40 * np.exp(-t * 18); y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    n = np.convolve(rng.standard_normal(len(t)), np.ones(60) / 60, "same") * np.exp(-t * 20) * 0.6
    fx((y + n) * 0.5, t0, g, wet=0.5)
def click(t0, g=1.0):
    L = int(0.012 * SR); c = rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 6)); c = np.convolve(c, [1, -0.9], "same")
    fx(c * 0.12, t0, g, wet=0.2, pan=rng.uniform(-0.6, 0.6))
def crawl(t0, t1, dens=20, g=1.0):
    for k in range(int((t1 - t0) * dens)):
        tk = t0 + rng.uniform(0, t1 - t0); L = int(0.004 * SR); c = rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)); c = np.convolve(c, [1, -1], "same")
        fx(c * 0.05 * rng.uniform(0.3, 1), tk, g, wet=0.1, pan=rng.uniform(-0.8, 0.8))
def rustle(t0, t1, g=1.0):
    t = tt(t1 - t0); n = rng.standard_normal(len(t)); n = np.convolve(n, [1, -1.6, 0.7], "same")
    am = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 1.3 * t) * np.sin(2 * np.pi * 0.7 * t))
    env = np.minimum(1, t / 0.5) * np.minimum(1, (t1 - t0 - t) / 0.5); fx(n * am * env * 0.02, t0, g, wet=0.1)
def bed(idx, t0, t1, g=1.0, start=0.0, fade=1.0):
    d = t1 - t0; y = sfx(idx, start=start, dur=d, norm=True); n = len(y); tt_ = np.arange(n) / SR
    env = np.minimum(1, tt_ / fade) * np.minimum(1, (d - tt_) / fade); fx(y * env, t0, g, wet=0.05)
def bite(t0, g=1.0): click(t0, 1.2 * g); click(t0 + 0.03, 0.8 * g); fx(sfx(80, dur=0.25, norm=True) * 0.12, t0, g * 0.5, wet=0.2)
def chew(t0, t1, g=1.0):
    for k in range(int((t1 - t0) * 7)):
        tk = t0 + k / 7 + rng.uniform(0, 0.05); click(tk, 0.6 * g)
def trickle(t0, t1, n, g=1.0):
    for k in range(n):
        L = int(0.06 * SR); fx(np.convolve(rng.standard_normal(L), np.ones(25) / 25, "same") * 0.2 * np.exp(-np.arange(L) / 700), t0 + rng.uniform(0, t1 - t0), g, wet=0.3)
def creak(t0, g=1.0, d=0.5): fx(sfx(85, start=rng.uniform(0, 1.2), dur=d, norm=True) * 0.15, t0, g, wet=0.3)

thud(0.0, 1.3); bed(273, 0.0, 5.0, 0.07, start=5.0)
crawl(0, 5, 12, 0.8); rustle(0, 5, 0.6)
for k in range(5): click(0.8 + k * 0.9, 0.5)                                 # mandibles in the crack
# 5–10 outside: dense crawling and fighting
crawl(5, 10, 70, 1.0); rustle(5, 10, 1.0)
for k in range(50): click(5 + rng.uniform(0, 5), rng.uniform(0.3, 0.9))
# 10–15 inside
bed(273, 10.0, 37.4, 0.06, start=12.0)
crawl(10, 15, 22, 0.8); trickle(10, 15, 12, 0.7)
bite(11.0, 1.0); bite(11.6, 0.8); bite(12.2, 0.8); chew(11.0, 12.6, 0.8); creak(12.8, 0.8, 0.6)
# 15–20
crawl(15, 20, 30, 0.9); bite(17.7, 0.9); bite(18.4, 0.8); bite(19.5, 0.9); bite(20.1, 0.8)
# 20–30
bite(21.0, 1.4); chew(21.1, 26.0, 0.9); crawl(20, 30, 35, 1.0)
bite(25.7, 1.2); bite(26.3, 0.9); bite(27.5, 0.9); chew(25.7, 28.6, 1.0)
rustle(28.5, 30.0, 1.4); trickle(28.5, 30, 8, 0.9)                           # guard dragged down
# 30–37.5 closing in
crawl(30, 37.5, 45, 1.1); chew(31.2, 35.2, 1.0)
for k, tk in enumerate((31.2, 32.6, 33.6, 34.4, 35.1, 35.7, 36.3, 36.8, 37.15)): creak(tk, 0.6 + 0.08 * k, 0.35)
trickle(33, 37.5, 14, 0.8); chew(36.0, 37.45, 1.2)
# 37.5 snap and collapse (kept through the music silence)
fx(sfx(83, dur=2.0, norm=True) * 0.9, TSNAP, 1.0, wet=0.35)
thud(TSNAP + 0.12, 1.4); thud(TSNAP + 0.38, 1.0)
fx(sfx(105, dur=3.0, norm=True) * 0.55, TSNAP + 0.05, 1.0, wet=0.3)
trickle(TSNAP, TSNAP + 3.5, 60, 1.0); trickle(TSNAP + 3.5, 44.0, 10, 0.5)
# 40–45 outside the exit: the front still audible in the distance
crawl(40, 45, 18, 0.5); rustle(40, 45, 0.4)
for k in range(20): click(40 + rng.uniform(0, 5), rng.uniform(0.15, 0.35))
# 45–50 underground: drips only, fading
for k in range(7): fx(sfx(70, start=0.0, dur=0.3, norm=True) * 0.05, 45.4 + k * 0.72 + rng.uniform(0, 0.25), 1.0 - 0.08 * k, wet=0.6)
bed(273, 45.0, 50.0, 0.04, start=40.0)
click(46.6, 0.25)                                                             # the antenna's last twitch
# 50–55 distant battle
crawl(50, 54.5, 14, 0.4)
for k in range(12): click(50 + rng.uniform(0, 4), rng.uniform(0.1, 0.3))

# ================= mix =================
def reverb(x, sec=2.4, dec=2.6):
    n = int(sec * SR); t = np.arange(n) / SR; ir = rng.standard_normal(n) * np.exp(-t * dec); ir = np.convolve(ir, np.ones(10) / 10, "same"); ir /= np.abs(ir).sum() ** 0.5 * 9
    sz = 1 << int(np.ceil(np.log2(len(x) + n))); return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
MUS += np.stack([reverb(MV[:, 0]), reverb(MV[:, 1])], 1) * 0.55
FX += np.stack([reverb(FV[:, 0], 1.5, 4), reverb(FV[:, 1], 1.5, 4)], 1) * 0.4
# hard music silence 37.5–38.5 (sfx untouched)
i0, i1 = int(TSNAP * SR), int((TSNAP + 1.0) * SR); fn = int(0.03 * SR)
MUS[i0 - fn:i0] *= np.linspace(1, 0, fn)[:, None]; MUS[i0:i1] = 0
MUS[i1:i1 + int(0.4 * SR)] *= np.linspace(0, 1, int(0.4 * SR))[:, None]
L = int(DUR * SR)
MUS = MUS[:L]; FX = FX[:L]
fo = int(0.25 * SR); MUS[-fo:] *= np.linspace(1, 0, fo)[:, None]; FX[-int(2.0 * SR):] *= np.linspace(1, 0, int(2.0 * SR))[:, None]
MUS = np.tanh(MUS / np.abs(MUS).max() * 1.5); MUS /= np.abs(MUS).max() / 0.9
FX = np.tanh(FX / np.abs(FX).max() * 1.2); FX /= np.abs(FX).max() / 0.9
def wr(path, X):
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(X, -1, 1) * 32767).astype("<i2").tobytes())
wr("/workspace/work/zhanshou/music.wav", MUS); wr("/workspace/work/zhanshou/sfx.wav", FX)
r = lambda X: " ".join(f"{i*5}:{20*np.log10(np.sqrt((X[int(i*5*SR):int((i+1)*5*SR)]**2).mean())+1e-9):.0f}" for i in range(11))
print("MUS", r(MUS)); print("FX ", r(FX))
print("silence check", np.abs(MUS[int(37.55*SR):int(38.45*SR)]).max())
