# 《为什么第一口奶茶最好喝？》9:16, 154 s. Safe zone x 180–900, y < 1440. Bright backgrounds, plain words, no dark outlines.
import sys, subprocess, math, random
sys.path.insert(0, "/workspace/work/ufo")
import film
film.SUIT = (255, 130, 90)
from film import (D, A, P, W, H, OW, OH, FPS, Image, cl, ease, back, pr, lerp, mix, pulse, pop, shake, glow, face, agent, wrap2,
                  WHITE, INKC, RED2, CY, GOLD, SUIT, SKIN, PAPERC)
from film2 import grad, rays, hills, headline, tag, bubble, verdict, DARKT
from mcues import *

PINK = (255, 150, 180); TEA = (214, 160, 110); TEA_L = (236, 196, 150); PEARL = (70, 44, 36); CHOC = (110, 64, 40); CHOC_L = (150, 96, 60)
GREEN = (70, 200, 120); PURP = (160, 90, 220); BLUE = (60, 150, 240)
def person(d, x, y, s, a=1.0, kind="happy", shirt=(255, 230, 120)): agent(d, x, y, s, a, kind, glasses=False, tie=shirt)

def cup(d, x, y, s, a=1.0, kind="happy", fill=1.0, t=0.0, look=0.0):
    w0, w1, h = s * 0.62, s * 0.48, s * 1.5
    d.poly([(x - w0, y - h / 2), (x + w0, y - h / 2), (x + w1, y + h / 2), (x - w1, y + h / 2)], A((250, 244, 236), 0.55 * a))
    ft = y + h / 2 - h * 0.92 * fill; k = (ft - (y - h / 2)) / h; wl = lerp(w0, w1, k)
    if fill > 0.02: d.poly([(x - wl, ft), (x + wl, ft), (x + w1, y + h / 2), (x - w1, y + h / 2)], A(TEA, a))
    r = random.Random(7)
    for i in range(int(14 * min(1, fill * 3))):
        px = x + r.uniform(-w1 * 0.8, w1 * 0.8); py = y + h / 2 - r.uniform(s * 0.08, s * 0.35); d.circ(px, py, s * 0.07, fill=A(PEARL, a))
    d.rect(x - w0 - s * 0.06, y - h / 2 - s * 0.12, x + w0 + s * 0.06, y - h / 2 + s * 0.02, fill=A(PINK, a), r=s * 0.05)
    d.line([(x + s * 0.12, y - h / 2 - s * 0.1), (x + s * 0.3, y - h / 2 - s * 0.62)], A((255, 90, 120), a), s * 0.1)
    d.ell(x - w0 * 0.55, y - h * 0.18, s * 0.06, s * 0.25, A(WHITE, 0.4 * a))
    face(d, x, y + h * 0.05, s * 0.42, kind, a, look)
def joybar(d, x, ybase, v, a=1.0, w=90, scale=34, col=None):
    col = col or (GREEN if v >= 0 else RED2)
    if v >= 0: d.rect(x - w / 2, ybase - v * scale, x + w / 2, ybase, fill=A(col, a), r=12)
    else: d.rect(x - w / 2, ybase, x + w / 2, ybase - v * scale, fill=A(col, a), r=12)
    d.text(x, ybase - v * scale - 34 if v >= 0 else ybase - v * scale + 34, f"{v:+d}" if v else "0", 40, A(DARKT, a), k=1)
def brain(d, x, y, s, a=1.0, good=0.0, bad=0.0):
    d.ell(x, y, s, s * 0.78, A((255, 170, 190), a))
    for i in range(5):
        d.arc(x - s * 0.6 + i * s * 0.3, y - s * 0.1, s * 0.22, s * 0.3, 200, 340, A((230, 130, 160), a), s * 0.05)
        d.arc(x - s * 0.45 + i * s * 0.25, y + s * 0.3, s * 0.2, s * 0.2, 20, 160, A((230, 130, 160), a), s * 0.05)
    if good > 0: glow(d, x - s * 0.15, y + s * 0.05, s * 0.75, (255, 220, 60), good * a); d.circ(x - s * 0.15, y + s * 0.05, s * 0.16, fill=A((255, 230, 90), good * a))
    if bad > 0: glow(d, x + s * 0.3, y - s * 0.2, s * 0.75, PURP, bad * a); d.circ(x + s * 0.3, y - s * 0.2, s * 0.16, fill=A((190, 120, 255), bad * a))
def choco(d, x, y, s, a=1.0):
    d.rect(x - s, y - s * 0.6, x + s, y + s * 0.6, fill=A(CHOC, a), r=s * 0.15)
    for i in range(3):
        for j in range(2): d.rect(x - s * 0.9 + i * s * 0.62, y - s * 0.5 + j * s * 0.52, x - s * 0.36 + i * s * 0.62, y - s * 0.04 + j * s * 0.52, fill=A(CHOC_L, a), r=s * 0.08)
def drop(d, x, y, s, a=1.0, kind="happy"):
    d.poly([(x, y - s * 1.3), (x - s * 0.8, y), (x + s * 0.8, y)], A((90, 180, 255), a)); d.circ(x, y + s * 0.1, s * 0.85, fill=A((90, 180, 255), a))
    d.ell(x - s * 0.35, y - s * 0.1, s * 0.15, s * 0.3, A(WHITE, 0.5 * a)); face(d, x, y + s * 0.15, s * 0.55, kind, a)
def diamond(d, x, y, s, a=1.0, kind="happy", t=0.0):
    glow(d, x, y, s * 1.8, (200, 240, 255), 0.6 * a)
    top = [(x - s, y - s * 0.3), (x - s * 0.55, y - s * 0.8), (x + s * 0.55, y - s * 0.8), (x + s, y - s * 0.3)]
    d.poly(top + [(x, y + s)], A((170, 230, 255), a)); d.poly([(x - s, y - s * 0.3), (x + s, y - s * 0.3), (x, y + s)], A((120, 200, 250), a))
    d.poly([(x - s * 0.55, y - s * 0.8), (x - s * 0.2, y - s * 0.3), (x + s * 0.2, y - s * 0.3), (x + s * 0.55, y - s * 0.8)], A((220, 248, 255), a))
    face(d, x, y + s * 0.05, s * 0.45, kind, a)
def parcel(d, x, y, s, a=1.0, opened=0.0):
    d.rect(x - s, y - s * 0.7, x + s, y + s * 0.7, fill=A((222, 170, 110), a), r=s * 0.08)
    d.rect(x - s * 0.12, y - s * 0.7, x + s * 0.12, y + s * 0.7, fill=A((250, 220, 140), a))
    if opened > 0: d.poly([(x - s, y - s * 0.7), (x - s * 1.3, y - s * (0.7 + 0.6 * opened)), (x - s * 0.2, y - s * 0.7)], A((200, 150, 95), a)); d.poly([(x + s, y - s * 0.7), (x + s * 1.3, y - s * (0.7 + 0.6 * opened)), (x + s * 0.2, y - s * 0.7)], A((200, 150, 95), a))
def ticket(d, x, y, s, a=1.0, ang=0.0):
    d.rect(x - s, y - s * 0.5, x + s, y + s * 0.5, fill=A((255, 214, 80), a), r=s * 0.1)
    d.text(x, y - s * 0.1, "LOTTERY", int(s * 0.32), A(RED2, a), k=1); d.text(x, y + s * 0.25, "$50,000", int(s * 0.28), A(DARKT, a), k=1)
def bars2(d, t, t0, lab, v1, v2, l1, l2, vmax=5.0):
    for i, (v, l, col) in enumerate(((v1, l1, GOLD), (v2, l2, BLUE))):
        k = ease(pr(t, t0 + i * 0.3, t0 + 0.9 + i * 0.3)); x = 400 + i * 280; hh = 520 * v / vmax * k
        d.rect(x - 85, 1050 - hh, x + 85, 1050, fill=A(col, 1), r=16)
        d.text(x, 1050 - hh - 45, f"{v * k:.2f}", 52, A(WHITE, 1), k=1); tag(d, x, 1100, l, 38)
    d.text(540, 440, lab, 46, A(WHITE, 1), k=1)

# ---------------- scenes ----------------
def bg_pink(d, t): grad(d, (255, 140, 170), (255, 205, 150)); rays(d, t, 540, 820, WHITE, 0.12)
def s_hook(t, d):
    bg_pink(d, t)
    if t < 3:
        q = pop(t, HIT0, 0.35); cup(d, 540, 820, 230 * (0.8 + 0.2 * q), 1, "happy", 1, t)
        for i in range(10):
            ang = i * 0.63 + t; rr = 330 + 60 * math.sin(t * 3 + i); d.text(540 + rr * math.cos(ang), 820 + rr * math.sin(ang) * 0.8, "♥" if False else "+", 64, A(WHITE, 0.8), k=1)
        headline(d, "第一口 = 最好喝", t, 0.2, RED2, WHITE, 400, 78)
    elif t < 6.5:
        for i in range(5):
            x = 230 + i * 155; cup(d, x, 830, 75, 1, ["happy", "happy", "sus", "shock", "scared"][i], 1 - i * 0.0, t)
            d.text(x, 980, f"第{i + 1}杯", 34, A(DARKT, 1), k=1)
        person(d, 540, 1080, 70, 1, "shock"); headline(d, "第五杯喝不下了？", t, 3.1, WHITE, DARKT, 400, 72)
    else:
        q = pop(t, 6.6, 0.3); d.rect(220, 560, 860, 960, fill=A(DARKT, 0.92 * cl(q * 3)), r=40)
        d.text(540, 680, "一条经济学规律", 64, A(GOLD, cl(q * 3)), k=1); d.text(540, 820, "奶茶·巧克力·钻石", 52, A(WHITE, cl(q * 3)), k=1); d.text(540, 900, "双11·彩票", 52, A(WHITE, cl(q * 3)), k=1)
def s_c1(t, d):
    grad(d, (255, 236, 210), (255, 200, 170))
    vals = [10, 6, 3, 1, -3]; times = [12.5, 16.5, 20.0, 22.0, 23.5]
    if t < 12.5:
        k = back(pr(t, 10, 10.6)); cup(d, 540, 800, 200 * cl(k), cl(k * 2), "sus", 1, t); person(d, 540, 1180, 70, 1, "happy")
        return
    if t < 31:
        n = sum(1 for x in times if t >= x)
        cur = n - 1; kinds = ["happy", "happy", "sus", "sus", "angry"]
        person(d, 300, 680, 110, 1, ["happy", "happy", "sus", "sus", "angry"][cur])
        cup(d, 700, 660, 110, 1, ["happy", "happy", "sus", "shock", "scared"][cur], 1 - pr(t, times[cur], times[cur] + 2.5) * 0.7, t)
        if cur == 0: glow(d, 300, 680, 300, (255, 230, 90), 1 - pr(t, 12.5, 15)); headline(d, "快乐爆表！", t, 12.6, RED2, WHITE, 400, 84)
        if cur == 4: headline(d, "拿开！", t, 23.6, RED2, WHITE, 400, 84)
        d.line([(200, 1120), (880, 1120)], A(DARKT, 0.6), 4)
        for i in range(n):
            joybar(d, 260 + i * 140, 1120, vals[i], ease(pr(t, times[i], times[i] + 0.3)) * 1.0, 96, 19)
        d.text(880, 850, "快乐值（示意）", 30, A(DARKT, 0.7), anchor="rm", k=1)
        if t > 27.5:
            k = ease(pr(t, 27.6, 28.6)); d.line([(260, 1120 - 190), (260 + 560 * k, 1120 - 190 + 247 * k)], A(RED2, 1), 12)
    elif t < 35:
        q = pop(t, 31.1, 0.3); d.rect(200, 520, 880, 860, fill=A(DARKT, 0.94 * cl(q * 3)), r=36)
        d.text(540, 610, "经济学名词", 44, A((200, 200, 220), cl(q * 3)), k=1); d.text(540, 740, "边际效用递减", 96, A(GOLD, cl(q * 3)), k=1)
        for i, v in enumerate([10, 6, 3, 1, -3]): joybar(d, 260 + i * 140, 1120, v, 1, 96, 19)
    else:
        for i in range(5): cup(d, 260 + i * 140, 760, 55, 1, "happy" if i < 4 else "shock", 1, t)
        k = ease(pr(t, 35.4, 36)); d.rect(780, 640, 900, 900, outline=A(RED2, k), w=10, r=20)
        tag(d, 680, 1000, "边际 = 多出来的这一杯", 46, WHITE, RED2, k)
        tag(d, 540, 400, "1854年 · 德国人戈森最早写下", 40, a=ease(pr(t, 36.5, 37)))
def s_c2(t, d):
    grad(d, (40, 150, 170), (120, 210, 200))
    if t < 43:
        q = pop(t, 40.1, 0.3); d.rect(200, 560, 880, 960, fill=A(DARKT, 0.92 * cl(q * 3)), r=40)
        d.text(540, 680, "巧克力实验", 84, A(GOLD, cl(q * 3)), k=1); d.text(540, 820, "2001年 · 美国 / 加拿大", 46, A(WHITE, cl(q * 3)), k=1); return
    if t < 50.5:
        d.ell(540, 720, 260, 260, A((235, 240, 245), 1)); d.ell(540, 720, 165, 165, A((40, 150, 170), 1))
        person(d, 540, 700, 70, 1, "happy")
        for i in range(9):
            k = back(pr(t, 43.3 + i * 0.12, 43.6 + i * 0.12)); x = 230 + i * 77; d.circ(x, 1030, 28 * cl(k), fill=A(SKIN, cl(k)))
        tag(d, 540, 1100, "9 个巧克力迷", 40, a=ease(pr(t, 43.5, 44)))
        if t > 47:
            for i in range(7): choco(d, 250 + i * 97, 420, 38, ease(pr(t, 47.1 + i * 0.15, 47.4 + i * 0.15)))
    else:
        n = 1 + min(6, int((t - 50.5) / 2.2))
        good = max(0, 1 - (t - 51) / 6); bad = cl((t - 58) / 1.5)
        brain(d, 540, 720, 240, 1, good, bad)
        if good > 0.2: tag(d, 360, 980, "奖励区", 40, DARKT, (255, 230, 90), good)
        if bad > 0.1: tag(d, 720, 980, "讨厌区", 40, WHITE, PURP, bad)
        for i in range(n): choco(d, 230 + i * 104, 420, 40, 1)
        if t < 66:
            score = [7, 6, 4, 3, 1, -1, -3][n - 1]
            d.rect(700, 1060, 890, 1170, fill=A(WHITE, 0.95), r=20); d.text(795, 1115, f"打分 {score:+d}", 40, A(GREEN if score > 0 else RED2, 1), k=1)
            d.rect(190, 1060, 400, 1170, fill=A(WHITE, 0.95), r=20); d.text(295, 1115, f"第 {n} 块", 40, A(DARKT, 1), k=1)
        if 66 <= t < 69:
            q = pop(t, TOILET, 0.3); d.text(540, 1100, "想吐", int(170 * (0.7 + 0.3 * q)), A(PURP, cl(q * 3)), k=1)
        verdict(d, t, 70.0, "多了也腻", PURP, 1060, 96)
def s_c3(t, d):
    grad(d, (50, 120, 220), (130, 200, 250))
    if t < 75.5:
        drop(d, 360, 760, 110, 1, "sus"); diamond(d, 740, 740, 120, 1, "happy", t)
        tag(d, 360, 960, "水 · 便宜", 46); tag(d, 740, 960, "钻石 · 贵", 46); headline(d, "为什么？", t, 72.2, RED2, WHITE, 420, 84)
    elif t < 79:
        drop(d, 360, 760, 130, 1, "happy"); diamond(d, 740, 760, 90, 1, "sus", t)
        tag(d, 360, 980, "能救命", 46, WHITE, GREEN, ease(pr(t, 75.6, 76))); tag(d, 740, 980, "不能吃", 46, WHITE, RED2, ease(pr(t, 76.8, 77.2)))
    elif t < 83:
        r = random.Random(3)
        for i in range(40):
            k = ease(pr(t, 79.1 + i * 0.05, 79.4 + i * 0.05)); x = 230 + (i % 8) * 88; y = 1150 - (i // 8) * 110
            if k > 0: drop(d, x, y, 34 * k, 1, "sus")
        tag(d, 540, 420, "水太多了：多一杯也不稀罕", 46, a=ease(pr(t, 79.5, 80)))
    elif t < 87:
        diamond(d, 540, 760, 170, 1, "happy", t); glow(d, 540, 760, 360, (255, 255, 255), 0.4)
        tag(d, 540, 1040, "太少了：每一颗都像第一口", 46, a=ease(pr(t, 83.2, 83.7)))
    else:
        k = ease(pr(t, 87.2, 88)); d.line([(300, 640), (780, 640)], A(DARKT, 1), 10); d.rect(525, 640, 555, 1000, fill=A(DARKT, 1))
        for i in range(10): drop(d, 260 + (i % 5) * 40, 600 - (i // 5) * 50, 20, 1, "sus")
        d.rect(480, 1000, 600, 1030, fill=A(DARKT, 1), r=8)
        drop(d, 300, 760, 50, k, "sus"); tag(d, 300, 880, "最后一杯水 ≈ 0", 38, a=k)
        diamond(d, 780, 760, 60, k, "happy", t); tag(d, 780, 880, "一颗钻石 = 很多", 38, a=k)
        verdict(d, t, 91.5, "越少越值钱", (40, 110, 210), 1100, 92)
def s_c4(t, d):
    grad(d, (255, 90, 60), (255, 170, 80)); rays(d, t, 540, 800, WHITE, 0.1)
    if t < 97.5:
        q = pop(t, 94.1, 0.3); d.text(540, 720, "11.11", int(220 * (0.8 + 0.2 * q)), A(WHITE, cl(q * 3)), k=1)
        for i in range(6): parcel(d, 240 + i * 120, 1050 - 20 * math.sin(t * 5 + i), 46, ease(pr(t, 95 + i * 0.25, 95.3 + i * 0.25)))
        return
    n = 1 if t < 101 else (3 if t < 105 else 5); joy = {1: "happy", 3: "sus", 5: "angry"}[n]
    for i in range(n): parcel(d, 250 + (i % 5) * 145, 1060 - (i // 5) * 100, 58, 1, 1.0 if i < max(1, n - 2) else 0.0)
    jump = 60 * abs(math.sin(t * 7)) if n == 1 else 0
    person(d, 540, 680 - jump, 120, 1, joy)
    if n == 1: glow(d, 540, 680, 280, (255, 240, 120), 0.8); headline(d, "开心到跳起来！", t, 97.6, RED2, WHITE, 400, 70)
    elif n == 3: headline(d, "拆完扔一边", t, 101.1, DARKT, WHITE, 400, 70)
    else: headline(d, "拆都没拆", t, 105.1, DARKT, WHITE, 400, 70)
    verdict(d, t, 108.7, "越买越不开心", RED2, 900, 84)
def s_c5(t, d):
    grad(d, (40, 150, 90), (140, 220, 120))
    if t < 113.5:
        q = pop(t, CLIMAX, 0.35); ticket(d, 540, 760, 230 * (0.7 + 0.3 * q), cl(q * 3))
        r = random.Random(1)
        for i in range(24):
            x = r.uniform(200, 880); y = (r.uniform(0, 1300) + (t - 110) * 400) % 1300 + 300
            d.rect(x - 34, y - 18, x + 34, y + 18, fill=A((120, 210, 120), 0.9), r=6); d.text(x, y, "$", 26, A((30, 100, 40), 1), k=1)
        headline(d, "中彩票，会更快乐吗？", t, 110.2, WHITE, DARKT, 400, 64)
    elif t < 120.5:
        for i in range(22):
            k = back(pr(t, 113.6 + i * 0.08, 113.9 + i * 0.08)); x = 240 + (i % 6) * 120; y = 620 + (i // 6) * 150
            if k > 0: person(d, x, y, 40 * cl(k), 1, "happy", GOLD)
        tag(d, 540, 400, "22 个中大奖的人", 52, WHITE, RED2, ease(pr(t, 113.6, 114)))
        if t > 117: tag(d, 540, 490, "每人至少赢了 5 万美元", 46, DARKT, GOLD, ease(pr(t, 117.1, 117.5)))
    elif t < 124:
        for side, x0, col, kind in ((0, 330, GOLD, "happy"), (1, 750, (120, 160, 255), "sus")):
            for i in range(6): person(d, x0 - 120 + (i % 3) * 120, 680 + (i // 3) * 170, 44, 1, kind, col)
        tag(d, 330, 1040, "中奖的人", 44, DARKT, GOLD); tag(d, 750, 1040, "普通人", 44, WHITE, BLUE)
        headline(d, "谁更快乐？", t, 120.6, DARKT, WHITE, 420, 72)
    elif t < 127.5: bars2(d, t, 124.1, "现在有多快乐？（满分5）", 4.00, 3.82, "中奖的人", "普通人")
    elif t < 131.5: bars2(d, t, 127.8, "日常小事有多开心？（满分5）", 3.33, 3.82, "中奖的人", "普通人")
    elif t < 135:
        d.circ(400, 760, 200, fill=A(GOLD, 1)); d.text(400, 760, "大快乐", 64, A(DARKT, 1), k=1)
        for i, s in enumerate(["吃饭", "聊天", "晒太阳"]):
            k = 1 - 0.6 * ease(pr(t, 132 + i * 0.4, 133 + i * 0.4)); d.circ(720, 560 + i * 200, 90 * k, fill=A(WHITE, 1)); d.text(720, 560 + i * 200, s, int(44 * k), A(DARKT, 1), k=1)
    else:
        ticket(d, 540, 640, 150, 0.6); verdict(d, t, 135.3, "快乐会变淡", (30, 120, 60), 1000, 92)
def s_out(t, d):
    grad(d, (255, 160, 140), (180, 120, 200))
    if t < 145:
        a1 = ease(pr(t, 137.2, 137.7)); cup(d, 540, 760, 160, 1, "sus" if t < 141 else "happy", 0.5, t)
        headline(d, "不是你变心了" if t < 141 else "是快乐本来就会变淡", t, 137.1 if t < 141 else 141.1, DARKT, WHITE, 400, 66)
    else:
        for i in range(5):
            k = ease(pr(t, 145.2 + i * 0.4, 145.6 + i * 0.4)); x = 260 + i * 140
            cup(d, x, 760, 55, k, "happy", 1, t); d.text(x, 900, ["周一", "周三", "周五", "下周", "下下周"][i], 32, A(DARKT, k), k=1)
        headline(d, "好东西，慢慢享受", t, 145.1, RED2, WHITE, 400, 72)
def s_end(t, d):
    grad(d, (60, 50, 110), (100, 80, 150))
    k = ease(pr(t, END, END + 0.5)); d.text(540, 380, "资料来源", 54, A(GOLD, k), k=1)
    src = ["Gossen 1854：边际效用递减最早表述", "Small et al. 2001, Brain 124:1720", "Adam Smith 1776《国富论》水与钻石", "Brickman et al. 1978, JPSP 36:917"]
    for i, s in enumerate(src): d.text(540, 500 + i * 80, s, 32, A(WHITE, ease(pr(t, END + 0.2 + i * 0.15, END + 0.6 + i * 0.15))), k=0)
    cup(d, 540, 1050, 80, k, "happy", 0.3, t)

SECS = [(HOOK, C1, s_hook), (C1, C2, s_c1), (C2, C3, s_c2), (C3, C4, s_c3), (C4, C5, s_c4), (C5, OUT, s_c5), (OUT, END, s_out), (END, 999, s_end)]
CUTS = [a for a, b, f in SECS[1:]] + [3.0, 6.5, 12.5, 31, 35, 43, 50.5, 75.5, 79, 83, 87, 97.5, 101, 105, 113.5, 120.5, 124, 127.5, 131.5, 135, 141, 145]
BIGS = [HIT0, ROS, CLIMAX]; SMALL = VERDICTS + [TOILET, NEWSHIT, REVEAL, 16.5, 20, 23.5]
def cam(t):
    z = 1.0 + 0.10 * pulse(t, BIGS, 3) + 0.05 * pulse(t, SMALL, 6)
    k = max([c for c in CUTS + [0] if c <= t]); z += 0.035 * min(1, (t - k) / 3.5)
    sx, sy = shake(t, 24 * pulse(t, BIGS, 4) + 8 * pulse(t, SMALL, 6), 61)
    return z, 540 + sx, 860 + sy
def top(t, d):
    d.rect(190, 150, 430, 196, fill=A(WHITE, 0.95), r=23); d.text(310, 173, "Vibe 知识大赏", 25, A(INKC, 1), k=1)
    d.rect(560, 150, 890, 196, fill=A(RED2, 0.95), r=23); d.text(725, 173, "为什么第一口最好喝", 25, A(WHITE, 1), k=1)
    if 10 <= t < END:
        cur = max(i for i, (ts, s) in enumerate(CHAP) if t >= ts)
        for i, (ts, s) in enumerate(CHAP):
            x = 190 + i * 142; on = i == cur; done = i < cur
            d.rect(x, 218, x + 132, 268, fill=A(RED2 if on else ((255, 255, 255) if done else (20, 20, 30)), 0.95 if on or done else 0.35), r=18)
            d.text(x + 66, 243, s, 28, A(WHITE if on else (DARKT if done else WHITE), 1), k=1)
def subs(t, d):
    for a, b, s in LINES:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.12)) * (1 - pr(t, b - 0.08, b))
            ls = wrap2(d, s, 56, 680); n = len(ls); y0 = 1350 - (n - 1) * 74
            w = max(d.tlen(x, 56, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 48, 540 + w / 2, y0 + (n - 1) * 74 + 48, fill=A((15, 12, 22), 0.82 * al), r=22)
            for i, x in enumerate(ls): d.text(540, y0 + i * 74, x, 56, A((255, 230, 120) if "结论" in s else WHITE, al), k=1)
            break
def frame(t):
    img = Image.new("RGB", (W, H), (30, 30, 50)); d = D(img)
    for a, b, sf in SECS:
        if a <= t < b: sf(t, d); break
    z, cx, cy = cam(t); cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.08: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.45 * (1 - (t - c) / 0.08)))
    top(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):06.1f}.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        last = None; errs = 0
        for i in range(i0, i1):
            try: last = frame(i / FPS).tobytes()
            except Exception as e: errs += 1; print('ERR', i, e, file=sys.stderr)
            if last: p.stdin.write(last)
        p.stdin.close(); p.wait(); print('errs', errs, file=sys.stderr)
