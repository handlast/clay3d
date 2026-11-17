# A. 工作群聊天记录体：整屏手机群聊界面；猴头像、消息气泡、监控截图（复用 B 的平涂场景 + 监控滤镜）、猴际关系卡
import time, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from common import *
import b_book

SS = 2
GREEN = (149, 236, 105); BG = (237, 237, 237); GRAY = (150, 150, 150); INK = (25, 25, 25); RED = (250, 81, 81)

def avatar(img, x, y, sz, expr, bg, lookx=0):
    """圆角方形头像，里面一颗猴头"""
    k = SS
    lay = Image.new("RGBA", (sz * k, sz * k), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, sz * k - 1, sz * k - 1), radius=14 * k, fill=bg)
    m = Image.new("L", lay.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, sz * k - 1, sz * k - 1), radius=14 * k, fill=255)
    s = sz * 0.36
    draw_prims(d, monkey_prims("peek", expr, lookx), sz / 2, sz * 0.55, s, 1, k=k, groups=("head", "face"))
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay)[..., 3], np.asarray(m))))
    img.alpha_composite(lay, (x * k, y * k))

def T(d, xy, s, sz, fill, anchor="la", black=False):
    d.text((xy[0] * SS, xy[1] * SS), s, font=font(sz * SS, black), fill=fill, anchor=anchor)
def RR(d, box, r, fill, **kw):
    d.rounded_rectangle(tuple(v * SS for v in box), radius=r * SS, fill=fill, **kw)

def bubble_left(d, x, y, text, sz=36, fill=(255, 255, 255)):
    w = tlen(text, sz) + 44; h = sz + 38
    RR(d, (x, y, x + w, y + h), 14, fill)
    d.polygon([((x - 12) * SS, (y + 30) * SS), (x * SS, (y + 22) * SS), (x * SS, (y + 40) * SS)], fill=fill)
    T(d, (x + 22, y + h / 2), text, sz, INK, "lm")
    return h
def bubble_right(d, xr, y, text, sz=36, fill=GREEN, hl=None):
    w = tlen(text, sz) + 44; h = sz + 38
    RR(d, (xr - w, y, xr, y + h), 14, fill)
    d.polygon([((xr + 12) * SS, (y + 30) * SS), (xr * SS, (y + 22) * SS), (xr * SS, (y + 40) * SS)], fill=fill)
    xx = xr - w + 22
    for seg, c in ([(text, INK)] if not hl else hl):
        T(d, (xx, y + h / 2), seg, sz, c, "lm"); xx += tlen(seg, sz)
    return h

def cctv(w, h):
    """监控截图：B 的平涂场景裁一块 → 偏冷去饱和 + 扫描线 + 时间戳"""
    src = b_book.flat_scene().crop((180, 480, 900, 880)).resize((w, h), Image.LANCZOS)
    a = np.asarray(src).astype(np.float32)
    g = a.mean(2, keepdims=True)
    a = a * 0.55 + g * 0.45; a = a * np.array([0.92, 1.0, 1.0]) + np.array([0, 6, 10])
    a[::4] *= 0.86
    rng = np.random.default_rng(3); a += rng.normal(0, 5, a.shape)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0, 0, w, 40), fill=(0, 0, 0, 90))
    d.ellipse((12, 12, 28, 28), fill=(255, 60, 60))
    d.text((36, 20), "REC  CAM-02  10:24:37", font=font(22, True), fill=(255, 255, 255), anchor="lm")
    # 监控里的高亮框：理毛（粉）/ 吵架（橙）
    return im

def rel_card(img, x, y, w, h):
    d = ImageDraw.Draw(img, "RGBA")
    RR(d, (x, y, x + w, y + h), 16, (255, 255, 255))
    T(d, (x + 24, y + 36), "猴际关系图 · 本周", 30, INK, "lm", True)
    T(d, (x + w - 24, y + 36), "来自监控", 22, GRAY, "rm")
    d.line(((x + 20) * SS, (y + 66) * SS, (x + w - 20) * SS, (y + 66) * SS), fill=(235, 235, 235), width=2 * SS)
    ny = y + 140
    nodes = dict(豆豆=(x + 75, ny), 花花=(x + 205, ny), 老灰=(x + w - 205, ny), 老白=(x + w - 75, ny))
    (ax, ay), (bx, by) = nodes["豆豆"], nodes["花花"]
    d.line((ax * SS, ay * SS, bx * SS, by * SS), fill=(255, 150, 180), width=12 * SS)
    (cx, cy), (ex, ey) = nodes["老灰"], nodes["老白"]
    zz = [(cx + (ex - cx) * i / 6, cy + (12 if i % 2 else -12) * (0 < i < 6)) for i in range(7)]
    d.line([(px * SS, py * SS) for px, py in zz], fill=(255, 150, 70), width=8 * SS, joint="curve")
    for nm, (nx, nyy) in nodes.items():
        expr = "happy" if nm in ("豆豆", "花花") else "angry"
        avatar(img, int(nx - 32), int(nyy - 32), 64, expr, (255, 228, 236) if expr == "happy" else (255, 232, 210), 1 if nm in ("豆豆", "老灰") else -1)
        T(d, (nx, nyy + 54), nm, 22, (90, 90, 90), "mm")
    heart(d, (ax + bx) / 2, ay - 2, 16, (255, 80, 130), SS)
    T(d, ((ax + bx) / 2, y + 92), "理毛 ×6", 24, (230, 70, 120), "mm", True)
    T(d, ((cx + ex) / 2, y + 92), "吵架 ×3", 24, (225, 110, 30), "mm", True)

def frame(t=0.0):
    k = SS
    img = Image.new("RGBA", (W * k, H * k), BG + (255,)); d = ImageDraw.Draw(img, "RGBA")
    # 顶栏（状态栏 + 群标题）
    RR(d, (0, -20, W, 352), 0, (247, 247, 247))
    T(d, (60, 50), "10:24", 30, INK, "lm", True)
    for i in range(4): RR(d, (900 + i * 12, 58 - i * 6, 908 + i * 12, 64), 2, INK)
    RR(d, (960, 42, 1012, 64), 6, INK); RR(d, (964, 46, 1000, 60), 3, (110, 220, 110))
    d.line((0, 352 * k, W * k, 352 * k), fill=(222, 222, 222), width=2 * k)
    T(d, (196, 288), "‹", 64, INK, "mm")
    RR(d, (222, 268, 282, 306), 19, RED); T(d, (252, 287), "12", 24, (255, 255, 255), "mm", True)
    T(d, (560, 272), "猴山行政部（5）", 38, INK, "mm", True)
    T(d, (560, 320), "大黑 正在输入…", 24, (87, 107, 149), "mm")
    T(d, (880, 286), "···", 40, INK, "mm", True)
    # 消息 1：小桃（探头猴）
    y = 372
    avatar(img, 186, y, 84, "wow", (255, 226, 214), -1)
    T(d, (292, y + 4), "小桃", 24, GRAY, "lm")
    bubble_left(d, 298, y + 22, "刚调了二号监控，你们看")
    # 消息 2：监控截图（图片消息）
    y = 482
    avatar(img, 186, y, 84, "wow", (255, 226, 214), -1)
    shot = cctv(440, 264)
    m = Image.new("L", (440 * k, 264 * k), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 440 * k - 1, 264 * k - 1), radius=14 * k, fill=255)
    img.paste(shot.resize((440 * k, 264 * k), Image.LANCZOS), (298 * k, y * k), m)
    # 消息 3：大黑（吵架那只）
    y = 760
    avatar(img, 186, y, 84, "angry", (255, 230, 200), 1)
    T(d, (292, y + 4), "大黑", 24, GRAY, "lm")
    bubble_left(d, 298, y + 22, "又吵起来了？谁赢了!!")
    RR(d, (252, y - 6, 276, y + 18), 12, RED)   # 未读红点
    # 消息 4：我（阿棕）
    y = 866
    avatar(img, 806, y, 84, "happy", (220, 240, 255), 0)
    bubble_right(d, 782, y + 4, "我只想知道：谁和谁是好朋友", sz=34, hl=[("我只想知道：谁和谁是", INK), ("好朋友", (200, 40, 100))])
    # 消息 5：小桃甩来关系卡
    y = 966
    avatar(img, 186, y, 84, "wow", (255, 226, 214), -1)
    rel_card(img, 298, y, 586, 232)
    img = img.resize((W, H), Image.LANCZOS).convert("RGB")
    # 底部输入栏（在抖音按钮区，非关键内容）
    d1 = ImageDraw.Draw(img)
    d1.rectangle((0, 1440, W, H), fill=(247, 247, 247)); d1.line((0, 1440, W, 1440), fill=(222, 222, 222), width=2)
    d1.rounded_rectangle((120, 1468, 860, 1548), radius=12, fill=(255, 255, 255))
    d1.text((150, 1508), "@小桃 再发一张", font=font(30), fill=(190, 190, 190), anchor="lm")
    brand(img, dark_text=(255, 255, 255), pill=(36, 36, 40, 255), title_col=(90, 90, 90), title_bg=None)
    subtitle(img, box=(20, 22, 30, 225), hl=["吵架", "好朋友"], hlcol=(255, 205, 80))
    return img

if __name__ == "__main__":
    t0 = time.time(); im = frame(); print("A sec", round(time.time() - t0, 2))
    im.save("/workspace/work/styles/A_chat.png")
