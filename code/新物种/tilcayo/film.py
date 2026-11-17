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

def bubble_txt(d, t, t0, x, y, s, col, size=70, tail=-1):
    k = popk(t, t0, "bouncy")
    if k <= 0: return
    sz = int(size * min(1.1, k)); w = d.tlen(s, sz, 1) + 60
    d.rect(x - w / 2, y - sz * 0.85, x + w / 2, y + sz * 0.85, fill=A(WHITE, 0.97), r=sz * 0.6)
    d.poly([(x + tail * 30, y + sz * 0.7), (x + tail * 80, y + sz * 1.5), (x + tail * 70, y + sz * 0.7)], A(WHITE, 0.97))
    d.text(x, y, s, sz, A(col, 1), k=1)
# ---------------- scenes ----------------
def ramp(t, a, b): return E.ease_in_out_sine(pr(t, a, b))
def garden(d, t, top=(70, 120, 80), bot=(24, 50, 34), ground=1350):
    flatbg(d, top, bot, t, False)
    d.rect(0, ground, 1080, 1920, fill=A((70, 52, 40), 1))
    for i in range(10):
        rv = random.Random(i); d.circ(rv.uniform(0, 1080), ground + rv.uniform(20, 500), rv.uniform(10, 30), fill=A((90, 70, 52), 1))
def check(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 18 * s_, y), (x - 4 * s_, y + 14 * s_), (x + 20 * s_, y - 14 * s_)], A(WHITE, a), 8 * s_)
def xmark(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 15 * s_, y - 15 * s_), (x + 15 * s_, y + 15 * s_)], A(WHITE, a), 8 * s_); d.line([(x - 15 * s_, y + 15 * s_), (x + 15 * s_, y - 15 * s_)], A(WHITE, a), 8 * s_)
def heart(d, x, y, r, col, a=1.0):
    d.circ(x - r * 0.5, y - r * 0.2, r * 0.55, fill=A(col, a)); d.circ(x + r * 0.5, y - r * 0.2, r * 0.55, fill=A(col, a))
    d.poly([(x - r * 1.02, y - 0.05 * r), (x + r * 1.02, y - 0.05 * r), (x, y + r * 1.1)], A(col, a))
def puddle(d, x, y, w, a=1.0): d.ell(x, y, w, w * 0.18, A((90, 170, 240), 0.85 * a))
def arrow_up(d, x, y0, y1, col, a=1.0, w=14):
    d.line([(x, y0), (x, y1 + 30)], A(col, a), w); d.poly([(x - 34, y1 + 40), (x + 34, y1 + 40), (x, y1)], A(col, a))

def screen(d, *a, **k): pass
def jungle(d, t, top=(70, 150, 110), bot=(20, 60, 40)):
    flatbg(d, top, bot, t, False)
    for i, x in enumerate((90, 990, 200, 880)):
        tree(d, x, 1150 - (i % 2) * 120, 1.4 - 0.3 * (i // 2), 0.9, (30 + 20 * (i % 2), 100 + 20 * (i % 2), 60))
def s_hook(t, d):
    jungle(d, t)
    if t < 0.3: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - t / 0.3)))
    k = popk(t, 0.0, "bouncy")
    tigercat(d, 540, 860, 1.9 * min(1.05, max(0.3, k)), t, face="shock" if t < 1.2 else "happy")
    k2 = popk(t, 0.25, "bouncy")
    if k2 > 0: tag(d, 540, 420, "新野猫", GOLD, min(1, k2), 72)
    k3 = popk(t, 0.9, "bouncy")
    if k3 > 0: tag(d, 830, 560, "百年首个", (255, 90, 90), min(1, k3), 40, tc=WHITE)
def s_q(t, d):
    t0 = T["q"]
    flatbg(d, (250, 220, 170), (220, 170, 120), t, False)
    d.rect(180, 360, 460, 620, fill=A((150, 200, 240), 1), r=16); d.line([(320, 360), (320, 620)], A(WHITE, 1), 10)
    d.ell(540, 1080, 300, 70, A((200, 80, 90), 1))
    tigercat(d, 540, 870, 1.3, t)
    d.ell(830, 1070, 90, 30, A((90, 140, 220), 1)); d.ell(830, 1060, 70, 18, A((250, 240, 220), 1))
    ptag(d, t, t0 + 0.6, 540, 470 + 40, "家猫？", (90, 140, 220), 46, tc=WHITE)
    for i in range(2):
        hk = ap(t, t0 + 1.2 + i * 0.4, 0.2)
        if hk > 0: heart(d, 380 + i * 300, 640 - 20 * math.sin(t * 3 + i), 26, (255, 110, 140), hk)
def s_who(t, d):
    t0 = T["who"]
    flatbg(d, (240, 236, 226), (210, 204, 190), t, False)
    housecat(d, 330, 860, 1.25, t)
    tigercat(d, 760, 900, 1.0, t)
    e = ease(pr(t, t0 + 1.2, t0 + 2.0))
    if e > 0:
        d.line([(930, 1060), (930, 1060 - 340 * e)], A((255, 90, 90), 1), 8)
        if e >= 1: d.text(930, 680, "约45厘米", 34, A((255, 90, 90), 1), k=1)
    ptag(d, t, t0 + 0.2, 540, 420, "Leopardus tilcayo", NAVYT, 40, tc=WHITE)
    d.text(330, 1120, "家猫", 38, A(NAVYT, 1), k=1); d.text(760, 1120, "蒂尔卡约虎猫", 38, A(NAVYT, 1), k=1)
def s_sperm(t, d):
    t0 = T["sperm"]
    flatbg(d, (60, 110, 90), (20, 40, 34), t, False)
    d.rect(130, 600, 950, 1060, fill=A(WHITE, 0.12), r=30)
    d.text(540, 560, "Leopardus tigrinus", 40, A(WHITE, 1), k=1)
    for i in range(6):
        b = i % 2; bx = (320, 760)[b]; k = popk(t, t0 + 0.3 + i * 0.22, "bouncy")
        if k > 0: tigercat(d, bx - 100 + (i // 2) * 100, 760 + (i // 2 % 2) * 180, 0.45 * min(1, k), t + i, blink=False)
    ptag(d, t, t0 + 1.8, 540, 420, "曾经：都算同一种", (120, 200, 160), 38, tc=NAVYT)
def s_egg(t, d):
    t0 = T["egg"]
    dim = 1 - 0.45 * pr(t, SIL0, SIL0 + 0.15)
    flatbg(d, (40, 40, 70), (12, 12, 26), t, False)
    helix(d, 540, 780, 560, t, 0.5 * dim)
    tigercat(d, 540, 900, 1.1, t, a=dim, face="shock")
    k = popk(t, t0 + 0.4, "bouncy")
    if k > 0: d.text(800, 560, "?", int(200 * min(1, k)), A(GOLD, dim), k=1)
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (255, 200, 90), (230, 110, 50))
    if t > t0: sparks(d, 540, 820, t, t0, 30, 900, (255, 240, 200), 1, 3, 0.9)
    k = popk(t, t0 + 0.05, "bouncy")
    if k > 0:
        tigercat(d, 540, 900, 1.5 * min(1.05, k), t)
        check(d, 820, 560, 90, (80, 210, 120), 1, min(1, k))
        tag(d, 540, 430, "新物种", GOLD, min(1, k), 66)
def s_how(t, d):
    t0 = T["how"]
    flatbg(d, (236, 230, 250), (200, 190, 226), t, False)
    yr = int(1923 + (2026 - 1923) * ease(pr(t, t0 + 0.6, t0 + 2.2)))
    d.rect(300, 520, 780, 900, fill=A(WHITE, 1), r=30); d.rect(300, 520, 780, 610, fill=A((255, 90, 90), 1), r=30)
    d.text(540, 760, str(yr), 130, A(NAVYT, 1), k=1)
    ptag(d, t, t0 + 0.2, 540, 430, "上一次：1923 潘帕斯猫", (120, 90, 200), 36, tc=WHITE)
    k = popk(t, t0 + 2.3, "bouncy")
    if k > 0: tigercat(d, 860, 1060, 0.6 * min(1, k), t)
    ptag(d, t, t0 + 2.3, 400, 1060, "隔了约100年", (255, 90, 90), 36, tc=WHITE)
def s_xray(t, d):
    t0 = T["xray"]
    flatbg(d, (30, 50, 80), (10, 18, 34), t, False)
    n = int(38 * ease(pr(t, t0 + 0.3, t0 + 3.2)))
    for i in range(38):
        cx_, cy_ = 260 + (i % 7) * 93, 520 + (i // 7) * 100
        if i < n:
            if i in (2, 7, 12, 17, 22, 27, 32, 36): d.ell(cx_, cy_, 30, 24, A((236, 226, 200), 1)); d.circ(cx_ - 10, cy_ - 4, 6, fill=A(NOSE, 1)); d.circ(cx_ + 10, cy_ - 4, 6, fill=A(NOSE, 1))
            else: d.circ(cx_, cy_, 26, fill=A(TCF, 1)); d.circ(cx_, cy_, 8, fill=A(TCS, 1))
    ptag(d, t, t0 + 0.2, 540, 400, "全基因组 %d / 38" % n, GOLD, 40, tc=NAVYT)
    ptag(d, t, t0 + 2.0, 760, 1160, "白色=博物馆标本（8只）", (236, 226, 200), 30, tc=NAVYT)
def s_swim(t, d):
    t0 = T["swim"]
    flatbg(d, (60, 110, 90), (20, 40, 34), t, False)
    cols = [(255, 120, 90), (255, 200, 80), (120, 220, 140), (90, 180, 255), (220, 130, 255)]
    e = ease(pr(t, t0 + 0.4, t0 + 1.6))
    d.line([(540, 1180), (540, 980)], A(WHITE, 1), 10)
    for i, c in enumerate(cols):
        x = 540 + (i - 2) * 175 * e; y = 980 - 220 * e
        d.line([(540, 980), (x, y)], A(c, 1), 10)
        if e > 0.95:
            kk = popk(t, t0 + 1.6 + i * 0.12, "bouncy")
            if kk > 0: tigercat(d, x, y - 120, 0.38 * min(1, kk), t + i, col=c, blink=False)
    if e > 0.95: d.circ(540 + 2 * 175, 760, 92, fill=A(GOLD, 0.0))
    ptag(d, t, t0 + 1.0, 540, 420, "现在：5种", GOLD, 54, tc=NAVYT)
def s_gene(t, d):
    t0 = T["gene"]
    jungle(d, t, (110, 170, 200), (40, 90, 80))
    px = 300; d.circ(px, 700, 60, fill=A((150, 100, 70), 1)); d.rect(px - 80, 770, px + 80, 1060, fill=A((220, 90, 70), 1), r=40)
    d.circ(px - 20, 690, 7, fill=A(NOSE, 1)); d.circ(px + 20, 690, 7, fill=A(NOSE, 1)); d.arc(px, 715, 16, 10, 10, 170, A(NOSE, 1), 4)
    tigercat(d, 780, 900, 1.0, t)
    k = popk(t, t0 + 0.4, "bouncy")
    if k > 0: bubble_txt(d, t, t0 + 0.4, 430, 500, min(1, k), WHITE, 60, tail=-1) if False else (d.rect(250, 440, 610, 560, fill=A(WHITE, 1), r=40), d.text(430, 500, "tilcayo!", 56, A(NAVYT, 1), k=1))
    ptag(d, t, t0 + 1.8, 780, 1130, "L. tilcayo", GOLD, 40, tc=NAVYT)
def s_why(t, d):
    t0 = T["why"]
    flatbg(d, (250, 236, 220), (220, 200, 180), t, False)
    for i in range(2):
        k = popk(t, t0 + 0.3 + i * 0.35, "bouncy")
        if k > 0: tigercat(d, 360 + i * 300, 900, 0.9 * min(1, k), t + i * 1.3)
    k = popk(t, t0 + 0.2, "bouncy")
    if k > 0: d.text(540, 520, "2", int(220 * min(1, k)), A((255, 90, 90), 1), k=1)
    ptag(d, t, t0 + 1.6, 540, 1150, "📍玻利维亚 Yungas" if False else "只在玻利维亚 云雾林", (60, 140, 90), 36, tc=WHITE)
def s_order(t, d):
    t0 = T["order"]
    flatbg(d, (150, 200, 230), (90, 150, 120), t, False)
    hut(d, 300, 820, 1.0)
    tigercat(d, 300, 1000, 0.55, t)
    ptag(d, t, t0 + 0.2, 300, 520, "救助站", (200, 90, 70), 36, tc=WHITE)
    for i, x in enumerate((760, 900, 650)): tree(d, x, 900 + i * 30, 1.1, 1)
    xo = 780 + 120 * ease(pr(t, t0 + 1.4, t0 + 3.0))
    tigercat(d, xo, 1060, 0.5, t, a=1 - 0.6 * pr(t, t0 + 2.4, t0 + 3.2))
    ptag(d, t, t0 + 1.2, 790, 520, "放归山林", (60, 140, 90), 36, tc=WHITE)
def s_card(t, d):
    flatbg(d, (60, 110, 90), (16, 40, 30), t, False)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    tigercat(d, cx_, cy_ - 150, 0.55, t, a=a_)
    d.text(cx_, cy_ + 30, "蒂尔卡约虎猫：百年首个新野猫", 40, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("比家猫小，目前只见于玻利维亚", "全基因组确认是新种", "虎猫一共有5种")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 130 + i * 78, s_, 38, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    jungle(d, t)
    tigercat(d, 540, 940, 1.1, t)
    k = popk(t, t0 + 0.8, "bouncy")
    if k > 0:
        d.rect(640, 1000, 900, 1150, fill=A(WHITE, 1), r=16)
        d.text(770, 1040, "户口", 34, A(NAVYT, 1), k=1); d.text(770, 1100, "L. tilcayo", 26, A((255, 90, 90), 1), k=1)
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 285, "Lescroart et al. 2026", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 330, "Current Biology · Leopardus tilcayo", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "新野猫", "q": "家猫", "who": "小一圈", "sperm": "同一种", "egg": "新物种", "reveal": "是", "how": "1923年", "xray": "8只",
      "swim": "5种", "gene": "tilcayo", "why": "2只", "order": "放归山林", "end": "户口"}
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
    img = Image.new("RGB", (W, H), (20, 40, 30)); d = D(img); key = None
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/tc_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/tc_sheet.png")
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
