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
def ocean(d, t, top=(30, 90, 150), bot=(6, 20, 50), surf=None):
    flatbg(d, top, bot, t, False)
    for i in range(14):  # rising bubbles
        rv = random.Random(i); bx = rv.uniform(80, 1000); sp = rv.uniform(40, 90)
        by = 1900 - ((t * sp + rv.uniform(0, 1900)) % 1900)
        d.circ(bx + 8 * math.sin(t + i), by, rv.uniform(5, 12), outline=A(WHITE, 0.25), w=3)
    if surf is not None:
        pts = [(x, surf + 14 * math.sin(x / 70 + t * 2)) for x in range(0, 1090, 30)]
        d.poly([(0, 0)] + pts + [(1080, 0)], A((150, 200, 240), 1))
def check(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 18 * s_, y), (x - 4 * s_, y + 14 * s_), (x + 20 * s_, y - 14 * s_)], A(WHITE, a), 8 * s_)
def xmark(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 15 * s_, y - 15 * s_), (x + 15 * s_, y + 15 * s_)], A(WHITE, a), 8 * s_); d.line([(x - 15 * s_, y + 15 * s_), (x + 15 * s_, y - 15 * s_)], A(WHITE, a), 8 * s_)
def bubble_txt(d, t, t0, x, y, s, col, size=70, tail=-1):
    k = popk(t, t0, "bouncy")
    if k <= 0: return
    sz = int(size * min(1.1, k)); w = d.tlen(s, sz, 1) + 60
    d.rect(x - w / 2, y - sz * 0.85, x + w / 2, y + sz * 0.85, fill=A(WHITE, 0.97), r=sz * 0.6)
    d.poly([(x + tail * 30, y + sz * 0.7), (x + tail * 80, y + sz * 1.5), (x + tail * 70, y + sz * 0.7)], A(WHITE, 0.97))
    d.text(x, y, s, sz, A(col, 1), k=1)
def wavebox(d, x0, y0, x1, y1, t, amp, noisy=0.0, col=MINT, a=1.0, call=0.0):
    d.rect(x0, y0, x1, y1, fill=A((6, 10, 24), 0.75 * a), r=20)
    cy = (y0 + y1) / 2; pts = []; rv = random.Random(int(t * 30))
    for i in range(80):
        xx = x0 + 20 + (x1 - x0 - 40) * i / 79
        v = noisy * rv.uniform(-1, 1) + call * math.sin(i / 3 + t * 6) * math.exp(-((i - 40) / 14) ** 2)
        pts.append((xx, cy + amp * v))
    d.line(pts, A(col, a), 5)
def depth(d, t, m, a=1.0):
    d.rect(905, 330, 965, 1150, fill=A(WHITE, 0.12 * a), r=30)
    yy = 340 + 800 * cl(m / 400)
    d.circ(935, yy, 24, fill=A(GOLD, a)); tag(d, 830, yy, "%d 米" % int(m), GOLD, a, 34)
def recbar(d, t, t0, a=1.0):
    d.rect(280, 330, 800, 410, fill=A((6, 10, 24), 0.7 * a), r=40)
    if int(t * 2.5) % 2 == 0: d.circ(330, 370, 16, fill=A((255, 70, 70), a))
    s_ = max(0, t - t0); d.text(560, 370, "REC  %02d:%02d:%02d" % (int(s_ * 900) // 3600, (int(s_ * 900) // 60) % 60, int(s_ * 900) % 60), 40, A(WHITE, a), k=1)

def s_hook(t, d):
    ocean(d, t)
    seal(d, 470, 920, 1.55, t, swim=0.3)
    k = popk(t, 0.05, "bouncy")
    if k > 0:
        tag(d, 380, 640, "窃听器", MEAN, min(1, k), 60)
        d.line([(430, 690), (470, 760)], A(MEAN, 1), 8)
    rings(d, 470, 760, t, [0.0, 0.9, 1.8], (255, 120, 120), 0.6, 300)
def s_q(t, d):
    ocean(d, t)
    t0 = T["q"]
    for i in range(9):
        x = 230 + (i % 3) * 310; y = 560 + (i // 3) * 230
        k = popk(t, t0 + 0.1 + i * 0.12)
        if k > 0: seal(d, x, y, 0.55 * min(1, k), t + i, swim=0.2, flip=1 if (i // 3) % 2 == 0 else -1)
    n = min(9, int(pr(t, t0, t0 + 1.2) * 9.99))
    ptag(d, t, t0 + 1.3, 540, 380, "%d只 · 全是雌性" % max(n, 1), PINK, 48)
    ptag(d, t, t0 + 1.8, 540, 1150, "头顶录音标签", GOLD, 44)
def s_trip(t, d):
    ocean(d, t, surf=420)
    t0 = T["trip"]; u = ease(pr(t, t0, t0 + 1.6))
    sx = lerp(-200, 540, u); stop = pr(t, t0 + 1.6, t0 + 2.0)
    seal(d, sx, 860, 1.0, t, swim=0.4 * (1 - stop), mood="sleep" if stop > 0.5 else "neutral", zz=stop > 0.5)
    for j in range(5):  # motion lines while swimming
        if stop < 0.5: d.line([(sx - 260 - j * 40, 820 + j * 20), (sx - 200 - j * 40, 820 + j * 20)], A(WHITE, 0.4), 5)
    ptag(d, t, t0 + 1.7, 540, 600, "歇一歇", MINT, 56)
def s_leaf(t, d):
    t0 = T["leaf"]; u = pr(t, t0, nxt("leaf"))
    ocean(d, t, mix((30, 90, 150), (14, 40, 90), u), mix((6, 20, 50), (2, 8, 24), u))
    ph = (t - t0) * 2.2
    x = 540 + 170 * math.sin(ph); y = 520 + 520 * u
    seal(d, x, y, 0.85, t, ang=0.35 * math.cos(ph), mood="sleep", flip=1 if math.cos(ph) > 0 else -1)
    for j in range(12):  # dashed falling-leaf path
        uu = j / 12; ph2 = ph - (1 - uu) * 3
        d.circ(540 + 170 * math.sin(ph2), y - (1 - uu) * 360, 6, fill=A(WHITE, 0.35 * uu))
    lk = popk(t, t0 + 0.5)
    if lk > 0:  # little leaf icon
        lx, ly = 220, 420 + 30 * math.sin(t * 2)
        d.ell(lx, ly, 46 * min(1, lk), 24 * min(1, lk), A(LEAF, 1)); d.line([(lx - 46, ly), (lx + 46, ly)], A(LEAF_D, 1), 4)
        tag(d, 220, 500, "像落叶", LEAF, min(1, lk), 40)
    xmark(d, 860, 420, 40, MEAN, 1, popk(t, t0 + 0.3)); tag(d, 860, 500, "不划水", MEAN, ap(t, t0 + 0.3), 36)
def s_deep(t, d):
    t0 = T["deep"]; u = pr(t, t0, SIL0)
    ocean(d, t, (10, 30, 70), (0, 4, 14))
    dim = 1 - 0.7 * pr(t, SIL0, SIL0 + 0.1)
    seal(d, 470, 820 + 20 * math.sin(t * 1.4), 1.1, t, mood="sleep", a=dim)
    glow(d, 450, 700, 160, (80, 200, 255), 0.12 * dim)
    depth(d, t, lerp(80, 320, ease(u)), dim)
    recbar(d, t, t0, dim)
    wavebox(d, 200, 1000, 800, 1140, t, 30, 0.15, MINT, dim)
def s_reveal(t, d):
    rays(d, t, (60, 150, 230), (10, 40, 110))
    t0 = BIG2
    seal(d, 540, 900, 1.1, t, phones=True, mood="happy", swim=0.2)
    for i, (kind, x, y, fl, dt) in enumerate((("blue", 300, 470, 1, 0.0), ("hump", 820, 560, -1, 0.25), ("sperm", 260, 1180, 1, 0.5), ("dolph", 850, 1160, -1, 0.7))):
        k = popk(t, t0 + dt, "bouncy")
        if k > 0: whale(d, x, y, 0.55 * min(1, k), t, kind, flip=fl, sing=True)
    for j in range(4):
        uu = ((t - t0) * 0.8 + j / 4) % 1
        d.circ(540, 830, 80 + 300 * uu, outline=A(WHITE, 0.5 * (1 - uu)), w=6)
    if t > t0: sparks(d, 540, 800, t, t0, 40, 1100, (180, 230, 255), 1, 3, 0.9)
def s_quiet(t, d):
    ocean(d, t)
    t0 = T["quiet"]
    d.rect(0, 0, 1080, 760, fill=A((120, 40, 60), 0.35)); d.rect(0, 760, 1080, 1250, fill=A((40, 140, 110), 0.3))
    seal(d, 300, 560, 0.6, t * 2, swim=1.0); tag(d, 300, 400, "划水：哗哗哗", MEAN, 1, 38)
    wavebox(d, 520, 470, 980, 650, t, 60, 1.0, MEAN)
    k = ap(t, t0 + 1.0, 0.2)
    seal(d, 300, 1010, 0.6, t, mood="sleep", a=max(0.3, k)); tag(d, 300, 850, "漂着：安静", MINT, k, 38)
    wavebox(d, 520, 920, 980, 1100, t, 60, 0.08, MINT, max(0.3, k), call=1.0 * k)
    if k > 0: whale(d, 760, 1180, 0.25, t, "hump", sing=True, a=k)
    ptag(d, t, t0 + 1.8, 540, 300, "天然窃听站", GOLD, 52)
def s_hours(t, d):
    ocean(d, t)
    t0 = T["hours"]
    h = int(lerp(0, 109, ease(pr(t, t0, t0 + 1.2))))
    d.rect(300, 330, 780, 520, fill=A((250, 248, 240), 1), r=30); d.text(540, 425, "%d小时" % h, 110, A(NAVYT, 1), k=1)
    kinds = ["blue", "hump", "sperm", "dolph", "blue", "hump", "sperm"]
    for i in range(7):
        x = 210 + (i % 4) * 220 + (110 if i >= 4 else 0); y = 700 + (i // 4) * 220
        k = popk(t, t0 + 1.0 + i * 0.15)
        if k <= 0: continue
        d.circ(x, y, 90 * min(1, k), fill=A(WHITE, 0.15))
        whale(d, x + 10, y, 0.25 * min(1, k), t, kinds[i] if i < 4 else ["blue", "hump", "blue"][i - 4], a=1)
        d.text(x, y + 70, str(i + 1), 34, A(GOLD, 1), k=1)
    ptag(d, t, t0 + 2.2, 540, 1200, "7种鲸", GOLD, 56)
def s_blue(t, d):
    ocean(d, t, (40, 110, 190), (10, 30, 80))
    t0 = T["blue"]; u = pr(t, t0, nxt("blue"))
    whale(d, lerp(1500, -350, u), 640, 1.6, t, "blue", flip=-1, sing=True)
    seal(d, 300, 1050, 0.6, t, phones=True, mood="happy")
    # spectrogram strip: low-frequency stripes
    d.rect(160, 330, 920, 470, fill=A((6, 10, 24), 0.8), r=20)
    for j in range(30):
        xx = 180 + j * 24; on = (j + int(t * 8)) % 8 < 5
        if on: d.rect(xx, 430 - 6 * math.sin(j), xx + 18, 450, fill=A(GOLD, 0.9), r=4)
    d.text(540, 365, "低频长鸣", 32, A(WHITE, 0.9), k=1)
    ptag(d, t, t0 + 0.8, 660, 1180, "录到它的漂流段：134段", GOLD, 40)
def s_more(t, d):
    ocean(d, t)
    t0 = T["more"]
    for i, (kind, lab, x, y) in enumerate((("hump", "座头鲸", 540, 520), ("sperm", "抹香鲸", 540, 820), ("dolph", "海豚", 540, 1100))):
        k = popk(t, t0 + i * 0.5, "bouncy")
        if k <= 0: continue
        whale(d, x - 60, y, 0.85 * min(1, k), t, kind, flip=1, sing=True)
        tag(d, 260 if i != 1 else 820, y - 120, lab, [CYAN2, GOLD, PINK][i], min(1, k), 44)
def s_why(t, d):
    t0 = T["why"]
    ocean(d, t, (40, 60, 90), (10, 14, 30), surf=None)
    d.rect(0, 0, 1080, 640, fill=A((60, 66, 84), 1))
    for j in range(30):  # rain
        rv = random.Random(j); x = (rv.uniform(0, 1080) + t * 300) % 1080; y = (rv.uniform(0, 640) + t * 900) % 640
        d.line([(x, y), (x - 12, y + 34)], A(WHITE, 0.4), 3)
    pts = [(x, 640 + 50 * math.sin(x / 90 + t * 3)) for x in range(0, 1090, 30)]
    d.poly([(0, 1920)] + pts + [(1080, 1920)], A((30, 70, 120), 1))
    bx, by = 380, 600 + 50 * math.sin(380 / 90 + t * 3); r_ = 0.25 * math.sin(t * 3)
    d.poly([rot(bx - 120, by - 20, bx, by, r_), rot(bx + 120, by - 20, bx, by, r_), rot(bx + 80, by + 40, bx, by, r_), rot(bx - 90, by + 40, bx, by, r_)], A((230, 230, 235), 1))
    d.poly([rot(bx - 10, by - 20, bx, by, r_), rot(bx - 10, by - 140, bx, by, r_), rot(bx + 70, by - 30, bx, by, r_)], A((240, 240, 245), 1))
    xmark(d, 620, 430, 46, MEAN, 1, popk(t, t0 + 0.5)); tag(d, 620, 520, "船难去", MEAN, ap(t, t0 + 0.5), 38)
    seal(d, 540, 1050, 0.8, t, swim=0.3, phones=True)
    check(d, 760, 900, 46, MINT, 1, popk(t, t0 + 2.0)); tag(d, 760, 985, "海豹去", MINT, ap(t, t0 + 2.0), 38)
def s_back(t, d):
    t0 = T["back"]
    flatbg(d, (150, 200, 230), (90, 150, 200), t, False)
    d.rect(0, 1050, 1080, 1920, fill=A((230, 210, 170), 1))
    pts = [(x, 1050 + 16 * math.sin(x / 60 + t * 2)) for x in range(0, 1090, 30)]
    d.poly([(0, 1000)] + pts + [(1080, 1000)], A((80, 150, 200), 1))
    u = ease(pr(t, t0, t0 + 1.0))
    off = pr(t, t0 + 1.6, t0 + 2.4)
    seal(d, lerp(-100, 420, u), 960, 0.95, t, tag=off < 0.5, mood="happy" if off > 0.5 else "neutral")
    for j in range(5):  # moulting patches
        d.circ(lerp(-100, 420, u) - 80 + j * 40, 930 + (j % 2) * 30, 14, fill=A(SEAL_L, 0.9))
    hx = 820; d.circ(hx, 760, 40, fill=A((250, 205, 170), 1)); d.rect(hx - 50, 800, hx + 50, 960, fill=A((240, 120, 60), 1), r=20)
    gx, gy = lerp(500, hx - 70, off), lerp(820, 860, off)
    if off > 0: d.rect(gx - 32, gy - 14, gx + 30, gy + 16, fill=A((40, 46, 60), 1)); 
    ptag(d, t, t0 + 0.6, 300, 600, "1月 · 回岸换毛", GOLD, 44)
    if off >= 1: tag(d, hx, 1010, "取回标签", MINT, ap(t, t0 + 2.4), 38)
def s_card(t, d):
    flatbg(d, (24, 50, 100), (8, 16, 40), t, False)
    for i in range(12): d.circ(540, 820, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    seal(d, cx_ - 20, cy_ - 160, 0.6, t, phones=True, mood="happy", a=a_)
    d.text(cx_, cy_ + 20, "海豹 = 会游泳的窃听站", 48, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("休息时像落叶往下漂", "不划水，录音就干净", "9只海豹录到7种鲸")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 130 + i * 78, s_, 42, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    ocean(d, t)
    t0 = T["end"]
    seal(d, 420, 950, 1.0, t, mood="sleep", phones=True, zz=True, ang=0.1 * math.sin(t))
    whale(d, 720, 600, 0.55, t, "hump", flip=-1, sing=True)
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 290, "Gros-Martial 等 2026 · Front. Mar. Sci.", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 335, "9只南象海豹 · 2017–2020 · DTAG4 录音", 25, A(WHITE, 0.85 * ra), k=1)
        d.text(540, 372, "doi:10.3389/fmars.2026.1832052", 22, A(WHITE, 0.75 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "窃听器", "q": "录音标签", "trip": "休息", "leaf": "落叶", "deep": "几百米", "reveal": "偷听鲸鱼", "quiet": "窃听站", "hours": "7种鲸",
      "blue": "南极蓝鲸", "more": "抹香鲸", "why": "海豹替人", "back": "换毛", "end": "鲸鱼全露馅"}
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/sl_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/sl_sheet.png")
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
