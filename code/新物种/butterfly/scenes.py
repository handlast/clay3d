# 《这只蝴蝶躲了200年？》scenes — every subtitle line gets its OWN set (user rule 2026-11-16).
# Flat 2D, no dark outlines. Content x 180–900, above subtitle box (y < ~1230). Entities spring in and fade >= 0.3 s.
import math, random
from PIL import Image, ImageDraw
from bchars import *
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
TRIO_X = [270, 540, 810]

# ======== 1. hook: three identical butterflies line up — "撞脸" ========
def s_hook(t, d):
    u = t
    forest(d, t, (54, 140, 100), (16, 60, 50), 4)
    spot(d, 540, 760, 620, 1.0, (255, 250, 220))
    for i, x in enumerate(TRIO_X):
        kk = popk(t, -0.15 + i * 0.12, "bouncy")
        if kk <= 0: continue
        yy = 760 + 12 * math.sin(t * 2.2 + i) + hop(u, -0.15 + i * 0.12, 60, 0.4)
        bfly(d, x, yy, 0.78 * min(1.12, kk), t, 1, 1.0, "shock" if u < 1.6 else "calm", look=(1 - i) * 0.6, seed=0.0)   # same seed = same flap
    for j, x in enumerate((405, 675)):
        al = ap(u, 0.45 + j * 0.1, 0.2)
        if al > 0: d.text(x, 1000, "=", 110, A(GOLD, al), k=1)
    zap(d, 540, 760, t, 0.0, WHITE, 560, 0.7)
    bigword(d, t, 0.0, 540, 470, "撞脸！", 190, GOLD, 3.2)
    for i in range(3):                                                    # photocopy flash bars
        v = u - 0.9 - i * 0.6
        if 0 <= v < 0.5: d.rect(170, 1080 - v * 600, 910, 1100 - v * 600, fill=A((220, 255, 240), 0.5 * (1 - v / 0.5)), r=8)

# ======== 2. one: museum drawer, every specimen pinned under ONE name; odometer 0 → 200+ years ========
def s_one(t, d):
    t0 = T["one"]; u = t - t0
    grad(d, (92, 64, 46), (48, 30, 24))
    sbox(d, 170, 410, 910, 1090, (150, 104, 66), 1, 26)
    d.rect(200, 440, 880, 1060, fill=A((238, 228, 204), 1), r=14)
    for r_ in range(3):
        for c_ in range(3):
            i = r_ * 3 + c_; kk = popk(t, t0 + 0.15 + i * 0.12)
            if kk <= 0: continue
            cx, cy = 320 + c_ * 220, 560 + r_ * 190
            bfly(d, cx, cy, 0.42 * min(1.1, kk), t, ap(u, 0.15 + i * 0.12, 0.2), 0, "calm", seed=i * 0.13)
            d.circ(cx, cy - 26, 6, fill=A((200, 60, 60), 1))
    ka = popk(t, t0 + 1.4)
    if ka > 0:
        sbox(d, 380, 1100 - 60 * min(1, ka) + 60, 700, 1180 - 60 * min(1, ka) + 60, (250, 246, 230), ap(u, 1.4, 0.2), 16)
        d.text(540, 1140 - 60 * min(1, ka) + 60, "C. dirce · 1 种", 40, A(NAVYT, ap(u, 1.4, 0.2)), k=1)
    n = int(200 * E.ease_out_cubic(pr(u, 0.6, 2.8)))
    al = ap(u, 0.5, 0.2)
    if al > 0:
        sbox(d, 300, 270, 780, 390, (30, 22, 18), 0.8 * al, 30)
        d.text(540, 330, f"{n}{'+' if n >= 200 else ''} 年", 92, A(GOLD, al), k=1)

# ======== 3. q: spotlight, magnifier sweeps over the trio, question marks ========
def s_q(t, d):
    t0 = T["q"]; u = t - t0
    grad(d, (24, 26, 40), (8, 8, 14))
    spot(d, 540, 800, 600, 1.2, (220, 230, 255))
    for i, x in enumerate(TRIO_X):
        bfly(d, x, 820 + 8 * math.sin(t * 2 + i), 0.7, t, 1, 0.6, "shy" if i == 1 else "calm", look=(1 - i) * 0.5)
        bigword(d, t, t0 + 0.3 + i * 0.25, x, 560, "?", 140, mix((200, 210, 255), WHITE, 0.3))
    mx = 540 + 270 * math.sin(u * 2.2); my = 840; ma = ap(u, 0.2, 0.3)
    if ma > 0:
        d.circ(mx, my, 120, fill=A((230, 240, 255), 0.16 * ma)); d.circ(mx, my, 120, outline=A((240, 240, 230), ma), w=12)
        d.line([(mx + 86, my + 86), (mx + 160, my + 160)], A((180, 150, 110), ma), 26)

# ======== 4. BIG2: UV lamp on — each wing glows a different colour ========
def s_big2(t, d):
    t0 = T["big2"]; u = t - t0
    grad(d, (40, 14, 70), (10, 4, 24))
    for i in range(10):
        ang = -math.pi / 2 + (i - 4.5) * 0.11; L = 1500
        d.poly([(540, 250), (540 + math.cos(ang - 0.05) * L, 250 - math.sin(ang - 0.05) * -L), (540 + math.cos(ang + 0.05) * L, 250 - math.sin(ang + 0.05) * -L)], A((170, 90, 255), 0.05 + 0.03 * math.sin(t * 9 + i)))
    d.rect(400, 210, 680, 270, fill=A((90, 70, 120), 1), r=20); d.rect(420, 262, 660, 286, fill=A((210, 160, 255), 0.9 + 0.1 * math.sin(t * 30)), r=10)
    for i, x in enumerate(TRIO_X):
        uv = E.ease_out_cubic(pr(u, 0.15 + i * 0.35, 0.65 + i * 0.35))
        bfly(d, x, 800 + 10 * math.sin(t * 2 + i), 0.8, t, 1, 0.8, "shock" if uv > 0.5 and u < 3 else "happy", uv=uv, uvi=i, look=(1 - i) * 0.4)
        zap(d, x, 800, t, t0 + 0.15 + i * 0.35, UVC[i], 260, 0.8)
    bigword(d, t, t0 + 0.02, 540, 460, "紫外模式", 160, (230, 200, 255))
    for i in range(18):
        v = (u * 0.4 + i * 0.137) % 1; px = 200 + (i * 137) % 680; py = 1150 - v * 700
        d.circ(px, py, 5, fill=A(UVC[i % 3], 0.6 * math.sin(math.pi * v)))

# ======== 5. nm: spectrometer readout — 344 / 370 / 376 nm on a UV ruler ========
def s_nm(t, d):
    t0 = T["nm"]; u = t - t0
    grad(d, (22, 30, 52), (10, 12, 26)); grid(d, (80, 110, 160), 0.18, 80)
    sbox(d, 180, 330, 900, 1150, (232, 236, 244), 1, 30)
    d.rect(220, 380, 860, 460, fill=A((40, 50, 80), 1), r=16); d.text(540, 420, "UV 光谱仪", 40, A((180, 220, 255), 1), k=1)
    x0, x1 = 240, 840
    for i in range(61): d.rect(x0 + i * 10, 900, x0 + i * 10 + 10, 960, fill=A(mix((120, 60, 200), (90, 140, 255), i / 60), 1))
    def X(nm): return x0 + (nm - 335) / (385 - 335) * (x1 - x0)
    for nm_ in (340, 360, 380): d.text(X(nm_), 995, str(nm_), 30, A((80, 90, 110), 1), k=1)
    for j, (nm_, i) in enumerate(((376, 0), (370, 1), (344, 2))):
        kk = popk(t, t0 + 0.4 + j * 0.55)
        if kk <= 0: continue
        al = ap(u, 0.4 + j * 0.55, 0.2); xx = X(nm_); top = 560 + j * 95
        d.line([(xx, top + 50), (xx, 900)], A(UVC[i], al), 8)
        bfly(d, xx, top, 0.3 * min(1.1, kk), t, al, 0.8, "happy", uv=1, uvi=i, seed=j)
        tag(d, xx + (110 if j < 2 else 130) * (1 if j == 2 else -1), top + 4, f"{nm_} nm", UVC[i], al, 34)
    d.text(540, 1080, "平均反射峰", 30, A((110, 116, 130), ap(u, 2.0, 0.3)), k=1)

# ======== 6. cat: caterpillar munching a Cecropia leaf ========
def s_cat(t, d):
    t0 = T["cat"]; u = t - t0
    forest(d, t, (70, 150, 96), (20, 70, 52), 7)
    cecropia(d, 540, 820, 380, 1, 0.0)
    bites = int(min(6, u * 2))
    for j in range(bites): d.circ(760 - j * 10, 560 + j * 26, 34 + 4 * (j % 2), fill=A((44, 112, 74), 1))
    cx = lerp(900, 640, E.ease_out_cubic(pr(u, 0, 1.6)))
    cater(d, cx, 700, 1.15, t, 1, "tear", "munch" if u > 1.6 else "calm", 1.0 if u < 1.6 else 0.3)
    for j in range(5):                                                      # spines glint
        v = u - 1.8 - j * 0.3
        if 0 <= v < 0.5: d.circ(cx - j * 39 * 1.15, 620, 18 * (1 - v * 2) + 4, fill=A(WHITE, 0.7 * (1 - v / 0.5)))
    ptag(d, t, t0 + 0.8, 380, 1130, "号角树叶 Cecropia", (230, 250, 220), 36)

# ======== 7. marks: three caterpillars stacked + magnifier lenses on teardrop / ring / nothing ========
def s_marks(t, d):
    t0 = T["marks"]; u = t - t0
    grad(d, (240, 236, 222), (210, 204, 186))
    for i, mk in enumerate(("tear", "ring", "none")):
        yy = 480 + i * 270; kx = lerp(-300, 0, E.ease_out_cubic(pr(u, i * 0.9, i * 0.9 + 0.6)))
        al = ap(u, i * 0.9, 0.3)
        if al <= 0: continue
        cater(d, 840 + kx, yy, 1.05, t, al, mk, "shock" if (mk == "none" and u > 3.0) else "calm", 0.5, seed=i)
        lx, ly = 360 + kx, yy + 4; lk = popk(t, t0 + i * 0.9 + 0.6)
        if lk > 0:
            r = 74 * min(1.1, lk)
            d.circ(lx, ly, r, fill=A((250, 246, 230), al)); d.circ(lx, ly, r * 0.7, fill=A(CATK, al))
            if mk == "tear":
                d.circ(lx, ly + 10, 16, fill=A(CREAM, al)); d.poly([(lx - 13, ly + 3), (lx + 13, ly + 3), (lx, ly - 30)], A(CREAM, al))
            elif mk == "ring": d.circ(lx, ly, 26, outline=A(CREAM, al), w=10)
            else: d.text(lx, ly, "?", 60, A((130, 120, 140), al), k=1)
            d.circ(lx, ly, r, outline=A((200, 170, 120), al), w=10)
        tag(d, 640 + kx, yy - 110, SPN[i], (60, 54, 70), al, 28, WHITE, k=0)

# ======== 8. sepp: 1852 old book, quill draws two caterpillars, ≠ ========
def s_sepp(t, d):
    t0 = T["sepp"]; u = t - t0
    grad(d, (96, 70, 52), (52, 36, 28))
    sbox(d, 170, 340, 910, 1150, (236, 216, 170), 1, 18); d.rect(536, 350, 544, 1140, fill=A((200, 176, 130), 1))
    for j in range(8): d.line([(210, 800 + j * 36), (500, 800 + j * 36)], A((170, 140, 100), 0.6 * ap(u, 0.2 + j * 0.1, 0.2)), 4)
    a1 = ap(u, 0.5, 0.5); a2 = ap(u, 1.6, 0.5)
    cater(d, 480, 620, 0.8, t, a1, "tear", "calm", 0.0, n=7)
    cater(d, 856, 620, 0.8, t, a2, "ring", "calm", 0.0, n=7)
    if u > 0.5:                                                          # quill moving
        qx = lerp(300, 860, pr(u, 0.5, 2.6)); qy = 560 + 30 * math.sin(u * 12)
        qa = 1 - pr(u, 2.6, 3.0)
        if qa > 0:
            d.poly([(qx, qy), (qx + 30, qy - 200), (qx + 90, qy - 260), (qx + 20, qy - 60)], A(WHITE, qa)); d.line([(qx, qy), (qx + 16, qy - 60)], A((90, 70, 60), qa), 5)
    bigword(d, t, t0 + 2.4, 540, 900, "≠", 200, (200, 60, 50))
    sk = popk(t, t0 + 0.1, "bouncy")
    if sk > 0:
        sc = 1.5 - 0.5 * min(1, sk); al = ap(u, 0.1, 0.2)
        d.circ(720, 900, 100 * sc, outline=A((190, 50, 40), al), w=10 * sc); d.text(720, 900, "1852", int(52 * sc), A((190, 50, 40), al), k=1)

# ======== 9. no: heads shake "no", a timeline bar crawls 1852 → 2001 ========
def s_no(t, d):
    t0 = T["no"]; u = t - t0
    grad(d, (70, 76, 96), (30, 32, 44))
    for i in range(4):
        x = 270 + i * 180; sh = 14 * math.sin(u * 10 + i) * (1 - pr(u, 2.0, 2.5)); al = ap(u, i * 0.15, 0.3)
        d.circ(x + sh, 560, 70, fill=A((236, 200, 170), al)); d.rect(x - 80, 640, x + 80, 820, fill=A([(90, 120, 170), (150, 90, 90), (90, 140, 110), (130, 110, 160)][i], al), r=40)
        for sd in (-1, 1): d.circ(x + sh + sd * 22, 550, 8, fill=A(INK, al))
        d.arc(x + sh, 600, 20, 10, 200, 340, A(INK, al), 5)
        xmark(d, x, 400, 34, (230, 80, 70), al, pr(u, 0.4 + i * 0.15, 0.8 + i * 0.15))
    sbox(d, 200, 930, 880, 1060, (240, 240, 236), 1, 30)
    k = E.ease_in_out_sine(pr(u, 0.5, 3.4)); d.rect(220, 970, 220 + 640 * k, 1020, fill=A((230, 170, 60), 1), r=25)
    yr = int(1852 + 149 * k); d.text(540, 995, f"{yr}", 44, A(NAVYT, 1), k=1)
    d.text(240, 1100, "1852", 30, A(WHITE, 0.8), k=1); d.text(840, 1100, "2001", 30, A(WHITE, 0.8), k=1)

# ======== 10. y2001: drawer gets a second slot — a new name card stamped 2001 ========
def s_y2001(t, d):
    t0 = T["y2001"]; u = t - t0
    grad(d, (110, 80, 56), (56, 38, 28))
    sbox(d, 170, 380, 910, 1100, (150, 104, 66), 1, 26)
    for j in range(2):
        x0 = 200 + j * 350; d.rect(x0, 410, x0 + 330, 1070, fill=A((238, 228, 204), 1), r=14)
    bfly(d, 365, 640, 0.6, t, 1, 0, "calm")
    d.text(365, 880, "dirce", 40, A(NAVYT, 1), k=0)
    k = E.ease_out_cubic(pr(u, 0.2, 1.2))
    bfly(d, lerp(980, 715, k), lerp(300, 640, k), 0.6, t, ap(u, 0.2, 0.3), 1.0 if k < 1 else 0, "happy")
    ptag(d, t, t0 + 1.3, 715, 880, "annulata", (250, 246, 230), 40, NAVYT, k=0)
    sk = popk(t, t0 + 1.8, "bouncy")
    if sk > 0:
        sc = 1.5 - 0.5 * min(1, sk); al = ap(u, 1.8, 0.2)
        d.circ(800, 980, 72 * sc, outline=A((40, 150, 90), al), w=8 * sc); d.text(800, 980, "2001", int(40 * sc), A((40, 150, 90), al), k=1)
    d.text(540, 325, "第 2 种", 90, A(GOLD, ap(u, 1.4, 0.3)), k=1)

# ======== 11. dna: barcode strips split three ways, third drawer slot fills ========
def s_dna(t, d):
    t0 = T["dna"]; u = t - t0
    grad(d, (24, 60, 72), (8, 22, 30)); grid(d, (90, 200, 210), 0.12, 70)
    tag(d, 540, 430, "DNA 条形码", (90, 200, 210), ap(u, 0, 0.3), 44)
    rr = random.Random(9); bars = [[rr.random() for _ in range(20)] for _ in range(3)]
    for i in range(3):
        x0 = 210 + i * 230; al = ap(u, 0.5 + i * 0.4, 0.3)
        if al <= 0: continue
        sbox(d, x0, 520, x0 + 200, 980, (236, 244, 246), al, 20)
        sh = rr.random()
        for j in range(20):
            v = bars[i][j] if i == 0 else (bars[0][j] if (j + i) % 3 else 1 - bars[0][j])
            d.rect(x0 + 20, 540 + j * 21, x0 + 20 + 160 * (0.25 + 0.75 * v) * pr(u, 0.5 + i * 0.4 + j * 0.03, 0.8 + i * 0.4 + j * 0.03), 552 + j * 21, fill=A(UVC[i], al), r=5)
        bfly(d, x0 + 100, 1060, 0.3, t, al, 0.6, "happy", uv=0.3, uvi=i, seed=i)
    check_mark(d, 790, 470, 46, (60, 190, 110), 1, popk(t, t0 + 2.4, "bouncy"))
    ptag(d, t, t0 + 1.0, 540, 1180, "佛罗里达自然史博物馆", (230, 250, 250), 34)

# ======== 12. name: a butterfly hides behind a Cecropia leaf — dictionary card "cryptica" ========
def s_name(t, d):
    t0 = T["name"]; u = t - t0
    forest(d, t, (60, 130, 90), (20, 60, 46), 11)
    hide = E.ease_in_out_sine(pr(u, 0.8, 1.6)) * (1 - 0.6 * E.ease_in_out_sine(pr(u, 2.6, 3.2)))
    bfly(d, 540 + 260 * (1 - hide), 760, 0.75, t, 1, 0.5, "shy" if hide > 0.5 else "happy", look=-0.6)
    cecropia(d, 560, 790, 260, ap(u, 0.3, 0.4), 0.2)
    kk = popk(t, t0 + 0.2)
    if kk > 0:
        al = ap(u, 0.2, 0.2); y0 = 330 + (1 - min(1, kk)) * 60
        sbox(d, 220, y0, 860, y0 + 190, (250, 246, 232), al, 24)
        d.text(540, y0 + 70, "crypt·ica", 66, A((150, 70, 200), al), k=0)
        d.text(540, y0 + 145, "拉丁词根 crypt = 隐藏", 34, A((110, 100, 90), al), k=1)

# ======== 13. same: one forest, three butterflies — lines between them crossed out ========
def s_same(t, d):
    t0 = T["same"]; u = t - t0
    forest(d, t, (40, 110, 86), (12, 46, 40), 21)
    pos = [(300, 560), (780, 640), (520, 960)]
    for i, (x, y) in enumerate(pos):
        bfly(d, x + 40 * math.sin(t * 0.9 + i * 2), y + 30 * math.sin(t * 1.3 + i), 0.55, t, ap(u, i * 0.2, 0.3), 1.0, "calm", uv=0.35, uvi=i, seed=i * 0.3)
    for j, (a_, b_) in enumerate(((0, 1), (1, 2), (2, 0))):
        (xa, ya), (xb, yb) = pos[a_], pos[b_]; k = pr(u, 0.8 + j * 0.3, 1.3 + j * 0.3)
        if k <= 0: continue
        dashed(d, [(xa, ya), (lerp(xa, xb, k), lerp(ya, yb, k))], WHITE, 0.7, 5)
        xmark(d, (xa + xb) / 2, (ya + yb) / 2, 30, (240, 80, 80), 1, pr(u, 1.6 + j * 0.3, 2.0 + j * 0.3))
    ptag(d, t, t0 + 0.4, 540, 330, "同一片雨林", (230, 250, 230), 44)

# ======== 14. end: back to the trio; UV blinks on and off; one winks ========
def s_end(t, d):
    t0 = T["end"]; u = t - t0
    forest(d, t, (54, 140, 100), (16, 60, 50), 4)
    spot(d, 540, 760, 620, 1.0, (255, 250, 220))
    fl = 0.5 + 0.5 * math.sin(u * 2.4 - 1.5)
    fl *= ap(u, 0.8, 0.5)
    for i, x in enumerate(TRIO_X):
        bfly(d, x, 760 + 12 * math.sin(t * 2.2 + i), 0.78, t, 1, 1.0, "happy" if i == 2 and u > 2.0 else "calm", uv=fl, uvi=i, look=(1 - i) * 0.6)
    bigword(d, t, t0 + 2.2, 540, 470, "1 种？", 170, GOLD)
