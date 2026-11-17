import math, random, sys, subprocess
from PIL import Image, ImageDraw, ImageFont
from cues import *

OW, OH, FPS = 1080, 1920, 30
S = 1.5
W, H = int(OW * S), int(OH * S)
FONTS = ["/workspace/work/tomato/NotoSansSC-Bold.otf", "/workspace/work/tomato/NotoSansSC-Black.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
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

# ---------- the tomato character ----------
def tomato(d, x, y, r, face="calm", a=1.0, sq=0.0, col=RED):
    rx, ry = r * 1.08 * (1 + sq * 0.12), r * 0.95 * (1 - sq * 0.12)
    d.ell(x, y + r * 0.05, rx, ry, A(mix(col, (0, 0, 0), 0.25), a))
    d.ell(x - r * 0.04, y, rx * 0.97, ry * 0.95, A(col, a))
    d.ell(x - r * 0.45, y - r * 0.45, r * 0.18, r * 0.11, A((255, 255, 255), 0.45 * a))
    cy = y - ry * 0.92
    for k in range(5):
        ang = -math.pi / 2 + k * 2 * math.pi / 5 + 0.3
        tip = (x + math.cos(ang) * r * 0.42, cy + math.sin(ang) * r * 0.22 + r * 0.08)
        pp = (math.sin(ang) * r * 0.07, -math.cos(ang) * r * 0.05)
        d.poly([(x + pp[0], cy + pp[1]), tip, (x - pp[0], cy - pp[1])], A(LEAF if k % 2 else LEAF_D, a))
    d.line([(x, cy), (x + r * 0.06, cy - r * 0.22)], A(LEAF_D, a), r * 0.08)
    ex, ey, er = r * 0.34, y - r * 0.12, r * 0.17
    if face == "scream":
        for s_ in (-1, 1):
            d.circ(x + s_ * ex, ey, er * 1.25, fill=A(WHITE, a)); d.circ(x + s_ * ex, ey, er * 0.38, fill=A(INK, a))
            d.line([(x + s_ * ex * 1.5, ey - er * 2.0), (x + s_ * ex * 0.45, ey - er * 1.45)], A(INK, a), r * 0.06)
        d.ell(x, y + r * 0.42, r * 0.3, r * 0.36, A(INK, a)); d.ell(x, y + r * 0.6, r * 0.18, r * 0.12, A(TONGUE, a))
    elif face == "thirsty":
        for s_ in (-1, 1):
            d.circ(x + s_ * ex, ey, er, fill=A(WHITE, a)); d.circ(x + s_ * ex, ey + er * 0.25, er * 0.45, fill=A(INK, a))
            d.rect(x + s_ * ex - er * 1.1, ey - er * 1.1, x + s_ * ex + er * 1.1, ey - er * 0.05, fill=A(col, a))
            d.line([(x + s_ * ex - er, ey - er * 0.05), (x + s_ * ex + er, ey - er * 0.05)], A(INK, a), r * 0.04)
        d.arc(x, y + r * 0.42, r * 0.2, r * 0.12, 200, 340, A(INK, a), r * 0.05)
        d.ell(x + r * 0.05, y + r * 0.42, r * 0.09, r * 0.13, A(TONGUE, a))
        d.ell(x + r * 0.78, y - r * 0.3, r * 0.08, r * 0.13, A(CYAN, a))
    elif face == "happy":
        for s_ in (-1, 1): d.arc(x + s_ * ex, ey + er * 0.4, er, er, 200, 340, A(INK, a), r * 0.06)
        d.arc(x, y + r * 0.2, r * 0.3, r * 0.28, 20, 160, A(INK, a), r * 0.06)
        for s_ in (-1, 1): d.ell(x + s_ * r * 0.6, y + r * 0.18, r * 0.12, r * 0.07, A(RED_L, 0.7 * a))
    elif face == "dizzy":
        for s_ in (-1, 1):
            cx_ = x + s_ * ex
            d.line([(cx_ - er * .8, ey - er * .8), (cx_ + er * .8, ey + er * .8)], A(INK, a), r * 0.05)
            d.line([(cx_ - er * .8, ey + er * .8), (cx_ + er * .8, ey - er * .8)], A(INK, a), r * 0.05)
        d.line([(x - r * 0.2, y + r * 0.4), (x - r * 0.07, y + r * 0.34), (x + r * 0.07, y + r * 0.42), (x + r * 0.2, y + r * 0.36)], A(INK, a), r * 0.05)
    else:  # calm / worried
        for s_ in (-1, 1): d.circ(x + s_ * ex, ey, er * 0.55, fill=A(INK, a))
        d.arc(x, y + r * 0.34, r * 0.16, r * 0.1, 20, 160, A(INK, a), r * 0.05)

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

SUBS = [(0.0, 2.6, "番茄缺水时，真的会“尖叫”。"),
        (2.6, 6.0, "只是声音太高，人耳听不见。"),
        (6.0, 9.0, "2023 年，以色列特拉维夫大学，把番茄放进隔音箱。"),
        (9.0, 12.0, "停水几天后，麦克风录到了它的叫声。"),
        (12.0, 17.0, "缺水的番茄，平均每小时叫 35 次。"),
        (17.0, 20.0, "浇足水的番茄，每小时不到 1 次。"),
        (20.0, 23.0, "只放土的空花盆，录了 500 多小时，一声没有。"),
        (23.0, 27.0, "离它 10 厘米，音量和人正常说话差不多。"),
        (27.0, 29.5, "把频率降到人耳听得见——"),
        (30.0, 36.0, "就是这样：啪、啪、啪（示意）。"),
        (36.0, 38.5, "声音可能来自茎里的“水管”："),
        (38.5, 41.0, "缺水时，气泡在里面形成、破裂。"),
        (41.0, 43.5, "停水后的 4–5 天，它越叫越频繁；"),
        (43.5, 46.0, "等快要干透了，反而安静下来。"),
        (46.0, 51.0, "3 到 5 米外，老鼠、飞蛾这类动物可能听得见。"),
        (51.0, 56.0, "AI 只听声音，就能大致分辨它是渴了，还是被剪断了。")]

def subs(t, d):
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.15)) * (1 - pr(t, b - 0.12, b))
            lines = wrap(d, s, 58)
            for i, ln in enumerate(lines):
                y = 1440 + (i - (len(lines) - 1) / 2) * 84
                d.rect(540 - d.tlen(ln, 58) / 2 - 22, y - 44, 540 + d.tlen(ln, 58) / 2 + 22, y + 44, fill=A((0, 0, 0), 0.45 * al), r=14)
                d.text(540, y, ln, 58, A(WHITE, al))

def brand(t, d):
    d.rect(50, 80, 300, 128, fill=A(WHITE, 0.92), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(BG, 1))

BURST_HITS = [BURST + i * BEAT for i in range(52)]
HOOK_HITS = [i * BEAT for i in range(5)]

def s_hook(t, d):
    a = 1 - pr(t, 2.45, 2.6)
    p = pulse(t, HOOK_HITS, 7)
    sh = 14 * math.sin(t * 90) * (1 - pr(t, 0, 2.5))
    rings(d, 540, 820, t, HOOK_HITS, YEL, a, 520)
    r = 250 * back(pr(t, 0, 0.25)) * (1 + 0.06 * p)
    tomato(d, 540 + sh, 820, r, "scream", a, sq=-p)
    for i in range(10):
        ang = i * 0.628 + 0.3; rr = 340 + 60 * p
        x0, y0 = 540 + math.cos(ang) * rr, 820 + math.sin(ang) * rr * 0.9
        d.line([(x0, y0), (x0 + math.cos(ang) * 70, y0 + math.sin(ang) * 63)], A(YEL, a * (0.5 + 0.5 * p)), 10)
    k = back(pr(t, 0.05, 0.3))
    d.text(540 + sh * 0.6, 330, "番茄在尖叫", int(140 * (0.7 + 0.3 * k)), A(YEL, a), k=1)

def s_freq(t, d):
    a = win(t, 2.6, 6.0, 0.25, 0.3)
    tomato(d, 540, 650, 170, "thirsty", a)
    x0, x1, y = 120, 960, 1080
    def X(khz): return lerp(x0, x1, khz / 100)
    d.line([(x0, y), (x1, y)], A(MUTE, a), 4)
    for k in (0, 20, 50, 100):
        d.line([(X(k), y - 12), (X(k), y + 12)], A(MUTE, a), 4); d.text(X(k), y + 45, f"{k}", 32, A(MUTE, a), k=2)
    d.text(x1, y + 95, "千赫 kHz", 28, A(MUTE, a), anchor="rm")
    d.rect(X(0), y - 90, X(20), y - 20, fill=A(WHITE, 0.18 * a), r=10); d.text(X(10), y - 55, "人耳", 34, A(WHITE, a))
    g = ease(pr(t, 3.2, 3.8))
    d.rect(X(20), y - 90, X(20) + (X(100) - X(20)) * g, y - 20, fill=A(CYAN, 0.35 * a), r=10)
    d.text(X(60), y - 55, "番茄的叫声  20–100", 34, A(CYAN, a * g))
    d.text(540, 880, "听不见", 90, A(WHITE, a * ease(pr(t, 4.0, 4.4))), k=1)

def s_box(t, d):
    a = win(t, 6.0, 12.0)
    d.rect(170, 400, 910, 1180, fill=A(BG2, a), outline=A(MUTE, a), w=4, r=30)
    for i in range(9):
        x = 210 + i * 80
        d.poly([(x, 430), (x + 40, 470), (x + 80, 430)], A((60, 66, 84), a))
        d.poly([(x, 1150), (x + 40, 1110), (x + 80, 1150)], A((60, 66, 84), a))
    hits = [9.5, 10.4, 10.9, 11.5]
    face = "thirsty" if t > 8.5 else "calm"
    tomato(d, 540, 820, 150, face, a, sq=-0.5 * pulse(t, hits, 10))
    d.rect(520, 980, 560, 1110, fill=A(LEAF_D, a)); d.rect(440, 1060, 640, 1130, fill=A((120, 84, 60), a), r=10)
    for s_ in (-1, 1):
        mx = 540 + s_ * 290
        d.rect(mx - 18, 640, mx + 18, 760, fill=A(MUTE, a), r=12); d.circ(mx, 640, 26, fill=A(WHITE, a))
    rings(d, 540, 800, t, hits, CYAN, a, 300)
    d.text(540, 340, "隔音箱 + 超声波麦克风", 38, A(MUTE, a))

def s_count(t, d):
    a = win(t, 12.0, 17.0)
    n = sum(1 for h in COUNTER if h <= t)
    p = pulse(t, COUNTER, 14)
    tomato(d, 540, 560, 140, "scream" if p > 0.4 else "thirsty", a, sq=-p * 0.6)
    rings(d, 540, 560, t, COUNTER, CYAN, a * 0.6, 240)
    d.text(540, 960, f"{n}", int(260 * (1 + 0.05 * p)), A(YEL, a), k=1)
    d.text(540, 1150, "次 / 小时", 48, A(WHITE, a))
    d.text(540, 1220, "缺水的番茄", 34, A(MUTE, a))

def s_ctrl(t, d):
    a = win(t, 17.0, 23.0)
    la = ease(pr(t, 17.0, 17.3)); ra = ease(pr(t, 20.0, 20.3))
    tomato(d, 300, 650, 120, "happy", a * la)
    d.ell(300, 850, 110, 22, A(WATER, 0.6 * a * la))
    d.text(300, 980, "< 1", 120, A(WHITE, a * la), k=1); d.text(300, 1090, "次 / 小时", 34, A(MUTE, a * la))
    d.poly([(700, 600), (900, 600), (870, 800), (730, 800)], A((150, 100, 70), a * ra)); d.rect(690, 580, 910, 610, fill=A((170, 116, 82), a * ra), r=8)
    d.text(800, 980, "0", 120, A(WHITE, a * ra), k=1); d.text(800, 1090, "次 / 500+ 小时", 34, A(MUTE, a * ra))
    d.text(300, 470, "浇足水", 40, A(WATER, a * la)); d.text(800, 470, "只有土", 40, A((200, 150, 110), a * ra))

def s_db(t, d):
    a = win(t, 23.0, 27.2)
    tomato(d, 300, 700, 130, "scream", a, sq=-0.4 * pulse(t, [23.0 + i * 0.75 for i in range(6)], 8))
    d.line([(450, 700), (700, 700)], A(MUTE, a), 4); d.text(575, 660, "10 厘米", 32, A(MUTE, a))
    d.circ(800, 700, 70, fill=A((230, 200, 170), a)); d.circ(780, 690, 8, fill=A(INK, a)); d.ell(740, 705, 14, 28, A((215, 182, 150), a))
    d.text(540, 1000, "61.6 分贝", 130, A(YEL, a * ease(pr(t, 23.3, 23.7))), k=1)
    d.text(540, 1140, "≈ 人正常说话的音量", 44, A(WHITE, a * ease(pr(t, 24.0, 24.4))))

def s_drop(t, d):
    a = win(t, 27.0, 29.5, 0.25, 0.08)
    k = eio(pr(t, 27.3, 29.3))
    tomato(d, 540, 640, 150 * (1 + 0.15 * k), "calm", a, sq=k * 0.8)
    x0, x1, y = 120, 960, 1050
    d.line([(x0, y), (x1, y)], A(MUTE, a), 4)
    d.rect(x0, y - 70, lerp(x0, x1, 0.2), y - 10, fill=A(WHITE, 0.18 * a), r=10)
    cx = lerp(lerp(x0, x1, 0.5), lerp(x0, x1, 0.1), k)
    d.rect(cx - 70, y - 70, cx + 70, y - 10, fill=A(CYAN, 0.8 * a), r=10)
    d.text(cx, y - 120, "↓", 70, A(CYAN, a), k=2)

def s_burst(t, d):
    a = win(t, BURST, 36.0, 0.01, 0.3)
    p = pulse(t, BURST_HITS, 8)
    if t < BURST + 0.12: d.rect(0, 0, OW, OH, fill=A(WHITE, 1 - pr(t, BURST, BURST + 0.12)))
    clicks = [BURST + i * 0.125 for i in range(48) if i % 16 in (2, 3, 6, 9, 11, 14)]
    for i, x in enumerate((230, 540, 850)):
        q = pulse(t, BURST_HITS[i::3], 9)
        tomato(d, x, 760 - 40 * q, 130, "scream", a, sq=-q)
    wave(d, 60, 1020, 1080, 160, t, clicks, a, YEL, 7)
    k = back(pr(t, BURST, BURST + 0.25))
    d.text(540 + 6 * math.sin(t * 70) * p, 380, "啪！啪！啪！", int(130 * (0.7 + 0.3 * k) * (1 + 0.05 * p)), A(YEL, a), k=1)
    d.text(540, 1230, "超声波降频 · 示意音效", 30, A(MUTE, a))

def s_xylem(t, d):
    a = win(t, 36.0, 41.0)
    d.text(540, 400, "茎里的导管", 60, A(WHITE, a), k=1)
    d.rect(80, 640, 1000, 900, fill=A((60, 120, 70), a), r=40)
    d.rect(80, 690, 1000, 850, fill=A(WATER, 0.55 * a), r=30)
    for i, h in enumerate(BUBBLES):
        bx = 170 + i * 92
        grow = ease(pr(t, h - 0.3, h + 0.2)); pop = pr(t, h + 0.25, h + 0.45)
        if pop < 1 and grow > 0:
            d.circ(bx, 770, 38 * grow * (1 + pop), fill=A(WHITE, a * 0.85 * (1 - pop)))
        if 0 < pop < 1:
            for j in range(8):
                ang = j * 0.785
                d.line([(bx + math.cos(ang) * 45, 770 + math.sin(ang) * 45), (bx + math.cos(ang) * (45 + 50 * pop), 770 + math.sin(ang) * (45 + 50 * pop))], A(YEL, a * (1 - pop)), 6)
    d.text(540, 1010, "气泡 形成 → 破裂", 48, A(CYAN, a))
    d.text(540, 1090, "（研究者推测的来源：气穴现象）", 32, A(MUTE, a))

def s_curve(t, d):
    a = win(t, 41.0, 46.0)
    x0, x1, y0 = 140, 940, 1130
    d.line([(x0, y0), (x1, y0)], A(MUTE, a), 4); d.text((x0 + x1) / 2, y0 + 50, "停水后的天数 →", 34, A(MUTE, a))
    d.text(x0, 470, "每天叫的次数", 34, A(MUTE, a), anchor="lm")
    vals = [0.05, 0.3, 0.6, 0.9, 1.0, 0.8, 0.5, 0.25, 0.1]
    g = pr(t, 41.2, 45.0)
    for i, v in enumerate(vals):
        if i / 8 > g + 0.02: break
        bx = lerp(x0 + 50, x1 - 50, i / 8)
        d.rect(bx - 32, y0 - 520 * v, bx + 32, y0, fill=A(mix(CYAN, YEL, v), a), r=8)
    for i, face in ((0, "calm"), (4, "scream"), (8, "dizzy")):
        if i / 8 <= g + 0.02:
            bx = lerp(x0 + 50, x1 - 50, i / 8)
            tomato(d, bx, y0 - 520 * vals[i] - 90, 62, face, a, col=RED if i < 8 else (170, 110, 80))

def mouse(d, x, y, a):
    d.ell(x, y, 110, 60, A((170, 170, 180), a)); d.circ(x + 90, y - 50, 40, fill=A((190, 190, 200), a)); d.circ(x + 90, y - 50, 24, fill=A((240, 170, 180), a))
    d.circ(x + 120, y - 10, 9, fill=A(INK, a)); d.line([(x - 110, y + 10), (x - 190, y - 30), (x - 240, y + 10)], A((170, 170, 180), a), 7)
def moth(d, x, y, a, t):
    f = 0.85 + 0.15 * math.sin(t * 25)
    for s_ in (-1, 1):
        d.ell(x + s_ * 60 * f, y - 25, 62 * f, 50, A((200, 180, 140), a)); d.ell(x + s_ * 45 * f, y + 35, 40 * f, 32, A((180, 160, 120), a))
    d.ell(x, y, 16, 60, A((120, 100, 80), a))

def s_animals(t, d):
    a = win(t, 46.0, 51.0)
    tomato(d, 200, 760, 110, "scream", a, sq=-0.4 * pulse(t, [46 + i * 0.5 for i in range(10)], 10))
    rings(d, 200, 760, t, [46 + i * 1.0 for i in range(5)], CYAN, a * 0.7, 700)
    mouse(d, 790, 640, a * ease(pr(t, 46.3, 46.7))); moth(d, 800, 930, a * ease(pr(t, 46.8, 47.2)), t)
    d.line([(330, 1130), (900, 1130)], A(MUTE, a), 4)
    for xx in (330, 900): d.line([(xx, 1110), (xx, 1150)], A(MUTE, a), 4)
    d.text(615, 1200, "3–5 米", 56, A(YEL, a), k=1)

def s_ai(t, d):
    a = win(t, 51.0, 56.0)
    hits = [51.2 + i * 0.5 for i in range(9)]
    wave(d, 80, 420, 760, 90, t, hits, a, CYAN, 5)
    d.line([(430, 760), (470, 760)], A(MUTE, a), 4)
    d.rect(480, 660, 640, 860, fill=A(BG2, a), outline=A(CYAN, a), w=4, r=24); d.text(560, 760, "AI", 64, A(CYAN, a), k=2)
    k1 = ease(pr(t, 52.5, 52.9)); k2 = ease(pr(t, 53.3, 53.7))
    d.line([(650, 720), (720, 620)], A(MUTE, a * k1), 4); d.line([(650, 800), (720, 900)], A(MUTE, a * k2), 4)
    tomato(d, 820, 590, 70, "thirsty", a * k1); d.text(820, 700, "渴了", 40, A(WHITE, a * k1))
    tomato(d, 820, 900, 70, "dizzy", a * k2); d.line([(760, 960), (880, 960)], A(YEL, a * k2), 6); d.text(820, 1010, "被剪断", 40, A(WHITE, a * k2))

def s_end(t, d):
    a = ease(pr(t, OUTRO, OUTRO + 0.3)) * (1 - pr(t, DUR - 0.4, DUR))
    blink = t > LAST_CLICK and t < LAST_CLICK + 0.15
    for i in range(5):
        u = ((t - OUTRO) * 1.2 + i * 0.2) % 1
        d.ell(540 + (i - 2) * 30, lerp(300, 520, u), 14, 22, A(WATER, a * (1 - u)))
    tomato(d, 540, 700, 170, "scream" if blink else "happy", a, sq=-0.5 if blink else 0)
    d.text(540, 1030, "下次路过番茄，", 72, A(WHITE, a), k=1)
    d.text(540, 1130, "它可能正在喊渴。", 72, A(YEL, a), k=1)
    d.text(540, 1330, "Khait et al., Cell 186:1328–1336 (2023)", 28, A(MUTE, a), k=2)

SECS = [(0, 2.65, s_hook), (2.6, 6.0, s_freq), (6, 12, s_box), (12, 17, s_count), (17, 23, s_ctrl), (23, 27.2, s_db),
        (27, 29.5, s_drop), (30, 36, s_burst), (36, 41, s_xylem), (41, 46, s_curve), (46, 51, s_animals), (51, 56, s_ai), (56, 60, s_end)]

def frame(t):
    bg = BG
    if t < 2.5: bg = mix(BG, (90, 20, 24), pulse(t, HOOK_HITS, 5) * 0.9)
    elif BURST <= t < 36: bg = mix(BG, (70, 18, 22), pulse(t, BURST_HITS, 6) * 0.8)
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
