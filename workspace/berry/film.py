import math, random, sys, subprocess
from PIL import Image, ImageDraw, ImageFont
from cues import *
import cues

OW, OH, FPS = 1080, 1920, 30
S = 1.5
W, H = int(OW * S), int(OH * S)
CJK = "/workspace/work/nobel/NotoSerifSC.otf"
LAT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
LATR = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
CREAM = (250, 243, 236); INK = (60, 44, 48); INK2 = (140, 120, 118)
BERRY = (222, 58, 72); BERRY_D = (176, 36, 54); BERRY_L = (244, 120, 120)
LEAF = (86, 150, 82); LEAF_D = (58, 118, 66); SEED = (246, 222, 150); SEED_D = (200, 160, 80)
GOLD = (236, 168, 36); GOLDL = (255, 214, 110); GRAY = (178, 168, 164); GREENB = (170, 204, 120)
PETAL = (255, 255, 255); POLLEN = (250, 200, 60); SKY = (140, 180, 210)
fc = {}
def F(size, lat=0):
    k = (size, lat)
    if k not in fc: fc[k] = ImageFont.truetype([CJK, LAT, LATR][lat], int(size * S))
    return fc[k]
def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x):  # overshoot pop
    x = cl(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def pr(t, a, b): return cl((t - a) / (b - a))
def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k): return tuple(int(lerp(a, b, cl(k))) for a, b in zip(c1, c2))
def A(c, a): return c[:3] + (int(255 * cl(a)),)
def P(x): return x * S
def win(t, a, b, fi=0.35, fo=0.35): return ease(pr(t, a, a + fi)) * (1 - pr(t, b - fo, b))

class D:
    def __init__(s, img): s.img = img; s.d = ImageDraw.Draw(img, "RGBA")
    def line(s, pts, fill, w): s.d.line([(P(x), P(y)) for x, y in pts], fill=fill, width=max(1, int(P(w))), joint="curve")
    def poly(s, pts, fill, outline=None): s.d.polygon([(P(x), P(y)) for x, y in pts], fill=fill, outline=outline)
    def circ(s, x, y, r, fill=None, outline=None, w=1): s.d.ellipse((P(x - r), P(y - r), P(x + r), P(y + r)), fill=fill, outline=outline, width=max(1, int(P(w))))
    def ell(s, x, y, rx, ry, fill): s.d.ellipse((P(x - rx), P(y - ry), P(x + rx), P(y + ry)), fill=fill)
    def rect(s, x0, y0, x1, y1, fill=None, outline=None, w=1, r=0):
        s.d.rounded_rectangle((P(x0), P(y0), P(x1), P(y1)), radius=P(r), fill=fill, outline=outline, width=max(1, int(P(w))) if outline else 0)
    def text(s, x, y, t, size, fill, anchor="mm", lat=0):
        al = fill[3] if len(fill) > 3 else 255
        if al <= 2: return
        fnt = F(size, lat); X, Y = P(x), P(y)
        if al >= 253: s.d.text((X, Y), t, font=fnt, fill=fill[:3], anchor=anchor); return
        b = [int(v) for v in s.d.textbbox((X, Y), t, font=fnt, anchor=anchor)]
        b[2] += 2; b[3] += 2
        m = Image.new("L", (b[2] - b[0], b[3] - b[1]), 0)
        ImageDraw.Draw(m).text((X - b[0], Y - b[1]), t, font=fnt, fill=al, anchor=anchor)
        s.img.paste(fill[:3], tuple(b), m)
    def tlen(s, t, size): return s.d.textlength(t, font=F(size)) / S

# ---------- strawberry ----------
def hw(u):
    if u < 0.3: return math.sqrt(max(0, 1 - ((0.3 - u) / 0.3) ** 2 * 0.55))
    return max(0, 1 - ((u - 0.3) / 0.7) ** 1.7) * 0.97 + 0.03 * (1 - u)
SEEDS = []
for r in range(10):
    u = 0.1 + r * 0.088
    n = max(1, int(round(6.5 * hw(u))))
    for j in range(n):
        s = (j + 0.5) / n * 2 - 1 + (0.08 if r % 2 else -0.08) / n
        SEEDS.append((u, s * 0.82))
DEFORM_SEEDS = {i for i, (u, s) in enumerate(SEEDS) if s > 0.15 and 0.35 < u < 0.8}

def deform_f(u, side, k):
    if side > 0: return 1 - 0.42 * k * math.exp(-((u - 0.58) / 0.2) ** 2)
    return 1 + 0.06 * k * math.exp(-((u - 0.5) / 0.25) ** 2)

def berry(d, cx, top, bw, bh, a=1.0, col=BERRY, lit=None, gray=None, deform=0.0, seeds=True, calyx=True, seed_off=None, gloss=True):
    us = [i / 40 for i in range(41)]
    def X(u, side): return cx + side * hw(u) * bw * deform_f(u, side, deform)
    tipshift = -bw * 0.18 * deform
    right = [(X(u, 1) + tipshift * u ** 3, top + u * bh) for u in us]
    left = [(X(u, -1) + tipshift * u ** 3, top + u * bh) for u in us[::-1]]
    d.poly(right + left, A(col, a))
    shade = [(X(u, 1) * 0.0 + (cx + tipshift * u ** 3 + (X(u, 1) - cx) * 0.98), top + u * bh) for u in us]
    d.poly(shade + [(cx + tipshift * u ** 3 + (X(u, 1) - cx) * 0.55, top + u * bh) for u in us[::-1]], A(mix(col, (0, 0, 0), 0.12), a * 0.6))
    if gloss: d.ell(cx - bw * 0.42, top + bh * 0.28, bw * 0.12, bh * 0.1, A((255, 255, 255), 0.35 * a))
    if seeds:
        for i, (u, s) in enumerate(SEEDS):
            if seed_off and seed_off(i) >= 1: continue
            side = 1 if s > 0 else -1
            x = cx + s * hw(u) * bw * deform_f(u, side, deform) + tipshift * u ** 3; y = top + u * bh
            if seed_off and seed_off(i) > 0:
                k = seed_off(i); x += (s + 0.2) * 260 * k; y -= 200 * k - 600 * k * k
            g = gray(i) if gray else 0
            l = lit(i) if lit else 0
            rr = bw * 0.035 * (1 - 0.35 * g)
            if l > 0: d.circ(x, y, rr * 2.4, fill=A(GOLDL, 0.55 * l * a))
            d.ell(x, y, rr, rr * 1.45, A(mix(mix(SEED, GOLD, l), GRAY, g), a))
            d.ell(x + rr * 0.25, y + rr * 0.3, rr * 0.45, rr * 0.7, A(mix(SEED_D, (120, 110, 106), g), a * 0.7))
    if calyx:
        cy = top + bh * 0.02
        for k in range(7):
            ang = math.pi * (0.08 + 0.84 * k / 6)
            ln = bw * (0.55 + 0.12 * (k % 2))
            tip = (cx + math.cos(ang) * ln * -1, cy + math.sin(ang) * ln * 0.42 + bh * 0.04)
            perp = (math.sin(ang) * bw * 0.09, math.cos(ang) * bw * 0.04)
            d.poly([(cx - perp[0], cy - perp[1]), tip, (cx + perp[0], cy + perp[1])], A(LEAF if k % 2 else LEAF_D, a))
        d.line([(cx, cy), (cx + bw * 0.05, cy - bh * 0.16)], A(LEAF_D, a), bw * 0.06)

def flower(d, cx, cy, r, a=1.0, center_col=(220, 226, 120), pistil=0.0, pollen=0.0, petals=1.0):
    for k in range(5):
        ang = -math.pi / 2 + k * 2 * math.pi / 5
        pr_ = r * 0.62 * petals
        d.circ(cx + math.cos(ang) * r * 0.62 * petals, cy + math.sin(ang) * r * 0.62 * petals, pr_, fill=A(PETAL, a * petals))
        d.circ(cx + math.cos(ang) * r * 0.62 * petals, cy + math.sin(ang) * r * 0.62 * petals, pr_, outline=A((230, 220, 214), a * petals), w=2)
    for k in range(18):
        ang = k * 2 * math.pi / 18
        d.circ(cx + math.cos(ang) * r * 0.5, cy + math.sin(ang) * r * 0.5, r * 0.06, fill=A(POLLEN, a))
    d.circ(cx, cy, r * 0.42, fill=A(center_col, a))
    rng = random.Random(3)
    for i in range(int(48 * pistil)):
        ang = rng.uniform(0, 6.28); rr = math.sqrt(rng.uniform(0, 1)) * r * 0.36
        d.circ(cx + math.cos(ang) * rr, cy + math.sin(ang) * rr, r * 0.025, fill=A(mix((150, 170, 80), SEED, pollen), a))

def bee(d, x, y, a=1.0, t=0):
    fl = abs(math.sin(t * 40))
    d.ell(x - 8, y - 26, 22, 14 + 8 * fl, A((220, 236, 246), 0.8 * a)); d.ell(x + 14, y - 24, 18, 12 + 6 * fl, A((220, 236, 246), 0.8 * a))
    d.ell(x, y, 34, 22, A((246, 196, 40), a))
    for k in (-10, 6): d.rect(x + k - 4, y - 21, x + k + 4, y + 21, fill=A(INK, a))
    d.circ(x + 32, y - 2, 12, fill=A(INK, a))

def wrap(d, s, size, maxw=920):
    if d.tlen(s, size) <= maxw: return [s]
    best = None
    for i in range(1, len(s)):
        if (s[i - 1] in "，：；、。" or (s[i - 1] == "—" and s[i] != "—")) and abs(i - len(s) / 2) < len(s) * 0.35:
            if best is None or abs(i - len(s) / 2) < abs(best - len(s) / 2): best = i
    if best is None: best = len(s) // 2
    return [s[:best], s[best:]]

SUBS = [(0.0, 3.0, "你吃的草莓，其实不是果实。"), (3.0, 6.0, "真正的果实，是表面这些“籽”。"), (6.0, 8.0, "那它，为什么会长歪？"),
        (11.0, 14.0, "时间倒回去，它是一朵小白花。"), (14.0, 17.0, "花心上，挤着一两百个雌蕊。"), (17.0, 21.0, "每个雌蕊授上粉，就变成一颗“籽”。"),
        (21.0, 26.0, "而你吃的红果肉，是花托——茎的顶端，鼓起来了。"),
        (26.0, 29.5, "授上粉的籽，会放出一种信号：生长素。"), (29.5, 33.0, "周围的果肉，收到信号就往外长。"), (33.0, 36.5, "没授上粉的籽，干瘪，不出声。"),
        (36.5, 40.0, "它周围的那一块，就不长。"), (40.0, 45.0, "一边鼓，一边瘦——草莓就歪了。"),
        (45.0, 49.0, "1950 年，加州理工的尼奇做了个实验。"), (49.0, 53.0, "把小草莓的籽全部摘掉——它不长了。"), (53.0, 57.0, "摘掉籽，再涂上生长素——它照样长大。"),
        (57.0, 61.0, "果实有多重，几乎跟授上粉的籽数成正比。"), (61.0, 65.0, "籽越多，草莓越大。"),
        (65.0, 69.0, "只靠风和重力，籽的授粉率很少超过 60%。"), (69.0, 73.0, "所以大棚里，要放蜜蜂。"), (73.0, 77.0, "开花时太冷、阴雨、下霜，籽也会坏。"),
        (77.0, 82.0, "挑草莓看一眼：籽饱满、均匀，就长得周正。"), (82.0, 86.0, "每一颗籽，都管着身边那一口甜。")]

def subs(t, d):
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.2)) * (1 - pr(t, b - 0.15, b))
            pop = 1 - 0.12 * (1 - back(pr(t, a, a + 0.3)))
            lines = wrap(d, s, 54)
            for i, ln in enumerate(lines):
                y = 1430 + (i - (len(lines) - 1) / 2) * 78 + (1 - pop) * 60
                d.text(540, y, ln, 54, A(INK, al))

def header(t, d):
    d.rect(370, 96, 710, 146, fill=A(INK, 0.9), r=25)
    d.text(540, 121, "Vibe 知识大赏", 28, A(CREAM, 1))
    a = ease(pr(t, 11, 11.5)) * (1 - pr(t, END - 0.3, END))
    d.text(540, 200, "籽 说 了 算", 40, A(BERRY_D, a))

# ---------- sections ----------
def hook(t, d):
    a = 1 - pr(t, 7.8, 8.1)
    sc = back(pr(t, 0, 0.45)); mv = eio(pr(t, ROLL_IN, ROLL_IN + 0.7))
    cx = lerp(540, 330, mv); bw = lerp(260, 190, mv) * sc; bh = bw * 2.1
    top = lerp(820, 860, mv) - bh / 2 + 80
    def lit(i):
        if i >= len(SEEDS): return 0
        k = i % 10
        return ease(pr(t, HOOK_SEEDS[k], HOOK_SEEDS[k] + 0.2)) * (1 - pr(t, ROLL_IN, ROLL_IN + 0.5)) if i % 3 == 0 or i < 10 else ease(pr(t, 5.6, 5.9)) * (1 - pr(t, ROLL_IN, ROLL_IN + 0.5))
    berry(d, cx, top, bw, bh, a, lit=lit)
    if t > ROLL_IN:
        k = ease(pr(t, ROLL_IN, ROLL_IN + 0.7)); x = lerp(1250, 760, k); rot = (1 - k)
        berry(d, x, 860 - 190 * 2.1 / 2 + 80 - 30 * math.sin(k * math.pi), 190, 190 * 2.1, a, deform=1.0, gray=lambda i: 1.0 if i in DEFORM_SEEDS else 0)
        q = ease(pr(t, 6.6, 7.0))
        d.text(760, 520, "?", 120, A(BERRY_D, q * a), lat=1)

def title(t, d):
    a = win(t, TITLE, 11.0, 0.3, 0.3)
    k = back(pr(t, TITLE, TITLE + 0.45))
    d.ell(540, 640, 46 * k, 66 * k, A(GOLD, a)); d.ell(552, 654, 18 * k, 28 * k, A(SEED_D, a * 0.8))
    d.text(540, 850, "籽说了算", int(150 * (0.85 + 0.15 * k)), A(INK, a))
    b = ease(pr(t, TITLE + 0.5, TITLE + 1.0))
    d.text(540, 1010, "草莓长成什么样，由表面的籽决定", 38, A(INK2, a * b))

def anatomy(t, d):
    a = win(t, 11.0, 26.0, 0.3, 0.4)
    cx, cy = 540, 820
    # rewind: berry shrinks into flower
    rw = eio(pr(t, REWIND[0], REWIND[1]))
    if rw < 1:
        bw = lerp(240, 60, rw); berry(d, cx, cy - bw * 1.05, bw, bw * 2.1, a * (1 - rw))
    pis = pr(t, PISTILS[0], PISTILS[-1] + 0.2)
    pol = pr(t, POLLEN[0], POLLEN[-1] + 0.2)
    sw = eio(pr(t, SWELL, SWELL + 1.6))
    if rw > 0 and sw < 1:
        fa = a * rw * (1 - sw)
        flower(d, cx, cy, 300 * (0.6 + 0.4 * rw), fa, pistil=pis, pollen=pol, petals=1 - sw * 0.9)
        # pollen grains falling on 8ths
        for i, tk in enumerate(POLLEN):
            u = pr(t, tk - 0.35, tk)
            if 0 < u < 1:
                r = random.Random(i); px = cx + r.uniform(-90, 90)
                d.circ(px, lerp(cy - 380, cy + r.uniform(-60, 60), u), 9, fill=A(POLLEN, fa))
    if sw > 0:
        bw = lerp(70, 250, sw); bh = bw * 2.1
        berry(d, cx, cy - bh * 0.45, bw, bh, a, col=mix(GREENB, BERRY, sw))
        lab = ease(pr(t, SWELL + 1.6, SWELL + 2.2)) * a
        d.line([(cx + 120, cy + 40), (cx + 330, cy - 60)], A(INK2, lab), 3); d.text(cx + 300, cy - 90, "花托（果肉）", 34, A(INK, lab), anchor="mm")
        d.line([(cx - 160, cy - 60), (cx - 330, cy - 200)], A(INK2, lab), 3); d.text(cx - 330, cy - 235, "瘦果（籽）", 34, A(INK, lab))
    if 14 < t < 22:
        la = win(t, 14.6, 21.6, 0.3, 0.3) * a
        d.text(cx, cy + 380, "雌蕊 × 一两百", 36, A(INK2, la))

# close-up grid
GRID = [(x, y) for y in range(5) for x in range(5)]
GRAYSET = {3, 4, 8, 9, 14}
def surface(t, d):
    a = win(t, 26.0, 40.9, 0.3, 0.5)
    gx, gy, cs = 540 - 2 * 160, 560, 155
    d.rect(110, 440, 970, 1240, fill=A(BERRY, a), r=60)
    d.text(540, 400, "放大：草莓表面", 32, A(INK2, a))
    dent = ease(pr(t, DENT, DENT + 0.8))
    if dent > 0:
        d.rect(110 + 3 * cs - 10, 440, 970, 440 + 3 * cs + 30, fill=A(BERRY_D, 0.45 * dent * a), r=60)
    for i, (x, y) in enumerate(GRID):
        px, py = gx + x * cs + (cs / 2 if y % 2 else 0) - 40, gy + y * cs
        if px > 920: continue
        g = i in GRAYSET
        if not g:
            k = i % 6
            sg = ease(pr(t, SIGNAL[k], SIGNAL[k] + 0.25)); bm = back(pr(t, BUMPS[k], BUMPS[k] + 0.4))
            if bm > 0:
                for rr, al in ((82, 0.25), (62, 0.3), (42, 0.35)):
                    d.circ(px, py, rr * bm, fill=A(BERRY_L, al * a))
            if sg > 0:
                for j in range(6):
                    ph = (t - SIGNAL[k]) * 1.2 + j / 6
                    rr = 30 + (ph % 1) * 70; ang = j * 1.05 + i
                    d.circ(px + math.cos(ang) * rr, py + math.sin(ang) * rr, 6 * (1 - ph % 1), fill=A(GOLD, sg * a))
            d.ell(px, py, 18, 26, A(mix(SEED, GOLD, sg), a))
        else:
            tk = cues.GRAY[sorted(GRAYSET).index(i) % 4]
            gg = ease(pr(t, tk, tk + 0.3))
            d.ell(px, py, 18 * (1 - 0.35 * gg), 26 * (1 - 0.35 * gg), A(mix(SEED, GRAY, gg), a))
    lab = win(t, SIGNAL[0], 33.0, 0.3, 0.3) * a
    d.text(540, 1300 - 20, "", 30, A(GOLD, lab))
    if t > 26.4 and t < 33:
        d.rect(370, 1255, 710, 1305, fill=A(GOLD, lab * 0.95), r=25); d.text(540, 1280, "生长素", 30, A((255, 255, 255), lab))

def tilt(t, d):  # 40-45 whole misshapen berry
    a = win(t, 40.6, 45.0, 0.4, 0.4)
    if a <= 0: return
    dk = ease(pr(t, HIT2, HIT2 + 0.5))
    berry(d, 540, 520, 270, 270 * 2.1, a, deform=dk, gray=lambda i: dk if i in DEFORM_SEEDS else 0)
    d.text(870, 700, "这一侧的籽", 34, A(INK2, a * dk)); d.text(870, 748, "没授上粉", 34, A(INK2, a * dk))

def lab(t, d):
    a = win(t, 45.0, 65.0, 0.4, 0.4)
    if t < 57:
        tag = ease(pr(t, LAB, LAB + 0.5)) * a
        d.text(540, 380, "1950 · Caltech · J. P. Nitsch", 32, A(INK2, tag), lat=2)
        d.rect(140, 1080, 940, 1110, fill=A((214, 200, 190), a), r=12)
        # A: seeds removed -> stays small
        bwA = 120
        def off(i): return ease(pr(t, PLUCK[i % 8], PLUCK[i % 8] + 0.6)) * 1.0001
        berry(d, 330, 1080 - bwA * 2.1 + 10, bwA, bwA * 2.1, a, col=GREENB, seed_off=off if t > 49 else None)
        d.text(330, 1160, "摘掉籽", 34, A(INK, a * ease(pr(t, 49, 49.4))))
        xa = ease(pr(t, 51.5, 51.9)) * a
        d.text(330, 640, "不长", 40, A(INK2, xa))
        # B: seeds removed + auxin -> grows
        if t > 53:
            gb = ease(pr(t, HIT3, HIT3 + 1.4)); bwB = lerp(120, 200, gb)
            berry(d, 750, 1080 - bwB * 2.1 + 10, bwB, bwB * 2.1, a * ease(pr(t, 53, 53.3)), col=mix(GREENB, BERRY, gb), seeds=False)
            br = pr(t, BRUSH, HIT3)
            if 0 < br < 1:
                d.line([(640, 760), (lerp(640, 860, br), 760 + 40 * math.sin(br * 9))], A(GOLD, a), 22)
            if t > BRUSH:
                d.text(750, 1160, "摘掉籽 + 生长素", 34, A(INK, a))
            gg = ease(pr(t, HIT3 + 0.3, HIT3 + 0.8))
            d.text(750, 560 - 80 * gb, "照样长大", 40, A(GOLD, a * gg))
    else:
        ca = win(t, 57.0, 65.0, 0.4, 0.4)
        x0, y0, x1, y1 = 200, 1150, 900, 520
        d.line([(x0, y0), (x1 + 20, y0)], A(INK, ca), 4); d.line([(x0, y0), (x0, y1 - 20)], A(INK, ca), 4)
        d.text((x0 + x1) / 2, y0 + 50, "授上粉的籽数 →", 32, A(INK2, ca)); d.text(x0 - 20, y1 - 50, "果重 ↑", 32, A(INK2, ca), anchor="lm")
        r = random.Random(5)
        for i, tk in enumerate(CHART):
            k = back(pr(t, tk, tk + 0.3))
            u = (i + 0.5) / 8; px = lerp(x0 + 40, x1 - 20, u); py = lerp(y0 - 40, y1 + 30, u) + r.uniform(-30, 30)
            if k > 0: berry(d, px, py - 30 * k, 26 * k, 55 * k, ca, calyx=True, seeds=False, gloss=False)
        lk = eio(pr(t, CHART[-1] + 0.3, CHART[-1] + 1.2))
        d.line([(x0 + 40, y0 - 40), (lerp(x0 + 40, x1 - 20, lk), lerp(y0 - 40, y1 + 30, lk))], A(GOLD, ca), 5)

def field(t, d):
    a = win(t, 65.0, 82.0, 0.4, 0.4)
    if t < 69:
        k = eio(pr(t, GAUGE[0], GAUGE[1]))
        d.text(540, 560, "无昆虫授粉", 40, A(INK2, a))
        d.rect(160, 700, 920, 770, fill=A((230, 220, 214), a), r=35)
        d.rect(160, 700, 160 + 760 * 0.6 * k + 1, 770, fill=A(BERRY, a), r=35)
        d.text(540, 890, f"≤ {round(60 * k)}%", 110, A(BERRY_D, a), lat=1)
        d.text(540, 1010, "籽的授粉率", 34, A(INK2, a))
    elif t < 73:
        ba = win(t, 69.0, 73.0, 0.3, 0.3) * a
        xs = [180, 360, 540, 720, 900]
        for i, x in enumerate(xs):
            hit = ease(pr(t, BEE[0] + 0.5 + i * 0.6, BEE[0] + 0.8 + i * 0.6))
            flower(d, x, 960, 85, ba, pistil=1, pollen=hit)
            d.line([(x, 1045), (x, 1180)], A(LEAF_D, ba), 6)
        u = pr(t, BEE[0], BEE[1]); bx = lerp(80, 1000, u); by = 860 + math.sin(u * 5 * math.pi) * 70
        trail = [(lerp(80, 1000, v), 860 + math.sin(v * 5 * math.pi) * 70) for v in [u * j / 20 for j in range(21)]]
        if len(trail) > 1: d.line(trail, A(GOLDL, ba * 0.8), 4)
        bee(d, bx, by, ba, t)
    elif t < 77:
        ca = win(t, 73.0, 77.0, 0.3, 0.3) * a
        k = eio(pr(t, COLD[0], COLD[1]))
        d.rect(500, 520, 580, 1060, fill=A((235, 235, 240), ca), outline=A(INK2, ca), w=3, r=40)
        d.circ(540, 1080, 62, fill=A(SKY, ca))
        d.rect(522, lerp(600, 960, k), 558, 1080, fill=A(SKY, ca), r=18)
        d.text(470, lerp(620, 960, k), f"{round(lerp(22, 2, k))}°C", 48, A(INK, ca), anchor="rm", lat=1)
        r = random.Random(2)
        for i in range(14):
            sx = r.uniform(120, 960); sy = (r.uniform(0, 1) + (t - 73) * 0.25) % 1 * 800 + 450
            d.text(sx, sy, "*", 44, A(SKY, ca * k), lat=1)
        flower(d, 210, 1000, 80, ca, pistil=1, pollen=0, center_col=mix((220, 226, 120), GRAY, k))
        flower(d, 860, 880, 90, ca, pistil=1, pollen=0, center_col=mix((220, 226, 120), GRAY, k))
    else:
        ca = win(t, 77.0, 82.0, 0.3, 0.3) * a
        berry(d, 330, 640, 170, 357, ca)
        berry(d, 750, 640, 170, 357, ca, deform=1.0, gray=lambda i: 1.0 if i in DEFORM_SEEDS else 0)
        ck = back(pr(t, CHECK, CHECK + 0.35))
        if ck > 0:
            d.line([(270, 1110), (320, 1160), (410, 1060)], A(LEAF, ca), 14)
            d.text(330, 1220, "籽饱满均匀", 34, A(INK, ca * cl(ck)))
            d.text(750, 1220, "一侧籽干瘪", 34, A(INK2, ca * cl(ck)))

def finale(t, d):
    a = ease(pr(t, 82.0, 82.4)) * (1 - pr(t, END, END + 0.4))
    if a > 0:
        def lit(i): return ease(pr(t, FINALE[i % 16], FINALE[i % 16] + 0.15))
        berry(d, 540, 560, 260, 546, a, lit=lit)
    if t > END - 0.1:
        e = ease(pr(t, END, END + 0.5)) * (1 - pr(t, DUR - 0.6, DUR))
        k = back(pr(t, END, END + 0.45))
        d.ell(540, 640, 40 * k, 58 * k, A(GOLD, e))
        d.text(540, 830, "草莓长成什么样，", 60, A(INK, e))
        d.text(540, 920, "籽说了算。", 84, A(BERRY_D, e))
        d.text(540, 1250, "Ref: Nitsch J.P. Growth and morphogenesis of the strawberry", 26, A(INK2, e), lat=2)
        d.text(540, 1285, "as related to auxin. Am. J. Bot. 37:211 (1950)", 26, A(INK2, e), lat=2)

SECS = [(0, 8.1, hook), (8, 11, title), (11, 26, anatomy), (26, 45, surface), (40, 45, tilt), (45, 65, lab), (65, 82, field), (82, 90, finale)]
def frame(t):
    img = Image.new("RGB", (W, H), CREAM)
    d = D(img)
    for a, b, fn in SECS:
        if a - 0.05 <= t < b + 0.05:
            fn(t, d)
    header(t, d); subs(t, d)
    return img.convert("RGB").resize((OW, OH), Image.LANCZOS)

if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.1f}.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for i in range(i0, i1): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); p.wait()
