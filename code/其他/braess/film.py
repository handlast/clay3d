import sys, subprocess
from fx import *
from cues import *

NAVY = (16, 20, 38); NAVY2 = (30, 38, 72)
ROAD = (70, 80, 120); ROAD_L = (110, 122, 170); NARROW = (220, 120, 70); NARROW_L = (255, 170, 120)
GOOD = (110, 220, 130); BAD = (255, 90, 80); SKY = (40, 60, 110)
CARS = [(255, 120, 110), (255, 196, 80), (120, 200, 255), (160, 230, 120), (220, 150, 255), (255, 160, 210)]
BRAESS = (126, 110, 170)

def car(d, x, y, s, col, mood="chill", a=1.0, t=0.0, spd=0.0, dirn=1, bounce=0.0):
    """Cartoon car, side view, (x,y) = wheel baseline. No outline: shading + highlight."""
    y = y - abs(math.sin(t * 14 + x * 0.01)) * s * 0.05 * bounce
    dark = mix(col, (0, 0, 0), 0.3); light = mix(col, WHITE, 0.45)
    d.ell(x, y + s * 0.08, s * 0.95, s * 0.1, A((0, 0, 0), 0.22 * a))
    d.rect(x - s * 0.5, y - s * 1.0, x + s * 0.45, y - s * 0.4, fill=A(dark, a), r=s * 0.28)
    d.rect(x - s * 0.42, y - s * 0.92, x + s * 0.37, y - s * 0.5, fill=A((190, 230, 255), 0.9 * a), r=s * 0.2)
    d.rect(x - s * 0.38, y - s * 0.88, x - s * 0.18, y - s * 0.55, fill=A(WHITE, 0.5 * a), r=s * 0.06)
    d.rect(x - s * 0.95, y - s * 0.6, x + s * 0.95, y - s * 0.1, fill=A(dark, a), r=s * 0.24)
    d.rect(x - s * 0.95, y - s * 0.62, x + s * 0.95, y - s * 0.22, fill=A(col, a), r=s * 0.22)
    d.ell(x - s * 0.45, y - s * 0.52, s * 0.3, s * 0.05, A(light, 0.7 * a))
    d.circ(x + dirn * s * 0.88, y - s * 0.38, s * 0.08, fill=A((255, 250, 200), a))
    for wx in (-0.55, 0.55):
        d.circ(x + wx * s, y - s * 0.1, s * 0.22, fill=A((60, 64, 84), a)); d.circ(x + wx * s, y - s * 0.1, s * 0.09, fill=A((170, 176, 200), a))
    face(d, x + dirn * s * 0.42, y - s * 0.4, s * 0.38, mood, a, look=0.5 * dirn)
    if spd > 0:
        for i in range(3):
            yy = y - s * 0.55 + i * s * 0.18; L = s * (0.5 + 0.3 * math.sin(t * 9 + i))
            d.line([(x - dirn * s * 1.1, yy), (x - dirn * (s * 1.1 + L), yy)], A(WHITE, 0.4 * a * spd), s * 0.05)
    if mood == "scream":
        for i in range(2):
            d.line([(x + s * 0.2 + i * s * 0.25, y - s * 1.15), (x + s * 0.3 + i * s * 0.25, y - s * 1.4)], A(BAD, a), s * 0.07)

def stars(d, t, a=1.0, n=50):
    for i in range(n):
        x = (i * 397) % 1080; y = (i * 211) % 1000
        d.circ(x, y, 2 + i % 3, fill=A(WHITE, a * 0.5 * (0.5 + 0.5 * math.sin(t * 2 + i * 1.3))))

# ---------- city grid (hook) ----------
def street(d, y, x0, x1, w, col=ROAD):
    d.rect(x0, y - w / 2, x1, y + w / 2, fill=A(col, 1))
    d.rect(x0, y - w / 2, x1, y - w / 2 + 6, fill=A(ROAD_L, 0.5))
    for x in range(int(x0), int(x1), 90): d.rect(x, y - 3, x + 46, y + 3, fill=A((240, 230, 180), 0.6))
def s_hook(t, d):
    if t < HOOK_HIT: grad(d, NAVY, NAVY2)
    else: rays(d, t, (40, 52, 100), (24, 30, 62), cy=1150)
    stars(d, t, 0.4)
    k = pr(t, HOOK_HIT, HOOK_HIT + 1.2)
    lanes = [(980, 1, 0), (1180, -1, 1), (1380, 1, 2)]
    for li, (y, dr, idx) in enumerate(lanes):
        street(d, y, -40, 1120, 120)
        closed = li == 1
        for i in range(6):
            col = CARS[(i + li * 2) % 6]
            if closed:
                x = 120 + i * 175
                if t > HOOK_HIT: continue
                car(d, x, y + 40, 62, col, "scream", t=t)
            else:
                spd = lerp(0.05, 1.0, eio(k))
                x = (i * 190 + t * 420 * spd * dr + li * 60) % 1300 - 110
                if dr < 0: x = 1080 - x
                car(d, x, y + 40, 62, col, "scream" if k < 0.3 else "happy", t=t, spd=spd, dirn=dr, bounce=spd)
    if t > HOOK_HIT:  # barrier slams down on the middle road
        u = back(pr(t, HOOK_HIT, HOOK_HIT + 0.2)); yb = 1180
        for i in range(6):
            x0 = 60 + i * 170
            d.rect(x0, yb - 52 * u, x0 + 150, yb + 10 * u, fill=A(BAD if i % 2 == 0 else WHITE, 1), r=10)
        d.rect(400, yb - 150 * u, 680, yb - 70 * u, fill=A(BAD, 1), r=20)
        d.text(540, yb - 110 * u, "封路", int(60 * u) + 1, A(WHITE, 1), k=1)
    sparks(d, 540, 1180, t, HOOK_HIT, 50, 1300, YEL, 1, 3)
    d.text(540, 380, "封掉一条路", 100, A(WHITE, ease(pr(t, 0, 0.2))), k=1)
    stamp(d, t, HOOK_HIT, "反而不堵了？", 540, 600, 170, YEL)
    glow(d, 540, 600, 360, YEL, 0.35 * pulse(t, [HOOK_HIT], 3))

# ---------- NYC ----------
def skyline(d, t, col=(44, 56, 104), lit=(255, 220, 120)):
    xs = [(0, 160, 520), (150, 290, 380), (280, 420, 640), (410, 560, 300), (550, 680, 560), (670, 820, 420), (810, 960, 700), (950, 1100, 460)]
    for i, (x0, x1, h) in enumerate(xs):
        top = 1080 - h
        d.rect(x0, top, x1, 1080, fill=A(mix(col, (0, 0, 0), 0.15 * (i % 2)), 1))
        d.rect(x0, top, x0 + 14, 1080, fill=A(WHITE, 0.06))
        for wy in range(int(top) + 30, 1060, 46):
            for wx in range(x0 + 24, x1 - 20, 40):
                if (wx * 7 + wy * 3 + i) % 5 < 3: d.rect(wx, wy, wx + 16, wy + 22, fill=A(lit, 0.55 + 0.25 * math.sin(t * 2 + wx)))
    d.poly([(840, 380), (885, 240), (930, 380)], A(mix(col, WHITE, 0.2), 1))
def s_nyc(t, d):
    grad(d, (24, 30, 70), (60, 50, 100)); stars(d, t, 0.5)
    glow(d, 800, 330, 140, (255, 240, 200), 0.5); d.circ(800, 330, 60, fill=A((255, 246, 220), 1))
    skyline(d, t)
    street(d, 1220, -40, 1120, 260)
    d.rect(-40, 1080, 1120, 1092, fill=A(ROAD_L, 1))
    # 42 St sign
    d.rect(150, 820, 162, 1090, fill=A((150, 160, 190), 1)); d.rect(60, 820, 360, 900, fill=A((40, 150, 90), 1), r=12)
    d.text(210, 860, "42 街", 52, A(WHITE, 1), k=1)
    if t < NYC2:
        u = back(pr(t, NYC_HIT, NYC_HIT + 0.2))
        for i in range(5):
            x0 = 120 + i * 180
            d.rect(x0, 1230 - 60 * u, x0 + 160, 1240, fill=A(BAD if i % 2 == 0 else WHITE, 1 if u > 0 else 0), r=10)
        if u > 0:
            d.rect(330, 1010, 750, 1080, fill=A((90, 200, 120), 1), r=30); d.text(540, 1045, "地球日 · 封路", 40, A(WHITE, 1), k=1)
        stamp(d, t, NYC_HIT, "1990 · 纽约", 540, 560, 140, WHITE)
        for i in range(3): car(d, 200 + i * 260, 1350, 70, CARS[i], "sus", t=t)
    else:
        for i in range(5): car(d, (i * 260 + t * 520) % 1400 - 160, 1360, 70, CARS[i % 6], "happy", t=t, spd=1, bounce=1)
        stamp(d, t, NYC2_HIT, "堵车反而少了", 540, 560, 130, GOOD)
        glow(d, 540, 560, 300, GOOD, 0.35 * pulse(t, [NYC2_HIT], 3))

# ---------- Seoul ----------
def s_seoul(t, d):
    grad(d, (30, 44, 80), (70, 90, 130)); stars(d, t, 0.3)
    skyline(d, t, (52, 66, 112), (255, 230, 160))
    u = pr(t, SEOUL_HIT, SEOUL_HIT + 1.0)
    # ground + stream
    d.rect(-40, 1080, 1120, 1500, fill=A((60, 120, 80), 1))
    sw = 200 * eio(u)
    if sw > 2:
        d.rect(-40, 1290 - sw / 2, 1120, 1290 + sw / 2, fill=A((80, 170, 240), 1))
        for i in range(8):
            x = (i * 160 + t * 120) % 1200 - 60; d.ell(x, 1290, 50, 6, A(WHITE, 0.4 * eio(u)))
    street(d, 1140, -40, 1120, 90); street(d, 1440, -40, 1120, 90)
    for i in range(4): car(d, (i * 300 + t * (200 + 500 * eio(u))) % 1400 - 150, 1170, 50, CARS[(i + 2) % 6], "happy" if u > 0.5 else "sus", t=t, spd=eio(u))
    for i in range(4): car(d, 1080 - ((i * 300 + t * (200 + 500 * eio(u))) % 1400 - 150), 1470, 50, CARS[i % 6], "happy" if u > 0.5 else "sus", t=t, spd=eio(u), dirn=-1)
    # elevated highway breaking apart
    for i in range(6):
        x0 = -40 + i * 200; fall = max(0, (t - SEOUL_HIT - i * 0.06)) ** 2 * 1800
        a = 1 - pr(t, SEOUL_HIT + 0.5, SEOUL_HIT + 1.0)
        if a <= 0: continue
        rot = fall * 0.02 * (1 if i % 2 else -1)
        d.rect(x0 + rot, 880 + fall, x0 + 200 + rot, 950 + fall, fill=A((150, 156, 176), a))
        d.rect(x0 + rot, 880 + fall, x0 + 200 + rot, 892 + fall, fill=A(WHITE, 0.3 * a))
        d.rect(x0 + 80, 950 + fall, x0 + 120, 1290 + fall, fill=A((120, 126, 150), a))
    sparks(d, 540, 950, t, SEOUL_HIT, 40, 1000, (200, 200, 220), 1, 4)
    stamp(d, t, SEOUL_HIT, "首尔 · 拆高架", 540, 500, 130, WHITE)
    if u > 0.6: stamp(d, t, SEOUL_HIT + 0.9, "车反而更快", 540, 680, 110, GOOD)

# ---------- Braess the mathematician ----------
def braess(d, x, y, s, t, mood="sus", a=1.0):
    bob = math.sin(t * 3) * s * 0.03
    d.ell(x, y, s * 0.7, s * 0.1, A((0, 0, 0), 0.25 * a))
    d.d.chord((P(x - s * 0.72), P(y - s * 1.5 + bob), P(x + s * 0.72), P(y + s * 0.4)), 180, 360, fill=A(BRAESS, a))
    d.rect(x - s * 0.72, y - s * 0.56 + bob, x + s * 0.72, y, fill=A(BRAESS, a))
    d.poly([(x - s * 0.16, y - s * 0.75 + bob), (x + s * 0.16, y - s * 0.75 + bob), (x, y - s * 0.3 + bob)], A(WHITE, a))
    d.circ(x, y - s * 1.2 + bob, s * 0.5, fill=A((250, 210, 170), a))
    d.ell(x - s * 0.2, y - s * 1.38 + bob, s * 0.12, s * 0.06, A(WHITE, 0.4 * a))
    d.d.chord((P(x - s * 0.52), P(y - s * 1.78 + bob), P(x + s * 0.52), P(y - s * 1.0 + bob)), 180, 360, fill=A((120, 90, 70), a))
    face(d, x, y - s * 1.22 + bob, s * 0.5, mood, a)
    for s_ in (-1, 1): d.circ(x + s_ * s * 0.18, y - s * 1.28 + bob, s * 0.13, outline=A((90, 200, 240), a), w=s * 0.03)
def s_why(t, d):
    grad(d, (18, 22, 46), (44, 34, 76)); stars(d, t, 0.4)
    for i in range(14):
        u = (t * 0.3 + i / 14) % 1
        d.text((i * 263) % 1000 + 40, 1500 - u * 1200, "?", 50 + i % 3 * 24, A(YEL, 0.4 * math.sin(u * math.pi)), k=1)
    braess(d, 540, 1300, 260, t, "sus" if t < WHY_HIT + 0.8 else "proud", ease(pr(t, WHY, WHY + 0.3)))
    stamp(d, t, WHY_HIT, "为什么？", 540, 420, 190, YEL)
    d.rect(300, 600, 780, 680, fill=A(BRAESS, ease(pr(t, WHY_HIT + 0.5, WHY_HIT + 0.8))), r=40)
    d.text(540, 640, "1968 · 布雷斯", 46, A(WHITE, ease(pr(t, WHY_HIT + 0.5, WHY_HIT + 0.8))), k=1)

# ---------- the network model ----------
NS, NE, NA, NB = (110, 1010), (970, 1010), (540, 620), (540, 1400)
def xflow(t):
    if t < FIRST: return 0.0
    if t < RUSH: return 1.0
    if t < CLOSE_HIT: return 1 + 3999 * eio(pr(t, RUSH, ALL))
    return 4000 * (1 - eio(pr(t, CLOSE_HIT, CLOSE_HIT + 1.0)))
def times(x):
    a = b = (4000 - x) / 2
    return (a + x) / 100 + 45, 45 + (b + x) / 100, (a + x) / 100 + (b + x) / 100, a, b
def ptpath(pts, u):
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; L = sum(seg); s = u * L
    for i, sl in enumerate(seg):
        if s <= sl: k = s / sl; return (lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k))
        s -= sl
    return pts[-1]
def tag(d, x, y, s, col, a=1.0, size=40):
    if a <= 0.01: return
    w = d.tlen(s, size, 1) + 40
    d.rect(x - w / 2, y - size * 0.75, x + w / 2, y + size * 0.75, fill=A(col, 0.95 * a), r=size * 0.6)
    d.text(x, y, s, size, A(NAVY, a), k=1)
def node(d, p, label, col, t, size=46):
    glow(d, p[0], p[1], 110, col, 0.5); d.circ(p[0], p[1], 52, fill=A(col, 1))
    d.circ(p[0] - 14, p[1] - 16, 14, fill=A(WHITE, 0.4)); d.text(p[0], p[1], label, size, A(NAVY, 1), k=1)
def road(d, p, q, narrow, k=1.0, a=1.0, hot=0.0):
    if k <= 0: return
    q2 = (lerp(p[0], q[0], k), lerp(p[1], q[1], k))
    if narrow:
        col = mix(NARROW, BAD, hot)
        d.line([p, q2], A(col, a), 38); d.line([p, q2], A(mix(col, WHITE, 0.3), 0.5 * a), 10)
    else:
        d.line([p, q2], A(ROAD, a), 76); d.line([p, q2], A(ROAD_L, 0.6 * a), 8)
def s_model(t, d):
    grad(d, NAVY, NAVY2); stars(d, t, 0.25)
    x = xflow(t); tA, tB, tC, a, b = times(x)
    hotA = cl((a + x - 2000) / 2000)
    rk = [ease(pr(t, ROADS[0], ROADS[0] + 0.5)), ease(pr(t, ROADS[1], ROADS[1] + 0.5))]
    if t < MODEL + 0.01: rk = [1, 1]
    road(d, NS, NA, True, rk[0], hot=hotA); road(d, NA, NE, False, rk[0])
    road(d, NS, NB, False, rk[1]); road(d, NB, NE, True, rk[1], hot=hotA)
    sk = ease(pr(t, SHORT_HIT, SHORT_HIT + 0.4)) if t >= SHORT_HIT else 0
    closed = t >= CLOSE_HIT
    if sk > 0:
        ga = 1 - 0.75 * ease(pr(t, CLOSE_HIT, CLOSE_HIT + 0.4)) if closed else 1
        glow(d, 540, 1010, 260, YEL, (0.35 + 0.3 * pulse(t, [SHORT_HIT], 2)) * ga)
        q2 = (540, lerp(NA[1], NB[1], sk)); d.line([NA, q2], A(YEL, ga), 44); d.line([NA, q2], A(WHITE, 0.6 * ga), 12)
        if t < ALL or closed: tag(d, 670, 1010, "0 分钟", YEL, ga * min(1, sk), 40)
    if closed:
        u = back(pr(t, CLOSE_HIT, CLOSE_HIT + 0.2))
        d.line([(470 - 10 * u, 940), (610 + 10 * u, 1080)], A(BAD, min(1, u)), 30 * u + 1)
        d.line([(610 + 10 * u, 940), (470 - 10 * u, 1080)], A(BAD, min(1, u)), 30 * u + 1)
    node(d, NA, "A", NARROW_L, t); node(d, NB, "B", NARROW_L, t)
    node(d, NS, "家", GOOD, t); node(d, NE, "公司", CYAN, t, 34)
    # rule labels
    ra = ease(pr(t, RULE_HITS[0], RULE_HITS[0] + 0.3)); rb = ease(pr(t, RULE_HITS[1], RULE_HITS[1] + 0.3))
    if t < SHORT_HIT:
        tag(d, 250, 760, "越挤越慢", NARROW_L, ra, 36); tag(d, 830, 1270, "越挤越慢", NARROW_L, ra, 36)
        tag(d, 830, 760, "45 分钟", ROAD_L, rb, 36); tag(d, 250, 1270, "45 分钟", ROAD_L, rb, 36)
    # cars
    routes = [([NS, NA, NE], a, CARS[0]), ([NS, NB, NE], b, CARS[2]), ([NS, NA, NB, NE], x, CARS[1])]
    if t >= MODEL + 0.6:
        for ri, (pts, n, col) in enumerate(routes):
            cnt = int(round(n / 4000 * 16)) if not (ri == 2 and 0 < n < 50) else 1
            ttot = [tA, tB, tC][ri]
            spd = 0.16 * 65 / max(ttot, 1)
            for i in range(cnt):
                u = (t * spd + i / max(cnt, 1) + ri * 0.13) % 1
                px, py = ptpath(pts, u)
                mood = "happy" if ttot <= 66 else ("scream" if ttot > 75 else "sus")
                if ri == 2 and n < 50:
                    mood = "happy"; glow(d, px, py - 20, 90, YEL, 0.5)
                car(d, px, py + 20, 36 if not (ri == 2 and n < 50) else 46, col, mood, t=t, bounce=0.5)
    # big readouts per phase
    if SPLIT <= t < SIL0:
        stamp(d, t, SPLIT_HIT, "各 2000 辆", 540, 450, 90, WHITE)
        tag(d, 330, 1530, f"上路 {tA:.0f} 分", CARS[0], ease(pr(t, SPLIT_HIT, SPLIT_HIT + .3)), 44)
        tag(d, 750, 1530, f"下路 {tB:.0f} 分", CARS[2], ease(pr(t, SPLIT_HIT, SPLIT_HIT + .3)), 44)
        stamp(d, t, SPLIT_HIT + 0.4, "65 分钟", 540, 320, 90, GOOD)
    elif MODEL <= t < SPLIT:
        stamp(d, t, ROADS[0], "4000 辆车", 540, 360, 120, WHITE)
    if t >= SIL0 and t < SHORT_HIT:
        d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.55))
    if SHORT_HIT <= t < FIRST:
        stamp(d, t, SHORT_HIT, "0 分钟近道！", 540, 360, 150, YEL)
    if FIRST <= t < RUSH:
        stamp(d, t, FIRST_HIT, "40 分钟", 540, 320, 190, GOOD)
        d.text(540, 480, "省了 25 分钟！", 60, A(WHITE, ease(pr(t, FIRST_HIT + .4, FIRST_HIT + .7))), k=1)
    if RUSH <= t < ALL:
        n = int(x); stamp(d, t, RUSH, "抄近道！", 540, 310, 120, YEL)
        tag(d, 540, 460, f"近道 {n} 辆 · {tC:.0f} 分钟", YEL, 1, 46)
    if ALL <= t < BACK:
        hb = pulse(t, [ALL_HIT], 3)
        stamp(d, t, ALL_HIT, "80 分钟", 540, 310, 200, BAD); glow(d, 540, 310, 320, BAD, 0.4 * hb)
        if t > ALL_HIT + 0.7: tag(d, 540, 470, "原来 65 · 慢了 15", WHITE, ease(pr(t, ALL_HIT + .7, ALL_HIT + 1.0)), 50)
    if CLOSE <= t < NAME:
        if t >= CLOSE_HIT:
            stamp(d, t, CLOSE_HIT, "封掉近道", 540, 280, 100, BAD)
            stamp(d, t, CLOSE_HIT + 0.9, "-15 分钟", 540, 430, 140, GOOD)
            glow(d, 540, 430, 300, GOOD, 0.4 * pulse(t, [CLOSE_HIT + 0.9], 3))
        else: d.text(540, 380, "如果……", 100, A(WHITE, ease(pr(t, CLOSE, CLOSE + 0.2))), k=1)

def s_back(t, d):  # nobody can go back: old road is 85 min; every driver selfish = all lose
    if t < NASH:
        grad(d, (40, 20, 34), (70, 30, 50)); stars(d, t, 0.2)
        street(d, 1150, -40, 1120, 170, mix(ROAD, BAD, 0.3))
        u = pr(t, BACK, NASH)
        cx = 300 + 160 * math.sin(min(1, u * 1.6) * math.pi)
        car(d, cx, 1210, 150, CARS[0], "scared" if t > BACK_HIT else "sus", t=t)
        d.rect(580, 980, 980, 1110, fill=A(ROAD_L, 1), r=20); d.text(780, 1045, "老路 →", 60, A(WHITE, 1), k=1)
        stamp(d, t, BACK_HIT, "85 分钟", 540, 560, 210, BAD)
        glow(d, 540, 560, 300, BAD, 0.35 * pulse(t, [BACK_HIT], 3))
        d.text(540, 760, "退回去更亏", 64, A(WHITE, ease(pr(t, BACK_HIT + .5, BACK_HIT + .8))), k=1)
        return
    grad(d, (14, 18, 40), (34, 30, 70)); stars(d, t, 0.3)
    for i in range(12):  # crowd of cars all jammed on the shortcut, each smug about its own choice
        row, colm = divmod(i, 4)
        x = 170 + colm * 245 + (row % 2) * 60; y = 1000 + row * 190
        car(d, x, y, 80, CARS[i % 6], "proud" if t < NASH_HIT + 0.8 else "scream", t=t)
    stamp(d, t, NASH_HIT, "我选最快的", 540, 420, 120, WHITE)
    stamp(d, t, NASH_HIT + 0.9, "大家一起慢", 540, 600, 130, BAD)

def s_name(t, d):
    if t < REAL2:
        rays(d, t, (60, 50, 120), (30, 26, 70), cy=900)
        braess(d, 540, 1350, 230, t, "proud")
        stamp(d, t, NAME_HIT, "布雷斯悖论", 540, 420, 160, YEL)
        glow(d, 540, 420, 380, YEL, 0.3 + 0.3 * pulse(t, [NAME_HIT], 3))
        d.rect(250, 600, 830, 700, fill=A(WHITE, ease(pr(t, NAME_HIT + .5, NAME_HIT + .8))), r=50)
        d.text(540, 650, "路多 ≠ 更快", 62, A(NAVY, ease(pr(t, NAME_HIT + .5, NAME_HIT + .8))), k=1)
        return
    grad(d, (24, 30, 70), (50, 60, 110)); stars(d, t, 0.4)
    skyline(d, t)
    street(d, 1220, -40, 1120, 200)
    for i in range(4): car(d, (i * 300 + t * 560) % 1400 - 160, 1300, 70, CARS[(i + 3) % 6], "happy", t=t, spd=1, bounce=1)
    stamp(d, t, REAL2_HIT, "纽约", 300, 520, 130, WHITE); stamp(d, t, REAL2_HIT + 0.35, "首尔", 780, 520, 130, WHITE)
    d.text(540, 720, "现实版", 80, A(GOOD, ease(pr(t, REAL2_HIT + .8, REAL2_HIT + 1.1))), k=1)

def bubble(d, x, y, s, side, col, tcol, a, size=50):
    if a <= 0: return
    w = d.tlen(s, size, 1) + 70; x0 = x if side < 0 else x - w
    d.rect(x0, y - 55, x0 + w, y + 55, fill=A(col, a), r=40)
    tx = x0 + 40 if side < 0 else x0 + w - 40
    d.poly([(tx - 15, y + 40), (tx - (25 if side < 0 else -25), y + 85), (tx + 15, y + 40)], A(col, a))
    d.text(x0 + w / 2, y, s, size, A(tcol, a), k=1)
def popk(t, t0): return min(1, back(pr(t, t0, t0 + 0.2)))
def s_end(t, d):
    grad(d, NAVY, NAVY2); stars(d, t, 0.5)
    car(d, 180, 640, 100, CARS[0], "proud", t=t)
    bubble(d, 300, 480, "早高峰我抄了近道", -1, CARS[0], NAVY, popk(t, BUBS[0]))
    car(d, 900, 960, 100, CARS[2], "proud", t=t, dirn=-1)
    bubble(d, 790, 800, "我也抄了", 1, CARS[2], NAVY, popk(t, BUBS[1]))
    car(d, 180, 1280, 100, CARS[1], "dizzy", t=t)
    bubble(d, 300, 1120, "所以都堵在近道上", -1, CARS[1], NAVY, popk(t, BUBS[2]))
    d.text(540, 1660, "Braess, Unternehmensforschung 12:258 (1968)", 28, A(WHITE, 0.6))
    d.text(540, 1700, "Kolata, The New York Times, 1990-12-25", 28, A(WHITE, 0.6))
    d.text(540, 1740, "模型数字：Easley & Kleinberg《Networks》第 8 章示例", 26, A(WHITE, 0.55))
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

def subs(t, d):
    if t >= OUTRO: return
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            lines = wrap(d, s, 58, 900)
            for j, ln in enumerate(lines):
                y = 1640 + (j - (len(lines) - 1) / 2) * 86
                w = d.tlen(ln, 58)
                d.rect(540 - w / 2 - 24, y - 44, 540 + w / 2 + 24, y + 44, fill=A((8, 10, 20), 0.82 * al), r=16)
                d.text(540, y, ln, 58, A(WHITE, al))
            break
def brand(t, d):
    d.rect(50, 80, 300, 128, fill=A((255, 255, 255), 0.16), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(WHITE, 1))
    d.rect(740, 80, 1030, 128, fill=A(YEL, 0.95), r=24); d.text(885, 104, "悖论 · 布雷斯悖论", 26, A(NAVY, 1), k=1)

SECS = [(0, HOOK_END, s_hook), (NYC, SEOUL, s_nyc), (SEOUL, WHY, s_seoul), (WHY, MODEL, s_why), (MODEL, BACK, s_model),
        (BACK, CLOSE, s_back), (CLOSE, NAME, s_model), (NAME, OUTRO, s_name), (OUTRO, 99, s_end)]
CUTS = [HOOK_END, NYC2, SEOUL, WHY, MODEL, SHORT_HIT, BACK, NASH, CLOSE, NAME, REAL2, OUTRO]
def cam(t):
    z = 1.0 + 0.05 * pulse(t, HITS, 7)
    for a, b in RISERS:
        if a <= t < b: z += 0.08 * eio(pr(t, a, b))
    if RUSH <= t < ALL: z += 0.06 * pr(t, RUSH, ALL)
    amp = 26 * pulse(t, [HOOK_HIT, SHORT_HIT], 4) + 10 * pulse(t, [ALL_HIT, SEOUL_HIT], 5) + 5 * pulse(t, HITS, 6)
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx, 960 + sy
def frame(t):
    img = Image.new("RGB", (W, H), NAVY); d = D(img)
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
