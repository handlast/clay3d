def screen(d, *a, **k): pass
def s_hook(t, d):
    snowbg(d, t, (20, 30, 60), (70, 95, 140))
    if t < 0.3: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.7 * (1 - t / 0.3)))
    k = popk(t, 0.0, "bouncy")
    simo(d, 600, 1110, 1.3 * min(1.05, max(0.4, k)), t, face="aim", breath=0.0)
    thermo2(d, 880, 640, max(0.05, 0.9 - 0.85 * ease(pr(t, 0.2, 1.2))))
    kk = popk(t, 0.3, "bouncy")
    if kk > 0: d.text(440, 520, "-40°", int(220 * min(1, kk)), A((150, 210, 255), 1), k=1)
    ptag(d, t, 1.4, 440, 700, "一趴一整天", GOLD, 50)
def s_q(t, d):
    t0 = T["q"]
    flatbg(d, (230, 238, 250), (180, 196, 222), t, False)
    k = popk(t, t0 + 0.1, "smooth")
    if k > 0:
        a_ = ap(t, t0 + 0.1)
        d.rect(230, 420, 850, 1180, fill=A((24, 32, 52), a_), r=36)
        simo(d, 540, 700, 2.4 * (0.85 + 0.15 * k), t, a_, pose="stand")
        d.text(540, 1000, "西莫·海耶", 56, A(WHITE, a_), k=1)
        d.text(540, 1070, "芬兰 · 狙击手", 32, A((180, 196, 222), a_), k=1)
    kk = popk(t, t0 + 1.2, "bouncy")
    if kk > 0: tag(d, 540, 360, "白色死神", (230, 70, 70), min(1, kk), 64, tc=WHITE)
def s_who(t, d):
    t0 = T["who"]
    snowbg(d, t, (60, 80, 120), (150, 170, 205))
    k = popk(t, t0 + 0.1, "bouncy")
    if k > 0:
        w = 260 * min(1, k)
        d.rect(540 - w, 420, 540 + w, 620, fill=A(WHITE, 1), r=24)
        d.rect(540 - w, 420, 540 + w, 490, fill=A((60, 110, 200), 1), r=24)
        d.text(540, 455, "冬季战争", 36, A(WHITE, 1), k=1); d.text(540, 560, "1939–1940", 64, A(NAVYT, 1), k=1)
    for i in range(5):
        x = 200 + i * 170; kk = popk(t, t0 + 1.0 + i * 0.15, "bouncy")
        if kk > 0: simo(d, x, 1000, 0.55 * min(1, kk), t + i, pose="stand")
    ptag(d, t, t0 + 2.0, 540, 760, "芬兰 vs 苏联", GOLD, 44)
def s_sperm(t, d):
    t0 = T["sperm"]
    snowbg(d, t, (90, 120, 170), (190, 210, 235), pines=False)
    hide = ease(pr(t, t0 + 1.8, t0 + 2.6))
    if hide < 1:
        simo(d, 420, 760, 1.4, t, 1 - hide, pose="stand")
        d.line([(640, 1150), (640, 700)], A(NAVYT, 1 - hide), 6)
        for yy in (700, 1150): d.line([(620, yy), (660, yy)], A(NAVYT, 1 - hide), 6)
        d.text(740, 920, "1.6米", 56, A(NAVYT, (1 - hide) * ap(t, t0 + 0.4)), k=1)
    if hide > 0:
        simo(d, 560, 1140, 1.2, t, 0.25 + 0.15 * math.sin(t * 2), face="aim")
        ptag(d, t, t0 + 2.4, 540, 900, "找到他了吗？", WHITE, 44)
def s_egg(t, d):
    t0 = T["egg"]
    dim = 1 - 0.45 * pr(t, SIL0, SIL0 + 0.15)
    snowbg(d, t, (10, 16, 30), (40, 55, 85), flakes=True)
    simo(d, 560, 1100, 1.3, t, dim, face="aim", breath=dim)
    k = popk(t, t0 + 0.5, "bouncy")
    if k > 0:
        d.circ(780, 960, 120 * min(1, k), outline=A((255, 90, 90), dim), w=8)
        d.text(860, 760, "?", int(160 * min(1, k)), A(GOLD, dim), k=1)
    ptag(d, t, t0 + 1.4, 540, 560, "白气会暴露", (255, 90, 90), 44, tc=WHITE)
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (200, 230, 255), (40, 80, 150))
    if t > t0: sparks(d, 540, 760, t, t0, 40, 1000, (230, 245, 255), 1, 3, 0.9)
    ch = ease(pr(t, t0 + 0.2, t0 + 0.7))
    simo(d, 540, 760, 3.0, t, pose="stand", cheeks=ch)
    for i in range(6):
        u = 1 - ease(pr(t, t0 + 0.05 + i * 0.04, t0 + 0.5 + i * 0.04))
        if u > 0: d.circ(560 + 300 * u * math.cos(i), 840 - 260 * u, 18, fill=A(WHITE, 1))
    ptag(d, t, t0 + 0.4, 540, 330, "含雪", GOLD, 90)
def s_how(t, d):
    t0 = T["how"]
    snowbg(d, t, (30, 45, 80), (90, 115, 160), pines=False)
    d.line([(540, 600), (540, 1200)], A(WHITE, 0.6), 4)
    simo(d, 300, 900, 0.8, t, face="aim", breath=1.0)
    simo(d, 780, 900, 0.8, t, face="aim", cheeks=1.0, breath=0.0)
    k1 = popk(t, t0 + 0.6, "bouncy"); k2 = popk(t, t0 + 1.2, "bouncy")
    if k1 > 0: tag(d, 300, 640, "冒白气 ✕".replace(" ✕", ""), (230, 70, 70), min(1, k1), 40, tc=WHITE)
    if k2 > 0: tag(d, 780, 640, "含雪 · 不冒", (60, 180, 110), min(1, k2), 40, tc=WHITE)
def s_xray(t, d):
    t0 = T["xray"]
    snowbg(d, t, (60, 80, 120), (160, 180, 215), pines=False)
    packed = t > t0 + 2.2
    simo(d, 520, 1000, 1.2, t, face="aim")
    d.ell(830, 1060, 120, 50 + (10 if packed else 0), A(SNOWC if not packed else (220, 230, 246), 1))
    shot = (t - t0) % 1.1 < 0.25 and t > t0 + 0.5
    if shot and not packed:
        for i in range(14):
            d.circ(840 + 20 * math.cos(i), 980 - 40 * ((t - t0) % 1.1) * 10 * (0.3 + (i % 3) * 0.3), 18, fill=A(WHITE, 0.85))
    if shot: d.circ(1000, 1000, 16, fill=A((255, 230, 120), 1))
    tag(d, 540, 600, "压实雪堆" if packed else "松雪会扬起", (60, 180, 110) if packed else (230, 70, 70), ap(t, t0 + 0.3), 44, tc=WHITE)
def s_swim(t, d):
    t0 = T["swim"]
    snowbg(d, t, (30, 45, 80), (110, 135, 180), pines=False, flakes=True)
    fog = ease(pr(t, t0 + 0.4, t0 + 1.4)); gl = abs(math.sin(t * 3)) * ap(t, t0 + 0.8)
    scope(d, 300, 820, 170, fog=fog, glint=gl)
    d.text(300, 1060, "瞄准镜", 44, A(WHITE, 1), k=1)
    tag(d, 300, 560, "起雾 · 反光", (230, 70, 70), ap(t, t0 + 1.0), 36, tc=WHITE)
    k = popk(t, t0 + 1.6, "bouncy")
    if k > 0:
        kk = min(1, k)
        d.rect(640, 800, 960, 830, fill=A((70, 74, 84), kk), r=8)
        d.poly([(900, 800), (920, 750), (940, 800)], A((70, 74, 84), kk))
        d.rect(660, 770, 700, 800, fill=A((70, 74, 84), kk))
        d.text(800, 1060, "铁瞄", 44, A(WHITE, kk), k=1)
        tag(d, 800, 560, "不起雾", (60, 180, 110), kk, 36, tc=WHITE)
def s_gene(t, d):
    t0 = T["gene"]
    flatbg(d, (230, 238, 250), (180, 196, 222), t, False)
    simo(d, 540, 640, 1.6, t, pose="stand")
    items = [(300, 1080, "s"), (420, 1130, "s"), (680, 1100, "b"), (800, 1070, "s")]
    for i, (x, y, kd) in enumerate(items):
        k = popk(t, t0 + 0.3 + i * 0.35, "bouncy")
        if k <= 0: continue
        (sugar if kd == "s" else bread)(d, x, y, 1.3 * min(1, k))
    e = ease(pr(t, t0 + 1.8, t0 + 3.2))
    d.rect(240, 1200, 840, 1240, fill=A((40, 50, 70), 1), r=20)
    d.rect(240, 1200, 240 + 600 * e, 1240, fill=A((255, 150, 60), 1), r=20)
    ptag(d, t, t0 + 1.6, 540, 360, "补热量", GOLD, 54)
def s_why(t, d):
    t0 = T["why"]
    flatbg(d, (24, 32, 52), (10, 14, 26), t, False)
    e1 = ease(pr(t, t0 + 0.2, t0 + 1.4)); e2 = ease(pr(t, t0 + 1.4, t0 + 2.6))
    d.rect(150, 560, 520, 960, fill=A((40, 54, 84), 1), r=30); d.rect(560, 560, 930, 960, fill=A((40, 54, 84), 1), r=30)
    d.text(335, 620, "军方记录", 36, A((180, 196, 222), 1), k=1); d.text(745, 620, "他的回忆录", 36, A((180, 196, 222), 1), k=1)
    d.text(335, 780, str(int(259 * e1)), 120, A(WHITE, 1), k=1); d.text(745, 780, "约" + str(int(500 * e2)), 100, A(WHITE, 1), k=1)
    ptag(d, t, t0 + 2.6, 540, 1080, "数字有争议", (230, 150, 60), 44, tc=WHITE)
    ptag(d, t, t0 + 0.4, 540, 440, "不到100天", GOLD, 44)
def s_order(t, d):
    t0 = T["order"]
    flatbg(d, (40, 30, 40), (14, 10, 18), t, False)
    k = popk(t, t0 + 0.1, "bouncy")
    if k > 0:
        w = 240 * min(1, k)
        d.rect(540 - w, 420, 540 + w, 620, fill=A(WHITE, 1), r=24); d.rect(540 - w, 420, 540 + w, 490, fill=A((200, 60, 60), 1), r=24)
        d.text(540, 455, "1940", 36, A(WHITE, 1), k=1); d.text(540, 560, "3月6日", 64, A(NAVYT, 1), k=1)
    hit = t0 + 1.3
    if hit < t < hit + 0.12: d.rect(0, 0, OW, OH, fill=A((255, 240, 240), 0.5))
    simo(d, 540, 900, 1.6, t, pose="stand", bandage=ease(pr(t, hit + 0.4, hit + 1.0)), face="calm")
    ptag(d, t, hit + 1.4, 540, 1180, "一周后醒来，正好停战", GOLD, 36)
def s_card(t, d):
    flatbg(d, (60, 80, 120), (20, 30, 50), t, False)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    simo(d, cx_, cy_ - 190, 1.0, t, a_, pose="stand")
    d.text(cx_, cy_ + 60, "雪地隐身三招", 44, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("嘴里含雪：不冒白气", "压实雪堆：开枪不扬雪", "用铁瞄：不起雾不反光")):
        kk = ap(t, at("card", 1.5 + i * 2.0), 0.25)
        if kk > 0: d.text(cx_, cy_ + 160 + i * 78, s_, 36, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    snowbg(d, t, (120, 150, 190), (210, 225, 240))
    simo(d, 420, 820, 1.3, t, pose="stand", old=True)
    dog(d, 740, 1080, 1.1, t)
    k = popk(t, t0 + 1.2, "bouncy")
    if k > 0: tag(d, 600, 560, "“练习。”", WHITE, min(1, k), 60)
    ra = ap(t, t0 + 2.6, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 285, "资料：Saarelainen《The White Sniper》2016", 24, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 330, "芬兰JR34团作战记录", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

