import sys, subprocess
from fx import *
from cues import *

SPB = (190, 104, 66); SPB_D = (132, 66, 42); SPB_L = (236, 160, 116); SPH = (255, 214, 170)
TAR = (110, 70, 52); TAR_D = (74, 44, 34); TAR_L = (232, 140, 70)
ROCK = (198, 128, 152); ROCK_D = (142, 84, 110); ROCK_L = (236, 180, 198); ROCK_N = (92, 62, 96)
SEAC = (40, 150, 214); SEA_D = (18, 88, 160); SEA_L = (110, 200, 240); FOAM = (236, 250, 255)
DOORC = (196, 168, 116); DOOR_D = (150, 122, 80); ALGA = (96, 170, 84); SILK = (250, 250, 255); SAND = (226, 196, 140)
SKIN = (240, 190, 140); SKIN_D = (212, 156, 108); CAP = (255, 140, 60)
NAVYT = (24, 20, 40); GOOD = (90, 220, 120); BAD = (250, 70, 70); GOLD = (255, 200, 60); COINC = (240, 196, 80)

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
def title(d, t, t0, s, y=320, size=110, col=WHITE):
    d.text(540, y, s, size, A(col, ease(pr(t, t0, t0 + 0.2))), k=1)
def hdr(d, t, t0, s, col):
    tag(d, 540, 250, s, col, popk(t, t0), 34, WHITE)
def bubbles(d, t, a=0.5, n=24, col=WHITE, spd=0.2, y0=300, y1=1500):
    for i in range(n):
        u = (t * spd + i * 0.137) % 1; x = 190 + (i * 211) % 700 + 14 * math.sin(t * 3 + i); y = lerp(y1, y0, u)
        d.circ(x, y, 5 + i % 4 * 3, outline=A(col, a * math.sin(u * math.pi)), w=3)
def stars_(d, t, a=1.0, n=40):
    for i in range(n):
        x = (i * 263) % 1080; y = 60 + (i * 157) % 900; tw = 0.5 + 0.5 * math.sin(t * 2 + i)
        d.circ(x, y, 2 + i % 3, fill=A(WHITE, a * (0.3 + 0.6 * tw)))
def arrow(d, x0, y0, x1, y1, col, a=1.0, w=16):
    L = math.hypot(x1 - x0, y1 - y0) + 1e-6; ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    bx, by = x1 - ux * w * 2.4, y1 - uy * w * 2.4
    d.line([(x0, y0), (bx, by)], A(col, a), w)
    d.poly([(bx + nx * w * 1.6, by + ny * w * 1.6), (x1, y1), (bx - nx * w * 1.6, by - ny * w * 1.6)], A(col, a))

# ---------------- characters / props ----------------
def legpts(hx, hy, sd, i, s, t, k=1.0, wig=0.0):
    ang = [-0.55, -0.15, 0.2, 0.55][i]
    w = wig * math.sin(t * 9 + i * 1.7 + sd)
    kx = hx + sd * (0.62 * s) * k; ky = hy + (ang * 0.9 - 0.42) * s * k + w * 0.05 * s
    fx_ = kx + sd * 0.32 * s * k; fy_ = ky + (0.78 + ang * 0.25) * s * k + w * 0.06 * s
    return [(hx, hy), (kx, ky), (fx_, fy_)]
def leg(d, pts, s, col, colL, a, hair=True):
    d.line(pts, A(col, a), 0.13 * s)
    d.line([(lerp(pts[0][0], pts[1][0], 0.2), lerp(pts[0][1], pts[1][1], 0.2) - 0.02 * s), (pts[1][0], pts[1][1] - 0.02 * s)], A(colL, 0.7 * a), 0.04 * s)
    d.circ(*pts[1], 0.075 * s, fill=A(colL, a))
    if hair:
        for j in range(3):
            u = 0.25 + j * 0.25; x = lerp(pts[1][0], pts[2][0], u); y = lerp(pts[1][1], pts[2][1], u)
            d.line([(x - 0.06 * s, y), (x + 0.06 * s, y - 0.03 * s)], A(colL, 0.8 * a), 0.025 * s)
    d.circ(*pts[2], 0.06 * s, fill=A(colL, a))

def spider(d, x, y, s, t, mood="chill", a=1.0, look=0.0, sq=0.0, legs=1.0, wig=0.4, col=SPB, dk=SPB_D, lt=SPB_L, fangs=True, glowc=None):
    if a <= 0.01 or s < 2: return
    if glowc: glow(d, x, y, 1.8 * s, glowc, 0.5 * a)
    rx, ry = 0.62 * s * (1 + sq), 0.55 * s * (1 - sq)
    # abdomen behind
    d.ell(x, y - 0.55 * s, 0.55 * s * (1 + sq), 0.45 * s, A(dk, a)); d.ell(x - 0.04 * s, y - 0.6 * s, 0.5 * s, 0.4 * s, A(col, a))
    d.ell(x - 0.18 * s, y - 0.78 * s, 0.16 * s, 0.08 * s, A(lt, 0.6 * a))
    if legs > 0:
        for sd in (-1, 1):
            for i in range(4): leg(d, legpts(x + sd * 0.35 * s, y + (i - 1.5) * 0.12 * s, sd, i, s, t, legs, wig), s, dk, lt, a)
    d.ell(x + 0.03 * s, y + 0.04 * s, rx, ry, A(dk, a)); d.ell(x, y, rx * 0.97, ry * 0.97, A(col, a))
    d.ell(x - 0.25 * s, y - 0.25 * s, 0.17 * s, 0.09 * s, A(WHITE, 0.35 * a))
    for k in range(6):   # small eye cluster on top
        ex = x + (k - 2.5) * 0.08 * s; d.circ(ex, y - 0.42 * s * (1 - sq) + abs(k - 2.5) * 0.02 * s, 0.03 * s, fill=A(INK, a))
    if fangs:
        for sd in (-1, 1):
            d.ell(x + sd * 0.14 * s, y + 0.5 * s * (1 - sq), 0.1 * s, 0.13 * s, A(dk, a))
            d.poly([(x + sd * 0.1 * s, y + 0.58 * s), (x + sd * 0.18 * s, y + 0.58 * s), (x + sd * 0.12 * s, y + 0.72 * s)], A(SPH, a))
    face(d, x, y + 0.02 * s, s * 0.62, mood, a, look)
    d.circ(x - 0.38 * s, y + 0.14 * s, 0.07 * s, fill=A((255, 120, 120), 0.35 * a)); d.circ(x + 0.38 * s, y + 0.14 * s, 0.07 * s, fill=A((255, 120, 120), 0.35 * a))

def tarantula(d, x, y, s, t, mood="chill", a=1.0, look=0.0):
    spider(d, x, y, s, t, mood, a, look, col=TAR, dk=TAR_D, lt=TAR_L, wig=0.2)
    for i in range(16):   # fuzz
        ang = i * 0.39; d.line([(x + math.cos(ang) * 0.6 * s, y + math.sin(ang) * 0.53 * s), (x + math.cos(ang) * 0.68 * s, y + math.sin(ang) * 0.6 * s)], A(TAR_L, 0.6 * a), 0.03 * s)

def legs_out(d, hx, hy, s, t, k, a=1.0, n=2, wig=1.0, reach=1.0):
    """legs poking up out of a hole at (hx,hy)"""
    if k <= 0: return
    for j in range(n):
        sd = -1 if j % 2 == 0 else 1; o = (j // 2) * 0.12
        w = wig * math.sin(t * 7 + j * 1.9)
        p0 = (hx + sd * (0.12 + o) * s, hy)
        p1 = (hx + sd * (0.35 + o) * s * k, hy - (0.75 + o) * s * k + w * 0.04 * s)
        p2 = (hx + sd * (0.75 + o) * s * k * reach, hy - (0.25) * s * k + w * 0.07 * s)
        leg(d, [p0, p1, p2], s, SPB_D, SPB_L, a)

def door3d(d, x, y, r, th, a=1.0, camo=0.0, rim=True, hole=True, ry=0.5):
    """trapdoor on a surface; hinge at the back edge; th = open angle (rad)"""
    if hole:
        d.ell(x, y + 0.04 * r, r * 1.08, r * ry * 1.08, A(mix(ROCK_D, (0, 0, 0), 0.25), a))
        d.ell(x, y + 0.06 * r, r * 0.92, r * ry * 0.88, A((34, 22, 30), a))
    col = mix(DOORC, ROCK, camo); dkc = mix(DOOR_D, ROCK_D, camo)
    c, sn = math.cos(th), math.sin(th)
    def Pp(u, v):   # u,v in door plane (v from -1 back edge to 1 front)
        vv = -1 + (v + 1) * c; z = (v + 1) * sn
        return x + u * r, y + vv * r * ry - z * r * 0.9
    pts = [Pp(math.cos(f), math.sin(f)) for f in [i * math.pi / 18 for i in range(36)]]
    under = th > math.pi / 2
    d.poly([(px, py + 6) for px, py in pts], A(dkc, a))
    d.poly(pts, A(mix(col, (240, 230, 210), 0.3) if under else col, a))
    if not under:
        r2 = random.Random(4)
        for i in range(26):
            f = r2.uniform(0, 2 * math.pi); rr = math.sqrt(r2.uniform(0, 0.85))
            px, py = Pp(rr * math.cos(f), rr * math.sin(f))
            d.circ(px, py, r * 0.035, fill=A(mix(DOOR_D, ROCK_D, camo), a * 0.9))
        for i in range(5):
            f = r2.uniform(0, 2 * math.pi); rr = r2.uniform(0.3, 0.8)
            px, py = Pp(rr * math.cos(f), rr * math.sin(f))
            d.ell(px, py, r * 0.1, r * 0.05, A(mix(ALGA, ROCK_L, camo * 0.6), a))
        if rim and camo < 0.9:
            d.arc(*Pp(0, 0), r * 0.95, r * ry * c * 0.95 + 1, 200, 330, A(SILK, 0.5 * a * (1 - camo)), r * 0.04)
    else:
        for i in range(6):
            px, py = Pp(-0.6 + i * 0.24, 0.0); d.line([Pp(-0.6 + i * 0.24, -0.6), Pp(-0.6 + i * 0.24, 0.6)], A(SILK, 0.7 * a), r * 0.03)

def rock_surface(d, y0, t, col=ROCK, dk=ROCK_D, lt=ROCK_L, seed=2):
    d.rect(-50, y0, OW + 50, OH + 50, fill=A(col, 1))
    r2 = random.Random(seed)
    for i in range(40):
        rx = r2.uniform(-40, 1120); ry = r2.uniform(y0 + 30, 1950); rr = r2.uniform(14, 60)
        d.ell(rx, ry, rr, rr * 0.5, A(dk, 0.55)); d.ell(rx - rr * 0.2, ry - rr * 0.15, rr * 0.6, rr * 0.25, A(lt, 0.35))
    d.ell(540, y0, 760, 60, A(col, 1)); d.ell(540, y0 - 6, 700, 40, A(lt, 0.25))

def sea_back(d, t, top, bot, y_surf, amp=26, col=SEAC):
    grad(d, top, bot)
    pts = [(-50, y_surf)]
    for i in range(0, 1141, 30): pts.append((i - 30, y_surf + amp * math.sin(i / 90 + t * 3) + amp * 0.4 * math.sin(i / 37 - t * 5)))
    pts += [(1130, 1980), (-50, 1980)]
    d.poly(pts, A(col, 1))
    d.line(pts[1:-2], A(FOAM, 0.75), 8)

def wave_crash(d, t, t0, k_rise, a=1.0):
    """towering wave curling from the left; k_rise 0..1 raise, then crash at t0"""
    u = pr(t, t0, t0 + 0.5)
    if u >= 1: return
    h = lerp(500, 1250, ease(k_rise)) * (1 - ease(u) * 0.3)
    base = 1250; top = base - h
    cx = lerp(380, 640, ease(u))
    pts = [(-60, base), (-60, top + 120)]
    for i in range(16):
        f = i / 15; ang = math.pi * 1.1 * f
        pts.append((cx - 300 + f * 520 + math.sin(ang) * 120, top + 60 - math.sin(ang) * 140 + f * f * 340 * (1 + 2 * u)))
    pts.append((1140, base))
    d.poly(pts, A(SEA_D, a)); d.poly([(px + 10, py + 30) for px, py in pts], A(SEAC, a * 0.9))
    for i in range(18):
        f = i / 17; ang = math.pi * 1.1 * f
        fx_ = cx - 300 + f * 520 + math.sin(ang) * 120; fy_ = top + 60 - math.sin(ang) * 140 + f * f * 340 * (1 + 2 * u)
        d.circ(fx_, fy_, 22 + 18 * math.sin(i * 1.3 + t * 6) ** 2, fill=A(FOAM, a))

def sci(d, x, y, s, t, mood="chill", a=1.0, look=0.0, sq=0.0, lamp=True):
    if a <= 0.01: return
    d.ell(x, y + 1.0 * s, 0.8 * s, 0.12 * s, A((0, 0, 0), 0.25 * a))
    d.ell(x, y + 1.15 * s, 0.85 * s * (1 + sq), 0.6 * s, A((60, 110, 170), a))   # jacket
    d.ell(x + 0.04 * s, y + 0.04 * s, s * (1 + sq), s * (1 - sq), A(SKIN_D, a)); d.ell(x, y, s * 0.97 * (1 + sq), s * 0.97 * (1 - sq), A(SKIN, a))
    d.ell(x - 0.35 * s, y - 0.4 * s, 0.18 * s, 0.1 * s, A(WHITE, 0.35 * a))
    d.d.chord((P(x - 0.95 * s), P(y - 1.0 * s * (1 - sq)), P(x + 0.95 * s), P(y + 0.1 * s)), 180, 360, fill=A((92, 60, 40), a))   # hair
    if lamp:
        d.line([(x - 0.95 * s, y - 0.42 * s), (x + 0.95 * s, y - 0.42 * s)], A((40, 40, 50), a), 0.12 * s)
        d.rect(x - 0.2 * s, y - 0.58 * s, x + 0.2 * s, y - 0.28 * s, fill=A((70, 74, 90), a), r=0.06 * s)
        d.circ(x, y - 0.43 * s, 0.11 * s, fill=A((255, 248, 200), a)); glow(d, x, y - 0.43 * s, 0.4 * s, (255, 240, 170), 0.6 * a)
    face(d, x, y + 0.12 * s, s * 0.8, mood, a, look)

def isopod(d, x, y, s, t, a=1.0, fl=1):
    d.ell(x, y, 0.9 * s, 0.45 * s, A((120, 126, 140), a))
    for i in range(6): d.line([(x - 0.6 * s + i * 0.24 * s, y - 0.4 * s), (x - 0.6 * s + i * 0.24 * s, y + 0.4 * s)], A((90, 96, 110), a), 0.05 * s)
    d.ell(x - 0.2 * s, y - 0.2 * s, 0.3 * s, 0.1 * s, A(WHITE, 0.3 * a))
    hx = x + fl * 0.85 * s
    for sd in (-1, 1): d.line([(hx, y), (hx + fl * 0.5 * s, y + sd * 0.35 * s + 0.05 * s * math.sin(t * 12))], A((90, 96, 110), a), 0.04 * s)
    d.circ(hx - fl * 0.05 * s, y - 0.12 * s, 0.07 * s, fill=A(INK, a))
    for i in range(5): d.line([(x - 0.5 * s + i * 0.25 * s, y + 0.4 * s), (x - 0.55 * s + i * 0.25 * s + 0.06 * s * math.sin(t * 20 + i), y + 0.55 * s)], A((90, 96, 110), a), 0.04 * s)
def cricket(d, x, y, s, t, a=1.0, fl=1):
    d.ell(x, y, 0.8 * s, 0.3 * s, A((120, 96, 50), a)); d.ell(x - fl * 0.1 * s, y - 0.12 * s, 0.6 * s, 0.14 * s, A((150, 124, 70), a))
    d.line([(x - fl * 0.3 * s, y), (x - fl * 0.6 * s, y - 0.5 * s), (x - fl * 0.9 * s, y + 0.3 * s)], A((100, 80, 40), a), 0.08 * s)
    hx = x + fl * 0.8 * s; d.circ(hx, y - 0.05 * s, 0.22 * s, fill=A((110, 86, 44), a)); d.circ(hx + fl * 0.06 * s, y - 0.1 * s, 0.06 * s, fill=A(INK, a))
    d.line([(hx, y - 0.2 * s), (hx + fl * 0.9 * s, y - 0.8 * s + 0.1 * s * math.sin(t * 9))], A((100, 80, 40), a), 0.03 * s)
def moth(d, x, y, s, t, a=1.0):
    f = 0.6 + 0.4 * abs(math.sin(t * 18))
    for sd in (-1, 1):
        d.poly([(x, y - 0.1 * s), (x + sd * 0.95 * s * f, y - 0.5 * s), (x + sd * 0.8 * s * f, y + 0.35 * s), (x, y + 0.2 * s)], A((214, 196, 156), a))
        d.circ(x + sd * 0.5 * s * f, y - 0.1 * s, 0.12 * s, fill=A((160, 130, 90), a))
    d.ell(x, y, 0.12 * s, 0.45 * s, A((150, 120, 84), a)); d.circ(x, y - 0.4 * s, 0.1 * s, fill=A(INK, a))

def coin(d, x, y, r, a=1.0):
    d.circ(x + 4, y + 6, r, fill=A((170, 130, 40), a)); d.circ(x, y, r, fill=A(COINC, a)); d.circ(x, y, r * 0.8, outline=A((214, 166, 56), a), w=r * 0.06)
    d.text(x, y, "1", int(r * 0.9), A((200, 150, 50), a), k=1); d.ell(x - r * 0.4, y - r * 0.45, r * 0.25, r * 0.12, A(WHITE, 0.5 * a))

def court(d, x, y, w, h, a=1.0):
    d.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=A((236, 150, 70), a), r=6)
    d.rect(x - w / 2 + 6, y - h / 2 + 6, x + w / 2 - 6, y + h / 2 - 6, outline=A(WHITE, a), w=4)
    d.line([(x, y - h / 2 + 6), (x, y + h / 2 - 6)], A(WHITE, a), 4); d.circ(x, y, h * 0.16, outline=A(WHITE, a), w=4)
    for sd in (-1, 1): d.arc(x + sd * (w / 2 - 6), y, w * 0.18, h * 0.32, 90 if sd > 0 else 270, 270 if sd > 0 else 450, A(WHITE, a), 4)

def drop(d, x, y, r, a=1.0, col=SEA_L):
    d.circ(x, y, r, fill=A(col, a)); d.poly([(x - r * 0.9, y - r * 0.3), (x, y - r * 2.2), (x + r * 0.9, y - r * 0.3)], A(col, a))
    d.circ(x - r * 0.35, y - r * 0.2, r * 0.25, fill=A(WHITE, 0.7 * a))

def splash(d, x, y, t, t0, n=14, col=FOAM, a=1.0, spd=500, seed=1, life=0.6):
    u = t - t0
    if u < 0 or u > life: return
    r2 = random.Random(seed)
    for i in range(n):
        ang = r2.uniform(math.pi * 1.05, math.pi * 1.95); v = r2.uniform(0.4, 1) * spd
        d.circ(x + math.cos(ang) * v * u, y + math.sin(ang) * v * u + 1400 * u * u, 8 * (1 - u / life) + 2, fill=A(col, a * (1 - u / life)))

def knowcard(d, t, t0, head, main, sub, cy=1060, mcol=(30, 90, 160)):
    k = popk(t, t0)
    if k <= 0: return
    al = min(1, k * 1.5); w = 660 * (0.7 + 0.3 * k); cy += 40 * (1 - k)
    d.rect(540 - w / 2, cy - 120, 540 + w / 2, cy + 120, fill=A(WHITE, 0.97 * al), r=34)
    d.rect(540 - w / 2, cy - 120, 540 - w / 2 + 16, cy + 120, fill=A(GOLD, al), r=8)
    tag(d, 540, cy - 120, head, GOLD, al, 34)
    d.text(540, cy - 18, main, int(70 * k) + 1, A(mcol, al), k=1)
    d.text(540, cy + 62, sub, int(36 * k) + 1, A(NAVYT, al), k=1)

# ---------------- scenes ----------------
def s_hook(t, d):
    hit = t >= HOOK_HIT
    if not hit:
        grad(d, (40, 70, 110), (14, 30, 60))
        wave_crash(d, t, HOOK_HIT, 0.75 + 0.25 * pr(t, -0.2, HOOK_HIT))
        rock_surface(d, 1180, t)
        door3d(d, 600, 1210, 150, 1.25, ry=0.42)
        legs_out(d, 600, 1225, 170, t, 1.0, n=4, wig=1.5)
        spider(d, 600, 1130, 110, t, "scream", look=-0.8, legs=0, sq=0.05 * math.sin(t * 40))
        d.rect(200, 250, 880, 410, fill=A((10, 30, 70), 0.8), r=40)
        d.text(540, 330, "大浪来了！", 120, A(YEL, 1), k=1)
        return
    u = t - HOOK_HIT
    zk = eio(pr(t, HOOK_HIT + 0.3, NIGHT))
    grad(d, (30, 120, 190), (10, 50, 110))
    for i in range(6):   # light rays under water
        x0 = 150 + i * 170 + 40 * math.sin(t * 0.7 + i)
        d.poly([(x0, 200), (x0 + 60, 200), (x0 + 220, 1300), (x0 + 120, 1300)], A(SEA_L, 0.08))
    s = 1 + 0.45 * zk; cy = lerp(880, 820, zk)
    def Z(px, py): return 540 + (px - 540) * s, cy + (py - 1180) * s
    rx, ry = Z(0, 1180)
    d.rect(-50, ry, OW + 50, OH + 50, fill=A(ROCK, 1))
    r2 = random.Random(2)
    for i in range(30):
        px, py = Z(r2.uniform(-200, 1280), r2.uniform(1220, 2300)); rr = r2.uniform(14, 60) * s
        d.ell(px, py, rr, rr * 0.5, A(ROCK_D, 0.55))
    d.ell(540, ry, 760 * s, 60 * s, A(ROCK, 1))
    sl = math.exp(-u * 18) * 0.12
    tx0, ty0 = Z(470, 1215); tx1, ty1 = Z(610, 1520)
    d.rect(tx0, ty0, tx1, ty1, fill=A((52, 34, 46), 1), r=30 * s)
    spk = pulse(t, [HOOK_HIT], 8)
    for sd in (-1, 1):
        for j in range(2):
            leg(d, [Z(540 + sd * 16, 1300), Z(540 + sd * (56 + j * 14), 1262 - j * 10), Z(540 + sd * (30 + j * 22), 1222)], 66 * s, SPB_D, SPB_L, 1)
    spider(d, *Z(540, 1330 + 8 * spk), 52 * s, t, "scared" if t < QLINE else "sus", look=0.0, legs=0.0, sq=0.06 * spk)
    door3d(d, 540, cy + 30 * s, 150 * s * (1 + sl), 0.0, ry=0.42)
    # slam burst
    if u < 0.5:
        star(d, 540, cy - 40 * s, 230 * popk(t, HOOK_HIT) * (1 - pr(t, HOOK_HIT + 0.3, HOOK_HIT + 0.5)), YEL, 0.9, 10, t)
        d.text(540, cy - 40 * s, "啪！", int(90 * popk(t, HOOK_HIT)) + 1, A(BAD, 1 - pr(t, HOOK_HIT + 0.3, HOOK_HIT + 0.5)), k=1)
    # foam from the crash
    for i in range(30):
        r3 = random.Random(i); fx_ = r3.uniform(0, 1080); fy_ = r3.uniform(300, 1100) - u * r3.uniform(100, 300)
        rr = r3.uniform(10, 40) * math.exp(-u * 1.2)
        if rr > 2: d.circ(fx_, fy_, rr, fill=A(FOAM, 0.75 * math.exp(-u * 1.5)))
    bubbles(d, t, 0.6, 26, WHITE, 0.35, 300, 1250)
    rings(d, 540, cy, t, [HOOK_HIT], WHITE, 0.6, 500)
    if t >= LAMP_IN:   # headlamp beam slides in during the stop
        k = ease(pr(t, LAMP_IN, LAMP_IN + 0.2)); lx = lerp(1400, 640, k)
        d.poly([(lx + 600, 1700), (lx - 200, cy - 20), (lx - 30, cy + 140)], A((255, 244, 190), 0.25))
        d.circ(lx - 110, cy + 50, 190, fill=A((255, 244, 190), 0.18))
    stamp(d, t, HOOK_HIT, "住在海里", 540, 320, 150, YEL)
    stamp(d, t, HOOK_HIT + 0.08, "的蜘蛛！", 540, 480, 130, WHITE)
    if t >= QLINE:
        k = popk(t, QLINE)
        d.rect(540 - 330 * k, 590, 540 + 330 * k, 790, fill=A((10, 30, 70), 0.75 * k), r=30)
        d.text(540, 645, "涨潮全淹，", int(64 * k) + 1, A(WHITE, k), k=1)
        d.text(540, 735, "家里一滴水不进？", int(64 * k) + 1, A(SEA_L, k), k=1)

def s_night(t, d):
    grad(d, (20, 22, 58), (8, 8, 24)); stars_(d, t, 0.8)
    d.ell(820, 260, 60, 60, A((255, 240, 190), 0.9)); d.ell(845, 245, 52, 52, A((20, 22, 58), 1))
    sea_back(d, t, (20, 22, 58), (8, 8, 24), 640, 14, (30, 50, 100))
    rock_surface(d, 860, t, mix(ROCK, (0, 0, 40), 0.55), mix(ROCK_D, (0, 0, 40), 0.55), mix(ROCK_L, (0, 0, 40), 0.5))
    hx, hy = 430, 960
    # crevice
    d.poly([(300, 900), (360, 880), (470, 940), (560, 920), (600, 1000), (480, 1010), (380, 990)], A((20, 12, 24), 1))
    scream = t >= SCREAM
    jump = 30 * math.sin(pr(t, SCREAM, SCREAM + 0.4) * math.pi) if scream else 0
    sx, sy = 760, 1160 - jump
    # beam: sweeps until LEGS, then locks on the hole
    sweep = 0.5 + 0.5 * math.sin((t - NIGHT) * 3.2) if t < LEGS - 0.3 else 1 - ease(pr(t, LEGS - 0.3, LEGS)) * 0 
    tx = lerp(260, 640, sweep) if t < LEGS - 0.3 else lerp(lerp(260, 640, 0.5 + 0.5 * math.sin((LEGS - 0.3 - NIGHT) * 3.2)), hx, ease(pr(t, LEGS - 0.3, LEGS)))
    ty = 960
    lx, ly = sx, sy - 0.43 * 90
    d.poly([(lx - 10, ly), (lx + 10, ly), (tx + 150, ty + 40), (tx - 150, ty - 40)], A((255, 244, 190), 0.16))
    d.ell(tx, ty, 170, 90, A((255, 244, 190), 0.22)); d.ell(tx, ty, 110, 60, A((255, 244, 200), 0.18))
    lk = ease(pr(t, LEGS, LEGS + 0.35))
    if lk > 0:
        legs_out(d, hx, hy - 20, 150, t, lk, n=2, wig=1.2, reach=1.1)
        for sd in (-1, 1): d.circ(hx + sd * 22, hy - 4, 9, fill=A((255, 250, 220), 0.9 * lk))
    sci(d, sx, sy, 90, t, "scream" if scream else ("scared" if t >= LEGS else "sus"), look=-0.8, sq=0.08 * pulse(t, [SCREAM], 6))
    if scream:
        sh = 3 * math.sin(t * 60)
        bubble(d, 880 + sh, 950, "啊——！！", 1, WHITE, BAD, popk(t, SCREAM), 52)
        for k in range(3):
            ang = -2.3 + k * 0.5; d.line([(sx + math.cos(ang) * 130, sy - 80 + math.sin(ang) * 130), (sx + math.cos(ang) * 170, sy - 80 + math.sin(ang) * 170)], A(YEL, popk(t, SCREAM)), 8)
    if t >= QUOTE:
        sci(d, 290, 1180, 70, t, "happy", look=0.8, lamp=True)
        bubble(d, 240, 1040, "我只记得他在尖叫", -1, YEL, NAVYT, popk(t, QUOTE), 36)
    tag(d, 540, 420, "2023 · 毛里求斯 Ilot Vacoas 小岛", WHITE, popk(t, NIGHT + 0.1), 30, NAVYT)
    if t < LEGS: title(d, t, NIGHT, "天黑，翻岩缝", 300, 104)
    else: stamp(d, t, LEGS, "洞里伸出长腿！", 540, 300, 100, YEL)

def s_family(t, d):
    rays(d, t, (255, 176, 70), (240, 120, 50), n=18, cx=540, cy=820)
    out = ease(pr(t, INLAND[0] - 0.15, INLAND[0] + 0.15))
    if out < 1:
        dx = -900 * out
        tk = popk(t, TARAN)
        tarantula(d, 360 + dx, 780 + 6 * math.sin(t * 3), 170 * tk, t, "happy" if t > KIN_TAG else "chill", look=0.6)
        spider(d, 750 + dx, 840 + 6 * math.sin(t * 3 + 1), 110, t, "happy", look=-0.6)
        if tk > 0:
            tag(d, 360 + dx, 1060, "捕鸟蛛", WHITE, tk, 36)
            tag(d, 750 + dx, 1060, "它", WHITE, 1, 36)
        if t > KIN_TAG:
            heart(d, 560 + dx, 640 - 10 * math.sin(t * 4), 40 * popk(t, KIN_TAG), (255, 90, 120))
            tag(d, 540 + dx, 1170, "原蛛下目：捕鸟蛛那一大类", (130, 40, 20), popk(t, KIN_TAG), 32, WHITE)
        title(d, t, FAMILY, "远房亲戚", 300, 110)
    if out > 0:
        dx = 900 * (1 - out)
        items = [(300, 640, "土里", (150, 100, 60), INLAND[0]), (540, 640, "草丛", (90, 160, 70), INLAND[1])]
        for x, y, lab, col, h in items:
            k = popk(t, h)
            if k <= 0: continue
            x += dx
            d.rect(x - 105, y - 110, x + 105, y + 110, fill=A(WHITE, 0.95), r=30)
            if lab == "土里": d.rect(x - 85, y - 10, x + 85, y + 90, fill=A(col, 1), r=12)
            else:
                for j in range(7): d.poly([(x - 85 + j * 26, y + 90), (x - 72 + j * 26, y - 60 + 20 * (j % 2)), (x - 60 + j * 26, y + 90)], A(col, 1))
            spider(d, x, y + 10, 34, t, "chill", legs=0.8, wig=0.2)
            tag(d, x, y + 155, lab, WHITE, k, 30)
            check(d, x + 80, y - 90, 24, ease(pr(t, h, h + 0.2)), GOOD)
        k = popk(t, SEA)
        if k > 0:
            x, y = 780 + dx, 640
            d.rect(x - 105, y - 110, x + 105, y + 110, fill=A(WHITE, 0.95), r=30)
            d.rect(x - 85, y - 90, x + 85, y + 90, fill=A(SEAC, 1), r=12)
            for j in range(3): d.line([(x - 80 + i * 10, y - 40 + j * 50 + 8 * math.sin(i * 0.8 + t * 5)) for i in range(17)], A(FOAM, 0.9), 5)
            spider(d, x, y + 10, 40, t, "proud", legs=0.8)
            tag(d, x, y + 155, "海边！", YEL, k, 30)
            d.text(x + 80, y - 100, "!?", int(60 * k) + 1, A(BAD, k), k=1)
        d.text(540, 970, "绝大多数蜘蛛  →  远离大海", 38, A(WHITE, popk(t, INLAND[0] + 0.1)), k=1)
        if t < SEA: title(d, t, INLAND[0], "别的蜘蛛住哪？", 300, 100)
        else: stamp(d, t, SEA, "它偏住海边", 540, 300, 110, WHITE)

def s_zone(t, d):
    grad(d, (150, 214, 250), (90, 170, 230))
    up = ease(pr(t, TIDE_UP - 0.2, TIDE_UP + 0.25)) * (1 - ease(pr(t, TIDE_DN - 0.1, TIDE_DN + 0.35)))
    lvl = lerp(780, 520, up) + 8 * math.sin(t * 3)
    # shore rock sloping down to the right
    shore = [(-50, 380), (180, 420), (420, 560), (640, 700), (900, 850), (1130, 920), (1130, 960), (-50, 960)]
    hi_y, lo_y = 520, 780
    sea = [(-50, lvl)] + [(x, lvl + 10 * math.sin(x / 60 + t * 4)) for x in range(0, 1131, 30)] + [(1130, 960), (-50, 960)]
    d.poly(shore, A(ROCK, 1))
    d.poly([(x, y + 14) for x, y in shore[:6]] + [(1130, 960), (-50, 960)], A(ROCK_D, 0.4))
    # band highlight
    def shore_x(y):   # x on the slope for a given y
        for (x0, y0), (x1, y1) in zip(shore[:5], shore[1:6]):
            if y0 <= y <= y1: return lerp(x0, x1, (y - y0) / (y1 - y0))
        return 900
    bk = 0.35 + 0.25 * math.sin(t * 5)
    d.poly([(shore_x(hi_y), hi_y), (shore_x(lo_y), lo_y), (shore_x(lo_y) + 40, lo_y + 30), (shore_x(hi_y) + 40, hi_y + 30)], A(YEL, bk))
    door3d(d, shore_x(650) + 20, 680, 34, 0.0 if up > 0.3 else 1.0, ry=0.45)
    d.poly(sea, A(SEAC, 0.82)); d.line(sea[1:-2], A(FOAM, 0.9), 7)
    for y, lab, col in ((hi_y, "涨潮线", (20, 60, 140)), (lo_y, "退潮线", (20, 60, 140))):
        for i in range(0, 1080, 40): d.line([(i, y), (i + 22, y)], A(WHITE, 0.9), 4)
        tag(d, 840 if y == hi_y else 300, y - 40, lab, WHITE, 1, 28, col)
    tag(d, 230, 650, "潮间带", YEL, popk(t, ZONE + 0.1), 34)
    arrow(d, 230, 600, 230, hi_y + 10, YEL, popk(t, ZONE + 0.1), 8); arrow(d, 230, 700, 230, lo_y - 10, YEL, popk(t, ZONE + 0.1), 8)
    if t >= SOUTH:
        k = popk(t, SOUTH)
        tag(d, 760, 420, "最爱：浪最大的南岸", BAD, k, 32, WHITE)
        splash(d, 820, lvl, t, SOUTH, 20, FOAM, 1, 700, 3, 0.8)
    knowcard(d, t, CARD1, "一句话学会", "潮间带", "涨潮被淹、退潮露出的那条海岸")
    if t < TIDE_UP: title(d, t, ZONE, "它的家在哪？", 300, 100, NAVYT)
    elif t < TIDE_DN: stamp(d, t, TIDE_UP, "涨潮：全淹", 540, 300, 104, (20, 60, 140))
    else: stamp(d, t, TIDE_DN, "退潮：露出", 540, 300, 104, (150, 60, 30))

TUBEP = [(560, 430), (585, 560), (560, 700), (600, 840), (640, 980), (610, 1100)]
def tube_path(k):
    n = len(TUBEP) - 1; f = k * n; i = min(int(f), n - 1); u = f - i
    return [TUBEP[j] for j in range(i + 1)] + [(lerp(TUBEP[i][0], TUBEP[i + 1][0], u), lerp(TUBEP[i][1], TUBEP[i + 1][1], u))]
def s_tube(t, d):
    grad(d, (120, 200, 240), (70, 150, 210))
    d.rect(-50, 400, OW + 50, 1240, fill=A(ROCK, 1))
    r2 = random.Random(9)
    for i in range(50):
        rx = r2.uniform(0, 1080); ry = r2.uniform(440, 1220); rr = r2.uniform(10, 40)
        d.ell(rx, ry, rr, rr * 0.6, A(ROCK_D, 0.5)); d.circ(rx - rr * 0.3, ry - rr * 0.2, rr * 0.25, fill=A(ROCK_L, 0.4))
    d.rect(-50, 400, OW + 50, 430, fill=A(ROCK_L, 0.6))
    old = t < NODIG
    wk = ease(pr(t, WORMS, NODIG - 0.1))
    k = wk if old else 1
    pts = tube_path(max(0.01, k))
    d.line(pts, A((50, 30, 44), 1), 64)
    if not old and t >= LINING:
        lk = ease(pr(t, LINING, LINING + 0.4))
        d.line(tube_path(lk), A(SILK, 0.7), 64); d.line(tube_path(lk), A((50, 30, 44), 1), 44)
        for j in range(int(30 * lk)):
            px, py = tube_path(j / 30)[-1]; d.circ(px + 26 * (1 if j % 2 else -1), py, 5, fill=A(SAND, 1))
        tag(d, 830, 900, "内衬：丝 + 沙", WHITE, popk(t, LINING), 30)
    if old:   # ghost sepia: worm drilling thousands of years ago
        d.rect(0, 0, OW, OH, fill=A((120, 90, 50), 0.22))
        hx, hy = pts[-1]
        for j in range(6): d.circ(hx - 6 * j * math.sin(t * 6), hy - 14 * j, 24 - j * 2, fill=A((255, 160, 170), 0.9))
        face(d, hx, hy + 4, 26, "proud", 1)
        for j in range(8):
            ang = t * 10 + j; d.circ(hx + math.cos(ang) * 40, hy + 30 + math.sin(ang) * 16, 5, fill=A(ROCK_L, 0.9))
        # clam
        cx, cy = 300, 760 + 6 * math.sin(t * 5)
        d.d.chord((P(cx - 60), P(cy - 50), P(cx + 60), P(cy + 50)), 180, 360, fill=A((240, 220, 190), 0.95))
        d.d.chord((P(cx - 60), P(cy - 40), P(cx + 60), P(cy + 60)), 0, 180, fill=A((220, 196, 160), 0.95))
        for j in range(4): d.line([(cx, cy), (cx - 45 + j * 30, cy - 40)], A((200, 170, 130), 0.9), 3)
        face(d, cx, cy + 10, 38, "proud", 1)
        tag(d, 540, 1170, "数千年前，蠕虫和贝类在钻洞", (120, 80, 40), popk(t, WORMS), 30, WHITE)
        title(d, t, TUBE, "它的洞……", 300, 110)
        return
    nk = popk(t, NODIG)
    if t < MOVEIN + 0.6:
        x, y = 800, 640
        d.line([(x - 40, y + 70), (x + 30, y - 60)], A((130, 90, 50), nk), 14)
        d.poly([(x - 75, y + 60), (x - 15, y + 120), (x - 5, y + 70), (x - 45, y + 40)], A((170, 176, 190), nk))
        cross(d, x - 10, y + 30, 70, ease(pr(t, NODIG, NODIG + 0.25)), BAD)
    mk = ease(pr(t, MOVEIN - 0.1, MOVEIN + 0.6))
    if mk > 0:
        px, py = tube_path(lerp(0.0, 0.62, mk))[-1]
        spider(d, px, py, 46, t, "happy", look=0.3, legs=0.75, wig=0.8)
    if t >= MOVEIN and t < LINING: bubble(d, 640, 480, "拎包入住～", -1, WHITE, NAVYT, popk(t, MOVEIN), 34)
    rk = ease(pr(t, RULER - 0.2, RULER + 0.25))
    if rk > 0:
        x = 380; y0, y1 = 430, 430 + 670 * rk
        d.rect(x - 24, y0, x + 24, y1, fill=A(YEL, 1), r=6)
        for j in range(13):
            yy = 430 + j * 670 / 12
            if yy <= y1: d.line([(x - 24, yy), (x - (2 if j % 2 else -6), yy)], A(NAVYT, 1), 3)
        tag(d, x - 6, 1150, "约 12 厘米", WHITE, popk(t, RULER), 34, BAD)
    if t < RULER: stamp(d, t, NODIG, "不自己挖洞", 540, 300, 104, WHITE)
    else: stamp(d, t, RULER, "12 厘米长", 540, 300, 110, YEL)

def s_door(t, d):
    hide = t >= HIDE
    if not hide:
        grad(d, (50, 180, 190), (20, 110, 140))
        for i in range(8): d.circ(540, 760, 160 + i * 130, outline=A(WHITE, 0.06), w=24)
    else:
        grad(d, ROCK, ROCK_D); rock_surface(d, 380, t, seed=7)
    srcs = [(-200, 500, "蛛丝"), (1280, 520, "沙子"), (540, -200, "藻类")]
    fk = popk(t, FORM)
    if t < FORM + 0.05:
        for i, (sx_, sy_, lab) in enumerate(srcs):
            u = ease(pr(t, ING[i] - 0.3, ING[i]))
            if u <= 0: continue
            home = [(300, 640), (780, 640), (540, 500)][i]
            x = lerp(sx_, home[0], u); y = lerp(sy_, home[1], u)
            mk = pr(t, FORM - 0.25, FORM); x = lerp(x, 540, ease(mk)); y = lerp(y, 760, ease(mk))
            if i == 0:
                for j in range(5): d.arc(x, y, 40 + j * 10, 30 + j * 6, j * 50, j * 50 + 200, A(SILK, 1), 6)
            elif i == 1:
                for j in range(18): d.circ(x + math.cos(j * 2.4) * (j * 3.5), y + math.sin(j * 2.4) * (j * 2.5), 9, fill=A(SAND, 1))
            else:
                for j in range(3): d.ell(x - 30 + j * 30, y, 18, 46, A(ALGA, 1))
            if mk <= 0: tag(d, x, y + 100, lab, WHITE, 1, 32)
    if t >= FORM and not hide:
        sk = ease(pr(t, COIN - 0.2, COIN + 0.2))
        dx = lerp(540, 360, sk); r = lerp(220, 120, sk) * (0.6 + 0.4 * fk)
        glow(d, dx, 760, r * 1.6, (255, 250, 220), 0.4 * (1 - sk))
        door3d(d, dx, 760, r, 0.0, hole=False, ry=0.95)
        if t < COIN: rings(d, 540, 760, t, [FORM], WHITE, 0.7, 300)
        if sk > 0:
            ck = popk(t, COIN)
            coin(d, 720, 760, 120 * ck, 1)
            d.text(540, 760, "≈", int(90 * ck) + 1, A(WHITE, ck), k=1)
            tag(d, 360, 940, "门", WHITE, ck, 32); tag(d, 720, 940, "硬币", WHITE, ck, 32)
    if hide:
        ck = ease(pr(t, HIDE, HIDE + 0.35))
        door3d(d, 600, 830, 130, 0.0, camo=ck, rim=False, hole=False, ry=0.5)
        if t >= FIND:
            fk2 = popk(t, FIND); lx = 600 + 60 * math.sin((t - FIND) * 5) * (1 - pr(t, FIND, FIND + 0.6)); ly = 830
            d.circ(lx, ly, 170 * fk2, outline=A(YEL, 0.95), w=10)
            d.line([(lx + 120, ly + 120), (lx + 220, ly + 220)], A(YEL, fk2), 22)
    if t < FORM: title(d, t, DOOR, "门用什么做？", 300, 100)
    elif t < COIN: stamp(d, t, FORM, "丝 + 沙 + 藻", 540, 300, 104, YEL)
    elif t < HIDE: stamp(d, t, COIN, "硬币大小", 540, 300, 120, WHITE)
    else: stamp(d, t, FIND, "门在哪？", 540, 300, 120, YEL) if t >= FIND else title(d, t, HIDE, "关上门……", 300, 110, WHITE)

def stopwatch(d, x, y, r, sec, a=1.0):
    d.rect(x - 18, y - r - 40, x + 18, y - r - 6, fill=A((80, 84, 100), a), r=6)
    d.circ(x, y, r + 10, fill=A((80, 84, 100), a)); d.circ(x, y, r, fill=A(WHITE, a))
    ang = -math.pi / 2 + sec / 20 * 2 * math.pi
    d.d.pieslice((P(x - r * 0.9), P(y - r * 0.9), P(x + r * 0.9), P(y + r * 0.9)), -90, -90 + sec / 20 * 360, fill=A(SEA_L, 0.6 * a))
    d.line([(x, y), (x + math.cos(ang) * r * 0.85, y + math.sin(ang) * r * 0.85)], A(BAD, a), 8)
    d.circ(x, y, 10, fill=A(NAVYT, a))
    d.text(x, y + r + 50, f"{int(sec)} 秒", 44, A(WHITE, a), k=1)

def s_test(t, d):
    grad(d, (255, 200, 120), (240, 140, 90))
    rock_surface(d, 960, t)
    door3d(d, 540, 1020, 130, 0.0, ry=0.42)
    pk = pr(t, *POUR)
    on = POUR[0] <= t < POUR[1]
    bx, by = 690, 520
    tilt = ease(pr(t, POUR[0] - 0.2, POUR[0])) * 0.9
    c, sn = math.cos(tilt), math.sin(tilt)
    def T(u, v): return bx + u * c - v * sn, by + u * sn + v * c
    d.poly([T(-90, -100), T(90, -100), T(70, 100), T(-70, 100)], A((90, 140, 220), 1))
    d.poly([T(-90, -100), T(90, -100), T(86, -70), T(-86, -70)], A((130, 180, 250), 1))
    d.text(*T(0, 10), "海水", 40, A(WHITE, 1), k=1)
    d.arc(*T(0, -100), 90, 60, 180, 360, A((60, 70, 90), 1), 8)
    if on:
        sx_, sy_ = T(-90, -100)
        pts = [(sx_ + 6 * math.sin(t * 40 + i), lerp(sy_, 1000, i / 12)) for i in range(13)]
        pts = [(lerp(sx_, 560, (i / 12) ** 0.6) + 8 * math.sin(t * 30 + i), y) for i, (x, y) in enumerate(pts)]
        d.line(pts, A(SEA_L, 0.9), 40); d.line(pts, A(FOAM, 0.6), 12)
        for j in range(4): splash(d, 560, 1010, t, POUR[0] + (int((t - POUR[0]) / 0.25) - j) * 0.25, 10, FOAM, 0.9, 500, j + int(t * 4), 0.5)
        d.ell(540, 1020, 220, 50, A(SEA_L, 0.45))
    if t >= TIMER[0]:
        sec = 20 * ease(pr(t, *TIMER)) if t < TIMER[1] else 20
        stopwatch(d, 300, 640, 110, sec, popk(t, TIMER[0]))
    if t < ASK: title(d, t, TEST, "浇 20 秒海水", 300, 104)
    else:
        stamp(d, t, ASK, "会进水吗？", 540, 300, 120, WHITE)

def s_reveal(t, d):
    rays(d, t, (255, 214, 80), (246, 150, 40), n=18, cx=540, cy=900)
    # cutaway: rock block with a dry tube
    d.rect(170, 820, 910, 1240, fill=A(ROCK, 1), r=30)
    for i in range(14):
        r2 = random.Random(i); d.ell(r2.uniform(200, 880), r2.uniform(850, 1220), r2.uniform(14, 34), r2.uniform(8, 18), A(ROCK_D, 0.5))
    d.rect(420, 830, 660, 1220, fill=A((60, 40, 50), 1), r=50)
    for j in range(12): d.circ(420 + 10 + (j % 2) * 220, 860 + j * 30, 6, fill=A(SAND, 1))
    ok = popk(t, BIG2)
    th = ease(pr(t, BIG2, BIG2 + 0.25)) * 1.9
    glow(d, 540, 1000, 200, WHITE, 0.4 * ok)
    sparks(d, 540, 830, t, BIG2, n=60, spd=1100, col=(255, 250, 220), seed=5, life=0.6)
    door3d(d, 540, 828, 120, th, hole=False, ry=0.35)
    spider(d, 540, 1010 - 30 * ok, 95, t, "proud", legs=0.85)
    # empty cup
    if t >= DRIP - 0.3:
        u = pr(t, DRIP - 0.3, DRIP); cx, cy = 790, 700
        if u < 1: drop(d, cx, lerp(500, cy - 20, u * u), 14)
        d.poly([(cx - 70, cy - 70), (cx + 70, cy - 70), (cx + 52, cy + 80), (cx - 52, cy + 80)], A((230, 245, 255), 0.75))
        d.line([(cx - 70, cy - 70), (cx - 52, cy + 80), (cx + 52, cy + 80), (cx + 70, cy - 70)], A(WHITE, 1), 6)
        d.text(cx, cy + 10, "积水", 30, A(NAVYT, 1), k=1); d.text(cx, cy + 130, "= 0", 44, A(NAVYT, popk(t, DRIP)), k=1)
    stamp(d, t, BIG2, "0 滴水！", 540, 330, 150, WHITE)

def s_why1(t, d):
    grad(d, (96, 176, 236), (40, 100, 184))
    hdr(d, t, WHY1, "原因 1", (30, 70, 150))
    x0, x1 = 230, 850; ys = [700, 770, 840]
    labs = [("蛛丝", SILK), ("沙子", SAND), ("藻类", ALGA)]
    for i, (lab, col) in enumerate(labs):
        k = popk(t, LAYERS[i])
        if k <= 0: continue
        y = ys[i] + 80 * (1 - k)
        d.rect(x0, y - 32, x1, y + 32, fill=A(col, 1), r=14)
        if i == 0:
            for j in range(16): d.line([(x0 + 20 + j * 38, y - 26), (x0 + 40 + j * 38, y + 26)], A((200, 210, 230), 1), 3)
        elif i == 1:
            for j in range(40): d.circ(x0 + 14 + j * 15.5, y + 12 * math.sin(j * 2.1), 6, fill=A(DOOR_D, 1))
        else:
            for j in range(10): d.ell(x0 + 30 + j * 62, y, 22, 14, A((60, 130, 60), 1))
        tag(d, x1 - 50, y, lab, NAVYT, k, 26, WHITE)
    for i, h in enumerate(BOUNCE):
        x = [380, 560, 720][i]
        u = pr(t, h - 0.35, h)
        if 0 < u < 1: drop(d, x, lerp(420, 650, u * u), 24)
        if t >= h:
            b = pr(t, h, h + 0.5)
            if b < 1: drop(d, x + 140 * b * (1 if i % 2 else -1), 650 - 260 * math.sin(b * math.pi), 18, a=1 - b)
            splash(d, x, 660, t, h, 10, FOAM, 1, 400, i + 3, 0.5)
    if t >= BOUNCE[0]: tag(d, 540, 1000, "水被挡在门外", WHITE, popk(t, BOUNCE[0]), 34, (30, 70, 150))
    stamp(d, t, WHY1 + 0.05, "门的材料", 540, 380, 110, WHITE)

def s_why2(t, d):
    grad(d, (70, 180, 120), (24, 100, 70))
    hdr(d, t, WHY2, "原因 2", (20, 90, 60))
    d.rect(-50, 620, OW + 50, 1240, fill=A(ROCK, 1))
    for i in range(16):
        r2 = random.Random(i + 40); d.ell(r2.uniform(0, 1080), r2.uniform(660, 1220), r2.uniform(14, 34), r2.uniform(8, 18), A(ROCK_D, 0.5))
    d.rect(-50, 450, OW + 50, 620, fill=A(SEAC, 0.85))
    for j in range(3): d.line([(x, 470 + j * 50 + 8 * math.sin(x / 50 + t * 5)) for x in range(-40, 1121, 30)], A(FOAM, 0.6), 4)
    d.rect(450, 620, 630, 1220, fill=A((60, 40, 50), 1), r=30)
    pull = sum(1 for h in PULL if t >= h); pk = pulse(t, PULL, 8)
    gap = max(0, 14 - 7 * pull) if t < SEAL else 0
    dy = 620 + gap
    d.rect(420, dy - 34, 660, dy + 6, fill=A(DOORC, 1), r=12)
    for j in range(8): d.circ(440 + j * 30, dy - 16, 5, fill=A(DOOR_D, 1))
    if gap > 0:
        for j in range(3): drop(d, 500 + j * 40, dy + 12 + ((t * 300 + j * 40) % 40), 6, a=0.0)
    # spider below, legs up holding the door
    sy = 860 + 18 * pk
    for sd in (-1, 1):
        for j in range(2): leg(d, [(540 + sd * 22, sy - 30), (540 + sd * (70 + j * 20), sy - 120 - j * 20), (540 + sd * (40 + j * 30), dy + 8)], 120, SPB_D, SPB_L, 1)
    spider(d, 540, sy, 78, t, "sus" if t < SEAL else "proud", legs=0.0)
    if pull:
        for sd in (-1, 1): arrow(d, 540 + sd * 170, 660, 540 + sd * 170, 820, YEL, popk(t, PULL[0]), 14)
    if t >= SEAL:
        sk = popk(t, SEAL)
        rings(d, 540, dy, t, [SEAL], YEL, 0.9, 260)
        tag(d, 780, 700, "压紧！", YEL, sk, 34)
    tag(d, 540, 1160, "浇水时，蜘蛛从里面拉住门", WHITE, popk(t, PULL[0] + 0.1), 30, (20, 90, 60))
    if t < SEAL: stamp(d, t, PULL[0], "往下拉！", 540, 360, 110, WHITE) if t >= PULL[0] else title(d, t, WHY2, "从里面拉紧", 360, 104)
    else: stamp(d, t, SEAL, "缝更紧", 540, 360, 120, YEL)

def s_hunt(t, d):
    grad(d, (50, 30, 90), (16, 10, 40)); stars_(d, t, 0.6, 30)
    rock_surface(d, 900, t, mix(ROCK, (20, 0, 60), 0.5), mix(ROCK_D, (20, 0, 60), 0.5), mix(ROCK_L, (20, 0, 60), 0.5))
    hx, hy = 540, 960
    ok = ease(pr(t, OPEN - 0.2, OPEN + 0.2))
    door3d(d, hx, hy, 110, ok * 1.6, ry=0.42)
    snap = pulse(t, PREY, 7)
    if ok > 0:
        spider(d, hx, hy - 20 * ok, 50, t, "sus", look=math.sin(t * 2), legs=0)
        legs_out(d, hx, hy + 10, 120 * (1 + 0.25 * snap), t, ok, n=4, wig=0.6, reach=1.2)
    for i, h in enumerate(PREY):
        u = pr(t, h - 1.0, h)
        if t >= h + 0.05: continue
        if i == 0: isopod(d, lerp(120, hx - 140, ease(u)), 1010, 70, t)
        elif i == 1: cricket(d, lerp(980, hx + 150, ease(u)), 990, 70, t, fl=-1)
        else: moth(d, lerp(820, hx + 30, ease(u)), lerp(450, 860, ease(u)) + 20 * math.sin(t * 8), 80, t)
    for i, h in enumerate(PREY):
        if t >= h:
            k = popk(t, h)
            star(d, hx + [-90, 100, 20][i], [960, 950, 860][i], 70 * k * (1 - pr(t, h + 0.2, h + 0.4)), YEL, 1, 9)
    names = ["等足类", "蟋蟀", "飞蛾"]
    for i, h in enumerate(PREY):
        k = popk(t, h)
        if k > 0: tag(d, 300 + i * 240, 1110, names[i], WHITE, k, 32)
    if t >= PREY[0]: d.text(540, 1180, "等足类 = 海蟑螂的亲戚", 30, A(WHITE, popk(t, PREY[0] + 0.1)), k=1)
    if t < OPEN: title(d, t, HUNT, "天黑了……", 300, 110)
    elif t < PREY[0]: stamp(d, t, OPEN, "开门伏击", 540, 300, 120, YEL)
    else: stamp(d, t, PREY[0], "抓到了！", 540, 300, 120, WHITE)

def island(d, x, y, r, a=1.0, seed=0):
    r2 = random.Random(seed); pts = []
    for i in range(24):
        ang = i * math.pi / 12; rr = r * (0.85 + 0.25 * r2.random())
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr * 0.75))
    d.poly([(px, py + 10) for px, py in pts], A((60, 120, 140), 0.5 * a))
    d.poly([(x + (px - x) * 1.12, y + (py - y) * 1.12) for px, py in pts], A((150, 220, 230), 0.6 * a))
    d.poly(pts, A((236, 210, 150), a)); d.poly([(x + (px - x) * 0.7, y + (py - y) * 0.7 - 6) for px, py in pts], A((120, 180, 90), a))

def s_tiny(t, d):
    grad(d, (40, 140, 200), (16, 80, 150))
    for i in range(14): d.line([(x, 360 + i * 70 + 6 * math.sin(x / 70 + t * 2 + i)) for x in range(160, 921, 40)], A(WHITE, 0.07), 3)
    tag(d, 540, 420, "毛里求斯东南外海", WHITE, popk(t, TINY + 0.1), 28, (16, 80, 150))
    data = [(370, 640, 70, "Ilot Vacoas", "约 227 平方米", ISL[0]), (680, 760, 122, "Ile aux Fouquets", "约 686 平方米", ISL[1])]
    for j, (x, y, r, nm, ar, h) in enumerate(data):
        k = popk(t, h)
        if k <= 0: continue
        island(d, x, y, r * k, 1, j + 3)
        spider(d, x, y - 10, 22 * k, t, "happy", legs=0.8, wig=0.2)
        rings(d, x, y, t, [h], WHITE, 0.6, 200)
        d.text(x, y + r * 0.75 + 44, nm, 30, A(WHITE, k), k=1)
        tag(d, x, y + r * 0.75 + 92, ar, YEL, k, 28)
    if t >= SUM:
        ck = [popk(t, h) for h in COURTS]
        for i in range(2):
            if ck[i] > 0: court(d, 380 + i * 320, 1080, 280 * ck[i], 150 * ck[i])
        if t >= COURTS[0]: d.text(540, 1080, "+", 60, A(WHITE, ck[0]), k=1)
    if t < SUM: title(d, t, TINY, "全世界只有这里", 300, 96)
    else: stamp(d, t, SUM, "≈ 913 平方米", 540, 300, 104, YEL)
    if t >= COURTS[1]: tag(d, 540, 1200, "≈ 两个篮球场", WHITE, popk(t, COURTS[1]), 34, (180, 80, 20))

def s_name(t, d):
    pc = t >= PCT
    grad(d, (255, 150, 110), (220, 80, 100)) if not pc else grad(d, (120, 90, 200), (60, 40, 130))
    if not pc:
        # sea wall with the spider's door, waves smash into it
        d.rect(170, 760, 910, 1220, fill=A(ROCK, 1), r=24)
        for j in range(4):
            for i in range(4):
                bx = 190 + i * 180 + (90 if j % 2 else 0); by = 780 + j * 108
                if bx < 880: d.rect(bx, by, min(bx + 170, 890), by + 98, fill=A(ROCK_L if (i + j) % 2 else ROCK_D, 0.5), r=14)
        door3d(d, 540, 990, 60, 0.0, ry=0.9, hole=False)
        spider(d, 700, 720, 40, t, "proud" if t >= MEAN else "chill", legs=0.8, wig=0.3)
        u = pr(t, WALL - 0.35, WALL + 0.6)
        if 0 < u < 1:
            wx = lerp(-200, 200, ease(min(1, u * 2)))
            d.ell(wx, 1000, 260, 220 * (1 - u), A(SEAC, 0.9))
            splash(d, 200, 900, t, WALL, 26, FOAM, 1, 900, 9, 0.9)
        k = pr(t, NAME + 0.1, NAME + 0.6); s = "Idioctis marevallum"; n = int(len(s) * k + 0.999)
        d.text(540, 560, s[:n], 60, A(WHITE, 1), k=1)
        mk = popk(t, MEAN)
        if mk > 0:
            tag(d, 540, 660, "marevallum = 海墙（拉丁语）", WHITE, mk, 34, (200, 60, 80))
        if t < MEAN: title(d, t, NAME, "它的名字", 300, 110)
        else: stamp(d, t, MEAN, "海墙", 540, 300, 150, YEL)
    else:
        x0 = 330; base = 1130
        d.line([(220, base), (860, base)], A(WHITE, 0.8), 5)
        k1 = ease(pr(t, PCT, PCT + 0.4)); k2 = ease(pr(t, PCT_HIT - 0.4, PCT_HIT))
        h1 = 420 * k1; h2 = 420 * 1.27 * k2
        d.rect(x0 - 90, base - h1, x0 + 90, base, fill=A((190, 180, 230), 1), r=12)
        d.rect(750 - 90, base - h2, 750 + 90, base, fill=A(YEL, 1), r=12)
        if k2 > 0: d.rect(750 - 90, base - h2, 750 + 90, base - h2 + 420 * 0.27 * k2, fill=A(BAD, 1), r=12)
        d.text(x0, base + 50, "论文前", 34, A(WHITE, 1), k=1); d.text(750, base + 50, "论文后", 34, A(WHITE, 1), k=1)
        tag(d, 540, 420, "毛里求斯已知蜘蛛种类", WHITE, 1, 30, (60, 40, 130))
        if t >= PCT_HIT:
            for j in range(10):
                sparks(d, 750, base - h2, t, PCT_HIT, n=30, spd=800, col=YEL, seed=8, life=0.8)
        if t < PCT_HIT: title(d, t, PCT, "一篇论文", 300, 110)
        else: stamp(d, t, PCT_HIT, "+27%", 540, 300, 160, YEL)

def s_card(t, d):
    grad(d, (255, 214, 90), (240, 150, 50))
    for i in range(10): d.circ(540, 600, 160 + i * 140, outline=A(WHITE, 0.08), w=26)
    rock_surface(d, 720, t)
    door3d(d, 540, 760, 90, 1.5 + 0.1 * math.sin(t * 3), ry=0.42)
    spider(d, 540, 700, 60, t, "happy", legs=0.0)
    legs_out(d, 540, 770, 90, t, 1, n=2, wig=0.8)
    k = popk(t, CARD)
    if k <= 0: return
    al = min(1, k * 1.5); cy = 1000 + 40 * (1 - k); w = 680 * (0.7 + 0.3 * k)
    d.rect(540 - w / 2, cy - 170, 540 + w / 2, cy + 190, fill=A(WHITE, 0.97 * al), r=34)
    d.rect(540 - w / 2, cy - 170, 540 - w / 2 + 16, cy + 190, fill=A(GOLD, al), r=8)
    tag(d, 540, cy - 170, "三秒复习", GOLD, al, 34)
    d.text(540, cy - 70, "好门 + 拉紧", int(70 * k) + 1, A((20, 90, 150), al), k=1)
    d.text(540, cy + 10, "= 淹在海里也不进水的家", int(38 * k) + 1, A(NAVYT, al), k=1)
    chips = [("丝+沙+藻", (60, 130, 220)), ("从里面拉", (40, 150, 100)), ("住老岩管", (190, 90, 60))]
    for i, (s, col) in enumerate(chips):
        ck = popk(t, CHIPS[i])
        if ck > 0: tag(d, 540 + (i - 1) * 215, cy + 110, s, col, ck, 30, WHITE)

def s_end(t, d):
    grad(d, (60, 70, 140), (20, 24, 60)); stars_(d, t, 0.5, 30)
    sea_back(d, t, (60, 70, 140), (20, 24, 60), 640, 18, (40, 90, 160))
    rock_surface(d, 860, t, mix(ROCK, (20, 20, 80), 0.35), mix(ROCK_D, (20, 20, 80), 0.35), mix(ROCK_L, (20, 20, 80), 0.3))
    th = 1.5 * (1 - ease(pr(t, SHUT - 0.4, SHUT)))
    if th > 0.05: spider(d, 540, 900 + 50 * (1 - th / 1.5), 50, t, "happy", legs=0)
    door3d(d, 540, 940, 110, th, ry=0.42)
    if t >= SHUT:
        star(d, 540, 900, 80 * popk(t, SHUT) * (1 - pr(t, SHUT + 0.2, SHUT + 0.4)), YEL, 0.9, 9)
        u = ease(pr(t, SHUT + 0.3, SHUT + 2.0))
        if u > 0:   # high tide rolls in over the door
            lvl = lerp(1000, 790, u)
            pts = [(-50, lvl)] + [(x, lvl + 14 * math.sin(x / 70 + t * 3)) for x in range(0, 1131, 30)] + [(1130, 1980), (-50, 1980)]
            d.poly(pts, A((50, 110, 190), 0.55)); d.line(pts[1:-2], A(FOAM, 0.8), 6)
            bubbles(d, t, 0.4 * u, 14, WHITE, 0.25, lvl + 40, 1240)
    if t >= SHUT - 0.1:   # cutaway: snug and dry inside
        ck = ease(pr(t, SHUT - 0.1, SHUT + 0.4))
        d.rect(480, 975, 600, 975 + 110 * ck + 1, fill=A((52, 34, 46), 1), r=26)
        for j in range(int(5 * ck)): d.circ(486 + (j % 2) * 108, 990 + j * 20, 4, fill=A(SAND, 1))
        if ck > 0.5: spider(d, 540, 1045 + 3 * math.sin(t * 2), 40, t, "happy", legs=0, fangs=False)
    bubble(d, 880, 690, "涨潮了，晚安～", 1, WHITE, NAVYT, popk(t, OUTRO + 0.3), 38)
    stamp(d, t, OUTRO + 0.05, "海墙里的家", 540, 320, 110, WHITE)
    tag(d, 540, 450, "2026 年 4 月 正式发表为新种", YEL, popk(t, OUTRO + 0.2), 30)
    ra = popk(t, FINAL)
    d.text(540, 1110, "Sherwood, Cole … Tercel (2026)", 26, A(WHITE, 0.9 * ra))
    d.text(540, 1146, "Arachnology 20(4): 608–622", 26, A(WHITE, 0.9 * ra))
    d.text(540, 1182, "DOI 10.13156/arac.2026.20.4.18", 26, A(WHITE, 0.9 * ra))
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

def heart(d, x, y, s, col, a=1.0):
    d.circ(x - s * 0.5, y - s * 0.2, s * 0.55, fill=A(col, a)); d.circ(x + s * 0.5, y - s * 0.2, s * 0.55, fill=A(col, a))
    d.poly([(x - s * 1.03, y - s * 0.05), (x, y + s * 1.05), (x + s * 1.03, y - s * 0.05), (x, y - s * 0.3)], A(col, a))
def star(d, x, y, r, col, a=1.0, n=9, rot=0):
    if r <= 1: return
    pts = []
    for i in range(n * 2):
        ang = rot + i * math.pi / n; rr = r if i % 2 == 0 else r * 0.55
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    d.poly(pts, A(col, a))

def subs(t, d):
    if SIL0 <= t < BIG2: return
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70
            w = max(d.tlen(x, 52, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 44, 540 + w / 2, y0 + (n - 1) * 70 + 44, fill=A((15, 12, 26), 0.82 * al), r=22)
            for i, x in enumerate(ls): d.text(540, y0 + i * 70, x, 52, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇新发现"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)

SECS = [(-1, NIGHT, s_hook), (NIGHT, FAMILY, s_night), (FAMILY, ZONE, s_family), (ZONE, TUBE, s_zone), (TUBE, DOOR, s_tube), (DOOR, TEST, s_door),
        (TEST, BIG2, s_test), (BIG2, WHY1, s_reveal), (WHY1, WHY2, s_why1), (WHY2, HUNT, s_why2), (HUNT, TINY, s_hunt), (TINY, NAME, s_tiny),
        (NAME, CARD, s_name), (CARD, OUTRO, s_card), (OUTRO, 99, s_end)]
def cam(t):
    z = 1.0 + 0.015 * pulse(t, HITS, 7) + 0.04 * pulse(t, [HOOK_HIT, BIG2], 3)
    for a, b in RISERS:
        if a <= t < b: z += 0.08 * eio(pr(t, a, b))
    if HOOK_STOP <= t < NIGHT: z += 0.05 * pr(t, HOOK_STOP, NIGHT)
    amp = 8 * pulse(t, [HOOK_HIT, BIG2], 5) + 1.5 * pulse(t, HITS, 8)
    sx, sy = shake(t, amp, 40)
    return z, 540 + sx, 900 + sy
def frame(t):
    img = Image.new("RGB", (W, H), (30, 20, 50)); d = D(img)
    if SIL0 + 0.06 <= t < BIG2:
        img = Image.new("RGB", (W, H), (0, 0, 0)); d = D(img)
        d.text(540, 900, "……", 80, A(WHITE, 0.5), k=1)
    else:
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
        for ts in sys.argv[2:]: frame(float(ts)).save(f"/tmp/td_test_{float(ts):05.2f}.png")
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
