import sys, subprocess
from fx import *
from cues import *

FUR = (92, 64, 54); FUR_L = (128, 92, 76); MUZ = (196, 150, 128); MUZ_D = (164, 120, 102)
CFUR = (54, 50, 58); CMUZ = (214, 184, 160)
FLOW = (240, 50, 70); FLOW_C = (255, 214, 64)
NAVYT = (24, 20, 40); GOLD = (255, 200, 60); OCHRE = (168, 66, 40); WALL = (214, 168, 116); WALL_D = (190, 142, 92)
MONK = (222, 96, 52); MONK_D = (84, 74, 84); MONK_F = (238, 186, 150)
ANTC = (176, 112, 62); ANTC_D = (140, 84, 44); MEAT = (226, 120, 100); MEAT_L = (246, 170, 150)
MALEC = (120, 160, 220)

def popk(t, t0): return min(1, back(pr(t, t0, t0 + 0.2)))
def tag(d, x, y, s, col, a=1.0, size=40, tc=NAVYT):
    if a <= 0.01: return
    w = d.tlen(s, size, 1) + 44
    d.rect(x - w / 2, y - size * 0.78, x + w / 2, y + size * 0.78, fill=A(col, 0.95 * a), r=size * 0.6)
    d.text(x, y, s, size, A(tc, a), k=1)
def bubble(d, x, y, s, side, col, tcol, a, size=44):
    if a <= 0: return
    w = d.tlen(s, size, 1) + 60; x0 = x if side < 0 else x - w
    d.rect(x0, y - 48, x0 + w, y + 48, fill=A(col, a), r=36)
    tx = x0 + 40 if side < 0 else x0 + w - 40
    d.poly([(tx - 14, y + 36), (tx - (22 if side < 0 else -22), y + 78), (tx + 14, y + 36)], A(col, a))
    d.text(x0 + w / 2, y, s, size, A(tcol, a), k=1)
def arrow(d, x0, y0, x1, y1, col, a=1.0, w=22):
    if a <= 0.01: return
    L = math.hypot(x1 - x0, y1 - y0) or 1; ux, uy = (x1 - x0) / L, (y1 - y0) / L; hx, hy = x1 - ux * w * 2.2, y1 - uy * w * 2.2
    d.line([(x0, y0), (hx, hy)], A(col, a), w)
    d.poly([(x1, y1), (hx - uy * w * 1.6, hy + ux * w * 1.6), (hx + uy * w * 1.6, hy - ux * w * 1.6)], A(col, a))
def rpoly(d, pts, ax, ay, s, rot, fill):
    c, sn = math.cos(rot), math.sin(rot)
    d.poly([(ax + (x * c - y * sn) * s, ay + (x * sn + y * c) * s) for x, y in pts], fill)
def rell(d, cx, cy, rx, ry, ax, ay, s, rot, fill, n=28):
    rpoly(d, [(cx + rx * math.cos(i / n * 6.2832), cy + ry * math.sin(i / n * 6.2832)) for i in range(n)], ax, ay, s, rot, fill)
def ground(d, y, col, top):
    d.rect(-50, y, OW + 50, OH + 50, fill=A(col, 1)); d.rect(-50, y, OW + 50, y + 22, fill=A(top, 1))
def pie(d, cx, cy, r, a0, a1, fill):
    if a1 - a0 < 0.5: return
    d.d.pieslice((P(cx - r), P(cy - r), P(cx + r), P(cy + r)), a0, a1, fill=fill)
def leaves(d, t, col, n=18, a=1.0, spd=0.18, seed=0):
    r2 = random.Random(seed)
    for i in range(n):
        u = (t * spd * r2.uniform(0.7, 1.3) + r2.random()) % 1
        x = r2.uniform(120, 960) + 60 * math.sin(t * 2 + i); y = -60 + u * 1600; rot = t * r2.uniform(1, 3) + i
        rell(d, 0, 0, 1.0, 0.45, x, y, 26, rot, A(col, a * 0.8))
def flower(d, x, y, r, a=1.0, t=0.0):
    for i in range(5):
        ang = i * 1.2566 + t * 0.5
        d.circ(x + math.cos(ang) * r * 0.62, y + math.sin(ang) * r * 0.62, r * 0.52, fill=A(FLOW, a))
    d.circ(x, y, r * 0.42, fill=A(FLOW_C, a)); d.circ(x - r * 0.15, y - r * 0.15, r * 0.14, fill=A(WHITE, 0.7 * a))

# ---------- apes ----------
POSES = {"stand": ((-0.55, 0.95), (0.55, 0.95)), "up": ((-0.95, -1.05), (0.95, -1.05)), "leap": ((0.75, -1.0), (1.15, -0.55)),
         "point": ((-0.5, 0.95), (1.45, -0.25)), "peace": ((-0.55, 0.95), (0.55, -1.25)), "hug": ((-1.25, 0.1), (1.25, 0.1)),
         "carry": ((-0.75, -1.25), (0.75, -1.25)), "fist": ((-0.6, 0.9), (0.95, -1.1))}
def ape(d, x, y, s, t, mood="chill", a=1.0, pose="stand", fem=False, look=0.0, sq=0.0, run=0.0, arms=None, chimp=False,
        older=False, baby=0.0, sit=False, flip=1, blink=True):
    fur = CFUR if chimp else FUR; muz = CMUZ if chimp else MUZ; fl = mix(fur, WHITE, 0.18)
    sy_ = 1 - sq; sx_ = 1 + sq
    ph = t * 13
    d.ell(x, y + 4, 0.95 * s, 0.14 * s, A((0, 0, 0), 0.22 * a))
    hipy = y - (0.45 if sit else 0.75) * s * sy_
    # legs
    for k, sd in enumerate((-1, 1)):
        hx = x + sd * 0.32 * s
        if sit: kn = (x + sd * 0.95 * s, y - 0.35 * s); ft = (x + sd * 0.7 * s, y)
        else:
            sw = math.sin(ph + k * math.pi) * run
            ft = (x + (sd * 0.42 + 0.55 * sw) * s * flip, y - 0.32 * max(0, math.sin(ph + k * math.pi + 1.2)) * run * s)
            kn = ((hx + ft[0]) / 2 + 0.12 * s * flip, (hipy + ft[1]) / 2)
        d.line([(hx, hipy), kn, ft], A(fur, a), 0.36 * s)
        d.ell(ft[0] + 0.12 * s * flip, ft[1] - 0.04 * s, 0.24 * s, 0.11 * s, A(mix(fur, (0, 0, 0), 0.25), a))
    # body
    by = y - 1.45 * s * sy_
    d.ell(x, by, 0.78 * s * sx_, 0.88 * s * sy_, A(fur, a))
    d.ell(x + 0.05 * s, by + 0.12 * s, 0.48 * s * sx_, 0.58 * s * sy_, A(fl, a))
    d.ell(x - 0.32 * s, by - 0.42 * s, 0.2 * s, 0.12 * s, A(WHITE, 0.18 * a))
    hy = y - 2.55 * s * sy_
    if baby > 0.01:   # baby clinging behind the left shoulder
        bx, byy, bs = x - 0.75 * s * flip, hy + 0.35 * s, 0.42 * s
        d.circ(bx, byy, bs, fill=A(FUR, a * baby)); d.ell(bx + 0.08 * bs * flip, byy + 0.08 * bs, bs * 0.72, bs * 0.66, A(MUZ, a * baby))
        face(d, bx + 0.08 * bs * flip, byy + 0.05 * bs, bs * 0.7, "happy", a * baby)
        d.line([(bx + 0.5 * bs * flip, byy + 0.9 * bs), (x - 0.1 * s * flip, by - 0.3 * s)], A(FUR, a * baby), 0.22 * s)
        d.circ(x - 0.1 * s * flip, by - 0.3 * s, 0.13 * s, fill=A(MUZ, a * baby))
    # arms
    sh = [(x - 0.62 * s * sx_, by - 0.5 * s * sy_), (x + 0.62 * s * sx_, by - 0.5 * s * sy_)]
    ar = arms or POSES.get(pose, POSES["stand"])
    for k, (sx0, sy0) in enumerate(sh):
        dx, dy = ar[k]
        if run and not arms and pose == "stand":
            sw = math.sin(ph + (1 - k) * math.pi) * run; dx, dy = dx * 0.6 + 0.7 * sw, 0.6 - 0.2 * abs(sw)
        if flip < 0 and arms is None: dx = -ar[1 - k][0] if pose in ("leap", "point", "peace", "fist") else dx
        hx_, hy_ = sx0 + dx * s, sy0 + dy * s
        el = ((sx0 + hx_) / 2 + 0.15 * s * (1 if k else -1), (sy0 + hy_) / 2 + 0.1 * s)
        d.line([(sx0, sy0), el, (hx_, hy_)], A(fur, a), 0.3 * s)
        d.circ(hx_, hy_, 0.19 * s, fill=A(muz, a))
        if pose == "peace" and k == 1:
            for j in (-1, 1): d.line([(hx_, hy_ - 0.05 * s), (hx_ + j * 0.14 * s, hy_ - 0.42 * s)], A(muz, a), 0.1 * s)
    # head
    hs = 1 + 0.08 * sq
    if chimp:
        for sd in (-1, 1): d.circ(x + sd * 0.74 * s, hy, 0.24 * s, fill=A(muz, a)); d.circ(x + sd * 0.74 * s, hy, 0.13 * s, fill=A(MUZ_D, a))
    else:
        for sd in (-1, 1): d.circ(x + sd * 0.66 * s, hy, 0.13 * s, fill=A(fur, a))
    d.circ(x, hy, 0.72 * s * hs, fill=A(fur, a))
    if not chimp:   # bonobo centre-parted hair: two side tufts
        for sd in (-1, 1): d.ell(x + sd * 0.42 * s, hy - 0.5 * s, 0.38 * s, 0.24 * s, A(mix(fur, (0, 0, 0), 0.15), a))
        d.line([(x, hy - 0.72 * s), (x, hy - 0.42 * s)], A(fl, a), 0.05 * s)
    if older:
        for sd in (-1, 1): d.ell(x + sd * 0.55 * s, hy + 0.1 * s, 0.16 * s, 0.3 * s, A((200, 200, 205), a))
    fx_ = x + look * 0.08 * s
    d.ell(fx_, hy + 0.06 * s, 0.56 * s, 0.52 * s, A(muz, a))
    d.ell(fx_, hy + 0.32 * s, 0.4 * s, 0.24 * s, A(mix(muz, WHITE, 0.25), a))
    if blink and (t + x * 0.003) % 3.3 < 0.1 and mood in ("chill", "sus"): face(d, fx_, hy + 0.06 * s, 0.55 * s, "happy", a)
    else: face(d, fx_, hy + 0.06 * s, 0.55 * s, mood, a, look)
    if fem: flower(d, x + 0.48 * s * flip, hy - 0.62 * s, 0.26 * s, a, t)
    return hy

def monkey(d, x, y, s, t, mood="chill", a=1.0, flip=1, swipe=0.0, jump=0.0):
    tl = [(x - flip * (0.6 + 0.5 * k / 8) * s, y - 0.1 * s + math.sin(t * 6 + k * 0.6) * 0.15 * s * k / 8 + 0.12 * s * k) for k in range(9)]
    d.line(tl, A(MONK_D, a), 0.13 * s)
    for k, sd in enumerate((-1, 1)):
        d.line([(x + sd * 0.35 * s, y + 0.2 * s), (x + sd * 0.45 * s + jump * 0.2 * s * sd, y + 0.75 * s - jump * 0.2 * s)], A(MONK, a), 0.17 * s)
    d.ell(x, y, 0.62 * s, 0.45 * s, A(MONK, a)); d.ell(x - 0.1 * s * flip, y - 0.2 * s, 0.45 * s, 0.25 * s, A(MONK_D, a))
    hx = x + 0.55 * s * flip; hy = y - 0.45 * s
    ax = hx + flip * (0.4 + 0.6 * swipe) * s; ay = hy + (0.4 - 0.8 * swipe) * s
    d.line([(x + 0.3 * s * flip, y - 0.1 * s), (ax, ay)], A(MONK, a), 0.15 * s); d.circ(ax, ay, 0.11 * s, fill=A(MONK_F, a))
    if swipe > 0.3:
        for j in range(3): d.arc(ax, ay, 0.35 * s + j * 0.12 * s, 0.35 * s + j * 0.12 * s, 200 if flip > 0 else 300, 260 if flip > 0 else 360, A(WHITE, a * swipe), 0.05 * s)
    d.circ(hx, hy, 0.42 * s, fill=A(MONK_D, a)); d.ell(hx + 0.05 * s * flip, hy + 0.06 * s, 0.32 * s, 0.3 * s, A(MONK_F, a))
    face(d, hx + 0.05 * s * flip, hy + 0.06 * s, 0.32 * s, mood, a)

def antelope(d, x, y, s, t, mood="scared", a=1.0, flip=1, run=0.0, rot=0.0, legs=True):
    if legs:
        for k in range(4):
            lx = x + (-0.5 + k * 0.33) * s * flip; sw = math.sin(t * 14 + k * 1.6) * run * 0.25 * s
            d.line([(lx, y), (lx + sw, y + 0.75 * s)], A(ANTC_D, a), 0.12 * s)
    d.ell(x, y, 0.8 * s, 0.42 * s, A(ANTC, a)); d.ell(x, y + 0.15 * s, 0.6 * s, 0.2 * s, A(mix(ANTC, WHITE, 0.35), a))
    d.circ(x - 0.78 * s * flip, y - 0.2 * s, 0.13 * s, fill=A(WHITE, a))
    hx, hy = x + 0.85 * s * flip, y - 0.4 * s
    d.line([(x + 0.5 * s * flip, y - 0.1 * s), (hx, hy)], A(ANTC, a), 0.3 * s)
    for sd in (-1, 1): d.ell(hx - 0.1 * s * flip + sd * 0.25 * s, hy - 0.3 * s, 0.1 * s, 0.22 * s, A(ANTC_D, a))
    for sd in (-0.08, 0.1): d.line([(hx + sd * s, hy - 0.25 * s), (hx + sd * s + 0.05 * s * flip, hy - 0.58 * s)], A((90, 70, 50), a), 0.06 * s)
    d.circ(hx, hy, 0.34 * s, fill=A(ANTC, a)); d.ell(hx + 0.2 * s * flip, hy + 0.12 * s, 0.2 * s, 0.15 * s, A(mix(ANTC, WHITE, 0.4), a))
    face(d, hx, hy - 0.02 * s, 0.32 * s, mood, a, 0.5 * flip)
    if mood == "dizzy":
        for j in range(3):
            ang = t * 5 + j * 2.09; d.text(hx + math.cos(ang) * 0.5 * s, hy - 0.55 * s + math.sin(ang) * 0.15 * s, "*", int(0.4 * s), A(GOLD, a), k=1)

def ham(d, x, y, s, a=1.0):
    d.line([(x + 0.4 * s, y - 0.2 * s), (x + 0.85 * s, y - 0.5 * s)], A(WHITE, a), 0.16 * s)
    for sd in (-1, 1): d.circ(x + 0.9 * s + sd * 0.06 * s, y - 0.55 * s + sd * 0.06 * s, 0.1 * s, fill=A(WHITE, a))
    d.ell(x, y, 0.55 * s, 0.4 * s, A(MEAT, a)); d.ell(x - 0.12 * s, y - 0.1 * s, 0.25 * s, 0.14 * s, A(MEAT_L, a))

def caveman(d, x, y, s, col, a=1.0, t=0.0, fem=False, spear=True):
    sw = math.sin(t * 6) * 0.15
    d.circ(x, y - 1.75 * s, 0.22 * s, fill=A(col, a))
    if fem:
        d.circ(x - 0.24 * s, y - 1.9 * s, 0.14 * s, fill=A(col, a)); d.line([(x - 0.24 * s, y - 1.9 * s), (x - 0.48 * s, y - 1.55 * s)], A(col, a), 0.1 * s)
    d.line([(x, y - 1.5 * s), (x + 0.1 * s, y - 0.8 * s)], A(col, a), 0.16 * s)
    for sd in (-1, 1): d.line([(x + 0.1 * s, y - 0.8 * s), (x + (0.1 + sd * 0.45 + sw) * s, y)], A(col, a), 0.12 * s)
    d.line([(x + 0.03 * s, y - 1.35 * s), (x + 0.55 * s, y - 1.2 * s)], A(col, a), 0.1 * s)
    d.line([(x + 0.03 * s, y - 1.35 * s), (x - 0.4 * s, y - 1.0 * s)], A(col, a), 0.1 * s)
    if spear:
        d.line([(x - 0.3 * s, y - 0.9 * s), (x + 1.3 * s, y - 1.55 * s)], A(col, a), 0.06 * s)
        d.poly([(x + 1.45 * s, y - 1.62 * s), (x + 1.2 * s, y - 1.62 * s), (x + 1.28 * s, y - 1.44 * s)], A(col, a))
def cave_animal(d, x, y, s, col, a=1.0, t=0.0):
    d.ell(x, y - 0.9 * s, 0.8 * s, 0.38 * s, A(col, a)); d.circ(x + 0.85 * s, y - 1.15 * s, 0.24 * s, fill=A(col, a))
    for k in range(4): d.line([(x + (-0.55 + k * 0.36) * s, y - 0.7 * s), (x + (-0.6 + k * 0.36 + 0.1 * math.sin(t * 8 + k)) * s, y)], A(col, a), 0.09 * s)
    for sd in (-0.05, 0.12): d.line([(x + (0.85 + sd) * s, y - 1.35 * s), (x + (0.95 + sd * 2) * s, y - 1.7 * s)], A(col, a), 0.06 * s)
def wall(d, t, warm=0.0):
    grad(d, mix(WALL, (240, 190, 120), warm), mix(WALL_D, (170, 100, 60), warm))
    r2 = random.Random(5)
    for i in range(40):
        d.ell(r2.uniform(0, 1080), r2.uniform(200, 1500), r2.uniform(30, 120), r2.uniform(14, 50), A(mix(WALL_D, (0, 0, 0), 0.1), 0.35))
    for i in range(8):
        d.line([(r2.uniform(0, 1080), r2.uniform(200, 1500)) for _ in range(3)], A((150, 106, 70), 0.3), 4)
def canopy_top(d, t, shake_=0.0, cols=((38, 110, 58), (60, 150, 70), (90, 180, 80))):
    for j, c in enumerate(cols):
        for i in range(9):
            x = i * 140 - 40 + j * 50 + shake_ * math.sin(t * 50 + i) * 12; y = 120 + j * 70 + 40 * math.sin(i * 1.7 + j)
            d.circ(x, y, 120 - j * 15, fill=A(c, 1))
def stars_bg(d, t, n=40):
    r2 = random.Random(3)
    for i in range(n):
        d.circ(r2.uniform(0, 1080), r2.uniform(0, 900), r2.uniform(2, 5), fill=A(WHITE, 0.4 + 0.4 * math.sin(t * 3 + i)))
def speed_lines(d, t, y0, y1, a=1.0, col=WHITE, dirx=-1):
    r2 = random.Random(int(t * 15))
    for i in range(10):
        y = r2.uniform(y0, y1); x = r2.uniform(100, 1000); L = r2.uniform(80, 220)
        d.line([(x, y), (x + dirx * L, y)], A(col, 0.5 * a), 6)

# ---------------- scenes ----------------
def s_hook(t, d):
    hit = t >= HOOK_HIT
    if hit: rays(d, t, (120, 210, 90), (40, 150, 80), n=20, cx=440, cy=900)
    else: grad(d, (40, 130, 80), (14, 60, 40))
    ground(d, 1150, (40, 96, 48), (110, 190, 90))
    canopy_top(d, t, pulse(t, [HOOK_HIT], 3))
    leaves(d, t, (110, 200, 90), 14, 1.0, 0.25, 1)
    if hit:
        for i in range(16):   # leaves bursting out from impact
            u = t - HOOK_HIT
            if u < 1.4:
                ang = -math.pi * (0.1 + 0.8 * i / 15); v = 600 + 300 * (i % 3)
                rell(d, 0, 0, 1.0, 0.45, 440 + math.cos(ang) * v * u, 1150 + math.sin(ang) * v * u + 600 * u * u, 30, u * 9 + i, A((120, 210, 90), 1 - u / 1.4))
    # female dives down
    u = pr(t, 0.0, HOOK_HIT)
    if not hit:
        yy = lerp(860, 1150, u * u); xx = lerp(300, 420, u)
        speed_lines(d, t, 300, 1000, 1.0, WHITE, 0)
        for i in range(6): d.line([(xx - 60 + i * 24, yy - 420 - 60 * i % 3), (xx - 60 + i * 24, yy - 620)], A(WHITE, 0.5), 6)
        ape(d, xx, yy, 140, t, "scream", pose="leap", fem=True)
    else:
        sq = 0.16 * math.exp(-(t - HOOK_HIT) * 6) * math.cos((t - HOOK_HIT) * 30)
        ape(d, 400, 1150, 145, t, "scream" if t < HOOK_STOP else "proud", pose="fist" if t < HOOK_STOP else "up", fem=True, sq=sq)
        sparks(d, 440, 1140, t, HOOK_HIT, n=50, spd=1100, col=(255, 240, 160), seed=3)
    # stunned male
    mk = popk(t, LAND)
    ape(d, 750, 1150, 100, t, "scream" if hit else "chill", pose="up" if hit else "stand", look=-1, sq=0.1 * pulse(t, [LAND], 8))
    if hit: d.text(800, 760 - 20 * mk, "?!", int(90 * mk) + 2, A(WHITE, mk), k=1); tag(d, 750, 1195, "雄性", MALEC, mk, 34, NAVYT)
    tag(d, 400, 1195, "雌性", FLOW, popk(t, LAND), 34, WHITE)
    if not hit: d.text(540, 330, "从天而降……", 92, A(WHITE, 1), k=1)
    stamp(d, t, HOOK_HIT, "打猎主力是母的！", 540, 330, 86, YEL)
def s_stereo(t, d):
    wall(d, t)
    d.rect(200, 560, 880, 1150, fill=A((236, 196, 140), 0.55), r=40)
    k0 = popk(t, PAINT[0]); cave_animal(d, 760, 1000, 110 * k0 + 1, OCHRE, k0, t)
    for i, (x, h) in enumerate([(300, PAINT[0]), (420, PAINT[1]), (540, PAINT[2])]):
        k = popk(t, h)
        if k > 0: caveman(d, x, 1080, 150 * k, OCHRE, k, t + i)
    tag(d, 540, 640, "古人壁画：男人去打猎", WHITE, popk(t, PAINT[1]), 40, OCHRE)
    stamp(d, t, PAINT[0], "打猎 = 男人？", 540, 330, 100, WHITE)
    k = popk(t, QMARK)
    if k > 0:
        glow(d, 540, 870, 300, (255, 80, 60), 0.5 * k)
        d.text(540 + 8 * math.sin(t * 9), 870, "?", int(420 * k) + 2, A(RED, 0.95 * k), k=1)
def s_chimp(t, d):
    grad(d, (255, 150, 60), (220, 90, 40))
    for i in range(7): d.rect(-50, 1150 - i * 60, OW + 50, 1153 - i * 60, fill=A(WHITE, 0.06))
    for i in range(6): d.circ(120 + i * 180, 1150, 140, fill=A((190, 80, 34), 1))
    ground(d, 1150, (170, 70, 30), (255, 180, 100))
    hop = pulse(t, CHIMP_HOPS, 5)
    for i, x in enumerate((330, 540, 750)):
        yy = 1150 - 60 * hop * (1 if i != 1 else 1.2)
        ape(d, x, yy, 92, t, "proud" if t > CHIMP_HOPS[0] else "sus", arms=((-0.9, 0.0), (0.9, 0.0)), chimp=True, sq=-0.08 * hop)
    tag(d, 540, 560, "黑猩猩：雄性组队", WHITE, popk(t, CHIMP_TAG), 46, (200, 80, 30))
    k = popk(t, MEAT_TAG)
    if k > 0:
        ham(d, 470, 700, 70 * k, k); d.text(590, 690, "=", 64, A(WHITE, k), k=1)
        tag(d, 690, 690, "地位", GOLD, k, 40)
    stamp(d, t, CHIMP + 0.15, "近亲：黑猩猩", 540, 330, 100, WHITE)
def s_ten(t, d):
    grad(d, (20, 50, 90), (10, 24, 50)); stars_bg(d, t)
    for i in range(7): d.circ(80 + i * 160, 1180, 170, fill=A((14, 60, 60), 1))
    ground(d, 1180, (12, 40, 40), (40, 110, 90))
    # tent + flag
    k = popk(t, TENT)
    d.poly([(330, 1180 - 230 * k), (180, 1180), (480, 1180)], A((80, 170, 100), 1)); d.poly([(330, 1180 - 230 * k), (300, 1180), (360, 1180)], A((30, 80, 50), 1))
    glow(d, 330, 1130, 90, GOLD, 0.6 * k)
    d.line([(450, 1180), (450, 930)], A((200, 200, 200), 1), 6); d.poly([(450, 930), (450, 990), (540, 960)], A(RED, k))
    tag(d, 340, 860, "刚果 LuiKotale", WHITE, k, 32, (20, 50, 90))
    for i in range(12):   # fireflies
        d.circ(540 + 380 * math.sin(t * 0.7 + i * 2.1), 900 + 220 * math.sin(t * 0.9 + i * 1.3), 5, fill=A((220, 255, 140), 0.7))
    # calendar flipping 10 years
    yr = 1 + int(9 * cl(pr(t, *CAL))) if t >= CAL[0] else 1
    fp = ((t - CAL[0]) / ((CAL[1] - CAL[0]) / 9)) % 1 if CAL[0] <= t < CAL[1] else 1
    cx, cy = 720, 600
    d.rect(cx - 130, cy - 130, cx + 130, cy + 140, fill=A(WHITE, 1), r=20); d.rect(cx - 130, cy - 130, cx + 130, cy - 70, fill=A(RED, 1), r=20)
    d.rect(cx - 130, cy - 90, cx + 130, cy - 70, fill=A(RED, 1))
    for sd in (-1, 1): d.rect(cx + sd * 60 - 8, cy - 150, cx + sd * 60 + 8, cy - 110, fill=A((120, 120, 130), 1), r=6)
    d.text(cx, cy + 30, f"{yr}", 120, A(NAVYT, 1), k=1); d.text(cx + 90, cy + 100, "年", 30, A(NAVYT, 0.7), k=1)
    if fp < 0.6:   # page flying up
        hh = 230 * (1 - fp / 0.6); d.rect(cx - 130, cy - 70 - hh * 0.2, cx + 130, cy - 70 + hh - hh * 0.2, fill=A((240, 240, 236), 0.9), r=10)
    # odometer 0 -> 415
    n = int(415 * ease(pr(t, *CNT))) if t >= CNT[0] else 0
    if t >= CNT[0] - 0.3:
        ka = popk(t, CNT[0] - 0.3)
        tag(d, 680, 900, "成功捕猎记录", GOLD, ka, 34)
        s_ = f"{n:03d}"
        for j, ch in enumerate(s_):
            x = 580 + j * 100
            d.rect(x - 44, 960, x + 44, 1080, fill=A((30, 30, 44), ka), r=12)
            d.text(x, 1020, ch, 90, A(YEL if t >= CNT[1] else WHITE, ka), k=1)
        if t >= CNT[1]: sparks(d, 680, 1020, t, CNT[1], n=30, spd=700, col=GOLD, seed=4, life=0.8)
    stamp(d, t, TENT, "蹲守 10 年", 540, 330, 110, WHITE)
def cloth(d, cx, cy, r, t, a=1.0, lift=0.0, rot=0.0, pul=0.0):
    rr = r * (1.08 + 0.05 * pul); yy = cy - lift * 1400
    d.circ(cx, yy, rr, fill=A((120, 60, 170), a))
    for i in range(10):
        ang = rot + i * math.pi / 5
        d.line([(cx + math.cos(ang) * rr * 0.2, yy + math.sin(ang) * rr * 0.2), (cx + math.cos(ang) * rr * 0.97, yy + math.sin(ang) * rr * 0.97)], A((150, 90, 200), a), 10)
    for i in range(12):
        ang = i * math.pi / 6; d.circ(cx + math.cos(ang) * rr, yy + math.sin(ang) * rr + 10, 26, fill=A((120, 60, 170), a))
    d.text(cx, yy, "?", int(r * 0.9), A(WHITE, a), k=1)
def s_pie(t, d):
    grad(d, (70, 30, 110), (24, 10, 44))
    d.poly([(440, 0), (640, 0), (900, 1200), (180, 1200)], A((255, 240, 200), 0.08))
    d.ell(540, 1150, 330, 50, A((0, 0, 0), 0.3))
    d.rect(520, 1080, 560, 1150, fill=A((180, 160, 200), 1)); d.rect(420, 1140, 660, 1160, fill=A((180, 160, 200), 1), r=8)
    beats_ = [qb(36 + i) for i in range(0, 10, 2)] + [qb(41 + i) for i in range(4)] + [qb(43.5), qb(44.5)]
    p = pulse(t, beats_, 6)
    cloth(d, 540, 800, 260, t, rot=(t - PIE) * (0.4 + 0.6 * pr(t, RISE[0], SIL0)) * 2, pul=p)
    dots = sum(1 for h in (qb(37), qb(39), qb(41)) if t >= h)
    d.text(540, 330, "结果" + "." * dots * 2, 110, A(WHITE, 1), k=1)
    if t >= SIL0: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.75))
def s_reveal(t, d):
    rays(d, t, (250, 90, 90), (200, 40, 60), n=22, cx=540, cy=820)
    glow(d, 540, 820, 520, (255, 220, 200), 0.6 * pulse(t, [BIG2], 2))
    sw = ease(pr(t, BIG2, BIG2 + 0.35))
    d.circ(540, 820, 285, fill=A(WHITE, 1))
    pie(d, 540, 820, 270, -90 + 360 * 0.6 * sw, -90 + 360 * sw, A(MALEC, 1))
    pie(d, 540, 820, 270 * (1 + 0.04 * pulse(t, [BIG2] + REV_TAGS, 6)), -90, -90 + 360 * 0.6 * sw, A(FLOW, 1))
    if sw > 0.9:
        d.text(640, 860, "60%", 96, A(WHITE, 1), k=1); d.text(410, 700, "40%", 60, A(WHITE, 1), k=1)
    cloth(d, 540, 800, 260, t, lift=ease(pr(t, BIG2, BIG2 + 0.4)), rot=t * 3)
    k = popk(t, REV_TAGS[0])
    if k > 0: flower(d, 760, 640, 50 * k, 1, t); tag(d, 760, 1150, "雌性", FLOW, k, 46, WHITE)
    tag(d, 330, 1150, "雄性", MALEC, popk(t, REV_TAGS[1]), 46, NAVYT)
    sparks(d, 540, 820, t, BIG2, n=80, spd=1400, col=(255, 230, 160), seed=5)
    stamp(d, t, BIG2, "60% 是雌性！", 540, 330, 116, WHITE)
def s_init(t, d):
    grad(d, (255, 214, 90), (240, 160, 50)); ground(d, 1150, (190, 120, 40), (255, 220, 120))
    speed_lines(d, t, 650, 1100, 1.0, WHITE, -1)
    u = pr(t, INIT, BABY)
    antelope(d, 790 + 30 * u, 1040, 80, t, "scream", run=1.0)
    ape(d, 420 + 110 * u, 1150, 120, t, "scream", pose="leap", fem=True, run=1.0)
    tag(d, 460 + 110 * u, 700, "发起者", FLOW, popk(t, INIT_TAG), 44, WHITE)
    arrow(d, 460 + 110 * u, 730, 460 + 110 * u, 780, FLOW, popk(t, INIT_TAG), 14)
    # male sits behind; "抢" crossed out
    ape(d, 240, 1150, 60, t, "sus", sit=True, look=1)
    k = popk(t, NO_STEAL)
    if k > 0:
        tag(d, 260, 860, "抢来的", WHITE, k, 40, NAVYT)
        d.line([(170, 820), (350, 900)], A(RED, k), 12); d.line([(170, 900), (350, 820)], A(RED, k), 12)
    stamp(d, t, INIT + 0.1, "她先出手！", 540, 330, 110, WHITE)
def s_baby(t, d):
    grad(d, (255, 140, 180), (210, 70, 130))
    for i in range(10):
        x = (i * 140 - t * 600) % 1300 - 100; d.rect(x, 1240, x + 70, 1252, fill=A(WHITE, 0.35), r=6)
    ground(d, 1150, (180, 60, 110), (255, 170, 200))
    for i in range(5):
        x = (i * 300 - t * 500) % 1500 - 200; d.circ(x, 1150, 90, fill=A((230, 110, 160), 1))
    ground(d, 1150, (180, 60, 110), (255, 170, 200))
    bob = 25 * pulse(t, BABY_STEPS, 8)
    speed_lines(d, t, 500, 1100, 0.8, WHITE, -1)
    ape(d, 560, 1150 - bob, 135, t, "proud", pose="stand", fem=True, run=1.0, baby=1.0, look=1)
    tag(d, 330, 700, "背着娃", WHITE, popk(t, BABY_TAG), 44, (210, 70, 130))
    arrow(d, 330, 740, 420, 820, WHITE, popk(t, BABY_TAG), 12)
    stamp(d, t, BABY + 0.15, "照样冲！", 540, 330, 120, WHITE)
def branch(d, x0, y0, x1, y1, t):
    d.line([(x0, y0), (x1, y1)], A((110, 76, 50), 1), 26)
    for i in range(4):
        u = (i + 0.5) / 4; d.circ(lerp(x0, x1, u), lerp(y0, y1, u) - 20, 46, fill=A((70, 160, 80), 1))
def s_canopy(t, d):
    grad(d, (110, 200, 250), (60, 150, 230))
    for i in range(4): d.ell((i * 340 + t * 30) % 1400 - 150, 450 + i * 60, 140, 40, A(WHITE, 0.5))
    d.rect(140, 300, 190, 1500, fill=A((100, 70, 46), 1)); d.rect(860, 300, 920, 1500, fill=A((100, 70, 46), 1))
    branch(d, 140, 1130, 520, 1100, t); branch(d, 420, 900, 920, 880, t); branch(d, 520, 690, 920, 660, t)
    canopy_top(d, t, 0, ((40, 120, 60), (60, 150, 70), (90, 180, 80)))
    P_ = [(300, 1110), (540, 880), (660, 690)]
    air = False; px, py = P_[0]
    for k_, land in enumerate(SWINGS[1:]):
        u = pr(t, land - 0.6, land)
        if t >= land - 0.6:
            a0, a1 = P_[k_], P_[k_ + 1]; u = eio(u); px = lerp(a0[0], a1[0], u); py = lerp(a0[1], a1[1], u) - 160 * math.sin(u * math.pi); air = 0 < u < 1
    if t < SWINGS[0]: py += 0
    ape(d, px, py, 88, t, "scream" if air else "proud", pose="leap" if air else "up", fem=True, look=1)
    sw_ = ease(pr(t, MONKEY_HIT, MONKEY_HIT + 0.15)) * (1 - pr(t, MONKEY_HIT + 0.5, MONKEY_HIT + 0.8))
    mx = 800 if t < SWINGS[1] else 830
    monkey(d, mx, 560, 72, t, "scream" if t >= MONKEY_HIT else "scared", flip=-1, swipe=sw_)
    if t >= MONKEY_HIT: tag(d, 800, 445, "会反击！", RED, popk(t, MONKEY_HIT), 38, WHITE)
    k = popk(t, EQ)
    if k > 0:
        d.rect(200, 950, 880, 1030, fill=A(WHITE, 0.92 * k), r=30)
        d.text(250, 990, "雌", 52, A(FLOW, k), k=1); d.text(540, 990, "=", 60, A(NAVYT, k), k=1); d.text(830, 990, "雄", 52, A((60, 110, 200), k), k=1)
        d.rect(300, 975, 490, 1005, fill=A(FLOW, k), r=10); d.rect(590, 975, 780, 1005, fill=A(MALEC, k), r=10)
    stamp(d, t, CANOPY + 0.15, "树上抓猴子", 540, 330, 110, WHITE)
def s_ante(t, d):
    grad(d, (170, 220, 90), (90, 160, 60)); ground(d, 1150, (70, 120, 40), (180, 230, 110))
    for i in range(6): d.rect(i * 200 - 20, 700, i * 200 + 20, 1150, fill=A((60, 120, 50), 0.5))
    step = math.sin(t * 6)
    hy = ape(d, 380, 1150 - 8 * abs(step), 115, t, "proud", pose="carry", fem=True, older=True)
    antelope(d, 380, hy - 135, 110, t, "dizzy", legs=False, flip=1)
    tag(d, 380, 1195, "年长雌性", WHITE, popk(t, ANTE + 0.3), 34, (70, 120, 40))
    k = popk(t, BARS3)
    base = 1150; u = 110
    for j, (x, hh, col, lab) in enumerate([(680, 3 * u * k, FLOW, "雌"), (820, u * k, MALEC, "雄")]):
        if k > 0:
            d.rect(x - 50, base - hh, x + 50, base, fill=A(col, 1), r=12); d.text(x, base - hh - 40, lab, 44, A(WHITE, 1), k=1)
    n = sum(1 for h in X3 if t >= h)
    if n:
        sz = [120, 160, 210][n - 1] * (1 + 0.25 * pulse(t, X3, 10))
        glow(d, 740, 570, 200, GOLD, 0.5 * pulse(t, X3, 4) + 0.2)
        d.text(740, 570, "×3", int(sz), A(YEL, 1), k=1)
    for i, h in enumerate(X3): sparks(d, 740, 570, t, h, n=20, spd=700, col=GOLD, seed=30 + i, life=0.6)
    stamp(d, t, ANTE + 0.15, "地上大羚羊", 540, 330, 110, WHITE)
def s_share(t, d):
    grad(d, (255, 120, 80), (200, 60, 50))
    for i in range(9): d.circ(540, 1150, 200 + i * 140, outline=A(WHITE, 0.06), w=30)
    ground(d, 1150, (150, 50, 40), (255, 160, 110))
    ape(d, 320, 1150, 105, t, "proud", sit=True, pose="point", fem=True, older=True)
    for j in range(3): ham(d, 300 + j * 70, 1120 - (j % 2) * 30, 50)
    stg = sum(1 for h in BELLS if t >= h)
    for i, x in enumerate((600, 710, 820)):
        ok = i < [0, 1, 1, 2, 2, 3][min(stg, 5)]
        bob = 10 * math.sin(t * 5 + i)
        ape(d, x, 1150 + (0 if not ok else -15), 45, t, "happy" if ok else "sus", look=-1)
        d.rect(x - 26, 1185, x + 26, 1225, fill=A(WHITE, 1), r=8); d.text(x, 1205, str(i + 1), 28, A(NAVYT, 1), k=1)
        if ok: d.text(x, 970 + bob * 0, "OK", 34, A(GOOD if 'GOOD' in globals() else (110, 225, 130), 1), k=1)
    for i, h in enumerate(BELLS): sparks(d, 450, 900, t, h, n=14, spd=400, col=GOLD, seed=40 + i, life=0.5)
    k = popk(t, BELLS[0])
    if k > 0:   # bell
        sw = 0.4 * math.sin(t * 20) * pulse(t, BELLS, 3)
        bx, by = 450 + sw * 30, 860
        d.d.chord((P(bx - 40), P(by - 40), P(bx + 40), P(by + 50)), 180, 360, fill=A(GOLD, k)); d.rect(bx - 44, by + 2, bx + 44, by + 16, fill=A(GOLD, k), r=6)
        d.circ(bx, by + 22, 10, fill=A((200, 140, 30), k))
    tag(d, 540, 620, "她说了算", WHITE, popk(t, SHARE_TAG), 50, (200, 60, 50))
    stamp(d, t, SHARE + 0.15, "谁先吃？", 540, 330, 120, WHITE)
def s_cult(t, d):
    d.rect(0, 0, 540, OH, fill=A((40, 170, 160), 1)); d.rect(540, 0, OW, OH, fill=A((140, 80, 200), 1))
    d.rect(530, 0, 550, OH, fill=A(WHITE, 0.8))
    d.rect(-50, 1150, 540, OH, fill=A((20, 110, 100), 1)); d.rect(540, 1150, OW + 50, OH, fill=A((90, 40, 140), 1))
    for gi, (cx, h, lab, col) in enumerate([(360, GROUPA, "A 群：主抓地上的", (20, 110, 100)), (720, GROUPB, "B 群：专抓猴子", (90, 40, 140))]):
        k = popk(t, h)
        for j in range(3):
            x = cx + (j - 1) * 100; ape(d, x, 1150 - 20 * pulse(t, [h], 6), 48, t, "proud" if k > 0 else "chill", fem=(j == 1), pose="up" if k > 0 and j == 1 else "stand")
        if k > 0:
            if gi == 0: antelope(d, cx - 15, 930, 70 * k, t, "scared", run=0.6)
            else: monkey(d, cx, 930, 70 * k, t, "scared", flip=-1)
            tag(d, cx, 820, lab, WHITE, k, 32, col)
    # "one-sentence takeaway" knowledge card
    k1 = popk(t, CARD1); k2 = popk(t, CULT_TAG)
    if k1 > 0:
        y0 = 300 + 30 * (1 - k1)
        d.rect(190, y0, 890, y0 + 420, fill=A((255, 250, 238), 0.97 * k1), r=36)
        d.rect(190, y0, 890, y0 + 18, fill=A(GOLD, k1), r=9)
        tag(d, 540, y0 + 70, "一句话学会", GOLD, k1, 36)
        d.text(540, y0 + 170, "同样的猎物", 50, A(NAVYT, k1), k=1)
        d.text(540, y0 + 240, "两群各抓各的", 50, A(NAVYT, k1), k=1)
        if k2 > 0:
            glow(d, 540, y0 + 340, 260, GOLD, 0.35 * k2 * (0.6 + 0.4 * pulse(t, [CULT_TAG], 3)))
            d.text(540, y0 + 340, "= 动物也有文化传统", int(58 * (0.7 + 0.3 * k2)), A((200, 60, 50), k2), k=1)
            sparks(d, 540, y0 + 340, t, CULT_TAG, n=30, spd=700, col=GOLD, seed=50, life=0.7)
    else:
        d.text(540, 400, "邻居两群", 96, A(WHITE, 1), k=1)
def s_human(t, d):
    wall(d, t, 0.6)
    glow(d, 540, 800, 500, (255, 200, 120), 0.5 + 0.1 * math.sin(t * 13))
    d.rect(200, 560, 880, 1150, fill=A((246, 210, 150), 0.5), r=40)
    caveman(d, 380, 1080, 150, OCHRE, 1, t)
    k = popk(t, FEM_ADD)
    if k > 0:
        caveman(d, 640, 1080, 150 * k, (200, 40, 70), k, t + 1, fem=True)
        for i in range(10):
            ang = i * 0.63 + t * 2; d.circ(660 + math.cos(ang) * 170 * k, 900 + math.sin(ang) * 170 * k, 7, fill=A(YEL, k * (0.6 + 0.4 * math.sin(t * 9 + i))))
    tag(d, 540, 640, "人和倭黑猩猩、黑猩猩的共同祖先", WHITE, popk(t, ANC_TAG), 34, OCHRE)
    tag(d, 540, 700, "500–700 万年前", GOLD, popk(t, ANC_TAG + 0.1), 34)
    stamp(d, t, HUMAN + 0.15, "祖先怎么打猎？", 540, 330, 96, WHITE)
def s_end(t, d):
    rays(d, t, (255, 206, 90), (240, 150, 50), n=16, cx=540, cy=1000)
    ground(d, 1150, (170, 110, 40), (255, 220, 120))
    ape(d, 460, 1150, 140, t, "happy" if t >= PEACE else "proud", pose="peace" if t >= PEACE else "stand", fem=True, sq=0.08 * pulse(t, [PEACE, FINAL], 7), blink=False)
    bubble(d, 880, 640, "今晚我请客！", 1, WHITE, NAVYT, popk(t, BUB), 44)
    ham(d, 760, 1110, 60 * popk(t, BUB))
    stamp(d, t, FINAL, "雌性也是好猎手", 540, 330, 92, WHITE)
    d.text(540, 1300, "Hohmann et al., Curr. Biol. (2026)", 28, A(WHITE, 0.95))
    d.text(540, 1345, "DOI 10.1016/j.cub.2026.09.082", 28, A(WHITE, 0.95))
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

def subs(t, d):
    if t >= OUTRO: return
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            ls = wrap(d, s, 52, 670); n = len(ls); y0 = 1350 - (n - 1) * 70
            w = max(d.tlen(x, 52, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 44, 540 + w / 2, y0 + (n - 1) * 70 + 44, fill=A((15, 12, 26), 0.82 * al), r=22)
            for i, x in enumerate(ls): d.text(540, y0 + i * 70, x, 52, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇新发现"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)

SECS = [(-1, HOOK_END, s_hook), (STEREO, CHIMP, s_stereo), (CHIMP, TEN, s_chimp), (TEN, PIE, s_ten), (PIE, BIG2, s_pie),
        (REVEAL, INIT, s_reveal), (INIT, BABY, s_init), (BABY, CANOPY, s_baby), (CANOPY, ANTE, s_canopy), (ANTE, SHARE, s_ante),
        (SHARE, CULT, s_share), (CULT, HUMAN, s_cult), (HUMAN, OUTRO, s_human), (OUTRO, 99, s_end)]
def cam(t):
    z = 1.0 + 0.05 * pulse(t, HITS, 7) + 0.07 * pulse(t, [HOOK_HIT, BIG2], 3)
    a, b = RISE
    if a <= t < b: z += 0.14 * eio(pr(t, a, b))
    amp = 28 * pulse(t, [HOOK_HIT, BIG2], 4) + 5 * pulse(t, HITS, 6)
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx, 960 + sy
def frame(t):
    img = Image.new("RGB", (W, H), (30, 20, 50)); d = D(img)
    for a, b, sf in SECS:
        if a <= t < b: sf(t, d); break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.08: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.55 * (1 - (t - c) / 0.08)))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.2f}.png")
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
