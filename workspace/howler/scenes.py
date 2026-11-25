# 《吼猴新种》scenes — every subtitle line gets its OWN set, composition and demo (user rule 2026-11-16).
# Flat 2D, no dark outlines (eye/mouth lines only). Content in x 180–900, above the subtitle box (y < ~1240) except card.
# Entities never pop: they spring-scale in from 0 or slide in, and fade out over >= 0.3 s with their own times.
import math, random
from PIL import Image, ImageDraw
from hchars import *
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
def dbox(d, x0, y0, x1, y1, col, a, w=4): dashed(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], col, a, w)
def glow_disc(d, x, y, r, col, a):
    for i in range(7):
        k = 1 - i / 7; d.circ(x, y, r * (0.3 + 0.9 * k), fill=A(col, a * 0.14 * (1.2 - k * 0.6)))
def grid(d, col, a, step=90):
    for i in range(-1, 14): d.line([(i * step, 0), (i * step, 1920)], A(col, a), 2)
    for j in range(-1, 23): d.line([(0, j * step), (1080, j * step)], A(col, a), 2)
def sbox(d, x0, y0, x1, y1, col, a=1.0, r=24, sh=0.22):
    d.rect(x0 + 12, y0 + 16, x1 + 12, y1 + 16, fill=A((0, 0, 0), sh * a), r=r); d.rect(x0, y0, x1, y1, fill=A(col, a), r=r)
def odometer(d, x, y, v, size, col, a=1.0, k=1):
    d.text(x, y, str(int(v)), size, A(col, a), k=k)

# ---------------- shared environment: rainforest canopy ----------------
TONES = {"dawn": ((255, 186, 120), (96, 160, 150), (40, 92, 76), (24, 66, 56), (14, 44, 40)),
         "day":  ((150, 214, 240), (110, 190, 170), (60, 130, 84), (40, 104, 70), (24, 76, 54)),
         "dusk": ((250, 140, 110), (120, 90, 140), (60, 60, 90), (40, 44, 70), (24, 30, 50))}
def canopy_row(d, y0, col, seed, r0=90, r1=150, a=1.0, t=0.0, sway=0.0):
    rr = random.Random(seed); x = -80
    while x < 1180:
        r = rr.uniform(r0, r1); d.circ(x + sway * math.sin(t * 0.7 + x * 0.01), y0 - r * 0.4 + rr.uniform(-30, 30), r, fill=A(col, a)); x += r * rr.uniform(0.9, 1.3)
    d.rect(-40, y0, 1120, 1960, fill=A(col, a))
def jungle(d, t, tone="dawn", sun=True, mist=1.0, shake=0.0):
    sky, sky2, c1, c2, c3 = TONES[tone]
    grad(d, sky, sky2, 0, 1000)
    if sun:
        glow_disc(d, 760, 560, 260, (255, 236, 180), 0.7); d.circ(760, 560, 90, fill=A((255, 240, 200), 1))
    sx = shake * math.sin(t * 61)
    canopy_row(d, 780, mix(c1, sky2, 0.35), 4, 80, 130, 1, t, 4)
    for i in range(3): d.ell((i * 420 + t * 20) % 1500 - 200, 800 + i * 30, 360, 46, A(WHITE, 0.10 * mist))
    canopy_row(d, 980, c1, 7, 100, 160, 1, t, 6 + sx)
    canopy_row(d, 1220, c2, 11, 110, 170, 1, t, 8 + sx)
    d.rect(-40, 1300, 1120, 1960, fill=A(c3, 1))
def side_leaves(d, t, a=1.0, shake=0.0):
    for x, y, L, ang, c in ((40, 420, 260, 0.2, LEAF3), (60, 720, 300, -0.15, LEAF1), (1040, 520, 280, math.pi - 0.2, LEAF1), (1030, 860, 300, math.pi + 0.1, LEAF3),
                            (30, 1100, 260, -0.3, LEAF2), (1050, 1150, 240, math.pi + 0.25, LEAF2)):
        leaf(d, x, y, L, ang + 0.04 * math.sin(t * 1.3 + y) + shake * 0.15 * math.sin(t * 50 + x), c, a, 0.36)

# ======== 1. hook: a leaf curtain; the roar at 0 s blows it apart ========
HX, HY, HS = 540, 860, 1.22
CURTAIN = []
_rr = random.Random(21)
for _i in range(46):
    CURTAIN.append((_rr.uniform(230, 850), _rr.uniform(430, 1180), _rr.uniform(90, 150), _rr.uniform(-math.pi, math.pi), [LEAF1, LEAF2, LEAF3][_i % 3],
                    _rr.uniform(0.0, 1.2), _rr.uniform(-0.6, 0.6)))
def leaf_curtain(d, t, t0=0.0):
    for i, (x, y, L, ang, c, td, dv) in enumerate(CURTAIN):
        u = t - (t0 + td)
        if u < 0:
            leaf(d, x + 3 * math.sin(t * 30 + i), y, L, ang, c, 1); continue
        dx, dy = x - HX, y - (HY - 180); dn = math.hypot(dx, dy) + 1e-6
        dist = 900 * (1 - math.exp(-u * 2.4)) / 2.4
        al = 1 - cl((u - 0.5) / 0.6)
        if al <= 0: continue
        leaf(d, x + dx / dn * dist, y + dy / dn * dist + 90 * u * u, L * (1 + 0.3 * u), ang + u * (5 + dv * 6), c, al)
def s_hook(t, d):
    jungle(d, t, "dawn", shake=pulse(t, [0.0], 2.0) * 6)
    branch(d, -40, HY + 150 * HS + 20, 1120, HY + 150 * HS - 10, 46, 1, t, True, 8)
    roar = 1.0 if t < 1.7 else 1 - ease(pr(t, 1.7, 2.1))
    howler(d, HX, HY, HS, t, 1, "red", "roar" if t < 2.0 else "sus", mouth=roar * (0.85 + 0.15 * math.sin(t * 22)), look=0.0 if t < 2.0 else 0.4 * math.sin(t * 2))
    roar_waves(d, HX, HY - 120 * HS, t, 0.0, 1.8, (255, 240, 190), 0.9, -math.pi / 2, 160, 900, 0.22, 14)
    leaf_curtain(d, t)
    flying_leaves(d, t, 0.0, HX, HY - 160, 30, 1300, 1, 5, 2.4)
    side_leaves(d, t, 1, pulse(t, [0.0], 2.5))
    k = popk(t, 0.0, "bouncy"); al = 1 - pr(t, 1.3, 1.7)
    if k > 0 and al > 0:
        sz = int(230 * min(1.12, 0.5 + 0.5 * k) * (1 + 0.04 * math.sin(t * 40)))
        d.text(540, 400, "吼——！", sz, A(GOLD, al), k=1)

# ======== 2. reveal: wide canopy, sound rings travel ~5 km across ========
def s_reveal(t, d):
    t0 = T["reveal"]
    jungle(d, t, "day", sun=False)
    # tall emergent trees
    for x, y, s_, col in ((250, 640, 1.0, (54, 120, 76)), (860, 820, 0.55, (64, 136, 86))):
        d.rect(x - 16 * s_, y, x + 16 * s_, 1320, fill=A(BARK, 1))
        for j in range(5): d.circ(x + (j - 2) * 60 * s_, y - 20 * s_ + (j % 2) * 30 * s_, 90 * s_, fill=A(col, 1))
    k = ease(pr(t, t0, t0 + 0.4))
    howler(d, 250, 470, 0.42, t, 1, "red", "roar", mouth=0.7 + 0.3 * math.sin(t * 20), tail=True)
    for j in range(8):                         # rings expanding across the canopy, each fades
        tb = t0 + 0.2 + j * 0.42; u = (t - tb) / 2.4
        if 0 <= u < 1:
            r = 60 + u * 900; d.arc(250, 420, r, r * 0.55, -40, 40, A((255, 240, 180), 0.85 * (1 - u) ** 1.2), 9)
    # distance ruler 0..5 km along the canopy
    rx0, rx1, ry = 250, 880, 1120
    prog = ease(pr(t, t0 + 0.3, t0 + 2.6))
    d.rect(rx0 - 10, ry - 24, rx1 + 10, ry + 24, fill=A((20, 40, 30), 0.55), r=24)
    d.rect(rx0, ry - 8, lerp(rx0, rx1, prog), ry + 8, fill=A(GOLD, 1), r=8)
    for i in range(6):
        x = lerp(rx0, rx1, i / 5); on = prog >= i / 5 - 1e-3
        kk = popk(t, t0 + 0.3 + 2.3 * (i / 5) ** 1, "bouncy") if on else 0
        d.circ(x, ry, 14, fill=A(WHITE if on else (120, 140, 130), 1))
        if kk > 0: d.text(x, ry - 60, str(i), int(44 * min(1.1, kk)), A(WHITE, min(1, kk)), k=1)
    if prog > 0.98: d.text(rx1 + 0, ry + 62, "km", 36, A(WHITE, ap(t, t0 + 2.6)), k=1)
    # far listener perks up
    kk = popk(t, t0 + 2.6, "bouncy")
    howler_head(d, 860, 690, 0.32, t, 1, "dull", "shock" if t > t0 + 2.6 else "calm", look=-0.8)
    if kk > 0: d.text(910, 610, "!", int(70 * min(1.1, kk)), A(GOLD, 1), k=1)

# ======== 3. why: two groups shout across a territory border ========
def s_why(t, d):
    t0 = T["why"]
    jungle(d, t, "dawn", sun=True, mist=0.6)
    for x in (170, 910):
        d.rect(x - 34, 600, x + 34, 1400, fill=A(BARK, 1)); d.rect(x - 34, 600, x - 14, 1400, fill=A(BARK_L, 0.5))
    branch(d, 100, 980, 470, 990, 34, 1, t, True, 2); branch(d, 610, 990, 980, 980, 34, 1, t, True, 4)
    L_on = (t0 + 0.3 <= t < t0 + 2.0); R_on = (t0 + 2.2 <= t < t0 + 3.9)
    for i, (x, y, s_) in enumerate(((330, 820, 0.62), (220, 860, 0.45))):
        m = (0.8 + 0.2 * math.sin(t * 20 + i)) if L_on else 0.0
        howler(d, x, y + (s_ - 0.62) * -260, s_, t + i, 1, "red", "roar" if L_on else ("proud" if t > t0 + 2.0 else "calm"), mouth=m, flip=1)
    for i, (x, y, s_) in enumerate(((750, 830, 0.62), (860, 870, 0.45))):
        m = (0.8 + 0.2 * math.sin(t * 20 + i)) if R_on else 0.0
        howler(d, x, y + (s_ - 0.62) * -260, s_, t + i, 1, "black", "roar" if R_on else ("shock" if L_on else "calm"), mouth=m, flip=-1)
    roar_waves(d, 360, 720, t, t0 + 0.3, t0 + 2.0, (255, 230, 160), 0.9, 0.0, 34, 420, 0.22, 10)
    roar_waves(d, 720, 730, t, t0 + 2.2, t0 + 3.9, (200, 220, 255), 0.9, math.pi, 34, 420, 0.22, 10)
    flying_leaves(d, t, t0 + 0.4, 560, 760, 10, 500, 0.9, 31, 1.6, dirx=1)
    flying_leaves(d, t, t0 + 2.3, 520, 760, 10, 500, 0.9, 32, 1.6, dirx=-1)
    ka = ap(t, t0 + 0.2)
    dashed(d, [(540, 520), (540, 1240)], WHITE, 0.55 * ka, 6, 22, 16)       # territory border
    kh = popk(t, t0 + 1.0, "bouncy")                                        # "home" sign on the left tree (picture only)
    if kh > 0:
        kk = min(1.05, kh); x, y = 230, 560
        d.line([(x - 40, y - 70), (x, y - 120), (x + 40, y - 70)], A((200, 170, 120), 1), 6)
        sbox(d, x - 90 * kk, y - 70 * kk, x + 90 * kk, y + 70 * kk, (236, 214, 160), 1, 14)
        d.poly([(x - 50 * kk, y), (x, y - 44 * kk), (x + 50 * kk, y)], A((210, 80, 60), 1)); d.rect(x - 36 * kk, y, x + 36 * kk, y + 46 * kk, fill=A((250, 244, 230), 1))
        d.rect(x - 10 * kk, y + 14 * kk, x + 10 * kk, y + 46 * kk, fill=A((140, 90, 60), 1))
    for side, on, x in ((0, L_on, 330), (1, R_on, 750)):                       # volume meters
        lv = (0.55 + 0.45 * abs(math.sin(t * 9 + side))) if on else 0.12
        for j in range(8):
            c = (110, 220, 120) if j < 5 else ((255, 210, 70) if j < 7 else (255, 90, 80))
            d.rect(x - 70 + j * 18, 470 - j * 8, x - 56 + j * 18, 500, fill=A(c, 1 if j / 8 < lv else 0.2), r=4)

# ======== 4. throat: anatomy chart, hollow hyoid resonates ========
def s_throat(t, d):
    t0 = T["throat"]
    grad(d, (246, 238, 220), (226, 214, 190)); grid(d, (200, 186, 160), 0.35, 60)
    d.rect(200, 300, 880, 316, fill=A((200, 70, 60), 0.8), r=8)
    cut = ease(pr(t, t0 + 0.5, t0 + 1.1)); glow = ease(pr(t, t0 + 1.1, t0 + 1.6))
    op = 0.5 + 0.5 * math.sin((t - t0) * 7) if t > t0 + 1.4 else 0.15
    hx, hy, hr = anat_head(d, 420, 600, 1.1, t, 1, open_=op * glow, glow=glow, cut=cut)
    if cut > 0.5:
        roar_waves(d, 720, 690, t, t0 + 1.5, t0 + 5, (230, 120, 60), 0.9, 0.0, 30, 300, 0.25, 9)
    ptag(d, t, t0 + 1.2, hx - 150, hy + 200, "舌骨", (255, 214, 120), 40)
    if t > t0 + 1.2: d.line([(hx - 120, hy + 170), (hx - hr * 0.6, hy + hr * 0.6)], A((150, 110, 70), ap(t, t0 + 1.2)), 5)
    # comparison: human hyoid = small horseshoe
    kc = popk(t, t0 + 2.4, "smooth")
    if kc > 0:
        al = min(1, kc); x0 = 640; y0 = 1050
        sbox(d, x0, y0 - 110, x0 + 240, y0 + 110, (255, 252, 244), al, 22)
        d.arc(x0 + 70, y0 + 4, 30, 26, 200, 340, A((190, 170, 140), al), 12)
        hyoid_icon(d, x0 + 170, y0 - 6, 50, "oval", al, (236, 220, 190), (110, 70, 70))
        d.text(x0 + 70, y0 + 70, "人", 34, A(NAVYT, al), k=1); d.text(x0 + 170, y0 + 70, "吼猴", 34, A(NAVYT, al), k=1)

# ======== 5. q: the field checklist — so loud, could anyone be missed? ========
KNOWN = ["black", "red", "dull", "sara", "grey", "black", "red"]
def s_q(t, d):
    t0 = T["q"]
    jungle(d, t, "dusk", sun=False, mist=0.8)
    for j in range(5):                              # roars echoing from all over the forest
        tb = t0 + 0.2 + j * 0.55; u = (t - tb) / 0.9
        if 0 <= u < 1:
            x = [220, 880, 300, 820, 540][j]; y = [520, 600, 980, 1020, 420][j]
            d.arc(x, y, 40 + 140 * u, 40 + 140 * u, -60, 60, A((255, 230, 170), 0.8 * (1 - u)), 6)
            d.arc(x, y, 40 + 140 * u, 40 + 140 * u, 120, 240, A((255, 230, 170), 0.8 * (1 - u)), 6)
    k = popk(t, t0, "smooth"); y_ = (1 - min(1, k)) * 90
    rot_ = 0.02 * math.sin(t * 1.3)
    sbox(d, 230, 470 + y_, 850, 1180 + y_, (250, 244, 222), 1, 20)
    d.rect(230, 470 + y_, 850, 540 + y_, fill=A((90, 140, 90), 1), r=20)
    for j in range(8): d.circ(270 + j * 82, 470 + y_, 12, fill=A((120, 120, 130), 1))    # spiral rings
    rows = len(KNOWN) + 1
    for i in range(rows):
        y = 600 + i * 72 + y_
        d.rect(300, y + 26, 800, y + 29, fill=A((210, 200, 180), 1))
        if i < len(KNOWN):
            ki = popk(t, t0 + 0.15 + i * 0.16, "bouncy")
            if ki > 0: howler_head(d, 340, y, 0.27 * min(1.05, ki), t + i, 1, KNOWN[i], "calm", blink=False, beard=False)
            for b in range(3): d.rect(400 + b * 120, y - 8, 490 + b * 120 - (i * 13 + b * 29) % 40, y + 6, fill=A((190, 180, 170), min(1, ki)), r=6)
            check_mark(d, 760, y, 24, (80, 170, 100), 1, popk(t, t0 + 0.3 + i * 0.16, "bouncy"))
        else:
            ka = ap(t, t0 + 1.5)
            dbox(d, 314, y - 30, 366, y + 22, (200, 80, 80), ka, 3)
            bl = 0.55 + 0.45 * math.sin(t * 8)
            d.text(340, y - 4, "?", 50, A((220, 70, 70), ka * bl), k=1)
    # magnifier sweeps the page
    mx = 560 + 200 * math.sin((t - t0) * 1.6); my = 800 + 160 * math.cos((t - t0) * 1.1) + y_
    d.circ(mx, my, 70, fill=A((200, 230, 255), 0.25)); d.arc(mx, my, 70, 70, 0, 360, A((60, 70, 90), 1), 10)
    d.line([(mx + 50, my + 50), (mx + 120, my + 120)], A((60, 70, 90), 1), 18)

# ======== 6. BIG2: two new species burst out ========
def s_big2(t, d):
    t0 = BIG2
    grad(d, (60, 120, 70), (14, 46, 30))
    for i in range(18):                          # rays
        a0 = i / 18 * 2 * math.pi + t * 0.25
        d.poly([(540, 760), (540 + math.cos(a0) * 1600, 760 + math.sin(a0) * 1600), (540 + math.cos(a0 + 0.12) * 1600, 760 + math.sin(a0 + 0.12) * 1600)], A((255, 230, 120), 0.10))
    M = MapT(-80, -44, 8, -18, 290, 540, 790, 900)
    draw_map(d, M, 0.35 * ap(t, t0 + 0.1), land=(150, 190, 120), amz=(90, 170, 90), rivers=1.0, rw=5)
    kn = popk(t, t0, "bouncy")
    if kn > 0:
        d.text(540, 430, "2", int(300 * min(1.12, kn)), A(GOLD, 1), k=1)
        zap(d, 540, 430, t, t0, GOLD, 460)
    for i, (pal, x) in enumerate((("gold", 340), ("red", 740))):
        ti = t0 + 0.15 + i * 0.25; u = ease(pr(t, ti, ti + 0.4))
        if u <= 0: continue
        y = lerp(1500, 930, u) + hop(t, ti + 0.45, 30, 0.3)
        roaring = ti + 0.4 < t < ti + 1.6
        howler(d, x, y, 0.62, t + i, 1, pal, "roar" if roaring else "happy", mouth=0.9 if roaring else 0.0, flip=1 if i == 0 else -1)
        kb = popk(t, ti + 0.5, "bouncy")
        if kb > 0:
            bx, by = x + (80 if i == 0 else -80), y - 260
            d.circ(bx, by, 40 * min(1.1, kb), fill=A((240, 60, 70), 1)); d.text(bx, by, "新", int(40 * min(1.1, kb)), A(WHITE, 1), k=1)
    flying_leaves(d, t, t0, 540, 760, 34, 1400, 1, 44, 2.6)
    sparks(d, 540, 520, t, t0 + 0.05, 46, 1100, (255, 230, 140), 1, 9, 1.2)

# ======== 7. gold: Pantepui (table mountains), north-west ========
def tepui(d, x, y, w, h, col, a=1.0, top=None):
    d.poly([(x - w / 2, y), (x - w / 2 + 40, y - h), (x + w / 2 - 30, y - h - 10), (x + w / 2, y)], A(col, a))
    d.rect(x - w / 2 + 40, y - h - 14, x + w / 2 - 30, y - h + 4, fill=A(top or mix(col, (120, 170, 100), 0.5), a), r=6)
def inset_map(d, t, t0, x0, y0, w, h, blob, col, pinll):
    k = popk(t, t0, "smooth"); al = min(1, k)
    if al <= 0: return
    y0 += (1 - al) * 40
    sbox(d, x0, y0, x0 + w, y0 + h, (240, 236, 220), al, 20)
    sc = min((w - 30) / 48, (h - 30) / 69); cx = x0 + w / 2; cy = y0 + h / 2
    M = MapT(-82, -34, 13, -56, cx - 24 * sc, cy - 34.5 * sc, cx + 24 * sc, cy + 34.5 * sc)
    draw_map(d, M, al, land=(214, 196, 150), amz=(110, 170, 100), rivers=1.0, rcol=(90, 160, 230), rw=3)
    pu = 0.55 + 0.45 * math.sin((t - t0) * 6)
    range_blob(d, M, blob, col, al * pu)
    bx_ = sum(p[0] for p in blob) / len(blob); by_ = sum(p[1] for p in blob) / len(blob); qx, qy = M(bx_, by_)
    u = ((t - t0) * 0.9) % 1; d.circ(qx, qy, 12 + 50 * u, outline=A(col, al * (1 - u)), w=5)
    px, py = M(*pinll); pin(d, px, py, (230, 60, 60), al * min(1, popk(t, t0 + 0.4, "bouncy")), 0.8)
def s_gold(t, d):
    t0 = T["gold"]
    grad(d, (170, 214, 236), (220, 230, 210), 0, 900)
    tepui(d, 300, 820, 420, 300, (120, 110, 130)); tepui(d, 760, 860, 520, 380, (100, 94, 118))
    for j in range(3):                            # waterfall
        x = 640 + j * 8; d.rect(x, 490 + j * 4, x + 10, 860, fill=A(WHITE, 0.55 + 0.2 * math.sin(t * 9 + j)))
    canopy_row(d, 900, (64, 140, 86), 13, 70, 120); canopy_row(d, 1150, (44, 112, 70), 17, 90, 140)
    d.rect(-40, 1250, 1120, 1960, fill=A((28, 80, 54), 1))
    branch(d, -40, 1110, 760, 1090, 40, 1, t, True, 6)
    xin = lerp(-300, 400, ease(pr(t, t0, t0 + 0.7)))
    howler(d, xin, 930, 0.95, t, 1, "gold", "happy" if t > t0 + 0.9 else "calm", look=0.6)
    ptag(d, t, t0 + 1.0, 330, 600, "A. iroi", (255, 220, 120), 44, k=0)
    inset_map(d, t, t0 + 0.6, 640, 290, 250, 340, IROI, (255, 200, 60), (-63.5, 0.85))
    for j in range(5):                             # golden sparkle on the coat
        u = ((t - t0) * 0.8 + j / 5) % 1; x = 400 + 120 * math.cos(j * 2.3); y = 900 + 110 * math.sin(j * 1.7)
        d.circ(x, y - 40 * u, 6 * (1 - u) + 1, fill=A((255, 250, 210), 0.9 * (1 - u) * ap(t, t0 + 0.7)))

# ======== 8. red: southern Amazon, a river winds through ========
def s_red(t, d):
    t0 = T["red"]
    grad(d, (200, 226, 236), (236, 220, 180), 0, 900)
    d.rect(-40, 700, 1120, 1960, fill=A((80, 150, 90), 1))
    pts = [(lerp(-40, 1120, i / 30), 760 + 70 * math.sin(i / 30 * 7 + 0.5) + i * 4) for i in range(31)]
    d.line(pts, A((110, 170, 220), 1), 60); d.line(pts, A((150, 200, 240), 0.6), 20)
    canopy_row(d, 1000, (60, 130, 76), 23, 80, 130); canopy_row(d, 1200, (40, 104, 64), 27, 90, 140)
    d.rect(-40, 1280, 1120, 1960, fill=A((26, 76, 50), 1))
    branch(d, 320, 1120, 1120, 1100, 40, 1, t, True, 9)
    xin = lerp(1380, 680, ease(pr(t, t0, t0 + 0.7)))
    howler(d, xin, 940, 0.95, t, 1, "red", "happy" if t > t0 + 0.9 else "calm", look=-0.6, flip=-1)
    ptag(d, t, t0 + 1.0, 680, 600, "A. matogrossensis", (255, 150, 110), 36, k=0)
    inset_map(d, t, t0 + 0.6, 190, 290, 250, 340, MATO, (255, 110, 80), (-56.1, -9.95))

# ======== 9. diff: "spot the difference" — fur colour, then the hyoid opening ========
def s_diff(t, d):
    t0 = T["diff"]
    grad(d, (60, 50, 80), (24, 20, 40))
    for i, x0 in enumerate((190, 560)):
        k = popk(t, t0 + i * 0.15, "smooth"); al = min(1, k)
        if al <= 0: continue
        y_ = (1 - al) * 60
        sbox(d, x0, 330 + y_, x0 + 330, 760 + y_, (196, 160, 90) if i == 0 else (150, 150, 170), al, 18)
        d.rect(x0 + 16, 346 + y_, x0 + 314, 744 + y_, fill=A((236, 230, 214), al), r=12)
        howler_head(d, x0 + 165, 520 + y_, 0.9, t + i, al, "gold" if i == 0 else "dull", "sus" if t < t0 + 2.6 else "shock", look=0.6 if i == 0 else -0.6)
        tag(d, x0 + 165, 800 + y_, "新种" if i == 0 else "近亲", (255, 220, 120) if i == 0 else (200, 200, 220), al, 34)
    for i, (x, y) in enumerate(((272, 560), (642, 560))):        # circles on the coat colour
        kc = ease(pr(t, t0 + 0.9 + i * 0.2, t0 + 1.3 + i * 0.2))
        if kc > 0: d.arc(x, y, 56, 56, -90, -90 + 360 * kc, A((255, 80, 80), 1), 8)
    kn = popk(t, t0 + 1.4, "bouncy")
    if kn > 0: d.text(540, 560, "≠", int(90 * min(1.1, kn)), A((255, 220, 120), 1), k=0)
    # x-ray strip: hyoid openings differ
    kx = popk(t, t0 + 2.4, "smooth"); ax = min(1, kx)
    if ax > 0:
        y0 = 900 + (1 - ax) * 60
        sbox(d, 190, y0, 890, y0 + 300, (14, 30, 70), ax, 20)
        tag(d, 280, y0 + 40, "舌骨", (255, 214, 120), ax, 30)
        for j in range(8): d.line([(200, y0 + 20 + j * 36), (880, y0 + 20 + j * 36)], A((60, 110, 200), 0.18 * ax), 2)
        hyoid_icon(d, 355, y0 + 150, 96, "oval", ax, (220, 236, 255), (20, 40, 90))
        hyoid_icon(d, 725, y0 + 150, 96, "semi", ax, (220, 236, 255), (20, 40, 90))
        for i, x in enumerate((355, 725)):
            kc = ease(pr(t, t0 + 3.2 + i * 0.3, t0 + 3.6 + i * 0.3))
            if kc > 0: d.arc(x, y0 + 122, 60, 44, -90, -90 + 360 * kc, A((255, 80, 80), 1), 7)
        kq = popk(t, t0 + 3.9, "bouncy")
        if kq > 0: d.text(540, y0 + 150, "≠", int(90 * min(1.1, kq)), A((255, 220, 120), 1), k=0)

# ======== 10. river: rivers grow and split one population into two ========
_rr = random.Random(77)
DOTS = [(_rr.uniform(-67.5, -58), _rr.uniform(-8, 2.5), _rr.uniform(0, 1)) for _ in range(70)]
def s_river(t, d):
    t0 = T["river"]
    grad(d, (30, 70, 110), (14, 40, 70))
    M = MapT(-70, -53, 4.5, -11, 150, 330, 930, 1220)
    rp = ease(pr(t, t0 + 0.3, t0 + 3.2))
    draw_map(d, M, 1, land=(196, 186, 140), amz=(84, 156, 92), rivers=0.0)
    split = ease(pr(t, t0 + 1.0, t0 + 4.2))
    for lon, lat, ph in DOTS:
        x, y = M(lon, lat)
        north = lat > -3.3 + (lon + 60) * -0.05      # rough side of the Amazon trunk
        c0 = (210, 150, 80); c1 = (255, 205, 80) if north else (210, 80, 50)
        off = (-14 if north else 14) * split
        bob = 4 * math.sin(t * 2 + ph * 6)
        d.circ(x, y + off + bob, 11, fill=A(mix(c0, c1, split), 0.95)); d.circ(x - 3, y + off + bob - 3, 3.5, fill=A(WHITE, 0.6))
    for kname, pts in RIVERS.items():
        n = len(pts); m = rp * (n - 1); q = [M(*p) for p in pts[:int(m) + 1]]
        if int(m) < n - 1 and m > 0:
            f = m - int(m); p0, p1 = M(*pts[int(m)]), M(*pts[int(m) + 1]); q.append((lerp(p0[0], p1[0], f), lerp(p0[1], p1[1], f)))
        if len(q) > 1:
            d.line(q, A((60, 140, 230), 1), 26 if kname == "amazon" else 16); d.line(q, A((150, 210, 255), 0.7), 8 if kname == "amazon" else 5)
    # hourglass: time passes
    hx, hy = 830, 1130; u = pr(t, t0 + 0.5, t0 + 5.5)
    sbox(d, hx - 60, hy - 90, hx + 60, hy + 90, (240, 232, 210), 1, 20)
    d.poly([(hx - 36, hy - 66), (hx + 36, hy - 66), (hx, hy)], A((200, 190, 170), 1)); d.poly([(hx - 36, hy + 66), (hx + 36, hy + 66), (hx, hy)], A((200, 190, 170), 1))
    d.poly([(hx - 36 * (1 - u), hy - 66 * (1 - u)), (hx + 36 * (1 - u), hy - 66 * (1 - u)), (hx, hy)], A((240, 190, 80), 1))
    d.poly([(hx - 36 * u, hy + 66 - 66 * u), (hx + 36 * u, hy + 66 - 66 * u), (hx + 36, hy + 66), (hx - 36, hy + 66)], A((240, 190, 80), 1))
    for i in range(3):
        if 0.02 < u < 0.98: d.circ(hx, hy + 8 + ((t * 120 + i * 20) % 50), 3, fill=A((240, 190, 80), 1))

# ======== 11. dna: 86 sample tubes report in, counter rolls 0 -> 86 ========
TUBE_C = [(255, 120, 120), (255, 200, 90), (120, 200, 255), (160, 220, 140), (220, 150, 255)]
def s_dna(t, d):
    t0 = T["dna"]
    grad(d, (214, 230, 240), (180, 200, 214), 0, 1100); d.rect(-40, 1100, 1120, 1960, fill=A((150, 170, 186), 1))
    sbox(d, 170, 470, 910, 1150, (236, 242, 248), 1, 24)
    cols, rows = 12, 8      # 96 slots, 86 used
    tt = t0 + 0.3; span = 2.6
    n = 0
    for i in range(86):
        r_, c_ = divmod(i, cols); x = 215 + c_ * 59; y = 520 + r_ * 80
        ti = tt + span * (i / 86) ** 0.85
        k = popk(t, ti, "bouncy")
        if k <= 0:
            d.circ(x, y + 20, 10, fill=A((200, 210, 220), 1)); continue
        n += 1
        tube(d, x, y + 20 - (1 - min(1, k)) * 40, 0.48 * min(1.08, k), 1, TUBE_C[i % 5], 0.7, TUBE_C[(i + 2) % 5])
    for i in range(86, 96):
        r_, c_ = divmod(i, cols); d.circ(215 + c_ * 59, 520 + r_ * 80 + 20, 10, fill=A((200, 210, 220), 1))
    pu = 1 + 0.06 * pulse(t, [tt + span * (i / 86) ** 0.85 for i in range(0, 86, 10)], 10)
    d.text(540, 380, str(n), int(150 * pu), A((40, 60, 110) if n < 86 else (230, 70, 70), 1), k=1)
    if n >= 86: zap(d, 540, 380, t, tt + span, (230, 70, 70), 260)

# ======== 12. museum: a flake of dried skin from an old mounted specimen ========
def s_museum(t, d):
    t0 = T["museum"]
    grad(d, (86, 60, 50), (40, 28, 26))
    for i in range(4): d.rect(120 + i * 240, 260, 160 + i * 240, 1300, fill=A((110, 80, 66), 0.6))     # columns
    for i in range(7): d.circ(540, 400, 600 - i * 70, fill=A((255, 230, 180), 0.025 + 0.008 * i))      # spot light
    sbox(d, 230, 400, 850, 1180, (70, 50, 44), 1, 16)                                                 # cabinet
    d.rect(250, 420, 830, 1060, fill=A((170, 200, 210), 0.20), r=10)                                    # glass
    d.rect(300, 1000, 780, 1040, fill=A((120, 86, 60), 1), r=6)                                         # plinth
    d.line([(560, 560), (560, 1000)], A((120, 86, 60), 1), 12)
    howler(d, 540, 760, 0.62, 0.0, 1, "sara", "calm", sway=0.0, blink=False)                            # mounted, still
    d.rect(250, 420, 290, 1060, fill=A(WHITE, 0.10))
    sbox(d, 600, 1080, 820, 1150, (236, 220, 180), 1, 8, 0.15)                                          # old label
    d.text(710, 1102, "Mycetes", 26, A((90, 70, 50), 1), k=0); d.rect(640, 1124, 780, 1130, fill=A((160, 140, 110), 1))
    # tweezers come in, pick a flake from the foot, carry it to a tube
    u1 = ease(pr(t, t0 + 0.4, t0 + 1.4)); u2 = ease(pr(t, t0 + 1.8, t0 + 2.8))
    fx, fy = 540 + 0.62 * 72, 760 + 0.62 * 148
    tx = lerp(lerp(1000, fx + 10, u1), 760, u2); ty = lerp(lerp(560, fy - 4, u1), 640, u2)
    if t > t0 + 0.4:
        d.line([(tx + 6, ty - 6), (tx + 220, ty - 160)], A((200, 206, 214), 1), 10); d.line([(tx - 6, ty + 6), (tx + 200, ty - 180)], A((170, 176, 186), 1), 10)
    if t > t0 + 1.5:
        d.circ(tx, ty, 9, fill=A((120, 70, 46), 1))
    kt = popk(t, t0 + 1.6, "bouncy")
    if kt > 0:
        tube(d, 760, 760, 0.9 * min(1.06, kt), 1, (255, 130, 120), 0.5 if t < t0 + 2.9 else 0.5 + 0.2 * ap(t, t0 + 2.9), (90, 150, 230))
    if t > t0 + 2.9:
        helix(d, 760, 640, 760, 330, t, ap(t, t0 + 2.9), 46, 3, w=10, prog=ease(pr(t, t0 + 2.9, t0 + 3.6)))
        glow_disc(d, 760, 700, 90, (255, 200, 160), 0.5 * ap(t, t0 + 2.9))
    ptag(d, t, t0 + 0.8, 380, 330, "慕尼黑 · 博物馆", (236, 220, 180), 34)

# ======== 13. genome: whole family tree gets a full "check-up" scan ========
FAMILY = ["black", "dull", "gold", "sara", "red", "grey", "black", "red", "dull", "grey", "sara"]
def s_genome(t, d):
    t0 = T["genome"]
    grad(d, (230, 244, 238), (200, 222, 214))
    bx, by = 280, 1180
    gp = ease(pr(t, t0, t0 + 0.9))
    for i in range(len(FAMILY)):            # cladogram: trunk on the left, a twig per species
        y = 380 + i * 72; xj = 300 + 40 * (i % 3)
        d.line([(230, by), (230, lerp(by, y, gp))], A((120, 160, 140), 1), 8)
        if gp > 0.3: d.line([(230, y), (lerp(230, xj, ease(pr(t, t0 + 0.3 + i * 0.03, t0 + 0.6 + i * 0.03))), y)], A((120, 160, 140), 1), 8)
        k = popk(t, t0 + 0.4 + i * 0.05, "bouncy")
        if k > 0: howler_head(d, xj + 40, y, 0.28 * min(1.06, k), t + i, 1, FAMILY[i], "calm", beard=False, blink=False)
        # genome barcode fills as the scanner passes
        sy = lerp(330, 1220, ease(pr(t, t0 + 1.0, t0 + 3.2)))
        fill = cl((sy - y + 20) / 60)
        rr = random.Random(i * 7)
        for b in range(26):
            if b / 26 > fill: break
            x = 420 + b * 17; c = [(90, 200, 230), (255, 140, 190), (255, 200, 80), (130, 210, 130)][rr.randrange(4)]
            d.rect(x, y - 18, x + 11, y + 18, fill=A(c, 1), r=3)
    sy = lerp(330, 1220, ease(pr(t, t0 + 1.0, t0 + 3.2)))
    if t0 + 0.9 < t < t0 + 3.6:
        al = 1 - pr(t, t0 + 3.2, t0 + 3.6)
        d.rect(200, sy - 4, 900, sy + 4, fill=A((60, 220, 200), al)); d.rect(200, sy - 50, 900, sy - 4, fill=A((60, 220, 200), 0.15 * al))
    sk = back(pr(t, t0 + 3.3, t0 + 3.5))     # "No.1" stamp
    if sk > 0:
        sz = 2 - sk; al = min(1, sk * 1.5); cx, cy = 800, 1150
        d.circ(cx, cy, 80 * sz, outline=A((220, 60, 60), 0.9 * al), w=10 * sz); d.text(cx, cy, "No.1", int(50 * sz), A((220, 60, 60), 0.9 * al), k=1)

# ======== 14. y1941: a timeline from the last name card to the two new ones ========
def namecard(d, x, y, s, a, pal, yr, sepia=0.0):
    c = mix((250, 246, 232), (226, 200, 150), sepia)
    sbox(d, x - 110 * s, y - 140 * s, x + 110 * s, y + 140 * s, c, a, 14 * s)
    if sepia > 0:
        HPAL["_sep"] = tuple(mix(cc, (170, 130, 90), sepia) for cc in HPAL[pal]); pal = "_sep"
    howler_head(d, x, y - 30 * s, 0.6 * s, 0.0, a, pal, "calm", beard=False, blink=False)
    d.text(x, y + 100 * s, yr, int(40 * s), A((90, 70, 50), a), k=1)
def s_y1941(t, d):
    t0 = T["y1941"]
    grad(d, (60, 70, 100), (26, 30, 52))
    ly = 900; prog = ease(pr(t, t0 + 0.6, t0 + 3.0))
    d.rect(200, ly - 6, 880, ly + 6, fill=A((120, 130, 170), 1), r=6)
    d.rect(200, ly - 6, lerp(200, 880, prog), ly + 6, fill=A(GOLD, 1), r=6)
    for i in range(10):
        x = lerp(200, 880, i / 9); d.rect(x - 3, ly - 22, x + 3, ly + 22, fill=A((160, 170, 200), 1))
    k1 = popk(t, t0 + 0.1, "smooth")
    if k1 > 0: namecard(d, 260, 640, 0.85 * min(1, k1), min(1, k1), "dull", "1941", 0.9)
    yr = int(lerp(1941, 2026, prog))
    if t > t0 + 0.6:
        x = lerp(200, 880, prog); d.circ(x, ly, 18, fill=A(GOLD, 1))
        d.text(x, ly + 70, str(yr), 48, A(WHITE, 1), k=1)
    for i, (pal, x) in enumerate((("gold", 740), ("red", 860))):
        ki = popk(t, t0 + 3.0 + i * 0.2, "bouncy")
        if ki > 0: namecard(d, x - 60, 640 + i * 40, 0.62 * min(1.06, ki), min(1, ki), pal, "2026")
    if t > t0 + 0.6 and prog < 1:                  # flying calendar pages
        for j in range(4):
            u = ((t - t0) * 2.2 + j / 4) % 1
            x = lerp(200, 880, prog) - 40 + 60 * u; y = 780 - 220 * u
            d.rect(x - 30, y - 34, x + 30, y + 34, fill=A((250, 246, 236), 0.9 * (1 - u)), r=6); d.rect(x - 30, y - 34, x + 30, y - 16, fill=A((220, 70, 60), 0.9 * (1 - u)), r=6)

# ======== 15. danger: forest tiles turn into fields; a canopy bridge links the fragments ========
TILES = [(c, r) for r in range(5) for c in range(6)]
_rr = random.Random(5)
LOSS = {tl: _rr.uniform(0, 1) for tl in TILES}
for keep in ((1, 2), (2, 2), (4, 2), (4, 1)): LOSS[keep] = 9
def s_danger(t, d):
    t0 = T["danger"]
    grad(d, (170, 200, 150), (120, 160, 110))
    x0, y0, cw, ch = 180, 380, 120, 150
    for (c, r) in TILES:
        x, y = x0 + c * cw, y0 + r * ch
        tl = t0 + 0.4 + LOSS[(c, r)] * 2.2; u = ease(pr(t, tl, tl + 0.35))
        d.rect(x + 3, y + 3, x + cw - 3, y + ch - 3, fill=A((230, 200, 110), 1), r=8)            # field
        for j in range(5): d.rect(x + 8, y + 14 + j * 26, x + cw - 8, y + 20 + j * 26, fill=A((210, 176, 90), 1))
        if u < 1:
            al = 1 - u
            d.rect(x + 3, y + 3, x + cw - 3, y + ch - 3, fill=A((50, 120, 70), al), r=8)
            for j in range(4): d.circ(x + 26 + (j % 2) * 60, y + 36 + (j // 2) * 70, 30, fill=A((70, 150, 84), al))
    howler(d, x0 + 2 * cw + 30, y0 + 2 * ch + 40, 0.36, t, 1, "red", "worry", look=0.5)
    kb = ease(pr(t, t0 + 3.0, t0 + 3.8))                       # rope bridge from fragment to fragment
    if kb > 0:
        ax, ay = x0 + 2 * cw + 100, y0 + 2 * ch + 70; bx, by = x0 + 4 * cw + 20, y0 + 2 * ch + 70
        ex = lerp(ax, bx, kb)
        d.line([(ax, ay), (ex, ay + 20 * math.sin(math.pi * (ex - ax) / max(1, bx - ax)))], A((140, 100, 60), 1), 8)
        d.line([(ax, ay - 30), (ex, ay - 30 + 20 * math.sin(math.pi * (ex - ax) / max(1, bx - ax)))], A((170, 130, 80), 1), 4)
    if t > t0 + 3.9:                                           # mother + baby start to cross (hopeful)
        u = ease(pr(t, t0 + 3.9, t0 + 5.4)); mx = lerp(x0 + 2 * cw + 120, x0 + 4 * cw - 10, u)
        howler(d, mx, y0 + 2 * ch - 40, 0.26, t, ap(t, t0 + 3.9), "red", "happy", baby=True, tail=False)

# ======== 16. card: one-line lesson — genome = the full DNA instruction book ========
def s_card(t, d):
    t0 = T["card"]
    grad(d, (34, 80, 64), (16, 40, 32))
    k = popk(t, t0, "smooth"); a_ = min(1, k); y_ = (1 - a_) * 60
    d.rect(186, 416 + y_, 926, 1336 + y_, fill=A((0, 0, 0), 0.25 * a_), r=30)
    d.rect(170, 400 + y_, 910, 1320 + y_, fill=A((230, 196, 110), a_), r=30)
    d.rect(190, 420 + y_, 890, 1300 + y_, fill=A((250, 244, 226), a_), r=22)
    d.rect(330, 450 + y_, 750, 520 + y_, fill=A((210, 70, 60), a_), r=35); d.text(540, 485 + y_, "一句话学会", 40, A(WHITE, a_), k=1)
    d.text(540, 610 + y_, "基因组", 96, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("一种生物", "全套的 DNA 说明书")):
        kk = ap(t, t0 + 0.6 + i * 0.5, 0.3)
        if kk > 0: d.text(540, 740 + i * 76 + y_, s_, 50, A(NAVYT, kk * a_), k=1)
    kk = ap(t, t0 + 1.6, 0.3)
    if kk > 0:                                      # an open book whose pages are DNA
        bx, by = 540, 1110
        d.poly([(bx, by - 120), (bx - 260, by - 150), (bx - 260, by + 90), (bx, by + 120)], A((236, 226, 200), kk))
        d.poly([(bx, by - 120), (bx + 260, by - 150), (bx + 260, by + 90), (bx, by + 120)], A((246, 238, 216), kk))
        d.rect(bx - 4, by - 120, bx + 4, by + 120, fill=A((190, 170, 130), kk))
        helix(d, bx - 230, by - 20, bx - 30, by - 10, t, kk, 28, 2.5, w=6)
        helix(d, bx + 30, by - 10, bx + 230, by - 20, t + 1, kk, 28, 2.5, w=6)
        u = (t - t0 - 1.6) % 1.2 / 1.2                   # page flipping
        if u < 0.5:
            fx = lerp(bx + 250, bx - 250, ease(u / 0.5))
            d.poly([(bx, by - 120), (fx, by - 150 + 40 * math.sin(u * 6.28)), (fx, by + 90), (bx, by + 120)], A((255, 250, 236), kk * 0.9))
        howler_head(d, 800, 1250 + y_, 0.36, t, a_ * ap(t, t0 + 1.8), "gold", "happy", beard=False)

# ======== 17. end: back to the dawn canopy, the two new species side by side ========
def s_end(t, d):
    t0 = T["end"]
    jungle(d, t, "dawn")
    branch(d, -40, 1140, 1120, 1120, 46, 1, t, True, 8)
    r1 = t0 + 0.4 <= t < t0 + 1.3; r2 = t0 + 1.5 <= t < t0 + 2.4
    howler(d, 360, 940, 0.8, t, 1, "gold", "roar" if r1 else "happy", mouth=0.9 if r1 else 0, look=0.5)
    howler(d, 730, 950, 0.8, t + 1, 1, "red", "roar" if r2 else ("shock" if r1 else "happy"), mouth=0.9 if r2 else 0, look=-0.5, flip=-1)
    roar_waves(d, 360, 820, t, t0 + 0.4, t0 + 1.3, (255, 230, 150), 0.7, -math.pi / 2, 50, 420, 0.25, 9)
    roar_waves(d, 730, 830, t, t0 + 1.5, t0 + 2.4, (255, 200, 170), 0.7, -math.pi / 2, 50, 420, 0.25, 9)
    k = popk(t, t0 + 2.6, "bouncy")
    if k > 0:
        bubble(d, 540, 370, 600 * min(1.05, k), 130, 0.95)
        d.text(540, 362, "谁的嗓门更大？", int(54 * min(1.05, k)), A(NAVYT, 1), k=1)
    ra = ap(t, t0 + 3.0, 0.3)
    if ra > 0:
        d.rect(170, 480, 910, 630, fill=A((6, 8, 20), 0.7 * ra), r=20)
        d.text(540, 515, "Batista et al. 2026, Communications Biology", 25, A(WHITE, 0.95 * ra), k=0)
        d.text(540, 555, "doi:10.1038/s42003-026-11187-8", 24, A(WHITE, 0.85 * ra), k=0)
        d.text(540, 595, "报道：IFLScience 2026-11-13", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))
