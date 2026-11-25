# Flat 2D characters/props for 《吼猴新种》: howler monkey (front, sitting on a branch; bare dark face, beard, puffy throat,
# prehensile tail), head-only portrait, side-view anatomy head with hollow hyoid, leaves, roar waves, Amazon map.
# No dark outlines: shapes separated by value, highlights and glow only. Eye/mouth lines may be dark.
import math, random
from chars import *          # base + fx + easing E, flatbg, rot, colors GOLD, NAVYT, ...

HPAL = {  # body, dark (limbs/tail), light (highlight), beard
    "red":   ((184, 72, 40), (122, 42, 28), (232, 118, 74), (150, 54, 32)),     # A. matogrossensis: bright reddish brown
    "gold":  ((222, 160, 62), (140, 64, 36), (250, 204, 118), (176, 98, 44)),   # A. iroi: yellowish-brown to golden, limbs dark reddish
    "dull":  ((168, 96, 54), (116, 60, 36), (198, 132, 86), (132, 70, 40)),     # A. macconnelli: dark orange-brown, dull
    "sara":  ((150, 74, 54), (104, 50, 38), (182, 108, 84), (120, 58, 42)),     # A. sara: opaque reddish brown
    "grey":  ((140, 132, 128), (100, 94, 92), (180, 174, 168), (116, 110, 106)),
    "black": ((60, 56, 60), (40, 38, 42), (100, 96, 104), (48, 44, 48)),
}
SKIN = (78, 58, 56); SKIN_L = (112, 86, 80); SKIN_D = (54, 40, 40); MOUTH = (110, 24, 36); TONGUE = (236, 110, 120); TEETH = (250, 246, 236)
LEAF1 = (60, 150, 80); LEAF2 = (92, 186, 96); LEAF3 = (40, 110, 66); BARK = (110, 78, 54); BARK_L = (150, 110, 76)

def howler_head(d, x, y, s, t, a=1.0, pal="red", face="calm", mouth=0.0, look=0.0, blink=True, puff=None, beard=True, lookup=0.0):
    """(x,y) = head centre; ~200*s wide. mouth 0..1 opens to a howl. puff swells the throat/beard."""
    if a <= 0.01: return
    body, dark, light, brd = HPAL[pal]
    pf = mouth if puff is None else puff
    if beard:   # beard + swollen throat (hyoid region)
        d.ell(x, y + 78 * s, (74 + 14 * pf) * s, (52 + 18 * pf) * s, A(brd, a))
        d.ell(x, y + 70 * s, (60 + 12 * pf) * s, (40 + 14 * pf) * s, A(mix(brd, body, 0.4), a))
    d.circ(x, y, 96 * s, fill=A(body, a))                                       # fur head
    d.ell(x - 30 * s, y - 56 * s, 46 * s, 22 * s, A(light, a * 0.55))           # fur highlight
    for i in range(9):                                                          # soft fur tufts round the crown/cheeks
        ang = -math.pi / 2 + (i - 4) * 0.36; r0 = 88 * s
        d.circ(x + math.cos(ang) * r0, y + math.sin(ang) * r0, 22 * s, fill=A(body, a))
    # bare face
    fy = y + 8 * s
    d.ell(x, fy, 62 * s, 70 * s, A(SKIN, a))
    d.ell(x, fy - 38 * s, 56 * s, 16 * s, A(SKIN_D, a))                         # brow ridge
    mx, my = x, fy + 34 * s
    d.ell(mx, my, (40 + 6 * mouth) * s, (32 + 10 * mouth) * s, A(SKIN_L, a))     # muzzle
    for sd in (-1, 1): d.ell(x + sd * 9 * s, fy + 12 * s, 5 * s, 3.5 * s, A(SKIN_D, a))   # nostrils
    # eyes
    bl = 1.0
    if blink and face not in ("shock", "roar"):
        ph = (t + x * 0.0031) % 3.9
        if ph < 0.12: bl = 0.12
    for sd in (-1, 1):
        ex, ey = x + sd * 25 * s, fy - 18 * s - lookup * 2 * s
        er = 17 * s * (1.2 if face == "shock" else 1.0)
        if face == "happy" or face == "proud":
            d.arc(ex, ey + 6 * s, er, er * 0.9, 200, 340, A(WHITE, a), 5 * s); continue
        if face == "roar":
            d.ell(ex, ey + 2 * s, er, er * 0.62, A(WHITE, a))
            d.circ(ex + look * 5 * s, ey + 2 * s, er * 0.5, fill=A(INK, a)); d.circ(ex + look * 5 * s - 3 * s, ey - 1 * s, er * 0.17, fill=A(WHITE, a))
            d.line([(ex - sd * 18 * s, ey - 22 * s), (ex + sd * 14 * s, ey - 12 * s)], A(INK, a), 5 * s)   # angry brows
            continue
        d.ell(ex, ey, er, er * bl, A(WHITE, a))
        if bl > 0.5:
            pr_ = er * (0.42 if face == "shock" else 0.58)
            d.circ(ex + look * 5 * s, ey + 1 * s - lookup * 4 * s, pr_, fill=A(INK, a))
            d.circ(ex + look * 5 * s - 4 * s, ey - 4 * s - lookup * 4 * s, pr_ * 0.32, fill=A(WHITE, a))
        if face == "worry":
            d.line([(ex - sd * 16 * s, ey - 18 * s), (ex + sd * 12 * s, ey - 26 * s)], A(INK, a), 4.5 * s)
        if face == "sus":
            d.line([(ex - sd * 18 * s, ey - 22 * s), (ex + sd * 14 * s, ey - 14 * s)], A(INK, a), 4.5 * s)
    # mouth
    if mouth > 0.04:
        ow, oh = (12 + 22 * mouth) * s, (8 + 30 * mouth) * s
        d.ell(mx, my + 8 * s, ow, oh, A(MOUTH, a))
        d.ell(mx, my + 8 * s + oh * 0.45, ow * 0.6, oh * 0.38, A(TONGUE, a))
        if mouth > 0.3:
            d.rect(mx - ow * 0.55, my + 8 * s - oh * 0.92, mx + ow * 0.55, my + 8 * s - oh * 0.72, fill=A(TEETH, a), r=3 * s)
    else:
        if face in ("happy", "proud"): d.arc(mx, my + 2 * s, 22 * s, 14 * s, 20, 160, A(INK, a), 5 * s)
        elif face == "worry": d.arc(mx, my + 18 * s, 18 * s, 10 * s, 200, 340, A(INK, a), 5 * s)
        elif face == "shock": d.ell(mx, my + 8 * s, 10 * s, 13 * s, A(MOUTH, a))
        elif face == "sus": d.line([(mx - 16 * s, my + 8 * s), (mx + 16 * s, my + 4 * s)], A(INK, a), 5 * s)
        else: d.arc(mx, my + 2 * s, 18 * s, 9 * s, 30, 150, A(INK, a), 5 * s)

def howler(d, x, y, s, t, a=1.0, pal="red", face="calm", mouth=0.0, look=0.0, flip=1, tail=True, sway=1.0, baby=False, lookup=0.0, blink=True):
    """sitting on a horizontal branch at local y=+150 (feet + hands grip it); (x,y) = torso centre; ~300*s wide, ~420*s tall."""
    if a <= 0.01: return
    body, dark, light, brd = HPAL[pal]
    sw = 4 * math.sin(t * 1.6) * sway
    P_ = lambda px, py: (x + flip * px * s, y + py * s)
    if tail:   # prehensile tail: hangs below the branch, tip curls into a spiral
        pts = []
        for i in range(30):
            u = i / 29
            if u < 0.6:
                px = -40 - 30 * math.sin(u * 4.0) ; py = 110 + 380 * u
            else:
                v = (u - 0.6) / 0.4; ang = math.pi + v * 4.4; rr_ = 44 * (1 - 0.6 * v)
                cx_, cy_ = -40 - 30 * math.sin(2.4) + 44, 110 + 228
                px = cx_ + rr_ * math.cos(ang); py = cy_ + rr_ * math.sin(ang)
            pts.append(P_(px + 6 * math.sin(t * 1.3 + u * 3) * u, py))
        d.line(pts, A(dark, a), 20 * s)
        d.line(pts[:-3], A(mix(dark, body, 0.35), a), 9 * s)
    for sd in (-1, 1):   # legs
        hx, hy = P_(sd * 52, 70); kx, ky = P_(sd * 96, 104); fx, fy = P_(sd * 72, 148)
        d.line([(hx, hy), (kx, ky), (fx, fy)], A(dark, a), 40 * s)
        d.ell(fx, fy + 2 * s, 30 * s, 14 * s, A(SKIN, a))
    bx, by = P_(0, 30)
    d.ell(bx, by + sw * 0.3 * s, 98 * s, 116 * s, A(body, a))
    d.ell(bx - flip * 30 * s, by - 50 * s, 40 * s, 30 * s, A(light, a * 0.5))
    if baby:   # infant riding on the back/shoulder
        howler_head(d, x + flip * 96 * s, y - 70 * s, s * 0.42, t + 0.7, a, pal, "happy", 0, 0, beard=False)
    for sd in (-1, 1):   # arms reach down to the branch
        sx_, sy_ = P_(sd * 78, -48); ex_, ey_ = P_(sd * 116, 48); hx_, hy_ = P_(sd * 100, 144)
        d.line([(sx_, sy_), (ex_, ey_), (hx_, hy_)], A(dark, a), 32 * s)
        d.ell(hx_, hy_ + 2 * s, 22 * s, 13 * s, A(SKIN, a))
    howler_head(d, x + sw * 0.5 * s, y - 150 * s, s, t, a, pal, face, mouth, look * flip, blink, lookup=lookup)

def branch(d, x0, y0, x1, y1, w, a=1.0, t=0.0, leaves=True, seed=3):
    d.line([(x0, y0), (x1, y1)], A(BARK, a), w); d.line([(x0, y0 - w * 0.22), (x1, y1 - w * 0.22)], A(BARK_L, a * 0.7), w * 0.3)
    if leaves:
        rr = random.Random(seed)
        for i in range(9):
            u = rr.uniform(0, 1); lx, ly = lerp(x0, x1, u), lerp(y0, y1, u)
            leaf(d, lx, ly - w * 0.3, rr.uniform(38, 60), rr.uniform(-2.6, -0.5) + 0.05 * math.sin(t * 1.4 + i), [LEAF1, LEAF2, LEAF3][i % 3], a)

def leaf(d, x, y, L, ang, col, a=1.0, w=0.42):
    ca, sa = math.cos(ang), math.sin(ang); nx, ny = -sa, ca
    tip = (x + ca * L, y + sa * L)
    m1 = (x + ca * L * 0.45 + nx * L * w, y + sa * L * 0.45 + ny * L * w)
    m2 = (x + ca * L * 0.45 - nx * L * w, y + sa * L * 0.45 - ny * L * w)
    d.poly([(x, y), m1, tip, m2], A(col, a))
    d.line([(x, y), tip], A(mix(col, WHITE, 0.25), a * 0.6), max(1.5, L * 0.04))

def flying_leaves(d, t, t0, cx, cy, n=26, spd=900, a=1.0, seed=5, life=2.2, dirx=None):
    """leaves torn off by the roar: each leaf has its own launch time, spins, drifts and FADES out (no pop)."""
    if t < t0: return
    rr = random.Random(seed)
    for i in range(n):
        dl = rr.uniform(0, 0.25); u = t - t0 - dl
        if u < 0: continue
        lf = life * rr.uniform(0.7, 1.0)
        if u > lf: continue
        ang = rr.uniform(-math.pi, math.pi) if dirx is None else (rr.uniform(-0.7, 0.7) + (0 if dirx > 0 else math.pi))
        v = spd * rr.uniform(0.5, 1.0)
        dist = v * (1 - math.exp(-u * 2.2)) / 2.2
        lx = cx + math.cos(ang) * dist + 40 * math.sin(u * 3 + i); ly = cy + math.sin(ang) * dist + 120 * u * u
        al = a * min(1, u / 0.1) * (1 - cl((u - lf * 0.6) / (lf * 0.4)))
        leaf(d, lx, ly, rr.uniform(30, 56), u * rr.uniform(4, 9) + i, [LEAF1, LEAF2, LEAF3][i % 3], al)

def roar_waves(d, x, y, t, t0, t1, col=(255, 236, 170), a=1.0, ang=-math.pi / 2, spread=70, maxr=700, period=0.28, w=10):
    """arcs pulsing out of the mouth while roaring between t0..t1; each arc fades as it grows (continuous in t)."""
    if t < t0: return
    k = 0
    while True:
        tb = t0 + k * period
        if tb > min(t, t1): break
        u = (t - tb) / 1.0
        if 0 <= u < 1:
            r = 40 + u * maxr; al = a * (1 - u) ** 1.3
            d.arc(x, y, r, r, math.degrees(ang) - spread, math.degrees(ang) + spread, A(col, al), w * (1 - 0.5 * u))
        k += 1

# ---- side-view anatomy head (for the hyoid "amplifier") ----
def anat_head(d, x, y, s, t, a=1.0, open_=0.0, glow=0.0, pal="red", cut=1.0):
    """profile facing right; (x,y) = skull centre. cut = cutaway showing the hollow hyoid bulb. returns hyoid (x,y,r)."""
    body, dark, light, brd = HPAL[pal]
    jo = 40 * open_
    d.ell(x + 70 * s, y + 200 * s, 150 * s, 120 * s, A(brd, a))                 # beard / throat bulge
    d.circ(x, y, 150 * s, fill=A(body, a))                                       # head fur
    d.ell(x - 40 * s, y - 80 * s, 60 * s, 26 * s, A(light, a * 0.5))
    d.ell(x + 95 * s, y + 10 * s, 105 * s, 115 * s, A(SKIN, a))                  # bare face
    d.ell(x + 120 * s, y - 70 * s, 70 * s, 18 * s, A(SKIN_D, a))                 # brow ridge
    d.ell(x + 128 * s, y - 34 * s, 22 * s, 18 * s, A(WHITE, a)); d.circ(x + 135 * s, y - 32 * s, 10 * s, fill=A(INK, a)); d.circ(x + 131 * s, y - 36 * s, 3.5 * s, fill=A(WHITE, a))
    d.ell(x + 185 * s, y + 40 * s, 70 * s, 48 * s, A(SKIN_L, a))                 # upper muzzle
    d.circ(x + 236 * s, y + 22 * s, 7 * s, fill=A(SKIN_D, a))                    # nostril
    if open_ > 0.05:
        d.poly([(x + 140 * s, y + 70 * s), (x + 256 * s, y + 66 * s), (x + 250 * s, y + 80 * s + jo * s), (x + 140 * s, y + 90 * s)], A(MOUTH, a))
    d.poly([(x + 120 * s, y + 92 * s), (x + 244 * s, y + 82 * s + jo * s), (x + 236 * s, y + 112 * s + jo * s), (x + 120 * s, y + 130 * s)], A(SKIN_L, a))   # lower jaw
    if cut > 0:
        ca = a * cut
        d.rect(x - 50 * s, y + 130 * s, x + 200 * s, y + 290 * s, fill=A((214, 120, 110), ca * 0.92), r=30 * s)   # cutaway window
        d.line([(x + 170 * s, y + 92 * s), (x + 165 * s, y + 140 * s), (x + 150 * s, y + 290 * s)], A((236, 140, 152), ca), 22 * s)   # airway
        hx, hy, hr = x + 80 * s, y + 205 * s, 64 * s
        for i in range(6): d.circ(hx, hy, hr * (1.6 - i * 0.09), fill=A((255, 220, 120), ca * glow * 0.05))
        bone = (240, 226, 196); bsh = (200, 180, 150)
        d.ell(hx, hy + 6 * s, hr * 1.12, hr * 0.98, A(bsh, ca)); d.ell(hx, hy, hr * 1.06, hr * 0.92, A(bone, ca))     # bony shell
        d.ell(hx + 4 * s, hy + 4 * s, hr * 0.8, hr * 0.68, A((120, 70, 70), ca))                                        # hollow inside (air)
        d.ell(hx + 4 * s, hy + 4 * s, hr * 0.7, hr * 0.58, A((150, 90, 86), ca))
        d.poly([(hx + hr * 0.5, hy - hr * 0.55), (hx + hr * 1.2, hy - hr * 1.0), (hx + hr * 1.3, hy - hr * 0.7), (hx + hr * 0.7, hy - hr * 0.25)], A((236, 140, 152), ca))  # opening to airway
        d.ell(hx - hr * 0.5, hy - hr * 0.55, hr * 0.28, hr * 0.12, A(WHITE, ca * 0.8))
        for k in range(3):     # air resonating inside
            u = ((t * 1.8) + k / 3) % 1
            d.ell(hx + 4 * s, hy + 4 * s, hr * 0.68 * u + 4, hr * 0.56 * u + 4, outline=A((255, 230, 140), ca * glow * (1 - u)), w=5 * s)
        return (hx, hy, hr)
    return (x + 80 * s, y + 205 * s, 64 * s)

def hyoid_icon(d, x, y, r, kind="oval", a=1.0, col=(246, 236, 214), hole=(60, 46, 60)):
    """howler hyoid bulla, front view: a bell-shaped bone 'cup' with its opening (foramen) near the top:
    'oval' = sub-oval opening, 'semi' = semicircular opening."""
    sh = mix(col, (150, 130, 110), 0.45)
    d.poly([(x - r * 0.42, y - r * 0.9), (x + r * 0.42, y - r * 0.9), (x + r * 0.95, y + r * 0.3), (x + r * 0.7, y + r * 0.85),
            (x - r * 0.7, y + r * 0.85), (x - r * 0.95, y + r * 0.3)], A(sh, a))
    d.ell(x, y + r * 0.25, r * 0.9, r * 0.62, A(sh, a))
    d.poly([(x - r * 0.36, y - r * 0.84), (x + r * 0.36, y - r * 0.84), (x + r * 0.84, y + r * 0.3), (x + r * 0.6, y + r * 0.76),
            (x - r * 0.6, y + r * 0.76), (x - r * 0.84, y + r * 0.3)], A(col, a))
    d.ell(x, y + r * 0.25, r * 0.8, r * 0.52, A(col, a))
    d.ell(x - r * 0.42, y - r * 0.1, r * 0.12, r * 0.4, A(WHITE, a * 0.7))
    hy = y - r * 0.28
    if kind == "oval": d.ell(x, hy, r * 0.34, r * 0.24, A(hole, a))
    else: d.d.pieslice((P(x - r * 0.4), P(hy - r * 0.3), P(x + r * 0.4), P(hy + r * 0.5)), 180, 360, fill=A(hole, a))

# ---- Amazon map (rough, kid-level illustration; lon/lat -> screen) ----
SA = [(-77, 8.5), (-72, 12), (-67, 10.7), (-62, 10.5), (-60, 8.5), (-57, 6), (-52, 5), (-50, 1.5), (-48, -1), (-44, -2.5), (-39, -3.5), (-35, -5.5),
      (-35, -9), (-39, -13.5), (-39, -18), (-41, -22), (-45, -23.8), (-48.5, -26), (-49, -29), (-52, -32.5), (-55, -35), (-57.5, -36.5), (-57, -38.5),
      (-62, -39), (-65, -41), (-65, -45), (-67.5, -46.5), (-69, -51), (-68.5, -53.5), (-71, -54), (-74, -52), (-75, -47), (-73.5, -42), (-73.5, -37),
      (-71.5, -31), (-71.3, -25), (-70.2, -18.5), (-75, -15), (-77, -12), (-79.5, -7), (-81, -4.5), (-80, -1), (-80, 1), (-78.5, 2.8), (-77.3, 4), (-77.5, 7)]
AMZ = [(-76, 2), (-72, 4.5), (-66, 5.5), (-60, 5.5), (-54, 3.5), (-50, 0), (-47, -3), (-50, -8), (-54, -13.5), (-60, -15), (-66, -14), (-71, -12), (-75, -8), (-77.5, -3)]
RIVERS = {
    "amazon":  [(-73.5, -4.4), (-70, -4.2), (-67, -3.4), (-64.5, -3.6), (-62, -3.4), (-60, -3.1), (-58, -3.2), (-55, -2.4), (-52, -1.6), (-50, -0.5)],
    "negro":   [(-67.5, 1.5), (-66.8, 0.2), (-65, -0.4), (-63, -0.9), (-61.5, -1.6), (-60, -3.1)],
    "branco":  [(-60.7, 3.5), (-61.2, 1.5), (-61.6, -1.3)],
    "madeira": [(-65.3, -10.8), (-63.9, -8.8), (-62, -7.5), (-60.5, -5.5), (-58.8, -3.4)],
    "teles":   [(-55.5, -13), (-56, -10), (-57.5, -7.5), (-56.5, -5), (-55, -2.4)],
}
IROI = [(-66.6, 0.1), (-63, -0.9), (-61.6, -1.3), (-61.2, 1.5), (-62, 2.6), (-64.5, 2.2), (-66.3, 1.4)]
MATO = [(-59, -4.5), (-60.5, -5.5), (-62, -7.5), (-63.9, -8.8), (-63, -11.5), (-58, -13), (-55.6, -12.5), (-56, -10), (-57.5, -7.5), (-57, -5.5)]
class MapT:
    def __init__(s, lon0, lon1, lat0, lat1, x0, y0, x1, y1): s.v = (lon0, lon1, lat0, lat1, x0, y0, x1, y1)
    def __call__(s, lon, lat):
        lon0, lon1, lat0, lat1, x0, y0, x1, y1 = s.v
        return (x0 + (lon - lon0) / (lon1 - lon0) * (x1 - x0), y0 + (lat0 - lat) / (lat0 - lat1) * (y1 - y0))
def draw_map(d, M, a=1.0, sea=(30, 70, 110), land=(214, 196, 150), amz=(70, 150, 84), rivers=1.0, rcol=(110, 190, 255), rw=8, which=None):
    d.poly([M(*p) for p in SA], A(land, a))
    d.poly([M(*p) for p in AMZ], A(amz, a))
    for k, pts in RIVERS.items():
        if which is not None and k not in which: continue
        n = len(pts); m = rivers * (n - 1)
        q = [M(*p) for p in pts[:int(m) + 1]]
        if int(m) < n - 1 and m > 0:
            f = m - int(m); p0, p1 = M(*pts[int(m)]), M(*pts[int(m) + 1]); q.append((lerp(p0[0], p1[0], f), lerp(p0[1], p1[1], f)))
        if len(q) > 1: d.line(q, A(rcol, a), rw * (1.4 if k == "amazon" else 1.0))
def range_blob(d, M, pts, col, a):
    d.poly([M(*p) for p in pts], A(col, a))
def pin(d, x, y, col, a=1.0, s=1.0):
    d.circ(x, y - 40 * s, 26 * s, fill=A(col, a)); d.poly([(x - 20 * s, y - 28 * s), (x + 20 * s, y - 28 * s), (x, y)], A(col, a)); d.circ(x, y - 40 * s, 10 * s, fill=A(WHITE, a))

def tube(d, x, y, s, a=1.0, col=(255, 120, 120), fill=0.7, cap=(80, 140, 230)):
    d.rect(x - 18 * s, y - 70 * s, x + 18 * s, y + 60 * s, fill=A((230, 240, 250), a * 0.85), r=18 * s)
    d.rect(x - 14 * s, y + 60 * s - 120 * s * fill, x + 14 * s, y + 56 * s, fill=A(col, a), r=14 * s)
    d.rect(x - 22 * s, y - 84 * s, x + 22 * s, y - 64 * s, fill=A(cap, a), r=6 * s)
    d.rect(x - 9 * s, y - 60 * s, x - 4 * s, y + 30 * s, fill=A(WHITE, a * 0.6), r=2 * s)

def helix(d, x0, y0, x1, y1, t, a=1.0, amp=40, turns=4, c1=(90, 220, 240), c2=(255, 140, 200), w=8, prog=1.0):
    L = math.hypot(x1 - x0, y1 - y0) + 1e-6; ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    n = 80; m = max(2, int(n * prog))
    for k in range(0, m, 3):
        u = k / n; ph = u * turns * 2 * math.pi + t * 3
        bx, by = x0 + ux * L * u, y0 + uy * L * u
        p1 = (bx + nx * amp * math.sin(ph), by + ny * amp * math.sin(ph)); p2 = (bx - nx * amp * math.sin(ph), by - ny * amp * math.sin(ph))
        d.line([p1, p2], A((240, 240, 255), a * 0.5), 3)
    for sgn, c in ((1, c1), (-1, c2)):
        pts = []
        for k in range(m):
            u = k / n; ph = u * turns * 2 * math.pi + t * 3
            bx, by = x0 + ux * L * u, y0 + uy * L * u
            pts.append((bx + sgn * nx * amp * math.sin(ph), by + sgn * ny * amp * math.sin(ph)))
        if len(pts) > 1: d.line(pts, A(c, a), w)
