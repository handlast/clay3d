# 《狮子座流星雨》 — 北京日报 2026-11-01（宋媛媛：11月18日8时极大，午夜后观测）；AstroTools 2026-10-26（ZHR≈15，黑暗郊外 8–12/h，71 km/s，凌晨2–6时最佳，母彗星55P）；
# NASA Leonids（71 km/s，约33年一次流星暴）；Planetary Society（1966年15分钟内每分钟数千颗；流星暴≥1000/h）；Kosmos.info.pl（遇到新鲜密集尘埃带才有流星暴）；SkyFlux（几乎迎面撞上地球）。
# MUSIC GRID cloned from muppet: 97.96 BPM, 0.4 s and 20.0 s on bar lines.
import math, re
BPB = 4; BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "这场流星雨，|曾每分钟下几千颗"),
         ("q", 5, "狮子座流星雨，|11月18日早上8点极大"),
         ("who", 11.5, "流星，其实是|彗星掉下的尘埃"),
         ("sperm", 18, "这颗彗星|每33年回来一次"),
         ("egg", 24, "地球每年11月|都穿过它的尘埃……"),
         ("reveal", 32, "迎面撞上，|每秒71公里！"),
         ("how", 37, "最快的年度流星雨，|常拖着发光余迹"),
         ("xray", 44, "撞上新鲜密集的尘埃，|就变成流星暴"),
         ("swim", 51.5, "1966年，15分钟里|每分钟几千颗"),
         ("gene", 57.5, "今年没流星暴，|理想条件每小时15颗"),
         ("why", 64.5, "黑暗郊外，|每小时能看到8到12颗"),
         ("order", 70.5, "18日凌晨2点到天亮，|越往后越多"),
         ("card", 77, "记住这张卡"),
         ("end", 86, "口诀：彗星掉渣，|地球迎面撞上")]
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
