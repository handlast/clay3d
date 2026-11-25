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
GY = 1000
BGS = {"river": ((40, 120, 110), (14, 60, 60)), "jungle": ((50, 110, 70), (16, 50, 30)), "dusk": ((150, 80, 70), (50, 24, 40)), "navy": ((24, 34, 70), (8, 12, 28)),
       "plum": ((80, 40, 110), (30, 14, 50)), "gold": ((180, 120, 40), (80, 46, 10)), "red": ((150, 40, 60), (60, 14, 26)), "grass": ((120, 150, 60), (50, 70, 24))}
def bg(d, t, k, deco=True): flatbg(d, BGS[k][0], BGS[k][1], t, deco)
def ground(d, col=(255, 255, 255), a=0.10, y=None): d.rect(0, (y or GY + 125), 1080, 1920, fill=A(col, a))
def river(d, t, y=GY + 125):
    d.rect(0, y, 1080, 1920, fill=A((60, 150, 200), 0.55))
    for i in range(6):
        xx = (i * 230 + t * 60) % 1300 - 120
        d.line([(xx, y + 40 + i % 3 * 50), (xx + 90, y + 40 + i % 3 * 50)], A(WHITE, 0.35), 5)
def check(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 18 * s_, y), (x - 4 * s_, y + 14 * s_), (x + 20 * s_, y - 14 * s_)], A(WHITE, a), 8 * s_)
def xmark(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 15 * s_, y - 15 * s_), (x + 15 * s_, y + 15 * s_)], A(WHITE, a), 8 * s_); d.line([(x - 15 * s_, y + 15 * s_), (x + 15 * s_, y - 15 * s_)], A(WHITE, a), 8 * s_)
def heart(d, x, y, r, col=PINK, a=1.0):
    if r <= 0: return
    d.circ(x - r * 0.5, y - r * 0.2, r * 0.58, fill=A(col, a)); d.circ(x + r * 0.5, y - r * 0.2, r * 0.58, fill=A(col, a))
    d.poly([(x - r * 1.05, y), (x + r * 1.05, y), (x, y + r * 1.1)], A(col, a))
def hearts(d, t, t0, x, y, n=5, a=1.0):
    for i in range(n):
        u = pr(t, t0 + i * 0.18, t0 + i * 0.18 + 1.2)
        if 0 < u < 1: heart(d, x + 60 * math.sin(i * 2.1 + u * 3), y - 260 * u, 26 * (0.6 + 0.4 * math.sin(u * math.pi)), PINK, a * (1 - u ** 3))
def bubble_txt(d, t, t0, x, y, s, col, size=70, tail=-1):
    k = popk(t, t0, "bouncy")
    if k <= 0: return
    sz = int(size * min(1.1, k)); w = d.tlen(s, sz, 1) + 60
    d.rect(x - w / 2, y - sz * 0.85, x + w / 2, y + sz * 0.85, fill=A(WHITE, 0.97), r=sz * 0.6)
    d.poly([(x + tail * 30, y + sz * 0.7), (x + tail * 80, y + sz * 1.5), (x + tail * 70, y + sz * 0.7)], A(WHITE, 0.97))
    d.text(x, y, s, sz, A(col, 1), k=1)
def poof(d, t, t0, x, y, r=120):
    u = pr(t, t0, t0 + 0.45)
    if 0 < u < 1:
        for i in range(8):
            an = i * math.pi / 4; rr = r * ease(u)
            d.circ(x + math.cos(an) * rr, y + math.sin(an) * rr * 0.7, 40 * (1 - u), fill=A(WHITE, 0.9 * (1 - u)))
def demo(d, a=0.5): tag(d, 900, 250, "示意", WHITE, a, 26)

def s_hook(t, d):
    bg(d, t, "river"); river(d, t)
    sx = 6 * math.sin(t * 40) * pr(t, 0.0, 0.1) * (1 - pr(t, 0.4, 0.6))
    bigcat(d, 130, GY - 40, 0.7, t, mood="hiss", flat=1, cub=True, bob=0.4)
    bigcat(d, 950, GY - 40, 0.7, t, mood="hiss", flat=1, cub=True, flip=-1, bob=0.4)
    bigcat(d, 320 + sx, GY + 30, 0.78, t, mood="hiss", flat=1, bob=0.4)
    bigcat(d, 760 - sx, GY + 30, 0.78, t, mood="hiss", flat=1, flip=-1, bob=0.4)
    bubble_txt(d, t, 0.0, 330, 560, "老吴——！", MEAN, 74, 1)
    bubble_txt(d, t, 1.1, 760, 700, "老吴！！", MEAN, 66, -1)
    rings(d, 540, 900, t, [0.0, 1.1], WHITE, 0.6, 360)
    demo(d)
def s_q(t, d):
    bg(d, t, "dusk"); river(d, t)
    t0 = T["q"]; c = ramp(t, t0, t0 + 1.2)
    bigcat(d, lerp(300, 350, c), GY, 0.85, t, mood="hiss", flat=1, bob=0.2)
    bigcat(d, lerp(780, 730, c), GY, 0.85, t, mood="hiss", flat=1, flip=-1, bob=0.2)
    for i in range(3):  # VS lightning between faces
        if (int(t * 12) + i) % 3 == 0:
            pts = [(540 + (j - 3) * 18, 820 + ((j * 37 + int(t * 30)) % 50) - 25) for j in range(7)]
            d.line(pts, A((255, 240, 120), 0.9), 6)
    k = popk(t, t0 + 0.5, "bouncy")
    if k > 0: d.text(540, 560, "VS", int(140 * min(1.05, k)), A(GOLD, 1), k=1)
    demo(d)
def s_reveal(t, d):
    rays(d, t, (255, 170, 200), (150, 60, 120))
    t0 = BIG2; flip_t = t0 + 1.4
    if t < flip_t:
        bigcat(d, 280, GY, 0.72, t, pose="belly", mood="happy")
        bigcat(d, 800, GY, 0.72, t, pose="belly", mood="happy", flip=-1)
    else:
        lk = 0.5 + 0.5 * math.sin((t - flip_t) * 9)
        bigcat(d, 330, GY, 0.8, t, mood="happy", lick=lk, bob=0.3)
        bigcat(d, 750, GY, 0.8, t, mood="happy", flip=-1, bob=0.3)
        tag(d, 540, 450, "互相舔毛", PINK, ap(t, flip_t + 0.1, 0.2), 52)
    poof(d, t, t0, 330, GY - 40); poof(d, t, t0, 750, GY - 40); poof(d, t, flip_t, 540, GY - 60, 200)
    if t < flip_t: tag(d, 540, 450, "翻肚皮", GOLD, ap(t, t0 + 0.2, 0.2), 52)
    hearts(d, t, t0 + 0.3, 540, GY - 150, 7)
    if t > t0: sparks(d, 540, 820, t, t0, 40, 1100, (255, 230, 150), 1, 3, 0.9)
def s_solo(t, d):
    bg(d, t, "jungle")
    t0 = T["solo"]
    d.ell(540, GY + 140, 300, 60, A((90, 80, 70), 1)); d.ell(540, GY + 120, 260, 50, A((120, 110, 95), 1))
    bigcat(d, 520, GY, 1.1, t, mood="neutral", bob=0.5)
    stamp(d, t, t0 + 0.3, "独行侠", 540, 470, 150, MEAN, 1, -8)
    k = ap(t, t0 + 1.6, 0.25)
    if k > 0:
        for j, (dx, dy) in enumerate(((-120, -50), (60, 40), (150, -30), (-30, 70))):
            d.line([(540, 470), (540 + dx * k, 470 + dy * k)], A(WHITE, 1), 7)
        d.text(830, 360, "?", int(150 * popk(t, t0 + 1.7)), A(GOLD, 1), k=1)
def s_team(t, d):
    bg(d, t, "river", False)
    t0 = T["team"]
    d.rect(0, GY - 40, 1080, 1920, fill=A((60, 150, 200), 0.6))
    for i in range(7):
        xx = (i * 190 + t * 90) % 1300 - 120
        d.line([(xx, GY + 20 + (i % 3) * 60), (xx + 90, GY + 20 + (i % 3) * 60)], A(WHITE, 0.35), 5)
    bx = lerp(-150, 1230, pr(t, t0, T["ids"]))
    d.poly([(bx - 150, GY - 20), (bx + 150, GY - 20), (bx + 110, GY + 30), (bx - 120, GY + 30)], A((230, 230, 235), 1))
    d.circ(bx - 20, GY - 70, 32, fill=A((250, 205, 170), 1)); d.rect(bx - 50, GY - 45, bx + 10, GY - 15, fill=A((80, 140, 220), 1), r=10)
    d.rect(bx + 5, GY - 85, bx + 55, GY - 60, fill=A(NOSE, 1), r=10)  # binoculars
    # year counter 2013 -> 2025
    yr = int(round(lerp(2013, 2025, ease(pr(t, t0 + 0.2, t0 + 2.2)))))
    d.rect(330, 380, 750, 560, fill=A((250, 248, 240), 1), r=30)
    d.text(540, 470, str(yr), 130, A(NAVYT, 1), k=1)
    ptag(d, t, t0 + 0.5, 540, 650, "13年 · 1710天沿河调查", GOLD, 44)
    ptag(d, t, t0 + 0.9, 540, 300, "巴西 · 潘塔纳尔北部", MINT, 40)
def s_ids(t, d):
    bg(d, t, "navy")
    t0 = T["ids"]
    rv = random.Random(4)
    for i in range(3):
        x = 220 + i * 320; y = 560
        k = popk(t, t0 + i * 0.2)
        if k <= 0: continue
        d.rect(x - 140, y - 160, x + 140, y + 160, fill=A((250, 246, 234), 1), r=24)
        d.ell(x, y - 20, 110 * min(1, k), 80 * min(1, k), A(JAG, 1))
        for j in range(7):
            px = x + rv.uniform(-80, 80); py = y - 20 + rv.uniform(-50, 50)
            d.circ(px, py, 14, fill=A(JAG_D, 1)); d.circ(px + 1, py, 7, fill=A(mix(JAG, JAG_D, 0.25), 1))
        d.text(x, y + 115, "No.%03d" % (17 + i * 131), 38, A(NAVYT, 1), k=1)
    # magnifier scanning
    u = pr(t, t0 + 0.3, t0 + 2.0)
    mx = lerp(150, 930, u); my = 540 + 40 * math.sin(u * 9)
    d.circ(mx, my, 80, outline=A(GOLD, 1), w=12); d.line([(mx + 56, my + 56), (mx + 120, my + 120)], A(GOLD, 1), 20)
    n = int(lerp(0, 459, ease(pr(t, t0 + 0.4, t0 + 2.4))))
    d.text(540, 930, "%d只" % n, 130, A(GOLD, 1), k=1)
NODES = None
def nodes():
    global NODES
    if NODES: return NODES
    rv = random.Random(13); cs = []
    for c in range(13):
        a = c / 13 * 2 * math.pi; r = 270 if c % 2 else 180
        cs.append((540 + math.cos(a) * r * 1.1, 720 + math.sin(a) * r))
    ns = []
    for i in range(69):
        c = i % 13; cx, cy = cs[c]
        ns.append((cx + rv.uniform(-50, 50), cy + rv.uniform(-45, 45), c))
    NODES = (cs, ns); return NODES
def s_events(t, d):
    bg(d, t, "plum")
    t0 = T["events"]; cs, ns = nodes(); rv = random.Random(7)
    pairs = []
    for i in range(167):
        a = rv.randrange(69); c = ns[a][2]
        same = [j for j in range(69) if ns[j][2] == c and j != a]
        b = rv.choice(same) if rv.random() < 0.8 and same else rv.randrange(69)
        pairs.append((a, b))
    shown = int(167 * ease(pr(t, t0 + 0.6, t0 + 2.4)))
    for a, b in pairs[:shown]:
        d.line([ns[a][:2], ns[b][:2]], A(PINK, 0.35), 3)
    for i, (x, y, c) in enumerate(ns):
        k = popk(t, t0 + i * 0.008)
        if k > 0: d.circ(x, y, 11 * min(1, k), fill=A(JAG, 1))
    d.text(320, 330, "%d只" % min(69, int(69 * pr(t, t0, t0 + 0.6))), 70, A(JAG, 1), k=1)
    d.text(760, 330, "%d次" % shown, 70, A(PINK, 1), k=1)
def s_pie(t, d):
    bg(d, t, "navy")
    t0 = T["pie"]; cx, cy, R0 = 540, 720, 300
    segs = [(24.5, MEAN, "打架 24.5%"), (36.5, (150, 156, 170), "中立 36.5%"), (38.9, PINK, "友好 38.9%")]
    grow = ease(pr(t, t0 + 0.1, t0 + 1.2)); a0 = -90
    for i, (p, c, lab) in enumerate(segs):
        sweep = 360 * p / 99.9 * grow
        off = 40 * popk(t, t0 + 1.3) if i == 0 else 0
        mid = math.radians(a0 + sweep / 2)
        ox, oy = cx + math.cos(mid) * off, cy + math.sin(mid) * off
        if sweep > 0.5:
            pts = [(ox, oy)] + [(ox + math.cos(math.radians(a0 + sweep * j / 40)) * R0, oy + math.sin(math.radians(a0 + sweep * j / 40)) * R0) for j in range(41)]
            d.poly(pts, A(c, 1))
        if grow >= 1:
            lx, ly = cx + math.cos(mid) * (R0 + 120), cy + math.sin(mid) * (R0 + 60)
            tag(d, cl(lx, 240, 840), ly, lab, c, ap(t, t0 + 1.2 + i * 0.15, 0.2), 40 if i else 52)
        a0 += 360 * p / 99.9 * grow
def s_friendly(t, d):
    bg(d, t, "grass")
    t0 = T["friendly"]
    acts = [("一起吃", 0), ("一起睡", 1), ("一起打猎", 2), ("互相舔毛", 3)]
    for i, (lab, kind) in enumerate(acts):
        x = 300 + (i % 2) * 480; y = 480 + (i // 2) * 420
        k = popk(t, t0 + i * 0.4)
        if k <= 0: continue
        sc = min(1, k)
        d.rect(x - 220 * sc, y - 180 * sc, x + 220 * sc, y + 180 * sc, fill=A(WHITE, 0.18), r=30)
        if kind == 0:
            d.ell(x, y + 70, 70, 26, A((180, 200, 220), 1)); d.poly([(x + 60, y + 70), (x + 100, y + 45), (x + 100, y + 95)], A((180, 200, 220), 1))
            bigcat(d, x - 110, y + 60, 0.42 * sc, t, mood="happy", bob=0.2); bigcat(d, x + 120, y + 60, 0.42 * sc, t, mood="happy", flip=-1, bob=0.2)
        elif kind == 1:
            bigcat(d, x - 70, y + 70, 0.45 * sc, t, pose="belly", mood="happy"); bigcat(d, x + 80, y + 70, 0.45 * sc, t, pose="belly", mood="happy", flip=-1)
            d.text(x + 120, y - 90 - 10 * math.sin(t * 3), "Zz", 50, A(WHITE, 0.9), k=1)
        elif kind == 2:
            ph = (t * 1.2) % 1
            d.ell(x + 120 + 30 * ph, y + 80, 50, 32, A((150, 110, 80), 1))
            bigcat(d, x - 30 + 30 * ph, y + 70, 0.4 * sc, t * 2, mood="neutral"); bigcat(d, x - 140 + 30 * ph, y + 90, 0.36 * sc, t * 2 + 1, mood="neutral")
        else:
            bigcat(d, x - 70, y + 60, 0.45 * sc, t, mood="happy", lick=0.5 + 0.5 * math.sin(t * 9), bob=0.2); bigcat(d, x + 110, y + 60, 0.45 * sc, t, mood="happy", flip=-1, bob=0.2)
        tag(d, x, y - 140 * sc, lab, GOLD, min(1, k), 40)
def s_kin(t, d):
    bg(d, t, "gold")
    t0 = T["kin"]
    # family tree: mom on top, two brothers below linked
    bigcat(d, 540, 520, 0.42, t, mood="happy", bob=0.3)
    for i, x in enumerate((330, 750)):
        k = popk(t, t0 + 0.2 + i * 0.15)
        if k <= 0: continue
        d.line([(540, 590), (540, 650), (x, 650), (x, 760)], A(WHITE, 0.8), 6)
        bigcat(d, x, 840, 0.42 * min(1, k), t, mood="happy", flip=1 if i == 0 else -1, bob=0.3)
        tag(d, x, 950, "兄弟", MINT, min(1, k), 34)
    hearts(d, t, t0 + 0.6, 540, 840, 4)
    # 68% bar
    u = ease(pr(t, t0 + 0.8, t0 + 2.0))
    d.rect(200, 1080, 880, 1150, fill=A((0, 0, 0), 0.25), r=35)
    d.rect(200, 1080, 200 + 680 * 0.68 * u, 1150, fill=A(PINK, 1), r=35)
    d.text(200 + 680 * 0.68 * u - 70, 1115, "%d%%" % int(68 * u), 46, A(NAVYT, 1), k=1) if u > 0.2 else None
    ptag(d, t, t0 + 2.0, 540, 360, "多是有亲缘的雄性", WHITE, 40)
def s_stranger(t, d):
    bg(d, t, "red")
    t0 = T["stranger"]
    lun = max(0, math.sin((t - t0) * 6)) * 30
    bigcat(d, 280 + lun, GY, 0.8, t, mood="hiss", flat=1, bob=0.2)
    bigcat(d, 800 - lun, GY, 0.8, t, mood="hiss", flat=1, flip=-1, bob=0.2)
    for x in (300, 780):
        k = popk(t, t0 + 0.2 + (x > 500) * 0.2)
        if k > 0: d.text(x + 60, 640, "?", int(140 * min(1, k)), A(WHITE, 1), k=1)
    if lun > 26: sparks(d, 540, GY - 80, t, t - 0.05, 10, 500, WHITE, 0.9, int(t * 10), 0.3)
    ptag(d, t, t0 + 0.6, 540, 470, "关系不明", GOLD, 52)
def s_meme(t, d):
    t0 = T["meme"]
    bg(d, t, "plum", False)
    d.rect(540, 0, 1080, 1920, fill=A((150, 40, 60), 1)); d.rect(532, 200, 548, 1250, fill=A(WHITE, 0.9))
    bigcat(d, 270, 980, 0.62, t, pose="belly", mood="happy")
    tag(d, 270, 560, "哈基米", PINK, ap(t, t0 + 0.1, 0.2), 64)
    hearts(d, t, t0 + 0.3, 270, 860, 4)
    k = ap(t, t0 + 1.0, 0.2)
    if k > 0:
        bigcat(d, 820, 980, 0.62, t, mood="hiss", flat=1, flip=-1, bob=0.2)
        bubble_txt(d, t, t0 + 1.2, 800, 600, "老吴！", MEAN, 72, -1)
    tag(d, 270, 1140, "亲戚", MINT, 1, 40); tag(d, 810, 1140, "陌生豹", WHITE, k, 40)
    tag(d, 900, 250, "玩梗", WHITE, 0.6, 26)
def s_net(t, d):
    bg(d, t, "navy")
    t0 = T["net"]; cs, ns = nodes()
    for c, (cx, cy) in enumerate(cs):
        k = popk(t, t0 + c * 0.06)
        if k > 0: d.circ(cx, cy, 78 * min(1, k), fill=A(MINT, 0.18)); d.circ(cx, cy, 78 * min(1, k), outline=A(MINT, 0.6), w=4)
    for x, y, c in ns: d.circ(x, y, 9, fill=A(JAG, 1))
    lk = ease(pr(t, t0 + 1.2, t0 + 2.4))
    for c in range(13):
        a, b = cs[c], cs[(c + 1) % 13]
        d.line([a, (lerp(a[0], b[0], lk), lerp(a[1], b[1], lk))], A(GOLD, 0.9), 8)
        if lk > 0.05:
            glow(d, a[0], a[1], 40, GOLD, 0.6); d.circ(a[0], a[1], 16, fill=A(GOLD, 1))
    if t > t0 + 0.8: d.text(540, 720, "13", int(120 * popk(t, t0 + 0.8)), A(MINT, 1), k=1)
    ptag(d, t, t0 + 2.4, 540, 330, "社牛：连接各圈子", GOLD, 44)
def s_cons(t, d):
    bg(d, t, "navy")
    t0 = T["cons"]; cs, ns = nodes()
    gone = 4; br = ease(pr(t, t0 + 0.6, t0 + 1.6))
    for c, (cx, cy) in enumerate(cs):
        dx = (cx - 540) * 0.25 * br * (1 if c in (3, 4, 5) else 0.4)
        d.circ(cx + dx, cy, 78, fill=A(MINT, 0.18))
    for x, y, c in ns:
        dx = (cs[c][0] - 540) * 0.25 * br * (1 if c in (3, 4, 5) else 0.4)
        d.circ(x + dx, y, 9, fill=A(JAG, 1))
    for c in range(13):
        if c in (3, 4): continue
        a, b = cs[c], cs[(c + 1) % 13]
        dxa = (a[0] - 540) * 0.25 * br * (1 if c in (3, 4, 5) else 0.4); dxb = (b[0] - 540) * 0.25 * br * (1 if (c + 1) % 13 in (3, 4, 5) else 0.4)
        d.line([(a[0] + dxa, a[1]), (b[0] + dxb, b[1])], A(GOLD, 0.9 * (1 - 0.6 * br)), 8)
        d.circ(a[0] + dxa, a[1], 16, fill=A(GOLD, 1))
    cx, cy = cs[gone]
    if t < t0 + 0.5:
        glow(d, cx, cy, 60, GOLD, 0.9); d.circ(cx, cy, 22, fill=A(GOLD, 1))
    xmark(d, cx, cy - 90, 40, MEAN, 1, popk(t, t0 + 0.4)); poof(d, t, t0 + 0.45, cx, cy, 100)
    for c in (3, 4):
        a, b = cs[c], cs[(c + 1) % 13]
        if br > 0: d.line([(a[0], a[1]), (lerp(a[0], b[0], 0.3), lerp(a[1], b[1], 0.3) + 60 * br)], A(GOLD, 0.6 * (1 - br)), 6)
    ptag(d, t, t0 + 1.6, 540, 330, "关系网被扯散", MEAN, 46)
def s_tiger(t, d):
    bg(d, t, "grass"); ground(d)
    t0 = T["tiger"]
    bigcat(d, 260, GY + 40, 0.75, t, sp="tig", pose="belly", mood="happy")
    d.text(330, GY - 150 - 10 * math.sin(t * 3), "Zz", 50, A(WHITE, 0.8), k=1)
    for i, x in enumerate((540, 670)):
        bigcat(d, x, GY + 60, 0.75, t + i, sp="tig", cub=True, mood="happy", flip=1 if i == 0 else -1, bob=0.6)
    dx = lerp(1250, 900, ease(pr(t, t0, t0 + 1.0)))
    bob = 30 * max(0, math.sin((t - t0 - 1.0) * 8)) * (t > t0 + 1.0)
    bigcat(d, dx, GY - bob * 0.3, 0.78, t, sp="tig", mood="happy", flip=-1, bob=0.3, look_up=-bob / 30)
    if t > t0 + 1.0: tag(d, 760, 520, "点头打招呼", GOLD, ap(t, t0 + 1.1, 0.2), 40)
    tag(d, 260, 760, "虎妈", PINK, 1, 36); tag(d, dx - 40, 680, "虎爸", TIG, ap(t, t0 + 0.6, 0.2), 36)
    tag(d, 820, 250, "纪录片画面 · 示意", WHITE, 0.6, 26)
def s_tiger2(t, d):
    bg(d, t, "jungle"); ground(d)
    t0 = T["tiger2"]
    lk = 0.5 + 0.5 * math.sin(t * 9)
    bigcat(d, 400, GY, 0.95, t, sp="tig", mood="happy", lick=lk, bob=0.3)
    bigcat(d, 690, GY + 60, 0.95, t, sp="tig", cub=True, mood="happy", flip=-1, bob=0.4)
    bigcat(d, 860, GY + 60, 0.95, t + 1, sp="tig", cub=True, mood="happy", flip=-1, bob=0.4)
    ptag(d, t, t0 + 0.3, 760, 760, "别家的崽", GOLD, 40)
    hearts(d, t, t0 + 0.6, 650, 900, 4)
    tag(d, 820, 250, "纪录片画面 · 示意", WHITE, 0.6, 26)
def s_caution(t, d):
    bg(d, t, "navy")
    t0 = T["caution"]
    tilt = 0.18 * ease(pr(t, t0 + 1.2, t0 + 2.0))
    cx, cy = 540, 560
    d.rect(530, cy, 550, 1060, fill=A(WHITE, 0.8)); d.poly([(470, 1060), (610, 1060), (540, 990)], A(WHITE, 0.8))
    lx, ly = cx - 300 * math.cos(tilt), cy - 300 * math.sin(tilt)
    rx, ry = cx + 300 * math.cos(tilt), cy + 300 * math.sin(tilt)
    d.line([(lx, ly), (rx, ry)], A(WHITE, 1), 12)
    for (px, py, side) in ((lx, ly, 0), (rx, ry, 1)):
        d.line([(px, py), (px - 90, py + 200)], A(WHITE, 0.6), 4); d.line([(px, py), (px + 90, py + 200)], A(WHITE, 0.6), 4)
        d.ell(px, py + 205, 120, 24, A(WHITE, 0.9))
        if side == 0:
            bigcat(d, px - 10, py + 150, 0.32, t, sp="tig", mood="happy", bob=0)
            tag(d, px, py + 290, "纪录片个例", TIG, ap(t, t0 + 0.2, 0.2), 38)
        else:
            for j in range(4):
                d.rect(px - 90 + j * 48, py + 190 - (j + 2) * 22, px - 58 + j * 48, py + 190, fill=A(JAG, 1), r=6)
            tag(d, px, py + 290, "13年系统数据", JAG, ap(t, t0 + 0.6, 0.2), 38)
def s_card(t, d):
    bg(d, t, "plum", False)
    for i in range(12): d.circ(540, 820, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    bigcat(d, cx_ - 20, cy_ - 150, 0.45, t, pose="belly", mood="happy", a=a_)
    d.text(cx_, cy_ + 40, "美洲豹不是纯独行侠", 48, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("打架只占24.5%", "友好互动近68%在亲戚间", "少数“社牛”连起13个圈子")):
        kk = ap(t, at("card", 1.0 + i * 1.4), 0.25)
        if kk > 0: d.text(cx_, cy_ + 150 + i * 78, s_, 42, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    bg(d, t, "river"); river(d, t)
    t0 = T["end"]
    bigcat(d, 360, GY + 20, 0.85, t, pose="belly", mood="happy")
    bigcat(d, 830, GY, 0.6, t, mood="hiss", flat=1, flip=-1, bob=0.3)
    bubble_txt(d, t, t0 + 0.8, 800, 720, "老吴", MEAN, 54, -1)
    hearts(d, t, t0 + 0.3, 360, 900, 5)
    ra = ap(t, t0 + 2.2, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 285, "Boron 等 2026 · Animal Behaviour", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 325, "潘塔纳尔北部 13 年直接观察", 25, A(WHITE, 0.85 * ra), k=1)
        d.text(540, 365, "老虎：PBS《Tiger Island》2026", 25, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "老吴", "q": "开打", "reveal": "翻肚皮", "solo": "独行侠", "team": "13年", "ids": "459只", "events": "167次社交", "pie": "24.5%",
      "friendly": "一起吃", "kin": "68%", "stranger": "关系不明", "meme": "哈基米", "net": "社牛", "cons": "整张网", "tiger": "虎爸", "tiger2": "别家的崽",
      "caution": "个例", "end": "翻肚皮"}
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/jg_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/jg_sheet.png")
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
