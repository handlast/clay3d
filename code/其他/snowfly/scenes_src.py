def screen(d, *a, **k): pass
def s_hook(t, d):
    snowfield(d, t)
    if t < 0.3: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - t / 0.3)))
    x = 300 + 120 * pr(t, 0, 3.4)
    snowfly(d, x, 960, 1.6, t, heat=0.4)
    thermo(d, 820, 640, 0.18 - 0.05 * pr(t, 0, 1), 1, (90, 170, 255))
    k = popk(t, 0.15, "bouncy")
    if k > 0: tag(d, 820, 470, "-6℃", (90, 170, 255), min(1, k), 60, tc=WHITE)
def s_q(t, d):
    t0 = T["q"]
    snowfield(d, t)
    for i, x in enumerate((260, 820)):
        k = popk(t, t0 + 0.2 + i * 0.25, "bouncy")
        if k > 0: icebug(d, x, 700, 0.8 * min(1.05, k), t)
    snowfly(d, 540 + 40 * math.sin(t * 1.2), 1000, 1.3, t, heat=0.4)
    ptag(d, t, t0 + 1.4, 540, 470, "冻住了", (120, 170, 220), 40, tc=WHITE)
def s_who(t, d):
    t0 = T["who"]
    flatbg(d, (240, 236, 226), (210, 204, 190), t, False)
    snowfly(d, 540, 820, 2.0, t, walk=0.3)
    k = popk(t, t0 + 0.6)
    if k > 0:
        d.ell(450, 650, 70 * min(1, k), 30 * min(1, k), A((180, 220, 255), 0.6)); d.ell(630, 650, 70 * min(1, k), 30 * min(1, k), A((180, 220, 255), 0.6))
        kx = pr(t, t0 + 1.1, t0 + 1.4)
        if kx > 0: cross(d, 540, 650, 160, kx, (230, 60, 60))
    ptag(d, t, t0 + 0.3, 540, 450, "雪蝇 Chionea", NAVYT, 42, tc=WHITE)
    ptag(d, t, t0 + 1.6, 540, 1110, "没有翅膀", (230, 60, 60), 38, tc=WHITE)
def s_sperm(t, d):
    t0 = T["sperm"]
    flatbg(d, (60, 70, 100), (20, 24, 40), t, False)
    for i in range(3):
        x = 270 + i * 270; k = ease(pr(t, t0 + 0.4 + i * 0.4, t0 + 1.1 + i * 0.4))
        snowfly(d, x, 760 + 120 * k, 0.6, t * (1 - k), walk=1 - k, face="cold", scarf=False, col=(120, 110, 140))
        if k > 0.9:
            for z in range(3): d.text(x + 60 + z * 26, 640 - z * 40 - 10 * math.sin(t * 2 + z), "Z", 30 + z * 8, A(WHITE, 0.8), k=1)
    d.rect(150, 960, 930, 1010, fill=A((90, 80, 70), 1), r=20)
    ptag(d, t, t0 + 0.3, 540, 450, "冷血动物", (120, 170, 220), 40, tc=WHITE)
def s_egg(t, d):
    t0 = T["egg"]
    dim = 1 - 0.45 * pr(t, SIL0, SIL0 + 0.15)
    flatbg(d, (40, 50, 80), (12, 16, 30), t, False)
    g = ease(pr(t, t0 + 0.3, t0 + 4.6))
    for i in range(8):
        u = i / 8 * 2 * math.pi
        r0 = 600 - 330 * g
        crystal(d, 540 + math.cos(u) * r0, 820 + math.sin(u) * r0 * 1.1, 60, 0.9 * dim, t * 0.3 + i)
    snowfly(d, 540, 840, 1.0, t, walk=0.2, face="cold", a=dim)
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (255, 190, 90), (220, 80, 40))
    if t > t0: sparks(d, 540, 820, t, t0, 30, 900, (255, 240, 200), 1, 3, 0.9)
    k = popk(t, t0 + 0.05, "bouncy")
    if k > 0:
        snowfly(d, 540, 860, 1.6 * min(1.05, k), t, heat=1.0)
        for i in range(6):
            u = i / 6 * 2 * math.pi; r_ = 300 + 250 * pr(t, t0, t0 + 1.2)
            crystal(d, 540 + math.cos(u) * r_, 860 + math.sin(u) * r_, 50, 1 - pr(t, t0 + 0.6, t0 + 1.4), t + i)
        tag(d, 540, 450, "自带暖气", GOLD, min(1, k), 60)
def s_how(t, d):
    t0 = T["how"]
    flatbg(d, (230, 236, 244), (190, 200, 216), t, False)
    sh = 6 * math.sin(t * 60) * (1 - pr(t, t0 + 2.4, t0 + 2.6))
    d.ell(300 + sh, 820, 110, 80, A((250, 200, 60), 1))
    for j in range(3): d.rect(260 + sh + j * 40, 750, 280 + sh + j * 40, 890, fill=A(NAVYT, 1))
    d.text(300, 960, "蜜蜂：发抖产热", 38, A(NAVYT, 1), k=1)
    snowfly(d, 780, 820, 0.9, t, walk=0.2, heat=0.6)
    d.text(780, 960, "雪蝇：不抖", 38, A(NAVYT, 1), k=1)
    v = 0.3 + 0.15 * ease(pr(t, t0 + 1.2, t0 + 2.6))
    thermo(d, 920, 640, v)
    ptag(d, t, t0 + 2.6, 900, 360, "+1~2℃", (255, 90, 90), 38, tc=WHITE)
def s_xray(t, d):
    t0 = T["xray"]
    flatbg(d, (60, 30, 30), (20, 8, 10), t, False)
    d.circ(380, 800, 230, fill=A((255, 200, 170), 0.35))
    for i in range(5):
        u = i / 5 * 2 * math.pi + t * 0.4; mx_, my_ = 380 + math.cos(u) * 120, 800 + math.sin(u) * 110
        gl = ap(t, t0 + 0.4 + i * 0.2, 0.3)
        d.circ(mx_, my_, 50, fill=A((255, 140, 60), 0.25 * gl)); d.ell(mx_, my_, 40, 20, A((255, 120, 60), 1))
    ptag(d, t, t0 + 0.3, 380, 500, "细胞产热", (255, 140, 60), 38, tc=NAVYT)
    k = popk(t, t0 + 1.8, "bouncy")
    if k > 0:
        s_ = min(1, k); bx, by = 790, 820
        d.ell(bx, by, 120 * s_, 100 * s_, A(WHITE, 1)); d.circ(bx - 60 * s_, by - 90 * s_, 30 * s_, fill=A(WHITE, 1)); d.circ(bx + 60 * s_, by - 90 * s_, 30 * s_, fill=A(WHITE, 1))
        d.circ(bx - 35 * s_, by - 20 * s_, 9 * s_, fill=A(NOSE, 1)); d.circ(bx + 35 * s_, by - 20 * s_, 9 * s_, fill=A(NOSE, 1)); d.circ(bx, by + 15 * s_, 16 * s_, fill=A(NOSE, 1))
        tag(d, bx, 1000, "棕色脂肪", (190, 130, 90), s_, 34, tc=WHITE)
    ptag(d, t, t0 + 2.6, 540, 1170, "推测", WHITE, 32, tc=NAVYT)
def s_swim(t, d):
    t0 = T["swim"]
    flatbg(d, (30, 70, 120), (10, 24, 50), t, False)
    g = 1 - 0.65 * ease(pr(t, t0 + 1.0, t0 + 2.4))
    crystal(d, 540, 800, 260 * g + 10 * math.sin(t * 3), 1, t * 0.2)
    for i in range(6):
        u = t * 0.2 + i * math.pi / 3; k = ease(pr(t, t0 + 0.6 + i * 0.1, t0 + 1.2 + i * 0.1))
        r_ = 260 * g + 140 * (1 - k)
        px, py = 540 + math.cos(u) * r_, 800 + math.sin(u) * r_
        d.circ(px, py, 32, fill=A(GOLD, k)); d.circ(px - 8, py - 6, 6, fill=A(NOSE, k)); d.circ(px + 8, py - 6, 6, fill=A(NOSE, k))
    ptag(d, t, t0 + 0.4, 540, 420, "防冻蛋白", GOLD, 40, tc=NAVYT)
    ptag(d, t, t0 + 2.4, 540, 1160, "冰晶长不大", (180, 230, 255), 38, tc=NAVYT)
def s_gene(t, d):
    t0 = T["gene"]
    flatbg(d, (20, 60, 100), (6, 20, 40), t, False)
    snowfly(d, 300, 780, 0.9, t, walk=0.2)
    fx_ = 790; fy = 780 + 10 * math.sin(t * 2)
    d.ell(fx_, fy, 130, 60, A((150, 180, 210), 1)); d.poly([(fx_ + 120, fy), (fx_ + 200, fy - 60), (fx_ + 200, fy + 60)], A((150, 180, 210), 1))
    d.circ(fx_ - 80, fy - 10, 12, fill=A(WHITE, 1)); d.circ(fx_ - 80, fy - 10, 6, fill=A(NOSE, 1))
    for i, x in enumerate((300, 790)):
        k = popk(t, t0 + 0.5 + i * 0.3, "bouncy")
        if k > 0: d.circ(x, 560, 40 * min(1, k), fill=A(GOLD, 1)); d.circ(x - 10, 552, 7, fill=A(NOSE, 1)); d.circ(x + 10, 552, 7, fill=A(NOSE, 1))
    e = pr(t, t0 + 1.4, t0 + 2.2)
    if e > 0:
        d.arc(545, 560, 245, 120 * e, 180, 360, A((255, 120, 160), 1), 8)
        if e >= 1: heart(d, 545, 430, 34, (255, 120, 160))
    ptag(d, t, t0 + 0.2, 300, 1000, "雪蝇", WHITE, 36, tc=NAVYT); ptag(d, t, t0 + 0.4, 790, 1000, "北极鱼", WHITE, 36, tc=NAVYT)
def s_why(t, d):
    t0 = T["why"]
    flatbg(d, (250, 236, 220), (220, 200, 180), t, False)
    rows = (("果蝇", 30, (150, 150, 170)), ("蚊子", 30, (120, 140, 180)), ("雪蝇", 1, (255, 120, 60)))
    for i, (nm, v, c) in enumerate(rows):
        y = 620 + i * 170; e = ease(pr(t, t0 + 0.3 + i * 0.4, t0 + 0.9 + i * 0.4))
        d.text(250, y - 26, nm, 40, A(NAVYT, 1), k=1)
        if e > 0: d.rect(340, y - 40, 340 + max(20, 560 * v / 30 * e), y + 40, fill=A(c, 1), r=20)
    ptag(d, t, t0 + 0.2, 540, 450, "冷刺痛受体 灵敏度", NAVYT, 36, tc=WHITE)
    ptag(d, t, t0 + 2.0, 620, 960, "×1/30", (255, 120, 60), 44, tc=WHITE)
def s_order(t, d):
    t0 = T["order"]
    m = ease(pr(t, t0 + 0.2, t0 + 1.6))
    flatbg(d, (int(150 + 60 * m), 190, int(230 - 80 * m)), (int(90 + 60 * m), 140, 110), t, False)
    d.rect(0, 1100 + 120 * m, OW, OH, fill=A((240, 246, 252), 1))
    d.circ(820, 380, 80 + 20 * m, fill=A((255, 220, 90), m))
    x = 540 - 300 * ease(pr(t, t0 + 1.4, t0 + 2.8))
    snowfly(d, x, 1000, 1.1, t, walk=1.4, face="cold", flip=-1)
    d.ell(160, 1100, 200, 120, A((90, 80, 70), 1))
    ptag(d, t, t0 + 1.0, 820, 560, "雪化了", (255, 150, 60), 38, tc=WHITE)
def s_card(t, d):
    flatbg(d, (60, 90, 130), (16, 26, 46), t, False)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    snowfly(d, cx_, cy_ - 170, 0.7, t, a=a_, walk=0.3)
    d.text(cx_, cy_ + 10, "雪蝇：零下6度照样出门", 42, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("自己产热，不靠发抖", "防冻蛋白挡住冰晶", "对冷刺痛很迟钝")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 120 + i * 78, s_, 38, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    snowfield(d, t)
    snowfly(d, 380, 980, 1.0, t, walk=0.5, heat=0.3)
    snowfly(d, 700, 980, 1.0, t + 1, walk=0.5, heat=0.3, flip=-1, scarf=False)
    if t > t0 + 1.0: heart(d, 540, 800 - 20 * math.sin(t * 2), 40, (255, 110, 140))
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 285, "Capek et al. 2026", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 330, "Current Biology · 雪蝇 Chionea alexandriana", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

