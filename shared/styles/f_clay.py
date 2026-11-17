# F. 黏土定格风：同一场景，每个图元记录为独立“泥块”→ 距离场鼓包高度 + 指纹/捏痕 → 法线打光 + 投影 + 景深
import time, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from common import *
import b_book

class Dual:
    """把每一次绘制同时写进颜色图和 id 图，id 记录图元编号、所在层（用于投影高度）"""
    def __init__(self, img, ids):
        self.c = ImageDraw.Draw(img); self.i = ImageDraw.Draw(ids); self.n = 0; self.meta = {}; self.layer = (0, 22)
    def _go(self, name, *a, **kw):
        getattr(self.c, name)(*a, **kw)
        self.n += 1; self.meta[self.n] = self.layer
        kw2 = dict(kw)
        if "fill" in kw2: kw2["fill"] = self.n
        if "outline" in kw2: kw2["outline"] = self.n
        getattr(self.i, name)(*a, **kw2)
    def __getattr__(self, name):
        return lambda *a, **kw: self._go(name, *a, **kw)

def build():
    k = 1
    img = Image.new("RGB", (W, H), (250, 236, 210)); ids = Image.new("I", (W, H), 0)
    d = Dual(img, ids)
    d.layer = (0, 60)       # 墙地：几乎平（只给大圆角）
    d.rectangle((0, 0, W, 905), fill=(255, 222, 178))
    d.rectangle((0, 905, W, H), fill=(214, 172, 128))
    d.layer = (6, 26)       # 墙上物件
    d.rounded_rectangle((300, 300, 780, 560), radius=30, fill=(150, 212, 240))
    d.ellipse((660, 330, 740, 410), fill=(255, 206, 96))
    for cx, cy in ((400, 420), (560, 380)):
        d.ellipse((cx - 60, cy - 22, cx + 60, cy + 22), fill=(252, 252, 248))
        d.ellipse((cx - 30, cy - 44, cx + 30, cy + 4), fill=(252, 252, 248))
    d.rectangle((300, 425, 780, 437), fill=(236, 204, 160)); d.rectangle((534, 300, 546, 560), fill=(236, 204, 160))
    d.ellipse((190, 330, 250, 390), fill=(255, 250, 238)); d.line((220, 360, 220, 338), fill=(120, 90, 80), width=6); d.line((220, 360, 238, 366), fill=(120, 90, 80), width=6)
    for ox, oy in ((-30, -40), (0, -70), (30, -45), (-15, -95), (20, -100)):
        d.ellipse((860 + ox - 32, 520 + oy - 22, 860 + ox + 32, 520 + oy + 22), fill=(110, 186, 100))
    d.polygon([(825, 520), (895, 520), (884, 600), (836, 600)], fill=(236, 120, 86))
    d.layer = (3, 40)
    d.ellipse((190, 860, 900, 960), fill=(250, 200, 150))
    d.layer = (14, 12)
    for i in range(3):
        bx = 540 + i * 16
        d.arc((bx - 34, 850, bx + 34, 910), 20, 160, fill=(255, 210, 70), width=16)
    d.layer = (22, 20)      # 角色
    for name, pose, expr, x, y, s, fl, lx in CAST:
        if name == "peeker": continue
        draw_prims(d, monkey_prims(pose, expr, lx, 0.6), x, y, s, fl)
    d.layer = (34, 22)
    heart(d, 330, 600, 30, (255, 110, 145)); heart(d, 384, 548, 20, (255, 145, 168))
    burst(d, 728, 600, 62, 34, (255, 210, 80)); burst(d, 728, 600, 36, 20, (240, 90, 66))
    anger(d, 860, 640, 26, (232, 74, 66))
    pk = [c for c in CAST if c[0] == "peeker"][0]; P = monkey_prims(pk[1], pk[2], pk[7])
    d.layer = (40, 26)
    draw_prims(d, P, pk[3], pk[4], pk[5], pk[6], groups=("head", "face"))
    d.layer = (60, 70)      # 前景隔板（大块泥板）
    d.rounded_rectangle((150, 1150, 930, 1980), radius=40, fill=(120, 176, 200))
    d.rounded_rectangle((150, 1150, 930, 1186), radius=18, fill=(150, 200, 220))
    d.layer = (72, 18)
    draw_prims(d, P, pk[3], pk[4], pk[5], pk[6], groups=("hands",))
    d.layer = (48, 22)
    d.ellipse((625, 860, 735, 960), fill=(255, 255, 250)); d.ellipse((610, 950, 632, 972), fill=(255, 255, 250))
    heart(d, 680, 915, 24, (255, 110, 145))
    return img, np.asarray(ids).astype(np.int32), d.meta

def noise(h, w, scale, seed, oct=3): return b_book.noise(h, w, scale, seed, oct)

def clay(img, ids, meta):
    col = np.asarray(img).astype(np.float32) / 255
    hgt = np.zeros((H, W), np.float32); elev = np.zeros((H, W), np.float32)
    for n, (lay, R) in meta.items():
        m = (ids == n)
        if not m.any(): continue
        ys, xs = np.where(m); y0, y1, x0, x1 = max(ys.min() - 2, 0), ys.max() + 3, max(xs.min() - 2, 0), xs.max() + 3
        sub = m[y0:y1, x0:x1].astype(np.uint8); mk = sub > 0
        dt = cv2.distanceTransform(sub, cv2.DIST_L2, 5)
        r = max(2.0, dt.max())
        if lay < 5: r = min(r, 40)                                   # 墙地只圆角
        u = np.clip(dt / r, 0, 1); dome = r * np.sqrt(1 - (1 - u) ** 2) * (0.35 if lay < 5 else 0.85)
        blk = hgt[y0:y1, x0:x1]
        under = blk[mk].mean() if lay >= 5 else 0.0                  # 贴在下面那块泥的表面上
        base = cv2.GaussianBlur(blk, (0, 0), 6)[mk] * 0.55 + under * 0.45 if lay >= 5 else 0
        newh = base + dome[mk]
        blk[mk] = np.maximum(blk[mk] * 0.0 + newh, newh)
        eb = elev[y0:y1, x0:x1]; eb[mk] = lay
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    lump = noise(H, W, 60, 3) * 1.4
    fp = np.sin((np.sqrt((xx - 400) ** 2 + (yy - 820) ** 2) + noise(H, W, 40, 5) * 18) * 0.6) * 0.18
    grain = noise(H, W, 2.5, 7, 2) * 0.22
    surf = (hgt + (lump + fp + grain) * np.where(elev < 5, 0.5, 1.0)).astype(np.float32)
    surf = cv2.GaussianBlur(surf, (0, 0), 1.0)
    gx = cv2.Sobel(surf, cv2.CV_32F, 1, 0, ksize=3) / 8; gy = cv2.Sobel(surf, cv2.CV_32F, 0, 1, ksize=3) / 8
    nz = 1.0 / np.sqrt(gx ** 2 + gy ** 2 + 1); nx, ny = -gx * nz, -gy * nz
    L = np.array([-0.5, -0.6, 0.62]); L /= np.linalg.norm(L)
    lam = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    Hh = L + np.array([0, 0, 1.0]); Hh /= np.linalg.norm(Hh)
    spec = np.clip(nx * Hh[0] + ny * Hh[1] + nz * Hh[2], 0, 1) ** 24 * 0.28
    rim = np.clip(nx * 0.7 + ny * 0.2, 0, 1) ** 2 * (1 - nz) * 0.35            # 右侧暖色轮廓光
    # 投射阴影：沿光线方向在高度场里步进
    top = (surf + elev * 2.2).astype(np.float32)
    dirx, diry = -L[0], -L[1]; dz = L[2] / np.hypot(L[0], L[1])
    sh = np.zeros_like(top)
    for st in (4, 8, 13, 19, 27, 36, 48, 62, 80):
        M = np.float32([[1, 0, -dirx * st], [0, 1, -diry * st]])        # 取光源方向上的点
        hs = cv2.warpAffine(top, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
        sh = np.maximum(sh, np.clip((hs - top - st * dz * 0.9) / 10, 0, 1))
    sh = cv2.GaussianBlur(sh, (0, 0), 3.5)
    ao = np.clip(cv2.GaussianBlur(top, (0, 0), 14) - top, 0, 25) / 25
    light = 0.38 + 0.78 * lam * (1 - 0.7 * sh)
    out = col * (light * (1 - 0.35 * ao))[..., None]
    out += spec[..., None] * (1 - sh[..., None]) * np.array([1.0, 0.97, 0.9])
    out += rim[..., None] * np.array([1.0, 0.75, 0.5]) * col
    g = out.mean(2, keepdims=True); out = g + (out - g) * 1.12
    out *= np.array([1.04, 1.0, 0.93])
    out = np.clip(out, 0, 1)
    # 微距景深：对焦在角色，墙与前景隔板下部虚化
    focus = np.clip(1 - np.abs(elev - 26) / 30, 0, 1)
    focus = np.maximum(focus, (elev >= 5).astype(np.float32) * 0.6)
    focus = cv2.GaussianBlur(focus.astype(np.float32), (0, 0), 8)
    bl = cv2.GaussianBlur(out, (0, 0), 5.5)
    w = (1 - focus)[..., None]
    out = out * (1 - w) + bl * w
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
    out *= (1 - 0.3 * np.clip(r - 0.25, 0, 1)[..., None])
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))

def frame():
    img, ids, meta = build()
    im = clay(img, ids, meta)
    brand(im, dark_text=(120, 70, 40), pill=(255, 250, 240, 240), title_col=(120, 70, 40), title_bg=(255, 250, 240, 170))
    subtitle(im, box=(92, 58, 40, 215), col=(255, 248, 236), hl=["吵架", "好朋友"], hlcol=(255, 200, 120))
    return im

if __name__ == "__main__":
    t0 = time.time(); im = frame(); print("F frame sec", round(time.time() - t0, 2))
    im.save("/workspace/work/styles/F_clay.png")
