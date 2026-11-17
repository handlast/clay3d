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
def zap(d, x, y, t, t0, col=WAX_L, maxr=300, a=1.0):
    u = (t - t0) / 0.7
    if 0 <= u < 1:
        for j in range(3):
            rr_ = 30 + (u + j * 0.1) * maxr
            d.circ(x, y, rr_, outline=A(col, a * (1 - u) * (1 - j * 0.3)), w=10 - j * 3)

# ---------------- scenes ----------------
def warmbg(d, t, c1=(70, 30, 44), c2=(28, 12, 22)): grad(d, c1, c2)
def bench(d, y=1300, a=1.0):
    d.rect(-20, y, 1100, 2000, fill=A((70, 84, 110), a)); d.rect(-20, y, 1100, y + 18, fill=A((110, 126, 156), a))
def fall_ant(d, t, t0, x, y, s, mood="scream"):
    """ant tumbling down from (x,y) starting t0; returns current pos"""
    u = max(0, t - t0)
    yy = y + 900 * u * u + 120 * u; xx = x + 120 * u
    ant(d, xx, yy, s, t, mood=mood, ang=u * 9, slip=1, walk=3)
    return xx, yy

def s_hook(t, d):
    warmbg(d, t, (90, 34, 50), (40, 14, 26))
    top, bot = canal(d, t, 980, wax=1.0)
    # ant charging in, then slipping back down the wax at t=0 hit
    k = pr(t, -0.2, 0.0)
    if t < 0.05:
        ant(d, lerp(80, 420, k), 1120, 1.3, t, mood="sus", walk=2)
    else:
        u = t
        ax = 420 - 380 * E.ease_out_cubic(pr(t, 0, 0.9)); ay = 1120 + 40 * math.sin(min(u, 0.9) * 12) * (1 - pr(t, 0, 0.9))
        ant(d, ax, ay, 1.3, t, mood="scream" if t < 1.6 else "dizzy", ang=-0.5 * math.sin(t * 9) * (1 - pr(t, 0, 1.2)), slip=1 - pr(t, 1.0, 1.6), walk=4)
        for j in range(5):
            d.line([(ax + 140 + j * 30, ay - 40 + j * 20), (ax + 220 + j * 30, ay - 40 + j * 20)], A(WHITE, 0.6 * (1 - pr(t, 0, 0.8))), 6)
    waxguy(d, 760, 1160, 110, t, mood="proud" if t > 0.2 else "sus")
    slamtxt(d, t, -0.2, "哧溜！", 380, 200, EARIN)
    if t > 1.2: ptag(d, t, 1.2, 540, 560, "耳屎拦住了", EARIN, 56, tc=WHITE)
def s_q(t, d):
    warmbg(d, t)
    waxguy(d, 540, 1050, 230, t, mood="sus", look=math.sin(t * 2))
    kk = popk(t, T["q"] + 0.05, "bouncy")
    if kk > 0: d.text(540, 520, "?", int(300 * (0.6 + 0.4 * kk)), A(WAX_L, ap(t, T["q"])), k=1)
def s_reveal(t, d):
    rays(d, t, (255, 200, 110), (230, 130, 60))
    k = min(1.1, popk(t, BIG2, "bouncy"))
    # brick wall of wax behind
    for row in range(4):
        for col in range(6):
            x0 = 110 + col * 150 + (75 if row % 2 else 0); y0 = 1300 - row * 92
            if x0 > 1000: continue
            kb = popk(t, BIG2 + 0.03 * (row * 6 + col))
            if kb > 0: d.rect(x0, y0 - 86 * min(1, kb), x0 + 140, y0, fill=A(mix(WAX, WAX_D, (row + col) % 2 * 0.4), 1), r=14)
    waxguy(d, 540, 960, 170 * (0.6 + 0.4 * k), t, mood="proud")
    slamtxt(d, t, BIG2, "防虫墙", 360, 170, WHITE)
    ptag(d, t, at("reveal", 2), 540, 520, "（可能）", NAVYT, 44, tc=WHITE)
    for i in range(3):
        u = pr(t, at("reveal", 1 + i * 0.6), at("reveal", 2.2 + i * 0.6))
        if 0 < u < 1: ant(d, lerp(1100, 860, math.sin(u * math.pi)), 1500 + i * 70, 0.5, t, mood="scared", ang=math.pi, walk=3)
def s_study(t, d):
    warmbg(d, t, (40, 50, 80), (16, 20, 40))
    bench(d, 1300)
    # petri box with ants
    d.rect(200, 1060, 880, 1300, fill=A(GLASS, 0.18), r=30); d.rect(200, 1060, 880, 1080, fill=A(GLASS, 0.5), r=10)
    for i in range(4):
        x = 280 + ((t * 90 + i * 170) % 560)
        ant(d, x, 1230 - (i % 2) * 40, 0.55, t + i, mood="happy", walk=1.5)
    ptag(d, t, at("study", 0.4), 540, 330, "佐治亚理工", WHITE, 64)
    ptag(d, t, at("study", 2), 540, 460, "物理学家 × 蚂蚁", WAX_L, 48)
    kk = popk(t, at("study", 4), "bouncy")
    if kk > 0:
        d.rect(640, 640, 900, 960, fill=A((248, 244, 230), 1), r=20); d.rect(700, 620, 840, 660, fill=A(METAL if False else (170, 186, 204), 1), r=10)
        for j in range(4): d.line([(680, 720 + j * 56), (860 - 40 * (j % 2), 720 + j * 56)], A((150, 160, 180), 1), 8)
        d.text(770, 920, "Soft Matter", 30, A(NAVYT, 1), k=1)
def s_samples(t, d):
    warmbg(d, t, (60, 40, 70), (24, 14, 32))
    names = ["猪", "羊", "狗", "牛", "兔", "人"]
    for i, n in enumerate(names):
        x = 250 + (i % 3) * 290; y = 800 + (i // 3) * 360
        kk = popk(t, at("samples", 0.3 + i * 0.45), "bouncy")
        if kk <= 0: continue
        s_ = min(1, kk)
        d.rect(x - 100 * s_, y - 120 * s_, x + 100 * s_, y + 120 * s_, fill=A(GLASS, 0.3), r=26)
        d.rect(x - 110 * s_, y - 150 * s_, x + 110 * s_, y - 110 * s_, fill=A((200, 90, 80), 1), r=12)
        waxguy(d, x, y + 50 * s_, 60 * s_, t + i, mood="happy" if n != "人" else "proud", face_=s_ > 0.6, dry=0.6 if i in (1, 4) else 0)
        tag(d, x, y - 40 * s_, n, WHITE, ap(t, at("samples", 0.3 + i * 0.45)), 40)
    if t > at("samples", 3.5): ptag(d, t, at("samples", 3.5), 540, 380, "36 份耳屎样本", WAX_L, 64)
BX, BY, BW, BH = 540, 1180, 420, 560
def climb_scene(d, t, rough=0.0, prog=0.0, mood="happy", fall_t=None, slipk=0.0):
    warmbg(d, t, (34, 44, 70), (14, 18, 34))
    bench(d, BY)
    rimy = beaker(d, BX, BY, BW, BH, rim=1.0, rough=rough, t=t)
    xL = BX - BW / 2 - 6
    if fall_t is not None and t >= fall_t:
        fall_ant(d, t, fall_t, xL - 60, rimy + 160, 0.75)
    else:
        y = lerp(BY - 120, rimy - 10, prog)
        ant(d, xL - 50, y, 0.75, t, mood=mood, ang=-math.pi / 2, walk=1.4 if rough else 2.2, slip=slipk)
    return rimy
def s_climb(t, d):
    k = E.ease_in_out_sine(pr(t, T["climb"], nxt("climb")))
    rimy = climb_scene(d, t, 0.0, 0.85 * k * 0.75)
    ptag(d, t, at("climb", 0.4), 540, 330, "杯口抹耳屎", WAX_L, 64)
    if t > at("climb", 2.5): ptag(d, t, at("climb", 2.5), 180, 760, "火蚁", (255, 130, 100), 48, tc=WHITE)
def s_rough(t, d):
    k = pr(t, T["rough"], nxt("rough"))
    p = 0.62 + 0.35 * (k - 0.05 * math.sin(k * 40) ** 2)
    rimy = climb_scene(d, t, 1.0, min(1, p), mood="sus")
    ptag(d, t, at("rough", 0.3), 540, 330, "粗糙", WAX, 90)
    if t > at("rough", 2): ptag(d, t, at("rough", 2), 760, 700, "爪子勾住", WHITE, 44)
    if t > at("rough", 4): ptag(d, t, at("rough", 4), 540, 470, "慢，但能爬", WHITE, 48)
def s_smooth(t, d):
    tf = at("smooth", 2.2)
    k = pr(t, T["smooth"], tf)
    rimy = climb_scene(d, t, 0.0, 0.62 + 0.3 * k, mood="happy" if t < tf - 0.4 else "scared", fall_t=tf, slipk=pr(t, tf - 0.4, tf))
    ptag(d, t, at("smooth", 0.3), 540, 330, "光滑", WAX_L, 90)
    if t > tf: slamtxt(d, t, tf, "滑！", 520, 200, WHITE)
def s_pad(t, d):
    warmbg(d, t, (30, 60, 80), (10, 24, 36))
    # big foot close-up pressing on glass
    gy = 1200
    d.rect(-20, gy, 1100, 2000, fill=A(GLASS, 0.25)); d.rect(-20, gy, 1100, gy + 10, fill=A(WHITE, 0.4))
    u = E.ease_in_out_sine(pr(t, at("pad", 0.5), at("pad", 2)))
    fx_, fy_ = 540, lerp(700, gy - 70, u)
    d.line([(400, 200), (500, fy_ - 160), (fx_, fy_ - 40)], A(ANT_D, 1), 60)
    for side in (-1, 1): d.line([(fx_ + side * 30, fy_), (fx_ + side * 110, fy_ - 60 + 30 * u)], A(ANT_D, 1), 18)   # claws
    pk = popk(t, at("pad", 2), "bouncy")
    d.ell(fx_, fy_ + 10, 70 + 40 * min(1, pk), 40, A(ANT_L, 1))
    if pk > 0:
        d.ell(fx_, gy - 8, 150 * min(1, pk), 18, A(WATERC, 0.75))
        for j in range(4): drop(d, fx_ - 90 + j * 60, gy - 30 - 10 * math.sin(t * 5 + j), 12, 0.8)
    ptag(d, t, at("pad", 0.3), 540, 330, "脚底特写", WHITE, 56)
    if t > at("pad", 2.4): ptag(d, t, at("pad", 2.4), 540, 470, "湿吸盘", WATERC, 70, tc=NAVYT)
def s_pore(t, d):
    warmbg(d, t, (80, 50, 30), (40, 22, 12))
    gy = 1150
    d.rect(-20, gy, 1100, 2000, fill=A(WAX, 1))
    rr_ = random.Random(9)
    pores = [(rr_.uniform(40, 1040), gy + rr_.uniform(40, 650), rr_.uniform(14, 38)) for _ in range(40)]
    for x, y, r in pores: d.circ(x, y, r, fill=A(WAX_D, 1)); d.circ(x - r * 0.2, y - r * 0.2, r * 0.6, fill=A((120, 72, 20), 1))
    for x in range(0, 1100, 160): d.circ(x + 40, gy + 6, 22, fill=A(WAX_D, 1))
    u = E.ease_in_out_sine(pr(t, at("pore", 0.3), at("pore", 1.6)))
    fx_, fy_ = 540, lerp(700, gy - 70, u)
    d.line([(400, 200), (500, fy_ - 160), (fx_, fy_ - 40)], A(ANT_D, 1), 60)
    d.ell(fx_, fy_ + 10, 110, 40, A(ANT_L, 1))
    sk = pr(t, at("pore", 1.8), at("pore", 4.5))
    if u > 0.95:
        d.ell(fx_, gy - 8, 150 * (1 - sk), 18 * (1 - sk) + 1, A(WATERC, 0.75))
        for j in range(6):
            v = cl(sk * 1.4 - j * 0.08)
            if 0 < v < 1: drop(d, fx_ - 120 + j * 48, gy + 30 + v * 300, 10, 0.8 * (1 - v))
    if sk > 0.6:
        uu = pr(t, at("pore", 4.6), at("pore", 6))
        d.line([(400, 200), (500, fy_ - 160 - 200 * uu), (fx_ + 40 * math.sin(t * 20) * uu, fy_ - 40 - 300 * uu)], A(ANT_D, 1), 1)
        ptag(d, t, at("pore", 4.6), 540, 600, "粘不住！", WHITE, 64)
    ptag(d, t, at("pore", 0.2), 540, 330, "满是小孔", WAX_L, 70)
    if t > at("pore", 2.2): ptag(d, t, at("pore", 2.2), 540, 460, "水被吸走", WATERC, 56, tc=NAVYT)
def s_sponge(t, d):
    warmbg(d, t, (40, 60, 90), (14, 22, 40))
    # scale: left wax, right 2 water drops
    tilt = 0.0
    d.rect(530, 700, 550, 1300, fill=A((170, 186, 204), 1), r=8); d.rect(400, 1290, 680, 1330, fill=A((170, 186, 204), 1), r=12)
    d.line([(240, 700 + tilt), (840, 700 - tilt)], A((200, 210, 226), 1), 16)
    for x in (240, 840):
        d.line([(x, 700), (x - 100, 900)], A((200, 210, 226), 0.8), 4); d.line([(x, 700), (x + 100, 900)], A((200, 210, 226), 0.8), 4)
        d.rect(x - 130, 900, x + 130, 920, fill=A((200, 210, 226), 1), r=8)
    kw = popk(t, at("sponge", 0.2), "bouncy")
    if kw > 0: waxguy(d, 240, 830, 70 * min(1, kw), t, mood="proud")
    for i in range(2):
        kk = popk(t, at("sponge", 1 + i * 0.6), "bouncy")
        if kk > 0: drop(d, 790 + i * 100, 860, 40 * min(1, kk), 1)
    slamtxt(d, t, at("sponge", 2.4), "×2", 400, 200, WATERC)
def s_tunnel(t, d):
    warmbg(d, t, (90, 34, 50), (40, 14, 26))
    top, bot = canal(d, t, 960, wax=1.0, open_=0.75)
    u = pr(t, at("tunnel", 0.3), at("tunnel", 5))
    ax = lerp(-80, 560, E.ease_out_cubic(u))
    ant(d, ax, 1050, 0.9, t, mood="happy" if u < 0.4 else "scared", walk=2 * (1 - u) + 0.3, wax=cl(u * 1.4))
    ptag(d, t, at("tunnel", 0.3), 540, 330, "耳道模型", WHITE, 60)
    if u > 0.5: ptag(d, t, at("tunnel", 3), 540, 470, "粘上了", WAX_L, 70)
def s_groom(t, d):
    warmbg(d, t, (70, 40, 60), (28, 14, 26))
    bench(d, 1160)
    sc = pr(t, T["groom"], nxt("groom"))
    ant(d, 540, 1020, 1.4, t, mood="sad" if sc < 0.6 else "dizzy", walk=0.3, wax=1 - 0.5 * sc, legs_up=0.6 + 0.3 * math.sin(t * 25))
    for j in range(6):
        a_ = t * 7 + j
        d.text(540 + 300 * math.cos(a_), 900 + 160 * math.sin(a_), "擦", 40, A(WHITE, 0.5), k=1)
    # stopwatch
    cx_, cy_ = 820, 560
    d.circ(cx_, cy_, 110, fill=A((248, 244, 230), 1)); d.rect(cx_ - 20, cy_ - 150, cx_ + 20, cy_ - 110, fill=A((200, 90, 80), 1), r=8)
    ang = -math.pi / 2 + sc * 2 * math.pi * 3
    d.line([(cx_, cy_), (cx_ + 80 * math.cos(ang), cy_ + 80 * math.sin(ang))], A(NAVYT, 1), 10)
    ptag(d, t, at("groom", 0.4), 360, 400, "疯狂清理", WHITE, 56)
    if t > at("groom", 4): ptag(d, t, at("groom", 4), 360, 520, "还是粘着", WAX_L, 48)
def s_both(t, d):
    warmbg(d, t, (50, 40, 70), (20, 14, 30))
    d.rect(0, 0, 540, 1920, fill=A((40, 90, 120), 0.5)); d.rect(540, 0, 1080, 1920, fill=A((150, 90, 30), 0.5))
    k1 = popk(t, at("both", 0.2), "bouncy"); k2 = popk(t, at("both", 1.2), "bouncy")
    if k1 > 0:
        d.text(270, 560, "滑", int(240 * min(1, k1)), A(WATERC, ap(t, at("both", 0.2))), k=1)
        u = (t * 0.8) % 1
        ant(d, 270 + 80 * math.sin(t * 6), 1050, 0.75, t, mood="scared", slip=1, ang=0.4 * math.sin(t * 8), walk=4)
    if k2 > 0:
        d.text(810, 560, "黏", int(240 * min(1, k2)), A(WAX_L, ap(t, at("both", 1.2))), k=1)
        ant(d, 810, 1050, 0.75, t, mood="sad", wax=1, walk=0.2, legs_up=0.4)
    if t > at("both", 2.6): ptag(d, t, at("both", 2.6), 540, 330, "双重绝招", WHITE, 70)
def s_skin(t, d):
    warmbg(d, t, (90, 50, 60), (40, 18, 26))
    cx_, cy_, R_ = 540, 900, 300
    k = E.ease_out_cubic(pr(t, at("skin", 0.3), at("skin", 2.3)))
    d.circ(cx_, cy_, R_, fill=A(WAX, 1))
    if k > 0:
        d.d.pieslice((P(cx_ - R_), P(cy_ - R_), P(cx_ + R_), P(cy_ + R_)), -90, -90 + 360 * 0.6 * k, fill=A(SKIN_L, 1))
    rr_ = random.Random(2)
    for i in range(14):
        a_ = rr_.uniform(-1.57, -1.57 + 6.28 * 0.6 * k) if k > 0.1 else -1.57; r_ = R_ * rr_.uniform(0.3, 0.85)
        if k > 0.1: skincell(d, cx_ + math.cos(a_) * r_, cy_ + math.sin(a_) * r_, 26, t, ang=i + t * 0.3)
    slamtxt(d, t, at("skin", 2.3), "约60%", 400, 150, SKIN_L)
    ptag(d, t, at("skin", 3.5), 540, 1290, "死掉的皮肤细胞", SKIN, 48)
def s_thin(t, d):
    warmbg(d, t, (50, 50, 80), (18, 18, 34))
    d.rect(538, 520, 542, 1260, fill=A(WHITE, 0.3))
    # left thin smooth: ant slips back down repeatedly
    d.rect(80, 600, 500, 1260, fill=A(SKIN, 1), r=20); d.rect(80, 600, 500, 650, fill=A(WAX, 1), r=10)
    for x in range(100, 500, 60): d.rect(x, 650, x + 30, 1240, fill=A(WAX, 0.25))
    ph = (t * 0.7) % 1
    ant(d, 290, 1180 - 400 * min(ph, 0.6) / 0.6 + (900 * (ph - 0.6) ** 2 if ph > 0.6 else 0), 0.55, t, mood="scared" if ph > 0.6 else "sus", ang=-math.pi / 2, slip=1 if ph > 0.6 else 0, walk=2)
    tag(d, 290, 540, "薄薄一层", WAX_L, 1, 44)
    # right thick boulders: ant climbs over
    k = popk(t, at("thin", 2.5))
    if k > 0:
        rr_ = random.Random(4)
        for j in range(9): waxguy(d, 620 + (j % 3) * 120, 1180 - (j // 3) * 150, 70 * min(1, k), t + j, face_=False)
        u = pr(t, at("thin", 3.2), at("thin", 8))
        ant(d, lerp(620, 900, u), 1100 - 380 * math.sin(u * math.pi * 0.9), 0.55, t, mood="happy", ang=-0.5 + u, walk=1.5)
        tag(d, 810, 540, "堆太厚", (255, 130, 100), ap(t, at("thin", 2.5)), 44, tc=WHITE)
        if u > 0.3: ptag(d, t, at("thin", 5), 810, 1360, "反而能爬", WHITE, 40)
def s_belt(t, d):
    warmbg(d, t, (90, 34, 50), (40, 14, 26))
    top, bot = canal(d, t, 960, wax=0.6)
    # conveyor arrows on skin walls, moving outward (to the left)
    for yy in (top - 70, bot + 70):
        for j in range(8):
            x = 1000 - ((t * 120 + j * 140) % 1120)
            arrow(d, x + 50, yy, x - 30, yy, WHITE, 0.5, 10)
    for j in range(4):
        x = 960 - ((t * 120 + j * 260) % 1100)
        waxguy(d, x, bot - 30, 40, t + j, face_=False, dry=cl((960 - x) / 900))
    ptag(d, t, at("belt", 0.4), 540, 330, "传送带", WHITE, 70)
    kk = popk(t, at("belt", 3), "bouncy")
    if kk > 0:
        d.rect(360, 420, 720, 600, fill=A((248, 244, 230), 1), r=20); d.rect(360, 420, 720, 470, fill=A((200, 90, 80), 1), r=20)
        d.text(540, 545, "8~10 周", int(60 * min(1, kk)), A(NAVYT, 1), k=1)
    if t > at("belt", 1.5): ptag(d, t, at("belt", 1.5), 160, 1500, "← 出口", WHITE, 36)
def s_card(t, d):
    grad(d, (110, 60, 40), (50, 24, 16))
    for i in range(12): d.circ(540, 860, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 680 * (0.8 + 0.2 * k), 960 * (0.8 + 0.2 * k); cx_, cy_ = 540, 840; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 80, "一句话学会", GOLD, a_, 32)
    waxguy(d, cx_, cy_ - 130, 90, t, mood="proud", a=a_)
    d.text(cx_, cy_ + 20, "耳屎是又滑又黏的防虫墙", 40, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("滑：小孔吸走蚂蚁脚底的水", "黏：粘在身上清不干净", "薄薄一层最管用，别掏太勤", "注意：目前是实验室里测的火蚁")):
        kk = popk(t, at("card", 1.2 + i * 1.6))
        if kk > 0: d.text(cx_, cy_ + 120 + i * 66, s_, 33, A((70, 70, 90) if i < 3 else (190, 80, 60), ap(t, at("card", 1.2 + i * 1.6))), k=1)
def s_dig(t, d):
    warmbg(d, t, (60, 90, 110), (20, 34, 46))
    # big ear (side) + cotton swab crossed
    ex, ey = 420, 980
    d.ell(ex, ey, 250, 330, A(SKIN, 1)); d.ell(ex + 20, ey, 170, 250, A(SKIN_D, 1)); d.ell(ex + 40, ey + 20, 110, 170, A(SKIN, 1)); d.ell(ex + 60, ey + 40, 40, 50, A(EARIN, 1))
    face(d, ex - 120, ey - 170, 70, "happy" if t > at("dig", 2) else "scared", 1)
    u = E.ease_out_cubic(pr(t, at("dig", 0.2), at("dig", 1)))
    sx_, sy_ = lerp(1100, 700, u), lerp(700, 900, u)
    d.line([(sx_, sy_), (sx_ + 330, sy_ - 260)], A(WHITE, 1), 18)
    d.ell(sx_, sy_, 34, 26, A((250, 250, 250), 1)); d.ell(sx_ + 330, sy_ - 260, 34, 26, A((250, 250, 250), 1))
    cross(d, sx_ + 160, sy_ - 130, 150, pr(t, at("dig", 1.2), at("dig", 1.8)), (240, 80, 70))
    ptag(d, t, at("dig", 0.3), 540, 330, "别老掏", WHITE, 80)
    if t > at("dig", 3): ptag(d, t, at("dig", 3), 540, 470, "会自己清洁", MINT, 56, tc=NAVYT)
def s_end(t, d):
    warmbg(d, t, (90, 34, 50), (40, 14, 26))
    top, bot = canal(d, t, 1000, wax=1.0)
    # wax guard with cap at entrance; ant bounces off
    gx, gy = 320, bot - 110
    waxguy(d, gx, gy, 100, t, mood="proud")
    d.rect(gx - 70, gy - 140, gx + 70, gy - 96, fill=A((60, 90, 170), 1), r=14); d.rect(gx - 90, gy - 104, gx + 40, gy - 90, fill=A((40, 64, 130), 1), r=6)
    d.circ(gx, gy - 118, 12, fill=A(GOLD, 1))
    t0 = at("end", 1.5)
    if t < t0: ant(d, lerp(-100, gx - 150, pr(t, T["end"], t0)), 1060, 0.7, t, mood="sus", walk=2)
    else:
        u = t - t0; ant(d, gx - 150 - 500 * u, 1060 - 400 * u + 600 * u * u, 0.7, t, mood="dizzy", ang=-u * 8, slip=1)
    if t < t0: ptag(d, t, T["end"] + 0.05, 540, 300, "耳屎", WAX_L, 110)
    else: slamtxt(d, t, t0, "防虫保安", 300, 130, WHITE)
    ra = ap(t, at("end", 3.5), 0.3)
    if ra > 0:
        d.rect(170, 395, 910, 505, fill=A((30, 12, 20), 0.6 * ra), r=20)
        d.text(540, 428, "Ancalle 等 2026 · Soft Matter", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 472, "实验室火蚁实验；防虫作用为论文假说", 25, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "耳屎", "q": "有啥用", "reveal": "防虫墙", "study": "蚂蚁", "samples": "耳屎", "climb": "火蚁", "rough": "爪子", "smooth": "滑下来",
      "pad": "吸盘", "pore": "吸走", "sponge": "两倍", "tunnel": "粘上", "groom": "弄不干净", "both": "又滑又黏", "skin": "皮肤细胞", "thin": "薄薄一层",
      "belt": "传送带", "dig": "自己清洁", "end": "防虫保安"}
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
                    j = x.index(hw); parts = [(x[:j], WHITE), (hw, WAX_L), (x[j + len(hw):], WHITE)]
                    xx = 540 - d.tlen(x, 54, 1) / 2
                    for p_, c_ in parts:
                        if p_: d.text(xx, yy, p_, 54, A(c_, al), anchor="lm", k=1); xx += d.tlen(p_, 54, 1)
                else: d.text(540, yy, x, 54, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇人体"; w = d.tlen(s, 28, 1) + 50
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
    img = Image.new("RGB", (W, H), (40, 20, 30)); d = D(img); key = None
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/ew_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/ew_sheet.png")
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
