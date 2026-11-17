import sys, subprocess
from fx import *
from cues import *

FE = (222, 74, 52); FE_D = (160, 44, 40); FE_L = (255, 150, 90); BELLY = (255, 196, 120)
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

# ---------------- characters ----------------
def head(d, hx, hy, r, t, mood="happy", op=0.0, sl=0.0, f=1, a=1.0, ridges=False, xray=False):
    X = lambda u: hx + f * u * r; Y = lambda v: hy + v * r
    if xray:
        c1, c2, c3, cb, cbd = A(XR, 0.18 * a), A(XR, 0.32 * a), A(XR, 0.5 * a), A(XR, 0.55 * a), A(XR, 0.75 * a)
    else:
        c1, c2, c3, cb, cbd = A(CREST_D, a), A(CREST, a), A(FE, a), A(BEAK, a), A(BEAK_D, a)
    # crest (casque)
    d.ell(X(-0.05), Y(-0.85), 0.42 * r, 0.62 * r, c1); d.ell(X(-0.02), Y(-0.8), 0.34 * r, 0.54 * r, c2)
    d.circ(hx, hy, r, fill=c3)
    if not xray: d.ell(X(-0.3), Y(-0.45), 0.3 * r, 0.18 * r, A(FE_L, 0.6 * a))
    # lower jaw (slides forward by sl, opens by op)
    s_ = sl * 0.35
    low = [(X(0.45 + s_), Y(0.22)), (X(1.18 + s_), Y(0.2 + op * 0.3)), (X(1.05 + s_), Y(0.5 + op * 0.25)), (X(0.4 + s_), Y(0.62))]
    d.poly(low, cbd)
    up = [(X(0.5), Y(-0.42)), (X(1.15), Y(-0.3)), (X(1.5), Y(0.02)), (X(1.42), Y(0.36)), (X(1.25), Y(0.18)), (X(0.5), Y(0.22))]
    d.poly(up, cb)
    if ridges:
        for i in range(5):
            u = 0.62 + i * 0.13
            d.line([(X(u), Y(-0.05 + i * 0.012)), (X(u + 0.07), Y(0.18))], A(BEAK_D if not xray else WHITE, a), 0.05 * r)
    if not xray: d.ell(X(0.95), Y(-0.18), 0.22 * r, 0.06 * r, A(WHITE, 0.45 * a))
    ex, ey, er = X(0.08), Y(-0.15), 0.27 * r
    if mood in ("happy", "proud"):
        d.arc(ex, ey + er * 0.4, er, er * 0.9, 200, 340, A(INK, a), er * 0.3)
    elif mood == "chew":
        d.line([(ex - er, ey), (ex + er, ey)], A(INK, a), er * 0.28)
    else:
        big = 1.25 if mood in ("scared", "shock") else 1.0
        if not xray or True: d.circ(ex, ey, er * big, fill=A(WHITE, a))
        lk = 0.45 * f
        d.circ(ex + lk * er, ey + er * 0.05, er * (0.38 if mood == "shock" else 0.55), fill=A(INK, a))
        d.circ(ex + lk * er - er * 0.18, ey - er * 0.2, er * 0.14, fill=A(WHITE, a))
        if mood == "sus": d.line([(ex - er * 1.1, ey - er * 1.2), (ex + er * 1.1, ey - er * 0.8)], A(INK, a), er * 0.3)
    if mood in ("happy", "proud", "chew") and not xray: d.ell(X(-0.3), Y(0.35), 0.18 * r, 0.1 * r, A((255, 120, 140), 0.6 * a))

def chicken(d, x, y, s, t, mood="happy", op=0.0, sl=0.0, f=1, a=1.0, walk=0.0, bob=0.0, neck=1.0, legs=True, fruit=False):
    X = lambda u: x + f * u * s; Y = lambda v: y + v * s
    b = bob * math.sin(t * 9) * 0.05
    d.ell(x, Y(1.95), 0.9 * s, 0.13 * s, A((0, 0, 0), 0.22 * a))
    if legs:
        for j, ph_ in enumerate((0, math.pi)):
            sw = math.sin(t * 10 + ph_) * 0.35 * walk
            kx, ky = X(0.05 + sw * 0.6 + j * 0.15), Y(1.05)
            fx_, fy_ = X(-0.05 + sw + j * 0.15), Y(1.9 - max(0, math.cos(t * 10 + ph_)) * 0.18 * walk)
            d.line([(X(j * 0.15), Y(0.3)), (kx, ky), (fx_, fy_)], A(LEGC if j == 0 else mix(LEGC, (0, 0, 0), 0.2), a), 0.13 * s)
            for dx in (-0.15, 0.12, 0.3): d.line([(fx_, fy_), (fx_ + f * dx * s, fy_ + 0.05 * s)], A(LEGC, a), 0.07 * s)
    # tail fan
    for i in range(5):
        ang = math.radians(150 + i * 12 + 4 * math.sin(t * 3 + i)); L = 1.5 - abs(i - 2) * 0.12
        tx, ty = X(-0.7) + f * math.cos(ang) * L * s, Y(-0.1 + b) - math.sin(ang) * L * s * 0.8
        col = [FE_D, FE, CREST_D, FE, FE_D][i]
        d.poly([(X(-0.6), Y(-0.25 + b)), (tx, ty - 0.12 * s), (tx - f * 0.05 * s, ty + 0.14 * s), (X(-0.6), Y(0.1 + b))], A(col, a))
    d.ell(x, Y(b), 1.0 * s, 0.78 * s, A(FE, a))
    d.ell(X(0.2), Y(0.25 + b), 0.62 * s, 0.45 * s, A(BELLY, a))
    d.ell(X(-0.35), Y(-0.3 + b), 0.35 * s, 0.18 * s, A(FE_L, 0.55 * a))
    # folded feathered wing on the upper back
    wb = 0.06 * math.sin(t * 5)
    for j in range(3): d.poly([(X(0.15), Y(-0.45 + b)), (X(-0.75 - j * 0.12), Y(-0.05 + j * 0.12 + b + wb)), (X(-0.2), Y(0.05 + j * 0.06 + b))], A(mix(FE_D, FE, j * 0.3), a))
    d.ell(X(-0.05), Y(-0.3 + b), 0.4 * s, 0.2 * s, A(FE_D, a))
    if fruit: peach(d, X(0.85), Y(0.25 + b), 0.32 * s, a)
    hx, hy = X(0.75 + 0.15 * neck), Y(-1.55 * neck + b + 0.04 * math.sin(t * 4))
    d.line([(X(0.45), Y(-0.35 + b)), (lerp(X(0.45), hx, 0.5) + f * 0.12 * s, lerp(Y(-0.35 + b), hy, 0.5)), (hx, hy)], A(FE, a), 0.42 * s)
    head(d, hx, hy, 0.48 * s, t, mood, op, sl, f, a)
    return hx, hy

def peach(d, x, y, r, a=1.0, bite=0.0, cut=False):
    d.circ(x, y, r, fill=A(PEACH_D, a)); d.circ(x - r * 0.06, y - r * 0.05, r * 0.94, fill=A(PEACH, a))
    d.ell(x - r * 0.35, y - r * 0.35, r * 0.3, r * 0.2, A(PEACH_L, 0.8 * a))
    d.arc(x + r * 0.15, y, r * 0.6, r * 0.95, 250, 300, A(PEACH_D, a), r * 0.08)
    d.ell(x + r * 0.3, y - r * 1.0, r * 0.35, r * 0.15, A(LEAFC, a))
    if cut:
        d.circ(x, y, r * 0.75, fill=A((255, 226, 150), a)); d.ell(x, y, r * 0.32, r * 0.42, A(PIT, a))
        for i in range(4): d.line([(x - r * 0.2, y - r * 0.25 + i * r * 0.15), (x + r * 0.2, y - r * 0.2 + i * r * 0.15)], A(mix(PIT, (0, 0, 0), 0.3), a), r * 0.04)
    if bite > 0: d.circ(x + r * 0.85, y - r * 0.5, r * 0.45 * bite, fill=A((255, 226, 150), a))
def cherry(d, x, y, r, a=1.0):
    for dx in (-0.8, 0.8):
        d.line([(x + dx * r, y - r * 0.6), (x, y - r * 2.6)], A((90, 140, 60), a), r * 0.15)
        d.circ(x + dx * r, y, r, fill=A((200, 30, 50), a)); d.circ(x + dx * r - r * 0.3, y - r * 0.35, r * 0.25, fill=A(WHITE, 0.5 * a))
def berries(d, x, y, r, a=1.0, col=(90, 80, 200)):
    for i, (dx, dy) in enumerate([(0, 0), (-1.6, 0.6), (1.6, 0.6), (-0.8, 1.9), (0.8, 1.9), (0, -1.6)]):
        d.circ(x + dx * r, y + dy * r, r, fill=A(mix(col, (0, 0, 0), 0.15 * (i % 2)), a)); d.circ(x + dx * r - r * 0.3, y + dy * r - r * 0.3, r * 0.25, fill=A(WHITE, 0.5 * a))

def trex(d, x, y, s, t, op=0.0, f=1, a=1.0, mood="sus"):
    X = lambda u: x + f * u * s; Y = lambda v: y + v * s
    d.poly([(X(-1.6), Y(0.2)), (X(-0.2), Y(-0.6)), (X(1.3), Y(-0.55)), (X(1.65), Y(-0.2)), (X(1.6), Y(0.15)), (X(0.3), Y(0.35)), (X(-1.6), Y(0.9))], A(TRX, a))
    d.poly([(X(0.2), Y(0.3)), (X(1.5), Y(0.18 + op * 0.4)), (X(1.4), Y(0.5 + op * 0.5)), (X(0.0), Y(0.75)), (X(-1.6), Y(1.1)), (X(-1.6), Y(0.75))], A(TRX_D, a))
    for i in range(6):
        u = 0.45 + i * 0.18
        d.poly([(X(u), Y(0.24)), (X(u + 0.05), Y(0.38)), (X(u + 0.1), Y(0.24))], A(WHITE, a))
    d.ell(X(0.3), Y(-0.25), 0.18 * s, 0.13 * s, A(WHITE, a)); d.circ(X(0.35), Y(-0.24), 0.07 * s, fill=A(INK, a))
    d.line([(X(0.1), Y(-0.45)), (X(0.5), Y(-0.38))], A(TRX_D, a), 0.08 * s)
    d.ell(X(1.2), Y(-0.38), 0.08 * s, 0.04 * s, A(TRX_D, a)); d.ell(X(-0.5), Y(-0.2), 0.5 * s, 0.12 * s, A(TRX_L, 0.4 * a))

def turkey(d, x, y, s, t, a=1.0):
    for i in range(7):
        ang = math.radians(100 + i * 23)
        d.ell(x - 0.2 * s + math.cos(ang) * 0.9 * s, y - 0.3 * s - math.sin(ang) * 0.8 * s, 0.35 * s, 0.35 * s, A([TURK_D, (190, 130, 70), TURK][i % 3], a))
    d.ell(x, y, 0.75 * s, 0.6 * s, A(TURK, a))
    for j in (0, 1): d.line([(x - 0.15 * s + j * 0.3 * s, y + 0.5 * s), (x - 0.15 * s + j * 0.3 * s, y + 1.1 * s)], A(LEGC, a), 0.08 * s)
    d.line([(x + 0.4 * s, y - 0.2 * s), (x + 0.65 * s, y - 0.75 * s)], A((150, 110, 100), a), 0.18 * s)
    d.circ(x + 0.68 * s, y - 0.85 * s, 0.17 * s, fill=A((170, 130, 120), a)); d.circ(x + 0.72 * s, y - 0.88 * s, 0.04 * s, fill=A(INK, a))
    d.ell(x + 0.75 * s, y - 0.68 * s, 0.07 * s, 0.14 * s, A((230, 40, 50), a)); d.poly([(x + 0.82 * s, y - 0.86 * s), (x + 0.95 * s, y - 0.8 * s), (x + 0.82 * s, y - 0.76 * s)], A(BEAK, a))

def parrot(d, x, y, r, a=1.0):
    d.circ(x, y + r * 1.0, r * 0.9, fill=A((60, 70, 80), a)); d.circ(x, y, r, fill=A((60, 70, 80), a))
    d.circ(x - r * 0.1, y - r * 0.05, r * 0.85, fill=A((90, 100, 120), a))
    d.poly([(x + r * 0.5, y - r * 0.4), (x + r * 1.25, y - r * 0.1), (x + r * 1.1, y + r * 0.55), (x + r * 0.8, y + r * 0.2), (x + r * 0.5, y + r * 0.3)], A((240, 200, 160), a))
    d.circ(x + r * 0.1, y - r * 0.2, r * 0.2, fill=A(WHITE, a)); d.circ(x + r * 0.15, y - r * 0.2, r * 0.1, fill=A(INK, a))
    d.ell(x - r * 0.2, y + r * 1.1, r * 0.6, r * 0.5, A((210, 60, 50), a))
def turtle(d, x, y, r, t, a=1.0):
    for dx in (-0.8, 0.8): d.ell(x + dx * r, y + r * 0.45, r * 0.4, r * 0.18, A((120, 190, 120), a))
    d.ell(x + r * 1.2, y + r * 0.05, r * 0.32, r * 0.26, A((120, 190, 120), a)); d.circ(x + r * 1.3, y - r * 0.02, r * 0.06, fill=A(INK, a))
    d.d.chord((P(x - r), P(y - r * 0.8), P(x + r), P(y + r * 0.8)), 180, 360, fill=A((60, 130, 80), a))
    for i in range(3): d.circ(x - r * 0.5 + i * r * 0.5, y - r * 0.35, r * 0.18, fill=A((90, 160, 100), a))
    d.rect(x - r, y - 2, x + r, y + r * 0.12, fill=A((150, 200, 140), a))

def plants(d, t, y0, col=(46, 110, 70), col2=(70, 150, 80), a=1.0, fruitc=PEACH):
    for i in range(7):
        x = -40 + i * 190 + (i % 2) * 40; h = 260 + (i * 97) % 180
        sw = 8 * math.sin(t * 1.5 + i)
        for k in range(5):
            ang = -math.pi / 2 + (k - 2) * 0.5
            d.poly([(x, y0), (x + math.cos(ang) * h + sw, y0 + math.sin(ang) * h * 0.8), (x + math.cos(ang) * h * 0.6 + 30 + sw, y0 + math.sin(ang) * h * 0.5)], A(col if k % 2 else col2, a))
        if i % 2: d.circ(x + 30 + sw, y0 - h * 0.45, 22, fill=A(fruitc, a))
def ground(d, y0, col, col2):
    d.rect(-50, y0, OW + 50, OH + 50, fill=A(col, 1)); d.rect(-50, y0, OW + 50, y0 + 20, fill=A(col2, 1))
def volcano(d, x, y, s, t, a=1.0):
    d.poly([(x - s, y), (x - s * 0.18, y - s * 0.8), (x + s * 0.18, y - s * 0.8), (x + s, y)], A((120, 50, 60), a))
    d.poly([(x - s * 0.18, y - s * 0.8), (x - s * 0.08, y - s * 0.55), (x + s * 0.05, y - s * 0.65), (x + s * 0.18, y - s * 0.8)], A((255, 140, 50), a))
    for i in range(5):
        u = (t * 0.3 + i / 5) % 1
        d.circ(x + 30 * math.sin(i * 2 + t), y - s * 0.85 - u * 260, 30 + u * 60, fill=A((90, 60, 70), 0.35 * a * (1 - u)))

# ---------------- scenes ----------------
def s_hook(t, d):
    grad(d, (255, 110, 70), (150, 40, 60)); glow(d, 540, 760, 360, (255, 220, 120), 0.8)
    volcano(d, 820, 1040, 360, t, 0.9)
    trex(d, 180, 860, 170, t, 0.15 * (1 + math.sin(t * 2)), 1, 0.45)
    plants(d, t, 1120, (110, 40, 60), (150, 60, 70), 1.0)
    ground(d, 1100, (120, 46, 54), (160, 70, 70))
    frz = t >= HOOK_STOP; tt = min(t, HOOK_STOP)
    u = ease(pr(tt, -0.3, HOOK_HIT))
    cx = lerp(1250, 600, u); cy = 900 - 160 * math.sin(math.pi * min(1, u)) * (1 - pr(tt, HOOK_HIT, HOOK_HIT + 0.01))
    chomp = pulse(tt, [HOOK_HIT, qb(1), qb(2), qb(3)], 9)
    hx, hy = chicken(d, cx, cy, 120, tt, "shock" if frz else ("happy" if tt > HOOK_HIT else "sus"), op=0.6 * (1 - chomp) if tt < HOOK_HIT else 0.5 * chomp, f=-1, walk=1 - pr(tt, HOOK_HIT - 0.1, HOOK_HIT), bob=1)
    if tt < HOOK_HIT + 0.05: peach(d, 380, 760 + 20 * math.sin(t * 6), 70, 1)
    else: peach(d, hx - 95, hy + 30, 46, 1, bite=min(1, pr(tt, HOOK_HIT, qb(3)) * 1.5))
    if t >= HOOK_HIT:
        sparks(d, hx - 90, hy + 20, t, HOOK_HIT, 36, 900, (255, 210, 140), 1, 4, 0.9)
        for h in (qb(1), qb(2), qb(3)): sparks(d, hx - 90, hy + 20, t, h, 12, 500, (255, 180, 120), 0.8, int(h * 10), 0.5)
    k = back(pr(t, -0.2, HOOK_HIT)); k2 = pulse(t, [HOOK_HIT], 6)
    if k > 0: d.text(540, 360, "恐龙吃水果？", int(118 * (0.6 + 0.4 * k) * (1 + 0.08 * k2)), A(YEL, 1), k=1)
    tag(d, 540, 500, "6600 万年前 · 真实化石", WHITE, popk(t, qb(1.5)), 34)
    if frz:
        glow(d, hx + 40, hy - 40, 120, WHITE, pr(t, HOOK_STOP, HOOKCUT))

def s_name(t, d):
    rays(d, t, (120, 60, 170), (90, 40, 140)); glow(d, 540, 900, 400, (255, 160, 220), 0.4)
    ground(d, 1230, (70, 30, 100), (110, 60, 140))
    hx, hy = chicken(d, 470, 1000, 130, t, "proud" if t >= T["name"] else "chew", op=0.25 * (0.5 + 0.5 * math.sin(t * 16)) if t < T["name"] else 0.0, f=1, bob=1, fruit=t < T["name"])
    if t < T["name"]:
        title(d, t, HOOKCUT, "6600 万年前", 330, 110, YEL)
    else:
        stamp(d, t, T["name"], "地狱鸡", 540, 320, 170, YEL)
        k = pr(t, T["name"] + 0.1, T["name"] + 0.6); s = "Infernogallus"; n = int(len(s) * k + 0.999)
        d.text(540, 480, s[:n], 58, A(WHITE, 1), k=1)
        tag(d, 360, 590, "Inferno = 地狱", (255, 120, 80), popk(t, at("name", 1.5)), 34, WHITE)
        tag(d, 730, 590, "gallus = 鸡", GOLD, popk(t, at("name", 2.5)), 34)
        for i in range(4):
            u = (t * 1.2 + i / 4) % 1
            d.circ(260 + i * 180, 1220 - u * 300, 18 * (1 - u), fill=A((255, 150, 60), 0.6 * (1 - u)))

def s_site(t, d):
    grad(d, (40, 150, 160), (20, 80, 100))
    title(d, t, T["site"], "化石产地", 300, 96)
    k1 = popk(t, at("site", 0)); k2 = popk(t, at("site", 0.5))
    for (x0, lab, k, c) in ((190, "蒙大拿", k1, (120, 200, 150)), (560, "北达科他", k2, (150, 210, 120))):
        if k > 0:
            d.rect(x0, 420 + 30 * (1 - k), x0 + 330, 640 + 30 * (1 - k), fill=A(c, k), r=26)
            d.text(x0 + 165, 530, lab, 46, A(NAVYT, k), k=1)
    tag(d, 540, 690, "美国", WHITE, popk(t, at("site", 1)), 32)
    pk = ease(pr(t, at("site", 1), at("site", 1.6)))
    if pk > 0:
        py = lerp(250, 560, pk)
        d.circ(530, py - 40, 34, fill=A(BAD, 1)); d.poly([(500, py - 30), (530, py + 10), (560, py - 30)], A(BAD, 1)); d.circ(530, py - 40, 13, fill=A(WHITE, 1))
    layers = [(170, 120, 90), (196, 150, 104), (140, 70, 60), (210, 170, 120), (150, 110, 90)]
    for i, c in enumerate(layers):
        y0 = 800 + i * 110; hot = i == 2
        d.rect(180, y0, 900, y0 + 110, fill=A(mix(c, (255, 110, 60), 0.5 * pulse(t, [at("site", 2.5)], 2) if hot else 0), 1), r=6 if i in (0, 4) else 0)
    hk = popk(t, at("site", 2.5))
    if hk > 0:
        for i in range(6): d.circ(260 + i * 115, 1020 + 8 * math.sin(t * 6 + i), 20, fill=A((255, 170, 60), 0.7 * hk))
        tag(d, 540, 1075, "“地狱溪”地层 Hell Creek", (255, 120, 60), hk, 34, WHITE)
        for i, (bx, by) in enumerate(((300, 1250), (700, 1250))):
            d.line([(bx - 40, by), (bx + 40, by)], A(BONE, hk), 14); d.circ(bx - 44, by - 8, 10, fill=A(BONE, hk)); d.circ(bx - 44, by + 8, 10, fill=A(BONE, hk)); d.circ(bx + 44, by - 8, 10, fill=A(BONE, hk)); d.circ(bx + 44, by + 8, 10, fill=A(BONE, hk))

def s_size(t, d):
    grad(d, (255, 220, 100), (240, 170, 60))
    for i in range(8): d.line([(180, 700 + i * 80), (900, 700 + i * 80)], A(WHITE, 0.25), 3)
    ground(d, 1200, (210, 140, 60), (230, 170, 80))
    title(d, t, T["size"], "有多大？", 300, 100, NAVYT)
    chicken(d, 380, 920, 110, t, "happy", f=1, bob=1)
    tk = popk(t, at("size", 1))
    if tk > 0: turkey(d, 780, 1040, 120 * tk, t)
    tag(d, 780, 830, "火鸡", WHITE, tk, 32)
    k = ease(pr(t, at("size", 0.5), at("size", 1.5)))
    if k > 0:
        d.line([(200, 1160), (200 + 400 * k, 1160)], A(NAVYT, 1), 8)
        d.line([(200, 1140), (200, 1180)], A(NAVYT, 1), 8); d.line([(200 + 400 * k, 1140), (200 + 400 * k, 1180)], A(NAVYT, 1), 8)
        d.text(400, 1205, "身长约 1.5 米", 34, A(NAVYT, k), k=1)
    wk = popk(t, at("size", 2.5))
    if wk > 0: stamp(d, t, at("size", 2.5), "≈ 11 公斤", 540, 470, 80, (200, 60, 50))

def s_beak(t, d):
    grad(d, (255, 160, 190), (220, 90, 140))
    for i in range(10): d.circ(540, 900, 160 + i * 120, outline=A(WHITE, 0.08), w=24)
    title(d, t, T["beak"], "没有牙", 300, 110)
    op = 0.4 * pulse(t, [at("beak", 0.5), at("beak", 1.5), at("beak", 3), at("beak", 4)], 5)
    head(d, 430, 860, 180, t, "proud", op=op)
    k = popk(t, at("beak", 1))
    if k > 0:
        tx, ty = 820, 560
        d.poly([(tx - 40, ty - 50), (tx + 40, ty - 50), (tx + 30, ty + 30), (tx + 12, ty + 60), (tx, ty + 20), (tx - 12, ty + 60), (tx - 30, ty + 30)], A(WHITE, k))
        cross(d, tx, ty, 70, ease(pr(t, at("beak", 1.3), at("beak", 1.8))), BAD)
    pk = popk(t, at("beak", 3))
    if pk > 0:
        parrot(d, 800, 1090, 50 * pk, pk); tag(d, 800, 990, "像鹦鹉", WHITE, pk, 34)

def s_neigh(t, d):
    grad(d, (30, 80, 60), (14, 40, 34)); plants(d, t, 1250, (24, 70, 50), (34, 96, 60))
    ground(d, 1230, (30, 60, 40), (40, 80, 50))
    u = ease(pr(t, T["neigh"] - 0.1, at("neigh", 1)))
    stomp = pulse(t, [at("neigh", 0), at("neigh", 1), at("neigh", 2), at("neigh", 3)], 8)
    trex(d, lerp(-400, 260, u), 760 + 10 * stomp, 260, t, 0.4 * pulse(t, [at("neigh", 2)], 3), 1, 1)
    tag(d, 260, 520, "霸王龙", TRX_L, popk(t, at("neigh", 1)), 36)
    chicken(d, 790, 1030, 100, t, "scared", f=-1, fruit=True)
    if t > at("neigh", 1): sweat(d, 700, 830, 12)
    title(d, t, T["neigh"], "邻居", 300, 110)

def s_menu(t, d):
    grad(d, (40, 70, 60), (24, 48, 40))
    d.rect(170, 380, 910, 1120, fill=A((30, 52, 44), 1), r=30); d.rect(170, 380, 910, 1120, outline=A((180, 120, 70), 1), w=22, r=30)
    d.text(540, 470, "恐龙菜单", 70, A(WHITE, 1), k=1)
    rows = [("肉", True, 0.5), ("草", True, 1.5), ("水果", None, 3.5)]
    for i, (s, ok, b) in enumerate(rows):
        y = 640 + i * 170; k = popk(t, at("menu", b))
        if k <= 0: continue
        d.text(400, y, s, 70, A(WHITE, k), k=1)
        if ok: check(d, 700, y, 50, ease(pr(t, at("menu", b), at("menu", b) + 0.25)), GOOD)
        else:
            q = 1 + 0.15 * math.sin(t * 8)
            d.text(700, y, "？", int(110 * q), A(YEL, k), k=1)
    tag(d, 540, 1050, "从没找到证据", BAD, popk(t, at("menu", 4)), 36, WHITE)
    hx = 860 - 60 * ease(pr(t, at("menu", 3), at("menu", 4)))
    chicken(d, hx - 20, 1140, 40, t, "sus", f=-1)

def s_jaw(t, d):
    grad(d, (16, 30, 70), (6, 12, 30))
    for i in range(14): d.line([(0, i * 140), (OW, i * 140)], A(XR, 0.06), 2)
    head(d, 470, 880, 240, t, "sus", op=0.1, xray=True)
    sy = 600 + 560 * ((t - T["jaw"]) * 0.6 % 1)
    d.rect(150, sy - 4, 930, sy + 4, fill=A(XR, 0.8)); d.rect(150, sy - 40, 930, sy, fill=A(XR, 0.12))
    mx, my = 700 + 60 * math.sin(t * 1.4), 1030 + 30 * math.cos(t * 1.7)
    d.circ(mx, my, 130, outline=A(WHITE, 1), w=18); d.circ(mx, my, 112, fill=A(XR, 0.12))
    d.line([(mx + 92, my + 92), (mx + 190, my + 190)], A((200, 140, 80), 1), 30)
    title(d, t, T["jaw"], "看下巴", 300, 110, XR)
    q = popk(t, at("jaw", 2))
    if q > 0: d.text(830, 600, "？", int(150 * (1 + 0.1 * math.sin(t * 10))), A(YEL, q), k=1)

def s_reveal(t, d):
    rays(d, t, (255, 200, 60), (255, 150, 40))
    for i in range(14):
        u = ((t - BIG2) * 0.5 + i * 0.13) % 1; x = 120 + (i * 137) % 860; y = lerp(380, 1500, u)
        [peach, lambda d_, x_, y_, r_, a_=1: cherry(d_, x_, y_, r_ * 0.5, a_), lambda d_, x_, y_, r_, a_=1: berries(d_, x_, y_, r_ * 0.35, a_)][i % 3](d, x, y, 40, 0.9)
    k = pulse(t, [BIG2], 4)
    chicken(d, 540, 1000 - 60 * k, 140, t, "proud", op=0.3 * k, f=1, bob=1, fruit=True)
    for i in range(3): peach(d, 470 + i * 70, 640 - 40 * k - 10 * math.sin(t * 5 + i), 30)
    stamp(d, t, BIG2, "水果党！", 540, 330, 150, (200, 40, 40))
    tag(d, 540, 480, "第一只确认的", WHITE, popk(t, at("reveal", 1)), 40)
    if t >= BIG2:
        sparks(d, 540, 700, t, BIG2, 60, 1300, YEL, 1, 3, 1.2); sparks(d, 540, 700, t, BIG2 + 0.05, 40, 1000, WHITE, 1, 5, 1.0)

def toolhead(d, t, bgt, bgb, n, ttl, key):
    grad(d, bgt, bgb)
    for i in range(10): d.circ(540, 950, 160 + i * 120, outline=A(WHITE, 0.07), w=24)
    tag(d, 540, 250, f"工具 {n}/3", WHITE, popk(t, T[key]), 34)
    title(d, t, T[key], ttl, 380, 110)

def s_f1(t, d):
    toolhead(d, t, (230, 70, 70), (150, 30, 50), 1, "前后嚼", "f1")
    u = t - T["f1"]; sl = 0.5 + 0.5 * math.sin(u * 2 * math.pi * 2) if u > 0.5 else 0
    head(d, 470, 980, 230, t, "chew", op=0.15, sl=sl)
    for i in range(3):
        a = 0.5 + 0.5 * pulse(t, [T["f1"] + 0.5 + j * 0.25 for j in range(20)], 6)
        d.line([(470 + 40 + i * 30, 980 - 60), (470 + 160 + sl * 80 + i * 20, 980 + 110)], A((255, 120, 140), 0.85 * a), 26)
    k = popk(t, at("f1", 1))
    if k > 0:
        arrow(d, 560, 1220, 820, 1220, WHITE, k, 18); arrow(d, 820, 1220, 560, 1220, WHITE, k, 18)
    tag(d, 760, 640, "颌部肌肉", (255, 160, 170), popk(t, at("f1", 1.5)), 34)

def s_f2(t, d):
    toolhead(d, t, (60, 120, 230), (30, 60, 150), 2, "下巴前滑", "f2")
    sl = ease(pr(t, at("f2", 1), at("f2", 1.5))) * (1 - ease(pr(t, at("f2", 3.5), at("f2", 4.5)))) + 0.6 * ease(pr(t, at("f2", 4.5), at("f2", 5))) * (1 - ease(pr(t, at("f2", 5.5), at("f2", 6))))
    head(d, 470, 980, 230, t, "sus", op=0.2, sl=sl)
    jx, jy = 470 + 0.42 * 230, 980 + 0.4 * 230
    glow(d, jx, jy, 90, (255, 255, 160), 0.8 + 0.2 * math.sin(t * 8)); d.circ(jx, jy, 22, fill=A(YEL, 1))
    tag(d, jx - 30, jy + 120, "关节", YEL, popk(t, at("f2", 0.5)), 34)
    k = popk(t, at("f2", 1))
    if k > 0: arrow(d, 600, 1240, 840, 1240, WHITE, k, 20)

def s_f3(t, d):
    toolhead(d, t, (255, 150, 60), (220, 90, 40), 3, "脊和沟", "f3")
    sq = [at("f3", b) for b in (1, 2, 3, 4, 5)]
    op = 0.55 - 0.5 * pulse(t, sq, 5)
    head(d, 370, 960, 250, t, "chew", op=op, ridges=True)
    hits = sum(1 for h in sq if t >= h)
    bx, by = 370 + 1.15 * 250, 960 + 0.25 * 250
    if hits < 2: peach(d, bx + 40, by, 70 * (1 - 0.12 * hits))
    for i in range(min(hits * 3, 12)):
        ang = i * 2.1; rr = 40 + (i * 23) % 70
        d.circ(bx + 40 + math.cos(ang) * rr, by + 40 + math.sin(ang) * rr * 0.6, 20 - i % 3 * 4, fill=A(mix(PEACH, PEACH_L, (i % 3) / 2), 0.95))
    for h in sq:
        sparks(d, bx + 30, by, t, h, 14, 600, PEACH_L, 1, int(h * 7), 0.5)
    tag(d, 540, 520, "一道道脊和沟", WHITE, popk(t, at("f3", 0.5)), 34)

def s_rare(t, d):
    grad(d, (120, 70, 190), (60, 30, 120))
    title(d, t, T["rare"], "三样全有？", 300, 100)
    cards = [("鹦鹉", 0.5, "有一部分"), ("海龟", 1.5, "有一部分"), ("地狱鸡", 4.5, "三样全有")]
    for i, (nm, b, lab) in enumerate(cards):
        k = popk(t, at("rare", b))
        if k <= 0: continue
        cx = 300 + i * 240; cy = 820 + 30 * (1 - k); hot = i == 2
        if hot: glow(d, cx, cy, 260, YEL, 0.6 + 0.2 * math.sin(t * 6))
        d.rect(cx - 112, cy - 240, cx + 112, cy + 240, fill=A(WHITE if not hot else (255, 240, 180), k), r=30)
        if i == 0: parrot(d, cx - 10, cy - 110, 55 * k, k)
        elif i == 1: turtle(d, cx - 20, cy - 70, 70 * k, t, k)
        else: head(d, cx - 35, cy - 60, 55 * k, t, "proud", a=k)
        d.text(cx, cy + 70, nm, 44, A(NAVYT, k), k=1)
        for j in range(3 if hot else 0):
            on = True
            jk = popk(t, at("rare", b + 0.5 + j * 0.3)) if hot else k
            d.rect(cx - 95 + j * 68, cy + 130, cx - 41 + j * 68, cy + 184, fill=A(GOOD if on else (210, 210, 220), jk if on else 0.6 * k), r=12)
            if on and jk > 0: check(d, cx - 68 + j * 68, cy + 157, 16, jk, WHITE)
        if not hot: d.text(cx, cy + 160, "部分", 34, A((120, 120, 150), k), k=1)
        tag(d, cx, cy - 245, lab, (200, 60, 50) if hot else (90, 90, 140), k, 26, WHITE)
    tag(d, 540, 1170, "今天没有动物三样全有", YEL, popk(t, at("rare", 6)), 34)

def s_stone(t, d):
    grad(d, (90, 170, 110), (40, 110, 70)); ground(d, 1200, (60, 120, 70), (80, 150, 90))
    title(d, t, T["stone"], "怎么磨碎食物？", 300, 90)
    # other plant-eating theropod: body with x-ray stomach full of rattling stones
    x, y = 300, 900
    d.ell(x, y, 170, 130, A((150, 120, 200), 1)); d.line([(x + 100, y - 60), (x + 160, y - 280)], A((150, 120, 200), 1), 60)
    d.circ(x + 170, y - 300, 60, fill=A((150, 120, 200), 1)); d.circ(x + 180, y - 315, 18, fill=A(WHITE, 1)); d.circ(x + 186, y - 315, 9, fill=A(INK, 1))
    for j in (0, 1): d.line([(x - 40 + j * 70, y + 100), (x - 50 + j * 70, y + 290)], A((120, 90, 170), 1), 30)
    d.ell(x - 10, y + 10, 100, 70, A((255, 255, 255), 0.35))
    rattle = 1 if t > at("stone", 1) else 0
    for i in range(7):
        a_ = i * 0.9 + t * 6 * rattle
        d.circ(x - 10 + math.cos(a_) * 50 * (0.4 + (i % 3) * 0.3), y + 10 + math.sin(a_) * 35 * (0.4 + (i % 3) * 0.3), 20, fill=A((150, 150, 160), 1))
    tag(d, x - 20, 480, "吞石头", (150, 150, 160), popk(t, at("stone", 1)), 34, WHITE)
    k = popk(t, at("stone", 5.5))
    if k > 0:
        u = t - at("stone", 5.5)
        chicken(d, 790, 980, 90, t, "chew", op=0.3 * (0.5 + 0.5 * math.sin(u * 16)), f=-1, a=k)
        tag(d, 790, 680, "自己嚼！", (220, 70, 50), popk(t, at("stone", 6)), 38, WHITE)
        if u > 0: sparks(d, 720, 860, t, at("stone", 6), 14, 500, PEACH_L, 1, 7, 0.5)
    else:
        d.text(790, 950, "VS", 80, A(WHITE, 0.6), k=1)

def s_fruit(t, d):
    grad(d, (255, 170, 190), (240, 110, 150))
    for i in range(9): d.circ(540, 900, 160 + i * 130, outline=A(WHITE, 0.08), w=26)
    title(d, t, T["fruit"], "可能的菜单", 300, 100)
    k1 = popk(t, at("fruit", 0.5)); k2 = popk(t, at("fruit", 3)); k3 = popk(t, at("fruit", 4)); k4 = popk(t, at("fruit", 5.5))
    if k1 > 0: berries(d, 300, 640, 32 * k1); tag(d, 300, 820, "浆果", WHITE, k1, 34)
    if k2 > 0: peach(d, 560, 690, 85 * k2, cut=k4 > 0.5); tag(d, 560, 830, "桃", WHITE, k2, 34)
    if k3 > 0: cherry(d, 800, 690, 40 * k3); tag(d, 800, 830, "樱桃", WHITE, k3, 34)
    tag(d, 540, 920, "核果：中间有硬核", (200, 60, 90), k4, 32, WHITE)
    chicken(d, 540, 1120, 68, t, "happy", op=0.2 * (0.5 + 0.5 * math.sin(t * 10)), f=1, bob=1)

def s_seed(t, d):
    grad(d, (120, 200, 230), (60, 150, 120)); ground(d, 1150, (90, 150, 80), (110, 180, 90))
    title(d, t, T["seed"], "帮植物搬家？", 300, 100)
    u = (t - T["seed"]) / (nxt("seed") - T["seed"])
    cx = lerp(150, 760, u)
    for i in range(5):
        dt = at("seed", 1 + i * 1.6)
        if t < dt: continue
        sx = lerp(150, 760, (dt - T["seed"]) / (nxt("seed") - T["seed"])) - 60
        g = ease(pr(t, dt + 0.3, dt + 1.2))
        d.circ(sx, 1150 - 10, 12, fill=A(PIT, 1))
        if g > 0:
            d.line([(sx, 1145), (sx, 1145 - 90 * g)], A(LEAFC, 1), 10)
            d.ell(sx - 22 * g, 1145 - 90 * g, 26 * g, 12 * g, A(LEAFC, 1)); d.ell(sx + 22 * g, 1145 - 95 * g, 26 * g, 12 * g, A(LEAFC, 1))
    chicken(d, cx, 920, 90, t, "happy", f=1, walk=1, bob=1, fruit=True)
    k = popk(t, at("seed", 5))
    if k > 0: stamp(d, t, at("seed", 5), "待证实", 540, 500, 100, BAD)

def s_card(t, d):
    grad(d, (255, 214, 90), (240, 150, 50))
    for i in range(10): d.circ(540, 600, 160 + i * 140, outline=A(WHITE, 0.08), w=26)
    chicken(d, 540, 560, 90, t, "proud", f=1, bob=1, fruit=True)
    k = popk(t, T["card"] + 0.1)
    if k <= 0: return
    al = min(1, k * 1.5); cy = 1040 + 40 * (1 - k); w = 700 * (0.7 + 0.3 * k)
    d.rect(540 - w / 2, cy - 190, 540 + w / 2, cy + 200, fill=A(WHITE, 0.97 * al), r=34)
    d.rect(540 - w / 2, cy - 190, 540 - w / 2 + 16, cy + 200, fill=A(GOLD, al), r=8)
    tag(d, 540, cy - 190, "一句话学会", GOLD, al, 34)
    chips = [("前后嚼", (220, 70, 70)), ("下巴前滑", (60, 120, 230)), ("喙有脊沟", (240, 130, 40))]
    for i, (s, col) in enumerate(chips):
        ck = popk(t, at("card", 0.6 + i * 0.6))
        if ck > 0: tag(d, 540 + (i - 1) * 215, cy - 70, s, col, ck, 32, WHITE)
    ek = popk(t, at("card", 2.6))
    if ek > 0:
        d.text(540, cy + 40, "= 恐龙里的", int(44 * ek) + 1, A(NAVYT, ek), k=1)
        d.text(540, cy + 120, "水果党", int(84 * ek) + 1, A((200, 40, 40), ek), k=1)

def s_end(t, d):
    grad(d, (255, 140, 90), (120, 50, 90)); glow(d, 540, 900, 380, (255, 220, 140), 0.7)
    volcano(d, 860, 1060, 300, t, 0.6)
    tx = lerp(-300, 1400, pr(t, T["end"], DUR)); trex(d, tx, 880, 150, t, 0, 1, 0.35)
    plants(d, t, 1160, (110, 50, 70), (150, 70, 80)); ground(d, 1140, (110, 46, 60), (150, 70, 70))
    chicken(d, 540, 900, 110, t, "chew", op=0.25 * (0.5 + 0.5 * math.sin(t * 12)), f=1, bob=1, fruit=True)
    stamp(d, t, T["end"] + 0.05, "地狱鸡", 540, 320, 130, YEL)
    tag(d, 540, 460, "Infernogallus jamesi", WHITE, popk(t, T["end"] + 0.3), 30)
    ra = popk(t, at("end", 2))
    d.rect(200, 520, 880, 640, fill=A((20, 12, 30), 0.5 * ra), r=20)
    d.text(540, 558, "Funston 等 (2026) Nature Communications", 26, A(WHITE, 0.95 * ra))
    d.text(540, 600, "化石未保存羽毛，羽毛据近亲推测", 26, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

def subs(t, d):
    if SIL0 <= t < BIG2: return
    for a, b, s, key in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70
            w = max(d.tlen(x, 54, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 70 + 46, fill=A((15, 12, 26), 0.82 * al), r=22)
            for i, x in enumerate(ls): d.text(540, y0 + i * 70, x, 54, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇新发现"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)

SF = {"site": s_site, "size": s_size, "beak": s_beak, "neigh": s_neigh, "menu": s_menu, "jaw": s_jaw, "reveal": s_reveal, "f1": s_f1, "f2": s_f2,
      "f3": s_f3, "rare": s_rare, "stone": s_stone, "fruit": s_fruit, "seed": s_seed, "card": s_card, "end": s_end}
SECS = [(-1, HOOKCUT, s_hook), (HOOKCUT, T["site"], s_name)] + [(T[n], nxt(n) if n != "jaw" else SIL0, SF[n]) for n in NAMES[2:]]
SECS = [(a, (99 if n == len(SECS) - 1 else b), f) for n, (a, b, f) in enumerate(SECS)]
HITS = [T[n] for n in NAMES] + [at("name", 1.5), at("name", 2.5), at("site", 2.5), at("size", 1), at("size", 2.5), at("beak", 1), at("beak", 3),
        at("menu", 0.5), at("menu", 1.5), at("menu", 3.5), at("reveal", 1), at("f1", 1), at("f2", 1), at("f3", 1), at("f3", 3), at("f3", 5),
        at("rare", 0.5), at("rare", 1.5), at("rare", 4.5), at("stone", 5.5), at("fruit", 0.5), at("fruit", 3), at("fruit", 4), at("seed", 5)]
def cam(t):
    z = 1.0 + 0.015 * pulse(t, HITS, 7) + 0.04 * pulse(t, [HOOK_HIT, BIG2], 3)
    if T["jaw"] <= t < SIL0: z += 0.06 * eio(pr(t, T["jaw"], SIL0))
    if HOOK_STOP <= t < HOOKCUT: z += 0.05 * pr(t, HOOK_STOP, HOOKCUT)
    amp = 8 * pulse(t, [HOOK_HIT, BIG2], 5) + 1.5 * pulse(t, HITS, 8)
    if T["neigh"] <= t < T["menu"]: amp += 3 * pulse(t, [at("neigh", b) for b in range(4)], 9)
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
        for ts in sys.argv[2:]: frame(float(ts)).save(f"/tmp/hc_test_{float(ts):05.2f}.png")
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
