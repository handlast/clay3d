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
def jungle(d, t, top=(70, 140, 100), bot=(20, 60, 40)): flatbg(d, top, bot, t, False)
def s_hook(t, d):
    jungle(d, t, (40, 110, 110), (10, 40, 50))
    if t < 0.3: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - t / 0.3)))
    z = 1 - 0.55 * E.ease_in_out_sine(pr(t, 1.4, 2.4))
    # ruler
    ra = 1 - pr(t, 1.4, 1.9)
    if ra > 0:
        d.rect(160, 900, 920, 980, fill=A((250, 230, 150), ra), r=10)
        for i in range(31):
            x = 200 + i * 22.7; h = 40 if i % 10 == 0 else 20
            d.line([(x, 900), (x, 900 + h)], A(NAVYT, ra), 3)
            if i % 10 == 0: d.text(x, 945, str(i // 10), 24, A(NAVYT, ra), k=1)
        d.text(880, 945, "cm", 22, A(NAVYT, ra), k=1)
    for i, (px, py) in enumerate(((280, 1000), (560, 1090), (820, 980))):
        k = popk(t, 1.8 + i * 0.25)
        if k > 0: pool(d, px, py, 120 * min(1, k), 50 * min(1, k))
    if t > 1.6:
        for x in (150, 420, 700, 950): tree(d, x, 850, 1.2, a=pr(t, 1.6, 2.0))
    e = E.ease_in_out_sine(pr(t, 1.4, 2.4)); killi(d, lerp(560, 560, e), lerp(840, 1090, e), lerp(1.6, 0.3, e), t)
    if t >= 2.4: tag(d, 540, 600, "全世界只见过 3 个水坑", GOLD, ap(t, 2.4), 48)
def s_q(t, d):
    t0 = T["q"]
    jungle(d, t, (255, 190, 120), (200, 110, 50))
    killi(d, 600, 760, 2.4, t)
    k = popk(t, t0 + 0.6, "bouncy")
    if k > 0: orange_fruit(d, 250, 480, 90 * min(1.1, k))
    ptag(d, t, t0 + 1.2, 540, 1080, "laranja = 橙子（葡萄牙语）", WHITE, 40)
def s_who(t, d):
    t0 = T["who"]
    jungle(d, t, (40, 80, 100), (12, 30, 44))
    killi(d, 560, 760, 2.8, t, spots=pr(t, t0 + 0.3, t0 + 1.5), chev=pr(t, t0 + 1.8, t0 + 2.8), wig=0.3)
    ptag(d, t, t0 + 0.6, 800, 520, "圆点", ORG, 40, tc=WHITE)
    ptag(d, t, t0 + 2.0, 360, 1000, "人字纹", ORG, 40, tc=WHITE)
def s_sperm(t, d):
    t0 = T["sperm"]
    jungle(d, t, (230, 236, 240), (190, 200, 210))
    for i, s_ in enumerate(("颜色", "鳞片", "骨头", "DNA")):
        y = 460 + i * 150; k = ap(t, t0 + 0.3 + i * 0.6, 0.2)
        if k > 0:
            d.rect(240, y - 50, 840, y + 50, fill=A(WHITE, k), r=24)
            d.text(400, y - 26, s_, 46, A(NAVYT, k), k=1)
            kk = popk(t, t0 + 0.6 + i * 0.6, "bouncy")
            if kk > 0: check(d, 720, y, 34, (60, 180, 100), min(1, kk))
def s_egg(t, d):
    t0 = T["egg"]
    jungle(d, t)
    dim = 1 - 0.45 * pr(t, SIL0, SIL0 + 0.15)
    for x, y in ((200, 600), (900, 700), (300, 1100), (850, 1150), (560, 450)): tree(d, x, y, 1.0, a=dim)
    k = popk(t, t0 + 0.2, "bouncy")
    if k > 0: tag(d, 540, 520, "新物种！", GOLD, min(1, k) * dim, 60)
    r = 60 + 200 * ease(pr(t, t0 + 1.2, t0 + 3.6))
    for i in range(36):
        u = i / 36 * 2 * math.pi; d.circ(540 + math.cos(u) * r, 860 + math.sin(u) * r, 6, fill=A(WHITE, 0.8 * dim))
    killi(d, 540, 860, 0.5, t, a=dim)
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (255, 170, 80), (180, 70, 30))
    if t > t0: sparks(d, 540, 760, t, t0, 30, 900, (255, 230, 180), 1, 3, 0.9)
    k1 = popk(t, t0 + 0.05, "bouncy"); k2 = popk(t, t0 + 0.6, "bouncy")
    if k2 > 0:
        r = 230 * min(1, k2); d.ell(700, 800, r, r * 0.8, A((240, 240, 250), 0.95)); d.text(700, 760, "澳门", 54, A(NAVYT, min(1, k2)), k=1); d.text(700, 830, "33.4 km²", 40, A(NAVYT, min(1, k2)), k=1)
    if k1 > 0:
        r = 230 * math.sqrt(25 / 33.4) * min(1, k1); d.ell(330, 900, r, r * 0.8, A(ORG, 0.95)); d.text(330, 860, "橙子鱼", 46, A(WHITE, min(1, k1)), k=1); d.text(330, 920, "约 25 km²", 38, A(WHITE, min(1, k1)), k=1)
def s_how(t, d):
    t0 = T["how"]
    jungle(d, t)
    # muddy stream
    for i in range(10):
        x = 900 - ((t * 120 + i * 90) % 900); d.ell(x, 600 + math.sin(i) * 20, 70, 26, A(MUD, 0.9))
    pool(d, 500, 900, 300, 130, col=mix(POOL, MUD, 0.4 * pr(t, t0, t0 + 3)))
    killi(d, 500, 900, 0.8, t, face="worried")
    ptag(d, t, t0 + 0.5, 700, 460, "采矿泥沙", MUD, 40, tc=WHITE)
def s_xray(t, d):
    t0 = T["xray"]
    flatbg(d, (150, 170, 190), (80, 90, 110), t, False)
    for i, h in enumerate((380, 520, 300, 460, 340)): d.rect(80 + i * 190, 760 - h, 230 + i * 190, 760, fill=A((110, 120, 140), 1))
    pool(d, 540, 950, 330, 140)
    for i in range(5):
        k = popk(t, t0 + 0.3 + i * 0.25)
        if k > 0:
            x = 330 + i * 100; y = 920 + (i % 2) * 40 + math.sin(t * 2 + i) * 6
            d.rect(x - 18, y - 40, x + 18, y + 10, fill=A((200, 230, 255), 0.85 * min(1, k)), r=8); d.rect(x - 8, y - 52, x + 8, y - 40, fill=A((60, 140, 220), min(1, k)))
    killi(d, 560, 1010, 0.6, t, face="worried")
    ptag(d, t, t0 + 1.6, 540, 1180, "塑料污染", WHITE, 40)
def s_swim(t, d):
    t0 = T["swim"]
    jungle(d, t, (60, 40, 50), (24, 14, 20))
    killi(d, 540, 820, 1.6, t, face="worried")
    k = popk(t, t0 + 0.5, "bouncy")
    if k > 0:
        s_ = min(1, k); d.rect(320, 470, 760, 590, fill=A((220, 50, 50), 0.95 * s_), r=20); d.text(540, 495, "濒危 EN", 60, A(WHITE, s_), k=1)
    ptag(d, t, t0 + 1.4, 540, 1080, "作者按 IUCN 标准评估", WHITE, 36)
def s_gene(t, d):
    t0 = T["gene"]
    flatbg(d, (120, 160, 200), (60, 90, 130), t, False)
    d.rect(0, 900, OW, OH, fill=A(MUD, 1)); d.rect(0, 1150, OW, OH, fill=A(MUD_D, 1))
    rain = pr(t, t0 + 2.4, t0 + 2.8)
    for i in range(6):
        x = 220 + i * 130; y = 1020 + (i % 2) * 50
        egg_r = 30
        d.circ(x, y, egg_r, fill=A((255, 230, 170), 0.9))
        if rain < 1: d.text(x + 34, y - 60 - 6 * math.sin(t * 3 + i), "z", 34, A(WHITE, 0.8 * (1 - rain)), k=1)
        else: d.circ(x + 6, y - 4, 8, fill=A(NOSE, 1))
    if rain > 0:
        for i in range(30):
            x = (i * 37) % OW; y = ((t * 900 + i * 97) % 900)
            d.line([(x, y), (x - 6, y + 30)], A((200, 230, 255), 0.7 * rain), 4)
    ptag(d, t, t0 + 0.5, 540, 600, "同属部分种类", WHITE, 38)
def s_why(t, d):
    t0 = T["why"]
    jungle(d, t, (200, 160, 110), (140, 100, 60))
    sh = 1 - E.ease_in_out_sine(pr(t, t0 + 0.5, t0 + 2.5))
    if sh > 0.02: pool(d, 540, 900, 320 * sh, 140 * sh)
    for i in range(8):
        x = 260 + i * 80; d.line([(x, 1060), (x + 30, 1090)], A(MUD_D, 1 - sh), 5)
    k = popk(t, t0 + 2.6, "bouncy")
    if k > 0: d.text(540, 620, "?", 160, A(WHITE, min(1, k)), k=1)
def s_order(t, d):
    t0 = T["order"]
    jungle(d, t, (60, 130, 90), (20, 60, 40))
    for i, (px, py) in enumerate(((340, 800), (560, 980), (760, 760))): pool(d, px, py, 70, 34)
    # reserve boundary: big shape on left expanding to cover pools
    e = ease(pr(t, t0 + 0.6, t0 + 2.6))
    cx_ = lerp(-200, 540, e); r = lerp(380, 430, e)
    for i in range(60):
        u = i / 60 * 2 * math.pi; d.circ(cx_ + math.cos(u) * r, 860 + math.sin(u) * r * 0.9, 7, fill=A((140, 255, 160), 0.9))
    k = popk(t, t0 + 2.7, "bouncy")
    if k > 0: tag(d, 540, 400, "卡雅里河保护区 + 水坑", GOLD, min(1, k), 40)
def s_card(t, d):
    flatbg(d, (40, 90, 80), (12, 36, 32), t, False)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    killi(d, cx_, cy_ - 170, 0.9, t, a=a_)
    d.text(cx_, cy_ + 10, "橙子鱼：刚发现就可能濒危", 42, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("体长不到 3 厘米", "只在 3 个林间水坑见过", "已知分布约 25 平方公里")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 120 + i * 78, s_, 38, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    jungle(d, t)
    for x in (150, 420, 700, 950): tree(d, x, 700, 1.2)
    pool(d, 540, 1000, 360, 150)
    killi(d, 540, 1000, 0.9, t)
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 285, "Abrantes et al. 2026 · Zoosyst. Evol.", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 330, "102(4):1079 · 濒危为作者评估建议", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "3个水坑", "q": "橙子", "who": "人字纹", "sperm": "DNA", "egg": "新物种", "reveal": "比澳门还小", "how": "浑水",
      "xray": "塑料", "swim": "濒危", "gene": "等雨回来", "why": "没用", "order": "圈进去", "end": "告别"}
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/kl_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/kl_sheet.png")
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
