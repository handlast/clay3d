# 《向日葵朝最暗的灯长》 — Kempinski A, Porat A, Rivière M, Meroz Y. PNAS 2026 Sep 29;123(39):e2614473123 (epub 2026-09-22), doi:10.1073/pnas.2614473123
# Facts (ZME 2026-11-04, TAU release 2026-11-04, PubMed abstract): week-old sunflower seedlings 1-3 cm; blue LED; tracked >=21 h (ZME) / >20 h (TAU)
# 1 lamp: brighter -> bends more, doubling intensity < double bend. 2 opposite lamps: bend to brighter, more difference -> more lean.
# 3 lamps: two equal opposite + third at right angle, < half as intense; 34 seedlings, average almost exactly toward dim one; individuals vary.
# mechanism: phototropins near stem surface sense locally; compressed (nonlinear) transduction; vectorial sum of transduced signals.
# model predicts "illusion" up to ~6 deg, not yet observed (stems naturally sway/circle).
import math, re
BPB = 4; BEAT = 60 / 100; BAR = BPB * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
PRE = [("hook", "三盏灯，|它偏朝最暗的长", 0.0),
       ("q", "向日葵是不是傻了？", 0.0)]
POST = [("reveal", "没傻：两盏强光|互相抵消了", 0.5),
        ("who", "主角：1周大的向日葵苗，|只有1到3厘米高", 0.4),
        ("lamp1", "实验一：|只开一盏蓝光灯", 0.4),
        ("bright", "灯越亮，|它弯得越厉害", 0.4),
        ("double", "但亮度翻倍，|弯曲却不到两倍", 0.6),
        ("lamp2", "实验二：左右各一盏，|一亮一暗", 0.4),
        ("lean", "它朝亮的那边弯，|亮度差越大，弯得越多", 0.4),
        ("lamp3", "实验三：|左右两盏一样亮", 0.4),
        ("third", "侧面再加一盏，|亮度不到它们的一半", 0.6),
        ("n34", "34株苗，平均方向|几乎正对最暗那盏", 0.8),
        ("vary", "单株歪法各不相同，|平均下来才是这个方向", 0.4),
        ("how", "茎的表面有感光蛋白，|每一小块各自感光", 0.4),
        ("compress", "信号会被“压缩”：|光强翻倍，反应不到两倍", 0.6),
        ("sum", "再把各方向的信号相加：|左右一样大，正好抵消", 0.6),
        ("left", "只剩侧面那盏弱光|在指方向", 0.4),
        ("illusion", "模型还预测它会有“视错觉”，|最多偏6度", 0.4),
        ("notyet", "不过这一点|还没被观测到", 0.4),
        ("card", "记住这张卡", 8.4),
        ("end", "向日葵口诀：|强光打架，弱光说了算", 3.4)]
T = {}; SUBS = []; k = 0
for i, (key, s, ex) in enumerate(PRE):
    st = -0.2 if i == 0 else qb(k)
    end_need = (0.0 if i == 0 else qb(k)) + need(s, ex)
    nb = max(1, math.ceil((end_need - G0) / BEAT - 1e-6)) - k
    T[key] = qb(k) if i else qb(0); SUBS.append([st, None, s, key]); k += nb
BIG2 = qb(k); K2 = k
NB = {}
for key, s, ex in POST:
    nb = math.ceil(need(s, ex) / BEAT - 1e-6); nb += nb % 2; NB[key] = nb
    T[key] = qb(k); SUBS.append([qb(k), None, s, key]); k += nb
DUR = qb(k)
for i in range(len(SUBS)): SUBS[i][1] = SUBS[i + 1][0] if i + 1 < len(SUBS) else 99
HOOK_HIT = qb(0); HOOKCUT = T["q"]; HOOK_STOP = round(HOOKCUT - BEAT / 2, 4)
def at(key, beats): return round(T[key] + beats * BEAT, 4)
NAMES = [a for a, _, _ in PRE + POST]
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
CUTS = [HOOKCUT] + [T[n] for n in NAMES[2:] if n not in ("bright", "double", "lean", "third", "vary", "left", "notyet")] + [BIG2]
def bars(key): return (T[key] - BIG2) / BAR
if __name__ == "__main__":
    for st, en, s, key in SUBS: print(f"{key:8s} {st:6.2f}-{min(en,DUR):6.2f}  {min(en,DUR)-max(st,0):4.2f}s need {need(s):4.2f}  bar {(max(st,0)-BIG2)/BAR:6.2f}  {s}")
    print("BIG2", BIG2, "DUR", DUR, "bars after BIG2", (DUR - BIG2) / BAR)
