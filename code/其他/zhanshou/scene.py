# 《断桥》 shared scene pieces: ant records, renderer, leaf bridge, ditch water, rain, text overlay
import os, math, numpy as np, cv2
from world import *
from cues import *
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
FONT = "/workspace/work/tomato/NotoSansSC-Bold.otf"; FONTB = "/workspace/work/tomato/NotoSansSC-Black.otf"
BLK = np.array([0.105, 0.082, 0.068], np.float32)      # 黑潮: near-black brown
RED = np.array([0.235, 0.118, 0.062], np.float32)       # 赤岸: warm deep brown
LARVA = np.array([0.86, 0.82, 0.70], np.float32)

def ease(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def lerp(a, b, u): return a + (b - a) * u
def kf(t, keys, mode="smooth"):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            if mode == "exp": return v0 * (v1 / v0) ** ease(u)
            return v0 + (v1 - v0) * (ease(u) if mode == "smooth" else u)
    return keys[-1][1]
def sky_grad(top, bot):
    y = np.linspace(0, 1, H)[:, None, None]; return (np.array(top, np.float32) * (1 - y) + np.array(bot, np.float32) * y).astype(np.float32)

def A(x, z, hd, ph=0.0, aa=0.0, ab=0.0, mand=0.0, st=0, br=1.0, lc=0.0, col=RED, sc=1.0, lift=0.0, hero=False, gk=1.0, pitch=0.0, roll=0.0, carry=False):
    return dict(x=x, z=z, hd=hd, ph=ph, aa=aa, ab=ab, mand=mand, st=st, br=br, lc=lc, col=col, sc=sc, lift=lift, hero=hero, gk=gk, pitch=pitch, roll=roll, carry=carry)
def walker(x, z, hd, t, k=1.0, col=RED, **kw):
    """an ant walking; phase from distance travelled is supplied by caller via kw['ph'] or from t"""
    kw.setdefault("ph", (t * 2.2 * k) % 1); kw.setdefault("aa", t * 4 * k); kw.setdefault("ab", t * 4.4 * k)
    return A(x, z, hd, col=col, **kw)

def sell(img, c, ax, ang, col, th=-1):
    c = np.asarray(c, float).reshape(-1)
    if not np.isfinite(c).all() or abs(c[0]) > 2e4 or abs(c[1]) > 2e4 or not (0 < ax[0] < 3000 and 0 < ax[1] < 3000): return
    cv2.ellipse(img, (int(c[0] * SC), int(c[1] * SC)), (max(1, int(ax[0] * SC)), max(1, int(ax[1] * SC))), float(ang), 0, 360, tuple(float(v) for v in col), th, cv2.LINE_AA, SH)

# ---------------- props ----------------
GREEN = [(0.26, 0.36, 0.15), (0.32, 0.42, 0.18), (0.22, 0.30, 0.13), (0.45, 0.42, 0.24), (0.38, 0.33, 0.20)]
STONE = [(0.52, 0.46, 0.38), (0.42, 0.38, 0.33), (0.60, 0.55, 0.47), (0.36, 0.30, 0.25), (0.55, 0.45, 0.35)]
def gen_props(seed, xr, zr, npeb=0, nbl=0, pr=(0.25, 2.2), bh=(25, 95), clear=None, larvae=0, lr=(0.5, 0.75), dark=1.0):
    rng = np.random.default_rng(seed); P = []
    ok = lambda x, z: clear is None or not clear(x, z)
    for i in range(npeb):
        x, z = rng.uniform(*xr), rng.uniform(*zr)
        if ok(x, z): P.append(("p", x, z, rng.uniform(*pr) * (1 + 2 * rng.random() ** 6), tuple(np.array(STONE[rng.integers(5)]) * dark), rng.uniform(0.45, 0.8), rng.uniform(0, 6.28), 0.0))
    for i in range(nbl):
        x, z = rng.uniform(*xr), rng.uniform(*zr)
        if ok(x, z): P.append(("b", x, z, rng.uniform(*bh), rng.uniform(1.6, 4.5), rng.uniform(-0.6, 0.6), rng.uniform(0, 6.28), np.array(GREEN[rng.integers(5)]) * rng.uniform(0.75, 1.1)))
    for i in range(larvae):
        x, z = rng.uniform(*xr), rng.uniform(*zr)
        if ok(x, z): P.append(("l", x, z, rng.uniform(*lr), rng.uniform(0, 6.28)))
    return P
def tube(pts, r0, r1=None, col=(0.31, 0.25, 0.19)):
    pts = np.asarray(pts, float); r1 = r0 if r1 is None else r1
    return ("r", pts, np.linspace(r0, r1, len(pts)), np.array(col))
def spline(ctrl, n=80):
    c = np.asarray(ctrl, float); t = np.linspace(0, 1, len(c)); u = np.linspace(0, 1, n)
    return np.stack([np.interp(u, t, c[:, k]) for k in range(3)], -1) if len(c) < 3 else np.stack([np.polyval(np.polyfit(t, c[:, k], min(3, len(c) - 1)), u) for k in range(3)], -1)
def larva(img, cam, x, z, r, rot, lift=0.0, br=1.0):
    fwd = np.array([math.cos(rot), 0, math.sin(rot)]); side = np.array([-math.sin(rot), 0, math.cos(rot)]); up = np.array([0, 1.0, 0])
    C = np.array([x, r * 0.55 + lift, z])
    shaded_ellipsoid(img, cam, C, fwd, side, up, r * 1.45, r * 0.85, r * 0.8, LARVA * br, spec=0.7)
    _, zc = cam.proj(C); px = cam.f * r / zc
    if px > 12:
        for k in range(-3, 4):
            P, _ = cam.proj(np.stack([C + fwd * r * 0.3 * k + side * r * 0.75 + up * r * 0.1, C + fwd * r * 0.3 * k + up * r * 0.8, C + fwd * r * 0.3 * k - side * r * 0.75 + up * r * 0.1]))
            line(img, P, LARVA * br * 0.78, max(1, px * 0.04), 0.6)
def prop_anchor(p):
    if p[0] == "r": return p[1][len(p[1]) // 2]
    return np.array([p[1], 0.0, p[2]])

# ---------------- leaf bridge ----------------
LX0, LX1 = -19.0, 9.0; CRACK = 13.4; PET1 = 17.5
def leaf_w(s): return 4.7 * np.sin(np.pi * np.clip(s, 0, 1)) ** 0.75 * (1 - 0.22 * s) + 0.15
def leaf_h(s): return 1.25 + 0.85 * np.sin(np.pi * np.clip(s, 0, 1))
_rl = np.random.default_rng(77); LEAFN = _rl.normal(0, 1, (2, 64))
def leaf_xf(P, t):
    """rigid motion of the leaf (and anything riding it) after the break. P (...,3)"""
    u = t - TBREAK
    if u <= 0: return P
    P = np.array(P, float)
    # 1) east end drops first: rotate about z through the west bank edge
    ang = -0.42 * ease(u / 0.32) + 0.30 * ease((u - 0.32) / 0.5)
    piv = np.array([-14.0, 0.6, 0.0]); d = P - piv
    ca, sa = math.cos(ang), math.sin(ang)
    P = piv + np.stack([d[..., 0] * ca - d[..., 1] * sa, d[..., 0] * sa + d[..., 1] * ca, d[..., 2]], -1)
    # 2) slips off the bank and settles flat on the water, then drifts downstream (+z) and turns
    f = ease((u - 0.25) / 0.7)
    P[..., 1] = P[..., 1] * (1 - f) + (0.12 + 0.12 * (P[..., 1] - 1.2)) * f
    P[..., 1] += -0.15 * f * math.sin(u * 2.3) * 0.3
    dr = max(0.0, u - 0.7); slide = 2.5 * ease((u - 0.3) / 0.8)
    yaw = 0.035 * dr * (1 - 0.3 * min(1, dr / 30)); cx = -4.0 + slide; cz = 0.0 + 3.2 * dr
    d = P.copy(); d[..., 0] -= -4.0; cyw, syw = math.cos(yaw), math.sin(yaw)
    P[..., 0] = cx + d[..., 0] * cyw - d[..., 2] * syw; P[..., 2] = cz + d[..., 0] * syw + d[..., 2] * cyw
    return P
def leaf_pts(t, n=64):
    s = np.linspace(0, 1, n); x = LX0 + (LX1 - LX0) * s; w = leaf_w(s) * (1 + 0.05 * LEAFN[0, :n]); zc = 0.35 * np.sin(s * 5)
    y = leaf_h(s)
    L = np.stack([x, y + 0.45 * (w / 4.7) ** 2, zc - w], -1); R = np.stack([x, y + 0.45 * (w / 4.7) ** 2, zc + w * (1 + 0.04 * LEAFN[1, :n])], -1)
    M = np.stack([x, y + 0.03, zc], -1)
    return leaf_xf(L, t), leaf_xf(R, t), leaf_xf(M, t), s
def on_leaf(x, z):
    s = (x - LX0) / (LX1 - LX0)
    return (0 <= s <= 1) and abs(z - 0.35 * math.sin(s * 5)) < leaf_w(s) + 0.2
def surf_h(x, z, t):
    """height of the walking surface at (x,z) before the break (leaf / petiole), else 0"""
    s = (x - LX0) / (LX1 - LX0)
    if 0 <= s <= 1 and abs(z - 0.35 * math.sin(s * 5)) < leaf_w(s) + 0.6:
        w = leaf_w(s); return float(leaf_h(s) + 0.45 * (min(abs(z), w) / 4.7) ** 2 * 0.0 + 0.05)
    if LX1 < x < PET1 and abs(z) < 1.2:
        return float(lerp(1.25, 0.35, (x - LX1) / (PET1 - LX1)) + 0.45)
    return 0.0
def petiole_pts(a, b, t, n=24):
    xs = np.linspace(a, b, n); y = lerp(1.25, 0.35, (xs - LX1) / (PET1 - LX1)); return np.stack([xs, y, 0.15 * np.sin(xs)], -1)
LEAFC = np.array([0.44, 0.31, 0.17], np.float32)
def fibers_n(t):
    return int(round(kf(t, [(0, 14), (72, 14), (80, 11), (112, 9), (120, 8), (140, 5), (150, 2), (155.5, 1), (159.95, 1), (160.0, 0)], "lin")))
def draw_leaf(img, cam, t, wet=0.0):
    L, R, M, s = leaf_pts(t)
    sL, zL = cam.proj(L); sR, zR = cam.proj(R)
    if (zL < 0.5).any() or (zR < 0.5).any(): return
    col = LEAFC * (1 - 0.35 * wet)
    # thickness / underside
    off = np.array([0, -0.28, 0]); uL, _ = cam.proj(L + off); uR, _ = cam.proj(R + off)
    poly(img, np.concatenate([uL, uR[::-1]]), col * 0.38)
    poly(img, np.concatenate([sL, sR[::-1]]), col * 0.82)
    # lit half and mottling
    sM, _ = cam.proj(M)
    poly(img, np.concatenate([sL, sM[::-1]]), col * 1.02, 0.85)
    rr = np.random.default_rng(5)
    for k in range(26):   # blotches / decay spots
        u = rr.uniform(0.08, 0.92); v = rr.uniform(-0.8, 0.8); i = int(u * 63)
        P = M[i] + (R[i] - M[i]) * max(v, 0) + (L[i] - M[i]) * max(-v, 0)
        c_, z_ = cam.proj(P); r_ = cam.f * rr.uniform(0.25, 0.9) / max(z_, 0.5)
        if r_ > 0.6: sell(img, c_, (r_, r_ * 0.55), rr.uniform(0, 180), col * rr.uniform(0.55, 0.8))
    wv = max(1.0, cam.f * 0.07 / max(zL.mean(), 1))
    line(img, sM, np.minimum(1, col * 1.45 + 0.05), wv * 1.6, 0.85)
    for k in range(4, 60, 6):    # lateral veins
        for E in (L, R):
            P = np.stack([M[k], (M[k] + E[min(63, k + 5)]) / 2 + np.array([0, 0.05, 0]), E[min(63, k + 6)] * 0.85 + M[k] * 0.15])
            q, _ = cam.proj(P); line(img, q, np.minimum(1, col * 1.3 + 0.03), wv * 0.8, 0.6)
    # curled torn edges highlight
    line(img, sL, col * 0.55, wv, 0.7); line(img, sR, np.minimum(1, col * 1.3), wv * 0.8, 0.5)
    # the petiole stub riding with the leaf (west part of the crack)
    pw = petiole_pts(LX1 - 0.5, CRACK - (0.15 if t > TBREAK else 0.0), t, 14)
    root(img, cam, leaf_xf(pw, t), np.full(14, 0.55), np.array([0.40, 0.29, 0.16]) * (1 - 0.3 * wet))
def draw_petiole(img, cam, t, wet=0.0, slow=None):
    """east (fixed) petiole stub + the crack fibres"""
    pe = petiole_pts(CRACK + 0.15, PET1 + 1.5, t, 16); pe[:, 1] = np.maximum(pe[:, 1], 0.3)
    root(img, cam, pe, np.linspace(0.55, 0.75, 16), np.array([0.40, 0.29, 0.16]) * (1 - 0.3 * wet))
    n = fibers_n(t)
    a = petiole_pts(CRACK - 0.15, CRACK - 0.15, t, 1)[0]; b = petiole_pts(CRACK + 0.15, CRACK + 0.15, t, 1)[0]
    if t > TBREAK: return
    rr = np.random.default_rng(9)
    gap = 0.35 + 0.45 * (1 - n / 14)
    for k in range(14):
        if k >= n: continue
        ang = rr.uniform(0, 6.28); rad = 0.45 * math.sqrt(rr.random())
        o = np.array([0, math.sin(ang) * rad, math.cos(ang) * rad])
        trem = 0.02 * math.sin(t * (40 + 9 * k)) * (1 + 3 * (n <= 2))
        p0 = a + o - np.array([gap / 2, 0, 0]); p1 = b + o + np.array([gap / 2, trem, trem])
        mid = (p0 + p1) / 2 + np.array([0, -0.05 + trem * 2, 0.04 * math.sin(k)])
        P, zz = cam.proj(np.stack([p0, mid, p1]))
        line(img, P, (0.72, 0.62, 0.42), max(1.0, cam.f * 0.03 / zz.mean()), 0.95)
    for p_, sgn in ((a, -1), (b, 1)):   # torn fibrous faces (dark, ragged)
        for q in range(7):
            ang = q * 0.9; o = np.array([0, math.sin(ang) * 0.42, math.cos(ang) * 0.42])
            P, zz = cam.proj(np.stack([p_ + o * 0.2 + np.array([sgn * gap / 2, 0, 0]), p_ + o + np.array([sgn * (gap / 2 + 0.08 * math.sin(q * 3)), 0, 0])]))
            line(img, P, (0.24, 0.17, 0.10), max(1.0, cam.f * 0.05 / zz.mean()), 0.8)

# ---------------- ditch water / banks ----------------
def wb(t): return 12.0 + 1.6 * ease((t - 128) / 45)
def RAIN(t): return float(np.clip((t - TRAIN) / 12, 0, 1)) * (1.0 if t < 222 else lerp(1.0, 0.55, (t - 222) / 18))
def ditch_water(t, fi, cam):
    def f(img, GX, GZ, dep):
        w = wb(t); ax = np.abs(GX)
        wet = np.clip(1 - (ax - w) / 5.0, 0, 1) * (ax > w)
        img = img * (1 - 0.42 * wet[..., None])
        # bank lip: dark band right at the waterline
        lip = np.clip(1 - np.abs(ax - w) / 0.9, 0, 1)
        img = img * (1 - 0.35 * lip[..., None])
        wm = np.clip((w - ax) / 0.6, 0, 1)[..., None]
        rip = 0.5 + 0.5 * np.sin(GZ * 0.9 - t * 5.0 + np.sin(GX * 0.6 + GZ * 0.13) * 2.0) * np.sin(GZ * 0.31 + GX * 0.4 - t * 2.2)
        refl = np.clip(1 - np.exp(-dep / 140.0), 0, 1)[..., None]
        wcol = np.array([0.075, 0.085, 0.075], np.float32) + refl * np.array([0.20, 0.22, 0.21], np.float32) * (0.75 + 0.25 * RAIN(t) * 0) + rip[..., None] * 0.035
        wcol = wcol + (np.sin(GZ * 0.05 - t * 1.4 + GX * 0.2) > 0.96)[..., None] * 0.05
        return img * (1 - wm) + wcol * wm
    return f
def rain_rings(img, cam, t, fi, GX, GZ, dep, k=1.0, water_only=False, w=None):
    R = RAIN(t) * k
    if R <= 0: return
    rr = np.random.default_rng(fi); n = int(140 * R)
    ys = rr.integers(int(H * 0.2), H, n); xs = rr.integers(0, W, n)
    ov = np.zeros((H, W), np.float32)
    for x, y in zip(xs, ys):
        d = dep[y, x]
        if d > 2500: continue
        age = rr.random(); r = cam.f * (0.06 + 0.45 * age) / d
        if r < 1.5 or r > 55: continue
        ry = r * max(0.2, min(0.85, math.sin(cam.p) + cam.h / d))
        sell(ov, (x, y), (r, max(1, ry)), 0, (1.0,), max(1, int(r * 0.08)))
    img += cv2.GaussianBlur(ov, (0, 0), 0.7)[..., None] * np.array([0.30, 0.32, 0.33], np.float32) * 0.45
def rain_streaks(img, t, fi, k=1.0, light=(0.75, 0.78, 0.80)):
    R = RAIN(t) * k
    if R <= 0: return img
    rr = np.random.default_rng(fi * 7 + 1); ov = np.zeros((H // 2, W // 2), np.float32)
    for i in range(int(420 * R)):
        x, y = rr.uniform(-40, W // 2 + 40), rr.uniform(-60, H // 2); L = rr.uniform(18, 60); dx = L * 0.12
        cv2.line(ov, (int(x), int(y)), (int(x + dx), int(y + L)), rr.uniform(0.25, 1.0), 1, cv2.LINE_AA)
    for i in range(int(6 * R)):    # big near drops, out of focus
        x, y = rr.uniform(0, W // 2), rr.uniform(0, H // 2); cv2.line(ov, (int(x), int(y)), (int(x + 6), int(y + 70)), 1.0, 5, cv2.LINE_AA)
    ov = cv2.GaussianBlur(ov, (0, 0), 0.8); ov = cv2.resize(ov, (W, H))
    return img * (1 - 0.10 * R) + ov[..., None] * np.array(light, np.float32) * 0.16 * R

# ---------------- renderer ----------------
def render(cam, t, fi, mats, props, ants=(), sky=None, fogd=500.0, light=1.0, water=None, post_ground=None, decal=None,
           dofk=1.0, objlight=1.0, shadow_k=0.5, leaf=False, petiole=False, wet=0.0, rings=0.0, slow=None, extra=None, fogc=0.6):
    sky = sky if sky is not None else sky_grad((0.55, 0.60, 0.58), (0.76, 0.74, 0.64))
    img, dep, GX, GZ = ground(cam, mats, sky=sky, fogd=fogd, light=light)
    if water is not None: img = water(img, GX, GZ, dep)
    if decal is not None: decal(img, cam)
    if rings: rain_rings(img, cam, t, fi, GX, GZ, dep, rings)
    sm = np.zeros((H, W), np.float32)
    for p in props:
        if p[0] == "p":
            _, zc = cam.proj(np.array([p[1], 0, p[2]]))
            if 0.8 < zc < fogd * 6: shadow_blob(sm, cam, p[1] + 0.35 * p[3], p[2] - 0.25 * p[3], p[3] * 1.2, p[3] * 0.9, 0.3)
    for a in ants:
        if a["st"] == 3 or a.get("noshadow"): continue
        _, zc = cam.proj(np.array([a["x"], 0, a["z"]]))
        if 0.8 < zc: shadow_blob(sm, cam, a["x"] - 0.15, a["z"] + 0.12, 1.45 * a["sc"], 0.55 * a["sc"], a["hd"], float(np.clip(1 - a["lift"] / 2.5, 0, 1)) * math.exp(-zc / (fogd * 2)))
    sm = cv2.GaussianBlur(sm, (0, 0), 7); img *= (1 - shadow_k * np.clip(sm, 0, 1))[..., None]
    D = []
    for p in props:
        s_, zc = cam.proj(prop_anchor(p))
        if zc < 0.8 or zc > fogd * 6: continue
        pm = 600 + (cam.f * 3.0 * p[3] / max(zc, 1.0) if p[0] in "pl" else 0)
        if p[0] not in "rb" and (s_[0] < -pm or s_[0] > W + pm or s_[1] < -pm - 300 or s_[1] > H + pm): continue
        D.append((zc, 0, p))
    for a in ants:
        s_, zc = cam.proj(np.array([a["x"], a["lift"], a["z"]]))
        mg = 300 + cam.f * 3.5 * a["sc"] / max(zc, 1.0)
        if zc < 1.0 or zc > fogd * 6 or s_[0] < -mg or s_[0] > W + mg or s_[1] < -mg or s_[1] > H + mg: continue
        D.append((zc, 1, a))
    if leaf:
        L, R, M, _ = leaf_pts(t); _, zz = cam.proj(np.concatenate([L, R]))
        D.append((float(zz.max()) + 0.01, 2, None))
    if petiole:
        _, zz = cam.proj(petiole_pts(CRACK, PET1, t, 6)); D.append((float(zz.max()) + 0.01, 3, None))
    if extra:
        for zc, fn in extra: D.append((zc, 4, fn))
    D.sort(key=lambda d: -d[0])
    for zc, k, p in D:
        fade = math.exp(-zc / fogd)
        if k == 0:
            if p[0] == "p": pebble(img, cam, p[1], p[2], p[3], np.array(p[4]) * fade * objlight * (1 - 0.3 * wet) + (1 - fade) * fogc, p[5], p[6], p[7])
            elif p[0] == "b": blade(img, cam, p[1], p[2], p[3], p[4], p[5], p[6], np.array(p[7]) * fade * objlight + (1 - fade) * fogc, t=t, sway=0.08 + 0.25 * RAIN(t))
            elif p[0] == "l": larva(img, cam, p[1], p[2], p[3], p[4], br=objlight * (0.15 + 0.85 * fade))
            else: root(img, cam, p[1], p[2], np.array(p[3]) * (0.35 + 0.65 * fade) * objlight * (1 - 0.25 * wet))
        elif k == 1:
            a = p; br = a["br"] * (fade + (1 - fade) * (1.5 if fogc > 0.3 else 0.3)) * objlight
            ant(img, cam, a["x"], a["z"], a["hd"], a["ph"], a["aa"], a["ab"], a["mand"], int(a["st"]), scale=a["sc"], bright=br, lift=a["lift"],
                roll=a["roll"], legcurl=a["lc"], col=a["col"], gk=a["gk"], hero=a["hero"], pitch=a["pitch"])
            pxa = cam.f * 2.6 * a["sc"] / max(zc, 1e-3)
            if dofk > 0 and pxa > 50:      # ants write their own depth so DOF focuses on them, not on the ground behind
                tmp = np.zeros((H, W, 3), np.float32)
                ant(tmp, cam, a["x"], a["z"], a["hd"], a["ph"], a["aa"], a["ab"], a["mand"], int(a["st"]), scale=a["sc"], bright=1.0, lift=a["lift"],
                    roll=a["roll"], legcurl=a["lc"], col=np.full(3, 0.9, np.float32), gk=a["gk"], hero=a["hero"], pitch=a["pitch"])
                m = tmp[..., 0] > 0.05; dep[m] = np.minimum(dep[m], zc)
            if a["carry"]:
                fw = np.array([math.cos(a["hd"]), 0, math.sin(a["hd"])])
                c = np.array([a["x"], a["lift"], a["z"]]) + fw * 1.35 * a["sc"]
                larva(img, cam, c[0], c[2], 0.42 * a["sc"], a["hd"] + 1.4, lift=a["lift"] + 0.2, br=objlight * 0.7)
        elif k == 2: draw_leaf(img, cam, t, wet)
        elif k == 3: draw_petiole(img, cam, t, wet)
        else: p(img, cam)
    if dofk > 0: img = dof(img, dep, cam)
    return img

# ---------------- text ----------------
_TX = {}
def text_sprite(s, size, font=FONT, col=(255, 255, 255), box=0.0, pad=(28, 12), spacing=0):
    key = (s, size, font, col, box, spacing)
    if key in _TX: return _TX[key]
    f = ImageFont.truetype(font, size)
    if spacing:
        ws = [f.getbbox(ch)[2] - f.getbbox(ch)[0] for ch in s]; tw = sum(ws) + spacing * (len(s) - 1)
    else:
        bb = f.getbbox(s); tw = bb[2] - bb[0]
    th = int(size * 1.35); w_, h_ = tw + pad[0] * 2, th + pad[1] * 2
    im = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if box > 0: d.rounded_rectangle([0, 0, w_ - 1, h_ - 1], radius=h_ // 3, fill=(8, 8, 10, int(255 * box)))
    if spacing:
        x = pad[0]
        for ch, wch in zip(s, ws): d.text((x, pad[1] + size * 0.05), ch, font=f, fill=col + (255,)); x += wch + spacing
    else: d.text((pad[0] - f.getbbox(s)[0], pad[1] + size * 0.05 - f.getbbox(s)[1] + size * 0.12), s, font=f, fill=col + (255,))
    a = np.asarray(im).astype(np.float32) / 255; _TX[key] = a; return a
def blit(img, spr, cx, cy, alpha=1.0):
    h_, w_ = spr.shape[:2]; x0 = int(cx - w_ / 2); y0 = int(cy - h_ / 2)
    xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + w_), min(H, y0 + h_)
    if xb <= xa or yb <= ya or alpha <= 0: return
    s = spr[ya - y0:yb - y0, xa - x0:xb - x0]; a = s[..., 3:4] * alpha
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - a) + s[..., :3] * a
def fadein(t, a, b, d=0.3): return min(ease((t - a) / d), ease((b - t) / d))
def overlay_text(img, t):
    for s, a, b in SUBS:
        if a - 0.01 <= t <= b + 0.01: blit(img, text_sprite(s, 42, box=0.36), W / 2, 975, fadein(t, a, b, 0.25))
    for s, a in CHAPS:
        b = a + 3.4
        if a <= t <= b:
            al = fadein(t, a, b, 0.6); sp = text_sprite(s, 30)
            blit(img, sp, 150 + sp.shape[1] / 2, 112, al)
            img[93:133, 128:131] = img[93:133, 128:131] * (1 - al) + 0.92 * al
    s, a, b = TITLE
    if a <= t:
        al = ease((t - a) / 1.5)
        blit(img, text_sprite(s, 96, font=FONTB, col=(236, 232, 224), spacing=16, pad=(10, 10)), W / 2, H / 2 - 10, al)
    return img
