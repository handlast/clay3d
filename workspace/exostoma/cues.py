# 《冲不走的鱼》 Exostoma nasibarbatum — Torisha & Shangningam 2026, J. Nat. Hist. 60(45-48): 2251-2263, doi 10.1080/00222933.2026.2737351
# (abstract read on tandfonline; details: Assam Tribune 2026-11-01, ThePrint 2026-11-03)
# ADAPTIVE TIMELINE: each subtitle >= max(1.5 s, chars/4 s)+extra; grid = 108 BPM 4/4 from 0.4 s; BIG2 follows the last pre text directly.
import math, re
BPB = 4; BEAT = 60 / 108; BAR = BPB * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
PRE = [("hook", "山溪激流里，|小鱼一条条被冲走", 0.0),
       ("stay", "只有它，|死死贴在石头上", 0.4),
       ("q", "靠的是吸盘吗？", 0.0)]
POST = [("reveal", "不是吸盘！|是鳍上一道道粘附纹", 0.4),
        ("flat", "头和身体压得扁扁的，|水流推力变小", 0.4),
        ("fins", "一对对大鳍摊开，|像防滑垫按住石头", 0.4),
        ("barbel", "嘴边的须也是扁的，|帮它贴住石头", 0.4),
        ("catfish", "对了，它不是泥鳅，|是一种山溪鲇鱼", 0.4),
        ("nameq", "它最特别的地方，|在鼻子上", 0.2),
        ("nose", "鼻孔边一根长须，|一直伸过眼睛后缘", 0.4),
        ("latin", "学名 nasibarbatum，|就是“鼻子长胡子”", 0.4),
        ("sense", "须上有感觉细胞，|能感知触碰和气味", 0.4),
        ("murky", "水流乱、看不清时，|靠它探路找吃的", 0.4),
        ("where", "发现地：印度曼尼普尔，|靠近缅甸边境的山溪", 0.4),
        ("rare", "这类小鲇鱼很少见，|藏在偏远的山溪里", 0.4),
        ("ident", "和二十多种亲戚比，|认出它靠三处细节", 0.6),
        ("card", "记住这张牌", 3.0),
        ("end", "冲不走的秘密，|全长在身上", 3.0)]
T = {}; SUBS = []; k = 0
for i, (key, s, ex) in enumerate(PRE):
    st = -0.2 if i == 0 else qb(k)
    end_need = (0.0 if i == 0 else qb(k)) + need(s, ex)
    nb = max(1, math.ceil((end_need - G0) / BEAT - 1e-6)) - k
    T[key] = qb(k) if i else qb(0); SUBS.append([st, None, s, key]); k += nb
BIG2 = qb(k); K2 = k
# v2 (2026-11-04): every POST segment padded to an even number of beats so each cut lands on beat 1 or 3 of the music grid
NB = dict(reveal=8, flat=8, fins=8, barbel=8, catfish=8, nameq=6, nose=8, latin=8, sense=8, murky=8, where=10, rare=8, ident=10, card=10, end=16)
for key, s, ex in POST:
    nb = NB[key]; assert nb >= math.ceil(need(s, ex) / BEAT - 1e-6), key
    T[key] = qb(k); SUBS.append([qb(k), None, s, key]); k += nb
DUR = qb(k)
for i in range(len(SUBS)): SUBS[i][1] = SUBS[i + 1][0] if i + 1 < len(SUBS) else 99
HOOK_HIT = qb(0); HOOKCUT = T["stay"]; HOOK_STOP = round(HOOKCUT - BEAT / 2, 4)
def at(key, beats): return round(T[key] + beats * BEAT, 4)
NAMES = [a for a, _, _ in PRE + POST]
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
CUTS = [HOOKCUT] + [T[n] for n in NAMES[2:] if n not in ("q", "murky")] + [BIG2]
if __name__ == "__main__":
    for st, en, s, key in SUBS: print(f"{key:7s} {st:6.2f}-{min(en,DUR):6.2f}  {min(en,DUR)-max(st,0):4.2f}s need {need(s):4.2f}  {s}")
    print("BIG2", BIG2, "DUR", DUR, "HOOKCUT", HOOKCUT)
