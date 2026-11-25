def screen(d, *a, **k): pass
def jungle(d, t, top=(70, 150, 110), bot=(20, 60, 40)):
    flatbg(d, top, bot, t, False)
    for i, x in enumerate((90, 990, 200, 880)):
        tree(d, x, 1150 - (i % 2) * 120, 1.4 - 0.3 * (i // 2), 0.9, (30 + 20 * (i % 2), 100 + 20 * (i % 2), 60))
def s_hook(t, d):
    jungle(d, t)
    if t < 0.3: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - t / 0.3)))
    k = popk(t, 0.0, "bouncy")
    tigercat(d, 540, 860, 1.9 * min(1.05, max(0.3, k)), t, face="shock" if t < 1.2 else "happy")
    k2 = popk(t, 0.25, "bouncy")
    if k2 > 0: tag(d, 540, 420, "新野猫", GOLD, min(1, k2), 72)
    k3 = popk(t, 0.9, "bouncy")
    if k3 > 0: tag(d, 830, 560, "百年首个", (255, 90, 90), min(1, k3), 40, tc=WHITE)
def s_q(t, d):
    t0 = T["q"]
    flatbg(d, (250, 220, 170), (220, 170, 120), t, False)
    d.rect(180, 360, 460, 620, fill=A((150, 200, 240), 1), r=16); d.line([(320, 360), (320, 620)], A(WHITE, 1), 10)
    d.ell(540, 1080, 300, 70, A((200, 80, 90), 1))
    tigercat(d, 540, 870, 1.3, t)
    d.ell(830, 1070, 90, 30, A((90, 140, 220), 1)); d.ell(830, 1060, 70, 18, A((250, 240, 220), 1))
    ptag(d, t, t0 + 0.6, 540, 470 + 40, "家猫？", (90, 140, 220), 46, tc=WHITE)
    for i in range(2):
        hk = ap(t, t0 + 1.2 + i * 0.4, 0.2)
        if hk > 0: heart(d, 380 + i * 300, 640 - 20 * math.sin(t * 3 + i), 26, (255, 110, 140), hk)
def s_who(t, d):
    t0 = T["who"]
    flatbg(d, (240, 236, 226), (210, 204, 190), t, False)
    housecat(d, 330, 860, 1.25, t)
    tigercat(d, 760, 900, 1.0, t)
    e = ease(pr(t, t0 + 1.2, t0 + 2.0))
    if e > 0:
        d.line([(930, 1060), (930, 1060 - 340 * e)], A((255, 90, 90), 1), 8)
        if e >= 1: d.text(930, 680, "约45厘米", 34, A((255, 90, 90), 1), k=1)
    ptag(d, t, t0 + 0.2, 540, 420, "Leopardus tilcayo", NAVYT, 40, tc=WHITE)
    d.text(330, 1120, "家猫", 38, A(NAVYT, 1), k=1); d.text(760, 1120, "蒂尔卡约虎猫", 38, A(NAVYT, 1), k=1)
def s_sperm(t, d):
    t0 = T["sperm"]
    flatbg(d, (60, 110, 90), (20, 40, 34), t, False)
    for b, bx in enumerate((320, 760)):
        d.rect(bx - 190, 600, bx + 190, 1060, fill=A(WHITE, 0.12), r=30)
        d.text(bx, 560, "虎猫 " + "AB"[b], 40, A(WHITE, 1), k=1)
    for i in range(6):
        b = i % 2; bx = (320, 760)[b]; k = popk(t, t0 + 0.3 + i * 0.22, "bouncy")
        if k > 0: tigercat(d, bx - 100 + (i // 2) * 100, 760 + (i // 2 % 2) * 180, 0.45 * min(1, k), t + i, blink=False)
    ptag(d, t, t0 + 1.8, 540, 420, "过去的分法", (120, 200, 160), 38, tc=NAVYT)
def s_egg(t, d):
    t0 = T["egg"]
    dim = 1 - 0.45 * pr(t, SIL0, SIL0 + 0.15)
    flatbg(d, (40, 40, 70), (12, 12, 26), t, False)
    helix(d, 540, 780, 560, t, 0.5 * dim)
    tigercat(d, 540, 900, 1.1, t, a=dim, face="shock")
    k = popk(t, t0 + 0.4, "bouncy")
    if k > 0: d.text(800, 560, "?", int(200 * min(1, k)), A(GOLD, dim), k=1)
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (255, 200, 90), (230, 110, 50))
    if t > t0: sparks(d, 540, 820, t, t0, 30, 900, (255, 240, 200), 1, 3, 0.9)
    k = popk(t, t0 + 0.05, "bouncy")
    if k > 0:
        tigercat(d, 540, 900, 1.5 * min(1.05, k), t)
        check(d, 820, 560, 90, (80, 210, 120), 1, min(1, k))
        tag(d, 540, 430, "新物种", GOLD, min(1, k), 66)
def s_how(t, d):
    t0 = T["how"]
    flatbg(d, (236, 230, 250), (200, 190, 226), t, False)
    yr = int(1923 + (2026 - 1923) * ease(pr(t, t0 + 0.6, t0 + 2.2)))
    d.rect(300, 520, 780, 900, fill=A(WHITE, 1), r=30); d.rect(300, 520, 780, 610, fill=A((255, 90, 90), 1), r=30)
    d.text(540, 760, str(yr), 130, A(NAVYT, 1), k=1)
    ptag(d, t, t0 + 0.2, 540, 430, "上一次：1923 潘帕斯猫", (120, 90, 200), 36, tc=WHITE)
    k = popk(t, t0 + 2.3, "bouncy")
    if k > 0: tigercat(d, 860, 1060, 0.6 * min(1, k), t)
    ptag(d, t, t0 + 2.3, 400, 1060, "隔了约100年", (255, 90, 90), 36, tc=WHITE)
def s_xray(t, d):
    t0 = T["xray"]
    flatbg(d, (30, 50, 80), (10, 18, 34), t, False)
    n = int(38 * ease(pr(t, t0 + 0.3, t0 + 3.2)))
    for i in range(38):
        cx_, cy_ = 260 + (i % 7) * 93, 520 + (i // 7) * 100
        if i < n:
            if i % 3 == 0: d.ell(cx_, cy_, 30, 24, A((236, 226, 200), 1)); d.circ(cx_ - 10, cy_ - 4, 6, fill=A(NOSE, 1)); d.circ(cx_ + 10, cy_ - 4, 6, fill=A(NOSE, 1))
            else: d.circ(cx_, cy_, 26, fill=A(TCF, 1)); d.circ(cx_, cy_, 8, fill=A(TCS, 1))
    ptag(d, t, t0 + 0.2, 540, 400, "样本 %d / 38" % n, GOLD, 40, tc=NAVYT)
    ptag(d, t, t0 + 2.0, 760, 1160, "白色=博物馆老头骨", (236, 226, 200), 30, tc=NAVYT)
def s_swim(t, d):
    t0 = T["swim"]
    flatbg(d, (60, 110, 90), (20, 40, 34), t, False)
    cols = [(255, 120, 90), (255, 200, 80), (120, 220, 140), (90, 180, 255), (220, 130, 255)]
    e = ease(pr(t, t0 + 0.4, t0 + 1.6))
    d.line([(540, 1180), (540, 980)], A(WHITE, 1), 10)
    for i, c in enumerate(cols):
        x = 540 + (i - 2) * 175 * e; y = 980 - 220 * e
        d.line([(540, 980), (x, y)], A(c, 1), 10)
        if e > 0.95:
            kk = popk(t, t0 + 1.6 + i * 0.12, "bouncy")
            if kk > 0: tigercat(d, x, y - 120, 0.38 * min(1, kk), t + i, col=c, blink=False)
    if e > 0.95: d.circ(540 + 2 * 175, 760, 92, fill=A(GOLD, 0.0))
    ptag(d, t, t0 + 1.0, 540, 420, "2种 → 5种", GOLD, 54, tc=NAVYT)
def s_gene(t, d):
    t0 = T["gene"]
    jungle(d, t, (110, 170, 200), (40, 90, 80))
    px = 300; d.circ(px, 700, 60, fill=A((150, 100, 70), 1)); d.rect(px - 80, 770, px + 80, 1060, fill=A((220, 90, 70), 1), r=40)
    d.circ(px - 20, 690, 7, fill=A(NOSE, 1)); d.circ(px + 20, 690, 7, fill=A(NOSE, 1)); d.arc(px, 715, 16, 10, 10, 170, A(NOSE, 1), 4)
    tigercat(d, 780, 900, 1.0, t)
    k = popk(t, t0 + 0.4, "bouncy")
    if k > 0: bubble_txt(d, t, t0 + 0.4, 430, 500, min(1, k), WHITE, 60, tail=-1) if False else (d.rect(250, 440, 610, 560, fill=A(WHITE, 1), r=40), d.text(430, 500, "tilcayo!", 56, A(NAVYT, 1), k=1))
    ptag(d, t, t0 + 1.8, 780, 1130, "L. tilcayo", GOLD, 40, tc=NAVYT)
def s_why(t, d):
    t0 = T["why"]
    flatbg(d, (250, 236, 220), (220, 200, 180), t, False)
    for i in range(2):
        k = popk(t, t0 + 0.3 + i * 0.35, "bouncy")
        if k > 0: tigercat(d, 360 + i * 300, 900, 0.9 * min(1, k), t + i * 1.3)
    k = popk(t, t0 + 0.2, "bouncy")
    if k > 0: d.text(540, 520, "2", int(220 * min(1, k)), A((255, 90, 90), 1), k=1)
    ptag(d, t, t0 + 1.6, 540, 1150, "📍玻利维亚 Yungas" if False else "只在玻利维亚 云雾林", (60, 140, 90), 36, tc=WHITE)
def s_order(t, d):
    t0 = T["order"]
    flatbg(d, (150, 200, 230), (90, 150, 120), t, False)
    hut(d, 300, 820, 1.0)
    tigercat(d, 300, 1000, 0.55, t)
    ptag(d, t, t0 + 0.2, 300, 520, "救助站", (200, 90, 70), 36, tc=WHITE)
    for i, x in enumerate((760, 900, 650)): tree(d, x, 900 + i * 30, 1.1, 1)
    xo = 780 + 120 * ease(pr(t, t0 + 1.4, t0 + 3.0))
    tigercat(d, xo, 1060, 0.5, t, a=1 - 0.6 * pr(t, t0 + 2.4, t0 + 3.2))
    ptag(d, t, t0 + 1.2, 790, 520, "放归山林", (60, 140, 90), 36, tc=WHITE)
def s_card(t, d):
    flatbg(d, (60, 110, 90), (16, 40, 30), t, False)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    tigercat(d, cx_, cy_ - 150, 0.55, t, a=a_)
    d.text(cx_, cy_ + 30, "蒂尔卡约虎猫：百年首个新野猫", 40, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("比家猫小，只在玻利维亚", "全基因组确认是新种", "南美虎猫因此分成5种")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 130 + i * 78, s_, 38, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    jungle(d, t)
    tigercat(d, 540, 940, 1.1, t)
    k = popk(t, t0 + 0.8, "bouncy")
    if k > 0:
        d.rect(640, 1000, 900, 1150, fill=A(WHITE, 1), r=16)
        d.text(770, 1040, "户口", 34, A(NAVYT, 1), k=1); d.text(770, 1100, "L. tilcayo", 26, A((255, 90, 90), 1), k=1)
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 285, "Lescroart et al. 2026", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 330, "Current Biology · Leopardus tilcayo", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

