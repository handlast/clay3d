# 《9900万年前，蜥蜴就会断尾逃命？》怪奇新发现, 46 s  (Nasser A. et al. 2026, Palaeontologia Electronica, DOI 10.26879/1706)
# 146.94 BPM: BAR = 19.6 / 12 so both big hits (0.4 s, 20.0 s) land on downbeats (bar 0 and bar 12).
G0 = 0.4; BAR = 19.6 / 12; BEAT = BAR / 4; DUR = 46.0
HOOK_HIT = 0.4; WIGS0 = [0.9, 1.5, 2.1]; SMUG = 1.4; HOOK_END = 3.5
TWIST = 3.5; WIGS = [4.0, 4.8, 5.6]; HUH = 5.6; SNEAK = 6.2
Q = 7.5; QMARK = 7.9; ROLL = [8.8, 9.4, 10.0, 10.6]
AMBER = 11.5; AMBER_HIT = 11.9; FINGER = 12.6; RULER = 13.4
TWIG = 15.5; MAG = 16.0; SCALES = 17.6; JUMP = 18.4
RISERS = [(18.6, 19.5)]
SIL0 = 19.5; BIG = 20.0
CT = 21.6; SCAN = 22.0; TAIL3D = 23.0
FLOWER = 24.0; PETALS = [24.4, 24.65, 24.9, 25.15, 25.4, 25.65]; MODERN = 26.6; MATCH = 27.6
CLEAN = 28.5; TICK = 29.3; CROSS = 30.3; SELF = 31.4
OLD = 32.5; OLD_HIT = 33.0; OLD_LAB = 33.8; UPG = 35.0
MYST = 36.5; CARDS = [37.0, 37.9, 38.8]; MYST_HIT = 39.8
NOW = 41.0; NOW_HIT = 41.4; FLICK = 42.4; YEARS = 43.0
OUTRO = 44.0; BUBS = [44.4, 44.9, 45.3]
SILENCES = [(19.5, 20.0)]
HITS = [HOOK_HIT] + WIGS + [QMARK] + ROLL + [AMBER_HIT, RULER, SCALES, JUMP, BIG, SCAN, TAIL3D] + PETALS[::2] + [MODERN, MATCH, TICK, CROSS, SELF,
        OLD_HIT, UPG] + CARDS + [MYST_HIT, NOW_HIT, FLICK, YEARS, BUBS[1]]
# "|" = forced line break (each line <= 670 px at 52 px)
SUBS = [(0.0, 3.5, "遇到危险，蜥蜴会|把自己的尾巴扔掉"),
        (3.5, 7.5, "断掉的尾巴还会扭，|把敌人的注意力骗走"),
        (7.5, 11.5, "可这一招，|是从什么时候开始的？"),
        (11.5, 15.5, "答案藏在一块|只有 18 毫米的琥珀里"),
        (15.5, 19.5, "大家一直以为是根小树枝，|直到有人看到了鳞片……"),
        (20.0, 21.6, "琥珀里是一截|9900 万年前的蜥蜴尾巴"),
        (21.6, 24.0, "用 X 光扫描，|不切开琥珀也能看清里面"),
        (24.0, 28.5, "断口有一圈花瓣样的肌肉，|跟今天蜥蜴主动断尾一样"),
        (28.5, 32.5, "断面整整齐齐，|不是被扯断，是自己断的"),
        (32.5, 36.5, "旧化石只能说明“能断”，|这块证明它“真断了”"),
        (36.5, 41.0, "它为什么断尾、|后来活没活下来，还是个谜"),
        (41.0, 44.0, "这招保命术用了快一亿年，|今天还在用")]
