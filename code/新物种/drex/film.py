import sys, subprocess
from fx import *
from cues import *

CREAM = (246, 236, 210); YOUNG = (250, 248, 240); OLDY = (214, 170, 70); OLDY_D = (170, 126, 44)
SOIL = (92, 62, 40); SOIL_D = (60, 40, 26); NAVYT = (24, 20, 40); GOOD = (110, 225, 130); BAD = (255, 80, 70)
MOREL = (176, 130, 84); CORD = (210, 150, 60); DINO = (96, 170, 90); DINO_D = (64, 126, 64); BARK = (120, 84, 54); LEAFC = (80, 160, 90)
GOLD = (255, 200, 60)

def drex(d, x, y, h, t, mood="proud", a=1.0, age=1.0, sq=0.0, crown=0.0, branch=1.0, look=0.0, lobes=1):
    """giant upright stroma standing on (x,y), height h. age 0 = white powdery, 1 = dark yellow."""
    col = mix(YOUNG, OLDY, age); dk = mix((220, 214, 200), OLDY_D, age)
    w = h * 0.28 * (1 + sq); hh = h * (1 - sq * 0.6); wob = math.sin(t * 2.4) * h * 0.012
    d.ell(x, y, w * 1.5, h * 0.05, A((0, 0, 0), 0.25 * a))
    offs = [0] if lobes == 1 else [-w * 0.55, w * 0.55]
    for k, ox in enumerate(offs):
        xx = x + ox; ww = w if lobes == 1 else w * 0.75; top = y - hh + (0 if k == 0 else hh * 0.08)
        d.rect(xx - ww, top + ww * 0.6, xx + ww, y, fill=A(dk, a), r=ww * 0.5)
        d.rect(xx - ww + 6, top + ww * 0.6, xx + ww - ww * 0.25, y - 4, fill=A(col, a), r=ww * 0.45)
        # garlic-bulb head
        d.ell(xx + wob, top + ww * 0.55, ww * 1.12, ww * 0.95, A(dk, a))
        d.ell(xx + wob - ww * 0.08, top + ww * 0.5, ww * 1.0, ww * 0.85, A(col, a))
        for j in (-1, 0, 1): d.arc(xx + wob + j * ww * 0.35, top + ww * 0.6, ww * 0.35, ww * 0.8, 200, 340, A(dk, 0.5 * a), max(3, ww * 0.05))
        d.ell(xx + wob - ww * 0.45, top + ww * 0.25, ww * 0.25, ww * 0.12, A(WHITE, 0.55 * a))
        if branch > 0:   # finger-like branches when mature
            for j, (bx, ang) in enumerate([(-0.7, -2.4), (0.75, -0.7), (0.2, -1.4)]):
                L = ww * 0.9 * branch; sx, sy = xx + wob + bx * ww * 0.8, top + ww * 0.3
                ex, ey = sx + math.cos(ang) * L, sy + math.sin(ang) * L + math.sin(t * 3 + j) * 4
                d.line([(sx, sy), (ex, ey)], A(col, a), ww * 0.28); d.circ(ex, ey, ww * 0.15, fill=A(col, a))
        if age < 0.6:   # white powdery fibres
            r2 = random.Random(7 + k)
            for i in range(40):
                px = xx + r2.uniform(-ww * 0.9, ww * 0.9); py = r2.uniform(top, y - 10)
                d.circ(px, py, r2.uniform(3, 7), fill=A(WHITE, (0.6 - age) * 1.4 * a))
        d.rect(xx - ww * 0.75, top + ww * 1.4, xx - ww * 0.55, y - 20, fill=A(WHITE, 0.25 * a), r=6)
    fy = y - hh * 0.5
    face(d, x, fy, min(w, h * 0.3) * 0.95, mood, a, look)
    if crown > 0:
        cy = y - hh - (w if lobes == 1 else 0) * 0.25 - 10; cw = w * 0.9 * crown
        glow(d, x, cy - cw * 0.3, cw * 1.6, GOLD, 0.4 * crown)
        d.poly([(x - cw, cy), (x - cw, cy - cw * 0.7), (x - cw * 0.5, cy - cw * 0.3), (x, cy - cw * 0.9), (x + cw * 0.5, cy - cw * 0.3), (x + cw, cy - cw * 0.7), (x + cw, cy)], A(GOLD, a))
        for j in (-1, 0, 1): d.circ(x + j * cw * 0.5, cy - cw * 0.15, cw * 0.1, fill=A(BAD if j else (90, 200, 255), a))

def ground(d, y, t, col=SOIL, top=(70, 140, 70)):
    d.rect(-50, y, OW + 50, OH + 50, fill=A(col, 1)); d.rect(-50, y, OW + 50, y + 26, fill=A(top, 1))
    r2 = random.Random(2)
    for i in range(30): d.circ(r2.uniform(0, 1080), r2.uniform(y + 50, 1900), r2.uniform(5, 14), fill=A(SOIL_D, 0.6))
def forest(d, t, c1=(40, 110, 80), c2=(16, 50, 40)):
    grad(d, c1, c2)
    for i in range(7):
        x = 40 + i * 170 + 30 * math.sin(i * 3); w = 50 + 20 * (i % 3)
        d.rect(x - w / 2, 0, x + w / 2, 1500, fill=A(mix(c2, (0, 0, 0), 0.2), 0.7), r=10)
    for i in range(14):
        d.circ((i * 157) % 1080, 120 + (i * 71) % 400, 160 + (i % 3) * 40, fill=A(mix(c1, (120, 200, 120), 0.2), 0.35))
def lilshroom(d, x, y, s, col, mood="scared", a=1.0, sq=0.0):
    d.rect(x - s * 0.25, y - s * 0.8, x + s * 0.25, y, fill=A(CREAM, a), r=s * 0.2)
    d.d.chord((P(x - s * 0.7), P(y - s * 1.4), P(x + s * 0.7), P(y - s * 0.4)), 180, 360, fill=A(col, a))
    face(d, x, y - s * 0.45, s * 0.35, mood, a)
def morel(d, x, y, s, mood, a=1.0):
    d.rect(x - s * 0.25, y - s * 0.7, x + s * 0.25, y, fill=A(CREAM, a), r=s * 0.2)
    d.ell(x, y - s * 1.2, s * 0.45, s * 0.65, A(MOREL, a))
    for i in range(4):
        for j in range(3): d.circ(x - s * 0.25 + j * s * 0.25, y - s * 1.6 + i * s * 0.25, s * 0.08, fill=A(mix(MOREL, (0, 0, 0), 0.35), a))
    face(d, x, y - s * 0.4, s * 0.3, mood, a)
def cordy(d, x, y, s, mood, a=1.0):
    d.ell(x, y - s * 0.3, s * 0.7, s * 0.28, A((230, 200, 140), a))
    for i in range(5): d.arc(x - s * 0.5 + i * s * 0.25, y - s * 0.3, s * 0.1, s * 0.25, 0, 360, A((200, 160, 100), a), s * 0.04)
    d.line([(x + s * 0.3, y - s * 0.5), (x + s * 0.4, y - s * 1.6)], A(CORD, a), s * 0.12)
    face(d, x - s * 0.15, y - s * 0.3, s * 0.3, mood, a)
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
def swirl(d, t, c1, c2, cx=540, cy=900):
    grad(d, c1, c2)
    for i in range(9):
        r = ((t * 120 + i * 140) % 1300)
        d.circ(cx, cy, r, outline=A(mix(c1, WHITE, 0.25), 0.18 * (1 - r / 1300)), w=40)
def dino(d, x, y, s, t, a=1.0, fall=0.0, mood="happy"):
    # simple cartoon T-rex facing right; fall rotates it onto its back (approximate by squash + offset)
    yy = y + fall * s * 0.4
    d.poly([(x - s * 1.4, yy - s * 0.5 - fall * s * 0.3), (x - s * 0.3, yy - s * 0.9), (x - s * 0.2, yy - s * 0.4)], A(DINO, a))   # tail
    d.ell(x, yy - s * 0.7, s * 0.6, s * 0.5 * (1 - 0.3 * fall), A(DINO, a))
    d.ell(x + s * 0.55, yy - s * 1.25 + fall * s * 0.6, s * 0.45, s * 0.3, A(DINO, a))   # head
    for k in (-1, 1):
        lx = x + k * s * 0.2
        if fall < 0.5: d.rect(lx - s * 0.1, yy - s * 0.4, lx + s * 0.1, yy, fill=A(DINO_D, a), r=s * 0.05)
        else: d.line([(lx, yy - s * 0.6), (lx + k * s * 0.15, yy - s * 1.1)], A(DINO_D, a), s * 0.18)
    d.line([(x + s * 0.4, yy - s * 0.8), (x + s * 0.55, yy - s * 0.65)], A(DINO_D, a), s * 0.07)
    ex, ey = x + s * 0.65, yy - s * 1.35 + fall * s * 0.6
    if fall > 0.5:
        d.line([(ex - 12, ey - 12), (ex + 12, ey + 12)], A(INK, a), 7); d.line([(ex - 12, ey + 12), (ex + 12, ey - 12)], A(INK, a), 7)
    else: d.circ(ex, ey, s * 0.08, fill=A(WHITE, a)); d.circ(ex + 3, ey, s * 0.045, fill=A(INK, a))
    for i in range(4): d.poly([(x + s * 0.6 + i * s * 0.08, ey + s * 0.18), (x + s * 0.64 + i * s * 0.08, ey + s * 0.28), (x + s * 0.68 + i * s * 0.08, ey + s * 0.18)], A(WHITE, a))
def tree(d, x, y, s, t, dead=0.0, a=1.0):
    bc = mix(BARK, (90, 80, 76), dead); lc = mix(LEAFC, (150, 120, 70), dead)
    d.rect(x - s * 0.18, y - s * 1.6, x + s * 0.18, y, fill=A(bc, a), r=s * 0.06)
    for i, (cx, cy, r) in enumerate([(-0.45, -1.7, 0.55), (0.45, -1.75, 0.55), (0, -2.15, 0.65), (0, -1.5, 0.5)]):
        d.circ(x + cx * s, y + cy * s + dead * s * 0.1, r * s * (1 - 0.65 * dead), fill=A(lc, a * (1 - 0.5 * dead)))
    for k in (-1, 1): d.line([(x, y), (x + k * s * 0.6, y + s * 0.35)], A(bc, a * 0.8), s * 0.08)

# ---------------- scenes ----------------
def s_hook(t, d):
    if t < HOOK_HIT: forest(d, t)
    else: rays(d, t, (255, 190, 60), (230, 140, 30), n=20, cx=540, cy=1100)
    ground(d, 1240, t)
    k = ease(pr(t, HOOK_HIT - 0.1, HOOK_HIT + 0.35))
    for i, x in enumerate([230, 380, 700, 860]):   # little mushrooms get blown away
        fl = max(0, t - HOOK_HIT) * (1 if x > 540 else -1)
        lilshroom(d, x + fl * 700, 1240 - max(0, t - HOOK_HIT) * 500 + 900 * max(0, t - HOOK_HIT) ** 2, 70, [(220, 70, 60), (240, 170, 60), (180, 120, 220), (90, 180, 230)][i], "scared" if t > HOOK_HIT else "happy")
    h = 640 * (0.15 + 0.85 * k)
    sq = 0.15 * math.exp(-max(t - HOOK_HIT, 0) * 6) * math.sin(max(t - HOOK_HIT, 0) * 35) if t > HOOK_HIT else 0
    drex(d, 540, 1240, h, t, "proud" if t > HOOK_HIT + 0.3 else "scream", age=0.85, sq=sq)
    sparks(d, 540, 1240, t, HOOK_HIT, n=60, spd=1200, col=(180, 130, 80), seed=3)
    d.rect(-50, 1240, OW + 50, 1266, fill=A((70, 140, 70), 1))
    stamp(d, t, HOOK_HIT, "菌中霸王龙！", 540, 330, 120, WHITE)
def s_size(t, d):
    grad(d, (60, 160, 200), (30, 100, 150)); ground(d, 1240, t, (60, 90, 120), (90, 130, 160))
    drex(d, 420, 1240, 600, t, "proud", age=0.85)
    d.rect(700, 600, 740, 1240, fill=A(WHITE, 0.9), r=8)
    for i in range(6):
        y = 1240 - i * 128; k = popk(t, RTICKS[min(i, 3)]) if i > 0 else 1
        d.rect(690, y - 3, 760, y + 3, fill=A(NAVYT, 1))
        if i > 0 and t > RTICKS[min(i - 1, 3)]: d.text(790, y, f"{i * 10}", 40, A(WHITE, 1), anchor="lm", k=1)
    if t > RTICKS[-1]: stamp(d, t, RTICKS[-1], "50 厘米", 540, 320, 110, YEL)
    if t > CASE_HIT:   # carry-on suitcase pops beside
        k = popk(t, CASE_HIT); cx = 860; ch = 560 * k
        d.rect(cx - 90 * k, 1240 - ch, cx + 90 * k, 1240, fill=A((230, 80, 90), 1), r=20)
        d.rect(cx - 30 * k, 1240 - ch - 60 * k, cx + 30 * k, 1240 - ch, outline=A((60, 60, 70), 1), w=10, r=8)
        tag(d, cx - 20, 1240 - ch - 110, "登机箱", WHITE, k, 38)
def s_scale(t, d):
    grad(d, (240, 120, 160), (190, 70, 120))
    k = ease(pr(t, SCALE, KG_HIT))
    d.rect(250, 1060 + 20 * k, 830, 1140 + 20 * k, fill=A((220, 224, 236), 1), r=24); d.rect(330, 1140 + 20 * k, 750, 1220, fill=A((180, 186, 200), 1), r=20)
    d.rect(420, 1160, 660, 1210, fill=A((30, 40, 50), 1), r=10)
    v = 2.2 * k + (0.03 * math.sin(t * 40) if t < KG_HIT else 0)
    d.text(540, 1186, f"{v:.1f} kg", 36, A((120, 255, 140), 1), k=1)
    drex(d, 540, 1060 + 20 * k, 420, t, "proud" if t > KG_HIT else "sus", age=0.85, lobes=2, sq=0.08 * pulse(t, [KG_HIT], 7))
    stamp(d, t, KG_HIT, "2.2 公斤", 540, 320, 120, WHITE)
    for i, h in enumerate(BOTTLES):
        kk = popk(t, h); bx = 300 + i * 160; by = 470
        if kk > 0:
            d.rect(bx - 30 * kk, by - 70 * kk, bx + 30 * kk, by + 70 * kk, fill=A((140, 210, 255), 0.95), r=14)
            d.rect(bx - 16 * kk, by - 92 * kk, bx + 16 * kk, by - 70 * kk, fill=A((40, 120, 220), 1), r=4)
            d.rect(bx - 30 * kk, by - 10, bx + 30 * kk, by + 20, fill=A(WHITE, 0.8))
    if t > BOTTLES[-1]: d.text(540, 600, "≈ 4 瓶矿泉水", 52, A(WHITE, ease(pr(t, BOTTLES[-1], BOTTLES[-1] + 0.3))), k=1)
def s_rec(t, d):
    rays(d, t, (120, 90, 200), (70, 50, 150), n=16, cx=540, cy=1240); ground(d, 1240, t, (60, 40, 110), (110, 80, 180))
    drex(d, 540, 1240, 560, t, "proud", age=0.85, crown=popk(t, CROWN_HIT), sq=0.1 * pulse(t, [CROWN_HIT], 7))
    if t > RIVALS[0]: morel(d, 230, 1240, 120 * popk(t, RIVALS[0]), "scared"); tag(d, 230, 1000, "羊肚菌", WHITE, popk(t, RIVALS[0]), 38)
    if t > RIVALS[1]: cordy(d, 860, 1240, 130 * popk(t, RIVALS[1]), "scared"); tag(d, 860, 1000, "冬虫夏草", WHITE, popk(t, RIVALS[1]), 38)
    stamp(d, t, CROWN_HIT, "子囊菌之王", 540, 320, 110, GOLD)
def s_look(t, d):
    grad(d, (250, 220, 120), (230, 170, 60))
    age = 0 if t < GROW[1] else ease(pr(t, GROW[1], GROW[1] + 0.6))
    br = ease(pr(t, GROW[2], GROW[2] + 0.4))
    ground(d, 1240, t, (140, 100, 50), (110, 160, 80))
    drex(d, 540, 1240, 600, t, "happy" if age < 0.5 else "proud", age=age, branch=br, sq=0.08 * pulse(t, GROW, 8))
    labs = ["白粉外衣", "变暗黄", "伸出手指"]
    for i, h in enumerate(GROW):
        if t > h: tag(d, 540, 340 + i * 0, labs[i], WHITE if i != 1 else NAVYT, popk(t, h) * (1 if (i == 2 or t < GROW[min(i + 1, 2)]) else 0), 64, NAVYT if i != 1 else WHITE)
    if t > GROW[1]:   # garlic hint
        k = popk(t, GROW[1] + 0.3); d.text(800, 520, "像蒜头", 44, A(NAVYT, k), k=1)
        d.ell(800, 600, 50 * k, 44 * k, A(WHITE, k)); d.line([(800, 556), (800, 530)], A((120, 170, 90), k), 8)
def helix(d, t, x, y0, y1, a=1.0):
    for i in range(36):
        y = lerp(y0, y1, i / 35); ph = t * 3 + i * 0.45
        x1 = x + math.sin(ph) * 110; x2 = x - math.sin(ph) * 110
        d.line([(x1, y), (x2, y)], A(WHITE, 0.25 * a), 5)
        d.circ(x1, y, 14, fill=A((255, 120, 160), a)); d.circ(x2, y, 14, fill=A((110, 200, 255), a))
def s_dna(t, d):
    k = pr(t, DNA, SIL0)
    grad(d, mix((30, 60, 100), (6, 10, 20), k), mix((14, 24, 50), (2, 4, 8), k))
    helix(d, t * (1 + 3 * k), 540, 380, 1180, 1 - 0.3 * k)
    drex(d, 220, 1240, 360, t, "sus", age=0.85)
    for i in range(3): d.text(760 + 40 * math.sin(t * 5 + i), 620 + i * 160, "?", 90, A(YEL, 0.8 * (1 - k)), k=1)
    if t >= SIL0: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.6))
def s_fam(t, d):
    rays(d, t, (80, 200, 140), (30, 140, 100), n=22, cx=540, cy=900)
    glow(d, 540, 900, 520, (255, 240, 150), 0.5 * pulse(t, [FAM_HIT], 2))
    # family tree: 16 known families as small leaves + one new big branch
    root = (540, 1220)
    for i in range(16):
        ang = math.pi + (i + 0.5) / 16 * math.pi * 0.9 + 0.05 * math.pi
        ex, ey = 540 + math.cos(ang) * 420, 1220 + math.sin(ang) * 620
        if ex > 640: continue
        d.line([root, (ex, ey)], A(WHITE, 0.5), 6); d.circ(ex, ey, 22, fill=A(WHITE, 0.7))
    k = back(pr(t, FAM_HIT, FAM_HIT + 0.35))
    ex, ey = lerp(540, 830, k), lerp(1220, 640, k)
    d.line([root, (ex, ey)], A(GOLD, 1), 14)
    if k > 0.3: drex(d, ex, ey + 140, 300 * k, t, "proud", age=0.85, crown=k)
    sparks(d, 830, 640, t, FAM_HIT, n=70, spd=1200, col=(255, 230, 120), seed=5)
    stamp(d, t, FAM_HIT, "新的一科！", 540, 330, 130, WHITE)
    if t > FAM_HIT + 0.8: tag(d, 540, 500, "滇菌科 Dianjunaceae", WHITE, ease(pr(t, FAM_HIT + .8, FAM_HIT + 1.1)), 48, (30, 120, 80))
def s_name(t, d):
    grad(d, (200, 70, 60), (130, 30, 40))
    for i in range(10): d.rect(0, 260 + i * 120, 1080, 262 + i * 120, fill=A(WHITE, 0.06))
    parts = [("滇", "古滇国", 260), ("菌", "菌子", 540), ("rex", "君王", 820)]
    for i, (ch, lab, x) in enumerate(parts):
        k = popk(t, NAME_HITS[i])
        if k > 0:
            d.rect(x - 120 * k, 470 - 120 * k, x + 120 * k, 470 + 120 * k, fill=A((255, 236, 200), 1), r=30)
            d.text(x, 470, ch, int((130 if i < 2 else 90) * k), A((150, 30, 40), 1), k=1)
            d.text(x, 640, lab, 44, A(WHITE, k), k=1)
    drex(d, 360, 1220, 400, t, "proud", age=0.85, crown=1)
    if t > NAME_HITS[2]:
        k = popk(t, NAME_HITS[2]); dino(d, 760, 1220, 200 * k, t)
        d.text(760, 870, "T. rex", 44, A(WHITE, k), k=1)
def s_ext(t, d):
    grad(d, (255, 140, 60), (150, 40, 30))
    ground(d, 1240, t, (110, 60, 40), (140, 120, 60))
    k = pr(t, EXT, ROCK_HIT)
    ax, ay = lerp(1100, 640, k), lerp(-100, 1150, k)
    if t < ROCK_HIT:
        for j in range(8): d.circ(ax + j * 40, ay - j * 90, 70 - j * 7, fill=A((255, 220, 120), 0.5 - j * 0.05))
        d.circ(ax, ay, 70, fill=A((110, 90, 80), 1)); d.circ(ax - 20, ay - 20, 16, fill=A((80, 64, 58), 1))
    fall = ease(pr(t, DINO_FALL - 0.3, DINO_FALL + 0.2))
    dino(d, 380, 1240, 220, t, fall=fall)
    if t >= ROCK_HIT:
        u = t - ROCK_HIT
        glow(d, 640, 1150, 700, (255, 240, 180), max(0, 1 - u * 0.8))
        sparks(d, 640, 1150, t, ROCK_HIT, n=80, spd=1500, col=(255, 200, 100), seed=9, life=1.6)
        flash(d, t, [ROCK_HIT], WHITE, 0.6)
    stamp(d, t, ROCK_HIT, "6500 万年前", 540, 330, 110, WHITE)
    if t > DINO_FALL: tag(d, 540, 500, "恐龙灭绝", WHITE, popk(t, DINO_FALL), 52, (150, 40, 30))
def s_rise(t, d):
    k = ease(pr(t, RISE, UP_HIT))
    grad(d, mix((80, 70, 70), (90, 180, 140), k), mix((40, 34, 34), (40, 110, 80), k))
    ground(d, 1240, t, (90, 70, 50), mix((110, 100, 80), (80, 160, 80), k))
    for i, x in enumerate([180, 900]): d.ell(x, 1230, 120, 40, A((200, 190, 170), 0.6))   # bones
    for i in range(3): d.circ(170 + i * 60, 1200, 20, fill=A((230, 225, 210), 0.7))
    s = 120 + 460 * ease(pr(t, SPROUT_HIT, UP_HIT + 0.3))
    if t > SPROUT_HIT - 0.1:
        drex(d, 540, 1240, s, t, "happy" if t < UP_HIT else "proud", age=0.85, branch=ease(pr(t, UP_HIT, UP_HIT + 0.4)), sq=0.1 * pulse(t, [SPROUT_HIT, UP_HIT], 7))
    stamp(d, t, SPROUT_HIT, "废墟里登场", 540, 330, 110, WHITE)
    if t > UP_HIT: tag(d, 540, 500, "滇菌家族的祖先", WHITE, popk(t, UP_HIT), 48, (40, 110, 80))
def s_life(t, d):
    forest(d, t, (90, 170, 220), (40, 100, 160))
    ground(d, 1240, t)
    dead = ease(pr(t, TREE_DIE, TREE_DIE + 0.4))
    tree(d, 540, 1240, 300, t, dead)
    if t < BURST_HIT:   # hidden ghost inside the trunk
        a_ = popk(t, INSIDE_HIT) * 0.85
        d.rect(500, 820, 580, 1180, fill=A(mix(OLDY, WHITE, 0.3), a_), r=40); glow(d, 540, 1000, 120, YEL, a_ * 0.6)
        face(d, 540, 1000, 40, "chill", a_, look=math.sin(t * 2))
        tag(d, 780, 980, "躲在活树里", WHITE, popk(t, INSIDE_HIT), 40)
    else:
        k = back(pr(t, BURST_HIT, BURST_HIT + 0.35))
        drex(d, 540, 1240, 560 * k, t, "proud", age=0.85, sq=0.12 * pulse(t, [BURST_HIT], 7))
        sparks(d, 540, 1200, t, BURST_HIT, n=50, spd=1000, col=(200, 160, 100), seed=11)
    if t > TREE_DIE: tag(d, 540, 330, "树一死……", WHITE, popk(t, TREE_DIE) * (1 - pr(t, BURST_HIT - 0.1, BURST_HIT)), 64)
    stamp(d, t, BURST_HIT, "冒出来！", 540, 330, 120, WHITE)
def s_gene(t, d):
    grad(d, (60, 70, 120), (30, 34, 70))
    # two toolboxes: relative ~600 tools vs D-rex ~220
    for i, (x, n, lab, c) in enumerate([(320, 600, "近亲 535–635", (150, 160, 190)), (760, 220, "霸王滇菌 ≈220", (240, 190, 80))]):
        k = popk(t, GENE_HIT + i * 0.3)
        hgt = 520 * n / 600 * ease(pr(t, GENE_HIT + i * 0.3, GENE_HIT + i * 0.3 + 0.5))
        d.rect(x - 110, 1080 - hgt, x + 110, 1080, fill=A(c, 1), r=20)
        for j in range(int(hgt / 40)): d.rect(x - 80, 1060 - j * 40, x + 80, 1064 - j * 40, fill=A(WHITE, 0.25))
        d.text(x, 1130, lab, 36, A(WHITE, k), k=1)
    d.text(540, 470, "分解植物的酶基因", 52, A(WHITE, ease(pr(t, GENE, GENE + 0.3))), k=1)
    if t > BIG_HIT2:
        k = popk(t, BIG_HIT2)
        stamp(d, t, BIG_HIT2, "省下来长个子", 540, 330, 96, YEL)
        drex(d, 760, 560 + 300, 240 * k, t, "proud", age=0.85, branch=1)
def s_yun(t, d):
    grad(d, (40, 150, 120), (20, 90, 80))
    # Yunnan blob map
    pts = [(540 + 300 * math.cos(a) * (1 + 0.15 * math.sin(a * 5)), 820 + 330 * math.sin(a) * (1 + 0.12 * math.cos(a * 3))) for a in [i / 40 * 2 * math.pi for i in range(40)]]
    d.poly(pts, A((120, 210, 150), 1))
    r2 = random.Random(4)
    n_show = int(lerp(0, 60, ease(pr(t, YUN_HIT, YUN2_HIT))))
    for i in range(60):
        x, y = 540 + r2.uniform(-220, 220), 820 + r2.uniform(-240, 240)
        if i < n_show: lilshroom(d, x, y, 22, [(220, 70, 60), (240, 170, 60), (180, 120, 220), (90, 180, 230), (250, 240, 230)][i % 5], "happy")
        elif t > YUN2_HIT: d.text(x, y, "?", 34, A(WHITE, 0.8 * popk(t, YUN2_HIT + (i % 10) * 0.03)), k=1)
    v = int(lerp(0, 6000, ease(pr(t, YUN_HIT, YUN_HIT + 0.8))))
    if t < YUN2_HIT: stamp(d, t, YUN_HIT, f"{v} 种", 540, 330, 110, WHITE)
    else: stamp(d, t, YUN2_HIT, "10 万+ ？", 540, 330, 120, YEL)
def s_end(t, d):
    rays(d, t, (255, 200, 90), (240, 150, 50), n=16, cx=540, cy=1240)
    ground(d, 1240, t)
    drex(d, 540, 1240, 560, t, "happy", age=0.85, crown=1)
    bubble(d, 300, 380, "我的兄弟还没被发现", -1, WHITE, NAVYT, popk(t, BUBS[0]), 40)
    bubble(d, 800, 500, "野外别乱采乱吃", 1, (200, 60, 50), WHITE, popk(t, BUBS[1]), 40)
    d.text(540, 1330, "Yu F. et al., Front. Fungal Biol. 7:1940464 (2026)", 24, A(WHITE, 0.85))
    d.text(540, 1370, "中国科学院昆明植物研究所", 24, A(WHITE, 0.8))
    stamp(d, t, BUBS[2], "霸王滇菌", 540, 300, 100, WHITE)
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

SECS = [(0, HOOK_END, s_hook), (SIZE, SCALE, s_size), (SCALE, REC, s_scale), (REC, LOOK, s_rec), (LOOK, DNA, s_look),
        (DNA, FAM_HIT, s_dna), (FAM_HIT, NAME, s_fam), (NAME, EXT, s_name), (EXT, RISE, s_ext), (RISE, LIFE, s_rise),
        (LIFE, GENE, s_life), (GENE, YUN, s_gene), (YUN, OUTRO, s_yun), (OUTRO, 99, s_end)]
CUTS = [HOOK_END, SCALE, REC, LOOK, DNA, FAM_HIT, NAME, EXT, RISE, LIFE, GENE, YUN, OUTRO]
def cam(t):
    z = 1.0 + 0.05 * pulse(t, HITS, 7)
    for a, b in RISERS:
        if a <= t < b: z += 0.1 * eio(pr(t, a, b))
    amp = 26 * pulse(t, [HOOK_HIT, FAM_HIT, ROCK_HIT], 4) + 5 * pulse(t, HITS, 6)
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
