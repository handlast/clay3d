import sys, subprocess
from doodle import *
from fx import *

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

