import sys, subprocess
from fx import *
from cues import *

XFE = (222, 74, 52); FE_D = (160, 44, 40); FE_L = (255, 150, 90); BELLY = (255, 196, 120)
CREST = (255, 196, 40); CREST_D = (230, 130, 30); BEAK = (255, 214, 92); BEAK_D = (214, 150, 50); LEGC = (236, 150, 60)
TRX = (88, 140, 84); TRX_D = (58, 100, 62); TRX_L = (150, 196, 120)
PEACH = (255, 150, 110); PEACH_L = (255, 206, 160); PEACH_D = (232, 96, 86); LEAFC = (96, 180, 84); PIT = (150, 92, 60)
NAVYT = (24, 20, 40); GOOD = (90, 220, 120); BAD = (250, 70, 70); GOLD = (255, 200, 60); TURK = (140, 92, 60); TURK_D = (100, 64, 44)
BONE = (246, 236, 214); XR = (110, 220, 255)

def popk(t, t0): return min(1, back(pr(t, t0, t0 + 0.2)))
def tag(d, x, y, s, col, a=1.0, size=40, tc=NAVYT):
    if a <= 0.01: return
    w = d.tlen(s, size, 1) + 44
    d.rect(x - w / 2, y - size * 0.78, x + w / 2, y + size * 0.78, fill=A(col, 0.95 * a), r=size * 0.6)
    d.text(x, y, s, size, A(tc, a), k=1)
def bubble(d, x, y, s, side, col, tcol, a, size=44):
    if a <= 0: return
    w = d.tlen(s, size, 1) + 60; x0 = x if side < 0 else x - w
    d.rect(x0, y - 48, x0 + w, y + 48, fill=A(col, a), r=36)
    tx = x0 + 40 if side < 0 else x0 + w - 40
    d.poly([(tx - 14, y + 36), (tx - (22 if side < 0 else -22), y + 78), (tx + 14, y + 36)], A(col, a))
    d.text(x0 + w / 2, y, s, size, A(tcol, a), k=1)
def check(d, x, y, s, k, col, a=1.0):
    p = [(x - s, y), (x - s * 0.3, y + s * 0.7), (x + s, y - s * 0.8)]
    if k <= 0: return
    if k < 0.5: d.line([p[0], (lerp(p[0][0], p[1][0], k * 2), lerp(p[0][1], p[1][1], k * 2))], A(col, a), s * 0.3)
    else: d.line([p[0], p[1], (lerp(p[1][0], p[2][0], (k - 0.5) * 2), lerp(p[1][1], p[2][1], (k - 0.5) * 2))], A(col, a), s * 0.3)
def cross(d, x, y, s, k, col, a=1.0):
    if k <= 0: return
    d.line([(x - s, y - s), (x - s + 2 * s * min(1, k * 2), y - s + 2 * s * min(1, k * 2))], A(col, a), s * 0.3)
    if k > 0.5: d.line([(x + s, y - s), (x + s - 2 * s * (k - 0.5) * 2, y - s + 2 * s * (k - 0.5) * 2)], A(col, a), s * 0.3)
def title(d, t, t0, s, y=330, size=110, col=WHITE):
    k = back(pr(t, t0, t0 + 0.22))
    if k > 0: d.text(540, y, s, int(size * (0.7 + 0.3 * k)), A(col, min(1, k * 1.4)), k=1)
def arrow(d, x0, y0, x1, y1, col, a=1.0, w=16):
    L = math.hypot(x1 - x0, y1 - y0) + 1e-6; ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    bx, by = x1 - ux * w * 2.4, y1 - uy * w * 2.4
    d.line([(x0, y0), (bx, by)], A(col, a), w)
    d.poly([(bx + nx * w * 1.6, by + ny * w * 1.6), (x1, y1), (bx - nx * w * 1.6, by - ny * w * 1.6)], A(col, a))
def star(d, x, y, r, col, a=1.0, n=9, rot=0):
    if r <= 1: return
    pts = []
    for i in range(n * 2):
        ang = rot + i * math.pi / n; rr = r if i % 2 == 0 else r * 0.55
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    d.poly(pts, A(col, a))
def sweat(d, x, y, s, a=1.0):
    d.circ(x, y, s, fill=A(CYAN, a)); d.poly([(x - s * 0.9, y - s * 0.3), (x, y - s * 2.2), (x + s * 0.9, y - s * 0.3)], A(CYAN, a))



# ---------------- palette ----------------
SAND = (226, 186, 120); SAND_D = (184, 140, 84); SAND_L = (246, 214, 160); SKY1 = (120, 180, 240); SKY2 = (250, 214, 160)
LAR = (244, 226, 180); LAR_D = (204, 180, 130); LAR_L = (255, 246, 220); ANTC = (200, 60, 40); ANT_D = (140, 36, 28)
ALC = (150, 110, 70); ALC_D = (100, 70, 44); FLYB = (36, 34, 40); FLYA = (210, 150, 70); WINGF = (255, 240, 190)
SNOW = (245, 248, 255); MTN = (110, 120, 160); MTN_D = (80, 88, 130); SEPIA = (196, 160, 110); SEPIA_D = (120, 90, 60)
rr_ = random.Random(9)
GRAINS = [(rr_.uniform(0, 1080), rr_.uniform(0, 1), rr_.uniform(2, 5)) for _ in range(160)]

def mountains(d, y=900, a=1.0, col=MTN):
    pts = [(-40, y), (80, y - 300), (200, y - 180), (340, y - 420), (470, y - 230), (600, y - 480), (760, y - 260), (900, y - 380), (1120, y - 150), (1120, y)]
    d.poly(pts, A(col, a))
    for (x0, y0) in ((340, y - 420), (600, y - 480), (900, y - 380), (80, y - 300)):
        d.poly([(x0, y0), (x0 - 50, y0 + 70), (x0 - 15, y0 + 55), (x0 + 10, y0 + 75), (x0 + 50, y0 + 70)], A(SNOW, a))

def sand_scene(d, t, cx=540, gy=900, w=330, depth=360, sky=(SKY1, SKY2), mtn=True):
    grad(d, sky[0], sky[1], 0, gy)
    if mtn: mountains(d, gy, 1, MTN)
    grad(d, SAND, SAND_D, gy, OH)
    d.poly([(cx - w, gy), (cx, gy + depth), (cx + w, gy)], A(SAND_D, 1))
    d.poly([(cx - w, gy), (cx, gy + depth), (cx - w * 0.2, gy)], A(mix(SAND_D, (0, 0, 0), 0.12), 1))
    for x, u, r in GRAINS:
        y = gy + 20 + u * (OH - gy)
        if abs(x - cx) < w * (1 - (y - gy) / depth) and y < gy + depth: continue
        d.circ(x, y, r, fill=A(SAND_L, 0.5))

def larva(d, x, y, s, t, mood="smug", a=1.0, curl=0.0, ang=0.0, n=13, wig=1.0):
    pts = []; px, py = x, y; hd = ang
    for i in range(n):
        pts.append((px, py))
        hd += curl * 2 * math.pi * 0.92 / n + 0.08 * wig * math.sin(t * 5 + i * 0.7)
        px += math.cos(hd) * 26 * s; py += math.sin(hd) * 26 * s
    rad = [0.55, 0.65, 0.72, 0.78, 0.84, 0.9, 0.95, 1.0, 1.05, 1.08, 1.0, 0.85, 0.65]
    for i in range(n - 1, -1, -1):
        X, Y = pts[i]; r = 34 * s * rad[i]
        d.circ(X, Y, r, fill=A(LAR_D, a)); d.circ(X - r * 0.08, Y - r * 0.1, r * 0.9, fill=A(LAR, a))
        d.circ(X - r * 0.3, Y - r * 0.38, r * 0.25, fill=A(LAR_L, 0.6 * a))
        if i == n - 3:
            for j in range(6):
                aa = hd + math.pi / 2 + (j - 2.5) * 0.25
                d.line([(X, Y), (X + math.cos(aa) * r * 1.5, Y + math.sin(aa) * r * 1.5)], A(SAND_D, a), 3 * s)
    hx, hy = pts[0]; hr = 34 * s * 0.55
    d.circ(hx, hy, hr, fill=A((150, 100, 60), a))
    d.ell(hx, hy + hr * 0.9, hr * 0.35, hr * 0.25, A(INK, a))
    for sd in (-1, 1):
        ex, ey = hx + sd * hr * 0.45, hy - hr * 0.15
        if mood == "happy": d.arc(ex, ey + hr * .1, hr * .3, hr * .25, 200, 340, A(INK, a), 4 * s)
        else:
            d.circ(ex, ey, hr * 0.33, fill=A(WHITE, a)); d.circ(ex, ey + hr * 0.03, hr * 0.17, fill=A(INK, a))
            if mood == "smug": d.line([(ex - hr * .35, ey - hr * (.45 if sd < 0 else .3)), (ex + hr * .35, ey - hr * (.3 if sd < 0 else .45))], A(INK, a), 4 * s)
    return pts

def ant(d, x, y, s, t, mood="happy", a=1.0, ang=0.0, walk=1.0, flip=1):
    c, sn = math.cos(ang), math.sin(ang)
    def T_(u, v): u *= flip; return x + (u * c - v * sn) * s, y + (u * sn + v * c) * s
    for i in range(3):
        sw = 20 * math.sin(t * 16 * walk + i * 2.1) * walk
        for sd in (0,):
            d.line([T_(-20 + i * 30, 10), T_(-30 + i * 30 + sw, 50), T_(-40 + i * 34 + sw, 80)], A(ANT_D, a), 6 * s)
    d.ell(*T_(-60, 0), 48 * s, 36 * s, A(ANTC, a)); d.ell(*T_(5, 0), 26 * s, 20 * s, A(ANTC, a)); d.circ(*T_(60, -10), 32 * s, fill=A(ANTC, a))
    d.ell(*T_(-70, -14), 18 * s, 9 * s, A((255, 140, 120), 0.6 * a))
    for k in (-1, 1): d.line([T_(75, -35), T_(100, -80 + k * 10), T_(125, -90 + k * 20)], A(ANT_D, a), 4 * s)
    ex, ey = T_(72, -18); er = 13 * s
    big = 1.35 if mood == "shock" else 1.0
    d.circ(ex, ey, er * big, fill=A(WHITE, a)); d.circ(ex + flip * 3 * s, ey, er * (0.4 if mood == "shock" else 0.55), fill=A(INK, a))
    mx, my = T_(80, 8)
    if mood == "shock": d.ell(mx, my, 6 * s, 9 * s, A(INK, a)); sweat(d, *T_(40, -60), 8 * s, a)
    else: d.arc(mx, my - 4 * s, 10 * s, 7 * s, 20, 160, A(INK, a), 3 * s)

def antlion(d, x, y, s, t, a=1.0):
    d.ell(x, y, 110 * s, 90 * s, A(ALC, a)); d.ell(x - 20 * s, y - 25 * s, 60 * s, 30 * s, A(mix(ALC, WHITE, 0.3), 0.6 * a))
    for i in range(4): d.arc(x, y + 10 * s, 100 * s - i * 18 * s, 70 * s, 200, 340, A(ALC_D, 0.4 * a), 4 * s)
    hx, hy = x, y - 90 * s
    d.circ(hx, hy, 40 * s, fill=A(ALC_D, a))
    for sd in (-1, 1):
        d.line([(hx + sd * 20 * s, hy - 20 * s), (hx + sd * 70 * s, hy - 90 * s), (hx + sd * 30 * s, hy - 140 * s)], A(ALC_D, a), 12 * s)
        d.circ(hx + sd * 16 * s, hy - 5 * s, 9 * s, fill=A(WHITE, a)); d.circ(hx + sd * 16 * s, hy - 4 * s, 4.5 * s, fill=A(INK, a))
    for sd in (-1, 1):
        for j in range(3): d.line([(x + sd * 80 * s, y - 20 * s + j * 30 * s), (x + sd * 140 * s, y + j * 30 * s)], A(ALC_D, a), 7 * s)

def fly(d, x, y, s, t, a=1.0, flap=1.0, mood="happy"):
    f = lerp(0.3, 0.5 + 0.5 * math.sin(t * 40), flap)
    for sd in (-1, 1):
        wy = -40 - 60 * f
        d.poly([(x + sd * 20 * s, y - 20 * s), (x + sd * 240 * s, y + (wy + 40) * s), (x + sd * 260 * s, y + (wy + 90) * s), (x + sd * 40 * s, y + 20 * s)], A(WINGF, 0.55 * a))
        d.line([(x + sd * 20 * s, y - 20 * s), (x + sd * 250 * s, y + (wy + 60) * s)], A((200, 170, 110), 0.6 * a), 3 * s)
    d.ell(x, y + 150 * s, 40 * s, 120 * s, A(FLYA, a))
    for i in range(5): d.arc(x, y + 80 * s + i * 30 * s, 40 * s, 14 * s, 20, 160, A(mix(FLYA, (0, 0, 0), 0.25), a), 3 * s)
    d.ell(x, y, 62 * s, 58 * s, A(FLYB, a)); d.ell(x - 18 * s, y - 20 * s, 18 * s, 10 * s, A(FLYA, 0.9 * a)); d.ell(x + 18 * s, y - 20 * s, 18 * s, 10 * s, A(FLYA, 0.9 * a))
    hx, hy = x, y - 80 * s
    d.circ(hx, hy, 36 * s, fill=A(FLYB, a))
    for sd in (-1, 1):
        d.circ(hx + sd * 20 * s, hy - 4 * s, 15 * s, fill=A((160, 50, 50), a)); d.circ(hx + sd * 22 * s, hy - 8 * s, 6 * s, fill=A(WHITE, 0.8 * a))
        d.line([(hx + sd * 10 * s, hy - 30 * s), (hx + sd * 40 * s, hy - 90 * s), (hx + sd * 55 * s, hy - 110 * s)], A(FLYA, a), 5 * s)
    d.ell(hx, hy + 32 * s, 8 * s, 7 * s, A((90, 60, 50), a))
    if mood == "happy": d.arc(hx, hy + 14 * s, 12 * s, 8 * s, 20, 160, A(WHITE, 0.8 * a), 3 * s)
    for sd in (-1, 1):
        for j in range(3): d.line([(x + sd * 30 * s, y + 20 * s + j * 18 * s), (x + sd * 80 * s, y + 70 * s + j * 30 * s), (x + sd * 95 * s, y + 120 * s + j * 30 * s)], A(FLYB, a), 4 * s)

def grains_fall(d, t, cx, gy, w, depth, a=1.0, n=40):
    for i in range(n):
        u = (t * 0.9 + i / n) % 1; side = -1 if i % 2 else 1
        x0 = cx + side * w * (1 - u); y0 = gy + depth * u
        d.circ(x0 + side * (i % 5) * 4, y0 - 6 - (i % 3) * 5, 4 + i % 3, fill=A(SAND_L, a * 0.9))

def qmark(d, x, y, size, t, a=1.0, col=WHITE):
    d.text(x, y + 8 * math.sin(t * 5 + x), "?", size, A(col, a), k=1)

# ---------------- scenes ----------------
def s_hook(t, d):
    frz = t >= HOOK_STOP; tt = min(t, HOOK_STOP)
    sand_scene(d, tt, 540, 640, 380, 420)
    grains_fall(d, tt, 540, 640, 380, 420, 0.9)
    pop = ease(pr(tt, HOOK_HIT, HOOK_HIT + 0.2)) * (1 - 0.5 * ease(pr(tt, HOOK_HIT + 1.4, HOOK_HIT + 2.0)))
    d.ell(540, 1180, 120, 150, A(mix(SAND_D, (0, 0, 0), 0.3), 0.8))
    larva(d, 540, 1080 - 80 * pop, 1.45, tt, "smug", 1, curl=0.3, ang=math.pi / 2, wig=0.5, n=12)
    for sd in (-1, 1): d.line([(540 + sd * 12, 1090 - 80 * pop), (540 + sd * 44, 1050 - 80 * pop - 30 * pop), (540 + sd * 18, 1010 - 80 * pop - 40 * pop)], A((110, 60, 30), 1), 10)
    tag(d, 760, 1180, "剖面图", WHITE, 0.8, 26, SAND_D)
    if t >= HOOK_HIT: sparks(d, 540, 1040, t, HOOK_HIT, 60, 1300, SAND_L, 1, 4, 1.1)
    kk = back(pr(t, -0.2, HOOK_HIT + 0.1)); k2 = pulse(t, [HOOK_HIT], 6)
    if kk > 0: d.text(540, 330, "死亡漏斗", int(150 * (0.6 + 0.4 * kk) * (1 + 0.08 * k2)), A((150, 30, 30), 1), k=1)
    tag(d, 540, 480, "西藏沙坑里的伏击者", WHITE, popk(t, qb(1.6)), 36)
    if frz: glow(d, 540, 1000, 160, WHITE, pr(t, HOOK_STOP, HOOKCUT))
def s_ant(t, d):
    sand_scene(d, t, 640, 760, 320, 420)
    u = pr(t, T["ant"], at("ant", 2.5))
    ax = lerp(150, 330, u); slip = ease(pr(t, at("ant", 2.5), at("ant", 3.6)))
    ant(d, ax + 80 * slip, 700 + 150 * slip, 1.1, t, "shock" if slip > 0 else "happy", 1, ang=0.8 * slip, walk=1 - slip)
    title(d, t, T["ant"], "一脚踩空", 300, 120, (150, 30, 30))
    if slip > 0: d.text(ax + 60, 560, "！", 110, A(YEL, 1), k=1)
def s_slide(t, d):
    sand_scene(d, t, 540, 560, 440, 640, mtn=False)
    grains_fall(d, t * 1.6, 540, 560, 440, 640, 1, 70)
    u = t - T["slide"]; p = 0.2 + 0.55 * ease(pr(t, T["slide"], nxt("slide")))
    px = lerp(100, 540, p); py = lerp(560, 1200, p) - 30 * abs(math.sin(u * 7))
    ant(d, px, py - 50, 1.05, t, "shock", 1, ang=0.95, walk=2.0, flip=-1)
    title(d, t, T["slide"], "越爬越往下", 300, 110, (120, 40, 30))
    for j in range(3):
        k = popk(t, at("slide", 1 + j))
        if k > 0: arrow(d, 760 - j * 40, 760 + j * 140, 680 - j * 40, 900 + j * 140, WHITE, 0.7 * k, 10)
def s_bottom(t, d):
    grad(d, (60, 44, 30), (20, 14, 10))
    d.poly([(0, 400), (540, 1200), (1080, 400)], A((90, 66, 40), 1)); d.poly([(0, 400), (540, 1200), (300, 400)], A((70, 50, 32), 1))
    bl = 1 if (t * 1.3) % 1 > 0.1 else 0.1
    for sd in (-1, 1):
        d.circ(540 + sd * 40, 1120, 18, fill=A((255, 240, 120), bl)); d.circ(540 + sd * 40, 1120, 8, fill=A(INK, bl))
    glow(d, 540, 1120, 140, (255, 230, 120), 0.25 * bl)
    title(d, t, T["bottom"], "坑底……", 300, 120)
def s_q(t, d):
    grad(d, (70, 50, 90), (24, 16, 34))
    antlion(d, 540, 960, 1.2 * popk(t, T["q"] + 0.05), t, 0.85)
    for i, (x, y) in enumerate(((260, 640), (820, 700), (300, 1180), (800, 1150))):
        if t > at("q", 0.3 + i * 0.5): qmark(d, x, y, 110, t, 0.9, YEL)
    title(d, t, T["q"], "蚁狮？", 300, 140)
def s_reveal(t, d):
    rays(d, t, (255, 200, 110), (220, 120, 60))
    larva(d, 330, 700, 1.35, t, "smug", 1, curl=0.18, ang=0.45)
    stamp(d, t, BIG2, "蛆狮！", 540, 330, 170, (160, 30, 30))
    tag(d, 540, 490, "苍蝇的幼虫", WHITE, popk(t, at("reveal", 1.5)), 38)
    if t >= BIG2: sparks(d, 540, 900, t, BIG2, 60, 1300, SAND_L, 1, 3, 1.2); sparks(d, 540, 900, t, BIG2 + 0.05, 40, 1000, WHITE, 1, 5, 1.0)
def s_fam(t, d):
    grad(d, (60, 120, 180), (24, 50, 100))
    title(d, t, T["fam"], "苍蝇界独一家", 300, 104)
    for i in range(20):
        x = 230 + (i % 5) * 155; y = 600 + (i // 5) * 150
        k = popk(t, T["fam"] + 0.1 + i * 0.05)
        if k <= 0: continue
        hl = i == 12 and t > at("fam", 3)
        if hl: glow(d, x, y, 120, YEL, 0.5)
        fly(d, x, y - 10, 0.28 * k * (1.5 if hl else 1), t, 1 if hl else 0.45, flap=1 if hl else 0)
    k = popk(t, at("fam", 3.5))
    if k > 0: tag(d, 540, 1200, "唯一会挖陷阱的一科", YEL, k, 36)
def s_same(t, d):
    grad(d, (240, 200, 140), (210, 160, 100))
    title(d, t, T["same"], "不同家 · 同一招", 300, 96, (110, 50, 30))
    d.rect(538, 420, 542, 1230, fill=A((110, 50, 30), 0.5))
    for x, who, lab in ((330, "al", "蚁狮"), (750, "wl", "蛆狮")):
        d.poly([(x - 170, 1050), (x, 1200), (x + 170, 1050)], A(SAND_D, 1)); d.rect(x - 200, 1040, x + 200, 1056, fill=A(SAND, 1))
        if who == "al": antlion(d, x, 800, 0.8, t)
        else: larva(d, x - 120, 760, 0.9, t, "smug", 1, curl=0.12, ang=0.4)
        tag(d, x, 520, lab, (110, 50, 30), 1, 40, WHITE)
    k1 = popk(t, at("same", 1.5)); k2 = popk(t, at("same", 3.5))
    if k1 > 0: d.text(540, 640, "≠", int(120 * k1), A(BAD, 1), k=1); tag(d, 330, 1130, "脉翅目", WHITE, k1, 28); tag(d, 750, 1130, "双翅目", WHITE, k1, 28)
    if k2 > 0: d.text(540, 1000, "=", int(130 * k2), A(GOOD, 1), k=1)
def s_y1978(t, d):
    grad(d, (230, 205, 160), (190, 160, 110))
    k = popk(t, T["y1978"] + 0.05)
    d.rect(200, 560, 880, 1180, fill=A(SEPIA, k), r=20); d.rect(230, 590, 850, 1150, outline=A(SEPIA_D, k), w=6, r=12)
    title(d, t, T["y1978"], "1978", 300, 170, SEPIA_D)
    if k > 0:
        d.rect(380, 680, 700, 1080, fill=A((240, 240, 230), 0.5 * k), r=40)
        larva(d, 450, 760, 0.7, t, "happy", k, curl=0.35, ang=0.9, wig=0.3)
    tag(d, 540, 480, "西藏 · 亚东", WHITE, popk(t, at("y1978", 1.5)), 36, SEPIA_D)
    tag(d, 540, 1220 - 10, "只有幼虫", SEPIA_D, popk(t, at("y1978", 3)), 34, WHITE)
def s_wait(t, d):
    grad(d, (60, 70, 110), (24, 26, 50))
    yr = 1978 + int(46 * ease(pr(t, T["wait"], at("wait", 4))))
    d.text(540, 360, f"{yr}", 150, A(YEL, 1), k=1)
    tag(d, 540, 500, "年复一年", WHITE, 1, 34)
    fly(d, 540, 820, 0.8, t, 0.25, flap=0)
    d.text(540, 900, "?", 260, A(WHITE, 0.9), k=1)
    tag(d, 540, 1180, "成虫：没人见过", WHITE, popk(t, at("wait", 1)), 34)
def s_y2025(t, d):
    grad(d, (140, 200, 250), (220, 240, 210), 0, 1000); mountains(d, 1000, 1, MTN); grad(d, (110, 160, 90), (70, 120, 60), 1000, OH)
    title(d, t, T["y2025"], "2025 科考", 300, 120, (30, 50, 90))
    d.poly([(220, 1080), (330, 940), (440, 1080)], A((230, 120, 60), 1)); d.poly([(300, 1080), (330, 1000), (360, 1080)], A((120, 60, 30), 1))
    u = ease(pr(t, at("y2025", 1), at("y2025", 3)))
    fx_, fy_ = lerp(760, 600, u), lerp(620, 760, u) + 20 * math.sin(t * 6)
    nx, ny = lerp(780, 600, ease(pr(t, at("y2025", 2.5), at("y2025", 3.3)))), 760
    fly(d, fx_, fy_, 0.38, t, 1, 1)
    d.line([(nx + 100, ny + 400), (nx, ny + 60)], A((140, 100, 60), 1), 10)
    d.circ(nx, ny, 90, outline=A(WHITE, 1), w=8); d.circ(nx, ny, 86, fill=A(WHITE, 0.25))
    k = popk(t, at("y2025", 3.3))
    if k > 0: tag(d, 540, 480, "抓到成虫了！", GOOD, k, 38, WHITE)
def s_newsp(t, d):
    rays(d, t, (255, 220, 120), (240, 160, 70))
    fly(d, 540, 820, 1.0, t, 1, 1)
    stamp(d, t, T["newsp"] + 0.03, "新物种！", 540, 340, 140, (160, 30, 30))
    sparks(d, 540, 820, t, T["newsp"] + 0.03, 40, 900, YEL, 1, 7, 1.0)
def s_size(t, d):
    grad(d, (250, 240, 220), (220, 205, 180))
    title(d, t, T["size"], "幼虫比成虫还长", 300, 96, (90, 50, 30))
    k1 = ease(pr(t, at("size", 0.5), at("size", 2))); k2 = ease(pr(t, at("size", 2.5), at("size", 4.5)))
    fly(d, 290, 640, 0.6, t, 1, 0.3)
    d.rect(450, 690, 450 + 19 * 15 * k1, 730, fill=A(FLYA, 1), r=10); d.text(470 + 19 * 15 * k1 + 60, 710, "19", 44, A((90, 50, 30), k1), k=1)
    larva(d, 200, 960, 1.0, t, "happy", 1, curl=0.0, ang=0.0, wig=0.3)
    d.rect(450, 1080, 450 + 28 * 15 * k2, 1120, fill=A(LAR_D, 1), r=10); d.text(450 + 28 * 15 * k2 - 40 if k2 > 0.9 else 1000, 1040, "28", 44, A((90, 50, 30), k2), k=1)
    for i in range(13): d.line([(190 + i * 54, 1170), (190 + i * 54, 1190 if i % 5 else 1205)], A((90, 50, 30), 0.7), 4)
    d.text(540, 1235 - 20, "单位：毫米", 28, A((90, 50, 30), 0.8), k=1)
def s_nofood(t, d):
    grad(d, (255, 210, 180), (230, 150, 140))
    title(d, t, T["nofood"], "一辈子不吃饭？", 300, 100, (110, 30, 40))
    fly(d, 380, 760, 0.9, t, 1, 0.4)
    k = popk(t, at("nofood", 1))
    if k > 0:
        d.circ(470, 735, 46, outline=A(RED, k), w=6); arrow(d, 600, 640, 500, 715, RED, k, 10); tag(d, 680, 610, "嘴很短", RED, k, 32, WHITE)
    k2 = popk(t, at("nofood", 2.8))
    if k2 > 0:
        d.ell(760, 1080, 130 * k2, 40 * k2, A(WHITE, 1)); cross(d, 760, 1060, 70, ease(pr(t, at("nofood", 3), at("nofood", 3.6))), BAD)
        tag(d, 540, 1190, "可能不进食", WHITE, k2, 32, (110, 30, 40))
def s_home(t, d):
    grad(d, (150, 200, 240), (200, 230, 250), 0, 1000)
    for i in range(40):
        u = (t * 1.2 + i / 40) % 1; x = (i * 97) % 1080; y = u * 1000
        d.line([(x, y), (x - 8, y + 30)], A((120, 160, 220), 0.6), 3)
    grad(d, (90, 150, 210), (60, 110, 180), 1000, 1150)
    for i in range(6): d.arc(150 + i * 160, 1060 + (i % 2) * 40, 40, 10, 200, 340, A(WHITE, 0.5), 4)
    grad(d, SAND, SAND_D, 1150, OH)
    d.poly([(380, 1150), (420, 700), (600, 600), (860, 680), (930, 1000), (900, 1150)], A((120, 116, 120), 1))
    d.poly([(420, 1150), (440, 760), (600, 660), (820, 720), (880, 1150)], A((150, 146, 150), 1))
    d.rect(460, 1070, 880, 1150, fill=A(SAND_L, 1))
    for j in range(3): x = 520 + j * 140; d.poly([(x - 40, 1070), (x, 1120), (x + 40, 1070)], A(SAND_D, 1))
    title(d, t, T["home"], "大石头下 · 不淋雨", 300, 90, (30, 60, 110))
    tag(d, 670, 1220 - 20, "河沙", SAND_D, popk(t, at("home", 2)), 32, WHITE)
def s_pose(t, d):
    grad(d, (120, 90, 200), (50, 40, 110))
    c = ease(pr(t, at("pose", 1.5), at("pose", 2.5)))
    larva(d, lerp(200, 470, c), lerp(820, 940, c), 1.5, t, "shock" if c > 0.2 else "happy", 1, curl=c * 0.95, ang=-math.pi / 2 * c, wig=1 - c)
    k = popk(t, at("pose", 1))
    if k > 0 and c < 0.5: d.circ(lerp(900, 640, k), 820, 40, fill=A((255, 210, 180), 1)); d.rect(lerp(900, 640, k), 800, lerp(900, 640, k) + 200, 840, fill=A((255, 210, 180), 1), r=20)
    k2 = popk(t, at("pose", 2.5))
    if k2 > 0: d.text(540, 330, "Ω", int(200 * k2), A(YEL, 1), k=1)
    else: title(d, t, T["pose"], "戳一下？", 300, 110)
    tag(d, 540, 1220 - 10, "Ω 形防御", YEL, k2, 34)
def s_name(t, d):
    grad(d, (140, 40, 50), (70, 20, 30))
    k = ease(pr(t, T["name"], at("name", 1)))
    d.rect(200, 520, 880, lerp(520, 1180, k), fill=A((250, 236, 200), 1), r=16)
    d.rect(180, 500, 900, 540, fill=A((180, 120, 60), 1), r=20); d.rect(180, lerp(520, 1180, k) - 20, 900, lerp(520, 1180, k) + 20, fill=A((180, 120, 60), 1), r=20)
    title(d, t, T["name"], "名字的来历", 300, 104, (255, 220, 160))
    if k > 0.9:
        d.text(540, 680, "仓央嘉措", int(110 * popk(t, at("name", 1))), A((120, 30, 30), 1), k=1)
        d.text(540, 800, "西藏诗人", 40, A((120, 70, 40), popk(t, at("name", 1.5))), k=1)
        k3 = popk(t, at("name", 2.5))
        d.text(540, 960, "Vermitigris", 46, A(NAVYT, k3)); d.text(540, 1020, "tsangyanggyatso", 46, A(NAVYT, k3))
        d.text(540, 1100, "仓央嘉措印穴虻", 36, A((120, 70, 40), k3), k=1)
def s_count(t, d):
    grad(d, (30, 90, 80), (12, 40, 36))
    title(d, t, T["count"], "全世界的蛆狮", 300, 100)
    flip_ = ease(pr(t, at("count", 2), at("count", 2.6)))
    n = "67" if flip_ > 0.5 else "66"; sc = abs(1 - 2 * flip_) if flip_ < 1 else 1
    d.rect(330, 560, 750, 560 + 380 * max(0.05, sc), fill=A((20, 24, 30), 1), r=30)
    if sc > 0.2: d.text(540, 560 + 190 * sc, n, int(260 * sc), A(YEL if n == "67" else WHITE, 1), k=1)
    k = popk(t, at("count", 2.7))
    if k > 0: tag(d, 540, 1050, "+1 来自西藏", YEL, k, 38); sparks(d, 540, 750, t, at("count", 2.6), 30, 800, YEL, 1, 9, 0.9)
    tag(d, 540, 1150, "种", WHITE, 1, 30)
def s_card(t, d):
    grad(d, (120, 80, 40), (60, 36, 20))
    for i in range(12): d.circ(540, 900, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1)
    if k <= 0: return
    w, h = 560 * (0.7 + 0.3 * k), 820 * (0.7 + 0.3 * k); cx, cy = 540, 880
    d.rect(cx - w / 2 + 14, cy - h / 2 + 18, cx + w / 2 + 14, cy + h / 2 + 18, fill=A((0, 0, 0), 0.3 * k), r=36)
    d.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=A((250, 244, 230), k), r=36)
    d.rect(cx - w / 2 + 24, cy - h / 2 + 24, cx + w / 2 - 24, cy + h / 2 - 24, outline=A((160, 30, 30), k), w=6, r=24)
    d.text(cx - w / 2 + 70, cy - h / 2 + 80, "Q", 70, A((160, 30, 30), k), k=1); d.text(cx + w / 2 - 70, cy + h / 2 - 80, "Q", 70, A((160, 30, 30), k), k=1)
    larva(d, cx - 150, cy - 140, 0.55 * k, t, "smug", k, curl=0.1, ang=0.2)
    tag(d, cx, cy + 70, "一句话学会", GOLD, k, 30)
    d.text(cx, cy + 160, "蛆狮 = 挖陷阱的蝇幼虫", 44, A((160, 30, 30), k), k=1)
    ek = popk(t, at("card", 1.5))
    if ek > 0: d.text(cx, cy + 240, "和蚁狮不同家，招数一样", 32, A(NAVYT, ek), k=1)
def s_end(t, d):
    sand_scene(d, t, 540, 860, 320, 300, sky=((255, 150, 100), (120, 60, 110)))
    larva(d, 470, 1080, 0.9, t, "happy", 1, curl=0.1, ang=-0.5)
    fly(d, 800, 760, 0.4, t, 1, 1)
    stamp(d, t, T["end"] + 0.05, "谜底揭晓", 540, 320, 110, YEL)
    ra = popk(t, at("end", 2))
    d.rect(170, 430, 910, 550, fill=A((20, 12, 30), 0.6 * ra), r=20)
    d.text(540, 468, "ZooKeys 1276 (2026) · Shan & Wang", 28, A(WHITE, 0.95 * ra))
    d.text(540, 510, "大理大学 · 西藏亚东、定结", 26, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

def subs(t, d):
    for a, b, s, key in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70
            w = max(d.tlen(x, 54, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 70 + 46, fill=A((15, 12, 26), 0.82 * al), r=22)
            for i, x in enumerate(ls): d.text(540, y0 + i * 70, x, 54, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇新物种"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)



SF = {n: globals()["s_" + n] for n in NAMES}
SECS = [(-1, HOOKCUT, s_hook)] + [(T[n], nxt(n), SF[n]) for n in NAMES[1:]]
SECS = [(a, (99 if n == len(SECS) - 1 else b), f) for n, (a, b, f) in enumerate(SECS)]
def cam(t):
    z = 1.0 + 0.04 * pulse(t, [HOOK_HIT, BIG2], 3)
    if T["q"] <= t < BIG2: z += 0.03 * eio(pr(t, T["q"], BIG2))
    if HOOK_STOP <= t < HOOKCUT: z += 0.05 * pr(t, HOOK_STOP, HOOKCUT)
    amp = 8 * pulse(t, [HOOK_HIT, BIG2], 5)
    sx, sy = shake(t, amp, 40)
    return z, 540 + sx, 900 + sy
def frame(t):
    img = Image.new("RGB", (W, H), (30, 20, 50)); d = D(img)
    if True:
        for a, b, sf in SECS:
            if a <= t < b: sf(t, d); break
        z, cx, cy = cam(t)
        cw, ch = W / z, H / z
        x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
        img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
        for c in CUTS:
            if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - (t - c) / 0.1)))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"/tmp/wl_test_{float(ts):05.2f}.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        last = None; errs = 0
        for i in range(i0, i1):
            try: last = frame(i / FPS).tobytes()
            except Exception as e: errs += 1; print('ERR', i, e, file=sys.stderr)
            if last: p.stdin.write(last)
        p.stdin.close(); p.wait(); print('errs', errs, file=sys.stderr)
