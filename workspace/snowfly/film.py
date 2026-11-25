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
        d.ell(440, 560, 70 * min(1, k), 30 * min(1, k), A((180, 220, 255), 0.7)); d.ell(600, 560, 70 * min(1, k), 30 * min(1, k), A((180, 220, 255), 0.7))
        kx = pr(t, t0 + 1.1, t0 + 1.4)
        if kx > 0: cross(d, 520, 560, 100, kx, (230, 60, 60))
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
    d.ell(260 + sh, 740, 60, 36, A((210, 235, 255), 0.85)); d.ell(340 + sh, 740, 60, 36, A((210, 235, 255), 0.85))
    d.ell(300 + sh, 820, 110, 80, A((250, 200, 60), 1)); d.circ(420 + sh, 810, 45, fill=A(NAVYT, 1)); d.circ(432 + sh, 800, 10, fill=A(WHITE, 1))
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

# ---------------- captions ----------------
HL = {"hook": "散步", "q": "冰棍", "who": "没有翅膀", "sperm": "躲起来", "egg": "凭什么", "reveal": "发热", "how": "一两度", "xray": "棕色脂肪",
      "swim": "防冻蛋白", "gene": "北极鱼", "why": "30倍", "order": "躲起来", "end": "约会"}
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/sf_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/sf_sheet.png")
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
