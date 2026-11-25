# York film — drawing base: supersampled Pillow canvas, rim-light shapes (NO dark outlines), fog, glow, splines.
import math, random, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import easing as E

OW, OH, FPS = 1080, 1920, 30
import os
S = float(os.environ.get("MS", "1.5"))
W, H = int(OW * S), int(OH * S)
FONTS = ["/workspace/work/tomato/NotoSansSC-Bold.otf", "/workspace/work/tomato/NotoSansSC-Black.otf"]
WHITE = (242, 240, 232); AMBER = (255, 170, 60); AMBER_L = (255, 214, 140); COLD = (150, 196, 210)
NIGHT0 = (10, 16, 22); NIGHT1 = (28, 44, 50); FOG = (120, 146, 150)
FELD = (58, 68, 64); FELD_L = (84, 96, 90); HELM = (66, 76, 72)
OD = (78, 74, 48); OD_L = (112, 106, 70); BRODIE = (84, 88, 58)
SKIN = (222, 158, 112); SKIN_D = (112, 70, 56); SKIN_M = (176, 116, 86)
HAIR = (150, 66, 34); INK = (26, 18, 18)
fc = {}
def F(size, k=0):
    key = (int(size * S), k)
    if key not in fc: fc[key] = ImageFont.truetype(FONTS[k], max(2, key[0]))
    return fc[key]
def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return x * x * (3 - 2 * x)
def pr(t, a, b): return cl((t - a) / (b - a)) if b != a else float(t >= a)
def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k): return tuple(int(lerp(a, b, cl(k))) for a, b in zip(c1, c2))
def A(c, a): return tuple(c[:3]) + (int(255 * cl(a)),)
def P(x): return x * S
def win(t, a, b, fi=0.3, fo=0.3): return ease(pr(t, a, a + fi)) * (1 - eio(pr(t, b - fo, b)))
def pulse(t, times, dec=6.0):
    v = 0
    for h in times:
        if h <= t: v = max(v, math.exp(-(t - h) * dec))
    return v
def hsh(i, s=0): return E._hash01(int(i), s)

def spline(pts, closed=True, n=10):
    """Catmull-Rom through control points -> dense polygon (smooth organic shapes)."""
    m = len(pts); out = []
    rng_ = range(m) if closed else range(m - 1)
    for i in rng_:
        p0 = pts[(i - 1) % m] if closed else pts[max(i - 1, 0)]
        p1 = pts[i]; p2 = pts[(i + 1) % m] if closed else pts[i + 1]
        p3 = pts[(i + 2) % m] if closed else pts[min(i + 2, m - 1)]
        for k in range(n):
            u = k / n; u2 = u * u; u3 = u2 * u
            x = 0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * u + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * u2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * u3)
            y = 0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * u + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * u2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * u3)
            out.append((x, y))
    if not closed: out.append(pts[-1])
    return out
def xf(pts, x, y, sc, sx=None, rot=0.0):
    sx = sc if sx is None else sx; c, s_ = math.cos(rot), math.sin(rot)
    return [(x + (px * c - py * s_) * sx, y + (px * s_ + py * c) * sc) for px, py in pts]

class D:
    def __init__(s, img, scale=S): s.img = img; s.d = ImageDraw.Draw(img, "RGBA"); s.k = scale
    def p(s, v): return v * s.k
    def line(s, pts, fill, w): s.d.line([(s.p(x), s.p(y)) for x, y in pts], fill=fill, width=max(1, int(s.p(w))), joint="curve")
    def poly(s, pts, fill): s.d.polygon([(s.p(x), s.p(y)) for x, y in pts], fill=fill)
    def circ(s, x, y, r, fill=None, outline=None, w=1):
        r = max(r, 0.3); s.d.ellipse((s.p(x - r), s.p(y - r), s.p(x + r), s.p(y + r)), fill=fill, outline=outline, width=max(1, int(s.p(w))))
    def ell(s, x, y, rx, ry, fill=None):
        rx = max(abs(rx), 0.3); ry = max(abs(ry), 0.3); s.d.ellipse((s.p(x - rx), s.p(y - ry), s.p(x + rx), s.p(y + ry)), fill=fill)
    def rect(s, x0, y0, x1, y1, fill=None, r=0):
        if x1 - x0 < 0.5 or y1 - y0 < 0.5: return
        r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
        s.d.rounded_rectangle((s.p(x0), s.p(y0), s.p(x1), s.p(y1)), radius=s.p(r), fill=fill)
    def text(s, x, y, t, size, fill, anchor="mm", k=1):
        al = fill[3] if len(fill) > 3 else 255
        if al <= 2: return
        fnt = F(size, k); X, Y = s.p(x), s.p(y)
        if al >= 253: s.d.text((X, Y), t, font=fnt, fill=fill[:3], anchor=anchor); return
        b = [int(v) for v in s.d.textbbox((X, Y), t, font=fnt, anchor=anchor)]; b[2] += 2; b[3] += 2
        m = Image.new("L", (b[2] - b[0], b[3] - b[1]), 0)
        ImageDraw.Draw(m).text((X - b[0], Y - b[1]), t, font=fnt, fill=al, anchor=anchor)
        s.img.paste(fill[:3], tuple(b), m)
    def tlen(s, t, size, k=1): return s.d.textlength(t, font=F(size, k)) / S

def rimpoly(d, pts, body, rim, dx, dy, a=1.0):
    """Rim light without outline: draw shape in rim colour, then the body shifted away from the light."""
    d.poly(pts, A(rim, a)); d.poly([(x + dx, y + dy) for x, y in pts], A(body, a))

@functools.lru_cache(maxsize=16)
def vgrad(top, bot, w=W, h=H, mid=None):
    y = np.linspace(0, 1, h)[:, None, None]
    a = np.array(top, np.float32); b = np.array(bot, np.float32)
    if mid is None: c = a + (b - a) * y
    else:
        m = np.array(mid[1], np.float32); p = mid[0]
        c = np.where(y < p, a + (m - a) * (y / p), m + (b - m) * ((y - p) / (1 - p)))
    return Image.fromarray(np.repeat(c, w, 1).astype(np.uint8), "RGB")

@functools.lru_cache(maxsize=4)
def _fogtex(seed):
    rng = np.random.default_rng(seed); h, w = 300, 340; acc = np.zeros((h, w), np.float32)
    for oc, amp in ((6, 1.0), (12, 0.5), (24, 0.25), (48, 0.12)):
        sm = rng.random((oc, int(oc * w / h) + 1)).astype(np.float32)
        im = Image.fromarray((sm * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        acc += amp * np.asarray(im, np.float32) / 255
    acc = (acc - acc.min()) / (acc.max() - acc.min())
    acc = np.concatenate([acc, acc[:, ::-1]], 1)  # seamless horizontally
    return acc
@functools.lru_cache(maxsize=8)
def _ymask(y0, y1, soft, h=H):
    y = np.linspace(0, OH, h)
    return np.clip(np.minimum((y - y0) / soft + 1, (y1 - y) / soft + 1), 0, 1).astype(np.float32)[:, None]
def fog(img, t, col=FOG, amt=0.6, speed=12.0, y0=0, y1=OH, soft=300, seed=1, scale=1.0, contrast=1.6):
    """Drifting volumetric fog band (continuous scroll; no per-frame randomness)."""
    tex = _fogtex(seed); th, tw = tex.shape
    lw, lh = int(270 / scale), 480
    ox = (t * speed * 0.25 / scale) % (tw - lw - 1); oy = int(th / 2 - lh / 2) if lh < th else 0
    i0 = int(ox); fr = ox - i0
    sub = tex[:, i0:i0 + lw + 1]; sub = sub[:, :-1] * (1 - fr) + sub[:, 1:] * fr
    sub = Image.fromarray((np.clip((sub - 0.5) * contrast + 0.5, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    m = np.asarray(sub, np.float32) / 255 * _ymask(y0, y1, soft) * amt
    mask = Image.fromarray(np.clip(m * 255, 0, 255).astype(np.uint8), "L")
    img.paste(col, (0, 0, W, H), mask)

def glow(img, draw_fn, blur=40, gain=1.0):
    """Additive bloom: draw_fn(D) on a 1/4 res black layer, blur, screen onto img."""
    q = 4; lay = Image.new("RGB", (W // q, H // q), (0, 0, 0)); draw_fn(D(lay, S / q))
    lay = lay.filter(ImageFilter.GaussianBlur(blur / q)).resize((W, H), Image.BILINEAR)
    if gain != 1.0: lay = Image.eval(lay, lambda v: min(255, int(v * gain)))
    img.paste(ImageChops.screen(img, lay))
def soft_shape(img, draw_fn, blur=8, alpha=1.0):
    """Soft-edged (blurred) layer composited over: for light pools, haze, soft shadows."""
    lay = Image.new("RGBA", (W // 2, H // 2), (0, 0, 0, 0)); draw_fn(D(lay, S / 2))
    lay = lay.filter(ImageFilter.GaussianBlur(blur / 2)).resize((W, H), Image.BILINEAR)
    if alpha < 1: lay.putalpha(Image.eval(lay.getchannel("A"), lambda v: int(v * alpha)))
    img.paste(lay, (0, 0), lay)
