# 《7.5万年前的命案：这根骨头上的洞，是谁干的？》怪奇新发现, ~47 s
# Pomeroy E., Hunt C.O., ... Barker G. (2026) Sci. Rep. 16(1), DOI 10.1038/s41598-026-69193-z
# Grid: 7/4. 0.4 s and 20.0 s both on bar lines -> 5 bars of 7/4 = 35 beats in 19.6 s -> 107.14 BPM.
BEAT = 19.6 / 35; BAR = 7 * BEAT; G0 = 0.4; G1 = 20.0; DUR = 47.0; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
# 0-2.36 hook: bone + hole, push into the hole; tape stop 2.08 while the magnifier slides in
HOOK_HIT = qb(0); ZOOM = (qb(1), qb(3)); HOOK_STOP = qb(3); LENS_IN = qb(3)
CAVE = qb(3.5); LOOP_IN = qb(4); DIG = (qb(3.5), qb(7)); FOUND = qb(6.5)
THIN = qb(7.5); LAMP = qb(8); GLOW = qb(9); SCAP_TAG = qb(9.5)
PROFILE = qb(11); PHOTO = qb(11.5); FIELDS = [qb(12.5), qb(13.5), qb(14.5), qb(15.5)]; NEAN_TAG = qb(16.5)
EVID = qb(18); CHECKS = [qb(19), qb(19.5), qb(20)]; LENS = qb(21); RULER = qb(22); TICKS = [qb(22 + 0.25 * i) for i in range(4)]; MM15 = qb(23)
STOP1 = (qb(23.5), qb(25))
SUSP = qb(25); SPOTS = [qb(26.5), qb(28), qb(29.5), qb(31)]; SCRATCH = qb(32); RISERS = [(qb(28), qb(34))]
SIL0 = qb(34); BIG2 = qb(35)
REVEAL = BIG2; CLUE1 = qb(37); STONE = qb(38); WOODH = qb(38.5); MATCH = qb(39.5); TEST_TAG = qb(40)
CLUE2 = qb(41); ZOOMB = qb(42); EXIT_TAG = qb(43); PATH2 = qb(44.5); ARROW2 = qb(45.5)
CLUE3 = qb(47.5); PIECES = [qb(48.5), qb(49), qb(49.5), qb(50)]; DOWN = qb(51); RIDGE_TAG = qb(52)
RECON = qb(53.5); DASH = (qb(54), qb(56)); HEART = qb(56.5); AIM = qb(57); MAYBE = qb(58)
STOP2 = (qb(59), qb(60))
TWIST = qb(60); CRACK = qb(60.5); TILT = qb(61.5); CALC = qb(64); FLIPS = [qb(64.5 + 0.25 * i) for i in range(8)]; YEAR = qb(66.5)
CARE = qb(68); BOWL = qb(69); HAND = qb(70.5); HEARTS = qb(71.5); SOFT_TAG = qb(72)
CARD = qb(74); CHIPS = [qb(75), qb(75.5), qb(76)]
OUTRO = qb(79); STONE_UP = qb(79.5); BUB = qb(80.5); FINAL = qb(80)
SILENCES = [(SIL0, BIG2)]
CUTS = [CAVE, THIN, PROFILE, EVID, SUSP, BIG2, CLUE1, CLUE2, CLUE3, RECON, TWIST, CARE, CARD, OUTRO]
HITS = [HOOK_HIT, FOUND, LAMP, PHOTO] + FIELDS + CHECKS + [LENS, MM15] + SPOTS + [BIG2, STONE, WOODH, MATCH, ZOOMB, EXIT_TAG, ARROW2] + PIECES + [DOWN, HEART, AIM, CRACK, TILT, YEAR, BOWL, HAND, HEARTS, CARD] + CHIPS + [FINAL]
# "|" = forced line break (each line <= 670 px at 52 px)
SUBS = [(-0.2, CAVE, "这块骨头上的洞，|是一桩 7.5 万年前的命案"),
        (CAVE, THIN, "它埋在近 8 米厚的|石头和泥土下面"),
        (THIN, PROFILE, "这块肩胛骨薄得能透光，|却几乎完好"),
        (PROFILE, FIELDS[2], "死者是一个尼安德特人：|一种已经灭绝的古人类"),
        (FIELDS[2], EVID, "大约 45 岁，|死在伊拉克的沙尼达尔洞穴"),
        (EVID, STOP1[0], "整块骨头几乎完好，|只有一个 15 毫米的圆洞"),
        (STOP1[0], SUSP, "这是它身上唯一的破损"),
        (SUSP, SPOTS[2], "凶器到底是什么？"),
        (SPOTS[2], SIL0, "石矛？木矛？猛兽？|还是摔了一跤？"),
        (BIG2, CLUE1, "答案：一根削尖的木矛"),
        (CLUE1, CLUE2, "线索一：石尖的洞有棱角，|木矛打的才是圆洞"),
        (CLUE2, PATH2, "线索二：洞边是斜的，|这是“穿出去”那一面"),
        (PATH2, CLUE3, "说明矛从前面刺进，|从背后穿出"),
        (CLUE3, DOWN, "线索三：撞掉的小骨片，|能像拼图一样拼回去"),
        (DOWN, RECON, "碎片的方向说明：|矛是从上往下刺的"),
        (RECON, AIM, "这条路线，|正好经过心脏附近"),
        (AIM, TWIST, "很像一次|瞄准心脏的一击"),
        (TWIST, CALC, "可它的脸生前被重击过，|门牙裂成了两半"),
        (CALC, CARE, "断牙上积了厚厚的牙结石：|受伤后它又活了至少一年"),
        (CARE, CARD, "没法好好咀嚼，|是同伴照顾它活了下来"),
        (CARD, OUTRO, "记住这三条，|你也能读懂骨头上的伤"),
        (OUTRO, 99, "同伴把它葬在大石头后面，|头朝东方")]
