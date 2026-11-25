# 《第一只下海的两栖动物》 Gerrothorax maritimus — Nature Ecology & Evolution 2026 (UC Davis news 2026-11-02, Motani)
# ADAPTIVE TIMELINE: every subtitle stays >= max(1.5 s, chars/4 s) (+extra for busy screens); grid = 112 BPM beats in 7/4 bars (4+3) from 0.4 s.
# Big hit 2 lands on the first bar line after the pre-reveal text + 1 silent beat. BGM (music.py) is generated from these cues.
import math, re
BPB = 7; BEAT = 60 / 112; BAR = BPB * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
PRE = [("hook", "两栖动物不能下海？|它偏偏下了", 0.0),
       ("skin", "青蛙的皮又薄又透，|一进海水就脱水", 0.4),
       ("count", "8000多种两栖动物，|没一种住在海里", 0.4),
       ("find", "贵州挖出两具|2.37亿年前的骨架", 0.4),
       ("q", "它凭什么能下海？", 0.0)]
POST = [("reveal", "它穿了一身骨头盔甲！", 0.4),
        ("armor", "推测：盔甲挡住皮肤，|改用嘴喝海水", 0.4),
        ("gill", "再用鳃|把盐滤出去", 0.4),
        ("body", "身长近1米，|扁得像个大圆盘", 0.4),
        ("suck", "趴在海底等猎物，|张嘴一吸就吞下", 0.4),
        ("proof", "怎么知道它住海里？|连手指骨都还在", 0.4),
        ("death", "尸体没漂远，|说明它就死在家门口", 0.3),
        ("sr", "骨头里的锶同位素，|和当年的海水对得上", 0.4),
        ("card", "记住这张牌", 3.0),
        ("end", "海里第一只两栖动物，|化石来自贵州", 3.5)]
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
