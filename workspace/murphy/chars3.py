# Murphy film — new characters & props: Audie Murphy face (young, no mustache, M1 helmet), M10 tank destroyer,
# continuous flames/smoke/embers, German tanks (front), infantry (front, walking), Murphy silhouettes. Rim light, NO dark outlines.
from chars2 import *

FIRE = (255, 104, 36); FIRE_L = (255, 196, 96); FIRE_C = (255, 240, 190)
SNOW = (92, 100, 112); SNOW_L = (176, 184, 196)
M1C = (80, 86, 58); M1H = (150, 156, 112)
HULL = (72, 76, 52); HULL_D = (44, 46, 32); TRACK = (30, 30, 28)
GERV = (78, 82, 84); GERV_D = (46, 50, 52)

# ---------------------------------------------------------------- M1 helmet
def m1_front(d, cx, cy, w, key=AMBER, a=1.0):
    """front view; cy = brim line, w = helmet width."""
    dome = ellpts(cx, cy, 0.5 * w, 0.6 * w, math.pi, 2 * math.pi, 22)
    d.poly(dome, A(mix(M1C, key, 0.55), a))
    d.poly([(x + 0.03 * w, y + 0.015 * w) for x, y in dome], A(M1C, a))
    d.poly(ellpts(cx - 0.12 * w, cy - 0.36 * w, 0.2 * w, 0.12 * w, math.pi * 1.05, math.pi * 1.7, 10) + [(cx - 0.1 * w, cy - 0.3 * w)], A(M1H, 0.7 * a))
    d.ell(cx, cy, 0.54 * w, 0.075 * w, fill=A(mix(M1C, key, 0.45), a))           # brim
    d.ell(cx + 0.01 * w, cy + 0.02 * w, 0.5 * w, 0.05 * w, fill=A((34, 36, 24), a))  # under-brim

def m1_side(d, m, cx, cy, w, key=AMBER, a=1.0):
    dome = ellpts(cx, cy, 0.5 * w, 0.52 * w, math.pi, 2 * math.pi, 18)
    d.poly(m(dome), A(mix(M1C, key, 0.5), a))
    d.poly(m([(x - 0.03 * w, y + 0.03 * w) for x, y in dome]), A(M1C, a))
    d.poly(m(ellpts(cx, cy, 0.56 * w, 0.06 * w, 0, 2 * math.pi, 18)), A(mix(M1C, key, 0.35), a))
    d.poly(m(ellpts(cx + 0.1 * w, cy - 0.3 * w, 0.18 * w, 0.09 * w, math.pi * 1.1, math.pi * 1.8, 8)), A(M1H, 0.6 * a))

# ---------------------------------------------------------------- Murphy close-up face (young, round, no mustache, M1)
def murphy_face(img, d, cx, cy, h, t, key=AMBER, rim=COLD, squint=0.2, a=1.0, blink=False, worry=0.0, shoulders=True, look=0.0):
    sh = spline([(-0.25, 0.5), (-0.9, 0.82), (-1.3, 1.35), (-1.45, 2.2), (1.45, 2.2), (1.3, 1.35), (0.9, 0.82), (0.25, 0.5)], n=6)
    if shoulders:
        rimpoly(d, xf(sh, cx, cy, h), (56, 54, 38), mix(OD_L, key, 0.5), 0.03 * h, 0.02 * h, a)
        d.poly(xf([(-0.3, 0.55), (0, 0.92), (0.3, 0.55), (0.25, 0.75), (0, 1.02), (-0.25, 0.75)], cx, cy, h), A((42, 40, 28), a))
        d.rect(cx - 0.19 * h, cy + 0.3 * h, cx + 0.19 * h, cy + 0.74 * h, fill=A(mix(SKIN_D, SKIN_M, 0.3), a))
        d.poly(xf([(-0.19, 0.52), (0.19, 0.4), (0.19, 0.74), (-0.19, 0.74)], cx, cy, h), A((60, 36, 32), 0.5 * a))
        # 2nd Lt gold bar on the collar (rank)
        d.rect(cx - 0.62 * h, cy + 0.92 * h, cx - 0.44 * h, cy + 0.97 * h, fill=A((236, 196, 90), a), r=0.02 * h)
    for sgn, col in ((-1, SKIN_M), (1, mix(SKIN_D, rim, 0.15))):
        d.ell(cx + sgn * 0.385 * h, cy - 0.02 * h, 0.065 * h, 0.115 * h, fill=A(col, a))
        d.ell(cx + sgn * 0.39 * h, cy - 0.02 * h, 0.03 * h, 0.066 * h, fill=A(mix(col, SKIN_D, 0.5), a))
    # unbuckled chin straps hanging
    for sgn in (-1, 1):
        d.line([(cx + sgn * 0.43 * h, cy - 0.4 * h), (cx + sgn * 0.42 * h, cy + 0.1 * h), (cx + sgn * 0.36 * h, cy + 0.42 * h)], A((92, 84, 54), 0.9 * a), 0.03 * h)
    FACEY = [(0, -0.6), (-0.33, -0.48), (-0.38, -0.12), (-0.35, 0.18), (-0.27, 0.37), (-0.13, 0.5), (0, 0.53), (0.13, 0.5), (0.27, 0.37), (0.35, 0.18), (0.38, -0.12), (0.33, -0.48)]
    fp = spline(FACEY, n=8)
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).polygon([(P(x), P(y)) for x, y in xf(fp, cx, cy, h)], fill=255)
    xs = (np.arange(img.size[0]) / S - cx) / h
    k = np.clip(0.5 - (xs - 0.08) / 0.24, 0, 1)[None, :, None]; k = k * k * (3 - 2 * k)
    lit = np.array(mix(SKIN, key, 0.14), np.float32); sh_ = np.array(mix(SKIN_D, (90, 70, 90), 0.15), np.float32)
    row = (sh_ + (lit - sh_) * k).astype(np.uint8)
    y0, y1 = int(P(cy - 0.62 * h)), int(P(cy + 0.58 * h))
    band = Image.fromarray(np.repeat(row, max(1, y1 - y0), 0), "RGB")
    if a < 1: m = Image.eval(m, lambda v: int(v * a))
    img.paste(band, (0, y0), m.crop((0, y0, img.size[0], y0 + band.height)))
    rp = xf(fp, cx, cy, h)
    rimm = Image.new("L", img.size, 0); ImageDraw.Draw(rimm).polygon([(P(x), P(y)) for x, y in rp], fill=255)
    inner = Image.new("L", img.size, 0); ImageDraw.Draw(inner).polygon([(P(x - 0.035 * h), P(y)) for x, y in rp], fill=255)
    rimm = ImageChops.subtract(rimm, inner); rimm = Image.eval(rimm, lambda v: int(v * 0.8 * a)); img.paste(rim, (0, 0), rimm)
    # youthful round cheeks (lit blush), soft jaw shade
    d.ell(cx - 0.21 * h, cy + 0.17 * h, 0.1 * h, 0.065 * h, fill=A(mix(SKIN, (230, 120, 100), 0.4), 0.35 * a))
    d.poly(xf(spline([(0.1, 0.46), (0.25, 0.35), (0.33, 0.18), (0.29, 0.38), (0.14, 0.5)], n=5), cx, cy, h), A((80, 46, 42), 0.35 * a))
    # wavy hair lock under the helmet front
    d.poly(xf(spline([(-0.3, -0.44), (-0.12, -0.47), (0.05, -0.45), (0.2, -0.47), (0.3, -0.42), (0.12, -0.36), (-0.02, -0.39), (-0.16, -0.35)], n=4), cx, cy, h), A(mix(HAIR, (60, 30, 18), 0.45), a))
    d.poly(xf(spline([(-0.16, -0.43), (-0.04, -0.45), (-0.08, -0.4)], n=4), cx, cy, h), A(mix(HAIR, AMBER_L, 0.3), 0.8 * a))
    # eyes (big, clear, thick lids) — face is always in focus
    lk = look * 0.02 * h
    for sgn in (-1, 1):
        ex, ey = cx + sgn * 0.15 * h, cy - 0.08 * h; lit_side = sgn < 0
        d.ell(ex, ey - 0.005 * h, 0.1 * h, 0.06 * h, fill=A((96, 56, 46) if lit_side else (62, 38, 36), 0.4 * a))
        oh = 0.036 * h * (1 - squint) if not blink else 0.004 * h
        eye = spline([(-0.075, 0.0), (-0.035, -oh / h), (0.03, -oh / h * 1.05), (0.075, 0.003), (0.02, oh / h * 0.7), (-0.04, oh / h * 0.65)], n=6)
        ep = xf(eye, ex, ey, h, sx=h * (1 if sgn < 0 else -1))
        d.poly(ep, A((228, 220, 206) if lit_side else (160, 150, 144), a))
        if not blink:
            ir = 0.028 * h
            d.circ(ex + lk, ey + 0.002 * h, ir, fill=A((92, 120, 150) if lit_side else (64, 86, 104), a))
            d.circ(ex + lk, ey + 0.002 * h, ir * 0.48, fill=A(INK, a))
            d.circ(ex + lk - ir * 0.35, ey - ir * 0.35, ir * 0.3, fill=A(WHITE, a))
        d.line(spline([ep[0], ep[2], ep[4], ep[6], ep[9], ep[12]], closed=False, n=4), A((40, 22, 18), a), 0.02 * h)
        by = ey - 0.075 * h
        w_ = worry
        bp = spline([(-0.1 * sgn, 0.014 - 0.03 * w_), (-0.02 * sgn, -0.02 - 0.02 * w_), (0.11 * sgn, -0.006 + 0.012 * w_), (0.12 * sgn, 0.018 + 0.012 * w_), (-0.02 * sgn, 0.01 - 0.01 * w_), (-0.1 * sgn, 0.04 - 0.03 * w_)], n=4)
        d.poly(xf(bp, ex, by, h), A(mix(HAIR, (60, 26, 16), 0.3 if lit_side else 0.6), a))
    # small young nose
    d.poly(xf(spline([(0.02, -0.04), (0.05, 0.08), (0.065, 0.15), (0.025, 0.17)], n=5), cx, cy, h), A((100, 60, 48), 0.5 * a))
    d.ell(cx - 0.015 * h, cy + 0.135 * h, 0.05 * h, 0.038 * h, fill=A(mix(SKIN, key, 0.25), 0.8 * a))
    d.circ(cx - 0.03 * h, cy + 0.125 * h, 0.011 * h, fill=A((255, 232, 204), 0.7 * a))
    for sgn in (-1, 1): d.ell(cx + sgn * 0.035 * h, cy + 0.165 * h, 0.019 * h, 0.01 * h, fill=A((64, 32, 28), a))
    # mouth: firm, slightly full lips (young)
    my = cy + 0.28 * h
    if worry > 0.3:
        d.line(spline([(cx - 0.075 * h, my + 0.008 * h), (cx, my - 0.004 * h), (cx + 0.075 * h, my + 0.01 * h)], closed=False, n=4), A((76, 30, 28), a), 0.02 * h)
    else:
        d.line(spline([(cx - 0.08 * h, my), (cx, my + 0.008 * h), (cx + 0.08 * h, my - 0.004 * h)], closed=False, n=4), A((76, 30, 28), a), 0.02 * h)
    d.ell(cx - 0.01 * h, my + 0.035 * h, 0.055 * h, 0.018 * h, fill=A(mix(SKIN, (210, 110, 96), 0.35), 0.6 * a))
    d.ell(cx, cy + 0.42 * h, 0.065 * h, 0.028 * h, fill=A(SKIN_M, 0.3 * a))
    m1_front(d, cx, cy - 0.4 * h, 0.95 * h, key, a)

# ---------------------------------------------------------------- continuous fire / smoke / embers (no per-frame randomness)
def flames(img, d, x, y, w, hgt, t, a=1.0, glow_on=True, seed=0):
    if a <= 0.01: return
    if glow_on: glow(img, lambda g: g.ell(x, y - hgt * 0.35, w * 0.8, hgt * 0.6, fill=A(FIRE, 0.9 * a)), blur=70)
    n = 9
    for layer, (col, sc) in enumerate(((FIRE, 1.0), (FIRE_L, 0.68), (FIRE_C, 0.38))):
        for i in range(n):
            u = (i + 0.5) / n - 0.5
            ph = hsh(i, 50 + seed) * 6.28
            hh = hgt * sc * (0.45 + 0.55 * (1 - abs(u) * 1.6)) * (0.75 + 0.25 * math.sin(t * 7.3 + ph) * math.sin(t * 3.1 + ph * 1.7))
            bx = x + u * w * sc; bw = w / n * 1.5 * sc
            sway = math.sin(t * 4.0 + ph) * bw * 0.6
            pts = spline([(bx - bw, y), (bx - bw * 0.5, y - hh * 0.45), (bx + sway, y - hh), (bx + bw * 0.5, y - hh * 0.45), (bx + bw, y)], closed=True, n=5)
            d.poly(pts, A(col, a * (0.9 if layer == 0 else 1)))

def smoke(img, d, x, y, w, rise, t, a=1.0, n=14, seed=0, col=(36, 34, 36), lit=FIRE):
    for i in range(n):
        u = (t * 0.22 + i / n + hsh(i, 60 + seed) * 0.05) % 1.0
        px = x + (hsh(i, 61 + seed) - 0.5) * w * 0.6 + math.sin(t * 0.7 + i) * 30 * u + u * w * 0.5
        py = y - u * rise; r = w * (0.25 + 0.6 * u)
        al = math.sin(math.pi * u) ** 1.2 * 0.55 * a
        d.circ(px, py, r, fill=A(mix(lit, col, min(1, 0.35 + u * 1.5)), al))

def embers(d, x, y, w, rise, t, a=1.0, n=18, seed=0):
    for i in range(n):
        u = (t * (0.35 + 0.2 * hsh(i, 70 + seed)) + hsh(i, 71 + seed)) % 1.0
        px = x + (hsh(i, 72 + seed) - 0.5) * w + math.sin(t * 2 + i * 1.3) * 20
        py = y - u * rise
        d.circ(px, py, 2.5 + 2.5 * hsh(i, 73 + seed), fill=A(FIRE_L, math.sin(math.pi * u) * a))

def snowfall(d, t, a=0.6, n=60, seed=0, x0=0, x1=1080, y0=0, y1=1920, speed=60):
    for i in range(n):
        u = (t * speed / (y1 - y0) * (0.6 + 0.6 * hsh(i, 80 + seed)) + hsh(i, 81 + seed)) % 1.0
        px = x0 + (x1 - x0) * hsh(i, 82 + seed) + math.sin(t * 0.8 + i) * 18
        py = y0 + (y1 - y0) * u
        d.circ(px, py, 1.6 + 2.6 * hsh(i, 83 + seed), fill=A(SNOW_L, a * (0.4 + 0.6 * hsh(i, 84 + seed)) * min(1, 6 * min(u, 1 - u))))

def pine(d, x, y, h, col, a=1.0, lit=None):
    pts = [(x, y - h)]
    for k in range(5):
        yy = y - h + h * (k + 1) / 5.2; ww = h * 0.075 * (k + 1)
        pts = [(x - ww, yy)] + pts + [(x + ww, yy)]
    d.poly(pts + [(x + h * 0.04, y), (x - h * 0.04, y)], A(col, a))
    if lit: d.poly([(x, y - h), (x + h * 0.1, y - h * 0.75), (x + h * 0.02, y - h * 0.8)], A(lit, a * 0.6))

def woods(d, y, col, seed=0, a=1.0, x0=-40, x1=1120, hmin=200, hmax=340, lit=None):
    r = random.Random(seed); x = x0
    while x < x1:
        pine(d, x, y, r.uniform(hmin, hmax), col, a, lit); x += r.uniform(40, 80)

# ---------------------------------------------------------------- M10 tank destroyer (side view, faces RIGHT when flip=1)
def m10(img, d, x, y, s, t, key=FIRE, a=1.0, flip=1, star=True):
    """(x,y) = ground centre, s = scale (vehicle ~ 6 s long). Returns Map; deck point m.p(-1.4,-1.8); MG point m.p(-0.9,-3.0)."""
    m = Map(x, y, s, 0.0, flip=flip)
    lit = mix(HULL, key, 0.5)
    d.poly(m(spline([(-2.95, -0.5), (-2.6, -0.98), (2.6, -0.98), (3.0, -0.5), (2.6, 0.0), (-2.6, 0.0)], n=3)), A(TRACK, a))
    for i in range(6):
        wx = -2.1 + i * 0.84
        d.poly(m(ellpts(wx, -0.42, 0.34, 0.34, n=18)), A((50, 50, 44), a)); d.poly(m(ellpts(wx, -0.42, 0.16, 0.16, n=12)), A((28, 28, 26), a))
        d.poly(m(ellpts(wx - 0.06, -0.48, 0.3, 0.3, math.pi * 1.1, math.pi * 1.6, 6) + [(wx - 0.05, -0.42)]), A(mix((90, 90, 76), key, 0.4), 0.7 * a))
    hull = [(-3.05, -1.0), (2.55, -1.0), (3.15, -1.2), (2.45, -1.8), (-2.6, -1.8), (-3.1, -1.25)]
    d.poly(m(hull), A(lit, a)); d.poly(m([(px, py + 0.06) for px, py in hull]), A(HULL, a))
    d.poly(m([(-2.6, -1.8), (2.45, -1.8), (2.3, -1.72), (-2.5, -1.72)]), A(mix(lit, (255, 230, 180), 0.2), a))
    tur = [(-1.35, -1.8), (1.15, -1.8), (0.95, -2.6), (-0.95, -2.6), (-1.4, -2.2)]
    d.poly(m(tur), A(lit, a)); d.poly(m([(px + 0.05, py + 0.05) for px, py in tur]), A(mix(HULL, HULL_D, 0.3), a))
    d.poly(m([(-0.95, -2.6), (0.95, -2.6), (0.9, -2.52), (-0.92, -2.52)]), A((24, 24, 20), a))   # open top lip
    d.line(m([(1.0, -2.2), (4.5, -2.28)]), A(HULL_D, a), 0.17 * s); d.line(m([(1.0, -2.25), (4.5, -2.33)]), A(lit, 0.6 * a), 0.05 * s)
    d.poly(m([(4.3, -2.4), (4.6, -2.42), (4.6, -2.13), (4.3, -2.13)]), A(HULL_D, a))
    # .50 cal on the turret rear
    d.line(m([(-1.0, -2.6), (-1.0, -3.0)]), A((40, 40, 38), a), 0.07 * s)
    d.line(m([(-1.25, -3.02), (0.55, -3.1)]), A((46, 48, 48), a), 0.09 * s); d.line(m([(-1.25, -3.06), (0.55, -3.14)]), A(mix((120, 120, 120), key, 0.4), a), 0.025 * s)
    if star:
        cxs, cys = m.p(-1.5, -1.38); rr = 0.3 * s
        st = [(cxs + math.cos(-math.pi / 2 + k * math.pi / 5) * (rr if k % 2 == 0 else rr * 0.4), cys + math.sin(-math.pi / 2 + k * math.pi / 5) * (rr if k % 2 == 0 else rr * 0.4)) for k in range(10)]
        d.poly(st, A((214, 210, 196), 0.75 * a))
    return m

# ---------------------------------------------------------------- Murphy silhouette (front, small, seen from the German side) firing the MG
def murphy_sil(img, d, x, y, h, t, flash=0.0, rim=FIRE_L, a=1.0):
    """(x,y) = feet; h = figure height."""
    u = h / 10
    body = spline([(-1.2, -6.4), (1.2, -6.4), (1.6, -3.6), (1.1, -3.4), (0.9, 0.0), (0.2, 0.0), (0.0, -2.6), (-0.2, 0.0), (-0.9, 0.0), (-1.1, -3.4), (-1.6, -3.6)], n=3)
    pts = xf(body, x, y, u); rimpoly(d, pts, (16, 14, 14), rim, 0, 0.12 * u, a)
    d.circ(x, y - 7.3 * u, 0.95 * u, fill=A(rim, a)); d.circ(x, y - 7.25 * u, 0.85 * u, fill=A((18, 16, 16), a))
    hp = ellpts(x, y - 7.7 * u, 1.35 * u, 1.3 * u, math.pi, 2 * math.pi, 14)
    d.poly(hp, A(rim, a)); d.poly([(px, py + 0.12 * u) for px, py in hp], A((22, 20, 18), a))
    d.ell(x, y - 7.62 * u, 1.45 * u, 0.22 * u, fill=A((22, 20, 18), a))
    # MG pointing at us: dark block + muzzle
    d.rect(x - 2.3 * u, y - 5.3 * u, x + 2.3 * u, y - 4.3 * u, fill=A((24, 22, 20), a), r=0.3 * u)
    d.circ(x + 1.6 * u, y - 4.8 * u, 0.55 * u, fill=A((10, 10, 10), a))
    if flash > 0.01: glow(img, lambda g: g.circ(x + 1.6 * u, y - 4.8 * u, (1.5 + 2.5 * flash) * u, fill=A(FIRE_C, flash)), blur=max(8, 3 * u))

# ---------------------------------------------------------------- German tank, front / rear view (no insignia)
def ger_tank(d, x, y, s, t, key=FIRE_L, a=1.0, rear=False):
    """(x,y) = ground centre, s = half-width."""
    if a <= 0.01: return
    lit = mix(GERV, key, 0.35)
    for sg in (-1, 1):
        d.rect(x + sg * 0.62 * s - 0.36 * s, y - 0.7 * s, x + sg * 0.62 * s + 0.36 * s, y, fill=A(TRACK, a), r=0.08 * s)
        d.rect(x + sg * 0.62 * s - 0.36 * s, y - 0.7 * s, x + sg * 0.62 * s + 0.36 * s, y - 0.62 * s, fill=A(mix(TRACK, key, 0.3), a))
    d.poly([(x - 0.95 * s, y - 0.62 * s), (x + 0.95 * s, y - 0.62 * s), (x + 0.82 * s, y - 1.0 * s), (x - 0.82 * s, y - 1.0 * s)], A(lit, a))
    d.poly([(x - 0.9 * s, y - 0.6 * s), (x + 0.9 * s, y - 0.6 * s), (x + 0.82 * s, y - 0.9 * s), (x - 0.82 * s, y - 0.9 * s)], A(GERV, a))
    d.poly([(x - 0.5 * s, y - 1.0 * s), (x + 0.5 * s, y - 1.0 * s), (x + 0.4 * s, y - 1.42 * s), (x - 0.4 * s, y - 1.42 * s)], A(lit, a))
    d.poly([(x - 0.46 * s, y - 1.0 * s), (x + 0.46 * s, y - 1.0 * s), (x + 0.38 * s, y - 1.36 * s), (x - 0.38 * s, y - 1.36 * s)], A(GERV_D, a))
    if not rear:
        d.circ(x, y - 1.18 * s, 0.13 * s, fill=A((30, 32, 32), a)); d.circ(x, y - 1.18 * s, 0.07 * s, fill=A((6, 6, 6), a))
    else:
        d.rect(x - 0.3 * s, y - 0.86 * s, x - 0.12 * s, y - 0.76 * s, fill=A((40, 40, 40), a))
        d.rect(x + 0.12 * s, y - 0.86 * s, x + 0.3 * s, y - 0.76 * s, fill=A((40, 40, 40), a))

# ---------------------------------------------------------------- infantry, front, walking (simple full figure)
def inf_front(d, x, y, h, t, ph=0.0, key=COLD, a=1.0, body=FELD, back=False, step=None):
    """(x,y) = feet; h = figure height. step: optional 0..1 phase override."""
    if a <= 0.01: return
    u = h / 10; s = math.sin(t * 6 + ph) if step is None else math.sin(step * 2 * math.pi)
    for sg in (-1, 1):
        d.line([(x + sg * 0.6 * u, y - 4.2 * u), (x + sg * 0.7 * u, y - 2 * u + abs(s) * 0.4 * u * (sg * s > 0)), (x + sg * 0.75 * u, y - (0.6 * u if sg * s > 0 else 0))], A(mix(body, (0, 0, 0), 0.25), a), 1.1 * u)
    tor = spline([(-1.3, -7.0), (1.3, -7.0), (1.5, -4.0), (-1.5, -4.0)], n=3)
    rimpoly(d, xf(tor, x, y, u), body, mix(body, key, 0.6), 0.1 * u, 0.05 * u, a)
    d.line([(x - 2.0 * u, y - 4.2 * u), (x + 1.8 * u, y - 7.6 * u)], A((70, 52, 36), a), 0.35 * u)   # rifle across chest
    d.circ(x, y - 7.8 * u, 0.85 * u, fill=A(mix(SKIN_D, (40, 40, 44), 0.5 if back else 0.2), a))
    hp = xf(STAHL, x, y - 8.25 * u, 2.2 * u); rimpoly(d, hp, HELM, mix(HELM, key, 0.6), 0, 0.08 * u, a)
