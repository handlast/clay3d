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
MO = (172, 140, 120); MO_D = (120, 96, 86); MO_L = (214, 190, 170); PINK = (255, 120, 170); PINK_L = (255, 190, 215)
WINGC = (150, 130, 118); WING_D = (104, 90, 84); BATC = (110, 70, 150); BAT_D = (72, 44, 104); BAT_L = (160, 120, 200)
NIGHT1 = (36, 28, 80); NIGHT2 = (12, 10, 34); CRT = (60, 255, 140); CRT_D = (10, 40, 24); US = (120, 240, 255)
SCALEC = (230, 200, 160); SCALE_D = (190, 150, 110)
rr_ = random.Random(5)
STARS = [(rr_.uniform(0, 1080), rr_.uniform(0, 1400), rr_.uniform(2, 5)) for _ in range(60)]

def night(d, t, k=1.0):
    grad(d, mix((60, 40, 110), NIGHT1, k), NIGHT2)
    for i, (x, y, r) in enumerate(STARS): d.circ(x, y, r, fill=A(WHITE, 0.35 + 0.3 * math.sin(t * 2 + i)))
    d.circ(820, 380, 90, fill=A((255, 246, 210), 0.9)); glow(d, 820, 380, 220, (255, 240, 200), 0.3)
    for i in range(9):
        x = i * 140 - 40; h = 260 + (i * 71) % 180
        d.poly([(x - 120, 1920), (x, 1920 - h - 380), (x + 120, 1920)], A((14, 12, 30), 1))

def moth(d, x, y, s, t, mood="happy", a=1.0, ang=0.0, flip=1, flap=1.0, tip=0.0, look=1.0):
    c, sn = math.cos(ang), math.sin(ang)
    def T_(u, v): u *= flip; return x + (u * c - v * sn) * s, y + (u * sn + v * c) * s
    def PG(pts, col, al=1.0): d.poly([T_(*p) for p in pts], A(col, a * al))
    f = 0.55 + 0.45 * math.sin(t * 38) if flap > 0 else 0.8
    f = lerp(0.8, f, flap)
    # far wings
    PG([(70, -20), (-90, -250 * f), (-230, -225 * f), (-90, -25)], WING_D)
    PG([(-40, -20), (-150, -130 * f), (-200, -70 * f)], mix(PINK, (0, 0, 0), 0.25))
    # antennae
    for k, (ax, ay) in enumerate(((330, -150), (310, -60))):
        pts = [(170 + j * (ax - 170) / 10, -30 + j * (ay + 30) / 10 + 12 * math.sin(j * 0.6 + t * 3 + k)) for j in range(11)]
        d.line([T_(*p) for p in pts], A(MO_D, a), 5 * s)
    # body: torpedo
    PG([(200, -10), (170, -55), (60, -62), (-120, -48), (-230, -12), (-250, 0), (-230, 14), (-120, 50), (60, 62), (170, 52)], MO)
    for j in range(5):
        u = -70 - j * 34
        PG([(u, -45 + j * 6), (u - 14, -42 + j * 6), (u - 14, 42 - j * 6), (u, 45 - j * 6)], PINK)
    PG([(150, -40), (40, -50), (-80, -38), (40, -30)], MO_L, 0.7)
    # tip glow
    if tip > 0:
        tx, ty = T_(-245, 0); glow(d, tx, ty, 90 * s, US, tip); d.circ(tx, ty, 14 * s, fill=A(WHITE, tip * a))
    # near wings
    PG([(80, 10), (-80, 265 * f), (-235, 235 * f), (-90, 30)], WINGC, 0.96)
    PG([(30, 40), (-120, 230 * f), (-60, 40)], MO_L, 0.25)
    PG([(-40, 25), (-150, 140 * f), (-205, 80 * f)], PINK, 0.9)
    # face
    ex, ey = T_(165, -15); er = 26 * s
    if mood == "happy": d.arc(ex, ey + er * 0.3, er * 0.8, er * 0.7, 200, 340, A(INK, a), 6 * s)
    elif mood == "dizzy":
        d.line([(ex - er * .7, ey - er * .7), (ex + er * .7, ey + er * .7)], A(INK, a), 6 * s); d.line([(ex - er * .7, ey + er * .7), (ex + er * .7, ey - er * .7)], A(INK, a), 6 * s)
    else:
        big = 1.25 if mood in ("shock", "scared") else 1.0
        d.circ(ex, ey, er * big, fill=A(WHITE, a)); d.circ(ex + flip * er * 0.3 * look, ey, er * (0.38 if mood == "shock" else 0.55), fill=A(INK, a))
        d.circ(ex + flip * er * 0.15, ey - er * 0.3, er * 0.18, fill=A(WHITE, a))
        if mood == "smug": d.line([(ex - er, ey - er * 1.0), (ex + er, ey - er * 0.6)], A(INK, a), 6 * s)
    mx, my = T_(190, 25)
    if mood in ("happy", "smug"): d.arc(mx, my - 6 * s, 16 * s, 12 * s, 20, 160, A(INK, a), 5 * s)
    elif mood == "dizzy": d.line([(mx - 12 * s + i * 4 * s, my + (3 if i % 2 else -3) * s) for i in range(7)], A(INK, a), 4 * s)
    else: d.ell(mx, my, 7 * s, 10 * s, A(INK, a))
    d.ell(*T_(140, 25), 13 * s, 8 * s, A((255, 140, 160), 0.6 * a))
    if mood in ("scared", "shock"): sweat(d, *T_(215, -70), 10 * s, a)

def bat(d, x, y, s, t, mood="hunt", a=1.0, flip=1, flap=1.0, mouth_open=0.0):
    f = lerp(0.7, 0.5 + 0.5 * math.sin(t * 14), flap)
    def T_(u, v): return x + u * s * flip, y + v * s
    for sd in (-1, 1):
        tipy = -200 + 260 * (1 - f)
        pts = [(0, -20), (sd * 120, tipy * 0.7 - 30), (sd * 300, tipy), (sd * 330, tipy + 60)]
        for j in range(4): pts.append((sd * (300 - j * 75), tipy + 120 + (j % 2) * -40 + j * 30))
        pts.append((0, 40))
        d.poly([T_(*p) for p in pts], A(BAT_D if sd < 0 else BATC, a))
        d.line([T_(0, -10), T_(sd * 120, tipy * 0.7 - 30), T_(sd * 300, tipy)], A(BAT_L, 0.6 * a), 6 * s)
    d.ell(*T_(0, 30), 80 * s, 100 * s, A(BATC, a)); d.ell(*T_(0, 50), 50 * s, 60 * s, A(BAT_L, 0.6 * a))
    hx, hy = T_(0, -60)
    for sd in (-1, 1):
        d.poly([T_(sd * 30, -90), T_(sd * 75, -200), T_(sd * 85, -70)], A(BATC, a)); d.poly([T_(sd * 42, -95), T_(sd * 72, -170), T_(sd * 72, -85)], A((230, 150, 190), a))
    d.circ(hx, hy, 72 * s, fill=A(BATC, a))
    er = 20 * s
    for sd in (-1, 1):
        ex, ey = hx + sd * 30 * s, hy - 10 * s
        if mood == "dizzy":
            for j in range(3): d.arc(ex, ey, er * (1 - j * 0.3), er * (1 - j * 0.3), (t * 600 + j * 90) % 360, (t * 600 + j * 90) % 360 + 260, A(WHITE, a), 3 * s)
        else:
            d.circ(ex, ey, er * (1.25 if mood == "shock" else 1.0), fill=A((255, 240, 120), a)); d.circ(ex + flip * 5 * s, ey, er * 0.45, fill=A(INK, a))
            if mood == "hunt": d.line([(ex - sd * er * 1.1, ey - er * 1.4), (ex + sd * er * 0.9, ey - er * 0.8)], A(INK, a), 6 * s)
    my = hy + 30 * s; mo = 8 + 26 * mouth_open
    d.ell(hx, my, 26 * s, mo * s * 0.6, A(INK, a))
    for sd in (-1, 1): d.poly([(hx + sd * 16 * s, my - 4 * s), (hx + sd * 8 * s, my - 4 * s), (hx + sd * 12 * s, my + 14 * s)], A(WHITE, a))
    if mood == "shock": d.text(hx + 110 * s * flip, hy - 110 * s, "！", int(80 * s), A(YEL, a), k=1)

def sonar(d, x, y, t, t0, dirx=1, col=CRT, a=1.0, n=3, spd=900, life=0.9, spread=40):
    for j in range(n):
        u = t - t0 - j * 0.12
        if 0 <= u < life:
            r = 40 + u * spd; al = a * (1 - u / life)
            d.arc(x, y, r, r, (0 if dirx > 0 else 180) - spread, (0 if dirx > 0 else 180) + spread, A(col, al), 9)

def zig(d, x, y, t, t0, a=1.0, n=4, col=US, life=1.0, spd=700):
    for j in range(n):
        u = (t - t0 - j * 0.15)
        if not (0 <= u < life): continue
        r = 50 + u * spd; al = a * (1 - u / life); pts = []
        for i in range(73):
            ang = i / 72 * 2 * math.pi; rr = r * (1 + 0.08 * (1 if i % 2 else -1))
            pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
        d.line(pts, A(col, al), 6)

def radar(d, cx, cy, r, t, stat=0.0, blip=None, lock=0.0, a=1.0):
    d.circ(cx, cy, r + 26, fill=A((40, 44, 56), a)); d.circ(cx, cy, r, fill=A(CRT_D, a))
    for j in (0.33, 0.66, 1.0): d.circ(cx, cy, r * j, outline=A(CRT, 0.35 * a), w=3)
    d.line([(cx - r, cy), (cx + r, cy)], A(CRT, 0.25 * a), 2); d.line([(cx, cy - r), (cx, cy + r)], A(CRT, 0.25 * a), 2)
    ang = t * 3.2
    for j in range(12):
        aa = ang - j * 0.05; d.line([(cx, cy), (cx + math.cos(aa) * r, cy + math.sin(aa) * r)], A(CRT, a * 0.5 * (1 - j / 12)), 6)
    if blip and stat < 0.6:
        bx, by = cx + blip[0] * r, cy + blip[1] * r
        d.circ(bx, by, 14 + 4 * math.sin(t * 10), fill=A(CRT, a)); glow(d, bx, by, 50, CRT, 0.6 * a)
        if lock > 0:
            L = lerp(160, 60, ease(lock)); col = A(RED, a)
            for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                d.line([(bx + sx * L, by + sy * L * 0.5), (bx + sx * L, by + sy * L), (bx + sx * L * 0.5, by + sy * L)], col, 7)
    if stat > 0:
        r2 = random.Random(int(t * 30))
        for i in range(int(380 * stat)):
            ang2 = r2.uniform(0, 2 * math.pi); rad = r * math.sqrt(r2.random())
            px, py = cx + math.cos(ang2) * rad, cy + math.sin(ang2) * rad
            d.rect(px, py, px + r2.uniform(6, 22), py + 5, fill=A(r2.choice([WHITE, CRT, US]), a * stat * r2.uniform(0.4, 1)))
        for i in range(5):
            yy = cy - r + r2.uniform(0, 2 * r); hw = math.sqrt(max(0, r * r - (yy - cy) ** 2))
            d.rect(cx - hw, yy, cx + hw, yy + 8, fill=A(WHITE, 0.25 * stat * a))

def wavebox(d, x0, y0, w, h, t, kind, a=1.0, col=US, prog=1.0):
    d.rect(x0, y0, x0 + w, y0 + h, fill=A((10, 14, 30), 0.8 * a), r=18)
    pts = []; n = 140; cy = y0 + h / 2
    r2 = random.Random(int(t * 15))
    for i in range(int(n * prog) + 1):
        u = i / n; xx = x0 + 20 + u * (w - 40)
        if kind == "burst":
            g = 1.0 if (math.sin(u * 23 + t * 9) > 0.55 or math.sin(u * 61 + t * 5) > 0.92) else 0.05
        else: g = 0.75 + 0.25 * math.sin(u * 30 + t * 6)
        pts.append((xx, cy + (r2.uniform(-1, 1)) * g * h * 0.4))
    if len(pts) > 1: d.line(pts, A(col, a), 4)

def lens(d, x, y, L, Wd, ang, col, a=1.0):
    c, s_ = math.cos(ang), math.sin(ang); pts = []
    for i in range(24):
        u = i / 23 * math.pi; px = math.cos(u) * L; py = math.sin(u) * Wd
        pts.append((px, py))
    pts += [(-px, -py) for px, py in pts[1:-1]]
    d.poly([(x + px * c - py * s_, y + px * s_ + py * c) for px, py in pts], A(col, a))
    d.line([(x - L * 0.7 * c, y - L * 0.7 * s_), (x + L * 0.7 * c, y + L * 0.7 * s_)], A(SCALE_D, a), 3)

def scope(d, cx, cy, r, a=1.0):
    d.circ(cx, cy, r + 30, fill=A((210, 214, 224), a)); d.circ(cx, cy, r + 12, fill=A((120, 126, 140), a))
    d.circ(cx, cy, r, fill=A((248, 236, 214), a))

# ---------------- scenes ----------------
def s_hook(t, d):
    frz = t >= HOOK_STOP; tt = min(t, HOOK_STOP)
    night(d, tt)
    bx = lerp(-160, 290, ease(pr(tt, -0.3, 0.6))) - 120 * ease(pr(tt, 1.2, 3.0))
    by = 980 + 40 * math.sin(tt * 3)
    hit = HOOK_HIT
    bat(d, bx, by, 0.9, tt, "dizzy" if tt > hit + 0.2 else "hunt", 1, 1, mouth_open=0.6 if tt < hit else 0.2)
    if tt < hit: sonar(d, bx + 90, by - 20, tt, -0.3, 1, CRT, 1, 4, 900)
    mx = 650 + 20 * math.sin(tt * 2)
    moth(d, mx, 950, 0.75, tt, "smug" if tt > hit else "scared", 1, flip=-1, tip=pulse(tt, [hit], 2.5))
    if tt >= hit: zig(d, mx + 185, 950, tt, hit, 0.7, 3, US, 1.1, 800); zig(d, mx + 185, 950, tt, hit + 0.8, 0.5, 3, US, 1.1, 800)
    if tt >= hit: sparks(d, mx + 185, 950, t, hit, 40, 1000, US, 1, 4, 1.0)
    # bat's radar inset
    ra = popk(tt, hit + 0.15)
    if ra > 0: radar(d, 330, 720, 120 * ra, tt, stat=1.0, a=ra)
    kk = back(pr(t, -0.2, HOOK_HIT + 0.1)); k2 = pulse(t, [hit], 6)
    if kk > 0: d.text(540, 330, "雷达花屏", int(150 * (0.6 + 0.4 * kk) * (1 + 0.08 * k2)), A(US, 1), k=1)
    tag(d, 540, 480, "飞蛾的超声干扰", WHITE, popk(t, qb(1.6)), 36)
    if frz: glow(d, 540, 900, 160, WHITE, pr(t, HOOK_STOP, HOOKCUT))
def s_chase(t, d):
    night(d, t)
    u = t - T["chase"]
    bx = lerp(-200, 420, ease(pr(t, T["chase"], at("chase", 3)))); by = 900 + 50 * math.sin(u * 3)
    bat(d, bx, by, 0.8, t, "hunt", 1, 1, mouth_open=0.5 + 0.5 * math.sin(u * 8))
    moth(d, 720, 1050 + 30 * math.sin(u * 4), 0.45, t, "happy", 1, flip=-1)
    title(d, t, T["chase"], "回声定位", 300, 120, CRT)
    tag(d, 540, 460, "蝙蝠的夜视仪", WHITE, popk(t, at("chase", 1.5)), 34)
    for b in range(1, 6): sonar(d, bx + 80, by - 20, t, at("chase", b), 1, CRT, 0.8, 2, 800, 0.8)
def s_ping(t, d):
    grad(d, (20, 40, 60), (8, 14, 28))
    bx, by, mx, my = 340, 900, 750, 900
    bat(d, bx, by, 0.6, t, "hunt", 1, 1, mouth_open=pulse(t, [at("ping", 0.3), at("ping", 4)], 4))
    moth(d, mx, my, 0.45, t, "happy", 1, flip=-1)
    for t0 in (at("ping", 0.3), at("ping", 4)):
        u = t - t0
        if 0 <= u < 0.7: sonar(d, bx + 60, by, t, t0, 1, CRT, 1, 3, 800, 0.7, 25)
        if 0.6 <= u < 1.4: sonar(d, mx - 60, my, t, t0 + 0.6, -1, YEL, 1, 3, 700, 0.8, 25)
    tag(d, 360, 700, "叫", CRT, popk(t, at("ping", 0.3)), 44)
    tag(d, 740, 700, "回声", YEL, popk(t, at("ping", 1.6)), 44)
    title(d, t, T["ping"], "叫一声 · 听回声", 300, 96)
    k = popk(t, at("ping", 4.5))
    if k > 0: d.line([(bx + 80, by + 140), (mx - 60, my + 140)], A(WHITE, 0.6 * k), 4); tag(d, 540, by + 140, "距离 · 方向", WHITE, k, 30)
def s_lock(t, d):
    grad(d, (10, 30, 20), (4, 12, 8))
    lk = ease(pr(t, at("lock", 0.5), at("lock", 2)))
    radar(d, 540, 860, 360, t, 0, (0.35, -0.3), lk)
    title(d, t, T["lock"], "锁定！", 300, 140, RED)
    if lk > 0.95: tag(d, 540, 1300 - 60, "目标：蛾子", RED, 1, 34, WHITE)
def s_q(t, d):
    grad(d, (60, 20, 40), (20, 8, 20))
    moth(d, 540, 900, 1.1, t, "scared", 1, flip=-1, flap=0.4)
    for i in range(3): d.circ(540, 900, 600 + i * 120 + 40 * math.sin(t * 6), outline=A(RED, 0.15), w=20)
    title(d, t, T["q"], "怎么反击？", 300, 130)
    rings(d, 540, 900, t, [at("q", 0.5), at("q", 1.5)], RED, 0.5, 600)
def s_reveal(t, d):
    rays(d, t, (40, 160, 200), (16, 60, 110))
    hit = BIG2
    moth(d, 600, 920, 1.0, t, "smug", 1, flip=-1, tip=0.5 + 0.5 * pulse(t, [hit], 1.5))
    for j in range(4): zig(d, 600 + 245, 920, t, hit + j * 0.45, 1, 3, US, 1.4, 750)
    stamp(d, t, hit, "反干扰！", 540, 330, 150, US)
    tag(d, 540, 480, "超声波 · 人耳听不到", WHITE, popk(t, at("reveal", 1.5)), 34)
    if t >= hit: sparks(d, 845, 920, t, hit, 60, 1300, US, 1, 3, 1.2); sparks(d, 845, 920, t, hit + 0.05, 40, 1000, WHITE, 1, 5, 1.0)
def s_jam(t, d):
    night(d, t, 0.6)
    radar(d, 540, 700, 250, t, stat=0.9 + 0.1 * math.sin(t * 9))
    u = pr(t, at("jam", 1.5), at("jam", 3.5))
    bat(d, lerp(250, 1250, ease(u)), 1180 - 120 * math.sin(u * math.pi), 0.55, t, "dizzy", 1, 1)
    mk = 1 - pr(t, at("jam", 2.5), at("jam", 2.6)) * 0 
    moth(d, 680, 1250 - 200 * ease(pr(t, at("jam", 1.8), at("jam", 2.6))), 0.4, t, "happy", 1, flip=-1, tip=0.6)
    zig(d, 760, 1150, t, T["jam"], 0.5, 6, US, 1.5, 500)
    title(d, t, T["jam"], "扑空！", 300 - 20, 120, YEL)
    if t > at("jam", 2.6): tag(d, 760, 960, "嗖", WHITE, popk(t, at("jam", 2.6)), 40)
def s_organ(t, d):
    grad(d, (250, 236, 210), (220, 196, 160))
    title(d, t, T["organ"], "发声器在哪？", 300, 100, (90, 50, 40))
    moth(d, 600, 860, 0.95, t, "happy", 1, flip=1, flap=0.0, tip=pulse(t, [at("organ", 1.5), at("organ", 2.5), at("organ", 3.5)], 3) * 0.6 + 0.3)
    k = popk(t, at("organ", 1))
    if k > 0:
        arrow(d, 300, 1100, 365, 900, RED, k, 14)
        tag(d, 300, 1150, "抱握器", RED, k, 42, WHITE)
    tag(d, 540, 460, "交配时用来抱住雌蛾", (90, 50, 40), popk(t, at("organ", 3)), 30, WHITE)
def s_scale(t, d):
    grad(d, (40, 60, 90), (20, 30, 50))
    title(d, t, T["scale"], "放大看", 300, 110)
    k = ease(pr(t, T["scale"], at("scale", 1.2)))
    scope(d, 540, 830, 290 * (0.4 + 0.6 * k), k)
    if k > 0.8:
        for i in range(15):
            r_, c_ = divmod(i, 5); x = 350 + c_ * 95 + (r_ % 2) * 40 - 20; y = 710 + r_ * 115
            pk = popk(t, at("scale", 1.2) + i * 0.08)
            if pk > 0: lens(d, x, y, 40 * pk, 19 * pk, -0.5, SCALEC if i != 7 else YEL)
    tag(d, 540, 1190, "橄榄球形鳞片", YEL, popk(t, at("scale", 3)), 36)
    if k > 0.5: d.text(540, 470, "抱握器表面", 34, A(WHITE, 0.8 * k), k=1)
def s_way(t, d):
    grad(d, (255, 190, 90), (230, 110, 60))
    title(d, t, T["way"], "三种刮法", 300, 120, WHITE)
    labs = [("①", "刮鳞片", (90, 120, 230)), ("②", "刮硬刺", (230, 70, 90)), ("③", "刮凸起", (60, 170, 110))]
    for i, (n, s, col) in enumerate(labs):
        k = popk(t, at("way", 1 + i * 1.0))
        if k <= 0: continue
        x = 310 + i * 230; y = 860
        d.rect(x - 100, y - 190 * k, x + 100, y + 190 * k, fill=A(col, 1), r=26)
        d.text(x, y - 60, n, int(90 * k), A(WHITE, 1), k=1); d.text(x, y + 70, s, int(40 * k), A(WHITE, 1), k=1)
        lens(d, x, y + 10, 34 * k, 14 * k, -0.4, SCALEC)
def rub(d, t, y, kind, t0):
    u = t - t0; dx = 140 * math.sin(u * 9)
    if kind == "scale":
        for i in range(7): lens(d, 240 + i * 100, y + 70, 44, 20, 0.5, SCALE_D)
    elif kind == "spine":
        d.rect(170, y + 70, 910, y + 110, fill=A(MO_D, 1), r=10)
        for i in range(14): d.poly([(190 + i * 52, y + 75), (214 + i * 52, y + 10), (238 + i * 52, y + 75)], A((240, 220, 200), 1))
    else:
        d.rect(170, y + 50, 910, y + 120, fill=A(MO_L, 1), r=30)
        for i in range(36): d.circ(195 + (i % 18) * 41, y + 70 + (i // 18) * 30, 9, fill=A((255, 240, 220), 1))
    for i in range(4): lens(d, 390 + i * 100 + dx, y - 20, 44, 20, -0.5, SCALEC)
    if math.sin(u * 9) > 0.7: sparks(d, 540 + dx, y + 30, t, t - ((t * 9) % 0.3), 10, 400, US, 0.8, int(t * 10), 0.3)
def s_w1(t, d):
    grad(d, (70, 90, 200), (30, 40, 110))
    title(d, t, T["w1"], "① 鳞片刮鳞片", 300, 96)
    rub(d, t, 700, "scale", T["w1"])
    wavebox(d, 190, 920, 700, 190, t, "burst", popk(t, at("w1", 2)), YEL, ease(pr(t, at("w1", 2), at("w1", 4))))
    tag(d, 540, 1175, "一阵一阵", YEL, popk(t, at("w1", 3)), 34)
def s_w1b(t, d):
    grad(d, (120, 90, 220), (50, 30, 110))
    title(d, t, T["w1b"], "两种可能", 300, 110)
    k1 = popk(t, at("w1b", 0.3)); k2 = popk(t, at("w1b", 3.5))
    if k1 > 0:
        bat(d, 330, 860, 0.62 * k1, t, "shock", 1, 1, flap=0.3)
        tag(d, 330, 1150, "吓一跳", YEL, k1, 34)
    if k2 > 0:
        moth(d, 740, 880, 0.5 * k2, t, "smug", 1, flip=-1)
        d.rect(600, 640, 880, 720, fill=A(GOOD, k2), r=16); d.text(740, 680, "我很难吃", 38, A(WHITE, k2), k=1)
        tag(d, 740, 1150, "冒充难吃", GOOD, k2, 34, WHITE)
def s_w2(t, d):
    grad(d, (230, 80, 100), (120, 30, 60))
    title(d, t, T["w2"], "② 刮硬刺", 300, 110)
    rub(d, t, 700, "spine", T["w2"])
    wavebox(d, 190, 920, 700, 190, t, "cont", popk(t, at("w2", 1.5)), US, ease(pr(t, at("w2", 1.5), at("w2", 3.5))))
    tag(d, 540, 1175, "连续不断", US, popk(t, at("w2", 3)), 34)
def s_w3(t, d):
    grad(d, (60, 170, 120), (20, 80, 60))
    title(d, t, T["w3"], "③ 刮微小凸起", 300, 96)
    rub(d, t, 700, "bump", T["w3"])
    wavebox(d, 190, 920, 700, 190, t, "cont", popk(t, at("w3", 1.5)), US, ease(pr(t, at("w3", 1.5), at("w3", 3.5))))
    stamp(d, t, at("w3", 4), "首次发现", 540, 480, 70, YEL)
def s_jam2(t, d):
    grad(d, (20, 30, 60), (8, 10, 24))
    title(d, t, T["jam2"], "谁更会干扰？", 300, 100)
    wavebox(d, 190, 470, 700, 160, t, "burst", 1, YEL); tag(d, 540, 670, "① 一阵一阵", YEL, 1, 30)
    wavebox(d, 190, 730, 700, 160, t, "cont", popk(t, at("jam2", 1.5)), US); tag(d, 540, 930, "②③ 连续", US, popk(t, at("jam2", 1.5)), 30)
    k = popk(t, at("jam2", 3.5))
    if k > 0: radar(d, 540, 1100, 110 * k, t, 1.0, a=k); tag(d, 760, 1040, "胜！", GOOD, k, 40, WHITE)
def s_count(t, d):
    grad(d, (40, 30, 70), (16, 12, 30))
    n = 143; lit = int(77 * ease(pr(t, at("count", 2.5), at("count", 4.5))))
    for i in range(n):
        x = 220 + (i % 13) * 53; y = 560 + (i // 13) * 62
        k = popk(t, T["count"] + i * 0.008)
        if k <= 0: continue
        on = i in LIT and LIT.index(i) < lit
        col = PINK if on else (110, 100, 120)
        d.ell(x, y, 20 * k, 7 * k, A(col, 1)); d.poly([(x - 2, y), (x - 14, y - 18 * k), (x - 20, y - 8 * k)], A(col, 0.8)); d.poly([(x - 2, y), (x - 14, y + 18 * k), (x - 20, y + 8 * k)], A(col, 0.8))
        if on: d.arc(x + 22, y, 10, 10, -50, 50, A(US, 0.8), 3)
    d.text(540, 320, f"{lit if t > at('count', 2.5) else 143}", 150, A(PINK if t > at("count", 2.5) else WHITE, 1), k=1)
    tag(d, 540, 460, "143 种里 77 种会发声" if t > at("count", 2.5) else "测了 143 种天蛾", WHITE, popk(t, T["count"]), 32)
LIT = sorted(random.Random(3).sample(range(143), 77), key=lambda i: random.Random(i).random())
def s_evo(t, d):
    grad(d, (30, 70, 60), (10, 30, 30))
    title(d, t, T["evo"], "各自发明了 4–7 次", 300, 84, YEL)
    d.line([(540, 1300), (540, 1100)], A((200, 170, 120), 1), 14)
    tips = []
    def br(x, y, ang, L, depth):
        if depth == 0: tips.append((x, y)); return
        x2, y2 = x + math.cos(ang) * L, y + math.sin(ang) * L
        d.line([(x, y), (x2, y2)], A((200, 170, 120), 1), 3 + depth * 2)
        br(x2, y2, ang - 0.42, L * 0.72, depth - 1); br(x2, y2, ang + 0.42, L * 0.72, depth - 1)
    br(540, 1100, -math.pi / 2, 170, 5)
    picks = [3, 9, 14, 20, 24, 27, 30]
    for j, ti in enumerate(picks):
        x, y = tips[ti]
        k = popk(t, at("evo", 0.6 + j * 0.45))
        if k <= 0: continue
        col = YEL if j < 4 else (255, 255, 255)
        star(d, x, y, 30 * k, col, 1 if j < 4 else 0.55, 5, t)
    tag(d, 540, 470, "约500万–3000万年前", WHITE, popk(t, at("evo", 3.5)), 32)
    tag(d, 540, 1360 - 30, "趋同演化", YEL, popk(t, at("evo", 4.5)), 34)
def s_lose(t, d):
    k = ease(pr(t, T["lose"], at("lose", 1.5)))
    grad(d, mix(NIGHT1, (130, 200, 250), k), mix(NIGHT2, (240, 220, 170), k))
    d.circ(820, lerp(1400, 420, k), 110, fill=A((255, 220, 80), 1)); glow(d, 820, lerp(1400, 420, k), 260, (255, 230, 120), 0.4)
    title(d, t, T["lose"], "白天不用了", 300, 110, (40, 40, 70))
    mx, my = 520, 860
    moth(d, mx, my, 0.75, t, "happy", 1, flip=-1)
    u = pr(t, at("lose", 3), at("lose", 5))
    bx, by = mx + 60 + 40 * u, my + 120 + 500 * u * u
    d.rect(bx - 70, by - 45, bx + 70, by + 45, fill=A(US, 1 - 0.5 * u), r=12); d.text(bx, by, "发声器", 30, A(NAVYT, 1 - 0.5 * u), k=1)
    if u > 0: tag(d, 540, 1150, "装备丢了", RED, popk(t, at("lose", 4)), 36, WHITE)
def s_card(t, d):
    grad(d, (30, 50, 100), (12, 20, 50))
    for i in range(12): d.circ(540, 900, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1)
    if k <= 0: return
    w, h = 560 * (0.7 + 0.3 * k), 820 * (0.7 + 0.3 * k); cx, cy = 540, 880
    d.rect(cx - w / 2 + 14, cy - h / 2 + 18, cx + w / 2 + 14, cy + h / 2 + 18, fill=A((0, 0, 0), 0.3 * k), r=36)
    d.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=A((250, 244, 230), k), r=36)
    d.rect(cx - w / 2 + 24, cy - h / 2 + 24, cx + w / 2 - 24, cy + h / 2 - 24, outline=A((40, 90, 200), k), w=6, r=24)
    d.text(cx - w / 2 + 70, cy - h / 2 + 80, "K", 70, A((40, 90, 200), k), k=1); d.text(cx + w / 2 - 70, cy + h / 2 - 80, "K", 70, A((40, 90, 200), k), k=1)
    moth(d, cx + 10, cy - 130, 0.5 * k, t, "smug", k, flip=-1, tip=0.6)
    tag(d, cx, cy + 70, "一句话学会", GOLD, k, 30)
    d.text(cx, cy + 160, "抱握器鳞片 = 干扰器", 46, A((40, 90, 200), k), k=1)
    ek = popk(t, at("card", 1.5))
    if ek > 0: d.text(cx, cy + 240, "刮一刮，蝙蝠声呐就乱", 34, A(NAVYT, ek), k=1)
def s_end(t, d):
    night(d, t)
    bat(d, 300, 1000, 0.6, t, "dizzy", 1, 1)
    moth(d, 780, 900, 0.5, t, "smug", 1, flip=-1, tip=0.5)
    zig(d, 900, 900, t, T["end"] + ((t - T["end"]) // 1.2) * 1.2, 0.6, 3, US, 1.2, 600)
    stamp(d, t, T["end"] + 0.05, "晚饭搅黄了！", 540, 320, 100, YEL)
    ra = popk(t, at("end", 2))
    d.rect(170, 430, 910, 550, fill=A((20, 12, 30), 0.6 * ra), r=20)
    d.text(540, 468, "Proc. R. Soc. B (2026) · Masonick 等", 28, A(WHITE, 0.95 * ra))
    d.text(540, 510, "天蛾超声防御的多次独立演化", 26, A(WHITE, 0.85 * ra), k=1)
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
    s = "Vibe 知识大赏 · 空中电子战"; w = d.tlen(s, 28, 1) + 50
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
        for ts in sys.argv[2:]: frame(float(ts)).save(f"/tmp/mo_test_{float(ts):05.2f}.png")
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
