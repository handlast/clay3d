import random
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
def s_hook(t, d):
    snowbg(d, t, (20, 30, 60), (70, 95, 140))
    if t < 0.3: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.7 * (1 - t / 0.3)))
    k = popk(t, 0.0, "bouncy")
    simo(d, 600, 1110, 1.3 * min(1.05, max(0.4, k)), t, face="aim", breath=0.0)
    thermo2(d, 880, 640, max(0.05, 0.9 - 0.85 * ease(pr(t, 0.2, 1.2))))
    kk = popk(t, 0.3, "bouncy")
    if kk > 0: d.text(440, 520, "-40°", int(220 * min(1, kk)), A((150, 210, 255), 1), k=1)
    ptag(d, t, 1.4, 440, 700, "一趴一整天", GOLD, 50)
def s_q(t, d):
    t0 = T["q"]
    flatbg(d, (230, 238, 250), (180, 196, 222), t, False)
    k = popk(t, t0 + 0.1, "smooth")
    if k > 0:
        a_ = ap(t, t0 + 0.1)
        d.rect(230, 420, 850, 1220, fill=A((24, 32, 52), a_), r=36)
        simo(d, 540, 620, 1.5 * (0.85 + 0.15 * k), t, a_, pose="stand")
        d.rect(300, 1050, 780, 1200, fill=A((24, 32, 52), a_), r=20)
        d.text(540, 1090, "西莫·海耶", 56, A(WHITE, a_), k=1)
        d.text(540, 1160, "芬兰 · 狙击手", 32, A((180, 196, 222), a_), k=1)
    kk = popk(t, t0 + 1.2, "bouncy")
    if kk > 0: tag(d, 540, 360, "白色死神", (230, 70, 70), min(1, kk), 64, tc=WHITE)
def s_who(t, d):
    t0 = T["who"]
    snowbg(d, t, (60, 80, 120), (150, 170, 205))
    k = popk(t, t0 + 0.1, "bouncy")
    if k > 0:
        w = 260 * min(1, k)
        d.rect(540 - w, 420, 540 + w, 620, fill=A(WHITE, 1), r=24)
        d.rect(540 - w, 420, 540 + w, 490, fill=A((60, 110, 200), 1), r=24)
        d.text(540, 455, "冬季战争", 36, A(WHITE, 1), k=1); d.text(540, 560, "1939–1940", 64, A(NAVYT, 1), k=1)
    for i in range(5):
        x = 200 + i * 170; kk = popk(t, t0 + 1.0 + i * 0.15, "bouncy")
        if kk > 0: simo(d, x, 1000, 0.55 * min(1, kk), t + i, pose="stand")
    ptag(d, t, t0 + 2.0, 540, 760, "芬兰 vs 苏联", GOLD, 44)
def s_sperm(t, d):
    t0 = T["sperm"]
    snowbg(d, t, (90, 120, 170), (190, 210, 235), pines=False)
    hide = ease(pr(t, t0 + 1.8, t0 + 2.6))
    if hide < 1:
        simo(d, 420, 760, 1.4, t, 1 - hide, pose="stand")
        d.line([(640, 1150), (640, 700)], A(NAVYT, 1 - hide), 6)
        for yy in (700, 1150): d.line([(620, yy), (660, yy)], A(NAVYT, 1 - hide), 6)
        d.text(740, 920, "1.6米", 56, A(NAVYT, (1 - hide) * ap(t, t0 + 0.4)), k=1)
    if hide > 0:
        simo(d, 560, 1140, 1.2, t, 0.25 + 0.15 * math.sin(t * 2), face="aim")
        ptag(d, t, t0 + 2.4, 540, 900, "找到他了吗？", WHITE, 44)
def s_egg(t, d):
    t0 = T["egg"]
    dim = 1 - 0.45 * pr(t, SIL0, SIL0 + 0.15)
    snowbg(d, t, (10, 16, 30), (40, 55, 85), flakes=True)
    simo(d, 560, 1100, 1.3, t, dim, face="aim", breath=dim)
    k = popk(t, t0 + 0.5, "bouncy")
    if k > 0:
        d.circ(780, 960, 120 * min(1, k), outline=A((255, 90, 90), dim), w=8)
        d.text(860, 760, "?", int(160 * min(1, k)), A(GOLD, dim), k=1)
    ptag(d, t, t0 + 1.4, 540, 560, "白气会暴露", (255, 90, 90), 44, tc=WHITE)
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (200, 230, 255), (40, 80, 150))
    if t > t0: sparks(d, 540, 760, t, t0, 40, 1000, (230, 245, 255), 1, 3, 0.9)
    ch = ease(pr(t, t0 + 0.2, t0 + 0.7))
    simo(d, 540, 760, 3.0, t, pose="stand", cheeks=ch)
    for i in range(6):
        u = 1 - ease(pr(t, t0 + 0.05 + i * 0.04, t0 + 0.5 + i * 0.04))
        if u > 0: d.circ(560 + 300 * u * math.cos(i), 840 - 260 * u, 18, fill=A(WHITE, 1))
    ptag(d, t, t0 + 0.4, 540, 330, "含雪", GOLD, 90)
def s_how(t, d):
    t0 = T["how"]
    snowbg(d, t, (30, 45, 80), (90, 115, 160), pines=False)
    d.line([(140, 900), (940, 900)], A(WHITE, 0.6), 4)
    simo(d, 560, 780, 0.95, t, face="aim", breath=1.0)
    simo(d, 560, 1130, 0.95, t, face="aim", cheeks=1.0, breath=0.0)
    k1 = popk(t, t0 + 0.2, "bouncy"); k2 = popk(t, t0 + 0.8, "bouncy")
    if k1 > 0: tag(d, 300, 560, "不含雪：冒白气", (230, 70, 70), min(1, k1), 40, tc=WHITE)
    if k2 > 0: tag(d, 300, 960, "含雪：不冒", (60, 180, 110), min(1, k2), 40, tc=WHITE)
def s_xray(t, d):
    t0 = T["xray"]
    snowbg(d, t, (60, 80, 120), (160, 180, 215), pines=False)
    packed = t > t0 + 2.2
    simo(d, 520, 1000, 1.2, t, face="aim")
    d.ell(830, 1060, 120, 50 + (10 if packed else 0), A(SNOWC if not packed else (220, 230, 246), 1))
    shot = (t - t0) % 1.1 < 0.25 and t > t0 + 0.5
    if shot and not packed:
        for i in range(14):
            d.circ(840 + 20 * math.cos(i), 980 - 40 * ((t - t0) % 1.1) * 10 * (0.3 + (i % 3) * 0.3), 18, fill=A(WHITE, 0.85))
    if shot: d.circ(1000, 1000, 16, fill=A((255, 230, 120), 1))
    tag(d, 540, 600, "压实雪堆" if packed else "松雪会扬起", (60, 180, 110) if packed else (230, 70, 70), ap(t, t0 + 0.3), 44, tc=WHITE)
def s_swim(t, d):
    t0 = T["swim"]
    snowbg(d, t, (30, 45, 80), (110, 135, 180), pines=False, flakes=True)
    fog = ease(pr(t, t0 + 0.4, t0 + 1.4)); gl = abs(math.sin(t * 3)) * ap(t, t0 + 0.8)
    scope(d, 300, 820, 170, fog=fog, glint=gl)
    d.text(300, 1060, "瞄准镜", 44, A(WHITE, 1), k=1)
    tag(d, 300, 560, "起雾 · 反光", (230, 70, 70), ap(t, t0 + 1.0), 36, tc=WHITE)
    k = popk(t, t0 + 1.6, "bouncy")
    if k > 0:
        kk = min(1, k)
        d.rect(640, 800, 960, 830, fill=A((70, 74, 84), kk), r=8)
        d.poly([(900, 800), (920, 750), (940, 800)], A((70, 74, 84), kk))
        d.rect(660, 770, 700, 800, fill=A((70, 74, 84), kk))
        d.text(800, 1060, "铁瞄", 44, A(WHITE, kk), k=1)
        tag(d, 800, 560, "不起雾", (60, 180, 110), kk, 36, tc=WHITE)
def s_gene(t, d):
    t0 = T["gene"]
    flatbg(d, (230, 238, 250), (180, 196, 222), t, False)
    simo(d, 540, 640, 1.6, t, pose="stand")
    items = [(300, 1080, "s"), (420, 1130, "s"), (680, 1100, "b"), (800, 1070, "s")]
    for i, (x, y, kd) in enumerate(items):
        k = popk(t, t0 + 0.3 + i * 0.35, "bouncy")
        if k <= 0: continue
        (sugar if kd == "s" else bread)(d, x, y, 1.3 * min(1, k))
    e = ease(pr(t, t0 + 1.8, t0 + 3.2))
    d.rect(240, 1150, 840, 1185, fill=A((40, 50, 70), 1), r=18)
    d.rect(240, 1150, 240 + 600 * e, 1185, fill=A((255, 150, 60), 1), r=20)
    ptag(d, t, t0 + 1.6, 540, 360, "补热量", GOLD, 54)
def s_why(t, d):
    t0 = T["why"]
    flatbg(d, (24, 32, 52), (10, 14, 26), t, False)
    e1 = ease(pr(t, t0 + 0.2, t0 + 1.4)); e2 = ease(pr(t, t0 + 1.4, t0 + 2.6))
    d.rect(150, 560, 520, 960, fill=A((40, 54, 84), 1), r=30); d.rect(560, 560, 930, 960, fill=A((40, 54, 84), 1), r=30)
    d.text(335, 620, "军方记录", 36, A((180, 196, 222), 1), k=1); d.text(745, 620, "他的回忆录", 36, A((180, 196, 222), 1), k=1)
    d.text(335, 780, str(int(259 * e1)), 120, A(WHITE, 1), k=1); d.text(745, 780, ("约" + str(int(500 * e2))) if e2 > 0 else "…", 100, A(WHITE, 1), k=1)
    ptag(d, t, t0 + 2.6, 540, 1080, "数字有争议", (230, 150, 60), 44, tc=WHITE)
    ptag(d, t, t0 + 0.4, 540, 440, "不到100天", GOLD, 44)
def s_order(t, d):
    t0 = T["order"]
    flatbg(d, (40, 30, 40), (14, 10, 18), t, False)
    k = popk(t, t0 + 0.1, "bouncy")
    if k > 0:
        w = 240 * min(1, k)
        d.rect(540 - w, 420, 540 + w, 620, fill=A(WHITE, 1), r=24); d.rect(540 - w, 420, 540 + w, 490, fill=A((200, 60, 60), 1), r=24)
        d.text(540, 455, "1940", 36, A(WHITE, 1), k=1); d.text(540, 560, "3月6日", 64, A(NAVYT, 1), k=1)
    hit = t0 + 1.3
    if hit < t < hit + 0.12: d.rect(0, 0, OW, OH, fill=A((255, 240, 240), 0.5))
    simo(d, 540, 780, 1.5, t, pose="stand", bandage=ease(pr(t, hit + 0.4, hit + 1.0)), face="calm")
    ptag(d, t, hit + 1.4, 540, 1180, "一周后醒来，正好停战", GOLD, 36)
def s_card(t, d):
    flatbg(d, (60, 80, 120), (20, 30, 50), t, False)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    simo(d, cx_, cy_ - 190, 1.0, t, a_, pose="stand")
    d.text(cx_, cy_ + 60, "雪地隐身三招", 44, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("嘴里含雪：不冒白气", "压实雪堆：开枪不扬雪", "用铁瞄：不起雾不反光")):
        kk = ap(t, at("card", 1.5 + i * 2.0), 0.25)
        if kk > 0: d.text(cx_, cy_ + 160 + i * 78, s_, 36, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    snowbg(d, t, (120, 150, 190), (210, 225, 240))
    simo(d, 420, 820, 1.3, t, pose="stand", old=True)
    dog(d, 740, 1080, 1.1, t)
    k = popk(t, t0 + 1.2, "bouncy")
    if k > 0: tag(d, 600, 560, "“练习。”", WHITE, min(1, k), 60)
    ra = ap(t, t0 + 2.6, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 285, "资料：Saarelainen《The White Sniper》2016", 24, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 330, "芬兰JR34团作战记录", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "一整天", "q": "白色死神", "who": "冬季战争", "sperm": "1.6米", "egg": "不被发现", "reveal": "含雪", "how": "白气", "xray": "压实", "swim": "铁瞄", "gene": "糖和面包", "why": "259", "order": "下颌", "end": "练习"}
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
    s = "Vibe 知识大赏 · 超级士兵 No.01"; w = d.tlen(s, 28, 1) + 50
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/sm_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/sm_sheet.png")
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
