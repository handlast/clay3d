# 《炎魔蟋蟀》 Dolichopoda balrogi — Journal of Orthoptera Research 2026 (Daily Galaxy 2026-11-02; Kalaentzis et al.)
# ADAPTIVE TIMELINE: every subtitle stays >= max(1.5 s, chars/4 s) (+extra for busy screens); grid = 104 BPM beats in 7/4 bars (4+3) from 0.4 s.
# Big hit 2 lands on the first bar line after the pre-reveal text + 1 silent beat. BGM (music.py) is generated from these cues.
import math, re
BPB = 7; BEAT = 60 / 104; BAR = BPB * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
PRE = [("hook", "它叫“炎魔”，|却是只蟋蟀", 0.0),
       ("island", "希腊有座小岛，|只有6公里长", 0.4),
       ("tunnel", "岛上唯一的“洞”，|是条25米深的人造隧道", 0.4),
       ("walls", "墙上爬满了蟋蟀", 0.3),
       ("dna", "一查长相和DNA……", 0.0)]
POST = [("reveal", "科学界从没见过的新物种！", 0.4),
        ("name", "名字来自《魔戒》里的炎魔", 0.4),
        ("real", "炎魔浑身是火，|它却完全无害", 0.4),
        ("legs", "棕色身体，|又长又弯的腿", 0.4),
        ("grip", "能牢牢抓住墙壁，|还能倒挂在顶上", 0.4),
        ("genus", "同属已有68种，|其中51种在希腊", 0.4),
        ("fragile", "这类蟋蟀常只住一个洞，|湿度一变就危险", 0.4),
        ("near", "新物种不只在雨林深海，|人造隧道里也有", 0.4),
        ("card", "记住这张牌", 3.0),
        ("end", "名字吓人，|其实是个乖宝宝", 3.5)]
T = {}; SUBS = []; k = 0
for i, (key, s, ex) in enumerate(PRE):
    st = -0.2 if i == 0 else qb(k)
    end_need = (0.0 if i == 0 else qb(k)) + need(s, ex)
    nb = max(1, math.ceil((end_need - G0) / BEAT - 1e-6)) - k
    T[key] = qb(k) if i else qb(0); SUBS.append([st, None, s, key]); k += nb
# (2026-11-03 user: no black-screen pause, no forced bar-line wait) big hit 2 follows the text directly
SIL0 = qb(k)
BIG2 = qb(k); K2 = k
for key, s, ex in POST:
    T[key] = qb(k); SUBS.append([qb(k), None, s, key]); k += math.ceil(need(s, ex) / BEAT - 1e-6)
DUR = qb(k)
for i in range(len(SUBS)): SUBS[i][1] = SUBS[i + 1][0] if i + 1 < len(SUBS) else 99
for i, sb in enumerate(SUBS):
    if sb[3] == PRE[-1][0]: sb[1] = SIL0
HOOK_HIT = qb(0); HOOK_STOP = qb(3.5); HOOKCUT = qb(4)
def at(key, beats): return round(T[key] + beats * BEAT, 4)
NAMES = [a for a, _, _ in PRE + POST]
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
SILENCES = []
CUTS = [HOOKCUT] + [T[n] for n in NAMES[2:] if n != "reveal"] + [BIG2]
if __name__ == "__main__":
    for st, en, s, key in SUBS: print(f"{key:7s} {st:6.2f}-{min(en,DUR):6.2f}  {min(en,DUR)-max(st,0):4.2f}s need {need(s):4.2f}  {s}")
    print("BIG2", BIG2, "SIL0", SIL0, "DUR", DUR)
