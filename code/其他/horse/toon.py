"""Sticker-style outlined cartoon characters: fire horse + red goat."""
import math
from base import *
from chars import FIRE, FIRE_L, HRED, HRED_D, GOLD, PAPER, INKB, glow

OL = (34, 14, 16)
CREAM = (255, 226, 190); HOOF = (70, 36, 30); MANE_C = (255, 150, 40)

def capsule(d, x0, y0, x1, y1, r, col):
    d.line([(x0, y0), (x1, y1)], col, 2 * r); d.circ(x0, y0, r, fill=col); d.circ(x1, y1, r, fill=col)

def teardrop(cx, cy, w, h, lean=0.0, n=14):
    pts = []
    for k in range(n + 1):
        th = math.radians(-25 + 230 * k / n)
        pts.append((cx + w * math.cos(th), cy + w * math.sin(th)))
    # curved sides up to tip
    tipx, tipy = cx + lean * w, cy - h
    left = pts[-1]; right = pts[0]
    sideL = [(lerp(left[0], tipx, u) - math.sin(u * math.pi) * w * 0.25, lerp(left[1], tipy, u)) for u in (0.33, 0.66)]
    sideR = [(lerp(tipx, right[0], u) + math.sin(u * math.pi) * w * 0.25, lerp(tipy, right[1], u)) for u in (0.33, 0.66)]
    return pts + sideL + [(tipx, tipy)] + sideR

def draw_shapes(d, shapes, ol, a):
    """shapes: ('e',x,y,rx,ry,col) | ('c',x0,y0,x1,y1,r,col) | ('p',pts,col). outline pass then fill pass."""
    for pas in (0, 1):
        for sh in shapes:
            k = sh[0]; col = A(OL, a) if pas == 0 else A(sh[-1], a)
            o = ol if pas == 0 else 0
            if k == 'e': d.ell(sh[1], sh[2], sh[3] + o, sh[4] + o, col)
            elif k == 'c': capsule(d, sh[1], sh[2], sh[3], sh[4], sh[5] + o, col)
            elif k == 'p':
                if pas == 0:
                    pts = sh[1]; d.line(pts + [pts[0]], col, 2 * ol)
                    for p in pts: d.circ(p[0], p[1], ol, fill=col)
                d.poly(sh[1], col)

def eye(d, x, y, r, kind, a, look=(0.3, 0)):
    if kind == "proud":
        d.arc(x, y + r * 0.3, r * 0.9, r * 0.8, 200, 340, A(OL, a), r * 0.42); return
    if kind == "dizzy":
        for s_ in (-1, 1): d.line([(x - r * .7, y - r * .7 * s_), (x + r * .7, y + r * .7 * s_)], A(OL, a), r * 0.35)
        return
    if kind == "sad":
        d.ell(x, y, r * 0.95, r * 1.05, A(OL, a)); d.ell(x, y, r * 0.8, r * 0.9, A(WHITE, a))
        d.circ(x + look[0] * r * .3, y + r * .25, r * .45, fill=A(OL, a)); d.circ(x - r * .1, y + r * .05, r * .14, fill=A(WHITE, a))
        d.line([(x - r, y - r * 1.15), (x + r * .8, y - r * 1.5)], A(OL, a), r * 0.3); return
    big = 1.25 if kind in ("shock", "scream", "scared") else 1.0
    d.ell(x, y, r * 0.95 * big + 4, r * 1.15 * big + 4, A(OL, a)); d.ell(x, y, r * 0.95 * big, r * 1.15 * big, A(WHITE, a))
    pr_ = r * (0.38 if kind in ("shock", "scream") else 0.58)
    px, py = x + look[0] * r * 0.35, y + look[1] * r * 0.35
    d.circ(px, py, pr_, fill=A(OL, a)); d.circ(px - pr_ * .35, py - pr_ * .4, pr_ * .38, fill=A(WHITE, a))
    if kind == "angry": d.line([(x - r * 1.1, y - r * 1.6), (x + r * 1.0, y - r * 0.95)], A(OL, a), r * 0.32)
    if kind == "sus": d.line([(x - r * 1.1, y - r * 1.05), (x + r * 1.0, y - r * 1.45)], A(OL, a), r * 0.32)

def fire_tuft(d, x, y, w, h, t, a, seed=0, lean=0.0):
    fl = 1 + 0.12 * math.sin(t * 12 + seed * 1.9)
    sw = 0.35 * math.sin(t * 9 + seed)
    draw_shapes(d, [('p', teardrop(x, y, w, h * fl, lean + sw), FIRE)], 4, a)
    d.poly(teardrop(x, y + w * 0.15, w * 0.62, h * 0.7 * fl, lean + sw * 1.2), A(MANE_C, a))
    d.poly(teardrop(x, y + w * 0.3, w * 0.32, h * 0.4 * fl, lean + sw * 1.4), A(FIRE_L, a))

def horse(d, x, y, s, t, kind="chill", gallop=1.0, fire=1.0, a=1.0, flip=1, look=(0.4, 0)):
    X = lambda u: x + flip * u * s
    ph = t * 13 * gallop
    by = y - abs(math.sin(ph)) * 0.07 * s * gallop
    Y = lambda v: by + v * s
    d.ell(x, y + 1.18 * s, 1.15 * s, 0.13 * s, A((0, 0, 0), 0.28 * a))
    body = HRED; dark = HRED_D
    # tail (flame)
    if fire > 0:
        for i in range(2):
            fire_tuft(d, X(-0.95 - i * 0.1), Y(-0.15 + i * 0.15), 0.19 * s, 0.55 * s, t, a * fire, i + 7, lean=-flip * 1.6)
    # far legs
    legs = []
    for lx, off in ((-0.55, math.pi), (0.5, math.pi * 1.5)):
        sw = math.sin(ph + off) * 0.32 * gallop; lift = max(0, math.sin(ph + off)) * 0.18 * gallop
        legs.append(('c', X(lx), Y(0.2), X(lx + sw), Y(0.98 - lift), 0.15 * s, dark))
    draw_shapes(d, legs, 6, a)
    for sh in legs: d.ell(sh[3], sh[4] + 0.08 * s, 0.17 * s, 0.1 * s, A(HOOF, a))
    # mane flames (behind neck/head)
    if fire > 0:
        for i in range(5):
            u = i / 4
            fire_tuft(d, X(0.4 + u * 0.42), Y(-0.36 - u * 1.02), 0.21 * s, 0.66 * s, t, a * fire, i, lean=-flip * 1.1)
    hx, hy = X(1.1), Y(-1.0)
    shapes = [('e', x, Y(0.0), 0.95 * s, 0.58 * s, body),
              ('c', X(0.5), Y(-0.12), X(0.9), Y(-0.8), 0.34 * s, body),
              ('p', [(X(0.8), Y(-1.4)), (X(0.9), Y(-1.92)), (X(1.12), Y(-1.5))], body),
              ('e', hx, hy, 0.62 * s, 0.56 * s, body),
              ('e', X(1.56), Y(-0.82), 0.4 * s, 0.33 * s, CREAM)]
    near = []
    for lx, off in ((-0.62, 0), (0.58, math.pi * 0.5)):
        sw = math.sin(ph + off) * 0.32 * gallop; lift = max(0, math.sin(ph + off)) * 0.18 * gallop
        near.append(('c', X(lx), Y(0.25), X(lx + sw), Y(1.0 - lift), 0.17 * s, body))
    draw_shapes(d, near + shapes, 7, a)
    for sh in near: d.ell(sh[3], sh[4] + 0.09 * s, 0.19 * s, 0.11 * s, A(HOOF, a))
    d.ell(X(-0.05), Y(0.28), 0.62 * s, 0.2 * s, A(mix(body, CREAM, 0.3), 0.7 * a))      # belly
    d.ell(X(-0.25), Y(-0.3), 0.42 * s, 0.1 * s, A(WHITE, 0.28 * a))                 # shine
    d.ell(X(0.95), Y(-1.35), 0.22 * s, 0.08 * s, A(WHITE, 0.25 * a))
    d.poly([(X(0.86), Y(-1.48)), (X(0.91), Y(-1.78)), (X(1.04), Y(-1.52))], A(CREAM, a))
    # face
    eye(d, X(1.18), Y(-1.1), 0.18 * s, kind, a, (flip * look[0], look[1]))
    d.ell(X(1.72), Y(-0.88), 0.045 * s, 0.065 * s, A(OL, a))                       # nostril
    mx, my = X(1.56), Y(-0.66)
    if kind in ("scream", "shock"):
        d.ell(mx, my, 0.13 * s, 0.15 * s, A(OL, a)); d.ell(mx, my + 0.06 * s, 0.08 * s, 0.05 * s, A(TONGUE, a))
    elif kind in ("proud", "chill"):
        d.arc(mx, my - 0.1 * s, 0.17 * s, 0.12 * s, 20, 160, A(OL, a), 0.045 * s)
    elif kind == "sad":
        d.arc(mx, my + 0.05 * s, 0.13 * s, 0.08 * s, 200, 340, A(OL, a), 0.045 * s)
    else:
        d.line([(mx - 0.12 * s, my), (mx + 0.12 * s, my - 0.02 * s)], A(OL, a), 0.045 * s)
    d.ell(X(0.98), Y(-0.86), 0.12 * s, 0.07 * s, A((255, 120, 130), 0.75 * a))     # blush
    if kind in ("scared", "shock", "scream"): draw_shapes(d, [('p', teardrop(X(0.7), Y(-1.45), 0.07 * s, 0.16 * s), CYAN)], 3, a)

def goat(d, x, y, s, t, kind="chill", a=1.0, fire=1.0, flip=1, look=(0.4, 0)):
    X = lambda u: x + flip * u * s
    hop = abs(math.sin(t * 6)) * 0.04 * s
    Y = lambda v: y - hop + v * s
    d.ell(x, y + 0.98 * s, 0.95 * s, 0.11 * s, A((0, 0, 0), 0.28 * a))
    body = (232, 70, 66); wool = (250, 110, 96)
    legs = [('c', X(lx), Y(0.25), X(lx), Y(0.88), 0.12 * s, HRED_D) for lx in (-0.5, -0.2, 0.25, 0.55)]
    legs = [l[:-1] + ((200, 52, 50),) for l in legs]
    draw_shapes(d, legs, 6, a)
    for sh in legs: d.ell(sh[3], sh[4] + 0.07 * s, 0.14 * s, 0.08 * s, A(HOOF, a))
    puffs = [('e', X(-0.75 + i * 0.25), Y(-0.05 + 0.1 * math.sin(i * 2.1)), 0.3 * s, 0.3 * s, wool) for i in range(7)]
    puffs += [('e', X(-0.6 + i * 0.3), Y(0.18), 0.28 * s, 0.26 * s, wool) for i in range(5)]
    head = [('e', X(0.95), Y(-0.45), 0.36 * s, 0.42 * s, body),
            ('e', X(0.62), Y(-0.55), 0.18 * s, 0.08 * s, body)]
    draw_shapes(d, puffs + [('p', [(X(0.9), Y(-0.15)), (X(1.0), Y(0.12)), (X(1.08), Y(-0.15))], CREAM)] + head, 7, a)
    for i in range(5): d.circ(X(-0.6 + i * 0.28), Y(-0.15), 0.08 * s, fill=A(WHITE, 0.25 * a))
    # curled horns
    for hx_ in (0.82, 1.08):
        d.arc(X(hx_), Y(-0.92), 0.2 * s, 0.2 * s, 150, 420, A(OL, a), 0.13 * s)
        d.arc(X(hx_), Y(-0.92), 0.2 * s, 0.2 * s, 150, 420, A(GOLD, a), 0.08 * s)
    eye(d, X(1.02), Y(-0.5), 0.12 * s, kind, a, (flip * look[0], look[1]))
    mx, my = X(1.08), Y(-0.22)
    if kind in ("scream", "shock"): d.ell(mx, my, 0.08 * s, 0.1 * s, A(OL, a))
    elif kind == "sad": d.arc(mx, my + 0.04 * s, 0.09 * s, 0.06 * s, 200, 340, A(OL, a), 0.035 * s)
    else: d.arc(mx, my - 0.06 * s, 0.1 * s, 0.07 * s, 20, 160, A(OL, a), 0.035 * s)
    d.ell(X(0.82), Y(-0.33), 0.08 * s, 0.05 * s, A((255, 140, 150), 0.7 * a))
    if fire > 0:
        for i in range(3): fire_tuft(d, X(-0.5 + i * 0.35), Y(-0.35), 0.16 * s, 0.45 * s, t, a * fire, i + 3, lean=-flip * 0.6)
