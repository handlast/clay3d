import sys, subprocess
from doodle import *
from fx import *
from cues import *
SKIN = (255, 222, 192); SKIN_D = (236, 186, 150); HOTF = (250, 120, 100); AIRW = (240, 120, 150); AIRB = (120, 190, 245)
RED2 = (220, 60, 50); GRN = (80, 170, 80); PINKL = (255, 190, 200); TISS = (255, 236, 220); YEL2 = (255, 196, 40)

def bigface(d, x, y, r, t, mood="ok", puff=0.0, red=0.0, pinch=0.0, mouth="line", seed=0, a=1.0, sweat=0.0):
    col = mix(SKIN, HOTF, red)
    rx = r * (1 + 0.18 * puff); ry = r * (1 + 0.05 * puff)
    ring(d, x, y, ry, t, INKC, 10, a, seed, fill=col, rx=rx)
    # ears
    for sx in (-1, 1): ring(d, x + sx * rx * 0.98, y + r * 0.05, r * 0.16, t, INKC, 8, a, seed + 3 + sx, fill=col)
    ring(d, x, y, ry * 0.97, t, col, 1, a * 0.0, seed)
    # cheeks
    for sx in (-1, 1): d.ell(x + sx * r * (0.5 + 0.12 * puff), y + r * 0.25, r * (0.18 + 0.12 * puff), r * (0.12 + 0.08 * puff), A((245, 140, 140), (0.45 + 0.4 * puff) * a))
    ey = y - r * 0.12; ex = r * 0.33
    for sx in (-1, 1):
        cx = x + sx * ex
        if mood == "squeeze":
            ink(d, [(cx - sx * r * 0.14, ey - r * 0.08), (cx + sx * r * 0.1, ey), (cx - sx * r * 0.14, ey + r * 0.08)], t, INKC, 9, a, seed + 10 + sx)
        elif mood == "shock":
            ring(d, cx, ey, r * 0.13, t, INKC, 7, a, seed + 12 + sx, fill=WHITE); d.circ(cx, ey, r * 0.05, fill=A(INKC, a))
        elif mood == "happy":
            d.arc(cx, ey + r * 0.05, r * 0.11, r * 0.09, 200, 340, A(INKC, a), r * 0.035)
        elif mood == "worry":
            d.circ(cx, ey, r * 0.055, fill=A(INKC, a))
            ink(d, [(cx - r * 0.12, ey - r * 0.12 - sx * r * 0.04), (cx + r * 0.12, ey - r * 0.12 + sx * r * 0.04)], t, INKC, 7, a, seed + 14 + sx)
        else:
            d.circ(cx, ey, r * 0.06, fill=A(INKC, a))
    # nose
    d.arc(x, y + r * 0.08, r * 0.09, r * 0.07, 0, 180, A(mix(SKIN_D, HOTF, red), a), r * 0.04)
    my = y + r * 0.45
    if mouth == "line": ink(d, [(x - r * 0.18, my), (x + r * 0.18, my)], t, INKC, 9, a, seed + 20)
    elif mouth == "clamp": ink(d, [(x - r * 0.22, my), (x - r * 0.1, my - r * 0.03), (x + r * 0.1, my + r * 0.03), (x + r * 0.22, my)], t, INKC, 10, a, seed + 20)
    elif mouth == "ah": d.ell(x, my, r * 0.16, r * 0.14, A((140, 40, 50), a)); d.ell(x, my + r * 0.06, r * 0.09, r * 0.05, A((240, 120, 130), a))
    elif mouth == "smile": d.arc(x, my - r * 0.12, r * 0.22, r * 0.15, 20, 160, A(INKC, a), r * 0.04)
    elif mouth == "sad": d.arc(x, my + r * 0.05, r * 0.18, r * 0.1, 200, 340, A(INKC, a), r * 0.04)
    if pinch > 0:  # hand pinching nose, arm from below
        hx, hy = x + r * 0.02, y + r * 0.1 + (1 - pinch) * r * 1.2
        ink(d, [(x + r * 0.9, y + r * 2.0), (x + r * 0.55, y + r * 1.0), (hx + r * 0.1, hy + r * 0.12)], t, INKC, 12, a * pinch, seed + 30)
        d.ell(hx, hy, r * 0.17, r * 0.13, A(col, a)); ring(d, hx, hy, r * 0.13, t, INKC, 7, a * pinch, seed + 31, rx=r * 0.17)
        for sx in (-1, 1): d.ell(hx + sx * r * 0.1, hy - r * 0.08, r * 0.05, r * 0.08, A(SKIN, a))
    if sweat > 0:
        for i, (sx, sy) in enumerate(((1.0, -0.6), (-1.05, -0.4), (0.9, -0.95))):
            u = ((t * 1.4 + i * 0.37) % 1); dx, dy = x + sx * r, y + sy * r + u * r * 0.4
            d.ell(dx, dy, r * 0.05, r * 0.08, A(AIRB, sweat * a * (1 - u * 0.5)))
    if red > 0.6:  # pressure veins
        for sx in (-1, 1):
            ink(d, [(x + sx * r * 0.55, y - r * 0.75), (x + sx * r * 0.62, y - r * 0.62), (x + sx * r * 0.5, y - r * 0.55)], t, RED2, 7, a * (red - 0.6) * 2.5, seed + 40 + sx)

# side cross-section, facing right
FRONT = [(380, 560), (395, 430), (470, 345), (600, 330), (705, 395), (745, 495), (748, 565), (805, 640), (770, 665), (752, 700), (772, 722), (748, 742), (758, 785), (722, 835), (660, 855), (642, 870), (640, 990), (760, 1050), (870, 1140), (900, 1560)]
BACK = [(380, 560), (378, 700), (420, 800), (478, 880), (470, 1000), (330, 1070), (215, 1170), (180, 1560)]
AIR = [(775, 640), (690, 638), (630, 680), (600, 750), (588, 830), (582, 920), (580, 1050), (580, 1150)]
HOLEP = (594, 800)
def profile(d, t, press=0.0, hole=0.0, leak=0.0, chest=0.0, red=0.0):
    poly = FRONT + BACK[::-1]
    d.poly(poly, A(mix(TISS, (255, 210, 200), red), 1))
    ink(d, FRONT, t, INKC, 10, 1, 201); ink(d, BACK, t, INKC, 10, 1, 202)
    d.circ(640, 470, 14, fill=A(INKC, 1))  # eye
    # lungs
    for sx in (-1, 1):
        lx = 580 + sx * 135
        d.ell(lx, 1330, 120, 190, A(PINKL, 0.9)); ring(d, lx, 1330, 190, t, (200, 110, 130), 7, 0.8, 210 + sx, rx=120)
    # airway (thick pink), thickness ~ pressure
    wv = 34 + 22 * press + 6 * press * math.sin(t * 40)
    pts = AIR + [(580, 1150)]
    glowc = mix(AIRW, RED2, press)
    if press > 0.3:
        for p in AIR[1:]: glow(d, p[0], p[1], 80 * press, (255, 120, 110), 0.25 * press, 3)
    d.line(pts, A(glowc, 1), wv)
    for sx in (-1, 1): d.line([(580, 1150), (580 + sx * 90, 1230), (580 + sx * 135, 1290)], A(glowc, 1), wv * 0.7)
    d.line([(752, 712), (680, 712), (618, 745)], A(glowc, 0.9), wv * 0.7)  # mouth
    # pressure arrows inside airway
    if 0 < press:
        for i in range(5):
            u = ((t * 1.8 + i / 5) % 1); k = int(u * (len(AIR) - 1)); f = u * (len(AIR) - 1) - k
            px = lerp(AIR[k][0], AIR[k + 1][0], f); py = lerp(AIR[k][1], AIR[k + 1][1], f)
            d.circ(px, py, 8 + 6 * press, fill=A(WHITE, 0.8 * press))
    if hole > 0:
        hx, hy = HOLEP
        r = 6 + 22 * hole
        d.ell(hx + 10, hy, r * 0.7, r, A((120, 20, 40), 1))
        for i in range(6):
            an = i * 1.05 + 0.3
            ink(d, [(hx + 10 + math.cos(an) * r, hy + math.sin(an) * r), (hx + 10 + math.cos(an) * r * 1.8, hy + math.sin(an) * r * 1.8)], t, RED2, 6, hole, 230 + i)
    if leak > 0:  # air bubbles spreading from hole into neck tissue, then down to chest
        rr = random.Random(5)
        n = 46
        for i in range(n):
            delay = i / n * 0.8; u = cl((leak - delay) / 0.6)
            if u <= 0: continue
            tx = rr.uniform(520, 760); ty = rr.uniform(760, 980) if i % 3 else rr.uniform(980, 1180 + 300 * chest)
            if i % 3 == 0 and chest <= 0: ty = rr.uniform(760, 980)
            px = lerp(HOLEP[0] + 10, tx, eio(u)) + 4 * math.sin(t * 5 + i); py = lerp(HOLEP[1], ty, eio(u)) + 4 * math.cos(t * 4 + i)
            rad = 8 + (i % 4) * 4
            d.circ(px, py, rad, fill=A(AIRB, 0.55)); d.circ(px - rad * 0.3, py - rad * 0.3, rad * 0.3, fill=A(WHITE, 0.8))

def s_hook(t, d):
    paper(d, t)
    wind = pr(t, 0, HOOK_HIT); held = t >= HOOK_HIT
    sh = 10 * math.sin(t * 70) * (1 - pr(t, HOOK_HIT, HOOK_HIT + 1.5)) if held else 0
    puff = (0.4 + 0.6 * pulse(t, [HOOK_HIT], 1.5)) if held else wind * 0.3
    bigface(d, 540 + sh, 1000, 300, t, "squeeze", puff=puff, red=0.75 if held else wind * 0.4, pinch=ease(pr(t, HOOK_HIT - 0.15, HOOK_HIT)), mouth="clamp" if held else "ah", sweat=1.0 if held else 0)
    if not held:
        k = 0.6 + 0.6 * wind
        dtext(d, 540, 470, "啊……啊……", int(140 * k), RED2, 1, t, 1)
    else:
        k = pop(t, HOOK_HIT, 0.2)
        d.text(540, 420, "憋住！", int(240 * (0.5 + 0.5 * k)) + 1, A(RED2, 1), k=1)
        rings(d, 540, 1000, t, [HOOK_HIT], RED2, 0.8, 520)
        sparks(d, 540, 1000, t, HOOK_HIT, 30, 1100, YEL2, 1, 3)
        if t > HOOK_HIT + 1.0:
            dtext(d, 540, 1450, "然后呢？", 90, INKC, ease(pr(t, HOOK_HIT + 1.0, HOOK_HIT + 1.3)), t, 2)

def s_case(t, d):
    paper(d, t)
    k = pop(t, CASE_HIT)
    box(d, 140, 330, 940, 760, t, INKC, 9, min(1, k * 1.5), 301, fill=(255, 252, 244))
    dtext(d, 540, 420, "英国 · 莱斯特", 70, INKC, min(1, k * 1.5), t, 302)
    dtext(d, 540, 540, "2018", int(180 * (0.6 + 0.4 * k)) + 1, RED2, min(1, k * 1.5), t, 303)
    dtext(d, 540, 680, "BMJ 病例报告", 50, MUTE, min(1, k * 1.5), t, 304)
    k2 = pop(t, AGE_HIT)
    bigface(d, 540, 1180, 220, t, "squeeze" if t > AGE_HIT + 0.6 else "ok", puff=0.6 * pr(t, AGE_HIT + 0.4, AGE_HIT + 0.8), red=0.5 * pr(t, AGE_HIT + 0.4, AGE_HIT + 1), pinch=ease(pr(t, AGE_HIT + 0.2, AGE_HIT + 0.6)), mouth="clamp" if t > AGE_HIT + 0.4 else "line", seed=310)
    if t >= AGE_HIT:
        d.rect(760, 900, 990, 1010, fill=A(YEL2, 1), r=30); d.text(875, 955, "34 岁", int(64 * (0.6 + 0.4 * k2)) + 1, A(INKC, 1), k=1)

def s_neck(t, d):
    paper(d, t)
    press = 0.35 + 0.5 * pr(t, NECK, POP)
    if t >= POP: press = 0.85 * (1 - 0.5 * pr(t, POP, POP + 1.5))
    profile(d, t, press=press, red=0.3)
    if t >= POP:
        k = pop(t, POP, 0.18)
        glow(d, HOLEP[0], HOLEP[1], 220 * k, YEL2, 0.6 * (1 - pr(t, POP + 0.4, POP + 1.2)), 6)
        d.text(840, 820, "啵！", int(170 * (0.5 + 0.5 * k)) + 1, A(RED2, 1 - pr(t, POP + 1.6, HOLE)), k=1)
        rings(d, HOLEP[0], HOLEP[1], t, [POP], RED2, 0.8, 300)
    dtext(d, 540, 230, "压力全堵在喉咙里", 64, INKC, ease(pr(t, NECK + 0.2, NECK + 0.5)), t, 401)

def s_hole(t, d):
    paper(d, t)
    z = 1.0
    # zoom into throat: draw magnified throat tube
    k = pop(t, HOLE_HIT)
    d.rect(300, 350, 780, 1500, fill=A(TISS, 1), r=60)
    ink(d, [(300, 350), (300, 1500)], t, INKC, 10, 1, 501); ink(d, [(780, 350), (780, 1500)], t, INKC, 10, 1, 502)
    d.rect(410, 350, 670, 1500, fill=A(AIRW, 1), r=40)
    for i in range(8): d.arc(540, 420 + i * 150, 130, 30, 0, 180, A((210, 90, 120), 0.6), 6)
    if t >= HOLE_HIT:
        r = 30 + 40 * k
        d.ell(640, 880, r * 0.8, r * 1.3, A((110, 15, 35), 1))
        for i in range(8):
            an = i * 0.8
            ink(d, [(640 + math.cos(an) * r * 0.8, 880 + math.sin(an) * r * 1.3), (640 + math.cos(an) * r * 1.8, 880 + math.sin(an) * r * 2.2)], t, RED2, 7, 1, 510 + i)
        for i in range(10):
            u = ((t - HOLE_HIT) * 1.2 + i / 10) % 1
            d.circ(640 + u * 260 + 20 * math.sin(i), 880 + (i - 5) * 25 * u, 10 + 8 * u, fill=A(AIRB, 0.7 * (1 - u)))
        d.text(540, 240, "破了个洞", int(150 * (0.6 + 0.4 * k)) + 1, A(RED2, min(1, k * 1.5)), k=1)
        dtext(d, 900, 1100, "梨状窝", 54, INKC, ease(pr(t, HOLE_HIT + 0.6, HOLE_HIT + 0.9)), t, 520)
        ink(d, [(900, 1060), (720, 920)], t, INKC, 6, ease(pr(t, HOLE_HIT + 0.6, HOLE_HIT + 0.9)), 521)
    else:
        sw = 1 + 0.06 * math.sin(t * 40)
        d.text(540, 240, "放大看", 100, A(INKC, 1), k=1)

def s_leak(t, d):
    paper(d, t)
    lk = pr(t, LEAK + 0.3, CHEST + 0.5)
    profile(d, t, press=0.2, hole=1.0, leak=lk * 1.4, chest=0.0, red=0.2)
    n = sum(1 for h in LEAKS if t >= h)
    dtext(d, 540, 230, "空气在往外钻", 70, INKC, ease(pr(t, LEAK + 0.2, LEAK + 0.5)), t, 601)
    for j, h in enumerate(LEAKS):
        if t >= h: d.text(820 + (j % 2) * 90, 900 + j * 70, "咕", int(54 * pop(t, h)) + 1, A(AIRB, 1 - pr(t, h + 0.8, h + 1.2)), k=1)

def s_chest(t, d):
    paper(d, t)
    profile(d, t, press=0.1, hole=1.0, leak=1.4, chest=ease(pr(t, CHEST, CHEST + 1.2)), red=0.25)
    # doctor's finger pressing chest
    fx, fy = 860, 1200
    press = pulse(t, CRACK, 8)
    ink(d, [(1080, 1350), (fx + 40 - 20 * press, fy + 20)], t, INKC, 16, 1, 701)
    d.circ(fx + 30 - 20 * press, fy + 10, 26, fill=A(SKIN, 1)); ring(d, fx + 30 - 20 * press, fy + 10, 26, t, INKC, 6, 1, 702)
    for j, h in enumerate(CRACK):
        if h <= t < h + 0.6:
            k = pop(t, h, 0.12); fade = 1 - pr(t, h + 0.3, h + 0.6)
            d.text(700 + (j % 3) * 120 - 200, 980 + (j % 2) * 180, ["噼", "啪", "噼啪"][j % 3], int(80 * k) + 1, A(RED2, fade), k=1)
    hb = pulse(t, [CHEST + 0.5 + 3.8 * (1 - (1 - i / 9) ** 1.5) for i in range(10)], 10)
    dtext(d, 600, 250, "一路钻到胸口", 70, INKC, ease(pr(t, CHEST + 0.2, CHEST + 0.5)), t, 703)

def gauge(d, t, val, x=540, y=1050, r=360):
    d.circ(x, y, r + 20, fill=A((255, 252, 244), 1)); ring(d, x, y, r + 20, t, INKC, 12, 1, 801)
    a0, a1 = 150, 390  # degrees (PIL: 0 = right, clockwise)
    for i in range(9):
        v = i * 5; ang = math.radians(a0 + (a1 - a0) * v / 40)
        ink(d, [(x + math.cos(ang) * r * 0.82, y + math.sin(ang) * r * 0.82), (x + math.cos(ang) * r * 0.95, y + math.sin(ang) * r * 0.95)], t, INKC, 8, 1, 810 + i)
        d.text(x + math.cos(ang) * r * 0.68, y + math.sin(ang) * r * 0.68, str(v), 40, A(INKC, 1), k=1)
    d.arc(x, y, r * 0.9, r * 0.9, a0 + (a1 - a0) * 1 / 40, a0 + (a1 - a0) * 2 / 40 + 2, A(GRN, 1), 40)
    d.arc(x, y, r * 0.9, r * 0.9, a0 + (a1 - a0) * 20 / 40, a1, A(RED2, 0.85), 40)
    ang = math.radians(a0 + (a1 - a0) * cl(val / 40) + 1.5 * math.sin(t * 60) * (val > 15))
    d.line([(x, y), (x + math.cos(ang) * r * 0.85, y + math.sin(ang) * r * 0.85)], A(RED2, 1), 16)
    d.circ(x, y, 34, fill=A(INKC, 1))
    d.text(x, y + r * 0.45, "千帕 kPa", 44, A(MUTE, 1), k=1)

def s_press(t, d):
    hit = t >= PRESS_HIT
    if hit:
        rays(d, t, (255, 236, 200), (255, 220, 170), 18, 540, 1050)
    else:
        paper(d, t)
    val = 1.5 if not hit else lerp(1.5, 36, back(pr(t, PRESS_HIT, PRESS_HIT + 0.35)))
    if t >= KPA: val = 36 + 2 * math.sin(t * 6)
    gauge(d, t, val)
    if hit:
        k = pop(t, PRESS_HIT, 0.2)
        glow(d, 540, 380, 380 * k, YEL2, 0.6, 6)
        d.text(540, 380, "×20", int(300 * (0.5 + 0.5 * k)) + 1, A(RED2, 1), k=1)
        sparks(d, 540, 380, t, PRESS_HIT, 40, 1300, RED2, 1, 9)
    else:
        dtext(d, 540, 380, "压力有多大？", 100, INKC, 1, t, 820)
    if t >= KPA:
        k2 = pop(t, KPA)
        d.rect(90, 560, 500, 660, fill=A(GRN, min(1, k2)), r=30); d.text(295, 610, "平时 1~2", 54, A(WHITE, min(1, k2)), k=1)
        d.rect(580, 560, 990, 660, fill=A(RED2, min(1, k2)), r=30); d.text(785, 610, "憋住 20~40", 54, A(WHITE, min(1, k2)), k=1)

def s_tube(t, d):
    paper(d, t)
    # bed
    box(d, 120, 1060, 960, 1180, t, INKC, 9, 1, 901, fill=(220, 232, 250))
    d.rect(140, 980, 360, 1060, fill=A(WHITE, 1), r=30)
    bigface(d, 260, 900, 140, t, "worry", mouth="sad", seed=910)
    # nasal tube to bag
    ink(d, [(265, 920), (330, 960), (450, 850), (520, 560), (560, 420)], t, (120, 170, 220), 10, 1, 902)
    d.rect(520, 300, 640, 440, fill=A((240, 230, 200), 1), r=20); ring(d, 580, 370, 70, t, INKC, 6, 1, 903, rx=60)
    d.text(580, 370, "营养液", 30, A(INKC, 1), k=1)
    # calendar 7 days
    for i, h in enumerate(DAYS):
        x0 = 640 + (i % 4) * 95; y0 = 560 + (i // 4) * 110
        box(d, x0, y0, x0 + 80, y0 + 90, t, INKC, 6, 1, 920 + i, fill=(255, 252, 244))
        d.text(x0 + 40, y0 + 45, str(i + 1), 40, A(INKC, 1), k=1)
        if t >= h:
            k = pop(t, h, 0.15)
            ink(d, [(x0 + 10, y0 + 50), (x0 + 35, y0 + 80), (x0 + 85 * k, y0 + 5)], t, RED2, 9, 1, 930 + i)
    d.text(780, 450, "7 天", int(120 * pop(t, TUBE + 0.3)) + 1, A(RED2, 1), k=1)
    dtext(d, 540, 1300, "不能吃，不能喝", 70, INKC, ease(pr(t, DAYS[3], DAYS[3] + 0.3)), t, 940)

def car(d, x, y, t, a=1.0):
    bob = 4 * math.sin(t * 16)
    d.rect(x - 380, y - 120 + bob, x + 380, y + 60 + bob, fill=A((120, 170, 230), a), r=50)
    d.poly([(x - 220, y - 120 + bob), (x - 140, y - 300 + bob), (x + 180, y - 300 + bob), (x + 280, y - 120 + bob)], A((120, 170, 230), a))
    d.poly([(x - 180, y - 130 + bob), (x - 120, y - 270 + bob), (x + 150, y - 270 + bob), (x + 230, y - 130 + bob)], A((220, 240, 255), a))
    for sx in (-1, 1):
        d.circ(x + sx * 240, y + 70, 80, fill=A((60, 70, 90), a)); d.circ(x + sx * 240, y + 70, 34, fill=A((200, 205, 215), a))
    d.circ(x + 360, y - 60 + bob, 24, fill=A(YEL2, a))

def s_car(t, d):
    paper(d, t)
    for i in range(8):  # road lines
        xx = 1080 - ((t * 900 + i * 260) % 1400)
        d.rect(xx, 1520, xx + 140, 1545, fill=A(MUTE, 0.8))
    car(d, 540, 1340, t)
    held = t >= CAR_HIT + 0.6
    bigface(d, 560, 1130, 95, t, "squeeze" if held else "ok", puff=0.8 if held else 0, red=0.7 if held else 0, pinch=ease(pr(t, CAR_HIT + 0.3, CAR_HIT + 0.6)), mouth="clamp" if held else "ah", seed=1010)
    k = pop(t, CAR_HIT)
    box(d, 160, 320, 920, 700, t, INKC, 9, min(1, k * 1.5), 1001, fill=(255, 252, 244))
    dtext(d, 540, 410, "苏格兰 · 邓迪", 70, INKC, min(1, k * 1.5), t, 1002)
    dtext(d, 540, 540, "2023", int(170 * (0.6 + 0.4 * k)) + 1, RED2, min(1, k * 1.5), t, 1003)
    dtext(d, 540, 650, "30 多岁 · 花粉过敏", 46, MUTE, min(1, k * 1.5), t, 1004)

def s_mm(t, d):
    paper(d, t)
    k = pop(t, MM_HIT)
    # trachea rings
    d.rect(360, 420, 720, 1380, fill=A(AIRW, 1), r=60)
    for i in range(9): d.rect(340, 450 + i * 105, 740, 500 + i * 105, fill=A((250, 200, 210), 1), r=24)
    if t >= MM_HIT:
        d.ell(600, 880, 14 + 10 * k, 30 + 10 * k, A((110, 15, 35), 1))
        glow(d, 600, 880, 120 * k, YEL2, 0.4, 5)
    # ruler
    rx0 = 170
    d.rect(rx0, 1450, 910, 1560, fill=A((255, 230, 150), 1), r=10)
    for i in range(0, 37):
        hh = 50 if i % 10 == 0 else (35 if i % 5 == 0 else 22)
        d.line([(rx0 + 20 + i * 20, 1450), (rx0 + 20 + i * 20, 1450 + hh)], A(INKC, 1), 4)
    if t >= MM_HIT:
        d.rect(rx0 + 20, 1430, rx0 + 20 + 40 * k, 1580, fill=A(RED2, 0.5))
    d.text(540, 300, "2 毫米", int(190 * (0.6 + 0.4 * k)) + 1, A(RED2, min(1, k * 1.5)), k=1)
    dtext(d, 850, 1000, "气管", 60, INKC, 1, t, 1101)

def s_heal(t, d):
    paper(d, t)
    k = pop(t, HEAL_HIT)
    for j, (x, lab, sub) in enumerate(((290, "莱斯特", "住院 7 天"), (790, "邓迪", "5 周后复查长好"))):
        kk = pop(t, HEAL_HIT + j * 0.5)
        bigface(d, x, 900, 170, t, "happy", mouth="smile", seed=1200 + j * 50, a=1)
        dtext(d, x, 1170, lab, 64, INKC, min(1, kk * 1.5), t, 1210 + j)
        d.rect(x - 220, 1240, x + 220, 1330, fill=A(GRN, min(1, kk)), r=30); d.text(x, 1285, sub, 44, A(WHITE, min(1, kk)), k=1)
    d.text(540, 380, "都没开刀", int(150 * (0.6 + 0.4 * k)) + 1, A(GRN, min(1, k * 1.5)), k=1)

def s_adv(t, d):
    paper(d, t)
    k = pop(t, ADV_HIT)
    sneezing = t >= ADV_HIT + 0.6
    bigface(d, 470, 1050, 230, t, "squeeze" if sneezing else "ok", mouth="ah" if sneezing else "line", seed=1300)
    # elbow in front of mouth
    if t >= ADV_HIT + 0.3:
        ink(d, [(140, 1500), (560, 1200), (900, 1350)], t, INKC, 30, 1, 1301)
        d.circ(560, 1200, 50, fill=A((120, 170, 230), 1))
    if sneezing:
        for i in range(24):
            u = ((t - ADV_HIT - 0.6) * 1.5 + i / 24) % 1
            d.circ(600 + u * 380, 1150 + (i - 12) * 18 * u - 60 * u, 10 * (1 - u) + 2, fill=A(AIRB, 0.7 * (1 - u)))
        d.text(800, 900, "阿嚏！", int(110 * pop(t, ADV_HIT + 0.6)) + 1, A(RED2, 1), k=1)
    d.text(540, 330, "要打就打出来", int(130 * (0.6 + 0.4 * k)) + 1, A(INKC, min(1, k * 1.5)), k=1)
    dtext(d, 540, 500, "别同时捏鼻子 + 闭嘴", 64, RED2, ease(pr(t, ADV_HIT + 0.5, ADV_HIT + 0.8)), t, 1310)

def bubble(d, x, y, s, side, col, tcol, a, size=50):
    w = d.tlen(s, size) + 70; x0 = x - w if side > 0 else x
    d.rect(x0, y - size * 1.1, x0 + w, y + size * 1.1, fill=A(col, a), r=40); d.text(x0 + w / 2, y, s, size, A(tcol, a), k=1)
def s_end(t, d):
    paper(d, t)
    d.rect(0, 160, 1080, 260, fill=A(INKC, 1)); d.text(540, 210, "宿舍群（6）", 44, A(WHITE, 0.95), k=1)
    d.text(540, 380, "明天这样说 ↓", 80, A(RED2, ease(pr(t, OUTRO, OUTRO + 0.3))), k=1)
    G = ((120, 220, 120), (20, 40, 20))
    if t > BUB1: bubble(d, 70, 620, "我上课憋了个喷嚏", -1, (90, 100, 130), WHITE, min(1, pop(t, BUB1)), 54)
    if t > BUB1 + 0.6: bubble(d, 1010, 800, "有人这样把喉咙憋破了", 1, *G, min(1, pop(t, BUB1 + 0.6)), 50)
    if t > BUB2: bubble(d, 70, 990, "……我脖子怎么咔咔响", -1, (90, 100, 130), WHITE, min(1, pop(t, BUB2)), 54)
    if t > BUB2 + 0.7: bubble(d, 1010, 1170, "那是你颈椎", 1, *G, min(1, pop(t, BUB2 + 0.7)), 54)
    if t > BUB2 + 0.7: bigface(d, 540, 1420, 110, t, "happy", mouth="smile", seed=1400)
    d.text(540, 1780, "Yang et al. 2018, BMJ Case Rep, bcr-2016-218906", 26, A(INKC, 0.75), k=0)
    d.text(540, 1815, "Misirovs et al. 2023, BMJ Case Rep 16:e255633", 26, A(INKC, 0.75), k=0)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

def brand2(t, d):
    d.rect(50, 80, 300, 128, fill=A(INKC, 0.95), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(WHITE, 1))
    d.rect(740, 80, 1030, 128, fill=A((240, 170, 40), 1), r=24); d.text(885, 104, "脑洞系列 · 如果", 26, A(INKC, 1))

SECS = [(0, HOOK_END, s_hook), (CASE, NECK, s_case), (NECK, HOLE, s_neck), (HOLE, LEAK, s_hole), (LEAK, CHEST, s_leak), (CHEST, PRESS, s_chest),
        (PRESS, TUBE, s_press), (TUBE, CAR, s_tube), (CAR, MM, s_car), (MM, HEAL, s_mm), (HEAL, ADV, s_heal), (ADV, OUTRO, s_adv), (OUTRO, 99, s_end)]
CUTS = [HOOK_END, NECK, HOLE, LEAK, CHEST, PRESS_HIT, TUBE, CAR, MM, HEAL, ADV, OUTRO]
def cam(t):
    z = 1.0 + 0.06 * pulse(t, HITS, 7) + 0.12 * pulse(t, [HOOK_HIT, PRESS_HIT], 3)
    for a, b in RISERS:
        if a <= t < b: z += 0.08 * eio(pr(t, a, b))
    if NECK <= t < HOLE: z += 0.15 * eio(pr(t, NECK, POP)); cx0, cy0 = lerp(540, 594, eio(pr(t, NECK, POP))), lerp(960, 820, eio(pr(t, NECK, POP)))
    else: cx0, cy0 = 540, 960
    if CHEST <= t < PRESS: z += 0.05 * pr(t, CHEST, PRESS)
    amp = 28 * pulse(t, [HOOK_HIT, PRESS_HIT, POP], 4) + 8 * pulse(t, HITS, 6) + (6 * pr(t, CHEST, PRESS) if CHEST <= t < PRESS else 0)
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
    if SILENCES[0][0] <= t < SILENCES[0][1]: d.rect(0, 0, OW, OH, fill=A((40, 50, 90), 0.5))
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
