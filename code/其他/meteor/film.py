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
def sky(d, t, top=(20, 24, 60), bot=(70, 60, 110)):
    flatbg(d, top, bot, t, False); stars(d, t)
def fall(t, t0, dur, x0, y0, x1, y1):
    u = ease(pr(t, t0, t0 + dur)); return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
def s_hook(t, d):
    sky(d, t, (30, 30, 80), (230, 120, 80))
    if t < 0.3: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - t / 0.3)))
    x, y = fall(t, -0.1, 2.0, 980, 220, 420, 860)
    rock(d, x, y, 1.4, t, face="happy", fire=1, green=True)
    mountains(d)
    person(d, 780, 1150, 1.1, t, face="shock" if t > 0.3 else "look", cover=ap(t, 2.2))
    k = popk(t, 2.4, "bouncy")
    if k > 0: tag(d, 780, 920, "几分钟后…轰！", GOLD, min(1, k), 46)
def s_q(t, d):
    t0 = T["q"]
    sky(d, t, (20, 24, 60), (60, 50, 100))
    # map dots: 北京/河北/山西/河南/天津
    for i, (nm, x, y) in enumerate((("北京", 640, 560), ("天津", 760, 640), ("河北", 600, 760), ("山西", 380, 760), ("河南", 520, 960))):
        k = popk(t, t0 + 0.3 + i * 0.3)
        if k > 0: d.circ(x, y, 22 * min(1.2, k), fill=A(GOLD, 1)); tag(d, x, y - 60, nm, WHITE, min(1, k), 36)
    x, y = fall(t, t0 + 0.2, 2.5, 1000, 280, 860, 420)
    rock(d, x, y, 0.6, t, fire=1, green=True)
    ptag(d, t, t0 + 2.0, 540, 1120, "约18:31，傍晚下班高峰", WHITE, 38)
def s_who(t, d):
    t0 = T["who"]
    sky(d, t, (10, 10, 30), (30, 30, 70))
    k = popk(t, t0, "bouncy")
    if k > 0: rock(d, 540, 760, 2.4 * min(1, k), t, face="happy")
    k2 = popk(t, t0 + 1.2)
    if k2 > 0:
        d.line([(370, 1000), (710, 1000)], A(GOLD, k2), 8)
        for xx in (370, 710): d.line([(xx, 980), (xx, 1020)], A(GOLD, k2), 8)
        tag(d, 540, 1060, "直径约1米（推算）", GOLD, min(1, k2), 40)
    person(d, 860, 1060, 0.7, t)
def s_sperm(t, d):
    t0 = T["sperm"]
    flatbg(d, (40, 60, 140), (110, 160, 230), t, False)
    for i in range(4): d.line([(0, 380 + i * 260), (1080, 380 + i * 260)], A(WHITE, 0.12), 3)
    tag(d, 900, 360, "大气层", WHITE, 1, 34)
    x, y = fall(t, t0 + 0.3, 2.0, 1100, 150, 420, 900)
    rock(d, x, y, 1.0, t, face="happy", fire=ease(pr(t, t0 + 0.8, t0 + 2.0)))
    ptag(d, t, t0 + 1.0, 540, 1120, "每秒十几公里", GOLD, 48)
def s_egg(t, d):
    t0 = T["egg"]
    flatbg(d, (40, 60, 140), (110, 160, 230), t, False)
    dim = 1 - 0.6 * pr(t, SIL0, SIL0 + 0.1)
    rock(d, 420, 800, 1.2, t, face="happy", a=dim)
    rv = random.Random(2)
    for i in range(30):  # air molecules piling up in front
        u = pr(t, t0 + 0.4, SIL0)
        x = 560 + rv.uniform(0, 260) * (1 - 0.7 * u); y = 800 + rv.uniform(-200, 200) * (1 - 0.3 * u)
        d.circ(x, y, 14, fill=A((220, 240, 255), dim))
    if t < SIL0: ptag(d, t, t0 + 1.5, 700, 540, "挤挤挤…", WHITE, 40)
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (255, 190, 80), (230, 80, 40))
    if t > t0: sparks(d, 540, 760, t, t0, 30, 900, FIRE2, 1, 3, 0.9)
    k = ease(pr(t, t0, t0 + 0.3))
    for i in range(3): d.arc(620, 760, (220 + i * 60) * k, (300 + i * 80) * k, -70, 70, A(WHITE, 0.8 - i * 0.2), 14)
    rock(d, 480, 760, 1.4, t, face="scared", fire=1, ang=math.pi)
    ptag(d, t, t0 + 0.5, 540, 460, "激波", WHITE, 70)
    ptag(d, t, t0 + 1.2, 540, 1080, "几千摄氏度", GOLD, 60)
def s_how(t, d):
    t0 = T["how"]
    flatbg(d, (10, 14, 40), (90, 150, 220), t, False)
    gy = 1200
    d.rect(0, gy, 1080, 1920, fill=A((60, 90, 60), 1))
    def yk(km): return gy - km * 8
    for km in (10, 30, 100):
        a_ = ap(t, t0 + {10: 1.4, 30: 0.4, 100: 0.4}[km])
        d.line([(160, yk(km)), (920, yk(km))], A(WHITE, 0.4 * a_), 3); d.text(240, yk(km) - 26, f"{km}公里", 34, A(WHITE, a_), k=1)
    d.rect(560, yk(100), 880, yk(30), fill=A(FIRE, 0.25 * ap(t, t0 + 0.4)), r=20)
    rock(d, 720, yk(60), 0.6, t, fire=ap(t, t0 + 0.4), green=True)
    tag(d, 720, yk(100) - 50, "发光区", FIRE, ap(t, t0 + 0.6), 34)
    if t > t0 + 1.4: plane(d, 640, yk(10), 0.8)
    person(d, 260, gy - 50, 0.45, t)
def s_xray(t, d):
    t0 = T["xray"]
    sky(d, t, (20, 24, 60), (70, 60, 110)); mountains(d)
    rock(d, 300, 420, 0.7, t, fire=1, green=True)
    person(d, 780, 1150, 0.9, t, face="shock")
    # light ray: instant
    if t > t0 + 0.3: d.line([(330, 450), (760, 1100)], A(FIRE2, 0.9), 8); tag(d, 420, 700, "光：一瞬", FIRE2, ap(t, t0 + 0.3), 36)
    # sound wavefront: slow
    u = pr(t, t0 + 1.2, t0 + 4.4)
    for i in range(3):
        r = max(0, 700 * u - i * 70)
        if r > 0: d.arc(300, 420, r, r, 20, 80, A((160, 200, 255), 0.7 - 0.2 * i), 8)
    tag(d, 760, 560, "声音：约20公里/分钟", (160, 200, 255), ap(t, t0 + 1.4), 34)
def s_swim(t, d):
    t0 = T["swim"]
    flatbg(d, (20, 24, 60), (40, 40, 80), t, False)
    d.line([(160, 820), (920, 820)], A(WHITE, 0.6), 6)
    for i, (sec, lab, col) in enumerate(((0, "看到火球", FIRE2), (90, "1.5分钟", (160, 200, 255)), (240, "4分钟", (160, 200, 255)))):
        x = 160 + 760 * sec / 240; a_ = ap(t, t0 + 0.3 + i * 0.7)
        d.circ(x, 820, 20, fill=A(col, a_)); tag(d, x, 740, lab, col, a_, 32)
    d.rect(160 + 760 * 90 / 240, 800, 920, 840, fill=A((160, 200, 255), 0.5 * ap(t, t0 + 1.0)), r=10)
    k = popk(t, t0 + 2.0, "bouncy")
    if k > 0: tag(d, 640, 920, "轰！", GOLD, min(1, k), 70)
    person(d, 540, 1120, 0.8, t, face="shock" if t > t0 + 2.0 else "look", cover=ap(t, t0 + 2.0))
def s_gene(t, d):
    t0 = T["gene"]
    sky(d, t, (10, 30, 40), (30, 70, 80))
    x, y = fall(t, t0, 3.5, 900, 300, 400, 900)
    rock(d, x, y, 1.0, t, fire=1, green=True)
    for i, (el, col) in enumerate((("镁 Mg", GREENF), ("镍 Ni", (150, 230, 200)))):
        k = popk(t, t0 + 0.8 + i * 0.6)
        if k > 0: tag(d, 300 + i * 480, 1120, el, col, min(1, k), 52)
    tag(d, 540, 1220, "可能", WHITE, ap(t, t0 + 1.8), 32)
def s_why(t, d):
    t0 = T["why"]
    flatbg(d, (80, 120, 180), (160, 190, 220), t, False)
    d.rect(0, 1250, 1080, 1920, fill=A((110, 90, 70), 1))
    x, y = fall(t, t0, 0.8, 760, 300, 540, 650)
    k = pr(t, t0 + 0.8, t0 + 1.0)
    if k < 1: rock(d, x, y, 1.0, t, fire=1)
    else:
        rv = random.Random(6)
        for i in range(5):
            u = ease(pr(t, t0 + 0.8, t0 + 2.0)); xx = 540 + rv.uniform(-300, 300) * u; yy = 650 + (560 + rv.uniform(-40, 40)) * u
            rock(d, xx, yy, 0.35, t, face="happy")
    ptag(d, t, t0 + 2.0, 540, 1380, "陨石", GOLD, 70)
def s_order(t, d):
    t0 = T["order"]
    flatbg(d, (240, 220, 180), (210, 180, 140), t, False)
    rock(d, 540, 640, 0.9, t, face="happy")
    for i, s_ in enumerate(("① 记坐标", "② 拍照片", "③ 找天文机构")):
        k = popk(t, t0 + 0.6 + i * 0.6)
        if k > 0: tag(d, 540, 860 + i * 100, s_, NAVYT if False else (60, 120, 200), min(1, k), 44)
def s_card(t, d):
    flatbg(d, (40, 46, 80), (14, 16, 30), t, False)
    for i in range(12): d.circ(540, 820, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    rock(d, cx_, cy_ - 160, 0.9, t, fire=1, green=True, a=a_, trail=0.45)
    d.text(cx_, cy_ + 20, "火流星：比金星还亮的流星", 44, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("激波把空气压到几千度", "光先到，音爆晚1.5到4分钟", "没烧完的碎块就是陨石")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 130 + i * 78, s_, 40, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    sky(d, t, (30, 30, 80), (230, 120, 80))
    x, y = fall(t, t0, 2.0, 980, 220, 420, 760)
    rock(d, x, y, 1.4, t, fire=1, green=True); mountains(d)
    person(d, 780, 1150, 1.1, t, cover=ap(t, t0 + 2.4))
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 290, "北京天文馆李昕（央视新闻、北京日报）", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 335, "American Meteor Society · Fireball FAQ", 24, A(WHITE, 0.85 * ra), k=1)
        d.text(540, 372, "2026年11月6日华北火流星", 22, A(WHITE, 0.75 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "“轰”", "q": "同一颗火球", "who": "约1米", "sperm": "十几公里", "egg": "来不及", "reveal": "几千度", "how": "30到100公里",
      "xray": "约20公里", "swim": "1.5到4分钟", "gene": "镁、镍", "why": "陨石", "order": "记坐标", "end": "再听轰"}
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
    s = "Vibe 知识大赏 · 怪奇天象"; w = d.tlen(s, 28, 1) + 50
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/mt_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/mt_sheet.png")
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
