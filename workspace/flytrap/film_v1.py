import math, random, sys, subprocess
from PIL import Image, ImageDraw, ImageFont
from cues import *

OW, OH, FPS = 1080, 1920, 30
S = 1.5
W, H = int(OW * S), int(OH * S)
FONTS = ["/workspace/work/flytrap/NotoSansSC-Bold.otf", "/workspace/work/flytrap/NotoSansSC-Black.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
BG = (18, 20, 28); BG2 = (30, 34, 46); WHITE = (245, 245, 240); MUTE = (150, 156, 170)
RED = (232, 62, 52); RED_D = (178, 36, 34); RED_L = (255, 130, 110)
LEAF = (88, 170, 92); LEAF_D = (56, 120, 66); CYAN = (90, 220, 240); YEL = (255, 214, 64); WATER = (90, 160, 240)
INK = (24, 18, 20); TONGUE = (255, 120, 140)
fc = {}
def F(size, k=0):
    key = (size, k)
    if key not in fc: fc[key] = ImageFont.truetype(FONTS[k], int(size * S))
    return fc[key]
def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def pr(t, a, b): return cl((t - a) / (b - a))
def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k): return tuple(int(lerp(a, b, cl(k))) for a, b in zip(c1, c2))
def A(c, a): return c[:3] + (int(255 * cl(a)),)
def P(x): return x * S
def win(t, a, b, fi=0.3, fo=0.3): return ease(pr(t, a, a + fi)) * (1 - pr(t, b - fo, b))
def pulse(t, times, dec=6.0):  # 1 at each hit, decaying
    v = 0
    for h in times:
        if h <= t: v = max(v, math.exp(-(t - h) * dec))
    return v

class D:
    def __init__(s, img): s.img = img; s.d = ImageDraw.Draw(img, "RGBA")
    def line(s, pts, fill, w): s.d.line([(P(x), P(y)) for x, y in pts], fill=fill, width=max(1, int(P(w))), joint="curve")
    def poly(s, pts, fill): s.d.polygon([(P(x), P(y)) for x, y in pts], fill=fill)
    def circ(s, x, y, r, fill=None, outline=None, w=1): s.d.ellipse((P(x - r), P(y - r), P(x + r), P(y + r)), fill=fill, outline=outline, width=max(1, int(P(w))))
    def ell(s, x, y, rx, ry, fill=None, outline=None, w=1): s.d.ellipse((P(x - rx), P(y - ry), P(x + rx), P(y + ry)), fill=fill, outline=outline, width=max(1, int(P(w))))
    def arc(s, x, y, rx, ry, a0, a1, fill, w): s.d.arc((P(x - rx), P(y - ry), P(x + rx), P(y + ry)), a0, a1, fill=fill, width=max(1, int(P(w))))
    def rect(s, x0, y0, x1, y1, fill=None, outline=None, w=1, r=0):
        s.d.rounded_rectangle((P(x0), P(y0), P(x1), P(y1)), radius=P(r), fill=fill, outline=outline, width=max(1, int(P(w))) if outline else 0)
    def text(s, x, y, t, size, fill, anchor="mm", k=0):
        al = fill[3] if len(fill) > 3 else 255
        if al <= 2: return
        fnt = F(size, k); X, Y = P(x), P(y)
        if al >= 253: s.d.text((X, Y), t, font=fnt, fill=fill[:3], anchor=anchor); return
        b = [int(v) for v in s.d.textbbox((X, Y), t, font=fnt, anchor=anchor)]; b[2] += 2; b[3] += 2
        m = Image.new("L", (b[2] - b[0], b[3] - b[1]), 0)
        ImageDraw.Draw(m).text((X - b[0], Y - b[1]), t, font=fnt, fill=al, anchor=anchor)
        s.img.paste(fill[:3], tuple(b), m)
    def tlen(s, t, size, k=0): return s.d.textlength(t, font=F(size, k)) / S

def rings(d, x, y, t, hits, col=CYAN, a=1.0, maxr=420):
    for h in hits:
        u = (t - h) / 0.8
        if 0 <= u < 1:
            for j in range(3):
                rr = 60 + (u + j * 0.12) * maxr
                d.circ(x, y, rr, outline=A(col, a * (1 - u) * (1 - j * 0.3)), w=8 - j * 2)

def wave(d, x0, x1, y, amp, t, hits, a=1.0, col=CYAN, w=5):
    pts = []
    n = 160
    for i in range(n + 1):
        xx = lerp(x0, x1, i / n); v = math.sin(i * 0.9 + t * 30) * 0.06
        for h in hits:
            dt = t - h
            if 0 <= dt < 0.6:
                ctr = lerp(x0, x1, (h * 7.31) % 1)
                v += math.sin((xx - ctr) * 0.25) * math.exp(-((xx - ctr) / 60) ** 2) * math.exp(-dt * 7)
        pts.append((xx, y + v * amp))
    d.line(pts, A(col, a), w)

def wrap(d, s, size, maxw=940):
    if d.tlen(s, size) <= maxw: return [s]
    best = None
    for i in range(1, len(s)):
        if (s[i - 1] in "，：；、。" or (s[i - 1] == "—" and s[i] != "—")) and abs(i - len(s) / 2) < len(s) * 0.35:
            if best is None or abs(i - len(s) / 2) < abs(best - len(s) / 2): best = i
    if best is None: best = len(s) // 2
    return [s[:best], s[best:]]

GREEN = (96, 178, 80); GREEN_D = (52, 112, 52); GREEN_L = (150, 210, 110); INNER = (196, 40, 66); INNER_D = (110, 18, 40)
DIGEST = (150, 230, 90); FLYC = (40, 42, 52)

def eyes(d, x, y, r, face, a, look=0.0):
    for s_ in (-1, 1):
        ex = x + s_ * r * 2.5
        if face == "sleep":
            d.arc(ex, y, r, r * 0.6, 20, 160, A(INK, a), r * 0.28); continue
        if face == "happy" or (face == "wink" and s_ == 1):
            d.arc(ex, y + r * 0.4, r, r, 200, 340, A(INK, a), r * 0.3); continue
        if face == "chomp":
            d.line([(ex - r * .8, y - r * .5), (ex + r * .5 * s_ * -1 + r * 0.0, y), (ex - r * .8, y + r * .5)] if s_ < 0 else
                   [(ex + r * .8, y - r * .5), (ex - r * .3, y), (ex + r * .8, y + r * .5)], A(INK, a), r * 0.3); continue
        d.circ(ex, y, r, fill=A(WHITE, a))
        pr_ = r * (0.32 if face == "evil" else 0.5)
        d.circ(ex + look * r * 0.4, y + r * 0.1, pr_, fill=A(INK, a))
        if face in ("peek", "smug", "evil"):
            lid = {"peek": 0.15, "smug": 0.05, "evil": 0.1}[face]
            d.rect(ex - r * 1.15, y - r * 1.2, ex + r * 1.15, y - r * lid, fill=A(GREEN, a))
            d.line([(ex - r, y - r * lid), (ex + r, y - r * lid)], A(GREEN_D, a), r * 0.15)
        if face == "evil":
            d.line([(ex + s_ * r * 1.3, y - r * 1.3), (ex - s_ * r * 0.6, y - r * 0.6)], A(INK, a), r * 0.3)
        if face == "smug" and s_ == 1:
            d.line([(ex - r, y - r * 1.4), (ex + r, y - r * 1.7)], A(INK, a), r * 0.28)

def trap(d, x, y, w, op, face="open", a=1.0, glow=0.0, look=0.0, stem=True, flyin=None):
    h = w * 0.58; gap = op * h * 1.15
    yu, yl = y - gap / 2, y + gap / 2
    if stem:
        d.line([(x, yl + h * 0.8), (x - 30, yl + h + 260), (x - 10, 1960)], A(GREEN_D, a), w * 0.12)
        d.poly([(x - 30, yl + h + 160), (x - 260, yl + h + 120), (x - 40, yl + h + 230)], A(GREEN_D, a))
    if gap > 4:
        d.ell(x, y, w * 0.93, gap / 2 + h * 0.18, A(INNER_D, a))
        d.ell(x, y + gap * 0.1, w * 0.8, gap / 2, A(INNER, a))
        if glow > 0: d.ell(x, y + gap * 0.1, w * 0.8, gap / 2, A(DIGEST, a * glow * 0.8))
        for k in (-1, 0, 1):
            hx = x + k * w * 0.32; hy = yl - gap * 0.05
            d.line([(hx, hy), (hx + k * 6, hy - min(gap * 0.35, 55))], A((255, 220, 200), a), 5)
        if flyin: flyin()
    pts_u = [(x + math.cos(t_) * w, yu + math.sin(t_) * h) for t_ in [math.pi + i * math.pi / 40 for i in range(41)]]
    pts_l = [(x + math.cos(t_) * w, yl + math.sin(t_) * h) for t_ in [i * math.pi / 40 for i in range(41)]]
    n = 11
    for i in range(n):
        tx = x - w * 0.95 + (i + 0.5) * (w * 1.9 / n)
        d.poly([(tx - 13, yu - 4), (tx + 13, yu - 4), (tx + (2 if op > 0.2 else 0), yu + h * 0.32)], A(GREEN_L, a))
        tx2 = tx + w * 0.95 / n
        if i < n - 1: d.poly([(tx2 - 13, yl + 4), (tx2 + 13, yl + 4), (tx2, yl - h * 0.32)], A(GREEN_L, a))
    d.poly(pts_l, A(GREEN, a)); d.line([(x - w, yl), (x + w, yl)], A(INNER, a), 12)
    d.poly(pts_u, A(GREEN, a)); d.line([(x - w, yu), (x + w, yu)], A(INNER, a), 12)
    if op < 0.25:  # interlocking teeth along the closed seam
        k_ = 1 - op / 0.25
        for i in range(n):
            tx = x - w * 0.95 + (i + 0.5) * (w * 1.9 / n)
            d.poly([(tx - 12, yu), (tx + 12, yu), (tx, yu + h * 0.28 * k_)], A(GREEN_L, a))
            tx2 = tx + w * 0.95 / n
            if i < n - 1: d.poly([(tx2 - 12, yl), (tx2 + 12, yl), (tx2, yl - h * 0.28 * k_)], A(GREEN_L, a))
    d.ell(x - w * 0.45, yu - h * 0.7, w * 0.2, h * 0.1, A((255, 255, 255), 0.25 * a))
    eyes(d, x, yu - h * 0.5, w * 0.13, face, a, look)

def fly(d, x, y, s, a=1.0, t=0.0, scared=False, flap=True):
    ang = math.sin(t * 60) * 0.5 if flap else 0.2
    for s_ in (-1, 1):
        wx = x + s_ * s * 0.55; wy = y - s * 0.55 - ang * s * 0.3
        d.ell(wx, wy, s * 0.45, s * 0.65, A((200, 230, 255), 0.55 * a))
    d.ell(x, y, s * 0.55, s * 0.62, A(FLYC, a))
    for s_ in (-1, 1):
        d.circ(x + s_ * s * 0.33, y - s * 0.38, s * 0.32, fill=A((200, 40, 40), a)); d.circ(x + s_ * s * 0.25, y - s * 0.48, s * 0.09, fill=A(WHITE, a))
        for k in range(3): d.line([(x + s_ * s * 0.4, y + s * (0.05 + k * 0.2)), (x + s_ * s * 0.85, y + s * (0.25 + k * 0.25))], A(FLYC, a), s * 0.07)
    if scared:
        d.ell(x, y + s * 0.22, s * 0.12, s * 0.15, A(INK, a)); d.ell(x + s * 0.75, y - s * 0.6, s * 0.1, s * 0.16, A(CYAN, a))

def bignum(d, t, n, hit, y=330, col=YEL, a=1.0, size=230):
    k = back(pr(t, hit, hit + 0.2))
    if k <= 0: return
    d.text(540, y, str(n), int(size * (0.6 + 0.4 * k)), A(col, a), k=1)

def flash(d, t, hits, col=WHITE, amt=0.5):
    p = pulse(t, hits, 12)
    if p > 0.02: d.rect(0, 0, OW, OH, fill=A(col, amt * p))

SUBS = [(0.0, 2.6, "捕蝇草会数数：被碰几下，它都记着。"),
        (2.6, 6.0, "只碰一下，它一般不动。"),
        (6.0, 9.0, "30 秒内没有第二下，它就忘了。"),
        (9.0, 12.0, "30 秒内碰两下：立刻合上。"),
        (12.0, 14.0, "苍蝇在里面挣扎，它接着数——"),
        (14.0, 16.5, "数到 3：开始制造消化酶。"),
        (20.0, 24.0, "数到 5：全力开吃。"),
        (24.0, 27.0, "为什么要数？风吹、雨滴通常只碰一下。"),
        (27.0, 30.0, "合一次很费力气，不能白合。"),
        (30.0, 35.0, "挣扎得越多，消化液分泌得越多。"),
        (35.0, 39.0, "数到 5 以后，还会打开吸收泵，吸走猎物里的盐分。")]

def subs(t, d):
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.15)) * (1 - pr(t, b - 0.12, b))
            lines = wrap(d, s, 58)
            for i, ln in enumerate(lines):
                y = 1500 + (i - (len(lines) - 1) / 2) * 84
                d.rect(540 - d.tlen(ln, 58) / 2 - 22, y - 44, 540 + d.tlen(ln, 58) / 2 + 22, y + 44, fill=A((0, 0, 0), 0.55 * al), r=14)
                d.text(540, y, ln, 58, A(WHITE, al))

def brand(t, d):
    d.rect(50, 80, 300, 128, fill=A(WHITE, 0.92), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(BG, 1))

def snap_op(t, t_snap, before=1.0):
    if t < t_snap: return before
    return max(0.0, 1 - (t - t_snap) / 0.06)

def shake(t, amt, f=70): return amt * math.sin(t * f), amt * 0.6 * math.cos(t * f * 1.3)

def s_hook(t, d):
    a = 1 - pr(t, 2.45, 2.6)
    op = snap_op(t, HOOK_SNAP)
    face = "peek" if t < HOOK_SNAP else ("chomp" if t < HOOK_SNAP + 0.5 else "happy")
    sx, sy = shake(t, 18 * pulse(t, [HOOK_SNAP], 4))
    fx = lerp(180, 540, ease(pr(t, -0.3, 0.1))); fy = lerp(500, 980, ease(pr(t, -0.3, 0.1)))
    trap(d, 540 + sx, 900 + sy, 360, op, face, a, look=0.3 if t < HOOK_SNAP else 0,
         flyin=lambda: fly(d, fx + sx, fy + sy, 80, a, t, scared=t > 0.25))
    flash(d, t, [HOOK_SNAP], YEL, 0.35)
    k = back(pr(t, 0.0, 0.2)) * (1 + 0.15 * pulse(t, [HOOK_SNAP], 6))
    d.text(540 + sx * 0.5, 330, "它会数数", int(150 * (0.6 + 0.4 * k)), A(YEL, a), k=1)
    for i, h in enumerate(HOOK_TOUCH):
        if h <= t < HOOK_SNAP + 0.3: d.text(840, 560 - i * 10, str(i + 1), 120, A(WHITE, a * (1 - pr(t, HOOK_SNAP, HOOK_SNAP + 0.3))), k=1)

def s_rule1(t, d):
    a = win(t, 2.6, 9.0, 0.3, 0.25)
    face = "peek" if T1 <= t < FORGET else "sleep"
    lx = lerp(150, 560, ease(pr(t, 3.0, 3.8))); ly = lerp(560, 1040, ease(pr(t, 3.0, 3.8)))
    if t > FORGET: lx += (t - FORGET) * 500; ly -= (t - FORGET) * 400
    trap(d, 540, 930, 330, 1.0, face, a, flyin=lambda: fly(d, lx, ly, 75, a, t, flap=(t < 3.8 or t > FORGET)))
    if T1 <= t < FORGET + 0.4:
        fa = a * (1 - pr(t, FORGET, FORGET + 0.4))
        bignum(d, t, 1, T1, a=fa)
        g = pr(t, T1, FORGET)
        d.arc(540, 330, 150, 150, -90, -90 + 360 * (1 - g), A(CYAN, fa), 12)
        d.text(540, 520, "30 秒内", 40, A(CYAN, fa))
    if t > FORGET: d.text(540, 330, "忘了", 110, A(MUTE, a * ease(pr(t, FORGET, FORGET + 0.3))), k=1)
    rings(d, 540, 1040, t, [T1], YEL, a, 200)

def s_rule2(t, d):
    a = win(t, 9.0, 12.0, 0.2, 0.1)
    op = snap_op(t, SNAP2)
    face = "peek" if t < T2[0] else "smug" if t < SNAP2 else "chomp" if t < SNAP2 + 0.5 else "happy"
    sx, sy = shake(t, 14 * pulse(t, [SNAP2], 5))
    trap(d, 540 + sx, 930 + sy, 330, op, face, a, flyin=lambda: fly(d, 560, 1030, 75, a, t, flap=False, scared=t > T2[1] - 0.2))
    rings(d, 540, 1040, t, T2, YEL, a, 200)
    flash(d, t, [SNAP2], YEL, 0.25)
    if t >= T2[1]: bignum(d, t, 2, T2[1])
    elif t >= T2[0]: bignum(d, t, 1, T2[0])

def s_count(t, d):
    a = win(t, 12.0, 19.5, 0.1, 0.05)
    p = pulse(t, [T3, T4], 7)
    rr = pr(t, RISER[0], RISER[1])
    sx, sy = shake(t, 10 * p + 4 + 10 * rr, 50)
    face = "smug" if t < T4 else "evil"
    trap(d, 540 + sx, 930 + sy, 330 * (1 + 0.05 * rr), 0.0, face, a, look=0.0)
    if t < T3: d.text(540, 330, "2", 230, A(YEL, a), k=1)
    elif t < T4:
        bignum(d, t, 3, T3); d.text(540, 520, "→ 开始制造消化酶", 44, A(DIGEST, a * ease(pr(t, T3 + 0.2, T3 + 0.5))))
    else:
        bignum(d, t, 4, T4, col=mix(YEL, RED, rr))
    if rr > 0: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.5 * rr))

def s_burst(t, d):
    a = win(t, BURST, 24.0, 0.01, 0.25)
    p = pulse(t, [BURST + i * BEAT for i in range(8)], 8)
    sx, sy = shake(t, 10 * p, 60)
    trap(d, 540 + sx, 950 + sy, 330, 0.0, "evil", a)
    for i in range(7):  # digestive juice drips
        u = ((t - BURST) * 0.9 + i * 0.37) % 1
        dx = 260 + i * 95
        d.ell(dx, lerp(960, 1180, u), 14, 22, A(DIGEST, a * (1 - u)))
    k = back(pr(t, BURST, BURST + 0.25))
    big = lerp(700, 260, ease(pr(t, BURST + 0.3, BURST + 1.0)))
    yy = lerp(900, 330, ease(pr(t, BURST + 0.3, BURST + 1.0)))
    d.text(540 + sx, yy, "5", int(big * (0.5 + 0.5 * k) * (1 + 0.05 * p)), A(YEL, a * 0.95), k=1)
    d.text(540, 560, "开饭！", 70, A(DIGEST, a * ease(pr(t, BURST + 0.9, BURST + 1.2))), k=1)
    if t < BURST + 0.12: d.rect(0, 0, OW, OH, fill=A(WHITE, 1 - pr(t, BURST, BURST + 0.12)))

def s_wind(t, d):
    a = win(t, 24.0, 30.0, 0.25, 0.25)
    face = "peek" if any(h <= t < h + 1.0 for h in WIND) else "sleep"
    trap(d, 540, 930, 300, 1.0, face, a)
    u = pr(t, WIND[0] - 0.6, WIND[0] + 0.4)
    for i in range(4):  # wind gust
        yy = 760 + i * 70; x0 = lerp(-300, 1200, u) - i * 60
        d.line([(x0, yy), (x0 + 260, yy - 10)], A(WHITE, a * 0.6 * (1 - abs(u - 0.5) * 2)), 6)
    dy = lerp(450, 1030, eio(pr(t, WIND[1] - 0.6, WIND[1])))
    if t < WIND[1] + 0.05: d.ell(560, dy, 18, 28, A(WATER, a))
    rings(d, 540, 1030, t, WIND, CYAN, a, 160)
    for h, lbl in zip(WIND, ("风", "雨滴")):
        if h <= t < h + 1.2:
            q = a * (1 - pr(t, h + 0.8, h + 1.2))
            bignum(d, t, 1, h, a=q); d.text(540, 520, lbl + "：只碰 1 下", 44, A(CYAN, q))
    if t > 28.0:
        d.text(540, 380, "不合", 130, A(MUTE, a * ease(pr(t, 28.0, 28.3))), k=1)
        for i in range(3):
            zu = ((t - 28) * 0.8 + i * 0.33) % 1
            d.text(820 + zu * 80, 640 - zu * 160, "z", int(40 + 30 * zu), A(WHITE, a * (1 - zu)), k=1)

def s_flood(t, d):
    a = win(t, FLOOD[0], FLOOD[1], 0.25, 0.25)
    n = 5 + int(pr(t, FLOOD[0], FLOOD[1] - 0.2) * 30)
    sx, sy = shake(t, 6, 55)
    trap(d, 400 + sx, 930 + sy, 260, 0.0, "evil", a)
    d.text(400, 330, str(n), 220, A(YEL, a), k=1)
    d.text(400, 500, "下", 44, A(WHITE, a))
    lvl = pr(t, FLOOD[0], FLOOD[1])
    d.rect(820, 560, 960, 1200, outline=A(WHITE, a), w=5, r=20)
    d.rect(826, 1194 - 620 * lvl, 954, 1194, fill=A(DIGEST, a), r=16)
    d.text(890, 1260, "消化液", 40, A(DIGEST, a))

def s_pump(t, d):
    a = win(t, PUMP[0], PUMP[1], 0.25, 0.25)
    trap(d, 540, 760, 300, 0.0, "happy", a)
    d.rect(500, 980, 580, 1360, fill=A(GREEN_D, a), r=20)
    for i in range(10):
        u = ((t - PUMP[0]) * 0.6 + i * 0.1) % 1
        yy = lerp(860, 1340, u)
        d.rect(525, yy - 14, 555, yy + 14, fill=A(WHITE, a * (1 - u)), r=4)
    d.text(780, 1100, "Na⁺", 70, A(WHITE, a), k=2)
    d.text(780, 1180, "盐分被吸走", 40, A(MUTE, a))
    d.text(540, 380, "吸收泵 开启", 84, A(CYAN, a * ease(pr(t, PUMP[0] + 0.2, PUMP[0] + 0.5))), k=1)

def s_end(t, d):
    a = ease(pr(t, OUTRO, OUTRO + 0.3)) * (1 - pr(t, DUR - 0.3, DUR))
    op = snap_op(t, LAST_SNAP)
    face = "wink" if 40.8 < t < 41.6 else ("chomp" if t >= LAST_SNAP else "open")
    trap(d, 540, 900, 320, op, face, a, look=0.0)
    d.text(540, 300, "你刚才", 80, A(WHITE, a), k=1)
    d.text(540, 420, "数到几了？", 100, A(YEL, a), k=1)
    d.text(540, 1500, "Böhm et al., Current Biology 26:286 (2016)", 30, A(MUTE, a), k=2)
    flash(d, t, [LAST_SNAP], YEL, 0.3)

SECS = [(0, 2.65, s_hook), (2.6, 9.0, s_rule1), (9.0, 12.0, s_rule2), (12.0, 19.5, s_count), (20.0, 24.0, s_burst),
        (24.0, 30.0, s_wind), (30.0, 35.0, s_flood), (35.0, 39.0, s_pump), (39.0, 45.0, s_end)]

HOOK_HITS = [HOOK_SNAP + i * BEAT for i in range(4)]
BURST_HITS = [BURST + i * BEAT for i in range(38)]

def frame(t):
    bg = BG
    if t < 2.5: bg = mix(BG, (20, 70, 30), pulse(t, HOOK_HITS, 5) * 0.9)
    elif BURST <= t < 24: bg = mix(BG, (20, 60, 28), pulse(t, BURST_HITS, 6) * 0.8)
    if SILENCE[0] <= t < SILENCE[1]: bg = (0, 0, 0)
    img = Image.new("RGB", (W, H), bg)
    d = D(img)
    for a, b, fn in SECS:
        if a <= t < b: fn(t, d)
    if not (SILENCE[0] <= t < SILENCE[1]):
        brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)

if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.1f}.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for i in range(i0, i1): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); p.wait()
