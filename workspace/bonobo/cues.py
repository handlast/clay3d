# 《倭黑猩猩打猎，主力居然是母的？》怪奇新发现, 47 s
# Hohmann G. et al. (2026) Females shape hunting of vertebrates in wild bonobos. Current Biology. DOI 10.1016/j.cub.2026.09.082
# Grid: 140.8 BPM (trap half-time feel = 70.4). 0.4 s -> 20.0 s = 11 bars of 4/4 + one 2/4 bar = 46 beats.
BEAT = 19.6 / 46; BAR = 4 * BEAT; G0 = 0.4; G1 = 20.0; DUR = 47.0; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
HOOK_HIT = qb(0); LAND = qb(1); HOOK_STOP = qb(5.5); HOOK_END = qb(7)
STEREO = HOOK_END; PAINT = [qb(8), qb(9), qb(10)]; QMARK = qb(12.5)
CHIMP = qb(17); CHIMP_HOPS = [qb(18), qb(20), qb(22)]; CHIMP_TAG = qb(19); MEAT_TAG = qb(23)
TEN = qb(26); TENT = qb(26.5); CAL = (qb(27), qb(31)); CNT = (qb(31), qb(34))
PIE = qb(35); RISE = (qb(41), qb(45)); SIL0 = qb(45); BIG2 = qb(46)
REVEAL = BIG2; REV_TAGS = [qb(47), qb(48)]
INIT = qb(50); INIT_TAG = qb(51); NO_STEAL = qb(53)
BABY = qb(56); BABY_STEPS = [qb(57 + i) for i in range(6)]; BABY_TAG = qb(59)
CANOPY = qb(65); SWINGS = [qb(66), qb(68), qb(70)]; MONKEY_HIT = qb(69); EQ = qb(71)
ANTE = qb(74); X3 = [qb(77), qb(77.5), qb(78)]; BARS3 = qb(80)
SHARE = qb(84); BELLS = [qb(85), qb(86), qb(88), qb(89), qb(90)]; SHARE_TAG = qb(87)
CULT = qb(92); GROUPA = qb(92.5); GROUPB = qb(93.5); CARD1 = qb(94.5); CULT_TAG = qb(95.5)
HUMAN = qb(99); FEM_ADD = qb(101); ANC_TAG = qb(102)
OUTRO = qb(104); PEACE = qb(105); BUB = qb(105.5); FINAL = qb(106)
SILENCES = [(SIL0, BIG2)]
CUTS = [HOOK_END, CHIMP, TEN, PIE, BIG2, INIT, BABY, CANOPY, ANTE, SHARE, CULT, HUMAN, OUTRO]
HITS = [HOOK_HIT, LAND] + PAINT + [QMARK] + CHIMP_HOPS + [TENT, CNT[1], BIG2] + REV_TAGS + [INIT_TAG, NO_STEAL] + BABY_STEPS[::2] + \
       SWINGS + [MONKEY_HIT, EQ] + X3 + [BARS3] + BELLS[::2] + [GROUPA, GROUPB, CARD1, CULT_TAG, FEM_ADD, PEACE, FINAL]
SUBS = [(-0.2, HOOK_END, "野生倭黑猩猩打猎，主力竟然是雌性"),
        (STEREO, CHIMP, "我们总以为，打猎是雄性的事"),
        (CHIMP, TEN, "近亲黑猩猩打猎，确实是雄性抱团"),
        (TEN, PIE, "科学家在刚果观察 10 年，记下 415 次成功捕猎"),
        (PIE, SIL0, "猎手里，雌性到底占多少？"),
        (REVEAL, INIT, "能认出猎手的记录里，60% 是雌性"),
        (INIT, BABY, "雌性自己发起追捕，不是抢雄性的猎物"),
        (BABY, CANOPY, "当妈的背着孩子，也照样去打猎"),
        (CANOPY, ANTE, "会反击的树上猴子最危险，雌雄抓得一样多"),
        (ANTE, SHARE, "地上的大羚羊，年长雌性抓得是雄性的 3 倍"),
        (SHARE, CULT, "抓到猎物后，由雌性决定谁先吃"),
        (CULT, HUMAN, "相邻两群倭黑猩猩，猎物一样，却各抓各的"),
        (HUMAN, OUTRO, "这项研究，挑战了“男人打猎”的说法")]
