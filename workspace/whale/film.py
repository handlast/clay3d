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
def sea(d, t, top=(40, 110, 150), bot=(10, 30, 60)): flatbg(d, top, bot, t, False)
def bubbles_bg(d, t, n=14):
    for i in range(n):
        x = 180 + (i * 97) % 720; y = 1500 - ((t * 60 + i * 140) % 1400)
        d.circ(x, y, 6 + i % 4 * 3, fill=A(WHITE, 0.18))
def s_hook(t, d):
    sea(d, t)
    bubbles_bg(d, t)
    if t < 0.3: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - t / 0.3)))
    whale_front(d, 540, 800, 1.5 + 0.03 * math.sin(t * 2), t, skew=1.0, glow=pr(t, 0.2, 0.8))
    k = popk(t, 0.9, "bouncy")
    if k > 0:
        d.line([(300, 430), (390, 520)], A(GOLD, min(1, k)), 10); d.line([(390, 520), (350, 520)], A(GOLD, min(1, k)), 10); d.line([(390, 520), (390, 480)], A(GOLD, min(1, k)), 10)
        tag(d, 300, 400, "鼻孔×2", GOLD, min(1, k), 44)
    ptag(d, t, 1.8, 760, 400, "右边：空", WHITE, 40)
def s_q(t, d):
    t0 = T["q"]
    flatbg(d, (210, 180, 130), (150, 110, 70), t, False)
    skull_top(d, 540, 820, 1.4, skew=1.0, line=False)
    k1 = popk(t, t0 + 0.4)
    if k1 > 0:
        tag(d, 540, 420, "被压扁？", (200, 70, 70), min(1, k1), 44)
        kx = pr(t, t0 + 1.2, t0 + 1.5)
        if kx > 0:
            d.line([(400, 420), (400 + 280 * kx, 420)], A((220, 40, 40), 0.9), 8)
    ptag(d, t, t0 + 1.8, 540, 1150, "骨缝完整 · 没有裂痕", (60, 160, 100), 40, tc=WHITE)
def s_who(t, d):
    t0 = T["who"]
    sea(d, t, (60, 140, 160), (20, 60, 80))
    whale_side(d, 520, 760, 1.1, t, snout=31)
    # ruler 2.7 m vs person 1.7 m
    e = pr(t, t0 + 1.2, t0 + 2.4)
    if e > 0:
        x0, x1 = 160, 160 + 740 * e
        d.line([(x0, 1000), (x1, 1000)], A(GOLD, 1), 8)
        if e >= 1: d.text(540, 1030, "约 2.7 米", 44, A(GOLD, 1), k=1)
    ptag(d, t, t0 + 0.4, 540, 470, "600 万年前 · 秘鲁", WHITE, 40)
def s_sperm(t, d):
    t0 = T["sperm"]
    flatbg(d, (230, 236, 240), (190, 200, 210), t, False)
    skull_top(d, 540, 820, 1.3, skew=0.25 * ap(t, t0 + 0.5, 0.8))
    ptag(d, t, t0 + 0.3, 540, 440, "普通齿鲸头骨", NAVYT, 40, tc=WHITE)
    ptag(d, t, t0 + 1.6, 790, 820, "中线", (255, 90, 90), 36, tc=WHITE)
def s_egg(t, d):
    t0 = T["egg"]
    dim = 1 - 0.45 * pr(t, SIL0, SIL0 + 0.15)
    flatbg(d, (40, 50, 80), (12, 16, 30), t, False)
    # meter dial
    cx_, cy_ = 540, 900; r = 260
    for i in range(11):
        u = math.pi + i / 10 * math.pi
        d.line([(cx_ + math.cos(u) * r, cy_ + math.sin(u) * r), (cx_ + math.cos(u) * (r - 40), cy_ + math.sin(u) * (r - 40))], A(WHITE, 0.8 * dim), 6)
    v = 0.15 + 0.8 * ease(pr(t, t0 + 0.8, t0 + 4.0)) + 0.02 * math.sin(t * 20)
    u = math.pi + v * math.pi
    d.line([(cx_, cy_), (cx_ + math.cos(u) * (r - 30), cy_ + math.sin(u) * (r - 30))], A((255, 90, 90), dim), 12); d.circ(cx_, cy_, 20, fill=A(WHITE, dim))
    d.text(cx_, cy_ + 50, "歪度计", 44, A(WHITE, dim), k=1)
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (120, 200, 240), (30, 80, 140))
    if t > t0: sparks(d, 540, 760, t, t0, 30, 900, (255, 240, 200), 1, 3, 0.9)
    k = popk(t, t0 + 0.05, "bouncy")
    if k > 0:
        skull_top(d, 540, 820, 1.3 * min(1.05, k), skew=2.2)
        tag(d, 540, 430, "最歪 No.1", GOLD, min(1, k), 60)
def s_how(t, d):
    t0 = T["how"]
    flatbg(d, (250, 240, 220), (220, 200, 170), t, False)
    rows = (("人", 0.05, (150, 150, 160)), ("海豚", 0.35, (120, 160, 200)), ("抹香鲸", 0.6, (100, 130, 170)), ("歪脸鲸", 1.0, (255, 120, 60)))
    for i, (nm, v, c) in enumerate(rows):
        y = 520 + i * 160; e = ease(pr(t, t0 + 0.3 + i * 0.4, t0 + 0.9 + i * 0.4))
        d.text(260, y - 26, nm, 40, A(NAVYT, 1), k=1)
        if e > 0: d.rect(340, y - 40, 340 + 520 * v * e + 10, y + 40, fill=A(c, 1), r=20)
    ptag(d, t, t0 + 2.4, 540, 1180, "头骨不对称程度（示意）", NAVYT, 34, tc=WHITE)
def s_xray(t, d):
    t0 = T["xray"]
    flatbg(d, (30, 60, 90), (8, 20, 36), t, False)
    g = ease(pr(t, t0 + 0.3, t0 + 3.2))
    skull_top(d, 540, 860, 1.3, skew=0.3 + 1.8 * g, line=False)
    d.ell(540 + 60 * g, 640, 70 + 70 * g, 90 + 60 * g, A((255, 200, 120), 0.75))
    for i in range(3):
        rr = 60 + ((t * 120 + i * 60) % 180)
        d.arc(540 + 60 * g, 520, rr, rr * 0.6, 200, 340, A((255, 220, 150), 0.6 * (1 - rr / 240)), 6)
    ptag(d, t, t0 + 0.8, 800, 520, "声呐器官", (255, 180, 80), 36, tc=NAVYT)
def s_swim(t, d):
    t0 = T["swim"]
    sea(d, t, (60, 140, 160), (20, 60, 80))
    sn = 31 * ease(pr(t, t0 + 0.3, t0 + 1.2)); nk = 55 * ease(pr(t, t0 + 1.8, t0 + 2.8))
    whale_side(d, 470, 700, 1.0, t, snout=sn, neck=nk)
    ptag(d, t, t0 + 0.6, 800, 450, "嘴 31°", GOLD, 40, tc=NAVYT)
    ptag(d, t, t0 + 2.0, 800, 1100, "脖子 55°", GOLD, 40, tc=NAVYT)
def s_gene(t, d):
    t0 = T["gene"]
    sea(d, t, (60, 120, 130), (30, 60, 70))
    d.rect(0, 1000, OW, OH, fill=A(SEAF, 1))
    sx, sy = whale_side(d, 470, 760, 0.9, t, snout=31, neck=40)
    for i in range(4):
        rr = 40 + ((t * 200 + i * 70) % 280)
        d.arc(sx, sy, rr, rr * 0.7, 30, 150, A((255, 230, 150), 0.7 * (1 - rr / 320)), 6)
    k = popk(t, t0 + 1.6, "bouncy")
    if k > 0:
        for j, x in enumerate((520, 640, 760)):
            d.ell(x, 1120 + j * 20, 30 * min(1, k), 14 * min(1, k), A((255, 160, 170), 1))
    ptag(d, t, t0 + 2.2, 540, 1240, "推测", WHITE, 34, tc=NAVYT)
def s_why(t, d):
    t0 = T["why"]
    flatbg(d, (90, 70, 120), (30, 20, 50), t, False)
    whale_front(d, 540, 820, 1.2, t, skew=1.0)
    k = popk(t, t0 + 0.4)
    if k > 0:
        for j in range(3):
            y = 900 + j * 30
            d.line([(240, y), (360, y + 10)], A(WHITE, 0.8 * min(1, k)), 5)
        kx = pr(t, t0 + 1.0, t0 + 1.3)
        if kx > 0: d.line([(220, 860), (380, 1000)], A((230, 50, 50), kx), 12); d.line([(220, 1000), (380, 860)], A((230, 50, 50), kx), 12)
        tag(d, 300, 800, "胡须", WHITE, min(1, k), 34)
    for i in range(3):
        rr = 40 + ((t * 160 + i * 60) % 200)
        d.arc(500, 640, rr, rr * 0.6, 200, 340, A((255, 220, 150), 0.6 * (1 - rr / 260)), 6)
def s_order(t, d):
    t0 = T["order"]
    rays(d, t, (255, 120, 200), (120, 40, 140))
    k = popk(t, t0 + 0.3, "bouncy")
    if k > 0:
        s_ = min(1, k); d.rect(220, 620, 860, 820, fill=A(GOLD, s_), r=40)
        d.text(540, 670, "huachafo", 84, A(NAVYT, s_), k=1)
    for i in range(12):
        u = t * 1.5 + i / 12 * 2 * math.pi
        d.circ(540 + math.cos(u) * 380, 720 + math.sin(u) * 260, 10, fill=A((255, 250, 200), 0.9 * ap(t, t0 + 0.8)))
    ptag(d, t, t0 + 1.4, 540, 1000, "浮夸 · 花哨 · 不好归类", WHITE, 38, tc=NAVYT)
def s_card(t, d):
    flatbg(d, (40, 80, 110), (12, 28, 44), t, False)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    whale_front(d, cx_, cy_ - 170, 0.55, t, a=a_)
    d.text(cx_, cy_ + 10, "歪脸鲸：史上最歪的鲸", 42, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("两个鼻孔全在左边", "声呐器官把头骨挤歪", "嘴朝下，专吃海底")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 120 + i * 78, s_, 38, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    sea(d, t, (60, 120, 130), (30, 60, 70))
    d.rect(0, 1050, OW, OH, fill=A(SEAF, 1))
    whale_side(d, 470, 800, 0.9, t, snout=31, neck=35)
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 285, "Benites-Palomino et al. 2026", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 330, "Communications Biology · 化石约 600 万年前", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "左边", "q": "天生就歪", "who": "2.7米", "sperm": "有点歪", "egg": "什么程度", "reveal": "最歪", "how": "哺乳动物", "xray": "越歪",
      "swim": "55度", "gene": "声呐", "why": "歪头", "order": "浮夸", "end": "吃饭"}
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
    s = "Vibe 知识大赏 · 新物种"; w = d.tlen(s, 28, 1) + 50
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/wh_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/wh_sheet.png")
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
