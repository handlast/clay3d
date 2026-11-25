# Flat 2D characters for 《这只蝴蝶躲了200年？》 Colobura (dirce / annulata / cryptica).
# Look (ScienceDaily / Florida Museum 2026-11-12): adult wings nearly identical (brown, yellow forewing crossband,
# grey stripe under forewing); caterpillars velvety black, yellow branched spines, cream teardrops / rings / none.
# No dark outlines: shapes separated by value, highlights and glow only. Eye/mouth lines may be dark.
import math, random
from gchars import *

BWN = (96, 62, 44); BWN_D = (70, 44, 34); BWN_L = (140, 96, 66); BAND = (246, 206, 84); CREAM = (246, 232, 196)
GREYB = (176, 170, 160); BODY = (74, 54, 46); BODY_L = (120, 90, 74)
CATK = (44, 38, 50); CATK_L = (78, 70, 88); SPINE = (252, 204, 52); CATH = (232, 120, 60)
UVC = [(120, 210, 255), (200, 120, 255), (255, 110, 200)]      # dirce 376 / annulata 370 / cryptica 344 nm (false colour)
SPN = ["dirce", "annulata", "cryptica"]
FW = [(6, -8), (40, -78), (96, -122), (150, -128), (158, -104), (126, -40), (60, -4), (14, 10)]
FWB = [(52, -86), (112, -116), (130, -100), (74, -50)]          # yellow crossband
FWG = [(26, -34), (98, -72), (104, -62), (34, -20)]             # grey stripe
HW = [(10, 6), (70, 2), (118, 24), (132, 62), (112, 100), (78, 122), (60, 160), (48, 124), (22, 96), (8, 40)]

def _tf(x, y, s, side, k, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    def f(p):
        px, py = p[0] * side * k * s, p[1] * s
        return (x + px * ca - py * sa, y + px * sa + py * ca)
    return f

def bfly(d, x, y, s, t, a=1.0, flap=1.0, face="calm", uv=0.0, uvi=0, look=0.0, seed=0.0, ang=0.0, glow=0.0):
    if a <= 0.01 or s <= 0.01: return
    ph = t * 7.0 * flap + seed * 6.28
    k = 0.42 + 0.58 * abs(math.cos(ph)) if flap > 0 else 1.0
    uc = UVC[uvi % 3]
    if uv > 0.01 or glow > 0.01: glow_disc(d, x, y, 190 * s * k + 40 * s, uc, (0.35 * uv + 0.25 * glow) * a)
    for side in (-1, 1):
        f = _tf(x, y, s, side, k, ang)
        d.poly([f(p) for p in HW], A(mix(BWN_D, uc, 0.85 * uv), a))
        for j in range(3):
            d.line([f((22 + j * 8, 40 + j * 22)), f((116 - j * 14, 40 + j * 22))], A(mix(CREAM, WHITE, uv), (0.55 - 0.1 * uv) * a), 5 * s)
        d.circ(*f((96, 96)), 11 * s, fill=A(mix(BAND, uc, uv), a))
        d.poly([f(p) for p in FW], A(mix(BWN, uc, 0.75 * uv), a))
        d.poly([f(p) for p in FWG], A(mix(GREYB, WHITE, uv), 0.8 * a))
        d.poly([f(p) for p in FWB], A(mix(BAND, WHITE, 0.6 * uv), a))
        d.circ(*f((138, -112)), 7 * s, fill=A(WHITE, 0.8 * a))
        if uv > 0.01:
            for j in range(4): d.circ(*f((70 + j * 18, -60 + j * 30)), (6 + 3 * math.sin(t * 6 + j)) * s, fill=A(WHITE, 0.45 * uv * a))
    fb = _tf(x, y, s, 1, 1.0, ang)
    d.ell(*fb((0, 30)), 13 * s, 62 * s, fill=A(BODY, a)); d.ell(*fb((-4, 14)), 5 * s, 34 * s, fill=A(BODY_L, a))
    hx, hy = fb((0, -40))
    for sd in (-1, 1):
        ex, ey = fb((sd * 40, -112)); d.line([fb((sd * 8, -54)), (ex, ey)], A(BODY, a), 4 * s); d.circ(ex, ey, 8 * s, fill=A(BAND, a))
    d.circ(hx, hy, 26 * s, fill=A(BODY_L, a))
    if s < 0.18: return
    lk = math.sin(t * 0.9 + seed * 5) * 0.3 + look
    blink = (t + seed * 3.1) % 3.7 < 0.12
    for sd in (-1, 1):
        ex, ey = hx + sd * 12 * s, hy - 4 * s
        if blink: d.line([(ex - 8 * s, ey), (ex + 8 * s, ey)], A(INK, a), 3 * s); continue
        er = (11 if face == "shock" else 9) * s
        d.circ(ex, ey, er, fill=A(WHITE, a)); d.circ(ex + lk * 3 * s, ey + 1 * s, er * 0.55, fill=A(INK, a)); d.circ(ex + lk * 3 * s - 2 * s, ey - 2 * s, er * 0.2, fill=A(WHITE, a))
    my = hy + 12 * s
    if face == "shock": d.ell(hx, my + 2 * s, 5 * s, 6 * s, fill=A(INK, a))
    elif face == "happy": d.arc(hx, my - 4 * s, 9 * s, 7 * s, 20, 160, A(INK, a), 3 * s)
    elif face == "shy":
        d.line([(hx - 5 * s, my), (hx + 5 * s, my)], A(INK, a), 3 * s)
        for sd in (-1, 1): d.circ(hx + sd * 20 * s, my - 4 * s, 6 * s, fill=A((255, 140, 150), 0.7 * a))
    else: d.line([(hx - 5 * s, my), (hx + 5 * s, my)], A(INK, a), 3 * s)

def cater(d, x, y, s, t, a=1.0, mark="tear", face="calm", crawl=1.0, n=9, flip=1, seed=0.0):
    """side view caterpillar walking along +x*flip; segments on a travelling wave"""
    if a <= 0.01 or s <= 0.01: return
    segs = []
    for i in range(n):
        sx = x - flip * i * 34 * s
        sy = y - max(0, math.sin(t * 5 * crawl + seed - i * 0.7)) * 14 * s * crawl
        segs.append((sx, sy))
    for i, (sx, sy) in reversed(list(enumerate(segs))):
        r = 28 * s * (0.85 if i == n - 1 else 1)
        for sd in (-0.5, 0.5):                                                        # yellow branched spines
            bx = sx + sd * 18 * s; d.line([(bx, sy - r * 0.6), (bx + sd * 6 * s, sy - r - 26 * s)], A(SPINE, a), 5 * s)
            d.line([(bx + sd * 4 * s, sy - r - 14 * s), (bx + sd * 16 * s, sy - r - 22 * s)], A(SPINE, a), 3 * s)
        d.circ(sx, sy, r, fill=A(CATK, a)); d.circ(sx - 6 * s, sy - 10 * s, r * 0.45, fill=A(CATK_L, 0.7 * a))
        d.ell(sx, sy + r * 0.55, r * 0.5, r * 0.25, fill=A((96, 86, 70), a))           # little prolegs
        if 0 < i < n - 1:
            if mark == "tear":
                d.circ(sx + 2 * s, sy + 6 * s, 6 * s, fill=A(CREAM, a)); d.poly([(sx - 3 * s, sy + 3 * s), (sx + 7 * s, sy + 3 * s), (sx + 2 * s, sy - 9 * s)], A(CREAM, a))
            elif mark == "ring":
                d.circ(sx, sy + 4 * s, 9 * s, outline=A(CREAM, a), w=4 * s)
    hx, hy = segs[0][0] + flip * 22 * s, segs[0][1] + 2 * s
    d.circ(hx, hy, 26 * s, fill=A(CATH, a)); d.circ(hx - 6 * s * flip, hy - 9 * s, 10 * s, fill=A((250, 170, 110), 0.7 * a))
    for sd in (-1, 1): d.line([(hx + sd * 8 * s, hy - 22 * s), (hx + sd * 14 * s, hy - 40 * s)], A(SPINE, a), 4 * s)
    ex = hx + flip * 9 * s
    d.circ(ex, hy - 4 * s, 7 * s, fill=A(WHITE, a)); d.circ(ex + flip * 2 * s, hy - 3 * s, 3.6 * s, fill=A(INK, a))
    if face == "happy": d.arc(ex, hy + 8 * s, 7 * s, 5 * s, 20, 160, A(INK, a), 3 * s)
    elif face == "shock": d.circ(ex, hy + 11 * s, 4 * s, fill=A(INK, a))
    elif face == "munch":
        o = abs(math.sin(t * 14)); d.ell(ex + flip * 4 * s, hy + 10 * s, 5 * s, (2 + 4 * o) * s, fill=A(INK, a))
    else: d.line([(ex - 4 * s, hy + 10 * s), (ex + 5 * s, hy + 10 * s)], A(INK, a), 3 * s)

def cecropia(d, x, y, R, a=1.0, ang=0.0, col=(70, 150, 84), col2=(104, 182, 104), bites=0.0):
    """palmate Cecropia leaf: lobes fanning from a centre"""
    for i in range(9):
        th = ang - math.pi * 0.95 + i * math.pi * 0.95 * 2 / 8
        leaf_shape(d, x + math.cos(th) * R * 0.15, y + math.sin(th) * R * 0.15, R, th, col if i % 2 else col2, a, 0.34)
    d.circ(x, y, R * 0.12, fill=A(col2, a))

def forest(d, t, top=(30, 96, 78), bot=(12, 44, 40), seed=4, a=1.0):
    grad(d, top, bot)
    rr = random.Random(seed)
    for i in range(7):
        tx = -40 + i * 190 + rr.uniform(-30, 30); d.rect(tx, 0, tx + 46, 1960, fill=A(mix(bot, top, 0.35), a * 0.8))
    for i in range(14):
        lx, ly = rr.uniform(-60, 1140), rr.uniform(-40, 1900); sw = 0.08 * math.sin(t * 0.8 + i)
        leaf_shape(d, lx, ly, rr.uniform(140, 260), rr.uniform(0, 6.28) + sw, mix(top, (120, 200, 120), rr.uniform(0, 0.5)), a * 0.55, 0.4)
