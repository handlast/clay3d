import sys, subprocess, math, random
from fx import *
from cues import *
import easing as E

# ---------------- palette ----------------
OLV = (150, 138, 84); OLV_D = (104, 94, 56); OLV_L = (206, 192, 128); BELLY = (232, 214, 160); SPOT = (84, 74, 44)
FIN = (196, 170, 104); FIN_D = (150, 126, 74); STRIA = (255, 236, 150)
ROCK = (110, 116, 128); ROCK_D = (76, 80, 92); ROCK_L = (160, 166, 178); MOSS = (90, 140, 80)
RIV1 = (46, 132, 172); RIV2 = (12, 44, 74); FOAM = (220, 244, 255)
ORG = (255, 140, 60); ORG_L = (255, 196, 120); PINK = (255, 120, 150); LIME = (170, 230, 90)
NAVYT = (22, 22, 40); GOOD = (90, 220, 120); BAD = (250, 70, 70); GOLD = (255, 200, 60)
rr_ = random.Random(5)
STREAKS = [(rr_.uniform(0, 1), rr_.uniform(0, 1920), rr_.uniform(80, 260), rr_.uniform(0.6, 1.4), rr_.uniform(3, 7)) for _ in range(70)]
BUBS = [(rr_.uniform(0, 1080), rr_.uniform(0, 1), rr_.uniform(5, 16), rr_.uniform(0.6, 1.3)) for _ in range(40)]

def popk(t, t0, preset="snappy"): return max(0.0, E.spring_at(t, t0, 0, 1, preset)) if t >= t0 else 0.0
def ap(t, t0, d=0.12): return cl((t - t0) / d)
def tag(d, x, y, s, col, a=1.0, size=40, tc=NAVYT):
    if a <= 0.01: return
    w = d.tlen(s, size, 1) + 44
    d.rect(x - w / 2, y - size * 0.78, x + w / 2, y + size * 0.78, fill=A(col, 0.95 * a), r=size * 0.6)
    d.text(x, y, s, size, A(tc, a), k=1)
def ptag(d, t, t0, x, y, s, col, size=40, tc=NAVYT):
    k = popk(t, t0)
    if k <= 0: return
    sc = 0.6 + 0.4 * k
    tag(d, x, y + (1 - min(k, 1)) * 30, s, col, ap(t, t0), int(size * sc), tc)
def title(d, t, t0, s, y=330, size=110, col=WHITE):
    k = popk(t, t0, "heavy")
    if k > 0: d.text(540, y + (1 - k) * 40, s, int(size * (0.85 + 0.15 * k)), A(col, ap(t, t0)), k=1)
def slamtxt(d, t, t0, s, y, size, col):
    if t < t0: return
    sc = E.slam(t, t0, 0.28, 1.8)
    d.text(540, y, s, int(size * sc), A(col, ap(t, t0, 0.06)), k=1)
def check(d, x, y, s, k, col, a=1.0):
    p = [(x - s, y), (x - s * 0.3, y + s * 0.7), (x + s, y - s * 0.8)]
    if k <= 0: return
    if k < 0.5: d.line([p[0], (lerp(p[0][0], p[1][0], k * 2), lerp(p[0][1], p[1][1], k * 2))], A(col, a), s * 0.3)
    else: d.line([p[0], p[1], (lerp(p[1][0], p[2][0], (k - 0.5) * 2), lerp(p[1][1], p[2][1], (k - 0.5) * 2))], A(col, a), s * 0.3)
def cross(d, x, y, s, k, col, a=1.0):
    if k <= 0: return
    d.line([(x - s, y - s), (x - s + 2 * s * min(1, k * 2), y - s + 2 * s * min(1, k * 2))], A(col, a), s * 0.3)
    if k > 0.5: d.line([(x + s, y - s), (x + s - 2 * s * (k - 0.5) * 2, y - s + 2 * s * (k - 0.5) * 2)], A(col, a), s * 0.3)
def arrow(d, x0, y0, x1, y1, col, a=1.0, w=16):
    L = math.hypot(x1 - x0, y1 - y0) + 1e-6; ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    bx, by = x1 - ux * w * 2.4, y1 - uy * w * 2.4
    d.line([(x0, y0), (bx, by)], A(col, a), w)
    d.poly([(bx + nx * w * 1.6, by + ny * w * 1.6), (x1, y1), (bx - nx * w * 1.6, by - ny * w * 1.6)], A(col, a))
def sweat(d, x, y, s, a=1.0):
    d.circ(x, y, s, fill=A(CYAN, a)); d.poly([(x - s * 0.9, y - s * 0.3), (x, y - s * 2.2), (x + s * 0.9, y - s * 0.3)], A(CYAN, a))

# ---------------- environment ----------------
def river(d, t, speed=1.0, top=RIV1, bot=RIV2, a=1.0, surf=True):
    grad(d, top, bot)
    if surf:
        pts = [(x, 120 + 14 * math.sin(x / 70 + t * 9)) for x in range(-20, 1101, 20)]
        d.poly([(-20, 0)] + pts + [(1100, 0)], A(mix(top, WHITE, 0.25), 1))
    for u, y, L, v, w in STREAKS:
        x = ((u + t * 0.9 * v * speed) % 1.3) * 1400 - 200
        d.line([(x, y), (x + L * (0.5 + speed * 0.5), y + 4 * math.sin(t * 3 + y))], A(FOAM, 0.18 * a * min(1, speed)), w)
    for x, u, r, v in BUBS:
        yy = 1920 - ((u + t * 0.18 * v) % 1) * 1900; xx = x + 18 * math.sin(t * 2 + u * 9) + t * 40 * speed % 1080
        d.circ(xx % 1080, yy, r, outline=A(FOAM, 0.35 * a), w=3)
def rock(d, x, y, w, h, a=1.0):
    pts = [(x - w, y + h * 0.3), (x - w * 0.85, y - h * 0.5), (x - w * 0.4, y - h), (x + w * 0.3, y - h * 0.95), (x + w * 0.85, y - h * 0.55), (x + w, y + h * 0.3), (x + w, 2100), (x - w, 2100)]
    d.poly(pts, A(ROCK, a))
    d.poly([(x - w * 0.6, y - h * 0.7), (x - w * 0.3, y - h * 0.92), (x + w * 0.25, y - h * 0.88), (x + w * 0.1, y - h * 0.62)], A(ROCK_L, 0.55 * a))
    d.poly([(x + w * 0.5, y - h * 0.4), (x + w, y + h * 0.3), (x + w, 2100), (x + w * 0.4, 2100)], A(ROCK_D, 0.6 * a))
    for i in range(5): d.ell(x - w * 0.7 + i * w * 0.32, y - h * 0.82 + abs(i - 2) * h * 0.1, w * 0.12, h * 0.06, A(MOSS, 0.5 * a))

# ---------------- characters ----------------
def fish(d, x, y, s, t, mood="chill", a=1.0, nose=1.0, finglow=0.0, noseglow=0.0, maxglow=0.0, look=0.4, breath=True, flatk=1.0):
    """Exostoma: flattened catfish, side 3/4 view facing right. y = belly line (sits on surface)."""
    if breath: y += E.bob(t, 3, 0.35)
    hh = 78 * s * (1.9 - 0.9 * flatk)   # body height (flatk=1 -> flat)
    L = 250 * s
    # tail
    d.poly([(x - L * 0.92, y - hh * 0.25), (x - L * 1.25, y - hh * 0.95 - 14 * s * math.sin(t * 6)), (x - L * 1.18, y + 6 * s), (x - L * 0.92, y)], A(FIN_D, a))
    # pelvic + pectoral fins (spread flat on the ground)
    for fx_, rx, ry in ((x - L * 0.25, 85 * s, 22 * s), (x + L * 0.38, 120 * s, 28 * s)):
        d.ell(fx_, y + 4 * s, rx, ry, A(FIN, a))
        if finglow > 0: glow(d, fx_, y + 4 * s, rx * 1.1, STRIA, finglow * 0.9, 6)
        for j in range(7):
            u = (j + 0.5) / 7; xx = fx_ - rx * 0.85 + u * rx * 1.7
            yy0 = y + 4 * s - ry * 0.75 * math.sqrt(max(0, 1 - ((u - 0.5) * 1.9) ** 2)); yy1 = y + 4 * s + ry * 0.75 * math.sqrt(max(0, 1 - ((u - 0.5) * 1.9) ** 2))
            d.line([(xx, yy0), (xx, yy1)], A(mix(FIN_D, STRIA, finglow), a * (0.6 + 0.4 * finglow)), (3 + 3 * finglow) * s)
    # body
    pts = []
    for i in range(31):
        u = i / 30; xx = lerp(x - L, x + L * 0.95, u)
        top = hh * (math.sin(min(1, u * 1.05) * math.pi) ** 0.7) * (0.55 + 0.45 * u)
        pts.append((xx, y - 8 * s - top))
    body = [(x - L, y)] + pts + [(x + L * 0.95, y - hh * 0.25), (x + L * 1.02, y - 4 * s), (x + L * 0.9, y + 6 * s), (x - L, y + 6 * s)]
    d.poly(body, A(OLV, a))
    d.poly([(x - L * 0.9, y + 2 * s)] + [(px, lerp(py, y, 0.62)) for px, py in pts[2:28]] + [(x + L * 0.85, y + 2 * s)], A(BELLY, 0.45 * a))
    for i, (u, v, r) in enumerate(((0.2, 0.5, 14), (0.35, 0.7, 10), (0.5, 0.45, 16), (0.62, 0.68, 11), (0.75, 0.5, 9), (0.1, 0.62, 9))):
        px, py = pts[int(u * 30)]; d.circ(px, lerp(py, y, v), r * s, fill=A(SPOT, 0.45 * a))
    hx, hy = pts[17]; d.ell(hx - 30 * s, hy + hh * 0.18, 110 * s, 16 * s, A(OLV_L, 0.55 * a))
    # dorsal fin
    dx, dy = pts[13]; d.poly([(dx - 26 * s, dy + 6 * s), (dx + 4 * s, dy - 46 * s), (dx + 30 * s, dy + 6 * s)], A(FIN_D, a))
    # maxillary barbels (flat, pressed down)
    mx, my = x + L * 0.98, y - 4 * s
    for k_ in (0, 1):
        w2 = (16 - k_ * 5) * s
        d.poly([(mx - 4 * s, my - w2 * 0.3), (mx + 34 * s + k_ * 10 * s, my + 22 * s), (mx + 70 * s + k_ * 18 * s, my + 30 * s), (mx + 20 * s, my + 8 * s)], A(mix(FIN, STRIA, maxglow), a))
    if maxglow > 0: glow(d, mx + 40 * s, my + 20 * s, 50 * s, STRIA, maxglow * 0.8, 5)
    # eyes (dorsal, close together)
    ex, ey = pts[22]; ey += 18 * s
    for j, ox in enumerate((-14 * s, 20 * s)):
        er = (17 if j else 15) * s
        if mood == "happy": d.arc(ex + ox, ey + er * 0.4, er, er * 0.9, 200, 340, A(INK, a), 5 * s); continue
        big = 1.25 if mood == "scared" else 1.0
        d.circ(ex + ox, ey, er * big, fill=A(WHITE, a)); d.circ(ex + ox + look * er * 0.5, ey + er * 0.1, er * 0.5, fill=A(INK, a))
        d.circ(ex + ox + look * er * 0.5 - er * 0.18, ey - er * 0.15, er * 0.15, fill=A(WHITE, a))
        if mood in ("determined", "sus"):
            sl = 1 if mood == "determined" else (-1 if j == 0 else 1)
            d.line([(ex + ox - er, ey - er * 1.25 - sl * er * 0.25 * (1 if j == 0 else -1)), (ex + ox + er, ey - er * 1.25 + sl * er * 0.25 * (1 if j == 0 else -1))], A(INK, a), 5 * s)
    # mouth
    qx, qy = x + L * 0.93, y - 14 * s
    if mood in ("chill", "happy", "proud"): d.arc(qx - 18 * s, qy - 8 * s, 18 * s, 12 * s, 20, 160, A(INK, a), 4 * s)
    elif mood == "determined": d.line([(qx - 30 * s, qy), (qx - 4 * s, qy - 3 * s)], A(INK, a), 5 * s)
    elif mood == "scared": d.ell(qx - 16 * s, qy, 9 * s, 12 * s, A(INK, a))
    else: d.line([(qx - 28 * s, qy + 2 * s), (qx - 6 * s, qy - 2 * s)], A(INK, a), 4 * s)
    # nasal barbel: from nostril, arcs up and back over the head past the eyes
    nx_, ny_ = pts[27]; ny_ += 10 * s
    if nose > 0:
        n = 18; bp = []
        for i in range(n + 1):
            u = i / n * nose
            bx = nx_ - u * 190 * s; by = ny_ - math.sin(min(u, 1.2) / 1.2 * math.pi * 0.8) * 70 * s + 6 * s * math.sin(t * 4 + u * 5)
            bp.append((bx, by))
        if noseglow > 0:
            for px, py in bp[::3]: glow(d, px, py, 26 * s, STRIA, noseglow * 0.7, 4)
        for i in range(n):
            w = lerp(9, 3, i / n) * s
            d.line([bp[i], bp[i + 1]], A(mix(OLV_D, STRIA, noseglow), a), w)
        d.circ(nx_, ny_, 5 * s, fill=A(INK, 0.6 * a))
    return dict(eye=(ex, ey), nose=(nx_, ny_), tip=bp[-1] if nose > 0 else (nx_, ny_), mouth=(mx, my), pec=(x + L * 0.38, y + 4 * s), pel=(x - L * 0.25, y + 4 * s))

def pal(d, x, y, s, t, mood="scared", a=1.0, ang=0.0, col=ORG):
    """round little fish (gets swept away)."""
    c, sn = math.cos(ang), math.sin(ang)
    def R(u, v): return x + (u * c - v * sn) * s, y + (u * sn + v * c) * s
    d.poly([R(-60, 0), R(-110, -45), R(-100, 0), R(-110, 45)], A(mix(col, (0, 0, 0), 0.2), a))
    d.ell(*R(0, 0), 75 * s, 58 * s, A(col, a)); d.ell(*R(-10, -22), 40 * s, 16 * s, A(ORG_L, 0.55 * a))
    ex, ey = R(30, -14); er = 15 * s * (1.3 if mood == "scared" else 1)
    d.circ(ex, ey, er, fill=A(WHITE, a)); d.circ(ex, ey, er * 0.4, fill=A(INK, a))
    mx, my = R(55, 18)
    if mood == "scared": d.ell(mx, my, 9 * s, 12 * s, A(INK, a))
    else: d.arc(mx, my - 6 * s, 10 * s, 7 * s, 20, 160, A(INK, a), 3 * s)
    if mood == "scared": sweat(d, *R(10, -70), 8 * s, a)

def loach(d, x, y, s, t, a=1.0):
    pts = [(x - 220 * s + i * 22 * s, y + 10 * s * math.sin(i * 0.8 + t * 6)) for i in range(21)]
    for i, (px, py) in enumerate(pts): d.circ(px, py, (18 + 10 * math.sin(i / 20 * math.pi)) * s, fill=A((190, 160, 110), a))
    hx, hy = pts[-1]; d.circ(hx - 8 * s, hy - 8 * s, 6 * s, fill=A(INK, a))
    for k_ in range(3): d.line([(hx + 10 * s, hy + 6 * s), (hx + 40 * s, hy + (10 + k_ * 10) * s)], A((140, 110, 70), a), 3 * s)

# ---------------- scenes ----------------
SW = [(HOOK_HIT + 0.05, 140, 0.9, ORG), (HOOK_HIT + 0.55, 380, 0.7, PINK), (HOOK_HIT + 1.3, 250, 0.8, LIME), (at("stay", 1.5), 300, 0.75, ORG)]
def swept(d, t, items):
    for t0, yy, s, col in items:
        u = t - t0
        if 0 <= u < 1.6:
            x = -200 + u * 1100; y = yy + 60 * math.sin(u * 7) + u * u * 60
            pal(d, x, y, s, t, "scared", 1, ang=u * 9, col=col)
            for j in range(4): d.line([(x - 120 - j * 40, y - 30 + j * 20), (x - 220 - j * 60, y - 30 + j * 20)], A(FOAM, 0.4), 5)
def s_hook(t, d):
    river(d, t, 1.6)
    rock(d, 540, 1060, 470, 170)
    swept(d, t, SW[:3])
    f = fish(d, 560, 900, 1.25, t, "determined", nose=1.0)
    for j in range(5):
        yy = 760 + j * 34; ph = (t * 3 + j * 0.3) % 1
        d.line([(120 + ph * 300, yy - 120), (300 + ph * 300, yy - 120)], A(FOAM, 0.5), 6)
    slamtxt(d, t, -0.25, "冲不走！", 400, 150, YEL)
def s_stay(t, d):
    river(d, t, 1.4)
    z = 1.0 + 0.04 * pr(t, T["stay"], T["q"])
    rock(d, 540, 1100, 520, 180)
    swept(d, t, SW[3:])
    f = fish(d, 540, 940, 1.45 * z, t, "determined" if t < at("stay", 2) else "proud", finglow=0.25 * pr(t, at("stay", 1), at("stay", 2)))
    for px in (f["pec"], f["pel"]):
        for j in range(3):
            k = (t * 2 + j / 3) % 1
            d.circ(px[0], px[1] + 10, 30 + k * 80, outline=A(WHITE, 0.25 * (1 - k)), w=4)
    title(d, t, at("stay", 0.5), "纹丝不动", 400, 120, WHITE)
def s_q(t, d):
    grad(d, (34, 40, 70), (12, 14, 30))
    f = fish(d, 560, 1060, 1.2, t, "sus", look=-0.5)
    k = popk(t, T["q"] + 0.05, "bouncy")
    if k > 0:  # suction cup icon
        x, y, sc = 540, 560, 0.6 + 0.4 * k
        d.rect(x - 30 * sc, y - 170 * sc, x + 30 * sc, y - 40 * sc, fill=A((230, 90, 110), ap(t, T["q"])), r=20 * sc)
        d.d.chord((P(x - 130 * sc), P(y - 80 * sc), P(x + 130 * sc), P(y + 80 * sc)), 180, 360, fill=A((240, 110, 130), ap(t, T["q"])))
        d.text(x, y + 90, "吸盘？", int(110 * sc), A(WHITE, ap(t, T["q"])), k=1)
def s_reveal(t, d):
    rays(d, t, (40, 90, 120), (20, 50, 80))
    f = fish(d, 560, 1080, 1.55, t, "proud", finglow=0.4 + 0.6 * pr(t, at("reveal", 1.5), at("reveal", 2.5)), look=0.2)
    slamtxt(d, t, T["reveal"], "不是吸盘！", 360, 150, YEL)
    k = popk(t, at("reveal", 2))
    if k > 0:
        px, py = f["pel"]; arrow(d, 290, 770, px - 20, py + 30, STRIA, ap(t, at("reveal", 2)), 12)
        ptag(d, t, at("reveal", 2), 290, 720, "粘附纹 ≈ 防滑纹", STRIA, 40)
def s_flat(t, d):
    river(d, t, 1.0, (40, 110, 150), (14, 40, 66))
    d.rect(-20, 1200, 1100, 1960, fill=A(ROCK_D, 1)); d.rect(-20, 1190, 1100, 1210, fill=A(ROCK, 1))
    # tall fish vs flat fish cross-sections
    kk = popk(t, at("flat", 0.3))
    tx, ty = 300, 1190
    push = 40 * pr(t, at("flat", 2), at("flat", 3.5)) + 8 * math.sin(t * 9) * pr(t, at("flat", 2), at("flat", 3))
    d.ell(tx + push, ty - 170, 95, 170, A(ORG, ap(t, at("flat", 0.3)))); d.circ(tx + push + 30, ty - 250, 18, fill=A(WHITE, 1)); d.circ(tx + push + 34, ty - 250, 8, fill=A(INK, 1))
    if t > at("flat", 2): sweat(d, tx + push + 80, ty - 330, 10)
    fxp = 760
    d.ell(fxp, ty - 45, 190, 48, A(OLV, 1)); d.ell(fxp - 20, ty - 70, 120, 14, A(OLV_L, 0.5))
    d.circ(fxp + 70, ty - 70, 14, fill=A(WHITE, 1)); d.circ(fxp + 74, ty - 69, 6, fill=A(INK, 1))
    for i in range(6):  # flow lines: hit tall one, slide over flat one
        y = 760 + i * 70; ph = (t * 1.6 + i * 0.17) % 1
        x0 = -100 + ph * 1300
        yy = y if x0 < 600 else y + (min(0, (ty - 110) - y) * 0.0)
        if 170 < x0 < 430 and y > ty - 360: continue
        d.line([(x0, yy), (x0 + 120, yy)], A(FOAM, 0.6), 6)
    for i in range(3):
        arrow(d, 60, 860 + i * 110, 180, 860 + i * 110, (255, 120, 100), 0.9 * pr(t, at("flat", 2), at("flat", 2.4)), 12)
    arrow(d, 560, ty - 140, 960, ty - 140, CYAN, pr(t, at("flat", 3), at("flat", 3.5)), 10)
    ptag(d, t, at("flat", 0.6), tx, 760, "鼓鼓的鱼", WHITE, 36)
    ptag(d, t, at("flat", 1.0), fxp, 1060, "扁扁的它", STRIA, 36)
    ptag(d, t, at("flat", 2.2), tx, 600, "被推！", BAD, 46, WHITE)
    ptag(d, t, at("flat", 3.2), 720, 880, "水从头顶滑过", CYAN, 38)
    title(d, t, T["flat"] + 0.05, "压扁 = 推力小", 400, 100)
def s_fins(t, d):
    grad(d, (70, 76, 92), (40, 44, 56))
    # top view of fish: body + four pads
    cx, cy = 540, 900; s = 1.0 + 0.02 * math.sin(t * 2)
    pads = [(-1, -150, 170, 120, 45), (1, -150, 170, 120, 45), (-1, 170, 110, 90, 35), (1, 170, 110, 90, 35)]
    for i, (sd, dy, ox, rx, ry) in enumerate(pads):
        k = popk(t, at("fins", 0.4 + i * 0.25), "snappy")
        if k <= 0: continue
        px, py = cx + sd * ox * k, cy + dy
        gl = pr(t, at("fins", 2 + i * 0.25), at("fins", 2.4 + i * 0.25))
        if gl > 0: glow(d, px, py, rx * 1.3, STRIA, gl * 0.8, 6)
        d.ell(px, py, rx * min(k, 1.1), ry, A(FIN, 1))
        for j in range(8):
            u = (j + 0.5) / 8 - 0.5
            d.line([(px + u * rx * 1.6, py - ry * 0.8 * math.cos(u * 2.6)), (px + u * rx * 1.6, py + ry * 0.8 * math.cos(u * 2.6))], A(mix(FIN_D, STRIA, gl), 1), 5)
    d.ell(cx, cy - 20, 150, 340, A(OLV, 1)); d.ell(cx, cy - 330, 150, 80, A(OLV, 1))
    d.ell(cx - 40, cy - 120, 40, 200, A(OLV_L, 0.4))
    for sd in (-1, 1):
        d.circ(cx + sd * 40, cy - 330, 18, fill=A(WHITE, 1)); d.circ(cx + sd * 40, cy - 334, 8, fill=A(INK, 1))
    d.poly([(cx - 40, cy + 300), (cx, cy + 480), (cx + 40, cy + 300)], A(OLV, 1)); d.poly([(cx - 70, cy + 470), (cx, cy + 420), (cx + 70, cy + 470), (cx, cy + 560)], A(FIN_D, 1))
    title(d, t, T["fins"] + 0.05, "四块防滑垫", 360, 110, STRIA)
def s_barbel(t, d):
    grad(d, (60, 70, 90), (24, 28, 40)); rock(d, 540, 1150, 620, 160)
    gl = pr(t, at("barbel", 1.5), at("barbel", 2.3))
    f = fish(d, 300, 1000, 2.2, t, "chill", maxglow=gl, nose=0.7)
    mx, my = f["mouth"]
    ptag(d, t, at("barbel", 2), 760, 760, "扁扁的颌须", STRIA, 42)
    if t > at("barbel", 2): arrow(d, 760, 810, mx + 40 * 2.2, my + 24 * 2.2, STRIA, ap(t, at("barbel", 2)), 10)
    title(d, t, T["barbel"] + 0.05, "胡须也帮忙", 360, 100)
def s_catfish(t, d):
    grad(d, (36, 60, 50), (14, 26, 24))
    ka = popk(t, at("catfish", 0.2)); kb = popk(t, at("catfish", 1.6))
    if ka > 0:
        loach(d, 540, 650, 1.3 * min(ka, 1.05), t, ap(t, at("catfish", 0.2)))
        ptag(d, t, at("catfish", 0.3), 540, 520, "泥鳅", WHITE, 44)
        cross(d, 830, 650, 50, pr(t, at("catfish", 1.0), at("catfish", 1.4)), BAD)
    if kb > 0:
        fish(d, 600, 1150, 1.15 * min(kb, 1.05), t, "proud", ap(t, at("catfish", 1.6)))
        ptag(d, t, at("catfish", 1.7), 540, 900, "鲇鱼（鮡科）", STRIA, 44)
        check(d, 880, 900, 46, pr(t, at("catfish", 2.4), at("catfish", 2.8)), GOOD)
def s_nameq(t, d):
    grad(d, (20, 20, 34), (8, 8, 16))
    sp = pr(t, T["nameq"], at("nameq", 1))
    d.ell(540, 1060, 520 * sp, 260 * sp, A((255, 240, 200), 0.10)); d.ell(540, 1060, 380 * sp, 190 * sp, A((255, 240, 200), 0.10))
    f = fish(d, 520, 1080, 1.5, t, "chill", nose=0.15 + 0.85 * pr(t, at("nameq", 1.4), at("nameq", 3)), noseglow=pr(t, at("nameq", 1.4), at("nameq", 2)), look=0.6)
    title(d, t, T["nameq"] + 0.05, "看鼻子！", 400, 130, YEL)
def s_nose(t, d):
    grad(d, (30, 40, 70), (12, 16, 34))
    gk = pr(t, T["nose"], at("nose", 3.5))
    f = fish(d, 560, 1180, 2.0, t, "proud", nose=0.25 + 1.0 * E.ease_out_cubic(gk), noseglow=0.8)
    ex, ey = f["eye"]; edge = ex - 14 * 2.0 - 15 * 2.0 - 6
    a_ = pr(t, at("nose", 1), at("nose", 1.4))
    for yy in range(int(ey - 300), int(ey + 60), 30): d.line([(edge, yy), (edge, yy + 16)], A(WHITE, 0.8 * a_), 5)
    ptag(d, t, at("nose", 1.1), edge, ey - 340, "眼睛后缘", WHITE, 34)
    tx, ty = f["tip"]
    if tx < edge and t > at("nose", 3):
        check(d, tx - 50, ty - 90, 40, pr(t, at("nose", 3.2), at("nose", 3.6)), GOOD)
        ptag(d, t, at("nose", 3.3), 540, 520, "超过了！", GOOD, 54)
    title(d, t, T["nose"] + 0.05, "鼻须", 380, 120, STRIA)
def s_latin(t, d):
    grad(d, (60, 34, 80), (24, 12, 40))
    for i, (s_, cn, col, x) in enumerate((("nasus", "鼻子", CYAN, 250), ("barba", "胡子", STRIA, 830))):
        k = popk(t, at("latin", 0.3 + i * 0.9), "snappy")
        if k <= 0: continue
        y = 600 + (1 - min(k, 1)) * 60; a_ = ap(t, at("latin", 0.3 + i * 0.9))
        d.rect(x - 190, y - 110, x + 190, y + 110, fill=A((255, 255, 255), 0.08 * a_), r=30)
        d.text(x, y - 35, s_, 62, A(col, a_), k=1); d.text(x, y + 50, cn, 58, A(WHITE, a_), k=1)
    if t > at("latin", 1.2): d.text(540, 600, "+", 100, A(WHITE, ap(t, at("latin", 1.2))), k=1)
    k = popk(t, at("latin", 2.4), "heavy")
    if k > 0:
        d.text(540, 830, "↓", 80, A(WHITE, ap(t, at("latin", 2.4))), k=1)
        d.text(540, 990, "nasibarbatum", int(92 * (0.85 + 0.15 * k)), A(YEL, ap(t, at("latin", 2.4))), k=1)
    f = fish(d, 560, 1170, 0.85, t, "happy", noseglow=0.6 * pulse(t, [at("latin", 2.4)], 2))
def s_sense(t, d):
    grad(d, (20, 50, 70), (6, 18, 30))
    f = fish(d, 420, 1150, 1.6, t, "chill", noseglow=0.5)
    tx, ty = f["tip"]; mx, my = f["mouth"]
    for j, (px, py) in enumerate(((tx, ty), (mx + 70 * 1.6, my + 30 * 1.6))):
        for r in range(3):
            k = (t * 1.2 + r / 3 + j * 0.5) % 1
            d.circ(px, py, 20 + k * 120, outline=A(CYAN, 0.6 * (1 - k)), w=5)
    ptag(d, t, at("sense", 1.5), 300, 620, "触碰", CYAN, 56)
    ptag(d, t, at("sense", 2.3), 780, 620, "气味", LIME, 56)
    title(d, t, T["sense"] + 0.05, "胡须 = 雷达", 400, 110)
def s_murky(t, d):
    grad(d, (60, 70, 50), (24, 28, 20))
    for i in range(60):
        x = (i * 97 + t * 160 * (1 + i % 3)) % 1180 - 50; y = (i * 151) % 1700 + 100 + 20 * math.sin(t * 2 + i)
        d.circ(x, y, 6 + i % 10, fill=A((150, 140, 100), 0.25))
    f = fish(d, 380, 1150, 1.3, t, "determined", noseglow=0.7)
    tx, ty = f["tip"]
    fx_, fy_ = 860, 1090 + 10 * math.sin(t * 3)
    found = t > at("murky", 2.5)
    d.circ(fx_, fy_, 22, fill=A((255, 140, 120), 1)); d.circ(fx_ + 30, fy_ - 10, 14, fill=A((255, 140, 120), 1))
    for r in range(2):
        k = (t * 1.5 + r / 2) % 1
        d.circ(fx_, fy_, 30 + k * 160, outline=A(LIME, 0.55 * (1 - k)), w=4)
    if found: ptag(d, t, at("murky", 2.5), fx_, fy_ - 130, "找到了！", LIME, 44)
    title(d, t, T["murky"] + 0.05, "浑水也不怕", 400, 110)
def s_where(t, d):
    grad(d, (44, 96, 70), (16, 44, 32))
    # stylised map: India (left), Myanmar (right), border dashed
    kb = pr(t, at("where", 0.3), at("where", 1.3))
    pts = [(560 + 40 * math.sin(i * 0.9), 400 + i * 60) for i in range(18)]
    for i in range(int(len(pts) * kb) - 1):
        if i % 2 == 0: d.line([pts[i], pts[i + 1]], A(WHITE, 0.8), 6)
    tag(d, 330, 520, "印度", WHITE, ap(t, at("where", 0.3)), 40); tag(d, 800, 520, "缅甸", WHITE, ap(t, at("where", 0.5)), 40)
    # stream to Chindwin
    ks = pr(t, at("where", 1.5), at("where", 2.6))
    sp = [(400 + i * 22, 900 + 70 * math.sin(i * 0.5)) for i in range(int(22 * ks) + 1)]
    if len(sp) > 1: d.line(sp, A(CYAN, 1), 12)
    k = popk(t, at("where", 1.5), "bouncy")
    if k > 0:
        px, py = 420, 880 - 40 * (1 - min(k, 1))
        glow(d, px, py - 60, 90, YEL, 0.6)
        d.circ(px, py - 70, 44 * min(k, 1.1), fill=A(RED, 1)); d.poly([(px - 34, py - 50), (px, py + 10), (px + 34, py - 50)], A(RED, 1)); d.circ(px, py - 70, 16, fill=A(WHITE, 1))
        ptag(d, t, at("where", 1.7), px, py - 170, "曼尼普尔", YEL, 42)
    ptag(d, t, at("where", 2.8), 860, 1000, "→ 钦敦江", CYAN, 38)
    fish(d, 560, 1150, 0.6, t, "happy")
def s_rare(t, d):
    grad(d, (30, 60, 60), (10, 24, 26))
    for i in range(4):
        x0 = -100 + i * 320; d.poly([(x0, 1000), (x0 + 220, 560 + i % 2 * 80), (x0 + 480, 1000)], A(mix((40, 90, 70), (0, 0, 0), i * 0.1), 1))
    river(d, t, 0.8, (50, 130, 150), (20, 60, 80), surf=False) if False else None
    d.rect(-20, 1000, 1100, 1960, fill=A((30, 90, 110), 1))
    for u, y, L, v, w in STREAKS[:30]:
        x = ((u + t * 0.5 * v) % 1.3) * 1400 - 200; d.line([(x, 1020 + (y % 900)), (x + L * 0.6, 1020 + (y % 900))], A(FOAM, 0.15), w)
    # magnifier sweeping, finds tiny fish
    mx = 540 + 260 * math.sin((t - T["rare"]) * 0.9); my = 1070
    found = abs(mx - 640) < 120
    f_ = fish(d, 640, 1110, 0.28, t, "chill", nose=1.0)
    d.circ(mx, my, 150, outline=A(WHITE, 0.95), w=14); d.line([(mx + 105, my + 105), (mx + 200, my + 200)], A(WHITE, 0.95), 26)
    d.circ(mx, my, 136, fill=A(WHITE, 0.08))
    title(d, t, T["rare"] + 0.05, "难得一见", 400, 120, YEL)
def s_ident(t, d):
    grad(d, (34, 34, 54), (14, 14, 26))
    title(d, t, T["ident"] + 0.05, "三处细节", 360, 110, WHITE)
    rows = [("鼻须超过眼睛后缘", STRIA), ("脂鳍和尾鳍连在一起", CYAN), ("嘴唇上的纹路形状", LIME)]
    for i, (s_, col) in enumerate(rows):
        t0 = at("ident", 0.8 + i * 0.9); k = popk(t, t0)
        if k <= 0: continue
        y = 620 + i * 170; a_ = ap(t, t0); x = 540 + (1 - min(k, 1)) * 80
        d.rect(x - 360, y - 62, x + 360, y + 62, fill=A((255, 255, 255), 0.07 * a_), r=30)
        d.text(x - 300, y, str(i + 1), 64, A(col, a_), k=1)
        d.text(x + 30, y, s_, 46, A(WHITE if i else STRIA, a_), k=1)
        check(d, x + 310, y, 30, pr(t, t0 + 0.3, t0 + 0.6), GOOD, a_)
    fish(d, 560, 1170, 0.7, t, "proud", noseglow=0.6)
def s_card(t, d):
    grad(d, (40, 70, 90), (16, 30, 44))
    for i in range(12): d.circ(540, 900, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 600 * (0.8 + 0.2 * k), 860 * (0.8 + 0.2 * k); cx, cy = 540, 880; a_ = ap(t, T["card"] + 0.1)
    glow(d, cx, cy, 560, (150, 220, 255), 0.35 * a_, 6)
    d.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=A((250, 246, 232), a_), r=36)
    tag(d, cx, cy - h / 2 + 80, "一句话学会", GOLD, a_, 32)
    fish(d, cx + 10, cy - 120, 0.85, t, "proud", a_, finglow=0.6, maxglow=0.6, noseglow=0.6, breath=False)
    d.text(cx, cy + 70, "激流鱼三件套", 54, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("扁身体：推力小", "防滑鳍：贴得牢", "长鼻须：探路找食")):
        kk = popk(t, at("card", 1.2 + i * 0.6))
        if kk > 0: d.text(cx, cy + 160 + i * 68, s_, 40, A((60, 70, 90), ap(t, at("card", 1.2 + i * 0.6))), k=1)
def s_end(t, d):
    river(d, t, 1.5)
    rock(d, 540, 1080, 480, 170)
    swept(d, t, [(T["end"] + 0.4, 300, 0.7, ORG), (T["end"] + 1.6, 520, 0.6, LIME), (T["end"] + 2.8, 250, 0.7, PINK)])
    fish(d, 560, 920, 1.3, t, "happy", finglow=0.3, noseglow=0.3)
    slamtxt(d, t, T["end"] + 0.05, "冲不走", 380, 150, YEL)
    ra = ap(t, at("end", 2), 0.3)
    if ra > 0:
        d.rect(170, 480, 910, 600, fill=A((10, 20, 34), 0.6 * ra), r=20)
        d.text(540, 518, "J. Nat. Hist. 60 (2026) · Torisha & Shangningam", 26, A(WHITE, 0.95 * ra))
        d.text(540, 562, "印度达纳曼朱里大学 · 曼尼普尔布帕尔溪", 26, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions (queued, spring pop, one highlight word) ----------------
HL = {"hook": "冲走", "stay": "贴", "q": "吸盘", "reveal": "粘附纹", "flat": "扁扁", "fins": "防滑垫", "barbel": "扁", "catfish": "鲇鱼",
      "nameq": "鼻子", "nose": "长须", "latin": "鼻子长胡子", "sense": "触碰和气味", "murky": "探路", "where": "曼尼普尔", "rare": "很少见", "ident": "三处细节", "end": "身上"}
def subs(t, d):
    for a, b, s, key in SUBS:
        if a <= t < b:
            ee = E.enter_exit(t, max(a, 0), b, 0.3, 0.12, rise=18, s0=0.96)
            al = ee["alpha"] if a > 0 else (1 - pr(t, b - 0.12, b))
            if al <= 0.01: return
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70 + ee["dy"] * (a > 0)
            w = max(d.tlen(x, 54, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 70 + 46, fill=A((12, 14, 26), 0.82 * al), r=22)
            hw = HL.get(key)
            for i, x in enumerate(ls):
                yy = y0 + i * 70
                if hw and hw in x:
                    j = x.index(hw); parts = [(x[:j], WHITE), (hw, YEL), (x[j + len(hw):], WHITE)]
                    tw = d.tlen(x, 54, 1); xx = 540 - tw / 2
                    for p_, c_ in parts:
                        if p_: d.text(xx, yy, p_, 54, A(c_, al), anchor="lm", k=1); xx += d.tlen(p_, 54, 1)
                else: d.text(540, yy, x, 54, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇新物种"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)

SF = {n: globals()["s_" + n] for n in NAMES}
SECS = [(-1, HOOKCUT, s_hook)] + [(T[n], nxt(n), SF[n]) for n in NAMES[1:]]
SECS = [(a, (99 if n == len(SECS) - 1 else b), f) for n, (a, b, f) in enumerate(SECS)]
def cam(t):
    z = 1.0 + 0.04 * pulse(t, [HOOK_HIT, BIG2], 3)
    for a, b, f in SECS:   # slow push during every hold (no dead frames)
        if a <= t < b: z += 0.03 * eio(pr(t, max(a, 0), min(b, DUR))); break
    if HOOK_STOP <= t < HOOKCUT: z += 0.04 * pr(t, HOOK_STOP, HOOKCUT)
    amp = 8 * pulse(t, [HOOK_HIT, BIG2], 5)
    sx, sy = shake(t, amp, 40)
    return z, 540 + sx, 900 + sy
def frame(t, fi=0):
    img = Image.new("RGB", (W, H), (20, 30, 50)); d = D(img)
    for a, b, sf in SECS:
        if a <= t < b: sf(t, d); break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - (t - c) / 0.1)))
    brand(t, d); subs(t, d)
    out = img.resize((OW, OH), Image.LANCZOS)
    out = E.vignette(out, 0.2); out = E.grain(out, 0.03, seed=fi)
    return out
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/ex_test_{float(ts):05.2f}.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                              "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", out], stdin=subprocess.PIPE)
        last = None; errs = 0
        for i in range(i0, i1):
            try: last = frame(i / FPS, i).tobytes()
            except Exception as e: errs += 1; print('ERR', i, e, file=sys.stderr)
            if last: p.stdin.write(last)
        p.stdin.close(); p.wait(); print('errs', errs, file=sys.stderr)
