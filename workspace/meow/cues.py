# 《猫冲你喵》 — Fukimoto et al. 2026 Animal Behaviour doi:10.1016/j.anbehav.2026.123756; phys.org 2026-11-12
import math, re
BPB = 4; BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "猫冲你喵喵叫，|是在叫你帮忙？"),
         ("q", 5, "把猫爱吃的零食|锁进透明盒子"),
         ("who", 10.5, "38只猫，|每只考两场，各1分钟"),
         ("sperm", 17, "一场主人在旁边看，|一场主人离开"),
         ("egg", 23.5, "哪一场猫叫得多？"),
         ("reveal", 32, "主人在：喵的几率约16倍！"),
         ("how", 37, "约56%的喵，|是看着主人叫的"),
         ("xray", 43, "它还在主人和盒子之间|来回看"),
         ("swim", 51, "像是要把你的目光|引到盒子上"),
         ("gene", 57, "主人一走，|它更常站着望门"),
         ("why", 64, "不过这还不能证明，|猫是“故意”在说话"),
         ("order", 70.5, "而且实验里的猫，|本来就爱在饭点叫"),
         ("card", 77, "记住这张卡"),
         ("end", 86, "下次它冲你喵，|看看它在看哪里")]
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
