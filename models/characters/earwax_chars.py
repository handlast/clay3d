# Characters for 《耳屎是防虫墙》: fire ant, earwax blob, ear canal, beaker, skin cells
import math, random
from fx import *
import easing as E

WAX = (218, 160, 62); WAX_D = (168, 112, 36); WAX_L = (255, 210, 120); WAX_DRY = (232, 200, 140)
ANT = (206, 84, 48); ANT_D = (150, 52, 30); ANT_L = (255, 140, 100)
SKIN = (246, 176, 160); SKIN_D = (214, 128, 120); SKIN_L = (255, 214, 200); EARIN = (120, 40, 60)
GLASS = (190, 230, 250); NAVYT = (22, 22, 40); GOLD = (255, 200, 60); WATERC = (110, 190, 255); MINT = (110, 230, 170)
WARM1 = (255, 196, 120); WARM2 = (230, 120, 70)
def rot(pts, ang, ox, oy):
    c, s = math.cos(ang), math.sin(ang)
    return [(ox + u * c - v * s, oy + u * s + v * c) for u, v in pts]

def ant(d, x, y, s, t, a=1.0, mood="happy", walk=1.0, ang=0.0, look=0.0, slip=0.0, wax=0.0, face_=True, legs_up=0.0):
    """fire ant facing right (ang rotates). walk = leg-cycle speed factor; slip = legs splayed; wax = blobs stuck on body"""
    def R(u, v): return rot([(u * s, v * s)], ang, x, y)[0]
    ph = t * 14 * walk
    # legs (3 pairs) from thorax
    for i, lx in enumerate((-10, 6, 22)):
        for side in (-1, 1):
            sw = math.sin(ph + i * 2.1 + (side > 0) * math.pi) * 14 * (1 - slip)
            spl = slip * 30
            knee = R(lx + sw * 0.5, side * (34 + spl * 0.5) - 26 * legs_up)
            foot = R(lx + sw + side * spl * 0.3 + (i - 1) * 22, side * (62 + spl) - 60 * legs_up)
            root = R(lx, side * 10)
            d.line([root, knee, foot], A(ANT_D, a), 7 * s)
            d.circ(*foot, 5 * s, fill=A(ANT_D, a))
    # gaster, petiole, thorax, head
    for (u, v, rx, ry, c) in ((-70, 0, 46, 36, ANT), (-28, 0, 12, 10, ANT_D), (4, 0, 30, 20, ANT), (54, -6, 34, 32, ANT)):
        cx, cy = R(u, v)
        d.ell(cx, cy, rx * s, ry * s, A(c, a))
    gx, gy = R(-80, -14); d.ell(gx, gy, 18 * s, 10 * s, A(ANT_L, 0.6 * a))
    hx, hy = R(60, -18); d.ell(hx, hy, 12 * s, 7 * s, A(ANT_L, 0.6 * a))
    # antennae
    for side in (-1, 1):
        b = R(72, -30 + side * 8); e1 = R(96, -70 + side * 18 + 4 * math.sin(t * 6 + side)); e2 = R(128, -62 + side * 30 + 6 * math.sin(t * 7 + side))
        d.line([b, e1, e2], A(ANT_D, a), 5 * s)
    # mandibles
    for side in (-1, 1):
        m0 = R(84, 6 + side * 8); m1 = R(100, 14 + side * 4)
        d.line([m0, m1], A(ANT_D, a), 6 * s)
    if face_:
        fx_, fy_ = R(60, -4)
        face(d, fx_, fy_, 30 * s, mood, a, look)
    if wax > 0:
        rr_ = random.Random(3)
        for j in range(int(9 * wax)):
            u, v = rr_.choice([(-80, -20), (-60, 20), (-50, -30), (10, -16), (20, 14), (50, 20), (40, -36), (-90, 10), (0, 30)])
            cx, cy = R(u, v); rad = rr_.uniform(9, 16) * s
            d.circ(cx, cy, rad, fill=A(WAX, a)); d.circ(cx - rad * 0.3, cy - rad * 0.3, rad * 0.35, fill=A(WAX_L, 0.8 * a))

def blob_pts(x, y, r, t, n=28, wob=0.08, seed=0, flat=0.0):
    pts = []
    for i in range(n):
        th = i / n * 2 * math.pi
        k = 1 + wob * math.sin(th * 3 + seed) + wob * 0.6 * math.sin(th * 5 + t * 2 + seed)
        yy = math.sin(th) * r * k * (1 - flat)
        if flat > 0 and yy > 0: yy *= 0.4
        pts.append((x + math.cos(th) * r * k * (1 + flat * 0.6), y + yy))
    return pts
def waxguy(d, x, y, r, t, mood="happy", a=1.0, sq=0.0, look=0.0, dry=0.0, face_=True):
    """the earwax character: lumpy amber blob with gloss"""
    col = mix(WAX, WAX_DRY, dry); colD = mix(WAX_D, (190, 160, 110), dry)
    d.ell(x, y + r * 0.9, r * 0.9, r * 0.15, A((0, 0, 0), 0.22 * a))
    d.poly(blob_pts(x, y + r * 0.05, r * (1 + sq * 0.3), t, seed=1, flat=sq), A(colD, a))
    d.poly(blob_pts(x - r * 0.04, y, r * 0.94 * (1 + sq * 0.3), t, seed=1, flat=sq), A(col, a))
    d.ell(x - r * 0.38, y - r * 0.45 * (1 - sq), r * 0.26, r * 0.14, A(WAX_L, 0.8 * a * (1 - dry)))
    d.circ(x - r * 0.12, y - r * 0.62 * (1 - sq), r * 0.06, fill=A(WHITE, 0.6 * a * (1 - dry)))
    if dry > 0.3:
        for j in range(5):
            u = -0.5 + j * 0.25
            d.line([(x + u * r, y - r * 0.3), (x + u * r + r * 0.1, y + r * 0.1)], A(colD, a * dry), r * 0.04)
    if face_: face(d, x, y + r * 0.05 * sq, r, mood, a, look)

def beaker(d, x, y, w, h, a=1.0, rim=1.0, rough=0.0, t=0.0):
    """glass beaker, rim coated with earwax band (rim = band fill 0..1). returns rim y"""
    d.rect(x - w / 2, y - h, x + w / 2, y, fill=A(GLASS, 0.18 * a), r=24)
    d.rect(x - w / 2, y - h, x - w / 2 + 16, y, fill=A(GLASS, 0.55 * a), r=8)
    d.rect(x + w / 2 - 16, y - h, x + w / 2, y, fill=A(GLASS, 0.55 * a), r=8)
    d.rect(x - w / 2 + 30, y - h + 40, x - w / 2 + 50, y - 60, fill=A(WHITE, 0.25 * a), r=10)
    if rim > 0:
        bh = 150
        for side in (-1, 1):
            x0 = x + side * w / 2 - (16 if side > 0 else 0)
            yb = y - h; d.rect(x0 - 10, yb - 6, x0 + 26, yb + bh * rim, fill=A(WAX, a), r=12)
            if rough > 0:
                rr_ = random.Random(7 + side)
                for j in range(int(10 * rough)):
                    d.circ(x0 + 8 + rr_.uniform(-14, 14), yb + rr_.uniform(0, bh * rim), rr_.uniform(6, 13), fill=A(WAX_D, a))
            else:
                d.rect(x0 - 4, yb, x0 + 4, yb + bh * rim, fill=A(WAX_L, 0.8 * a), r=4)
    return y - h

def canal(d, t, y0=960, a=1.0, wax=1.0, thick=0.0, open_=1.0):
    """horizontal ear-canal cross-section: entrance left, eardrum right"""
    top, bot = y0 - 230 * open_, y0 + 230 * open_
    d.rect(-40, -40, 1120, top, fill=A(SKIN, a)); d.rect(-40, bot, 1120, 2000, fill=A(SKIN, a))
    d.rect(-40, top - 26, 1120, top, fill=A(SKIN_D, a)); d.rect(-40, bot, 1120, bot + 26, fill=A(SKIN_D, a))
    d.rect(-40, top, 1120, bot, fill=A(EARIN, a))
    # eardrum
    d.ell(1010, y0, 40, 220 * open_, A((255, 200, 200), 0.9 * a))
    if wax > 0:
        th = 22 + 120 * thick
        for yy, sd in ((top, 1), (bot, -1)):
            pts = [(x, yy + sd * (th * wax * (0.6 + 0.4 * math.sin(x / 70 + 1.3)) * (1 if thick < 0.5 else 0.7 + 0.6 * abs(math.sin(x / 40))))) for x in range(-40, 1001, 20)]
            d.poly([(-40, yy)] + pts + [(1000, yy)], A(WAX, a))
            d.line(pts, A(WAX_L, 0.6 * a), 6)
    return top, bot

def skincell(d, x, y, r, t, a=1.0, ang=0.0, col=SKIN_L):
    pts = [(math.cos(th) * r, math.sin(th) * r * 0.6) for th in [i / 6 * 2 * math.pi for i in range(6)]]
    d.poly(rot(pts, ang, x, y), A(col, a))
    d.circ(x, y, r * 0.18, fill=A(SKIN_D, 0.8 * a))

def drop(d, x, y, r, a=1.0, col=WATERC):
    d.poly([(x, y - r * 1.8), (x - r * 0.8, y - r * 0.3), (x + r * 0.8, y - r * 0.3)], A(col, a))
    d.circ(x, y, r, fill=A(col, a)); d.circ(x - r * 0.35, y - r * 0.3, r * 0.25, fill=A(WHITE, 0.7 * a))

def bubble(d, x, y, s_, k, a=1.0, size=40, col=WHITE, tc=NAVYT):
    if k <= 0: return
    w = d.tlen(s_, size, 1) + 40; hh = size * 0.85
    sc = min(1, k)
    d.rect(x - w / 2 * sc, y - hh * sc, x + w / 2 * sc, y + hh * sc, fill=A(col, a), r=hh * sc)
    d.poly([(x - 14, y + hh * sc - 4), (x, y + hh * sc + 24 * sc), (x + 14, y + hh * sc - 4)], A(col, a))
    if sc > 0.6: d.text(x, y, s_, int(size * sc), A(tc, a), k=1)
