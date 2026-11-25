# York film — extra characters (2026-11-16 pass): side-view York (prone / standing / kneeling hunter), steel Brodie helmet,
# shouting mouth, German officer cap, marching column walkers, irregular sandbags. Rim light & value contrast, NO dark outlines.
from chars import *

STEEL = (78, 88, 80); STEEL_HI = (176, 188, 176); STEEL_MID = (112, 124, 114); STEEL_UND = (22, 26, 24)

def ellpts(cx, cy, rx, ry, a0=0.0, a1=2 * math.pi, n=28, rot=0.0):
    c, s_ = math.cos(rot), math.sin(rot); out = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n; x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s_, cy + x * s_ + y * c))
    return out

class Map:
    """local (units of h, origin = anchor) -> world, with rotation `rot` about local pivot `piv`."""
    def __init__(s, x, y, h, rot=0.0, piv=(0.0, 0.0), flip=1):
        s.x, s.y, s.h, s.rot, s.piv, s.f = x, y, h, rot, piv, flip; s.c, s.s = math.cos(rot), math.sin(rot)
    def __call__(s, pts):
        out = []
        for px, py in pts:
            px *= s.f; dx, dy = px - s.piv[0] * s.f, py - s.piv[1]
            rx, ry = dx * s.c - dy * s.s * s.f, dx * s.s * s.f + dy * s.c
            out.append((s.x + (rx + s.piv[0] * s.f) * s.h, s.y + (ry + s.piv[1]) * s.h))
        return out
    def p(s, x, y): return s([(x, y)])[0]

# ---------------------------------------------------------------- steel Brodie (clearly STEEL, not straw)
def brodie_side(d, m, cx, cy, w, rim=AMBER_L, a=1.0, tilt=0.0):
    """side / 3-4 view, local units through Map m. Wide flat brim (thin), very shallow dome; crisp cool highlights."""
    rimc = mix(STEEL_HI, rim, 0.35)
    d.poly(m(ellpts(cx, cy + 0.02 * w, 0.5 * w, 0.075 * w, 0, math.pi, 16, tilt)), A(STEEL_UND, a))          # brim underside (dark)
    d.poly(m(ellpts(cx, cy, 0.5 * w, 0.06 * w, 0, 2 * math.pi, 28, tilt)), A(STEEL_MID, a))                 # brim top plane
    d.poly(m(ellpts(cx, cy - 0.006 * w, 0.5 * w, 0.03 * w, math.pi, 2 * math.pi, 16, tilt)), A(rimc, a))       # rolled lip catching light
    dome = ellpts(cx, cy - 0.01 * w, 0.31 * w, 0.2 * w, math.pi, 2 * math.pi, 18, tilt)
    d.poly(m(dome), A(STEEL, a))
    d.poly(m(ellpts(cx - 0.03 * w, cy - 0.06 * w, 0.22 * w, 0.12 * w, math.pi * 1.1, math.pi * 1.75, 10, tilt) + [(cx - 0.02 * w, cy - 0.1 * w)]), A(STEEL_HI, 0.85 * a))  # specular
    d.poly(m(ellpts(cx, cy - 0.01 * w, 0.31 * w, 0.035 * w, 0, math.pi, 10, tilt)), A((40, 46, 42), a))      # band shadow where dome meets brim

def brodie_back2(d, x, y, h, t, rim=AMBER, a=1.0, seed=0, duck=0.0):
    """US soldier ducking behind cover, seen from behind: steel dish helmet with clear light/dark separation."""
    y = y + duck * 0.3 * h + math.sin(t * 2 + seed) * 0.01 * h
    sh = spline([(-0.2, 0.2), (-0.8, 0.45), (-1.0, 1.2), (1.0, 1.2), (0.8, 0.45), (0.2, 0.2)], n=5)
    rimpoly(d, xf(sh, x, y, h), (40, 40, 28), mix(OD_L, rim, 0.6), 0, 0.03 * h, a)
    d.ell(x, y - 0.03 * h, 0.27 * h, 0.3 * h, fill=A((52, 36, 28), a))                           # back of head / neck
    m = Map(x, y - 0.2 * h, h)
    brodie_side(d, m, 0, 0, 1.45, rim, a, tilt=0.03 * math.sin(seed * 2.1))

# ---------------------------------------------------------------- side head (faces RIGHT), clear features
HEAD_S = spline([(-0.30, -0.05), (-0.25, -0.36), (0.02, -0.47), (0.25, -0.35), (0.32, -0.14), (0.35, -0.05), (0.45, 0.07), (0.36, 0.12),
                 (0.37, 0.2), (0.34, 0.27), (0.31, 0.37), (0.14, 0.45), (-0.08, 0.42), (-0.26, 0.22)], n=5)
def head_side(d, m, key=AMBER, rim=COLD, a=1.0, hat="brodie", mouth=0.0, squint=0.4, look_down=0.0):
    hp = m(HEAD_S)
    d.poly(hp, A(mix(SKIN, key, 0.25), a))                                    # rim (lit front edge)
    d.poly([(x - 0.03 * m.h * m.f, y + 0.01 * m.h) for x, y in hp], A(mix(SKIN_M, SKIN, 0.35), a))   # body of face
    d.poly(m(spline([(-0.3, -0.05), (-0.22, -0.3), (0.0, -0.34), (-0.05, 0.1), (-0.12, 0.35), (-0.26, 0.22)], n=4)), A(mix(SKIN_D, (40, 30, 30), 0.2), a))  # back-of-head shade
    d.poly(m(spline([(-0.27, -0.2), (-0.12, -0.33), (0.05, -0.35), (-0.04, -0.14), (-0.2, -0.04)], n=4)), A(mix(HAIR, (40, 20, 14), 0.5), a))  # hair
    ex, ey = m.p(-0.06, 0.03); d.ell(ex, ey, 0.065 * m.h, 0.1 * m.h, fill=A(SKIN_M, a)); d.ell(ex, ey, 0.03 * m.h, 0.06 * m.h, fill=A(SKIN_D, a))  # ear
    d.poly(m(spline([(0.08, 0.1), (0.2, 0.06), (0.26, 0.2), (0.12, 0.3)], n=4)), A(SKIN_D, 0.25 * a))                 # cheek shade
    # eye
    eo = 0.032 * (1 - squint) + 0.006
    ex, ey = m.p(0.22, -0.07 + 0.02 * look_down)
    d.ell(ex, ey, 0.055 * m.h, eo * m.h, fill=A((226, 218, 204), a))
    if eo > 0.012: d.circ(ex + 0.022 * m.h * m.f, ey + 0.004 * m.h, min(eo, 0.03) * m.h, fill=A((40, 60, 70), a))
    d.line([m.p(0.16, -0.075 - eo), m.p(0.28, -0.07 - eo * 0.8)], A((44, 24, 18), a), 0.02 * m.h)            # lid
    d.poly(m([(0.12, -0.15), (0.31, -0.14), (0.31, -0.11), (0.13, -0.11)]), A(mix(HAIR, (50, 22, 14), 0.5), a))  # brow (heavy)
    d.circ(*m.p(0.41, 0.065), 0.012 * m.h, fill=A((255, 228, 196), 0.7 * a))                                     # nose highlight
    d.poly(m(spline([(0.24, 0.165), (0.37, 0.14), (0.36, 0.2), (0.27, 0.215)], n=4)), A(mix(HAIR, (70, 30, 18), 0.25), a))   # mustache
    if mouth > 0.05:
        d.poly(m(ellpts(0.31, 0.27, 0.06, 0.035 + 0.07 * mouth, 0, 2 * math.pi, 16)), A((60, 20, 20), a))
        d.poly(m(ellpts(0.31, 0.245, 0.05, 0.018, 0, math.pi, 8)), A((230, 220, 206), a))
    else:
        d.line([m.p(0.24, 0.27), m.p(0.33, 0.265)], A((80, 34, 28), a), 0.018 * m.h)
    if hat == "brodie": brodie_side(d, m, 0.03, -0.3, 1.25, key, a, tilt=-0.05)
    elif hat == "farm":
        d.poly(m(spline([(-0.3, -0.27), (-0.22, -0.62), (0.18, -0.66), (0.3, -0.3)], n=5)), A((84, 60, 38), a))
        d.poly(m(ellpts(0.02, -0.28, 0.56, 0.07)), A(mix((96, 70, 44), key, 0.4), a))
        d.poly(m(ellpts(0.02, -0.26, 0.54, 0.05, 0, math.pi, 12)), A((40, 28, 20), a))

# ---------------------------------------------------------------- York PRONE, side view (unmistakably lying on the ground)
def york_prone_side(img, d, x, y, h, t, rot=0.0, key=AMBER, rim=COLD, a=1.0, mouth=0.0, flash=0.0, dust=0.0, recoil=0.0):
    """(x,y) = head centre, h = head height; faces RIGHT. Body lies flat along y+0.62h (the ground).
    rot rotates the whole figure about the feet (for the 'drop' animation)."""
    m = Map(x - recoil * 0.05 * h, y, h, rot, piv=(-4.6, 0.55))
    uni, uni_d, uni_l = (70, 66, 42), (48, 46, 30), mix(OD_L, key, 0.55)
    def part(pts, c=uni, lit=uni_l, dy=0.03):
        pp = m(pts); d.poly(pp, A(lit, a)); d.poly([(px, py + dy * h) for px, py in pp], A(c, a))
    # far leg + far arm (darker)
    part(spline([(-2.5, 0.28), (-3.5, 0.38), (-4.45, 0.36), (-4.5, 0.55), (-3.5, 0.6), (-2.5, 0.6)], n=4), uni_d, mix(uni_d, key, 0.3))
    d.poly(m([(-4.45, 0.3), (-4.75, 0.28), (-4.78, 0.52), (-4.45, 0.56)]), A((44, 32, 24), a))
    d.line(m([(-0.4, 0.3), (0.25, 0.56), (0.95, 0.36)]), A(uni_d, a), 0.24 * h)
    # torso, hips, near leg (bent knee), boots
    part(spline([(-0.35, 0.02), (-1.2, -0.14), (-2.0, -0.04), (-2.7, 0.14), (-2.8, 0.45), (-2.5, 0.62), (-1.0, 0.64), (-0.25, 0.62), (-0.05, 0.42)], n=4))
    part(spline([(-1.0, -0.14), (-1.75, -0.24), (-1.95, -0.06), (-1.1, -0.02)], n=3), (60, 58, 38), mix((90, 86, 56), key, 0.4), 0.02)   # haversack
    part(spline([(-2.6, 0.3), (-3.3, 0.3), (-3.75, 0.18), (-3.95, 0.3), (-4.2, 0.46), (-4.25, 0.62), (-3.6, 0.62), (-2.6, 0.62)], n=4))
    d.poly(m([(-4.2, 0.36), (-4.55, 0.33), (-4.6, 0.6), (-4.2, 0.62)]), A((56, 40, 28), a)); d.poly(m([(-4.55, 0.33), (-4.62, 0.33), (-4.66, 0.6), (-4.6, 0.6)]), A(mix((90, 66, 44), key, 0.5), a))
    # rifle: stock in the shoulder, barrel forward, nearly level
    d.poly(m([(-0.75, 0.38), (0.35, 0.24), (0.38, 0.36), (-0.7, 0.55)]), A((92, 58, 32), a))
    d.poly(m([(-0.75, 0.38), (0.35, 0.24), (0.36, 0.27), (-0.74, 0.42)]), A(mix((150, 100, 56), key, 0.4), a))
    d.line(m([(0.3, 0.27), (1.55, 0.2)]), A((96, 62, 34), a), 0.1 * h)
    d.line(m([(0.3, 0.22), (2.75, 0.1)]), A((60, 64, 66), a), 0.05 * h); d.line(m([(0.3, 0.205), (2.75, 0.085)]), A(mix((150, 150, 150), key, 0.5), a), 0.016 * h)
    d.line(m([(2.62, 0.1), (2.64, 0.04)]), A((70, 74, 76), a), 0.03 * h)
    # near arm: elbow planted in the dirt, hand under the fore-end
    d.line(m([(-0.45, 0.4), (0.15, 0.6)]), A(uni, a), 0.27 * h); d.line(m([(-0.45, 0.37), (0.15, 0.57)]), A(uni_l, 0.55 * a), 0.08 * h)
    d.line(m([(0.15, 0.6), (0.95, 0.3)]), A(uni, a), 0.22 * h); d.line(m([(0.15, 0.56), (0.95, 0.26)]), A(uni_l, 0.55 * a), 0.06 * h)
    d.poly(m(ellpts(1.0, 0.3, 0.12, 0.09)), A(mix(SKIN_M, key, 0.2), a))
    # elbow pressed into ground: a dirt mound
    d.poly(m(ellpts(0.18, 0.66, 0.3, 0.06, math.pi, 2 * math.pi, 10)), A((70, 56, 40), a))
    # head (cheek welded to the stock, slightly down)
    hm = Map(*m.p(0.0, 0.0), h, rot + 0.1, piv=(0, 0))
    head_side(d, hm, key, rim, a, "brodie", mouth=mouth, squint=0.5)
    if dust > 0.01:
        for i in range(22):
            u = dust; px, py = m.p(-4.4 + i * 0.27 + hsh(i, 41) * 0.2, 0.62)
            d.ell(px + (hsh(i, 42) - 0.5) * 120 * (1 - u), py - 50 * (1 - u) * (0.3 + hsh(i, 43)) - 6, (10 + 18 * hsh(i, 44)) * (1.8 - u) * h / 170, (6 + 9 * hsh(i, 45)) * h / 170, fill=A((140, 116, 86), 0.4 * u * a))
    if flash > 0.01:
        mx, my = m.p(2.8, 0.09); glow(img, lambda g: g.circ(mx, my, 50 * (1 + flash) * h / 170, fill=A(AMBER_L, flash)), blur=30)
    return m

def york_stand_side(d, x, yf, h, t, key=AMBER, a=1.0, sway=0.0):
    """Standing profile facing right, rifle at the ready. (x, yf) = feet; h = head height (body ~6.2 h)."""
    hy = yf - 5.6 * h; m = Map(x + sway * h, hy, h)
    uni, uni_l = (70, 66, 42), mix(OD_L, key, 0.55)
    for c, dx in ((uni_l, 0.04), (uni, 0)):
        d.poly(m(spline([(-0.25, 0.42), (0.25, 0.45), (0.35, 1.5), (0.3, 2.7), (-0.35, 2.7), (-0.4, 1.4)], n=4)), A(c, a)) if dx == 0 else d.poly([(px + dx * h, py) for px, py in m(spline([(-0.25, 0.42), (0.25, 0.45), (0.35, 1.5), (0.3, 2.7), (-0.35, 2.7), (-0.4, 1.4)], n=4))], A(c, a))
    for lx in (-0.18, 0.12):
        d.line(m([(lx, 2.6), (lx + 0.05, 4.0), (lx, 5.3)]), A((60, 56, 36), a), 0.3 * h)
        d.poly(m([(lx - 0.15, 5.2), (lx + 0.3, 5.2), (lx + 0.32, 5.62), (lx - 0.17, 5.62)]), A((50, 36, 26), a))
    d.line(m([(-0.6, 1.9), (1.6, 0.7)]), A((92, 58, 32), a), 0.12 * h); d.line(m([(0.9, 1.08), (2.3, 0.3)]), A((64, 68, 70), a), 0.05 * h)
    d.line(m([(0.0, 0.6), (0.35, 1.5), (1.0, 1.15)]), A(uni, a), 0.22 * h)
    d.poly(m(ellpts(1.0, 1.15, 0.13, 0.1)), A(mix(SKIN_M, key, 0.2), a))
    head_side(d, m, key, COLD, a, "brodie", squint=0.3)
    return m

def hunter_side(img, d, x, y, h, t, key=AMBER, a=1.0, flash=0.0, recoil=0.0):
    """Young York kneeling in the woods (farm hat), rifle level, facing right. (x,y) = head centre."""
    m = Map(x - recoil * 0.05 * h, y, h)
    shirt, shirt_l = (110, 52, 40), mix((170, 90, 60), key, 0.4)
    d.poly(m(spline([(-0.2, 0.4), (-0.75, 0.6), (-0.95, 1.5), (-0.9, 2.4), (0.3, 2.4), (0.4, 1.3), (0.25, 0.5)], n=5)), A(shirt_l, a))
    d.poly([(px - 0.04 * h, py + 0.02 * h) for px, py in m(spline([(-0.2, 0.4), (-0.75, 0.6), (-0.95, 1.5), (-0.9, 2.4), (0.3, 2.4), (0.4, 1.3), (0.25, 0.5)], n=5))], A(shirt, a))
    d.poly(m([(-0.5, 0.65), (-0.35, 0.62), (-0.35, 2.4), (-0.5, 2.4)]), A((60, 44, 34), a))              # suspender
    d.poly(m([(-0.75, 0.38), (0.35, 0.24), (0.38, 0.36), (-0.7, 0.55)]), A((92, 58, 32), a))
    d.line(m([(0.3, 0.27), (1.55, 0.2)]), A((96, 62, 34), a), 0.1 * h)
    d.line(m([(0.3, 0.22), (2.9, 0.1)]), A((60, 64, 66), a), 0.05 * h); d.line(m([(0.3, 0.205), (2.9, 0.085)]), A(mix((150, 150, 150), key, 0.5), a), 0.016 * h)
    d.line(m([(-0.2, 0.7), (0.4, 1.25), (1.0, 0.3)]), A(shirt, a), 0.22 * h)
    d.poly(m(ellpts(1.0, 0.3, 0.12, 0.09)), A(mix(SKIN_M, key, 0.2), a))
    hm = Map(x - recoil * 0.05 * h, y, h, 0.08); head_side(d, hm, key, COLD, a, "farm", squint=0.5)
    if flash > 0.01:
        mx, my = m.p(2.95, 0.09); glow(img, lambda g: g.circ(mx, my, 50 * (1 + flash) * h / 170, fill=A(AMBER_L, flash)), blur=30)
    return m

# ---------------------------------------------------------------- German officer: peaked cap instead of Stahlhelm
def officer(d, x, y, sc, t, hands=0.0, face=0.9, rim=AMBER, rdx=-1, fear=0.5, talk=0.0, a=1.0):
    h = sc
    german(d, x, y, sc, t, hands=hands, face=face, rim=rim, rdx=rdx, fear=fear, seed=7, a=a, body=(74, 80, 76), helm=None)
    fx, fy = x, y - 0.42 * h + math.sin(t * 2.1 + 7) * 0.01 * h
    if talk > 0: d.ell(fx, fy + 0.12 * h, 0.06 * h, 0.03 * h + 0.03 * h * talk, fill=A(INK, a))
    # peaked cap: crown (wide top), band, dark visor
    cr = spline([(-0.38, -0.28), (-0.5, -0.46), (-0.2, -0.56), (0.25, -0.56), (0.52, -0.46), (0.38, -0.28)], n=5)
    d.poly(xf(cr, fx, fy, h), A(mix((86, 92, 86), rim, 0.45), a)); d.poly(xf(cr, fx + 0.02 * h, fy + 0.02 * h, h), A((80, 86, 80), a))
    d.rect(fx - 0.37 * h, fy - 0.33 * h, fx + 0.37 * h, fy - 0.24 * h, fill=A((150, 50, 40), a))                 # red band
    d.circ(fx, fy - 0.29 * h, 0.035 * h, fill=A((210, 190, 140), a))                                           # cockade
    d.poly(xf(spline([(-0.34, -0.25), (0.34, -0.25), (0.24, -0.15), (-0.24, -0.15)], n=3), fx, fy, h), A((26, 28, 26), a))   # visor
    d.poly(xf([(-0.3, -0.25), (0.3, -0.25), (0.26, -0.22), (-0.26, -0.22)], fx, fy, h), A(mix((90, 94, 90), rim, 0.5), 0.8 * a))  # visor sheen
    for sgn in (-1, 1):                                                                                     # shoulder boards
        d.rect(x + sgn * 0.62 * h - 0.14 * h, y + 0.22 * h, x + sgn * 0.62 * h + 0.14 * h, y + 0.32 * h, fill=A((190, 180, 150), a), r=0.03 * h)

# ---------------------------------------------------------------- column walkers (side view, walking RIGHT)
def walker(d, x, y, h, t, ph, kind="ger", key=AMBER, a=1.0):
    """(x,y) = feet on ground, h = head size. kind 'ger' = prisoner, hands on head; 'us' = escort with rifle."""
    s = math.sin(t * 7.0 + ph); bob = abs(math.cos(t * 7.0 + ph)) * 0.08 * h
    hy = y - 5.4 * h - bob; body = (66, 74, 72) if kind == "ger" else (70, 66, 42); lit = mix(body, key, 0.45)
    for sg in (-1, 1):                                           # legs (swing)
        fxp = x + sg * s * 0.9 * h
        d.line([(x, y - 2.8 * h - bob), (lerp(x, fxp, 0.6) + 0.15 * h, y - 1.4 * h), (fxp, y)], A(mix(body, (0, 0, 0), 0.2 if sg < 0 else 0), a), 0.42 * h)
        d.ell(fxp + 0.15 * h, y - 0.08 * h, 0.32 * h, 0.12 * h, fill=A((40, 30, 24), a))
    tor = [(x - 0.5 * h, hy + 0.7 * h), (x + 0.5 * h, hy + 0.7 * h), (x + 0.55 * h, y - 2.7 * h - bob), (x - 0.55 * h, y - 2.7 * h - bob)]
    d.poly(tor, A(lit, a)); d.poly([(px - 0.08 * h, py + 0.04 * h) for px, py in tor], A(body, a))
    if kind == "ger":                                           # elbows out, hands on helmet
        for sg in (-1, 1):
            d.line([(x + sg * 0.2 * h, hy + 0.9 * h), (x + sg * 0.95 * h, hy - 0.1 * h), (x + sg * 0.25 * h, hy - 0.55 * h)], A(body, a), 0.32 * h)
    else:
        d.line([(x - 0.6 * h, hy + 2.6 * h), (x + 1.4 * h, hy + 0.3 * h)], A((92, 58, 32), a), 0.18 * h)
        d.line([(x + 0.2 * h, hy + 1.0 * h), (x + 0.5 * h, hy + 1.9 * h), (x + 0.9 * h, hy + 0.9 * h)], A(body, a), 0.3 * h)
    d.ell(x + 0.1 * h, hy + 0.05 * h, 0.42 * h, 0.5 * h, fill=A(mix(SKIN_M, key, 0.15), a))
    d.ell(x + 0.18 * h, hy + 0.05 * h, 0.36 * h, 0.46 * h, fill=A(SKIN_M, a))
    d.circ(x + 0.35 * h, hy - 0.02 * h, 0.06 * h, fill=A(INK, a))
    if kind == "ger":
        hp = xf(STAHL, x + 0.05 * h, hy - 0.35 * h, h * 1.15); d.poly(hp, A(mix(HELM, key, 0.5), a)); d.poly([(px - 0.05 * h, py + 0.05 * h) for px, py in hp], A(HELM, a))
        if kind == "ger": d.circ(x + 0.25 * h, hy - 0.5 * h, 0.16 * h, fill=A(mix(SKIN_M, key, 0.2), a))     # hand on top
    else:
        brodie_side(d, Map(x + 0.05 * h, hy - 0.35 * h, h), 0, 0, 1.3, key, a)

# ---------------------------------------------------------------- irregular sandbag heap
def sandbags2(d, y, col, rim, seed=3, a=1.0, rows=3, x0=-140, x1=1220):
    """Jumbled pile: bags of varied size, tilt, slump and tone; uneven top contour, some gaps and toppled bags."""
    r = random.Random(seed)
    for row in range(rows):
        yy0 = y + row * 50 - (rows - 1 - row) * 0
        x = x0 + r.uniform(0, 110)
        while x < x1:
            w_ = r.uniform(130, 250); hh = r.uniform(40, 66)
            if row == 0 and r.random() < 0.18: x += r.uniform(60, 140); continue        # gap on top row (uneven skyline)
            yy = yy0 + r.uniform(-14, 14) - (r.uniform(8, 26) if row == 0 and r.random() < 0.3 else 0)
            tilt = r.uniform(-0.16, 0.16)
            bp = [(-0.5, 0.1), (-0.47, -0.3), (-0.22, -0.5), (0.18, -0.48), (0.46, -0.3), (0.5, 0.12), (0.3, 0.45), (-0.3, 0.44)]
            bp = [(px + r.uniform(-0.05, 0.05), py + r.uniform(-0.08, 0.08)) for px, py in bp]
            pts = spline(bp, n=4)
            c = mix(mix(col, (0, 0, 0), row * 0.08 + r.uniform(0, 0.16)), (90, 80, 60), r.uniform(0, 0.25))
            ct, st_ = math.cos(tilt), math.sin(tilt)
            pp = [(x + (px * ct - py * st_) * w_, yy + (px * st_ + py * ct) * hh) for px, py in pts]
            d.poly(pp, A(mix(c, rim, 0.32), a)); d.poly([(px + 2, py + 5) for px, py in pp], A(c, a))
            d.line([(x - w_ * 0.38 * ct, yy - w_ * 0.38 * st_ + 2), (x - w_ * 0.45 * ct, yy - w_ * 0.45 * st_ - hh * 0.25)], A(mix(c, (0, 0, 0), 0.3), a), 4)  # tie fold
            d.line([(x - w_ * 0.1, yy + hh * 0.1), (x + w_ * 0.15, yy + hh * 0.05)], A(mix(c, (0, 0, 0), 0.18), 0.6 * a), 3)  # crease
            x += w_ * r.uniform(0.72, 0.95)

# shouting front face: open mouth drawn over york_face
def mouth_open(d, cx, cy, h, k, a=1.0):
    if k <= 0.02: return
    d.ell(cx + 0.01 * h, cy + 0.33 * h, 0.1 * h, (0.03 + 0.07 * k) * h, fill=A((70, 22, 22), a))
    d.ell(cx + 0.01 * h, cy + 0.3 * h - 0.0 * h, 0.08 * h, 0.018 * h, fill=A((232, 222, 208), a))
    d.ell(cx + 0.01 * h, cy + (0.36 + 0.05 * k) * h, 0.05 * h, 0.02 * h * k, fill=A((170, 70, 70), a))
