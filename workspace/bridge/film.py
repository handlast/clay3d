# 《断桥：蚁群最后的防线》 renderer. python3 film.py test t.. | sheet t.. | render f0 f1 out.mp4 | prep
import sys, os, math, numpy as np, cv2
from scene import *
import sim

# ================= helpers =================
def along(pts, s):
    P = np.asarray(pts, float); d = np.linalg.norm(np.diff(P, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(d)])
    s = float(np.clip(s, 0, cum[-1] - 1e-6)); i = int(np.clip(np.searchsorted(cum, s) - 1, 0, len(P) - 2)); u = (s - cum[i]) / max(d[i], 1e-9)
    p = P[i] + (P[i + 1] - P[i]) * u; v = P[i + 1] - P[i]
    return p[0], p[1], math.atan2(v[1], v[0])
def plen(pts): P = np.asarray(pts, float); return float(np.linalg.norm(np.diff(P, axis=0), axis=1).sum())
def trav(pts, t, t0, spd, col=RED, wob=0.25, seed=0, **kw):
    """ant walking polyline pts from time t0 at speed spd (mm/s); stays at the end"""
    s = max(0.0, (t - t0) * spd); x, z, hd = along(pts, s)
    moving = s < plen(pts)
    hd += 0.06 * math.sin(t * 2.3 + seed)
    nx, nz = -math.sin(hd), math.cos(hd); o = wob * math.sin(t * 1.7 + seed * 1.3)
    kw.setdefault("ph", (s / 0.55) % 1 if moving else 0.3)
    kw.setdefault("aa", t * (4 if moving else 2.2) + seed); kw.setdefault("ab", t * (4.4 if moving else 2.5) + seed * 2)
    return A(x + nx * o, z + nz * o, hd, col=col, **kw)
def grapple(cx, cz, t, t0, ca=BLK, cb=RED, seed=0, r=1.45, lift=0.0, hero_b=False, sc=(1.0, 1.0), spin=0.35):
    u = max(0.0, t - t0); w = spin * u + 0.4 * math.sin(0.8 * u + seed) + seed
    c = np.array([cx + 0.25 * math.sin(u * 0.9 + seed), cz + 0.25 * math.sin(u * 0.6 + seed * 2)])
    ra = np.array([math.cos(w), math.sin(w)]) * r; pa = c + ra; pb = c - ra * 0.98
    ha = math.atan2(-ra[1], -ra[0]) + 0.22 * math.sin(u * 6 + seed); hb = ha + math.pi + 0.2 * math.sin(u * 5 + seed)
    jit = lambda k: 0.06 * math.sin(u * (23 + k) + seed * k)
    return [A(pa[0] + jit(1), pa[1] + jit(2), ha, ph=(0.2 + 0.15 * math.sin(u * 15 + seed)) % 1, aa=u * 9 + seed, ab=u * 8, mand=0.5 + 0.5 * math.sin(u * 11 + seed), col=ca, lift=lift, sc=sc[0]),
            A(pb[0] + jit(3), pb[1] + jit(4), hb, ph=(0.6 + 0.15 * math.sin(u * 17 + seed)) % 1, aa=u * 9, ab=u * 10 + seed, mand=0.5 + 0.5 * math.sin(u * 12 + seed * 2), col=cb, lift=lift, hero=hero_b, sc=sc[1])]
def glow(img, p, cam, rad, col, a=1.0):
    s_, z_ = cam.proj(np.asarray(p, float))
    if z_ < 1: return img
    yy, xx = np.mgrid[0:H:4, 0:W:4]; g = np.exp(-(((xx - s_[0]) / rad) ** 2 + ((yy - s_[1]) / (rad * 0.8)) ** 2)).astype(np.float32)
    return img + cv2.resize(g, (W, H))[..., None] * np.array(col, np.float32) * a
def shake(t, t0, amp_px, f=1500.0, dur=0.45):
    u = t - t0
    if u < 0 or u > dur: return 0.0
    return amp_px / f * (1 - u / dur) * math.sin(u * 70)

# ================= simulations (cached) =================
def fold(u, v, k=0.9):
    s = (v - LX0) / (LX1 - LX0)
    if 0 <= s <= 1:
        w = float(leaf_w(s)) * k; return w * math.tanh(u / max(w, 0.2))
    if LX1 < v < PET1 + 1.0: return 0.55 * math.tanh(u / 0.55)
    return u
_S = {}
def S(name):
    if name in _S: return _S[name]
    c = os.path.join(HERE, f"sim_{name}.npz")
    if name == "W":
        rng = np.random.default_rng(1); paths = []
        for i, z0 in enumerate(np.linspace(-140, 140, 14)):
            paths.append(sim.curve((-285 + rng.uniform(-20, 20), z0), (-21, rng.uniform(-2.5, 2.5)), 25, 10 + i))
        for i in range(6):
            paths.append(sim.curve((-20, rng.uniform(-2, 2)), (-72 + rng.uniform(-8, 8), rng.uniform(-35, 35)), 8, 40 + i))
        cfg = dict(seed=2, t0=0.0, t1=60.0, warm=0, paths=paths, path_colony=[0] * 14 + [1] * 6, path_weights=[1] * 14 + [0.33] * 6, n=330,
                   speed=(6, 9), lat=0.8, s0=lambda rng, pid, L, col: np.where(pid < 14, rng.uniform(-0.45, 0.12, len(pid)) * L, rng.uniform(0.2, 1.0, len(pid)) * L), p_fight=0.85, fight_after=30.0, fight_dur=(4, 11), p_join=0.1, join_r=3.0, max_cluster=6)
    elif name == "BR":
        rng = np.random.default_rng(3); paths = []
        for i, u0 in enumerate(np.linspace(-70, 70, 16)):
            a = sim.curve((u0, -175), (rng.uniform(-2.2, 2.2), -21), 22, 60 + i); b = np.linspace(a[-1], (a[-1][0] * 0.8, 4.0), 25)
            paths.append(np.vstack([a, b[1:]]))
        for i in range(6):
            uu = rng.uniform(-1.5, 1.5); paths.append(np.linspace((uu * 0.3, 28.0), (uu, 4.0), 30))
        cfg = dict(seed=4, t0=60.0, t1=TBREAK + 80.0, warm=25, paths=paths, path_colony=[0] * 16 + [1] * 6, path_weights=[1] * 16 + [0.42] * 6, n=430,
                   speed=(5, 8), lat=0.5, spawn_spread=0.6, fill=0.9, border=dict(zb=lambda x: 4.0, off=1.0, xr=(-2.0, 2.0)), p_fight=0.7, fight_after=-1e9,
                   fight_dur=(4, 12), p_join=0.1, join_r=2.4, max_cluster=5, contact_r=1.25)
    elif name == "E":
        rng = np.random.default_rng(5); paths = []
        for i in range(5):
            u1 = rng.uniform(-1, 1); a = np.linspace((u1, -30.0), (u1 * 0.3, PET1 + 0.5), 40)
            b = sim.curve(a[-1], (rng.uniform(-6, 26), 33.0), 6, 80 + i); paths.append(np.vstack([a, b[1:]]))
        for i in range(4):
            uu = rng.uniform(-2, 26); paths.append(sim.curve((uu, 600.0), (uu, 34.0), 30, 90 + i))
        for i in range(3):
            uu = rng.uniform(2, 22); paths.append(sim.curve((uu + 3, 50.0), (uu, 34.0), 4, 95 + i))
        def s0(rng, pid, L, col):
            s = np.zeros(len(pid))
            for k, p in enumerate(pid):
                if p < 5: s[k] = -rng.uniform(15, 260)
                elif p < 9: s[k] = L[k] - rng.uniform(520, 640)
                else: s[k] = rng.uniform(0, L[k])
            return s
        cfg = dict(seed=6, t0=110.0, t1=215.0, warm=0, paths=paths, path_colony=[0] * 5 + [1] * 4 + [1] * 3, path_weights=[10] * 5 + [11] * 4 + [4] * 3, n=106,
                   speed=(5.5, 8), lat=0.5, s0=s0, border=dict(zb=lambda x: 34.0, off=1.0, xr=(-5.0, 25.0)), p_fight=0.85, fight_after=112.0, fight_dur=(3, 9), p_join=0.12,
                   join_r=3.0, max_cluster=5)
    _S[name] = sim.run(cfg, c); return _S[name]
def sidx(name, t, t0): sd = S(name); return sd, int(np.clip(round((t - t0) * FPS), 0, sd["x"].shape[0] - 1))
def crowd(name, t, t0, swap=False, keep=None, lift=True, tt=None):
    sd, fi = sidx(name, t if tt is None else tt, t0); o = []
    for i in np.nonzero(sd["vis"][fi] > 0)[0]:
        sx, sz, sh = float(sd["x"][fi, i]), float(sd["z"][fi, i]), float(sd["hd"][fi, i])
        if swap: x, z, hd = sz, fold(sx, sz), math.pi / 2 - sh
        else: x, z, hd = sx, sz, sh
        col = BLK if sd["col"][i] < 0.5 else RED
        if keep and not keep(x, z, col is BLK, i): continue
        o.append(A(x, z, hd, ph=float(sd["ph"][fi, i]), aa=float(sd["aa"][fi, i]), ab=float(sd["ab"][fi, i]), mand=float(sd["mand"][fi, i]),
                   st=int(sd["st"][fi, i]), col=col, lift=surf_h(x, z, t) if lift else 0.0))
    return o
def bridge_crowd(t, keep=None, slow_t=None):
    """bridge battle with the break handled: leaf riders follow the leaf, west bank piles at the edge, east of crack continues"""
    tt = t if slow_t is None else slow_t
    if tt < TBREAK:
        k2 = (lambda x, z, b, i: (keep is None or keep(x, z, b, i)) and not (not b and tt > 112 and i % 3 == 0) and not (tt > 69.5 and CRACK - 1.6 < x < CRACK + 3.2) and not (b and x > 9.5))
        return crowd("BR", t, 60.0, swap=True, keep=k2, tt=tt)
    out = []
    frozen = crowd("BR", TBREAK, 60.0, swap=True, keep=lambda x, z, b, i: LX0 - 0.6 < x < CRACK and not (not b and i % 3 == 0))
    u = t - TBREAK; rr = np.random.default_rng(3)
    for k, a in enumerate(frozen):
        if k % 3 == 0 and u > 0.45 + 0.3 * rr.random(): continue      # thrown into the water
        P = leaf_xf(np.array([a["x"], a["lift"], a["z"]]), t); a["x"], a["lift"], a["z"] = P[0], max(P[1], 0.05), P[2]
        a["hd"] += 0.035 * max(0, u - 0.7)
        if a["st"] != 3:
            a["lc"] = 0.45 + 0.35 * math.sin(t * 9 + k); a["roll"] = 0.25 * math.sin(t * 5 + k) * (u < 3) ; a["ph"] = (t * 3 + k * 0.37) % 1
            a["aa"] = t * 8 + k; a["ab"] = t * 9 + k
            if u > 6: a["lc"] *= 0.4
        if keep is None or keep(a["x"], a["z"], a["col"] is BLK, k): out.append(a)
    live = crowd("BR", t, 60.0, swap=True, keep=lambda x, z, b, i: (b and x < CRACK) or (x > CRACK + 0.6 and not (not b and i % 3 == 0)))
    for j, a in enumerate(live):
        if a["x"] < CRACK:
            a["x"] = min(a["x"], -13.4 - (j % 9) * 0.85 - 0.4 * math.sin(j)); a["lift"] = 0.0
            if a["x"] > -24: a["z"] = a["z"] * 1.0 + ((j * 7919) % 23 - 11) * 0.9
        if keep is None or keep(a["x"], a["z"], a["col"] is BLK, 0): out.append(a)
    return out
def east_crowd(t, keep=None):
    def k(x, z, b, i):
        if t > TBREAK and x < CRACK + 0.3: return False
        return keep is None or keep(x, z, b, i)
    return crowd("E", t, 110.0, swap=True, keep=k) if t >= 110 else []

# ================= worlds =================
def mats_main(gx, gz):
    m = 0.5 + 0.5 * np.sin(gx * 0.021 + 1) * np.sin(gz * 0.017); md = np.clip(1 - (np.abs(gx) - 12) / 16, 0, 1)
    return [("soil", (1 - md) * m), ("sand", (1 - md) * (1 - m)), ("mud", md)]
ROOT_E = spline([(26, 0.6, -90), (33, 5.5, -30), (40, 8.8, 15), (55, 6.5, 60), (85, 0.8, 120)], 90)
ROOT_W = spline([(-130, 0.8, 70), (-85, 4.2, 52), (-55, 3.6, 44), (-32, 0.8, 28)], 70)
NESTH = (37.5, 6.0); SLIT = (-52.0, 39.5)
def clear_main(x, z):
    return abs(x) < 17.5 or (20 < x < 60 and -12 < z < 26) or (-62 < x < -40 and 32 < z < 46)
PMAIN = (gen_props(11, (-320, -16), (-220, 420), npeb=1500, nbl=200, pr=(0.25, 2.4), bh=(30, 120), clear=clear_main) +
         gen_props(12, (16, 320), (-220, 420), npeb=1000, nbl=150, pr=(0.25, 2.4), bh=(30, 120), clear=clear_main) +
         gen_props(13, (-60, 60), (-30, 30), npeb=260, pr=(0.15, 0.8), clear=lambda x, z: abs(x) < 15 or (CRACK - 2 < x < 45 and -4 < z < 14)) +
         [tube(ROOT_E, 6.5, 4.8), tube(ROOT_W, 4.6, 3.2, (0.29, 0.23, 0.17)),
          tube(spline([(60, 1, -40), (90, 2.5, -10), (130, 0.8, 30)], 40), 3.0, 2.0), tube(spline([(-150, 1, 140), (-100, 2.2, 160), (-60, 0.7, 200)], 40), 3.5, 2.4)])
def main_decal(t):
    def f(img, cam):
        for (cx, cz), rx, rz, k in ((NESTH, 5.2, 3.4, 1.0), (SLIT, 3.6, 1.1, 0.9)):
            ph = np.linspace(0, 2 * np.pi, 40)
            for sc_, a in ((1.35, 0.35), (1.0, 0.9 * k)):
                P, zz = cam.proj(np.stack([cx + np.cos(ph) * rx * sc_, np.full(40, 0.02), cz + np.sin(ph) * rz * sc_], -1))
                if (zz > 0.8).all(): poly(img, P, (0.03, 0.022, 0.016), a)
    return f
def main_render(cam, t, fi, ants, fogd=300, sky=None, light=1.0, extra=None, dofk=1.0, leaf=True):
    R = RAIN(t)
    sky = sky if sky is not None else sky_grad(lerp(np.array([0.50, 0.57, 0.55]), np.array([0.40, 0.44, 0.46]), R), lerp(np.array([0.74, 0.72, 0.62]), np.array([0.55, 0.56, 0.54]), R))
    wfn = ditch_water(t, fi, cam)
    return render(cam, t, fi, mats_main, PMAIN, ants, sky=sky, fogd=fogd * (1 - 0.35 * R), light=light * (1 - 0.22 * R), water=wfn, decal=main_decal(t),
                  leaf=leaf, petiole=True, wet=R, rings=R, extra=extra, dofk=dofk)
def look(img, t, k=1.0, cool=0.0):
    R = RAIN(t)
    img = rain_streaks(img, t, int(t * 30), k)
    return grade(img, sat=0.82 * (1 - 0.25 * R), contrast=1.08, gain=(0.98 - 0.08 * R - 0.04 * cool, 0.98 - 0.05 * R, 1.0), warm=0.012 * (1 - R), vign=0.42)

# nest chamber world
PNEST = (gen_props(21, (-60, 60), (0, 110), npeb=650, pr=(0.12, 0.6), dark=0.42, clear=lambda x, z: (abs(x) < 10 and 34 < z < 51) or (-30 < x < -18 and 44 < z < 56)) +
         gen_props(22, (-7, 7), (37, 47), larvae=40, lr=(0.42, 0.6)) +
         [tube(spline([(-80, 4, 92), (-20, 9, 88), (40, 7, 95), (90, 3, 85)], 70), 9, 7, (0.25, 0.19, 0.14)),
          tube(spline([(-48, 2, 10), (-44, 5, 50), (-50, 3, 100)], 50), 6, 5, (0.26, 0.20, 0.15)),
          tube(spline([(48, 2, 15), (45, 6, 55), (52, 3, 100)], 50), 6, 5, (0.26, 0.20, 0.15))])
EXIT_A = (18.0, 4.0, 74.0); EXIT_B = (-14.0, 4.0, 77.0)
def mats_nest(gx, gz):
    v = 0.5 + 0.5 * np.sin(gx * 0.08) * np.sin(gz * 0.06 + 1); return [("soil", v * 0.85), ("mud", (1 - v) * 0.85)]
def nest_render(cam, t, fi, ants, flood=0.0, glow_k=1.0, props=None, extra=None, decal=None):
    sky = sky_grad((0.035, 0.026, 0.02), (0.10, 0.07, 0.05))
    def water(img, GX, GZ, dep):
        if flood <= 0: return img
        lvl = flood * (0.6 + 0.4 * np.sin(GX * 0.05) * np.sin(GZ * 0.07 + 2))
        wm = np.clip((lvl - 0.25) / 0.2, 0, 1)[..., None]
        rip = 0.5 + 0.5 * np.sin(GZ * 0.7 + GX * 0.3 - t * 2)
        wc = np.array([0.07, 0.068, 0.06], np.float32) + 0.05 * rip[..., None] ** 4 + np.clip(1 - np.exp(-dep / 50.0), 0, 1)[..., None] * np.array([0.16, 0.13, 0.09], np.float32)
        return img * (1 - 0.85 * wm) + wc * 0.85 * wm
    img = render(cam, t, fi, mats_nest, PNEST if props is None else props, ants, sky=sky, fogd=75, light=0.62, water=water, objlight=0.85, extra=extra, decal=decal, fogc=0.07)
    img = glow(img, EXIT_A, cam, 300, (0.32, 0.24, 0.15), 0.9 * glow_k); img = glow(img, EXIT_B, cam, 220, (0.20, 0.16, 0.11), 0.7 * glow_k)
    return img
def nlook(img, t):
    img = grade(img, sat=0.78, contrast=1.1, gain=(1.0, 0.92, 0.82), vign=0.55, lift=(0.012, 0.01, 0.01))
    return img

# tunnel world (crack under the roots): runs along +z, x≈0
def _tun_props():
    rng = np.random.default_rng(31); P = gen_props(32, (-7, 7), (-10, 150), npeb=300, pr=(0.08, 0.45), clear=lambda x, z: abs(x) < 2.6, dark=0.42)
    for side in (-1, 1):
        for k in range(3):
            xs = side * (4.6 + 1.6 * k + rng.uniform(-0.5, 0.5)); ys = 1.2 + 2.6 * k
            pts = np.stack([xs + 0.8 * np.sin(np.linspace(0, 9, 90) + k), ys + 0.6 * np.sin(np.linspace(0, 5, 90) + side), np.linspace(-20, 160, 90)], -1)
            P.append(tube(pts, 2.4 + 0.6 * k, 2.0 + 0.5 * k, np.array([0.24, 0.18, 0.13]) * rng.uniform(0.8, 1.1)))
    return P
PTUN = _tun_props()
def tun_render(cam, t, fi, ants, glow_z=135.0, glow_k=1.0):
    sky = sky_grad((0.02, 0.016, 0.012), (0.06, 0.045, 0.032))
    img = render(cam, t, fi, mats_nest, PTUN, ants, sky=sky, fogd=38, light=0.55, objlight=0.8, fogc=0.04)
    return glow(img, (0, 3, glow_z), cam, 360, (0.30, 0.22, 0.13), glow_k)

# root-top world (exit and the survivors)
RTOP = spline([(0, 12, -40), (2, 14, 80), (-4, 15, 220), (6, 13, 420)], 120)
PROOT = [tube(RTOP, 12, 11, (0.46, 0.37, 0.27))] + gen_props(41, (-300, 300), (-60, 600), npeb=900, nbl=260, pr=(0.4, 3.0), bh=(40, 160), clear=lambda x, z: abs(x) < 45)
def rtop(z):
    i = np.clip(np.searchsorted(RTOP[:, 2], z), 1, len(RTOP) - 1); p = RTOP[i]; return float(p[0]), float(p[1] + 12 * (1 - 0.08 * (i / len(RTOP))))
def root_render(cam, t, fi, ants, extra=None):
    R = RAIN(t)
    sky = sky_grad((0.38, 0.42, 0.44), (0.56, 0.57, 0.54))
    img = render(cam, t, fi, mats_main, PROOT, ants, sky=sky, fogd=260, light=0.8, objlight=0.9, wet=R, extra=extra, dofk=0)
    img = img * 0.25 + cv2.GaussianBlur(img, (0, 0), 1.2) * 0.75 if False else img
    return img

# ================= hero & handmade groups =================
def hero_main(t):
    """断须 on the surface (main world) for the whole film"""
    if t < 10: return trav([(-21.5, -0.8), (-24.5, -1.2)], t, 0.6, 1.4, hero=True, aa=2.6 + 0.35 * math.sin(t * 1.3) if t > 6 else t * 4, ab=2.4 + 0.3 * math.sin(t * 1.1) if t > 6 else t * 4.4)
    if t < 30:
        pts = [(36, 9), (30, 6), (22, 2.5), (17.5, 0.2), (14.7, 0.15)]
        a = trav(pts, t, 20.0, 3.4, hero=True)
        if t > 27.0: a.update(aa=2.4 + 0.5 * math.sin(t * 7), ab=2.2 + 0.5 * math.sin(t * 6.3), hd=math.pi + 0.05 * math.sin(t))
        a["lift"] = surf_h(a["x"], a["z"], t); return a
    return None
def chewers(t, ts=None, pause=None):
    """hero + two helpers working the crack, facing west across it; ts = (slowed) animation time"""
    s = t if ts is None else ts; out = []
    for k, (dx, dz, hd0) in enumerate(((0.95, 0.1, math.pi), (1.6, -0.75, math.pi - 0.6), (1.6, 0.85, math.pi + 0.55))):
        pull = 0.12 * math.sin(s * (7.5 + k)) + 0.08 * math.sin(s * 3.1 + k)
        x = CRACK + dx + pull; z = dz
        hd = hd0 + 0.06 * math.sin(s * 5 + k)
        if k == 0 and pause is not None and pause[0] <= t <= pause[1]:
            u = (t - pause[0]) / (pause[1] - pause[0]); hd = hd0 + 1.45 * math.sin(math.pi * u) ** 0.6; pull = 0
        a = A(x, z, hd, ph=(0.25 + 0.1 * math.sin(s * 9 + k)) % 1, aa=2.3 + 0.4 * math.sin(s * 6 + k), ab=2.5 + 0.4 * math.sin(s * 5.4 + k),
              mand=0.5 + 0.5 * math.sin(s * 13 + k), col=RED, hero=(k == 0), pitch=-0.12)
        a["lift"] = surf_h(x, z, t); out.append(a)
    return out
def raiders_tunnel(t):
    """five light raiders in the root crack (tunnel world): lead z(t), followers behind"""
    zl = 7.0 * (min(t, 94.5) - 87.6) + 7.0 * max(0.0, t - 96.3)
    out = []
    for k, (lag, dx) in enumerate(((0, 0.0), (3.2, 0.9), (5.8, -0.8), (8.5, 0.4), (11.0, -0.3))):
        z = zl - lag; x = dx + 0.5 * math.sin(z * 0.35 + k)
        hd = math.pi / 2 + 0.25 * math.cos(z * 0.35 + k)
        if k == 0 and 94.5 <= t <= 96.3: continue
        out.append(A(x, z, hd, ph=(z / 0.5) % 1, aa=t * 4.6 + k, ab=t * 4.2 + k, col=BLK, sc=0.82))
    return out

# ================= shots =================
def s01(t, fi):
    cam = Cam(kf(t, [(0, -8.5), (10, -15.5)]), kf(t, [(0, -7.5), (10, -5.0)]), kf(t, [(0, 2.9), (10, 2.4)]), 6.5, -78 + 2 * math.sin(t * 0.2),
              focus=kf(t, [(0, 15), (5.5, 15), (7.8, 70), (10, 60)], "exp"), aperture=1.0)
    ants = crowd("W", t, 0.0) + [hero_main(t)]
    img = main_render(cam, t, fi, ants, fogd=kf(t, [(0, 150), (10, 220)]))
    return look(img, t)
def s02(t, fi):
    cam = Cam(kf(t, [(10, -2), (20, 3)]), kf(t, [(10, 12), (20, 18)]), 3.6, 10, 4, focus=kf(t, [(10, 30), (14, 30), (16.5, 16), (20, 18)]), aperture=1.0)
    ants = []
    rng = np.random.default_rng(2)
    moving = ease((t - 17.6) / 1.2)
    for k in range(13):     # nurses tending the brood
        a0 = rng.uniform(0, 6.28); r0 = rng.uniform(5, 10); cx, cz = 0 + math.cos(a0) * r0, 42 + math.sin(a0) * r0 * 0.8
        hd = math.atan2(42 - cz, -cx) + 0.4 * math.sin(t * 0.7 + k)
        if moving > 0:
            cx += moving * (t - 17.6) * 2.5 * math.cos(0.4); cz += moving * (t - 17.6) * 2.5 * math.sin(0.4); hd = 0.4 + 0.2 * math.sin(k)
        ants.append(A(cx, cz, hd, ph=(t * 0.8 + k * 0.3) % 1 if moving == 0 else (t * 2.4 + k * 0.3) % 1, aa=t * 2.5 + k, ab=t * 2.8 + k,
                      mand=0.2 + 0.2 * math.sin(t * 3 + k), col=RED, carry=(k % 3 == 0 and moving > 0)))
    q = trav([(-14, 47), (-4, 48.5), (6, 49), (14, 55)], t, 10.6, 1.5, col=RED, sc=1.75, gk=1.6, seed=3)
    q["br"] = 1.08; ants.append(q)
    for k, dz in enumerate((-2.6, 2.6)):    # her escorts
        e = trav([(-14 + 1.5, 47 + dz), (-4 + 1.5, 48.5 + dz), (6 + 1.5, 49 + dz), (14 + 1.5, 55 + dz)], t, 10.6, 1.5, col=RED, seed=5 + k); ants.append(e)
    g = A(9.5, 33.5, -2.4, aa=2.5 + 0.4 * math.sin(t * 2), ab=2.6, col=RED)
    if t > 16.4: g.update(aa=2.4 + 0.5 * math.sin(t * 11), ab=2.6 + 0.5 * math.sin(t * 10))
    ants.append(g)
    hx = trav([(24, 27), (17, 30), (11.4, 32.6)], t, 14.4, 5.2, hero=True)
    if t > 16.2: hx.update(aa=2.4 + 0.5 * math.sin(t * 12), ab=2.3 + 0.4 * math.sin(t * 11), ph=0.3)
    if t > 17.8: hx = trav([(11.4, 32.6), (14, 30), (24, 26)], t, 17.8, 5.2, hero=True)
    if t > 14.4: ants.append(hx)
    img = nest_render(cam, t, fi, ants)
    return nlook(img, t)
def s03(t, fi):
    u = ease((t - 20) / 7.2)
    cam = Cam(lerp(0, 8.6, u), lerp(-120, -7.2, u), 170 * (4.6 / 170) ** u, lerp(64, 22, u), lerp(0, 30, u),
              focus=lerp(190, 9.0, u), aperture=lerp(0.35, 1.0, u))
    ants = crowd("W", t, 0.0) + ([hero_main(t)] if t > 20 else [])
    img = main_render(cam, t, fi, ants, fogd=lerp(2600, 260, u))
    if t > 27.2:   # fibre creak highlight
        pass
    return look(img, t)
def s04(t, fi):
    cam = Cam(kf(t, [(30, -82), (40, -58)], "lin"), -34, 4.2, 8, 4, focus=34, aperture=0.95)
    img = main_render(cam, t, fi, crowd("W", t, 0.0), fogd=260)
    return look(img, t)
PAIR5 = 41.6; BITE5 = 42.7
def s05(t, fi):
    sh = shake(t, BITE5, 4)
    cam = Cam(-50.0 + 0.3 * math.sin(t * 0.4) + sh, -10.0, 2.2, 6, 0, focus=10, aperture=1.0)
    xb = kf(t, [(40, -60.0), (PAIR5, -51.7)], "lin"); xr = kf(t, [(40, -40.0), (PAIR5, -48.3)], "lin")
    if t < BITE5:
        tw = t > PAIR5
        pair = [A(xb, 0.0, 0.0, ph=(xb / 0.55) % 1 if not tw else 0.2, aa=t * 4 if not tw else 2.6 + 0.35 * math.sin(t * 13), ab=t * 4.4 if not tw else 2.6 + 0.3 * math.sin(t * 11), col=BLK),
                A(xr, 0.0, math.pi, ph=(-xr / 0.55) % 1 if not tw else 0.6, aa=t * 4 if not tw else 2.6 + 0.35 * math.sin(t * 12), ab=t * 3.9 if not tw else 2.6 + 0.3 * math.sin(t * 14), col=RED)]
    else: pair = grapple(-50.0, 0.0, t, BITE5, BLK, RED, seed=0.3)
    bg = crowd("W", t, 0.0, keep=lambda x, z, b, i: not (abs(x + 50) < 4.5 and abs(z) < 3.5))
    extra2 = grapple(-56.0, 9.0, t, 44.2, seed=1.2) if t > 44.2 else []
    extra3 = grapple(-44.5, 14.0, t, 45.6, seed=2.1) if t > 45.6 else []
    img = main_render(cam, t, fi, bg + pair + extra2 + extra3, fogd=200)
    return look(img, t)
RETREAT = [((-40 - 3.0 * (i % 4) - 1.5 * i, -3 + (i % 5) * 1.5), i * 0.5) for i in range(9)]
def retreat_group(t):
    out = []
    for k, ((x0, z0), dl) in enumerate([((-40.0, -0.4), 0.0)] + RETREAT):
        pts = [(x0, z0), (-22, z0 * 0.4), (-12, 0.3 * z0 * 0.4), (4, 0.2 * z0), (14, 0.1 * z0), (20, 0.5 + z0 * 0.4)]
        a = trav(pts, t, 50.0 + dl * 0.6, 5.6, hero=(k == 0), seed=k); a["lift"] = surf_h(a["x"], a["z"], t); out.append(a)
    return out
def rearguard(t, t0=52.0):
    out = []
    for k, (cx, cz) in enumerate(((-19.5, -1.2), (-20.5, 1.6))):
        out += grapple(cx, cz, t, t0 + k * 0.7, seed=k * 1.7, r=1.35)
    for a in out: a["lift"] = surf_h(a["x"], a["z"], t)
    return out
def s06(t, fi):
    h = hero_x = retreat_group(t)[0]["x"]
    turn = ease((t - 57.2) / 2.2)
    cam = Cam(hero_x - 3.0 + 4 * turn, kf(t, [(50, -9), (60, -8)]), 4.0 + 1.5 * turn, 14, lerp(25, -95, turn), focus=lerp(9.5, 22, turn), aperture=1.0)
    ants = crowd("W", t, 0.0, keep=lambda x, z, b, i: b) + retreat_group(t) + rearguard(t)
    img = main_render(cam, t, fi, ants, fogd=240)
    return look(img, t)
def s07(t, fi):
    up = ease((t - 65.5) / 4.5)
    cam = Cam(lerp(24, 26, up), lerp(-20, -34, up), 5.5 * (34 / 5.5) ** up, lerp(15, 42, up), lerp(-48, -40, up), focus=lerp(24, 46, up), aperture=lerp(1.0, 0.6, up))
    img = main_render(cam, t, fi, bridge_crowd(t), fogd=lerp(260, 600, up))
    return look(img, t)
def crack_cam(t, x=15.6, z=-6.4, h=3.1, pitch=15, yaw=-12, foc=6.6):
    return Cam(x + 0.15 * math.sin(t * 0.35), z, h, pitch, yaw, focus=foc, aperture=1.0)
def s08(t, fi):
    cam = crack_cam(t)
    arrive = []
    if t < 72.4:   # hero and two helpers leave the fight and come to the crack
        for k, (tx, tz) in enumerate(((CRACK + 0.95, 0.1), (CRACK + 1.6, -0.75), (CRACK + 1.6, 0.85))):
            a = trav([(5.5, (k - 1) * 0.8), (CRACK - 0.8, (k - 1) * 0.4), (CRACK + 3.0, tz), (tx, tz)], t, 70.0 + k * 0.3, 4.5, hero=(k == 0), seed=k)
            a["lift"] = surf_h(a["x"], a["z"], t); arrive.append(a)
        work = arrive
    else: work = chewers(t)
    img = main_render(cam, t, fi, bridge_crowd(t) + work, fogd=200)
    return look(img, t)
def s09(t, fi):
    if t < 87.6:
        u = ease((t - 84.5) / 3.0)
        cam = Cam(lerp(-70, -58, u), lerp(20, 30, u), lerp(3.6, 2.4, u), 10, lerp(8, 30, u), focus=lerp(19, 10, u), aperture=1.0)
        ants = []
        for k in range(5):
            pts = [(-96 + k * 1.5, 30 - k * 0.8), (-74, 34 + 0.5 * k), (-60, 37.5), (SLIT[0] + 1, SLIT[1] - 0.2)]
            a = trav(pts, t, 80.0 + k * 0.9, 6.5, col=BLK, sc=0.82, seed=k)
            d = math.hypot(a["x"] - SLIT[0], a["z"] - SLIT[1])
            if d < 2.2 and t > 83: a["br"] = max(0.0, d / 2.2)
            if a["br"] > 0.05: ants.append(a)
        img = main_render(cam, t, fi, ants + crowd("W", 59.9, 0.0, keep=lambda x, z, b, i: x < -60), fogd=180)
        img = look(img, t)
        if t > 86.6: img *= 1 - 0.85 * ease((t - 86.6) / 1.0)
        return img
    cam = Cam(0.3, 7.0 * (t - 87.6) - 8.0, 2.0, 5, 0, focus=8, aperture=1.0)
    img = tun_render(cam, t, fi, raiders_tunnel(t), glow_k=0.25)
    img = nlook(img, t)
    if t < 88.6: img *= 0.15 + 0.85 * ease((t - 87.6) / 1.0)
    return img
GUARD_Z = 48.5
def s10(t, fi):
    zl = 7.0 * (min(t, 94.5) - 87.6) + 7.0 * max(0.0, t - 96.3)
    cam = Cam(-0.6 + 0.4 * math.sin(t * 0.5), zl - 8.5, 2.1, 5, 4, focus=8.5, aperture=1.0)
    ants = raiders_tunnel(t)
    if t < 94.5: ants.append(trav([(0.3, GUARD_Z + 14), (0.0, GUARD_Z + 1.4)], t, 91.5, 4.5, col=RED, seed=4))
    elif t < 96.3: ants += grapple(0.0, GUARD_Z, t, 94.5, BLK, RED, seed=0.7, sc=(0.82, 1.0))
    else: ants.append(A(1.6, GUARD_Z + 0.4, 2.0, st=3, col=RED, mand=0.3))
    img = tun_render(cam, t, fi, ants, glow_z=118, glow_k=lerp(0.4, 1.0, (t - 90) / 10))
    return nlook(img, t)
def queen_group(t, path, t0, spd, stop=None):
    q = trav(path, t, t0, spd, col=RED, sc=1.75, gk=1.6, seed=3); q["br"] = 1.08
    if stop and stop[0] < t < stop[1]: q = trav(path, stop[0], t0, spd, col=RED, sc=1.75, gk=1.6, seed=3); q.update(ph=0.3, aa=2.5 + 0.5 * math.sin(t * 6), ab=2.4 + 0.5 * math.sin(t * 5.5), br=1.08)
    out = [q]
    for k, (dx, dz) in enumerate(((-2.2, -2.4), (2.4, -1.4), (0.5, 3.2))):
        pp = [(p[0] + dx, p[1] + dz) for p in path]
        e = trav(pp, t if not (stop and stop[0] < t < stop[1]) else stop[0], t0 - 0.2 * k, spd, col=RED, seed=7 + k)
        if stop and stop[0] < t < stop[1]: e.update(aa=t * 6 + k, ab=t * 6.3 + k, hd=e["hd"] + 0.6 * math.sin(t * 2 + k))
        out.append(e)
    return out
def s11(t, fi):
    cam = Cam(kf(t, [(100, -17), (110, -5)]), kf(t, [(100, 28), (110, 34)]), 3.4, 10, kf(t, [(100, -6), (110, 22)]), focus=kf(t, [(100, 13), (110, 16)]), aperture=1.0)
    ants = []
    for k in range(5):
        pts = [(-40, 38 + k * 1.5), (-26, 40 + k), (-14 + k, 41 + k * 0.5)]
        ants.append(trav(pts, t, 100.2 + k * 0.5, 6.0, col=BLK, sc=0.82, seed=k))
    gtimes = [101.8, 102.6, 103.5]
    for k, tg in enumerate(gtimes):
        if t > tg: ants = [a for a in ants if not (abs(a["x"] - (-22 + 2.5 * k)) < 3 and abs(a["z"] - (40 + 1.5 * k)) < 3 and a["col"] is BLK)]
        if t > tg: ants += grapple(-22 + 2.5 * k, 40 + 1.5 * k, t, tg, BLK, RED, seed=k * 2.1, sc=(0.82, 1.0))
        else: ants.append(trav([(-4 + k * 2, 44 + k), (-20 + 2.5 * k, 41.5 + 1.5 * k)], t, 100.6 + k * 0.4, 7.0, seed=k + 10))
    for k in range(6):    # carriers taking brood toward the exit
        pts = [(-4 + k * 1.4, 38 + (k % 3) * 2.5), (6 + k, 52 + k * 0.7), (EXIT_A[0] - 1 + k * 0.3, EXIT_A[2] - 4)]
        a = trav(pts, t, 101.0 + k * 0.6, 3.8, seed=k + 20, carry=True); ants.append(a)
    ants += queen_group(t, [(1, 48), (8, 56), (EXIT_A[0], EXIT_A[2] - 2)], 101.5, 2.2)
    img = nest_render(cam, t, fi, ants)
    return nlook(img, t)
def leavers(t, t0=110.0):
    out = []
    for k in range(6):
        pts = [(4.5 + 0.4 * k, (k - 2.5) * 0.5), (CRACK - 1, 0.1 * (k - 2.5)), (CRACK + 3, 0.2 * (k - 2.5)), (24, 3 + k * 0.6), (36, 8 + k * 0.4)]
        a = trav(pts, t, t0 + k * 0.35, 6.5, seed=k + 30); a["lift"] = surf_h(a["x"], a["z"], t); out.append(a)
    return out
def s12(t, fi):
    if t < 113.3:
        cam = Cam(21.5, -15, 4.2, 11, -32, focus=19, aperture=1.0)
        img = main_render(cam, t, fi, bridge_crowd(t) + chewers(t) + leavers(t) + east_crowd(t), fogd=220)
    elif t < 116.6:
        cam = Cam(-6 + 0.6 * (t - 113.3), -42, 14, 19, 12, focus=46, aperture=0.6)
        img = main_render(cam, t, fi, bridge_crowd(t) + chewers(t) + east_crowd(t) + leavers(t), fogd=400)
    else:
        cam = crack_cam(t, x=15.0, z=-4.6, h=2.4, pitch=11, yaw=-6, foc=4.8)
        ch = chewers(t)
        if t > 118.2:
            u = ease((t - 118.2) / 0.6); ch[0].update(pitch=-0.12 + 0.45 * u, hd=math.pi + 0.9 * u, aa=2.2 + 0.2 * math.sin(t * 3), ab=2.4)
        img = main_render(cam, t, fi, bridge_crowd(t) + ch + east_crowd(t), fogd=160)
    return look(img, t)
def s13(t, fi):
    cam = Cam(3 + 0.25 * (t - 120), -31, 10.5, 19, 4, focus=31, aperture=0.65)
    img = main_render(cam, t, fi, bridge_crowd(t) + chewers(t) + east_crowd(t), fogd=330)
    return look(img, t)
def s14(t, fi):
    cam = Cam(kf(t, [(130, 3), (140, 6)]), 44, 3.3, 9, 22, focus=22, aperture=1.0)
    ants = queen_group(t, [(6, 52), (12, 60), (EXIT_A[0], EXIT_A[2] - 2), (-13, EXIT_B[2] - 3)], 130.0, 2.4, stop=(133.0, 137.6))
    if t > 137.6:   # turned toward the other slope
        ants = queen_group(t, [(11.5, 59.5), (4, 66), (EXIT_B[0], EXIT_B[2] - 2)], 137.6, 2.0)
    rd = [(EXIT_A[0] + 1, EXIT_A[2] + 4), (16, 66), (13, 63)]
    for k in range(3):
        r_ = trav([(p[0] + k, p[1] + k * 0.8) for p in rd], t, 132.0 + 0.4 * k, 5.0, col=BLK, sc=0.82, seed=k)
        if t > 134.5 + 0.5 * k: ants += grapple(14.5 + k * 1.2, 64 + k, t, 134.5 + 0.5 * k, BLK, RED, seed=k, sc=(0.82, 1.0))
        else: ants.append(r_)
    for k in range(3):
        if t < 134.5 + 0.5 * k: ants.append(trav([(4 + k, 50), (13 + k, 61 + k)], t, 131.0, 5.5, seed=k + 40))
    for k in range(3):
        pts = [(8 + k, 58 + k), (14, 66), (6, 68), (EXIT_B[0] + 1, EXIT_B[2] - 2)]
        ants.append(trav(pts, t, 131.0 + k * 0.4, 3.0, seed=k + 50, carry=True))
    img = nest_render(cam, t, fi, ants, glow_k=0.8)
    return nlook(img, t)
def s15(t, fi):
    cam = crack_cam(t, x=15.2, z=-5.6, h=2.8, pitch=14, yaw=-10, foc=5.8)
    img = main_render(cam, t, fi, bridge_crowd(t) + chewers(t, pause=(145.0, 146.2)) + east_crowd(t), fogd=180)
    return look(img, t)
def s16(t, fi):
    if t < 152.3:
        cam = Cam(-34, -30, 12.5, 21, 42, focus=44, aperture=0.6); img = main_render(cam, t, fi, bridge_crowd(t) + chewers(t) + east_crowd(t), fogd=350)
    elif t < 154.6:
        cam = Cam(10.5, -8.2, 3.0, 9, -38, focus=9, aperture=1.0); img = main_render(cam, t, fi, bridge_crowd(t) + chewers(t) + east_crowd(t), fogd=180)
    elif t < 157.0:
        cam = Cam(14.6, -3.4, 1.9, 9, -10, focus=3.7, aperture=1.0); img = main_render(cam, t, fi, bridge_crowd(t) + chewers(t) + east_crowd(t), fogd=120)
    else:
        ts = 157.0 + (t - 157.0) * 0.22
        cam = Cam(CRACK + 0.4, -2.3, 1.45, 8, -4, focus=2.45, aperture=1.0)
        img = main_render(cam, t, fi, bridge_crowd(t, slow_t=ts) + chewers(t, ts=ts), fogd=90)
    return look(img, t, k=1.0 if t < 157 else 0.5)
def s17(t, fi):
    u = ease((t - 160.4) / 4.8)
    sh = shake(t, TBREAK, 6)
    cam = Cam(lerp(15.0, 2.0, u) + sh, lerp(-7.5, -95, u), 3.4 * (120 / 3.4) ** u, lerp(14, 55, u), lerp(-28, 0, u), focus=lerp(9, 150, u), aperture=lerp(1.0, 0.35, u))
    ch = chewers(TBREAK - 0.01) if t < TBREAK + 0.6 else [A(CRACK + 1.2 + 0.4 * ease((t - TBREAK - 0.6) / 1), 0.1, math.pi, hero=True, aa=2.4, ab=2.4, ph=0.3),
                                                         A(CRACK + 1.9, -0.8, math.pi - 0.6, aa=2.6, ab=2.4), A(CRACK + 1.9, 0.9, math.pi + 0.5, aa=2.5, ab=2.5)]
    for a in ch: a["lift"] = surf_h(a["x"], a["z"], 0)
    img = main_render(cam, t, fi, bridge_crowd(t) + ch + east_crowd(t), fogd=lerp(200, 2000, u))
    if TBREAK < t < TBREAK + 2.5:   # splash rings where the leaf hits the water
        pass
    return look(img, t)
def s18(t, fi):
    if t < 173.3:
        cam = Cam(25 + 0.6 * (t - 170), -16, 5.2, 12, 28, focus=22, aperture=1.0)
        img = main_render(cam, t, fi, east_crowd(t) + bridge_crowd(t), fogd=240); return look(img, t)
    if t < 176.6:
        cam = Cam(4, 50, 3.0, 8, 25, focus=17, aperture=1.0)
        ants = queen_group(t, [(11.5, 59.5), (4, 66), (EXIT_B[0] + 3, EXIT_B[2] - 4)], 171.0, 1.6)
        for k in range(3): ants.append(trav([(22 + k, 60 + 2 * k), (12 + k, 63 + k)], t, 173.3 + 0.3 * k, 3.5, col=BLK, sc=0.82, seed=k))
        return nlook(nest_render(cam, t, fi, ants), t)
    pts = [(17.5, 0.5), (25, 2), (31, 4.5), (NESTH[0], NESTH[1])]
    h = trav(pts, t, 176.6, 6.0, hero=True)
    cam = Cam(h["x"] - 3.2, h["z"] - 6.5, 3.2, 12, 25, focus=7, aperture=1.0)
    return look(main_render(cam, t, fi, [h] + east_crowd(t), fogd=200), t)
MOUTH = (-34.0, 40.0)
def s19(t, fi):
    cam = Cam(-25.5, 31.5, 3.6, 10, -45, focus=12, aperture=1.0)
    ants = []
    for k in range(4):
        cx, cz = MOUTH[0] + 3.2 + 0.4 * k, MOUTH[1] - 2.0 + 1.3 * k
        ants.append(A(cx + 0.2 * math.sin(t * 6 + k), cz, math.pi + 0.3 * math.sin(t * 3 + k), ph=(t * 3 + k * 0.4) % 1, aa=t * 6 + k, ab=t * 6.5 + k, mand=0.5 + 0.5 * math.sin(t * 9 + k), col=RED, pitch=0.2 * math.sin(t * 4 + k)))
    for k in range(6):   # blocked reinforcements behind the collapsing mouth
        x = MOUTH[0] - 4 - 1.8 * k + (2.5 * ease((t - 185.5) / 2) if k % 2 else 0); z = MOUTH[1] - 2 + (k % 3) * 1.5
        hd = 0.0 if t < 185.5 else math.pi + 0.3 * math.sin(k)
        ants.append(A(x, z, hd, ph=(t * 2 + k) % 1, aa=t * 5 + k, ab=t * 5.4, col=BLK, sc=0.82, br=0.8))
    ants += grapple(-12, 44, t, 179.0, BLK, RED, seed=1.1, sc=(0.82, 1)) + grapple(-6, 50, t, 180.5, BLK, RED, seed=2.7, sc=(0.82, 1))
    rr = np.random.default_rng(8); fall = []
    for k in range(70):
        t0 = 181.0 + rr.uniform(0, 5.0); x = MOUTH[0] + rr.uniform(-2.5, 1.5); z = MOUTH[1] + rr.uniform(-3.5, 3.5); r = rr.uniform(0.25, 0.9)
        y = max(0.0, 7.5 - 9.8 * max(0, t - t0) ** 2 * 6) if t > t0 else None
        if y is not None: fall.append(("p", x, z, r, (0.11, 0.08, 0.055), 0.7, rr.uniform(0, 6), y + r * 0.3 * (1 if y > 0 else 0) + (ease((t - 181) / 5) * 0.8 if y == 0 else 0)))
    img = nest_render(cam, t, fi, ants, props=PNEST + fall, glow_k=0.6)
    return nlook(img, t)
def s20(t, fi):
    cam = Cam(-8.5, 60.0, 2.4, 6, -14, focus=11, aperture=1.0)
    ants = []
    hx = trav([(-15, 82), (-13.5, 75), (-12.6, 71.5)], t, 190.0, 5.0, hero=True)
    if t > 192.0:
        ants += grapple(-12.4, 70.2, t, 192.0, BLK, RED, seed=0.4, hero_b=True, sc=(0.82, 1.0), spin=0.1)
        if t > 196.0:
            dr = ease((t - 196.0) / 2.5)
            for a in ants[-2:]: a["x"] -= 2.2 * dr; a["z"] += 0.6 * dr
            ants[-1]["pitch"] = -0.25 * dr; ants[-1]["roll"] = 0.3 * dr
    else: ants.append(hx)
    for k, (gx, gz) in enumerate(((-10, 72), (-14.5, 73.5))): ants.append(A(gx, gz, -1.2 + k * 0.4, aa=t * 6, ab=t * 6.2, mand=0.4 + 0.4 * math.sin(t * 8 + k), col=RED, ph=(t * 2 + k) % 1))
    if t > 195.4: ants += grapple(-10.6, 68.6, t, 195.4, BLK, RED, seed=1.9, sc=(0.82, 1.0))
    else: ants.append(trav([(-4, 63), (-9.5, 68)], t, 193.0, 4.0, col=BLK, sc=0.82, seed=2))
    ants.append(trav([(-2, 62), (-11, 69)], t, 191.0, 3.0, col=BLK, sc=0.82, seed=3)) if t < 192 else None
    ants += queen_group(t, [(-2, 63), (-8, 72), (-15, 79), (-18, 86)], 196.0, 2.6)
    rr = np.random.default_rng(4); mud = []
    for k in range(40):
        t0 = 196.0 + rr.uniform(0, 3.5); x = -15.5 + rr.uniform(-2, 1.5); z = 70 + rr.uniform(-2, 3); r = rr.uniform(0.2, 0.7)
        if t > t0: mud.append(("p", x, z, r, (0.28, 0.21, 0.14), 0.7, rr.uniform(0, 6), max(0.0, 5 - 60 * (t - t0) ** 2)))
    img = nest_render(cam, t, fi, [a for a in ants if a], props=PNEST + mud, glow_k=0.9)
    return nlook(img, t)
def s21(t, fi):
    if t < 203.3:
        cam = Cam(31 + 0.5 * (t - 200), -13, 5.0, 12, 22, focus=20, aperture=1.0)
        return look(main_render(cam, t, fi, east_crowd(t) + bridge_crowd(t), fogd=240), t)
    if t < 206.6:
        cam = Cam(-19, 37, 3.0, 9, 8, focus=10, aperture=1.0)
        ants = grapple(-17, 47, t, 201.0, BLK, RED, seed=0.6, sc=(0.82, 1)) + [A(-15.5, 46.0, 0.4, ph=0.2, aa=2.4, ab=2.6, mand=0.6 + 0.4 * math.sin(t * 10), col=RED)]
        if t > 205.0: ants[0].update(st=3, mand=0.3)
        ants += [A(-21.5, 50.5, 2.0, st=3, col=BLK, sc=0.82), A(-13.0, 49.0, 1.0, aa=t * 4, ab=t * 4.2, col=RED, ph=(t * 2) % 1)]
        return nlook(nest_render(cam, t, fi, ants, glow_k=0.7), t)
    x0, ytop = rtop(4.0)
    cam = Cam(x0 - 6.5, -4.0, ytop + 4.0, 16, 28, focus=10, aperture=1.0)
    def hole(img, cam):
        ph = np.linspace(0, 2 * np.pi, 30); x, y = rtop(3.0)
        P, zz = cam.proj(np.stack([x + np.cos(ph) * 2.6, np.full(30, y + 0.05), 3.0 + np.sin(ph) * 1.7], -1))
        if (zz > 0.5).all(): poly(img, P, (0.03, 0.02, 0.015), 0.95)
    ants = []
    for k, dl in enumerate((0, 1.0, 1.6, 2.3, 2.9)):
        a = trav([(rtop(3.0)[0], 3.0), (rtop(9)[0] + 0.5 * (k % 2 - 0.5), 9.0), (rtop(16)[0], 16.0)], t, 207.0 + dl, 2.4, col=RED, sc=1.75 if k == 0 else 1.0, gk=1.6 if k == 0 else 1.0, carry=(k in (2, 4)), seed=k)
        u = math.hypot(a["x"] - rtop(3.0)[0], a["z"] - 3.0)
        a["lift"] = rtop(a["z"])[1] + 0.05; a["br"] = min(1.0, 0.2 + u / 2.0) * (1.08 if k == 0 else 1.0)
        if t > 207.0 + dl: ants.append(a)
    img = root_render(cam, t, fi, ants, extra=[(1e4 - 1, hole)])
    img = glow(img, (x0 + 10, ytop + 30, 60), cam, 700, (0.18, 0.16, 0.12), 0.8)
    return look(img, t)
def s22(t, fi):
    cam = Cam(kf(t, [(210, -24), (220, 8)]), kf(t, [(210, 20), (220, 26)]), kf(t, [(210, 3.4), (220, 2.2)]), 10, 10, focus=kf(t, [(210, 22), (220, 9)]), aperture=1.0)
    rr = np.random.default_rng(12); mud = []
    for k in range(120):
        x = rr.uniform(-40, 30); z = rr.uniform(40, 85)
        if abs(x - 12) < 5 and z < 46: continue
        mud.append(("p", x, z, rr.uniform(0.4, 2.4), (0.24, 0.18, 0.12), 0.55, rr.uniform(0, 6), 0.0))
    props = [p for p in PNEST if p[0] != "l"] + gen_props(24, (-8, 6), (38, 48), larvae=7) + mud
    hero = A(12.6, 34.0, 2.6, ph=0.3, aa=2.6, ab=2.3, mand=0.25, col=RED, hero=True, lc=0.6, pitch=0.12, lift=-0.2)
    def bury(img, cam):
        r2 = np.random.default_rng(5)
        for k in range(16):
            pebble(img, cam, 12.6 + 1.6 + r2.uniform(-1.4, 1.6), 34.0 - 0.9 + r2.uniform(-1.1, 1.3), r2.uniform(0.5, 1.0), (0.22, 0.165, 0.11), 0.7, r2.uniform(0, 6), 0.0)
    _, zz = cam.proj(np.array([12.6, 0, 34.0]))
    img = nest_render(cam, t, fi, [hero], flood=0.9, props=props, extra=[(float(zz) - 0.5, bury)], glow_k=0.35)
    # drips
    rr2 = np.random.default_rng(fi); 
    return nlook(img, t)
def s23(t, fi):
    zc = lerp(10, 62, (t - 220) / 10)
    x0, ytop = rtop(zc)
    cam = Cam(x0 - 2.5, zc - 14 - 0.3 * (t - 220), ytop + 9.5, 30, 6, focus=18, aperture=0.9)
    ants = []
    for k, (dz, dx, carry) in enumerate(((0, 0, False), (3.5, 0.8, False), (-3.4, -0.6, True), (6.5, -0.4, True), (-6.4, 0.7, False), (9.5, 0.3, False), (-9.4, -0.2, True))):
        z = 20 + 5.2 * (t - 220) + dz
        x = rtop(z)[0] + dx + 0.3 * math.sin(z * 0.4 + k)
        a = A(x, z, math.pi / 2 + 0.1 * math.sin(z * 0.4 + k), ph=(z / 0.55) % 1, aa=t * 4 + k, ab=t * 4.3 + k, col=RED, sc=1.75 if k == 0 else 1.0, gk=1.6 if k == 0 else 1.0, carry=carry)
        a["lift"] = rtop(z)[1] + 0.05; ants.append(a)
    img = root_render(cam, t, fi, ants)
    return look(img, t)
def s24(t, fi):
    u = ease((t - 230) / 7.0)
    cam = Cam(lerp(-6, 0, u), lerp(-58, -150, u), 28 * (240 / 28) ** u, lerp(24, 48, u), 0, focus=lerp(70, 300, u), aperture=lerp(0.6, 0.25, u))
    img = main_render(cam, t, fi, bridge_crowd(t), fogd=lerp(500, 3500, u))
    img = look(img, t)
    if t > 233.8: img *= 1 - ease((t - 233.8) / 2.2)
    return img
SHOTF = {f"S{i+1:02d}": f for i, f in enumerate([s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20, s21, s22, s23, s24])}
def frame(fi):
    t = fi / FPS
    n, a, b = shot_at(t)
    img = SHOTF[n](t, fi)
    if n in ("S10",) and t < a + 0.4: pass
    img = overlay_text(img, t)
    img = grain(img, fi, 0.016)
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prep":
        for n in sys.argv[2:]: S(n); print("sim", n, "ok")
    elif cmd == "test":
        for ts in sys.argv[2:]:
            im = frame(int(round(float(ts) * FPS))); cv2.imwrite(f"/tmp/br_{ts}.jpg", im[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 88])
    elif cmd == "sheet":
        out = sys.argv[2]; ims = [cv2.resize(frame(int(round(float(ts) * FPS))), (640, 360)) for ts in sys.argv[3:]]
        while len(ims) % 3: ims.append(np.zeros_like(ims[0]))
        rows = [np.hstack(ims[i:i + 3]) for i in range(0, len(ims), 3)]
        cv2.imwrite(out, np.vstack(rows)[..., ::-1])
    elif cmd == "render":
        f0, f1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        import subprocess
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for fi in range(f0, f1): p.stdin.write(frame(fi).tobytes())
        p.stdin.close(); p.wait()
