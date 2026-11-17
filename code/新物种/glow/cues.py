# 《戳一下就闪绿光》Corallizoanthus aureus — Kise et al. 2025, Royal Society Open Science 12:250890, doi:10.1098/rsos.250890
# 385 m, NW off Minamidaito Is.; polyps on Pleurocorallium inutile at karst-cave entrances; blinking green 515.4 nm on pinch/KCl; in situ blink
# propagating from stimulus; first report of bioluminescence inside a deep-sea cave; no symbiotic bacteria seen in histology;
# 'burglar alarm' (Burkenroad 1943) = HYPOTHESIS. WoRMS Top Ten Marine Species of 2025 (U-Ryukyu 2026-04-06).
# ADAPTIVE TIMELINE (same rules as croc): subtitle >= max(1.5 s, chars/4)+extra; 100 BPM 4/4 from 0.4 s; BIG2 right after last PRE text.
import math, re
BPB = 4; BEAT = 60 / 100; BAR = BPB * BEAT; G0 = 0.4; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
PRE = [("hook", "戳一下，它就|闪绿光报警？", 0.0),
       ("deep", "385米深，|海底洞穴里的小家伙", 0.2),
       ("q", "它为什么要发光？", 0.0)]
POST = [("reveal", "学名意思是“金色的”：|一身亮黄的小触手", 0.5),
        ("notcoral", "它不是珊瑚，|是海葵的亲戚", 0.4),
        ("host", "专门长在红珊瑚上，|爬满枝杈", 0.4),
        ("size", "一个才几毫米高，|24到26根触手", 0.4),
        ("rov", "洞里太窄：|大机器人派出小机器人", 0.4),
        ("poke", "小机器人碰它一下——", 0.2),
        ("flash", "啪！一闪一闪的绿光", 0.6),
        ("spread", "光从碰到的地方|往外传开", 0.4),
        ("first", "在深海洞穴里拍到生物发光，|这是首次记录", 0.4),
        ("lab", "带回实验室：|镊子夹、滴氯化钾，都会亮", 0.4),
        ("nm", "峰值515纳米：|标准的绿光", 0.4),
        ("self", "是它自己在发光：|切片里没看到共生细菌", 0.4),
        ("why", "为啥要发光？|论文给了个猜想", 0.2),
        ("alarm", "“防盗警报”：|光把更大的捕食者引过来", 0.6),
        ("eat", "来偷吃的家伙，|反被大鱼盯上", 0.6),
        ("maybe", "注意：这还只是猜想，|没被证实", 0.4),
        ("card", "记住这张卡", 3.4),
        ("top10", "它还入选了|2025年度十大海洋新物种", 0.6),
        ("end", "所以别乱戳它：|它会报警！", 3.4)]
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
HOOK_HIT = qb(0); HOOKCUT = T["deep"]; HOOK_STOP = round(HOOKCUT - BEAT / 2, 4)
def at(key, beats): return round(T[key] + beats * BEAT, 4)
NAMES = [a for a, _, _ in PRE + POST]
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
CUTS = [HOOKCUT] + [T[n] for n in NAMES[2:] if n not in ("q", "flash", "spread", "eat")] + [BIG2]
def bars(key): return (T[key] - BIG2) / BAR
if __name__ == "__main__":
    for st, en, s, key in SUBS: print(f"{key:8s} {st:6.2f}-{min(en,DUR):6.2f}  {min(en,DUR)-max(st,0):4.2f}s need {need(s):4.2f}  bar {(max(st,0)-BIG2)/BAR:6.2f}  {s}")
    print("BIG2", BIG2, "DUR", DUR, "bars after BIG2", (DUR - BIG2) / BAR)
