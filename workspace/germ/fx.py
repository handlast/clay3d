import math, random, sys, subprocess
from PIL import Image, ImageDraw
from base import *


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

