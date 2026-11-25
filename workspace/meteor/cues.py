# 《火流星为什么先亮后轰》 — 2026-11-06 ~18:31 华北火流星。来源：央视新闻（环球网转载 2026-11-08）、北京日报 2026-11-07（李昕，北京天文馆）、
# 澎湃/北青 2026-11-06；American Meteor Society Fireball FAQ（声音约每分钟 20 km，音爆在火球后 1.5–4 分钟，需低于约 50 km 爆裂）。
# 事实：同一颗；亮度超过金星即火流星；每秒十几公里进大气；前方空气压缩成激波，几千摄氏度；发光高度一般 30–100 km，飞机约 10 km；
# 专家推算直径可能约 1 米；燃烧/解体/音爆在几十公里高空；网友称轰鸣约半分钟；绿光可能与镁、镍等元素有关；很可能有陨石落地（未证实）。
# MUSIC GRID cloned from muppet: 97.96 BPM, 0.4 s and 20.0 s on bar lines, silence beat 31.
import math, re
BPB = 4; BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
LINES = [("hook", 0, "火流星先亮，|过几分钟才“轰”"),
         ("q", 5, "11月6日，华北多地|看到同一颗火球"),
         ("who", 11.5, "它是一块太空石头，|专家推算约1米大"),
         ("sperm", 18, "每秒十几公里，|一头扎进大气层"),
         ("egg", 24, "前面的空气|根本来不及让开……"),
         ("reveal", 32, "被压成激波，|烧到几千度！"),
         ("how", 37, "发光处离地30到100公里，|飞机才10公里"),
         ("xray", 44, "光几乎一瞬就到，|声音1分钟只走约20公里"),
         ("swim", 51.5, "所以先看到火球，|1.5到4分钟后才听到轰"),
         ("gene", 58.5, "那抹绿光，可能来自|镁、镍等元素"),
         ("why", 64.5, "没烧完的碎块|落地就是陨石"),
         ("order", 70, "捡到疑似陨石？|记坐标、拍照、找天文机构"),
         ("card", 77, "记住这张卡"),
         ("end", 86, "口诀：先看光，|再听轰")]
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
