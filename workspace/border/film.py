# 《无声的边境》 renderer. python3 film.py test t1 t2 ... | sheet t... | render f0 f1 out.mp4 | prep
import sys, os, math, numpy as np, cv2
from world import *
from cues import *
import maps, sim
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
FONT = "/workspace/work/tomato/NotoSansSC-Bold.otf"; FONTB = "/workspace/work/tomato/NotoSansSC-Black.otf"
def ease(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def lerp(a, b, u): return a + (b - a) * u
def kf(t, keys, mode="smooth"):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0); u = ease(u) if mode == "smooth" else u
            if mode == "exp": return v0 * (v1 / v0) ** ease((t - t0) / (t1 - t0))
            return v0 + (v1 - v0) * u
    return keys[-1][1]
def sky_grad(top, bot):
    y = np.linspace(0, 1, H)[:, None, None]; return (np.array(top, np.float32) * (1 - y) + np.array(bot, np.float32) * y).astype(np.float32)

# ---------------- props ----------------
GREEN = [(0.26, 0.36, 0.15), (0.32, 0.42, 0.18), (0.22, 0.30, 0.13), (0.45, 0.42, 0.24), (0.38, 0.33, 0.20)]
STONE = [(0.52, 0.46, 0.38), (0.42, 0.38, 0.33), (0.60, 0.55, 0.47), (0.36, 0.30, 0.25), (0.55, 0.45, 0.35)]
def gen_props(seed, xr, zr, npeb=0, nbl=0, nroot=0, pr=(0.25, 2.2), bh=(25, 95), clear=None, rz=None, rrad=(2.5, 6)):
    rng = np.random.default_rng(seed); P = []
    def ok(x, z): return clear is None or not clear(x, z)
    for i in range(npeb):
        x, z = rng.uniform(*xr), rng.uniform(*zr)
        if ok(x, z): P.append(("p", x, z, rng.uniform(*pr) * (1 + 2 * rng.random() ** 6), STONE[rng.integers(5)], rng.uniform(0.45, 0.8), rng.uniform(0, 6.28), rng.random()))
    for i in range(nbl):
        x, z = rng.uniform(*xr), rng.uniform(*zr)
        if ok(x, z): P.append(("b", x, z, rng.uniform(*bh), rng.uniform(1.6, 4.5), rng.uniform(-0.6, 0.6), rng.uniform(0, 6.28), np.array(GREEN[rng.integers(5)]) * rng.uniform(0.75, 1.1)))
    for i in range(nroot):
        z0 = rng.uniform(*(rz or zr)); x0 = rng.uniform(*xr); ang = rng.uniform(-1.2, 1.2); L = rng.uniform(60, 220); r0 = rng.uniform(*rrad)
        u = np.linspace(-0.5, 0.5, 70); bend = rng.uniform(-0.6, 0.6)
        xs = x0 + u * L * np.cos(ang + bend * u * 2); zs = z0 + u * L * np.sin(ang + bend * u * 2) + 4 * np.sin(u * 9 + i)
        ys = r0 * 0.2 + r0 * 0.7 * np.clip(np.sin((u + 0.5) * math.pi * rng.uniform(1, 2.2)), 0, None)
        rad = r0 * (1 - 0.35 * np.abs(u)); P.append(("r", np.stack([xs, ys, zs], -1), rad, np.array([0.31, 0.25, 0.19]) * rng.uniform(0.8, 1.1)))
    return P

def prop_anchor(p):
    if p[0] == "r": return p[1][len(p[1]) // 2]
    return np.array([p[1], 0.0, p[2]])

def render(cam, t, fi, mats, props, ants=(), sky=None, fogd=500.0, light=1.0, gk=None, shadow_k=0.5, bounce=None,
           decal=None, water=None, extra_dark=None, post_ground=None, dofk=1.0, objlight=1.0, bok=0.0):
    sky = sky if sky is not None else sky_grad((0.62, 0.68, 0.70), (0.80, 0.78, 0.70))
    if bok:
        sky = np.repeat(sky, W, axis=1) if sky.shape[1] == 1 else sky.copy()
        sky = sky * (1 - bok * 0.45) + BOKEH[..., :3] * bok * 0.45
    img, dep, GX, GZ = ground(cam, mats, sky=sky, fogd=fogd, light=light)
    if water is not None: img = water(img, GX, GZ, dep)
    if extra_dark is not None: img *= extra_dark(GX, GZ, dep)[..., None]
    if decal is not None: decal(img, cam)
    if post_ground is not None: post_ground(img, cam)
    # shadows
    sm = np.zeros((H, W), np.float32)
    for p in props:
        if p[0] == "p":
            _, zc = cam.proj(np.array([p[1], 0, p[2]]))
            if 0.8 < zc < fogd * 2: shadow_blob(sm, cam, p[1] + 0.35 * p[3], p[2] - 0.25 * p[3], p[3] * 1.2, p[3] * 0.9, 0.3)
    for a in ants:
        if a[7] == 3: continue
        _, zc = cam.proj(np.array([a[0], 0, a[1]]))
        if 0.8 < zc < fogd * 1.5: ant_shadow(sm, cam, a[0], a[1], a[2])
    sm = cv2.GaussianBlur(sm, (0, 0), 7); img *= (1 - shadow_k * np.clip(sm, 0, 1))[..., None]
    # drawables
    D = []
    for p in props:
        s_, zc = cam.proj(prop_anchor(p))
        if zc < 1.0 or zc > fogd * 3: continue
        if p[0] != "r" and (s_[0] < -600 or s_[0] > W + 600 or s_[1] < -900 or s_[1] > H + 600): continue
        D.append((zc, "p", p))
    for a in ants:
        s_, zc = cam.proj(np.array([a[0], 0, a[1]]))
        if zc < 1.2 or zc > fogd * 3 or s_[0] < -300 or s_[0] > W + 300 or s_[1] < -300 or s_[1] > H + 300: continue
        D.append((zc, "a", a))
    D.sort(key=lambda d: -d[0])
    fogc = lambda zc, c: np.asarray(c) * math.exp(-zc / fogd) + sky[min(H - 1, max(0, int(cam.proj(np.array([0, 0, 0]))[0][1]))), 0] * (1 - math.exp(-zc / fogd)) if False else np.asarray(c)
    for zc, k, p in D:
        fade = math.exp(-zc / fogd)
        if k == "p":
            if p[0] == "p":
                lift = 0.0
                if bounce is not None: lift = bounce(p, t)
                pebble(img, cam, p[1], p[2], p[3], np.array(p[4]) * fade * objlight + (1 - fade) * 0.7, p[5], p[6], lift)
            elif p[0] == "b":
                blade(img, cam, p[1], p[2], p[3], p[4], p[5], p[6], np.array(p[7]) * fade * objlight + (1 - fade) * 0.72, t=t, sway=0.08)
            else:
                root(img, cam, p[1], p[2], np.array(p[3]) * fade * objlight + (1 - fade) * 0.7)
        else:
            x, z, hd, ph, aa, ab, mand, st, br = p[:9]; lc = p[9] if len(p) > 9 else 0.0
            ant(img, cam, x, z, hd, ph, aa, ab, mand, int(st), bright=br * (fade + (1 - fade) * 1.6) * objlight, legcurl=lc)
    img = dof(img, dep, cam) if dofk > 0 else img
    return img

def _bokeh():
    rng = np.random.default_rng(21); im = np.zeros((H, W, 3), np.float32)
    im[:] = sky_grad((0.30, 0.40, 0.22), (0.55, 0.58, 0.40))
    for i in range(70):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H * 0.75), rng.uniform(25, 110)
        c = np.array([rng.uniform(0.6, 1.0), rng.uniform(0.75, 1.0), rng.uniform(0.4, 0.75)]) * rng.uniform(0.5, 1.0)
        cv2.circle(im, (int(x), int(y)), int(r), tuple(float(v) for v in c), -1, cv2.LINE_AA)
    for i in range(40):
        x = rng.uniform(0, W); cv2.line(im, (int(x), H), (int(x + rng.uniform(-200, 200)), int(rng.uniform(0, H * 0.4))), (0.18, 0.26, 0.12), int(rng.uniform(20, 60)), cv2.LINE_AA)
    return cv2.GaussianBlur(im, (0, 0), 18)
BOKEH = _bokeh()
# ---------------- subtitles / text ----------------
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
    if xb <= xa or yb <= ya: return
    s = spr[ya - y0:yb - y0, xa - x0:xb - x0]; a = s[..., 3:4] * alpha
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - a) + s[..., :3] * a
def fadein(t, a, b, d=0.3): return min(ease((t - a) / d), ease((b - t) / d))
def overlay_text(img, t):
    for s, a, b in SUBS:
        if a - 0.01 <= t <= b + 0.01:
            blit(img, text_sprite(s, 42, box=0.34), W / 2, 985, fadein(t, a, b, 0.25))
    s, a, b = CAPTION
    if a <= t <= b:
        al = fadein(t, a, b, 0.6); sp = text_sprite(s, 30, box=0.0)
        blit(img, sp, 140 + sp.shape[1] / 2, 120, al)
        img[100:140, 118:121] = img[100:140, 118:121] * (1 - al) + 0.95 * al
    L, src, a, b = CARD
    if a <= t <= b:
        al = fadein(t, a, b, 0.8)
        for i, line_ in enumerate(L):
            blit(img, text_sprite(line_, 48 if i else 40, col=(240, 236, 228) if i else (200, 196, 188)), W / 2, 430 + i * 86 + (0 if i else -10), al * min(1, ease((t - a - i * 0.5) / 0.8)))
        blit(img, text_sprite(src, 26, col=(170, 168, 160)), W / 2, 720, al * ease((t - a - 1.6) / 0.8))
    s, a, b = TITLE
    if a <= t:
        al = ease((t - a) / 1.4)
        blit(img, text_sprite(s, 112, font=FONTB, col=(236, 232, 224), spacing=30, pad=(10, 10)), W / 2, H / 2 - 10, al)
    return img
def label(img, s, x, y, a, size=28, col=(230, 226, 214)):
    if a > 0: blit(img, text_sprite(s, size, col=col), x, y, a)

# ---------------- simulations (cached) ----------------
def zbE(x): return 5.0 * math.sin(x / 23.0) + 2.5 * math.sin(x / 8.7 + 1.0)
_S = {}
def S(name):
    if name in _S: return _S[name]
    c = os.path.join(HERE, f"sim_{name}.npz")
    if name == "B":
        paths = [sim.curve((-160, z), (160, z + 3), 4, i) for i, z in enumerate((-2, 3, 9, 16, 26, 40))]
        paths += [p[::-1].copy() for p in paths[1::2]]
        cfg = dict(seed=3, t0=15.0, t1=18.4, warm=40, paths=paths, path_colony=[0] * len(paths), n=150, speed=(7, 11), lat=0.5, spawn_spread=0.5)
    elif name == "C":
        paths = [sim.curve((-90, -50), (90, 45), 10, 1), sim.curve((90, -45), (-90, 50), 10, 2), sim.curve((-90, 40), (90, -50), 8, 3)]
        cfg = dict(seed=4, t0=30.8 - 1.0, t1=35.5, warm=25, paths=paths, path_colony=[0, 0, 0], n=110, speed=(5, 8), lat=0.6, spawn_spread=0.4)
    elif name == "DS":
        paths = [sim.curve((x0, -260), (x0 * 0.4 + 10 * i, zbE(x0 * 0.4) - 1), 25, 10 + i) for i, x0 in enumerate(np.linspace(-220, 220, 7))]
        paths += [sim.curve((x0, 260), (x0 * 0.4 - 8 * i, zbE(x0 * 0.4) + 1), 25, 30 + i) for i, x0 in enumerate(np.linspace(-200, 230, 7))]
        cfg = dict(seed=5, t0=46.5, t1=55.0, warm=30, paths=paths, path_colony=[0] * 7 + [1] * 7, n=520, speed=(7, 11), lat=0.7, spawn_spread=0.3,
                   border=dict(zb=zbE, off=1.5), p_fight=0.0)
    elif name == "D":
        paths = []
        for i, z in enumerate((5, -4.5, 11, 22, -15, 35, 60, 90)):
            paths.append(sim.curve((-140, z), (40, z * 0.3), 6, 50 + i)); paths.append(sim.curve((140, z + 2), (-40, z * 0.3 + 1), 6, 70 + i))
        cfg = dict(seed=6, t0=55.0, t1=75.0, warm=0, paths=paths, path_colony=[0, 1] * 8, n=260, speed=(3.2, 5.5), lat=0.6, spawn_spread=0.9, fill=0.62,
                   p_fight=0.85, fight_after=65.3, fight_dur=(4, 12), p_join=0.12, join_r=3.2)
    elif name == "EF":
        paths = []
        for i, x0 in enumerate(np.linspace(-320, 320, 18)):
            xe = x0 * 0.8 + np.random.default_rng(i).uniform(-15, 15)
            paths.append(sim.curve((x0, -230), (xe, zbE(xe) - 1), 30, 100 + i))
            xe2 = x0 * 0.8 + np.random.default_rng(50 + i).uniform(-15, 15)
            paths.append(sim.curve((x0 + 10, 230), (xe2, zbE(xe2) + 1), 30, 200 + i))
        cfg = dict(seed=7, t0=75.0, t1=110.0, warm=8, paths=paths, path_colony=[0, 1] * 18, n=1300, speed=(7, 12), lat=0.8, spawn_spread=0.15, fill=1.0,
                   border=dict(zb=zbE, off=1.0), p_fight=0.8, fight_after=-1e9, fight_dur=(3, 10), p_join=0.1, join_r=3.0, max_cluster=7,
                   dead_litter=900, litter_x=(-300, 300), litter_w=3.5)
    elif name == "G":
        paths = [sim.curve((-60, z), (60, z + 4), 6, 300 + i) for i, z in enumerate((-4, 4, 9, 18, 30))]
        paths += [p[::-1].copy() for p in paths[::2]]
        cfg = dict(seed=8, t0=110.0, t1=134.0, warm=20, paths=paths, path_colony=[0] * len(paths), n=70, speed=(6, 9), lat=0.6, spawn_spread=0.5, timescale=0.3)
    _S[name] = sim.run(cfg, c); return _S[name]

def ants_from(sd, fi, bright=1.0, xform=None, keep=None):
    o = []
    vis = sd["vis"][fi]
    for i in np.nonzero(vis > 0)[0]:
        x, z, hd = float(sd["x"][fi, i]), float(sd["z"][fi, i]), float(sd["hd"][fi, i])
        if xform: x, z, hd = xform(x, z, hd)
        if keep and not keep(x, z): continue
        o.append((x, z, hd, float(sd["ph"][fi, i]), float(sd["aa"][fi, i]), float(sd["ab"][fi, i]), float(sd["mand"][fi, i]), int(sd["st"][fi, i]), bright))
    return o
def sfi(name, t, t0): sd = S(name); return sd, int(np.clip(round((t - t0) * FPS), 0, sd["x"].shape[0] - 1))

# ---------------- shots ----------------
def mats_sidewalk(gx, gz):
    wc = np.clip((285 - gz) / 25, 0, 1); return [("concrete", wc), ("soil", 1 - wc)]
def mats_soil(gx, gz): return [("soil", 1.0)]
def mats_mix(gx, gz):
    m = 0.5 + 0.5 * np.sin(gx * 0.02 + 1) * np.sin(gz * 0.017); return [("soil", m), ("sand", 1 - m)]
def mats_sand(gx, gz): return [("sand", 1.0)]

PA = gen_props(1, (-260, 260), (-170, 270), npeb=240, pr=(0.25, 2.4)) + \
     gen_props(2, (-260, 260), (300, 1100), npeb=260, nbl=230, nroot=6, pr=(0.3, 3.0), bh=(30, 120), rz=(425, 650), rrad=(3, 7),
               clear=lambda x, z: abs(x) < 9 and z < 440) + \
     gen_props(3, (-40, 40), (382, 420), npeb=50, pr=(0.2, 1.3))
def bounceA(p, t):
    out = 0.0
    for k, st in enumerate(STEPS):
        u = t - st - 0.01 * (p[2] + 150) / 40
        if 0 < u < 0.22: out += p[3] * (0.35 + 0.5 * p[7]) * math.sin(math.pi * u / 0.22) * (0.6 + 0.1 * k)
    return out if p[2] < 290 else out * 0.2
def shotA(t, fi):
    cz = kf(t, [(0, -150), (11.5, 387.0), (15, 388.0)]); h = kf(t, [(0, 36), (11.5, 3.3), (15, 3.1)], "exp")
    pit = kf(t, [(0, 13), (11.5, 7.0), (15, 6.5)]); foc = kf(t, [(0, 140), (11.5, 18), (15, 15.5)], "exp")
    shake = sum(max(0, 1 - (t - st) / 0.35) * (t > st) for st in STEPS)
    cam = Cam(0.6 + 0.8 * math.sin(t * 0.3) + shake * 0.12 * math.sin(t * 90), cz, h + shake * 0.08 * math.sin(t * 77), pit, 0.0, focus=foc, aperture=1.0)
    sky = sky_grad((0.55, 0.62, 0.70), (0.88, 0.80, 0.66))
    def dark(GX, GZ, dep):
        d = 1 - 0.55 * np.clip((GZ - 399.0) / 3.0, 0, 1)                         # leaf shadow hiding the ant
        if 3.2 < t < 6.8:                                                           # a human shadow sweeps over the pavement
            cx = lerp(-400, 500, (t - 3.2) / 3.6); d = d * (1 - 0.35 * np.clip(1 - np.abs(GX - cx) / 160, 0, 1) ** 0.5 * (GZ < 300))
        return d.astype(np.float32)
    def joints(img, cam):
        for zj in (110.0, -40.0):
            xs = np.linspace(-700, 700, 60); P, zz = cam.proj(np.stack([xs, np.zeros(60), np.full(60, zj)], -1))
            if (zz > 1).all(): line(img, P, (0.30, 0.29, 0.27), max(1, cam.f * 1.4 / zz.mean()), 0.75)
    ants = []
    if t > 11.0:
        az = 404.0 - 1.6 * (t - 11.0); br = 0.3 + 0.7 * np.clip((402.0 - az) / 3.5, 0, 1)
        ants.append((0.4, az, -math.pi / 2 + 0.08 * math.sin(t * 1.7), (4.0 - az * 0.0 + 2.0 * (t - 11.0)) / 0.55 % 1, t * 3, t * 3.3, 0.0, 0, br))
    fog = kf(t, [(0, 900), (11.5, 260)], "exp")
    img = render(cam, t, fi, mats_sidewalk, PA, ants, sky=sky, fogd=fog, light=1.05, bounce=bounceA, decal=joints, extra_dark=dark, bok=float(np.clip((t - 5) / 5, 0, 1)) * 0.9)
    img = grade(img, sat=0.88, warm=0.025, contrast=1.05, vign=0.4)
    return img

PB = gen_props(4, (-120, 220), (-14, 300), npeb=420, nbl=160, nroot=3, pr=(0.25, 2.2), bh=(30, 110), rz=(55, 120),
               clear=lambda x, z: -12 < z < 50 and not (z < -8))
def shotB(t, fi):
    cam = Cam(-25 + 11 * (t - 15), -19, 4.4, 8, 0, focus=20, aperture=1.0)
    sd, i = sfi("B", t, 15.0)
    img = render(cam, t, fi, mats_mix, PB, ants_from(sd, i), sky=sky_grad((0.50, 0.58, 0.55), (0.78, 0.76, 0.64)), fogd=300, bok=0.9)
    return grade(img, sat=0.85, warm=0.02, contrast=1.05)

def shotM1(t, fi):
    img, mv = maps.world_map(t, 18.2)
    u = t - 18.2
    label(img, "原产地 · 南美洲", *(mv(*maps.ORIGIN) + np.array([0, 44])), ease((u - 0.6) / 0.8))
    for nm, p, a0 in (("加州", maps.CA, 4.8), ("欧洲", maps.EU, 6.2), ("日本", maps.JP, 7.8)):
        label(img, nm, *(mv(*p) + np.array([0, -40])), ease((u - a0) / 0.6))
    return grade(img, vign=0.5, sat=1.0)

PC = gen_props(5, (-160, 160), (-20, 400), npeb=380, nbl=120, nroot=4, pr=(0.25, 2.4), rz=(80, 200), clear=lambda x, z: z < 60 and abs(x) < 120)
def shotC(t, fi):
    cam = Cam(lerp(-4, 4, (t - 29.8) / 6), -34 + 1.2 * (t - 30.8), 8.0, 17, 0, focus=36, aperture=0.9)
    sd, i = sfi("C", t, 29.8)
    img = render(cam, t, fi, mats_soil, PC, ants_from(sd, i), sky=sky_grad((0.48, 0.56, 0.52), (0.75, 0.74, 0.62)), fogd=350, bok=0.8)
    return grade(img, sat=0.85, warm=0.015, contrast=1.06)

def shotM2(t, fi):
    u = t - 35.5
    ck = maps.contact_km()
    # phase 1: world zoom
    if t < 41.0:
        k = 5.2 * (260 / 5.2) ** ease(u / 5.3); cl = lerp(-20, maps.LH[0], ease(u / 4.2)); ca = lerp(12, maps.LH[1], ease(u / 4.2))
        img = maps.base_map(maps.MapView(cl, ca, k))
        p = maps.MapView(cl, ca, k)(*maps.LH)
        maps.glow_dot(img, p, 6, maps.GLOW, ease((u - 1.0) / 1.0))
        if u < 2.0: maps.glow_dot(img, maps.MapView(cl, ca, k)(*maps.CA), 10, np.array([1, .85, .55]), 1 - ease(u / 2))
    if t > 39.8:
        kp = kf(t, [(39.8, 30), (41.5, 110), (47.5, 520)], "exp")
        cx = lerp(0.0, ck[0], ease((t - 41.0) / 6.5)); cy = lerp(0.0, ck[1], ease((t - 41.0) / 6.5))
        loc, tr = maps.local_map(t, cx, cy, kp, regions=ease((t - 41.6) / 1.4), border_glow=0.75 + 0.25 * math.sin(t * 3))
        label(loc, "霍奇斯湖", *tr(np.array([[-2.4, 0.75]]))[0], ease((t - 41.2) / 0.8) * (1 - ease((t - 45.5) / 1)), 26, (150, 175, 190))
        label(loc, "加州大群落", *tr(np.array([[-2.2, -1.3]]))[0], ease((t - 42.4) / 0.8) * (1 - ease((t - 45.8) / 1)), 30, (245, 190, 120))
        label(loc, "霍奇斯湖群落", *tr(np.array([[1.4, 1.9]]))[0], ease((t - 42.9) / 0.8) * (1 - ease((t - 45.8) / 1)), 30, (140, 215, 220))
        a = ease((t - 39.8) / 1.2)
        img = loc if t >= 41.0 else img * (1 - a) + loc * a
    return grade(img, vign=0.5)

PDS = gen_props(6, (-400, 400), (-400, 400), npeb=900, nbl=60, nroot=7, pr=(0.4, 3.0), bh=(20, 60), rrad=(2, 5))
def shotDS(t, fi):
    h = kf(t, [(46.5, 300), (55.0, 52)], "exp")
    cam = Cam(0, -2, h, 89.0, kf(t, [(46.5, -8), (55, 6)]), focus=h, aperture=0.5)
    sd, i = sfi("DS", t, 46.5)
    def overlay(img, cam):
        al = 0.30 * (1 - ease((t - 48.5) / 2.5))
        if al <= 0: return
        xs = np.linspace(-1500, 1500, 200); zb = np.array([zbE(x) for x in xs])
        top, _ = cam.proj(np.stack([xs, np.zeros_like(xs), zb], -1))
        far_hi = np.array([[W + 3000, -3000], [-3000, -3000]]); far_lo = np.array([[W + 3000, H + 3000], [-3000, H + 3000]])
        poly(img, np.vstack([top, far_lo]), (0.95, 0.62, 0.25), al); poly(img, np.vstack([top, far_hi]), (0.25, 0.75, 0.80), al)
        line(img, top, (1, 0.95, 0.85), 2, al * 2.5)
    img = render(cam, t, fi, mats_mix, PDS, ants_from(sd, i), sky=sky_grad((0.5, 0.5, 0.45), (0.5, 0.5, 0.45)), fogd=3000, post_ground=None)
    overlay(img, cam)
    return grade(img, sat=0.85, contrast=1.08, warm=0.01)

PD = gen_props(7, (-150, 150), (-25, 400), npeb=520, nbl=150, nroot=5, pr=(0.2, 2.0), bh=(30, 110), rz=(30, 90),
               clear=lambda x, z: (abs(x) < 6 and abs(z) < 4) or (z < 18 and abs(x) < 70)) + \
     gen_props(8, (-60, 60), (-12, 18), npeb=160, pr=(0.15, 0.7), clear=lambda x, z: abs(x) < 4 and abs(z) < 2.5)
def pairD(t):
    # A from left (hd 0), B from right (hd pi). returns two ant tuples
    xa = kf(t, [(55, -11.0), (59.4, -1.78)]); xb = kf(t, [(55, 11.0), (59.4, 1.78)])
    ha, hb = 0.0, math.pi; ma = mb = 0.0; aa = t * 4; ab = t * 4.4; ba = t * 4.2; bb = t * 3.9; za = zb = 0.0
    if t > 59.4:
        u = t - 59.4
        aa = 2.6 + 0.35 * math.sin(u * 13); ab = 2.6 + 0.35 * math.sin(u * 11 + 1); ba = 2.6 + 0.35 * math.sin(u * 12 + 2); bb = 2.6 + 0.35 * math.sin(u * 14)
        ha = 0.04 * math.sin(u * 2.1); hb = math.pi + 0.05 * math.sin(u * 1.7 + 1)
    if t > BITE:
        u = t - BITE
        xb = 1.78 - 0.55 * ease(u / 0.1) + 0.2 * ease((u - 0.25) / 0.4); mb = 1.0 if u < 0.06 else 0.2 + 0.6 * abs(math.sin(u * 9))
        xa = -1.78 - 0.25 * ease(u / 0.12) + 0.12 * math.sin(u * 7)
        ha = 0.25 * math.sin(u * 5); ma = 0.5 + 0.5 * math.sin(u * 11)
        if u > 0.6:   # grapple: rotate around a drifting centre
            w = 0.35 * (u - 0.6); c = np.array([0.15 * math.sin(u * 0.9), 0.3 * math.sin(u * 0.6)])
            ra = np.array([math.cos(math.pi + w), math.sin(math.pi + w)]) * 1.55; rb = -ra * 0.98
            xa, za = c + ra; xb, zb = c + rb; ha = math.atan2(-ra[1], -ra[0]) + 0.2 * math.sin(u * 6); hb = math.atan2(-rb[1], -rb[0]) + 0.2 * math.sin(u * 5)
        aa += u * 9; ab += u * 8; ba += u * 9; bb += u * 10
    pha = (xa + 20) / 0.55 % 1 if t < 59.4 else (0.2 + (0.15 * math.sin((t - 59) * 15) if t > BITE else 0))
    phb = (-xb + 20) / 0.55 % 1 if t < 59.4 else (0.6 + (0.15 * math.sin((t - 59) * 17) if t > BITE else 0))
    return [(xa, za, ha, pha, aa, ab, ma, 0, 1.0), (xb, zb, hb, phb, ba, bb, mb, 0, 1.0)]
def shotD(t, fi):
    z = kf(t, [(55, -12.5), (59.6, -10.2), (68.0, -10.0), (75.0, -75.0)]); h = kf(t, [(55, 2.6), (68, 2.6), (75, 46)], "exp")
    pit = kf(t, [(55, 6), (68, 6), (75, 33)])
    sh = max(0, 1 - (t - BITE) / 0.4) * (t > BITE) * 0.06
    foc = math.hypot(z, h)
    cam = Cam(0.3 * math.sin(t * 0.4) + sh * math.sin(t * 80), z, h, pit, 0, focus=foc, aperture=kf(t, [(55, 1.0), (68, 1.0), (75, 0.45)]))
    sd, i = sfi("D", t, 55.0)
    bg = ants_from(sd, i, keep=lambda x, z: (not (abs(x) < 4.2 and abs(z) < 3.2) or t > 66.5) and (t > 64.0 or abs(x) > 9 or z > 9 or z < -9))
    img = render(cam, t, fi, mats_mix, PD, bg + pairD(t), sky=sky_grad((0.46, 0.52, 0.48), (0.70, 0.68, 0.58)), fogd=380, bok=0.85)
    return grade(img, sat=0.82, contrast=1.08, warm=0.01)

PE = gen_props(9, (-360, 360), (-60, 240), npeb=1800, nbl=260, nroot=10, pr=(0.25, 2.6), bh=(30, 120), rz=(-40, 120),
               clear=lambda x, z: (zbE(x) - 13 < z < zbE(x) - 3)) + gen_props(10, (-360, 360), (-240, -60), npeb=500, nbl=60, pr=(0.3, 2.6))
def shotEF(t, fi):
    if t < CRANE:
        x = -95 + 9.5 * (t - 75); zc = zbE(x) - 16.5
        cam = Cam(x, zc, 4.3, 8, 0, focus=16.5, aperture=1.0)
    else:
        u = (t - CRANE) / (110 - CRANE); x = -95 + 9.5 * 17.5 + 6 * (t - CRANE) * (1 - u * 0.5)
        h = 4.3 * (300 / 4.3) ** ease(u * 1.05); pit = lerp(8, 60, ease(u)); zc = zbE(x) - lerp(16.5, 160, ease(u))
        cam = Cam(x, zc, h, pit, 0, focus=math.hypot(h, zbE(x) - zc), aperture=lerp(1.0, 0.25, ease(u)))
    sd, i = sfi("EF", t, 75.0)
    ants = [a for a in ants_from(sd, i)]
    fog = 260 if t < CRANE else kf(t, [(CRANE, 260), (110, 2500)], "exp")
    img = render(cam, t, fi, mats_mix, PE, ants, sky=sky_grad((0.44, 0.47, 0.46), (0.62, 0.60, 0.52)), fogd=fog, bok=0.7)
    return grade(img, sat=0.72, contrast=1.12, gain=(0.95, 0.95, 0.97))

PG = gen_props(11, (-120, 120), (-15, 260), npeb=480, nbl=90, nroot=3, pr=(0.2, 2.0), rz=(40, 120), clear=lambda x, z: z < 40 and z > -14 and abs(x) < 50) + \
     gen_props(12, (-40, 40), (-12, 30), npeb=200, pr=(0.15, 0.8), clear=lambda x, z: abs(x) < 3.5 and abs(z) < 2.5)
LITTER = [(x, z, h) for x, z, h in np.random.default_rng(13).uniform([-30, -3, 0], [30, 35, 6.28], (16, 3)) if not (abs(x) < 4 and abs(z) < 4)]
def zbG(x): return 4 * math.sin(x / 300.0) + 2 * math.sin(x / 70.0)
def shotGK(t, fi):
    u = np.clip((t - 115.6) / (122.5 - 115.6), 0, 1)
    if t < 115.6: h, pit, z = 2.5, 6.0, -10.8 + 0.08 * (t - 110)
    else:
        h = 2.5 * (2400 / 2.5) ** ease(u); pit = lerp(6, 88.5, ease(min(1, u * 1.5))); z = lerp(-10.36, -40, ease(u))
    if t > 122.5: h = 2400 * (1 + 0.025 * (t - 122.5))
    cam = Cam(0.2, z, h, pit, 0, focus=math.hypot(h, z) if t > 115.6 else 11.0, aperture=1.0 if t < 115.6 else lerp(1.0, 0.15, ease(u)))
    sd, i = sfi("G", t, 110.0)
    tw = 0.12 * math.sin(t * 1.3) * (math.sin(t * 0.7) > 0.6)
    hero = (0.0, 0.0, 2.3, 0.4, 2.4 + tw, 5.6, 0.15, 0, 0.92, 0.55)
    dead = [(x, z, h_, 0.0, 0.0, 0.0, 0.3, 3, 0.85) for x, z, h_ in LITTER]
    pas = []
    for x0, x1, z_, a0, a1 in ((-14, 14, 2.6, 110.0, 119.0), (13, -13, -2.7, 111.5, 121.0)):
        if a0 <= t <= a1:
            x_ = lerp(x0, x1, (t - a0) / (a1 - a0)); hd_ = 0.0 if x1 > x0 else math.pi
            pas.append((x_, z_ + 0.2 * math.sin(t * 0.8), hd_ + 0.04 * math.sin(t), abs(x_ - x0) / 0.55 % 1, t * 1.5, t * 1.7, 0.0, 0, 1.0))
    ants = ants_from(sd, i, keep=lambda x, z: not (abs(x) < 3.2 and abs(z) < 2.2)) + dead + [hero] + pas
    def mats(gx, gz):
        m = np.clip((np.abs(gz) - 60) / 140, 0, 1); v = 0.5 + 0.5 * np.sin(gx / 517.0 + 0.7) * np.sin(gz / 389.0 + 2.1)
        return [("sand", 1 - m), ("mud", m * v), ("soil", m * (1 - v))]
    def water(img, GX, GZ, dep):
        shore = 520 + 110 * np.sin(GX / 420.0) + 45 * np.sin(GX / 130.0 + 1)
        wet = np.clip(1 - (shore - GZ) / 140, 0, 1)[..., None]
        img = img * (1 - 0.35 * wet)
        wm = np.clip((GZ - shore) / 12, 0, 1)[..., None]
        wcol = np.array([0.09, 0.13, 0.16], np.float32) + 0.04 * np.exp(-np.clip(GZ - shore, 0, None) / 300)[..., None]
        return img * (1 - wm) + wcol * wm
    def border(img, cam):
        a = np.clip((h - 120) / 300, 0, 1)
        if a <= 0: return
        xs = np.linspace(-6000, 6000, 900); P, zz = cam.proj(np.stack([xs, np.zeros_like(xs), [zbG(x) for x in xs]], -1))
        line(img, P, (0.12, 0.08, 0.05), max(1.0, cam.f * 5 / zz.mean()), 0.8 * a)
        rr = np.random.default_rng(1)
        for k in range(0, 900, 2):
            o = rr.normal(0, 1.5)
            if 0 < P[k][0] < W: disk(img, P[k] + np.array([rr.uniform(-2, 2), o]), max(0.8, cam.f * 1.4 / zz[k]), (0.10, 0.07, 0.05))
    def tufts(img, cam):
        a = np.clip((h - 150) / 400, 0, 1)
        if a <= 0: return
        rr = np.random.default_rng(31); P = rr.uniform([-5000, -3000], [5000, 470], (2600, 2)); R = rr.uniform(2.5, 11, 2600) * (1 + 2 * rr.random(2600) ** 8)
        s_, zz = cam.proj(np.stack([P[:, 0], np.zeros(2600), P[:, 1]], -1))
        for (x, y), r, z_ in zip(s_, R, zz):
            if -50 < x < W + 50 and -50 < y < H + 50: disk(img, (x, y), cam.f * r / z_, (0.20, 0.22, 0.15))
    def pg(img, cam): tufts(img, cam); border(img, cam)
    img = render(cam, t, fi, mats, PG if h < 200 else [], [] if h > 400 else ants, sky=sky_grad((0.55, 0.60, 0.64), (0.70, 0.70, 0.66)), fogd=kf(t, [(110, 300), (115.6, 300), (122.5, 9000)], "exp"),
                 water=water, post_ground=pg)
    img = grade(img, sat=0.55, contrast=1.06, gain=(0.92, 0.95, 1.0), lift=(0.02, 0.025, 0.03))
    if t > 122.3: img *= 1 - 0.55 * ease((t - 122.3) / 1.2)
    return img

PH = gen_props(14, (-150, 150), (-25, 400), npeb=520, nbl=170, nroot=5, pr=(0.2, 2.2), bh=(30, 120), rz=(25, 80),
               clear=lambda x, z: z < 20 and z > -14 and abs(x) < 70) + gen_props(15, (-50, 50), (-12, 20), npeb=180, pr=(0.15, 0.8), clear=lambda x, z: abs(z) < 2.2)
def shotHs(t, fi):
    cam = Cam(0.0, kf(t, [(134, -14.0), (147.5, -10.6)]), 2.5, 5.0, 0, focus=kf(t, [(134, 14.0), (147.5, 10.6)]), aperture=1.0)
    xa = kf(t, [(134, -13.0), (147.4, -1.95)], "lin"); xb = kf(t, [(134, 12.5), (147.4, 1.95)], "lin")
    def k_(x0, x, hd, s):
        return (x, 0.15 * s, hd + 0.05 * math.sin(t * 1.3 * s), abs(x - x0) / 0.55 % 1, t * 3.5 * s + (2.2 if t > 145.5 else 0), t * 3.1 * s, 0.0, 0, 1.0)
    ants = [k_(-13, xa, 0.0, 1.0), k_(12.5, xb, math.pi, 1.1)]
    sky = sky_grad((0.32, 0.30, 0.36), (0.86, 0.62, 0.40))
    img = render(cam, t, fi, mats_mix, PH, ants, sky=sky, fogd=200, light=0.85, objlight=0.85, shadow_k=0.65, bok=0.35)
    # low sun glow
    yy, xx = np.mgrid[0:H:4, 0:W:4]; gl = np.exp(-(((xx - 520) / 700.0) ** 2 + ((yy - 300) / 380.0) ** 2))
    img += cv2.resize(gl.astype(np.float32), (W, H))[..., None] * np.array([0.30, 0.18, 0.07], np.float32)
    return grade(img, sat=0.78, contrast=1.08, gain=(1.02, 0.88, 0.74), warm=0.015)

SHOTF = {"A": shotA, "B": shotB, "M1": shotM1, "C": shotC, "M2": shotM2, "DS": shotDS, "D": shotD, "E": shotEF, "F": shotEF,
         "G": shotGK, "K": shotGK, "Hs": shotHs, "TITLE": lambda t, fi: np.zeros((H, W, 3), np.float32)}
def frame(fi):
    t = fi / FPS
    n, a, b = shot_at(t)
    img = SHOTF[n](t, fi)
    xf = {"B": 1.0, "M1": 1.0, "C": 0.8, "M2": 0.6, "DS": 1.0, "Hs": 1.2}.get(n, 0)
    if xf and t < a + xf:
        prev = [s for s in SHOTS if s[2] == a][0][0]
        img2 = SHOTF[prev](t, fi); u = ease((t - a) / xf); img = img2 * (1 - u) + img * u
    img = overlay_text(img, t)
    img = grain(img, fi, 0.016)
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prep":
        for n in sys.argv[2:]: S(n); print("sim", n, "ok")
    elif cmd == "test":
        for ts in sys.argv[2:]:
            im = frame(int(round(float(ts) * FPS))); cv2.imwrite(f"/tmp/bd_{ts}.jpg", im[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 88])
    elif cmd == "sheet":
        ims = [cv2.resize(frame(int(round(float(ts) * FPS))), (640, 360)) for ts in sys.argv[2:]]
        while len(ims) % 3: ims.append(np.zeros_like(ims[0]))
        rows = [np.hstack(ims[i:i + 3]) for i in range(0, len(ims), 3)]
        cv2.imwrite("/tmp/bd_sheet.jpg", np.vstack(rows)[..., ::-1])
    elif cmd == "render":
        f0, f1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        import subprocess
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for fi in range(f0, f1): p.stdin.write(frame(fi).tobytes())
        p.stdin.close(); p.wait()
