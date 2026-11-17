import sys, subprocess
from fx import *
from cues import *

SKIN = (255, 192, 150); SKIN_D = (226, 150, 112)
BODY = (40, 40, 52); BODY_HI = (92, 96, 120); BODY_UV = (30, 16, 52); BODY_UV_HI = (120, 80, 200)
SPOT = (255, 200, 40); SPOT_D = (226, 160, 20)
NEON = (120, 255, 130); NEON_C = (70, 240, 255); UVC = (170, 90, 255); UV_D = (60, 20, 120)
NAVYT = (24, 20, 40); GOLD = (255, 200, 60); FOXC = (240, 120, 50); FOX_L = (255, 236, 214)

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
def arrow(d, x0, y0, x1, y1, col, a=1.0, w=22):
    if a <= 0.01: return
    L = math.hypot(x1 - x0, y1 - y0) or 1; ux, uy = (x1 - x0) / L, (y1 - y0) / L; hx, hy = x1 - ux * w * 2.2, y1 - uy * w * 2.2
    d.line([(x0, y0), (hx, hy)], A(col, a), w)
    d.poly([(x1, y1), (hx - uy * w * 1.6, hy + ux * w * 1.6), (hx + uy * w * 1.6, hy - ux * w * 1.6)], A(col, a))
def stamp2(d, t, t0, lines, y, size, col, gap=None):
    gap = gap or size * 1.15
    for i, s in enumerate(lines): stamp(d, t, t0 + i * 0.08, s, 540, y + i * gap, size, col)

# ---------------- the fire salamander ----------------
# spots: (u along body 0 = tail tip .. 1 = neck, v = -1 top .. +1 belly, size, kind) kind 0 back, 1 side, 2 belly
SPOTS = [(0.10, -0.2, 0.05, 0), (0.2, -0.45, 0.07, 0), (0.31, -0.3, 0.08, 0), (0.42, -0.55, 0.1, 0), (0.55, -0.6, 0.11, 0),
         (0.66, -0.55, 0.12, 0), (0.78, -0.62, 0.11, 0), (0.88, -0.55, 0.1, 0),
         (0.26, 0.25, 0.06, 1), (0.48, 0.15, 0.08, 1), (0.6, 0.2, 0.09, 1), (0.72, 0.1, 0.08, 1), (0.84, 0.18, 0.08, 1),
         (0.58, 0.72, 0.13, 2), (0.68, 0.78, 0.13, 2), (0.78, 0.74, 0.13, 2), (0.88, 0.7, 0.11, 2), (0.36, 0.6, 0.07, 2)]
def _r(u):
    if u < 0.55: return 0.035 + 0.215 * (u / 0.55) ** 0.8
    if u < 0.92: return 0.25 + 0.03 * math.sin((u - 0.55) / 0.37 * math.pi)
    return 0.25
def sal(d, x, y, s, t, mood="chill", uv=0.0, glowk=1.0, walk=0.0, curl=0.0, wig=0.0, look=0.0, dr=1, wink=0.0, a=1.0, sq=0.0, belly=1.0):
    def sp(u):
        px = x + dr * lerp(-1.85, 0.5, u) * s * (1 + sq)
        w = wig * 0.1 * s * math.sin(u * 7 - t * 9) * (1 - u) ** 1.2 + 0.03 * s * math.sin(u * 4 - t * 3) * (1 - u)
        c = -curl * s * 0.95 * cl(1 - u / 0.42) ** 2
        return px, y + w + c
    bc = mix(BODY, BODY_UV, uv); hc = mix(BODY_HI, BODY_UV_HI, uv)
    d.ell(x - dr * 0.5 * s, y + 0.42 * s, 1.5 * s, 0.07 * s, A((0, 0, 0), 0.22 * a * (1 - uv)))
    legs = [(0.6, -1), (0.94, -1), (0.6, 1), (0.94, 1)]
    def leg(u, near):
        ax, ay = sp(u); ph = math.sin(t * 9 * walk + (0 if (u > 0.8) == (near > 0) else math.pi)) if walk else 0
        fx_, fy_ = ax + dr * 0.14 * s * ph + (0.05 * s if near < 0 else 0), ay + 0.36 * s - 0.05 * s * max(0, ph) * (walk > 0)
        col = mix(bc, (0, 0, 0), 0.25) if near < 0 else bc
        d.line([(ax, ay), (fx_, fy_)], A(col, a), 0.13 * s)
        for k in range(3): d.circ(fx_ + dr * (k - 1) * 0.06 * s + dr * 0.04 * s, fy_ + 0.03 * s, 0.035 * s, fill=A(col, a))
    for u, n in legs[:2]: leg(u, n)
    N_ = 46
    for i in range(N_ + 1):
        u = i / N_; px, py = sp(u); d.circ(px, py, _r(u) * s, fill=A(bc, a))
    hx, hy = x + dr * 0.9 * s * (1 + sq), y - 0.1 * s
    d.ell(hx, hy, 0.56 * s, 0.44 * s, A(bc, a)); d.ell(hx + dr * 0.36 * s, hy + 0.12 * s, 0.28 * s, 0.24 * s, A(bc, a))
    for i in range(0, N_ + 1, 2):   # top sheen (no outline, just a lighter streak)
        u = i / N_; px, py = sp(u); d.circ(px, py - _r(u) * s * 0.55, _r(u) * s * 0.28, fill=A(hc, 0.35 * a))
    d.ell(hx - dr * 0.12 * s, hy - 0.3 * s, 0.26 * s, 0.07 * s, A(hc, 0.45 * a))
    for u, n in legs[2:]: leg(u, n)
    # spots + glow
    for (u, v, rr, kind) in SPOTS:
        if kind == 2 and belly <= 0: continue
        px, py = sp(u); py += v * _r(u) * s * 0.85
        R = rr * s
        gcol = NEON if kind == 0 else (NEON_C if kind == 1 else mix(NEON, NEON_C, 0.4))
        gk = uv * glowk * (0.55 if kind == 0 else 1.0) * (belly if kind == 2 else 1)
        if gk > 0.02: glow(d, px, py, R * (2.5 if kind else 1.9), gcol, gk * 0.55, 5)
        c = mix(SPOT if kind < 2 else SPOT_D, mix(gcol, WHITE, 0.25 * gk), cl(uv * 1.2))
        d.ell(px, py, R * 1.15, R * 0.8, A(c, a))
        d.ell(px - R * 0.3, py - R * 0.25, R * 0.4, R * 0.22, A(WHITE, (0.35 + 0.4 * gk) * a))
    # parotoid glands (yellow bumps behind the eyes) + brow spot
    for gx, gy, rx, ry in [(-0.36, -0.28, 0.17, 0.1), (-0.05, -0.38, 0.1, 0.06)]:
        px, py = hx + dr * gx * s, hy + gy * s
        if uv * glowk > 0.02: glow(d, px, py, 0.3 * s, NEON, uv * glowk * 0.55, 5)
        d.ell(px, py, rx * s, ry * s, A(mix(SPOT, mix(NEON, WHITE, 0.3), cl(uv * 1.2)), a))
    sface(d, hx + dr * 0.14 * s, hy + 0.04 * s, 0.46 * s, mood, a, look * dr, wink)
    return hx, hy
LITE = (236, 236, 250); PINK = (255, 110, 140); PINK_D = (150, 30, 60)
def sface(d, x, y, r, kind, a, look=0.0, wink=0.0):
    """salamander face: drawn in light colours so it reads on the near-black head (no outlines)."""
    er = r * 0.19; ey = y - r * 0.1
    for s_ in (-1, 1):
        ex = x + s_ * r * 0.36
        closed = kind in ("happy", "proud") or (wink > 0.5 and s_ == 1)
        if closed:
            d.arc(ex, ey + er * 0.4, er, er * 0.8, 200, 340, A(LITE, a), er * 0.45)
        elif kind == "dizzy":
            d.line([(ex - er, ey - er), (ex + er, ey + er)], A(LITE, a), er * 0.4); d.line([(ex - er, ey + er), (ex + er, ey - er)], A(LITE, a), er * 0.4)
        else:
            big = 1.3 if kind in ("scream", "scared") else 1.0
            d.circ(ex, ey, er * big, fill=A(WHITE, a))
            pr_ = er * (0.32 if kind in ("scream", "scared") else 0.55)
            d.circ(ex + look * er * 0.4, ey + er * (0.25 if kind in ("angry", "sus") else 0.05), pr_, fill=A(INK, a))
            d.circ(ex + look * er * 0.4 - pr_ * 0.35, ey - pr_ * 0.3, pr_ * 0.3, fill=A(WHITE, a))
            if kind == "sus": d.rect(ex - er * 1.1, ey - er * 1.3, ex + er * 1.1, ey - er * 0.15, fill=A((44, 40, 60), a), r=er * 0.3)
        if kind == "angry":
            d.line([(ex + s_ * er * 1.25, ey - er * 1.95), (ex - s_ * er * 1.0, ey - er * 1.05)], A(LITE, a), er * 0.5)
        if kind == "sus":
            d.line([(ex - er * 1.1, ey - er * (1.4 + 0.3 * s_)), (ex + er * 1.1, ey - er * (1.4 - 0.3 * s_))], A(LITE, a), er * 0.4)
    my = y + r * 0.42
    if kind == "angry":
        d.rect(x - r * 0.3, my - r * 0.1, x + r * 0.3, my + r * 0.12, fill=A(WHITE, a), r=r * 0.06)
        d.line([(x - r * 0.3, my), (x + r * 0.3, my)], A((120, 120, 140), a), r * 0.035)
        for k in (-1, 0, 1): d.line([(x + k * r * 0.12, my - r * 0.1), (x + k * r * 0.12, my + r * 0.12)], A((120, 120, 140), a), r * 0.03)
    elif kind in ("happy", "proud") or wink > 0.5:
        d.d.chord((P(x - r * .38), P(my - r * .25), P(x + r * .38), P(my + r * .28)), 0, 180, fill=A(PINK, a))
    elif kind == "scream":
        d.ell(x, my + r * 0.05, r * 0.24, r * 0.3, A(PINK_D, a)); d.ell(x, my + r * 0.2, r * 0.14, r * 0.1, A(PINK, a))
    elif kind == "scared":
        d.ell(x, my, r * 0.1, r * 0.13, A(PINK, a)); d.ell(x + r * 0.78, y - r * 0.45, r * 0.08, r * 0.13, A(CYAN, a))
    elif kind in ("sus", "dizzy"):
        d.line([(x - r * .22, my), (x + r * .22, my + r * 0.04)], A(PINK, a), r * 0.07)
    else:
        d.arc(x, my - r * 0.2, r * 0.3, r * 0.22, 20, 160, A(PINK, a), r * 0.07)
def bcol_mask(): return (0, 0, 0)

# ---------------- props ----------------
def uvlamp(d, x0, x1, y, on, t, a=1.0):
    fl = on * (0.85 + 0.15 * math.sin(t * 53))
    if fl > 0.01:
        d.poly([(x0, y), (x1, y), (x1 + 120, y + 900), (x0 - 120, y + 900)], A(UVC, 0.10 * fl * a))
        glow(d, (x0 + x1) / 2, y, (x1 - x0) * 0.55, UVC, 0.8 * fl * a, 7)
    d.rect(x0 - 30, y - 40, x1 + 30, y - 18, fill=A((70, 70, 90), a), r=10)
    d.rect(x0, y - 18, x1, y + 18, fill=A(mix((90, 80, 120), (235, 210, 255), fl), a), r=18)
def poison(d, x, y, s, a=1.0):
    d.circ(x, y + 0.2 * s, 0.6 * s, fill=A((150, 60, 210), a)); d.poly([(x - 0.42 * s, y - 0.2 * s), (x, y - 0.95 * s), (x + 0.42 * s, y - 0.2 * s)], A((150, 60, 210), a))
    d.ell(x - 0.22 * s, y - 0.05 * s, 0.12 * s, 0.2 * s, A(WHITE, 0.4 * a))
    for s_ in (-1, 1):
        ex, ey = x + s_ * 0.22 * s, y + 0.15 * s; e = 0.1 * s
        d.line([(ex - e, ey - e), (ex + e, ey + e)], A(WHITE, a), 0.06 * s); d.line([(ex - e, ey + e), (ex + e, ey - e)], A(WHITE, a), 0.06 * s)
    d.arc(x, y + 0.55 * s, 0.2 * s, 0.1 * s, 200, 340, A(WHITE, a), 0.05 * s)
def scientist(d, x, y, s, t, mood, a=1.0, look=0.3):
    d.rect(x - 0.55 * s, y + 0.25 * s, x + 0.55 * s, y + 1.5 * s, fill=A((236, 244, 250), a), r=0.4 * s)
    d.poly([(x - 0.12 * s, y + 0.25 * s), (x, y + 0.6 * s), (x + 0.12 * s, y + 0.25 * s)], A((90, 140, 220), a))
    d.circ(x, y - 0.15 * s, 0.45 * s, fill=A(SKIN, a))
    d.d.chord((P(x - 0.47 * s), P(y - 0.65 * s), P(x + 0.47 * s), P(y - 0.05 * s)), 180, 360, fill=A((70, 50, 40), a))
    face(d, x, y - 0.1 * s, 0.38 * s, mood, a, look)
    for s_ in (-1, 1): d.circ(x + s_ * 0.137 * s, y - 0.155 * s, 0.11 * s, outline=A((60, 60, 80), a), w=0.03 * s)
def microscope(d, x, y, s, a=1.0):
    d.rect(x - 0.5 * s, y + 0.8 * s, x + 0.5 * s, y + 0.95 * s, fill=A((60, 70, 90), a), r=0.05 * s)
    d.line([(x + 0.2 * s, y + 0.85 * s), (x + 0.25 * s, y - 0.2 * s), (x - 0.05 * s, y - 0.55 * s)], A((80, 90, 110), a), 0.16 * s)
    d.line([(x - 0.05 * s, y - 0.55 * s), (x - 0.25 * s, y - 0.05 * s)], A((200, 210, 225), a), 0.2 * s)
    d.rect(x - 0.45 * s, y + 0.15 * s, x + 0.2 * s, y + 0.25 * s, fill=A((60, 70, 90), a), r=0.03 * s)
def paper(d, x, y, w, h, rot, a=1.0, col=(250, 250, 244), lines=True):
    c, sn = math.cos(rot), math.sin(rot)
    def R(px, py): return x + px * c - py * sn, y + px * sn + py * c
    d.poly([R(-w / 2, -h / 2), R(w / 2, -h / 2), R(w / 2, h / 2), R(-w / 2, h / 2)], A(col, a))
    if lines:
        for k in range(5): d.line([R(-w * 0.38, -h * 0.3 + k * h * 0.15), R(w * (0.38 if k % 2 else 0.2), -h * 0.3 + k * h * 0.15)], A((150, 160, 180), a), max(2, h * 0.03))
def heart(d, x, y, r, col, a=1.0):
    if r <= 0.5 or a <= 0.01: return
    d.circ(x - r * 0.5, y - r * 0.2, r * 0.55, fill=A(col, a)); d.circ(x + r * 0.5, y - r * 0.2, r * 0.55, fill=A(col, a))
    d.poly([(x - r * 1.02, y - 0.05 * r), (x + r * 1.02, y - 0.05 * r), (x, y + r * 1.05)], A(col, a))
def fox(d, x, y, s, t, mood, a=1.0, look=-0.6):
    d.poly([(x - 0.75 * s, y - 0.3 * s), (x - 0.55 * s, y - 1.05 * s), (x - 0.2 * s, y - 0.55 * s)], A(FOXC, a))
    d.poly([(x + 0.75 * s, y - 0.3 * s), (x + 0.55 * s, y - 1.05 * s), (x + 0.2 * s, y - 0.55 * s)], A(FOXC, a))
    d.poly([(x - 0.62 * s, y - 0.45 * s), (x - 0.55 * s, y - 0.85 * s), (x - 0.35 * s, y - 0.55 * s)], A((90, 40, 30), a))
    d.poly([(x + 0.62 * s, y - 0.45 * s), (x + 0.55 * s, y - 0.85 * s), (x + 0.35 * s, y - 0.55 * s)], A((90, 40, 30), a))
    d.ell(x, y - 0.1 * s, 0.8 * s, 0.6 * s, A(FOXC, a))
    d.poly([(x - 0.8 * s, y - 0.05 * s), (x + 0.8 * s, y - 0.05 * s), (x, y + 0.75 * s)], A(FOX_L, a))
    d.circ(x, y + 0.62 * s, 0.11 * s, fill=A(INK, a))
    face(d, x, y - 0.12 * s, 0.6 * s, mood, a, look, nomouth=True)
def firefly(d, x, y, s, t, lit, a=1.0):
    if lit > 0.01: glow(d, x - 0.35 * s, y + 0.1 * s, 1.3 * s, (230, 255, 120), lit * a, 7)
    for s_ in (-1, 1):
        fl = math.sin(t * 40) * 0.25
        d.ell(x + 0.05 * s, y - 0.35 * s, 0.35 * s, 0.16 * s, A((210, 230, 255), 0.55 * a))
    d.ell(x - 0.32 * s, y + 0.1 * s, 0.3 * s, 0.22 * s, A(mix((120, 110, 60), (240, 255, 150), lit), a))
    d.ell(x + 0.1 * s, y, 0.3 * s, 0.22 * s, A((70, 50, 40), a)); d.circ(x + 0.45 * s, y - 0.02 * s, 0.17 * s, fill=A((220, 60, 50), a))
    d.circ(x + 0.5 * s, y - 0.06 * s, 0.06 * s, fill=A(WHITE, a)); d.circ(x + 0.52 * s, y - 0.06 * s, 0.03 * s, fill=A(INK, a))
    d.line([(x + 0.55 * s, y - 0.15 * s), (x + 0.75 * s, y - 0.45 * s)], A((70, 50, 40), a), 0.03 * s)
def hexmol(d, cx, cy, R, rot, col, a=1.0, w=10):
    pts = [(cx + R * math.cos(rot + k * math.pi / 3), cy + R * math.sin(rot + k * math.pi / 3)) for k in range(7)]
    d.line(pts, A(col, a), w)
    for px, py in pts[:6]: d.circ(px, py, w * 1.2, fill=A(col, a))
    return pts
def clock(d, x, y, R, ang_h, ang_m, a=1.0, col=WHITE):
    d.circ(x, y, R + 12, fill=A((60, 40, 110), a)); d.circ(x, y, R, fill=A(col, a))
    for k in range(12):
        an = k * math.pi / 6; d.line([(x + R * 0.82 * math.sin(an), y - R * 0.82 * math.cos(an)), (x + R * 0.95 * math.sin(an), y - R * 0.95 * math.cos(an))], A(NAVYT, a), 6)
    d.line([(x, y), (x + R * 0.5 * math.sin(ang_h), y - R * 0.5 * math.cos(ang_h))], A(NAVYT, a), 12)
    d.line([(x, y), (x + R * 0.8 * math.sin(ang_m), y - R * 0.8 * math.cos(ang_m))], A((230, 70, 90), a), 7)
    d.circ(x, y, 12, fill=A(NAVYT, a))
def stars(d, t, n=40, a=1.0, seed=3):
    r2 = random.Random(seed)
    for i in range(n):
        x, y = r2.uniform(180, 900), r2.uniform(250, 1250); tw = 0.5 + 0.5 * math.sin(t * r2.uniform(2, 5) + i)
        d.circ(x, y, r2.uniform(2, 5), fill=A(WHITE, a * (0.3 + 0.6 * tw)))
def uvbg(d, t, k=1.0, cx=540, cy=900):
    rays(d, t, mix((40, 14, 80), (96, 36, 190), k), mix((20, 8, 40), (60, 20, 130), k), n=20, cx=cx, cy=cy)
def ground(d, y, col, top):
    d.rect(-50, y, OW + 50, OH + 50, fill=A(col, 1)); d.rect(-50, y, OW + 50, y + 22, fill=A(top, 1))
def trees(d, y, col, n=6, h=520, seed=4, a=1.0):
    r2 = random.Random(seed)
    for i in range(n):
        x = r2.uniform(60, 1020); hh = h * r2.uniform(0.7, 1.1); w = hh * 0.3
        d.rect(x - 14, y - hh * 0.4, x + 14, y, fill=A(col, a))
        d.poly([(x - w, y - hh * 0.3), (x, y - hh), (x + w, y - hh * 0.3)], A(col, a))
        d.poly([(x - w * 0.8, y - hh * 0.55), (x, y - hh * 1.15), (x + w * 0.8, y - hh * 0.55)], A(col, a))

# ---------------- scenes ----------------
def s_hook(t, d):
    hit = t >= HOOK_HIT
    if t < LIGHT_OFF:
        grad(d, (250, 196, 110), (200, 120, 60)); ground(d, 1150, (150, 90, 50), (230, 160, 90))
        glow(d, 540, 330, 260, (255, 240, 190), 0.8)
    elif not hit:
        grad(d, (12, 10, 22), (4, 4, 10)); ground(d, 1150, (8, 8, 14), (20, 18, 30))
    else:
        uvbg(d, t, 0.6 + 0.4 * pulse(t, [HOOK_HIT], 2), 540, 980); ground(d, 1150, (36, 12, 70), (110, 50, 200))
    stopped = t >= HOOK_STOP
    uv = ease(pr(t, HOOK_HIT - 0.03, HOOK_HIT + 0.08)) if hit else 0
    gk = 1.0 + 0.8 * pulse(t, [HOOK_HIT], 3)
    mood = "angry" if t < HOOK_HIT else ("scream" if t < 1.7 else ("proud" if not stopped else "sus"))
    sq = 0.08 * math.exp(-max(0, t - HOOK_HIT) * 5) * math.sin(max(0, t - HOOK_HIT) * 30) if hit else 0
    dark = 0.75 if (LIGHT_OFF <= t < HOOK_HIT) else 0
    sal(d, 580, 960, 205, t, mood, uv, gk, curl=0.25 + (0.25 if hit else 0) * eio(pr(t, HOOK_HIT, HOOK_HIT + 0.4)), wig=0 if stopped else (1.2 if hit else 0.3), look=0.3, sq=sq)
    if dark: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), dark))
    uvlamp(d, 300, 780, 560, 1.0 if hit else 0.0, t)
    rings(d, 540, 960, t, [HOOK_HIT], NEON, 1.0, 520)
    sparks(d, 540, 960, t, HOOK_HIT, n=70, spd=1300, col=(170, 255, 190), seed=3)
    sparks(d, 540, 900, t, HOOK_HIT + 0.05, n=40, spd=900, col=(120, 240, 255), seed=4)
    if t < LIGHT_OFF: d.text(540, 360, "关灯！", 150, A(WHITE, 1), k=1)
    elif not hit:
        d.text(540, 360, "啪！", 170, A(WHITE, 1), k=1)
    else:
        stamp2(d, t, HOOK_HIT, ["有毒蝾螈", "会发光！"], 300, 128, (190, 255, 150), 140)

def s_meet(t, d):
    grad(d, (150, 220, 190), (80, 170, 130)); trees(d, 1000, (110, 190, 140), 7, 560, 9); trees(d, 1040, (70, 150, 100), 5, 460, 21)
    d.rect(-50, 1040, OW + 50, OH + 50, fill=A((88, 150, 80), 1))
    d.rect(-50, 1150, OW + 50, 1260, fill=A((90, 170, 230), 1))
    for i in range(8):
        xx = (i * 170 + t * 120) % 1200 - 60; d.line([(xx, 1190 + (i % 3) * 22), (xx + 70, 1190 + (i % 3) * 22)], A(WHITE, 0.5), 5)
    for rx, rr in [(250, 50), (820, 64)]: d.ell(rx, 1150, rr, rr * 0.55, A((150, 150, 140), 1))
    walk = 1.0 if t < MEET_TAGS[1] else 0.0
    xo = lerp(-80, 0, ease(pr(t, MEET, MEET_TAGS[0])))
    sal(d, 600 + xo, 1000, 170, t, "chill" if t < MEET_TAGS[1] else "angry", 0, walk=walk, wig=0.6 * walk, look=0.5, sq=0.06 * pulse(t, MEET_TAGS, 7))
    tag(d, 420, 830, "火蝾螈", (255, 210, 60), popk(t, MEET_TAGS[0]), 50)
    k = popk(t, MEET_TAGS[1])
    if k > 0:
        poison(d, 800, 620, 90 * k); tag(d, 800, 760, "有毒", (150, 60, 210), k, 40, WHITE)
    tag(d, 390, 600, "毒素之一：蝾螈碱", WHITE, popk(t, MEET_TAGS[2]), 34, (40, 100, 70))
    k = popk(t, MEET_TAGS[3])
    if k > 0:
        d.rect(250, 470, 520, 540, fill=A((230, 60, 50), k), r=14); d.text(385, 505, "易危 VU", 40, A(WHITE, k), k=1)
        d.text(385, 448, "IUCN 红色名录", 26, A((20, 60, 40), k), k=1)
    stamp2(d, t, MEET + 0.1, ["黑黄 = 我有毒"], 330, 96, (30, 34, 44))

def s_lab(t, d):
    grad(d, (120, 214, 236), (60, 150, 190))
    for i in range(10):
        for j in range(8): d.rect(i * 120 - 10, 240 + j * 120, i * 120 + 104, 240 + j * 120 + 104, fill=A(WHITE, 0.08))
    d.rect(-50, 1080, OW + 50, OH + 50, fill=A((70, 90, 120), 1)); d.rect(-50, 1080, OW + 50, 1110, fill=A((200, 220, 235), 1))
    n = sum(1 for h in PAPERS if t >= h)
    for i in range(n):   # stack grows
        k = popk(t, PAPERS[i]); yy = 1070 - i * 26
        paper(d, 720 + 8 * math.sin(i * 2.1), yy - 60 * (1 - k), 260, 30, 0.04 * math.sin(i * 3.1), 1, mix((250, 250, 244), (255, 236, 200), (i % 3) / 2), lines=False)
    for i in range(4):   # flying flipped pages
        u = ((t - LAB) * 1.6 + i / 4) % 1
        paper(d, lerp(380, 700, u), 760 - 260 * math.sin(u * math.pi), 120, 150, u * 6, 0.85 * math.sin(u * math.pi))
    microscope(d, 420, 940, 170)
    d.ell(350, 970, 70, 16, A((220, 240, 255), 0.7))
    sal(d, 360, 960, 26, t, "sus", 0)
    scientist(d, 250, 830, 120, t, "dizzy" if t > PAPERS[6] else "sus", look=0.6)
    tag(d, 720, 1070 - n * 26 - 50, f"论文 x {n * 10}+" if n else "", WHITE, popk(t, PAPERS[0]) if n else 0, 34, (40, 90, 140))
    stamp2(d, t, LAB_STAMP, ["研究了几十年"], 330, 100, WHITE)
    for i in range(3):
        hexmol(d, 260 + i * 260, 520 + 30 * math.sin(t * 2 + i), 40, t * (1 + i * 0.3), WHITE, 0.25, 6)

def s_none(t, d):
    rays(d, t, (255, 214, 80), (250, 170, 50), n=22, cx=540, cy=900)
    for i in range(14):
        paper(d, 540 + 12 * math.sin(i * 1.7), 1090 - i * 28, 380, 34, 0.05 * math.sin(i * 2.3), 1, mix((250, 250, 244), (230, 236, 255), (i % 2)), lines=False)
    for j, h in enumerate(QMARKS + [qb(22.5), qb(23), qb(23.5)]):
        k = popk(t, h)
        if k > 0:
            ang = j * 2.1; x = 540 + math.cos(ang) * (230 + 30 * (j % 2)); y = 640 + math.sin(ang) * 140 - 20 * math.sin(t * 4 + j)
            d.text(x, y, "?", int(110 * k), A((120, 70, 200), 1), k=1)
    # salamander peeks from behind the pile
    pk = ease(pr(t, NONE + 0.3, NONE + 0.8))
    sal(d, 820, 1180 - 90 * pk, 120, t, "proud" if t > ZERO + 0.3 else "sus", 0, look=-0.6, dr=-1, curl=0.4)
    k = popk(t, ZERO)
    if k > 0:
        d.rect(250, 400, 830, 520, fill=A((230, 50, 60), k), r=30)
        d.text(540, 460, "荧光：0 篇", int(76 * (0.6 + 0.4 * k)), A(WHITE, 1), k=1)
    tag(d, 540, 580, "几十年，没人报道过", WHITE, popk(t, NONE_TAG), 40, (200, 60, 60))
    if t < ZERO: stamp2(d, t, NONE + 0.05, ["没人发现？"], 460, 110, (120, 60, 200))

def s_switch(t, d):
    k = pr(t, SWITCH, SIL0)
    grad(d, mix((60, 50, 90), (14, 10, 26), k), mix((30, 24, 50), (6, 4, 12), k))
    glow(d, 540, 760, 360, UVC, 0.25 + 0.35 * k)
    d.rect(370, 560, 710, 980, fill=A((220, 220, 235), 1), r=40); d.rect(400, 590, 680, 950, fill=A((200, 200, 220), 1), r=28)
    d.rect(490, 640, 590, 900, fill=A((120, 110, 140), 1), r=30)
    d.rect(500, 660, 580, 760, fill=A((150, 90, 255), 1), r=24)
    d.text(540, 1030, "紫外灯", 54, A(UVC, 1), k=1)
    # finger creeping in
    fx_ = lerp(980, 560, eio(pr(t, SWITCH, SIL0 - 0.05))) + 8 * pulse(t, COUNT, 6)
    d.rect(fx_, 670, fx_ + 600, 760, fill=A(SKIN_D, 1), r=45); d.rect(fx_ + 4, 676, fx_ + 600, 750, fill=A(SKIN, 1), r=40)
    d.ell(fx_ + 40, 700, 26, 16, A((255, 230, 220), 1))
    for j, h in enumerate(COUNT):
        kk = popk(t, h)
        if kk > 0 and t < (COUNT[j + 1] if j + 1 < len(COUNT) else SIL0):
            d.text(540, 380, str(3 - j), int(220 * (1.6 - 0.6 * kk)), A(WHITE, 1), k=1)
    if t < COUNT[0]: d.text(540, 380, "准备……", 96, A(WHITE, 0.9), k=1)
    vignette(d, 0.5 + 0.5 * k)

def s_burst(t, d):
    uvbg(d, t, 1.0, 540, 900)
    glow(d, 540, 900, 600, (200, 140, 255), 0.6 * pulse(t, [BIG], 2))
    sq = 0.1 * math.exp(-(t - BIG) * 5) * math.sin((t - BIG) * 30)
    sal(d, 570, 900, 212, t, "scream" if t < BIG + 0.8 else "proud", 1.0, 1.4 + 0.8 * pulse(t, [BIG] + BURST_TAGS, 4), curl=0.3, wig=1.0, look=0.2, sq=sq)
    rings(d, 540, 960, t, [BIG], NEON, 1.0, 560); rings(d, 540, 960, t, [BIG + 0.12], NEON_C, 0.8, 520)
    sparks(d, 540, 950, t, BIG, n=90, spd=1400, col=(170, 255, 190), seed=5)
    sparks(d, 540, 950, t, BIG + 0.06, n=50, spd=1000, col=(140, 245, 255), seed=6)
    for i in range(28):
        u = ((t - BIG) * 0.5 + i / 28) % 1; x = 200 + (i * 97) % 700; y = 1150 - u * 800
        d.circ(x, y, 6, fill=A(NEON if i % 2 else NEON_C, 0.8 * math.sin(u * math.pi)))
    k1 = popk(t, BURST_TAGS[0]); k2 = popk(t, BURST_TAGS[1])
    if k1 > 0: arrow(d, 330, 1150, 520, 1010, NEON, k1, 16); tag(d, 300, 1180, "腹部", NEON, k1, 42)
    if k2 > 0: arrow(d, 820, 650, 640, 860, NEON_C, k2, 16); tag(d, 800, 620, "身体两侧", NEON_C, k2, 42)
    stamp2(d, t, BIG, ["肚子在发光！"], 340, 118, (200, 255, 170))

def s_venom(t, d):
    grad(d, (40, 24, 90), (14, 8, 40)); stars(d, t, 30, 0.4, 7)
    uvlamp(d, 260, 600, 440, 1.0, t, 0.9)
    sal(d, 600, 640, 110, t, "chill", 1.0, 1.0, dr=1, look=0.6)
    # drop forms under the parotoid gland, falls, lands on a glass slide
    sx_, sy_ = 640, 1030
    d.rect(250, sy_, 830, sy_ + 40, fill=A((200, 230, 255), 0.45), r=8); d.rect(250, sy_, 830, sy_ + 8, fill=A(WHITE, 0.6), r=4)
    gx = 560
    if t < DRIP:
        u = pr(t, VENOM + 0.15, DRIP); yy = lerp(680, sy_ - 22, u ** 2)
        r_ = 10 + 12 * pr(t, VENOM, VENOM + 0.4)
        glow(d, gx, yy, 50, NEON, 0.8); d.circ(gx, yy, r_, fill=A(mix(NEON, WHITE, 0.3), 1))
    else:
        k = popk(t, DRIP); pp = 0.8 + 0.2 * math.sin(t * 6)
        glow(d, gx, sy_ - 10, 160 * pp, NEON, 0.9); d.ell(gx, sy_ - 8, 70 * k, 22 * k, A(mix(NEON, WHITE, 0.3), 1))
        sparks(d, gx, sy_ - 10, t, DRIP, n=24, spd=500, col=(180, 255, 190), seed=9, life=0.6)
        rings(d, gx, sy_ - 10, t, [DRIP], NEON, 0.8, 220)
    # 24 h clock
    ck = popk(t, CLOCK0)
    if ck > 0:
        hrs = 24 * ease(pr(t, CLOCK0, CLOCK1)); cx, cy = 790, 850
        clock(d, cx, cy, 80 * ck, hrs / 12 * 2 * math.pi, hrs * 2 * math.pi, 1)
        tag(d, cx, cy + 140, f"{int(hrs)} 小时", WHITE, ck, 40, (60, 20, 120))
    tag(d, gx, sy_ + 90, "毒液分泌物", NEON, popk(t, DRIP + 0.2), 36)
    stamp2(d, t, VEN_STAMP, ["24 小时还在亮！"], 330, 92, (200, 255, 170))
    if t < VEN_STAMP: stamp2(d, t, VENOM + 0.05, ["毒液也会亮"], 330, 100, WHITE)

def s_fluo(t, d):
    """'一句话学会' knowledge card: 生物发光 = 自己点灯 / 荧光 = 借光再发光"""
    grad(d, (44, 20, 96), (16, 8, 44))
    for i in range(12): d.line([(180 + i * 65, 230), (180 + i * 65, 1240)], A(WHITE, 0.04), 3)
    ck = popk(t, FLUO)
    d.rect(190, 290, 890, 1170, fill=A((250, 248, 240), ck), r=40)
    tag(d, 540, 290, "一句话学会", GOLD, popk(t, FLUO + 0.05), 46)
    # row 1: firefly lights itself
    k1 = popk(t, FLUO + 0.15)
    d.rect(220, 350, 860, 690, fill=A((22, 60, 46), k1), r=30)
    lit = max([pulse(t, [h], 2.5) for h in FIREFLY] + [0.45 if t > FIREFLY[0] else 0])
    if k1 > 0.05: firefly(d, 340, 520, 80 * k1, t, lit, 1)
    d.text(640, 440, "生物发光", 50, A((240, 255, 150), k1), k=1)
    d.text(640, 520, "=", 50, A(WHITE, popk(t, FIREFLY[1])), k=1)
    d.text(640, 605, "自己点灯", 76, A(WHITE, popk(t, FIREFLY[1])), k=1)
    d.text(340, 650, "萤火虫", 30, A(WHITE, 0.8 * k1), k=1)
    # row 2: salamander borrows invisible UV light and re-emits green
    k2 = popk(t, UVON - 0.25)
    d.rect(220, 720, 860, 1060, fill=A((60, 24, 120), k2), r=30)
    on = ease(pr(t, UVON - 0.05, UVON + 0.1)) * (0.85 + 0.15 * math.sin(t * 53))
    if k2 > 0.05:
        d.poly([(260, 790), (420, 790), (450, 1000), (240, 1000)], A(UVC, 0.16 * on * k2))
        glow(d, 340, 780, 70, UVC, 0.6 * on * k2, 5)
        d.rect(255, 765, 425, 795, fill=A(mix((90, 80, 120), (235, 210, 255), on), k2), r=15)
        sal(d, 360, 960, 56 * k2, t, "chill" if t < UVON else "proud", on, 1.4, curl=0.2)
    kc = popk(t, CONVERT)
    if kc > 0:
        d.line([(445 + i * 5, 840 + 10 * math.sin(i * 1.2)) for i in range(int(12 * kc))], A(UVC, 1), 6)
        d.text(472, 810, "紫外光", 22, A((220, 190, 255), kc), k=1)
        d.line([(445 + i * 5, 990 + 12 * math.sin(i * 0.6)) for i in range(int(12 * kc))], A(NEON, 1), 6)
        d.text(472, 1030, "绿光", 22, A(NEON, kc), k=1)
    d.text(680, 800, "荧光", 50, A(NEON, k2), k=1)
    d.text(680, 880, "=", 50, A(WHITE, popk(t, CONVERT)), k=1)
    d.text(680, 965, "借光再发光", 64, A(WHITE, popk(t, CONVERT)), k=1)
    k = popk(t, FLUO_TAG)
    if k > 0:
        d.rect(250, 1085, 830, 1145, fill=A(NEON, k), r=30)
        d.text(540, 1115, "火蝾螈是荧光，不是自己点灯", 32, A(NAVYT, k), k=1)
def s_mol(t, d):
    grad(d, (10, 50, 56), (4, 18, 24))
    for i in range(12): d.line([(180 + i * 65, 230), (180 + i * 65, 1240)], A(NEON_C, 0.06), 3)
    for i in range(16): d.line([(180, 250 + i * 65), (900, 250 + i * 65)], A(NEON_C, 0.06), 3)
    rot = t * 0.8; gp = pulse(t, GLITCH, 8)
    p1 = hexmol(d, 470, 760, 120, rot, NEON, 1, 12)
    p2 = hexmol(d, 470 + 208 * math.cos(rot + 0.52), 760 + 208 * math.sin(rot + 0.52), 120, rot + math.pi / 3, NEON_C, 1, 12)
    for px, py in [p1[3], p2[1]]:
        d.line([(px, py), (px + 80 * math.cos(rot * 2), py + 80 * math.sin(rot * 2))], A(WHITE, 0.7), 8)
    k = 1 + 0.25 * gp
    glow(d, 560, 760, 260, NEON, 0.35 + 0.4 * gp)
    d.text(560, 760, "?", int(260 * k), A(WHITE, 1), k=1)
    for j in range(5):
        ang = t * 1.2 + j * 1.26; d.text(560 + math.cos(ang) * 300, 760 + math.sin(ang) * 260, "?", 70, A(NEON_C, 0.7), k=1)
    tag(d, 540, 1130, "很可能是没认识过的新分子", NEON, popk(t, MOL_TAG), 38)
    stamp2(d, t, MOL + 0.05, ["未知分子"], 340, 120, WHITE)

def s_moon(t, d):
    grad(d, (28, 40, 110), (10, 14, 50)); stars(d, t, 50, 0.8, 11)
    glow(d, 720, 470, 240, (230, 230, 255), 0.6); d.circ(720, 470, 120, fill=A((250, 248, 230), 1))
    for cx, cy, r in [(680, 440, 22), (760, 500, 16), (700, 520, 12)]: d.circ(cx, cy, r, fill=A((225, 222, 205), 1))
    trees(d, 1150, (16, 22, 60), 6, 520, 13)
    d.rect(-50, 1150, OW + 50, OH + 50, fill=A((14, 20, 50), 1))
    sal(d, 370, 1080, 108, t, "happy", 0.85, 1.2, dr=1, look=0.6, curl=0.1)
    sal(d, 710, 1080, 108, t, "happy", 0.85, 1.2, dr=-1, look=0.6, curl=0.1, wink=1.0 if HEARTS[2] <= t < HEARTS[2] + 0.4 else 0)
    for j, h in enumerate(HEARTS):
        u = t - h
        if 0 <= u < 1.6: heart(d, 560 + 30 * math.sin(u * 4 + j), 940 - u * 160, 34 * min(1, back(u / 0.25)), (255, 110, 160), 1 - u / 1.6)
    tag(d, 330, 330, "猜想 1", WHITE, popk(t, MOON + 0.1), 40, (40, 50, 140))
    tag(d, 670, 630, "满月光里，紫光比例更高", (230, 230, 255), popk(t, MOON_TAG), 32)
    stamp(d, t, HEARTS[0] - 0.4, "同伴暗号？", 540, 800, 92, (200, 255, 170))

def s_pred(t, d):
    grad(d, (250, 130, 80), (150, 50, 70)); trees(d, 1150, (110, 40, 60), 6, 540, 17)
    d.rect(-50, 1150, OW + 50, OH + 50, fill=A((90, 30, 50), 1))
    fxp = lerp(1000, 740, ease(pr(t, PRED, FOX_IN + 0.5)))
    rec = ease(pr(t, ZAP2, ZAP2 + 0.3)); fxp += 160 * rec
    zp = pulse(t, [ZAP, ZAP2], 3)
    fox(d, fxp, 820 - 20 * rec, 150, t, "scared" if t > ZAP else "sus", 1, -0.7)
    if t > ZAP: d.text(fxp - 40, 560, "!", 120, A(WHITE, 1), k=1)
    on = 1.0 if t > ZAP - 0.05 else 0.15
    if t > ZAP: d.rect(0, 0, OW, OH, fill=A((40, 0, 80), 0.3 * zp))
    sal(d, 420, 1060, 120, t, "angry", on, 1.0 + 2.0 * zp, curl=0.5, wig=0.5, look=0.8)
    rings(d, 420, 1040, t, [ZAP, ZAP2], NEON, 1.0, 500)
    tag(d, 330, 330, "猜想 2", WHITE, popk(t, PRED + 0.1), 40, (150, 50, 70))
    stamp(d, t, PRED_STAMP, "别吃我！", 540, 470, 120, (200, 255, 170))

def s_end(t, d):
    grad(d, (16, 24, 44), (6, 8, 18)); stars(d, t, 30, 0.6, 19)
    trees(d, 1180, (24, 40, 50), 7, 600, 23); d.rect(-50, 1180, OW + 50, OH + 50, fill=A((14, 24, 30), 1))
    ang = -0.5 + 1.0 * eio(pr(t, END, OUTRO))
    bx, by = 540, 1250; tx, ty = bx + math.sin(ang) * 900, by - math.cos(ang) * 900
    px_, py_ = -math.cos(ang), -math.sin(ang)
    d.poly([(bx, by), (tx + px_ * 260, ty + py_ * 260), (tx - px_ * 260, ty - py_ * 260)], A(UVC, 0.22))
    r2 = random.Random(5)
    for i in range(40):
        x, y = r2.uniform(200, 880), r2.uniform(420, 1150); h0 = DOTS0 + r2.uniform(0, 1.5)
        da = math.atan2(x - bx, by - y)
        inb = abs(da - ang) < 0.32
        k = popk(t, h0) * (1.0 if inb else 0.35)
        if k > 0.02 and t > h0:
            c = NEON if i % 2 else NEON_C; glow(d, x, y, 30, c, k * 0.9, 5); d.circ(x, y, 6, fill=A(mix(c, WHITE, .4), k))
    d.rect(bx - 40, by - 20, bx + 40, by + 120, fill=A((70, 70, 90), 1), r=12); d.rect(bx - 50, by - 40, bx + 50, by, fill=A((150, 90, 255), 1), r=10)
    stamp2(d, t, END_STAMP, ["身边还藏着", "多少秘密？"], 300, 104, WHITE)

def s_outro(t, d):
    uvbg(d, t, 0.8, 540, 950); ground(d, 1150, (36, 12, 70), (110, 50, 200))
    blink = WINK <= t < WINK + 0.5
    sal(d, 590, 960, 190, t, "happy", 1.0, 1.0 + 0.5 * pulse(t, [WINK, FINAL], 4), wink=1.0 if blink else 0, curl=0.3, wig=0.4, sq=0.06 * pulse(t, [WINK, FINAL], 7))
    bubble(d, 880, 640, "开灯！别偷看！", 1, WHITE, NAVYT, popk(t, BUB), 46)
    stamp2(d, t, OUTRO + 0.05, ["有毒，还会发光"], 360, 92, (200, 255, 170))
    d.text(540, 1290, "Burriel-Carranza et al., R. Soc. Open Sci. (2026)", 26, A(WHITE, 0.9))
    d.text(540, 1332, "DOI 10.1098/rsos.251991", 26, A(WHITE, 0.9))
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

def s_black(t, d): d.rect(-50, -50, OW + 50, OH + 50, fill=A((0, 0, 0), 1))
SECS = [(0, HOOK_END, s_hook), (MEET, LAB, s_meet), (LAB, NONE, s_lab), (NONE, SWITCH, s_none), (SWITCH, SIL0, s_switch), (SIL0, BIG, s_black),
        (BURST, VENOM, s_burst), (VENOM, FLUO, s_venom), (FLUO, MOL, s_fluo), (MOL, MOON, s_mol), (MOON, PRED, s_moon), (PRED, END, s_pred),
        (END, OUTRO, s_end), (OUTRO, 99, s_outro)]
CUTS = [HOOK_END, LAB, NONE, SWITCH, BIG, VENOM, FLUO, MOL, MOON, PRED, END, OUTRO]
def cam(t):
    z = 1.0 + 0.05 * pulse(t, HITS, 7) + 0.08 * pulse(t, [HOOK_HIT, BIG], 3)
    for a, b in RISERS:
        if a <= t < b: z += 0.14 * eio(pr(t, a, b))
    if HOOK_STOP <= t < HOOK_END: z += 0.04
    amp = 28 * pulse(t, [HOOK_HIT, BIG], 4) + 5 * pulse(t, HITS, 6)
    if HOOK_STOP <= t < HOOK_END: amp = 0
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx, 960 + sy
def glitch(img, t):
    g = max(pulse(t, GLITCH, 9) if MOL <= t < MOON else 0, 0)
    if g < 0.15: return img
    r2 = random.Random(int(t * 30))
    for _ in range(int(10 * g)):
        y = r2.randint(int(P(250)), int(P(1200))); h = r2.randint(int(P(10)), int(P(60))); dx = int(P(r2.uniform(-60, 60) * g))
        band = img.crop((0, y, W, y + h)); img.paste(band, (dx, y))
    return img
def frame(t):
    img = Image.new("RGB", (W, H), (30, 20, 50)); d = D(img)
    for a, b, sf in SECS:
        if a <= t < b: sf(t, d); break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); img = glitch(img, t); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.08 and c != BIG: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.5 * (1 - (t - c) / 0.08)))
    if BIG <= t < BIG + 0.12: d.rect(0, 0, OW, OH, fill=A((235, 255, 240), 0.8 * (1 - (t - BIG) / 0.12)))
    if HOOK_HIT <= t < HOOK_HIT + 0.1: d.rect(0, 0, OW, OH, fill=A((235, 255, 240), 0.6 * (1 - (t - HOOK_HIT) / 0.1)))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.2f}.png")
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
