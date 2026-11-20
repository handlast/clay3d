# 《动物打工人 No.04》BGM — "夜班育婴室 Lo-fi Jazz + 嗡嗡低音"：Bb 大调 IV-iii-ii-V（Ebmaj7 Dm7 Cm7 F7），96 BPM 4/4，8 分 swing
# 音色：Tine EP（Rhodes）慢摇 comp + Acoustic Bass + Brush Kit 刷子鼓 + Muted Trumpet / Vibraphone 旋律 + 黑胶噪声
#       “嗡嗡低音”= 自合成锯齿波（根音，带 ~26 Hz 翅膀颤动 + 低通），全片贯穿，muscle 段加强（飞行肌抖动发热）
# 大重音只有两个：0 s（干饭王）与 BIG2（热成像揭晓）；其余动作配轻音效。全部时间读 cues.py（自适应）。BIG2 处重设小节原点。
import sys, math, wave, functools, numpy as np
sys.path.insert(0, "/workspace/work/sf")
from samp import gm as _gm, drum as _drum, SR
from cues import *
import film_times as FT
@functools.lru_cache(maxsize=None)
def _peak(name): return np.abs(_gm(name, 64, 0.5, 100, release=0.2)).max() + 1e-6
@functools.lru_cache(maxsize=None)
def gm(name, m, dur=0.5, vel=100, release=0.2): return _gm(name, m, dur, vel, release=release) * (0.5 / _peak(name))
@functools.lru_cache(maxsize=None)
def _dpk(n, kit): return np.abs(_drum(n, 100, kit=kit)).max() + 1e-6
@functools.lru_cache(maxsize=None)
def drum(n, vel=100, kit="Standard 1"): return _drum(n, vel, kit=kit) * (0.6 / _dpk(n, kit))
N = int(SR * DUR); MIX = np.zeros((N, 2)); VERB = np.zeros((N, 2)); ECHO = np.zeros((N, 2))
rng = np.random.default_rng(42)
def add(y, t0, g=1.0, pan=0.0, wet=0.0, echo=0.0, human=True):
    if human: g *= 1 + rng.uniform(-0.06, 0.06); t0 += rng.uniform(-0.004, 0.004)
    i = int(max(0, t0) * SR)
    if i >= N: return
    y = y[: N - i] * g
    if pan: y = y * np.array([1 - max(pan, 0), 1 + min(pan, 0)])
    MIX[i:i + len(y)] += y
    if wet: VERB[i:i + len(y)] += y * wet
    if echo: ECHO[i:i + len(y)] += y * echo
def mono(y): return np.stack([y, y], 1)
tt_ = lambda d: np.arange(int(d * SR)) / SR
E8 = BEAT / 2; SW = 0.18 * BEAT          # 8 分 swing（后半拍推迟）
ORG = [0.0]
def org(t): ORG.append(t)
def origin(t): return max(o for o in ORG if o <= t + 1e-6)
def eighths(t0, t1):
    out = []
    o = origin(t0); b0 = int(math.floor((t0 - o) / BAR)) - 1
    for b in range(max(-1, b0), b0 + 200):
        s0 = o + b * BAR
        if s0 > t1 + 0.1: break
        for k in range(8):
            tt = s0 + k * E8
            if t0 - 1e-4 <= tt < t1 - 1e-4 and origin(tt) == o: out.append((tt + (SW if k % 2 else 0), k, b))
    return out
# ---------------- SFX ----------------
def boom(t0, g=1.0, dur=1.1):
    t = tt_(dur); f = 38 + 80 * np.exp(-t * 16)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2) * 0.9), t0, g, human=False)
def tick(t0, g=1.0, f=3200):
    t = tt_(0.04); y = np.sin(2 * np.pi * f * t) * np.exp(-t * 160) + rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.4
    add(mono(y * 0.35), t0, g, pan=0.2, human=False)
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
def riser(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; T_ = t1 - t0
    y = np.convolve(rng.standard_normal(n), np.ones(5) / 5, "same") * (t / T_) ** 2.5 * 0.07
    f = 180 * (1600 / 180) ** (t / T_); y += np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / T_) ** 2 * 0.04
    add(mono(y), t0, g, human=False)
def whoosh(t0, d=0.35, g=1.0, f0=400):
    n = int(d * SR); t = np.arange(n) / SR; nz = rng.standard_normal(n); k = max(2, int(SR / f0 / 2))
    y = nz - np.convolve(nz, np.ones(k) / k, "same"); y = np.convolve(y, np.ones(3) / 3, "same")
    add(mono(y * np.sin(np.pi * t / d) ** 2 * 0.12), t0, g, human=False)
def chirp(t0, g=1.0):
    for j in range(3):
        t = tt_(0.08); f = 3000 + 1500 * np.sin(np.pi * t / 0.08) + j * 200
        add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.08) * 0.12), t0 + j * 0.1, g, pan=-0.3, wet=0.2, human=False)
def thunk(t0, g=1.0):
    t = tt_(0.25); f = 90 + 120 * np.exp(-t * 30)
    add(mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * 0.6 + rng.standard_normal(len(t)) * np.exp(-t * 60) * 0.1), t0, g, human=False)
def click(t0, g=1.0): add(drum(75, 110), t0, 0.35 * g); tick(t0 + 0.03, 0.7 * g, 4200)
def heartbeat(t0, g=1.0): add(drum(36, 80), t0, 0.35 * g); add(drum(36, 60), t0 + 0.18, 0.22 * g)
def buzzfx(t0, d, f=180, g=1.0, trem=26.0):
    """熊蜂嗡嗡（翅膀/飞行肌）：锯齿 + 颤动 + 低通"""
    n = int(d * SR); t = np.arange(n) / SR
    ph = np.cumsum(f * (1 + 0.03 * np.sin(2 * np.pi * 5 * t))) / SR
    y = (2 * (ph % 1) - 1) * (0.65 + 0.35 * np.sin(2 * np.pi * trem * t))
    y = np.convolve(y, np.ones(9) / 9, "same")
    y *= np.minimum(1, t / 0.08) * np.minimum(1, (t[-1] - t + 1e-9) / 0.12)
    add(mono(y * 0.14), t0, g, pan=0.15, human=False)
def vinyl(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); y = np.convolve(rng.standard_normal(n), np.ones(30) / 30, "same") * 0.012
    for _ in range(int((t1 - t0) * 6)):
        i = rng.integers(0, n - 200); y[i:i + 60] += rng.standard_normal(60) * np.exp(-np.arange(60) / 12) * 0.08
    add(mono(y), t0, g, human=False)

# ---------------- harmony: Bb major IV-iii-ii-V ----------------
PROG = ["Ebmaj7", "Dm7", "Cm7", "F7"]
CH = {"Ebmaj7": (63, 67, 70, 74), "Dm7": (62, 65, 69, 72), "Cm7": (60, 63, 67, 70), "F7": (60, 63, 65, 69), "Bbmaj7": (62, 65, 69, 70)}
ROOT = {"Ebmaj7": 39, "Dm7": 38, "Cm7": 36, "F7": 41, "Bbmaj7": 46}
def chord_of(b): return PROG[b % 4]
WALK = [(0, 0), (2, 7), (4, 12), (6, 10)]
def ubass(t0, t1, g=1.0, walk=True):
    for tt, k, b in eighths(t0, t1):
        pat = WALK if walk else [(0, 0), (5, 7)]
        for pos, iv in pat:
            if pos == k: add(gm("Acoustic Bass", ROOT[chord_of(b)] + iv, E8 * 1.9, 105 if k == 0 else 88, 0.1), tt, 0.62 * g)
def rhodes(t0, t1, g=1.0):
    for tt, k, b in eighths(t0, t1):
        if k in (0, 3, 6):
            for j, m in enumerate(CH[chord_of(b)]):
                add(gm("Tine Electric Piano", m, E8 * (2.6 if k == 0 else 1.4), 74 if k == 0 else 62, 0.3), tt + j * 0.012, 0.13 * g, pan=-0.2, wet=0.3)
def brushes(t0, t1, g=1.0, kick=True):
    for tt, k, b in eighths(t0, t1):
        if kick and k in (0, 5): add(drum(36, 84), tt, 0.4 * g)
        if k in (2, 6): add(drum(38, 82, "Brush"), tt, 0.32 * g, wet=0.15)
        add(drum(42 if k % 2 == 0 else 44, 60 if k % 2 == 0 else 46), tt, 0.11 * g, pan=-0.3)
def buzzbass(t0, t1, g=1.0, trem=26.0):
    for tt, k, b in eighths(t0, t1):
        if k == 0:
            f = 440 * 2 ** ((ROOT[chord_of(b)] + 12 - 69) / 12)
            buzzfx(tt, BAR * 0.96, f, 0.55 * g, trem)
MEL = [[(0, 74, 2), (2, 75, 1), (3, 77, 2), (6, 79, 2)],
       [(0, 77, 3), (3, 74, 1), (4, 72, 2), (6, 69, 2)],
       [(0, 70, 2), (2, 72, 1), (3, 75, 2), (5, 74, 1), (6, 72, 2)],
       [(0, 72, 4), (5, 69, 1), (6, 70, 2)]]
def melody(t0, t1, g=1.0, inst="Muted Trumpet", up=0):
    for tt, k, b in eighths(t0, t1):
        for pos, m, du in MEL[b % 4]:
            if pos == k: add(gm(inst, m + up, du * E8 * 1.1, 96 if k % 2 == 0 else 84, 0.25), tt, 0.26 * g, pan=0.2, wet=0.35, echo=0.15)
def groove(t0, t1, g=1.0, mel=True, inst="Muted Trumpet", buzz=1.0):
    ubass(t0, t1, g); rhodes(t0, t1, g); brushes(t0, t1, g)
    if buzz > 0: buzzbass(t0, t1, buzz * g)
    if mel: melody(t0, t1, g, inst)
def vib(t0, m, g=1.0): add(gm("Vibraphone", m, 0.8, 100, 0.5), t0, 0.32 * g, wet=0.4, echo=0.3)
def glock(t0, m, g=1.0): add(gm("Glockenspiel", m, 0.4, 95, 0.3), t0, 0.28 * g, wet=0.35, echo=0.3)
def pizz(t0, m, g=1.0): add(gm("Pizzicato Strings", m, 0.3, 100, 0.2), t0, 0.35 * g, wet=0.2)
def wood(t0, g=1.0, hi=True): add(drum(76 if hi else 77, 100), t0, 0.33 * g, pan=0.25 if hi else -0.25)
def flute(t0, m, d=0.5, g=1.0): add(gm("Flute", m, d, 96, 0.3), t0, 0.28 * g, wet=0.4, echo=0.2)
def big(t0, g=1.0):
    boom(t0, 1.0 * g, 1.2); add(drum(36, 127), t0, 1.0 * g); add(drum(49, 118), t0, 0.5 * g, wet=0.35)
    for m in (58, 62, 65, 70, 74): add(gm("Brass Section", m, 0.5, 122, 0.15), t0, 0.28 * g, wet=0.3)
    add(gm("Timpani", 34, 1.0, 120, 0.4), t0, 0.5 * g, wet=0.2)
    add(gm("Acoustic Bass", 34, 0.9, 127, 0.15), t0, 0.9 * g)
    buzzfx(t0, 0.9, 233, 0.9 * g, 30)

# ---------------- arrangement（全部读 cues）----------------
vinyl(0, DUR, 0.9)
# 0 s 大重音：干饭王
big(0.0, 0.9)
groove(0.3, T["myth"], 0.8, mel=False)
for j in range(int(T["myth"] / (2 * math.pi / 7.0))):          # 每次大口嚼 = 一个 pop（与 chew 周期一致）
    tt = (j + 0.5) * 2 * math.pi / 7.0 / 2 * 2
    if 0.5 < tt < T["myth"] - 0.2: popfx(tt, 0.32, 900 + 80 * (j % 3), 300)
ding(0.6, 0.35, 2794); pizz(1.5, 70, 0.6); pizz(1.7, 67, 0.5)             # 工牌弹出 / 同事“！”
# myth：轻快 swing + 小爱心 glock + 起飞嗡嗡
groove(T["myth"], T["night"], 0.75, inst="Vibraphone")
buzzfx(T["myth"] + 0.25, T["night"] - T["myth"] - 0.4, 250, 0.5, 34)
for j in range(4): glock(T["myth"] + 0.8 + j * 0.7, [82, 84, 86, 89][j], 0.45)
popfx(T["myth"] + 1.0, 0.4); popfx(T["myth"] + 2.0, 0.4, 900)
# night：潜行——只留拨弦一步一音 + 钟表滴答 + 低音
for j, tt in enumerate(np.arange(T["night"], T["q"] - 0.01, BEAT)): wood(tt, 0.5, j % 2 == 0)
for j in range(int(2.6 / (math.pi / 6.0))):
    tt = T["night"] + (j + 0.5) * math.pi / 6.0
    if tt < T["night"] + 2.6: pizz(tt, [58, 62, 65, 62][j % 4], 0.6)
ubass(T["night"], T["q"], 0.55, walk=False)
for j in range(3): add(gm("Music Box", [86, 89, 91][j], 0.6, 80, 0.4), T["night"] + 1.0 + j * 0.6, 0.18, wet=0.5)
# q：breakdown——心跳 + riser，SIL0 收
for j, tt in enumerate(np.arange(T["q"], SIL0, 0.62)): heartbeat(tt, 0.8 + 0.1 * j)
boing(T["q"] + 0.2, 0.35, 0.4, 350, 0.3, 5); boing(T["q"] + 0.5, 0.3, 0.4, 420, 0.3, 5)
riser(T["q"] + 0.2, SIL0, 0.9); add(gm("Reverse Cymbal", 60, 1.4, 110), SIL0 - 1.4, 0.25)
# BIG2：热成像揭晓 —— 小节原点重设
org(BIG2)
big(BIG2, 0.95); ding(BIG2 + 0.35, 0.5, 3136)
groove(BIG2, T["know"], 1.0)
for i in range(4): glock(BIG2 + 0.3 + i * 0.16, [82, 86, 89, 94][i], 0.45)
# know：知识卡——vibraphone 琶音 + 扫描线一声 whoosh + 低频嗡
for j in range(int((T["temp"] - T["know"]) / E8)): vib(T["know"] + j * E8, CH[PROG[(j // 8) % 4]][j % 4] + 12, 0.28)
whoosh(T["know"] + 0.5, 1.8, 0.6, 700); ubass(T["know"], T["temp"], 0.5, walk=False)
buzzbass(T["know"], T["temp"], 0.5)
# temp：温度计上升——上滑 + 计数滴答，到 34.8 一个 ding
ubass(T["temp"], T["muscle"], 0.7); rhodes(T["temp"], T["muscle"], 0.8); brushes(T["temp"], T["muscle"], 0.6, kick=False)
slide(T["temp"] + 0.6, 300, 620, 2.6, 0.5)
for j in range(19): tick(T["temp"] + 0.6 + 2.6 * (j / 19) ** 0.9, 0.35, 2800 + 30 * j)
ding(T["temp"] + 3.25, 0.55, 3520)
# muscle：飞行肌抖动——嗡嗡低音加强、颤动加快
groove(T["muscle"], T["exp"], 0.8, mel=False, buzz=0.0)
buzzbass(T["muscle"], T["exp"], 1.3, trem=34.0)
for j in range(int((T["exp"] - T["muscle"]) / (BEAT / 2))): tick(T["muscle"] + 0.4 + j * BEAT / 2, 0.18, 1800)
# exp：每个盒子标签一个拨弦 pop，雄蜂弹入 pop
groove(T["exp"], T["start"], 0.75, inst="Vibraphone", buzz=0.5)
for j in range(4): pizz(T["exp"] + 0.6 + j * 0.45, [70, 74, 77, 82][j], 0.7)
for j in range(9): popfx(T["exp"] + 1.0 + j * 0.15, 0.25, 1300 + 60 * j)
# start：数天——右边 6 下到“下蛋”ding，左边 15 下到 ding
ubass(T["start"], T["brood"], 0.6); rhodes(T["start"], T["brood"], 0.7); brushes(T["start"], T["brood"], 0.5, kick=False)
for j in range(6): wood(T["start"] + 0.3 + (FT.DAY_R - 0.3) * j / 6, 0.5, True)
for j in range(15): tick(T["start"] + 0.3 + (FT.DAY_L - 0.3) * j / 15, 0.35, 2500)
ding(T["start"] + FT.DAY_R, 0.6, 3136); glock(T["start"] + FT.DAY_R + 0.05, 89, 0.4)
ding(T["start"] + FT.DAY_L, 0.45, 2637)
# brood：幼虫一只只冒出来（每只一个上行 pop），×1.5 时 glock 琶音
groove(T["brood"], T["lab"], 0.75, buzz=0.5)
for i in range(10): popfx(T["brood"] + 0.3 + i * 0.17, 0.35, 900 + 90 * i, 400)
for i in range(4): glock(T["brood"] + 2.6 + i * 0.12, [82, 86, 89, 94][i], 0.4)
# lab：盖子落下 + 上锁，转小调
thunk(T["lab"] + 0.9, 0.9); click(T["lab"] + 1.0, 0.9)
for j, ch in enumerate(["Cm7", "F7"]):
    for m in CH[ch]: add(gm("Tine Electric Piano", m, 2.4, 70, 0.4), T["lab"] + 0.3 + j * 2.6, 0.14, wet=0.35)
ubass(T["lab"], T["wild"], 0.55, walk=False); brushes(T["lab"], T["wild"], 0.4, kick=False)
# wild：户外——长笛问句 + 鸟鸣 + 嗡嗡
for j, m in enumerate([74, 77, 79, 77, 74, 72]): flute(T["wild"] + 0.3 + j * 0.45, m, 0.42, 0.8)
chirp(T["wild"] + 0.6, 0.6); chirp(T["wild"] + 2.7, 0.5)
buzzfx(T["wild"] + 0.2, T["end"] - T["wild"] - 0.4, 230, 0.35, 32)
ubass(T["wild"], T["end"], 0.55); rhodes(T["wild"], T["end"], 0.6)
# end：工牌翻面——铜管 ta-da + 彩纸 pop + groove 回归
for m in (58, 65, 70, 74): add(gm("Brass Section", m, 0.7, 110, 0.2), T["end"] + 0.9, 0.22, wet=0.3)
for j in range(6): popfx(T["end"] + 0.95 + j * 0.08, 0.3, 1500 - 100 * j)
ding(T["end"] + 0.9, 0.5, 3520)
FINAL = DUR - 1.4
groove(T["end"], FINAL, 0.8)
for j, m in enumerate((34, 46, 58, 62, 65, 69, 70)): add(gm("Vibraphone" if m > 45 else "Acoustic Bass", m, 1.4, 105, 0.6), FINAL + j * 0.02, 0.4, wet=0.35)
add(drum(36, 100), FINAL, 0.5); add(drum(49, 70), FINAL, 0.2, wet=0.4); buzzfx(FINAL, 1.2, 233, 0.4, 26)
# ---------------- mix ----------------
def reverb(x, sec=1.6, dec=3.2):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * dec); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir /= np.abs(ir).sum() ** 0.5 * 10
    sz = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, sz) * np.fft.rfft(ir, sz), sz)[: len(x)]
d_ = int(3 * E8 / 2 * SR)
for r in range(1, 3):
    sh = ECHO[: N - d_ * r] * (0.4 ** r)
    MIX[d_ * r:, 0] += sh[:, 1] * (0.8 if r % 2 else 0.3); MIX[d_ * r:, 1] += sh[:, 0] * (0.3 if r % 2 else 0.8)
MIX += np.stack([reverb(VERB[:, 0]), reverb(VERB[:, 1])], 1) * 0.5
# lo-fi：轻微 tape wow（0.6 Hz，±6 cents）
t_ = np.arange(N) / SR; idx = np.clip(t_ * SR + 0.0035 * SR * np.sin(2 * np.pi * 0.6 * t_) / (2 * np.pi * 0.6), 0, N - 1)
MIX = np.stack([np.interp(idx, np.arange(N), MIX[:, c]) for c in range(2)], 1)
i0, i1 = int(SIL0 * SR), int(BIG2 * SR); fade = np.linspace(1, 0, int(0.04 * SR))
MIX[i0:i0 + len(fade)] *= fade[:, None]; MIX[i0 + len(fade):i1] *= 0.1
MIX = np.tanh(MIX / np.abs(MIX).max() * 2.0); MIX /= np.abs(MIX).max() / 0.85
fo = int(0.8 * SR); MIX[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open("/workspace/work/claybee/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((MIX * 32767).astype("<i2").tobytes())
r = [20 * np.log10(np.sqrt((MIX[int(i * SR):int((i + 2) * SR)] ** 2).mean()) + 1e-9) for i in range(0, int(DUR), 2)]
print("RMS/2s dBFS:", " ".join(f"{i*2}:{v:.1f}" for i, v in enumerate(r)))
print("ok BPM %.2f DUR %.2f BIG2 %.2f" % (BPM, DUR, BIG2))
