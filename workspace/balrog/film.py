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



# ---------------- characters ----------------
CRK = (156, 104, 62); CRK_D = (112, 72, 42); CRK_L = (206, 156, 104); ROCK = (92, 70, 58); ROCK_D = (60, 44, 38); ROCK_L = (130, 102, 84)
FIRE1 = (255, 90, 40); FIRE2 = (255, 180, 50); FIRE3 = (255, 240, 150); SEAC = (40, 140, 200)
def cricket(d, x, y, s, t, mood="happy", a=1.0, ang=0.0, flip=1, wave_=0.0, leg_hl=0.0, sq=0.0):
    c, sn = math.cos(ang), math.sin(ang)
    def T_(u, v): u *= flip; return x + (u * c - v * sn) * s, y + (u * sn + v * c) * s
    def L(pts, col, w): d.line([T_(*p) for p in pts], A(col, a), w * s)
    bob = 4 * math.sin(t * 5)
    lc = mix(CRK_D, (255, 220, 80), leg_hl)
    # antennae
    for k, (ax, ay) in enumerate(((-300, -260), (-340, -170))):
        pts = [(90 + j * (ax - 90) / 12, -40 + j * (ay + 40) / 12 + 30 * math.sin(j * 0.5 + t * 2 + k)) for j in range(13)]
        L(pts, CRK_D, 4)
    # far legs
    L([(-40, 10), (-110, -150), (-250, 90 + bob)], mix(lc, (0, 0, 0), 0.2), 12)
    L([(30, 20), (10, 80), (-30, 110)], mix(lc, (0, 0, 0), 0.2), 9)
    # body (humped)
    d.ell(*T_(-30, -10), 150 * s, 85 * s * (1 - 0.1 * sq), A(CRK, a))
    for j in range(4): d.arc(*T_(-110 + j * 50, -20), 30 * s, 70 * s, 250, 290, A(CRK_D, a), 4 * s)
    d.ell(*T_(-60, -55), 70 * s, 22 * s, A(CRK_L, 0.7 * a))
    # head
    hx, hy = T_(120, -20)
    d.circ(hx, hy, 62 * s, fill=A(CRK, a))
    # near legs
    L([(-20, 20), (-90, -170), (-260, 110 + bob)], lc, 16); d.circ(*T_(-90, -170), 12 * s, fill=A(lc, a))
    L([(40, 30), (60, 100), (20, 130)], lc, 11); L([(90, 30), (130, 100), (170, 120)], lc, 11)
    if wave_ > 0:
        L([(100, 20), (170, -40), (200 + 20 * math.sin(t * 12), -110)], lc, 11)
    ex, ey = T_(140, -40); er = 22 * s
    if mood == "happy": d.arc(ex, ey + er * 0.3, er * 0.8, er * 0.7, 200, 340, A(INK, a), 6 * s)
    else:
        d.circ(ex, ey, er, fill=A(WHITE, a)); d.circ(ex + flip * er * 0.25, ey, er * (0.4 if mood == "shock" else 0.55), fill=A(INK, a))
        d.circ(ex + flip * er * 0.1, ey - er * 0.25, er * 0.17, fill=A(WHITE, a))
    mx, my = T_(160, 10)
    if mood in ("happy", "proud"): d.arc(mx, my, 18 * s, 12 * s, 20, 160, A(INK, a), 5 * s)
    else: d.ell(mx, my, 8 * s, 10 * s, A(INK, a))
    d.ell(*T_(105, 0), 14 * s, 8 * s, A((255, 140, 150), 0.6 * a))
def flame(d, x, y, s, t, a=1.0, seed=0):
    for k, col in enumerate((FIRE1, FIRE2, FIRE3)):
        r = s * (1 - k * 0.28)
        pts = []
        for i in range(24):
            u = i / 24 * 2 * math.pi
            rr = r * (0.75 + 0.25 * math.sin(u * 5 + t * 9 + seed + k)) * (1 + 0.8 * max(0, -math.sin(u)) ** 3)
            pts.append((x + math.cos(u) * rr * 0.7, y + k * s * 0.12 + math.sin(u) * rr))
        d.poly(pts, A(col, a))
def demon(d, x, y, s, t, a=1.0):
    flame(d, x, y, 260 * s, t, a, 1)
    for sd in (-1, 1):
        d.poly([(x + sd * 90 * s, y - 150 * s), (x + sd * 180 * s, y - 330 * s), (x + sd * 40 * s, y - 190 * s)], A((80, 30, 30), a))
        d.ell(x + sd * 70 * s, y - 60 * s, 34 * s, 20 * s, A((255, 255, 200), a)); d.ell(x + sd * 70 * s, y - 60 * s, 12 * s, 14 * s, A((140, 20, 20), a))
    d.poly([(x - 80 * s, y + 40 * s), (x + 80 * s, y + 40 * s), (x, y + 90 * s)], A((80, 20, 20), a))
def tunnel_bg(d, t, light=0.0, hue=0.0):
    grad(d, mix((40, 30, 30), (90, 30, 30), hue), mix((14, 10, 12), (40, 10, 12), hue))
    d.d.ellipse((P(60), P(380), P(1020), P(1500)), fill=A(ROCK, 1))
    d.d.ellipse((P(160), P(500), P(920), P(1460)), fill=A(ROCK_D, 1))
    for i in range(26): d.ell(100 + (i * 173) % 900, 420 + (i * 97) % 1000, 30 + i % 3 * 12, 14, A(ROCK_L, 0.35))
    if light > 0: glow(d, 540, 820, 380, (255, 240, 200), 0.25 * light)
def drop(d, x, y, r, a=1.0): d.circ(x, y, r, fill=A((170, 220, 255), a)); d.poly([(x - r * 0.8, y - r * 0.4), (x + r * 0.8, y - r * 0.4), (x, y - r * 2.2)], A((170, 220, 255), a))

# ---------------- scenes ----------------
def s_hook(t, d):
    frz = t >= HOOK_STOP; tt = min(t, HOOK_STOP)
    tunnel_bg(d, tt, 0, 1.0 - 0.7 * pr(tt, HOOK_HIT, HOOK_HIT + 0.6))
    f = 1 - ease(pr(tt, HOOK_HIT, HOOK_HIT + 0.35))
    if f > 0: demon(d, 540, 880, 1.2 * (0.7 + 0.3 * back(pr(tt, -0.3, HOOK_HIT))), tt, f)
    k = ease(pr(tt, HOOK_HIT, HOOK_HIT + 0.3))
    if k > 0: cricket(d, 560, 950, 1.0 * back(pr(tt, HOOK_HIT, HOOK_HIT + 0.3)), tt, "shock" if frz else "happy", 1, wave_=1)
    if t >= HOOK_HIT: sparks(d, 540, 900, t, HOOK_HIT, 50, 1100, FIRE2, 1, 4, 1.0)
    kk = back(pr(t, -0.2, HOOK_HIT)); k2 = pulse(t, [HOOK_HIT], 6)
    if kk > 0: d.text(540, 330, "炎魔", int(170 * (0.6 + 0.4 * kk) * (1 + 0.08 * k2)), A(FIRE2, 1), k=1)
    tag(d, 540, 480, "其实是只蟋蟀", WHITE, popk(t, qb(1.2)), 36)
    if frz: glow(d, 540, 900, 160, WHITE, pr(t, HOOK_STOP, HOOKCUT))
def s_island(t, d):
    grad(d, (90, 190, 230), SEAC)
    for i in range(8): d.arc(100 + i * 120, 1000 + (i % 3) * 120, 40, 14, 200, 340, A(WHITE, 0.4), 5)
    k = back(pr(t, HOOKCUT, HOOKCUT + 0.4))
    pts = [(540 + math.cos(u) * 300 * k * (1 + 0.15 * math.sin(3 * u)), 820 + math.sin(u) * 150 * k * (1 + 0.2 * math.cos(2 * u))) for u in [i / 30 * 2 * math.pi for i in range(30)]]
    d.poly(pts, A((214, 196, 140), 1)); d.poly([(540 + (x - 540) * 0.75, 810 + (y - 820) * 0.7) for x, y in pts], A((120, 170, 90), 1))
    d.poly([(560, 700), (640, 790), (480, 790)], A((140, 120, 100), 1))
    title(d, t, HOOKCUT, "希腊 · 小岛", 300, 100)
    kr = ease(pr(t, at("island", 1), at("island", 2.5)))
    d.rect(240, 1040, lerp(240, 840, kr), 1080, fill=A(YEL, 1), r=8)
    tag(d, 540, 1150, "约 6 公里长", YEL, popk(t, at("island", 2.5)), 36)
    pk = popk(t, at("island", 3.5))
    if pk > 0: d.circ(600, 760 - 30 * pk, 22, fill=A(BAD, 1)); d.poly([(582, 770 - 30 * pk), (618, 770 - 30 * pk), (600, 800)], A(BAD, 1))
def s_tunnel(t, d):
    grad(d, (255, 200, 140), (230, 140, 90))
    d.poly([(-20, 1250), (300, 650), (540, 520), (820, 640), (1100, 1250)], A((150, 120, 90), 1))
    d.poly([(-20, 1250), (300, 650), (540, 520), (820, 640), (1100, 1250)], A((150, 120, 90), 1))
    z = ease(pr(t, at("tunnel", 2), at("tunnel", 5)))
    r = lerp(90, 420, z)
    d.ell(540, 900, r, r * 1.1, A((30, 20, 20), 1))
    d.arc(540, 900, r, r * 1.1, 180, 360, A(ROCK_L, 1), 18)
    if z > 0.6: cricket(d, 540, 960, 0.35 * ease(pr(z, 0.6, 1)), t, "open", 1)
    title(d, t, T["tunnel"], "岛上唯一的“洞”", 300, 90)
    tag(d, 540, 460, "人造隧道", (255, 220, 120), popk(t, at("tunnel", 1.2)), 36)
    dk = popk(t, at("tunnel", 4))
    if dk > 0:
        d.rect(820, 640, 860, lerp(640, 1180, ease(pr(t, at("tunnel", 4), at("tunnel", 6)))), fill=A(YEL, dk), r=10)
        tag(d, 780, 1200 - 20, "25 米深", YEL, dk, 34)
def s_walls(t, d):
    tunnel_bg(d, t, 1)
    u = t - T["walls"]
    bx = 540 + 280 * math.sin(u * 1.6)
    spots = [(260, 640), (780, 600), (330, 980), (760, 1020), (540, 520), (200, 820), (880, 820), (620, 1180), (420, 1200)]
    for i, (x, y) in enumerate(spots):
        k = popk(t, T["walls"] + 0.1 + i * 0.12)
        lit = max(0, 1 - abs(x - bx) / 260)
        if k > 0: cricket(d, x, y, 0.32 * k, t + i, "happy" if lit > 0.5 else "open", 0.5 + 0.5 * lit, ang=(i % 4 - 1.5) * 0.6, flip=1 if i % 2 else -1)
    d.poly([(540, 1700), (bx - 160, 450), (bx + 160, 450)], A((255, 250, 210), 0.12))
    glow(d, bx, 780, 220, (255, 250, 210), 0.25)
    title(d, t, T["walls"], "满墙都是", 300, 110)
def s_dna(t, d):
    grad(d, (30, 30, 70), (10, 10, 30))
    title(d, t, T["dna"], "长相 + DNA", 300, 110, (140, 220, 255))
    cricket(d, 360, 900, 0.7, t, "open", 0.9)
    u = t - T["dna"]
    for i in range(16):
        y = 600 + i * 38; ph = u * 4 + i * 0.5
        x1, x2 = 780 + 90 * math.sin(ph), 780 - 90 * math.sin(ph)
        d.line([(x1, y), (x2, y)], A((255, 255, 255), 0.4), 5)
        d.circ(x1, y, 12, fill=A((120, 200, 255), 1)); d.circ(x2, y, 12, fill=A((255, 120, 180), 1))
    sy = 600 + (u * 260) % 620
    d.rect(180, sy - 4, 900, sy + 4, fill=A(GOOD, 0.7))
def s_reveal(t, d):
    rays(d, t, (255, 180, 60), (230, 90, 40))
    cricket(d, 560, 940, 1.15, t, "happy", 1, wave_=1)
    stamp(d, t, BIG2, "新物种！", 540, 330, 150, (200, 40, 60))
    tag(d, 540, 480, "Dolichopoda balrogi", WHITE, popk(t, at("reveal", 1.5)), 34)
    if t >= BIG2: sparks(d, 540, 900, t, BIG2, 60, 1300, YEL, 1, 3, 1.2); sparks(d, 540, 900, t, BIG2 + 0.05, 40, 1000, WHITE, 1, 5, 1.0)
def s_name(t, d):
    tunnel_bg(d, t, 0, 1)
    title(d, t, T["name"], "名字：炎魔", 300, 110, FIRE2)
    demon(d, 540, 820, 1.0 * popk(t, at("name", 0.5)), t)
    cricket(d, 800, 1150, 0.4, t, "shock", 1, flip=-1)
    tag(d, 540, 470, "《魔戒》里的火焰恶魔", WHITE, popk(t, at("name", 1.5)), 32)
def s_real(t, d):
    k = ease(pr(t, at("real", 2), at("real", 3)))
    tunnel_bg(d, t, k, 1 - k)
    if k < 1: demon(d, 540, 820, 1.0 * (1 - k), t, 1 - k)
    if k > 0: cricket(d, 560, 920, 1.0 * back(k), t, "happy", 1, wave_=1)
    if k > 0.3: tag(d, 540, 1170, "完全无害", GOOD, popk(t, at("real", 3)), 44, WHITE)
    title(d, t, T["real"], "名不副实", 300, 110)
def s_legs(t, d):
    grad(d, (240, 200, 150), (200, 140, 90))
    title(d, t, T["legs"], "又长又弯的腿", 300, 100, (110, 50, 20))
    hl = 0.5 + 0.5 * math.sin((t - T["legs"]) * 6) if t > at("legs", 2) else 0
    cricket(d, 640, 900, 1.15, t, "happy", 1, leg_hl=hl)
    tag(d, 330, 1180, "棕色身体", CRK, popk(t, at("legs", 0.8)), 34, WHITE)
    tag(d, 760, 1180, "长弯腿", YEL, popk(t, at("legs", 2)), 34)
def s_grip(t, d):
    tunnel_bg(d, t, 0.6)
    title(d, t, T["grip"], "倒挂也不掉", 300, 110)
    u = t - T["grip"]
    fl = ease(pr(t, at("grip", 2), at("grip", 3.5)))
    cricket(d, 540, lerp(1050, 640, fl), 0.85, t, "happy" if fl > 0.9 else "open", 1, ang=math.pi * fl, flip=1)
    k = popk(t, at("grip", 4))
    if k > 0: tag(d, 540, 1150, "爪子钩住岩壁", YEL, k, 34)
def s_genus(t, d):
    grad(d, (60, 120, 170), (24, 60, 110))
    n = int(68 * ease(pr(t, T["genus"], at("genus", 3))))
    for i in range(n):
        x = 220 + (i % 10) * 70; y = 600 + (i // 10) * 80
        col = (255, 200, 60) if i < 51 and t > at("genus", 4) else CRK_L
        d.ell(x, y, 22, 12, A(col, 1)); d.line([(x - 10, y), (x - 26, y - 22)], A(col, 1), 4); d.line([(x + 14, y - 4), (x + 30, y - 24)], A(col, 1), 3)
    k = popk(t, at("genus", 0.3))
    if k > 0: d.text(540, 330, f"{max(1, n)} 种", int(130 * k), A(YEL, 1), k=1)
    tag(d, 540, 470, "51 种在希腊", (255, 200, 60), popk(t, at("genus", 4)), 36)
def s_fragile(t, d):
    tunnel_bg(d, t, 0.5)
    title(d, t, T["fragile"], "一洞一家", 300, 110)
    cricket(d, 540, 900, 0.7, t, "open" if t < at("fragile", 4) else "shock", 1)
    hum = 1 - 0.6 * ease(pr(t, at("fragile", 4), at("fragile", 6)))
    d.rect(820, 600, 880, 1100, fill=A((20, 14, 20), 0.7), r=20)
    d.rect(830, 1090 - 480 * hum, 870, 1090, fill=A(mix(BAD, (120, 200, 255), hum), 1), r=14)
    tag(d, 850, 1150, "湿度", WHITE, popk(t, at("fragile", 1)), 30)
    for i in range(4):
        ph = (t * 0.8 + i * 0.25) % 1
        if hum > 0.7: drop(d, 300 + i * 70, 520 + ph * 500, 10, 0.8)
    if hum < 0.6: tag(d, 540, 470, "危险！", BAD, popk(t, at("fragile", 5)), 42, WHITE)
def s_near(t, d):
    grad(d, (120, 200, 160), (50, 120, 110))
    title(d, t, T["near"], "新物种在哪？", 300, 100)
    items = [("雨林", (60, 160, 70), 330, 640, 0.5), ("深海", (30, 80, 160), 750, 640, 1.0)]
    for s, col, x, y, b in items:
        k = popk(t, at("near", b))
        if k > 0:
            d.circ(x, y, 120 * k, fill=A(col, 1)); d.text(x, y, s, 50, A(WHITE, k), k=1)
    k = popk(t, at("near", 3))
    if k > 0:
        d.rect(330, 860, 750, 1150, fill=A(ROCK, k), r=30); d.ell(540, 1080, 120, 110, A((30, 20, 20), k))
        cricket(d, 540, 1000, 0.3, t, "happy", k, wave_=1)
        tag(d, 540, 870, "人造隧道", YEL, k, 34)
        glow(d, 540, 1000, 260, YEL, 0.25 * k)
def s_card(t, d):
    grad(d, (30, 90, 70), (12, 50, 40))
    for i in range(12): d.circ(540, 900, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1)
    if k <= 0: return
    w, h = 560 * (0.7 + 0.3 * k), 820 * (0.7 + 0.3 * k); cx, cy = 540, 880
    d.rect(cx - w / 2 + 14, cy - h / 2 + 18, cx + w / 2 + 14, cy + h / 2 + 18, fill=A((0, 0, 0), 0.3 * k), r=36)
    d.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=A((250, 244, 230), k), r=36)
    d.rect(cx - w / 2 + 24, cy - h / 2 + 24, cx + w / 2 - 24, cy + h / 2 - 24, outline=A((200, 50, 60), k), w=6, r=24)
    d.text(cx - w / 2 + 70, cy - h / 2 + 80, "J", 70, A((200, 50, 60), k), k=1); d.text(cx + w / 2 - 70, cy + h / 2 - 80, "J", 70, A((200, 50, 60), k), k=1)
    cricket(d, cx + 10, cy - 120, 0.55, t, "happy", k)
    tag(d, cx, cy + 70, "一句话学会", GOLD, k, 30)
    d.text(cx, cy + 160, "长弯腿 = 洞顶抓手", 48, A((200, 50, 60), k), k=1)
    ek = popk(t, at("card", 1.5))
    if ek > 0: d.text(cx, cy + 240, "黑暗里倒挂也不掉", 34, A(NAVYT, ek), k=1)
def s_end(t, d):
    grad(d, (255, 150, 100), (120, 60, 110)); glow(d, 540, 900, 380, (255, 220, 140), 0.5)
    d.poly([(-20, 1300), (260, 700), (540, 620), (820, 700), (1100, 1300)], A((140, 100, 80), 1)); d.ell(540, 1080, 200, 220, A((30, 20, 20), 1))
    cricket(d, 540, 1060, 0.7, t, "happy", 1, wave_=1)
    stamp(d, t, T["end"] + 0.05, "炎魔？乖宝宝！", 540, 320, 100, YEL)
    ra = popk(t, at("end", 2))
    d.rect(170, 430, 910, 550, fill=A((20, 12, 30), 0.5 * ra), r=20)
    d.text(540, 468, "Journal of Orthoptera Research (2026)", 28, A(WHITE, 0.95 * ra))
    d.text(540, 510, "Kalaentzis 等 · 希腊 Kastellorizo 岛", 26, A(WHITE, 0.85 * ra), k=1)
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
    s = "Vibe 知识大赏 · 怪奇新发现"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)



SF = {n: globals()["s_" + n] for n in NAMES}
SECS = [(-1, HOOKCUT, s_hook), (HOOKCUT, T["tunnel"], s_island)] + [(T[n], nxt(n) if n != "dna" else SIL0, SF[n]) for n in NAMES[2:]]
SECS = [(a, (99 if n == len(SECS) - 1 else b), f) for n, (a, b, f) in enumerate(SECS)]
HITS = [T[n] for n in NAMES] + [at("island", 2.5), at("island", 3.5), at("tunnel", 1.2), at("tunnel", 4), at("reveal", 1.5), at("name", 0.5), at("name", 1.5),
        at("real", 3), at("legs", 0.8), at("legs", 2), at("grip", 4), at("genus", 4), at("fragile", 5), at("near", 0.5), at("near", 1), at("near", 3), at("card", 1.5)]
def cam(t):
    z = 1.0 + 0.04 * pulse(t, [HOOK_HIT, BIG2], 3)
    if T["dna"] <= t < SIL0: z += 0.03 * eio(pr(t, T["dna"], SIL0))
    if HOOK_STOP <= t < HOOKCUT: z += 0.05 * pr(t, HOOK_STOP, HOOKCUT)
    amp = 8 * pulse(t, [HOOK_HIT, BIG2], 5)
    sx, sy = shake(t, amp, 40)
    return z, 540 + sx, 900 + sy
def frame(t):
    img = Image.new("RGB", (W, H), (30, 20, 50)); d = D(img)
    if True:
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
        for ts in sys.argv[2:]: frame(float(ts)).save(f"/tmp/br_test_{float(ts):05.2f}.png")
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
