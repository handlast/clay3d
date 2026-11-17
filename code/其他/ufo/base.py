import math, random, sys, subprocess
from PIL import Image, ImageDraw, ImageFont


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
    if key not in fc: fc[key] = ImageFont.truetype(FONTS[k], max(2, int(size * S)))
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
    def circ(s, x, y, r, fill=None, outline=None, w=1):
        r = max(r, 0.5); s.d.ellipse((P(x - r), P(y - r), P(x + r), P(y + r)), fill=fill, outline=outline, width=max(1, int(P(w))))
    def ell(s, x, y, rx, ry, fill=None, outline=None, w=1):
        rx = max(abs(rx), 0.5); ry = max(abs(ry), 0.5); s.d.ellipse((P(x - rx), P(y - ry), P(x + rx), P(y + ry)), fill=fill, outline=outline, width=max(1, int(P(w))))
    def arc(s, x, y, rx, ry, a0, a1, fill, w):
        rx = max(abs(rx), 0.5); ry = max(abs(ry), 0.5); s.d.arc((P(x - rx), P(y - ry), P(x + rx), P(y + ry)), a0, a1, fill=fill, width=max(1, int(P(w))))
    def rect(s, x0, y0, x1, y1, fill=None, outline=None, w=1, r=0):
        if x1 - x0 < 1 or y1 - y0 < 1: return
        r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
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
