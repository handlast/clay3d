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
SOILY = 1090
def s_hook(t, d):
    room(d, t)
    k = ramp(t, 0.2, 1.6)
    hx, hy = topview(d, t, 90, 200 * k, [(180, 1, ""), (0, 1, ""), (90, 0.35, "")], cy=880)
    if t > 1.6: ptag(d, t, 1.6, 540, 400, "最暗的这盏", GOLD, 52)
    if t < 1.5: slamtxt(d, t, -0.2, "？！", 300, 160, GOLD)
    ptag(d, t, -0.2, 220, 880 + 150, "亮", BLUE_L, 46); ptag(d, t, -0.2, 860, 880 + 150, "亮", BLUE_L, 46)
def s_q(t, d):
    room(d, t)
    sprout(d, 540, SOILY, 1.3, t, lean=0.25 * math.sin(t * 4), mood="confused")
    for sd in (-1, 1): lamp(d, 540 + sd * 340, 560, 0.8, 1.0, t, mood="angry", dirx=-sd)
def s_reveal(t, d):
    rays(d, t, (120, 170, 255), (40, 70, 160))
    k = min(1.1, popk(t, BIG2, "bouncy"))
    for sd in (-1, 1):
        x = 540 + sd * (380 - 120 * ease(pr(t, BIG2, BIG2 + 0.4)))
        lamp(d, x, 760, 0.9, 1.0, t, mood="angry", dirx=-sd)
    if t > BIG2 + 0.4: slamtxt(d, t, BIG2 + 0.4, "抵消！", 1040, 220, WHITE)
    slamtxt(d, t, BIG2, "没傻", 380, 170, GOLD)
def s_who(t, d):
    room(d, t, (40, 60, 40), (12, 20, 12))
    sprout(d, 540, SOILY, 1.2, t, mood="happy")
    k = ease(pr(t, at("who", 2), at("who", 3.5)))
    if k > 0:
        x = 840; y0, y1 = SOILY - 20, SOILY - 20 - 380 * k
        d.line([(x, y0), (x, y1)], A(GOLD, 1), 10)
        for yy in (y0, y1): d.line([(x - 24, yy), (x + 24, yy)], A(GOLD, 1), 10)
        if k > 0.9: tag(d, x, (y0 + y1) / 2, "1~3 cm", GOLD, ap(t, at("who", 3.5)), 40)
    ptag(d, t, at("who", 0.3), 540, 360, "出生 1 周", LEAF_L, 60)
def s_lamp1(t, d):
    room(d, t)
    b = ap(t, at("lamp1", 0.5), 0.2)
    lamp(d, 200, 600, 0.8, b, t, mood="happy", dirx=1)
    sprout(d, 600, SOILY, 1.1, t, lean=-0.25 * ease(pr(t, at("lamp1", 1), at("lamp1", 4))), mood="happy", look=-1)
    ptag(d, t, at("lamp1", 0.3), 540, 360, "蓝光 LED", BLUE_L, 60)
def s_bright(t, d):
    room(d, t)
    u = pr(t, T["bright"], at("bright", 5))
    b = 0.3 + 0.7 * u
    lamp(d, 200, 600, 0.8, b, t, mood="proud", dirx=1)
    sprout(d, 600, SOILY, 1.1, t, lean=-(0.25 + 0.55 * u ** 0.5), mood="wow", look=-1)
    d.rect(760, 420, 880, 440, fill=A((60, 70, 100), 1), r=8); d.rect(760, 420, 760 + 120 * u, 440, fill=A(BLUE_L, 1), r=8)
    ptag(d, t, at("bright", 0.3), 820, 380, "亮度", BLUE_L, 36)
def s_double(t, d):
    room(d, t)
    k = ease(pr(t, at("double", 0.5), at("double", 1.5)))
    for i, (b, ang, lab) in enumerate(((0.45, 0.45, "×1"), (0.9, 0.7, "×2"))):
        x = 330 + i * 420
        lamp(d, x - 190, 640, 0.5, b, t, face=False)
        sprout(d, x + 30, SOILY, 0.75, t, lean=-ang * (k if i else 1), mood="happy" if i == 0 else "sus", look=-1)
        ptag(d, t, at("double", 0.3 + i), x - 190, 500, "亮度" + lab, BLUE_L, 40)
    if t > at("double", 3):
        ptag(d, t, at("double", 3), 540, 380, "弯曲 ≠ ×2", GOLD, 70)
def s_lamp2(t, d):
    room(d, t)
    lamp(d, 180, 600, 0.8, 1.0, t, mood="proud", dirx=1); lamp(d, 900, 600, 0.6, 0.35, t, mood="sad", dirx=-1)
    sprout(d, 540, SOILY, 1.1, t, mood="sus", lean=0.08 * math.sin(t * 3))
    ptag(d, t, at("lamp2", 0.3), 180, 400, "亮", BLUE_L, 50); ptag(d, t, at("lamp2", 0.8), 900, 440, "暗", (130, 140, 170), 46)
def s_lean(t, d):
    room(d, t)
    u = pr(t, at("lean", 2), at("lean", 7))
    br = 0.35 - 0.3 * u
    lamp(d, 180, 600, 0.8, 1.0, t, mood="proud", dirx=1); lamp(d, 900, 600, 0.6, br, t, mood="sad", dirx=-1)
    sprout(d, 540, SOILY, 1.1, t, lean=-(0.35 + 0.4 * u) * ease(pr(t, T["lean"], at("lean", 1.5))), mood="happy", look=-1)
    if t > at("lean", 2): ptag(d, t, at("lean", 2), 540, 380, "差距越大 → 越弯", GOLD, 54)
def s_lamp3(t, d):
    room(d, t, (30, 30, 70), (8, 8, 26))
    topview(d, t, None, 0, [(180, 1, ""), (0, 1, "")], cy=880)
    ptag(d, t, at("lamp3", 0.3), 540, 380, "俯视图", WHITE, 46)
    ptag(d, t, at("lamp3", 1.5), 190, 1080, "一样亮", BLUE_L, 40); ptag(d, t, at("lamp3", 1.5), 890, 1080, "一样亮", BLUE_L, 40)
def s_third(t, d):
    room(d, t, (30, 30, 70), (8, 8, 26))
    b3 = 0.35 * ap(t, at("third", 0.6), 0.3)
    topview(d, t, None, 0, [(180, 1, ""), (0, 1, ""), (90, b3, "")], cy=880)
    if b3 > 0.2: ptag(d, t, at("third", 1.5), 540, 380, "＜ 一半亮", GOLD, 54)
def s_n34(t, d):
    room(d, t, (30, 30, 70), (8, 8, 26))
    k = ramp(t, at("n34", 0.5), at("n34", 3))
    topview(d, t, 90, 210 * k, [(180, 1, ""), (0, 1, ""), (90, 0.35, "")], cy=880)
    if k > 0.6: slamtxt(d, t, at("n34", 3), "朝最暗！", 380, 120, GOLD)
    ptag(d, t, at("n34", 0.2), 860, 1300 - 70, "34 株", LEAF_L, 44)
rv = random.Random(3); VARY = [rv.gauss(90, 28) for _ in range(34)]
def s_vary(t, d):
    room(d, t, (30, 30, 70), (8, 8, 26))
    cx, cy = 540, 880
    topview(d, t, None, 0, [(180, 1, ""), (0, 1, ""), (90, 0.35, "")], cy=cy)
    for i, ang in enumerate(VARY):
        kk = ap(t, at("vary", 0.2 + i * 0.05), 0.2)
        if kk <= 0: continue
        r_ = math.radians(ang); L = 120 + 60 * ((i * 37) % 10) / 10
        d.line([(cx, cy), (cx + math.cos(r_) * L, cy - math.sin(r_) * L)], A(LEAF_L, 0.35 * kk), 6)
    ka = ap(t, at("vary", 4), 0.3)
    if ka > 0:
        arrow(d, cx, cy, cx, cy - 260, GOLD, ka, 16); ptag(d, t, at("vary", 4), 760, cy - 230, "平均", GOLD, 44)
def s_how(t, d):
    grad(d, (20, 60, 40), (6, 20, 12))
    # stem cross-section close-up: big circle with sensor dots around circumference
    cx, cy, R = 540, 820, 290
    d.circ(cx, cy, R + 20, fill=A(STEM_D, 1)); d.circ(cx, cy, R, fill=A(STEM, 1)); d.circ(cx, cy, R * 0.55, fill=A((150, 215, 120), 1))
    for i in range(24):
        kk = popk(t, at("how", 0.4 + i * 0.06))
        if kk <= 0: continue
        th = i / 24 * 2 * math.pi; x, y = cx + math.cos(th) * (R - 10), cy + math.sin(th) * (R - 10)
        lit = 0.5 + 0.5 * math.cos(th - math.pi)
        d.circ(x, y, 18 * min(1, kk), fill=A(mix((60, 90, 70), BLUE_L, lit), 1))
    ptag(d, t, at("how", 0.3), 540, 380, "茎的横切面", LEAF_L, 50)
    if t > at("how", 3): ptag(d, t, at("how", 3), 540, 1165, "感光蛋白", BLUE_L, 44)
def s_compress(t, d):
    grad(d, (40, 30, 70), (12, 8, 26))
    x0, y0 = 240, 1080; W, Hh = 620, 560
    d.line([(x0, y0), (x0 + W, y0)], A(WHITE, 0.7), 6); d.line([(x0, y0), (x0, y0 - Hh)], A(WHITE, 0.7), 6)
    d.text(x0 + W - 40, y0 + 46, "光强", 34, A(WHITE, 0.8), k=1); d.text(x0 - 10, y0 - Hh - 40, "反应", 34, A(WHITE, 0.8), k=1)
    k = ramp(t, at("compress", 0.4), at("compress", 3))
    pts = [(x0 + W * u, y0 - Hh * 0.9 * u ** 0.45) for u in [i / 40 * k for i in range(41)]]
    if k > 0.02: d.line(pts, A(GOLD, 1), 12)
    lin = [(x0, y0), (x0 + W * k, y0 - Hh * 0.9 * k)]
    d.line(lin, A((255, 255, 255), 0.18), 6)
    if t > at("compress", 3.5):
        for u, lab in ((0.4, "1×"), (0.8, "2×")):
            x = x0 + W * u; y = y0 - Hh * 0.9 * u ** 0.45
            d.circ(x, y, 16, fill=A(BLUE_L, 1)); tag(d, x, y0 + 46, lab, BLUE_L, ap(t, at("compress", 3.5)), 32)
        ptag(d, t, at("compress", 4), 540, 380, "被“压缩”", GOLD, 64)
def s_sum(t, d):
    grad(d, (30, 30, 70), (8, 8, 26))
    cx, cy = 540, 880
    k = ramp(t, at("sum", 0.4), at("sum", 2.5))
    lamp(d, 150, cy - 30, 0.55, 1, t, face=False); lamp(d, 930, cy - 30, 0.55, 1, t, face=False)
    arrow(d, cx, cy, cx - 280 * k + 1, cy, BLUE_L, 1, 16); arrow(d, cx, cy, cx + 280 * k + 1, cy, BLUE_L, 1, 16)
    m = ramp(t, at("sum", 4), at("sum", 6))
    if m > 0:
        d.rect(0, 0, 1080, 1920, fill=A((8, 8, 26), 0.0))
        for sd in (-1, 1): arrow(d, cx + sd * 280 * (1 - m), cy, cx + sd * 280 * (1 - m) - sd * 120 * (1 - m) + sd * 1, cy, BLUE_L, 1 - m, 16)
    if m > 0.9: slamtxt(d, t, at("sum", 6), "= 0", cy + 220, 140, GOLD)
    d.circ(cx, cy, 24, fill=A(LEAF_L, 1))
    ptag(d, t, at("sum", 0.3), 540, 380, "信号相加", WHITE, 54)
def s_left(t, d):
    room(d, t, (30, 30, 70), (8, 8, 26))
    k = ramp(t, at("left", 0.4), at("left", 3))
    hx, hy = topview(d, t, 90, 210 * k, [(180, 1, ""), (0, 1, ""), (90, 0.35, "")], cy=880)
    arrow(d, 540, 880, 540, 880 - 300 * k + 1, GOLD, k, 14)
    ptag(d, t, at("left", 2.5), 540, 380, "弱光说了算", GOLD, 60)
def s_illusion(t, d):
    room(d, t, (50, 30, 80), (14, 8, 28))
    sw = math.radians(6) * math.sin((t - T["illusion"]) * 2)
    sprout(d, 540, SOILY, 1.2, t, lean=sw * 1.5, mood="confused")
    d.line([(540, SOILY - 20), (540, SOILY - 560)], A(WHITE, 0.25), 4)
    ptag(d, t, at("illusion", 0.4), 540, 380, "视错觉？", (255, 150, 220), 64)
    if t > at("illusion", 3): ptag(d, t, at("illusion", 3), 820, 700, "≤ 6°", GOLD, 56)
def s_notyet(t, d):
    room(d, t, (50, 30, 80), (14, 8, 28))
    sprout(d, 540, SOILY, 1.2, t, lean=0.12 * math.sin(t * 2.2), mood="chill", sway=2)
    stamp(d, t, at("notyet", 0.6), "待观测", 540, 420, 110, (255, 150, 60))
def s_card(t, d):
    grad(d, (30, 50, 90), (8, 14, 34))
    for i in range(12): d.circ(540, 860, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 690 * (0.8 + 0.2 * k), 980 * (0.8 + 0.2 * k); cx_, cy_ = 540, 840; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 80, "一句话学会", GOLD, a_, 32)
    sprout(d, cx_, cy_ - 60, 0.45, t, mood="proud", a=a_, pot=True)
    d.text(cx_, cy_ + 60, "植物不是“哪亮朝哪长”", 40, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("茎表面各处分别感光，信号被压缩", "再把各方向信号相加定方向", "两盏等亮对灯会互相抵消", "所以弱光也能决定方向")):
        kk = popk(t, at("card", 1.2 + i * 1.6))
        if kk > 0: d.text(cx_, cy_ + 150 + i * 62, s_, 31, A((70, 70, 90), ap(t, at("card", 1.2 + i * 1.6))), k=1)
def s_end(t, d):
    room(d, t)
    k = ramp(t, at("end", 1), at("end", 3))
    for sd in (-1, 1): lamp(d, 540 + sd * 360, 700, 0.7, 1, t, mood="angry", dirx=-sd)
    lamp(d, 540, 640, 0.4, 0.35, t, mood="proud")
    sprout(d, 540, SOILY, 1.15, t, mood="proud" if k > 0.8 else "sus", lean=0)
    if k > 0.8: ptag(d, t, at("end", 3), 540, 340, "弱光说了算", GOLD, 70)
    ra = ap(t, at("end", 5), 0.3)
    if ra > 0:
        d.rect(170, 1410 - 1000, 910, 1520 - 1000, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 443, "Kempinski 等 2026 · PNAS", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 487, "实验室蓝光实验 · 1周龄向日葵幼苗", 25, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "最暗", "q": "傻了", "reveal": "互相抵消", "who": "1到3厘米", "lamp1": "一盏蓝光灯", "bright": "弯得越厉害", "double": "不到两倍",
      "lamp2": "一亮一暗", "lean": "弯得越多", "lamp3": "一样亮", "third": "不到它们的一半", "n34": "最暗那盏", "vary": "平均下来", "how": "感光蛋白",
      "compress": "压缩", "sum": "正好抵消", "left": "弱光", "illusion": "视错觉", "notyet": "还没被观测到", "end": "弱光说了算"}
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/sf_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/sf_sheet.png")
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
