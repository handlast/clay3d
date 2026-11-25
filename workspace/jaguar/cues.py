# 《狐狸变温顺，脑子里少了“攻击开关”？》 — Klein JL, Shepeleva DV, Vladimirova AV, Kharlamova AV, Miller AD, Kukekova AV, Markenscoff-Papadimitriou E.
# Current Biology 36(21):R1216-R1217, 2026-11-02, doi:10.1016/j.cub.2026.09.020 (abstract read on cell.com); Cornell Chronicle 2026-11-02 (read); SciAm 2026-11-06 (excerpt)
# facts: Siberia late 1950s (SciAm: 1959); bred friendliest; after 6 generations pups interacted with humans; floppy ears, shorter snouts (Cornell), curly tails (SciAm)
# 9 brains: 3 tame, 3 bred aggressive, 3 wild; thin slices; fluorescent RNAscope; VMH at base of brain
# mice (prior work, optogenetics): activating ERa neurons in VMH -> immediately attack
# abstract: tame fewer ER-expressing neurons in VMHvl than aggressive foxes; reduction specific to subtype linked to aggressive states in mice; "candidate" cell type
import math, re
BPB = 4; BEAT = 60 / 108; BAR = BPB * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
PRE = [("hook", "两家美洲豹狭路相逢：|老吴——！", 0.2),
       ("q", "下一秒，要开打了吗？", 0.0)]
POST = [("reveal", "没有！翻肚皮，互相舔毛", 0.5),
        ("solo", "都说美洲豹是独行侠", 0.3),
        ("team", "巴西科学家沿河蹲守13年", 0.4),
        ("ids", "认出459只：靠斑点认豹", 0.5),
        ("events", "拍到167次社交，69只参与", 0.3),
        ("pie", "真动手的只占24.5%", 0.7),
        ("friendly", "更多是一起吃、睡、|打猎、舔毛", 0.5),
        ("kin", "友好互动近68%在亲戚间", 0.5),
        ("stranger", "打架的多是关系不明的", 0.3),
        ("meme", "亲戚面前哈基米，|陌生豹前才老吴", 0.5),
        ("net", "13个小圈子，|靠少数几只“社牛”连起来", 0.4),
        ("cons", "少了关键社牛，|整张网都受影响", 0.4),
        ("tiger", "老虎也被拍到：|虎爸来看娃", 0.5),
        ("tiger2", "还有母虎照顾别家的崽", 0.4),
        ("caution", "老虎是纪录片拍的个例，|美洲豹是13年数据", 0.3),
        ("card", "记住这张卡", 6.6),
        ("end", "口诀：亲戚翻肚皮，|陌生才老吴", 2.2)]
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
CUTS = [HOOKCUT] + [T[n] for n in NAMES[2:] if n not in ("tiger2", "stranger", "friendly")] + [BIG2]
def bars(key): return (T[key] - BIG2) / BAR
if __name__ == "__main__":
    for st, en, s, key in SUBS: print(f"{key:8s} {st:6.2f}-{min(en,DUR):6.2f}  {min(en,DUR)-max(st,0):4.2f}s need {need(s):4.2f}  bar {(max(st,0)-BIG2)/BAR:6.2f}  {s}")
    print("BIG2", BIG2, "DUR", DUR, "bars after BIG2", (DUR - BIG2) / BAR)
