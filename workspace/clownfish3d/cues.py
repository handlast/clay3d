# 《动物打工人 No.03》Noble et al. 2026 R. Soc. Open Sci.
# ScienceAlert 2026-11-14. ADAPTIVE TIMELINE driven by subtitles AND voice-over (edge-tts Yunjian −5%, never sped up):
#   each line lasts ceil(max(need(sub)+extra, voice+0.1+TAIL) / BEAT) beats; voice starts at line start + 0.1 s.
# Big hit 1 = 3.0 s (bleaching reveal); 0–3 s hook: anemone fades to white.
# Big hit 2 (BIG2) follows the previous line directly (no silent beat, no bar rounding); music resets bar origin there.
import math, re, json, os
from lines import LINES, PRE_KEYS
BPB = 4; BEAT = 0.5; BAR = BPB * BEAT; BPM = 60 / BEAT; G0 = 3.0; TAIL = 0.25
_dir = os.path.dirname(os.path.abspath(__file__))
VDUR = json.load(open(os.path.join(_dir, "vox/durs.json")))
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
BIG1 = 3.0; HOOK_HIT = 0.0
COUNT = []
T = {"hook": 0.0}; SUBS = [[-0.2, None, LINES[0][1], "hook"]]; VOFF = {k: 0.1 for k, *_ in LINES}
t = BIG1
for key, sub, vo, ex in LINES[1:]:
    if key == "big2": BIG2 = t
    T[key] = t; SUBS.append([t, None, sub, key])
    L = max(need(sub, ex), VDUR[key] + 0.1 + TAIL)
    t = round(t + math.ceil(L / BEAT - 1e-6) * BEAT, 4)
DUR = t
for i in range(len(SUBS)): SUBS[i][1] = SUBS[i + 1][0] if i + 1 < len(SUBS) else 99
FOUND = BIG1; SIL0 = BIG2 - 0.3
def qb(k): return round(G0 + k * BEAT, 4)
def at(key, beats): return round(T[key] + beats * BEAT, 4)
NAMES = [k for k, *_ in LINES]
SUBTXT = {k: s for k, s, *_ in LINES}; VOTXT = {k: v for k, s, v, e in LINES}
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
CUTS = [T[n] for n in NAMES[2:]]
def check():
    bad = []
    for st, en, s, key in SUBS:
        en = min(en, DUR); d = en - max(st, 0)
        if d < need(s) - 1e-6 or d < VDUR[key] + 0.1 - 1e-6: bad.append((key, d, need(s), VDUR[key]))
    return bad
if __name__ == "__main__":
    for st, en, s, key in SUBS:
        en = min(en, DUR); d = en - max(st, 0)
        print(f"{key:7s} {st:6.2f}-{en:6.2f} {d:4.2f}s need {need(s):4.2f} voice {VDUR[key]:4.2f}  {s}")
    print("BIG1", BIG1, "BIG2", BIG2, "DUR", DUR, "frames", round(DUR * 30), "bad:", check())
