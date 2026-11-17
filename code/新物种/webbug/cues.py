# 《蜘蛛网上的新虫》 — Xiong et al. 2026 ZooKeys 1296:11-25 doi:10.3897/zookeys.1296.200871; New Scientist 2026-11-10
import math, re
BPB = 4; BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "它住在蜘蛛网上，|蜘蛛却不吃它"),
         ("q", 5, "只有盐粒那么大，|约1毫米"),
         ("who", 10.5, "2025年9月，|在福建的蜘蛛网上发现"),
         ("sperm", 17, "一个新物种：|Heissophila sinica"),
         ("egg", 23.5, "它在网上靠什么活？"),
         ("reveal", 32, "吃蜘蛛的剩饭！"),
         ("how", 37, "还吃网上的螨虫，|有些螨寄生蜘蛛"),
         ("xray", 43, "蜘蛛蜕皮时，|它们围上去喝体液"),
         ("swim", 51, "它们不躲蜘蛛，|反而跟着它绕圈"),
         ("gene", 57, "可能因为太小，|蜘蛛不拿它当饭"),
         ("why", 64, "卵、小虫、成虫|都在同一张网上"),
         ("order", 70.5, "它可能一辈子|都住在网上"),
         ("card", 77, "记住这张卡"),
         ("end", 86, "走网怎么不粘脚？|科学家还没弄清")]
ENDB = 95
T = {k: qb(b) for k, b, s in LINES}; B = {k: b for k, b, s in LINES}
NAMES = [k for k, b, s in LINES]
SUBS = [[(-0.2 if i == 0 else qb(b)), (qb(LINES[i + 1][1]) if i + 1 < len(LINES) else 99), s, k] for i, (k, b, s) in enumerate(LINES)]
BIG2 = qb(32); DUR = qb(ENDB); HOOK_HIT = qb(0); HOOKCUT = T["q"]; HOOK_STOP = qb(4); SIL0 = qb(31)
def at(key, beats): return round(T[key] + beats * BEAT, 4)
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
CUTS = [T[n] for n in NAMES[1:]]
if __name__ == "__main__":
    for st, en, s, key in SUBS:
        en = min(en, DUR); print(f"{key:7s} {st:6.2f}-{en:6.2f} {en-max(st,0):4.2f}s need {need(s):4.2f} {'SHORT' if en-max(st,0) < need(s) else ''} {s}")
    print("BIG2", BIG2, "DUR", DUR, "BPM", round(BPM, 2))
