# 《48年的蛆狮之谜》 Vermitigris tsangyanggyatso — Shan & Wang 2026, ZooKeys 1276: 249-262 (PMC full text checked; Pensoft/EurekAlert 2026-06-24)
# ADAPTIVE TIMELINE: each subtitle >= max(1.5 s, chars/4 s)+extra; grid = 100 BPM 4/4 from 0.4 s; BIG2 follows the last pre text directly.
import math, re
BPB = 4; BEAT = 60 / 100; BAR = BPB * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9Ω]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
PRE = [("hook", "这条小虫，|在沙里挖了个死亡漏斗", 0.0),
       ("ant", "蚂蚁路过，|一脚踩空", 0.4),
       ("slide", "沙往下滑，|越爬越往下掉", 0.4),
       ("bottom", "坑底有东西……", 0.2),
       ("q", "是蚁狮吗？", 0.0)]
POST = [("reveal", "不！是苍蝇的幼虫，|叫“蛆狮”", 0.4),
        ("fam", "全世界只有这一类苍蝇，|幼虫会挖陷阱", 0.4),
        ("same", "和蚁狮不是亲戚，|却想出了同一招", 0.4),
        ("y1978", "1978年，西藏亚东|就挖到过这种幼虫", 0.4),
        ("wait", "可成虫长啥样，|一直没人知道", 0.4),
        ("y2025", "2025年，科考队|终于抓到了成虫", 0.4),
        ("newsp", "确认是新物种！", 0.3),
        ("size", "成虫约19毫米，|幼虫最长28毫米", 0.4),
        ("nofood", "成虫嘴很短，|可能一辈子不吃东西", 0.4),
        ("home", "幼虫最爱躲在|河边大石头下的细沙里", 0.4),
        ("pose", "一碰它，|就弯成Ω形防御", 0.4),
        ("name", "名字献给诗人仓央嘉措", 0.4),
        ("count", "全世界的蛆狮，|从66种变成67种", 0.4),
        ("card", "记住这张牌", 3.0),
        ("end", "48年的谜，|终于有了名字", 3.0)]
T = {}; SUBS = []; k = 0
for i, (key, s, ex) in enumerate(PRE):
    st = -0.2 if i == 0 else qb(k)
    end_need = (0.0 if i == 0 else qb(k)) + need(s, ex)
    nb = max(1, math.ceil((end_need - G0) / BEAT - 1e-6)) - k
    T[key] = qb(k) if i else qb(0); SUBS.append([st, None, s, key]); k += nb
SIL0 = qb(k); BIG2 = qb(k); K2 = k
for key, s, ex in POST:
    T[key] = qb(k); SUBS.append([qb(k), None, s, key]); k += math.ceil(need(s, ex) / BEAT - 1e-6)
DUR = qb(k)
for i in range(len(SUBS)): SUBS[i][1] = SUBS[i + 1][0] if i + 1 < len(SUBS) else 99
HOOK_HIT = qb(0); HOOKCUT = T["ant"]; HOOK_STOP = round(HOOKCUT - BEAT / 2, 4)
def at(key, beats): return round(T[key] + beats * BEAT, 4)
NAMES = [a for a, _, _ in PRE + POST]
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
SILENCES = []
CUTS = [HOOKCUT] + [T[n] for n in NAMES[2:] if n not in ("reveal", "slide", "bottom", "q", "newsp")] + [BIG2]
if __name__ == "__main__":
    for st, en, s, key in SUBS: print(f"{key:7s} {st:6.2f}-{min(en,DUR):6.2f}  {min(en,DUR)-max(st,0):4.2f}s need {need(s):4.2f}  {s}")
    print("BIG2", BIG2, "DUR", DUR, "HOOKCUT", HOOKCUT)
