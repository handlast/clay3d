# 《穿鞋会改造你的骨头？》怪奇新发现, 47 s
# Farrell H.N. et al. (2026) The impact of footwear on human talar trabecular architecture. J. Anat. DOI 10.1111/joa.70236
# Grid: 0.4 s and 20.0 s are both bar lines -> 8 bars of 4/4 + one 2/4 bar = 34 beats in 19.6 s -> 104.08 BPM.
BEAT = 19.6 / 34; BAR = 4 * BEAT; G0 = 0.4; G1 = 20.0; DUR = 47.0; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
HOOK_HIT = qb(0); HOOK_CLICKS = [qb(2), qb(3)]; HOOK_END = qb(5.5)
TALUS = HOOK_END; TALUS_HIT = qb(6); WEIGHT = [qb(8), qb(9)]; TAG_HIT = qb(10)
EIF = qb(12); POPS = [qb(12.5 + 0.5 * i) for i in range(12)]; EIF_TAGS = [qb(13), qb(15)]
REO = qb(19); FLIP = qb(20); GROUPS = [qb(20.5 + 0.5 * i) for i in range(8)]
SCAN = qb(25); SHOE_CNT = (qb(26), qb(29)); FOOT_CNT = (qb(29.5), qb(31)); RISERS = [(qb(31), qb(33))]
SIL0 = qb(33); BIG2 = qb(34)
REVEAL = BIG2; REV_TAGS = [qb(35), qb(35.5)]
SHOD = qb(37); SHOD_HITS = [qb(38), qb(39)]
MEDIAL = qb(41); MED_HITS = [qb(42), qb(44), qb(46)]
BARE = qb(48); CLIMB = [qb(49), qb(50), qb(51)]; SQUAT = qb(52); SQ_BOB = [qb(53), qb(54)]
ALIVE = qb(55); SQUEEZE = [qb(56), qb(58), qb(60)]
ANC = qb(62); PRINTS = [qb(63 + i) for i in range(7)]; FOSSIL = qb(64.5)
BAL = qb(70); BAL_DROP = [qb(71), qb(71.5)]; BAL_SET = qb(72); BAL_TAG = qb(74)
OUTRO = qb(76); WINK = qb(77); BUB = qb(76.5); FINAL = qb(78)
SILENCES = [(SIL0, BIG2)]
HITS = [HOOK_HIT] + HOOK_CLICKS + [TALUS_HIT] + WEIGHT + [TAG_HIT] + EIF_TAGS + [FLIP, GROUPS[-1]] + [BIG2] + SHOD_HITS + MED_HITS + CLIMB + [SQUAT] + SQUEEZE + [PRINTS[0], FOSSIL, BAL_SET, WINK, FINAL]
SUBS = [(-0.2, HOOK_END, "你每天穿鞋，脚踝里的骨头正在悄悄改造"),
        (TALUS, EIF, "脚踝里有块骨头叫距骨，全身的重量都压在它身上"),
        (EIF, REO, "骨头里面是海绵一样的支架，像埃菲尔铁塔"),
        (REO, SCAN, "受力一变，支柱就会重新排队"),
        (SCAN, SIL0, "科学家扫描了 40 个穿鞋的人和 16 个常年赤脚的人"),
        (REVEAL, SHOD, "结果一出来：两边的支架完全不一样"),
        (SHOD, MEDIAL, "穿鞋的人：骨头支架堆在后面"),
        (MEDIAL, BARE, "还往大脚趾那侧偏，鞋把重量重新分配了"),
        (BARE, ALIVE, "赤脚的人：支架堆在前面，可能来自爬树和下蹲"),
        (ALIVE, ANC, "骨头不是死的，一辈子都在跟着你的动作改"),
        (ANC, BAL, "这能帮科学家看懂，几百万年前的祖先怎么走路"),
        (BAL, OUTRO, "这不是说穿鞋有害，只是骨头记住了你怎么走")]
