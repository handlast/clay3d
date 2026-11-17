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
def _unused_blink(t, t0, n=4, per=0.32):
    """blinking glow envelope: n flashes starting t0"""
    if t < t0: return 0.0
    u = (t - t0) / per; i = int(u)
    if i >= n: return 0.0
    f = u - i
    return math.exp(-f * 2.4) * (1 - 0.1 * i)
def zap(d, x, y, t, t0, col=WHITE, maxr=300, a=1.0):
    u = (t - t0) / 0.7
    if 0 <= u < 1:
        for j in range(3):
            rr_ = 30 + (u + j * 0.1) * maxr
            d.circ(x, y, rr_, outline=A(col, a * (1 - u) * (1 - j * 0.3)), w=10 - j * 3)

# ---------------- scenes ----------------
def ramp(t, a, b): return E.ease_in_out_sine(pr(t, a, b))
GY = 1000
BGS = {"teal": ((30, 120, 130), (12, 60, 72)), "plum": ((80, 40, 110), (30, 14, 50)), "navy": ((24, 34, 70), (8, 12, 28)),
       "red": ((150, 40, 60), (60, 14, 26)), "snow": ((90, 130, 180), (40, 60, 100)), "lab": ((30, 70, 90), (10, 26, 36)), "gold": ((170, 110, 30), (80, 46, 10))}
def bg(d, t, k, deco=True): flatbg(d, BGS[k][0], BGS[k][1], t, deco)
def ground(d, col=(255, 255, 255), a=0.10): d.rect(0, GY + 150, 1080, 1920, fill=A(col, a))
def check(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 18 * s_, y), (x - 4 * s_, y + 14 * s_), (x + 20 * s_, y - 14 * s_)], A(WHITE, a), 8 * s_)
def xmark(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 15 * s_, y - 15 * s_), (x + 15 * s_, y + 15 * s_)], A(WHITE, a), 8 * s_); d.line([(x - 15 * s_, y + 15 * s_), (x + 15 * s_, y - 15 * s_)], A(WHITE, a), 8 * s_)
def heart(d, x, y, r, col, a=1.0):
    if r <= 0: return
    d.circ(x - r * 0.5, y - r * 0.2, r * 0.58, fill=A(col, a)); d.circ(x + r * 0.5, y - r * 0.2, r * 0.58, fill=A(col, a))
    d.poly([(x - r * 1.05, y), (x + r * 1.05, y), (x, y + r * 1.1)], A(col, a))
NEU = [(math.cos(i * 2.4) * (30 + 24 * math.sqrt(i)), math.sin(i * 2.4) * (30 + 24 * math.sqrt(i)) * 0.75) for i in range(22)]
def bubble(d, t, cx, cy, s, offk, a=1.0, col=MAG, pop_t0=None):
    """thought-bubble 'brain window': dark circle full of glowing neurons; offk 0..1 switches them off one by one"""
    d.circ(cx, cy, 200 * s, fill=A((255, 255, 255), 0.95 * a)); d.circ(cx, cy, 182 * s, fill=A((34, 24, 60), a))
    n = len(NEU)
    for i, (nx, ny) in enumerate(NEU):
        on = cl((offk * n - i) * -1 + 1) if False else (0.0 if i < offk * n else 1.0)
        neuron(d, cx + nx * s, cy + ny * s, 12 * s, col, a, t, on)
def switch(d, x, y, s, on, col, a=1.0, label=None):
    """toggle switch: on in [0,1]"""
    d.rect(x - 130 * s, y - 60 * s, x + 130 * s, y + 60 * s, fill=A(mix((70, 74, 96), col, on), a), r=60 * s)
    kx = x + lerp(-70, 70, on) * s
    d.circ(kx, y, 48 * s, fill=A(WHITE, a))
    if label: d.text(x, y - 150 * s, label, int(64 * s), A(WHITE, a), k=1)
def s_hook(t, d):
    bg(d, t, "plum")
    ground(d)
    k = ramp(t, 1.0, 3.6)
    sq = 1 + 0.06 * math.sin(pr(t, 2.2, 2.5) * math.pi)
    fox(d, 500, GY, 1.15 * sq, t, tame=k, mood="angry" if k < 0.5 else "happy", wag=t * 3 * k)
    if 2.2 <= t < 2.5: sparks(d, 640, GY - 80, t, 2.2, 24, 700, WHITE, 0.9, 2, 0.5)
    bubble(d, t, 720, 600, 0.8, k * 0.6)
    for j in range(3): d.circ(590 - j * 40, 780 + j * 40, (22 - j * 6), fill=A(WHITE, 0.95))
    # count down chip
    if t < 1.4: slamtxt(d, t, -0.2, "少了！", 300, 150, GOLD)
def s_q(t, d):
    bg(d, t, "plum")
    z = ramp(t, T["q"], T["q"] + 0.6)
    bubble(d, t, lerp(720, 540, z), lerp(600, 720, z), lerp(0.8, 2.2, z), 0.6)
    for i in range(3):
        kk = popk(t, T["q"] + 0.4 + i * 0.15)
        nx, ny = NEU[i * 4 + 1]
        if kk > 0: d.text(540 + nx * 2.2, 720 + ny * 2.2 - 50, "?", int(90 * min(1, kk)), A(GOLD, 1), k=1)
def s_reveal(t, d):
    rays(d, t, (255, 90, 110), (120, 20, 50))
    k = popk(t, BIG2, "bouncy")
    off = ramp(t, BIG2 + 0.6, BIG2 + 1.0)
    if k > 0:
        neuron(d, 540, 520, 100 * min(1.05, k), MEAN, 1, t, 1 - 0.5 * off)
        switch(d, 540, 1000, 1.1 * min(1, k), 1 - off, MEAN, 1, "攻击")
    if t > BIG2 + 0.6: zap(d, 540, 1000, t, BIG2 + 0.6, WHITE, 260, 0.9)
    if t > BIG2 + 0.25: sparks(d, 540, 520, t, BIG2 + 0.25, 50, 1200, (255, 200, 120), 1, 7, 1.0)
def s_y1959(t, d):
    bg(d, t, "snow", False)
    t0 = T["y1959"]
    for i in range(34):
        sx = (i * 97 + 30 * math.sin(t + i)) % 1080; sy = (i * 211 + t * 120) % 1600 + 200
        d.circ(sx, sy, 4 + i % 4, fill=A(WHITE, 0.7))
    d.rect(0, GY + 150, 1080, 1920, fill=A(WHITE, 0.9))
    # flip counter 2026 -> 1959 (rolling)
    u = E.ease_out_cubic(pr(t, t0, t0 + 1.0)) if hasattr(E, "ease_out_cubic") else ease(pr(t, t0, t0 + 1.0))
    yr = int(round(lerp(2026, 1959, u)))
    d.rect(300, 330, 780, 560, fill=A((250, 248, 240), 1), r=30); d.rect(300, 330, 780, 380, fill=A(MEAN, 1), r=30); d.rect(300, 360, 780, 380, fill=A(MEAN, 1))
    d.text(540, 470, str(yr), 150, A(NAVYT, 1), k=1)
    # cages slide in
    sl = E.ease_out_cubic(pr(t, t0 + 0.6, t0 + 1.4)) if hasattr(E, "ease_out_cubic") else ease(pr(t, t0 + 0.6, t0 + 1.4))
    for i in range(3):
        x0 = 150 + i * 270 + (1 - sl) * 1100
        d.rect(x0, GY - 140, x0 + 240, GY + 150, fill=A((60, 80, 110), 1), r=16)
        fox(d, x0 + 120, GY + 50, 0.42, t + i, tame=0, mood="angry" if i != 1 else "neutral", flip=1 if i % 2 == 0 else -1, bob=0.4)
        for j in range(7): d.rect(x0 + 14 + j * 34, GY - 130, x0 + 22 + j * 34, GY + 140, fill=A((170, 190, 220), 0.9))
    ptag(d, t, t0 + 1.2, 540, 640, "西伯利亚 · 狐狸养殖场", (90, 200, 255), 46)
def s_pick(t, d):
    bg(d, t, "teal")
    ground(d)
    t0 = T["pick"]
    xs = [210, 430, 650, 870]; good = [False, True, False, True]
    hand_i = min(3, int(pr(t, t0, t0 + 1.6) * 4))
    for i, x in enumerate(xs):
        seen = t > t0 + i * 0.4 + 0.2
        mood = ("happy" if good[i] else "angry") if seen else "neutral"
        slide_ = ramp(t, t0 + 1.9, t0 + 2.4) if good[i] else 0
        tx = lerp(x, 400 if i == 1 else 700, slide_)
        al = 1 - 0.7 * ramp(t, t0 + 1.9, t0 + 2.2) * (not good[i])
        fox(d, tx, GY, 0.4, t + i, tame=0.1, mood=mood, a=al, flip=-1 if (i == 3 and slide_ > 0.5) else 1, bob=0.5)
        if seen:
            kk = popk(t, t0 + i * 0.4 + 0.2)
            (check if good[i] else xmark)(d, x, GY - 200, 40, MINT if good[i] else MEAN, al, kk)
    # hand probing each cage
    if t < t0 + 1.8:
        hx = xs[hand_i] + 70; hy = GY - 110 + 20 * math.sin(t * 12)
        d.rect(hx, hy - 30, hx + 600, hy + 30, fill=A((80, 140, 220), 1), r=30); d.ell(hx, hy, 55, 40, A((250, 205, 170), 1))
    hk = popk(t, t0 + 2.5)
    heart(d, 540, GY - 330, 70 * min(1, hk), PINK)
def s_six(t, d):
    bg(d, t, "gold")
    t0 = T["six"]
    # family tree: 6 generations stacked; each pup tamer
    for g in range(6):
        tg = t0 + g * 0.35
        kk = popk(t, tg)
        if kk <= 0: continue
        y = 330 + g * 125; x = 330 + (g % 2) * 60
        if g: d.line([(330 + ((g - 1) % 2) * 60, y - 80), (x, y - 30)], A(WHITE, 0.5), 5)
        fox(d, x, y, 0.3 * min(1, kk), t + g, tame=g / 5, mood="happy" if g >= 3 else ("angry" if g == 0 else "neutral"), wag=t * 3, bob=0.3)
        d.text(150, y, "%d代" % (g + 1), 40, A(WHITE, 0.9), k=1)
        # tameness meter
        d.rect(560, y - 14, 900, y + 14, fill=A((0, 0, 0), 0.2), r=14)
        d.rect(560, y - 14, 560 + 340 * (0.12 + 0.88 * g / 5) * min(1, kk), y + 14, fill=A(PINK, 1), r=14)
    # last pup runs to a hand
    if t > t0 + 2.4:
        u = ramp(t, t0 + 2.4, t0 + 3.4)
        fox(d, lerp(390, 700, u), 1140, 0.5, t, tame=1, mood="happy", wag=t * 6, bob=1.5)
        d.ell(860, 1080, 60, 40, A((250, 205, 170), 1)); d.rect(860, 1050, 1200, 1110, fill=A((80, 140, 220), 1), r=30)
        if u > 0.95: heart(d, 760, 960, 40 * popk(t, t0 + 3.4), PINK)
    ptag(d, t, t0 + 0.2, 730, 260, "亲人度", PINK, 36)
def s_look(t, d):
    bg(d, t, "teal")
    ground(d)
    t0 = T["look"]; b = BEAT
    ek = ramp(t, t0 + 0.2, t0 + 0.9); sk = ramp(t, t0 + 1.4, t0 + 2.0); ck = ramp(t, t0 + 2.5, t0 + 3.3)
    fox(d, 520, GY, 1.35, t, ears=ek, snout=sk, curl=ck, mood="happy", wag=t * 3)
    hx, hy = 520 + 168 * 1.35, GY + (-72) * 1.35
    focus = [(hx - 20, hy - 70, t0 + 0.1, t0 + 1.2, "耳朵耷拉"), (hx + 130, hy + 20, t0 + 1.3, t0 + 2.3, "嘴变短"), (520 - 260, GY - 120, t0 + 2.4, t0 + 9, "尾巴卷")]
    for i, (fx_, fy_, a0, a1, lab) in enumerate(focus):
        w = win(t, a0, a1, 0.2, 0.2) if i < 2 else ap(t, a0, 0.2)
        if w > 0:
            d.circ(fx_, fy_, 150, outline=A(GOLD, w), w=10)
            tag(d, fx_, fy_ - 190 if i < 2 else fy_ - 210, lab, GOLD, w, 46)
        if t > a1 and i < 2: check(d, 220 + i * 120, 330, 30, MINT, 1, popk(t, a1))
    if t > t0 + 3.3: check(d, 460, 330, 30, MINT, 1, popk(t, t0 + 3.3))
def s_mean(t, d):
    t0 = T["mean"]
    bg(d, t, "teal", False)
    d.rect(540, 0, 1080, 1920, fill=A((150, 40, 60), 1))
    d.rect(530, 220, 550, 1250, fill=A(WHITE, 0.9))
    fox(d, 270, GY, 0.7, t, tame=1, mood="happy", wag=t * 4)
    lun = max(0, math.sin((t - t0) * 7)) * 40 * ap(t, t0 + 0.4, 0.2)
    fox(d, 880, GY, 0.7, t, tame=0, mood="angry", flip=-1, lunge=lun)
    for j in range(5): d.rect(600 + j * 20, GY - 220, 606 + j * 20, GY + 150, fill=A((220, 220, 230), 0.8)) if False else None
    for j in range(4): d.rect(610 + j * 30, GY - 200, 618 + j * 30, GY + 150, fill=A((230, 230, 240), 0.9))
    if lun > 30: sparks(d, 640, GY - 60, t, t - 0.05, 8, 500, WHITE, 0.8, int(t * 10), 0.3)
    ptag(d, t, t0 + 0.1, 290, 560, "亲人组", TAME, 48)
    ptag(d, t, t0 + 0.4, 800, 560, "凶狐狸组", WHITE, 48, MEAN)
def s_nine(t, d):
    bg(d, t, "lab")
    t0 = T["nine"]
    labs = (("温顺", TAME, 1.0, "happy"), ("凶", MEAN, 0.0, "angry"), ("野生", MINT, 0.0, "neutral"))
    for r_, (lab, c, tm, md) in enumerate(labs):
        x = 220 + r_ * 320
        fox(d, x, 470, 0.38, t + r_, tame=tm, mood=md, bob=0.3)
        d.rect(x - 130, 980, x + 130, 1140, fill=A(c, 0.25), r=24)
        tag(d, x, 1180, lab, c, 1, 40)
        for j in range(3):
            td = t0 + 0.3 + r_ * 0.35 + j * 0.15
            u = pr(t, td, td + 0.45)
            if u <= 0: continue
            yy = lerp(560, 1050, u * u); xx = x + (j - 1) * 80
            brain(d, xx, yy, 0.17, 1, mix((255, 180, 200), c, 0.35), mix((230, 140, 170), c, 0.35))
    kn = popk(t, t0 + 1.9, "heavy")
    if kn > 0: d.text(540, 300, "9", int(150 * min(1.05, kn)), A(GOLD, 1), k=1)
def s_slice(t, d):
    bg(d, t, "navy")
    t0 = T["slice"]; cx, cy = 540, 700
    k = ramp(t, t0 + 0.1, t0 + 1.0)
    f = ramp(t, t0 + 1.0, t0 + 1.5)
    if f <= 0:
        brain(d, cx, cy, 1.2, 1)
        bx = 140 + 800 * k
        d.rect(bx - 5, cy - 300, bx + 5, cy + 300, fill=A(WHITE, 1)); glow(d, bx, cy, 110, CYAN2, 0.7)
        for i in range(1, 7):
            lx = 140 + i * 115
            if lx < bx: d.line([(lx, cy - 220), (lx, cy + 220)], A((60, 40, 80), 0.6), 4)
    else:
        z = ramp(t, t0 + 1.6, t0 + 2.1)
        for i in range(6):
            ox = (i - 2.5) * 140 * f
            if i == 2 and z > 0: continue
            d.rect(cx + ox - 48, cy - 220, cx + ox + 48, cy + 220, fill=A((255, 200, 215), 0.95 * (1 - 0.6 * z)), r=40)
        if z > 0:
            w = lerp(96, 560, z); h = lerp(440, 760, z); x0 = lerp(cx - 70 - 140 * 0.5, cx, z)
            d.rect(x0 - w / 2, cy - h / 2, x0 + w / 2, cy + h / 2, fill=A((255, 200, 215), 1), r=40)
            g = ap(t, t0 + 2.1, 0.5)
            if g > 0:
                rv = random.Random(5)
                for i in range(46):
                    sx = cx + rv.uniform(-230, 230); sy = cy + rv.uniform(-330, 330)
                    c = [MAG, CYAN2, MINT][i % 3]
                    gi = ap(t, t0 + 2.1 + i * 0.02, 0.15)
                    glow(d, sx, sy, 34, c, gi, 5); d.circ(sx, sy, 10, fill=A(c, gi)); d.circ(sx, sy, 4, fill=A(WHITE, gi))
def s_where(t, d):
    bg(d, t, "navy")
    t0 = T["where"]
    z = ramp(t, t0, t0 + 1.2)
    s = lerp(1.0, 2.0, z); cx, cy = lerp(540, 600, z), lerp(700, 560, z)
    # fox head silhouette fades as we dive in
    if z < 0.6:
        fox(d, 300, 1000, 1.5, t, tame=1, mood="happy", a=0.35 * (1 - z / 0.6), bob=0)
    brain(d, cx, cy, s, 1)
    tx, ty = cx + 10 * s, cy + 55 * s
    # reticle closing in
    rk = ramp(t, t0 + 0.8, t0 + 1.6)
    r = lerp(300, 70, rk)
    d.circ(tx, ty, r, outline=A(GOLD, 1), w=8)
    for an in range(4):
        a_ = an * math.pi / 2
        d.line([(tx + math.cos(a_) * (r - 30), ty + math.sin(a_) * (r - 30)), (tx + math.cos(a_) * (r + 40), ty + math.sin(a_) * (r + 40))], A(GOLD, 1), 8)
    if rk >= 1:
        lk = popk(t, t0 + 1.6)
        d.circ(tx, ty, 36 * min(1, lk), fill=A(GOLD, 1)); glow(d, tx, ty, 120, GOLD, 0.7)
        rings(d, tx, ty, t, [t0 + 1.6], GOLD, 0.8, 260)
        ptag(d, t, t0 + 1.7, 540, 1110, "下丘脑腹内侧", GOLD, 54)
def s_mouse(t, d):
    bg(d, t, "lab")
    ground(d)
    t0 = T["mouse"]
    mouse(d, 430, GY + 70, 1.4, t)
    hx, hy = 430 + 30 * 1.4, GY + 70 - 50 * 1.4
    d.line([(hx, 220), (hx, hy - 30)], A((200, 210, 230), 0.9), 8)
    # light pulses travel down the fibre
    lit = 0.0
    for p in range(4):
        tp = t0 + 0.6 + p * 0.9
        u = pr(t, tp, tp + 0.45)
        if 0 < u < 1:
            yy = lerp(220, hy - 30, u); glow(d, hx, yy, 50, CYAN2, 0.9); d.circ(hx, yy, 14, fill=A(WHITE, 1))
        if t > tp + 0.45: lit = max(lit, 1 - pr(t, tp + 0.45, tp + 0.95) * 0.5)
    # inset: neurons in the mouse brain lighting up
    d.circ(780, 520, 190, fill=A((20, 24, 46), 1)); d.circ(780, 520, 190, outline=A(CYAN2, 0.7), w=6)
    d.line([(hx + 20, hy - 20), (640, 640)], A(CYAN2, 0.5), 4)
    rv = random.Random(3)
    for i in range(9):
        nx = 780 + rv.uniform(-120, 120); ny = 520 + rv.uniform(-120, 120)
        neuron(d, nx, ny, 16, CYAN2, 1, t, lit * (1 if i % 3 else 0.3))
    ptag(d, t, t0 + 0.3, 780, 270, "ERα 神经元", CYAN2, 40)
    if lit > 0.5: tag(d, 780, 770, "点亮！", CYAN2, 1, 44)
def s_attack(t, d):
    bg(d, t, "red")
    ground(d)
    t0 = T["attack"]
    u = E.ease_in_cubic(pr(t, t0 + 0.2, t0 + 0.6)) if hasattr(E, "ease_in_cubic") else pr(t, t0 + 0.2, t0 + 0.6) ** 3
    mouse(d, 300 + 320 * u, GY + 70, 1.2, t, "angry", col=(255, 190, 200))
    hop = 80 * math.sin(pr(t, t0 + 0.6, t0 + 1.1) * math.pi)
    mouse(d, 860 + 60 * pr(t, t0 + 0.6, t0 + 1.0), GY + 70 - hop, 1.0, t, "neutral", flip=-1)
    for i in range(3):  # speed lines
        if 0.05 < u < 0.99: d.line([(200, GY + 20 + i * 40), (300 + 320 * u - 120, GY + 20 + i * 40)], A(WHITE, 0.6), 6)
    if u >= 1: zap(d, 760, GY + 30, t, t0 + 0.6, WHITE, 300, 1); stamp(d, t, t0 + 0.65, "扑！", 540, 480, 150, GOLD)
def s_result(t, d):
    bg(d, t, "navy")
    t0 = T["result"]
    tag(d, 900, 260, "示意", WHITE, 0.5, 26)
    for i, (lab, c, n, x, md, tm) in enumerate((("凶狐狸", MEAN, 24, 300, "angry", 0), ("温顺狐狸", TAME, 13, 780, "happy", 1))):
        fox(d, x, 470, 0.36, t, tame=tm, mood=md, bob=0.2, flip=1 if i == 0 else -1)
        tag(d, x, 640, lab, c, 1, 40)
        d.rect(x - 200, 700, x + 200, 1180, fill=A((255, 255, 255), 0.06), r=30)
        rv = random.Random(11)
        cnt = int(n * ramp(t, t0 + 0.3, t0 + 2.0))
        for j in range(cnt):
            col_, row_ = j % 6, j // 6
            neuron(d, x - 150 + col_ * 60, 770 + row_ * 90, 15, MAG, 1, t, 1)
    if t > t0 + 2.2:
        k = popk(t, t0 + 2.2)
        d.text(540, 960, "<", int(120 * min(1, k)), A(GOLD, 1), k=1) if False else tag(d, 780, 1060, "更少", GOLD, min(1, k), 50)
def s_sub(t, d):
    bg(d, t, "plum")
    t0 = T["sub"]
    tag(d, 900, 260, "示意", WHITE, 0.5, 26)
    # stacked blocks: cyan = other subtypes, magenta = aggression-linked subtype
    for i, (lab, nm, x) in enumerate((("凶狐狸", 6, 330), ("温顺狐狸", 2, 750))):
        tag(d, x, 1130, lab, MEAN if i == 0 else TAME, 1, 40)
        blocks = [CYAN2] * 5 + [MAG] * nm
        for j, c in enumerate(blocks):
            td = t0 + 0.2 + j * 0.12
            u = pr(t, td, td + 0.3)
            if u <= 0: continue
            yy = lerp(200, 1040 - j * 54, E.ease_out_bounce(u) if hasattr(E, "ease_out_bounce") else ease(u))
            d.rect(x - 110, yy - 24, x + 110, yy + 24, fill=A(c, 1), r=12)
            if c == MAG: glow(d, x, yy, 80, MAG, 0.25)
    k = ap(t, t0 + 1.8, 0.3)
    if k > 0:
        d.circ(130 + 0, 0, 0)
        tag(d, 540, 330, "其他类型：没明显变", CYAN2, k, 40)
        tag(d, 540, 410, "攻击相关型：变少", MAG, ap(t, t0 + 2.4, 0.3), 40)
def s_caution(t, d):
    bg(d, t, "navy")
    t0 = T["caution"]
    for j in range(9):
        kk = popk(t, t0 + 0.1 + j * 0.06)
        if kk > 0: brain(d, 300 + (j % 3) * 240, 330 + (j // 3) * 110, 0.2 * min(1, kk), 1)
    # correlation vs causation diagram
    a1 = ap(t, t0 + 1.0, 0.3)
    if a1 > 0:
        neuron(d, 290, 900, 50, MAG, a1, t, 0.6)
        fox(d, 790, 960, 0.4, t, tame=1, mood="happy", a=a1, bob=0.3, flip=-1)
        tag(d, 290, 1040, "细胞少", MAG, a1, 38); tag(d, 790, 1040, "更温顺", TAME, a1, 38)
    a2 = ap(t, t0 + 1.6, 0.3)
    if a2 > 0:
        for i in range(8):
            x0 = 380 + i * 40
            d.line([(x0, 900), (x0 + 20, 900)], A(WHITE, a2), 8)
        tag(d, 540, 840, "相关 ✓" if False else "相关", MINT, a2, 40)
    a3 = ap(t, t0 + 2.6, 0.3)
    if a3 > 0:
        arrow(d, 360, 980, 710, 980, GOLD, a3, 10)
        xmark(d, 535, 980, 36, MEAN, 1, popk(t, t0 + 3.0))
        tag(d, 540, 1100, "因果？未证明", GOLD, a3, 40)
def s_card(t, d):
    bg(d, t, "plum", False)
    for i in range(12): d.circ(540, 820, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 700 * (0.8 + 0.2 * k), 880 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    fox(d, cx_ - 30, cy_ - 140, 0.45, t, tame=1, mood="happy", a=a_, wag=t * 3, bob=0.3)
    d.text(cx_, cy_ + 50, "温顺狐狸：攻击相关细胞更少", 46, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("位置：下丘脑腹内侧", "小鼠里点亮这类细胞就会攻击", "只是相关，还没证明因果")):
        kk = ap(t, at("card", 1.0 + i * 1.4), 0.25)
        if kk > 0: d.text(cx_, cy_ + 160 + i * 76, s_, 40, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    bg(d, t, "gold")
    ground(d)
    t0 = T["end"]
    fox(d, 400, GY, 1.2, t, tame=1, mood="happy", wag=t * 4)
    on = 1 - ramp(t, t0 + 0.8, t0 + 1.2)
    switch(d, 760, 620, 0.9, on, MEAN, 1, "攻击开关")
    if t > t0 + 1.2: sparks(d, 760, 620, t, t0 + 1.2, 30, 700, WHITE, 0.9, 9, 0.8)
    ra = ap(t, t0 + 2.4, 0.3)
    if ra > 0:
        d.rect(170, 250, 910, 360, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 283, "Klein 等 2026 · Current Biology", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 327, "9 颗狐狸脑的比较 · 相关性研究", 25, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "少了一类细胞", "q": "哪一类", "reveal": "攻击", "y1959": "1959年", "pick": "最亲人", "six": "主动找人", "look": "尾巴卷",
      "mean": "最凶", "nine": "9颗脑", "slice": "荧光", "where": "下丘脑腹内侧", "mouse": "雌激素受体α神经元", "attack": "立刻", "result": "少",
      "sub": "攻击相关", "caution": "还没证明", "end": "少装几个"}
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
                    j = x.index(hw); parts = [(x[:j], WHITE), (hw, GOLD), (x[j + len(hw):], WHITE)]
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
    img = Image.new("RGB", (W, H), (6, 20, 40)); d = D(img); key = None
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/fx_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/fx_sheet.png")
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
