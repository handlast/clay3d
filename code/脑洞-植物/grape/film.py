import math, random, sys, subprocess
from PIL import Image, ImageDraw
from base import *
from cues import *

GRAPE = (120, 46, 150); GRAPE_D = (70, 22, 96); GRAPE_L = (190, 120, 220)
FLESH = (196, 226, 150); PLASMA = (220, 120, 255); PLASMA_C = (255, 235, 255); HOT = (255, 170, 60)
BEADC = (110, 210, 240); EGGC = (236, 222, 196); WARN = (255, 70, 60); NA = (255, 210, 60); KC = (200, 120, 255)
rnd = random.Random(11)

def glow(d, x, y, r, col, a, n=7):
    if a <= 0.01: return
    for i in range(n):
        k = 1 - i / n
        d.circ(x, y, r * (0.25 + 0.75 * k), fill=A(col, a * 0.16 * (1.2 - k * 0.6)))

def mouth(d, x, y, r, kind, a, col=INK):
    if kind == "smile": d.arc(x, y - r * 0.25, r * 0.45, r * 0.35, 20, 160, A(col, a), r * 0.09)
    elif kind == "o": d.ell(x, y, r * 0.12, r * 0.15, A(col, a))
    elif kind == "scream":
        d.ell(x, y + r * 0.05, r * 0.3, r * 0.38, A(col, a)); d.ell(x, y + r * 0.22, r * 0.17, r * 0.12, A(TONGUE, a))
    elif kind == "grin":
        d.d.chord((P(x - r * .42), P(y - r * .3), P(x + r * .42), P(y + r * .35)), 0, 180, fill=A(col, a))
    elif kind == "flat": d.line([(x - r * .25, y), (x + r * .25, y)], A(col, a), r * 0.08)
    elif kind == "wobble":
        d.line([(x - r * .3 + i * r * .1, y + (r * .06 if i % 2 else -r * .06)) for i in range(7)], A(col, a), r * 0.07)

def face(d, x, y, r, kind, a, look=0.0):
    er = r * 0.17; ey = y - r * 0.12
    for s_ in (-1, 1):
        ex = x + s_ * r * 0.36
        if kind == "dizzy":
            d.line([(ex - er, ey - er), (ex + er, ey + er)], A(INK, a), er * 0.45); d.line([(ex - er, ey + er), (ex + er, ey - er)], A(INK, a), er * 0.45)
        elif kind in ("proud", "happy"):
            d.arc(ex, ey + er * 0.5, er, er, 200, 340, A(INK, a), er * 0.45)
        elif kind == "chill":
            d.circ(ex + look * er * 0.4, ey, er * 0.5, fill=A(INK, a))
        else:
            big = 1.35 if kind in ("scared", "scream") else 1.0
            d.circ(ex, ey, er * big, fill=A(WHITE, a)); d.circ(ex + look * er * 0.5, ey + er * 0.1, er * (0.38 if kind == "scream" else 0.5), fill=A(INK, a))
            if kind == "sad": d.line([(ex - er, ey - er * 1.3 + s_ * er * .4), (ex + er, ey - er * 1.3 - s_ * er * .4)], A(INK, a), er * .3)
    m = {"chill": "smile", "scared": "o", "scream": "scream", "dizzy": "wobble", "proud": "grin", "happy": "grin", "sad": "flat", "sus": "flat"}[kind]
    mouth(d, x, y + r * 0.38, r, m, a)
    if kind == "sus":
        for s_ in (-1, 1): d.line([(x + s_ * r * .2, ey - er * 1.5), (x + s_ * r * .55, ey - er * 1.1 - s_ * er * .4)], A(INK, a), er * .35)
    if kind in ("scared", "scream"): d.ell(x + r * 0.75, y - r * 0.5, r * 0.08, r * 0.13, A(CYAN, a))

def grape(d, x, y, r, kind="chill", a=1.0, sq=0.0, look=0.0, col=GRAPE):
    rx, ry = r * (1 + sq), r * (1 - sq)
    d.ell(x, y + r * 0.92, r * 0.8, r * 0.14, A((0, 0, 0), 0.25 * a))
    d.ell(x, y, rx, ry, A(mix(col, (0, 0, 0), 0.35), a)); d.ell(x - r * 0.04, y - r * 0.04, rx * 0.95, ry * 0.95, A(col, a))
    d.ell(x - r * 0.38, y - r * 0.42, r * 0.22, r * 0.14, A(WHITE, 0.45 * a)); d.circ(x - r * 0.15, y - r * 0.6, r * 0.05, fill=A(WHITE, .6 * a))
    d.line([(x, y - ry), (x + r * 0.1, y - ry - r * 0.25)], A((90, 120, 50), a), r * 0.08)
    face(d, x, y, r, kind, a, look)

def bead(d, x, y, r, kind="chill", a=1.0, sq=0.0):
    d.ell(x, y, r * (1 + sq), r * (1 - sq), A(BEADC, 0.55 * a)); d.ell(x, y, r * 0.85 * (1 + sq), r * 0.85 * (1 - sq), A((170, 240, 255), 0.35 * a))
    d.ell(x - r * .38, y - r * .42, r * .25, r * .15, A(WHITE, .7 * a))
    face(d, x, y, r, kind, a)

def egg(d, x, y, r, kind, a=1.0, fill=1.0):
    d.ell(x, y, r * 0.82, r, A(EGGC, a))
    if fill > 0: d.ell(x, y + r * 0.1, r * 0.7, r * 0.82 * fill, A(BEADC, 0.35 * a))
    for i in range(14):
        sx, sy = x + math.cos(i * 2.3) * r * 0.6 * ((i * 37) % 10) / 10, y + math.sin(i * 1.7) * r * 0.75 * ((i * 53) % 10) / 10
        d.circ(sx, sy, r * 0.06, fill=A((120, 90, 60), 0.7 * a))
    face(d, x, y + r * 0.1, r * 0.8, kind, a)

def plasma(d, x, y, t, s, a=1.0, seed=0):
    if a <= 0.01: return
    fl = 0.85 + 0.15 * math.sin(t * 47 + seed) + 0.1 * math.sin(t * 83)
    glow(d, x, y, s * 2.4 * fl, PLASMA, a, 9)
    glow(d, x, y, s * 1.2 * fl, (255, 160, 255), a, 6)
    r2 = random.Random(int(t * 30) + seed)
    for i in range(9):
        ang = r2.uniform(0, 2 * math.pi); L = s * r2.uniform(0.8, 2.0)
        pts = [(x, y)]
        for k in range(1, 6):
            pts.append((x + math.cos(ang) * L * k / 5 + r2.uniform(-1, 1) * s * 0.18, y + math.sin(ang) * L * k / 5 + r2.uniform(-1, 1) * s * 0.18))
        d.line(pts, A((255, 210, 255), a * 0.9), max(3, s * 0.05))
    d.circ(x, y, s * 0.45 * fl, fill=A(PLASMA_C, a))

def sparks(d, x, y, t, t0, n=40, spd=900, col=(255, 200, 255), a=1.0, seed=1, life=1.1):
    u = t - t0
    if u < 0 or u > life: return
    r2 = random.Random(seed)
    for i in range(n):
        ang = r2.uniform(0, 2 * math.pi); v = r2.uniform(0.3, 1) * spd
        px = x + math.cos(ang) * v * u; py = y + math.sin(ang) * v * u + 700 * u * u
        k = 1 - u / life
        d.line([(px, py), (px - math.cos(ang) * 30 * k, py - math.sin(ang) * 30 * k)], A(col, a * k), 6 * k + 1)

def embers(d, t, col, a=1.0, n=26):
    for i in range(n):
        u = (t * 0.25 + i / n) % 1
        x = (i * 173) % 1080 + 30 * math.sin(t + i); y = 1900 - u * 2000
        d.circ(x, y, 4 + i % 4, fill=A(col, a * math.sin(u * math.pi) * 0.7))

def oven(d, t, lit=1.0, hum=0.0):
    grad(d, mix((40, 34, 22), (90, 72, 30), lit), mix((14, 12, 8), (40, 30, 14), lit))
    d.poly([(0, 0), (180, 260), (180, 1500), (0, 1920)], A((0, 0, 0), 0.25)); d.poly([(1080, 0), (900, 260), (900, 1500), (1080, 1920)], A((0, 0, 0), 0.25))
    d.rect(180, 260, 900, 1500, fill=A(mix((70, 60, 34), (150, 120, 60), lit), 1))
    d.line([(0, 0), (180, 260)], A((0, 0, 0), .4), 4); d.line([(1080, 0), (900, 260)], A((0, 0, 0), .4), 4)
    d.line([(180, 1500), (0, 1920)], A((0, 0, 0), .4), 4); d.line([(900, 1500), (1080, 1920)], A((0, 0, 0), .4), 4)
    glow(d, 540, 200, 380, (255, 230, 150), 0.5 * lit)
    d.ell(540, 1330, 470, 120, A((200, 220, 230), 0.25)); d.ell(540, 1320, 450, 108, A((230, 240, 245), 0.18))
    for i in range(8):
        ang = t * 0.8 + i * math.pi / 4
        d.circ(540 + math.cos(ang) * 400, 1320 + math.sin(ang) * 95, 6, fill=A(WHITE, 0.25))
    for yy in range(0, 1920, 40):  # door mesh at edges
        for xx in (20, 60, 1020, 1060): d.circ(xx, yy + 20, 7, fill=A((0, 0, 0), 0.35))
    if hum > 0:
        for i in range(6):
            yy = 400 + i * 180 + 30 * math.sin(t * 6 + i)
            d.line([(x, yy + 22 * math.sin(x / 40 + t * 12)) for x in range(180, 901, 20)], A((255, 240, 160), 0.15 * hum), 4)

def warn_badge(d, t):
    d.rect(770, 80, 1030, 128, fill=A(WARN, 0.95), r=24); d.text(900, 104, "危险 勿模仿", 26, A(WHITE, 1), k=1)

def shake(t, amt, f=70): return amt * math.sin(t * f), amt * 0.6 * math.cos(t * f * 1.3)
def bignum(d, t, n, hit, y=330, col=YEL, a=1.0, size=230):
    k = back(pr(t, hit, hit + 0.2))
    if k > 0: d.text(540, y, str(n), int(size * (0.6 + 0.4 * k)), A(col, a), k=1)
def stamp(d, t, t0, s, x, y, size, col, a=1.0, rot=0):
    k = back(pr(t, t0, t0 + 0.18))
    if k <= 0: return
    sz = int(size * (2.2 - 1.2 * k))
    d.text(x, y, s, sz, A(col, a * min(1, k * 1.5)), k=1)
def flash(d, t, hits, col=WHITE, amt=0.5):
    p = pulse(t, hits, 12)
    if p > 0.02: d.rect(0, 0, OW, OH, fill=A(col, amt * p))

def grad(d, top, bot, y0=0, y1=OH, n=48):
    for i in range(n):
        ya = lerp(y0, y1, i / n); yb = lerp(y0, y1, (i + 1) / n) + 1
        d.rect(-50, ya, OW + 50, yb, fill=A(mix(top, bot, i / (n - 1)), 1))
def rays(d, t, c1, c2, n=18, cx=540, cy=900):
    grad(d, c2, mix(c2, (0, 0, 0), 0.4)); rot = t * 0.6
    for i in range(n):
        a0 = rot + i * 2 * math.pi / n; a1 = a0 + math.pi / n
        d.poly([(cx, cy), (cx + math.cos(a0) * 2000, cy + math.sin(a0) * 2000), (cx + math.cos(a1) * 2000, cy + math.sin(a1) * 2000)], A(c1, 1))
def vignette(d, k):
    for i in range(10):
        m = 40 * i; d.rect(-m, -m, OW + m, OH + m, outline=A((0, 0, 0), 0.12 * k), w=120)

# ================= scenes =================
def w_hook(t, d):
    boom = pulse(t, [HOOK_BOOM], 2.2) if t >= HOOK_BOOM else 0
    oven(d, t, 1 - 0.6 * boom, 1.0)
    pre = pulse(t, HOOK_ZAP, 9)
    sq = 0.08 * math.sin(t * 40) * (1 if t < HOOK_BOOM else 0.3)
    k = "scared" if t < HOOK_ZAP[0] else "scream" if t < 1.6 else "dizzy"
    grape(d, 430, 1150, 120, k, 1, sq, look=0.5); grape(d, 650, 1150, 120, k, 1, -sq, look=-0.5)
    if t < HOOK_BOOM:
        for h in HOOK_ZAP:
            if h <= t: plasma(d, 540, 1150, t, 40 * pre + 10, 0.6 + 0.4 * pre, 3)
    else:
        u = t - HOOK_BOOM; rise = 260 * ease(u / 1.8)
        plasma(d, 540, 1120 - rise, t, 150 + 60 * boom, 1, 1)
        sparks(d, 540, 1120, t, HOOK_BOOM, 70, 1400, (255, 210, 255), 1, 5, 1.3)
        sparks(d, 540, 1120, t, HOOK_BOOM + 0.5, 40, 900, HOT, 1, 6, 1.0)
        rings(d, 540, 1120, t, [HOOK_BOOM], PLASMA, 1, 900)
def u_hook(t, d):
    a = 1 - pr(t, 2.45, 2.6)
    k = back(pr(t, HOOK_BOOM, HOOK_BOOM + 0.2)) * (1 + 0.12 * pulse(t, [HOOK_BOOM + i * BEAT for i in range(5)], 8))
    if t < HOOK_BOOM: d.text(540, 380, "微波几秒……", 110, A(WHITE, ease(pr(t, 0, 0.1))), k=1)
    else:
        d.text(546, 386, "葡萄喷火了", int(150 * (0.6 + 0.4 * k)), A(PLASMA, a), k=1)
        d.text(540, 380, "葡萄喷火了", int(150 * (0.6 + 0.4 * k)), A(YEL, a), k=1)
    flash(d, t, [HOOK_BOOM], WHITE, 0.95); flash(d, t, HOOK_ZAP, PLASMA, 0.25)

def w_myth(t, d):
    grad(d, (26, 20, 44), (8, 6, 16))
    for i in range(30):  # scrolling "internet" tiles
        x = (i % 5) * 230 + 40; y = ((i // 5) * 330 + t * 80) % 2100 - 200
        d.rect(x, y, x + 200, y + 280, fill=A((50, 44, 80), 0.6), r=18); d.circ(x + 100, y + 120, 50, fill=A(GRAPE, 0.5))
    cx, cy = 540, 1050
    sep = 70 + 20 * math.sin(t * 3)
    for s_ in (-1, 1):  # two halves, flesh facing out
        x = cx + s_ * sep
        d.d.pieslice((P(x - 150), P(cy - 150), P(x + 150), P(cy + 150)), 90 if s_ < 0 else -90, 270 if s_ < 0 else 90, fill=A(GRAPE, 1))
        d.d.pieslice((P(x - 132), P(cy - 132), P(x + 132), P(cy + 132)), 90 if s_ < 0 else -90, 270 if s_ < 0 else 90, fill=A(FLESH, 1))
    face(d, cx - sep - 60, cy, 90, "sus", 1); face(d, cx + sep + 60, cy, 90, "sus", 1)
    d.line([(cx - sep, cy + 130), (cx, cy + 165), (cx + sep, cy + 130)], A(GRAPE_D, 1), 18)
    if t > MYTH_HITS[1]:  # zap travels along skin
        u = ((t - MYTH_HITS[1]) * 1.5) % 1
        glow(d, lerp(cx - sep, cx + sep, u), cy + 150, 60, YEL, 1)
    if t > MYTH_HITS[2]:
        X = back(pr(t, MYTH_HITS[2], MYTH_HITS[2] + 0.2))
        d.line([(cx - 330 * X, cy - 330 * X), (cx + 330 * X, cy + 330 * X)], A(WARN, 0.9), 40); d.line([(cx - 330 * X, cy + 330 * X), (cx + 330 * X, cy - 330 * X)], A(WARN, 0.9), 40)
def u_myth(t, d):
    a = win(t, MYTH[0], MYTH[1], 0.15, 0.15)
    stamp(d, t, MYTH_HITS[0], "网上流传 20 多年", 540, 330, 76, WHITE, a)
    stamp(d, t, MYTH_HITS[1], "“葡萄皮 = 天线”", 540, 470, 90, YEL, a)
    stamp(d, t, MYTH_HITS[2], "错！", 540, 1500 - 220, 150, WARN, a)

def w_whole(t, d):
    oven(d, t, 1, 0.6)
    roll = ease(pr(t, 6.1, WHOLE_TOUCH))
    xl, xr = lerp(-150, 430, roll), lerp(1230, 650, roll)
    bounce = abs(math.sin(t * 10)) * 40 * (1 - roll)
    k = "chill" if t < WHOLE_TOUCH else "scared" if t < WHOLE_ZAP else "scream"
    sq = 0.12 * pulse(t, [WHOLE_TOUCH], 8)
    grape(d, xl, 1150 - bounce, 120, k, 1, sq, 0.6); grape(d, xr, 1150 - bounce, 120, k, 1, sq, -0.6)
    if t >= WHOLE_ZAP:
        plasma(d, 540, 1150 - 120 * ease(pr(t, WHOLE_ZAP, 9)), t, 110, 1, 2)
        sparks(d, 540, 1150, t, WHOLE_ZAP, 50, 1100, (255, 210, 255), 1, 8)
        rings(d, 540, 1150, t, [WHOLE_ZAP], PLASMA, 1, 600)
def u_whole(t, d):
    a = win(t, WHOLE[0], WHOLE[1], 0.15, 0.15)
    d.text(540, 330, "不切开，两颗贴着", 70, A(WHITE, a * ease(pr(t, 6.1, 6.4))), k=1)
    stamp(d, t, WHOLE_ZAP, "照样冒火", 540, 480, 120, PLASMA, a)
    flash(d, t, [WHOLE_ZAP], WHITE, 0.6)

def w_bead(t, d):
    grad(d, (10, 40, 60), (4, 14, 26))
    for i in range(40):  # bubbles
        u = (t * 0.3 + i / 40) % 1; d.circ((i * 211) % 1080, 1950 - u * 2100, 6 + i % 9, outline=A(BEADC, 0.4), w=3)
    drop = back(pr(t, 9.05, 9.4))
    k = "chill" if t < BEAD_SALT else "scared" if t < BEAD_ZAP else "scream"
    sq = 0.15 * pulse(t, [9.4, BEAD_SALT], 7)
    bead(d, 430, lerp(-200, 1100, drop), 120, k, 1, sq); bead(d, 650, lerp(-300, 1100, drop), 120, k, 1, sq)
    if BEAD_SALT - 0.3 < t < BEAD_ZAP:
        for i in range(30):
            u = (t - BEAD_SALT + 0.3 + i * 0.03) * 2.2
            d.rect(380 + (i * 47) % 330, lerp(500, 1000, u % 1), 392 + (i * 47) % 330, lerp(512, 1012, u % 1), fill=A(WHITE, 0.9))
    if t >= BEAD_ZAP:
        plasma(d, 540, 1100, t, 100, 1, 4); sparks(d, 540, 1100, t, BEAD_ZAP, 45, 1000, (200, 240, 255), 1, 9)
        rings(d, 540, 1100, t, [BEAD_ZAP], BEADC, 1, 500)
def u_bead(t, d):
    a = win(t, BEAD[0], BEAD[1], 0.1, 0.1)
    d.text(540, 330, "换成水珠（99% 是水）", 64, A(WHITE, a * ease(pr(t, 9.1, 9.4))), k=1)
    if BEAD_SALT <= t < BEAD_ZAP: d.text(760, 640, "撒点盐", 54, A(WHITE, a), k=1)
    if t >= ANSWER:
        k = back(pr(t, ANSWER, ANSWER + 0.2))
        d.rect(140, 410, 940, 560, fill=A(WARN, a * min(1, k)), r=30)
        d.text(540, 485, "真凶是：水", int(96 * (0.6 + 0.4 * k)), A(WHITE, a), k=1)
    flash(d, t, [BEAD_ZAP], WHITE, 0.6); flash(d, t, [ANSWER], YEL, 0.4)

def w_res(t, d):
    grad(d, (12, 10, 30), (2, 2, 8))
    rr = pr(t, RISER[0], RISER[1]); p = pulse(t, BOUNCE, 6)
    sx, sy = shake(t, 4 + 14 * rr + 8 * p, 55)
    cx, cy, R = 540 + sx, 980 + sy, 330
    for i in range(7):  # incoming microwaves
        yy = 520 + i * 75
        d.line([(x, yy + 25 * math.sin(x / 55 - t * 9)) for x in range(-20, int(cx - R) + 40, 14)], A((255, 230, 120), 0.5), 6)
    d.circ(cx, cy, R + 14, fill=A(GRAPE_D, 1)); d.circ(cx, cy, R, fill=A((60, 20, 90), 1))
    n = sum(1 for h in BOUNCE if h <= t)
    energy = min(1, n / 4 + rr * 0.3)
    glow(d, cx, cy, R * 0.9, HOT, 0.4 + 0.6 * energy)
    for j in range(n + 1):  # bouncing ray inside sphere
        ang = t * 3 + j * 2.4
        pts = [(cx + math.cos(ang + k * 2.2) * R * 0.95, cy + math.sin(ang + k * 2.2) * R * 0.95) for k in range(6)]
        d.line(pts, A((255, 240, 160), 0.5 + 0.1 * j), 5)
    for h in BOUNCE:
        u = (t - h) / 0.5
        if 0 <= u < 1: d.circ(cx, cy, R * u, outline=A(YEL, 1 - u), w=10)
    face(d, cx, cy + 40, 200, "scared" if n < 3 else "scream", 1, look=math.sin(t * 5) * 0.6)
    embers(d, t, HOT, energy)
    if rr > 0: vignette(d, rr * 1.5)
def u_res(t, d):
    a = win(t, RES[0], RES[1], 0.1, 0.05); rr = pr(t, RISER[0], RISER[1])
    d.text(540, 330, "葡萄 ≈ 一颗小水球", 76, A(WHITE, a * ease(pr(t, 12.1, 12.4))), k=1)
    n = sum(1 for h in BOUNCE if h <= t)
    if n: d.text(540, 470, f"微波在里面反弹 ×{n}", int(64 * (1 + 0.15 * pulse(t, BOUNCE, 10))), A(YEL, a), k=1)
    if t > 16.0: d.text(540, 1380, "大小刚好：共振，能量越攒越多", 48, A(HOT, a * ease(pr(t, 16.0, 16.3))), k=1)
    if rr > 0: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.5 * rr))

BURST_HITS = [BURST + i * BEAT for i in range(8)]
def w_burst(t, d):
    p = pulse(t, BURST_HITS, 8); beat = int((t - BURST) / BEAT)
    rays(d, t, (110, 40, 150) if beat % 2 else (60, 20, 90), (20, 6, 30))
    sq = 0.1 * p
    grape(d, 400, 1150, 140, "scream" if t < 21.5 else "dizzy", 1, sq, 0.6); grape(d, 680, 1150, 140, "scream" if t < 21.5 else "dizzy", 1, sq, -0.6)
    plasma(d, 540, 1150 - 150 * ease(pr(t, BURST, 23)), t, 170 * (1 + 0.15 * p), 1, 7)
    sparks(d, 540, 1150, t, BURST, 90, 1600, (255, 220, 255), 1, 12, 1.4)
    for h in BURST_HITS[1:]: sparks(d, 540, 1150 - 150 * ease(pr(h, BURST, 23)), t, h, 18, 800, HOT, 0.9, int(h * 10), 0.6)
    embers(d, t, PLASMA, 1)
def u_burst(t, d):
    a = win(t, BURST, 24.0, 0.01, 0.2)
    k = back(pr(t, BURST, BURST + 0.25)); p = pulse(t, BURST_HITS, 8)
    d.text(540, 360, "嘭！", int(260 * (0.5 + 0.5 * k) * (1 + 0.06 * p)), A(YEL, a), k=1)
    if t > 21.2:
        al = a * ease(pr(t, 21.2, 21.5)); d.rect(150, 510, 930, 700, fill=A((20, 6, 30), 0.75 * al), r=30)
        d.text(540, 560, "两颗水球的能量", 64, A(WHITE, a * ease(pr(t, 21.2, 21.5))), k=1)
        d.text(540, 650, "挤进接触点那一小点", 64, A(PLASMA_C, a * ease(pr(t, 21.6, 21.9))), k=1)
    if t < BURST + 0.15: d.rect(0, 0, OW, OH, fill=A(WHITE, 1 - pr(t, BURST, BURST + 0.15)))

def w_egg(t, d):
    grad(d, (240, 226, 200), (200, 180, 150))
    for i in range(12): d.line([(0, 200 + i * 160), (1080, 200 + i * 160)], A((180, 160, 130), 0.4), 3)
    idx = sum(1 for h in EGG_HITS if h <= t) - 1
    full = 1.0 if idx != 1 else 0.0
    if idx == 1: full = 1 - ease(pr(t, EGG_HITS[1] - 0.4, EGG_HITS[1]))
    if idx == 2: full = ease(pr(t, EGG_HITS[2] - 0.5, EGG_HITS[2]))
    if idx < 0: full = 1
    hot = pulse(t, [EGG_HITS[0], EGG_HITS[2]], 1.5) if idx in (0, 2) else 0
    k = "chill" if idx < 0 else ("scream" if idx in (0, 2) else "sad")
    sx, sy = shake(t, 10 * hot, 60)
    egg(d, 420 + sx, 1050 + sy, 170, k, 1, full); egg(d, 660 - sx, 1050 + sy, 170, k, 1, full)
    if idx in (0, 2):
        glow(d, 540, 1050, 160, HOT, hot); d.circ(540, 1050, 24, fill=A((60, 30, 10), min(1, (t - EGG_HITS[idx]) * 3)))
        sparks(d, 540, 1050, t, EGG_HITS[idx], 30, 800, HOT, 1, idx + 20, 0.8)
    if idx == 1:
        for i in range(8):
            u = ((t - EGG_HITS[1]) * 1.2 + i / 8) % 1
            d.circ(540 + 40 * math.sin(i), 1050 - u * 400, 10, fill=A((150, 150, 150), 0.5 * (1 - u)))
def u_egg(t, d):
    a = win(t, EGG[0], EGG[1], 0.15, 0.15)
    d.text(540, 300, "鹌鹑蛋验证", 80, A(INK, a * ease(pr(t, 24.1, 24.4))), k=1)
    labels = [("装满水：接触点烫出黑点", WARN), ("掏空：毫无反应", (90, 90, 90)), ("再灌水：又来了！", WARN)]
    idx = sum(1 for h in EGG_HITS if h <= t) - 1
    if idx >= 0:
        s, c = labels[idx]; k = back(pr(t, EGG_HITS[idx], EGG_HITS[idx] + 0.2))
        d.text(540, 470, s, int(66 * (0.6 + 0.4 * k)), A(c, a), k=1)
    for i in range(min(idx + 1, 3)):
        d.circ(390 + i * 150, 620, 40, fill=A(WARN if i != 1 else (120, 120, 120), a)); d.text(390 + i * 150, 620, "有" if i != 1 else "无", 40, A(WHITE, a), k=1)

def w_spec(t, d):
    grad(d, (8, 8, 14), (2, 2, 4))
    for x in range(80, 1001, 60): d.line([(x, 700), (x, 1250)], A((60, 60, 90), 0.4), 2)
    # rainbow axis
    for i in range(46):
        c = mix(mix((120, 60, 255), (60, 220, 120), cl(i / 23)), (255, 60, 40), cl((i - 23) / 23))
        d.rect(80 + i * 20, 1260, 100 + i * 20, 1300, fill=A(c, 1))
    n = sum(1 for h in SPEC_HITS if h <= t)
    na = (n >= 1) * ease(pr(t, SPEC_HITS[0], SPEC_HITS[0] + 0.3)); kk = (n >= 2) * ease(pr(t, SPEC_HITS[1], SPEC_HITS[1] + 0.3))
    pts = []
    for x in range(80, 1001, 6):
        v = 0.04 * math.sin(x * 0.3 + t * 20) + na * math.exp(-((x - 640) / 14) ** 2) * (1 + 0.1 * math.sin(t * 30)) + kk * 0.9 * math.exp(-((x - 900) / 14) ** 2)
        pts.append((x, 1240 - v * 480))
    d.line(pts, A(WHITE, 1), 6)
    if na: glow(d, 640, 780, 90, NA, na); d.text(640, 690, "钠 Na", 52, A(NA, na), k=1)
    if kk: glow(d, 900, 800, 90, KC, kk); d.text(900, 710, "钾 K", 52, A(KC, kk), k=1)
    plasma(d, 200, 480, t, 70, 1, 9)
    if n >= 3:
        u = ease(pr(t, SPEC_HITS[2], SPEC_HITS[2] + 0.4)); grape(d, lerp(1200, 820, u), 470, 110, "proud", 1)
def u_spec(t, d):
    a = win(t, SPEC[0], SPEC[1], 0.15, 0.15)
    d.text(540, 300, "拆开火光的颜色", 80, A(WHITE, a * ease(pr(t, 30.1, 30.4))), k=1)
    if t > SPEC_HITS[2]: d.text(540, 1370, "钾和钠：葡萄皮里本来就有", 54, A(YEL, a * ease(pr(t, SPEC_HITS[2], SPEC_HITS[2] + .3))), k=1)
    if t > SPEC_HITS[3]: d.text(540, 1450, "强电场把它们电离，点燃空气", 46, A(PLASMA, a * ease(pr(t, SPEC_HITS[3], SPEC_HITS[3] + .3))), k=1)

def w_nano(t, d):
    grad(d, (6, 20, 40), (2, 6, 14))
    z = ease(pr(t, 35.3, 37.5)); r = lerp(150, 26, z)
    grape(d, 540 - r * 1.05, 1000, r, "proud", 1 - z * 0.7); grape(d, 540 + r * 1.05, 1000, r, "proud", 1 - z * 0.7)
    if z > 0.3:
        for j in range(5):
            for i in range(7):
                x, y = 180 + i * 120, 620 + j * 170
                if abs(x - 540) < 120 and abs(y - 1000) < 120: continue
                d.circ(x - 22, y, 20, fill=A((230, 190, 80), (z - .3) * 1.4)); d.circ(x + 22, y, 20, fill=A((230, 190, 80), (z - .3) * 1.4))
                glow(d, x, y, 30, CYAN, (z - .3) * (0.6 + 0.4 * math.sin(t * 8 + i + j)))
    glow(d, 540, 1000, 120 * (1 - z) + 30, PLASMA, 1)
def u_nano(t, d):
    a = win(t, NANO[0], NANO[1], 0.15, 0.15)
    d.text(540, 330, "科学家的结论", 70, A(WHITE, a * ease(pr(t, 35.1, 35.4))), k=1)
    d.text(540, 460, "葡萄 = 放大版的纳米“热点”", 64, A(CYAN, a * ease(pr(t, 36.0, 36.3))), k=1)
    d.text(540, 1380, "能用来研究光怎么被压进极小的空间", 46, A(WHITE, a * ease(pr(t, 37.2, 37.5))), k=1)

def w_end(t, d):
    oven(d, t, 0.8, 0.3)
    z = t >= LAST_ZAP
    grape(d, 430, 1150, 120, "sus" if t < 42 else "scared" if not z else "scream", 1, look=0.6 * math.sin(t * 2))
    grape(d, 650, 1150, 120, "sus" if t < 42 else "scared" if not z else "scream", 1, look=0.6 * math.sin(t * 2))
    if z: plasma(d, 540, 1150, t, 120, 1, 3); sparks(d, 540, 1150, t, LAST_ZAP, 60, 1300, (255, 210, 255), 1, 33)
def u_end(t, d):
    a = ease(pr(t, OUTRO, OUTRO + 0.3))
    k = back(pr(t, OUTRO, OUTRO + .2))
    d.rect(110, 230, 970, 400, fill=A(WARN, a * min(1, k)), r=34)
    d.text(540, 315, "千万别在家试", int(100 * (0.6 + .4 * k)), A(WHITE, a), k=1)
    d.text(540, 470, "会损坏微波炉，甚至起火", 50, A(WHITE, a), k=1)
    d.text(540, 640, "你还见过什么东西在微波炉里冒火？", 46, A(YEL, a * ease(pr(t, 40.5, 40.8))), k=1)
    d.text(540, 1500, "Khattak et al., PNAS 116:4000 (2019)", 30, A(WHITE, a), k=2)
    flash(d, t, [LAST_ZAP], WHITE, 0.8)
    if t > DUR - 0.3: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.3, DUR)))

SUBS = [(0.6, 2.6, "葡萄放进微波炉，几秒就喷出等离子火球。"),
        (2.6, 6.0, "网上一直说：是葡萄皮在当天线。"),
        (6.0, 9.0, "可科学家把两颗完整的葡萄贴在一起——照样冒火。"),
        (9.0, 12.0, "换成几乎纯水的水珠，也一样。"),
        (12.0, 16.0, "葡萄的大小，正好让微波在里面来回反弹。"),
        (16.0, 19.5, "反弹叠加，能量越攒越多——"),
                (24.0, 30.0, "鹌鹑蛋：有水就有热点，没水就没有。"),
        (30.0, 31.0, "火光里的钾和钠，来自葡萄本身。"),
        (35.0, 39.0, "科学家用它模拟纳米尺度的光学“热点”。")]
def subs(t, d):
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.15)) * (1 - pr(t, b - 0.12, b))
            lines = wrap(d, s, 56)
            for i, ln in enumerate(lines):
                y = 1580 + (i - (len(lines) - 1) / 2) * 82
                d.rect(540 - d.tlen(ln, 56) / 2 - 22, y - 42, 540 + d.tlen(ln, 56) / 2 + 22, y + 42, fill=A((0, 0, 0), 0.6 * al), r=14)
                d.text(540, y, ln, 56, A(WHITE, al))
def brand(t, d):
    d.rect(50, 80, 300, 128, fill=A(WHITE, 0.92), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(BG, 1))

SECS = [(0, 2.6, w_hook, u_hook), (2.6, 6.0, w_myth, u_myth), (6.0, 9.0, w_whole, u_whole), (9.0, 12.0, w_bead, u_bead), (12.0, 19.5, w_res, u_res),
        (20.0, 24.0, w_burst, u_burst), (24.0, 30.0, w_egg, u_egg), (30.0, 35.0, w_spec, u_spec), (35.0, 39.0, w_nano, u_nano), (39.0, 45.0, w_end, u_end)]
CUTS = [2.6, 6.0, 9.0, 12.0, 24.0, 30.0, 35.0, 39.0]

def cam(t):
    z, cx, cy, sx, sy = 1.0, 540, 960, 0, 0
    if t < 2.6:
        z = lerp(1.35, 1.0, ease(pr(t, 0, 0.45))) + 0.3 * pulse(t, [HOOK_BOOM], 4) + 0.04 * pulse(t, HOOK_ZAP, 10); cy = 1050
        a = 28 * pulse(t, [HOOK_BOOM], 2.5) + 6 * pulse(t, HOOK_ZAP, 10); sx, sy = shake(t, a, 63)
    elif t < 6: z = 1.0 + 0.06 * pulse(t, MYTH_HITS, 7); cy = 960
    elif t < 9: z = lerp(1.0, 1.2, eio(pr(t, 6, WHOLE_ZAP))) + 0.15 * pulse(t, [WHOLE_ZAP], 5); cy = 1100; sx, sy = shake(t, 18 * pulse(t, [WHOLE_ZAP], 3), 60)
    elif t < 12: z = 1.05 + 0.12 * pulse(t, [BEAD_ZAP], 5) + 0.05 * pulse(t, [ANSWER], 6); cy = 1000; sx, sy = shake(t, 16 * pulse(t, [BEAD_ZAP], 3), 60)
    elif t < 19.5: z = lerp(1.0, 1.35, eio(pr(t, 12, 19.5))) + 0.05 * pulse(t, BOUNCE, 6); cy = 980
    elif BURST <= t < 24:
        z = 1.0 + 0.08 * pulse(t, BURST_HITS, 7) + 0.25 * pulse(t, [BURST], 3); sx, sy = shake(t, 30 * pulse(t, [BURST], 2) + 6 * pulse(t, BURST_HITS, 8), 61)
    elif t < 30: z = 1.05 + 0.08 * pulse(t, EGG_HITS, 6); cy = 1000
    elif t < 35: z = 1.0 + 0.04 * pulse(t, SPEC_HITS, 8)
    elif t < 39: z = lerp(1.25, 1.0, ease(pr(t, 35, 37.5)))
    else: z = lerp(1.3, 1.0, eio(pr(t, 39, 40.5))) + 0.2 * pulse(t, [LAST_ZAP], 4); sx, sy = shake(t, 20 * pulse(t, [LAST_ZAP], 3), 60)
    return z, cx + sx, cy + sy

def frame(t):
    img = Image.new("RGB", (W, H), BG); d = D(img); ui = None
    for a, b, wf, uf in SECS:
        if a <= t < b: wf(t, d); ui = uf
    if SILENCE[0] <= t < SILENCE[1]: img = Image.new("RGB", (W, H), (0, 0, 0)); d = D(img); ui = None
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    if abs(z - 1) > 1e-3: img = img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    elif cx != 540 or cy != 960:
        img = img.transform((W, H), Image.AFFINE, (1, 0, P(cx - 540), 0, 1, P(cy - 960)), resample=Image.BILINEAR, fillcolor=(0, 0, 0))
    d = D(img)
    if ui: ui(t, d)
    for c in CUTS:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.7 * (1 - (t - c) / 0.1)))
    if not (SILENCE[0] <= t < SILENCE[1]): brand(t, d); warn_badge(d, t); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)

if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.1f}.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for i in range(i0, i1): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); p.wait()
