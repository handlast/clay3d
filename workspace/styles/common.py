# 动物打工人 画风样张 · 公用：字体、品牌胶囊、字幕、程序化猕猴（primitives，可被任意画风渲染）
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1920
FB = "/workspace/work/tomato/NotoSansSC-Bold.otf"
FK = "/workspace/work/tomato/NotoSansSC-Black.otf"
_fc = {}
def font(sz, black=False):
    k = (sz, black)
    if k not in _fc: _fc[k] = ImageFont.truetype(FK if black else FB, sz)
    return _fc[k]
def tlen(s, sz, black=False): return font(sz, black).getlength(s)

SUB = ["有的猴爱看吵架，", "有的猴爱看谁和谁是好朋友"]

def brand(img, dark_text=(30, 24, 40), pill=(255, 255, 255, 235), title_col=(255, 255, 255), title_bg=(15, 12, 26, 110)):
    """顶部「Vibe 知识大赏」胶囊 + 小片名"""
    d = ImageDraw.Draw(img, "RGBA")
    s = "Vibe 知识大赏"; w = tlen(s, 30, True) + 52
    d.rounded_rectangle((540 - w / 2, 120, 540 + w / 2, 174), radius=27, fill=pill)
    d.text((540, 147), s, font=font(30, True), fill=dark_text, anchor="mm")
    s2 = "动物打工人 No.01"; w2 = tlen(s2, 26) + 36
    if title_bg: d.rounded_rectangle((540 - w2 / 2, 186, 540 + w2 / 2, 226), radius=20, fill=title_bg)
    d.text((540, 206), s2, font=font(26), fill=title_col, anchor="mm")

def subtitle(img, lines=SUB, sz=54, box=(6, 14, 26, 210), col=(255, 255, 255), hl=None, hlcol=(255, 205, 80), radius=22, frame=None):
    """字幕：最后一行中心 y=1350，深色底；hl=要高亮的词"""
    d = ImageDraw.Draw(img, "RGBA")
    n = len(lines); y0 = 1350 - (n - 1) * 70
    w = max(tlen(x, sz) for x in lines) + 44
    bb = (540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 70 + 46)
    d.rounded_rectangle(bb, radius=radius, fill=box)
    if frame: d.rounded_rectangle(bb, radius=radius, outline=frame, width=6)
    for i, x in enumerate(lines):
        yy = y0 + i * 70; xx = 540 - tlen(x, sz) / 2
        segs = [(x, col)]
        if hl:
            for h in hl:
                if h in x:
                    j = x.index(h); segs = [(x[:j], col), (h, hlcol), (x[j + len(h):], col)]; break
        for s, c in segs:
            if s: d.text((xx, yy), s, font=font(sz), fill=c, anchor="lm"); xx += tlen(s, sz)
    return bb

# ---------- 猕猴：头半径=1 单位，(0,0)=头中心 ----------
# role → 颜色由各画风调色板决定
PAL_DEFAULT = dict(fur=(168, 116, 74), fur_dark=(132, 86, 52), fur_light=(214, 176, 132), face=(246, 168, 160),
                   skin=(236, 150, 140), blush=(255, 128, 140), ink=(62, 36, 30), white=(255, 255, 255), mouth=(150, 50, 60))

def monkey_prims(pose="sit", expr="look", lookx=0.0, arm_t=0.0):
    P = []
    E = lambda b, r, **k: P.append(dict(k="e", g=b, r=r, **k))
    L = lambda pts, r, w, **k: P.append(dict(k="l", g=pts, r=r, w=w, **k))
    C = lambda x, y, rr, r, **k: P.append(dict(k="e", g=(x - rr, y - rr, x + rr, y + rr), r=r, **k))
    grp = "body"
    if pose != "peek":
        E((-1.25, 1.95, -0.6, 2.3), "fur_dark", grp=grp)                  # 短尾（猕猴关键特征）
        if pose == "angry":                                               # 举起的手臂（身体后面）
            for sx in (-1, 1):
                L([(sx * 0.6, 1.05), (sx * 1.05, 0.55), (sx * 1.3, 0.05)], "fur", 0.34, grp=grp)
                C(sx * 1.3, 0.0, 0.2, "skin", grp=grp)
        E((-0.85, 0.62, 0.85, 2.35), "fur", grp=grp)
        E((-0.5, 0.98, 0.5, 2.2), "fur_light", grp=grp)
        E((-0.85, 2.05, -0.22, 2.45), "skin", grp=grp); E((0.22, 2.05, 0.85, 2.45), "skin", grp=grp)
        if pose == "sit":
            for sx in (-1, 1):
                L([(sx * 0.68, 1.0), (sx * 0.72, 1.55), (sx * 0.45, 1.95)], "fur", 0.32, grp=grp); C(sx * 0.42, 1.98, 0.17, "skin", grp=grp)
        if pose == "groom":
            L([(-0.68, 1.0), (-0.72, 1.55), (-0.45, 1.95)], "fur", 0.32, grp=grp); C(-0.42, 1.98, 0.17, "skin", grp=grp)
            hx, hy = 1.55 + 0.12 * math.sin(arm_t), 1.05 - 0.1 * math.cos(arm_t)
            L([(0.62, 1.0), (1.15, 1.3), (hx, hy)], "fur", 0.32, grp=grp); C(hx, hy, 0.19, "skin", grp=grp)
    grp = "head"
    if pose == "peek":   # 扒着隔板的两只手（画在隔板之前由场景控制顺序：grp=hands）
        for sx in (-1, 1):
            E((sx * 0.78 - 0.3, 0.98, sx * 0.78 + 0.3, 1.28), "skin", grp="hands")
    for sx in (-1, 1):
        C(sx * 0.98, -0.02, 0.3, "fur_dark", grp=grp); C(sx * 0.98, -0.02, 0.16, "skin", grp=grp)
    E((-1.0, -0.94, 1.0, 0.95), "fur", grp=grp)
    E((-0.6, -1.02, 0.6, -0.55), "fur_dark", grp=grp)                    # 头顶毛冠
    grp = "face"
    C(-0.33, -0.02, 0.41, "face", grp=grp); C(0.33, -0.02, 0.41, "face", grp=grp)
    E((-0.44, 0.02, 0.44, 0.8), "face", grp=grp)                           # 粉脸（猕猴关键特征）
    C(-0.55, 0.38, 0.13, "blush", grp=grp); C(0.55, 0.38, 0.13, "blush", grp=grp)
    lx = lookx * 0.07
    if expr in ("look", "wow"):
        rr = 0.13 if expr == "look" else 0.16
        for sx in (-1, 1):
            C(sx * 0.3 + lx, 0.0, rr, "ink", grp=grp); C(sx * 0.3 + lx - rr * 0.35, -rr * 0.4, rr * 0.38, "white", grp=grp)
            if expr == "wow": C(sx * 0.3 + lx + rr * 0.4, rr * 0.4, rr * 0.16, "white", grp=grp)
    elif expr == "happy":
        for sx in (-1, 1):
            L([(sx * 0.3 - 0.14, 0.04), (sx * 0.3, -0.08), (sx * 0.3 + 0.14, 0.04)], "ink", 0.07, grp=grp)
    elif expr == "angry":
        for sx in (-1, 1):
            C(sx * 0.3 + lx, 0.03, 0.11, "ink", grp=grp)
            L([(sx * 0.48, -0.26), (sx * 0.14, -0.12)], "ink", 0.08, grp=grp)
    C(-0.07, 0.3, 0.04, "ink", grp=grp); C(0.07, 0.3, 0.04, "ink", grp=grp)
    if expr == "angry":
        E((-0.22, 0.42, 0.22, 0.72), "mouth", grp=grp); E((-0.16, 0.42, 0.16, 0.52), "white", grp=grp)
    elif expr == "wow":
        E((-0.09, 0.47, 0.09, 0.64), "mouth", grp=grp)
    else:
        L([(-0.14, 0.5), (0.0, 0.58), (0.14, 0.5)], "ink", 0.06, grp=grp)
    return P

def draw_prims(d, P, x, y, s, flip=1, pal=None, k=1.0, groups=None, col_fn=None):
    """在 ImageDraw d 上画；k=画布相对 1080 宽的缩放倍数（超采样或低分辨率）"""
    pal = pal or PAL_DEFAULT
    def tx(px, py): return ((x + flip * px * s) * k, (y + py * s) * k)
    for p in P:
        if groups and p.get("grp") not in groups: continue
        c = pal[p["r"]]
        if col_fn: c = col_fn(p, c)
        if p["k"] == "e":
            x0, y0, x1, y1 = p["g"]
            a, b = tx(x0, y0), tx(x1, y1)
            d.ellipse((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), fill=c)
        else:
            pts = [tx(*q) for q in p["g"]]; w = max(1, int(round(p["w"] * s * k)))
            d.line(pts, fill=c, width=w, joint="curve")
            for q in (pts[0], pts[-1]):
                r = w / 2; d.ellipse((q[0] - r, q[1] - r, q[0] + r, q[1] + r), fill=c)

def heart(d, x, y, r, col, k=1.0):
    x, y, r = x * k, y * k, r * k
    d.ellipse((x - r, y - r * 0.55 - r * 0.55, x, y - r * 0.55 + r * 0.55), fill=col)
    d.ellipse((x, y - r * 1.1, x + r, y), fill=col)
    d.polygon([(x - r * 0.97, y - r * 0.4), (x + r * 0.97, y - r * 0.4), (x, y + r * 0.95)], fill=col)

def anger(d, x, y, r, col, k=1.0, w=None):
    """漫画“怒”符号：四个向外凸的弯角，中间留十字空隙"""
    w = w or max(2, int(r * 0.32 * k))
    g = r * 0.22
    for sx in (-1, 1):
        for sy in (-1, 1):
            pts = [(x + sx * g, y + sy * r), (x + sx * g, y + sy * g), (x + sx * r, y + sy * g)]
            d.line([(px * k, py * k) for px, py in pts], fill=col, width=w, joint="curve")

def burst(d, x, y, r1, r0, col, k=1.0, n=10, rot=0.2):
    """吵架爆炸星"""
    pts = []
    for i in range(n * 2):
        a = rot + math.pi * i / n; r = r1 if i % 2 == 0 else r0
        pts.append(((x + math.cos(a) * r) * k, (y + math.sin(a) * r) * k))
    d.polygon(pts, fill=col)

# 同一情节的布局（1080×1920 坐标）
CAST = [  # (name, pose, expr, x, y, s, flip, lookx)
    ("groomer", "groom", "happy", 262, 720, 58, 1, 0),
    ("groomee", "sit", "happy", 400, 748, 62, -1, 0),
    ("fightL", "angry", "angry", 645, 712, 56, 1, 1),
    ("fightR", "angry", "angry", 812, 712, 56, -1, 1),
    ("peeker", "peek", "wow", 540, 1040, 108, 1, -1.6),
]
