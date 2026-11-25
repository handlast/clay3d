# 《超级士兵 No.03 19岁小个子 vs 6辆坦克》 Audie L. Murphy — dark, fire-lit, German POV silhouette grows; no outlines, no gore.
# python3 film.py test t1 t2 ... -> /tmp/mu_test_<t>.png ; sheet out.png t... ; render f0 f1 out.mp4   (env MS=2.0 for face segments)
import sys, subprocess
from PIL import ImageOps
from chars3 import *
from cues import *

NOSUB = {"hook", "big2"}
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
def tracer(d, x0, y0, x1, y1, u, col=FIRE_L, a=1.0, L=0.15, w=5):
    if not (0 <= u <= 1 + L): return
    ua, ub = cl(u - L), cl(u)
    d.line([(lerp(x0, x1, ua), lerp(y0, y1, ua)), (lerp(x0, x1, ub), lerp(y0, y1, ub))], A(col, a), w)
def flash_at(t, times, dur=0.12): return max([max(0.0, 1 - (t - b) / dur) for b in times if t >= b] + [0.0])
def stepped(t, times, dur=0.25):
    """count of completed steps with eased in-between motion (continuous)."""
    v = 0.0
    for b in times: v += eio(pr(t, b, b + dur))
    return v
def odo(t, t0, dur, n):
    u = pr(t, t0, t0 + dur); return int(round(n * (1 - (1 - u) ** 2.2)))

def sky(img, top=(10, 12, 20), bot=(46, 40, 44), mid=(0.5, (60, 40, 38))): img.paste(vgrad(top, bot, mid=mid))
def snowfield(d, img, t, gy, glowx=540, glowa=0.5, seed=0):
    d.poly([(-40, gy + 10), (1120, gy - 6), (1120, 1960), (-40, 1960)], A(SNOW, 1))
    soft_shape(img, lambda g: g.ell(glowx, gy + 40, 560, 90, fill=A(FIRE, glowa)), blur=60)
    for i in range(14):
        x = (i * 97 + 210 * hsh(i, seed)) % 1160 - 40; y = gy + 40 + 700 * hsh(i, seed + 1) ** 1.6
        r = 30 + 60 * hsh(i, seed + 2) * (1 + (y - gy) / 400)
        d.ell(x, y, r * 2.2, r * 0.35, fill=A(mix(SNOW, SNOW_L, 0.3 + 0.4 * hsh(i, seed + 3)), 0.55))
def burning_m10(img, d, x, y, s, t, flip=-1, fire=1.0, smoke_a=1.0, seed=0):
    m = m10(img, d, x, y, s, t, key=FIRE, flip=flip)
    fx, fy = m.p(0.6, -1.8)
    smoke(img, d, fx, fy - s, 3.2 * s, 14 * s, t, smoke_a * fire, seed=seed)
    flames(img, d, fx, fy + 0.1 * s, 2.6 * s, 2.6 * s * fire, t, fire, seed=seed)
    embers(d, fx, fy, 3 * s, 9 * s, t, fire, seed=seed)
    return m
def ui_txt(d, x, y, s, size, col, a=1.0): d.text(x, y, s, size, A(col, a))

# ================================================================ scenes
def s_hook(t, img, d):
    sky(img)
    soft_shape(img, lambda g: g.ell(560, 1000, 620, 260, fill=A(FIRE, 0.55)), blur=110)
    woods(d, 1010, (22, 22, 28), seed=3, hmin=110, hmax=190)
    fog(img, t, (70, 62, 66), 0.3, 10, 880, 1060, 160, seed=2)
    snowfield(d, img, t, 1010, 560, 0.45)
    g = 1 + 0.22 * eio(pr(t, -0.3, T["who"]))
    m = burning_m10(img, d, 560, 1080, 34 * g, t, flip=-1)
    fx_ = flash_at(t, [k * 0.14 for k in range(30)], 0.07)
    px, py = m.p(-1.2, -2.6)
    murphy_sil(img, d, px, py, 170 * g, t, flash=fx_)
    for j in range(16):   # tracers fan out from his MG toward the German line (camera)
        t0 = j * 0.21 - 0.1; u = (t - t0) / 0.45
        tx = 540 + (-1) ** j * (180 + 260 * hsh(j, 3)); ty = 1500 + 300 * hsh(j, 4)
        tracer(d, px + 10, py - 58 * g, tx, ty, u, FIRE_L, 0.9, 0.2, 5)
    ger_tank(d, 230, 1180, 95, t, rear=True); ger_tank(d, 870, 1210, 110, t, rear=True)
    snowfall(d, t, 0.5, 50, seed=1)
    german_back(d, 170, 1640, 160, t, rim=FIRE_L, lean=-0.08, seed=1)
    german_back(d, 920, 1700, 180, t, rim=FIRE_L, lean=0.06, seed=2)
    fog(img, t * 0.6, (40, 34, 36), 0.25, 8, 1500, 1920, 200, seed=8)
    k = popk(t, -0.15, "bouncy")
    d.text(540, 390, "19岁小个子", int(140 * (0.7 + 0.3 * min(k, 1.1))), A(FIRE_L, ap(t, -0.15, 0.1)))
    k2 = popk(t, 0.3, "bouncy")
    if k2 > 0: d.text(540, 545, "1个人 VS 6辆坦克", int(80 * (0.7 + 0.3 * min(k2, 1.1))), A(WHITE, ap(t, 0.3, 0.12)))

def s_who(t, img, d):
    t0 = T["who"]
    img.paste(vgrad((22, 26, 34), (12, 12, 14), mid=(0.62, (36, 40, 48))))
    soft_shape(img, lambda g: g.ell(560, 700, 420, 520, fill=A((255, 196, 130), 0.25)), blur=120)
    d.poly([(-40, 1240), (1120, 1240), (1120, 1960), (-40, 1960)], A((30, 30, 32), 1))
    cy = 560 + 4 * math.sin(t * 1.3); hh = 140; top = cy - 0.6 * hh; k = (1240 - top) / 165
    # height ruler
    rx = 250; a_r = ap(t, t0 + 0.1, 0.3)
    d.rect(rx - 20, 1240 - 180 * k, rx + 20, 1240, fill=A((214, 200, 168), 0.9 * a_r), r=6)
    for cm in range(0, 181, 10):
        yy = 1240 - cm * k; L = 30 if cm % 50 == 0 else 16
        d.line([(rx - 20, yy), (rx - 20 + L, yy)], A((60, 44, 30), a_r), 3)
    # Murphy: body + legs, then the face
    for sg in (-1, 1):
        d.line([(540 + sg * 0.42 * hh, cy + 3.2 * hh), (540 + sg * 0.45 * hh, 1236)], A((62, 58, 40), 1), 0.62 * hh)
        d.ell(540 + sg * 0.5 * hh, 1236, 0.36 * hh, 0.1 * hh, fill=A((40, 30, 24), 1))
    d.rect(540 - 1.15 * hh, cy + 1.2 * hh, 540 + 1.15 * hh, cy + 3.35 * hh, fill=A((56, 54, 38), 1), r=0.3 * hh)
    d.rect(540 - 1.0 * hh, cy + 3.0 * hh, 540 + 1.0 * hh, cy + 3.25 * hh, fill=A((40, 36, 26), 1))
    for sg in (-1, 1): d.line([(540 + sg * 1.25 * hh, cy + 1.0 * hh), (540 + sg * 1.4 * hh, cy + 3.0 * hh)], A((60, 58, 40), 1), 0.4 * hh)
    for sg in (-1, 1): d.circ(540 + sg * 1.4 * hh, cy + 3.1 * hh, 0.18 * hh, fill=A(SKIN_M, 1))
    murphy_face(img, d, 540, cy, hh, t, key=(255, 200, 140), rim=COLD, squint=0.15, blink=(t0 + 2.2 < t < t0 + 2.32))
    # 165 cm mark (pops) + 50 kg scale
    s1 = t0 + 1.0; kk = popk(t, s1)
    if kk > 0:
        yy = top; a1 = ap(t, s1, 0.15)
        d.line([(rx + 20, yy), (540 - 0.5 * hh, yy)], A(FIRE_L, 0.8 * a1), 4)
        d.text(rx + 130, yy - 36, "165cm", int(52 * (0.7 + 0.3 * min(kk, 1.1))), A(FIRE_L, a1))
    s2 = t0 + 1.8
    if t > s2 - 0.2:
        a2 = ap(t, s2 - 0.2, 0.25)
        d.rect(690, 1150, 880, 1230, fill=A((24, 26, 28), 0.95 * a2), r=14)
        d.text(785, 1190, f"{odo(t, s2, 0.9, 50)}kg", 52, A(FIRE_L, a2))

def s_attack(t, img, d):
    t0 = T["attack"]; adv = eio(pr(t, t0 - 0.3, nxt("attack")))
    sky(img, (10, 12, 18), (40, 42, 50), (0.55, (50, 48, 54)))
    woods(d, 900, (24, 26, 32), seed=7, hmin=90, hmax=150)
    fog(img, t, (80, 84, 92), 0.35, 12, 800, 980, 160, seed=11)
    d.poly([(-40, 905), (1120, 895), (1120, 1960), (-40, 1960)], A(SNOW, 1))
    for row, (yy, hh, n) in enumerate(((960, 46, 12), (1010, 60, 10))):
        for i in range(n):
            x = 60 + i * (960 / (n - 1)) + 20 * hsh(i, row); y = yy + 30 * adv + 10 * hsh(i, row + 5)
            inf_front(d, x, y, hh * (1 + 0.15 * adv), t, ph=i * 1.3 + row, key=FIRE_L if x > 540 else COLD, a=0.85)
        fog(img, t + row, (90, 92, 100), 0.25, 14, yy - 60, yy + 40, 80, seed=12 + row)
    tanks = [(170, 1060, 70), (400, 1030, 62), (640, 1045, 66), (880, 1070, 74), (290, 1150, 92), (760, 1170, 98)]
    for i, (x, y, s) in enumerate(sorted(tanks, key=lambda q: q[1])):
        sc = s * (1 + 0.25 * adv); yy = y + 70 * adv
        ger_tank(d, x + (x - 540) * 0.1 * adv, yy, sc, t, key=COLD)
        d.ell(x + (x - 540) * 0.1 * adv, yy + 4, sc * 1.1, sc * 0.08, fill=A((60, 66, 76), 0.6))
    snowfall(d, t, 0.55, 60, seed=2)
    fog(img, t * 0.6, (50, 54, 62), 0.3, 8, 1500, 1920, 220, seed=13)
    for i in range(6):   # tank tally (icons, no text)
        s0 = t0 + 0.4 + i * 0.22
        if t >= s0:
            kk = popk(t, s0, "bouncy"); ger_tank(d, 290 + i * 100, 480, 40 * (0.6 + 0.4 * min(kk, 1.1)), t, key=(255, 230, 190), a=ap(t, s0, 0.12))

def kneel_phone(img, d, x, y, h, t, key=FIRE_L, a=1.0, talk=0.0):
    """Murphy kneeling, faces LEFT, handset at the ear. (x,y) = knee on ground, h = head height."""
    uni, uni_l = (66, 62, 42), mix(OD_L, key, 0.5)
    tor = [(x - 0.4 * h, y - 3.1 * h), (x + 0.5 * h, y - 3.0 * h), (x + 0.6 * h, y - 1.4 * h), (x - 0.4 * h, y - 1.3 * h)]
    d.poly(tor, A(uni_l, a)); d.poly([(px + 0.05 * h, py + 0.03 * h) for px, py in tor], A(uni, a))
    d.line([(x + 0.3 * h, y - 1.4 * h), (x - 0.9 * h, y - 1.1 * h), (x - 1.0 * h, y)], A((56, 52, 36), a), 0.42 * h)   # front leg
    d.line([(x + 0.4 * h, y - 1.3 * h), (x + 0.9 * h, y - 0.1 * h), (x + 2.0 * h, y)], A((50, 46, 32), a), 0.42 * h)    # knee down
    hm = Map(x, y - 3.65 * h, h, 0.0, flip=-1)
    head_side(d, hm, key, COLD, a, hat=None, squint=0.35, mouth=talk)
    m1_side(d, hm, 0.03, -0.32, 1.2, key, a)
    d.line([(x + 0.4 * h, y - 2.8 * h), (x + 0.2 * h, y - 1.9 * h), (x - 0.1 * h, y - 3.45 * h)], A(uni, a), 0.26 * h)  # arm up to ear
    d.rect(x - 0.2 * h, y - 3.7 * h, x + 0.05 * h, y - 3.3 * h, fill=A((30, 30, 28), a), r=0.06 * h)                  # handset
    d.rect(x + 0.9 * h, y - 0.7 * h, x + 1.9 * h, y, fill=A((56, 50, 34), a), r=0.08 * h)                                 # EE-8 phone case
    d.line([(x + 1.9 * h, y - 0.2 * h), (x + 3.5 * h, y + 0.1 * h), (1200, y + 0.3 * h)], A((20, 20, 20), a), 3)          # wire

def s_retreat(t, img, d):
    t0 = T["retreat"]
    sky(img, (10, 12, 18), (40, 40, 46), (0.55, (58, 46, 46)))
    soft_shape(img, lambda g: g.ell(160, 980, 420, 160, fill=A(FIRE, 0.35)), blur=100)
    d.poly([(-40, 1040), (1120, 1030), (1120, 1960), (-40, 1960)], A(SNOW, 1))
    # comrades walk right into the woods and fade among the trees (each on its own time)
    for i in range(7):
        x = 330 + i * 70 + (t - t0 + 0.4) * 55 - 10 * hsh(i, 5)
        a_ = 1 - eio(pr(x, 760, 900))
        walker(d, x, 1100 + 12 * hsh(i, 6), 26, t, i * 1.7, "us", key=FIRE_L, a=a_)
    woods(d, 1115, (18, 22, 24), seed=21, x0=780, x1=1120, hmin=170, hmax=300, lit=(90, 70, 60))
    woods(d, 1150, (14, 16, 18), seed=22, x0=820, x1=1140, hmin=220, hmax=340)
    for i, s0 in enumerate(ARTY):   # shells arc from behind the woods to the enemy side (left), snow puff
        u = pr(t, s0 - 0.9, s0)
        if 0 < u < 1:
            x = lerp(980, 90 + 60 * i, u); y = lerp(760, 960, u) - 380 * math.sin(math.pi * u)
            d.circ(x, y, 6, fill=A(FIRE_C, 1)); d.line([(x, y), (x + 40, y + 6 - 60 * math.cos(math.pi * u))], A(FIRE_L, 0.5), 3)
        if t >= s0:
            v = pr(t, s0, s0 + 1.2)
            if v < 1:
                bx = 90 + 60 * i
                glow(img, lambda g: g.circ(bx, 990, 30 + 50 * v, fill=A(FIRE_L, 1 - v)), blur=30) if v < 0.25 else None
                d.circ(bx, 990 - 60 * v, 40 + 90 * v, fill=A(SNOW_L, 0.55 * (1 - v)))
    kneel_phone(img, d, 260, 1420, 85, t, talk=0.5 * max(0, math.sin((t - t0) * 10)) * (1 - pr(t, t0 + 3.2, t0 + 3.4)))
    snowfall(d, t, 0.5, 50, seed=3)
    fog(img, t * 0.6, (50, 50, 58), 0.3, 8, 1550, 1920, 200, seed=14)

def s_hit(t, img, d):
    t0 = T["hit"]; hk = HIT_T
    sky(img, (10, 12, 18), (40, 38, 42), (0.55, (56, 44, 44)))
    woods(d, 1060, (18, 22, 24), seed=31, x0=760, x1=1120, hmin=170, hmax=280)
    d.poly([(-40, 1060), (1120, 1050), (1120, 1960), (-40, 1960)], A(SNOW, 1))
    fire = eio(pr(t, hk + 0.05, hk + 0.9))
    if fire > 0: soft_shape(img, lambda g: g.ell(660, 1120, 460, 160, fill=A(FIRE, 0.5 * fire)), blur=90)
    m = m10(img, d, 660, 1150, 50, t, key=mix(COLD, FIRE, fire), flip=-1)
    fx, fy = m.p(0.6, -1.8)
    if fire > 0:
        smoke(img, d, fx, fy - 50, 160, 700, t, fire, seed=2)
        flames(img, d, fx, fy + 5, 130, 140 * fire, t, fire, seed=2); embers(d, fx, fy, 150, 450, t, fire, seed=2)
    if hk <= t < hk + 0.3:
        v = (t - hk) / 0.3; glow(img, lambda g: g.circ(fx, fy, 60 + 200 * v, fill=A(FIRE_C, 1 - v)), blur=40)
    for i in range(2):   # crew climbs out and runs to the woods, fading among trees
        st = hk + 0.5 + i * 0.35
        if t > st:
            x = fx + 30 + (t - st) * 160; a_ = ap(t, st, 0.3) * (1 - eio(pr(x, 900, 1010)))
            walker(d, x, 1150 + 10 * i, 22, t * 1.6, i * 2.0, "us", key=FIRE_L, a=a_)
    kneel_phone(img, d, 200, 1440, 80, t, talk=0.0)
    snowfall(d, t, 0.45, 45, seed=4)
    fog(img, t * 0.6, (50, 46, 50), 0.3, 8, 1550, 1920, 200, seed=15)
    if t > t0 + 0.3: tag(d, 660, 800, "M10", (214, 206, 186), ap(t, t0 + 0.3, 0.25), 40)

def murphy_side(img, d, x, y, h, t, climb=1.0, key=FIRE_L, a=1.0, grip=True):
    """Full side figure facing LEFT (toward the enemy). (x,y) = feet, h = head height (~6.6 h tall).
    climb 0..1: from reaching up / knee raised to standing at the gun."""
    m = Map(x, y, h, 0.0, flip=-1)
    uni, uni_l, uni_d = (66, 62, 42), mix(OD_L, key, 0.55), (48, 46, 30)
    c = eio(climb)
    hip = (0.0, -2.9); knee_b = (lerp(-0.6, -0.1, c), lerp(-2.4, -1.5, c)); foot_b = (lerp(-0.5, 0.0, c), lerp(-1.6, 0.0, c))
    d.line(m([(0.2, -2.9), (0.35, -1.5), (0.3, 0.0)]), A(uni_d, a), 0.45 * h)
    d.line(m([hip, knee_b, foot_b]), A(uni, a), 0.45 * h)
    for f in ((0.3, 0.0), foot_b): d.poly(m(ellpts(f[0] - 0.15, f[1] - 0.08, 0.3, 0.12)), A((40, 30, 24), a))
    tor = spline([(-0.45, -5.6), (0.5, -5.5), (0.55, -3.9), (0.45, -2.7), (-0.5, -2.7), (-0.55, -4.0)], n=4)
    tl = [(px + lerp(-0.4, 0.15, c) * (py + 2.7) / -2.9, py) for px, py in tor]
    d.poly(m(tl), A(uni_l, a)); d.poly(m([(px + 0.06, py + 0.04) for px, py in tl]), A(uni, a))
    hx = lerp(-0.5, 0.2, c)
    hm = Map(*m.p(hx, -6.1), h, 0.0, flip=-1)
    head_side(d, hm, key, COLD, a, hat=None, squint=0.45)
    m1_side(d, hm, 0.03, -0.32, 1.2, key, a)
    if grip:   # hands forward on the spade grips (at ~ -4.6)
        d.line(m([(hx, -5.2), (lerp(0.6, 0.9, c), lerp(-6.6, -4.6, c)), (lerp(0.8, 1.6, c), lerp(-7.4, -4.8, c))]), A(uni, a), 0.3 * h)
        d.poly(m(ellpts(lerp(0.8, 1.6, c), lerp(-7.4, -4.8, c), 0.16, 0.13)), A(mix(SKIN_M, key, 0.3), a))
    return m

def s_big2(t, img, d):
    t0 = BIG2
    sky(img, (12, 10, 14), (60, 34, 30), (0.5, (90, 44, 30)))
    soft_shape(img, lambda g: g.ell(560, 1200, 700, 300, fill=A(FIRE, 0.55)), blur=110)
    d.poly([(-40, 1420), (1120, 1410), (1120, 1960), (-40, 1960)], A(mix(SNOW, FIRE, 0.15), 1))
    m = m10(img, d, 520, 1440, 95, t, key=FIRE, flip=-1)
    fx, fy = m.p(0.7, -1.8)
    smoke(img, d, fx, fy - 90, 300, 1000, t, 1.0, seed=3)
    flames(img, d, fx + 40, fy + 8, 230, 260, t, 1.0, seed=3)
    c = E.spring_at(t, t0 + 0.05, 0, 1, "snappy") if t >= t0 + 0.05 else 0.0
    dx, dy = m.p(-1.7, -1.8)          # rear deck
    gx, gy_ = m.p(-2.9, -0.2)         # beside the rear track
    px = lerp(gx + 20, dx, min(1, c)); py = lerp(gy_ - 120, dy, min(1, c))
    murphy_side(img, d, px, py, 46, t, climb=min(1, c))
    embers(d, fx, fy, 300, 700, t, 1.0, 22, seed=3)
    snowfall(d, t, 0.4, 40, seed=5)
    d.text(540, 330, "他却", 84, A(WHITE, ap(t, t0 + 0.02, 0.1)))
    slam(d, t, t0 + 0.12, "爬了上去！", 540, 490, 140, FIRE_L)

def s_danger(t, img, d):
    t0 = T["danger"]
    img.paste(vgrad((14, 8, 10), (50, 20, 14), mid=(0.6, (70, 30, 20))))
    soft_shape(img, lambda g: g.ell(120, 1760, 420, 260, fill=A(FIRE, 0.7)), blur=90)      # fire light low-left, away from the face
    soft_shape(img, lambda g: g.ell(980, 1820, 360, 220, fill=A(FIRE, 0.55)), blur=90)
    smoke(img, d, 540, 380, 600, 500, t, 0.6, n=10, seed=7, col=(30, 22, 22))
    fl = 0.5 + 0.5 * math.sin(t * 8.3) * math.sin(t * 3.7)
    key = mix(FIRE_L, (255, 214, 150), 0.4 + 0.2 * fl)
    z = 1 + 0.04 * eio(pr(t, t0 - 0.3, nxt("danger")))
    murphy_face(img, d, 540, 840, 500 * z, t, key=key, rim=COLD, squint=0.3, blink=(t0 + 1.4 < t < t0 + 1.52))
    flames(img, d, 120, 1940, 360, 380, t, 1.0, glow_on=False, seed=8)
    flames(img, d, 990, 1950, 300, 300, t, 1.0, glow_on=False, seed=9)
    embers(d, 140, 1700, 260, 1200, t, 1.0, 14, seed=8); embers(d, 960, 1700, 220, 1200, t, 1.0, 12, seed=9)

def m2_gun(img, d, x, y, s, t, recoil=0.0, key=FIRE_L, a=1.0):
    """Browning .50 side view, muzzle LEFT. (x,y) = receiver centre, s = scale (receiver ~ 3 s long)."""
    x += recoil * 8
    d.rect(x - 1.5 * s, y - 0.5 * s, x + 1.5 * s, y + 0.5 * s, fill=A((40, 42, 44), a), r=0.1 * s)
    d.rect(x - 1.5 * s, y - 0.5 * s, x + 1.5 * s, y - 0.32 * s, fill=A(mix((90, 92, 96), key, 0.45), a), r=0.08 * s)
    d.rect(x - 4.8 * s, y - 0.28 * s, x - 1.5 * s, y + 0.18 * s, fill=A((46, 48, 50), a), r=0.12 * s)            # barrel jacket
    for i in range(7): d.ell(x - 4.4 * s + i * 0.45 * s, y - 0.05 * s, 0.12 * s, 0.09 * s, fill=A((16, 16, 18), a))
    d.line([(x - 4.8 * s, y - 0.25 * s), (x - 1.5 * s, y - 0.25 * s)], A(mix((120, 120, 124), key, 0.5), a), 0.06 * s)
    d.rect(x - 5.4 * s, y - 0.16 * s, x - 4.8 * s, y + 0.08 * s, fill=A((30, 30, 32), a), r=0.06 * s)            # muzzle
    d.rect(x + 1.5 * s, y - 0.3 * s, x + 1.75 * s, y + 0.3 * s, fill=A((36, 36, 38), a))
    for sg in (-1, 1): d.rect(x + 1.75 * s, y + sg * 0.32 * s - 0.1 * s, x + 2.3 * s, y + sg * 0.32 * s + 0.1 * s, fill=A((70, 50, 34), a), r=0.08 * s)   # spade grips
    d.line([(x - 0.2 * s, y + 0.5 * s), (x - 0.2 * s, y + 2.2 * s)], A((36, 36, 34), a), 0.25 * s)                  # pintle
    return (x - 5.4 * s, y - 0.04 * s)

def s_mg(t, img, d):
    t0 = T["mg"]
    img.paste(vgrad((12, 10, 14), (40, 18, 14), mid=(0.55, (50, 28, 24))))
    soft_shape(img, lambda g: g.ell(700, 1500, 600, 300, fill=A(FIRE, 0.6)), blur=110)
    smoke(img, d, 760, 1300, 500, 1100, t, 0.8, n=12, seed=11, col=(28, 22, 24))
    fl = flash_at(t, MG_BURSTS, 0.12); rc = flash_at(t, MG_BURSTS, 0.1)
    mx, my = m2_gun(img, d, 640, 860, 82, t, recoil=rc)
    # ammo belt feeding in from the left side, links move a step per burst
    off = stepped(t, MG_BURSTS, 0.1) * 26
    for i in range(14):
        bx = 560 - 20 - ((i * 26 - off) % 364) * 0.15; by = 905 + ((i * 26 - off) % 364)
        d.rect(bx - 22, by - 7, bx + 22, by + 7, fill=A(mix((170, 130, 60), FIRE_L, 0.3), 1), r=5)
    # his hands on the spade grips (gloves)
    for sg in (-1, 1): d.ell(640 + 2.05 * 82, 860 + sg * 0.32 * 82, 34, 28, fill=A(mix((90, 70, 50), FIRE_L, 0.3), 1))
    d.poly([(640 + 2.2 * 82, 820), (1120, 760), (1120, 1000), (640 + 2.2 * 82, 900)], A((60, 56, 38), 1))            # sleeves to the right edge
    for b in MG_BURSTS:   # tracers + brass casings (each casing: own lifetime, fades)
        u = (t - b) / 0.35
        tracer(d, mx, my, -100, my - 60 + 30 * hsh(int(b * 100), 1), u, FIRE_C, 1.0, 0.3, 7)
        v = (t - b) / 0.7
        if 0 <= v < 1:
            cx_ = 600 + 120 * v; cy_ = 920 + 200 * v + 500 * v * v
            d.rect(cx_ - 7, cy_ - 16, cx_ + 7, cy_ + 16, fill=A((230, 180, 80), 1 - eio(pr(v, 0.6, 1))), r=4)
    if fl > 0.01: glow(img, lambda g: g.circ(mx - 30, my, 60 + 90 * fl, fill=A(FIRE_C, fl)), blur=40)
    if t > t0 + 0.4: tag(d, 540, 560, ".50口径", FIRE_L, ap(t, t0 + 0.4, 0.25), 48)

def s_three(t, img, d):
    t0 = T["three"]; z = 1 + 0.05 * eio(pr(t, t0, nxt("three")))
    img.paste(vgrad((26, 30, 38), (18, 20, 26)))
    def P_(x, y): return (540 + (x - 540) * z, 820 + (y - 820) * z)
    d.rect(*P_(150, 330), *P_(930, 1260), fill=A((170, 176, 186), 1), r=20)
    for i in range(26):   # snow texture blots
        x, y = P_(180 + 720 * hsh(i, 1), 360 + 870 * hsh(i, 2)); d.ell(x, y, 40 * z, 14 * z, fill=A((196, 200, 208), 0.6))
    for i in range(22):   # woods (right)
        x, y = P_(760 + 150 * hsh(i, 3), 420 + 760 * hsh(i, 4)); d.circ(x, y, (22 + 12 * hsh(i, 5)) * z, fill=A((44, 62, 52), 1))
    for i in range(6):    # village (top-left)
        x, y = P_(230 + 50 * (i % 3), 400 + 50 * (i // 3)); d.rect(x - 16 * z, y - 16 * z, x + 16 * z, y + 16 * z, fill=A((110, 100, 96), 1), r=3)
    d.text(*P_(830, 380), "树林", int(40 * z), A((30, 40, 34), 1))
    d.text(*P_(285, 540), "霍茨维尔", int(36 * z), A((60, 50, 46), 1))
    cx, cy = P_(560, 820)
    glow(img, lambda g: g.circ(cx, cy, 70 * z, fill=A(FIRE, 0.9)), blur=40)
    d.rect(cx - 50 * z, cy - 26 * z, cx + 50 * z, cy + 26 * z, fill=A((70, 74, 50), 1), r=8)
    d.circ(cx, cy, 13 * z, fill=A(FIRE_L, 1))
    dirs = [((-1, 0), (180, 820)), ((0, -1), (520, 360)), ((0, 1), (520, 1230))]
    for i, ((ux, uy), (sx, sy)) in enumerate(dirs):
        s0 = THREE_ARROWS[i]
        if t < s0 - 0.05: continue
        u = eio(pr(t, s0, s0 + 0.35)); a_ = ap(t, s0, 0.12)
        ex = lerp(sx, 560 - ux * 150 + (40 if uy else 0), u); ey = lerp(sy, 820 - uy * 150, u)
        p0, p1 = P_(sx, sy), P_(ex, ey)
        d.line([p0, p1], A((80, 96, 120), a_), 22 * z)
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]); hl = 46 * z
        d.poly([(p1[0] + math.cos(ang) * hl, p1[1] + math.sin(ang) * hl), (p1[0] + math.cos(ang + 2.4) * hl, p1[1] + math.sin(ang + 2.4) * hl),
                (p1[0] + math.cos(ang - 2.4) * hl, p1[1] + math.sin(ang - 2.4) * hl)], A((80, 96, 120), a_))
        if t > s0 + 0.4:   # fire dashes toward him (continuous flow)
            for k in range(4):
                v = ((t * 1.8 + k / 4) % 1.0)
                q0 = (lerp(p1[0], cx, v), lerp(p1[1], cy, v)); q1 = (lerp(p1[0], cx, min(1, v + 0.08)), lerp(p1[1], cy, min(1, v + 0.08)))
                d.line([q0, q1], A((90, 110, 140), 0.8 * math.sin(math.pi * v)), 6)

def s_waver(t, img, d):
    t0 = T["waver"]
    sky(img, (10, 10, 16), (54, 36, 36), (0.5, (80, 44, 36)))
    soft_shape(img, lambda g: g.ell(540, 1040, 640, 300, fill=A(FIRE, 0.6)), blur=110)
    woods(d, 1020, (22, 20, 26), seed=3, hmin=110, hmax=190)
    snowfield(d, img, t, 1020, 540, 0.5, seed=4)
    g = 1 + 0.12 * eio(pr(t, t0, nxt("waver")))
    m = burning_m10(img, d, 540, 1090, 40 * g, t, flip=-1, seed=5)
    fl = flash_at(t, WAVER_BURSTS, 0.15)
    px, py = m.p(-1.2, -2.6)
    murphy_sil(img, d, px, py, 210 * g, t, flash=fl)
    for b in WAVER_BURSTS:
        for j in range(4): tracer(d, px + 26 * g, py - 100 * g, 540 + (j - 1.5) * 380, 1600, (t - b - j * 0.04) / 0.35, FIRE_C, 0.9, 0.25, 6)
    st = stepped(t, WAVER_STEPS, 0.3)
    for i in range(9):   # German infantry backing away toward the camera, one step per beat; fade as they reach the edge
        x0 = 120 + i * 105; y = 1150 + 45 * st + 20 * hsh(i, 8); hh = (90 + 40 * hsh(i, 9)) * (1 + 0.12 * st)
        x = x0 + (x0 - 540) * 0.08 * st
        inf_front(d, x, y, hh, t, step=0.25 * st + hsh(i, 10), key=FIRE_L, a=1 - eio(pr(st, 4.0, 5.0)) * 0.6, back=True)
    for i, (x0, s0) in enumerate(((210, 100), (880, 110))):   # tanks reversing toward us
        ger_tank(d, x0 + (x0 - 540) * 0.15 * st, 1240 + 50 * st, s0 * (1 + 0.15 * st), t, key=FIRE_L, rear=True)
    snowfall(d, t, 0.45, 45, seed=6)
    german_back(d, 120, 1750, 170, t, rim=FIRE_L, lean=-0.12 - 0.02 * st, seed=3)
    german_back(d, 960, 1780, 180, t, rim=FIRE_L, lean=0.12 + 0.02 * st, seed=4)

def s_hour(t, img, d):
    t0 = T["hour"]; en = nxt("hour")
    img.paste(vgrad((20, 18, 22), (12, 12, 14)))
    soft_shape(img, lambda g: g.ell(540, 800, 600, 500, fill=A(FIRE, 0.2)), blur=120)
    # left: dial 0 -> 60 min
    cx, cy, r = 330, 700, 150; u = eio(pr(t, t0 + 0.3, en - 1.0))
    d.circ(cx, cy, r + 14, fill=A((40, 40, 44), 1)); d.circ(cx, cy, r, fill=A((214, 206, 186), 1))
    ang0 = -math.pi / 2
    if u > 0:
        pts = [(cx, cy)] + [(cx + r * 0.92 * math.cos(ang0 + 2 * math.pi * u * k / 40), cy + r * 0.92 * math.sin(ang0 + 2 * math.pi * u * k / 40)) for k in range(41)]
        d.poly(pts, A(FIRE_L, 0.55))
    for k in range(12):
        a_ = ang0 + k * math.pi / 6; d.line([(cx + r * 0.8 * math.cos(a_), cy + r * 0.8 * math.sin(a_)), (cx + r * 0.93 * math.cos(a_), cy + r * 0.93 * math.sin(a_))], A((60, 50, 40), 1), 5)
    d.line([(cx, cy), (cx + r * 0.85 * math.cos(ang0 + 2 * math.pi * u), cy + r * 0.85 * math.sin(ang0 + 2 * math.pi * u))], A((40, 30, 24), 1), 8)
    d.circ(cx, cy, 12, fill=A((40, 30, 24), 1))
    d.text(cx, cy + r + 70, f"约{int(round(60 * u))}分钟", 50, A(WHITE, ap(t, t0 + 0.3, 0.3)))
    # right: ammo rounds vanish one by one (0.3 s fade each)
    bx = 740
    d.rect(bx - 120, 520, bx + 120, 890, fill=A((70, 74, 50), 1), r=10); d.rect(bx - 120, 520, bx + 120, 560, fill=A((90, 94, 64), 1), r=10)
    left = 0
    for i, s0 in enumerate(AMMO_OUT):
        a_ = 1 - eio(pr(t, s0, s0 + 0.3)); left += a_ > 0.5
        yy = 600 + i * 28
        if a_ > 0.01: d.rect(bx - 90, yy - 9, bx + 90, yy + 9, fill=A((220, 170, 70), a_), r=8); d.rect(bx + 60, yy - 9, bx + 90, yy + 9, fill=A((180, 120, 50), a_), r=6)
    d.text(bx, 950, str(left), 70, A(FIRE_L if left else (240, 120, 90), 1))
    # bottom: small figure on the vehicle with a bandaged leg (white wrap, no blood)
    m = m10(img, d, 560, 1250, 30, t, key=FIRE, flip=-1, star=False)
    px, py = m.p(-1.7, -1.8)
    murphy_side(img, d, px, py, 16, t, 1.0)
    d.rect(px - 9, py - 30, px + 9, py - 20, fill=A((236, 232, 222), 1), r=3)
    flames(img, d, *m.p(0.6, -1.75), 70, 70, t, 1.0, glow_on=False, seed=12)

def s_counter(t, img, d):
    """drawn facing RIGHT then mirrored, so the counter-attack heads LEFT (toward the enemy, consistent screen direction)."""
    t0 = T["counter"]
    lay = Image.new("RGB", (W, H)); dd = D(lay)
    lay.paste(vgrad((14, 16, 22), (40, 40, 46), mid=(0.55, (60, 50, 50))))
    soft_shape(lay, lambda g: g.ell(820, 1000, 500, 200, fill=A(FIRE, 0.3)), blur=100)
    woods(dd, 1100, (18, 22, 24), seed=41, x0=-60, x1=330, hmin=200, hmax=330)
    dd.poly([(-40, 1080), (1120, 1070), (1120, 1960), (-40, 1960)], A(SNOW, 1))
    go = t0 + 1.6; adv = max(0.0, t - go) * 70
    for i in range(6):   # comrades follow out of the woods (fade in from the trees)
        x = 120 + i * 85 + adv
        walker(dd, x, 1140 + 8 * hsh(i, 2), 22, t, i * 1.4, "us", key=FIRE_L, a=eio(pr(x, 150, 300)))
    # Murphy leading (bigger, nearer), medic beside him at first
    mx = 560 + adv * 1.1
    walker(dd, mx, 1330, 44, t if t > go else 0.0, 0.3, "us", key=FIRE_L)
    ma = 1 - eio(pr(t, go + 0.4, go + 1.0))
    if ma > 0.01:
        walker(dd, 470, 1290, 30, 0.0, 1.0, "us", key=COLD, a=ma)
        dd.rect(470 - 14, 1290 - 30 * 4.0, 470 + 14, 1290 - 30 * 3.5, fill=A((236, 232, 222), ma), r=4)
        dd.text(470, 1290 - 30 * 3.75, "+", 24, A((200, 50, 40), ma))
        if t < go: dd.line([(500, 1290 - 30 * 3.6), (mx - 30, 1300 - 32 * 3.4)], A(SKIN_M, ma), 9)
    for i in range(7):   # enemy far right, withdrawing into fog (fade)
        x = 860 + i * 40 + max(0, t - go - 0.5) * 50; a_ = 1 - eio(pr(t, go + 1.2 + i * 0.15, go + 2.4 + i * 0.15))
        inf_front(dd, x, 1100 + 10 * hsh(i, 3), 50, t, ph=i, key=COLD, a=a_ * 0.8, back=True)
    fog(lay, t, (70, 70, 80), 0.3, 12, 1000, 1180, 140, seed=16)
    snowfall(dd, t, 0.45, 45, seed=7)
    img.paste(ImageOps.mirror(lay))

def s_cite(t, img, d):
    t0 = T["cite"]
    img.paste(vgrad((18, 18, 22), (10, 10, 12)))
    soft_shape(img, lambda g: g.ell(540, 820, 560, 560, fill=A((255, 190, 120), 0.3)), blur=110)
    k = popk(t, t0 - 0.1); kk = min(1, k * 1.5); y0 = 340 + 50 * (1 - min(k, 1))
    d.rect(170, y0, 910, y0 + 880, fill=A((226, 216, 190), kk), r=12)
    d.rect(170, y0, 910, y0 + 70, fill=A((198, 180, 146), kk), r=12)
    ink = (64, 50, 36)
    d.text(540, y0 + 36, "MEDAL OF HONOR · CITATION", 30, A(ink, kk))
    medal_icon(d, 540, y0 + 200, 80, kk)
    n_lines = 14; typed = (t - t0 - 0.3) / 0.12
    for i in range(n_lines):   # greeked typed lines (shapes, not words)
        if typed <= i: break
        wl = 520 - 120 * hsh(i, 3) if i != 8 else 520; yy = y0 + 330 + i * 34
        if i == 8: continue
        d.rect(280, yy - 6, 280 + wl * min(1, typed - i), yy + 6, fill=A((150, 136, 112), 0.8), r=6)
    hy = y0 + 330 + 8 * 34; hs = t0 + 1.6
    if typed > 8:
        hw = eio(pr(t, hs, hs + 0.5))
        if hw > 0: d.rect(276, hy - 26, 276 + 540 * hw, hy + 26, fill=A(FIRE_L, 0.75), r=8)
        d.text(280, hy, "...he killed or wounded about 50.", 36, A((40, 28, 20), ap(t, t0 + 1.3, 0.2)), anchor="lm")
    tag(d, 540, y0 - 40, "嘉奖词", FIRE_L, ap(t, t0 + 0.2, 0.2), 40)
    d.text(540, y0 + 840, "CMOHS", 28, A((120, 100, 80), ap(t, t0 + 0.8, 0.3)))

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
    t0 = T["medal"]
    img.paste(vgrad((20, 18, 16), (10, 10, 12)))
    soft_shape(img, lambda g: g.ell(540, 820, 520, 520, fill=A(FIRE, 0.28)), blur=110)
    k = popk(t, t0 - 0.1); kk = min(1, k * 1.5)
    d.rect(170, 330 + 40 * (1 - min(k, 1)), 910, 1220, fill=A((26, 28, 30), 0.92 * kk), r=36)
    tag(d, 540, 420, "一句话学会", FIRE_L, kk, 40)
    drop = E.spring_at(t, t0 + 0.4, 0, 1, "bouncy") if t >= t0 + 0.4 else 0
    my = 560 + 230 * min(drop, 1.2)
    if drop > 0: medal_icon(d, 540, my, 190, ap(t, t0 + 0.4, 0.15))
    for i in range(6):   # sparkle glints (continuous)
        u = (t * 0.6 + i / 6) % 1.0; sx = 540 + 200 * math.cos(i * 1.05); sy = 860 + 200 * math.sin(i * 1.05)
        if drop > 0.5: d.circ(sx, sy, 4 + 6 * math.sin(math.pi * u), fill=A(FIRE_C, math.sin(math.pi * u) * 0.8))
    if t > t0 + 1.4: d.text(540, 1130, "美军最高英勇勋章", 62, A(WHITE, ap(t, t0 + 1.4, 0.3)))

def s_scared(t, img, d):
    t0 = T["scared"]
    img.paste(vgrad((8, 12, 22), (16, 20, 30), mid=(0.5, (24, 32, 48))))
    soft_shape(img, lambda g: g.ell(140, 300, 360, 300, fill=A((150, 180, 230), 0.25)), blur=110)   # moonlight, upper-left, off the face
    z = 1 + 0.03 * eio(pr(t, t0 - 0.3, nxt("scared")))
    murphy_face(img, d, 540, 860, 480 * z, t, key=(170, 196, 236), rim=(255, 170, 110), squint=0.1, worry=0.8, look=-0.6, blink=(t0 + 2.0 < t < t0 + 2.12))
    for i in range(3):   # breath vapour, continuous puffs
        u = ((t - t0) * 0.5 + i / 3) % 1.0
        d.circ(540 - 0.45 * 480 - 160 * u, 860 + 0.62 * 480 - 50 * u, 25 + 60 * u, fill=A((200, 214, 236), 0.22 * math.sin(math.pi * u)))
    d.poly(spline([(-60, 1500), (300, 1440), (780, 1460), (1140, 1420), (1140, 1960), (-60, 1960)], n=4), A((30, 28, 30), 1))   # foxhole lip
    d.poly(spline([(-60, 1500), (300, 1440), (780, 1460), (1140, 1420), (1140, 1470), (-60, 1530)], n=4), A((120, 130, 150), 1))
    snowfall(d, t, 0.55, 60, seed=9, speed=40)

def s_friends(t, img, d):
    t0 = T["friends"]
    sky(img, (10, 10, 16), (54, 36, 36), (0.55, (84, 46, 36)))
    soft_shape(img, lambda g: g.ell(540, 1150, 700, 300, fill=A(FIRE, 0.55)), blur=110)
    woods(d, 1060, (20, 22, 26), seed=51, hmin=330, hmax=470, lit=(110, 70, 50))
    for i in range(9):   # friends' helmets in the woods, appearing one by one (fade-in)
        a_ = ap(t, t0 + 0.3 + i * 0.12, 0.35); x = 130 + i * 105 + 20 * hsh(i, 1); y = 1050 - 30 * hsh(i, 2)
        if a_ > 0: m1_front(d, x, y, 46, FIRE_L, a_)
    snowfield(d, img, t, 1060, 540, 0.5, seed=6)
    m = burning_m10(img, d, 540, 1300, 58, t, flip=-1, fire=0.85, seed=6)
    px, py = m.p(-1.2, -2.6)
    murphy_sil(img, d, px, py, 330 * (1 + 0.04 * eio(pr(t, t0, nxt("friends")))), t, flash=0.0)
    snowfall(d, t, 0.45, 45, seed=10)

def s_end(t, img, d):
    t0 = T["end"]
    img.paste(vgrad((14, 12, 16), (10, 10, 12)))
    soft_shape(img, lambda g: g.ell(540, 260, 500, 160, fill=A(FIRE, 0.3)), blur=90)
    a0 = ap(t, t0, 0.3)
    m = m10(img, d, 560, 470, 14, t, key=FIRE, flip=-1, star=False)
    px, py = m.p(-1.2, -2.6); murphy_sil(img, d, px, py, 70, t)
    flames(img, d, *m.p(0.6, -1.75), 36, 36, t, 1.0, glow_on=False, seed=13)
    for i, (x, lab, s0) in enumerate(((330, "A", t0 + 0.6), (750, "B", t0 + 1.6))):
        k = popk(t, s0, "bouncy")
        if k <= 0: continue
        a_ = ap(t, s0, 0.12); sc = 0.7 + 0.3 * min(k, 1.1)
        d.rect(x - 175, 620, x + 175, 1120, fill=A((30, 30, 34), 0.95 * a_), r=30)
        d.text(x, 700, lab, int(90 * sc), A(FIRE_L, a_))
        if i == 0:   # shield (fearless)
            sh = [(x - 90, 800), (x + 90, 800), (x + 80, 920), (x, 1010), (x - 80, 920)]
            d.poly(xf([(px_ - x, py_ - 900) for px_, py_ in sh], x, 900, sc), A((120, 140, 170), a_))
        else:        # heart with a small tremble line (afraid, but holds on)
            hs = xf(spline([(0, -40), (45, -95), (100, -40), (0, 70), (-100, -40), (-45, -95)], n=6), x, 920, sc)
            d.poly(hs, A((230, 110, 80), a_))
            for j in range(3): d.line([(x - 150 + j * 8, 840 + j * 20), (x - 130 + j * 8, 830 + j * 20)], A(WHITE, 0.5 * a_), 4)
    if t > t0 + 2.6: d.text(540, 1200, "评论区聊聊", 52, A(FIRE_L, ap(t, t0 + 2.6, 0.3)))

def s_stub(t, img, d): img.paste(vgrad((14, 18, 20), (10, 10, 10)))

SCN = {"hook": s_hook, "who": s_who, "attack": s_attack, "retreat": s_retreat, "hit": s_hit, "big2": s_big2, "danger": s_danger,
       "mg": s_mg, "three": s_three, "waver": s_waver, "hour": s_hour, "counter": s_counter, "cite": s_cite, "medal": s_medal,
       "scared": s_scared, "friends": s_friends, "end": s_end}
XF = {k: 0.35 for k in SCN}; XF["hook"] = 0; XF["big2"] = 0
FACE_KEYS = {"who", "danger", "scared"}
SECS = [(max(-1, a if i else -1), b, k) for i, (a, b, s, k) in enumerate(SUBS)]
def scene_at(t):
    for i, (a, b, k) in enumerate(SECS):
        if a <= t < b: return i
    return len(SECS) - 1
def render_scene(k, t):
    img = Image.new("RGB", (W, H), (10, 10, 10)); d = D(img); SCN.get(k, s_stub)(t, img, d); return img
def cam(t):
    z = 1.0 + 0.04 * pulse(t, [0.0, BIG2], 3)
    sx, sy = E.shake(t, 0.0, 8, 0.4) if t < BIG2 else E.shake(t, BIG2, 8, 0.4)
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
    s = "Vibe 知识大赏 · 超级士兵 No.03"; w = d.tlen(s, 28) + 50
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
    if BIG2 <= t < BIG2 + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - (t - BIG2) / 0.1)))
    subtitle(d, t); ui(d, t)
    img = img.resize((OW, OH), Image.LANCZOS)
    img = E.vignette(img, 0.3, 0.5); img = E.grain(img, 0.03, seed=fi)
    return img

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "test":
        for s_ in sys.argv[2:]: frame(float(s_), int(float(s_) * 30)).save(f"/tmp/mu_test_{s_}.png")
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
