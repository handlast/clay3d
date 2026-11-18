# Flat 2D characters/props for 《叶中幽灵蛙》 Oreobates foliaspectrum.
# Frog per Venegas et al. 2026 (Diversity 18:458): dorsum light brown with faint reddish hue + dark W-shaped scapular mark,
# limbs with orange / reddish-brown hue, pointed granules homogeneous in size, snout nearly truncate, DISTINCTLY long slender
# fingers & toes (no webbing), iris bicoloured (upper half red, lower half greenish bronze, brown reticulations), sclera yellow,
# belly orange / brownish orange with brown reticulations.
# No dark outlines: shapes separated by value, highlights and glow only. Eye/mouth lines may be dark.
import math, random
from chars import *          # base + fx + easing E, flatbg, rot, colors GOLD, NAVYT, ...

GF = (176, 120, 92); GF_D = (122, 78, 58); GF_L = (214, 160, 124); GF_M = (96, 58, 42)   # body / dark / light / marks
LIMB = (204, 118, 72); LIMB_L = (232, 156, 104)
BELLY = (236, 132, 52); BELLY_R = (140, 72, 36)
IRED = (214, 36, 40); IRED_L = (255, 96, 84); IBRZ = (128, 138, 70); IBRZ_L = (170, 176, 96); IRET = (96, 60, 36)
SCL = (246, 204, 60); PUP = (16, 12, 14)
LITTER = [(150, 92, 50), (176, 112, 58), (120, 74, 44), (196, 136, 70), (100, 64, 40), (164, 104, 64), (138, 86, 52)]
SOIL = (92, 62, 44); SOIL_D = (62, 40, 30); ROOT = (126, 88, 60); ROOT_L = (160, 118, 82)
MOSS = (70, 120, 60); MOSS_D = (44, 84, 44)
SKINH = (232, 186, 146); SKINH_D = (196, 146, 108)

# other three new species (colours from the paper's characterizations; used in the line-up)
PALS = {
    "folia":  (GF, GF_D, GF_L, GF_M, LIMB, BELLY),
    "azul":   ((150, 112, 70), (104, 76, 48), (190, 150, 100), (80, 56, 36), (140, 102, 66), (226, 204, 168)),   # bronze/brown, tan-cream belly
    "chiri":  ((176, 140, 100), (126, 96, 66), (210, 178, 134), (110, 80, 54), (226, 140, 60), (246, 214, 70)),  # light brown, yellow belly
    "nigrum": ((54, 46, 44), (34, 28, 28), (90, 80, 76), (40, 32, 30), (62, 52, 48), (60, 46, 42)),              # deep brown / nearly black
    "grey":   ((120, 120, 128), (86, 86, 94), (160, 160, 168), (80, 80, 88), (130, 130, 138), (180, 180, 186)),
}
IRISES = {"folia": "split", "azul": (184, 104, 52), "chiri": (220, 176, 60), "nigrum": (70, 50, 36), "grey": (150, 150, 150)}

def glow_disc(d, x, y, r, col, a):
    if a <= 0.01: return
    for i in range(7):
        k = 1 - i / 7; d.circ(x, y, r * (0.3 + 0.9 * k), fill=A(col, a * 0.14 * (1.2 - k * 0.6)))

def _pie(d, x, y, r, a0, a1, col):
    if a1 - a0 < 0.5: return
    d.d.pieslice((P(x - r), P(y - r), P(x + r), P(y + r)), a0, a1, fill=col)

def iris(d, x, y, r, t, a=1.0, top=1.0, bot=1.0, ret=1.0, scl=1.0, look=0.0, lid=0.0, kind="split", lidcol=GF, pupil=1.0, shine=1.0):
    """Eye seen from the front. r = eyeball radius. top/bot 0..1 paint the red upper / bronze lower half (sweep).
    ret 0..1 draws brown reticulations; scl 0..1 colours the sclera rim yellow; lid 0..1 closes the eyelid from the top."""
    if a <= 0.01: return
    d.circ(x, y, r, fill=A(mix((60, 54, 50), SCL, scl), a))                 # sclera rim
    ri = r * 0.86; cx = x + look * r * 0.08
    if kind == "split":
        d.circ(cx, y, ri, fill=A((84, 78, 74), a))                           # unpainted iris
        if top > 0: _pie(d, cx, y, ri, 180, 180 + 180 * cl(top), A(IRED, a))
        if bot > 0: _pie(d, cx, y, ri, 0, 180 * cl(bot), A(IBRZ, a))
        if top > 0.98: d.ell(cx - ri * 0.32, y - ri * 0.55, ri * 0.34, ri * 0.14, A(IRED_L, a * 0.7))
        if bot > 0.98: d.ell(cx + ri * 0.3, y + ri * 0.62, ri * 0.32, ri * 0.12, A(IBRZ_L, a * 0.8))
        if ret > 0:                                                            # brown reticulation network (mostly lower half)
            rr = random.Random(7); w = max(1.5, r * 0.035)
            for i in range(16):
                ang = math.pi * (i + 0.5) / 16                                 # lower half: 0..pi (y down)
                r0 = ri * rr.uniform(0.38, 0.5); r1 = ri * rr.uniform(0.8, 0.97); kk = cl(ret * 1.6 - i / 16 * 0.6)
                if kk <= 0: continue
                xm = cx + math.cos(ang + 0.08) * (r0 + (r1 - r0) * 0.5); ym = y + math.sin(ang + 0.08) * (r0 + (r1 - r0) * 0.5)
                d.line([(cx + math.cos(ang) * r0, y + math.sin(ang) * r0), (xm, ym),
                        (cx + math.cos(ang - 0.05) * lerp(r0, r1, kk), y + math.sin(ang - 0.05) * lerp(r0, r1, kk))], A(IRET, a * 0.85 * kk), w)
                kb = cl((kk - 0.6) / 0.4)
                if i % 2 == 0 and kb > 0:   # side branch fades in (no pop)
                    a2 = ang + math.pi / 16; d.line([(xm, ym), (cx + math.cos(a2) * (r0 + (r1 - r0) * 0.55), y + math.sin(a2) * (r0 + (r1 - r0) * 0.55))], A(IRET, a * 0.7 * kb), w * 0.8)
            for i in range(7):                                                 # a few faint ones on the red half too
                ang = math.pi + math.pi * (i + 0.5) / 7
                d.line([(cx + math.cos(ang) * ri * 0.48, y + math.sin(ang) * ri * 0.48), (cx + math.cos(ang + 0.1) * ri * 0.85, y + math.sin(ang + 0.1) * ri * 0.85)], A((150, 30, 30), a * 0.6 * ret), max(1.2, r * 0.025))
    else:
        d.circ(cx, y, ri, fill=A(kind, a))
        for i in range(10):
            ang = 2 * math.pi * i / 10
            d.line([(cx + math.cos(ang) * ri * 0.45, y + math.sin(ang) * ri * 0.45), (cx + math.cos(ang + 0.15) * ri * 0.88, y + math.sin(ang + 0.15) * ri * 0.88)], A(mix(kind, (0, 0, 0), 0.4), a * 0.6), max(1.2, r * 0.03))
    pw = ri * 0.62 * pupil; ph = ri * 0.30 * pupil                             # horizontal pupil
    d.ell(cx, y, pw, ph, A(PUP, a))
    if shine > 0:
        d.circ(cx - ri * 0.36, y - ri * 0.36, ri * 0.15, fill=A(WHITE, a * 0.95 * shine)); d.circ(cx + ri * 0.3, y + ri * 0.05, ri * 0.06, fill=A(WHITE, a * 0.7 * shine))
    if lid > 0.01: _lid_partial(d, x, y, r, lid, A(lidcol, a))                # eyelid closing from the top

def _lid_partial(d, x, y, r, lid, col):
    # filled cap of the circle above the line y0 = y - r + 2r*lid
    y0 = y - r + 2 * r * cl(lid)
    # simpler robust: polygon of circle points with y clipped at y0
    cpts = []
    for i in range(73):
        ang = 2 * math.pi * i / 72
        px_, py_ = x + math.cos(ang) * (r + 1), y + math.sin(ang) * (r + 1)
        cpts.append((px_, min(py_, y0)))
    d.poly(cpts, col)
    d.line([(x - math.sqrt(max(0, (r + 1) ** 2 - (y0 - y) ** 2)), y0), (x + math.sqrt(max(0, (r + 1) ** 2 - (y0 - y) ** 2)), y0)], A(mix(col[:3], (0, 0, 0), 0.35), col[3] / 255), max(2, r * 0.07))

def blink_k(t, seed=0.0, period=3.9):
    ph = (t + seed) % period
    return math.sin(math.pi * ph / 0.18) if ph < 0.18 else 0.0

def granules(d, x0, y0, x1, y1, col, a, step=14, seed=3, size=4.0, clip=None):
    """pointed granules homogeneous in size: tiny triangles on a jittered grid"""
    rr = random.Random(seed)
    yy = y0; row = 0
    while yy < y1:
        xx = x0 + (step / 2 if row % 2 else 0)
        while xx < x1:
            px_, py_ = xx + rr.uniform(-2, 2), yy + rr.uniform(-2, 2)
            if clip is None or clip(px_, py_):
                d.poly([(px_ - size, py_ + size * 0.7), (px_ + size, py_ + size * 0.7), (px_, py_ - size * 1.1)], A(col, a))
            xx += step
        yy += step * 0.86; row += 1

def long_hand(d, x, y, s, a, ang, n=4, L=46, col=LIMB, tip=LIMB_L, spread=0.42, fk=1.0):
    """long slender fingers fanned from (x,y). fk scales finger length (for the 'long fingers' demo)."""
    for j in range(n):
        th = ang + (j - (n - 1) / 2) * spread; l = L * s * (0.8 + 0.25 * (j == n // 2 or j == n // 2 - 1)) * fk
        ex, ey = x + math.cos(th) * l, y + math.sin(th) * l
        d.line([(x, y), (ex, ey)], A(col, a), max(2, 7 * s)); d.circ(ex, ey, max(2, 5.5 * s), fill=A(tip, a))

def ghostfrog(d, x, y, s, t, a=1.0, face="calm", pal="folia", look=0.0, blink=True, eye=None, ghost=0.0, fk=1.0, squash=0.0,
              mouth=0.0, lift=0.0, seed=0.0, eyes_only=0.0, glow_eyes=0.0, lid=None):
    """Front view sitting frog; (x,y) = belly centre; ~ 320*s wide. eye: dict(top,bot,ret,scl) paint progress.
    ghost 0..1 turns it into a translucent leaf-coloured 'apparition'. eyes_only 0..1 fades the body leaving the eyes."""
    if a <= 0.01: return
    body, dark, light, mark, limb, belly = PALS[pal]
    if ghost > 0:
        g = cl(ghost); body = mix(body, (196, 150, 96), g * 0.5); light = mix(light, (240, 220, 180), g * 0.4)
    ab = a * (1 - 0.55 * cl(ghost)) * (1 - cl(eyes_only))
    br = 1 + 0.02 * math.sin(t * 3.0 + seed)
    sy = (1 - squash) * br; sx = 1 + squash * 0.5
    P_ = lambda px, py: (x + px * s * sx, y + py * s * sy - lift * s)
    if ghost > 0: glow_disc(d, x, y - 40 * s, 300 * s, (255, 240, 200), 0.35 * ghost * a)
    if ab > 0.01:
        d.ell(x, y + 132 * s, 190 * s, 22 * s, A((0, 0, 0), 0.25 * ab))
        # hind legs folded at the sides + long slender toes splayed forward
        for sd in (-1, 1):
            cx, cy = P_(sd * 112, 74)
            d.ell(cx - sd * 4 * s, cy + 2 * s, 56 * s, 44 * s, A(mix(limb, dark, 0.3), ab)); d.ell(cx - sd * 4 * s, cy - 6 * s, 56 * s, 44 * s, A(limb, ab))
            d.ell(cx + sd * 6 * s, cy - 18 * s, 26 * s, 10 * s, A(LIMB_L, ab * 0.6))
            for j in range(2): d.line([(cx - sd * 30 * s, cy - 10 * s + j * 22 * s), (cx + sd * 30 * s, cy - 18 * s + j * 22 * s)], A(mark, ab * 0.7), 8 * s)  # limb bars
            fx_, fy_ = P_(sd * 150, 126)
            long_hand(d, fx_, fy_, s, ab, (0 if sd > 0 else math.pi) + sd * 0.15, 5, 62, limb, LIMB_L, 0.34, fk)
        # body (granular) with W-shaped scapular mark
        bx, by = P_(0, 20)
        d.ell(bx, by + 6 * s, 112 * s * sx, 98 * s * sy, A(dark, ab)); d.ell(bx, by - 4 * s, 112 * s * sx, 98 * s * sy, A(body, ab))
        d.ell(bx - 30 * s, by - 52 * s, 50 * s, 20 * s, A(light, ab * 0.5))
        W_ = [P_(-58, -20), P_(-30, 8), P_(0, -14), P_(30, 8), P_(58, -20)]
        d.line(W_, A(mark, ab * 0.85), 13 * s)
        granules(d, bx - 100 * s, by - 90 * s, bx + 100 * s, by + 60 * s, light, ab * 0.5, 17 * s, 5, 3.4 * s,
                 clip=lambda px_, py_: ((px_ - bx) / (104 * s)) ** 2 + ((py_ - by) / (92 * s)) ** 2 < 1)
        ex_, ey_ = P_(0, 58)                                                        # orange belly peeking
        d.ell(ex_, ey_, 70 * s, 46 * s, A(belly, ab))
        for j in range(5): d.arc(ex_ - 40 * s + j * 20 * s, ey_ + 4 * s, 16 * s, 12 * s, 200, 340, A(BELLY_R, ab * 0.5), 4 * s)
        # front arms: slender, with LONG fingers
        for sd in (-1, 1):
            ax, ay = P_(sd * 56, 32); hx, hy = P_(sd * 80, 118)
            d.line([(ax, ay), (hx, hy)], A(mix(limb, dark, 0.25), ab), 22 * s); d.line([(ax - sd * 3 * s, ay), (hx - sd * 2 * s, hy - 4 * s)], A(limb, ab), 15 * s)
            long_hand(d, hx, hy + 4 * s, s, ab, math.pi / 2 + sd * 0.55, 4, 50, limb, LIMB_L, 0.42, fk)
        # head: as long as wide, nearly truncate snout
        hx, hy = P_(0, -80)
        d.rect(hx - 126 * s * sx, hy - 54 * s * sy, hx + 126 * s * sx, hy + 66 * s * sy, fill=A(dark, ab), r=56 * s)
        d.rect(hx - 126 * s * sx, hy - 62 * s * sy, hx + 126 * s * sx, hy + 58 * s * sy, fill=A(body, ab), r=56 * s)
        d.ell(hx, hy - 34 * s, 72 * s, 14 * s, A(light, ab * 0.5))
        for sd in (-1, 1):                                                          # canthal / supratympanic stripes, labial bars
            d.line([P_(sd * 20, -118), P_(sd * 70, -96)], A(mark, ab * 0.8), 8 * s)
            d.line([P_(sd * 96, -96), P_(sd * 126, -56)], A((40, 26, 22), ab * 0.8), 8 * s)
            for j in range(3): d.line([P_(sd * (40 + j * 28), -36), P_(sd * (44 + j * 28), -22)], A(mark, ab * 0.7), 7 * s)
        granules(d, hx - 110 * s, hy - 56 * s, hx + 110 * s, hy + 40 * s, light, ab * 0.4, 18 * s, 9, 3 * s)
        mx, my = P_(0, -40)
        if mouth > 0.02:
            d.ell(mx, my + 12 * s * mouth, 90 * s, 30 * s * mouth + 4 * s, A((96, 26, 40), a)); d.ell(mx, my + 24 * s * mouth, 50 * s, 12 * s * mouth + 2 * s, A((255, 120, 140), a))
        else:
            if face in ("happy", "proud"): d.arc(mx, my - 24 * s, 104 * s, 30 * s, 25, 155, A(INK, ab), 6 * s)
            elif face in ("shock", "scared"): d.ell(mx, my + 4 * s, 22 * s, 16 * s, A((90, 20, 40), ab))
            elif face == "sus": d.line([(mx - 70 * s, my), (mx + 70 * s, my - 8 * s)], A(INK, ab), 6 * s)
            else: d.arc(mx, my - 18 * s, 92 * s, 22 * s, 30, 150, A(INK, ab), 6 * s)
    # eyes: domes on top of the head
    ek = dict(top=1, bot=1, ret=1, scl=1) if eye is None else eye
    bl = blink_k(t, seed) if blink and face not in ("shock", "scared") else 0.0
    if lid is not None: bl = max(bl, lid)
    kind = "split" if IRISES[pal] == "split" else IRISES[pal]
    for sd in (-1, 1):
        exx, eyy = P_(sd * 74, -132)
        if ab > 0.01:
            d.circ(exx, eyy + 5 * s, 50 * s, fill=A(dark, ab)); d.circ(exx, eyy - 3 * s, 50 * s, fill=A(body, ab))
        ea = a * (1 - 0.3 * cl(ghost))
        if glow_eyes > 0: glow_disc(d, exx, eyy, 90 * s, IRED_L, glow_eyes * a)
        rr_ = 38 * s * (1.12 if face in ("shock", "scared") else 1.0)
        iris(d, exx, eyy, rr_, t, ea, ek["top"], ek["bot"], ek["ret"], ek["scl"], look, bl, kind, lidcol=body, pupil=0.75 if face in ("shock", "scared") else 1.0)
        if face == "sus" and ab > 0.01:
            d.line([(exx - sd * 40 * s, eyy - 52 * s), (exx + sd * 34 * s, eyy - 40 * s)], A(INK, ab), 6 * s)
        if face == "proud" and ab > 0.01:
            _lid_partial(d, exx, eyy, rr_, 0.32, A(body, ea))
    if face in ("shock", "scared") and ab > 0.01:
        q = P_(160, -180); d.ell(q[0], q[1], 10 * s, 16 * s, A(CYAN, ab))

def frog_top(d, x, y, s, t, a=1.0, pal="folia", belly=False, gran=1.0, ang=0.0, fk=1.0, flipx=1.0, eye=1.0):
    """Dorsal (top-down) view, head up. (x,y)=body centre. snout at y-150*s, vent at y+120*s (SVL ~ 270*s).
    belly=True draws the ventral side (orange with brown reticulations). flipx scales x (for the flip-over demo)."""
    if a <= 0.01: return
    body, dark, light, mark, limb, bel = PALS[pal]
    ca, sa = math.cos(ang), math.sin(ang)
    def Q(px, py): px *= flipx; return (x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s)
    def E_(px, py, rx, ry, col):
        pts = [Q(px + rx * math.cos(2 * math.pi * i / 28), py + ry * math.sin(2 * math.pi * i / 28)) for i in range(28)]; d.poly(pts, col)
    top = body if not belly else bel
    d.ell(x + 10 * s, y + 20 * s, 150 * s * abs(flipx), 160 * s, A((0, 0, 0), 0.18 * a))
    for sd in (-1, 1):   # hind legs: thigh, shank, long foot + toes
        k1 = Q(sd * 70, 90); k2 = Q(sd * 150, 40); k3 = Q(sd * 120, 170); k4 = Q(sd * 150, 230)
        d.line([k1, k2, k3], A(limb if not belly else mix(bel, limb, 0.5), a), 34 * s); d.line([k3, k4], A(limb, a), 18 * s)
        for j in range(5):
            th = math.atan2(k4[1] - k3[1], k4[0] - k3[0]) + (j - 2) * 0.32
            L = (40 + 18 * (j in (3,))) * s * fk; d.line([k4, (k4[0] + math.cos(th) * L, k4[1] + math.sin(th) * L)], A(LIMB_L, a), 6 * s)
        a1 = Q(sd * 60, -40); a2 = Q(sd * 120, -10); a3 = Q(sd * 128, -70)   # arms + long fingers
        d.line([a1, a2, a3], A(limb, a), 18 * s)
        for j in range(4):
            th = math.atan2(a3[1] - a2[1], a3[0] - a2[0]) + (j - 1.5) * 0.38
            L = 40 * s * fk; d.line([a3, (a3[0] + math.cos(th) * L, a3[1] + math.sin(th) * L)], A(LIMB_L, a), 5 * s)
    E_(0, 24, 90, 112, A(mix(top, (0, 0, 0), 0.25), a)); E_(0, 16, 90, 112, A(top, a))
    pts = [Q(-80, -60), Q(-70, -130), Q(-30, -152), Q(30, -152), Q(70, -130), Q(80, -60)]   # head, truncate snout
    d.poly(pts, A(top, a))
    if not belly:
        d.line([Q(-50, -10), Q(-24, 20), Q(0, 0), Q(24, 20), Q(50, -10)], A(mark, a * 0.85), 12 * s)
        for j in range(3): d.line([Q(-70, 60 + j * 26), Q(-40, 70 + j * 26)], A(mark, a * 0.4), 6 * s)
        if gran > 0:
            gp = []
            rr = random.Random(4)
            for i in range(130):
                px, py = rr.uniform(-86, 86), rr.uniform(-140, 125)
                if (px / 88) ** 2 + ((py - 16) / 112) ** 2 < 1 or (abs(px) < 72 and -150 < py < -60):
                    c = Q(px, py); g = 3.2 * s
                    d.poly([(c[0] - g, c[1] + g * 0.7), (c[0] + g, c[1] + g * 0.7), (c[0], c[1] - g * 1.1)], A(light, a * 0.7 * gran))
        if eye > 0:
            for sd in (-1, 1):
                c = Q(sd * 50, -112); d.circ(c[0], c[1], 22 * s, fill=A(dark, a)); d.circ(c[0], c[1], 17 * s, fill=A(SCL, a * eye))
                d.d.pieslice((P(c[0] - 14 * s), P(c[1] - 14 * s), P(c[0] + 14 * s), P(c[1] + 14 * s)), 180, 360, fill=A(IRED, a * eye))
                d.d.pieslice((P(c[0] - 14 * s), P(c[1] - 14 * s), P(c[0] + 14 * s), P(c[1] + 14 * s)), 0, 180, fill=A(IBRZ, a * eye))
                d.ell(c[0], c[1], 8 * s, 4 * s, A(PUP, a * eye))
    else:
        rr = random.Random(8)   # brown reticulation / blotches on orange
        for i in range(26):
            px, py = rr.uniform(-70, 70), rr.uniform(-60, 110); c = Q(px, py)
            d.ell(c[0], c[1], rr.uniform(8, 18) * s, rr.uniform(5, 11) * s, A(BELLY_R, a * 0.55))
        c = Q(0, -100); d.ell(c[0], c[1], 50 * s, 30 * s, A((150, 96, 70), a))   # brown throat
        for i in range(6): cc = Q(rr.uniform(-36, 36), -100 + rr.uniform(-18, 18)); d.circ(cc[0], cc[1], 4 * s, fill=A((236, 214, 170), a))

def leaf_shape(d, x, y, L, ang, col, a=1.0, w=0.42, vein=True):
    if a <= 0.01: return
    ca, sa = math.cos(ang), math.sin(ang); pts = []
    for i in range(13):
        u = i / 12; hw = math.sin(math.pi * u) ** 0.8 * L * w * 0.5
        pts.append((x + ca * (u - 0.5) * L - sa * hw, y + sa * (u - 0.5) * L + ca * hw))
    for i in range(12, -1, -1):
        u = i / 12; hw = math.sin(math.pi * u) ** 0.8 * L * w * 0.5
        pts.append((x + ca * (u - 0.5) * L + sa * hw, y + sa * (u - 0.5) * L - ca * hw))
    d.poly(pts, A(col, a))
    if vein: d.line([(x - ca * L * 0.45, y - sa * L * 0.45), (x + ca * L * 0.45, y + sa * L * 0.45)], A(mix(col, (255, 230, 190), 0.3), a * 0.7), max(2, L * 0.02))

def litter_bed(d, t, seed=1, n=150, box=(-80, 0, 1160, 1980), a=1.0, dark=0.0, sway=1.0, scale=1.0):
    rr = random.Random(seed)
    for i in range(n):
        x, y = rr.uniform(box[0], box[2]), rr.uniform(box[1], box[3]); L = rr.uniform(120, 220) * scale; ang = rr.uniform(-math.pi, math.pi)
        c = mix(LITTER[i % len(LITTER)], (10, 14, 20), dark)
        leaf_shape(d, x, y, L, ang + 0.01 * sway * math.sin(t * 0.8 + i), c, a, rr.uniform(0.36, 0.5))

def fern(d, x, y, sc, ang, t, col, col2, a=1.0):
    for j in range(5):
        a_ = -math.pi / 2 + ang + (j - 2) * 0.25 + 0.03 * math.sin(t * 1.5 + j)
        lx, ly = x + math.cos(a_) * 10, y
        d.poly([(lx, ly), (lx + math.cos(a_ - 0.2) * 220 * sc, ly + math.sin(a_ - 0.2) * 220 * sc), (lx + math.cos(a_) * 300 * sc, ly + math.sin(a_) * 300 * sc),
                (lx + math.cos(a_ + 0.2) * 220 * sc, ly + math.sin(a_ + 0.2) * 220 * sc)], A(col if j % 2 else col2, a))

def tree_fern(d, x, y, h, t, a=1.0, col=(46, 104, 70), col2=(70, 134, 84), trunk=(80, 60, 50)):
    d.rect(x - 12, y - h, x + 12, y, fill=A(trunk, a), r=8)
    for j in range(8):
        ang = -math.pi / 2 + (j - 3.5) * 0.42 + 0.04 * math.sin(t * 1.2 + j)
        pts = [(x, y - h)]; L = 170
        for k in range(1, 9):
            u = k / 8; pts.append((x + math.cos(ang) * L * u, y - h + math.sin(ang) * L * u + 60 * u * u))
        d.line(pts, A(col, a), 10)
        for k in range(2, 9, 2): d.ell(pts[k][0], pts[k][1] + 6, 16, 8, A(col2, a))

def bamboo(d, x, y, h, t, a=1.0, col=(120, 160, 80)):
    sw = 8 * math.sin(t * 0.9 + x)
    pts = [(x + sw * (k / 8) ** 2, y - h * k / 8) for k in range(9)]
    d.line(pts, A(col, a), 9)
    for k in range(1, 9): d.line([(pts[k][0] - 8, pts[k][1]), (pts[k][0] + 8, pts[k][1])], A(mix(col, (40, 60, 30), 0.4), a), 4)
    for k in range(3, 9, 2):
        for sd in (-1, 1): leaf_shape(d, pts[k][0] + sd * 34, pts[k][1] - 10, 70, -0.5 * sd + (math.pi if sd < 0 else 0), mix(col, (60, 140, 70), 0.5), a, 0.3, False)

def scientist(d, x, y, s, t, a=1.0, walk=0.0, beam=0.0, beam_ang=0.35, night=1.0):
    """side view walking right; (x,y)=feet. beam: headlamp cone strength. (from frog/scenes.py)"""
    dk = lambda c: mix(c, (14, 20, 40), 0.45 * night)
    ph = t * 6 * walk
    hx, hy = x + 6 * s, y - 330 * s
    if beam > 0:
        L = 760 * s
        for j in range(5):
            sp = 0.20 - j * 0.035
            p1 = (hx + 30 * s + math.cos(beam_ang - sp) * L, hy + math.sin(beam_ang - sp) * L)
            p2 = (hx + 30 * s + math.cos(beam_ang + sp) * L, hy + math.sin(beam_ang + sp) * L)
            d.poly([(hx + 30 * s, hy - 8 * s), p1, p2], A((255, 244, 190), 0.07 * beam * a))
    for sd, c in ((1, (40, 46, 64)), (-1, (54, 62, 84))):
        sw = math.sin(ph + (0 if sd > 0 else math.pi)) * 0.45 * walk
        kx, ky = x + math.sin(sw) * 70 * s, y - 80 * s
        d.line([(x, y - 160 * s), (kx, ky), (kx + math.sin(sw) * 40 * s, y)], A(dk(c), a), 30 * s)
        d.ell(kx + math.sin(sw) * 40 * s + 14 * s, y - 4 * s, 26 * s, 12 * s, A(dk((60, 50, 40)), a))
    d.rect(x - 70 * s, y - 300 * s, x - 10 * s, y - 170 * s, fill=A(dk((150, 96, 56)), a), r=16 * s)
    d.rect(x - 34 * s, y - 290 * s, x + 46 * s, y - 150 * s, fill=A(dk((80, 128, 98)), a), r=26 * s)
    sw = math.sin(ph) * 0.4 * walk
    d.line([(x + 6 * s, y - 270 * s), (x + 6 * s + math.sin(-sw) * 50 * s, y - 200 * s), (x + 60 * s, y - 210 * s)], A(dk((70, 116, 88)), a), 22 * s)
    d.circ(hx, hy, 42 * s, fill=A(dk(SKINH), a))
    d.ell(hx - 4 * s, hy - 30 * s, 52 * s, 22 * s, A(dk((70, 120, 90)), a)); d.rect(hx - 4 * s, hy - 34 * s, hx + 62 * s, hy - 22 * s, fill=A(dk((70, 120, 90)), a), r=6 * s)
    d.circ(hx + 24 * s, hy - 4 * s, 5 * s, fill=A(INK, a))
    d.arc(hx + 22 * s, hy + 14 * s, 12 * s, 7 * s, 20, 160, A(INK, a), 3 * s)
    lx, ly = hx + 34 * s, hy - 14 * s
    if beam > 0: glow_disc(d, lx, ly, 46 * s, (255, 240, 170), 0.9 * beam * a)
    d.circ(lx, ly, 10 * s, fill=A((255, 250, 220) if beam > 0 else (180, 180, 170), a))

def cow(d, x, y, s, t, a=1.0, flip=1, graze=0.0, seed=0):
    """flat side-view cow; (x,y)=hooves line centre"""
    if a <= 0.01: return
    f = flip; W_, B_ = (244, 240, 232), (52, 46, 48)
    d.ell(x, y + 4 * s, 120 * s, 12 * s, A((0, 0, 0), 0.18 * a))
    for dx in (-80, -50, 50, 80):
        d.rect(x + f * dx * s - 9 * s, y - 70 * s, x + f * dx * s + 9 * s, y, fill=A(mix(W_, (0, 0, 0), 0.12), a), r=4 * s)
        d.rect(x + f * dx * s - 10 * s, y - 10 * s, x + f * dx * s + 10 * s, y, fill=A(B_, a), r=3 * s)
    d.rect(x - 110 * s, y - 150 * s, x + 110 * s, y - 60 * s, fill=A(W_, a), r=40 * s)
    for px_, py_, rx, ry in ((-40, -118, 34, 22), (40, -96, 26, 18), (-80, -84, 18, 14)):
        d.ell(x + f * px_ * s, y + py_ * s, rx * s, ry * s, A(B_, a))
    hb = math.sin(t * 2 + seed) * 4 * s + graze * 50 * s
    hx, hy = x + f * 128 * s, y - 140 * s + hb
    d.line([(x + f * 96 * s, y - 120 * s), (hx, hy)], A(W_, a), 46 * s)
    d.rect(hx - 34 * s, hy - 30 * s, hx + 34 * s, hy + 34 * s, fill=A(W_, a), r=22 * s)
    d.rect(hx + f * 4 * s - 24 * s, hy + 6 * s, hx + f * 4 * s + 30 * s, hy + 36 * s, fill=A((240, 170, 170), a), r=14 * s)
    d.circ(hx + f * 8 * s, hy - 8 * s, 6 * s, fill=A(INK, a))
    d.ell(hx - f * 30 * s, hy - 30 * s, 16 * s, 8 * s, A(B_, a))
    tl = x - f * 110 * s; d.line([(tl, y - 140 * s), (tl - f * 18 * s, y - 80 * s + 6 * s * math.sin(t * 3 + seed))], A(B_, a), 6 * s)

def hoof(d, x, y, s, a=1.0, ang=0.0, col=(70, 50, 38)):
    """cloven hoofprint: two rounded halves"""
    if a <= 0.01: return
    for sd in (-1, 1):
        d.ell(x + sd * 9 * s, y, 8 * s, 13 * s, A(col, a))
    d.ell(x - 9 * s, y - 5 * s, 3 * s, 4 * s, A(mix(col, (0, 0, 0), 0.3), a)); d.ell(x + 9 * s, y - 5 * s, 3 * s, 4 * s, A(mix(col, (0, 0, 0), 0.3), a))

def egg(d, x, y, r, a=1.0, col=(246, 238, 210), inner=None, k=0.0, t=0.0):
    """jelly egg; inner: draw a curled froglet inside growing with k 0..1"""
    if a <= 0.01: return
    d.circ(x, y, r * 1.15, fill=A(mix(col, (255, 255, 255), 0.4), 0.4 * a)); d.circ(x, y, r, fill=A(col, 0.85 * a))
    if k > 0:
        rr = r * (0.3 + 0.45 * k)
        d.ell(x, y + rr * 0.1, rr, rr * 0.8, A(GF, a)); d.circ(x - rr * 0.35, y - rr * 0.35, rr * 0.22, fill=A(SCL, a))
        d.circ(x + rr * 0.35, y - rr * 0.35, rr * 0.22, fill=A(SCL, a))
        for sd in (-1, 1): d.circ(x + sd * rr * 0.35, y - rr * 0.35, rr * 0.12, fill=A(IRED, a))
    d.ell(x - r * 0.35, y - r * 0.4, r * 0.25, r * 0.13, A(WHITE, 0.7 * a))

def tadpole(d, x, y, s, t, a=1.0, col=(70, 70, 80)):
    if a <= 0.01: return
    pts = []
    for i in range(14):
        u = i / 13; pts.append((x + 40 * s + u * 120 * s, y + math.sin(t * 9 - u * 5) * 14 * s * u))
    d.line(pts, A(col, a), 14 * s)
    d.ell(x, y, 54 * s, 40 * s, A(col, a)); d.circ(x - 22 * s, y - 12 * s, 8 * s, fill=A(WHITE, a)); d.circ(x - 24 * s, y - 12 * s, 4 * s, fill=A(INK, a))

def coin(d, x, y, r, a=1.0):
    d.circ(x + 6, y + 8, r, fill=A((0, 0, 0), 0.25 * a)); d.circ(x, y, r, fill=A((196, 200, 206), a)); d.circ(x, y, r * 0.86, fill=A((214, 218, 224), a))
    d.circ(x, y, r * 0.86, outline=A((160, 166, 176), a), w=3)
    d.text(x, y - r * 0.12, "1", int(r * 0.9), A((150, 156, 166), a), k=1); d.text(x, y + r * 0.5, "元", int(r * 0.3), A((150, 156, 166), a), k=1)
    d.ell(x - r * 0.4, y - r * 0.5, r * 0.3, r * 0.12, A(WHITE, 0.5 * a))

def mist(d, t, a=1.0, y0=600, n=6, col=(220, 236, 240), seed=2):
    rr = random.Random(seed)
    for i in range(n):
        x = (rr.uniform(0, 1400) + t * rr.uniform(18, 40)) % 1600 - 260; y = y0 + rr.uniform(-200, 500)
        d.ell(x, y, rr.uniform(260, 420), rr.uniform(40, 80), A(col, a * 0.08))
