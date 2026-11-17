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

def R(d, x0, y0, x1, y1, **kw): d.rect(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), **kw)
def fox(d, x, y, s, t, tame=0.0, mood="neutral", a=1.0, flip=1, wag=0.0, bob=1.0, ears=None, snout=None, curl=None, col=None, lunge=0.0):
    """side view, facing right if flip=1 (all geometry in local coords, mirrored once by S -> no flip glitches).
    tame drives ears/snout/curl unless given separately (0 wild .. 1 domestic)."""
    ek = tame if ears is None else ears; sk = tame if snout is None else snout; ck = tame if curl is None else curl
    fur = col or FUR; furd = mix(fur, (0, 0, 0), 0.3)
    S = lambda px, py: (x + flip * (px + lunge) * s, y + py * s)
    by = -5 * math.sin(t * 3) * bob
    # tail: chain whose heading turns smoothly with curl (never changes direction of turn)
    px, py = -150.0, -5.0 + by; ang = math.pi - 0.25 - 0.12 * math.sin(t * 4 + wag) * (0.4 + ck)
    pts = []
    for i in range(22):
        pts.append((px, py))
        ang += (0.03 + 0.24 * ck) * (1 if i > 2 else 0.3)  # positive turn = toward up then forward (over the back)
        px += math.cos(ang) * 14; py += math.sin(ang) * 14
    for i, (qx, qy) in enumerate(pts):
        r = 30 * (0.55 + 0.7 * math.sin((i + 2) / 23 * math.pi))
        d.circ(*S(qx, qy), r * s, fill=A(CREAM if i > 17 else fur, a))
    # far legs (darker) then body then near legs
    for lx, ph in ((-95, 1.7), (75, 0.2)):
        sw = 7 * math.sin(t * 6 + ph) * bob
        R(d, *S(lx - 13 + sw, 30 + by), *S(lx + 13 + sw, 145), fill=A(furd, a), r=12 * s)
    d.ell(*S(0, 10 + by), 170 * s, 80 * s, A(fur, a))
    d.ell(*S(105, 32 + by), 72 * s, 56 * s, A(CREAM, a))
    for lx, ph in ((-120, 0.0), (55, 1.4)):
        sw = 7 * math.sin(t * 6 + ph) * bob
        R(d, *S(lx - 14 + sw, 40 + by), *S(lx + 14 + sw, 150), fill=A(fur, a), r=12 * s)
    hx, hy = 168, -72 + by
    L = lerp_(125, 72, sk)
    # ears (behind head = far ear, front = near ear). droop: tip moves forward/down along an arc OUTSIDE the head, inner colour fades.
    def ear(ex, sz, c, inner):
        bx, byy = hx + ex, hy - 50
        th = -math.radians(160) * ek
        P0 = [(-32 * sz, 6), (0, -108 * sz * (1 - 0.15 * ek)), (32 * sz, 6)]
        P1 = [(-14 * sz, 0), (0, -74 * sz), (14 * sz, 0)]
        rp = lambda p: S(*rot(bx + p[0], byy + p[1], bx, byy, th))
        d.poly([rp(p) for p in P0], A(mix(c, (40, 46, 70), 0.75 * ek) if inner else c, a))
        if inner: d.poly([rp(p) for p in P1], A(PINK, 0.65 * a * (1 - ek)))
    ear(-42, 1.0, furd, False)
    d.poly([S(hx - 25, hy - 58), S(hx + L, hy + 20), S(hx - 15, hy + 60)], A(fur, a))
    d.circ(*S(hx, hy), 76 * s, fill=A(fur, a))
    d.poly([S(hx + 8, hy + 22), S(hx + L, hy + 20), S(hx + 8, hy + 60)], A(CREAM, a))
    d.circ(*S(hx + L - 2, hy + 18), 15 * s, fill=A(NOSE, a))
    ear(8, 0.95, fur, True)
    ex_, ey_ = hx + 32, hy - 8
    if mood == "angry":
        d.ell(*S(ex_, ey_), 15 * s, 10 * s, A(GOLD, a)); d.ell(*S(ex_ + 3, ey_), 5 * s, 9 * s, A(NOSE, a))
        d.line([S(ex_ - 24, ey_ - 28), S(ex_ + 22, ey_ - 12)], A(NOSE, a), 7 * s)
        mx = hx + 8 + (L - 8) * 0.45; my = hy + 44
        d.poly([S(mx - 34, my - 6), S(mx + 40, my - 8), S(mx + 30, my + 18), S(mx - 28, my + 18)], A((120, 40, 60), a))
        for j in range(4): d.poly([S(mx - 30 + j * 18, my - 6), S(mx - 22 + j * 18, my + 9), S(mx - 14 + j * 18, my - 6)], A(WHITE, a))
    elif mood == "happy":
        cx_, cy_ = S(ex_, ey_ + 4); d.arc(cx_, cy_, 15 * s, 11 * s, 200, 340, A(NOSE, a), 7 * s)
        d.circ(*S(ex_ - 8, ey_ + 30), 14 * s, fill=A(PINK, 0.5 * a))
        mx = hx + 8 + (L - 8) * 0.5; my = hy + 46
        d.poly([S(mx - 10, my - 2), S(mx + 20, my - 2), S(mx + 6, my + 30)], A((240, 110, 140), a))
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

# ---------------- big cats (哈基米 style, side view; mirrored once via S) ----------------
JAG = (238, 172, 72); JAG_D = (84, 52, 30); TIG = (244, 128, 44); TIG_D = (44, 30, 32); BELLY = (250, 240, 222)
ROS = [(-95, -25), (-60, 10), (-20, -35), (15, 5), (55, -30), (85, 15), (-120, 15), (-35, 35), (40, 40), (100, -10)]
def bigcat(d, x, y, s, t, sp="jag", pose="stand", mood="neutral", a=1.0, flip=1, bob=1.0, cub=False, lick=0.0, flat=0.0, wag=0.0, look_up=0.0):
    fur = JAG if sp == "jag" else TIG; dk = JAG_D if sp == "jag" else TIG_D
    if cub: s = s * 0.62
    hs = 1.3 if cub else 1.0
    S = lambda px, py: (x + flip * px * s, y + py * s)
    by = -4 * math.sin(t * 3) * bob
    def spots(cx0, cy0, rx, ry, top_only=False):
        for (px, py) in ROS:
            qx, qy = cx0 + px * rx / 150, cy0 + py * ry / 70
            if top_only and py > 10: continue
            if sp == "jag":
                d.circ(*S(qx, qy), 13 * s, fill=A(dk, a)); d.circ(*S(qx + 1, qy), 7 * s, fill=A(mix(fur, dk, 0.25), a))
    def stripes(cx0, cy0, rx, ry, up=1):
        if sp != "tig": return
        for i, px in enumerate((-110, -65, -20, 25, 70, 110)):
            qx = cx0 + px * rx / 150; L = ry * (0.9 if i % 2 else 0.65)
            yt = cy0 - up * ry * 0.95
            d.poly([S(qx - 11, yt), S(qx + 11, yt), S(qx + 3, yt + up * L)], A(dk, a))
    if pose == "stand":
        # tail
        px, py = -140.0, -10.0 + by; ang = math.pi + 0.6
        for i in range(16):
            r = 17 if i < 14 else 19
            col = dk if (sp == "tig" and i % 3 == 0) or (sp == "jag" and i > 12) else fur
            d.circ(*S(px, py), r * s, fill=A(col, a))
            ang += 0.13 + 0.06 * math.sin(t * 3 + wag + i * 0.3)
            px += math.cos(ang) * 14; py += math.sin(ang) * 14
        for lx, ph in ((-90, 1.7), (80, 0.2)):
            sw = 6 * math.sin(t * 6 + ph) * bob
            R(d, *S(lx - 16 + sw, 20 + by), *S(lx + 16 + sw, 120), fill=A(mix(fur, (0, 0, 0), 0.22), a), r=14 * s)
        d.ell(*S(0, 0 + by), 155 * s, 72 * s, A(fur, a))
        d.ell(*S(10, 38 + by), 110 * s, 30 * s, A(BELLY, a))
        spots(0, -5 + by, 150, 60, True); stripes(0, by, 150, 70)
        for lx, ph in ((-115, 0.0), (60, 1.4)):
            sw = 6 * math.sin(t * 6 + ph) * bob
            R(d, *S(lx - 17 + sw, 25 + by), *S(lx + 17 + sw, 125), fill=A(fur, a), r=15 * s)
            d.ell(*S(lx + sw + 4, 122), 24 * s, 11 * s, A(BELLY, a))
        hx, hy = 150, -62 + by
    else:  # belly up, legs in the air
        px, py = -150.0, 40.0
        for i in range(14):
            d.circ(*S(px, py), 16 * s, fill=A(fur if i < 12 else dk, a)); px -= 12; py -= 6 * math.sin(t * 5 + i * 0.5)
        d.ell(*S(0, 40), 155 * s, 62 * s, A(fur, a))
        spots(0, 70, 150, 40)
        d.ell(*S(0, 18), 125 * s, 38 * s, A(BELLY, a))
        for i, lx in enumerate((-110, -60, 50, 100)):
            sw = 14 * math.sin(t * 7 + i * 1.3)
            R(d, *S(lx - 15, 15), *S(lx - 15 + sw + 30, -70), fill=A(fur, a), r=14 * s)
            d.circ(*S(lx + sw * 1.0, -72), 20 * s, fill=A(BELLY, a))
        hx, hy = 165, 20
    # head (round, 哈基米 style)
    hr = 72 * hs
    for ex in (-38, 38):  # ears; flat=1 rotates them back (飞机耳)
        bx, byy = hx + ex * hs, hy - hr * 0.72
        th = (-1.25 if ex < 0 else -1.05) * flat
        pts = [(-26 * hs, 8), (0, -48 * hs), (26 * hs, 8)]
        rp = lambda p: S(*rot(bx + p[0], byy + p[1], bx, byy, th))
        d.poly([rp(p) for p in pts], A(fur, a))
        d.poly([rp((p[0] * 0.5, p[1] * 0.55 + 4)) for p in pts], A(dk if sp == "tig" else (190, 110, 90), a))
    d.circ(*S(hx, hy), hr * s, fill=A(fur, a))
    d.ell(*S(hx + 30 * hs, hy + 30 * hs), 44 * hs * s, 30 * hs * s, A(BELLY, a))
    if sp == "tig":
        for j in (-1, 0, 1): d.poly([S(hx + j * 18 - 7, hy - hr + 4), S(hx + j * 18 + 7, hy - hr + 4), S(hx + j * 18, hy - hr + 34)], A(dk, a))
        d.poly([S(hx - hr + 2, hy - 8), S(hx - hr + 2, hy + 10), S(hx - hr + 34, hy + 1)], A(dk, a))
    elif not cub:
        for (qx, qy) in ((-30, -40), (-46, -10), (-10, -52)): d.circ(*S(hx + qx, hy + qy), 7 * s, fill=A(dk, a))
    ex_, ey_ = hx + 26 * hs, hy - 12 * hs - look_up * 6
    if mood in ("hiss", "angry"):
        d.ell(*S(ex_, ey_), 15 * s * hs, 9 * s * hs, A((250, 230, 120), a)); d.ell(*S(ex_ + 2, ey_), 4 * s * hs, 8 * s * hs, A(NOSE, a))
        d.line([S(ex_ - 20, ey_ - 24), S(ex_ + 16, ey_ - 10)], A(NOSE, a), 6 * s)
    elif mood == "happy":
        cx_, cy_ = S(ex_, ey_ + 4); d.arc(cx_, cy_, 13 * s * hs, 10 * s * hs, 200, 340, A(NOSE, a), 6 * s)
        d.circ(*S(ex_ - 6, ey_ + 30), 13 * s, fill=A(PINK, 0.55 * a))
    else:
        d.circ(*S(ex_, ey_), 12 * s * hs, fill=A(NOSE, a)); d.circ(*S(ex_ + 3, ey_ - 4), 4 * s * hs, fill=A(WHITE, a))
    nx, ny = hx + 64 * hs, hy + 14 * hs
    d.poly([S(nx - 8, ny - 6), S(nx + 6, ny - 6), S(nx - 1, ny + 5)], A((230, 120, 130), a))
    if mood == "hiss":
        d.poly([S(nx - 26, ny + 16), S(nx + 6, ny + 14), S(nx, ny + 44), S(nx - 22, ny + 40)], A((110, 30, 50), a))
        d.poly([S(nx - 20, ny + 16), S(nx - 14, ny + 30), S(nx - 9, ny + 16)], A(WHITE, a)); d.poly([S(nx - 4, ny + 15), S(nx + 0, ny + 28), S(nx + 4, ny + 15)], A(WHITE, a))
    else:
        d.line([S(nx - 1, ny + 5), S(nx - 6, ny + 14), S(nx - 14, ny + 12)], A(NOSE, a), 4 * s)
    if lick > 0:
        d.ell(*S(nx + 6 + 14 * lick, ny + 20), (10 + 12 * lick) * s, 9 * s, A((240, 110, 140), a))
    for k in (-1, 1):
        d.line([S(nx - 18, ny + 6), S(nx + 30, ny + 6 + k * 12)], A(WHITE, 0.7 * a), 3 * s)
    return S(hx, hy)

# ---------------- elephant seal & whales (side view, one mirror via S, optional tilt) ----------------
SEAL = (150, 132, 118); SEAL_D = (104, 90, 82); SEAL_L = (196, 182, 168)
def _xf(x, y, s, flip, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    return lambda px, py: (x + flip * (px * ca - py * sa) * s, y + (px * sa + py * ca) * s)
def _ellp(S, cx, cy, rx, ry, n=36, a0=0, a1=2 * math.pi):
    return [S(cx + rx * math.cos(a0 + (a1 - a0) * i / n), cy + ry * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
def seal(d, x, y, s, t, a=1.0, flip=1, ang=0.0, mood="neutral", tag=True, rec=True, phones=False, swim=0.0, zz=False):
    S = _xf(x, y, s, flip, ang)
    sw = math.sin(t * 7) * swim
    # rear flippers
    d.poly([S(-150, -5), S(-215, -45 + 20 * sw), S(-205, 0), S(-215, 40 - 20 * sw)], A(SEAL_D, a))
    # body: chubby teardrop
    pts = [S(px, py) for px, py in [(-160 + 300 * (i / 40), 0) for i in range(1)]]
    body = []
    for i in range(48):
        u = i / 48 * 2 * math.pi; cx_ = math.cos(u); sy = math.sin(u)
        rx = 165; ry = 78 * (0.75 + 0.25 * cx_)
        body.append(S(cx_ * rx, sy * ry))
    d.poly(body, A(SEAL, a))
    d.poly(_ellp(S, 10, 34, 120, 28, 30, 0.1, math.pi - 0.1), A(SEAL_L, a))
    for qx, qy in ((-60, -30), (-10, -50), (40, -35), (-100, -10)): d.poly(_ellp(S, qx, qy, 9, 6, 10), A(SEAL_D, 0.6 * a))
    # fore flipper
    fa = 0.5 + 0.35 * sw
    d.poly([S(35, 40), S(35 - 70 * math.cos(fa), 40 + 70 * math.sin(fa) + 10), S(70, 50)], A(SEAL_D, a))
    # head
    hx, hy = 150, -18
    d.poly(_ellp(S, hx, hy, 70, 60, 30), A(SEAL, a))
    d.poly(_ellp(S, hx + 52, hy + 14, 30, 22, 20), A(SEAL_L, a))
    d.poly(_ellp(S, hx + 72, hy + 4, 9, 7, 10), A(NOSE, a))
    if mood == "sleep":
        for ex in (hx + 18,): d.line([S(ex - 14, hy - 12), S(ex, hy - 6), S(ex + 14, hy - 12)], A(NOSE, a), 5 * s)
    else:
        for ex in (hx + 20,):
            d.poly(_ellp(S, ex, hy - 12, 16, 18, 16), A(NOSE, a)); d.poly(_ellp(S, ex + 5, hy - 19, 5, 5, 8), A(WHITE, a))
    if mood == "happy": d.poly(_ellp(S, hx + 10, hy + 18, 11, 7, 10), A(PINK, 0.6 * a))
    for k in (-1, 0, 1): d.line([S(hx + 60, hy + 20), S(hx + 105, hy + 16 + k * 12)], A(WHITE, 0.75 * a), 3 * s)
    if tag:
        tx, ty = hx - 10, hy - 62
        d.poly([S(tx - 34, ty - 14), S(tx + 30, ty - 14), S(tx + 30, ty + 16), S(tx - 34, ty + 16)], A((40, 46, 60), a))
        d.line([S(tx - 20, ty - 14), S(tx - 30, ty - 52)], A((40, 46, 60), a), 5 * s)
        if rec and int(t * 2.5) % 2 == 0:
            p = S(tx + 14, ty); d.circ(p[0], p[1], 9 * s, fill=A((255, 70, 70), a)); glow(d, p[0], p[1], 22 * s, (255, 70, 70), 0.5 * a)
    if phones:
        d.line(_ellp(S, hx - 5, hy - 10, 66, 70, 20, math.pi * 1.05, math.pi * 1.95), A((255, 90, 140), a), 12 * s)
        d.poly(_ellp(S, hx - 10, hy + 2, 18, 26, 12), A((255, 90, 140), a))
    if zz: d.text(*S(hx + 40, hy - 120 - 10 * math.sin(t * 2)), "Zz", int(56 * s), A(WHITE, 0.85 * a), k=1)
    return S(hx, hy)
WHC = {"blue": ((110, 150, 200), (70, 100, 150)), "hump": ((60, 66, 84), (220, 225, 235)), "sperm": ((96, 100, 118), (70, 72, 88)), "dolph": ((140, 160, 185), (225, 232, 240))}
def whale(d, x, y, s, t, kind="blue", a=1.0, flip=1, sing=False):
    c1, c2 = WHC[kind]; S = _xf(x, y, s, flip, 0.04 * math.sin(t * 1.5))
    L = {"blue": 300, "hump": 230, "sperm": 240, "dolph": 150}[kind]; Hh = {"blue": 62, "hump": 82, "sperm": 80, "dolph": 42}[kind]
    tw = 14 * math.sin(t * 2.4)
    d.poly([S(-L + 10, 0), S(-L - 75, -26 + tw), S(-L - 50, tw * 0.6), S(-L - 75, 22 + tw)], A(c1, a))
    body = []
    for i in range(41):
        u = i / 40; xx = -L + 2 * L * u
        if kind == "sperm": th = Hh * (min(1, (u / 0.35) ** 0.6) if u < 0.35 else 1.0)
        else: th = Hh * math.sin(math.pi * min(1, (u * 0.85 + 0.05))) ** 0.7
        body.append(S(xx, -th))
    for i in range(41):
        u = 1 - i / 40; xx = -L + 2 * L * u
        th = Hh * (0.9 if kind == "sperm" and u > 0.35 else math.sin(math.pi * min(1, (u * 0.85 + 0.05))) ** 0.7)
        body.append(S(xx, th))
    d.poly(body, A(c1, a))
    d.poly(_ellp(S, L * 0.1, Hh * 0.35, L * 0.75, Hh * 0.45, 24, 0.05, math.pi - 0.05), A(mix(c1, WHITE, 0.35), a))
    if kind == "hump":
        d.poly([S(L * 0.35, Hh * 0.5), S(L * 0.25 - 40, Hh * 0.5 + 150), S(L * 0.15, Hh * 0.6)], A(c2, a))
    elif kind == "dolph":
        d.poly([S(L, 0), S(L + 45, 6), S(L, 14)], A(c1, a)); d.poly(_ellp(S, L * 0.1, Hh * 0.45, L * 0.7, Hh * 0.35, 20, 0, math.pi), A(c2, a))
    else:
        for j in range(4): d.line([S(L * 0.45, 10 + j * 9), S(L * 0.9, 6 + j * 8)], A(c2, a), 3 * s)
    if kind != "sperm": d.poly([S(-L * 0.35, -Hh * 0.8), S(-L * 0.45, -Hh * 0.8 - 30), S(-L * 0.55, -Hh * 0.75)], A(c1, a))
    ex = L * (0.72 if kind != "sperm" else 0.55)
    d.poly(_ellp(S, ex, -4, 8, 8, 10), A(NOSE, a)); d.poly(_ellp(S, ex + 3, -7, 3, 3, 6), A(WHITE, a))
    if sing:
        for j in range(3):
            u = ((t * 0.9) + j / 3) % 1
            p = S(L + 30 + u * 220, -10); d.arc(p[0], p[1], 40 * u * s + 10, 70 * u * s + 10, -50 if flip > 0 else 130, 50 if flip > 0 else 230, A(WHITE, 0.8 * (1 - u) * a), 5)

# ---------------- liverwort ----------------
LW = (92, 186, 96); LW_D = (56, 140, 70); LW_L = (150, 220, 140); STALK = (196, 150, 90); UMB = (120, 196, 110)
def thallus(d, x, y, s, t, a=1.0, n=5):
    for i in range(n):
        ang = -math.pi * 0.95 + math.pi * 0.9 * i / (n - 1); L = 190 * s
        cx_, cy_ = x + math.cos(ang) * L * 0.55, y + math.sin(ang) * L * 0.18 + 10 * s
        pts = []
        for j in range(25):
            u = j / 24 * 2 * math.pi
            px, py = math.cos(u) * L * 0.6, math.sin(u) * L * 0.22
            ca, sa = math.cos(ang * 0.25), math.sin(ang * 0.25)
            pts.append((cx_ + px * ca - py * sa, cy_ + px * sa + py * ca))
        d.poly(pts, A(LW if i % 2 else LW_D, a))
        d.line([(x, y + 10 * s), (cx_ + math.cos(ang) * L * 0.4, cy_)], A(LW_L, 0.6 * a), 4 * s)
def umbrella(d, x, y, s, t, h=300, a=1.0, face="neutral", water=0.0, wet_t=None, structs=0.0):
    """female archegoniophore: stalk from (x,y) up h, star-rayed head; water = fraction of stalk with climbing water"""
    top = y - h * s
    d.rect(x - 9 * s, top, x + 9 * s, y, fill=A(STALK, a), r=6 * s)
    if structs > 0:  # surface micro-structures: little ridges + hairs
        for j in range(int(h / 22)):
            yy = y - 10 * s - j * 22 * s
            d.line([(x - 9 * s, yy), (x - 20 * s, yy - 8 * s)], A(LW_D, a * structs), 3 * s)
            d.line([(x + 9 * s, yy - 11 * s), (x + 20 * s, yy - 19 * s)], A(LW_D, a * structs), 3 * s)
    if water > 0:
        wy = y - h * s * min(1, water)
        d.rect(x - 13 * s, wy, x + 13 * s, y, fill=A((90, 180, 255), 0.75 * a), r=8 * s)
        for j in range(4):
            u = ((t * 0.8 + j / 4) % 1)
            if u < water: d.circ(x + (12 if j % 2 else -12) * s, y - h * s * u, 8 * s, fill=A((170, 220, 255), a))
    # head: 9 rays
    for i in range(9):
        ang = math.pi * (1.05 + 0.9 * i / 8)
        ex, ey = x + math.cos(ang) * 90 * s, top + 20 * s + math.sin(ang) * 30 * s + 40 * s
        d.line([(x, top + 6 * s), (ex, ey)], A(UMB, a), 22 * s); d.circ(ex, ey, 13 * s, fill=A(UMB, a))
    d.ell(x, top - 4 * s, 62 * s, 34 * s, A(LW, a))
    d.ell(x - 14 * s, top - 18 * s, 20 * s, 9 * s, A(LW_L, 0.8 * a))
    if face:
        for ex in (-18, 18):
            if face == "sleep": d.line([(x + ex * s - 7 * s, top - 4 * s), (x + ex * s + 7 * s, top - 4 * s)], A(NOSE, a), 4 * s)
            else:
                d.circ(x + ex * s, top - 4 * s, 7 * s, fill=A(NOSE, a)); d.circ(x + ex * s + 2 * s, top - 7 * s, 2.5 * s, fill=A(WHITE, a))
        if face == "happy": d.arc(x, top + 6 * s, 10 * s, 7 * s, 20, 160, A(NOSE, a), 4 * s)
        elif face == "worry": d.arc(x, top + 16 * s, 10 * s, 6 * s, 200, 340, A(NOSE, a), 4 * s)
    return x, top
def sperm(d, x, y, s, t, a=1.0, goggles=True, ang=0.0, col=(250, 250, 255)):
    ca, sa = math.cos(ang), math.sin(ang)
    R = lambda px, py: (x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s)
    for k in (-1, 1):  # two flagella
        pts = [R(-10 - i * 6, k * (6 + 8 * math.sin(t * 14 + i * 0.6 + k))) for i in range(12)]
        d.line(pts, A(col, 0.9 * a), 3 * s)
    d.poly([R(-14 + 30 * math.cos(u), 13 * math.sin(u)) for u in [j / 20 * 2 * math.pi for j in range(21)]], A(col, a))
    if goggles:
        d.line([R(4, 0), R(24, 0)], A((255, 120, 60), a), 3 * s)
        for gx in (8, 19): p = R(gx, -2); d.circ(p[0], p[1], 5 * s, fill=A((60, 200, 255), a))

# ---------------- crow / human / monkey ----------------
CRW = (46, 52, 78); CRW_L = (90, 110, 170); CRW_H = (140, 170, 240); BEAK = (70, 70, 84)
def crow(d, x, y, s, t, a=1.0, face="neutral", head=0.0, glasses=False, flip=False, name=None, peck=0.0):
    f = -1 if flip else 1
    # tail + body
    d.poly([(x - f * 70 * s, y + 10 * s), (x - f * 150 * s, y + 60 * s), (x - f * 140 * s, y + 80 * s), (x - f * 60 * s, y + 40 * s)], A(CRW, a))
    d.ell(x, y, 95 * s, 70 * s, A(CRW, a))
    d.ell(x - f * 20 * s, y - 10 * s, 60 * s, 34 * s, A(CRW_L, a))           # wing
    d.ell(x - f * 30 * s, y - 22 * s, 30 * s, 10 * s, A(CRW_H, 0.6 * a))     # sheen
    for k in (-20, 20): d.line([(x + k * s, y + 60 * s), (x + k * s, y + 110 * s)], A(BEAK, a), 7 * s)
    # head (rotates by head angle, peck moves forward/down)
    hx, hy = x + f * (70 + 30 * peck) * s, y - 70 * s + 40 * peck * s
    d.circ(hx, hy, 52 * s, fill=A(CRW, a)); d.ell(hx - f * 14 * s, hy - 24 * s, 20 * s, 9 * s, A(CRW_H, 0.5 * a))
    ang = head + (0.5 * peck)
    bx, by = hx + f * 48 * s * math.cos(ang), hy + 48 * s * math.sin(ang)
    tipx, tipy = hx + f * 115 * s * math.cos(ang), hy + 115 * s * math.sin(ang)
    px_, py_ = -math.sin(ang) * 16 * s, math.cos(ang) * 16 * s
    d.poly([(bx - px_, by - py_), (tipx, tipy), (bx + px_, by + py_)], A(BEAK, a))
    d.line([(bx, by), (tipx, tipy)], A((110, 110, 130), a), 2 * s)
    ex, ey = hx + f * 14 * s, hy - 10 * s
    if glasses:
        d.rect(ex - 34 * s, ey - 14 * s, ex + 34 * s, ey + 12 * s, fill=A((20, 20, 30), a), r=10 * s)
        d.line([(ex - 26 * s, ey - 8 * s), (ex - 10 * s, ey - 8 * s)], A((150, 220, 255), a), 3 * s)
    else:
        d.circ(ex, ey, 15 * s, fill=A(WHITE, a)); d.circ(ex + f * 4 * s, ey, 8 * s, fill=A((20, 20, 30), a)); d.circ(ex + f * 7 * s, ey - 4 * s, 3 * s, fill=A(WHITE, a))
        if face == "smug": d.line([(ex - 16 * s, ey - 18 * s), (ex + 16 * s, ey - 24 * s)], A(CRW_H, a), 5 * s)
    pass
SKIN = (250, 205, 170); MONK = (170, 120, 80); MONK_F = (235, 195, 160)
def human(d, x, y, s, t, a=1.0, face="slow", load=0.0):
    d.rect(x - 80 * s, y + 60 * s, x + 80 * s, y + 260 * s, fill=A((90, 140, 230), a), r=40 * s)
    d.circ(x, y, 85 * s, fill=A(SKIN, a)); d.ell(x, y - 70 * s, 85 * s, 35 * s, A((60, 45, 40), a))
    for ex in (-30, 30):
        if face == "slow": d.line([(x + ex * s - 14 * s, y), (x + ex * s + 14 * s, y)], A(NOSE, a), 5 * s)
        else: d.circ(x + ex * s, y, 10 * s, fill=A(NOSE, a))
    if face == "shock": d.circ(x, y + 40 * s, 14 * s, fill=A(NOSE, a))
    else: d.line([(x - 18 * s, y + 40 * s), (x + 18 * s, y + 40 * s)], A(NOSE, a), 5 * s)
    if load > 0:  # loading spinner over head
        for i in range(8):
            u = i / 8 * 2 * math.pi + t * 6
            d.circ(x + math.cos(u) * 40 * s, y - 150 * s + math.sin(u) * 40 * s, 8 * s, fill=A(WHITE, a * load * (0.2 + 0.8 * i / 8)))
def monkey(d, x, y, s, t, a=1.0, face="slow"):
    d.rect(x - 70 * s, y + 60 * s, x + 70 * s, y + 230 * s, fill=A(MONK, a), r=40 * s)
    for ex in (-90, 90): d.circ(x + ex * s, y, 30 * s, fill=A(MONK, a)); d.circ(x + ex * s, y, 16 * s, fill=A(MONK_F, a))
    d.circ(x, y, 80 * s, fill=A(MONK, a)); d.ell(x, y + 15 * s, 60 * s, 52 * s, A(MONK_F, a))
    for ex in (-25, 25):
        if face == "slow": d.line([(x + ex * s - 12 * s, y - 5 * s), (x + ex * s + 12 * s, y - 5 * s)], A(NOSE, a), 5 * s)
        else: d.circ(x + ex * s, y - 5 * s, 9 * s, fill=A(NOSE, a))
    d.arc(x, y + 30 * s, 16 * s, 8 * s, 20, 160, A(NOSE, a), 4 * s)
def dots(d, cx, cy, w, h, t, coh=0.5, dirn=1, n=70, a=1.0, seed=3, col=WHITE):
    rv = random.Random(seed)
    for i in range(n):
        x0, y0 = rv.uniform(0, w), rv.uniform(0, h); ang = rv.uniform(0, 2 * math.pi); coherent = rv.random() < coh
        vx, vy = (dirn * 180, 0) if coherent else (math.cos(ang) * 180, math.sin(ang) * 180)
        x = (x0 + vx * t) % w; y = (y0 + vy * t) % h
        d.circ(cx - w / 2 + x, cy - h / 2 + y, 7, fill=A(col, a))

# ---------------- meteor ----------------
ROCK = (120, 100, 90); ROCK_L = (170, 150, 135); FIRE = (255, 170, 60); FIRE2 = (255, 240, 160); GREENF = (120, 255, 170)
def rock(d, x, y, s, t, a=1.0, face="happy", fire=0.0, ang=-0.85, trail=1.0, green=False):
    if fire > 0:
        L = 520 * s * trail
        for i in range(14, 0, -1):
            u = i / 14
            cx, cy = x + math.cos(ang) * L * u, y + math.sin(ang) * L * u
            col = GREENF if (green and u > 0.3) else (FIRE if u > 0.25 else FIRE2)
            d.circ(cx, cy, (70 - 40 * u) * s, fill=A(col, a * fire * (1 - u) * 0.8))
        d.circ(x, y, 100 * s, fill=A(FIRE2, a * fire * 0.35))
    rv = random.Random(4); pts = []
    for i in range(10):
        u = i / 10 * 2 * math.pi; r = 70 * s * rv.uniform(0.85, 1.1); pts.append((x + math.cos(u) * r, y + math.sin(u) * r))
    d.poly(pts, A(ROCK, a))
    d.circ(x - 22 * s, y - 24 * s, 18 * s, fill=A(ROCK_L, a)); d.circ(x + 30 * s, y + 26 * s, 10 * s, fill=A(ROCK_L, a))
    for ex in (-20, 20):
        if face == "scared": d.circ(x + ex * s, y - 4 * s, 11 * s, fill=A(WHITE, a)); d.circ(x + ex * s, y - 4 * s, 5 * s, fill=A(NOSE, a))
        else: d.circ(x + ex * s, y - 4 * s, 8 * s, fill=A(NOSE, a))
    if face == "scared": d.circ(x, y + 26 * s, 10 * s, fill=A(NOSE, a))
    else: d.arc(x, y + 18 * s, 16 * s, 10 * s, 20, 160, A(NOSE, a), 4 * s)
def plane(d, x, y, s, a=1.0):
    d.ell(x, y, 90 * s, 18 * s, A((235, 238, 245), a))
    d.poly([(x - 10 * s, y), (x - 40 * s, y + 60 * s), (x + 10 * s, y + 60 * s), (x + 30 * s, y)], A((200, 205, 220), a))
    d.poly([(x - 80 * s, y), (x - 95 * s, y - 40 * s), (x - 70 * s, y - 40 * s), (x - 55 * s, y)], A((200, 205, 220), a))
def person(d, x, y, s, t, a=1.0, face="look", cover=0.0):
    d.rect(x - 50 * s, y + 50 * s, x + 50 * s, y + 200 * s, fill=A((90, 140, 230), a), r=30 * s)
    d.circ(x, y, 60 * s, fill=A((250, 205, 170), a)); d.ell(x, y - 48 * s, 60 * s, 24 * s, A((60, 45, 40), a))
    for ex in (-20, 20): d.circ(x + ex * s, y - 4 * s, 8 * s, fill=A(NOSE, a))
    if face == "shock": d.circ(x, y + 28 * s, 11 * s, fill=A(NOSE, a))
    else: d.arc(x, y + 22 * s, 12 * s, 7 * s, 20, 160, A(NOSE, a), 4 * s)
    if cover > 0:
        for ex in (-1, 1): d.circ(x + ex * 62 * s, y, 22 * s * cover, fill=A((250, 205, 170), a))
def mountains(d, col=(30, 40, 70), y0=1450):
    d.poly([(-50, y0), (150, y0 - 260), (330, y0 - 120), (520, y0 - 330), (730, y0 - 140), (900, y0 - 280), (1130, y0 - 80), (1130, 1950), (-50, 1950)], A(col, 1))
def stars(d, t, a=1.0):
    rv = random.Random(11)
    for i in range(60):
        x, y = rv.uniform(0, 1080), rv.uniform(0, 1200); tw = 0.5 + 0.5 * math.sin(t * 2 + i)
        d.circ(x, y, rv.uniform(2, 4), fill=A(WHITE, a * (0.3 + 0.5 * tw)))

# ---------------- penguin ----------------
PBLK = (40, 46, 66); PBEL = (250, 250, 252); PBEAK = (255, 170, 50); ALG_G = (70, 190, 90); ALG_R = (230, 80, 90); SNOW = (238, 244, 252); GUANO = (240, 170, 160)
def penguin(d, x, y, s, t, a=1.0, face="happy", waddle=True, flip=1):
    r = math.sin(t * 9) * 0.08 if waddle else 0
    d.ell(x, y, 110 * s, 150 * s, A(PBLK, a)); d.ell(x + 6 * s * flip, y + 20 * s, 78 * s, 120 * s, A(PBEL, a))
    for ex in (-1, 1): d.ell(x + ex * 110 * s, y + 10 * s + ex * r * 60 * s, 26 * s, 70 * s, A(PBLK, a))
    for ex in (-36, 36): d.ell(x + ex * s, y + 145 * s, 32 * s, 12 * s, A(PBEAK, a))
    for ex in (-28, 28):
        if face == "shock": d.circ(x + ex * s, y - 70 * s, 14 * s, fill=A(WHITE, a)); d.circ(x + ex * s, y - 70 * s, 7 * s, fill=A(NOSE, a))
        elif face == "smug": d.arc(x + ex * s, y - 66 * s, 12 * s, 8 * s, 200, 340, A(WHITE, a), 5 * s)
        else: d.circ(x + ex * s, y - 70 * s, 9 * s, fill=A(WHITE, a)); d.circ(x + ex * s, y - 70 * s, 5 * s, fill=A(NOSE, a))
    d.poly([(x - 18 * s, y - 40 * s), (x + 18 * s, y - 40 * s), (x, y - 14 * s)], A(PBEAK, a))
    d.circ(x - 54 * s, y - 34 * s, 12 * s, fill=A((255, 150, 170), a * 0.6)); d.circ(x + 54 * s, y - 34 * s, 12 * s, fill=A((255, 150, 170), a * 0.6))
def algae(d, x, y, s, t, col=None, a=1.0, face="happy", ph=0.0):
    col = col or ALG_G; b = 1 + 0.06 * math.sin(t * 6 + ph)
    d.circ(x, y, 40 * s * b, fill=A(col, a)); d.circ(x - 12 * s, y - 14 * s, 10 * s, fill=A(WHITE, a * 0.45))
    for ex in (-12, 12): d.circ(x + ex * s, y - 2 * s, 5 * s, fill=A(NOSE, a))
    if face == "eat": d.circ(x, y + 16 * s, 8 * s, fill=A(NOSE, a))
    else: d.arc(x, y + 12 * s, 10 * s, 6 * s, 20, 160, A(NOSE, a), 3 * s)
def snowfield(d, y0=1150, col=SNOW):
    d.rect(0, y0, 1080, 1950, fill=A(col, 1))
    d.ell(300, y0, 420, 50, A(col, 1)); d.ell(820, y0 + 10, 360, 40, A(col, 1))
def sun(d, x, y, s, t, a=1.0):
    for i in range(10):
        u = i / 10 * 2 * math.pi + t * 0.5; d.line([(x + math.cos(u) * 90 * s, y + math.sin(u) * 90 * s), (x + math.cos(u) * 130 * s, y + math.sin(u) * 130 * s)], A((255, 210, 80), a), 10 * s)
    d.circ(x, y, 70 * s, fill=A((255, 220, 90), a))
    for ex in (-22, 22): d.circ(x + ex * s, y - 6 * s, 7 * s, fill=A(NOSE, a))
    d.arc(x, y + 14 * s, 18 * s, 10 * s, 20, 160, A(NOSE, a), 4 * s)
