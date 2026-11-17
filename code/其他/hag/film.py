import math, random, sys, subprocess
from PIL import Image
from base import *
from fx import glow, sparks, shake, stamp, flash, grad, rays, face
from cues import *

HAG = (232, 150, 165); HAG_D = (180, 100, 120); HAG_L = (255, 205, 215)
SLIME = (215, 240, 255); SHARK_C = (110, 140, 175); SHARK_L = (200, 215, 230)
MEAT = (220, 90, 90); GOLD = (255, 190, 60); TRUCKC = (240, 160, 50); CARC = (90, 170, 230)

def shade(c, k=0.35): return mix(c, (0, 0, 0), k)

# ---------- hagfish ----------
def body_path(x0, y0, L, t, amp=28, ang=0.0, knot=None, kr=70, n=80, speed=6.0):
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []; extra = 0.0; done = False
    for i in range(n):
        u = i / (n - 1); s = u * L
        if knot is not None and not done and u >= knot:
            done = True
            px = s + extra; py = amp * math.sin(s / 90 - t * speed) * min(1, s / 80) * 0.4
            for j in range(26):
                a = math.pi / 2 + 2 * math.pi * j / 25
                lx = px + kr * math.cos(a) + (j / 25) * kr * 0.7; ly = py - kr + kr * math.sin(a)
                pts.append((x0 + lx * ca - ly * sa, y0 + lx * sa + ly * ca, u))
            extra = kr * 0.7
        k_amp = 0.4 if knot is not None else 1.0
        lx = s + extra; ly = amp * k_amp * math.sin(s / 90 - t * speed) * min(1, s / 80)
        pts.append((x0 + lx * ca - ly * sa, y0 + lx * sa + ly * ca, u))
    return pts

def hagfish(d, pts, R, t, kind="chill", a=1.0, mouth_open=0.0):
    dense = []
    for (x1, y1, u1), (x2, y2, u2) in zip(pts, pts[1:]):
        seg = math.hypot(x2 - x1, y2 - y1); m = max(1, int(seg / (R * 0.3)))
        for k in range(m): dense.append((lerp(x1, x2, k / m), lerp(y1, y2, k / m), lerp(u1, u2, k / m)))
    dense.append(pts[-1])
    for x, y, u in reversed(dense): d.circ(x + R * 0.08, y + R * 0.12, R * (1 - 0.45 * u), fill=A(HAG_D, a))
    for x, y, u in reversed(dense): d.circ(x, y, R * (1 - 0.45 * u) * 0.94, fill=A(HAG, a))
    for x, y, u in dense[::2]: d.circ(x - R * 0.15, y - R * 0.35 * (1 - 0.45 * u), R * 0.18 * (1 - 0.5 * u), fill=A(HAG_L, 0.6 * a))
    # slime pores along side
    for x, y, u in dense[6::9]: d.circ(x, y + R * 0.45 * (1 - 0.45 * u), R * 0.07, fill=A(HAG_D, 0.8 * a))
    hx, hy, _ = dense[0]; nx, ny, _ = dense[min(4, len(dense) - 1)]
    dx, dy = hx - nx, hy - ny; dl = math.hypot(dx, dy) or 1; dx, dy = dx / dl, dy / dl
    for k in (-1, -0.35, 0.35, 1):  # barbels
        bx, by = hx + dx * R * 0.9 - dy * k * R * 0.5, hy + dy * R * 0.9 + dx * k * R * 0.5
        d.line([(bx, by), (bx + dx * R * 0.55 - dy * k * R * 0.25, by + dy * R * 0.55 + dx * k * R * 0.25)], A(HAG_D, a), R * 0.12)
    d.circ(hx, hy, R * 1.12, fill=A(HAG_D, a)); d.circ(hx - R * 0.05, hy - R * 0.06, R * 1.06, fill=A(HAG, a))
    d.ell(hx - R * 0.35, hy - R * 0.55, R * 0.3, R * 0.15, A(WHITE, 0.45 * a))
    if mouth_open > 0:
        mx, my = hx + dx * R * 0.15, hy + dy * R * 0.15 + R * 0.42
        mr = R * 0.45 * mouth_open
        d.circ(mx, my, mr, fill=A((120, 30, 50), a))
        for k in range(8):
            ang = k * math.pi / 4 + t * 2
            d.circ(mx + math.cos(ang) * mr * 0.7, my + math.sin(ang) * mr * 0.7, mr * 0.14, fill=A((255, 240, 200), a))
        face(d, hx - dx * R * 0.1, hy - R * 0.32, R * 0.85, kind if kind != "chill" else "scared", a, nomouth=True)
    else:
        face(d, hx - dx * R * 0.1, hy, R * 0.95, kind, a)
    return dense

def slime(d, x, y, r, t, a=1.0, seed=0):
    if r < 2 or a <= 0.01: return
    rnd = random.Random(seed)
    glow(d, x, y, r * 1.4, SLIME, a * 0.6, 5)
    for k in range(7):
        ang = rnd.uniform(0, 6.28); rr = r * rnd.uniform(0.3, 0.6)
        d.circ(x + math.cos(ang) * rr + math.sin(t * 3 + k) * r * 0.05, y + math.sin(ang) * rr, r * rnd.uniform(0.45, 0.7), fill=A(SLIME, 0.32 * a))
    for k in range(6):
        ang = rnd.uniform(0, 6.28)
        d.line([(x + math.cos(ang) * r * 0.2, y + math.sin(ang) * r * 0.2), (x + math.cos(ang + 0.5) * r * 0.9, y + math.sin(ang + 0.5) * r * 0.9)], A(WHITE, 0.4 * a), max(2, r * 0.02))
    d.ell(x - r * 0.35, y - r * 0.4, r * 0.25, r * 0.12, A(WHITE, 0.5 * a))

def shark(d, x, y, s, t, kind="chill", bite=0.0, a=1.0, clog=0.0):
    d.poly([(x + 0.9 * s, y), (x + 1.4 * s, y - 0.45 * s), (x + 1.25 * s, y), (x + 1.4 * s, y + 0.4 * s)], A(shade(SHARK_C, 0.15), a))
    d.poly([(x + 0.0 * s, y - 0.35 * s), (x + 0.35 * s, y - 0.8 * s), (x + 0.45 * s, y - 0.3 * s)], A(shade(SHARK_C, 0.15), a))
    d.ell(x + 0.04 * s, y + 0.05 * s, 1.0 * s, 0.4 * s, A(shade(SHARK_C), a)); d.ell(x, y, 1.0 * s, 0.4 * s, A(SHARK_C, a))
    d.ell(x - 0.1 * s, y + 0.18 * s, 0.75 * s, 0.17 * s, A(SHARK_L, a))
    mo = 0.18 * s * bite
    if bite > 0.02:
        d.poly([(x - 1.0 * s, y + 0.05 * s), (x - 0.55 * s, y + 0.05 * s - mo), (x - 0.55 * s, y + 0.05 * s + mo)], A((140, 40, 60), a))
        for k in range(4):
            tx = x - 0.9 * s + k * 0.09 * s
            d.poly([(tx, y + 0.05 * s - mo * (0.25 + k * 0.2)), (tx + 0.04 * s, y + 0.05 * s - mo * (0.25 + k * 0.2)), (tx + 0.02 * s, y + 0.05 * s - mo * (0.1 + k * 0.2))], A(WHITE, a))
    for k in range(4):
        gx = x - 0.32 * s + k * 0.08 * s
        d.line([(gx, y - 0.12 * s), (gx - 0.03 * s, y + 0.12 * s)], A(shade(SHARK_C, 0.3), a), 0.025 * s)
        if clog > 0: slime(d, gx, y, 0.12 * s * clog, t, a * clog, seed=k)
    face(d, x - 0.62 * s, y - 0.15 * s, 0.32 * s, kind, a)

def bubbles(d, t, a=0.25, n=30, col=SLIME):
    for i in range(n):
        rnd = random.Random(i); x = rnd.uniform(0, 1080); y = (rnd.uniform(0, 1920) - t * rnd.uniform(60, 160)) % 1920
        d.circ(x, y, rnd.uniform(4, 10), fill=A(col, a))

def bigtext(d, x, y, s, size, col, a=1.0): d.text(x, y, s, size, A(col, a), k=1)
def pop_text(d, t, t0, s, y, size, col):
    k = back(pr(t, t0, t0 + 0.2))
    if k > 0: bigtext(d, 540, y, s, int(size * (0.6 + 0.4 * k)) + 1, col, min(1, k * 1.5))

# ---------- scenes ----------
def w_hook(t, d):
    grad(d, (14, 40, 70), (4, 10, 22)); bubbles(d, t)
    if t > BURST: rays(d, t, (30, 70, 110), (10, 30, 55), 20, 540, 1150)
    pts = body_path(330, 1250, 520, t, 34)
    hagfish(d, pts, 52, t, "scared" if t > BURST else "chill")
    k = back(pr(t, BURST, BURST + 0.4))
    if k > 0:
        slime(d, 600, 1150, 80 + 360 * k, t, 1.0, 3)
        sparks(d, 600, 1150, t, BURST, 60, 1500, SLIME, 1, 2, 1.0)
def u_hook(t, d):
    if t < BURST: bigtext(d, 540, 400, "0.4 秒", 170, WHITE)
    else:
        pop_text(d, t, BURST, "0.4 秒", 300, 130, WHITE)
        pop_text(d, t, BURST + 0.1, "变大 1 万倍", 480, 170, YEL)
    flash(d, t, [BURST], WHITE, 0.9)

def w_eel(t, d):
    grad(d, (20, 50, 70), (6, 14, 22)); bubbles(d, t)
    # real eel ghost for comparison
    if t < NOJAW:
        a = 0.5 * ease(pr(t, NOTEEL, NOTEEL + 0.3))
        if a > 0:
            ep = body_path(260, 820, 560, t, 30)
            for x, y, u in ep[::2]: d.circ(x, y, 34 * (1 - 0.5 * u), fill=A((120, 160, 90), a))
            d.circ(ep[0][0], ep[0][1], 40, fill=A((120, 160, 90), a))
            k = back(pr(t, NOTEEL, NOTEEL + 0.2))
            d.line([(200, 700), (880, 940)], A(RED, k), 22); d.line([(200, 940), (880, 700)], A(RED, k), 22)
    z = 1 + 0.6 * eio(pr(t, NOJAW - 0.3, NOJAW + 0.3))
    pts = body_path(540 - 230 * z, 1250, 520 * z, t, 30)
    hagfish(d, pts, 52 * z, t, "sus" if t < NOJAW else "scared", mouth_open=ease(pr(t, NOJAW, NOJAW + 0.3)))
def u_eel(t, d):
    if t < NOJAW:
        bigtext(d, 540, 290, "盲鳗", 120, WHITE)
        stamp(d, t, NOTEEL, "≠ 鳗鱼", 540, 470, 150, RED)
    else: stamp(d, t, NOJAW, "没有下巴", 540, 380, 160, YEL)
    flash(d, t, [NOTEEL, NOJAW], WHITE, 0.5)

def w_shark(t, d):
    grad(d, (10, 36, 64), (2, 8, 18)); bubbles(d, t)
    lunge = ease(pr(t, SHARK, BITE))
    spit = ease(pr(t, SPIT, SPIT + 0.6))
    sx = lerp(1300, 760, lunge) + 300 * spit
    bite = 1 - pr(t, BITE - 0.4, BITE) if t < BITE else (0.2 if t < SPIT else 1.0)
    if t < BITE: bite = ease(pr(t, BITE - 0.8, BITE - 0.3))
    clog = ease(pr(t, SLIME_IN, SLIME_IN + 0.8))
    kind = "chill" if t < BITE else ("scared" if t < SLIME_IN + 0.5 else ("dizzy" if t < SPIT else "sad"))
    hx = 360 if t < SPIT else lerp(360, 120, spit)
    hy = 1150 if t < SPIT else 1150 + 80 * spit
    hagfish(d, body_path(hx - 150, hy, 420, t, 30 if t < BITE else 10, speed=10), 46, t, "scared" if t < SPIT else "proud")
    shark(d, sx, 1120, 380, t, kind, bite, clog=clog)
    if t > SLIME_IN:
        k = back(pr(t, SLIME_IN, SLIME_IN + 0.4)) * (1 - spit * 0.6)
        slime(d, sx - 300, 1130, 200 * k, t, 1.0, 5)
        sparks(d, sx - 300, 1130, t, SLIME_IN, 40, 1100, SLIME, 1, 3, 1.0)
def u_shark(t, d):
    if t < SLIME_IN: pop_text(d, t, BITE, "咬！", 380, 200, RED)
    elif t < SPIT: stamp(d, t, SLIME_IN, "鳃被堵住", 540, 380, 150, YEL)
    else: stamp(d, t, SPIT, "吐出来", 540, 380, 170, WHITE)
    flash(d, t, [BITE, SLIME_IN], WHITE, 0.5)

def beaker(d, x, y, w, h, fill, label, col=SLIME):
    d.rect(x - w / 2, y - h, x + w / 2, y, fill=A(WHITE, 0.12), r=20)
    fh = h * fill
    if fh > 4: d.rect(x - w / 2 + 8, y - fh, x + w / 2 - 8, y - 8, fill=A(col, 0.75), r=16)
    for k in range(1, 5): d.line([(x - w / 2, y - h * k / 5), (x - w / 2 + 30, y - h * k / 5)], A(WHITE, 0.4), 4)
    d.text(x, y + 50, label, 46, A(WHITE, 1), k=1)
def w_vol(t, d):
    grad(d, (20, 44, 60), (6, 12, 18)); bubbles(d, t, 0.15)
    f = eio(pr(t, FILL[0], FILL[1]))
    beaker(d, 700, 1450, 300, 700, f, "黏液 0.9 升")
    beaker(d, 300, 1450, 160, 100, 1.0, "盲鳗 0.14 升", HAG)
    hagfish(d, body_path(150, 1180, 300, t, 16), 34, t, "scared" if t > PINCH else "chill")
    if PINCH <= t < PINCH + 0.5:
        k = 1 - pr(t, PINCH, PINCH + 0.5)
        d.circ(440, 1150, 40, fill=A(SKIN := (255, 205, 160), k)); d.circ(440, 1215, 40, fill=A(SKIN, k))
    if FILL[0] < t < FILL[1]:
        for k in range(4): slime(d, lerp(450, 700, (t * 2 + k / 4) % 1), 1150 + 30 * math.sin(t * 9 + k), 30, t, 0.8, k)
def u_vol(t, d):
    if t < SEVEN: bigtext(d, 540, 300, "捏一下尾巴", 110, WHITE)
    else: pop_text(d, t, SEVEN, "自己体积的 7 倍", 330, 130, YEL)
    flash(d, t, [SEVEN], WHITE, 0.5)

def w_knot(t, d):
    grad(d, (24, 30, 64), (6, 8, 20)); bubbles(d, t, 0.2)
    if t > CLEAN: rays(d, t, (50, 60, 120), (20, 24, 60), 18, 540, 1150)
    s = eio(pr(t, SLIDE[0], SLIDE[1]))
    knot = None if t < KNOT else lerp(0.08, 0.98, s)
    L = 620
    pts = body_path(200, 1200, L, t, 26 if t < KNOT else 8, knot=knot, kr=80, speed=4)
    kind = "scared" if t < KNOT else ("sus" if t < CLEAN else "proud")
    stuck = t < KNOT
    # slime coating: on body behind knot only
    hagfish(d, pts, 50, t, kind)
    kx = 200 + (knot or 0) * L
    for i in range(14):
        u = i / 13; x = 200 + u * L + 60
        if knot is None or x > kx + 120:
            slime(d, x, 1200 + 20 * math.sin(i), 70, t, 0.9 if t < CLEAN else 0, i)
    if knot is not None and t < CLEAN:
        sparks(d, kx + 60, 1120, t, KNOT, 20, 600, SLIME, 1, 1, 3.0)
    if t > CLEAN:
        k = pr(t, CLEAN, CLEAN + 1.2)
        for i in range(8): slime(d, 900 + k * 260 + i * 20, 1200 - i * 60 + k * k * 300, 60 * (1 - k * 0.5), t, 1 - k, i)
        sparks(d, 540, 1150, t, CLEAN, 60, 1400, YEL, 4, 3, 1.0)
def u_knot(t, d):
    if t < KNOT:
        bigtext(d, 540, 300, "会不会", 110, WHITE); bigtext(d, 540, 460, "把自己闷死？", 120, YEL)
    elif t < CLEAN: stamp(d, t, KNOT, "打个结！", 540, 380, 190, YEL)
    else: stamp(d, t, CLEAN, "擦干净了", 540, 380, 170, WHITE)
    flash(d, t, [KNOT, CLEAN], WHITE, 0.7)
    if SILENCES[0][0] <= t < KNOT: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.4))

def w_feed(t, d):
    grad(d, (40, 30, 50), (12, 8, 16)); bubbles(d, t, 0.15)
    tear = ease(pr(t, TEAR, TEAR + 0.4))
    # big meat block right
    d.rect(640, 900, 1040, 1450, fill=A(shade(MEAT), 1), r=40); d.rect(630, 890, 1030, 1440, fill=A(MEAT, 1), r=40)
    for k in range(3): d.line([(660, 1000 + k * 140), (1000, 980 + k * 140)], A((255, 220, 220), 0.6), 16)
    pull = 160 * tear
    s = eio(pr(t, KNOT2, TEAR))
    knot = None if t < KNOT2 else lerp(0.95, 0.12, s)
    # hagfish head at meat (x=630), body extends left -> path with ang=pi
    hx = 640 - lerp(160, 0, ease(pr(t, FEED, CHOMP))) - pull
    pts = body_path(hx, 1170, 540, t, 20 if t < CHOMP else 6, ang=math.pi, knot=knot, kr=70, speed=5)
    if t > TEAR:
        cx = hx - 10
        d.rect(cx - 60, 1110, cx + 80, 1230, fill=A(MEAT, 1), r=30)
        sparks(d, 640, 1170, t, TEAR, 40, 1000, (255, 160, 160), 7, 3, 1.0)
    hagfish(d, pts, 50, t, "chill" if t < CHOMP else ("sus" if t < TEAR else "proud"))
def u_feed(t, d):
    if t < KNOT2: pop_text(d, t, CHOMP, "咬住", 380, 170, WHITE)
    elif t < TEAR: stamp(d, t, KNOT2, "打结一撑", 540, 380, 170, YEL)
    else: stamp(d, t, TEAR, "扯下来！", 540, 380, 180, RED)
    flash(d, t, [CHOMP, TEAR], WHITE, 0.5)

def truck(d, x, y, s, rot, a=1.0):
    ca, sa = math.cos(rot), math.sin(rot)
    def R_(pts): return [(x + px * s * ca - (py + 0.35) * s * sa, y + px * s * sa + (py + 0.35) * s * ca) for px, py in pts]
    d.poly(R_([(-1.2, -0.7), (0.5, -0.7), (0.5, 0), (-1.2, 0)]), A((200, 210, 220), a))
    for k in range(3): d.poly(R_([(-1.1 + k * 0.55, -0.62), (-0.65 + k * 0.55, -0.62), (-0.65 + k * 0.55, -0.1), (-1.1 + k * 0.55, -0.1)]), A((90, 160, 220), a))
    d.poly(R_([(0.55, -0.55), (0.95, -0.55), (1.1, -0.25), (1.1, 0), (0.55, 0)]), A(TRUCKC, a))
    d.poly(R_([(0.65, -0.48), (0.9, -0.48), (1.0, -0.28), (0.65, -0.28)]), A((180, 230, 255), a))
    for wx in (-0.9, -0.3, 0.85):
        cx, cy = R_([(wx, 0.05)])[0]; d.circ(cx, cy, 0.15 * s, fill=A((60, 62, 72), a)); d.circ(cx, cy, 0.06 * s, fill=A((170, 175, 185), a))
def car(d, x, y, s, slimed=0.0):
    d.rect(x - 0.9 * s, y - 0.35 * s, x + 0.9 * s, y, fill=A(CARC, 1), r=0.15 * s)
    d.rect(x - 0.5 * s, y - 0.7 * s, x + 0.45 * s, y - 0.3 * s, fill=A(shade(CARC, 0.15), 1), r=0.15 * s)
    d.rect(x - 0.42 * s, y - 0.63 * s, x + 0.37 * s, y - 0.38 * s, fill=A((190, 230, 255), 1), r=0.08 * s)
    for wx in (-0.55, 0.55): d.circ(x + wx * s, y, 0.18 * s, fill=A((60, 62, 72), 1))
    if slimed > 0:
        for k in range(7): slime(d, x - 0.8 * s + k * 0.27 * s, y - 0.45 * s + 0.1 * s * math.sin(k * 2), 0.28 * s * slimed, 0, slimed, k)
def w_truck(t, d):
    grad(d, (120, 180, 230), (200, 225, 245), 0, 1100)
    d.rect(0, 1100, 1080, 1920, fill=A((80, 84, 96), 1))
    for k in range(6): d.rect(k * 220 - (t * 300) % 220 * (t < FLIP), 1440, k * 220 + 110 - (t * 300) % 220 * (t < FLIP), 1460, fill=A(YEL, 1))
    d.rect(0, 1080, 1080, 1100, fill=A((110, 150, 90), 1))
    car(d, 800, 1520, 170, ease(pr(t, SPLAT, SPLAT + 0.5)))
    rot = math.pi * ease(pr(t, FLIP, FLIP + 0.5))
    tx = lerp(-200, 360, ease(pr(t, TRUCK, FLIP))) + 60 * ease(pr(t, FLIP, FLIP + 0.5))
    hop = 160 * math.sin(math.pi * pr(t, FLIP, FLIP + 0.5))
    truck(d, tx, 1350 - 0.35 * 260 - hop, 260, rot)
    if t > FLIP:
        for i in range(10):
            u = pr(t, FLIP + 0.1 + i * 0.05, FLIP + 1.0 + i * 0.05)
            if u <= 0: continue
            sx = lerp(tx, 120 + i * 90, u); sy = lerp(1250, 1500 + (i % 3) * 120, u) - 300 * math.sin(math.pi * u)
            hagfish(d, body_path(sx, sy, 160, t + i, 14, ang=i * 0.6), 18, t, "scared")
        if t > SPLAT:
            k = ease(pr(t, SPLAT, SPLAT + 0.6))
            for i in range(9): slime(d, 100 + i * 110, 1480 + 70 * math.sin(i * 1.7), 80 * k, t, 0.9 * k, i + 10)
        sparks(d, tx, 1300, t, FLIP, 50, 1400, (255, 230, 150), 9, 3, 1.0)
def u_truck(t, d):
    if t < SPLAT: bigtext(d, 540, 300, "2017 · 美国公路", 100, (20, 40, 80))
    else:
        pop_text(d, t, SPLAT, "3.4 吨盲鳗", 330, 150, YEL)
    flash(d, t, [FLIP, SPLAT], WHITE, 0.6)

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
    for i, (t0, s) in enumerate(((BUB1, "盲鳗不是鳗鱼，它没有下巴"), (BUB2, "被黏液糊住，它就打个结擦掉"))):
        if t > t0:
            k = back(pr(t, t0, t0 + 0.25))
            bubble(d, 1010, 640 + i * 190, s, 1, (120, 220, 120), (20, 40, 20), min(1, k), int(58 * (0.7 + 0.3 * k)))
    if t > BUB2 + 1.0:
        k = back(pr(t, BUB2 + 1.0, BUB2 + 1.25))
        bubble(d, 70, 1020, "？？？真的假的", -1, (60, 64, 80), WHITE, min(1, k), 66)
    if t > BUB2 + 1.8:
        a = ease(pr(t, BUB2 + 1.8, BUB2 + 2.1))
        bubble(d, 1010, 1210, "Scientific Reports 2011，自己查", 1, (120, 220, 120), (20, 40, 20), a, 50)
    d.text(540, 1780, "Zintzen et al. Sci Rep 2011, 1:131 · Böni et al. Sci Rep 2016, 6:30371", 24, A(WHITE, 0.7), k=0)
    d.text(540, 1815, "Zeng et al. eLife 2023 · Oregon State Police, 2017-07-13", 24, A(WHITE, 0.7), k=0)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

SECS = [(0, HOOK_END, w_hook, u_hook), (EEL, SHARK, w_eel, u_eel), (SHARK, VOL, w_shark, u_shark), (VOL, STUCK, w_vol, u_vol),
        (STUCK, FEED, w_knot, u_knot), (FEED, TRUCK, w_feed, u_feed), (TRUCK, OUTRO, w_truck, u_truck), (OUTRO, 99, w_end, u_end)]
CUTS = [HOOK_END, NOJAW, SHARK, VOL, STUCK, FEED, TRUCK, OUTRO]

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
    d.rect(800, 80, 1030, 128, fill=A((220, 120, 150), 0.95), r=24); d.text(915, 104, "盲鳗打结", 26, A(WHITE, 1))

def cam(t):
    z = 1.0 + 0.07 * pulse(t, HITS, 7)
    if t < 0.5: z += 0.1 * (1 - ease(pr(t, 0, 0.3)))
    for a, b in RISERS:
        if a <= t < b: z += 0.1 * eio(pr(t, a, b))
    amp = 28 * pulse(t, [BURST, SLIME_IN, KNOT, FLIP], 3) + 12 * pulse(t, HITS, 5)
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
