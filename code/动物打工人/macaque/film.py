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
def bugs_on_web(d, t, cx, cy, R, n, s, a=1.0, seed=3, spd=0.25, orbit=False):
    rr = random.Random(seed)
    for i in range(n):
        r0 = R * rr.uniform(0.3, 0.95); an = rr.uniform(0, 6.28) + (t * spd * (1 if i % 2 else -0.7) if orbit else 0)
        if not orbit:
            r0 = R * (0.3 + 0.6 * ((rr.random() + t * 0.05 * (1 + i % 3)) % 1))
            an = round(an / (2 * math.pi / 12)) * (2 * math.pi / 12)
        webbug(d, cx + r0 * math.cos(an), cy + r0 * math.sin(an), s, t + i, a)
def s_hook(t, d):
    forest_bg(d, t)
    if t < 0.3: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - t / 0.3)))
    web(d, 540, 820, 470, 1, t=t)
    k = popk(t, 0.0, "bouncy")
    spider(d, 540, 760, 1.25 * min(1.05, max(0.3, k)), t)
    for i in range(5):
        kk = popk(t, 0.3 + i * 0.25, "bouncy")
        if kk > 0:
            an = i * 1.25 + t * 0.4; r0 = 330
            webbug(d, 540 + r0 * math.cos(an), 820 + r0 * math.sin(an) * 0.9, 1.1 * min(1, kk), t + i)
    ptag(d, t, 1.6, 540, 1170, "不吃？", GOLD, 60)
def s_q(t, d):
    t0 = T["q"]
    flatbg(d, (230, 236, 246), (190, 200, 220), t, False)
    k = popk(t, t0 + 0.2, "bouncy")
    salt(d, 360, 820, 130 * min(1, k))
    k2 = popk(t, t0 + 0.8, "bouncy")
    if k2 > 0: webbug(d, 730, 830, 2.6 * min(1, k2), t)
    d.text(360, 1010, "盐粒", 44, A(NAVYT, ap(t, t0 + 0.3)), k=1); d.text(720, 1010, "新虫", 44, A(BUGR, ap(t, t0 + 0.9)), k=1)
    e = ease(pr(t, t0 + 1.4, t0 + 2.0))
    if e > 0:
        d.line([(600, 1090), (600 + 260 * e, 1090)], A(NAVYT, 1), 8)
        for xx in (600, 600 + 260 * e): d.line([(xx, 1070), (xx, 1110)], A(NAVYT, 1), 6)
        d.text(730, 1140, "约1毫米", 40, A(NAVYT, e), k=1)
    ptag(d, t, t0 + 0.1, 540, 560, "放大看", NAVYT, 32, tc=WHITE)
def s_who(t, d):
    t0 = T["who"]
    forest_bg(d, t, (60, 110, 80), (20, 44, 34))
    web(d, 540, 940, 380, 0.8)
    for i in range(3): webbug(d, 540 + 160 * math.cos(i * 2.1 + t * 0.3), 940 + 160 * math.sin(i * 2.1 + t * 0.3), 0.7, t + i)
    k = popk(t, t0 + 0.1, "bouncy")
    if k > 0:
        cx_, cy_ = 540, 520; w = 230 * min(1, k)
        d.rect(cx_ - w, cy_ - 80, cx_ + w, cy_ + 90, fill=A(WHITE, 1), r=24)
        d.rect(cx_ - w, cy_ - 80, cx_ + w, cy_ - 20, fill=A((230, 80, 70), 1), r=24)
        d.text(cx_, cy_ - 50, "2025", 36, A(WHITE, 1), k=1); d.text(cx_, cy_ + 35, "9月", 64, A(NAVYT, 1), k=1)
    ptag(d, t, t0 + 1.4, 540, 1150, "福建 · 野外调查", GOLD, 38)
    mx = 540 + 260 * math.cos(t * 1.4); my = 940 + 120 * math.sin(t * 1.9)
    d.circ(mx, my, 90, outline=A(WHITE, 0.9), w=12); d.line([(mx + 64, my + 64), (mx + 140, my + 140)], A(WHITE, 0.9), 16)
def s_sperm(t, d):
    t0 = T["sperm"]
    flatbg(d, (255, 240, 220), (240, 200, 170), t, False)
    k = popk(t, t0 + 0.1, "smooth")
    if k > 0:
        a_ = ap(t, t0 + 0.1)
        d.rect(220, 420, 860, 1180, fill=A(WHITE, a_), r=36)
        tag(d, 540, 480, "新物种", (230, 80, 70), a_, 40, tc=WHITE)
        webbug(d, 540, 760, 4.0 * (0.85 + 0.15 * k), t, a_)
        d.text(540, 1000, "Heissophila", 48, A(NAVYT, a_), k=1); d.text(540, 1060, "sinica", 48, A(NAVYT, a_), k=1)
        d.text(540, 1125, "网栖蝽 · 同属第2种", 30, A((90, 90, 110), ap(t, t0 + 1.4)), k=1)
def s_egg(t, d):
    t0 = T["egg"]
    dim = 1 - 0.45 * pr(t, SIL0, SIL0 + 0.15)
    flatbg(d, (30, 40, 50), (8, 12, 18), t, False)
    web(d, 540, 860, 420, 0.5 * dim)
    webbug(d, 540, 860, 2.2, t, dim, walk=0.3)
    k = popk(t, t0 + 0.5, "bouncy")
    if k > 0: d.text(700, 650, "?", int(160 * min(1, k)), A(GOLD, dim), k=1)
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (255, 200, 90), (200, 90, 60))
    if t > t0: sparks(d, 540, 820, t, t0, 30, 900, (255, 240, 200), 1, 3, 0.9)
    spider(d, 540, 640, 0.9, t, eat=1.0)
    d.ell(540, 760, 40, 26, A((90, 80, 70), 1))      # prey (fly) in mouth
    for i in range(6):
        u = ((t - t0) * 0.8 + i / 6) % 1
        cx_, cy_ = 540 + (i - 2.5) * 60, 820 + u * 360
        d.circ(cx_, cy_, 10, fill=A((150, 120, 100), 1 - u * 0.5))
    for i in range(4):
        kk = popk(t, t0 + 0.3 + i * 0.15, "bouncy")
        if kk > 0: webbug(d, 300 + i * 160, 1180, 1.4 * min(1, kk), t + i, sip=abs(math.sin(t * 10 + i)))
    ptag(d, t, t0 + 0.5, 540, 340, "剩饭", GOLD, 70)
def s_how(t, d):
    t0 = T["how"]
    forest_bg(d, t, (50, 80, 90), (16, 30, 36))
    web(d, 540, 860, 440, 0.8)
    for i in range(5):
        an = i * 1.256; mx, my = 540 + 260 * math.cos(an), 860 + 260 * math.sin(an)
        eaten = t > t0 + 0.8 + i * 0.5
        if not eaten: mite(d, mx, my, 2.2)
        else: sparks(d, mx, my, t, t0 + 0.8 + i * 0.5, 8, 200, (220, 220, 230), 1, i, 0.4)
        bx = lerp(540 + 420 * math.cos(an), mx - 50, ease(pr(t, t0 + 0.2 + i * 0.5, t0 + 0.8 + i * 0.5)))
        by = lerp(860 + 420 * math.sin(an), my, ease(pr(t, t0 + 0.2 + i * 0.5, t0 + 0.8 + i * 0.5)))
        webbug(d, bx, by, 1.0, t + i)
    ptag(d, t, t0 + 0.3, 540, 420, "螨虫", (200, 200, 210), 40)
    ptag(d, t, t0 + 2.0, 540, 1170, "有些寄生蜘蛛", (230, 80, 70), 36, tc=WHITE)
def s_xray(t, d):
    t0 = T["xray"]
    forest_bg(d, t, (70, 60, 100), (24, 18, 40))
    web(d, 540, 860, 460, 0.7)
    m = ease(pr(t, t0 + 0.2, t0 + 1.4))
    spider(d, 540, 820, 0.9, t, molt=m)
    for i in range(6):
        an = i * 1.047 + 0.3
        e = ease(pr(t, t0 + 1.2 + i * 0.12, t0 + 2.2 + i * 0.12))
        r0 = lerp(440, 200, e)
        webbug(d, 540 + r0 * math.cos(an), 900 + r0 * math.sin(an) * 0.8, 1.0, t + i, sip=e * abs(math.sin(t * 9 + i)))
    ptag(d, t, t0 + 0.3, 540, 380, "蜕皮", GOLD, 50)
    for i in range(4):
        if t > t0 + 2.4: d.circ(540 + (i - 1.5) * 70, 1010 + 20 * math.sin(t * 6 + i), 10, fill=A((150, 220, 255), 0.8))
def s_swim(t, d):
    t0 = T["swim"]
    forest_bg(d, t, (60, 100, 80), (18, 36, 30))
    web(d, 540, 860, 460, 0.7)
    an = (t - t0) * 1.3
    sx, sy = 540 + 170 * math.cos(an), 860 + 170 * math.sin(an)
    spider(d, sx, sy - 40, 0.65, t, walk=1.0)
    for i in range(5):
        a2 = an - 0.55 - i * 0.38 + 0.15 * math.sin(t * 3 + i)
        webbug(d, 540 + 340 * math.cos(a2), 860 + 340 * math.sin(a2), 0.9, t + i)
    ptag(d, t, t0 + 0.3, 540, 330, "跟着绕圈", GOLD, 46)
    ptag(d, t, t0 + 1.4, 540, 1180, "原因还不清楚", WHITE, 32)
def s_gene(t, d):
    t0 = T["gene"]
    flatbg(d, (230, 236, 246), (190, 200, 220), t, False)
    spider(d, 540, 760, 1.6, t)
    webbug(d, 540 + 30 * math.sin(t * 2), 1160, 0.7, t)
    k = popk(t, t0 + 0.6, "bouncy")
    if k > 0:
        d.circ(540, 1160, 70 * min(1, k), outline=A((230, 80, 70), 1), w=6)
        tag(d, 760, 1120, "太小了", (230, 80, 70), min(1, k), 40, tc=WHITE)
    ptag(d, t, t0 + 1.5, 540, 360, "可能", NAVYT, 40, tc=WHITE)
def s_why(t, d):
    t0 = T["why"]
    forest_bg(d, t, (50, 90, 80), (16, 30, 30))
    d.line([(150, 860), (930, 860)], A((235, 240, 255), 0.8), 5)
    items = [(300, "卵"), (540, "小虫"), (780, "成虫")]
    for i, (x, lab) in enumerate(items):
        k = popk(t, t0 + 0.3 + i * 0.6, "bouncy")
        if k <= 0: continue
        kk = min(1, k)
        if i == 0:
            for j in range(3): d.ell(x - 50 + j * 50, 845, 22 * kk, 30 * kk, A((255, 240, 210), 1))
        else: webbug(d, x, 840, (0.9 if i == 1 else 1.5) * kk, t + i)
        d.text(x, 960, lab, 44, A(WHITE, kk), k=1)
    ptag(d, t, t0 + 2.2, 540, 600, "同一张网", GOLD, 46)
def s_order(t, d):
    t0 = T["order"]
    forest_bg(d, t, (70, 110, 90), (20, 40, 34))
    k = popk(t, t0 + 0.1, "smooth")
    web(d, 540, 820, 380 * (0.8 + 0.2 * min(1, k)), 0.9)
    for i in range(4):
        an = i * 1.57 + t * 0.5
        webbug(d, 540 + 200 * math.cos(an), 860 + 200 * math.sin(an), 0.9, t + i)
    ptag(d, t, t0 + 1.0, 540, 1170, "网 = 家", GOLD, 50)
def s_card(t, d):
    flatbg(d, (90, 130, 110), (30, 60, 50), t, False)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    webbug(d, cx_, cy_ - 150, 2.0, t, a_)
    d.text(cx_, cy_ + 20, "网栖蝽：住在蜘蛛网上的虫", 40, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("约1毫米，像一粒盐", "吃剩饭、吃螨虫", "蜘蛛蜕皮时喝体液")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 130 + i * 78, s_, 38, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    forest_bg(d, t)
    d.line([(100, 900), (980, 900)], A((235, 240, 255), 0.9), 8)
    x = 540 + 60 * math.sin((t - t0) * 0.8)
    webbug(d, x, 860, 4.2, t)
    k = popk(t, t0 + 0.8, "bouncy")
    if k > 0:
        d.circ(x - 20, 990, 90 * min(1, k), outline=A(GOLD, 1), w=8)
        d.text(x + 140, 1060, "?", int(110 * min(1, k)), A(GOLD, 1), k=1)
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 285, "Xiong et al. 2026", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 330, "ZooKeys 1296: 11–25", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "不吃它", "q": "1毫米", "who": "福建", "sperm": "新物种", "egg": "靠什么活", "reveal": "剩饭", "how": "螨虫", "xray": "喝体液",
      "swim": "绕圈", "gene": "太小", "why": "同一张网", "order": "一辈子", "end": "不粘脚"}
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
    s = "Vibe 知识大赏 · 动物打工人 No.01"; w = d.tlen(s, 28, 1) + 50
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/mq_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/mq_sheet.png")
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
