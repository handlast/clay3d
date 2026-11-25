import math, random, sys, subprocess
from PIL import Image
from base import *
from fx import glow, face, mouth, sparks, embers, shake, stamp, flash, grad, rays, vignette
from cues import *

def ls(i): return L[i][0]
def le(i): return L[i][1]
FIRE = (255, 120, 30); FIRE_L = (255, 200, 80); HRED = (214, 46, 40); HRED_D = (140, 24, 26); GOLD = (240, 190, 70)
PAPER = (238, 222, 188); PAPER_D = (196, 170, 128); INKB = (40, 30, 26); JADE = (60, 170, 140); SKY = (40, 60, 110)

# scene bounds
A0, B0, C0, D0, E0, F0, G0, H0, I0 = 0, ls(3) - 0.1, ls(8), ls(9), ls(12), ls(14), ls(17), ls(21), ls(22)
CUTS = [B0, C0, D0, E0, F0, G0, H0, I0]

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

# ---------- scenes ----------
H_BOOM = 0.35; H_NUM = ls(1) + 0.9; H_Q = ls(2)
def sA(t, d):
    if t < H_Q - 0.1:
        rays(d, t, (150, 30, 20), (60, 10, 8), 20, 540, 1050)
        embers(d, t, FIRE_L, 1, 40)
        p = pulse(t, [H_BOOM], 2.5)
        for i in range(9):  # flame wall
            flame(d, 60 + i * 120, 1500, 300 + 80 * math.sin(t * 3 + i) + 200 * p, t, 0.9, i * 2.3)
        run = ease(pr(t, 0, 0.35))
        if t < H_NUM - 0.3:
            horse(d, lerp(-400, 470, run), 1080, 230, t, "proud" if t > 1.2 else "scream", 1.0, 1.0)
            sparks(d, 540, 1000, t, H_BOOM, 80, 1500, FIRE_L, 1, 3, 1.4)
        else:
            u = t - (H_NUM - 0.3)
            horse(d, 300, 1180, 150, t, "shock", 0.0, 0.8, look=0.8)
            # babies falling off bar
            for i in range(18):
                bx = 560 + (i % 6) * 80; by0 = 900 + (i // 6) * 110
                fall = max(0, u - i * 0.03)
                yy = by0 + 900 * fall * fall * (1 if i % 3 == 0 else 0.0)
                baby(d, bx, yy, 30, 1 if i % 3 else 1 - cl(fall * 1.5), )
                if i % 3 == 0 and fall > 0: d.text(bx, by0 - 50, "-", 40, A(WARN, 1 - cl(fall)), k=1)
    else:
        grad(d, (40, 14, 10), (10, 4, 4)); embers(d, t, FIRE, 0.6)
        u = t - H_Q
        horse(d, 540 - 160, 1100, 200, t, "sus", 0.0, 1.0, look=-0.6 + 1.2 * (math.sin(u * 4) > 0))
        for i in range(3):
            k = back(pr(t, H_Q + 0.15 * i, H_Q + 0.15 * i + 0.2))
            d.text(700 + i * 110, 700 - i * 40, "?", int(150 * k), A(YEL, 1), k=1)
WARN = (255, 70, 60)
def uA(t, d):
    if t < H_NUM - 0.3:
        k = back(pr(t, H_BOOM, H_BOOM + 0.25)); p = pulse(t, [H_BOOM + i * 0.5 for i in range(6)], 9)
        d.text(540, 330, "2026", int(120 * k), A(WHITE, 1), k=1)
        s = int(190 * k * (1 + 0.05 * p))
        d.text(548, 508, "双火马年", s, A(HRED_D, 1), k=1); d.text(540, 500, "双火马年", s, A(FIRE_L, 1), k=1)
        d.text(540, 670, "60 年一遇", int(70 * ease(pr(t, 1.2, 1.5))) + 1, A(WHITE, ease(pr(t, 1.2, 1.5))), k=1)
    elif t < H_Q - 0.1:
        k = back(pr(t, H_NUM - 0.3, H_NUM - 0.05))
        d.text(540, 330, "上一次 · 日本", 70, A(WHITE, 1), k=1)
        d.text(540, 520, "-46万", int(220 * k), A(WARN, 1), k=1)
        d.text(540, 680, "一年少生的孩子", 60, A(WHITE, ease(pr(t, H_NUM, H_NUM + 0.3))), k=1)
    else:
        d.text(540, 420, "为什么偏偏是这一年？", int(84 * back(pr(t, H_Q, H_Q + 0.2))), A(WHITE, 1), k=1)
    flash(d, t, [H_BOOM], WHITE, 0.95); flash(d, t, [H_NUM - 0.3], WARN, 0.4)

STEMS = "甲乙丙丁戊己庚辛壬癸"; BRANCH = "子丑寅卯辰巳午未申酉戌亥"
B_GEAR, B_60, B_BING, B_WU, B_FIRE = ls(3), ls(4), ls(5), ls(6), ls(7)
def wheel(d, cx, cy, R, chars, rot, col, hi=None, a=1.0):
    n = len(chars)
    d.circ(cx, cy, R + 50, fill=A(mix(col, (0, 0, 0), 0.5), a)); d.circ(cx, cy, R - 50, fill=A(mix(col, (0, 0, 0), 0.7), a))
    for i, c in enumerate(chars):
        ang = rot + i * 2 * math.pi / n - math.pi / 2
        x, y = cx + math.cos(ang) * R, cy + math.sin(ang) * R
        on = hi is not None and i == hi
        if on: glow(d, x, y, 70, FIRE_L, a)
        d.circ(x, y, 42, fill=A(FIRE if on else col, a)); d.text(x, y, c, 50, A(WHITE, a), k=1)
def sB(t, d):
    grad(d, (22, 26, 48), (8, 8, 18))
    for i in range(40):
        d.circ((i * 263) % 1080, (i * 151 + t * 15) % 1920, 2 + i % 3, fill=A(WHITE, 0.3 + 0.3 * math.sin(t * 2 + i)))
    if t < B_BING:
        n = 0
        if t >= B_60: n = int(cl((t - B_60) / 2.8) * 59)
        else: n = int(cl((t - B_GEAR - 0.5) / 2.0) * 5)
        si, bi = n % 10, n % 12
        app = back(pr(t, B_GEAR, B_GEAR + 0.4))
        wheel(d, 330, 1050, 200 * app + 1, STEMS, -si * 2 * math.pi / 10, (150, 110, 40), 0, app)
        wheel(d, 760, 1050, 240 * app + 1, BRANCH, -bi * 2 * math.pi / 12, (40, 110, 150), 0, app)
        # pointer + combo
        d.poly([(330, 790), (310, 750), (350, 750)], A(FIRE_L, app)); d.poly([(760, 750), (740, 710), (780, 710)], A(FIRE_L, app))
        if t >= B_60:
            d.rect(340, 1380, 740, 1480, fill=A((0, 0, 0), 0.5), r=24)
            d.text(470, 1430, STEMS[si] + BRANCH[bi], 70, A(YEL, 1), k=1); d.text(640, 1430, f"{n + 1:02d}", 70, A(WHITE, 1), k=1)
    elif t < B_FIRE:
        rays(d, t, (60, 40, 20), (20, 14, 8), 16, 540, 1000)
        if t < B_WU:
            k = back(pr(t, B_BING, B_BING + 0.3))
            glow(d, 540, 800, 300, FIRE_L, 0.8); d.circ(540, 800, 160 * k, fill=A((255, 220, 120), 1))
            for i in range(12):
                ang = t * 0.8 + i * math.pi / 6
                d.line([(540 + math.cos(ang) * 190, 800 + math.sin(ang) * 190), (540 + math.cos(ang) * 260 * k, 800 + math.sin(ang) * 260 * k)], A(FIRE_L, 1), 14)
            tile(d, 540, 1220, 300 * k, "丙", HRED, 1, "天干 · 阳火", glowc=FIRE)
        else:
            k = back(pr(t, B_WU, B_WU + 0.3))
            # clock at noon
            cx, cy = 360, 830
            d.circ(cx, cy, 170, fill=A(PAPER, 1)); d.circ(cx, cy, 170, outline=A(GOLD, 1), w=10)
            for i in range(12):
                ang = i * math.pi / 6 - math.pi / 2
                d.text(cx + math.cos(ang) * 135, cy + math.sin(ang) * 135, BRANCH[i], 30, A(FIRE if i == 6 else INKB, 1), k=1)
            hand = math.pi / 2 + (1 - ease(pr(t, B_WU, B_WU + 0.8))) * 3
            d.line([(cx, cy), (cx + math.cos(hand) * 110, cy + math.sin(hand) * 110)], A(HRED, 1), 12)
            horse(d, 780, 840, 120, t, "proud", 0.8, 0.9)
            tile(d, 540, 1230, 300 * k, "午", HRED, 1, "地支 · 火 · 马", glowc=FIRE)
    else:
        u = t - B_FIRE
        rays(d, t, (140, 40, 16), (50, 10, 6), 22, 540, 1000); embers(d, t, FIRE_L, 1, 36)
        m = eio(pr(t, B_FIRE + 0.3, B_FIRE + 1.6))
        tile(d, lerp(300, 470, m), 1000, 240, "丙", HRED, 1 - m * 0.9, glowc=FIRE)
        tile(d, lerp(780, 610, m), 1000, 240, "午", HRED, 1 - m * 0.9, glowc=FIRE)
        if t < B_FIRE + 1.6: d.text(540, 1000, "+", 120, A(WHITE, 1 - m), k=1)
        if m >= 1:
            p = pulse(t, [B_FIRE + 1.6], 3)
            for i in range(7): flame(d, 220 + i * 107, 1450, 380 + 120 * p, t, 0.9, i)
            horse(d, 470, 1050, 210 + 20 * p, t, "proud", 1.0, 1.0)
            sparks(d, 540, 1000, t, B_FIRE + 1.6, 70, 1400, FIRE_L, 1, 7, 1.3)
def uB(t, d):
    if t < B_BING:
        d.text(540, 330, "10 天干 × 12 地支", int(80 * back(pr(t, B_GEAR, B_GEAR + 0.25))), A(WHITE, 1), k=1)
        if t >= B_60:
            d.text(540, 470, "阳配阳 阴配阴 → 60 种", 60, A(YEL, ease(pr(t, B_60, B_60 + 0.3))), k=1)
            if t > B_60 + 2.9: stamp(d, t, B_60 + 2.9, "一甲子", 540, 620, 110, FIRE_L)
    elif t < B_FIRE:
        if t < B_WU: d.text(540, 380, "丙 ＝ 正午的太阳", 76, A(WHITE, ease(pr(t, B_BING, B_BING + 0.3))), k=1)
        else: d.text(540, 380, "午 ＝ 马 ＝ 正午", 76, A(WHITE, ease(pr(t, B_WU, B_WU + 0.3))), k=1)
    else:
        if t > B_FIRE + 1.6:
            k = back(pr(t, B_FIRE + 1.6, B_FIRE + 1.85))
            d.text(548, 438, "火 + 火", int(170 * k), A(HRED_D, 1), k=1); d.text(540, 430, "火 + 火", int(170 * k), A(FIRE_L, 1), k=1)
        else: d.text(540, 430, "天干火 · 地支火", 76, A(WHITE, 1), k=1)
    flash(d, t, [B_BING, B_WU], FIRE_L, 0.3); flash(d, t, [B_FIRE + 1.6], WHITE, 0.8)

YEARS = [1906, 1966, 2026, 2086]
def sC(t, d):
    grad(d, (16, 20, 36), (6, 6, 12))
    u = t - C0
    off = lerp(0, -1, eio(pr(t, C0, C0 + 1.2))) + lerp(0, 2, eio(pr(t, C0 + 1.8, C0 + 3.2)))
    d.line([(0, 1000), (1080, 1000)], A(GOLD, 0.8), 8)
    for i, y in enumerate(YEARS):
        x = 540 + (i - 2 + off) * 400 * -1 * -1
        x = 540 + (i - 2) * 400 - off * 400 + 400 * 0
        x = 540 + (i - 2 - (off - 0)) * 400 + 400 * (-0)
        on = abs(x - 540) < 60
        d.circ(x, 1000, 34 if on else 22, fill=A(FIRE if on else GOLD, 1))
        if on: glow(d, x, 1000, 120, FIRE_L, 1)
        d.text(x, 1100, str(y), 70 if on else 48, A(WHITE, 1 if on else 0.6), k=1)
        if y == 2026: d.text(x, 1180, "今年", 44, A(FIRE_L, 1), k=1)
    horse(d, 540, 760, 110, t, "chill", 0.9, 1.0)
def uC(t, d):
    d.text(540, 380, "每 60 年 · 轮回一次", 76, A(WHITE, ease(pr(t, C0, C0 + 0.3))), k=1)

D_COUNT, D_JIE, D_JK = ls(9), ls(10), ls(11)
def sD(t, d):
    paper_bg(d, t)
    if t < D_JIE:
        n = int(cl((t - D_COUNT - 1.0) / 2.6) * 21)
        scholar(d, 290, 1050, 190, t, "sus" if n < 21 else "scared", 1, 0.5 + 0.5 * math.sin(t * 8))
        # scrolls + tally marks
        d.rect(500, 720, 980, 1320, fill=A(PAPER, 1), r=16)
        for k in range(n):
            gx = 560 + (k % 5) * 80; gy = 790 + (k // 5) * 110
            if k % 5 == 4: d.line([(gx - 300, gy + 30), (gx + 20, gy - 20)], A(HRED, 1), 10)
            else: d.line([(gx, gy - 30), (gx, gy + 40)], A(INKB, 1), 12)
        for i in range(10):  # flying books
            u = ((t - D_COUNT) * 0.6 + i / 10) % 1
            d.rect(100 + i * 90, 1500 - u * 1300, 160 + i * 90, 1540 - u * 1300, fill=A(PAPER_D, 0.5 * math.sin(u * math.pi)), r=4)
    elif t < D_JK:
        rays(d, t, (130, 20, 16), (40, 6, 6), 16, 540, 1050); embers(d, t, FIRE_L, 1)
        k1 = back(pr(t, D_JIE, D_JIE + 0.3)); k2 = back(pr(t, D_JIE + 0.6, D_JIE + 0.9))
        horse(d, 300, 1100, 150 * k1 + 1, t, "angry", 0.6, 1.0)
        goat(d, 720, 1120, 150 * k2 + 1, t, "sus", 1, 1)
    else:
        grad(d, (60, 20, 14), (14, 6, 6))
        # burning city walls
        for i in range(6):
            x = 90 + i * 180
            d.rect(x - 70, 1050, x + 70, 1400, fill=A((60, 40, 36), 1)); d.poly([(x - 90, 1050), (x, 980), (x + 90, 1050)], A((40, 26, 24), 1))
            flame(d, x, 1000 + 20 * math.sin(i), 260 + 60 * math.sin(t * 4 + i), t, 0.9, i * 5)
        d.rect(-10, 1400, 1090, 1920, fill=A((30, 18, 14), 1))
        embers(d, t, FIRE_L, 1, 40)
        for i, (yr, gz) in enumerate(((1126, "丙午"), (1127, "丁未"))):
            k = back(pr(t, D_JK + 0.8 + i * 0.6, D_JK + 1.1 + i * 0.6))
            tile(d, 340 + i * 400, 720, 230 * k + 1, gz[1], HRED, 1, f"{yr} {gz}", glowc=FIRE)
def uD(t, d):
    if t < D_JIE:
        d.text(540, 330, "南宋 · 柴望《丙丁龟鉴》", 66, A(WHITE, ease(pr(t, D_COUNT, D_COUNT + 0.3))), k=1)
        n = int(cl((t - D_COUNT - 1.0) / 2.6) * 21)
        if n: d.text(540, 480, f"丙午·丁未年 ×{n}", int(80 * (1 + 0.1 * pulse(t, [D_COUNT + 1.0 + i * 2.6 / 21 for i in range(21)], 12))), A(YEL, 1), k=1)
    elif t < D_JK:
        k = back(pr(t, D_JIE + 0.2, D_JIE + 0.45))
        d.text(548, 448, "赤马红羊劫", int(150 * k), A(INKB, 1), k=1); d.text(540, 440, "赤马红羊劫", int(150 * k), A(FIRE_L, 1), k=1)
        d.text(300, 1400, "丙午 · 赤马", 50, A(WHITE, 1), k=1); d.text(760, 1400, "丁未 · 红羊", 50, A(WHITE, ease(pr(t, D_JIE + 0.6, D_JIE + 0.9))), k=1)
    else:
        d.text(540, 380, "靖康之变", int(130 * back(pr(t, D_JK, D_JK + 0.25))), A(FIRE_L, 1), k=1)
    flash(d, t, [D_JIE + 0.2], FIRE_L, 0.5); flash(d, t, [D_JK], WHITE, 0.6)

E_SEAL, E_ANY = ls(12) + 2.1, ls(13)
def sE(t, d):
    if t < E_ANY:
        grad(d, (230, 214, 176), (196, 174, 130))
        for i in range(6):  # book stack
            d.rect(140, 1500 - i * 70, 940, 1560 - i * 70, fill=A(mix((80, 50, 30), (130, 80, 40), i / 6), 1), r=6)
            d.rect(160, 1508 - i * 70, 920, 1520 - i * 70, fill=A(PAPER, 0.8))
        d.rect(240, 660, 840, 1060, fill=A(PAPER, 1), r=10); d.rect(240, 660, 840, 1060, outline=A(PAPER_D, 1), w=6, r=10)
        for i in range(8): d.line([(800 - i * 70, 690), (800 - i * 70, 1030)], A((150, 120, 90), 0.5), 3)
        d.text(540, 760, "四库全书", 60, A(INKB, 1), k=1)
        d.text(540, 870, "所列事迹", 64, A(INKB, ease(pr(t, E0 + 1.2, E0 + 1.5))), k=1)
        if t >= E_SEAL:
            k = back(pr(t, E_SEAL, E_SEAL + 0.15)); sz = 2.0 - k
            d.rect(540 - 260 * sz, 980 - 80 * sz, 540 + 260 * sz, 980 + 80 * sz, fill=A(HRED, min(1, k)), r=12)
            d.text(540, 980, "多涉牵就", int(110 * sz), A(WHITE, min(1, k)), k=1)
            sparks(d, 540, 980, t, E_SEAL, 30, 900, HRED, 1, 4, 0.6)
        scholar(d, 880, 1250, 120, t, "scared" if t >= E_SEAL else "sus", 1, 0)
    else:
        grad(d, (20, 16, 24), (8, 6, 10))
        r2 = random.Random(5)
        hits = [E_ANY + 0.5 + i * 0.28 for i in range(10)]
        for i in range(30):
            x, y = 140 + (i % 5) * 200, 700 + (i // 5) * 150
            yr = r2.randint(120, 1900)
            lit = any(h <= t and r2.random() < 0.9 for h in hits[:i % 10 + 1]) if t > hits[0] else False
            on = t >= hits[i % 10]
            d.rect(x - 85, y - 55, x + 85, y + 55, fill=A((60, 56, 70) if not on else (110, 30, 26), 1), r=12)
            d.text(x, y - 10, str(abs(yr)), 40, A(WHITE, 0.85), k=1)
            if on: d.text(x, y + 32, ["战乱", "饥荒", "洪水", "瘟疫", "政变"][i % 5], 28, A(FIRE_L, 1), k=1)
def uE(t, d):
    if t < E_ANY:
        d.text(540, 330, "清代学者批注", 74, A(INKB, ease(pr(t, E0, E0 + 0.3))), k=1)
        d.text(540, 470, "＝ 牵强附会", 70, A(HRED, ease(pr(t, E_SEAL + 0.4, E_SEAL + 0.7))), k=1)
    else:
        d.text(540, 330, "随便挑一年", 80, A(WHITE, 1), k=1)
        d.text(540, 460, "史书里都有灾", 80, A(FIRE_L, ease(pr(t, E_ANY + 2.0, E_ANY + 2.3))), k=1)
        d.text(540, 1640 - 0, "", 10, A(WHITE, 0))
    flash(d, t, [E_SEAL], HRED, 0.4)

F_OSH, F_RUM = ls(15), ls(16)
def sF(t, d):
    if t < F_OSH:
        grad(d, (250, 170, 180), (120, 60, 90))
        d.circ(540, 900, 300, fill=A((255, 236, 220), 0.9))
        # torii
        d.rect(320, 980, 360, 1500, fill=A(HRED, 1)); d.rect(720, 980, 760, 1500, fill=A(HRED, 1))
        d.rect(250, 960, 830, 1000, fill=A(HRED, 1)); d.poly([(220, 900), (860, 900), (830, 950), (250, 950)], A(INKB, 1))
        for i in range(30):  # sakura petals
            u = (t * 0.2 + i / 30) % 1
            d.ell((i * 137 + 60 * math.sin(t + i)) % 1080, u * 2000 - 50, 12, 8, A((255, 200, 215), 0.9))
        horse(d, 540, 1300, 130, t, "chill", 0.6, 1.0)
    elif t < F_RUM:
        grad(d, (20, 16, 40), (6, 4, 14))
        # fire lookout tower
        tx = 760
        d.line([(tx - 90, 1500), (tx - 40, 800)], A((110, 80, 50), 1), 18); d.line([(tx + 90, 1500), (tx + 40, 800)], A((110, 80, 50), 1), 18)
        for k in range(6): d.line([(tx - 85 + k * 8, 1400 - k * 110), (tx + 85 - k * 8, 1400 - k * 110)], A((110, 80, 50), 1), 10)
        d.rect(tx - 70, 740, tx + 70, 800, fill=A((90, 60, 40), 1)); d.circ(tx, 720, 26, fill=A(GOLD, 1))
        fire_on = t > F_OSH + 2.4
        if fire_on:
            for i in range(6): flame(d, 150 + i * 170, 1560, 300 + 100 * math.sin(t * 3 + i), t, 0.95, i * 4)
            embers(d, t, FIRE_L, 1, 40)
        girl(d, 320, 1150, 190, t, "sad" if t > F_OSH + 4.0 else ("scared" if fire_on else "chill"), 1)
        if not fire_on:
            d.circ(450, 900, 40, fill=A(TONGUE, 0.8 + 0.2 * math.sin(t * 8)))
            d.text(450, 900, "♥", 50, A(WHITE, 1), k=2)
    else:
        grad(d, (40, 10, 14), (10, 4, 6))
        # theater curtains
        op = ease(pr(t, F_RUM, F_RUM + 0.6))
        for s_ in (-1, 1):
            x0 = 540 + s_ * (60 + 420 * op)
            for k in range(6):
                xx = x0 + s_ * k * 90
                d.rect(min(xx, xx + s_ * 90), 200, max(xx, xx + s_ * 90), 1700, fill=A(mix(HRED, HRED_D, k % 2), 1))
        d.rect(0, 160, 1080, 260, fill=A(GOLD, 1))
        if op > 0.5:
            girl(d, 540, 1050, 170, t, "sad", 1)
            for i in range(5):  # rumor bubbles
                k = back(pr(t, F_RUM + 0.8 + i * 0.25, F_RUM + 1.0 + i * 0.25))
                bx, by = [(250, 700), (820, 650), (180, 1300), (900, 1250), (540, 560)][i]
                d.ell(bx, by, 130 * k + 1, 70 * k + 1, A(WHITE, 0.92)); d.text(bx, by, ["克夫", "性子烈", "不吉", "别生", "丙午女"][i], int(46 * k) + 1, A(HRED_D, 1), k=1)
def uF(t, d):
    if t < F_OSH:
        k = back(pr(t, F0, F0 + 0.25))
        d.text(540, 400, "日本 · 丙午", int(120 * k), A(WHITE, 1), k=1)
    elif t < F_RUM:
        d.text(540, 330, "1666 年生 · 八百屋阿七", 64, A(WHITE, ease(pr(t, F_OSH, F_OSH + 0.3))), k=1)
        if t > F_OSH + 2.4: stamp(d, t, F_OSH + 2.4, "纵火", 540, 480, 120, FIRE_L)
    else:
        d.text(540, 330, "戏剧传成谣言", 70, A(WHITE, ease(pr(t, F_RUM, F_RUM + 0.3))), k=1)
    flash(d, t, [F_OSH + 2.4], FIRE_L, 0.5)

G_BAR, G_TWIST, G_SHIFT, G_PLUS = ls(17), ls(18), ls(19), ls(20)
BARS = [(1965, 182.4), (1966, 136.1), (1967, 193.6)]
def sG(t, d):
    tw = t >= G_TWIST
    grad(d, (14, 18, 34) if not tw else (16, 30, 30), (4, 6, 12))
    base, x0 = 1330, 220
    for i, (yr, v) in enumerate(BARS):
        g = ease(pr(t, G_BAR + 0.3 + i * 0.5, G_BAR + 0.9 + i * 0.5))
        if i == 1: g = ease(pr(t, G_BAR + 2.2, G_BAR + 2.9))
        h = v / 200 * 650 * g
        x = x0 + i * 320
        col = WARN if i == 1 else (90, 140, 220)
        if tw and i != 1 and t >= G_PLUS: col = JADE
        d.rect(x - 100, base - h, x + 100, base, fill=A(col, 1), r=12)
        d.text(x, base + 60, str(yr), 52, A(WHITE, 1), k=1)
        if g > 0.1: d.text(x, base - h - 50, f"{v:.0f}万", 56, A(WHITE, g), k=1)
        if i == 1 and g > 0:
            ghost = 182.4 / 200 * 650
            d.rect(x - 100, base - ghost, x + 100, base - h, outline=A(WARN, 0.8 * g), w=5, r=12)
    if t >= G_SHIFT:  # blocks fly from 1966 gap to neighbours
        for i in range(10):
            u = ease(pr(t, G_SHIFT + 0.6 + i * 0.12, G_SHIFT + 1.4 + i * 0.12))
            tx = x0 if i % 2 == 0 else x0 + 640
            sx, sy = x0 + 320, base - 450 - (i // 2) * 40
            x = lerp(sx, tx, u); y = sy - math.sin(u * math.pi) * 200
            if t < G_PLUS or u < 1: baby(d, x, y, 22)
    if t >= G_TWIST and t < G_SHIFT:
        k = back(pr(t, G_TWIST, G_TWIST + 0.3))
        d.rect(150, 560, 930, 720, fill=A(JADE, min(1, k)), r=30)
def uG(t, d):
    if t < G_TWIST:
        d.text(540, 330, "1966 · 日本出生人数", 70, A(WHITE, ease(pr(t, G_BAR, G_BAR + 0.3))), k=1)
        if t > G_BAR + 2.9: stamp(d, t, G_BAR + 2.9, "-25%", 540, 500, 160, WARN)
    elif t < G_SHIFT:
        d.text(540, 640, "不只是迷信", int(100 * back(pr(t, G_TWIST, G_TWIST + 0.3))), A(WHITE, 1), k=1)
    else:
        d.text(540, 330, "减少的多是二胎、三胎", 66, A(WHITE, 1), k=1)
        d.text(540, 460, "只是挪了一年", 76, A(JADE, ease(pr(t, G_SHIFT + 2.0, G_SHIFT + 2.3))), k=1)
        if t >= G_PLUS: stamp(d, t, G_PLUS + 0.3, "前后多生 20 多万", 540, 600, 72, YEL)
    flash(d, t, [G_BAR + 2.9], WARN, 0.4); flash(d, t, [G_TWIST], WHITE, 0.6)

def sH(t, d):
    grad(d, (12, 26, 30), (4, 8, 10))
    d.line([(100, 1100), (980, 1100)], A(WHITE, 0.3), 4)
    g = ease(pr(t, H0 + 0.3, H0 + 1.8))
    pts = [(100 + k * 8, 1100 - 8 * math.sin(k * 0.4) * 0.3 - 6 * math.sin(k * 0.13)) for k in range(int(110 * g) + 1)]
    if len(pts) > 1: d.line(pts, A(JADE, 1), 10)
    if g > 0.95: glow(d, pts[-1][0], pts[-1][1], 50, JADE, 1)
    horse(d, 540, 1450, 130, t, "chill", 0.7, 1.0)
def uH(t, d):
    d.text(540, 380, "2026 年 1 月 · 日本", 70, A(WHITE, ease(pr(t, H0, H0 + 0.3))), k=1)
    k = back(pr(t, H0 + 1.6, H0 + 1.85))
    d.text(540, 620, "+0.5%", int(200 * k), A(JADE, 1), k=1)
    d.text(540, 800, "几乎没受影响", 60, A(WHITE, ease(pr(t, H0 + 2.0, H0 + 2.3))), k=1)

I_TWO = ls(23)
def sI(t, d):
    rays(d, t, (110, 30, 16), (40, 8, 6), 24, 540, 1050); embers(d, t, FIRE_L, 0.9)
    rot = t * 0.4
    R = 360
    for i in range(60):
        ang = rot + i * 2 * math.pi / 60
        on = i == 42
        x, y = 540 + math.cos(ang) * R, 1050 + math.sin(ang) * R
        d.circ(x, y, 22 if on else 12, fill=A(FIRE_L if on else GOLD, 1 if on else 0.6))
        if on: glow(d, x, y, 60, FIRE, 1)
    horse(d, 470, 1050, 150, t, "proud", 0.5, 1.0)
def uI(t, d):
    d.text(540, 330, "不是命", int(130 * back(pr(t, I0, I0 + 0.25))), A(WHITE, 1), k=1)
    d.text(540, 480, "是几千年的计时法", 74, A(YEL, ease(pr(t, I0 + 1.2, I0 + 1.5))), k=1)
    if t > I_TWO:
        a = ease(pr(t, I_TWO, I_TWO + 0.3))
        d.rect(90, 1440, 990, 1720, fill=A((0, 0, 0), 0.6 * a), r=30)
        d.text(540, 1520, "历法是智慧 · 吉凶是附会", 62, A(FIRE_L, a), k=1)
        d.text(540, 1630, "你身边有人因为属相改过计划吗？", 44, A(WHITE, ease(pr(t, I_TWO + 2.5, I_TWO + 2.8))), k=1)
    if t > DUR - 3.2:
        a = ease(pr(t, DUR - 3.2, DUR - 2.9))
        d.text(540, 1780, "资料：柴望《丙丁龟鉴》·《四库全书总目提要》· 日本厚生劳动省人口动态统计 · Kikkawa, nippon.com 2025", 22, A(WHITE, 0.8 * a), k=0)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

def subs(t, d):
    if t > I_TWO: return
    for i, (a, b) in enumerate(L):
        if a - 0.05 <= t < b + 0.15:
            s = LINES[i].rstrip("。？")
            al = ease(pr(t, a - 0.05, a + 0.1)) * (1 - pr(t, b + 0.05, b + 0.15))
            lines = wrap(d, s, 54, 900)
            for j, ln in enumerate(lines):
                y = 1600 + (j - (len(lines) - 1) / 2) * 80
                w = d.tlen(ln, 54)
                d.rect(540 - w / 2 - 22, y - 40, 540 + w / 2 + 22, y + 40, fill=A((0, 0, 0), 0.62 * al), r=14)
                d.text(540, y, ln, 54, A(WHITE, al))
def brand(t, d):
    d.rect(50, 80, 300, 128, fill=A(WHITE, 0.92), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(BG, 1))
    d.rect(780, 80, 1030, 128, fill=A(HRED, 0.92), r=24); d.text(905, 104, "丙午 · 双火马年", 26, A(WHITE, 1))

SECS = [(A0, B0, sA, uA), (B0, C0, sB, uB), (C0, D0, sC, uC), (D0, E0, sD, uD), (E0, F0, sE, uE), (F0, G0, sF, uF), (G0, H0, sG, uG), (H0, I0, sH, uH), (I0, 999, sI, uI)]
KEYHITS = [H_BOOM, H_NUM - 0.3, B_FIRE + 1.6, D_JIE + 0.2, D_JK, E_SEAL, F_OSH + 2.4, G_BAR + 2.9, G_TWIST, I0]

def cam(t):
    z = 1.0 + 0.06 * pulse(t, KEYHITS, 6) + 0.02 * pulse(t, [a for a, b in L], 8)
    if t < 1.0: z += 0.35 * (1 - ease(pr(t, 0, 0.45)))
    amp = 26 * pulse(t, [H_BOOM], 2.5) + 14 * pulse(t, KEYHITS[1:], 4)
    sx, sy = shake(t, amp, 61)
    # slow drift per section
    for a, b, *_ in SECS:
        if a <= t < b: z += 0.05 * eio(pr(t, a, min(b, a + 8)))
    return z, 540 + sx, 960 + sy

def frame(t):
    img = Image.new("RGB", (W, H), BG); d = D(img); ui = None
    for a, b, sf, uf in SECS:
        if a <= t < b: sf(t, d); ui = uf; break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    d = D(img)
    if ui: ui(t, d)
    for c in CUTS:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - (t - c) / 0.1)))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)

if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.1f}.png")
    elif sys.argv[1] == "times":
        print({k: round(v, 2) for k, v in dict(B0=B0, C0=C0, D0=D0, E0=E0, F0=F0, G0=G0, H0=H0, I0=I0, DUR=DUR).items()})
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        last = None
        for i in range(i0, i1):
            try: last = frame(i / FPS).tobytes()
            except Exception as e: print('ERR', i, e, file=sys.stderr)
            p.stdin.write(last if last else frame((i + 1) / FPS).tobytes())
        p.stdin.close(); p.wait()
