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
def sky(d, t, top=(120, 180, 240), bot=(200, 225, 250)): flatbg(d, top, bot, t, False)
def dots(d, t, t0, n, x0, x1, y, col=GUANO, seed=3, r=12):
    rv = random.Random(seed)
    for i in range(n):
        k = ap(t, t0 + i * 0.08, 0.2)
        if k > 0: d.circ(rv.uniform(x0, x1), y + rv.uniform(-30, 30), r * k, fill=A(col, 1))
def s_hook(t, d):
    sky(d, t)
    if t < 0.3: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - t / 0.3)))
    snowfield(d, 880)
    gk = ease(pr(t, 0.2, 2.0))
    d.ell(540, 1060, 420 * gk, 90 * gk, A(ALG_G, 0.85))
    for i in range(5): algae(d, 300 + i * 120, 1060, 0.6 * gk, t, ph=i)
    penguin(d, 540, 640, 1.5, t, face="smug")
    k = popk(t, 2.4, "bouncy")
    if k > 0: tag(d, 540, 330, "噗～", GUANO, min(1, k), 60)
def s_q(t, d):
    t0 = T["q"]
    flatbg(d, (20, 60, 110), (40, 100, 160), t, False)
    # peninsula
    d.poly([(600, 300), (660, 360), (620, 520), (560, 700), (470, 900), (380, 1080), (330, 1060), (430, 860), (520, 650), (570, 450)], A(SNOW, 1))
    for i in range(9):
        k = popk(t, t0 + 0.2 + i * 0.18)
        u = i / 8; x = 610 - 250 * u + 10 * math.sin(i); y = 380 + 680 * u
        if k > 0: d.circ(x + 40, y, 16 * min(1.2, k), fill=A(GOLD, 1))
    ptag(d, t, t0 + 1.0, 760, 500, "9个海岸点", GOLD, 44)
    k = popk(t, t0 + 1.8, "bouncy")
    if k > 0: tag(d, 760, 620, "111份雪样", WHITE, min(1, k), 44)
def s_who(t, d):
    t0 = T["who"]
    flatbg(d, (230, 240, 252), (200, 220, 245), t, False)
    k = popk(t, t0, "bouncy")
    if k > 0: algae(d, 370, 760, 2.4 * min(1, k), t, ALG_G)
    k2 = popk(t, t0 + 1.2, "bouncy")
    if k2 > 0: algae(d, 710, 760, 2.4 * min(1, k2), t, ALG_R, ph=1)
    ptag(d, t, t0 + 0.4, 370, 1000, "绿雪藻", ALG_G, 44); ptag(d, t, t0 + 1.4, 710, 1000, "红雪藻", ALG_R, 44)
def s_sperm(t, d):
    t0 = T["sperm"]
    sky(d, t, (40, 100, 170), (120, 180, 230))
    d.rect(0, 1000, 1080, 1950, fill=A((40, 90, 160), 1))
    rv = random.Random(5)
    for i in range(10):  # krill
        x = (rv.uniform(0, 1080) + t * 60) % 1080; y = rv.uniform(1050, 1300)
        d.ell(x, y, 26, 9, A((255, 140, 120), 1))
    penguin(d, 540, 720, 1.3, t, face="happy")
    dots(d, t, t0 + 1.3, 8, 360, 720, 960)
    ptag(d, t, t0 + 1.4, 760, 420, "磷 P", GOLD, 64)
    ptag(d, t, t0 + 0.4, 280, 1120, "磷虾", (255, 140, 120), 40)
def s_egg(t, d):
    t0 = T["egg"]
    flatbg(d, (230, 240, 252), (200, 220, 245), t, False)
    dim = 1 - 0.6 * pr(t, SIL0, SIL0 + 0.1)
    algae(d, 540, 820, 2.2, t, ALG_G, a=dim, face="eat")
    for i in range(5):
        u = pr(t, t0 + 0.3 + i * 0.4, t0 + 1.0 + i * 0.4)
        if 0 < u < 1: d.circ(540 + (1 - u) * (300 - i * 130), 820 - (1 - u) * 400, 18, fill=A(GUANO, dim))
    if t < SIL0: ptag(d, t, t0 + 1.2, 540, 500, "吧唧吧唧", WHITE, 44)
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (130, 230, 140), (40, 150, 80))
    if t > t0: sparks(d, 540, 760, t, t0, 30, 900, (255, 255, 200), 1, 3, 0.9)
    algae(d, 540, 760, 3.0, t, ALG_G, face="happy")
    k = popk(t, t0 + 0.4, "bouncy")
    if k > 0: tag(d, 540, 420, "×70", WHITE, min(1, k), 120)
    ptag(d, t, t0 + 1.0, 540, 1080, "绿雪 vs 干净雪（磷含量）", WHITE, 40)
def s_how(t, d):
    t0 = T["how"]
    flatbg(d, (230, 240, 252), (200, 220, 245), t, False)
    base = 1100
    for i, (lab, v, col) in enumerate((("干净雪", 1.54, (180, 200, 230)), ("红雪", 11.43, ALG_R), ("绿雪", 113.8, ALG_G))):
        x = 300 + i * 240; h = 620 * (v / 113.8) ** 0.5 * ease(pr(t, t0 + 0.2 + i * 0.4, t0 + 0.9 + i * 0.4))
        d.rect(x - 70, base - h, x + 70, base, fill=A(col, 1), r=14)
        tag(d, x, base + 50, lab, col if i else (90, 110, 150), 1, 36)
        if h > 20: d.text(x, base - h - 52, f"{v:g}", 34, A(NAVYT, 1), k=1)
    tag(d, 540, 330, "磷酸盐中位数（微摩尔/升）", WHITE, ap(t, t0 + 0.2), 32)
    ptag(d, t, t0 + 1.8, 560, 520, "×10", ALG_G, 64)
def s_xray(t, d):
    t0 = T["xray"]
    sky(d, t); snowfield(d, 1000)
    sun(d, 260, 380, 1.0, t)
    u = pr(t, t0 + 0.3, t0 + 1.3)
    d.line([(300, 440), (300 + (560 - 300) * u, 440 + (1000 - 440) * u)], A((255, 210, 80), 1), 12)
    v = pr(t, t0 + 1.3, t0 + 2.3)
    if v > 0: d.line([(560, 1000), (560 + 340 * v, 1000 - 560 * v)], A((255, 230, 140), 1), 12)
    ptag(d, t, t0 + 1.6, 820, 620, "反射回去", (200, 140, 20), 40)
    penguin(d, 820, 870, 0.6, t)
def s_swim(t, d):
    t0 = T["swim"]
    sky(d, t); snowfield(d, 1000)
    gk = ease(pr(t, t0 + 0.2, t0 + 1.2))
    d.ell(600, 1080, 400 * gk, 70 * gk, A(ALG_G, 0.9))
    sun(d, 260, 380, 1.0, t)
    d.line([(300, 440), (600, 1060)], A((255, 210, 80), 1), 12)
    rv = 1 - 0.4 * gk
    d.line([(600, 1060), (600 + 300 * rv, 1060 - 500 * rv)], A((255, 230, 140), 0.4 + 0.6 * rv), max(4, int(12 * rv)))
    ptag(d, t, t0 + 1.4, 760, 640, "反光最多 -40%", ALG_G, 50)
def s_gene(t, d):
    t0 = T["gene"]
    sky(d, t); snowfield(d, 1000)
    sun(d, 260, 380, 1.0, t)
    m = ease(pr(t, t0 + 0.6, t0 + 3.0))
    d.ell(560, 1060, 380 + 80 * m, 60 + 30 * m, A(ALG_G, 0.9 * (1 - m * 0.5)))
    if m > 0: d.ell(560, 1080, 300 * m, 50 * m, A((110, 170, 230), 0.9))
    for i in range(3):  # heat waves
        y0 = 980 - i * 40 - (t * 80) % 120
        d.arc(470 + i * 90, y0, 20, 30, 200, 340, A((255, 140, 80), 0.7), 6)
    penguin(d, 860, 860, 0.6, t, face="shock" if m > 0.4 else "happy")
    ptag(d, t, t0 + 1.0, 540, 720, "吸热 ↑  融化 ↑", (230, 110, 60), 46)
def s_why(t, d):
    t0 = T["why"]
    flatbg(d, (30, 40, 70), (20, 26, 50), t, False)
    d.rect(200, 450, 880, 980, fill=A((236, 240, 248), 1), r=24)
    tag(d, 540, 500, "融雪预测模型", GOLD, 1, 38)
    for i, s_ in enumerate(("气温 ✓", "阳光 ✓", "灰尘 ✓")):
        a_ = ap(t, t0 + 0.2 + i * 0.3); d.rect(320, 590 + i * 80, 320 + (440 - 60 * i) * a_, 620 + i * 80, fill=A((190, 198, 215), 1), r=12)
    k = popk(t, t0 + 1.5, "bouncy")
    if k > 0: d.text(540, 870, "企鹅便便  没算", 44, A((220, 70, 70), min(1, k)), k=1)
    penguin(d, 880, 1120, 0.5, t, face="smug")
def s_order(t, d):
    t0 = T["order"]
    flatbg(d, (20, 60, 110), (40, 100, 160), t, False)
    d.poly([(600, 300), (660, 360), (620, 520), (560, 700), (470, 900), (380, 1080), (330, 1060), (430, 860), (520, 650), (570, 450)], A(SNOW, 1))
    u = ease(pr(t, t0 + 0.3, t0 + 2.6))
    px, py = 620 - 230 * u, 420 + 560 * u
    d.ell(px, py + 40, 70 * (0.5 + u), 18 * (0.5 + u), A(ALG_G, 0.8))
    penguin(d, px + 120, py - 60, 0.45, t)
    ptag(d, t, t0 + 0.6, 820, 1000, "往南", WHITE, 38)
def s_card(t, d):
    flatbg(d, (30, 80, 70), (12, 30, 28), t, False)
    for i in range(12): d.circ(540, 820, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    penguin(d, cx_ - 90, cy_ - 160, 0.6, t, a=a_); algae(d, cx_ + 110, cy_ - 120, 1.0, t, a=a_)
    d.text(cx_, cy_ + 20, "企鹅便便＝雪藻的肥料", 46, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("磷多，绿雪藻长得旺", "雪变暗，少反光", "吸热更多，融得更快")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 130 + i * 78, s_, 40, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    sky(d, t); snowfield(d, 880)
    gk = ease(pr(t, t0 + 0.6, t0 + 2.0))
    d.ell(540, 1060, 420 * gk, 90 * gk, A(ALG_G, 0.85))
    penguin(d, 540, 680, 1.4, t, face="smug")
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 290, "Ryan & Khan 2026", 28, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 335, "J. Geophys. Res. Biogeosciences 131", 24, A(WHITE, 0.85 * ra), k=1)
        d.text(540, 372, "doi:10.1029/2026JG009918", 22, A(WHITE, 0.75 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "便便", "q": "111份雪", "who": "雪藻", "sperm": "磷", "egg": "磷", "reveal": "70倍", "how": "10倍",
      "xray": "镜子", "swim": "四成", "gene": "融得更快", "why": "没算进", "order": "跟着走", "end": "雪就变绿"}
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/pg_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/pg_sheet.png")
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
