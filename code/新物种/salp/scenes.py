# 《这只海樽只住在深海？》scenes — every subtitle line gets its OWN set. Flat 2D, no dark outlines.
# Content x 180–900, above subtitle box (y < ~1230). Entities spring in and fade >= 0.3 s.
import math, random
from PIL import Image, ImageDraw
from gchars import *
from cues import *
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
def L_(k): return nxt(k) - T[k]

# ---------------- salp character (glass barrel, no outlines) ----------------
GL = (150, 222, 255); GL_L = (214, 244, 255); GL_B = (120, 200, 240); GUT = (240, 140, 70); GUT_L = (255, 196, 130)
SEA0 = (8, 24, 50); SEA1 = (2, 6, 16); SURF = (70, 170, 225); SURF_D = (30, 96, 160)
def salp(d, x, y, s, t, a=1.0, kind="chill", look=0.0, dirn=1, glw=0.35, ph=0.0, nf=False):
    if a <= 0.01 or s <= 0.01: return
    p = math.sin(t * 3.2 + ph)                          # jet-pulse breathing
    rx, ry = 150 * s * (1 - 0.035 * p), 92 * s * (1 + 0.05 * p)
    glow_disc(d, x, y, rx * 1.25, GL, glw * a)
    d.ell(x, y, rx, ry, fill=A(GL, 0.30 * a))
    d.ell(x + dirn * rx * 0.05, y - ry * 0.08, rx * 0.86, ry * 0.74, fill=A(GL_L, 0.16 * a))
    for j in range(5):                                  # muscle bands
        bx = x + (j - 2) * rx * 0.34
        hh = ry * math.sqrt(max(0.05, 1 - ((bx - x) / rx) ** 2)) * 0.96
        d.line([(bx - 6 * s, y - hh), (bx + 6 * s, y), (bx - 6 * s, y + hh)], A(GL_L, 0.42 * a), max(2, 7 * s))
    d.ell(x + dirn * rx * 0.96, y, rx * 0.10, ry * 0.46, fill=A(GL_L, 0.35 * a))      # mouth siphon
    d.ell(x - dirn * rx * 0.97, y, rx * 0.07, ry * 0.30, fill=A(GL_L, 0.30 * a))      # atrial siphon
    gx = x - dirn * rx * 0.55; gy = y + ry * 0.18
    d.circ(gx, gy, 24 * s, fill=A(GUT, 0.92 * a)); d.circ(gx - 7 * s, gy - 8 * s, 8 * s, fill=A(GUT_L, 0.9 * a))
    d.arc(x - dirn * rx * 0.1, y - ry * 0.25, rx * 0.7, ry * 0.55, 200, 300, A(WHITE, 0.55 * a), max(2, 6 * s))   # sheen
    if not nf: face(d, x + dirn * rx * 0.32, y - ry * 0.05, ry * 0.9, kind, a, look)
def chain(d, x0, y0, n, s, t, a=1.0, dirn=1, gap=None, amp=26, t_in=None, kinds=("happy", "chill"), sway=1.5):
    """small clones trailing BEHIND a parent at (x0,y0) facing dirn. t_in[i] = pop time per clone."""
    gap = gap or 210 * s; pts = []
    for i in range(n):
        x = x0 - dirn * (i + 1) * gap; y = y0 + amp * math.sin(t * sway - (i + 1) * 0.7)
        pts.append((x, y))
    prev = (x0 - dirn * gap * 0.4, y0)
    for i, (x, y) in enumerate(pts):
        k = 1.0; al = a
        if t_in is not None:
            k = popk(t, t_in[i], "bouncy"); al = a * ap(t, t_in[i], 0.3)
            if k <= 0: break
        d.line([prev, (x + dirn * gap * 0.35, y)], A(GL_L, 0.35 * al), max(2, 8 * s))
        salp(d, x, y, s * 0.62 * min(1.1, k), t, al, kinds[i % len(kinds)], 0.3 * dirn, dirn, 0.25, ph=i * 0.9)
        prev = (x - dirn * gap * 0.3, y)
def snow(d, t, a=1.0, n=60, seed=5, sp=(18, 40), box=(0, 240, 1080, 1700)):
    rr = random.Random(seed)
    for i in range(n):
        x0 = rr.uniform(box[0], box[2]); y0 = rr.uniform(0, 3000); v = rr.uniform(*sp); r = rr.uniform(1.6, 4.2)
        y = box[1] + (y0 + t * v) % (box[3] - box[1]); x = x0 + 14 * math.sin(t * 0.5 + i)
        d.circ(x, y, r, fill=A((210, 230, 240), a * rr.uniform(0.25, 0.6)))
def deep(d, t, top=SEA0, bot=SEA1, a=1.0, seed=5):
    grad(d, top, bot); snow(d, t, a, seed=seed)
def qmark(d, t, t0, x, y, size=90, col=GOLD):
    k = popk(t, t0, "bouncy")
    if k <= 0: return
    d.text(x, y + hop(t, t0, 30, 0.4), "?", int(size * min(1.1, k)), A(col, ap(t, t0, 0.3)), k=1)
def heart(d, x, y, r, col, a):
    d.circ(x - r * 0.5, y - r * 0.2, r * 0.55, fill=A(col, a)); d.circ(x + r * 0.5, y - r * 0.2, r * 0.55, fill=A(col, a))
    d.poly([(x - r * 1.02, y), (x + r * 1.02, y), (x, y + r * 1.1)], A(col, a))
def blob(d, x, y, rx, ry, col, a):   # faint unknown silhouette
    d.ell(x, y, rx, ry, fill=A(col, a))

# ======== 1. hook: glass barrel glides in, BIG1 ========
def s_hook(t, d):
    u = t
    deep(d, t)
    spot(d, 540, 760, 640, 0.9, (120, 200, 255))
    k = popk(t, -0.2, "bouncy")
    x = lerp(760, 540, E.ease_out_cubic(pr(u, -0.2, 1.3)))
    salp(d, x, 760 + 10 * math.sin(t * 1.6), 1.6 * min(1.12, k), t, 1, "scared" if u < 1.6 else "happy", 0.5, 1, 0.55)
    v = pr(u, 0.9, 1.7)
    if 0 < v < 1:
        sx = lerp(260, 820, v); d.poly([(sx - 30, 620), (sx + 20, 620), (sx - 10, 900), (sx - 60, 900)], A(WHITE, 0.35 * math.sin(math.pi * v)))
    zap(d, 540, 760, t, 0.0, GL_L, 600, 0.8)
    bigword(d, t, 0.0, 540, 440, "玻璃桶？", 170, GOLD, 3.4)

# ======== 2. tail: a string of little clones pops in behind ========
TAIL_T = [T["tail"] + 0.3 + i * 0.28 for i in range(6)]
def s_tail(t, d):
    t0 = T["tail"]; u = t - t0
    deep(d, t, seed=6)
    px = lerp(800, 780, eio(pr(u, 0, 3)))
    salp(d, px, 640, 0.75, t, 1, "proud", 0.4, 1, 0.45)
    chain(d, px - 50, 680, 6, 0.6, t, 1, 1, 92, 40, TAIL_T)
    for i, tt in enumerate(TAIL_T):
        if 0 <= t - tt < 0.6: d.text(px - 50 - (i + 1) * 92, 590 - (t - tt) * 120, "+1", 40, A(GOLD, 1 - (t - tt) / 0.6), k=1)

# ======== 3. q: bright surface home above, our salp alone deep below ========
def s_q(t, d):
    t0 = T["q"]; u = t - t0
    deep(d, t, seed=7)
    grad(d, SURF, SURF_D, 0, 560)
    for i in range(5):
        xx = 220 + i * 160 + 30 * math.sin(t + i); d.poly([(xx, 240), (xx + 50, 240), (xx + 140, 560), (xx + 60, 560)], A(WHITE, 0.07))
    d.line([(x, 250 + 10 * math.sin(x * 0.02 + t * 2)) for x in range(-20, 1110, 20)], A(WHITE, 0.6), 6)
    for i in range(3):
        k = popk(t, t0 + 0.2 + i * 0.15)
        if k > 0: salp(d, 330 + i * 200, 420 + 12 * math.sin(t * 2 + i), 0.42 * min(1.1, k), t, ap(t, t0 + 0.2 + i * 0.15), "happy", 0, 1, 0.2, ph=i)
    dashed(d, [(540, 580), (540, lerp(580, 930, eio(pr(u, 0.6, 1.8))))], GOLD, 0.8, 6)
    if u > 0.6: d.poly([(518, lerp(580, 930, eio(pr(u, 0.6, 1.8)))), (562, lerp(580, 930, eio(pr(u, 0.6, 1.8)))), (540, lerp(580, 930, eio(pr(u, 0.6, 1.8))) + 30)], A(GOLD, 0.9))
    salp(d, 540, 1080 + 8 * math.sin(t * 1.5), 0.8, t, ap(u, 0.3, 0.3), "sus", -0.3, -1, 0.5)
    for i, (qx, qy) in enumerate(((330, 980), (760, 960), (700, 1180))): qmark(d, t, t0 + 1.6 + i * 0.35, qx, qy, 90)
    ptag(d, t, t0 + 0.1, 790, 320, "海面", (240, 250, 255), 34)

# ======== 4. BIG2: plunge — depth ticks race upward, ONLY DEEP ========
def s_big2(t, d):
    t0 = T["big2"]; u = t - t0
    grad(d, (6, 16, 40), (0, 2, 8)); snow(d, t * 3, 0.9, seed=9, sp=(60, 120))
    off = (u * 420) % 90
    d.rect(205, 260, 225, 1240, fill=A(GL, 0.25))
    for j in range(13):
        yy = 270 + j * 90 - off
        if 260 < yy < 1240: d.rect(205, yy - 3, 250 if j % 2 else 270, yy + 3, fill=A(GL_L, 0.6))
    y = lerp(640, 800, E.ease_out_cubic(pr(u, 0, 1.5)))
    rings(d, 560, y, t, [t0], GL_L, 0.8, 560)
    salp(d, 580, y, 1.25 * min(1.1, popk(t, t0, "bouncy")), t, 1, "proud", 0, 1, 0.8)
    bigword(d, t, t0, 560, 400, "只住深海", 165, GOLD)
    ptag(d, t, t0 + 1.2, 580, 1090, "No.1", GOLD, 64)

# ======== 5. depth: depth column with zones, 280–2200 m band ========
def ym(m): return 300 + m * 0.3
def s_depth(t, d):
    t0 = T["depth"]; u = t - t0
    deep(d, t, seed=10, a=0.6)
    cx0, cx1 = 330, 450
    d.rect(cx0, ym(0), cx1, ym(200), fill=A(SURF, 1))
    d.rect(cx0, ym(200), cx1, ym(1000), fill=A((26, 70, 130), 1))
    d.rect(cx0, ym(1000), cx1, ym(3000), fill=A((10, 22, 52), 1))
    for m in range(0, 3001, 500): d.rect(cx1, ym(m) - 2, cx1 + 18, ym(m) + 2, fill=A(WHITE, 0.6))
    sa = 1 - 0.7 * pr(u, 0.2, 2.0)
    glow_disc(d, 260, 330, 70, (255, 230, 140), 0.9 * sa); d.circ(260, 330, 30, fill=A((255, 226, 120), sa))
    for i in range(4): d.line([(cx0 + 20 + i * 25, ym(0)), (cx0 + 30 + i * 25, ym(200 + 300 * sa))], A((255, 240, 180), 0.35 * sa), 6)
    kb = eio(pr(u, 0.5, 1.6))
    if kb > 0:
        yb = ym(280); ye = lerp(yb, ym(2200), kb)
        d.rect(cx0 - 8, yb, cx1 + 8, ye, fill=A(GL, 0.22))
        d.rect(cx1 + 30, yb, cx1 + 40, ye, fill=A(GOLD, 1)); d.rect(cx1 + 30, yb - 3, cx1 + 60, yb + 5, fill=A(GOLD, 1)); d.rect(cx1 + 30, ye - 5, cx1 + 60, ye + 3, fill=A(GOLD, 1))
    ptag(d, t, t0 + 0.6, 610, ym(280), "280 m", GOLD, 40)
    ptag(d, t, t0 + 1.6, 620, ym(2200), "2200 m", GOLD, 40)
    yy = ym(lerp(600, 1700, 0.5 + 0.5 * math.sin((u - 1.6) * 0.9))) if u > 1.6 else ym(lerp(280, 600, eio(pr(u, 1.0, 1.6))))
    salp(d, 770, yy, 0.42, t, ap(u, 0.8, 0.3), "chill", 0, -1, 0.5)
    ptag(d, t, t0 + 2.2, 255, ym(600), "暮光层", (80, 130, 200), 28, WHITE)
    ptag(d, t, t0 + 2.5, 255, ym(1500), "午夜层", (40, 60, 110), 28, WHITE)

# ======== 6. fifty: ~50 species crowd the bright surface; ours alone below ========
def s_fifty(t, d):
    t0 = T["fifty"]; u = t - t0
    deep(d, t, seed=11, a=0.5)
    grad(d, SURF, SURF_D, 260, 720)
    d.line([(x, 268 + 8 * math.sin(x * 0.02 + t * 2)) for x in range(-20, 1110, 20)], A(WHITE, 0.6), 6)
    n = 0
    for i in range(50):
        r_, c_ = divmod(i, 10); tt = t0 + 0.15 + i * 0.04
        k = popk(t, tt, "snappy")
        if k <= 0: continue
        n += 1
        salp(d, 228 + c_ * 70 + (r_ % 2) * 16, 360 + r_ * 70 + 5 * math.sin(t * 2 + i), 0.17 * min(1.1, k), t, ap(t, tt, 0.3), "happy", 0, 1 if (i % 3) else -1, 0.0, ph=i, nf=True)
    al = ap(u, 0.1, 0.2)
    if al > 0:
        sbox(d, 400, 750, 680, 850, (10, 30, 60), 0.85 * al, 30); d.text(540, 800, f"≈{n}", 70, A(GOLD, al), k=1)
    salp(d, 540, 1100 + 8 * math.sin(t * 1.3), 0.7, t, ap(u, 0.8, 0.4), "sad", -0.5, -1, 0.55)
    spot(d, 540, 1100, 260, 0.7, (120, 200, 255))

# ======== 7. slow: speed gauge stuck near 'slow', salp yawns along ========
def s_slow(t, d):
    t0 = T["slow"]; u = t - t0
    deep(d, t, seed=12)
    cx, cy, R = 540, 560, 230
    d.arc(cx, cy, R, R, 180, 360, A((40, 70, 110), 1), 34)
    d.arc(cx, cy, R, R, 180, 215, A(GL, 1), 34)
    for j in range(7):
        an = math.pi + j * math.pi / 6; d.line([(cx + math.cos(an) * (R - 30), cy + math.sin(an) * (R - 30)), (cx + math.cos(an) * (R - 60), cy + math.sin(an) * (R - 60))], A(WHITE, 0.6), 5)
    ang = math.pi + lerp(0.9, 0.22, E.ease_out_back(pr(u, 0.2, 1.0))) + 0.04 * math.sin(t * 5)
    d.line([(cx, cy), (cx + math.cos(ang) * (R - 50), cy + math.sin(ang) * (R - 50))], A(GOLD, 1), 12); d.circ(cx, cy, 20, fill=A(GOLD, 1))
    d.text(cx - R + 10, cy + 50, "慢", 40, A(GL_L, 1), k=1); d.text(cx + R - 10, cy + 50, "快", 40, A((120, 140, 170), 1), k=1)
    x = lerp(330, 600, pr(u, 0, L_("slow")))
    salp(d, x, 960, 0.75, t, ap(u, 0.1, 0.3), "chill" if (u % 1.6) < 1.1 else "happy", 0, 1, 0.4)
    for i in range(3):
        v = (u - 0.5 - i * 0.5) % 1.5
        if u > 0.5 + i * 0.5: d.text(x + 150 + v * 40, 860 - v * 80, "z", 44 - i * 6, A(GL_L, 0.8 * (1 - v / 1.5)), k=1)
    al = ap(u, 1.2, 0.3)                                     # battery barely used
    if al > 0:
        sbox(d, 700, 1080, 860, 1160, (30, 50, 80), al, 14); d.rect(860, 1105, 874, 1135, fill=A((30, 50, 80), al), r=4)
        d.rect(712, 1092, 712 + 136 * lerp(1, 0.93, pr(u, 1.2, 3.0)), 1148, fill=A((110, 230, 150), al), r=8)

# ======== 8. chain: clones bud from the parent's rear one by one ========
CH_T = [T["chain"] + 0.4 + i * 0.4 for i in range(6)]
def s_chain(t, d):
    t0 = T["chain"]; u = t - t0
    deep(d, t, seed=13)
    px, py = 760, 520
    for i, tt in enumerate(CH_T):                     # each clone slides out along a curved path
        k = popk(t, tt, "bouncy")
        if k <= 0: continue
        prog = min(1, (t - tt) / 0.6)
        s_ = (i + 1) - (1 - prog)
        x = px - 150 - s_ * 68; y = py + 60 + s_ * 75 + 20 * math.sin(t * 1.5 - i)
        if i > 0 or prog > 0.3: d.line([(x + 40, y - 30), (x + 68, y - 75)], A(GL_L, 0.35), 6)
        salp(d, x, y, 0.42 * min(1.1, k), t, ap(t, tt, 0.3), "happy", 0.3, 1, 0.25, ph=i)
        if 0 <= t - tt < 0.5: zap(d, px - 140, py + 40, t, tt, GL_L, 160, 0.6)
    salp(d, px, py, 0.8, t, 1, "proud", 0.5, 1, 0.5)
    ptag(d, t, t0 + 0.4, 700, 340, "复制 ×N", GOLD, 40)

# ======== 9. twenty: serpentine chain fills, counter to 20 ========
def tw_pos(i):
    r_, c_ = divmod(i, 7); c2 = c_ if r_ % 2 == 0 else 6 - c_
    return 830 - c2 * 105, 520 + r_ * 190
TW_T = [T["twenty"] + 0.2 + i * 0.09 for i in range(20)]
def s_twenty(t, d):
    t0 = T["twenty"]; u = t - t0
    deep(d, t, seed=14)
    n = 0
    for i, tt in enumerate(TW_T):
        k = popk(t, tt, "bouncy")
        if k <= 0: continue
        n += 1; x, y = tw_pos(i); y += 10 * math.sin(t * 2 - i * 0.5)
        if i > 0:
            x2, y2 = tw_pos(i - 1); d.line([(x2, y2), (x, y)], A(GL_L, 0.3 * ap(t, tt, 0.3)), 5)
        salp(d, x, y, 0.27 * min(1.1, k), t, ap(t, tt, 0.3), "happy", 0, -1 if (i // 7) % 2 == 0 else 1, 0.2, ph=i, nf=i > 0)
    al = ap(u, 0.15, 0.2)
    if al > 0: d.text(540, 360, f"×{n}", 140, A(GOLD, al), k=1)

# ======== 10. twins: x-ray close-up of one clone, two embryos with heartbeats ========
def s_twins(t, d):
    t0 = T["twins"]; u = t - t0
    deep(d, t, seed=15)
    spot(d, 540, 720, 520, 0.8, (255, 180, 210))
    salp(d, 540, 700, 1.75, t, 1, "happy", 0.3, -1, 0.5)
    for j, (ex, ey) in enumerate(((470, 760), (590, 760))):
        k = popk(t, t0 + 0.5 + j * 0.3, "bouncy")
        if k <= 0: continue
        hb = pulse(t, [t0 + 0.8 + j * 0.25 + n * 0.75 for n in range(6)], 9)
        r = 42 * min(1.1, k) * (1 + 0.12 * hb)
        glow_disc(d, ex, ey, r * 1.6, (255, 170, 200), 0.6 * ap(t, t0 + 0.5 + j * 0.3))
        d.circ(ex, ey, r, fill=A((255, 176, 204), ap(t, t0 + 0.5 + j * 0.3)))
        face(d, ex, ey, r, "chill", ap(t, t0 + 0.5 + j * 0.3))
        if hb > 0.2: heart(d, ex, ey - 80, 14 * hb + 6, (255, 110, 150), hb)
    bigword(d, t, t0 + 1.2, 540, 420, "×2", 160, GOLD)

# ======== 11. gemini: twin stars draw the Gemini constellation + name card ========
GEM = [(400, 380), (420, 520), (400, 660), (360, 820), (440, 820), (660, 400), (650, 540), (680, 680), (620, 830), (720, 830)]
GEML = [(0, 1), (1, 2), (2, 3), (2, 4), (5, 6), (6, 7), (7, 8), (7, 9), (1, 6)]
def s_gemini(t, d):
    t0 = T["gemini"]; u = t - t0
    grad(d, (10, 20, 52), (2, 6, 18)); snow(d, t, 0.5, seed=16)
    for i, (a_, b_) in enumerate(GEML):
        k = eio(pr(u, 0.2 + i * 0.12, 0.5 + i * 0.12))
        if k > 0:
            (x0, y0), (x1, y1) = GEM[a_], GEM[b_]; d.line([(x0, y0), (lerp(x0, x1, k), lerp(y0, y1, k))], A(GL_L, 0.55), 4)
    for i, (x, y) in enumerate(GEM):
        al = ap(u, 0.1 + i * 0.06, 0.3); big_ = i in (0, 5)
        if al <= 0: continue
        tw = 0.8 + 0.2 * math.sin(t * 4 + i)
        glow_disc(d, x, y, 60 if big_ else 26, (255, 236, 170), 0.7 * al * tw); d.circ(x, y, (16 if big_ else 7) * tw, fill=A((255, 246, 210), al))
    al = ap(u, 1.1, 0.3); kk = popk(t, t0 + 1.1)
    if al > 0:
        yy = 1010 + (1 - min(1, kk)) * 40
        sbox(d, 240, yy - 70, 840, yy + 70, (250, 246, 232), al, 26)
        d.text(540, yy - 18, "Vitreosalpa gemini", 46, A(NAVYT, al), k=1); d.text(540, yy + 38, "gemini = 双子", 30, A((90, 96, 120), al), k=1)

# ======== 12. robot: ROV spotlight finds the salp, REC frame, 20+ years ========
def s_robot(t, d):
    t0 = T["robot"]; u = t - t0
    deep(d, t, (4, 14, 34), (0, 3, 10), seed=17)
    rx = lerp(980, 700, E.ease_out_cubic(pr(u, 0, 1.0))); ry = 420 + 8 * math.sin(t * 1.8)
    lit = ap(u, 0.8, 0.3)
    sx, sy = 380, 900
    if lit > 0:
        d.poly([(rx - 120, ry + 40), (rx - 100, ry + 100), (sx + 200, sy + 160), (sx - 200, sy - 120)], A((255, 250, 210), 0.13 * lit))
        spot(d, sx, sy, 280, lit, (255, 250, 220))
    salp(d, sx, sy, 0.75, t, 0.35 + 0.65 * lit, "scared" if 0.8 < u < 1.8 else "happy", 0.6, 1, 0.3 + 0.4 * lit)
    sbox(d, rx - 110, ry - 90, rx + 150, ry + 90, (255, 200, 50), 1, 20)                 # ROV body
    d.rect(rx - 110, ry - 90, rx + 150, ry - 50, fill=A((240, 120, 50), 1), r=16)
    d.circ(rx - 110, ry + 40, 36, fill=A((60, 70, 90), 1)); d.circ(rx - 110, ry + 40, 22, fill=A((140, 210, 255), 1))
    for j in (0, 1): d.circ(rx - 60 + j * 70, ry + 100, 16, fill=A((255, 250, 200), 0.4 + 0.6 * lit))
    d.rect(rx + 150, ry - 30, rx + 190, ry + 30, fill=A((90, 100, 120), 1), r=8)
    for j in range(3): d.line([(rx + 195, ry - 25 + j * 25), (rx + 195 + 12 * math.sin(t * 30 + j), ry - 25 + j * 25)], A(GL_L, 0.5), 4)
    if lit > 0:
        c = 160
        for ax, ay in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            d.line([(sx + ax * c, sy + ay * (c - 40)), (sx + ax * c, sy + ay * c), (sx + ax * (c - 40), sy + ay * c)], A(WHITE, lit), 6)
        if math.sin(t * 6) > 0: d.circ(sx - c + 20, sy - c - 30, 12, fill=A((255, 70, 70), lit))
        d.text(sx - c + 80, sy - c - 30, "REC", 30, A(WHITE, lit), k=1)
    bigword(d, t, t0 + 1.8, 560, 1150, "20+ 年前", 90, GOLD)

# ======== 13. name: salp family tree sprouts a brand-new golden branch ========
def s_name(t, d):
    t0 = T["name"]; u = t - t0
    deep(d, t, seed=18, a=0.6)
    d.line([(540, 1200), (540, 900)], A((90, 130, 170), 1), 18)
    olds = [(300, 620), (420, 520), (540, 480), (660, 540)]
    for i, (x, y) in enumerate(olds):
        d.line([(540, 900), (540, 820), (x, y + 60)], A((90, 130, 170), 1), 12)
        salp(d, x, y, 0.3, t, 1, "chill", 0, 1, 0.1, ph=i, nf=True)
    k = eio(pr(u, 0.4, 1.4))
    if k > 0:
        ex, ey = lerp(540, 790, k), lerp(900, 700, k)
        d.line([(540, 900), (ex, ey)], A(GOLD, 1), 14)
        kk = popk(t, t0 + 1.4, "bouncy")
        if kk > 0:
            glow_disc(d, 790, 640, 120, GOLD, 0.5 * ap(t, t0 + 1.4))
            salp(d, 790, 640, 0.45 * min(1.1, kk), t, ap(t, t0 + 1.4), "proud", 0, -1, 0.4)
    ptag(d, t, t0 + 1.8, 720, 520, "Vitreosalpa", GOLD, 40)
    kk = popk(t, t0 + 2.6, "bouncy")
    if kk > 0:
        al = ap(t, t0 + 2.6, 0.3)
        sbox(d, 230, 1020, 470, 1120, (230, 80, 70), 0.9 * al, 20); d.text(350, 1070, "2026", int(56 * min(1.1, kk)), A(WHITE, al), k=1)

# ======== 14. end: pull back — the big dark ocean, many nameless silhouettes ========
def s_end(t, d):
    t0 = T["end"]; u = t - t0
    deep(d, t, seed=19)
    rr = random.Random(4)
    for i in range(9):
        x, y = rr.uniform(220, 860), rr.uniform(330, 1150); rx_, ry_ = rr.uniform(30, 70), rr.uniform(20, 45)
        al = ap(u, 0.4 + i * 0.25, 0.4) * (0.5 + 0.2 * math.sin(t * 2 + i))
        if al <= 0: continue
        blob(d, x + 10 * math.sin(t + i), y, rx_, ry_, (60, 110, 160), al * 0.7)
        d.text(x + 10 * math.sin(t + i), y, "?", int(ry_ * 1.5), A(GOLD, al), k=1)
    s = lerp(0.8, 0.45, eio(pr(u, 0, 2.0)))
    x = lerp(620, 520, pr(u, 0, L_("end")))
    salp(d, x, 760, s, t, 1, "happy", 0.4, 1, 0.5)
    chain(d, x - 60 * s / 0.8, 800, 5, s * 0.9, t, 1, 1, 150 * s / 0.8, 25)
