# 穿模约束（2026-11-16，起因：《动物打工人 No.03》小丑鱼和海葵触手/珊瑚互相穿模）
#  思路：角色（鱼、猴…）是一段连续的 PRIMS；其余实心图元(mode 0)是障碍物。
#   1) owned(fn, ...)  调用建模函数并记下它占用的 PRIMS / GROUPS 区间
#   2) hull_points(rng)  在角色每个实心图元表面撒点（球/胶囊/盒 → 26 个方向）
#   3) obstacles(skip)  打包除角色、气泡等以外的实心图元（numpy 数组）
#   4) sdf(points, obs)  向量化 SDF（与 clay_proto.sd_prim 同公式，取并集 min，不做 smin → 偏保守）
#   5) need_lift(...)  沿方向 dir 至少要挪多远，才能让 min SDF ≥ margin（且更远处也都满足 → 不会卡在触手缝里来回跳）
#   6) envelope(ts, ds)  时间上的包络：提前 rise 秒升起、离开后 fall 秒落下，max-of-bumps → 连续且 ≥ 需求
#   7) translate(rng, v, anchors)  把角色整体平移（图元 + 包围组 + 锚点）
#  纯 numpy，无 numba；单帧 1 条鱼约 10–30 ms，适合预计算轨迹缓存后再渲染。
import math, numpy as np
import clay_proto as cp

def mark(): return len(cp.PRIMS), len(cp.GROUPS)

def owned(fn, *a, **k):
    p0, g0 = mark(); r = fn(*a, **k); p1, g1 = mark()
    return r, (p0, p1, g0, g1)

_DIRS = None
def _dirs():
    global _DIRS
    if _DIRS is None:
        d = [(x, y, z) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1) if (x, y, z) != (0, 0, 0)]
        d = np.array(d, float); _DIRS = d / np.linalg.norm(d, axis=1, keepdims=True)
    return _DIRS

def hull_points(rng, min_r=0.0):
    """角色实心图元表面采样点（世界坐标）"""
    D = _dirs(); out = []
    for i in range(rng[0], rng[1]):
        t, mode, a, b, r, k, c, gl, g = cp.PRIMS[i]
        if mode != 0: continue
        a = np.array(a, float); b = np.array(b, float)
        if t == 0:
            if max(b) < min_r: continue
            out.append(a + D * b)                           # 椭球：半径各向
        elif t == 1:
            if r < min_r: continue
            for h in (0.0, 0.5, 1.0): out.append(a + (b - a) * h + D * r)
        else:
            out.append(a + D * b)                           # 圆角盒：取角点方向（近似）
    return np.concatenate(out, 0) if out else np.zeros((0, 3))

def obstacles(skip=(), keep=None):
    """skip: [(p0,p1,...)] 不当障碍的区间（角色自己、气泡）；返回 dict(t, a, b, r, cen, rad)"""
    sk = np.zeros(len(cp.PRIMS), bool)
    for s in skip: sk[s[0]:s[1]] = True
    T, A, B, R = [], [], [], []
    for i, (t, mode, a, b, r, k, c, gl, g) in enumerate(cp.PRIMS):
        if sk[i] or mode != 0: continue
        if keep is not None and not keep(i): continue
        T.append(t); A.append(a); B.append(b); R.append(r)
    T = np.array(T, int); A = np.array(A, float).reshape(-1, 3); B = np.array(B, float).reshape(-1, 3); R = np.array(R, float)
    cen = np.where(T[:, None] == 1, (A + B) / 2, A)
    rad = np.where(T == 1, np.linalg.norm(B - A, axis=1) / 2 + R, np.where(T == 2, np.linalg.norm(B, axis=1), B.max(1) if len(B) else 0))
    return dict(t=T, a=A, b=B, r=R, cen=cen, rad=rad)

def near(obs, c, reach):
    m = np.linalg.norm(obs["cen"] - c, axis=1) - obs["rad"] < reach
    return {k: v[m] for k, v in obs.items()}

def sdf(P, obs):
    """P (n,3) → 每点到障碍并集的距离 (n,)"""
    n = len(P); best = np.full(n, 1e9)
    if len(obs["t"]) == 0: return best
    T, A, B, R = obs["t"], obs["a"], obs["b"], obs["r"]
    i0 = np.where(T == 0)[0]
    if len(i0):
        p = P[:, None, :] - A[i0][None]; rr = B[i0][None]
        k0 = np.linalg.norm(p / rr, axis=2); k1 = np.linalg.norm(p / (rr * rr), axis=2)
        best = np.minimum(best, (k0 * (k0 - 1) / (k1 + 1e-12)).min(1))
    i1 = np.where(T == 1)[0]
    if len(i1):
        a = A[i1][None]; ba = (B[i1] - A[i1])[None]; p = P[:, None, :] - a
        h = np.clip((p * ba).sum(2) / ((ba * ba).sum(2) + 1e-12), 0, 1)
        best = np.minimum(best, (np.linalg.norm(p - ba * h[..., None], axis=2) - R[i1][None]).min(1))
    i2 = np.where(T == 2)[0]
    if len(i2):
        r = R[i2][None]; q = np.abs(P[:, None, :] - A[i2][None]) - B[i2][None] + r[..., None]
        d = np.linalg.norm(np.maximum(q, 0), axis=2) + np.minimum(q.max(2), 0) - r
        best = np.minimum(best, d.min(1))
    return best

def clearance(P, obs): return float(sdf(P, obs).min()) if len(P) else 1e9

def need_lift(P, obs, margin=0.03, direction=(0, 1, 0), dmax=0.8, step=0.01, run=0.06):
    """最小 d ≥ 0，使 P + d·dir 与障碍保持 ≥ margin，并且从 d 再往前 run 这一段也都满足
    （不会选到两根触手之间的窄缝 → 相邻帧不在缝/顶之间来回跳）。原位已满足 → 0。
    只保留“扫掠胶囊”（鱼包围球沿 dir 移动 dmax）附近的障碍；由近到远扫描，满足即停。"""
    v = np.asarray(direction, float); v /= np.linalg.norm(v)
    if len(P) == 0 or len(obs["t"]) == 0: return 0.0
    c = P.mean(0); R = np.linalg.norm(P - c, axis=1).max()
    q = obs["cen"] - c; h = np.clip(q @ v, 0, dmax + run)
    m = np.linalg.norm(q - h[:, None] * v, axis=1) - obs["rad"] < R + margin + step
    ob = {k: x[m] for k, x in obs.items()}
    if len(ob["t"]) == 0 or clearance(P, ob) >= margin: return 0.0
    n = int(round(run / step)); streak = 0; first = None
    for d in np.arange(step, dmax + run + 1e-9, step):
        if clearance(P + v * d, ob) >= margin:
            if streak == 0: first = d
            streak += 1
            if streak > n:
                lo, hi = first - step, first                 # 细化到 1 mm
                for _ in range(4):
                    mm = (lo + hi) / 2
                    if clearance(P + v * mm, ob) < margin: lo = mm
                    else: hi = mm
                return float(min(hi, dmax))
        else: streak = 0
    return float(dmax)

def envelope(ts, ds, rise=0.5, fall=0.6, hold=0.12):
    """ts 升序；返回 D(ts)：max_s ds(s)·w(t-s)，w 在 |Δ|<hold 为 1，之前 rise 秒/之后 fall 秒余弦降到 0"""
    ts = np.asarray(ts, float); ds = np.asarray(ds, float); out = np.zeros_like(ds)
    for j, (s, d) in enumerate(zip(ts, ds)):
        if d <= 0: continue
        dt = ts - s
        w = np.where(np.abs(dt) <= hold, 1.0, 0.0)
        u = np.clip((-dt - hold) / rise, 0, 1); w = np.maximum(w, np.where(dt < -hold, 0.5 + 0.5 * np.cos(math.pi * u), 0))
        u = np.clip((dt - hold) / fall, 0, 1); w = np.maximum(w, np.where(dt > hold, 0.5 + 0.5 * np.cos(math.pi * u), 0))
        out = np.maximum(out, d * w)
    return out

def translate(rng, v, anchors=None):
    """把区间内图元（椭球/盒的中心、胶囊两端）和组中心平移 v；anchors(dict) 里的 3 维坐标一起平移"""
    v = np.asarray(v, float)
    for i in range(rng[0], rng[1]):
        t, mode, a, b, r, k, c, gl, g = cp.PRIMS[i]
        a = [a[j] + v[j] for j in range(3)]
        if t == 1: b = [b[j] + v[j] for j in range(3)]
        cp.PRIMS[i] = (t, mode, a, b, r, k, c, gl, g)
    for gi in range(rng[2], rng[3]):
        for j in range(3): cp.GROUPS[gi][j] += v[j]
    if anchors:
        for kk, p in list(anchors.items()):
            if isinstance(p, (list, tuple, np.ndarray)) and len(p) == 3 and not isinstance(p, str):
                try:
                    q = [float(p[j]) + v[j] for j in range(3)]
                    if isinstance(p, list): p[:] = q            # 原地改：调用方已拿到的同一个列表（如对焦点）也跟着动
                    elif isinstance(p, np.ndarray): p[:] = q
                    else: anchors[kk] = q
                except (TypeError, ValueError): pass
    return anchors

def pair_gap(rngA, rngB):
    """两个角色之间的最小距离（A 的表面点到 B 的实心图元）"""
    P = hull_points(rngA)
    keep = set(range(rngB[0], rngB[1]))
    return clearance(P, obstacles(keep=lambda i: i in keep))
