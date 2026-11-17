import sys, subprocess, math, random
from mchars import *
from cues import *

def popk(t, t0, preset="snappy"): return max(0.0, E.spring_at(t, t0, 0, 1, preset)) if t >= t0 else 0.0
def ap(t, t0, d=0.12): return cl((t - t0) / d)
def tag(d, x, y, s, col, a=1.0, size=40, tc=NAVYT):
    if a <= 0.01: return
    w = d.tlen(s, size, 1) + 44
    d.rect(x - w / 2, y - size * 0.78, x + w / 2, y + size * 0.78, fill=A(col, 0.95 * a), r=size * 0.6)
    d.text(x, y, s, size, A(tc, a), k=1)
def ptag(d, t, t0, x, y, s, col, size=40, tc=NAVYT, t1=None):
    k = popk(t, t0)
    if t1 is not None: k *= 1 - pr(t, t1 - 0.15, t1)
    if k > 0: tag(d, x, y + (1 - min(k, 1)) * 30, s, col, min(1, ap(t, t0)) * (1 if t1 is None else 1 - pr(t, t1 - 0.15, t1)), int(size * (0.6 + 0.4 * min(1.1, k))), tc)
def arrow(d, x0, y0, x1, y1, col, a=1.0, w=12):
    L = math.hypot(x1 - x0, y1 - y0) + 1e-6; ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    bx, by = x1 - ux * w * 2.4, y1 - uy * w * 2.4
    d.line([(x0, y0), (bx, by)], A(col, a), w); d.poly([(bx + nx * w * 1.6, by + ny * w * 1.6), (x1, y1), (bx - nx * w * 1.6, by - ny * w * 1.6)], A(col, a))
def check_mark(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 18 * s_, y), (x - 4 * s_, y + 14 * s_), (x + 20 * s_, y - 14 * s_)], A(WHITE, a), 8 * s_)
def zap(d, x, y, t, t0, col=WHITE, maxr=380, a=1.0):
    u = (t - t0) / 0.7
    if 0 <= u < 1:
        for j in range(3):
            d.circ(x, y, 30 + (u + j * 0.1) * maxr, outline=A(col, a * (1 - u) * (1 - j * 0.3)), w=10 - j * 3)
def qmark(d, x, y, size, col, a=1.0): d.text(x, y, "?", int(size), A(col, a), k=1)

def wiggle(t, t0, amp=0.32, dur=1.2, hz=7.0):
    if t < t0: return 0.0
    u = t - t0
    return amp * math.sin(u * hz * 2 * math.pi) * math.exp(-u * 3.2) if u < dur * 2 else 0.0

# ---------------- the find-it bush (hook / reveal / end share it: match cut) ----------------
MX, MY, MS = 560, 1010, 1.0
BACK = [(230, 1250, -1.75, 1.05, 11), (850, 1260, -1.45, 1.0, 12), (420, 1270, -1.25, 0.9, 13), (700, 1240, -1.95, 1.0, 14)]
FRONT = [(330, 1300, -1.35, 1.0, 21), (760, 1300, -1.85, 1.05, 22), (560, 1320, -1.6, 0.85, 23), (180, 1280, -1.1, 0.8, 24), (920, 1290, -2.05, 0.8, 25)]
def bush(d, t, camo=1.0, wig=0.0, face="happy", eyes=0.0, front_a=1.0, part=0.0, glowk=0.0, look=0.0, blush=0.0):
    jungle(d, t)
    for i in range(6):
        d.circ(140 + i * 170, 1330 + 30 * math.sin(i), 120, fill=A((14, 40, 34), 1))
    d.rect(-50, 1330, 1130, 1970, fill=A((16, 34, 30), 1))
    for x, y, an, s, sd in BACK: frond(d, x, y, s, an, t, SEL_D, 1, sd, L=340)
    mantis(d, MX, MY, MS, t, 1, face, wig=wig, camo=camo, eyes_open=eyes, glowk=glowk, look=look, blush=blush)
    for x, y, an, s, sd in FRONT:
        dx = (x - MX) * 0.35 * part
        frond(d, x + dx, y, s, an + (0.3 * part * (1 if x > MX else -1)), t, SEL, front_a, sd, L=400)
    if camo > 0.5 and part < 0.05:
        frond(d, MX + 150, 1060, 0.7, -2.2, t, SEL, front_a, 29, L=300)

def s_hook(t, d):
    bush(d, t, 1.0, 0.0, "happy", 0.0)
    for i, c in enumerate(COUNT):
        t1 = COUNT[i + 1] if i + 1 < len(COUNT) else BIG1
        k = popk(t, c, "bouncy")
        if c <= t < t1:
            a_ = 1 - pr(t, t1 - 0.12, t1)
            d.circ(540, 400, 120, fill=A((6, 20, 20), 0.55 * a_))
            prog_ = pr(t, c, t1)
            d.arc(540, 400, 120, 120, -90, -90 + 360 * (1 - prog_), A(GOLD, a_), 12)
            d.text(540, 400, str(3 - i), int(170 * min(1.15, 0.6 + 0.4 * k)), A(GOLD, a_), k=1)
    ptag(d, t, 0.25, 540, 600, "找找看！", WHITE, 46)

def s_reveal(t, d):
    t0 = BIG1
    w = wiggle(t, t0, 0.34, 1.4) + wiggle(t, t0 + 1.6, 0.16, 0.8)
    camo = 1 - ease(pr(t, t0 + 0.05, t0 + 0.5))
    face = "shock" if t < t0 + 1.0 else "happy"
    bush(d, t, camo, w, face, 1.0 if t > t0 + 0.1 else 0.0, 1 - 0.55 * ease(pr(t, t0 + 0.2, t0 + 0.8)), ease(pr(t, t0 + 0.2, t0 + 0.9)),
         glowk=0.8 * ease(pr(t, t0, t0 + 0.3)), blush=ease(pr(t, t0 + 1.0, t0 + 1.4)))
    bx, by = butt_point(MX, MY, MS, w)
    zap(d, bx, by, t, t0, GOLD, 420)
    sparks(d, bx, by, t, t0, 34, 900, (255, 230, 140), 1, 5, 1.0)
    for j in range(3):   # motion lines on the wiggling butt
        if t0 < t < t0 + 1.2:
            yy = by - 50 + j * 50; d.line([(bx - 170 - 20 * j, yy), (bx - 110 - 20 * j, yy)], A(WHITE, 0.8 * (1 - pr(t, t0, t0 + 1.2))), 8)
    ptag(d, t, t0 + 0.15, 540, 470, "找到啦！", GOLD, 64)

def s_lobes(t, d):
    t0 = T["lobes"]
    flatbg(d, (34, 84, 76), (12, 36, 36), t, True)
    x, y, s = 640, 860, 1.75
    w = 0.05 * math.sin((t - t0) * 3)
    hi = 7 - int((t - t0 - 0.6) / 0.22) if t > t0 + 0.6 else -5
    hk = 1.0 if 1 <= hi <= 7 else (0.6 if t > t0 + 0.6 + 7 * 0.22 else 0)
    mantis(d, x, y, s, t, 1, "proud", wig=w, lobe_hi=hk, hi_i=(hi if 1 <= hi <= 7 else -1), look=0.3)
    sp = [butt_point(x, y, s, w)]
    bx, by = sp[0]
    k = ease(pr(t, t0 + 0.4, t0 + 0.8))
    if k > 0:
        arrow(d, 330, 640, lerp(330, bx + 20, k), lerp(640, by - 75, k), GOLD, 1, 10)
        arrow(d, 330, 1110, lerp(330, bx + 20, k), lerp(1110, by + 75, k), GOLD, 1, 10)
    ptag(d, t, t0 + 0.35, 330, 600, "上面一排", GOLD, 36)
    ptag(d, t, t0 + 0.6, 330, 1150, "下面一排", GOLD, 36)
    ptag(d, t, t0 + 2.2, 760, 640, "翅膀透明", WINGC, 34)

def s_bird(t, d):
    t0 = T["bird"]
    grad(d, (44, 52, 92), (16, 22, 40))
    d.circ(820, 380, 90, fill=A((255, 236, 180), 0.9)); glow(d, 820, 380, 200, (255, 236, 180), 0.3)
    d.rect(-50, 1330, 1130, 1970, fill=A((18, 30, 40), 1))
    for x, y, an, s, sd in BACK: frond(d, x, y, s, an, t, SEL_D, 1, sd, L=340)
    strike = ease(pr(t, t0 + 2.75, t0 + 2.9)) * (1 - ease(pr(t, t0 + 3.1, t0 + 3.4)))
    face = "smug" if t < t0 + 2.6 else ("happy")
    mantis(d, MX, MY, MS, t, 1, face, camo=0.75, eyes_open=1, arm=strike, look=-0.6 if t < t0 + 2.2 else 0.6)
    for x, y, an, s, sd in FRONT[:3]: frond(d, x, y, s, an, t, SEL, 0.85, sd, L=330)
    # bird: flies in, hovers puzzled, flies away
    u = t - t0
    bx = lerp(-150, 430, ease(pr(t, t0, t0 + 0.8))) + lerp(0, 900, E.ease_in_cubic(pr(t, t0 + 2.0, t0 + 2.8)))
    by = 560 + 30 * math.sin(u * 5)
    bird(d, bx, by, 1.15, t, 1, "sus", 1, flap=u * 18)
    if t0 + 0.8 < t < t0 + 2.1:
        k = popk(t, t0 + 0.85, "bouncy"); qmark(d, bx + 30, by - 140, 110 * min(1.1, k), WHITE)
        ptag(d, t, t0 + 1.0, bx + 10, by + 120, "只是草吧？", WHITE, 32)
    # gnat
    if t < t0 + 2.95:
        gx = lerp(1150, 860, ease(pr(t, t0 + 1.8, t0 + 2.6))) + 12 * math.sin(u * 9); gy = 760 + 14 * math.cos(u * 7)
        gnat(d, gx, gy, 1.2, t)
    ptag(d, t, t0 + 3.0, 760, 700, "抓到！", GOLD, 48)

def s_amber(t, d):
    t0 = T["amber"]
    k_res = ease(pr(t, t0 + 0.1, t0 + 1.1))       # resin engulfs
    pull = eio(pr(t, t0 + 1.1, t0 + 2.2))          # camera pulls back to a gem
    grad(d, mix((24, 52, 46), (40, 22, 10), pull), mix((8, 20, 20), (14, 8, 4), pull))
    s = lerp(1.2, 0.55, pull); cx, cy = 560, lerp(930, 830, pull)
    if pull < 1:
        for x, y, an, sc, sd in BACK[:2]: frond(d, lerp(x, 540, pull), lerp(y, 900, pull), sc * (1 - pull * 0.6), an, t, SEL_D, 1 - pull, sd, L=340)
    rx = lerp(30, lerp(470, 330, pull), k_res); ry = lerp(30, lerp(420, 220, pull), k_res)
    # dripping resin from top before it covers
    if t < t0 + 0.7:
        da = 1 - pr(t, t0 + 0.4, t0 + 0.7)
        yy = lerp(260, cy - 80, ease(pr(t, t0, t0 + 0.5)))
        d.line([(cx - 20, 260 + 300 * pr(t, t0 + 0.35, t0 + 0.7)), (cx - 20, max(260, yy))], A(AMB_L, 0.9 * da), 50)
        d.circ(cx - 20, yy, 46, fill=A(AMB_L, 0.95 * da))
    ea = 0.0 if k_res <= 0 else min(1, k_res * 1.3)
    amber_back(d, cx - 30 * s, cy - 30 * s, rx, ry, ea)
    mantis(d, cx + 40 * s, cy - 20 * s, s, t, 1, "shock" if t < t0 + 1.4 else "happy", camo=0.0, eyes_open=1)
    amber_front(d, cx - 30 * s, cy - 30 * s, rx, ry, ea)
    # odometer 0 -> 9800
    k = ease(pr(t, t0 + 0.6, t0 + 2.2))
    if t > t0 + 0.5:
        v = int(round(9800 * k / 100) * 100)
        d.text(540, 400, f"{v}", int(150 * (0.9 + 0.1 * popk(t, t0 + 0.5))), A(GOLD, ap(t, t0 + 0.5)), k=1)
        d.text(540, 510, "万年前", 56, A(WHITE, ap(t, t0 + 0.6)), k=1)
    ptag(d, t, t0 + 2.3, 540, 1100, "缅甸琥珀", AMB_L, 40)
    if t > t0 + 2.6: d.text(540, 1165, "Folimantis hyalinala", 30, A((255, 230, 190), ap(t, t0 + 2.6, 0.3)), k=0)

def s_q(t, d):
    t0 = T["q"]
    dim = 1 - 0.4 * pr(t, SIL0, SIL0 + 0.15)
    grad(d, mix((40, 22, 10), (10, 6, 4), 1 - dim), (10, 6, 4))
    s = 0.7; cx, cy = 400, 900
    amber_back(d, cx - 30 * s, cy - 30 * s, 330 * s, 240 * s, dim)
    mantis(d, cx + 40 * s, cy - 20 * s, s, t, dim, "happy", eyes_open=1, look=0.8)
    amber_front(d, cx - 30 * s, cy - 30 * s, 330 * s, 240 * s, dim)
    # mystery plant silhouette
    k = popk(t, t0 + 0.3, "bouncy")
    if k > 0:
        frond(d, 800, 1180, 0.8 * min(1, k), -1.65, t, (60, 60, 70), dim, 31, L=360)
        qmark(d, 800, 690 + 10 * math.sin(t * 6), 200 * min(1.1, k), GOLD, dim)
    ptag(d, t, t0 + 0.2, 540, 420, "它装成了谁？", WHITE, 44)

def s_big2(t, d):
    t0 = BIG2
    rays(d, t, (40, 110, 70), (18, 60, 40), 18, 540, 860)
    dead = ease(pr(t, t0 + 1.2, t0 + 1.9))
    crumble = pr(t, t0 + 1.9, t0 + 3.2)
    fa = 1 - 0.75 * crumble
    frond(d, 330, 1220, 1.25 * (0.6 + 0.4 * min(1, popk(t, t0, "bouncy"))), -1.62, t, SEL, fa, 41, L=440, dead=dead)
    frond(d, 380, 1230, 1.05, -1.25, t, SEL, fa, 42, L=360, dead=dead)
    if crumble > 0:
        rv = random.Random(5)
        for i in range(40):
            x0, y0 = rv.uniform(200, 520), rv.uniform(650, 1200)
            d.circ(x0 + rv.uniform(-60, 60) * crumble, y0 + 320 * crumble ** 1.5 * rv.uniform(0.5, 1), rv.uniform(5, 11), fill=A(DEAD, (1 - crumble) * 0.9))
    face = "shock" if t > t0 + 1.4 else "happy"
    mantis(d, 790, 980, 1.0, t, 1, face, flip=-1, look=0.5, wig=wiggle(t, t0, 0.2, 0.8))
    ptag(d, t, t0 + 0.1, 330, 660, "卷柏", SEL_L, 56)
    if t > t0 + 1.6:
        stamp(d, t, t0 + 1.6, "已灭绝", 540, 430, 140, (240, 70, 70))

def s_none(t, d):
    t0 = T["none"]
    grad(d, (30, 40, 70), (10, 14, 30))
    d.rect(-50, 1100, 1130, 1970, fill=A((20, 28, 50), 1))
    kinds = [(300, (255, 160, 200), "兰花螳螂"), (540, (190, 140, 90), "枯叶螳螂"), (780, (130, 200, 100), "绿螳螂")]
    for i, (x, c, lab) in enumerate(kinds):
        k = popk(t, t0 + 0.2 + i * 0.25, "bouncy")
        if k <= 0: continue
        kk = min(1, k)
        mantis(d, x + 40, 980 - 40 * (1 - kk), 0.55 * kk, t + i, kk, "happy" if t < t0 + 2.2 else "sad", col=c, lobes=0.0, look=0.4)
        d.text(x, 1150, lab, 32, A(WHITE, kk), k=1)
        # thought bubble with a Selaginella sprig + ?
        kb = popk(t, t0 + 1.2 + i * 0.2, "bouncy")
        if kb > 0:
            bx, by = x, 700
            d.circ(bx, by, 85 * min(1, kb), fill=A(WHITE, 0.95)); d.circ(bx - 30, by + 105, 16 * min(1, kb), fill=A(WHITE, 0.95))
            frond(d, bx - 20, by + 50, 0.35 * min(1, kb), -1.6, t, SEL, 1, 50 + i, L=260, depth=1)
            qmark(d, bx + 40, by - 20, 70 * min(1, kb), (230, 80, 70))
    # magnifier sweep
    mx = 540 + 300 * math.sin((t - t0) * 1.6); my = 900 + 40 * math.cos((t - t0) * 2.1)
    d.circ(mx, my, 95, fill=A(WHITE, 0.08)); d.circ(mx, my, 95, outline=A(WHITE, 0.9), w=12); d.line([(mx + 68, my + 68), (mx + 150, my + 150)], A(WHITE, 0.9), 18)
    ptag(d, t, t0 + 0.1, 540, 430, "现代螳螂", WHITE, 40)
    ptag(d, t, t0 + 2.0, 540, 530, "目前还没发现", GOLD, 52)

def s_match(t, d):
    t0 = T["match"]
    grad(d, (24, 56, 52), (8, 22, 22))
    for j, (x, lab, col) in enumerate(((365, "螳螂肚子", M_G), (715, "卷柏叶子", SEL))):
        k = popk(t, t0 + 0.1 + 0.2 * j, "smooth")
        if k <= 0: continue
        r = 165 * min(1.05, k)
        d.circ(x, 700, r + 14, fill=A(WHITE, 0.95)); d.circ(x, 700, r, fill=A((230, 244, 226), 1))
        ex = ease(pr(t, t0 + 0.4, t0 + 1.0))
        if j == 0:
            d.line([(x - 120, 730), (x + 120, 730)], A(M_G, 1), 46)
            for i in range(5):
                xx = x - 100 + i * 50
                for sd in (-1, 1): leaf(d, xx, 730 + sd * 18, 60 * min(1, k), 21, -math.pi / 2 * sd + (-0.55 if sd > 0 else 0.55) - math.pi / 2 * (sd - 1) * 0 + (math.pi if sd > 0 else 0) * 0, LOBE if i % 2 else LOBE_L, 1)
        else:
            d.line([(x - 120, 730), (x + 120, 730)], A(SEL_D, 1), 10)
            for i in range(5):
                xx = x - 100 + i * 50
                for sd in (-1, 1): leaf(d, xx, 730, 60 * min(1, k), 21, -math.pi / 2 * sd + (-0.55 if sd > 0 else 0.55), SEL if i % 2 else SEL_L, 1)
        d.text(x, 470, lab, 38, A(WHITE, min(1, k)), k=1)
    d.text(540, 700, "≈", 90, A(GOLD, ap(t, t0 + 0.8)), k=1)
    rows = ["形状", "大小", "排列"]
    for i, s_ in enumerate(rows):
        tt = t0 + 1.2 + i * 0.9
        k = popk(t, tt, "bouncy")
        if k <= 0: continue
        y = 940 + i * 90; kk = min(1, k)
        d.rect(300, y - 38, 780, y + 38, fill=A((255, 255, 255), 0.12 * kk), r=30)
        d.text(470, y, s_, 46, A(WHITE, kk), k=1)
        check_mark(d, 640, y, 34, (90, 200, 110), kk, k)

def s_first(t, d):
    t0 = T["first"]
    flatbg(d, (36, 30, 60), (12, 10, 26), t, False)
    y = 900; xl, xr = 210, 870
    e = ease(pr(t, t0 + 0.1, t0 + 0.8))
    d.line([(xr, y), (lerp(xr, xl, e), y)], A(WHITE, 0.85), 10)
    d.text(xr, y + 70, "今天", 34, A(WHITE, ap(t, t0 + 0.1)), k=1)
    for i in range(1, 6):
        xx = lerp(xr, xl, i / 6)
        if e > i / 6: d.line([(xx, y - 18), (xx, y + 18)], A(WHITE, 0.6), 6)
    # mantis-with-leaves pin at the far left
    k = popk(t, t0 + 0.8, "bouncy")
    if k > 0:
        kk = min(1.1, k)
        d.circ(xl + 40, y, 22 * kk, fill=A(GOLD, 1))
        d.text(xl + 40, y + 70, "9800万年前", 32, A(GOLD, min(1, k)), k=1)
        d.rect(xl - 30, 520, xl + 330, 800, fill=A(AMB, 0.9 * min(1, k)), r=40)
        mantis(d, xl + 175, 690, 0.62 * min(1, kk), t, min(1, k), "proud", look=0.5)
        d.line([(xl + 40, y - 22), (xl + 40, 800)], A(GOLD, min(1, k)), 6)
    # crown + "最早"
    kc = popk(t, t0 + 1.6, "bouncy")
    if kc > 0:
        cx_, cy_ = xl + 210, 470 - 20 * (1 - min(1, kc))
        d.poly([(cx_ - 60, cy_ + 30), (cx_ - 70, cy_ - 30), (cx_ - 30, cy_), (cx_, cy_ - 45), (cx_ + 30, cy_), (cx_ + 70, cy_ - 30), (cx_ + 60, cy_ + 30)], A(GOLD, min(1, kc)))
        ptag(d, t, t0 + 1.7, 680, 470, "最早！", GOLD, 56)
    # other fossil insects later on the line (grey dots), the record keeps going
    for i in range(4):
        kd = popk(t, t0 + 2.2 + i * 0.2)
        if kd > 0: d.circ(lerp(xr, xl, 0.15 + i * 0.17), y - 60, 14 * min(1, kd), fill=A((180, 180, 200), 0.7))
    ptag(d, t, t0 + 2.4, 540, 1120, "清楚的化石证据", WHITE, 38)

def s_rear(t, d):
    t0 = T["rear"]
    grad(d, (60, 40, 80), (20, 12, 34))
    x, y, s = 620, 820, 1.6
    w = wiggle(t, t0 + 0.5, 0.18, 1.0, 5) + wiggle(t, t0 + 2.6, 0.12, 0.8, 5)
    bx, by = butt_point(x, y, s, w)
    d.ell(bx, by + 30, 300, 260, A((255, 240, 200), 0.10))
    mantis(d, x, y, s, t, 1, "smug" if t < t0 + 2.0 else "happy", wig=w, blush=ease(pr(t, t0 + 2.2, t0 + 2.6)), lobe_hi=0.35 * (0.5 + 0.5 * math.sin(t * 6)), look=-0.6)
    ptag(d, t, t0 + 0.3, bx, by - 230, "只有这里像叶子", GOLD, 40)
    e = ease(pr(t, t0 + 1.9, t0 + 2.9))
    if e > 0:
        ya = y + 165 * s
        arrow(d, bx - 40, ya, lerp(bx - 40, x + 130 * s, e), ya, WHITE, 1, 12)
        ptag(d, t, t0 + 2.4, 540, ya + 62, "伪装从屁股开始？", WHITE, 36)
    ptag(d, t, t0 + 2.6, 840, 420, "科学家猜", (200, 180, 255), 34)

def s_card(t, d):
    t0 = T["card"]
    flatbg(d, (40, 90, 80), (14, 40, 36), t, False)
    k = popk(t, t0 + 0.1, "smooth")
    if k <= 0: return
    a_ = ap(t, t0 + 0.1); w_, h_ = 720 * (0.85 + 0.15 * k), 930 * (0.85 + 0.15 * k); cx_, cy_ = 540, 800
    d.rect(cx_ - w_ / 2, cy_ - h_ / 2, cx_ + w_ / 2, cy_ + h_ / 2, fill=A((250, 246, 234), a_), r=40)
    tag(d, cx_, cy_ - h_ / 2 + 70, "一句话学会", GOLD, a_, 32)
    d.text(cx_, cy_ - 250, "拟态", 120, A((46, 120, 70), a_), k=1)
    # icon: lobe row  ≈  Selaginella sprig
    ki = ap(t, t0 + 0.7, 0.3)
    if ki > 0:
        d.line([(300, cy_ - 40), (470, cy_ - 40)], A(M_G, ki), 40)
        for i in range(4):
            for sd in (-1, 1): leaf(d, 320 + i * 45, cy_ - 40 + sd * 14, 48, 17, -math.pi / 2 * sd + (-0.5 if sd > 0 else 0.5), LOBE if i % 2 else LOBE_L, ki)
        d.text(540, cy_ - 40, "≈", 80, A(GOLD, ki), k=1)
        frond(d, 660, cy_ + 20, 0.42, -1.2, t, SEL, ki, 61, L=300, depth=1)
    for i, s_ in enumerate(("把自己长得像别的东西，", "骗过眼睛")):
        kk = ap(t, t0 + 1.2 + i * 0.5, 0.25)
        if kk > 0: d.text(cx_, cy_ + 150 + i * 80, s_, 46, A(NAVYT, kk * a_), k=1)
    kk = ap(t, t0 + 2.4, 0.3)
    if kk > 0: d.text(cx_, cy_ + 330, "它：肚子装成卷柏叶", 34, A((90, 110, 100), kk * a_), k=1)

def s_end(t, d):
    t0 = T["end"]
    w = wiggle(t, t0 + 1.2, 0.22, 1.0)
    bush(d, t, 1.0, w, "smug", 1.0 if t0 + 1.0 < t < t0 + 2.6 else 0.0)
    bx, by = butt_point(MX, MY, MS, w)
    k = popk(t, t0 + 0.2, "bouncy")
    if k > 0:
        d.circ(540, 400, 110 * min(1.05, k), fill=A((6, 20, 20), 0.6))
        d.text(540, 392, "第?秒", int(70 * min(1.1, k)), A(GOLD, 1), k=1)
    ra = ap(t, t0 + 1.8, 0.3)
    if ra > 0:
        d.rect(170, 540, 910, 700, fill=A((6, 8, 20), 0.65 * ra), r=20)
        d.text(540, 575, "Yang et al. 2026, New Phytologist", 26, A(WHITE, 0.95 * ra), k=0)
        d.text(540, 618, "doi:10.1111/nph.71619", 24, A(WHITE, 0.85 * ra), k=0)
        d.text(540, 660, "报道：ScienceAlert 2026-11-14", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "你能找到吗", "reveal": "藏在这里", "lobes": "像叶子的小瓣", "bird": "认不出", "amber": "9800 万年", "q": "哪种植物",
      "big2": "早就灭绝", "none": "还没发现", "match": "很像", "first": "最早", "rear": "屁股", "card": "拟态", "end": "第几秒"}
def subs(t, d):
    for a, b, s, key in SUBS:
        if key == "card": continue                     # the card itself carries this line
        if a <= t < b:
            ee = E.enter_exit(t, max(a, 0), b, 0.3, 0.12, rise=18, s0=0.96)
            al = ee["alpha"] if a > 0 else (1 - pr(t, b - 0.12, b))
            if al <= 0.01: return
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70 + ee["dy"] * (a > 0)
            w = max(d.tlen(x, 54, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 70 + 46, fill=A((6, 14, 26), 0.82 * al), r=22)
            hw = HL.get(key)
            for i, x in enumerate(ls):
                yy = y0 + i * 70
                if hw and hw in x:
                    j = x.index(hw); parts = [(x[:j], WHITE), (hw, GOLD), (x[j + len(hw):], WHITE)]
                    xx = 540 - d.tlen(x, 54, 1) / 2
                    for p_, c_ in parts:
                        if p_: d.text(xx, yy, p_, 54, A(c_, al), anchor="lm", k=1); xx += d.tlen(p_, 54, 1)
                else: d.text(540, yy, x, 54, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)
    d.text(540, 228, "新物种 · 屁股会装叶子的螳螂", 24, A((235, 235, 225), 0.85), k=1)

SF = {n: globals()["s_" + n] for n in NAMES}
SECS = [(-1, T["reveal"], s_hook, "hook")] + [(T[n], nxt(n), SF[n], n) for n in NAMES[1:]]
SECS = [(a, (99 if i == len(SECS) - 1 else b), f, n) for i, (a, b, f, n) in enumerate(SECS)]
HARD = {BIG1, BIG2}
def cam(t):
    z = 1.0 + 0.04 * pulse(t, [BIG1, BIG2], 3); cx, cy = 540, 900
    if t < BIG1:                       # 0–3 s: camera already drifting in + panning (motion from frame 0)
        z += 0.07 * E.ease_in_out_sine(pr(t, 0, BIG1)) + 0.02; cx = 500 + 60 * E.ease_in_out_sine(pr(t, 0, BIG1)); cy = 930
    elif t < T["lobes"]:
        z += 0.09 + 0.16 * ease(pr(t, BIG1 + 0.25, BIG1 + 1.1)); cx, cy = 520, 900
    else:
        for a, b, f, n in SECS:
            if a <= t < b: z += 0.03 * eio(pr(t, max(a, 0), min(b, DUR))); break
    sx, sy = shake(t, 8 * pulse(t, [BIG1, BIG2], 5), 40)
    return z, cx + sx, cy + sy
def render_world(t, idx):
    img = Image.new("RGB", (W, H), (20, 40, 30)); d = D(img)
    SECS[idx][2](t, d)
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
XF = 0.3
def frame(t, fi=0, ui=True):
    idx = next(i for i, (a, b, f, n) in enumerate(SECS) if a <= t < b)
    img = render_world(t, idx)
    a = SECS[idx][0]
    if idx > 0 and a not in HARD and t < a + XF:          # soft cross-dissolve between ordinary scenes
        prev = render_world(t, idx - 1)
        img = Image.blend(prev, img, E.ease_in_out_sine((t - a) / XF))
    d = D(img)
    for c in HARD:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.55 * (1 - (t - c) / 0.1)))
    brand(t, d)
    if ui: subs(t, d)
    out = img.resize((OW, OH), Image.LANCZOS)
    out = E.vignette(out, 0.2); out = E.grain(out, 0.03, seed=fi)
    return out
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/mt_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[3:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save(sys.argv[2])
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                              "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", out], stdin=subprocess.PIPE)
        last = None; errs = 0
        for i in range(i0, i1):
            try: last = frame(i / FPS, i).tobytes()
            except Exception as e: errs += 1; print('ERR', i, e, file=sys.stderr)
            if last: p.stdin.write(last)
        p.stdin.close(); p.wait(); print('errs', errs, file=sys.stderr)
