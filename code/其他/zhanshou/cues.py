# 《斩首：最后一道防线》 timeline (s). 96 BPM 4/4: beat 0.625, bar 2.5, 22 bars = 55 s
BPM = 96; BEAT = 60 / BPM; BAR = 4 * BEAT
DUR = 55.0
TSNAP = 37.5            # dead root snaps, soil collapses
TBREAK = 1e9; TRAIN = 1e9   # (engine hooks from 断桥, unused)
SHOTS = [("S01", 0, 5), ("S02", 5, 10), ("S03", 10, 15), ("S04", 15, 20), ("S05", 20, 25), ("S06", 25, 30),
         ("S07", 30, 35), ("S08", 35, 40), ("S09", 40, 45), ("S10", 45, 50), ("S11", 50, 55)]
# kind: C = on-screen caption (字幕), N = narration subtitle (旁白, no voice audio)
LINES = [("C", "斩首队，已潜入巢穴。", 0.3, 2.5),
         ("N", "敌人的斩首队，已经到了。", 2.5, 5.0),
         ("N", "正面的厮杀，掩护了另一支队伍。", 5.6, 9.4),
         ("N", "它们距蚁后，只剩最后一道防线。", 15.8, 19.6),
         ("C", "蚁后被截住！", 21.0, 23.6),
         ("N", "再晚一步，蚁后就走不了了。", 25.8, 29.4),
         ("N", "它的身后，是最后的退路。", 31.0, 34.4),
         ("N", "蚁后，逃出去了。", 40.8, 43.8),
         ("N", "但断须，再也没能走出来。", 50.0, 52.5),
         ("C", "斩首失败，战争仍在继续。", 52.5, 55.0)]
SUBS = [(s, a, b) for k, s, a, b in LINES]; CHAPS = []; TITLE = ("", 1e9, 1e9)
def shot_at(t):
    for s in SHOTS:
        if s[1] <= t < s[2]: return s
    return SHOTS[-1]
if __name__ == "__main__":
    import re
    for k, s, a, b in LINES:
        n = len(re.findall(r"[\u4e00-\u9fff]", s)); need = max(1.5, n / 4)
        print(f"{k} {a:5.1f}-{b:5.1f} {b-a:4.1f}s need {need:4.2f} {'SHORT' if b-a < need - 1e-6 else ''} {s}")
