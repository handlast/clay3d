# 《乌鸦做决定比人快一倍》 — Schmidbauer P, Nieder A. 2026. Ultrarapid decision-making in an avian brain. Science 394(6822):445-449,
# published 2026-10-22, doi:10.1126/science.aed6459 (abstract read). ZME Science 2026-11-06 + Ars Technica 2026-10-23 + Tübingen PR (read):
# two carrion crows Iggy & Lemmy; random-dot motion on touchscreen; peck left/right target for mealworm; ~235 ms (to head turn onset);
# monkeys ~410-600 ms, humans ~450-820 ms (six earlier studies); 3% coherence still above chance; near 100% with clear signal;
# 248 neurons in NCL, 58 choice-predictive; ~70 ms after onset, ~170 ms before response; ramping, steeper with stronger evidence;
# birds lack 6-layer neocortex; why fast = untested hypotheses (dense short wiring, 41-42 C body temp).
# MUSIC GRID cloned from muppet: 97.96 BPM, 0.4 s and 20.0 s on bar lines, silence beat 31.
import math, re
BPB = 4; BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "乌鸦做决定|比人快一倍"),
         ("q", 5, "一屏乱飘的点，|它0.235秒就选好了"),
         ("who", 11.5, "主角是两只小嘴乌鸦：|Iggy和Lemmy"),
         ("sperm", 18, "看点往哪边飘，|啄对边就有面包虫"),
         ("egg", 24, "同一道题，|人和猴子要多久？"),
         ("reveal", 32, "人要0.45到0.82秒！"),
         ("how", 37, "只有3%的点同向，|它也比瞎猜准"),
         ("xray", 43.5, "248个神经元里，|58个能预判它选哪边"),
         ("swim", 51, "点出现约70毫秒，|答案就已经有了"),
         ("gene", 57, "证据越强，|神经元冲得越快"),
         ("why", 63.5, "鸟没有人那种六层皮层，|算法却很像"),
         ("order", 70, "为什么这么快？|可能是脑子小、线路短"),
         ("card", 77, "记住这张卡"),
         ("end", 86, "口诀：乌鸦脑子小，|出手比你早")]
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
