import math, random, sys, subprocess
from PIL import Image
from base import *
from fx import glow, sparks, shake, stamp, flash, grad, rays, vignette, bignum
from cues import *

OL = (22, 30, 26)
POT = (226, 112, 70); POT_D = (176, 76, 48); POT_L = (246, 150, 104)
LF = (110, 205, 96); LF_D = (60, 150, 70); LF_L = (170, 235, 130); STEM = (70, 140, 70)
PINK = (255, 120, 190); PINK_L = (255, 190, 225); MINT = (120, 240, 200); WARN = (255, 80, 70)
FOAM = (255, 150, 190)

def rpoly(cx, cy, rx, ry, ang, n=14):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + rx * math.cos(2 * math.pi * k / n) * ca - ry * math.sin(2 * math.pi * k / n) * sa,
             cy + rx * math.cos(2 * math.pi * k / n) * sa + ry * math.sin(2 * math.pi * k / n) * ca) for k in range(n)]

def oline(d, pts, ol, col):
    d.line(pts + [pts[0]], OL, 2 * ol); d.poly(pts, col)

def pinna(d, x, y, ang, L, fold, s, a=1.0):
    """compound leaf: rachis from (x,y) at angle ang, leaflet pairs fold up along rachis."""
    ex, ey = x + math.cos(ang) * L, y + math.sin(ang) * L
    d.line([(x, y), (ex, ey)], A(OL, a), 0.075 * s); d.line([(x, y), (ex, ey)], A(STEM, a), 0.04 * s)
    n = 8
    for i in range(n):
        u = 0.18 + 0.8 * i / (n - 1)
        px, py = x + math.cos(ang) * L * u, y + math.sin(ang) * L * u
        lw = 0.16 * s * (1 - 0.35 * abs(u - 0.55))
        for side in (-1, 1):
            # open: perpendicular to rachis; closed: folded forward along rachis, overlapping
            th = ang + side * lerp(math.pi / 2 * 0.92, 0.18, fold)
            off = lw * lerp(1.0, 0.35, fold)
            cx, cy = px + math.cos(th) * off, py + math.sin(th) * off
            pts = rpoly(cx, cy, lw, lw * 0.32, th)
            d.poly(rpoly(cx, cy, lw + 0.025 * s, lw * 0.32 + 0.025 * s, th), A(OL, a))
            d.poly(pts, A(mix(LF, LF_D, fold * 0.5) if side < 0 else mix(LF_L, LF, fold * 0.5), a))

def eye(d, x, y, r, kind, a, look=0.0):
    if kind == "proud":
        d.arc(x, y + r * 0.3, r * 0.9, r * 0.8, 200, 340, A(OL, a), r * 0.42); return
    if kind == "closed":
        d.arc(x, y - r * 0.2, r * 0.9, r * 0.6, 20, 160, A(OL, a), r * 0.38); return
    big = 1.3 if kind in ("shock", "scared") else 1.0
    rx, ry = r * 0.95 * big, r * 1.15 * big
    d.ell(x, y, rx + 4, ry + 4, A(OL, a)); d.ell(x, y, rx, ry, A(WHITE, a))
    pr_ = r * (0.36 if kind in ("shock", "scared") else 0.56)
    px = x + look * r * 0.35
    d.circ(px, y + r * 0.1, pr_, fill=A(OL, a)); d.circ(px - pr_ * .35, y - pr_ * .3, pr_ * .38, fill=A(WHITE, a))
    if kind in ("bored", "meh"):  # heavy lids
        lid = 0.55 if kind == "bored" else 0.3
        d.rect(x - rx - 5, y - ry - 5, x + rx + 5, y - ry + 2 * ry * lid, fill=A(POT, a))
        d.line([(x - rx, y - ry + 2 * ry * lid), (x + rx, y - ry + 2 * ry * lid)], A(OL, a), r * 0.28)
    if kind == "angry":
        return

def brow(d, x, y, r, s_, kind, a):
    if kind == "angry": d.line([(x - r * 1.1 * s_, y - r * 1.75), (x + r * 1.0 * s_, y - r * 1.1)], A(OL, a), r * 0.32)
    if kind == "sus" and s_ < 0: d.line([(x - r, y - r * 1.5), (x + r, y - r * 1.2)], A(OL, a), r * 0.3)

def mimosa(d, x, y, s, t, fold=0.0, kind="chill", a=1.0, look=0.0, squash=0.0, flower=True):
    """x,y = pot bottom center. s ~ pot height."""
    sq = 1 + squash * 0.18; st = 1 - squash * 0.15
    ph, pw, pb = s * st, 0.62 * s * sq, 0.46 * s * sq
    top = y - ph
    d.ell(x, y + 0.04 * s, 0.7 * s * sq, 0.1 * s, A((0, 0, 0), 0.3 * a))
    # stem + leaves (behind rim)
    sway = 0.04 * math.sin(t * 2.2)
    droop = fold * 0.55
    sx, sy = x + sway * s, top - 1.05 * s * (1 - 0.12 * fold)
    d.line([(x, top), (lerp(x, sx, 0.5), top - 0.55 * s), (sx, sy)], A(OL, a), 0.12 * s)
    d.line([(x, top), (lerp(x, sx, 0.5), top - 0.55 * s), (sx, sy)], A(STEM, a), 0.07 * s)
    for side in (-1, 1):
        bx, by = lerp(x, sx, 0.55), lerp(top, sy, 0.55)
        base_ang = -math.pi / 2 + side * (0.95 + droop)
        for j, (dang, L) in enumerate(((-0.25, 0.85), (0.25, 0.8))):
            pinna(d, bx, by, base_ang + side * dang + side * 0.15 * j, L * s, fold, s, a)
        base2 = -math.pi / 2 + side * (0.45 + droop * 0.8)
        pinna(d, sx, sy, base2, 0.75 * s, fold, s, a)
    if flower:
        fr = 0.2 * s
        for k in range(18):
            ang = k * math.pi * 2 / 18 + t * 0.4
            d.line([(sx, sy - fr * 0.6), (sx + math.cos(ang) * fr * 1.3, sy - fr * 0.6 + math.sin(ang) * fr * 1.3)], A(PINK, a), 0.03 * s)
        d.circ(sx, sy - fr * 0.6, fr * 0.55, fill=A(PINK_L, a))
    # pot
    pts = [(x - pw, top + 0.18 * s), (x + pw, top + 0.18 * s), (x + pb, y), (x - pb, y)]
    oline(d, pts, 0.035 * s, A(POT, a))
    d.rect(x - pw - 0.08 * s - 0.035 * s, top - 0.035 * s, x + pw + 0.08 * s + 0.035 * s, top + 0.2 * s + 0.035 * s, fill=A(OL, a), r=0.06 * s)
    d.rect(x - pw - 0.08 * s, top, x + pw + 0.08 * s, top + 0.2 * s, fill=A(POT_L, a), r=0.05 * s)
    d.poly([(x - pw * 0.8, top + 0.26 * s), (x - pw * 0.6, top + 0.26 * s), (x - pb * 0.7, y - 0.08 * s), (x - pb * 0.85, y - 0.08 * s)], A(WHITE, 0.18 * a))
    # face
    fy = top + 0.5 * s; er = 0.12 * s
    for s_ in (-1, 1):
        ex = x + s_ * 0.24 * s
        eye(d, ex, fy, er, kind, a, look); brow(d, ex, fy, er, s_, kind, a)
    my = fy + 0.24 * s
    if kind in ("shock", "scared"):
        d.ell(x, my, 0.08 * s, 0.1 * s, A(OL, a)); d.ell(x, my + 0.04 * s, 0.045 * s, 0.03 * s, A(TONGUE, a))
    elif kind in ("proud", "chill", "closed"):
        d.arc(x, my - 0.06 * s, 0.12 * s, 0.08 * s, 20, 160, A(OL, a), 0.03 * s)
    elif kind == "bored":
        d.line([(x - 0.08 * s, my), (x + 0.08 * s, my)], A(OL, a), 0.03 * s)
    elif kind == "angry":
        d.arc(x, my + 0.04 * s, 0.1 * s, 0.06 * s, 200, 340, A(OL, a), 0.03 * s)
    else:
        d.line([(x - 0.07 * s, my + 0.01 * s), (x + 0.07 * s, my - 0.01 * s)], A(OL, a), 0.03 * s)
    for s_ in (-1, 1): d.ell(x + s_ * 0.38 * s, fy + 0.15 * s, 0.07 * s, 0.04 * s, A((255, 110, 120), 0.6 * a))
    if kind in ("scared", "shock"):
        d.ell(x + 0.55 * s, top + 0.3 * s, 0.035 * s, 0.06 * s, A(CYAN, a))

# ---------------- helpers ----------------
DROPS = SLOW + FAST + [BURST]
def count_at(t):
    n = sum(1 for h in SLOW if h <= t)
    if t >= FAST0: n = 6 + int(round(53 * pr(t, FAST0, FAST1))) if t < BURST else 60
    return n
def resp(k): return 1.0 if k <= 3 else max(0.0, 1 - (k - 3) / 10)
def kind_for(k):
    if k <= 3: return "scared"
    if k <= 8: return "angry"
    if k <= 20: return "sus"
    return "bored"
def drop_pos(t, hits, fall=0.13):
    """0 = up, 1 = landed."""
    prev = [h for h in hits if h <= t]; nxt = [h for h in hits if h > t]
    if nxt and t >= nxt[0] - fall: return ((t - (nxt[0] - fall)) / fall) ** 2
    if not prev: return 0.0
    h = prev[-1]; gap = (nxt[0] - h) if nxt else 1.0
    return 1 - eio(pr(t, h + 0.06, h + 0.06 + max(0.05, gap - fall - 0.1)))
def fold_from(t, hits, ks):
    v = 0.0
    for h, k in zip(hits, ks):
        if h <= t < h + 3.0:
            r = resp(k); u = t - h
            v = max(v, r * ease(pr(u, 0, 0.12)) * (1 - eio(pr(u, 0.5, 2.2))))
    return v

def grad_bg(d, top, bot): grad(d, top, bot)
def leaves_bg(d, t, col=(20, 70, 56), a=0.5):
    for i in range(14):
        x = (i * 173) % 1080; y = 300 + (i * 271) % 1300
        d.poly(rpoly(x + 10 * math.sin(t + i), y, 90, 30, i * 0.7 + 0.1 * math.sin(t * 0.8 + i)), A(col, a))
def rig(d, x, y0, y1, a=1.0):
    for s_ in (-1, 1):
        d.rect(x + s_ * 260 - 14, y0, x + s_ * 260 + 14, y1 + 40, fill=A((150, 165, 180), a), r=8)
    d.rect(x - 300, y1 + 30, x + 300, y1 + 110, fill=A(FOAM, a), r=24)
    d.rect(x - 300, y1 + 30, x + 300, y1 + 110, outline=A(OL, a), w=6, r=24)
    for k in range(5): d.text(x + 280 + 40, y1 - k * 40, "-" if k % 2 else "—", 26, A(WHITE, 0.5 * a))

# ---------------- scenes ----------------
def w_hook(t, d):
    grad(d, (18, 60, 50), (6, 20, 18))
    rays(d, t, (30, 100, 80), (10, 40, 32), 20, 540, 1200)
    p = drop_pos(t, [HOOK_DROP])
    y = 1560 - 120 * (1 - p) if t < HOOK_DROP else 1560
    sq = pulse(t, [HOOK_DROP], 9)
    fold = ease(pr(t, HOOK_DROP, HOOK_DROP + 0.12)) * (1 - eio(pr(t, 1.6, 2.5)))
    mimosa(d, 540, y, 290, t, fold, "scared" if t < 1.6 else "proud", squash=sq)
    sparks(d, 540, 1560, t, HOOK_DROP, 50, 1300, MINT, 1, 3, 0.9)
def u_hook(t, d):
    k = back(pr(t, -0.12, 0.18))
    d.text(540, 300, "含羞草", int(120 * (0.85 + 0.15 * k)), A(WHITE, 1), k=1)
    s = int(250 * (0.85 + 0.15 * k) * (1 + 0.06 * pulse(t, [HOOK_DROP, 1.0], 8)))
    d.text(552, 512, "记28天", s, A(OL, 1), k=1); d.text(540, 500, "记28天", s, A(YEL, 1), k=1)
    a_ = ease(pr(t, 0.9, 1.2)); d.rect(330, 615, 750, 705, fill=A((0, 0, 0), 0.55 * a_), r=40); d.text(540, 660, "它没有大脑", 60, A(MINT, a_), k=1)
    flash(d, t, [HOOK_DROP], WHITE, 0.9)

def w_touch(t, d):
    grad(d, (130, 200, 230), (200, 236, 210)) if t < SUNLOSS else grad(d, (60, 80, 110), (90, 110, 100))
    # sun
    sa = 1 - 0.75 * ease(pr(t, SUNLOSS, SUNLOSS + 0.4))
    glow(d, 880, 700, 200, YEL, sa); d.circ(880, 700, 90, fill=A(mix((255, 214, 64), (150, 150, 120), 1 - sa), 1))
    d.rect(0, 1500, 1080, 1920, fill=A((90, 150, 80), 1))
    fold = ease(pr(t, POKE, POKE + 0.15)) * (1 - eio(pr(t, 7.4, 8.4)))
    kind = "chill" if t < POKE else ("shock" if t < POKE + 1.2 else ("closed" if t < SUNLOSS else "sad"))
    mimosa(d, 540, 1520, 290, t, fold, kind)
    # finger
    if t < POKE + 0.8:
        u = ease(pr(t, 3.0, POKE)); back_ = ease(pr(t, POKE + 0.2, POKE + 0.8))
        fx, fy = lerp(1150, 800, u) + 300 * back_, lerp(700, 860, u)
        d.d.line([(P(fx), P(fy)), (P(fx + 400), P(fy - 120))], fill=A(OL, 1), width=int(P(110)))
        d.line([(fx, fy), (fx + 400, fy - 120)], A((250, 205, 170), 1), 90); d.ell(fx + 6, fy - 4, 22, 16, A((255, 230, 220), 1))
    if t >= SUNLOSS:  # energy bar draining
        e = 1 - 0.6 * ease(pr(t, SUNLOSS + 0.2, SUNLOSS + 1.6))
        d.rect(200, 760, 880, 830, fill=A((0, 0, 0), 0.5), r=30); d.rect(206, 766, 206 + 668 * e, 824, fill=A(WARN if e < 0.6 else YEL, 1), r=26)
def u_touch(t, d):
    if t < SUNLOSS:
        k = back(pr(t, POKE, POKE + 0.2))
        if t > POKE: d.text(540, 420, "啪！合上", int(140 * k) + 1, A(OL, 1), k=1)
        else: d.text(540, 420, "碰一下", 110, A(OL, ease(pr(t, 2.6, 2.9))), k=1)
    else:
        d.text(540, 420, "合上 = 饿肚子", int(110 * back(pr(t, SUNLOSS, SUNLOSS + 0.2))) + 1, A(WHITE, 1), k=1)
        d.text(540, 680, "光合作用 ↓", 60, A(WARN, ease(pr(t, SUNLOSS + 0.4, SUNLOSS + 0.7))), k=1)
    flash(d, t, [POKE], WHITE, 0.45)

def w_drop(t, d):
    grad(d, (16, 40, 46), (6, 14, 18)); leaves_bg(d, t, (24, 70, 70), 0.35)
    fastk = pr(t, FAST0, FAST0 + 0.3) * (1 - pr(t, FAST1, FAST1 + 0.3))
    hits = SLOW + FAST
    ks = list(range(1, 7)) + [6 + int(round(53 * pr(h, FAST0, FAST1))) for h in FAST]
    p = drop_pos(t, hits, 0.13 if t < FAST0 else 0.06)
    y = 1470 - 150 * (1 - p)
    k = count_at(t)
    rig(d, 540, 980, 1470)
    sq = pulse(t, hits, 10)
    mimosa(d, 540, y, 235, t, fold_from(t, hits, ks), kind_for(max(k, 1)), squash=sq, look=0.6 * math.sin(t * 3))
    if fastk > 0:
        for i in range(8):
            yy = (t * 2400 + i * 260) % 1800
            d.rect(60 + i * 130, yy, 66 + i * 130, yy + 140, fill=A(WHITE, 0.12 * fastk))
def u_drop(t, d):
    k = count_at(t)
    if t < SLOW[0]:
        d.text(540, 330, "掉落实验", int(110 * back(pr(t, MACH, MACH + 0.25))), A(WHITE, 1), k=1)
        d.text(540, 470, "15 厘米", 80, A(MINT, ease(pr(t, MACH + 0.3, MACH + 0.6))), k=1)
    else:
        bignum(d, t, f"{k}次", max([h for h in SLOW + FAST if h <= t] + [SLOW[0]]) - 0.06, 400, YEL if k < 20 else (MINT if k < 59 else WARN), 1, 250)
        d.text(540, 240, "已经摔了", 56, A(WHITE, 0.9), k=1)
    if FAST0 <= t < FAST1 + 0.3:
        a = 0.6 + 0.4 * math.sin(t * 14)
        d.rect(780, 620, 1000, 690, fill=A(WARN, a), r=20); d.text(890, 655, "快进 ▶▶", 40, A(WHITE, 1), k=1)
    if t >= RISER[0]:
        d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.5 * pr(t, RISER[0], SILENCE[1])))

def w_learn(t, d):
    rays(d, t, (40, 140, 110), (10, 50, 40), 22, 540, 1200)
    if t < SHAKE:
        p = drop_pos(t, [BURST]); y = 1470
        rig(d, 540, 980, 1470)
        mimosa(d, 540, y, 240, t, 0.0, "proud" if t > BURST + 0.4 else "bored", squash=pulse(t, [BURST], 9))
        sparks(d, 540, 1350, t, BURST, 90, 1700, YEL, 1, 5, 1.3)
        for i in range(4):
            kk = back(pr(t, BURST + 0.8 + i * 0.25, BURST + 1.0 + i * 0.25))
            d.text(200 + (i % 2) * 680, 950 + (i // 2) * 240, "✓", int(110 * kk) + 1, A(MINT, 1), k=1)
    else:
        grad(d, (40, 30, 60), (12, 8, 20))
        sx = math.sin((t - SHAKE) * 40) * 60 * (1 - pr(t, SHAKE + 0.6, SHAKE + 0.9)) if t < SHAKE + 0.9 else 0
        fold = ease(pr(t, SHAKE + 0.1, SHAKE + 0.25))
        mimosa(d, 540 + sx, 1470, 250, t, fold, "shock" if t < NOTTIRED else "closed")
        if t < SHAKE + 0.9:
            for s_ in (-1, 1): d.text(540 + s_ * 380, 1100, "~", 160, A(WHITE, 0.8), k=1)
def u_learn(t, d):
    if t < SHAKE:
        k = back(pr(t, BURST, BURST + 0.2))
        s = int(170 * k) + 1
        d.text(552, 412, "它不合了！", s, A(OL, 1), k=1); d.text(540, 400, "它不合了！", s, A(YEL, 1), k=1)
        d.rect(170, 560, 910, 680, fill=A((0, 0, 0), 0.55 * ease(pr(t, BURST + 1.0, BURST + 1.3))), r=40)
        d.text(540, 620, "掉下来 = 没事", 76, A(MINT, ease(pr(t, BURST + 1.0, BURST + 1.3))), k=1)
    else:
        d.text(540, 380, "累了吗？", 90, A(WHITE, ease(pr(t, SHAKE, SHAKE + 0.2))), k=1)
        if t > NOTTIRED: stamp(d, t, NOTTIRED, "是学会了", 540, 560, 150, MINT)
    flash(d, t, [BURST], WHITE, 0.95); flash(d, t, [SHAKE + 0.1], WHITE, 0.35)

def w_mem(t, d):
    if t < DAY28 - 0.3:
        grad(d, (20, 26, 50), (6, 8, 18))
        day = 1 + int(27 * eio(pr(t, CAL0 + 0.6, CAL1)))
        night = 0.5 + 0.5 * math.sin((t - CAL0) * 12)
        d.rect(0, 0, OW, OH, fill=A((255, 220, 140), 0.08 * night))
        mimosa(d, 540, 1500, 220, t, 0.0, "closed")
        cx, cy = 540, 820
        draw_card = [(cx - 220, cy - 240), (cx + 220, cy - 240), (cx + 220, cy + 240), (cx - 220, cy + 240)]
        d.poly([(x + 10, y + 10) for x, y in draw_card], A((0, 0, 0), 0.4))
        d.rect(cx - 220, cy - 240, cx + 220, cy + 240, fill=A(WHITE, 1), r=30)
        d.rect(cx - 220, cy - 240, cx + 220, cy - 120, fill=A(WARN, 1), r=30); d.rect(cx - 220, cy - 160, cx + 220, cy - 120, fill=A(WARN, 1))
        d.text(cx, cy - 180, "不碰它", 50, A(WHITE, 1), k=1)
        d.text(cx, cy + 60, f"{day}天", 170, A(OL, 1), k=1)
    else:
        rays(d, t, (60, 50, 140), (16, 12, 40), 22, 540, 1200)
        p = drop_pos(t, [DAY28]); y = 1470 - 150 * (1 - p)
        rig(d, 540, 980, 1470)
        mimosa(d, 540, y, 240, t, 0.0, "bored" if t < DAY28 + 0.4 else "proud", squash=pulse(t, [DAY28], 9))
        sparks(d, 540, 1300, t, DAY28, 70, 1500, MINT, 1, 7, 1.1)
def u_mem(t, d):
    if t < DAY28 - 0.3:
        d.text(540, 320, "一个月不碰它", 90, A(WHITE, ease(pr(t, CAL0, CAL0 + 0.3))), k=1)
    else:
        k = back(pr(t, DAY28, DAY28 + 0.2))
        d.text(552, 412, "还记得！", int(180 * k) + 1, A(OL, 1), k=1); d.text(540, 400, "还记得！", int(180 * k) + 1, A(YEL, 1), k=1)
        d.text(540, 580, "照样不合", 70, A(MINT, ease(pr(t, DAY28 + 0.6, DAY28 + 0.9))), k=1)
    flash(d, t, [DAY28], WHITE, 0.8)

def w_dark(t, d):
    grad(d, (14, 16, 30), (4, 4, 10))
    d.rect(540, 0, 1080, 1920, fill=A((80, 70, 30), 0.35))
    glow(d, 810, 500, 260, YEL, 1); d.circ(810, 500, 90, fill=A(YEL, 1))
    d.circ(270, 500, 70, fill=A((120, 120, 140), 0.6))
    kL = back(pr(t, DARK + 0.2, DARK + 0.5)); kR = back(pr(t, DARK + 0.5, DARK + 0.8))
    mimosa(d, 270, 1470, 170 * kL + 1, t, 0.0, "proud", flower=False)
    mimosa(d, 810, 1470, 170 * kR + 1, t, 0.6 + 0.4 * math.sin(t * 6) ** 2, "scared", flower=False)
    for i, (lab, col) in enumerate((("学得快", MINT), ("记得久", MINT))):
        a = back(pr(t, DARK + 1.4 + i * 0.4, DARK + 1.6 + i * 0.4))
        d.text(270, 560 + i * 100, lab, int(66 * a) + 1, A(col, 1), k=1)
def u_dark(t, d):
    d.text(270, 300, "光少", 100, A(WHITE, ease(pr(t, DARK, DARK + 0.3))), k=1)
    d.text(810, 300, "光多", 100, A(WHITE, ease(pr(t, DARK + 0.3, DARK + 0.6))), k=1)

def w_end(t, d):
    grad(d, (18, 60, 50), (6, 20, 18)); leaves_bg(d, t, (30, 100, 80), 0.4)
    p = drop_pos(t, [LAST]); y = 1300 - 120 * (1 - p) if t > LAST - 0.5 else 1300
    mimosa(d, 540, y, 280, t, 0.0, "closed" if int(t * 2) % 5 else "proud", squash=pulse(t, [LAST], 9))
def u_end(t, d):
    d.text(540, 330, "没有大脑", int(130 * back(pr(t, OUTRO, OUTRO + 0.25))), A(WHITE, 1), k=1)
    d.text(540, 490, "也会学习", int(130 * back(pr(t, OUTRO + 0.6, OUTRO + 0.85))), A(YEL, 1), k=1)
    a = ease(pr(t, OUTRO + 1.6, OUTRO + 2.0))
    d.rect(110, 1440, 970, 1560, fill=A((0, 0, 0), 0.6 * a), r=30)
    d.text(540, 1500, "你小时候也一直戳过它吗？", 50, A(WHITE, a), k=1)
    d.text(540, 1800, "Gagliano et al. 2014, Oecologia 175:63–72", 26, A(WHITE, 0.75 * a), k=0)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

SECS = [(0, HOOK_END, w_hook, u_hook), (HOOK_END, MACH, w_touch, u_touch), (MACH, BURST, w_drop, u_drop),
        (BURST, CAL0, w_learn, u_learn), (CAL0, DARK, w_mem, u_mem), (DARK, OUTRO, w_dark, u_dark), (OUTRO, 99, w_end, u_end)]
CUTS = [HOOK_END, MACH, BURST, SHAKE, CAL0, DAY28 - 0.3, DARK, OUTRO]
HITS = [HOOK_DROP, POKE, BURST, SHAKE + 0.1, NOTTIRED, DAY28, LAST] + SLOW

def subs(t, d):
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.12)) * (1 - pr(t, b - 0.1, b))
            lines = wrap(d, s, 58, 920)
            for j, ln in enumerate(lines):
                y = 1660 + (j - (len(lines) - 1) / 2) * 84
                w = d.tlen(ln, 58)
                d.rect(540 - w / 2 - 24, y - 44, 540 + w / 2 + 24, y + 44, fill=A((0, 0, 0), 0.62 * al), r=16)
                d.text(540, y, ln, 58, A(WHITE, al))
def brand(t, d):
    d.rect(50, 80, 300, 128, fill=A(WHITE, 0.92), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(BG, 1))
    d.rect(780, 80, 1030, 128, fill=A((60, 160, 110), 0.95), r=24); d.text(905, 104, "含羞草会记仇", 26, A(WHITE, 1))

def cam(t):
    z = 1.0 + 0.07 * pulse(t, HITS, 7) + 0.03 * pulse(t, FAST, 14)
    if t < 0.5: z += 0.12 * (1 - ease(pr(t, 0, 0.3)))
    if RISER[0] <= t < BURST: z += 0.12 * eio(pr(t, RISER[0], BURST))
    amp = 28 * pulse(t, [HOOK_DROP, BURST, DAY28], 3) + 12 * pulse(t, HITS, 5) + 5 * pulse(t, FAST, 14)
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx, 960 + sy

def frame(t):
    img = Image.new("RGB", (W, H), BG); d = D(img); ui = None
    for a, b, sf, uf in SECS:
        if a <= t < b: sf(t, d); ui = uf; break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    d = D(img)
    if ui: ui(t, d)
    for c in CUTS:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.55 * (1 - (t - c) / 0.1)))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)

if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.1f}.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        last = None
        for i in range(i0, i1):
            try: last = frame(i / FPS).tobytes()
            except Exception as e: print('ERR', i, e, file=sys.stderr)
            if last: p.stdin.write(last)
        p.stdin.close(); p.wait()
