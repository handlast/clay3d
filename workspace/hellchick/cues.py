# 《地狱鸡：恐龙里的水果党》 Infernogallus jamesi — Funston et al. 2026, Nature Communications (Reuters 2026-10-27)
# ADAPTIVE TIMELINE: every subtitle stays >= max(1.5 s, chars/4 s) (+extra for busy screens); grid = 120 BPM beats from 0.4 s.
# Big hit 2 lands on the first bar line after the pre-reveal text + 1 silent beat. BGM (music.py) is generated from these cues.
import math, re
BEAT = 0.5; BAR = 4 * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
PRE = [("hook", "6600 万年前，|有种恐龙爱吃水果", 0.0),
       ("name", "它叫“地狱鸡”", 0.5),
       ("site", "化石出自美国|“地狱溪”地层", 0.4),
       ("size", "火鸡那么大，|约 11 公斤", 0.4),
       ("beak", "没有牙，|长着鹦鹉似的喙", 0.3),
       ("neigh", "邻居是霸王龙", 0.4),
       ("menu", "恐龙吃肉、吃草，|吃水果却从没证据", 0.4),
       ("jaw", "直到看清它的下巴——", 0.0)]
POST = [("reveal", "第一只确认吃水果的恐龙", 0.4),
        ("f1", "一：前后嚼的颌部肌肉", 0.5),
        ("f2", "二：能往前滑的下巴关节", 0.5),
        ("f3", "三：喙上的脊和沟，|专门捣烂软果肉", 0.4),
        ("rare", "鹦鹉、海龟只有一部分，|三样全有的动物，今天没有", 0.5),
        ("stone", "多数吃素的兽脚类|靠吞石头磨碎食物，|它这一支自己嚼", 0.4),
        ("fruit", "菜单可能有浆果，|和桃、樱桃这类核果", 0.4),
        ("seed", "也许还帮植物传播种子|（这点仍需更多证据）", 0.3),
        ("card", "记住这三件工具", 2.5),
        ("end", "恐龙的菜单，|比想象的丰富", 3.5)]
T = {}; SUBS = []; k = 0
for i, (key, s, ex) in enumerate(PRE):
    st = -0.2 if i == 0 else qb(k)
    end_need = (0.0 if i == 0 else qb(k)) + need(s, ex)
    nb = max(1, math.ceil((end_need - G0) / BEAT - 1e-6)) - k
    T[key] = qb(k) if i else qb(0); SUBS.append([st, None, s, key]); k += nb
k += 1                         # one silent beat
k = math.ceil(k / 4) * 4       # land big hit 2 on a bar line
SIL0 = qb(k - 1) if qb(k) - qb(k - 1) >= 0.5 else qb(k) - 0.5
BIG2 = qb(k); K2 = k
for key, s, ex in POST:
    T[key] = qb(k); SUBS.append([qb(k), None, s, key]); k += math.ceil(need(s, ex) / BEAT - 1e-6)
DUR = qb(k)
for i in range(len(SUBS)): SUBS[i][1] = SUBS[i + 1][0] if i + 1 < len(SUBS) else 99
for i, sb in enumerate(SUBS):
    if sb[3] == "jaw": sb[1] = SIL0
HOOK_HIT = qb(0); HOOK_STOP = qb(3.5); HOOKCUT = qb(4)
def at(key, beats): return round(T[key] + beats * BEAT, 4)
NAMES = [a for a, _, _ in PRE + POST]
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
SILENCES = [(SIL0, BIG2)]
CUTS = [HOOKCUT] + [T[n] for n in NAMES[2:] if n != "reveal"] + [BIG2]
if __name__ == "__main__":
    for st, en, s, key in SUBS: print(f"{key:7s} {st:6.2f}-{min(en,DUR):6.2f}  {min(en,DUR)-max(st,0):4.2f}s need {need(s):4.2f}  {s}")
    print("BIG2", BIG2, "SIL0", SIL0, "DUR", DUR)
