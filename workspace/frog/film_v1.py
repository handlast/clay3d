# 《喜欢吃蜗牛的“小角蛙”，是印度第一只？》 film — flat 2D, no outlines, each line has its own demo.
import sys, subprocess, math, random
from fchars import *
from cues import *

def popk(t, t0, preset="snappy"): return max(0.0, E.spring_at(t, t0, 0, 1, preset)) if t >= t0 else 0.0
def ap(t, t0, d=0.12): return cl((t - t0) / d)
def tag(d, x, y, s, col, a=1.0, size=40, tc=NAVYT):
    if a <= 0.01: return
    w = d.tlen(s, size, 1) + 44
    d.rect(x - w / 2, y - size * 0.78, x + w / 2, y + size * 0.78, fill=A(col, 0.95 * a), r=size * 0.6)
    d.text(x, y, s, size, A(tc, a), k=1)
def ptag(d, t, t0, x, y, s, col, size=40, tc=NAVYT, t1=None):
    k = popk(t, t0)
    if t1 is not None: k *= 1 - pr(t, t1 - 0.15, t1)
    if k > 0: tag(d, x, y + (1 - min(k, 1)) * 30, s, col, min(1, ap(t, t0)) * (1 if t1 is None else 1 - pr(t, t1 - 0.15, t1)), int(size * (0.6 + 0.4 * min(1.1, k))), tc)
def arrow(d, x0, y0, x1, y1, col, a=1.0, w=12):
    L = math.hypot(x1 - x0, y1 - y0) + 1e-6; ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    bx, by = x1 - ux * w * 2.4, y1 - uy * w * 2.4
    d.line([(x0, y0), (bx, by)], A(col, a), w); d.poly([(bx + nx * w * 1.6, by + ny * w * 1.6), (x1, y1), (bx - nx * w * 1.6, by - ny * w * 1.6)], A(col, a))
def check_mark(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 18 * s_, y), (x - 4 * s_, y + 14 * s_), (x + 20 * s_, y - 14 * s_)], A(WHITE, a), 8 * s_)
def cross_mark(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 16 * s_, y - 16 * s_), (x + 16 * s_, y + 16 * s_)], A(WHITE, a), 8 * s_); d.line([(x - 16 * s_, y + 16 * s_), (x + 16 * s_, y - 16 * s_)], A(WHITE, a), 8 * s_)
def zap(d, x, y, t, t0, col=WHITE, maxr=380, a=1.0):
    u = (t - t0) / 0.7
    if 0 <= u < 1:
        for j in range(3): d.circ(x, y, 30 + (u + j * 0.1) * maxr, outline=A(col, a * (1 - u) * (1 - j * 0.3)), w=10 - j * 3)
def bubble(d, x, y, w, h, a=1.0, col=WHITE, tail=(0, 1)):
    d.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=A(col, a), r=min(w, h) * 0.4)
    tx, ty = tail; d.poly([(x - 18, y + h / 2 - 4), (x + 18, y + h / 2 - 4), (x + tx * 40, y + h / 2 + ty * 40)], A(col, a))
def grid(d, col, a, step=90, t=0.0):
    for i in range(-1, 14): d.line([(i * step + (t * 20) % step, 0), (i * step + (t * 20) % step, 1920)], A(col, a), 2)
    for j in range(-1, 23): d.line([(0, j * step), (1080, j * step)], A(col, a), 2)
def hop(t, t0, h=60, dur=0.35):
    u = (t - t0) / dur
    return -h * 4 * u * (1 - u) if 0 <= u <= 1 else 0.0

FX_, FY_ = 540, 900          # hero frog anchor (hook / reveal / end: match cut)

def hero_set(d, t, rain=0.6):
    forest_night(d, t, rain=rain)
    # flashlight pool
    for i in range(8): d.circ(540, 980, 520 - i * 50, fill=A((255, 240, 190), 0.03 + 0.012 * i))
    log_(d, 540, 1100, 760)
    for x, sc, ang in ((150, 1.0, -0.4), (930, 1.1, 0.5), (260, 0.7, 0.2), (820, 0.8, -0.3)):
        for j in range(5):
            a_ = -math.pi / 2 + ang + (j - 2) * 0.25
            leafx = x + math.cos(a_) * 10; leafy = 1180
            d.poly([(leafx, leafy), (leafx + math.cos(a_ - 0.2) * 220 * sc, leafy + math.sin(a_ - 0.2) * 220 * sc), (leafx + math.cos(a_) * 300 * sc, leafy + math.sin(a_) * 300 * sc),
                    (leafx + math.cos(a_ + 0.2) * 220 * sc, leafy + math.sin(a_ + 0.2) * 220 * sc)], A((40, 96, 60) if j % 2 else (54, 120, 72), 1))

# ---------------- scenes ----------------
def s_hook(t, d):
    hero_set(d, t)
    yb = hop(t, 0.05, 40, 0.4) + hop(t, 1.4, 25, 0.3)
    frog(d, FX_, FY_ + yb, 1.25, t, 1, "sus" if t < 1.6 else "smug", look=0.6 * math.sin(t * 2), belly_q=ease(pr(t, 0.2, 0.6)), squash=0.06 * pulse(t, [0.45, 1.7], 10))
    # scanner bar sweeping across the belly
    sy = 760 + 360 * (0.5 - 0.5 * math.cos(t * 2.4))
    d.rect(330, sy - 4, 750, sy + 4, fill=A(CYAN, 0.85)); d.rect(330, sy - 40, 750, sy, fill=A(CYAN, 0.12))
    for i, c in enumerate(COUNT):
        t1 = COUNT[i + 1] if i + 1 < len(COUNT) else BIG1
        k = popk(t, c, "bouncy")
        if c <= t < t1:
            a_ = 1 - pr(t, t1 - 0.12, t1)
            d.circ(540, 420, 110, fill=A((6, 20, 24), 0.6 * a_))
            d.arc(540, 420, 110, 110, -90, -90 + 360 * (1 - pr(t, c, t1)), A(CYAN, a_), 12)
            d.text(540, 420, str(3 - i), int(160 * min(1.15, 0.6 + 0.4 * k)), A(CYAN, a_), k=1)
    ptag(d, t, 0.3, 540, 575, "肚子里有啥？", WHITE, 46)

def s_reveal(t, d):
    t0 = BIG1
    k = ease(pr(t, t0, t0 + 0.25))
    grad(d, mix((20, 52, 50), (10, 30, 80), k), mix((6, 18, 22), (4, 10, 34), k))
    if k > 0: grid(d, XR, 0.12 * k, 90, t)
    sk = [pr(t, t0 + 0.05, t0 + 0.4), pr(t, t0 + 0.35, t0 + 0.7), pr(t, t0 + 0.65, t0 + 1.0)]
    face = "shock" if t < t0 + 1.2 else "scared"
    frog(d, FX_, FY_, 1.25, t, 1, face, xray=k, shells=3, shell_k=sk, blush=ease(pr(t, t0 + 1.2, t0 + 1.5)))
    zap(d, FX_, FY_ + 60, t, t0, SHELL, 460)
    sparks(d, FX_, FY_ + 60, t, t0, 40, 900, SHELL_L, 1, 7, 1.0)
    for i, tt in enumerate((t0 + 0.05, t0 + 0.35, t0 + 0.65)):
        ptag(d, t, tt, [330, 750, 540][i], [1000, 990, 1190][i], str(i + 1), SHELL, 46)
    ptag(d, t, t0 + 0.9, 540, 470, "蜗牛壳 ×3", SHELL, 70)

def s_ct(t, d):
    t0 = T["ct"]
    grad(d, (30, 110, 120), (10, 50, 60))
    grid(d, WHITE, 0.05, 120)
    d.rect(140, 1180, 940, 1220, fill=A((200, 220, 225), 1), r=18)             # tray rail
    u = ease(pr(t, t0 + 0.2, t0 + 2.2))
    fx = lerp(180, 700, u)
    ct_ring(d, 700, 950, 300, t, 1, scan=pr(t, t0 + 1.2, t0 + 2.4))
    inside = cl((fx - 520) / 180)
    frog(d, fx, 1040, 0.55, t, 1, "scared" if u < 0.9 else "sus", xray=inside, shells=3)
    d.circ(700, 950, 300 * 0.66, outline=A((14, 46, 58), 1), w=1)
    # scan beam
    if t0 + 1.0 < t < t0 + 3.2:
        yy = 950 + 180 * math.sin((t - t0) * 6)
        d.rect(520, yy - 3, 880, yy + 3, fill=A(CYAN, 0.9))
    # monitor with 3D render
    ka = popk(t, t0 + 1.6, "bouncy")
    if ka > 0:
        kk = min(1, ka)
        d.rect(170, 330, 560, 640, fill=A((20, 30, 40), 0.95 * kk), r=20); d.rect(190, 350, 540, 620, fill=A((10, 40, 90), kk), r=12)
        frog(d, 365, 520, 0.36 * kk, t, kk, "shock", xray=1, shells=3)
        d.text(365, 300, "3D 透视", 34, A(WHITE, kk), k=1)
    ptag(d, t, t0 + 2.4, 365, 690, "显微 CT", CYAN, 38)

def s_who(t, d):
    t0 = T["who"]
    rays(d, t, (255, 196, 80), (240, 150, 50), 16, 540, 880)
    k = popk(t, t0, "bouncy")
    frog(d, 540, 870 + hop(t, t0 + 0.05, 70, 0.4), 0.95 * min(1.05, 0.7 + 0.3 * k), t, 1, "proud", blush=0.5)
    # NEW badge
    kb = popk(t, t0 + 0.4, "bouncy")
    if kb > 0:
        r = 92 * min(1.1, kb)
        for i in range(16):
            an = i * math.pi / 8 + t * 0.6
            d.poly([(820 + math.cos(an) * r * 1.25, 560 + math.sin(an) * r * 1.25), (820 + math.cos(an + 0.2) * r, 560 + math.sin(an + 0.2) * r), (820 + math.cos(an - 0.2) * r, 560 + math.sin(an - 0.2) * r)], A((240, 60, 70), 1))
        d.circ(820, 560, r, fill=A((240, 60, 70), 1)); d.text(820, 548, "新", int(64 * min(1.1, kb)), A(WHITE, 1), k=1); d.text(820, 600, "物种", int(30 * min(1.1, kb)), A(WHITE, 1), k=1)
    # name plate
    kn = popk(t, t0 + 1.4, "bouncy")
    if kn > 0:
        kk = min(1, kn); y = 1130 + (1 - kk) * 40
        d.rect(250, y - 60, 830, y + 60, fill=A(WHITE, kk), r=30); d.text(540, y, "吃蜗牛角蟾", 64, A(NAVYT, kk), k=1)
    sx = lerp(1200, 920, ease(pr(t, t0 + 2.0, t0 + 2.6)))
    snail(d, sx, 1180, 0.5, t, 1, "scared", flip=-1, crawl=1)

def s_name(t, d):
    t0 = T["name"]
    grad(d, (255, 160, 110), (120, 70, 120))
    d.circ(780, 520, 120, fill=A((255, 236, 170), 0.95))
    mtn(d, 0, [(150, 90, 130), (110, 64, 110), (70, 44, 84)], 1, seed=5, amp=300, y0=1050)
    # dictionary card flip
    k = popk(t, t0 + 0.1, "bouncy")
    if k > 0:
        kk = min(1, k); cx, cy = 540, 640
        d.rect(cx - 330 * kk, cy - 200, cx + 330 * kk, cy + 200, fill=A(WHITE, 0.97), r=30)
        d.text(cx, cy - 120, "阿帕塔尼语（当地话）", 32, A((120, 110, 130), kk), k=1)
        d.text(cx, cy - 40, "tanogogo", 84, A(NAVYT, kk), k=0)
        ke = popk(t, t0 + 1.0, "bouncy")
        if ke > 0:
            d.text(cx - 110, cy + 100, "=", 80, A(SHELL, min(1, ke)), k=1)
            d.text(cx + 30, cy + 100, "蜗牛", int(76 * min(1.1, ke)), A(SHELL, min(1, ke)), k=1)
            shell(d, cx + 200, cy + 100, 46 * min(1, ke), 1)
    fr = "love" if t > t0 + 1.4 else "happy"
    frog(d, 330, 1110, 0.7, t, 1, fr)
    snail(d, 790, 1190, 0.65, t, 1, "scared" if t > t0 + 1.4 else "happy", flip=-1, crawl=1.0 - pr(t, t0 + 1.4, t0 + 1.6), hide=ease(pr(t, t0 + 1.6, t0 + 2.2)))

def s_q(t, d):
    t0 = T["q"]
    grad(d, (30, 24, 50), (8, 6, 16))
    for i in range(6): d.poly([(540 - 90 + i * 2, 0), (540 + 90 - i * 2, 0), (540 + 380 - i * 40, 1500), (540 - 380 + i * 40, 1500)], A((255, 240, 200), 0.025))
    d.ell(540, 1360, 400, 70, A((255, 240, 200), 0.18))
    d.rect(370, 1220, 710, 1360, fill=A((90, 70, 130), 1), r=12); d.text(540, 1290, "No.1 ?", 56, A(GOLD, 1), k=1)
    frog(d, 540, 1060, 0.85, t, 1, "smug", look=0.5 * math.sin(t * 2))
    k = popk(t, t0 + 0.3, "bouncy")
    if k > 0:
        tr = min(1.1, k); cx, cy = 540, 560 + 8 * math.sin(t * 5)   # trophy with ?
        d.poly([(cx - 90 * tr, cy - 90 * tr), (cx + 90 * tr, cy - 90 * tr), (cx + 50 * tr, cy + 30 * tr), (cx - 50 * tr, cy + 30 * tr)], A(GOLD, 1))
        d.rect(cx - 16 * tr, cy + 30 * tr, cx + 16 * tr, cy + 80 * tr, fill=A(GOLD, 1)); d.rect(cx - 60 * tr, cy + 80 * tr, cx + 60 * tr, cy + 104 * tr, fill=A((200, 150, 40), 1), r=6)
        d.text(cx, cy - 34 * tr, "?", int(110 * tr), A(NAVYT, 1), k=1)
    for i, x in enumerate((180, 900)):   # silhouettes of other frogs in the dark
        frog_icon(d, x, 1300, 0.45, 0.5, "grey", "sus", t)
        if t > t0 + 1.0 + i * 0.3: d.text(x, 1100, "?", 80, A(WHITE, 0.6 * ap(t, t0 + 1.0 + i * 0.3)), k=1)

FAM = [(190, 790, 0.4, "grey"), (400, 740, 0.44, "olive"), (680, 740, 0.44, "choc"), (890, 790, 0.4, "rust"), (210, 1060, 0.44, "gold"), (870, 1060, 0.44, "olive")]
def s_big2(t, d):
    t0 = BIG2
    rays(d, t, (130, 80, 200), (70, 40, 130), 18, 540, 1000)
    d.rect(200, 300, 880, 380, fill=A(WHITE, 0.95), r=40); d.text(540, 340, "角蟾家族", 50, A(NAVYT, 1), k=1)
    for i, (x, y, s, p) in enumerate(FAM):
        k = popk(t, t0 + 0.05 + i * 0.06, "bouncy")
        if k <= 0: continue
        frog_icon(d, x, y, s * min(1.05, k), 1, p, "shock" if t > t0 + 1.6 else "happy", t + i)
        if t > t0 + 2.6: cross_mark(d, x + 70, y - 110, 26, (230, 70, 80), 1, popk(t, t0 + 2.6 + i * 0.08, "bouncy"))
    ch = t0 + 0.9
    mo = ease(pr(t, ch, ch + 0.2)) * (1 - ease(pr(t, ch + 0.35, ch + 0.5)))
    frog(d, 540, 1040, 0.72, t, 1, "chew" if ch + 0.5 < t < ch + 2.0 else ("proud" if t > ch + 2 else "happy"), mouth=mo, cheeks=0.6 * pr(t, ch + 0.5, ch + 0.7) * (1 - pr(t, ch + 1.8, ch + 2.0)))
    if t < ch + 0.4:
        sx = lerp(820, 600, ease(pr(t, t0, ch + 0.3))); snail(d, sx, 1150, 0.4, t, 1, "scared", flip=-1)
    if t > t0 + 1.8:
        stamp(d, t, t0 + 1.8, "第一次！", 540, 500, 140, (255, 80, 90))
        if t > t0 + 2.3: tag(d, 540, 610, "首次记录：角蟾科吃蜗牛", WHITE, ap(t, t0 + 2.3, 0.3), 30)

def s_other(t, d):
    t0 = T["other"]
    grad(d, (60, 140, 150), (20, 70, 80))
    d.rect(-50, 1180, 1130, 1970, fill=A((30, 90, 110), 1))
    for i in range(5): d.ell(200 + i * 180, 1220 + 10 * math.sin(t * 2 + i), 90, 14, A(WHITE, 0.12))
    d.rect(538, 300, 542, 1500, fill=A(WHITE, 0.5))
    # left: 黑斑蛙 (green, black spots, no horns) eating a snail
    k = popk(t, t0, "bouncy")
    frog(d, 290, 880, 0.62 * min(1.05, k), t, 1, "chew" if t > t0 + 1.0 else "happy", pal="green", horns=False, mouth=ease(pr(t, t0 + 0.6, t0 + 0.8)) * (1 - ease(pr(t, t0 + 0.9, t0 + 1.0))))
    if t < t0 + 0.9: snail(d, lerp(470, 330, ease(pr(t, t0 + 0.1, t0 + 0.85))), 1010, 0.3, t, 1, "scared", flip=-1)
    ptag(d, t, t0 + 0.4, 290, 560, "黑斑蛙", (150, 214, 130), 44)
    check_mark(d, 290, 1090, 40, (80, 190, 110), 1, popk(t, t0 + 1.4, "bouncy"))
    if t > t0 + 1.4: d.text(290, 1170, "早就吃过", 40, A(WHITE, ap(t, t0 + 1.5)), k=1)
    # right: ours (horned) with crown "角蟾家族首次"
    frog(d, 790, 880, 0.62, t, 1, "happy", look=-0.6)
    ptag(d, t, t0 + 0.8, 790, 560, "吃蜗牛角蟾", FROG_L, 40)
    if t > t0 + 2.0: d.text(790, 1170, "角蟾家族第一个", 40, A(GOLD, ap(t, t0 + 2.0)), k=1)

def s_kin(t, d):
    t0 = T["kin"]
    grad(d, (14, 34, 90), (4, 10, 34)); grid(d, XR, 0.1, 90, t)
    d.rect(538, 500, 542, 1180, fill=A(WHITE, 0.25))
    frog(d, 290, 860, 0.72, t, 1, "happy", xray=1, shells=3)
    kr = popk(t, t0 + 0.9, "bouncy")
    if kr > 0:
        kk = min(1.05, kr)
        xr = ease(pr(t, t0 + 1.6, t0 + 2.0))
        frog(d, 790, 860, 0.72 * kk, t, 1, "shock" if xr > 0.5 else "happy", pal="olive", xray=xr, shells=0)
        if xr > 0.5:
            ks = popk(t, t0 + 2.0, "bouncy")
            if ks > 0:
                shell(d, 790, 860 + 0.72 * 50, 30 * min(1.1, ks), 1, SHELL, SHELL_L, (200, 90, 20), glowk=0.9)
                zap(d, 790, 896, t, t0 + 2.0, SHELL, 260)
    ptag(d, t, t0 + 0.2, 290, 540, "吃蜗牛角蟾", FROG_L, 36)
    ptag(d, t, t0 + 0.2, 290, 1110, "3 个壳", SHELL, 46)
    ptag(d, t, t0 + 1.0, 790, 540, "近亲 J. vegrandis", (176, 180, 110), 32)
    ptag(d, t, t0 + 2.2, 790, 1110, "1 个壳", SHELL, 46)
    if t > t0 + 3.2: tag(d, 540, 420, "两种吃蜗牛，都是首次记录", GOLD, ap(t, t0 + 3.2, 0.3), 32)

def s_gulp(t, d):
    t0 = T["gulp"]
    grad(d, (240, 236, 220), (210, 200, 180))
    CM = 127; x0 = 540 - 1.5 * CM; ry = 1020      # ruler: 3 cm == the frog's body length on screen
    rk = ease(pr(t, t0, t0 + 0.6))
    d.rect(x0 - 30, ry, x0 - 30 + (3 * CM + 90) * rk, ry + 80, fill=A((255, 214, 90), 1), r=10)
    for i in range(31):
        xx = x0 + i * CM / 10
        if xx > x0 - 30 + (3 * CM + 90) * rk: break
        d.line([(xx, ry), (xx, ry + (38 if i % 10 == 0 else (28 if i % 5 == 0 else 18)))], A(NAVYT, 1), 4 if i % 10 == 0 else 3)
        if i % 10 == 0: d.text(xx, ry + 58, str(i // 10), 28, A(NAVYT, 1), k=1)
    d.text(x0 + 3 * CM + 40, ry + 58, "cm", 26, A(NAVYT, rk), k=1)
    sc = 3 * CM / 380
    frog(d, 540, ry - 150 * sc, sc, t, 1, "shock" if t > t0 + 2.2 else "happy", mouth=0.5 * ease(pr(t, t0 + 2.4, t0 + 2.7)))
    if t > t0 + 0.8:
        a_ = ap(t, t0 + 0.8, 0.3); by = ry - 18; c_ = (240, 70, 80)
        d.line([(x0, by), (x0 + 3 * CM, by)], A(c_, a_), 6); d.line([(x0, by - 16), (x0, by + 16)], A(c_, a_), 6); d.line([(x0 + 3 * CM, by - 16), (x0 + 3 * CM, by + 16)], A(c_, a_), 6)
        tag(d, x0 + 3 * CM + 110, ry - 60, "约 3 厘米", c_, a_, 32, WHITE)
    snail(d, 860, 640, 0.42, t, 1, "sus", flip=-1, crawl=0.5)
    k = popk(t, t0 + 2.0, "bouncy")
    if k > 0: d.text(740, 470 + 10 * math.sin(t * 5), "?", int(170 * min(1.1, k)), A((240, 70, 80), 1), k=1)
    ptag(d, t, t0 + 2.6, 540, 330, "整只吞？", NAVYT, 50, tc=WHITE)

def s_jaw(t, d):
    t0 = T["jaw"]
    grad(d, (26, 40, 70), (10, 16, 34)); grid(d, (120, 160, 255), 0.07, 80)
    # side-view frog head (X-ray tint): skull on top, lower jaw hinged at the BACK, swings open
    hx, hy = 330, 860                 # jaw joint
    op = 0.5 - 0.5 * math.cos((t - t0) * 3.0)
    ang = 0.55 * op * ease(pr(t, t0 + 0.5, t0 + 0.9))
    up = [(hx - 30, hy - 10), (hx + 20, hy - 120), (hx + 160, hy - 170), (hx + 330, hy - 140), (hx + 470, hy - 60), (hx + 500, hy - 20), (hx + 470, hy)]
    up = [rot(x, y, hx, hy, -ang * 0.25) for x, y in up]
    d.poly(up + [(hx, hy + 10)], A((60, 110, 210), 0.9))
    ex, ey = rot(hx + 210, hy - 150, hx, hy, -ang * 0.25)
    d.circ(ex, ey - 20, 62, fill=A((60, 110, 210), 1)); d.circ(ex, ey - 22, 40, fill=A(WHITE, 1)); d.circ(ex + 10, ey - 18, 20, fill=A(INK, 1))
    hn = rot(hx + 190, hy - 205, hx, hy, -ang * 0.25)
    d.poly([(hn[0] - 30, hn[1] + 30), (hn[0] - 10, hn[1] - 40), (hn[0] + 20, hn[1] + 26)], A(XR, 1))       # eyelid horn
    sk = [rot(x, y, hx, hy, -ang * 0.25) for x, y in [(hx + 10, hy - 40), (hx + 150, hy - 110), (hx + 330, hy - 100), (hx + 470, hy - 30)]]
    d.line(sk, A(BONE, 0.9), 12)                                                                       # skull line
    lo = [rot(x, y, hx, hy, ang) for x, y in [(hx - 10, hy + 10), (hx + 150, hy + 70), (hx + 320, hy + 60), (hx + 470, hy + 10), (hx + 470, hy - 4), (hx + 10, hy - 6)]]
    d.poly(lo, A((50, 96, 190), 0.95))
    d.line([rot(x, y, hx, hy, ang) for x, y in [(hx, hy + 6), (hx + 160, hy + 46), (hx + 460, hy + 2)]], A(BONE, 0.9), 12)   # jaw bone
    if ang > 0.08:   # pink mouth inside
        m1 = rot(hx + 440, hy - 6, hx, hy, -ang * 0.25); m2 = rot(hx + 440, hy - 4, hx, hy, ang)
        d.poly([(hx + 30, hy), m1, m2], A((255, 120, 140), 0.85))
    ka = ease(pr(t, t0 + 0.3, t0 + 0.7))
    glow_disc(d, hx, hy, 80, GOLD, 0.9 * ka); d.circ(hx, hy, 20, fill=A(GOLD, ka))
    ptag(d, t, t0 + 0.6, hx + 20, hy + 150, "下巴关节", GOLD, 36)
    ptag(d, t, t0 + 1.2, 700, 560, "头骨形状", BONE, 36)
    shell(d, 860, 880 - 10 * op, 54, 1)
    # magnifier + progress
    k = popk(t, t0 + 2.2, "bouncy")
    if k > 0:
        kk = min(1, k); mx, my = 820 + 20 * math.sin(t * 2), 400
        d.circ(mx, my, 80 * kk, fill=A((170, 220, 255), 0.25)); d.circ(mx, my, 80 * kk, outline=A(WHITE, 0.95), w=14)
        d.line([(mx + 56 * kk, my + 56 * kk), (mx + 130 * kk, my + 130 * kk)], A(WHITE, 0.95), 24)
        p = 0.2 + 0.5 * pr(t, t0 + 2.4, t0 + 4.8)
        d.rect(250, 1110, 830, 1150, fill=A(WHITE, 0.2 * kk), r=20); d.rect(250, 1110, 250 + 580 * p, 1150, fill=A(GOLD, kk), r=20)
        d.text(540, 1060, "研究中…", 40, A(WHITE, kk), k=1)

def s_survey(t, d):
    t0 = T["survey"]
    grad(d, (60, 90, 140), (20, 30, 60))
    mtn(d, 0, [(200, 210, 230), (120, 140, 170), (60, 100, 90), (30, 70, 60)], 1, seed=9, amp=380, y0=900)
    for i in range(6):   # snow caps
        d.circ(120 + i * 180, 560 + 40 * math.sin(i * 2), 26, fill=A(WHITE, 0.6))
    rr = random.Random(4)
    for i in range(14):    # headlamp dots appear one by one (searchers)
        tt = t0 + 0.4 + i * 0.2
        if t > tt:
            x, y = rr.uniform(220, 860), rr.uniform(1000, 1360)
            glow_disc(d, x, y, 40, (255, 240, 170), ap(t, tt, 0.2)); d.circ(x, y, 7, fill=A((255, 250, 210), ap(t, tt, 0.2)))
    # calendar flipping 2021 -> 2025
    yrs = 2021 + min(4, int(max(0, t - t0 - 0.3) / 0.6))
    k = popk(t, t0 + 0.3 + (yrs - 2021) * 0.6, "bouncy")
    d.rect(370, 320, 710, 560, fill=A(WHITE, 0.97), r=24); d.rect(370, 320, 710, 380, fill=A((240, 80, 80), 1), r=24)
    d.text(540, 470, str(yrs), int(96 * (0.85 + 0.15 * min(1, k))), A(NAVYT, 1), k=1)
    ptag(d, t, t0 + 2.8, 540, 640, "5 年", GOLD, 60)
    ptag(d, t, t0 + 0.6, 540, 820, "印度 · 喜马拉雅山东部", WHITE, 34)

FIVE = [("taniitatii", "tan"), ("tanogogo", "rust"), ("siangensis", "olive"), ("hrdy", "choc"), ("wularsoni", "gold")]
def s_five(t, d):
    t0 = T["five"]
    rays(d, t, (90, 200, 140), (40, 140, 100), 16, 540, 900)
    pos = [(300, 660), (780, 660), (540, 870), (300, 1080), (780, 1080)]
    for i, ((nm, p), (x, y)) in enumerate(zip(FIVE, pos)):
        k = popk(t, t0 + 0.1 + i * 0.22, "bouncy")
        if k <= 0: continue
        frog_icon(d, x, y + hop(t, t0 + 0.1 + i * 0.22, 50, 0.3), 0.5 * min(1.08, k), 1, p, "happy", t + i)
        tag(d, x, y + 135, "J. " + nm, WHITE, min(1, k), 28)
    k = popk(t, t0 + 1.3, "bouncy")
    if k > 0: d.text(540, 400, "5", int(220 * min(1.1, k)), A(GOLD, 1), k=1)

def s_double(t, d):
    t0 = T["double"]
    grad(d, (36, 30, 70), (14, 10, 30))
    # 6 known (grey) + 5 new (colour) — counter 6 -> 11
    cols = ["grey"] * 6 + [p for _, p in FIVE]
    for i in range(11):
        r_, c_ = divmod(i, 4); x = 250 + c_ * 195; y = 640 + r_ * 210
        t1 = t0 + 0.1 + i * 0.08 if i < 6 else t0 + 1.4 + (i - 6) * 0.2
        k = popk(t, t1, "bouncy")
        if k <= 0: continue
        frog_icon(d, x, y, 0.26 * min(1.08, k), 1, cols[i], "happy" if i >= 6 else "sus", t + i, grey=0.0)
        if i >= 6: d.circ(x + 52, y - 78, 22, fill=A((240, 60, 70), min(1, k))); d.text(x + 52, y - 78, "新", 22, A(WHITE, min(1, k)), k=1)
    n = 6 if t < t0 + 1.4 else min(11, 6 + int((t - t0 - 1.4) / 0.2) + 1)
    d.text(540, 420, f"{n} 种", int(130 * (1 + 0.08 * pulse(t, [t0 + 1.4 + j * 0.2 for j in range(5)], 10))), A(GOLD if n == 11 else WHITE, 1), k=1)
    ptag(d, t, t0 + 2.8, 540, 1150, "翻了一倍还多", (255, 120, 120), 44, tc=WHITE)

def s_card(t, d):
    t0 = T["card"]
    grad(d, (255, 214, 120), (240, 160, 80))
    k = popk(t, t0, "smooth"); a_ = min(1, k)
    cx_, cy_ = 540, 860
    d.rect(170, 420, 910, 1340, fill=A(WHITE, 0.97 * a_), r=40)
    d.rect(330, 450, 750, 520, fill=A((240, 80, 80), a_), r=35); d.text(540, 485, "一句话学会", 40, A(WHITE, a_), k=1)
    d.text(540, 610, "新物种", 96, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("科学家第一次", "正式描述、起名的物种")):
        kk = ap(t, t0 + 0.6 + i * 0.5, 0.25)
        if kk > 0: d.text(540, 740 + i * 76, s_, 46, A(NAVYT, kk * a_), k=1)
    kk = ap(t, t0 + 1.8, 0.3)
    if kk > 0:
        frog_icon(d, 400, 1120, 0.38, kk, "rust", "proud", t)
        d.rect(560, 1060, 820, 1140, fill=A((255, 236, 200), kk), r=20); d.text(690, 1100, "J. tanogogo", 30, A(NAVYT, kk), k=0)
        d.text(690, 1180, "2026 年命名", 30, A((120, 110, 100), kk), k=1)

def s_end(t, d):
    t0 = T["end"]
    hero_set(d, t, 0.4)
    frog(d, FX_ - 120, FY_ + 60, 1.0, t, 1, "happy", look=0.7)
    snail(d, 780, 1080, 0.55, t, 1, "sus", flip=-1, look=-0.5)
    k = popk(t, t0 + 0.2, "bouncy")
    if k > 0:
        bubble(d, 540, 430, 640 * min(1.05, k), 150, 0.95)
        d.text(540, 420, "谁还爱吃蜗牛？", int(56 * min(1.05, k)), A(NAVYT, 1), k=1)
    ra = ap(t, t0 + 1.8, 0.3)
    if ra > 0:
        d.rect(170, 560, 910, 720, fill=A((6, 8, 20), 0.7 * ra), r=20)
        d.text(540, 597, "Garg et al. 2026, R. Soc. Open Sci. 13:261030", 23, A(WHITE, 0.95 * ra), k=0)
        d.text(540, 638, "doi:10.1098/rsos.261030", 24, A(WHITE, 0.85 * ra), k=0)
        d.text(540, 680, "报道：BBC News 2026-11-12", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "藏着什么", "reveal": "三个蜗牛壳", "ct": "CT", "who": "新物种", "name": "蜗牛", "q": "第一只",
      "big2": "第一次", "other": "黑斑蛙", "kin": "也有蜗牛壳", "gulp": "3 厘米", "jaw": "还在研究", "survey": "5 年", "five": "5 个新物种",
      "double": "11 种", "card": "新物种", "end": "评论区"}
def subs(t, d):
    for a, b, s, key in SUBS:
        if key == "card": continue
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
    s = "Vibe 知识大赏"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)
    d.text(540, 228, "新物种 · 爱吃蜗牛的小角蟾", 24, A((235, 235, 225), 0.85), k=1)

SF = {n: globals()["s_" + n] for n in NAMES}
SECS = [(-1, T["reveal"], s_hook, "hook")] + [(T[n], nxt(n), SF[n], n) for n in NAMES[1:]]
SECS = [(a, (99 if i == len(SECS) - 1 else b), f, n) for i, (a, b, f, n) in enumerate(SECS)]
HARD = {BIG1, BIG2}
def cam(t):
    z = 1.0 + 0.04 * pulse(t, [BIG1, BIG2], 3); cx, cy = 540, 900
    if t < BIG1:
        z += 0.06 * E.ease_in_out_sine(pr(t, 0, BIG1)) + 0.02; cx = 510 + 40 * E.ease_in_out_sine(pr(t, 0, BIG1)); cy = 930
    elif t < T["ct"]:
        z += 0.08 + 0.06 * ease(pr(t, BIG1 + 0.2, BIG1 + 1.2)); cx, cy = 540, 960
    else:
        for a, b, f, n in SECS:
            if a <= t < b: z += 0.03 * eio(pr(t, max(a, 0), min(b, DUR))); break
    sx, sy = shake(t, 8 * pulse(t, [BIG1, BIG2], 5), 40)
    return z, cx + sx, cy + sy
def render_world(t, idx):
    img = Image.new("RGB", (W, H), (20, 40, 30)); d = D(img)
    SECS[idx][2](t, d)
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
XF = 0.3
def frame(t, fi=0, ui=True):
    idx = next(i for i, (a, b, f, n) in enumerate(SECS) if a <= t < b)
    img = render_world(t, idx)
    a = SECS[idx][0]
    if idx > 0 and a not in HARD and t < a + XF:
        prev = render_world(t, idx - 1)
        img = Image.blend(prev, img, E.ease_in_out_sine((t - a) / XF))
    d = D(img)
    for c in HARD:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.55 * (1 - (t - c) / 0.1)))
    brand(t, d)
    if ui: subs(t, d)
    out = img.resize((OW, OH), Image.LANCZOS)
    out = E.vignette(out, 0.2); out = E.grain(out, 0.03, seed=fi)
    return out
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/fg_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[3:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=4, thumb_w=400, labels=[f"{x:.1f}s" for x in ts]).save(sys.argv[2])
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                              "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", out], stdin=subprocess.PIPE)
        last = None; errs = 0
        for i in range(i0, i1):
            try: last = frame(i / FPS, i).tobytes()
            except Exception as e: errs += 1; print('ERR', i, e, file=sys.stderr)
            if last: p.stdin.write(last)
        p.stdin.close(); p.wait(); print('errs', errs, file=sys.stderr)
