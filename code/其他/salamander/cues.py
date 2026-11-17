# 《有毒的火蝾螈，一照紫外灯居然会发光？》怪奇新发现, ~46.5 s
# Burriel-Carranza B., Brunetti A.E. ... Kaltenpoth M., Carranza S. (2026) Glandular biofluorescence in fire salamanders
# (Salamandra salamandra): first evidence and ecological implications. R. Soc. Open Sci. 13(5). DOI 10.1098/rsos.251991
# Grid: 0.4 s and 20.0 s are bar lines -> 9 bars of 4/4 in 19.6 s -> BAR 2.1778 s, 110.2 BPM. A minor (Am F Dm E).
BEAT = 19.6 / 36; BAR = 4 * BEAT; G0 = 0.4; G1 = 20.0; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
def bar(n): return qb(4 * n)
DUR = 46.6
# --- 1 hook
LIGHT_OFF = 0.16; HOOK_HIT = qb(0); HOOK_STOP = qb(4); HOOK_END = qb(6)          # 0.40 / 2.58 / 3.67
# --- 2 meet
MEET = HOOK_END; MEET_TAGS = [qb(7), qb(9), qb(10), qb(11.5)]                     # 火蝾螈 / 有毒 / 蝾螈碱 / 易危
# --- 3 lab
LAB = qb(13); PAPERS = [qb(13.5 + 0.5 * i) for i in range(10)]; LAB_STAMP = qb(15)
# --- 4 nobody (drop bar 5 = 11.28 - 13.47)
NONE = qb(20); QMARKS = [qb(20.5), qb(21), qb(21.5)]; ZERO = qb(22); NONE_TAG = qb(24)
# --- 5 switch countdown
SWITCH = qb(28); COUNT = [qb(30), qb(32), qb(34)]; RISERS = [(qb(30), qb(35))]
SIL0 = qb(35); BIG = G1                                                            # 19.456 -> 20.0 black + silence
# --- 6 burst
BURST = BIG; BURST_TAGS = [qb(37), qb(38)]
# --- 7 venom
VENOM = qb(39); DRIP = qb(40); CLOCK0 = qb(41); CLOCK1 = qb(43.5); VEN_STAMP = qb(44)
# --- 8 fluorescence vs luminescence
FLUO = qb(45); FIREFLY = [qb(46), qb(46.5), qb(47)]; UVON = qb(49); CONVERT = qb(50); FLUO_TAG = qb(51)
# --- 9 molecule
MOL = qb(53); GLITCH = [qb(54), qb(55.5), qb(57), qb(58)]; MOL_TAG = qb(57)
# --- 10 hypothesis 1: full moon (breakdown bars 15-16, bar 16 = drop bar)
MOON = qb(60); HEARTS = [qb(62), qb(63), qb(64), qb(66)]; MOON_TAG = qb(61)
# --- 11 hypothesis 2: predator
PRED = qb(68); FOX_IN = qb(69); ZAP = qb(71); ZAP2 = qb(72); PRED_STAMP = qb(73)
# --- 12 ending
END = qb(76); DOTS0 = qb(77); END_STAMP = qb(79)
# --- 13 outro
OUTRO = qb(81); WINK = qb(82); BUB = qb(82.5); FINAL = qb(84)
SILENCES = [(SIL0, BIG)]
HITS = [HOOK_HIT] + MEET_TAGS + [LAB_STAMP] + QMARKS + [ZERO] + COUNT + [BIG] + BURST_TAGS + [DRIP, VEN_STAMP] + FIREFLY[::2] + \
       [UVON, CONVERT] + GLITCH + HEARTS + [ZAP, ZAP2, PRED_STAMP, DOTS0, END_STAMP, WINK, FINAL]
SUBS = [(-0.2, HOOK_END, "这只有毒的蝾螈，|紫外灯一照全身发光"),
        (MEET, LAB, "这种黑黄蝾螈叫火蝾螈，|黑黄配色就是警告：我有毒"),
        (LAB, NONE, "火蝾螈的毒液，|科学家已经研究了几十年"),
        (NONE, SWITCH, "可几十年里，从没人报道过|火蝾螈会发光"),
        (SWITCH, SIL0, "直到研究者关掉灯，|打开紫外灯照它……"),
        (BURST, VENOM, "紫外灯下发出绿光、青光，|肚子和身体两侧最亮"),
        (VENOM, FLUO, "它皮肤分泌的毒液也会亮，|离开身体 24 小时后还在亮"),
        (FLUO, UVON, "萤火虫是“生物发光”：|身体自己会点灯"),
        (UVON, MOL, "火蝾螈是“生物荧光”：|把看不见的紫外光变成绿光"),
        (MOL, MOON, "火蝾螈靠哪种分子发光？|科学家还不知道答案"),
        (MOON, PRED, "猜想一：发光也许是|夜里给同伴看的暗号"),
        (PRED, END, "猜想二：给天敌再加一道|警告：我有毒，别吃我"),
        (END, OUTRO, "连研究了几十年的动物，|也可能藏着没人见过的秘密")]
