# Characters + environment for 《鳄鱼妈妈贴地偷听》 — "Where's My Water?"-style cutaway: sunny surface above, diggable dirt below.
import math, random
from fx import *
import easing as E

CROC = (96, 156, 72); CROC_D = (62, 110, 52); CROC_L = (156, 202, 112); BELLYC = (220, 218, 156)
BABY = (132, 196, 92); BABY_D = (92, 150, 66); BABY_B = (236, 214, 110)
DIRT = (156, 100, 52); DIRT_D = (122, 76, 38); DIRT_L = (190, 136, 82); HOLE = (84, 50, 28); RIM = (206, 156, 100)
STONE = (128, 116, 140); STONE_L = (168, 158, 182); STONE_D = (96, 86, 110)
SKY1 = (110, 196, 240); SKY2 = (246, 232, 186); SAND = (222, 196, 132); SAND_D = (190, 160, 100); GRASS = (110, 176, 70); GRASS_D = (70, 130, 52)
SHELL = (250, 244, 226); SHELL_D = (214, 204, 180); PINKB = (255, 150, 160); GOLD = (255, 200, 60); NAVYT = (22, 22, 40)
WAT1 = (70, 170, 230); WAT2 = (30, 100, 170); FOAM = (220, 244, 255)
rr = random.Random(7)
DSPK = [(rr.uniform(0, 1080), rr.uniform(0, 1), rr.uniform(4, 14), rr.random()) for _ in range(260)]
DSTN = [(rr.uniform(60, 1020), rr.uniform(0.15, 1), rr.uniform(26, 60), rr.uniform(0, 6.28)) for _ in range(14)]
ROOTS = [(rr.uniform(80, 1000), rr.uniform(60, 180), rr.uniform(-0.5, 0.5)) for _ in range(9)]
TUFT = [(rr.uniform(-20, 1100), rr.uniform(0.7, 1.3)) for _ in range(70)]

def rot(pts, ang, ox, oy):
    c, s = math.cos(ang), math.sin(ang)
    return [(ox + u * c - v * s, oy + u * s + v * c) for u, v in pts]

# ---------------- environment ----------------
def sky(d, t, gy):
    grad(d, SKY1, SKY2, 0, gy + 10, 24)
    d.circ(860, 300, 70, fill=A((255, 236, 150), 1)); glow(d, 860, 300, 200, (255, 240, 170), 0.6, 6)
    for i, (cx, cy, s) in enumerate(((180, 330, 1.0), (720, 230, 0.8), (450, 420, 0.6))):
        x = (cx + t * 12 * (i + 1)) % 1300 - 110
        for ox, oy, r in ((0, 0, 40), (40, -14, 50), (88, 0, 38), (44, 12, 40)): d.circ(x + ox * s, cy + oy * s, r * s, fill=A(WHITE, 0.85))
def papyrus(d, x, gy, h, t, s=1.0):
    sw = 8 * math.sin(t * 1.4 + x)
    d.line([(x, gy), (x + sw, gy - h)], A(GRASS_D, 1), 6 * s)
    for j in range(9):
        a = -math.pi / 2 + (j - 4) * 0.28
        d.line([(x + sw, gy - h), (x + sw + math.cos(a) * 60 * s, gy - h + math.sin(a) * 60 * s + 10 * s)], A(GRASS, 1), 4 * s)
def surface(d, t, gy, mound=True, pap=True, mx=540):
    sky(d, t, gy)
    if pap:
        for x, h in ((70, 260), (130, 200), (990, 240), (1040, 300), (930, 180)): papyrus(d, x, gy, h, t)
    if mound: d.ell(mx, gy + 6, 330, 46, A(SAND, 1)); d.ell(mx - 60, gy - 14, 180, 18, A(mix(SAND, WHITE, 0.3), 0.7))
def dirt(d, t, gy, a=1.0, y1=2000):
    d.rect(-60, gy, 1140, y1, fill=A(DIRT, a))
    for i in range(5): d.rect(-60, gy + 160 + i * 240, 1140, gy + 160 + i * 240 + 120, fill=A(DIRT_D, 0.18 * a))
    for x, u, r, c in DSPK:
        y = gy + 30 + u * (y1 - gy)
        d.circ(x, y, r, fill=A(DIRT_D if c < 0.6 else DIRT_L, (0.55 if c < 0.6 else 0.5) * a))
    for x, u, r, ang in DSTN:
        y = gy + 120 + u * 1100
        pts = [(x + math.cos(ang + k * 1.05) * r * (1 + 0.25 * math.sin(k * 3)), y + math.sin(ang + k * 1.05) * r * 0.7) for k in range(6)]
        d.poly(pts, A(STONE, a)); d.circ(x - r * 0.25, y - r * 0.2, r * 0.3, fill=A(STONE_L, 0.7 * a))
    for x, L, b in ROOTS:
        d.line([(x, gy), (x + b * L, gy + L * 0.6), (x + b * L * 0.6, gy + L)], A(DIRT_D, 0.8 * a), 5)
    for x, s in TUFT:   # grass fringe
        d.poly([(x - 10 * s, gy + 4), (x, gy - 26 * s), (x + 10 * s, gy + 4)], A(GRASS, a))
    d.rect(-60, gy - 2, 1140, gy + 10, fill=A(GRASS_D, a))
def chamber(d, x, y, rx, ry, a=1.0):
    if rx < 2: return
    pts = [(x + math.cos(k / 24 * 6.283) * rx * (1 + 0.05 * math.sin(k * 2.1)), y + math.sin(k / 24 * 6.283) * ry * (1 + 0.06 * math.cos(k * 1.7))) for k in range(24)]
    big = [(x + (px - x) * 1.09, y + (py - y) * 1.14) for px, py in pts]
    d.poly(big, A(RIM, a)); d.poly(pts, A(HOLE, a))
    d.ell(x, y + ry * 0.62, rx * 0.86, ry * 0.32, A(mix(HOLE, SAND, 0.35), a))
def tunnel(d, pts, w, a=1.0):
    if len(pts) < 2: return
    d.line(pts, A(RIM, a), w * 1.3)
    for p in (pts[0], pts[-1]): d.circ(p[0], p[1], w * 0.65, fill=A(RIM, a))
    d.line(pts, A(HOLE, a), w)
    for p in (pts[0], pts[-1]): d.circ(p[0], p[1], w * 0.5, fill=A(HOLE, a))

# ---------------- mom croc (side view, facing right; x,y = ground point under chest) ----------------
def croc(d, x, y, s, t, mood="normal", tilt=0.0, a=1.0, iso=0.0, ear=0.0, jaw=0.0, blush=0.0, breath=True, look=0.0, bob=True, tail=True):
    if bob and breath: y += E.bob(t, 2, 0.4)
    L = lambda u, v: (x + u * s, y + v * s)
    d.ell(*L(-120, 6), 420 * s, 20 * s, A((0, 0, 0), 0.18 * a))
    if tail:
        w = math.sin(t * 2.2) * 10
        top = [(-180, -88), (-280, -70), (-380, -48), (-470, -28 + w * 0.4), (-560, -10 + w)]
        bot = [(-560, 2 + w), (-450, 4), (-300, 4), (-180, 4)]
        d.poly([L(u, v) for u, v in top + bot], A(CROC, a))
        for i in range(8):
            u0 = -200 - i * 44; v0 = lerp(-86, -14, i / 8) + (w * (i / 8) ** 2 if i > 5 else 0)
            d.poly([L(u0 - 14, v0 + 4), L(u0 - 3, v0 - 16 + i * 1.2), L(u0 + 8, v0 + 4)], A(CROC_D, a))
    for lx in (-170, 70):   # legs
        d.poly([L(lx - 36, -30), L(lx + 22, -30), L(lx + 30, 6), L(lx + 48, 14), L(lx - 40, 14)], A(CROC_D, a))
        for c in range(3): d.poly([L(lx + 20 + c * 11, 8), L(lx + 34 + c * 11, 14), L(lx + 20 + c * 11, 16)], A(SHELL, a))
    d.ell(*L(-60, -58), 210 * s, 64 * s, A(CROC, a))
    d.ell(*L(-60, -26), 190 * s, 30 * s, A(BELLYC, 0.8 * a))
    for i in range(9): d.circ(*L(-230 + i * 38, -114 + abs(i - 4) * 2.2), 13 * s, fill=A(CROC_D, a))
    for u, v, r in ((-150, -70, 14), (-80, -84, 10), (0, -70, 12), (-210, -60, 9)): d.circ(*L(u, v), r * s, fill=A(CROC_D, 0.6 * a))
    # head
    ang = math.radians(9 * tilt); px, py = L(115, -62 + 28 * tilt)
    H = lambda pts: [(px + (u * math.cos(ang) - v * math.sin(ang)) * s, py + (u * math.sin(ang) + v * math.cos(ang)) * s) for u, v in pts]
    def H1(u, v): return H([(u, v)])[0]
    oj = 22 * jaw
    lower = [(-26, 4), (60, 6 + oj * 0.4), (180, 6 + oj * 0.8), (300, 6 + oj), (312, 18 + oj), (270, 30 + oj), (60, 34 + oj * 0.3), (-30, 24)]
    d.poly(H(lower), A(CROC_D, a))
    if jaw > 0.05: d.poly(H([(0, 2), (300, 2), (300, 6 + oj), (0, 8)]), A((150, 40, 50), a))
    for i in range(10):   # teeth
        u = 60 + i * 24
        d.poly(H([(u - 6, 0), (u, 13), (u + 6, 0)]), A(SHELL, a))
        if i % 2 == 0: d.poly(H([(u + 6, 6 + oj * u / 300), (u + 12, -6 + oj * u / 300), (u + 18, 6 + oj * u / 300)]), A(SHELL, a))
    upper = [(-34, -62), (40, -70), (130, -54), (230, -42), (300, -38), (326, -22), (316, -2), (0, -2), (-34, 14)]
    d.poly(H(upper), A(CROC, a))
    d.poly(H([(-20, -40), (120, -40), (300, -26), (310, -10), (0, -8)]), A(mix(CROC, CROC_L, 0.35), 0.6 * a))
    d.circ(*H1(298, -40), 13 * s, fill=A(CROC, a)); d.circ(*H1(302, -42), 4 * s, fill=A(INK, 0.8 * a))
    # sensory bumps (ISOs)
    for i in range(16):
        for j, vv in enumerate((-30, -16, 20)):
            u = 70 + i * 15 + (j % 2) * 7
            if u > 300: continue
            vy = vv + (oj * u / 300 if vv > 0 else 0)
            q = H1(u, vy)
            if iso > 0: glow(d, q[0], q[1], 12 * s, (255, 236, 120), iso * 0.9, 3)
            d.circ(q[0], q[1], 3.4 * s, fill=A(mix(CROC_D, (255, 240, 140), iso), a))
    # eye bump + eye
    ex, ey = H1(58, -70); d.circ(ex, ey, 36 * s, fill=A(CROC, a))
    er = 24 * s; ex2, ey2 = H1(62, -74)
    if mood in ("soft", "listen"):
        if mood == "soft": d.arc(ex2, ey2 + er * 0.35, er * 0.8, er * 0.7, 200, 340, A(INK, a), 6 * s)
        else: d.arc(ex2, ey2 - er * 0.2, er * 0.8, er * 0.6, 20, 160, A(INK, a), 6 * s)
    else:
        big = 1.2 if mood == "shock" else 1.0
        d.circ(ex2, ey2, er * big, fill=A((250, 236, 120), a))
        pw = er * (0.55 if mood == "shock" else 0.22)
        d.ell(ex2 + look * er * 0.4, ey2, pw, er * 0.8 * big, A(INK, a))
        d.circ(ex2 - er * 0.3, ey2 - er * 0.35, er * 0.18, fill=A(WHITE, a))
    b0, b1 = H1(30, -104), H1(96, -104)
    if mood == "fierce": b0, b1 = H1(28, -112), H1(96, -94)
    elif mood in ("listen", "shock"): b0, b1 = H1(30, -110), H1(96, -114)
    elif mood == "soft": b0, b1 = H1(30, -106), H1(96, -108)
    d.line([b0, b1], A(CROC_D, a), 10 * s)
    # ear slit (just behind the eye)
    q0, q1 = H1(8, -54), H1(-14, -44)
    if ear > 0:
        glow(d, (q0[0] + q1[0]) / 2, (q0[1] + q1[1]) / 2, 50 * s, (255, 230, 120), ear, 5)
    d.line([q0, q1], A(INK, 0.85 * a), 6 * s)
    if blush > 0: d.ell(*H1(110, -22), 30 * s, 13 * s, A(PINKB, 0.65 * blush * a))
    if mood == "soft": d.arc(*H1(250, -8), 40 * s, 14 * s, 20, 160, A(INK, 0.7 * a), 4 * s)
    return dict(ear=H1(-3, -49), eye=(ex2, ey2), snout=H1(320, -10), jaw=H1(180, 10), chin=H1(150, 34 + oj), head=H1(120, -30), back=L(-60, -122))

# ---------------- babies & eggs ----------------
def baby(d, x, y, s, t, mood="happy", a=1.0, ang=0.0, mouth=0.0, body=True):
    def R(u, v): c, sn = math.cos(ang), math.sin(ang); return x + (u * c - v * sn) * s, y + (u * sn + v * c) * s
    if body:
        d.poly([R(-30, 10), R(-110, 30 + 8 * math.sin(t * 7)), R(-104, 44), R(-20, 40)], A(BABY_D, a))
        d.ell(*R(-24, 34), 40 * s, 28 * s, A(BABY, a)); d.ell(*R(-24, 44), 32 * s, 14 * s, A(BABY_B, 0.8 * a))
    d.ell(*R(46, 18 + mouth * 6), 46 * s, 16 * s, A(BABY_D, a))
    d.ell(*R(42, 8), 50 * s, 20 * s, A(BABY, a)); d.circ(*R(88, 2), 5 * s, fill=A(INK, 0.6 * a))
    d.circ(*R(0, 0), 42 * s, fill=A(BABY, a))
    for i in range(3): d.ell(*R(-26 + i * 4, -18 + i * 16), 8 * s, 5 * s, A(BABY_B, 0.6 * a))
    ex, ey = R(8, -26); d.circ(ex, ey, 22 * s, fill=A(BABY, a))
    if mood == "happy": d.arc(ex, ey + 6 * s, 13 * s, 11 * s, 200, 340, A(INK, a), 5 * s)
    else:
        d.circ(ex, ey, 15 * s, fill=A(WHITE, a)); d.circ(ex + 4 * s, ey + 1 * s, 8 * s, fill=A(INK, a)); d.circ(ex, ey - 4 * s, 3 * s, fill=A(WHITE, a))
    if mouth > 0.1: d.ell(*R(40, 20), 18 * s, 9 * s * mouth, A((150, 40, 50), a))
    else: d.arc(*R(46, 8), 22 * s, 10 * s, 20, 160, A(INK, 0.7 * a), 3 * s)
    d.ell(*R(18, 10), 9 * s, 5 * s, A(PINKB, 0.6 * a))
def egg(d, x, y, s, t, crack=0.0, out=0.0, wob=0.0, mood="happy", a=1.0, mouth=0.0):
    ang = wob * 0.18 * math.sin(t * 18)
    def R(u, v): c, sn = math.cos(ang), math.sin(ang); return x + (u * c - v * sn) * s, y + (u * sn + v * c) * s
    d.ell(x, y + 58 * s, 44 * s, 8 * s, A((0, 0, 0), 0.25 * a))
    if out <= 0:
        pts = [R(math.cos(k / 20 * 6.283) * 44, math.sin(k / 20 * 6.283) * 58 - 0) for k in range(20)]
        d.poly(pts, A(SHELL, a)); d.ell(*R(-14, -22), 12 * s, 20 * s, A(WHITE, 0.7 * a))
        if crack > 0:
            zz = [R(-44 + i * 11, -4 + (8 if i % 2 else -8)) for i in range(int(1 + 8 * crack))]
            if len(zz) > 1: d.line(zz, A((120, 100, 80), a), 3.5 * s)
        return
    # hatched: lower shell cup + baby head + lid
    baby(d, x + 4 * s, y - 10 * s - 34 * s * out, 0.62 * s, t, mood, a, mouth=mouth, body=False)
    cup = [R(-44, -2)] + [R(math.cos(k / 12 * math.pi) * 44, math.sin(k / 12 * math.pi) * 58) for k in range(13)] + [R(44, -2)]
    zz = [R(44 - i * 11, -2 + (8 if i % 2 else -8)) for i in range(9)]
    d.poly(cup + zz, A(SHELL, a))
    lx, ly = x - 6 * s, y - 50 * s - 70 * s * out
    d.ell(lx, ly, 34 * s, 20 * s, A(SHELL, a))
def bubble(d, x, y, s_, k, a=1.0, size=40, col=WHITE, tc=NAVYT, tail=(0, 1)):
    if k <= 0: return
    sc = 0.6 + 0.4 * k; w = d.tlen(s_, size, 1) * sc + 46 * sc; h = size * 1.5 * sc
    d.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=A(col, a), r=h / 2)
    tx, ty = tail
    d.poly([(x - 14 * sc, y + h / 2 - 4), (x + 14 * sc, y + h / 2 - 4), (x + tx * 30 * sc, y + h / 2 + ty * 26 * sc)], A(col, a))
    d.text(x, y, s_, int(size * sc), A(tc, a), k=1)
def waves_up(d, t, x, y0, y1, a=1.0, col=(255, 236, 120), n=4, w0=90):
    for j in range(n):
        u = (t * 0.9 + j / n) % 1
        yy = lerp(y0, y1, u); ww = w0 * (1 + 0.6 * u)
        d.arc(x, yy, ww, ww * 0.45, 200, 340, A(col, a * math.sin(u * math.pi)), 9)
# ---------------- enemies (round head icons) ----------------
def enemy(d, kind, x, y, r, a=1.0, mood="sus"):
    if kind == "hippo":
        c = (150, 130, 170); d.circ(x - r * 0.6, y - r * 0.8, r * 0.22, fill=A(c, a)); d.circ(x + r * 0.6, y - r * 0.8, r * 0.22, fill=A(c, a))
        d.circ(x, y, r, fill=A(c, a)); d.ell(x, y + r * 0.45, r * 0.85, r * 0.5, A(mix(c, WHITE, 0.25), a))
        for sx in (-1, 1): d.ell(x + sx * r * 0.3, y + r * 0.35, r * 0.08, r * 0.12, A(INK, a))
    elif kind == "leopard":
        c = (236, 180, 70)
        for sx in (-1, 1): d.circ(x + sx * r * 0.7, y - r * 0.75, r * 0.28, fill=A(c, a))
        d.circ(x, y, r, fill=A(c, a))
        for u, v in ((-0.6, -0.3), (0.6, -0.3), (-0.3, -0.7), (0.35, -0.65), (-0.75, 0.3), (0.75, 0.3)): d.circ(x + u * r, y + v * r, r * 0.09, fill=A((110, 70, 30), a))
        d.ell(x, y + r * 0.4, r * 0.4, r * 0.28, A((250, 236, 210), a)); d.poly([(x - r * .12, y + r * .25), (x + r * .12, y + r * .25), (x, y + r * .38)], A(INK, a))
    elif kind == "hyena":
        c = (170, 150, 120)
        for sx in (-1, 1): d.ell(x + sx * r * 0.62, y - r * 0.85, r * 0.3, r * 0.4, A(c, a))
        d.circ(x, y, r, fill=A(c, a))
        for u, v in ((-0.5, 0.0), (0.55, 0.05), (-0.2, -0.6), (0.3, -0.55)): d.circ(x + u * r, y + v * r, r * 0.1, fill=A((90, 70, 50), a))
        d.ell(x, y + r * 0.45, r * 0.42, r * 0.3, A((90, 80, 70), a))
    else:   # monitor lizard
        c = (120, 130, 90); d.ell(x, y, r * 1.15, r * 0.7, A(c, a)); d.ell(x + r * 0.7, y + r * 0.15, r * 0.6, r * 0.35, A(c, a))
        for u in range(5): d.circ(x - r * 0.6 + u * r * 0.3, y - r * 0.2, r * 0.07, fill=A((230, 220, 150), a))
        d.line([(x + r * 1.25, y + r * 0.2), (x + r * 1.6, y + r * 0.2), (x + r * 1.75, y + r * 0.1)], A((220, 60, 80), a), r * 0.06)
        d.line([(x + r * 1.6, y + r * 0.2), (x + r * 1.75, y + r * 0.32)], A((220, 60, 80), a), r * 0.06)
    ex = x - r * 0.3 if kind != "monitor" else x + r * 0.2
    for i, ox in enumerate((0, r * 0.6 if kind != "monitor" else 0)):
        if kind == "monitor" and i: break
        d.circ(ex + ox, y - r * 0.15, r * 0.16, fill=A(WHITE, a)); d.circ(ex + ox, y - r * 0.12, r * 0.08, fill=A(INK, a))
        if mood == "sus": d.line([(ex + ox - r * .18, y - r * .38 + (r * .06 if i else -r * .06)), (ex + ox + r * .18, y - r * .38 - (r * .06 if i else -r * .06))], A(INK, a), r * 0.06)
def trailcam(d, x, y, s, t, a=1.0):
    d.rect(x - 4 * s, y, x + 4 * s, y + 160 * s, fill=A((110, 80, 50), a))
    d.rect(x - 50 * s, y - 70 * s, x + 50 * s, y + 20 * s, fill=A((70, 90, 60), a), r=12 * s)
    d.circ(x, y - 26 * s, 26 * s, fill=A((30, 30, 36), a)); d.circ(x, y - 26 * s, 14 * s, fill=A((80, 120, 170), a)); d.circ(x - 6 * s, y - 32 * s, 5 * s, fill=A(WHITE, 0.8 * a))
    if int(t * 2.5) % 2 == 0: d.circ(x + 34 * s, y - 56 * s, 6 * s, fill=A((255, 60, 60), a))
