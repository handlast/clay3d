import math, random, sys, subprocess
from PIL import Image, ImageDraw, ImageFont

OW, OH, FPS = 1920, 1080, 30
S = 1.5
W, H = int(OW * S), int(OH * S)
BAR = 10 / 3; BEAT = BAR / 4; NB = 45; DUR = NB * BAR
CJK = "/workspace/work/nobel/NotoSerifSC.otf"
LAT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
LATR = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
PAPER = (244, 239, 226); INK = (48, 54, 50); INK2 = (120, 118, 108)
GOLD = (200, 146, 40); GOLDL = (226, 182, 86)
TALLG = (122, 160, 86); SHORTG = (62, 120, 82); EAR = (214, 172, 78)
SICK = (170, 132, 82); RED = (196, 72, 52); SKY = (150, 170, 178)
fc = {}
def F(size, lat=0):
    k = (size, lat)
    if k not in fc: fc[k] = ImageFont.truetype([CJK, LAT, LATR][lat], int(size * S))
    return fc[k]
def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return x * x * (3 - 2 * x)
def pr(t, a, b): return cl((t - a) / (b - a))
def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k): return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))
def A(c, a): return c[:3] + (int(255 * cl(a)),)
def bt(b, beat=0): return b * BAR + beat * BEAT
def P(x): return x * S

class D:
    def __init__(s, img): s.d = ImageDraw.Draw(img, "RGBA")
    def line(s, pts, fill, w): s.d.line([(P(x), P(y)) for x, y in pts], fill=fill, width=max(1, int(P(w))), joint="curve")
    def poly(s, pts, fill): s.d.polygon([(P(x), P(y)) for x, y in pts], fill=fill)
    def circ(s, x, y, r, fill=None, outline=None, w=1): s.d.ellipse((P(x - r), P(y - r), P(x + r), P(y + r)), fill=fill, outline=outline, width=max(1, int(P(w))))
    def rect(s, x0, y0, x1, y1, fill=None, outline=None, w=1, r=0):
        s.d.rounded_rectangle((P(x0), P(y0), P(x1), P(y1)), radius=P(r), fill=fill, outline=outline, width=max(1, int(P(w))) if outline else 0)
    def text(s, x, y, t, size, fill, anchor="mm", lat=0): s.d.text((P(x), P(y)), t, font=F(size, lat), fill=fill, anchor=anchor)

def qpts(p0, p1, p2, n=10):
    return [((1 - k) ** 2 * p0[0] + 2 * (1 - k) * k * p1[0] + k * k * p2[0], (1 - k) ** 2 * p0[1] + 2 * (1 - k) * k * p1[1] + k * k * p2[1]) for k in [i / n for i in range(n + 1)]]

def plant(d, x, by, h, tall, t, sick=0.0, a=1.0, sway=1.0, seed=0, spots=None):
    base = TALLG if tall else SHORTG
    col = A(mix(base, SICK, sick), a)
    sw = math.sin(t * 1.3 + x * 0.013 + seed) * h * 0.035 * sway
    top = (x + sw, by - h)
    stalk = qpts((x, by), (x + sw * 0.2, by - h * 0.55), top, 8)
    w = 5 if tall else 6
    d.line(stalk, col, w * h / 400 + 1.5)
    lf = [(0.18, -1, 0.55), (0.32, 1, 0.6), (0.48, -1, 0.5), (0.62, 1, 0.45)]
    for i, (fy, sd, ln) in enumerate(lf):
        y0 = by - h * fy; x0 = x + sw * fy * 0.5
        tipx = x0 + sd * h * ln * 0.55 + sw * 1.4; tipy = y0 - h * ln * 0.55
        c = qpts((x0, y0), (x0 + sd * h * 0.08, y0 - h * ln * 0.5), (tipx, tipy), 8)
        wid = h * 0.028
        up = [(px - sd * wid * (1 - j / 8) * 0.5, py - wid * (1 - j / 8)) for j, (px, py) in enumerate(c)]
        dn = [(px + sd * wid * (1 - j / 8) * 0.5, py + wid * (1 - j / 8) * 0.3) for j, (px, py) in enumerate(c)]
        d.poly(up + dn[::-1], col)
        if sick > 0.05:
            r = random.Random(seed * 31 + i)
            for k in range(int(1 + sick * 3)):
                u = r.uniform(0.2, 0.8); px, py = c[int(u * 8)]
                d.circ(px, py, max(1.5, wid * 0.45), fill=A(RED, a * min(1, sick * 1.6)))
    # ear
    ec = A(mix(EAR if tall else mix(EAR, SHORTG, 0.35), SICK, sick * 0.7), a)
    droop = h * (0.16 if tall else 0.11)
    e = qpts(top, (top[0] + droop * 0.9, top[1] - droop * 0.4), (top[0] + droop * 1.2, top[1] + droop * 0.6), 7)
    d.line(e, ec, 2.2)
    for j, (px, py) in enumerate(e[1:]):
        r = h * 0.016 + 1.2
        d.circ(px - r * 0.8, py, r, fill=ec); d.circ(px + r * 0.6, py - r * 0.3, r * 0.9, fill=ec)
    return top

def spore(d, x, y, a=1.0, r=7):
    d.circ(x, y, r * 2.2, fill=A(RED, 0.15 * a)); d.circ(x, y, r, fill=A(RED, a))

def ground(d, x0, x1, y, a=1.0):
    d.rect(x0, y, x1, y + 14, fill=A((150, 132, 98), 0.55 * a), r=6)
    d.line([(x0, y), (x1, y)], A((120, 104, 76), a), 2)

# ---------------- sections ----------------
def hook(t, d):
    a0 = ease(pr(t, 0.2, 1.4))
    GY = 760
    for side, (x0, x1) in enumerate([(120, 900), (1020, 1800)]):
        ground(d, x0, x1, GY, a0)
    # left: all tall glutinous, disease spreads from centre one beat per plant
    xs = [170 + i * 85 for i in range(9)]
    for i, x in enumerate(xs):
        ti = bt(2) + abs(i - 4) * BEAT
        sk = ease(pr(t, ti, ti + 0.6))
        plant(d, x, GY, 330, True, t, sick=sk, a=a0, seed=i)
        if t >= ti - 0.35 and t < ti + 0.35 and t > bt(2) - 0.4:
            k = pr(t, ti - 0.35, ti)
            spore(d, x + 30, GY - 330 * 0.6 - 60 * (1 - k), 1 - pr(t, ti, ti + 0.35))
    la = ease(pr(t, bt(1), bt(1) + 0.6))
    d.text(510, 300, "只种一种", 40, A(INK, la * a0))
    # right: mixed T S S
    pat = [1, 0, 0, 1, 0, 0, 1, 0, 0]
    xr = [1070 + i * 85 for i in range(9)]
    ra = ease(pr(t, bt(3), bt(3) + 0.6))
    tland = bt(4)
    for i, x in enumerate(xr):
        tall = pat[i] == 1
        sk = 0.45 * ease(pr(t, tland, tland + 0.5)) if i == 3 else 0
        plant(d, x, GY, 330 if tall else 225, tall, t, sick=sk, a=a0, seed=i + 20)
    d.text(1410, 300, "混着种", 40, A(INK, ra * a0))
    # spore drops on plant 3 then tries neighbours and fails
    if bt(4) - 0.8 < t < bt(6):
        k = pr(t, tland - 0.8, tland)
        if t < tland:
            spore(d, xr[3] + 30, GY - 200 - 260 * (1 - eio(k)))
        else:
            for j, nb in enumerate([2, 4]):
                tj = tland + BEAT * (1 + j)
                if t > tj - 0.5:
                    kk = pr(t, tj - 0.5, tj)
                    sx = lerp(xr[3], xr[nb], eio(kk)); sy = GY - 200 - math.sin(kk * math.pi) * 60
                    fa = 1 - pr(t, tj, tj + 0.5)
                    if fa > 0:
                        spore(d, sx, sy, fa, 6)
                        if t > tj: d.text(xr[nb], GY - 290, "×", 40, A(INK2, fa), lat=1)
    if t > bt(4, 3):
        g = ease(pr(t, bt(4, 3), bt(4, 3) + 0.6)) * (1 - pr(t, bt(6), bt(6) + 0.6))
        d.circ(xr[3] + 10, GY - 200, 150, outline=A(GOLD, g), w=4)
    q = ease(pr(t, bt(6), bt(6) + 0.6))
    d.text(1410, 220, "?", 90, A(GOLD, q), lat=1)

def title(t, d):
    t0 = bt(7); a = ease(pr(t, t0, t0 + 0.8)) * (1 - pr(t, bt(9) - 0.5, bt(9)))
    k = ease(pr(t, t0, t0 + 1.6))
    # rice ear line drawing
    e = qpts((960, 470), (1010, 260 - 30 * k), (1120, 300), 9)
    d.line(e[: 1 + int(9 * k)], A(GOLD, a), 3)
    for j, (px, py) in enumerate(e[1: 1 + int(9 * k)]):
        d.circ(px - 9, py + 6, 9, fill=A(GOLDL, a)); d.circ(px + 7, py - 6, 8, fill=A(GOLDL, a))
    d.line([(960, 470), (955, 560)], A(GOLD, a), 3)
    d.text(960, 650, "混  种", 150, A(INK, a))
    b = ease(pr(t, t0 + 0.9, t0 + 1.8))
    d.text(960, 770, "D I V E R S I T A S", 30, A(GOLD, b * a), lat=2)
    d.text(960, 840, "一位院士，如何让庄稼不靠农药少生病", 36, A(INK2, b * a))

def mono(t, d):
    t0 = bt(9)
    a = ease(pr(t, t0, t0 + 0.8))
    rows = [(640, 150, 0.45), (740, 210, 0.7), (880, 300, 1.0)]
    wave_t = bt(10, 2)
    for ri, (gy, h, al) in enumerate(rows):
        n = 26 if ri < 2 else 18
        sp = 1920 / (n - 1)
        for i in range(n):
            x = i * sp + (sp / 2 if ri == 1 else 0) - 20
            ts = wave_t + (x / 1920) * (BAR * 1.2)
            sk = ease(pr(t, ts, ts + 0.7)) * (1 - 0.6 * ease(pr(t, bt(12, 1) + x / 1920, bt(12, 2) + x / 1920)))
            plant(d, x, gy, h, True, t, sick=sk, a=a * al, seed=i + ri * 50)
    # spores raining in bar 10
    r = random.Random(4)
    for i in range(26):
        ts = bt(10) + r.uniform(0, BAR * 0.9); x = r.uniform(80, 1840)
        k = pr(t, ts, ts + 1.0)
        if 0 < k < 1: spore(d, x, lerp(120, 560, k), 1 - k * 0.6, 6)
    # sprayer passes in bar 12, counter per beat
    if t > bt(12) - 0.3:
        k = pr(t, bt(12), bt(13) - 0.4)
        fa = 1 - pr(t, bt(13) - 0.6, bt(13))
        for i in range(60):
            rr = random.Random(i)
            mx = (rr.uniform(0, 1) + k * 1.4) * 1920 - 600
            my = rr.uniform(330, 600)
            if 0 < mx < 1920: d.circ(mx, my, rr.uniform(3, 7), fill=A(SKY, 0.45 * fa))
        n = 1 + int(cl((t - bt(12)) / BEAT, 0, 3.99)) if t >= bt(12) else 0
        if n: d.text(1660, 170, f"农药  第 {n} 遍", 40, A(INK, fa))

def oldway(t, d):
    t0 = bt(13); a = ease(pr(t, t0, t0 + 0.8))
    GY = 840
    xs = [130 + i * 105 for i in range(17)]
    for i, x in enumerate(xs):
        tall = i % 4 == 2
        if tall:
            g = ease(pr(t, bt(14) + (i // 4) * BEAT, bt(14) + (i // 4) * BEAT + 0.7))
            h = lerp(250, 400, g)
            if g <= 0: continue
            plant(d, x, GY, h, True, t, a=a * g, seed=i)
        else:
            plant(d, x, GY, 250, False, t, a=a, seed=i)
    ground(d, 60, 1860, GY, a)
    ka = ease(pr(t, bt(14) + 1, bt(14) + 1.6)) * (1 - pr(t, bt(15), bt(15) + .4))
    d.text(1590, 330, "糯稻（高，易生病）", 32, A(INK, ka * a))
    q = ease(pr(t, bt(15), bt(15) + 0.5)) * (1 - pr(t, bt(16), bt(16) + .4))
    d.text(960, 300, "?", 140, A(GOLD, q), lat=1)
    # timeline: 20 years
    if t > bt(16) - 0.2:
        k = eio(pr(t, bt(16), bt(17) - 0.3)); fa = 1 - pr(t, bt(18) - 0.7, bt(18))
        x0, x1, y = 360, 1560, 260
        d.line([(x0, y), (lerp(x0, x1, k), y)], A(GOLD, fa), 4)
        n = int(k * 20 + 0.001)
        for j in range(n + 1): d.line([(lerp(x0, x1, j / 20), y - 12), (lerp(x0, x1, j / 20), y + 12)], A(GOLD, fa), 3)
        d.text(lerp(x0, x1, k), y - 60, f"{n} 年", 44, A(INK, fa))

FIELD = [(100 + i * 125, i % 4 == 0) for i in range(15)]
def mechanism(t, d):
    t0 = bt(18); a = ease(pr(t, t0, t0 + 0.8))
    GY = 860; TH, SH = 470, 320
    if bt(21) < t < bt(22):
        band = ease(pr(t, bt(21), bt(21) + 0.6)) * (1 - pr(t, bt(22) - 0.6, bt(22)))
        d.rect(160, GY - SH - 20, 1880, GY - SH * 0.45, fill=A(GOLDL, 0.35 * band), r=30)
    tops = {}
    for i, (x, tall) in enumerate(FIELD):
        sk = 0
        tops[i] = plant(d, x, GY, TH if tall else SH, tall, t, a=a, seed=i, sway=1.0 + (1.6 if bt(23) < t < bt(25) else 0))
    ground(d, 40, 1880, GY, a)
    la = ease(pr(t, t0 + 0.6, t0 + 1.2)) * (1 - pr(t, bt(20) - 0.4, bt(20)))
    d.text(100 + 18, GY - TH - 90, "糯稻 · 易感病", 28, A(INK, la), anchor="lm")
    d.text(100 + 125 * 2, GY - SH - 120, "杂交稻 · 抗病", 28, A(INK, la))
    def head(txt, b0, b1):
        ha = ease(pr(t, bt(b0), bt(b0) + 0.5)) * (1 - pr(t, bt(b1) - 0.5, bt(b1)))
        if ha > 0: d.text(110, 150, txt, 46, A(GOLD, ha), anchor="lm")
    head("① 稀释", 18, 20); head("② 屏障", 20, 22); head("③ 小气候", 22, 25)
    # 1 dilution: spores land on beats
    r = random.Random(9)
    for k in range(8):
        ts = bt(18) + k * BEAT; i = r.choice([1, 2, 3, 5, 6, 7, 9, 10, 11, 13])
        if k in (3, 6): i = r.choice([0, 4, 8, 12])
        x, tall = FIELD[i]; ty = GY - (TH if tall else SH) * 0.62
        u = pr(t, ts - 0.6, ts)
        if 0 < u and t < bt(20) - 0.2:
            fa = 1 - pr(t, ts + 0.5, ts + 1.1)
            if u < 1: spore(d, x + 25, lerp(120, ty, eio(u)))
            elif fa > 0:
                spore(d, x + 25, ty, fa * (0.6 if not tall else 1))
                if not tall: d.text(x + 25, ty - 45, "×", 36, A(INK2, fa), lat=1)
    # 2 barrier: wind carries spores at short canopy level, they stop at the first short wall
    if bt(20) - 0.2 < t < bt(22):
        fa = 1 - pr(t, bt(22) - 0.6, bt(22))
        wy = GY - SH * 0.75
        for k in range(10):
            ts = bt(20) + k * BEAT * 0.75
            u = pr(t, ts, ts + 1.4)
            if 0 < u < 1:
                stopx = FIELD[1][0] - 20
                x = lerp(-40, stopx, min(1, u * 1.4)); y = wy + (k % 3 - 1) * 40 + math.sin(u * 9) * 6
                spore(d, x, y, fa * (1 - pr(u, 0.72, 1.0)), 6)
        for k in range(3):
            ax = ((t - bt(20)) * 260 + k * 160) % 520 - 60
            d.line([(ax, wy - 120 + k * 50), (ax + 90, wy - 120 + k * 50)], A(SKY, 0.8 * fa), 3)
    # 3 microclimate
    if bt(22) - 0.2 < t < bt(25):
        fa = 1 - pr(t, bt(25) - 0.6, bt(25))
        ru = ease(pr(t, bt(22), bt(22) + 0.8)) * fa
        rx = FIELD[8][0] - 70
        y1, y2 = GY - SH, GY - TH
        d.line([(rx, y1), (rx, lerp(y1, y2, ru))], A(GOLD, ru), 4)
        d.line([(rx - 14, y1), (rx + 14, y1)], A(GOLD, ru), 4); d.line([(rx - 14, y2), (rx + 14, y2)], A(GOLD, ru * ru), 4)
        d.text(rx - 30, (y1 + y2) / 2, "35～40 cm", 34, A(GOLD, ru), anchor="rm")
        # wind lines over tall canopy
        wa = ease(pr(t, bt(23), bt(23) + 0.5)) * fa
        for k in range(6):
            ax = ((t - bt(23)) * 520 + k * 330) % 2100 - 120
            yy = GY - TH - 40 + (k % 3) * 45
            d.line(qpts((ax, yy), (ax + 70, yy - 18), (ax + 150, yy), 6), A(SKY, wa), 3)
        # dew drops on tall leaves shrink
        dr = 1 - ease(pr(t, bt(23, 1), bt(24)))
        for i in (0, 4, 8, 12):
            x, _ = FIELD[i]
            for j, (dx, dy) in enumerate([(-40, -0.32), (45, -0.47), (-30, -0.6)]):
                rr = 9 * dr * ru
                if rr > 0.6: d.circ(x + dx, GY - TH * -dy * -1 if False else GY + TH * dy, rr, fill=A((150, 190, 205), 0.85 * fa))
        # spore tries to sprout and withers
        sa = ease(pr(t, bt(24), bt(24) + 0.3)) * fa
        if sa > 0:
            x, _ = FIELD[8]; sy = GY - TH * 0.47
            spore(d, x + 45, sy, sa, 7)
            g = ease(pr(t, bt(24, 1), bt(24, 2))) ; wl = 1 - ease(pr(t, bt(24, 2), bt(24, 3)))
            d.line([(x + 45, sy), (x + 45 + 30 * g, sy - 26 * g * wl)], A(mix(RED, INK2, 1 - wl), sa), 3)
    # summary
    if t > bt(25) - 0.2:
        fa = 1 - pr(t, bt(28) - 0.6, bt(28))
        sa = ease(pr(t, bt(25), bt(25) + 0.6)) * fa
        d.text(960, 150, "稀释 · 屏障 · 小气候", 46, A(GOLD, sa))
        fr = ease(pr(t, bt(26), bt(26) + 0.9)) * fa
        d.rect(60, 240, 1860, 890, outline=A(GOLD, fr), w=4, r=30)

def trial(t, d):
    t0 = bt(28); fa = 1 - pr(t, bt(36) - 0.5, bt(36))
    # townships
    if t < bt(30):
        ga = 1 - pr(t, bt(30) - 0.5, bt(30))
        for i in range(10):
            x = 560 + (i % 5) * 200; y = 360 + (i // 5) * 220
            on = bt(28) + i * BEAT * 0.6 if i < 5 else bt(29) + (i - 5) * BEAT * 0.6
            k = ease(pr(t, on, on + 0.4))
            d.circ(x, y, 70, outline=A(INK2, 0.6 * ga * ease(pr(t, t0, t0 + 0.6))), w=3)
            if k > 0:
                d.circ(x, y, 70 * (0.6 + 0.4 * k), fill=A(GOLDL, 0.85 * k * ga))
                d.line(qpts((x - 10, y + 40), (x - 5, y - 10), (x + 25, y - 35), 6), A(INK, k * ga), 4)
                d.circ(x + 25, y - 35, 9, fill=A(INK, k * ga)); d.circ(x + 8, y - 22, 8, fill=A(INK, k * ga))
        l1 = ease(pr(t, bt(28, 2), bt(28, 3))) * ga; l2 = ease(pr(t, bt(29, 2), bt(29, 3))) * ga
        d.text(1600, 360, "1998", 40, A(INK2, l1), lat=1); d.text(1600, 410, "812 公顷", 40, A(INK, l1))
        d.text(1600, 580, "1999", 40, A(INK2, l2), lat=1); d.text(1600, 630, "3342 公顷", 40, A(INK, l2))
    # bar chart
    if bt(30) - 0.2 < t < bt(32):
        ga = ease(pr(t, bt(30), bt(30) + 0.5)) * (1 - pr(t, bt(32) - 0.5, bt(32)))
        x0 = 620; full = 1100
        d.text(x0 - 30, 420, "单种糯稻", 40, A(INK, ga), anchor="rm")
        d.text(x0 - 30, 600, "混种糯稻", 40, A(INK, ga), anchor="rm")
        k1 = ease(pr(t, bt(30, 1), bt(31) - 0.3)); k2 = ease(pr(t, bt(31), bt(31, 1)))
        d.rect(x0, 385, x0 + full * k1 + 4, 455, fill=A(RED, ga * 0.85), r=10)
        d.text(x0 + full * k1 + 30, 420, f"{round(20 * k1)}%", 52, A(RED, ga), anchor="lm", lat=1)
        d.rect(x0, 565, x0 + full * 0.05 * k2 + 4, 635, fill=A(GOLD, ga), r=10)
        if k2 > 0: d.text(x0 + full * 0.05 * k2 + 30, 600, "1%", 52, A(GOLD, ga * k2), anchor="lm", lat=1)
        d.text(x0, 300, "稻瘟病吃掉的收成", 32, A(INK2, ga), anchor="lm")
    # big numbers
    if bt(32) - 0.2 < t < bt(34):
        ga = ease(pr(t, bt(32), bt(32) + 0.4)) * (1 - pr(t, bt(34) - 0.4, bt(34)))
        k1 = ease(pr(t, bt(32), bt(32, 2))); k2 = ease(pr(t, bt(32, 1), bt(32, 3)))
        dim = 1 - 0.35 * ease(pr(t, bt(33), bt(33) + 0.8))
        d.text(600, 470, f"−{round(94 * k1)}%", 150, A(GOLD, ga * dim), lat=1)
        d.text(600, 600, "病害", 44, A(INK, ga * dim))
        d.text(1320, 470, f"+{round(89 * k2)}%", 150, A(GOLD, ga * dim), lat=1)
        d.text(1320, 600, "产量", 44, A(INK, ga * dim))
    # fungicide crossed
    if bt(34) - 0.2 < t < bt(35):
        ga = ease(pr(t, bt(34), bt(34) + 0.3)) * (1 - pr(t, bt(35) - 0.4, bt(35)))
        x, y = 960, 470
        d.rect(x - 90, y - 110, x + 90, y + 170, fill=A((210, 214, 206), ga), outline=A(INK, ga), w=4, r=24)
        d.rect(x - 35, y - 170, x + 35, y - 110, fill=A(INK2, ga), r=8)
        d.text(x, y + 30, "杀菌剂", 40, A(INK, ga))
        k = ease(pr(t, bt(34, 1), bt(34, 1) + 0.35))
        d.line([(x - 170, y + 200), (lerp(x - 170, x + 170, k), lerp(y + 200, y - 200, k))], A(GOLD, ga), 12)
    # journal page
    if t > bt(35) - 0.2:
        k = ease(pr(t, bt(35), bt(35) + 0.9)); ga = k * fa
        y = lerp(-200, 0, k)
        d.rect(560, 170 + y, 1360, 880 + y, fill=A((252, 250, 244), ga), outline=A(INK2, ga * 0.6), w=2, r=8)
        d.text(620, 250 + y, "nature", 64, A((190, 40, 40) if False else INK, ga), anchor="lm", lat=1)
        d.line([(620, 300 + y), (1300, 300 + y)], A(INK, ga), 2)
        d.text(620, 390 + y, "Genetic diversity and", 44, A(INK, ga), anchor="lm", lat=1)
        d.text(620, 450 + y, "disease control in rice", 44, A(INK, ga), anchor="lm", lat=1)
        d.text(620, 530 + y, "Youyong Zhu et al.", 30, A(INK2, ga), anchor="lm", lat=2)
        d.text(620, 580 + y, "Nature 406, 718–722 · 17 Aug 2000", 30, A(INK2, ga), anchor="lm", lat=2)
        for j in range(5): d.line([(620, 660 + j * 36 + y), (1300 - (j == 4) * 300, 660 + j * 36 + y)], A(INK2, ga * 0.35), 6)

def hills(d, a, t):
    d.poly([(0, 700), (300, 520), (620, 640), (980, 470), (1350, 610), (1700, 500), (1920, 580), (1920, 1080), (0, 1080)], A((206, 210, 180), a))
    d.poly([(0, 820), (420, 650), (860, 760), (1260, 640), (1640, 750), (1920, 690), (1920, 1080), (0, 1080)], A((178, 192, 152), a))

def land(t, d):
    t0 = bt(36); a = ease(pr(t, t0, t0 + 0.7)) * (1 - pr(t, bt(41) - 0.5, bt(41)))
    if t < bt(37):
        ga = a * (1 - pr(t, bt(37) - 0.4, bt(37)))
        hills(d, ga, t)
        k = ease(pr(t, t0 + 0.2, bt(37) - 0.6))
        for j in range(16):
            for i in range(30):
                x = i * 66; y = 640 + j * 26
                ord_ = (abs(i - 15) / 15 + j / 16) / 2
                if ord_ < k * 1.05:
                    c = TALLG if (i + j) % 4 == 0 else SHORTG
                    d.rect(x, y, x + 60, y + 20, fill=A(c, ga * 0.8), r=6)
        d.text(960, 330, f"{3 * k:.1f} 亿多亩" if k < 1 else "3 亿多亩", 110, A(GOLD, ga))
    if bt(37) - 0.4 < t < bt(39):
        ga = ease(pr(t, bt(37) - 0.4, bt(37) + 0.3)) * (1 - pr(t, bt(39) - 0.4, bt(39))) * a
        hills(d, ga, t)
        if t < bt(38):
            hk = 1 - pr(t, bt(38) - 0.4, bt(38))
            for i, (x, y) in enumerate([(700, 610), (820, 590), (960, 625), (1090, 600), (1210, 630)]):
                k = ease(pr(t, bt(37) + i * BEAT * 0.5, bt(37) + i * BEAT * 0.5 + 0.4)) * ga * hk
                d.rect(x - 45, y, x + 45, y + 60, fill=A((236, 226, 204), k), outline=A(INK, k), w=3)
                d.poly([(x - 60, y + 2), (x, y - 45), (x + 60, y + 2)], A(INK2, k))
            d.text(960, 330, "2015 · 澜沧", 70, A(GOLD, ga * hk))
        else:
            fk = ease(pr(t, bt(38), bt(38) + 0.6)) * ga
            for i in range(6):
                x = 260 + i * 280; y = 820
                d.rect(x - 9, y - 60, x + 9, y, fill=A((110, 90, 70), fk))
                for k in range(4):
                    w = 120 - k * 24; yy = y - 60 - k * 70
                    d.poly([(x - w, yy), (x, yy - 110), (x + w, yy)], A((70, 112, 84), fk))
                for k in (-1, 1):
                    gk = ease(pr(t, bt(38, 1) + i * 0.12, bt(38, 2) + i * 0.12)) * fk
                    sx = x + k * 100; sy = 850
                    d.line([(sx, sy), (sx, sy - 40 * gk)], A(SHORTG, gk), 4)
                    for ang in range(5):
                        th = -math.pi / 2 + (ang - 2) * 0.55
                        d.line([(sx, sy - 40 * gk), (sx + math.cos(th) * 34 * gk, sy - 40 * gk + math.sin(th) * 24 * gk)], A(SHORTG, gk), 6)
                ground(d, 40, 1880, 852, fk)
            d.text(960, 250, "林下三七", 60, A(GOLD, fk))
    if bt(39) - 0.3 < t < bt(40):
        ga = ease(pr(t, bt(39) - 0.3, bt(39) + 0.3)) * (1 - pr(t, bt(40) - 0.4, bt(40))) * a
        plant(d, 520, 800, 400, True, t, a=ga, seed=1); plant(d, 640, 800, 270, False, t, a=ga, seed=2)
        x = 1340; y = 800
        d.rect(x - 9, y - 50, x + 9, y, fill=A((110, 90, 70), ga))
        for k in range(4):
            w = 110 - k * 22; yy = y - 50 - k * 64
            d.poly([(x - w, yy), (x, yy - 100), (x + w, yy)], A((70, 112, 84), ga))
        sx = 1470; d.line([(sx, y), (sx, y - 40)], A(SHORTG, ga), 4)
        for ang in range(5):
            th = -math.pi / 2 + (ang - 2) * 0.55
            d.line([(sx, y - 40), (sx + math.cos(th) * 34, y - 40 + math.sin(th) * 24)], A(SHORTG, ga), 6)
        ground(d, 380, 1600, 800, ga)
        k = ease(pr(t, bt(39, 1), bt(39, 2)))
        d.line([(760, 500), (lerp(760, 1160, k), 500)], A(GOLD, ga), 4)
        d.text(960, 440, "找对邻居", 44, A(GOLD, ga * k))
    if t > bt(40) - 0.3:
        ga = ease(pr(t, bt(40) - 0.1, bt(40) + 0.6)) * a
        d.text(960, 470, "“我就是一个", 76, A(INK, ga))
        d.text(960, 590, "会种庄稼的农民。”", 76, A(INK, ga))
        d.text(1300, 720, "—— 朱有勇", 36, A(INK2, ease(pr(t, bt(40, 2), bt(40, 3))) * ga))

def outro(t, d):
    t0 = bt(41); a = ease(pr(t, t0, t0 + 0.9)) * (1 - pr(t, bt(44) - 0.5, bt(44)))
    if a > 0:
        GY = 820; pat = [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]
        for i, tall in enumerate(pat):
            plant(d, 120 + i * 130, GY, 470 if tall else 320, tall, t, a=a, seed=i + 20, sway=2.4)
        ground(d, 50, 1870, GY, a)
        for k in range(5):
            ax = ((t - t0) * 300 + k * 420) % 2200 - 150
            yy = 250 + (k % 3) * 40
            d.line(qpts((ax, yy), (ax + 80, yy - 20), (ax + 170, yy), 6), A(SKY, 0.7 * a), 3)
    if t > bt(44) - 0.5:
        e = ease(pr(t, bt(44) - 0.3, bt(44) + 0.6)) * (1 - pr(t, DUR - 0.8, DUR))
        d.text(960, 380, "混  种", 120, A(INK, e))
        d.text(960, 480, "D I V E R S I T A S", 28, A(GOLD, e), lat=2)
        d.text(960, 640, "Ref: Zhu Y. et al. Genetic diversity and disease control in rice.", 26, A(INK2, e), lat=2)
        d.text(960, 685, "Nature 406, 718–722 (2000)", 26, A(INK2, e), lat=2)
        d.text(960, 740, "云南农业大学及公开报道整理", 26, A(INK2, e))

SUBS = {0: "同一个村，两块稻田。", 1: "左边，只种一种稻。", 2: "病，一株传一株。", 3: "右边，高的矮的，混着种。", 4: "病，停住了。",
        6: "为什么混着种，庄稼就少生病？",
        9: "为了高产，人们越来越爱只种一种。", 10: "可病菌也最爱这样的田。", 11: "吃完一块，接着下一块。", 12: "于是，农药一遍又一遍。",
        13: "云南的老乡，有个老习惯——", 14: "在稻田里，间栽几行高高的糯稻。", 15: "导师问他：这有没有科学道理？", 16: "这个问题，他追了近 20 年。",
        18: "病菌落到抗病的稻上——", 19: "走不通了。", 20: "矮稻站成一道墙，", 21: "把飘来的孢子挡在外面。",
        22: "糯稻比杂交稻高出一截。", 23: "风一吹，叶上的露水干得快——", 24: "病菌，发不了芽。", 25: "不是哪一株变强了，", 26: "是一块田，变得不一样了。",
        28: "1998 年，5 个乡镇的稻田全部混着种。", 29: "1999 年，10 个。", 30: "单种的糯稻，稻瘟病吃掉约 20% 的收成；", 31: "混种的，只有 1%。",
        32: "病害轻了 94%，产量多了 89%。", 34: "两年后，农民停掉了杀菌剂。", 35: "2000 年，这块田登上了《Nature》。",
        36: "后来，这套思路铺开到 3 亿多亩田里。", 37: "2015 年，他住进了澜沧的山村。", 38: "把三七种到松林下：不占耕地，不用农药。",
        39: "同一个道理：给庄稼找对邻居。", 42: "一块田里多一点不同，", 43: "就少一点农药。"}

def subs(t, d):
    b = int(t / BAR)
    if b in SUBS:
        s = SUBS[b]; t0 = b * BAR
        a = ease(pr(t, t0 + 0.05, t0 + 0.35)) * (1 - pr(t, t0 + BAR - 0.3, t0 + BAR - 0.05))
        if b + 1 in SUBS and t > t0 + BAR - 0.3: a = 1 - pr(t, t0 + BAR - 0.3, t0 + BAR - 0.05)
        d.text(960, 990, s, 44, A(INK, a))

SECS = [(0, 7, hook), (7, 9, title), (9, 13, mono), (13, 18, oldway), (18, 28, mechanism), (28, 36, trial), (36, 41, land), (41, 45, outro)]
def frame(t):
    img = Image.new("RGBA", (W, H), PAPER + (255,))
    d = D(img)
    for b0, b1, fn in SECS:
        if bt(b0) - 0.6 <= t < bt(b1) + 0.1:
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fn(t, D(lay))
            if fn is not outro and fn is not title:
                k = pr(t, bt(b1) - 0.55, bt(b1))
                if k > 0: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * (1 - k))))
            img.alpha_composite(lay)
    subs(t, d)
    return img.convert("RGB").resize((OW, OH), Image.LANCZOS)

if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]:
            frame(float(ts)).save(f"test_{ts}.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for i in range(i0, i1):
            p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); p.wait()
