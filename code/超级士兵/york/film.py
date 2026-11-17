# 《超级士兵 No.02 不想打仗的农村神枪手》 — dark, enemy-POV, fog + rim light, no outlines.
# python3 film.py test t1 t2 ...   -> /tmp/yk_test_<t>.png ; python3 film.py sheet out.png t1 t2 ... ; python3 film.py render f0 f1 out.mp4
import sys, subprocess
from chars import *
from chars2 import *
from cues import *

NOSUB = {"hook", "big1", "big2"}
def popk(t, t0, preset="snappy"): return max(0.0, E.spring_at(t, t0, 0, 1, preset)) if t >= t0 else 0.0
def ap(t, t0, d=0.15): return cl((t - t0) / d)
def slam(d, t, t0, s, x, y, size, col, a=1.0):
    if t < t0: return
    d.text(x, y, s, int(size * E.slam(t, t0, 0.28, 1.6)), A(col, ap(t, t0, 0.08) * a), k=1)
def tag(d, x, y, s, col, a=1.0, size=40, tc=(20, 16, 12)):
    if a <= 0.01: return
    w = d.tlen(s, size) + 44
    d.rect(x - w / 2, y - size * 0.8, x + w / 2, y + size * 0.8, fill=A(col, 0.95 * a), r=size * 0.6)
    d.text(x, y, s, size, A(tc, a))
def tracer(d, x0, y0, x1, y1, u, col=AMBER_L, a=1.0, L=0.12, w=5):
    if not (0 <= u <= 1 + L): return
    ua, ub = cl(u - L), cl(u)
    d.line([(lerp(x0, x1, ua), lerp(y0, y1, ua)), (lerp(x0, x1, ub), lerp(y0, y1, ub))], A(col, a), w)
def deadtree(d, x, y, h, col, seed=0, a=1.0):
    r = random.Random(seed)
    d.poly([(x - h * 0.03, y), (x - h * 0.012, y - h), (x + h * 0.012, y - h), (x + h * 0.03, y)], A(col, a))
    for i in range(5):
        yy = y - h * r.uniform(0.35, 0.9); s_ = r.choice((-1, 1)); L = h * r.uniform(0.15, 0.3)
        d.line([(x, yy), (x + s_ * L, yy - L * r.uniform(0.4, 0.9))], A(col, a), max(2, h * 0.012))
def ridge(d, y, amp, col, seed, a=1.0, freq=1.0):
    r = random.Random(seed); ph = [r.uniform(0, 6.28) for _ in range(3)]
    pts = [(x, y + amp * (0.5 * math.sin(x * 0.006 * freq + ph[0]) + 0.3 * math.sin(x * 0.017 * freq + ph[1]) + 0.2 * math.sin(x * 0.043 * freq + ph[2]))) for x in range(-40, 1130, 20)]
    d.poly(pts + [(1130, 2000), (-40, 2000)], A(col, a))
def sandbags(d, y, col, rim, seed=3, a=1.0, rows=3): sandbags2(d, y, col, rim, seed, a, rows)

# ================================================================ scenes
def s_hook(t, img, d):
    img.paste(vgrad((8, 12, 18), (16, 20, 20), mid=(0.55, (40, 50, 50))))
    soft_shape(img, lambda g: g.ell(540, 1010, 520, 150, fill=A((255, 150, 60), 0.55)), blur=90)   # dawn glow behind the lone man
    ridge(d, 930, 40, (24, 32, 34), 1); fog(img, t, (90, 110, 112), 0.35, 10, 820, 1100, 160, seed=2)
    for i, (x, hh) in enumerate(((120, 300), (300, 220), (820, 260), (980, 340))): deadtree(d, x, 1000, hh, (26, 32, 32), i)
    ridge(d, 1040, 26, (30, 38, 38), 4)
    # lone figure (York) far away, backlit — steady, slowly walking closer
    ky = 1050; ks = 128 * (1 + 0.12 * eio(pr(t, 0, 3)))
    body = spline([(-0.22, -1.1), (0.22, -1.1), (0.3, -0.2), (0.18, 0.05), (-0.18, 0.05), (-0.3, -0.2)], n=4)
    rimpoly(d, xf(body, 540, ky, ks), (20, 20, 16), AMBER_L, 0, 2)
    d.circ(540, ky - ks * 1.32, ks * 0.2, fill=A(AMBER_L, 1)); d.circ(540, ky - ks * 1.3, ks * 0.18, fill=A((24, 22, 18), 1))
    d.ell(540, ky - ks * 1.43, ks * 0.44, ks * 0.08, fill=A(AMBER_L, 1)); d.ell(540, ky - ks * 1.41, ks * 0.42, ks * 0.07, fill=A((30, 30, 22), 1))  # Brodie brim
    d.line([(540 + ks * 0.15, ky - ks * 0.5), (540 + ks * 0.45, ky - ks * 1.7)], A(AMBER_L, 1), ks * 0.09); d.line([(540 + ks * 0.17, ky - ks * 0.48), (540 + ks * 0.47, ky - ks * 1.68)], A((26, 24, 18), 1), ks * 0.06)
    fog(img, t + 3, (110, 130, 130), 0.42, 16, 980, 1260, 200, seed=5)
    # enemy MG nest foreground (we stand behind it)
    ridge(d, 1330, 30, (18, 22, 22), 7)
    # tracers from the MG into the valley (they miss: fan around him)
    for j in range(14):
        t0 = j * 0.21 - 0.05; u = (t - t0) / 0.5
        tx = 540 + (-1) ** j * (120 + 90 * hsh(j, 3)) + 30 * math.sin(j); ty = 930 + 90 * hsh(j, 4)
        tracer(d, 760, 1470, tx, ty, u, (255, 200, 120), 0.9, 0.18, 5)
    sandbags(d, 1560, (40, 40, 34), (180, 120, 70), 3)
    # MG barrel + flash (bottom right, pointing up-left into the valley)
    d.line([(1000, 1760), (770, 1475)], A((30, 32, 34), 1), 34); d.line([(990, 1748), (772, 1470)], A((120, 96, 70), 0.9), 6)
    fl = 1.0 if (t * 30) % 3 < 1.2 else 0.0
    if fl: glow(img, lambda g: g.circ(765, 1465, 60, fill=A((255, 190, 90), 1)), blur=40)
    german_back(d, 250, 1500, 150, t, rim=(200, 130, 70), lean=-0.08, seed=1)
    german_back(d, 880, 1600, 175, t, rim=(200, 130, 70), lean=0.05, seed=2)
    fog(img, t * 0.6, (60, 70, 70), 0.25, 8, 1500, 1920, 200, seed=8)
    # hook keyword (0 s visible): 1人 VS 一整片阵地
    k = popk(t, -0.12, "bouncy")
    if k > 0:
        kk = 0.7 + 0.3 * min(k, 1.1)
        d.text(470, 420, "1个人", int(150 * kk), A(AMBER, ap(t, -0.12, 0.12)))
        d.text(760, 432, "VS", int(90 * kk), A(WHITE, ap(t, -0.05, 0.12)))
    k2 = popk(t, 0.25, "bouncy")
    if k2 > 0: d.text(540, 590, "一整片阵地", int(120 * (0.7 + 0.3 * min(k2, 1.1))), A(WHITE, ap(t, 0.25, 0.12)))

def odo(t, t0, dur, n):
    u = pr(t, t0, t0 + dur); return int(round(n * (1 - (1 - u) ** 2.2)))
def s_big1(t, img, d):
    img.paste(vgrad((12, 22, 30), (14, 16, 16), mid=(0.62, (190, 110, 50))))
    soft_shape(img, lambda g: g.ell(540, 1180, 700, 200, fill=A((255, 180, 90), 0.7)), blur=80)
    ridge(d, 1190, 30, (36, 40, 38), 11, freq=0.6)
    fog(img, t, (140, 120, 100), 0.35, 14, 1050, 1300, 160, seed=3)
    # back row (small, in haze) then front row (big) — hands up lagged one by one
    rows = [(1215, 70, 9, 0.55, 3.15), (1330, 105, 7, 0.8, 3.25), (1500, 150, 5, 1.0, 3.4)]
    for ri, (yy, hh, n, al, ts) in enumerate(rows):
        for i in range(n):
            x = 540 + (i - (n - 1) / 2) * (900 / n) + (hsh(i, ri) - 0.5) * 30
            st = ts + 0.12 * ((i * 3 + ri) % n)
            german(d, x, yy, hh, t, hands=E.spring_at(t, st, 0, 1, "snappy") if t >= st else 0.0, face=0.25, rim=(255, 176, 90), rdx=1 if x > 540 else -1,
                   fear=0.7, seed=i + ri * 10, a=al)
        if ri == 1: fog(img, t + 1, (150, 120, 96), 0.3, 18, 1250, 1450, 140, seed=4)
    fog(img, t * 0.7, (70, 60, 52), 0.35, 10, 1600, 1920, 220, seed=6)
    n = odo(t, BIG1, 0.9, 132)
    slam(d, t, BIG1, str(n), 540, 420, 270, AMBER)
    if t > BIG1 + 0.5: d.text(540, 615, "全部举手投降！", int(100 * E.slam(t, BIG1 + 0.5, 0.28, 1.5)), A(WHITE, ap(t, BIG1 + 0.5, 0.1)))

def s_q(t, img, d):
    t0 = T["q"]
    img.paste(vgrad((8, 12, 16), (12, 14, 14), mid=(0.5, (30, 34, 34))))
    soft_shape(img, lambda g: g.ell(220, 900, 420, 700, fill=A((255, 150, 60), 0.35)), blur=120)   # fire light from the left
    fog(img, t, (70, 84, 86), 0.4, 10, 300, 900, 300, seed=9)
    z = 1 + 0.05 * eio(pr(t, t0 - 0.4, t0 + 2.5)); y = 900 - 30 * eio(pr(t, t0 - 0.4, t0 + 2.5))
    blink = (t0 + 1.1) < t < (t0 + 1.22)
    york_face(img, d, 540, y, 600 * z, t, key=AMBER, rim=COLD, squint=0.3, blink=blink)
    fog(img, t + 4, (60, 70, 70), 0.45, 14, 1350, 1920, 260, seed=10)   # fog only below the face

def s_who(t, img, d):
    t0 = T["who"]; shot = at("who", 3)
    img.paste(vgrad((40, 30, 52), (16, 14, 14), mid=(0.5, (196, 104, 56))))
    soft_shape(img, lambda g: g.ell(760, 930, 300, 160, fill=A((255, 200, 120), 0.8)), blur=60)   # setting sun
    ridge(d, 900, 50, (90, 52, 50), 21, freq=0.5); ridge(d, 980, 40, (60, 36, 38), 22, freq=0.7)
    fog(img, t, (200, 120, 90), 0.25, 8, 850, 1050, 120, seed=12)
    ridge(d, 1120, 30, (34, 24, 22), 23, freq=0.8)
    for i, (x, w_) in enumerate(((60, 50), (190, 30), (1000, 44))):
        d.poly([(x - w_, 1400), (x - w_ * 0.6, 200), (x + w_ * 0.6, 200), (x + w_, 1400)], A((26, 18, 16), 1))
        d.poly([(x + w_ * 0.55, 1400), (x + w_ * 0.35, 200), (x + w_ * 0.6, 200), (x + w_, 1400)], A((170, 90, 54), 0.55))
    # target board on a far tree, right
    tx, ty = 870, 900
    d.rect(tx - 14, 800, tx + 14, 1150, fill=A((40, 26, 20), 1))
    for r, c in ((46, (210, 196, 170)), (34, (150, 50, 40)), (22, (210, 196, 170)), (11, (150, 50, 40))): d.circ(tx, ty, r, fill=A(c, 1))
    if t >= shot:
        d.circ(tx + 2, ty - 1, 6, fill=A((20, 14, 12), 1))
        zz = pr(t, shot + 0.05, shot + 0.4)
        if zz < 1: glow(img, lambda g: [g.circ(tx, ty, 30 + 80 * zz, outline=A(AMBER_L, 1 - zz), w=8)], blur=10)
    px = 330 + 10 * eio(pr(t, t0 - 0.3, t0 + 3)); py = 1000; ph = 150
    york_profile(d, px, py, ph, t, key=(255, 170, 90), hat=True)
    if shot <= t < shot + 0.12: glow(img, lambda g: g.circ(px + 3.45 * ph, py - 0.12 * ph, 50, fill=A(AMBER_L, 1)), blur=30)
    fog(img, t * 0.5, (50, 34, 30), 0.3, 6, 1400, 1920, 200, seed=13)
    k = popk(t, t0 + 0.2)
    if k > 0: tag(d, 540, 470 + (1 - min(k, 1)) * 20, "阿尔文·约克", AMBER, ap(t, t0 + 0.2), int(58 * (0.7 + 0.3 * min(k, 1))))
    if t > t0 + 0.6: d.text(540, 560, "美国田纳西州 · 山村", 40, A(WHITE, 0.9 * ap(t, t0 + 0.6, 0.3)))
    if t > shot + 0.15: d.text(tx, ty - 110, "正中！", int(64 * E.slam(t, shot + 0.15, 0.25, 1.5)), A(AMBER_L, ap(t, shot + 0.15, 0.08)))

def s_nowar(t, img, d):
    t0 = T["nowar"]; st = at("nowar", 4)
    img.paste(vgrad((20, 18, 16), (10, 10, 10)))
    soft_shape(img, lambda g: g.ell(540, 800, 520, 480, fill=A((255, 190, 110), 0.45)), blur=100)
    d.rect(170, 420, 910, 1180, fill=A((214, 200, 168), 1), r=8); d.rect(170, 420, 910, 470, fill=A((190, 172, 138), 1), r=8)
    d.text(540, 560, "申请书", 64, A((60, 44, 30), 1))
    d.text(540, 700, "我不想打仗，", 56, A((70, 50, 34), ap(t, t0 + 0.2, 0.4)))
    d.text(540, 790, "请让我不上战场", 56, A((70, 50, 34), ap(t, t0 + 0.6, 0.4)))
    d.text(700, 930, "—— 约克", 44, A((70, 50, 34), ap(t, t0 + 1.0, 0.4)))
    u = eio(pr(t, t0 + 1.2, t0 + 1.8))
    if u > 0: d.line([(600, 975), (600 + 220 * u, 968)], A((90, 60, 40), 0.9), 5)
    z = 1 + 0.05 * eio(pr(t, t0, nxt("nowar")))   # slow push on the letter (no stamp: we only say he applied)

def s_pinned(t, img, d):
    t0 = T["pinned"]
    img.paste(vgrad((10, 14, 18), (14, 16, 14), mid=(0.45, (36, 46, 46))))
    ridge(d, 760, 160, (22, 28, 30), 31, freq=0.4)          # the hill with the guns (top right)
    for i, (x, y) in enumerate(((760, 640), (880, 600), (980, 660), (650, 700))):
        on = ((t * 30 + i * 2) % 5) < 1.5 and t > t0 + 0.15 * i
        if on: glow(img, lambda g: g.circ(x, y, 26, fill=A((255, 200, 110), 1)), blur=26)
    fog(img, t, (90, 110, 110), 0.35, 12, 650, 950, 200, seed=14)
    for j in range(24):  # tracers sweeping overhead, right->left
        t1 = t0 - 0.3 + j * 0.19; u = (t - t1) / 0.55
        sx = [760, 880, 980, 650][j % 4]; sy = [640, 600, 660, 700][j % 4]
        tracer(d, sx, sy, -60, 980 + 160 * hsh(j, 9), u, (255, 196, 120), 0.9, 0.2, 8)
    ridge(d, 1240, 24, (26, 30, 26), 33)
    # squad ducking behind a log
    for i, (x, h_, ph) in enumerate(((250, 190, 0.0), (560, 215, 0.4), (860, 185, 0.9))):
        brodie_back2(d, x, 1110, h_, t, rim=(190, 160, 110), seed=i, duck=0.3 + 0.3 * math.sin(t * 2.5 + ph) ** 2)
    lg = spline([(-40, 1250), (300, 1225), (700, 1240), (1120, 1222), (1120, 1450), (-40, 1460)], n=5)
    rimpoly(d, lg, (44, 34, 26), (150, 120, 90), 0, 6)
    fog(img, t * 0.6, (50, 60, 58), 0.3, 8, 1400, 1920, 220, seed=15)
    k = popk(t, t0 + 0.1)
    if k > 0: tag(d, 540, 400, "1918.10.8 · 法国 阿尔贡森林", (200, 196, 180), ap(t, t0 + 0.1), int(44 * (0.7 + 0.3 * min(k, 1))))

def overhead_tracers(d, t, t0, n, y0, y1, x_from=1140, x_to=-60, seed=60, a=0.85, w=7, every=0.23):
    for j in range(n):
        t1 = t0 - 0.4 + j * every; u = (t - t1) / 0.5; yy = lerp(y0, y1, hsh(j, seed))
        tracer(d, x_from, yy - 30, x_to, yy + 40, u, (255, 196, 120), a, 0.22, w)

def ground_scene(img, d, t, gy, seed=40, glowx=540):
    """Ground-level low camera: horizon just above the ground line, dawn glow, dirt plane, stones."""
    img.paste(vgrad((10, 14, 18), (18, 18, 14), mid=(0.5, (58, 54, 44))))
    soft_shape(img, lambda g: g.ell(glowx, gy - 120, 640, 220, fill=A((255, 160, 70), 0.5)), blur=100)
    ridge(d, gy - 110, 22, (30, 34, 32), seed + 1)
    fog(img, t, (100, 110, 106), 0.32, 12, gy - 260, gy - 40, 200, seed=16)
    d.poly([(-20, gy - 30), (1100, gy - 40), (1100, 1920), (-20, 1920)], A((40, 36, 28), 1))
    soft_shape(img, lambda g: g.ell(glowx, gy - 34, 620, 26, fill=A((255, 176, 90), 0.45)), blur=24)   # light skimming the ground
    for i in range(16):
        x = (i * 83 + 200 * hsh(i, seed)) % 1120 - 20; y = gy + 10 + 600 * hsh(i, seed + 1) ** 2
        r = 3 + 9 * hsh(i, seed + 2) * (1 + (y - gy) / 300)
        d.ell(x, y, r * 1.6, r * 0.7, fill=A(mix((60, 54, 42), (110, 96, 72), hsh(i, seed + 3)), 1))

def grass_front(d, t, y_base=1920, hmin=120, hmax=280, n=40, seed=5, skip=None):
    for i in range(n):
        x = (i * 1120 / n + 13 * hsh(i, 2)) % 1120 - 20
        if skip and skip[0] < x < skip[1]: continue
        hh = hmin + (hmax - hmin) * hsh(i, seed); sway = math.sin(t * 1.5 + i) * 10
        col = mix((26, 30, 22), (70, 64, 40), hsh(i, 7))
        d.poly([(x - 9, y_base), (x + sway, y_base - hh), (x + 9, y_base)], A(col, 1))

def s_big2(t, img, d):
    """LOW camera at the dirt: York drops flat (side view) — body lying along the ground; bullets pass over him."""
    t0 = T["big2"]; gy = 1180
    ground_scene(img, d, t, gy)
    overhead_tracers(d, t, t0, 14, 780, 990)
    u = pr(t, t0, t0 + 0.2); rot = -0.42 * (1 - u * u)
    dust = (1 - pr(t, t0 + 0.2, t0 + 1.4)) if t >= t0 + 0.2 else 0.0
    h = 185; hx = 740 + 12 * eio(pr(t, t0 + 0.3, t0 + 2.7))
    york_prone_side(img, d, hx, gy - 0.62 * h, h, t, rot=rot, dust=dust)
    grass_front(d, t, 1920, 260, 560, 34, skip=(560, 1000))
    fog(img, t * 0.6, (60, 64, 58), 0.3, 8, 1500, 1920, 200, seed=17)
    if t > t0 + 0.05: d.text(540, 300, "据他回忆，他先——", 54, A(WHITE, ap(t, t0 + 0.05, 0.15)))
    slam(d, t, t0 + 0.12, "趴下！", 540, 470, 230, AMBER)
    if t > t0 + 0.6:
        a_ = ap(t, t0 + 0.6, 0.25); d.text(300, gy + 150, "整个人贴在地上", 46, A(AMBER_L, a_))
        d.line([(300, gy + 115), (330, gy + 20)], A(AMBER_L, 0.7 * a_), 4)

def panel(img, x0, y0, x1, y1, fn, r=0):
    lay = Image.new("RGB", (W, H), (10, 10, 10)); fn(lay, D(lay))
    box = (int(P(x0)), int(P(y0)), int(P(x1)), int(P(y1)))
    if r:
        m = Image.new("L", (box[2] - box[0], box[3] - box[1]), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, m.width - 1, m.height - 1), radius=int(P(r)), fill=255)
        img.paste(lay.crop(box), box[:2], m)
    else: img.paste(lay.crop(box), box[:2])

def aimtrail(d, t, cx, cy, amp, col, a=1.0):
    pts = []
    for k in range(18):
        tt = t - k * 0.035
        pts.append((cx + amp * (math.sin(tt * 5.3) + 0.6 * math.sin(tt * 11.7 + 1)), cy + amp * (math.cos(tt * 4.1) + 0.5 * math.sin(tt * 9.3))))
    d.line(pts, A(col, 0.5 * a), 4)
    d.circ(pts[0][0], pts[0][1], 12, fill=A(col, a))
    d.circ(cx, cy, 34, outline=A(col, 0.6 * a), w=3)

def s_why(t, img, d):
    """Side-by-side: standing = big target & shaky; prone = small target & steady."""
    t0 = T["why"]; b2 = at("why", 4)
    img.paste(vgrad((10, 12, 16), (12, 12, 12)))
    gy = 1180
    def left(L, dd):
        L.paste(vgrad((14, 18, 22), (22, 20, 18), mid=(0.55, (48, 46, 40))))
        dd.poly([(-20, gy), (1100, gy), (1100, 1920), (-20, 1920)], A((40, 36, 28), 1))
        york_stand_side(dd, 190, gy, 100, t, sway=0.05 * math.sin(t * 2.3))
        overhead_tracers(dd, t, t0, 16, 680, 1150, x_from=560, x_to=-40, seed=61, every=0.2)
        a_ = ap(t, t0 + 0.6, 0.3)
        dd.rect(80, gy - 560, 420, gy, fill=A((220, 80, 60), 0.16 * a_), r=10)
        dd.line([(445, gy - 560), (445, gy)], A((240, 120, 100), a_), 5)
        dd.text(470, gy - 600, "目标大", 46, A((250, 140, 120), a_), anchor="rm")
        if t > b2: aimtrail(dd, t, 300, 470, 34, (250, 140, 120), ap(t, b2, 0.3)); dd.text(300, 545, "晃", 52, A((250, 140, 120), ap(t, b2, 0.3)))
    def right(R, dd):
        R.paste(vgrad((14, 18, 22), (22, 20, 18), mid=(0.55, (58, 52, 40))))
        dd.poly([(-20, gy), (1100, gy), (1100, 1920), (-20, 1920)], A((40, 36, 28), 1))
        overhead_tracers(dd, t, t0 + 0.1, 16, 700, 1060, x_from=1120, x_to=520, seed=62, every=0.2)
        york_prone_side(R, dd, 820, gy - 0.62 * 80, 80, t)
        a_ = ap(t, t0 + 0.9, 0.3)
        dd.line([(1030, gy - 110), (1030, gy)], A(AMBER, a_), 5)
        dd.text(1040, gy - 150, "目标小", 46, A(AMBER, a_), anchor="rm")
        if t > b2: aimtrail(dd, t, 800, 470, 3, AMBER, ap(t, b2, 0.3)); dd.text(800, 545, "稳", 52, A(AMBER, ap(t, b2, 0.3)))
    panel(img, 30, 360, 532, 1240, left, 24); panel(img, 548, 360, 1050, 1240, right, 24)
    k = popk(t, t0 + 0.1)
    if k > 0:
        tag(d, 281, 300, "站着", (200, 196, 180), ap(t, t0 + 0.1), int(48 * (0.7 + 0.3 * min(k, 1))))
        tag(d, 799, 300, "趴着", AMBER, ap(t, t0 + 0.1), int(48 * (0.7 + 0.3 * min(k, 1))))

def s_shot(t, img, d):
    """York's eye through the iron sights: helmet peeks over the parapet -> PING (helmet knocked off, no gore)."""
    t0 = T["peek"]; hit = at("shot", 3)
    img.paste(vgrad((14, 20, 24), (18, 20, 18), mid=(0.5, (60, 70, 68))))
    ridge(d, 880, 20, (40, 46, 44), 51)
    fog(img, t, (110, 124, 120), 0.3, 10, 700, 1000, 200, seed=18)
    sandbags(d, 1040, (52, 56, 50), (120, 130, 120), 5, rows=2)
    # peeking helmet (rises slowly; after the ping it spins away and the head ducks)
    hx = 540; rise = eio(pr(t, t0 + 0.6, t0 + 2.4)) if t < hit else 1.0
    if t < hit:
        german(d, hx, 1110 - 80 * rise, 150, t, face=0.25, fear=0.2, seed=3)
    else:
        u = pr(t, hit, hit + 0.6)
        german(d, hx, 1030 + 160 * eio(pr(t, hit, hit + 0.35)), 150, t, face=0.2, fear=1.0, seed=3, a=1 - eio(pr(t, hit + 0.25, hit + 0.55)))
        hp = xf(STAHL, hx + 300 * u, 870 - 320 * u + 600 * u * u, 165, rot=u * 7)
        d.poly(hp, A(mix(HELM, COLD, 0.3), 1 - eio(pr(t, hit + 0.4, hit + 0.8))))
        if u < 0.3: glow(img, lambda g: g.circ(hx - 40, 890, 20 + 70 * u, fill=A((255, 230, 160), 1 - u / 0.3)), blur=14)
    sandbags(d, 1120, (60, 62, 56), (130, 140, 128), 6, rows=4)
    # iron sight: dark soft vignette ring + front post at centre (soft edge, not an outline)
    soft_shape(img, lambda g: [g.d.rectangle((0, 0, g.p(1080), g.p(1920)), fill=(6, 8, 8, 255)),
                               g.d.ellipse((g.p(140), g.p(560), g.p(940), g.p(1360)), fill=(0, 0, 0, 0))], blur=50, alpha=0.92)
    d.poly([(540 - 20, 1900), (540 - 16, 1085), (540 + 16, 1085), (540 + 20, 1900)], A((30, 32, 32), 1))
    d.rect(540 - 16, 1085, 540 - 9, 1900, fill=A((110, 110, 104), 1))
    if hit <= t < hit + 0.12: glow(img, lambda g: g.circ(540, 1085, 70, fill=A(AMBER_L, 1)), blur=30)
    if t > hit + 0.1: d.text(780, 820, "叮！", int(90 * E.slam(t, hit + 0.1, 0.25, 1.6)), A(AMBER_L, ap(t, hit + 0.1, 0.08) * (1 - pr(t, hit + 1.6, hit + 2.0))))

def s_fear(t, img, d):
    t0 = T["fear"]
    img.paste(vgrad((8, 12, 16), (10, 12, 12), mid=(0.45, (26, 34, 38))))
    # row of MG flashes in the distance going out one by one
    for i in range(6):
        x = 250 + i * 116; off = t0 + 0.4 + i * 0.5
        a_ = 1 - eio(pr(t, off, off + 0.35))
        if a_ > 0 and ((t * 30 + i) % 4) < 1.6: glow(img, lambda g: g.circ(x, 560, 26, fill=A((255, 196, 110), a_)), blur=24)
        d.circ(x, 560, 9, fill=A(mix((80, 70, 60), (255, 200, 120), a_ * 0.6), 1))
    fog(img, t, (70, 86, 90), 0.35, 10, 480, 760, 160, seed=19)
    sandbags(d, 1380, (34, 38, 36), (90, 110, 120), 9)
    for i, (x, y, h_) in enumerate(((290, 1250, 190), (790, 1270, 200), (540, 1180, 230))):
        german(d, x, y + 6 * math.sin(t * 9 + i), h_, t, face=0.55, fear=0.6 + 0.4 * pr(t, t0, t0 + 2.5), rim=COLD, rdx=-1, seed=i + 4)
    sandbags(d, 1530, (28, 30, 30), (80, 100, 110), 10)
    fog(img, t * 0.6, (40, 50, 54), 0.35, 8, 1550, 1920, 200, seed=20)

def s_hunt2(t, img, d):
    """Match cut as two stacked panels: boy hunter in the woods vs 1918 prone — same calm aim, same result."""
    t0 = T["hunt2"]; shots = [at("hunt2", 2.5), at("hunt2", 6.5)]
    img.paste(vgrad((10, 10, 14), (12, 12, 12)))
    def peek(tt, s0):   # target rises 0.9 s before the shot, knocked away after
        if tt < s0: return eio(pr(tt, s0 - 0.9, s0 - 0.25)), 0.0
        return 1.0, pr(tt, s0, s0 + 0.5)
    def which(tt):
        return 0 if tt < shots[0] + 0.9 else 1
    def top(L, dd):
        L.paste(vgrad((50, 34, 60), (20, 14, 14), mid=(0.3, (196, 110, 60))))
        soft_shape(L, lambda g: g.ell(820, 560, 260, 120, fill=A((255, 200, 120), 0.8)), blur=60)
        ridge(dd, 600, 40, (90, 52, 50), 21, freq=0.6); ridge(dd, 660, 26, (44, 28, 26), 23)
        for x, w_ in ((60, 34), (480, 22), (1010, 40)):
            dd.poly([(x - w_, 780), (x - w_ * 0.6, 280), (x + w_ * 0.6, 280), (x + w_, 780)], A((30, 20, 18), 1))
        i = which(t); s0 = shots[i]; rise, knock = peek(t, s0)
        tx = 880 - 50 * i; ty = 640 - 70 * rise
        if knock < 1:
            ang = knock * 2.5; dx = knock * 120
            pts = xf(ellpts(0, 0, 1, 1, n=24), tx + dx, ty - 120 * knock + 260 * knock * knock, 36, rot=ang)
            dd.poly(pts, A((214, 200, 172), 1 - knock)); dd.circ(tx + dx, ty - 120 * knock + 260 * knock * knock, 16, fill=A((160, 54, 42), 1 - knock))
        dd.poly(spline([(700, 700), (1060, 690), (1080, 760), (690, 770)], n=4), A((60, 38, 28), 1))   # log in front of the target
        dd.poly(spline([(700, 700), (1060, 690), (1062, 702), (702, 712)], n=4), A((150, 96, 60), 1))
        hunter_side(L, dd, 190, 610, 118, t, key=(255, 176, 100), flash=max(0, 1 - (t - s0) / 0.12) if t >= s0 else 0, recoil=max(0, 1 - (t - s0) / 0.2) if t >= s0 else 0)
        if s0 <= t < s0 + 0.2: tracer(dd, 190 + 2.95 * 118, 621, tx, ty, (t - s0) / 0.08, AMBER_L, 1, 0.4, 6)
    def bot(L, dd):
        L.paste(vgrad((12, 16, 20), (16, 18, 16), mid=(0.4, (40, 46, 44))))
        ridge(dd, 1020, 18, (32, 36, 34), 51)
        i = which(t); s0 = shots[i]; rise, knock = peek(t, s0)
        hx = 860 - 50 * i
        if knock < 1:
            german(dd, hx, 1150 - 70 * rise + 140 * eio(knock), 90, t, face=0.3, fear=0.3 + 0.7 * knock, seed=3, a=1 - eio(pr(knock, 0.3, 0.8)))
        sandbags2(dd, 1150, (52, 56, 50), (120, 130, 120), 8, rows=2, x0=640, x1=1120)
        dd.poly([(-20, 1215), (1100, 1210), (1100, 1300), (-20, 1300)], A((36, 34, 26), 1))
        york_prone_side(L, dd, 330, 1215 - 0.62 * 100, 100, t, flash=max(0, 1 - (t - s0) / 0.12) if t >= s0 else 0, recoil=max(0, 1 - (t - s0) / 0.2) if t >= s0 else 0)
        if knock > 0 and knock < 0.6: glow(L, lambda g: g.circ(hx, 1080, 20 + 60 * knock, fill=A((255, 230, 160), 1 - knock / 0.6)), blur=14)
        if s0 <= t < s0 + 0.2: tracer(dd, 330 + 2.8 * 100, 1215 - 0.62 * 100 + 9, hx, 1090, (t - s0) / 0.08, AMBER_L, 1, 0.4, 6)
    panel(img, 30, 300, 1050, 770, top, 24); panel(img, 30, 800, 1050, 1260, bot, 24)
    a_ = ap(t, t0 + 0.1, 0.25)
    tag(d, 230, 345, "小时候 · 打猎", (214, 196, 160), a_, 36); tag(d, 230, 845, "1918 · 战场", (200, 196, 180), a_, 36)
    for i, s0 in enumerate(shots):   # hit counter, shared by both panels
        if t > s0 + 0.1:
            k = popk(t, s0 + 0.1, "bouncy"); d.text(900 + i * 70, 345, "中", int(44 * (0.7 + 0.3 * min(k, 1.1))), A(AMBER, ap(t, s0 + 0.1, 0.1)))
            d.text(900 + i * 70, 845, "中", int(44 * (0.7 + 0.3 * min(k, 1.1))), A(AMBER, ap(t, s0 + 0.1, 0.1)))

def s_shout(t, img, d):
    """Front, ground level: York flat on the dirt, rifle at us — mouth wide: '投降吧！' rings roll out."""
    t0 = T["shout"]; sh = t0 + 1.8; fire = [t0 + 0.35, t0 + 1.05]
    img.paste(vgrad((10, 14, 18), (16, 18, 14), mid=(0.5, (60, 56, 46))))
    soft_shape(img, lambda g: g.ell(540, 760, 620, 260, fill=A((255, 160, 70), 0.5)), blur=100)
    ridge(d, 1000, 24, (30, 34, 32), 41); fog(img, t, (100, 110, 106), 0.35, 12, 850, 1100, 220, seed=16)
    d.poly([(-20, 1130), (1100, 1110), (1100, 1920), (-20, 1920)], A((40, 36, 28), 1))
    soft_shape(img, lambda g: g.ell(540, 1130, 600, 40, fill=A((255, 170, 80), 0.35)), blur=30)
    fl = max([max(0, 1 - (t - f) / 0.12) for f in fire if t >= f] + [0])
    h = 400; cx, cy = 540, 1000
    york_prone(img, d, cx, cy, h, t, key=AMBER, rim=COLD, flash=fl)
    k = eio(pr(t, sh - 0.1, sh + 0.08)) * (1 - 0.3 * eio(pr(t, sh + 0.9, sh + 1.3)))
    mouth_open(d, cx + 0.07 * h, cy, h, k)
    for i in range(3):   # sound rings
        u = pr(t, sh + i * 0.18, sh + i * 0.18 + 1.0)
        if 0 < u < 1: d.circ(cx + 0.08 * h, cy + 0.33 * h, 60 + 520 * u, outline=A(AMBER_L, 0.5 * (1 - u)), w=6)
    grass_front(d, t, 1920, 120, 280, 46)
    german_back(d, 140, 1720, 140, t + 3 * math.sin(t * 20) * pr(t, sh, sh + 0.3), rim=(200, 130, 70), lean=-0.1, seed=4)
    german_back(d, 950, 1760, 160, t, rim=(200, 130, 70), lean=0.08, seed=5)
    fog(img, t * 0.6, (60, 64, 58), 0.3, 8, 1450, 1920, 200, seed=17)
    if t > sh:   # speech bubble
        kk = E.slam(t, sh, 0.25, 1.5); a_ = ap(t, sh, 0.08); bw, bh = 560 * kk, 170 * kk
        d.rect(540 - bw / 2, 470 - bh / 2, 540 + bw / 2, 470 + bh / 2, fill=A(AMBER, 0.95 * a_), r=50)
        d.poly([(600, 470 + bh / 2 - 4), (680, 470 + bh / 2 - 4), (640, 470 + bh / 2 + 70)], A(AMBER, 0.95 * a_))
        d.text(540, 466, "投降吧！", int(104 * kk), A((24, 16, 10), a_))

def s_give(t, img, d):
    """German officer, lit by the dawn, raises his hands — chest-up, face clear."""
    t0 = T["give"]; up = at("give", 2)
    img.paste(vgrad((20, 22, 28), (14, 14, 14), mid=(0.55, (120, 84, 56))))
    soft_shape(img, lambda g: g.ell(540, 900, 560, 380, fill=A((255, 176, 100), 0.45)), blur=110)
    for i, x in enumerate((90, 230, 880, 1000)): deadtree(d, x, 1100, 360 + 80 * hsh(i, 5), (40, 36, 36), i + 10)
    fog(img, t, (130, 120, 108), 0.35, 10, 700, 1150, 220, seed=21)
    for i, x in enumerate((180, 330, 760, 910)):   # others in the haze, already giving up
        german(d, x, 1000 + 20 * (i % 2), 70, t, hands=1.0, face=0.2, rim=(220, 160, 100), fear=0.6, seed=20 + i, a=0.55)
    fog(img, t + 2, (120, 110, 100), 0.3, 14, 1000, 1250, 160, seed=22)
    hk = E.spring_at(t, up, 0, 1, "snappy") if t >= up else 0.0
    officer(d, 540, 900 - 6 * eio(pr(t, t0, t0 + 3.5)), 250, t, hands=hk, face=0.95, rim=(255, 180, 110), rdx=-1, fear=0.45, talk=0.6 * max(0, math.sin((t - t0) * 9)) * (1 - pr(t, up, up + 0.2)))
    fog(img, t * 0.6, (50, 46, 44), 0.35, 8, 1500, 1920, 220, seed=23)
    k = popk(t, t0 + 0.15)
    if k > 0: tag(d, 540, 400, "德军军官", (220, 210, 190), ap(t, t0 + 0.15), int(48 * (0.7 + 0.3 * min(k, 1))))

def s_march(t, img, d):
    """Tracking shot: a long column walking right, 8 Americans escorting; odometer counts the prisoners."""
    t0 = T["march"]; gy = 1220
    img.paste(vgrad((26, 30, 36), (20, 18, 16), mid=(0.5, (150, 110, 70))))
    soft_shape(img, lambda g: g.ell(820, 860, 420, 160, fill=A((255, 196, 120), 0.55)), blur=90)
    off = (t - t0) * 70
    for i in range(10):   # far trees scroll left (parallax)
        x = (i * 140 - off * 0.4) % 1400 - 160; deadtree(d, x, 980, 260 + 100 * hsh(i, 31), (60, 52, 50), i + 30, a=0.8)
    ridge(d, 960, 20, (70, 56, 46), 61)
    fog(img, t, (150, 130, 110), 0.3, 10, 860, 1060, 160, seed=24)
    d.poly([(-20, 860), (1100, 850), (1100, 1920), (-20, 1920)], A((52, 44, 34), 1))
    for i in range(16):   # ground clods scroll at full speed
        x = (i * 90 - off) % 1440 - 180; y = 900 + 360 * hsh(i, 33)
        d.ell(x, y, 22 + 20 * hsh(i, 34), 7, fill=A((76, 64, 48), 1))
    drift = (t - t0) * 6
    for i in range(17):   # back row: prisoners
        walker(d, -60 + i * 72 + drift, 970, 16, t, i * 1.7, "ger", key=(255, 190, 120), a=0.85)
    for i in range(12):   # mid row
        walker(d, -40 + i * 100 + drift, 1090, 22, t, i * 2.3 + 1, "ger", key=(255, 190, 120))
    us = [40, 190, 340, 490, 640, 900, 1040]
    for i, x in enumerate(us):   # front: 7 comrades
        walker(d, x + drift, 1225, 27, t, i * 1.3 + 0.5, "us", key=(255, 190, 120))
    walker(d, 770 + drift, 1245, 33, t, 0.2, "us", key=AMBER)   # York, nearest
    if t > t0 + 0.6: tag(d, 770 + drift + 6, 1245 - 33 * 7.0, "约克", AMBER, ap(t, t0 + 0.6, 0.25), 34)
    fog(img, t * 0.6, (60, 50, 44), 0.3, 8, 1550, 1920, 200, seed=25)
    n = odo(t, t0 + 0.3, 3.4, 132)
    d.text(540, 420, str(n), 210, A(AMBER, ap(t, t0 + 0.3, 0.15)))
    d.text(540, 575, "名俘虏", 64, A(WHITE, ap(t, t0 + 0.5, 0.2)))
    if t > t0 + 1.2: tag(d, 540, 680, "约克 + 7 个战友", (214, 204, 180), ap(t, t0 + 1.2, 0.25), 40)

def medal_icon(d, x, y, s, a=1.0):
    d.rect(x - 0.45 * s, y - 1.1 * s, x + 0.45 * s, y - 0.45 * s, fill=A((70, 110, 170), a), r=0.06 * s)
    for i in range(13):
        d.circ(x - 0.33 * s + (i % 5) * 0.165 * s, y - 0.98 * s + (i // 5) * 0.18 * s, 0.035 * s, fill=A((236, 236, 230), a))
    d.line([(x, y - 0.45 * s), (x, y - 0.25 * s)], A((200, 160, 70), a), 0.06 * s)
    d.circ(x, y + 0.25 * s, 0.52 * s, fill=A((70, 110, 60), 0.9 * a))
    st = [(math.cos(-math.pi / 2 + math.pi + k * math.pi / 5) * (0.5 if k % 2 == 0 else 0.22) * s, math.sin(-math.pi / 2 + math.pi + k * math.pi / 5) * (0.5 if k % 2 == 0 else 0.22) * s) for k in range(10)]
    d.poly([(x + px, y + 0.25 * s + py) for px, py in st], A((236, 186, 80), a))
    d.poly([(x + px * 0.55 - 0.03 * s, y + 0.22 * s + py * 0.55) for px, py in st], A((255, 226, 150), a))

def s_medal(t, img, d):
    t0 = T["medal"]; r1, r2, r3 = t0 + 2.75, t0 + 3.9, t0 + 4.9
    img.paste(vgrad((16, 18, 24), (10, 10, 12)))
    soft_shape(img, lambda g: g.ell(540, 820, 560, 520, fill=A((255, 196, 120), 0.35)), blur=110)
    k = E.spring_at(t, t0 - 0.1, 0, 1, "snappy") if t >= t0 - 0.1 else 0
    y0 = 340 + 60 * (1 - min(k, 1))
    d.rect(150, y0, 930, y0 + 900, fill=A((222, 210, 182), min(1, k * 1.5)), r=14)
    d.rect(150, y0, 930, y0 + 70, fill=A((196, 176, 140), min(1, k * 1.5)), r=14)
    ink = (60, 44, 30)
    d.text(540, y0 + 36, "荣誉勋章 · 嘉奖词", 40, A(ink, min(1, k * 1.5)))
    medal_icon(d, 540, y0 + 270, 120 * (0.9 + 0.1 * min(k, 1.05)), min(1, k * 1.5))
    d.text(540, y0 + 420, "1918.10.8 · 阿尔贡森林", 40, A(ink, ap(t, t0 + 0.6, 0.3)))
    d.text(540, y0 + 480, "俘虏：", 40, A(ink, ap(t, t0 + 0.9, 0.3)))
    for s0, txt, yy in ((r1, "4 名军官", 560), (r2, "128 名士兵", 650)):
        if t > s0:
            kk = popk(t, s0, "bouncy"); d.text(540, y0 + yy, txt, int(70 * (0.7 + 0.3 * min(kk, 1.1))), A((40, 30, 22), ap(t, s0, 0.1)))
    if t > r3:
        d.line([(300, y0 + 715), (780, y0 + 715)], A(ink, ap(t, r3, 0.2)), 4)
        slam(d, t, r3, "= 132 人", 540, y0 + 790, 96, (196, 92, 30))
    d.text(540, y0 + 868, "来源：国会荣誉勋章协会 CMOHS", 28, A((110, 92, 70), ap(t, t0 + 0.8, 0.3)))

def icon_prone(d, x, y, s, col, a):
    d.rect(x - 0.9 * s, y + 0.05 * s, x + 0.4 * s, y + 0.35 * s, fill=A(col, a), r=0.15 * s)
    d.circ(x + 0.55 * s, y + 0.05 * s, 0.22 * s, fill=A(col, a)); d.line([(x + 0.4 * s, y + 0.2 * s), (x + 1.0 * s, y + 0.12 * s)], A(col, a), 0.08 * s)
    d.rect(x - 1.0 * s, y + 0.38 * s, x + 1.05 * s, y + 0.46 * s, fill=A(col, 0.5 * a))
def icon_cross(d, x, y, s, col, a):
    d.circ(x, y, 0.62 * s, outline=A(col, a), w=0.1 * s)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): d.line([(x + dx * 0.25 * s, y + dy * 0.25 * s), (x + dx * 0.85 * s, y + dy * 0.85 * s)], A(col, a), 0.08 * s)
    d.circ(x, y, 0.1 * s, fill=A(col, a))
def icon_talk(d, x, y, s, col, a):
    d.rect(x - 0.8 * s, y - 0.55 * s, x + 0.8 * s, y + 0.4 * s, fill=A(col, a), r=0.3 * s)
    d.poly([(x - 0.3 * s, y + 0.35 * s), (x + 0.05 * s, y + 0.35 * s), (x - 0.4 * s, y + 0.8 * s)], A(col, a))
    d.text(x, y - 0.08 * s, "降", int(0.7 * s), A((24, 18, 12), a))

def s_card(t, img, d):
    t0 = T["card"]; ts = [t0 + 1.45, t0 + 2.3, t0 + 3.45]
    img.paste(vgrad((20, 18, 16), (10, 10, 12)))
    soft_shape(img, lambda g: g.ell(540, 820, 520, 520, fill=A((255, 170, 80), 0.3)), blur=110)
    k = popk(t, t0 - 0.1); kk = min(k, 1)
    d.rect(160, 330 + 40 * (1 - kk), 920, 1230, fill=A((26, 28, 30), 0.9 * min(1, k * 1.5)), r=36)
    tag(d, 540, 410, "一句话学会", AMBER, min(1, k * 1.5), 40)
    d.text(540, 510, "约克三招", 76, A(WHITE, min(1, k * 1.5)))
    rows = [(icon_prone, "趴低", "子弹难打中"), (icon_cross, "一枪一个准", "不慌，瞄准再打"), (icon_talk, "喊话劝降", "让对方先放下枪")]
    for i, ((ic, big_, small), s0) in enumerate(zip(rows, ts)):
        if t < s0 - 0.05: continue
        kk = popk(t, s0, "bouncy"); a_ = ap(t, s0, 0.1); y = 680 + i * 180
        d.circ(290, y, 62, fill=A((50, 50, 52), a_))
        ic(d, 290, y, 52 * (0.7 + 0.3 * min(kk, 1.1)), AMBER, a_)
        d.text(390, y - 24, big_, int(58 * (0.8 + 0.2 * min(kk, 1.1))), A(WHITE, a_), anchor="lm")
        d.text(390, y + 40, small, 36, A((190, 186, 176), a_), anchor="lm")

def s_end(t, img, d):
    """Callback to the hook: same valley, now quiet — rifles laid down; then his face and the question."""
    t0 = T["end"]; tb = t0 + 3.7; q1, q2 = t0 + 4.9, t0 + 6.0
    def wide(L, dd):
        L.paste(vgrad((30, 34, 44), (20, 20, 18), mid=(0.55, (200, 130, 70))))
        soft_shape(L, lambda g: g.ell(540, 1000, 600, 200, fill=A((255, 190, 100), 0.7)), blur=90)
        ridge(dd, 930, 40, (40, 44, 44), 1)
        for i, (x, hh) in enumerate(((120, 300), (300, 220), (820, 260), (980, 340))): deadtree(dd, x, 1000, hh, (36, 40, 40), i)
        ridge(dd, 1040, 26, (44, 46, 44), 4)
        ky = 1060; ks = 170 * (1 + 0.06 * eio(pr(t, t0, tb)))
        body = spline([(-0.22, -1.1), (0.22, -1.1), (0.3, -0.2), (0.18, 0.05), (-0.18, 0.05), (-0.3, -0.2)], n=4)
        rimpoly(dd, xf(body, 540, ky, ks), (30, 28, 22), AMBER_L, 0, 2)
        dd.circ(540, ky - ks * 1.32, ks * 0.2, fill=A(AMBER_L, 1)); dd.circ(540, ky - ks * 1.3, ks * 0.18, fill=A((34, 30, 24), 1))
        brodie_side(dd, Map(540, ky - ks * 1.44, ks), 0, 0, 0.9, AMBER_L)
        fog(L, t + 3, (140, 130, 120), 0.35, 16, 980, 1260, 200, seed=5)
        ridge(dd, 1330, 30, (34, 32, 28), 7)
        for i in range(16):   # rifles laid down in the foreground
            x = 80 + i * 60 + 20 * hsh(i, 70); y = 1450 + 120 * hsh(i, 71); ang = -0.25 + 0.5 * hsh(i, 72)
            dd.line([(x - 150 * math.cos(ang), y - 150 * math.sin(ang)), (x + 150 * math.cos(ang), y + 150 * math.sin(ang))], A(mix((70, 50, 34), (140, 100, 60), hsh(i, 73)), 1), 14)
        sandbags2(dd, 1620, (50, 46, 38), (190, 130, 80), 3)
        fog(L, t * 0.6, (70, 64, 58), 0.25, 8, 1550, 1920, 200, seed=8)
        a_ = ap(t, t0 + 0.4, 0.2)
        if a_ > 0:
            k = popk(t, t0 + 0.4, "bouncy"); dd.text(540, 430, "132 人", int(150 * (0.7 + 0.3 * min(k, 1.1))), A(AMBER, a_))
            dd.text(540, 580, "放下了枪", 90, A(WHITE, ap(t, t0 + 0.9, 0.2)))
    def close(L, dd):
        L.paste(vgrad((8, 12, 16), (12, 14, 14), mid=(0.5, (34, 36, 34))))
        soft_shape(L, lambda g: g.ell(220, 900, 420, 700, fill=A((255, 160, 70), 0.4)), blur=120)
        z = 1 + 0.04 * eio(pr(t, tb, t0 + 8)); york_face(L, dd, 540, 960, 560 * z, t, key=AMBER, rim=COLD, squint=0.2, blink=(tb + 2.0 < t < tb + 2.12))
        fog(L, t + 4, (60, 70, 70), 0.45, 14, 1400, 1920, 260, seed=10)
        for s0, txt, x in ((q1, "枪法？", 300), (q2, "胆量？", 780)):
            if t > s0: k = popk(t, s0, "bouncy"); tag(dd, x, 420, txt, AMBER if txt == "胆量？" and False else (236, 226, 204), ap(t, s0, 0.1), int(64 * (0.7 + 0.3 * min(k, 1.1))))
        if t > q2 - 0.3: dd.text(540, 420, "还是", 44, A(WHITE, ap(t, q2 - 0.3, 0.2)))
        if t > q2 + 1.0: dd.text(540, 540, "评论区说说你的看法", 40, A(AMBER_L, ap(t, q2 + 1.0, 0.3)))
    if t < tb: wide(img, d)
    elif t < tb + 0.4:
        A_ = Image.new("RGB", (W, H)); wide(A_, D(A_)); B_ = Image.new("RGB", (W, H)); close(B_, D(B_))
        img.paste(Image.blend(A_, B_, eio((t - tb) / 0.4)))
    else: close(img, d)

def s_stub(t, img, d):
    img.paste(vgrad((14, 18, 20), (10, 10, 10)))

SCN = {"hook": s_hook, "big1": s_big1, "q": s_q, "who": s_who, "nowar": s_nowar, "pinned": s_pinned, "big2": s_big2, "why": s_why,
       "peek": s_shot, "shot": s_shot, "hunt2": s_hunt2, "shout": s_shout, "fear": s_fear, "give": s_give, "march": s_march,
       "medal": s_medal, "card": s_card, "end": s_end}
XF = {"shot": 0, "q": 0.35, "who": 0.35, "nowar": 0.35, "pinned": 0.35, "why": 0.35, "peek": 0.35, "hunt2": 0.35, "shout": 0.35, "fear": 0.35, "give": 0.35, "march": 0.35, "medal": 0.35, "card": 0.35, "end": 0.35}
SECS = [(max(-1, a if i else -1), b, k) for i, (a, b, s, k) in enumerate(SUBS)]
def scene_at(t):
    for i, (a, b, k) in enumerate(SECS):
        if a <= t < b: return i
    return len(SECS) - 1
def render_scene(k, t):
    img = Image.new("RGB", (W, H), (10, 10, 10)); d = D(img); SCN.get(k, s_stub)(t, img, d); return img
def cam(t):
    z = 1.0 + 0.04 * pulse(t, [BIG1, BIG2], 3)
    sx, sy = E.shake(t, BIG1, 8, 0.4) if t < BIG2 else E.shake(t, BIG2, 8, 0.4)
    return z, sx, sy
def subtitle(d, t):
    i = scene_at(t); st, en, s, k = SUBS[i]
    if k in NOSUB: return
    a = ap(t, max(st, 0), 0.12) * (1 - pr(t, en - 0.08, en))
    if a <= 0.01: return
    lines = s.split("|"); size = 52; lh = 74
    wmax = max(d.tlen(l, size) for l in lines) + 56
    y0 = 1330 - (len(lines) - 1) * lh / 2
    d.rect(540 - wmax / 2, y0 - lh / 2 - 8, 540 + wmax / 2, y0 + (len(lines) - 1) * lh + lh / 2 + 8, fill=A((8, 10, 12), 0.62 * a), r=22)
    for j, l in enumerate(lines): d.text(540, y0 + j * lh, l, size, A(WHITE, a))
def ui(d, t):
    s = "Vibe 知识大赏 · 超级士兵 No.02"; w = d.tlen(s, 28) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((10, 10, 12), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 0.92))
def frame(t, fi=0):
    i = scene_at(t); a, b, k = SECS[i]
    img = render_scene(k, t)
    xfd = XF.get(k, 0)
    if xfd and t < a + xfd and i > 0:
        prev = render_scene(SECS[i - 1][2], t); img = Image.blend(prev, img, eio((t - a) / xfd))
    z, sx, sy = cam(t)
    if z != 1.0 or sx or sy:
        cw, ch = W / z, H / z; x0 = (W - cw) / 2 - P(sx); y0 = (H - ch) / 2 - P(sy)
        img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    d = D(img)
    for c in (BIG1, BIG2):
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - (t - c) / 0.1)))
    subtitle(d, t); ui(d, t)
    img = img.resize((OW, OH), Image.LANCZOS)
    img = E.vignette(img, 0.3, 0.5); img = E.grain(img, 0.03, seed=fi)
    return img

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "test":
        for s_ in sys.argv[2:]: frame(float(s_), int(float(s_) * 30)).save(f"/tmp/yk_test_{s_}.png")
    elif cmd == "sheet":
        out = sys.argv[2]; ts = [float(x) for x in sys.argv[3:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=4, thumb_w=360, labels=[f"{x:.2f}s {SUBS[scene_at(x)][3]}" for x in ts]).save(out)
    elif cmd == "render":
        f0, f1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", "30", "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for fi in range(f0, f1): p.stdin.write(frame(fi / 30, fi).tobytes())
        p.stdin.close(); p.wait()
