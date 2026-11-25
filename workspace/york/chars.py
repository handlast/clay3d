# York film characters: German soldiers (Stahlhelm), Alvin York close-up / prone / profile. Rim light, no outlines.
from base import *

# ---------------------------------------------------------------- German soldier (front, chest-up)
STAHL = spline([(-0.43, 0.02), (-0.44, -0.2), (-0.32, -0.44), (0.0, -0.53), (0.32, -0.44), (0.44, -0.2), (0.43, 0.02)], closed=False, n=8) + \
        [(0.47, 0.06), (0.50, 0.10), (0.58, 0.30), (0.42, 0.33), (0.38, 0.12), (-0.38, 0.12), (-0.42, 0.33), (-0.58, 0.30), (-0.50, 0.10), (-0.47, 0.06)]
def german(d, x, y, sc, t, pose="stand", hands=0.0, face=0.0, rim=COLD, rdx=-1, fear=0.0, seed=0, a=1.0, body=FELD, helm=HELM):
    """x,y = neck base; sc = head height in px. hands 0..1 raises arms; face 0..1 how lit/visible the face is.
    rdx: rim side (-1 light from left). fear 0..1: wide eyes + sweat."""
    if a <= 0.01: return
    h = sc; bob = math.sin(t * 2.1 + seed) * 0.01 * h
    y = y + bob; ox = -rdx * 0.035 * h  # body shift away from light => rim crescent on light side
    # arms (behind torso when raised)
    if hands > 0.01:
        for sgn in (-1, 1):
            k = E.ease_out_back(cl(hands), 1.2)
            sh = (x + sgn * 0.62 * h, y + 0.35 * h)
            el = (x + sgn * lerp(0.95, 0.85, k) * h, y + lerp(1.0, -0.2, k) * h)
            hd = (x + sgn * lerp(0.75, 0.80, k) * h, y + lerp(1.4, -0.95, k) * h)
            for c, o in ((rim, 0), (body, ox)):
                d.line([(sh[0] + o, sh[1]), (el[0] + o, el[1]), (hd[0] + o, hd[1])], A(c, a), 0.36 * h)
            d.circ(hd[0], hd[1], 0.19 * h, fill=A(mix(SKIN_D, rim, 0.25), a))
            d.circ(hd[0] + ox * 0.5, hd[1] + 0.02 * h, 0.165 * h, fill=A(mix(SKIN_D, (40, 40, 44), 0.4), a))
    # torso/shoulders
    tor = spline([(-0.2, 0.0), (-0.62, 0.22), (-0.8, 0.6), (-0.86, 1.6), (0.86, 1.6), (0.8, 0.6), (0.62, 0.22), (0.2, 0.0)], n=6)
    rimpoly(d, xf(tor, x, y, h), body, rim, ox, 0.01 * h, a)
    d.poly(xf([(-0.22, 0.02), (0.0, 0.32), (0.22, 0.02)], x + ox, y, h), A(mix(body, (20, 24, 24), 0.35), a))  # collar shadow
    # neck + face
    d.rect(x - 0.15 * h + ox, y - 0.25 * h, x + 0.15 * h + ox, y + 0.1 * h, fill=A(mix(SKIN_D, (30, 30, 34), 0.5), a))
    fpts = spline([(-0.3, -0.35), (-0.31, -0.05), (-0.22, 0.2), (0.0, 0.3), (0.22, 0.2), (0.31, -0.05), (0.3, -0.35)], n=6)
    fx, fy = x, y - 0.42 * h
    skin = mix(mix(SKIN_D, (36, 38, 44), 0.55), mix(SKIN_M, rim, 0.15), face)
    rimpoly(d, xf(fpts, fx, fy, h), skin, mix(skin, rim, 0.6), ox * 0.6, 0, a)
    # eyes (deep under the brim) — wide when afraid
    ew = 0.075 * h; eh = lerp(0.018, 0.05, fear) * h
    for sgn in (-1, 1):
        ex, ey = fx + sgn * 0.13 * h + ox * 0.3, fy - 0.13 * h
        wcol = mix((70, 70, 72), (214, 208, 196), 0.35 + 0.65 * max(face, fear))
        d.ell(ex, ey, ew, eh, fill=A(wcol, a))
        d.circ(ex + rdx * -0.01 * h, ey, lerp(0.022, 0.016, fear) * h, fill=A(INK, a))
        if face + fear > 0.3: d.circ(ex - 0.01 * h, ey - 0.008 * h, 0.006 * h, fill=A(WHITE, a * 0.9))
        # brow: raised when afraid, low/flat when cocky
        by = ey - lerp(0.045, 0.085, fear) * h
        d.line([(ex - sgn * 0.07 * h, by + lerp(0.0, -0.01, fear) * h), (ex + sgn * 0.08 * h, by + lerp(0.02, 0.025, fear) * h)], A(mix(INK, skin, 0.3), a), 0.025 * h)
    # mouth: grin (cocky) or small open (fear)
    mx, my = fx + ox * 0.3, fy + 0.12 * h
    if fear > 0.3: d.ell(mx, my, 0.05 * h, 0.04 * h * fear, fill=A(INK, a))
    elif pose == "cocky": d.line(spline([(mx - 0.1 * h, my - 0.01 * h), (mx, my + 0.03 * h), (mx + 0.11 * h, my - 0.03 * h)], closed=False, n=5), A(INK, a * 0.85), 0.02 * h)
    else: d.line([(mx - 0.07 * h, my), (mx + 0.07 * h, my)], A(INK, a * 0.7), 0.018 * h)
    if fear > 0.4:  # sweat drops sliding (continuous, per-soldier phase)
        for j in range(2):
            u = ((t * 0.7 + j * 0.5 + seed * 0.37) % 1.0)
            sx, sy = fx + (0.24 + 0.05 * j) * h * (-1 if j else 1), fy - 0.15 * h + u * 0.3 * h
            d.ell(sx, sy, 0.02 * h, 0.032 * h, fill=A((170, 210, 230), a * (fear - 0.4) * 1.6 * math.sin(math.pi * u)))
    # Stahlhelm: rim side lit, brim shadow on face
    if helm is None: return
    hp = xf(STAHL, fx, fy - 0.33 * h, h * 1.05)
    rimpoly(d, hp, helm, mix(helm, rim, 0.75), ox * 0.8, 0.012 * h, a)
    d.poly(xf([(-0.36, 0.11), (0.36, 0.11), (0.3, 0.2), (-0.3, 0.2)], fx + ox * 0.6, fy - 0.33 * h, h * 1.05), A((14, 16, 18), 0.45 * a))

def german_back(d, x, y, sc, t, rim=AMBER, a=1.0, lean=0.0, seed=0):
    """Seen from behind (enemy POV): helmet + shoulders silhouette, rim light from the valley ahead."""
    h = sc; y += math.sin(t * 1.7 + seed) * 0.008 * h
    tor = spline([(-0.25, 0.0), (-0.75, 0.25), (-0.95, 0.8), (-1.0, 1.9), (1.0, 1.9), (0.95, 0.8), (0.75, 0.25), (0.25, 0.0)], n=6)
    tp = xf(tor, x, y, h, rot=lean); rimpoly(d, tp, (24, 28, 28), rim, 0, 0.03 * h, a)
    d.rect(x - 0.16 * h, y - 0.3 * h, x + 0.16 * h, y + 0.1 * h, fill=A((30, 30, 32), a))
    hp = xf(STAHL, x, y - 0.55 * h, h * 1.15, rot=lean); rimpoly(d, hp, (30, 36, 36), rim, 0, 0.025 * h, a)

# ---------------------------------------------------------------- Alvin York close-up face (front, 3/4 light)
def _facemask(cx, cy, h, pts):
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon([(P(x), P(y)) for x, y in xf(pts, cx, cy, h)], fill=255); return m
FACE = [(0, -0.6), (-0.33, -0.48), (-0.39, -0.12), (-0.36, 0.2), (-0.27, 0.4), (-0.12, 0.53), (0, 0.56), (0.12, 0.53), (0.27, 0.4), (0.36, 0.2), (0.39, -0.12), (0.33, -0.48)]
def york_face(img, d, cx, cy, h, t, key=AMBER, rim=COLD, look=0.0, squint=0.25, a=1.0, blink=False, shoulders=True, closed=()):
    """Big readable face. key light from LEFT (amber), cool rim on the right. Facial lines may be dark (allowed)."""
    # shoulders / uniform
    sh = spline([(-0.25, 0.5), (-0.95, 0.85), (-1.35, 1.4), (-1.5, 2.2), (1.5, 2.2), (1.35, 1.4), (0.95, 0.85), (0.25, 0.5)], n=6)
    if shoulders: rimpoly(d, xf(sh, cx, cy, h), (52, 50, 34), mix(OD_L, key, 0.5), 0.03 * h, 0.02 * h, a)
    if shoulders: d.poly(xf([(-0.3, 0.55), (0, 0.95), (0.3, 0.55), (0.25, 0.75), (0, 1.05), (-0.25, 0.75)], cx, cy, h), A((40, 38, 26), a))  # collar
    if shoulders: d.rect(cx - 0.2 * h, cy + 0.3 * h, cx + 0.2 * h, cy + 0.75 * h, fill=A(mix(SKIN_D, SKIN_M, 0.3), a))  # neck
    if shoulders: d.poly(xf([(-0.2, 0.55), (0.2, 0.42), (0.2, 0.75), (-0.2, 0.75)], cx, cy, h), A((60, 36, 32), 0.55 * a))  # neck shadow under jaw
    # ears + sideburn hair
    for sgn, col in ((-1, SKIN_M), (1, mix(SKIN_D, rim, 0.15))):
        d.ell(cx + sgn * 0.39 * h, cy - 0.02 * h, 0.065 * h, 0.12 * h, fill=A(col, a))
        d.ell(cx + sgn * 0.395 * h, cy - 0.02 * h, 0.03 * h, 0.07 * h, fill=A(mix(col, SKIN_D, 0.5), a))
        d.poly(xf([(sgn * 0.3, -0.42), (sgn * 0.39, -0.4), (sgn * 0.38, -0.12), (sgn * 0.33, -0.12)], cx, cy, h), A(mix(HAIR, (40, 20, 14), 0.3 if sgn < 0 else 0.6), a))
    # chin strap (behind the face: shows along the jaw and under the chin)
    d.line([(cx - 0.41 * h, cy - 0.36 * h), (cx - 0.37 * h, cy + 0.25 * h), (cx - 0.15 * h, cy + 0.6 * h), (cx + 0.15 * h, cy + 0.6 * h), (cx + 0.37 * h, cy + 0.25 * h), (cx + 0.41 * h, cy - 0.36 * h)], A((84, 60, 38), 0.9 * a), 0.026 * h)
    # face base: horizontal key->shadow gradient, through a face mask (soft terminator)
    m = _facemask(cx, cy, h, spline(FACE, n=8))
    xs = (np.arange(W) / S - cx) / h
    k = np.clip(0.5 - (xs - 0.06) / 0.22, 0, 1)[None, :, None]; k = k * k * (3 - 2 * k)
    lit = np.array(mix(SKIN, key, 0.12), np.float32); sh_ = np.array(SKIN_D, np.float32)
    row = (sh_ + (lit - sh_) * k).astype(np.uint8)
    y0, y1 = int(P(cy - 0.62 * h)), int(P(cy + 0.6 * h))
    band = Image.fromarray(np.repeat(row, max(1, y1 - y0), 0), "RGB")
    if a < 1: m = Image.eval(m, lambda v: int(v * a))
    img.paste(band, (0, y0), m.crop((0, y0, W, y0 + band.height)))
    # cool rim on right edge of face
    rp = xf(spline(FACE, n=8), cx, cy, h)
    rimm = Image.new("L", (W, H), 0); ImageDraw.Draw(rimm).polygon([(P(x), P(y)) for x, y in rp], fill=255)
    inner = Image.new("L", (W, H), 0); ImageDraw.Draw(inner).polygon([(P(x - 0.035 * h), P(y)) for x, y in rp], fill=255)
    rimm = ImageChops.subtract(rimm, inner); rimm = Image.eval(rimm, lambda v: int(v * 0.85 * a))
    img.paste(rim, (0, 0), rimm)
    # cheekbone / jaw / temple shading (soft polys)
    d.poly(xf(spline([(-0.34, 0.05), (-0.22, 0.12), (-0.25, 0.3), (-0.33, 0.22)], n=5), cx, cy, h), A(SKIN_M, 0.35 * a))
    d.poly(xf(spline([(0.1, 0.48), (0.25, 0.38), (0.34, 0.2), (0.3, 0.42), (0.14, 0.54)], n=5), cx, cy, h), A((70, 40, 36), 0.4 * a))
    # brow ridge shadow from helmet brim
    d.poly(xf([(-0.37, -0.42), (0.37, -0.42), (0.37, -0.24), (0.0, -0.2), (-0.37, -0.26)], cx, cy, h), A((60, 34, 30), 0.38 * a))
    # eyes
    lk = look * 0.02 * h
    for sgn in (-1, 1):
        ex, ey = cx + sgn * 0.155 * h, cy - 0.1 * h
        lit_side = sgn < 0
        sock = A((90, 52, 42) if lit_side else (60, 34, 30), 0.45 * a)
        d.ell(ex, ey - 0.005 * h, 0.1 * h, 0.06 * h, fill=sock)
        shut = blink or sgn in closed
        oh = 0.034 * h * (1 - squint) if not shut else 0.004 * h
        eye = spline([(-0.075, 0.0), (-0.035, -oh / h * 1.0), (0.03, -oh / h * 1.05), (0.075, 0.003), (0.02, oh / h * 0.7), (-0.04, oh / h * 0.65)], n=6)
        ep = xf(eye, ex, ey, h, sx=h * (1 if sgn < 0 else -1))
        d.poly(ep, A((222, 214, 200) if lit_side else (150, 140, 132), a))
        if not shut:
            ir = 0.026 * h
            d.circ(ex + lk, ey + 0.002 * h, ir, fill=A((78, 112, 128) if lit_side else (56, 80, 92), a))
            d.circ(ex + lk, ey + 0.002 * h, ir * 0.48, fill=A(INK, a))
            d.circ(ex + lk - ir * 0.35, ey - ir * 0.35, ir * 0.28, fill=A(WHITE, a))
        # upper lid line (thick, dark) + lower lid soft
        d.line(spline([ep[0], ep[2], ep[4], ep[6], ep[9], ep[12]], closed=False, n=4)[:], A((40, 22, 18), a), 0.016 * h)
        # brow: heavy, angled down to the centre (determined)
        bx = ex; by = ey - 0.068 * h
        bp = spline([(-0.1 * sgn, 0.012), (-0.02 * sgn, -0.024), (0.11 * sgn, -0.012), (0.12 * sgn, 0.014), (-0.02 * sgn, 0.012), (-0.1 * sgn, 0.042)], n=4)
        d.poly(xf(bp, bx, by, h), A(mix(HAIR, (60, 26, 16), 0.2 if lit_side else 0.55), a))
    # nose
    d.poly(xf(spline([(0.02, -0.08), (0.06, 0.08), (0.08, 0.17), (0.03, 0.2)], n=5), cx, cy, h), A((96, 58, 46), 0.55 * a))  # shadow side
    d.ell(cx - 0.02 * h, cy + 0.15 * h, 0.06 * h, 0.045 * h, fill=A(mix(SKIN, key, 0.25), 0.8 * a))  # lit tip
    d.circ(cx - 0.035 * h, cy + 0.14 * h, 0.012 * h, fill=A((255, 230, 200), 0.7 * a))
    for sgn in (-1, 1): d.ell(cx + sgn * 0.04 * h, cy + 0.19 * h, 0.022 * h, 0.011 * h, fill=A((60, 30, 26), a))
    # mustache (reddish, lit left)
    mu = spline([(-0.14, 0.27), (-0.07, 0.215), (0.0, 0.225), (0.07, 0.215), (0.14, 0.27), (0.07, 0.255), (0.0, 0.265), (-0.07, 0.255)], n=5)
    d.poly(xf(mu, cx, cy, h), A(mix(HAIR, (70, 30, 18), 0.25), a))
    d.poly(xf(spline([(-0.12, 0.255), (-0.06, 0.225), (-0.01, 0.235), (-0.06, 0.245)], n=4), cx, cy, h), A(mix(HAIR, AMBER_L, 0.35), 0.8 * a))
    # mouth: firm, set
    d.line(spline([(cx - 0.085 * h, cy + 0.31 * h), (cx, cy + 0.318 * h), (cx + 0.085 * h, cy + 0.305 * h)], closed=False, n=4), A((70, 30, 26), a), 0.016 * h)
    d.ell(cx - 0.01 * h, cy + 0.345 * h, 0.06 * h, 0.016 * h, fill=A(mix(SKIN, (200, 110, 90), 0.3), 0.6 * a))
    d.ell(cx, cy + 0.44 * h, 0.07 * h, 0.03 * h, fill=A(SKIN_M, 0.35 * a))  # chin highlight
    # Brodie helmet (wide shallow dish), seen slightly from below: brim underside dark, dome rim-lit
    dome = spline([(-0.43, -0.42), (-0.4, -0.62), (-0.24, -0.78), (0.0, -0.82), (0.24, -0.78), (0.4, -0.62), (0.43, -0.42)], closed=False, n=6)
    rimpoly(d, xf(dome + [(0.43, -0.4), (-0.43, -0.4)], cx, cy, h), BRODIE, mix(BRODIE, key, 0.7), 0.03 * h, 0.01 * h, a)
    d.ell(cx, cy - 0.41 * h, 0.8 * h, 0.13 * h, fill=A(mix(BRODIE, key, 0.55), a))
    d.ell(cx + 0.02 * h, cy - 0.395 * h, 0.79 * h, 0.12 * h, fill=A((52, 54, 36), a))
    d.ell(cx + 0.02 * h, cy - 0.385 * h, 0.5 * h, 0.075 * h, fill=A((36, 36, 26), a))   # underside / lining

# ---------------------------------------------------------------- York prone, aiming AT the viewer (enemy POV)
def york_prone(img, d, cx, cy, h, t, key=AMBER, rim=COLD, a=1.0, flash=0.0):
    """Lying flat, seen at ground level from the enemy side. cx,cy = face centre; h = face height.
    Muzzle in front of his right cheek (viewer's left), right eye open behind the sights, left eye shut."""
    # low mound of shoulders/back right behind the head + elbows planted out to the sides
    bd = spline([(-1.3, 0.62), (-1.0, 0.36), (-0.4, 0.26), (0.4, 0.26), (1.0, 0.36), (1.3, 0.62), (0.0, 0.66)], n=6)
    rimpoly(d, xf(bd, cx, cy, h), (36, 36, 26), mix(OD_L, key, 0.5), 0.0, 0.02 * h, a)
    for sgn in (-1, 1):
        arm = [(sgn * 1.15, 0.66), (sgn * 0.7, 0.52), (sgn * 0.32 if sgn > 0 else -0.2, 0.44)]
        d.line(xf(arm, cx, cy, h), A(mix(OD, key, 0.45), a), 0.3 * h)
        d.line(xf([(x, y + 0.03) for x, y in arm], cx, cy, h), A((46, 44, 30), a), 0.26 * h)
    york_face(img, d, cx, cy, h, t, key, rim, squint=0.5, a=a, shoulders=False, closed=(1,))
    mx, my, mr = cx - 0.17 * h, cy + 0.2 * h, 0.17 * h
    d.poly(xf([(-0.42, 0.3), (-0.05, 0.28), (0.02, 0.5), (-0.4, 0.55)], cx, cy, h), A((84, 54, 30), a))           # stock under cheek
    d.poly(xf([(-0.42, 0.3), (-0.05, 0.28), (-0.06, 0.32), (-0.42, 0.34)], cx, cy, h), A(mix((130, 86, 46), key, 0.4), a))
    d.ell(mx + 0.005 * h, my + 0.03 * h, mr * 1.02, mr * 0.98, fill=A((58, 38, 24), a))                              # fore-end wood
    d.poly([(mx - mr * 0.9, my + mr * 0.7), (mx + mr * 0.9, my + mr * 0.7), (mx + mr * 0.7, my + mr * 1.25), (mx - mr * 0.7, my + mr * 1.25)], A(mix(SKIN_M, key, 0.1), a))  # fingers under the fore-end
    d.circ(mx, my, mr * 0.8, fill=A((66, 70, 74), a))
    d.circ(mx - mr * 0.12, my - mr * 0.12, mr * 0.62, fill=A(mix((112, 118, 122), key, 0.3), a))
    d.circ(mx, my, mr * 0.34, fill=A((8, 8, 10), a))
    d.rect(mx - mr * 0.1, my - mr * 1.25, mx + mr * 0.1, my - mr * 0.72, fill=A((84, 88, 90), a))                # front sight post
    if flash > 0.01:
        glow(img, lambda g: g.circ(mx, my, mr * (2 + 3 * flash), fill=A(AMBER_L, flash)), blur=50)

# ---------------------------------------------------------------- York profile with rifle (dusk woods)
def york_profile(d, x, y, h, t, key=AMBER, a=1.0, hat=True):
    """Kneeling/standing profile facing right, rifle shouldered. (x,y) = head centre, h = head height."""
    ox = -0.03 * h
    body = spline([(-0.2, 0.4), (-0.55, 0.7), (-0.65, 1.6), (-0.55, 2.6), (0.35, 2.6), (0.4, 1.4), (0.3, 0.6), (0.1, 0.42)], n=6)
    rimpoly(d, xf(body, x, y, h), (40, 36, 26), mix(OD_L, key, 0.7), ox, 0, a)
    head = spline([(-0.28, -0.1), (-0.2, -0.42), (0.1, -0.48), (0.3, -0.25), (0.34, -0.05), (0.42, 0.05), (0.34, 0.12), (0.32, 0.28), (0.18, 0.42), (-0.1, 0.42), (-0.28, 0.2)], n=6)
    rimpoly(d, xf(head, x, y, h), (72, 44, 36), mix(SKIN, key, 0.3), ox, 0, a)
    d.circ(x + 0.2 * h, y - 0.06 * h, 0.03 * h, fill=A((20, 14, 12), a))            # eye (squint)
    d.line([(x + 0.12 * h, y - 0.13 * h), (x + 0.3 * h, y - 0.12 * h)], A((90, 40, 22), a), 0.035 * h)  # brow
    d.poly(xf([(0.22, 0.17), (0.36, 0.14), (0.35, 0.21), (0.2, 0.22)], x, y, h), A(mix(HAIR, key, 0.3), a))  # mustache
    if hat:  # farm hat
        d.poly(xf(spline([(-0.32, -0.25), (-0.25, -0.62), (0.15, -0.66), (0.3, -0.3)], n=5), x, y, h), A((70, 54, 36), a))
        d.ell(x, y - 0.27 * h, 0.55 * h, 0.07 * h, fill=A(mix((80, 60, 40), key, 0.4), a))
    # rifle along the cheek, pointing right
    d.line([(x - 0.3 * h, y + 0.55 * h), (x + 2.6 * h, y + 0.02 * h)], A((80, 52, 30), a), 0.13 * h)
    d.line([(x + 0.9 * h, y + 0.32 * h), (x + 3.4 * h, y - 0.1 * h)], A((70, 72, 74), a), 0.05 * h)
    d.line([(x + 0.9 * h, y + 0.29 * h), (x + 3.4 * h, y - 0.13 * h)], A(mix((120, 120, 120), key, 0.5), a), 0.015 * h)
    for (px, py) in ((0.6, 0.5), (1.4, 0.32)):  # hands
        d.ell(x + px * h, y + py * h, 0.13 * h, 0.1 * h, fill=A(mix(SKIN_M, key, 0.2), a))

def brodie_back(d, x, y, h, t, rim=AMBER, a=1.0, seed=0, duck=0.0):
    """US soldier ducking behind cover, seen from behind-low: dish helmet + shoulders."""
    y = y + duck * 0.3 * h + math.sin(t * 2 + seed) * 0.01 * h
    sh = spline([(-0.2, 0.2), (-0.8, 0.45), (-1.0, 1.2), (1.0, 1.2), (0.8, 0.45), (0.2, 0.2)], n=5)
    rimpoly(d, xf(sh, x, y, h), (40, 40, 28), mix(OD_L, rim, 0.6), 0, 0.03 * h, a)
    d.ell(x, y - 0.05 * h, 0.3 * h, 0.32 * h, fill=A((60, 40, 30), a))
    d.ell(x, y - 0.2 * h, 0.72 * h, 0.15 * h, fill=A(mix(BRODIE, rim, 0.7), a))
    d.ell(x, y - 0.17 * h, 0.7 * h, 0.13 * h, fill=A(BRODIE, a))
    d.ell(x, y - 0.3 * h, 0.4 * h, 0.22 * h, fill=A(mix(BRODIE, rim, 0.3), a))
