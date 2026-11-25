import math, random, sys, subprocess
from PIL import Image
from base import *
from fx import glow, face, sparks, embers, shake, stamp, flash, grad, rays, vignette
from chars import flame, scholar, girl, baby, tile, paper_bg, FIRE, FIRE_L, HRED, HRED_D, GOLD, PAPER, PAPER_D, INKB, JADE
from toon import horse, goat, fire_tuft, draw_shapes, OL
from cues import *

def ls(i): return L[i][0]
def le(i): return L[i][1]
WARN = (255, 70, 60); BLUE = (90, 140, 230); PINK = (255, 120, 160)

A0 = 0; B0 = ls(3) - 0.15; C0 = ls(7) - 0.2; D0 = ls(10) - 0.2; E0 = ls(13) - 0.2; F0 = ls(18) - 0.2; G0 = ls(22) - 0.2
CUTS = [B0, C0, D0, E0, F0, G0]

# ===== A: hook =====
H_BOOM = 0.3; H_NUM = ls(1) + 1.6; H_GONE = ls(2)
def sA(t, d):
    rays(d, t, (150, 30, 20), (55, 10, 8), 22, 540, 1050)
    embers(d, t, FIRE_L, 1, 46)
    p = pulse(t, [H_BOOM], 2.2)
    for i in range(10): flame(d, 20 + i * 115, 1560, 280 + 70 * math.sin(t * 3 + i) + 240 * p, t, 0.92, i * 2.3)
    if t < H_NUM - 0.2:
        run = ease(pr(t, 0, 0.32))
        horse(d, lerp(-300, 430, run), 1130, 210, t, "scream" if t < 1.0 else "proud", 1.0, 1.0)
        sparks(d, 540, 1000, t, H_BOOM, 90, 1600, FIRE_L, 1, 3, 1.4)
    else:
        horse(d, 250, 1260, 130, t, "shock", 0.0, 0.9, look=(0.8, 0))
        u = t - H_GONE
        for i in range(24):
            bx = 470 + (i % 6) * 95; by = 860 + (i // 6) * 120
            gone = i % 4 == 1 and u > 0
            fall = max(0, u - (i // 4) * 0.12) if gone else 0
            if fall < 1.2: baby(d, bx, by + 900 * fall * fall, 34, 1 - cl(fall * 1.2))
def uA(t, d):
    if t < H_NUM - 0.2:
        k = back(pr(t, H_BOOM, H_BOOM + 0.25)); p = pulse(t, [H_BOOM + i * 0.55 for i in range(7)], 9)
        d.text(540, 330, "2026 · 丙午", int(96 * k), A(WHITE, 1), k=1)
        s = int(200 * k * (1 + 0.05 * p))
        d.text(550, 520, "双火马年", s, A(HRED_D, 1), k=1); d.text(540, 510, "双火马年", s, A(FIRE_L, 1), k=1)
        d.text(540, 690, "60 年才来一次", 66, A(WHITE, ease(pr(t, 1.3, 1.6))), k=1)
    else:
        k = back(pr(t, H_NUM - 0.2, H_NUM + 0.05))
        d.text(540, 330, "上一次丙午 · 日本", 70, A(WHITE, 1), k=1)
        d.text(540, 530, "-46万", int(240 * k), A(WARN, 1), k=1)
        d.text(540, 700, "一年少生的孩子", 62, A(WHITE, ease(pr(t, H_NUM, H_NUM + 0.3))), k=1)
    flash(d, t, [H_BOOM], WHITE, 0.95); flash(d, t, [H_NUM - 0.2], WARN, 0.45)

# ===== B: Oshichi =====
B_GIRL, B_FIRE, B_STAGE, B_RUM = ls(3), ls(4) + 2.6, ls(5), ls(6)
def sB(t, d):
    if t < ls(4):
        grad(d, (14, 10, 22), (4, 2, 8))
        k = ease(pr(t, B_GIRL, B_GIRL + 0.6))
        for i in range(10): d.poly([(540 - 60 - i * 6, 0), (540 + 60 + i * 6, 0), (540 + 260 + i * 10, 1500), (540 - 260 - i * 10, 1500)], A((255, 230, 180), 0.025 * k))
        d.ell(540, 1480, 260, 50, A((255, 230, 180), 0.25 * k))
        girl(d, 540, 1200, 210, t, "chill", k)
    elif t < B_STAGE:
        grad(d, (24, 18, 48), (6, 4, 14))
        for i in range(40): d.circ((i * 263) % 1080, (i * 151) % 900, 2 + i % 2, fill=A(WHITE, 0.4 + 0.3 * math.sin(t * 2 + i)))
        tx = 780
        for s_ in (-1, 1): d.line([(tx + s_ * 95, 1520), (tx + s_ * 40, 780)], A((120, 86, 54), 1), 20)
        for k in range(6): d.line([(tx - 88 + k * 8, 1420 - k * 115), (tx + 88 - k * 8, 1420 - k * 115)], A((120, 86, 54), 1), 11)
        d.rect(tx - 75, 720, tx + 75, 785, fill=A((96, 64, 42), 1), r=6); d.circ(tx, 700, 30, fill=A(GOLD, 1))
        on = t > B_FIRE
        if on:
            g = ease(pr(t, B_FIRE, B_FIRE + 0.5))
            for i in range(7): flame(d, 80 + i * 160, 1600, (320 + 110 * math.sin(t * 3 + i)) * g, t, 0.95, i * 4)
            embers(d, t, FIRE_L, 1, 50)
            sparks(d, 600, 1400, t, B_FIRE, 60, 1300, FIRE_L, 1, 9, 1.2)
        girl(d, 330, 1160, 200, t, "scared" if on else "chill", 1)
        if not on:
            hb = 1 + 0.15 * math.sin(t * 9)
            d.text(470, 880, "♥", int(90 * hb), A(PINK, 1), k=2)
            d.text(tx, 640, "♥", 60, A(PINK, 0.8), k=2)
    else:
        grad(d, (44, 10, 14), (10, 3, 5))
        op = ease(pr(t, B_STAGE, B_STAGE + 0.7))
        if t < B_RUM:
            for i in range(5): flame(d, 300 + i * 120, 1380, 200 + 50 * math.sin(t * 4 + i), t, 0.9, i * 3)
            girl(d, 540, 1100, 170, t, "sad", 1)
        else:
            girl(d, 540, 1100, 170, t, "sad", 1)
            bubbles = [(240, 760, "克夫"), (840, 720, "性子烈"), (200, 1300, "不吉利"), (880, 1280, "别娶"), (540, 600, "丙午女")]
            for i, (bx, by, s_) in enumerate(bubbles):
                k = back(pr(t, B_RUM + 0.5 + i * 0.3, B_RUM + 0.75 + i * 0.3))
                sc = 1 + 0.08 * math.sin(t * 6 + i)
                draw_shapes(d, [('e', bx, by, 150 * k * sc + 1, 78 * k * sc + 1, WHITE)], 5, 1)
                d.text(bx, by, s_, int(50 * k) + 1, A(HRED_D, 1), k=1)
        for s_ in (-1, 1):
            x0 = 540 + s_ * (40 + 440 * op)
            for k in range(7):
                xx = x0 + s_ * k * 80
                d.rect(min(xx, xx + s_ * 80), 220, max(xx, xx + s_ * 80), 1720, fill=A(mix(HRED, HRED_D, k % 2), 1))
        d.rect(0, 170, 1080, 270, fill=A(GOLD, 1)); d.rect(0, 1700, 1080, 1920, fill=A((60, 30, 20), 1))
def uB(t, d):
    if t < ls(4):
        d.text(540, 380, "300 多年前", int(120 * back(pr(t, B_GIRL, B_GIRL + 0.25))), A(WHITE, 1), k=1)
        d.text(540, 540, "一个丙午年出生的少女", 62, A(FIRE_L, ease(pr(t, B_GIRL + 0.6, B_GIRL + 0.9))), k=1)
    elif t < B_STAGE:
        d.text(540, 330, "八百屋阿七 · 江户", 68, A(WHITE, ease(pr(t, ls(4), ls(4) + 0.3))), k=1)
        if t > B_FIRE: stamp(d, t, B_FIRE, "纵火", 540, 500, 150, FIRE_L)
    elif t < B_RUM:
        d.text(540, 400, "火刑 → 被编成戏", 80, A(WHITE, ease(pr(t, B_STAGE + 0.4, B_STAGE + 0.7))), k=1)
        d.text(540, 530, "一演几百年", 70, A(FIRE_L, ease(pr(t, B_STAGE + 1.6, B_STAGE + 1.9))), k=1)
    else:
        d.text(540, 400, "谣言", int(110 * back(pr(t, B_RUM, B_RUM + 0.25))), A(WHITE, 1), k=1)
    flash(d, t, [B_FIRE], FIRE_L, 0.55)

# ===== C: why fire =====
C_Q, C_ONE, C_MERGE = ls(7), ls(8), ls(9)
STEMS = "甲乙丙丁戊己庚辛壬癸"; BRANCH = "子丑寅卯辰巳午未申酉戌亥"
def sC(t, d):
    if t < C_ONE:
        grad(d, (40, 14, 10), (10, 4, 4)); embers(d, t, FIRE, 0.6)
        horse(d, 400, 1150, 200, t, "sus", 0, 1, look=(-0.7 if math.sin((t - C_Q) * 5) > 0 else 0.7, 0))
        for i in range(3):
            k = back(pr(t, C_Q + 0.12 * i, C_Q + 0.12 * i + 0.2))
            d.text(740 + i * 100, 760 - i * 50, "?", int(150 * k) + 1, A(YEL, 1), k=1)
    elif t < C_MERGE:
        rays(d, t, (70, 40, 20), (20, 12, 8), 16, 540, 1000)
        u = t - C_ONE
        k1 = back(pr(t, C_ONE, C_ONE + 0.3)); k2 = back(pr(t, C_ONE + 1.7, C_ONE + 2.0))
        glow(d, 280, 760, 200, FIRE_L, k1); d.circ(280, 760, 110 * k1 + 1, fill=A((255, 222, 120), 1))
        for i in range(12):
            ang = t * 0.9 + i * math.pi / 6
            d.line([(280 + math.cos(ang) * 130 * k1, 760 + math.sin(ang) * 130 * k1), (280 + math.cos(ang) * 175 * k1, 760 + math.sin(ang) * 175 * k1)], A(FIRE_L, 1), 12)
        tile(d, 280, 1130, 260 * k1 + 1, "丙", HRED, 1, "天干 · 阳火", glowc=FIRE)
        if k2 > 0:
            horse(d, 760, 800, 105 * k2 + 1, t, "proud", 0.8, 1.0)
            tile(d, 800, 1130, 260 * k2 + 1, "午", HRED, 1, "地支 · 火 · 马", glowc=FIRE)
    else:
        rays(d, t, (140, 40, 16), (50, 10, 6), 22, 540, 1000); embers(d, t, FIRE_L, 1, 40)
        m = eio(pr(t, C_MERGE, C_MERGE + 0.8))
        if m < 1:
            tile(d, lerp(280, 470, m), 1000, 240, "丙", HRED, 1 - m * 0.8, glowc=FIRE)
            tile(d, lerp(800, 610, m), 1000, 240, "午", HRED, 1 - m * 0.8, glowc=FIRE)
        else:
            R = 380; rot = (t - C_MERGE) * 1.6
            for i in range(60):
                ang = rot + i * 2 * math.pi / 60 - math.pi / 2
                on = i == 42
                x, y = 540 + math.cos(ang) * R, 1040 + math.sin(ang) * R
                if on: glow(d, x, y, 70, FIRE, 1)
                d.circ(x, y, 22 if on else 11, fill=A(FIRE_L if on else GOLD, 1 if on else 0.55))
            p = pulse(t, [C_MERGE + 0.8], 3)
            horse(d, 450, 1030, 170 + 20 * p, t, "proud", 1.0, 1.0)
            sparks(d, 540, 1040, t, C_MERGE + 0.8, 70, 1400, FIRE_L, 1, 7, 1.2)
def uC(t, d):
    if t < C_ONE:
        d.text(540, 420, "凭什么这么火？", int(110 * back(pr(t, C_Q, C_Q + 0.25))), A(WHITE, 1), k=1)
    elif t < C_MERGE:
        d.text(540, 380, "丙 ＝ 火", 90, A(WHITE, ease(pr(t, C_ONE, C_ONE + 0.3))), k=1)
        d.text(540, 510, "午 ＝ 火 ＝ 马", 90, A(FIRE_L, ease(pr(t, C_ONE + 1.7, C_ONE + 2.0))), k=1)
    else:
        k = back(pr(t, C_MERGE + 0.8, C_MERGE + 1.05))
        d.text(550, 448, "火 + 火", int(170 * k) + 1, A(HRED_D, 1), k=1); d.text(540, 440, "火 + 火", int(170 * k) + 1, A(FIRE_L, 1), k=1)
        d.text(540, 600, "60 年转一圈", 62, A(WHITE, ease(pr(t, C_MERGE + 1.4, C_MERGE + 1.7))), k=1)
    flash(d, t, [C_MERGE + 0.8], WHITE, 0.8)

# ===== D: China =====
D_JIE, D_JAIL, D_SEAL = ls(10), ls(11) + 1.6, ls(12) + 2.2
def sD(t, d):
    if t < ls(11):
        rays(d, t, (130, 22, 16), (40, 6, 6), 18, 540, 1050); embers(d, t, FIRE_L, 1)
        k1 = back(pr(t, D_JIE, D_JIE + 0.3)); k2 = back(pr(t, D_JIE + 0.5, D_JIE + 0.8))
        horse(d, 260, 1150, 150 * k1 + 1, t, "angry", 0.7, 1.0)
        goat(d, 760, 1160, 165 * k2 + 1, t, "angry", 1, 1, flip=-1)
        n = int(cl((t - D_JIE - 2.2) / 2.5) * 21)
        for k in range(n):
            gx = 160 + (k % 11) * 76; gy = 640 + (k // 11) * 80
            d.rect(gx - 30, gy - 30, gx + 30, gy + 30, fill=A(HRED, 1), r=8); d.text(gx, gy, "乱", 34, A(WHITE, 1), k=1)
    elif t < ls(12):
        paper_bg(d, t)
        scholar(d, 540, 1100, 230, t, "scared" if t > D_JAIL else "proud", 1, 0.3 if t < D_JAIL else 1.0)
        if t < D_JAIL:
            k = back(pr(t, ls(11), ls(11) + 0.3))
            d.rect(640, 960, 900, 1080, fill=A(PAPER, 1), r=8); d.text(770, 1020, "丙丁龟鉴", 42, A(INKB, 1), k=1)
        drop = ease(pr(t, D_JAIL, D_JAIL + 0.25))
        if drop > 0:
            for i in range(8):
                x = 160 + i * 108
                d.rect(x - 14, -1400 + 2200 * drop, x + 14, 800 * drop + 800, fill=A((70, 70, 80), 1), r=8)
    else:
        grad(d, (232, 216, 178), (196, 172, 128))
        for i in range(6):
            d.rect(140, 1500 - i * 70, 940, 1560 - i * 70, fill=A(mix((80, 50, 30), (130, 80, 40), i / 6), 1), r=6)
        d.rect(240, 640, 840, 1080, fill=A(PAPER, 1), r=10); d.rect(240, 640, 840, 1080, outline=A(PAPER_D, 1), w=6, r=10)
        d.text(540, 740, "四库全书总目", 56, A(INKB, 1), k=1)
        d.text(540, 850, "所列事迹", 64, A(INKB, ease(pr(t, ls(12) + 1.0, ls(12) + 1.3))), k=1)
        if t >= D_SEAL:
            k = back(pr(t, D_SEAL, D_SEAL + 0.15)); sz = 2.0 - k
            d.rect(540 - 250 * sz, 975 - 80 * sz, 540 + 250 * sz, 975 + 80 * sz, fill=A(HRED, min(1, k)), r=12)
            d.text(540, 975, "多涉牵就", int(108 * sz), A(WHITE, min(1, k)), k=1)
            sparks(d, 540, 975, t, D_SEAL, 30, 900, HRED, 1, 4, 0.6)
        horse(d, 850, 1290, 100, t, "proud" if t > D_SEAL else "sus", 0, 1, flip=-1)
def uD(t, d):
    if t < ls(11):
        k = back(pr(t, D_JIE + 2.0, D_JIE + 2.25))
        d.text(540, 330, "南宋 · 柴望统计", 66, A(WHITE, ease(pr(t, D_JIE, D_JIE + 0.3))), k=1)
        d.text(550, 498, "赤马红羊劫", int(140 * k) + 1, A(INKB, 1), k=1); d.text(540, 490, "赤马红羊劫", int(140 * k) + 1, A(FIRE_L, 1), k=1)
    elif t < ls(12):
        d.text(540, 380, "献书给皇帝", 84, A(WHITE, ease(pr(t, ls(11), ls(11) + 0.3))), k=1)
        if t > D_JAIL: stamp(d, t, D_JAIL, "下狱", 540, 540, 160, HRED)
    else:
        d.text(540, 380, "＝ 硬凑", int(110 * back(pr(t, D_SEAL + 0.5, D_SEAL + 0.75))) + 1, A(HRED, 1), k=1)
    flash(d, t, [D_JIE + 2.0], FIRE_L, 0.4); flash(d, t, [D_JAIL], WHITE, 0.6); flash(d, t, [D_SEAL], HRED, 0.4)

# ===== E: data =====
E_PYR, E_1906, E_BAR, E_TWIST, E_SHIFT = ls(13), ls(14), ls(15), ls(16), ls(17)
BARS = [(1965, 182.4), (1966, 136.1), (1967, 193.6)]
def pyramid(d, t, k):
    for i in range(46):
        age = 59 - i  # rows: 1966 cohort at index 
        y = 700 + i * 20
        wv = 300 + 60 * math.sin(i * 0.25) - i * 1.5
        if i == 23: wv *= 0.62
        w = wv * ease(pr(k, i / 60, i / 60 + 0.4))
        col = WARN if i == 23 else (90, 130, 210)
        d.rect(540 - w, y, 538, y + 16, fill=A(col, 1)); d.rect(542, y, 540 + w * 0.96, y + 16, fill=A(mix(col, PINK, 0.5), 1))
def sE(t, d):
    if t < E_1906:
        grad(d, (14, 18, 36), (4, 6, 12))
        pyramid(d, t, (t - E_PYR) / 1.2)
        if t > E_PYR + 1.0:
            a = 0.5 + 0.5 * math.sin(t * 8)
            d.rect(120, 1155, 960, 1185, outline=A(YEL, a), w=5, r=6)
            d.text(1000, 1170, "1966", 36, A(YEL, 1), k=1)
    elif t < E_BAR:
        grad(d, (24, 16, 30), (8, 6, 12))
        k = ease(pr(t, E_1906, E_1906 + 0.5))
        # scale balance
        tilt = 0.18 * ease(pr(t, E_1906 + 1.0, E_1906 + 1.8))
        cx, cy = 540, 900
        d.line([(cx, cy), (cx, 1400)], A(GOLD, k), 16); d.rect(cx - 120, 1390, cx + 120, 1420, fill=A(GOLD, k), r=8)
        lx, ly = cx - 330 * math.cos(tilt), cy + 330 * math.sin(tilt); rx, ry = cx + 330 * math.cos(tilt), cy - 330 * math.sin(tilt)
        d.line([(lx, ly), (rx, ry)], A(GOLD, k), 14)
        for (px, py, col, lab, n) in ((lx, ly, BLUE, "男婴 108.7", 6), (rx, ry, PINK, "女婴 100", 5)):
            d.line([(px, py), (px, py + 140)], A(GOLD, k), 5)
            d.ell(px, py + 160, 150, 34, A(GOLD, k))
            for j in range(n): baby(d, px - 100 + (j % 3) * 100, py + 110 - (j // 3) * 70, 28, k, (255, 214, 186))
            d.text(px, py + 260, lab, 48, A(col, k), k=1)
        # girls sliding out to other-year boxes
        for j in range(4):
            u = ease(pr(t, E_1906 + 2.4 + j * 0.25, E_1906 + 3.0 + j * 0.25))
            if u > 0:
                tx = 160 if j % 2 == 0 else 920
                x = lerp(rx, tx, u); y = lerp(ry + 100, 650, u) - math.sin(u * math.pi) * 120
                baby(d, x, y, 26, 1, (255, 190, 200))
        for bx, lab in ((150, "1905"), (930, "1907")):
            a = ease(pr(t, E_1906 + 2.3, E_1906 + 2.6))
            d.rect(bx - 105, 590, bx + 105, 700, outline=A(WHITE, a), w=4, r=14); d.text(bx, 740, lab, 40, A(WHITE, a), k=1)
    else:
        tw = t >= E_TWIST
        grad(d, (14, 18, 34) if not tw else (14, 32, 30), (4, 6, 12))
        base, x0 = 1320, 220
        for i, (yr, v) in enumerate(BARS):
            g = ease(pr(t, E_BAR + 0.2 + i * 0.4, E_BAR + 0.7 + i * 0.4))
            if i == 1: g = ease(pr(t, E_BAR + 1.6, E_BAR + 2.3))
            h = v / 200 * 650 * g; x = x0 + i * 320
            col = WARN if i == 1 else (BLUE if t < E_SHIFT + 2.5 else JADE)
            d.rect(x - 100, base - h, x + 100, base, fill=A(col, 1), r=12)
            d.text(x, base + 60, str(yr), 52, A(WHITE, 1), k=1)
            if g > 0.1: d.text(x, base - h - 50, f"{v:.0f}万", 56, A(WHITE, g), k=1)
            if i == 1 and g > 0: d.rect(x - 100, base - 182.4 / 200 * 650, x + 100, base - h, outline=A(WARN, 0.8 * g), w=5, r=12)
        if E_TWIST <= t < E_SHIFT:
            for j in range(3):  # 2nd/3rd child icons fading from 1966 bar
                k = back(pr(t, E_TWIST + 1.4 + j * 0.2, E_TWIST + 1.6 + j * 0.2))
                bx = x0 + 320 + (j - 1) * 70
                baby(d, bx, base - 520, 30 * k + 1, 1, (255, 214, 186))
                if k > 0.5: d.text(bx, base - 590, ["一胎", "二胎", "三胎"][j], 30, A(WHITE if j == 0 else WARN, 1), k=1)
        if t >= E_SHIFT:
            for i in range(12):
                u = ease(pr(t, E_SHIFT + 0.4 + i * 0.12, E_SHIFT + 1.2 + i * 0.12))
                tx = x0 if i % 2 == 0 else x0 + 640
                sx, sy = x0 + 320, base - 470 - (i // 2) * 30
                x = lerp(sx, tx + ((i // 2) - 2.5) * 34, u); y = lerp(sy, 590, u) - math.sin(u * math.pi) * 110
                baby(d, x, y, 22)
def uE(t, d):
    if t < E_1906:
        d.text(540, 330, "日本人口金字塔", 74, A(WHITE, ease(pr(t, E_PYR, E_PYR + 0.3))), k=1)
        d.text(540, 460, "缺了一大块", 74, A(WARN, ease(pr(t, E_PYR + 1.0, E_PYR + 1.3))), k=1)
    elif t < E_BAR:
        d.text(540, 330, "1906 · 丙午", int(100 * back(pr(t, E_1906, E_1906 + 0.25))), A(WHITE, 1), k=1)
        d.text(540, 470, "女婴“消失”了", 72, A(PINK, ease(pr(t, E_1906 + 2.4, E_1906 + 2.7))), k=1)
    elif t < E_TWIST:
        d.text(540, 330, "1966 · 出生人数", 70, A(WHITE, ease(pr(t, E_BAR, E_BAR + 0.3))), k=1)
        if t > E_BAR + 2.3: stamp(d, t, E_BAR + 2.3, "-25%", 540, 500, 170, WARN)
    elif t < E_SHIFT:
        k = back(pr(t, E_TWIST, E_TWIST + 0.3))
        d.rect(170, 400, 910, 560, fill=A(JADE, min(1, k)), r=30)
        d.text(540, 480, "真相反转", int(110 * k) + 1, A(WHITE, 1), k=1)
    else:
        d.text(540, 330, "孩子只是挪了一年", 72, A(WHITE, 1), k=1)
        if t > E_SHIFT + 2.5: stamp(d, t, E_SHIFT + 2.5, "+20多万", 540, 490, 120, YEL)
    flash(d, t, [E_BAR + 2.3], WARN, 0.4); flash(d, t, [E_TWIST], WHITE, 0.7)

# ===== F: climax =====
F_NOW, F_EMPTY, F_TFR, F_ALL = ls(18), ls(19), ls(20), ls(21)
TFR = [(1960, 2.00), (1965, 2.14), (1966, 1.58), (1967, 2.23), (1970, 2.13), (1973, 2.14), (1975, 1.91), (1980, 1.75), (1985, 1.76), (1989, 1.57), (1990, 1.54),
       (1995, 1.42), (2000, 1.36), (2005, 1.26), (2010, 1.39), (2015, 1.45), (2020, 1.33), (2022, 1.26), (2023, 1.20), (2024, 1.15), (2025, 1.14)]
def tx_(y): return 110 + (y - 1960) / 65 * 860
def ty_(v): return 1400 - (v - 1.0) / 1.4 * 700
def sF(t, d):
    if t < F_TFR:
        grad(d, (12, 26, 30), (4, 8, 10))
        if t < F_EMPTY:
            g = ease(pr(t, F_NOW + 0.3, F_NOW + 1.6))
            pts = [(110 + k * 8, 1050 + 6 * math.sin(k * 0.3)) for k in range(int(108 * g) + 1)]
            if len(pts) > 1: d.line(pts, A(JADE, 1), 10)
            horse(d, 540, 1290, 120, t, "sus", 0, 1)
        else:
            # empty basket being shaken
            sh = math.sin(t * 22) * 14 * (1 - pr(t, F_EMPTY + 1.2, F_EMPTY + 1.6))
            bx, by = 540 + sh, 1050
            draw_shapes(d, [('p', [(bx - 260, by - 120), (bx + 260, by - 120), (bx + 200, by + 160), (bx - 200, by + 160)], (180, 130, 70))], 7, 1)
            for i in range(5): d.line([(bx - 240 + i * 4, by - 60 + i * 50), (bx + 240 - i * 4, by - 60 + i * 50)], A((130, 90, 46), 1), 6)
            d.ell(bx, by - 120, 260, 40, A((70, 46, 26), 1))
            horse(d, 200, 1340, 90, t, "sad", 0, 0.6)
    elif t < F_ALL:
        grad(d, (20, 12, 16), (6, 3, 5))
        for v in (1.0, 1.5, 2.0):
            d.line([(110, ty_(v)), (970, ty_(v))], A(WHITE, 0.12), 2); d.text(80, ty_(v), f"{v:.1f}", 26, A(WHITE, 0.5), k=0)
        g = pr(t, F_TFR + 0.3, F_TFR + 4.2)
        yr = 1960 + 65 * g
        a = ease(pr(t, F_TFR + 0.6, F_TFR + 1.0))
        d.line([(110, ty_(1.58)), (970, ty_(1.58))], A(WARN, a), 5)
        pts = []
        for (y0, v0), (y1, v1) in zip(TFR, TFR[1:]):
            if y0 > yr: break
            y1c = min(y1, yr); v1c = lerp(v0, v1, (y1c - y0) / (y1 - y0))
            pts.append((tx_(y0), ty_(v0))); last = (tx_(y1c), ty_(v1c))
        if pts:
            pts.append(last)
            if yr > 1989:
                below = [(x, y) for x, y in pts if x >= tx_(1989)]
                if len(below) > 1: d.poly(below + [(below[-1][0], ty_(1.58)), (tx_(1989), ty_(1.58))], A(WARN, 0.35))
            d.line(pts, A(WHITE, 1), 9); glow(d, last[0], last[1], 40, YEL, 1); d.circ(last[0], last[1], 12, fill=A(YEL, 1))
        if yr > 1966.3: d.text(tx_(1966), ty_(1.58) + 50, "1966", 30, A(WARN, 1), k=1)
        if yr > 1989.3:
            k = back(pr(t, F_TFR + 0.3 + 29 / 65 * 3.9, F_TFR + 0.5 + 29 / 65 * 3.9))
            d.text(tx_(1989), ty_(1.58) - 60, "1989：1.57", int(44 * k) + 1, A(YEL, 1), k=1)
        if g >= 1: d.text(tx_(2025) - 90, ty_(1.14) + 50, "2025：1.14", 36, A(YEL, 1), k=1)
    else:
        rays(d, t, (140, 20, 18), (40, 4, 6), 24, 540, 1050); embers(d, t, FIRE_L, 1, 50)
        u = t - F_ALL
        yrs = list(range(1989, 2026))
        n = int(cl(u / 2.2) * len(yrs))
        for j in range(min(n, 12)):
            idx = n - 1 - j
            ox = (j % 4 - 1.5) * 220; oy = (j // 4) * 230
            x, y = 540 + ox, 820 + oy
            rot_a = 0.12 * math.sin(idx)
            d.rect(x - 95, y - 105, x + 95, y + 105, fill=A(PAPER, 1), r=12)
            d.rect(x - 95, y - 105, x + 95, y - 60, fill=A(HRED, 1), r=12)
            d.text(x, y - 82, str(yrs[idx]), 30, A(WHITE, 1), k=1)
            d.text(x, y + 25, "丙午", 64, A(HRED, 1), k=1)
        p = pulse(t, [F_ALL + 2.4], 2.5)
        if t > F_ALL + 2.4:
            sparks(d, 540, 1100, t, F_ALL + 2.4, 100, 1700, FIRE_L, 1, 11, 1.5)
def uF(t, d):
    if t < F_EMPTY:
        d.text(540, 380, "2026 年 1 月 · 日本出生", 66, A(WHITE, ease(pr(t, F_NOW, F_NOW + 0.3))), k=1)
        k = back(pr(t, F_NOW + 1.6, F_NOW + 1.85))
        d.text(540, 600, "+0.5%", int(210 * k) + 1, A(JADE, 1), k=1)
    elif t < F_TFR:
        k = back(pr(t, F_EMPTY + 1.0, F_EMPTY + 1.25))
        d.text(540, 420, "没得可减了", int(130 * k) + 1, A(WHITE, 1), k=1)
    elif t < F_ALL:
        d.text(540, 330, "日本总和生育率", 72, A(WHITE, ease(pr(t, F_TFR, F_TFR + 0.3))), k=1)
        d.text(540, 450, "红线 ＝ 1966 丙午年 1.58", 52, A(WARN, ease(pr(t, F_TFR + 0.6, F_TFR + 0.9))), k=1)
    else:
        k = back(pr(t, F_ALL + 2.4, F_ALL + 2.65))
        if t > F_ALL + 2.4:
            d.text(550, 478, "每一年都是丙午", int(120 * k) + 1, A(INKB, 1), k=1); d.text(540, 470, "每一年都是丙午", int(120 * k) + 1, A(FIRE_L, 1), k=1)
        else:
            d.text(540, 470, "1989 → 2025", 100, A(WHITE, 1), k=1)
    flash(d, t, [F_EMPTY + 1.0], WHITE, 0.4); flash(d, t, [F_ALL + 2.4], WHITE, 0.95)

# ===== G: outro =====
def sG(t, d):
    grad(d, (34, 12, 10), (8, 3, 3)); embers(d, t, FIRE_L, 0.7)
    R = 360; rot = t * 0.35
    for i in range(60):
        ang = rot + i * 2 * math.pi / 60
        on = i == 42
        x, y = 540 + math.cos(ang) * R, 1060 + math.sin(ang) * R
        if on: glow(d, x, y, 60, FIRE, 1)
        d.circ(x, y, 20 if on else 10, fill=A(FIRE_L if on else GOLD, 1 if on else 0.5))
    horse(d, 300, 1080, 110, t, "proud", 0.5, 1.0)
    goat(d, 790, 1110, 105, t, "chill", 1, 1, flip=-1)
def uG(t, d):
    d.text(540, 330, "双火马年", int(120 * back(pr(t, G0, G0 + 0.25))), A(FIRE_L, 1), k=1)
    d.text(540, 480, "不是命", 100, A(WHITE, ease(pr(t, G0 + 1.0, G0 + 1.3))), k=1)
    end = le(22)
    if t > end + 0.2:
        a = ease(pr(t, end + 0.2, end + 0.5))
        d.rect(90, 1460, 990, 1680, fill=A((0, 0, 0), 0.65 * a), r=30)
        d.text(540, 1530, "你觉得年轻人不生，", 52, A(WHITE, a), k=1)
        d.text(540, 1610, "真正的原因是什么？", 52, A(FIRE_L, a), k=1)
        d.text(540, 1780, "资料：日本厚生劳动省人口动态统计 · 《四库全书总目提要》· Kikkawa, nippon.com 2025 · 日本综研 2026", 22, A(WHITE, 0.8 * a), k=0)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

def subs(t, d):
    for i, (a, b) in enumerate(L):
        if a - 0.05 <= t < b + 0.15:
            s = LINES[i].rstrip("。？")
            al = ease(pr(t, a - 0.05, a + 0.1)) * (1 - pr(t, b + 0.05, b + 0.15))
            lines = wrap(d, s, 56, 900)
            for j, ln in enumerate(lines):
                y = 1590 + (j - (len(lines) - 1) / 2) * 82
                w = d.tlen(ln, 56)
                d.rect(540 - w / 2 - 22, y - 42, 540 + w / 2 + 22, y + 42, fill=A((0, 0, 0), 0.62 * al), r=14)
                d.text(540, y, ln, 56, A(WHITE, al))
def brand(t, d):
    d.rect(50, 80, 300, 128, fill=A(WHITE, 0.92), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(BG, 1))
    d.rect(780, 80, 1030, 128, fill=A(HRED, 0.92), r=24); d.text(905, 104, "丙午 · 双火马年", 26, A(WHITE, 1))

SECS = [(A0, B0, sA, uA), (B0, C0, sB, uB), (C0, D0, sC, uC), (D0, E0, sD, uD), (E0, F0, sE, uE), (F0, G0, sF, uF), (G0, 999, sG, uG)]
KEYHITS = [H_BOOM, H_NUM - 0.2, B_FIRE, C_MERGE + 0.8, D_JIE + 2.0, D_JAIL, D_SEAL, E_BAR + 2.3, E_TWIST, F_EMPTY + 1.0, F_ALL + 2.4]

def cam(t):
    z = 1.0 + 0.06 * pulse(t, KEYHITS, 6) + 0.015 * pulse(t, [a for a, b in L], 8)
    if t < 1.0: z += 0.35 * (1 - ease(pr(t, 0, 0.45)))
    amp = 26 * pulse(t, [H_BOOM, F_ALL + 2.4], 2.5) + 12 * pulse(t, KEYHITS, 4)
    sx, sy = shake(t, amp, 61)
    for a, b, *_ in SECS:
        if a <= t < b: z += 0.05 * eio(pr(t, a, min(b, a + 8)))
    return z, 540 + sx, 960 + sy

def frame(t):
    img = Image.new("RGB", (W, H), BG); d = D(img); ui = None
    for a, b, sf, uf in SECS:
        if a <= t < b: sf(t, d); ui = uf; break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    d = D(img)
    if ui: ui(t, d)
    for c in CUTS:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - (t - c) / 0.1)))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)

if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.1f}.png")
    elif sys.argv[1] == "times":
        print({k: round(v, 2) for k, v in dict(B0=B0, C0=C0, D0=D0, E0=E0, F0=F0, G0=G0, DUR=DUR).items()})
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        last = None
        for i in range(i0, i1):
            try: last = frame(i / FPS).tobytes()
            except Exception as e: print('ERR', i, e, file=sys.stderr)
            if last: p.stdin.write(last)
        p.stdin.close(); p.wait()
