import sys, subprocess, math, random
from chars import *
from cues import *

def popk(t, t0, preset="snappy"): return max(0.0, E.spring_at(t, t0, 0, 1, preset)) if t >= t0 else 0.0
def ap(t, t0, d=0.12): return cl((t - t0) / d)
def tag(d, x, y, s, col, a=1.0, size=40, tc=NAVYT):
    if a <= 0.01: return
    w = d.tlen(s, size, 1) + 44
    d.rect(x - w / 2, y - size * 0.78, x + w / 2, y + size * 0.78, fill=A(col, 0.95 * a), r=size * 0.6)
    d.text(x, y, s, size, A(tc, a), k=1)
def ptag(d, t, t0, x, y, s, col, size=40, tc=NAVYT):
    k = popk(t, t0)
    if k > 0: tag(d, x, y + (1 - min(k, 1)) * 30, s, col, ap(t, t0), int(size * (0.6 + 0.4 * k)), tc)
def title(d, t, t0, s, y=330, size=110, col=WHITE):
    k = popk(t, t0, "heavy")
    if k > 0: d.text(540, y + (1 - k) * 40, s, int(size * (0.85 + 0.15 * k)), A(col, ap(t, t0)), k=1)
def slamtxt(d, t, t0, s, y, size, col):
    if t < t0: return
    d.text(540, y, s, int(size * E.slam(t, t0, 0.28, 1.8)), A(col, ap(t, t0, 0.06)), k=1)
def arrow(d, x0, y0, x1, y1, col, a=1.0, w=12):
    L = math.hypot(x1 - x0, y1 - y0) + 1e-6; ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    bx, by = x1 - ux * w * 2.4, y1 - uy * w * 2.4
    d.line([(x0, y0), (bx, by)], A(col, a), w); d.poly([(bx + nx * w * 1.6, by + ny * w * 1.6), (x1, y1), (bx - nx * w * 1.6, by - ny * w * 1.6)], A(col, a))
def cross(d, x, y, s, k, col, a=1.0):
    if k <= 0: return
    d.line([(x - s, y - s), (x - s + 2 * s * min(1, k * 2), y - s + 2 * s * min(1, k * 2))], A(col, a), s * 0.3)
    if k > 0.5: d.line([(x + s, y - s), (x + s - 2 * s * (k - 0.5) * 2, y - s + 2 * s * (k - 0.5) * 2)], A(col, a), s * 0.3)
def blink(t, t0, n=4, per=0.32):
    """blinking glow envelope: n flashes starting t0"""
    if t < t0: return 0.0
    u = (t - t0) / per; i = int(u)
    if i >= n: return 0.0
    f = u - i
    return math.exp(-f * 2.4) * (1 - 0.1 * i)
def zap(d, x, y, t, t0, col=GLOWC, maxr=300, a=1.0):
    u = (t - t0) / 0.7
    if 0 <= u < 1:
        for j in range(3):
            rr_ = 30 + (u + j * 0.1) * maxr
            d.circ(x, y, rr_, outline=A(col, a * (1 - u) * (1 - j * 0.3)), w=10 - j * 3)

# ---------------- scenes ----------------
HX, HY = 540, 1080
def s_hook(t, d):
    deep(d, t, (10, 40, 70), (2, 12, 30))
    g = max(blink(t, 0.0, 3, 0.45), 0.0)
    glow_(d, HX, HY - 150, 700, GLOWC, 0.5 * g)
    coral(d, 540, 1500, 0.9, t)
    polyp(d, HX, HY + 50, 1.9, t, glow=g, mood="scream" if t < 1.4 else "scared")
    # poking finger/stick from right
    u = pr(t, -0.2, 0.05) * (1 - pr(t, 0.4, 0.8))
    d.line([(1200, 700), (lerp(1200, HX + 120, u), lerp(700, HY - 140, u))], A(METAL, 1), 22)
    zap(d, HX, HY - 140, t, 0.02, GLOWC, 520)
    slamtxt(d, t, -0.25, "啪！", 360, 200, GLOWC)
    if t > 1.0: ptag(d, t, 1.0, 540, 520, "会报警？", WHITE, 64)
def s_deep(t, d):
    k = pr(t, T["deep"], T["deep"] + 2.5)
    deep(d, t, mix((20, 90, 150), DEEP1, k), DEEP2)
    # depth gauge descending
    dm = int(385 * E.ease_in_out_sine(pr(t, T["deep"] + 0.1, at("deep", 3))))
    x = 860
    d.rect(x - 8, 300, x + 8, 1200, fill=A(WHITE, 0.25), r=8)
    yy = lerp(300, 1200, dm / 385)
    d.circ(x, yy, 22, fill=A(GLOWC, 1))
    d.text(x - 40, yy, f"{dm} 米", 54, A(WHITE, 1), anchor="rm", k=1)
    caverock(d, t, 0.8, y0=lerp(500, 0, E.ease_out_cubic(k)))
    # little polyp peeking from dark at cave mouth
    kp = popk(t, at("deep", 3.2), "bouncy")
    if kp > 0:
        coral(d, 520, 1500, 0.55, t)
        polyp(d, 470, 1040, 0.9 * min(1, kp), t, mood="happy")
        bubble(d, 470, 820, "嗨", kp, size=44)
def s_q(t, d):
    deep(d, t)
    coral(d, 540, 1500, 0.8, t)
    polyp(d, 540, 1100, 1.6, t, mood="sus", look=math.sin(t * 2))
    kk = popk(t, T["q"] + 0.05, "bouncy")
    if kk > 0: d.text(540, 500, "?", int(300 * (0.6 + 0.4 * kk)), A(GLOWC, ap(t, T["q"])), k=1)
def s_reveal(t, d):
    rays(d, t, (255, 220, 90), (230, 160, 30))
    k = min(1.1, popk(t, BIG2, "bouncy"))
    glow_(d, 540, 900, 600, (255, 250, 200), 0.6 * k)
    polyp(d, 540, 1200, 2.4 * (0.6 + 0.4 * k), t, mood="proud")
    slamtxt(d, t, BIG2, "aureus", 330, 150, WHITE)
    ptag(d, t, at("reveal", 2), 540, 470, "拉丁语：金色的", NAVYT, 48, tc=WHITE)
def s_notcoral(t, d):
    deep(d, t, (20, 60, 100), (6, 20, 44))
    # left: coral (crossed), right: sea anemone cousin
    kc = popk(t, T["notcoral"] + 0.1)
    if kc > 0:
        coral(d, 300, 950, 0.45, t)
        tag(d, 300, 1030, "珊瑚", WHITE, ap(t, T["notcoral"] + 0.1), 40)
        cross(d, 300, 730, 110, pr(t, at("notcoral", 1), at("notcoral", 1.4)), (240, 70, 70))
    ka = popk(t, at("notcoral", 2), "bouncy")
    if ka > 0:
        # anemone: pink column + many tentacles
        x, y = 780, 950; s = 0.9 * min(1, ka)
        for i in range(16):
            ang = -math.pi / 2 + (i / 15 - 0.5) * 2.4; L = 120 * s
            d.line([(x, y - 140 * s), (x + math.cos(ang + 0.1 * math.sin(t * 3 + i)) * L, y - 140 * s + math.sin(ang) * L)], A((255, 140, 190), 1), 16 * s)
        d.rect(x - 60 * s, y - 150 * s, x + 60 * s, y, fill=A((240, 100, 160), 1), r=30 * s)
        tag(d, x, 1030, "海葵", WHITE, ap(t, at("notcoral", 2)), 40)
        polyp(d, 560, 950, 0.9, t, mood="happy")
        bubble(d, 600, 640, "我们是亲戚", ka, size=40)
def s_host(t, d):
    deep(d, t)
    floor(d, 1500)
    gr = E.ease_out_cubic(pr(t, T["host"], at("host", 2)))
    pts = coral(d, 540, 1520, 1.25, t, grow=gr)
    n = 0
    for i, (x, y, dep) in enumerate(pts):
        if dep < 1: continue
        t0 = at("host", 2) + (i % 9) * 0.12
        kk = popk(t, t0, "bouncy")
        if kk > 0: polyp(d, x, y + 4, 0.32 * min(1, kk), t + i, mood="happy", face_=False); n += 1
    ptag(d, t, at("host", 0.8), 540, 320, "红珊瑚", CORAL, 70, tc=WHITE)
    if t > at("host", 3): ptag(d, t, at("host", 3), 540, 440, "爬满了", GOLDP, 56)
def s_size(t, d):
    grad(d, (20, 50, 80), (8, 20, 40))
    # ruler
    k = popk(t, T["size"] + 0.1)
    polyp(d, 400, 1240, 3.0 * (0.5 + 0.5 * min(1, k)), t, mood="chill")
    x0 = 760
    d.rect(x0, 700, x0 + 80, 1250, fill=A((240, 230, 200), 1), r=8)
    for i in range(12):
        y = 1250 - i * 45; d.line([(x0, y), (x0 + (40 if i % 5 == 0 else 22), y)], A(NAVYT, 1), 4)
    d.text(x0 + 120, 1250 - 45 * 8, "8 mm", 40, A(WHITE, 1), anchor="lm", k=1)
    ptag(d, t, at("size", 0.6), 540, 330, "几毫米", GOLDP, 72)
    # tentacle counter
    tc_ = int(24 + 2 * pr(t, at("size", 3), at("size", 5)))
    if t > at("size", 2.6):
        kk = popk(t, at("size", 2.6))
        d.text(540, 480, f"{tc_ if tc_ < 26 else '24~26'} 根触手", int(64 * (0.7 + 0.3 * min(1, kk))), A(WHITE, ap(t, at("size", 2.6))), k=1)
def s_rov(t, d):
    deep(d, t, (10, 40, 70), DEEP2)
    caverock(d, t, 0.25)
    rov(d, 540, 420, 1.0, t)
    k = E.ease_in_out_sine(pr(t, at("rov", 1.5), at("rov", 5)))
    mx, my = lerp(540, 560, k), lerp(560, 1120, k)
    minirov(d, mx, my, 0.9, t, tx=540, ty=530)
    ptag(d, t, at("rov", 0.5), 540, 250, "太窄！", (255, 120, 90), 60)
    if k > 0.2: ptag(d, t, at("rov", 2.2), 820, my, "小的上", GOLDP, 40)
PX, PY = 470, 1260
def scene_cave(d, t, g=0.0, mood="happy", arm=0.0, rovon=True):
    deep(d, t, (4, 16, 34), (0, 4, 14), 0.6)
    glow_(d, PX, PY - 100, 700, GLOWC, 0.45 * g)
    caverock(d, t, 0.7, a=0.85)
    coral(d, 470, 1700, 0.75, t)
    polyp(d, PX, PY, 1.4, t, glow=g, mood=mood)
    if rovon:
        return minirov(d, 800, 830, 1.0, t, arm=arm)
def s_poke(t, d):
    arm = E.ease_in_out_sine(pr(t, at("poke", 0.5), at("poke", 3.6)))
    scene_cave(d, t, 0, "sus" if arm < 0.9 else "scared", arm=arm)
    title(d, t, at("poke", 0.4), "轻轻碰……", 340, 100, WHITE)
def s_flash(t, d):
    g = max(blink(t, T["flash"], 5, 0.4), 0.0)
    ex, ey = scene_cave(d, t, g, "scream" if g > 0.3 else "scared", arm=1 - pr(t, at("flash", 2), at("flash", 4)))
    zap(d, PX, PY - 170, t, T["flash"], GLOWC, 500)
    slamtxt(d, t, T["flash"], "啪！", 330, 170, GLOWC)
    if t > at("flash", 1.2): ptag(d, t, at("flash", 1.2), 540, 480, "闪 · 闪 · 闪", GLOW_L, 50)
def s_spread(t, d):
    deep(d, t, (4, 16, 34), (0, 4, 14), 0.6)
    pts = coral(d, 540, 1600, 1.2, t)
    src = None
    ps = [(x, y, dep) for x, y, dep in pts if dep >= 1]
    if ps: src = ps[len(ps) // 2]
    t0 = at("spread", 0.5)
    for i, (x, y, dep) in enumerate(ps):
        dist = math.hypot(x - src[0], y - src[1])
        tt0 = t0 + dist / 500
        g = blink(t, tt0, 3, 0.35)
        polyp(d, x, y + 4, 0.34, t + i, glow=g, face_=False)
    if t >= t0:
        u = (t - t0) * 500
        d.circ(src[0], src[1], u, outline=A(GLOWC, 0.6 * max(0, 1 - u / 900)), w=8)
    ptag(d, t, at("spread", 0.5), src[0], src[1] - 90, "碰这里", WHITE, 36)
    ptag(d, t, at("spread", 2.5), 540, 320, "往外传开", GLOWC, 70)
def s_first(t, d):
    deep(d, t, (4, 16, 34), (0, 4, 14))
    caverock(d, t, 0.5)
    for i, (x, y) in enumerate(((420, 1080), (640, 1020), (530, 1160))):
        polyp(d, x, y, 0.9, t + i, glow=blink((t - T["first"]) % 1.6 + 10, 10 + i * 0.25, 2, 0.4), face_=False)
    # camera frame / REC
    k = popk(t, at("first", 0.3))
    if k > 0:
        for (x, y, sx, sy) in ((230, 680, 1, 1), (850, 680, -1, 1), (230, 1220, 1, -1), (850, 1220, -1, -1)):
            d.line([(x, y + sy * 60), (x, y), (x + sx * 60, y)], A(WHITE, 0.85 * ap(t, at("first", 0.3))), 6)
        if int(t * 2) % 2 == 0: d.circ(265, 725, 12, fill=A((255, 60, 60), 1))
        d.text(290, 725, "REC  MiniROV", 30, A(WHITE, 0.95), anchor="lm", k=1)
    kk = popk(t, at("first", 3), "bouncy")
    if kk > 0:
        d.circ(540, 440, 150 * min(1, kk) + 10, fill=A(GOLD, 0.95))
        d.text(540, 415, "首次", int(84 * min(1, kk)), A(NAVYT, 1), k=1)
        d.text(540, 490, "记录", int(44 * min(1, kk)), A(NAVYT, 1), k=1)
    ptag(d, t, at("first", 1), 540, 250, "深海洞穴 · 生物发光", WHITE, 40)
def s_lab(t, d):
    grad(d, (30, 44, 64), (14, 22, 36))
    d.rect(140, 1200, 940, 1240, fill=A((80, 96, 120), 1), r=10)
    d.ell(540, 1150, 260, 60, A((140, 200, 230), 0.4)); d.ell(540, 1150, 260, 60, outline=A(WHITE, 0.6), w=5)
    t1, t2 = at("lab", 1), at("lab", 4)
    g = max(blink(t, t1 + 0.4, 3, 0.35), blink(t, t2 + 0.5, 3, 0.35))
    polyp(d, 540, 1150, 1.2, t, glow=g, mood="scared" if g > 0.2 else "chill")
    # tweezers
    u = pr(t, t1, t1 + 0.4) * (1 - pr(t, t1 + 1.2, t1 + 1.6))
    tx, ty = lerp(1000, 640, u), lerp(700, 980, u)
    d.line([(tx, ty), (tx + 260, ty - 300)], A(METAL, 1), 14); d.line([(tx + 20, ty - 4), (tx + 280, ty - 296)], A(METAL, 1), 14)
    ptag(d, t, t1, 760, 760, "镊子夹", WHITE, 42)
    # dropper
    v = pr(t, t2 - 0.5, t2) * (1 - pr(t, t2 + 1.4, t2 + 1.8))
    dx, dy = 400, lerp(300, 700, v)
    if v > 0:
        d.rect(dx - 22, dy - 200, dx + 22, dy, fill=A((220, 240, 255), 0.9), r=10); d.rect(dx - 34, dy - 260, dx + 34, dy - 190, fill=A((240, 80, 80), 1), r=20)
        tag(d, dx, dy - 300, "氯化钾", WHITE, v, 40)
        if t > t2:
            yy = dy + (t - t2) * 900
            if yy < 1120: d.circ(dx + 10, yy, 14, fill=A((180, 230, 255), 1))
    if g > 0.1: glow_(d, 540, 1000, 400, GLOWC, 0.4 * g)
    ptag(d, t, at("lab", 0.2), 540, 280, "实验室", GOLDP, 56)
def s_nm(t, d):
    grad(d, (16, 22, 40), (6, 10, 20))
    x0, x1, y = 200, 880, 980
    k = pr(t, T["nm"], at("nm", 1.2))
    cols = [(130, 60, 220), (60, 100, 255), (40, 200, 230), (60, 230, 90), (240, 230, 60), (255, 150, 40), (230, 50, 40)]
    for i in range(120):
        u = i / 119
        if u > k: break
        j = u * (len(cols) - 1); a0 = int(j); c = mix(cols[a0], cols[min(a0 + 1, len(cols) - 1)], j - a0)
        xx = lerp(x0, x1, u); d.rect(xx, y - 60, xx + (x1 - x0) / 119 + 1, y + 60, fill=A(c, 1))
    d.text(x0, y + 110, "400", 34, A(MUTE, 1), k=1); d.text(x1, y + 110, "700 nm", 34, A(MUTE, 1), k=1)
    xm = lerp(x0, x1, (515 - 400) / 300)
    km = popk(t, at("nm", 1.5), "bouncy")
    if km > 0:
        # bell-shaped emission curve
        pts = [(lerp(x0, x1, u), y - 80 - 360 * math.exp(-((lerp(400, 700, u) - 515) / 40) ** 2) * min(1, km)) for u in [i / 80 for i in range(81)]]
        d.line(pts, A(GLOWC, 1), 8)
        glow_(d, xm, y - 300, 220, GLOWC, 0.5 * min(1, km))
        arrow(d, xm, y - 520, xm, y - 460, WHITE, 1, 12)
    slamtxt(d, t, at("nm", 1.5), "515", 420, 180, GLOWC)
    ptag(d, t, at("nm", 3), 540, 560, "纳米 · 绿光", WHITE, 44)
def s_self(t, d):
    grad(d, (240, 200, 210), (210, 150, 170))
    cx_, cy_, R_ = 540, 860, 330
    k = popk(t, T["self"] + 0.05, "smooth")
    R2 = R_ * min(1, k)
    d.circ(cx_, cy_, R2 + 16, fill=A(WHITE, 1)); d.circ(cx_, cy_, R2, fill=A((250, 210, 230), 1))
    rnd_ = random.Random(4)
    if k > 0.5:
        for i in range(40):
            a_ = rnd_.uniform(0, 6.28); r_ = R_ * 0.85 * math.sqrt(rnd_.random())
            d.ell(cx_ + math.cos(a_) * r_, cy_ + math.sin(a_) * r_, 26, 18, A((200, 110, 170), 0.8))
            d.circ(cx_ + math.cos(a_) * r_, cy_ + math.sin(a_) * r_, 7, fill=A((110, 50, 120), 0.9))
    # magnifier sweeping
    u = pr(t, at("self", 1), at("self", 4))
    mx, my = cx_ - 150 + 300 * u, cy_ - 60 + 80 * math.sin(u * 6)
    if u > 0:
        d.circ(mx, my, 110, outline=A(NAVYT, 1), w=16); d.line([(mx + 80, my + 80), (mx + 190, my + 190)], A(NAVYT, 1), 26)
    kb = popk(t, at("self", 4.2))
    if kb > 0:
        tag(d, 540, 1300, "细菌？", WHITE, ap(t, at("self", 4.2)), 52)
        cross(d, 700, 1300, 50, pr(t, at("self", 4.6), at("self", 5)), (230, 50, 50))
    ptag(d, t, at("self", 0.3), 540, 330, "组织切片", NAVYT, 56, tc=WHITE)
def s_why(t, d):
    deep(d, t)
    coral(d, 540, 1500, 0.8, t)
    polyp(d, 540, 1100, 1.6, t, mood="chill", glow=0.3 + 0.3 * math.sin(t * 3))
    kk = popk(t, at("why", 0.2), "bouncy")
    if kk > 0: d.text(540, 480, "为啥？", int(170 * (0.6 + 0.4 * kk)), A(GLOWC, ap(t, at("why", 0.2))), k=1)
    if t > at("why", 2.5): ptag(d, t, at("why", 2.5), 540, 640, "论文的猜想", GOLD, 48)
def alarm_scene(d, t, t0, key):
    """thief approaches, polyp blinks, big fish arrives"""
    deep(d, t, (6, 22, 44), (0, 6, 18))
    floor(d, 1380)
    coral(d, 360, 1400, 0.8, t)
    g = blink(t, t0, 6, 0.38)
    polyp(d, 380, 1060, 1.1, t, glow=g, mood="scream" if g > 0.3 else "sus")
    return g
def s_alarm(t, d):
    t0 = at("alarm", 2)
    deep(d, t, (6, 22, 44), (0, 6, 18)); floor(d, 1150)
    coral(d, 360, 1170, 0.8, t)
    g = blink(t, t0, 8, 0.38)
    polyp(d, 380, 850, 1.1, t, glow=g, mood="scream" if g > 0.3 else "sus")
    cx_ = lerp(1000, 640, E.ease_out_cubic(pr(t, T["alarm"], t0)))
    thief(d, cx_, 1080, 1.0, t, scared=pr(t, at("alarm", 4), at("alarm", 5)))
    if t < t0 + 0.3: ptag(d, t, at("alarm", 0.6), cx_, 950, "嘿嘿", WHITE, 36)
    # siren lights
    if g > 0.05:
        for j in range(4):
            a_ = t * 4 + j * 1.57
            d.poly([(380, 680), (380 + math.cos(a_) * 900, 680 + math.sin(a_) * 900), (380 + math.cos(a_ + 0.25) * 900, 680 + math.sin(a_ + 0.25) * 900)], A(GLOWC, 0.12 * g))
    fx_ = lerp(1500, 900, E.ease_out_cubic(pr(t, at("alarm", 4), at("alarm", 6.5))))
    if fx_ < 1450: bigfish(d, fx_, 470, 0.8, t, eye_glow=g)
    stamp(d, t, t0, "防盗警报", 540, 330, 120, GLOWC)
def s_eat(t, d):
    deep(d, t, (6, 22, 44), (0, 6, 18)); floor(d, 1150)
    coral(d, 360, 1170, 0.8, t)
    polyp(d, 380, 850, 1.1, t, glow=0.25 + 0.2 * math.sin(t * 9), mood="happy")
    u = E.ease_in_out_sine(pr(t, at("eat", 0.5), at("eat", 2.5)))
    cx_ = lerp(640, 1250, u)
    thief(d, cx_, 1080 - 200 * u, 1.0, t, scared=1)
    if u < 0.9: ptag(d, t, at("eat", 0.3), cx_, 920 - 200 * u, "溜了溜了", WHITE, 36)
    bigfish(d, lerp(900, 1050, u), 470 + 260 * u, 0.8, t, mouth_=0.3 + 0.5 * u)
    ptag(d, t, at("eat", 2.8), 540, 330, "反被盯上", (255, 120, 90), 64)
def s_maybe(t, d):
    deep(d, t)
    polyp(d, 540, 1200, 1.7, t, mood="chill", glow=0.2)
    stamp(d, t, at("maybe", 0.3), "猜想", 540, 360, 150, (255, 150, 60))
    if t > at("maybe", 2): ptag(d, t, at("maybe", 2), 540, 520, "还没证实", WHITE, 56)
    for i, (x, y) in enumerate(((300, 760), (800, 700), (760, 900))):
        d.text(x, y + 12 * math.sin(t * 3 + i), "?", 90, A(GLOW_L, 0.45), k=1)
def s_card(t, d):
    grad(d, (20, 70, 70), (6, 28, 36))
    for i in range(12): d.circ(540, 860, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 660 * (0.8 + 0.2 * k), 920 * (0.8 + 0.2 * k); cx_, cy_ = 540, 840; a_ = ap(t, T["card"] + 0.1)
    glow_(d, cx_, cy_, 560, (200, 255, 220), 0.3 * a_)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((248, 248, 236), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 80, "一句话学会", GOLD, a_, 32)
    polyp(d, cx_, cy_ + 20, 0.9, t, glow=0.5 + 0.5 * math.sin(t * 5), mood="happy", a=a_)
    d.text(cx_, cy_ + 90, "碰一下就闪绿光的小触手", 38, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("住哪：385米深的洞口红珊瑚上", "怎么亮：自己发光，峰值515纳米", "为啥亮：可能是防盗警报（猜想）")):
        kk = popk(t, at("card", 1.2 + i * 0.8))
        if kk > 0: d.text(cx_, cy_ + 180 + i * 64, s_, 33, A((60, 70, 90), ap(t, at("card", 1.2 + i * 0.8))), k=1)
def s_top10(t, d):
    rays(d, t, (40, 120, 120), (10, 50, 60))
    polyp(d, 540, 1220, 1.8, t, glow=0.3, mood="proud")
    kk = popk(t, at("top10", 0.5), "bouncy")
    if kk > 0:
        x, y = 540, 640; s = min(1, kk)
        d.poly([(x - 120 * s, y - 120 * s), (x - 40 * s, y + 60 * s), (x - 90 * s, y + 70 * s)], A((80, 140, 230), 1))
        d.poly([(x + 120 * s, y - 120 * s), (x + 40 * s, y + 60 * s), (x + 90 * s, y + 70 * s)], A((230, 70, 70), 1))
        d.circ(x, y + 110 * s, 120 * s, fill=A(GOLD, 1)); d.circ(x, y + 110 * s, 92 * s, fill=A((255, 226, 120), 1))
        d.text(x, y + 110 * s, "TOP 10", int(46 * s), A(NAVYT, 1), k=1)
    ptag(d, t, at("top10", 2), 540, 330, "2025 十大海洋新物种", WHITE, 46)
    for i in range(10):
        u = ((t - T["top10"]) * 0.6 + i / 10) % 1
        d.rect(150 + i * 80, 200 + u * 1200, 166 + i * 80, 230 + u * 1200, fill=A([GOLD, GLOWC, CORAL, WHITE][i % 4], 0.8 * (1 - u)), r=4)
def s_end(t, d):
    deep(d, t, (4, 16, 34), (0, 4, 14), 0.6)
    t0 = at("end", 1.6)
    g = blink(t, t0, 3, 0.4)
    glow_(d, 540, 950, 700, GLOWC, 0.4 * g)
    coral(d, 540, 1600, 0.9, t)
    polyp(d, 540, 1200, 1.7, t, glow=g, mood="scream" if g > 0.3 else ("happy" if t > t0 + 1.2 else "sus"))
    u = pr(t, at("end", 0.5), t0) * (1 - pr(t, t0 + 0.1, t0 + 0.5))
    d.line([(1200, 700), (lerp(1200, 660, u), lerp(700, 960, u))], A(METAL, 1), 22)
    if t < t0: ptag(d, t, T["end"] + 0.05, 540, 300, "别乱戳", WHITE, 90)
    else: slamtxt(d, t, t0, "会报警！", 300, 130, GLOWC)
    ra = ap(t, at("end", 3.5), 0.3)
    if ra > 0:
        d.rect(170, 395, 910, 505, fill=A((10, 20, 34), 0.6 * ra), r=20)
        d.text(540, 428, "Kise 等 2025 · Royal Society Open Science", 25, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 472, "防盗警报为论文猜想，尚未证实", 25, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "闪绿光", "deep": "385米", "q": "发光", "reveal": "金色的", "notcoral": "不是珊瑚", "host": "红珊瑚", "size": "几毫米",
      "rov": "小机器人", "poke": "碰", "flash": "绿光", "spread": "传开", "first": "首次", "lab": "都会亮", "nm": "515纳米", "self": "自己",
      "why": "猜想", "alarm": "防盗警报", "eat": "大鱼", "maybe": "猜想", "top10": "十大", "end": "报警"}
def subs(t, d):
    for a, b, s, key in SUBS:
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
                    j = x.index(hw); parts = [(x[:j], WHITE), (hw, GOLDP if key not in ("flash", "hook", "nm") else GLOWC), (x[j + len(hw):], WHITE)]
                    xx = 540 - d.tlen(x, 54, 1) / 2
                    for p_, c_ in parts:
                        if p_: d.text(xx, yy, p_, 54, A(c_, al), anchor="lm", k=1); xx += d.tlen(p_, 54, 1)
                else: d.text(540, yy, x, 54, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇动物"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)

SF = {n: globals()["s_" + n] for n in NAMES}
SECS = [(-1, HOOKCUT, s_hook, "hook")] + [(T[n], nxt(n), SF[n], n) for n in NAMES[1:]]
SECS = [(a, (99 if i == len(SECS) - 1 else b), f, n) for i, (a, b, f, n) in enumerate(SECS)]
def cam(t):
    z = 1.0 + 0.04 * pulse(t, [HOOK_HIT, BIG2], 3)
    for a, b, f, n in SECS:
        if a <= t < b: z += 0.03 * eio(pr(t, max(a, 0), min(b, DUR))); break
    sx, sy = shake(t, 8 * pulse(t, [HOOK_HIT, BIG2], 5), 40)
    return z, 540 + sx, 900 + sy
def frame(t, fi=0):
    img = Image.new("RGB", (W, H), (6, 14, 30)); d = D(img); key = None
    for a, b, sf, n in SECS:
        if a <= t < b: sf(t, d); key = n; break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.5 * (1 - (t - c) / 0.1)))
    brand(t, d); subs(t, d)
    out = img.resize((OW, OH), Image.LANCZOS)
    out = E.vignette(out, 0.2); out = E.grain(out, 0.03, seed=fi)
    return out
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/gl_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/gl_sheet.png")
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
