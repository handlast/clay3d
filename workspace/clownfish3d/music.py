# 《动物打工人 No.03》BGM — "海底打工人 Bubble Office Bossa-Funk": F 大调 I-vi-ii-V（Fmaj7 Dm7 Gm7 C7），120 BPM 4/4，16 分 16% swing
# 音色：Vibraphone 主旋律（水下闪光感）+ Kalimba 叠、Fretless Bass、Tine EP 反拍和弦、bongo/shaker/刷子感小鼓、气泡 bloop
# 只有两个大重音：BIG1 = 3.0 s（白化揭晓）、BIG2（加班守家）；其余动作配轻音效。全部时间读 cues.py（自适应）。
# 0–3 s 钩子：打卡滴答 + 下行拨弦（触手一根根变白）+ riser；BIG2 处重设小节原点 org()。
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import gm as _gm, drum as _drum, SR
from cues import *
@functools.lru_cache(maxsize=None)
def _peak(name): return np.abs(_gm(name, 64, 0.5, 100, release=0.2)).max() + 1e-6
@functools.lru_cache(maxsize=None)
def gm(name, m, dur=0.5, vel=100, release=0.2): return _gm(name, m, dur, vel, release=release) * (0.5 / _peak(name))
@functools.lru_cache(maxsize=None)
def _dpk(n): return np.abs(_drum(n, 100)).max() + 1e-6
@functools.lru_cache(maxsize=None)
def drum(n, vel=100): return _drum(n, vel) * (0.6 / _dpk(n))
N = int(SR * DUR); MIX = np.zeros((N, 2)); VERB = np.zeros((N, 2)); ECHO = np.zeros((N, 2))
rng = np.random.default_rng(23)
def add(y, t0, g=1.0, pan=0.0, wet=0.0, echo=0.0, human=True):
    if human: g *= 1 + rng.uniform(-0.06, 0.06); t0 += rng.uniform(-0.003, 0.003)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    MIX[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet
    if echo: ECHO[i:i + len(y)] += y * echo
def mono(y): return np.stack([y, y], 1)
tt_ = lambda d: np.arange(int(d * SR)) / SR
S16 = BEAT / 4; SW = 0.16 * S16
ORG = [G0]
def org(t): ORG.append(t)
def origin(t): return max(o for o in ORG if o <= t + 1e-6) if t >= ORG[0] else ORG[0]
def sixteenths(t0, t1):
    out = []
    o = origin(t0); b0 = int(math.floor((t0 - o) / BAR)) - 1
    for b in range(max(-2, b0), b0 + 200):
        s0 = o + b * BAR
        if s0 > t1 + 0.1: break
        for k in range(16):
            tt = s0 + k * S16
            if t0 - 1e-4 <= tt < t1 - 1e-4 and origin(tt) == o: out.append((tt + (SW if k % 2 else 0), k, b))
    return out
# ---------------- SFX ----------------
def boom(t0, g=1.0, dur=1.1):
    t = tt_(dur); f = 38 + 80 * np.exp(-t * 16)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2) * 0.9), t0, g, human=False)
def tick(t0, g=1.0, f=3200):
    t = tt_(0.04); y = np.sin(2 * np.pi * f * t) * np.exp(-t * 160) + rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.4
    add(mono(y * 0.35), t0, g, pan=0.2, human=False)
def whoosh(t0, d=0.35, g=1.0, f0=400):
    n = int(d * SR); t = np.arange(n) / SR; nz = rng.standard_normal(n); k = max(2, int(SR / f0 / 2))
    y = nz - np.convolve(nz, np.ones(k) / k, "same"); y = np.convolve(y, np.ones(3) / 3, "same")
    add(mono(y * np.sin(np.pi * t / d) ** 2 * 0.12), t0, g, human=False)
def popfx(t0, g=1.0, f0=1200, f1=300):
    t = tt_(0.09); f = f1 + (f0 - f1) * np.exp(-t * 60)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.32), t0, g, human=False)
def ding(t0, g=1.0, f=2637):
    t = tt_(1.2); y = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t * 3) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6))
    add(mono(y * np.exp(-t * 3.5) * np.minimum(1, t / 0.002) * 0.16), t0, g, wet=0.6, echo=0.4, human=False)
def boing(t0, g=1.0, d=0.6, f0=180, depth=0.5, hz=11):
    t = tt_(d); f = f0 * (1 + depth * np.sin(2 * np.pi * hz * t) * np.exp(-t * 3)) * (1 + 0.6 * t)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    add(mono(y * np.exp(-t * 4) * np.minimum(1, t / 0.005) * 0.22), t0, g, wet=0.15, human=False)
def slide(t0, f0, f1, d=0.4, g=1.0):
    t = tt_(d); f = f0 * (f1 / f0) ** (t / d) * (1 + 0.01 * np.sin(2 * np.pi * 6 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.2 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    add(mono(y * np.sin(np.pi * t / d) ** 0.5 * 0.12), t0, g, wet=0.3, human=False)
def chirp(t0, g=1.0):
    for j in range(3):
        t = tt_(0.08); f = 3000 + 1500 * np.sin(np.pi * t / 0.08) + j * 200
        add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.08) * 0.12), t0 + j * 0.1, g, pan=-0.3, wet=0.2, human=False)
def buzz(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    ph = np.cumsum(220 * (1 + 0.04 * np.sin(2 * np.pi * 9 * t))) / SR
    y = (2 * (ph % 1) - 1) * (0.6 + 0.4 * np.sin(2 * np.pi * 31 * t)) * np.minimum(1, t / 0.05) * np.minimum(1, (t[-1] - t) / 0.05)
    add(mono(y * 0.03), t0, g, pan=0.4, human=False)
def snap(t0, g=1.0):
    add(drum(39, 110), t0, 0.6 * g); popfx(t0, 0.8 * g, 2000, 400)
def bloop(t0, g=1.0, f0=300, f1=900, d=0.18):
    t = tt_(d); f = f0 * (f1 / f0) ** (t / d)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) * 0.3), t0, g, wet=0.3, human=False)
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T_ = t1 - t0
    y = np.convolve(rng.standard_normal(n), np.ones(5) / 5, "same") * (t / T_) ** 2.5 * 0.07
    f = 180 * (1600 / 180) ** (t / T_); y += np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / T_) ** 2 * 0.04
    add(mono(y), t0, g, human=False)
def rattle(t0, d, g=1.0):
    for j in range(int(d * 22)):
        tt = t0 + rng.uniform(0, d); L = tt_(0.03)
        y = np.sin(2 * np.pi * rng.uniform(1500, 3200) * L) * np.exp(-L * 180) * 0.25 + rng.standard_normal(len(L)) * np.exp(-L * 300) * 0.2
        add(mono(y), tt, g * rng.uniform(0.4, 1), pan=rng.uniform(-0.3, 0.3), human=False)
def clock(t0, t1, g=1.0):
    for j, tt in enumerate(np.arange(t0, t1 - 1e-6, BEAT)):
        add(drum(76 if j % 2 == 0 else 77, 100), tt, 0.35 * g, pan=0.25 if j % 2 else -0.25)

# ---------------- music parts: F major I-vi-ii-V ----------------
PROG = ["Fmaj7", "Dm7", "Gm7", "C7"]
CH = {"Fmaj7": (65, 69, 72, 76), "Dm7": (62, 65, 69, 72), "Gm7": (62, 65, 67, 70), "C7": (64, 67, 70, 72), "Bb": (62, 65, 70, 74)}
ROOT = {"Fmaj7": 41, "Dm7": 38, "Gm7": 43, "C7": 36, "Bb": 46}
def chord_of(b): return PROG[b % 4]
BASSL = [(0, 0, 3), (3, 7, 1), (6, 12, 1), (8, 7, 2), (10, 0, 1), (11, 10, 1), (14, 7, 2)]     # 巴萨诺瓦式根-五
def bass(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        for pos, iv, du in BASSL:
            if pos == k: add(gm("Fretless Bass", ROOT[chord_of(b)] + iv, du * S16 * 0.95, 110 if k == 0 else 90, 0.08), tt, 0.6 * g)
COMP = [2, 6, 10, 13]
def comp(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k in COMP:
            for j, m in enumerate(CH[chord_of(b)]): add(gm("Tine Electric Piano", m - 12 if m > 74 else m, S16 * 1.6, 82 if k % 4 == 2 else 66, 0.1), tt + j * 0.004, 0.1 * g, pan=-0.25, wet=0.2)
def bongo(t0, t1, g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if k in (0, 3, 6, 8, 11, 14): add(drum(60 if k in (0, 8) else 61, 100 if k in (0, 8) else 78), tt, 0.3 * g, pan=0.35)
        if k % 2 == 1: add(drum(70, 60), tt, 0.16 * g, pan=-0.35)     # maracas/shaker
MEL = [[(0, 81, 2), (2, 79, 1), (3, 77, 1), (4, 76, 2), (6, 77, 2), (8, 81, 4), (12, 84, 4)],
       [(0, 81, 3), (3, 77, 1), (4, 74, 2), (6, 77, 2), (8, 76, 6), (14, 74, 2)],
       [(0, 79, 2), (2, 82, 2), (4, 79, 2), (6, 77, 2), (8, 74, 4), (12, 77, 4)],
       [(0, 76, 2), (2, 79, 2), (4, 82, 2), (6, 84, 2), (8, 82, 3), (11, 79, 1), (12, 76, 4)]]
def melody(t0, t1, g=1.0, up=0, inst="Vibraphone"):
    for tt, k, b in sixteenths(t0, t1):
        for pos, m, du in MEL[b % 4]:
            if pos == k:
                add(gm(inst, m + up, du * S16 * 1.2, 108 if k % 4 == 0 else 92, 0.3), tt, 0.34 * g, pan=0.2, wet=0.3, echo=0.15)
                add(gm("Kalimba", m + up, du * S16, 90, 0.2), tt, 0.13 * g, pan=-0.2, wet=0.2)
def kit(t0, t1, style="full", g=1.0):
    for tt, k, b in sixteenths(t0, t1):
        if style == "full":
            if k in (0, 6, 10): add(drum(36, 96), tt, 0.48 * g)
            if k in (4, 12): add(drum(38, 80), tt, 0.24 * g, wet=0.15)
        if k % 2 == 0: add(drum(42, 58 if k % 4 == 0 else 40), tt, 0.17 * g, pan=-0.3)
        if style == "lite" and k in (4, 12): add(drum(37, 85), tt, 0.24 * g)
def groove(t0, t1, g=1.0, mel=True, up=0, style="full", inst="Vibraphone"):
    bass(t0, t1, g); comp(t0, t1, g); bongo(t0, t1, g); kit(t0, t1, style, g)
    if mel: melody(t0, t1, g, up, inst)
def kal(t0, m, g=1.0): add(gm("Kalimba", m, 0.4, 105, 0.3), t0, 0.4 * g, wet=0.3)
def vib(t0, m, g=1.0): add(gm("Vibraphone", m, 0.8, 100, 0.5), t0, 0.32 * g, wet=0.4, echo=0.3)
def glock(t0, m, g=1.0): add(gm("Glockenspiel", m, 0.4, 95, 0.3), t0, 0.28 * g, wet=0.35, echo=0.3)
def wood(t0, g=1.0, hi=True): add(drum(76 if hi else 77, 100), t0, 0.35 * g, pan=0.25 if hi else -0.25)
def pizz(t0, m, g=1.0): add(gm("Pizzicato Strings", m, 0.3, 100, 0.2), t0, 0.35 * g, wet=0.2)
def epch(t0, ch, d=1.8, g=1.0):
    for j, m in enumerate(CH[ch]): add(gm("Tine Electric Piano", m, d, 72, 0.4), t0 + j * 0.01, 0.16 * g, wet=0.3)
def bub(t0, g=1.0, f0=None):
    f0 = f0 or rng.uniform(380, 700); bloop(t0, 0.5 * g, f0, f0 * 2.4, 0.12)
def sonar(t0, g=1.0):
    t = tt_(1.4); y = np.sin(2 * np.pi * 1180 * t) * np.exp(-t * 3.0) * np.minimum(1, t / 0.004)
    add(mono(y * 0.12), t0, g, wet=0.6, echo=0.5, human=False)
def shutter(t0, g=1.0):
    add(drum(75, 110), t0, 0.3 * g); tick(t0 + 0.06, 0.6 * g, 2400)
def big(t0, g=1.0):
    boom(t0, 1.0 * g, 1.2); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 118), t0, 0.5 * g, wet=0.35)
    for m in (53, 60, 65, 69, 72): add(gm("Brass Section", m, 0.45, 122, 0.15), t0, 0.28 * g, wet=0.3)
    for j, m in enumerate((72, 77, 81, 84, 89)): add(gm("Steel Drums", m, 0.4, 118, 0.2), t0 + 0.02 + j * 0.035, 0.3 * g, wet=0.3)
    add(gm("Timpani", 41, 1.0, 120, 0.4), t0, 0.5 * g, wet=0.2)
    add(gm("Fretless Bass", 29, 0.8, 127, 0.15), t0, 0.9 * g)

# ---------------- arrangement ----------------
# 0–3 s hook: 打卡滴答 + 触手一根根变白（下行 pizz）+ 低音心跳 + riser（0 s 有明显起音：pop + 下滑）
popfx(0.02, 0.8, 1500, 400); pizz(0.02, 77, 0.9); slide(0.05, 900, 500, 0.5, 0.6)
for j, tt in enumerate(np.arange(0.0, BIG1 - 0.01, BEAT)): wood(tt, 0.7, j % 2 == 0)
for j, m in enumerate([84, 81, 77, 76, 72, 69, 65, 64, 60, 57]): pizz(0.3 + j * 0.24, m, 0.75)
for b in range(6): add(drum(36, 70), b * BEAT, 0.26)
for j in range(4): bub(0.4 + j * 0.55, 0.6)
add(gm("Reverse Cymbal", 60, 1.6, 110), BIG1 - 1.6, 0.25); riser(1.4, BIG1 - 0.05, 0.8)
# BIG1: 白化揭晓
big(BIG1, 0.85); sonar(BIG1 + 0.15, 0.7)
bass(BIG1, T["where"], 0.8); comp(BIG1, T["where"], 0.8); kit(BIG1, T["where"], "lite", 0.6)
for j, m in enumerate([77, 76, 72, 69]): vib(BIG1 + 0.4 + j * 0.5, m, 0.6)           # 体温计上涨：下行叹息 + 上滑
slide(BIG1 + 0.4, 300, 900, 1.8, 0.45)
# where: 热浪（月份翻页一次一个 glock，温度条 riser），lite groove + 旋律
groove(T["where"], T["cam"], 0.85, style="lite")
for j in range(5): glock(T["where"] + 0.9 + j * 0.75, [77, 79, 81, 84, 86][j], 0.5)
riser(T["where"] + 0.8, T["where"] + 4.2, 0.35)
# cam: 快门 + 计数小音
bass(T["cam"], T["q"], 0.8); bongo(T["cam"], T["q"], 0.8); comp(T["cam"], T["q"], 0.7)
shutter(T["cam"] + 0.05, 0.9); shutter(T["cam"] + 1.4, 0.6)
for i in range(3): popfx(T["cam"] + 0.2 + i * 0.25, 0.55, 1100 + 150 * i)
for j in range(23): tick(T["cam"] + 0.3 + j * 0.09, 0.35, 3000 + 40 * j)
ding(T["cam"] + 2.4, 0.45, 2794)
# q: breakdown – kalimba 问句、心跳、riser，SIL0 前收
for b in range(int((SIL0 - T["q"]) / BEAT)): add(drum(36, 70), T["q"] + b * BEAT, 0.28)
for j, m in enumerate([72, 76, 79, 81]): kal(T["q"] + 0.5 + j * 0.25, m, 0.6)
boing(T["q"] + 0.55, 0.4, 0.4, 350, 0.3, 5); boing(T["q"] + 0.85, 0.35, 0.4, 420, 0.3, 5)
riser(T["q"] + 0.8, SIL0, 1.0); add(gm("Reverse Cymbal", 60, 1.4, 110), SIL0 - 1.4, 0.25)
# BIG2: 加班守家 —— 小节原点重设
org(BIG2)
big(BIG2, 0.9); ding(BIG2 + 0.35, 0.6, 3136)
groove(BIG2, T["guard"], 1.0, up=0)
for i in range(4): glock(BIG2 + 0.3 + i * 0.18, [84, 88, 91, 96][i], 0.5)
for j in range(8): whoosh(T["care"] + 0.3 + j * 0.55, 0.25, 0.35, 900); bub(T["care"] + 0.5 + j * 0.55, 0.5)
# guard: 追逐 – tom 滚奏 + bass，入侵者被赶走时一个 boing
bass(T["guard"], T["fight"], 0.8); bongo(T["guard"], T["fight"], 1.0); kit(T["guard"], T["fight"], "full", 0.7)
for j in range(10): add(gm("Melodic Tom", [50, 53, 55][j % 3], 0.2, 100), T["guard"] + 1.0 + j * 0.12, 0.13, pan=-0.3 + 0.6 * (j % 2))
whoosh(T["guard"] + 1.0, 0.5, 0.8, 500); boing(T["guard"] + 1.8, 0.6, 0.6, 260, 0.6, 7); ding(T["guard"] + 2.0, 0.5, 2794)
# fight: 吵架 – 每次顶撞一个 tom，数字滚动 ticks
bass(T["fight"], T["calm"], 0.8); comp(T["fight"], T["calm"], 0.8); kit(T["fight"], T["calm"], "lite", 0.7)
for j in range(int((T["calm"] - T["fight"]) / (math.pi / 5)) - 1):
    tt = T["fight"] + (j + 0.5) * math.pi / 5; add(gm("Melodic Tom", [48, 52][j % 2], 0.2, 100), tt, 0.12, pan=-0.3 + 0.6 * (j % 2))
for j in range(16): tick(T["fight"] + 1.0 + 1.6 * (j / 16) ** 0.8, 0.4, 3200)
ding(T["fight"] + 2.6, 0.55, 3520); boing(T["fight"] + 2.7, 0.5, 0.5, 200, 0.6, 6)
# calm: 左右对比 – 柔和 EP + 轻 bongo
for j, ch in enumerate(["Fmaj7", "Dm7", "Gm7", "C7", "Fmaj7"]):
    if T["calm"] + j * 1.0 < T["know"] - 0.2: epch(T["calm"] + j * 1.0, ch, 1.0, 1.8)
bongo(T["calm"], T["know"], 0.6); popfx(T["calm"] + 0.2, 0.5); popfx(T["calm"] + 0.6, 0.5, 900)
# know: 知识卡 – 安静 vibraphone 琶音 + 藻类一颗颗飘走（每颗一个 bloop）
for j in range(int((T["card"] - T["know"]) / BEAT)): vib(T["know"] + j * BEAT, CH[PROG[(j // 4) % 4]][j % 4] + 12, 0.35)
for i in range(14): bub(T["know"] + 0.8 + i * 0.16, 0.45, 500 + 25 * i)
bass(T["know"], T["card"], 0.5)
# card: 未知 – 问句 kalimba + 进度条滴答
for j, m in enumerate([72, 74, 76, 79, 76, 74]): kal(T["card"] + 0.4 + j * 0.4, m, 0.45)
for j, tt in enumerate(np.arange(T["card"] + 2.5, T["end"] - 0.1, BEAT)): wood(tt, 0.6, j % 2 == 0)
bass(T["card"], T["end"], 0.55); comp(T["card"], T["end"], 0.6)
# end: groove 回归（lite）+ 收尾和弦
FINAL = DUR - 1.4
groove(T["end"], FINAL, 0.75, style="lite")
popfx(T["end"] + 1.2, 0.6); boing(T["end"] + 2.6, 0.5, 0.5, 240, 0.5, 7)
for j, m in enumerate((41, 53, 60, 65, 69, 72, 77)): add(gm("Vibraphone" if m > 45 else "Fretless Bass", m, 1.4, 105, 0.6), FINAL + j * 0.02, 0.4, wet=0.35)
add(drum(36, 100), FINAL, 0.5); add(drum(49, 70), FINAL, 0.2, wet=0.4)
# ---------------- mix ----------------
def reverb(x, sec=1.6, dec=3.2):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * dec); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
d_ = int(3 * S16 * SR)
for r in range(1, 3):
    sh = ECHO[: N - d_ * r] * (0.4 ** r)
    MIX[d_ * r:, 0] += sh[:, 1] * (0.8 if r % 2 else 0.3); MIX[d_ * r:, 1] += sh[:, 0] * (0.3 if r % 2 else 0.8)
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
i0, i1 = int(SIL0 * SR), int(BIG2 * SR); fade = np.linspace(1, 0, int(0.04 * SR))
MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] *= 0.1
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.0); MIX /= np.abs(MIX).max() / 0.85
fo = int(0.8 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("/workspace/work/clownfish3d/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG1 %.2f BIG2 %.2f" % (BPM, DUR, BIG1, BIG2))
