# 《章鱼越狱三步法》 — Xin W et al. 2026, J Exp Biol, doi:10.1242/jeb.252825 (pub 2026-11-05); Science News 2026-11-05 (N. Bradford)
# 3 O. vulgaris + 4 O. maya; eye-to-eye distance = proxy for rigid cartilage around brain; acrylic boxes w/ holes slightly smaller/larger.
# wider: 3 steps (1-2 arms, a couple more, outside arms push on box & yank head + rest through at once; few seconds)
# narrower (common): 4th step: all arms first, then squeeze head + mantle. Maya: narrower hole -> usually ignored, didn't attempt.
# habitat reason = Kuba's suggestion ("could stem from"). soft robots: W. Xin (NUS) hope; current hole robots tend snake-shaped.
import math, re
BPB = 4; BEAT = 60 / 112; BAR = BPB * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
PRE = [("hook", "章鱼越狱，|只要三步？", 0.0),
       ("q", "它到底怎么挤出去的？", 0.0)]
POST = [("reveal", "答案：先出腕，再出头，|有固定套路", 0.5),
        ("soft", "章鱼几乎全是软肌肉，|但也有硬的地方", 0.4),
        ("brain", "最硬的：|包住大脑的软骨", 0.4),
        ("eyes", "科学家用两眼间距|估算这块软骨有多宽", 0.4),
        ("box", "再做带孔的亚克力盒：|孔比两眼间距略大或略小", 0.4),
        ("who", "测试了3只普通章鱼|和4只玛雅章鱼", 0.4),
        ("big", "孔比两眼间距宽：|三步走", 0.4),
        ("s1", "第一步：|先伸出一两条腕", 0.6),
        ("s2", "第二步：|再穿过几条腕", 0.6),
        ("s3", "第三步：外面的腕撑住盒子，|把头和剩下的腕一把拽出", 0.8),
        ("fast", "整个过程只要几秒", 0.4),
        ("small", "孔比两眼间距窄：|加一步", 0.4),
        ("s4a", "先把所有腕|全部塞出去", 0.6),
        ("s4b", "最后硬挤|头和外套膜", 0.8),
        ("maya", "玛雅章鱼呢？|遇到窄孔，通常理都不理", 0.6),
        ("why", "研究者推测：它们住沙地岩石区，|不太需要钻窄缝", 0.4),
        ("robot", "团队希望由此造出|能变形钻小孔的软体机器人", 0.4),
        ("card", "记住这张卡", 8.4),
        ("end", "章鱼越狱口诀：|腕先出，头最后", 3.4)]
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
CUTS = [HOOKCUT] + [T[n] for n in NAMES[2:] if n not in ("s1", "s2", "s3", "fast", "s4a", "s4b")] + [BIG2]
def bars(key): return (T[key] - BIG2) / BAR
if __name__ == "__main__":
    for st, en, s, key in SUBS: print(f"{key:8s} {st:6.2f}-{min(en,DUR):6.2f}  {min(en,DUR)-max(st,0):4.2f}s need {need(s):4.2f}  bar {(max(st,0)-BIG2)/BAR:6.2f}  {s}")
    print("BIG2", BIG2, "DUR", DUR, "bars after BIG2", (DUR - BIG2) / BAR)
