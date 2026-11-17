def screen(d, *a, **k): pass
def bugs_on_web(d, t, cx, cy, R, n, s, a=1.0, seed=3, spd=0.25, orbit=False):
    rr = random.Random(seed)
    for i in range(n):
        r0 = R * rr.uniform(0.3, 0.95); an = rr.uniform(0, 6.28) + (t * spd * (1 if i % 2 else -0.7) if orbit else 0)
        if not orbit:
            r0 = R * (0.3 + 0.6 * ((rr.random() + t * 0.05 * (1 + i % 3)) % 1))
            an = round(an / (2 * math.pi / 12)) * (2 * math.pi / 12)
        webbug(d, cx + r0 * math.cos(an), cy + r0 * math.sin(an), s, t + i, a)
def s_hook(t, d):
    forest_bg(d, t)
    if t < 0.3: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - t / 0.3)))
    web(d, 540, 820, 470, 1, t=t)
    k = popk(t, 0.0, "bouncy")
    spider(d, 540, 760, 1.25 * min(1.05, max(0.3, k)), t)
    for i in range(5):
        kk = popk(t, 0.3 + i * 0.25, "bouncy")
        if kk > 0:
            an = i * 1.25 + t * 0.4; r0 = 330
            webbug(d, 540 + r0 * math.cos(an), 820 + r0 * math.sin(an) * 0.9, 1.1 * min(1, kk), t + i)
    ptag(d, t, 1.6, 540, 1240, "不吃？", GOLD, 60)
def s_q(t, d):
    t0 = T["q"]
    flatbg(d, (230, 236, 246), (190, 200, 220), t, False)
    k = popk(t, t0 + 0.2, "bouncy")
    salt(d, 360, 820, 130 * min(1, k))
    k2 = popk(t, t0 + 0.8, "bouncy")
    if k2 > 0: webbug(d, 730, 830, 2.6 * min(1, k2), t)
    d.text(360, 1010, "盐粒", 44, A(NAVYT, ap(t, t0 + 0.3)), k=1); d.text(720, 1010, "新虫", 44, A(BUGR, ap(t, t0 + 0.9)), k=1)
    e = ease(pr(t, t0 + 1.4, t0 + 2.0))
    if e > 0:
        d.line([(600, 1090), (600 + 260 * e, 1090)], A(NAVYT, 1), 8)
        for xx in (600, 600 + 260 * e): d.line([(xx, 1070), (xx, 1110)], A(NAVYT, 1), 6)
        d.text(730, 1140, "约1毫米", 40, A(NAVYT, e), k=1)
    ptag(d, t, t0 + 0.1, 540, 560, "放大约50倍", NAVYT, 32, tc=WHITE)
def s_who(t, d):
    t0 = T["who"]
    forest_bg(d, t, (60, 110, 80), (20, 44, 34))
    web(d, 540, 940, 380, 0.8)
    for i in range(3): webbug(d, 540 + 160 * math.cos(i * 2.1 + t * 0.3), 940 + 160 * math.sin(i * 2.1 + t * 0.3), 0.7, t + i)
    k = popk(t, t0 + 0.1, "bouncy")
    if k > 0:
        cx_, cy_ = 540, 520; w = 230 * min(1, k)
        d.rect(cx_ - w, cy_ - 80, cx_ + w, cy_ + 90, fill=A(WHITE, 1), r=24)
        d.rect(cx_ - w, cy_ - 80, cx_ + w, cy_ - 20, fill=A((230, 80, 70), 1), r=24)
        d.text(cx_, cy_ - 50, "2025", 36, A(WHITE, 1), k=1); d.text(cx_, cy_ + 35, "9月", 64, A(NAVYT, 1), k=1)
    ptag(d, t, t0 + 1.4, 540, 1240, "福建 · 野外调查", GOLD, 38)
    mx = 540 + 260 * math.cos(t * 1.4); my = 940 + 120 * math.sin(t * 1.9)
    d.circ(mx, my, 90, outline=A(WHITE, 0.9), w=12); d.line([(mx + 64, my + 64), (mx + 140, my + 140)], A(WHITE, 0.9), 16)
def s_sperm(t, d):
    t0 = T["sperm"]
    flatbg(d, (255, 240, 220), (240, 200, 170), t, False)
    k = popk(t, t0 + 0.1, "smooth")
    if k > 0:
        a_ = ap(t, t0 + 0.1)
        d.rect(220, 420, 860, 1180, fill=A(WHITE, a_), r=36)
        tag(d, 540, 480, "新物种", (230, 80, 70), a_, 40, tc=WHITE)
        webbug(d, 540, 760, 4.0 * (0.85 + 0.15 * k), t, a_)
        d.text(540, 1000, "Heissophila", 48, A(NAVYT, a_), k=1); d.text(540, 1060, "sinica", 48, A(NAVYT, a_), k=1)
        d.text(540, 1125, "网栖蝽 · 同属第2种", 30, A((90, 90, 110), ap(t, t0 + 1.4)), k=1)
def s_egg(t, d):
    t0 = T["egg"]
    dim = 1 - 0.45 * pr(t, SIL0, SIL0 + 0.15)
    flatbg(d, (30, 40, 50), (8, 12, 18), t, False)
    web(d, 540, 860, 420, 0.5 * dim)
    webbug(d, 540, 860, 2.2, t, dim, walk=0.3)
    k = popk(t, t0 + 0.5, "bouncy")
    if k > 0: d.text(700, 650, "?", int(160 * min(1, k)), A(GOLD, dim), k=1)
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (255, 200, 90), (200, 90, 60))
    if t > t0: sparks(d, 540, 820, t, t0, 30, 900, (255, 240, 200), 1, 3, 0.9)
    spider(d, 540, 640, 0.9, t, eat=1.0)
    d.ell(540, 760, 40, 26, A((90, 80, 70), 1))      # prey (fly) in mouth
    for i in range(6):
        u = ((t - t0) * 0.8 + i / 6) % 1
        cx_, cy_ = 540 + (i - 2.5) * 60, 820 + u * 360
        d.circ(cx_, cy_, 10, fill=A((150, 120, 100), 1 - u * 0.5))
    for i in range(4):
        kk = popk(t, t0 + 0.3 + i * 0.15, "bouncy")
        if kk > 0: webbug(d, 300 + i * 160, 1180, 1.4 * min(1, kk), t + i, sip=abs(math.sin(t * 10 + i)))
    ptag(d, t, t0 + 0.5, 540, 340, "剩饭", GOLD, 70)
def s_how(t, d):
    t0 = T["how"]
    forest_bg(d, t, (50, 80, 90), (16, 30, 36))
    web(d, 540, 860, 440, 0.8)
    for i in range(5):
        an = i * 1.256; mx, my = 540 + 260 * math.cos(an), 860 + 260 * math.sin(an)
        eaten = t > t0 + 0.8 + i * 0.5
        if not eaten: mite(d, mx, my, 1.4)
        else: sparks(d, mx, my, t, t0 + 0.8 + i * 0.5, 8, 200, (220, 220, 230), 1, i, 0.4)
        bx = lerp(540 + 420 * math.cos(an), mx - 50, ease(pr(t, t0 + 0.2 + i * 0.5, t0 + 0.8 + i * 0.5)))
        by = lerp(860 + 420 * math.sin(an), my, ease(pr(t, t0 + 0.2 + i * 0.5, t0 + 0.8 + i * 0.5)))
        webbug(d, bx, by, 1.0, t + i)
    ptag(d, t, t0 + 0.3, 540, 420, "螨虫", (200, 200, 210), 40)
    ptag(d, t, t0 + 2.0, 540, 1250, "有些寄生蜘蛛", (230, 80, 70), 36, tc=WHITE)
def s_xray(t, d):
    t0 = T["xray"]
    forest_bg(d, t, (70, 60, 100), (24, 18, 40))
    web(d, 540, 860, 460, 0.7)
    m = ease(pr(t, t0 + 0.2, t0 + 1.4))
    spider(d, 540, 820, 0.9, t, molt=m)
    for i in range(6):
        an = i * 1.047 + 0.3
        e = ease(pr(t, t0 + 1.2 + i * 0.12, t0 + 2.2 + i * 0.12))
        r0 = lerp(440, 200, e)
        webbug(d, 540 + r0 * math.cos(an), 900 + r0 * math.sin(an) * 0.8, 1.0, t + i, sip=e * abs(math.sin(t * 9 + i)))
    ptag(d, t, t0 + 0.3, 540, 380, "蜕皮", GOLD, 50)
    for i in range(4):
        if t > t0 + 2.4: d.circ(540 + (i - 1.5) * 70, 1010 + 20 * math.sin(t * 6 + i), 10, fill=A((150, 220, 255), 0.8))
def s_swim(t, d):
    t0 = T["swim"]
    forest_bg(d, t, (60, 100, 80), (18, 36, 30))
    web(d, 540, 860, 460, 0.7)
    an = (t - t0) * 1.3
    sx, sy = 540 + 170 * math.cos(an), 860 + 170 * math.sin(an)
    spider(d, sx, sy - 40, 0.65, t, walk=1.0)
    for i in range(5):
        a2 = an - 0.55 - i * 0.38 + 0.15 * math.sin(t * 3 + i)
        webbug(d, 540 + 340 * math.cos(a2), 860 + 340 * math.sin(a2), 0.9, t + i)
    ptag(d, t, t0 + 0.3, 540, 330, "跟着绕圈", GOLD, 46)
    ptag(d, t, t0 + 1.4, 540, 1300 - 40, "原因还不清楚", WHITE, 32)
def s_gene(t, d):
    t0 = T["gene"]
    flatbg(d, (230, 236, 246), (190, 200, 220), t, False)
    spider(d, 540, 760, 1.6, t)
    webbug(d, 540 + 30 * math.sin(t * 2), 1160, 0.7, t)
    k = popk(t, t0 + 0.6, "bouncy")
    if k > 0:
        d.circ(540, 1160, 70 * min(1, k), outline=A((230, 80, 70), 1), w=6)
        tag(d, 760, 1120, "太小了", (230, 80, 70), min(1, k), 40, tc=WHITE)
    ptag(d, t, t0 + 1.5, 540, 360, "可能", NAVYT, 40, tc=WHITE)
def s_why(t, d):
    t0 = T["why"]
    forest_bg(d, t, (50, 90, 80), (16, 30, 30))
    d.line([(150, 860), (930, 860)], A((235, 240, 255), 0.8), 5)
    items = [(300, "卵"), (540, "小虫"), (780, "成虫")]
    for i, (x, lab) in enumerate(items):
        k = popk(t, t0 + 0.3 + i * 0.6, "bouncy")
        if k <= 0: continue
        kk = min(1, k)
        if i == 0:
            for j in range(3): d.ell(x - 30 + j * 30, 850, 16 * kk, 22 * kk, A((255, 240, 210), 1))
        else: webbug(d, x, 840, (0.9 if i == 1 else 1.5) * kk, t + i)
        d.text(x, 960, lab, 44, A(WHITE, kk), k=1)
    ptag(d, t, t0 + 2.2, 540, 600, "同一张网", GOLD, 46)
def s_order(t, d):
    t0 = T["order"]
    forest_bg(d, t, (70, 110, 90), (20, 40, 34))
    k = popk(t, t0 + 0.1, "smooth")
    web(d, 540, 820, 380 * (0.8 + 0.2 * min(1, k)), 0.9)
    d.poly([(400, 640), (540, 520), (680, 640)], A((255, 200, 120), 0.85 * ap(t, t0 + 0.4)))
    for i in range(4):
        an = i * 1.57 + t * 0.5
        webbug(d, 540 + 200 * math.cos(an), 860 + 200 * math.sin(an), 0.9, t + i)
    ptag(d, t, t0 + 1.0, 540, 1250, "网 = 家", GOLD, 50)
def s_card(t, d):
    flatbg(d, (90, 130, 110), (30, 60, 50), t, False)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    webbug(d, cx_, cy_ - 150, 2.0, t, a_)
    d.text(cx_, cy_ + 20, "网栖蝽：住在蜘蛛网上的虫", 40, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("约1毫米，像一粒盐", "吃剩饭、吃螨虫", "蜘蛛蜕皮时喝体液")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 130 + i * 78, s_, 38, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    forest_bg(d, t)
    d.line([(100, 900), (980, 900)], A((235, 240, 255), 0.9), 8)
    x = 540 + 60 * math.sin((t - t0) * 0.8)
    webbug(d, x, 860, 4.2, t)
    k = popk(t, t0 + 0.8, "bouncy")
    if k > 0:
        d.circ(x - 20, 990, 90 * min(1, k), outline=A(GOLD, 1), w=8)
        d.text(x + 140, 1060, "?", int(110 * min(1, k)), A(GOLD, 1), k=1)
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 285, "Xiong et al. 2026", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 330, "ZooKeys 1296: 11–25", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

