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

def stick(d, x, y, s, t, pose="stand", a=1.0, seed=1, fire=0.0, brows=True, mood="ok", col=INKC, w=None, hat=True, tired=0.0, hair=False):
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
    if hair:
        for j in range(5): ink(d, [(x + (j - 2) * 0.1 * s, hy - 0.3 * s), (x + (j - 2) * 0.14 * s + 0.03 * s * math.sin(t * 3 + j) * tired, hy - 0.45 * s)], t, col, w * 0.8, a, seed + 30 + j)
    if hat:
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
    if tired > 0:
        for sx in (-1, 1):
            d.arc(x + sx * ex, hy + 0.04 * s, 0.07 * s, 0.045 * s, 0, 180, A((150, 90, 170), a * min(1, tired)), max(2, w * 0.5 * tired))
            if tired > 0.5: ink(d, [(x + sx * ex - 0.06 * s, hy - 0.04 * s), (x + sx * ex + 0.06 * s, hy - 0.04 * s)], t, col, w * 0.6, a, seed + 40 + sx)
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

