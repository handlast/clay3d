# Flat 2D characters for 《喜欢吃蜗牛的“小角蛙”》: horned frog (Jingophrys, eyelid horns, ")(" belly mark, X-ray mode with
# skeleton + orange snail shells like the paper's micro-CT figure), land snail (Macrochlamys-like glossy amber shell),
# CT ring, map bits. No dark outlines: shapes separated by value, highlights and glow only. Eye/mouth lines may be dark.
import math, random
from chars import *          # base + fx + easing E, flatbg, rot, colors GOLD, NAVYT, ...

FROG = (176, 116, 70); FROG_D = (128, 80, 48); FROG_L = (214, 160, 108); BELLY = (238, 218, 168); MARK = (196, 150, 100)
SPOT = (120, 74, 44); PINKM = (255, 120, 140); IRIS = (232, 170, 60)
XR = (70, 150, 255); XR_D = (30, 70, 160); BONE = (225, 240, 255); SHELL = (255, 140, 40); SHELL_L = (255, 200, 110)
SN_SH = (196, 120, 46); SN_SHL = (240, 180, 96); SN_SHD = (150, 84, 30); SN_B = (160, 156, 150); SN_BL = (200, 196, 188)
FOREST1 = (20, 52, 50); FOREST2 = (6, 18, 22); MOSS = (70, 120, 60); MOSS_D = (44, 84, 44)
PAL = {  # body, dark, light, belly, mark/spots, horns
    "tan":   ((176, 116, 70), (128, 80, 48), (214, 160, 108), (238, 218, 168), (120, 74, 44)),
    "olive": ((128, 132, 70), (88, 94, 46), (176, 180, 110), (226, 222, 170), (70, 76, 36)),
    "rust":  ((196, 92, 60), (140, 60, 40), (236, 140, 100), (244, 214, 180), (110, 50, 30)),
    "grey":  ((130, 120, 116), (90, 82, 80), (176, 168, 160), (226, 220, 210), (70, 64, 62)),
    "choc":  ((120, 82, 60), (84, 56, 40), (168, 124, 96), (220, 196, 160), (60, 40, 28)),
    "green": ((96, 176, 92), (60, 128, 60), (150, 214, 130), (232, 240, 200), (30, 40, 30)),   # 黑斑蛙-ish
    "gold":  ((210, 160, 70), (160, 116, 40), (240, 200, 120), (246, 230, 190), (130, 90, 30)),
}

def spiral(d, x, y, r, col, a=1.0, turns=2.6, w=None, ang0=0.0):
    pts = []
    n = 60
    for i in range(n + 1):
        u = i / n; th = ang0 + u * turns * 2 * math.pi; rr = r * (0.12 + 0.88 * u)
        pts.append((x + math.cos(th) * rr, y + math.sin(th) * rr))
    d.line(pts, A(col, a), w or max(2, r * 0.14))

def shell(d, x, y, r, a=1.0, col=SN_SH, hi=SN_SHL, dk=SN_SHD, ang=0.0, glowk=0.0):
    """glossy coiled land-snail shell (side view)"""
    if a <= 0.01: return
    if glowk > 0:
        for i in range(6): d.circ(x, y, r * (1.0 + 0.18 * i), fill=A(col, 0.1 * glowk * (1 - i / 6)))
    d.ell(x, y, r * 1.08, r, A(dk, a)); d.ell(x - r * 0.04, y - r * 0.04, r * 1.0, r * 0.93, A(col, a))
    spiral(d, x + r * 0.12, y + r * 0.02, r * 0.78, hi, a * 0.9, 2.4, max(2, r * 0.12), ang0=ang)
    d.ell(x - r * 0.42, y - r * 0.5, r * 0.26, r * 0.13, A(WHITE, 0.55 * a))

def snail(d, x, y, s, t, a=1.0, face="happy", flip=1, crawl=0.0, hide=0.0, look=0.0):
    """x,y = foot contact centre. hide 0..1 pulls the body into the shell."""
    if a <= 0.01: return
    f = flip; bob = 3 * s * math.sin(t * 2.0 + x * 0.01) * crawl
    d.ell(x, y + 6 * s, 120 * s, 14 * s, A((0, 0, 0), 0.22 * a))
    bl = 1 - 0.85 * hide
    if bl > 0.05:
        # foot / body
        pts = []
        for i in range(21):
            u = i / 20; xx = x + f * lerp(-70, 120 * bl, u) * s; hh = (36 + 16 * math.sin(math.pi * u)) * s
            pts.append((xx, y - hh + 4 * s * math.sin(u * 12 + t * 6) * crawl))
        pts += [(x + f * 125 * bl * s, y), (x - f * 75 * s, y)]
        d.poly(pts, A(SN_B, a)); d.line([(x - f * 60 * s, y - 10 * s), (x + f * 100 * bl * s, y - 12 * s)], A(SN_BL, a * 0.6), 6 * s)
        # head + eye stalks
        hx, hy = x + f * 108 * bl * s, y - 40 * s + bob
        d.circ(hx, hy, 30 * s * max(0.4, bl), fill=A(SN_B, a))
        for k, (dx, ln) in enumerate(((-6, 62), (14, 70))):
            sw = 0.15 * math.sin(t * 3 + k) + look * 0.2
            ex, ey = hx + f * (dx + 10) * s + math.sin(sw) * ln * s * bl, hy - ln * s * bl
            d.line([(hx + f * dx * s, hy - 10 * s), (ex, ey)], A(SN_B, a), 9 * s)
            d.circ(ex, ey, 13 * s, fill=A(WHITE, a)); d.circ(ex + f * 3 * s + look * 4 * s, ey + 1 * s, 6.5 * s, fill=A(INK, a))
            if face in ("scared", "shock"): d.circ(ex, ey, 15 * s, outline=A(WHITE, a * 0.6), w=2)
        if face == "happy": d.arc(hx + f * 8 * s, hy + 4 * s, 12 * s, 9 * s, 20, 160, A(INK, a), 3.5 * s)
        elif face in ("scared", "shock"): d.ell(hx + f * 8 * s, hy + 10 * s, 7 * s, 10 * s, A(INK, a))
        elif face == "sus": d.line([(hx, hy + 8 * s), (hx + f * 18 * s, hy + 6 * s)], A(INK, a), 3.5 * s)
        if face in ("scared", "shock"): d.ell(hx - f * 30 * s, hy - 30 * s, 6 * s, 10 * s, A(CYAN, a))
    # shell on the back
    shell(d, x - f * 6 * s, y - 92 * s + bob * 0.5, 78 * s, a, ang=0.3 * f)

def _xf(px, py, x, y, s): return (x + px * s, y + py * s)

def frog(d, x, y, s, t, a=1.0, face="happy", pal="tan", xray=0.0, shells=0, shell_k=None, horns=True, mouth=0.0, look=0.0,
         blush=0.0, breathe=1.0, blink=True, belly_q=0.0, cheeks=0.0, spots=None, jaw_glow=0.0, squash=0.0):
    """Front view sitting frog; (x,y) = belly centre; ~300*s wide, ~330*s tall. xray 0..1. shells: count to draw in belly
    (shell_k: list of pop progress 0..1 each). mouth 0..1 opens wide. belly_q draws a glowing '?' on the belly."""
    if a <= 0.01: return
    body, dark, light, bel, spot = PAL[pal]
    k = cl(xray)
    if k > 0:
        body = mix(body, XR_D, k); dark = mix(dark, (20, 46, 120), k); light = mix(light, XR, k); bel = mix(bel, (80, 140, 230), k); spot = mix(spot, XR_D, k)
    ab = a * (1 - 0.45 * k)
    br = 1 + 0.02 * math.sin(t * 3.2) * breathe
    sy = (1 - squash) * br; sx = 1 + squash * 0.6
    P_ = lambda px, py: (x + px * s * sx, y + py * s * sy)
    d.ell(x, y + 128 * s, 170 * s, 22 * s, A((0, 0, 0), 0.25 * a * (1 - k)))
    # hind legs (folded, at sides)
    for sd in (-1, 1):
        cx, cy = P_(sd * 118, 78)
        d.ell(cx, cy, 70 * s, 54 * s, A(dark, ab)); d.ell(cx - sd * 4 * s, cy - 6 * s, 62 * s, 46 * s, A(body, ab))
        for j in range(3):   # toes, fringed
            fx, fy = P_(sd * (128 + 26 * j), 124)
            d.ell(fx, fy, 22 * s, 9 * s, A(light, ab))
        if spots is not False:
            d.circ(cx + sd * 10 * s, cy - 14 * s, 9 * s, fill=A(spot, ab * 0.8)); d.circ(cx - sd * 22 * s, cy + 8 * s, 7 * s, fill=A(spot, ab * 0.8))
    # body
    bx, by = P_(0, 22)
    d.ell(bx, by, 122 * s * sx, 108 * s * sy, A(dark, ab)); d.ell(bx, by - 4 * s, 116 * s * sx, 102 * s * sy, A(body, ab))
    ex_, ey_ = P_(0, 52)
    d.ell(ex_, ey_, 80 * s * sx, 70 * s * sy, A(bel, ab))
    if k < 0.6:   # light-brown ")(" chest mark (diagnostic for J. tanogogo)
        for sd in (-1, 1):
            d.arc(ex_ + sd * 74 * s, ey_ - 6 * s, 40 * s, 52 * s, 140 if sd < 0 else -40, 220 if sd < 0 else 40, A(MARK, ab * (1 - k / 0.6)), 7 * s)
    # front arms
    for sd in (-1, 1):
        ax, ay = P_(sd * 60, 30); hx, hy = P_(sd * 74, 122)
        d.line([(ax, ay), (hx, hy)], A(dark, ab), 26 * s); d.line([(ax - sd * 3 * s, ay), (hx - sd * 2 * s, hy - 4 * s)], A(body, ab), 18 * s)
        for j in (-1, 0, 1): d.ell(hx + j * 14 * s, hy + 6 * s, 9 * s, 6 * s, A(light, ab))
    # head
    hx, hy = P_(0, -78)
    d.ell(hx, hy, 140 * s * sx, 78 * s * sy, A(dark, ab)); d.ell(hx, hy - 4 * s, 134 * s * sx, 72 * s * sy, A(body, ab))
    d.poly([P_(-26, -40), P_(26, -40), P_(0, -14)], A(body, ab))                     # pointed snout tip
    d.ell(hx, hy - 34 * s, 70 * s, 16 * s, A(light, ab * 0.55))                         # head highlight
    if spots is not False:
        for px_, py_ in ((-40, -60), (46, -70), (-8, -100), (20, 0), (-60, 10), (70, 30)): 
            q = P_(px_, py_); d.circ(q[0], q[1], 8 * s, fill=A(spot, ab * 0.7))
    # dorsolateral ridge lines
    for sd in (-1, 1): d.line([P_(sd * 40, -40), P_(sd * 60, 30)], A(light, ab * 0.5), 5 * s)
    # cheeks puff
    if cheeks > 0:
        for sd in (-1, 1): q = P_(sd * 110, -56); d.circ(q[0], q[1], 34 * s * cheeks, fill=A(light, ab))
    # mouth
    mx, my = P_(0, -46)
    if mouth > 0.02:
        mo = mouth
        d.ell(mx, my + 18 * s * mo, 108 * s, 40 * s * mo + 4 * s, A((90, 20, 40), a))
        d.ell(mx, my + 34 * s * mo, 60 * s, 18 * s * mo + 2 * s, A(PINKM, a))
    else:
        if face in ("happy", "proud", "smug", "love"): d.arc(mx, my - 26 * s, 112 * s, 36 * s, 25, 155, A(INK, a), 6 * s)
        elif face in ("shock", "scared"): d.ell(mx, my + 6 * s, 26 * s, 20 * s, A((90, 20, 40), a))
        elif face == "chew":
            w_ = 6 * math.sin(t * 18)
            d.line([(mx - 90 * s, my - 4 * s), (mx - 30 * s, my + w_ * s), (mx + 30 * s, my - w_ * s), (mx + 90 * s, my - 4 * s)], A(INK, a), 6 * s)
        elif face == "sus": d.line([(mx - 80 * s, my), (mx + 80 * s, my - 8 * s)], A(INK, a), 6 * s)
        else: d.arc(mx, my - 20 * s, 100 * s, 26 * s, 30, 150, A(INK, a), 6 * s)
    # eyes (domes on top) + eyelid horns
    bl = 1.0
    if blink and face not in ("shock", "scared"):
        ph = (t + x * 0.003) % 3.7
        if ph < 0.12: bl = 0.15
    for sd in (-1, 1):
        exx, eyy = P_(sd * 72, -128)
        d.circ(exx, eyy, 46 * s, fill=A(dark, ab)); d.circ(exx, eyy - 3 * s, 42 * s, fill=A(body, ab))
        if horns:   # small pointed tubercle on the outer edge of each upper eyelid
            d.poly([(exx + sd * 18 * s, eyy - 36 * s), (exx + sd * 54 * s, eyy - 70 * s), (exx + sd * 40 * s, eyy - 22 * s)], A(light if k < 0.5 else XR, ab))
        er = 30 * s * (1.18 if face in ("shock", "scared") else 1.0)
        if face in ("happy", "love") and bl > 0.5 and face != "love":
            d.circ(exx, eyy + 2 * s, er, fill=A(WHITE, a)); d.circ(exx + look * 8 * s, eyy + 4 * s, er * 0.55, fill=A(INK, a))
            d.circ(exx + look * 8 * s - 6 * s, eyy - 4 * s, er * 0.18, fill=A(WHITE, a))
        elif face == "proud" or face == "smug":
            d.circ(exx, eyy + 2 * s, er, fill=A(WHITE, a)); d.circ(exx + look * 8 * s, eyy + 8 * s, er * 0.55, fill=A(INK, a))
            d.d.chord((P(exx - er - 2), P(eyy + 2 * s - er - 2), P(exx + er + 2), P(eyy + 2 * s + er + 2)), 180, 360, fill=A(body, ab if k == 0 else a))
        elif face == "love":
            for q in (-1, 1): d.circ(exx + q * 8 * s, eyy - 2 * s, 12 * s, fill=A(PINKM, a))
            d.poly([(exx - 19 * s, eyy + 2 * s), (exx + 19 * s, eyy + 2 * s), (exx, eyy + 22 * s)], A(PINKM, a))
        else:
            d.ell(exx, eyy + 2 * s, er, er * bl, A(WHITE, a))
            if bl > 0.5:
                d.circ(exx + look * 8 * s, eyy + 4 * s, er * (0.4 if face in ("shock", "scared") else 0.55), fill=A(INK, a))
                d.circ(exx + look * 8 * s - 6 * s, eyy - 4 * s, er * 0.16, fill=A(WHITE, a))
        if face == "sus":
            d.line([(exx - sd * 30 * s, eyy - 40 * s), (exx + sd * 26 * s, eyy - 30 * s)], A(INK, a), 6 * s)
    if face in ("shock", "scared"):
        q = P_(150, -170); d.ell(q[0], q[1], 10 * s, 16 * s, A(CYAN, a))
    if blush > 0:
        for sd in (-1, 1): q = P_(sd * 96, -48); d.ell(q[0], q[1], 22 * s, 11 * s, A(PINKM, 0.6 * blush * a))
    # ---- X-ray skeleton + shells ----
    if k > 0.02:
        bo = A(BONE, a * k * 0.9); w = 6 * s
        d.arc(hx, hy + 6 * s, 112 * s, 56 * s, 200, 340, bo, w)                    # skull roof
        d.arc(hx, hy - 8 * s, 104 * s, 52 * s, 20, 160, bo, w)                       # jaw
        for sd in (-1, 1):
            q = P_(sd * 72, -128); d.circ(q[0], q[1], 34 * s, outline=bo, w=int(w * 0.8))   # orbits
            q2 = P_(sd * 104, -66); d.circ(q2[0], q2[1], 9 * s, fill=A(GOLD, a * k * jaw_glow)) if jaw_glow > 0 else None
        sp = [P_(0, -40 + i * 16) for i in range(9)]
        for i, q in enumerate(sp): d.ell(q[0], q[1], 13 * s, 6 * s, bo)
        for sd in (-1, 1):
            d.line([P_(sd * 10, 90), P_(sd * 70, 60), P_(sd * 150, 90), P_(sd * 120, 120)], bo, w)   # pelvis/femur/tibia
            d.line([P_(sd * 30, 0), P_(sd * 70, 50), P_(sd * 74, 118)], bo, w * 0.8)               # arm
            d.line([P_(sd * 14, -24), P_(sd * 90, -18)], bo, w * 0.8)                              # transverse process
        locs = [(-34, 48, 34), (38, 40, 32), (2, 92, 22)]   # two medium, one small
        for i in range(min(shells, 3)):
            kk = 1.0 if shell_k is None else cl(shell_k[i])
            if kk <= 0: continue
            px_, py_, r_ = locs[i]; q = P_(px_, py_)
            sc = 1 + 0.35 * math.sin(math.pi * cl(kk * 1.4)) if kk < 1 else 1
            shell(d, q[0], q[1], r_ * s * kk * sc, a, SHELL, SHELL_L, (200, 90, 20), ang=i * 1.3, glowk=0.9)
    if belly_q > 0:
        q = P_(0, 50); glow_disc(d, q[0], q[1], 70 * s, CYAN, belly_q * 0.6)
        d.text(q[0], q[1], "?", int(120 * s), A(CYAN, belly_q * a), k=1)

def glow_disc(d, x, y, r, col, a):
    for i in range(7):
        k = 1 - i / 7; d.circ(x, y, r * (0.3 + 0.9 * k), fill=A(col, a * 0.14 * (1.2 - k * 0.6)))

def frog_icon(d, x, y, s, a=1.0, pal="tan", face="happy", t=0.0, horns=True, grey=0.0):
    p = pal
    if grey > 0:
        PAL["_g"] = tuple(mix(c, (90, 96, 110), grey) for c in PAL[pal]); p = "_g"
    frog(d, x, y, s, t, a, face, p, horns=horns, breathe=0.0, blink=False)

def ct_ring(d, x, y, r, t, a=1.0, scan=0.0):
    d.circ(x, y, r * 1.15, fill=A((210, 225, 232), a)); d.circ(x, y, r * 1.06, fill=A((236, 244, 248), a))
    d.circ(x, y, r * 0.72, fill=A((24, 70, 84), a)); d.circ(x, y, r * 0.66, fill=A((14, 46, 58), a))
    d.arc(x, y, r * 0.9, r * 0.9, -60 + t * 120, 20 + t * 120, A(CYAN, a * 0.9), r * 0.06)
    if scan > 0:
        d.circ(x, y, r * 0.66, outline=A(CYAN, a * scan * 0.8), w=6)
    d.rect(x - r * 0.3, y - r * 1.08, x + r * 0.3, y - r * 0.96, fill=A(CYAN, a * 0.85), r=8)

def forest_night(d, t, top=FOREST1, bot=FOREST2, rain=0.0, seed=3):
    grad(d, top, bot)
    for i in range(7):   # distant tree trunks / mist
        xx = 60 + i * 160 + 20 * math.sin(i * 2.1)
        d.rect(xx - 22, 0, xx + 22, 1500, fill=A((10, 30, 30), 0.6))
    for i in range(5): d.ell(200 + i * 220, 700 + 60 * math.sin(i + t * 0.3), 300, 60, A((120, 170, 160), 0.05))
    if rain > 0:
        for i in range(70):
            u = (t * 1.6 + i * 0.137) % 1; xx = (i * 97) % 1200 - 60 + u * 60; yy = u * 2100 - 100
            d.line([(xx, yy), (xx + 8, yy + 46)], A((170, 210, 230), 0.28 * rain), 3)

def log_(d, x, y, w, a=1.0):
    d.ell(x, y + 40, w * 0.55, 60, A((60, 40, 30), a)); d.ell(x, y + 24, w * 0.53, 50, A((92, 62, 42), a))
    d.ell(x, y + 6, w * 0.5, 24, A(MOSS, a));
    for i in range(9): d.circ(x - w * 0.45 + i * w * 0.11, y + 4 + 8 * math.sin(i * 1.7), 22, fill=A(MOSS_D if i % 2 else MOSS, a))

def mtn(d, base, cols, a=1.0, seed=1, amp=260, y0=1100):
    r = random.Random(seed)
    for j, c in enumerate(cols):
        pts = [(-60, 1980)]; x = -60
        while x < 1160:
            pts.append((x, y0 + j * 120 - r.uniform(0.3, 1.0) * amp)); x += r.uniform(80, 180)
            pts.append((x, y0 + j * 120 - r.uniform(0.0, 0.4) * amp)); x += r.uniform(60, 140)
        pts.append((1160, 1980)); d.poly(pts, A(c, a))
