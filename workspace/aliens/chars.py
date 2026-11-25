# Characters / props for 《历史课没讲的一天》 — flat fills + highlights, NO dark outlines.
from fx import *

NAVYT = (24, 20, 40); GOLD = (255, 200, 60); GOLD_D = (214, 150, 40)
ALC = (176, 190, 196); ALC_D = (138, 152, 162); ALC_L = (214, 226, 230); EYEC = (22, 24, 44)
STN = (164, 150, 128); STN_D = (124, 112, 94); STN_L = (196, 184, 162)
SILV = (206, 214, 226); SILV_D = (150, 160, 178); SILV_L = (240, 244, 250)
TREX = (110, 176, 90); TREX_D = (76, 132, 66); TREX_L = (160, 210, 120); TREX_B = (222, 220, 160)
PTER = (170, 120, 200); PTER_D = (124, 82, 160); PTER_L = (206, 168, 230)
SAND = (238, 206, 150); SAND_D = (214, 176, 116); PYR = (240, 196, 110); PYR_D = (196, 146, 72)
BLUE_N = (54, 104, 210); LAZ = (255, 60, 50); PINK = (255, 120, 160); TEAL = (40, 200, 210)

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
def heart(d, x, y, s, col, a=1.0):
    d.circ(x - s * 0.5, y - s * 0.2, s * 0.55, fill=A(col, a)); d.circ(x + s * 0.5, y - s * 0.2, s * 0.55, fill=A(col, a))
    d.poly([(x - s * 1.02, y), (x + s * 1.02, y), (x, y + s * 1.1)], A(col, a))
def star(d, x, y, r, col, a=1.0, n=5, rot=0):
    pts = []
    for i in range(n * 2):
        ang = rot + i * math.pi / n - math.pi / 2; rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    d.poly(pts, A(col, a))
def note(d, x, y, s, col, a=1.0):
    d.ell(x, y, s * 0.5, s * 0.36, A(col, a)); d.line([(x + s * 0.45, y), (x + s * 0.45, y - s * 1.4), (x + s * 1.0, y - s * 1.1)], A(col, a), s * 0.16)
def rot(pts, cx, cy, ang):
    c, s_ = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * c - (y - cy) * s_, cy + (x - cx) * s_ + (y - cy) * c) for x, y in pts]
def ellpts(x, y, rx, ry, ang=0.0, n=28):
    return rot([(x + rx * math.cos(2 * math.pi * i / n), y + ry * math.sin(2 * math.pi * i / n)) for i in range(n)], x, y, ang)
def sweat(d, x, y, s, a=1.0):
    d.circ(x, y + s * 0.3, s * 0.45, fill=A((120, 210, 255), a)); d.poly([(x - s * 0.42, y + s * 0.15), (x, y - s * 0.6), (x + s * 0.42, y + s * 0.15)], A((120, 210, 255), a))
    d.circ(x - s * 0.12, y + s * 0.2, s * 0.12, fill=A(WHITE, 0.7 * a))
def stamp(d, t, t0, s, x, y, size, col, a=1.0):
    k = back(pr(t, t0, t0 + 0.18))
    if k <= 0: return
    d.text(x, y, s, int(size * (1.8 - 0.8 * k)), A(col, a * min(1, k * 1.5)), k=1)

# ---------------- grey alien ----------------
def alien(d, x, y, s, t, mood="chill", a=1.0, look=0.0, col=ALC, handL=None, handR=None, walk=0.0, pharaoh=False, sq=0.0, body=True, brow=0.0):
    """x,y = head centre; s = head radius. handL/handR = absolute hand points."""
    if a <= 0.01: return
    dk = mix(col, (40, 50, 70), 0.3); lt = mix(col, WHITE, 0.35)
    if body:
        d.ell(x, y + 2.75 * s, 0.7 * s, 0.12 * s, A((0, 0, 0), 0.18 * a))
        for sd in (-1, 1):  # legs
            ph = math.sin(walk * 2 * math.pi + (0 if sd < 0 else math.pi))
            d.line([(x + sd * 0.16 * s, y + 1.85 * s), (x + sd * 0.2 * s + ph * 0.18 * s, y + 2.7 * s)], A(dk, a), 0.16 * s)
            d.ell(x + sd * 0.24 * s + ph * 0.18 * s, y + 2.72 * s, 0.14 * s, 0.06 * s, A(dk, a))
        sh = {-1: handL, 1: handR}
        for sd in (-1, 1):
            hx, hy = sh[sd] if sh[sd] else (x + sd * 0.62 * s, y + 1.85 * s + math.sin(walk * 2 * math.pi + sd) * 0.05 * s)
            d.line([(x + sd * 0.25 * s, y + 1.15 * s), (hx, hy)], A(dk, a), 0.13 * s); d.circ(hx, hy, 0.1 * s, fill=A(dk, a))
        d.ell(x, y + 1.45 * s, 0.36 * s, 0.55 * s, A(col, a)); d.ell(x - 0.1 * s, y + 1.3 * s, 0.12 * s, 0.25 * s, A(lt, 0.5 * a))
        d.line([(x, y + 0.7 * s), (x, y + 1.0 * s)], A(col, a), 0.2 * s)
    if pharaoh:  # nemes back flaps
        d.poly([(x - 0.9 * s, y - 0.35 * s), (x + 0.9 * s, y - 0.35 * s), (x + 1.08 * s, y + 1.05 * s), (x + 0.55 * s, y + 1.1 * s), (x - 0.55 * s, y + 1.1 * s), (x - 1.08 * s, y + 1.05 * s)], A(GOLD, a))
        for i in range(5):
            yy = y - 0.1 * s + i * 0.24 * s
            for sd in (-1, 1): d.line([(x + sd * 0.86 * s, yy), (x + sd * 1.06 * s, yy + 0.06 * s)], A(BLUE_N, a), 0.09 * s)
    rx, ry = s * (0.88 + sq), s * (0.78 - sq)
    d.ell(x, y - 0.12 * s, rx, ry, A(col, a))
    d.poly([(x - rx * 0.92, y), (x + rx * 0.92, y), (x + 0.32 * s, y + 0.68 * s), (x, y + 0.84 * s), (x - 0.32 * s, y + 0.68 * s)], A(col, a))
    d.ell(x - 0.38 * s, y - 0.5 * s, 0.26 * s, 0.14 * s, A(WHITE, 0.4 * a))
    if pharaoh:  # cap + cobra
        d.d.chord((P(x - 0.92 * s), P(y - 1.0 * s), P(x + 0.92 * s), P(y + 0.3 * s)), 180, 360, fill=A(GOLD, a))
        for i in range(4):
            xx = x - 0.6 * s + i * 0.4 * s
            d.line([(xx, y - 0.86 * s + abs(xx - x) * 0.25), (xx, y - 0.4 * s)], A(BLUE_N, a), 0.08 * s)
        d.ell(x, y - 0.6 * s, 0.1 * s, 0.17 * s, A(GOLD_D, a)); d.circ(x, y - 0.74 * s, 0.07 * s, fill=A((255, 230, 120), a))
    # eyes
    ey = y + 0.08 * s
    for sd in (-1, 1):
        ex = x + sd * 0.36 * s; ang = -sd * 0.38
        if mood in ("happy", "proud"):
            d.arc(ex, ey + 0.08 * s, 0.22 * s, 0.16 * s, 200, 340, A(EYEC, a), 0.09 * s)
            d.circ(ex + sd * 0.05 * s, ey + 0.28 * s, 0.1 * s, fill=A(PINK, 0.55 * a))
            continue
        big = {"scared": 1.25, "scream": 1.3, "angry": 0.95}.get(mood, 1.0)
        d.poly(ellpts(ex, ey, 0.3 * s * big, 0.17 * s * big, ang), A(EYEC, a))
        if mood in ("scared", "scream"):
            d.circ(ex + look * 0.06 * s, ey, 0.05 * s, fill=A(WHITE, a))
        elif mood == "love":
            heart(d, ex, ey - 0.02 * s, 0.09 * s, PINK, a)
        else:
            d.circ(ex - 0.09 * s + look * 0.1 * s, ey - 0.05 * s, 0.065 * s, fill=A(WHITE, 0.9 * a))
            d.circ(ex + 0.06 * s + look * 0.1 * s, ey + 0.04 * s, 0.03 * s, fill=A(WHITE, 0.8 * a))
        if mood == "flat":   # half-closed lid: cut the top half straight
            d.rect(ex - 0.36 * s, ey - 0.3 * s, ex + 0.36 * s, ey + 0.01 * s, fill=A(col, a))
            d.circ(ex + look * 0.1 * s, ey + 0.07 * s, 0.045 * s, fill=A(WHITE, 0.9 * a))
        if mood == "angry" or brow > 0:   # slanted lid + brow: inner end low, outer end high
            bk = max(brow, 0.6 if mood == "angry" else 0)
            ix, ox = ex - sd * 0.34 * s, ex + sd * 0.36 * s
            iy, oy = ey - 0.02 * s + bk * 0.04 * s, ey - 0.24 * s
            d.poly([(ix, iy), (ox, oy), (ox, ey - 0.4 * s), (ix, ey - 0.4 * s)], A(col, a))
            d.line([(ix, iy - 0.08 * s), (ox, oy - 0.12 * s)], A(dk, a), 0.09 * s)
    my = y + 0.52 * s
    if mood in ("scared",): d.ell(x, my, 0.06 * s, 0.08 * s, A(EYEC, a))
    elif mood == "scream": d.ell(x, my + 0.03 * s, 0.12 * s, 0.15 * s, A(EYEC, a)); d.ell(x, my + 0.11 * s, 0.07 * s, 0.04 * s, A(TONGUE, a))
    elif mood in ("happy", "proud", "love"): d.d.chord((P(x - 0.14 * s), P(my - 0.1 * s), P(x + 0.14 * s), P(my + 0.1 * s)), 0, 180, fill=A(EYEC, a))
    elif mood == "angry": d.rect(x - 0.13 * s, my - 0.03 * s, x + 0.13 * s, my + 0.05 * s, fill=A(EYEC, a), r=0.02 * s)
    elif mood == "flat": d.line([(x - 0.1 * s, my), (x + 0.1 * s, my)], A(EYEC, a), 0.04 * s)
    else: d.arc(x, my - 0.06 * s, 0.1 * s, 0.07 * s, 20, 160, A(EYEC, a), 0.04 * s)
    if mood in ("scared", "scream", "angry"): sweat(d, x + 0.9 * s, y - 0.4 * s, 0.16 * s, a)

def blaster(d, x, y, s, a=1.0, face=-1, charge=0.0, t=0.0):
    """chunky toy laser/water blaster, grip at x,y, pointing left if face=-1."""
    f = face
    d.rect(min(x, x + f * 1.9 * s), y - 0.42 * s, max(x, x + f * 1.9 * s), y + 0.06 * s, fill=A((255, 140, 50), a), r=0.2 * s)
    d.rect(min(x + f * 1.9 * s, x + f * 2.5 * s), y - 0.3 * s, max(x + f * 1.9 * s, x + f * 2.5 * s), y - 0.06 * s, fill=A((90, 210, 230), a), r=0.1 * s)
    for i in range(3): d.ell(x + f * (2.0 + i * 0.18) * s, y - 0.18 * s, 0.06 * s, 0.2 * s, A((40, 160, 200), a))
    d.circ(x + f * 0.6 * s, y - 0.62 * s, 0.32 * s, fill=A((120, 220, 255), 0.9 * a)); d.circ(x + f * 0.5 * s, y - 0.72 * s, 0.1 * s, fill=A(WHITE, 0.7 * a))
    d.rect(min(x - f * 0.05 * s, x + f * 0.35 * s), y, max(x - f * 0.05 * s, x + f * 0.35 * s), y + 0.6 * s, fill=A((230, 100, 40), a), r=0.1 * s)
    d.ell(x + f * 1.0 * s, y - 0.28 * s, 0.5 * s, 0.07 * s, A(WHITE, 0.35 * a))
    if charge > 0: glow(d, x + f * 2.55 * s, y - 0.18 * s, 0.6 * s * (1 + 0.2 * math.sin(t * 30)), (120, 240, 255), charge)

# ---------------- statue king (Mesopotamian style) ----------------
def statue(d, x, y, s, t, eo=0.0, eglow=0.0, a=1.0, col=STN, mood="calm", wink=0.0, body=True, gray=0.0):
    """x,y = face centre; s scale (face half-width ~0.42 s). eo = eye open 0..1."""
    col = mix(col, (150, 150, 156), gray); dk = mix(col, (40, 34, 30), 0.3); lt = mix(col, WHITE, 0.25)
    if body:
        d.poly([(x - 0.55 * s, y + 0.9 * s), (x + 0.55 * s, y + 0.9 * s), (x + 0.95 * s, y + 4.2 * s), (x - 0.95 * s, y + 4.2 * s)], A(col, a))
        d.poly([(x - 0.55 * s, y + 0.9 * s), (x - 0.2 * s, y + 0.9 * s), (x - 0.45 * s, y + 4.2 * s), (x - 0.95 * s, y + 4.2 * s)], A(lt, 0.55 * a))
        d.rect(x - 0.7 * s, y + 1.75 * s, x + 0.7 * s, y + 2.25 * s, fill=A(dk, a), r=0.2 * s)    # folded arms
        d.circ(x - 0.05 * s, y + 2.0 * s, 0.2 * s, fill=A(col, a)); d.circ(x + 0.18 * s, y + 2.0 * s, 0.18 * s, fill=A(col, a))
        for i in range(4): d.line([(x - 0.8 * s + i * 0.1 * s, y + 2.6 * s + i * 0.4 * s), (x + 0.8 * s + i * 0.1 * s, y + 2.5 * s + i * 0.4 * s)], A(dk, 0.5 * a), 0.05 * s)
    # hat (polos)
    d.poly([(x - 0.44 * s, y - 0.4 * s), (x + 0.44 * s, y - 0.4 * s), (x + 0.52 * s, y - 1.45 * s), (x - 0.52 * s, y - 1.45 * s)], A(col, a))
    d.ell(x, y - 1.45 * s, 0.52 * s, 0.1 * s, A(lt, a))
    for i in range(3): d.rect(x - 0.48 * s + i * 0.02 * s, y - 0.65 * s - i * 0.28 * s, x + 0.48 * s - i * 0.02 * s, y - 0.57 * s - i * 0.28 * s, fill=A(dk, 0.7 * a))
    d.rect(x - 0.42 * s, y - 1.38 * s, x - 0.3 * s, y - 0.45 * s, fill=A(lt, 0.5 * a))
    # face
    d.rect(x - 0.42 * s, y - 0.45 * s, x + 0.42 * s, y + 0.45 * s, fill=A(col, a), r=0.16 * s)
    for sd in (-1, 1): d.ell(x + sd * 0.45 * s, y - 0.05 * s, 0.08 * s, 0.16 * s, A(dk, a))
    d.ell(x - 0.2 * s, y - 0.3 * s, 0.12 * s, 0.06 * s, A(lt, 0.7 * a))
    # beard
    d.poly([(x - 0.44 * s, y + 0.12 * s), (x + 0.44 * s, y + 0.12 * s), (x + 0.5 * s, y + 1.5 * s), (x - 0.5 * s, y + 1.5 * s)], A(dk, a))
    for r_ in range(5):
        for c_ in range(4):
            d.circ(x - 0.33 * s + c_ * 0.22 * s + (r_ % 2) * 0.05 * s, y + 0.32 * s + r_ * 0.26 * s, 0.1 * s, fill=A(mix(dk, col, 0.45), a))
    d.poly([(x - 0.34 * s, y + 0.2 * s), (x, y + 0.12 * s), (x + 0.34 * s, y + 0.2 * s), (x + 0.3 * s, y + 0.3 * s), (x - 0.3 * s, y + 0.3 * s)], A(mix(dk, (20, 16, 14), 0.2), a))
    if mood == "whistle": d.ell(x + 0.08 * s, y + 0.3 * s, 0.06 * s, 0.07 * s, A((50, 30, 26), a))
    # nose
    d.poly([(x - 0.05 * s, y - 0.12 * s), (x + 0.05 * s, y - 0.12 * s), (x + 0.12 * s, y + 0.1 * s), (x - 0.12 * s, y + 0.1 * s)], A(dk, a))
    # eyes + brows
    for sd in (-1, 1):
        ex, ey = x + sd * 0.19 * s, y - 0.18 * s
        o = eo if not (wink > 0 and sd > 0) else eo * (1 - wink)
        if o > 0.05:
            d.poly(ellpts(ex, ey, 0.12 * s, 0.075 * s * o, 0), A(WHITE if eglow < 0.5 else (255, 210, 200), a))
            if o > 0.4: d.circ(ex + (0.03 * s if mood == "whistle" else 0), ey, 0.045 * s * min(1, o), fill=A(LAZ if eglow > 0.2 else EYEC, a))
        else:
            d.arc(ex, ey - 0.02 * s, 0.11 * s, 0.05 * s, 20, 160, A(dk, a), 0.035 * s)
        if eglow > 0: glow(d, ex, ey, 0.4 * s * (0.8 + 0.2 * math.sin(t * 40 + sd)), LAZ, eglow)
        tilt = 0.06 * s if mood in ("angry", "calm") else -0.04 * s
        d.line([(ex - 0.15 * s, ey - 0.13 * s - sd * tilt * 0.5), (ex + 0.15 * s, ey - 0.13 * s + sd * tilt * 0.5)], A(dk, a), 0.06 * s)

def laser(d, x0, y0, x1, y1, t, a=1.0, k=1.0):
    if a <= 0.01 or k <= 0: return
    x1, y1 = lerp(x0, x1, k), lerp(y0, y1, k); fl = 1 + 0.15 * math.sin(t * 60)
    for w, c, al in ((90, LAZ, 0.12), (54, LAZ, 0.25), (28, (255, 90, 70), 0.9), (10, (255, 236, 220), 1.0)):
        d.line([(x0, y0), (x1, y1)], A(c, al * a), w * fl)
    glow(d, x1, y1, 80 * fl, (255, 200, 120), a)

# ---------------- UFO / explosion / capsule / portal ----------------
def ufo(d, x, y, s, t, a=1.0, face=False, mood="chill", beam=0.0):
    if a <= 0.01: return
    if beam > 0: d.poly([(x - 0.4 * s, y + 0.15 * s), (x + 0.4 * s, y + 0.15 * s), (x + 1.2 * s, y + 4 * s), (x - 1.2 * s, y + 4 * s)], A((255, 250, 170), 0.22 * beam * a))
    d.ell(x, y - 0.2 * s, 0.46 * s, 0.4 * s, A((130, 230, 240), 0.95 * a))
    d.ell(x - 0.16 * s, y - 0.38 * s, 0.12 * s, 0.07 * s, A(WHITE, 0.7 * a))
    if face:
        for sd in (-1, 1): d.poly(ellpts(x + sd * 0.13 * s, y - 0.18 * s, 0.1 * s, 0.05 * s, sd * 0.4), A(EYEC, a))
    d.ell(x, y + 0.06 * s, 1.0 * s, 0.26 * s, A(SILV_D, a))
    d.ell(x, y - 0.02 * s, 1.0 * s, 0.2 * s, A(SILV, a))
    d.ell(x - 0.3 * s, y - 0.07 * s, 0.4 * s, 0.06 * s, A(SILV_L, 0.8 * a))
    for i in range(5):
        lx = x + (i - 2) * 0.38 * s; on = (int(t * 6) + i) % 2
        d.circ(lx, y + 0.1 * s + abs(i - 2) * -0.02 * s, 0.06 * s, fill=A((255, 220, 80) if on else (255, 110, 160), a))

def explosion(d, x, y, t, t0, s=200, a=1.0, seed=3):
    u = t - t0
    if u < 0 or u > 2.0: return
    g = ease(u / 0.3); fade = 1 - pr(u, 0.7, 2.0)
    r2 = random.Random(seed)
    if u > 0.25:
        for i in range(7):  # smoke
            ang = r2.uniform(0, 6.28); rr = s * (0.6 + u * 0.5)
            d.circ(x + math.cos(ang) * rr * 0.6, y + math.sin(ang) * rr * 0.4 - u * 80, s * 0.45 * (0.6 + u * 0.4), fill=A((120, 100, 96), 0.45 * fade * a))
    for col, k in (((230, 60, 40), 1.0), ((255, 140, 40), 0.78), ((255, 210, 70), 0.55), ((255, 250, 220), 0.3)):
        r2 = random.Random(seed)
        for i in range(8):
            ang = i * 0.785 + r2.uniform(-0.3, 0.3); off = s * 0.45 * k * g
            d.circ(x + math.cos(ang) * off, y + math.sin(ang) * off, s * 0.5 * k * g * (1.15 - 0.3 * pr(u, 0.4, 2)), fill=A(col, fade * a))
        d.circ(x, y, s * 0.7 * k * g, fill=A(col, fade * a))
    sparks(d, x, y, t, t0, n=46, spd=s * 6, col=(255, 220, 140), a=a, seed=seed, life=1.1)
    rings(d, x, y, t, [t0], (255, 240, 200), 0.6 * a, s * 2.4)

def capsule(d, x, y, s, a=1.0, door=0.0, flame=0.0, t=0.0, eyes=0.0):
    if a <= 0.01: return
    if flame > 0:
        for i in range(8):
            k = i / 8; d.circ(x + 0.4 * s * k * 3, y - 0.5 * s - k * 1.6 * s, s * 0.6 * (1 - k * 0.7) * (0.9 + 0.1 * math.sin(t * 40 + i)), fill=A(mix((255, 240, 160), (230, 60, 30), k), flame * a * (1 - k * 0.6)))
    d.ell(x, y + 0.7 * s, 0.9 * s, 0.12 * s, A((0, 0, 0), 0.18 * a))
    d.rect(x - 1.0 * s, y - 0.58 * s, x + 1.0 * s, y + 0.58 * s, fill=A(SILV, a), r=0.56 * s)
    d.rect(x - 1.0 * s, y + 0.1 * s, x + 1.0 * s, y + 0.58 * s, fill=A(SILV_D, a), r=0.4 * s)
    d.rect(x - 0.8 * s, y - 0.45 * s, x + 0.4 * s, y - 0.32 * s, fill=A(SILV_L, 0.8 * a), r=0.06 * s)
    d.circ(x - 0.5 * s, y - 0.02 * s, 0.26 * s, fill=A((90, 150, 200), a)); d.circ(x - 0.57 * s, y - 0.1 * s, 0.08 * s, fill=A(WHITE, 0.7 * a))
    # door on the right half
    d.rect(x + 0.05 * s, y - 0.4 * s, x + 0.65 * s, y + 0.4 * s, fill=A((40, 40, 60), a), r=0.12 * s)
    if eyes > 0:
        for sd in (-1, 1): d.ell(x + 0.35 * s + sd * 0.1 * s, y - 0.05 * s, 0.05 * s, 0.03 * s, A((200, 255, 220), eyes * a))
    if door < 1:
        dw = 0.6 * s * (1 - door)
        d.rect(x + 0.05 * s, y - 0.4 * s, x + 0.05 * s + max(dw, 1), y + 0.4 * s, fill=A(mix(SILV_D, SILV, 0.5), a), r=0.12 * s)

def portal(d, x, y, r, t, a=1.0):
    if a <= 0.01: return
    glow(d, x, y, r * 1.4, (120, 200, 255), 0.7 * a, 9)
    cols = [(40, 80, 200), (70, 140, 240), (120, 210, 255), (60, 110, 230), (180, 240, 255)]
    for i in range(10):
        k = 1 - i / 10; rr = r * k
        d.ell(x + math.sin(t * 3 + i) * 8, y + math.cos(t * 2.5 + i) * 6, rr, rr * 0.92, A(cols[i % 5], a))
    for arm in range(5):
        pts = []
        for j in range(26):
            u = j / 25; ang = -t * 4 + arm * 2 * math.pi / 5 + u * 4.2; rr = r * 0.92 * (1 - u)
            pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr * 0.92))
        d.line(pts, A(WHITE, 0.5 * a), 10)
    d.circ(x, y, r * 0.12, fill=A(WHITE, a))

# ---------------- landscape ----------------
def moon(d, x, y, r, a=1.0, col=(252, 248, 232)):
    glow(d, x, y, r * 1.35, (255, 250, 230), 0.45 * a)
    d.circ(x, y, r, fill=A(col, a))
    for cx, cy, cr in ((-0.35, -0.2, 0.18), (0.25, 0.3, 0.14), (0.4, -0.35, 0.09), (-0.1, 0.45, 0.08), (0.05, -0.05, 0.06)):
        d.circ(x + cx * r, y + cy * r, cr * r, fill=A(mix(col, (180, 170, 150), 0.25), a))
    d.ell(x - 0.45 * r, y - 0.5 * r, 0.25 * r, 0.12 * r, A(WHITE, 0.5 * a))
def pyramid(d, x, by, w, h, a=1.0, lit=PYR, sh=PYR_D):
    d.poly([(x - w / 2, by), (x, by - h), (x + w * 0.12, by)], A(lit, a))
    d.poly([(x, by - h), (x + w / 2, by), (x + w * 0.12, by)], A(sh, a))
    for i in range(1, 6):
        yy = by - h * i / 6; hw = w / 2 * (1 - i / 6)
        d.line([(x - hw, yy), (x + w * 0.12 * (1 - i / 6), yy)], A(mix(lit, sh, 0.4), 0.6 * a), 3)
def mountain(d, x, by, w, h, a=1.0, col=(150, 160, 186)):
    d.poly([(x - w / 2, by), (x, by - h), (x + w / 2, by)], A(col, a))
    d.poly([(x, by - h), (x + w / 2, by), (x + w * 0.1, by)], A(mix(col, (60, 60, 90), 0.2), a))
    d.poly([(x - w * 0.15, by - h * 0.7), (x, by - h), (x + w * 0.15, by - h * 0.7), (x + w * 0.05, by - h * 0.62), (x - w * 0.05, by - h * 0.72)], A((250, 252, 255), a))

def flag(d, x, y, s, t, a=1.0):
    """pole base at x,y; earth-flag (stripes + little planet), no real-world flag."""
    d.line([(x, y), (x, y - 3.2 * s)], A((200, 200, 210), a), 0.08 * s); d.circ(x, y - 3.25 * s, 0.1 * s, fill=A(GOLD, a))
    fw, fh = 1.8 * s, 1.1 * s; top = y - 3.1 * s
    for i in range(7):
        y0 = top + fh * i / 7; y1 = top + fh * (i + 1) / 7
        pts = [(x + fw * j / 10, y0 + math.sin(t * 6 + j * 0.7) * 0.06 * s * j / 10) for j in range(11)] + \
              [(x + fw * j / 10, y1 + math.sin(t * 6 + j * 0.7) * 0.06 * s * j / 10) for j in range(10, -1, -1)]
        d.poly(pts, A((230, 70, 70) if i % 2 == 0 else (250, 246, 240), a))
    d.rect(x, top, x + fw * 0.42, top + fh * 4 / 7, fill=A((50, 90, 190), a))
    ex, ey, er = x + fw * 0.21, top + fh * 2 / 7, fh * 0.2
    d.circ(ex, ey, er, fill=A((90, 170, 250), a)); d.ell(ex - er * 0.3, ey - er * 0.2, er * 0.4, er * 0.3, A((90, 200, 110), a)); d.ell(ex + er * 0.35, ey + er * 0.35, er * 0.3, er * 0.25, A((90, 200, 110), a))

def phone(d, x, y, s, a=1.0, flash_=0.0):
    d.rect(x - 0.5 * s, y - 0.9 * s, x + 0.5 * s, y + 0.9 * s, fill=A((40, 44, 64), a), r=0.15 * s)
    d.rect(x - 0.4 * s, y - 0.75 * s, x + 0.4 * s, y + 0.75 * s, fill=A((120, 210, 240), a), r=0.08 * s)
    d.poly([(x - 0.3 * s, y - 0.6 * s), (x - 0.05 * s, y - 0.6 * s), (x - 0.35 * s, y + 0.1 * s)], A(WHITE, 0.4 * a))
    if flash_ > 0: glow(d, x, y, 2.5 * s, WHITE, flash_)

# ---------------- dinos ----------------
def trex(d, x, y, s, t, mood="chill", jaw=0.0, a=1.0, look=(0.0, 0.0), body=True, col=TREX):
    """x,y = head centre, snout pointing left."""
    if a <= 0.01: return
    dk = mix(col, (20, 50, 20), 0.3); lt = mix(col, WHITE, 0.3)
    if body:
        d.poly([(x + 0.5 * s, y + 0.6 * s), (x + 2.2 * s, y + 1.3 * s), (x + 3.4 * s, y + 1.0 * s), (x + 2.2 * s, y + 2.0 * s), (x + 0.9 * s, y + 2.2 * s)], A(col, a))
        d.ell(x + 1.1 * s, y + 1.6 * s, 0.95 * s, 0.75 * s, A(col, a)); d.ell(x + 0.8 * s, y + 1.8 * s, 0.5 * s, 0.45 * s, A(TREX_B, a))
        for sd in (0, 1): d.rect(x + (0.8 + sd * 0.6) * s, y + 2.0 * s, x + (1.1 + sd * 0.6) * s, y + 2.9 * s, fill=A(dk if sd else col, a), r=0.1 * s)
        d.line([(x + 0.55 * s, y + 1.3 * s), (x + 0.3 * s, y + 1.5 * s + math.sin(t * 8) * 0.04 * s)], A(dk, a), 0.12 * s)
        d.line([(x + 0.4 * s, y + 0.4 * s), (x + 0.7 * s, y + 1.0 * s)], A(col, a), 0.6 * s)
    jo = jaw * 0.45
    # lower jaw (rotates down at the back hinge)
    jx, jy = x + 0.5 * s, y + 0.15 * s
    lj = rot([(x - 0.75 * s, y + 0.1 * s), (x + 0.55 * s, y + 0.1 * s), (x + 0.5 * s, y + 0.45 * s), (x - 0.6 * s, y + 0.35 * s)], jx, jy, -jo)
    if jaw > 0.05:
        d.poly([(x - 0.7 * s, y + 0.12 * s), (x + 0.5 * s, y + 0.12 * s)] + [lj[1], lj[0]], A((150, 40, 50), a))
        for i in range(5):
            bx, by = lerp(lj[0][0], lj[1][0], 0.1 + i * 0.16), lerp(lj[0][1], lj[1][1], 0.1 + i * 0.16)
            d.poly(rot([(bx - 0.05 * s, by), (bx + 0.05 * s, by), (bx, by - 0.12 * s)], bx, by, -jo), A(WHITE, a))
    d.poly(lj, A(col, a))
    d.rect(x - 0.95 * s, y - 0.55 * s, x + 0.6 * s, y + 0.15 * s, fill=A(col, a), r=0.3 * s)
    d.ell(x - 0.4 * s, y - 0.42 * s, 0.35 * s, 0.08 * s, A(lt, 0.6 * a))
    for i in range(6): d.poly([(x - 0.8 * s + i * 0.2 * s, y + 0.12 * s), (x - 0.7 * s + i * 0.2 * s, y + 0.12 * s), (x - 0.75 * s + i * 0.2 * s, y + 0.25 * s)], A(WHITE, a))
    d.circ(x - 0.82 * s, y - 0.35 * s, 0.04 * s, fill=A(dk, a))
    ex, ey = x + 0.15 * s, y - 0.28 * s; big = 1.3 if mood in ("scared", "up") else 1.0
    d.circ(ex, ey, 0.16 * s * big, fill=A(WHITE, a)); d.circ(ex + look[0] * 0.07 * s, ey + look[1] * 0.07 * s, 0.075 * s * (0.7 if mood == "scared" else 1), fill=A(EYEC, a))
    if mood == "angry": d.line([(ex - 0.2 * s, ey - 0.25 * s), (ex + 0.2 * s, ey - 0.12 * s)], A(dk, a), 0.08 * s)
    elif mood == "sus": d.line([(ex - 0.2 * s, ey - 0.15 * s), (ex + 0.2 * s, ey - 0.2 * s)], A(dk, a), 0.07 * s)
    if mood in ("scared", "up"): sweat(d, x - 0.2 * s, y - 0.75 * s, 0.13 * s, a)

def ptero(d, x, y, s, t, flap=0.0, a=1.0, mood="chill", carry=False):
    if a <= 0.01: return
    w = math.sin(flap) * 0.6 * s
    for sd in (-1, 1):
        d.poly([(x - 0.15 * s, y), (x + sd * 1.5 * s, y - 0.3 * s - w), (x + sd * 1.1 * s, y + 0.25 * s - w * 0.3), (x + 0.15 * s, y + 0.25 * s)], A(PTER if sd < 0 else PTER_D, a))
    d.ell(x, y + 0.1 * s, 0.35 * s, 0.25 * s, A(PTER, a))
    hx, hy = x - 0.35 * s, y - 0.2 * s
    d.poly([(hx + 0.05 * s, hy - 0.15 * s), (hx + 0.7 * s, hy - 0.35 * s), (hx + 0.1 * s, hy + 0.02 * s)], A(PTER_D, a))   # crest
    d.poly([(hx - 0.05 * s, hy - 0.05 * s), (hx - 0.95 * s, hy + 0.12 * s), (hx - 0.05 * s, hy + 0.15 * s)], A(GOLD, a))    # beak
    d.circ(hx, hy, 0.2 * s, fill=A(PTER, a)); d.circ(hx - 0.03 * s, hy - 0.04 * s, 0.08 * s, fill=A(WHITE, a))
    d.circ(hx - 0.05 * s, hy - 0.03 * s, 0.04 * s, fill=A(EYEC, a))
    if mood == "smug": d.line([(hx - 0.13 * s, hy - 0.14 * s), (hx + 0.08 * s, hy - 0.1 * s)], A(PTER_D, a), 0.04 * s)
    if carry:
        bx, by = hx - 0.6 * s, hy + 0.12 * s
        d.line([(bx, by), (bx - 0.3 * s, by + 1.2 * s)], A((210, 210, 220), a), 0.05 * s); phone(d, bx - 0.32 * s, by + 1.35 * s, 0.22 * s, a)

def sauropod(d, x, y, s, t, a=1.0, look_up=0.0, col=(110, 160, 200)):
    """x,y = body centre."""
    dk = mix(col, (20, 30, 60), 0.3)
    d.poly([(x + 0.8 * s, y), (x + 2.4 * s, y + 0.5 * s), (x + 0.9 * s, y + 0.5 * s)], A(col, a))
    for i in range(4): d.rect(x - 0.8 * s + i * 0.45 * s, y + 0.3 * s, x - 0.55 * s + i * 0.45 * s, y + 1.2 * s, fill=A(dk if i % 2 else col, a), r=0.1 * s)
    d.ell(x, y, 1.0 * s, 0.65 * s, A(col, a)); d.ell(x - 0.2 * s, y - 0.3 * s, 0.5 * s, 0.15 * s, A(mix(col, WHITE, 0.3), 0.6 * a))
    hx, hy = x - 1.5 * s + look_up * 0.5 * s, y - 2.4 * s - look_up * 0.4 * s
    d.line([(x - 0.6 * s, y - 0.2 * s), (x - 1.2 * s, y - 1.4 * s), (hx, hy)], A(col, a), 0.4 * s)
    d.ell(hx - 0.15 * s, hy, 0.35 * s, 0.22 * s, A(col, a))
    d.circ(hx - 0.1 * s, hy - 0.06 * s, 0.09 * s, fill=A(WHITE, a)); d.circ(hx - 0.1 * s, hy - 0.06 * s - look_up * 0.04 * s, 0.045 * s, fill=A(EYEC, a))

def earth(d, x, y, r, t, a=1.0):
    glow(d, x, y, r * 1.25, (140, 220, 255), 0.5 * a)
    d.circ(x, y, r, fill=A((70, 150, 235), a))
    for cx, cy, rx, ry in ((-0.4, -0.3, 0.35, 0.22), (0.3, 0.1, 0.3, 0.38), (-0.2, 0.45, 0.25, 0.15), (0.5, -0.5, 0.15, 0.1)):
        d.ell(x + cx * r, y + cy * r, rx * r, ry * r, A((90, 200, 110), a))
    d.ell(x - 0.4 * r, y - 0.55 * r, 0.3 * r, 0.12 * r, A(WHITE, 0.4 * a))

def fireball(d, x, y, s, t, dx, dy, a=1.0, core=(255, 240, 180)):
    """flaming chunk moving in direction (dx,dy) (unit), tail behind."""
    for i in range(14):
        k = i / 14
        d.circ(x - dx * s * 4 * k + math.sin(t * 30 + i) * 4, y - dy * s * 4 * k + math.cos(t * 27 + i) * 4, s * (1 - k * 0.75), fill=A(mix((255, 220, 90), (220, 50, 30), k), a * (1 - k * 0.7)))
    d.circ(x, y, s * 0.75, fill=A(core, a))

def clock(d, x, y, r, t, a=1.0, spin=-12.0):
    d.circ(x, y, r * 1.08, fill=A((240, 110, 70), a)); d.circ(x, y, r, fill=A((252, 246, 230), a))
    for i in range(12):
        ang = i * math.pi / 6; d.line([(x + math.cos(ang) * r * 0.82, y + math.sin(ang) * r * 0.82), (x + math.cos(ang) * r * 0.92, y + math.sin(ang) * r * 0.92)], A(NAVYT, a), r * 0.05)
    a1 = t * spin; a2 = t * spin / 12
    d.line([(x, y), (x + math.cos(a1) * r * 0.75, y + math.sin(a1) * r * 0.75)], A(NAVYT, a), r * 0.06)
    d.line([(x, y), (x + math.cos(a2) * r * 0.5, y + math.sin(a2) * r * 0.5)], A(NAVYT, a), r * 0.09)
    d.circ(x, y, r * 0.07, fill=A((240, 110, 70), a))
def rew_icon(d, x, y, s, col, a=1.0):
    for k in (0, 1): d.poly([(x + (k - 0.5) * s, y - s * 0.5), (x + (k - 0.5) * s, y + s * 0.5), (x + (k - 1.5) * s, y)], A(col, a))
