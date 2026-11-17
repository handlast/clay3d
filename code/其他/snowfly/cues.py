# 《雪蝇》 — Capek et al. 2026 Current Biology doi:10.1016/j.cub.2026.02.060; Northwestern/ScienceDaily 2026-03-26
import math, re
BPB = 4; BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "零下6度，|这只虫子在雪地上散步"),
         ("q", 5, "别的虫冻成冰棍，|它偏这时出门"),
         ("who", 11, "雪蝇：没有翅膀，|是大蚊的亲戚"),
         ("sperm", 17, "虫子是冷血动物，|天一冷就躲起来"),
         ("egg", 23.5, "它凭什么不被冻住？"),
         ("reveal", 32, "它自己会发热！"),
         ("how", 37, "不靠发抖，|体温比别的虫高一两度"),
         ("xray", 44, "热可能来自细胞，|有点像北极熊的棕色脂肪"),
         ("swim", 52, "体内还有防冻蛋白，|贴住冰晶不让它长大"),
         ("gene", 59, "这种蛋白的结构，|和北极鱼的是亲戚"),
         ("why", 65.5, "感受冷刺痛的受体，|比蚊子迟钝30倍"),
         ("order", 72, "雪一化，|它反而躲起来"),
         ("card", 78, "记住这张卡"),
         ("end", 87, "你在寒潮里发抖，|它在雪地上约会")]
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
