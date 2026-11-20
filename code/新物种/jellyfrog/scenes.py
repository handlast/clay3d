# 《果冻蛙》scenes — every subtitle line gets its OWN set, composition and demo (user rule 2026-11-16).
# Flat 2D, no dark outlines (eye/mouth lines only). Content in x 180–900, above the subtitle box (y < ~1230) except card.
# Entities never pop: they spring-scale in from 0, slide/hop in, and fade out over >= 0.3 s with their own times.
import math, random
from PIL import Image, ImageDraw
from jchars import *
from cues import *

# ---------------- helpers ----------------
def popk(t, t0, preset="snappy"): return max(0.0, E.spring_at(t, t0, 0, 1, preset)) if t >= t0 else 0.0
def ap(t, t0, d=0.3): return cl((t - t0) / d)
def tag(d, x, y, s, col, a=1.0, size=40, tc=NAVYT, k=1):
    if a <= 0.01: return
    w = d.tlen(s, size, k) + 44
    d.rect(x - w / 2, y - size * 0.78, x + w / 2, y + size * 0.78, fill=A(col, 0.95 * a), r=size * 0.6)
    d.text(x, y, s, size, A(tc, a), k=k)
def ptag(d, t, t0, x, y, s, col, size=40, tc=NAVYT, t1=None, k=1):
    kk = popk(t, t0)
    if kk <= 0: return
    al = min(1, ap(t, t0, 0.15))
    if t1 is not None: al *= 1 - pr(t, t1 - 0.3, t1)
    tag(d, x, y + (1 - min(kk, 1)) * 30, s, col, al, int(size * (0.6 + 0.4 * min(1.1, kk))), tc, k)
def arrow(d, x0, y0, x1, y1, col, a=1.0, w=12):
    L = math.hypot(x1 - x0, y1 - y0) + 1e-6; ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    bx, by = x1 - ux * w * 2.4, y1 - uy * w * 2.4
    d.line([(x0, y0), (bx, by)], A(col, a), w); d.poly([(bx + nx * w * 1.6, by + ny * w * 1.6), (x1, y1), (bx - nx * w * 1.6, by - ny * w * 1.6)], A(col, a))
def check_mark(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 18 * s_, y), (x - 4 * s_, y + 14 * s_), (x + 20 * s_, y - 14 * s_)], A(WHITE, a), 8 * s_)
def xmark(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0 or a <= 0.01: return
    k1 = cl(k * 2); k2 = cl(k * 2 - 1)
    d.line([(x - r, y - r), (x - r + 2 * r * k1, y - r + 2 * r * k1)], A(col, a), r * 0.28)
    if k2 > 0: d.line([(x + r, y - r), (x + r - 2 * r * k2, y - r + 2 * r * k2)], A(col, a), r * 0.28)
def zap(d, x, y, t, t0, col=WHITE, maxr=380, a=1.0):
    u = (t - t0) / 0.7
    if 0 <= u < 1:
        for j in range(3): d.circ(x, y, 30 + (u + j * 0.1) * maxr, outline=A(col, a * (1 - u) * (1 - j * 0.3)), w=10 - j * 3)
def bubble(d, x, y, w, h, a=1.0, col=WHITE, tail=(0, 1)):
    d.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=A(col, a), r=min(w, h) * 0.4)
    tx, ty = tail; d.poly([(x - 18, y + h / 2 - 4), (x + 18, y + h / 2 - 4), (x + tx * 40, y + h / 2 + ty * 40)], A(col, a))
def hop(t, t0, h=60, dur=0.35):
    u = (t - t0) / dur
    return -h * 4 * u * (1 - u) if 0 <= u <= 1 else 0.0
def dashed(d, pts, col, a, w=4, on=14, off=10):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0) + 1e-6; n = int(L // (on + off)) + 1
        for i in range(n):
            u0 = i * (on + off) / L; u1 = min(1, (i * (on + off) + on) / L)
            if u0 < 1: d.line([(lerp(x0, x1, u0), lerp(y0, y1, u0)), (lerp(x0, x1, u1), lerp(y0, y1, u1))], A(col, a), w)
def dcirc(d, x, y, r, col, a, w=5, n=36, rot_=0.0):
    for i in range(n):
        if i % 2: continue
        a0 = rot_ + 2 * math.pi * i / n; a1 = rot_ + 2 * math.pi * (i + 1) / n
        d.line([(x + math.cos(a0) * r, y + math.sin(a0) * r), (x + math.cos(a1) * r, y + math.sin(a1) * r)], A(col, a), w)
def grid(d, col, a, step=90, x0=-90, x1=1170, y0=-90, y1=2010, w=2):
    i = 0
    while x0 + i * step <= x1: d.line([(x0 + i * step, y0), (x0 + i * step, y1)], A(col, a), w); i += 1
    j = 0
    while y0 + j * step <= y1: d.line([(x0, y0 + j * step), (x1, y0 + j * step)], A(col, a), w); j += 1
def sbox(d, x0, y0, x1, y1, col, a=1.0, r=24, sh=0.22):
    d.rect(x0 + 12, y0 + 16, x1 + 12, y1 + 16, fill=A((0, 0, 0), sh * a), r=r); d.rect(x0, y0, x1, y1, fill=A(col, a), r=r)
def bigword(d, t, t0, x, y, s, size, col, t1=None, k=1):
    kk = popk(t, t0, "bouncy") if t >= t0 else 0
    if kk <= 0: return
    al = min(1, ap(t, t0, 0.1)) * (1 if t1 is None else 1 - pr(t, t1 - 0.35, t1))
    if al <= 0.01: return
    d.text(x, y, s, max(8, int(size * (0.5 + 0.5 * min(1.15, kk)))), A(col, al), k=k)
def fireflies(d, t, n=14, seed=11, a=1.0, box=(80, 300, 1000, 1150)):
    rr = random.Random(seed)
    for i in range(n):
        x0, y0, ph = rr.uniform(box[0], box[2]), rr.uniform(box[1], box[3]), rr.uniform(0, 6.28)
        x = x0 + 30 * math.sin(t * 0.7 + ph); y = y0 + 20 * math.sin(t * 0.9 + ph * 1.3)
        b = 0.5 + 0.5 * math.sin(t * 2.3 + ph * 2)
        glow_disc(d, x, y, 24, (220, 255, 170), 0.6 * b * a); d.circ(x, y, 4, fill=A((240, 255, 210), (0.5 + 0.5 * b) * a))
def spot(d, x, y, r, a, col=(255, 236, 190)):
    for i in range(8): d.circ(x, y, r * (1 - i * 0.1), fill=A(col, (0.025 + 0.012 * i) * a))


def night_bg(d, t, top=(14, 40, 46), bot=(6, 16, 20), stars=True, seed=3):
    grad(d, top, bot)
    if stars:
        rr = random.Random(seed)
        for i in range(40):
            sx, sy = rr.uniform(0, 1080), rr.uniform(260, 900); d.circ(sx, sy, rr.uniform(1.5, 3.2), fill=A(WHITE, 0.25 + 0.2 * math.sin(t * 2 + i)))
def rain(d, t, a=0.5, n=46, seed=8, col=(190, 220, 230)):
    rr = random.Random(seed)
    for i in range(n):
        x0 = rr.uniform(-100, 1180); sp = rr.uniform(900, 1300); ph = rr.uniform(0, 3000)
        y = (ph + t * sp) % 2200 - 140; x = x0 - (y + 140) * 0.12
        d.line([(x, y), (x - 6, y + 46)], A(col, a * rr.uniform(0.3, 0.8)), 2)
def odometer(d, x, y, val, size, col, a=1.0):
    d.text(x, y, val, size, A(col, a), k=1)
def card_box(d, x0, y0, x1, y1, a, col=(250, 248, 238), r=28): sbox(d, x0, y0, x1, y1, col, a, r)

# ======== 1. hook: jelly blob on a branch over water; tadpoles wriggle; a flying frog glides in at 0 s ========
def hook_set(d, t, u_frog=None, jelly_r=190, jx=540, jy=760, jig=0.0, big=True):
    night_bg(d, t, (12, 44, 52), (6, 18, 24))
    mist(d, t, 1.2, 600, 6)
    pond(d, 1150, t, 1, (16, 46, 60), (60, 120, 140))
    jelly(d, jx, 1250 + (1250 - jy) * -0.15, jelly_r * 0.8, t, 0.18, 10, 0.95, 3, 0.4)        # faint reflection
    branch(d, -40, 470, 1120, 410, 34, 1, t, 6, 4)
    d.line([(jx - 10, 452), (jx, jy - jelly_r * 0.9)], A(BRANCH_L, 1), 12)                         # twig it hangs from
    for sd in (-1, 1): leaf_shape(d, jx + sd * 60, jy - jelly_r - 40, 150, -1.57 + sd * 1.0, LEAFG_L, 1)
    wob = 1 + 3.0 * jig
    jelly(d, jx + 6 * jig * math.sin(t * 22), jy, jelly_r, t, 1, 15, 0.92, 3, wob, 0.35 + 0.35 * jig, 1, 1.6)
def s_hook(t, d):
    u = t
    jig = math.exp(-max(0, u) * 2.5)
    hook_set(d, t, jig=jig)
    # frog glides in from the top-right at 0 s, lands on the branch at ~1.1 s, then sits
    k = E.ease_out_cubic(pr(u, -0.2, 1.1))
    ga = 1 - pr(u, 0.95, 1.3)
    if ga > 0:
        gx, gy = lerp(1040, 820, k), lerp(160, 360, k) + 40 * math.sin(k * 3.1)
        jfrog_glide(d, gx, gy, 0.75, t, ga, lerp(2.4, 2.0, k), 1.0 - 0.5 * pr(u, 0.9, 1.3), 0.7)
    if u > 0.95:
        kk = popk(t, 0.95)
        jfrog(d, 820, 360 + hop(u, 1.1, 30, 0.3), 0.5 * (0.9 + 0.1 * min(1.1, kk)), t, ap(u, 0.95, 0.35), "shock" if u < 2.4 else "happy", look=-0.8, seed=0.2)
    zap(d, 540, 760, t, 0.0, GEL_L, 520, 0.8)
    bigword(d, t, -0.12, 540, 1120, "在扭！", 160, GOLD, 2.6)
    bigword(d, t, 0.10, 420, 330, "果冻？", 170, GEL_L, 2.6)

# ======== 2. lake: high mountain lake at dusk — thousands of green frogs calling ========
_lr = random.Random(5)
LAKE_FROGS = []
for _i in range(40):
    _row = _i // 10; _y = 860 + _row * 90; _sc = 0.12 + _row * 0.035
    LAKE_FROGS.append((180 + (_i % 10) * 80 + _lr.uniform(-25, 25) + (_row % 2) * 30, _y + _lr.uniform(-20, 20), _sc, _lr.uniform(0.2, 1.8), _lr.uniform(0, 6.28)))
def s_lake(t, d):
    t0 = T["lake"]; u = t - t0
    grad(d, (60, 50, 104), (22, 60, 80), 0, 900)
    d.rect(-40, 880, 1120, 1960, fill=A((30, 70, 56), 1))
    for j, (c, y0, amp) in enumerate((((54, 60, 110), 640, 240), ((40, 74, 90), 720, 170))):
        r2 = random.Random(30 + j); pts = [(-60, 1000)]; x = -60
        while x < 1160: pts.append((x, y0 - r2.uniform(0.3, 1.0) * amp)); x += r2.uniform(100, 180)
        pts.append((1160, 1000)); d.poly(pts, A(c, 1))
    d.ell(540, 820, 520, 90, A((70, 120, 150), 1)); d.ell(540, 812, 470, 64, A((110, 160, 190), 0.6))   # the small lake
    for i in range(8): d.line([(220 + i * 80 + (t * 20) % 40, 800 + (i % 3) * 18), (270 + i * 80 + (t * 20) % 40, 800 + (i % 3) * 18)], A((180, 220, 240), 0.4), 3)
    mist(d, t, 1.4, 640, 6)
    for (x, y, sc, td, ph) in LAKE_FROGS:
        kk = popk(t, t0 + td * 0.8)
        if kk <= 0: continue
        sac = max(0, math.sin(t * 5 + ph)) ** 2 if u > td * 0.8 + 0.3 else 0
        jfrog(d, x, y + hop(u, td * 0.8, 20, 0.3), sc * min(1.1, kk), t, ap(u, td * 0.8, 0.2), "happy" if ph > 3 else "calm", look=math.sin(ph), sac=sac, seed=ph)
    for i in range(10):                                                   # music notes rising = chorus
        st = 0.6 + i * 0.35; v = u - st
        if v < 0: continue
        vv = (v % 2.2) / 2.2; nx_ = 220 + (i * 71) % 640; ny_ = 900 - vv * 520
        al = math.sin(math.pi * vv) * 0.8
        d.circ(nx_, ny_, 13, fill=A(JG_H, al)); d.line([(nx_ + 11, ny_), (nx_ + 11, ny_ - 46)], A(JG_H, al), 5)
    ka = popk(t, t0 + 1.2)
    if ka > 0:
        al = ap(u, 1.2, 0.2); n = int(1000 * E.ease_out_cubic(pr(u, 1.2, 2.8)))
        sbox(d, 600, 300, 900, 420, (20, 30, 50), 0.75 * al, 30)
        jfrog(d, 660, 378, 0.17, t, al, "happy", seed=1); odometer(d, 790, 360, f"×{n}+", 58, GOLD, al)

# ======== 3. q: whose jelly is this? spotlight + magnifier + mystery card ========
def s_q(t, d):
    t0 = T["q"]; u = t - t0
    grad(d, (16, 22, 30), (6, 8, 12))
    spot(d, 540, 760, 560, 1.2, (200, 255, 240))
    branch(d, -40, 420, 1120, 400, 30, 0.9, t, 4, 9)
    d.line([(540, 410), (540, 560)], A(BRANCH_L, 1), 12)
    jelly(d, 540, 760, 230, t, 1, 16, 0.92, 3, 1.0, 0.4, 1, 1.4)
    gk = 0.5 + 0.5 * math.sin(t * 5)
    bigword(d, t, t0 + 0.2, 300, 520, "?", 260, mix((150, 230, 220), WHITE, 0.3 * gk))
    mx = 540 + 200 * math.sin(u * 1.6); my = 800 + 60 * math.cos(u * 1.3); ma = ap(u, 0.3, 0.3)
    if ma > 0:
        d.circ(mx, my, 110, fill=A((220, 255, 250), 0.18 * ma))
        tadpole_dir(d, mx - 20, my, 0.7, t * 1.3, ma, 0.4 * math.sin(t))
        d.circ(mx, my, 110, outline=A((240, 240, 230), ma), w=12)
        d.line([(mx + 78, my + 78), (mx + 150, my + 150)], A((180, 150, 110), ma), 26)
    kk = popk(t, t0 + 1.0)
    if kk > 0:
        al = ap(u, 1.0, 0.2); x0 = 610; y0 = 980 + (1 - min(1, kk)) * 80
        sbox(d, x0, y0, x0 + 270, y0 + 180, (240, 236, 220), al, 20)
        d.rect(x0 + 20, y0 + 22, x0 + 100, y0 + 112, fill=A((120, 130, 150), al), r=10); d.text(x0 + 60, y0 + 67, "?", 60, A(WHITE, al), k=1)
        for j in range(3): d.rect(x0 + 120, y0 + 30 + j * 30, x0 + 250 - j * 20, y0 + 44 + j * 30, fill=A((190, 186, 176), al), r=6)
        d.text(x0 + 135, y0 + 148, "妈妈：？？？", 32, A((90, 80, 70), al), k=1)

# ======== 4. BIG2: a new flying frog — babies raised in jelly ========
def s_big2(t, d):
    t0 = T["big2"]; u = t - t0
    rays(d, t, (120, 220, 110), (40, 120, 70), 18, 540, 760)
    for i in range(16):                                                    # confetti burst
        ang = i * 2 * math.pi / 16 + 0.2; v = cl(u / 1.2); r_ = 120 + 520 * E.ease_out_cubic(v)
        al = (1 - pr(u, 0.9, 1.3))
        if al > 0: d.circ(540 + math.cos(ang) * r_, 760 + math.sin(ang) * r_, 14, fill=A([GOLD, JG_H, GEL_L, JWEB][i % 4], al))
    kk = popk(t, t0, "bouncy")
    jfrog(d, 600, 840 + hop(u, 0.0, 160, 0.5), 1.15 * (0.6 + 0.4 * min(1.1, kk)), t, 1, "proud" if u > 0.6 else "shock", seed=0.4)
    jk = popk(t, t0 + 0.5)
    if jk > 0:
        jelly(d, 250, 900, 110 * min(1.1, jk), t, ap(u, 0.5, 0.2), 10, 0.9, 6, 1.0, 0.5)
        hk = ap(u, 0.9, 0.3); hy = 760 - 30 * math.sin(u * 3)
        if hk > 0:
            for sd in (-1, 1): d.circ(250 + sd * 16, hy, 20, fill=A((255, 110, 140), hk))
            d.poly([(250 - 36, hy + 6), (250 + 36, hy + 6), (250, hy + 46)], A((255, 110, 140), hk))
    bigword(d, t, t0 + 0.05, 540, 400, "新物种！", 170, GOLD)
    sk = popk(t, t0 + 1.2, "bouncy")
    if sk > 0:
        al = ap(u, 1.2, 0.2); sc = 1.6 - 0.6 * min(1, sk); cx, cy = 790, 610
        d.d.ellipse((P(cx - 95 * sc), P(cy - 95 * sc), P(cx + 95 * sc), P(cy + 95 * sc)), outline=A((230, 50, 50), al), width=int(P(10 * sc)))
        d.text(cx, cy - 18 * sc, "2026", int(44 * sc), A((230, 50, 50), al), k=1); d.text(cx, cy + 30 * sc, "命名", int(36 * sc), A((230, 50, 50), al), k=1)
    ptag(d, t, t0 + 0.8, 540, 1130, "Rhacophorus kurniatiae", (250, 248, 236), 40, NAVYT, k=0)

# ======== 5. glide: tree to tree with webbed feet as parachutes ========
def s_glide(t, d):
    t0 = T["glide"]; u = t - t0
    grad(d, (24, 50, 96), (40, 96, 110))
    glow_disc(d, 800, 380, 160, (240, 250, 220), 0.6); d.circ(800, 380, 56, fill=A((240, 246, 226), 1))
    mist(d, t, 1.2, 700, 6)
    for x, w, c in ((110, 90, (30, 50, 46)), (980, 100, (26, 46, 44))):
        d.rect(x - w / 2, 300, x + w / 2, 1960, fill=A(c, 1))
        d.circ(x, 300, 260, fill=A((26, 70, 54), 1)); d.circ(x + (60 if x < 500 else -60), 380, 180, fill=A((34, 86, 62), 1))
    d.line([(110, 560), (330, 540)], A(BRANCH, 1), 24); d.line([(980, 1000), (760, 980)], A(BRANCH, 1), 24)
    k = E.ease_in_out_sine(pr(u, 0.4, 3.2))
    path = lambda kk: (lerp(300, 790, kk), lerp(500, 920, kk) - 160 * math.sin(math.pi * kk))
    if u > 0.4:
        pts = [path(j / 30 * k) for j in range(31)]
        dashed(d, pts, WHITE, 0.5 * ap(u, 0.4, 0.3), 5)
    gx, gy = path(k)
    sp = E.ease_out_cubic(pr(u, 0.3, 0.9)) * (1 - 0.7 * pr(u, 3.1, 3.5))
    ga = 1 - pr(u, 3.15, 3.5)
    if ga > 0:
        for i in range(5):                                                       # wind streaks
            ww = ((u * 2 + i * 0.2) % 1); al = math.sin(math.pi * ww) * 0.5 * sp
            d.line([(gx - 160 - ww * 200, gy - 60 + i * 30), (gx - 60 - ww * 200, gy - 60 + i * 30)], A(WHITE, al), 4)
        jfrog_glide(d, gx, gy, 0.8, t, ga, math.atan2(path(min(1, k + 0.02))[1] - gy, path(min(1, k + 0.02))[0] - gx + 1e-6), sp, 0.8 * sp)
    if u > 3.15:
        jfrog(d, 790, 900 + hop(u, 3.3, 30, 0.3), 0.42, t, ap(u, 3.15, 0.35), "happy", look=-0.5, seed=0.9)
    ca = ap(u, 1.4, 0.3) * (1 - pr(u, 3.6, 3.9))                                 # callout: foot ≈ parachute
    if ca > 0:
        sbox(d, 260, 960, 640, 1180, (250, 248, 236), ca, 34)
        web_hand(d, 330, 1110, 1.5, ca, -1.57, 5, 52, 0.36, 1.0, glow=0.5)
        d.text(450, 1070, "≈", 70, A(NAVYT, ca), k=1)
        cx, cy = 560, 1060; d.d.pieslice((P(cx - 66), P(cy - 60), P(cx + 66), P(cy + 70)), 180, 360, fill=A((240, 90, 80), ca))
        for sd in (-1, 0, 1): d.line([(cx + sd * 64, cy + 5), (cx, cy + 90)], A(NAVYT, ca), 3)
        d.rect(cx - 12, cy + 86, cx + 12, cy + 110, fill=A(NAVYT, ca), r=4)

# ======== 6. cheek: small enough to sit on a person's cheek ========
def s_cheek(t, d):
    t0 = T["cheek"]; u = t - t0
    grad(d, (255, 216, 180), (250, 170, 140))
    for i in range(10): d.circ(100 + i * 110, 300 + (i % 3) * 600, 50, fill=A(WHITE, 0.12))
    kk = E.ease_out_cubic(pr(u, 0.0, 0.5))
    kid_face(d, 540, 760 + (1 - kk) * 120, 1.0, t, kk, look=0.6 if u > 1.2 else 0.0, face="wow" if 1.0 < u < 2.2 else "smile")
    fx = lerp(1000, 690, E.ease_in_out_sine(pr(u, 0.5, 1.1))); fy = 850 + hop(u, 0.5, 180, 0.6)
    jfrog(d, fx, fy, 0.3, t, ap(u, 0.4, 0.3), "happy", look=-0.6, seed=1.3)
    ra = ap(u, 1.4, 0.3)
    if ra > 0:
        dcirc(d, 690, 830, 120, GOLD, ra * (0.7 + 0.3 * math.sin(t * 6)), 6, 30, t * 0.6)
        ptag(d, t, t0 + 1.6, 780, 1010, "示意", (255, 250, 240), 30, NAVYT)

# ======== 7. jelly: mum lays a gel mass on a plant hanging over water ========
def s_jelly(t, d):
    t0 = T["jelly"]; u = t - t0
    night_bg(d, t, (16, 46, 50), (8, 22, 26), True, 7)
    pond(d, 1040, t, 1, (20, 56, 70), (70, 140, 160))
    branch(d, 1120, 360, 200, 470, 30, 1, t, 6, 11)
    d.line([(560, 436), (560, 560)], A(BRANCH_L, 1), 12)
    for sd in (-1, 1): leaf_shape(d, 560 + sd * 70, 520, 170, -1.57 + sd * 1.1, LEAFG_L, 1)
    jfrog(d, 370, 430, 0.42, t, 1, "calm" if u < 2.0 else "happy", look=0.7, seed=0.3, lift=10 * math.sin(min(1, u / 1.2) * 3.14))
    jk = popk(t, t0 + 0.7, "smooth") if True else 0
    if jk > 0:
        r = 170 * min(1.05, jk)
        jelly(d, 560, 560 + r, r, t, 1, 15, 0.0, 12, 1.0, 0.3)
        jelly(d, 560, 1140 + r * 0.5, r * 0.8, t, 0.16 * min(1, jk), 10, 0.0, 12, 0.5)        # reflection
    aa = ap(u, 2.0, 0.3)
    if aa > 0:
        dashed(d, [(780, 760), (780, 1010)], WHITE, aa * 0.8, 6); arrow(d, 780, 990, 780, 1040, WHITE, aa, 8)
        for j in range(3):
            ph = ((u * 0.7 + j / 3) % 1); d.ell(780, 1060, 40 + ph * 140, 10 + ph * 30, outline=A((180, 230, 240), aa * (1 - ph)), w=4)
    # drops of rain that fall in the water occasionally (rainforest) — continuous
    rain(d, t, 0.25, 30, 4)

# ======== 8. grow: inside the gel, eggs -> embryos -> tadpoles ========
def s_grow(t, d):
    t0 = T["grow"]; u = t - t0; dur = nxt("grow") - t0
    grad(d, (10, 40, 52), (4, 18, 26))
    for r_ in range(6): d.circ(540, 690, 440 - r_ * 8, fill=A((60, 160, 170), 0.04))
    d.circ(540, 690, 400, fill=A((26, 76, 86), 1))
    st = E.ease_in_out_sine(pr(u, 0.3, dur - 0.5))
    jelly(d, 540, 680, 300, t, 1, 12, st, 21, 0.6, 0.0, 1, 1.0)
    d.circ(540, 690, 400, outline=A((220, 230, 230), 1), w=22)                       # microscope ring
    d.circ(540, 690, 422, outline=A((120, 130, 140), 1), w=10)
    # stage track
    xs = (340, 540, 740); y = 1160
    d.line([(340, y), (740, y)], A((90, 120, 130), 1), 8); d.line([(340, y), (lerp(340, 740, st), y)], A(GOLD, 1), 8)
    for i, x in enumerate(xs):
        on = ap(st, i * 0.45, 0.1) if i else 1
        d.circ(x, y, 46, fill=A(mix((40, 60, 70), (250, 248, 236), on), 1))
        if i == 0: d.circ(x, y, 22, fill=A(EGGC, 1)); d.circ(x, y, 10, fill=A(EMB, 1))
        if i == 1: d.circ(x, y, 22, fill=A(EGGC, 1)); d.arc(x, y, 13, 13, 30, 320, A(EMB, 1), 6)
        if i == 2: tadpole_dir(d, x - 8, y, 0.42, t, 1, 0.0)

# ======== 9. foam: side by side — gel mass (new species) vs foam nest (relatives) ========
def s_foam(t, d):
    t0 = T["foam"]; u = t - t0
    sl = E.ease_out_cubic(pr(u, 0.0, 0.5))
    d.rect(-40, -40, 540, 1960, fill=A((22, 66, 74), 1)); d.rect(540, -40, 1120, 1960, fill=A((92, 70, 60), 1))
    for x0, c in ((0, (30, 84, 92)), (540, (112, 88, 74))):
        for i in range(5): d.circ(x0 + 80 + i * 110, 320 + (i % 2) * 900, 70, fill=A(c, 1))
    jx = lerp(-200, 330, sl); fx_ = lerp(1280, 750, sl)
    d.line([(jx - 140, 560), (jx + 140, 560)], A(BRANCH, 1), 20); d.line([(fx_ - 140, 560), (fx_ + 140, 560)], A(BRANCH, 1), 20)
    jelly(d, jx, 760, 160, t, 1, 14, 0.25, 31, 1.0, 0.4)
    leaf_shape(d, fx_, 610, 260, 0.0, LEAFG, 1, 0.5)
    foam(d, fx_, 760, 150, t, 1, 70, 7, eggs=7, grow=0.6 + 0.4 * E.ease_out_cubic(pr(u, 0.4, 1.4)))
    ia = ap(u, 0.8, 0.3)
    jfrog(d, 330, 1060, 0.3, t, ia, "proud", seed=0.2)
    jfrog(d, 750, 1060, 0.3, t, ia, "calm", seed=1.7, col=(RELG, RELG_D, mix(RELG, WHITE, 0.3)))
    vk = popk(t, t0 + 0.5, "bouncy")
    if vk > 0:
        d.circ(540, 760, 70 * min(1.1, vk), fill=A(GOLD, 1)); d.text(540, 760, "VS", int(56 * min(1.1, vk)), A(NAVYT, 1), k=1)

# ======== 10. card: 一句话学会 — foam nest ========
def s_card(t, d):
    t0 = T["card"]; u = t - t0
    grad(d, (92, 70, 60), (48, 36, 32))
    kk = popk(t, t0 + 0.05); sc = min(1.04, 0.85 + 0.15 * kk); al = ap(u, 0.05, 0.25)
    x0, y0, x1, y1 = 540 - 380 * sc, 380, 540 + 380 * sc, 380 + 880 * sc
    sbox(d, x0, y0, x1, y1, (252, 248, 236), al, 40)
    d.rect(x0, y0, x1, y0 + 110, fill=A((232, 120, 52), al), r=40); d.rect(x0, y0 + 60, x1, y0 + 110, fill=A((232, 120, 52), al))
    d.text(540, y0 + 56, "一句话学会", 52, A(WHITE, al), k=1)
    d.text(540, y0 + 210, "泡沫巢", 112, A((40, 70, 60), al), k=1)
    d.text(540, y0 + 330, "用一团泡泡裹住卵，", 48, A((80, 80, 80), al), k=1)
    d.text(540, y0 + 400, "让卵一直湿湿的", 48, A((80, 80, 80), al), k=1)
    fa = ap(u, 0.8, 0.3)
    foam(d, 540, y0 + 640, 140, t, fa, 60, 9, eggs=6, grow=0.5 + 0.5 * E.ease_out_cubic(pr(u, 0.8, 1.6)))
    for j in range(4):                                                         # moisture drops
        v = ((u - 1.6) * 0.8 + j / 4) % 1 if u > 1.6 else -1
        if v < 0: continue
        dx = 540 + (j - 1.5) * 90; dy = y0 + 470 + v * 60; dd = math.sin(math.pi * v) * fa
        d.circ(dx, dy, 12, fill=A((90, 170, 240), dd)); d.poly([(dx - 11, dy - 3), (dx + 11, dy - 3), (dx, dy - 26)], A((90, 170, 240), dd))

# ======== 11. first: among Sulawesi flying frogs, a gel nest was never recorded before ========
REL4 = [(RELG, RELG_D), ((110, 160, 120), (70, 110, 80)), ((140, 168, 96), (96, 120, 64)), ((100, 150, 110), (64, 104, 74))]
def sulawesi_icon(d, x, y, s, col, a):
    if a <= 0.01: return
    pts = [(x + (lon - 121.5) * 52 * s, y - (lat + 2.2) * 52 * s) for lon, lat in SULA]
    d.poly(pts, A(col, a))
def s_first(t, d):
    t0 = T["first"]; u = t - t0
    grad(d, (24, 34, 66), (12, 18, 38))
    sulawesi_icon(d, 540, 450, 0.75, (90, 140, 120), ap(u, 0.0, 0.4))
    for i, (c, cd) in enumerate(REL4):
        kk = popk(t, t0 + 0.2 + i * 0.25)
        if kk <= 0: continue
        al = ap(u, 0.2 + i * 0.25, 0.2) * (1 - 0.45 * ap(u, 2.6, 0.4)); x = 255 + i * 190; y = 720 + (1 - min(1, kk)) * 60
        card_box(d, x - 80, y - 110, x + 80, y + 120, al, (224, 230, 236), 22)
        jfrog(d, x, y - 10, 0.26, t, al, "calm", seed=i, col=(c, cd, mix(c, WHITE, 0.3)))
        dcirc(d, x, y + 78, 26, (130, 140, 150), al, 3, 18)                    # empty gel slot
        d.text(x, y + 78, "?", 30, A((130, 140, 150), al), k=1)
    nk = popk(t, t0 + 2.4, "bouncy")
    if nk > 0:
        al = ap(u, 2.4, 0.2); y = 1040 + (1 - min(1, nk)) * 120; sc = min(1.08, nk)
        glow_disc(d, 540, y, 260, GOLD, 0.35 * al)
        card_box(d, 540 - 230 * sc, y - 150 * sc, 540 + 230 * sc, y + 150 * sc, al, (252, 248, 236), 30)
        jfrog(d, 450, y + 20, 0.42 * sc, t, al, "proud", seed=0.4)
        jelly(d, 650, y + 10, 70 * sc, t, al, 8, 0.6, 5, 1.0, 0.6)
        sk = popk(t, t0 + 3.2, "bouncy")
        if sk > 0:
            for j in range(10):
                ang = j * 0.628 + u; rr_ = 70 + 24 * (j % 2)
                d.line([(800 + math.cos(ang) * 40, 900 + math.sin(ang) * 40), (800 + math.cos(ang) * rr_, 900 + math.sin(ang) * rr_)], A(GOLD, ap(u, 3.2, 0.2)), 6)
            d.circ(800, 900, 46 * min(1.1, sk), fill=A(GOLD, 1)); d.text(800, 900, "首次", int(30 * min(1.1, sk)), A(NAVYT, 1), k=1)

# ======== 12. three: look-alikes, so: 28 measurements + DNA + calls ========
def s_three(t, d):
    t0 = T["three"]; u = t - t0
    grad(d, (232, 240, 236), (196, 214, 210))
    grid(d, (170, 196, 192), 0.5, 60)
    ka = E.ease_out_cubic(pr(u, 0.0, 0.5))
    jfrog(d, lerp(-100, 350, ka), 520, 0.55, t, 1, "sus", look=0.8, seed=0.2)
    jfrog(d, lerp(1180, 730, ka), 520, 0.55, t, 1, "sus", look=-0.8, seed=1.2, col=(RELG, RELG_D, mix(RELG, WHITE, 0.3)))
    eq = ap(u, 0.6, 0.3) * (1 - 0.6 * ap(u, 2.2, 0.3))
    d.text(540, 520, "≈", 120, A((80, 90, 100), eq), k=1)
    PX = (290, 540, 790); py = 970
    for i, x in enumerate(PX):
        kk = popk(t, t0 + 1.4 + i * 0.9)
        if kk <= 0: continue
        al = ap(u, 1.4 + i * 0.9, 0.2); sc = min(1.06, kk)
        sbox(d, x - 115 * sc, py - 150 * sc, x + 115 * sc, py + 150 * sc, (252, 252, 248), al, 26)
        v = u - (1.4 + i * 0.9)
        if i == 0:                                                              # ruler + counter 0 -> 28
            d.rect(x - 90, py + 40, x + 90, py + 80, fill=A((250, 210, 70), al), r=6)
            for j in range(19): d.line([(x - 84 + j * 9.3, py + 40), (x - 84 + j * 9.3, py + (60 if j % 5 else 70))], A(NAVYT, al), 2)
            n = int(28 * E.ease_out_cubic(cl(v / 1.4)))
            d.text(x, py - 40, str(n), 110, A((40, 130, 70), al), k=1)
        elif i == 1:                                                            # DNA barcode
            rr = random.Random(4)
            for j in range(18):
                bw = rr.choice((4, 6, 10, 14)); xx = x - 92 + j * 10.5; bk = ap(v, j * 0.04, 0.2)
                d.rect(xx, py - 110, xx + bw * 0.7, py + 30, fill=A(NAVYT, al * bk))
            d.text(x, py + 90, "DNA", 44, A((40, 130, 70), al), k=0)
        else:                                                                   # call waveform
            pts = []
            for j in range(80):
                xx = x - 95 + j * 2.4; env = math.exp(-((j % 20) - 6) ** 2 / 18)
                pts.append((xx, py - 20 + math.sin(j * 1.7 + t * 18) * 70 * env * ap(v, j * 0.01, 0.2)))
            d.line(pts, A((40, 130, 70), al), 5)
            for j in range(3): d.arc(x + 70, py + 90, 16 + j * 14, 16 + j * 14, -50, 50, A(NAVYT, al * (0.5 + 0.5 * math.sin(t * 6 - j))), 4)
            d.ell(x + 40, py + 90, 16, 22, A(NAVYT, al))

# ======== 13. map: Sulawesi -> Mekongga Mountains -> high lake, 1800+ m ========
SULA = [(120.0, 0.8), (121.0, 1.2), (122.5, 1.0), (123.5, 0.9), (124.5, 1.3), (125.2, 1.6), (125.0, 1.0), (124.4, 0.5), (123.4, 0.4), (122.0, 0.5),
        (121.0, 0.4), (120.6, 0.0), (120.8, -0.6), (121.5, -0.9), (122.5, -0.8), (123.4, -0.9), (123.3, -1.3), (122.3, -1.5), (121.6, -1.9),
        (122.3, -2.8), (122.8, -3.6), (123.2, -4.4), (122.9, -4.8), (122.6, -5.6), (122.0, -5.2), (121.7, -4.6), (121.3, -4.1), (120.9, -3.5),
        (120.6, -3.0), (120.4, -3.6), (120.4, -5.5), (119.6, -5.6), (119.4, -5.0), (119.6, -4.0), (119.3, -3.4), (118.9, -3.0), (118.8, -2.6),
        (119.3, -1.8), (119.5, -0.8), (119.8, 0.0)]
BORNEO = [(108.8, 1.5), (109.6, 2.2), (111.0, 2.9), (113.0, 3.3), (114.8, 4.6), (116.0, 6.0), (117.2, 6.8), (118.6, 5.4), (117.8, 4.2),
          (117.9, 1.8), (119.0, 1.0), (117.8, 0.0), (117.5, -1.0), (116.4, -2.8), (116.0, -3.9), (114.5, -3.8), (113.0, -3.2), (111.0, -3.0), (110.2, -2.0), (109.0, -0.5)]
MEK = (121.25, -3.65)
def s_map(t, d):
    t0 = T["map"]; u = t - t0
    grad(d, (30, 90, 140), (16, 56, 96))
    zk = E.ease_in_out_sine(pr(u, 1.0, 2.6)); z = 1 + 3.2 * zk
    base = 52.0; c0 = (119.0, -1.5)
    cx = lerp(c0[0], MEK[0], zk); cy = lerp(c0[1], MEK[1], zk)
    M = lambda lon, lat: (540 + (lon - cx) * base * z, 760 - (lat - cy) * base * z)
    d.poly([M(*p) for p in BORNEO], A((150, 170, 120), 0.8))
    d.poly([M(*p) for p in SULA], A((120, 190, 120), 1))
    la = ap(u, 0.2, 0.3) * (1 - pr(u, 1.0, 1.3))
    if la > 0: px_, py_ = M(119.6, -1.0); d.text(px_, py_, "苏拉威西", 46, A((30, 70, 40), la), k=1)
    if u > 1.6:                                                                  # mountains on the SE arm
        ma = ap(u, 1.6, 0.4)
        for j, (lo, la_, h) in enumerate(((121.15, -3.55, 1.0), (121.35, -3.75, 0.8), (121.0, -3.85, 0.7))):
            px_, py_ = M(lo, la_); hh = 120 * h; d.poly([(px_ - hh * 0.8, py_ + hh * 0.3), (px_, py_ - hh * 0.7), (px_ + hh * 0.8, py_ + hh * 0.3)], A((96, 130, 90), ma))
            d.poly([(px_ - hh * 0.22, py_ - hh * 0.42), (px_, py_ - hh * 0.7), (px_ + hh * 0.22, py_ - hh * 0.42)], A((230, 240, 230), ma))
    ka = popk(t, t0 + 0.5)
    if ka > 0:
        px_, py_ = M(*MEK); al = ap(u, 0.5, 0.2)
        for j in range(3):
            ph = ((u * 0.8 + j / 3) % 1); d.circ(px_, py_, 20 + ph * 90, outline=A((255, 110, 90), al * (1 - ph)), w=5)
        d.circ(px_, py_, 18 * min(1.2, ka), fill=A((230, 60, 50), al)); d.circ(px_, py_, 7, fill=A(WHITE, al))
        ptag(d, t, t0 + 2.6, px_, py_ - 110, "梅孔加山", (250, 244, 226), 38)
    ga = ap(u, 2.4, 0.3)                                                          # altitude gauge
    if ga > 0:
        gx, gy0, gy1 = 820, 1150, 600
        sbox(d, gx - 120, gy1 - 110, gx + 60, gy0 + 40, (20, 36, 60), 0.85 * ga, 30)
        d.rect(gx - 18, gy1, gx + 18, gy0, fill=A((230, 236, 240), 0.9 * ga), r=18)
        h = 1800 * E.ease_out_cubic(pr(u, 2.5, 3.6)); yy = lerp(gy0, gy1, h / 2500)
        d.rect(gx - 18, yy, gx + 18, gy0, fill=A((100, 190, 140), ga), r=18)
        for m in (0, 1000, 2000):
            ym = lerp(gy0, gy1, m / 2500); d.line([(gx - 34, ym), (gx - 20, ym)], A(WHITE, ga), 3); d.text(gx - 44, ym, str(m), 22, A(WHITE, ga), anchor="rm", k=1)
        d.text(gx - 30, gy1 - 60, (f"{int(round(h, -1))} 米" if h < 1795 else "1800+ 米"), 36, A(GOLD, ga), k=1)

# ======== 14. years: 2009–2013 expeditions, calendar flips, paper lands this year ========
def s_years(t, d):
    t0 = T["years"]; u = t - t0
    grad(d, (250, 190, 120), (230, 120, 80))
    pts = [(-60, 1300), (200, 1100), (420, 960), (640, 900), (900, 760), (1140, 700), (1140, 1960), (-60, 1960)]
    d.poly(pts, A((150, 96, 70), 1)); d.poly([(x, y + 40) for x, y in pts], A((120, 76, 56), 1))
    wk = E.ease_in_out_sine(pr(u, 0.0, 2.6)); sx_ = lerp(220, 560, wk); sy_ = lerp(1100, 920, wk)
    scientist(d, sx_, sy_, 0.62, t, ap(u, 0.0, 0.3) * (1 - pr(u, 2.6, 2.9)), walk=1.0, beam=0.0, night=0.0)
    ta = ap(u, 0.4, 0.3) * (1 - pr(u, 2.6, 2.9))                                 # tent
    if ta > 0: d.poly([(640, 900), (740, 760), (840, 870)], A((60, 140, 200), ta)); d.poly([(720, 880), (740, 800), (760, 880)], A((30, 60, 90), ta))
    cx, cy = 540, 500                                                             # flip calendar
    if u < 2.6: yr = 2009 + min(4, int(cl(u / 2.3) * 5)); fl = (cl(u / 2.3) * 5) % 1
    else: yr = 2013 + int(13 * E.ease_in_out_sine(pr(u, 2.6, 3.4))); fl = 0
    sbox(d, cx - 170, cy - 150, cx + 170, cy + 150, (252, 248, 236), 1, 26)
    d.rect(cx - 170, cy - 150, cx + 170, cy - 70, fill=A((220, 70, 60), 1), r=26); d.rect(cx - 170, cy - 100, cx + 170, cy - 70, fill=A((220, 70, 60), 1))
    for sd in (-1, 1): d.rect(cx + sd * 90 - 10, cy - 176, cx + sd * 90 + 10, cy - 130, fill=A((90, 90, 100), 1), r=8)
    d.text(cx, cy + 40, str(yr), 110, A(NAVYT if yr < 2026 else (40, 130, 70), 1), k=1)
    if u < 2.4 and fl < 0.35:                                                    # page flipping up
        k = fl / 0.35; d.rect(cx - 170, cy - 70 - 220 * k, cx + 170, cy + 150 - 220 * k - 120 * k, fill=A((240, 236, 222), 1 - k), r=20)
    pk = popk(t, t0 + 3.5)
    if pk > 0:                                                                   # the paper lands
        al = ap(u, 3.5, 0.2); y = 960 + (1 - min(1, pk)) * -200
        sbox(d, 380, y - 170, 700, y + 170, (252, 252, 250), al, 14)
        d.rect(400, y - 150, 680, y - 110, fill=A((40, 90, 140), al), r=6); d.text(540, y - 130, "ZOOTAXA", 28, A(WHITE, al), k=0)
        for j in range(6): d.rect(410, y - 80 + j * 30, 670 - (j % 3) * 40, y - 66 + j * 30, fill=A((200, 200, 200), al), r=4)
        jfrog(d, 600, y + 120, 0.18, t, al, "happy", seed=0.3)
        check_mark(d, 700, y - 170, 44, (40, 160, 90), al, pr(u, 3.9, 4.2))

# ======== 15. name: honouring the late herpetologist Hellen Kurniati ========
def s_name(t, d):
    t0 = T["name"]; u = t - t0
    grad(d, (196, 186, 230), (130, 120, 180))
    for i in range(8): d.circ(160 + i * 110, 300 + (i % 2) * 980, 40, fill=A(WHITE, 0.1))
    na = ap(u, 0.0, 0.4); ny = 980
    sbox(d, 230, ny - 120, 850, ny + 120, (250, 246, 232), na, 22)
    for j in range(6): d.line([(260, ny - 80 + j * 34), (820, ny - 80 + j * 34)], A((200, 210, 230), na), 2)
    d.text(540, ny - 10, "Hellen Kurniati", 60, A((60, 50, 90), na), k=0)
    for j in range(5):                                                           # white memorial flower
        ang = j * 1.2566 + 0.3; d.ell(790 + math.cos(ang) * 26, ny - 100 + math.sin(ang) * 26, 22, 22, A(WHITE, na))
    d.circ(790, ny - 100, 14, fill=A((250, 210, 80), na))
    k = E.ease_in_out_sine(pr(u, 1.3, 2.4)); FS = 80
    kx = 540 - d.tlen("ae", FS) / 2
    tx = lerp(540 + 90, kx, k); ty = lerp(ny - 10, 580, k); ta = ap(u, 1.3, 0.2)
    if ta > 0: d.text(tx, ty, "Kurniati" if k < 0.6 else "kurniati", int(lerp(60, FS, k)), A((40, 40, 70), ta), k=0)
    aa = popk(t, t0 + 2.4, "bouncy")
    if aa > 0:
        d.text(kx + d.tlen("kurniati", FS) / 2 + d.tlen("ae", FS) / 2 + 2, 580 - (1 - min(1, aa)) * 40, "ae", FS, A(GOLD, ap(u, 2.4, 0.2)), k=0)
    ra = ap(u, 2.9, 0.3)
    if ra > 0: d.text(540, 470 + (1 - ra) * 20, "Rhacophorus", 56, A((60, 50, 90), ra), k=0)
    jfrog(d, 540, 800 + hop(u, 3.3, 30, 0.3), 0.32, t, ap(u, 0.6, 0.3), "happy", seed=0.8, lift=6 * math.sin(u * 2))

# ======== 16. end: back to the jelly on the branch — jelly or bubbles? ========
def s_end(t, d):
    t0 = T["end"]; u = t - t0
    hook_set(d, t, jelly_r=170, jx=540, jy=720, jig=0.15 * math.exp(-u * 2))
    jfrog(d, 800, 360, 0.45, t, 1, "happy", look=-0.7, seed=0.2)
    for i, (x, kind) in enumerate(((330, "gel"), (750, "foam"))):
        kk = popk(t, t0 + 0.5 + i * 0.3)
        if kk <= 0: continue
        al = ap(u, 0.5 + i * 0.3, 0.2) * (1 - pr(u, 3.9, 4.3)); sc = min(1.05, kk) * (1 + 0.04 * math.sin(t * 4 + i * 3))
        bubble(d, x, 975, 260 * sc, 170 * sc, al, (252, 250, 240), (0, 1))
        if kind == "gel": jelly(d, x - 50, 975, 50 * sc, t, al, 6, 0.9, 2, 1.0)
        else: foam(d, x - 50, 975, 50 * sc, t, al, 24, 3, eggs=2)
        d.text(x + 55, 975, "果冻" if kind == "gel" else "泡泡", 44, A(NAVYT, al), k=1)
    ra = ap(u, 1.0, 0.4)
    d.text(540, 1180, "Trilaksono et al. 2026 · Zootaxa 5900(4):349–370", 24, A((230, 230, 220), 0.8 * ra), k=0)
    fo = pr(t, DUR - 0.6, DUR)
    if fo > 0: d.rect(-40, -40, 1120, 1960, fill=A((0, 0, 0), fo))
