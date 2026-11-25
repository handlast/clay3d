import sys, subprocess, math, random
from chars import *
from cues import *

def popk(t, t0, preset="snappy"): return max(0.0, E.spring_at(t, t0, 0, 1, preset)) if t >= t0 else 0.0
def ap(t, t0, d=0.12): return cl((t - t0) / d)
def tag(d, x, y, s, col, a=1.0, size=40, tc=NAVYT):
    if a <= 0.01: return
    w = d.tlen(s, size, 1) + 44
    d.rect(x - w / 2, y - size * 0.78, x + w / 2, y + size * 0.78, fill=A(col, 0.95 * a), r=size * 0.6)
    d.text(x, y, s, size, A(tc, a), k=1)
def ptag(d, t, t0, x, y, s, col, size=40, tc=NAVYT):
    k = popk(t, t0)
    if k > 0: tag(d, x, y + (1 - min(k, 1)) * 30, s, col, ap(t, t0), int(size * (0.6 + 0.4 * k)), tc)
def title(d, t, t0, s, y=330, size=110, col=WHITE):
    k = popk(t, t0, "heavy")
    if k > 0: d.text(540, y + (1 - k) * 40, s, int(size * (0.85 + 0.15 * k)), A(col, ap(t, t0)), k=1)
def slamtxt(d, t, t0, s, y, size, col):
    if t < t0: return
    d.text(540, y, s, int(size * E.slam(t, t0, 0.28, 1.8)), A(col, ap(t, t0, 0.06)), k=1)
def arrow(d, x0, y0, x1, y1, col, a=1.0, w=12):
    L = math.hypot(x1 - x0, y1 - y0) + 1e-6; ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    bx, by = x1 - ux * w * 2.4, y1 - uy * w * 2.4
    d.line([(x0, y0), (bx, by)], A(col, a), w); d.poly([(bx + nx * w * 1.6, by + ny * w * 1.6), (x1, y1), (bx - nx * w * 1.6, by - ny * w * 1.6)], A(col, a))
def cross(d, x, y, s, k, col, a=1.0):
    if k <= 0: return
    d.line([(x - s, y - s), (x - s + 2 * s * min(1, k * 2), y - s + 2 * s * min(1, k * 2))], A(col, a), s * 0.3)
    if k > 0.5: d.line([(x + s, y - s), (x + s - 2 * s * (k - 0.5) * 2, y - s + 2 * s * (k - 0.5) * 2)], A(col, a), s * 0.3)
def _unused_blink(t, t0, n=4, per=0.32):
    """blinking glow envelope: n flashes starting t0"""
    if t < t0: return 0.0
    u = (t - t0) / per; i = int(u)
    if i >= n: return 0.0
    f = u - i
    return math.exp(-f * 2.4) * (1 - 0.1 * i)
def zap(d, x, y, t, t0, col=WHITE, maxr=300, a=1.0):
    u = (t - t0) / 0.7
    if 0 <= u < 1:
        for j in range(3):
            rr_ = 30 + (u + j * 0.1) * maxr
            d.circ(x, y, rr_, outline=A(col, a * (1 - u) * (1 - j * 0.3)), w=10 - j * 3)

def bubble_txt(d, t, t0, x, y, s, col, size=70, tail=-1):
    k = popk(t, t0, "bouncy")
    if k <= 0: return
    sz = int(size * min(1.1, k)); w = d.tlen(s, sz, 1) + 60
    d.rect(x - w / 2, y - sz * 0.85, x + w / 2, y + sz * 0.85, fill=A(WHITE, 0.97), r=sz * 0.6)
    d.poly([(x + tail * 30, y + sz * 0.7), (x + tail * 80, y + sz * 1.5), (x + tail * 70, y + sz * 0.7)], A(WHITE, 0.97))
    d.text(x, y, s, sz, A(col, 1), k=1)
# ---------------- scenes ----------------
def ramp(t, a, b): return E.ease_in_out_sine(pr(t, a, b))
def garden(d, t, top=(70, 120, 80), bot=(24, 50, 34), ground=1350):
    flatbg(d, top, bot, t, False)
    d.rect(0, ground, 1080, 1920, fill=A((70, 52, 40), 1))
    for i in range(10):
        rv = random.Random(i); d.circ(rv.uniform(0, 1080), ground + rv.uniform(20, 500), rv.uniform(10, 30), fill=A((90, 70, 52), 1))
def check(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 18 * s_, y), (x - 4 * s_, y + 14 * s_), (x + 20 * s_, y - 14 * s_)], A(WHITE, a), 8 * s_)
def xmark(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 15 * s_, y - 15 * s_), (x + 15 * s_, y + 15 * s_)], A(WHITE, a), 8 * s_); d.line([(x - 15 * s_, y + 15 * s_), (x + 15 * s_, y - 15 * s_)], A(WHITE, a), 8 * s_)
def heart(d, x, y, r, col, a=1.0):
    d.circ(x - r * 0.5, y - r * 0.2, r * 0.55, fill=A(col, a)); d.circ(x + r * 0.5, y - r * 0.2, r * 0.55, fill=A(col, a))
    d.poly([(x - r * 1.02, y - 0.05 * r), (x + r * 1.02, y - 0.05 * r), (x, y + r * 1.1)], A(col, a))
def puddle(d, x, y, w, a=1.0): d.ell(x, y, w, w * 0.18, A((90, 170, 240), 0.85 * a))
def arrow_up(d, x, y0, y1, col, a=1.0, w=14):
    d.line([(x, y0), (x, y1 + 30)], A(col, a), w); d.poly([(x - 34, y1 + 40), (x + 34, y1 + 40), (x, y1)], A(col, a))

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
    d.text(730, base - 80, "1倍", 40, A(NAVYT, 1), k=1)
    ptag(d, t, t0 + 0.1, 730, 600, "喵的几率", NAVYT, 40, tc=WHITE)
    k = popk(t, t0 + 0.6, "bouncy")
    if k > 0:
        tag(d, 730, 760, "约16倍", GOLD, min(1, k), 70)
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
        sw = 0.56 * ease(pr(t, t0 + 1.4, t0 + 2.4))
        if sw > 0.005:
            pts = [(cx_, cy_)] + [(cx_ + r * min(1, k) * math.sin(2 * math.pi * sw * j / 40), cy_ - r * min(1, k) * math.cos(2 * math.pi * sw * j / 40)) for j in range(41)]
            d.poly(pts, A(GOLD, 1))
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

# ---------------- captions ----------------
HL = {"hook": "帮忙", "q": "锁进", "who": "38只猫", "sperm": "离开", "egg": "叫得多", "reveal": "约16倍", "how": "看着主人", "xray": "来回看",
      "swim": "盒子", "gene": "望门", "why": "故意", "order": "饭点", "end": "看哪里"}
def subs(t, d):
    for a, b, s, key in SUBS:
        if a <= t < b:
            ee = E.enter_exit(t, max(a, 0), b, 0.3, 0.12, rise=18, s0=0.96)
            al = ee["alpha"] if a > 0 else (1 - pr(t, b - 0.12, b))
            if al <= 0.01: return
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70 + ee["dy"] * (a > 0)
            w = max(d.tlen(x, 54, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 70 + 46, fill=A((6, 14, 26), 0.82 * al), r=22)
            hw = HL.get(key)
            for i, x in enumerate(ls):
                yy = y0 + i * 70
                if hw and hw in x:
                    j = x.index(hw); parts = [(x[:j], WHITE), (hw, GOLD), (x[j + len(hw):], WHITE)]
                    xx = 540 - d.tlen(x, 54, 1) / 2
                    for p_, c_ in parts:
                        if p_: d.text(xx, yy, p_, 54, A(c_, al), anchor="lm", k=1); xx += d.tlen(p_, 54, 1)
                else: d.text(540, yy, x, 54, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇动物"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)

SF = {n: globals()["s_" + n] for n in NAMES}
SECS = [(-1, HOOKCUT, s_hook, "hook")] + [(T[n], nxt(n), SF[n], n) for n in NAMES[1:]]
SECS = [(a, (99 if i == len(SECS) - 1 else b), f, n) for i, (a, b, f, n) in enumerate(SECS)]
def cam(t):
    z = 1.0 + 0.04 * pulse(t, [HOOK_HIT, BIG2], 3)
    for a, b, f, n in SECS:
        if a <= t < b: z += 0.03 * eio(pr(t, max(a, 0), min(b, DUR))); break
    sx, sy = shake(t, 8 * pulse(t, [HOOK_HIT, BIG2], 5), 40)
    return z, 540 + sx, 900 + sy
def frame(t, fi=0):
    img = Image.new("RGB", (W, H), (20, 40, 30)); d = D(img); key = None
    for a, b, sf, n in SECS:
        if a <= t < b: sf(t, d); key = n; break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.5 * (1 - (t - c) / 0.1)))
    brand(t, d); subs(t, d)
    out = img.resize((OW, OH), Image.LANCZOS)
    out = E.vignette(out, 0.2); out = E.grain(out, 0.03, seed=fi)
    return out
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/mw_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/mw_sheet.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                              "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", out], stdin=subprocess.PIPE)
        last = None; errs = 0
        for i in range(i0, i1):
            try: last = frame(i / FPS, i).tobytes()
            except Exception as e: errs += 1; print('ERR', i, e, file=sys.stderr)
            if last: p.stdin.write(last)
        p.stdin.close(); p.wait(); print('errs', errs, file=sys.stderr)
