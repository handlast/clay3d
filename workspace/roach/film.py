import math, random, sys, subprocess
from PIL import Image
from base import *
from fx import glow, sparks, shake, stamp, flash, grad, rays, vignette, embers
from cues import *

OL = (24, 16, 12)
ROACH = (150, 78, 36); ROACH_D = (96, 44, 20); ROACH_L = (214, 132, 72)
TERM = (246, 226, 180); TERM_D = (210, 180, 130); THEAD = (214, 140, 60)
PINK = (255, 90, 170); PINK_L = (255, 180, 220); MINT = (110, 240, 200); WARN = (255, 80, 70)
ORANGE = (255, 150, 50); ANC = (120, 110, 50)

def rpoly(cx, cy, rx, ry, ang, n=20):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + rx * math.cos(2 * math.pi * k / n) * ca - ry * math.sin(2 * math.pi * k / n) * sa,
             cy + rx * math.cos(2 * math.pi * k / n) * sa + ry * math.sin(2 * math.pi * k / n) * ca) for k in range(n)]

def eye(d, x, y, r, kind, a, look=0.0):
    if kind == "proud":
        d.arc(x, y + r * 0.3, r * 0.9, r * 0.8, 200, 340, A(OL, a), r * 0.42); return
    big = 1.3 if kind in ("shock", "scared") else 1.0
    rx, ry = r * 0.95 * big, r * 1.1 * big
    d.ell(x, y, rx, ry, A(WHITE, a))
    pr_ = r * (0.36 if kind in ("shock", "scared") else 0.55)
    px = x + look * r * 0.35
    d.circ(px, y + r * 0.1, pr_, fill=A(OL, a)); d.circ(px - pr_ * .35, y - pr_ * .3, pr_ * .38, fill=A(WHITE, a))

def bug(d, x, y, s, t, k=1.0, kind="chill", a=1.0, look=0.0, walk=0.0, xray=0.0, tail=False, col=None, flip=False):
    """front/top view. k: 0 termite -> 1 roach. y = body center."""
    body = col or mix(TERM, ROACH, k); bodyd = mix(TERM_D, ROACH_D, k); head = mix(THEAD, ROACH, k)
    if xray > 0:
        body = mix(body, (40, 70, 120), xray); bodyd = mix(bodyd, (20, 40, 80), xray); head = mix(head, (50, 80, 130), xray)
    hx, hy = x, y - 0.95 * s
    # legs
    for side in (-1, 1):
        for j in range(3):
            ph = math.sin(walk * 12 + j * 2.1 + (side > 0) * math.pi) * 0.25
            ax, ay = x + side * 0.38 * s, y + (j - 1) * 0.42 * s
            kx, ky = x + side * 0.85 * s, ay - 0.2 * s + ph * 0.3 * s
            fx, fy = x + side * 1.05 * s, ay + 0.35 * s + (j - 1) * 0.15 * s + ph * 0.2 * s
            d.line([(ax, ay), (kx, ky), (fx, fy)], A(bodyd, a), 0.08 * s)
    if tail:
        d.line([(x, y + 0.6 * s), (x + 0.1 * s, y + 1.3 * s), (x + 0.05 * s, y + 1.75 * s)], A(bodyd, a), 0.06 * s)
    # body
    rx, ry = lerp(0.44, 0.55, k) * s, lerp(0.7, 0.78, k) * s
    d.ell(x, y, rx, ry, A(body, a))
    if k < 0.99 and xray < 0.5:
        for i in range(5):
            yy = y - ry * 0.5 + i * ry * 0.3
            w_ = rx * math.sqrt(max(0, 1 - ((yy - y) / ry) ** 2))
            d.line([(x - w_ * 0.9, yy), (x + w_ * 0.9, yy)], A(bodyd, a * (1 - k)), 0.03 * s)
    if k > 0.01 and xray < 0.5:
        d.line([(x, y - ry * 0.85), (x, y + ry * 0.95)], A(ROACH_D, a * k), 0.035 * s)
        d.ell(x - rx * 0.45, y - ry * 0.35, rx * 0.18, ry * 0.4, A(ROACH_L, 0.75 * a * k))
        d.ell(x - rx * 0.5, y - ry * 0.5, rx * 0.07, ry * 0.12, A(WHITE, 0.6 * a * k))
    if xray > 0:
        rnd = random.Random(5)
        for i in range(26):
            ang = rnd.uniform(0, 6.28); rr = math.sqrt(rnd.random()) * 0.8
            bx, by = x + math.cos(ang) * rx * rr, y + math.sin(ang) * ry * rr
            th = rnd.uniform(0, 3.14) + t * 0.6
            glow(d, bx, by, 0.12 * s, PINK, xray * 0.8, 4)
            d.poly(rpoly(bx, by, 0.07 * s, 0.025 * s, th, 10), A(PINK_L, xray * a))
    # pronotum + head
    d.ell(x, y - ry * 0.95, rx * 0.8, 0.25 * s, A(mix(bodyd, body, 0.4), a))
    hr = 0.4 * s
    # antennae
    alen = lerp(0.9, 2.1, k) * s
    for side in (-1, 1):
        pts = []
        for i in range(12):
            u = i / 11
            ang = -math.pi / 2 + side * (0.35 + 0.5 * u) + 0.12 * math.sin(t * 3 + side + u * 3)
            pts.append((hx + side * 0.15 * s + math.cos(ang) * alen * u, hy - 0.25 * s + math.sin(ang) * alen * u))
        d.line(pts, A(head, a), 0.045 * s)
        if k < 0.6:
            for px, py in pts[2::2]: d.circ(px, py, 0.04 * s, fill=A(head, a * (1 - k)))
    d.circ(hx, hy, hr, fill=A(head, a))
    er = 0.12 * s
    for s_ in (-1, 1): eye(d, hx + s_ * 0.17 * s, hy - 0.04 * s, er, kind, a, look)
    my = hy + 0.2 * s
    if kind in ("shock", "scared"): d.ell(hx, my, 0.06 * s, 0.08 * s, A(OL, a))
    elif kind in ("proud", "chill"): d.arc(hx, my - 0.05 * s, 0.1 * s, 0.07 * s, 20, 160, A(OL, a), 0.03 * s)
    else: d.line([(hx - 0.06 * s, my), (hx + 0.06 * s, my)], A(OL, a), 0.03 * s)
    for s_ in (-1, 1): d.ell(hx + s_ * 0.28 * s, hy + 0.12 * s, 0.06 * s, 0.035 * s, A((255, 110, 120), 0.6 * a))
    if kind in ("scared", "shock"): d.ell(hx + 0.45 * s, hy - 0.3 * s, 0.04 * s, 0.07 * s, A(CYAN, a))

def ootheca(d, x, y, s, a=1.0, col=ROACH, glowk=0.0, filled=1.0):
    w, h = 0.9 * s, 0.38 * s
    d.rect(x - w, y - h, x + w, y + h, fill=A(col, a), r=h)
    for row in (-1, 1):
        for i in range(8):
            ex = x - w * 0.8 + i * w * 1.6 / 7; ey = y + row * h * 0.45
            d.ell(ex, ey, w * 0.09, h * 0.36, A(mix(col, WHITE, 0.25), a))
            if glowk > 0 and (i + (row > 0) * 8) / 16 < filled:
                glow(d, ex, ey, 0.12 * s, PINK, glowk, 4); d.circ(ex, ey, 0.03 * s, fill=A(PINK_L, glowk))
    d.line([(x - w * 0.85, y - h * 0.8), (x + w * 0.85, y - h * 0.8)], A(mix(col, WHITE, 0.3), 0.6 * a), 5)

def dino(d, x, y, s, a=1.0, col=(60, 90, 70)):
    d.line([(x + 0.5 * s, y - 0.2 * s), (x + 1.0 * s, y - 1.1 * s), (x + 1.25 * s, y - 1.25 * s)], A(col, a), 0.22 * s)
    d.circ(x + 1.28 * s, y - 1.25 * s, 0.17 * s, fill=A(col, a))
    d.line([(x - 0.6 * s, y - 0.1 * s), (x - 1.3 * s, y + 0.2 * s), (x - 1.8 * s, y + 0.15 * s)], A(col, a), 0.16 * s)
    for lx in (-0.4, -0.2, 0.25, 0.45): d.rect(x + lx * s - 0.08 * s, y, x + lx * s + 0.08 * s, y + 0.55 * s, fill=A(col, a), r=10)
    d.ell(x, y - 0.1 * s, 0.8 * s, 0.45 * s, A(col, a))
    d.circ(x + 1.33 * s, y - 1.3 * s, 0.035 * s, fill=A(WHITE, a))

def counter(d, t, t0, t1, v0, v1, y=760, a=1.0):
    u = eio(pr(t, t0, t1)); v = v0 + (v1 - v0) * u
    s = "今天" if v < 0.5 else (f"{v:.0f} 万年前" if v < 10000 else f"{v / 10000:.2f} 亿年前")
    if v >= 10000 and abs(v - round(v / 10000, 1) * 10000) < 1 and u >= 1: s = f"{v / 10000:g} 亿年前"
    d.rect(140, y - 110, 940, y + 110, fill=A((0, 0, 0), 0.6 * a), r=40)
    d.text(540, y, s, 120, A(YEL, a), k=1)

def tunnel(d, t, col=(80, 60, 160)):
    grad(d, (10, 6, 30), (2, 2, 8))
    for i in range(14):
        r = ((t * 900 + i * 140) % 1960)
        d.circ(540, 960, r, outline=A(col, 0.5 * (r / 1960)), w=6)
    for i in range(24):
        ang = i * math.pi / 12 + t * 2
        r0 = (t * 1500 + i * 90) % 900 + 100
        d.line([(540 + math.cos(ang) * r0, 960 + math.sin(ang) * r0), (540 + math.cos(ang) * (r0 + 120), 960 + math.sin(ang) * (r0 + 120))], A(WHITE, 0.35), 4)

def outline_text(d, x, y, s, size, col, a=1.0):
    d.text(x, y, s, size, A(col, a), k=1)

# ---------------- scenes ----------------
def w_hook(t, d):
    grad(d, (120, 40, 20), (30, 8, 6)); rays(d, t, (170, 70, 30), (60, 16, 10), 22, 540, 1150)
    k = ease(pr(t, MORPH, MORPH + 0.25))
    bug(d, 540, 1230, 230 * (1 + 0.1 * pulse(t, [MORPH], 8)), t, k, "scared" if t < MORPH else "proud", walk=t * 0.3)
    sparks(d, 540, 1150, t, MORPH, 70, 1500, YEL, 1, 3, 1.0)
    if t < MORPH:
        pass
def u_hook(t, d):
    outline_text(d, 540, 290, "白蚁", 150, WHITE)
    outline_text(d, 540, 500, "其实是蟑螂", int(170 * (1 + 0.08 * pulse(t, [MORPH], 7))), YEL)
    flash(d, t, [MORPH], WHITE, 0.95)

LEAVES = [("螳螂", 150), ("姬蠊", 340), ("蜚蠊", 530), ("隐尾蠊", 720), ("白蚁", 910)]
def w_tree(t, d):
    grad(d, (10, 26, 40), (2, 6, 12))
    for i in range(30):  # dna dots
        yy = (i * 70 + t * 80) % 1920; ph = i * 0.5 + t * 2
        d.circ(60 + 30 * math.sin(ph), yy, 7, fill=A(CYAN, 0.35)); d.circ(60 - 30 * math.sin(ph), yy, 7, fill=A(PINK, 0.35))
        d.circ(1020 + 30 * math.sin(ph), yy, 7, fill=A(CYAN, 0.35)); d.circ(1020 - 30 * math.sin(ph), yy, 7, fill=A(PINK, 0.35))
    g = eio(pr(t, GROW[0], GROW[1]))
    col = A(CYAN, 1); W_ = 10
    def el(x0, y0, x1, y1, u):
        if u <= 0: return
        pts = [(x0, y0), (x0, y1), (x1, y1)] if False else [(x0, y0), (x1, y0), (x1, y1)]
        L1 = abs(x1 - x0); L2 = abs(y1 - y0); L = (L1 + L2) * u
        if L <= L1: d.line([(x0, y0), (x0 + math.copysign(L, x1 - x0), y0)], col, W_)
        else: d.line([(x0, y0), (x1, y0), (x1, y0 - (L - L1))], col, W_)
    root = (540, 1540)
    d.line([root, (540, 1420)], col, W_)
    el(540, 1420, 150, 820, pr(g, 0, 0.4)); el(540, 1420, 640, 1300, pr(g, 0, 0.2))
    el(640, 1300, 340, 820, pr(g, 0.2, 0.6)); el(640, 1300, 740, 1170, pr(g, 0.2, 0.4))
    el(740, 1170, 530, 820, pr(g, 0.4, 0.8)); el(740, 1170, 815, 1020, pr(g, 0.4, 0.6))
    el(815, 1020, 720, 820, pr(g, 0.6, 1.0))
    tin = pr(t, TERM_IN, TERM_IN + 0.3)
    if tin > 0:
        d.line([(815, 1020), (910, 1020), (910, 1020 - 200 * ease(tin))], A(YEL, 1), 14)
    hl = ease(pr(t, STAMP1, STAMP1 + 0.3))
    if hl > 0:
        d.rect(250, 600, 1010, 1340, outline=A(ORANGE, hl), w=8, r=40)
        d.text(630, 1390, "蟑螂家族", 54, A(ORANGE, hl), k=1)
        d.rect(640, 620, 990, 800, outline=A(MINT, hl * (0.6 + 0.4 * math.sin(t * 8))), w=6, r=30)
    for i, (nm, lx) in enumerate(LEAVES):
        if nm == "白蚁":
            if tin <= 0: continue
            bug(d, lx, 680 - 300 * (1 - ease(tin)), 70, t, 0.0, "shock" if t < STAMP1 else "proud")
            d.text(lx, 790, nm, 46, A(YEL, 1), k=1)
        else:
            ka = pr(g, 0.25 * i - 0.05, 0.25 * i + 0.15) if i else pr(g, 0.3, 0.45)
            if ka > 0:
                if nm == "螳螂": d.text(lx, 600, "🦗", 1, A(WHITE, 0))
                bug(d, lx, 680, 70 * ease(ka), t, 1.0 if nm != "螳螂" else 0.5, "chill", col=(90, 170, 80) if nm == "螳螂" else None)
                d.text(lx, 790, nm, 44, A(WHITE, ka), k=1)
def u_tree(t, d):
    if t < STAMP1:
        d.text(540, 260, "2007 · 测 DNA", 90, A(WHITE, ease(pr(t, TREE0, TREE0 + 0.3))), k=1)
        d.text(540, 380, "107 种虫子 × 5 个基因", 56, A(CYAN, ease(pr(t, TREE0 + 0.4, TREE0 + 0.7))), k=1)
    elif t < ORDER_X:
        stamp(d, t, STAMP1, "白蚁 = 社会性蟑螂", 540, 300, 96, YEL)
    else:
        k = back(pr(t, ORDER_X, ORDER_X + 0.2))
        outline_text(d, 540, 300, "白蚁目", int(150 * k) + 1, WHITE)
        if t > ORDER_X + 0.3:
            u = ease(pr(t, ORDER_X + 0.3, ORDER_X + 0.5))
            d.line([(300, 300), (300 + 480 * u, 300)], A(WARN, 1), 26)
        stamp(d, t, ORDER_X + 0.6, "已除名", 540, 450, 90, WARN)
    flash(d, t, [ORDER_X], WHITE, 0.6)

def w_masto(t, d):
    if t < XRAY:
        grad(d, (230, 120, 60), (120, 50, 24))
        for i, (mx, mh) in enumerate(((120, 520), (930, 680), (300, 380), (780, 420))):
            d.poly([(mx - 90, 1500), (mx - 30, 1500 - mh), (mx + 10, 1500 - mh - 40), (mx + 60, 1500 - mh + 30), (mx + 100, 1500)], A((160, 70, 30), 0.8))
        d.rect(0, 1480, 1080, 1920, fill=A((150, 70, 34), 1))
        if t < EGG:
            bug(d, 540, 1150, 240 * back(pr(t, MASTO, MASTO + 0.3)) + 1, t, 0.0, "chill", walk=t * 0.4, look=math.sin(t * 2))
        else:
            ke = back(pr(t, EGG, EGG + 0.3))
            bug(d, 290, 1000, 120, t, 1.0, "proud" if t > SAME else "chill")
            bug(d, 790, 1000, 120, t, 0.0, "proud" if t > SAME else "chill")
            ootheca(d, 290, 1330, 150 * ke + 1, col=ROACH)
            ootheca(d, 790, 1330, 150 * ke + 1, col=(196, 140, 80))
            d.text(290, 780, "蟑螂", 56, A(WHITE, 1), k=1); d.text(790, 780, "巨达尔文白蚁", 50, A(WHITE, 1), k=1)
            if t > SAME:
                outline_text(d, 540, 1330, "=", int(160 * back(pr(t, SAME, SAME + 0.2))) + 1, YEL)
    else:
        grad(d, (8, 16, 40), (2, 4, 14))
        for i in range(0, 1080, 60): d.line([(i, 0), (i, 1920)], A(CYAN, 0.06), 2)
        xr = ease(pr(t, XRAY, XRAY + 0.3))
        bug(d, 290, 1150, 170, t, 1.0, "shock", xray=xr)
        bug(d, 790, 1150, 170, t, 0.0, "shock", xray=xr)
        d.text(290, 1500, "蟑螂", 50, A(WHITE, 1), k=1); d.text(790, 1500, "白蚁", 50, A(WHITE, 1), k=1)
def u_masto(t, d):
    if t < EGG:
        outline_text(d, 540, 290, "最原始的白蚁", int(110 * back(pr(t, MASTO, MASTO + 0.25))) + 1, WHITE)
        d.text(540, 440, "巨达尔文白蚁 · 澳大利亚", 56, A(YEL, ease(pr(t, MASTO + 0.4, MASTO + 0.7))), k=1)
    elif t < XRAY:
        d.text(540, 300, "下蛋方式", 90, A(WHITE, 1), k=1)
        if t > SAME: stamp(d, t, SAME, "同款卵鞘", 540, 470, 130, YEL)
    else:
        outline_text(d, 540, 300, "X 光一照", 100, WHITE)
        if t > XRAY + 0.8: stamp(d, t, XRAY + 0.8, "同一种共生菌", 540, 470, 110, PINK)
        d.text(540, 600, "Blattabacterium", 44, A(PINK_L, ease(pr(t, XRAY + 1.4, XRAY + 1.7))), k=0)
    flash(d, t, [SAME, XRAY], WHITE, 0.6)

def w_rew(t, d):
    if t < DINO or REW2 <= t:
        tunnel(d, t)
        bug(d, 540, 1400, 150, t, 1.0, "shock", walk=t)
    elif t < IMPACT:
        grad(d, (255, 150, 80), (120, 60, 50))
        d.rect(0, 1420, 1080, 1920, fill=A((80, 60, 40), 1))
        dino(d, 420 + (t - DINO) * 40, 1250, 230)
        u = pr(t, DINO, IMPACT)
        mx, my = lerp(1100, 560, u), lerp(-100, 1200, u); mr = lerp(40, 120, u)
        for i in range(10): d.circ(mx + i * 30 * (1 - 0.05 * i), my - i * 55, mr * (1 - i * 0.08), fill=A(ORANGE, 0.5 * (1 - i / 10)))
        glow(d, mx, my, mr * 2, YEL, 1); d.circ(mx, my, mr, fill=A((255, 240, 200), 1))
        bug(d, 820, 1500, 55, t, 1.0, "scared", walk=t)
    else:
        grad(d, (60, 50, 50), (14, 10, 10)); embers(d, t, ORANGE, 1.0, 40)
        u = pr(t, IMPACT, IMPACT + 1.2)
        for j in range(3): d.circ(540, 1300, 200 + u * 1600 + j * 80, outline=A(WHITE, (1 - u) * 0.8), w=30)
        for i in range(9):
            d.poly(rpoly(150 + i * 100, 1550 + (i % 3) * 30, 110, 60, i * 0.4, 7), A((70, 60, 55), 1))
        d.text(330, 1420, "🦴", 1, A(WHITE, 0))
        for bx in (260, 330, 400): d.rect(bx, 1430, bx + 40, 1460, fill=A((230, 220, 200), 0.8), r=12)
        k = back(pr(t, SURVIVE, SURVIVE + 0.3))
        if t > SURVIVE: bug(d, 640, 1480 - 150 * ease(pr(t, SURVIVE, SURVIVE + 0.3)), 130 * k + 1, t, 1.0, "proud")
def u_rew(t, d):
    if t < DINO: d.text(540, 300, "倒带 ◀◀", 100, A(WHITE, 1), k=1); counter(d, t, REW + 0.5, DINO - 0.3, 0, 6600)
    elif t < IMPACT: d.text(540, 300, "6600 万年前", 100, A(OL, 1), k=1)
    elif t < REW2:
        if t > SURVIVE: outline_text(d, 540, 420, "它还在！", int(170 * back(pr(t, SURVIVE, SURVIVE + 0.2))) + 1, YEL)
    else:
        d.text(540, 300, "继续倒带 ◀◀", 90, A(WHITE, 1), k=1); counter(d, t, REW2 + 0.3, REW2 + 3.0, 6600, 20000)
        if t > 43.6: stamp(d, t, 43.6, "签下长期合同", 540, 960, 110, PINK)
    flash(d, t, [IMPACT], WHITE, 1.0)
    if SILENCES[0][0] <= t < IMPACT: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.3))

def w_bact(t, d):
    grad(d, (60, 14, 40), (14, 2, 12))
    if t < EGGS2:
        cr = 440
        d.circ(540, 1040, cr + 14, fill=A((255, 160, 200), 0.25)); d.circ(540, 1040, cr, fill=A((120, 30, 70), 1))
        rnd = random.Random(3)
        n = int(16 * ease(pr(t, BACT, RECYCLE)))
        for i in range(16):
            cx, cy = 540 + rnd.uniform(-380, 380), 1040 + rnd.uniform(-380, 380)
            if i >= n: continue
            conv = ease(pr(t, RECYCLE + 0.5 + i * 0.1, RECYCLE + 0.8 + i * 0.1)) if t > RECYCLE else 0
            if conv < 1: d.poly([(cx, cy - 34), (cx + 24, cy), (cx, cy + 34), (cx - 24, cy)], A(WHITE, 1 - conv))
            if conv > 0:
                glow(d, cx, cy, 60, YEL, conv * 0.8, 4); d.circ(cx, cy, 14 * conv, fill=A(YEL, conv))
        if t > RECYCLE:
            for i in range(6):
                ang = t * 1.5 + i
                bx, by = 540 + math.cos(ang) * 300, 1040 + math.sin(ang * 1.3) * 300
                d.poly(rpoly(bx, by, 50, 18, ang + 1.2, 12), A(PINK_L, 1))
                d.poly(rpoly(bx, by, 40, 10, ang + 1.2, 12), A(PINK, 1))
    else:
        ootheca(d, 540, 1000, 400, glowk=1.0, filled=pr(t, EGGS2 + 0.3, PASS))
        bug(d, 540, 1450, 130, t, 1.0, "proud" if t > PASS else "chill")
        if t > PASS + 1.0:
            for i in range(6):
                xx = (i * 220 - (t - PASS) * 300) % 1320 - 120
                bug(d, xx, 1720, 40, t, 1.0, "chill", walk=t)
                glow(d, xx, 1720, 30, PINK, 1, 3)
def u_bact(t, d):
    if t < GLU:
        outline_text(d, 540, 290, "身体里存尿", int(130 * back(pr(t, BACT, BACT + 0.25))) + 1, WHITE)
        d.text(540, 440, "尿酸晶体 · 存在脂肪体里", 50, A(PINK_L, ease(pr(t, BACT + 0.5, BACT + 0.8))), k=1)
    elif t < EGGS2:
        stamp(d, t, GLU, "回收成谷氨酸", 540, 330, 120, YEL)
    else:
        d.text(540, 300, "妈妈打包细菌", 100, A(WHITE, 1), k=1)
        if t > PASS: stamp(d, t, PASS, "每颗卵都有", 540, 460, 120, PINK)
    flash(d, t, [GLU, PASS], WHITE, 0.6)

def w_carb(t, d):
    grad(d, (40, 90, 60), (8, 26, 16))
    for i in range(7):
        fx = i * 180 + 30 * math.sin(t * 0.5 + i); fy = 1500
        for j in range(14):
            ang = -math.pi / 2 + (j - 7) * 0.12
            d.line([(fx, fy), (fx + math.cos(ang) * 600, fy + math.sin(ang) * 900)], A((20, 60, 30), 0.7), 18)
    d.rect(0, 1480, 1080, 1920, fill=A((30, 50, 26), 1))
    for i in range(10):
        y = 700 + i * 90; d.rect(0, y, 1080, y + 40, fill=A(WHITE, 0.03))
    bug(d, 540 + 40 * math.sin(t), 1300, 150 * back(pr(t, ROACH0, ROACH0 + 0.3)) + 1, t, 1.0, "scared" if t > BIGFLY else "chill", col=ANC, tail=True, walk=t)
    if t > BIGFLY:
        u = pr(t, BIGFLY, BIGFLY + 3.0); fx, fy = lerp(-400, 1500, u), 760 + 80 * math.sin(u * 6)
        for s_ in (-1, 1):
            for dy in (-40, 40):
                wing = 0.3 + 0.7 * abs(math.sin(t * 30))
                d.ell(fx + dy * 1.5, fy + s_ * 300 * wing * 0.5, 70, 300 * wing * 0.5 + 10, A((200, 230, 255), 0.5))
        d.line([(fx - 300, fy), (fx + 120, fy)], A((40, 80, 160), 1), 48)
        d.circ(fx + 140, fy, 50, fill=A((40, 80, 160), 1)); d.circ(fx + 160, fy - 20, 18, fill=A(WHITE, 1))
def u_carb(t, d):
    outline_text(d, 540, 290, "3 亿年前", int(150 * back(pr(t, CARB, CARB + 0.25))) + 1, YEL)
    d.text(540, 450, "石炭纪 · 老祖宗", 64, A(WHITE, ease(pr(t, CARB + 0.4, CARB + 0.7))), k=1)
    if t > BIGFLY: stamp(d, t, BIGFLY, "翼展 70 厘米", 540, 1050, 96, CYAN)
    flash(d, t, [CARB, BIGFLY], WHITE, 0.6)

def w_end(t, d):
    grad(d, (14, 20, 46), (4, 6, 14))
    for i in range(0, 1080, 120):
        for j in range(1480, 1920, 120): d.rect(i + 4, j + 4, i + 116, j + 116, fill=A((30, 38, 70), 1))
    d.rect(600, 500, 1040, 1480, fill=A((200, 210, 225), 1), r=30); d.rect(610, 900, 1030, 910, fill=A((150, 160, 180), 1))
    d.rect(600, 1480, 1040, 1500, fill=A((255, 240, 180), 0.8))
    glow(d, 820, 1490, 260, (255, 240, 180), 0.5)
    k = ease(pr(t, OUTRO + 0.3, OUTRO + 1.0))
    bug(d, lerp(900, 520, k), 1560, 110, t, 1.0, "proud" if t > OUTRO + 1.0 else "chill", walk=t * (1 - k))
    if t > LAST - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0))
def u_end(t, d):
    d.text(540, 280, "你厨房那只", int(110 * back(pr(t, OUTRO, OUTRO + 0.25))) + 1, A(WHITE, 1), k=1)
    outline_text(d, 540, 440, "3 亿年老字号", int(140 * back(pr(t, OUTRO + 0.6, OUTRO + 0.85))) + 1, YEL)
    a = ease(pr(t, OUTRO + 1.6, OUTRO + 2.0))
    d.rect(90, 600, 990, 700, fill=A((0, 0, 0), 0.6 * a), r=30)
    d.text(540, 650, "白蚁和蟑螂，你更怕哪个？", 52, A(WHITE, a), k=1)
    d.text(540, 1800, "Inward et al. 2007 Biol Lett · Sabree et al. 2009 PNAS · Nalepa & Lenz 2000 Proc B", 22, A(WHITE, 0.75 * a), k=0)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

SECS = [(0, HOOK_END, w_hook, u_hook), (TREE0, MASTO, w_tree, u_tree), (MASTO, REW, w_masto, u_masto), (REW, BACT, w_rew, u_rew),
        (BACT, CARB, w_bact, u_bact), (CARB, OUTRO, w_carb, u_carb), (OUTRO, 99, w_end, u_end)]
CUTS = [HOOK_END, MASTO, EGG, XRAY, REW, DINO, IMPACT, REW2, BACT, EGGS2, CARB, OUTRO]

def subs(t, d):
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.12)) * (1 - pr(t, b - 0.1, b))
            lines = wrap(d, s, 58, 920)
            for j, ln in enumerate(lines):
                y = 1660 + (j - (len(lines) - 1) / 2) * 84
                w = d.tlen(ln, 58)
                d.rect(540 - w / 2 - 24, y - 44, 540 + w / 2 + 24, y + 44, fill=A((0, 0, 0), 0.62 * al), r=16)
                d.text(540, y, ln, 58, A(WHITE, al))
def brand(t, d):
    d.rect(50, 80, 300, 128, fill=A(WHITE, 0.92), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(BG, 1))
    d.rect(800, 80, 1030, 128, fill=A((170, 90, 40), 0.95), r=24); d.text(915, 104, "蟑螂寻祖", 26, A(WHITE, 1))

def cam(t):
    z = 1.0 + 0.07 * pulse(t, HITS, 7)
    if t < 0.5: z += 0.1 * (1 - ease(pr(t, 0, 0.3)))
    for a, b in RISERS:
        if a <= t < b: z += 0.1 * eio(pr(t, a, b))
    amp = 30 * pulse(t, [MORPH, IMPACT, BIGFLY], 3) + 12 * pulse(t, HITS, 5)
    if REW <= t < DINO or REW2 <= t < BACT: amp += 4
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
