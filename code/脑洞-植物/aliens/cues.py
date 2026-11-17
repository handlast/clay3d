# 《历史课没讲的一天》娱乐加更 · 纯属虚构, 42 s  (reference: user's collage, fully redrawn)
# Grid: 7/4 (4+3). 0.4 s and 20.0 s on bar lines -> 5 bars of 7/4 = 35 beats in 19.6 s -> 107.14 BPM.
BEAT = 19.6 / 35; BAR = 7 * BEAT; G0 = 0.4; G1 = 20.0; DUR = 42.0; BPM = 60 / BEAT
def qb(k): return round(G0 + k * BEAT, 4)
# 0-2.36 hook: statue lasers the UFO in front of the moon; tape stop 2.08 while the "3 hours ago" clock slides in; cut 2.36
HOOK_HIT = qb(0); HOOK_STOP = qb(3); CLOCK_IN = qb(3)
REWIND = qb(3.5); LOOP_IN = qb(4); POD = qb(5); POD_LAND = qb(5.5); DOOR_OPEN = qb(6); STEP = qb(6.5); HANDS = qb(7.5)
DATE = qb(9); HEART1 = qb(10); POSE = qb(11); SNAP = qb(12); SNAP2 = qb(12.5)
FLAG = qb(14); PLANT = qb(15); CLAIM = qb(16)
DINO = qb(18); PEEK = qb(19); ROAR = qb(20); PTERO = qb(22); STEAL = qb(22.5); WAIT = qb(23)
PHARAOH = qb(25); LAND = qb(25.5); AIM = qb(27); GLARE = [qb(28), qb(28.5), qb(29)]
FLEET = qb(30); FLEET_HITS = [qb(30.5), qb(31.5), qb(32.5)]
RISERS = [(qb(30), qb(34))]
SIL0 = qb(34); BIG2 = qb(35)            # 19.44 silent: statue opens its eyes ; 20.00 laser
BOOM2 = qb(35.5)
FALL = qb(38); TRAILS = [qb(39), qb(40), qb(41)]
EXTINCT = qb(42.5); LOOKUP = qb(43); Q_HIT = qb(44.5)
SELFIE = qb(47); CLICK = qb(48.5); FREEZE = qb(49)
STONE = qb(53); WHISTLE = qb(54.5); STARE = qb(56); BUSTED = qb(57.5)
EXAM = qb(60); WRITE = qb(61); REDX = qb(63.5); REDX2 = qb(64.5)
OUTRO = qb(68); FINAL = qb(68.5); WINK = qb(70)
SILENCES = [(SIL0, BIG2)]
CUTS = [REWIND, DATE, FLAG, DINO, PHARAOH, FLEET, BIG2, FALL, EXTINCT, SELFIE, STONE, EXAM, OUTRO]
HITS = [HOOK_HIT, POD_LAND, DOOR_OPEN, HANDS, HEART1, SNAP, PLANT, PEEK, ROAR, STEAL, WAIT, LAND, AIM] + GLARE + FLEET_HITS + \
       [BIG2, BOOM2] + TRAILS + [Q_HIT, CLICK, FREEZE, WHISTLE, BUSTED, WRITE, REDX, FINAL]
# "|" = forced line break (each line <= 670 px at 52 px)
SUBS = [(-0.2, REWIND, "月亮前，一艘飞碟|被一道激光打爆了"),
        (REWIND, STEP, "时间倒回 3 小时前"),
        (STEP, DATE, "时空门里掉出个胶囊，|两个外星人手拉手下来"),
        (DATE, SNAP, "他们是来|金字塔约会的"),
        (SNAP, FLAG, "先来张自拍"),
        (FLAG, DINO, "插上小旗：|“这块地，我们的了”"),
        (DINO, STEAL, "金字塔后面，|探出来一个大脑袋"),
        (STEAL, PHARAOH, "翼龙一口叼走了自拍杆"),
        (PHARAOH, AIM, "法老外星人|扛着大水枪赶到"),
        (AIM, FLEET, "双方对峙，|谁也不让谁"),
        (FLEET, SIL0, "天上的飞碟舰队|也压过来了"),
        (BIG2, FALL, "沙子里的石像国王，|醒了"),
        (FALL, EXTINCT, "炸碎的飞碟拖着火尾，|砸向地球"),
        (EXTINCT, SELFIE, "所有恐龙抬头：|……"),
        (SELFIE, STONE, "翼龙按下快门：|全员惊恐合照"),
        (STONE, EXAM, "石像国王：|“我只是一块石头”"),
        (EXAM, OUTRO, "历史考试|千万别这么写"),
        (OUTRO, 99, "纯属虚构，|看个乐呵")]
