# 《叶中幽灵蛙》scenes — every subtitle line gets its OWN set, composition and demo (user rule 2026-11-16).
# Flat 2D, no dark outlines (eye/mouth lines only). Content in x 180–900, above the subtitle box (y < ~1230) except card.
# Entities never pop: they spring-scale in from 0, slide/hop in, and fade out over >= 0.3 s with their own times.
import math, random
from PIL import Image, ImageDraw
from gchars import *
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

# ---------------- shared set: night leaf-litter floor (hook / leaf / end) ----------------
def floor_night(d, t, dark=0.55, beam=1.0, bx=540, by=820, br=620, seed=1):
    grad(d, (22, 30, 30), (10, 14, 16))
    litter_bed(d, t, seed, 150, (-80, 0, 1160, 1980), 1, dark)
    for x, sc, ang in ((90, 1.0, 0.3), (1000, 1.1, -0.4), (150, 0.8, -0.2), (950, 0.7, 0.4)):
        fern(d, x, 1500 if x < 500 else 1450, sc, ang, t, mix((40, 96, 60), (0, 0, 0), dark * 0.6), mix((56, 120, 72), (0, 0, 0), dark * 0.6))
    if beam > 0:   # warm headlamp pool: brighten litter inside a soft circle
        spot(d, bx, by, br, beam)
    mist(d, t, 0.9, 500)

# ======== 1. hook: a giant eye in the litter opens at 0 s; pull back to the whole frog ========
_rr = random.Random(21)
COVER = [(_rr.uniform(150, 930), _rr.uniform(380, 1180), _rr.uniform(150, 240), _rr.uniform(-math.pi, math.pi), LITTER[_i % 7], _rr.uniform(0.0, 0.5)) for _i in range(26)]
def cover_leaves(d, t, cx=540, cy=760, t0=0.0):
    for i, (x, y, L, ang, c, td) in enumerate(COVER):
        u = max(0.0, t - (t0 + td))
        dx, dy = x - cx, y - cy; dn = math.hypot(dx, dy) + 1e-6
        dist = 1300 * (1 - math.exp(-u * 2.2)) if u > 0 else 0
        if (math.hypot(x + dx / dn * dist - 540, y + dy / dn * dist - 960)) > 1500: continue
        leaf_shape(d, x + dx / dn * dist, y + dy / dn * dist + 60 * u * u, L, ang + u * 3 * (1 if i % 2 else -1), c, 1)
def hook_frog_pose(t):
    """scale + centre so that the frog's LEFT eye sits at (540,760) at the start, then pull back."""
    k = E.ease_in_out_sine(pr(t, 2.3, 3.7))
    s = lerp(5.6, 1.75, k)
    ax, ay = lerp(540, 540 - 74 * 1.75, k), lerp(770, 900 - 132 * 1.75, k)
    return ax + 74 * s, ay + 132 * s, s
def s_hook(t, d):
    floor_night(d, t, 0.5, 1.0, 540, 760, 700)
    x, y, s = hook_frog_pose(t)
    lid = 1 - E.ease_out_cubic(pr(t, -0.15, 0.35))
    ghostfrog(d, x, y, s, t, 1, "calm", lid=lid, blink=t > 3.8, look=0.0, seed=0.3)
    zap(d, 540, 770, t, 0.0, IRED_L, 520, 0.8)
    cover_leaves(d, t, 540, 770, 0.0)
    bigword(d, t, -0.12, 540, 420, "一半红", 170, IRED_L, 2.6)
    bigword(d, t, 0.12, 540, 1130, "一半铜绿", 150, IBRZ_L, 2.6)

# ======== 2. leaf: the frog sits still and melts into the litter — only the eyes give it away ========
def s_leaf(t, d):
    t0 = T["leaf"]; u = t - t0
    floor_night(d, t, 0.25, 1.0, 540, 820, 720, seed=4)
    k = E.ease_in_out_sine(pr(u, 0.6, 2.2))
    m = E.ease_in_out_sine(pr(u, 0.0, 0.9)); fs = lerp(1.75, 1.05, m); fy = lerp(900, 860, m)
    ghostfrog(d, 540, fy, fs, t, 1, "calm", eyes_only=0.78 * k, blink=True, seed=1.1)
    rr = random.Random(9)   # a few leaves drift down and settle over the frog's body
    for i in range(9):
        td = 0.3 + i * 0.18; v = cl((u - td) / 0.9)
        if u < td: continue
        x1, y1 = 540 + rr.uniform(-170, 170), 900 + rr.uniform(-60, 160)
        x0_, y0_ = x1 + rr.uniform(-200, 200), 200
        e = E.ease_out_cubic(v)
        leaf_shape(d, lerp(x0_, x1, e) + 30 * math.sin(v * 6) * (1 - v), lerp(y0_, y1, e), rr.uniform(140, 200), rr.uniform(-3, 3) + (1 - e) * 2, LITTER[i % 7], cl((u - td) / 0.3))
    al = ap(u, 2.6, 0.35)
    if al > 0:
        for sd in (-1, 1): dcirc(d, 540 + sd * 74 * 1.05, 860 - 132 * 1.05, 70, GOLD, al * (0.6 + 0.4 * math.sin(t * 6)), 6, 28, t * 0.8)

# ======== 3. night: headlamp survey along a cloud-forest stream, clock 19:00 -> 03:00 ========
def clock_face(d, x, y, r, hours, a=1.0):
    sbox(d, x - r - 20, y - r - 20, x + r + 20, y + r + 90, (24, 30, 52), 0.9 * a, 30)
    d.circ(x, y, r, fill=A((236, 236, 226), a)); d.circ(x, y, r * 0.92, fill=A((250, 250, 244), a))
    for i in range(12):
        th = 2 * math.pi * i / 12 - math.pi / 2
        d.line([(x + math.cos(th) * r * 0.78, y + math.sin(th) * r * 0.78), (x + math.cos(th) * r * 0.88, y + math.sin(th) * r * 0.88)], A((60, 60, 80), a), 5)
    hh = hours % 12; th = 2 * math.pi * hh / 12 - math.pi / 2; tm = 2 * math.pi * (hours % 1) - math.pi / 2
    if hours > 19 + 0.01:   # elapsed sector, night blue
        a0 = math.degrees(2 * math.pi * 7 / 12 - math.pi / 2); a1 = math.degrees(th)
        if a1 < a0: a1 += 360
        d.d.pieslice((P(x - r * 0.7), P(y - r * 0.7), P(x + r * 0.7), P(y + r * 0.7)), a0, a1, fill=A((110, 140, 230), 0.35 * a))
    d.line([(x, y), (x + math.cos(th) * r * 0.5, y + math.sin(th) * r * 0.5)], A((40, 40, 60), a), 10)
    d.line([(x, y), (x + math.cos(tm) * r * 0.78, y + math.sin(tm) * r * 0.78)], A((230, 70, 60), a), 5)
    d.circ(x, y, 10, fill=A((40, 40, 60), a))
    hd = int(hours) % 24; mm = int((hours % 1) * 60)
    d.text(x, y + r + 48, f"{hd:02d}:{mm:02d}", 54, A(GOLD, a), k=1)
def s_night(t, d):
    t0 = T["night"]; u = t - t0; dur = nxt("night") - t0
    grad(d, (16, 26, 54), (8, 14, 26))
    rr = random.Random(3)
    for i in range(50):
        sx, sy = rr.uniform(0, 1080), rr.uniform(260, 800); d.circ(sx, sy, rr.uniform(1.5, 3.5), fill=A(WHITE, 0.4 + 0.3 * math.sin(t * 2 + i)))
    mx = lerp(260, 420, u / dur); glow_disc(d, mx, 430, 120, (230, 240, 210), 0.5); d.circ(mx, 430, 44, fill=A((236, 240, 222), 1))
    for j, (c, y0, amp) in enumerate((((30, 46, 74), 820, 260), ((22, 38, 54), 940, 200))):
        r2 = random.Random(10 + j); pts = [(-60, 1980)]; x = -60
        while x < 1160: pts.append((x, y0 - r2.uniform(0.3, 1.0) * amp)); x += r2.uniform(90, 170)
        pts.append((1160, 1980)); d.poly(pts, A(c, 1))
    mist(d, t, 1.2, 800, 7)
    for i in range(7):   # cloud-forest trunks with moss
        xx = 40 + i * 170 + 26 * math.sin(i * 2.1)
        d.rect(xx - 14, 520, xx + 14, 1160, fill=A((16, 32, 34), 1))
        d.ell(xx + (i % 2 * 2 - 1) * 14, 700 + (i * 53) % 200, 22, 46, A((36, 74, 56), 1))
    d.rect(-40, 1120, 1120, 1960, fill=A((20, 36, 32), 1))          # bank
    for i in range(6): d.ell(80 + i * 190, 1124, 120, 24, A((30, 56, 44), 1))
    d.rect(-40, 1190, 1120, 1260, fill=A((40, 80, 120), 1))         # stream
    for i in range(10):
        xx = (i * 140 + t * 60) % 1300 - 100; d.line([(xx, 1215 + (i % 3) * 14), (xx + 60, 1215 + (i % 3) * 14)], A((120, 180, 230), 0.4), 4)
    sx_ = lerp(170, 470, E.ease_in_out_sine(u / dur))
    scientist(d, sx_, 1150, 0.95, t, 1, walk=1.0, beam=1.0, beam_ang=0.55)
    kk = ap(u, 2.6, 0.5)
    if kk > 0:   # two red eye-shines in the beam
        spot(d, 780, 1130, 160, kk)
        for sd in (-1, 1): glow_disc(d, 780 + sd * 16, 1118, 30, IRED_L, kk); d.circ(780 + sd * 16, 1118, 6, fill=A(IRED_L, kk))
    hours = 19 + 8 * E.ease_in_out_sine(pr(u, 0.4, dur - 0.6))
    clock_face(d, 760, 470, 110, hours, ap(u, 0.0, 0.3))
    fireflies(d, t, 10, 5, 0.7, (100, 600, 1000, 1100))

# ======== 4. q: in the headlamp spotlight — a mystery ID card ========
def s_q(t, d):
    t0 = T["q"]; u = t - t0
    grad(d, (14, 18, 22), (6, 8, 10))
    litter_bed(d, t, 7, 110, (-80, 700, 1160, 1980), 1, 0.7)
    spot(d, 540, 860, 520, 1)
    gk = 0.5 + 0.5 * math.sin(t * 5)
    glow_disc(d, 540, 560, 260, (120, 200, 255), 0.35 * ap(u, 0.6, 0.4))
    bigword(d, t, t0 + 0.6, 540, 520, "?", 380, mix((150, 210, 255), WHITE, 0.3 * gk))
    ghostfrog(d, 540 + 6 * math.sin(t * 2), 900, 1.15, t, 1, "sus", look=math.sin(t * 2.2), seed=2.2)
    kk = popk(t, t0 + 1.2)
    if kk > 0:   # ID card slides up on the right
        al = ap(u, 1.2, 0.2); x0 = 640; y0 = 1010 + (1 - min(1, kk)) * 80
        sbox(d, x0, y0, x0 + 250, y0 + 170, (240, 236, 220), al, 20)
        d.rect(x0 + 20, y0 + 22, x0 + 90, y0 + 102, fill=A((120, 130, 150), al), r=10); d.text(x0 + 55, y0 + 62, "?", 54, A(WHITE, al), k=1)
        for j in range(3): d.rect(x0 + 110, y0 + 30 + j * 30, x0 + 230 - j * 20, y0 + 44 + j * 30, fill=A((190, 186, 176), al), r=6)
        d.text(x0 + 125, y0 + 140, "物种：？？？", 30, A((90, 80, 70), al), k=1)

# ======== 5. big2: NEW SPECIES burst ========
def s_big2(t, d):
    t0 = T["big2"]; u = t - t0
    rays(d, t, (60, 110, 80), (30, 64, 52), 18, 540, 860)
    for i in range(8): d.circ(540, 860, 560 - i * 60, fill=A((255, 236, 170), 0.02 + 0.008 * i))
    rr = random.Random(12)   # litter confetti burst
    for i in range(40):
        ang = rr.uniform(0, 2 * math.pi); v = rr.uniform(500, 1100); uu = max(0.0, u)
        r_ = v * (1 - math.exp(-uu * 2.5)) / 2.5
        x = 540 + math.cos(ang) * r_; y = 860 + math.sin(ang) * r_ + 140 * uu * uu
        if y < 2100: leaf_shape(d, x, y, rr.uniform(60, 110), ang + uu * 4, LITTER[i % 7], 1 - pr(u, 3.0, 4.5))
    yb = hop(u, 0.0, 120, 0.5)
    ghostfrog(d, 540, 930 + yb, 1.35, t, 1, "happy" if u > 0.5 else "shock", seed=0.7, glow_eyes=0.4 * (1 - pr(u, 0, 1.2)))
    bigword(d, t, t0 + 0.02, 540, 420, "新物种！", 170, GOLD)
    st = popk(t, t0 + 0.9)
    if st > 0:
        al = ap(u, 0.9, 0.15); sc = 1 + 0.6 * (1 - min(1, st))
        x, y = 790, 640
        d.circ(x, y, 92 * sc, fill=A(IRED, al)); d.circ(x, y, 80 * sc, fill=A((236, 70, 60), al))
        d.text(x, y - 14 * sc, "2026", int(40 * sc), A(WHITE, al), k=1); d.text(x, y + 28 * sc, "命名", int(30 * sc), A(WHITE, al), k=1)
    ptag(d, t, t0 + 1.6, 540, 1170, "Oreobates foliaspectrum", (250, 244, 226), 34, NAVYT, k=0)

# ======== 6. eye: extreme close-up, a brush paints the iris half by half ========
def brush(d, x, y, col, a=1.0, ang=-0.8):
    if a <= 0.01: return
    ca, sa = math.cos(ang), math.sin(ang)
    d.line([(x, y), (x - ca * 60, y - sa * 60)], A(col, a), 22)
    d.line([(x - ca * 60, y - sa * 60), (x - ca * 90, y - sa * 90)], A((200, 200, 210), a), 26)
    d.line([(x - ca * 90, y - sa * 90), (x - ca * 300, y - sa * 300)], A((176, 120, 70), a), 18)
def s_eye(t, d):
    t0 = T["eye"]; u = t - t0
    S_ = 300 / 38; ax, ay = 540, 720
    x, y = ax + 74 * S_, ay + 132 * S_
    grad(d, (40, 30, 26), (20, 16, 14))
    top = E.ease_in_out_sine(pr(u, 0.4, 1.5)); bot = E.ease_in_out_sine(pr(u, 1.7, 2.8)); ret = pr(u, 3.0, 4.0); scl = E.ease_out_cubic(pr(u, 4.2, 4.8))
    ghostfrog(d, x, y, S_, t, 1, "calm", eye=dict(top=top, bot=bot, ret=ret, scl=scl), blink=False, seed=0)
    ri = 38 * S_ * 0.86
    if 0.3 < u < 1.7:
        th = math.radians(180 + 180 * top); bx, by = ax + math.cos(th) * ri * 0.7, ay + math.sin(th) * ri * 0.7
        brush(d, bx, by, IRED, ap(u, 0.3, 0.2) * (1 - pr(u, 1.5, 1.7)))
    if 1.6 < u < 3.0:
        th = math.radians(180 * bot); bx, by = ax + math.cos(th) * ri * 0.7, ay + math.sin(th) * ri * 0.7
        brush(d, bx, by, IBRZ, ap(u, 1.6, 0.2) * (1 - pr(u, 2.8, 3.0)), 0.8)
    # colour chips on the left: up / down
    for j, (lbl, col, tt) in enumerate((("上", IRED, 1.4), ("下", IBRZ, 2.7))):
        kk = popk(t, t0 + tt)
        if kk > 0:
            yy = 420 + j * 600; al = ap(u, tt, 0.2)
            d.circ(230, yy, 52 * min(1.1, kk), fill=A(col, al)); d.text(230, yy, lbl, 46, A(WHITE, al), k=1)
    if scl > 0.05:
        arrow(d, 860, 1090, ax + 38 * S_ * 0.7, ay + 38 * S_ * 0.72, SCL, ap(u, 4.3, 0.3), 10)
        ptag(d, t, t0 + 4.4, 770, 1150, "眼白：黄色", SCL, 40)

# ======== 7. name: Latin dictionary cards  folia + spectrum ========
def ghost_icon(d, x, y, s, a, t):
    if a <= 0.01: return
    glow_disc(d, x, y, 90 * s, (220, 230, 255), 0.6 * a)
    pts = [(x - 50 * s, y + 60 * s)]
    for i in range(7): pts.append((x - 50 * s + i * 100 * s / 6, y + (60 + 14 * (i % 2)) * s + 4 * s * math.sin(t * 5 + i)))
    pts += [(x + 50 * s, y + 60 * s), (x + 50 * s, y - 10 * s)]
    for i in range(1, 12): th = math.pi * i / 12; pts.append((x + math.cos(th) * 50 * s, y - 10 * s - math.sin(th) * 56 * s))
    d.poly(pts, A((236, 240, 255), a))
    for sd in (-1, 1): d.ell(x + sd * 18 * s, y - 14 * s, 9 * s, 13 * s, A((60, 60, 90), a))
def dict_card(d, x, y, w, h, word, mean, icon, t, a=1.0, col=(250, 244, 226)):
    sbox(d, x - w / 2, y - h / 2, x + w / 2, y + h / 2, col, a, 26)
    d.rect(x - w / 2, y - h / 2, x + w / 2, y - h / 2 + 56, fill=A((150, 90, 60), a), r=26); d.rect(x - w / 2, y - h / 2 + 30, x + w / 2, y - h / 2 + 56, fill=A((150, 90, 60), a))
    d.text(x, y - h / 2 + 30, "拉丁文", 28, A((255, 240, 220), a), k=1)
    d.text(x, y - h / 2 + 110, word, 56, A((60, 40, 30), a), k=0)
    icon(d, x, y + 40, 1.0, a, t)
    d.text(x, y + h / 2 - 54, mean, 44, A((150, 60, 40), a), k=1)
def s_name(t, d):
    t0 = T["name"]; u = t - t0
    grad(d, (230, 214, 182), (200, 178, 140)); grid(d, (180, 150, 110), 0.25, 60)
    m = E.ease_in_out_sine(pr(u, 2.6, 3.3))
    k1 = E.ease_out_cubic(pr(u, 0.1, 0.6)); k2 = E.ease_out_cubic(pr(u, 0.7, 1.2))
    lx = lerp(-300, 350, k1) + m * 100; rx = lerp(1380, 730, k2) - m * 100
    al = 1 - pr(u, 2.9, 3.3)
    leaf_icon = lambda d_, x_, y_, s_, a_, t_: leaf_shape(d_, x_, y_, 170 * s_, -0.6 + 0.08 * math.sin(t_ * 2), (186, 120, 62), a_, 0.45)
    if al > 0.01:
        dict_card(d, lx, 760, 330, 440, "folia", "叶子", leaf_icon, t, al)
        dict_card(d, rx, 760, 330, 440, "spectrum", "幽灵 · 影像", ghost_icon, t, al)
        pk = popk(t, t0 + 1.4)
        if pk > 0: d.text(540, 760, "+", int(120 * min(1.1, pk)), A((150, 60, 40), ap(u, 1.4, 0.15) * al), k=1)
    mk = popk(t, t0 + 3.0)
    if mk > 0:
        a2 = ap(u, 3.0, 0.25); sc = min(1.05, mk)
        sbox(d, 540 - 360 * sc, 760 - 280 * sc, 540 + 360 * sc, 760 + 280 * sc, (250, 244, 226), a2, 30)
        ghostfrog(d, 540, 800, 0.95 * sc, t, a2, "calm", ghost=0.8, seed=0.4)
        d.text(540, 760 - 220 * sc, "foliaspectrum", int(60 * sc), A((60, 40, 30), a2), k=0)

# ======== 8. ghost: translucent leaf-coloured apparition; callouts: red eyes, long digits, litter colour ========
def s_ghost(t, d):
    t0 = T["ghost"]; u = t - t0
    floor_night(d, t, 0.2, 1.0, 540, 820, 760, seed=6)
    fk = 1 + 0.6 * E.ease_in_out_sine(pr(u, 1.6, 2.4))
    by = 860 + 14 * math.sin(t * 1.6)
    ghostfrog(d, 540, by, 1.15, t, 1, "calm", ghost=0.85, fk=fk, glow_eyes=0.8 * ap(u, 0.3, 0.4) * (0.7 + 0.3 * math.sin(t * 4)), seed=0.9)
    # 1) red eyes: rings
    a1 = ap(u, 0.3, 0.3)
    for sd in (-1, 1): dcirc(d, 540 + sd * 74 * 1.15, by - 132 * 1.15, 70, IRED_L, a1, 6, 30, t)
    # 2) long fingers & toes: glowing ticks at the digit tips
    a2 = ap(u, 1.6, 0.3)
    if a2 > 0:
        for (hx, hy) in ((540 - 80 * 1.15, by + 122 * 1.15), (540 + 80 * 1.15, by + 122 * 1.15)):
            glow_disc(d, hx, hy + 50, 120, (255, 230, 140), 0.9 * a2)
        for sd in (-1, 1):
            hx = 540 + sd * 150 * 1.15; hy = by + 126 * 1.15
            glow_disc(d, hx + sd * 60, hy, 110, (255, 230, 140), 0.8 * a2)
    # 3) colour match: frog chip = litter chip
    a3 = ap(u, 3.0, 0.3)
    if a3 > 0:
        y = 450
        sbox(d, 250, y - 95, 830, y + 95, (24, 30, 30), 0.85 * a3, 40)
        d.circ(390, y, 62, fill=A(GF, a3)); granules(d, 330, y - 60, 450, y + 60, GF_L, a3 * 0.6, 22, 3, 6, clip=lambda px, py: (px - 390) ** 2 + (py - y) ** 2 < 52 ** 2)
        leaf_shape(d, 690, y, 170, -0.5, (176, 120, 92), a3, 0.5)
        d.text(540, y, "=", 90, A(WHITE, a3), k=1)

# ======== 9. skin: magnifier over the back (pointed granules), then flip to the orange belly ========
def lens(d, x, y, r, a, inner):
    if a <= 0.01: return
    d.circ(x + 10, y + 14, r + 14, fill=A((0, 0, 0), 0.25 * a))
    d.circ(x, y, r + 14, fill=A((60, 70, 90), a)); inner(x, y, r)
    d.ell(x - r * 0.4, y - r * 0.5, r * 0.32, r * 0.14, A(WHITE, 0.35 * a))
    ang = 0.8; d.line([(x + math.cos(ang) * (r + 10), y + math.sin(ang) * (r + 10)), (x + math.cos(ang) * (r + 170), y + math.sin(ang) * (r + 170))], A((60, 70, 90), a), 34)
def s_skin(t, d):
    t0 = T["skin"]; u = t - t0
    grad(d, (60, 44, 32), (30, 22, 18)); litter_bed(d, t, 15, 110, a=1, dark=0.35)
    fl = math.cos(math.pi * E.ease_in_out_sine(pr(u, 2.7, 3.5)))
    belly = fl < 0
    frog_top(d, 540, 800, 1.6, t, 1, "folia", belly=belly, flipx=max(0.03, abs(fl)))
    la = ap(u, 0.4, 0.3) * (1 - pr(u, 2.4, 2.7)); lx = 520 + 40 * math.sin(u * 1.2); ly = 760
    def back_in(x, y, r):
        d.circ(x, y, r, fill=A(GF, la)); granules(d, x - r, y - r, x + r, y + r, GF_L, la, 38, 2, 11, clip=lambda px, py: (px - x) ** 2 + (py - y) ** 2 < (r - 10) ** 2)
        d.line([(x - r * 0.6, y - r * 0.1), (x - r * 0.3, y + r * 0.3), (x, y), (x + r * 0.3, y + r * 0.3), (x + r * 0.6, y - r * 0.1)], A(GF_M, la * 0.8), 26)
    lens(d, lx, ly, 190, la, back_in)
    lb = ap(u, 3.8, 0.3)
    def belly_in(x, y, r):
        d.circ(x, y, r, fill=A(BELLY, lb)); rr = random.Random(3)
        for i in range(18):
            px, py = x + rr.uniform(-r, r) * 0.8, y + rr.uniform(-r, r) * 0.8
            if (px - x) ** 2 + (py - y) ** 2 < (r - 30) ** 2: d.ell(px, py, rr.uniform(20, 40), rr.uniform(12, 24), A(BELLY_R, lb * 0.6))
    lens(d, 560, 860, 170, lb, belly_in)

# ======== 10. size: graph paper + ruler + 1-yuan coin ========
MM = 12.0
def paper(d):
    grad(d, (246, 244, 236), (232, 228, 216))
    grid(d, (170, 200, 220), 0.35, MM, -10, 1090, -10, 1930, 1); grid(d, (120, 160, 200), 0.45, MM * 10, -10, 1090, -10, 1930, 3)
def ruler_v(d, x, y0, mm, a=1.0, prog=1.0):
    d.rect(x - 8, y0 - 14, x + 66, y0 + mm * MM + 14, fill=A((250, 214, 90), a), r=10)
    for i in range(int(mm) + 1):
        L = 30 if i % 10 == 0 else (20 if i % 5 == 0 else 12)
        d.line([(x, y0 + i * MM), (x + L, y0 + i * MM)], A((70, 60, 40), a), 2)
        if i % 10 == 0: d.text(x + 50, y0 + i * MM, str(i), 22, A((70, 60, 40), a), k=1)
def s_size(t, d):
    t0 = T["size"]; u = t - t0
    paper(d)
    sv = 32.4 * MM; s = sv / 270; fx, fy = 455, 400 + 150 * s
    k = E.ease_out_cubic(pr(u, 0.0, 0.5))
    frog_top(d, fx - (1 - k) * 600, fy, s, t, 1)
    sn, vt = fy - 150 * s, fy + 120 * s
    ra = ap(u, 0.6, 0.3); rx = 770
    if ra > 0:
        ruler_v(d, rx, sn, 36, ra)
        dashed(d, [(fx, sn), (rx - 10, sn)], (230, 70, 60), ra, 4); dashed(d, [(fx, vt), (rx - 10, vt)], (230, 70, 60), ra, 4)
    mk = E.ease_in_out_sine(pr(u, 1.0, 2.6))
    if mk > 0:
        d.rect(rx - 34, sn, rx - 16, sn + sv * mk, fill=A((230, 70, 60), 1), r=8)
        v = 32.4 * mk; d.text(rx - 10, sn - 60, f"{v:4.1f} 毫米", 54, A((200, 50, 40), ap(u, 1.0, 0.2)), k=1)
    ck = popk(t, t0 + 3.0)
    if ck > 0:
        cx_, cy_ = 750, 1070 + (1 - min(1, ck)) * 60
        coin(d, cx_, cy_, 12.5 * MM, ap(u, 3.0, 0.2))
        ptag(d, t, t0 + 3.4, 400, 1175, "一元硬币：直径 25 毫米", (90, 110, 150), 32, WHITE)

# ======== 11. sex: male vs female side by side on the same paper ========
def s_sex(t, d):
    t0 = T["sex"]; u = t - t0
    paper(d)
    mm = 9.5; base = 1010
    tops = {}
    for j, (x, svl, lo, hi, lbl, col, tt) in enumerate(((335, 24.5, 23, 26, "雄", (80, 140, 220), 0.1), (690, 31.5, 30, 33, "雌", (230, 90, 120), 0.4))):
        kk = popk(t, t0 + tt)
        if kk <= 0: continue
        al = ap(u, tt, 0.2); s = svl * mm / 270 * min(1.05, 0.7 + 0.3 * kk)
        fy = base - 230 * s
        frog_top(d, x, fy, s, t, al)
        top = fy - 150 * s; tops[j] = top
        d.circ(x, top - 80, 46, fill=A(col, al)); d.text(x, top - 80, lbl, 46, A(WHITE, al), k=1)
        d.text(x, base + 60, f"{lo}–{hi} 毫米", 40, A(col, al), k=1)
    a2 = ap(u, 1.0, 0.3)
    if a2 > 0 and len(tops) == 2:
        dashed(d, [(200, tops[0]), (900, tops[0])], (80, 140, 220), a2, 4)
        dashed(d, [(520, tops[1]), (900, tops[1])], (230, 90, 120), a2, 4)
        arrow(d, 880, tops[0] - 4, 880, tops[1] + 14, (230, 90, 120), a2, 8)

# ======== 12. hole: cutaway — roots arch over a burrow; danger -> the frog dives in ========
GY = 760
def s_hole(t, d):
    t0 = T["hole"]; u = t - t0
    grad(d, (34, 44, 40), (20, 28, 26))
    litter_bed(d, t, 21, 50, (-80, 300, 1160, GY + 20), 1, 0.35)
    d.rect(820, 120, 1000, GY, fill=A((86, 62, 46), 1), r=20)                 # tree trunk (right)
    d.rect(-40, GY, 1120, 1960, fill=A(SOIL, 1))                               # soil cut
    for i in range(5): d.rect(-40, GY + 80 + i * 110, 1120, GY + 120 + i * 110, fill=A(mix(SOIL, SOIL_D, 0.3 + 0.1 * i), 1))
    rr = random.Random(5)
    for i in range(40): d.circ(rr.uniform(0, 1080), rr.uniform(GY + 30, 1300), rr.uniform(4, 12), fill=A(SOIL_D, 0.6))
    tun = [(640, GY - 10), (650, GY + 80), (620, GY + 170), (560, GY + 250), (560, GY + 330)]   # tunnel + chamber
    d.line(tun, A((26, 16, 12), 1), 120); d.ell(560, GY + 360, 130, 80, A((26, 16, 12), 1))
    for (x0, x1, h) in ((560, 860, 120), (470, 860, 70)):                     # raised roots arching over the entrance
        pts = [(x0 + (x1 - x0) * i / 16, GY - h * math.sin(math.pi * i / 16) ** 0.8) for i in range(17)]
        d.line(pts, A(ROOT, 1), 34); d.line([(p[0], p[1] - 8) for p in pts], A(ROOT_L, 0.6), 10)
    for i in range(6): d.line([(560 + i * 50, GY + 10), (540 + i * 56, GY + 90 + 20 * (i % 2))], A(ROOT, 0.9), 10)
    # path: sit at (360,GY) -> hop to the arch mouth -> slide down the tunnel to the chamber
    jt = 2.2; jd = 0.45
    if u < jt:
        fx, fy, s = 360, GY - 70, 0.42; face = "calm" if u < 1.3 else "shock"
    elif u < jt + jd:
        v = (u - jt) / jd; fx = lerp(360, 640, v); fy = lerp(GY - 70, GY - 10, v) - 160 * 4 * v * (1 - v); s = 0.42; face = "shock"
    else:
        v = E.ease_in_out_sine(pr(u, jt + jd, jt + jd + 0.9)); n = len(tun) - 1; q = v * n; i = min(n - 1, int(q)); f = q - i
        fx = lerp(tun[i][0], tun[i + 1][0], f); fy = lerp(tun[i][1], tun[i + 1][1], f) + 20 * v; s = lerp(0.42, 0.34, v); face = "calm"
    glow_eyes = 0.5 * ap(u, 3.6, 0.4)
    ghostfrog(d, fx, fy, s, t, 1, face, seed=0.2, glow_eyes=glow_eyes)
    da = ap(u, 1.2, 0.3) * (1 - pr(u, 2.6, 3.0))                                # danger: a big shadow sweeps in + "!"
    if da > 0:
        ang = lerp(-0.2, 0.55, E.ease_out_cubic(pr(u, 1.2, 2.2)))
        for j in range(5):
            sp = 0.16 - j * 0.03
            d.poly([(-40, 260), (-40 + math.cos(ang - sp) * 900, 260 + math.sin(ang - sp) * 900), (-40 + math.cos(ang + sp) * 900, 260 + math.sin(ang + sp) * 900)], A((255, 244, 190), 0.07 * da))
        d.text(360, GY - 210, "!", 110, A((255, 90, 70), da), k=1)
    ptag(d, t, t0 + 3.4, 280, GY + 340, "树根下的洞", (250, 220, 160), 36)

# ======== 13. four: four new species report in ========
LINEUP = [("azul", "azulensis"), ("chiri", "chirimoto"), ("folia", "foliaspectrum"), ("nigrum", "nigrumcompletum")]
def s_four(t, d):
    t0 = T["four"]; u = t - t0
    grad(d, (40, 110, 110), (20, 64, 70)); grid(d, WHITE, 0.05, 90)
    for i, (p, nm) in enumerate(LINEUP):
        x = 360 + (i % 2) * 360; y = 590 + (i // 2) * 410; tt = 0.15 + i * 0.35; kk = popk(t, t0 + tt)
        if kk <= 0: continue
        al = ap(u, tt, 0.2); yb = hop(u, tt, 90, 0.4)
        d.ell(x, y + 110, 150, 26, A((14, 50, 54), al))
        if p == "folia": glow_disc(d, x, y - 20, 230, GOLD, 0.6 * ap(u, 1.8, 0.4))
        ghostfrog(d, x, y + yb, 0.68 * min(1.08, kk), t, al, "happy", pal=p, seed=i * 0.7)
        d.circ(x - 150, y - 150, 34, fill=A(GOLD if p == "folia" else WHITE, al)); d.text(x - 150, y - 150, str(i + 1), 40, A(NAVYT, al), k=1)
        d.text(x, y + 160, nm, 30, A((236, 246, 240) if p != "folia" else GOLD, al), k=0)

# ======== 14. genus: a specimen cabinet fills from 27 to 31 drawers ========
def s_genus(t, d):
    t0 = T["genus"]; u = t - t0
    grad(d, (64, 44, 34), (36, 24, 20))
    cx0, cy0, cw, ch, cols = 220, 500, 128, 92, 5
    sbox(d, cx0 - 30, cy0 - 90, cx0 + cols * cw + 30, cy0 + 7 * ch + 30, (120, 80, 52), 1, 24)
    d.text(540, cy0 - 48, "Oreobates 属", 40, A((250, 230, 200), 1), k=0)
    n_old = min(27, int(27 * E.ease_out_cubic(pr(u, 0.0, 1.0)) + 0.999)) if u > 0 else 0
    for i in range(35):
        c, r = i % cols, i // cols; x0 = cx0 + c * cw + 8; y0 = cy0 + r * ch + 8
        d.rect(x0, y0, x0 + cw - 16, y0 + ch - 16, fill=A((90, 60, 40), 1), r=10)
        if i < 27:
            tt = 1.0 * (i / 27) ** 0.7; al = ap(u, tt, 0.3)
            if al > 0:
                d.rect(x0, y0, x0 + cw - 16, y0 + ch - 16, fill=A((176, 128, 84), al), r=10); d.rect(x0 + 40, y0 + 50, x0 + cw - 56, y0 + 62, fill=A((110, 76, 50), al), r=5)
                d.rect(x0 + 18, y0 + 14, x0 + cw - 34, y0 + 36, fill=A((240, 230, 210), al), r=4)
        elif i < 31:
            tt = 1.6 + (i - 27) * 0.4; kk = popk(t, t0 + tt)
            if kk > 0:
                al = ap(u, tt, 0.2); off = (1 - min(1, kk)) * 60
                glow_disc(d, x0 + cw / 2 - 8, y0 + ch / 2 - 8, 90, GOLD, 0.5 * al)
                d.rect(x0, y0 + off, x0 + cw - 16, y0 + ch - 16 + off, fill=A((250, 200, 90), al), r=10)
                d.text(x0 + cw / 2 - 8, y0 + ch / 2 - 8 + off, "新", 36, A(IRED, al), k=1)
    n = 27 if u < 1.6 else min(31, 27 + int((u - 1.6) / 0.4) + 1)
    if u < 1.0: n = n_old
    d.text(540, 340, f"{n} 种", 96, A(GOLD if n > 27 else (250, 230, 200), ap(u, 0, 0.2)), k=1)

# ======== 15. devel: many frogs: egg -> tadpole -> frog ;  this kind: egg -> froglet ========
def s_devel(t, d):
    t0 = T["devel"]; u = t - t0
    grad(d, (230, 240, 236), (204, 222, 214))
    d.rect(150, 330, 930, 700, fill=A((120, 180, 220), 0.6), r=40)              # top panel: pond
    d.rect(150, 780, 930, 1160, fill=A((190, 150, 100), 0.55), r=40)             # bottom panel: forest floor
    ptag(d, t, t0 + 0.05, 260, 370, "水里", (60, 120, 180), 30, WHITE)
    ptag(d, t, t0 + 1.6, 260, 820, "地上", (150, 100, 60), 30, WHITE)
    a1 = ap(u, 0.1, 0.3); a2 = ap(u, 0.6, 0.3); a3 = ap(u, 1.1, 0.3)
    for j in range(5): egg(d, 270 + (j % 3) * 30, 560 + (j // 3) * 30, 16, a1, (240, 240, 210))
    arrow(d, 360, 560, 420, 560, (60, 90, 120), a2, 8)
    tadpole(d, 480, 560, 0.75, t, a2)
    arrow(d, 640, 560, 700, 560, (60, 90, 120), a3, 8)
    ghostfrog(d, 800, 600, 0.32, t, a3, "happy", pal="grey", seed=1.0)
    b1 = ap(u, 1.7, 0.3)
    egg(d, 290, 1000, 62, b1, (246, 238, 210), k=E.ease_out_cubic(pr(u, 1.8, 2.6)))
    arrow(d, 380, 1000, 440, 1000, (120, 80, 50), ap(u, 2.2, 0.3), 8)
    gt = ap(u, 2.2, 0.3)
    if gt > 0:
        tadpole(d, 500, 1000, 0.65, t, gt * 0.35, (90, 80, 70)); xmark(d, 545, 1000, 60, (230, 60, 50), gt, pr(u, 2.3, 2.7))
    arrow(d, 640, 1000, 700, 1000, (120, 80, 50), ap(u, 2.7, 0.3), 8)
    fk = popk(t, t0 + 2.9)
    if fk > 0: ghostfrog(d, 800, 1040 + hop(u, 2.9, 60, 0.4), 0.30 * min(1.1, fk), t, ap(u, 2.9, 0.2), "happy", seed=0.5)

# ======== 16. card: 一句话学会 ========
def s_card(t, d):
    t0 = T["card"]; u = t - t0
    grad(d, (34, 54, 50), (18, 30, 28)); litter_bed(d, t, 31, 60, a=0.5, dark=0.6)
    kk = popk(t, t0 + 0.05); sc = min(1.04, 0.85 + 0.15 * kk); al = ap(u, 0.05, 0.25)
    x0, y0, x1, y1 = 540 - 380 * sc, 420, 540 + 380 * sc, 420 + 860 * sc
    sbox(d, x0, y0, x1, y1, (252, 248, 236), al, 40)
    d.rect(x0, y0, x1, y0 + 110, fill=A((232, 120, 52), al), r=40); d.rect(x0, y0 + 60, x1, y0 + 110, fill=A((232, 120, 52), al))
    d.text(540, y0 + 56, "一句话学会", 52, A(WHITE, al), k=1)
    d.text(540, y0 + 210, "直接发育", 110, A((40, 70, 60), al), k=1)
    d.text(540, y0 + 330, "跳过蝌蚪，", 48, A((80, 80, 80), al), k=1)
    d.text(540, y0 + 400, "在卵里直接长成小青蛙", 48, A((80, 80, 80), al), k=1)
    e1 = ap(u, 0.8, 0.3); e2 = ap(u, 1.4, 0.3)
    egg(d, 330, y0 + 610, 70, e1, k=E.ease_out_cubic(pr(u, 0.9, 1.6)))
    tadpole(d, 470, y0 + 610, 0.45, t, e2 * 0.3, (120, 120, 120)); xmark(d, 510, y0 + 610, 40, (230, 60, 50), e2, pr(u, 1.4, 1.8))
    arrow(d, 600, y0 + 610, 650, y0 + 610, (120, 80, 50), e2, 7)
    fk = popk(t, t0 + 2.0)
    if fk > 0: ghostfrog(d, 760, y0 + 650 + hop(u, 2.0, 50, 0.4), 0.3 * min(1.1, fk), t, ap(u, 2.0, 0.2), "happy", seed=0.1)

# ======== 17. map: South America -> Peru -> a single dot at ~2100 m ========
SAM = [(-77.5, 8.5), (-71.5, 12.4), (-63, 10.7), (-60, 8.5), (-52, 5), (-50, 0), (-44, -2.5), (-35, -5.5), (-38.5, -13), (-41, -22), (-48.5, -26),
       (-53, -34), (-57.5, -38), (-62, -39), (-65, -42), (-67.5, -46.5), (-66, -48.5), (-69, -51), (-68.5, -55), (-72, -54), (-75, -50),
       (-73.5, -43), (-73.5, -37), (-71.5, -30), (-70.3, -18.5), (-75.5, -15), (-78, -10), (-81.3, -5.5), (-80, -1), (-80, 1), (-78.5, 2.5)]
PERU = [(-81.3, -4.6), (-80.4, -3.4), (-79.0, -4.9), (-78.4, -3.4), (-75.3, -0.1), (-73.7, -1.3), (-70.0, -2.3), (-69.9, -4.3), (-72.9, -5.3),
        (-73.9, -7.4), (-72.8, -9.1), (-70.6, -9.5), (-70.5, -11.0), (-68.7, -11.1), (-69.5, -14.2), (-68.9, -16.3), (-69.6, -17.3), (-70.4, -18.3),
        (-75.5, -15.3), (-77.7, -11.5), (-79.5, -7.9), (-81.2, -6.1)]
ANDES = [(-72, 10), (-74.5, 6), (-76.5, 2), (-78.3, -1.5), (-78.3, -5.5), (-77.2, -8.5), (-75.5, -11.5), (-72.5, -14.5), (-69.5, -17.5), (-68.5, -22),
         (-69, -27), (-70, -32), (-70.5, -37), (-71.5, -42), (-73, -47), (-73.5, -52)]
CANAAN = (-77.4476, -6.8926)
def s_map(t, d):
    t0 = T["map"]; u = t - t0
    grad(d, (24, 60, 96), (14, 36, 62))
    z = 1 + 4.5 * E.ease_in_out_sine(pr(u, 1.4, 3.2))
    base = 15.0; c0 = (-60.0, -21.0)
    cx = lerp(c0[0], CANAAN[0], E.ease_in_out_sine(pr(u, 1.4, 3.2))); cy = lerp(c0[1], CANAAN[1], E.ease_in_out_sine(pr(u, 1.4, 3.2)))
    M = lambda lon, lat: (540 + (lon - cx) * base * z, 760 - (lat - cy) * base * z)
    d.poly([M(*p) for p in SAM], A((190, 176, 132), 1))
    d.poly([M(*p) for p in PERU], A((240, 200, 120), 1))
    d.line([M(*p) for p in ANDES], A((150, 112, 82), 0.85), 14 * min(z, 3.0))
    pa = ap(u, 0.3, 0.3) * (1 - pr(u, 1.4, 1.8))
    if pa > 0: px_, py_ = M(-73.0, -13.0); d.text(px_, py_, "秘鲁", 44, A((90, 60, 30), pa), k=1)
    ka = popk(t, t0 + 0.6)
    if ka > 0:
        px_, py_ = M(*CANAAN); al = ap(u, 0.6, 0.2)
        for j in range(3):
            ph = ((u * 0.8 + j / 3) % 1); d.circ(px_, py_, 20 + ph * 90, outline=A(IRED_L, al * (1 - ph)), w=5)
        d.circ(px_, py_, 18 * min(1.2, ka), fill=A(IRED, al)); d.circ(px_, py_, 7, fill=A(WHITE, al))
        if u > 3.0:
            for j in range(4):
                xx = px_ - 220 + ((u * 40 + j * 130) % 460); d.ell(xx, py_ - 30 + (j % 2) * 50, 120, 26, A(WHITE, 0.14 * ap(u, 3.0, 0.5)))
        ptag(d, t, t0 + 3.3, px_, py_ - 90, "秘鲁 · 圣马丁", (250, 244, 226), 34)
    ga = ap(u, 3.4, 0.3)                                                       # altitude gauge
    if ga > 0:
        gx, gy0, gy1 = 820, 1150, 560
        sbox(d, gx - 120, gy1 - 110, gx + 60, gy0 + 40, (20, 36, 60), 0.85 * ga, 30)
        d.rect(gx - 18, gy1, gx + 18, gy0, fill=A((230, 236, 240), 0.9 * ga), r=18)
        h = 2100 * E.ease_out_cubic(pr(u, 3.5, 4.6)); yy = lerp(gy0, gy1, h / 3000)
        d.rect(gx - 18, yy, gx + 18, gy0, fill=A((100, 190, 140), ga), r=18)
        for m in (0, 1000, 2000, 3000):
            ym = lerp(gy0, gy1, m / 3000); d.line([(gx - 34, ym), (gx - 20, ym)], A(WHITE, ga), 3); d.text(gx - 44, ym, str(m), 22, A(WHITE, ga), anchor="rm", k=1)
        d.text(gx - 30, gy1 - 60, f"约 {int(round(h, -1))} 米", 36, A(GOLD, ga), k=1)

# ======== 18. cows: a small low forest patch surrounded by cattle pasture; hoofprints ========
def s_cows(t, d):
    t0 = T["cows"]; u = t - t0
    grad(d, (170, 210, 236), (210, 228, 230), 0, 520)
    d.rect(-40, 500, 1120, 1960, fill=A((132, 186, 90), 1))
    for i in range(7): d.line([(-40, 560 + i * 110), (1120, 540 + i * 116)], A((150, 200, 104), 0.6), 6)
    for i in range(9): d.line([(i * 140 - 60, 520), (i * 140 - 60, 1300)], A((120, 96, 70), 0.0), 4)
    # forest patch (low canopy) in the middle
    cx_, cy_ = 540, 760
    d.ell(cx_, cy_ + 120, 330, 110, A((70, 100, 50), 1))
    for x, h in ((300, 220), (390, 260), (480, 240), (600, 270), (690, 230), (770, 210)):
        d.rect(x - 8, cy_ + 120 - h, x + 8, cy_ + 120, fill=A((90, 66, 48), 1))
        d.circ(x, cy_ + 120 - h, 70, fill=A((50, 110, 70), 1)); d.circ(x - 30, cy_ + 120 - h + 20, 50, fill=A((60, 128, 80), 1))
    tree_fern(d, 440, cy_ + 120, 150, t); tree_fern(d, 650, cy_ + 120, 140, t)
    for x in (340, 560, 740): bamboo(d, x, cy_ + 130, 200, t)
    ha = ap(u, 0.8, 0.3)                                                        # canopy height marker
    if ha > 0:
        d.line([(880, cy_ + 120), (880, cy_ + 120 - 270)], A(WHITE, ha), 5); d.line([(860, cy_ + 120 - 270), (900, cy_ + 120 - 270)], A(WHITE, ha), 5)
        ptag(d, t, t0 + 0.9, 820, cy_ - 190, "树冠不到 6 米", (250, 244, 226), 32)
    # cows grazing around
    for i, (x, y, f, s) in enumerate(((235, 1170, 1, 0.62), (850, 1120, -1, 0.66), (225, 680, 1, 0.48))):
        kk = ap(u, 0.1 + i * 0.25, 0.4)
        cow(d, x + f * 20 * math.sin(t * 0.4 + i) + (1 - kk) * -f * 200, y, s, t, kk, f, graze=0.5 + 0.5 * math.sin(t + i), seed=i)
    # hoofprints trail into the patch, each fades in
    ma = ap(u, 1.6, 0.4)
    for j in range(16): d.ell(330 + j * 28, 1050 + 14 * math.sin(j * 0.6 / 30 * 28), 34, 26, A((150, 132, 84), 0.8 * ma))
    rr = random.Random(7)
    for j in range(14):
        tt = 1.8 + j * 0.16; al = ap(u, tt, 0.3) * 0.85
        if al <= 0: continue
        x = 340 + j * 30 + rr.uniform(-8, 8); y = 1050 + 14 * math.sin(j * 0.6) + (16 if j % 2 else -16)
        hoof(d, x, y, 1.0, al, 0.2, (92, 66, 40))
    ptag(d, t, t0 + 2.6, 560, 1140, "牛蹄印", (110, 80, 60), 32, WHITE)

# ======== 19. end: back to the opening close-up; the eyes stay in the dark ========
def s_end(t, d):
    t0 = T["end"]; u = t - t0
    floor_night(d, t, 0.5, 1.0 - 0.6 * pr(u, 2.8, 4.0), 540, 800, 700)
    eo = E.ease_in_out_sine(pr(u, 2.6, 3.8))
    ghostfrog(d, 540, 900, 1.75, t, 1, "happy" if u < 1.6 else "calm", look=0.6 * math.sin(t * 1.5), eyes_only=0.9 * eo, glow_eyes=0.6 * eo, seed=0.5)
    ka = popk(t, t0 + 0.6)
    if ka > 0:
        al = ap(u, 0.6, 0.2) * (1 - pr(u, 3.6, 4.0))
        bubble(d, 760, 460, 200 * min(1.05, ka), 150 * min(1.05, ka), al, WHITE, (-1, 1)); d.text(760, 460, "?", 100, A(NAVYT, al), k=1)
    ra = ap(u, 1.0, 0.4)
    d.text(540, 1210, "Venegas et al. 2026 · Diversity 18:458", 24, A((230, 230, 220), 0.8 * ra), k=0)
    fo = pr(t, DUR - 0.6, DUR)
    if fo > 0: d.rect(-40, -40, 1120, 1960, fill=A((0, 0, 0), fo))
