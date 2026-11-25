# dark world map, routes, SoCal zoom, stylized Lake Hodges local map
import json, math, numpy as np, cv2, os
from world import W, H, poly, line, disk
HERE = os.path.dirname(os.path.abspath(__file__))
_LAND = None
def land():
    global _LAND
    if _LAND is None:
        d = json.load(open(os.path.join(HERE, "land.geojson"))); out = []
        for f in d["features"]:
            g = f["geometry"]; cs = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            for pg in cs: out.append(np.array(pg[0], float))
        _LAND = out
    return _LAND
def merc(lon, lat):
    lat = np.clip(lat, -80, 82)
    return np.asarray(lon), np.degrees(np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)))
class MapView:
    def __init__(s, lon, lat, k): s.lon, s.k = lon, k; _, s.my = merc(lon, lat)
    def __call__(s, lon, lat):
        x, y = merc(lon, lat); return np.stack([W / 2 + (x - s.lon) * s.k, H / 2 - (y - s.my) * s.k], -1)
BG = np.array([0.035, 0.045, 0.06], np.float32); LANDC = np.array([0.11, 0.125, 0.14], np.float32); COAST = np.array([0.30, 0.33, 0.36], np.float32)
GLOW = np.array([1.0, 0.72, 0.38], np.float32)
def base_map(mv, img=None, land_alpha=1.0):
    if img is None: img = np.ones((H, W, 3), np.float32) * BG
    # graticule
    for lon in range(-180, 181, 30):
        p = mv(np.full(50, lon), np.linspace(-75, 80, 50)); line(img, p, (0.08, 0.09, 0.11), 1, 0.7)
    for lat in range(-60, 81, 30):
        p = mv(np.linspace(-180, 180, 80), np.full(80, lat)); line(img, p, (0.08, 0.09, 0.11), 1, 0.7)
    for pg in land():
        p = mv(pg[:, 0], pg[:, 1])
        if p[:, 0].max() < -50 or p[:, 0].min() > W + 50 or p[:, 1].max() < -50 or p[:, 1].min() > H + 50: continue
        poly(img, p, LANDC, land_alpha)
    for pg in land():
        p = mv(pg[:, 0], pg[:, 1])
        if p[:, 0].max() < -50 or p[:, 0].min() > W + 50: continue
        line(img, np.vstack([p, p[:1]]), COAST, 1.4, 0.6 * land_alpha)
    return img
def arc(mv, a, b, bulge, n=80):
    t = np.linspace(0, 1, n)[:, None]; A = mv(*a); B = mv(*b)
    d = B - A; nrm = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9)
    return A + d * t + nrm * bulge * np.linalg.norm(d) * 4 * t * (1 - t)
def glow_dot(img, p, r, col, a):
    ov = np.zeros_like(img); cv2.circle(ov, (int(p[0]), int(p[1])), int(r * 3), tuple(float(c) for c in col), -1, cv2.LINE_AA)
    ov = cv2.GaussianBlur(ov, (0, 0), r * 1.5); img += ov * a * 0.8
    if a > 0.3: disk(img, p, r * 0.45, np.minimum(1, col * 0.6 + 0.5))
def glow_line(img, pts, col, w, a):
    ov = np.zeros_like(img); line(ov, pts, col, w * 3)
    img += cv2.GaussianBlur(ov, (0, 0), w * 2) * a * 0.6; line(img, pts, np.minimum(1, col * 0.7 + 0.3), w, a)

ORIGIN = (-59.0, -33.5); CA = (-118.5, 34.2); EU = (-4.0, 38.5); JP = (135.2, 34.7)
OTHERS = [(18.5, -33.9), (145.0, -37.8), (-157.9, 21.3), (174.8, -36.9), (-16.3, 28.3)]
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def world_map(t, t0):
    u = t - t0
    k = 5.2 * (1 + 0.06 * ease(u / 12.6)); mv = MapView(-20 + 6 * ease(u / 12.6), 12, k)
    img = base_map(mv)
    o = mv(*ORIGIN)
    glow_dot(img, o, 9, GLOW, ease((u - 0.3) / 0.8))
    routes = [(CA, -0.18, 1.2, 4.6), (EU, 0.22, 2.6, 6.0), (JP, -0.25, 4.0, 7.6)] + [(p, 0.15 * (-1) ** i, 4.6 + 0.4 * i, 7.2 + 0.4 * i) for i, p in enumerate(OTHERS)]
    for i, (dst, bul, a0, a1) in enumerate(routes):
        pr = ease((u - a0) / (a1 - a0))
        if pr <= 0: continue
        pts = arc(mv, ORIGIN, dst, bul)
        n = max(2, int(len(pts) * pr))
        major = i < 3
        glow_line(img, pts[:n], GLOW * (1 if major else 0.6), 2.2 if major else 1.3, 0.75 if major else 0.4)
        if pr > 0.98: glow_dot(img, mv(*dst), 7 if major else 4, GLOW * (1 if major else 0.6), 0.9 if major else 0.5)
    # same supercolony: CA, EU, JP pulse together + faint links
    lk = ease((u - 8.2) / 1.5)
    if lk > 0:
        pulse = 0.6 + 0.4 * math.sin((u - 8.2) * 2.6)
        for p in (CA, EU, JP): glow_dot(img, mv(*p), 13, np.array([1.0, 0.85, 0.55]), lk * pulse)
        for a, b in ((CA, EU), (EU, JP)):
            pts = arc(mv, a, b, 0.12); glow_line(img, pts, np.array([1.0, 0.85, 0.55]), 1.2, 0.35 * lk)
    return img, mv

# ---------------- local (Lake Hodges, stylized) ----------------
from tex import fbm
_LOC = {}
LH = (-117.12, 33.06)   # lake centre (approx)
def local_assets():
    if _LOC: return _LOC
    rng = np.random.default_rng(7)
    # lake: dammed river valley = meandering centreline with varying width (km) + arms
    u = np.linspace(0, 1, 160)
    cl = np.stack([-3.3 + 6.4 * u, 0.25 * np.sin(u * 7.0) + 0.12 * np.sin(u * 17 + 1) - 0.3 * u], -1)
    wd = 0.12 + 0.30 * np.sin(np.pi * u) ** 0.7 * (0.75 + 0.25 * np.sin(u * 11))
    v = np.linspace(0, 1, 40)
    arm1 = np.stack([0.6 + 0.35 * v, -0.05 - 1.1 * v + 0.1 * np.sin(v * 6)], -1); w1 = 0.16 * (1 - v) + 0.04
    arm2 = np.stack([-1.3 - 0.4 * v, 0.1 + 0.9 * v], -1); w2 = 0.12 * (1 - v) + 0.03
    _LOC.update(lake=[(cl, wd), (arm1, w1), (arm2, w2)])
    n = fbm(11, octaves=5, base=4); _LOC["terrain"] = n
    # LH colony blob: around north-east shore; boundary follows the lake's west/south edge
    t = np.linspace(0, 2 * np.pi, 220, endpoint=False)
    b = 1 + 0.12 * np.sin(5 * t + 0.5) + 0.07 * np.sin(11 * t)
    _LOC["lhc"] = np.stack([0.9 + 2.3 * np.cos(t) * b, 1.0 + 1.6 * np.sin(t) * b], -1)
    return _LOC
def local_map(t, cx, cy, kpx, alpha=1.0, regions=1.0, border_glow=1.0):
    """cx,cy km centre, kpx px per km"""
    A = local_assets()
    tr = lambda P: np.stack([W / 2 + (P[:, 0] - cx) * kpx, H / 2 - (P[:, 1] - cy) * kpx], -1)
    # terrain: contour-ish shading from fbm sampled in km space
    yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
    kx = (xx * 4 - W / 2) / kpx + cx; ky = -(yy * 4 - H / 2) / kpx + cy
    tex = A["terrain"]; S = tex.shape[0]
    hval = cv2.remap(tex, np.mod(kx * 60, S).astype(np.float32), np.mod(ky * 60, S).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    cont = (np.abs(((hval * 4) % 1.0) - 0.5) < 0.04).astype(np.float32)
    base = np.stack([0.06 + 0.015 * hval, 0.07 + 0.015 * hval, 0.07 + 0.012 * hval], -1) + cont[..., None] * 0.03
    img = cv2.resize(base.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    if regions > 0:
        ov = img.copy(); ov[:] = ov * 0.0 + np.array([0.95, 0.62, 0.25], np.float32)
        m = np.zeros((H, W), np.float32); m[:] = 1.0
        poly(m, tr(A["lhc"]), (0.0,))
        img = img * (1 - 0.15 * regions * m[..., None]) + ov * 0.15 * regions * m[..., None]
        poly(img, tr(A["lhc"]), np.array([0.25, 0.75, 0.80]), 0.24 * regions)
        line(img, np.vstack([tr(A["lhc"]), tr(A["lhc"])[:1]]), np.array([1.0, 0.95, 0.85]), 2.0, 0.8 * regions * border_glow)
    for c_, w_ in A["lake"]:
        P = tr(c_)
        for p, w in zip(P, w_): disk(img, p, w * kpx + 1.5, (0.20, 0.28, 0.33))
    for c_, w_ in A["lake"]:
        P = tr(c_)
        for p, w in zip(P, w_): disk(img, p, w * kpx, (0.03, 0.06, 0.09))
    return img, tr
# the contact point we zoom toward: where the LH blob boundary meets the lake's south-west shore
def contact_km():
    A = local_assets(); L = A["lake"][0][0]; B = A["lhc"]
    d = np.linalg.norm(L[:, None, :] - B[None, :, :], axis=2) + (L[:, None, 0] > 0.2) * 9
    i, j = np.unravel_index(np.argmin(d), d.shape)
    return (L[i] + B[j]) / 2
