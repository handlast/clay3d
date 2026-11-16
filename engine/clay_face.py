# 面部清晰度模块（2026-11-16 用户永久要求：“脸绝不能糊”）
#  render_faces(): 全帧按 RW×RH 渲染并放大到 W×H，然后对每张脸的屏幕框做“脸部超采样”：
#     在 (W*ss)×(H*ss) 的虚拟画布上只渲染脸框那一块，INTER_AREA 缩回输出分辨率，按“椭圆羽化 × 深度接近”蒙版贴回。
#     脸框面积很大（特写）时自动降低 ss，保证单帧光线数在预算内，但不低于 1.0×输出分辨率（永远比底图 0.67× 清楚）。
#  post_faces(): 与 clay_proto.post 同一套色调（ACES/gamma/饱和/暖调/暗角），但
#     · 景深 CoC 在脸部蒙版内强制为 0（脸永远不进景深模糊）
#     · 柔光 glow 不叠在脸上
#     · 可选水下雾（只作用于比焦平面远的地方，且避开脸）
#  face_crop(): 把脸部裁出来放大 2 倍，供自检
import math, numpy as np, cv2
import clay_proto as cp
_FAST = {}

def _basis(cam, tgt):
    f = tgt - cam; f = f / np.linalg.norm(f)
    r = np.array([-f[2], 0.0, f[0]]); r /= np.linalg.norm(r); u = np.cross(r, f)
    return f, r, u

def project(p, cam, tgt, fov, W, H):
    f, r, u = _basis(np.asarray(cam, float), np.asarray(tgt, float))
    d = np.asarray(p, float) - cam; z = d @ f
    tn = math.tan(fov / 2)
    sx = (d @ r) / z / (tn * W / H); sy = (d @ u) / z / tn
    return (sx + 1) / 2 * W, (1 - sy) / 2 * H, z

def face_box(c, rad, cam, tgt, fov, W, H, pad=1.2):
    x, y, z = project(c, cam, tgt, fov, W, H)
    if z <= 0.1: return None
    rp = rad / z / math.tan(fov / 2) * H / 2
    x0, x1 = int(max(0, x - rp * pad)), int(min(W, x + rp * pad))
    y0, y1 = int(max(0, y - rp * pad)), int(min(H, y + rp * pad))
    if x1 - x0 < 8 or y1 - y0 < 8: return None
    return x0, y0, x1, y1, x, y, rp, z

def render_faces(RW, RH, W, H, cam, tgt, fov, L, PI, PF, GR, G0, G1, flags, seed, faces, ss=2.0, budget=3.0e5, min_px=18, fast=True):
    """faces: [(中心3D, 半径3D)]。返回 (线性 img W×H×3 float32, dep W×H, mask W×H, info)
    fast=True：底图用 clay_fast 4-pass（阴影/AO 稀疏采样 + 插值，约快 2×）；脸部补丁始终用完整单 pass 着色"""
    if fast:
        import clay_fast
        if (RW, RH) not in _FAST: _FAST[(RW, RH)] = clay_fast.Renderer(RW, RH)
        img, dep = _FAST[(RW, RH)].frame(cam, tgt, fov, L, PI, PF, GR, G0, G1, seed)
    else:
        img = np.zeros((RH, RW, 3)); dep = np.zeros((RH, RW))
        cp.render(RW, RH, 0, RW, 0, RH, cam, tgt, fov, L, PI, PF, GR, G0, G1, img, dep, flags, seed)
    up = cv2.resize(img.astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    du = cv2.resize(dep.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    mask = np.zeros((H, W), np.float32); info = []
    for c, rad in faces:
        b = face_box(c, rad, cam, tgt, fov, W, H)
        if b is None: continue
        x0, y0, x1, y1, fx, fy, rp, zf = b
        if rp < min_px: continue
        area = (x1 - x0) * (y1 - y0)
        s = float(min(ss, max(1.0, math.sqrt(budget / max(area, 1)))))
        W2, H2 = int(round(W * s)), int(round(H * s))
        X0, X1, Y0, Y1 = int(x0 * s), int(math.ceil(x1 * s)), int(y0 * s), int(math.ceil(y1 * s))
        X1, Y1 = min(X1, W2), min(Y1, H2)
        if fast:   # 4-pass 只算脸框（缓冲只开到 (Y1, X1)，calloc 惰性分配，实际只占脸框内存）
            import clay_fast
            R2 = clay_fast.Renderer.__new__(clay_fast.Renderer)
            R2.w, R2.h, R2.stride = W2, H2, 2
            R2.P = np.zeros((Y1, X1, 3)); R2.N = np.zeros((Y1, X1, 3)); R2.C = np.zeros((Y1, X1, 4))
            R2.T = np.zeros((Y1, X1)); R2.S = np.zeros((Y1, X1, 3)); R2.RD = np.zeros((Y1, X1, 3))
            R2.done = np.zeros((Y1, X1), np.bool_); R2.img = np.zeros((Y1, X1, 3)); R2.dep = np.zeros((Y1, X1))
            im2, de2 = R2.frame(cam, tgt, fov, L, PI, PF, GR, G0, G1, seed, rect=(X0, X1, Y0, Y1))
        else:
            im2 = np.empty((Y1, X1, 3), np.float64); de2 = np.empty((Y1, X1), np.float64)
            cp.render(W2, H2, X0, X1, Y0, Y1, cam, tgt, fov, L, PI, PF, GR, G0, G1, im2, de2, flags, seed)
        pim = cv2.resize(im2[Y0:Y1, X0:X1].astype(np.float32), (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
        pde = cv2.resize(de2[Y0:Y1, X0:X1].astype(np.float32), (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        dd = np.sqrt((xx - fx) ** 2 + (yy - fy) ** 2) / rp
        m = np.clip((1.22 - dd) / 0.3, 0, 1)                                   # 椭圆羽化
        m *= np.clip(1 - (np.abs(pde - zf) - rad * 0.9) / (rad * 0.6), 0, 1)     # 只取脸附近深度（背景不换）
        m = m * m * (3 - 2 * m)
        up[y0:y1, x0:x1] = up[y0:y1, x0:x1] * (1 - m[..., None]) + pim * m[..., None]
        du[y0:y1, x0:x1] = du[y0:y1, x0:x1] * (1 - m) + pde * m
        mask[y0:y1, x0:x1] = np.maximum(mask[y0:y1, x0:x1], m)
        info.append((x0, y0, x1, y1, round(s, 2)))
    return up, du, mask, info

def post_faces(img, dep, focus, mask, fog=None, exposure=0.85, sat=1.12, dof_band=0.6, dof_span=4.0, glow_k=0.04):
    H, W = dep.shape
    img = np.maximum(img, 0) * exposure
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    img = np.clip((img * (a * img + b)) / (img * (c * img + d) + e), 0, 1)
    img = img ** (1 / 2.2)
    if fog is not None:   # 水下雾：比焦平面远 start 之后逐渐融进水色，脸不受影响
        col, start, span, kmax = fog
        fk = (np.clip((dep - focus - start) / span, 0, 1) * kmax * (1 - mask))[..., None]
        img = img * (1 - fk) + np.array(col, np.float32)[None, None] / 255.0 * fk
    coc = np.clip((np.abs(dep - focus) - dof_band) / dof_span, 0, 1) * (1 - mask)    # 脸部 CoC 强制 0
    coc = coc[..., None]
    sm = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    up = lambda a_: cv2.resize(a_, (W, H), interpolation=cv2.INTER_LINEAR)
    wgt = np.clip(coc[..., 0] * 6, 0, 1).astype(np.float32)
    iw = img * wgt[..., None]; smw = cv2.resize(wgt, (W // 4, H // 4), interpolation=cv2.INTER_AREA)[..., None]
    smi = cv2.resize(iw, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    b1 = cv2.GaussianBlur(iw, (0, 0), 3) / (cv2.GaussianBlur(wgt, (0, 0), 3)[..., None] + 1e-4)
    b2 = up(cv2.GaussianBlur(smi, (0, 0), 2.3) / (cv2.GaussianBlur(smw, (0, 0), 2.3)[..., None] + 1e-4))
    b1 = np.where(wgt[..., None] > 0.02, b1, img); b2 = np.where(wgt[..., None] > 0.02, b2, img)
    img = img * np.clip(1 - coc * 2, 0, 1) + b1 * np.clip(1 - np.abs(coc * 2 - 1), 0, 1) + b2 * np.clip(coc * 2 - 1, 0, 1)
    glow = up(cv2.GaussianBlur(sm, (0, 0), 6))
    gk = (glow_k * (1 - mask))[..., None]                                             # 柔光不叠脸
    img = img * (1 - gk) + glow * gk
    sk = (0.6 * (1 - cv2.dilate(coc[..., 0], np.ones((9, 9), np.uint8)) * 8).clip(0, 1) * (1 - 0.4 * mask))[..., None]
    img = np.clip(img + (img - cv2.GaussianBlur(img, (0, 0), 1.6)) * sk, 0, 1)
    g = img.mean(2, keepdims=True); img = g + (img - g) * sat
    img = img * np.array([1.02, 1.0, 0.96], np.float32) + np.array([0.012, 0.006, 0.0], np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
    img *= (1 - 0.3 * np.clip(r - 0.22, 0, 1) ** 1.5)[..., None]
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)

def face_crop(rgb, box, zoom=2):
    x0, y0, x1, y1 = box[:4]
    c = rgb[y0:y1, x0:x1]
    return cv2.resize(c, ((x1 - x0) * zoom, (y1 - y0) * zoom), interpolation=cv2.INTER_NEAREST)
