# Characters + environment for 《戳一下就闪绿光》: deep-sea karst cave, red precious coral, golden polyps that blink green.
import math, random
from fx import *
import easing as E

GOLDP = (255, 206, 52); GOLDP_D = (214, 150, 30); GOLDP_L = (255, 238, 140)
GLOWC = (90, 255, 140); GLOW_L = (200, 255, 210)
CORAL = (226, 70, 72); CORAL_D = (160, 40, 52); CORAL_L = (255, 130, 120)
DEEP1 = (8, 32, 62); DEEP2 = (2, 10, 26); ROCK = (26, 40, 62); ROCK_L = (44, 66, 96); ROCK_D = (14, 22, 38)
ROVY = (255, 196, 40); ROVY_D = (200, 140, 20); METAL = (170, 186, 204); NAVYT = (22, 22, 40); GOLD = (255, 200, 60)
FISH = (60, 84, 120); FISH_D = (36, 52, 80); FISH_L = (100, 130, 170); CRAB = (232, 120, 70); CRAB_D = (180, 80, 46)
rr = random.Random(5)
SNOW = [(rr.uniform(0, 1080), rr.uniform(0, 1920), rr.uniform(2, 5), rr.uniform(0.2, 1)) for _ in range(90)]

def rot(pts, ang, ox, oy):
    c, s = math.cos(ang), math.sin(ang)
    return [(ox + u * c - v * s, oy + u * s + v * c) for u, v in pts]

# ---------------- environment ----------------
def deep(d, t, top=DEEP1, bot=DEEP2, snow=1.0):
    grad(d, top, bot)
    for x, y, r, sp in SNOW:
        yy = (y + t * 30 * sp) % 1980 - 30; xx = x + 10 * math.sin(t * 0.6 + y)
        d.circ(xx, yy, r, fill=A((200, 220, 255), 0.25 * snow * sp))
def caverock(d, t, open_=1.0, y0=0, a=1.0):
    """cave mouth frame: rock masses left/right/top; open_ widens the hole"""
    w = 160 + 120 * (1 - open_)
    L = [(-60, -60), (w + 120, -60), (w + 40, 300), (w + 90, 620), (w - 10, 980), (w + 70, 1360), (w, 1980), (-60, 1980)]
    R = [(1140, -60), (1080 - w - 140, -60), (1080 - w - 30, 380), (1080 - w - 100, 760), (1080 - w + 10, 1120), (1080 - w - 60, 1500), (1080 - w, 1980), (1140, 1980)]
    for P_ in (L, R):
        d.poly([(x, y + y0) for x, y in P_], A(ROCK, a))
        d.line([(x, y + y0) for x, y in P_[1:-1]], A(ROCK_L, 0.8 * a), 10)
    for i in range(7):
        x = 40 + (i * 157) % 1000; y = 1700 + (i % 3) * 60
        d.ell(x, y + y0, 180, 70, A(ROCK_D, a))
def floor(d, y, a=1.0):
    d.poly([(-50, y + 30)] + [(x, y + 18 * math.sin(x / 90)) for x in range(-50, 1131, 30)] + [(1130, 1980), (-50, 1980)], A(ROCK, a))
    d.line([(x, y + 18 * math.sin(x / 90)) for x in range(-50, 1131, 30)], A(ROCK_L, 0.7 * a), 8)

BR = []
def _branch(x, y, ang, L, w, dep, rnd):
    x2, y2 = x + math.cos(ang) * L, y + math.sin(ang) * L
    BR.append((x, y, x2, y2, w, dep))
    if dep >= 4: return
    for da in (-0.5 + rnd.uniform(-0.15, 0.15), 0.42 + rnd.uniform(-0.15, 0.15)):
        _branch(x2, y2, ang + da, L * rnd.uniform(0.62, 0.78), w * 0.68, dep + 1, rnd)
_branch(0, 0, -math.pi / 2, 300, 46, 0, random.Random(21))
TIPS = [(x2, y2, dep) for x, y, x2, y2, w, dep in BR]
def coral(d, x, y, s, t, a=1.0, grow=1.0):
    """red precious-coral tree, rooted at (x, y); returns list of anchor points (for polyps)"""
    pts = []
    for (x0, y0, x1, y1, w, dep) in BR:
        k = cl(grow * 5 - dep)
        if k <= 0: continue
        sw = math.sin(t * 0.8 + dep) * 3 * dep
        X0, Y0, X1, Y1 = x + x0 * s, y + y0 * s, x + (x0 + (x1 - x0) * k) * s + sw, y + (y0 + (y1 - y0) * k) * s
        d.line([(X0, Y0), (X1, Y1)], A(CORAL, a), w * s)
        d.line([(X0 - w * s * 0.18, Y0), (X1 - w * s * 0.18, Y1)], A(CORAL_L, 0.5 * a), w * s * 0.22)
        d.circ(X1, Y1, w * s * 0.5, fill=A(CORAL, a))
        if k >= 1: pts.append((X1, Y1, dep))
    return pts

# ---------------- the polyp ----------------
def polyp(d, x, y, s, t, glow=0.0, mood="happy", a=1.0, open_=1.0, look=0.0, face_=True, sway=0.0, hide=0.0):
    """golden zoantharian polyp: column + crown of 24-26 tentacles; glow 0..1 tints green + halo"""
    h = 120 * s * (1 - 0.45 * hide); r = 46 * s
    body = mix(GOLDP, GLOWC, glow * 0.85); bodyD = mix(GOLDP_D, (40, 190, 100), glow * 0.85); bodyL = mix(GOLDP_L, GLOW_L, glow)
    if glow > 0.02:
        glow_(d, x, y - h, 260 * s * (0.6 + 0.4 * glow), GLOWC, 0.9 * glow * a)
    top = y - h
    sw = sway + 4 * s * math.sin(t * 1.6 + x * 0.01)
    # tentacles: 13 visible back + front
    n = 13; op = open_ * (1 - hide)
    for layer in (0, 1):
        for i in range(n):
            u = (i + 0.5 * layer) / (n - 1) - 0.5
            ang = -math.pi / 2 + u * 2.6 * (0.3 + 0.7 * op)
            L = (70 + 10 * math.sin(i * 1.7)) * s * (0.25 + 0.75 * op)
            wv = math.sin(t * 3 + i * 0.8) * 0.12
            x1, y1 = x + sw + math.cos(ang + wv) * L, top + math.sin(ang + wv) * L
            xm, ym = x + sw * 0.6 + math.cos(ang) * L * 0.5, top + math.sin(ang) * L * 0.55
            col = bodyD if layer == 0 else bodyL
            d.line([(x + sw * 0.4, top + 4 * s), (xm, ym), (x1, y1)], A(col, a), 11 * s if layer else 13 * s)
            if layer: d.circ(x1, y1, 7 * s, fill=A(bodyL, a))
    d.ell(x + sw * 0.4, top, r * 1.05, 16 * s, A(bodyD, a))   # oral disc
    d.poly([(x - r, y), (x - r * 0.95 + sw * 0.4, top), (x + r * 0.95 + sw * 0.4, top), (x + r, y)], A(body, a))
    d.ell(x, y, r, 14 * s, A(body, a))
    d.line([(x - r * 0.55, y - 8 * s), (x - r * 0.5 + sw * 0.4, top + 10 * s)], A(bodyL, 0.7 * a), 9 * s)
    if face_ and s > 0.35:
        fy = y - h * 0.48; fx = x + sw * 0.25
        face(d, fx, fy, 38 * s, mood, a, look)
    return {"top": (x + sw * 0.4, top), "face": (x, y - h * 0.48)}
def glow_(d, x, y, r, col, a, n=8):
    if a <= 0.01: return
    for i in range(n):
        k = 1 - i / n
        d.circ(x, y, r * (0.2 + 0.8 * k), fill=A(col, a * 0.11 * (1.25 - k * 0.7)))

# ---------------- machines ----------------
def rov(d, x, y, s, t, a=1.0, lights=1.0):
    bob = 6 * s * math.sin(t * 1.3)
    y += bob
    if lights > 0:
        for dx in (-70, 70):
            d.poly([(x + dx * s, y + 60 * s), (x + dx * s - 260 * s, y + 900 * s), (x + dx * s + 260 * s, y + 900 * s)], A((255, 250, 210), 0.08 * lights * a))
    d.rect(x - 150 * s, y - 90 * s, x + 150 * s, y + 70 * s, fill=A(ROVY, a), r=24 * s)
    d.rect(x - 150 * s, y - 90 * s, x + 150 * s, y - 50 * s, fill=A(ROVY_D, a), r=20 * s)
    for dx in (-110, 110):
        d.rect(x + dx * s - 26 * s, y + 70 * s, x + dx * s + 26 * s, y + 110 * s, fill=A(METAL, a), r=8 * s)
    for dx in (-70, 70):
        d.circ(x + dx * s, y + 40 * s, 22 * s, fill=A((255, 250, 220), a)); glow_(d, x + dx * s, y + 40 * s, 80 * s, (255, 250, 200), 0.6 * lights * a)
    d.circ(x, y - 10 * s, 34 * s, fill=A((30, 40, 60), a)); d.circ(x - 8 * s, y - 18 * s, 10 * s, fill=A((180, 220, 255), a))
    return (x, y + 110 * s)
def minirov(d, x, y, s, t, a=1.0, arm=0.0, tx=None, ty=None):
    if tx is not None: d.line([(tx, ty), (lerp(tx, x, 0.5) + 30, lerp(ty, y, 0.5) + 40), (x, y - 30 * s)], A((255, 140, 60), 0.9 * a), 5)
    d.rect(x - 70 * s, y - 40 * s, x + 70 * s, y + 40 * s, fill=A(ROVY, a), r=18 * s)
    d.circ(x - 30 * s, y, 14 * s, fill=A((255, 250, 220), a)); glow_(d, x - 30 * s, y, 70 * s, (255, 250, 210), 0.5 * a)
    d.circ(x + 26 * s, y - 4 * s, 18 * s, fill=A((30, 40, 60), a)); d.circ(x + 21 * s, y - 9 * s, 6 * s, fill=A((180, 220, 255), a))
    # arm reaching down-left
    ex, ey = x - 40 * s - 90 * s * arm, y + 40 * s + 90 * s * arm
    d.line([(x - 20 * s, y + 36 * s), (ex, ey)], A(METAL, a), 10 * s); d.circ(ex, ey, 10 * s, fill=A(METAL, a))
    return (ex, ey)

# ---------------- creatures ----------------
def thief(d, x, y, s, t, a=1.0, mood="sus", scared=0.0):
    """little crab with a bandit mask"""
    for i in range(3):
        for sd in (-1, 1):
            lx = x + sd * (40 + i * 18) * s; ly = y + 10 * s
            d.line([(x + sd * 30 * s, y), (lx + sd * 20 * s, ly - 20 * s + 6 * s * math.sin(t * 12 + i)), (lx + sd * 34 * s, ly + 30 * s)], A(CRAB_D, a), 8 * s)
    for sd in (-1, 1):
        cx_, cy_ = x + sd * 78 * s, y - 50 * s - 10 * s * math.sin(t * 6)
        d.line([(x + sd * 36 * s, y - 14 * s), (cx_, cy_ + 20 * s)], A(CRAB_D, a), 10 * s)
        d.circ(cx_, cy_, 22 * s, fill=A(CRAB, a)); d.poly([(cx_, cy_), (cx_ + sd * 26 * s, cy_ - 30 * s), (cx_ + sd * 6 * s, cy_ - 26 * s)], A(DEEP2, a))
    d.ell(x, y, 62 * s, 42 * s, A(CRAB, a)); d.ell(x - 14 * s, y - 14 * s, 28 * s, 12 * s, A((255, 170, 120), 0.6 * a))
    d.rect(x - 52 * s, y - 26 * s, x + 52 * s, y - 4 * s, fill=A((30, 26, 40), a), r=10 * s)   # bandit mask
    for sd in (-1, 1):
        ey = y - 15 * s
        d.circ(x + sd * 22 * s, ey, (10 + 4 * scared) * s, fill=A(WHITE, a)); d.circ(x + sd * 22 * s, ey, 4 * s, fill=A(INK, a))
    if scared > 0.3: d.ell(x, y + 16 * s, 10 * s, 12 * s, A(INK, a))
    else: d.arc(x, y + 6 * s, 16 * s, 10 * s, 20, 160, A(INK, a), 4 * s)
def bigfish(d, x, y, s, t, a=1.0, mouth_=0.3, face_dir=-1, eye_glow=0.0):
    sd = face_dir
    tail = [(x - sd * 230 * s, y), (x - sd * 330 * s, y - 90 * s + 10 * s * math.sin(t * 5)), (x - sd * 320 * s, y + 90 * s + 10 * s * math.sin(t * 5))]
    d.poly(tail, A(FISH_D, a))
    d.ell(x, y, 260 * s, 140 * s, A(FISH, a))
    d.ell(x - sd * 30 * s, y + 50 * s, 190 * s, 60 * s, A(FISH_L, 0.5 * a))
    d.poly([(x - sd * 40 * s, y - 120 * s), (x - sd * 140 * s, y - 210 * s), (x - sd * 160 * s, y - 110 * s)], A(FISH_D, a))
    mx = x + sd * 200 * s
    m = mouth_
    d.poly([(mx + sd * 70 * s, y + 10 * s - 50 * s * m), (mx - sd * 40 * s, y + 20 * s), (mx + sd * 70 * s, y + 30 * s + 50 * s * m)], A(DEEP2, a))
    for j in range(4):
        tx_ = mx + sd * (20 + j * 14) * s
        d.poly([(tx_, y + 10 * s - 40 * s * m), (tx_ + sd * 6 * s, y + 10 * s - 40 * s * m + 18 * s), (tx_ + sd * 12 * s, y + 10 * s - 40 * s * m)], A(WHITE, a))
    ex, ey = x + sd * 120 * s, y - 40 * s
    if eye_glow > 0: glow_(d, ex, ey, 90 * s, (255, 240, 160), 0.7 * eye_glow * a)
    d.circ(ex, ey, 30 * s, fill=A(WHITE, a)); d.circ(ex + sd * 8 * s, ey, 14 * s, fill=A(INK, a)); d.circ(ex + sd * 3 * s, ey - 6 * s, 5 * s, fill=A(WHITE, a))
    d.line([(ex - 34 * s, ey - 44 * s), (ex + 34 * s, ey - 34 * s * (1 if sd < 0 else -1) - 40 * s)], A(INK, a), 7 * s)
def bubble(d, x, y, s_, k, a=1.0, size=40, col=WHITE, tc=NAVYT):
    if k <= 0: return
    w = d.tlen(s_, size, 1) + 40; hh = size * 0.85
    sc = min(1, k)
    d.rect(x - w / 2 * sc, y - hh * sc, x + w / 2 * sc, y + hh * sc, fill=A(col, a), r=hh * sc)
    d.poly([(x - 14, y + hh * sc - 4), (x, y + hh * sc + 24 * sc), (x + 14, y + hh * sc - 4)], A(col, a))
    if sc > 0.6: d.text(x, y, s_, int(size * sc), A(tc, a), k=1)
