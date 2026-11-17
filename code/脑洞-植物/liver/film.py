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

def s_hook(t, d):
    garden(d, t)
    thallus(d, 540, 1330, 2.4, t); umbrella(d, 540, 1290, 2.2, t, h=330, face="happy", water=0.15 + 0.85 * ((t * 0.5) % 1), structs=0.6)
    k = popk(t, 0.05, "bouncy")
    if k > 0: arrow_up(d, 820, 1250, 620, (90, 190, 255), min(1, k)); tag(d, 820, 560, "水往上爬", (60, 150, 230), min(1, k), 50)
def s_q(t, d):
    garden(d, t)
    t0 = T["q"]
    thallus(d, 540, 1330, 2.4, t); umbrella(d, 540, 1290, 2.2, t, h=330, face="neutral", water=0.15 + 0.85 * ((t * 0.5) % 1), structs=0.6)
    # a pump with a big X
    k = popk(t, t0 + 0.2)
    if k > 0:
        px, py = 250, 620
        d.rect(px - 70, py - 60, px + 70, py + 80, fill=A((200, 200, 210), 1), r=16); d.rect(px - 15, py - 130, px + 15, py - 60, fill=A((170, 170, 180), 1))
        d.text(px, py + 10, "泵", 60, A(NAVYT, 1), k=1)
        xmark(d, px + 70, py - 70, 40, MEAN, 1, popk(t, t0 + 0.6))
    ptag(d, t, t0 + 1.2, 800, 600, "全靠表面", GOLD, 46)
def s_who(t, d):
    garden(d, t, (90, 140, 96), (40, 80, 50), 1100)
    t0 = T["who"]
    k = popk(t, t0, "bouncy")
    for i, (x, y, s_) in enumerate(((300, 1110, 1.6), (720, 1130, 1.9), (520, 1160, 1.2))):
        kk = popk(t, t0 + i * 0.2)
        if kk > 0: thallus(d, x, y, s_ * min(1, kk), t)
    puddle(d, 520, 1240, 300)
    ptag(d, t, t0 + 0.4, 540, 620, "地钱 Marchantia", LEAF, 52)
    ptag(d, t, t0 + 1.4, 540, 760, "苔藓的亲戚 · 没有花和种子", WHITE, 36)
def s_sperm(t, d):
    t0 = T["sperm"]
    flatbg(d, (40, 110, 170), (12, 50, 100), t, False)
    for i in range(5):
        rv = random.Random(i); x = (rv.uniform(0, 1080) + (t - t0) * 260) % 1180 - 50; y = 500 + i * 140
        sperm(d, x, y, 2.6, t + i)
    k = popk(t, t0 + 1.2)
    if k > 0:
        d.rect(160, 1080, 920, 1200, fill=A((70, 52, 40), 1), r=24)
        sperm(d, 540, 1040, 2.6, t, ang=0.0); bubble_txt(d, t, t0 + 1.5, 680, 920, "没水游不动…", NAVYT, 46)
def s_egg(t, d):
    t0 = T["egg"]
    garden(d, t, (110, 160, 210), (60, 110, 160))
    dim = 1 - 0.6 * pr(t, SIL0, SIL0 + 0.1)
    puddle(d, 540, 1360, 380, dim)
    thallus(d, 540, 1330, 2.4, t, a=dim)
    hk = ease(pr(t, t0, t0 + 1.4))
    x, top = umbrella(d, 540, 1290, 2.2, t, h=80 + 250 * hk, face="worry", a=dim)
    k = popk(t, t0 + 1.0)
    if k > 0:
        for ex in (-60, 0, 60): d.circ(x + ex, top + 70, 16 * min(1, k), fill=A((255, 200, 220), dim)); 
        tag(d, x + 250, top + 40, "卵在这儿", PINK, min(1, k) * dim, 40); d.line([(x + 170, top + 50), (x + 80, top + 68)], A(PINK, dim), 5)
    for i in range(3): sperm(d, 380 + i * 140, 1360, 1.6, t + i, ang=-0.3, a=dim)
    bubble_txt(d, t, t0 + 2.4, 330, 1150, "太高了！", NAVYT, 44, tail=1) if t < SIL0 else None
def s_reveal(t, d):
    rays(d, t, (120, 200, 140), (30, 90, 60))
    t0 = BIG2
    puddle(d, 540, 1360, 380)
    thallus(d, 540, 1330, 2.4, t)
    u = ease(pr(t, t0, t0 + 1.4))
    x, top = umbrella(d, 540, 1290, 2.2, t, h=330, face="happy", water=0.05 + 0.95 * u, structs=1)
    arrow_up(d, 780, 1250, 650, (90, 190, 255), ap(t, t0, 0.2))
    for i in range(3): sperm(d, x - 20 + i * 10, lerp(1340, top + 90, ease(pr(t, t0 + 0.4 + i * 0.25, t0 + 2.2 + i * 0.25))), 1.4, t + i, ang=-math.pi / 2)
    if t > t0: sparks(d, x, top, t, t0, 30, 900, (180, 230, 255), 1, 3, 0.9)
def s_how(t, d):
    t0 = T["how"]
    flatbg(d, (30, 60, 50), (10, 24, 20), t, False)
    # zoomed stalk surface
    d.rect(420, 260, 660, 1320, fill=A(STALK, 1), r=30)
    cols = [(LW_D, "脊"), ((230, 210, 160), "沟"), (LW_L, "毛")]
    for j in range(16):
        y = 1280 - j * 64
        k = popk(t, t0 + 0.05 * j)
        if k <= 0: continue
        d.rect(400, y - 10, 440, y + 10, fill=A(LW_D, 1), r=6); d.rect(640, y - 10, 680, y + 10, fill=A(LW_D, 1), r=6)
        d.line([(660, y), (700 + 20 * min(1, k), y - 26)], A(LW_L, 1), 6)
        d.rect(500, y - 22, 580, y - 14, fill=A((230, 210, 160), 1), r=4)
    u = ((t - t0) * 0.45) % 1
    d.rect(445, 1320 - 1060 * u, 635, 1320, fill=A((90, 180, 255), 0.45), r=20)
    for i, (lab, y, col) in enumerate((("结构A", 1180, CYAN2), ("结构B", 900, GOLD), ("结构C", 620, PINK))):
        tag(d, 230 if i % 2 == 0 else 850, y, lab, col, ap(t, t0 + 0.6 + i * 0.4), 38)
    ptag(d, t, t0 + 2.0, 540, 260, "结构完整，受精才顺利", WHITE, 40); tag(d, 540, 1370 - 60, "示意图", WHITE, 0.6, 28)
def s_xray(t, d):
    t0 = T["xray"]
    flatbg(d, (16, 22, 40), (4, 6, 14), t, False)
    sc = ease(pr(t, t0 + 0.3, t0 + 2.0))
    x, top = umbrella(d, 540, 1220, 2.0, t, h=300, face=None, a=0.35 + 0.4 * sc, structs=sc)
    yy = lerp(1250, 450, ((t - t0) * 0.6) % 1)
    d.rect(250, yy - 4, 830, yy + 4, fill=A((120, 255, 220), 0.9)); glow(d, 540, yy, 300, (120, 255, 220), 0.15)
    d.rect(170, 330, 910, 430, fill=A((6, 10, 24), 0.8), r=30); d.text(540, 380, "3D X光扫描", 52, A((120, 255, 220), 1), k=1)
def s_swim(t, d):
    t0 = T["swim"]
    garden(d, t, (120, 180, 220), (70, 130, 170))
    puddle(d, 540, 1360, 380); thallus(d, 540, 1330, 2.4, t)
    x, top = umbrella(d, 540, 1290, 2.2, t, h=330, face="happy", water=1.0, structs=1)
    for i in range(5):
        u = ((t - t0) * 0.35 + i / 5) % 1
        sperm(d, x + (14 if i % 2 else -14), lerp(1340, top + 80, u), 1.3, t + i, ang=-math.pi / 2)
    k = popk(t, t0 + 2.0, "bouncy")
    if k > 0:
        for ex in (-60, 0, 60): heart(d, x + ex, top + 120, 22 * min(1, k), PINK, 1)
        tag(d, x, top - 120, "受精成功", PINK, min(1, k), 46)
def s_gene(t, d):
    t0 = T["gene"]
    flatbg(d, (40, 30, 80), (14, 10, 30), t, False)
    k = popk(t, t0, "bouncy")
    if k > 0:
        d.rect(540 - 260 * k, 520 - 120 * k, 540 + 260 * k, 520 + 120 * k, fill=A((250, 246, 234), 1), r=40)
        d.text(540, 490, "MpLAS", int(110 * min(1, k)), A(NAVYT, 1), k=1); d.text(540, 590, "一种GRAS蛋白", 34, A((90, 90, 110), 1), k=1)
    on = int((t - t0) * 2) % 2 == 0
    sw = ap(t, t0 + 0.8)
    d.rect(400, 760, 680, 860, fill=A((80, 80, 110), sw), r=50); d.circ(470 if not on else 610, 810, 40, fill=A(MINT if on else (200, 200, 210), sw))
    d.text(540, 930, "开" if on else "关", 50, A(WHITE, sw), k=1)
    for i, col in enumerate((CYAN2, GOLD, PINK)):
        kk = on and t > t0 + 1.2
        d.rect(240 + i * 230, 960, 380 + i * 230, 1000 + (80 if kk else 0), fill=A(col, 0.95 if kk else 0.25), r=14)
    ptag(d, t, t0 + 1.6, 540, 1150, "管着这些小结构", WHITE, 40)
def s_why(t, d):
    t0 = T["why"]
    garden(d, t, (150, 200, 230), (100, 160, 200))
    x, top = umbrella(d, 300, 1330, 1.6, t, h=120, face="neutral")
    x2, top2 = umbrella(d, 760, 1330, 1.6, t, h=420, face="happy")
    for i in range(14):
        u = ((t - t0) * 0.5 + i / 14) % 1
        d.circ(x + (i - 7) * 10 * u * 3, top + 40 + u * 90, 6, fill=A((200, 160, 90), 1 - u))
        d.circ(x2 + (i - 7) * 10 * u * 9, top2 + 40 + u * 160, 6, fill=A((200, 160, 90), 1 - u * 0.6))
    tag(d, 300, top - 110, "矮：撒得近", MEAN, ap(t, t0 + 0.8), 36)
    tag(d, 760, top2 - 110, "高：撒得远", MINT, ap(t, t0 + 1.6), 36)
def s_order(t, d):
    t0 = T["order"]
    flatbg(d, (60, 90, 70), (20, 36, 28), t, False)
    d.line([(160, 1000), (920, 1000)], A(WHITE, 0.6), 8); d.poly([(920, 970), (970, 1000), (920, 1030)], A(WHITE, 0.6))
    k1 = popk(t, t0 + 0.2)
    if k1 > 0: umbrella(d, 330, 950, 1.2 * min(1, k1), t, h=280, face="neutral"); tag(d, 330, 1080, "第1步：高柄", GOLD, min(1, k1), 36)
    k2 = popk(t, t0 + 1.8)
    if k2 > 0: umbrella(d, 760, 950, 1.2 * min(1, k2), t, h=280, face="happy", water=1.0, structs=1); tag(d, 760, 1080, "第2步：运水", CYAN2, min(1, k2), 36)
    ptag(d, t, t0 + 2.6, 540, 420, "后来的补上了前面的短板", WHITE, 38)
def s_card(t, d):
    flatbg(d, (34, 70, 50), (10, 24, 18), t, False)
    for i in range(12): d.circ(540, 820, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    umbrella(d, cx_, cy_ - 40, 0.9, t, h=200, face="happy", water=1.0, structs=1, a=a_)
    d.text(cx_, cy_ + 40, "地钱的伞柄 = 一根运水管", 46, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("精子靠水游过去", "伞柄表面把水往上送", "举高是为了撒孢子")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 140 + i * 78, s_, 42, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    garden(d, t)
    puddle(d, 540, 1360, 380); thallus(d, 540, 1330, 2.4, t)
    x, top = umbrella(d, 540, 1290, 2.2, t, h=330, face="happy", water=1.0, structs=1)
    for i in range(3):
        u = ((t - t0) * 0.35 + i / 3) % 1
        sperm(d, x + (14 if i % 2 else -14), lerp(1340, top + 80, u), 1.3, t + i, ang=-math.pi / 2)
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 290, "Qi 等 2026 · Nature Plants", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 335, "中国科学院植物研究所 徐波团队", 25, A(WHITE, 0.85 * ra), k=1)
        d.text(540, 372, "doi:10.1038/s41477-026-02450-1", 22, A(WHITE, 0.75 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "往高处流", "q": "往上爬", "who": "地钱", "sperm": "游", "egg": "小伞", "reveal": "往上送", "how": "刚刚好", "xray": "3D X光",
      "swim": "游到卵", "gene": "MpLAS", "why": "撒得更远", "order": "后来", "end": "精子游上楼"}
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
    s = "Vibe 知识大赏 · 怪奇植物"; w = d.tlen(s, 28, 1) + 50
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/lv_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/lv_sheet.png")
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
