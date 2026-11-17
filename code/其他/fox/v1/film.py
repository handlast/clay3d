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

# ---------------- scenes ----------------
def ramp(t, a, b): return E.ease_in_out_sine(pr(t, a, b))
GY = 1120  # ground line
BGS = {"teal": ((30, 120, 130), (12, 60, 72)), "plum": ((80, 40, 110), (30, 14, 50)), "navy": ((24, 34, 70), (8, 12, 28)),
       "red": ((150, 40, 60), (60, 14, 26)), "snow": ((90, 130, 180), (40, 60, 100)), "lab": ((30, 70, 90), (10, 26, 36)), "gold": ((170, 110, 30), (80, 46, 10))}
def bg(d, t, k, deco=True): flatbg(d, BGS[k][0], BGS[k][1], t, deco)
def ground(d, col=(255, 255, 255), a=0.12): d.rect(0, GY + 150, 1080, 1920, fill=A(col, a))
NEU = [(math.cos(i * 2.4) * (40 + 22 * math.sqrt(i)), math.sin(i * 2.4) * (40 + 22 * math.sqrt(i)) * 0.7) for i in range(26)]
def xray(d, t, cx, cy, s, off_frac, a=1.0, col=MAG):
    """brain silhouette with a cluster of glowing neurons; off_frac of them switched off"""
    brain(d, cx, cy, s, a * 0.9, (255, 255, 255), (220, 225, 240))
    d.circ(cx + 10 * s, cy + 40 * s, 95 * s, fill=A((40, 30, 70), 0.9 * a))
    n = len(NEU)
    for i, (nx, ny) in enumerate(NEU):
        lit = 0.0 if i < off_frac * n else 1.0
        neuron(d, cx + 10 * s + nx * s * 0.8, cy + 40 * s + ny * s * 0.8, 9 * s, col, a, t, lit)
def s_hook(t, d):
    bg(d, t, "plum")
    k = ramp(t, 1.2, 3.6)
    ground(d)
    fox(d, 470, GY, 1.25, t, tame=k, mood="angry" if k < 0.5 else "happy", wag=t * 3 * k)
    xray(d, t, 760, 580, 0.7, k * 0.55)
    if t < 1.3: slamtxt(d, t, -0.2, "少了！", 300, 150, GOLD)
    if k > 0.05: sparks(d, 760, 610, t, 1.4, 30, 600, MAG, 0.8, 4, 1.0)
def s_q(t, d):
    bg(d, t, "plum")
    ground(d)
    fox(d, 470, GY, 1.25, t, tame=1, mood="happy", wag=t * 3)
    xray(d, t, 760, 580, 0.7, 0.55)
    q_ = popk(t, T["q"] + 0.1)
    if q_ > 0: d.text(760, 400, "？", int(150 * min(1, q_)), A(GOLD, 1), k=1)
def s_reveal(t, d):
    rays(d, t, (255, 90, 110), (120, 20, 50))
    k = popk(t, BIG2, "bouncy")
    if k > 0:
        xray(d, t, 540, 800, 1.6 * (0.85 + 0.15 * min(1, k)), 0.0, 1, MEAN)
    slamtxt(d, t, BIG2, "攻击", 360, 230, WHITE)
    if t > BIG2 + 0.25: sparks(d, 560, 860, t, BIG2 + 0.25, 50, 1200, (255, 200, 120), 1, 7, 1.0)
def s_y1959(t, d):
    bg(d, t, "snow", False)
    for i in range(30):  # snow
        sx = (i * 97 + 20 * math.sin(t + i)) % 1080; sy = (i * 211 + t * 90) % 1500 + 200
        d.circ(sx, sy, 5 + i % 4, fill=A(WHITE, 0.6))
    d.rect(0, GY + 150, 1080, 1920, fill=A(WHITE, 0.85))
    # farm cages (flat)
    for i in range(3):
        x0 = 170 + i * 260
        d.rect(x0, GY - 120, x0 + 220, GY + 150, fill=A((60, 80, 110), 0.9), r=16)
        for j in range(6): d.line([(x0 + 20 + j * 36, GY - 110), (x0 + 20 + j * 36, GY + 140)], A((150, 170, 200), 0.8), 5)
        fox(d, x0 + 110, GY + 60, 0.45, t + i, tame=0, mood="angry" if i != 1 else "neutral", flip=1 if i % 2 == 0 else -1, bob=0.4)
    k = popk(t, at("y1959", 0.2), "heavy")
    if k > 0:
        d.text(540, 520, "1959", int(240 * (0.8 + 0.2 * min(k, 1.1))), A(WHITE, ap(t, at("y1959", 0.2))), k=1)
        ptag(d, t, at("y1959", 1.2), 540, 700, "西伯利亚", (90, 200, 255), 54)
def s_pick(t, d):
    bg(d, t, "teal")
    ground(d)
    xs = [180, 400, 640, 880]
    for i, x in enumerate(xs):
        chosen = i in (1, 2)
        fade = 1 - 0.65 * ap(t, at("pick", 2), 0.3) * (not chosen)
        fox(d, x, GY, 0.6, t + i, tame=0.15 if chosen else 0, mood="happy" if chosen else "angry", a=fade, flip=1 if i < 2 else -1, bob=0.5)
        if chosen and t > at("pick", 1):
            ptag(d, t, at("pick", 1 + i * 0.3), x, GY - 300, "✓" if False else "亲人", TAME, 40)
    if t > at("pick", 3):
        hk = popk(t, at("pick", 3))
        d.text(520, GY - 420, "♥", int(120 * min(1, hk)), A(PINK, 1), k=1) if False else d.circ(520, GY - 420, 50 * min(1, hk), fill=A(PINK, 1))
        d.circ(470, GY - 440, 40 * min(1, hk), fill=A(PINK, 1)); d.circ(570, GY - 440, 40 * min(1, hk), fill=A(PINK, 1))
        d.poly([(430, GY - 425), (610, GY - 425), (520, GY - 330)], A(PINK, min(1, hk)))
def s_six(t, d):
    bg(d, t, "gold")
    ground(d)
    g = 1 + min(5, int(pr(t, at("six", 0.2), at("six", 4.5)) * 6))
    k = (g - 1) / 5
    fox(d, 380, GY, 0.9, t, tame=0.35 * k, mood="happy" if g >= 4 else "neutral", wag=t * 3)
    # human hand reaching in from right
    hx = 1000 - 160 * ramp(t, at("six", 3.5), at("six", 5))
    d.ell(hx, GY - 200, 90, 60, A((250, 205, 170), 1)); d.rect(hx, GY - 250, hx + 300, GY - 150, fill=A((80, 140, 220), 1), r=30)
    gk = popk(t, at("six", 0.2) + (g - 1) * 0.75)
    d.text(540, 470, "第%d代" % g, int(150 * (0.85 + 0.15 * min(1, gk))), A(WHITE, 1), k=1)
    d.rect(300, 590, 780, 616, fill=A((0, 0, 0), 0.25), r=13); d.rect(300, 590, 300 + 480 * g / 6, 616, fill=A(GOLD, 1), r=13)
def s_look(t, d):
    bg(d, t, "teal")
    ground(d)
    k = ramp(t, at("look", 0.3), at("look", 3.3))
    fx_, fy_ = fox(d, 470, GY, 1.3, t, tame=k, mood="happy", wag=t * 3)
    for i, (lab, x, y) in enumerate((("耳朵耷拉", 380, 470), ("嘴变短", 840, 640), ("尾巴卷", 210, 740))):
        ptag(d, t, at("look", 1.0 + i * 1.0), x, y, lab, TAME, 44)
def s_mean(t, d):
    bg(d, t, "red")
    ground(d)
    fox(d, 300, GY, 0.85, t, tame=1, mood="happy", wag=t * 3)
    sh = 6 * math.sin(t * 30) * ap(t, at("mean", 1.5), 0.2)
    fox(d, 780 + sh, GY, 0.95, t, tame=0, mood="angry", flip=-1)
    ptag(d, t, at("mean", 0.3), 300, GY - 330, "温顺组", TAME, 44)
    ptag(d, t, at("mean", 1.5), 780, GY - 360, "凶狐狸组", MEAN, 48)
def s_nine(t, d):
    bg(d, t, "lab")
    labs = (("温顺", TAME), ("凶", MEAN), ("野生", MINT))
    for r_, (lab, c) in enumerate(labs):
        y = 560 + r_ * 230
        ptag(d, t, at("nine", 2 + r_ * 0.6), 220, y, lab, c, 44)
        for j in range(3):
            kk = popk(t, at("nine", 0.4 + (r_ * 3 + j) * 0.15))
            if kk > 0:
                d.rect(370 + j * 190 - 70, y - 75, 370 + j * 190 + 70, y + 75, fill=A((255, 255, 255), 0.12), r=24)
                brain(d, 370 + j * 190 + 10, y - 15, 0.28 * min(1, kk), 1, mix((255, 180, 200), c, 0.4), mix((230, 140, 170), c, 0.4))
    kn = popk(t, at("nine", 0.2), "heavy")
    if kn > 0: d.text(540, 360, "9", int(170 * min(1.05, kn)), A(GOLD, 1), k=1)
def s_slice(t, d):
    bg(d, t, "navy")
    k = ramp(t, at("slice", 0.3), at("slice", 2.2))
    cx, cy = 540, 760
    if k < 1:
        brain(d, cx, cy, 1.2, 1)
        bx = 120 + 840 * k
        d.rect(bx - 6, cy - 300, bx + 6, cy + 300, fill=A(WHITE, 0.9)); glow(d, bx, cy, 120, CYAN2, 0.6)
    else:
        f = ramp(t, at("slice", 2.2), at("slice", 3.2))
        for i in range(6):
            ox = (i - 2.5) * 140 * f
            d.rect(cx + ox - 50, cy - 230 + abs(i - 2.5) * 20 * f, cx + ox + 50, cy + 230 - abs(i - 2.5) * 20 * f, fill=A((255, 200, 215), 0.95), r=40)
        g = ap(t, at("slice", 3.4), 0.5)
        if g > 0:
            rv = random.Random(5)
            for i in range(60):
                sx = cx + rv.uniform(-400, 400) * f; sy = cy + rv.uniform(-200, 200)
                c = [MAG, CYAN2, MINT][i % 3]
                glow(d, sx, sy, 40, c, g, 5); d.circ(sx, sy, 11, fill=A(c, g)); d.circ(sx, sy, 5, fill=A(WHITE, g))
            ptag(d, t, at("slice", 3.6), 540, 1110, "荧光标记", CYAN2, 46)
def s_where(t, d):
    bg(d, t, "navy")
    k = ramp(t, at("where", 0.3), at("where", 2.5))
    s = 1.2 + 0.6 * k
    cx, cy = 540 - 10 * s, 760 - 50 * k
    brain(d, cx, cy, s, 1 - 0.4 * k)
    tx, ty = cx + 10 * s, cy + 50 * s
    pul = 0.5 + 0.5 * math.sin(t * 6)
    glow(d, tx, ty, 90 + 30 * pul, GOLD, ap(t, at("where", 1.5), 0.3))
    d.circ(tx, ty, 34, fill=A(GOLD, ap(t, at("where", 1.5), 0.3)))
    ptag(d, t, at("where", 2.2), 540, 330, "下丘脑腹内侧", GOLD, 58)
def s_mouse(t, d):
    bg(d, t, "lab")
    ground(d)
    mouse(d, 420, GY + 60, 1.3, t)
    # optic fibre from top
    d.line([(450, 200), (450, GY - 40)], A((200, 210, 230), 0.9), 8)
    b = ap(t, at("mouse", 2.5), 0.2) * (0.6 + 0.4 * math.sin(t * 20))
    if b > 0:
        glow(d, 450, GY - 30, 160, CYAN2, b); d.line([(450, 260), (450, GY - 40)], A(CYAN2, b), 16)
        for i in range(5): neuron(d, 700 + (i % 3) * 80, 520 + (i // 3) * 90, 18, CYAN2, 1, t, b)
    ptag(d, t, at("mouse", 0.3), 760, 380, "小鼠实验", WHITE, 44)
    ptag(d, t, at("mouse", 3.5), 760, 760, "ERα 神经元", CYAN2, 44)
def s_attack(t, d):
    bg(d, t, "red")
    ground(d)
    u = ramp(t, at("attack", 0.3), at("attack", 1.2))
    sh = 5 * math.sin(t * 40) * u
    mouse(d, 300 + 260 * u + sh, GY + 60, 1.2, t, "angry", col=(255, 190, 200))
    mouse(d, 860, GY + 60 - 40 * u, 1.0, t, "neutral", flip=-1)
    d.line([(450, 200), (300 + 260 * u + 30, GY - 40)], A(CYAN2, 0.9), 12)
    if u > 0.95: zap(d, 760, GY - 20, t, at("attack", 1.2), WHITE, 300, 1); stamp(d, t, at("attack", 1.3), "立刻攻击", 540, 420, 110, MEAN)
def s_result(t, d):
    bg(d, t, "navy")
    tag(d, 900, 330, "示意", WHITE, 0.5, 26)
    for i, (lab, c, off, x) in enumerate((("凶狐狸", MEAN, 0.0, 300), ("温顺狐狸", TAME, 0.45, 780))):
        d.rect(x - 210, 470, x + 210, 1110, fill=A((255, 255, 255), 0.06), r=36)
        ptag(d, t, at("result", 0.3 + i * 0.4), x, 420, lab, c, 46)
        rv = random.Random(11 + i * 0)
        for j in range(30):
            nx = x + rv.uniform(-170, 170); ny = 540 + rv.uniform(0, 520)
            kk = ap(t, at("result", 0.6 + j * 0.03), 0.2)
            # tame panel: some switch off one by one
            offk = 1.0
            if i == 1 and j < off * 30: offk = 1 - ap(t, at("result", 2.4 + j * 0.08), 0.15)
            neuron(d, nx, ny, 13, MAG, kk, t, offk)
    if t > at("result", 4): slamtxt(d, t, at("result", 4), "更少", 330 - 120 + 0, 0 + 120, GOLD) if False else ptag(d, t, at("result", 4), 780, 1170, "更少", GOLD, 56)
def s_sub(t, d):
    bg(d, t, "plum")
    tag(d, 900, 330, "示意", WHITE, 0.5, 26)
    # zoom: subtypes as colored neuron groups, magenta (aggression-linked) shrink
    types = [("其他亚型", CYAN2, 0), ("攻击相关亚型", MAG, 1)]
    for i, (lab, c, agg) in enumerate(types):
        x = 300 + i * 480
        cnt = 12
        if agg: cnt = 12 - int(5 * ap(t, at("sub", 2.2), 1.2))
        for j in range(12):
            gx = x - 120 + (j % 3) * 120; gy = 560 + (j // 3) * 140
            lit = 1.0 if j < cnt else 0.0
            neuron(d, gx, gy, 20, c, ap(t, at("sub", 0.4 + j * 0.04), 0.2), t, lit)
        ptag(d, t, at("sub", 0.8 + i * 0.5), x, 430, lab, c, 40)
    if t > at("sub", 3.4): ptag(d, t, at("sub", 3.4), 780, 1120, "只少这一种", GOLD, 50)
def s_caution(t, d):
    bg(d, t, "navy")
    for j in range(9):
        x = 230 + (j % 3) * 310; y = 520 + (j // 3) * 200
        kk = popk(t, at("caution", 0.2 + j * 0.08))
        if kk > 0: brain(d, x, y, 0.3 * min(1, kk), 1)
    if t > at("caution", 2):
        k = ap(t, at("caution", 2), 0.3)
        d.rect(170, 1100 - 100, 910, 1100 - 10, fill=A((255, 255, 255), 0.0))
        tag(d, 540, 360, "相关 ≠ 因果", GOLD, k, 60)
def s_next(t, d):
    bg(d, t, "teal")
    ground(d)
    fox(d, 420, GY, 1.0, t, tame=1, mood="happy", wag=t * 3)
    qk = popk(t, at("next", 1))
    for i, (x, y) in enumerate(((760, 520), (860, 650), (700, 700))):
        kk = popk(t, at("next", 1 + i * 0.4))
        if kk > 0: d.text(x, y, "？", int((110 - i * 20) * min(1, kk)), A(GOLD, 1), k=1)
    ptag(d, t, at("next", 0.3), 540, 340, "为什么？", WHITE, 56)
def s_card(t, d):
    bg(d, t, "plum", False)
    for i in range(12): d.circ(540, 860, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 690 * (0.8 + 0.2 * k), 980 * (0.8 + 0.2 * k); cx_, cy_ = 540, 840; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 80, "一句话学会", GOLD, a_, 32)
    fox(d, cx_ - 20, cy_ - 100, 0.42, t, tame=1, mood="happy", a=a_, wag=t * 3, bob=0.3)
    d.text(cx_, cy_ + 60, "温顺狐狸：攻击相关细胞更少", 38, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("驯化：一代代只挑最亲人的配对", "下丘脑腹内侧：管攻击等本能", "小鼠里点亮 ERα 神经元就会攻击", "目前只是候选细胞，还没证明因果")):
        kk = popk(t, at("card", 1.2 + i * 1.6))
        if kk > 0: d.text(cx_, cy_ + 150 + i * 62, s_, 31, A((70, 70, 90), ap(t, at("card", 1.2 + i * 1.6))), k=1)
def s_end(t, d):
    bg(d, t, "gold")
    ground(d)
    fox(d, 470, GY, 1.2, t, tame=1, mood="happy", wag=t * 4)
    xray(d, t, 790, 600, 0.6, 0.55)
    ptag(d, t, at("end", 3), 540, 330, "少装几个", WHITE, 70)
    ra = ap(t, at("end", 5), 0.3)
    if ra > 0:
        d.rect(170, 1250 - 860, 910, 1360 - 860, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 423, "Klein 等 2026 · Current Biology", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 467, "9 颗狐狸脑的比较 · 相关性研究", 25, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "少了一类细胞", "q": "哪一类", "reveal": "攻击", "y1959": "1959年", "pick": "最亲人", "six": "6代", "look": "尾巴卷",
      "mean": "最凶", "nine": "9颗", "slice": "荧光标记", "where": "下丘脑腹内侧", "mouse": "雌激素受体α神经元", "attack": "立刻", "result": "少",
      "sub": "那一亚型", "caution": "还没证明", "next": "为什么", "end": "少装几个"}
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
    img = Image.new("RGB", (W, H), (6, 20, 40)); d = D(img); key = None
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/fx_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/fx_sheet.png")
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
