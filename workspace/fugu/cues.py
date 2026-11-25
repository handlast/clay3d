# 《河豚宝宝》 — Kaneko et al. 2026 iScience 29(9):117080, doi:10.1016/j.isci.2026.117080 (published 2026-08-18; full text PMC13594433)
# Itoi et al. 2014 Toxicon 78:35 (maternal TTX). Orsted fugu meme: fan meme, canonical source unverified.
import math, re
BPB = 4; BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "最强龙神，|也被河豚毒倒过"),
         ("q", 5, "河豚妈妈把毒|装进卵里传给宝宝"),
         ("who", 11.5, "可新研究发现，|护娃靠的不全是剧毒"),
         ("sperm", 18, "斑鱾吃到剧毒宝宝，|照样吞下去"),
         ("egg", 24, "换成几乎无毒的TDT……"),
         ("reveal", 32, "一入口，就吐！"),
         ("how", 37, "TDT铺满宝宝|全身的皮肤"),
         ("xray", 44, "鱼一尝到，|马上吐出来"),
         ("swim", 51.5, "比目鱼更挑：|剧毒和TDT都吐"),
         ("gene", 57.5, "妈妈给了两道防线：|剧毒，加一个“难吃”警报"),
         ("why", 64.5, "同一种分子，|河豚自己闻到会靠近"),
         ("order", 70.5, "警报不用毒死对方，|吐出来就能活"),
         ("card", 77, "记住这张卡"),
         ("end", 86, "龙神要是会吐，|就不用读档了")]
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
