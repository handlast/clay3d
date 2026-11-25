# 《橙子鱼》 — Abrantes et al. 2026 Zoosystematics and Evolution 102(4):1079, doi:10.3897/zse.102.187659; ScienceDaily/Pensoft 2026-11-08
import math, re
BPB = 4; BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "不到3厘米，|只在3个水坑见过"),
         ("q", 5, "新物种，名叫“橙子”"),
         ("who", 11.5, "前半身橙色圆点，|尾巴橙色人字纹"),
         ("sperm", 18, "颜色、鳞片、骨头、DNA|一项项比对"),
         ("egg", 24, "新物种确认！可它的地盘……"),
         ("reveal", 32, "全部已知分布，|比澳门还小"),
         ("how", 37, "一个水坑，|挨着采矿冲来的浑水"),
         ("xray", 44, "一个在城里，|漂着塑料"),
         ("swim", 51.5, "作者认为：|够格列为濒危"),
         ("gene", 57.5, "亲戚的卵能在湿泥里|停住发育，等雨回来"),
         ("why", 64.5, "可水坑要是没了，|再会等也没用"),
         ("order", 70.5, "建议扩大保护区，|把水坑圈进去"),
         ("card", 77, "记住这张卡"),
         ("end", 86, "刚被认识，|别马上就告别")]
ENDB = 94
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
