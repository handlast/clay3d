import sys, subprocess
from doodle import *
from fx import *
from parts import *
from cues import *

BUNC = (252, 247, 236); BUN_S = (232, 220, 198); MEAT = (196, 120, 90); ESO = (232, 176, 140)
CTBG = (16, 20, 34); BONE = (225, 230, 240); SOFT = (120, 128, 150)

def bun(d, x, y, r, t, a=1.0, seed=0, cut=0.0, slide=0.0):
    """steamed bun seen from the side; cut>0 draws two dashed cut lines, slide moves right third out."""
    ry = r * 0.72
    d.ell(x, y, r, ry, A(BUNC, a)); d.ell(x - r * 0.15, y + ry * 0.35, r * 0.75, ry * 0.45, A(BUN_S, 0.45 * a))
    d.ell(x - r * 0.35, y - ry * 0.4, r * 0.25, ry * 0.18, A(WHITE, 0.8 * a))
    ring(d, x, y, ry, t, INKC, 9, a, seed, rx=r)
    for k in range(-3, 4):  # pleats converging to the top knot
        ink(d, [(x + k * r * 0.13, y - ry * 0.55 + abs(k) * ry * 0.08), (x, y - ry * 0.92)], t, INKC, 5, a * 0.7, seed + 10 + k, 1.4)
    if cut > 0:
        for sx in (-1, 1):
            cx = x + sx * r * 0.34
            for j in range(7):
                y0 = y - ry * 1.05 + j * ry * 0.32
                if (y0 - y) / (ry * 1.05) < 1: d.line([(cx, y0), (cx, y0 + ry * 0.18 * cut)], A(RED2, a), 6)
    if slide > 0:
        sx_ = x + r * 0.34 + slide * r * 1.1; sy_ = y - slide * r * 0.15
        d.rect(x + r * 0.34, y - ry, x + r * 1.05, y + ry, fill=A(PAPER, a))   # erase the third from the bun
        d.ell(sx_ + r * 0.33, sy_, r * 0.36, ry * 0.95, A(BUNC, a)); ring(d, sx_ + r * 0.33, sy_, ry * 0.95, t, INKC, 8, a, seed + 30, rx=r * 0.36)
        d.ell(sx_ + r * 0.05, sy_, r * 0.09, ry * 0.75, A(MEAT, a))   # filling on the cut face

def eso(d, t, bolus=None, a=1.0):
    pts = [(700, 700), (620, 740), (528, 820), (512, 950), (506, 1160)]
    d.line(pts, A(ESO, a), 44); ink(d, pts, t, (190, 120, 100), 5, 0.6 * a, 1501)
    if bolus is not None:
        bx, by = bolus
        d.ell(bx, by, 64, 50, A(BUNC, a)); ring(d, bx, by, 50, t, INKC, 8, a, 1502, rx=64)
        d.ell(bx + 14, by + 8, 20, 14, A(MEAT, a))

def s_hook(t, d):
    paper(d, t)
    hit = t >= GULP_HIT
    u = pr(t, 0, GULP_HIT)
    sh = 10 * math.sin(t * 70) * (1 - pr(t, GULP_HIT, GULP_HIT + 1.5)) if hit else 0
    bigface(d, 540 + sh, 1050, 290, t, "shock" if hit else "happy", puff=(0.9 * (1 - pr(t, GULP_HIT, GULP_HIT + 2))) if hit else 0.0,
            red=0.55 if hit else 0.0, mouth="clamp" if hit else "ah", sweat=1.0 if hit else 0, seed=10)
    if not hit:   # bun flies into mouth
        bx = lerp(900, 540, eio(u)); by = lerp(420, 1180, eio(u)); s = lerp(200, 90, eio(u))
        bun(d, bx, by, s, t, 1, 20)
        dtext(d, 540, 360, "啊——呜", int(170 * (0.75 + 0.25 * u)), RED2, 1, t, 1)
    else:
        k = pop(t, GULP_HIT, 0.2)
        d.text(540, 380, "咕咚！", int(240 * (0.5 + 0.5 * k)) + 1, A(RED2, 1), k=1)
        rings(d, 540, 1300, t, [GULP_HIT], RED2, 0.8, 520)
        sparks(d, 540, 1300, t, GULP_HIT, 30, 1100, YEL2, 1, 3)
        # lump sliding down the throat
        v = pr(t, GULP_HIT, GULP_HIT + 1.2)
        if v < 1: d.ell(540, 1380 + v * 140, 70 * (1 - v * 0.3), 46, A(SKIN_D, 0.9))
        if t > GULP_HIT + 1.3:
            dtext(d, 540, 1490, "然后呢？", 90, INKC, ease(pr(t, GULP_HIT + 1.3, GULP_HIT + 1.6)), t, 2)

def s_case(t, d):
    paper(d, t)
    k = min(1, pop(t, CASE_HIT) * 1.5)
    box(d, 140, 330, 940, 760, t, INKC, 9, k, 301, fill=(255, 252, 244))
    dtext(d, 540, 420, "日本 · 川崎", 70, INKC, k, t, 302)
    dtext(d, 540, 540, "2026", int(180 * (0.6 + 0.4 * pop(t, CASE_HIT))) + 1, RED2, k, t, 303)
    dtext(d, 540, 680, "国际急诊医学杂志 · 病例报告", 44, MUTE, k, t, 304)
    k2 = pop(t, AGE_HIT)
    bigface(d, 480, 1180, 210, t, "happy", mouth="smile", seed=310)
    bun(d, 800, 1290, 120, t, 1, 320)
    if t >= AGE_HIT:
        d.rect(690, 900, 1000, 1010, fill=A(YEL2, 1), r=30); d.text(845, 955, "20 多岁", int(60 * (0.6 + 0.4 * k2)) + 1, A(INKC, 1), k=1)

def s_bun(t, d):
    paper(d, t)
    cut = pr(t, CUT - 0.3, CUT); slide = ease(pr(t, CUT + 0.2, CUT + 0.7))
    up = ease(pr(t, CUT + 1.0, BUN + 3.0))
    bun(d, 470, 860, 260, t, 1, 401, cut=cut, slide=slide if up <= 0 else 0)
    if up > 0:  # the third flies up toward the mouth (off screen)
        sx = 470 + 260 * 0.34 + 260 * 1.1 + 260 * 0.33; sy = 860 - 40 - up * 900
        d.ell(sx, sy, 94, 180, A(BUNC, 1)); ring(d, sx, sy, 180, t, INKC, 8, 1, 431, rx=94)
        dtext(d, 780, 1000, "不嚼！", 90, RED2, ease(pr(t, CUT + 1.0, CUT + 1.3)), t, 432)
    # ruler
    k = pop(t, RULER)
    if t >= RULER:
        x0, x1 = 210, 730
        d.rect(x0 - 20, 1120, x1 + 20, 1220, fill=A((255, 230, 150), min(1, k)), r=10)
        for i in range(11):
            xx = lerp(x0, x1, i / 10); d.line([(xx, 1120), (xx, 1120 + (50 if i % 5 == 0 else 30))], A(INKC, min(1, k)), 4)
        d.text(470, 1300, "10 厘米", int(110 * (0.6 + 0.4 * k)) + 1, A(INKC, min(1, k)), k=1)
    if t >= CUT + 0.2 and up <= 0.3:
        k3 = pop(t, CUT + 0.2)
        d.text(860, 560, "1/3", int(200 * (0.5 + 0.5 * k3)) + 1, A(RED2, 1 - pr(t, CUT + 1.0, CUT + 1.4)), k=1)

def s_stuck(t, d):
    paper(d, t)
    profile(d, t, press=0.25, red=0.2)
    eso(d, t, bolus=(640, 735))
    # tight rings around the throat
    sq = 0.5 + 0.5 * math.sin(t * 9)
    for j in range(3): d.arc(640, 735, 110 + j * 26 + 8 * sq, 70 + j * 18, 200, 340, A(RED2, 0.6 - j * 0.15), 7)
    # water glass pouring at WATER beats, drops stop at the bolus
    gx, gy = 900, 420
    tilt = 0.5 if t > WATER[0] - 0.3 else 0
    d.poly([(gx - 60, gy - 90), (gx + 60, gy - 90 + tilt * 60), (gx + 45, gy + 90), (gx - 45, gy + 90)], A((200, 230, 255), 0.9))
    ink(d, [(gx - 60, gy - 90), (gx - 45, gy + 90), (gx + 45, gy + 90), (gx + 60, gy - 90 + tilt * 60)], t, INKC, 7, 1, 1510)
    for j, h in enumerate(WATER):
        u = pr(t, h, h + 0.5)
        if 0 < u < 1 or (t >= h + 0.5 and t < h + 0.9):
            px = lerp(820, 720, u); py = lerp(470, 700, eio(u))
            d.ell(px, py, 18, 24, A(AIRB, 1 - pr(t, h + 0.5, h + 0.9)))
            if t >= h + 0.5: d.text(800, 650 - j * 10, "咕", int(60 * pop(t, h + 0.5)) + 1, A(AIRB, 1 - pr(t, h + 0.5, h + 0.9)), k=1)
    n = sum(1 for h in WATER if t >= h + 0.5)
    dtext(d, 540, 230, "压不下去" if n else "卡住了", 80, INKC, ease(pr(t, STUCK + 0.2, STUCK + 0.5)), t, 1520)

def s_crackle(t, d):
    paper(d, t)
    lk = pr(t, CRACKLE, CRACKLE + 2.5)
    profile(d, t, press=0.1, hole=0.0, leak=lk * 1.2, chest=0.0, red=0.2)
    eso(d, t)
    # finger pressing neck
    press = pulse(t, CRK, 8); fx, fy = 820, 900
    ink(d, [(1080, 1080), (fx + 40 - 20 * press, fy + 20)], t, INKC, 16, 1, 1601)
    d.circ(fx + 30 - 20 * press, fy + 10, 26, fill=A(SKIN, 1)); ring(d, fx + 30 - 20 * press, fy + 10, 26, t, INKC, 6, 1, 1602)
    for j, h in enumerate(CRK):
        if h <= t < h + 0.6:
            k = pop(t, h, 0.12); fade = 1 - pr(t, h + 0.3, h + 0.6)
            d.text(880 - (j % 3) * 110, 760 + (j % 2) * 260, ["噼", "啪", "噼啪"][j % 3], int(80 * k) + 1, A(RED2, fade), k=1)
    # bubble wrap card: one bubble pops per press
    d.rect(150, 300, 520, 520, fill=A((230, 240, 252), 1), r=20); ring(d, 335, 410, 110, t, INKC, 0, 0, 1603)
    for i in range(12):
        bx = 200 + (i % 4) * 90; by = 350 + (i // 4) * 70
        popped = sum(1 for h in CRK if t >= h) > i * 0.6
        if popped: ink(d, [(bx - 18, by), (bx + 18, by)], t, MUTE, 5, 1, 1610 + i)
        else: d.circ(bx, by, 26, fill=A(AIRB, 0.55)); d.circ(bx - 8, by - 8, 7, fill=A(WHITE, 0.9))
    dtext(d, 335, 580, "像捏泡泡纸", 50, INKC, ease(pr(t, CRACKLE + 0.6, CRACKLE + 0.9)), t, 1620)

def heart(d, x, y, s, t, a=1.0, col=RED2):
    pts = []
    for i in range(60):
        th = i / 60 * 2 * math.pi
        hx = 16 * math.sin(th) ** 3; hy = 13 * math.cos(th) - 5 * math.cos(2 * th) - 2 * math.cos(3 * th) - math.cos(4 * th)
        pts.append((x + hx * s / 16, y - hy * s / 16))
    d.poly(pts, A(col, a)); d.ell(x - s * 0.42, y - s * 0.38, s * 0.18, s * 0.12, A((255, 170, 160), 0.8 * a))
    ink(d, pts + [pts[0]], t, INKC, 9, a, 1701, 1.6, 26)

def s_heart(t, d):
    paper(d, t)
    b = pulse(t, BEATS, 9)
    heart(d, 540, 900, 250 * (1 + 0.12 * b), t)
    rr = random.Random(3)
    for i in range(14):   # air bubbles hugging the heart
        an = rr.uniform(0, 6.28); r = 330 + rr.uniform(-30, 60) + 10 * b
        d.circ(540 + math.cos(an) * r, 900 + math.sin(an) * r * 0.9, 16 + (i % 3) * 6, fill=A(AIRB, 0.55))
    # stethoscope
    ink(d, [(980, 300), (900, 520), (760, 640), (700, 700)], t, INKC, 10, 1, 1710)
    d.circ(700, 700, 40, fill=A((190, 200, 215), 1)); ring(d, 700, 700, 40, t, INKC, 7, 1, 1711)
    for j, h in enumerate(BEATS):
        if h <= t < h + 0.45:
            k = pop(t, h, 0.1); fade = 1 - pr(t, h + 0.25, h + 0.45)
            d.text(250 + (j % 2) * 580, 560 + (j % 3) * 90, "咔嚓", int(90 * k) + 1, A(INKC, fade), k=1)
    # ECG strip
    pts = []
    for i in range(121):
        xx = 120 + i * 7; tt = t - (120 + 840 - xx) / 840 * 1.6; v = 0
        for h in BEATS:
            dt = tt - h
            if 0 <= dt < 0.12: v = math.sin(dt / 0.12 * math.pi * 2) * (1 if dt < 0.06 else -0.4)
        pts.append((xx, 1330 - v * 90))
    d.line(pts, A(GRN, 1), 7)
    dtext(d, 540, 240, "心跳一下，咔嚓一下", 72, INKC, ease(pr(t, HEART + 0.2, HEART + 0.5)), t, 1720)

def torso(d, t, air=0.0, a=1.0):
    """frontal X-ray style: neck to chest, air (cyan glow) spreading down from neck around heart."""
    d.poly([(440, 260), (640, 260), (650, 560), (900, 640), (980, 760), (1000, 1560), (80, 1560), (100, 760), (180, 640), (430, 560)], A((60, 68, 92), a))
    for i in range(7):  # ribs
        y = 820 + i * 95
        for sx in (-1, 1): d.arc(540 + sx * 230, y, 260, 70, 200 if sx < 0 else 270, 270 if sx < 0 else 340, A(BONE, 0.45 * a), 12)
    d.rect(520, 560, 560, 1560, fill=A(BONE, 0.5 * a), r=10)   # spine
    for sx in (-1, 1): d.ell(540 + sx * 220, 1080, 170, 330, A((22, 26, 40), a))   # lungs (dark)
    d.rect(522, 260, 558, 900, fill=A((22, 26, 40), a), r=14)   # trachea (air, dark)
    heart_pts = []
    d.ell(590, 1170, 170, 150, A(SOFT, a))
    rr = random.Random(7)
    for i in range(70):
        f = i / 70
        if f > air: continue
        y = lerp(320, 1330, f); spread = 70 + 160 * min(1, max(0, (y - 600) / 500))
        x = 540 + rr.uniform(-spread, spread) * (0.6 if y < 600 else 1)
        if 950 < y < 1330 and abs(x - 590) < 120: x = 590 + (170 if x > 590 else -170) * rr.uniform(0.85, 1.1)
        rad = rr.uniform(10, 22); fl = 0.7 + 0.3 * math.sin(t * 6 + i)
        glow(d, x, y, rad * 2.5, CYAN, 0.35 * fl * a, 3); d.circ(x, y, rad, fill=A((200, 250, 255), 0.85 * a))

def s_ct(t, d):
    d.rect(0, 0, OW, OH, fill=A(CTBG, 1))
    if t < CT_HIT:
        torso(d, t, 0.0, 0.5)
        d.text(540, 380, "拍个片……", 80, A(WHITE, 0.8), k=1)
        return
    air = ease(pr(t, CT_HIT, CT_HIT + 2.2))
    torso(d, t, air)
    k = pop(t, CT_HIT, 0.2)
    d.text(540, 300, "漏气了！", int(220 * (0.5 + 0.5 * k)) + 1, A(CYAN, 1), k=1)
    sparks(d, 540, 420, t, CT_HIT, 40, 1300, CYAN, 1, 9)
    if t >= CT_LBL:
        k2 = pop(t, CT_LBL)
        d.rect(640, 560, 1010, 660, fill=A(CYAN, min(1, k2)), r=30); d.text(825, 610, "脖子：有空气", 46, A(CTBG, min(1, k2)), k=1)
        d.rect(60, 1380, 470, 1480, fill=A(YEL2, min(1, k2)), r=30); d.text(265, 1430, "心脏周围：有空气", 44, A(CTBG, min(1, k2)), k=1)

def tube_panel(d, t, y, step, k):
    x0, x1 = 170, 910
    wv = 70 + (40 if step >= 2 else 0) + (8 * math.sin(t * 40) if step == 2 else 0)
    d.rect(x0, y - wv / 2, x1, y + wv / 2, fill=A(AIRW, 1), r=30)
    ink(d, [(x0, y - wv / 2), (x1, y - wv / 2)], t, INKC, 7, 1, 1800 + step); ink(d, [(x0, y + wv / 2), (x1, y + wv / 2)], t, INKC, 7, 1, 1810 + step)
    d.text(110, y, str(step), 70, A(RED2, 1), k=1)
    if step == 1:
        bx = lerp(x0 - 40, 420, ease(k)); d.ell(bx, y, 80, 60, A(BUNC, 1)); ring(d, bx, y, 60, t, INKC, 7, 1, 1820, rx=80)
        d.text(700, y - 90, "堵住", 60, A(INKC, min(1, k * 1.5)), k=1)
    if step == 2:
        for i in range(8):
            u = ((t * 2 + i / 8) % 1); d.circ(lerp(x0 + 40, x1 - 40, u), y + 20 * math.sin(i * 2.1), 10, fill=A(WHITE, 0.85))
        d.text(700, y - 110, "气压猛涨", 60, A(RED2, min(1, k * 1.5)), k=1)
    if step == 3:
        cx = 620; d.ell(cx, y - wv / 2, 18 * k, 10 * k, A((110, 15, 35), 1))
        for i in range(6):
            u = ((t * 1.3 + i / 6) % 1)
            d.circ(cx + (i - 3) * 14 * u, y - wv / 2 - 20 - u * 140, 9 + 8 * u, fill=A(AIRB, 0.75 * (1 - u)))
        d.text(330, y - 110, "撑出小口子", 60, A(INKC, min(1, k * 1.5)), k=1)

def s_why(t, d):
    paper(d, t)
    d.rect(330, 220, 750, 320, fill=A(INKC, 1), r=50); d.text(540, 270, "医生推测", 56, A(WHITE, 1), k=1)
    for j, (h, y) in enumerate(((W1, 560), (W2, 920), (W3, 1280))):
        if t >= h: tube_panel(d, t, y, j + 1, pop(t, h))

def check(d, x, y, s, t, k, seed):
    ink(d, [(x - s * 0.5, y), (x - s * 0.15, y + s * 0.4), (x - s * 0.5 + s * 1.2 * k, y - s * 0.55 * k)], t, GRN, 14, 1, seed)

def s_safe(t, d):
    paper(d, t)
    eso_pts = [(540, 380), (540, 1300)]
    d.line(eso_pts, A(ESO, 1), 120); ink(d, [(480, 380), (480, 1300)], t, (190, 120, 100), 6, 1, 1901); ink(d, [(600, 380), (600, 1300)], t, (190, 120, 100), 6, 1, 1902)
    d.text(540, 1380, "食道", 54, A(INKC, 1), k=1)
    for j, (h, lab) in enumerate(((D2, "第 2 天 · 造影"), (D3, "第 3 天 · 胃镜"))):
        if t >= h:
            k = pop(t, h); y = 640 + j * 300
            d.rect(640, y - 70, 1020, y + 70, fill=A((255, 252, 244), min(1, k)), r=24); ink(d, [(640, y - 70), (1020, y - 70), (1020, y + 70), (640, y + 70), (640, y - 70)], t, INKC, 6, min(1, k), 1910 + j)
            d.text(860, y, lab, 44, A(INKC, min(1, k)), k=1)
            check(d, 330, y, 120, t, min(1, k), 1920 + j)
    if t >= D3 + 0.5:
        k = pop(t, D3 + 0.5)
        d.text(540, 260, "没破！", int(170 * (0.5 + 0.5 * k)) + 1, A(GRN, 1), k=1)

def s_days(t, d):
    paper(d, t)
    for i, h in enumerate(DAYS):
        x0 = 170 + (i % 3) * 260; y0 = 520 + (i // 3) * 260
        box(d, x0, y0, x0 + 220, y0 + 220, t, INKC, 7, 1, 2000 + i, fill=(255, 252, 244))
        d.text(x0 + 40, y0 + 38, str(i + 1), 40, A(MUTE, 1), k=1)
        if t >= h:
            k = pop(t, h, 0.15)
            if i == 3: d.text(x0 + 110, y0 + 120, "吃饭", int(64 * k) + 1, A(RED2, 1), k=1)
            elif i == 7: d.text(x0 + 110, y0 + 120, "CT 干净", int(48 * k) + 1, A(CYAN, 1), k=1)
            elif i == 8: d.text(x0 + 110, y0 + 120, "出院", int(64 * k) + 1, A(GRN, 1), k=1)
            else: ink(d, [(x0 + 50, y0 + 120), (x0 + 95, y0 + 170), (x0 + 50 + 130 * k, y0 + 60)], t, MUTE, 10, 1, 2020 + i)
    k = pop(t, DAYS0 + 0.2)
    d.text(540, 330, "禁食 + 抗生素", int(90 * (0.6 + 0.4 * k)) + 1, A(INKC, 1), k=1)
    if t >= DAYS[-1]:
        bigface(d, 540, 1440, 110, t, "happy", mouth="smile", seed=2050)

def s_rare(t, d):
    paper(d, t)
    k = pop(t, RARE_HIT)
    cols, rows = 26, 20; x0, y0, gap = 140, 640, 31
    lit = int(cols * rows * ease(pr(t, RARE, RARE_HIT + 1.5)))
    for i in range(cols * rows):
        if i >= lit: break
        x = x0 + (i % cols) * gap; y = y0 + (i // cols) * gap
        if i == 263: d.circ(x, y, 15, fill=A(RED2, 1)); glow(d, x, y, 60, RED2, 0.5, 4)
        else: d.circ(x, y, 9, fill=A(INKC, 0.35))
    d.text(540, 330, "< 1/44000", int(170 * (0.5 + 0.5 * k)) + 1, A(RED2, min(1, k * 1.5)), k=1)
    if t >= RARE_HIT + 1.2:
        k2 = pop(t, RARE_HIT + 1.2)
        d.rect(260, 1330, 820, 1430, fill=A(INKC, min(1, k2)), r=40); d.text(540, 1380, "多见于年轻男性", 52, A(WHITE, min(1, k2)), k=1)

def s_asth(t, d):
    paper(d, t)
    k = pop(t, ASTH_HIT)
    # pie 1/5
    cx, cy, r = 540, 860, 260
    d.circ(cx, cy, r, fill=A((230, 236, 248), 1)); ring(d, cx, cy, r, t, INKC, 8, 1, 2101)
    sweep = 72 * ease(pr(t, ASTH_HIT, ASTH_HIT + 0.6))
    if sweep > 0: d.d.pieslice((P(cx - r), P(cy - r), P(cx + r), P(cy + r)), -90, -90 + sweep, fill=A(YEL2, 1))
    d.text(cx + 110, cy - 150, "1/5", int(90 * min(1, k)) + 1, A(INKC, 1), k=1)
    # inhaler
    d.rect(150, 1240, 260, 1420, fill=A((120, 170, 230), 1), r=20); d.rect(150, 1380, 330, 1450, fill=A((120, 170, 230), 1), r=20)
    ink(d, [(150, 1240), (260, 1240), (260, 1380), (330, 1380), (330, 1450), (150, 1450), (150, 1240)], t, INKC, 7, 1, 2102)
    d.text(640, 1340, "哮喘", 110, A(INKC, 1), k=1)
    d.text(540, 330, "他有哮喘", int(130 * (0.6 + 0.4 * k)) + 1, A(INKC, min(1, k * 1.5)), k=1)

def s_adv(t, d):
    paper(d, t)
    k = pop(t, ADV_HIT)
    chew = int(t * 5) % 2
    bigface(d, 470, 1020, 220, t, "happy", puff=0.3 * chew, mouth="clamp" if chew else "line", seed=2200)
    bun(d, 830, 1180, 110, t, 1, 2210)
    for j in range(3):
        if t >= ADV_HIT + 0.4 + j * 0.4: d.text(800 + j * 40, 760 + j * 90, "嚼", int(70 * pop(t, ADV_HIT + 0.4 + j * 0.4)) + 1, A(RED2, 1), k=1)
    d.text(540, 330, "嚼几口再咽", int(140 * (0.6 + 0.4 * k)) + 1, A(INKC, min(1, k * 1.5)), k=1)
    if t >= ADV_HIT + 1.6:
        k2 = pop(t, ADV_HIT + 1.6)
        d.rect(120, 1340, 960, 1450, fill=A(RED2, min(1, k2)), r=50); d.text(540, 1395, "胸痛、脖子噼啪响：马上就医", 50, A(WHITE, min(1, k2)), k=1)

def bubble(d, x, y, s, side, col, tcol, a, size=50):
    w = d.tlen(s, size) + 70; x0 = x - w if side > 0 else x
    d.rect(x0, y - size * 1.1, x0 + w, y + size * 1.1, fill=A(col, a), r=40); d.text(x0 + w / 2, y, s, size, A(tcol, a), k=1)
def s_end(t, d):
    paper(d, t)
    d.rect(0, 160, 1080, 260, fill=A(INKC, 1)); d.text(540, 210, "宿舍群（6）", 44, A(WHITE, 0.95), k=1)
    d.text(540, 380, "明天这样说 ↓", 80, A(RED2, ease(pr(t, OUTRO, OUTRO + 0.3))), k=1)
    G = ((120, 220, 120), (20, 40, 20))
    if t > BUB1: bubble(d, 70, 620, "我刚一口闷了个包子", -1, (90, 100, 130), WHITE, min(1, pop(t, BUB1)), 54)
    if t > BUB1 + 0.6: bubble(d, 1010, 800, "有人这样把空气咽进了胸口", 1, *G, min(1, pop(t, BUB1 + 0.6)), 48)
    if t > BUB2: bubble(d, 70, 990, "……我胸口怎么咔嚓响", -1, (90, 100, 130), WHITE, min(1, pop(t, BUB2)), 54)
    if t > BUB2 + 0.7: bubble(d, 1010, 1170, "那是你在嚼薯片", 1, *G, min(1, pop(t, BUB2 + 0.7)), 54)
    if t > BUB2 + 0.7: bigface(d, 540, 1420, 110, t, "happy", mouth="smile", seed=1400)
    d.text(540, 1780, "Nakamura et al. 2026, Int J Emerg Med 19:249", 26, A(INKC, 0.75), k=0)
    d.text(540, 1815, "doi:10.1186/s12245-026-01273-3", 26, A(INKC, 0.75), k=0)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

def brand2(t, d):
    dark = CT <= t < WHY
    d.rect(50, 80, 300, 128, fill=A(WHITE if dark else INKC, 0.95), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(INKC if dark else WHITE, 1))
    d.rect(740, 80, 1030, 128, fill=A((240, 170, 40), 1), r=24); d.text(885, 104, "脑洞系列 · 如果", 26, A(INKC, 1))

SECS = [(0, HOOK_END, s_hook), (CASE, BUN, s_case), (BUN, STUCK, s_bun), (STUCK, CRACKLE, s_stuck), (CRACKLE, HEART, s_crackle), (HEART, CT, s_heart),
        (CT, WHY, s_ct), (WHY, SAFE, s_why), (SAFE, DAYS0, s_safe), (DAYS0, RARE, s_days), (RARE, ASTH, s_rare), (ASTH, ADV, s_asth), (ADV, OUTRO, s_adv), (OUTRO, 99, s_end)]
CUTS = [HOOK_END, BUN, STUCK, CRACKLE, HEART, CT_HIT, WHY, SAFE, DAYS0, RARE, ASTH, ADV, OUTRO]
def cam(t):
    z = 1.0 + 0.05 * pulse(t, HITS, 7) + 0.12 * pulse(t, [GULP_HIT, CT_HIT], 3)
    for a, b in RISERS:
        if a <= t < b: z += 0.08 * eio(pr(t, a, b))
    cx0, cy0 = 540, 960
    if STUCK <= t < CRACKLE: k = eio(pr(t, STUCK, STUCK + 1.0)); z += 0.2 * k; cx0, cy0 = lerp(540, 640, k), lerp(960, 760, k)
    if HEART <= t < CT: z += 0.06 * pr(t, HEART, CT) + 0.04 * pulse(t, BEATS, 9)
    amp = 28 * pulse(t, [GULP_HIT, CT_HIT], 4) + 7 * pulse(t, HITS, 6) + 5 * pulse(t, CRK + BEATS, 9)
    sx, sy = shake(t, amp, 61)
    return z, cx0 + sx, cy0 + sy
def frame(t):
    img = Image.new("RGB", (W, H), PAPER); d = D(img)
    for a, b, sf in SECS:
        if a <= t < b: sf(t, d); break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.08: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.5 * (1 - (t - c) / 0.08)))
    brand2(t, d); subs(t, d)
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
