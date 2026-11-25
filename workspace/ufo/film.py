#《FBI 的 UFO 档案 1947–2026》 9:16, 204 s. Safe zone: x 180–900, y < 1440 (Douyin UI covers sides 1/6, bottom 1/4).
import sys, subprocess, random
from base import *
from cues import *

SKY0 = (6, 8, 22); SKY1 = (24, 22, 54); PAPERC = (238, 232, 212); PAPER_D = (214, 205, 180); INKC = (30, 28, 36)
RED2 = (230, 64, 52); CY = (110, 230, 255); GOLD = (255, 200, 80); SILVER = (196, 204, 218); SILVER_D = (130, 138, 156)
SUIT = (40, 50, 78); SKIN = (242, 204, 170); BRONZE = (205, 140, 70); NIGHTG = (16, 22, 30); GREENT = (120, 255, 160)
X0, X1, YB = 180, 900, 1440
rnd = random.Random(5)
STARS = [(rnd.uniform(0, 1080), rnd.uniform(0, 1300), rnd.uniform(1.2, 3.6), rnd.uniform(0, 6.28)) for _ in range(170)]

def pop(t, t0, d=0.25): return back(pr(t, t0, t0 + d))
def shake(t, amp, seed=1):
    if amp < 0.3: return 0, 0
    return amp * math.sin(t * 61 + seed), amp * math.cos(t * 47 + seed * 2)
def glow(d, x, y, r, col, a, n=7):
    if a <= 0.01: return
    for i in range(n):
        k = 1 - i / n; d.circ(x, y, r * (0.25 + 0.75 * k), fill=A(col, a * 0.15 * (1.2 - k * 0.6)))
def sky(d, t, top=SKY0, bot=SKY1, star=1.0, hide=None):
    for i in range(24):
        d.rect(0, i * 80, 1080, i * 80 + 81, fill=A(mix(top, bot, i / 23), 1))
    for x, y, r, ph in STARS:
        if hide and hide(x, y): continue
        a = star * (0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * 2.2 + ph)))
        d.circ(x, y, r, fill=A(WHITE, a))
def ridge(d, y, col=(10, 12, 20), seed=3, amp=90):
    r = random.Random(seed); pts = [(0, 1920)]
    for i in range(13): pts.append((i * 90, y - r.uniform(0.2, 1) * amp))
    pts += [(1080, y - amp * 0.5), (1080, 1920)]; d.poly(pts, A(col, 1))
def ptri(px, py, a, b, c):
    def s(p, q, r): return (p[0] - r[0]) * (q[1] - r[1]) - (q[0] - r[0]) * (p[1] - r[1])
    d1, d2, d3 = s((px, py), a, b), s((px, py), b, c), s((px, py), c, a)
    return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))
def tri_pts(x, y, s, ang=0.0):
    pts = [(0, -1.0), (0.95, 0.55), (-0.95, 0.55)]; ca, sa = math.cos(ang), math.sin(ang)
    return [(x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s * 0.55) for px, py in pts]
def tri(d, x, y, s, a=1.0, ang=0.0, hot=0.0, col=(18, 18, 24)):
    glow(d, x, y + s * 0.05, s * 1.6, (120, 90, 255), 0.5 * a)
    pts = tri_pts(x, y, s, ang); d.poly(pts, A(col, a))
    d.line([pts[0], pts[1]], A((80, 84, 110), 0.8 * a), max(2, s * 0.03))
    d.line([pts[0], pts[2]], A((60, 64, 86), 0.6 * a), max(2, s * 0.02))
    if hot > 0: d.poly(tri_pts(x, y, s * 0.96, ang), A((255, 170, 60), hot * a))
def saucer(d, x, y, r, t, a=1.0, kind="sus", look=0.0, beam=0.0):
    if beam > 0: d.poly([(x - r * 0.4, y + r * 0.2), (x + r * 0.4, y + r * 0.2), (x + r * 1.1, y + r * 3.2), (x - r * 1.1, y + r * 3.2)], A(CY, 0.18 * beam * a))
    glow(d, x, y, r * 1.8, CY, 0.35 * a)
    d.ell(x, y - r * 0.32, r * 0.55, r * 0.5, A((150, 230, 255), 0.85 * a))
    face(d, x, y - r * 0.36, r * 0.42, kind, a, look)
    d.ell(x, y + r * 0.05, r, r * 0.32, A(SILVER_D, a)); d.ell(x, y - r * 0.02, r * 0.98, r * 0.25, A(SILVER, a))
    d.ell(x - r * 0.4, y - r * 0.1, r * 0.3, r * 0.07, A(WHITE, 0.6 * a))
    for i in range(6):
        lx = x + (i - 2.5) * r * 0.32; on = 0.5 + 0.5 * math.sin(t * 8 + i)
        d.circ(lx, y + r * 0.12, r * 0.06, fill=A([GOLD, CY, RED2][i % 3], (0.4 + 0.6 * on) * a))
def face(d, x, y, r, kind, a, look=0.0):
    er = r * 0.2; ey = y - r * 0.1
    for s_ in (-1, 1):
        ex = x + s_ * r * 0.38
        if kind == "happy": d.arc(ex, ey + er * 0.5, er, er, 200, 340, A(INKC, a), er * 0.5)
        else:
            big = 1.35 if kind in ("scared", "shock") else 1.0
            d.circ(ex, ey, er * big, fill=A(WHITE, a)); d.circ(ex + look * er * 0.5, ey + er * 0.1, er * 0.5, fill=A(INKC, a))
            if kind == "sus": d.rect(ex - er * 1.2, ey - er * 1.25, ex + er * 1.2, ey - er * 0.35, fill=A(SILVER_D, a))
    my = y + r * 0.42
    if kind in ("scared", "shock"): d.ell(x, my, r * 0.14, r * 0.18, A(INKC, a))
    elif kind == "happy": d.d.chord((P(x - r * .35), P(my - r * .25), P(x + r * .35), P(my + r * .25)), 0, 180, fill=A(INKC, a))
    else: d.line([(x - r * 0.2, my), (x + r * 0.2, my + r * 0.04)], A(INKC, a), r * 0.08)
def agent(d, x, y, s, a=1.0, kind="sus", look=0.0, glasses=True, cap=None, tie=RED2):
    d.poly([(x - s * 0.55, y + s * 1.6), (x - s * 0.42, y + s * 0.55), (x + s * 0.42, y + s * 0.55), (x + s * 0.55, y + s * 1.6)], A(SUIT, a))
    d.poly([(x - s * 0.16, y + s * 0.55), (x + s * 0.16, y + s * 0.55), (x, y + s * 0.95)], A(WHITE, a))
    d.poly([(x - s * 0.05, y + s * 0.6), (x + s * 0.05, y + s * 0.6), (x + s * 0.07, y + s * 1.05), (x, y + s * 1.15), (x - s * 0.07, y + s * 1.05)], A(tie, a))
    d.circ(x, y, s * 0.48, fill=A(SKIN, a)); d.ell(x - s * 0.18, y - s * 0.2, s * 0.12, s * 0.07, A(WHITE, 0.4 * a))
    if cap: d.ell(x, y - s * 0.32, s * 0.5, s * 0.2, A(cap, a)); d.rect(x - s * 0.36, y - s * 0.55, x + s * 0.36, y - s * 0.3, fill=A(cap, a), r=s * 0.1)
    else: d.ell(x, y - s * 0.38, s * 0.42, s * 0.16, A((60, 44, 34), a))
    if glasses:
        for s_ in (-1, 1): d.rect(x + s_ * s * 0.2 - s * 0.15, y - s * 0.1, x + s_ * s * 0.2 + s * 0.15, y + s * 0.06, fill=A(INKC, a), r=s * 0.05)
        d.line([(x - s * 0.06, y - s * 0.05), (x + s * 0.06, y - s * 0.05)], A(INKC, a), s * 0.04)
    else:
        for s_ in (-1, 1): d.circ(x + s_ * s * 0.18 + look * s * 0.04, y - s * 0.04, s * 0.06, fill=A(INKC, a))
    my = y + s * 0.22
    if kind == "shock": d.ell(x, my, s * 0.07, s * 0.09, A(INKC, a))
    elif kind == "angry": d.line([(x - s * 0.13, my + s * 0.03), (x, my - s * 0.02), (x + s * 0.13, my + s * 0.03)], A(INKC, a), s * 0.04)
    elif kind == "happy": d.arc(x, my - s * 0.06, s * 0.14, s * 0.1, 20, 160, A(INKC, a), s * 0.04)
    else: d.line([(x - s * 0.1, my), (x + s * 0.1, my)], A(INKC, a), s * 0.04)
def paper(d, x0, y0, x1, y1, a=1.0):
    d.rect(x0, y0, x1, y1, fill=A(PAPER_D, a), r=10); d.rect(x0 + 6, y0 + 6, x1 - 6, y1 - 6, fill=A(PAPERC, a), r=8)
def typed(d, x, y, s, size, a, k=1.0, col=INKC, font=2, anchor="lm"):
    n = int(len(s) * cl(k))
    if n > 0: d.text(x, y, s[:n], size, A(col, a), anchor=anchor, k=font)
def stamp(d, x, y, s, size, col, a, k=1.0):
    if a <= 0.01: return
    sz = size * (1.6 - 0.6 * k); w = d.tlen(s, sz, 1) + sz * 0.8
    d.rect(x - w / 2, y - sz * 0.75, x + w / 2, y + sz * 0.75, outline=A(col, a), w=max(4, sz * 0.09), r=sz * 0.2)
    d.text(x, y, s, sz, A(col, a), k=1)
def redact(d, x0, y, x1, h, a): d.rect(x0, y - h / 2, x1, y + h / 2, fill=A((12, 12, 14), a))
def big_text(d, x, y, s, size, col, a, t, t0, k=1):
    q = pop(t, t0, 0.3); d.text(x, y, s, max(2, int(size * (0.6 + 0.4 * q))), A(col, a * cl(q * 3)), k=k)
def balloon(d, x, y, r, a=1.0):
    d.line([(x, y + r), (x, y + r * 2.4)], A(SILVER, a), 4)
    d.circ(x, y, r, fill=A((220, 222, 230), a)); d.ell(x - r * 0.35, y - r * 0.35, r * 0.25, r * 0.18, A(WHITE, 0.8 * a))
    hx, hy, hr = x, y + r * 2.4 + r * 0.45, r * 0.45
    pts = [(hx + hr * math.cos(i * math.pi / 3), hy + hr * math.sin(i * math.pi / 3)) for i in range(6)]
    d.poly(pts, A(SILVER, a)); d.poly([pts[0], pts[1], pts[2], (hx, hy)], A(SILVER_D, a)); d.poly([pts[3], pts[4], (hx, hy)], A(WHITE, 0.5 * a))
    return hx, hy, hr
def plane(d, x, y, s, a=1.0, col=SILVER):
    d.ell(x, y, s, s * 0.16, A(col, a)); d.poly([(x - s * 0.1, y), (x + s * 0.25, y), (x - s * 0.3, y + s * 0.6), (x - s * 0.45, y + s * 0.6)], A(SILVER_D, a))
    d.poly([(x - s * 0.1, y), (x + s * 0.2, y), (x - s * 0.25, y - s * 0.5), (x - s * 0.4, y - s * 0.5)], A(SILVER_D, a))
    d.poly([(x - s * 0.95, y), (x - s * 0.75, y), (x - s * 1.0, y - s * 0.35)], A(col, a))
    for i in range(5): d.circ(x + s * 0.2 + i * s * 0.12, y - s * 0.03, s * 0.03, fill=A((90, 140, 200), a))
def label(d, x, y, s, size=40, col=WHITE, bg=(0, 0, 0), a=1.0, k=0):
    w = d.tlen(s, size, k) + size * 0.8
    d.rect(x - w / 2, y - size * 0.72, x + w / 2, y + size * 0.72, fill=A(bg, 0.55 * a), r=size * 0.35); d.text(x, y, s, size, A(col, a), k=k)

# ---------------- scenes ----------------
def s_hook(t, d):
    hide = None
    tx = lerp(540, 610, eio(pr(t, 0, 3.4))); ty = lerp(820, 640, eio(pr(t, 0, 3.4)))
    if t > 4.2: tx = lerp(tx, -400, ease(pr(t, 4.2, 4.6))); ty = lerp(ty, 560, ease(pr(t, 4.2, 4.6)))
    sky(d, t); ridge(d, 1060, seed=4)
    if t < 7.2:
        tri(d, tx, ty, 230 * (1 + 0.15 * pulse(t, [HIT0], 4)), 1, -0.08)
        if t > 4.2 and t < 4.9:
            for i in range(10): d.line([(tx + 60 + i * 50, ty - 30 + i * 4), (tx + 260 + i * 70, ty - 20 + i * 5)], A(WHITE, 0.5 * (1 - pr(t, 4.2, 4.9))), 4)
        agent(d, 300, 1130, 70, 1, "shock" if t > 1.5 else "sus"); agent(d, 780, 1130, 70, 1, "shock" if t > 4.3 else "sus")
        q = pop(t, HIT0, 0.3)
        stamp(d, 540, 330, "FBI 档案 · 2026", 70, RED2, cl(q * 3), q)
        if t > 3.6: label(d, 540, 470, "0 分贝", 64, CY, a=ease(pr(t, 3.7, 4.0)), k=1)
    else:
        u = ease(pr(t, 7.4, 8.4)); x0, x1 = 230, 850
        d.line([(x0, 760), (lerp(x0, x1, u), 760)], A(CY, 1), 10)
        for xx, yr in ((x0, "1947"), (x1, "2026")):
            if xx <= lerp(x0, x1, u) + 1: d.circ(xx, 760, 18, fill=A(CY, 1)); d.text(xx, 830, yr, 54, A(WHITE, 1), k=1)
        big_text(d, 540, 560, "79 年", 230, GOLD, 1, t, 8.6)
        saucer(d, 540, 1080, 110, t, ease(pr(t, 9.5, 10.2)), "sus", math.sin(t * 2))
def s_summer(t, d):
    sky(d, t, (14, 18, 40), (60, 44, 70)); ridge(d, 1150, (20, 18, 30), 7, 60)
    for i in range(14):
        k = pr(t, SUMMER + i * 0.18, SUMMER + i * 0.18 + 0.4)
        if k > 0:
            x = 200 + (i * 137) % 680; y = 300 + (i * 89) % 520
            glow(d, x, y, 40, [CY, GOLD, WHITE][i % 3], k); d.ell(x, y, 26 * back(k), 9 * back(k), A(SILVER, k))
    for i, x in enumerate((260, 400, 540, 680, 820)):
        agent(d, x, 1180 + (i % 2) * 30, 52, 1, "shock" if t > SUMMER + 1.2 + i * 0.2 else "sus", glasses=False, tie=[RED2, GOLD, CY][i % 3])
    big_text(d, 540, 250, "1947", 150, GOLD, 1, t, SUMMER)
def s_tele(t, d):
    sky(d, t, (12, 14, 26), (26, 26, 40), 0.4)
    paper(d, 220, 300, 860, 1180)
    lines = ["TELETYPE   FBI DALLAS", "7-8-47     6-17 PM", "DIRECTOR AND SAC, CINCINNATI", "U R G E N T", "FLYING DISC,", "INFORMATION CONCERNING."]
    for i, s in enumerate(lines):
        typed(d, 270, 400 + i * 95, s, 40 if i != 3 else 58, 1, pr(t, TELE + 0.4 + i * 0.7, TELE + 1.1 + i * 0.7), RED2 if i == 3 else INKC)
    redact(d, 270, 980, 760, 40, ease(pr(t, TELE + 4.2, TELE + 4.6)))
    d.text(540, 1090, "达拉斯 → 胡佛", 46, A(INKC, ease(pr(t, TELE + 2.5, TELE + 3))), k=1)
def s_rosw(t, d):
    sky(d, t, (20, 16, 30), (70, 50, 40), 0.5); ridge(d, 1200, (40, 30, 26), 9, 50)
    if t < 24.5:
        q = pop(t, ROS, 0.3)
        stamp(d, 540, 420, "ROSWELL", 110, RED2, cl(q * 3), q)
        saucer(d, 540, 820 + 10 * math.sin(t * 3), 150, t, 1, "shock" if t > ROS + 0.3 else "sus", beam=0.6)
        label(d, 540, 1100, "回收：一个“飞碟”", 56, GOLD, k=1)
    elif t < 33:
        u = ease(pr(t, 24.5, 25.5)); hx, hy, hr = balloon(d, 540, lerp(1300, 470, u), 150)
        if t > 25.4:
            k = ease(pr(t, 25.4, 26.2)); d.line([(320, 320), (320, 620)], A(CY, k), 5); d.line([(300, 320), (340, 320)], A(CY, k), 5); d.line([(300, 620), (340, 620)], A(CY, k), 5)
            d.text(250, 470, "约6米", 46, A(CY, k), k=1)
            label(d, 780, hy, "六角形", 48, WHITE, a=ease(pr(t, 26, 26.5)), k=1)
        if t > 29:
            k = ease(pr(t, 29, 29.6)); label(d, 540, 1130, "≈ 气象气球 + 雷达反射器", 46, GOLD, a=k, k=1)
            saucer(d, 300, 1000, 60, t, k, "sus", 1)
    else:
        u = pr(t, 33, 36); plane(d, lerp(1300, -300, u), 700 - 120 * u, 200)
        d.text(540, 1000, "→ 莱特机场", 70, A(WHITE, ease(pr(t, 33.3, 33.8))), k=1)
def s_hoover(t, d):
    sky(d, t, (18, 18, 30), (34, 30, 46), 0.3)
    if t < 40.5:
        agent(d, 330, 820, 120, 1, "happy", glasses=False, cap=(70, 96, 60), tie=(70, 96, 60)); d.text(330, 1110, "陆军航空队", 42, A(WHITE, 1), k=1)
        agent(d, 750, 820, 120, 1, "sus"); d.text(750, 1110, "FBI", 46, A(WHITE, 1), k=1)
        k = ease(pr(t, 36.5, 37.2)); d.rect(210, 430, 640, 560, fill=A(WHITE, k), r=40); d.text(425, 495, "帮我们查飞碟？", 46, A(INKC, k), k=1)
        saucer(d, 540, 300, 60, t, k, "happy")
    else:
        paper(d, 210, 300, 870, 1180)
        typed(d, 260, 380, "SUBJECT:  FLYING DISCS", 38, 1, 1)
        for i in range(5): d.rect(260, 450 + i * 50, 820 - (i % 2) * 120, 470 + i * 50, fill=A((180, 172, 150), 1), r=6)
        k = pr(t, 41, 45); s1 = "可以，但我们必须完全接触"; s2 = "回收的飞碟。"
        typed(d, 260, 780, s1, 44, 1, k * 1.6, (30, 60, 160), 0); typed(d, 260, 860, s2, 44, 1, (k - 0.6) * 2.5, (30, 60, 160), 0)
        d.text(820, 950, "—— 胡佛", 44, A((30, 60, 160), ease(pr(t, 44.5, 45))), anchor="rm", k=0)
        if t > 46:
            k2 = ease(pr(t, 46, 46.6)); d.rect(180, 990, 900, 1170, fill=A((20, 20, 30), 0.92 * k2), r=20)
            agent(d, 300, 1080, 60, k2, "angry", glasses=False)
            sx = lerp(820, 640, ease(pr(t, 47.5, 48.5))); saucer(d, sx, 1070, 50, t, k2, "scared", 1)
            agent(d, lerp(900, 720, ease(pr(t, 47.5, 48.5))), 1080, 60, k2, "happy", glasses=False, cap=(70, 96, 60), tie=(70, 96, 60))
            d.text(460, 1030, "看都不让看！", 40, A(GOLD, k2), k=1)
def evidence(d, t, t0, y, title, a=1.0):
    k = ease(pr(t, t0, t0 + 0.4)) * a; d.rect(220, y - 50, 860, y + 50, fill=A((255, 255, 255), 0.08 * k), r=20); d.text(540, y, title, 48, A(GOLD, k), k=1)
def s_prank(t, d):
    sky(d, t, (16, 20, 26), (30, 36, 40), 0.25)
    d.rect(180, 1000, 900, 1260, fill=A((70, 50, 36), 1), r=20)
    if t < 56:
        stamp(d, 540, 450, "收“飞碟”", 90, GOLD, ease(pr(t, 52.3, 52.6)), pop(t, 52.3))
        for i in range(3):
            k = ease(pr(t, 53 + i * 0.6, 53.4 + i * 0.6)); d.rect(250 + i * 210, 700, 400 + i * 210, 900, fill=A(PAPERC, k), r=10); d.text(325 + i * 210, 800, "?", 90, A(INKC, k), k=1)
    elif t < 65:
        k = ease(pr(t, 56, 56.6)); r = 230
        d.circ(540, 760, r, fill=A((180, 184, 192), k)); d.circ(540, 760, r * 0.9, fill=A((200, 204, 214), k)); d.ell(470, 690, 60, 30, A(WHITE, 0.5 * k))
        d.text(540, 470, "威斯康星 · 48 厘米", 54, A(GOLD, k), k=1)
        if t > 61:
            k2 = ease(pr(t, 61, 61.5)); d.circ(540, 760, r * 0.75, fill=A((90, 70, 50), k2))
            d.rect(450, 700, 560, 780, fill=A((80, 120, 200), k2), r=10); d.text(505, 740, "光电管", 26, A(WHITE, k2), k=1)
            d.rect(560, 790, 650, 860, fill=A((150, 150, 160), k2), r=8); d.text(605, 825, "电机", 26, A(INKC, k2), k=1)
            ang = t * 25; d.line([(540 + 70 * math.cos(ang), 860 + 20 * math.sin(ang)), (540 - 70 * math.cos(ang), 860 - 20 * math.sin(ang))], A(GOLD, k2), 10)
            agent(d, 780, 1090, 55, k2, "sus", glasses=False, cap=GOLD, tie=CY); d.text(780, 1200, "小孩？", 36, A(WHITE, k2), k=1)
    elif t < 69.5:
        d.rect(180, 900, 900, 1000, fill=A((60, 120, 60), 1)); d.rect(300, 640, 520, 900, fill=A((160, 110, 80), 1)); d.poly([(280, 650), (410, 540), (540, 650)], A((140, 60, 50), 1))
        k = ease(pr(t, 65, 65.5)); saucer(d, 700, 900, 80, t, k, "happy"); d.text(540, 470, "伊利诺伊 · 前院", 54, A(GOLD, k), k=1)
        stamp(d, 700, 1120, "恶作剧", 60, RED2, ease(pr(t, 67, 67.3)), pop(t, 67))
    else:
        if t < 75:
            u = pr(t, 69.5, 72.5); px = lerp(1100, 560, u); py = lerp(500, 900, u ** 2)
            plane(d, px, py, 150, 1, (150, 150, 160))
            if t > 72.5:
                k = pr(t, 72.5, 73.5); glow(d, 560, 950, 260, (255, 120, 40), 1 - k * 0.5)
            d.text(540, 400, "1947.8.1 · 凯尔索坠机", 52, A(GOLD, 1), k=1)
            if t > 73: label(d, 540, 1140, "传言：机上有飞碟碎片", 44, WHITE, a=ease(pr(t, 73, 73.4)), k=1)
        else:
            for i in range(7): d.poly([(380 + i * 50, 900 - (i % 3) * 20), (420 + i * 50, 860), (450 + i * 50, 910)], A((90, 84, 80), 1))
            k = ease(pr(t, 75.4, 76)); d.rect(300, 520, 780, 740, fill=A(PAPERC, k), r=16)
            d.text(540, 580, "化验结果", 44, A(INKC, k), k=1); d.text(540, 670, "炼渣厂的炉渣", 62, A(RED2, k), k=1)
            saucer(d, 760, 1100, 60, t, k, "happy")
def s_quit(t, d):
    sky(d, t, (18, 16, 26), (40, 30, 40), 0.3)
    if t < 89:
        paper(d, 220, 320, 860, 860)
        typed(d, 260, 400, "COOPERATION OF FBI WITH AAF", 30, 1, 1); typed(d, 260, 450, "3 SEPTEMBER 1947", 30, 1, 1)
        for i in range(4): d.rect(260, 520 + i * 45, 820 - (i % 2) * 100, 538 + i * 45, fill=A((180, 172, 150), 1), r=6)
        if t > 85:
            k = pop(t, TOILET, 0.3); d.rect(240, 740, 840, 830, fill=A((255, 230, 80), 0.7 * cl(k * 3)), r=8)
            d.text(540, 785, "ash can covers, toilet seats", 34, A(INKC, cl(k * 3)), k=2)
            for i, (xx, kind) in enumerate(((360, 0), (720, 1))):
                yy = 990 + 30 * math.sin(t * 6 + i); kk = cl(k * 3)
                if kind == 0: d.ell(xx, yy, 120, 80, outline=A(WHITE, kk), w=30); d.ell(xx, yy - 95, 110, 30, A((230, 230, 236), kk))
                else: d.ell(xx, yy, 120, 40, A((150, 156, 168), kk)); d.rect(xx - 25, yy - 60, xx + 25, yy - 30, fill=A((150, 156, 168), kk), r=8)
            d.text(360, 1130, "马桶盖", 44, A(GOLD, cl(k * 3)), k=1); d.text(720, 1130, "垃圾桶盖", 44, A(GOLD, cl(k * 3)), k=1)
        else: agent(d, 540, 1040, 90, 1, "sus")
    else:
        agent(d, 540, 760, 160, 1, "angry", glasses=False)
        q = pop(t, 89.6, 0.3); stamp(d, 540, 1120, "停止调查", 100, RED2, cl(q * 3), q)
        d.text(540, 400, "1947.9.27", 60, A(GOLD, 1), k=1)
def s_pastor(t, d):
    sky(d, t, (12, 16, 36), (50, 40, 70), 0.8); ridge(d, 1000, (20, 26, 40), 11, 160)
    if t < 99:
        k = ease(pr(t, 94.5, 95.2)); d.rect(260, 520, 820, 860, fill=A(PAPERC, k), r=12); d.poly([(260, 520), (540, 720), (820, 520)], A(PAPER_D, k))
        d.text(540, 460, "牧师来信 · 1949", 54, A(GOLD, k), k=1); d.text(540, 800, "To: J. Edgar Hoover", 34, A(INKC, k), k=2)
    elif t < 104:
        cx, cy = 560, 900
        for i, (sx, sy) in enumerate(((180, 300), (300, 260), (420, 230), (230, 420))):
            k = ease(pr(t, 99.4 + i * 0.25, 100.2 + i * 0.25)); d.line([(sx, sy), (lerp(sx, cx, k), lerp(sy, cy, k))], A(CY, 0.8), 10)
        if t > 100.6:
            k = pr(t, 100.6, 102.5); glow(d, cx, cy - 250 * k, 160 + 200 * k, GOLD, 1.2 - k * 0.4)
            d.line([(860, cy), (860, cy - 300)], A(WHITE, ease(k)), 5); d.text(860, cy - 340, "约3000米", 40, A(WHITE, ease(k)), k=1)
    else:
        k = ease(pr(t, 104, 104.6)); d.rect(560, 640, 860, 1000, fill=A((70, 80, 100), k), r=10)
        for j in range(3): d.ell(710, 760, 90, 30, outline=A(CY, k), w=6) if j == 0 else None
        for ang in (0.6, -0.6):
            pts = [(710 + 90 * math.cos(a_) * math.cos(ang) - 30 * math.sin(a_) * math.sin(ang), 760 + 90 * math.cos(a_) * math.sin(ang) + 30 * math.sin(a_) * math.cos(ang)) for a_ in [i * 0.2 for i in range(33)]]
            d.line(pts, A(CY, k), 6)
        d.circ(710, 760, 14, fill=A(GOLD, k)); d.text(710, 920, "原子能委员会", 38, A(WHITE, k), k=1)
        u = ease(pr(t, 104.8, 106.3)); d.rect(lerp(200, 520, u), 760, lerp(360, 600, u), 860, fill=A(PAPERC, 1 - pr(t, 106.3, 106.8)), r=8)
        agent(d, 330, 1000, 80, 1, "sus", glasses=False)
def s_hottel(t, d):
    sky(d, t, (10, 12, 22), (30, 34, 50), 0.6)
    if t < 113:
        paper(d, 220, 330, 860, 1150)
        typed(d, 260, 410, "SUBJECT:  FLYING SAUCERS", 36, 1, 1); typed(d, 260, 460, "MARCH 22, 1950", 32, 1, 1)
        redact(d, 260, 560, 760, 34, ease(pr(t, 109.5, 110))); redact(d, 260, 620, 640, 34, ease(pr(t, 110, 110.5)))
        typed(d, 260, 720, "\"three so-called flying saucers", 30, 1, pr(t, 110.5, 112)); typed(d, 260, 770, "had been recovered in New Mexico\"", 30, 1, pr(t, 111.5, 113))
    elif t < 123:
        for i in range(3):
            x = 300 + i * 240; k = ease(pr(t, 113 + i * 0.35, 113.6 + i * 0.35))
            saucer(d, x, 640, 100, t, k, "scared" if t > 118 else "sus")
            if t > 118:
                for j in range(3):
                    kk = ease(pr(t, 118.2 + i * 0.3 + j * 0.1, 118.6 + i * 0.3 + j * 0.1)); bx = x - 50 + j * 50
                    d.rect(bx - 15, 930, bx + 15, 1010, fill=A((150, 156, 170), kk), r=10); d.circ(bx, 905, 22, fill=A((170, 176, 190), kk))
        k = ease(pr(t, 114, 114.5)); d.line([(200, 790), (880, 790)], A(CY, k), 5); d.text(540, 840, "直径约15米", 46, A(CY, k), k=1)
        if t > 118: d.text(540, 1100, "约90厘米 × 9", 50, A(GOLD, ease(pr(t, 119, 119.5))), k=1)
    elif t < 128:
        k = ease(pr(t, 123, 123.5)); d.rect(220, 420, 860, 900, fill=A((30, 36, 56), k), r=24)
        d.text(540, 520, "FBI 档案库", 50, A(WHITE, k), k=1); big_text(d, 540, 680, "浏览量 No.1", 110, GOLD, k, t, 123.5)
        d.text(540, 820, "（2013年 FBI 公布）", 36, A(MUTE, k), k=1)
    else:
        agent(d, 540, 700, 140, 1, "sus")
        q = pop(t, 128.6, 0.3); stamp(d, 540, 1080, "二三手传闻 · 未调查", 70, RED2, cl(q * 3), q)
def s_pages(t, d):
    sky(d, t, (8, 8, 14), (16, 16, 24), 0.2 if t < 137 else 0.6)
    if t < 137:
        n = int(lerp(0, 22, pr(t, 133.2, 136)))
        for i in range(n): d.rect(300 + (i % 2) * 8, 1150 - i * 28, 780 + (i % 2) * 8, 1150 - i * 28 + 24, fill=A(mix(PAPERC, PAPER_D, i % 2), 1), r=4)
        d.text(540, 380, f"{int(lerp(0, 2000, pr(t, 133.2, 136))):d}+ 页", 110, A(GOLD, 1), k=1); d.text(540, 500, "1947 – 1968", 54, A(WHITE, 1), k=1)
    elif t >= 138.5:
        k = ease(pr(t, 138.5, 139.2)); agent(d, 420, 820, 110, k, "sus"); agent(d, 700, 840, 100, k, "shock", glasses=False, tie=CY)
        d.rect(540, 600, 860, 700, fill=A(PAPERC, k), r=10); typed(d, 560, 650, "FD-302", 44, k, pr(t, 139, 140))
def s_bagram(t, d):
    tx = lerp(-300, 1400, pr(t, 145.5, 152.5)); ty = 520
    pts = tri_pts(tx, ty, 420, math.pi / 2)
    hide = (lambda x, y: ptri(x, y, *pts)) if t >= 145.5 else None
    sky(d, t, (4, 6, 14), (14, 16, 30), 1.0, hide)
    if t >= 145.5:
        d.poly(pts, A((2, 2, 6), 0.55)); d.line([pts[0], pts[1], pts[2], pts[0]], A((60, 60, 90), 0.35), 3)
    ridge(d, 1150, (6, 8, 12), 21, 70)
    if t < 145.5:
        agent(d, 540, 820, 140, 1, "sus", cap=(70, 96, 60), tie=(70, 96, 60)); d.rect(560, 560, 860, 660, fill=A(PAPERC, 1), r=10); typed(d, 580, 610, "2002 → 2024", 40, 1, 1)
    else:
        for x, kind in ((420, "shock"), (640, "shock")): agent(d, x, 1180, 55, 1, kind if t > 147 else "sus", glasses=False, cap=(70, 96, 60), tie=(70, 96, 60))
        if t > 150: label(d, 540, 340, "等边三角形 · 无声", 54, GOLD, a=ease(pr(t, 150, 150.4)), k=1)
        if t > 153: big_text(d, 540, 900, "约150米", 130, CY, 1, t, 153)
        d.text(540, 1360 - 1000 + 0, "", 10, A(WHITE, 0))
def thermal(d, x0, y0, x1, y1, t, tx, ty, s, a=1.0):
    d.rect(x0, y0, x1, y1, fill=A((20, 10, 40), a), r=20)
    for i in range(10): d.rect(x0, y0 + i * (y1 - y0) / 10, x1, y0 + (i + 1) * (y1 - y0) / 10, fill=A(mix((24, 12, 50), (60, 20, 80), i / 9), a))
    d.poly([(x0, y1 - 120), (x0 + 200, y1 - 190), (x0 + 420, y1 - 140), (x1, y1 - 210), (x1, y1), (x0, y1)], A((90, 30, 90), a))
    glow(d, tx, ty, s * 1.4, (255, 150, 40), 0.9 * a); d.poly(tri_pts(tx, ty, s, -0.1), A((255, 210, 90), a))
    d.text(x0 + 30, y0 + 40, "THERMAL", 30, A(WHITE, a), anchor="lm", k=2); d.circ(x1 - 40, y0 + 40, 10, fill=A(RED2, a * (0.5 + 0.5 * math.sin(t * 8))))
def s_tri(t, d):
    if t < 160:
        sky(d, t); ridge(d, 900, (10, 12, 20), 31, 120)
        d.rect(560, 1000, 900, 1260, fill=A((40, 44, 56), 1)); d.text(730, 1060, "观察哨", 40, A(WHITE, 1), k=1)
        u = ease(pr(t, 156.4, 158.2))
        agent(d, lerp(820, 320, u), 1120, 70, 1, "shock"); agent(d, lerp(880, 440, u), 1140, 66, 1, "sus")
        stamp(d, 540, 330, "2026 · 6月", 70, RED2, cl(pop(t, CLIMAX) * 3), pop(t, CLIMAX))
        if t > 158.5: tri(d, 300, 820, 60, ease(pr(t, 158.5, 159.2)))
    elif t < 164.5:
        thermal(d, 190, 360, 890, 1060, t, 540, 640, 150)
        k = ease(pr(t, 160.5, 161)); label(d, 540, 820, "翼展约 3 – 4.5 米", 48, WHITE, a=k, k=1)
        k2 = ease(pr(t, 162, 162.5)); label(d, 380, 1150, "比周围热", 44, GOLD, a=k2, k=1); label(d, 700, 1150, "无尾气", 44, CY, a=k2, k=1)
    else:
        sky(d, t); ridge(d, 900, (10, 12, 20), 31, 120)
        u1 = ease(pr(t, 164.8, 166.6)); u2 = pr(t, 166.9, 167.5)
        x = lerp(560, -500, u2 ** 2); y = lerp(860, 520, u1)
        tri(d, x, y, 110, 1, -0.05)
        if t > 165: d.line([(560, 880), (560, lerp(880, 520, u1))], A(CY, 0.4), 4)
        if t > 166.9:
            for i in range(6): d.line([(x + 140 + i * 40, y - 10), (x + 340 + i * 60, y)], A(WHITE, 0.4 * (1 - pr(t, 167.3, 168))), 4)
        d.rect(300, 1120, 780, 1240, fill=A((0, 0, 0), 0.5), r=20)
        d.line([(330, 1180), (750, 1180)], A(GREENT, 1), 5); d.text(540, 1130, "声音：0", 36, A(GREENT, 1), k=1)
def s_news(t, d):
    sky(d, t, (12, 12, 20), (24, 24, 36), 0.4)
    k = pop(t, HEADLINE, 0.3); d.rect(200, 420, 880, 900, fill=A(WHITE, cl(k * 3)), r=20)
    d.rect(200, 420, 880, 500, fill=A(RED2, cl(k * 3)), r=20); d.text(540, 460, "热搜", 44, A(WHITE, cl(k * 3)), k=1)
    d.text(540, 640, "3秒飞了", 90, A(INKC, cl(k * 3)), k=1); d.text(540, 780, "2.4公里！", 110, A(RED2, cl(k * 3)), k=1)
    tri(d, 540, 1100, 90, 1, math.sin(t * 2) * 0.1)
def s_orig(t, d):
    sky(d, t, (12, 12, 20), (24, 24, 36), 0.3)
    paper(d, 200, 300, 880, 1060)
    typed(d, 240, 370, "FD-302   FBI", 36, 1, 1)
    k1 = pr(t, REVEAL, REVEAL + 1.4); k2 = pr(t, REVEAL + 2.2, REVEAL + 3.6)
    d.rect(232, 440, 848, 600, fill=A((255, 230, 80), 0.6 * ease(k1)), r=8)
    typed(d, 250, 485, "\"The total duration of the sighting", 27, 1, k1 * 2); typed(d, 250, 550, "was approximately three seconds\"", 27, 1, k1 * 2 - 1)
    d.text(540, 650, "整段目击 ≈ 3 秒", 54, A(RED2, ease(pr(t, REVEAL + 1.2, REVEAL + 1.6))), k=1)
    d.rect(232, 740, 848, 900, fill=A((120, 220, 255), 0.5 * ease(k2)), r=8)
    typed(d, 250, 785, "\"lost visual contact ... at a range", 27, 1, k2 * 2); typed(d, 250, 850, "of about 1.5 miles from our position\"", 27, 1, k2 * 2 - 1)
    d.text(540, 960, "消失时 离他们 ≈ 2.4 公里", 50, A((30, 90, 170), ease(pr(t, REVEAL + 3.4, REVEAL + 3.8))), k=1)
def s_howfar(t, d):
    sky(d, t); ridge(d, 1100, (10, 12, 20), 31, 80)
    ox, oy = 360, 1080; vx, vy = 760, 520
    agent(d, ox, oy, 50, 1, "sus")
    k = ease(pr(t, 178.7, 179.5)); d.line([(ox, oy - 40), (lerp(ox, vx, k), lerp(oy - 40, vy, k))], A(CY, 1), 6)
    if k > 0.99: d.text(640, 760, "2.4 公里", 48, A(CY, 1), k=1)
    for i in range(3):
        sx, sy = [(560, 820), (420, 520), (840, 700)][i]; kk = ease(pr(t, 179.8 + i * 0.5, 180.2 + i * 0.5))
        pts = [(lerp(sx, vx, j / 20) + math.sin(j * 0.6 + i) * 60, lerp(sy, vy, j / 20)) for j in range(21)]
        for j in range(0, 20, 2): d.line([pts[j], pts[j + 1]], A(GOLD, 0.7 * kk), 5)
    tri(d, vx, vy, 50, 1)
    big_text(d, 540, 330, "飞了多远？", 110, GOLD, 1, t, 180.5)
def s_recap(t, d):
    sky(d, t, (10, 12, 28), (30, 28, 56), 0.8)
    if t < 188.5:
        d.line([(210, 760), (870, 760)], A(CY, 0.8), 8)
        items = [("1947", "气球"), ("1947", "恶作剧"), ("1950", "传闻"), ("2026", "未解")]
        for i, (yr, s) in enumerate(items):
            x = 260 + i * 187; k = ease(pr(t, 183.3 + i * 1.1, 183.8 + i * 1.1))
            d.circ(x, 760, 20, fill=A(GOLD, k)); d.text(x, 700, yr, 34, A(WHITE, k), k=1)
            y = 900
            if i == 0: balloon(d, x, 860, 40, k)
            elif i == 1: saucer(d, x, 900, 60, t, k, "happy")
            elif i == 2: d.rect(x - 50, 850, x + 50, 980, fill=A(PAPERC, k), r=6); d.text(x, 915, "?", 60, A(INKC, k), k=1)
            else: tri(d, x, 910, 60, k)
            d.text(x, 1080, s, 42, A(GOLD if i == 3 else WHITE, k), k=1)
    else:
        n = int(lerp(0, 478, ease(pr(t, 188.7, 191)))); big_text(d, 540, 600, f"{n}", 250, GOLD, 1, t, 188.6)
        d.text(540, 780, "份 UAP 档案已公开", 60, A(WHITE, 1), k=1); d.text(540, 870, "2026.5 → 至今", 44, A(MUTE, 1), k=1)
        for i in range(5): d.rect(300 + i * 100, 980, 380 + i * 100, 1090, fill=A(mix(PAPERC, PAPER_D, i % 2), ease(pr(t, 189 + i * 0.2, 189.4 + i * 0.2))), r=6)
def s_ask(t, d):
    sky(d, t, (4, 6, 16), (20, 18, 44), 1.0); ridge(d, 1150, (6, 8, 14), 41, 80)
    tri(d, 540, lerp(700, 640, pr(t, 193.5, 198)), 160 * (1 + 0.1 * math.sin(t * 2)), 1, 0)
    agent(d, 420, 1120, 60, 1, "sus"); saucer(d, 680, 1100, 60, t, 1, "sus", -1)
    big_text(d, 540, 320, "下一份……", 120, WHITE, 1, t, 194)
def s_end(t, d):
    sky(d, t, (8, 10, 20), (16, 18, 32), 0.5)
    k = ease(pr(t, END, END + 0.6)); d.text(540, 330, "资料来源", 56, A(GOLD, k), k=1)
    src = ["FBI Vault · UFO（1947–1954）", "FBI 卷宗 62-HQ-83894（1947–1968）", "FBI《UFOs and the Guy Hottel Memo》2013", "PURSUE 解密档案 war.gov/UFO", "FBI-UAP-D011 / D024 / D043（FD-302）", "新华社、Axios 2026.10.23–24 报道"]
    for i, s in enumerate(src): d.text(540, 450 + i * 80, s, 29, A(WHITE, ease(pr(t, END + 0.3 + i * 0.15, END + 0.7 + i * 0.15))), k=0)
    d.text(540, 1060, "关注 · 下一批解密见", 50, A(CY, ease(pr(t, END + 1.5, END + 2))), k=1)
    saucer(d, 540, 1220, 60, t, k, "happy")

SECS = [(HOOK, SUMMER, s_hook), (SUMMER, TELE, s_summer), (TELE, ROSW, s_tele), (ROSW, HOOV, s_rosw), (HOOV, PRANK, s_hoover), (PRANK, QUIT, s_prank),
        (QUIT, PASTOR, s_quit), (PASTOR, HOTTEL, s_pastor), (HOTTEL, PAGES, s_hottel), (PAGES, BAGRAM, s_pages), (BAGRAM, TRI, s_bagram), (TRI, NEWS, s_tri),
        (NEWS, ORIG, s_news), (ORIG, HOWFAR, s_orig), (HOWFAR, RECAP, s_howfar), (RECAP, ASK, s_recap), (ASK, END, s_ask), (END, 999, s_end)]
CUTS = [a for a, b, f in SECS[1:]] + [24.5, 33.0, 40.5, 56, 65, 69.5, 75, 85, 89, 99, 104, 113, 123, 128, 160, 164.5, 188.5]
BIGS = [HIT0, ROS, CLIMAX]; SMALL = STAMPS + [TOILET, HEADLINE, REVEAL, 8.6, 123.5, 153, 180.5]
def cam(t):
    z = 1.0 + 0.10 * pulse(t, BIGS, 3) + 0.04 * pulse(t, SMALL, 6)
    for a, b, f in SECS:
        if a <= t < b: z += 0.05 * pr(t, a, b)
    amp = 26 * pulse(t, BIGS, 4) + 7 * pulse(t, SMALL, 6)
    if BAGRAM <= t < TRI: amp += 3 * pulse(t, [cyc for cyc in [141 + i * 1.5 for i in range(10)]], 8)
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx, 860 + sy
def year_of(t):
    y = 2026
    for a, yy in YEARS:
        if t >= a: y = yy
    return y
def top(t, d):
    d.rect(190, 150, 430, 196, fill=A(WHITE, 0.92), r=23); d.text(310, 173, "Vibe 知识大赏", 25, A(INKC, 1), k=1)
    d.rect(620, 150, 890, 196, fill=A(RED2, 0.95), r=23); d.text(755, 173, "FBI 的 UFO 档案", 25, A(WHITE, 1), k=1)
    if t < END:
        y = year_of(t); u = (y - 1947) / (2026 - 1947)
        d.rect(190, 222, 890, 228, fill=A(WHITE, 0.25), r=3); d.rect(190, 222, 190 + 700 * u, 228, fill=A(GOLD, 0.9), r=3)
        d.circ(190 + 700 * u, 225, 10, fill=A(GOLD, 1)); d.text(190 + 700 * u, 252, str(y), 22, A(GOLD, 1), k=1)
def wrap2(d, s, size, maxw=640):
    if d.tlen(s, size, 1) <= maxw: return [s]
    n = 2 if d.tlen(s, size, 1) <= maxw * 1.9 else 3
    tgt = d.tlen(s, size, 1) / n; out = []; cur = ""
    for i, ch in enumerate(s):
        cur += ch
        nxt = s[i + 1] if i + 1 < len(s) else ""
        if len(out) < n - 1 and d.tlen(cur, size, 1) >= tgt * 0.85 and (ch in "，：；、。”" or d.tlen(cur, size, 1) >= tgt) and not (ch == "—" and nxt == "—") and nxt not in "，。：；、”":
            out.append(cur); cur = ""
    if cur: out.append(cur)
    return out
def subs(t, d):
    for a, b, s in LINES:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.15)) * (1 - pr(t, b - 0.1, b))
            ls = wrap2(d, s, 52, 670); n = len(ls); y0 = 1350 - (n - 1) * 70
            w = max(d.tlen(x, 52, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 70 + 46, fill=A((0, 0, 0), 0.6 * al), r=22)
            for i, x in enumerate(ls): d.text(540, y0 + i * 70, x, 52, A(WHITE, al), k=1)
            break
def frame(t):
    img = Image.new("RGB", (W, H), SKY0); d = D(img)
    for a, b, sf in SECS:
        if a <= t < b: sf(t, d); break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.08: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.45 * (1 - (t - c) / 0.08)))
    top(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):06.1f}.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        last = None; errs = 0
        for i in range(i0, i1):
            try: last = frame(i / FPS).tobytes()
            except Exception as e: errs += 1; print('ERR', i, e, file=sys.stderr)
            if last: p.stdin.write(last)
        p.stdin.close(); p.wait(); print('errs', errs, file=sys.stderr)
