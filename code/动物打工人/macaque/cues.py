# 《动物打工人 No.01 爱看同事社交的猴子》 — Pereira et al. 2026 Current Biology doi:10.1016/j.cub.2026.10.037; phys.org 2026-11-09
import math, re
BPB = 4; BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "爱围观的猴子，|两年后地位更高"),
         ("q", 5, "泰国野外，|46只雄性阿萨姆猕猴"),
         ("who", 10.5, "研究者记下：|每只猴围观同伴多久"),
         ("sperm", 17, "围观分两种：|理毛 和 打架"),
         ("egg", 23.5, "猜猜，看哪种更有用？"),
         ("reveal", 32, "看理毛的！"),
         ("how", 37, "第一年：|它们交到更铁的朋友"),
         ("xray", 43, "第二年：|地位跟着升高"),
         ("swim", 51, "地位高的，|交配次数多约20%"),
         ("gene", 57, "打架反而看得更多，|却跟地位没关系"),
         ("why", 64, "打架谁都盯着，|怕被卷进去"),
         ("order", 70.5, "爱看理毛的，|也更会出手搅局"),
         ("card", 77, "记住这张卡"),
         ("end", 86, "人也爱盯着：|谁和谁关系好")]
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
