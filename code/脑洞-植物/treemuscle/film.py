import sys, subprocess
from fx import *
from cues import *

XFE = (222, 74, 52); FE_D = (160, 44, 40); FE_L = (255, 150, 90); BELLY = (255, 196, 120)
CREST = (255, 196, 40); CREST_D = (230, 130, 30); BEAK = (255, 214, 92); BEAK_D = (214, 150, 50); LEGC = (236, 150, 60)
TRX = (88, 140, 84); TRX_D = (58, 100, 62); TRX_L = (150, 196, 120)
PEACH = (255, 150, 110); PEACH_L = (255, 206, 160); PEACH_D = (232, 96, 86); LEAFC = (96, 180, 84); PIT = (150, 92, 60)
NAVYT = (24, 20, 40); GOOD = (90, 220, 120); BAD = (250, 70, 70); GOLD = (255, 200, 60); TURK = (140, 92, 60); TURK_D = (100, 64, 44)
BONE = (246, 236, 214); XR = (110, 220, 255)

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
def title(d, t, t0, s, y=330, size=110, col=WHITE):
    k = back(pr(t, t0, t0 + 0.22))
    if k > 0: d.text(540, y, s, int(size * (0.7 + 0.3 * k)), A(col, min(1, k * 1.4)), k=1)
def arrow(d, x0, y0, x1, y1, col, a=1.0, w=16):
    L = math.hypot(x1 - x0, y1 - y0) + 1e-6; ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    bx, by = x1 - ux * w * 2.4, y1 - uy * w * 2.4
    d.line([(x0, y0), (bx, by)], A(col, a), w)
    d.poly([(bx + nx * w * 1.6, by + ny * w * 1.6), (x1, y1), (bx - nx * w * 1.6, by - ny * w * 1.6)], A(col, a))
def star(d, x, y, r, col, a=1.0, n=9, rot=0):
    if r <= 1: return
    pts = []
    for i in range(n * 2):
        ang = rot + i * math.pi / n; rr = r if i % 2 == 0 else r * 0.55
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    d.poly(pts, A(col, a))
def sweat(d, x, y, s, a=1.0):
    d.circ(x, y, s, fill=A(CYAN, a)); d.poly([(x - s * 0.9, y - s * 0.3), (x, y - s * 2.2), (x + s * 0.9, y - s * 0.3)], A(CYAN, a))


# ---------------- tree character ----------------
BARK = (150, 100, 66); BARK_D = (112, 72, 48); BARK_L = (196, 146, 100)
LEAF = (86, 190, 96); LEAF_D = (50, 140, 76); LEAF_L = (150, 226, 130)
MUS = (240, 76, 96); MUS_L = (255, 150, 160); MUS_G = (170, 160, 170)
POT = (214, 110, 70); POT_D = (170, 80, 56); SOIL = (90, 60, 44)

def stem_pts(x0, y0, a0, L, kap, frac=0.6, n=28):
    pts = [(x0, y0, a0)]; x, y, a = x0, y0, a0; ds = L / n
    for i in range(n):
        if i / n < frac: a += kap * ds
        x += math.cos(a) * ds; y -= math.sin(a) * ds; pts.append((x, y, a))
    return pts
def rot(px, py, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang); dx, dy = px - cx, py - cy
    return cx + dx * c - dy * s, cy + dx * s + dy * c
def pot(d, x, y, s, ang=0.0, a=1.0):
    P_ = [(-0.75, 0), (0.75, 0), (0.55, 1.1), (-0.55, 1.1)]
    Q = [rot(x + u * s, y + v * s, x, y, ang) for u, v in P_]
    d.poly(Q, A(POT, a))
    R = [(-0.85, -0.05), (0.85, -0.05), (0.85, 0.22), (-0.85, 0.22)]
    d.poly([rot(x + u * s, y + v * s, x, y, ang) for u, v in R], A(POT_D, a))
    d.poly([rot(x + u * s, y + v * s, x, y, ang) for u, v in [(-0.7, -0.05), (0.7, -0.05), (0.6, 0.08), (-0.6, 0.08)]], A(SOIL, a))
def face(d, x, y, r, t, mood="happy", a=1.0, look=(0, 0)):
    ex = r * 0.32; ey = -r * 0.08; er = r * 0.17
    for sx in (-1, 1):
        cx, cy = x + sx * ex, y + ey
        if mood in ("happy", "proud"):
            d.arc(cx, cy + er * 0.4, er, er * 0.9, 200, 340, A(INK, a), er * 0.35)
        elif mood == "closed":
            d.line([(cx - er, cy), (cx + er, cy)], A(INK, a), er * 0.3)
        elif mood == "dizzy":
            for k in range(3): d.circ(cx, cy, er * (1 - k * 0.3), outline=A(INK, a), w=er * 0.18)
        else:
            big = 1.25 if mood in ("scared", "shock") else 1.0
            d.circ(cx, cy, er * big, fill=A(WHITE, a))
            d.circ(cx + look[0] * er * 0.4, cy + look[1] * er * 0.4, er * (0.4 if mood == "shock" else 0.55), fill=A(INK, a))
            d.circ(cx + look[0] * er * 0.4 - er * 0.18, cy + look[1] * er * 0.4 - er * 0.2, er * 0.14, fill=A(WHITE, a))
            if mood in ("worried", "scared"): d.line([(cx - er * sx * 1.1, cy - er * 1.5), (cx + er * sx * 0.9, cy - er * 1.15)], A(INK, a), er * 0.28)
    my = y + r * 0.3
    if mood in ("happy", "proud"): d.arc(x, my - r * 0.08, r * 0.2, r * 0.16, 20, 160, A(INK, a), r * 0.06)
    elif mood in ("worried", "scared", "shock"): d.ell(x, my, r * 0.09, r * 0.11, A(INK, a))
    elif mood == "strain": d.line([(x - r * 0.18, my), (x - r * 0.06, my - r * 0.05), (x + r * 0.06, my), (x + r * 0.18, my - r * 0.05)], A(INK, a), r * 0.05)
    else: d.line([(x - r * 0.12, my), (x + r * 0.12, my)], A(INK, a), r * 0.05)
    if mood in ("happy", "proud", "strain"):
        for sx in (-1, 1): d.ell(x + sx * r * 0.52, y + r * 0.18, r * 0.12, r * 0.07, A((255, 130, 150), 0.6 * a))
def crown(d, x, y, r, t, mood="happy", a=1.0, look=(0, 0), sway=0.0):
    for i in range(7):
        ang = i * 2 * math.pi / 7 + 0.3
        d.circ(x + math.cos(ang) * r * 0.62, y + math.sin(ang) * r * 0.55, r * 0.5, fill=A(LEAF_D if i % 2 else LEAF, a))
    d.circ(x, y, r * 0.78, fill=A(LEAF, a)); d.ell(x - r * 0.3, y - r * 0.4, r * 0.3, r * 0.16, A(LEAF_L, 0.7 * a))
    face(d, x, y + r * 0.05, r * 0.9, t, mood, a, look)
def stem(d, pts, w0, a=1.0, up=0.0, dn=0.0, up_col=MUS, dn_col=MUS, bulge=0.0):
    n = len(pts) - 1
    for i in range(n):
        (x0, y0, a0), (x1, y1, _) = pts[i], pts[i + 1]
        w = w0 * (1 - 0.45 * i / n)
        d.line([(x0, y0), (x1, y1)], A(BARK, a), w + 2); d.circ(x1, y1, w / 2 + 1, fill=A(BARK, a))
    for side, k, col in ((1, up, up_col), (-1, dn, dn_col)):
        if k <= 0.01: continue
        m = max(2, int(n * 0.65))
        Ls = []
        for i in range(m + 1):
            x, y, ang = pts[i]; w = w0 * (1 - 0.45 * i / n)
            nx, ny = -math.sin(ang) * side, -math.cos(ang) * side
            bl = 1 + bulge * math.sin(math.pi * i / m)
            off = w * 0.32 * bl
            Ls.append((x + nx * off, y + ny * off))
        bw = w0 * 0.3 * k * (1 + 0.6 * bulge)
        d.line(Ls, A(col, a), bw)
        for p in Ls[::3]: d.circ(p[0], p[1], bw / 2, fill=A(col, a))
def tree(d, x0, y0, a0, L, kap, t, mood="happy", w0=40, cr=110, a=1.0, up=0, dn=0, frac=0.6, look=(0, 0), arms=0.0, flex=0.0, bulge=0.0, up_col=MUS, dn_col=MUS):
    pts = stem_pts(x0, y0, a0, L, kap, frac)
    stem(d, pts, w0, a, up, dn, up_col, dn_col, bulge)
    tx, ty, ta = pts[-1]
    if arms > 0:
        j = int(len(pts) * 0.72); ax, ay, aa = pts[j]
        for sd in (-1, 1):
            ang = aa + sd * (0.9 + 0.5 * flex)
            ex, ey = ax + math.cos(ang) * 110 * arms, ay - math.sin(ang) * 110 * arms
            hx, hy = ex + math.cos(aa) * 80 * arms * (0.3 + flex), ey - math.sin(aa) * 80 * arms * (0.3 + flex)
            d.line([(ax, ay), (ex, ey), (hx, hy)], A(BARK, a), 16 * arms)
            if flex > 0.05: d.circ((ax + ex) / 2 + math.cos(aa) * 14 * flex, (ay + ey) / 2 - math.sin(aa) * 14 * flex, 22 * flex * arms, fill=A(BARK_L, a))
            d.circ(hx, hy, 26 * arms, fill=A(LEAF, a))
    crown(d, tx + math.cos(ta) * cr * 0.6, ty - math.sin(ta) * cr * 0.6, cr, t, mood, a, look)
    return pts
def curl_arrow(d, pts, side, col, a=1.0, w=10, rev=False):
    m = int(len(pts) * 0.6); Ls = []
    for i in range(2, m):
        x, y, ang = pts[i]; nx, ny = -math.sin(ang) * side, -math.cos(ang) * side
        Ls.append((x + nx * 70, y + ny * 70))
    if rev: Ls = Ls[::-1]
    if len(Ls) > 2:
        d.line(Ls[:-1], A(col, a), w); arrow(d, Ls[-3][0], Ls[-3][1], Ls[-1][0], Ls[-1][1], col, a, w)

# ---------------- scenes ----------------
def lab(d, top, bot, y0=1150):
    grad(d, top, bot); d.rect(-20, y0, OW + 20, OH + 20, fill=A((236, 226, 210), 1)); d.rect(-20, y0, OW + 20, y0 + 18, fill=A((200, 186, 170), 1))
def s_hook(t, d):
    grad(d, (255, 90, 150), (120, 40, 140))
    for i in range(8): d.rect(0, 380 + i * 130, OW, 380 + i * 130 + 60, fill=A(WHITE, 0.05))
    d.rect(-20, 1180, OW + 20, OH, fill=A((90, 30, 100), 1))
    frz = t >= HOOK_STOP; tt = min(t, HOOK_STOP)
    k = ease(pr(tt, -0.4, HOOK_HIT)); fl = pulse(tt, [HOOK_HIT, qb(1), qb(2), qb(3)], 6)
    kap = lerp(0.0030, 0.0, k)
    pot(d, 540, 1100, 120)
    tree(d, 540, 1095, math.pi / 2 + lerp(0.9, 0, k), 430, -kap, tt, "shock" if frz else ("strain" if tt < HOOK_HIT else "proud"), 46, 130, arms=1.0, flex=min(1, pr(tt, HOOK_HIT - 0.1, HOOK_HIT) + fl), up=0, bulge=fl)
    if t >= HOOK_HIT:
        sparks(d, 540, 520, t, HOOK_HIT, 40, 1000, (255, 230, 140), 1, 4, 0.9)
    kk = back(pr(t, -0.2, HOOK_HIT)); k2 = pulse(t, [HOOK_HIT], 6)
    if kk > 0: d.text(540, 330, "树也有肌肉？", int(118 * (0.6 + 0.4 * kk) * (1 + 0.08 * k2)), A(YEL, 1), k=1)
    tag(d, 540, 460, "真实实验 · 2026", WHITE, popk(t, qb(1.5)), 34)
    if frz: glow(d, 540, 520, 140, WHITE, pr(t, HOOK_STOP, HOOKCUT))
def s_lay(t, d):
    lab(d, (120, 200, 240), (70, 150, 210))
    title(d, t, HOOKCUT, "实验：放倒小杨树", 300, 84)
    u = pr(t, HOOKCUT + 0.4, T["pull"] - 0.4)
    day = 1 + int(9 * u)
    tag(d, 540, 440, f"第 {day} 天", (255, 230, 120), popk(t, HOOKCUT + 0.2), 44)
    pot(d, 230, 1050, 110, math.pi / 2)
    kap = 0.0048 * ease(u)
    pts = tree(d, 235, 1050, 0.0, 520, kap, t, "worried" if u < 0.4 else "happy", 40, 100, frac=0.55, look=(1, -1))
    for i in range(4):
        x = 200 + i * 60; d.circ(x, 1135, 10, fill=A(WHITE, 0.3))
def s_pull(t, d):
    grad(d, (255, 210, 120), (240, 150, 70))
    title(d, t, T["pull"], "张力木", 300, 120, (190, 40, 60))
    k = popk(t, at("pull", 0.5)); bl = 0.4 + 0.4 * pulse(t, [at("pull", b) for b in (1, 2, 3, 4, 5, 6, 7)], 4)
    pot(d, 230, 1060, 110, math.pi / 2)
    pts = tree(d, 235, 1060, 0.0, 560, 0.0048, t, "strain", 58, 100, up=k, frac=0.55, bulge=bl if k > 0.5 else 0, look=(1, -1))
    if k > 0.5: curl_arrow(d, pts, 1, WHITE, k, 12)
    tag(d, 760, 480, "上侧：像肌肉收缩", MUS, popk(t, at("pull", 1)), 34, WHITE)
def s_q(t, d):
    grad(d, (130, 120, 200), (70, 60, 140)); d.rect(-20, 1150, OW + 20, OH, fill=A((60, 50, 110), 1))
    pot(d, 230, 1060, 110, math.pi / 2)
    tree(d, 235, 1060, 0.0, 540, 0.0048, t, "worried", 44, 100, frac=0.55, look=(-1, 1))
    sweat(d, 770, 420, 14, popk(t, at("q", 1)))
    q = popk(t, at("q", 1))
    if q > 0: d.text(780, 640, "？", int(220 * (1 + 0.08 * math.sin(t * 8))), A(YEL, q), k=1)
    title(d, t, T["q"], "腰弯了怎么办", 300, 96)
def sphere_bg(d, t, cx, cy, R, a=1.0):
    grad(d, (20, 30, 80), (8, 12, 40))
    for i in range(16):
        ang = i * 2 * math.pi / 16 + t * 0.3
        x0, y0 = cx + math.cos(ang) * (R + 220), cy + math.sin(ang) * (R + 220)
        x1, y1 = cx + math.cos(ang) * (R - 40), cy + math.sin(ang) * (R - 40)
        d.line([(x0, y0), (x1, y1)], A((255, 240, 160), 0.35 * a), 10)
    glow(d, cx, cy, R * 1.1, (255, 250, 210), 0.35 * a)
    d.circ(cx, cy, R, fill=A((250, 250, 230), 0.16 * a)); d.circ(cx, cy, R, outline=A((255, 250, 220), 0.8 * a), w=10)
def s_spin(t, d):
    cx, cy, R = 540, 860, 330
    sphere_bg(d, t, cx, cy, R)
    title(d, t, T["spin"], "旋转发光球", 300, 96, (255, 240, 160))
    u = t - T["spin"]; ang = u * 2.2
    d.ell(cx, cy + 40, 260, 30, A((180, 190, 220), 0.8))
    x0, y0 = rot(cx - 200, cy + 40, cx, cy + 40, 0)
    pts = stem_pts(cx - 200, cy + 40, 0.0, 330, 0.0055, 0.55)
    # rotate whole tree around its own axis: squash the drawing vertically by cos(ang)
    sc = math.cos(ang)
    P2 = [(x, cy + 40 + (y - cy - 40) * sc, a_ if sc >= 0 else -a_) for x, y, a_ in pts]
    stem(d, P2, 30)
    tx, ty, _ = P2[-1]; crown(d, tx + 20, ty - 45 * sc, 58, t, "dizzy" if u > 1.5 else "shock")
    for j in range(3):
        a0 = u * 3 + j * 2.1
        Ls = [(cx + math.cos(a0 + q * 0.08) * 120, cy + 40 + math.sin(a0 + q * 0.08) * 40) for q in range(10)]
        d.line(Ls, A((120, 200, 255), 0.9), 8)
    tag(d, 300, 1280 - 60, "绕自己转", (120, 200, 255), popk(t, at("spin", 1)), 32)
    tag(d, 780, 1280 - 60, "四面八方都有光", (255, 230, 120), popk(t, at("spin", 2)), 32)
def s_left(t, d):
    cx, cy, R = 540, 860, 330
    sphere_bg(d, t, cx, cy, R, 0.6)
    title(d, t, T["left"], "只剩一种感觉", 300, 96, (255, 240, 160))
    pts = tree(d, cx - 200, cy + 120, 0.0, 330, 0.0055, t, "closed", 30, 66, frac=0.55)
    items = [("上下", False, 0.5), ("光", False, 1.0), ("自己的弯度", True, 2.0)]
    for i, (s, ok, b) in enumerate(items):
        k = popk(t, at("left", b))
        if k <= 0: continue
        x = 300 + i * 240 if i < 2 else 540; y = 1130 if i < 2 else 1200
        if i == 2: y = 520; x = 540
        tag(d, x, y, s, GOOD if ok else (120, 120, 150), k, 36, WHITE)
        if not ok: cross(d, x + 80, y, 22, ease(pr(t, at("left", b), at("left", b) + 0.3)), BAD)
        else: glow(d, x, y, 120, GOOD, 0.4 * k)
def s_reveal(t, d):
    rays(d, t, (255, 210, 70), (255, 160, 50))
    k = pulse(t, [BIG2, at("reveal", 2), at("reveal", 4)], 5)
    pot(d, 230, 1060, 110, math.pi / 2)
    tree(d, 235, 1060, 0.35, 520, 0.0, t, "proud", 46, 110, arms=1.0, flex=0.6 + 0.4 * k, bulge=k)
    stamp(d, t, BIG2, "自己变直！", 540, 330, 140, (200, 40, 60))
    tag(d, 540, 470, "几周后", WHITE, popk(t, at("reveal", 1)), 40)
    if t >= BIG2:
        sparks(d, 540, 600, t, BIG2, 60, 1300, YEL, 1, 3, 1.2); sparks(d, 540, 600, t, BIG2 + 0.05, 40, 1000, WHITE, 1, 5, 1.0)
def s_flip(t, d):
    grad(d, (90, 200, 170), (40, 130, 120))
    title(d, t, T["flip"], "换一边长", 300, 110)
    u = pr(t, at("flip", 1), nxt("flip") - 0.5)
    kap = lerp(0.0048, 0.0, ease(u)); a0 = lerp(0.0, 0.35, ease(u))
    up = 1 - ease(pr(t, at("flip", 0.5), at("flip", 1.5))); dn = ease(pr(t, at("flip", 3.5), at("flip", 5)))
    pot(d, 230, 1060, 110, math.pi / 2)
    pts = tree(d, 235, 1060, a0, 520, kap, t, "happy", 58, 90, up=max(up, 0.6), dn=dn, frac=0.55, up_col=mix(MUS_G, MUS, up), look=(1, -1))
    tag(d, 700, 470, "上侧：停", MUS_G, popk(t, at("flip", 1)), 36, WHITE)
    tag(d, 760, 1210 - 40, "下侧：长出新的", MUS, popk(t, at("flip", 4)), 36, WHITE)
    if dn > 0.5: curl_arrow(d, pts, -1, WHITE, dn, 12, rev=True)
def s_anta(t, d):
    grad(d, (255, 120, 120), (200, 60, 90))
    title(d, t, T["anta"], "拔河", 300, 120)
    sw = 0.08 * math.sin((t - T["anta"]) * math.pi * 2)
    pot(d, 330, 1130, 90)
    tree(d, 330, 1125, math.pi / 2 + sw, 420, 0.0, t, "strain", 50, 100, up=1, dn=1, bulge=0.3 + 0.3 * abs(math.sin((t - T["anta"]) * math.pi * 2)))
    k = popk(t, at("anta", 1.5))
    if k > 0:
        sx_, sy_ = 700, 640; ex_, ey_ = 720, 900
        fl = 0.5 + 0.5 * math.sin((t - T["anta"]) * math.pi * 2)
        hx_, hy_ = ex_ + 170 * math.cos(-0.3 - 0.9 * fl), ey_ + 170 * math.sin(-0.3 - 0.9 * fl)
        d.line([(sx_, sy_), (ex_, ey_)], A(SKIN, k), 64); d.line([(ex_, ey_), (hx_, hy_)], A(SKIN, k), 54)
        d.circ(sx_, sy_, 34, fill=A(SKIN, k)); d.circ(ex_, ey_, 30, fill=A(SKIN_D, k)); d.circ(hx_, hy_, 36, fill=A(SKIN_D, k))
        d.ell(sx_ + 34, (sy_ + ey_) / 2, 26 + 14 * fl, 80, A(MUS, k)); d.ell(sx_ - 30, (sy_ + ey_) / 2, 26 + 14 * (1 - fl), 80, A((110, 150, 240), k))
        tag(d, 750, 1060, "手臂也是一对", WHITE, k, 30)
    tag(d, 540, 470, "一个拉弯，一个拉直", YEL, popk(t, at("anta", 3)), 36)
SKIN = (240, 190, 150); SKIN_D = (214, 156, 118)
def s_term(t, d):
    grad(d, (170, 110, 230), (100, 60, 170))
    stamp(d, t, T["term"], "本体感觉", 540, 320, 130, YEL)
    pot(d, 400, 1130, 100)
    tree(d, 400, 1125, math.pi / 2, 400, 0.0, t, "closed", 44, 110)
    k = popk(t, at("term", 1.5))
    if k > 0:
        for i, (bx, by, br) in enumerate(((560, 760, 14), (610, 720, 22))): d.circ(bx, by, br * k, fill=A(WHITE, 0.95 * k))
        d.ell(770, 640, 170 * k, 110 * k, A(WHITE, 0.95 * k))
        pts = stem_pts(690, 700, 0.0, 170, 0.006 * (0.5 + 0.5 * math.sin(t * 3)), 0.8, 12)
        d.line([(x, y) for x, y, _ in pts], A(BARK, k), 14)
    tag(d, 540, 470, "闭着眼也知道自己的姿势", WHITE, popk(t, at("term", 3)), 32)
def s_spring(t, d):
    grad(d, (80, 170, 240), (40, 100, 190))
    title(d, t, T["spring"], "不是弹回去", 300, 100)
    k1 = popk(t, at("spring", 0.5))
    if k1 > 0:
        x, y = 290, 760; pts = []
        for i in range(60):
            u = i / 59; pts.append((x + 60 * math.sin(u * 2 * math.pi * 5), y - 150 + 300 * u + 10 * math.sin(t * 10) * u))
        d.line(pts, A((210, 220, 230), k1), 10)
        cross(d, x, y, 110, ease(pr(t, at("spring", 1), at("spring", 1.4))), BAD)
        tag(d, x, y + 220, "弹簧回弹", (120, 120, 150), k1, 30, WHITE)
    k2 = popk(t, at("spring", 3))
    if k2 > 0:
        x, y, R = 760, 760, 170 * k2
        d.circ(x, y, R, fill=A(BARK, k2))
        for i in range(5): d.circ(x - 8 * i, y - 6 * i, R * (0.85 - i * 0.15), fill=A(mix(BARK_L, (255, 230, 190), i / 5), k2))
        d.d.chord((P(x - R * 0.82), P(y - R * 0.82), P(x + R * 0.82), P(y + R * 0.82)), 20, 160, fill=A(MUS, k2))
        d.circ(x - 10, y - 8, R * 0.18, fill=A((120, 80, 50), k2))
        tag(d, x, y + 220, "新长的木头", MUS, popk(t, at("spring", 4)), 30, WHITE)
        d.circ(x, y, R + 30, outline=A(WHITE, k2), w=14); d.line([(x + R * 0.8, y + R * 0.8), (x + R * 1.3, y + R * 1.3)], A(WHITE, k2), 24)
def s_use(t, d):
    u = t - T["use"]
    grad(d, (80, 90, 120), (40, 46, 70))
    for i in range(24):
        y = 300 + (i * 97) % 900; x = (u * 1600 + i * 233) % 1300 - 100
        d.line([(x, y), (x + 120, y + 10)], A(WHITE, 0.35), 5)
    gt = 0.12 * ease(pr(t, at("use", 3), at("use", 4)))
    d.poly([(-50, 1150 - 200 * gt), (OW + 50, 1150 + 200 * gt), (OW + 50, OH), (-50, OH)], A((90, 110, 70), 1))
    lean = 0.35 * math.sin(u * 4) * math.exp(-u * 0.25) if t < at("use", 3) else -gt * 2.2 * (1 - ease(pr(t, at("use", 4.5), at("use", 6.5))))
    pot(d, 540, 1100, 0.01)
    tree(d, 540, 1150, math.pi / 2 - lean, 460, lean * 0.002, t, "strain", 46, 120)
    tag(d, 300, 470, "风暴", (120, 140, 200), popk(t, at("use", 0.5)), 40, WHITE)
    tag(d, 780, 470, "滑坡", (170, 120, 80), popk(t, at("use", 3)), 40, WHITE)
    if pulse(t, [at("use", 1), at("use", 2.5)], 8) > 0.5: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.25))
def s_crop(t, d):
    grad(d, (140, 210, 250), (250, 230, 160)); d.rect(-20, 1100, OW + 20, OH, fill=A((150, 120, 60), 1))
    title(d, t, T["crop"], "庄稼倒伏", 300, 100, NAVYT)
    k = ease(pr(t, at("crop", 2.5), at("crop", 4)))
    for i in range(9):
        x = 200 + i * 85
        lodged = i < 5
        ang = math.pi / 2 - (1.2 if lodged else 0) * (1 - k) - 0.05 * math.sin(t * 2 + i)
        x1, y1 = x + math.cos(ang) * 380, 1100 - math.sin(ang) * 380
        d.line([(x, 1100), (x1, y1)], A((230, 190, 90), 1), 12)
        d.ell(x1, y1, 22, 40, A((240, 200, 100), 1))
    tag(d, 540, 470, "将来也许能少倒伏", GOOD, popk(t, at("crop", 2.5)), 36, WHITE)
def s_card(t, d):
    grad(d, (255, 214, 90), (240, 150, 50))
    for i in range(10): d.circ(540, 600, 160 + i * 140, outline=A(WHITE, 0.08), w=26)
    pot(d, 540, 820, 70)
    tree(d, 540, 815, math.pi / 2, 300, 0.0, t, "proud", 30, 80, arms=0.7, flex=0.8, bulge=0.4)
    k = popk(t, T["card"] + 0.1)
    if k <= 0: return
    al = min(1, k * 1.5); cy = 1040 + 40 * (1 - k); w = 700 * (0.7 + 0.3 * k)
    d.rect(540 - w / 2, cy - 150, 540 + w / 2, cy + 170, fill=A(WHITE, 0.97 * al), r=34)
    d.rect(540 - w / 2, cy - 150, 540 - w / 2 + 16, cy + 170, fill=A(GOLD, al), r=8)
    tag(d, 540, cy - 150, "一句话学会", GOLD, al, 34)
    d.text(540, cy - 40, "张力木 = 树的肌肉", int(62 * k) + 1, A((190, 40, 60), al), k=1)
    ek = popk(t, at("card", 1.5))
    if ek > 0: d.text(540, cy + 70, "哪边需要就长在哪边", int(40 * ek) + 1, A(NAVYT, ek), k=1)
def s_end(t, d):
    grad(d, (255, 160, 100), (130, 70, 120)); glow(d, 540, 900, 380, (255, 220, 140), 0.6)
    d.rect(-20, 1150, OW + 20, OH, fill=A((80, 70, 70), 1))
    for i, x in enumerate((200, 340, 740, 880)):
        tree(d, x, 1150, math.pi / 2, 300 + (i % 2) * 60, 0.0, t + i, "happy", 22, 60, a=0.85)
    tree(d, 540, 1150, math.pi / 2 + 0.06 * math.sin(t * 2), 380, 0.0, t, "proud", 40, 110, arms=0.8, flex=0.3)
    stamp(d, t, T["end"] + 0.05, "树的肌肉", 540, 320, 120, YEL)
    ra = popk(t, at("end", 2))
    d.rect(200, 430, 880, 550, fill=A((20, 12, 30), 0.5 * ra), r=20)
    d.text(540, 468, "Caulus 等 (2026) New Phytologist", 28, A(WHITE, 0.95 * ra))
    d.text(540, 510, "INRAE 新闻稿 2026-09-02", 26, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))


def subs(t, d):
    if SIL0 <= t < BIG2: return
    for a, b, s, key in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70
            w = max(d.tlen(x, 54, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 70 + 46, fill=A((15, 12, 26), 0.82 * al), r=22)
            for i, x in enumerate(ls): d.text(540, y0 + i * 70, x, 54, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 植物有感觉"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)


SF = {"pull": s_pull, "q": s_q, "spin": s_spin, "left": s_left, "reveal": s_reveal, "flip": s_flip, "anta": s_anta, "term": s_term,
      "spring": s_spring, "use": s_use, "crop": s_crop, "card": s_card, "end": s_end}
SECS = [(-1, HOOKCUT, s_hook), (HOOKCUT, T["pull"], s_lay)] + [(T[n], nxt(n) if n != "left" else SIL0, SF[n]) for n in NAMES[2:]]
SECS = [(a, (99 if n == len(SECS) - 1 else b), f) for n, (a, b, f) in enumerate(SECS)]
HITS = [T[n] for n in NAMES] + [at("pull", 0.5), at("pull", 1), at("q", 1), at("spin", 1), at("spin", 2), at("left", 0.5), at("left", 1), at("left", 2),
        at("reveal", 1), at("flip", 1), at("flip", 4), at("anta", 1.5), at("anta", 3), at("term", 1.5), at("term", 3), at("spring", 0.5), at("spring", 1),
        at("spring", 3), at("spring", 4), at("use", 0.5), at("use", 3), at("crop", 2.5), at("card", 1.5)]

def cam(t):
    z = 1.0 + 0.015 * pulse(t, HITS, 7) + 0.04 * pulse(t, [HOOK_HIT, BIG2], 3)
    if T["left"] <= t < SIL0: z += 0.06 * eio(pr(t, T["left"], SIL0))
    if HOOK_STOP <= t < HOOKCUT: z += 0.05 * pr(t, HOOK_STOP, HOOKCUT)
    amp = 8 * pulse(t, [HOOK_HIT, BIG2], 5) + 1.5 * pulse(t, HITS, 8)
    sx, sy = shake(t, amp, 40)
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
        for c in CUTS:
            if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - (t - c) / 0.1)))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"/tmp/tm_test_{float(ts):05.2f}.png")
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
