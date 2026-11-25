import sys, subprocess
from fx import *
from cues import *

BOD = (150, 98, 58); BOD_L = (196, 140, 86); BOD_D = (104, 66, 40); FRINGE = (240, 160, 74); PALP = (232, 196, 140)
EYEC = (34, 52, 74); RET = (10, 12, 20); NAVYT = (24, 20, 40); SILK = (235, 240, 255); PINK = (255, 150, 190)
GOOD = (110, 225, 130); BAD = (255, 80, 70); FLY = (60, 70, 90)

# ---------------- spider (all geometry goes through a rotate+scale transform; no outlines) ----------------
class Sp:
    def __init__(s, d, x, y, sc, rot=0.0):
        s.d, s.x, s.y, s.sc = d, x, y, sc; s.c, s.s = math.cos(rot), math.sin(rot)
    def T(s, lx, ly):
        lx *= s.sc; ly *= s.sc
        return (s.x + lx * s.c - ly * s.s, s.y + lx * s.s + ly * s.c)
    def ell(s, cx, cy, rx, ry, col, n=28, a0=0.0, a1=2 * math.pi):
        pts = [s.T(cx + rx * math.cos(lerp(a0, a1, i / n)), cy + ry * math.sin(lerp(a0, a1, i / n))) for i in range(n + 1)]
        s.d.poly(pts, col)
    def line(s, pts, col, w): s.d.line([s.T(*p) for p in pts], col, w * s.sc)
    def circ(s, cx, cy, r, col):
        X, Y = s.T(cx, cy); s.d.circ(X, Y, r * s.sc, fill=col)

def spider(d, x, y, sc, t, mood="happy", a=1.0, rot=0.0, sleep=0.0, look=(0.0, 0.0), curl=0.0, twitch=0.0, clean=-1, droop=0.0, bags=0.0, sq=0.0):
    """sc ~ head half-width in px. local units: head radius ~1. y down. mood: happy/proud/scared/sleepy/dream/sus"""
    g = Sp(d, x, y, sc, rot)
    # legs: 4 per side, root on head sides, two segments
    for side in (-1, 1):
        for i in range(4):
            jit = twitch * (0.5 + 0.5 * math.sin(t * (29 + i * 7) + i * 2.1 + side * 1.3)) * (0.5 + 0.5 * math.sin(t * 11 + i))
            k = cl(curl + jit * 0.8)
            rx, ry = side * 0.62, -0.25 + i * 0.25
            kx = rx + side * (0.8 - 0.25 * k); ky = ry - 0.55 + i * 0.22 + 0.15 * droop
            fx_ = kx + side * 0.5 * (1 - 1.9 * k); fy_ = ky + (0.95 - 0.35 * k) + 0.25 * droop
            if clean == i + (0 if side == -1 else 4): continue   # drawn in front of the face below
            g.line([(rx, ry), (kx, ky)], A(BOD_D, a), 0.18)
            g.line([(kx, ky), (fx_, fy_)], A(BOD_D, a), 0.14)
            g.circ(lerp(kx, fx_, 0.5), lerp(ky, fy_, 0.5), 0.085, A(BOD_L, a))
            g.circ(kx, ky, 0.1, A(BOD_L, a)); g.circ(fx_, fy_, 0.075, A(FRINGE, a))
    # abdomen (behind, below)
    ab_y = 1.25 + 0.15 * droop
    g.ell(0, ab_y, 0.78 * (1 + sq), 0.86 * (1 - sq), A(BOD_D, a))
    g.ell(-0.05, ab_y - 0.05, 0.72 * (1 + sq), 0.8 * (1 - sq), A(BOD, a))
    for j in range(3): g.ell(0, ab_y - 0.3 + j * 0.3, 0.42 - j * 0.08, 0.07, A(BOD_L, 0.8 * a))
    for j in range(9):
        an = math.pi * 0.15 + j * math.pi * 0.7 / 8
        g.ell(math.cos(an) * 0.74, ab_y + math.sin(an) * 0.82, 0.12, 0.08, A(FRINGE, 0.9 * a))
    # head
    g.ell(0, 0, 1.0 * (1 + sq), 0.85 * (1 - sq), A(BOD_D, a))
    g.ell(-0.04, -0.05, 0.95 * (1 + sq), 0.8 * (1 - sq), A(BOD, a))
    g.ell(-0.35, -0.45, 0.35, 0.16, A(BOD_L, 0.7 * a))
    for j in range(7):   # fuzzy fringe on top
        an = math.pi * 1.15 + j * math.pi * 0.7 / 6
        g.ell(math.cos(an) * 0.95, math.sin(an) * 0.8, 0.13, 0.09, A(FRINGE, 0.85 * a))
    # side eyes
    for sx in (-0.78, 0.78): g.circ(sx, -0.2, 0.11, A(EYEC, a)); g.circ(sx - 0.03, -0.24, 0.035, A(WHITE, 0.8 * a))
    for sx in (-0.5, 0.5): g.circ(sx, -0.62, 0.08, A(EYEC, a))
    # big front eyes
    er = 0.33
    for sx in (-0.36, 0.36):
        g.circ(sx, -0.12, er, A(EYEC, a))
        if sleep < 0.5 or mood == "dream":
            lx, ly = look
            g.circ(sx + lx * er * 0.45, -0.12 + ly * er * 0.45, er * 0.62, A(RET, a))
            g.circ(sx - er * 0.35, -0.12 - er * 0.38, er * 0.22, A(WHITE, 0.9 * a)); g.circ(sx + er * 0.3, -0.12 + er * 0.3, er * 0.08, A(WHITE, 0.7 * a))
            if mood == "scared": g.circ(sx, -0.12, er * 0.2, A(WHITE, 0.0))
        else:   # closed: lid colour + lash arc
            g.ell(sx, -0.12, er, er, A(BOD_L, a), a0=math.pi, a1=2 * math.pi)
            g.ell(sx, -0.12, er, er * 0.25, A(BOD_L, a))
            g.line([(sx - er * 0.8, -0.05), (sx, 0.04), (sx + er * 0.8, -0.05)], A(INK, a), 0.06)
        if bags > 0: g.ell(sx, 0.3, er * 0.8, 0.07, A((90, 60, 120), bags * a))
    # palps + mouth
    for sx in (-0.18, 0.18): g.ell(sx, 0.48, 0.13, 0.17, A(PALP, a))
    if mood in ("happy", "proud"): g.ell(0, 0.33, 0.16, 0.1, A(INK, a), a0=0, a1=math.pi)
    elif mood == "scared": g.ell(0, 0.35, 0.08, 0.1, A(INK, a))
    elif mood == "sleepy" or mood == "dream": g.ell(0, 0.33, 0.06, 0.05, A(INK, 0.8 * a))
    elif mood == "sus": g.line([(-0.12, 0.33), (0.12, 0.3)], A(INK, a), 0.05)
    if mood in ("happy", "proud"):
        for sx in (-0.62, 0.62): g.ell(sx, 0.22, 0.12, 0.06, A(PINK, 0.6 * a))
    if 0 <= clean < 8:   # one leg pulled through the palps, rubbing
        side = -1 if clean < 4 else 1; rb = 0.12 * math.sin(t * 40)
        kx, ky = side * 1.15, -0.55; fx_, fy_ = side * (0.05 + rb), 0.62
        g.line([(side * 0.62, -0.25 + (clean % 4) * 0.25), (kx, ky)], A(BOD_D, a), 0.18)
        g.line([(kx, ky), (fx_, fy_)], A(BOD_D, a), 0.15)
        g.circ(kx, ky, 0.11, A(BOD_L, a)); g.circ(lerp(kx, fx_, 0.5), lerp(ky, fy_, 0.5), 0.09, A(BOD_L, a)); g.circ(fx_, fy_, 0.09, A(FRINGE, a))
        for j in range(4): g.circ(fx_ + side * 0.1 * j + rb, fy_ - 0.15 - 0.12 * j, 0.06, A(WHITE, 0.7 * a))

def zzz(d, x, y, t, a=1.0, size=60):
    for i in range(3):
        u = (t * 0.6 + i / 3) % 1
        d.text(x + u * 120 + 20 * math.sin(t * 2 + i), y - u * 220, "Z", int(size * (0.6 + 0.6 * u)), A(WHITE, a * math.sin(u * math.pi)), k=1)

def hammock(d, x, y, w, t, a=1.0, k=1.0):
    sw = 8 * math.sin(t * 1.6)
    d.line([(x - w / 2 - 120, y - 260), (x - w / 2, y)], A(SILK, 0.6 * a * k), 3)
    d.line([(x + w / 2 + 120, y - 260), (x + w / 2, y)], A(SILK, 0.6 * a * k), 3)
    pts = [(x - w / 2 + w * i / 20, y + math.sin(i / 20 * math.pi) * 40 * k + sw * math.sin(i / 20 * math.pi)) for i in range(21)]
    for j in range(5): d.line([(px, py - j * 6) for px, py in pts], A(SILK, (0.5 - j * 0.07) * a * k), 4)
    for i in range(0, 21, 3): d.line([(pts[i][0], pts[i][1] - 30), pts[i]], A(SILK, 0.35 * a * k), 2)

def tag(d, x, y, s, col, a=1.0, size=40, tc=NAVYT):
    if a <= 0.01: return
    w = d.tlen(s, size, 1) + 44
    d.rect(x - w / 2, y - size * 0.78, x + w / 2, y + size * 0.78, fill=A(col, 0.95 * a), r=size * 0.6)
    d.text(x, y, s, size, A(tc, a), k=1)
def popk(t, t0): return min(1, back(pr(t, t0, t0 + 0.2)))
def bubble(d, x, y, s, side, col, tcol, a, size=44):
    if a <= 0: return
    w = d.tlen(s, size, 1) + 60; x0 = x if side < 0 else x - w
    d.rect(x0, y - 48, x0 + w, y + 48, fill=A(col, a), r=36)
    tx = x0 + 40 if side < 0 else x0 + w - 40
    d.poly([(tx - 14, y + 36), (tx - (22 if side < 0 else -22), y + 78), (tx + 14, y + 36)], A(col, a))
    d.text(x0 + w / 2, y, s, size, A(tcol, a), k=1)
def stars(d, t, a=1.0, n=40, seed=3):
    r = random.Random(seed)
    for i in range(n):
        x, y = r.uniform(0, 1080), r.uniform(0, 1500); tw = 0.5 + 0.5 * math.sin(t * r.uniform(1, 4) + i)
        d.circ(x, y, r.uniform(2, 5), fill=A(WHITE, a * (0.3 + 0.6 * tw)))
def moon(d, x, y, r, col=(255, 236, 170), a=1.0, bg=(20, 24, 60)):
    glow(d, x, y, r * 2.4, col, 0.5 * a); d.circ(x, y, r, fill=A(col, a)); d.circ(x + r * 0.45, y - r * 0.25, r * 0.85, fill=A(bg, a))
def swirl(d, t, c1, c2, cx=540, cy=900):
    grad(d, c1, c2)
    for i in range(9):
        r = ((t * 120 + i * 140) % 1300)
        d.circ(cx, cy, r, outline=A(mix(c1, WHITE, 0.25), 0.18 * (1 - r / 1300)), w=40)
def check(d, x, y, s, k, col=GOOD):
    if k <= 0: return
    d.line([(x - s * 0.5, y), (x - s * 0.1, y + s * 0.4 * min(1, k * 2)), ], A(col, 1), s * 0.22)
    if k > 0.5: d.line([(x - s * 0.1, y + s * 0.4), (lerp(x - s * 0.1, x + s * 0.6, (k - 0.5) * 2), lerp(y + s * 0.4, y - s * 0.5, (k - 0.5) * 2))], A(col, 1), s * 0.22)
def fly(d, x, y, s, t, a=1.0):
    for sg in (-1, 1): d.ell(x + sg * s * 0.55, y - s * 0.45, s * 0.55, s * 0.28 + s * 0.12 * math.sin(t * 60), A((210, 235, 255), 0.6 * a))
    d.ell(x, y, s * 0.55, s * 0.45, A(FLY, a)); d.circ(x - s * 0.25, y - s * 0.15, s * 0.2, fill=A(BAD, a)); d.circ(x + s * 0.25, y - s * 0.15, s * 0.2, fill=A(BAD, a))
def speaker(d, x, y, s, t, on):
    d.rect(x - s * 0.5, y - s * 0.7, x + s * 0.5, y + s * 0.7, fill=A((60, 64, 80), 1), r=s * 0.15)
    p = 1 + 0.12 * on
    d.circ(x, y + s * 0.15, s * 0.36 * p, fill=A((30, 32, 44), 1)); d.circ(x, y + s * 0.15, s * 0.14 * p, fill=A((120, 124, 140), 1))
    d.circ(x, y - s * 0.42, s * 0.12, fill=A((30, 32, 44), 1))
def lab_bg(d, t):
    grad(d, (30, 120, 130), (16, 60, 74))
    for i in range(8): d.rect(0, 300 + i * 160, 1080, 304 + i * 160, fill=A(WHITE, 0.05))
    d.rect(140, 1080, 940, 1110, fill=A((210, 230, 235), 0.25), r=10)

# ---------------- scenes ----------------
def s_hook(t, d):
    if t < HOOK_HIT: grad(d, (24, 30, 80), (12, 14, 40))
    else: rays(d, t, (130, 60, 210), (80, 30, 150), n=20, cx=540, cy=900)
    stars(d, t, 0.6)
    k = t - HOOK_HIT
    glow(d, 540, 900, 460, (255, 140, 255), 0.4 * pulse(t, [HOOK_HIT], 2.5))
    hammock(d, 540, 720, 520, t)
    tw = 1.0 if t > HOOK_HIT else 0.0
    sq = 0.18 * math.exp(-max(k, 0) * 7) * math.sin(max(k, 0) * 38) if k > 0 else 0
    spider(d, 540, 960, 170, t, "dream", rot=math.pi, sleep=1, look=(math.sin(t * 23), 0.3 * math.cos(t * 17)), curl=0.25, twitch=tw, droop=0.4, sq=sq)
    for i in range(10):   # twitch motion marks
        if t > HOOK_HIT:
            an = i * 0.63 + 0.3; r = 380 + 30 * math.sin(t * 40 + i)
            x, y = 540 + math.cos(an) * r, 900 + math.sin(an) * r * 0.9
            d.line([(x, y), (x + math.cos(an) * 40, y + math.sin(an) * 40)], A(YEL, 0.8 * (0.5 + 0.5 * math.sin(t * 30 + i))), 8)
    sparks(d, 540, 900, t, HOOK_HIT, n=50, spd=1100, col=(255, 220, 120))
    stamp(d, t, HOOK_HIT, "蜘蛛会做梦？", 540, 380, 120, WHITE)

def s_lab(t, d):
    lab_bg(d, t)
    for i, h in enumerate(CAMS):   # cameras pop in
        k = popk(t, h); cx = 280 if i == 0 else 800
        if k > 0:
            d.rect(cx - 70 * k, 470 - 45 * k, cx + 70 * k, 470 + 45 * k, fill=A((40, 44, 56), 1), r=14)
            d.circ(cx, 470, 32 * k, fill=A((90, 200, 255), 1)); d.circ(cx - 8, 462, 10 * k, fill=A(WHITE, 0.7))
            if math.sin(t * 8) > 0: d.circ(cx + 52 * k, 438, 8, fill=A(BAD, 1))
            d.poly([(cx, 510), (540 - 160, 1080), (540 + 160, 1080)], A((140, 220, 255), 0.07))
    spider(d, 540, 900, 130, t, "sus" if t < NAME_HIT else "happy", look=(math.sin(t * 2) * 0.6, -0.3), sq=0.12 * pulse(t, [LAB_HIT], 7))
    stamp(d, t, LAB_HIT, "德国 · 波恩大学", 540, 320, 76, WHITE)
    if t > NAME_HIT:
        tag(d, 540, 1160, "缤纷跳蛛 Portia fimbriata", YEL, popk(t, NAME_HIT), 40)
def s_brush(t, d):
    grad(d, (255, 170, 200), (220, 110, 160))
    for i in range(12):   # bathroom tiles
        for j in range(16): d.rect(i * 92 + 4, j * 122 + 4, i * 92 + 88, j * 122 + 118, fill=A(WHITE, 0.08), r=10)
    n = sum(1 for h in LEGS if t >= h)
    ci = n - 1 if 0 < n <= 8 and t < LEGS[-1] + 0.3 else -1
    spider(d, 540, 960, 150, t, "happy", look=(0, 0.4), clean=ci, sq=0.06 * pulse(t, LEGS, 10))
    for h in LEGS:   # foam bubbles
        u = t - h
        if 0 <= u < 0.9:
            for j in range(5):
                d.circ(700 + (j - 2) * 30 + 30 * u * (j - 2), 880 - u * 260 - j * 10, 14 + j * 3, fill=A(WHITE, 0.8 * (1 - u)))
    if n > 0: bignum(d, t, min(n, 8), LEGS[min(n, 8) - 1], y=380, col=WHITE, size=230)
    d.text(540, 520, "/ 8 条腿", 52, A(WHITE, 0.9 if n > 0 else 0), k=1)
    if t > TOOTH_HIT: tag(d, 540, 1170, "像人睡前刷牙", WHITE, popk(t, TOOTH_HIT), 52, (190, 60, 120))
def s_ham(t, d):
    grad(d, (40, 30, 110), (18, 14, 60)); stars(d, t, 0.8); moon(d, 880, 290, 60, bg=(36, 28, 104))
    k = ease(pr(t, SILK_HIT - 0.3, SILK_HIT + 0.5))
    hammock(d, 540, 780, 520, t, k=k)
    f = eio(pr(t, FLIP_HIT - 0.4, FLIP_HIT + 0.2))
    y = lerp(1180, 1000, ease(pr(t, HAM, SILK_HIT + 0.6)))
    spider(d, 540, y, 140, t, "happy" if f < 0.5 else "sleepy", rot=f * math.pi, sleep=1 if f > 0.8 else 0, look=(0, -0.6), sq=0.15 * pulse(t, [FLIP_HIT], 8))
    if f > 0.9: zzz(d, 700, 900, t)
    stamp(d, t, SILK_HIT, "丝做的小吊床", 520, 420, 84, WHITE)
    if t > FLIP_HIT: tag(d, 540, 570, "倒挂着睡", YEL, popk(t, FLIP_HIT), 52)
def s_check(t, d):
    rays(d, t, (255, 210, 80), (250, 180, 40), n=16, cx=540, cy=1500)
    items = ["姿势固定", "一动不动", "更难叫醒", "按昼夜规律", "缺觉会补觉"]
    d.rect(170, 330, 910, 1180, fill=A(WHITE, 0.92), r=40)
    d.text(540, 410, "睡眠 5 条标准", 64, A(NAVYT, 1), k=1)
    for i, s in enumerate(items):
        yy = 530 + i * 128; k = popk(t, TICKS[i])
        d.rect(230, yy - 46, 330, yy + 46, fill=A((230, 232, 240), 1), r=16)
        d.text(370, yy, s, 54, A(NAVYT, 1), anchor="lm", k=1)
        if t < TICKS[i]: d.text(280, yy, str(i + 1), 46, A((150, 150, 170), 1), k=1)
        else: check(d, 285, yy - 4, 70 * k, ease(pr(t, TICKS[i], TICKS[i] + 0.25)))
def s_deep(t, d):
    k = pr(t, DEEP, SIL0)
    grad(d, mix((30, 24, 90), (8, 8, 24), k), mix((12, 10, 40), (2, 2, 8), k)); stars(d, t, 0.6 * (1 - k))
    hammock(d, 540, 700, 520, t)
    spider(d, 540, 940, 160, t, "sleepy", rot=math.pi, sleep=1, droop=0.3 + 0.7 * k, curl=0.1)
    zzz(d, 700, 860, t, 1 - k * 0.7)
    glow(d, 540, 960, 300, (120, 140, 255), 0.25 * (1 - k))
    if t >= SIL0: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.6))
def s_rem(t, d):
    rays(d, t, (255, 80, 200), (170, 40, 160), n=22, cx=540, cy=920)
    glow(d, 540, 920, 520, (255, 230, 120), 0.5 * pulse(t, [REM_HIT], 2))
    hammock(d, 540, 680, 520, t)
    lk = (math.sin(t * 26) * 0.9, 0.4 * math.sin(t * 19))
    spider(d, 540, 920, 175, t, "dream", rot=math.pi, sleep=1, look=lk, curl=0.45 + 0.25 * math.sin(t * 9), twitch=1.0, droop=0.3,
           sq=0.2 * math.exp(-(t - REM_HIT) * 6) * math.sin((t - REM_HIT) * 40))
    sparks(d, 540, 920, t, REM_HIT, n=70, spd=1300, col=(255, 240, 140), seed=4)
    stamp(d, t, REM_HIT, "REM 睡眠！", 540, 360, 130, WHITE)
    if t > REM_HIT + 0.9: tag(d, 540, 540, "像狗狗睡觉时抽腿", WHITE, ease(pr(t, REM_HIT + .9, REM_HIT + 1.2)), 50, (170, 40, 160))
def s_eye(t, d):
    swirl(d, t, (20, 120, 150), (8, 50, 80), cy=880)
    # giant close-up of the two front eyes, retina tubes darting
    for sx in (-1, 1):
        x = 540 + sx * 190; y = 880
        d.circ(x, y, 190, fill=A(EYEC, 1)); d.circ(x, y, 160, fill=A((50, 80, 110), 1))
        lx = math.sin(t * 22 + (0 if sx < 0 else 0.2)) * 70; ly = math.sin(t * 15) * 30
        glow(d, x + lx, y + ly, 120, CYAN, 0.35)
        d.ell(x + lx, y + ly, 80, 95, A(RET, 1))   # the retina tube seen end-on
        d.circ(x - 70, y - 80, 40, fill=A(WHITE, 0.85)); d.circ(x + 60, y + 70, 14, fill=A(WHITE, 0.6))
    for sx in (-1, 1):   # motion arrows
        d.text(540 + sx * 420, 880, "‹" if sx < 0 else "›", 140, A(YEL, 0.5 + 0.5 * math.sin(t * 22)), k=1)
    stamp(d, t, EYE_HIT, "视网膜管在乱转", 540, 400, 84, WHITE)
    for i in range(4):   # curled twitching legs at bottom
        x = 260 + i * 190; ph = math.sin(t * 28 + i * 1.7)
        d.line([(x, 1200), (x + 40 * ph, 1100), (x + 70 + 30 * ph, 1160)], A(BOD_D, 1), 24); d.circ(x + 40 * ph, 1100, 16, fill=A(BOD_L, 1))
def s_sound(t, d):
    grad(d, (230, 70, 60), (150, 30, 40))
    hammock(d, 620, 640, 420, t)
    spider(d, 620, 860, 130, t, "dream", rot=math.pi, sleep=1, look=(math.sin(t * 24), 0), curl=0.4, twitch=0.8, droop=0.3)
    on = pulse(t, HONK, 5)
    speaker(d, 250, 1060, 200, t, on)
    for h in HONK:
        u = (t - h) / 0.7
        if 0 <= u < 1:
            for j in range(3): d.arc(250, 1060, 140 + u * 300 + j * 50, 140 + u * 300 + j * 50, -50, 50, A(WHITE, (1 - u) * (1 - j * .3)), 10)
            stamp(d, t, h, "哔！", 330 + HONK.index(h) * 150, 480 + HONK.index(h) * 40, 70, YEL)
    if t > DEAF_HIT: tag(d, 540, 1180, "照睡不误", WHITE, popk(t, DEAF_HIT), 56, (150, 30, 40))
def s_reb(t, d):
    if t < NIGHT2:
        grad(d, (30, 30, 80), (14, 14, 40)); stars(d, t, 0.5)
        d.text(540, 340, "第 1 晚：不停吵醒", 60, A(WHITE, 1), k=1)
        st = any(0 <= t - h < 0.3 for h in POKES)
        spider(d, 540, 960, 140, t, "scared" if st else "sleepy", sleep=0 if st else 1, look=(0, -0.3), sq=0.15 * pulse(t, POKES, 9))
        for h in POKES:
            k = popk(t, h)
            if 0 < t - h < 0.5: d.line([(860, 760), (lerp(860, 690, k), lerp(760, 860, k))], A((240, 220, 180), 1), 26)
            if t >= h: stamp(d, t, h, "醒!", 300 + POKES.index(h) * 90, 640, 56, YEL)
    else:
        grad(d, (255, 190, 90), (240, 130, 60))
        d.text(540, 340, "第 2 晚：补觉", 60, A(NAVYT, 1), k=1)
        hammock(d, 540, 700, 480, t)
        spider(d, 540, 920, 150, t, "sleepy", rot=math.pi, sleep=1, droop=0.6, bags=1.0)
        zzz(d, 700, 860, t, 1, 80)
        k = ease(pr(t, NIGHT2, LONG_HIT))   # sleep bar grows
        d.rect(220, 1110, 860, 1170, fill=A(WHITE, 0.6), r=30); d.rect(220, 1110, 220 + 640 * (0.45 + 0.55 * k), 1170, fill=A((110, 90, 220), 1), r=35)
        d.text(540, 1140, "睡得更久", 40, A(WHITE, 1), k=1)
        stamp(d, t, LONG_HIT, "多睡！", 820, 520, 90, (110, 60, 200))
def s_proof(t, d):
    rays(d, t, (255, 220, 90), (255, 170, 40), n=18, cx=540, cy=900)
    glow(d, 540, 900, 450, WHITE, 0.4 * pulse(t, [PROOF_HIT], 2))
    for i in range(5): check(d, 240 + i * 150, 530, 80, ease(pr(t, PROOF_HIT + i * 0.08, PROOF_HIT + i * 0.08 + 0.25)), (40, 150, 70))
    spider(d, 540, 920, 150, t, "proud", look=(0, 0), sq=0.15 * pulse(t, [PROOF_HIT, STAGE_HIT], 7))
    stamp(d, t, PROOF_HIT, "真的会睡觉", 540, 380, 110, NAVYT)
    if t > STAGE_HIT:
        k = popk(t, STAGE_HIT)
        tag(d, 350, 660, "安静睡", (90, 110, 230), k, 46, WHITE); tag(d, 730, 660, "REM 样睡", (220, 60, 170), k, 46, WHITE)
        d.text(540, 660, "⇄", 1, A(NAVYT, 0))
def s_dream(t, d):
    grad(d, (110, 70, 190), (60, 30, 120)); stars(d, t, 0.5, seed=8)
    for i, (cx, cy, r) in enumerate([(700, 520, 230), (560, 470, 170), (840, 470, 160), (700, 380, 140)]):
        d.circ(cx, cy, r * popk(t, DREAM_HIT), fill=A(WHITE, 0.95))
    for (cx, cy, r) in [(520, 760, 40), (470, 840, 26)]: d.circ(cx, cy, r * popk(t, DREAM_HIT), fill=A(WHITE, 0.95))
    if t > DREAM_HIT + 0.2:
        fx_ = 700 + 120 * math.sin(t * 3); fy_ = 480 + 40 * math.sin(t * 5)
        fly(d, fx_, fy_, 50, t); d.text(620, 600, "梦到抓苍蝇？", 44, A(NAVYT, ease(pr(t, DREAM_HIT + .2, DREAM_HIT + .5))), k=1)
    spider(d, 400, 980, 130, t, "dream", sleep=1, look=(math.sin(t * 20) * 0.8, 0), curl=0.3, twitch=0.6)
    if t > Q_HIT:
        k = popk(t, Q_HIT); d.text(790, 920, "?", int(220 * k), A(YEL, 1), k=1)
        tag(d, 760, 1160, "还不知道", WHITE, k, 56, (60, 30, 120))
def s_old(t, d):
    grad(d, (90, 150, 110), (40, 80, 60))
    # timeline bar
    d.rect(180, 540, 900, 570, fill=A(WHITE, 0.5), r=15)
    k = ease(pr(t, OLD_HIT, OLD_HIT + 1.0))
    d.rect(180, 540, 180 + 720 * k, 570, fill=A(YEL, 1), r=15)
    d.text(200, 615, "几亿年前", 40, A(WHITE, 1), anchor="lm", k=1); d.text(880, 615, "今天", 40, A(WHITE, 1), anchor="rm", k=1)
    tag(d, 280, 475, "共同祖先", WHITE, popk(t, OLD_HIT), 38)
    spider(d, 330, 960, 110, t, "sleepy", sleep=1, droop=0.2)
    zzz(d, 420, 860, t, 0.9, 40)
    # little human sleeping
    hx, hy = 760, 1000
    if t > OLD2_HIT - 0.2:
        a_ = popk(t, OLD2_HIT - 0.2)
        d.rect(hx - 150, hy + 20, hx + 150, hy + 80, fill=A((240, 240, 255), a_), r=20)
        d.circ(hx - 100, hy, 50, fill=A((255, 214, 178), a_)); d.rect(hx - 60, hy - 20, hx + 150, hy + 30, fill=A((100, 140, 230), a_), r=24)
        d.line([(hx - 120, hy), (hx - 80, hy)], A(INK, a_), 6)
        zzz(d, hx - 60, hy - 60, t, a_, 40)
    stamp(d, t, OLD2_HIT, "都会睡觉", 540, 380, 110, WHITE)
def s_end(t, d):
    grad(d, (255, 200, 150), (255, 140, 120))
    glow(d, 540, 1500, 600, (255, 240, 180), 0.5)
    ci = int((t - OUTRO) / 0.3) % 8 if t < BUBS[2] else -1
    spider(d, 540, 960, 150, t, "happy", look=(0, 0.2), clean=ci)
    bubble(d, 300, 560, "早安，先擦腿", -1, WHITE, NAVYT, popk(t, BUBS[0]))
    bubble(d, 790, 700, "你昨晚做梦了吗？", 1, (110, 60, 200), WHITE, popk(t, BUBS[1]), 40)
    d.text(540, 1330, "Geiger & Rößler, PNAS (2026)", 26, A(NAVYT, 0.75))
    d.text(540, 1372, "doi:10.1073/pnas.2618030123 · University of Bonn", 24, A(NAVYT, 0.7))
    stamp(d, t, BUBS[2], "蜘蛛也睡觉", 540, 330, 100, WHITE)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

def subs(t, d):
    if t >= OUTRO: return
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            ls = wrap(d, s, 52, 670); n = len(ls); y0 = 1350 - (n - 1) * 70
            w = max(d.tlen(x, 52, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 44, 540 + w / 2, y0 + (n - 1) * 70 + 44, fill=A((15, 12, 26), 0.82 * al), r=22)
            for i, x in enumerate(ls): d.text(540, y0 + i * 70, x, 52, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇新发现"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)

SECS = [(0, HOOK_END, s_hook), (LAB, BRUSH, s_lab), (BRUSH, HAM, s_brush), (HAM, CHECK, s_ham), (CHECK, DEEP, s_check),
        (DEEP, REM_HIT, s_deep), (REM_HIT, EYE, s_rem), (EYE, SOUND, s_eye), (SOUND, REB, s_sound), (REB, PROOF, s_reb),
        (PROOF, DREAM, s_proof), (DREAM, OLD, s_dream), (OLD, OUTRO, s_old), (OUTRO, 99, s_end)]
CUTS = [HOOK_END, BRUSH, HAM, CHECK, DEEP, REM_HIT, EYE, SOUND, REB, NIGHT2, PROOF, DREAM, OLD, OUTRO]
def cam(t):
    z = 1.0 + 0.05 * pulse(t, HITS, 7)
    for a, b in RISERS:
        if a <= t < b: z += 0.1 * eio(pr(t, a, b))
    if DEEP <= t < SIL0: z += 0.06 * pr(t, DEEP, SIL0)
    amp = 26 * pulse(t, [HOOK_HIT, REM_HIT], 4) + 5 * pulse(t, HITS, 6)
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx, 960 + sy + 8 * math.sin(t * math.pi / (BEAT * 2))
def frame(t):
    img = Image.new("RGB", (W, H), (30, 20, 50)); d = D(img)
    for a, b, sf in SECS:
        if a <= t < b: sf(t, d); break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.08: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.5 * (1 - (t - c) / 0.08)))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.1f}.png")
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
