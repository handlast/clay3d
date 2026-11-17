import sys, subprocess
from fx import *
from cues import *

SEA = (255, 150, 56); SEA_D = (210, 98, 34); SEA_L = (255, 206, 120)
MUP = (168, 96, 222); MUP_D = (116, 56, 170); MUP_L = (214, 168, 250); HELM = (226, 196, 255)
SKIN = (255, 200, 160); SKIN_D = (226, 156, 120); NAIL = (255, 228, 214)
NAVYT = (24, 20, 40); GOOD = (90, 220, 120); BAD = (250, 70, 70); GOLD = (255, 200, 60)
BONEC = (236, 250, 255); XRC = (90, 200, 255); WOOD = (150, 96, 56); WOOD_D = (104, 64, 38); WOOD_L = (196, 140, 88)
SHELL = (236, 214, 176); SHELL_D = (196, 166, 124)

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
def check(d, x, y, s, k, col, a=1.0):
    p = [(x - s, y), (x - s * 0.3, y + s * 0.7), (x + s, y - s * 0.8)]
    if k <= 0: return
    if k < 0.5: d.line([p[0], (lerp(p[0][0], p[1][0], k * 2), lerp(p[0][1], p[1][1], k * 2))], A(col, a), s * 0.3)
    else: d.line([p[0], p[1], (lerp(p[1][0], p[2][0], (k - 0.5) * 2), lerp(p[1][1], p[2][1], (k - 0.5) * 2))], A(col, a), s * 0.3)
def cross(d, x, y, s, k, col, a=1.0):
    if k <= 0: return
    d.line([(x - s, y - s), (x - s + 2 * s * min(1, k * 2), y - s + 2 * s * min(1, k * 2))], A(col, a), s * 0.3)
    if k > 0.5: d.line([(x + s, y - s), (x + s - 2 * s * (k - 0.5) * 2, y - s + 2 * s * (k - 0.5) * 2)], A(col, a), s * 0.3)
def bubbles(d, t, a=0.5, n=22, col=WHITE, spd=0.18):
    for i in range(n):
        u = (t * spd + i / n) % 1; x = 200 + (i * 197) % 680 + 18 * math.sin(t * 2 + i); y = 1450 - u * 1250
        d.circ(x, y, 6 + i % 5 * 3, outline=A(col, a * math.sin(u * math.pi)), w=3)
def snow(d, t, a=0.5, n=40):
    for i in range(n):
        u = (t * 0.05 + i * 0.137) % 1; x = (i * 211) % 1080 + 14 * math.sin(t + i); y = u * 1920
        d.circ(x, y, 2 + i % 3, fill=A(WHITE, a * (0.4 + 0.6 * ((i * 7) % 5) / 5)))

# ---------------- seahorse body (unit coords, facing right) ----------------
def _cr(pts, n=8):
    out = []
    P_ = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for j in range(n):
            u = j / n
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * u + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u * u + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u ** 3) for k in range(3)))
    out.append(pts[-1]); return out
SPINE = _cr([(0.02, -0.84, 0.15), (-0.10, -0.64, 0.17), (-0.11, -0.40, 0.22), (-0.02, -0.14, 0.26), (0.03, 0.12, 0.24), (-0.03, 0.34, 0.16),
             (-0.12, 0.52, 0.10), (-0.10, 0.70, 0.075), (0.0, 0.80, 0.06), (0.12, 0.75, 0.05), (0.15, 0.63, 0.04), (0.08, 0.56, 0.032), (0.03, 0.62, 0.026)], 7)
BELLY = [i for i, p in enumerate(SPINE) if -0.32 < p[1] < 0.22]

def seahorse(d, x, y, s, t, col=SEA, dk=SEA_D, lt=SEA_L, mood="chill", a=1.0, crown=False, helmet=False, pouch=True, rot=0.0, fl=1, look=0.0, sq=0.0, fin=True):
    if a <= 0.01 or s < 2: return
    c, sn = math.cos(rot), math.sin(rot)
    def T(ux, uy):
        ux *= fl * (1 + sq); uy *= (1 - sq)
        return x + (ux * c - uy * sn) * s, y + (ux * sn + uy * c) * s
    # dorsal fin
    if fin:
        fx_, fy_ = T(-0.30, -0.22); fl_ = 0.06 * math.sin(t * 22)
        pts = [T(-0.24, -0.38)] + [T(-0.42 - 0.04 * math.sin(k + t * 18), -0.36 + k * 0.07 + fl_) for k in range(6)] + [T(-0.20, 0.0)]
        d.poly(pts, A(lt, 0.55 * a))
    # body tube: dark back layer, then main colour shifted to the front
    for (ux, uy, r) in SPINE:
        px, py = T(ux, uy); d.circ(px, py, r * s, fill=A(dk, a))
    for (ux, uy, r) in SPINE:
        px, py = T(ux + 0.025, uy - 0.01); d.circ(px, py, r * s * 0.86, fill=A(col, a))
    # head + snout
    hx, hy = T(0.06, -0.96); d.circ(hx, hy, 0.20 * s, fill=A(dk, a))
    for k in range(9):
        u = k / 8; px, py = T(lerp(0.16, 0.52, u), lerp(-0.94, -0.84, u)); d.circ(px, py, (0.075 if k < 8 else 0.09) * s, fill=A(dk, a))
    for k in range(9):
        u = k / 8; px, py = T(lerp(0.16, 0.52, u), lerp(-0.955, -0.855, u)); d.circ(px, py, (0.055 if k < 8 else 0.07) * s, fill=A(col, a))
    hx2, hy2 = T(0.08, -0.975); d.circ(hx2, hy2, 0.175 * s, fill=A(col, a))
    # body rings
    for i in range(3, len(SPINE) - 12, 4):
        ux, uy, r = SPINE[i]
        d.line([T(ux - r * 0.55, uy), T(ux + r * 0.75, uy - 0.02)], A(lt, 0.45 * a), max(2, 0.018 * s))
    if pouch:
        px, py = T(0.17, 0.02); d.ell(px, py, 0.13 * s, 0.17 * s, A(lt, 0.8 * a))
    # highlights
    for ux, uy in [(0.06, -0.3), (0.12, -0.05)]:
        px, py = T(ux, uy); d.ell(px, py, 0.05 * s, 0.09 * s, A(WHITE, 0.3 * a))
    if crown:
        for k in range(5):
            bx = -0.06 + k * 0.05; tip = T(bx + 0.01, -1.26 - 0.03 * (k % 2)); b0 = T(bx - 0.025, -1.1); b1 = T(bx + 0.035, -1.1)
            d.poly([b0, tip, b1], A(dk, a))
        px, py = T(0.04, -1.1); d.ell(px, py, 0.11 * s, 0.05 * s, A(dk, a))
    if helmet:
        px, py = T(0.03, -1.10); d.ell(px, py, 0.2 * s, 0.13 * s, A(HELM, a))
        px, py = T(-0.02, -1.15); d.ell(px, py, 0.08 * s, 0.035 * s, A(WHITE, 0.6 * a))
    # face: eye on head, mouth at snout tip
    ex, ey = T(0.11, -0.99); er = 0.085 * s
    mx, my = T(0.56, -0.85)
    if mood in ("happy", "proud"):
        d.arc(ex, ey + er * 0.4, er, er * 0.9, 200, 340, A(INK, a), er * 0.35)
    elif mood == "wink":
        d.arc(ex, ey + er * 0.4, er, er * 0.7, 200, 340, A(INK, a), er * 0.35)
    else:
        big = 1.3 if mood in ("shock", "scared") else 1.0
        d.circ(ex, ey, er * big, fill=A(WHITE, a))
        pr_ = 0.32 if mood == "shock" else 0.5
        oy = er * 0.35 if mood == "sad" else 0
        d.circ(ex + look * er * 0.4 * fl, ey + oy, er * pr_, fill=A(INK, a))
        d.circ(ex + look * er * 0.4 * fl + er * 0.18, ey + oy - er * 0.18, er * 0.12, fill=A(WHITE, a))
        if mood in ("smug", "sus"):
            d.d.chord((P(ex - er * 1.05), P(ey - er * 1.05), P(ex + er * 1.05), P(ey + er * 1.05)), 180, 360, fill=A(col, a))
            d.line([(ex - er, ey), (ex + er, ey)], A(dk, a), er * 0.25)
        if mood == "sad":
            b0 = T(0.04, -1.13); b1 = T(0.18, -1.10 - 0.06); d.line([b0, b1], A(INK, a), er * 0.3)
            tx, ty = T(0.10, -0.86); d.ell(tx, ty + (t * 60) % 40, er * 0.25, er * 0.38, A(XRC, a))
        if mood in ("angry", "sus"):
            b0 = T(0.02, -1.14); b1 = T(0.2, -1.07); d.line([b0, b1], A(INK, a), er * 0.32)
    if mood in ("shock", "scared"):
        d.ell(mx, my, 0.04 * s, 0.05 * s, A(INK, a))
        sx, sy = T(-0.12, -1.1); d.ell(sx, sy + (t * 50) % 30, 0.03 * s, 0.05 * s, A(XRC, a))
    elif mood in ("happy", "proud", "wink", "smug", "chill"):
        d.arc(mx - 0.02 * s * fl, my - 0.02 * s, 0.04 * s, 0.035 * s, 20, 160, A(INK, a), max(2, 0.016 * s))
    elif mood == "sad":
        d.arc(mx - 0.02 * s * fl, my + 0.03 * s, 0.04 * s, 0.03 * s, 200, 340, A(INK, a), max(2, 0.016 * s))
    return T

def muppet(d, x, y, s, t, **k):
    k.setdefault("helmet", True); return seahorse(d, x, y, s, t, MUP, MUP_D, MUP_L, **k)

def skeleton(d, x, y, s, t, kind="sea", a=1.0, hl_cage=0.0, hl_crown=0.0, col=BONEC):
    if a <= 0.01: return
    def T(ux, uy): return x + ux * s, y + uy * s
    glow(d, x, y, s * 0.9, XRC, 0.18 * a)
    # faint flesh ghost
    for (ux, uy, r) in SPINE[::2]:
        px, py = T(ux, uy); d.circ(px, py, r * s, fill=A(XRC, 0.08 * a))
    # vertebrae along the back edge
    for i in range(0, len(SPINE) - 2, 2):
        ux, uy, r = SPINE[i]; px, py = T(ux - r * 0.45, uy)
        d.rect(px - 0.035 * s, py - 0.02 * s, px + 0.035 * s, py + 0.02 * s, fill=A(col, a), r=0.015 * s)
    # skull ring + snout bone
    hx, hy = T(0.07, -0.97); d.circ(hx, hy, 0.17 * s, outline=A(col, a), w=max(2, 0.03 * s))
    d.line([T(0.2, -0.94), T(0.54, -0.85)], A(col, a), max(2, 0.04 * s))
    ex, ey = T(0.1, -0.99); d.circ(ex, ey, 0.05 * s, fill=A((20, 40, 80), a))
    if kind == "sea":
        cg = mix(col, GOOD, hl_cage)
        if hl_cage > 0: glow(d, *T(0.02, -0.05), 0.4 * s, GOOD, 0.5 * hl_cage * a)
        for i in BELLY[::3]:
            ux, uy, r = SPINE[i]; px, py = T(ux, uy)
            d.ell(px + 0.02 * s, py, r * s * 0.95, 0.035 * s, outline=A(cg, a), w=max(2, 0.022 * s))
        for side in (-1, 1):
            pts = [T(SPINE[i][0] + side * SPINE[i][2] * 0.95 + 0.02, SPINE[i][1]) for i in BELLY]
            d.line(pts, A(cg, a), max(2, 0.02 * s))
        cr = mix(col, GOOD, hl_crown)
        if hl_crown > 0: glow(d, *T(0.04, -1.16), 0.22 * s, GOOD, 0.6 * hl_crown * a)
        for k in range(5):
            bx = -0.06 + k * 0.05; d.poly([T(bx - 0.022, -1.11), T(bx + 0.01, -1.27 - 0.03 * (k % 2)), T(bx + 0.032, -1.11)], A(cr, a))
    else:
        # different belly arrangement: loose diagonal plates, no closed cage, smooth skull top
        for j, i in enumerate(BELLY[::4]):
            ux, uy, r = SPINE[i]; px, py = T(ux, uy)
            for side in (-1, 1):
                d.line([(px + side * r * s * 0.3, py - 0.03 * s), (px + side * r * s * 0.8, py + 0.03 * s)], A(col, 0.85 * a), max(2, 0.02 * s))
        d.arc(*T(0.05, -1.03), 0.17 * s, 0.14 * s, 200, 340, A(col, 0.8 * a), max(2, 0.025 * s))

def thumb(d, x, y0, y1, w, a=1.0):
    d.rect(x - w / 2, y1, x + w / 2, y0 + 200, fill=A(SKIN_D, a), r=w / 2)
    d.rect(x - w / 2 + 10, y1 + 6, x + w / 2 - 4, y0 + 200, fill=A(SKIN, a), r=w / 2 - 8)
    d.rect(x - w * 0.3, y1 + 26, x + w * 0.32, y1 + w * 0.75, fill=A(NAIL, a), r=w * 0.25)
    d.rect(x - w * 0.2, y1 + 40, x - w * 0.05, y1 + w * 0.5, fill=A(WHITE, 0.5 * a), r=12)
    for k in range(3): d.arc(x, y1 + (y0 - y1) * 0.55 + k * 14, w * 0.25, 10, 200, 340, A(SKIN_D, a), 4)

def shellb(d, x, y, r, rot, a=1.0, seed=0):
    c, sn = math.cos(rot), math.sin(rot)
    pts = []
    for k in range(24):
        u = k / 24 * 2 * math.pi; rr = r * (1 + 0.12 * math.cos(u * 2))
        px, py = math.cos(u) * rr, math.sin(u) * rr * 0.8 - (r * 0.25 if math.sin(u) < -0.9 else 0)
        pts.append((x + px * c - py * sn, y + px * sn + py * c))
    d.poly(pts, A(SHELL_D, a))
    d.poly([(x + (px - x) * 0.86 - 4, y + (py - y) * 0.86 - 4) for px, py in pts], A(SHELL, a))
    for k in range(5):
        u = -math.pi / 2 + (k - 2) * 0.35
        d.line([(x + math.sin(rot) * r * 0.7, y - math.cos(rot) * r * 0.7), (x + math.cos(u + rot) * r * 0.8 * 0 + math.cos(u + math.pi + rot) * r * 0.75, y + math.sin(u + math.pi + rot) * r * 0.75)], A(SHELL_D, 0.7 * a), 3)

def helix(d, x, y0, y1, t, k, a=1.0, w=90):
    if k <= 0: return
    yt = lerp(y0, y1, k); n = 26
    pts1, pts2 = [], []
    for i in range(n + 1):
        yy = lerp(y0, yt, i / n); ph = i * 0.55 + t * 5
        pts1.append((x + w * math.sin(ph), yy)); pts2.append((x + w * math.sin(ph + math.pi), yy))
        if i % 2 == 0:
            cc = [(255, 90, 110), (90, 220, 120), (90, 170, 255), (255, 210, 70)][(i // 2) % 4]
            d.line([pts1[-1], pts2[-1]], A(cc, a), 8)
    d.line(pts1, A((230, 240, 255), a), 12); d.line(pts2, A((180, 200, 255), a), 12)

def jar(d, x, y, w, h, liq, lab, a=1.0):
    d.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=A((220, 240, 255), 0.35 * a), r=40)
    d.rect(x - w / 2 + 14, y - h / 2 + 70, x + w / 2 - 14, y + h / 2 - 14, fill=A(liq, 0.6 * a), r=30)
    d.rect(x - w / 2 - 10, y - h / 2 - 30, x + w / 2 + 10, y - h / 2 + 20, fill=A((90, 90, 110), a), r=14)
    d.rect(x - w / 2 + 26, y - h / 2 + 90, x - w / 2 + 50, y + h / 2 - 40, fill=A(WHITE, 0.35 * a), r=12)
    tag(d, x, y + h / 2 + 60, lab, WHITE, a, 40)

def gantry(d, cx, cy, R, t, spd, a=1.0):
    d.circ(cx, cy, R + 50, fill=A((214, 224, 240), a)); d.circ(cx, cy, R, fill=A((24, 34, 60), a))
    d.circ(cx, cy, R + 50, outline=A((170, 186, 214), a), w=10)
    ang = t * spd
    ex, ey = cx + (R - 20) * math.cos(ang), cy + (R - 20) * math.sin(ang)
    ox, oy = cx - (R - 20) * math.cos(ang), cy - (R - 20) * math.sin(ang)
    px, py = -math.sin(ang) * R * 0.45, math.cos(ang) * R * 0.45
    d.poly([(ex, ey), (ox + px, oy + py), (ox - px, oy - py)], A(XRC, 0.25 * a))
    d.circ(ex, ey, 24, fill=A(XRC, a))
    d.circ(cx + (R + 25) * math.cos(-0.6), cy + (R + 25) * math.sin(-0.6), 12, fill=A(GOOD if int(t * 4) % 2 else BAD, a))

# ---------------- scenes ----------------
def s_hook(t, d):
    hit = t >= HOOK_HIT
    if not hit:
        grad(d, (20, 40, 60), (6, 12, 24))
    else:
        rays(d, t, (230, 70, 90), (150, 30, 70), n=20, cx=540, cy=860)
    # spotlight cone
    d.poly([(470, 0), (610, 0), (900, 1250), (180, 1250)], A((255, 250, 220), 0.12 if not hit else 0.08))
    d.ell(540, 1210, 330, 50, A((255, 250, 220), 0.18))
    jig = 0.04 * math.sin(t * 9)
    sq = 0.1 * math.exp(-max(0, t - HOOK_HIT) * 7) * math.sin(max(0, t - HOOK_HIT) * 40) if hit else 0
    y = 850 + 14 * math.sin(t * 3)
    if hit:
        muppet(d, 520, y, 380, t, mood="shock" if t < 2.4 else "sus", rot=jig, sq=sq, look=-0.5)
    # x-ray beam sweeping down
    if t < HOOK_HIT + 0.25:
        by = lerp(420, 1250, pr(t, 0.0, HOOK_HIT)); al = 1 - pr(t, HOOK_HIT, HOOK_HIT + 0.25)
    # mask: an orange "seahorse skin" that rips off and flies away
    u = pr(t, HOOK_HIT, HOOK_HIT + 0.9)
    if u < 1:
        mx = 520 + 600 * ease(u) ** 1.3; my = y - 900 * ease(u) + 1400 * u * u
        seahorse(d, mx, my, 380 * (1 + 0.25 * u), t, mood="happy" if not hit else "shock", crown=True, rot=jig + 2.6 * u, a=1 - u ** 3)
        if hit:   # tear edge strips
            for k in range(6):
                d.line([(mx - 160 + k * 50, my + 300), (mx - 140 + k * 50, my + 360 + 20 * (k % 2))], A(SEA_D, 1 - u), 10)
    if t < HOOK_HIT + 0.25:
        d.rect(180, by - 70, 900, by, fill=A(XRC, 0.2 * al)); d.rect(180, by - 8, 900, by + 8, fill=A((210, 245, 255), 0.95 * al)); glow(d, 540, by, 260, XRC, 0.4 * al)
    sparks(d, 640, 520, t, HOOK_HIT, n=60, spd=1300, col=(255, 220, 160), seed=3)
    if hit:
        for k, (qx, qy) in enumerate([(300, 560), (780, 640), (760, 1000)]):
            ka = popk(t, HOOK_HIT + 0.5 + k * 0.25)
            if ka > 0: d.text(qx, qy - 10 * math.sin(t * 6 + k), "?", int(90 * ka), A(YEL, ka), k=1)
    if t < HOOK_HIT: d.text(540, 330, "海马？", 130, A(WHITE, 1), k=1)
    stamp(d, t, HOOK_HIT, "假海马！", 540, 330, 150, YEL)

def s_same(t, d):
    grad(d, (60, 190, 230), (20, 110, 170)); bubbles(d, t, 0.4)
    for i in range(6): d.rect(0, 300 + i * 190, 1080, 304 + i * 190, fill=A(WHITE, 0.05))
    bob = 12 * math.sin(t * 3.5)
    p = pulse(t, CHECKS, 7)
    seahorse(d, 320, 840 + bob, 320, t, mood="smug", crown=True, sq=0.05 * p)
    muppet(d, 700, 840 - bob, 320, t, mood="sus" if t < CHECKS[2] else "happy", sq=0.05 * p, look=-0.6)
    tag(d, 320, 1150, "真海马", SEA_L, popk(t, SAME + 0.15), 38)
    tag(d, 700, 1150, "它", MUP_L, popk(t, SAME + 0.3), 38)
    rows = [(840 - 0.95 * 320, "马头"), (840 + 0.68 * 320, "卷尾巴"), (840 + 0.02 * 320, "育儿袋")]
    for i, (yy, lab) in enumerate(rows):
        k = popk(t, CHECKS[i])
        if k <= 0: continue
        d.line([(400, yy), (650, yy)], A(WHITE, 0.6 * k), 4)
        d.circ(540, yy, 44 * k, fill=A(GOOD, 1)); check(d, 540, yy + 4, 22, ease(pr(t, CHECKS[i], CHECKS[i] + 0.2)), WHITE)
        d.text(540, yy - 74, lab, 40, A(WHITE, k), k=1)
        rings(d, 540, yy, t, [CHECKS[i]], WHITE, 0.6, 160)
    stamp(d, t, CHECKS[2] + 0.2, "一模一样", 540, 330, 120, WHITE)
    if t < CHECKS[2] + 0.2: d.text(540, 330, "找不同？", 110, A(WHITE, ease(pr(t, SAME, SAME + 0.2))), k=1)

def s_tiny(t, d):
    grad(d, (255, 214, 90), (240, 150, 50))
    for i in range(10): d.circ(540, 1500, 300 + i * 150, outline=A(WHITE, 0.08), w=30)
    ty = lerp(1600, 0, ease(pr(t, THUMB - 0.3, THUMB + 0.1)))
    thumb(d, 360, 1220 + ty, 470 + ty, 220)
    tag(d, 360, 1190 + ty, "你的拇指", WHITE, 1, 36, (180, 90, 30))
    p = pulse(t, [MEASURE, TINY_POP], 6)
    shrink = 1 - 0.12 * ease(pr(t, TINY_POP, TINY_POP + 0.2))
    s = 290 * shrink; base = 1220
    my = base - 0.82 * s
    muppet(d, 700, my, s, t, mood="proud" if t < TINY_POP else "shock", sq=0.06 * p)
    # ruler + measuring bar
    top = my - 1.12 * s
    k = ease(pr(t, MEASURE - 0.3, MEASURE + 0.2))
    if k > 0:
        d.rect(860, lerp(base, top, k), 880, base, fill=A(BAD, 1), r=8)
        d.line([(830, top), (890, top)], A(BAD, k), 6)
        d.line([(500, 470), (890, 470)], A(WHITE, 0.8 * k), 4)
        for j in range(10):
            yy = 470 + j * 75
            d.line([(500, yy), (520, yy)], A(WHITE, 0.6 * k), 3)
    if t > TINY_POP:
        d.rect(560, top - 6, 860, top + 6, fill=A(WHITE, 0.6), r=6)
        arrow_k = popk(t, TINY_POP)
        d.text(700, (top + 470) / 2, "还差一截", 40, A(NAVYT, arrow_k), k=1)
    stamp(d, t, TINY_POP, "不到一拇指", 540, 330, 120, WHITE)
    if t < TINY_POP: d.text(540, 330, "多大？", 120, A(WHITE, ease(pr(t, TINY, TINY + 0.2))), k=1)

def s_drawer(t, d):
    grad(d, (120, 80, 50), (60, 38, 26))
    # cabinet of drawers
    for r_ in range(6):
        for c_ in range(3):
            x0 = 120 + c_ * 290; y0 = 260 + r_ * 220
            d.rect(x0, y0, x0 + 270, y0 + 200, fill=A(WOOD, 1), r=10)
            d.rect(x0 + 100, y0 + 90, x0 + 170, y0 + 110, fill=A(GOLD, 0.8), r=8)
    d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.35))
    # pulled-out drawer (perspective tray)
    k = ease(pr(t, DRAWER_OPEN - 0.25, DRAWER_OPEN + 0.1)); sh = 6 * pulse(t, [DRAWER_OPEN], 10)
    fy = lerp(640, 980, k) + sh
    top_y = fy - 400 * k
    d.poly([(250, top_y), (830, top_y), (920, fy), (160, fy)], A(WOOD_L, 1))
    d.poly([(280, top_y + 20), (800, top_y + 20), (880, fy - 10), (200, fy - 10)], A((236, 222, 196), 1))
    # shells + the fish
    if k > 0.3:
        r2 = random.Random(4)
        for i in range(9):
            sx_ = lerp(300, 780, ((i * 37) % 9) / 8); sy_ = lerp(top_y + 80, fy - 80, ((i * 53) % 7) / 6)
            if abs(sx_ - 560) < 150 and abs(sy_ - (top_y + fy) / 2) < 110: continue
            shellb(d, sx_, sy_, 46, r2.uniform(-0.5, 0.5))
        mood = "sad" if t > SAD else "sus"
        muppet(d, 560, (top_y + fy) / 2 + 10, 220, t, mood=mood, rot=-math.pi / 2 + 0.05 * math.sin(t * 2), fin=False)
    # drawer front with label
    d.rect(150, fy, 930, fy + 170, fill=A(WOOD, 1), r=12)
    d.rect(150, fy, 930, fy + 22, fill=A(WOOD_L, 1), r=8)
    lk = popk(t, LABEL)
    d.rect(330, fy + 40, 750, fy + 130, fill=A(WHITE, 1), r=10)
    d.text(540, fy + 86, "无脊椎动物", 54, A(NAVYT, 1), k=1)
    if lk > 0: d.rect(330, fy + 40, 750, fy + 130, outline=A(BAD, lk), w=8, r=10)
    if lk > 0: tag(d, 770, fy - 30, "放错了！", BAD, lk, 36, WHITE)
    if t > DUSTQ:
        for j, (qx, qy) in enumerate([(300, top_y - 60), (780, top_y - 40), (540, top_y - 120)]):
            ka = popk(t, DUSTQ + j * BEAT)
            d.text(qx, qy + 8 * math.sin(t * 5 + j), "?", int(80 * ka), A(WHITE, ka), k=1)
    for i in range(30):
        u = (t * 0.08 + i / 30) % 1; d.circ(200 + (i * 131) % 680, 1300 - u * 900, 3, fill=A((255, 240, 200), 0.4 * math.sin(u * math.pi)))
    stamp(d, t, LABEL, "进错抽屉", 540, 330, 120, WHITE)
    if t < LABEL: d.text(540, 330, "博物馆里", 110, A(WHITE, ease(pr(t, DRAWER, DRAWER + 0.2))), k=1)

def s_ct(t, d):
    k = pr(t, RISERS[0][0], SIL0)
    grad(d, mix((30, 60, 100), (12, 18, 36), k), mix((12, 24, 50), (4, 6, 14), k))
    for i in range(8): d.line([(180 + i * 103, 0), (180 + i * 103, 1920)], A(XRC, 0.05), 2)
    cx, cy = 540, 780
    gantry(d, cx, cy, 240, t, 3 + 14 * k)
    tx = lerp(-300, cx, ease(pr(t, TRAY - 0.2, TRAY + 0.5)))
    d.rect(tx - 330, cy + 20, tx + 330, cy + 60, fill=A((200, 210, 226), 1), r=14)
    d.rect(cx - 60, cy + 60, cx + 60, 1150, fill=A((150, 160, 184), 1), r=10)
    muppet(d, tx, cy - 20, 120, t, mood="scared" if t > ZZZ[0] else "sus", rot=-math.pi / 2, fin=False)
    if ZZZ[0] <= t < SIL0:
        zz = 1 - pr(t, SIL0 - 0.2, SIL0)
        for j in range(3):
            pts = [(260 + i * 10, 1100 + j * 40 + 16 * math.sin(i * 1.3 + t * 40 + j)) for i in range(57)]
            d.line(pts, A(XRC, 0.6 * zz), 4)
        d.text(540, 1020, "滋——", 48, A(XRC, zz), k=1)
    for i, h in enumerate(COUNT):
        if h <= t < h + BEAT:
            u = pr(t, h, h + BEAT)
            d.text(540, 330, "321"[i], int(170 * (1.3 - 0.3 * back(pr(t, h, h + 0.15)))), A(WHITE, 1 - u * 0.5), k=1)
    if t < COUNT[0]: d.text(540, 330, "拍个 CT", 110, A(WHITE, ease(pr(t, CT, CT + 0.2))), k=1)
    if t >= SHUTTER: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.75))

def screen_bg(d, t, c1=(14, 40, 80), c2=(6, 14, 34)):
    grad(d, c1, c2)
    for i in range(12): d.line([(0, 260 + i * 100), (1080, 260 + i * 100)], A(XRC, 0.06), 2)
    for i in range(9): d.line([(180 + i * 90, 0), (180 + i * 90, 1920)], A(XRC, 0.06), 2)
    yy = (t * 400) % 1300 + 250; d.rect(0, yy, OW, yy + 6, fill=A(XRC, 0.15))

def s_reveal(t, d):
    screen_bg(d, t)
    glow(d, 540, 820, 520, XRC, 0.5 * pulse(t, [BIG2], 2))
    k = popk(t, BIG2)
    hl = 0.6 + 0.4 * math.sin(t * 8)
    skeleton(d, 320, 860, 300 * k, t, "sea", 1, hl_cage=hl, hl_crown=hl)
    skeleton(d, 720, 860, 300 * k, t, "mup", 1)
    tag(d, 320, 1150, "海马", SEA, k, 38)
    tag(d, 720, 1150, "它", MUP_L, k, 38)
    for i, h in enumerate(XS):
        kk = ease(pr(t, h, h + 0.2)); bl = 0.75 + 0.25 * math.sin(t * 14)
        yy = [860, 860 - 1.1 * 300][i]
        cross(d, 730, yy, 56, kk, BAD, bl)
    sparks(d, 540, 820, t, BIG2, n=70, spd=1300, col=(170, 230, 255), seed=5)
    stamp(d, t, BIG2, "骨头不对！", 540, 330, 140, WHITE)

def s_detail(t, d):
    grad(d, (40, 170, 150), (16, 96, 96))
    for i in range(8): d.circ(540, 820, 200 + i * 130, outline=A(WHITE, 0.06), w=24)
    rows = [(610, "腹部骨板笼", 0), (1000, "头顶骨冠", 1)]
    for j, (cy, lab, kind) in enumerate(rows):
        k = popk(t, DETAIL + j * 0.12); km = popk(t, MARKS[j])
        if k <= 0: continue
        for side, cx in ((0, 340), (1, 740)):
            lens(d, cx, cy, 140 * k, (10, 34, 70))
            if kind == 0:
                if side == 0:
                    for q in range(5): d.ell(cx, cy - 80 + q * 40, 100 * k, 16 * k, outline=A(GOOD, 1), w=6)
                    d.line([(cx - 100 * k, cy - 80), (cx - 100 * k, cy + 80)], A(GOOD, 1), 6); d.line([(cx + 100 * k, cy - 80), (cx + 100 * k, cy + 80)], A(GOOD, 1), 6)
                else:
                    for q in range(4):
                        for sd in (-1, 1): d.line([(cx + sd * 30 * k, cy - 70 + q * 46), (cx + sd * 90 * k, cy - 50 + q * 46)], A(BONEC, 0.9), 6)
            else:
                if side == 0:
                    d.arc(cx, cy + 50, 100 * k, 80 * k, 190, 350, A(BONEC, 1), 8)
                    for q in range(5): d.poly([(cx - 70 + q * 32, cy - 10), (cx - 58 + q * 32, cy - 90 - 14 * (q % 2)), (cx - 44 + q * 32, cy - 10)], A(GOOD, 1))
                else:
                    d.arc(cx, cy + 50, 100 * k, 80 * k, 190, 350, A(BONEC, 1), 8)
        d.text(540, cy + 182, lab, 42, A(WHITE, k), k=1)
        check(d, 340, cy + 105, 26, ease(pr(t, MARKS[j], MARKS[j] + 0.2)), GOOD)
        cross(d, 740, cy, 70, ease(pr(t, MARKS[j], MARKS[j] + 0.2)), BAD, 0.8 + 0.2 * math.sin(t * 14))
        if km > 0: tag(d, 830, cy - 120, "没有", BAD, km, 34, WHITE)
        rings(d, 740, cy, t, [MARKS[j]], BAD, 0.7, 200)
    tag(d, 340, 425, "海马", SEA, 1, 34); tag(d, 740, 425, "它", MUP_L, 1, 34)
    stamp(d, t, MARKS[1], "两样都没有", 540, 300, 100, WHITE)

def s_dna(t, d):
    grad(d, (130, 80, 210), (60, 30, 130))
    d.rect(-50, 1110, OW + 50, 1150, fill=A((80, 50, 140), 1))
    k = popk(t, JARS)
    jar(d, 340, 860, 260 * k, 460 * k, (120, 220, 255), "酒精", k)
    jar(d, 740, 860, 260 * k, 460 * k, (240, 210, 90), "福尔马林", k)
    if k > 0.3:
        muppet(d, 340, 900 + 10 * math.sin(t * 2), 150, t, mood="happy" if t > HELIX else "chill", fin=False)
        muppet(d, 740, 900, 150, t, mood="sad", fin=False, a=0.8)
    cross(d, 740, 880, 80, ease(pr(t, FORMX, FORMX + 0.2)), BAD, 0.9)
    hk = ease(pr(t, HELIX, HELIX + 1.0))
    helix(d, 340, 640, 410, t, hk, 1, 60)
    if hk > 0: glow(d, 340, lerp(640, 410, hk), 120, (200, 240, 255), 0.5)
    tag(d, 600, 520, "能测 DNA", GOOD, popk(t, DNA_TAG), 40, WHITE)
    stamp(d, t, HELIX, "测出 DNA！", 540, 300, 110, WHITE)
    if t < HELIX: d.text(540, 300, "两个瓶子", 110, A(WHITE, ease(pr(t, DNA, DNA + 0.2))), k=1)

def s_tree(t, d):
    grad(d, (110, 200, 110), (40, 120, 70))
    gk = ease(pr(t, TREE, TREE + 0.6))
    # trunk + fork
    d.line([(540, 1250), (540, lerp(1250, 980, gk))], A(WOOD_D, 1), 40)
    if gk > 0.5:
        g2 = (gk - 0.5) * 2
        d.line([(540, 990), (lerp(540, 330, g2), lerp(990, 720, g2))], A(WOOD_D, 1), 30)
        d.line([(540, 990), (lerp(540, 760, g2), lerp(990, 700, g2))], A(WOOD_D, 1), 30)
    tag(d, 540, 1180, "海龙科", WHITE, gk, 38, (40, 110, 60))
    tag(d, 540, 1060, "最近的亲戚", GOLD, popk(t, LAND + 0.3), 30)
    # hippocampus branch: three real seahorses
    for i, (hx, hy) in enumerate([(250, 690), (330, 650), (410, 690)]):
        seahorse(d, hx, hy, 80 * popk(t, TREE + 0.3 + i * 0.1), t, crown=True, mood="sus" if t > JUMP else "chill", fin=False)
    tag(d, 300, 820, "海马属", SEA_L, popk(t, TREE + 0.4), 36)
    # the fish: sits on the seahorse branch, crouches, jumps over to the new branch
    if t < CROUCH:
        mx, my, sq, mood = 330, 545, 0, "sus"
    elif t < JUMP:
        mx, my, sq, mood = 330, 555, 0.15 * ease(pr(t, CROUCH, CROUCH + 0.2)), "angry"
    else:
        u = ease(pr(t, JUMP, LAND)); mx = lerp(330, 760, u); my = lerp(545, 610, u) - 240 * math.sin(math.pi * u)
        sq = 0.12 * pulse(t, [LAND], 8) if t > LAND else -0.08; mood = "happy" if t > LAND else "shock"
    muppet(d, mx, my, 130, t, mood=mood, sq=sq, fin=False)
    if t > LAND:
        sparks(d, 760, 680, t, LAND, n=30, spd=700, col=(255, 255, 200), seed=9, life=0.7)
        kk = popk(t, LAND)
        d.rect(545, 790, 895, 890, fill=A(WHITE, 0.95 * kk), r=20)
        d.text(720, 822, "Australyichthys", 36, A(MUP_D, kk), k=1)
        d.text(720, 864, "海布偶 · 新属", 32, A(NAVYT, kk), k=1)
        for j, nm in enumerate(["头盔头", "牛脖", "悖论"]):
            tag(d, 600 + j * 120, 940, nm, MUP_L, popk(t, LAND + 0.3 + j * 0.15), 28)
        d.text(720, 995, "属：比“种”大一级的一家子", 28, A(WHITE, popk(t, LAND + 0.15)), k=1)
    stamp(d, t, LAND, "新的属！", 540, 300, 120, WHITE)
    if t < LAND: d.text(540, 300, "查家谱", 110, A(WHITE, ease(pr(t, TREE, TREE + 0.2))), k=1)

def s_conv(t, d):
    grad(d, (240, 100, 160), (160, 40, 110))
    for i in range(9):
        r = ((t * 140 + i * 140) % 1300); d.circ(540, 900, r, outline=A(WHITE, 0.1 * (1 - r / 1300)), w=30)
    d.rect(200, 1100, 880, 1130, fill=A(WHITE, 0.8), r=14); d.text(540, 1170, "海龙科", 34, A(WHITE, 1), k=1)
    g = ease(pr(t, *GROW))
    for side, (x0, x1, ph) in enumerate([(320, 330, 0.0), (760, 750, 1.7)]):
        n = 40; pts = []
        for i in range(int(n * g) + 1):
            u = i / n; pts.append((lerp(x0, x1, u) + 70 * math.sin(u * 7 + ph) * (1 - u), lerp(1100, 760, u)))
        if len(pts) > 1: d.line(pts, A(WHITE, 1), 12)
        # different ancestors at the bottom: straight pipefish-like sticks
        d.rect(x0 - 70, 1050, x0 + 70, 1080, fill=A([(255, 220, 120), (140, 230, 255)][side], 1), r=14)
        if pts: d.circ(*pts[-1], 14, fill=A(WHITE, 1))
        fk = popk(t, FORM)
        if fk > 0:
            seahorse(d, x1, 620, 210 * fk, t, col=WHITE, dk=(250, 210, 230), lt=(255, 240, 248), mood="proud", crown=False, fin=False)
            rings(d, x1, 600, t, [FORM], WHITE, 0.7, 260)
    tag(d, 540, 620, "第 2 次", GOLD, popk(t, TWICE), 40)
    stamp(d, t, TWICE, "造了两次", 540, 300, 120, WHITE)
    if t < TWICE: d.text(540, 300, "同一身材", 110, A(WHITE, ease(pr(t, CONV, CONV + 0.2))), k=1)
    knowcard(d, t, CARD)
def knowcard(d, t, t0):
    k = popk(t, t0)
    if k <= 0: return
    cy = 960 + 40 * (1 - k); w = 660 * (0.7 + 0.3 * k)
    d.rect(540 - w / 2, cy - 130, 540 + w / 2, cy + 130, fill=A(WHITE, 0.97 * min(1, k * 1.5)), r=34)
    d.rect(540 - w / 2, cy - 130, 540 - w / 2 + 16, cy + 130, fill=A(GOLD, min(1, k * 1.5)), r=8)
    tag(d, 540, cy - 130, "一句话学会", GOLD, min(1, k * 1.5), 34)
    d.text(540, cy - 30, "长得像≠是亲戚", int(70 * k), A((150, 30, 90), min(1, k * 1.5)), k=1)
    d.text(540, cy + 50, "这叫：趋同演化", int(48 * k), A(NAVYT, min(1, k * 1.5)), k=1)
    d.text(540, cy + 100, "不同祖先，各自长成同一副身材", int(28 * k), A((110, 100, 130), min(1, k * 1.5)), k=1)

def s_lost(t, d):
    if t < MAP:
        grad(d, (40, 120, 200), (4, 14, 40)); snow(d, t, 0.4)
        sy = 470
        d.rect(-50, sy - 70, OW + 50, sy, fill=A((140, 210, 250), 1))
        # depth scale
        def dy(m): return sy + m / 140 * 700
        d.rect(250, dy(50), 900, dy(125), fill=A(WHITE, 0.08))
        for m in (0, 50, 125):
            d.line([(200, dy(m)), (250, dy(m))], A(WHITE, 0.9), 4); d.text(225, dy(m) - 26, f"{m} 米", 26, A(WHITE, 0.9), k=1)
        d.line([(225, dy(0)), (225, dy(140))], A(WHITE, 0.6), 4)
        # trawler + net
        u = ease(pr(t, *TRAWL)); bx = lerp(300, 820, u)
        d.poly([(bx - 110, sy - 50), (bx + 90, sy - 50), (bx + 60, sy + 10), (bx - 80, sy + 10)], A((230, 80, 60), 1))
        d.rect(bx - 40, sy - 110, bx + 20, sy - 50, fill=A(WHITE, 1), r=8)
        nx, ny = bx - 220, dy(95)
        d.line([(bx - 100, sy - 10), (nx + 60, ny - 60)], A(WHITE, 0.8), 4); d.line([(bx - 100, sy - 10), (nx + 60, ny + 60)], A(WHITE, 0.8), 4)
        d.poly([(nx + 60, ny - 70), (nx + 60, ny + 70), (nx - 130, ny + 20), (nx - 130, ny - 20)], A(WHITE, 0.25))
        for i in range(6): d.line([(nx + 60 - i * 32, ny - 70 + i * 8), (nx + 60 - i * 32, ny + 70 - i * 8)], A(WHITE, 0.5), 3)
        if t < CATCH:
            muppet(d, 640, dy(95) - 10 + 8 * math.sin(t * 3), 70, t, mood="chill", fin=False)
        else:
            muppet(d, nx - 30, ny - 10, 70, t, mood="shock", fin=False)
            sparks(d, nx, ny, t, CATCH, n=24, spd=500, col=WHITE, seed=21, life=0.6)
        tag(d, 720, dy(125) + 70, "拖网意外捞到", WHITE, popk(t, CATCH), 36, (20, 60, 120))
        d.text(540, 300, "50–125 米深", 100, A(WHITE, ease(pr(t, LOST, LOST + 0.2))), k=1)
    else:
        grad(d, (16, 40, 70), (8, 18, 36))
        for i in range(10): d.line([(180 + i * 80, 380), (180 + i * 80, 1180)], A(XRC, 0.06), 2)
        # stylised southern coastline (land above)
        cpts = [(160, 720), (260, 700), (330, 760), (420, 740), (480, 820), (540, 780), (600, 830), (660, 800), (740, 840), (820, 830), (920, 900)]
        d.poly([(160, 420)] + cpts + [(920, 420)], A((200, 170, 110), 1))
        d.line(cpts, A((240, 220, 170), 1), 6)
        d.text(540, 540, "澳大利亚南部", 40, A((110, 80, 40), 1), k=1)
        spots = [(250, 740), (330, 800), (420, 780), (500, 860), (600, 870), (700, 860), (830, 880)]
        for i, (h, (px, py)) in enumerate(zip(DOTS, spots)):
            kk = popk(t, h)
            if kk <= 0: continue
            glow(d, px, py, 60, (255, 230, 120), 0.6 * kk); d.circ(px, py, 16 * kk, fill=A(YEL, 1))
            rings(d, px, py, t, [h], YEL, 0.7, 120)
        n = sum(1 for h in DOTS if t >= h)
        d.line([(250, 1000), (830, 1000)], A(WHITE, 0.8), 4)
        for xx in (250, 830): d.line([(xx, 985), (xx, 1015)], A(WHITE, 0.8), 4)
        d.text(540, 1050, "2500 多公里海岸线 · 跨约 65 年", 34, A(WHITE, 0.95), k=1)
        d.text(540, 300, f"只有 {n} 个", 120, A(YEL, 1), k=1) if n else None
        if t > DOTS[-1] + 0.2: tag(d, 540, 1140, "没人见过活的", BAD, popk(t, DOTS[-1] + 0.2), 40, WHITE)

def s_alive(t, d):
    grad(d, (8, 20, 50), (2, 4, 12)); snow(d, t, 0.35)
    for j in range(3):
        u = ((t - ALIVE) * 0.6 + j / 3) % 1
        d.circ(540, 820, 80 + u * 520, outline=A(XRC, 0.25 * (1 - u)), w=6)
    ek = ease(pr(t, EYES, EYES + 0.3))
    blink = (t % 2.2) < 0.12
    sil = 0.3 * ease(pr(t, EYES + 0.3, EYES + 1.5))
    if sil > 0: seahorse(d, 520, 860, 300, t, mix((6, 14, 36), MUP, sil), mix((6, 14, 36), MUP_D, sil), mix((6, 14, 36), MUP_L, sil), mood="chill", helmet=False, fin=False)
    ex, ey = 520 + 0.11 * 300, 860 - 0.99 * 300
    if ek > 0:
        glow(d, ex, ey, 110, (160, 255, 220), 0.8 * ek)
        if not blink: d.circ(ex, ey, 22 * ek, fill=A((200, 255, 230), 1)); d.circ(ex + 4, ey, 9 * ek, fill=A(INK, 1))
        else: d.line([(ex - 22, ey), (ex + 22, ey)], A((200, 255, 230), 1), 6)
    stamp(d, t, ALIVE_TAG, "失踪不是灭绝", 540, 300, 96, WHITE)
    if t < ALIVE_TAG: d.text(540, 300, "还在吗？", 110, A(WHITE, ease(pr(t, ALIVE, ALIVE + 0.3))), k=1)

def s_end(t, d):
    rays(d, t, (90, 200, 240), (40, 140, 200), n=16, cx=520, cy=900)
    bubbles(d, t, 0.4)
    y = 860 + 10 * math.sin(t * 3)
    wink = WINK <= t < WINK + 0.6
    mk = ease(pr(t, MASK_ON - 0.3, MASK_ON))
    muppet(d, 480, y, 330, t, mood="wink" if wink else "happy", sq=0.06 * pulse(t, [MASK_ON, FINAL], 7))
    if mk > 0:
        seahorse(d, 480, lerp(y - 700, y, mk), 330, t, mood="wink" if wink else "smug", crown=True, a=mk)
    bubble(d, 880, 520, "猜猜我是谁？", 1, WHITE, NAVYT, popk(t, BUB), 44)
    tag(d, 480, 1170, "头盔头海布偶", MUP_L, popk(t, FINAL), 36)
    stamp(d, t, FINAL, "冒牌海马", 540, 300, 110, WHITE)
    d.text(540, 1300, "Short & Harasti et al., J. Lost Species (2026)", 26, A(WHITE, 0.95))
    d.text(540, 1340, "DOI 10.66264/y1ffbcwb", 26, A(WHITE, 0.95))
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

def lens(d, cx, cy, r, bg, a=1.0):
    if r < 2: return
    glow(d, cx, cy, r * 1.25, WHITE, 0.3 * a); d.circ(cx, cy, r + 12, fill=A((230, 240, 255), a)); d.circ(cx, cy, r, fill=A(bg, a))

def subs(t, d):
    if t >= OUTRO: return
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70
            w = max(d.tlen(x, 52, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 44, 540 + w / 2, y0 + (n - 1) * 70 + 44, fill=A((15, 12, 26), 0.82 * al), r=22)
            for i, x in enumerate(ls): d.text(540, y0 + i * 70, x, 52, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇新发现"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)

SECS = [(-1, SAME, s_hook), (SAME, TINY, s_same), (TINY, DRAWER, s_tiny), (DRAWER, CT, s_drawer), (CT, BIG2, s_ct),
        (BIG2, DETAIL, s_reveal), (DETAIL, DNA, s_detail), (DNA, TREE, s_dna), (TREE, CONV, s_tree), (CONV, LOST, s_conv),
        (LOST, ALIVE, s_lost), (ALIVE, OUTRO, s_alive), (OUTRO, 99, s_end)]
def cam(t):
    z = 1.0 + 0.04 * pulse(t, HITS, 7) + 0.08 * pulse(t, [HOOK_HIT, BIG2], 3)
    for a, b in RISERS:
        if a <= t < b: z += 0.12 * eio(pr(t, a, b))
    if ALIVE <= t < OUTRO: z += 0.06 * eio(pr(t, ALIVE, OUTRO))
    amp = 28 * pulse(t, [HOOK_HIT, BIG2], 4) + 5 * pulse(t, HITS, 6)
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx, 900 + sy
def frame(t):
    img = Image.new("RGB", (W, H), (30, 20, 50)); d = D(img)
    if SIL0 + 0.06 <= t < BIG2:
        img = Image.new("RGB", (W, H), (0, 0, 0)); d = D(img)
        d.text(540, 900, "……", 80, A(WHITE, 0.5), k=1)
    else:
        for a, b, sf in SECS:
            if a <= t < b: sf(t, d); break
        z, cx, cy = cam(t)
        cw, ch = W / z, H / z
        x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
        img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
        for c in CUTS + [SHUTTER]:
            if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - (t - c) / 0.1)))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"/tmp/mp_test_{float(ts):05.2f}.png")
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
