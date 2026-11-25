import sys, subprocess
from fx import *
from cues import *

SN = (64, 196, 186); SN_D = (34, 132, 134); SN_B = (255, 214, 90); SN_L = (170, 240, 220)
NAVYT = (24, 20, 40); GOOD = (90, 200, 110); BAD = (240, 80, 70); GOLD = (255, 200, 60)
BIRD = (70, 34, 96); PINK = (255, 150, 170); PINK_D = (220, 104, 130); TIRE = (64, 68, 82)

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
def speedlines(d, t, a=0.35, col=WHITE, y0=300, y1=1200, spd=2600, n=16, seed=5):
    r2 = random.Random(seed)
    for i in range(n):
        y = r2.uniform(y0, y1); L = r2.uniform(120, 320); x = (r2.uniform(0, 1400) - t * spd) % 1500 - 200
        d.line([(x, y), (x + L, y)], A(col, a), 6)
def gscroll(d, y, off, col, top, a=1.0):
    d.rect(-50, y, OW + 50, OH + 50, fill=A(col, a)); d.rect(-50, y, OW + 50, y + 18, fill=A(top, a))
    for i in range(12):
        x = (i * 130 - off) % 1560 - 240
        d.rect(x, y + 50 + (i % 3) * 40, x + 70 + (i % 2) * 40, y + 62 + (i % 3) * 40, fill=A(mix(col, (0, 0, 0), 0.22), 0.7 * a), r=6)
def dashed(d, x0, x1, y, col, a=1.0, w=6, seg=28):
    x = x0
    while x < x1: d.line([(x, y), (min(x1, x + seg), y)], A(col, a), w); x += seg * 1.8
def star(d, x, y, r, col, a=1.0, rot=0):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45; ang = rot + i * math.pi / 5 - math.pi / 2
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    d.poly(pts, A(col, a))
def arrow(d, pts, col, a=1.0, w=14, head=34):
    d.line(pts, A(col, a), w)
    (x0, y0), (x1, y1) = pts[-2], pts[-1]; ang = math.atan2(y1 - y0, x1 - x0)
    d.poly([(x1 + math.cos(ang) * head * 0.6, y1 + math.sin(ang) * head * 0.6), (x1 + math.cos(ang + 2.4) * head, y1 + math.sin(ang + 2.4) * head),
            (x1 + math.cos(ang - 2.4) * head, y1 + math.sin(ang - 2.4) * head)], A(col, a))

# ---------------- snake ----------------
def tube(d, pts, ws, col, dk, a=1.0, band=None, hl=True):
    for (x, y), w in zip(pts, ws): d.circ(x, y + w * 0.16, w, fill=A(dk, a))
    for i, ((x, y), w) in enumerate(zip(pts, ws)):
        c = band(i) if band else None
        d.circ(x, y, w * 0.86, fill=A(c or col, a))
    if hl:
        for i, ((x, y), w) in enumerate(zip(pts, ws)):
            if i % 2 == 0: d.circ(x - w * 0.15, y - w * 0.45, w * 0.2, fill=A(WHITE, 0.32 * a))

def shead(d, x, y, s, mood, t, look=0.6, dir=1, a=1.0, tongue=0.0, col=SN, dk=SN_D):
    if tongue > 0:
        tx = x + dir * s * 0.9; ty = y + s * 0.28; L = s * 0.75 * tongue
        d.line([(tx, ty), (tx + dir * L, ty + s * 0.05)], A((240, 70, 90), a), s * 0.07)
        for k in (-1, 1): d.line([(tx + dir * L, ty + s * 0.05), (tx + dir * (L + s * 0.18), ty + s * 0.05 + k * s * 0.12)], A((240, 70, 90), a), s * 0.06)
    d.ell(x, y + s * 0.07, s, s * 0.74, A(dk, a)); d.ell(x - dir * s * 0.02, y, s * 0.97, s * 0.7, A(col, a))
    d.ell(x + dir * s * 0.35, y + s * 0.3, s * 0.5, s * 0.28, A(mix(col, WHITE, 0.35), a))
    d.ell(x - dir * s * 0.25, y - s * 0.45, s * 0.35, s * 0.12, A(WHITE, 0.4 * a))
    face(d, x + dir * s * 0.14, y - s * 0.05, s * 0.78, mood, a, look * dir)

def wsnake(d, x, y, R, ang, t, mood="happy", lift=0.0, a=1.0, look=0.6, glowb=0.0, glowh=0.0, head=True, spin=0.0, tongue=0.0, shadow=True,
           bodycol=SN, hilite=0.0, wob=0.0):
    w = R * 0.3
    if shadow: d.ell(x, y + R + w * 0.95, R * 0.9, w * 0.35, A((0, 0, 0), 0.22 * a))
    if glowb > 0: glow(d, x, y, R * 1.7, HOT, glowb, 9)
    n = max(28, min(96, int(2 * math.pi * R / (w * 0.32))))
    pts = [(x + R * math.cos(2 * math.pi * i / n), y + R * math.sin(2 * math.pi * i / n)) for i in range(n)]
    def band(i):
        fr = ((2 * math.pi * i / n + ang) / (2 * math.pi)) % 1
        return SN_B if (fr * 7) % 1 < 0.2 else None
    tube(d, pts, [w] * n, bodycol, mix(bodycol, (0, 0, 0), 0.32), a, band, hl=False)
    d.arc(x, y, R, R, 195, 255, A(WHITE, 0.35 * a), w * 0.25)
    if spin > 0:
        dg = -math.degrees(ang)
        for k in range(3):
            d.arc(x, y, R * 0.58, R * 0.58, dg + k * 120, dg + k * 120 + 70, A(WHITE, 0.55 * spin * a), max(4, R * 0.05))
            d.arc(x, y, R * 1.45, R * 1.45, dg + k * 120 + 40, dg + k * 120 + 95, A(WHITE, 0.4 * spin * a), max(4, R * 0.045))
    if not head: return None
    if hilite > 0:   # the "stroke" segment next to the head (front of the ring)
        seg = [(x + R * math.cos(th), y + R * math.sin(th)) for th in [-0.6 + 1.5 * i / 14 for i in range(15)]]
        tube(d, seg, [w * 1.05] * 15, mix(bodycol, (255, 120, 80), hilite), mix(bodycol, (180, 60, 40), hilite), a, hl=False)
    bx, by = x + R * math.cos(-0.75), y + R * math.sin(-0.75)
    hx, hy = x + R * 1.02, y - R * 0.98 - lift * R + wob
    npts = []
    for i in range(14):
        u = i / 13; cx_, cy_ = x + R * 1.2, by - R * 0.15
        px = (1 - u) ** 2 * bx + 2 * u * (1 - u) * cx_ + u * u * (hx - R * 0.28); py = (1 - u) ** 2 * by + 2 * u * (1 - u) * cy_ + u * u * (hy + R * 0.08)
        npts.append((px, py))
    tube(d, npts, [w * (0.95 - 0.12 * i / 13) for i in range(14)], bodycol, mix(bodycol, (0, 0, 0), 0.32), a, lambda i: SN_B if i == 6 else None)
    if glowh > 0: glow(d, hx, hy, R * 1.0, CYAN, glowh, 8)
    shead(d, hx, hy, R * 0.42, mood, t, look, 1, a, tongue)
    return hx, hy

def csnake(d, x, y, s, t, mood="chill", dir=1, spd=6, a=1.0, look=0.5, L=3.4, amp=0.3, tongue=0.0):
    n = 46; pts = []; ws = []
    for i in range(n):
        u = i / (n - 1)
        pts.append((x - dir * (s * 0.3 + u * L * s), y + math.sin(u * 2 * math.pi * 1.2 - t * spd) * s * amp * min(1, u * 3)))
        ws.append(s * 0.24 * (1 - 0.8 * u ** 1.6))
    pts.reverse(); ws.reverse()
    tube(d, pts, ws, SN, SN_D, a, lambda i: SN_B if i % 6 == 0 and i < n - 6 else None)
    shead(d, x + dir * s * 0.08, y - s * 0.03, s * 0.42, mood, t, look, dir, a, tongue)

def bird(d, x, y, s, flap, a=1.0, col=BIRD):
    wy = -s * 1.1 * flap
    d.poly([(x - s * 0.2, y - s * 0.1), (x - s * 1.6, y + wy * 0.9 - s * 0.2), (x - s * 0.9, y + s * 0.15)], A(mix(col, WHITE, 0.1), a * 0.8))
    d.poly([(x - s * 0.8, y), (x - s * 1.5, y - s * 0.3), (x - s * 1.5, y + s * 0.3)], A(col, a))
    d.ell(x, y, s * 0.95, s * 0.38, A(col, a))
    d.poly([(x + s * 0.1, y - s * 0.1), (x - s * 0.5, y + wy - s * 0.3), (x - s * 1.1, y + wy * 0.7), (x - s * 0.4, y + s * 0.1)], A(mix(col, WHITE, 0.18), a))
    hx, hy = x + s * 0.85, y - s * 0.2
    d.circ(hx, hy, s * 0.33, fill=A(col, a))
    d.poly([(hx + s * 0.25, hy - s * 0.1), (hx + s * 0.7, hy + s * 0.08), (hx + s * 0.25, hy + s * 0.15)], A(GOLD, a))
    d.circ(hx + s * 0.08, hy - s * 0.06, s * 0.1, fill=A(WHITE, a)); d.circ(hx + s * 0.11, hy - s * 0.05, s * 0.05, fill=A(INK, a))
    d.line([(hx - s * 0.08, hy - s * 0.2), (hx + s * 0.2, hy - s * 0.12)], A(INK, a), s * 0.05)
    for k in (-1, 1): d.line([(x + s * 0.2 + k * s * 0.15, y + s * 0.3), (x + s * 0.3 + k * s * 0.15, y + s * 0.62)], A(GOLD, a), s * 0.07)

def gauge(d, x, y, r, k, label, col=RED, a=1.0):
    d.circ(x, y, r, fill=A((250, 248, 240), a))
    d.arc(x, y, r * 0.8, r * 0.8, 150, 270, A(GOOD, a), r * 0.12); d.arc(x, y, r * 0.8, r * 0.8, 270, 345, A(YEL, a), r * 0.12); d.arc(x, y, r * 0.8, r * 0.8, 345, 390, A(BAD, a), r * 0.12)
    ang = math.radians(150 + 240 * cl(k))
    d.line([(x, y), (x + math.cos(ang) * r * 0.78, y + math.sin(ang) * r * 0.78)], A(col, a), r * 0.07)
    d.circ(x, y, r * 0.11, fill=A(NAVYT, a))
    d.text(x, y + r * 0.5, label, int(r * 0.3), A(NAVYT, a), k=1)

def tire(d, x, y, r, ang, a=1.0):
    d.circ(x, y, r, fill=A(TIRE, a))
    for i in range(16):
        th = ang + i * 2 * math.pi / 16; d.circ(x + math.cos(th) * r * 0.92, y + math.sin(th) * r * 0.92, r * 0.07, fill=A((96, 100, 116), a))
    d.circ(x, y, r * 0.62, fill=A((200, 206, 218), a)); d.circ(x, y, r * 0.52, fill=A((160, 168, 184), a))
    for i in range(5):
        th = ang + i * 2 * math.pi / 5; d.line([(x, y), (x + math.cos(th) * r * 0.52, y + math.sin(th) * r * 0.52)], A((220, 226, 236), a), r * 0.09)
    d.circ(x, y, r * 0.14, fill=A((240, 200, 80), a))
    d.arc(x, y, r * 0.95, r * 0.95, 200, 250, A(WHITE, 0.3 * a), r * 0.06)

def blob(d, x, y, s, t, spin, mood, a=1.0):
    for k in (0, 1):
        th = spin + k * math.pi
        ex, ey = x + math.cos(th) * s * 1.35, y + math.sin(th) * s * 0.5
        d.line([(x, y), (ex, ey)], A(PINK_D, a), s * 0.2); d.circ(ex, ey, s * 0.16, fill=A(PINK, a))
    d.circ(x, y + s * 0.06, s, fill=A(PINK_D, a)); d.circ(x, y, s * 0.97, fill=A(PINK, a))
    d.ell(x - s * 0.35, y - s * 0.5, s * 0.3, s * 0.13, A(WHITE, 0.45 * a))
    fx_ = x + math.sin(spin) * s * 0.25
    face(d, fx_, y, s * 0.85, mood, a)
    for k in range(3):
        d.arc(x, y, s * 1.5, s * 0.75, math.degrees(spin) + k * 120, math.degrees(spin) + k * 120 + 60, A(WHITE, 0.6 * a), 7)

def gyro(d, x, y, r, t, a=1.0, col=CYAN):
    glow(d, x, y, r * 1.5, col, 0.35 * a)
    d.circ(x, y, r, outline=A(col, a), w=8)
    d.ell(x, y, r * abs(math.cos(t * 7)) + 3, r, outline=A(WHITE, a), w=6)
    d.ell(x, y, r, r * abs(math.sin(t * 5)) + 3, outline=A(mix(col, WHITE, 0.5), a), w=6)
    d.circ(x, y, r * 0.22, fill=A(GOLD, a))

def ghosts(d, x, y, R, ang, t, dx=-90, n=4, a=0.22):
    for k in range(n, 0, -1): wsnake(d, x + dx * k, y, R, ang + k * 0.4, t, a=a * (1 - k / (n + 1)), head=False, shadow=False)

def swirl(d, t, c1, c2, cx=540, cy=900):
    grad(d, c1, c2)
    for i in range(9):
        r = ((t * 120 + i * 140) % 1300)
        d.circ(cx, cy, r, outline=A(mix(c1, WHITE, 0.25), 0.18 * (1 - r / 1300)), w=40)

# ---------------- scenes ----------------
def hook_motion(t):
    sp = 16.0
    if t < BRAKE: return -(t - CURL) * sp, 1.0
    u = t - BRAKE; T = 0.35
    if u < T: return -(BRAKE - CURL) * sp - sp * (u - u * u / (2 * T)), 1 - u / T
    return -(BRAKE - CURL) * sp - sp * T / 2, 0.0
def s_hook(t, d):
    if t < HOOK_HIT:
        grad(d, (70, 160, 100), (24, 90, 64))
        gscroll(d, 1100, t * 300, (120, 90, 60), (90, 170, 80))
        sk = ease(pr(t, -0.3, HOOK_HIT))
        d.ell(560 - 60 * sk, 1110, 200 + 200 * sk, 34 + 20 * sk, A((0, 0, 0), 0.25 + 0.2 * sk))
        bird(d, lerp(430, 470, sk), lerp(330, 640, sk), 130 + 50 * sk, 0.5 + 0.5 * math.sin(t * 30))
        csnake(d, 660 + 30 * t, 1055, 100, t, "scream", 1, 18, look=-0.8)
        stamp(d, t, -0.2, "!", 760, 760, 200, YEL)
        stamp(d, t, -0.25, "危险！", 540, 350, 130, YEL)
        return
    ang, v = hook_motion(t)
    rays(d, t, (255, 196, 70), (240, 140, 40), n=20, cx=560, cy=900)
    off = 300 * HOOK_HIT + 2600 * (t - HOOK_HIT) if t < BRAKE else 300 * HOOK_HIT + 2600 * (BRAKE - HOOK_HIT) + 2600 * (-hook_motion(t)[0] + hook_motion(BRAKE)[0]) / 16
    gscroll(d, 1100, off, (120, 90, 60), (90, 170, 80))
    if v > 0.05: speedlines(d, t, 0.45 * v, WHITE, 320, 1050)
    bu = t - HOOK_HIT
    bird(d, 470 - 900 * bu, 640 - 500 * bu, 180, 0.5 + 0.5 * math.sin(t * 30), a=1 - pr(t, HOOK_HIT, HOOK_HIT + 0.8))
    R = 115; x = lerp(520, 600, ease(pr(t, HOOK_HIT, HOOK_HIT + 0.4))); y = 1100 - R - R * 0.3
    if v > 0.05: ghosts(d, x, y, R, ang, t, -95 * v, 4, 0.35 * v)
    if t > BRAKE:
        for k in range(6):
            u = t - BRAKE - k * 0.04
            if 0 < u < 0.7: d.circ(x - 40 - k * 30 - u * 120, y + R * 1.2 - u * 160, 26 + u * 70, fill=A(WHITE, 0.5 * (1 - u / 0.7)))
        d.rect(x - 260 * pr(t, BRAKE, BRAKE + 0.35), 1102, x, 1112, fill=A((60, 40, 30), 0.6))
    mood = "scared" if t < HOOK_HIT + 0.5 else ("happy" if t < BRAKE + 0.3 else "proud")
    wsnake(d, x, y, R, ang, t, mood, a=1, spin=v * 0.9, tongue=0.0 if t < BRAKE + 0.4 else 0.6 + 0.4 * math.sin(t * 20))
    sparks(d, x, y, t, HOOK_HIT, n=40, spd=900, col=(255, 250, 200), seed=4)
    bang(d, t, HOOK_HIT, 300, 900, "嗖！", 120, WHITE)
    bang(d, t, BRAKE, 720, 650, "吱——", 90, WHITE, 0.8)
    stamp(d, t, HOOK_HIT, "蛇会滚着跑！", 540, 350, 112, WHITE)

def lane(d, y0, y1, col, lab, a=1.0):
    d.rect(195, y0, 885, y1, fill=A(col, a), r=36)
    tag(d, 300, y0 + 50, lab, WHITE, a, 38)
def s_cmp(t, d):
    grad(d, (40, 150, 170), (16, 70, 100))
    lane(d, 400, 770, (236, 196, 130), "平时爬")
    lane(d, 800, 1170, (140, 200, 250), "滚起来")
    d.rect(195, 700, 885, 770, fill=A((200, 150, 90), 1), r=0); d.rect(195, 1100, 885, 1170, fill=A((90, 150, 210), 1))
    cx = 300 + (t - CMP) * 45
    csnake(d, cx, 640, 62, t, "sad", 1, 5, look=0.5)
    k = ease(pr(t, GAUGE, GAUGE + 0.5))
    gauge(d, 790, 560, 75, 0.18 * k + 0.02 * math.sin(t * 9) * k, "x1", BAD)
    u = ((t - CMP) * 1.25) % 1; R = 55; wx = lerp(180, 900, u)
    if 0.05 < u < 0.97:
        ghosts(d, wx, 1100 - R * 1.3, R, -t * 22, t, -45, 4, 0.35)
        wsnake(d, wx, 1100 - R * 1.3, R, -t * 22, t, "happy", spin=0.8)
    speedlines(d, t, 0.35, WHITE, 840, 1080, 3000, 8)
    gauge(d, 790, 960, 75, (0.18 + 0.62 * ease(pr(t, X4 - 0.5, X4))) * k + 0.03 * math.sin(t * 31) * k, "x4" if t > X4 else "", GOOD)
    if t > X4: rings(d, 790, 960, t, [X4], YEL, 0.8, 200)
    tag(d, 540, 310, "比一比谁快", WHITE, popk(t, CMP + 0.15) * (1 - pr(t, X4 - 0.1, X4)), 60)
    stamp(d, t, X4, "快 4 倍！", 540, 310, 130, YEL)

def radar(d, x, y, s, t, a=1.0):
    d.rect(x - s * 0.9, y - s * 0.35, x + s * 0.6, y + s * 0.3, fill=A((90, 104, 130), a), r=s * 0.2)
    d.rect(x + s * 0.5, y - s * 0.25, x + s * 1.0, y + s * 0.2, fill=A((120, 134, 160), a), r=s * 0.1)
    d.rect(x - s * 0.5, y + s * 0.2, x - s * 0.15, y + s * 1.0, fill=A((70, 80, 104), a), r=s * 0.1)
    d.rect(x - s * 0.15, y + s * 0.3, x, y + s * 0.55, fill=A(RED, a), r=s * 0.05)
    d.rect(x - s * 0.75, y - s * 0.22, x + s * 0.2, y + s * 0.12, fill=A((40, 70, 60), a), r=s * 0.06)
    d.ell(x - s * 0.5, y - s * 0.25, s * 0.25, s * 0.06, A(WHITE, 0.35 * a))
def s_num(t, d):
    grad(d, (30, 50, 110), (12, 20, 60))
    for i in range(7): d.rect(0, 300 + i * 120, 1080, 302 + i * 120, fill=A(WHITE, 0.04))
    gscroll(d, 1150, (t - NUM) * 900, (60, 66, 90), (240, 220, 120))
    # passing wheel (two passes)
    for p0, p1, R in ((NUM + 0.1, BEEP1 + 0.35, 70), (COUNT[0] + 0.2, BEEP2 + 0.3, 70)):
        u = pr(t, p0, p1)
        if 0 < u < 1:
            wx = lerp(120, 980, u); wy = 1150 - R * 1.3
            ghosts(d, wx, wy, R, -t * 20, t, -60, 3, 0.3); wsnake(d, wx, wy, R, -t * 20, t, "happy", spin=0.8)
    radar(d, 300, 880, 120, t)
    for h in (BEEP1, BEEP2):
        u = (t - h + 0.25) / 0.6
        if 0 < u < 1:
            for j in range(3): d.arc(430, 870, 60 + (u + j * 0.2) * 300, 60 + (u + j * 0.2) * 300, -25, 25, A(CYAN, (1 - u) * 0.8), 8)
    # LCD
    if t < BEEP1: val = 0.0
    elif t < COUNT[0]: val = 1.72
    else: val = lerp(1.72, 3.69, eio(pr(t, COUNT[0], COUNT[1])))
    hot = t >= BEEP2
    d.rect(220, 420, 860, 700, fill=A((20, 30, 26), 1), r=34); d.rect(240, 440, 840, 680, fill=A((30, 60, 44), 1), r=24)
    sc = 1 + 0.15 * pulse(t, [BEEP1, BEEP2], 7)
    col = (255, 110, 90) if hot else (120, 255, 150)
    if hot: glow(d, 540, 540, 330, (255, 90, 70), 0.35)
    d.text(540, 545, f"{val:.2f}", int(170 * sc), A(col, 1), k=1)
    d.text(540, 650, "米 / 秒", 34, A(col, 0.85), k=1)
    tag(d, 540, 330, "测速枪", WHITE, popk(t, NUM + 0.15) * (1 - pr(t, NUM_TAG - 0.1, NUM_TAG)), 60)
    stamp(d, t, NUM_TAG, "最快 3.69！", 540, 330, 120, (255, 120, 100))
    if t > BEEP2: tag(d, 650, 790, "约 4 倍爬行速度", YEL, popk(t, BEEP2 + 0.3), 38)

def s_diz(t, d):
    swirl(d, t, (120, 70, 200), (60, 30, 120), 540, 760)
    k = ease(pr(t, SPIN - 0.3, SPIN + 0.2))
    tx, ty, tr = lerp(540, 330, k), lerp(760, 640, k), lerp(170, 105, k)
    ang = (t - DIZ) * 4
    # bracket + box (does not rotate)
    d.rect(tx - tr * 0.08, ty - tr * 1.55, tx + tr * 0.08, ty, fill=A((220, 224, 236), 1), r=6)
    tire(d, tx, ty, tr, ang)
    d.rect(tx - tr * 0.75, ty - tr * 2.15, tx + tr * 0.75, ty - tr * 1.5, fill=A(GOLD, 1), r=tr * 0.15)
    face(d, tx, ty - tr * 1.83, tr * 0.32, "chill", 1)
    if t > AXLE_TAG:
        a2 = popk(t, AXLE_TAG)
        tag(d, tx + tr * 1.25, ty - tr * 1.83, "不转", WHITE, a2, int(lerp(40, 32, k)))
        tag(d, tx + tr * 1.25, ty, "轴", CYAN, a2, int(lerp(40, 32, k)))
    if k > 0:
        sp = (t - SPIN) * 14 if t > SPIN else 0
        blob(d, 690, 840, 130 * k, t, sp, "dizzy" if t > STARS[0] else "scared")
        for i, h in enumerate(STARS):
            if t > h:
                th = t * 5 + i * 2.1
                star(d, 690 + math.cos(th) * 150, 640 + math.sin(th) * 40, 30 * popk(t, h), YEL, 1, t * 3)
        if t > SPIN: tag(d, 690, 1060, "全身一起转", WHITE, popk(t, SPIN + 0.2), 40)
    tag(d, 540, 330, "轮子靠轴", WHITE, popk(t, AXLE_TAG) * (1 - pr(t, DIZ_TAG - 0.1, DIZ_TAG)), 64)
    stamp(d, t, DIZ_TAG, "会晕！", 540, 330, 140, YEL)

def s_q(t, d):
    grad(d, (24, 40, 90), (8, 14, 40))
    for i in range(6): d.circ(540, 720, 200 + i * 150 + (t * 60) % 150, outline=A(CYAN, 0.08), w=6)
    # blurred spinning body behind
    wsnake(d, 520, 1060, 220, -t * 9, t, a=0.35, head=False, spin=0.8, shadow=False)
    k = back(pr(t, HEADZ, HEADZ + 0.3)); s = 230 * (0.5 + 0.5 * k)
    look = math.sin((t - Q) * 3) * 0.9
    shead(d, 540, 720, s, "sus" if t < QMARK else "scared", t, look, 1, 1, 0.5 + 0.5 * math.sin(t * 14) if t < QMARK else 0)
    if t > QMARK:
        kq = popk(t, QMARK); wob = math.sin(t * 5) * 6
        glow(d, 540, 340, 200, (255, 220, 120), 0.4 * kq)
        d.text(540 + wob, 340, "?", int(240 * kq), A(YEL, 1), k=1)
    tag(d, 540, 340, "头怎么办？", WHITE, popk(t, HEADZ + 0.2) * (1 - pr(t, QMARK - 0.1, QMARK)), 60)
    if t >= SIL0: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.55))

def s_reveal(t, d):
    rays(d, t, (255, 210, 80), (245, 150, 40), n=22, cx=500, cy=820)
    R = 215; x, y = 490, 860; ang = -(t - BIG) * 7
    ghosts(d, x, y, R, ang, t, -25, 2, 0.25)
    hx, hy = wsnake(d, x, y, R, ang, t, "proud", a=1, spin=1.0, glowh=0.5 + 0.3 * pulse(t, [BIG], 2), look=0.8)
    if t > LEVEL:
        k = ease(pr(t, LEVEL, LEVEL + 0.4)); dashed(d, 190, lerp(190, 890, k), hy, CYAN, 1, 8)
        tag(d, 280, hy - 70, "水平", CYAN, popk(t, LEVEL + 0.2), 34)
    sparks(d, hx, hy, t, BIG, n=60, spd=1200, col=(255, 250, 200), seed=5, life=1.3)
    tag(d, 300, 500, "慢动作", (40, 30, 60), popk(t, BIG + 0.3), 32, WHITE)
    bk = ease(pr(t, BIG, BIG + 0.15))
    if bk > 0: d.rect(540 - 350 * bk, 268, 540 + 350 * bk, 422, fill=A((150, 36, 30), 0.92), r=40)
    stamp(d, t, BIG, "头一动不动！", 540, 345, 104, WHITE)

def s_gyro(t, d):
    grad(d, (20, 80, 100), (8, 30, 50))
    for i in range(14): d.rect(i * 80, 0, i * 80 + 2, 1920, fill=A(CYAN, 0.05))
    for i in range(26): d.rect(0, i * 80, 1080, i * 80 + 2, fill=A(CYAN, 0.05))
    gscroll(d, 1120, (t - GYRO) * 700, (40, 60, 70), (90, 200, 180))
    R = 160; x, y = 520, 1120 - R * 1.3; ang = -(t - GYRO) * 7
    # traces: head = straight line, a body point = wave
    hx0, hy0 = x + R * 1.02, y - R * 0.98
    k = ease(pr(t, GYRO + 0.2, GYRO + 0.8))
    d.line([(lerp(hx0, 190, k), hy0), (hx0 - 60, hy0)], A(CYAN, 0.9), 8)
    def mk(tau): return 1.0 + (tau - GYRO) * 7
    pts = [(x + R * math.cos(mk(t - j * 0.012)) - j * 20, y + R * math.sin(mk(t - j * 0.012))) for j in range(int(56 * k) + 2) if x - j * 20 + R > 150]
    if k > 0: d.line(pts, A(HOT, 0.85), 7)
    hx, hy = wsnake(d, x, y, R, ang, t, "chill", spin=0.7, look=0.8, glowh=0.3)
    d.circ(x + R * math.cos(mk(t)), y + R * math.sin(mk(t)), 18, fill=A(HOT, 1))
    gk = popk(t, GYRO_HIT)
    if gk > 0: gyro(d, hx, hy - 170, 60 * gk, t)
    if t > HTAG:
        tag(d, 330, hy0 - 60, "头：直线", CYAN, popk(t, HTAG), 36)
        tag(d, 300, 820, "身体：一直转", HOT, popk(t, HTAG + 0.3), 36)
    tag(d, 540, 330, "像陀螺仪一样稳", WHITE, popk(t, GYRO_HIT), 60)

def s_fast(t, d):
    grad(d, (250, 150, 60), (200, 70, 40))
    sp = eio(pr(t, SPEEDUP[0], SPEEDUP[1]))
    gscroll(d, 1130, (t - FAST) * (900 + 1800 * sp), (150, 70, 40), (255, 200, 90))
    speedlines(d, t, 0.2 + 0.4 * sp, WHITE, 650, 1080, 2000 + 2500 * sp, 12)
    gauge(d, 330, 490, 115, 0.3 + 0.6 * sp + 0.02 * math.sin(t * 40), "速度", RED)
    # wobble graph
    d.rect(560, 400, 890, 590, fill=A((40, 20, 30), 0.75), r=24)
    d.text(725, 435, "上下晃动", 30, A(WHITE, 0.9), k=1)
    amp = 50 * (1 - 0.85 * sp)
    d.line([(580 + i * 5, 525 + amp * math.sin(i * 0.35 - t * 12)) for i in range(59)], A(YEL, 1), 7)
    R = 140; x, y = 470, 1130 - R * 1.3; ang = -(t - FAST) * (6 + 10 * sp)
    lift = 0.45 * sp; wob = math.sin(t * 18) * 26 * (1 - 0.9 * sp)
    ghosts(d, x, y, R, ang, t, -30 - 25 * sp, 3, 0.15 + 0.2 * sp)
    hx, hy = wsnake(d, x, y, R, ang, t, "happy" if sp > 0.5 else "chill", lift=lift, spin=0.5 + 0.5 * sp, wob=wob, look=0.8)
    if t > LIFT_TAG:
        arrow(d, [(hx + 110, hy + 120), (hx + 110, hy - 10)], WHITE, popk(t, LIFT_TAG), 12, 36)
        tag(d, 760, hy + 170, "头抬高", WHITE, popk(t, LIFT_TAG), 40)
    if t > FLAT_TAG: tag(d, 725, 650, "晃动变小", YEL, popk(t, FLAT_TAG), 40)
    tag(d, 540, 290, "越快越稳", WHITE, popk(t, FAST + 0.15), 60)

def s_stroke(t, d):
    grad(d, (250, 230, 240), (220, 190, 230))
    for i in range(10): d.circ(540, 820, 120 + i * 110, outline=A((180, 140, 210), 0.12), w=4)
    d.rect(-50, 1060, 1130, 1080, fill=A((160, 120, 190), 1))
    R = 165; x, y = 460, 1060 - R * 1.3
    ci = -1
    for i, h in enumerate(STROKES):
        if t >= h - 0.05: ci = i
    ang = -(t - STROKE) * 3.5
    hp = pulse(t, STROKES, 3.5)
    hx, hy = wsnake(d, x, y, R, ang, t, "proud" if ci >= 0 else "chill", look=0.8, hilite=hp, spin=0.3)
    if ci >= 0:
        h = STROKES[ci]; u = pr(t, h, h + 0.35)
        ax = x + R + 95
        arrow(d, [(ax, y - R * 0.55), (ax, lerp(y - R * 0.3, y + R * 0.5, ease(u)))], (240, 90, 60), min(1, 2 * hp + 0.3), 16, 40)
        tag(d, 800, y - R * 0.7, "划一下", (240, 90, 60), popk(t, h) * (0.5 + 0.5 * hp), 40, WHITE)
        side = ci % 2
        for j, (lab, x0) in enumerate((("左侧着地", 330), ("右侧着地", 750))):
            on = j == side
            d.rect(x0 - 150, 1120, x0 + 150, 1195, fill=A(GOLD if on else (190, 170, 210), 1), r=30)
            d.text(x0, 1157, lab, 38, A(NAVYT if on else (120, 100, 140), 1), k=1)
        d.text(540, 1157, "<>", 40, A((120, 90, 160), 0.8), k=1)
        cx_ = x + (-1 if side == 0 else 1) * R * 0.35
        d.ell(cx_, 1062, 70, 16, A(GOLD, 0.9))
    tag(d, 540, 300, "秘诀：左右换边", (120, 60, 170), popk(t, STROKE + 0.15), 60, WHITE)

def s_track(t, d):
    grad(d, (40, 110, 60), (14, 50, 30))
    for i in range(7):
        bx = 120 + i * 150; d.ell(bx, 760, 90, 160, A((30, 90, 50), 0.6))
    d.rect(-50, 800, 1130, 1220, fill=A((200, 70, 50), 1))
    for i in range(14): d.circ((i * 97) % 1080, 1150 + (i % 3) * 25, 14, fill=A((255, 140, 80), 0.5))
    tag(d, 800, 1160, "出界", (150, 40, 30), 1, 32, WHITE)
    sh = 120
    T0, T1 = 900, 1060
    d.poly([(180 + sh, T0), (960, T0), (960 - sh, T1), (180, T1)], A((236, 220, 180), 1))
    d.line([(180 + sh, T0), (960, T0)], A(WHITE, 1), 8); d.line([(180, T1), (960 - sh, T1)], A(WHITE, 1), 8)
    # ruler (track width)
    if t > RULER:
        k = ease(pr(t, RULER, RULER + 0.3))
        d.line([(205 + sh, T0), (205 + sh - sh * k, lerp(T0, T1, k))], A(YEL, 1), 10)
        for j in range(5): d.line([(205 + sh - sh * j / 4 - 14, lerp(T0, T1, j / 4)), (205 + sh - sh * j / 4 + 14, lerp(T0, T1, j / 4))], A(YEL, k), 5)
        tag(d, 330, 820, "20 厘米", YEL, popk(t, RULER + 0.1), 44)
    u = ((t - TRACK) * 0.55) % 1; R = 70
    wx = lerp(200, 900, u); base = lerp(T0, T1, 0.5 + 0.28 * math.sin(u * 13))
    wsnake(d, wx, base - R * 1.3, R, -t * 16, t, "happy", spin=0.7)
    if t > IN_TAG:
        k = popk(t, IN_TAG); d.circ(780, 520, 80 * k, fill=A(GOOD, 1))
        d.line([(735, 520), (770, 560), (830, 480)], A(WHITE, k), 18)
    tag(d, 540, 330, "窄跑道挑战", WHITE, popk(t, TRACK + 0.15) * (1 - pr(t, IN_TAG - 0.1, IN_TAG)), 60)
    stamp(d, t, IN_TAG, "不出界！", 540, 330, 120, WHITE)

def s_split(t, d):
    grad(d, (20, 40, 80), (10, 90, 110))
    R = 200; x, y = 450, 860; ang = -(t - SPLIT) * 5
    gb = 0.5 * ease(pr(t, TAG_ROT, TAG_ROT + 0.3)); gh = 0.6 * ease(pr(t, TAG_STB, TAG_STB + 0.3))
    hx, hy = wsnake(d, x, y, R, ang, t, "proud", glowb=gb, glowh=gh, spin=0.6, look=0.8)
    if t > DIVIDE:
        k = ease(pr(t, DIVIDE, DIVIDE + 0.4)); bx, by = x + R * 1.1, y - R * 0.6
        dashed(d, bx - 120 * k, bx + 120 * k, by, WHITE, 1, 8, 20)
    tag(d, x, y, "负责转", HOT, popk(t, TAG_ROT), 48)
    tag(d, 700, hy - 140, "负责稳", CYAN, popk(t, TAG_STB), 48)
    tag(d, 540, 300, "分区工作", WHITE, popk(t, SPLIT + 0.15), 64)

def s_concl(t, d):
    rays(d, t, (120, 220, 170), (40, 160, 130), n=18, cx=540, cy=820)
    ang = -(t - CONCL) * 5
    wsnake(d, 330, 840, 115, ang, t, "happy", spin=0.5, look=0.8)
    tire(d, 760, 860, 120, -ang)
    if t > EQ: d.text(585, 860, "=", int(120 * popk(t, EQ)), A(WHITE, 1), k=1)
    tag(d, 330, 1080, "蛇", WHITE, popk(t, CONCL + 0.2), 40)
    tag(d, 760, 1080, "轮子", WHITE, popk(t, CONCL + 0.35), 40)
    tag(d, 540, 330, "没有轴，也能滚", WHITE, popk(t, CONCL + 0.15) * (1 - pr(t, CONCL_TAG - 0.1, CONCL_TAG)), 60)
    stamp(d, t, CONCL_TAG, "形状不是极限！", 540, 330, 92, YEL)
    sparks(d, 540, 860, t, CONCL_TAG, n=40, spd=800, col=WHITE, seed=9)
    kc = ease(pr(t, CARD, CARD + 0.25))
    if kc > 0:
        d.rect(0, 0, OW, OH, fill=A((10, 20, 30), 0.45 * kc))
        yo = (1 - back(pr(t, CARD, CARD + 0.3))) * 120
        x0, x1, y0, y1 = 200, 880, 470 + yo, 1150 + yo
        d.rect(x0, y0, x1, y1, fill=A((255, 252, 240), kc), r=40)
        d.rect(x0, y0, x1, y0 + 110, fill=A((40, 150, 130), kc), r=40); d.rect(x0, y0 + 70, x1, y0 + 110, fill=A((40, 150, 130), kc))
        d.text(540, y0 + 56, "一句话学会", 52, A(WHITE, kc), k=1)
        k1 = popk(t, CARD + 0.25); k2 = popk(t, CARD + 0.55); k3 = popk(t, CARD + 0.9)
        glow(d, 300, y0 + 220, 60, HOT, 0.5 * k1); d.circ(300, y0 + 220, 34 * k1, fill=A(HOT, kc))
        d.text(300, y0 + 220, "转", int(36 * k1) + 1, A(WHITE, kc), k=1)
        d.text(370, y0 + 220, "身体负责转", 62, A(NAVYT, kc * min(1, k1)), anchor="lm", k=1)
        glow(d, 300, y0 + 360, 60, CYAN, 0.5 * k2); d.circ(300, y0 + 360, 34 * k2, fill=A((40, 170, 200), kc))
        d.text(300, y0 + 360, "稳", int(36 * k2) + 1, A(WHITE, kc), k=1)
        d.text(370, y0 + 360, "头负责稳", 62, A(NAVYT, kc * min(1, k2)), anchor="lm", k=1)
        d.rect(250, y0 + 445, 830, y0 + 451, fill=A((200, 190, 170), kc * min(1, k3)))
        d.text(540, y0 + 560, "= 分区控制", int(96 * (0.6 + 0.4 * k3)) if k3 > 0 else 1, A((220, 70, 50), kc * min(1, k3)), k=1)

def s_end(t, d):
    rays(d, t, (200, 240, 120), (110, 190, 90), n=16, cx=540, cy=1000)
    d.rect(-50, 1120, 1130, 1970, fill=A((120, 90, 60), 1)); d.rect(-50, 1120, 1130, 1138, fill=A((90, 170, 80), 1))
    k = ease(pr(t, OUTRO, STOPS + 0.3))
    if t < STOPS:
        u = pr(t, OUTRO, STOPS); R = 100
        wsnake(d, lerp(200, 480, ease(u)), 1120 - R * 1.3, R, -t * 10 * (1 - u), t, "happy", spin=0.5 * (1 - u))
    else:
        # upright S-coil with tail tip making an OK ring
        pts = []; ws = []
        for i in range(40):
            u = i / 39; ang_ = u * math.pi * 1.6
            pts.append((480 + math.sin(ang_) * 110 * (1 - u * 0.3), 1080 - u * 320)); ws.append(48 * (0.75 + 0.25 * u))
        tail = []; tw = []
        okk = ease(pr(t, OK, OK + 0.4))
        for i in range(30):
            u = i / 29; th = math.pi + u * 2 * math.pi * okk
            tail.append((760 + 60 * math.cos(th) + (1 - okk) * u * 0, 1000 + 60 * math.sin(th) - u * 0)); tw.append(26 * (1 - 0.5 * u))
        tube(d, [(560 - (1 - j / 10) * 0, 1080) for j in range(1)] + [(480 + 220 * j / 10, 1080 - 80 * j / 10) for j in range(11)], [40] * 12, SN, SN_D, 1)
        tube(d, tail, tw, SN, SN_D, 1, lambda i: SN_B if i % 7 == 3 else None)
        tube(d, pts, ws, SN, SN_D, 1, lambda i: SN_B if i % 6 == 0 else None)
        shead(d, 480 + math.sin(1.6 * math.pi) * 110 * 0.7 + 40, 1080 - 320 - 60, 95, "happy", t, 0.5, 1, 1, 0.5 + 0.5 * math.sin(t * 16))
        if t > OK: d.text(760, 1000, "OK", int(40 * popk(t, OK + 0.2)), A(WHITE, 1), k=1)
        rings(d, 760, 1000, t, [OK], WHITE, 0.6, 160)
    bubble(d, 720, 560, "你会滚吗？", 1, WHITE, NAVYT, popk(t, BUB), 48)
    d.rect(250, 1270, 830, 1372, fill=A(WHITE, 0.6), r=20)
    d.text(540, 1300, "Kojima et al., Curr. Biol. (2026)", 26, A(NAVYT, 0.9))
    d.text(540, 1342, "DOI 10.1016/j.cub.2026.08.057", 26, A(NAVYT, 0.9))
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

SECS = [(-1, CMP, s_hook), (CMP, NUM, s_cmp), (NUM, DIZ, s_num), (DIZ, Q, s_diz), (Q, BIG, s_q), (BIG, GYRO, s_reveal), (GYRO, FAST, s_gyro),
        (FAST, STROKE, s_fast), (STROKE, TRACK, s_stroke), (TRACK, SPLIT, s_track), (SPLIT, CONCL, s_split), (CONCL, OUTRO, s_concl), (OUTRO, 99, s_end)]
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
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.2f}.png")
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
