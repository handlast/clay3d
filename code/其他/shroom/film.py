import sys, subprocess
from fx import *
from cues import *

CAP = (176, 84, 52); CAP_L = (214, 122, 80); STEM = (238, 198, 92); STEM_D = (206, 160, 64); PORE = (240, 176, 56)
BRU = (50, 100, 210); SKIN = (255, 214, 178); SOUP = (240, 170, 70); PINK = (255, 150, 190)
ELF = [(255, 90, 110), (90, 200, 255), (130, 230, 110), (255, 200, 60), (190, 130, 255), (255, 140, 60)]
GOOD = (110, 225, 130); BAD = (255, 80, 70); NAVYT = (24, 20, 40)
rnd = random.Random(5)

# ---------------- characters ----------------
def shroom(d, x, y, s, mood, t, a=1.0, blue=0.0, bpos=(0.12, -0.45), sq=0.0, look=0.0):
    wob = math.sin(t * 3) * s * 0.02
    d.ell(x, y, s * 0.7, s * 0.1, A((0, 0, 0), 0.22 * a))
    h = s * (1 - sq)
    d.rect(x - s * 0.34 * (1 + sq), y - h, x + s * 0.34 * (1 + sq), y, fill=A(STEM, a), r=s * 0.26)
    d.rect(x + s * 0.12, y - h * 0.9, x + s * 0.3 * (1 + sq), y - s * 0.06, fill=A(STEM_D, 0.6 * a), r=s * 0.14)
    d.rect(x - s * 0.26, y - h * 0.85, x - s * 0.16, y - s * 0.2, fill=A(WHITE, 0.35 * a), r=s * 0.05)
    if blue > 0:
        bx, by = x + bpos[0] * s, y + bpos[1] * s
        glow(d, bx, by, s * 0.5 * blue, BRU, 0.6 * a)
        d.circ(bx, by, s * 0.24 * blue, fill=A(BRU, 0.92 * a)); d.circ(bx - s * 0.05, by - s * 0.05, s * 0.07 * blue, fill=A((120, 170, 255), 0.7 * a))
    top = y - h - s * 0.62 + wob
    d.ell(x, y - h + s * 0.05 + wob, s * 0.82, s * 0.14, A(PORE, a))
    d.d.chord((P(x - s * 0.88), P(top), P(x + s * 0.88), P(y - h + s * 0.62 + wob)), 180, 360, fill=A(CAP, a))
    d.ell(x - s * 0.35, top + s * 0.25, s * 0.26, s * 0.1, A(CAP_L, 0.8 * a))
    d.ell(x - s * 0.42, top + s * 0.2, s * 0.1, s * 0.04, A(WHITE, 0.5 * a))
    for i, (sx, sy) in enumerate([(0.2, 0.2), (0.48, 0.42), (-0.05, 0.45)]):
        d.ell(x + sx * s, top + sy * s, s * 0.07, s * 0.04, A(CAP_L, 0.7 * a))
    face(d, x, y - h * 0.5, s * 0.42, mood, a, look)

def tiny(d, x, y, s, ci, t, ph=0.0, walk=1.0, a=1.0, clown=False, flip=1, arms=0.0, mood="happy"):
    col = ELF[ci % 6]; hat = ELF[(ci + 2) % 6]; dark = mix(col, (0, 0, 0), 0.35)
    st = math.sin(t * 12 + ph) * walk; bob = abs(st) * s * 0.05
    yb = y - bob
    for sgn in (-1, 1):
        d.line([(x + sgn * s * 0.07, yb - s * 0.28), (x + sgn * s * 0.07 + sgn * st * s * 0.09, y)], A(dark, a), s * 0.075)
    d.poly([(x - s * 0.21, yb - s * 0.24), (x + s * 0.21, yb - s * 0.24), (x + s * 0.12, yb - s * 0.6), (x - s * 0.12, yb - s * 0.6)], A(col, a))
    d.poly([(x - s * 0.18, yb - s * 0.26), (x - s * 0.08, yb - s * 0.26), (x - s * 0.06, yb - s * 0.56), (x - s * 0.1, yb - s * 0.56)], A(WHITE, 0.25 * a))
    sw = math.sin(t * 12 + ph + 1.5) * walk * 0.5 + arms
    for sgn in (-1, 1):
        d.line([(x + sgn * s * 0.12, yb - s * 0.54), (x + sgn * s * 0.26, yb - s * 0.36 - sgn * sw * s * 0.18 - arms * s * 0.25)], A(col, a), s * 0.06)
    hy = yb - s * 0.73
    d.circ(x, hy, s * 0.16, fill=A(SKIN, a))
    d.circ(x - s * 0.055, hy - s * 0.01, s * 0.022, fill=A(INK, a)); d.circ(x + s * 0.055, hy - s * 0.01, s * 0.022, fill=A(INK, a))
    if mood == "scream": d.ell(x, hy + s * 0.07, s * 0.04, s * 0.05, A(INK, a))
    else: d.arc(x, hy + s * 0.03, s * 0.06, s * 0.05, 20, 160, A(INK, a), max(1, s * 0.02))
    if clown:
        d.circ(x, hy + s * 0.02, s * 0.04, fill=A(BAD, a))
        for sgn in (-1, 1): d.circ(x + sgn * s * 0.15, hy - s * 0.08, s * 0.07, fill=A(hat, a))
        d.circ(x, hy - s * 0.2, s * 0.05, fill=A(hat, a))
    else:
        d.poly([(x - s * 0.18, hy - s * 0.08), (x + s * 0.18, hy - s * 0.08), (x + flip * s * 0.16, hy - s * 0.42)], A(hat, a))
        d.circ(x + flip * s * 0.16, hy - s * 0.42, s * 0.045, fill=A(WHITE, a))

def crowd(n, seed):
    r = random.Random(seed)
    return [dict(x=r.uniform(200, 880), y=r.uniform(0, 1), s=r.uniform(0.7, 1.3), ci=r.randrange(6), ph=r.uniform(0, 6), clown=r.random() < 0.3,
                 v=r.uniform(40, 110) * r.choice([-1, 1]), ang=r.uniform(0, 2 * math.pi), sp=r.uniform(500, 1100)) for _ in range(n)]
CR1 = crowd(34, 3); CR2 = crowd(26, 8); CR3 = crowd(18, 12)

def tag(d, x, y, s, col, a=1.0, size=40, tc=NAVYT):
    if a <= 0.01: return
    w = d.tlen(s, size, 1) + 44
    d.rect(x - w / 2, y - size * 0.78, x + w / 2, y + size * 0.78, fill=A(col, 0.95 * a), r=size * 0.6)
    d.text(x, y, s, size, A(tc, a), k=1)
def popk(t, t0): return min(1, back(pr(t, t0, t0 + 0.2)))
def bubble(d, x, y, s, side, col, tcol, a, size=44):
    if a <= 0: return
    w = d.tlen(s, size, 1) + 60; x0 = x if side < 0 else x - w
    d.rect(x0, y - 48, x0 + w, y + 48, fill=A(col, a), r=36)
    tx = x0 + 40 if side < 0 else x0 + w - 40
    d.poly([(tx - 14, y + 36), (tx - (22 if side < 0 else -22), y + 78), (tx + 14, y + 36)], A(col, a))
    d.text(x0 + w / 2, y, s, size, A(tcol, a), k=1)
def dots(d, t, col, a=0.3, n=30):
    for i in range(n):
        u = (t * 0.15 + i / n) % 1
        x = (i * 211) % 1080; y = 1900 - u * 2000
        d.circ(x, y, 5 + i % 5, fill=A(col, a * math.sin(u * math.pi)))
def swirl(d, t, c1, c2, cx=540, cy=900):
    grad(d, c1, c2)
    for i in range(9):
        r = ((t * 120 + i * 140) % 1300)
        d.circ(cx, cy, r, outline=A(mix(c1, WHITE, 0.25), 0.18 * (1 - r / 1300)), w=40)

# ---------------- scenes ----------------
def s_hook(t, d):
    if t < HOOK_HIT: grad(d, (60, 30, 90), (30, 16, 50))
    else: rays(d, t, (150, 60, 200), (90, 30, 140), n=20, cx=540, cy=980)
    k = t - HOOK_HIT
    sq = 0.25 * math.exp(-max(k, 0) * 8) * math.sin(max(k, 0) * 40) if k > 0 else -0.08 * pr(t, 0, HOOK_HIT)
    if k > 0: glow(d, 540, 820, 420, YEL, 0.35 * pulse(t, [HOOK_HIT], 2.5))
    for p in CR1:
        if k <= 0: break
        u = min(k, 0.7)
        sx = 540 + math.cos(p["ang"]) * p["sp"] * u * 0.55; sy = 760 - math.sin(abs(p["ang"])) * p["sp"] * u * 0.6 + 1400 * u * u
        land = 960 + p["y"] * 230
        if k > 0.7 or sy > land:
            sx = 540 + math.cos(p["ang"]) * p["sp"] * 0.385 + p["v"] * (k - 0.7) if k > 0.7 else sx; sy = land
            sx = 200 + (sx - 200) % 680
        tiny(d, sx, min(sy, land), 70 * p["s"], p["ci"], t, p["ph"], 1.0 if sy >= land else 0.0, clown=p["clown"], flip=1 if p["v"] > 0 else -1, arms=0 if sy >= land else 0.8)
    shroom(d, 540, 1150, 330, "proud" if k > 0 else "sus", t, sq=sq)
    sparks(d, 540, 700, t, HOOK_HIT, 60, 1300, YEL, 1, 3)
    d.text(540, 330, "吃了它", 100, A(WHITE, ease(pr(t, 0, 0.15))), k=1)
    stamp(d, t, HOOK_HIT, "看见小人？", 540, 520, 140, YEL)

def mountains(d, t, c1, c2):
    for i, (x, h, c) in enumerate([(200, 520, c1), (560, 640, c2), (900, 480, c1), (380, 380, c2), (760, 400, c1)]):
        d.poly([(x - 420, 1100), (x, 1100 - h), (x + 420, 1100)], A(c, 1))
        d.poly([(x - 60, 1100 - h + 90), (x, 1100 - h), (x + 60, 1100 - h + 90)], A(WHITE, 0.5))
def wok(d, x, y, s, t, fire=1.0):
    for i in range(7):
        fx_ = x - s * 0.6 + i * s * 0.2; fh = s * (0.35 + 0.15 * math.sin(t * 17 + i * 1.7)) * fire
        d.poly([(fx_ - s * 0.1, y + s * 0.35), (fx_ + s * 0.1, y + s * 0.35), (fx_ + s * 0.02 * math.sin(t * 11 + i), y + s * 0.35 - fh)], A((255, 140 + i % 3 * 30, 40), 0.9))
    glow(d, x, y + s * 0.2, s * 0.9, (255, 150, 50), 0.35 * fire)
    d.d.chord((P(x - s), P(y - s * 0.55), P(x + s), P(y + s * 0.4)), 0, 180, fill=A((50, 52, 62), 1))
    d.ell(x, y - s * 0.07, s, s * 0.12, A((80, 84, 96), 1))
    d.rect(x + s * 0.95, y - s * 0.12, x + s * 1.45, y - s * 0.02, fill=A((90, 60, 40), 1), r=s * 0.05)
def slice_(d, x, y, s, rot, blue=0.0, a=1.0):
    d.ell(x, y, s, s * 0.55, A(mix((250, 220, 120), BRU, blue), a)); d.ell(x - s * 0.3, y - s * 0.15, s * 0.3, s * 0.12, A(WHITE, 0.4 * a))
def s_yun(t, d):
    grad(d, (110, 200, 255), (200, 240, 255))
    glow(d, 800, 330, 160, (255, 240, 160), 0.6); d.circ(800, 330, 70, fill=A((255, 236, 140), 1))
    mountains(d, t, (70, 170, 110), (50, 140, 90))
    d.rect(-40, 1100, 1120, 1500, fill=A((96, 190, 110), 1))
    wok(d, 540, 960, 260, t)
    for i, h in enumerate(WOK_POP):
        u = t - h
        if u > 0:
            ph = u % 0.8; yy = 900 - math.sin(ph / 0.8 * math.pi) * 180
            slice_(d, 420 + i * 120, yy, 46, 0)
    for i, p in enumerate(CR2[:5]):
        x = 230 + i * 150; tiny(d, x, 1150 + (i % 2) * 30, 60, p["ci"], t, p["ph"], 0.3, clown=p["clown"])
    stamp(d, t, YUN_HIT, "云南 · 菌子季", 540, 420, 100, NAVYT)
    if t > YUN_HIT + 0.6: tag(d, 540, 580, "吃菌子 = 见小人？", (255, 214, 64), ease(pr(t, YUN_HIT + 0.6, YUN_HIT + 0.9)), 50)

def finger(d, x, y, s, a=1.0):
    d.rect(x, y - s * 0.3, x + s * 4, y + s * 0.3, fill=A(SKIN, a), r=s * 0.3)
    d.rect(x + s * 0.06, y - s * 0.22, x + s * 0.5, y + s * 0.22, fill=A((255, 236, 220), a), r=s * 0.18)
    d.rect(x + s * 0.8, y - s * 0.3, x + s * 4, y - s * 0.18, fill=A((0, 0, 0), 0.06 * a))
def s_bruise(t, d):
    swirl(d, t, (255, 196, 90), (250, 140, 60))
    pk = eio(pr(t, BRUISE, TOUCH)) * (1 - eio(pr(t, TOUCH + 0.4, TOUCH + 0.9)))
    blue = ease(pr(t, TOUCH, TOUCH + 0.9))
    shroom(d, 470, 1150, 340, "scared" if t > TOUCH else "chill", t, blue=blue, bpos=(0.2, -0.16), look=0.6)
    finger(d, lerp(1100, 470 + 0.2 * 340 + 40, pk), 1150 - 0.16 * 340, 70)
    rings(d, 538, 1096, t, [TOUCH], BRU, 0.8, 260)
    stamp(d, t, NAME_HIT, "见手青", 540, 340, 150, NAVYT)
    if t > NAME_HIT + 0.5: tag(d, 540, 520, "一碰就变青", BRU, ease(pr(t, NAME_HIT + 0.5, NAME_HIT + 0.8)), 52, WHITE)

def land(d, pts, col):
    for (x, y, rx, ry) in pts: d.ell(x, y, rx, ry, A(col, 1))
def pin(d, x, y, t, t0, label, lx, ly):
    k = back(pr(t, t0, t0 + 0.25))
    if k <= 0: return
    yy = y - 60 * k
    glow(d, x, y, 90, BAD, 0.4 * pulse(t, [t0], 3))
    d.circ(x, yy - 30, 34 * k, fill=A(BAD, 1)); d.poly([(x - 26 * k, yy - 14), (x + 26 * k, yy - 14), (x, y)], A(BAD, 1)); d.circ(x, yy - 32, 13 * k, fill=A(WHITE, 1))
    tag(d, lx, ly, label, WHITE, min(1, k), 38)
    tiny(d, x + 50, y + 10, 50, int(t0 * 3), t, t0, 0.6)
def s_map(t, d):
    grad(d, (40, 110, 200), (20, 60, 140))
    for i in range(10):
        y = 300 + i * 100 + 10 * math.sin(t * 2 + i); d.line([(200 + (i * 70) % 200, y), (320 + (i * 70) % 200, y)], A(WHITE, 0.15), 4)
    land(d, [(260, 520, 200, 170), (380, 470, 160, 110), (220, 700, 120, 90)], (110, 200, 120))
    land(d, [(640, 740, 40, 70), (670, 840, 30, 55), (690, 910, 34, 40)], (110, 200, 120))
    land(d, [(780, 1020, 130, 50), (700, 1000, 60, 30)], (110, 200, 120))
    pin(d, 290, 660, t, PINS[0], "云南", 290, 820)
    pin(d, 660, 800, t, PINS[1], "菲律宾", 520, 930)
    pin(d, 790, 1010, t, PINS[2], "新几内亚", 760, 1110)
    if t > FAR_HIT:
        k = ease(pr(t, FAR_HIT, FAR_HIT + 0.5))
        for (a_, b_) in [((290, 600), (660, 740)), ((660, 740), (790, 950))]:
            n = 16
            for i in range(int(n * k)):
                u = i / n; px = lerp(a_[0], b_[0], u); py = lerp(a_[1], b_[1], u) - math.sin(u * math.pi) * 80
                d.circ(px, py, 6, fill=A(YEL, 0.9))
    stamp(d, t, FAR_HIT, "看见同样的小人", 540, 330, 92, YEL)

def ruler(d, x, y0, y1, a=1.0):
    d.rect(x - 40, y1 - 10, x + 40, y0 + 10, fill=A((255, 236, 150), a), r=8)
    for cm in range(0, 31):
        yy = lerp(y0, y1, cm / 30); L = 34 if cm % 5 == 0 else 16
        d.line([(x - 40, yy), (x - 40 + L, yy)], A((90, 70, 30), a), 3)
        if cm % 10 == 0: d.text(x + 14, yy, str(cm), 26, A((90, 70, 30), a), k=1)
def s_ruler(t, d):
    grad(d, (255, 120, 150), (230, 80, 120)); dots(d, t, WHITE, 0.25)
    d.rect(-40, 1150, 1120, 1500, fill=A((200, 60, 100), 1))
    ruler(d, 230, 1150, 520)
    px_cm = 630 / 30
    if t < KIND:
        tiny(d, 330, 1150, 30 * px_cm * ease(pr(t, SIZE_HITS[0], SIZE_HITS[0] + 0.3)) + 1, 1, t, 0, 0.2)
        tiny(d, 420, 1150, 3 * px_cm * 1.0, 3, t, 1, 1.0)
        d.text(330, 470, "30 cm", 40, A(WHITE, ease(pr(t, SIZE_HITS[0], SIZE_HITS[0] + 0.3))), k=1)
        n = int(120 * ease(pr(t, SIZE_HITS[1], SIZE_HITS[1] + 0.7)))
        for i in range(min(n, 60)):
            x = 480 + (i * 37) % 420; yy = 1150 + (i // 12) * 0 - (i % 3) * 6
            tiny(d, x, 1150 + (i % 4) * 30, 40 + (i * 13) % 40, i, t, i * 0.7, 1.0, clown=i % 3 == 0)
        if t > SIZE_HITS[1]: stamp(d, t, SIZE_HITS[1], f"×{max(n,1)}", 640, 560, 150, YEL)
        stamp(d, t, SIZE_HITS[0], "3–30 厘米", 560, 300, 100, WHITE)
    else:
        for i, p in enumerate(CR2[:14]):
            x = 360 + (i % 5) * 120; y = 900 + (i // 5) * 140
            tiny(d, x, y, 110, p["ci"], t, p["ph"], 0.6, clown=(i % 2 == 1), arms=0.5 * math.sin(t * 6 + i))
        stamp(d, t, KIND_HITS[0], "精灵", 420, 360, 120, WHITE)
        stamp(d, t, KIND_HITS[1], "小丑", 700, 520, 120, YEL)
        if t > KIND_HITS[1] + 0.3: tag(d, 540, 680, "九成长这样", WHITE, ease(pr(t, KIND_HITS[1] + .3, KIND_HITS[1] + .6)), 46)

def cup(d, x, y, s):
    d.ell(x, y, s * 0.6, s * 0.12, A((0, 0, 0), 0.2))
    d.rect(x - s * 0.5, y - s * 1.1, x + s * 0.5, y, fill=A((240, 244, 250), 1), r=s * 0.12)
    d.rect(x + s * 0.2, y - s * 1.0, x + s * 0.4, y - s * 0.1, fill=A((200, 210, 225), 0.6), r=s * 0.08)
    d.arc(x + s * 0.55, y - s * 0.6, s * 0.22, s * 0.25, 270, 90, A((240, 244, 250), 1), s * 0.09)
    d.ell(x, y - s * 1.1, s * 0.5, s * 0.1, A((150, 90, 50), 1))
def s_table(t, d):
    grad(d, (60, 180, 170), (30, 120, 130))
    d.rect(-40, 1000, 860, 1060, fill=A((180, 120, 70), 1)); d.rect(-40, 1060, 860, 1110, fill=A((130, 84, 50), 1))
    d.rect(-40, 900, 860, 1000, fill=A((206, 146, 90), 1))
    cup(d, 470, 975, 200)
    u = t - TABLE
    for i in range(5):  # walkers: go around the cup (behind it, up the table)
        x = 200 + ((u * 110 + i * 120) % 520)
        dy = -60 * math.exp(-((x - 470) / 90) ** 2)
        tiny(d, x, 990 + dy - (i % 2) * 10, 66, i + 1, t, i, 1.0)
    fx_ = 600 + (t - TABLE) * 160
    if t < FALL:
        tiny(d, min(fx_, 850), 990, 70, 0, t, 2, 1.0)
    else:
        k = t - FALL; tiny(d, 850 + k * 120, 990 + 1600 * k * k, 70, 0, t, 2, 0.0, arms=1.0, mood="scream")
        stamp(d, t, FALL + 0.1, "啊——", 760, 760, 80, WHITE)
    stamp(d, t, TABLE + 0.3, "会绕路", 360, 420, 110, WHITE)
    if t > FALL: stamp(d, t, FALL, "会摔跤", 600, 580, 110, YEL)
    if t >= SIL0: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.6))

def bowl(d, x, y, s, t):
    d.d.chord((P(x - s), P(y - s * 0.8), P(x + s), P(y + s * 0.8)), 0, 180, fill=A((250, 250, 245), 1))
    d.d.chord((P(x - s * 0.9), P(y - s * 0.6), P(x + s * 0.9), P(y + s * 0.7)), 0, 180, fill=A((225, 230, 240), 0.5))
    d.ell(x, y, s, s * 0.22, A((235, 240, 245), 1)); d.ell(x, y + 6, s * 0.92, s * 0.18, A(SOUP, 1))
    for i in range(5):
        xx = x - s * 0.6 + i * s * 0.3; d.ell(xx + 10 * math.sin(t * 2 + i), y + 6, s * 0.06, s * 0.025, A((255, 210, 120), 0.8))
    for i in range(4):
        sx = x - s * 0.5 + i * s * 0.33
        d.line([(sx + 20 * math.sin(t * 2 + i + yy / 60), yy) for yy in range(int(y - s * 0.8), int(y - 20), 20)], A(WHITE, 0.25), 10)
def spoon(d, x, y, s, a=1.0):
    d.line([(x, y), (x + s * 2.2, y - s * 1.5)], A((210, 214, 225), a), s * 0.16)
    d.ell(x, y, s * 0.55, s * 0.32, A((210, 214, 225), a)); d.ell(x, y + 4, s * 0.44, s * 0.22, A(SOUP, a))
def s_soup(t, d):
    rays(d, t, (255, 190, 80), (240, 130, 50), n=20, cx=540, cy=1000)
    bowl(d, 540, 1000, 340, t)
    k = t - SOUP_HIT
    sx, sy = 700, 620
    spoon(d, sx, sy, 160)
    for i in range(7):
        ph = i * 0.11
        if k < ph: tiny(d, sx - 80 + i * 26, sy - 10, 46, i, t, i, 0.0); continue
        u = min((k - ph) / 0.55, 1)
        tx = 380 + i * 50; ty = 1010
        if u < 1:
            x = lerp(sx - 80 + i * 26, tx, u); y = lerp(sy - 10, ty, u) - math.sin(u * math.pi) * 260
            tiny(d, x, y, 46, i, t, i, 0.0, arms=1.0)
        else:  # swimming: head + waving arm above the soup
            bx = tx + 20 * math.sin(t * 3 + i); by = ty - 8 + 6 * math.sin(t * 6 + i)
            d.circ(bx, by - 12, 10, fill=A(SKIN, 1)); d.poly([(bx - 10, by - 18), (bx + 10, by - 18), (bx + 6, by - 44)], A(ELF[(i + 2) % 6], 1))
            ang = math.sin(t * 8 + i) * 0.8
            d.line([(bx + 8, by - 6), (bx + 8 + math.cos(ang - 1.2) * 24, by - 6 + math.sin(ang - 1.2) * 24)], A(ELF[i % 6], 1), 5)
            d.ell(bx, by + 2, 20, 5, A(WHITE, 0.5))
    for i in range(7): sparks(d, 380 + i * 50, 1000, t, SOUP_HIT + i * 0.11 + 0.55, 10, 500, (255, 230, 150), 1, i, 0.6)
    stamp(d, t, SOUP_HIT, "在汤里游泳！", 540, 360, 120, NAVYT)

def s_mouth(t, d):
    grad(d, (255, 214, 178), (240, 180, 150))
    for sgn in (-1, 1):
        ex = 540 + sgn * 210
        d.circ(ex, 420, 110, fill=A(WHITE, 1)); d.circ(ex + 20 * math.sin(t * 3), 440, 50, fill=A(INK, 1)); d.circ(ex - 12, 420, 14, fill=A(WHITE, 1))
        d.line([(ex - 100, 270 - sgn * 20), (ex + 100, 270 + sgn * 20)], A((120, 80, 60), 1), 22)
    ok = back(pr(t, MOUTH, MOUTH + 0.3))
    d.ell(540, 900, 330 * ok + 1, 300 * ok + 1, A((120, 30, 50), 1))
    d.rect(300, 640, 780, 700, fill=A(WHITE, 1 if ok > 0.5 else 0), r=20)
    d.ell(540, 1090, 220 * ok + 1, 110 * ok + 1, A(TONGUE, 1))
    for i in range(6):
        bx = 340 + i * 80 + 20 * math.sin(t * 2 + i); by = 960 + 30 * math.sin(t * 3 + i * 1.3)
        if t < MOUTH_HIT - 0.1: continue
        d.circ(bx, by - 16, 14, fill=A(SKIN, 1)); d.poly([(bx - 14, by - 26), (bx + 14, by - 26), (bx + 8, by - 64)], A(ELF[(i + 2) % 6], 1))
        ang = math.sin(t * 8 + i) * 0.8
        d.line([(bx + 10, by - 6), (bx + 10 + math.cos(ang - 1.2) * 34, by - 6 + math.sin(ang - 1.2) * 34)], A(ELF[i % 6], 1), 7)
        d.ell(bx, by + 4, 28, 7, A(PINK, 0.6))
    stamp(d, t, MOUTH_HIT, "嘴里还有！", 540, 1150, 100, NAVYT)

def scientist(d, x, y, s, mood, t, a=1.0):
    bob = math.sin(t * 3) * s * 0.03
    d.ell(x, y, s * 0.6, s * 0.1, A((0, 0, 0), 0.2 * a))
    d.d.chord((P(x - s * 0.62), P(y - s * 1.4 + bob), P(x + s * 0.62), P(y + s * 0.3)), 180, 360, fill=A((245, 245, 245), a))
    d.rect(x - s * 0.62, y - s * 0.55 + bob, x + s * 0.62, y, fill=A((245, 245, 245), a))
    d.line([(x, y - s * 0.75 + bob), (x, y)], A((200, 200, 205), a), s * 0.03)
    d.circ(x, y - s * 1.15 + bob, s * 0.45, fill=A((250, 210, 170), a))
    d.d.chord((P(x - s * 0.47), P(y - s * 1.65 + bob), P(x + s * 0.47), P(y - s * 0.95 + bob)), 180, 360, fill=A((200, 200, 205), a))
    face(d, x, y - s * 1.15 + bob, s * 0.45, mood, a)
    for sgn in (-1, 1): d.circ(x + sgn * s * 0.16, y - s * 1.2 + bob, s * 0.12, outline=A((60, 60, 70), a), w=s * 0.025)
    tx, ty = x + s * 0.75, y - s * 0.7 + bob
    d.rect(tx - s * 0.08, ty - s * 0.45, tx + s * 0.08, ty + s * 0.1, fill=A((220, 240, 255), 0.8 * a), r=s * 0.07)
    d.rect(tx - s * 0.07, ty - s * 0.1, tx + s * 0.07, ty + s * 0.09, fill=A((150, 110, 200), a), r=s * 0.06)
def s_arch(t, d):
    grad(d, (230, 205, 160), (200, 170, 120))
    d.rect(220, 330, 860, 760, fill=A((250, 240, 215), 1), r=10)
    d.text(540, 390, "1934 · 巴布亚新几内亚", 40, A((110, 80, 50), 1), k=1)
    d.text(540, 450, "\"mushroom madness\"", 40, A((110, 80, 50), 1))
    for i in range(5): d.rect(270, 490 + i * 46, 270 + (420 + (i * 97) % 160), 504 + i * 46, fill=A((170, 140, 100), 0.7), r=6)
    for i in range(4):
        x = 300 + i * 150; tiny(d, x, 740, 50, i, t, i, 0.0, a=0.6)
    stamp(d, t, ARCH_HIT, "1934", 540, 270, 100, BAD)
    scientist(d, 400, 1120, 190, "sus" if t < HOF_HIT else "dizzy", t)
    if t > HOF_HIT - 0.4: tag(d, 400, 1160, "霍夫曼（LSD 之父）", WHITE, ease(pr(t, HOF_HIT - 0.4, HOF_HIT - 0.1)), 32)
    stamp(d, t, HOF_HIT, "查不出！", 720, 880, 110, BAD)

def helix(d, t, x, y0, y1, a=1.0):
    n = 26
    for i in range(n):
        u = i / (n - 1); y = lerp(y0, y1, u); ph = u * 4 * math.pi + t * 2.5
        x1 = x + math.sin(ph) * 120; x2 = x - math.sin(ph) * 120
        dep = math.cos(ph)
        d.line([(x1, y), (x2, y)], A(ELF[i % 6], 0.7 * a), 8)
        d.circ(x1, y, 16 + 4 * dep, fill=A((255, 255, 255), (0.6 + 0.4 * dep) * a)); d.circ(x2, y, 16 - 4 * dep, fill=A((255, 255, 255), (0.6 - 0.4 * dep) * a))
def s_dna(t, d):
    grad(d, (30, 160, 170), (20, 100, 130)); dots(d, t, WHITE, 0.2)
    helix(d, t, 540, 420, 1080, 0.9)
    k = ease(pr(t, DNA_HIT, DNA_HIT + 0.4))
    shroom(d, lerp(-200, 290, k), 1040, 170, "chill", t)
    shroom(d, lerp(1280, 790, k), 1040, 170, "chill", t + 1)
    tag(d, 290, 1110, "云南 · 见手青", WHITE, k, 32); tag(d, 790, 1170, "菲律宾 · Sedesdem", WHITE, k, 30)
    stamp(d, t, DNA_HIT, "测 DNA", 540, 330, 110, WHITE)
    if t > SAME_HIT:
        glow(d, 540, 800, 260, YEL, 0.5 * pulse(t, [SAME_HIT], 2))
        stamp(d, t, SAME_HIT, "同一种！", 540, 520, 130, YEL)
        tag(d, 540, 680, "Lanmaoa asiatica", WHITE, ease(pr(t, SAME_HIT + 0.4, SAME_HIT + 0.7)), 40)

def xmark(d, x, y, s, k):
    if k <= 0: return
    s = s * (1.6 - 0.6 * k)
    d.line([(x - s, y - s), (x + s, y + s)], A(BAD, min(1, k)), 14); d.line([(x - s, y + s), (x + s, y - s)], A(BAD, min(1, k)), 14)
def s_lab(t, d):
    grad(d, (110, 60, 190), (60, 30, 120)); dots(d, t, (220, 180, 255), 0.3)
    if t < Q_HIT:
        d.rect(220, 420, 860, 1000, fill=A((250, 248, 255), 1), r=30)
        d.text(540, 490, "化验单", 50, A((60, 30, 120), 1), k=1)
        for i, s in enumerate(["裸盖菇素", "LSD 类", "其他已知致幻物"]):
            y = 610 + i * 130
            d.text(280, y, s, 46, A(NAVYT, 1), anchor="lm", k=1)
            xmark(d, 770, y, 32, back(pr(t, XS[i], XS[i] + 0.2)))
        scientist(d, 300, 1170, 140, "sus", t)
    else:
        k = back(pr(t, Q_HIT, Q_HIT + 0.3))
        glow(d, 540, 820, 380, (255, 120, 255), 0.5 + 0.2 * math.sin(t * 6))
        pts = [(540 + 200 * k * math.cos(a_ + t), 820 + 200 * k * math.sin(a_ + t)) for a_ in [i * math.pi / 3 for i in range(6)]]
        for i in range(6):
            d.line([pts[i], pts[(i + 1) % 6]], A(WHITE, 1), 16); d.circ(*pts[i], 22, fill=A(YEL, 1))
        d.text(540, 820, "?", int(200 * k) + 1, A(WHITE, 1), k=1)
        stamp(d, t, Q_HIT, "全新的分子？", 540, 380, 110, YEL)

def brain(d, x, y, s, mood, t):
    for (bx, by, r) in [(-0.45, 0.05, 0.5), (0.45, 0.05, 0.5), (-0.2, -0.3, 0.5), (0.25, -0.3, 0.5), (0, 0.15, 0.55)]:
        d.circ(x + bx * s, y + by * s, r * s, fill=A(PINK, 1))
    for i in range(5):
        d.arc(x - s * 0.5 + i * s * 0.25, y - s * 0.2, s * 0.15, s * 0.2, 200, 340, A((235, 110, 160), 1), s * 0.04)
    d.ell(x - s * 0.4, y - s * 0.55, s * 0.18, s * 0.08, A(WHITE, 0.45))
    face(d, x, y + s * 0.15, s * 0.5, mood, 1)
def s_brain(t, d):
    swirl(d, t, (50, 40, 110), (30, 20, 70), cy=860)
    brain(d, 540, 900, 260, "scared" if t < BRAIN_HIT else "proud", t)
    for i in range(6):
        ang = t * 0.8 + i * math.pi / 3
        x = 540 + math.cos(ang) * 330; y = 900 + math.sin(ang) * 260
        tiny(d, x, y, 60, i, t, i, 1.0, clown=i % 2 == 0, flip=-1 if math.sin(ang) > 0 else 1)
    tag(d, 330, 520, "痴呆", WHITE, popk(t, BRAIN_TAGS[0]), 48); tag(d, 750, 520, "戒酒", WHITE, popk(t, BRAIN_TAGS[1]), 48)
    if t < BRAIN_HIT: d.text(540, 380, "也会看见小人", 60, A(WHITE, ease(pr(t, BRAIN_TAGS[1] + 0.3, BRAIN_TAGS[1] + 0.6))), k=1)
    else: stamp(d, t, BRAIN_HIT, "看懂大脑", 540, 370, 110, YEL)

def s_safe(t, d):
    rays(d, t, (255, 110, 70), (220, 60, 50), n=18, cx=540, cy=980)
    wok(d, 540, 1000, 300, t, 1.3)
    for i in range(5):
        ph = (t * 1.6 + i * 0.37) % 1
        slice_(d, 400 + i * 70, 960 - math.sin(ph * math.pi) * 230, 44, 0, blue=0.3 * (1 - ph))
    stamp(d, t, SAFE_HIT, "炒熟炒透！", 540, 380, 140, WHITE)
    if t > SAFE_HIT + 0.6: tag(d, 540, 580, "没熟会中毒", WHITE, ease(pr(t, SAFE_HIT + .6, SAFE_HIT + .9)), 52, BAD)

def s_end(t, d):
    grad(d, (60, 30, 100), (30, 16, 60)); dots(d, t, (255, 200, 255), 0.3)
    shroom(d, 540, 1120, 230, "proud", t)
    tiny(d, 260, 760, 110, 0, t, 0, 0.3, arms=0.4 * math.sin(t * 5))
    bubble(d, 330, 560, "我们还会回来的", -1, ELF[0], WHITE, popk(t, BUBS[0]))
    tiny(d, 820, 920, 110, 3, t, 1, 0.3, clown=True)
    bubble(d, 760, 760, "记得炒熟哦", 1, ELF[3], NAVYT, popk(t, BUBS[1]))
    d.text(540, 1230, "Domnauer & Dentinger, Mycologia 118(4):732 (2026)", 24, A(WHITE, 0.65))
    d.text(540, 1268, "University of Utah · ScienceDaily, 2026-10-25", 24, A(WHITE, 0.6))
    stamp(d, t, BUBS[2], "炒熟再吃", 540, 330, 100, YEL)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

def subs(t, d):
    if t >= OUTRO: return
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            ls = wrap(d, s, 54, 680); n = len(ls); y0 = 1350 - (n - 1) * 72
            w = max(d.tlen(x, 54, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 72 + 46, fill=A((15, 12, 26), 0.82 * al), r=22)
            for i, x in enumerate(ls): d.text(540, y0 + i * 72, x, 54, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇新发现"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)

SECS = [(0, HOOK_END, s_hook), (YUN, BRUISE, s_yun), (BRUISE, MAP, s_bruise), (MAP, RULER, s_map), (RULER, TABLE, s_ruler),
        (TABLE, SOUP_HIT, s_table), (SOUP_HIT, MOUTH, s_soup), (MOUTH, ARCH, s_mouth), (ARCH, DNA, s_arch), (DNA, LAB, s_dna),
        (LAB, BRAIN, s_lab), (BRAIN, SAFE, s_brain), (SAFE, OUTRO, s_safe), (OUTRO, 99, s_end)]
CUTS = [HOOK_END, BRUISE, MAP, RULER, KIND, TABLE, SOUP_HIT, MOUTH, ARCH, DNA, LAB, Q_HIT, BRAIN, SAFE, OUTRO]
def cam(t):
    z = 1.0 + 0.05 * pulse(t, HITS, 7)
    for a, b in RISERS:
        if a <= t < b: z += 0.08 * eio(pr(t, a, b))
    z += 0.025 * math.sin(t * 2 * math.pi / (BEAT * 2)) ** 2 * (1 if t > HOOK_HIT else 0)   # gentle reggae sway
    amp = 26 * pulse(t, [HOOK_HIT, SOUP_HIT], 4) + 5 * pulse(t, HITS, 6)
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx + 6 * math.sin(t * math.pi / BEAT), 960 + sy
def frame(t):
    img = Image.new("RGB", (W, H), (30, 20, 50)); d = D(img)
    for a, b, sf in SECS:
        if a <= t < b: sf(t, d); break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.08: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.5 * (1 - (t - c) / 0.08)))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.1f}.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        last = None; errs = 0
        for i in range(i0, i1):
            try: last = frame(i / FPS).tobytes()
            except Exception as e: errs += 1; print('ERR', i, e, file=sys.stderr)
            if last: p.stdin.write(last)
        p.stdin.close(); p.wait(); print('errs', errs, file=sys.stderr)
