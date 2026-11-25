import sys, subprocess
from fx import *
from cues import *

LIZ = (110, 200, 90); LIZ_D = (70, 150, 66); LIZ_B = (200, 236, 150); LIZ_S = (60, 130, 60)
OLDL = (150, 160, 80); OLDL_D = (110, 116, 56)
PRED = (150, 80, 190); PRED_D = (104, 48, 140); PRED_L = (200, 140, 230); MOUTHC = (120, 20, 50)
AMB = (236, 150, 30); AMB_D = (190, 100, 20); AMB_L = (255, 206, 90)
TWIGC = (130, 86, 50); SKIN = (255, 206, 170); SKIN_D = (226, 160, 126)
NAVYT = (24, 20, 40); GOOD = (90, 200, 110); BAD = (240, 80, 70); GOLD = (255, 200, 60)
MUSC = (236, 110, 110); MUSC_D = (200, 70, 80); BONE = (250, 240, 214); BONE_D = (214, 196, 160)

def rell(d, cx, cy, rx, ry, ang, fill, n=28):
    ca, sa = math.cos(ang), math.sin(ang)
    pts = [(cx + rx * math.cos(u) * ca - ry * math.sin(u) * sa, cy + rx * math.cos(u) * sa + ry * math.sin(u) * ca) for u in [i / n * 2 * math.pi for i in range(n)]]
    d.poly(pts, fill)

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
def bang(d, t, t0, x, y, s="啪！", size=110, col=WHITE, life=0.7):
    u = t - t0
    if 0 <= u < life:
        k = back(pr(t, t0, t0 + 0.15)); d.text(x, y - u * 60, s, int(size * (0.5 + 0.5 * k)), A(col, 1 - pr(t, t0 + life * 0.6, t0 + life)), k=1)
def ground(d, y, col=(150, 110, 70), top=(110, 180, 90)):
    d.rect(-50, y, OW + 50, OH + 50, fill=A(col, 1)); d.rect(-50, y, OW + 50, y + 22, fill=A(top, 1))
    r2 = random.Random(2)
    for i in range(26): d.circ(r2.uniform(0, 1080), r2.uniform(y + 50, 1900), r2.uniform(5, 13), fill=A(mix(col, (0, 0, 0), 0.25), 0.6))
def speedlines(d, t, a=0.35, col=WHITE):
    r2 = random.Random(5)
    for i in range(16):
        y = r2.uniform(300, 1250); L = r2.uniform(120, 320); x = (r2.uniform(0, 1400) - t * 2600) % 1500 - 200
        d.line([(x, y), (x + L, y)], A(col, a), 6)

def swirl(d, t, c1, c2, cx=540, cy=900):
    grad(d, c1, c2)
    for i in range(9):
        r = ((t * 120 + i * 140) % 1300)
        d.circ(cx, cy, r, outline=A(mix(c1, WHITE, 0.25), 0.18 * (1 - r / 1300)), w=40)

# ---------------- characters ----------------
def tailpts(x0, y0, L, s, t, dir, droop=0.25, wav=0.08, spd=8, n=26):
    return [(x0 - dir * L * u, y0 + s * droop * u * (2 - u) + math.sin(u * 5 - t * spd) * s * wav * u, u) for u in [i / n for i in range(n + 1)]]
def drawtail(d, pts, s, col, dk, a, w0=0.2, regrow=False):
    for x, y, u in pts: d.circ(x, y + s * 0.04, s * w0 * (1 - u * 0.8), fill=A(dk, a))
    for x, y, u in pts: d.circ(x, y - s * 0.01, s * w0 * (1 - u * 0.8) * 0.88, fill=A(col, a))
    for i, (x, y, u) in enumerate(pts):
        if i % 4 == 2 and u < 0.92: d.circ(x, y - s * w0 * 0.35 * (1 - u * 0.8), s * w0 * 0.3 * (1 - u * 0.8), fill=A(mix(col, WHITE, 0.35), a * 0.7))

def lizard(d, x, y, s, t, mood="happy", tail=1.0, dir=1, run=0.0, col=LIZ, dk=LIZ_D, a=1.0, look=0.0, hop=0.0, stub=0.0, vsign=0.0):
    if a <= 0.01: return
    y = y - hop
    d.ell(x, y + hop + 4, s * 1.1, s * 0.09, A((0, 0, 0), 0.22 * a))
    by = y - s * 0.4
    # legs (far pair first, darker)
    for k, (lx, ph) in enumerate([(0.45, 0.0), (-0.45, math.pi), (0.5, math.pi), (-0.4, 0.0)]):
        sw = math.sin(run * 2 * math.pi + ph); fx_ = x + dir * (lx * s + sw * s * 0.22); fy = y - max(0, math.cos(run * 2 * math.pi + ph)) * s * 0.12 * (run != 0)
        c = dk if k < 2 else col
        d.line([(x + dir * lx * s, by + s * 0.1), (fx_, fy)], A(c, a), s * 0.14); d.circ(fx_ + dir * s * 0.05, fy, s * 0.09, fill=A(c, a))
    if tail > 0: drawtail(d, tailpts(x - dir * s * 0.62, by + s * 0.05, s * 1.9 * tail, s, t, dir), s, col, dk, a)
    if stub > 0: drawtail(d, tailpts(x - dir * s * 0.62, by + s * 0.05, s * 1.9 * stub, s, t, dir, 0.1, 0.02), s, (220, 250, 130), (170, 210, 90), a)
    d.ell(x, by + s * 0.04, s * 0.78, s * 0.32, A(dk, a)); d.ell(x, by, s * 0.75, s * 0.28, A(col, a))
    d.ell(x + dir * s * 0.05, by + s * 0.15, s * 0.55, s * 0.1, A(LIZ_B if col == LIZ else mix(col, WHITE, 0.4), a))
    for i in range(4): d.circ(x + dir * (-0.4 + i * 0.25) * s, by - s * 0.12, s * 0.06, fill=A(mix(dk, (0, 0, 0), 0.1), a))
    d.ell(x - dir * s * 0.15, by - s * 0.18, s * 0.3, s * 0.07, A(WHITE, 0.35 * a))
    hx, hy = x + dir * s * 0.9, by - s * 0.18
    d.ell(hx, hy + s * 0.04, s * 0.44, s * 0.36, A(dk, a)); d.ell(hx, hy, s * 0.42, s * 0.34, A(col, a))
    d.ell(hx - dir * s * 0.12, hy - s * 0.2, s * 0.14, s * 0.07, A(WHITE, 0.45 * a))
    face(d, hx + dir * s * 0.06, hy, s * 0.4, mood, a, look)
    if vsign > 0:
        ax, ay = x + dir * s * 0.3, by - s * 0.1; ex, ey = x + dir * s * 0.05, ay - s * 0.85 * vsign
        d.line([(ax, ay), (ex, ey)], A(dk, a), s * 0.16)
        for k in (-1, 1): d.line([(ex, ey), (ex + k * s * 0.16, ey - s * 0.38 * vsign)], A(col, a), s * 0.11)
        d.circ(ex, ey, s * 0.14, fill=A(col, a))
        for k in (-1, 1): d.circ(ex + k * s * 0.16, ey - s * 0.38 * vsign, s * 0.065, fill=A(col, a))

def looseTail(d, x, y, s, t, wig=1.0, dir=1, col=LIZ, dk=LIZ_D, a=1.0, L=1.9):
    # stump end at (x, y); tail lies toward -dir; wig drives a fast S-wiggle
    pts = [(x - dir * s * L * u * (1 - 0.08 * wig * math.sin(t * 20)), y - math.sin(u * 7 - t * 28) * s * 0.3 * wig * (0.3 + u), u) for u in [i / 26 for i in range(27)]]
    drawtail(d, pts, s, col, dk, a)
    d.ell(x, y, s * 0.07, s * 0.17, A(MUSC, a))

def monster(d, x, y, s, t, open_=0.0, mood="angry", dir=1, look=0.0, a=1.0):
    d.ell(x, y + s * 0.05, s, s * 0.85, A(PRED_D, a)); d.ell(x - dir * s * 0.03, y, s * 0.96, s * 0.8, A(PRED, a))
    for i in range(4):   # spikes
        sx = x - dir * s * 0.55 + dir * i * s * 0.3; sy = y - s * 0.78 + abs(i - 1.5) * s * 0.06
        d.poly([(sx - s * 0.12, sy + s * 0.08), (sx, sy - s * 0.3), (sx + s * 0.12, sy + s * 0.08)], A(PRED_L, a))
    d.ell(x - dir * s * 0.35, y - s * 0.45, s * 0.3, s * 0.12, A(WHITE, 0.3 * a))
    o = open_ * s * 0.38; mx = x + dir * s * 0.98
    d.poly([(x + dir * s * 0.05, y + s * 0.12), (mx, y - s * 0.02 - o), (mx, y + s * 0.26 + o)], A(MOUTHC, a))
    for i in range(4):
        tx = x + dir * s * (0.35 + i * 0.16); ut = y + s * 0.12 - (o + s * 0.14) * (i + 1) / 5; lt = y + s * 0.12 + (o + s * 0.14) * (i + 1) / 5
        d.poly([(tx - s * 0.05, ut - 2), (tx, ut + s * 0.1), (tx + s * 0.05, ut - 2)], A(WHITE, a))
        d.poly([(tx - s * 0.05, lt + 2), (tx, lt - s * 0.1), (tx + s * 0.05, lt + 2)], A(WHITE, a))
    ex, ey = x + dir * s * 0.3, y - s * 0.3
    kind = "chill" if mood == "angry" else mood
    face(d, ex, ey + s * 0.1, s * 0.6, "scared" if kind == "huh" else kind, a, look, nomouth=True)
    if mood == "angry":
        for k in (-1, 1): d.line([(ex + k * s * 0.38, ey - s * 0.12), (ex + k * s * 0.08, ey)], A(INK, a), s * 0.06)
def person(d, x, y, s, t, mood="chill", jump=0.0, a=1.0):
    # chair
    d.rect(x - s * 0.5, y - s * 0.62, x + s * 0.5, y - s * 0.5, fill=A((90, 90, 120), a), r=8)
    d.rect(x + s * 0.38, y - s * 1.4, x + s * 0.5, y - s * 0.5, fill=A((90, 90, 120), a), r=8)
    for k in (-1, 1): d.rect(x + k * s * 0.4 - s * 0.05, y - s * 0.5, x + k * s * 0.4 + s * 0.05, y, fill=A((70, 70, 96), a))
    j = jump * s * 0.9; by = y - s * 0.62 - j
    for k in (-1, 1): d.line([(x - s * 0.15 + k * s * 0.1, by), (x - s * 0.45 + k * s * 0.1 + jump * k * s * 0.1, by + s * 0.45 + j * 0.6)], A((60, 80, 150), a), s * 0.16)
    d.rect(x - s * 0.32, by - s * 0.8, x + s * 0.28, by + s * 0.05, fill=A((240, 240, 250), a), r=s * 0.2)   # lab coat
    arm_up = jump
    for k in (-1, 1):
        sx, sy = x + k * s * 0.28, by - s * 0.65
        ex, ey = sx + k * s * 0.25, sy + lerp(s * 0.5, -s * 0.55, arm_up)
        d.line([(sx, sy), (ex, ey)], A((230, 230, 245), a), s * 0.14); d.circ(ex, ey, s * 0.09, fill=A(SKIN, a))
    hx, hy = x - s * 0.02, by - s * 1.18
    d.circ(hx, hy, s * 0.42, fill=A(SKIN_D, a)); d.circ(hx - s * 0.02, hy - s * 0.02, s * 0.4, fill=A(SKIN, a))
    d.d.chord((P(hx - s * 0.42), P(hy - s * 0.46), P(hx + s * 0.42), P(hy + s * 0.2)), 180, 360, fill=A((60, 40, 30), a))
    face(d, hx, hy + s * 0.04, s * 0.36, mood, a)
    for k in (-1, 1): d.circ(hx + k * s * 0.13, hy - s * 0.0, s * 0.11, outline=A((40, 40, 60), a), w=max(2, s * 0.025))
    tag(d, x - s * 0.02, by - s * 0.35, "博士生", (90, 150, 240), a, max(18, int(s * 0.17)), WHITE)

def amberblob(d, x, y, r, t, a=1.0, glowk=0.4):
    glow(d, x, y, r * 1.7, (255, 190, 80), glowk * a)
    pts = [(x + r * math.cos(u) * (1 + 0.1 * math.sin(u * 3 + 1)), y + r * 0.82 * math.sin(u) * (1 + 0.08 * math.cos(u * 2))) for u in [i / 36 * 2 * math.pi for i in range(36)]]
    d.poly(pts, A(AMB_D, a))
    d.poly([(x + (px - x) * 0.93 - r * 0.03, y + (py - y) * 0.92 - r * 0.03) for px, py in pts], A(AMB, a))
    d.ell(x - r * 0.1, y - r * 0.05, r * 0.6, r * 0.45, A(AMB_L, 0.45 * a))
    r2 = random.Random(3)
    for i in range(9): d.circ(x + r2.uniform(-0.7, 0.7) * r, y + r2.uniform(-0.5, 0.5) * r, r * r2.uniform(0.02, 0.05), fill=A(WHITE, 0.4 * a))
    for i in range(3): d.circ(x + r2.uniform(-0.5, 0.5) * r, y + r2.uniform(-0.4, 0.4) * r, r * 0.3, fill=A((255, 230, 180), 0.12 * a))
def amberhl(d, x, y, r, a=1.0):
    d.ell(x - r * 0.48, y - r * 0.45, r * 0.28, r * 0.12, A(WHITE, 0.6 * a)); d.circ(x - r * 0.15, y - r * 0.58, r * 0.05, fill=A(WHITE, 0.7 * a))
def twig(d, x, y, L, w, t, a=1.0, scales=0.0):
    pts = [(x - L / 2 + L * u, y + math.sin(u * 4.5) * w * 0.6) for u in [i / 20 for i in range(21)]]
    col = mix(TWIGC, (120, 120, 60), scales)
    for i, (px, py) in enumerate(pts):
        u = i / 20; d.circ(px, py, w * (1 - u * 0.6), fill=A(mix(col, (0, 0, 0), 0.2), a))
        d.circ(px, py - w * 0.1, w * (1 - u * 0.6) * 0.85, fill=A(col, a))
    if scales < 0.5:
        d.line([(x - L * 0.1, y), (x - L * 0.2, y - w * 2.0)], A(TWIGC, a * (1 - scales * 2)), w * 0.4)
    if scales > 0:
        for i, (px, py) in enumerate(pts[:-1]):
            u = i / 20; rr = w * (1 - u * 0.6)
            for k in (-1, 0, 1):
                d.arc(px, py + k * rr * 0.5, rr * 0.35, rr * 0.3, 200, 340, A((220, 230, 160), a * scales), max(2, rr * 0.12))

def flowerx(d, x, y, r, ks, a=1.0, skin=LIZ, n=6):
    d.circ(x, y, r, fill=A(mix(skin, (0, 0, 0), 0.25), a)); d.circ(x, y, r * 0.93, fill=A(skin, a))
    for i in range(18):
        ang = i / 18 * 2 * math.pi; d.circ(x + math.cos(ang) * r * 0.93, y + math.sin(ang) * r * 0.93, r * 0.09, fill=A(mix(skin, WHITE, 0.25), a))
    d.circ(x, y, r * 0.82, fill=A((250, 200, 190), a))
    for i in range(n):
        k = ks[i] if i < len(ks) else 1
        if k <= 0: continue
        ang = i / n * 2 * math.pi - math.pi / 2
        rr = r * 0.4 * k
        rell(d, x + math.cos(ang) * rr * 1.05, y + math.sin(ang) * rr * 1.05, rr * 0.95, rr * 0.48, ang, A(MUSC_D, a))
        rell(d, x + math.cos(ang) * rr * 1.0, y + math.sin(ang) * rr * 1.0, rr * 0.82, rr * 0.38, ang, A(MUSC, a))
        rell(d, x + math.cos(ang) * rr * 0.9, y + math.sin(ang) * rr * 0.9, rr * 0.4, rr * 0.12, ang, A(WHITE, 0.35 * a))
    d.circ(x, y, r * 0.15, fill=A(BONE, a))
def dinosil(d, t, col, a=1.0):
    # sauropod right, small raptor-ish left; flat silhouettes
    bx, by = 760, 1230
    d.ell(bx, by - 120, 170, 85, A(col, a)); d.line([(bx + 110, by - 160), (bx + 230, by - 380)], A(col, a), 50); d.ell(bx + 250, by - 390, 45, 28, A(col, a))
    d.poly([(bx - 140, by - 140), (bx - 360, by - 60), (bx - 130, by - 90)], A(col, a))
    for k in (-100, -40, 60, 120): d.rect(bx + k - 22, by - 70, bx + k + 22, by + 10, fill=A(col, a))
    rx, ry = 270, 1230
    d.ell(rx, ry - 130, 80, 50, A(col, a)); d.ell(rx + 85, ry - 205, 50, 32, A(col, a)); d.poly([(rx - 60, ry - 150), (rx - 230, ry - 190), (rx - 60, ry - 110)], A(col, a))
    for k in (-20, 25): d.line([(rx + k, ry - 100), (rx + k + 10, ry)], A(col, a), 22)

# ---------------- scenes ----------------
def s_hook(t, d):
    if t < HOOK_HIT:
        grad(d, (90, 190, 120), (40, 120, 80)); speedlines(d, t)
    else: rays(d, t, (255, 196, 70), (240, 150, 40), n=20, cx=600, cy=1050)
    ground(d, 1160)
    u = max(0, t - HOOK_HIT)
    # predator chasing from left
    mx = 300 + 140 * pr(t, 0, HOOK_HIT) - 40 * ease(pr(t, HOOK_HIT, HOOK_HIT + 0.3))
    op = 0.5 + 0.5 * math.sin(t * 25) if t < HOOK_HIT else 0.3 * (1 - pr(t, HOOK_HIT, 0.8))
    monster(d, mx, 940, 190, t, op, "angry" if t < HOOK_HIT + 0.5 else "sus", look=0.6 if t < 0.8 else 0.3 + 0.4 * math.sin(t * 9))
    # lizard
    if t < HOOK_HIT:
        lx = 640 + 40 * t; lizard(d, lx, 1160, 140, t, "scream", 1.0, 1, run=t * 7, hop=abs(math.sin(t * 22)) * 20)
    else:
        lx = lerp(656, 720, ease(pr(t, HOOK_HIT, SMUG - 0.2)))
        dir_ = 1 if t < SMUG else -1
        lizard(d, lx, 1160, 140, t, "scared" if t < SMUG else "proud", 0.0, dir_, run=t * 9 if t < SMUG - 0.2 else 0, hop=18 * pulse(t, [SMUG], 8))
        tx = 656 - 140 * 0.62 + 30
        looseTail(d, tx - 70, 1100, 140, t, 0.5 + 0.8 * pulse(t, [HOOK_HIT] + WIGS0, 3), 1, L=1.7)
        sparks(d, tx - 50, 1090, t, HOOK_HIT, n=40, spd=900, col=(255, 250, 200), seed=4)
        bang(d, t, HOOK_HIT, tx - 60, 900, "啪！", 120, WHITE)
        if t > SMUG: bubble(d, 760, 840, "拜拜～", 1, WHITE, NAVYT, popk(t, SMUG), 40)
    stamp(d, t, HOOK_HIT, "断尾逃命！", 540, 340, 140, WHITE)

def s_twist(t, d):
    grad(d, (60, 190, 190), (20, 120, 140)); ground(d, 1160, (70, 120, 110), (100, 180, 150))
    w = 0.45 + 0.9 * pulse(t, WIGS, 3)
    looseTail(d, 600, 1110, 140, t, w, 1, L=1.7)
    for h in WIGS: rings(d, 480, 1100, t, [h], WHITE, 0.6, 260)
    lk = math.sin(t * 9) * 0.8
    monster(d, 400, 780, 210, t, 0.15, "huh" if t > HUH else "chill", look=lk)
    if t > HUH:
        k = popk(t, HUH); d.text(690 + 10 * math.sin(t * 6), 560, "?", int(150 * k), A(YEL, 1), k=1)
    # lizard tiptoes away right
    lx = lerp(760, 1010, ease(pr(t, TWIST + 0.4, 7.4)))
    lizard(d, lx, 1160, 80, t, "proud", 0.0, 1, run=t * 2.5, hop=abs(math.sin(t * 8)) * 10)
    if t > SNEAK: tag(d, min(lx, 840), 990, "溜了～", WHITE, popk(t, SNEAK), 36)
    tag(d, 540, 340, "尾巴还在扭！", WHITE, popk(t, WIGS[0]) * (1 - pr(t, SNEAK - 0.1, SNEAK)), 64)
    stamp(d, t, SNEAK, "骗过去了！", 540, 340, 120, YEL)

def s_q(t, d):
    swirl(d, t, (130, 70, 200), (70, 30, 130), 540, 520)
    k = popk(t, QMARK)
    if k > 0:
        wob = math.sin(t * 5) * 8
        glow(d, 540, 500, 260, (255, 220, 120), 0.4 * k)
        d.text(540 + wob, 500, "?", int(300 * k), A(YEL, 1), k=1)
    # rewinding time band
    band_y = 860
    d.rect(150, band_y - 60, 930, band_y + 60, fill=A((40, 20, 80), 0.75), r=30)
    off = (t - Q) * 380 + 400 * sum(ease(pr(t, h, h + 0.3)) for h in ROLL)
    for i in range(-2, 30):
        x = 180 + ((i * 90 + off) % 900)
        if 180 <= x <= 900: d.rect(x - 3, band_y - 30 + (0 if i % 2 else 12), x + 3, band_y + 30 - (0 if i % 2 else 12), fill=A(WHITE, 0.7))
    for s_, x in (("<", 470), ("<", 510)): pass
    d.poly([(520, band_y - 26), (470, band_y), (520, band_y + 26)], A(YEL, 0.9)); d.poly([(580, band_y - 26), (530, band_y), (580, band_y + 26)], A(YEL, 0.9))
    labs = ["今天", "1 万年前", "100 万年前", "更早……"]
    cur = -1
    for i, h in enumerate(ROLL):
        if t >= h: cur = i
    if cur >= 0: tag(d, 540, 975, labs[cur], WHITE, popk(t, ROLL[cur]), 52)
    lizard(d, 430, 1175, 85, t, "sus", 1.0, 1)
    stamp(d, t, QMARK, "从什么时候？", 540, 260, 96, WHITE)

def ruler(d, x0, x1, y, k, n=18, a=1.0):
    d.rect(x0 - 20, y - 40, x1 + 20, y + 40, fill=A((255, 226, 110), a), r=10)
    for i in range(n + 1):
        x = lerp(x0, x1, i / n); hh = 28 if i % 5 == 0 else 16
        d.rect(x - 2, y - 40, x + 2, y - 40 + hh, fill=A(NAVYT, a))
    xm = lerp(x0, x1, k)
    d.rect(x0, y + 6, xm, y + 22, fill=A(RED, a), r=6)
    d.text(xm, y + 70, f"{int(round(k * n))} mm", 34, A(WHITE, a), k=1)
def finger(d, x, y, s, a=1.0):
    d.rect(x, y - s * 0.32, x + s * 2.5, y + s * 0.32, fill=A(SKIN_D, a), r=s * 0.32)
    d.rect(x + 4, y - s * 0.3, x + s * 2.5, y + s * 0.26, fill=A(SKIN, a), r=s * 0.3)
    d.rect(x + s * 0.08, y - s * 0.24, x + s * 0.55, y + s * 0.12, fill=A((255, 236, 226), a), r=s * 0.15)
def s_amber(t, d):
    grad(d, (150, 86, 40), (70, 34, 18))
    glow(d, 540, 700, 600, (255, 180, 80), 0.35)
    k = popk(t, AMBER_HIT)
    r = 150 * k
    if k > 0:
        amberblob(d, 480, 700, r, t, 1, 0.5 + 0.3 * math.sin(t * 4))
        twig(d, 480, 700, r * 0.9, r * 0.06, t)
        amberhl(d, 480, 700, r)
        sparks(d, 480, 700, t, AMBER_HIT, n=30, spd=700, col=(255, 230, 150), seed=7)
    fk = ease(pr(t, FINGER, FINGER + 0.4))
    if fk > 0:
        finger(d, lerp(1000, 660, fk), 700, 120)
        tag(d, 760, 540, "指尖大小", WHITE, popk(t, FINGER + 0.2), 40)
    rk = ease(pr(t, AMBER_HIT + 0.4, RULER))
    if t > AMBER_HIT + 0.3: ruler(d, 330, 630, 960, rk, a=ease(pr(t, AMBER_HIT + 0.3, AMBER_HIT + 0.5)))
    tag(d, 540, 340, "一块缅甸琥珀", WHITE, popk(t, AMBER_HIT) * (1 - pr(t, RULER - 0.1, RULER)), 60)
    stamp(d, t, RULER, "18 毫米", 540, 340, 130, YEL)

def s_twig(t, d):
    grad(d, (90, 130, 190), (40, 70, 120))
    for i in range(6): d.rect(0, 250 + i * 160, 1080, 254 + i * 160, fill=A(WHITE, 0.05))
    d.rect(-50, 1100, 1130, 1150, fill=A((170, 120, 80), 1)); d.rect(-50, 1150, 1130, 1950, fill=A((60, 70, 100), 1))
    amberblob(d, 330, 1060, 50, t, 1, 0.3); twig(d, 330, 1060, 45, 4, t); amberhl(d, 330, 1060, 50)
    sk = ease(pr(t, SCALES, SCALES + 0.5))
    jk = back(pr(t, JUMP, JUMP + 0.3)) * (1 - 0.6 * ease(pr(t, JUMP + 0.6, JUMP + 1.0)))
    person(d, 760, 1100, 130, t, "chill" if t < SCALES else ("scared" if t < JUMP else "scream"), jk)
    # magnifier
    mk = ease(pr(t, TWIG, MAG))
    lx = lerp(330, 450, mk); ly = lerp(1060, 690, mk); lr = lerp(50, 210, mk)
    d.line([(lx + lr * 0.7, ly + lr * 0.7), (lx + lr * 1.25, ly + lr * 1.25)], A((60, 50, 70), 1), max(10, lr * 0.16))
    d.circ(lx, ly, lr + 18, fill=A((200, 210, 230), 1))
    d.circ(lx, ly, lr, fill=A(AMB, 1)); d.circ(lx - lr * 0.1, ly - lr * 0.1, lr * 0.7, fill=A(AMB_L, 0.35))
    twig(d, lx, ly + 10, lr * 1.5, lr * 0.13, t, 1, sk)
    d.ell(lx - lr * 0.45, ly - lr * 0.5, lr * 0.3, lr * 0.12, A(WHITE, 0.5))
    if t > SCALES: rings(d, lx, ly, t, [SCALES], YEL, 0.8, 300)
    tag(d, 540, 340, "一根小树枝？", WHITE, popk(t, MAG) * (1 - pr(t, SCALES - 0.1, SCALES)), 64)
    stamp(d, t, SCALES, "有鳞片！", 540, 340, 130, YEL)
    if t > JUMP: bubble(d, 900, 600, "哇！", 1, WHITE, NAVYT, popk(t, JUMP), 44)
    if t >= SIL0: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.55))

def bigtail(d, x, y, L, w, t, a=1.0, dir=-1):
    pts = [(x - dir * L * u, y + math.sin(u * 3 + t * 2) * w * 0.4, u) for u in [i / 30 for i in range(31)]]
    drawtail(d, pts, w / 0.2, (130, 150, 70), (90, 100, 46), a)
    for x_, y_, u in pts[::2]:
        rr = w * (1 - u * 0.8)
        for k in (-1, 0, 1): d.arc(x_, y_ + k * rr * 0.45, rr * 0.3, rr * 0.25, 200, 340, A((220, 230, 160), 0.8 * a), max(2, rr * 0.08))
    d.ell(x, y, w * 0.25, w * 0.9, A(MUSC, a))
def s_boom(t, d):
    rays(d, t, (255, 204, 80), (240, 140, 40), n=22, cx=540, cy=820)
    dinosil(d, t, (205, 110, 30), 0.9)
    k = back(pr(t, BIG, BIG + 0.3))
    glow(d, 540, 820, 520, (255, 250, 200), 0.5 + 0.5 * pulse(t, [BIG], 2))
    amberblob(d, 540, 820, 240 * k, t, 1, 0.8)
    bigtail(d, 380, 820, 330 * k, 46 * k, t)
    amberhl(d, 540, 820, 240 * k)
    sparks(d, 540, 820, t, BIG, n=80, spd=1300, col=(255, 240, 170), seed=5, life=1.4)
    bk = ease(pr(t, BIG, BIG + 0.15))
    if bk > 0: d.rect(540 - 355 * bk, 220, 540 + 355 * bk, 495, fill=A((150, 36, 30), 0.92), r=40)
    stamp(d, t, BIG, "9900万年前的", 540, 292, 94, WHITE)
    stamp(d, t, BIG + 0.15, "蜥蜴尾巴！", 540, 422, 120, YEL)
    if t > BIG + 0.5: tag(d, 540, 1150, "白垩纪 · 缅甸北部", WHITE, ease(pr(t, BIG + 0.5, BIG + 0.8)), 40, (170, 80, 20))

def tail3d(d, x, y, L, w, ang, a=1.0):
    ca, sa = math.cos(ang), math.sin(ang)
    for i in range(14):
        u = i / 13; px = x + (u - 0.5) * L * ca; ry = w * (1 - u * 0.7)
        rx = max(4, ry * abs(sa) * 0.9 + 4)
        d.ell(px, y + (u - 0.5) * L * 0.15 * sa, rx, ry, outline=A(CYAN, a * (0.5 + 0.5 * (1 - u))), w=4)
    d.line([(x - L / 2 * ca, y - w - L * 0.075 * sa), (x + L / 2 * ca, y - w * 0.3 + L * 0.075 * sa)], A(CYAN, 0.6 * a), 3)
    d.line([(x - L / 2 * ca, y + w - L * 0.075 * sa), (x + L / 2 * ca, y + w * 0.3 + L * 0.075 * sa)], A(CYAN, 0.6 * a), 3)
    ex = x - L / 2 * ca
    flowerx(d, ex, y - L * 0.075 * sa, w * 0.95, [1] * 6, a * 0.85 * abs(ca) if abs(ca) > 0.2 else 0)
def s_ct(t, d):
    grad(d, (24, 80, 110), (8, 34, 56))
    for i in range(14): d.rect(i * 80, 0, i * 80 + 2, 1920, fill=A(CYAN, 0.06))
    for i in range(26): d.rect(0, i * 80, 1080, i * 80 + 2, fill=A(CYAN, 0.06))
    cx, cy = 540, 800
    amberblob(d, cx, cy, 190, t, 0.45, 0.2)
    ang = (t - CT) * 2.6
    ex, ey = cx + math.cos(ang) * 330, cy + math.sin(ang) * 330
    bx, by = cx - math.cos(ang) * 330, cy - math.sin(ang) * 330
    nx, ny = -math.sin(ang) * 120, math.cos(ang) * 120
    d.poly([(ex, ey), (bx + nx, by + ny), (bx - nx, by - ny)], A((140, 240, 255), 0.18))
    d.circ(cx, cy, 330, outline=A(CYAN, 0.3), w=4)
    d.rect(ex - 36, ey - 36, ex + 36, ey + 36, fill=A((220, 240, 250), 1), r=12); d.circ(ex, ey, 14, fill=A(CYAN, 1))
    d.rect(bx - 20, by - 50, bx + 20, by + 50, fill=A((120, 160, 190), 0.8), r=8)
    k3 = ease(pr(t, TAIL3D, TAIL3D + 0.5))
    if k3 < 1: twig(d, cx, cy, 260, 22, t, 1 - k3, 1)
    if k3 > 0:
        glow(d, cx, cy, 260, CYAN, 0.35 * k3)
        tail3d(d, cx, cy, 380, 72, (t - TAIL3D) * 1.5, k3)
    sy = cy - 200 + ((t - CT) * 260) % 400
    d.rect(cx - 230, sy - 3, cx + 230, sy + 3, fill=A(CYAN, 0.7))
    tag(d, 540, 340, "微 CT 扫描", CYAN, popk(t, SCAN) * (1 - pr(t, TAIL3D - 0.1, TAIL3D)), 64)
    stamp(d, t, TAIL3D, "不切开也看清", 540, 340, 100, WHITE)

def s_flower(t, d):
    grad(d, (255, 150, 180), (210, 80, 130))
    mk = ease(pr(t, MODERN, MODERN + 0.5))
    x = lerp(540, 360, mk); y = lerp(760, 760, mk); r = lerp(230, 150, mk)
    # tail body receding behind the cut face
    d.poly([(x - r * 0.9, y - r * 0.45), (x + r * 1.2, y - r * 1.6), (x + r * 1.5, y - r * 1.25), (x + r * 0.9, y + r * 0.45)], A((130, 150, 70), 1))
    d.poly([(x + r * 0.2, y - r * 0.9), (x + r * 1.2, y - r * 1.6), (x + r * 1.5, y - r * 1.25), (x + r * 0.6, y - r * 0.2)], A((160, 180, 90), 0.6))
    ks = [ease(back(pr(t, h, h + 0.25))) for h in PETALS]
    flowerx(d, x, y, r, ks, 1, (130, 150, 70))
    for h in PETALS[-1:]: rings(d, x, y, t, [h], WHITE, 0.6, 300)
    if mk > 0:
        k2 = popk(t, MODERN + 0.2)
        if k2 > 0:
            d.poly([(720 + 150 * k2 * 0.9, 760 - 150 * k2 * 0.45), (720 + 150 * k2 * 1.0, 760 - 150 * k2 * 1.4), (720 + 150 * k2 * 1.25, 760 - 150 * k2 * 1.15), (720 + 150 * k2 * 0.6, 760 + 150 * k2 * 0.5)], A(LIZ, 1))
            flowerx(d, 720, 760, 150 * k2, [1] * 6, 1, LIZ)
        tag(d, 360, 980, "9900 万年前", WHITE, mk, 38)
        tag(d, 720, 980, "今天的蜥蜴", WHITE, k2, 38)
        if t > MATCH: d.text(540, 760, "=", int(110 * popk(t, MATCH)), A(WHITE, 1), k=1)
    tag(d, 540, 340, "花瓣样的肌肉", WHITE, popk(t, PETALS[0]) * (1 - pr(t, MATCH - 0.1, MATCH)), 64, (190, 50, 90))
    stamp(d, t, MATCH, "一模一样！", 540, 340, 130, WHITE)

def tailseg(d, x, y0, y1, w, t, kind, a=1.0):
    col, dk = (130, 150, 70), (90, 100, 46)
    d.rect(x - w * 0.6 + 6, y0 - 40, x + w * 0.6 + 6, y1, fill=A(dk, a), r=w * 0.5)
    d.rect(x - w * 0.6, y0 - 40, x + w * 0.6 - 6, y1, fill=A(col, a), r=w * 0.5)
    for i in range(5): d.rect(x - w * 0.6, y0 + i * 50, x + w * 0.6 - 6, y0 + i * 50 + 8, fill=A(mix(col, WHITE, 0.3), 0.6 * a))
    if kind == "clean":
        d.rect(x - w * 0.6, y1 - 40, x + w * 0.6, y1, fill=A(col, a))
        d.ell(x, y1, w * 0.6, w * 0.22, A((250, 200, 190), a))
        for i in range(6):
            ang = i / 6 * 2 * math.pi
            rell(d, x + math.cos(ang) * w * 0.28, y1 + math.sin(ang) * w * 0.1, w * 0.18, w * 0.06, ang, A(MUSC, a))
        face(d, x, y0 + 60, w * 0.55, "proud", a)
    else:
        r2 = random.Random(8)
        pts = [(x - w * 0.6, y1 - 30)] + [(x - w * 0.6 + i * w * 1.2 / 9, y1 + (r2.uniform(10, 60) if i % 2 else r2.uniform(-30, 0))) for i in range(10)] + [(x + w * 0.6, y1 - 30)]
        d.poly(pts, A(col, a))
        for i in range(5):
            px = x - w * 0.5 + i * w * 0.25; d.line([(px, y1), (px + r2.uniform(-20, 20), y1 + r2.uniform(40, 90))], A(MUSC_D, a), 10)
        face(d, x, y0 + 60, w * 0.55, "dizzy", a)
def check(d, x, y, s, k, col, a=1.0):
    p = [(x - s, y), (x - s * 0.3, y + s * 0.7), (x + s, y - s * 0.8)]
    if k <= 0: return
    if k < 0.5: d.line([p[0], (lerp(p[0][0], p[1][0], k * 2), lerp(p[0][1], p[1][1], k * 2))], A(col, a), s * 0.28)
    else: d.line([p[0], p[1], (lerp(p[1][0], p[2][0], (k - 0.5) * 2), lerp(p[1][1], p[2][1], (k - 0.5) * 2))], A(col, a), s * 0.28)
def cross(d, x, y, s, k, col, a=1.0):
    if k <= 0: return
    d.line([(x - s, y - s), (x - s + 2 * s * min(1, k * 2), y - s + 2 * s * min(1, k * 2))], A(col, a), s * 0.28)
    if k > 0.5: d.line([(x + s, y - s), (x + s - 2 * s * (k - 0.5) * 2, y - s + 2 * s * (k - 0.5) * 2)], A(col, a), s * 0.28)
def s_clean(t, d):
    d.rect(-50, -50, 540, 1970, fill=A((90, 190, 130), 1)); d.rect(540, -50, 1130, 1970, fill=A((235, 110, 100), 1))
    d.rect(536, 0, 544, 1920, fill=A(WHITE, 0.6))
    sh = shake(t, 10 * pulse(t, [CROSS], 6), 70)
    tailseg(d, 360, 620, 900, 150, t, "clean")
    tailseg(d, 720 + sh[0], 620, 900, 150, t, "torn")
    tag(d, 360, 520, "整齐对称", WHITE, popk(t, CLEAN + 0.2), 44, (40, 120, 70))
    tag(d, 720, 520, "撕裂伤口", WHITE, popk(t, CLEAN + 0.4), 44, (170, 40, 40))
    check(d, 360, 1070, 70, ease(pr(t, TICK, TICK + 0.3)), WHITE)
    cross(d, 720, 1060, 60, ease(pr(t, CROSS, CROSS + 0.3)), WHITE)
    stamp(d, t, SELF, "自己断的！", 540, 340, 130, WHITE)

def vertebra(d, x, y, s, a=1.0):
    d.rect(x - s * 0.5, y - s * 0.3, x + s * 0.5, y + s * 0.3, fill=A(BONE_D, a), r=s * 0.15)
    d.rect(x - s * 0.46, y - s * 0.3, x + s * 0.42, y + s * 0.24, fill=A(BONE, a), r=s * 0.15)
    d.poly([(x - s * 0.15, y - s * 0.3), (x, y - s * 0.8), (x + s * 0.15, y - s * 0.3)], A(BONE, a))
    d.poly([(x - s * 0.15, y + s * 0.3), (x - s * 0.05, y + s * 0.7), (x + s * 0.15, y + s * 0.3)], A(BONE_D, a))
def s_old(t, d):
    grad(d, (236, 206, 150), (196, 150, 100))
    r2 = random.Random(1)
    for i in range(30): d.circ(r2.uniform(0, 1080), r2.uniform(250, 1500), r2.uniform(8, 30), fill=A((170, 130, 90), 0.25))
    d.rect(195, 600, 525, 940, fill=A((150, 130, 110), 1), r=40); d.rect(205, 610, 515, 920, fill=A((170, 150, 128), 1), r=34)
    for i in range(4): vertebra(d, 255 + i * 82, 770, 80 - i * 6)
    if t > OLD_HIT:
        k = ease(pr(t, OLD_HIT, OLD_HIT + 0.3)); xx = 255 + 82
        for j in range(8):
            yy = 660 + j * 30
            if yy < 660 + 240 * k: d.rect(xx - 3, yy, xx + 3, yy + 16, fill=A(RED, 1))
        tag(d, xx, 630, "预裂线", RED, popk(t, OLD_HIT + 0.15), 34, WHITE)
    tag(d, 360, 500, "旧化石", WHITE, popk(t, OLD + 0.2), 44)
    if t > OLD_LAB: tag(d, 360, 1030, "只能说明：能断", (120, 110, 100), popk(t, OLD_LAB), 38, WHITE)
    tag(d, 720, 500, "这块琥珀", WHITE, popk(t, OLD + 0.5), 44)
    uk = popk(t, UPG)
    amberblob(d, 720, 770, 140, t, 1, 0.3 + 0.5 * uk)
    bigtail(d, 640, 770, 170, 22, t)
    amberhl(d, 720, 770, 140)
    if t > UPG:
        tag(d, 720, 1030, "证明：真断了", GOLD, uk, 38)
        d.poly([(720, 940 - 30 * uk), (690, 975), (750, 975)], A(GOLD, uk))
        sparks(d, 720, 770, t, UPG, n=40, spd=800, col=(255, 230, 120), seed=12)
    stamp(d, t, UPG, "升级：真断了！", 540, 340, 100, (190, 60, 20))

def card(d, y, s, icon, k, t, a=1.0):
    if k <= 0: return
    x0, x1 = 210, 870; xo = (1 - k) * 300
    d.rect(x0 + xo, y - 95, x1 + xo, y + 95, fill=A((255, 250, 240), a), r=36)
    d.rect(x0 + xo, y + 75, x1 + xo, y + 95, fill=A((210, 200, 230), a), r=10)
    ix = 310 + xo
    if icon == 0:
        amberblob(d, ix, y, 62, t, a, 0.2); looseTail(d, ix + 30, y + 10, 40, t, 0.6, 1, (130, 150, 70), (90, 100, 46), a, L=2.0)
    elif icon == 1: monster(d, ix - 10, y, 62, t, 0.6, "angry", a=a)
    else: lizard(d, ix + 10, y + 50, 50, t, "sad", 0.0, 1, a=a)
    d.text(400 + xo, y, s, 44, A(NAVYT, a), anchor="lm", k=1)
    d.circ(820 + xo, y - 50, 30, fill=A((140, 90, 220), a)); d.text(820 + xo, y - 50, "?", 40, A(WHITE, a), k=1)
def s_myst(t, d):
    grad(d, (80, 60, 160), (34, 22, 80))
    for i in range(12):
        u = (t * 0.12 + i / 12) % 1
        d.text((i * 197) % 1000 + 40, 1600 - u * 1500, "?", 60 + (i % 3) * 30, A(WHITE, 0.12 * math.sin(u * math.pi)), k=1)
    sh = 6 * pulse(t, [MYST_HIT], 5) * math.sin(t * 60)
    for i, (s, h) in enumerate(zip(["被树脂粘住了？", "被捕食者攻击？", "后来活下来了吗？"], CARDS)):
        card(d, 560 + i * 230 + sh, s, i, ease(pr(t, h, h + 0.3)), t)
    stamp(d, t, MYST_HIT, "还是个谜", 540, 340, 130, YEL)

def s_now(t, d):
    d.rect(-50, -50, 540, 1970, fill=A((240, 150, 70), 1)); d.rect(540, -50, 1130, 1970, fill=A((90, 160, 230), 1))
    for i in range(5):   # ferns left
        fx_ = 120 + i * 100; d.line([(fx_, 1160), (fx_ + 30, 900 - (i % 2) * 80)], A((60, 130, 60), 0.6), 14)
        for j in range(5): d.ell(fx_ + 8 + j * 5, 1100 - j * 50 - (i % 2) * 20, 40, 12, A((60, 130, 60), 0.6))
    for r_ in range(10):   # brick wall right
        for c in range(6):
            x = 540 + c * 110 + (55 if r_ % 2 else 0) - 55; y = 560 + r_ * 62
            d.rect(x + 4, y + 4, x + 106, y + 58, fill=A((120, 180, 240), 0.5), r=6)
    ground(d, 1160, (120, 80, 50), (110, 170, 80)); d.rect(540, 1160, 1130, 1970, fill=A((90, 100, 120), 1))
    d.rect(536, 0, 544, 1920, fill=A(WHITE, 0.7))
    k = popk(t, NOW_HIT); fk = t > FLICK
    for x, col, dk, h in [(410, OLDL, OLDL_D, 0), (765, LIZ, LIZ_D, 0.1)]:
        lizard(d, x, 1160, 88 * k, t, "proud" if fk else "happy", 0.0 if fk else 1.0, 1, col=col, dk=dk, hop=16 * pulse(t, [FLICK], 7))
        if fk:
            looseTail(d, x - 88 * 0.62 - 20, 1118, 88, t, 0.5 + 0.8 * pulse(t, [FLICK], 3), 1, col, dk, L=1.6)
            bang(d, t, FLICK, x - 110, 1000, "啪！", 70, WHITE)
    tag(d, 360, 470, "9900 万年前", WHITE, popk(t, NOW + 0.1), 44, (170, 80, 20))
    tag(d, 720, 470, "今天", WHITE, popk(t, NOW + 0.3), 44, (40, 90, 170))
    stamp(d, t, YEARS, "快 1 亿年！", 540, 320, 120, WHITE)

def s_end(t, d):
    rays(d, t, (200, 240, 120), (120, 200, 90), n=16, cx=540, cy=1100)
    ground(d, 1150)
    st = 0.42 * ease(pr(t, BUBS[0], BUBS[0] + 0.6))
    lizard(d, 620, 1150, 190, t, "happy", 0.0, -1, stub=st, vsign=ease(pr(t, OUTRO, OUTRO + 0.4)), hop=14 * pulse(t, BUBS, 7))
    if t > BUBS[0]: rings(d, 620 + 190 * 0.62 + 50, 1070, t, [BUBS[0]], WHITE, 0.7, 160); sparks(d, 800, 1060, t, BUBS[0], n=24, spd=500, col=WHITE, seed=21)
    bubble(d, 220, 640, "新尾巴还能再长！", -1, WHITE, NAVYT, popk(t, BUBS[1]), 46)
    stamp(d, t, BUBS[2], "断尾保命术", 540, 340, 120, WHITE)
    d.rect(250, 1270, 830, 1372, fill=A(WHITE, 0.55), r=20)
    d.text(540, 1300, "Nasser et al., Palaeontol. Electron. (2026)", 26, A(NAVYT, 0.9))
    d.text(540, 1342, "DOI 10.26879/1706", 26, A(NAVYT, 0.9))
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

def subs(t, d):
    if t >= OUTRO: return
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

SECS = [(0, HOOK_END, s_hook), (TWIST, Q, s_twist), (Q, AMBER, s_q), (AMBER, TWIG, s_amber), (TWIG, BIG, s_twig),
        (BIG, CT, s_boom), (CT, FLOWER, s_ct), (FLOWER, CLEAN, s_flower), (CLEAN, OLD, s_clean), (OLD, MYST, s_old),
        (MYST, NOW, s_myst), (NOW, OUTRO, s_now), (OUTRO, 99, s_end)]
CUTS = [TWIST, Q, AMBER, TWIG, BIG, CT, FLOWER, CLEAN, OLD, MYST, NOW, OUTRO]
def cam(t):
    z = 1.0 + 0.05 * pulse(t, HITS, 7) + 0.12 * pulse(t, [HOOK_HIT, BIG], 4)
    for a, b in RISERS:
        if a <= t < b: z += 0.12 * eio(pr(t, a, b))
    amp = 28 * pulse(t, [HOOK_HIT, BIG], 4) + 5 * pulse(t, HITS, 6)
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx, 900 + sy
def frame(t):
    img = Image.new("RGB", (W, H), (30, 20, 50)); d = D(img)
    for a, b, sf in SECS:
        if a <= t < b: sf(t, d); break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.08: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - (t - c) / 0.08)))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.1f}.png")
    elif sys.argv[1] == "subw":
        d = D(Image.new("RGB", (W // 4, H // 4)))
        for a, b, s in SUBS:
            for x in s.split("|"): print(int(d.tlen(x, 52, 1)), x)
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
