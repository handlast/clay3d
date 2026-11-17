def screen(d, *a, **k): pass
def room(d, t, top=(255, 226, 180), bot=(232, 180, 130), floor=(210, 150, 100)):
    flatbg(d, top, bot, t, False)
    d.rect(0, 1150, OW, OH, fill=A(floor, 0.55))
def mw(t, t0, per=0.62, n=99):
    """meow mouth envelope: pulses starting at t0"""
    if t < t0: return 0.0
    k = int((t - t0) / per)
    if k >= n: return 0.0
    u = ((t - t0) % per) / per
    return math.sin(math.pi * min(1, u / 0.6)) if u < 0.6 else 0.0
def s_hook(t, d):
    room(d, t, (255, 200, 120), (240, 140, 80))
    if t < 0.3: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - t / 0.3)))
    k = popk(t, 0.0, "bouncy")
    m = mw(t, 0.05, 0.7)
    orangecat(d, 540, 880, 1.8 * min(1.05, max(0.3, k)), t, meow=m)
    for i in range(3):
        kk = popk(t, 0.15 + i * 0.7, "bouncy")
        if kk > 0: meowbub(d, (330, 760, 380)[i], (430, 520, 620)[i], 52 * min(1, kk), min(1, kk) * (1 - 0.6 * pr(t, 0.9 + i * 0.7, 1.4 + i * 0.7)))
    ptag(d, t, 1.6, 540, 1120, "求助？", GOLD, 60)
def s_q(t, d):
    t0 = T["q"]
    room(d, t)
    lid = ease(pr(t, t0 + 1.3, t0 + 1.9))
    treatbox(d, 700, 1000, 1.3, lid=lid, t=t)
    orangecat(d, 330, 960, 1.0, t, look=1)
    if lid >= 1:
        k = popk(t, t0 + 1.9, "bouncy")
        d.rect(660, 800 - 30 * k, 740, 860, fill=A(GOLD, min(1, k)), r=12); d.arc(700, 800, 30, 40, 180, 360, A(GOLD, min(1, k)), 10)
    ptag(d, t, t0 + 0.3, 700, 760, "猫最爱的零食", (255, 120, 90), 34, tc=WHITE)
def s_who(t, d):
    t0 = T["who"]
    flatbg(d, (250, 236, 220), (226, 206, 186), t, False)
    n = int(38 * ease(pr(t, t0 + 0.2, t0 + 1.8)))
    for i in range(38):
        if i >= n: break
        cx_, cy_ = 250 + (i % 7) * 97, 520 + (i // 7) * 105
        d.circ(cx_, cy_, 36, fill=A(ORG if i % 3 else (150, 156, 170) if i % 2 else (90, 80, 70), 1))
        for sd in (-1, 1): d.circ(cx_ + sd * 26, cy_ - 30, 13, fill=A(ORG if i % 3 else (150, 156, 170) if i % 2 else (90, 80, 70), 1))
        d.circ(cx_ - 12, cy_ - 2, 5, fill=A(NOSE, 1)); d.circ(cx_ + 12, cy_ - 2, 5, fill=A(NOSE, 1))
    ptag(d, t, t0 + 0.1, 540, 400, "%d 只猫" % n, NAVYT, 44, tc=WHITE)
    ptag(d, t, t0 + 2.0, 540, 1160, "每场 1 分钟", GOLD, 38)
def s_sperm(t, d):
    t0 = T["sperm"]
    flatbg(d, (240, 236, 226), (210, 204, 190), t, False)
    d.line([(540, 480), (540, 1180)], A(NAVYT, 0.3), 6)
    kL = popk(t, t0 + 0.2, "bouncy"); kR = popk(t, t0 + 1.6, "bouncy")
    if kL > 0:
        owner(d, 300, 900, 0.75 * min(1, kL)); treatbox(d, 400, 1080, 0.5, t=t); orangecat(d, 260, 1070, 0.45, t, look=1)
        tag(d, 360, 520, "主人在", (90, 140, 220), min(1, kL), 38, tc=WHITE)
    if kR > 0:
        door(d, 780, 1000, 0.8, open_=0.2); treatbox(d, 860, 1080, 0.5, t=t); orangecat(d, 700, 1070, 0.45, t)
        tag(d, 780, 520, "主人走", (255, 110, 90), min(1, kR), 38, tc=WHITE)
def s_egg(t, d):
    t0 = T["egg"]
    dim = 1 - 0.45 * pr(t, SIL0, SIL0 + 0.15)
    flatbg(d, (40, 40, 70), (12, 12, 26), t, False)
    for i, (x, lab, c) in enumerate(((340, "主人在", (90, 140, 220)), (740, "主人走", (255, 110, 90)))):
        d.rect(x - 90, 560, x + 90, 1060, fill=A(WHITE, 0.08 * dim), r=20)
        d.text(x, 1110, lab, 40, A(c, dim), k=1)
        k = popk(t, t0 + 0.5 + i * 0.3, "bouncy")
        if k > 0: d.text(x, 800, "?", int(150 * min(1, k)), A(GOLD, dim), k=1)
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (255, 200, 90), (230, 110, 50))
    if t > t0: sparks(d, 540, 820, t, t0, 30, 900, (255, 240, 200), 1, 3, 0.9)
    e = ease(pr(t, t0 + 0.05, t0 + 0.9))
    base = 1120
    d.rect(250, base - 560 * e, 450, base, fill=A((90, 140, 220), 1), r=16)
    d.rect(630, base - 35 * e, 830, base, fill=A((255, 110, 90), 1), r=12)
    d.text(350, 1170, "主人在", 38, A(NAVYT, 1), k=1); d.text(730, 1170, "主人走", 38, A(NAVYT, 1), k=1)
    k = popk(t, t0 + 0.6, "bouncy")
    if k > 0:
        tag(d, 540, 420, "≈16倍" if False else "约16倍", GOLD, min(1, k), 70)
        orangecat(d, 350, base - 560 * e - 120, 0.5, t, meow=mw(t, t0 + 0.6, 0.5))
def s_how(t, d):
    t0 = T["how"]
    room(d, t, (226, 240, 255), (180, 210, 240), (150, 180, 210))
    owner(d, 790, 1100, 1.0)
    orangecat(d, 330, 1020, 0.9, t, look=1, meow=mw(t, t0 + 0.5, 0.75))
    e = pr(t, t0 + 0.6, t0 + 1.4)
    gaze(d, 370, 900, 760, 830, GOLD, 1, e, t)
    k = popk(t, t0 + 1.2, "bouncy")
    if k > 0:
        r = 110; cx_, cy_ = 540, 540
        d.circ(cx_, cy_, r * min(1, k), fill=A(WHITE, 1))
        d.pie(cx_, cy_, r * min(1, k), -90, -90 + 360 * 0.56 * ease(pr(t, t0 + 1.4, t0 + 2.4)), A(GOLD, 1)) if hasattr(d, "pie") else None
        d.text(cx_, cy_ + 165, "约56%", 52, A(NAVYT, 1), k=1)
def s_xray(t, d):
    t0 = T["xray"]
    room(d, t, (226, 240, 255), (180, 210, 240), (150, 180, 210))
    owner(d, 830, 1100, 0.9)
    treatbox(d, 300, 1120, 0.7, t=t)
    ph = int((t - t0) / 0.9) % 2
    lk = 1 if ph == 0 else -1
    orangecat(d, 560, 1060, 0.8, t, look=lk)
    if ph == 0: gaze(d, 600, 940, 800, 860, GOLD, 1, 1, t)
    else: gaze(d, 520, 960, 330, 1050, (255, 120, 90), 1, 1, t)
    d.text(540, 600, "主人 ⇄ 盒子" if False else "主人  ↔  盒子", 56, A(NAVYT, 1), k=1)
def s_swim(t, d):
    t0 = T["swim"]
    room(d, t, (226, 240, 255), (180, 210, 240), (150, 180, 210))
    owner(d, 820, 1100, 0.9)
    treatbox(d, 300, 1120, 0.7, t=t)
    orangecat(d, 560, 1060, 0.8, t, look=-1, meow=mw(t, t0 + 0.3, 0.8, 3))
    gaze(d, 520, 960, 330, 1050, (255, 120, 90), 1, 1, t)
    e = pr(t, t0 + 1.2, t0 + 2.2)
    gaze(d, 800, 830, 360, 1040, (90, 140, 220), 1, e, t)
    ptag(d, t, t0 + 0.5, 540, 560, "像是在说：看那个盒子！", WHITE, 40)
def s_gene(t, d):
    t0 = T["gene"]
    room(d, t, (200, 196, 214), (150, 146, 170), (120, 116, 140))
    door(d, 780, 1150, 1.0, open_=0.0)
    treatbox(d, 300, 1150, 0.6, t=t)
    orangecat(d, 520, 1080, 0.8, t, look=1, face="flat" if True else "happy", tail=0.2)
    gaze(d, 560, 960, 730, 900, WHITE, 0.6, pr(t, t0 + 0.6, t0 + 1.4), t)
    ptag(d, t, t0 + 1.4, 540, 560, "……", WHITE, 60)
def s_why(t, d):
    t0 = T["why"]
    flatbg(d, (60, 60, 90), (24, 24, 40), t, False)
    orangecat(d, 540, 960, 1.1, t)
    k = popk(t, t0 + 0.5, "bouncy")
    if k > 0:
        d.circ(780, 600, 110 * min(1, k), fill=A(WHITE, 1)); d.circ(690, 720, 24 * min(1, k), fill=A(WHITE, 1)); d.circ(650, 770, 14 * min(1, k), fill=A(WHITE, 1))
        d.text(780, 600, "故意？", int(52 * min(1, k)), A(NAVYT, 1), k=1)
    ptag(d, t, t0 + 1.6, 540, 1180, "未证明", (255, 110, 90), 44, tc=WHITE)
def s_order(t, d):
    t0 = T["order"]
    room(d, t)
    cx_, cy_ = 300, 560
    d.circ(cx_, cy_, 120, fill=A(WHITE, 1)); d.circ(cx_, cy_, 120, outline=A(NAVYT, 0.3), width=6) if False else None
    for i in range(12):
        an = i / 12 * 2 * math.pi; d.circ(cx_ + 96 * math.sin(an), cy_ - 96 * math.cos(an), 6, fill=A(NAVYT, 0.6))
    an = (t - t0) * 2
    d.line([(cx_, cy_), (cx_ + 70 * math.sin(an), cy_ - 70 * math.cos(an))], A(NAVYT, 1), 8)
    d.line([(cx_, cy_), (cx_, cy_ + 50)], A(NAVYT, 1), 10)
    ptag(d, t, t0 + 0.3, 300, 740, "饭点", (255, 120, 90), 40, tc=WHITE)
    d.ell(700, 1110, 110, 34, A((90, 140, 220), 1)); d.ell(700, 1098, 86, 18, A((240, 236, 226), 1))
    orangecat(d, 700, 900, 0.95, t, meow=mw(t, t0 + 0.8, 0.6))
    kk = popk(t, t0 + 1.0, "bouncy")
    if kk > 0: meowbub(d, 860, 560, 44 * min(1, kk), min(1, kk), "喵喵！")
def s_card(t, d):
    flatbg(d, (255, 190, 110), (210, 120, 60), t, False)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    orangecat(d, cx_, cy_ - 150, 0.55, t, a=a_)
    d.text(cx_, cy_ + 30, "主人在场，猫更爱喵", 44, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("喵的几率约高16倍", "约56%的喵看着主人", "还不能证明是故意的")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 130 + i * 78, s_, 38, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    room(d, t, (255, 200, 120), (240, 140, 80))
    treatbox(d, 760, 1120, 0.6, t=t)
    lk = 0 if (t - t0) % 1.6 < 0.8 else 1
    orangecat(d, 420, 1000, 1.0, t, look=lk, meow=mw(t, t0 + 0.3, 0.8, 2))
    if lk: gaze(d, 470, 880, 700, 1080, (255, 120, 90), 1, 1, t)
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 285, "Fukimoto et al. 2026", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 330, "Animal Behaviour · 38 cats", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

