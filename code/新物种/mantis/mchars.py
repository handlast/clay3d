# Flat 2D characters for the leaf-butt mantis: mantis (abdominal leaf lobes, glass wings), Selaginella frond, bird, gnat, amber.
# No dark outlines: shapes separated by value, highlights and glow only. Eyes/mouth lines may be dark.
import math, random
from chars import *          # base + fx + easing E, flatbg, rot, colors GOLD, NAVYT, ...

M_G = (124, 196, 92); M_GD = (78, 146, 66); M_GL = (178, 230, 130)       # mantis green
LOBE = (104, 182, 84); LOBE_L = (160, 220, 120)
SEL = (70, 150, 84); SEL_D = (44, 108, 62); SEL_L = (120, 196, 110)      # Selaginella
WINGC = (200, 240, 255)
AMB = (240, 150, 40); AMB_L = (255, 206, 90); AMB_D = (190, 96, 24)
DEAD = (150, 140, 120); DEAD_D = (110, 100, 86)
FOR1 = (22, 54, 50); FOR2 = (8, 20, 22)

def leafpoly(x, y, L, w, ang, n=10):
    """pointed oval leaf from base (x,y) along angle ang, length L, half-width w"""
    pts = []
    ca, sa = math.cos(ang), math.sin(ang)
    for i in range(n + 1):
        u = i / n; hw = w * math.sin(math.pi * u) ** 0.8 * (1.1 - 0.3 * u)
        pts.append((u * L, hw))
    for i in range(n, -1, -1):
        u = i / n; hw = w * math.sin(math.pi * u) ** 0.8 * (1.1 - 0.3 * u)
        pts.append((u * L, -hw))
    return [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]

def leaf(d, x, y, L, w, ang, col, a=1.0, rib=True, hi=None):
    if a <= 0.01 or L < 1: return
    d.poly(leafpoly(x, y, L, w, ang), A(col, a))
    if rib:
        c = hi or mix(col, (255, 255, 255), 0.35)
        d.line([(x, y), (x + math.cos(ang) * L * 0.75, y + math.sin(ang) * L * 0.75)], A(c, a * 0.8), max(1.5, w * 0.18))

def frond(d, x, y, s, ang, t, col=SEL, a=1.0, seed=0, sway=1.0, depth=2, L=360, dead=0.0):
    """Selaginella-like branching frond: stem + alternating branchlets, all covered with small scale leaves."""
    rr = random.Random(seed)
    c = mix(col, DEAD, dead); cl_ = mix(SEL_L, DEAD, dead); cd = mix(SEL_D, DEAD_D, dead)
    def branch(x0, y0, an, length, lvl):
        n = max(4, int(length / (22 * s)))
        pts = [(x0, y0)]; px, py, a_ = x0, y0, an
        for i in range(n):
            a_ += 0.05 * math.sin(t * 1.3 + seed + lvl) * sway + (0.03 if lvl % 2 else -0.03)
            px += math.cos(a_) * length / n; py += math.sin(a_) * length / n; pts.append((px, py))
        d.line(pts, A(cd, a), max(2, 6 * s * (1 - 0.3 * lvl)))
        for i in range(1, n + 1):
            bx, by = pts[i]; ta = math.atan2(pts[i][1] - pts[i - 1][1], pts[i][0] - pts[i - 1][0])
            sz = 26 * s * (1 - 0.5 * i / n) * (1 - 0.25 * lvl)
            for sd in (-1, 1):
                leaf(d, bx, by, sz, sz * 0.38, ta + sd * 0.95, c if (i + (sd > 0)) % 2 else mix(c, cl_, 0.35), a, rib=False)
            if lvl < depth and i % 3 == 1 and i < n - 1:
                sd = 1 if (i // 3) % 2 else -1
                branch(bx, by, ta + sd * (0.75 + 0.2 * rr.random()), length * 0.5, lvl + 1)
        leaf(d, pts[-1][0], pts[-1][1], 22 * s, 8 * s, a_, cl_, a, rib=False)
    branch(x, y, ang, L * s, 0)

def _seg_curve(x, y, s, wig, curl, flip):
    """abdomen spine points from root (near thorax) back to tip"""
    pts = []; n = 7; a_ = math.pi + 0.08 + wig
    px, py = x - 10 * s * flip, y + 6 * s
    for i in range(n + 1):
        pts.append((px, py))
        a_ += (-0.06 - curl * 0.05) + wig * 0.05 * i
        px += math.cos(a_) * 30 * s * flip; py += math.sin(a_) * 30 * s
    return pts

def mantis(d, x, y, s, t, a=1.0, face="happy", flip=1, wig=0.0, lobes=1.0, lobe_hi=0.0, hi_i=-1, wing=1.0, camo=0.0,
           col=None, kind="folio", look=0.0, arm=0.0, blush=0.0, eyes_open=1.0, glowk=0.0):
    """side view mantis facing right (flip=-1 faces left). wig: abdomen wiggle angle. lobes: 0..1 lobe size.
    camo: blend toward Selaginella colours with eyes half closed. arm: 0 folded .. 1 strike."""
    if a <= 0.01: return
    F_ = lambda px, py: (x + px * s * flip, y + py * s)
    g = col or M_G
    g = mix(g, SEL, camo * 0.8); gd = mix(M_GD if col is None else mix(col, (0, 0, 0), 0.3), SEL_D, camo * 0.8)
    gl = mix(M_GL if col is None else mix(col, (255, 255, 255), 0.4), SEL_L, camo * 0.8)
    lob = mix(LOBE, SEL, camo); lobl = mix(LOBE_L, SEL_L, camo)
    if glowk > 0: glow(d, x - 90 * s * flip, y, 260 * s, GOLD, 0.5 * glowk)
    d.ell(x - 40 * s * flip, y + 150 * s, 200 * s, 16 * s, A((0, 0, 0), 0.18 * a * (1 - camo)))
    # far legs (darker)
    for lx, fx_ in ((-6, -70), (16, 40)):
        hx, hy = F_(lx, 8); kx, ky = F_(lx + fx_ * 0.6, -40); ex, ey = F_(lx + fx_, 150)
        d.line([(hx, hy), (kx, ky), (ex, ey)], A(gd, a), 7 * s)
    # abdomen
    sp = _seg_curve(x, y, s, wig, 0.0, flip); n = len(sp) - 1
    for i in range(n, 0, -1):          # lobes first (behind body): a row of small leaf-like flaps on BOTH edges
        bx, by = sp[i]; ta = math.atan2(sp[i][1] - sp[i - 1][1], sp[i][0] - sp[i - 1][0])
        if i >= 1 and lobes > 0:
            r = (26 - 1.8 * i) * s
            sz = (46 + 6 * math.sin(i * 1.7)) * s * lobes * (1 - 0.06 * i)
            for sd in (-1, 1):
                col_ = lob if (i + (sd > 0)) % 2 else mix(lob, lobl, 0.4)
                if lobe_hi > 0 and hi_i in (-1, i): col_ = mix(col_, GOLD, lobe_hi)
                an = ta + sd * (math.pi / 2 - 0.55)
                bx2, by2 = bx + math.cos(ta + sd * math.pi / 2) * r * 0.55, by + math.sin(ta + sd * math.pi / 2) * r * 0.55
                leaf(d, bx2, by2, sz, sz * 0.36, an, col_, a, hi=mix(col_, (255, 255, 255), 0.45))
    d.line(sp, A(g, a), 40 * s)
    for i in range(n, -1, -1):
        bx, by = sp[i]; r = (26 - 1.8 * i) * s
        d.circ(bx, by, r, fill=A(g, a))
    for i in range(n, -1, -1):
        bx, by = sp[i]; r = (26 - 1.8 * i) * s
        d.ell(bx, by - r * 0.35, r * 0.7, r * 0.3, A(gl, a * 0.55))
    # wings (glass)
    if wing > 0:
        wx0, wy0 = F_(10, -24)
        tipx, tipy = sp[min(n, 5)]
        pts = [(wx0, wy0)]
        for k in range(1, 15):
            u = k / 14
            pts.append((lerp_(wx0, tipx, u), lerp_(wy0, tipy - 26 * s, u) - math.sin(math.pi * u) * 30 * s))
        for k in range(14, -1, -1):
            u = k / 14
            pts.append((lerp_(wx0, tipx, u), lerp_(wy0 + 8 * s, tipy - 14 * s, u) + math.sin(math.pi * u) * 6 * s))
        d.poly(pts, A(WINGC, 0.28 * a * wing))
        for k in (0.3, 0.55, 0.8):
            d.line([(lerp_(wx0, tipx, k * 0.6), lerp_(wy0, tipy, k * 0.6) - 20 * s), (lerp_(wx0, tipx, k), lerp_(wy0, tipy, k) - 22 * s)], A(WHITE, 0.35 * a * wing), 2.5 * s)
    # thorax (long neck)
    th0 = F_(0, 0); th1 = F_(90, -110)
    d.line([th0, th1], A(g, a), 26 * s)
    d.line([F_(10, -6), F_(86, -104)], A(gl, a * 0.6), 7 * s)
    # near legs
    for lx, fx_ in ((-14, -90), (8, 30)):
        hx, hy = F_(lx, 12); kx, ky = F_(lx + fx_ * 0.6, -30); ex, ey = F_(lx + fx_ * 1.05, 150)
        d.line([(hx, hy), (kx, ky), (ex, ey)], A(g, a), 9 * s)
    # raptorial foreleg
    sx_, sy_ = F_(76, -86)
    k_ = cl(arm)
    ex_, ey_ = F_(lerp_(126, 210, k_), lerp_(-30, -110, k_)); wx_, wy_ = F_(lerp_(104, 260, k_), lerp_(-74, -120, k_))
    d.line([(sx_, sy_), (ex_, ey_)], A(g, a), 14 * s); d.line([(ex_, ey_), (wx_, wy_)], A(g, a), 10 * s)
    for j in range(3):
        u = 0.3 + j * 0.22; px_, py_ = lerp_(sx_, ex_, u), lerp_(sy_, ey_, u)
        d.line([(px_, py_), (px_ - 8 * s * flip, py_ - 10 * s)], A(gl, a), 4 * s)
    # head
    hx, hy = F_(112, -128)
    d.poly([F_(78, -156), F_(150, -156), F_(118, -88)], A(g, a))
    d.ell(hx, hy - 10 * s, 46 * s, 32 * s, A(g, a))
    d.ell(hx - 10 * s * flip, hy - 26 * s, 20 * s, 8 * s, A(gl, a * 0.6))
    for sd in (-1, 1):   # antennae
        d.line([F_(104 + sd * 6, -146), F_(80 + sd * 30, -230 - 10 * math.sin(t * 2 + sd)), F_(60 + sd * 46, -250)], A(gd, a), 3 * s)
    # eyes
    for sd in (-1, 1):
        ex, ey = F_(112 + sd * 30, -142)
        if camo > 0.5 and eyes_open < 0.5:
            d.line([(ex - 9 * s, ey), (ex + 9 * s, ey)], A(gd, a), 4 * s); continue
        er = 21 * s * (1.25 if face in ("shock", "scared") else 1.0)
        d.circ(ex, ey, er, fill=A(WHITE, a)); d.circ(ex + (3 + look * 5) * s * flip, ey + 2 * s, er * 0.5, fill=A(NAVYT, a))
        d.circ(ex + (5 + look * 5) * s * flip, ey - 2 * s, er * 0.16, fill=A(WHITE, a))
    mx, my = F_(116, -112)
    if face in ("happy", "proud"): d.arc(mx, my - 6 * s, 12 * s, 9 * s, 20, 160, A(NAVYT, a), 3.5 * s)
    elif face in ("shock", "scared"): d.ell(mx, my, 6 * s, 8 * s, A(NAVYT, a))
    elif face == "smug":
        d.line([(mx - 10 * s, my - 2 * s), (mx + 10 * s * flip, my - 6 * s)], A(NAVYT, a), 3.5 * s)
    elif face == "sad": d.arc(mx, my + 6 * s, 10 * s, 7 * s, 200, 340, A(NAVYT, a), 3 * s)
    else: d.line([(mx - 8 * s, my), (mx + 8 * s, my)], A(NAVYT, a), 3 * s)
    if blush > 0:
        for sd in (-1, 1): d.ell(F_(112 + sd * 34, -120)[0], F_(0, -120)[1], 10 * s, 6 * s, A((255, 120, 140), 0.7 * blush * a))

def butt_point(x, y, s, wig=0.0, flip=1):
    sp = _seg_curve(x, y, s, wig, 0.0, flip); return sp[4]

def bird(d, x, y, s, t, a=1.0, face="sus", flip=1, flap=0.0, col=(240, 120, 90)):
    if a <= 0.01: return
    F_ = lambda px, py: (x + px * s * flip, y + py * s)
    d.ell(x, y, 80 * s, 62 * s, A(col, a)); d.ell(x + 10 * s * flip, y + 18 * s, 54 * s, 36 * s, A(mix(col, WHITE, 0.55), a))
    wa = math.sin(flap) * 0.9
    d.poly([F_(-20, -10), F_(-120, -40 - 70 * wa), F_(-60, 20)], A(mix(col, (0, 0, 0), 0.2), a))
    d.poly([F_(-70, 0), F_(-130, 20), F_(-80, 25)], A(mix(col, (0, 0, 0), 0.2), a))     # tail
    d.poly([F_(70, -10), F_(118, 4), F_(70, 14)], A(GOLD, a))
    ex, ey = F_(40, -24); d.circ(ex, ey, 16 * s, fill=A(WHITE, a)); d.circ(ex + 4 * s * flip, ey + 2 * s, 7 * s, fill=A(NAVYT, a))
    if face == "sus": d.line([F_(24, -46), F_(58, -38)], A(NAVYT, a), 4 * s)

def gnat(d, x, y, s, t, a=1.0, face="happy"):
    if a <= 0.01: return
    for sd in (-1, 1):
        d.ell(x + sd * 14 * s, y - 16 * s + 3 * s * math.sin(t * 60), 16 * s, 9 * s, A(WINGC, 0.6 * a))
    d.ell(x, y, 20 * s, 14 * s, A((90, 90, 110), a))
    d.circ(x + 14 * s, y - 4 * s, 6 * s, fill=A(WHITE, a)); d.circ(x + 15 * s, y - 4 * s, 3 * s, fill=A(NAVYT, a))

def amber_blob(d, x, y, rx, ry, a=1.0, t=0.0):
    if a <= 0.01: return
    glow(d, x, y, max(rx, ry) * 1.3, AMB_L, 0.5 * a)
    for i in range(10):
        k = i / 9
        d.ell(x - rx * 0.1 * k, y - ry * 0.12 * k, rx * (1 - 0.55 * k), ry * (1 - 0.55 * k), A(mix(AMB_D, AMB_L, k), 0.55 * a if i else a))
    d.ell(x - rx * 0.45, y - ry * 0.5, rx * 0.22, ry * 0.1, A(WHITE, 0.5 * a))
    d.circ(x + rx * 0.5, y - ry * 0.3, rx * 0.05, fill=A(WHITE, 0.6 * a))
    for i in range(6):   # bubbles
        rv = random.Random(i + 40)
        d.circ(x + rv.uniform(-0.6, 0.6) * rx, y + rv.uniform(-0.5, 0.6) * ry, rv.uniform(4, 12), fill=A((255, 240, 200), 0.5 * a))

def jungle(d, t, top=FOR1, bot=FOR2, deco=True):
    grad(d, top, bot)
    if deco:
        for i in range(9):
            x = (i * 151 + t * 10) % 1300 - 110; y = 250 + (i * 263) % 1300
            d.circ(x, y, 70 + (i * 41) % 90, fill=A((140, 255, 200), 0.03))

def amber_back(d, x, y, rx, ry, a=1.0):
    if a <= 0.01: return
    glow(d, x, y, max(rx, ry) * 1.3, AMB_L, 0.5 * a)
    d.ell(x, y, rx, ry, A(AMB_D, a)); d.ell(x - rx * 0.06, y - ry * 0.06, rx * 0.9, ry * 0.88, A(AMB, a))
    d.ell(x - rx * 0.12, y - ry * 0.12, rx * 0.65, ry * 0.6, A(mix(AMB, AMB_L, 0.5), a))
def amber_front(d, x, y, rx, ry, a=1.0):
    if a <= 0.01: return
    d.ell(x, y, rx, ry, A(AMB, 0.28 * a))
    d.ell(x - rx * 0.45, y - ry * 0.5, rx * 0.22, ry * 0.1, A(WHITE, 0.55 * a))
    d.circ(x + rx * 0.5, y - ry * 0.3, rx * 0.05, fill=A(WHITE, 0.6 * a))
    for i in range(6):
        rv = random.Random(i + 40)
        d.circ(x + rv.uniform(-0.6, 0.6) * rx, y + rv.uniform(-0.5, 0.6) * ry, rv.uniform(4, 12), fill=A((255, 240, 200), 0.5 * a))
