# 黏土 SDF 原型（研究用，不改 g_clay3d.py）
# 用法: PYTHONPATH=/workspace/.pylib python3 clay_proto.py <res_w> <res_h> [flags...]
#  flags: noshadow noao nobump nosss nocull norelax central  bg  (bg=测试背景缓存+脏矩形)
import time, math, sys, os
import numpy as np, numba as nb, cv2

# ----------------------------------------------------------------- 场景描述（Python 侧）
# 每个图元: type(0椭球 1胶囊 2圆角盒) mode(0并 1刻(凹进) 2涂色(只改颜色+微鼓)) a(3) b(3) r k col(3) gloss group
PRIMS = []
GROUPS = []          # cx cy cz rad kjoin
def group(c, rad, kj=0.0):
    GROUPS.append([c[0], c[1], c[2], rad, kj]); return len(GROUPS) - 1
def prim(t, mode, a, b, r, k, col, gloss, g):
    PRIMS.append((t, mode, list(a), list(b), r, k, [(x / 255.0) ** 2.2 for x in col], gloss, g))   # 颜色转线性

FUR, FURD, FACE, BLUSH, INK, WHT, MOUTH = (150, 92, 54), (104, 60, 34), (240, 170, 150), (236, 110, 118), (26, 18, 16), (250, 248, 240), (120, 30, 44)

def monkey(x, z, s=1.0, yaw=0.0, expr="look", seed=0.0):
    cy, sy = math.cos(yaw), math.sin(yaw)
    def T(px, py, pz):
        px, py, pz = px * s, py * s, pz * s
        return [x + px * cy + pz * sy, py, z - px * sy + pz * cy]
    def E(g, mode, c, r, k, col, gl=0.25, inflate=0.0):
        prim(0, mode, T(*c), [r[0] * s, r[1] * s, r[2] * s], inflate * s, k * s, col, gl, g)
    def C(g, mode, a, b, r, k, col, gl=0.25):
        prim(1, mode, T(*a), T(*b), r * s, k * s, col, gl, g)
    body = group(T(0, 0.35, 0), 0.62 * s, 0.0)
    E(body, 0, (0, 0.32, 0), (0.30, 0.34, 0.26), 0.0, FUR)
    E(body, 2, (0, 0.28, 0.2), (0.17, 0.2, 0.12), 0.012, FACE, inflate=0.004)     # 肚皮：涂色区（不是贴片）
    for sx in (-1, 1):
        E(body, 0, (sx * 0.15, 0.05, 0.16), (0.11, 0.06, 0.13), 0.04, FACE)
        C(body, 0, (sx * 0.25, 0.45, 0.02), (sx * 0.2, 0.17, 0.2), 0.07, 0.03, FUR)
    hy = 0.88
    head = group(T(0, hy, 0.02), 0.48 * s, 0.03 * s)       # 头与身体用 kjoin 平滑连接
    E(head, 0, (0, hy, 0), (0.36, 0.33, 0.31), 0.0, FUR)
    E(head, 0, (0, hy + 0.27, -0.04), (0.16, 0.07, 0.14), 0.03, FURD)
    for sx in (-1, 1):
        E(head, 0, (sx * 0.36, hy + 0.03, -0.03), (0.1, 0.1, 0.06), 0.02, FURD)        # 耳
        E(head, 1, (sx * 0.40, hy + 0.03, 0.03), (0.055, 0.06, 0.04), 0.012, FACE)     # 耳窝：刻进去，内壁用脸色
    # 脸盘：两个眼区 + 下巴区，涂色（颜色区域长在头表面上，跟着头转）
    for sx in (-1, 1):
        E(head, 2, (sx * 0.1, hy + 0.04, 0.26), (0.15, 0.15, 0.12), 0.008, FACE, inflate=0.006)
    E(head, 2, (0, hy - 0.1, 0.25), (0.24, 0.13, 0.12), 0.008, FACE, inflate=0.006)
    E(head, 0, (0, hy - 0.11, 0.25), (0.14, 0.085, 0.08), 0.03, FACE)                 # 口鼻鼓包（平滑并入）
    for sx in (-1, 1):
        E(head, 2, (sx * 0.19, hy - 0.08, 0.26), (0.05, 0.035, 0.05), 0.012, BLUSH)    # 腮红：软边涂色
        ex, ey, ez = sx * 0.1, hy + 0.04, 0.29
        if expr == "happy":   # 眯眼：刻出弧形凹线
            C(head, 1, (ex - 0.045, ey - 0.01, ez + 0.02), (ex, ey + 0.018, ez + 0.025), 0.015, 0.005, INK)
            C(head, 1, (ex, ey + 0.018, ez + 0.025), (ex + 0.045, ey - 0.01, ez + 0.02), 0.015, 0.005, INK)
        else:
            rr = 0.06 if expr == "wow" else 0.05
            E(head, 0, (ex, ey, ez), (rr, rr * 1.12, 0.045), 0.004, INK, gl=1.0)        # 眼珠：亮面珠子，嵌入
        if expr == "angry":
            C(head, 0, (ex + sx * 0.06, ey + 0.1, ez + 0.0), (ex - sx * 0.04, ey + 0.065, ez + 0.02), 0.018, 0.008, FURD)
    for sx in (-1, 1):
        E(head, 1, (sx * 0.022, hy - 0.085, 0.335), (0.011, 0.009, 0.02), 0.004, INK)  # 鼻孔：刻洞
    if expr == "angry" or expr == "wow":
        E(head, 1, (0, hy - 0.16, 0.33), (0.055 if expr == "angry" else 0.03, 0.03, 0.04), 0.006, MOUTH)   # 张嘴：刻洞，内部深红
    else:
        C(head, 1, (-0.045, hy - 0.14, 0.32), (0.0, hy - 0.162, 0.33), 0.008, 0.004, MOUTH)
        C(head, 1, (0.0, hy - 0.162, 0.33), (0.045, hy - 0.14, 0.32), 0.008, 0.004, MOUTH)

def build(test="trio"):
    PRIMS.clear(); GROUPS.clear()
    gw = group((0, 1, -1.6), 1e3, 0.0)
    prim(2, 0, [0, 1.6, -1.95], [3.0, 1.8, 0.2], 0.08, 0, (196, 150, 112), 0.1, gw)
    prim(2, 0, [0, -0.1, 0], [3.0, 0.1, 3.0], 0.05, 0, (176, 128, 88), 0.1, gw)
    monkey(-0.62, 0.0, 1.0, 0.55, "happy")
    monkey(0.0, 0.1, 1.0, 0.0, "angry")
    monkey(0.62, 0.0, 1.0, -0.8, "wow")          # 大角度侧脸，检验脸盘
    n = len(PRIMS)
    PI = np.zeros((n, 3), np.int32); PF = np.zeros((n, 12), np.float64)
    for i, (t, mode, a, b, r, k, c, gl, g) in enumerate(PRIMS):
        PI[i] = (t, mode, g)
        PF[i] = a + b + [r, k] + c + [gl]
    GR = np.array(GROUPS, np.float64)
    G0 = np.zeros(len(GROUPS), np.int32); G1 = np.zeros(len(GROUPS), np.int32)
    for gi in range(len(GROUPS)):
        idx = np.where(PI[:, 2] == gi)[0]; G0[gi], G1[gi] = idx.min(), idx.max() + 1
    return PI, PF, GR, G0, G1

# ----------------------------------------------------------------- numba 内核
@nb.njit(fastmath=True, inline='always', cache=True)
def sd_prim(t, f, x, y, z):
    if t == 0:   # IQ 椭球（梯度归一化版，更接近欧氏距离 → 步数少、阴影/AO 更准）
        px, py, pz = x - f[0], y - f[1], z - f[2]
        k0 = math.sqrt((px / f[3]) ** 2 + (py / f[4]) ** 2 + (pz / f[5]) ** 2)
        k1 = math.sqrt((px / (f[3] * f[3])) ** 2 + (py / (f[4] * f[4])) ** 2 + (pz / (f[5] * f[5])) ** 2)
        return k0 * (k0 - 1.0) / (k1 + 1e-12)
    elif t == 1:
        px, py, pz = x - f[0], y - f[1], z - f[2]
        bx, by, bz = f[3] - f[0], f[4] - f[1], f[5] - f[2]
        h = (px * bx + py * by + pz * bz) / (bx * bx + by * by + bz * bz)
        h = min(1.0, max(0.0, h))
        dx, dy, dz = px - bx * h, py - by * h, pz - bz * h
        return math.sqrt(dx * dx + dy * dy + dz * dz) - f[6]
    else:
        r = f[6]
        qx = abs(x - f[0]) - f[3] + r; qy = abs(y - f[1]) - f[4] + r; qz = abs(z - f[2]) - f[5] + r
        ox, oy, oz = max(qx, 0.0), max(qy, 0.0), max(qz, 0.0)
        return math.sqrt(ox * ox + oy * oy + oz * oz) + min(max(qx, max(qy, qz)), 0.0) - r

# ---- 噪声：整数哈希 value noise + fbm（各向同性、无条纹）
@nb.njit(fastmath=True, inline='always', cache=True)
def hash3(i, j, k):
    h = (i * 374761393 + j * 668265263 + k * 1274126177) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h = h ^ (h >> 16)
    return (h & 0xFFFFFF) / 16777215.0

@nb.njit(fastmath=True, cache=True)
def vnoise(x, y, z):
    ix, iy, iz = math.floor(x), math.floor(y), math.floor(z)
    fx, fy, fz = x - ix, y - iy, z - iz
    ux, uy, uz = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy), fz * fz * (3 - 2 * fz)
    i, j, k = int(ix), int(iy), int(iz)
    a = hash3(i, j, k); b = hash3(i + 1, j, k); c = hash3(i, j + 1, k); d = hash3(i + 1, j + 1, k)
    e = hash3(i, j, k + 1); f = hash3(i + 1, j, k + 1); g = hash3(i, j + 1, k + 1); h = hash3(i + 1, j + 1, k + 1)
    x1 = a + (b - a) * ux; x2 = c + (d - c) * ux; x3 = e + (f - e) * ux; x4 = g + (h - g) * ux
    y1 = x1 + (x2 - x1) * uy; y2 = x3 + (x4 - x3) * uy
    return (y1 + (y2 - y1) * uz) * 2.0 - 1.0

@nb.njit(fastmath=True, cache=True)
def fbm3(x, y, z, octaves):
    # IQ fbm: G=0.5，每层旋转+放大 2.0x，打散轴向对齐（避免条纹）
    t = 0.0; a = 0.5
    for _ in range(octaves):
        t += a * vnoise(x, y, z)
        nx = 0.00 * x + 1.60 * y + 1.20 * z
        ny = -1.60 * x + 0.72 * y - 0.96 * z
        nz = -1.20 * x - 0.96 * y + 1.28 * z
        x, y, z = nx + 1.7, ny + 9.2, nz + 3.1
        a *= 0.5
    return t

@nb.njit(fastmath=True, cache=True)
def fingerprint(x, y, z, pix):
    # 指纹：随机分布的“按压点”，每个点 = 浅凹坑(press) + 同心脊纹(ridge)。2x2x2 邻格（IQ sdBase 思路）
    cs = 0.16
    gx, gy, gz = x / cs, y / cs, z / cs
    ix, iy, iz = int(math.floor(gx)), int(math.floor(gy)), int(math.floor(gz))
    v = 0.0
    period = 0.0075
    ridge_w = min(1.0, max(0.0, (period / (pix + 1e-9) - 2.0) / 2.0))   # 像素太大时脊纹淡出，避免闪烁/摩尔纹
    for di in range(2):
        for dj in range(2):
            for dk in range(2):
                ci, cj, ck = ix + di, iy + dj, iz + dk
                if hash3(ci, cj, ck + 77) > 0.45:
                    continue
                cx = (ci + hash3(ci, cj, ck) - 0.5) * cs
                cy = (cj + hash3(ci + 11, cj, ck) - 0.5) * cs
                cz = (ck + hash3(ci, cj + 23, ck) - 0.5) * cs
                R = (0.45 + 0.35 * hash3(ci + 5, cj + 7, ck)) * cs
                dx, dy, dz = x - cx, y - cy, z - cz
                r = math.sqrt(dx * dx * 1.0 + dy * dy * 1.6 + dz * dz)   # 略椭圆
                if r < R:
                    q = r / R
                    fall = (1 - q * q) * (1 - q * q)
                    v += -0.6 * fall                                     # 按压凹坑
                    v += 0.18 * fall * math.cos(6.2831 * r / period + 7 * hash3(ci, cj, ck + 3)) * ridge_w
    return v

@nb.njit(fastmath=True, cache=True)
def clay_detail(x, y, z, pix, seed):
    # 表面细节（只在求法线时加，不进光线步进）。seed 每“定格拍”变一次 = boil
    x += seed * 0.37; y += seed * 0.21; z -= seed * 0.29
    lump = fbm3(x * 7.0, y * 7.0, z * 7.0, 3)                 # 手捏的大块不平整
    grain = vnoise(x * 160.0, y * 160.0, z * 160.0)           # 细颗粒
    fp = fingerprint(x, y, z, pix)
    return lump * 0.0035 + grain * 0.00025 * min(1.0, 0.004 / (pix + 1e-9)) + fp * 0.0012

@nb.njit(fastmath=True, cache=True)
def smin_w(a, b, k):
    # IQ quadratic smin，返回 (值, b 的混合权重)
    if k <= 0.0:
        return (a, 0.0) if a < b else (b, 1.0)
    h = 1.0 - min(abs(a - b) / (4.0 * k), 1.0)
    w = h * h; m = w * 0.5; s = w * k
    if a < b:
        return a - s, m
    return b - s, 1.0 - m

@nb.njit(fastmath=True, cache=True)
def map_geo(x, y, z, PI, PF, GR, G0, G1, gmask):
    # 快速路径：只要距离（无涂色、无凹凸、无颜色）
    best = 1e9
    for gi in range(GR.shape[0]):
        if not gmask[gi]:
            continue
        dxg, dyg, dzg = x - GR[gi, 0], y - GR[gi, 1], z - GR[gi, 2]
        bd = math.sqrt(dxg * dxg + dyg * dyg + dzg * dzg) - GR[gi, 3]
        if bd > best + GR[gi, 4] * 4.0 and bd > 0.02:
            best = min(best, bd)    # 包围球距离本身就是下界，可直接用
            continue
        d = 1e9
        for i in range(G0[gi], G1[gi]):
            mode = PI[i, 1]
            if mode == 2:
                continue
            di = sd_prim(PI[i, 0], PF[i], x, y, z)
            k = PF[i, 7]
            if mode == 0:
                d, _ = smin_w(d, di, k)
            else:
                d2, _ = smin_w(-d, di, k); d = -d2           # smooth subtraction = smax(d, -di)
        best, _ = smin_w(best, d, GR[gi, 4])
    return best

@nb.njit(fastmath=True, cache=True)
def map_full(x, y, z, PI, PF, GR, G0, G1, out, pix, seed, use_detail):
    # 完整路径：颜色/光泽混合 + 涂色区微鼓 + 表面细节
    best = 1e9; br = bg_ = bb = 0.0; bgl = 0.0
    for gi in range(GR.shape[0]):
        dxg, dyg, dzg = x - GR[gi, 0], y - GR[gi, 1], z - GR[gi, 2]
        bd = math.sqrt(dxg * dxg + dyg * dyg + dzg * dzg) - GR[gi, 3]
        if bd > best + GR[gi, 4] * 4.0 and bd > 0.02:
            continue
        d = 1e9; cr = cg = cb = 0.0; gl = 0.0; infl = 0.0
        for i in range(G0[gi], G1[gi]):
            mode = PI[i, 1]
            di = sd_prim(PI[i, 0], PF[i], x, y, z)
            k = PF[i, 7]
            if mode == 0:
                d, w = smin_w(d, di, k)
            elif mode == 1:
                d2, w = smin_w(-d, di, k); d = -d2
                w = min(1.0, max(0.0, 1.0 - di / (2.0 * k + 1e-6))); w = w * w
            else:
                e = k
                w = min(1.0, max(0.0, 0.5 - di / (2.0 * e)))
                w = w * w * (3 - 2 * w)
                infl = max(infl, w * PF[i, 6])           # 涂色区像一层压上去的薄泥片；取 max，重叠处不叠厚
            cr += (PF[i, 8] - cr) * w; cg += (PF[i, 9] - cg) * w; cb += (PF[i, 10] - cb) * w; gl += (PF[i, 11] - gl) * w
        d -= infl
        bw = 0.0
        best, bw = smin_w(best, d, GR[gi, 4])
        br += (cr - br) * bw; bg_ += (cg - bg_) * bw; bb += (cb - bb) * bw; bgl += (gl - bgl) * bw
    if use_detail:
        best += clay_detail(x, y, z, pix, seed) * (1.0 - min(bgl, 1.0) * 0.9)   # 亮面眼珠不加指纹
    out[0] = br; out[1] = bg_; out[2] = bb; out[3] = bgl
    return best

@nb.njit(parallel=True, fastmath=True, cache=True)
def render(w, h, x0, x1, y0, y1, cam, tgt, fov, L, PI, PF, GR, G0, G1, img, dep, flags, seed):
    # flags: 0 shadow 1 ao 2 detail 3 sss 4 cull 5 relax 6 tetra
    NG = GR.shape[0]
    fx, fy, fz = tgt[0] - cam[0], tgt[1] - cam[1], tgt[2] - cam[2]
    fl = math.sqrt(fx * fx + fy * fy + fz * fz); fx /= fl; fy /= fl; fz /= fl
    rx, ry, rz = -fz, 0.0, fx; rl = math.sqrt(rx * rx + rz * rz); rx /= rl; rz /= rl
    ux, uy, uz = ry * fz - rz * fy, rz * fx - rx * fz, rx * fy - ry * fx
    tn = math.tan(fov / 2)
    pixang = 2 * tn / h
    allm = np.ones(NG, np.bool_)
    for j in nb.prange(y0, y1):
        out = np.zeros(4); tmp = np.zeros(4)
        gm = np.ones(NG, np.bool_)
        for i in range(x0, x1):
            sx = (2 * (i + 0.5) / w - 1) * tn * w / h; sy = (1 - 2 * (j + 0.5) / h) * tn
            dx, dy, dz = fx + rx * sx + ux * sy, fy + ry * sx + uy * sy, fz + rz * sx + uz * sy
            dl = math.sqrt(dx * dx + dy * dy + dz * dz); dx /= dl; dy /= dl; dz /= dl
            # 每条主光线先和各组包围球求交，不相交的组整条射线都不算
            if flags[4]:
                for g in range(NG):
                    ox, oy, oz = cam[0] - GR[g, 0], cam[1] - GR[g, 1], cam[2] - GR[g, 2]
                    b = ox * dx + oy * dy + oz * dz
                    c = ox * ox + oy * oy + oz * oz - (GR[g, 3] + GR[g, 4] * 4) ** 2
                    gm[g] = (b * b - c) > 0.0
            # 过松弛球追踪（Keinert 2014）
            t = 0.05; hit = False; omega = 1.5 if flags[5] else 1.0
            prev_r = 0.0; step = 0.0
            for s in range(160):
                px, py, pz = cam[0] + dx * t, cam[1] + dy * t, cam[2] + dz * t
                rad = map_geo(px, py, pz, PI, PF, GR, G0, G1, gm)
                if omega > 1.0 and abs(rad) + prev_r < step:
                    t -= step; step = 0.0; omega = 1.0          # 失败：退回上一步，改回普通球追踪
                    t += 0.0
                    prev_r = 0.0
                    continue
                if rad < 0.5 * pixang * t:
                    hit = True; break
                step = rad * omega; prev_r = abs(rad)
                t += step
                if t > 20: break
            if not hit:
                img[j, i, 0] = 0.6; img[j, i, 1] = 0.45; img[j, i, 2] = 0.3; dep[j, i] = 20; continue
            px, py, pz = cam[0] + dx * t, cam[1] + dy * t, cam[2] + dz * t
            pix = pixang * t
            use_d = flags[2] == 1
            map_full(px, py, pz, PI, PF, GR, G0, G1, out, pix, seed, use_d)
            cr, cg, cb, gl = out[0], out[1], out[2], out[3]
            e = max(0.0008, pix * 0.7)
            if flags[6]:   # 四面体法线：4 次求值
                k0 = map_full(px + e, py - e, pz - e, PI, PF, GR, G0, G1, tmp, pix, seed, use_d)
                k1 = map_full(px - e, py - e, pz + e, PI, PF, GR, G0, G1, tmp, pix, seed, use_d)
                k2 = map_full(px - e, py + e, pz - e, PI, PF, GR, G0, G1, tmp, pix, seed, use_d)
                k3 = map_full(px + e, py + e, pz + e, PI, PF, GR, G0, G1, tmp, pix, seed, use_d)
                nx = k0 - k1 - k2 + k3; ny = -k0 - k1 + k2 + k3; nz = -k0 + k1 - k2 + k3
            else:
                nx = map_full(px + e, py, pz, PI, PF, GR, G0, G1, tmp, pix, seed, use_d) - map_full(px - e, py, pz, PI, PF, GR, G0, G1, tmp, pix, seed, use_d)
                ny = map_full(px, py + e, pz, PI, PF, GR, G0, G1, tmp, pix, seed, use_d) - map_full(px, py - e, pz, PI, PF, GR, G0, G1, tmp, pix, seed, use_d)
                nz = map_full(px, py, pz + e, PI, PF, GR, G0, G1, tmp, pix, seed, use_d) - map_full(px, py, pz - e, PI, PF, GR, G0, G1, tmp, pix, seed, use_d)
            nl = math.sqrt(nx * nx + ny * ny + nz * nz) + 1e-12; nx /= nl; ny /= nl; nz /= nl
            ndl = nx * L[0] + ny * L[1] + nz * L[2]
            # 软阴影（IQ 改进版：允许进入物体内部，-1..1 smoothstep），背光面直接跳过
            sh = 1.0
            if flags[0] and ndl > -0.35:
                res = 1.0; st = 0.015; wsz = 0.12
                ox, oy, oz = px + nx * 0.004, py + ny * 0.004, pz + nz * 0.004
                for s in range(36):
                    hh = map_geo(ox + L[0] * st, oy + L[1] * st, oz + L[2] * st, PI, PF, GR, G0, G1, allm)
                    res = min(res, hh / (wsz * st))
                    st += min(max(hh, 0.012), 0.25)
                    if res < -1.0 or st > 3.0: break
                res = max(res, -1.0)
                sh = 0.25 * (1.0 + res) * (1.0 + res) * (2.0 - res)
            elif flags[0]:
                sh = 0.0
            ao = 1.0
            if flags[1]:
                occ = 0.0; sc = 1.0
                for s in range(4):
                    hh = 0.01 + 0.04 * s
                    dd = map_geo(px + nx * hh, py + ny * hh, pz + nz * hh, PI, PF, GR, G0, G1, allm)
                    occ += (hh - dd) * sc; sc *= 0.8
                ao = min(1.0, max(0.0, 1.0 - 2.6 * occ))
            # 厚度（往表面内侧探 SDF：薄的地方如耳朵会透光）
            thin = 0.0
            if flags[3]:
                for s in range(2):
                    hh = 0.03 + 0.05 * s
                    dd = map_geo(px - nx * hh, py - ny * hh, pz - nz * hh, PI, PF, GR, G0, G1, allm)
                    thin += max(0.0, hh + dd) / hh * 0.5    # 实心处 dd≈-hh → 0；薄处 → 正
                thin = min(1.0, thin)
            # ---- 黏土着色
            wrap = 0.3
            dif = max(0.0, (ndl + wrap) / (1 + wrap))                       # wrap lighting（GPU Gems 16）
            sct = 0.0
            if flags[3]:
                q = (ndl + wrap) / (1 + wrap)
                sct = min(1.0, max(0.0, q / 0.3)) * min(1.0, max(0.0, (0.6 - q) / 0.3))   # 明暗交界带
            hx, hy, hz = L[0] - dx, L[1] - dy, L[2] - dz
            hl = math.sqrt(hx * hx + hy * hy + hz * hz); hx /= hl; hy /= hl; hz /= hl
            ndh = max(0.0, nx * hx + ny * hy + nz * hz)
            ndv = max(0.0, -(nx * dx + ny * dy + nz * dz))
            fre = 0.04 + 0.96 * (1.0 - max(0.0, -(hx * dx + hy * dy + hz * dz))) ** 5
            pw = 6.0 + 90.0 * gl                                                   # 黏土宽而弱的高光；眼珠窄而亮
            spec = (0.10 + 1.6 * gl) * ndh ** pw * max(ndl, 0.0) * fre * 6.0
            sky = 0.5 + 0.5 * ny
            bounce = max(0.0, -ny) * 0.5 + 0.15
            rim = (1.0 - ndv) ** 3
            back = max(0.0, -(dx * L[0] + dy * L[1] + dz * L[2]))   # 视线与光反向时（逆光）
            for c in range(3):
                alb = (cr, cg, cb)[c]
                key = (1.0, 0.86, 0.70)[c] * 2.3
                shc = sh ** (1.0, 1.2, 1.5)[c]                                    # 半影偏暖（IQ 三灯）
                v = alb * key * dif * shc
                v += alb * (0.30, 0.10, 0.04)[c] * sct * 1.2 * (0.4 + 0.6 * shc)  # 交界处的红晕 = SSS 感
                v += alb * (0.42, 0.48, 0.60)[c] * sky * ao * 0.55                        # 天光
                v += alb * (0.55, 0.40, 0.28)[c] * bounce * ao * 0.45               # 地面暖反射
                v += alb * (1.0, 0.75, 0.55)[c] * rim * 0.22 * ao                  # 柔和轮廓光
                v += alb * (1.0, 0.45, 0.30)[c] * thin * (0.35 + 0.65 * back) * 0.8   # 透光
                v += spec * (1.0, 0.95, 0.88)[c] * shc
                img[j, i, c] = v
            dep[j, i] = t
    return img, dep

def post(img, dep, focus, W=1080, H=1920):
    img = cv2.resize(img.astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    dep = cv2.resize(dep.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    img = np.maximum(img, 0) * 0.85
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14                     # ACES 拟合（Narkowicz）
    img = np.clip((img * (a * img + b)) / (img * (c * img + d) + e), 0, 1)
    img = img ** (1 / 2.2)
    coc = np.clip(np.abs(dep - focus) / 2.0, 0, 1)[..., None]
    sm = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)       # 大半径模糊在 1/4 分辨率做
    up = lambda a: cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)
    b1 = cv2.GaussianBlur(img, (0, 0), 3); b2 = up(cv2.GaussianBlur(sm, (0, 0), 2.3))
    img = img * np.clip(1 - coc * 2, 0, 1) + b1 * np.clip(1 - np.abs(coc * 2 - 1), 0, 1) + b2 * np.clip(coc * 2 - 1, 0, 1)
    glow = up(cv2.GaussianBlur(sm, (0, 0), 6)); img = img * 0.9 + glow * 0.1   # 柔光（屏幕空间“扩散”）
    g = img.mean(2, keepdims=True); img = g + (img - g) * 1.12
    img = img * np.array([1.02, 1.0, 0.96], np.float32) + np.array([0.012, 0.006, 0.0], np.float32)  # 暖调
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
    img *= (1 - 0.3 * np.clip(r - 0.22, 0, 1) ** 1.5)[..., None]
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)

if __name__ == "__main__":
    w, h = int(sys.argv[1]), int(sys.argv[2])
    args = set(sys.argv[3:])
    flags = np.array([0 if "noshadow" in args else 1, 0 if "noao" in args else 1, 0 if "nobump" in args else 1,
                      0 if "nosss" in args else 1, 0 if "nocull" in args else 1, 0 if "norelax" in args else 1,
                      0 if "central" in args else 1], np.int64)
    PI, PF, GR, G0, G1 = build()
    CAM = np.array([0.0, 1.0, 3.2]); TGT = np.array([0.0, 0.62, 0.0])
    L = np.array([-0.55, 0.75, 0.45]); L /= np.linalg.norm(L)
    t0 = time.time()
    ti = np.zeros((8, 8, 3)); td = np.zeros((8, 8))
    render(8, 8, 0, 8, 0, 8, CAM, TGT, 0.77, L, PI, PF, GR, G0, G1, ti, td, flags, 0.0)
    print("jit", round(time.time() - t0, 1))
    img = np.zeros((h, w, 3)); dep = np.zeros((h, w))
    t0 = time.time()
    render(w, h, 0, w, 0, h, CAM, TGT, math.radians(44), L, PI, PF, GR, G0, G1, img, dep, flags, 0.0)
    tr = time.time() - t0
    t0 = time.time(); out = post(img, dep, 3.15); tp = time.time() - t0
    tag = "_".join(sorted(args)) or "full"
    cv2.imwrite(f"/workspace/work/research/proto_{w}x{h}_{tag}.png", out[..., ::-1])
    print(f"{w}x{h} {tag}: render {tr:.2f}s  post {tp:.2f}s")
