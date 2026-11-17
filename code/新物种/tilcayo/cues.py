# 《蒂尔卡约虎猫》 — Lescroart et al. 2026 Current Biology doi:10.1016/j.cub.2026.08.059; phys.org/AFP 2026-09-18
import math, re
BPB = 4; BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "这只“小猫”，|是百年首个新野猫"),
         ("q", 5, "一家人把它|当成家猫收养了"),
         ("who", 10.5, "它叫蒂尔卡约虎猫，|比家猫还小一圈"),
         ("sperm", 17, "南美小斑点虎猫，|曾被当成同一种"),
         ("egg", 23.5, "它真是新物种吗？"),
         ("reveal", 32, "测全基因组：是！"),
         ("how", 37, "上一次发现新野猫，|还是1923年"),
         ("xray", 43, "比对38只猫的全基因组，|8只来自博物馆"),
         ("swim", 51, "最新结论：|虎猫一共有5种"),
         ("gene", 57, "学名用了当地人的叫法：|tilcayo"),
         ("why", 64, "目前只找到2只，|只在玻利维亚"),
         ("order", 70.5, "一只住救助站，|一只救治后放归山林"),
         ("card", 77, "记住这张卡"),
         ("end", 86, "当地人早就认识它，|科学界刚给它上了户口")]
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
