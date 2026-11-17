# 《企鹅便便让南极雪变绿》 — Ryan EL, Khan AL. 2026. JGR Biogeosciences 131:e2026JG009918, 2026-10-07, doi:10.1029/2026JG009918（全文已读）；CU Boulder Today 2026-11-06。
# 事实：西南极半岛 9 个海岸点，111 份雪样（2024–25 南半球夏季）；绿雪磷酸盐中位数 113.8 μM，红雪 11.43 μM（约 10 倍），干净雪 1.54 μM（约 70 倍）；
# 高磷样本细胞更密、色素更多；磷与野生动物影响正相关 r=0.54；企鹅吃磷虾，粪便把海里的磷带上雪（相关性研究）；
# 引 Khan 2021：绿藻可让雪反照率最多降 40%，红藻约 20%；Khan：现有融雪预测没算进去；企鹅向南迁，绿雪会跟着走。
# MUSIC GRID cloned from muppet: 97.96 BPM, 0.4 s and 20.0 s on bar lines.
import math, re
BPB = 4; BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "企鹅便便，|可能在帮南极雪融化"),
         ("q", 5, "南极半岛9个海岸，|铲了111份雪"),
         ("who", 11.5, "雪里住着雪藻，|有绿的，也有红的"),
         ("sperm", 18, "企鹅吃磷虾，|便便里有大量的磷"),
         ("egg", 24, "雪藻吃到这些磷……"),
         ("reveal", 32, "绿雪的磷，|是干净雪的70倍！"),
         ("how", 37, "也是红雪的10倍，|藻长得更密更绿"),
         ("xray", 44, "白雪像镜子，|把阳光反射回去"),
         ("swim", 51.5, "绿藻能让雪的反光|最多少四成"),
         ("gene", 58.5, "雪变暗，吸热更多，|融得更快"),
         ("why", 64.5, "融雪预测，|还没算进企鹅便便"),
         ("order", 70.5, "企鹅往南搬，|绿雪可能跟着走"),
         ("card", 77, "记住这张卡"),
         ("end", 86, "口诀：企鹅一拉，|雪就变绿")]
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
