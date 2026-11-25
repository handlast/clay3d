import math, random, sys, subprocess
from PIL import Image
from base import *
from fx import glow, sparks, shake, flash
from cues import *

PAPER = (248, 243, 228); GRID = (200, 215, 235); INKC = (40, 52, 92); BOLTC = (255, 206, 40); FIRE = (255, 120, 40)
SKY = (120, 130, 160); BEAR = (150, 95, 60); POND = (120, 180, 230); WOOD = (170, 120, 70)

def qt(t): return int(t * 12)  # boiling lines at 12 fps
def jit(seed, amt=2.6):
    r = random.Random(seed); return r.uniform(-amt, amt), r.uniform(-amt, amt)
def ink(d, pts, t, col=INKC, w=9, a=1.0, seed=0, amt=2.6, sub=18):
    out = []; q = qt(t)
    for i, ((x1, y1), (x2, y2)) in enumerate(zip(pts, pts[1:])):
        L = math.hypot(x2 - x1, y2 - y1); m = max(1, int(L / sub))
        for k in range(m):
            jx, jy = jit(hash((seed, i, k, q)) & 0xffffff, amt)
            out.append((lerp(x1, x2, k / m) + jx, lerp(y1, y2, k / m) + jy))
    jx, jy = jit(hash((seed, 99, q)) & 0xffffff, amt); out.append((pts[-1][0] + jx, pts[-1][1] + jy))
    d.line(out, A(col, a), w)
def ring(d, x, y, r, t, col=INKC, w=9, a=1.0, seed=0, fill=None, rx=None):
    rx = rx or r; n = max(14, int(r / 4))
    pts = [(x + rx * math.cos(2 * math.pi * k / n), y + r * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]
    if fill: d.ell(x, y, rx, r, A(fill, a))
    ink(d, pts, t, col, w, a, seed, 2.0)
def box(d, x0, y0, x1, y1, t, col=INKC, w=9, a=1.0, seed=0, fill=None):
    if fill: d.rect(x0, y0, x1, y1, fill=A(fill, a))
    ink(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], t, col, w, a, seed)
def dtext(d, x, y, s, size, col, a=1.0, t=0, seed=0):
    jx, jy = jit(hash((seed, qt(t))) & 0xffffff, 2.0)
    d.text(x + jx, y + jy, s, size, A(col, a), k=1)

def paper(d, t):
    d.rect(0, 0, OW, OH, fill=A(PAPER, 1))
    for y in range(120, 1920, 60): d.line([(0, y), (1080, y)], A(GRID, 0.55), 2)
    d.line([(110, 0), (110, 1920)], A((240, 150, 150), 0.6), 3)

def flame(d, x, y, s, t, a=1.0):
    glow(d, x, y - s * 0.4, s * 1.3, FIRE, 0.5 * a, 5)
    for k in range(5):
        fx = x + (k - 2) * s * 0.28; h = s * (0.9 + 0.35 * math.sin(t * 25 + k * 1.7))
        d.poly([(fx - s * 0.2, y), (fx + s * 0.2, y), (fx + 0.08 * s * math.sin(t * 30 + k), y - h)], A(FIRE, a))
        d.poly([(fx - s * 0.1, y), (fx + s * 0.1, y), (fx, y - h * 0.6)], A(BOLTC, a))

def stick(d, x, y, s, t, pose="stand", a=1.0, seed=1, fire=0.0, brows=True, mood="ok", col=INKC, w=None):
    """x,y = feet center. s = scale (~ body height/2)."""
    w = w or max(4, 9 * s / 100)
    hy = y - 2.25 * s; neck = (x, y - 1.95 * s); hip = (x, y - 1.0 * s)
    sh = (x, y - 1.75 * s)
    P_ = {"stand": ((-0.5, 0.5), (0.5, 0.5), (-0.3, 1.0), (0.3, 1.0)),
          "up": ((-0.6, -0.6), (0.6, -0.6), (-0.3, 1.0), (0.3, 1.0)),
          "zap": ((-0.8, -0.3), (0.8, -0.35), (-0.55, 0.95), (0.55, 0.95)),
          "run": ((-0.6, 0.1), (0.5, -0.3), (-0.6, 0.8), (0.55, 0.85)),
          "fall": ((-0.7, 0.0), (0.7, 0.0), (-0.5, 0.9), (0.5, 0.9)),
          "swing": ((0.3, -0.8), (0.8, -0.6), (-0.3, 1.0), (0.35, 1.0)),
          "pour": ((0.2, -0.9), (-0.5, 0.4), (-0.3, 1.0), (0.3, 1.0)),
          "sit": ((-0.5, 0.4), (0.6, 0.0), (-0.8, 0.5), (0.7, 0.5))}[pose]
    if pose == "run":
        ph = math.sin(t * 14); P_ = ((-0.6 * ph, 0.2), (0.6 * ph, 0.2), (-0.6 * ph, 0.9), (0.6 * ph, 0.9))
    if pose == "zap":
        j = math.sin(t * 60) * 0.12; P_ = tuple((dx + j, dy - j) for dx, dy in P_)
    la, ra, ll, rl = P_
    ink(d, [neck, hip], t, col, w, a, seed)
    ink(d, [sh, (x + la[0] * s, sh[1] + la[1] * s * 0.9)], t, col, w, a, seed + 1)
    ink(d, [sh, (x + ra[0] * s, sh[1] + ra[1] * s * 0.9)], t, col, w, a, seed + 2)
    ink(d, [hip, (x + ll[0] * s, hip[1] + ll[1] * s)], t, col, w, a, seed + 3)
    ink(d, [hip, (x + rl[0] * s, hip[1] + rl[1] * s)], t, col, w, a, seed + 4)
    ring(d, x, hy, 0.32 * s, t, col, w, a, seed + 5, fill=PAPER)
    # ranger hat
    ink(d, [(x - 0.45 * s, hy - 0.22 * s), (x + 0.45 * s, hy - 0.22 * s)], t, (110, 140, 80), w * 1.1, a, seed + 6)
    d.poly([(x - 0.22 * s, hy - 0.22 * s), (x + 0.22 * s, hy - 0.22 * s), (x, hy - 0.52 * s)], A((130, 160, 90), a))
    ex = 0.12 * s
    if mood == "x" or pose == "zap":
        for sx in (-1, 1):
            cx = x + sx * ex
            ink(d, [(cx - 0.05 * s, hy - 0.05 * s), (cx + 0.05 * s, hy + 0.05 * s)], t, col, w * 0.6, a, seed + 7 + sx)
            ink(d, [(cx - 0.05 * s, hy + 0.05 * s), (cx + 0.05 * s, hy - 0.05 * s)], t, col, w * 0.6, a, seed + 9 + sx)
        ring(d, x, hy + 0.15 * s, 0.06 * s, t, col, w * 0.6, a, seed + 11)
    else:
        for sx in (-1, 1): d.circ(x + sx * ex, hy - 0.02 * s, 0.035 * s + 1.5, fill=A(col, a))
        if mood == "ok": d.arc(x, hy + 0.08 * s, 0.12 * s, 0.08 * s, 20, 160, A(col, a), w * 0.6)
        elif mood == "sad": d.arc(x, hy + 0.2 * s, 0.11 * s, 0.07 * s, 200, 340, A(col, a), w * 0.6)
        elif mood == "o": ring(d, x, hy + 0.13 * s, 0.05 * s, t, col, w * 0.6, a, seed + 11)
    if brows:
        for sx in (-1, 1): ink(d, [(x + sx * ex - 0.06 * s, hy - 0.12 * s), (x + sx * ex + 0.06 * s, hy - 0.13 * s)], t, col, w * 0.5, a, seed + 13 + sx)
    if fire > 0: flame(d, x, hy - 0.4 * s, 0.38 * s * fire, t, a)

def bolt(d, x0, y0, x1, y1, t, t0, a=1.0, seed=3, w=26):
    u = pr(t, t0 - 0.12, t0)
    if u <= 0 or t > t0 + 0.55: return
    fade = 1 - pr(t, t0 + 0.25, t0 + 0.55)
    r = random.Random(seed + qt(t * 2)); n = 9; pts = [(x0, y0)]
    for k in range(1, n):
        f = k / n; pts.append((lerp(x0, x1, f) + r.uniform(-70, 70), lerp(y0, y1, f)))
    pts.append((x1, y1)); m = max(2, int(len(pts) * u)); pts = pts[:m]
    for (px, py) in pts[::2]: glow(d, px, py, 110, BOLTC, 0.25 * a * fade, 3)
    d.line(pts, A(BOLTC, a * fade), w); d.line(pts, A(WHITE, a * fade), w * 0.35)

def cloud(d, x, y, s, t, a=1.0, mood="mad", seed=20):
    for k, (dx, dy, r) in enumerate([(-0.6, 0.1, 0.45), (0, -0.15, 0.6), (0.6, 0.1, 0.45), (0.25, 0.25, 0.4), (-0.25, 0.25, 0.4)]):
        d.circ(x + dx * s, y + dy * s, r * s, fill=A(SKY, a))
    for k in (-1, 1):
        d.circ(x + k * 0.22 * s, y + 0.05 * s, 0.07 * s, fill=A(PAPER, a)); d.circ(x + k * 0.22 * s, y + 0.07 * s, 0.035 * s, fill=A(INKC, a))
        if mood == "mad": ink(d, [(x + k * 0.36 * s, y - 0.12 * s), (x + k * 0.1 * s, y - 0.02 * s)], t, INKC, 8, a, seed + k)
    d.arc(x, y + 0.32 * s, 0.14 * s, 0.07 * s, 200, 340, A(INKC, a), 7)

def tally(d, n, t, x=920, y=290, a=1.0):
    # 正 strokes: 1 横 2 竖 3 横 4 竖(left) 5 底横
    S_ = 46
    segs = [((-1, -1), (1, -1)), ((0, -1), (0, 1)), ((0, 0), (0.8, 0)), ((-0.7, -0.1), (-0.7, 1)), ((-1.1, 1), (1.1, 1))]
    for k in range(n):
        g, j = divmod(k, 5)
        (a1, b1), (a2, b2) = segs[j]; ox = x - g * 140 + (0 if g == 0 else 0)
        ox = x - 70 + g * 130 - (0 if n > 5 else -60)
        ink(d, [(ox + a1 * S_, y + b1 * S_), (ox + a2 * S_, y + b2 * S_)], t, (220, 60, 50), 12, a, 300 + k)

def subs(t, d):
    if t >= OUTRO: return
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            lines = wrap(d, s, 56, 900)
            for j, ln in enumerate(lines):
                y = 1660 + (j - (len(lines) - 1) / 2) * 82
                w = d.tlen(ln, 56)
                d.rect(540 - w / 2 - 24, y - 42, 540 + w / 2 + 24, y + 42, fill=A(INKC, 0.92 * al), r=16)
                d.text(540, y, ln, 56, A(WHITE, al))
            break

def brand(t, d):
    d.rect(50, 80, 300, 128, fill=A(INKC, 0.95), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(WHITE, 1))
    d.rect(740, 80, 1030, 128, fill=A((240, 170, 40), 1), r=24); d.text(885, 104, "脑洞系列 · 如果", 26, A(INKC, 1))

def pop(t, t0, k=0.25): return back(pr(t, t0, t0 + k))

# ---------- scenes ----------
def s_hook(t, d):
    paper(d, t)
    zap = BOLT0 <= t < BOLT0 + 1.2
    stick(d, 540, 1350, 190, t, "zap" if zap else "stand", fire=1.0 if t > BOLT0 else 0, mood="x" if t > BOLT0 + 1.2 else "o", brows=t < BOLT0)
    bolt(d, 600, 0, 540, 840, t, BOLT0, seed=1, w=34)
    if t > BOLT0: sparks(d, 540, 900, t, BOLT0, 50, 1300, BOLTC, 1, 2, 1.0)
    k = pop(t, BOLT0)
    if t < BOLT0: dtext(d, 540, 400, "如果被雷劈", 110, INKC, 1, t, 1)
    else:
        dtext(d, 540, 300, "如果被雷劈", 90, INKC, 1, t, 1)
        if k > 0: d.text(540, 470, "7 次", int(250 * (0.6 + 0.4 * k)) + 1, A((220, 60, 50), min(1, k * 1.5)), k=1)
        if t > 2.0: dtext(d, 540, 640, "真有人试过", 70, INKC, ease(pr(t, 2.0, 2.3)), t, 2)

def s_hot(t, d):
    paper(d, t)
    # thermometer
    lv = ease(pr(t, HOT, HOT_HIT))
    ring(d, 300, 1380, 70, t, INKC, 10, 1, 40, fill=(255, 120, 90))
    box(d, 265, 700, 335, 1320, t, INKC, 10, 1, 41)
    d.rect(280, 1320 - 600 * lv, 320, 1325, fill=A((255, 120, 90), 1))
    bolt(d, 300, 120, 300, 690, t, HOT_HIT, seed=7)
    if t > HOT_HIT: dtext(d, 640, 520, "约 2.8 万°C", 120, (220, 60, 50), min(1, pop(t, HOT_HIT) * 1.5), t, 3)
    # sun
    k = pop(t, SUN_HIT)
    if k > 0:
        sx, sy, r = 760, 1080, 150 * min(1, k)
        glow(d, sx, sy, r * 1.6, BOLTC, 0.4, 5); d.circ(sx, sy, r, fill=A((255, 196, 60), 1))
        for j in range(12):
            an = j * math.pi / 6 + t * 0.6
            ink(d, [(sx + math.cos(an) * r * 1.15, sy + math.sin(an) * r * 1.15), (sx + math.cos(an) * r * 1.45, sy + math.sin(an) * r * 1.45)], t, (240, 150, 40), 10, 1, 60 + j)
        d.circ(sx - 45, sy - 20, 10, fill=A(INKC, 1)); d.circ(sx + 45, sy - 20, 10, fill=A(INKC, 1)); d.arc(sx, sy + 40, 40, 25, 200, 340, A(INKC, 1), 8)
        dtext(d, 760, 1330, "太阳表面 ×5", 80, INKC, min(1, k), t, 4)

def s_surv(t, d):
    paper(d, t)
    for i in range(100):
        r_, c_ = divmod(i, 10); x = 150 + c_ * 87; y = 560 + r_ * 100
        dead = (i * 37) % 100 < 10
        k = pr(t, FALL + (i % 10) * 0.03, FALL + 0.3 + (i % 10) * 0.03)
        if dead and k > 0:
            col = mix(INKC, (190, 190, 200), k)
            stick(d, x, y, 34, t, "fall", seed=i, col=col, mood="x", brows=False, a=1)
        else:
            stick(d, x, y, 34, t, "up" if t > NINETY and not dead else "stand", seed=i, mood="ok", brows=False)
    if t > NINETY:
        k = pop(t, NINETY)
        d.text(540, 380, "≈ 90 个活下来", int(110 * (0.6 + 0.4 * k)) + 1, A((40, 150, 80), min(1, k * 1.5)), k=1)
    else: dtext(d, 540, 380, "100 个被雷劈的人", 90, INKC, 1, t, 5)

def s_fast(t, d):
    paper(d, t)
    stick(d, 330, 1350, 170, t, "zap" if FAST_HIT <= t < FAST_HIT + 0.5 else "stand", mood="o" if t > FAST_HIT else "ok")
    bolt(d, 380, 0, 330, 900, t, FAST_HIT, seed=9)
    # stopwatch
    cx, cy, r = 770, 1050, 190
    ring(d, cx, cy, r, t, INKC, 12, 1, 70, fill=WHITE)
    box(d, cx - 30, cy - r - 50, cx + 30, cy - r - 10, t, INKC, 10, 1, 71)
    an = -math.pi / 2 + (t - FAST) * 0.5 if t < FAST_HIT else -math.pi / 2 + 0.5 + min(1, (t - FAST_HIT) * 2) * 0.05
    ink(d, [(cx, cy), (cx + math.cos(an) * r * 0.8, cy + math.sin(an) * r * 0.8)], t, (220, 60, 50), 10, 1, 72)
    if t > FAST_HIT:
        k = pop(t, FAST_HIT)
        d.text(540, 380, "1/1000 ~ 1/10 秒", int(100 * (0.6 + 0.4 * k)) + 1, A((220, 60, 50), min(1, k * 1.5)), k=1)
        dtext(d, 540, 520, "一闪就过去了", 70, INKC, ease(pr(t, FAST_HIT + 0.6, FAST_HIT + 0.9)), t, 6)

def s_roy(t, d):
    paper(d, t)
    k = pop(t, ROY_HIT, 0.35)
    stick(d, 540, 1400, 230 * (0.7 + 0.3 * min(1, k)), t, "stand", mood="ok")
    dtext(d, 540, 400, "美国护林员", 100, INKC, min(1, k), t, 7)
    dtext(d, 540, 560, "Roy Sullivan", 80, (110, 140, 80), min(1, k), t, 8)
    for j in range(3):
        x = 230 + j * 310
        ink(d, [(x, 1400), (x, 1150)], t, WOOD, 14, 0.8, 90 + j)
        d.poly([(x - 90, 1200), (x + 90, 1200), (x, 950)], A((90, 160, 90), 0.6))

def scene_prop(k, t, d, ts):
    if k == 0:  # tower
        ink(d, [(220, 1420), (300, 760), (380, 1420)], t, WOOD, 12, 1, 100); box(d, 240, 680, 360, 770, t, WOOD, 12, 1, 101)
    elif k == 1:  # car
        box(d, 330, 1180, 900, 1400, t, INKC, 10, 1, 110, fill=(150, 200, 235)); box(d, 430, 1050, 780, 1180, t, INKC, 10, 1, 111)
        for wx in (450, 790): ring(d, wx, 1400, 55, t, INKC, 10, 1, 112 + wx, fill=(90, 95, 110))
    elif k == 2:  # yard + pole
        ink(d, [(860, 1420), (860, 760)], t, WOOD, 14, 1, 120); box(d, 820, 820, 900, 900, t, INKC, 9, 1, 121, fill=(180, 180, 190))
        for j in range(5): ink(d, [(150 + j * 60, 1420), (150 + j * 60, 1340)], t, (90, 160, 90), 8, 1, 122 + j)
    elif k == 3:  # station
        box(d, 250, 900, 830, 1420, t, INKC, 10, 1, 130, fill=(240, 225, 200)); ink(d, [(220, 900), (540, 720), (860, 900)], t, (200, 80, 60), 12, 1, 131)
    elif k == 6:  # pond
        d.ell(540, 1460, 400, 70, A(POND, 0.8))
    if k in (4, 5):  # chasing cloud
        cx = lerp(150, 560, ease(pr(t, ts, ts + 0.5))); cloud(d, cx, 700, 150, t)

def s_strikes(t, d):
    paper(d, t)
    k = min(6, int((t - STRIKE0) / SDUR)); ts = STRIKE0 + k * SDUR; tb = STRIKES[k]
    year, where, what = YEARS[k]
    scene_prop(k, t, d, ts)
    hit = tb <= t < tb + 0.5; after = t >= tb + 0.5
    px = {0: 560, 1: 600, 2: 560, 3: 540, 4: 600, 5: lerp(300, 700, pr(t, ts, tb)), 6: 420}[k]
    py = {1: 1290}.get(k, 1420)
    s = 150 if k != 1 else 110
    pose = "zap" if hit else ({4: "pour", 5: "run", 6: "swing"}.get(k, "stand") if after else ({5: "run", 6: "stand"}.get(k, "stand")))
    fire = 1.0 if (after and k in (3, 4, 6)) else 0.0
    stick(d, px, py, s, t, pose, fire=fire, brows=not (k >= 1 and t > STRIKES[1]), mood="sad" if after else "ok", seed=200 + k)
    tx, ty = (px, py - 2.3 * s) if k not in (2,) else (860, 820)
    if k == 2 and t < tb + 0.3: bolt(d, 900, 0, 860, 820, t, tb - 0.05, seed=50)
    bolt(d, px + 40, 0, tx, ty, t, tb, seed=30 + k)
    if k == 2: bolt(d, 860, 860, px + 0.6 * s, py - 1.8 * s, t, tb + 0.12, seed=60, w=16)
    if hit: sparks(d, px, py - 1.6 * s, t, tb, 40, 1100, BOLTC, 1, k, 1.0)
    if after:
        if k == 0: ring(d, px + 0.3 * s, py, 18, t, (220, 60, 50), 8, 1, 400)
        if k == 2: ring(d, px - 0.0 * s, py - 1.75 * s, 34, t, (220, 60, 50), 8, 1, 401)
        if k == 5: ring(d, px + 0.3 * s, py - 0.1 * s, 26, t, (220, 60, 50), 8, 1, 402)
        if k == 4:  # water can
            box(d, px + 10, py - 3.0 * s, px + 90, py - 2.6 * s, t, INKC, 8, 1, 403, fill=(160, 170, 190))
            for j in range(5): d.circ(px + 20 + j * 12, py - 2.5 * s + ((t * 400 + j * 30) % 80), 8, fill=A(POND, 1))
        if k == 6:  # bear
            bx = 820 - 60 * ease(pr(t, tb + 0.5, tb + 1.2))
            ring(d, bx, 1240, 120, t, BEAR, 12, 1, 410, fill=(200, 150, 110), rx=150)
            ring(d, bx - 110, 1130, 60, t, BEAR, 10, 1, 411, fill=(200, 150, 110))
            for ex_ in (-140, -80): ring(d, bx + ex_, 1078, 18, t, BEAR, 8, 1, 412 + ex_, fill=(200, 150, 110))
            d.circ(bx - 125, 1125, 7, fill=A(INKC, 1)); d.circ(bx - 95, 1125, 7, fill=A(INKC, 1))
            for lx in (-80, 80): ink(d, [(bx + lx, 1340), (bx + lx, 1410)], t, BEAR, 16, 1, 415 + lx)
            ink(d, [(px + 0.8 * s, py - 2.3 * s), (bx - 150, 1080)], t, WOOD, 12, 1, 418)
            if t > tb + 1.2: dtext(d, bx - 110, 980, "！", 90, (220, 60, 50), 1, t, 419)
    # year + caption
    kk = pop(t, ts, 0.2)
    d.text(330, 300, year, int(140 * (0.6 + 0.4 * kk)) + 1, A(INKC, min(1, kk * 1.5)), k=1)
    tally(d, k + (1 if t >= tb else 0), t)
    if after: dtext(d, 540, 470, what, 66 if len(what) < 9 else 56, (220, 60, 50), ease(pr(t, tb + 0.5, tb + 0.7)), t, 500 + k)

def s_guin(t, d):
    paper(d, t)
    for j in range(16):
        an = j * math.pi / 8 + t * 0.3
        ink(d, [(540 + math.cos(an) * 260, 1050 + math.sin(an) * 260), (540 + math.cos(an) * 420, 1050 + math.sin(an) * 420)], t, BOLTC, 14, 1, 600 + j)
    k = pop(t, GUIN_HIT)
    stick(d, 540, 1300, 170, t, "up", mood="ok", brows=False, fire=0.6)
    if k > 0:
        d.rect(140, 330, 940, 600, fill=A((220, 60, 50), min(1, k)), r=30)
        d.text(540, 410, "吉尼斯世界纪录", int(90 * (0.6 + 0.4 * k)) + 1, A(WHITE, min(1, k * 1.5)), k=1)
        d.text(540, 525, "被雷劈次数最多", int(70 * (0.6 + 0.4 * k)) + 1, A(WHITE, min(1, k * 1.5)), k=1)
    tally(d, 7, t, 920, 730)

def s_safe(t, d):
    paper(d, t)
    k = pop(t, SAFE_HIT)
    box(d, 120, 900, 500, 1400, t, INKC, 10, 1, 700, fill=(240, 225, 200)); ink(d, [(90, 900), (310, 740), (530, 900)], t, (200, 80, 60), 12, 1, 701)
    stick(d, 310, 1380, 110, t, "stand", mood="ok", brows=True)
    box(d, 600, 1170, 1000, 1360, t, INKC, 10, 1, 702, fill=(150, 200, 235)); box(d, 670, 1060, 920, 1170, t, INKC, 10, 1, 703, fill=(210, 235, 250))
    for wx in (680, 920): ring(d, wx, 1360, 45, t, INKC, 10, 1, 704 + wx, fill=(90, 95, 110))
    cloud(d, 540, 560, 160, t, mood="sad")
    if k > 0:
        for x in (310, 800): d.text(x, 760 if x == 310 else 990, "✓" if False else "OK", 70, A((40, 150, 80), min(1, k)), k=1)
    dtext(d, 540, 330, "打雷时这样躲", 90, INKC, 1, t, 705)

def bubble(d, x, y, s, side, col, tcol, a, size=50):
    w = d.tlen(s, size) + 70; x0 = x - w if side > 0 else x
    d.rect(x0, y - size * 1.1, x0 + w, y + size * 1.1, fill=A(col, a), r=40); d.text(x0 + w / 2, y, s, size, A(tcol, a), k=1)
def s_end(t, d):
    paper(d, t)
    d.rect(0, 160, 1080, 260, fill=A(INKC, 1)); d.text(540, 210, "同学群（48）", 44, A(WHITE, 0.95), k=1)
    d.text(540, 380, "明天这样说 ↓", 80, A((220, 60, 50), ease(pr(t, OUTRO, OUTRO + 0.3))), k=1)
    if t > BUB1: bubble(d, 1010, 640, "有人被雷劈了 7 次还活着", 1, (120, 220, 120), (20, 40, 20), min(1, pop(t, BUB1)), 56)
    if t > BUB1 + 0.6: bubble(d, 1010, 830, "被雷劈的人九成能活下来", 1, (120, 220, 120), (20, 40, 20), min(1, pop(t, BUB1 + 0.6)), 56)
    if t > BUB2: bubble(d, 70, 1020, "？？？真的假的", -1, (90, 100, 130), WHITE, min(1, pop(t, BUB2)), 64)
    if t > BUB2 + 0.7: bubble(d, 1010, 1210, "吉尼斯纪录，自己查", 1, (120, 220, 120), (20, 40, 20), min(1, pop(t, BUB2 + 0.7)), 52)
    d.text(540, 1780, "CDC Lightning Strike Victim Data · NWS: How Hot Is Lightning?", 24, A(INKC, 0.75), k=0)
    d.text(540, 1815, "Guinness World Records · StatPearls: Lightning Injuries", 24, A(INKC, 0.75), k=0)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

SECS = [(0, HOOK_END, s_hook), (HOT, SURV, s_hot), (SURV, FAST, s_surv), (FAST, ROY, s_fast), (ROY, STRIKE0, s_roy),
        (STRIKE0, GUIN, s_strikes), (GUIN, SAFE, s_guin), (SAFE, OUTRO, s_safe), (OUTRO, 99, s_end)]
CUTS = [HOOK_END, SURV, FAST, ROY, STRIKE0, GUIN, SAFE, OUTRO] + [STRIKE0 + k * SDUR for k in range(1, 7)]

def cam(t):
    z = 1.0 + 0.06 * pulse(t, HITS, 7)
    for a, b in RISERS:
        if a <= t < b: z += 0.08 * eio(pr(t, a, b))
    amp = 26 * pulse(t, [BOLT0] + STRIKES, 4) + 10 * pulse(t, HITS, 6)
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx, 960 + sy

def frame(t):
    img = Image.new("RGB", (W, H), PAPER); d = D(img)
    for a, b, sf in SECS:
        if a <= t < b: sf(t, d); break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for h in [BOLT0] + STRIKES + [HOT_HIT, FAST_HIT]:
        if h <= t < h + 0.12: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.7 * (1 - (t - h) / 0.12)))
    for c in CUTS:
        if c <= t < c + 0.08: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.5 * (1 - (t - c) / 0.08)))
    if SILENCES[0][0] <= t < SILENCES[0][1]: d.rect(0, 0, OW, OH, fill=A(INKC, 0.35))
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
