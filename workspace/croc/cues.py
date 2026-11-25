# 《鳄鱼妈妈贴地偷听》 Nile crocodile head-tilt — Discover Wildlife (Sophie Ellis) 2026-11-04,
# https://www.discoverwildlife.com/animal-facts/reptiles/nile-crocodile-listening-for-offspring
# Camera trap: Sven Bourquin (Great Plains Foundation) & Vince Shacks (Wilderness), Duba area, Okavango Delta, Botswana.
# Researchers' interpretation, not a published paper. ISO studies: Soares 2002 Nature 417:241; Leitch & Catania 2012 (J Exp Biol).
# ADAPTIVE TIMELINE: subtitle >= max(1.5 s, chars/4 s)+extra; 112 BPM 4/4 from 0.4 s; BIG2 right after last PRE text;
# every POST segment padded to an EVEN number of beats so cuts land on beat 1 or 3 (structure rule R11).
import math, re
BPB = 4; BEAT = 60 / 112; BAR = BPB * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
PRE = [("hook", "鳄鱼妈妈耳朵贴地，|在偷听地底下？", 0.0),
       ("stay", "相机拍到：她歪着头，|一动不动好一会儿", 0.4),
       ("q", "地底下有什么？", 0.0)]
POST = [("reveal", "埋着她的蛋！|宝宝快出壳了", 0.6),
        ("call", "快出壳的小鳄鱼，|会在土里叫", 0.6),
        ("where", "地点：博茨瓦纳|奥卡万戈三角洲", 0.4),
        ("rule", "规矩不能坏：|下完蛋，守窝三个月", 0.6),
        ("guard", "这三个月很少离开，|河马、豹、鬣狗、巨蜥都防着", 0.6),
        ("tilt1", "平时她也歪头，|那是叼东西，又快又准", 0.4),
        ("tilt2", "这次歪着头不动，|耳孔贴平地面", 0.6),
        ("dig", "没过多久，|她就挖开了窝", 0.4),
        ("think", "研究者认为：|她在贴地听娃的叫声", 0.6),
        ("bumps", "她身上还有数千个|小鼓包：感觉器官", 0.4),
        ("drop", "2002年研究：|一滴水的涟漪都能察觉", 0.4),
        ("vib", "2012年发现：里面有|专感压力和振动的受体", 0.4),
        ("maybe", "研究者推测：|地下的动静，她也许能感觉到", 0.6),
        ("card", "记住这张卡", 3.4),
        ("water", "挖出来的小鳄鱼，|下一站：水里", 1.2),
        ("end", "凶是凶了点，|但当妈，不烧心", 3.6)]
T = {}; SUBS = []; k = 0
for i, (key, s, ex) in enumerate(PRE):
    st = -0.2 if i == 0 else qb(k)
    end_need = (0.0 if i == 0 else qb(k)) + need(s, ex)
    nb = max(1, math.ceil((end_need - G0) / BEAT - 1e-6)) - k
    T[key] = qb(k) if i else qb(0); SUBS.append([st, None, s, key]); k += nb
BIG2 = qb(k); K2 = k
NB = {}
for key, s, ex in POST:
    nb = math.ceil(need(s, ex) / BEAT - 1e-6); nb += nb % 2; NB[key] = nb
    T[key] = qb(k); SUBS.append([qb(k), None, s, key]); k += nb
DUR = qb(k)
for i in range(len(SUBS)): SUBS[i][1] = SUBS[i + 1][0] if i + 1 < len(SUBS) else 99
HOOK_HIT = qb(0); HOOKCUT = T["stay"]; HOOK_STOP = round(HOOKCUT - BEAT / 2, 4)
def at(key, beats): return round(T[key] + beats * BEAT, 4)
NAMES = [a for a, _, _ in PRE + POST]
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
CUTS = [HOOKCUT] + [T[n] for n in NAMES[2:] if n not in ("q", "tilt2", "think")] + [BIG2]
def bars(key): return (T[key] - BIG2) / BAR
if __name__ == "__main__":
    for st, en, s, key in SUBS: print(f"{key:7s} {st:6.2f}-{min(en,DUR):6.2f}  {min(en,DUR)-max(st,0):4.2f}s need {need(s):4.2f}  bar {(max(st,0)-BIG2)/BAR:6.2f}  {s}")
    print("BIG2", BIG2, "DUR", DUR, "bars after BIG2", (DUR - BIG2) / BAR)
