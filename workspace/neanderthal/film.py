import sys, subprocess
from fx import *
from cues import *

BONE = (242, 228, 198); BONE_D = (204, 184, 148); BONE_L = (255, 248, 230); HOLEC = (46, 30, 24)
SKN = (232, 178, 128); SKN_D = (204, 146, 100); SKN_B = (214, 156, 110); HAIR = (92, 58, 36); BEARD = (118, 76, 46)
FUR = (156, 104, 62); FUR_D = (118, 76, 44); FUR_L = (196, 146, 96)
TAN = (220, 176, 112); TAN_D = (178, 136, 80); CHK = (128, 84, 52); BRASS = (226, 182, 70)
NAVYT = (24, 20, 40); GOOD = (90, 220, 120); BAD = (250, 70, 70); GOLD = (255, 200, 60)
WOOD = (170, 112, 62); WOOD_D = (118, 74, 40); WOOD_L = (214, 160, 100); FLINT = (130, 136, 150); FLINT_L = (184, 190, 204)
XRC = (90, 200, 255); HEARTC = (255, 92, 130); CALCC = (226, 200, 120)

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
def check(d, x, y, s, k, col, a=1.0):
    p = [(x - s, y), (x - s * 0.3, y + s * 0.7), (x + s, y - s * 0.8)]
    if k <= 0: return
    if k < 0.5: d.line([p[0], (lerp(p[0][0], p[1][0], k * 2), lerp(p[0][1], p[1][1], k * 2))], A(col, a), s * 0.3)
    else: d.line([p[0], p[1], (lerp(p[1][0], p[2][0], (k - 0.5) * 2), lerp(p[1][1], p[2][1], (k - 0.5) * 2))], A(col, a), s * 0.3)
def cross(d, x, y, s, k, col, a=1.0):
    if k <= 0: return
    d.line([(x - s, y - s), (x - s + 2 * s * min(1, k * 2), y - s + 2 * s * min(1, k * 2))], A(col, a), s * 0.3)
    if k > 0.5: d.line([(x + s, y - s), (x + s - 2 * s * (k - 0.5) * 2, y - s + 2 * s * (k - 0.5) * 2)], A(col, a), s * 0.3)
def dust(d, t, a=0.4, n=34, col=(255, 236, 200)):
    for i in range(n):
        u = (t * 0.06 + i * 0.137) % 1; x = 180 + (i * 211) % 720 + 16 * math.sin(t * 0.8 + i); y = 260 + ((i * 97) % 1200) - 60 * u
        d.circ(x, y, 2 + i % 3, fill=A(col, a * math.sin(u * math.pi)))
def title(d, t, t0, s, y=320, size=110, col=WHITE):
    d.text(540, y, s, size, A(col, ease(pr(t, t0, t0 + 0.2))), k=1)
def hdr(d, t, t0, s, col):
    tag(d, 540, 250, s, col, popk(t, t0), 34, WHITE)

def _cr2(pts, n=6):
    out = []; P_ = [pts[-1]] + pts + [pts[0], pts[1]]
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for j in range(n):
            u = j / n
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * u + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u * u + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u ** 3) for k in range(2)))
    return out
SCAP = _cr2([(-0.50, -0.62), (-0.1, -0.60), (0.18, -0.56), (0.30, -0.68), (0.42, -0.62), (0.53, -0.50), (0.59, -0.38), (0.52, -0.26),
             (0.38, -0.04), (0.22, 0.30), (0.08, 0.62), (0.0, 0.86), (-0.18, 0.52), (-0.40, 0.06), (-0.56, -0.34)])
HOLE = (-0.06, 0.14, 0.075)

def scap(d, cx, cy, s, a=1.0, rot=0.0, hole=1.0, glow_=0.0, col=BONE, holecol=HOLEC, shadow=True):
    if a <= 0.01 or s < 2: return None
    c, sn = math.cos(rot), math.sin(rot)
    def T(u, v): return cx + (u * c - v * sn) * s, cy + (u * sn + v * c) * s
    if shadow: d.ell(cx + 0.04 * s, cy + 0.95 * s, 0.5 * s, 0.07 * s, A((0, 0, 0), 0.25 * a))
    d.poly([T(u + 0.025, v + 0.03) for u, v in SCAP], A(mix(col, (0, 0, 0), 0.22), a))
    d.poly([T(u, v) for u, v in SCAP], A(col, a))
    if glow_ > 0:
        glow(d, *T(-0.08, 0.15), 0.55 * s, (255, 220, 130), 0.9 * glow_)
        d.poly([T(-0.08 + (u + 0.08) * 0.62, 0.15 + (v - 0.15) * 0.62) for u, v in SCAP], A((255, 236, 170), 0.55 * glow_ * a))
        d.poly([T(-0.08 + (u + 0.08) * 0.35, 0.15 + (v - 0.15) * 0.35) for u, v in SCAP], A((255, 250, 220), 0.6 * glow_ * a))
    # spine ridge + acromion
    d.line([T(-0.52, -0.33), T(0.0, -0.44), T(0.40, -0.58), T(0.52, -0.70)], A(mix(col, (0, 0, 0), 0.2), a), 0.075 * s)
    d.line([T(-0.52, -0.36), T(0.0, -0.47), T(0.40, -0.61), T(0.50, -0.72)], A(BONE_L, a), 0.05 * s)
    d.circ(*T(0.53, -0.38), 0.09 * s, fill=A(mix(col, (0, 0, 0), 0.12), a))
    d.ell(*T(-0.22, -0.05), 0.07 * s, 0.16 * s, A(WHITE, 0.25 * a))
    if hole > 0:
        hx, hy = T(HOLE[0], HOLE[1]); r = HOLE[2] * s * hole
        d.circ(hx + r * 0.18, hy + r * 0.18, r * 1.32, fill=A(mix(col, (0, 0, 0), 0.25), a))
        d.circ(hx, hy, r, fill=A(holecol, a))
    return T

def mag(d, x, y, r, a=1.0, ang=0.8, glass=0.3):
    if a <= 0.01: return
    hx, hy = x + math.cos(ang) * r * 1.1, y + math.sin(ang) * r * 1.1
    d.line([(hx, hy), (hx + math.cos(ang) * r * 1.1, hy + math.sin(ang) * r * 1.1)], A(WOOD_D, a), r * 0.3)
    d.circ(x, y, r * 1.14, fill=A(BRASS, a)); d.circ(x, y, r, fill=A((210, 240, 255), glass * a))
    d.arc(x, y, r * 0.78, r * 0.78, 200, 250, A(WHITE, 0.8 * a), r * 0.08)

def lensframe(d, x, y, r, a=1.0, ang=0.8):
    hx, hy = x + math.cos(ang) * r * 1.08, y + math.sin(ang) * r * 1.08
    d.line([(hx, hy), (hx + math.cos(ang) * r * 0.9, hy + math.sin(ang) * r * 0.9)], A(WOOD_D, a), r * 0.24)
    d.circ(x, y, r * 1.1, outline=A(BRASS, a), w=r * 0.12)
    d.arc(x, y, r * 0.82, r * 0.82, 200, 245, A(WHITE, 0.7 * a), r * 0.06)

def nean(d, x, y, s, t, mood="chill", a=1.0, look=0.0, sq=0.0, body=True, wave_=0.0, bowl=0.0):
    if a <= 0.01 or s < 2: return
    sx, sy = s * (1 + sq), s * (1 - sq)
    if body:
        by = y + 1.3 * s
        d.ell(x + 0.05 * s, by + 0.05 * s, 0.85 * s, 0.75 * s, A(FUR_D, a)); d.ell(x, by, 0.8 * s, 0.72 * s, A(FUR, a))
        for k in range(7):
            hx = x - 0.6 * s + k * 0.2 * s; d.poly([(hx - 0.1 * s, by + 0.55 * s), (hx, by + 0.78 * s), (hx + 0.1 * s, by + 0.55 * s)], A(FUR, a))
        d.ell(x - 0.3 * s, by - 0.2 * s, 0.12 * s, 0.2 * s, A(FUR_L, 0.6 * a))
        lx = x - 0.85 * s; ly = by - 0.05 * s
        if wave_ > 0: ly -= 0.7 * s * wave_; lx += 0.1 * s * math.sin(t * 14) * wave_
        d.circ(lx, ly, 0.22 * s, fill=A(SKN, a))
        rx_, ry_ = x + 0.85 * s, by - 0.05 * s - 0.3 * s * bowl
        d.circ(rx_ - 0.4 * s * bowl, ry_, 0.22 * s, fill=A(SKN, a))
    # hair back
    d.ell(x, y - 0.45 * sy, 1.0 * sx, 0.68 * sy, A(HAIR, a))
    d.ell(x + 0.04 * s, y + 0.05 * s, 0.98 * sx, 0.98 * sy, A(SKN_D, a)); d.ell(x, y, 0.95 * sx, 0.95 * sy, A(SKN, a))
    # bangs
    for k in range(7):
        bx = x - 0.75 * sx + k * 0.25 * sx
        d.poly([(bx - 0.2 * sx, y - 0.62 * sy), (bx + 0.05 * sx, y - 0.40 * sy - 0.06 * sy * (k % 2)), (bx + 0.22 * sx, y - 0.66 * sy)], A(HAIR, a))
    d.ell(x, y - 0.75 * sy, 0.8 * sx, 0.22 * sy, A(HAIR, a))
    # beard
    d.ell(x, y + 0.58 * sy, 0.72 * sx, 0.42 * sy, A(BEARD, a))
    d.ell(x - 0.68 * sx, y + 0.2 * sy, 0.16 * sx, 0.32 * sy, A(BEARD, a)); d.ell(x + 0.68 * sx, y + 0.2 * sy, 0.16 * sx, 0.32 * sy, A(BEARD, a))
    # brow ridge
    d.rect(x - 0.66 * sx, y - 0.40 * sy, x + 0.66 * sx, y - 0.2 * sy, fill=A(SKN_B, a), r=0.1 * s)
    er = 0.15 * s; ey = y - 0.05 * sy
    for k in (-1, 1):
        ex = x + k * 0.32 * sx
        if mood in ("happy", "sleep"):
            if mood == "happy": d.arc(ex, ey + er * 0.4, er, er * 0.9, 200, 340, A(INK, a), er * 0.4)
            else: d.arc(ex, ey - er * 0.3, er, er * 0.7, 20, 160, A(INK, a), er * 0.35)
        elif mood == "wink" and k > 0:
            d.arc(ex, ey + er * 0.4, er, er * 0.7, 200, 340, A(INK, a), er * 0.4)
        else:
            big = 1.3 if mood in ("shock", "scared") else 1.0
            d.circ(ex, ey, er * big, fill=A(WHITE, a))
            oy = er * 0.35 if mood == "sad" else 0
            d.circ(ex + look * er * 0.45, ey + oy, er * (0.35 if mood == "shock" else 0.55), fill=A(INK, a))
            d.circ(ex + look * er * 0.45 + er * 0.2, ey + oy - er * 0.2, er * 0.15, fill=A(WHITE, a))
            if mood == "sad": d.line([(ex - er * 1.1, ey - er * 1.25 - k * er * 0.4), (ex + er * 1.1, ey - er * 1.25 + k * er * 0.4)], A(HAIR, a), er * 0.35)
    d.circ(x - 0.55 * sx, y + 0.18 * sy, 0.12 * s, fill=A((255, 140, 140), 0.35 * a)); d.circ(x + 0.55 * sx, y + 0.18 * sy, 0.12 * s, fill=A((255, 140, 140), 0.35 * a))
    d.ell(x, y + 0.14 * sy, 0.21 * sx, 0.16 * sy, A(SKN_D, a)); d.ell(x - 0.06 * s, y + 0.1 * sy, 0.06 * s, 0.04 * s, A(WHITE, 0.4 * a))
    mx, my = x, y + 0.45 * sy
    if mood in ("happy", "chill", "wink", "sleep"):
        d.ell(mx, my - 0.02 * s, 0.24 * s, 0.1 * s, A(SKN, a)); d.arc(mx, my - 0.07 * s, 0.17 * s, 0.11 * s, 20, 160, A(INK, a), 0.045 * s)
    elif mood in ("shock", "scared"):
        d.ell(mx, my + 0.02 * s, 0.12 * s, 0.15 * s, A(INK, a))
    elif mood == "sad":
        d.ell(mx, my, 0.22 * s, 0.09 * s, A(SKN, a)); d.arc(mx, my + 0.06 * s, 0.14 * s, 0.07 * s, 200, 340, A(INK, a), 0.04 * s)
    if mood in ("shock", "scared"): d.ell(x + 0.85 * sx, y - 0.4 * sy + (t * 50) % 30, 0.06 * s, 0.1 * s, A(XRC, a))

def nean_lying(d, x, y, s, t, a=1.0):   # on its back, head to the right (east)
    d.ell(x, y + 0.42 * s, 1.45 * s, 0.16 * s, A((0, 0, 0), 0.25 * a))
    d.ell(x - 0.3 * s, y + 0.08 * s, 0.95 * s, 0.4 * s, A(FUR_D, a)); d.ell(x - 0.32 * s, y, 0.92 * s, 0.37 * s, A(FUR, a))
    d.ell(x - 1.25 * s, y + 0.12 * s, 0.3 * s, 0.16 * s, A(SKN, a))
    hx = x + 0.95 * s
    d.ell(hx + 0.18 * s, y, 0.3 * s, 0.5 * s, A(HAIR, a))
    d.circ(hx, y, 0.45 * s, fill=A(SKN, a))
    d.ell(hx - 0.25 * s, y, 0.2 * s, 0.32 * s, A(BEARD, a))
    d.ell(hx + 0.08 * s, y - 0.28 * s, 0.1 * s, 0.05 * s, A(SKN_D, a))
    for k in (-1, 1): d.arc(hx + 0.12 * s, y + k * 0.17 * s, 0.08 * s, 0.06 * s, 110, 250, A(INK, a), 0.03 * s)

def det(d, x, y, s, t, mood="chill", a=1.0, scratch=0.0, look=0.0, holdmag=True, sq=0.0):
    if a <= 0.01: return
    d.ell(x, y + 1.0 * s, 0.8 * s, 0.12 * s, A((0, 0, 0), 0.25 * a))
    d.ell(x + 0.05 * s, y + 0.05 * s, s * (1 + sq), s * 1.02 * (1 - sq), A(TAN_D, a)); d.ell(x, y, s * 0.97 * (1 + sq), s * (1 - sq), A(TAN, a))
    d.line([(x - 0.3 * s, y + 0.45 * s), (x, y + 0.75 * s), (x + 0.3 * s, y + 0.45 * s)], A(TAN_D, a), 0.06 * s)
    d.ell(x - 0.35 * s, y - 0.4 * s, 0.18 * s, 0.1 * s, A(WHITE, 0.35 * a))
    hy = y - 0.82 * s * (1 - sq)
    d.ell(x, hy + 0.06 * s, 0.86 * s, 0.2 * s, A(mix(CHK, (0, 0, 0), 0.25), a))
    d.d.chord((P(x - 0.62 * s), P(hy - 0.5 * s), P(x + 0.62 * s), P(hy + 0.36 * s)), 180, 360, fill=A(CHK, a))
    for k in range(4): d.line([(x - 0.45 * s + k * 0.3 * s, hy - 0.42 * s), (x - 0.45 * s + k * 0.3 * s, hy - 0.02 * s)], A(mix(CHK, WHITE, 0.25), a), 0.04 * s)
    face(d, x, y + 0.05 * s, s * 0.8, mood, a, look)
    if holdmag: mag(d, x + 1.0 * s, y + 0.1 * s, 0.32 * s, a, 0.9)
    if scratch > 0:
        hx, hy2 = x - 0.42 * s, y - 0.72 * s + 0.025 * s * math.sin(t * 38)
        d.line([(x - 0.8 * s, y + 0.15 * s), (x - 0.95 * s, y - 0.4 * s), (hx, hy2)], A(TAN_D, a * scratch), 0.18 * s)
        d.circ(hx, hy2, 0.13 * s, fill=A(TAN, a * scratch))

def wspear(d, x0, y0, x1, y1, w, a=1.0, col=WOOD, dark=WOOD_D, lt=WOOD_L):
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    tip = 0.16 * L; bx, by = x1 - ux * tip, y1 - uy * tip
    d.line([(x0, y0), (bx, by)], A(dark, a), w); d.line([(x0 + nx * w * 0.15, y0 + ny * w * 0.15), (bx + nx * w * 0.15, by + ny * w * 0.15)], A(col, a), w * 0.65)
    d.poly([(bx + nx * w / 2, by + ny * w / 2), (x1, y1), (bx - nx * w / 2, by - ny * w / 2)], A(lt, a))
    d.poly([(bx + nx * w / 2, by + ny * w / 2), (x1, y1), (bx, by)], A(col, a))
def sspear(d, x0, y0, x1, y1, w, a=1.0):
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    tip = 0.2 * L; bx, by = x1 - ux * tip, y1 - uy * tip
    d.line([(x0, y0), (bx, by)], A(WOOD_D, a), w * 0.8)
    pts = [(bx + nx * w * 1.2, by + ny * w * 1.2), (x1 - ux * tip * 0.45 + nx * w * 0.5, y1 - uy * tip * 0.45 + ny * w * 0.5), (x1, y1),
           (x1 - ux * tip * 0.5 - nx * w * 0.6, y1 - uy * tip * 0.5 - ny * w * 0.6), (bx - nx * w * 1.2, by - ny * w * 1.2)]
    d.poly(pts, A(FLINT, a)); d.poly([pts[0], pts[1], pts[2], (bx, by)], A(FLINT_L, a))
    d.line([(bx - nx * w, by - ny * w), (bx + nx * w, by + ny * w)], A((90, 70, 50), a), w * 0.3)

def heart(d, x, y, s, col, a=1.0):
    d.circ(x - s * 0.5, y - s * 0.2, s * 0.55, fill=A(col, a)); d.circ(x + s * 0.5, y - s * 0.2, s * 0.55, fill=A(col, a))
    d.poly([(x - s * 1.03, y - s * 0.05), (x, y + s * 1.05), (x + s * 1.03, y - s * 0.05), (x, y - s * 0.3)], A(col, a))
    d.ell(x - s * 0.55, y - s * 0.4, s * 0.18, s * 0.12, A(WHITE, 0.5 * a))
def star(d, x, y, r, col, a=1.0, n=9, rot=0):
    pts = []
    for i in range(n * 2):
        ang = rot + i * math.pi / n; rr = r if i % 2 == 0 else r * 0.55
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    d.poly(pts, A(col, a))
def arrow(d, x0, y0, x1, y1, col, a=1.0, w=16):
    L = math.hypot(x1 - x0, y1 - y0) + 1e-6; ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    bx, by = x1 - ux * w * 2.4, y1 - uy * w * 2.4
    d.line([(x0, y0), (bx, by)], A(col, a), w)
    d.poly([(bx + nx * w * 1.6, by + ny * w * 1.6), (x1, y1), (bx - nx * w * 1.6, by - ny * w * 1.6)], A(col, a))
def dashed(d, x0, y0, x1, y1, k, col, a=1.0, w=12, seg=34):
    L = math.hypot(x1 - x0, y1 - y0); n = int(L / seg)
    for i in range(int(n * k)):
        if i % 2: continue
        u0, u1 = i / n, min((i + 1) / n, k)
        d.line([(lerp(x0, x1, u0), lerp(y0, y1, u0)), (lerp(x0, x1, u1), lerp(y0, y1, u1))], A(col, a), w)

# ---------------- scenes ----------------
def s_hook(t, d):
    hit = t >= HOOK_HIT
    if not hit: grad(d, (26, 22, 34), (6, 6, 12))
    else: rays(d, t, (206, 70, 46), (130, 32, 30), n=20, cx=540, cy=860)
    zk = eio(pr(t, ZOOM[0], CAVE)) if hit else 0
    s = 360 * (1 + 4.2 * zk) * (1 + 0.03 * math.exp(-max(0, t - HOOK_HIT) * 6) * math.sin(max(0, t - HOOK_HIT) * 30) if hit else 1)
    hx, hy = HOLE[0], HOLE[1]
    cx = lerp(540, 540 - hx * s, zk); cy = lerp(860, 840 - hy * s, zk)
    sweep = 540 + 260 * math.sin(t * 6) if not hit else 540
    d.poly([(sweep - 70, 0), (sweep + 70, 0), (sweep + 380, 1300), (sweep - 380, 1300)], A((255, 250, 220), 0.1 if not hit else 0.07))
    if not hit:
        scap(d, 540, 860, 360, a=0.5, rot=0.05, col=(120, 110, 100), holecol=(10, 8, 12))
    else:
        if zk < 0.02: d.ell(540, 1210, 340, 50, A((255, 250, 220), 0.18))
        scap(d, cx, cy, s, rot=0.05 * math.sin(t * 2.2) * (1 - zk), shadow=zk < 0.05)
        if zk > 0.45:   # inside the hole: tunnel rings
            k2 = pr(zk, 0.45, 1)
            for j in range(6):
                rr = ((t * 900 + j * 160) % 960) * k2
                d.circ(540, 840, rr, outline=A(BONE_D, 0.35 * k2 * (1 - rr / 960)), w=14)
        sparks(d, 540, 900, t, HOOK_HIT, n=60, spd=1300, col=(255, 236, 190), seed=3)
        rings(d, 520, 900, t, [HOOK_HIT], WHITE, 0.6, 420)
    if t >= LENS_IN:   # magnifier slides in during the stop: nothing goes quiet
        u = ease(pr(t, LENS_IN, LENS_IN + 0.18)); lx = lerp(1300, 560, u) + 3 * math.sin(t * 9); ly = 820 + 3 * math.cos(t * 7)
        d.circ(lx, ly, 250, fill=A((230, 246, 255), 0.25))
        d.ell(lx, ly, 130, 90, A(WHITE, 1)); d.circ(lx - 20 + 25 * math.sin(t * 5), ly + 5, 52, fill=A((80, 120, 60), 1)); d.circ(lx - 20 + 25 * math.sin(t * 5), ly + 5, 28, fill=A(INK, 1))
        d.circ(lx + 2 + 25 * math.sin(t * 5), ly - 14, 10, fill=A(WHITE, 1))
        lensframe(d, lx, ly, 250, 1, 0.8)
    if not hit: d.text(540, 330, "一个洞？", 130, A(WHITE, 1), k=1)
    stamp(d, t, HOOK_HIT, "7.5万年前", 540, 300, 140, YEL)
    stamp(d, t, HOOK_HIT + 0.08, "的命案！", 540, 450, 140, WHITE)

def strata(d, off, t):
    cols = [(196, 146, 92), (168, 116, 72), (210, 168, 112), (140, 96, 60), (182, 136, 90), (124, 84, 54)]
    for i in range(-2, 30):
        y0 = 150 + i * 120 - off
        if y0 > 1920 or y0 < -200: continue
        d.rect(-50, y0, OW + 50, y0 + 121, fill=A(cols[i % 6], 1))
        r2 = random.Random(i)
        for j in range(4):
            rx = r2.uniform(60, 1020); ry = y0 + r2.uniform(25, 95)
            d.ell(rx, ry, r2.uniform(22, 50), r2.uniform(12, 24), A(mix(cols[i % 6], (60, 40, 30), 0.35), 1))

def s_cave(t, d):
    k = eio(pr(t, CAVE, FOUND)); off = 900 * k
    strata(d, off, t)
    vib = 1.2 * math.sin(t * 80) if t < FOUND else 0
    bot = 520 + 600 * k
    d.rect(470, -50, 610, bot, fill=A((40, 26, 20), 0.85))
    if t < FOUND + 0.15:
        d.rect(522 + vib, -50, 558 + vib, bot - 70, fill=A((150, 156, 170), 1))
        d.poly([(490 + vib, bot - 80), (590 + vib, bot - 80), (540 + vib, bot)], A((190, 196, 210), 1))
        for j in range(10):
            ang = (t * 7 + j) % (2 * math.pi); d.circ(540 + math.cos(ang) * 90, bot - 30 + math.sin(ang * 1.7) * 30, 6 + j % 4, fill=A((230, 200, 150), 0.7))
    fk = popk(t, FOUND)
    if fk > 0:
        glow(d, 540, bot - 90, 220, (255, 236, 170), 0.7 * fk)
        scap(d, 540, bot - 100 - 120 * ease(pr(t, FOUND, FOUND + 0.4)), 150 * fk, rot=0.2 * math.sin(t * 3))
        sparks(d, 540, bot - 100, t, FOUND, n=30, spd=600, col=(255, 240, 200), seed=7, life=0.8)
    # depth gauge
    d.line([(255, 330), (255, 1150)], A(WHITE, 0.8), 6)
    depth = 7.5 * k
    gy = lerp(330, 1150, k)
    d.circ(255, gy, 16, fill=A(YEL, 1))
    tag(d, 255, gy - 52, f"{depth:.1f} 米", WHITE, 1, 30)
    if t < FOUND: title(d, t, CAVE, "往下挖", 300, 110)
    stamp(d, t, FOUND, "近 8 米深", 540, 300, 120, YEL)

def s_thin(t, d):
    on = t >= LAMP
    grad(d, (62, 44, 34) if on else (30, 22, 18), (24, 16, 12))
    lx, ly = 300, 470
    if on:
        d.poly([(lx - 30, ly), (lx + 30, ly), (860, 1250), (330, 1250)], A((255, 236, 170), 0.12))
        glow(d, lx, ly, 160, (255, 230, 150), 0.9)
    d.line([(lx, 250), (lx, ly - 40)], A((60, 60, 70), 1), 6)
    d.d.chord((P(lx - 70), P(ly - 60), P(lx + 70), P(ly + 40)), 180, 360, fill=A((70, 74, 90), 1))
    d.circ(lx, ly, 26, fill=A((255, 246, 200) if on else (120, 110, 90), 1))
    gk = ease(pr(t, GLOW - 0.3, GLOW + 0.4))
    cy = 880 + 10 * math.sin(t * 2.5)
    scap(d, 580, cy, 330, rot=-0.08 + 0.04 * math.sin(t * 1.7), glow_=gk, col=BONE if on else mix(BONE, (0, 0, 0), 0.5))
    for sd in (-1, 1):   # gloved hands
        hx = 580 + sd * 250; d.ell(hx, cy + 40, 60, 46, A(WHITE, 1)); d.ell(hx - sd * 40, cy + 10, 26, 18, A((235, 235, 240), 1))
    tag(d, 540, 1180, "肩胛骨 = 背后那块扁扁的骨头", WHITE, popk(t, SCAP_TAG), 32, (110, 70, 40))
    if t < GLOW: title(d, t, THIN, "对着灯看", 300, 110)
    stamp(d, t, GLOW, "薄得透光！", 540, 300, 120, YEL)

def s_profile(t, d):
    grad(d, (252, 196, 84), (232, 138, 50))
    for i in range(-4, 14):
        x0 = i * 140 + (t * 40) % 140; d.poly([(x0, 0), (x0 + 60, 0), (x0 - 600, 1920), (x0 - 660, 1920)], A(WHITE, 0.06))
    d.rect(200, 400, 890, 1230, fill=A((120, 70, 30), 0.25), r=24)
    d.rect(190, 390, 880, 1220, fill=A((246, 226, 180), 1), r=24)
    d.rect(190, 360, 420, 410, fill=A((246, 226, 180), 1), r=16)
    d.text(305, 386, "死者档案", 28, A((140, 90, 40), 1), k=1)
    pk = popk(t, PHOTO)
    if pk > 0:
        px, py = 360, 600
        d.rect(px - 140 * pk, py - 160 * pk, px + 140 * pk, py + 180 * pk, fill=A(WHITE, 1), r=8)
        d.rect(px - 120 * pk, py - 140 * pk, px + 120 * pk, py + 100 * pk, fill=A((90, 150, 200), 1))
        if pk > 0.6:
            blink = (t % 2.6) < 0.1
            nean(d, px, py - 20 + 4 * math.sin(t * 3), 78, t, mood="happy" if blink else ("chill" if t < NEAN_TAG else "happy"), body=False)
        if t < PHOTO + 0.12: d.rect(px - 140, py - 160, px + 140, py + 180, fill=A(WHITE, 1 - pr(t, PHOTO, PHOTO + 0.12)), r=8)
    d.text(690, 520, "Shanidar A", 52, A(NAVYT, popk(t, PHOTO + 0.1)), k=1)
    d.text(690, 590, "沙尼达尔 A 号", 32, A((120, 90, 60), popk(t, PHOTO + 0.15)), k=1)
    tag(d, 690, 680, "已灭绝的古人类", BAD, popk(t, NEAN_TAG), 30, WHITE)
    rows = [("种类", "尼安德特人"), ("年龄", "约 45 岁"), ("地点", "伊拉克 沙尼达尔洞穴"), ("年代", "约 7.5 万年前")]
    for i, (lab, val) in enumerate(rows):
        k = popk(t, FIELDS[i])
        if k <= 0: continue
        yy = 850 + i * 92
        d.line([(230, yy + 36), (840, yy + 36)], A((200, 170, 120), 1), 3)
        d.text(232, yy, lab, 34, A((150, 110, 70), k), anchor="lm", k=1)
        n = int(len(val) * pr(t, FIELDS[i], FIELDS[i] + 0.25) + 0.999)
        d.text(340, yy, val[:n], 40, A(NAVYT, 1), anchor="lm", k=1)
        if i == 1: d.circ(640, yy, 0, fill=None)
    stamp(d, t, PROFILE + 0.05, "死者档案", 540, 270, 110, WHITE)

def s_evid(t, d):
    grad(d, (34, 140, 150), (14, 70, 88))
    for i in range(10): d.line([(180 + i * 80, 380), (180 + i * 80, 1220)], A(WHITE, 0.05), 2)
    for i in range(11): d.line([(180, 380 + i * 84), (900, 380 + i * 84)], A(WHITE, 0.05), 2)
    s = 340; cx, cy = 540, 820 + 6 * math.sin(t * 2)
    T = scap(d, cx, cy, s, rot=0.03 * math.sin(t * 1.5))
    pts = [(0.0, -0.72, "完整"), (0.62, -0.38, "完整"), (0.04, 0.86, "完整")]
    for i, (u, v, lab) in enumerate(pts):
        k = popk(t, CHECKS[i])
        if k <= 0: continue
        x, y = T(u, v); x = cl(x, 230, 850)
        d.circ(x, y, 34 * k, fill=A(GOOD, 1)); check(d, x, y + 3, 17, ease(pr(t, CHECKS[i], CHECKS[i] + 0.2)), WHITE)
        rings(d, x, y, t, [CHECKS[i]], WHITE, 0.6, 140)
    hx, hy = T(HOLE[0], HOLE[1])
    lk = ease(pr(t, LENS - 0.3, LENS + 0.1))
    if lk > 0:
        lx, ly = lerp(1150, hx + 60, lk), lerp(1250, hy - 40, lk)
        R = 170
        d.circ(lx, ly, R, fill=A(BONE, 1)); d.circ(lx + 14, ly + 14, 88, fill=A(BONE_D, 1)); d.circ(lx, ly, 76, fill=A(HOLEC, 1))
        d.arc(lx, ly, 90, 90, 200, 330, A(BONE_L, 1), 8)
        lensframe(d, lx, ly, R, 1, 0.75)
        rk = ease(pr(t, RULER - 0.2, RULER + 0.15))
        if rk > 0:
            ry = ly + 108
            d.rect(lx - 160, ry - 4, lx - 160 + 320 * rk, ry + 40, fill=A(YEL, 1), r=6)
            for j in range(17):
                xx = lx - 152 + j * 19
                if xx < lx - 160 + 320 * rk: d.line([(xx, ry), (xx, ry + (22 if j % 5 == 0 else 12))], A(NAVYT, 1), 3)
            nt = sum(1 for h in TICKS if t >= h)
            for j in range(nt):
                xx = lerp(lx - 76, lx + 76, j / 3); d.line([(xx, ly - 100), (xx, ry)], A(BAD, 0.7), 4)
            if t >= MM15:
                d.line([(lx - 76, ly), (lx + 76, ly)], A(BAD, 1), 6)
                for sd in (-1, 1): d.poly([(lx + sd * 76, ly), (lx + sd * 56, ly - 12), (lx + sd * 56, ly + 12)], A(BAD, 1))
                tag(d, lx, ly - 30, "15 mm", WHITE, popk(t, MM15), 34, BAD)
    if t >= STOP1[0]:
        tag(d, 540, 1190, "唯一的破损", BAD, popk(t, STOP1[0]), 38, WHITE)
        rings(d, hx, hy, t, [STOP1[0]], BAD, 0.7, 260)
    if t < MM15: title(d, t, EVID, "只有一个洞", 300, 110)
    stamp(d, t, MM15, "15 毫米", 540, 300, 130, YEL)

def suspect(d, i, x, y, lit, t, a=1.0, fall=0.0):
    col = mix((30, 20, 50), (250, 240, 220), lit)
    dx = fall * (-1 if x < 540 else 1) * 300; dy = fall * fall * 600
    x += dx; y += dy
    if i == 0: sspear(d, x - 20, y + 240, x + 20, y - 230, 22, a)
    elif i == 1: wspear(d, x - 20, y + 240, x + 20, y - 230, 22, a)
    elif i == 2:
        for k in range(3):
            bx = x - 50 + k * 50
            d.poly([(bx - 22, y + 120), (bx + 22, y + 120), (bx + 30 + 20 * math.sin(t * 3 + k) * 0, y - 60), (bx - 4, y - 140 + k * 10)], A(mix((90, 80, 70), (240, 236, 220), lit), a))
        d.ell(x, y + 160, 110, 70, A(mix((60, 40, 30), (150, 100, 60), lit), a))
    else:
        d.ell(x, y + 210, 90, 40, A(mix((60, 50, 60), (150, 150, 160), lit), a))
        arrow(d, x, y - 200, x, y + 120, mix((80, 80, 110), WHITE, lit), a, 18)
        d.text(x, y - 40, "摔", 70, A(mix((60, 60, 90), YEL, lit), a), k=1)

def s_susp(t, d):
    grad(d, (46, 30, 84), (16, 10, 32))
    for i in range(8):
        yy = 440 + i * 80; d.line([(180, yy), (900, yy)], A(WHITE, 0.12), 3)
    xs = [270, 450, 630, 810]; labs = ["石矛", "木矛", "猛兽爪", "意外跌落"]
    for i, x in enumerate(xs):
        lit = ease(pr(t, SPOTS[i], SPOTS[i] + 0.12)) * (1 - 0.55 * pr(t, SPOTS[i] + BEAT, SPOTS[i] + BEAT * 1.5))
        if lit > 0: d.poly([(x - 30, 330), (x + 30, 330), (x + 100, 1000), (x - 100, 1000)], A((255, 250, 220), 0.18 * lit))
        suspect(d, i, x, 720, max(0.25 * pr(t, SPOTS[i], SPOTS[i] + 0.1), lit), t)
        tag(d, x, 1030, labs[i], WHITE if t >= SPOTS[i] else (90, 80, 120), popk(t, SUSP + 0.1 * i), 30, NAVYT)
        d.text(x, 1080, f"{i + 1} 号", 24, A(WHITE, 0.6), k=1)
    sc = 1.0 if t >= SCRATCH else 0.0
    det(d, 540, 1160, 70, t, mood="sus" if t < SCRATCH else "scared", scratch=sc, look=math.sin(t * 2), holdmag=t < SCRATCH)
    if t >= SCRATCH:
        for k, (qx, qy) in enumerate([(430, 1080), (650, 1060), (560, 1000)]):
            ka = popk(t, SCRATCH + k * 0.15)
            if ka > 0: d.text(qx, qy - 8 * math.sin(t * 6 + k), "?", int(64 * ka), A(YEL, ka), k=1)
    title(d, t, SUSP, "凶器是什么？", 300, 110)

def s_reveal(t, d):
    rays(d, t, (255, 206, 70), (236, 126, 36), n=18, cx=560, cy=820)
    for i, x in enumerate([270, 450, 630, 810]):
        if i != 1: suspect(d, i, x, 760, 0.0, t, a=1 - pr(t, BIG2, BIG2 + 0.6), fall=ease(pr(t, BIG2, BIG2 + 0.7)))
    k = popk(t, BIG2)
    d.circ(700, 560, 230 * k, fill=A((255, 252, 230), 0.35))
    glow(d, 700, 560, 260, WHITE, 0.6 * k)
    sh = 2 * math.sin(t * 50) * pulse(t, [BIG2], 4)
    wspear(d, 300 + sh, 1180, lerp(540, 790, k) + sh, lerp(940, 470, k), 46)
    sparks(d, 700, 560, t, BIG2, n=70, spd=1300, col=(255, 250, 220), seed=5)
    det(d, 330, 1090, 70, t, mood="happy" if t > BIG2 + 0.2 else "scared", holdmag=True)
    stamp(d, t, BIG2, "木矛！", 540, 310, 180, WHITE)

def s_clue1(t, d):
    grad(d, (96, 176, 236), (40, 100, 184))
    hdr(d, t, CLUE1, "线索 1", (30, 70, 150))
    for side, (x, t0, kind) in enumerate([(360, STONE, "s"), (720, WOODH, "w")]):
        py = 820
        d.rect(x - 140, py - 150, x + 140, py + 150, fill=A(BONE_D, 1), r=40); d.rect(x - 132, py - 146, x + 128, py + 140, fill=A(BONE, 1), r=36)
        u = pr(t, t0 - 0.35, t0); back_ = pr(t, t0 + 0.05, t0 + 0.35)
        tip_y = lerp(380, py, ease(u)) - 260 * ease(back_)
        if kind == "s": sspear(d, x, tip_y - 330, x, tip_y, 26, 1 - back_ * 0.4)
        else: wspear(d, x, tip_y - 330, x, tip_y, 26, 1 - back_ * 0.4)
        if t >= t0:
            hk = popk(t, t0)
            if kind == "s":
                pts = [(x, py - 62), (x + 30, py - 20), (x + 64, py - 6), (x + 22, py + 28), (x + 8, py + 66), (x - 26, py + 30), (x - 62, py + 8), (x - 30, py - 26)]
                d.poly([(x + (px - x) * hk, py + (pp - py) * hk) for px, pp in pts], A(HOLEC, 1))
            else:
                d.circ(x + 8, py + 8, 66 * hk, fill=A(BONE_D, 1)); d.circ(x, py, 56 * hk, fill=A(HOLEC, 1))
            sparks(d, x, py, t, t0, n=24, spd=500, col=BONE_L, seed=11 + side, life=0.6)
            tag(d, x, py + 205, "有棱角" if kind == "s" else "圆的", WHITE, hk, 34, NAVYT)
        d.text(x, 470, "石尖" if kind == "s" else "木尖", 40, A(WHITE, 1), k=1) if t < t0 - 0.35 else None
    mk = ease(pr(t, MATCH - 0.3, MATCH))
    if mk > 0:
        ex, ey = lerp(540, 720, mk), lerp(1300, 820, mk)
        d.circ(ex, ey, 70, outline=A(YEL, 0.95), w=10)
        if mk < 1: tag(d, ex, ey + 100, "证物的洞", YEL, 1, 30)
    km = ease(pr(t, MATCH, MATCH + 0.2))
    check(d, 720, 640, 40, km, GOOD); cross(d, 360, 640, 40, km, BAD)
    if km > 0: rings(d, 720, 820, t, [MATCH], GOOD, 0.8, 260)
    tag(d, 540, 1180, "复原木矛实测：洞形吻合", GOOD, popk(t, TEST_TAG), 32, WHITE)
    if t < MATCH: title(d, t, CLUE1, "看形状", 370, 100)
    stamp(d, t, MATCH, "圆洞 = 木矛", 540, 370, 100, WHITE)

def s_clue2(t, d):
    grad(d, (70, 180, 120), (24, 100, 70))
    hdr(d, t, CLUE2, "线索 2", (20, 90, 60))
    z = 1 + 0.25 * ease(pr(t, ZOOMB - 0.2, ZOOMB + 0.2))
    cx, cy = 540, 820
    def Z(x, y): return cx + (x - cx) * z, cy + (y - cy) * z
    # bone slab in cross-section (left = front/chest side, right = back side)
    x0, x1 = 470, 610
    d.poly([Z(x0, 560), Z(x1, 560), Z(x1, 1060), Z(x0, 1060)], A(BONE_D, 1))
    d.poly([Z(x0 + 8, 560), Z(x1 - 8, 560), Z(x1 - 8, 1060), Z(x0 + 8, 1060)], A(BONE, 1))
    r2 = random.Random(5)
    for i in range(40):
        px, py = r2.uniform(x0 + 20, x1 - 20), r2.uniform(580, 1040)
        if abs(py - 820) < 120: continue
        d.circ(*Z(px, py), 6 * z, fill=A(BONE_D, 0.6))
    # funnel hole: narrow at entry, wide bevel at exit
    bev = [Z(x0 - 2, 790), Z(x0 - 2, 850), Z(x1 + 2, 910), Z(x1 + 2, 730)]
    d.poly(bev, A((50, 120, 84), 1))
    bk = pulse(t, [ZOOMB, EXIT_TAG], 3) + 0.4 * (t > ZOOMB)
    if t > ZOOMB:
        d.line([Z(x0 + 30, 790), Z(x1 + 2, 730)], A(YEL, min(1, bk)), 10 * z); d.line([Z(x0 + 30, 850), Z(x1 + 2, 910)], A(YEL, min(1, bk)), 10 * z)
    d.text(300, 640, "前面", 40, A(WHITE, 1), k=1); d.text(300, 690, "（胸口这侧）", 28, A(WHITE, 0.85), k=1)
    d.text(790, 640, "背面", 40, A(WHITE, 1), k=1)
    tag(d, 790, 1000, "出口", YEL, popk(t, EXIT_TAG), 40, NAVYT)
    d.text(540, 1170, "穿出去那面，洞边会崩成斜坡", 32, A(WHITE, popk(t, EXIT_TAG)), k=1)
    u = ease(pr(t, PATH2, ARROW2))
    if u > 0:
        tipx = lerp(220, 900, u)
        wspear(d, tipx - 330, 820, tipx, 820, 30, 1)
        if t > ARROW2: arrow(d, 330, 470, 750, 470, WHITE, popk(t, ARROW2), 14)
    if t < EXIT_TAG: title(d, t, CLUE2, "看洞边", 370, 100)
    if t < PATH2: stamp(d, t, EXIT_TAG, "边是斜的", 540, 370, 100, WHITE)
    else: stamp(d, t, PATH2 + 0.1, "从前往后", 540, 370, 100, YEL)

def s_clue3(t, d):
    grad(d, (160, 100, 210), (80, 40, 130))
    hdr(d, t, CLUE3, "线索 3", (70, 30, 120))
    s = 520; cx, cy = 571, 827
    T = scap(d, cx, cy, s, rot=0.02 * math.sin(t * 2))
    hx, hy = T(HOLE[0], HOLE[1]); hr = HOLE[2] * s
    # ridges (muscle marks) across the bone
    for j in range(3):
        d.line([(hx - 260, hy - 150 + j * 150), (hx - hr - 80, hy - 130 + j * 150)], A(BONE_D, 0.9), 7)
        d.line([(hx + hr + 80, hy - 120 + j * 150), (hx + 250, hy - 100 + j * 150)], A(BONE_D, 0.9), 7)
    angs = [-2.3, -0.7, 0.8, 2.4]
    for i, h in enumerate(PIECES):
        a0 = angs[i]; u = ease(pr(t, h - 0.3, h))
        fx_, fy_ = hx + math.cos(a0) * hr * 2.3, hy + math.sin(a0) * hr * 2.3
        sx_, sy_ = hx + math.cos(a0) * 700, hy + math.sin(a0) * 700
        x, y = lerp(sx_, fx_, u), lerp(sy_, fy_, u); rot = (1 - u) * 3
        pts = [(math.cos(rot + q * 1.6) * (58 if q % 2 else 44), math.sin(rot + q * 1.6) * (44 if q % 2 else 36)) for q in range(4)]
        d.poly([(x + px + 4, y + py + 4) for px, py in pts], A(BONE_D, 1)); d.poly([(x + px, y + py) for px, py in pts], A(BONE_L, 1))
        if u >= 1:
            d.line([(x - 40, y), (x + 40, y)], A(BONE_D, 1), 6)
            rings(d, x, y, t, [h], WHITE, 0.7, 120)
    dk = ease(pr(t, DOWN, DOWN + 0.35))
    if dk > 0:
        arrow(d, hx, 470, hx, lerp(470, 1150, dk), YEL, 1, 22)
        glow(d, hx, hy, 120, YEL, 0.5 * dk)
    tag(d, 560, 1205, "靠肌肉留下的细棱对上", WHITE, popk(t, RIDGE_TAG), 30, (80, 40, 130))
    if t < DOWN: title(d, t, CLUE3, "拼碎片", 370, 100)
    stamp(d, t, DOWN, "从上往下", 540, 370, 100, YEL)

def s_recon(t, d):
    grad(d, (20, 44, 88), (8, 14, 36))
    for i in range(12): d.line([(0, 300 + i * 100), (1080, 300 + i * 100)], A(XRC, 0.06), 2)
    for i in range(9): d.line([(180 + i * 90, 0), (180 + i * 90, 1920)], A(XRC, 0.06), 2)
    # ghost body, side view facing right
    d.ell(540, 900, 230, 300, A(XRC, 0.16)); d.ell(540, 900, 210, 282, A(XRC, 0.12))
    d.circ(580, 500, 130, fill=A(XRC, 0.18)); d.ell(712, 520, 26, 34, A(XRC, 0.18))
    d.circ(640, 470, 14, fill=A(WHITE, 0.8)); d.circ(644, 470, 7, fill=A(INK, 1))
    for j in range(6): d.arc(560, 720 + j * 52, 190, 40, 180, 360, A(XRC, 0.35), 5)
    d.rect(330, 640, 360, 1150, fill=A(XRC, 0.3), r=12)
    scap(d, 400, 900, 170, rot=0.1, shadow=False)
    hb = 1 + 0.15 * pulse(t, [HEART, HEART + 0.18, AIM + BEAT, AIM + BEAT + 0.18], 6)
    hx, hy = 620, 800
    glow(d, hx, hy, 120, HEARTC, 0.4 + 0.5 * pulse(t, [HEART, AIM], 2))
    heart(d, hx, hy, 46 * hb, HEARTC)
    k = ease(pr(t, *DASH))
    sx_, sy_, ex_, ey_ = 790, 640, 392, 914
    dashed(d, sx_, sy_, ex_, ey_, k, YEL, 1, 12)
    if k >= 1: arrow(d, lerp(sx_, ex_, 0.85), lerp(sy_, ey_, 0.85), ex_ - 20, ey_ + 14, YEL, 1, 12)
    tag(d, 740, 585, "入口：左胸前方", WHITE, popk(t, DASH[0]), 30, NAVYT)
    tag(d, 360, 1010, "出口：肩胛骨", WHITE, popk(t, DASH[1]), 30, NAVYT)
    ak = popk(t, AIM)
    if ak > 0:
        d.circ(hx, hy, 90 * (2 - ak), outline=A(BAD, ak), w=6); d.circ(hx, hy, 50 * (2 - ak), outline=A(BAD, ak), w=4)
        for sd in ((1, 0), (-1, 0), (0, 1), (0, -1)): d.line([(hx + sd[0] * 60, hy + sd[1] * 60), (hx + sd[0] * 120, hy + sd[1] * 120)], A(BAD, ak), 5)
    mk = popk(t, MAYBE)
    if mk > 0:
        d.rect(250, 1160, 830, 1220, fill=A((0, 0, 0), 0.4 * mk), r=20)
        d.text(540, 1190, "也可能是猎猛犸时的意外", 30, A((200, 220, 240), mk), k=1)
    if t < AIM: title(d, t, RECON, "还原路线", 300, 110)
    stamp(d, t, AIM, "瞄准心脏？", 540, 300, 110, WHITE)

def tooth(d, x, y, w, h, col=(250, 248, 240), a=1.0, rot=0.0, half=0, gap=0.0):
    c, sn = math.cos(rot), math.sin(rot)
    def T(u, v): return x + u * c - v * sn, y + u * sn + v * c   # (x,y) = root base centre, crown up
    sides = [(-1, 0), (0, 1)] if half == 0 else ([(-1, 0)] if half < 0 else [(0, 1)])
    for lo, hi in sides:
        off = (lo + hi) / 2 * gap
        poly = [T(lerp(-w * 0.5, w * 0.5, (lo + 1) / 2) * 0.7 + off, 0), T(lerp(-w * 0.5, w * 0.5, (hi + 1) / 2) * 0.7 + off, 0),
                T(lerp(-w * 0.5, w * 0.5, (hi + 1) / 2) + off, -h), T(lerp(-w * 0.5, w * 0.5, (lo + 1) / 2) + off, -h)]
        d.poly(poly, A(col, a))
        d.poly([poly[1], poly[2], T(lerp(-w * 0.5, w * 0.5, (hi + 1) / 2) - w * 0.16 + off, -h), T(lerp(-w * 0.5, w * 0.5, (hi + 1) / 2) * 0.7 - w * 0.12 + off, 0)], A(mix(col, (190, 170, 150), 0.6), a))
        d.poly([T(lerp(-w * 0.5, w * 0.5, (lo + 1) / 2) + off, -h), T(lerp(-w * 0.5, w * 0.5, (hi + 1) / 2) + off, -h), T(lerp(-w * 0.5, w * 0.5, (hi + 1) / 2) + off, -h + 26), T(lerp(-w * 0.5, w * 0.5, (lo + 1) / 2) + off, -h + 26)], A((255, 255, 255), 0.9 * a))
    d.ell(*T(-w * 0.2, -h * 0.7), w * 0.07, h * 0.14, A(WHITE, 0.7 * a))

def s_twist(t, d):
    grad(d, (236, 166, 196), (168, 98, 150))
    for i in range(7): d.circ(540, 800, 200 + i * 150, outline=A(WHITE, 0.07), w=26)
    gy = 1000
    tilt = -0.28 * ease(pr(t, TILT, TILT + 0.25))
    split = ease(pr(t, CRACK, CRACK + 0.3))
    # roots behind translucent gum
    for x in (360, 540, 720): d.rect(x - 34, gy - 20, x + 34, gy + 140, fill=A((246, 240, 226), 0.9), r=30)
    tooth(d, 360, gy, 150, 360, rot=0)
    if split <= 0: tooth(d, 540, gy, 150, 360)
    else:
        tooth(d, 540, gy, 150, 360, half=-1, gap=0)
        fall = pr(t, CRACK + 0.3, CRACK + 1.0)
        tooth(d, 540 + 30 * split + 200 * fall, gy + 900 * fall * fall, 150, 360, half=1, rot=0.15 * split + 1.2 * fall, a=1 - fall)
        zz = [(540, gy - 360 + j * 45) for j in range(9)]
        d.line([(x + (8 if j % 2 else -8), y) for j, (x, y) in enumerate(zz)], A((200, 190, 180), 1 - fall), 5)
    tooth(d, 720, gy, 150, 360, rot=tilt)
    d.rect(200, gy - 10, 880, gy + 180, fill=A((236, 120, 140), 0.75), r=60)
    d.rect(200, gy - 10, 880, gy + 20, fill=A((250, 160, 176), 0.9), r=20)
    # tartar builds up on the remaining half
    ck = ease(pr(t, CALC, CALC + 1.6))
    if ck > 0:
        for j in range(9):
            q = j / 8
            if q > ck: break
            d.circ(536 + 8 * math.sin(j * 2.1), gy - 30 - j * 32, 16 + 6 * (j % 3), fill=A(CALCC, 1))
        tag(d, 680, 1235 - 70, "牙结石 = 变硬的牙垢", WHITE, popk(t, CALC + 0.2), 30, (150, 60, 100))
    if t < CRACK + 0.4 and t >= TWIST:
        sk = popk(t, TWIST + 0.08) * (1 - pr(t, CRACK + 0.2, CRACK + 0.4))
        star(d, 560, 560, 120 * sk, YEL, 1, 10, t * 2); d.text(560, 560, "砰！", int(60 * sk) + 2, A(BAD, sk), k=1)
    # calendar
    if t >= CALC:
        cx, cy = 300, 1150; ck2 = popk(t, CALC)
        d.rect(cx - 80 * ck2, cy - 80 * ck2, cx + 80 * ck2, cy + 80 * ck2, fill=A(WHITE, 1), r=14)
        d.rect(cx - 80 * ck2, cy - 80 * ck2, cx + 80 * ck2, cy - 40 * ck2, fill=A(BAD, 1), r=14)
        n = sum(1 for h in FLIPS if t >= h)
        lab = "1 年+" if t >= YEAR else f"{min(12, n * 12 // 8 + (1 if n else 0))} 月"
        d.text(cx, cy + 20, lab, int(44 * ck2) + 2, A(NAVYT, 1), k=1)
        for h in FLIPS:
            u = pr(t, h, h + 0.2)
            if 0 < u < 1: d.poly([(cx - 80, cy - 40), (cx + 80, cy - 40), (cx + 80, cy - 40 + 120 * (1 - u)), (cx - 80, cy - 40 + 120 * (1 - u))], A((240, 240, 240), 1 - u))
    if t < CRACK: title(d, t, TWIST, "等一下……", 300, 110)
    elif t < CALC: stamp(d, t, CRACK, "门牙裂成两半", 540, 300, 100, WHITE)
    elif t < YEAR: title(d, t, CALC, "牙结石越积越厚", 300, 90)
    else: stamp(d, t, YEAR, "又活了 1 年+", 540, 300, 104, YEL)

def fire(d, x, y, t, s=1.0):
    glow(d, x, y - 40 * s, 260 * s, (255, 170, 60), 0.6)
    for j in range(3): d.line([(x - 80 * s + j * 60 * s, y + 20 * s), (x - 20 * s + j * 40 * s, y - 10 * s)], A(WOOD_D, 1), 18 * s)
    for k, (c, r) in enumerate([((255, 120, 40), 1.0), ((255, 190, 60), 0.7), ((255, 240, 160), 0.4)]):
        fl = 1 + 0.12 * math.sin(t * 17 + k)
        d.poly([(x - 60 * s * r, y), (x - 20 * s * r, y - 90 * s * r * fl), (x, y - 150 * s * r * fl), (x + 25 * s * r, y - 80 * s * r * fl), (x + 60 * s * r, y)], A(c, 1))

def s_care(t, d):
    grad(d, (120, 66, 42), (48, 24, 18))
    d.ell(540, 300, 700, 260, A((40, 20, 14), 0.6))
    embers(d, t, (255, 190, 90), 0.6, 18)
    fire(d, 540, 1080, t, 0.8)
    hk = ease(pr(t, HAND - 0.3, HAND + 0.2))
    happy = t >= HAND + 0.2
    nean(d, 330, 780 + 6 * math.sin(t * 2), 110, t, mood="happy" if happy else "sad", look=0.6, sq=0.05 * pulse(t, [HAND, HEARTS], 7))
    nean(d, 760, 780 + 6 * math.sin(t * 2 + 1), 110, t, mood="happy", look=-0.6, bowl=hk)
    # bowl with soaked plants travelling to the injured one
    bx, by = lerp(820, 470, hk), lerp(1000, 940, hk)
    bk = popk(t, BOWL)
    if bk > 0:
        d.d.chord((P(bx - 70 * bk), P(by - 50 * bk), P(bx + 70 * bk), P(by + 50 * bk)), 0, 180, fill=A(WOOD, 1))
        d.ell(bx, by, 70 * bk, 14 * bk, A((120, 170, 200), 1))
        for j in range(4): d.line([(bx - 40 + j * 26, by - 4), (bx - 30 + j * 26, by - 40 - 10 * math.sin(t * 3 + j))], A(LEAF, 1), 8)
        for j in range(3):
            u = (t * 0.7 + j / 3) % 1; d.circ(bx - 20 + j * 20 + 10 * math.sin(t * 3 + j), by - 60 - u * 140, 10 + 8 * u, fill=A(WHITE, 0.3 * (1 - u)))
    if t >= HEARTS:
        for j in range(5):
            u = ((t - HEARTS) * 0.6 + j * 0.2) % 1; hx = 330 + 60 * math.sin(j * 2 + t * 2) + (j - 2) * 50
            heart(d, hx, 600 - u * 300, 22 + 6 * (j % 2), HEARTC, math.sin(u * math.pi))
    tag(d, 540, 1190, "洞里有把植物泡软再煮的证据", WHITE, popk(t, SOFT_TAG), 28, (120, 60, 30))
    if t < HEARTS: title(d, t, CARE, "谁在照顾它？", 300, 104)
    stamp(d, t, HEARTS, "被照顾着", 540, 300, 120, YEL)

def s_card(t, d):
    grad(d, (255, 214, 90), (240, 150, 50))
    for i in range(10): d.circ(540, 520, 160 + i * 140, outline=A(WHITE, 0.08), w=26)
    scap(d, 540, 540, 200, rot=0.05 * math.sin(t * 2))
    lx = 540 - 12 + 70 * math.sin(t * 2.4); ly = 568 + 30 * math.cos(t * 2.4)
    mag(d, lx, ly, 62, 1, 0.8, 0.25)
    k = popk(t, CARD)
    if k <= 0: return
    al = min(1, k * 1.5); cy = 960 + 40 * (1 - k); w = 680 * (0.7 + 0.3 * k)
    d.rect(540 - w / 2, cy - 190, 540 + w / 2, cy + 200, fill=A(WHITE, 0.97 * al), r=34)
    d.rect(540 - w / 2, cy - 190, 540 - w / 2 + 16, cy + 200, fill=A(GOLD, al), r=8)
    tag(d, 540, cy - 190, "一句话学会", GOLD, al, 34)
    d.text(540, cy - 90, "形状 · 边缘 · 碎片", int(62 * k), A((150, 60, 30), al), k=1)
    d.text(540, cy - 10, "= 法医看凶器的三条线索", int(40 * k), A(NAVYT, al), k=1)
    chips = [("圆洞=木矛", (60, 130, 220)), ("斜边=出口", (40, 150, 100)), ("碎片=方向", (130, 70, 190))]
    for i, (s, col) in enumerate(chips):
        ck = popk(t, CHIPS[i])
        if ck > 0: tag(d, 540 + (i - 1) * 215, cy + 110, s, col, ck, 30, WHITE)

def s_end(t, d):
    grad(d, (34, 66, 88), (10, 20, 34))
    dust(d, t, 0.5, 40, (200, 230, 255))
    d.ell(540, 1110, 520, 110, A((60, 50, 44), 1)); d.rect(-50, 1110, OW + 50, 1960, fill=A((60, 50, 44), 1))
    glow(d, 640, 1000, 360, (190, 230, 255), 0.35)
    # burial behind the tall stone, head to the east (right)
    nean_lying(d, 650, 1030, 120, t)
    sk = ease(pr(t, OUTRO, STONE_UP + 0.3))
    d.poly([(250, 1120), (280, lerp(1120, 600, sk)), (390, lerp(1120, 560, sk)), (450, lerp(1120, 640, sk)), (460, 1120)], A((120, 120, 132), 1))
    d.poly([(280, lerp(1120, 600, sk)), (330, lerp(1120, 580, sk)), (340, 1120), (290, 1120)], A((150, 150, 164), 1))
    arrow(d, 760, 880, 880, 880, (190, 230, 255), popk(t, STONE_UP), 10)
    d.text(820, 835, "东", 34, A((190, 230, 255), popk(t, STONE_UP)), k=1)
    bubble(d, 880, 560, "凶手是谁？没人知道", 1, WHITE, NAVYT, popk(t, BUB), 40)
    stamp(d, t, STONE_UP, "被照顾，也被杀害", 540, 330, 84, WHITE)
    d.text(540, 1150, "Pomeroy et al., Sci. Rep. (2026)", 26, A(WHITE, 0.9))
    d.text(540, 1186, "DOI 10.1038/s41598-026-69193-z", 26, A(WHITE, 0.9))
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

def subs(t, d):
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            if t >= SIL0 and t < BIG2: return
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70
            w = max(d.tlen(x, 52, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 44, 540 + w / 2, y0 + (n - 1) * 70 + 44, fill=A((15, 12, 26), 0.82 * al), r=22)
            for i, x in enumerate(ls): d.text(540, y0 + i * 70, x, 52, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇新发现"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)

SECS = [(-1, CAVE, s_hook), (CAVE, THIN, s_cave), (THIN, PROFILE, s_thin), (PROFILE, EVID, s_profile), (EVID, SUSP, s_evid), (SUSP, BIG2, s_susp),
        (BIG2, CLUE1, s_reveal), (CLUE1, CLUE2, s_clue1), (CLUE2, CLUE3, s_clue2), (CLUE3, RECON, s_clue3), (RECON, TWIST, s_recon),
        (TWIST, CARE, s_twist), (CARE, CARD, s_care), (CARD, OUTRO, s_card), (OUTRO, 99, s_end)]
def cam(t):
    z = 1.0 + 0.015 * pulse(t, HITS, 7) + 0.04 * pulse(t, [HOOK_HIT, BIG2], 3)
    for a, b in RISERS:
        if a <= t < b: z += 0.12 * eio(pr(t, a, b))
    if HOOK_STOP <= t < CAVE: z += 0.06 * pr(t, HOOK_STOP, CAVE)     # keep pushing through the stop
    if CAVE <= t < FOUND: z += 0.05 * (1 - pr(t, CAVE, FOUND))
    amp = 8 * pulse(t, [HOOK_HIT, BIG2], 5) + 1.5 * pulse(t, HITS, 8)
    sx, sy = shake(t, amp, 40)
    return z, 540 + sx, 900 + sy
def frame(t):
    img = Image.new("RGB", (W, H), (30, 20, 50)); d = D(img)
    if SIL0 + 0.06 <= t < BIG2:
        img = Image.new("RGB", (W, H), (0, 0, 0)); d = D(img)
        d.text(540, 900, "……", 80, A(WHITE, 0.5), k=1)
    else:
        for a, b, sf in SECS:
            if a <= t < b: sf(t, d); break
        z, cx, cy = cam(t)
        cw, ch = W / z, H / z
        x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
        img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
        for c in CUTS:
            if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - (t - c) / 0.1)))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"/tmp/ne_test_{float(ts):05.2f}.png")
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
