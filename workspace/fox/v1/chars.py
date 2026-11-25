# Flat 2D characters for 《狐狸变温顺》: silver fox (tame 0..1 morph), mouse, brain, neurons
import math, random
from fx import *
import easing as E

FUR = (92, 104, 132); FUR_D = (64, 74, 100); FUR_L = (150, 162, 190); CREAM = (244, 236, 220); NOSE = (40, 36, 52)
TAME = (255, 168, 90); MEAN = (255, 86, 96); MINT = (110, 230, 170); GOLD = (255, 205, 70); NAVYT = (22, 22, 40)
PINK = (255, 150, 200); CYAN2 = (90, 220, 255); MAG = (255, 90, 200)
def mix(c1, c2, k): return tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3))
def lerp_(a, b, k): return a + (b - a) * k
def rot(px, py, cx, cy, a): ca, sa = math.cos(a), math.sin(a); return (cx + (px - cx) * ca - (py - cy) * sa, cy + (px - cx) * sa + (py - cy) * ca)

def flatbg(d, top, bot, t, deco=True, col=WHITE):
    grad(d, top, bot)
    if deco:
        for i in range(7):
            x = (i * 173 + t * 18) % 1300 - 110; y = 300 + (i * 251) % 1200
            d.circ(x, y, 60 + (i * 37) % 80, fill=A(col, 0.035))

def fox(d, x, y, s, t, tame=0.0, mood="neutral", a=1.0, flip=1, wag=0.0, bob=1.0):
    """side view, facing right if flip=1. tame: 0 = wild look, 1 = floppy ears, short snout, curly tail."""
    S = lambda px, py: (x + flip * px * s, y + py * s)
    by = -6 * math.sin(t * 3) * bob
    # tail
    if tame < 0.5:
        ang = math.radians(200 - 15 * math.sin(t * 2 + wag))
    k = tame
    pts = []
    for i in range(20):
        u = i / 19
        straight = (-150 - 170 * u, -10 + 40 * u + 10 * math.sin(t * 3 + wag + u * 3) * u)
        curl_a = math.pi * 0.2 + u * math.pi * 1.6
        curl = (-150 - 70 * math.sin(curl_a) * (1 - 0.35 * u) - 30 * u, -40 - 80 * (1 - math.cos(curl_a)) * 0.6 * (1 - 0.2 * u))
        pts.append((lerp_(straight[0], curl[0], k), lerp_(straight[1], curl[1], k) + by))
    for i, (px, py) in enumerate(pts):
        r = 36 * (0.55 + math.sin(i / 19 * math.pi) * 0.7)
        c = CREAM if i > 15 else FUR
        d.circ(*S(px, py), r * s, fill=A(c, a))
    # legs
    for lx in (-110, -60, 60, 105):
        sw = 6 * math.sin(t * 6 + lx) * bob
        d.rect(*S(lx - 14 + sw, 40 + by), *S(lx + 14 + sw, 150), fill=A(FUR_D, a), r=12 * s) if flip == 1 else d.rect(*S(lx + 14 + sw, 40 + by), *S(lx - 14 + sw, 150), fill=A(FUR_D, a), r=12 * s)
    # body
    d.ell(*S(0, 10 + by), 170 * s, 82 * s, A(FUR, a))
    d.ell(*S(110, 30 + by), 70 * s, 60 * s, A(CREAM, a))
    # head
    hx, hy = 165, -70 + by
    snout = lerp_(120, 70, k)
    d.poly([S(hx - 20, hy - 60), S(hx + snout, hy + 18), S(hx - 10, hy + 60)], A(FUR, a))
    d.circ(*S(hx, hy), 78 * s, fill=A(FUR, a))
    d.poly([S(hx + 10, hy + 20), S(hx + snout, hy + 18), S(hx + 10, hy + 58)], A(CREAM, a))
    d.circ(*S(hx + snout, hy + 16), 15 * s, fill=A(NOSE, a))
    # ears: upright triangles -> floppy (rotated down)
    for ex, sz, c in ((-40, 1.0, FUR_D), (10, 0.9, FUR)):
        bx, byy = hx + ex, hy - 55
        tip = (bx + 10, byy - 110 * sz)
        flop = math.radians(115) * k * flip
        tipx, tipy = rot(tip[0], tip[1], bx, byy, math.radians(115) * k)
        e1 = S(bx - 34 * sz, byy + 10); e2 = S(bx + 34 * sz, byy + 10); e3 = S(tipx, tipy)
        d.poly([e1, e2, e3], A(c, a))
        ix, iy = rot(bx + 8, byy - 70 * sz, bx, byy, math.radians(115) * k)
        d.poly([S(bx - 14 * sz, byy), S(bx + 18 * sz, byy), S(ix, iy)], A(PINK if k > 0.5 else (200, 140, 160), 0.7 * a))
    # eye + mouth
    ex_, ey_ = hx + 30, hy - 8
    if mood == "angry":
        d.ell(*S(ex_, ey_), 14 * s, 9 * s, A(GOLD, a)); d.ell(*S(ex_ + 2, ey_), 5 * s, 9 * s, A(NOSE, a))
        d.line([S(ex_ - 22, ey_ - 26), S(ex_ + 22, ey_ - 12)], A(NOSE, a), 7 * s)
        # snarl teeth
        mx = hx + snout * 0.55; my = hy + 44
        d.poly([S(mx - 40, my - 4), S(mx + 30, my - 6), S(mx + 20, my + 16), S(mx - 30, my + 18)], A((120, 40, 60), a))
        for j in range(4): d.poly([S(mx - 34 + j * 18, my - 4), S(mx - 26 + j * 18, my + 10), S(mx - 18 + j * 18, my - 4)], A(WHITE, a))
    elif mood == "happy":
        px_, py_ = S(ex_, ey_); d.arc(px_, py_ + 4 * s, 16 * s, 12 * s, 200, 340, A(NOSE, a), 7 * s)
        d.circ(*S(ex_ - 6, ey_ + 30), 14 * s, fill=A(PINK, 0.5 * a))
        mx = hx + snout * 0.5; my = hy + 42
        d.poly([S(mx - 10, my), S(mx + 20, my), S(mx + 6, my + 30)], A((240, 110, 140), a))
    else:
        d.circ(*S(ex_, ey_), 11 * s, fill=A(NOSE, a)); d.circ(*S(ex_ + 3, ey_ - 4), 4 * s, fill=A(WHITE, a))
    return S(hx, hy)

def mouse(d, x, y, s, t, mood="neutral", a=1.0, flip=1, col=(200, 200, 215)):
    S = lambda px, py: (x + flip * px * s, y + py * s)
    pts = [S(-80 - 60 * u, 20 - 30 * math.sin(u * 3 + t * 4) * u) for u in [i / 10 for i in range(11)]]
    d.line(pts, A((240, 170, 190), a), 6 * s)
    d.ell(*S(0, 0), 90 * s, 55 * s, A(col, a))
    d.poly([S(50, -40), S(130, 10), S(50, 40)], A(col, a))
    d.circ(*S(130, 10), 9 * s, fill=A((240, 120, 150), a))
    d.circ(*S(30, -50), 30 * s, fill=A(col, a)); d.circ(*S(30, -50), 18 * s, fill=A((245, 180, 200), a))
    if mood == "angry":
        d.line([S(66, -24), S(96, -12)], A(NOSE, a), 6 * s); d.circ(*S(84, -6), 8 * s, fill=A(MEAN, a))
    else:
        d.circ(*S(84, -8), 8 * s, fill=A(NOSE, a))

def brain(d, cx, cy, s, a=1.0, col=(255, 170, 190), col2=(230, 130, 160)):
    """flat side-view brain (mammal-ish), front to the right"""
    lobes = [(-90, -40, 120, 90), (40, -50, 120, 85), (-20, -90, 110, 60), (120, 10, 70, 60), (-130, 20, 70, 60)]
    for lx, ly, rx, ry in lobes: d.ell(cx + lx * s, cy + ly * s, rx * s, ry * s, A(col, a))
    d.ell(cx - 170 * s, cy + 70 * s, 70 * s, 45 * s, A(col2, a))  # cerebellum
    d.rect(cx - 70 * s, cy + 60 * s, cx - 20 * s, cy + 190 * s, fill=A(col2, a), r=20 * s)  # brainstem
    for i in range(6):
        x0 = cx + (-150 + i * 55) * s
        d.arc(x0 + 35 * s, cy - 45 * s, 35 * s, 55 * s, 200, 330, A(col2, 0.8 * a), 8 * s)

def neuron(d, x, y, r, col, a=1.0, t=0.0, lit=1.0):
    if lit > 0.01:
        for i in range(5, 0, -1): d.circ(x, y, r * (1 + i * 0.6), fill=A(col, 0.06 * a * lit))
    for j in range(5):
        an = j * 1.256 + x * 0.01
        d.line([(x, y), (x + math.cos(an) * r * 2.2, y + math.sin(an) * r * 2.2)], A(mix((70, 80, 110), col, lit), 0.8 * a), max(2, r * 0.25))
    d.circ(x, y, r, fill=A(mix((70, 80, 110), col, lit), a))
    if lit > 0.5: d.circ(x - r * 0.3, y - r * 0.3, r * 0.3, fill=A(WHITE, 0.6 * a * lit))
