# v2 《FBI 查了79年UFO，查到外星人了吗？》 9:16, 154 s. Safe zone x 180–900, y < 1440. Bright chapter backgrounds, five cases, scoreboard.
import sys, subprocess, math, random
from film import (D, A, P, W, H, OW, OH, FPS, Image, cl, ease, eio, back, pr, lerp, mix, pulse, pop, shake, glow, ptri, tri_pts, tri,
                  saucer, face, agent, paper, typed, stamp, redact, balloon, plane, wrap2, STARS, WHITE, INKC, RED2, CY, GOLD, SILVER,
                  SILVER_D, PAPERC, PAPER_D, SUIT, SKIN, MUTE)
from cues2 import *

ARMY = (86, 110, 64); DARKT = (34, 30, 40)
def grad(d, top, bot, y0=0, y1=1920, n=24):
    h = (y1 - y0) / n
    for i in range(n): d.rect(0, y0 + i * h, 1080, y0 + (i + 1) * h + 1, fill=A(mix(top, bot, i / (n - 1)), 1))
def stars(d, t, a=1.0, hide=None, ymax=1300):
    for x, y, r, ph in STARS:
        if y > ymax or (hide and hide(x, y)): continue
        d.circ(x, y, r, fill=A(WHITE, a * (0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * 2.2 + ph)))))
def rays(d, t, cx, cy, col, a=0.18, n=16):
    for i in range(n):
        a0 = i * 2 * math.pi / n + t * 0.15; a1 = a0 + math.pi / n
        d.poly([(cx, cy), (cx + 2000 * math.cos(a0), cy + 2000 * math.sin(a0)), (cx + 2000 * math.cos(a1), cy + 2000 * math.sin(a1))], A(col, a))
def hills(d, y, col, seed=3, amp=90):
    r = random.Random(seed); pts = [(0, 1920)]
    for i in range(13): pts.append((i * 90, y - r.uniform(0.2, 1) * amp))
    pts += [(1080, y - amp * 0.5), (1080, 1920)]; d.poly(pts, A(col, 1))
def bg_hook(d, t): grad(d, (40, 50, 120), (130, 70, 150)); stars(d, t, 0.8); rays(d, t, 540, 700, (255, 255, 255), 0.05)
def bg_desert(d, t):
    grad(d, (255, 150, 80), (255, 214, 150)); d.circ(800, 420, 90, fill=A((255, 240, 190), 1)); glow(d, 800, 420, 200, (255, 240, 190), 0.6)
    hills(d, 1180, (214, 140, 80), 5, 120); hills(d, 1300, (180, 110, 60), 8, 70)
def bg_office(d, t):
    grad(d, (60, 120, 140), (110, 170, 170))
    for i in range(4): d.rect(120 + i * 230, 1000, 300 + i * 230, 1440, fill=A((70, 90, 110), 1), r=10); [d.rect(140 + i * 230, 1030 + j * 130, 280 + i * 230, 1130 + j * 130, fill=A((95, 118, 138), 1), r=6) for j in range(3)]
    d.rect(0, 1240, 1080, 1920, fill=A((150, 110, 80), 1))
def bg_comic(d, t, col=(255, 205, 60)): grad(d, col, mix(col, (255, 150, 60), 0.6)); rays(d, t, 540, 760, WHITE, 0.16)
def bg_alert(d, t):
    grad(d, (210, 60, 60), (150, 30, 50))
    for i in range(-4, 14): d.poly([(i * 110, 0), (i * 110 + 50, 0), (i * 110 - 450, 1920), (i * 110 - 500, 1920)], A((255, 255, 255), 0.05))
def bg_purple(d, t): grad(d, (70, 40, 130), (170, 90, 170)); stars(d, t, 0.6)
def bg_night(d, t, hide=None): grad(d, (20, 40, 100), (60, 90, 160)); stars(d, t, 1.0, hide)
def bg_teal(d, t):
    grad(d, (16, 90, 110), (40, 150, 140))
    for i in range(12): d.line([(0, 300 + i * 100), (1080, 300 + i * 100)], A(WHITE, 0.05), 2)
    for i in range(12): d.line([(i * 100, 0), (i * 100, 1920)], A(WHITE, 0.05), 2)
def bg_paper(d, t): grad(d, (250, 236, 200), (236, 210, 160))

def headline(d, s, t, t0, col=WHITE, bgc=DARKT, y=400, size=72):
    k = pop(t, t0, 0.3); a = cl(k * 3)
    w = d.tlen(s, size, 1) + size * 0.9; w = min(w, 720)
    d.rect(540 - w / 2, y - size * 0.8, 540 + w / 2, y + size * 0.8, fill=A(bgc, 0.92 * a), r=size * 0.4)
    d.text(540, y, s, max(2, int(size * (0.8 + 0.2 * k))), A(col, a), k=1)
def tag(d, x, y, s, size=38, col=DARKT, bgc=WHITE, a=1.0):
    w = d.tlen(s, size, 1) + size * 0.8; x = cl(x, 190 + w / 2, 890 - w / 2)
    d.rect(x - w / 2, y - size * 0.7, x + w / 2, y + size * 0.7, fill=A(bgc, 0.95 * a), r=size * 0.35); d.text(x, y, s, size, A(col, a), k=1)
def bubble(d, x, y, s, size=40, a=1.0, tail=-1):
    w = d.tlen(s, size, 1) + size * 1.0; h = size * 1.7; x = cl(x, 190 + w / 2, 890 - w / 2)
    d.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=A(WHITE, a), r=h * 0.4)
    d.poly([(x + tail * w * 0.2, y + h / 2 - 2), (x + tail * w * 0.2 + 30 * tail, y + h / 2 - 2), (x + tail * w * 0.3, y + h / 2 + 34)], A(WHITE, a))
    d.text(x, y, s, size, A(DARKT, a), k=1)
def verdict(d, t, t0, s, col=RED2, y=1060, size=96):
    q = pop(t, t0, 0.3); a = cl(q * 3)
    if a <= 0: return
    d.rect(200, y - 120, 880, y + 120, fill=A((255, 255, 255), a), r=30)
    d.text(540, y - 62, "结论", 44, A(DARKT, a), k=1)
    sz = size * (1.5 - 0.5 * q); d.text(540, y + 30, s, max(2, int(sz)), A(col, a), k=1)
def casecard(d, t, t0, n, title, sub):
    k = ease(pr(t, t0, t0 + 0.35)); a = k
    d.rect(200, 560, 880, 1000, fill=A(DARKT, 0.9 * a), r=40)
    d.text(540, 660, f"第 {n} 案", 70, A(GOLD, a), k=1); d.text(540, 790, title, 84, A(WHITE, a), k=1); d.text(540, 910, sub, 46, A((200, 200, 220), a), k=1)
def hoover(d, x, y, s, a=1.0, kind="sus"): agent(d, x, y, s, a, kind, glasses=False); tag(d, x, y + s * 1.9, "FBI局长 胡佛", 30, a=a)
def army(d, x, y, s, a=1.0, kind="happy"): agent(d, x, y, s, a, kind, glasses=False, cap=ARMY, tie=ARMY); tag(d, x, y + s * 1.9, "军方", 30, a=a)

# ---------------- scenes ----------------
def s_hook(t, d):
    bg_hook(d, t)
    if t < 3:
        q = pop(t, HIT0, 0.3); d.text(540, 520, "79年", int(260 * (0.7 + 0.3 * q)), A(GOLD, cl(q * 3)), k=1)
        tag(d, 540, 700, "FBI 的 UFO 档案", 50, WHITE, RED2)
        for i in range(8):
            k = ease(pr(t, 0.3 + i * 0.12, 0.6 + i * 0.12)); x = 230 + (i % 4) * 205; y = 900 + (i // 4) * 190
            paper(d, x - 70, y - 80, x + 70, y + 80, k); redact(d, x - 50, y - 20, x + 50, 18, k); redact(d, x - 50, y + 20, x + 20, 18, k)
    elif t < 6.5:
        saucer(d, 540, 760, 200, t, 1, "shock", math.sin(t * 3))
        agent(d, 300, 1080, 80, 1, "shock"); agent(d, 780, 1080, 80, 1, "sus")
        headline(d, "查到外星人了吗？", t, 3.1, GOLD, DARKT, 380, 78)
    else:
        labels = ["气球?", "玩具?", "传闻?", "未解?", "未解?"]
        for i in range(5):
            k = back(pr(t, 6.7 + i * 0.4, 7.0 + i * 0.4)); x = 270 + (i % 3) * 270 if i < 3 else 405 + (i - 3) * 270; y = 640 if i < 3 else 960
            if k > 0:
                d.rect(x - 105, y - 135, x + 105, y + 135, fill=A(PAPERC, 1), r=16); d.text(x, y - 60, f"案{i + 1}", 52, A(RED2, 1), k=1)
                d.text(x, y + 40, "?", 110, A(DARKT, 1), k=1)
def s_c1(t, d):
    bg_desert(d, t)
    if t < 12.5: casecard(d, t, C1, 1, "罗斯威尔", "1947 年 · 美国新墨西哥州")
    elif t < 16.5:
        army(d, 330, 900, 110, 1, "happy"); bubble(d, 420, 620, "我们捡到飞碟啦！", 46, 1, -1)
        saucer(d, 760, 900 + 15 * math.sin(t * 4), 120, t, 1, "happy")
        q = pop(t, ROS, 0.3); tag(d, 540, 380, "1947年7月8日", 54, WHITE, RED2, cl(q * 3))
    else:
        paper(d, 210, 300, 870, 660); typed(d, 250, 370, "FBI 电报 · 加急", 44, 1, 1, RED2, 1)
        typed(d, 250, 450, "“飞碟”是六角形的", 44, 1, pr(t, 16.8, 17.6), DARKT, 1); typed(d, 250, 530, "用缆绳挂在气球下面", 44, 1, pr(t, 17.6, 18.5), DARKT, 1)
        hx, hy, hr = balloon(d, 540, lerp(1500, 800, ease(pr(t, 16.6, 17.6))), 100)
        if t > 20:
            k = ease(pr(t, 20, 20.4)); tag(d, 760, 800, "气球", 42, a=k); tag(d, 790, hy, "铁皮反光板", 38, a=k)
        if t > 24:
            k = ease(pr(t, 24, 24.4)); army(d, 280, 1000, 80, k, "sus"); bubble(d, 330, 820, "其实……是气象气球", 38, k, -1)
        verdict(d, t, V1, "气 球", (40, 120, 210))
def s_hoov(t, d):
    bg_office(d, t)
    army(d, 300, 760, 110, 1, "happy" if t < 37 else "angry"); hoover(d, 780, 760, 110, 1, "sus" if t < 37 else "angry")
    if t < 33.5: bubble(d, 360, 500, "帮我们查飞碟吧？", 44, ease(pr(t, 30.2, 30.6)), -1)
    elif t < 37: bubble(d, 720, 500, "行，但飞碟得给我看", 44, ease(pr(t, 33.6, 34)), 1)
    else:
        bubble(d, 700, 500, "上次你们抢走了！", 46, 1, 1)
        u = ease(pr(t, 37.3, 38.3)); saucer(d, lerp(560, 230, u), 620, 60, t, 1, "scared", -1)
        tag(d, 540, 380, "看都不让看", 50, WHITE, RED2, ease(pr(t, 37.5, 37.8)))
def s_c2(t, d):
    if t < 54: bg_comic(d, t)
    else: bg_comic(d, t, (120, 200, 255))
    if t < 43: casecard(d, t, C2, 2, "捡到“飞碟”", "1947 年 · 美国各地")
    elif t < 54:
        r = 230; cx, cy = 540, 760
        if t < 47:
            d.circ(cx, cy, r, fill=A((190, 194, 204), 1)); d.circ(cx, cy, r * 0.9, fill=A((214, 218, 228), 1)); d.ell(470, 690, 60, 30, A(WHITE, 0.6))
            headline(d, "打开一看……", t, 43.1, DARKT, WHITE, 400, 64); tag(d, 540, 1080, "纸板 + 银漆", 54, WHITE, DARKT)
        else:
            d.circ(cx, cy, r, fill=A((190, 194, 204), 1)); d.circ(cx, cy, r * 0.78, fill=A((150, 110, 70), 1))
            d.rect(420, 660, 560, 760, fill=A((80, 120, 200), 1), r=12); d.text(490, 710, "电机", 34, A(WHITE, 1), k=1)
            ang = t * 25; d.line([(600 + 80 * math.cos(ang), 820 + 26 * math.sin(ang)), (600 - 80 * math.cos(ang), 820 - 26 * math.sin(ang))], A(RED2, 1), 14)
            d.circ(600, 820, 14, fill=A(DARKT, 1)); tag(d, 600, 900, "螺旋桨", 36)
            agent(d, 820, 1040, 60, 1, "happy", glasses=False, cap=RED2, tie=CY); tag(d, 820, 1170, "小孩", 32)
            verdict(d, t, TOY, "小孩的玩具", (230, 120, 20), 1060, 88)
    elif t < 58:
        u = pr(t, 54, 56.5); px = lerp(1100, 560, u); py = lerp(450, 820, u ** 2); plane(d, px, py, 150, 1, (150, 150, 160))
        if t > 56.5: glow(d, 560, 860, 260, (255, 120, 40), 1 - pr(t, 56.5, 58) * 0.5)
        if t > 56.6: bubble(d, 540, 420, "飞机上有飞碟碎片！", 46, ease(pr(t, 56.6, 57)), 1)
    else:
        for i in range(7): d.poly([(380 + i * 50, 880 - (i % 3) * 20), (420 + i * 50, 840), (450 + i * 50, 890)], A((90, 84, 80), 1))
        paper(d, 260, 380, 820, 640); d.text(540, 450, "化验结果", 46, A(DARKT, 1), k=1); d.text(540, 560, "工厂炉渣", 80, A(RED2, ease(pr(t, 58.4, 58.8))), k=1)
        verdict(d, t, SLAG, "恶作剧 / 谣言", (230, 120, 20), 1080, 84)
def s_quit(t, d):
    bg_alert(d, t)
    if t < 66:
        paper(d, 220, 330, 860, 760); typed(d, 260, 400, "军方内部文件", 46, 1, 1, RED2, 1)
        d.text(540, 520, "让FBI去捡的是：", 50, A(DARKT, ease(pr(t, 62.5, 63))), k=1)
        d.text(540, 640, "？？？", 90, A(RED2, ease(pr(t, 63.5, 64))), k=1); hoover(d, 540, 960, 80, 1, "sus")
    elif t < 69:
        k = cl(pop(t, TOILET, 0.3) * 3)
        for i, (xx, kind) in enumerate(((350, 0), (730, 1))):
            yy = 740 + 30 * math.sin(t * 6 + i)
            if kind == 0: d.ell(xx, yy, 140, 95, outline=A(WHITE, k), w=36); d.ell(xx, yy - 115, 130, 36, A((240, 240, 246), k))
            else: d.ell(xx, yy, 140, 48, A((170, 176, 188), k)); d.rect(xx - 30, yy - 70, xx + 30, yy - 36, fill=A((170, 176, 188), k), r=8)
        tag(d, 350, 950, "马桶盖", 56, a=k); tag(d, 730, 950, "垃圾桶盖", 56, a=k)
        headline(d, "就这？", t, 66.4, RED2, WHITE, 420, 90)
    else:
        hoover(d, 540, 640, 150, 1, "angry"); verdict(d, t, 70.0, "FBI 不查了！", RED2, 1060, 90)
def s_c3(t, d):
    bg_purple(d, t)
    if t < 75.5: casecard(d, t, C3, 3, "神秘文件", "1950 年 3 月 22 日")
    elif t < 83:
        for i in range(3):
            x = 300 + i * 240; k = ease(pr(t, 75.6 + i * 0.3, 76 + i * 0.3)); saucer(d, x, 560, 100, t, k, "scared" if t > 79 else "sus")
            if t > 79:
                for j in range(3):
                    kk = back(pr(t, 79.2 + i * 0.3 + j * 0.1, 79.5 + i * 0.3 + j * 0.1)); bx = x - 55 + j * 55
                    d.rect(bx - 18, 820, bx + 18, 910, fill=A((190, 230, 200), cl(kk)), r=12); d.circ(bx, 790, 26, fill=A((200, 240, 210), cl(kk)))
                    face(d, bx, 790, 22, "shock", cl(kk))
        tag(d, 540, 380, "3 个飞碟", 60, WHITE, RED2, ease(pr(t, 75.6, 76)))
        if t > 79: tag(d, 540, 1020, "每个 3 人 · 约 90 厘米高", 46, a=ease(pr(t, 79.5, 80)))
    elif t < 87:
        d.rect(220, 420, 860, 960, fill=A(WHITE, 0.95), r=30); d.text(540, 520, "FBI 网站", 52, A(DARKT, 1), k=1)
        q = pop(t, 83.4, 0.3); d.text(540, 700, "看的人最多", int(96 * (0.8 + 0.2 * q)), A(RED2, cl(q * 3)), k=1)
        d.text(540, 860, "No.1", 90, A(GOLD, cl(q * 3)), k=1)
    else:
        agent(d, 540, 620, 130, 1, "sus"); tag(d, 540, 880, "FBI", 40)
        bubble(d, 540, 390, "听别人转述的，没查过", 44, ease(pr(t, 87.2, 87.6)), 1)
        verdict(d, t, 91.5, "传 闻", (150, 80, 200), 1080)
def s_c4(t, d):
    tx = lerp(-300, 1400, pr(t, 98.5, 106)); pts = tri_pts(tx, 560, 420, math.pi / 2)
    hide = (lambda x, y: ptri(x, y, *pts)) if t >= 98.5 else None
    bg_night(d, t, hide)
    if t >= 98.5: d.poly(pts, A((10, 14, 30), 0.85))
    hills(d, 1160, (20, 30, 60), 21, 70)
    if t < 97.5: casecard(d, t, C4, 4, "星星消失了", "2002 年 · 阿富汗美军基地")
    else:
        for x in (420, 640): agent(d, x, 1060, 70, 1, "shock" if t > 98.8 else "sus", glasses=False, cap=ARMY, tie=ARMY)
        tag(d, 530, 1220, "美军飞行员", 34)
        if t > 101: tag(d, 540, 360, "巨大三角形 · 没声音", 52, WHITE, DARKT, ease(pr(t, 101, 101.4)))
        if t > 105 and t < 108.5: d.text(540, 860, "约150米", 120, A(GOLD, ease(pr(t, 105, 105.4))), k=1)
        verdict(d, t, 108.7, "未 解", RED2, 860)
def thermal(d, t, tx, ty, s):
    d.rect(190, 330, 890, 1020, fill=A((40, 16, 70), 1), r=24)
    for i in range(10): d.rect(190, 330 + i * 69, 890, 330 + (i + 1) * 69, fill=A(mix((40, 16, 70), (90, 30, 100), i / 9), 1))
    glow(d, tx, ty, s * 1.4, (255, 150, 40), 1); d.poly(tri_pts(tx, ty, s, -0.1), A((255, 210, 90), 1))
    d.text(230, 380, "热像仪", 36, A(WHITE, 1), anchor="lm", k=1); d.circ(850, 380, 12, fill=A(RED2, 0.5 + 0.5 * math.sin(t * 8)))
def s_c5(t, d):
    bg_teal(d, t)
    if t < 113.5: casecard(d, t, C5, 5, "黑色三角形", "2026 年 6 月 · 美国西部")
    elif t < 117:
        hills(d, 1000, (20, 70, 80), 31, 120); tri(d, 540, 560, 150, 1, -0.05)
        for i, x in enumerate((330, 540, 750)): agent(d, x, 960, 70, 1, "shock")
        tag(d, 540, 1150, "3 名 FBI 特工", 44, WHITE, DARKT)
    elif t < 120.5:
        thermal(d, t, 540, 620, 150)
        tag(d, 380, 900, "是热的 ✓".replace(" ✓", ""), 46, DARKT, GOLD, ease(pr(t, 117.5, 117.9))); tag(d, 700, 900, "没尾气", 46, DARKT, CY, ease(pr(t, 118.5, 118.9)))
    elif t < 124:
        hills(d, 1000, (20, 70, 80), 31, 120)
        u1 = ease(pr(t, 120.6, 122)); u2 = pr(t, 122.2, 123); x = lerp(540, -500, u2 ** 2); y = lerp(900, 520, u1)
        tri(d, x, y, 110, 1, -0.05)
        if t < 122.2: d.line([(540, 940), (540, 980)], A(WHITE, 0.0), 1); tag(d, 760, 700, "↑ 往上", 44, a=ease(pr(t, 120.8, 121.1)))
        else: tag(d, 540, 700, "← 突然平飞", 44, a=1)
        d.rect(330, 1080, 750, 1200, fill=A(DARKT, 0.8), r=20); d.text(540, 1140, "声音：0", 50, A((120, 255, 160), 1), k=1)
    elif t < 127.5:
        q = pop(t, NEWSHIT, 0.3); a = cl(q * 3)
        d.rect(200, 400, 880, 900, fill=A(WHITE, a), r=24); d.rect(200, 400, 880, 490, fill=A(RED2, a), r=24); d.text(540, 445, "新闻", 46, A(WHITE, a), k=1)
        d.text(540, 620, "3秒 飞了", 96, A(DARKT, a), k=1); d.text(540, 770, "2.4公里！", 116, A(RED2, a), k=1)
        tri(d, 540, 1080, 90, 1)
    elif t < 131.5:
        d.rect(190, 330, 890, 1080, fill=A(PAPERC, 1), r=24); d.text(540, 400, "FBI 报告原文", 48, A(DARKT, 1), k=1)
        k1 = ease(pr(t, 127.8, 128.3)); k2 = ease(pr(t, 129.3, 129.8))
        d.rect(230, 470, 850, 720, fill=A((255, 225, 90), k1), r=20); d.text(540, 545, "一共只看了", 50, A(DARKT, k1), k=1); d.text(540, 650, "3 秒", 96, A(RED2, k1), k=1)
        d.rect(230, 770, 850, 1040, fill=A((150, 220, 255), k2), r=20); d.text(540, 845, "消失时 离他们", 50, A(DARKT, k2), k=1); d.text(540, 955, "2.4 公里", 96, A((20, 80, 170), k2), k=1)
    elif t < 135:
        hills(d, 1100, (20, 70, 80), 31, 80); ox, oy, vx, vy = 330, 1040, 780, 520
        agent(d, ox, oy, 55, 1, "sus"); d.line([(ox, oy - 40), (vx, vy)], A(CY, 1), 6); tag(d, 610, 760, "2.4公里 = 距离", 40, a=1)
        for i in range(3):
            sx, sy = [(560, 820), (420, 520), (860, 720)][i]; kk = ease(pr(t, 132 + i * 0.4, 132.3 + i * 0.4))
            pts = [(lerp(sx, vx, j / 20) + math.sin(j * 0.6 + i) * 60, lerp(sy, vy, j / 20)) for j in range(21)]
            for j in range(0, 20, 2): d.line([pts[j], pts[j + 1]], A(GOLD, 0.8 * kk), 6)
        tri(d, vx, vy, 50, 1); headline(d, "飞了多远？不知道", t, 131.7, GOLD, DARKT, 400, 64)
    else:
        tri(d, 540, 600, 140, 1); verdict(d, t, 135.3, "未 解", RED2, 1000)
def s_out(t, d):
    grad(d, (60, 50, 130), (220, 120, 120)); stars(d, t, 0.5)
    if t < 145:
        items = [("气球", (40, 120, 210), 1), ("恶作剧", (230, 120, 20), 2), ("传闻", (150, 80, 200), 1), ("未解", RED2, 2)]
        for i, (s, col, n) in enumerate(items):
            k = back(pr(t, 137.2 + i * 0.6, 137.5 + i * 0.6)); y = 450 + i * 170
            if k > 0:
                d.rect(230, y - 65, 850, y + 65, fill=A(WHITE, 0.95), r=30); d.text(300, y, f"{i + 1}", 50, A(col, 1), k=1)
                d.text(480, y, s, 64, A(col, 1), k=1); d.text(760, y, f"× {n}", 64, A(DARKT, 1), k=1)
        if t > 141: d.rect(220, 450 + 3 * 170 - 75, 860, 450 + 3 * 170 + 75, outline=A(GOLD, 0.6 + 0.4 * math.sin(t * 8)), w=10, r=34)
    else:
        tri(d, 540, 640, 170, 1, 0.05 * math.sin(t)); saucer(d, 740, 980, 70, t, 1, "sus", -1); agent(d, 360, 1000, 70, 1, "sus")
        headline(d, "你觉得是什么？", t, 145.2, GOLD, DARKT, 380, 76)
        tag(d, 540, 1180, "评论区说说", 44, WHITE, RED2, ease(pr(t, 146, 146.4)))
def s_end(t, d):
    grad(d, (30, 40, 80), (60, 70, 120))
    k = ease(pr(t, END, END + 0.5)); d.text(540, 380, "资料来源", 54, A(GOLD, k), k=1)
    src = ["FBI Vault · UFO 档案（1947–1954）", "FBI 卷宗 62-HQ-83894", "FBI：UFOs and the Guy Hottel Memo（2013）", "美国国防部 PURSUE 解密档案（2026）", "FBI-UAP-D024 / D043（FD-302）", "新华社、Axios 2026.10.23–24"]
    for i, s in enumerate(src): d.text(540, 490 + i * 75, s, 29, A(WHITE, ease(pr(t, END + 0.2 + i * 0.12, END + 0.6 + i * 0.12))), k=0)
    saucer(d, 540, 1100, 70, t, k, "happy")

SECS = [(HOOK, C1, s_hook), (C1, HOOV, s_c1), (HOOV, C2, s_hoov), (C2, QUIT, s_c2), (QUIT, C3, s_quit), (C3, C4, s_c3), (C4, C5, s_c4), (C5, OUT, s_c5), (OUT, END, s_out), (END, 999, s_end)]
CUTS = [a for a, b, f in SECS[1:]] + [3.0, 6.5, 12.5, 16.5, 43, 47, 54, 58, 66, 69, 75.5, 83, 87, 97.5, 113.5, 117, 120.5, 124, 127.5, 131.5, 135, 145]
BIGS = [HIT0, ROS, CLIMAX]; SMALL = VERDICTS + [TOILET, NEWSHIT, REVEAL] + CASES
def cam(t):
    z = 1.0 + 0.10 * pulse(t, BIGS, 3) + 0.05 * pulse(t, SMALL, 6)
    for a, b in zip([0] + CUTS, CUTS + [DUR]):
        pass
    k = 0
    for c in sorted(CUTS + [0]):
        if c <= t: k = c
    z += 0.035 * min(1, (t - k) / 3.5)
    amp = 24 * pulse(t, BIGS, 4) + 8 * pulse(t, SMALL, 6)
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx, 860 + sy
def top(t, d):
    d.rect(190, 150, 430, 196, fill=A(WHITE, 0.95), r=23); d.text(310, 173, "Vibe 知识大赏", 25, A(INKC, 1), k=1)
    d.rect(620, 150, 890, 196, fill=A(RED2, 0.95), r=23); d.text(755, 173, "FBI 的 UFO 档案", 25, A(WHITE, 1), k=1)
    if 6.5 <= t < END:
        cnt = [0, 0, 0, 0]; hits = []
        for ts, kk in SCORE:
            if t >= ts: cnt[kk] += 1; hits.append((ts, kk))
        cols = [(40, 120, 210), (230, 120, 20), (150, 80, 200), RED2]
        for i in range(4):
            x = 190 + i * 177.5; w = 165; bump = max([math.exp(-(t - ts) * 5) for ts, kk in hits if kk == i] + [0])
            d.rect(x, 218, x + w, 270, fill=A(cols[i], 0.95), r=18)
            d.text(x + w / 2, 244, f"{KEYS[i]} {cnt[i]}", int(28 * (1 + 0.35 * bump)), A(WHITE, 1), k=1)
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
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
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
