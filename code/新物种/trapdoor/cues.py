# 《住在海里的蜘蛛：涨潮全淹，家里却一滴水不进》怪奇新发现, 47 s
# Sherwood D., Cole N. C., ... Tercel M. P. T. G. (2026) Arachnology 20(4): 608-622, DOI 10.13156/arac.2026.20.4.18
# Grid: 4/4 calypso swing. 0.4 s and 20.0 s on bar lines -> 8 bars of 4/4 + 1 bar of 2/4 = 34 beats in 19.6 s -> 104.08 BPM.
BEAT = 19.6 / 34; BAR = 4 * BEAT; G0 = 0.4; G1 = 20.0; DUR = 47.0; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
# 0-2.42 hook: wave slams, door slams; tape stop at 2.13 while a headlamp beam slides in; cut 2.42
HOOK_HIT = qb(0); QLINE = qb(1.5); HOOK_STOP = qb(3); LAMP_IN = qb(3)
NIGHT = qb(3.5); LOOP_IN = qb(4); LEGS = qb(5.5); SCREAM = qb(6.5); QUOTE = qb(8)
FAMILY = qb(10); TARAN = qb(10.5); KIN_TAG = qb(11.5); INLAND = [qb(12), qb(12.5)]; SEA = qb(13.5)
ZONE = qb(14.5); CARD1 = qb(15); TIDE_UP = qb(15.5); TIDE_DN = qb(16.5); SOUTH = qb(17.5)
TUBE = qb(19); WORMS = qb(19.5); NODIG = qb(21); MOVEIN = qb(22); RULER = qb(23); LINING = qb(24)
DOOR = qb(25); ING = [qb(25.5), qb(26), qb(26.5)]; FORM = qb(27); COIN = qb(28); HIDE = qb(29); FIND = qb(29.5)
TEST = qb(30); POUR = (qb(30.25), qb(33)); TIMER = (qb(30.5), qb(32.75)); ASK = qb(32)
RISERS = [(qb(30), qb(33))]
SIL0 = qb(33); BIG2 = qb(34)
REVEAL = BIG2; DRIP = qb(34.5)
WHY1 = qb(35.5); LAYERS = [qb(36), qb(36.5), qb(37)]; BOUNCE = [qb(37.5), qb(38), qb(38.5)]
WHY2 = qb(39.5); PULL = [qb(40.5), qb(41)]; SEAL = qb(42)
HUNT = qb(44); OPEN = qb(44.5); PREY = [qb(46), qb(47.5), qb(49)]; STOP1 = (qb(44), qb(46))
TINY = qb(50.5); ISL = [qb(51.5), qb(52.5)]; SUM = qb(54); COURTS = [qb(55), qb(55.5)]
NAME = qb(57); WALL = qb(58.5); MEAN = qb(59); PCT = qb(61); PCT_HIT = qb(62)
CARD = qb(63); CHIPS = [qb(64.5), qb(65), qb(65.5)]
OUTRO = qb(69); SHUT = qb(70); FINAL = qb(71)
SILENCES = [(SIL0, BIG2)]
CUTS = [NIGHT, FAMILY, ZONE, TUBE, DOOR, TEST, BIG2, WHY1, WHY2, HUNT, TINY, NAME, CARD, OUTRO]
HITS = [HOOK_HIT, QLINE, LEGS, SCREAM, TARAN, KIN_TAG] + INLAND + [SEA, CARD1, TIDE_UP, NODIG, MOVEIN, RULER] + ING + [FORM, COIN, FIND,
        BIG2, DRIP] + LAYERS + BOUNCE + PULL + [SEAL, OPEN] + PREY + ISL + [SUM] + COURTS + [WALL, MEAN, PCT_HIT, CARD] + CHIPS + [SHUT, FINAL]
# "|" = forced line break (each line <= 670 px at 52 px)
SUBS = [(-0.2, NIGHT, "涨潮时，它的家|会被海水整个淹掉"),
        (NIGHT, LEGS, "2023 年，毛里求斯小岛|天黑后，科学家翻岩缝"),
        (LEGS, QUOTE, "洞口伸出一对长腿——|他当场尖叫"),
        (QUOTE, FAMILY, "同事回忆：|记得最清楚的是他在尖叫"),
        (FAMILY, INLAND[0], "它是捕鸟蛛的亲戚，|属于原蛛下目"),
        (INLAND[0], ZONE, "绝大多数蜘蛛远离大海，|它却住在海边"),
        (ZONE, SOUTH, "潮间带：涨潮被淹、|退潮露出的那条海岸"),
        (SOUTH, TUBE, "它还专挑浪最大的南岸"),
        (TUBE, NODIG, "它不自己挖洞"),
        (NODIG, RULER, "住的岩管，可能是数千年前|蠕虫和贝类钻出来的"),
        (RULER, DOOR, "洞约 12 厘米长，|内壁铺着蛛丝和沙"),
        (DOOR, COIN, "门用蛛丝、沙子、藻类做成"),
        (COIN, TEST, "只有硬币大小，|关上就和岩石融为一体"),
        (TEST, SIL0, "往巢上浇 20 秒海水，|打开看看——"),
        (BIG2, WHY1, "里面没有积水"),
        (WHY1, WHY2, "原因一：靠门的材料|蛛丝、沙子、藻类"),
        (WHY2, SEAL, "原因二：被淹时，|蜘蛛从里面往下拉住门"),
        (SEAL, HUNT, "可能把门缝压得更紧"),
        (HUNT, PREY[0], "它主要在夜里活动，|开门伸腿，在门口伏击"),
        (PREY[0], TINY, "圈养时，它吃等足类、|蟋蟀和飞蛾"),
        (TINY, SUM, "全世界只在两座小岛上找到"),
        (SUM, NAME, "加起来约 913 平方米，|差不多两个篮球场"),
        (NAME, PCT, "它叫 marevallum，|拉丁语意思是“海墙”"),
        (PCT, CARD, "这篇论文让毛里求斯|已知蜘蛛种类多了约 27%"),
        (CARD, OUTRO, "门的材料 + 从里面拉紧，|20 秒海水也灌不进"),
        (OUTRO, 99, "2026 年 4 月，|它被正式命名为新种")]
