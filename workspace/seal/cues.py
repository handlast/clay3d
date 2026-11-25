# 《海豹打个盹，顺手偷听了鲸鱼》 — Gros-Martial A, Torterotot M, Picard B, Michel M, Cazau D, Bazin S, Guinet C. 2026.
# Cetacean acoustic occurrence in the Southern Ocean from biologged southern elephant seals. Front. Mar. Sci. 13, doi:10.3389/fmars.2026.1832052 (2026-10-07, full text read)
# facts: 2017-2020, 9 female SES (3 Peninsula Valdes, 6 Kerguelen), head-mounted DTAG4; drift phases = rest, falling-leaf, little flow noise;
# 109 h 11 min drift recordings annotated; mean drift depth ~264-338 m; 6 mysticete spp + sperm whale + delphinids; ABW most annotated (134 drift phases);
# tags recollected at moult in January. Discover Wildlife 2026-10-27 (poor weather, hard to spot dolphins).
# MUSIC GRID cloned from muppet: 97.96 BPM, 0.4 s and 20.0 s on bar lines, silence beat 31.
import math, re
BPB = 4; BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "这只海豹头上|顶着一个“窃听器”"),
         ("q", 5, "9只雌海豹，|头上都装了录音标签"),
         ("trip", 11.5, "出海觅食时，|它们会停下来休息"),
         ("leaf", 18, "不划水，像片落叶|慢慢往下漂"),
         ("deep", 24, "漂在几百米深的黑暗里，|标签一直在录音"),
         ("reveal", 32, "它在偷听鲸鱼！"),
         ("quiet", 37, "不划水就没水流声，|正好当“窃听站”"),
         ("hours", 43.5, "109小时录音里，|录到7种鲸"),
         ("blue", 49.5, "最常出现的是南极蓝鲸"),
         ("more", 55.5, "还有座头鲸、抹香鲸，|甚至海豚"),
         ("why", 62, "南大洋风大浪高，人很难去，|海豹替人去听"),
         ("back", 69, "1月回岸换毛时，|再把标签取回来"),
         ("card", 76, "记住这张卡"),
         ("end", 86, "口诀：海豹歇一歇，|鲸鱼全露馅")]
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
