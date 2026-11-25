# Flat 2D characters/props for 《果冻蛙》 Rhacophorus kurniatiae (Trilaksono et al. 2026, Zootaxa 5900:349–370).
# Look (from the UC Davis release photos): bright green flying frog, pale pink legs, pointed snout, large webbed hands/feet
# with toe discs. Eggs + tadpoles develop inside an irregular transparent gel mass on vegetation over / near water;
# related species make white foam nests.
# No dark outlines: shapes separated by value, highlights and glow only. Eye/mouth lines may be dark.
import math, random
from gchars import _lid_partial
from gchars import *          # base + fx + easing E, glow_disc, tadpole, egg, mist, leaf_shape, colors ...

JG = (104, 204, 92); JG_D = (58, 146, 64); JG_L = (170, 236, 124); JG_H = (214, 250, 170)       # body / shade / light / hilite
JLEG = (240, 184, 176); JLEG_D = (214, 148, 144); JWEB = (250, 170, 120); JWEB_L = (255, 210, 160)
JBEL = (240, 242, 214)
JIR = (214, 168, 70); JIR_D = (150, 104, 40)
GEL = (180, 236, 230); GEL_L = (230, 255, 250); EGGC = (250, 244, 214); EMB = (60, 64, 58)
RELG = (126, 170, 104); RELG_D = (82, 120, 72)            # look-alike relative (duller green)
FOAMC = (250, 250, 246); FOAM_S = (214, 222, 226)
BRANCH = (110, 78, 56); BRANCH_L = (148, 108, 76); LEAFG = (52, 132, 76); LEAFG_L = (84, 168, 96)

def jeye(d, x, y, r, t, a=1.0, look=0.0, lid=0.0, pupil=1.0, col=JIR, lidcol=JG):
    if a <= 0.01: return
    d.circ(x, y, r, fill=A(JIR_D, a)); d.circ(x, y, r * 0.9, fill=A(col, a))
    for i in range(10):     # fine iris rays
        th = 2 * math.pi * i / 10
        d.line([(x + math.cos(th) * r * 0.45, y + math.sin(th) * r * 0.45), (x + math.cos(th + 0.12) * r * 0.82, y + math.sin(th + 0.12) * r * 0.82)], A(JIR_D, a * 0.45), max(1.2, r * 0.05))
    cx = x + look * r * 0.12
    d.ell(cx, y, r * 0.56 * pupil, r * 0.30 * pupil, A(PUP, a))
    d.circ(cx - r * 0.34, y - r * 0.36, r * 0.16, fill=A(WHITE, a * 0.95)); d.circ(cx + r * 0.3, y + r * 0.12, r * 0.07, fill=A(WHITE, a * 0.7))
    if lid > 0.01:
        from gchars import _lid_partial
        _lid_partial(d, x, y, r, lid, A(lidcol, a))

def web_hand(d, x, y, s, a, ang, n=4, L=46, spread=0.42, web=1.0, col=JLEG, wcol=JWEB, glow=0.0):
    """fingers fanned from (x,y) with webbing between them and round toe discs (flying-frog hand/foot)."""
    if a <= 0.01: return
    tips = []
    for j in range(n):
        th = ang + (j - (n - 1) / 2) * spread; l = L * s * (0.85 + 0.2 * (j in (n // 2, n // 2 - 1)))
        tips.append((x + math.cos(th) * l, y + math.sin(th) * l))
    if glow > 0: glow_disc(d, x + (tips[n // 2][0] - x) * 0.6, y + (tips[n // 2][1] - y) * 0.6, L * s * 1.1, JWEB_L, glow * a)
    if web > 0.01:
        pts = [(x, y)] + [(lerp(x, px, 0.92), lerp(y, py, 0.92)) for px, py in tips]
        d.poly(pts, A(wcol, a * 0.85 * web))
        for (x1, y1), (x2, y2) in zip(tips, tips[1:]):   # scalloped web edge
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2; d.ell(lerp(x, mx, 0.86), lerp(y, my, 0.86), 6 * s, 6 * s, A(wcol, a * 0.6 * web))
    for px, py in tips:
        d.line([(x, y), (px, py)], A(col, a), max(2, 7 * s)); d.circ(px, py, max(2.5, 8 * s), fill=A(JLEG_D, a)); d.circ(px - 1.5 * s, py - 1.5 * s, max(2, 6 * s), fill=A(col, a))

def jfrog(d, x, y, s, t, a=1.0, face="calm", look=0.0, blink=True, lid=None, squash=0.0, lift=0.0, seed=0.0,
          col=None, sac=0.0, mouth=0.0, web=1.0):
    """Front-view sitting flying frog; (x,y) = belly centre; ~300*s wide. sac 0..1 inflates the vocal sac (calling)."""
    if a <= 0.01: return
    body, dark, light = (JG, JG_D, JG_L) if col is None else col
    br = 1 + 0.02 * math.sin(t * 3.0 + seed)
    sy = (1 - squash) * br; sx = 1 + squash * 0.5
    P_ = lambda px, py: (x + px * s * sx, y + py * s * sy - lift * s)
    d.ell(x, y + 128 * s, 180 * s, 20 * s, A((0, 0, 0), 0.22 * a))
    for sd in (-1, 1):                                        # hind legs folded (pale pink) + big webbed feet
        cx, cy = P_(sd * 108, 72)
        d.ell(cx, cy + 4 * s, 58 * s, 44 * s, A(JLEG_D, a)); d.ell(cx, cy - 4 * s, 58 * s, 44 * s, A(JLEG, a))
        d.ell(cx + sd * 4 * s, cy - 22 * s, 30 * s, 10 * s, A(WHITE, a * 0.25))
        fx_, fy_ = P_(sd * 150, 124)
        web_hand(d, fx_, fy_, s, a, (0 if sd > 0 else math.pi) + sd * 0.2, 5, 60, 0.34, web)
    bx, by = P_(0, 20)                                        # body
    d.ell(bx, by + 6 * s, 110 * s * sx, 96 * s * sy, A(dark, a)); d.ell(bx, by - 4 * s, 110 * s * sx, 96 * s * sy, A(body, a))
    d.ell(bx - 34 * s, by - 50 * s, 46 * s, 18 * s, A(light, a * 0.7))
    ex_, ey_ = P_(0, 56); d.ell(ex_, ey_, 66 * s, 44 * s, A(JBEL, a))
    for sd in (-1, 1):                                        # front arms + webbed hands
        ax, ay = P_(sd * 54, 30); hx, hy = P_(sd * 78, 112)
        d.line([(ax, ay), (hx, hy)], A(JLEG_D, a), 22 * s); d.line([(ax - sd * 3 * s, ay), (hx - sd * 2 * s, hy - 4 * s)], A(JLEG, a), 15 * s)
        web_hand(d, hx, hy + 4 * s, s, a, math.pi / 2 + sd * 0.55, 4, 44, 0.42, web)
    # head: pointed snout (rounded triangle)
    hx, hy = P_(0, -78)
    head = [P_(-122, -40), P_(-118, -96), P_(-70, -128), P_(0, -148), P_(70, -128), P_(118, -96), P_(122, -40), P_(80, -12), P_(-80, -12)]
    d.poly([(px, py + 7 * s) for px, py in head], A(dark, a)); d.poly(head, A(body, a))
    d.ell(hx, hy - 40 * s, 60 * s, 12 * s, A(light, a * 0.6))
    d.circ(hx - 14 * s, hy - 58 * s, 4 * s, fill=A(dark, a)); d.circ(hx + 14 * s, hy - 58 * s, 4 * s, fill=A(dark, a))   # nostrils
    if sac > 0.01:                                            # vocal sac under the chin
        sx_, sy_ = P_(0, -8); d.ell(sx_, sy_ + 18 * s * sac, 64 * s * (0.4 + 0.6 * sac), 46 * s * sac + 4, A(mix(JBEL, (255, 255, 255), 0.3), a * 0.95))
        d.ell(sx_ - 18 * s, sy_ + 6 * s * sac, 18 * s * sac, 8 * s * sac + 1, A(WHITE, a * 0.6))
    mx, my = P_(0, -36)
    if mouth > 0.02:
        d.ell(mx, my + 10 * s * mouth, 80 * s, 26 * s * mouth + 4 * s, A((120, 40, 60), a)); d.ell(mx, my + 20 * s * mouth, 44 * s, 10 * s * mouth + 2 * s, A((255, 140, 150), a))
    elif face in ("happy", "proud"): d.arc(mx, my - 26 * s, 100 * s, 30 * s, 25, 155, A(INK, a), 6 * s)
    elif face in ("shock", "scared"): d.ell(mx, my + 4 * s, 22 * s, 16 * s, A((90, 20, 40), a))
    elif face == "sus": d.line([(mx - 64 * s, my), (mx + 64 * s, my - 8 * s)], A(INK, a), 6 * s)
    else: d.arc(mx, my - 18 * s, 90 * s, 22 * s, 30, 150, A(INK, a), 6 * s)
    if face in ("happy", "proud"):
        for sd in (-1, 1): d.ell(*P_(sd * 92, -46), 20 * s, 10 * s, A((255, 150, 150), a * 0.45))
    bl = blink_k(t, seed) if blink and face not in ("shock", "scared") else 0.0
    if lid is not None: bl = max(bl, lid)
    for sd in (-1, 1):                                        # big bulging eyes
        exx, eyy = P_(sd * 80, -116)
        d.circ(exx, eyy + 6 * s, 50 * s, fill=A(dark, a)); d.circ(exx, eyy - 2 * s, 50 * s, fill=A(body, a))
        rr_ = 40 * s * (1.12 if face in ("shock", "scared") else 1.0)
        jeye(d, exx, eyy, rr_, t, a, look, bl, 0.75 if face in ("shock", "scared") else 1.0, lidcol=body)
        if face == "sus": d.line([(exx - sd * 42 * s, eyy - 52 * s), (exx + sd * 34 * s, eyy - 40 * s)], A(INK, a), 6 * s)
        if face == "proud": _lid_partial(d, exx, eyy, rr_, 0.3, A(body, a))
    if face in ("shock", "scared"):
        q = P_(160, -180); d.ell(q[0], q[1], 10 * s, 16 * s, A(CYAN, a))

def jfrog_glide(d, x, y, s, t, a=1.0, ang=0.0, spread=1.0, glow=0.0, col=None):
    """Top-down gliding pose: limbs splayed, four big webbed 'parachutes'. head points along ang (0 = right)."""
    if a <= 0.01: return
    body, dark, light = (JG, JG_D, JG_L) if col is None else col
    ca, sa = math.cos(ang), math.sin(ang)
    Q = lambda px, py: (x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s)
    d.ell(x + 30 * s, y + 60 * s, 150 * s, 60 * s, A((0, 0, 0), 0.12 * a))
    for sd in (-1, 1):
        # hind legs (back) and front legs; spread 0..1 opens them
        k1, k2 = Q(-50, sd * 40), Q(lerp(-80, -120, spread), sd * lerp(70, 120, spread))
        d.line([k1, k2], A(JLEG, a), 26 * s)
        web_hand(d, k2[0], k2[1], s * lerp(0.8, 1.25, spread), a, ang + math.pi + sd * lerp(0.4, 0.9, spread), 5, 52, lerp(0.22, 0.38, spread), spread, glow=glow)
        a1, a2 = Q(40, sd * 34), Q(lerp(60, 90, spread), sd * lerp(70, 110, spread))
        d.line([a1, a2], A(JLEG, a), 18 * s)
        web_hand(d, a2[0], a2[1], s * lerp(0.8, 1.15, spread), a, ang + sd * lerp(0.7, 1.1, spread), 4, 44, lerp(0.24, 0.4, spread), spread, glow=glow)
    body_pts = [Q(95 * math.cos(2 * math.pi * i / 32) - 10, 62 * math.sin(2 * math.pi * i / 32)) for i in range(32)]
    d.poly([(px, py + 6 * s) for px, py in body_pts], A(dark, a)); d.poly(body_pts, A(body, a))
    d.poly([Q(60, -48), Q(128, 0), Q(60, 48)], A(body, a))   # pointed snout
    d.ell(*Q(-10, -26), 50 * s, 12 * s, A(light, a * 0.7))
    for sd in (-1, 1):
        c = Q(66, sd * 38); d.circ(c[0], c[1], 22 * s, fill=A(dark, a)); jeye(d, c[0], c[1], 17 * s, t, a, 0.0, 0.0)

def jelly_pts(x, y, r, t, seed=0, wob=1.0, drip=0.25):
    rr = random.Random(seed); ph = [rr.uniform(0, 6.28) for _ in range(4)]; amp = [rr.uniform(0.05, 0.11) for _ in range(4)]
    pts = []
    for i in range(48):
        th = 2 * math.pi * i / 48
        k = 1 + sum(amp[j] * math.sin((j + 2) * th + ph[j] + wob * 0.6 * math.sin(t * (1.3 + 0.4 * j) + j)) for j in range(4))
        k += drip * max(0, math.sin(th)) ** 6          # sags downward (hanging)
        pts.append((x + math.cos(th) * r * k, y + math.sin(th) * r * k * 1.05))
    return pts

def jelly(d, x, y, r, t, a=1.0, n=14, stage=0.0, seed=3, wob=1.0, glow=0.0, eggs_a=1.0, wiggle=1.0):
    """irregular transparent gel mass. stage 0 = eggs, 0.5 = curled embryos, 1 = tadpoles swimming inside the gel."""
    if a <= 0.01 or r < 2: return
    if glow > 0: glow_disc(d, x, y, r * 1.5, GEL_L, glow * a)
    pts = jelly_pts(x, y, r, t, seed, wob)
    d.poly(pts, A(GEL, 0.5 * a))
    d.poly(jelly_pts(x - r * 0.04, y - r * 0.05, r * 0.86, t, seed, wob), A(GEL_L, 0.18 * a))
    rr = random.Random(seed + 7)
    for i in range(n):
        ang = rr.uniform(0, 6.28); rad = r * 0.72 * math.sqrt(rr.uniform(0.02, 1)); ex, ey = x + math.cos(ang) * rad, y + math.sin(ang) * rad * 1.02
        er = r * rr.uniform(0.09, 0.12)
        eggk = cl(1 - (stage - 0.55) / 0.3)                 # egg capsule fades as tadpoles hatch
        if eggk > 0.01:
            d.circ(ex, ey, er, fill=A(EGGC, a * 0.75 * eggs_a * eggk))
            if stage < 0.25: d.circ(ex, ey, er * 0.45, fill=A(EMB, a * eggs_a * eggk))
        if 0.15 < stage < 0.85:                              # curled embryo grows
            k = cl((stage - 0.15) / 0.4); ek = cl((0.85 - stage) / 0.15)
            d.arc(ex, ey, er * (0.4 + 0.3 * k), er * (0.4 + 0.3 * k), 30, 30 + 300 * k, A(EMB, a * eggs_a * ek), max(2, er * 0.35))
        if stage > 0.55:                                     # tadpoles wriggle inside the gel
            k = cl((stage - 0.55) / 0.3); ph = rr.uniform(0, 6.28)
            tx = ex + 0.08 * r * math.sin(t * 0.9 * wiggle + ph) * k; ty = ey + 0.06 * r * math.cos(t * 0.7 * wiggle + ph) * k
            sc = er / 60 * 1.05
            tadpole_dir(d, tx, ty, sc, t * wiggle + ph, a * k * eggs_a, ph)
    d.ell(x - r * 0.42, y - r * 0.48, r * 0.24, r * 0.1, A(WHITE, 0.75 * a)); d.circ(x + r * 0.45, y - r * 0.3, r * 0.05, fill=A(WHITE, 0.6 * a))

def tadpole_dir(d, x, y, s, t, a=1.0, ang=0.0, col=(54, 60, 56)):
    if a <= 0.01: return
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    for i in range(12):
        u = i / 11; px, py = 34 * s + u * 100 * s, math.sin(t * 9 - u * 5) * 13 * s * u
        pts.append((x + px * ca - py * sa, y + px * sa + py * ca))
    d.line(pts, A(col, a), max(2, 12 * s))
    d.ell(x, y, 44 * s, 34 * s, A(col, a))
    ex, ey = x - 16 * s * ca + 10 * s * sa, y - 16 * s * sa - 10 * s * ca
    d.circ(ex, ey, max(1.5, 7 * s), fill=A(WHITE, a)); d.circ(ex, ey, max(1, 3.5 * s), fill=A(INK, a))

def foam(d, x, y, r, t, a=1.0, n=60, seed=5, eggs=0, grow=1.0):
    """white foam nest: many bubbles; each bubble shimmers (alpha), none pops in."""
    if a <= 0.01: return
    rr = random.Random(seed)
    d.ell(x, y + r * 0.1, r * 1.05 * grow, r * 0.85 * grow, A(FOAM_S, 0.9 * a))
    for i in range(n):
        ang = rr.uniform(0, 6.28); rad = r * math.sqrt(rr.uniform(0, 1)) * grow; bx, by = x + math.cos(ang) * rad, y + math.sin(ang) * rad * 0.8
        br = r * rr.uniform(0.08, 0.2) * grow * (1 + 0.06 * math.sin(t * 3 + i))
        d.circ(bx, by, br, fill=A(FOAMC, a * 0.95)); d.circ(bx - br * 0.35, by - br * 0.35, br * 0.25, fill=A((210, 236, 255), a * 0.9))
    for i in range(eggs):
        ang = rr.uniform(0, 6.28); rad = r * 0.5 * math.sqrt(rr.uniform(0, 1)); ex, ey = x + math.cos(ang) * rad, y + math.sin(ang) * rad * 0.8
        d.circ(ex, ey, r * 0.08, fill=A((246, 226, 160), a * 0.9)); d.circ(ex, ey, r * 0.035, fill=A(EMB, a * 0.8))

def branch(d, x0, y0, x1, y1, w=26, a=1.0, t=0.0, leaves=4, seed=1):
    d.line([(x0, y0 + 4), (x1, y1 + 4)], A(mix(BRANCH, (0, 0, 0), 0.3), a), w); d.line([(x0, y0), (x1, y1)], A(BRANCH, a), w)
    d.line([(x0, y0 - w * 0.25), (x1, y1 - w * 0.25)], A(BRANCH_L, a * 0.6), max(2, w * 0.2))
    rr = random.Random(seed)
    for i in range(leaves):
        u = rr.uniform(0.1, 0.95); lx, ly = lerp(x0, x1, u), lerp(y0, y1, u)
        ang = rr.choice((-1, 1)) * rr.uniform(0.6, 1.3) + 0.08 * math.sin(t * 1.3 + i)
        leaf_shape(d, lx + math.cos(ang - 1.57) * 10, ly, rr.uniform(110, 160), ang - 1.57, LEAFG if i % 2 else LEAFG_L, a)

def kid_face(d, x, y, s, t, a=1.0, look=0.0, face="smile"):
    """friendly flat cartoon kid head (front view) — big clear face for the size comparison."""
    if a <= 0.01: return
    SK = (250, 214, 186); SK_D = (226, 180, 150); HAIR = (60, 44, 40)
    d.circ(x, y + 330 * s, 120 * s, fill=A(SK_D, a))                             # neck
    d.rect(x - 240 * s, y + 360 * s, x + 240 * s, y + 620 * s, fill=A((90, 150, 230), a), r=120 * s)   # shirt
    for sd in (-1, 1): d.ell(x + sd * 262 * s, y + 20 * s, 44 * s, 64 * s, A(SK_D, a))    # ears
    d.ell(x, y + 8 * s, 262 * s, 300 * s, A(SK_D, a)); d.ell(x, y, 262 * s, 300 * s, A(SK, a))
    d.ell(x, y - 230 * s, 250 * s, 110 * s, A(HAIR, a)); d.ell(x - 120 * s, y - 180 * s, 140 * s, 80 * s, A(HAIR, a)); d.ell(x + 140 * s, y - 170 * s, 120 * s, 70 * s, A(HAIR, a))
    bl = blink_k(t, 0.7, 3.3)
    for sd in (-1, 1):
        ex, ey = x + sd * 96 * s, y - 20 * s
        d.ell(ex, ey, 30 * s, 38 * s * (1 - 0.9 * bl) + 1, A(WHITE, a)); d.circ(ex + look * 10 * s, ey + 4 * s, 18 * s * (1 - 0.9 * bl) + 0.5, fill=A((50, 36, 30), a))
        d.circ(ex + look * 10 * s - 6 * s, ey - 4 * s, 6 * s * (1 - bl) + 0.5, fill=A(WHITE, a))
        d.line([(ex - 34 * s, ey - 62 * s), (ex + 30 * s, ey - 70 * s)], A(HAIR, a), 9 * s)
        d.ell(x + sd * 150 * s, y + 90 * s, 46 * s, 24 * s, A((255, 150, 150), a * 0.45))  # blush
    d.ell(x, y + 50 * s, 16 * s, 12 * s, A(SK_D, a))
    if face == "wow": d.ell(x, y + 150 * s, 40 * s, 34 * s, A((150, 50, 60), a))
    else: d.arc(x, y + 110 * s, 70 * s, 44 * s, 20, 160, A((150, 50, 60), a), 9 * s)

def pond(d, y0, t, a=1.0, col=(34, 74, 92), col2=(70, 130, 150)):
    d.rect(-60, y0, 1140, 1980, fill=A(col, a))
    for i in range(9):
        xx = (i * 150 + t * 30) % 1300 - 100; yy = y0 + 30 + (i % 4) * 46
        d.line([(xx, yy), (xx + 90, yy)], A(col2, 0.5 * a), 4)
