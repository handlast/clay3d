# 提速版：分 4 个 pass（主光线+法线 / 稀疏阴影AO / 边缘感知插值 / 着色），并支持脏矩形 + 静态背景缓存
import math, numpy as np, numba as nb
from clay_proto import map_geo, map_full

@nb.njit(fastmath=True, cache=True)
def cam_basis(cam, tgt):
    fx, fy, fz = tgt[0] - cam[0], tgt[1] - cam[1], tgt[2] - cam[2]
    fl = math.sqrt(fx * fx + fy * fy + fz * fz); fx /= fl; fy /= fl; fz /= fl
    rx, ry, rz = -fz, 0.0, fx; rl = math.sqrt(rx * rx + rz * rz); rx /= rl; rz /= rl
    ux, uy, uz = ry * fz - rz * fy, rz * fx - rx * fz, rx * fy - ry * fx
    return fx, fy, fz, rx, ry, rz, ux, uy, uz

@nb.njit(fastmath=True, cache=True)
def ray_mask(ox, oy, oz, dx, dy, dz, GR, gm, tmin):
    for g in range(GR.shape[0]):
        cx, cy, cz = ox - GR[g, 0], oy - GR[g, 1], oz - GR[g, 2]
        b = cx * dx + cy * dy + cz * dz
        rr = GR[g, 3] + GR[g, 4] * 4
        c = cx * cx + cy * cy + cz * cz - rr * rr
        disc = b * b - c
        gm[g] = disc > 0.0 and (-b + math.sqrt(max(disc, 0.0))) > tmin

@nb.njit(parallel=True, fastmath=True, cache=True)
def pass_primary(w, h, x0, x1, y0, y1, cam, tgt, fov, PI, PF, GR, G0, G1, seed, detail,
                 P, N, C, T, RD):
    fx, fy, fz, rx, ry, rz, ux, uy, uz = cam_basis(cam, tgt)
    tn = math.tan(fov / 2); pixang = 2 * tn / h
    NG = GR.shape[0]
    for j in nb.prange(y0, y1):
        out = np.zeros(4); tmp = np.zeros(4); gm = np.ones(NG, np.bool_)
        for i in range(x0, x1):
            sx = (2 * (i + 0.5) / w - 1) * tn * w / h; sy = (1 - 2 * (j + 0.5) / h) * tn
            dx, dy, dz = fx + rx * sx + ux * sy, fy + ry * sx + uy * sy, fz + rz * sx + uz * sy
            dl = math.sqrt(dx * dx + dy * dy + dz * dz); dx /= dl; dy /= dl; dz /= dl
            RD[j, i, 0] = dx; RD[j, i, 1] = dy; RD[j, i, 2] = dz
            ray_mask(cam[0], cam[1], cam[2], dx, dy, dz, GR, gm, 0.0)
            t = 0.05; hit = False
            for s in range(160):
                rad = map_geo(cam[0] + dx * t, cam[1] + dy * t, cam[2] + dz * t, PI, PF, GR, G0, G1, gm)
                if rad < 0.5 * pixang * t:
                    hit = True; break
                t += rad
                if t > 20: break
            if not hit:
                T[j, i] = -1.0; continue
            px, py, pz = cam[0] + dx * t, cam[1] + dy * t, cam[2] + dz * t
            pix = pixang * t
            map_full(px, py, pz, PI, PF, GR, G0, G1, out, pix, seed, detail)
            e = max(0.0008, pix * 0.7)
            k0 = map_full(px + e, py - e, pz - e, PI, PF, GR, G0, G1, tmp, pix, seed, detail)
            k1 = map_full(px - e, py - e, pz + e, PI, PF, GR, G0, G1, tmp, pix, seed, detail)
            k2 = map_full(px - e, py + e, pz - e, PI, PF, GR, G0, G1, tmp, pix, seed, detail)
            k3 = map_full(px + e, py + e, pz + e, PI, PF, GR, G0, G1, tmp, pix, seed, detail)
            nx = k0 - k1 - k2 + k3; ny = -k0 - k1 + k2 + k3; nz = -k0 + k1 - k2 + k3
            nl = math.sqrt(nx * nx + ny * ny + nz * nz) + 1e-12
            P[j, i, 0] = px; P[j, i, 1] = py; P[j, i, 2] = pz
            N[j, i, 0] = nx / nl; N[j, i, 1] = ny / nl; N[j, i, 2] = nz / nl
            for c in range(4): C[j, i, c] = out[c]
            T[j, i] = t

@nb.njit(fastmath=True, cache=True)
def light_terms(px, py, pz, nx, ny, nz, L, PI, PF, GR, G0, G1, gm, allm, res3):
    ndl = nx * L[0] + ny * L[1] + nz * L[2]
    sh = 0.0
    if ndl > -0.35:
        ox, oy, oz = px + nx * 0.004, py + ny * 0.004, pz + nz * 0.004
        ray_mask(ox, oy, oz, L[0], L[1], L[2], GR, gm, 0.0)       # 阴影光线也做包围球剔除
        res = 1.0; st = 0.015; wsz = 0.12
        for s in range(36):
            hh = map_geo(ox + L[0] * st, oy + L[1] * st, oz + L[2] * st, PI, PF, GR, G0, G1, gm)
            res = min(res, hh / (wsz * st))
            st += min(max(hh, 0.012), 0.25)
            if res < -1.0 or st > 3.0: break
        res = max(res, -1.0)
        sh = 0.25 * (1.0 + res) * (1.0 + res) * (2.0 - res)
    occ = 0.0; sc = 1.0
    for s in range(4):
        hh = 0.01 + 0.04 * s
        dd = map_geo(px + nx * hh, py + ny * hh, pz + nz * hh, PI, PF, GR, G0, G1, allm)
        occ += (hh - dd) * sc; sc *= 0.8
    ao = min(1.0, max(0.0, 1.0 - 2.6 * occ))
    thin = 0.0
    for s in range(2):
        hh = 0.03 + 0.05 * s
        dd = map_geo(px - nx * hh, py - ny * hh, pz - nz * hh, PI, PF, GR, G0, G1, allm)
        thin += max(0.0, hh + dd) / hh * 0.5
    res3[0] = sh; res3[1] = ao; res3[2] = min(1.0, thin)

@nb.njit(parallel=True, fastmath=True, cache=True)
def pass_light(x0, x1, y0, y1, stride, L, PI, PF, GR, G0, G1, P, N, T, S, done):
    # 只在每 stride×stride 的格点上算阴影/AO/厚度
    NG = GR.shape[0]
    for jj in nb.prange((y1 - y0 + stride - 1) // stride + 1):
        j = min(y0 + jj * stride, y1 - 1)
        gm = np.ones(NG, np.bool_); allm = np.ones(NG, np.bool_); r3 = np.zeros(3)
        i = x0
        while True:
            ii = min(i, x1 - 1)
            if T[j, ii] > 0 and not done[j, ii]:
                light_terms(P[j, ii, 0], P[j, ii, 1], P[j, ii, 2], N[j, ii, 0], N[j, ii, 1], N[j, ii, 2], L, PI, PF, GR, G0, G1, gm, allm, r3)
                S[j, ii, 0] = r3[0]; S[j, ii, 1] = r3[1]; S[j, ii, 2] = r3[2]; done[j, ii] = True
            if ii == x1 - 1: break
            i += stride

@nb.njit(parallel=True, fastmath=True, cache=True)
def pass_fill(x0, x1, y0, y1, stride, L, PI, PF, GR, G0, G1, P, N, T, S, done):
    # 其余像素：四个格点深度/法线都相近 → 双线性插值；否则（轮廓、接缝）补算
    NG = GR.shape[0]
    for j in nb.prange(y0, y1):
        gm = np.ones(NG, np.bool_); allm = np.ones(NG, np.bool_); r3 = np.zeros(3)
        ja = y0 + ((j - y0) // stride) * stride; jb = min(ja + stride, y1 - 1)
        fy = (j - ja) / max(1, jb - ja)
        for i in range(x0, x1):
            if T[j, i] <= 0 or done[j, i]:
                continue
            ia = x0 + ((i - x0) // stride) * stride; ib = min(ia + stride, x1 - 1)
            fx = (i - ia) / max(1, ib - ia)
            ok = True
            t0 = T[j, i]
            for (cj, ci) in ((ja, ia), (ja, ib), (jb, ia), (jb, ib)):
                if not done[cj, ci] or T[cj, ci] <= 0 or abs(T[cj, ci] - t0) > 0.02 * t0 or \
                   N[cj, ci, 0] * N[j, i, 0] + N[cj, ci, 1] * N[j, i, 1] + N[cj, ci, 2] * N[j, i, 2] < 0.9:
                    ok = False; break
            if ok:
                for c in range(3):
                    a = S[ja, ia, c] + (S[ja, ib, c] - S[ja, ia, c]) * fx
                    b = S[jb, ia, c] + (S[jb, ib, c] - S[jb, ia, c]) * fx
                    S[j, i, c] = a + (b - a) * fy
            else:
                light_terms(P[j, i, 0], P[j, i, 1], P[j, i, 2], N[j, i, 0], N[j, i, 1], N[j, i, 2], L, PI, PF, GR, G0, G1, gm, allm, r3)
                S[j, i, 0] = r3[0]; S[j, i, 1] = r3[1]; S[j, i, 2] = r3[2]

@nb.njit(parallel=True, fastmath=True, cache=True)
def pass_shade(x0, x1, y0, y1, L, N, C, T, S, RD, img, dep):
    for j in nb.prange(y0, y1):
        for i in range(x0, x1):
            if T[j, i] <= 0:
                img[j, i, 0] = 0.6; img[j, i, 1] = 0.45; img[j, i, 2] = 0.3; dep[j, i] = 20; continue
            nx, ny, nz = N[j, i, 0], N[j, i, 1], N[j, i, 2]
            dx, dy, dz = RD[j, i, 0], RD[j, i, 1], RD[j, i, 2]
            cr, cg, cb, gl = C[j, i, 0], C[j, i, 1], C[j, i, 2], C[j, i, 3]
            sh, ao, thin = S[j, i, 0], S[j, i, 1], S[j, i, 2]
            ndl = nx * L[0] + ny * L[1] + nz * L[2]
            wrap = 0.3
            q = (ndl + wrap) / (1 + wrap)
            dif = max(0.0, q)
            sct = min(1.0, max(0.0, q / 0.3)) * min(1.0, max(0.0, (0.6 - q) / 0.3))
            hx, hy, hz = L[0] - dx, L[1] - dy, L[2] - dz
            hl = math.sqrt(hx * hx + hy * hy + hz * hz); hx /= hl; hy /= hl; hz /= hl
            ndh = max(0.0, nx * hx + ny * hy + nz * hz)
            ndv = max(0.0, -(nx * dx + ny * dy + nz * dz))
            fre = 0.04 + 0.96 * (1.0 - max(0.0, -(hx * dx + hy * dy + hz * dz))) ** 5
            pw = 6.0 + 90.0 * gl
            spec = (0.10 + 1.6 * gl) * ndh ** pw * max(ndl, 0.0) * fre * 6.0
            sky = 0.5 + 0.5 * ny
            bounce = max(0.0, -ny) * 0.5 + 0.15
            rim = (1.0 - ndv) ** 3
            back = max(0.0, -(dx * L[0] + dy * L[1] + dz * L[2]))
            for c in range(3):
                alb = (cr, cg, cb)[c]
                shc = sh ** (1.0, 1.2, 1.5)[c]
                v = alb * (1.0, 0.86, 0.70)[c] * 2.3 * dif * shc
                v += alb * (0.30, 0.10, 0.04)[c] * sct * 1.2 * (0.4 + 0.6 * shc)
                v += alb * (0.42, 0.48, 0.60)[c] * sky * ao * 0.55
                v += alb * (0.55, 0.40, 0.28)[c] * bounce * ao * 0.45
                v += alb * (1.0, 0.75, 0.55)[c] * rim * 0.22 * ao
                v += alb * (1.0, 0.45, 0.30)[c] * thin * (0.35 + 0.65 * back) * 0.8
                v += spec * (1.0, 0.95, 0.88)[c] * shc
                img[j, i, c] = v
            dep[j, i] = T[j, i]

class Renderer:
    """用法: r = Renderer(w, h); img, dep = r.frame(cam, tgt, fov, L, PI, PF, GR, G0, G1, seed, rect=None)
    rect=(x0,x1,y0,y1) 时只重算该矩形，其余像素沿用上一帧缓冲（静态背景复用）。"""
    def __init__(self, w, h, stride=2):
        self.w, self.h, self.stride = w, h, stride
        self.P = np.zeros((h, w, 3)); self.N = np.zeros((h, w, 3)); self.C = np.zeros((h, w, 4))
        self.T = np.zeros((h, w)); self.S = np.zeros((h, w, 3)); self.RD = np.zeros((h, w, 3))
        self.done = np.zeros((h, w), np.bool_)
        self.img = np.zeros((h, w, 3)); self.dep = np.zeros((h, w))
    def frame(self, cam, tgt, fov, L, PI, PF, GR, G0, G1, seed=0.0, rect=None, detail=True):
        x0, x1, y0, y1 = rect if rect else (0, self.w, 0, self.h)
        self.done[y0:y1, x0:x1] = False
        pass_primary(self.w, self.h, x0, x1, y0, y1, cam, tgt, fov, PI, PF, GR, G0, G1, seed, detail,
                     self.P, self.N, self.C, self.T, self.RD)
        pass_light(x0, x1, y0, y1, self.stride, L, PI, PF, GR, G0, G1, self.P, self.N, self.T, self.S, self.done)
        pass_fill(x0, x1, y0, y1, self.stride, L, PI, PF, GR, G0, G1, self.P, self.N, self.T, self.S, self.done)
        pass_shade(x0, x1, y0, y1, L, self.N, self.C, self.T, self.S, self.RD, self.img, self.dep)
        return self.img, self.dep

def screen_rect(cam, tgt, fov, w, h, spheres, pad=8):
    """把若干包围球 (cx,cy,cz,r) 投影成屏幕矩形（含阴影落点时把地面投影点也放进来）。"""
    f = tgt - cam; f /= np.linalg.norm(f)
    r = np.array([-f[2], 0, f[0]]); r /= np.linalg.norm(r); u = np.cross(r, f)
    tn = math.tan(fov / 2); xs, ys = [], []
    for cx, cy, cz, rad in spheres:
        v = np.array([cx, cy, cz]) - cam; zc = v @ f
        if zc <= rad: return (0, w, 0, h)
        sx = (v @ r) / zc / (tn * w / h); sy = (v @ u) / zc / tn; rr = rad / zc / tn * 1.15
        xs += [sx - rr * h / w, sx + rr * h / w]; ys += [sy - rr, sy + rr]
    x0 = int(max(0, (min(xs) + 1) / 2 * w - pad)); x1 = int(min(w, (max(xs) + 1) / 2 * w + pad))
    y0 = int(max(0, (1 - max(ys)) / 2 * h - pad)); y1 = int(min(h, (1 - min(ys)) / 2 * h + pad))
    return (x0, x1, y0, y1)
