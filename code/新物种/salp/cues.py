# 《这只海樽只住在深海？》 adaptive timeline (seconds), shared by film + music. NO voice: each line lasts
# ceil(need(sub)+extra / BEAT) beats, need = max(1.5 s, chars/4). BIG1 = 0 s; BIG2 follows the previous line directly.
import math, re, os
from lines import LINES, PRE_KEYS
BPB = 4; BEAT = 0.5; BAR = BPB * BEAT; BPM = 60 / BEAT; G0 = 0.0
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
BIG1 = 0.0
T = {}; SUBS = []
t = 0.0
for key, sub, ex in LINES:
    if key == "big2": BIG2 = t
    T[key] = t; SUBS.append([t if t > 0 else -0.2, None, sub, key])
    t = round(t + math.ceil(need(sub, ex) / BEAT - 1e-6) * BEAT, 4)
DUR = t
for i in range(len(SUBS)): SUBS[i][1] = SUBS[i + 1][0] if i + 1 < len(SUBS) else 99
SIL0 = BIG2 - 0.3
def at(key, beats): return round(T[key] + beats * BEAT, 4)
NAMES = [k for k, *_ in LINES]
SUBTXT = {k: s for k, s, e in LINES}
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
def check():
    bad = []
    for st, en, s, key in SUBS:
        en = min(en, DUR); d = en - max(st, 0)
        if d < need(s) - 1e-6: bad.append((key, d, need(s)))
    return bad
def srt(path):
    f = lambda x: "%02d:%02d:%02d,%03d" % (x // 3600, x // 60 % 60, int(x) % 60, round((x - int(x)) * 1000))
    out = []
    for i, (st, en, s, key) in enumerate(SUBS):
        out.append(f"{i+1}\n{f(max(st,0))} --> {f(min(en,DUR))}\n{s.replace('|','')}\n")
    open(path, "w").write("\n".join(out))
if __name__ == "__main__":
    for st, en, s, key in SUBS:
        en = min(en, DUR); d = en - max(st, 0)
        print(f"{key:7s} {st:6.2f}-{en:6.2f} {d:4.2f}s need {need(s):4.2f}  {s}")
    print("BIG1", BIG1, "BIG2", BIG2, "DUR", DUR, "frames", round(DUR * 30), "bad:", check())
