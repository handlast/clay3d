# 《超级士兵 No.03》 Audie L. Murphy — adaptive timeline (subs + VO edge-tts Yunjian -5%, never sped up).
# Big accents ONLY at 0 s (hook) and BIG2 (他却爬了上去). Phonk 133.3 BPM (BEAT 0.45), grid origin 0 s, reset at BIG2.
import math, re, json, os
from lines import LINES, PRE_KEYS, SCREEN
BPB = 4; BEAT = 0.45; BAR = BPB * BEAT; BPM = 60 / BEAT; TAIL = 0.2
_dir = os.path.dirname(os.path.abspath(__file__))
VDUR = json.load(open(os.path.join(_dir, "vox/durs.json")))
def nchars(s):
    s = s.replace("|", "")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s)); asc = len(re.findall(r"[A-Za-z0-9]", s))
    return cjk + 0.5 * asc
def need(s, extra=0.0): return max(1.5, nchars(s) / 4) + extra
BIG1 = 0.0
T = {}; SUBS = []; VOFF = {k: 0.1 for k, *_ in LINES}; VOFF["hook"] = 0.25
t = 0.0
for key, sub, vo, ex in LINES:
    if key == "big2": BIG2 = t
    T[key] = t; SUBS.append([t if t > 0 else -0.2, None, sub, key])
    L = max(need(sub + SCREEN.get(key, ''), ex), VDUR[key] + VOFF[key] + TAIL)
    t = round(t + math.ceil(L / BEAT - 1e-6) * BEAT, 4)
DUR = t
for i in range(len(SUBS)): SUBS[i][1] = SUBS[i + 1][0] if i + 1 < len(SUBS) else 99
SIL0 = BIG2 - 0.3
def at(key, beats): return round(T[key] + beats * BEAT, 4)
NAMES = [k for k, *_ in LINES]
SUBTXT = {k: s for k, s, *_ in LINES}; VOTXT = {k: v for k, s, v, e in LINES}
def nxt(key): i = NAMES.index(key); return T[NAMES[i + 1]] if i + 1 < len(NAMES) else DUR
def check():
    bad = []
    for st, en, s, key in SUBS:
        en = min(en, DUR); d = en - max(st, 0)
        if d < need(s + SCREEN.get(key, '')) - 1e-6 or d < VDUR[key] + VOFF[key] - 1e-6: bad.append((key, d, need(s), VDUR[key]))
    return bad
if __name__ == "__main__":
    for st, en, s, key in SUBS:
        en = min(en, DUR); d = en - max(st, 0)
        print(f"{key:8s} {max(st,0):6.2f}-{en:6.2f} {d:4.2f}s need {need(s + SCREEN.get(key, '')):4.2f} voice {VDUR[key]:4.2f}  {s}")
    print("BIG2", BIG2, "DUR", DUR, "frames", round(DUR * 30), "bad:", check())
# ---- shared beat events (film + music) ----
MG_BURSTS = [at("mg", b) for b in (1, 1.5, 2, 3, 3.5, 4, 5, 5.5, 6, 7)]
WAVER_BURSTS = [at("waver", b) for b in (0.5, 2.5, 4.5, 6.5, 8.5)]
WAVER_STEPS = [at("waver", b) for b in (1.5, 3.5, 5.5, 7.5, 9.5)]     # enemy steps back on the off-burst beats
HIT_T = at("hit", 2)                                                    # shell hits the M10
ARTY = [at("retreat", b) for b in (2, 4.5, 7)]
THREE_ARROWS = [at("three", b) for b in (1, 2.5, 4)]
AMMO_OUT = [at("hour", 1 + i * 0.75) for i in range(10)]
