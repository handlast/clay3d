# 2.5D macro renderer: perspective ground (remapped procedural textures), props, ants, DOF, grade. Units: mm.
import numpy as np, cv2, math
from tex import pyr, TS, S as TEXS
W, H = 1920, 1080
F = 1500.0
SH = 8   # cv2 subpixel shift
SC = float(1 << SH)

class Cam:
    def __init__(s, x, z, h, pitch, yaw=0.0, f=F, focus=None, aperture=1.0, roll=0.0):
        s.x, s.z, s.h, s.p, s.yaw, s.f, s.roll = x, z, h, math.radians(pitch), math.radians(yaw), f, roll
        s.focus = focus if focus else h / max(0.05, math.sin(s.p)) ; s.ap = aperture
        s.cp, s.sp, s.cy, s.sy = math.cos(s.p), math.sin(s.p), math.cos(s.yaw), math.sin(s.yaw)
    def proj(s, P):
        P = np.asarray(P, np.float64); dx = P[..., 0] - s.x; dy = P[..., 1] - s.h; dz = P[..., 2] - s.z
        xr = dx * s.cy - dz * s.sy; zr = dx * s.sy + dz * s.cy
        zc = zr * s.cp - dy * s.sp; yc = zr * s.sp + dy * s.cp
        zc = np.maximum(zc, 1e-3)
        return np.stack([W / 2 + s.f * xr / zc, H / 2 - s.f * yc / zc], -1), zc
    def rays(s, w, h):
        u = (np.arange(w) + 0.5) * (W / w); v = (np.arange(h) + 0.5) * (H / h)
        U, V = np.meshgrid(u, v)
        dxc = (U - W / 2) / s.f; dyc = -(V - H / 2) / s.f
        # camera -> world: inverse pitch then yaw
        zr = 1.0 * s.cp + dyc * s.sp; dy = -1.0 * s.sp + dyc * s.cp
        dx = dxc * s.cy + zr * s.sy; dz = -dxc * s.sy + zr * s.cy
        return dx, dy, dz

def ground(cam, texfn, sky=(0.75, 0.72, 0.65), fogd=600.0, light=1.0):
    """texfn(gx, gz) -> list of (texname, weight array). returns img float32 HxWx3, depth (H,W)"""
    lw, lh = 480, 270
    dx, dy, dz = cam.rays(lw, lh)
    hit = dy < -1e-4
    t = np.where(hit, cam.h / np.maximum(-dy, 1e-4), 1e6)
    t = np.minimum(t, 1e6)
    gx = cam.x + dx * t; gz = cam.z + dz * t
    fp = t / cam.f / np.maximum(-dy, 0.02)          # mm per screen px on the ground
    mats = texfn(gx, gz)
    up = lambda a: cv2.resize(a.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    GX, GZ, FP, T = up(np.where(hit, gx, 0)), up(np.where(hit, gz, 0)), up(fp), up(np.minimum(t, 5e4))
    img = np.zeros((H, W, 3), np.float32)
    for name, wgt in mats:
        Wt = up(wgt) if not np.isscalar(wgt) else wgt
        if np.isscalar(Wt) and Wt == 0: continue
        L = pyr(name); k = TEXS / TS[name]
        mx = np.mod(GX * k, TEXS).astype(np.float32); my = np.mod(GZ * k, TEXS).astype(np.float32)
        lev = np.log2(np.maximum(FP * k, 1e-3))     # texture px per screen px
        acc = np.zeros((H, W, 3), np.float32); wsum = np.zeros((H, W), np.float32)
        centers = (0.0, 1.6, 3.0, 4.4)
        for i, c in enumerate(centers):
            wl = np.clip(1 - np.abs(lev - c) / 1.5, 0, 1)
            if i == 0: wl = np.where(lev < 0, 1.0, wl)
            if i == 3: wl = np.where(lev > 4.4, 1.0, wl)
            if wl.max() < 1e-3: continue
            acc += cv2.remap(L[i], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP) * wl[..., None]; wsum += wl
        acc /= np.maximum(wsum, 1e-4)[..., None]
        img += acc * (Wt[..., None] if not np.isscalar(Wt) else Wt)
    img *= light
    fog = 1 - np.exp(-T / fogd)
    hitf = up(hit.astype(np.float32))
    fog = np.maximum(fog, 1 - hitf)
    img = img * (1 - fog[..., None]) + np.array(sky, np.float32) * fog[..., None]
    return img, T, GX, GZ

# ---------------- drawing helpers (cv2, AA, float images) ----------------
def poly(img, pts, col, alpha=1.0):
    p = np.round(np.asarray(pts) * SC).astype(np.int32).reshape(-1, 1, 2)
    if alpha >= 0.999: cv2.fillPoly(img, [p], tuple(float(c) for c in col), cv2.LINE_AA, SH)
    else:
        x0, y0 = np.floor(np.asarray(pts).min(0)).astype(int) - 2; x1, y1 = np.ceil(np.asarray(pts).max(0)).astype(int) + 2
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, img.shape[1]), min(y1, img.shape[0])
        if x1 <= x0 or y1 <= y0: return
        m = np.zeros((y1 - y0, x1 - x0), np.float32)
        p2 = p - np.array([[[int(x0 * SC), int(y0 * SC)]]], np.int32)
        cv2.fillPoly(m, [p2], 1.0, cv2.LINE_AA, SH)
        m *= alpha; sub = img[y0:y1, x0:x1]; sub *= (1 - m)[..., None]; sub += m[..., None] * np.array(col, np.float32)
def line(img, pts, col, w=1.0, alpha=1.0):
    p = np.round(np.asarray(pts) * SC).astype(np.int32).reshape(-1, 1, 2)
    if alpha >= 0.999: cv2.polylines(img, [p], False, tuple(float(c) for c in col), max(1, int(round(w))), cv2.LINE_AA, SH)
    else:
        ov = img.copy(); cv2.polylines(ov, [p], False, tuple(float(c) for c in col), max(1, int(round(w))), cv2.LINE_AA, SH)
        cv2.addWeighted(ov, alpha, img, 1 - alpha, 0, img)
def disk(img, c, r, col):
    cv2.circle(img, (int(c[0] * SC), int(c[1] * SC)), max(1, int(r * SC)), tuple(float(v) for v in col), -1, cv2.LINE_AA, SH)

def ellipsoid_hull(cam, C, fwd, side, up, a, b, c, n=22):
    ph = np.linspace(0, 2 * np.pi, n, endpoint=False)[:, None]
    ring = np.concatenate([C + np.cos(ph) * fwd * a + np.sin(ph) * side * b,
                           C + np.cos(ph) * fwd * a + np.sin(ph) * up * c,
                           C + np.cos(ph) * side * b + np.sin(ph) * up * c])
    s, z = cam.proj(ring)
    hull = cv2.convexHull(s.astype(np.float32)).reshape(-1, 2)
    return hull, z.mean()

LIGHT = np.array([-0.45, 0.8, 0.35]); LIGHT /= np.linalg.norm(LIGHT)
def shaded_ellipsoid(img, cam, C, fwd, side, up, a, b, c, col, spec=0.6, rim=None):
    hull, z = ellipsoid_hull(cam, C, fwd, side, up, a, b, c)
    col = np.asarray(col, np.float32)
    poly(img, hull, col * 0.55)
    # lit side: smaller ellipsoid shifted toward the light
    lv = LIGHT; sh = 0.28
    off = (fwd * a * np.dot(lv, fwd) + side * b * np.dot(lv, side) + up * c * np.dot(lv, up)) * sh
    h2, _ = ellipsoid_hull(cam, C + off, fwd, side, up, a * 0.86, b * 0.8, c * 0.8)
    poly(img, h2, col)
    h3, _ = ellipsoid_hull(cam, C + off * 2.1, fwd, side, up, a * 0.45, b * 0.4, c * 0.35)
    poly(img, h3, col * 1.35 + 0.04, 0.8)
    if spec > 0:
        h4, _ = ellipsoid_hull(cam, C + off * 1.7 + up * c * 0.3, fwd, side, up, a * 0.22, b * 0.16, c * 0.12)
        poly(img, h4, np.minimum(1, col * 1.9 + 0.22), spec * 0.55)
    if rim is not None:
        poly(img, hull, rim, 0.0)
    return hull

def shadow_blob(mask, cam, x, z, r_along, r_side, ang, val=1.0):
    ph = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    ca, sa = math.cos(ang), math.sin(ang)
    px = x + np.cos(ph) * r_along * ca - np.sin(ph) * r_side * sa
    pz = z + np.cos(ph) * r_along * sa + np.sin(ph) * r_side * ca
    s, zz = cam.proj(np.stack([px, np.zeros_like(px), pz], -1))
    if (zz < 0.5).any(): return
    poly(mask, s, (val,))

# ---------------- props ----------------
def pebble(img, cam, x, z, r, col, squash=0.65, rot=0.0, lift=0.0):
    fwd = np.array([math.cos(rot), 0, math.sin(rot)]); side = np.array([-math.sin(rot), 0, math.cos(rot)]); up = np.array([0, 1.0, 0])
    C = np.array([x, r * squash * 0.45 + lift, z])
    shaded_ellipsoid(img, cam, C, fwd, side, up, r, r * 0.8, r * squash, col, spec=0.25)

def blade(img, cam, x, z, Hh, w, lean, ang, col, t=0.0, sway=0.0, nseg=9):
    s = np.linspace(0, 1, nseg)
    bend = lean * s ** 1.7 + sway * math.sin(t * 1.3 + x * 0.05) * s ** 2
    ca, sa = math.cos(ang), math.sin(ang)
    cx = x + bend * Hh * ca; cz = z + bend * Hh * sa; cy = Hh * s * (1 - 0.25 * abs(lean) * s)
    wid = w * (1 - s) ** 0.8 + 0.05
    nx, nz = -sa, ca
    L = np.stack([cx + nx * wid / 2, cy, cz + nz * wid / 2], -1); R = np.stack([cx - nx * wid / 2, cy, cz - nz * wid / 2], -1)
    sL, zL = cam.proj(L); sR, zR = cam.proj(R)
    if (zL < 1).any(): return
    col = np.asarray(col, np.float32)
    poly(img, np.concatenate([sL, sR[::-1]]), col * 0.7)
    M = np.stack([cx, cy, cz], -1); sM, _ = cam.proj(M)
    poly(img, np.concatenate([sL, sM[::-1]]), col * 1.05)
    line(img, sM, np.minimum(1, col * 1.4 + 0.05), max(1, 900 / max(zL.mean(), 1) * 0.06), 0.5)

def root(img, cam, pts, rads, col):
    """pts: (n,3) curve, rads: radii. drawn as overlapping shaded tubes (sorted far->near)"""
    pts = np.asarray(pts); n = len(pts)
    s, z = cam.proj(pts)
    pr = cam.f * np.asarray(rads) / z
    col = np.asarray(col, np.float32)
    if (z < 1).any(): return
    for i in np.argsort(-z):
        disk(img, s[i], pr[i], col * 0.55)
    for i in np.argsort(-z):
        disk(img, s[i] + np.array([-0.25, -0.35]) * pr[i], pr[i] * 0.7, col)
    rr = np.random.default_rng(int(abs(pts[0][0] * 7)) % 999)
    for k in range(12):          # bark streaks along the tube
        o = rr.uniform(-0.75, 0.6); c2 = col * rr.uniform(0.5, 1.25)
        line(img, s + np.array([0.15, 1.0]) * o * pr[:, None], np.clip(c2, 0, 1), max(1, pr.mean() * rr.uniform(0.04, 0.12)), 0.55)
    line(img, s + np.array([-0.35, -0.55]) * pr[:, None], np.minimum(1, col * 1.45 + 0.05), max(1, pr.mean() * 0.18), 0.45)

# ---------------- ant ----------------
ANT = np.array([0.24, 0.14, 0.085], np.float32)   # deep brown (RGB)
def ant(img, cam, x, z, hd, phase=0.0, ant_a=0.0, ant_b=0.0, mand=0.0, state=0, scale=1.0, bright=1.0, lift=0.0, roll=0.0, legcurl=0.0):
    """x,z position (mm), hd heading rad, phase walk cycle (0..1 per stride), state 3=dead (on back)."""
    s_ = scale; fwd = np.array([math.cos(hd), 0, math.sin(hd)]); side = np.array([-math.sin(hd), 0, math.cos(hd)]); up = np.array([0, 1.0, 0])
    if state == 3:   # dead: on its side/back
        up, side = side, -up
    base = np.array([x, lift, z])
    C = lambda sx, sy, sz: base + fwd * sx * s_ + side * sz * s_ + up * sy * s_
    _, zc = cam.proj(base); px = cam.f * 2.6 * s_ / zc
    col = ANT * bright
    if px < 2: return
    if px < 14:
        a, _ = cam.proj(C(0.75, 0.4, 0)); b, _ = cam.proj(C(-0.8, 0.4, 0))
        line(img, [a, b], col * 0.7, max(1, px * 0.22)); return
    lw = max(1.0, px * 0.012)
    dead = state == 3
    # legs
    legs = []
    for i, (ls, fs, fl) in enumerate(((0.22, 0.5, 0.62), (0.07, 0.0, 0.74), (-0.08, -0.6, 0.72))):
        for sd in (-1, 1):
            grp = (i + (sd > 0)) % 2
            ph = (phase + 0.5 * grp) % 1.0
            if ph < 0.5: off = 0.32 - 1.28 * ph; lf = 0.0       # stance: foot moves back
            else: off = -0.32 + 1.28 * (ph - 0.5); lf = 0.22 * math.sin((ph - 0.5) * 2 * math.pi)
            if dead or legcurl > 0:
                cf = 1.0 if dead else legcurl
                off = off * (1 - cf); lf = lf * (1 - cf) + cf * 0.55
            A = C(ls, 0.33, 0.12 * sd)
            Fz = (fl * (1 - 0.55 * (dead or legcurl > 0) * (1 if dead else legcurl))) * sd
            Fp = C(fs + off, lf - 0.0 if not dead else lf, Fz)
            Kn = A + (Fp - A) * 0.45 + up * 0.42 * s_ + side * 0.12 * sd * s_
            legs.append((A, Kn, Fp))
    for A, Kn, Fp in legs:
        P, zz = cam.proj(np.stack([A, Kn, Fp]))
        line(img, P[:2], col * 0.75, lw * 3.0); line(img, P[1:], col * 0.65, lw * 1.8)
    # body: gaster, petiole, mesosoma, head (draw far->near roughly by projected depth of centers)
    segs = [(C(-0.76, 0.42, 0), 0.43, 0.31, 0.27, 1.0), (C(-0.27, 0.40, 0), 0.09, 0.09, 0.13, 0.9),
            (C(0.07, 0.43, 0), 0.38, 0.17, 0.19, 1.0), (C(0.63, 0.46, 0), 0.28, 0.25, 0.21, 1.05)]
    order = np.argsort([-cam.proj(sg[0])[1] for sg in segs])
    for i in order:
        Cc, a, b, c, k = segs[i]
        shaded_ellipsoid(img, cam, Cc, fwd, side, up, a * s_, b * s_, c * s_, col * k, spec=0.9 if px > 60 else 0.5)
    if px > 40:
        for sd in (-1, 1):
            e, ez = cam.proj(C(0.68, 0.55, 0.2 * sd))
            disk(img, e, px * 0.018, (0.05, 0.04, 0.035)); disk(img, e + np.array([-0.3, -0.4]) * px * 0.01, px * 0.006, (0.6, 0.55, 0.5))
    # mandibles
    for sd in (-1, 1):
        m0 = C(0.86, 0.38, 0.09 * sd); m1 = C(1.02 + 0.05 * mand, 0.34, (0.03 + 0.12 * mand) * sd)
        P, _ = cam.proj(np.stack([m0, m1])); line(img, P, col * 0.8, lw * 2.2)
    # antennae (elbowed): scape + funiculus
    for sd, aa in ((-1, ant_a), (1, ant_b)):
        s0 = C(0.82, 0.55, 0.1 * sd)
        if dead: el = C(1.0, 0.5, 0.35 * sd); tp = C(1.3, 0.3, 0.6 * sd)
        else:
            el = C(1.05, 0.85, 0.33 * sd)
            tp = C(1.45 + 0.12 * math.sin(aa * 0.7), 0.3 + 0.22 * math.sin(aa * 2.1), (0.42 + 0.18 * math.sin(aa * 1.3)) * sd)
        mid = (el + tp) / 2 + up * 0.08 * s_
        P, _ = cam.proj(np.stack([s0, el, mid, tp])); line(img, P[:2], col * 0.7, lw * 1.6); line(img, P[1:], col * 0.65, lw * 1.2)
        if px > 120: disk(img, P[3], lw * 1.2, col * 0.8)
    # fine hairs on gaster for close-ups
    if px > 200:
        rr = np.random.default_rng(int(abs(x * 1000)) % 10000)
        for k in range(10):
            u = rr.uniform(-1.15, -0.5); v = rr.uniform(-0.25, 0.25)
            p0 = C(u, 0.72 - 0.4 * abs(u + 0.8), v); p1 = p0 + (up * 0.12 + fwd * -0.05) * s_
            P, _ = cam.proj(np.stack([p0, p1])); line(img, P, col * 1.6 + 0.1, 1, 0.5)

def ant_shadow(mask, cam, x, z, hd, scale=1.0, state=0):
    shadow_blob(mask, cam, x - 0.15, z + 0.12, 1.45 * scale, 0.55 * scale, hd, 1.0)

# ---------------- post ----------------
def dof(img, depth, cam, near_strength=1.0):
    coc = np.abs(1.0 / np.maximum(depth, 0.1) - 1.0 / cam.focus) * cam.focus * cam.ap * 11.0   # 0..~ px sigma
    coc = np.clip(coc, 0, 26).astype(np.float32)
    if coc.max() < 0.6: return img
    small = cv2.resize(img, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    b1 = cv2.GaussianBlur(img, (0, 0), 2.2)
    b2 = cv2.resize(cv2.GaussianBlur(small, (0, 0), 3.5), (W, H), interpolation=cv2.INTER_LINEAR)
    b3 = cv2.resize(cv2.GaussianBlur(small, (0, 0), 9.0), (W, H), interpolation=cv2.INTER_LINEAR)
    c = coc[..., None]
    w0 = np.clip(1 - c / 2.2, 0, 1); w1 = np.clip(1 - np.abs(c - 2.2) / 4.8, 0, 1) * (c > 0)
    w2 = np.clip(1 - np.abs(c - 7) / 11, 0, 1) * (c > 2.2); w3 = np.clip((c - 7) / 11, 0, 1)
    ws = w0 + w1 + w2 + w3 + 1e-6
    return (img * w0 + b1 * w1 + b2 * w2 + b3 * w3) / ws

def grade(img, lift=(0.02, 0.02, 0.025), gain=(1, 1, 1), gamma=1.0, sat=1.0, vign=0.35, warm=0.0, contrast=1.0):
    g = img.mean(2, keepdims=True); img = g + (img - g) * sat
    img = (img - 0.5) * contrast + 0.5
    img = img * np.array(gain, np.float32) + np.array(lift, np.float32)
    if warm: img = img + np.array([warm, warm * 0.35, -warm * 0.6], np.float32)
    img = np.clip(img, 0, 1) ** gamma
    if vign:
        global _V
        try: V = _V
        except NameError:
            yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
            V = _V = (1 - np.clip(r - 0.55, 0, 1) ** 1.6).astype(np.float32)
        img = img * (1 - vign + vign * V[..., None])
    return img

_GR = [np.random.default_rng(i).standard_normal((H // 2, W // 2)).astype(np.float32) for i in range(6)]
def grain(img, fi, amt=0.018):
    g = cv2.resize(_GR[fi % 6], (W, H), interpolation=cv2.INTER_LINEAR)
    return img + g[..., None] * amt

def bokeh(img, t, pts, col, alpha=0.25):
    ov = np.zeros_like(img)
    for x, y, r in pts:
        cv2.circle(ov, (int(x), int(y)), int(r), tuple(float(c) for c in col), -1, cv2.LINE_AA)
    ov = cv2.GaussianBlur(ov, (0, 0), 3)
    return img + ov * alpha
