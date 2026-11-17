# 《歪脸鲸》 — Benites-Palomino et al. 2026 Communications Biology doi:10.1038/s42003-026-11074-2 (2026-11-09); UZH / NHMLA releases
import math, re
BPB = 4; BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "这头鲸，|两个鼻孔都长在左边"),
         ("q", 5, "不是化石压歪的，|它天生就歪"),
         ("who", 11.5, "600万年前的小抹香鲸，|身长约2.7米"),
         ("sperm", 18, "其实齿鲸的头骨|本来就有点歪"),
         ("egg", 24, "那它歪到什么程度？"),
         ("reveal", 32, "史上最歪的鲸！"),
         ("how", 37, "可能也是|最歪的哺乳动物"),
         ("xray", 44, "发声的“声呐”器官越大，|头骨就挤得越歪"),
         ("swim", 51.5, "嘴往下弯31度，|脖子还能再低55度"),
         ("gene", 57.5, "贴着海底游，|推测用声呐扫泥里的猎物"),
         ("why", 64.5, "它没有胡须，|全靠这颗歪头找吃的"),
         ("order", 70.5, "种名huachafo：|秘鲁俚语“浮夸”"),
         ("card", 77, "记住这张卡"),
         ("end", 86, "歪得离谱，|却刚好够它吃饭")]
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
