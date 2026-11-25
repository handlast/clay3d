import sys, subprocess, math, random
from PIL import ImageOps
from chars import *
from cues import *

GY = 700; CX, CY, CRX, CRY = 540, 1040, 250, 125
EGGS = [(420, 1062), (505, 1040), (590, 1058), (668, 1044)]
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
def qmarks(d, t, a=1.0):
    for i, (x, y) in enumerate(((300, 980), (560, 1120), (800, 960))):
        d.text(x, y + 10 * math.sin(t * 4 + i), "?", 90, A((255, 220, 140), 0.5 * a), k=1)
def eggs(d, t, crack=0.0, outs=(0, 0, 0, 0), wob=0.0, mouths=(0, 0, 0, 0), a=1.0):
    for i, (x, y) in enumerate(EGGS):
        egg(d, x, y, 0.95, t + i * 0.37, crack, outs[i], wob, "happy" if mouths[i] < 0.1 else "o", a, mouths[i])
def cutaway(d, t, rev=1.0, gy=GY, mound=True):
    surface(d, t, gy, mound)
    dirt(d, t, gy)
    if rev > 0: chamber(d, CX, CY + gy - GY, CRX * rev, CRY * rev)
MX, MS = 330, 1.0   # mom position on the mound
def mom(d, t, **kw):
    kw.setdefault("mood", "normal")
    return croc(d, kw.pop("x", MX), kw.pop("y", GY - 4), kw.pop("s", MS), t, **kw)

# ---------------- scenes ----------------
def s_hook(t, d):
    cutaway(d, t, 0)
    tl = popk(t, 0.02, "bouncy")
    f = mom(d, t, mood="listen", tilt=min(1.1, tl), ear=0.8 + 0.2 * math.sin(t * 8))
    qmarks(d, t)
    waves_up(d, t, f["ear"][0], 1150, f["ear"][1] + 40, 0.9)
    slamtxt(d, t, -0.25, "偷听？", 360, 190, YEL)
def s_stay(t, d):
    cutaway(d, t, 0)
    f = mom(d, t, mood="listen", tilt=1.0, ear=0.4, breath=False)
    for j in range(3):
        k = (t * 1.5 + j / 3) % 1
        d.circ(f["ear"][0], f["ear"][1], 30 + k * 120, outline=A(WHITE, 0.35 * (1 - k)), w=5)
    title(d, t, at("stay", 0.5), "一动不动", 360, 130, WHITE)
def s_q(t, d):
    dirt(d, t, 200)
    k = pr(t, T["q"], T["q"] + 0.4)
    d.poly([(540, 120), (540 - 380 * k, 1300), (540 + 380 * k, 1300)], A((255, 240, 190), 0.16))
    d.ell(540, 1080, 300 * k, 90 * k, A((255, 240, 190), 0.2))
    kk = popk(t, T["q"] + 0.05, "bouncy")
    if kk > 0: d.text(540, 760, "?", int(320 * (0.6 + 0.4 * kk)), A(YEL, ap(t, T["q"])), k=1)
def s_reveal(t, d):
    rv = min(1.08, popk(t, BIG2, "bouncy"))
    cutaway(d, t, rv)
    if rv > 0.3: eggs(d, t, crack=pr(t, at("reveal", 4), at("reveal", 6)), wob=pr(t, at("reveal", 3), at("reveal", 4)), a=cl((rv - 0.3) * 2))
    mood = "shock" if t < at("reveal", 3) else "soft"
    mom(d, t, mood=mood, tilt=1 - pr(t, BIG2, BIG2 + 0.4), blush=pr(t, at("reveal", 3), at("reveal", 4)))
    slamtxt(d, t, BIG2, "蛋！", 330, 200, YEL)
    for i, (x, y) in enumerate(EGGS):
        kk = popk(t, at("reveal", 1 + i * 0.4))
        if kk > 0 and t < at("reveal", 3): glow(d, x, y, 90, (255, 240, 170), 0.5 * kk, 5)
def s_call(t, d):
    cutaway(d, t, 1)
    outs = [min(1, popk(t, at("call", 0.3 + i * 0.7), "bouncy")) for i in range(4)]
    mouths = [0.5 + 0.5 * math.sin(t * 10 + i) if outs[i] > 0.5 else 0 for i in range(4)]
    eggs(d, t, crack=1, outs=outs, wob=0.3, mouths=mouths)
    f = mom(d, t, mood="listen", tilt=pr(t, at("call", 2), at("call", 3)), ear=pr(t, at("call", 3), at("call", 4)))
    for i, (x, y), s_ in zip(range(4), EGGS, ("妈～", "挖我！", "嘿！", "出来啦")):
        if i in (0, 1, 3): bubble(d, x + (0 if i != 3 else 30), y - 150 - (i % 2) * 70, s_, popk(t, at("call", 0.6 + i * 0.7)), size=36)
    waves_up(d, t, 540, CY - 120, f["ear"][1] + 50, pr(t, at("call", 1.5), at("call", 2.5)))
def s_where(t, d):
    grad(d, (236, 214, 160), (206, 180, 120))
    k = pr(t, T["where"], at("where", 2))
    trunk = [(120, 560), (240, 620), (330, 670), (420, 700)]
    d.line(trunk, A(WAT2, 1), 26)
    rr_ = random.Random(3)
    for i in range(9):
        a0 = -0.15 + i * 0.16; L = 600 * k
        x1, y1 = 420 + math.sin(a0 + 0.55) * L, 700 + math.cos(a0 + 0.55) * L * 0.85
        mx_, my_ = lerp(420, x1, 0.5) + rr_.uniform(-40, 40), lerp(700, y1, 0.5)
        d.line([(420, 700), (mx_, my_), (x1, y1)], A(WAT1, 0.9), 14 - i * 0.6)
        if k > 0.6: d.ell(x1, y1, 50 * (k - 0.6) * 2.5, 26 * (k - 0.6) * 2.5, A(GRASS, 0.8))
    for i in range(14): d.circ(420 + 380 * math.sin(i * 0.7 + 0.4) * k, 780 + (i * 47) % 380 * k, 18, fill=A(GRASS, 0.55 * k))
    kp = popk(t, at("where", 1.5), "bouncy")
    if kp > 0:
        px, py = 640, 930 - (1 - min(kp, 1)) * 200
        d.circ(px, py - 70, 44, fill=A((240, 70, 70), 1)); d.poly([(px - 38, py - 50), (px, py), (px + 38, py - 50)], A((240, 70, 70), 1)); d.circ(px, py - 70, 16, fill=A(WHITE, 1))
    ptag(d, t, at("where", 1.0), 540, 330, "博茨瓦纳", GOLD, 64)
    title(d, t, at("where", 2.0), "奥卡万戈三角洲", 450, 90, NAVYT)
    kc = popk(t, at("where", 4))
    if kc > 0:
        trailcam(d, 330, 1060, 0.9 * min(1, kc), t)
        d.ell(560, 1190, 140 * kc, 34 * kc, A(SAND_D, 1)); ptag(d, t, at("where", 4.4), 330, 1220, "藏好的相机", WHITE, 32)
def s_rule(t, d):
    rays(d, t, (200, 50, 40), (120, 20, 20))
    dirt(d, t, 900)
    d.ell(540, 906, 330, 40, A(SAND, 1))
    croc(d, 430, 896, 0.8, t, "fierce", jaw=0.2)
    stamp(d, t, T["rule"] + 0.05, "规矩不能坏", 540, 330, 130, GOLD)
    k = popk(t, at("rule", 1.5))
    if k > 0:
        x, y = 830, 520; sc = 0.6 + 0.4 * k
        d.rect(x - 100 * sc, y - 90 * sc, x + 100 * sc, y + 90 * sc, fill=A(WHITE, 1), r=16)
        d.rect(x - 100 * sc, y - 90 * sc, x + 100 * sc, y - 44 * sc, fill=A((220, 60, 50), 1), r=16)
        dd = int(1 + 89 * E.ease_in_out_sine(pr(t, at("rule", 2), at("rule", 5))))
        d.text(x, y + 10 * sc, f"第{dd}天", int(46 * sc), A(NAVYT, 1), k=1)
        if t > at("rule", 5.2): ptag(d, t, at("rule", 5.2), x, y + 130, "≈三个月", GOLD, 38)
def s_guard(t, d):
    gy = 1000
    surface(d, t, gy, True, False, 470); dirt(d, t, gy)
    f = croc(d, 400, gy - 4, 0.75, t, "fierce", jaw=0.3 + 0.2 * math.sin(t * 6))
    for i, (kind, nm, x) in enumerate((("hippo", "河马", 200), ("leopard", "豹", 420), ("hyena", "鬣狗", 650), ("monitor", "巨蜥", 870))):
        t0 = at("guard", 0.3 + i * 0.9); k = popk(t, t0, "bouncy")
        if k <= 0: continue
        back_ = E.ease_out_cubic(pr(t, t0 + 0.7, t0 + 1.0))
        x = x + (x - 540) * 0.9 * back_; y = 640 + 40 * k - (i % 2) * 50
        enemy(d, kind, x, y, 66 * min(1.1, k), 1.0 - 0.5 * back_)
        tag(d, x, y + 110, nm, WHITE, ap(t, t0), 34)
        cross(d, x, y, 60, pr(t, t0 + 0.45, t0 + 0.65), (240, 60, 60))
        if t0 + 0.45 <= t < t0 + 0.9: rings(d, x, y, t, [t0 + 0.45], (255, 230, 120), 0.8, 160)
    if t > at("guard", 4.4): title(d, t, at("guard", 4.4), "全都防着", 300, 100, WHITE)
def s_tilt1(t, d):
    cutaway(d, t, 0)
    hits = [at("tilt1", 1), at("tilt1", 3)]
    tl = sum(math.exp(-((t - h - 0.12) / 0.12) ** 2) for h in hits)
    picked = t > hits[1] + 0.12
    f = mom(d, t, mood="normal", tilt=1.3 * tl, jaw=0.4 * tl, look=0.6)
    if not picked: d.line([(720, GY - 4), (830, GY - 16)], A((130, 90, 50), 1), 10)
    else: d.line([(f["snout"][0] - 120, f["snout"][1] - 6), (f["snout"][0] - 10, f["snout"][1] - 18)], A((130, 90, 50), 1), 10)
    for h in hits:
        if 0 <= t - h < 0.4:
            for j in range(4): d.line([(f["head"][0] - 60, f["head"][1] - 90 + j * 26), (f["head"][0] - 160 - j * 20, f["head"][1] - 90 + j * 26)], A(WHITE, 0.6 * (1 - (t - h) / 0.4)), 6)
    ptag(d, t, hits[0] + 0.15, 540, 330, "嗖！", WHITE, 70)
    if t > hits[1]: ptag(d, t, hits[1] + 0.2, 540, 450, "又快又准", GOLD, 56)
def s_tilt2(t, d):
    cutaway(d, t, 0)
    tl = E.ease_in_out_sine(pr(t, T["tilt2"] + 0.1, at("tilt2", 2)))
    f = mom(d, t, mood="listen", tilt=tl, ear=0.6 * pr(t, at("tilt2", 2), at("tilt2", 3)), breath=False)
    ka = popk(t, at("tilt2", 3))
    if ka > 0:
        ex, ey = f["ear"]; arrow(d, ex - 190, ey - 210, ex - 14, ey - 16, YEL, ap(t, at("tilt2", 3)), 12)
        tag(d, ex - 200, ey - 250, "耳孔", YEL, ap(t, at("tilt2", 3)), 44)
    title(d, t, at("tilt2", 1.5), "不动……", 330, 110, WHITE)
def s_dig(t, d):
    cutaway(d, t, 1)
    k = E.ease_in_out_sine(pr(t, at("dig", 0.5), at("dig", 4)))
    path = [(600 + 40 * math.sin(u * 3), GY + u * (CY - CRY - GY + 20)) for u in [i / 20 * k for i in range(21)]]
    if k > 0.01: tunnel(d, path, 70)
    done = k > 0.98
    outs = (1, 1, 1, 1) if done else (0, 0, 0, 0)
    eggs(d, t, crack=1, outs=outs, wob=0 if done else 0.6, mouths=[0.6 + 0.4 * math.sin(t * 9 + i) if done else 0 for i in range(4)])
    f = mom(d, t, mood="fierce" if not done else "soft", tilt=0.6 + 0.3 * math.sin(t * 14) * (not done), blush=float(done))
    if 0.02 < k < 0.98:
        hx, hy = path[-1]
        for j in range(8):
            u = (t * 3 + j / 8) % 1; ang = -1.6 + (j - 4) * 0.25
            d.circ(hx + math.cos(ang) * u * 160, hy - 40 + math.sin(ang) * u * 200 + u * u * 160, 12 * (1 - u) + 4, fill=A(DIRT_L, 1 - u))
    stamp(d, t, at("dig", 0.5), "挖！", 540, 340, 150, YEL)
    if done: ptag(d, t, at("dig", 4.1), 540, 470, "接娃！", WHITE, 54)
def s_think(t, d):
    cutaway(d, t, 1)
    mouths = [0.5 + 0.5 * math.sin(t * 9 + i) for i in range(4)]
    eggs(d, t, crack=1, outs=(1, 1, 1, 1), mouths=mouths)
    f = mom(d, t, mood="listen", tilt=1.0, ear=0.7 + 0.3 * math.sin(t * 6))
    waves_up(d, t, 540, CY - 110, f["ear"][1] + 50, 1.0)
    ptag(d, t, at("think", 0.3), 540, 300, "研究者的解读", GOLD, 44)
    title(d, t, at("think", 1.5), "贴地听", 430, 120, WHITE)
def closeup(d, t, iso=0.0, jaw=0.0, mood="normal"):
    return croc(d, -60, 1130, 2.0, t, mood, iso=iso, jaw=jaw, bob=False, tail=False)
def s_bumps(t, d):
    grad(d, SKY1, SKY2)
    iso = pr(t, at("bumps", 0.5), at("bumps", 3))
    f = closeup(d, t, iso)
    ptag(d, t, at("bumps", 1.5), 560, 330, "数千个", GOLD, 70)
    if t > at("bumps", 3): ptag(d, t, at("bumps", 3), 760, 1300 - 120, "感觉器官", WHITE, 46)
def s_drop(t, d):
    grad(d, SKY1, SKY2)
    th = at("drop", 1.6)
    f = closeup(d, t, iso=pr(t, th + 0.3, th + 0.9) * (0.6 + 0.4 * math.sin(t * 8)))
    wy = 1050
    d.rect(-50, wy, 1130, 1960, fill=A(WAT1, 0.62))
    d.line([(x, wy + 4 * math.sin(x / 40 + t * 3)) for x in range(-20, 1101, 20)], A(FOAM, 0.8), 6)
    dx = 600
    if t < th:
        u = pr(t, at("drop", 0.4), th); y = lerp(250, wy, u * u)
        if u > 0: d.circ(dx, y, 22, fill=A(WAT1, 1)); d.poly([(dx - 20, y - 6), (dx, y - 50), (dx + 20, y - 6)], A(WAT1, 1))
    for j in range(3):
        u = (t - th - j * 0.25) / 1.4
        if 0 <= u < 1: d.ell(dx, wy, 40 + u * 520, 10 + u * 70, outline=A(WHITE, 0.8 * (1 - u)), w=6)
    ptag(d, t, at("drop", 0.3), 540, 330, "2002 · Nature", WHITE, 48)
    if t > th + 0.4: ptag(d, t, th + 0.4, 540, 450, "一滴水也知道", GOLD, 52)
def s_vib(t, d):
    grad(d, (60, 120, 90), (24, 60, 50))
    cx_, cy_, R_ = 540, 800, 330
    k = popk(t, T["vib"] + 0.05, "smooth")
    R2 = R_ * min(1, k)
    d.circ(cx_, cy_, R2 + 14, fill=A(WHITE, 0.9)); d.circ(cx_, cy_, R2, fill=A(CROC_L, 1))
    if k > 0.3:
        d.rect(cx_ - R2 * 0.94, cy_ - 40, cx_ + R2 * 0.94, cy_ + R2 * 0.92, fill=A((240, 196, 170), 1), r=40)
        d.d.chord((P(cx_ - R2 * 0.7), P(cy_ - R2 * 0.55), P(cx_ + R2 * 0.7), P(cy_ + R2 * 0.4)), 180, 360, fill=A(CROC, 1))
        for j in range(5):
            xx = cx_ - 160 + j * 80
            d.line([(xx, cy_ + 10), (xx + 10 * math.sin(t * 3 + j), cy_ + 140), (cx_, cy_ + 280)], A((250, 220, 110), 0.9), 7)
    kp = popk(t, at("vib", 1.5))
    if kp > 0:
        y = cy_ - R_ * 0.75 + 30 * abs(math.sin(t * 5)); arrow(d, cx_ - 140, y - 130, cx_ - 140, y - 10, WHITE, 1, 16)
        tag(d, cx_ - 150, cy_ - R_ - 70, "压力", WHITE, ap(t, at("vib", 1.5)), 50)
    kv = popk(t, at("vib", 3))
    if kv > 0:
        pts = [(cx_ + 60 + i * 9, cy_ - R_ * 0.75 - 70 + 22 * math.sin(i * 0.9 + t * 18)) for i in range(22)]
        d.line(pts, A(YEL, ap(t, at("vib", 3))), 8)
        tag(d, cx_ + 170, cy_ - R_ - 70, "振动", YEL, ap(t, at("vib", 3)), 50)
    ptag(d, t, at("vib", 0.4), 540, 300, "2012", WHITE, 54)
def s_maybe(t, d):
    cutaway(d, t, 1)
    eggs(d, t, crack=1, outs=(1, 1, 1, 1), mouths=[0.3 + 0.3 * math.sin(t * 7 + i) for i in range(4)])
    f = mom(d, t, mood="listen", tilt=1.0, iso=0.5 + 0.4 * math.sin(t * 7), ear=0.3)
    for j, x0 in enumerate((440, 600)):
        pts = [(x0 + 18 * math.sin(i * 1.3 + t * 16 + j), lerp(CY - 140, GY + 10, i / 14)) for i in range(15)]
        d.line(pts, A((255, 236, 120), 0.75), 6)
    stamp(d, t, at("maybe", 0.3), "推测", 540, 330, 130, (255, 150, 60))
    if t > at("maybe", 2): title(d, t, at("maybe", 2), "也许能感觉到？", 460, 80, WHITE)
def s_card(t, d):
    grad(d, (60, 110, 80), (24, 50, 40))
    for i in range(12): d.circ(540, 860, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 640 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 840; a_ = ap(t, T["card"] + 0.1)
    glow(d, cx_, cy_, 560, (200, 255, 200), 0.3 * a_, 6)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 232), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 80, "一句话学会", GOLD, a_, 32)
    croc(d, cx_ - 30, cy_ - 60, 0.5, t, "listen", tilt=1, a=a_, ear=0.8, iso=0.6, breath=False)
    d.text(cx_, cy_ + 50, "鳄鱼妈妈怎么知道娃要出来？", 38, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("耳朵：贴地听叫声（研究者解读）", "小鼓包：感压力和振动", "然后：挖开窝，接娃出来")):
        kk = popk(t, at("card", 1.2 + i * 0.8))
        if kk > 0: d.text(cx_, cy_ + 140 + i * 66, s_, 36, A((60, 70, 90), ap(t, at("card", 1.2 + i * 0.8))), k=1)
def s_water(t, d):
    gy = 1000
    sky(d, t, gy)
    d.rect(-50, gy, 1130, 1960, fill=A(SAND, 1))
    wx = 520
    d.poly([(wx, gy + 10)] + [(x, gy + 10 + 6 * math.sin(x / 30 + t * 4)) for x in range(wx, 1141, 20)] + [(1140, 1960), (wx - 160, 1960)], A(WAT1, 1))
    croc(d, 260, gy - 2, 0.6, t, "soft", blush=0.7, tail=True)
    for i in range(3):
        t0 = at("water", 0.5 + i * 0.9); u = pr(t, t0, t0 + 0.8)
        if u <= 0: continue
        x = lerp(400, 640 + i * 110, u); y = gy - 30 - math.sin(u * math.pi) * 160 + (40 if u >= 1 else 0)
        baby(d, x, y, 0.7, t, "happy", ang=-0.3 + 0.6 * u)
        if t - t0 - 0.8 < 0.5 and u >= 1:
            for j in range(7):
                v = (t - t0 - 0.8) / 0.5; ang = -math.pi / 2 + (j - 3) * 0.35
                d.circ(x + math.cos(ang) * v * 120, y + math.sin(ang) * v * 140 + v * v * 120, 10 * (1 - v) + 3, fill=A(FOAM, 1 - v))
    ka = popk(t, at("water", 2.8))
    if ka > 0:
        x, y = 280, 520
        d.rect(x - 34, y - 40, x + 34, y + 50, fill=A((230, 200, 160), 1), r=10); d.line([(x + 10, y - 40), (x + 26, y - 100)], A(WHITE, 1), 8)
        for j in range(4): d.circ(x - 16 + j * 11, y + 30, 6, fill=A((80, 50, 30), 1))
        cross(d, x, y, 60, pr(t, at("water", 3.3), at("water", 3.6)), (240, 60, 60))
        tag(d, x, y + 110, "弱者喝饮料", WHITE, ap(t, at("water", 2.8)), 36)
    kb = popk(t, at("water", 3.8), "bouncy")
    if kb > 0:
        tag(d, 760, 360, "强者喝大水", GOLD, ap(t, at("water", 3.8)), int(56 * (0.6 + 0.4 * kb)))
        for j in range(3): d.arc(760, 520 + j * 26, 160 - j * 30, 40, 200, 340, A(WAT1, 0.9), 10)
def s_end(t, d):
    cutaway(d, t, 1)
    soft = t > at("end", 2)
    f = mom(d, t, mood="soft" if soft else "fierce", jaw=0 if soft else 0.35, blush=pr(t, at("end", 2), at("end", 3)))
    for i in range(3):
        k = popk(t, at("end", 0.6 + i * 0.5), "bouncy")
        if k <= 0: continue
        bx, by = f["back"][0] - 120 + i * 110, f["back"][1] - 6 - (i == 1) * 10
        baby(d, bx, by - 30 * (1 - min(1, k)), 0.5, t + i, "happy", ang=0.1 * math.sin(t * 3 + i))
    if not soft: ptag(d, t, T["end"] + 0.05, 540, 300, "凶？", WHITE, 90)
    else: slamtxt(d, t, at("end", 2), "不烧心", 290, 140, YEL)
    ra = ap(t, at("end", 4), 0.3)
    if ra > 0:
        d.rect(170, 385, 910, 495, fill=A((10, 20, 34), 0.6 * ra), r=20)
        d.text(540, 418, "Discover Wildlife 2026-11-04 · 相机：Bourquin & Shacks", 25, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 462, "研究者的解读，尚未发表论文", 25, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "偷听", "stay": "歪着头", "q": "地底下", "reveal": "蛋", "call": "叫", "where": "奥卡万戈", "rule": "规矩不能坏", "guard": "很少离开",
      "tilt1": "叼东西", "tilt2": "耳孔贴平地面", "dig": "挖开", "think": "研究者认为", "bumps": "感觉器官", "drop": "一滴水", "vib": "压力和振动",
      "maybe": "推测", "water": "水里", "end": "不烧心"}
def subs(t, d):
    for a, b, s, key in SUBS:
        if a <= t < b:
            ee = E.enter_exit(t, max(a, 0), b, 0.3, 0.12, rise=18, s0=0.96)
            al = ee["alpha"] if a > 0 else (1 - pr(t, b - 0.12, b))
            if al <= 0.01: return
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70 + ee["dy"] * (a > 0)
            w = max(d.tlen(x, 54, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 70 + 46, fill=A((26, 16, 10), 0.82 * al), r=22)
            hw = HL.get(key)
            for i, x in enumerate(ls):
                yy = y0 + i * 70
                if hw and hw in x:
                    j = x.index(hw); parts = [(x[:j], WHITE), (hw, YEL), (x[j + len(hw):], WHITE)]
                    xx = 540 - d.tlen(x, 54, 1) / 2
                    for p_, c_ in parts:
                        if p_: d.text(xx, yy, p_, 54, A(c_, al), anchor="lm", k=1); xx += d.tlen(p_, 54, 1)
                else: d.text(540, yy, x, 54, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇动物"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)
TRAIL = ("stay", "tilt2")
def trail_ui(t, d, key):
    d.rect(170, 236, 910, 1250, outline=A(WHITE, 0.0))
    for (x, y, sx, sy) in ((190, 240, 1, 1), (890, 240, -1, 1), (190, 1240, 1, -1), (890, 1240, -1, -1)):
        d.line([(x, y + sy * 60), (x, y), (x + sx * 60, y)], A(WHITE, 0.85), 6)
    if int(t * 2) % 2 == 0: d.circ(225, 285, 12, fill=A((255, 60, 60), 1))
    d.text(250, 285, "REC  CAM-03", 30, A(WHITE, 0.95), anchor="lm", k=1)
    sec = int(t - T[key]) + (6 if key == "stay" else 41)
    d.text(870, 1200, f"00:00:{sec:02d}", 30, A(WHITE, 0.95), anchor="rm", k=1)

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
    img = Image.new("RGB", (W, H), (20, 30, 50)); d = D(img); key = None
    for a, b, sf, n in SECS:
        if a <= t < b: sf(t, d); key = n; break
    if key in TRAIL:
        g = img.convert("L"); img = ImageOps.colorize(g, (16, 24, 18), (226, 238, 214)); d = D(img)
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - (t - c) / 0.1)))
    if key in TRAIL: trail_ui(t, d, key)
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
