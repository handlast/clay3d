# 《小草让水往高处流》 — Qi X, Du J, Zhang X, Wang Y, Wang H, Zhang T, Shi Y, Xu B. 2026. Directional water transport system resolves
# fertilization-dispersal conflicts in Marchantia. Nature Plants, published 2026-10-29, doi:10.1038/s41477-026-02450-1 (abstract read);
# Earth.com 2026-11-07 (read): sperm must swim; female stalk lifts eggs; stalk & head carry water upward on outer surface, no pump;
# several tiny surface structures precisely positioned; 3D X-ray imaging; intact structures -> fertilization success; MpLAS (GRAS) controls them;
# MpGRAS10 builds stalk (gibberellin genes MpKAOL1/2); height helps spores spread; stalk evolved first, water structures later.
# MUSIC GRID cloned from muppet: 97.96 BPM, 0.4 s and 20.0 s on bar lines, silence beat 31.
import math, re
BPB = 4; BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "这棵小草能让水|往高处流"),
         ("q", 5, "不靠泵，水却|顺着伞柄往上爬"),
         ("who", 11.5, "它叫地钱，|贴着湿地面长"),
         ("sperm", 18, "它的精子|只能在水里游"),
         ("egg", 24, "可卵细胞被举在|一把“小伞”顶上"),
         ("reveal", 32, "伞柄会把水|往上送！"),
         ("how", 37, "柄上几种小结构，|位置排得刚刚好"),
         ("xray", 43.5, "科学家用3D X光|把它们拍了出来"),
         ("swim", 49.5, "水爬上去，精子|顺着水游到卵那里"),
         ("gene", 55.5, "总开关是一个|叫MpLAS的蛋白"),
         ("why", 62, "为什么要举高？|孢子从高处撒得更远"),
         ("order", 69, "先长出了高柄，|运水结构是后来才有的"),
         ("card", 76, "记住这张卡"),
         ("end", 86, "口诀：小伞会运水，|精子游上楼")]
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
