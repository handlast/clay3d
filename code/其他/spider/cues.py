# 《蜘蛛睡觉也会做梦抽腿？》怪奇新发现, 47 s  (Geiger & Rößler 2026, PNAS, doi 10.1073/pnas.2618030123)
BEAT = 0.6125; BAR = 2.45; G0 = 0.4; DUR = 47.0          # 98 BPM; 0.4 and 20.0 both land on a downbeat (8 bars apart)
HOOK_HIT = 0.4; HOOK_END = 3.5
LAB = 3.5; LAB_HIT = 3.9; CAMS = [4.9, 5.5]; NAME_HIT = 6.1
BRUSH = 7.2; LEGS = [7.65 + i * 0.306 for i in range(8)]; TOOTH_HIT = 10.3
HAM = 11.0; SILK_HIT = 11.4; FLIP_HIT = 12.6
CHECK = 14.0; TICKS = [14.4, 15.0, 15.6, 16.2, 16.8]
DEEP = 17.4; RISERS = [(18.4, 19.5)]
SIL0 = 19.5; REM_HIT = 20.0
EYE = 23.5; EYE_HIT = 23.9
SOUND = 27.0; HONK = [27.5, 28.1, 28.7]; DEAF_HIT = 29.4
REB = 30.5; POKES = [31.0, 31.4, 31.8]; NIGHT2 = 32.4; LONG_HIT = 33.2
PROOF = 34.5; PROOF_HIT = 34.9; STAGE_HIT = 36.2
DREAM = 37.5; DREAM_HIT = 37.9; Q_HIT = 39.6
OLD = 41.0; OLD_HIT = 41.4; OLD2_HIT = 42.7
OUTRO = 44.0; BUBS = [44.4, 45.2, 45.9]
SILENCES = [(19.5, 20.0)]
HITS = [HOOK_HIT, LAB_HIT] + CAMS + [NAME_HIT] + LEGS + [TOOTH_HIT, SILK_HIT, FLIP_HIT] + TICKS + [REM_HIT, EYE_HIT] + HONK + [DEAF_HIT] + POKES + [LONG_HIT, PROOF_HIT, STAGE_HIT, DREAM_HIT, Q_HIT, OLD_HIT, OLD2_HIT, OUTRO]
SUBS = [(0.0, 3.5, "蜘蛛睡着以后，腿会一抽一抽的"),
        (3.5, 7.2, "德国波恩大学，盯着一群跳蛛过了很多个夜晚"),
        (7.2, 11.0, "睡前，它先把 8 条腿挨个擦一遍，像刷牙"),
        (11.0, 14.0, "再爬上丝做的小吊床，倒挂着睡"),
        (14.0, 17.4, "科学家用判断睡眠的 5 条标准，一条条去验"),
        (17.4, 19.5, "睡熟了，身体慢慢耷拉下来……"),
        (20.0, 23.5, "突然，它进入像 REM 一样的“快速眼动”睡眠"),
        (23.5, 27.0, "腿蜷起来抽动，眼睛里的视网膜管左右乱转"),
        (27.0, 30.5, "这时放声音吵它，它也更难被叫醒"),
        (30.5, 34.5, "前一晚被吵醒，第二晚它会多睡，把觉补回来"),
        (34.5, 37.5, "5 条全过：蜘蛛真的会睡觉，还分两个阶段"),
        (37.5, 41.0, "那它是在做梦吗？研究者说：还不知道"),
        (41.0, 44.0, "蜘蛛这一支非常古老，睡觉这件事，可能比我们想的还古老")]
