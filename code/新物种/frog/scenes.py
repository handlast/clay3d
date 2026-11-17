# 《爱吃蜗牛的小角蟾》v2 scenes — every subtitle line gets its OWN set, composition and demo (user 2026-11-16).
# Flat 2D, no dark outlines (eye/mouth lines only). Content in x 180–900, above the subtitle box (y < ~1220) except card.
import math, random
from PIL import Image
from fchars import *
from cues import *

# ---------------- small helpers ----------------
def popk(t, t0, preset="snappy"): return max(0.0, E.spring_at(t, t0, 0, 1, preset)) if t >= t0 else 0.0
def ap(t, t0, d=0.12): return cl((t - t0) / d)
def tag(d, x, y, s, col, a=1.0, size=40, tc=NAVYT):
    if a <= 0.01: return
    w = d.tlen(s, size, 1) + 44
    d.rect(x - w / 2, y - size * 0.78, x + w / 2, y + size * 0.78, fill=A(col, 0.95 * a), r=size * 0.6)
    d.text(x, y, s, size, A(tc, a), k=1)
def ptag(d, t, t0, x, y, s, col, size=40, tc=NAVYT, t1=None):
    k = popk(t, t0)
    if t1 is not None: k *= 1 - pr(t, t1 - 0.15, t1)
    if k > 0: tag(d, x, y + (1 - min(k, 1)) * 30, s, col, min(1, ap(t, t0)) * (1 if t1 is None else 1 - pr(t, t1 - 0.15, t1)), int(size * (0.6 + 0.4 * min(1.1, k))), tc)
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
def grid(d, col, a, step=90, t=0.0, speed=20):
    for i in range(-1, 14): d.line([(i * step + (t * speed) % step, 0), (i * step + (t * speed) % step, 1920)], A(col, a), 2)
    for j in range(-1, 23): d.line([(0, j * step), (1080, j * step)], A(col, a), 2)
def hop(t, t0, h=60, dur=0.35):
    u = (t - t0) / dur
    return -h * 4 * u * (1 - u) if 0 <= u <= 1 else 0.0
def dashed(d, pts, col, a, w=4, on=14, off=10):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0); n = int(L // (on + off)) + 1
        for i in range(n):
            u0 = i * (on + off) / L; u1 = min(1, (i * (on + off) + on) / L)
            if u0 < 1: d.line([(lerp(x0, x1, u0), lerp(y0, y1, u0)), (lerp(x0, x1, u1), lerp(y0, y1, u1))], A(col, a), w)
def dbox(d, x0, y0, x1, y1, col, a, w=4): dashed(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], col, a, w)
def fireflies(d, t, n=16, seed=11, a=1.0, box=(80, 300, 1000, 1150)):
    rr = random.Random(seed)
    for i in range(n):
        x0, y0, ph = rr.uniform(box[0], box[2]), rr.uniform(box[1], box[3]), rr.uniform(0, 6.28)
        x = x0 + 30 * math.sin(t * 0.7 + ph); y = y0 + 20 * math.sin(t * 0.9 + ph * 1.3)
        b = 0.5 + 0.5 * math.sin(t * 2.3 + ph * 2)
        glow_disc(d, x, y, 26, (220, 255, 150), 0.7 * b * a); d.circ(x, y, 4, fill=A((240, 255, 200), (0.5 + 0.5 * b) * a))

# ---------------- people (flat, no outlines) ----------------
SKIN = (232, 186, 146); SKIN_D = (196, 146, 108)
def scientist(d, x, y, s, t, a=1.0, walk=0.0, beam=0.0, beam_ang=0.35, night=1.0):
    """side view walking right; (x,y)=feet. beam: headlamp cone strength."""
    dk = lambda c: mix(c, (14, 20, 40), 0.55 * night)
    ph = t * 6 * walk
    hx, hy = x + 6 * s, y - 330 * s
    if beam > 0:
        L = 760 * s
        for j in range(5):
            sp = 0.20 - j * 0.035
            p1 = (hx + 30 * s + math.cos(beam_ang - sp) * L, hy + math.sin(beam_ang - sp) * L)
            p2 = (hx + 30 * s + math.cos(beam_ang + sp) * L, hy + math.sin(beam_ang + sp) * L)
            d.poly([(hx + 30 * s, hy - 8 * s), p1, p2], A((255, 244, 190), 0.06 * beam))
    for sd, c in ((1, (40, 46, 64)), (-1, (54, 62, 84))):            # legs
        sw = math.sin(ph + (0 if sd > 0 else math.pi)) * 0.45 * walk
        kx, ky = x + math.sin(sw) * 70 * s, y - 80 * s
        d.line([(x, y - 160 * s), (kx, ky), (kx + math.sin(sw) * 40 * s, y)], A(dk(c), a), 30 * s)
        d.ell(kx + math.sin(sw) * 40 * s + 14 * s, y - 4 * s, 26 * s, 12 * s, A(dk((60, 50, 40)), a))
    d.rect(x - 70 * s, y - 300 * s, x - 10 * s, y - 170 * s, fill=A(dk((150, 96, 56)), a), r=16 * s)   # backpack
    d.rect(x - 34 * s, y - 290 * s, x + 46 * s, y - 150 * s, fill=A(dk((80, 128, 98)), a), r=26 * s)   # jacket
    sw = math.sin(ph) * 0.4 * walk
    d.line([(x + 6 * s, y - 270 * s), (x + 6 * s + math.sin(-sw) * 50 * s, y - 200 * s), (x + 60 * s, y - 210 * s)], A(dk((70, 116, 88)), a), 22 * s)
    d.circ(hx, hy, 42 * s, fill=A(dk(SKIN), a))
    d.ell(hx - 4 * s, hy - 30 * s, 52 * s, 22 * s, A(dk((70, 120, 90)), a)); d.rect(hx - 4 * s, hy - 34 * s, hx + 62 * s, hy - 22 * s, fill=A(dk((70, 120, 90)), a), r=6 * s)
    d.circ(hx + 24 * s, hy - 4 * s, 5 * s, fill=A(INK, a))
    lx, ly = hx + 34 * s, hy - 14 * s                                  # headlamp
    if beam > 0: glow_disc(d, lx, ly, 46 * s, (255, 240, 170), 0.9 * beam)
    d.circ(lx, ly, 10 * s, fill=A((255, 250, 220) if beam > 0 else (180, 180, 170), a))

def villager(d, x, y, s, t, a=1.0, point=0.0):
    """front view, (x,y)=feet. point 0..1 raises right arm toward +x."""
    d.ell(x, y, 90 * s, 14 * s, A((0, 0, 0), 0.2 * a))
    d.poly([(x - 60 * s, y - 10 * s), (x + 60 * s, y - 10 * s), (x + 44 * s, y - 170 * s), (x - 44 * s, y - 170 * s)], A((52, 52, 76), a))   # wrap skirt
    for j in range(3): d.rect(x - 56 * s + j * 4 * s, y - 60 * s - j * 40 * s, x + 56 * s - j * 4 * s, y - 50 * s - j * 40 * s, fill=A((210, 70, 70), a * 0.8))
    d.poly([(x - 66 * s, y - 160 * s), (x + 66 * s, y - 160 * s), (x + 50 * s, y - 300 * s), (x - 50 * s, y - 300 * s)], A((236, 236, 226), a))  # shawl
    for j in range(4): d.rect(x - 60 * s + j * 2 * s, y - 180 * s - j * 30 * s, x + 60 * s - j * 2 * s, y - 172 * s - j * 30 * s, fill=A((200, 60, 60), a))
    d.line([(x - 48 * s, y - 280 * s), (x - 70 * s, y - 200 * s), (x - 56 * s, y - 150 * s)], A((236, 236, 226), a), 26 * s)
    ang = lerp(1.25, -0.25, ease(point)); ex, ey = x + 48 * s, y - 280 * s
    hx_, hy_ = ex + math.cos(ang) * 120 * s, ey + math.sin(ang) * 120 * s
    d.line([(ex, ey), (hx_, hy_)], A((236, 236, 226), a), 26 * s); d.circ(hx_, hy_, 15 * s, fill=A(SKIN_D, a))
    d.rect(x - 14 * s, y - 330 * s, x + 14 * s, y - 300 * s, fill=A(SKIN_D, a))
    hy = y - 370 * s
    d.circ(x, hy, 52 * s, fill=A(SKIN_D, a))
    d.ell(x, hy - 30 * s, 56 * s, 30 * s, A((30, 26, 30), a)); d.circ(x, hy - 76 * s, 24 * s, fill=A((30, 26, 30), a))   # hair + bun
    for sd in (-1, 1): d.arc(x + sd * 18 * s, hy + 2 * s, 9 * s, 7 * s, 200, 340, A(INK, a), 4 * s)
    d.arc(x, hy + 20 * s, 16 * s, 10 * s, 20, 160, A(INK, a), 4 * s)

def fingertip(d, x, y, s, a=1.0):
    """finger pointing down-left; (x,y)=tip"""
    ang = -2.3; c, sn = math.cos(ang), math.sin(ang)
    P2 = lambda u, v: (x + (u * c - v * sn) * s, y + (u * sn + v * c) * s)
    d.poly([P2(-10, -48), P2(-10, 48), P2(-600, 70), P2(-600, -70)], A(SKIN, a)); d.circ(x, y, 48 * s, fill=A(SKIN, a))
    nail = [P2(-14 + 8 * math.cos(q), 26 * math.sin(q)) for q in [i * math.pi / 10 - math.pi / 2 for i in range(11)]]
    d.poly([P2(-70, -28), P2(-70, 28)] + nail[::-1], A((250, 214, 196), a))
    d.line([P2(-160, -40), P2(-160, 30)], A(SKIN_D, a * 0.7), 5 * s)

def tongue_line(d, x0, y0, x1, y1, k, a=1.0, w=14):
    if k <= 0: return
    xe, ye = lerp(x0, x1, k), lerp(y0, y1, k)
    d.line([(x0, y0), (xe, ye)], A(PINKM, a), w); d.circ(xe, ye, w * 0.9, fill=A(PINKM, a))

# ---------------- S1/S16: Himalayan rainforest at night ----------------
FX_, FY_ = 540, 900
def rainforest(d, t, rain=0.6, beam=1.0, xr=False):
    if xr:
        grad(d, (8, 22, 66), (2, 8, 28)); grid(d, XR, 0.10, 90, t, 0)
        tc = [(30, 70, 160), (44, 96, 200)]; leaf = [(36, 84, 180), (50, 110, 220)]
    else:
        grad(d, (16, 36, 56), (6, 16, 20))
        glow_disc(d, 820, 360, 170, (230, 240, 210), 0.5); d.circ(820, 360, 58, fill=A((236, 240, 220), 1)); d.circ(800, 346, 14, fill=A((210, 216, 196), 1))
        mtn(d, 0, [(26, 52, 66)], 1, seed=21, amp=220, y0=760)
        tc = [(14, 34, 38), (24, 50, 46)]; leaf = [(36, 92, 58), (52, 118, 72)]
    for i in range(8):                                      # far trunks
        xx = 30 + i * 150 + 30 * math.sin(i * 2.1)
        d.rect(xx - 16, 0, xx + 16, 1400, fill=A(tc[0], 0.75))
    for i in range(4): d.ell(160 + i * 260, 760 + 40 * math.sin(i + t * 0.3), 320, 50, A((150, 190, 180) if not xr else XR, 0.06))
    for xx, w_ in ((70, 70), (1010, 80)):                    # near trunks with moss + vines
        d.rect(xx - w_, -20, xx + w_, 1500, fill=A(tc[1], 1))
        for j in range(5): d.ell(xx + (j % 2 * 2 - 1) * 30, 300 + j * 230, 40, 70, A(leaf[0], 0.8))
    for i, vx in enumerate((250, 380, 700, 860)):
        sw = 10 * math.sin(t * 1.1 + i)
        pts = [(vx + sw * (k / 8) ** 2, k * 70) for k in range(9)]
        d.line(pts, A(leaf[0], 1), 6)
        for k in range(2, 9, 2): d.ell(pts[k][0] + 14, pts[k][1], 18, 9, A(leaf[1], 1))
    if beam > 0 and not xr:                                 # flashlight from upper-left onto the log
        for j in range(5):
            d.poly([(-60, 240), (-60 + 24 * j, 200), (540 + 380 - 40 * j, 1000), (540 - 300 + 30 * j, 1080)], A((255, 244, 200), 0.035 * beam))
        for i in range(7): d.circ(540, 990, 470 - i * 55, fill=A((255, 240, 190), (0.025 + 0.01 * i) * beam))
    log_(d, 540, 1100, 760, 1) if not xr else (d.ell(540, 1140, 418, 60, A((24, 60, 150), 1)), d.ell(540, 1110, 400, 30, A((40, 90, 190), 1)))
    for x, sc, ang in ((150, 1.0, -0.4), (930, 1.1, 0.5), (260, 0.7, 0.2), (820, 0.8, -0.3)):   # ferns
        for j in range(5):
            a_ = -math.pi / 2 + ang + (j - 2) * 0.25 + 0.03 * math.sin(t * 1.5 + j)
            lx, ly = x + math.cos(a_) * 10, 1180
            d.poly([(lx, ly), (lx + math.cos(a_ - 0.2) * 220 * sc, ly + math.sin(a_ - 0.2) * 220 * sc), (lx + math.cos(a_) * 300 * sc, ly + math.sin(a_) * 300 * sc),
                    (lx + math.cos(a_ + 0.2) * 220 * sc, ly + math.sin(a_ + 0.2) * 220 * sc)], A(leaf[j % 2], 1))
    if not xr: fireflies(d, t, 14, 11, 0.9)
    if rain > 0:
        for i in range(70):
            u = (t * 1.6 + i * 0.137) % 1; xx = (i * 97) % 1200 - 60 + u * 60; yy = u * 2100 - 100
            d.line([(xx, yy), (xx + 8, yy + 46)], A((170, 210, 230) if not xr else (120, 170, 255), 0.28 * rain), 3)

def s_hook(t, d):
    rainforest(d, t, 0.6, ease(pr(t, 0, 0.5)))
    yb = hop(t, 0.05, 40, 0.4) + hop(t, 1.4, 25, 0.3)
    frog(d, FX_, FY_ + yb, 1.25, t, 1, "sus" if t < 1.6 else "smug", look=0.6 * math.sin(t * 2), belly_q=ease(pr(t, 0.2, 0.6)), squash=0.06 * pulse(t, [0.45, 1.7], 10))
    sy = 760 + 360 * (0.5 - 0.5 * math.cos(t * 2.4))
    d.rect(330, sy - 4, 750, sy + 4, fill=A(CYAN, 0.85)); d.rect(330, sy - 40, 750, sy, fill=A(CYAN, 0.12))
    for i, c in enumerate(COUNT):
        t1 = COUNT[i + 1] if i + 1 < len(COUNT) else BIG1
        k = popk(t, c, "bouncy")
        if c <= t < t1:
            a_ = 1 - pr(t, t1 - 0.12, t1)
            d.circ(540, 420, 110, fill=A((6, 20, 24), 0.6 * a_))
            d.arc(540, 420, 110, 110, -90, -90 + 360 * (1 - pr(t, c, t1)), A(CYAN, a_), 12)
            d.text(540, 420, str(3 - i), int(160 * min(1.15, 0.6 + 0.4 * k)), A(CYAN, a_), k=1)

# ---------------- S2: X-ray wipe over the same forest (match cut) ----------------
def _reveal_xr(t, d, t0):
    rainforest(d, t, 0.3, 0, xr=True)
    sk = [pr(t, t0 + 0.05, t0 + 0.4), pr(t, t0 + 0.35, t0 + 0.7), pr(t, t0 + 0.65, t0 + 1.0)]
    face = "shock" if t < t0 + 1.2 else "scared"
    frog(d, FX_, FY_, 1.25, t, 1, face, xray=1, shells=3, shell_k=sk, blush=ease(pr(t, t0 + 1.2, t0 + 1.5)))
    d.text(210, 330, "R", 60, A((200, 225, 255), 0.6), k=1)                                  # radiograph marker
    for j in range(12): d.rect(880, 360 + j * 60, 880 + (34 if j % 2 else 20), 366 + j * 60, fill=A((200, 225, 255), 0.5))
def s_reveal(t, d):
    t0 = BIG1; wy = lerp(-40, 1960, ease(pr(t, t0, t0 + 0.3)))
    if wy < 1950:
        rainforest(d, t, 0.6, 1.0); frog(d, FX_, FY_, 1.25, t, 1, "shock")
        img2 = Image.new("RGB", d.img.size); _reveal_xr(t, D(img2), t0)
        if wy > 0:
            m = Image.new("L", d.img.size, 0); ImageDraw.Draw(m).rectangle((0, 0, d.img.size[0], int(P(wy))), fill=255)
            d.img.paste(img2, (0, 0), m)
        d.rect(-10, wy - 6, 1090, wy + 6, fill=A(CYAN, 1)); d.rect(-10, wy - 60, 1090, wy - 6, fill=A(CYAN, 0.18))
    else: _reveal_xr(t, d, t0)
    zap(d, FX_, FY_ + 60, t, t0 + 0.05, SHELL, 460)
    sparks(d, FX_, FY_ + 60, t, t0 + 0.05, 40, 900, SHELL_L, 1, 7, 1.0)
    for i, tt in enumerate((t0 + 0.05, t0 + 0.35, t0 + 0.65)):
        ptag(d, t, tt, [330, 750, 540][i], [1000, 990, 1190][i], str(i + 1), SHELL, 46)
    ptag(d, t, t0 + 0.9, 540, 470, "蜗牛壳 ×3", SHELL, 70)

# ---------------- S3: CT room — tray slides in, slices stack into a 3D picture ----------------
def ct_slices(d, cx, by, sc, prog, a=1.0):
    """frog silhouette built from horizontal slices, bottom-up; shells show as orange when reached"""
    n = 26; top = 300
    for i in range(int(n * prog)):
        u = i / (n - 1); y = by - u * top * sc
        hw = (130 if u < 0.15 else 115 * (1 - (u - 0.15) * 0.3)) if u < 0.6 else 120 * (1 - (u - 0.6) * 1.1)
        if u > 0.82: hw = 50
        col = mix(XR_D, XR, u)
        d.ell(cx, y, hw * sc, 9 * sc, A(col, a))
        if u > 0.82:
            for sd in (-1, 1): d.circ(cx + sd * 70 * sc, y, 30 * sc, fill=A(XR, a))
        if 0.2 < u < 0.5:
            d.circ(cx - 30 * sc, by - 0.32 * top * sc, 26 * sc, fill=A(SHELL, a)); d.circ(cx + 34 * sc, by - 0.36 * top * sc, 24 * sc, fill=A(SHELL, a))
        if 0.08 < u: d.circ(cx + 2 * sc, by - 0.12 * top * sc, 17 * sc, fill=A(SHELL, a))
def s_ct(t, d):
    t0 = T["ct"]
    grad(d, (196, 214, 222), (160, 182, 194), 0, 1000)
    for i in range(5): d.rect(-20 + i * 230, 260, 190 + i * 230, 980, fill=A(WHITE, 0.10), r=10)        # wall panels
    grad(d, (120, 140, 156), (80, 96, 112), 1000, 1920)                                               # floor
    for i in range(-6, 8): d.line([(540 + i * 60, 1000), (540 + i * 260, 1920)], A(WHITE, 0.12), 3)
    for j in range(6): d.line([(-20, 1000 + j * j * 26), (1100, 1000 + j * j * 26)], A(WHITE, 0.12), 3)
    lamp = 0.5 + 0.5 * math.sin(t * 9)                                                              # warning lamp
    d.rect(820, 300, 920, 360, fill=A((60, 60, 70), 1), r=10); glow_disc(d, 870, 330, 60, (255, 80, 70), 0.6 * lamp); d.circ(870, 330, 18, fill=A((255, 90, 80), 0.6 + 0.4 * lamp))
    gx, gy, gr = 660, 860, 280
    d.rect(gx - 230, gy + 230, gx + 230, gy + 330, fill=A((214, 226, 232), 1), r=30)                   # gantry base
    ct_ring(d, gx, gy, gr, t, 1, scan=pr(t, t0 + 1.2, t0 + 2.4))
    d.line([(gx, gy - gr * 0.66), (gx, gy + gr * 0.66)], A((255, 70, 70), 0.6), 3); d.line([(gx - gr * 0.66, gy), (gx + gr * 0.66, gy)], A((255, 70, 70), 0.6), 3)
    u = ease(pr(t, t0 + 0.2, t0 + 2.0)); tx = lerp(0, 340, u)
    d.rect(80 + tx, gy + 60, 420 + tx, gy + 92, fill=A((236, 242, 246), 1), r=14)                        # tray
    d.rect(60, gy + 92, 420, gy + 230, fill=A((180, 196, 206), 1), r=16)                                # table body
    fx = 250 + tx; inside = cl((fx - (gx - gr * 0.6)) / 140)
    frog(d, fx, gy + 18, 0.30, t, 1, "scared" if u < 0.95 else "sus", xray=inside, shells=3 if inside > 0.3 else 0)
    if t0 + 1.0 < t < t0 + 3.3:                                                                     # scan fan
        ang = (t - t0) * 4
        for j in range(3): d.poly([(gx, gy - gr * 0.66), (gx - 60 + j * 10 + 40 * math.sin(ang), gy + gr * 0.5), (gx + 60 - j * 10 + 40 * math.sin(ang), gy + gr * 0.5)], A(CYAN, 0.08))
    d.line([(330, 560), (330, 300), (400, 300)], A((150, 166, 176), 1), 14)                           # monitor arm
    d.rect(150, 330, 520, 620, fill=A((32, 40, 52), 1), r=22); d.rect(168, 348, 502, 602, fill=A((8, 26, 70), 1), r=12)
    for j in range(6): d.line([(168, 360 + j * 42), (502, 360 + j * 42)], A(XR, 0.12), 2)
    ct_slices(d, 335, 560, 0.62, pr(t, t0 + 1.0, t0 + 2.8))
    if t0 + 1.0 < t < t0 + 2.8:
        yy = 560 - pr(t, t0 + 1.0, t0 + 2.8) * 190; d.rect(176, yy - 2, 494, yy + 2, fill=A(CYAN, 0.9))
    ptag(d, t, t0 + 2.6, 335, 670, "显微 CT", CYAN, 38)

# ---------------- S4: researcher's desk — archive card gets the NEW SPECIES stamp ----------------
def s_who(t, d):
    t0 = T["who"]
    grad(d, (150, 98, 62), (104, 64, 40))
    for j in range(9): d.rect(-20, 120 + j * 210, 1100, 126 + j * 210, fill=A((80, 48, 28), 0.5))      # planks
    for i in range(8): d.circ(540, 760, 820 - i * 90, fill=A((255, 230, 170), 0.03 + 0.01 * i))      # lamp pool
    d.rect(620, 1090, 980, 1180, fill=A((60, 90, 140), 1), r=6); d.rect(640, 1100, 960, 1170, fill=A((80, 110, 160), 1), r=4)   # notebook
    d.line([(160, 1110), (520, 1170)], A((240, 196, 60), 1), 18); d.poly([(520, 1170), (500, 1155), (546, 1178)], A((60, 50, 40), 1))   # pencil
    k = popk(t, t0, "smooth"); y_ = (1 - min(1, k)) * 80
    d.rect(232, 412 + y_, 852, 1062 + y_, fill=A((0, 0, 0), 0.18), r=14)                               # card + shadow
    d.rect(220, 400 + y_, 840, 1050 + y_, fill=A((250, 244, 226), 1), r=14)
    d.rect(220, 400 + y_, 840, 440 + y_, fill=A((240, 204, 120), 1), r=14)
    d.rect(280, 470 + y_, 600, 820 + y_, fill=A(WHITE, 1), r=6)                                       # polaroid
    d.rect(296, 486 + y_, 584, 760 + y_, fill=A((70, 120, 80), 1))
    for i in range(4): d.ell(330 + i * 80, 760 + y_, 70, 26, A((50, 96, 60), 1))
    frog(d, 440, 690 + y_ + hop(t, t0 + 1.0, 20, 0.3), 0.42, t, 1, "proud" if t > t0 + 1.0 else "happy")
    d.line([(560, 450 + y_), (560, 520 + y_), (580, 520 + y_), (580, 460 + y_)], A((180, 186, 196), 1), 6)   # paperclip
    for j in range(4): d.rect(640, 500 + j * 70 + y_, 800 - (j % 2) * 50, 518 + j * 70 + y_, fill=A((200, 194, 180), 1), r=9)   # blank fields
    for j in range(3): d.rect(280, 870 + j * 56 + y_, 780 - j * 90, 886 + j * 56 + y_, fill=A((210, 204, 190), 1), r=8)
    sk = back(pr(t, t0 + 0.9, t0 + 1.08))                                                          # stamp slam
    if sk > 0:
        sz = 2.2 - 1.2 * sk; cx, cy = 690, 900; al = min(1, sk * 1.5)
        w_, h_ = 190 * sz, 120 * sz
        d.rect(cx - w_, cy - h_, cx + w_, cy + h_, outline=A((220, 50, 50), 0.9 * al), w=10 * sz, r=20 * sz)
        d.text(cx, cy - 18 * sz, "新物种", int(84 * sz), A((220, 50, 50), 0.92 * al), k=1)
        d.text(cx, cy + 66 * sz, "2026", int(34 * sz), A((220, 50, 50), 0.85 * al), k=1)
        if t < t0 + 1.4: sparks(d, cx, cy, t, t0 + 1.0, 24, 600, (255, 120, 100), 1, 5, 0.5)
    sx = lerp(1180, 830, ease(pr(t, t0 + 2.0, t0 + 2.8)))
    snail(d, sx, 1210, 0.45, t, 1, "shock" if t > t0 + 2.8 else "happy", flip=-1, crawl=1 - pr(t, t0 + 2.6, t0 + 2.8), look=-0.6)

# ---------------- S5: Apatani village at dusk — elder says the word, dictionary card ----------------
def stilt_house(d, x, y, s, a=1.0):
    for j in range(4): d.rect(x - 120 * s + j * 76 * s, y - 10, x - 108 * s + j * 76 * s, y + 140 * s, fill=A((110, 70, 44), a))
    d.rect(x - 140 * s, y - 130 * s, x + 140 * s, y, fill=A((214, 168, 104), a))
    for j in range(5): d.rect(x - 140 * s, y - 120 * s + j * 24 * s, x + 140 * s, y - 112 * s + j * 24 * s, fill=A((190, 140, 82), a))
    d.poly([(x - 175 * s, y - 120 * s), (x, y - 250 * s), (x + 175 * s, y - 120 * s)], A((150, 112, 60), a))
    d.poly([(x - 150 * s, y - 130 * s), (x, y - 230 * s), (x + 150 * s, y - 130 * s)], A((176, 134, 72), a))
    d.rect(x - 30 * s, y - 90 * s, x + 30 * s, y, fill=A((70, 44, 30), a))
def s_name(t, d):
    t0 = T["name"]
    grad(d, (255, 170, 120), (150, 90, 140), 0, 1100)
    glow_disc(d, 760, 640, 200, (255, 230, 160), 0.6); d.circ(760, 640, 80, fill=A((255, 236, 180), 1))
    mtn(d, 0, [(160, 96, 136), (120, 70, 110)], 1, seed=5, amp=260, y0=820)
    for j in range(6):                                                                              # rice terraces
        y = 920 + j * 70; c = mix((150, 170, 90), (70, 120, 70), j / 5)
        pts = [(-40, y + 30)] + [(x, y + 18 * math.sin(x / 160 + j)) for x in range(-40, 1141, 60)] + [(1140, 1960), (-40, 1960)]
        d.poly(pts, A(c, 1))
        d.line([(x, y + 18 * math.sin(x / 160 + j)) for x in range(-40, 1141, 60)], A((200, 220, 140), 0.5), 4)
    stilt_house(d, 860, 880, 0.8); stilt_house(d, 170, 900, 0.65)
    for i in range(4): d.ell(840 + 20 * math.sin(t + i), 600 - i * 50 - (t * 30 % 50), 30 + i * 8, 16 + i * 4, A(WHITE, 0.10))   # chimney smoke
    villager(d, 290, 1200, 0.9, t, 1, point=ease(pr(t, t0 + 0.4, t0 + 0.8)))
    hid = ease(pr(t, t0 + 1.8, t0 + 2.4))
    snail(d, 560, 1190, 0.55, t, 1, "scared" if t > t0 + 1.8 else "happy", flip=-1, crawl=1 - hid, hide=hid)
    frog(d, 790, 1110, 0.55, t, 1, "love" if t > t0 + 1.6 else "happy", look=-0.7)
    kb = popk(t, t0 + 0.2, "bouncy")                                                                 # speech bubble
    if kb > 0:
        kk = min(1.05, kb); d.rect(150, 770 - 70 * kk, 490, 770 + 70 * kk, fill=A(WHITE, 0.97), r=50)
        d.poly([(260, 830), (310, 830), (290, 880)], A(WHITE, 0.97))
        d.text(320, 770, "tanogogo！", int(52 * kk), A(NAVYT, 1), k=1)
    kc = popk(t, t0 + 1.2, "bouncy")                                                                 # dictionary card
    if kc > 0:
        kk = min(1, kc); cx, cy = 600, 430 + (1 - kk) * -60
        d.rect(cx - 240 * kk, cy - 120, cx + 240 * kk, cy + 120, fill=A((255, 250, 236), 1), r=24)
        d.rect(cx - 240 * kk, cy - 120, cx - 200 * kk, cy + 120, fill=A((200, 70, 60), 1), r=12)
        d.text(cx - 40, cy, "=", 90, A(SHELL, kk), k=1); d.text(cx + 100, cy, "蜗牛", 80, A(NAVYT, kk), k=1)
        shell(d, cx - 140, cy, 50 * kk, 1)
        arrow(d, 420, 690, cx - 100, cy + 130, (255, 250, 236), ap(t, t0 + 1.3, 0.2), 8)

# ---------------- S6: quiz show — "first ever?" board, YES / NO lamps flicker ----------------
def s_q(t, d):
    t0 = T["q"]
    grad(d, (44, 20, 70), (12, 6, 24))
    for i, x in enumerate((220, 860)):                                                                # spotlights
        d.poly([(x, 240), (x + 40, 240), (540 + 260 * (1 if i else -1) * -0.2 + 160, 1250), (540 - 160 + 260 * (1 if i else -1) * -0.2, 1250)], A((255, 240, 200), 0.06))
    d.ell(540, 1210, 460, 70, A((120, 60, 160), 0.6))
    bx0, by0, bx1, by1 = 190, 320, 890, 610                                                          # marquee board
    d.rect(bx0, by0, bx1, by1, fill=A((150, 30, 80), 1), r=30); d.rect(bx0 + 30, by0 + 30, bx1 - 30, by1 - 30, fill=A((40, 10, 40), 1), r=20)
    n = 28
    for i in range(n):
        u = i / n; per = 2 * (bx1 - bx0 + by1 - by0); p = u * per
        if p < bx1 - bx0: x, y = bx0 + p, by0
        elif p < bx1 - bx0 + by1 - by0: x, y = bx1, by0 + p - (bx1 - bx0)
        elif p < 2 * (bx1 - bx0) + by1 - by0: x, y = bx1 - (p - (bx1 - bx0) - (by1 - by0)), by1
        else: x, y = bx0, by1 - (p - 2 * (bx1 - bx0) - (by1 - by0))
        on = (int(t * 8) + i) % 2
        d.circ(x, y, 10, fill=A((255, 220, 120) if on else (120, 80, 60), 1))
    kq = popk(t, t0 + 0.1, "bouncy")
    if kq > 0:
        d.text(470, 460, "第一只？", int(110 * min(1.08, kq)), A(GOLD, 1), k=1)
        shell(d, 760, 460, 44 * min(1, kq), 1)
    fl = (t - t0) * (3 + 6 * pr(t, t0, t0 + 3)); yes = math.sin(fl * 3) > 0                          # lamps flicker faster
    for x, s_, col, on in ((220, "是", (80, 200, 110), yes), (860, "不是", (240, 70, 80), not yes)):
        a_ = 1 if on else 0.35
        if on: glow_disc(d, x, 800, 110, col, 0.6)
        d.circ(x, 800, 70, fill=A(mix(col, (40, 30, 50), 0 if on else 0.6), 1)); d.text(x, 800, s_, 44 if len(s_) == 1 else 38, A(WHITE, a_), k=1)
    frog(d, 540, 900 + hop(t, t0 + 1.2, 16, 0.25), 0.62, t, 1, "sus", look=0.8 * math.sin(t * 4))
    d.rect(370, 990, 710, 1220, fill=A((90, 70, 150), 1), r=16); d.rect(370, 990, 710, 1030, fill=A((130, 104, 200), 1), r=16)
    d.ell(540, 990, 60, 26, A((200, 40, 50), 1)); d.ell(540, 982, 50, 18, A((240, 80, 90), 1))
    for i in range(9): d.circ(60 + i * 120, 1300 + 12 * math.sin(t * 3 + i), 60, fill=A((20, 10, 30), 0.9))   # audience heads

# ---------------- S7 (BIG2): horned-frog family tree; our branch lights up ----------------
TREE = [(230, 1040, "grey"), (850, 1040, "olive"), (250, 830, "choc"), (830, 830, "rust"), (300, 640, "gold"), (780, 640, "olive")]
def s_big2(t, d):
    t0 = BIG2
    grad(d, (30, 40, 80), (10, 14, 34))
    ch = t0 + 0.9
    rk = ease(pr(t, t0 + 1.7, t0 + 2.1))
    if rk > 0:
        for i in range(18):
            a0 = t * 0.4 + i * math.pi / 9; a1 = a0 + math.pi / 18
            d.poly([(540, 560), (540 + math.cos(a0) * 1400, 560 + math.sin(a0) * 1400), (540 + math.cos(a1) * 1400, 560 + math.sin(a1) * 1400)], A((255, 200, 80), 0.10 * rk))
    g = ease(pr(t, t0, t0 + 0.5))
    trunk = (110, 74, 50)
    d.poly([(470, 1300), (610, 1300), (560, lerp(1300, 640, g)), (520, lerp(1300, 640, g))], A(trunk, 1))
    for i, (x, y, p) in enumerate(TREE):
        gi = ease(pr(t, t0 + 0.1 + i * 0.05, t0 + 0.45 + i * 0.05))
        sx_, sy_ = 540, y + 120
        if gi > 0: d.line([(sx_, sy_), (lerp(sx_, x, gi), lerp(sy_, y + 60, gi))], A(trunk, 1), 26)
        if gi > 0:
            for j in range(3): d.ell(lerp(sx_, x, gi) + (j - 1) * 50, lerp(sy_, y + 60, gi) + 30, 60, 30, A((50, 110, 70), 0.9))
    gb = ease(pr(t, t0 + 0.3, t0 + 0.7))                                                         # our branch, gold
    if gb > 0: d.line([(540, 760), (540, lerp(760, 640, gb))], A(GOLD if t > t0 + 1.7 else trunk, 1), 30)
    for i, (x, y, p) in enumerate(TREE):
        k = popk(t, t0 + 0.4 + i * 0.07, "bouncy")
        if k > 0: frog_icon(d, x, y, 0.36 * min(1.05, k), 1, p, "shock" if t > t0 + 1.8 else "sus", t + i, grey=0.35)
    d.rect(400, 1120, 680, 1200, fill=A((200, 150, 90), 1), r=12); d.text(540, 1160, "角蟾家族", 44, A((60, 36, 20), 1), k=1)
    if t > t0 + 1.7: glow_disc(d, 540, 560, 230, GOLD, 0.7 * rk)
    mo = ease(pr(t, ch, ch + 0.2)) * (1 - ease(pr(t, ch + 0.35, ch + 0.5)))
    kf = popk(t, t0 + 0.5, "bouncy")
    if kf > 0:
        frog(d, 540, 560, 0.55 * min(1.05, kf), t, 1, "chew" if ch + 0.5 < t < ch + 2.0 else ("proud" if t > ch + 2 else "happy"), mouth=mo,
             cheeks=0.6 * pr(t, ch + 0.5, ch + 0.7) * (1 - pr(t, ch + 1.8, ch + 2.0)))
    if t < ch + 0.4:
        sx = lerp(820, 580, ease(pr(t, t0 + 0.4, ch + 0.3))); snail(d, sx, 640 - 40 * ease(pr(t, ch, ch + 0.3)), 0.32, t, 1, "scared", flip=-1)
    if t > t0 + 1.7:
        stamp(d, t, t0 + 1.7, "第一次！", 540, 340, 140, (255, 90, 100))
        sparks(d, 540, 560, t, t0 + 1.7, 40, 900, GOLD, 1, 9, 1.0)

# ---------------- S8: rice paddy by day — black-spotted frog tongues a snail ----------------
def s_other(t, d):
    t0 = T["other"]
    grad(d, (140, 200, 240), (214, 236, 246), 0, 760)
    for i in range(3): d.ell(200 + i * 360 + (t * 10) % 40, 380 + i * 60, 110, 36, A(WHITE, 0.8))
    mtn(d, 0, [(110, 170, 120), (80, 140, 100)], 1, seed=8, amp=160, y0=700)
    grad(d, (150, 200, 210), (90, 150, 170), 760, 1920)                                             # paddy water
    for j in range(9):                                                                              # rice rows in perspective
        y = 790 + (j ** 1.5) * 26; sc = 0.4 + j * 0.16
        for i in range(-8, 9):
            x = 540 + i * (60 + j * 24) + (j % 2) * 20
            if -40 < x < 1120:
                for b in (-1, 0, 1): d.line([(x, y), (x + b * 14 * sc + 2 * math.sin(t * 2 + i), y - 46 * sc)], A((80, 160, 70) if b else (110, 190, 80), 1), max(2, 5 * sc))
        d.ell(540, y + 4, 600, 3, A(WHITE, 0.15))
    d.poly([(-40, 1000), (1120, 940), (1120, 1040), (-40, 1100)], A((150, 112, 72), 1)); d.poly([(-40, 1000), (1120, 940), (1120, 960), (-40, 1020)], A((180, 140, 96), 1))   # bund
    sx, sy = 770, 820
    d.line([(sx, 990), (sx - 10, sy - 30), (sx + 6, sy - 120)], A((90, 170, 70), 1), 8)               # tall stalk with snail
    eat = ch = t0 + 0.6
    tk = ease(pr(t, ch, ch + 0.15)) * (1 - ease(pr(t, ch + 0.25, ch + 0.45)))
    fx, fy, fs = 380, 960, 0.62
    mx, my = fx, fy - 46 * fs
    if t < ch + 0.25: snail(d, sx + 6, sy, 0.26, t, 1, "happy" if t < ch else "shock", flip=-1, crawl=0.5)
    elif t < ch + 0.45:
        u = pr(t, ch + 0.25, ch + 0.45); snail(d, lerp(sx, mx + 20, u), lerp(sy, my, u), 0.26 * (1 - 0.5 * u), t, 1, "shock", flip=-1, hide=1)
    frog(d, fx, fy, fs, t, 1, "chew" if ch + 0.45 < t < ch + 1.6 else "happy", pal="green", horns=False, mouth=0.6 * (tk > 0), look=0.8,
         cheeks=0.6 * pr(t, ch + 0.45, ch + 0.6) * (1 - pr(t, ch + 1.4, ch + 1.6)))
    if tk > 0: tongue_line(d, mx + 10, my + 6, sx - 20, sy - 30, tk, 1, 16)
    for i in range(3):
        u = (t - t0 + i * 0.6) % 1.8 / 1.8; d.ell(560, 1120, 60 + 180 * u, 10 + 30 * u, outline=A(WHITE, 0.4 * (1 - u)), w=3)
    ptag(d, t, t0 + 0.2, fx, 640, "黑斑蛙", (150, 214, 130), 46)
    check_mark(d, 700, 620, 44, (80, 190, 110), 1, popk(t, t0 + 1.6, "bouncy"))
    if t > t0 + 1.6: d.text(840, 620, "早就吃过", 40, A(NAVYT, ap(t, t0 + 1.7)), k=1)

# ---------------- S9: radiology lightbox — two films side by side ----------------
def film_xray(d, x, y, t, pal, shells, a=1.0, label_shell=None):
    d.rect(x - 170, y - 300, x + 170, y + 300, fill=A((10, 22, 56), a), r=10)
    for j in range(7): d.line([(x - 170, y - 300 + j * 100), (x + 170, y - 300 + j * 100)], A(XR, 0.12 * a), 2)
    frog(d, x, y + 40, 0.72, t, a, "happy", pal=pal, xray=1, shells=shells)
def s_kin(t, d):
    t0 = T["kin"]
    grad(d, (96, 112, 128), (60, 72, 88))
    d.rect(-20, 1180, 1100, 1960, fill=A((70, 80, 96), 1))
    d.rect(150, 400, 930, 1140, fill=A((206, 212, 220), 1), r=24)                                  # lightbox
    for x in (345, 735): d.rect(x - 186, 430, x + 186, 1110, fill=A((226, 238, 255), 1), r=10); glow_disc(d, x, 770, 300, (220, 236, 255), 0.25)
    film_xray(d, 345, 780, t, "tan", 3)
    d.rect(305, 460, 385, 490, fill=A((170, 176, 186), 1), r=6)
    kr = ease(pr(t, t0 + 0.8, t0 + 1.3)); ry = lerp(-400, 780, kr)
    if kr > 0:
        film_xray(d, 735, ry, t, "olive", 0)
        d.rect(695, ry - 320, 775, ry - 290, fill=A((170, 176, 186), 1), r=6)
        if t > t0 + 1.6:
            ks = popk(t, t0 + 1.6, "bouncy"); sx, sy = 735, ry + 40 + 0.72 * 50
            shell(d, sx, sy, 30 * min(1.1, ks), 1, SHELL, SHELL_L, (200, 90, 20), glowk=0.9)
            ca = pr(t, t0 + 2.0, t0 + 2.5)
            if ca > 0: d.arc(sx, sy, 70, 64, -90, -90 + 360 * ca, A((255, 70, 70), 1), 8)
    ptag(d, t, t0 + 0.2, 345, 400, "吃蜗牛角蟾", FROG_L, 34)
    ptag(d, t, t0 + 0.5, 345, 1050, "3 个壳", SHELL, 44)
    ptag(d, t, t0 + 1.2, 735, 400, "近亲", (176, 180, 110), 34)
    ptag(d, t, t0 + 2.3, 735, 1050, "1 个壳", SHELL, 44)
    if t > t0 + 3.2: tag(d, 540, 320, "两种都是首次记录", GOLD, ap(t, t0 + 3.2, 0.3), 34)

# ---------------- S10: graph paper macro — 3 cm ruler, fingertip, snail ----------------
def s_gulp(t, d):
    t0 = T["gulp"]
    grad(d, (238, 244, 230), (220, 230, 212))
    for i in range(0, 1100, 40): d.line([(i, 0), (i, 1920)], A((150, 200, 150), 0.35 if i % 200 else 0.6), 2)
    for j in range(0, 1920, 40): d.line([(0, j), (1080, j)], A((150, 200, 150), 0.35 if j % 200 else 0.6), 2)
    CM = 127; x0 = 540 - 1.5 * CM; ry = 1020
    rk = ease(pr(t, t0, t0 + 0.6))
    d.rect(x0 - 30, ry, x0 - 30 + (3 * CM + 90) * rk, ry + 80, fill=A((255, 214, 90), 1), r=10)
    for i in range(31):
        xx = x0 + i * CM / 10
        if xx > x0 - 30 + (3 * CM + 90) * rk: break
        big = i in (0, 10, 20, 30)
        d.line([(xx, ry), (xx, ry + (38 if big else (28 if i in (5, 15, 25) else 18)))], A(NAVYT, 1), 4 if big else 3)
        if big: d.text(xx, ry + 58, str(i // 10), 28, A(NAVYT, 1), k=1)
    d.text(x0 + 3 * CM + 40, ry + 58, "cm", 26, A(NAVYT, rk), k=1)
    sc = 3 * CM / 380
    mo = 0.55 * ease(pr(t, t0 + 2.4, t0 + 2.7))
    frog(d, 540, ry - 130 * sc, sc, t, 1, "shock" if t > t0 + 2.2 else "happy", mouth=mo, look=0.7)
    if t > t0 + 0.8:
        a_ = ap(t, t0 + 0.8, 0.3); by = ry - 14; c_ = (240, 70, 80)
        d.line([(x0, by), (x0 + 3 * CM, by)], A(c_, a_), 6); d.line([(x0, by - 16), (x0, by + 16)], A(c_, a_), 6); d.line([(x0 + 3 * CM, by - 16), (x0 + 3 * CM, by + 16)], A(c_, a_), 6)
    ptag(d, t, t0 + 0.9, 540, 1160, "约 3 厘米", (240, 70, 80), 36, tc=WHITE)
    fk = ease(pr(t, t0 + 1.2, t0 + 1.8))                                                               # fingertip for scale
    fingertip(d, lerp(1180, 800, fk), lerp(380, 560, fk), 1.0)
    snx = lerp(1150, 800, ease(pr(t, t0 + 1.6, t0 + 2.3)))
    snail(d, snx, ry - 4, 0.32, t, 1, "sus", flip=-1, crawl=1)
    if t > t0 + 2.6:
        dashed(d, [(snx - 50, ry - 50), (650, ry - 140)], (240, 70, 80), ap(t, t0 + 2.6, 0.2), 5)
    ptag(d, t, t0 + 2.8, 540, 470, "整只吞？", NAVYT, 54, tc=WHITE)

# ---------------- S11: anatomy poster — side cut of the head, jaw joint far back ----------------
def s_jaw(t, d):
    t0 = T["jaw"]
    grad(d, (70, 84, 110), (40, 50, 72))
    for i in range(0, 1100, 60): d.line([(i, 0), (i, 1920)], A(WHITE, 0.04), 2)
    hx, hy = 380, 820                                                                         # jaw joint (behind the eye)
    op = 0.5 - 0.5 * math.cos(max(0, t - t0 - 0.8) * 2.6)
    ang = 0.6 * op * ease(pr(t, t0 + 0.8, t0 + 1.2)); ua = -ang * 0.2
    R_ = lambda x, y: rot(x, y, hx, hy, ua); L_ = lambda x, y: rot(x, y, hx, hy, ang)
    # side-view frog: sitting body + hind leg on the left, head to the right
    d.ell(hx - 120, hy + 170, 250, 190, A(FROG_D, 1)); d.ell(hx - 124, hy + 160, 240, 178, A(FROG, 1))
    d.ell(hx - 200, hy + 290, 170, 80, A(FROG_D, 1)); d.ell(hx - 190, hy + 282, 160, 70, A(FROG_L, 1))
    d.line([(hx + 40, hy + 140), (hx + 70, hy + 330)], A(FROG_D, 1), 40); d.ell(hx + 90, hy + 340, 44, 14, A(FROG_L, 1))
    # lower jaw (skin) + jaw bone, rotating about the joint
    if ang > 0.04:
        d.poly([(hx + 20, hy + 4), R_(hx + 520, hy + 4), L_(hx + 520, hy - 4)], A((120, 30, 50), 1))
        d.poly([(hx + 60, hy + 10), R_(hx + 420, hy + 6), L_(hx + 420, hy - 2)], A(PINKM, 1))
    d.poly([L_(x, y) for x, y in [(hx - 40, hy - 10), (hx - 30, hy + 60), (hx + 200, hy + 90), (hx + 420, hy + 60), (hx + 540, hy + 4), (hx + 20, hy - 4)]], A(BELLY, 1))
    d.line([L_(x, y) for x, y in [(hx, hy + 10), (hx + 200, hy + 52), (hx + 520, hy + 8)]], A((255, 200, 110), 1), 22)   # jaw bone
    # upper head (skin) with skull cutaway
    d.poly([R_(x, y) for x, y in [(hx - 90, hy + 20), (hx - 70, hy - 120), (hx + 120, hy - 200), (hx + 360, hy - 170), (hx + 540, hy - 70), (hx + 570, hy - 10), (hx + 530, hy + 6), (hx - 40, hy + 10)]], A(FROG, 1))
    d.poly([R_(x, y) for x, y in [(hx - 20, hy - 6), (hx + 10, hy - 100), (hx + 160, hy - 150), (hx + 360, hy - 120), (hx + 500, hy - 50), (hx + 510, hy - 14), (hx + 40, hy - 6)]], A((250, 242, 226), 0.92))
    ox, oy = R_(hx + 200, hy - 150)
    d.circ(ox, oy - 20, 74, fill=A(FROG, 1)); d.circ(ox, oy - 26, 50, fill=A(WHITE, 1)); d.circ(ox + 14, oy - 22, 25, fill=A(INK, 1)); d.circ(ox + 4, oy - 32, 8, fill=A(WHITE, 1))
    hn = R_(hx + 170, hy - 238); d.poly([(hn[0] - 30, hn[1] + 30), (hn[0] - 6, hn[1] - 46), (hn[0] + 24, hn[1] + 26)], A(FROG_L, 1))   # eyelid horn
    if ang > 0.08:                                                                              # gape angle
        Rr = 640
        d.arc(hx, hy, Rr, Rr, math.degrees(ua) - 1, math.degrees(ang), A(CYAN, 0.9), 7)
    ka = ease(pr(t, t0 + 0.3, t0 + 0.7))
    glow_disc(d, hx, hy, 90, GOLD, 0.9 * ka); d.circ(hx, hy, 22, fill=A(GOLD, ka))
    if ka > 0: d.line([(hx, hy - 300), (hx, hy - 28)], A(GOLD, ka * 0.8), 5)
    ptag(d, t, t0 + 0.4, hx, hy - 330, "下巴关节", GOLD, 38)
    ptag(d, t, t0 + 1.0, 600, 560, "头骨", (250, 242, 226), 38)
    sx = lerp(1060, hx + 470, ease(pr(t, t0 + 1.2, t0 + 2.0)))
    shell(d, sx, hy + 10 + 60 * math.sin(ang * 0.6), 52, 1)
    k = popk(t, t0 + 2.3, "bouncy")                                                              # research in progress
    if k > 0:
        kk = min(1, k); mx, my = 820 + 16 * math.sin(t * 2), 400
        d.circ(mx, my, 70 * kk, fill=A((170, 220, 255), 0.25)); d.arc(mx, my, 70 * kk, 70 * kk, 0, 360, A(WHITE, 0.95), 12)
        d.line([(mx + 50 * kk, my + 50 * kk), (mx + 115 * kk, my + 115 * kk)], A(WHITE, 0.95), 22)
        p = 0.2 + 0.5 * pr(t, t0 + 2.5, t0 + 4.5)
        d.rect(700, 540, 900, 568, fill=A(WHITE, 0.2 * kk), r=14); d.rect(700, 540, 700 + 200 * p, 568, fill=A(GOLD, kk), r=14)
        d.text(800, 505, "研究中…", 36, A(WHITE, kk), k=1)

# ---------------- S12: night survey on the mountain — headlamps, calendar flipping 5 years ----------------
def s_survey(t, d):
    t0 = T["survey"]
    grad(d, (12, 18, 46), (32, 44, 86))
    rr = random.Random(5)
    for i in range(60):
        x, y = rr.uniform(0, 1080), rr.uniform(240, 800); b = 0.5 + 0.5 * math.sin(t * 3 + i)
        d.circ(x, y, 2.5 + (i % 3), fill=A(WHITE, 0.3 + 0.5 * b))
    pk = [(-60, 980), (120, 760), (260, 860), (420, 660), (600, 820), (760, 700), (900, 820), (1140, 740), (1140, 1000)]
    d.poly(pk, A((150, 166, 206), 1))
    for (x, y) in pk[1:-2:2]: d.poly([(x - 70, y + 60), (x, y), (x + 70, y + 60), (x + 30, y + 46), (x, y + 70), (x - 30, y + 46)], A(WHITE, 0.95))
    mtn(d, 0, [(26, 64, 66), (16, 44, 46)], 1, seed=9, amp=260, y0=1100)
    rr = random.Random(7)
    for i in range(10):                                                                           # teammates' headlamps on the slopes
        tt = t0 + 0.6 + i * 0.25; x, y = rr.uniform(160, 920), rr.uniform(920, 1150)
        if t > tt:
            b = ap(t, tt, 0.25) * (0.7 + 0.3 * math.sin(t * 5 + i))
            glow_disc(d, x, y, 34, (255, 240, 170), b); d.circ(x, y, 5, fill=A((255, 250, 210), b))
    d.poly([(-40, 1240), (300, 1180), (700, 1200), (1120, 1150), (1120, 1960), (-40, 1960)], A((10, 30, 30), 1))   # trail ridge
    sx = lerp(240, 560, pr(t, t0, nxt("survey")))
    scientist(d, sx, 1200, 0.9, t, 1, walk=1.0, beam=1.0, beam_ang=0.25 + 0.25 * math.sin(t * 1.3))
    cx, cy = 720, 400                                                                             # tear-off calendar
    yrs = 2021 + min(4, int(max(0, t - t0 - 0.3) / 0.55))
    d.rect(cx - 150, cy - 110, cx + 150, cy + 130, fill=A((250, 248, 240), 1), r=16); d.rect(cx - 150, cy - 110, cx + 150, cy - 50, fill=A((230, 80, 80), 1), r=16)
    for j in range(4): d.circ(cx - 90 + j * 60, cy - 110, 10, fill=A((150, 150, 160), 1))
    d.text(cx, cy + 36, str(yrs), 92, A(NAVYT, 1), k=1)
    for k_ in range(yrs - 2021):                                                                   # torn pages fly away
        tp = t0 + 0.3 + (k_ + 1) * 0.55; u = pr(t, tp, tp + 0.6)
        if 0 < u < 1:
            px, py = cx + 260 * u, cy + 20 - 120 * u + 300 * u * u
            d.poly([rot(x, y, px, py, u * 2.5) for x, y in ((px - 110, py - 70), (px + 110, py - 70), (px + 110, py + 90), (px - 110, py + 90))], A((250, 248, 240), 1 - u))
    ptag(d, t, t0 + 2.6, cx, 600, "5 年", GOLD, 64)
    kp = popk(t, t0 + 0.4, "bouncy")
    if kp > 0:
        px, py = 360, 640; kk = min(1.05, kp)
        d.circ(px, py - 60 * kk, 34 * kk, fill=A((240, 70, 80), 1)); d.poly([(px - 30 * kk, py - 50 * kk), (px + 30 * kk, py - 50 * kk), (px, py)], A((240, 70, 80), 1)); d.circ(px, py - 60 * kk, 12 * kk, fill=A(WHITE, 1))
        tag(d, px, py - 140, "喜马拉雅山东部", WHITE, min(1, kp), 32)

# ---------------- S13: line-up wall — five new species hop in to report ----------------
FIVE = ["tan", "rust", "olive", "choc", "gold"]
def s_five(t, d):
    t0 = T["five"]
    grad(d, (196, 204, 218), (170, 178, 196), 0, 1150)
    for j in range(9): d.rect(-20, 520 + j * 70, 1100, 524 + j * 70, fill=A((120, 130, 150), 0.6))
    d.rect(-20, 1150, 1100, 1960, fill=A((90, 96, 116), 1))
    xs = [220, 380, 540, 700, 860]
    for i, (p, x) in enumerate(zip(FIVE, xs)):
        ti = t0 + 0.05 + i * 0.22; u = ease(pr(t, ti, ti + 0.3))
        if u <= 0: continue
        fx = lerp(1250, x, u)
        frog_icon(d, fx, 950 + hop(t, ti, 120, 0.3) + hop(t, ti + 0.3, 30, 0.2), 0.46, 1, p, "proud" if u >= 1 else "happy", t + i)
        if u >= 1:
            kp = popk(t, ti + 0.3, "bouncy")
            d.rect(x - 56, 1050, x + 56, 1120, fill=A(WHITE, min(1, kp)), r=10); d.text(x, 1085, str(i + 1), int(48 * min(1.1, kp)), A(NAVYT, min(1, kp)), k=1)
            d.circ(x + 52, 860, 22 * min(1.1, kp), fill=A((240, 60, 70), 1)); d.text(x + 52, 860, "新", int(22 * min(1.1, kp)), A(WHITE, min(1, kp)), k=1)
    k = popk(t, t0 + 1.25, "bouncy")
    if k > 0:
        d.text(540, 440, "5", int(240 * min(1.1, k)), A(GOLD, 1), k=1)
        zap(d, 540, 440, t, t0 + 1.25, GOLD, 300)

# ---------------- S14: specimen cabinet — 6 known, 5 slots fill up, counter 6 -> 11 ----------------
def s_double(t, d):
    t0 = T["double"]
    grad(d, (64, 44, 36), (30, 20, 18))
    cols = ["grey"] * 6 + FIVE
    n = 6 if t < t0 + 1.4 else min(11, 6 + int((t - t0 - 1.4) / 0.3) + 1)
    d.text(540, 380, f"{n} 种", int(130 * (1 + 0.08 * pulse(t, [t0 + 1.4 + j * 0.3 for j in range(5)], 10))), A(GOLD if n == 11 else WHITE, 1), k=1)
    ptag(d, t, t0 + 3.0, 540, 520, "翻了一倍还多", (255, 120, 120), 42, tc=WHITE)
    cx0, cy0, cw, chh = 190, 620, 175, 170
    d.rect(cx0 - 20, cy0 - 20, cx0 + 4 * cw + 20, cy0 + 3 * chh + 20, fill=A((150, 100, 60), 1), r=16)
    for i in range(12):
        r_, c_ = divmod(i, 4); x, y = cx0 + c_ * cw, cy0 + r_ * chh
        d.rect(x + 10, y + 10, x + cw - 10, y + chh - 10, fill=A((84, 56, 38), 1), r=10)
        mx, my = x + cw / 2, y + chh / 2 + 18
        if i >= 11:
            d.text(mx, my - 18, "?", 60, A((160, 120, 90), 1), k=1); continue
        if i < 6:
            k = popk(t, t0 + 0.1 + i * 0.07, "bouncy")
            if k > 0: frog_icon(d, mx, my, 0.24 * min(1.05, k), 1, "grey", "sus", t + i)
        else:
            tj = t0 + 1.4 + (i - 6) * 0.3
            if t < tj: dbox(d, x + 26, y + 26, x + cw - 26, y + chh - 26, (200, 160, 120), 0.6, 3)
            else:
                yy = my + lerp(-200, 0, ease(pr(t, tj - 0.15, tj + 0.1)))
                frog_icon(d, mx, yy, 0.24, 1, cols[i], "happy", t + i)
                kk = popk(t, tj, "bouncy"); d.circ(x + cw - 30, y + 32, 20 * min(1.1, kk), fill=A((240, 60, 70), 1)); d.text(x + cw - 30, y + 32, "新", int(20 * min(1.1, kk)), A(WHITE, 1), k=1)

# ---------------- S15: knowledge card as a naming certificate on a green felt table ----------------
def s_card(t, d):
    t0 = T["card"]
    grad(d, (34, 80, 64), (16, 40, 32))
    k = popk(t, t0, "smooth"); a_ = min(1, k); y_ = (1 - a_) * 60
    d.rect(186, 416 + y_, 926, 1336 + y_, fill=A((0, 0, 0), 0.25 * a_), r=30)
    d.rect(170, 400 + y_, 910, 1320 + y_, fill=A((230, 196, 110), a_), r=30)
    d.rect(190, 420 + y_, 890, 1300 + y_, fill=A((250, 244, 226), a_), r=22)
    d.rect(330, 450 + y_, 750, 520 + y_, fill=A((210, 70, 60), a_), r=35); d.text(540, 485 + y_, "一句话学会", 40, A(WHITE, a_), k=1)
    d.text(540, 610 + y_, "新物种", 96, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("科学家第一次", "正式描述、起名的物种")):
        kk = ap(t, t0 + 0.6 + i * 0.5, 0.25)
        if kk > 0: d.text(540, 740 + i * 76 + y_, s_, 46, A(NAVYT, kk * a_), k=1)
    kk = ap(t, t0 + 1.8, 0.3)
    if kk > 0:
        d.rect(250, 920, 830, 924, fill=A((220, 200, 160), kk))
        frog_icon(d, 380, 1110, 0.38, kk, "rust", "proud", t)
        d.text(660, 1080, "J. tanogogo", 34, A(NAVYT, kk), k=0)
        d.text(660, 1140, "2026 年命名", 30, A((120, 110, 100), kk), k=1)
    sk = back(pr(t, t0 + 2.6, t0 + 2.78))
    if sk > 0:
        sz = 2 - sk; x, y = 790, 1230
        d.circ(x, y, 56 * sz, fill=A((200, 50, 50), min(1, sk * 1.5))); d.circ(x, y, 44 * sz, fill=A((220, 70, 60), min(1, sk * 1.5)))
        d.text(x, y, "名", int(48 * sz), A((255, 230, 210), min(1, sk * 1.5)), k=1)

# ---------------- S16: back to the opening forest ----------------
def s_end(t, d):
    t0 = T["end"]
    rainforest(d, t, 0.4, 1.0)
    frog(d, FX_ - 120, FY_ + 60, 1.0, t, 1, "happy", look=0.7)
    snail(d, 780, 1080, 0.55, t, 1, "sus", flip=-1, look=-0.5)
    k = popk(t, t0 + 0.2, "bouncy")
    if k > 0:
        bubble(d, 540, 430, 640 * min(1.05, k), 150, 0.95)
        d.text(540, 420, "谁还爱吃蜗牛？", int(56 * min(1.05, k)), A(NAVYT, 1), k=1)
    ra = ap(t, t0 + 1.8, 0.3)
    if ra > 0:
        d.rect(170, 560, 910, 720, fill=A((6, 8, 20), 0.7 * ra), r=20)
        d.text(540, 597, "Garg et al. 2026, R. Soc. Open Sci. 13:261030", 23, A(WHITE, 0.95 * ra), k=0)
        d.text(540, 638, "doi:10.1098/rsos.261030", 24, A(WHITE, 0.85 * ra), k=0)
        d.text(540, 680, "报道：BBC News 2026-11-12", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))
