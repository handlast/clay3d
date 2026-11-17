# 《这条“海马”是冒牌货？在博物馆抽屉里躺错了地方》怪奇新发现, ~47 s
# Short G. & Harasti D. et al. (2026) Journal of Lost Species, DOI 10.66264/y1ffbcwb
# Grid: 0.4 s and 20.0 s both on bar lines -> 8 bars of 4/4 = 32 beats in 19.6 s -> 97.96 BPM.
BEAT = 19.6 / 32; BAR = 4 * BEAT; G0 = 0.4; G1 = 20.0; DUR = 47.5; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
HOOK_HIT = qb(0); RIP_END = qb(1); HOOK_STOP = qb(4)
SAME = qb(5); CHECKS = [qb(7), qb(8.5), qb(10)]
TINY = qb(11.5); THUMB = qb(12); MEASURE = qb(14); TINY_POP = qb(15.5)
DRAWER = qb(18); DRAWER_OPEN = qb(18.5); LABEL = qb(19.5); SAD = qb(20.5); STOP1 = (qb(22), qb(24)); DUSTQ = qb(22)
CT = qb(24.5); TRAY = qb(25); ZZZ = (qb(26), qb(28)); COUNT = [qb(28), qb(29), qb(30)]; SHUTTER = qb(31)
RISERS = [(qb(26), qb(31))]
SIL0 = qb(31); BIG2 = qb(32)
REVEAL = BIG2; XS = [qb(33), qb(34)]
DETAIL = qb(36); MARKS = [qb(36.5), qb(38)]
DNA = qb(39.5); JARS = qb(40); FORMX = qb(42); HELIX = qb(43); DNA_TAG = qb(45)
TREE = qb(47); CROUCH = qb(50); JUMP = qb(51); LAND = qb(52); STOP2 = (qb(50), qb(52))
CONV = qb(53.5); GROW = (qb(54), qb(55.5)); FORM = qb(56); TWICE = qb(56.5); CARD = qb(57)
LOST = qb(61); TRAWL = (qb(61.5), qb(63.5)); CATCH = qb(63); MAP = qb(64); DOTS = [qb(64 + 0.5 * i) for i in range(7)]
ALIVE = qb(67.5); EYES = qb(68.5); ALIVE_TAG = qb(69.5)
OUTRO = qb(72); BUB = qb(72.5); MASK_ON = qb(73); WINK = qb(73.5); FINAL = qb(74)
SILENCES = [(SIL0, BIG2)]
CUTS = [SAME, TINY, DRAWER, CT, BIG2, DETAIL, DNA, TREE, CONV, LOST, ALIVE, OUTRO]
HITS = [HOOK_HIT] + CHECKS + [THUMB, MEASURE, TINY_POP, DRAWER_OPEN, LABEL, SAD] + COUNT + [BIG2] + XS + MARKS + [JARS, FORMX, HELIX, LAND, FORM, CARD, CATCH] + DOTS[::2] + [EYES, ALIVE_TAG, WINK, FINAL]
# "|" = forced line break (each line <= 670 px at 52 px)
SUBS = [(-0.2, SAME, "这只“海马”，|其实是个冒牌货"),
        (SAME, TINY, "马头、卷尾巴、育儿袋，|它和海马全都一样"),
        (TINY, DRAWER, "它的个头，|还不到你一根拇指长"),
        (DRAWER, STOP1[0], "它被错放进博物馆|“无脊椎动物”的抽屉"),
        (STOP1[0], CT, "多年都没人发现它放错了"),
        (CT, SIL0, "直到科学家给它拍了 CT：|不用切开，就能看清骨头"),
        (BIG2, DETAIL, "真海马肚子上有一圈|骨板笼子，头顶还有骨冠"),
        (DETAIL, DNA, "这条冒牌货，|骨笼和骨冠一样都没有"),
        (DNA, TREE, "只有一条标本泡在酒精里，|还能测出它的 DNA"),
        (TREE, CONV, "DNA 也说它不是海马，|而是自成一家的新“属”"),
        (CONV, CARD, "海马这套身材，|大自然至少独立造了两次"),
        (CARD, LOST, "不是亲戚也能长得一样，|这就叫“趋同演化”"),
        (LOST, ALIVE, "这种鱼只有 7 个标本，|全世界没人见过活的"),
        (ALIVE, OUTRO, "这种鱼很可能还在深海里，|等人去找")]
