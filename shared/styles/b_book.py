# B. 儿童绘本风：平涂 → 全局“水彩/蜡笔”后处理（噪声位移的不规则边、颜料颗粒、同色系湿边、纸纹）
import sys, time, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from common import *

SS = 2
def noise(h, w, scale, seed, oct=3):
    rng = np.random.default_rng(seed); out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(oct):
        sh, sw = max(2, int(h / scale) + 2), max(2, int(w / scale) + 2)
        n = rng.standard_normal((sh, sw)).astype(np.float32)
        out += amp * cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC); tot += amp
        amp *= 0.5; scale /= 2
    return out / tot

def flat_scene(t=0.0):
    k = SS
    img = Image.new("RGB", (W * k, H * k), (250, 236, 210)); d = ImageDraw.Draw(img)
    # 墙 + 地板
    d.rectangle((0, 0, W * k, 905 * k), fill=(252, 226, 190))
    d.rectangle((0, 905 * k, W * k, H * k), fill=(226, 190, 150))
    # 窗（天空+云+太阳）
    d.rounded_rectangle((300 * k, 300 * k, 780 * k, 560 * k), radius=30 * k, fill=(170, 214, 236))
    d.ellipse((660 * k, 330 * k, 740 * k, 410 * k), fill=(255, 214, 120))
    for cx, cy in ((400, 420), (560, 380)):
        d.ellipse(((cx - 60) * k, (cy - 22) * k, (cx + 60) * k, (cy + 22) * k), fill=(250, 250, 246))
        d.ellipse(((cx - 30) * k, (cy - 44) * k, (cx + 30) * k, (cy + 4) * k), fill=(250, 250, 246))
    d.rectangle((300 * k, 425 * k, 780 * k, 437 * k), fill=(240, 214, 176)); d.rectangle((534 * k, 300 * k, 546 * k, 560 * k), fill=(240, 214, 176))
    # 盆栽、挂钟
    d.ellipse((190 * k, 330 * k, 250 * k, 390 * k), fill=(255, 250, 238)); d.line((220 * k, 360 * k, 220 * k, 338 * k), fill=(120, 90, 80), width=5 * k); d.line((220 * k, 360 * k, 238 * k, 366 * k), fill=(120, 90, 80), width=5 * k)
    for i, (ox, oy) in enumerate(((-30, -40), (0, -70), (30, -45), (-15, -95), (20, -100))):
        d.ellipse(((860 + ox - 32) * k, (520 + oy - 22) * k, (860 + ox + 32) * k, (520 + oy + 22) * k), fill=(130, 186, 120))
    d.polygon([(825 * k, 520 * k), (895 * k, 520 * k), (884 * k, 600 * k), (836 * k, 600 * k)], fill=(232, 130, 100))
    # 地毯、香蕉
    d.ellipse((190 * k, 860 * k, 900 * k, 960 * k), fill=(246, 212, 170))
    for i in range(3):
        bx = 540 + i * 16
        d.arc(((bx - 34) * k, (850) * k, (bx + 34) * k, (910) * k), 20, 160, fill=(255, 210, 80), width=14 * k)
    # 角色
    for name, pose, expr, x, y, s, fl, lx in CAST:
        if name == "peeker": continue
        draw_prims(d, monkey_prims(pose, expr, lx, 0.6), x, y, s, fl, k=k)
    # 前景工位隔板 + 探头的猴
    pk = [c for c in CAST if c[0] == "peeker"][0]; P = monkey_prims(pk[1], pk[2], pk[7])
    draw_prims(d, P, pk[3], pk[4], pk[5], pk[6], k=k, groups=("head", "face"))
    d.rounded_rectangle((150 * k, 1150 * k, 930 * k, 1980 * k), radius=40 * k, fill=(130, 178, 196))
    d.rounded_rectangle((150 * k, 1150 * k, 930 * k, 1186 * k), radius=18 * k, fill=(160, 202, 218))
    draw_prims(d, P, pk[3], pk[4], pk[5], pk[6], k=k, groups=("hands",))
    # 隔板上贴的便签
    # 符号：理毛 = 心，吵架 = 怒
    heart(d, 330, 600, 30, (255, 120, 150), k); heart(d, 384, 548, 20, (255, 150, 170), k)
    burst(d, 728, 600, 62, 34, (255, 214, 90), k); burst(d, 728, 600, 36, 20, (240, 96, 70), k)
    anger(d, 860, 640, 26, (235, 80, 70), k)
    # 探头猴头顶的小心心泡泡
    d.ellipse((625 * k, 860 * k, 735 * k, 960 * k), fill=(255, 255, 250)); d.ellipse((610 * k, 950 * k, 632 * k, 972 * k), fill=(255, 255, 250))
    heart(d, 680, 915, 24, (255, 120, 150), k)
    return img.resize((W, H), Image.LANCZOS)

_cache = {}
def fields(seed=1):
    if seed not in _cache:
        _cache[seed] = dict(dx=noise(H, W, 60, seed) * 5.0 + noise(H, W, 8, seed + 9, 2) * 1.6,
                            dy=noise(H, W, 60, seed + 1) * 5.0 + noise(H, W, 8, seed + 10, 2) * 1.6,
                            gran=noise(H, W, 3, seed + 2, 2), blot=noise(H, W, 140, seed + 3),
                            paper=noise(H, W, 2, seed + 4, 2) * 0.6 + noise(H, W, 30, seed + 5) * 0.4,
                            crayon=None)
        rng = np.random.default_rng(seed + 7)            # 蜡笔斜向笔触
        st = rng.standard_normal((H // 2, W // 2)).astype(np.float32)
        st = cv2.filter2D(st, -1, np.eye(15, dtype=np.float32)[::-1] / 15)
        _cache[seed]["crayon"] = cv2.resize(st, (W, H))
    return _cache[seed]

def watercolor(img, seed=1):
    F = fields(seed)
    a = np.asarray(img).astype(np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = cv2.remap(a, xx + F["dx"], yy + F["dy"], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)   # 不规则边
    soft = cv2.GaussianBlur(a, (0, 0), 1.6); a = a * 0.55 + soft * 0.45                              # 晕开
    lum = a.mean(2)
    edge = np.abs(lum - cv2.GaussianBlur(lum, (0, 0), 5))                                             # 湿边（同色加深，非描边）
    edge = np.clip(edge * 5, 0, 1)[..., None]
    pig = 1 - a
    pig *= (1 + 0.28 * edge)                                                                          # 颜料在边缘堆积
    pig *= (1 + 0.10 * F["blot"][..., None] + 0.09 * F["gran"][..., None] + 0.07 * F["crayon"][..., None])
    out = 1 - pig
    out *= (0.96 + 0.04 * F["paper"][..., None])                                                      # 纸纹
    out = np.clip(out, 0, 1)
    # 暖色晕影
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
    out *= (1 - 0.18 * np.clip(r - 0.3, 0, 1)[..., None])
    return Image.fromarray((out * 255).astype(np.uint8))

def frame(t=0.0):
    img = watercolor(flat_scene(t))
    brand(img, dark_text=(120, 70, 40), pill=(255, 250, 240, 240), title_col=(120, 70, 40), title_bg=(255, 250, 240, 170))
    subtitle(img, box=(92, 58, 40, 215), col=(255, 248, 236), hl=["吵架", "好朋友"], hlcol=(255, 200, 120))
    return img

if __name__ == "__main__":
    t0 = time.time(); im = frame(); print("B frame sec", round(time.time() - t0, 2))
    t0 = time.time(); frame(); print("B 2nd frame sec (noise cached)", round(time.time() - t0, 2))
    im.save("/workspace/work/styles/B_storybook.png")
