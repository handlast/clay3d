# 《耳屎是防虫墙》 — Ancalle et al. 2026, Soft Matter 22(41):6884-6897, doi:10.1039/d6sm00737f (pub 2026-10-28)
# Facts used (from abstract + D. Hu's Conversation piece 2026-10-27 + Science News 2026-11-04):
#  36 samples: pigs, sheep, dogs, cows, rabbits, humans; fire ants (Solenopsis invicta); beaker rim coated with earwax;
#  rough earwax: climbable with claws; smooth: ants fell immediately; ants' wet adhesive pads, pores absorb the droplets;
#  absorbs 2x its weight in water; earwax-coated tunnel -> wax sticks, ants groom furiously, still stuck after minutes;
#  ~60% dead skin cells; thin layer hardest; heaps = boulders ants climb; epithelial migration 8-10 weeks; HYPOTHESIS (lab ants only).
import math, re
BPB = 4; BEAT = 60 / 104; BAR = BPB * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
PRE = [("hook", "虫子想钻你耳朵？|先过耳屎这关", 0.0),
       ("q", "耳屎到底有啥用？", 0.0)]
POST = [("reveal", "答案：它可能是|一道防虫墙", 0.5),
        ("study", "美国佐治亚理工的团队|真拿蚂蚁做了实验", 0.4),
        ("samples", "收集了猪、羊、狗、牛、兔|和人的耳屎", 0.4),
        ("climb", "在杯口抹一圈耳屎，|让火蚁往上爬", 0.4),
        ("rough", "粗糙的耳屎：|蚂蚁用爪子勾着，慢慢爬", 0.4),
        ("smooth", "光滑的耳屎：|一上去就滑下来", 0.6),
        ("pad", "蚂蚁爬光滑面，|靠脚底湿湿的“吸盘”", 0.4),
        ("pore", "耳屎满是小孔，|把吸盘的水吸走了", 0.6),
        ("sponge", "它能吸下|自己两倍重的水", 0.4),
        ("tunnel", "钻进耳道模型的蚂蚁|浑身粘上耳屎", 0.4),
        ("groom", "停下来拼命清理，|几分钟都弄不干净", 0.6),
        ("both", "又滑又黏：|这就是耳屎的绝招", 0.4),
        ("skin", "耳屎大约六成|是死掉的皮肤细胞", 0.4),
        ("thin", "薄薄一层最难爬；|堆太厚，蚂蚁反而能爬过去", 0.4),
        ("belt", "耳道皮肤像传送带，|8到10周把旧耳屎推出去", 0.4),
        ("card", "记住这张卡", 8.2),
        ("dig", "所以别老掏：|医生普遍认为耳朵会自己清洁", 0.4),
        ("end", "耳屎：|你耳朵里的防虫保安", 3.4)]
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
HOOK_HIT = qb(0); HOOKCUT = T["q"]; HOOK_STOP = round(HOOKCUT - BEAT / 2, 4)
def at(key, beats): return round(T[key] + beats * BEAT, 4)
NAMES = [a for a, _, _ in PRE + POST]
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
CUTS = [HOOKCUT] + [T[n] for n in NAMES[2:] if n not in ("pore", "groom", "sponge")] + [BIG2]
def bars(key): return (T[key] - BIG2) / BAR
if __name__ == "__main__":
    for st, en, s, key in SUBS: print(f"{key:8s} {st:6.2f}-{min(en,DUR):6.2f}  {min(en,DUR)-max(st,0):4.2f}s need {need(s):4.2f}  bar {(max(st,0)-BIG2)/BAR:6.2f}  {s}")
    print("BIG2", BIG2, "DUR", DUR, "bars after BIG2", (DUR - BIG2) / BAR)
