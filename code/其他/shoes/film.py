import sys, subprocess
from fx import *
from cues import *

SKIN = (255, 192, 150); SKIN_D = (226, 150, 112); SKIN_L = (255, 222, 196)
BONEC = (246, 236, 212); BONE_DK = (214, 196, 160); STRUT = (196, 140, 96); HOTC = (255, 150, 40); XRC = (90, 190, 255)
SHOE = (236, 70, 80); SHOE_D = (180, 40, 56); SOLE = (250, 250, 245); NAVYT = (24, 20, 40); GOOD = (110, 225, 130)
GOLD = (255, 200, 60); BARK = (120, 84, 54); LEAFC = (80, 160, 90); STONE = (170, 150, 120); STONE_D = (130, 112, 88)

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
def rpoly(d, pts, ax, ay, s, rot, fill):
    c, sn = math.cos(rot), math.sin(rot)
    d.poly([(ax + (x * c - y * sn) * s, ay + (x * sn + y * c) * s) for x, y in pts], fill)
def rell(d, cx, cy, rx, ry, ax, ay, s, rot, fill, n=28):
    rpoly(d, [(cx + rx * math.cos(i / n * 6.2832), cy + ry * math.sin(i / n * 6.2832)) for i in range(n)], ax, ay, s, rot, fill)
def rpt(x, y, ax, ay, s, rot):
    c, sn = math.cos(rot), math.sin(rot); return ax + (x * c - y * sn) * s, ay + (x * sn + y * c) * s

# ---------- trabecular talus ----------
def _pts(seed=3):
    r2 = random.Random(seed); out = []; g = 0.19
    for iy in range(-5, 6):
        for ix in range(-7, 10):
            ux = ix * g + r2.uniform(-.05, .05); uy = iy * g + r2.uniform(-.05, .05)
            inb = (ux / 1.04) ** 2 + (uy / 0.66) ** 2 < 1; inh = ((ux - 1.05) / 0.38) ** 2 + ((uy - 0.1) / 0.36) ** 2 < 1
            if inb or inh: out.append((ux, uy, r2.random(), r2.uniform(-0.3, 0.3), inh and not inb))
    return out
TP = _pts()
def talus(d, cx, cy, R, t, mood=None, a=1.0, wfn=None, hot=1.0, ang=None, show=None, sx=1.0, sy=1.0, look=0.0, base=0.62,
          col=BONEC, dk=BONE_DK, sc=STRUT, head=True, fr=0.45):
    d.ell(cx, cy, R * 1.2 * sx, R * 0.82 * sy, A(dk, a))
    if head: d.ell(cx + R * 1.05 * sx, cy + R * 0.12 * sy, R * 0.5 * sx, R * 0.48 * sy, A(dk, a))
    d.ell(cx - R * 0.03 * sx, cy - R * 0.03 * sy, R * 1.13 * sx, R * 0.75 * sy, A(col, a))
    if head: d.ell(cx + R * 1.02 * sx, cy + R * 0.1 * sy, R * 0.45 * sx, R * 0.43 * sy, A(col, a))
    for i, (ux, uy, r, jit, inh) in enumerate(TP):
        if inh and not head: continue
        w = wfn(ux, uy) if wfn else 0.0
        if r > base + 0.38 * w: continue
        k = 1.0 if show is None else show(i, ux, uy)
        if k <= 0: continue
        th = (ang(i, ux, uy) if ang else math.pi / 2) + jit * 0.45
        px, py = cx + ux * R * sx, cy + uy * R * sy
        c = mix(sc, HOTC, cl(w) * hot); L = 0.14 * R * k; cs, sn = math.cos(th), math.sin(th)
        d.line([(px - cs * L, py - sn * L), (px + cs * L, py + sn * L)], A(c, a), max(2, 0.06 * R * k))
        d.line([(px + sn * L * 0.6, py - cs * L * 0.6), (px - sn * L * 0.6, py + cs * L * 0.6)], A(c, 0.55 * a), max(1, 0.028 * R * k))
        d.circ(px, py, 0.045 * R * k, fill=A(c, a))
    d.ell(cx - R * 0.55 * sx, cy - R * 0.5 * sy, R * 0.32 * sx, R * 0.1 * sy, A(WHITE, 0.55 * a))
    if mood: face(d, cx - R * 0.05 * sx, cy + R * 0.02, R * fr, mood, a, look)
W_BACK = lambda ux, uy: cl((-ux - 0.1) / 0.55) - 0.6 * cl((ux - 0.2) / 0.5)
W_FRONT = lambda ux, uy: cl((ux - 0.1) / 0.55) - 0.6 * cl((-ux - 0.2) / 0.5)
W_MED = lambda ux, uy: cl((-ux) / 0.5) - 0.6 * cl(ux / 0.5)

# ---------- foot mascot (side view, toes to the right) ----------
FOOT_BODY = [(-0.2, -0.12), (0.35, -0.22), (1.5, 0.18), (1.72, 0.42), (1.66, 0.68), (-0.2, 0.68)]
def foot(d, x, gy, s, t, mood="chill", a=1.0, xr=0.0, shoe=0.0, hl=0.0, wfn=None, look=0.0, wink=0.0, sq=0.0, leg=2.0, blink=True):
    rot = 0.13 * shoe
    toe_b = 1.6 * math.sin(rot) + 0.68 * math.cos(rot)
    ay = gy - (toe_b + 0.1 * shoe) * s * (1 - sq * 0.3)
    skin_a = a * (1 - 0.6 * xr); sk = mix(SKIN, XRC, xr * 0.7); skd = mix(SKIN_D, mix(XRC, (0, 0, 0), 0.3), xr * 0.7)
    d.ell(x + 0.5 * s, gy + 6, 1.4 * s, 0.1 * s, A((0, 0, 0), 0.22 * a))
    # leg
    d.rect(x - 0.42 * s, ay - leg * s, x + 0.42 * s, ay + 0.15 * s, fill=A(skd, skin_a), r=0.42 * s)
    d.rect(x - 0.36 * s, ay - leg * s + 0.04 * s, x + 0.3 * s, ay + 0.1 * s, fill=A(sk, skin_a), r=0.36 * s)
    # foot
    for col, dx in ((skd, 0.0), (sk, -0.03)):
        rell(d, -0.22 + dx, 0.32 + dx, 0.42, 0.36, x, ay, s, rot, A(col, skin_a)); rpoly(d, [(px + dx, py + dx) for px, py in FOOT_BODY], x, ay, s, rot, A(col, skin_a))
        rell(d, 1.42 + dx, 0.45 + dx, 0.32, 0.24, x, ay, s, rot, A(col, skin_a))
    if shoe > 0.01:   # sneaker with raised heel
        sa = a * shoe * (1 - 0.55 * xr); sh = mix(SHOE, XRC, xr * 0.6); shd = mix(SHOE_D, XRC, xr * 0.5)
        bot = [rpt(px, 0.7, x, ay, s, rot) for px in (-0.66, -0.3, 0.4, 1.2, 1.85)]
        d.poly(bot + [(bot[-1][0], gy), (bot[0][0], gy)], A(SOLE, sa))
        d.rect(bot[0][0], gy - 0.06 * s, bot[-1][0], gy, fill=A((200, 200, 205), sa))
        up = [(-0.68, 0.0), (-0.45, -0.24), (0.3, -0.16), (1.45, 0.16), (1.88, 0.45), (1.86, 0.72), (-0.68, 0.72)]
        rpoly(d, up, x, ay, s, rot, A(shd, sa)); rpoly(d, [(px - 0.03, py - 0.02) for px, py in up], x, ay, s, rot, A(sh, sa))
        rell(d, -0.1, -0.18, 0.4, 0.08, x, ay, s, rot, A(mix(shd, (0, 0, 0), 0.3), sa))
        p0 = rpt(-0.5, 0.45, x, ay, s, rot); p1 = rpt(0.4, 0.2, x, ay, s, rot); p2 = rpt(1.2, 0.45, x, ay, s, rot)
        d.line([p0, p1, p2], A(WHITE, 0.9 * sa), 0.07 * s)
        for k in range(4):
            q0 = rpt(0.45 + k * 0.22, -0.05 + k * 0.07, x, ay, s, rot); q1 = rpt(0.6 + k * 0.22, 0.02 + k * 0.07, x, ay, s, rot)
            d.line([q0, q1], A(WHITE, sa), 0.05 * s)
    if xr > 0.01:   # bones
        ba = a * xr; bc = (235, 245, 255)
        glow(d, x, ay, 0.9 * s, XRC, 0.35 * ba)
        d.rect(x - 0.18 * s, ay - leg * s + 0.15 * s, x + 0.18 * s, ay - 0.24 * s, fill=A(bc, ba), r=0.1 * s)
        d.ell(x, ay - 0.27 * s, 0.27 * s, 0.11 * s, A(bc, ba))
        rell(d, -0.3, 0.36, 0.3, 0.22, x, ay, s, rot, A(bc, ba)); rell(d, 0.42, 0.14, 0.14, 0.13, x, ay, s, rot, A(bc, ba))
        for k in range(3):
            d.line([rpt(0.58, 0.14 + k * 0.08, x, ay, s, rot), rpt(1.42, 0.38 + k * 0.05, x, ay, s, rot)], A(bc, ba), 0.08 * s)
        for k in range(2): rell(d, 1.6, 0.42 + k * 0.08, 0.08, 0.04, x, ay, s, rot, A(bc, ba))
        tc = mix(bc, HOTC, hl)
        if hl > 0: glow(d, x, ay, 0.7 * s, HOTC, 0.6 * hl * ba)
        d.ell(x, ay - 0.02 * s, 0.33 * s, 0.2 * s, A(tc, ba))
        if wfn:
            for ux, uy, r, jit, inh in TP[::2]:
                if inh: continue
                w = wfn(ux, uy)
                if r > 0.4 + 0.5 * w: continue
                px, py = x + ux * 0.28 * s, ay - 0.02 * s + uy * 0.26 * s
                d.line([(px, py - 0.04 * s), (px, py + 0.04 * s)], A(mix((150, 110, 80), (230, 90, 20), cl(w)), ba), 0.025 * s)
    # face on the shin
    fy = ay - 1.05 * s; fr = 0.36 * s
    bl = blink and (t % 3.1) < 0.12
    if wink > 0.5 or bl:
        for s_ in (-1, 1):
            ex = x + s_ * fr * 0.36; ey = fy - fr * 0.12
            if s_ == 1 or bl: d.arc(ex, ey + fr * 0.08, fr * 0.17, fr * 0.12, 200, 340, A(INK, a), fr * 0.07)
            else: d.circ(ex, ey, fr * 0.17, fill=A(WHITE, a)); d.circ(ex, ey + fr * 0.02, fr * 0.09, fill=A(INK, a))
        mouth(d, x, fy + fr * 0.38, fr, "grin", a)
    else: face(d, x, fy, fr, mood, a, look)
    d.ell(x - 0.2 * s, ay - leg * s + 0.3 * s, 0.1 * s, 0.22 * s, A(WHITE, 0.3 * skin_a))
    return ay

# ---------- small props ----------
def footprint(d, cx, cy, s, col, a=1.0, mirror=1):
    d.ell(cx, cy + 0.9 * s, 0.36 * s, 0.42 * s, A(col, a)); d.ell(cx - 0.05 * s * mirror, cy - 0.25 * s, 0.48 * s, 0.6 * s, A(col, a))
    d.poly([(cx - 0.38 * s, cy + 0.85 * s), (cx + 0.36 * s, cy + 0.85 * s), (cx + 0.42 * s, cy - 0.1 * s), (cx - 0.5 * s, cy - 0.1 * s)], A(col, a))
    for k, (dx, dy, r) in enumerate([(-0.33, -1.02, 0.2), (-0.04, -1.06, 0.13), (0.16, -1.0, 0.11), (0.32, -0.9, 0.1), (0.44, -0.76, 0.09)]):
        d.circ(cx + dx * s * mirror, cy + dy * s, r * s, fill=A(col, a))
def mini_shoe(d, x, y, s, col=SHOE, a=1.0):
    d.rect(x - 0.55 * s, y + 0.12 * s, x + 0.6 * s, y + 0.32 * s, fill=A(SOLE, a), r=0.1 * s)
    d.poly([(x - 0.55 * s, y + 0.15 * s), (x - 0.5 * s, y - 0.32 * s), (x - 0.05 * s, y - 0.3 * s), (x + 0.6 * s, y + 0.02 * s), (x + 0.6 * s, y + 0.15 * s)], A(col, a))
    d.ell(x + 0.42 * s, y + 0.06 * s, 0.2 * s, 0.12 * s, A(col, a)); d.line([(x - 0.4 * s, y + 0.02 * s), (x + 0.3 * s, y + 0.04 * s)], A(WHITE, a), max(2, 0.07 * s))
def kid(d, x, y, s, t, pose, mood, a=1.0, col=(255, 210, 70), skin=SKIN, sil=None):
    if sil: col = skin = sil
    if pose == "climb":
        hip = (x, y - 0.5 * s); sh = (x + 0.06 * s, y - 0.95 * s); hd = (x + 0.02 * s, y - 1.2 * s)
        legs = [((x + 0.2 * s, y - 0.48 * s), (x + 0.24 * s, y - 0.25 * s)), ((x + 0.16 * s, y - 0.62 * s), (x + 0.24 * s, y - 0.45 * s))]
        arms = [(x + 0.26 * s, y - 1.3 * s), (x + 0.26 * s, y - 1.12 * s)]
    elif pose == "squat":
        hip = (x - 0.16 * s, y - 0.22 * s); sh = (x + 0.0 * s, y - 0.68 * s); hd = (x + 0.06 * s, y - 0.94 * s)
        legs = [((x + 0.16 * s, y - 0.36 * s), (x + 0.06 * s, y)), ((x + 0.12 * s, y - 0.32 * s), (x - 0.02 * s, y))]
        arms = [(x + 0.32 * s, y - 0.5 * s), (x + 0.3 * s, y - 0.42 * s)]
    else:
        sw = math.sin(t * 7)
        hip = (x, y - 0.5 * s); sh = (x + 0.04 * s, y - 0.95 * s); hd = (x + 0.06 * s, y - 1.2 * s)
        legs = [((x + 0.08 * s * sw, y - 0.25 * s), (x + 0.16 * s * sw, y)), ((x - 0.08 * s * sw, y - 0.25 * s), (x - 0.16 * s * sw, y))]
        arms = [(x - 0.15 * s * sw, y - 0.6 * s), (x + 0.15 * s * sw, y - 0.6 * s)]
    for kn, ft in legs:
        d.line([hip, kn, ft], A(skin, a), 0.11 * s); d.ell(ft[0] + 0.05 * s, ft[1], 0.09 * s, 0.045 * s, A(sil or SKIN_D, a))
    d.line([hip, sh], A(col, a), 0.26 * s); d.circ(hip[0], hip[1], 0.13 * s, fill=A(sil or (60, 90, 170), a))
    for hnd in arms: d.line([sh, hnd], A(skin, a), 0.09 * s); d.circ(hnd[0], hnd[1], 0.06 * s, fill=A(skin, a))
    d.circ(hd[0], hd[1], 0.2 * s, fill=A(skin, a))
    if sil:
        for hnd in arms: pass
        return
    d.d.chord((P(hd[0] - 0.21 * s), P(hd[1] - 0.24 * s), P(hd[0] + 0.21 * s), P(hd[1] + 0.06 * s)), 180, 360, fill=A((60, 40, 30), a))
    face(d, hd[0] + 0.03 * s, hd[1] + 0.03 * s, 0.16 * s, mood, a)
def tree(d, x, y, s, a=1.0):
    d.rect(x - 0.2 * s, y - 2.4 * s, x + 0.2 * s, y, fill=A(BARK, a), r=0.08 * s)
    for k in range(5): d.line([(x - 0.12 * s, y - 0.3 * s - k * 0.42 * s), (x + 0.05 * s, y - 0.4 * s - k * 0.42 * s)], A(mix(BARK, (0, 0, 0), 0.3), a), 0.04 * s)
    for cx, cy, r in [(-0.5, -2.5, 0.5), (0.5, -2.55, 0.5), (0, -2.85, 0.6)]: d.circ(x + cx * s, y + cy * s, r * s, fill=A(LEAFC, a))
def mitt(d, x, y, s, side, a=1.0):
    d.rect(x - 0.5 * s, y - 0.35 * s, x + 0.5 * s, y + 0.35 * s, fill=A(SKIN_D, a), r=0.3 * s)
    d.rect(x - 0.46 * s, y - 0.32 * s, x + 0.42 * s, y + 0.3 * s, fill=A(SKIN, a), r=0.28 * s)
    d.circ(x - side * 0.1 * s, y - 0.38 * s, 0.16 * s, fill=A(SKIN, a))
    for k in range(3): d.line([(x + side * 0.15 * s, y - 0.2 * s + k * 0.16 * s), (x + side * 0.42 * s, y - 0.2 * s + k * 0.16 * s)], A(SKIN_D, a), 0.04 * s)
def ground(d, y, col, top):
    d.rect(-50, y, OW + 50, OH + 50, fill=A(col, 1)); d.rect(-50, y, OW + 50, y + 22, fill=A(top, 1))
def lens(d, cx, cy, r, bg, a=1.0):
    glow(d, cx, cy, r * 1.25, WHITE, 0.35 * a); d.circ(cx, cy, r + 14, fill=A((230, 240, 255), a)); d.circ(cx, cy, r, fill=A(bg, a))

# ---------------- scenes ----------------
def s_hook(t, d):
    hit = t >= HOOK_HIT
    if not hit: grad(d, (16, 40, 80), (6, 14, 34))
    else: rays(d, t, (34, 120, 210), (14, 60, 140), n=20, cx=420, cy=1040)
    ground(d, 1200, (20, 40, 80), (60, 140, 220))
    xr = ease(pr(t, HOOK_HIT - 0.05, HOOK_HIT + 0.1))
    sq = 0.12 * math.exp(-max(t - HOOK_HIT, 0) * 6) * math.sin(max(t - HOOK_HIT, 0) * 35) if hit else 0
    mood = "chill" if not hit else ("scream" if t < 2.7 else "scared")
    ay = foot(d, 380, 1200, 200, t, mood, xr=xr, shoe=1.0, hl=xr * (0.6 + 0.4 * pulse(t, [HOOK_HIT] + HOOK_CLICKS, 5)), wfn=W_BACK if hit else None, sq=sq)
    # scanner beam sweeping down
    by = lerp(560, 1240, pr(t, 0.0, HOOK_HIT))
    if t < HOOK_HIT + 0.3:
        al = 1 - pr(t, HOOK_HIT, HOOK_HIT + 0.3)
        d.rect(180, by - 70, 900, by, fill=A(XRC, 0.18 * al)); d.rect(180, by - 8, 900, by + 8, fill=A((200, 240, 255), 0.95 * al))
        glow(d, 540, by, 260, XRC, 0.4 * al)
    if hit:   # magnifier: trabecular lattice clicks into new shape
        k = popk(t, HOOK_HIT + 0.1); cx, cy, r = 690, 640, 190 * k
        if k > 0.05:
            d.line([(380 + 20, ay - 10), (cx - r * 0.7, cy + r * 0.7)], A((230, 240, 255), 0.8 * k), 8)
            lens(d, cx, cy, r, (20, 50, 100))
            stage = sum(1 for h in HOOK_CLICKS if t >= h)
            target = [math.pi / 2, math.pi / 2 - 0.5, math.pi / 2 - 0.9][stage]
            jit = 0.25 * pulse(t, [HOOK_HIT] + HOOK_CLICKS, 9) * math.sin(t * 60)
            talus(d, cx - 20, cy, 120 * k, t, None, wfn=lambda ux, uy: W_BACK(ux, uy) * min(1, 0.4 + 0.3 * stage), ang=lambda i, ux, uy: target + jit + (0.25 if ux < 0 else -0.2) * stage / 2)
    sparks(d, 690, 640, t, HOOK_HIT, n=60, spd=1200, col=(170, 230, 255), seed=3)
    for i, h in enumerate(HOOK_CLICKS): sparks(d, 690, 640, t, h, n=20, spd=700, col=(255, 200, 120), seed=7 + i, life=0.6)
    if t < HOOK_HIT: d.text(540, 330, "X 光一照……", 100, A(XRC, 1), k=1)
    stamp(d, t, HOOK_HIT, "穿鞋改了你的骨头！", 540, 330, 82, WHITE)
def s_talus(t, d):
    grad(d, (30, 150, 150), (12, 84, 96)); ground(d, 1200, (14, 70, 80), (70, 190, 180))
    sq = 0.1 * pulse(t, WEIGHT, 7)
    hl = popk(t, TALUS_HIT)
    ay = foot(d, 420, 1200, 200, t, "scared" if t > WEIGHT[0] else "sus", xr=1.0, shoe=0.0, hl=hl, sq=sq, look=0.6)
    rings(d, 420, ay, t, [TALUS_HIT], HOTC, 1.0, 300)
    for i, h in enumerate(WEIGHT):
        u = pr(t, h - 0.35, h)
        if t > h - 0.35:
            for xx in (260, 580):
                yy = lerp(560, 780, ease(u)) + (0 if t < h else 30 * pulse(t, [h], 8))
                arrow(d, xx, yy - 200, xx, yy, YEL, 1.0, 24)
            if t > h: sparks(d, 420, ay, t, h, n=24, spd=600, col=(255, 210, 120), seed=20 + i, life=0.6)
    if t > WEIGHT[0]: d.text(420, 500, "全身重量", 56, A(YEL, ease(pr(t, WEIGHT[0], WEIGHT[0] + 0.2))), k=1)
    tag(d, 540, 340, "距骨：全身重量压在这", WHITE, popk(t, TAG_HIT), 50)
    if t < TAG_HIT: stamp(d, t, TALUS_HIT, "距骨", 540, 340, 120, (255, 200, 120))
def eiffel_segs(cx, by, h):
    L = lambda f: cx - (0.3 - 0.27 * (f ** 0.6)) * h; R_ = lambda f: cx + (0.3 - 0.27 * (f ** 0.6)) * h
    lv = [0, 0.12, 0.25, 0.4, 0.55, 0.7, 0.85, 0.94]; segs = []
    for j in range(len(lv) - 1):
        f0, f1 = lv[j], lv[j + 1]; y0, y1 = by - f0 * h, by - f1 * h
        segs += [((L(f0), y0), (L(f1), y1)), ((R_(f0), y0), (R_(f1), y1)), ((L(f0), y0), (R_(f1), y1)), ((R_(f0), y0), (L(f1), y1)), ((L(f1), y1), (R_(f1), y1))]
    return segs
def s_eif(t, d):
    grad(d, (255, 160, 80), (220, 84, 70))
    for i in range(8): d.circ(540, 1700, 400 + i * 160, outline=A(WHITE, 0.06), w=30)
    lens(d, 380, 820, 190, (255, 228, 190))
    n = len(TP); order = sorted(range(n), key=lambda i: (TP[i][1], TP[i][0]))
    rank = {i: k for k, i in enumerate(order)}
    def show(i, ux, uy):
        g = int(rank[i] / n * len(POPS)); return popk(t, POPS[min(g, len(POPS) - 1)] - 0.05)
    talus(d, 350, 820, 104, t, "happy" if t > POPS[4] else "chill", show=show, wfn=lambda ux, uy: 0.6 * pulse(t, POPS, 5))
    segs = eiffel_segs(770, 1130, 600)
    for j, (p0, p1) in enumerate(segs):
        g = int(j / len(segs) * len(POPS)); k = popk(t, POPS[min(g, len(POPS) - 1)])
        if k <= 0: continue
        mx_, my_ = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        q0 = (lerp(mx_, p0[0], k), lerp(my_, p0[1], k)); q1 = (lerp(mx_, p1[0], k), lerp(my_, p1[1], k))
        d.line([q0, q1], A((90, 40, 70), 1), 10 if j % 5 < 2 else 6)
    d.ell(770, 1130, 190, 22, A((0, 0, 0), 0.15))
    if t > POPS[-1]: d.line([(770, 530), (770, 490)], A((90, 40, 70), 1), 6)
    d.text(625, 820, "=", 100, A(WHITE, popk(t, EIF_TAGS[1])), k=1)
    tag(d, 380, 580, "骨小梁", WHITE, popk(t, EIF_TAGS[0]), 50, (200, 70, 50))
    tag(d, 770, 1185, "埃菲尔铁塔", WHITE, popk(t, EIF_TAGS[1]), 44, (200, 70, 50))
    stamp(d, t, EIF_TAGS[0] - 0.4, "骨头里是支架", 540, 330, 96, WHITE)
def s_reo(t, d):
    grad(d, (126, 76, 210), (66, 36, 140))
    for i in range(9):
        r = ((t * 160 + i * 140) % 1300); d.circ(540, 820, r, outline=A(WHITE, 0.12 * (1 - r / 1300)), w=36)
    turn = ease(pr(t, FLIP - 0.1, FLIP + 0.25)); fa = lerp(math.pi / 2, math.pi / 2 - 0.75, turn)
    # force arrow above the bone
    ax, ay_ = 540 + 260 * math.cos(fa + math.pi), 820 + 360 * math.sin(fa + math.pi) * 1.0
    arrow(d, lerp(540, 300, turn), 460, lerp(520, 420, turn), 640, YEL, 1.0, 26)
    d.text(lerp(680, 700, turn), 500, "受力", 56, A(YEL, 1), k=1)
    cols = sorted(set(round(p[0], 1) for p in TP))
    def ang(i, ux, uy):
        g = int((ux + 1.05) / 2.5 * len(GROUPS)); g = max(0, min(len(GROUPS) - 1, g))
        k = back(pr(t, GROUPS[g] - 0.05, GROUPS[g] + 0.15)); return lerp(math.pi / 2, math.pi / 2 - 0.75, k)
    sq = 0.06 * pulse(t, GROUPS, 9)
    talus(d, 460, 870, 165, t, "dizzy" if FLIP < t < GROUPS[3] else ("proud" if t > GROUPS[-1] else "scared"), ang=ang, sx=1 + sq, sy=1 - sq,
          wfn=lambda ux, uy: 0.8 * pulse(t, [GROUPS[max(0, min(7, int((ux + 1.05) / 2.5 * 8)))]], 6))
    stamp(d, t, GROUPS[-1], "重新排队！", 540, 330, 110, YEL)
def s_scan(t, d):
    k = pr(t, RISERS[0][0], SIL0)
    grad(d, mix((50, 74, 110), (20, 26, 44), k), mix((20, 30, 52), (8, 10, 20), k))
    cx, cy = 540, 560
    d.circ(cx, cy, 200, fill=A((210, 220, 236), 1)); d.circ(cx, cy, 150, fill=A((30, 44, 70), 1))
    sp = 4 + 10 * k; a0 = t * sp
    ex, ey = cx + 175 * math.cos(a0), cy + 175 * math.sin(a0)
    ox, oy = cx - 175 * math.cos(a0), cy - 175 * math.sin(a0)
    px, py = -math.sin(a0) * 80, math.cos(a0) * 80
    d.poly([(ex, ey), (ox + px, oy + py), (ox - px, oy - py)], A(XRC, 0.3))
    d.circ(ex, ey, 26, fill=A(XRC, 1)); d.rect(ox - 30, oy - 30, ox + 30, oy + 30, fill=A((120, 130, 150), 1), r=8)
    talus(d, cx - 10, cy, 52, t, None, col=(220, 236, 255), dk=(160, 190, 230), sc=(90, 130, 200))
    tag(d, 540, 800, "微 CT 扫描", XRC, 1.0, 36)
    # counters
    n1 = int(40 * cl(pr(t, *SHOE_CNT))); n2 = int(16 * cl(pr(t, *FOOT_CNT)))
    for i in range(n1):
        r_, c_ = divmod(i, 8); kk = popk(t, SHOE_CNT[0] + i / 40 * (SHOE_CNT[1] - SHOE_CNT[0])); mini_shoe(d, 212 + c_ * 42, 1000 + r_ * 44, 36 * kk, SHOE, 1)
    for i in range(n2):
        r_, c_ = divmod(i, 4); kk = popk(t, FOOT_CNT[0] + i / 16 * (FOOT_CNT[1] - FOOT_CNT[0])); footprint(d, 668 + c_ * 58, 1005 + r_ * 54, 17 * kk, SKIN, 1)
    if t > SHOE_CNT[0]:
        d.text(300, 920, f"{n1}", 96, A(WHITE, 1), k=1); tag(d, 430, 920, "穿鞋", SHOE, 1, 36, WHITE)
    if t > FOOT_CNT[0]:
        d.text(680, 920, f"{n2}", 96, A(WHITE, 1), k=1); tag(d, 810, 920, "赤脚", SKIN, 1, 36, NAVYT)
    if t >= SIL0: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.6))
def s_reveal(t, d):
    rays(d, t, (255, 196, 70), (240, 140, 40), n=22, cx=540, cy=860)
    glow(d, 540, 860, 520, (255, 240, 170), 0.5 * pulse(t, [BIG2], 2))
    for j, (cy, lab, col, wf, ico) in enumerate([(620, "穿鞋", SHOE, W_BACK, 0), (1010, "赤脚", (230, 120, 70), W_FRONT, 1)]):
        k = popk(t, BIG2 + j * 0.08)
        if k <= 0: continue
        cx = 610
        d.rect(190, cy - 150, 890, cy + 150, fill=A(WHITE, 0.35 * k), r=40)
        talus(d, cx, cy, 112 * k, t, "scared" if j == 0 else "happy", wfn=wf, hot=1.0, fr=0.42)
        tag(d, 280, cy - 70, lab, col, popk(t, REV_TAGS[j]), 44, WHITE)
        if ico == 0: mini_shoe(d, 280, cy + 40, 90 * k)
        else: footprint(d, 280, cy + 30, 58 * k, SKIN)
        d.text(cx - 160, cy + 125, "后", 34, A(NAVYT, k), k=1); d.text(cx + 200, cy + 125, "前", 34, A(NAVYT, k), k=1)
    sparks(d, 540, 820, t, BIG2, n=70, spd=1300, col=(255, 240, 160), seed=5)
    stamp(d, t, BIG2, "完全不一样！", 540, 330, 120, WHITE)
def s_shod(t, d):
    grad(d, (244, 96, 96), (170, 40, 64)); ground(d, 1200, (130, 30, 50), (255, 150, 140))
    p = pulse(t, SHOD_HITS, 6)
    ay = foot(d, 400, 1200, 190, t, "sus", xr=0.85, shoe=1.0, hl=popk(t, SHOD_HITS[0]), wfn=W_BACK, sq=0.08 * p)
    for i, h in enumerate(SHOD_HITS):
        if t > h - 0.3: arrow(d, 210, 700 + 60 * ease(pr(t, h - 0.3, h)), 270, 960 + 30 * p, YEL, 1, 22)
    lens(d, 690, 650, 180, (255, 236, 220), popk(t, SHOD - 0 + 0.15))
    k = popk(t, SHOD + 0.15)
    if k > 0.05:
        d.line([(430, ay - 10), (690 - 130 * k, 650 + 130 * k)], A(WHITE, 0.8 * k), 8)
        talus(d, 670, 650, 112 * k, t, None, wfn=W_BACK, hot=popk(t, SHOD_HITS[0]))
        glow(d, 600, 650, 120, HOTC, 0.6 * popk(t, SHOD_HITS[0]) * (0.6 + 0.4 * p))
        tag(d, 575, 560, "后侧", YEL, popk(t, SHOD_HITS[0]), 40)
    d.text(330, 1150, "鞋跟抬高", 34, A(WHITE, 0.95), k=1)
    stamp(d, t, SHOD_HITS[1], "堆在后面", 540, 330, 110, WHITE)
def s_medial(t, d):
    grad(d, (76, 146, 244), (40, 76, 176))
    for i in range(12): d.rect(0, 280 + i * 100, 1080, 283 + i * 100, fill=A(WHITE, 0.06))
    cx, cy, s = 540, 820, 230
    # shoe outline (top view) + foot inside
    d.ell(cx, cy + 0.9 * s, 0.5 * s, 0.56 * s, A(SHOE, 0.55)); d.ell(cx - 0.05 * s, cy - 0.35 * s, 0.62 * s, 0.86 * s, A(SHOE, 0.55))
    d.rect(cx - 0.55 * s, cy - 0.3 * s, cx + 0.5 * s, cy + 0.9 * s, fill=A(SHOE, 0.55), r=0.3 * s)
    footprint(d, cx, cy, s, SKIN)
    face(d, cx - 0.02 * s, cy - 0.32 * s, 0.32 * s, "happy" if t > MED_HITS[1] else "sus", 1)
    # talus top-view with medial struts
    tk = popk(t, MEDIAL + 0.1)
    talus(d, cx - 10, cy + 0.55 * s, 70 * tk, t, None, wfn=W_MED if t > MED_HITS[1] else None, hot=popk(t, MED_HITS[1]), head=False, sx=1.0, sy=1.0)
    if t > MED_HITS[1]: glow(d, cx - 70, cy + 0.55 * s, 140, HOTC, 0.6 * popk(t, MED_HITS[1]))
    for i, h in enumerate([MED_HITS[0], MED_HITS[2]]):
        u = ease(pr(t, h - 0.2, h + 0.3))
        if t > h - 0.2:
            yy = cy + (0.1 if i == 0 else -0.45) * s
            arrow(d, cx + 0.55 * s, yy, lerp(cx + 0.5 * s, cx - 0.62 * s, u), yy, YEL, 1, 20)
    tag(d, 270, 520, "大脚趾一侧", WHITE, popk(t, MED_HITS[1]), 40, (40, 80, 180))
    d.text(250, cy + 0.6 * s, "内侧", 44, A(WHITE, 1), k=1); d.text(830, cy + 0.6 * s, "外侧", 44, A(WHITE, 0.6), k=1)
    stamp(d, t, MED_HITS[0], "还偏内侧", 540, 330, 110, WHITE)
def s_bare(t, d):
    grad(d, (110, 196, 100), (40, 116, 64)); ground(d, 1200, (90, 70, 46), (120, 190, 90))
    tree(d, 790, 1200, 210)
    if t < SQUAT:
        step = sum(1 for h in CLIMB if t >= h); y0 = 1200 - step * 70 - 30 * pulse(t, CLIMB, 9)
        kid(d, 650 + 10, y0, 300, t, "climb", "happy" if step < 3 else "proud")
    else:
        u = pr(t, SQUAT, SQUAT + 0.25); yy = lerp(1200 - 210, 1200, ease(u))
        kid(d, 600, yy, 300, t, "squat" if u >= 1 else "climb", "proud" if u >= 1 else "scared")
        sparks(d, 600, 1200, t, SQUAT + 0.25, n=26, spd=600, col=(200, 170, 120), seed=13, life=0.6)
    lens(d, 340, 700, 160, (236, 255, 220))
    p = pulse(t, CLIMB + [SQUAT + 0.25] + SQ_BOB, 6)
    talus(d, 320, 700, 96, t, None, wfn=W_FRONT, hot=0.5 + 0.5 * p)
    glow(d, 420, 700, 110, HOTC, 0.4 + 0.4 * p)
    tag(d, 420, 600, "前侧", YEL, popk(t, CLIMB[0]), 40)
    tag(d, 770, 520, "爬树", WHITE, popk(t, CLIMB[0]) * (1 - pr(t, SQUAT, SQUAT + 0.1)), 44, (40, 116, 64))
    tag(d, 770, 520, "下蹲", WHITE, popk(t, SQUAT + 0.25), 44, (40, 116, 64))
    stamp(d, t, BARE + 0.2, "堆在前面", 540, 330, 110, WHITE)
def s_alive(t, d):
    grad(d, (252, 126, 176), (190, 60, 130))
    for i in range(9):
        r = ((t * 120 + i * 140) % 1300); d.circ(540, 820, r, outline=A(WHITE, 0.12 * (1 - r / 1300)), w=36)
    shapes = [(1.0, 1.0), (1.22, 0.78), (0.8, 1.22), (1.08, 0.94)]; stg = sum(1 for h in SQUEEZE if t >= h)
    k = back(pr(t, SQUEEZE[stg - 1], SQUEEZE[stg - 1] + 0.3)) if stg else 1
    a0 = shapes[max(stg - 1, 0)] if stg else shapes[0]; a1 = shapes[stg]
    sx = lerp(shapes[stg - 1][0] if stg else 1, shapes[stg][0], k) if stg else 1; sy = lerp(shapes[stg - 1][1] if stg else 1, shapes[stg][1], k) if stg else 1
    angs = [math.pi / 2, 0.15, math.pi / 2 + 0.2, math.pi / 2 - 0.6]
    ang0 = angs[max(stg - 1, 0)]; ang1 = angs[stg]
    R = 140; cx, cy = 490, 850
    talus(d, cx, cy, R, t, "dizzy" if pulse(t, SQUEEZE, 3) > 0.5 else "happy", sx=sx, sy=sy, ang=lambda i, ux, uy: lerp(ang0, ang1, k if stg else 1), fr=0.42)
    # mitts press on each squeeze
    for j, h in enumerate(SQUEEZE):
        nxt = SQUEEZE[j + 1] if j + 1 < len(SQUEEZE) else ANC
        pp = math.exp(-max(0, t - h) * 1.2) * (1 - pr(t, nxt - 0.15, nxt)) if t >= h else 0
        if j == 1: mitt(d, 470, cy - R * 0.82 * sy - 70 - 40 * (1 - pp), 130, 1, pp); mitt(d, 470, cy + R * 0.82 * sy + 70 + 40 * (1 - pp), 130, -1, pp)
        else:
            mitt(d, max(240, cx - R * 1.2 * sx - 60 - 40 * (1 - pp)), cy, 120, 1, pp); mitt(d, min(840, cx + R * 1.55 * sx + 60 + 40 * (1 - pp)), cy, 120, -1, pp)
    stamp(d, t, SQUEEZE[0], "骨头是活的", 540, 330, 110, WHITE)
    tag(d, 540, 1150, "一辈子都在改", WHITE, popk(t, SQUEEZE[2]), 44, (190, 60, 130))
def s_anc(t, d):
    grad(d, (240, 180, 96), (176, 112, 52))
    d.rect(-50, 800, OW + 50, OH + 50, fill=A((214, 160, 90), 1))
    for i in range(6): d.ell(200 + i * 160, 800, 120, 18, A((200, 140, 70), 1))
    path = [(560 + (40 if i % 2 else -40) - i * 10, lerp(1150, 880, i / 6)) for i in range(7)]
    for i, h in enumerate(PRINTS):
        k = popk(t, h)
        if k > 0: footprint(d, path[i][0], path[i][1], 40 * (1 - 0.4 * i / 6) * k, (150, 100, 50), 0.9, -1 if i % 2 else 1)
    wk = pr(t, ANC, BAL); hx = lerp(560, 700, wk)
    glow(d, hx, 650, 200, (255, 240, 200), 0.5); kid(d, hx, 820, 300, t, "walk", "chill", 1, sil=(120, 70, 40))
    k = popk(t, FOSSIL)
    if k > 0:
        talus(d, 300, 1070, 70 * k, t, None, col=STONE, dk=STONE_D, sc=(110, 92, 70))
        tag(d, 300, 940, "化石里的骨头", WHITE, k, 36, (140, 90, 40))
        d.text(420, 1010, "?", 80, A(WHITE, k * (0.7 + 0.3 * math.sin(t * 8))), k=1)
    stamp(d, t, PRINTS[0], "几百万年前", 540, 330, 110, WHITE)
def s_bal(t, d):
    grad(d, (126, 224, 194), (60, 160, 140))
    for i in range(8): d.circ(540, 760, 200 + i * 130, outline=A(WHITE, 0.07), w=24)
    cx, cy = 540, 680
    tilt = (0.25 * math.exp(-max(0, t - BAL_DROP[0]) * 2.2) * math.cos((t - BAL_DROP[0]) * 9) if t > BAL_DROP[0] else -0.15 * (1 - pr(t, BAL, BAL_DROP[0])))
    if t > BAL_SET: tilt *= math.exp(-(t - BAL_SET) * 5)
    d.rect(cx - 16, cy, cx + 16, 1150, fill=A((60, 90, 110), 1), r=8); d.rect(cx - 140, 1130, cx + 140, 1170, fill=A((60, 90, 110), 1), r=16)
    L = 290; lx, ly = cx - L * math.cos(tilt), cy - L * math.sin(tilt); rx, ry = cx + L * math.cos(tilt), cy + L * math.sin(tilt)
    d.line([(lx, ly), (rx, ry)], A((60, 90, 110), 1), 18); d.circ(cx, cy, 24, fill=A(GOLD, 1))
    for j, (px, py) in enumerate([(lx, ly), (rx, ry)]):
        d.line([(px, py), (px - 90, py + 220)], A((60, 90, 110), 1), 5); d.line([(px, py), (px + 90, py + 220)], A((60, 90, 110), 1), 5)
        d.d.chord((P(px - 120), P(py + 180), P(px + 120), P(py + 270)), 0, 180, fill=A((240, 250, 250), 1))
        k = popk(t, BAL_DROP[j]); drop = (1 - ease(pr(t, BAL_DROP[j] - 0.25, BAL_DROP[j]))) * 260
        if t > BAL_DROP[j] - 0.25:
            if j == 0: mini_shoe(d, px, py + 190 - drop, 110)
            else: footprint(d, px, py + 140 - drop, 40, SKIN)
    if t > BAL_SET: sparks(d, cx, cy, t, BAL_SET, n=30, spd=700, col=(255, 255, 255), seed=17, life=0.7)
    stamp(d, t, BAL_SET, "不是说穿鞋有害", 540, 330, 90, WHITE)
    tag(d, 540, 480, "骨头只是记了下来", WHITE, popk(t, BAL_TAG), 44, (40, 120, 100))
def s_end(t, d):
    rays(d, t, (255, 206, 90), (240, 150, 50), n=16, cx=480, cy=1100)
    ground(d, 1200, (170, 110, 40), (255, 220, 120))
    foot(d, 400, 1200, 180, t, "happy", wink=1.0 if WINK <= t < WINK + 0.5 else 0.0, sq=0.08 * pulse(t, [WINK, FINAL], 7), blink=False)
    bubble(d, 880, 640, "你今天走了几步？", 1, WHITE, NAVYT, popk(t, BUB), 44)
    stamp(d, t, FINAL, "骨头记得你怎么走", 540, 330, 84, WHITE)
    d.text(540, 1310, "Farrell et al., J. Anat. (2026)", 26, A(WHITE, 0.9))
    d.text(540, 1350, "DOI 10.1111/joa.70236", 26, A(WHITE, 0.9))
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

def subs(t, d):
    if t >= OUTRO: return
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            ls = wrap(d, s, 52, 670); n = len(ls); y0 = 1350 - (n - 1) * 70
            w = max(d.tlen(x, 52, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 44, 540 + w / 2, y0 + (n - 1) * 70 + 44, fill=A((15, 12, 26), 0.82 * al), r=22)
            for i, x in enumerate(ls): d.text(540, y0 + i * 70, x, 52, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇新发现"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)

SECS = [(0, HOOK_END, s_hook), (TALUS, EIF, s_talus), (EIF, REO, s_eif), (REO, SCAN, s_reo), (SCAN, BIG2, s_scan),
        (REVEAL, SHOD, s_reveal), (SHOD, MEDIAL, s_shod), (MEDIAL, BARE, s_medial), (BARE, ALIVE, s_bare), (ALIVE, ANC, s_alive),
        (ANC, BAL, s_anc), (BAL, OUTRO, s_bal), (OUTRO, 99, s_end)]
CUTS = [HOOK_END, EIF, REO, SCAN, BIG2, SHOD, MEDIAL, BARE, ALIVE, ANC, BAL, OUTRO]
def cam(t):
    z = 1.0 + 0.05 * pulse(t, HITS, 7) + 0.06 * pulse(t, [HOOK_HIT, BIG2], 3)
    for a, b in RISERS:
        if a <= t < b: z += 0.12 * eio(pr(t, a, b))
    amp = 26 * pulse(t, [HOOK_HIT, BIG2], 4) + 5 * pulse(t, HITS, 6)
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx, 960 + sy
def frame(t):
    img = Image.new("RGB", (W, H), (30, 20, 50)); d = D(img)
    for a, b, sf in SECS:
        if a <= t < b: sf(t, d); break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.08: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.5 * (1 - (t - c) / 0.08)))
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
