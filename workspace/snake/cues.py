# 《蛇没有轮子，为什么能滚着逃命？》Vibe 知识大赏, ~46 s
# Kojima Y. et al. (2026) Locomotor kinematics and head stabilization in rolling snakes. Curr. Biol. 36(20): R1061. DOI 10.1016/j.cub.2026.08.057
# Grid: 0.4 s and 20.0 s are both bar lines -> 13 bars of 4/4 + one 5/4 bar (riser/silence bar) = 57 beats in 19.6 s -> 174.49 BPM (DnB).
BEAT = 19.6 / 57; BAR = 4 * BEAT; S16 = BEAT / 4; G0 = 0.4; G1 = 20.0; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)          # beat k before the drop
def qa(k): return round(G1 + k * BEAT, 4)          # beat k after 20.0
DUR = qa(76)                                        # 46.13 s
# ---- part 1 ----
HOOK_HIT = qb(0); CURL = qb(0); BRAKE = round(G0 + 27 * S16, 4); HOOK_END = qb(9)
CMP = qb(9); CRAWL_TICKS = [qb(10 + 2 * i) for i in range(5)]; GAUGE = qb(11); X4 = qb(15)
NUM = qb(20); BEEP1 = qb(21); COUNT = (qb(22), qb(27)); BEEP2 = qb(27); NUM_TAG = qb(28)
DIZ = qb(32); AXLE_TAG = qb(33); SPIN = qb(36.5); STARS = [qb(37), qb(39), qb(41)]; DIZ_TAG = qb(40)
Q = qb(44); HEADZ = qb(45); QMARK = qb(48); RISERS = [(qb(50), 19.5)]
SIL0 = 19.5; BIG = G1
# ---- part 2 ----
REVEAL = BIG; LEVEL = qa(1.5)
GYRO = qa(6); GYRO_HIT = qa(7); HTAG = qa(9)
FAST = qa(12); SPEEDUP = (qa(13), qa(22)); LIFT_TAG = qa(17); FLAT_TAG = qa(21)
STROKE = qa(26); STROKES = [qa(27 + 2.5 * i) for i in range(5)]
TRACK = qa(40); RULER = qa(41); IN_TAG = qa(46)
SPLIT = qa(50); TAG_ROT = qa(51); TAG_STB = qa(53); DIVIDE = qa(55)
CONCL = qa(60); EQ = qa(61); CONCL_TAG = qa(62); CARD = qa(63.5)
OUTRO = qa(70); STOPS = qa(70.5); OK = qa(72); BUB = qa(73)
BREAKDOWN = (TRACK, SPLIT)
SILENCES = [(SIL0, BIG)]
HITS = [HOOK_HIT, BRAKE, GAUGE, X4, BEEP1, BEEP2, AXLE_TAG, SPIN, DIZ_TAG, HEADZ, QMARK, BIG, LEVEL, GYRO_HIT, HTAG, LIFT_TAG, FLAT_TAG] + STROKES + [RULER, IN_TAG, TAG_ROT, TAG_STB, EQ, CONCL_TAG, CARD, OK, BUB]
CUTS = [CMP, NUM, DIZ, Q, BIG, GYRO, FAST, STROKE, TRACK, SPLIT, CONCL, OUTRO]
# "|" = forced line break (each line <= 670 px at 52 px)
SUBS = [(0.0, CMP, "这条蛇遇到危险，|直接把自己卷成轮子"),
        (CMP, NUM, "这条蛇滚着跑，|比它平时爬快 4 倍"),
        (NUM, DIZ, "测速发现：它滚得最快|每秒 3.69 米"),
        (DIZ, Q, "轮子有轴，上面可以不转，|动物没轴，全身转就会晕"),
        (Q, SIL0, "这条蛇滚的时候，|头会不会跟着转晕？"),
        (BIG, FAST, "蛇身一直在打转，|头却朝前，高度几乎不变"),
        (FAST, STROKE, "滚得越快，头抬得越高，|上下晃动反而越小"),
        (STROKE, TRACK, "秘诀：左右两侧轮流着地，|头边那段身体像划桨往下推"),
        (TRACK, SPLIT, "跑道只有 20 厘米宽，|它也能滚直，不出界"),
        (SPLIT, CONCL, "没有轴，它就分工：|身体负责转，头负责稳"),
        (CONCL, OUTRO, "身体长得不像轮子，|靠肌肉配合也能滚")]
