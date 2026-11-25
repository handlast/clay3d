# 《超级士兵 No.01 白色死神》 — Simo Häyhä; en.wikipedia (Saarelainen 2016; Finnish Army JR34 docs)
import math, re
BPB = 4; BEAT = 19.6 / 40; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "零下40度，|他在雪里一趴一整天"),
         ("q", 6.25, "他叫西莫·海耶，|外号“白色死神”"),
         ("who", 13.1, "1939年冬季战争，|芬兰对抗苏联"),
         ("sperm", 21.25, "他身高只有1.6米，|一身白衣藏进雪里"),
         ("egg", 29.4, "他靠什么不被发现？"),
         ("reveal", 40, "嘴里含雪！"),
         ("how", 46.25, "这样呼出的白气|就不会暴露位置"),
         ("xray", 53.75, "枪口前把雪压实，|开枪不扬起雪雾"),
         ("swim", 63.75, "不用瞄准镜：|铁瞄不起雾、不反光"),
         ("gene", 71.25, "口袋揣着糖和面包，|随时补热量"),
         ("why", 80, "军方记录259人，|他自己写约500人"),
         ("order", 88.1, "1940年3月6日，|他被子弹打碎下颌"),
         ("card", 96.25, "记住这张卡"),
         ("end", 107.5, "问他怎么练的？|他只说：“练习。”")]
ENDB = 119
T = {k: qb(b) for k, b, s in LINES}; B = {k: b for k, b, s in LINES}
NAMES = [k for k, b, s in LINES]
SUBS = [[(-0.2 if i == 0 else qb(b)), (qb(LINES[i + 1][1]) if i + 1 < len(LINES) else 99), s, k] for i, (k, b, s) in enumerate(LINES)]
BIG2 = qb(40); DUR = qb(ENDB); HOOK_HIT = qb(0); HOOKCUT = T["q"]; HOOK_STOP = qb(5); SIL0 = qb(39)
def at(key, beats): return round(T[key] + beats * BEAT, 4)
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
CUTS = [T[n] for n in NAMES[1:]]
if __name__ == "__main__":
    for st, en, s, key in SUBS:
        en = min(en, DUR); print(f"{key:7s} {st:6.2f}-{en:6.2f} {en-max(st,0):4.2f}s need {need(s):4.2f} {'SHORT' if en-max(st,0) < need(s) else ''} {s}")
    print("BIG2", BIG2, "DUR", DUR, "BPM", round(BPM, 2))
