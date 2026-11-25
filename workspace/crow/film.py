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

def screen(d, cx, cy, w, h, t, coh=0.5, dirn=1, a=1.0, targets=True, hit=None):
    d.rect(cx - w / 2 - 16, cy - h / 2 - 16, cx + w / 2 + 16, cy + h / 2 + 16, fill=A((70, 74, 92), a), r=24)
    d.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=A((8, 10, 18), a), r=10)
    dots(d, cx, cy, w - 120, h - 40, t, coh, dirn, a=a)
    if targets:
        for sx in (-1, 1):
            col = MINT if hit == sx else (200, 200, 210)
            d.circ(cx + sx * (w / 2 - 36), cy, 24, fill=A(col, a))
def timer(d, x, y, val, col, a=1.0, size=96):
    d.text(x, y, val, size, A(col, a), k=1)
def bar(d, x, y, w, frac, col, lab, val, a=1.0):
    d.rect(x, y, x + w, y + 64, fill=A((40, 44, 60), 0.7 * a), r=16)
    d.rect(x, y, x + max(20, w * frac), y + 64, fill=A(col, a), r=16)
    d.text(x - 90, y + 32, lab, 40, A(WHITE, a), k=1); d.text(x + w - 120, y - 32, val, 44, A(col, a), k=1)

def s_hook(t, d):
    rays(d, t, (255, 190, 90), (230, 120, 60))
    crow(d, 420, 900, 2.4, t, glasses=True, head=-0.15)
    k = popk(t, 0.05, "bouncy")
    if k > 0: tag(d, 760, 560, "0.235秒", MINT, min(1, k), 64)
    human(d, 830, 1000, 0.8, t, load=1.0)
def s_q(t, d):
    t0 = T["q"]
    flatbg(d, (60, 70, 110), (20, 24, 44), t, False)
    screen(d, 540, 700, 640, 440, t, 0.35, 1)
    crow(d, 380, 1150, 1.6, t, head=-0.4)
    el = min(0.235, max(0, (t - t0 - 0.6) * 0.235 / 0.8))
    timer(d, 760, 1060, f"{el:.3f}秒", GOLD, ap(t, t0 + 0.4))
    if t > t0 + 1.4: check(d, 760, 1180, 40, MINT, 1, popk(t, t0 + 1.4))
def s_who(t, d):
    t0 = T["who"]
    flatbg(d, (120, 170, 220), (70, 120, 180), t, False)
    k1, k2 = popk(t, t0), popk(t, t0 + 0.5)
    if k1 > 0: crow(d, 330, 950, 1.5 * min(1, k1), t, head=-0.1); tag(d, 330, 1180, "Iggy", CRW_H, min(1, k1), 44)
    if k2 > 0: crow(d, 760, 950, 1.5 * min(1, k2), t, head=-0.1, flip=True); tag(d, 760, 1180, "Lemmy", CRW_H, min(1, k2), 44)
    ptag(d, t, t0 + 1.0, 540, 560, "小嘴乌鸦 Corvus corone", CRW_H, 40)
    ptag(d, t, t0 + 1.8, 540, 660, "德国图宾根大学实验室", WHITE, 34)
def s_sperm(t, d):
    t0 = T["sperm"]
    flatbg(d, (60, 70, 110), (20, 24, 44), t, False)
    hit = 1 if t > t0 + 2.0 else None
    screen(d, 540, 640, 640, 420, t, 0.8, 1, hit=hit)
    pk = ease(pr(t, t0 + 1.4, t0 + 2.0)) * (1 - ease(pr(t, t0 + 2.3, t0 + 2.8)))
    crow(d, 400, 1120, 1.5, t, head=-0.5, peck=pk)
    arrow = ap(t, t0 + 0.6)
    if arrow > 0: d.line([(420, 640), (680, 640)], A(GOLD, arrow), 10); d.poly([(680, 615), (720, 640), (680, 665)], A(GOLD, arrow))
    k = popk(t, t0 + 2.2, "bouncy")
    if k > 0:  # mealworm
        d.line([(780 + 12 * math.sin(t * 8 + i * 0.5), 1060 - i * 6) for i in range(10)], A((235, 200, 120), 1), 22 * min(1, k))
        tag(d, 800, 960, "奖励：面包虫", GOLD, min(1, k), 34)
def s_egg(t, d):
    t0 = T["egg"]
    flatbg(d, (240, 200, 120), (210, 140, 80), t, False)
    dim = 1 - 0.6 * pr(t, SIL0, SIL0 + 0.1)
    human(d, 330, 950, 1.2, t, a=dim, load=1.0 * dim)
    monkey(d, 760, 960, 1.2, t, a=dim)
    bubble_txt(d, t, t0 + 1.0, 540, 600, "嗯……让我想想", NAVYT, 44) if t < SIL0 else None
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (120, 170, 255), (40, 60, 140))
    if t > t0: sparks(d, 540, 700, t, t0, 30, 900, (200, 230, 255), 1, 3, 0.9)
    bar(d, 300, 470, 560, 0.235 / 0.82 * ease(pr(t, t0, t0 + 0.4)), MINT, "乌鸦", "0.235秒")
    bar(d, 300, 620, 560, (0.6 / 0.82) * ease(pr(t, t0 + 0.4, t0 + 1.0)), (240, 170, 90), "猴子", "0.41–0.6秒", ap(t, t0 + 0.3))
    bar(d, 300, 770, 560, 1.0 * ease(pr(t, t0 + 0.9, t0 + 1.7)), PINK, "人类", "0.45–0.82秒", ap(t, t0 + 0.8))
    crow(d, 360, 1130, 1.3, t, glasses=True, head=-0.2)
    human(d, 760, 1080, 0.9, t, face="shock")
def s_how(t, d):
    t0 = T["how"]
    flatbg(d, (60, 70, 110), (20, 24, 44), t, False)
    screen(d, 540, 640, 640, 420, t, 0.03, 1, hit=1 if t > t0 + 2.0 else None)
    tag(d, 540, 380, "只有3%的点在同向走", GOLD, ap(t, t0 + 0.3), 40)
    crow(d, 300, 1150, 1.1, t, head=-0.5, face="smug")
    k = popk(t, t0 + 1.8)
    if k > 0:
        tag(d, 700, 960, "瞎猜：一半对", (150, 150, 170), min(1, k), 36)
        tag(d, 700, 1060, "乌鸦：比一半多", MINT, min(1, k), 40)
def s_xray(t, d):
    t0 = T["xray"]
    flatbg(d, (36, 24, 70), (12, 8, 28), t, False)
    d.ell(540, 760, 330, 250, A((200, 150, 200), 0.25))
    rv = random.Random(5)
    for i in range(248):
        x, y = 540 + rv.uniform(-300, 300), 760 + rv.uniform(-220, 220)
        if ((x - 540) / 320) ** 2 + ((y - 760) / 240) ** 2 > 1: continue
        hot = i % 4 == 0 and t > t0 + 1.4
        d.circ(x, y, 7 if not hot else 10, fill=A(GOLD if hot else (150, 140, 200), 1))
    ptag(d, t, t0 + 0.3, 540, 420, "记录 248 个神经元", WHITE, 44)
    ptag(d, t, t0 + 1.6, 540, 1110, "58 个能预判选择", GOLD, 48)
def s_swim(t, d):
    t0 = T["swim"]
    flatbg(d, (60, 70, 110), (20, 24, 44), t, False)
    d.line([(200, 900), (880, 900)], A(WHITE, 0.6), 6)
    for ms, lab, col in ((0, "点出现", WHITE), (70, "神经元已知道", GOLD), (235, "开始转头", MINT)):
        x = 200 + 680 * ms / 235; a_ = ap(t, t0 + 0.3 + ms / 235 * 1.4)
        d.circ(x, 900, 20, fill=A(col, a_)); d.text(x, 980, f"{ms}ms", 40, A(col, a_), k=1); tag(d, x, 820, lab, col, a_, 32)
    crow(d, 540, 1220, 1.0, t, head=-0.3)
def s_gene(t, d):
    t0 = T["gene"]
    flatbg(d, (36, 24, 70), (12, 8, 28), t, False)
    d.line([(220, 1150), (880, 1150)], A(WHITE, 0.5), 5); d.line([(220, 1150), (220, 450)], A(WHITE, 0.5), 5)
    d.line([(220, 520), (880, 520)], A(MEAN, 0.7), 4); tag(d, 760, 470, "出手线", MEAN, 1, 32)
    u = pr(t, t0 + 0.2, t0 + 2.8)
    for slope, col, lab in ((1.0, MINT, "证据强"), (0.55, GOLD, "证据弱")):
        n = int(40 * u)
        if n < 2: continue
        pts = [(220 + 660 * i / 40, 1150 - min(630, 630 * slope * (i / 40) * 1.6)) for i in range(n)]
        d.line(pts, A(col, 1), 10)
        tag(d, pts[-1][0] + 60, pts[-1][1], lab, col, 1, 30)
def s_why(t, d):
    t0 = T["why"]
    flatbg(d, (240, 220, 200), (210, 180, 160), t, False)
    k = popk(t, t0)
    if k > 0:
        for i in range(6): d.rect(140, 520 + i * 44, 480, 556 + i * 44, fill=A([(250, 170, 160), (240, 150, 140)][i % 2], 1), r=10)
        tag(d, 310, 470, "人：六层皮层", PINK, min(1, k), 34)
    k2 = popk(t, t0 + 0.8)
    if k2 > 0:
        rv = random.Random(9)
        for i in range(40): d.circ(780 + rv.uniform(-150, 150), 650 + rv.uniform(-120, 120), rv.uniform(14, 26), fill=A((150, 170, 240), 1))
        tag(d, 780, 470, "鸟：一团团的核", CRW_H, min(1, k2), 34)
    ptag(d, t, t0 + 1.8, 540, 1000, "算法却很像", NAVYT, 50, tc=WHITE) if False else ptag(d, t, t0 + 1.8, 540, 1000, "算法却很像", GOLD, 50)
def s_order(t, d):
    t0 = T["order"]
    flatbg(d, (120, 170, 220), (70, 120, 180), t, False)
    crow(d, 330, 820, 1.3, t, head=-0.2)
    human(d, 780, 760, 0.9, t, face="slow")
    k = popk(t, t0 + 0.8)
    if k > 0:
        d.line([(330, 640), (420, 640)], A(MINT, 1), 10); tag(d, 330, 560, "线路短", MINT, min(1, k), 36)
        d.line([(640, 600), (920, 600)], A(PINK, 1), 10); tag(d, 780, 520, "线路长", PINK, min(1, k), 36)
    k2 = popk(t, t0 + 2.0)
    if k2 > 0: tag(d, 330, 1040, "体温约41–42℃", GOLD, min(1, k2), 34)
    tag(d, 540, 1180, "推测，尚未验证", WHITE, ap(t, t0 + 2.6), 30)
def s_card(t, d):
    flatbg(d, (40, 46, 80), (14, 16, 30), t, False)
    for i in range(12): d.circ(540, 820, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    crow(d, cx_ - 30, cy_ - 150, 0.9, t, glasses=True, a=a_)
    d.text(cx_, cy_ + 20, "乌鸦看图做决定 ≈ 0.235秒", 44, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("约比人和猴子快一倍", "快，但不是瞎蒙", "大脑结构不同，算法相似")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 130 + i * 78, s_, 42, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    rays(d, t, (255, 190, 90), (230, 120, 60))
    crow(d, 540, 900, 2.2, t, glasses=True, head=-0.15)
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 290, "Schmidbauer & Nieder 2026 · Science", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 335, "德国图宾根大学", 25, A(WHITE, 0.85 * ra), k=1)
        d.text(540, 372, "doi:10.1126/science.aed6459", 22, A(WHITE, 0.75 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "快一倍", "q": "0.235秒", "who": "小嘴乌鸦", "sperm": "面包虫", "egg": "要多久", "reveal": "0.45到0.82秒", "how": "3%",
      "xray": "58个", "swim": "70毫秒", "gene": "越快", "why": "很像", "order": "线路短", "end": "出手比你早"}
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/cr_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/cr_sheet.png")
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
