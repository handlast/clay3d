# 《树也有肌肉》 tension wood — Caulus et al. 2026 New Phytologist (INRAE press release 2026-09-02)
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
PRE = [("hook", "树也有“肌肉”？|还会自己掰直腰", 0.0),
       ("lay", "小杨树被放倒，|十来天就弯回朝上", 0.4),
       ("pull", "上侧长出“张力木”，|像肌肉一样往上拉", 0.4),
       ("q", "可弯了的腰，|怎么再变直？", 0.3),
       ("spin", "放进旋转发光球：|分不清上下和光", 0.4),
       ("left", "只剩一种感觉：|自己弯成啥样", 0.0)]
POST = [("reveal", "几周后，它自己变直了！", 0.4),
        ("flip", "上侧停止长张力木，|下侧长出一模一样的", 0.4),
        ("anta", "两边拔河，|就像我们的一对拮抗肌", 0.4),
        ("term", "这叫“本体感觉”：|知道自己身体摆成啥姿势", 0.4),
        ("spring", "不是被动弹回去，|切片里有新长出的木头", 0.4),
        ("use", "这本事帮树|扛过风暴和滑坡", 0.3),
        ("crop", "将来也许能帮庄稼|少倒伏", 0.3),
        ("card", "记住这个比喻", 2.8),
        ("end", "树一直在悄悄|调整自己的姿势", 3.5)]
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
    if sb[3] == PRE[-1][0]: sb[1] = SIL0
HOOK_HIT = qb(0); HOOK_STOP = qb(3.5); HOOKCUT = qb(4)
def at(key, beats): return round(T[key] + beats * BEAT, 4)
NAMES = [a for a, _, _ in PRE + POST]
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
SILENCES = [(SIL0, BIG2)]
CUTS = [HOOKCUT] + [T[n] for n in NAMES[2:] if n != "reveal"] + [BIG2]
if __name__ == "__main__":
    for st, en, s, key in SUBS: print(f"{key:7s} {st:6.2f}-{min(en,DUR):6.2f}  {min(en,DUR)-max(st,0):4.2f}s need {need(s):4.2f}  {s}")
    print("BIG2", BIG2, "SIL0", SIL0, "DUR", DUR)
