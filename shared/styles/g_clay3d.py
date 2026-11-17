# G. 真 3D 黏土：numba SDF 光线步进（平滑并集的泥块 + 透视相机 + 软阴影 + AO + 指纹凹凸 + 微距景深）
import time, math, sys
import numpy as np, numba as nb, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, "/workspace/work/styles")
from common import W, H, brand, subtitle, heart, burst, anger

# 图元：type 0=椭球 1=胶囊 2=圆角盒 ; 参数 a(3) b(3) r ; 颜色 ; 组
P_T, P_A, P_B, P_R, P_C, P_G = [], [], [], [], [], []
GROUPS = []   # (cx,cy,cz,radius,k)
def prim(t, a, b, r, c, g):
    P_T.append(t); P_A.append(a); P_B.append(b); P_R.append(r); P_C.append([x / 255 for x in c]); P_G.append(g)
def group(center, rad, k=0.07):
    GROUPS.append((*center, rad, k)); return len(GROUPS) - 1

FUR, FURD, FURL = (166, 104, 62), (118, 70, 40), (222, 180, 130)
FACE, BLUSH, INK, WHT, MOUTH = (246, 160, 150), (255, 112, 128), (40, 24, 22), (255, 255, 255), (150, 40, 54)

def monkey(x, z, s=1.0, yaw=0.0, expr="look", pose="sit", look=(0, 0), y0=0.0):
    cy, sy = math.cos(yaw), math.sin(yaw)
    def T(px, py, pz):   # 局部 → 世界（局部 +z 朝向镜头）
        px, py, pz = px * s, py * s, pz * s
        return [x + px * cy + pz * sy, py + y0, z - px * sy + pz * cy]
    g = group(T(0, 0.55, 0), 0.75 * s, 0.05 * s)
    E = lambda c, r, col: prim(0, T(*c), [r[0] * s, r[1] * s, r[2] * s], 0, col, g)
    C = lambda a, b, r, col: prim(1, T(*a), T(*b), r * s, col, g)
    E((0, 0.32, 0), (0.30, 0.34, 0.26), FUR)                 # 身体
    E((0, 0.30, 0.13), (0.20, 0.24, 0.16), FURL)             # 肚皮
    for sx in (-1, 1):
        E((sx * 0.15, 0.05, 0.16), (0.11, 0.06, 0.13), FACE)   # 脚
    if pose == "angry":
        for sx in (-1, 1):
            C((sx * 0.24, 0.45, 0.02), (sx * 0.42, 0.78, 0.06), 0.075, FUR); E((sx * 0.44, 0.83, 0.07), (0.075, 0.075, 0.075), FACE)
    elif pose == "groom":
        C((-0.24, 0.45, 0.02), (-0.18, 0.18, 0.2), 0.07, FUR)
        C((0.24, 0.45, 0.02), (0.55, 0.52, 0.12), 0.07, FUR); E((0.6, 0.53, 0.13), (0.08, 0.08, 0.08), FACE)
    else:
        for sx in (-1, 1):
            C((sx * 0.25, 0.45, 0.02), (sx * 0.2, 0.17, 0.2), 0.07, FUR)
    E((-0.3, 0.12, -0.18), (0.08, 0.06, 0.12), FURD)           # 短尾
    hy = 0.88
    E((0, hy, 0), (0.36, 0.33, 0.31), FUR)                    # 大头（Q 版）
    E((0, hy + 0.29, -0.03), (0.17, 0.06, 0.14), FURD)        # 头顶毛冠
    for sx in (-1, 1):
        E((sx * 0.36, hy + 0.03, -0.03), (0.1, 0.1, 0.06), FURD)
    # 五官单独一组：硬边，颜色干净，不和毛糊在一起
    f = group(T(0, hy, 0.25), 0.42 * s, 0.012 * s)
    F = lambda c, r, col: prim(0, T(*c), [r[0] * s, r[1] * s, r[2] * s], 0, col, f)
    FC = lambda a, b, r, col: prim(1, T(*a), T(*b), r * s, col, f)
    for sx in (-1, 1):
        F((sx * 0.37, hy + 0.03, 0.02), (0.05, 0.05, 0.03), FACE)            # 耳内
    F((0, hy - 0.02, 0.2), (0.25, 0.23, 0.12), FACE)                           # 粉色脸盘
    F((0, hy - 0.12, 0.27), (0.12, 0.08, 0.07), FACE)                          # 口鼻鼓包
    lx, ly = look
    for sx in (-1, 1):
        F((sx * 0.17, hy - 0.08, 0.27), (0.045, 0.03, 0.03), BLUSH)
        ex, ey, ez = sx * 0.095, hy + 0.035, 0.29
        if expr == "happy":
            FC((ex - 0.04, ey - 0.01, ez + 0.02), (ex, ey + 0.02, ez + 0.025), 0.014, INK)
            FC((ex, ey + 0.02, ez + 0.025), (ex + 0.04, ey - 0.01, ez + 0.02), 0.014, INK)
        else:
            rr = 0.062 if expr == "wow" else 0.052
            F((ex + lx, ey + ly, ez), (rr, rr * 1.12, 0.04), INK)
            F((ex + lx - rr * 0.32, ey + ly + rr * 0.4, ez + 0.035), (rr * 0.33, rr * 0.33, 0.012), WHT)
            F((ex + lx + rr * 0.3, ey + ly - rr * 0.35, ez + 0.035), (rr * 0.14, rr * 0.14, 0.008), WHT)
        if expr == "angry":
            FC((ex + sx * 0.06, ey + 0.1, ez + 0.0), (ex - sx * 0.04, ey + 0.065, ez + 0.02), 0.016, FURD)
    F((-0.022, hy - 0.09, 0.335), (0.01, 0.008, 0.008), INK); F((0.022, hy - 0.09, 0.335), (0.01, 0.008, 0.008), INK)
    if expr == "angry":
        F((0, hy - 0.155, 0.32), (0.06, 0.035, 0.02), MOUTH); F((0, hy - 0.135, 0.333), (0.042, 0.009, 0.006), WHT)
    elif expr == "wow":
        F((0, hy - 0.16, 0.32), (0.03, 0.038, 0.02), MOUTH)
    else:
        FC((-0.04, hy - 0.145, 0.33), (0.0, hy - 0.162, 0.336), 0.01, INK); FC((0.0, hy - 0.162, 0.336), (0.04, hy - 0.145, 0.33), 0.01, INK)

import os
TEST = os.environ.get('CLAYTEST')
# ---- 场景：小办公室，后墙 + 地面 + 窗 + 盆栽 + 前景工位隔板 ----
gw = group((0, 1, -1.6), 99, 0.0)
prim(2, [0, 1.6, -1.95], [3.0, 1.8, 0.2], 0.08, (255, 214, 168), gw)                 # 后墙
prim(2, [0, -0.1, 0], [3.0, 0.1, 3.0], 0.05, (222, 170, 122), gw)                    # 地面
gp = group((0, 1.75, -1.7), 0.9, 0.0)
prim(2, [0.0, 1.85, -1.74], [0.62, 0.38, 0.05], 0.05, (238, 206, 162), gp)          # 窗框
prim(2, [0.0, 1.85, -1.69], [0.55, 0.32, 0.03], 0.03, (150, 210, 240), gp)          # 窗玻璃（天空）
prim(0, [0.32, 1.98, -1.64], [0.1, 0.1, 0.04], 0, (255, 206, 90), gp)                # 太阳
prim(0, [-0.2, 1.78, -1.64], [0.14, 0.07, 0.04], 0, (252, 252, 248), gp)             # 云
gk = group((1.05, 0.5, -1.2), 0.6, 0.04)
prim(2, [1.05, 0.22, -1.25], [0.15, 0.2, 0.15], 0.04, (236, 116, 80), gk)            # 花盆
for ox, oy, oz in ((-0.1, 0.55, 0), (0.1, 0.6, 0.02), (0, 0.72, -0.05), (-0.05, 0.85, 0.03), (0.08, 0.82, -0.02)):
    prim(0, [1.05 + ox, oy, -1.25 + oz], [0.12, 0.09, 0.1], 0, (104, 182, 92), gk)
gb = group((-0.05, 0.05, -0.2), 0.3, 0.02)
for i in range(3):
    prim(1, [-0.15 + i * 0.07, 0.05, -0.25], [-0.08 + i * 0.07, 0.04, -0.1], 0.035, (255, 210, 70), gb)   # 香蕉
monkey(-0.8, -0.75, 0.74, 0.22, "happy", "groom")
monkey(-0.3, -0.6, 0.76, -0.18, "happy", "sit")
monkey(0.33, -0.7, 0.74, 0.2, "angry", "angry", (0.02, 0))
monkey(0.87, -0.65, 0.74, -0.22, "angry", "angry", (-0.02, 0))
# 前景：工位隔板 + 探头的猴
monkey(0.0, 1.05, 0.9, 0.0, "wow", "sit", (-0.03, 0.0), y0=-0.06)
gc = group((0, 0.6, 1.25), 1.6, 0.0)
prim(2, [0, 0.3, 1.32], [1.05, 0.42, 0.06], 0.05, (118, 176, 200), gc)               # 隔板
prim(2, [0, 0.73, 1.32], [1.07, 0.035, 0.09], 0.035, (150, 200, 222), gc)              # 隔板顶沿
gh = group((0, 0.76, 1.4), 0.4, 0.03)
for sx in (-1, 1):
    prim(0, [sx * 0.24, 0.78, 1.42], [0.09, 0.055, 0.08], 0, FACE, gh)                     # 扒着隔板的手

if TEST:
    for lst in (P_T, P_A, P_B, P_R, P_C, P_G, GROUPS): lst.clear()
    gw = group((0, 1, -1.6), 99, 0.0)
    prim(2, [0, 1.6, -1.95], [3.0, 1.8, 0.2], 0.08, (255, 214, 168), gw)
    prim(2, [0, -0.1, 0], [3.0, 0.1, 3.0], 0.05, (222, 170, 122), gw)
    monkey(-0.62, 0.0, 1.0, 0.25, "happy", "groom")
    monkey(0.0, 0.1, 1.0, 0.0, "angry", "angry")
    monkey(0.62, 0.0, 1.0, -0.25, "wow", "sit")
PT = np.array(P_T, np.int32); PA = np.array(P_A, np.float64); PB = np.array(P_B, np.float64)
PR = np.array(P_R, np.float64); PC = np.array(P_C, np.float64); PG = np.array(P_G, np.int32)
GR = np.array(GROUPS, np.float64)
NG = len(GROUPS)
G0 = np.zeros(NG, np.int32); G1 = np.zeros(NG, np.int32)
for gi in range(NG):
    idx = np.where(PG == gi)[0]; G0[gi], G1[gi] = idx.min(), idx.max() + 1

@nb.njit(fastmath=True)
def sd_prim(t, a, b, r, x, y, z):
    if t == 0:
        qx, qy, qz = (x - a[0]) / b[0], (y - a[1]) / b[1], (z - a[2]) / b[2]
        k0 = math.sqrt(qx * qx + qy * qy + qz * qz)
        mn = min(b[0], min(b[1], b[2]))
        return (k0 - 1.0) * mn
    elif t == 1:
        px, py, pz = x - a[0], y - a[1], z - a[2]
        bx, by, bz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        h = (px * bx + py * by + pz * bz) / (bx * bx + by * by + bz * bz)
        h = min(1.0, max(0.0, h))
        dx, dy, dz = px - bx * h, py - by * h, pz - bz * h
        return math.sqrt(dx * dx + dy * dy + dz * dz) - r
    else:
        qx = abs(x - a[0]) - b[0] + r; qy = abs(y - a[1]) - b[1] + r; qz = abs(z - a[2]) - b[2] + r
        ox, oy, oz = max(qx, 0.0), max(qy, 0.0), max(qz, 0.0)
        return math.sqrt(ox * ox + oy * oy + oz * oz) + min(max(qx, max(qy, qz)), 0.0) - r

@nb.njit(fastmath=True)
def bump(x, y, z):
    # 捏痕：几组不同方向的低幅正弦叠加，避免规则条纹
    v = math.sin(x * 31.0 + y * 7.0) * math.sin(y * 27.0 - z * 11.0)
    v += 0.7 * math.sin(z * 37.0 + x * 13.0 + math.sin(y * 19.0)) * math.sin(x * 9.0 - y * 33.0)
    v += 0.4 * math.sin(x * 71.0 + z * 53.0) * math.sin(y * 67.0 + x * 29.0)
    return v * 0.0009

@nb.njit(fastmath=True)
def scene(x, y, z, want_col, cout):
    best = 1e9; br, bg, bb = 0.0, 0.0, 0.0
    for gi in range(GR.shape[0]):
        dxg, dyg, dzg = x - GR[gi, 0], y - GR[gi, 1], z - GR[gi, 2]
        bd = math.sqrt(dxg * dxg + dyg * dyg + dzg * dzg) - GR[gi, 3]
        if bd > best and bd > 0.02:
            continue
        k = GR[gi, 4]
        d = 1e9; cr, cg, cb = 0.0, 0.0, 0.0
        for i in range(G0[gi], G1[gi]):
            di = sd_prim(PT[i], PA[i], PB[i], PR[i], x, y, z)
            if k > 0:
                h = max(k - abs(d - di), 0.0) / k
                nd = min(d, di) - h * h * k * 0.25
                if want_col:
                    w = 0.5 + 0.5 * (d - di) / k
                    w = min(1.0, max(0.0, w))
                    w = w * w * (3 - 2 * w)
                    cr = cr * (1 - w) + PC[i, 0] * w; cg = cg * (1 - w) + PC[i, 1] * w; cb = cb * (1 - w) + PC[i, 2] * w
                d = nd
            else:
                if di < d:
                    d = di; cr, cg, cb = PC[i, 0], PC[i, 1], PC[i, 2]
        if d < best:
            best = d; br, bg, bb = cr, cg, cb
    best += bump(x, y, z)
    if want_col:
        cout[0] = br; cout[1] = bg; cout[2] = bb
    return best

@nb.njit(parallel=True, fastmath=True)
def render(w, h, cam, tgt, fov, light):
    img = np.zeros((h, w, 3)); dep = np.zeros((h, w))
    fx, fy, fz = tgt[0] - cam[0], tgt[1] - cam[1], tgt[2] - cam[2]
    fl = math.sqrt(fx * fx + fy * fy + fz * fz); fx /= fl; fy /= fl; fz /= fl
    rx, ry, rz = -fz, 0.0, fx; rl = math.sqrt(rx * rx + rz * rz); rx /= rl; rz /= rl
    ux, uy, uz = ry * fz - rz * fy, rz * fx - rx * fz, rx * fy - ry * fx
    tn = math.tan(fov / 2)
    for j in nb.prange(h):
        col = np.zeros(3); tmp = np.zeros(3)
        for i in range(w):
            sx = (2 * (i + 0.5) / w - 1) * tn * w / h; sy = (1 - 2 * (j + 0.5) / h) * tn
            dx, dy, dz = fx + rx * sx + ux * sy, fy + ry * sx + uy * sy, fz + rz * sx + uz * sy
            dl = math.sqrt(dx * dx + dy * dy + dz * dz); dx /= dl; dy /= dl; dz /= dl
            t = 0.0; hit = False
            for s in range(140):
                px, py, pz = cam[0] + dx * t, cam[1] + dy * t, cam[2] + dz * t
                d = scene(px, py, pz, False, tmp)
                if d < 0.0008 * t:
                    hit = True; break
                t += d * 0.85
                if t > 20: break
            if not hit:
                img[j, i, 0] = 1.0; img[j, i, 1] = 0.9; img[j, i, 2] = 0.8; dep[j, i] = 20; continue
            px, py, pz = cam[0] + dx * t, cam[1] + dy * t, cam[2] + dz * t
            scene(px, py, pz, True, col)
            e = 0.0015
            nx = scene(px + e, py, pz, False, tmp) - scene(px - e, py, pz, False, tmp)
            ny = scene(px, py + e, pz, False, tmp) - scene(px, py - e, pz, False, tmp)
            nz = scene(px, py, pz + e, False, tmp) - scene(px, py, pz - e, False, tmp)
            nl = math.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9; nx /= nl; ny /= nl; nz /= nl
            # 软阴影
            sh = 1.0; st = 0.02
            for s in range(40):
                d = scene(px + light[0] * st, py + light[1] * st, pz + light[2] * st, False, tmp)
                sh = min(sh, 9.0 * d / st)
                if sh < 0.02: break
                st += min(max(d, 0.01), 0.15)
                if st > 3: break
            sh = max(sh, 0.0); sh = sh * sh * (3 - 2 * sh)
            # AO
            ao = 0.0; sc = 1.0
            for s in range(1, 6):
                hh = 0.025 * s
                d = scene(px + nx * hh, py + ny * hh, pz + nz * hh, False, tmp)
                ao += (hh - d) * sc; sc *= 0.75
            ao = min(1.0, max(0.0, 1 - 3.2 * ao))
            lam = max(nx * light[0] + ny * light[1] + nz * light[2], 0.0)
            hx, hy, hz = light[0] - dx, light[1] - dy, light[2] - dz
            hl = math.sqrt(hx * hx + hy * hy + hz * hz); hx /= hl; hy /= hl; hz /= hl
            sp = max(nx * hx + ny * hy + nz * hz, 0.0) ** 28 * 0.22 * sh
            sky = 0.5 + 0.5 * ny
            fre = (1 - max(-(nx * dx + ny * dy + nz * dz), 0.0)) ** 3
            for c in range(3):
                key = (1.0, 0.93, 0.82)[c]; fill = (0.62, 0.7, 0.86)[c]; bounce = (1.0, 0.78, 0.6)[c]
                v = col[c] * (key * lam * sh * 1.05 + fill * sky * 0.32 * ao + bounce * 0.12 * (1 - ny) * ao)
                v += col[c] * fre * 0.25 * ao       # 次表面感的边缘发亮
                v += sp
                img[j, i, c] = v
            dep[j, i] = t
    return img, dep

CAM = np.array([0.0, 2.2, 6.0]); TGT = np.array([0.0, 0.7, -0.4])
if TEST: CAM = np.array([0.0, 1.0, 3.2]); TGT = np.array([0.0, 0.62, 0.0])
L = np.array([-0.55, 0.75, 0.45]); L /= np.linalg.norm(L)

def frame(res=0.5):
    w, h = int(W * res), int(H * res)
    img, dep = render(w, h, CAM, TGT, math.radians(44), L)
    img = np.clip(img, 0, 1) ** (1 / 1.12)
    img = cv2.resize(img.astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    dep = cv2.resize(dep.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    # 微距景深：焦点在中景猴子（距离≈5.1）
    coc = np.clip(np.abs(dep - (3.15 if TEST else 6.7)) / 3.0, 0, 1)
    b1 = cv2.GaussianBlur(img, (0, 0), 3); b2 = cv2.GaussianBlur(img, (0, 0), 8)
    c = coc[..., None]
    img = img * np.clip(1 - c * 2, 0, 1) + b1 * np.clip(1 - np.abs(c * 2 - 1), 0, 1) + b2 * np.clip(c * 2 - 1, 0, 1)
    g = img.mean(2, keepdims=True); img = g + (img - g) * 1.1
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
    img *= (1 - 0.28 * np.clip(r - 0.25, 0, 1)[..., None])
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    heart(d, 250, 800, 34, (255, 110, 145)); heart(d, 310, 735, 22, (255, 145, 168))
    burst(d, 790, 790, 62, 34, (255, 210, 80)); burst(d, 790, 790, 36, 20, (240, 90, 66)); anger(d, 640, 800, 26, (232, 74, 66))
    brand(im, dark_text=(120, 70, 40), pill=(255, 250, 240, 240), title_col=(120, 70, 40), title_bg=(255, 250, 240, 170))
    subtitle(im, box=(92, 58, 40, 215), col=(255, 248, 236), hl=["吵架", "好朋友"], hlcol=(255, 200, 120))
    return im

if __name__ == "__main__":
    res = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    t0 = time.time(); render(16, 28, CAM, TGT, 0.6, L); print("jit", round(time.time() - t0, 1))
    t0 = time.time(); im = frame(res); print("G frame sec", round(time.time() - t0, 2))
    im.save("/workspace/work/styles/" + ("G_test.png" if TEST else "G_clay3d.png"))
