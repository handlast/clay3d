import math, random, sys, subprocess
from PIL import Image
from base import *
from fx import glow, sparks, shake, stamp, flash, grad, rays, face
from cues import *

GERM = (120, 220, 120); GERM2 = (255, 170, 80); GERM3 = (170, 140, 255)
GERMS = [GERM, GERM2, GERM3, (90, 200, 230)]
SKIN = (255, 205, 160); SHIRT = (70, 130, 240); RBCC = (230, 60, 70); NUC = (150, 110, 230)
MITOC = (255, 150, 60); APPLEC = (225, 50, 50); PINK = (255, 110, 180); GOLD = (255, 190, 60)

def shade(c, k=0.35): return mix(c, (0, 0, 0), k)
def rpoly(cx, cy, rx, ry, ang, n=22):
    ca, sa = math.cos(ang), math.sin(ang)
    out = []
    for k in range(n):
        u = 2 * math.pi * k / n
        px, py = rx * math.cos(u), ry * math.sin(u)
        out.append((cx + px * ca - py * sa, cy + px * sa + py * ca))
    return out
def capsule(d, x, y, L, r, ang, col, a=1.0):
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    for k in range(12):
        u = -math.pi / 2 + math.pi * k / 11
        pts.append((L / 2 + r * math.cos(u), r * math.sin(u)))
    for k in range(12):
        u = math.pi / 2 + math.pi * k / 11
        pts.append((-L / 2 + r * math.cos(u), r * math.sin(u)))
    d.poly([(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts], A(col, a))

def germ(d, x, y, r, t, col=GERM, kind="chill", ang=0.0, a=1.0, seed=0):
    ca, sa = math.cos(ang), math.sin(ang)
    for k in range(3):  # flagella
        pts = []
        for i in range(8):
            u = i / 7
            lx = -r * 1.1 - u * r * 1.2; ly = (k - 1) * r * 0.4 + math.sin(t * 10 + u * 5 + seed + k) * r * 0.18 * u
            pts.append((x + lx * ca - ly * sa, y + lx * sa + ly * ca))
        d.line(pts, A(shade(col, 0.2), a * 0.8), max(2, r * 0.08))
    capsule(d, x + r * 0.05, y + r * 0.08, r * 1.2, r * 0.8, ang, shade(col), a)
    capsule(d, x, y, r * 1.2, r * 0.76, ang, col, a)
    d.ell(x - r * 0.45, y - r * 0.38, r * 0.3, r * 0.14, A(WHITE, 0.45 * a))
    face(d, x, y, r * 0.75, kind, a)

def kid(d, x, y, s, t, kind="chill", a=1.0, arms=0.0):
    d.ell(x, y + 1.25 * s, 0.7 * s, 0.12 * s, A((0, 0, 0), 0.25 * a))
    for sd in (-1, 1):
        d.line([(x + sd * 0.4 * s, y + 0.15 * s), (x + sd * (0.75 + 0.1 * arms) * s, y + (0.55 - 0.9 * arms) * s)], A(shade(SHIRT, 0.1), a), 0.2 * s)
        d.rect(x + sd * 0.22 * s - 0.11 * s, y + 0.7 * s, x + sd * 0.22 * s + 0.11 * s, y + 1.2 * s, fill=A((50, 60, 90), a), r=0.08 * s)
    d.rect(x - 0.45 * s, y - 0.05 * s, x + 0.45 * s, y + 0.8 * s, fill=A(shade(SHIRT, 0.25), a), r=0.25 * s)
    d.rect(x - 0.43 * s, y - 0.08 * s, x + 0.41 * s, y + 0.76 * s, fill=A(SHIRT, a), r=0.24 * s)
    d.circ(x + 0.03 * s, y - 0.47 * s, 0.45 * s, fill=A(shade(SKIN, 0.2), a)); d.circ(x, y - 0.5 * s, 0.44 * s, fill=A(SKIN, a))
    d.ell(x, y - 0.86 * s, 0.4 * s, 0.17 * s, A((60, 40, 30), a))
    d.ell(x - 0.18 * s, y - 0.72 * s, 0.1 * s, 0.05 * s, A(WHITE, 0.4 * a))
    face(d, x, y - 0.45 * s, 0.4 * s, kind, a)
    for sd in (-1, 1): d.ell(x + sd * 0.27 * s, y - 0.33 * s, 0.07 * s, 0.04 * s, A((255, 120, 120), 0.5 * a))

def rbc(d, x, y, r, a=1.0):
    d.circ(x + r * 0.06, y + r * 0.08, r, fill=A(shade(RBCC), a)); d.circ(x, y, r, fill=A(RBCC, a))
    d.ell(x, y, r * 0.5, r * 0.42, A(shade(RBCC, 0.2), a)); d.ell(x - r * 0.4, y - r * 0.45, r * 0.25, r * 0.12, A(WHITE, 0.4 * a))
def hcell(d, x, y, r, a=1.0, col=(255, 190, 200)):
    d.circ(x + r * 0.05, y + r * 0.06, r, fill=A(shade(col, 0.25), a)); d.circ(x, y, r, fill=A(col, a))
    d.circ(x + r * 0.1, y, r * 0.35, fill=A(NUC, a)); d.ell(x - r * 0.4, y - r * 0.45, r * 0.25, r * 0.12, A(WHITE, 0.4 * a))
def mito(d, x, y, r, ang, t, a=1.0, glowk=0.0, kind=None):
    if glowk > 0: glow(d, x, y, r * 2.0, MITOC, glowk)
    d.poly(rpoly(x + r * 0.06, y + r * 0.08, r * 1.3, r * 0.7, ang), A(shade(MITOC), a)); d.poly(rpoly(x, y, r * 1.3, r * 0.7, ang), A(MITOC, a))
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    for i in range(13):
        lx = -r + i * r / 6; ly = (r * 0.38) * (1 if i % 2 else -1)
        pts.append((x + lx * ca - ly * sa, y + lx * sa + ly * ca))
    d.line(pts, A((255, 210, 150), a), max(2, r * 0.1))
    if kind: face(d, x, y, r * 0.6, kind, a)
def apple(d, x, y, r, a=1.0):
    d.circ(x - r * 0.35 + r * .06, y + r * .08, r * 0.8, fill=A(shade(APPLEC), a)); d.circ(x + r * 0.35 + r * .06, y + r * .08, r * 0.8, fill=A(shade(APPLEC), a))
    d.circ(x - r * 0.35, y, r * 0.8, fill=A(APPLEC, a)); d.circ(x + r * 0.35, y, r * 0.8, fill=A(APPLEC, a))
    d.line([(x, y - r * 0.7), (x + r * 0.1, y - r * 1.15)], A((110, 70, 40), a), r * 0.1)
    d.ell(x + r * 0.35, y - r * 1.05, r * 0.3, r * 0.13, A(LEAF, a)); d.ell(x - r * 0.5, y - r * 0.35, r * 0.2, r * 0.12, A(WHITE, 0.45 * a))
def toilet(d, x, y, s, t, swirl=0.0, a=1.0):
    d.rect(x - 0.55 * s, y - 1.3 * s, x + 0.55 * s, y - 0.55 * s, fill=A((215, 225, 235), a), r=0.12 * s)
    d.rect(x - 0.45 * s, y + 0.2 * s, x + 0.45 * s, y + 0.9 * s, fill=A((205, 215, 228), a), r=0.12 * s)
    d.ell(x, y, 0.85 * s, 0.38 * s, A((230, 238, 245), a)); d.ell(x, y, 0.65 * s, 0.26 * s, A((90, 170, 230), a))
    if swirl > 0:
        for i in range(10):
            ang = t * 12 + i * 0.63; rr = 0.6 * s * (1 - i / 10)
            d.circ(x + math.cos(ang) * rr, y + math.sin(ang) * rr * 0.4, 0.04 * s, fill=A(WHITE, swirl * 0.8))
    d.rect(x + 0.35 * s, y - 1.2 * s, x + 0.5 * s, y - 1.12 * s, fill=A((160, 170, 185), a), r=6)

def bigtext(d, x, y, s, size, col, a=1.0): d.text(x, y, s, size, A(col, a), k=1)
def bars(d, t, b_val, h_val, y=640, a=1.0):
    mx = 40.0
    for i, (nm, v, col) in enumerate((("细菌", b_val, GERM), ("人体细胞", h_val, PINK))):
        yy = y + i * 120
        d.text(150, yy, nm, 44, A(WHITE, a), k=1)
        w = 640 * v / mx
        d.rect(280, yy - 36, 280 + 640, yy + 36, fill=A((255, 255, 255), 0.08 * a), r=36)
        d.rect(280, yy - 36, 280 + max(72, w), yy + 36, fill=A(col, a), r=36)
        d.text(280 + max(72, w) - 80, yy, f"{v:.0f}", 44, A((20, 30, 30), a), k=1)

# ---------------- scenes ----------------
SW = [(random.Random(i).uniform(560, 760), random.Random(i + 99).uniform(800, 1500), random.Random(i + 7).uniform(0, 6.28)) for i in range(40)]
def w_hook(t, d):
    grad(d, (30, 24, 60), (8, 6, 20)); rays(d, t, (50, 40, 100), (16, 12, 40), 20, 540, 1150)
    kid(d, 540, 1150, 330, t, "scared" if t > SPLIT else "chill")
    k = ease(pr(t, SPLIT, SPLIT + 0.3))
    if k > 0:
        d.rect(540, 820, 700, 1560, fill=A((40, 120, 60), 0.35 * k))
        for i, (gx, gy, ang) in enumerate(SW):
            if (gx - 540) / 170 * 740 > (gy - 820) * 0 and abs(gy - 1150) < 400:
                germ(d, gx + 6 * math.sin(t * 5 + i), gy + 6 * math.cos(t * 4 + i), 26 * k, t, GERMS[i % 4], "happy" if i % 3 else "chill", ang, seed=i)
        d.line([(540, 760), (540, 1600)], A(WHITE, k), 10)
        sparks(d, 540, 1150, t, SPLIT, 60, 1400, GERM, 1, 3, 1.0)
def u_hook(t, d):
    bigtext(d, 540, 280, "你身上", 130, WHITE)
    bigtext(d, 540, 470, "一半是细菌", int(180 * (1 + 0.08 * pulse(t, [SPLIT], 7))), YEL)
    flash(d, t, [SPLIT], WHITE, 0.9)

def w_myth(t, d):
    grad(d, (20, 40, 50), (6, 12, 16))
    cr = ease(pr(t, WRONG, WRONG + 0.6))
    # scale: 1 cell vs 10 germs
    tilt = 0.25 * ease(pr(t, TEN, TEN + 0.4)) * (1 - cr)
    cx, cy = 540, 1150
    d.rect(530, cy, 550, 1450, fill=A((150, 160, 180), 1)); d.poly([(470, 1460), (610, 1460), (540, 1400)], A((150, 160, 180), 1))
    lx, ly = cx - 330 * math.cos(tilt), cy - 330 * math.sin(tilt); rx, ry = cx + 330 * math.cos(tilt), cy + 330 * math.sin(tilt)
    d.line([(lx, ly), (rx, ry)], A((190, 200, 220), 1), 16)
    hcell(d, lx, ly - 80, 70)
    n = int(10 * ease(pr(t, TEN - 0.6, TEN)))
    for i in range(n):
        germ(d, rx - 120 + (i % 4) * 80, ry - 50 - (i // 4) * 70, 34, t, GERMS[i % 4], "proud", 0.2 * i, seed=i)
    if t > NAPKIN:
        k = back(pr(t, NAPKIN, NAPKIN + 0.3)) * (1 - cr)
        if k > 0.01:
            x, y = 540, 800
            ang = 0.08 + cr * 3
            d.poly(rpoly(x, y, 330 * k, 180 * k, ang, 4), A((250, 240, 210), 1))
            d.text(x, y - 50 * k, "1972", int(70 * k) + 1, A((40, 40, 60), 1), k=1)
            d.text(x, y + 50 * k, "一句话估算", int(56 * k) + 1, A((40, 40, 60), 1), k=1)
def u_myth(t, d):
    if t < WRONG:
        bigtext(d, 540, 290, "细菌是你的", 96, WHITE)
        if t > TEN: bigtext(d, 540, 460, "10 倍？", int(170 * back(pr(t, TEN, TEN + 0.2))) + 1, YEL)
    else:
        stamp(d, t, WRONG, "算错了", 540, 380, 200, RED)
    flash(d, t, [WRONG], RED, 0.4)

def w_count(t, d):
    grad(d, (16, 30, 60), (4, 8, 20))
    for i in range(60):
        rnd = random.Random(i); x = rnd.uniform(0, 1080); y = (rnd.uniform(0, 1920) - t * rnd.uniform(40, 120)) % 1920
        d.circ(x, y, rnd.uniform(3, 7), fill=A(CYAN, 0.2))
    u = eio(pr(t, CNT[0], CNT[1]))
    hcell(d, 300, 1050, 140 * (1 + 0.06 * math.sin(t * 6)))
    germ(d, 780, 1050, 120 * (1 + 0.06 * math.sin(t * 6 + 1)), t, GERM, "proud" if t > EVEN else "chill")
    d.text(300, 1280, "人体细胞", 50, A(WHITE, 1), k=1); d.text(780, 1280, "细菌", 50, A(WHITE, 1), k=1)
    d.text(300, 1380, f"{30 * u:.0f} 万亿", 78, A(PINK, 1), k=1); d.text(780, 1380, f"{38 * u:.0f} 万亿", 78, A(GERM, 1), k=1)
def u_count(t, d):
    if t < EVEN:
        bigtext(d, 540, 290, "2016 · 重新数", 110, WHITE)
    else:
        stamp(d, t, EVEN, "差不多 1 : 1", 540, 330, 150, YEL)
    flash(d, t, [EVEN], WHITE, 0.6)

def w_rbc(t, d):
    if t < COLON:
        grad(d, (60, 14, 24), (16, 4, 8))
        if t < NONUC:
            f = int(84 * eio(pr(t, RBC_FILL[0], RBC_FILL[1])))
            for i in range(100):
                x = 140 + (i % 10) * 89; y = 700 + (i // 10) * 89
                if i < f: rbc(d, x, y, 36)
                else: d.circ(x, y, 34, fill=A((255, 255, 255), 0.12))
        else:
            k = back(pr(t, NONUC, NONUC + 0.3))
            rbc(d, 540, 1100, 300 * k + 1)
            if k > 0.5:
                d.text(540, 1100, "?", 200, A(WHITE, 0.9), k=1)
    else:
        grad(d, (50, 30, 20), (14, 8, 6))
        kid(d, 540, 1150, 340, t, "sus")
        u = ease(pr(t, COLON, COLON + 0.4))
        pts = [(450, 1390), (450, 1240), (630, 1240), (630, 1390), (560, 1400)]
        d.line(pts, A((200, 120, 90), u), 50)
        for i in range(24):
            s_ = (i / 24 + t * 0.15) % 1
            seg = s_ * 4; j = min(3, int(seg)); fr = seg - j
            x = lerp(pts[j][0], pts[j + 1][0], fr); y = lerp(pts[j][1], pts[j + 1][1], fr)
            glow(d, x, y, 30, GERM, u * 0.7, 3); d.circ(x, y, 9, fill=A(GERMS[i % 4], u))
def u_rbc(t, d):
    if t < NONUC:
        bigtext(d, 540, 280, "你的细胞里", 90, WHITE)
        bigtext(d, 540, 450, f"{int(84 * eio(pr(t, RBC_FILL[0], RBC_FILL[1])))}% 是红细胞", 120, RBCC if t < RBC_FILL[1] else YEL)
    elif t < COLON:
        stamp(d, t, NONUC, "没有细胞核", 540, 350, 150, YEL)
    else:
        stamp(d, t, COLON, "细菌住在大肠", 540, 350, 130, GERM)
    flash(d, t, [NONUC, COLON], WHITE, 0.6)

def w_poop(t, d):
    grad(d, (30, 60, 90), (8, 16, 30))
    for i in range(0, 1080, 120):
        for j in range(1200, 1920, 120): d.rect(i + 4, j + 4, i + 116, j + 116, fill=A((50, 80, 110), 1))
    sw = pr(t, FLUSH, FLUSH + 1.6) * (1 - pr(t, FLIP + 1, FLIP + 2))
    if t < FLIP:
        toilet(d, 540, 1350, 300, t, sw)
        if t > FLUSH:
            sparks(d, 540, 1350, t, FLUSH, 40, 900, (150, 210, 255), 2, 4, 1.2)
            for i in range(10):
                u = pr(t, FLUSH + i * 0.1, FLUSH + 1.2 + i * 0.1)
                if 0 < u < 1:
                    ang = i * 0.7 + u * 10; rr = 200 * (1 - u)
                    germ(d, 540 + math.cos(ang) * rr, 1350 + math.sin(ang) * rr * 0.4, 30 * (1 - u * 0.7), t, GERMS[i % 4], "scream", ang, seed=i)
    else:
        toilet(d, 540, 1400, 260, t, 0, 0.5)
        k = back(pr(t, FLIP, FLIP + 0.3))
        kid(d, 540, 1250, 280 * k + 1, t, "proud", arms=1.0)
        sparks(d, 540, 1050, t, FLIP, 70, 1500, YEL, 4, 3, 1.0)
def u_poop(t, d):
    b = lerp(38, 25.3, ease(pr(t, FLUSH, FLUSH + 1.4)))
    bars(d, t, b, 30, y=620)
    if t < FLIP: bigtext(d, 540, 300, "拉一次", 120, WHITE)
    else: stamp(d, t, FLIP, "拉完更像人", 540, 330, 150, YEL)
    if t > FLUSH: d.text(540, 900, "大肠内容物 -1/3", 52, A(CYAN, ease(pr(t, FLUSH, FLUSH + 0.3))), k=1)
    flash(d, t, [FLIP], WHITE, 0.9)
    if SILENCES[0][0] <= t < FLIP: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.35))

def w_mass(t, d):
    grad(d, (50, 40, 20), (14, 10, 6))
    u = ease(pr(t, APPLE, APPLE_HIT))
    rnd = random.Random(2)
    for i in range(40):
        gx = 540 + rnd.uniform(-300, 300); gy = 1100 + rnd.uniform(-260, 260)
        x = lerp(gx, 540, u); y = lerp(gy, 1150, u)
        if u < 0.98: germ(d, x, y, 30 * (1 - u * 0.6), t, GERMS[i % 4], "chill", i, seed=i)
    if t > APPLE_HIT:
        k = back(pr(t, APPLE_HIT, APPLE_HIT + 0.3))
        glow(d, 540, 1150, 400 * k, GOLD, 0.6); apple(d, 540, 1150 - 30 * abs(math.sin((t - APPLE_HIT) * 5)) * (1 - pr(t, APPLE_HIT, APPLE_HIT + 1.5)), 200 * k + 1)
        sparks(d, 540, 1150, t, APPLE_HIT, 50, 1200, GOLD, 5, 3, 1.0)
def u_mass(t, d):
    if t < APPLE_HIT: bigtext(d, 540, 300, "加起来多重？", 110, WHITE)
    else:
        bigtext(d, 540, 290, "0.2 公斤", int(170 * back(pr(t, APPLE_HIT, APPLE_HIT + 0.2))) + 1, YEL)
        d.text(540, 460, "≈ 一个苹果", 70, A(WHITE, ease(pr(t, APPLE_HIT + 0.3, APPLE_HIT + 0.6))), k=1)
    flash(d, t, [APPLE_HIT], WHITE, 0.6)

MPOS = [(random.Random(i).uniform(-0.75, 0.75), random.Random(i + 50).uniform(-0.75, 0.75), random.Random(i + 9).uniform(0, 3.1)) for i in range(40)]
MPOS = [p for p in MPOS if p[0] ** 2 + p[1] ** 2 < 0.6 and (p[0] - 0.1) ** 2 + p[1] ** 2 > 0.12][:16]
def w_mito(t, d):
    grad(d, (40, 16, 50), (10, 4, 14))
    z = 1 + 1.4 * eio(pr(t, ZOOM, MITO_HIT - 0.3))
    R = 330 * z
    cx, cy = 540, 1100
    d.circ(cx + 10, cy + 14, R, fill=A((180, 90, 120), 1)); d.circ(cx, cy, R, fill=A((250, 170, 190), 1))
    d.circ(cx + 0.1 * R, cy, 0.3 * R, fill=A(NUC, 1)); d.ell(cx - 0.45 * R, cy - 0.5 * R, 0.2 * R, 0.08 * R, A(WHITE, 0.35))
    g = ease(pr(t, MITO_HIT, MITO_HIT + 0.3))
    for i, (px, py, ang) in enumerate(MPOS):
        x, y = cx + px * R, cy + py * R
        if -60 < x < 1140 and 300 < y < 1650:
            mito(d, x, y, 0.09 * R, ang + 0.3 * math.sin(t * 2 + i), t, glowk=g, kind=("happy" if i % 2 else "chill") if g > 0.5 else None)
def u_mito(t, d):
    if t < MITO_HIT:
        bigtext(d, 540, 290, "细胞里还有", 96, WHITE)
        bigtext(d, 540, 450, "线粒体", int(150 * back(pr(t, MITO + 0.3, MITO + 0.5))) + 1, MITOC)
    else:
        stamp(d, t, MITO_HIT, "祖上是细菌", 540, 350, 160, YEL)
    flash(d, t, [MITO_HIT], WHITE, 0.6)

def bubble(d, x, y, s, side, col, tcol, a, size=50):
    w = d.tlen(s, size) + 70
    x0 = x - w if side > 0 else x
    d.rect(x0, y - size * 1.1, x0 + w, y + size * 1.1, fill=A(col, a), r=40)
    d.text(x0 + w / 2, y, s, size, A(tcol, a), k=1)
def w_end(t, d):
    grad(d, (24, 26, 34), (10, 11, 16))
    d.rect(0, 160, 1080, 260, fill=A((40, 42, 54), 1)); d.text(540, 210, "同学群（48）", 44, A(WHITE, 0.9), k=1)
def u_end(t, d):
    d.text(540, 380, "明天这样说 ↓", 80, A(YEL, ease(pr(t, OUTRO, OUTRO + 0.3))), k=1)
    for i, (t0, s) in enumerate(((BUB1, "你知道你一半是细菌吗"), (BUB2, "拉完屎你就更像人了"))):
        if t > t0:
            k = back(pr(t, t0, t0 + 0.25))
            bubble(d, 1010, 640 + i * 190, s, 1, (120, 220, 120), (20, 40, 20), min(1, k), int(66 * (0.7 + 0.3 * k)))
    if t > BUB2 + 1.0:
        k = back(pr(t, BUB2 + 1.0, BUB2 + 1.25))
        bubble(d, 70, 1020, "？？？真的假的", -1, (60, 64, 80), WHITE, min(1, k), 66)
    if t > BUB2 + 1.8:
        a = ease(pr(t, BUB2 + 1.8, BUB2 + 2.1))
        bubble(d, 1010, 1210, "PLOS Biology 2016，自己查", 1, (120, 220, 120), (20, 40, 20), a, 54)
    d.text(540, 1800, "Sender R, Fuchs S, Milo R. PLOS Biology, 2016, 14(8): e1002533", 24, A(WHITE, 0.7), k=0)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

SECS = [(0, HOOK_END, w_hook, u_hook), (MYTH, RECOUNT, w_myth, u_myth), (RECOUNT, RBC, w_count, u_count), (RBC, POOP, w_rbc, u_rbc),
        (POOP, MASS, w_poop, u_poop), (MASS, MITO, w_mass, u_mass), (MITO, OUTRO, w_mito, u_mito), (OUTRO, 99, w_end, u_end)]
CUTS = [HOOK_END, RECOUNT, RBC, NONUC, COLON, POOP, FLIP, MASS, MITO, OUTRO]

def subs(t, d):
    if t >= OUTRO: return
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            lines = wrap(d, s, 58, 920)
            for j, ln in enumerate(lines):
                y = 1660 + (j - (len(lines) - 1) / 2) * 84
                w = d.tlen(ln, 58)
                d.rect(540 - w / 2 - 24, y - 44, 540 + w / 2 + 24, y + 44, fill=A((0, 0, 0), 0.62 * al), r=16)
                d.text(540, y, ln, 58, A(WHITE, al))
def brand(t, d):
    d.rect(50, 80, 300, 128, fill=A(WHITE, 0.92), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(BG, 1))
    d.rect(800, 80, 1030, 128, fill=A((60, 150, 80), 0.95), r=24); d.text(915, 104, "一半是细菌", 26, A(WHITE, 1))

def cam(t):
    z = 1.0 + 0.07 * pulse(t, HITS, 7)
    if t < 0.5: z += 0.1 * (1 - ease(pr(t, 0, 0.3)))
    for a, b in RISERS:
        if a <= t < b: z += 0.1 * eio(pr(t, a, b))
    amp = 28 * pulse(t, [SPLIT, WRONG, FLIP], 3) + 12 * pulse(t, HITS, 5)
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx, 960 + sy

def frame(t):
    img = Image.new("RGB", (W, H), BG); d = D(img); ui = None
    for a, b, sf, uf in SECS:
        if a <= t < b: sf(t, d); ui = uf; break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    d = D(img)
    if ui: ui(t, d)
    for c in CUTS:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.55 * (1 - (t - c) / 0.1)))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)

if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.1f}.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        last = None
        for i in range(i0, i1):
            try: last = frame(i / FPS).tobytes()
            except Exception as e: print('ERR', i, e, file=sys.stderr)
            if last: p.stdin.write(last)
        p.stdin.close(); p.wait()
