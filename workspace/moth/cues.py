# 《天蛾的超声干扰器》 Masonick et al. 2026 Proc. R. Soc. B, doi 10.1098/rspb.2026.2303 (Science News 2026-11-04, Elie Dolgin)
# ADAPTIVE TIMELINE: each subtitle >= max(1.5 s, chars/4 s)+extra; grid = 116 BPM, 4/4, from 0.4 s. BIG2 follows the last pre text directly.
import math, re
BPB = 4; BEAT = 60 / 116; BAR = BPB * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
PRE = [("hook", "蝙蝠追来，|这只蛾子让它雷达花屏", 0.0),
       ("chase", "蝙蝠夜里靠回声抓虫", 0.4),
       ("ping", "叫一声，听回声，|就知道虫在哪", 0.4),
       ("lock", "锁定！", 0.2),
       ("q", "蛾子怎么反击？", 0.0)]
POST = [("reveal", "尾巴一刮，|放出一串超声波！", 0.4),
        ("jam", "蝙蝠的回声被搅乱，|扑了个空", 0.4),
        ("organ", "发声的地方，|是尾端的抱握器", 0.4),
        ("scale", "上面长着一片|橄榄球形的大鳞片", 0.4),
        ("way", "拿它刮身上别处，|一共三种刮法", 0.4),
        ("w1", "①鳞片刮鳞片：|一阵一阵乱响", 0.4),
        ("w1b", "可能是吓蝙蝠一跳，|或冒充难吃的虫", 0.4),
        ("w2", "②刮腹部边缘的硬刺", 0.4),
        ("w3", "③刮腹下的微小凸起，|这是首次发现", 0.4),
        ("jam2", "刮刺和凸起声音更连续，|更能干扰声呐", 0.4),
        ("count", "测了143种天蛾，|77种会发超声", 0.4),
        ("evo", "这招至少独立演化4次，|最多7次", 0.4),
        ("lose", "改到白天活动的天蛾，|反而把装备弄丢了", 0.4),
        ("card", "记住这张牌", 3.0),
        ("end", "蝙蝠的晚饭，|被一把“梳子”搅黄了", 3.0)]
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
HOOK_HIT = qb(0); HOOK_STOP = qb(5.5); HOOKCUT = qb(6)
def at(key, beats): return round(T[key] + beats * BEAT, 4)
NAMES = [a for a, _, _ in PRE + POST]
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
SILENCES = []
CUTS = [HOOKCUT] + [T[n] for n in NAMES[2:] if n not in ("reveal", "w1b")] + [BIG2]
if __name__ == "__main__":
    for st, en, s, key in SUBS: print(f"{key:7s} {st:6.2f}-{min(en,DUR):6.2f}  {min(en,DUR)-max(st,0):4.2f}s need {need(s):4.2f}  {s}")
    print("BIG2", BIG2, "DUR", DUR, "HOOKCUT", HOOKCUT, "T chase", T["chase"])
