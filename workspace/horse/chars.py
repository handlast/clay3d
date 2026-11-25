import math
from base import *
from fx import glow, face, mouth, sparks, embers, shake, stamp, flash, grad, rays, vignette
FIRE = (255, 120, 30); FIRE_L = (255, 200, 80); HRED = (214, 46, 40); HRED_D = (140, 24, 26); GOLD = (240, 190, 70)
PAPER = (238, 222, 188); PAPER_D = (196, 170, 128); INKB = (40, 30, 26); JADE = (60, 170, 140); SKY = (40, 60, 110)
# ---------- characters ----------
def flame(d, x, y, h, t, a=1.0, seed=0, col=FIRE, col2=FIRE_L):
    for k in range(3):
        w = h * (0.42 - k * 0.12); hh = h * (1 - k * 0.25)
        sw = math.sin(t * 9 + seed + k) * w * 0.25
        pts = [(x - w, y), (x - w * 0.6, y - hh * 0.45), (x + sw, y - hh), (x + w * 0.6, y - hh * 0.45), (x + w, y)]
        d.poly(pts, A(mix(col, col2, k / 2), a * (0.85 if k == 0 else 1)))
        d.ell(x, y, w, w * 0.55, A(mix(col, col2, k / 2), a))

def horse(d, x, y, s, t, kind="chill", gallop=1.0, fire=1.0, a=1.0, flip=1, look=0.4):
    """cartoon fire horse, facing right (flip=-1 faces left)"""
    X = lambda u: x + flip * u * s
    Y = lambda v: y + v * s
    ph = t * 14 * gallop
    bob = -abs(math.sin(ph)) * 0.08 * gallop
    y0 = y; y = y + bob * s
    d.ell(x, y0 + 1.15 * s, 1.2 * s, 0.12 * s, A((0, 0, 0), 0.3 * a))
    # tail flame
    if fire > 0:
        for i in range(4):
            ang = math.pi + 0.5 + 0.15 * math.sin(t * 10 + i)
            flame_pts = [(X(-1.0), Y(-0.2)), (X(-1.0 - 0.7 * math.cos(0.4 + i * 0.25)), Y(-0.2 - 0.5 + i * 0.25 + 0.1 * math.sin(t * 12 + i))), (X(-1.0), Y(0.1))]
            d.poly(flame_pts, A(mix(FIRE, FIRE_L, i / 4), a * fire))
    # legs
    for i, (lx, off) in enumerate(((-0.65, 0), (-0.45, math.pi), (0.45, math.pi * 0.5), (0.65, math.pi * 1.5))):
        sw = math.sin(ph + off) * 0.35 * gallop
        kx = X(lx + sw * 0.5); ky = Y(0.55)
        fx_, fy_ = X(lx + sw), Y(1.05 - max(0, math.sin(ph + off)) * 0.2 * gallop)
        col = HRED_D if i % 2 else mix(HRED, HRED_D, 0.3)
        d.line([(X(lx), Y(0.2)), (kx, ky), (fx_, fy_)], A(col, a), 0.16 * s)
        d.ell(fx_, fy_ + 0.03 * s, 0.1 * s, 0.06 * s, A(INKB, a))
    # body
    d.ell(x, Y(0.05), 1.05 * s, 0.55 * s, A(HRED_D, a)); d.ell(X(-0.04), Y(0.0), 1.0 * s, 0.5 * s, A(HRED, a))
    d.ell(X(-0.2), Y(-0.22), 0.5 * s, 0.14 * s, A(WHITE, 0.25 * a))
    # neck + head
    d.poly([(X(0.55), Y(-0.3)), (X(0.95), Y(-1.05)), (X(1.35), Y(-0.85)), (X(0.95), Y(0.1))], A(HRED, a))
    hx, hy = X(1.25), Y(-1.0)
    d.ell(hx, hy, 0.48 * s, 0.4 * s, A(HRED, a))
    d.ell(X(1.6), Y(-0.85), 0.3 * s, 0.26 * s, A(mix(HRED, PAPER, 0.35), a))
    d.circ(X(1.72), Y(-0.86), 0.04 * s, fill=A(INKB, a))
    d.poly([(X(1.0), Y(-1.3)), (X(1.08), Y(-1.62)), (X(1.2), Y(-1.32))], A(HRED_D, a))
    # mane flames
    if fire > 0:
        for i in range(6):
            u = i / 5
            flame(d, X(0.75 + u * 0.45), Y(-0.45 - u * 0.75), 0.42 * s * (1 + 0.15 * math.sin(t * 11 + i)), t, a * fire, i * 1.7)
    # face (eyes on head, mouth on muzzle)
    er = 0.12 * s; ex, ey = X(1.25), Y(-1.08)
    big = 1.35 if kind in ("scared", "scream", "shock") else 1.0
    if kind == "proud":
        d.arc(ex, ey + er * 0.4, er, er, 200, 340, A(INKB, a), er * 0.45)
    elif kind == "dizzy":
        d.line([(ex - er, ey - er), (ex + er, ey + er)], A(INKB, a), er * 0.4); d.line([(ex - er, ey + er), (ex + er, ey - er)], A(INKB, a), er * 0.4)
    else:
        d.circ(ex, ey, er * big, fill=A(WHITE, a)); d.circ(ex + flip * look * er * 0.5, ey, er * 0.5 * (0.8 if kind == "shock" else 1), fill=A(INKB, a))
        if kind == "angry": d.line([(ex - er * 1.2, ey - er * 1.5), (ex + er * 1.2, ey - er * 0.9)], A(INKB, a), er * 0.35)
        if kind == "sus": d.line([(ex - er * 1.2, ey - er * 1.0), (ex + er * 1.2, ey - er * 1.4)], A(INKB, a), er * 0.35)
    mx, my = X(1.62), Y(-0.72)
    if kind in ("scream", "shock"): d.ell(mx, my, 0.1 * s, 0.13 * s, A(INKB, a)); d.ell(mx, my + 0.05 * s, 0.06 * s, 0.04 * s, A(TONGUE, a))
    elif kind in ("proud", "chill"): d.arc(mx - flip * 0.05 * s, my - 0.06 * s, 0.13 * s, 0.09 * s, 20, 160, A(INKB, a), 0.035 * s)
    elif kind == "sus": d.line([(mx - 0.1 * s, my), (mx + 0.1 * s, my - 0.02 * s)], A(INKB, a), 0.03 * s)
    if kind in ("scared", "shock", "scream"): d.ell(X(0.85), Y(-1.35), 0.06 * s, 0.1 * s, A(CYAN, a))

def goat(d, x, y, s, t, kind="chill", a=1.0, fire=1.0):
    d.ell(x, y + 0.85 * s, 0.9 * s, 0.1 * s, A((0, 0, 0), 0.3 * a))
    for lx in (-0.5, -0.25, 0.3, 0.55): d.line([(x + lx * s, y + 0.2 * s), (x + lx * s, y + 0.8 * s)], A(HRED_D, a), 0.12 * s)
    for i in range(7): d.circ(x + (-0.6 + i * 0.2) * s, y + (0.0 + 0.08 * math.sin(i * 2)) * s, 0.32 * s, fill=A(mix(HRED, FIRE, 0.25), a))
    d.ell(x + 0.85 * s, y - 0.35 * s, 0.32 * s, 0.38 * s, A(HRED, a))
    d.arc(x + 0.7 * s, y - 0.75 * s, 0.25 * s, 0.25 * s, 180, 360, A(GOLD, a), 0.09 * s); d.arc(x + 1.0 * s, y - 0.75 * s, 0.25 * s, 0.25 * s, 180, 360, A(GOLD, a), 0.09 * s)
    d.poly([(x + 0.95 * s, y - 0.05 * s), (x + 1.05 * s, y + 0.3 * s), (x + 0.85 * s, y + 0.0 * s)], A(PAPER, a))
    face(d, x + 0.85 * s, y - 0.35 * s, 0.33 * s, kind, a)
    if fire: 
        for i in range(3): flame(d, x + (-0.4 + i * 0.3) * s, y - 0.25 * s, 0.4 * s, t, a * fire, i * 3)

def scholar(d, x, y, s, t, kind="chill", a=1.0, arm=0.0):
    d.ell(x, y + 1.25 * s, 0.8 * s, 0.1 * s, A((0, 0, 0), 0.3 * a))
    d.poly([(x - 0.6 * s, y + 1.2 * s), (x - 0.35 * s, y + 0.2 * s), (x + 0.35 * s, y + 0.2 * s), (x + 0.6 * s, y + 1.2 * s)], A((52, 70, 120), a))
    d.line([(x, y + 0.25 * s), (x, y + 1.15 * s)], A((30, 40, 80), a), 0.04 * s)
    ax = x + 0.35 * s; ay = y + 0.35 * s; ang = -0.4 - arm * 1.4
    hx, hy = ax + math.cos(ang) * 0.6 * s, ay - math.sin(-ang) * 0.6 * s
    d.line([(ax, ay), (hx, hy)], A((52, 70, 120), a), 0.18 * s); d.circ(hx, hy, 0.1 * s, fill=A((250, 214, 170), a))
    d.circ(x, y - 0.15 * s, 0.42 * s, fill=A((250, 214, 170), a))
    d.rect(x - 0.4 * s, y - 0.62 * s, x + 0.4 * s, y - 0.42 * s, fill=A(INKB, a), r=6)  # futou hat
    d.rect(x - 0.65 * s, y - 0.58 * s, x + 0.65 * s, y - 0.52 * s, fill=A(INKB, a))
    d.ell(x, y - 0.68 * s, 0.25 * s, 0.14 * s, A(INKB, a))
    for s_ in (-1, 1): d.line([(x + s_ * 0.06 * s, y + 0.18 * s), (x + s_ * 0.12 * s, y + 0.45 * s)], A(INKB, 0.8 * a), 0.03 * s)
    face(d, x, y - 0.12 * s, 0.4 * s, kind, a)

def girl(d, x, y, s, t, kind="chill", a=1.0):
    d.ell(x, y + 1.25 * s, 0.7 * s, 0.1 * s, A((0, 0, 0), 0.3 * a))
    d.poly([(x - 0.5 * s, y + 1.2 * s), (x - 0.3 * s, y + 0.2 * s), (x + 0.3 * s, y + 0.2 * s), (x + 0.5 * s, y + 1.2 * s)], A((220, 70, 110), a))
    for i in range(5): d.circ(x + (-0.3 + i * 0.15) * s, y + (0.5 + (i % 2) * 0.35) * s, 0.06 * s, fill=A(WHITE, 0.8 * a))
    d.rect(x - 0.34 * s, y + 0.55 * s, x + 0.34 * s, y + 0.7 * s, fill=A(GOLD, a))
    d.poly([(x - 0.15 * s, y + 0.2 * s), (x, y + 0.5 * s), (x + 0.15 * s, y + 0.2 * s)], A(WHITE, a))
    d.circ(x, y - 0.6 * s, 0.32 * s, fill=A(INKB, a)); d.circ(x, y - 0.15 * s, 0.4 * s, fill=A((252, 224, 196), a))
    d.ell(x, y - 0.42 * s, 0.42 * s, 0.18 * s, A(INKB, a))
    d.line([(x + 0.2 * s, y - 0.75 * s), (x + 0.45 * s, y - 0.95 * s)], A(GOLD, a), 0.04 * s)
    for s_ in (-1, 1): d.ell(x + s_ * 0.25 * s, y - 0.02 * s, 0.07 * s, 0.04 * s, A((255, 140, 150), 0.7 * a))
    face(d, x, y - 0.12 * s, 0.38 * s, kind, a)

def baby(d, x, y, r, a=1.0, col=(255, 210, 180)):
    d.circ(x, y + r * 1.2, r * 0.9, fill=A((250, 250, 245), a)); d.circ(x, y, r, fill=A(col, a))
    d.circ(x - r * .35, y - r * .05, r * .12, fill=A(INKB, a)); d.circ(x + r * .35, y - r * .05, r * .12, fill=A(INKB, a))
    d.arc(x, y + r * .2, r * .25, r * .18, 20, 160, A(INKB, a), r * .1)

def tile(d, x, y, sz, ch, col, a=1.0, sub=None, subcol=WHITE, glowc=None):
    if glowc: glow(d, x, y, sz * 1.1, glowc, a)
    d.rect(x - sz / 2, y - sz / 2, x + sz / 2, y + sz / 2, fill=A(col, a), r=sz * 0.14)
    d.rect(x - sz / 2 + 10, y - sz / 2 + 10, x + sz / 2 - 10, y + sz / 2 - 10, outline=A(WHITE, 0.5 * a), w=4, r=sz * 0.11)
    d.text(x, y - (sz * 0.06 if sub else 0), ch, int(sz * 0.62), A(WHITE, a), k=1)
    if sub: d.text(x, y + sz * 0.36, sub, int(sz * 0.14), A(subcol, a), k=0)

def paper_bg(d, t):
    grad(d, (60, 30, 24), (24, 12, 10))
    for i in range(14):
        y = (i * 150 + t * 20) % 2100 - 100
        d.line([(0, y), (1080, y + 40)], A((90, 50, 36), 0.25), 3)

