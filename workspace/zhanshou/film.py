# 《斩首：最后一道防线》 9:16 renderer. python3 film.py test t.. | sheet out t.. | render f0 f1 out.mp4
# Anti-pop rules (2026-11-14): every actor exists for the whole film with continuous keyframed motion;
# no per-frame random, no index filters, no list switching; entries/exits are fades into darkness or off-frame walks.
import sys, os, math, numpy as np, cv2
from scene import *

NF = int(DUR * FPS)
QCOL = RED * 1.12

# ================= actor system =================
class Act:
    """keys: [(t, x, z), ...]. position = linear path smoothed over ±0.25 s (continuous velocity).
    fights: [(t0, t1, target)] target = Act or (x, z). during a fight the ant faces the target, jitters and snaps."""
    def __init__(s, keys, col=RED, sc=1.0, gk=1.0, hero=False, seed=0.0, fights=(), face=None, carry=False,
                 br=None, roll=None, lc=None, pitch=None, lift=None, aa=None, ab=None, hd0=None):
        s.keys = sorted(keys); s.col, s.sc, s.gk, s.hero, s.seed, s.fights, s.face, s.carry = col, sc, gk, hero, seed, list(fights), face, carry
        s.fbr, s.froll, s.flc, s.fpitch, s.flift, s.faa, s.fab, s.hd0 = br, roll, lc, pitch, lift, aa, ab, hd0
        s._tab = None
    def lin(s, t):
        K = s.keys
        if t <= K[0][0]: return np.array(K[0][1:], float)
        if t >= K[-1][0]: return np.array(K[-1][1:], float)
        for (t0, x0, z0), (t1, x1, z1) in zip(K, K[1:]):
            if t <= t1:
                u = (t - t0) / max(t1 - t0, 1e-9); return np.array([x0 + (x1 - x0) * u, z0 + (z1 - z0) * u])
    def pos(s, t): return sum(s.lin(t + d) for d in np.linspace(-0.25, 0.25, 9)) / 9
    def table(s):
        if s._tab is not None: return s._tab
        ts = np.arange(-1.0, DUR + 1.0, 1 / FPS); P = np.array([s.pos(t) for t in ts])
        v = np.gradient(P, axis=0) * FPS; spd = np.linalg.norm(v, axis=1)
        arc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
        hd = np.zeros(len(ts)); cur = s.hd0
        if cur is None:
            mv = np.nonzero(spd > 0.3)[0]; cur = math.atan2(v[mv[0], 1], v[mv[0], 0]) if len(mv) else 0.0
        for i in range(len(ts)):
            if spd[i] > 0.3: cur = math.atan2(v[i, 1], v[i, 0])
            hd[i] = cur
        hd = np.unwrap(hd)
        # facing targets (fights / explicit face) blend in over 0.3 s
        tgt = np.full(len(ts), np.nan)
        for i, t in enumerate(ts):
            for (t0, t1, T) in s.fights:
                if t0 - 0.3 <= t <= t1 + 0.3:
                    q = T.pos(t) if isinstance(T, Act) else np.array(T, float); d = q - P[i]
                    w = min(ease((t - t0 + 0.3) / 0.3), ease((t1 + 0.3 - t) / 0.3))
                    tgt[i] = math.atan2(d[1], d[0]); hd[i] = hd[i] + w * (((tgt[i] - hd[i] + math.pi) % (2 * math.pi)) - math.pi)
            if s.face is not None:
                for (t0, t1, ang) in s.face:
                    if t0 - 0.4 <= t <= t1 + 0.4:
                        w = min(ease((t - t0 + 0.4) / 0.4), ease((t1 + 0.4 - t) / 0.4))
                        hd[i] = hd[i] + w * (((ang - hd[i] + math.pi) % (2 * math.pi)) - math.pi)
        k = 7; hd = np.convolve(np.pad(np.unwrap(hd), k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), "same")[k:-k]
        s._tab = (ts, P, hd, arc, spd); return s._tab
    def fightw(s, t):
        w = 0.0
        for (t0, t1, T) in s.fights: w = max(w, min(ease((t - t0) / 0.25), ease((t1 - t) / 0.35)))
        return w
    def __call__(s, t):
        ts, P, hd, arc, spd = s.table(); i = int(np.clip(round((t + 1.0) * FPS), 0, len(ts) - 1))
        x, z = P[i]; h = hd[i]; sd = s.seed; fw = s.fightw(t)
        stride = 1.15 * s.sc
        ph = (arc[i] / stride) % 1
        if fw > 0:
            jx = 0.22 * s.sc * fw * (math.sin(t * 7.3 + sd) + 0.5 * math.sin(t * 13.1 + 2 * sd))
            jz = 0.22 * s.sc * fw * (math.sin(t * 6.1 + 3 * sd) + 0.5 * math.sin(t * 11.7 + sd))
            x += jx; z += jz; h += 0.25 * fw * math.sin(t * 9 + sd); ph = (ph + fw * t * 1.8) % 1
        mand = 0.15 + 0.15 * math.sin(t * 2 + sd)
        if fw > 0: mand = mand * (1 - fw) + fw * (0.5 + 0.5 * math.sin(t * 12 + sd))
        moving = spd[i] > 0.3 or fw > 0
        aa = t * (5.0 if moving else 2.2) + sd; ab = t * (5.4 if moving else 2.5) + 2 * sd
        if fw > 0: aa = t * 9 + sd; ab = t * 10 + sd
        a = A(float(x), float(z), float(h), ph=ph, aa=aa, ab=ab, mand=mand, col=s.col, sc=s.sc, gk=s.gk, hero=s.hero, carry=s.carry)
        for key, f in (("br", s.fbr), ("roll", s.froll), ("lc", s.flc), ("pitch", s.fpitch), ("lift", s.flift), ("aa", s.faa), ("ab", s.fab)):
            if f is not None: a[key] = f(t) if callable(f) else f
        return a

def ramp(t, t0, t1, a=0.0, b=1.0): return a + (b - a) * ease((t - t0) / max(t1 - t0, 1e-6))
def look_cam(C, T, focus=None, ap=0.8, roll=0.0):
    """C=(x,z,h) camera, T=(x,y,z) target."""
    dx, dz = T[0] - C[0], T[2] - C[1]; dh = C[2] - T[1]; dist = math.hypot(dx, dz)
    yaw = math.degrees(math.atan2(dx, dz)); pitch = math.degrees(math.atan2(dh, dist))
    return Cam(C[0], C[1], C[2], pitch, yaw, focus=focus if focus else math.hypot(dist, dh), aperture=ap, roll=roll)
def lerp3(a, b, u): return tuple(lerp(np.array(a, float), np.array(b, float), u))
def grapple(cx, cz, t, ca=BLK, cb=RED, seed=0.0, r=1.45, sc=(1.0, 1.0), spin=0.3, br=1.0):
    """two ants locked together; always active (continuous in t)."""
    u = t + 30; w = spin * math.sin(0.11 * u + seed) * 3 + seed
    c = np.array([cx + 0.3 * math.sin(u * 0.9 + seed), cz + 0.3 * math.sin(u * 0.6 + seed * 2)])
    ra = np.array([math.cos(w), math.sin(w)]) * r * 0.5; pa = c + ra; pb = c - ra
    ha = math.atan2(-ra[1], -ra[0]) + 0.22 * math.sin(u * 6 + seed); hb = ha + math.pi + 0.2 * math.sin(u * 5 + seed)
    jit = lambda k: 0.06 * math.sin(u * (23 + k) + seed * k)
    return [A(pa[0] + jit(1), pa[1] + jit(2), ha, ph=(0.2 + 0.15 * math.sin(u * 15 + seed)) % 1, aa=u * 9 + seed, ab=u * 8, mand=0.5 + 0.5 * math.sin(u * 11 + seed), col=ca, sc=sc[0], br=br),
            A(pb[0] + jit(3), pb[1] + jit(4), hb, ph=(0.6 + 0.15 * math.sin(u * 17 + seed)) % 1, aa=u * 9, ab=u * 10 + seed, mand=0.5 + 0.5 * math.sin(u * 12 + seed * 2), col=cb, sc=sc[1], br=br)]

# ================= nest world (interior) =================
SLIT = (-29.6, 47.4)                 # left root crack (enemy infiltration route)
PATH = [(3.0, 46.0), (6.5, 51.5), (10.0, 58.0), (15.0, 67.0), (22.0, 80.0), (26.0, 87.0)]   # nursery -> fork -> narrow uphill -> exit (upper right)
EXIT = (22.0, 4.0, 80.0)
FORK = (10.0, 58.0)
DRB = np.array([13.4, 0.0, 57.2]); DRT = np.array([15.8, 8.0, 60.8]); DRC = 0.3      # dead root strut: base, top, crack position
def near_path(x, z, w):
    P = np.array(PATH); best = 1e9
    for a, b in zip(P, P[1:]):
        d = b - a; u = np.clip(((x - a[0]) * d[0] + (z - a[1]) * d[1]) / (d @ d), 0, 1); q = a + d * u
        best = min(best, math.hypot(x - q[0], z - q[1]))
    return best < w
def nest_clear(x, z):
    return ((abs(x) < 12 and 30 < z < 50) or near_path(x, z, 4.0) or (-32 < x < -8 and 40 < z < 50) or (-34 < x < -26 and 38 < z < 52))
def _nest_props():
    rng = np.random.default_rng(101)
    P = gen_props(102, (-60, 60), (5, 120), npeb=900, pr=(0.12, 0.6), dark=0.42, clear=nest_clear)
    P += gen_props(103, (-5.5, 5.5), (36.5, 44.5), larvae=34, lr=(0.42, 0.6))
    # walls of the narrow uphill passage: larger stones on both sides
    Pp = np.array(PATH)
    for a, b in zip(Pp[1:], Pp[2:]):
        d = b - a; L = np.linalg.norm(d); n = np.array([-d[1], d[0]]) / L
        for k in range(int(L / 1.4)):
            q = a + d * (k / (L / 1.4))
            for sd in (-1, 1):
                o = q + n * sd * rng.uniform(4.6, 6.0)
                if sd > 0 and math.hypot(o[0] - DRB[0], o[1] - DRB[2]) < 2.2: continue
                P.append(("p", float(o[0]), float(o[1]), rng.uniform(1.3, 2.6), tuple(np.array(STONE[rng.integers(5)]) * 0.38), rng.uniform(0.6, 0.9), rng.uniform(0, 6.28), 0.0))
    # chamber roots
    P += [tube(spline([(-46, 2.6, 49.5), (-36, 3.0, 48.9), (-27, 2.4, 49.2), (-18, 1.4, 52)], 60), 2.6, 1.8, (0.26, 0.20, 0.15)),     # root over the crack
          tube(spline([(-80, 4, 95), (-20, 9, 92), (40, 7, 100), (90, 3, 92)], 70), 9, 7, (0.25, 0.19, 0.14)),
          tube(spline([(-50, 2, 10), (-46, 5, 40), (-52, 3, 90)], 50), 6, 5, (0.26, 0.20, 0.15)),
          tube(spline([(34, 2, 20), (32, 6, 45), (40, 3, 70)], 50), 6, 5, (0.26, 0.20, 0.15))]
    return P
PNEST2 = _nest_props()
# loose soil held up by the dead root: every clump exists from frame 0 and falls at TSNAP
def _soil():
    rng = np.random.default_rng(55); S = []
    for k in range(75):
        big = k < 9
        x0 = rng.uniform(6.5, 16.0); z0 = rng.uniform(54.0, 62.0); l0 = rng.uniform(6.5, 9.5) if not big else rng.uniform(7.0, 8.5)
        r = rng.uniform(1.3, 2.0) if big else rng.uniform(0.3, 0.8)
        # landing spot: spread over the fork, but keep a small gap at 断须's head so the antenna can show later
        for _ in range(20):
            x1 = x0 + rng.uniform(-2.0, 2.0); z1 = z0 + rng.uniform(-3.0, 1.5)
            if math.hypot(x1 - 13.0, z1 - 57.1) > 1.0 + r * 0.6: break
        delay = rng.uniform(0.0, 0.5) + (0.0 if big else 0.08); col = np.array([0.20, 0.15, 0.105]) * rng.uniform(0.75, 1.15)
        S.append((x0, z0, l0, x1, z1, r, delay, tuple(col), rng.uniform(0, 6.28), rng.uniform(0.55, 0.8)))
    return S
SOIL = _soil()
def soil_state(c, t):
    x0, z0, l0, x1, z1, r, dl, col, rot, sq = c
    u = t - TSNAP - dl
    if u <= 0: return x0, z0, l0 + 0.04 * math.sin(t * 3 + rot) * (t > 31) * (1 + 3 * (t > 36))   # trembling before the collapse
    g = 55.0; L = max(0.0, l0 - 0.5 * g * u * u); f = min(1.0, u / math.sqrt(2 * l0 / g))
    bounce = 0.25 * r * max(0.0, math.sin(min(1.0, (u - math.sqrt(2 * l0 / g)) / 0.25) * math.pi)) if L <= 0 else 0.0
    return x0 + (x1 - x0) * ease(f), z0 + (z1 - z0) * ease(f), L + bounce
def dead_root(img, cam, t):
    """strut from DRB to DRT with a pale split at DRC; snaps at TSNAP: the lower stub stays, upper part drops."""
    s = np.linspace(0, 1, 26); P = DRB[None] + (DRT - DRB)[None] * s[:, None]; P[:, 0] += 0.25 * np.sin(s * 5)
    rads = np.linspace(1.05, 0.8, 26); col = np.array([0.23, 0.175, 0.12])
    u = t - TSNAP; c = int(DRC * 25)
    gap = 0.06 + 0.10 * ease((t - 10) / 3) + 0.10 * ease((t - 31) / 6)
    lo, hi = P[:c].copy(), P[c + 1:].copy()
    if u > 0:
        a = min(1.0, (u / 0.45) ** 2) * 1.25            # upper part pivots and falls with the soil
        piv = hi[0].copy(); d = hi - piv; ca_, sa_ = math.cos(a), math.sin(a)
        hi = piv + np.stack([d[:, 0], d[:, 1] * ca_ - d[:, 2] * sa_, d[:, 1] * sa_ + d[:, 2] * ca_], -1)
        hi[:, 1] = np.maximum(hi[:, 1] - 0.5 * 55 * max(0, u - 0.1) ** 2, 0.4); gap += 0.6 * min(1, u / 0.3)
        hi[:, 0] -= 1.2 * min(1, u / 0.5); hi[:, 2] -= 1.6 * min(1, u / 0.5)
    hi = hi + (hi[0] - P[c])[None] * 0 + np.array([0, gap, 0])
    root(img, cam, lo, rads[:c], col); root(img, cam, hi, rads[c + 1:], col)
    # pale torn fibres in the split (visible from 10 s; they stretch, then are gone after the snap)
    if u < 0.05:
        a_, b_ = P[c - 1] + np.array([0, 0.25, 0]), hi[0] - np.array([0, 0.05, 0])
        for k in range(7):
            o = np.array([0.5 * math.cos(k * 0.9), 0, 0.5 * math.sin(k * 0.9)]) * 0.8
            Q, zz = cam.proj(np.stack([a_ + o, (a_ + b_) / 2 + o * 1.1, b_ + o]))
            if (zz > 1).all(): line(img, Q, (0.70, 0.60, 0.42), max(1.0, cam.f * 0.035 / zz.mean()), 0.9)
def soil_layer(img, cam, t):
    for c in SOIL:
        x, z, L = soil_state(c, t); pebble(img, cam, x, z, c[5], np.array(c[7]), c[9], c[8], L)
def dust(img, cam, t):
    u = t - TSNAP
    if u <= 0 or u > 5: return img
    s_, zc = cam.proj(np.array([FORK[0] + 1.5, 1.5, FORK[1] - 0.5]))
    if zc < 1: return img
    rad = cam.f * (3 + 9 * ease(u / 2.5)) / zc
    yy, xx = np.mgrid[0:H:4, 0:W:4]; g = np.exp(-(((xx - s_[0]) / rad) ** 2 + ((yy - s_[1] + rad * 0.3) / (rad * 0.7)) ** 2)).astype(np.float32)
    a = 0.55 * ease(u / 0.25) * (1 - ease((u - 1.0) / 4.0))
    g = cv2.resize(g, (W, H))[..., None]
    return img * (1 - a * g * 0.8) + a * g * 0.8 * np.array([0.30, 0.24, 0.17], np.float32)
def slit_decal(img, cam):
    ph = np.linspace(0, 2 * np.pi, 40)
    for sc_, a in ((1.5, 0.35), (1.0, 0.95)):
        P, zz = cam.proj(np.stack([SLIT[0] + np.cos(ph) * 2.0 * sc_, np.full(40, 0.02), SLIT[1] + np.sin(ph) * 1.4 * sc_], -1))
        if (zz > 0.8).sum() > 30: poly(img, P[zz > 0.8], (0.02, 0.015, 0.012), a)
def nest2(cam, t, fi, ants, glow_k=1.0, dofk=1.0, extra=None, light=0.8):
    sky = sky_grad((0.035, 0.026, 0.02), (0.10, 0.07, 0.05))
    _, zr = cam.proj(DRB + (DRT - DRB) * 0.5); _, zs = cam.proj(np.array([11.0, 0.0, 58.0]))
    ex = [(float(zr), lambda im, c: dead_root(im, c, t)), (float(zs) if t <= TSNAP else 0.5, lambda im, c: soil_layer(im, c, t))]
    img = render(cam, t, fi, mats_nest, PNEST2, ants, sky=sky, fogd=75, light=light, objlight=0.85, extra=ex + (extra or []), decal=slit_decal, fogc=0.07, dofk=dofk)
    img = glow(img, EXIT, cam, 320, (0.34, 0.25, 0.15), 0.9 * glow_k)
    img = glow(img, (0.0, 2.0, 40.0), cam, 260, (0.10, 0.07, 0.045), 0.6)
    return dust(img, cam, t)
def mats_nest(gx, gz):
    v = 0.5 + 0.5 * np.sin(gx * 0.08) * np.sin(gz * 0.06 + 1); return [("soil", v * 0.85), ("mud", (1 - v) * 0.85)]
def glow(img, p, cam, rad, col, a=1.0):
    s_, z_ = cam.proj(np.asarray(p, float))
    if z_ < 1: return img
    yy, xx = np.mgrid[0:H:4, 0:W:4]; g = np.exp(-(((xx - s_[0]) / rad) ** 2 + ((yy - s_[1]) / (rad * 0.8)) ** 2)).astype(np.float32)
    return img + cv2.resize(g, (W, H))[..., None] * np.array(col, np.float32) * a
def nlook(img, t): return grade(img, sat=0.78, contrast=1.1, gain=(1.0, 0.92, 0.82), vign=0.5, lift=(0.012, 0.01, 0.01))

# ================= interior cast (global time, one definition for the whole film) =================
QHOME = (1.5, 41.5)
Q = Act([(0, 1.5, 41.5), (4, 1.0, 41.8), (8, 1.8, 41.2), (12, 1.2, 41.6), (16.6, 1.5, 41.5), (18.8, 4.2, 47.5), (20.6, 6.6, 52.0), (21.1, 6.9, 52.6),
         (26.3, 7.1, 52.9), (28.4, 10.0, 58.0), (31.0, 15.0, 67.0), (33.6, 22.0, 80.0), (35.6, 25.5, 86.5)],
        col=QCOL, sc=2.0, gk=1.75, seed=0.5, hd0=2.6, face=[(0, 16.4, 2.9)])
C1 = Act([(0, -2.2, 42.4), (15.6, -2.2, 42.4), (17.2, 3.0, 46.0), (18.7, 6.5, 51.5), (20.2, 10.0, 58.0), (22.4, 15.0, 67.0), (25.0, 22.0, 80.0), (26.6, 25.5, 86.5)],
         col=RED, carry=True, seed=1.1, hd0=0.3)
C2 = Act([(0, 3.4, 38.6), (16.0, 3.4, 38.6), (17.6, 3.6, 45.4), (19.2, 6.8, 51.8), (20.8, 10.2, 58.2), (23.0, 15.2, 67.2), (25.6, 22.2, 80.2), (27.2, 25.7, 86.7)],
         col=RED, carry=True, seed=2.3, hd0=1.6)
D_KEYS = [(0, 24.0, 32.0), (14.6, 24.0, 32.0), (16.4, 3.0, 44.0), (17.0, -2.4, 45.4), (19.6, -2.8, 45.6), (21.2, 0.8, 47.6), (24.8, 2.4, 49.0), (25.6, 5.0, 50.4),
          (28.6, 5.3, 50.8), (30.4, 7.6, 53.6), (33.0, 9.8, 56.2), (35.2, 10.3, 56.6), (36.0, 12.1, 56.9), (60, 12.1, 56.9)]
G2 = Act([(0, 14.0, 26.0), (14.8, 14.0, 26.0), (16.6, 0.0, 43.0), (17.2, -2.6, 42.2), (21.0, -1.0, 44.8), (24.6, 2.2, 47.6), (28.4, 2.6, 47.8), (29.6, 0.6, 45.8), (60, 0.6, 45.8)],
         col=RED, seed=3.7, hd0=2.2,
         roll=lambda t: ramp(t, 28.4, 29.4, 0, 1.25), lc=lambda t: ramp(t, 28.6, 29.8, 0, 0.5) + 0.2 * math.sin(t * 6) * (t > 29.5) * ramp(t, 29.5, 33, 1, 0.2))
R1 = Act([(0, -29.6, 46.8), (5.0, -29.4, 44.4), (7.0, -26.5, 43.6), (10.4, -13.0, 45.0), (11.0, -10.6, 45.2), (12.9, -10.4, 45.2), (14.6, -8.0, 46.2),
          (17.6, -5.8, 45.8), (19.6, -5.4, 45.4), (20.3, 1.0, 48.4), (21.0, 5.0, 50.4), (26.2, 5.2, 50.6), (28.6, 5.6, 51.6), (30.8, 7.4, 53.2), (33.4, 9.6, 54.6), (60, 9.6, 54.6)],
         col=BLK, sc=0.95, seed=4.2, br=lambda t: ramp(t, 0.0, 2.2, 0.3, 1.0))
R2 = Act([(0, -40.0, 47.4), (5.4, -40.0, 47.4), (6.8, -29.6, 46.0), (8.4, -28.0, 43.8), (11.4, -13.6, 46.4), (12.2, -11.4, 46.0), (14.8, -9.0, 47.0),
          (18.0, -6.5, 47.4), (19.4, -4.6, 46.6), (21.6, 0.6, 48.4), (24.6, 1.6, 49.4), (28.4, 2.0, 48.8), (30.6, 6.2, 52.0), (33.4, 10.9, 54.0), (60, 10.9, 54.0)],
         col=BLK, sc=0.95, seed=5.9, br=lambda t: ramp(t, 6.0, 7.2, 0.0, 1.0))
R3 = Act([(0, -40.0, 47.0), (6.4, -40.0, 47.0), (7.8, -29.6, 46.0), (9.4, -28.0, 43.4), (12.4, -12.6, 43.8), (15.6, -8.4, 43.4), (18.6, -6.0, 42.6), (19.6, -5.0, 42.4),
          (22.0, 0.2, 46.6), (24.8, 1.0, 47.4), (28.4, 1.2, 47.4), (30.8, 5.4, 53.4), (33.4, 8.6, 56.4), (60, 8.6, 56.4)],
         col=BLK, sc=0.95, seed=6.6, br=lambda t: ramp(t, 7.0, 8.2, 0.0, 1.0))
G1 = Act([(0, -8.2, 44.4), (11.0, -8.2, 44.4), (12.9, -8.6, 44.2), (13.8, -9.0, 44.0), (60, -9.0, 44.0)], col=RED, seed=7.3, hd0=math.pi,
         roll=lambda t: ramp(t, 12.4, 13.2, 0, 1.35), lc=lambda t: ramp(t, 12.6, 13.6, 0, 0.55) + 0.25 * math.sin(t * 7) * (t > 13.4) * ramp(t, 13.4, 20, 1, 0.3))
D = Act(D_KEYS, col=RED, hero=True, seed=8.8, hd0=2.5,
        pitch=lambda t: ramp(t, 33.0, 33.8, 0, 0.42) * (1 - ramp(t, 34.6, 35.2)) + ramp(t, 35.6, 36.4, 0, 0.30),
        aa=None, ab=None)
# fights (set after creation so targets exist)
G1.fights = [(10.9, 12.6, R1)]
R1.fights = [(10.9, 12.9, G1), (17.6, 19.6, D), (21.0, 26.2, None), (25.6, 28.6, D), (31.6, 37.6, D)]
R2.fights = [(19.4, 21.4, D), (24.6, 29.4, G2), (33.0, 37.6, D)]
R3.fights = [(19.6, 21.8, G2), (24.8, 29.4, G2), (33.2, 37.6, D)]
D.fights = [(17.6, 19.6, R1), (19.4, 21.0, R2), (25.6, 28.6, R1), (31.2, 35.2, R2), (36.0, 37.6, tuple(DRB[[0, 2]]))]
G2.fights = [(19.6, 21.6, R3), (24.6, 28.6, R2)]
Q.fights = [(21.1, 26.2, (10.0, 58.0))]
# R1 bites the queen's hind end: aim at the queen itself
R1.fights[2] = (21.0, 26.2, Q)
CAST = [Q, C1, C2, D, G2, R1, R2, R3, G1]
def cast(t, skip=()):
    out = []
    for a in CAST:
        if a in skip: continue
        r = a(t)
        if r["br"] < 0.02: continue          # fully faded into the crack: nothing visible to remove
        r["br"] *= 1.5; out.append(r)
    return out
def d_final(t):
    """断须 after burial: still; one small antenna twitch at 46.5 s."""
    a = D(t); tw = math.exp(-((t - 46.6) / 0.25) ** 2) * 0.9 + 0.3 * math.exp(-((t - 47.3) / 0.2) ** 2)
    a.update(ph=0.3, mand=0.2, aa=2.6 + tw, ab=2.4 + 0.6 * tw, lc=0.25, br=1.5)
    return a

# ================= exterior world =================
NH = (0.0, 0.0); SLITX = (-37.5, 19.0); EXH = (45.0, 62.0)
EROOT = spline([(-95, 1.0, 55), (-60, 4.5, 30), (-36, 3.6, 20.5), (-14, 1.0, 8)], 80)
def ext_clear(x, z):
    return (math.hypot(x - NH[0], z - NH[1]) < 9 or (-32 < x < 32 and -36 < z < -4) or math.hypot(x - SLITX[0], z - SLITX[1]) < 7 or
            (-34 < x < 14 and -75 < z < 14) or math.hypot(x - EXH[0], z - EXH[1]) < 8 or (40 < x < 56 and 60 < z < 95) or (42 < x < 90 and 75 < z < 140))
PEXT = (gen_props(201, (-220, 220), (-180, 260), npeb=1300, nbl=220, pr=(0.25, 2.4), bh=(30, 120), clear=ext_clear) +
        gen_props(202, (-40, 40), (-40, 30), npeb=200, pr=(0.15, 0.7), clear=ext_clear) +
        [tube(EROOT, 4.2, 3.0, (0.30, 0.24, 0.18)), tube(spline([(60, 1, -40), (90, 2.5, -10), (130, 0.8, 30)], 40), 3.0, 2.0),
         tube(spline([(70, 1, 50), (66, 3.4, 80), (80, 1, 120)], 50), 3.6, 2.6, (0.32, 0.25, 0.18))])
def mats_main(gx, gz):
    m = 0.5 + 0.5 * np.sin(gx * 0.021 + 1) * np.sin(gz * 0.017); return [("soil", m * 0.9), ("sand", (1 - m) * 0.9)]
def ext_decal(img, cam):
    for (cx, cz), rx, rz in ((NH, 5.0, 3.4), (SLITX, 2.4, 1.4), (EXH, 3.4, 2.4)):
        ph = np.linspace(0, 2 * np.pi, 40)
        for sc_, a in ((1.4, 0.35), (1.0, 0.95)):
            P, zz = cam.proj(np.stack([cx + np.cos(ph) * rx * sc_, np.full(40, 0.02), cz + np.sin(ph) * rz * sc_], -1))
            if (zz > 0.8).sum() > 30: poly(img, P[zz > 0.8], (0.03, 0.022, 0.016), a)
def ext_render(cam, t, fi, ants, fogd=320, dofk=1.0):
    sky = sky_grad((0.50, 0.56, 0.55), (0.74, 0.72, 0.62))
    return render(cam, t, fi, mats_main, PEXT, ants, sky=sky, fogd=fogd, light=0.95, decal=ext_decal, dofk=dofk)
def elook(img, t): return grade(img, sat=0.80, contrast=1.08, gain=(0.97, 0.96, 0.98), warm=0.008, vign=0.42)
# front battle: fixed pairs + marching columns, all continuous for the whole film
_rb = np.random.default_rng(301)
PAIRS = [(float(_rb.uniform(-28, 28)), float(_rb.uniform(-34, -8)), float(_rb.uniform(0, 6.28))) for _ in range(44)]
MARCH = []
for k in range(36):
    x1, z1 = _rb.uniform(-26, 26), _rb.uniform(-36, -18); x0 = x1 + _rb.uniform(-15, 15); z0 = -170 - _rb.uniform(0, 60); spd = _rb.uniform(5, 8); t0 = -40 + k * 1.4
    arr = t0 + math.hypot(x1 - x0, z1 - z0) / spd
    MARCH.append(Act([(t0, x0, z0), (arr, x1, z1), (arr + 200, x1 + _rb.uniform(-2, 2), z1 + _rb.uniform(-2, 2))], col=BLK, sc=0.95, seed=float(k), hd0=math.pi / 2,
                     fights=[(arr, 200, (x1 + 1, z1 + 2))]))
REDS = []
for k in range(14):
    x1, z1 = _rb.uniform(-20, 20), _rb.uniform(-16, -6); t0 = -30 + k * 4.0
    REDS.append(Act([(t0, 0.5 * _rb.uniform(-3, 3), 0.0), (t0 + 3, x1, z1), (t0 + 300, x1, z1)], col=RED, seed=50.0 + k, hd0=-math.pi / 2,
                    fights=[(t0 + 3, 300, (x1, z1 - 2))], br=(lambda tt, t0=t0: ramp(tt, t0, t0 + 0.8, 0.0, 1.0))))
def battle(t, br=1.0):
    out = []
    for k, (x, z, s) in enumerate(PAIRS): out += grapple(x, z, t, BLK, RED, seed=s, br=br)
    for a in MARCH + REDS:
        r = a(t)
        if r["br"] >= 0.02: r["br"] *= br; out.append(r)
    return out
# raiders outside, slipping into the root crack (fade into darkness as they enter)
R2X = Act([(0, -18.0, -16.0), (5.0, -22.0, -10.0), (8.8, -36.6, 17.6), (9.6, -38.2, 19.6), (30, -38.2, 19.6)], col=BLK, sc=0.95, seed=11.0,
          br=lambda t: ramp(t, 8.6, 9.5, 1.0, 0.0))
R3X = Act([(0, -14.0, -18.0), (5.4, -19.0, -12.0), (9.4, -37.0, 17.0), (10.2, -38.4, 19.4), (30, -38.4, 19.4)], col=BLK, sc=0.95, seed=12.0,
          br=lambda t: ramp(t, 9.2, 10.0, 1.0, 0.0))
# the queen and her escort outside the high exit
QX = Act([(38.0, 45.0, 60.6), (40.0, 45.0, 61.4), (44.8, 46.8, 70.2), (50.0, 48.4, 78.6), (55.0, 49.6, 86.0)], col=QCOL, sc=2.0, gk=1.75, seed=13.0, hd0=1.4,
         br=lambda t: ramp(t, 39.6, 41.4, 0.15, 1.0))
E1 = Act([(38.0, 47.5, 62.6), (40.0, 47.8, 64.4), (44.8, 49.6, 73.0), (50.0, 51.0, 81.0), (55.0, 52.2, 88.4)], col=RED, seed=14.0, carry=True, hd0=1.4,
         br=lambda t: ramp(t, 38.6, 39.8, 0.0, 1.0))
E2 = Act([(38.0, 43.0, 60.4), (40.6, 42.6, 61.8), (44.8, 43.8, 68.6), (50.0, 45.6, 76.8), (55.0, 47.0, 84.2)], col=RED, seed=15.0, hd0=1.4,
         br=lambda t: ramp(t, 40.2, 41.6, 0.0, 1.0))
def escort(t): return [r for r in (QX(t), E1(t), E2(t)) if r["br"] >= 0.02]

# ================= shots =================
def s01(t, fi):      # 0–5 mandibles from the crack, focus pulls to the queen
    u = ease((t - 2.6) / 1.8)
    cam = look_cam((-34.2, 44.9, 1.1), (1.5, -1.0, 42.4), focus=lerp(4.8, 36.0, u), ap=lerp(0.8, 0.12, u))
    return nlook(nest2(cam, t, fi, cast(t)), t)
def s02(t, fi):      # 5–10 front assault outside, then the camera drifts to the root crack
    u = ease((t - 6.6) / 2.6)
    C = lerp3((6.0, -64.0, 16.0), (-27.0, 6.0, 6.0), u); T = lerp3((0.0, 0.0, -18.0), (-37.0, 0.5, 18.4), u)
    cam = look_cam(C, T, ap=0.55)
    return elook(ext_render(cam, t, fi, battle(t) + [r for r in (R2X(t), R3X(t)) if r["br"] >= 0.02]), t)
def s03(t, fi):      # 10–15 raiders in the nursery; pass over the cracked root; back to the raiders
    if t < 12.7:
        cam = look_cam((-17.0, 36.0, 6.5), (-9.5, 0.5, 45.0), ap=0.7)
    elif t < 13.9:
        u = (t - 12.7) / 1.2
        cam = look_cam((lerp(8.0, 8.8, u), 52.0, 6.0), (13.5, 2.0, 57.8), ap=0.4)
    else:
        u = (t - 13.9) / 1.1
        cam = look_cam((-3.0 - 0.6 * u, 49.6, 2.0), (-9.0, 0.8, 45.6), ap=1.0)
    return nlook(nest2(cam, t, fi, cast(t)), t)
def s04(t, fi):      # 15–20 the last guards; carriers start uphill with larvae, queen follows
    u = ease((t - 15) / 5)
    cam = look_cam((lerp(-1.0, 1.0, u), lerp(24.0, 26.0, u), lerp(17.0, 15.0, u)), (1.5, 0.0, lerp(46.0, 49.0, u)), ap=0.55)
    return nlook(nest2(cam, t, fi, cast(t)), t)
def s05(t, fi):      # 20–25 the queen is caught on the uphill entrance
    qp = Q.pos(t)
    cam = look_cam((qp[0] - 9.0, qp[1] - 6.0, 6.0), (qp[0] - 0.6, 0.8, qp[1] - 0.5), ap=0.9)
    return nlook(nest2(cam, t, fi, cast(t)), t)
def s06(t, fi):      # 25–30 断须 hits from the side; queen breaks free uphill; guard dragged down
    u = ease((t - 25) / 5)
    cam = look_cam((lerp(-4.0, -2.0, u), lerp(38.0, 41.0, u), lerp(10.5, 12.0, u)), (lerp(5.0, 7.0, u), 0.5, lerp(51.0, 54.0, u)), ap=0.65)
    return nlook(nest2(cam, t, fi, cast(t)), t)
def s07(t, fi):      # 30–35 queen through the exit; 断须 alone at the fork, backed to the cracked root, looks up
    if t < 32.4:
        cam = look_cam((6.0, 44.0, 16.0), (13.0, 0.0, 66.0), ap=0.5)
    else:
        u = ease((t - 32.4) / 2.6)
        cam = look_cam((lerp(7.0, 8.2, u), lerp(52.0, 52.8, u), 2.4), (12.6, lerp(1.6, 4.8, u), 58.6), ap=0.8)
    return nlook(nest2(cam, t, fi, cast(t)), t)
def s08(t, fi):      # 35–40 bites the root; 37.5 snap and collapse
    sh = 0.0
    if t > TSNAP: sh = 0.35 * math.exp(-(t - TSNAP) * 5) * math.sin((t - TSNAP) * 60)
    cam = look_cam((3.0, 46.0, 9.5 + sh), (11.0, 1.5, 57.6), ap=0.6)
    img = nest2(cam, t, fi, cast(t))
    return nlook(img, t)
def s09(t, fi):      # 40–45 the high exit outside: queen and two escorts, larva carried
    qp = QX.pos(t)
    cam = look_cam((qp[0] + 3.0, qp[1] + 12.0, 4.0), (qp[0], 1.0, qp[1] - 1.0), ap=0.9)
    return elook(ext_render(cam, t, fi, escort(t) + battle(t)), t)
def s10(t, fi):      # 45–50 underground: the damaged antenna in the soil, one twitch, then still
    a0 = D(46.0); hp = np.array([a0["x"] + 0.9 * math.cos(a0["hd"]), 0.5, a0["z"] + 0.9 * math.sin(a0["hd"])])
    cam = look_cam((hp[0] - 2.6, hp[2] - 2.4, 1.9), tuple(hp), focus=3.6, ap=1.0)
    ants = [d_final(t)]
    a = ants[0]; fw = np.array([math.cos(a["hd"]), math.sin(a["hd"])]); sd_ = np.array([-fw[1], fw[0]])
    def cover(im, c):       # soil lying over the body: only the head and the damaged antenna stay visible
        for k, (al, si, r, l) in enumerate(((-1.0, 0.0, 0.7, 0.1), (-0.5, 0.38, 0.5, 0.12), (-0.45, -0.38, 0.5, 0.12), (-1.6, 0.25, 0.6, 0.05))):
            p = np.array([a["x"], a["z"]]) + fw * al + sd_ * si
            pebble(im, c, p[0], p[1], r, np.array([0.21, 0.16, 0.11]) * (0.85 + 0.05 * k), 0.75, k * 1.3, l)
    _, zc_ = cam.proj(np.array([a["x"], 0.5, a["z"]]))
    img = nest2(cam, t, fi, ants, glow_k=0.25, light=0.65, extra=[(float(zc_) - 0.4, cover)])
    img = glow(img, (hp[0] - 0.5 * math.cos(a["hd"]), 0.8, hp[2] - 0.5 * math.sin(a["hd"])), cam, 260, (0.12, 0.08, 0.05), 0.9)
    img = img * lerp(1.0, 0.82, ease((t - 47) / 3))
    return nlook(img, t)
def s11(t, fi):      # 50–55 pull back from the queen: the main force is still out there; cut to black
    u = ease((t - 50) / 4.0); qp = QX.pos(t)
    C = lerp3((qp[0] + 2.0, qp[1] + 10.0, 4.0), (qp[0] + 30.0, qp[1] + 70.0, 46.0), u)
    T = lerp3((qp[0], 1.0, qp[1]), (8.0, 0.0, -10.0), ease((t - 50.5) / 3.5))
    cam = look_cam(C, T, ap=lerp(0.8, 0.2, u))
    img = elook(ext_render(cam, t, fi, escort(t) + battle(t), fogd=lerp(320, 900, u)), t)
    return img * (1 - ease((t - 52.2) / 1.0))
SHOTF = {"S01": s01, "S02": s02, "S03": s03, "S04": s04, "S05": s05, "S06": s06, "S07": s07, "S08": s08, "S09": s09, "S10": s10, "S11": s11}

# ================= text =================
def overlay(img, t):
    for k, s, a, b in LINES:
        if a - 0.01 <= t <= b + 0.01:
            al = fadein(t, a, b, 0.25)
            if k == "C": blit(img, text_sprite(s, 58, font=FONTB, col=(240, 236, 228), box=0.30, pad=(30, 14)), W / 2, 1250, al)
            else: blit(img, text_sprite(s, 44, box=0.40), W / 2, 1400, al)
    return img
def frame(fi):
    t = fi / FPS
    n, a, b = shot_at(t)
    img = SHOTF[n](t, fi)
    img = overlay(img, t)
    img = grain(img, fi, 0.014)
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "test":
        for ts in sys.argv[2:]:
            im = frame(int(round(float(ts) * FPS))); cv2.imwrite(f"/tmp/zs_{ts}.jpg", im[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 88])
    elif cmd == "sheet":
        out = sys.argv[2]; ims = [cv2.resize(frame(int(round(float(ts) * FPS))), (360, 640)) for ts in sys.argv[3:]]
        while len(ims) % 4: ims.append(np.zeros_like(ims[0]))
        rows = [np.hstack(ims[i:i + 4]) for i in range(0, len(ims), 4)]
        cv2.imwrite(out, np.vstack(rows)[..., ::-1])
    elif cmd == "render":
        f0, f1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        import subprocess
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for fi in range(f0, f1): p.stdin.write(frame(fi).tobytes())
        p.stdin.close(); p.wait()
