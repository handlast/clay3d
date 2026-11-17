# 《狐狸变温顺，脑子里少了“攻击开关”？》 — Klein JL, Shepeleva DV, Vladimirova AV, Kharlamova AV, Miller AD, Kukekova AV, Markenscoff-Papadimitriou E.
# Current Biology 36(21):R1216-R1217, 2026-11-02, doi:10.1016/j.cub.2026.09.020 (abstract read on cell.com); Cornell Chronicle 2026-11-02 (read); SciAm 2026-11-06 (excerpt)
# facts: Siberia late 1950s (SciAm: 1959); bred friendliest; after 6 generations pups interacted with humans; floppy ears, shorter snouts (Cornell), curly tails (SciAm)
# 9 brains: 3 tame, 3 bred aggressive, 3 wild; thin slices; fluorescent RNAscope; VMH at base of brain
# mice (prior work, optogenetics): activating ERa neurons in VMH -> immediately attack
# abstract: tame fewer ER-expressing neurons in VMHvl than aggressive foxes; reduction specific to subtype linked to aggressive states in mice; "candidate" cell type
import math, re
BPB = 4; BEAT = 60 / 104; BAR = BPB * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
PRE = [("hook", "一代代驯出来的温顺狐狸，|脑子里少了一类细胞", 0.0),
       ("q", "少的是哪一类？", 0.0)]
POST = [("reveal", "管“攻击”的那一类", 0.5),
        ("y1959", "1959年起，|西伯利亚的狐狸养殖场", 0.4),
        ("pick", "科学家只挑最亲人的狐狸|配对繁殖", 0.4),
        ("six", "才过了6代，|小狐狸就会主动跟人互动", 0.6),
        ("look", "长相也跟着变：|耳朵耷拉、嘴变短、尾巴卷", 0.6),
        ("mean", "另一组专挑最凶的配，|成了“凶狐狸”", 0.4),
        ("nine", "康奈尔团队拿到9颗狐狸脑：|温顺、凶、野生各3颗", 0.6),
        ("slice", "切成极薄的片，|再给细胞打上荧光标记", 0.4),
        ("where", "盯住脑底部的一小块：|下丘脑腹内侧", 0.4),
        ("mouse", "以前在小鼠身上，用光点亮这里的|雌激素受体α神经元", 0.4),
        ("attack", "小鼠会立刻去攻击别的小鼠", 0.6),
        ("result", "结果：温顺狐狸的这类神经元|比凶狐狸少", 0.8),
        ("sub", "少的正是小鼠里|跟攻击状态有关的那一亚型", 0.6),
        ("caution", "不过只有9颗脑，只能说相关，|还没证明就是原因", 0.6),
        ("next", "下一步：弄清驯化|为什么会改变这里", 0.4),
        ("card", "记住这张卡", 8.4),
        ("end", "温顺狐狸口诀：|攻击开关，少装几个", 3.4)]
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
CUTS = [HOOKCUT] + [T[n] for n in NAMES[2:] if n not in ("pick", "six", "look", "slice", "attack", "sub", "next")] + [BIG2]
def bars(key): return (T[key] - BIG2) / BAR
if __name__ == "__main__":
    for st, en, s, key in SUBS: print(f"{key:8s} {st:6.2f}-{min(en,DUR):6.2f}  {min(en,DUR)-max(st,0):4.2f}s need {need(s):4.2f}  bar {(max(st,0)-BIG2)/BAR:6.2f}  {s}")
    print("BIG2", BIG2, "DUR", DUR, "bars after BIG2", (DUR - BIG2) / BAR)
