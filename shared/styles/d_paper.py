# D. 剪纸拼贴定格风：每个纸片 = RGBA 图层 → 撕边/剪边位移 + 纸纤维纹理 + 柔和浅色投影，逐片叠加
import time, math
import numpy as np, cv2
from PIL import Image, ImageDraw
from common import *

SS = 2
rng0 = np.random.default_rng(5)
def noise(h, w, scale, seed, oct=3):
    rng = np.random.default_rng(seed); out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(oct):
        n = rng.standard_normal((max(2, int(h / scale) + 2), max(2, int(w / scale) + 2))).astype(np.float32)
        out += amp * cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC); tot += amp; amp *= 0.5; scale /= 2
    return out / tot
NX = noise(H, W, 14, 1) * 2.2 + noise(H, W, 70, 2) * 3.0
NY = noise(H, W, 14, 3) * 2.2 + noise(H, W, 70, 4) * 3.0
FIB = noise(H, W, 2, 6, 2) * 0.5 + noise(H, W, 9, 7, 2) * 0.5          # 纸纤维
rng = np.random.default_rng(8)
fib = rng.standard_normal((H, W)).astype(np.float32)
FIB2 = cv2.filter2D(fib, -1, np.ones((1, 9), np.float32) / 9) * 0.5 + cv2.filter2D(fib, -1, np.ones((9, 1), np.float32) / 9) * 0.5
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)

def layer(draw_fn):
    im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    draw_fn(d, SS)
    return np.asarray(im.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255

def put(canvas, L, torn=False, shadow=0.24, off=(5, 8), tex=0.07, seed=0):
    a = L[..., 3]
    ys, xs = np.nonzero(a > 0.01)
    if len(xs) == 0: return
    pad = 40
    x0, x1 = max(0, xs.min() - pad), min(W, xs.max() + pad); y0, y1 = max(0, ys.min() - pad), min(H, ys.max() + pad)
    sl = (slice(y0, y1), slice(x0, x1))
    amp = 1.0 if torn else 0.35
    sx, sy = (seed * 37) % 200, (seed * 53) % 200
    nx = np.roll(NX, (sy, sx), (0, 1))[sl] * amp; ny = np.roll(NY, (sy, sx), (0, 1))[sl] * amp
    mx, my = XX[sl] + nx, YY[sl] + ny
    Lp = np.ascontiguousarray(np.concatenate([L[..., :3] * L[..., 3:4], L[..., 3:4]], 2))   # 预乘，避免透明区黑色渗边
    Lc = cv2.remap(Lp, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    al0 = Lc[..., 3]
    col = Lc[..., :3] / np.maximum(al0[..., None], 1e-4)
    al = np.clip((al0 - 0.5) * 3 + 0.5, 0, 1) if torn else al0
    # 柔和投影（浅色：画布压暗 ≤ 24%，暖调，非黑边）
    if shadow > 0:
        sh = cv2.GaussianBlur(al, (0, 0), 7)
        M = np.float32([[1, 0, off[0]], [0, 1, off[1]]])
        sh = cv2.warpAffine(sh, M, (sh.shape[1], sh.shape[0]))
        c = canvas[sl]
        canvas[sl] = c * (1 - shadow * sh[..., None] * np.array([1.0, 1.05, 1.15], np.float32))
    # 纸纹
    f = FIB[sl][..., None] * tex + FIB2[sl][..., None] * tex * 0.6
    col = np.clip(col * (1 + f), 0, 1)
    if torn:   # 撕边露出浅色纸芯
        er = cv2.erode((al > 0.5).astype(np.float32), np.ones((5, 5), np.uint8))
        rim = np.clip(al - er, 0, 1) * (0.5 + 0.5 * np.clip(FIB[sl] * 2, 0, 1))
        col = col * (1 - rim[..., None] * 0.7) + rim[..., None] * 0.7 * np.array([0.99, 0.97, 0.92], np.float32)
    c = canvas[sl]
    canvas[sl] = c * (1 - al[..., None]) + col * al[..., None]

def R(c): return tuple(int(v) for v in c) + (255,)

def frame(t=0.0):
    cv = np.ones((H, W, 3), np.float32) * np.array([0.96, 0.93, 0.86], np.float32)
    cv *= (1 + FIB[..., None] * 0.04)
    sd = 0
    def P(fn, **kw):
        nonlocal sd; sd += 1; put(cv, layer(fn), seed=sd, **kw)
    # —— 背景拼贴 ——
    P(lambda d, k: d.polygon([(0, 0), (W * k, 0), (W * k, 880 * k), (0, 900 * k)], fill=R((246, 196, 92))), torn=True, shadow=0.0)
    P(lambda d, k: d.polygon([(0, 260 * k), (W * k, 230 * k), (W * k, 290 * k), (0, 330 * k)], fill=R((240, 170, 70))), torn=True, shadow=0.12)
    P(lambda d, k: d.polygon([(0, 890 * k), (W * k, 870 * k), (W * k, H * k), (0, H * k)], fill=R((214, 108, 78))), torn=True, shadow=0.2)
    P(lambda d, k: d.polygon([(120 * k, 935 * k), (960 * k, 925 * k), (930 * k, 1010 * k), (150 * k, 1020 * k)], fill=R((236, 140, 104))), torn=True, shadow=0.15)
    P(lambda d, k: d.rectangle((300 * k, 330 * k, 780 * k, 580 * k), fill=R((128, 196, 222))), torn=True)
    P(lambda d, k: d.ellipse((650 * k, 360 * k, 740 * k, 450 * k), fill=R((255, 236, 150))), shadow=0.12)
    def cloud(cx, cy):
        return lambda d, k: (d.ellipse(((cx - 62) * k, (cy - 20) * k, (cx + 62) * k, (cy + 22) * k), fill=R((252, 250, 244))),
                             d.ellipse(((cx - 30) * k, (cy - 46) * k, (cx + 30) * k, (cy + 6) * k), fill=R((252, 250, 244))))
    P(cloud(410, 455), torn=True, shadow=0.12); P(cloud(560, 410), torn=True, shadow=0.12)
    P(lambda d, k: (d.rectangle((300 * k, 450 * k, 780 * k, 462 * k), fill=R((250, 238, 210))), d.rectangle((534 * k, 330 * k, 546 * k, 580 * k), fill=R((250, 238, 210)))), shadow=0.15)
    # 挂钟、盆栽（叶片一片一片）
    P(lambda d, k: d.ellipse((190 * k, 350 * k, 254 * k, 414 * k), fill=R((250, 248, 240))))
    P(lambda d, k: (d.line((222 * k, 382 * k, 222 * k, 360 * k), fill=R((70, 60, 80)), width=5 * k), d.line((222 * k, 382 * k, 240 * k, 388 * k), fill=R((70, 60, 80)), width=5 * k)), shadow=0.1, off=(2, 3))
    for i, (ox, oy, a) in enumerate(((-34, -40, 30), (0, -78, 0), (32, -46, -30), (-16, -110, 15), (22, -112, -15))):
        P(lambda d, k, ox=ox, oy=oy: d.ellipse(((860 + ox - 22) * k, (540 + oy - 36) * k, (860 + ox + 22) * k, (540 + oy + 36) * k), fill=R((96, 170, 110) if i % 2 else (120, 190, 120))), shadow=0.18)
    P(lambda d, k: d.polygon([(825 * k, 535 * k), (895 * k, 535 * k), (884 * k, 615 * k), (836 * k, 615 * k)], fill=R((200, 90, 120))), torn=True)
    # 香蕉
    P(lambda d, k: d.chord((505 * k, 850 * k, 585 * k, 912 * k), 20, 160, fill=R((255, 214, 80))), shadow=0.2)
    # —— 角色：每只猴 = 身体 / 头 / 脸 三片纸 ——
    for name, pose, expr, x, y, s, fl, lx in CAST:
        if name == "peeker": continue
        Pm = monkey_prims(pose, expr, lx, 0.6)
        for g in ("body", "head", "face"):
            P(lambda d, k, g=g: draw_prims(d, Pm, x, y, s, fl, k=k, groups=(g,)), shadow=0.22 if g != "face" else 0.12, off=(4, 7) if g != "face" else (2, 3))
    pk = [c for c in CAST if c[0] == "peeker"][0]; Pm = monkey_prims(pk[1], pk[2], pk[7])
    for g in ("head", "face"):
        P(lambda d, k, g=g: draw_prims(d, Pm, pk[3], pk[4], pk[5], pk[6], k=k, groups=(g,)), shadow=0.22 if g != "face" else 0.12)
    P(lambda d, k: d.rectangle((150 * k, 1150 * k, 930 * k, 1990 * k), fill=R((84, 160, 170))), torn=True, shadow=0.28, off=(0, -8))
    P(lambda d, k: d.rectangle((150 * k, 1150 * k, 930 * k, 1190 * k), fill=R((120, 196, 196))), torn=True, shadow=0.15)
    P(lambda d, k: draw_prims(d, Pm, pk[3], pk[4], pk[5], pk[6], k=k, groups=("hands",)), shadow=0.25)
    # 符号纸片
    P(lambda d, k: heart(d, 330, 600, 30, R((240, 90, 130)), k)); P(lambda d, k: heart(d, 384, 548, 20, R((255, 140, 170)), k))
    P(lambda d, k: burst(d, 728, 600, 62, 34, R((255, 240, 200)), k)); P(lambda d, k: burst(d, 728, 600, 38, 20, R((230, 70, 70)), k), shadow=0.12)
    P(lambda d, k: anger(d, 862, 640, 26, R((230, 60, 60)), k), shadow=0.12, off=(2, 3))
    P(lambda d, k: (d.ellipse((625 * k, 860 * k, 735 * k, 960 * k), fill=R((255, 254, 248))), d.ellipse((608 * k, 950 * k, 632 * k, 974 * k), fill=R((255, 254, 248)))), torn=True)
    P(lambda d, k: heart(d, 680, 915, 24, R((240, 90, 130)), k), shadow=0.12)
    # 胶带
    for (bx, by, ang) in ((300, 330, -20), (780, 330, 20)):
        def tape(d, k, bx=bx, by=by, ang=ang):
            a = math.radians(ang); c, s_ = math.cos(a), math.sin(a)
            pts = [(bx + c * dx - s_ * dy, by + s_ * dx + c * dy) for dx, dy in ((-50, -16), (50, -16), (50, 16), (-50, 16))]
            d.polygon([(px * k, py * k) for px, py in pts], fill=(255, 250, 225, 170))
        P(tape, shadow=0.05, off=(1, 2), tex=0.03)
    img = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8))
    brand(img, dark_text=(150, 70, 50), pill=(255, 252, 244, 245), title_col=(255, 252, 244), title_bg=(150, 70, 50, 200))
    subtitle(img, box=(70, 50, 60, 220), col=(255, 250, 240), hl=["吵架", "好朋友"], hlcol=(255, 210, 110))
    return img

if __name__ == "__main__":
    t0 = time.time(); im = frame(); print("D frame sec", round(time.time() - t0, 2))
    im.save("/workspace/work/styles/D_papercut.png")
