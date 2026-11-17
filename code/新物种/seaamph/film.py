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
ARM = (168, 140, 92); ARM_D = (128, 102, 66); ARM_L = (214, 190, 140); SKN = (120, 176, 150); SKN_D = (84, 136, 116)
GILL = (255, 120, 150); GILL_D = (220, 80, 120); FROG = (110, 200, 90); FROG_D = (70, 150, 66); FISH = (255, 150, 60)
SEA1 = (30, 120, 180); SEA2 = (8, 34, 80); SAND = (214, 190, 140); SAND_D = (180, 156, 110); ICH = (90, 110, 140)
def sea(d, t, top=SEA1, bot=SEA2, bed=1160, rays_=True):
    grad(d, top, bot)
    if rays_:
        for i in range(5):
            x = 120 + i * 220 + 40 * math.sin(t * 0.5 + i)
            d.poly([(x - 30, -20), (x + 30, -20), (x + 160, bed), (x + 40, bed)], A(WHITE, 0.05))
    for i in range(14):
        bx = (i * 167) % 1000 + 40; by = (bed - ((t * 90 + i * 211) % (bed - 200)))
        d.circ(bx + 8 * math.sin(t * 2 + i), by, 6 + i % 3 * 3, outline=A(WHITE, 0.35), w=3)
    d.rect(-20, bed, OW + 20, OH + 20, fill=A(SAND, 1)); d.rect(-20, bed, OW + 20, bed + 14, fill=A(SAND_D, 1))
    for i in range(10): d.ell(60 + i * 110, bed + 60 + (i % 3) * 40, 26, 8, A(SAND_D, 0.7))
def fish(d, x, y, s, t, a=1.0, flip=1, col=FISH, mood="ok"):
    w = 50 * s; h = 28 * s; wag = math.sin(t * 14) * 0.3
    d.poly([(x - flip * w * 0.8, y), (x - flip * w * 1.5, y - h * (0.9 + wag)), (x - flip * w * 1.5, y + h * (0.9 - wag))], A(mix(col, (0, 0, 0), 0.15), a))
    d.ell(x, y, w, h, A(col, a)); d.ell(x - flip * w * 0.1, y + h * 0.3, w * 0.6, h * 0.35, A(mix(col, WHITE, 0.4), a))
    d.circ(x + flip * w * 0.5, y - h * 0.2, h * 0.32, fill=A(WHITE, a)); d.circ(x + flip * w * 0.56, y - h * 0.2, h * 0.17 if mood != "shock" else h * 0.1, fill=A(INK, a))
def gerro(d, x, y, s, t, mood="happy", a=1.0, mo=0.0, armor=1.0, gill=0.6, look=(0.3, -0.6), sq=0.0):
    W_ = 250 * s * (1 + 0.08 * sq); H_ = 170 * s * (1 - 0.1 * sq)
    for sx, sy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        lx, ly = x + sx * W_ * 0.55, y + sy * H_ * 0.8
        d.ell(lx, ly, 34 * s, 22 * s, A(SKN_D, a))
        for j in range(3): d.circ(lx + sx * 20 * s + (j - 1) * 14 * s, ly + sy * 18 * s, 8 * s, fill=A(SKN_D, a))
    d.poly([(x - W_ * 0.9, y - 30 * s), (x - W_ * 1.55, y + 10 * s * math.sin(t * 3)), (x - W_ * 0.9, y + 40 * s)], A(SKN_D, a))
    d.ell(x, y, W_, H_, A(SKN, a))
    if armor > 0.01:
        d.ell(x, y, W_ * 0.98, H_ * 0.96, A(ARM, a * armor))
        for i in range(-3, 4):
            for j in range(-2, 3):
                px, py = x + i * 62 * s + (j % 2) * 31 * s - 40 * s, y + j * 52 * s
                if ((px - x) / W_) ** 2 + ((py - y) / H_) ** 2 < 0.78:
                    d.ell(px, py, 26 * s, 21 * s, A(ARM_L, a * armor)); d.ell(px, py + 4 * s, 20 * s, 12 * s, A(ARM_D, 0.25 * a * armor))
    # head (wide, flat) on the right
    hx = x + W_ * 0.62; hw = 150 * s; hh = 150 * s
    for k, sy in enumerate((-1, 1)):
        for j in range(3):
            fl = math.sin(t * 6 + j + k) * 10 * s * gill
            gx, gy = hx - hw * 0.45 - j * 26 * s, y + sy * (hh * 0.85 + 22 * s + fl)
            d.ell(gx, gy, 16 * s, 34 * s, A(GILL if j % 2 == 0 else GILL_D, a))
    d.ell(hx, y, hw, hh, A(SKN, a))
    if armor > 0.01: d.ell(hx - 6 * s, y, hw * 0.92, hh * 0.9, A(ARM, a * armor)); d.ell(hx - 30 * s, y - 40 * s, hw * 0.4, hh * 0.25, A(ARM_L, 0.7 * a * armor))
    if mo > 0.02:
        d.d.pieslice((P(hx + hw * 0.1 - hw * 0.9), P(y - hh * 0.95), P(hx + hw * 0.1 + hw * 0.9), P(y + hh * 0.95)), -35 * mo, 35 * mo, fill=A((70, 30, 50), a))
        d.d.pieslice((P(hx + hw * 0.1 - hw * 0.6), P(y - hh * 0.5), P(hx + hw * 0.1 + hw * 0.6), P(y + hh * 0.5)), -25 * mo, 25 * mo, fill=A((230, 110, 120), a))
    else:
        d.arc(hx + hw * 0.55, y, hw * 0.45, hh * 0.65, -70, 70, A((70, 40, 40), a), 6 * s)
    for sy in (-1, 1):
        ex, ey = hx + hw * 0.15, y + sy * hh * 0.42
        er = 30 * s
        d.circ(ex, ey, er * 1.15, fill=A(ARM_D if armor > 0.5 else SKN_D, a))
        if mood == "closed": d.line([(ex - er, ey), (ex + er, ey)], A(INK, a), 6 * s)
        elif mood == "happy": d.arc(ex, ey + er * 0.4, er * 0.8, er * 0.7, 200, 340, A(INK, a), 7 * s)
        else:
            d.circ(ex, ey, er, fill=A(WHITE, a)); pr_ = er * (0.35 if mood == "shock" else 0.5)
            d.circ(ex + look[0] * er * 0.4, ey + look[1] * er * 0.4, pr_, fill=A(INK, a)); d.circ(ex + look[0] * er * 0.4 - pr_ * 0.4, ey + look[1] * er * 0.4 - pr_ * 0.4, pr_ * 0.3, fill=A(WHITE, a))
    return hx + hw, y
def frog(d, x, y, s, t, a=1.0, dry=0.0, mood="happy"):
    col = mix(FROG, (150, 140, 90), dry); cd = mix(FROG_D, (110, 100, 70), dry)
    sx_ = 1 - 0.35 * dry; sy_ = 1 - 0.45 * dry
    for sd in (-1, 1): d.ell(x + sd * 120 * s * sx_, y + 70 * s, 70 * s * sx_, 40 * s, A(cd, a))
    d.ell(x, y, 170 * s * sx_, 130 * s * sy_, A(col, a))
    d.ell(x, y + 40 * s * sy_, 110 * s * sx_, 60 * s * sy_, A(mix(col, (255, 250, 210), 0.5), a))
    if dry > 0.2:
        for i in range(5): d.arc(x - 80 * s + i * 40 * s, y - 20 * s, 18 * s, 10 * s, 200, 340, A(cd, a * dry), 4 * s)
    for sd in (-1, 1):
        ex, ey = x + sd * 75 * s * sx_, y - 110 * s * sy_
        d.circ(ex, ey, 46 * s, fill=A(col, a)); d.circ(ex, ey, 32 * s, fill=A(WHITE, a))
        if mood == "dizzy":
            d.line([(ex - 16 * s, ey - 16 * s), (ex + 16 * s, ey + 16 * s)], A(INK, a), 6 * s); d.line([(ex - 16 * s, ey + 16 * s), (ex + 16 * s, ey - 16 * s)], A(INK, a), 6 * s)
        else: d.circ(ex, ey + 4 * s, 16 * s, fill=A(INK, a))
    if mood == "happy": d.arc(x, y - 30 * s, 60 * s, 30 * s, 20, 160, A(INK, a), 6 * s)
    else: d.ell(x, y - 20 * s, 22 * s, 14 * s, A(INK, a))
def ichthy(d, x, y, s, a=1.0, flip=-1, mo=0.0):
    d.ell(x, y, 220 * s, 70 * s, A(ICH, a))
    d.poly([(x - flip * 200 * s, y), (x - flip * 330 * s, y - 90 * s), (x - flip * 300 * s, y), (x - flip * 330 * s, y + 90 * s)], A(ICH, a))
    d.poly([(x + flip * 200 * s, y - 20 * s), (x + flip * 360 * s, y - 6 * s + 20 * s * mo), (x + flip * 200 * s, y + 24 * s)], A(ICH, a))
    d.poly([(x, y - 60 * s), (x - flip * 60 * s, y - 130 * s), (x - flip * 80 * s, y - 50 * s)], A(ICH, a))
    d.circ(x + flip * 160 * s, y - 20 * s, 18 * s, fill=A(WHITE, a)); d.circ(x + flip * 165 * s, y - 20 * s, 9 * s, fill=A(INK, a))
def salt(d, x, y, r, a=1.0):
    d.poly([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], A(WHITE, a)); d.poly([(x, y - r * 0.5), (x + r * 0.5, y), (x, y + r * 0.5), (x - r * 0.5, y)], A((210, 230, 255), a))

# ---------------- scenes ----------------
def s_hook(t, d):
    sea(d, t)
    frz = t >= HOOK_STOP; tt = min(t, HOOK_STOP)
    mo = ease(pr(tt, HOOK_HIT - 0.15, HOOK_HIT)) * (1 - pr(tt, HOOK_HIT + 0.3, HOOK_HIT + 0.7))
    if tt < HOOK_HIT + 0.05:
        u = pr(tt, -0.4, HOOK_HIT); fish(d, lerp(980, 820, u), 900, 1.4, tt, flip=-1, mood="shock")
    gerro(d, 470, 960, 1.15, tt, "shock" if frz else "open", mo=mo, look=(0.6, 0) if not frz else (0, -0.5))
    if HOOK_HIT <= tt < HOOK_HIT + 0.4:
        for i in range(12):
            u = pr(tt, HOOK_HIT, HOOK_HIT + 0.4); ang = i * 0.5
            d.line([(800 + 120 * math.cos(ang) * (1 - u), 900 + 120 * math.sin(ang) * (1 - u)), (730, 960)], A(WHITE, 0.6 * (1 - u)), 6)
    if t >= HOOK_HIT: sparks(d, 700, 900, t, HOOK_HIT, 40, 1000, (190, 240, 255), 1, 4, 0.9)
    kk = back(pr(t, -0.2, HOOK_HIT)); k2 = pulse(t, [HOOK_HIT], 6)
    if kk > 0: d.text(540, 330, "两栖动物下海了？", int(100 * (0.6 + 0.4 * kk) * (1 + 0.08 * k2)), A(YEL, 1), k=1)
    tag(d, 540, 460, "2.37亿年前 · 中国贵州", WHITE, popk(t, qb(1.5)), 34)
    if frz: glow(d, 540, 900, 160, WHITE, pr(t, HOOK_STOP, HOOKCUT))
def s_skin(t, d):
    u = t - T["skin"]
    wet = ease(pr(t, at("skin", 3), at("skin", 4)))
    grad(d, mix((140, 210, 120), SEA1, wet), mix((60, 140, 90), SEA2, wet))
    title(d, t, T["skin"], "两栖动物的皮肤", 300, 90)
    dry = ease(pr(t, at("skin", 4), at("skin", 6.5)))
    frog(d, 540, 860, 1.6, t, dry=dry, mood="dizzy" if dry > 0.5 else "happy")
    for i, (s, b) in enumerate((("呼吸", 1), ("喝水", 2))):
        k = popk(t, at("skin", b)); x = 300 + 480 * i
        tag(d, x, 560, s, WHITE, k, 38)
        if k > 0: arrow(d, x, 610, x + (120 if i == 0 else -120), 720, WHITE, k, 10)
    if wet > 0:
        for i in range(10):
            ang = i * 0.63; r = 330 - 60 * dry
            dx, dy = math.cos(ang + u) * r, math.sin(ang + u) * r * 0.8
            d.circ(540 + dx, 860 + dy, 14, fill=A((150, 210, 255), 0.8 * dry))
            salt(d, 540 + dx * 0.75, 860 + dy * 0.75, 12, wet * 0.9)
    if dry > 0.3: tag(d, 540, 1150, "脱水！", BAD, popk(t, at("skin", 5)), 46, WHITE)
def s_count(t, d):
    grad(d, (90, 160, 110), (40, 100, 80))
    d.rect(560, 520, 900, 1180, fill=A(SEA1, 1), r=30); d.rect(180, 520, 530, 1180, fill=A((110, 190, 120), 1), r=30)
    tag(d, 355, 560, "陆地 · 淡水", WHITE, 1, 30); tag(d, 730, 560, "大海", WHITE, 1, 30)
    n = int(96 * ease(pr(t, T["count"], at("count", 4))))
    for i in range(n):
        x = 215 + (i % 8) * 40; y = 630 + (i // 8) * 52
        d.ell(x, y, 15, 12, A(FROG if i % 3 else (240, 160, 70), 1)); d.circ(x - 6, y - 10, 5, fill=A(WHITE, 1)); d.circ(x + 6, y - 10, 5, fill=A(WHITE, 1))
    k = popk(t, at("count", 0.5))
    if k > 0: d.text(540, 330, "8000+", int(160 * k), A(YEL, 1), k=1)
    z = popk(t, at("count", 4))
    if z > 0: d.text(730, 850, "0", int(300 * z), A(WHITE, z), k=1)
    tag(d, 730, 1100, "完全住海里的", GOOD, popk(t, at("count", 4.5)), 30, WHITE)
def s_find(t, d):
    grad(d, (230, 180, 120), (180, 120, 80))
    title(d, t, T["find"], "中国贵州", 300, 110, (120, 40, 30))
    k = ease(pr(t, at("find", 0.5), at("find", 3)))
    d.rect(170, 560, 910, 1110, fill=A((150, 140, 130), 1), r=40)
    for i in range(30): d.ell(200 + (i * 137) % 680, 590 + (i * 89) % 500, 20, 8, A((120, 112, 104), 0.6))
    for j, (cx, cy, sc) in enumerate(((430, 720, 0.75), (620, 980, 0.7))):
        kk = ease(pr(t, at("find", 0.8 + j), at("find", 2.5 + j)))
        if kk <= 0: continue
        for i in range(12):
            d.line([(cx - 220 * sc + i * 36 * sc, cy - 50 * sc), (cx - 220 * sc + i * 36 * sc, cy + 50 * sc)], A(BONE, kk), 8 * sc)
        d.line([(cx - 240 * sc, cy), (cx + 240 * sc, cy)], A(BONE, kk), 14 * sc); d.ell(cx + 270 * sc, cy, 90 * sc, 80 * sc, A(BONE, kk)); d.ell(cx + 270 * sc, cy, 60 * sc, 50 * sc, A((150, 140, 130), kk))
    tag(d, 540, 470, "两具几乎完整的骨架", WHITE, popk(t, at("find", 1)), 34)
    yk = popk(t, at("find", 3))
    if yk > 0: d.text(540, 1170, "2.37亿年前", int(70 * yk), A(YEL, 1), k=1)
def s_q(t, d):
    sea(d, t, (24, 80, 140), (6, 20, 50))
    gerro(d, 470, 980, 1.0, t, "open", look=(-0.3, -0.8))
    for i in range(3): fish(d, (t * 160 + i * 330) % 1200 - 60, 600 + i * 90, 0.8, t, 0.9)
    q = popk(t, T["q"] + 0.2)
    if q > 0: d.text(760, 700, "？", int(240 * (1 + 0.06 * math.sin(t * 8))), A(YEL, q), k=1)
    title(d, t, T["q"], "凭什么？", 300, 120)
def s_reveal(t, d):
    rays(d, t, (255, 200, 80), (230, 140, 50))
    ar = ease(pr(t, BIG2 - 0.05, BIG2 + 0.25))
    gerro(d, 470, 940, 1.2, t, "happy" if t > at("reveal", 1.5) else "shock", armor=ar)
    if t >= BIG2:
        sparks(d, 540, 940, t, BIG2, 60, 1300, YEL, 1, 3, 1.2)
        u = pr(t, at("reveal", 1), at("reveal", 3))
        if 0 < u < 1:
            ix = lerp(1250, 900, ease(u * 2)) if u < 0.5 else lerp(900, 1300, ease((u - 0.5) * 2))
            ichthy(d, ix, 760, 0.8, 1, -1, 1 if u < 0.5 else 0)
            if 0.45 < u < 0.6: star(d, 760, 820, 60, WHITE, 1)
    stamp(d, t, BIG2, "骨头盔甲", 540, 330, 140, (200, 40, 60))
    tag(d, 540, 470, "还能防鱼龙咬", WHITE, popk(t, at("reveal", 2)), 34)
def s_armor(t, d):
    sea(d, t, (40, 130, 190), (10, 40, 90), bed=1200)
    title(d, t, T["armor"], "盔甲 = 防水外套", 300, 92)
    tag(d, 540, 420, "科学家推测", (255, 220, 120), popk(t, T["armor"] + 0.1), 30)
    hx, hy = gerro(d, 420, 900, 1.05, t, "happy", mo=0.5 * ease(pr(t, at("armor", 4), at("armor", 4.5))))
    for i in range(9):
        ph_ = (t * 1.3 + i * 0.37) % 1
        x = 160 + i * 60; y = 560 + ph_ * 220
        if ph_ < 0.8: d.circ(x, y, 12, fill=A((170, 220, 255), 0.9))
        else: d.circ(x, y - (ph_ - 0.8) * 300, 12, fill=A((170, 220, 255), 0.9 * (1 - (ph_ - 0.8) * 5)))
    tag(d, 330, 520 + 20, "皮肤不进水", WHITE, popk(t, at("armor", 1.5)), 30)
    k = popk(t, at("armor", 4))
    if k > 0:
        for i in range(4):
            ph_ = (t * 1.5 + i * 0.25) % 1
            d.circ(lerp(960, hx - 40, ph_), 900 + 20 * math.sin(ph_ * 6), 12, fill=A((170, 220, 255), k))
        tag(d, 830, 760, "用嘴喝", WHITE, k, 34)
def s_gill(t, d):
    sea(d, t, (60, 150, 200), (14, 50, 100), bed=1250)
    title(d, t, T["gill"], "鳃：滤盐", 300, 110)
    gerro(d, 470, 880, 1.3, t, "happy", gill=2.0)
    k = popk(t, at("gill", 1))
    if k > 0:
        for i in range(8):
            ph_ = (t * 0.9 + i / 8) % 1
            x = 420 + ph_ * 360; y = 880 + (1 if i % 2 else -1) * (220 + ph_ * 160)
            salt(d, x, y, 14, k * (1 - ph_))
        tag(d, 760, 560, "盐被排出", WHITE, k, 34)
def s_body(t, d):
    sea(d, t, (40, 130, 190), (10, 40, 90))
    gerro(d, 500, 860, 1.25, t, "happy", sq=0.3 * math.sin((t - T["body"]) * 4))
    k = ease(pr(t, at("body", 0.5), at("body", 2)))
    x0, x1 = 120, lerp(120, 960, k)
    d.rect(x0, 1080, x1, 1130, fill=A(YEL, 1), r=8)
    for i in range(int((x1 - x0) / 42)): d.line([(x0 + i * 42, 1080), (x0 + i * 42, 1100 if i % 5 else 1120)], A(NAVYT, 1), 4)
    stamp(d, t, at("body", 2), "近 1 米", 540, 330, 120, YEL)
    tag(d, 540, 470, "像个大圆盘", WHITE, popk(t, at("body", 4)), 36)
def s_suck(t, d):
    sea(d, t, (20, 90, 150), (5, 25, 60))
    title(d, t, T["suck"], "海底吸尘器", 300, 100)
    tag(d, 540, 420, "科学家推测", (255, 220, 120), popk(t, T["suck"] + 0.1), 30)
    hit = at("suck", 4)
    mo = ease(pr(t, hit - 0.15, hit)) * (1 - pr(t, hit + 0.4, hit + 0.8))
    hx, hy = gerro(d, 380, 1010, 1.0, t, "closed" if t < at("suck", 3) else "open", mo=mo, look=(0.7, -0.5))
    if t < hit + 0.08:
        u = pr(t, hit - 0.05, hit + 0.08)
        fx_ = lerp(830 + 40 * math.sin(t * 2), hx - 40, ease(u)); fy = lerp(780, hy, ease(u))
        fish(d, fx_, fy, 1.1 * (1 - 0.7 * u), t, flip=-1, mood="shock" if t > hit - 0.6 else "ok")
    if hit <= t < hit + 0.4:
        for i in range(10):
            uu = pr(t, hit, hit + 0.4); ang = i * 0.6
            d.line([(hx + 140 * math.cos(ang) * (1 - uu) + 80, hy + 140 * math.sin(ang) * (1 - uu)), (hx, hy)], A(WHITE, 0.7 * (1 - uu)), 6)
    k = popk(t, hit)
    if k > 0: d.text(800, 700, "嗖！", int(120 * k), A(YEL, 1), k=1)
def s_proof(t, d):
    grad(d, (60, 60, 90), (30, 30, 50))
    title(d, t, T["proof"], "证据一：手指骨", 300, 96)
    k = popk(t, at("proof", 0.5))
    d.rect(150, 560, 930, 1150, fill=A((150, 140, 130), k), r=40)
    if k > 0:
        cx, cy = 540, 900
        for i, ang in enumerate((-0.7, -0.25, 0.2, 0.65)):
            for j in range(3):
                r0 = 90 + j * 70
                d.line([(cx + math.sin(ang) * r0, cy - math.cos(ang) * r0), (cx + math.sin(ang) * (r0 + 55), cy - math.cos(ang) * (r0 + 55))], A(BONE, k), 22)
                d.circ(cx + math.sin(ang) * r0, cy - math.cos(ang) * r0, 14, fill=A(BONE, k))
        d.ell(cx, cy + 40, 90, 70, A(BONE, k))
        g = popk(t, at("proof", 3))
        glow(d, cx, cy - 150, 260, (255, 240, 160), 0.4 * g)
        tag(d, 540, 1240 - 30, "一根都没丢", GOOD, g, 36, WHITE)
def s_death(t, d):
    sea(d, t, (30, 110, 170), (6, 26, 60))
    title(d, t, T["death"], "死在家门口", 300, 100)
    u = pr(t, T["death"], nxt("death"))
    # floating carcass drifting away (X)
    k1 = popk(t, at("death", 0.5))
    if k1 > 0:
        d.ell(400 + 120 * u, 580 + 10 * math.sin(t * 2), 90, 40, A((150, 160, 150), 0.8 * k1))
        tag(d, 420, 680, "漂远：会掉手脚", (120, 120, 150), k1, 28, WHITE)
        cross(d, 560, 580, 50, ease(pr(t, at("death", 1), at("death", 1.4))), BAD)
    k2 = popk(t, at("death", 3))
    if k2 > 0:
        gerro(d, 600, 1060, 0.7, t, "closed", a=k2, gill=0)
        tag(d, 600, 1170, "原地沉底：完整", GOOD, k2, 28, WHITE)
        check(d, 850, 940, 50, ease(pr(t, at("death", 3.5), at("death", 4))), GOOD)
def s_sr(t, d):
    grad(d, (70, 50, 130), (30, 20, 70))
    title(d, t, T["sr"], "证据二：锶同位素", 300, 90)
    x0, y0, x1, y1 = 180, 580, 900, 1120
    d.rect(x0, y0, x1, y1, fill=A((20, 14, 40), 0.6), r=24)
    k = ease(pr(t, at("sr", 0.5), at("sr", 2.5)))
    pts = [(x0 + 30 + i * 22, 850 + 60 * math.sin(i * 0.3)) for i in range(int(31 * k) + 1)]
    if len(pts) > 1: d.line(pts, A((120, 200, 255), 1), 8)
    tag(d, 380, 640, "三叠纪海水", (120, 200, 255), popk(t, at("sr", 1)), 28, WHITE)
    kb = popk(t, at("sr", 3))
    if kb > 0:
        bx = x0 + 30 + 20 * 22; by = 850 + 60 * math.sin(20 * 0.3)
        d.circ(bx, by, 26 * kb, fill=A(YEL, 1)); glow(d, bx, by, 90, YEL, 0.5 * kb)
        tag(d, bx, by + 90, "化石的骨头", YEL, kb, 28)
        check(d, 780, 1000, 50, ease(pr(t, at("sr", 4), at("sr", 4.5))), GOOD)
def s_card(t, d):
    grad(d, (30, 90, 70), (12, 50, 40))
    for i in range(12): d.circ(540, 900, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1)
    if k <= 0: return
    rot = 0.04 * math.sin(t * 2)
    w, h = 560 * (0.7 + 0.3 * k), 820 * (0.7 + 0.3 * k); cx, cy = 540, 880
    d.rect(cx - w / 2 + 14, cy - h / 2 + 18, cx + w / 2 + 14, cy + h / 2 + 18, fill=A((0, 0, 0), 0.3 * k), r=36)
    d.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=A((250, 244, 230), k), r=36)
    d.rect(cx - w / 2 + 24, cy - h / 2 + 24, cx + w / 2 - 24, cy + h / 2 - 24, outline=A((200, 50, 60), k), w=6, r=24)
    d.text(cx - w / 2 + 70, cy - h / 2 + 80, "A", 70, A((200, 50, 60), k), k=1); d.text(cx + w / 2 - 70, cy + h / 2 - 80, "A", 70, A((200, 50, 60), k), k=1)
    gerro(d, cx - 30, cy - 120, 0.62, t, "happy", a=k)
    tag(d, cx, cy + 70, "一句话学会", GOLD, k, 30)
    d.text(cx, cy + 160, "盔甲 = 防水外套", 50, A((200, 50, 60), k), k=1)
    ek = popk(t, at("card", 1.5))
    if ek > 0: d.text(cx, cy + 240, "皮肤不吸水，才敢下海", 34, A(NAVYT, ek), k=1)
def s_end(t, d):
    sea(d, t, (255, 150, 110), (40, 60, 120))
    gerro(d, 470, 1000, 1.0, t, "happy", sq=0.2 * math.sin(t * 3))
    for i in range(3): fish(d, (t * 120 + i * 360) % 1200 - 60, 700 + i * 70, 0.7, t, 0.8)
    stamp(d, t, T["end"] + 0.05, "海里的第一只", 540, 320, 110, YEL)
    ra = popk(t, at("end", 2))
    d.rect(170, 430, 910, 550, fill=A((20, 12, 30), 0.5 * ra), r=20)
    d.text(540, 468, "Nature Ecology & Evolution (2026)", 28, A(WHITE, 0.95 * ra))
    d.text(540, 510, "UC Davis 新闻稿 2026-11-02 · Motani 等", 26, A(WHITE, 0.85 * ra), k=1)
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
SECS = [(-1, HOOKCUT, s_hook), (HOOKCUT, T["count"], s_skin)] + [(T[n], nxt(n) if n != "q" else SIL0, SF[n]) for n in NAMES[2:]]
SECS = [(a, (99 if n == len(SECS) - 1 else b), f) for n, (a, b, f) in enumerate(SECS)]
HITS = [T[n] for n in NAMES] + [at("skin", 1), at("skin", 2), at("skin", 5), at("count", 0.5), at("count", 4), at("find", 1), at("find", 3),
        at("reveal", 2), at("armor", 1.5), at("armor", 4), at("gill", 1), at("body", 2), at("body", 4), at("suck", 4), at("proof", 0.5), at("proof", 3),
        at("death", 0.5), at("death", 3), at("sr", 1), at("sr", 3), at("card", 1.5)]

def cam(t):
    z = 1.0 + 0.04 * pulse(t, [HOOK_HIT, BIG2], 3)
    if T["q"] <= t < SIL0: z += 0.03 * eio(pr(t, T["q"], SIL0))
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
        for ts in sys.argv[2:]: frame(float(ts)).save(f"/tmp/sa_test_{float(ts):05.2f}.png")
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
