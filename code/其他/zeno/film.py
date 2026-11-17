import sys, subprocess
from fx import *
from cues import *

NAVY = (16, 20, 38); NAVY2 = (30, 38, 72); ACH = (238, 100, 62); ACH_L = (255, 160, 120); ACH_D = (180, 62, 40)
GOLD = (250, 196, 70); GOLD_L = (255, 232, 150); PLUME = (220, 48, 60)
SH = (84, 168, 98); SH_L = (140, 214, 130); SH_D = (52, 118, 70); SKIN = (176, 214, 120); SKIN_D = (130, 170, 84)
TRACK = (196, 86, 64); TRACK_D = (150, 60, 46); LANE = (250, 230, 220)
STONE = (226, 214, 186); STONE_D = (178, 164, 136); ZEN = (126, 110, 170); BEARD = (240, 240, 236)
PINKBG = (64, 30, 54); CAKEC = (250, 220, 170); CREAM = (255, 244, 236); BERRY = (236, 70, 100)
PIECES = [(255, 120, 120), (255, 190, 90), (250, 236, 110), (130, 220, 130), (110, 200, 250), (160, 140, 255), (240, 130, 230), (255, 255, 255)]

def ach(d, x, y, s, t, run=1.0, mood="chill", lean=0.0, a=1.0, sweat=0.0):
    """Achilles: round runner with Greek helmet. (x,y) = feet."""
    ph = t * 16 * run
    by = y - s * 1.05 - abs(math.sin(ph)) * s * 0.08 * run
    d.ell(x, y, s * 0.6, s * 0.08, A((0, 0, 0), 0.25 * a))
    for k in (0, 1):  # legs
        sw = math.sin(ph + k * math.pi) * run
        hx, hy = x - s * 0.1 + k * s * 0.15, by + s * 0.55
        fx_, fy_ = hx + sw * s * 0.45, y - max(0, -math.cos(ph + k * math.pi)) * s * 0.2 * run
        col = ACH_D if k == 0 else ACH
        d.line([(hx, hy), ((hx + fx_) / 2 + s * 0.08, (hy + fy_) / 2), (fx_, fy_)], A(col, a), s * 0.17)
        d.ell(fx_ + s * 0.06, fy_ - s * 0.02, s * 0.14, s * 0.07, A(GOLD, a))
    arm = math.sin(ph) * run
    d.line([(x - s * 0.2, by + s * 0.15), (x - s * 0.2 - arm * s * 0.4, by + s * 0.45)], A(ACH_D, a), s * 0.13)
    bx = x + lean * s * 0.2
    d.ell(bx, by, s * 0.62, s * 0.68, A(ACH_D, a)); d.ell(bx - s * 0.04, by - s * 0.04, s * 0.58, s * 0.64, A(ACH, a))
    d.ell(bx - s * 0.25, by - s * 0.35, s * 0.18, s * 0.11, A(ACH_L, 0.6 * a))
    # helmet
    d.d.chord((P(bx - s * 0.6), P(by - s * 0.92), P(bx + s * 0.6), P(by + s * 0.1)), 180, 360, fill=A(GOLD, a))
    d.ell(bx - s * 0.22, by - s * 0.66, s * 0.16, s * 0.07, A(GOLD_L, 0.8 * a))
    for i in range(9):
        u = i / 8; px = bx - s * 0.55 + u * s * 1.0; py = by - s * 0.82 - math.sin(u * math.pi) * s * 0.42
        d.circ(px - run * s * 0.1 * u, py, s * 0.13, fill=A(PLUME if i % 2 else (245, 80, 80), a))
    face(d, bx + s * 0.12, by + s * 0.12, s * 0.62, mood, a, look=0.6)
    if sweat > 0:
        for i in range(2):
            u = (t * 2 + i * 0.5) % 1
            d.ell(bx - s * 0.6 - u * s * 0.3, by - s * 0.3 + u * s * 0.5, s * 0.06, s * 0.09, A(CYAN, sweat * a * (1 - u)))
    if run > 0.6:
        for i in range(4):
            yy = by - s * 0.3 + i * s * 0.22; L = s * (0.6 + 0.4 * math.sin(t * 9 + i))
            d.line([(x - s * 0.95 - L, yy), (x - s * 0.95, yy)], A(WHITE, 0.35 * a * run), s * 0.04)

def turtle(d, x, y, s, t, walk=1.0, mood="chill", a=1.0, spin=0.0):
    ph = t * 9 * walk
    d.ell(x, y, s * 0.95, s * 0.09, A((0, 0, 0), 0.25 * a))
    for k, lx in enumerate((-0.5, -0.15, 0.25, 0.55)):
        sw = math.sin(ph + k * 1.7) * walk * s * 0.08
        d.rect(x + lx * s - s * 0.1 + sw, y - s * 0.3, x + lx * s + s * 0.1 + sw, y, fill=A(SKIN_D if k % 2 else SKIN, a), r=s * 0.08)
    hx, hy = x + s * 0.95, y - s * 0.55 + math.sin(ph) * s * 0.03 * walk
    d.line([(x + s * 0.6, y - s * 0.32), (hx - s * 0.1, hy + s * 0.1)], A(SKIN, a), s * 0.26)
    d.ell(hx, hy, s * 0.36, s * 0.3, A(SKIN, a)); d.ell(hx - s * 0.1, hy - s * 0.12, s * 0.12, s * 0.06, A((220, 240, 180), 0.6 * a))
    d.line([(x - s * 0.85, y - s * 0.25), (x - s * 1.1, y - s * 0.18)], A(SKIN, a), s * 0.1)
    d.d.chord((P(x - s * 0.9), P(y - s * 1.25), P(x + s * 0.9), P(y + s * 0.05)), 180, 360, fill=A(SH_D, a))
    d.d.chord((P(x - s * 0.84), P(y - s * 1.2), P(x + s * 0.84), P(y - s * 0.02)), 180, 360, fill=A(SH, a))
    for cx, cy, r in ((0, -0.78, 0.2), (-0.45, -0.5, 0.17), (0.45, -0.5, 0.17), (-0.25, -0.33, 0.12), (0.25, -0.33, 0.12)):
        d.ell(x + cx * s, y + cy * s, r * s * 1.2, r * s, A(SH_L, 0.7 * a))
    d.ell(x - s * 0.3, y - s * 0.95, s * 0.2, s * 0.07, A(WHITE, 0.35 * a))
    d.rect(x - s * 0.9, y - s * 0.12, x + s * 0.9, y - s * 0.02, fill=A(SH_D, a), r=s * 0.04)
    face(d, hx + s * 0.04, hy, s * 0.42, mood, a, look=0.4)

def stars(d, t, a=1.0, n=60):
    for i in range(n):
        x = (i * 397) % 1080; y = (i * 211) % 1100
        tw = 0.5 + 0.5 * math.sin(t * 2 + i * 1.3)
        d.circ(x, y, 2 + i % 3, fill=A(WHITE, a * 0.6 * tw))
def stadium(d, t, lit=1.0):
    grad(d, NAVY, NAVY2); stars(d, t, 0.6)
    for x in (140, 940):
        d.rect(x - 8, 300, x + 8, 1150, fill=A((60, 70, 110), 1))
        glow(d, x, 300, 200, (255, 240, 200), 0.6 * lit); d.rect(x - 60, 270, x + 60, 320, fill=A((255, 250, 220), lit), r=10)
def track(d, y0, t, scroll, h=420):
    d.rect(-50, y0, OW + 50, y0 + h, fill=A(TRACK, 1))
    d.rect(-50, y0, OW + 50, y0 + 18, fill=A(ACH_L, 0.5))
    for i in range(3): d.rect(-50, y0 + 110 + i * 110, OW + 50, y0 + 118 + i * 110, fill=A(LANE, 0.8))
    for i in range(14):
        x = (i * 160 - scroll) % 2240 - 80; d.rect(x, y0 + 60, x + 60, y0 + 70, fill=A(TRACK_D, 1))

def s_hook(t, d):
    if t < HOOK_HIT: grad(d, NAVY, NAVY2)
    else: rays(d, t, (40, 50, 96), (26, 32, 64), cy=1000)
    stars(d, t, 0.4); track(d, 1180, t, t * 1500)
    sparks(d, 540, 700, t, HOOK_HIT, 50, 1300, GOLD, 1, 3)
    ach(d, 300, 1300, 200, t, 1.4, "scream" if t > HOOK_HIT else "scared", sweat=1)
    turtle(d, 790, 1300, 150, t, 0.6, "proud")
    # gap arrow
    d.line([(450, 1360), (660, 1360)], A(WHITE, 0.7), 6); d.poly([(660, 1340), (690, 1360), (660, 1380)], A(WHITE, 0.7))
    d.text(560, 1410, "永远差一点", 40, A(WHITE, 0.85), k=1)
    d.text(540, 380, "跑得最快的人", 92, A(WHITE, ease(pr(t, 0, 0.2))), k=1)
    stamp(d, t, HOOK_HIT, "永远追不上", 540, 560, 158, YEL)
    stamp(d, t, HOOK_HIT + 0.25, "乌龟？", 540, 780, 210, SH_L)
    glow(d, 540, 780, 300, SH_L, 0.4 * pulse(t, [HOOK_HIT + 0.25], 3))

def temple(d, t):
    grad(d, (26, 30, 60), (60, 50, 90)); stars(d, t, 0.5)
    glow(d, 540, 520, 420, (255, 200, 140), 0.35)
    d.poly([(120, 520), (540, 330), (960, 520)], A(STONE, 1)); d.poly([(200, 500), (540, 360), (880, 500)], A(STONE_D, 0.5))
    d.rect(120, 520, 960, 570, fill=A(STONE, 1))
    for i in range(6):
        x = 170 + i * 148; d.rect(x, 570, x + 74, 1180, fill=A(STONE, 1)); d.rect(x + 10, 570, x + 26, 1180, fill=A(WHITE, 0.35)); d.rect(x + 54, 570, x + 74, 1180, fill=A(STONE_D, 0.6))
    d.rect(80, 1180, 1000, 1240, fill=A(STONE_D, 1)); d.rect(40, 1240, 1040, 1300, fill=A(STONE, 1))
def zeno(d, x, y, s, t, mood="sus", a=1.0):
    bob = math.sin(t * 3) * s * 0.03
    d.ell(x, y, s * 0.7, s * 0.1, A((0, 0, 0), 0.25 * a))
    d.d.chord((P(x - s * 0.75), P(y - s * 1.6 + bob), P(x + s * 0.75), P(y + s * 0.4)), 180, 360, fill=A(ZEN, a))
    d.rect(x - s * 0.75, y - s * 0.62 + bob, x + s * 0.75, y, fill=A(ZEN, a))
    d.circ(x, y - s * 1.25 + bob, s * 0.5, fill=A((250, 210, 170), a))
    d.ell(x, y - s * 0.85 + bob, s * 0.42, s * 0.38, A(BEARD, a))
    d.ell(x, y - s * 1.66 + bob, s * 0.46, s * 0.16, A(BEARD, a))
    face(d, x, y - s * 1.3 + bob, s * 0.5, mood, a, nomouth=True)
    d.arc(x, y - s * 1.03 + bob, s * 0.15, s * 0.08, 20, 160, A(INK, a), s * 0.04)
def s_setup(t, d):
    if t < RULE:
        temple(d, t)
        zeno(d, 540, 1230, 260, t, "sus" if t < ZENO_HIT + 0.6 else "proud", ease(pr(t, SETUP, SETUP + 0.3)))
        stamp(d, t, ZENO_HIT, "芝诺", 540, 250, 150, GOLD)
        d.rect(300, 1360, 780, 1430, fill=A(GOLD, ease(pr(t, ZENO_HIT, ZENO_HIT + .3))), r=35)
        d.text(540, 1395, "公元前 5 世纪 · 古希腊", 40, A(NAVY, ease(pr(t, ZENO_HIT, ZENO_HIT + .3))), k=1)
    else:
        stadium(d, t); track(d, 1100, t, 0)
        d.rect(140, 1100, 156, 1520, fill=A(WHITE, 0.9))
        ach(d, 170, 1300, 150, t, 0.0, "chill"); turtle(d, 820, 1300, 110, t, 0.0, "proud")
        k = ease(pr(t, RULE_HIT, RULE_HIT + 0.5))
        d.line([(220, 1450), (220 + 580 * k, 1450)], A(YEL, 1), 8)
        if k > 0.95: d.text(510, 1500, "先跑 100 米", 48, A(YEL, 1), k=1)
        stamp(d, t, RULE_HIT, "速度 ×10", 270, 800, 96, ACH_L)
        stamp(d, t, RULE_HIT + 0.5, "×1", 820, 800, 96, SH_L)
        d.text(270, 890, "10 米/秒", 44, A(WHITE, ease(pr(t, RULE_HIT, RULE_HIT + 0.3))), k=1)
        d.text(820, 890, "1 米/秒", 44, A(WHITE, ease(pr(t, RULE_HIT + 0.5, RULE_HIT + 0.8))), k=1)
        d.text(540, 420, "阿基里斯 vs 乌龟", 92, A(WHITE, ease(pr(t, RULE, RULE + 0.3))), k=1)

# ---------- the steps: zooming ruler ----------
def apos(k): return sum(100 / 10 ** j for j in range(k))  # achilles position at start of step k
def stepstate(t):
    for k in range(len(STEPS)):
        t0 = STEPS[k]; t1 = STEPS[k + 1] if k + 1 < len(STEPS) else STEPS_END
        if t0 <= t < t1 or (k == len(STEPS) - 1): break
    dur = t1 - t0; u = (t - t0) / dur
    dash = eio(pr(u, 0.05, 0.42)); zoom = eio(pr(u, 0.68, 0.98))
    a0 = apos(k); g = 100 / 10 ** k
    a = a0 + g * dash; b = a0 + g + g / 10 * dash
    sc = 5.6 * 10 ** (k + zoom)
    ax = lerp(820, 260, zoom) if dash >= 1 else 260 + g * dash * 5.6 * 10 ** k
    anchor = a - (ax - 260) / sc
    return k, u, dash, zoom, a, b, sc, anchor
def fmt(v, dec):
    return f"{v:.{max(0, dec)}f}"
def s_steps(t, d):
    k, u, dash, zoom, a, b, sc, anchor = stepstate(t)
    grad(d, NAVY, NAVY2); stars(d, t, 0.35)
    hue = PIECES[k % len(PIECES)]
    glow(d, 540, 700, 600, hue, 0.12)
    X = lambda x: 260 + (x - anchor) * sc
    track(d, 1060, t, (anchor * sc) % 2240, 300)
    # ruler
    d.rect(0, 1360, OW, 1480, fill=A((22, 26, 48), 0.95))
    lu = math.floor(math.log10(220 / sc)); un = 10 ** lu
    i0 = math.floor((anchor - 300 / sc) / un); i1 = math.ceil((anchor + 900 / sc) / un)
    for i in range(i0, min(i1, i0 + 80) + 1):
        x = X(i * un)
        if -20 < x < 1100:
            major = i % 10 == 0
            d.rect(x - 2, 1360, x + 2, 1360 + (60 if major else 30), fill=A(WHITE, 0.9 if major else 0.5))
            if un * sc > 120 or major:
                d.text(x, 1450, fmt(i * un, -lu), 26 if not major else 30, A(YEL if major else WHITE, 0.9), k=1)
    d.text(80, 1330, "米", 30, A(WHITE, 0.6))
    # markers of previous positions
    bx = X(b); ax_ = X(a)
    tx = X(apos(k + 1))
    d.line([(tx, 980), (tx, 1360)], A(YEL, 0.6), 4)
    ach(d, ax_, 1250, 140, t, 1.4 * (1 - pr(u, 0.42, 0.5)) + 0.2, "scared" if k >= 3 else "chill", sweat=k / 7)
    turtle(d, bx + 70, 1250, 100, t, 0.8, "proud")
    # gap readout
    t1 = STEPS[k + 1] if k + 1 < len(STEPS) else STEPS_END
    gap_now = 100 / 10 ** (k + 1); dec = max(0, k - 1)
    if u > 0.42:
        stamp(d, t, STEPS[k] + 0.42 * (t1 - STEPS[k]), "差 " + fmt(gap_now, dec) + " 米", 540, 640, 130 if k < 4 else 96, YEL)
    d.rect(380, 300, 700, 380, fill=A(hue, 0.95), r=40)
    d.text(540, 340, f"第 {k + 1} 步", 52, A(NAVY, 1), k=1)
    if zoom > 0:
        rr = 120 + 500 * zoom
        d.circ(540, 900, rr, outline=A(WHITE, 0.5 * (1 - zoom)), w=10)
        d.text(540, 900, "放大 ×10", 80, A(WHITE, 0.9 * math.sin(zoom * math.pi)), k=1)
    if k >= 4: d.text(540, 820, "……还有下一步", 60, A(WHITE, 0.6 + 0.4 * math.sin(t * 8)), k=1)

def s_tense(t, d):
    grad(d, (8, 10, 22), (24, 20, 46))
    hb = pulse(t, [TENSE + 3.4 * (1 - (1 - i / 10) ** 1.6) for i in range(10)], 8)
    # infinite staircase shrinking to a vanishing point
    x, y, w, h = 80, 1400, 420, 160
    for i in range(22):
        col = PIECES[i % 8]
        d.rect(x, y - h, x + w, y, fill=A(col, 0.85 - i * 0.03))
        x += w; y -= h; w *= 0.6; h *= 0.6
    glow(d, x, y, 120 + 40 * hb, YEL, 0.8)
    d.text(x - 10, y - 120, "∞", 140 + int(30 * hb), A(YEL, 1), k=1)
    ach(d, 230, 1240, 120, t, 1.6, "scream", sweat=1)
    if t < NEVER:
        stamp(d, t, TENSE + 0.2, "无穷多步", 540, 420, 160, WHITE)
    else:
        turtle(d, 640, 1144, 110, t, 0.0, "proud")
        stamp(d, t, NEVER + 0.1, "永远追不上？", 540, 420, 150 + int(10 * hb), YEL)
    vignette(d, 0.6 + 0.4 * hb)
    if t > SIL0 - 0.05: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.6))

def s_real(t, d):
    if t < REAL_HIT:
        grad(d, (4, 4, 10), (10, 10, 20)); d.text(540, 900, "现实呢？", 120, A(WHITE, ease(pr(t, REAL, REAL + 0.2))), k=1); return
    rays(d, t, (255, 196, 80), (240, 120, 60), cy=1000)
    track(d, 1180, t, t * 2400)
    sparks(d, 540, 1000, t, REAL_HIT, 60, 1500, WHITE, 1, 5)
    u = pr(t, REAL_HIT, REAL_HIT + 1.6)
    ax = lerp(200, 860, eio(u)); tx = 620
    turtle(d, tx, 1300, 140, t, 0.0, "scared" if u < 0.7 else "sad")
    ach(d, ax, 1300, 210, t, 1.6, "proud" if u > 0.5 else "scream")
    stamp(d, t, REAL_HIT, "11.1 秒", 540, 520, 250, WHITE)
    stamp(d, t, REAL_HIT + 0.5, "就追上了！", 540, 760, 120, NAVY)
    if t > REAL_HIT + 1.2:
        d.rect(330, 880, 750, 960, fill=A(NAVY, 0.9 * ease(pr(t, REAL_HIT + 1.2, REAL_HIT + 1.5))), r=40)
        d.text(540, 920, "在 111.1 米处", 48, A(YEL, ease(pr(t, REAL_HIT + 1.2, REAL_HIT + 1.5))), k=1)

def s_why(t, d):
    grad(d, (18, 22, 46), (40, 30, 70)); stars(d, t, 0.3)
    if t < SUM:
        zeno(d, 540, 1300, 230, t, "scared" if t > NEQ_HIT else "proud")
        d.rect(90, 330, 990, 460, fill=A((60, 70, 130), 0.9), r=30); d.text(540, 395, "无穷多步", 100, A(WHITE, 1), k=1)
        d.rect(90, 690, 990, 820, fill=A((60, 70, 130), 0.9), r=30); d.text(540, 755, "无穷长的时间", 100, A(WHITE, 1), k=1)
        d.text(540, 575, "=", 150, A(WHITE, 1 - ease(pr(t, NEQ_HIT, NEQ_HIT + 0.1))), k=1)
        stamp(d, t, NEQ_HIT, "≠", 540, 575, 190, RED)
        if t > NEQ_HIT: glow(d, 540, 575, 200, RED, 0.5 * pulse(t, [NEQ_HIT], 3)); stamp(d, t, NEQ_HIT + 0.4, "漏洞", 860, 560, 80, RED)
        return
    # summing the times
    x0, x1, yb = 90, 990, 1020; scl = (x1 - x0) / 12.0
    d.rect(x0, yb, x1, yb + 10, fill=A(WHITE, 0.5))
    for s_ in range(13):
        d.rect(x0 + s_ * scl - 2, yb, x0 + s_ * scl + 2, yb + 30, fill=A(WHITE, 0.6)); d.text(x0 + s_ * scl, yb + 60, str(s_), 30, A(WHITE, 0.7))
    d.text(x1, yb + 105, "秒", 30, A(WHITE, 0.7))
    acc = 0.0; eq = []
    for i, bt in enumerate(BLK):
        L = 10 / 10 ** i
        k = back(pr(t, bt, bt + 0.25))
        if k > 0:
            h = 220 * (0.4 + 0.6 * k)
            d.rect(x0 + acc * scl, yb - h, x0 + (acc + L) * scl * min(1, k) + 2, yb, fill=A(PIECES[i], 0.95), r=min(12, L * scl / 2))
            if i < 2: d.text(x0 + (acc + L / 2) * scl + (0 if i == 0 else 40), yb - h - (50 if i == 0 else 130), fmt(L, i - 1) + " 秒", 46, A(PIECES[i], 1), k=1)
            eq.append(fmt(L, i - 1) if i < 4 else "")
        acc += L
    s = " + ".join([e for e in eq if e][:4]) + (" + …" if len(eq) > 4 else "")
    if s: d.text(540, 420, s, 66, A(WHITE, 1), k=1)
    lx = x0 + 100 / 9 * scl
    if t > LIMIT_HIT:
        glow(d, lx, yb - 120, 160, RED, 0.6 * pulse(t, [LIMIT_HIT], 2) + 0.2)
        for yy in range(int(yb - 360), int(yb + 20), 30): d.rect(lx - 3, yy, lx + 3, yy + 16, fill=A(RED, 1))
        stamp(d, t, LIMIT_HIT, "= 11.11… 秒", 540, 600, 120, YEL)
        d.text(540, 1300, "加无穷多次，也超不过这条线", 52, A(WHITE, ease(pr(t, LIMIT_HIT + 0.4, LIMIT_HIT + 0.7))), k=1)
    else:
        u = (t * 2) % 1
        d.circ(540, 1300, 70, fill=A(WHITE, 0.9)); ang = t * 8
        d.line([(540, 1300), (540 + math.cos(ang) * 55, 1300 + math.sin(ang) * 55)], A(NAVY, 1), 8)

def s_cake(t, d):
    grad(d, PINKBG, (110, 50, 80)); stars(d, t, 0.25)
    S0 = 680; x0, y0 = 540 - S0 / 2, 520
    mood = "chill"
    if t > CUT[0]: mood = "scared"
    if t > CUT[4]: mood = "dizzy"
    if t > ONE_HIT: mood = "happy"
    wob = 1 + 0.03 * pulse(t, CUT + [ONE_HIT], 8)
    d.rect(x0 - 20, y0 + S0 - 10, x0 + S0 + 20, y0 + S0 + 40, fill=A((240, 240, 250), 1), r=20)
    d.rect(x0, y0, x0 + S0, y0 + S0, fill=A(CAKEC, 1), r=16)
    d.rect(x0, y0, x0 + S0, y0 + 60, fill=A(CREAM, 1), r=16)
    rx, ry, rw, rh = x0, y0, S0, S0
    labels = ["1/2", "1/4", "1/8", "1/16", "", "", "", ""]
    for i, ct in enumerate(CUT):
        if t < ct - 0.25: break
        horiz = i % 2 == 0
        if horiz: px0, py0, px1, py1 = rx, ry, rx + rw / 2, ry + rh
        else: px0, py0, px1, py1 = rx, ry, rx + rw, ry + rh / 2
        kc = pr(t, ct - 0.25, ct)
        if t < ct:  # knife sweep
            if horiz: d.rect(px1 - 4, py0 - 40, px1 + 4, py0 + (py1 - py0 + 80) * kc, fill=A(WHITE, 0.95))
            else: d.rect(px0 - 40, py1 - 4, px0 + (px1 - px0 + 80) * kc, py1 + 4, fill=A(WHITE, 0.95))
            break
        k = back(pr(t, ct, ct + 0.2)); g = 6
        d.rect(px0 + g, py0 + g, px1 - g, py1 - g, fill=A(PIECES[i], 0.85 * min(1, k)), r=10)
        if labels[i] and (px1 - px0) > 60: d.text((px0 + px1) / 2, (py0 + py1) / 2, labels[i], int(min(90, (px1 - px0) * 0.35) * (0.7 + 0.3 * k)), A(NAVY, 1), k=1)
        if horiz: rx += rw / 2; rw /= 2
        else: ry += rh / 2; rh /= 2
    for i in range(5): d.circ(x0 + 80 + i * 130, y0 + 30, 26, fill=A(BERRY, 1))
    face(d, 540, y0 + S0 + 210, 150 * wob, mood, 1)
    if t > ONE_HIT:
        glow(d, 540, y0 + S0 / 2, 500, YEL, 0.5 * pulse(t, [ONE_HIT], 2) + 0.15)
        stamp(d, t, ONE_HIT, "= 1 块", 540, 350, 150, YEL)
    else:
        stamp(d, t, CUT[0], "1/2 + 1/4 + 1/8 + …", 540, 360, 74, WHITE)
    sparks(d, 540, y0 + S0 / 2, t, ONE_HIT, 50, 1200, YEL, 1, 9)

HEV = [(-450, "公元前 450 年", "芝诺出题", ZEN), (-350, "公元前 4 世纪", "亚里士多德记下它", STONE), (1680, "17 世纪", "牛顿、莱布尼茨 · 微积分", SH_L), (1821, "1821 年", "柯西 · 极限", YEL)]
def s_hist(t, d):
    grad(d, (14, 26, 40), (24, 50, 70)); stars(d, t, 0.4)
    xl = 170; ys = [640, 840, 1040, 1240]
    d.rect(xl - 5, 560, xl + 5, 1320, fill=A(WHITE, 0.3))
    for i, (yr, a_, b_, col) in enumerate(HEV):
        y = ys[i]; k = back(pr(t, HPTS[i], HPTS[i] + 0.25))
        if k <= 0: d.circ(xl, y, 12, fill=A(WHITE, 0.4)); continue
        glow(d, xl, y, 90, col, 0.4 * k); d.circ(xl, y, 28 * k, fill=A(col, 1))
        d.text(xl + 70, y - 34, a_, 50, A(col, min(1, k)), anchor="lm", k=1)
        d.text(xl + 70, y + 34, b_, 42, A(WHITE, min(1, k)), anchor="lm", k=1)
    if t < HPTS[3]:
        stamp(d, t, HIST + 0.2, "两千多年", 540, 380, 170, WHITE)
    else:
        glow(d, 540, 380, 260, YEL, 0.3 + 0.4 * pulse(t, [HPTS[3]], 3))
        stamp(d, t, HPTS[3], "极限", 540, 380, 200, YEL)
        d.text(540, 1440, "无穷多个数，加起来可以是有限的", 50, A(YEL, ease(pr(t, HPTS[3] + 0.5, HPTS[3] + 0.8))), k=1)

def s_phys(t, d):
    grad(d, (10, 12, 26), (20, 30, 60))
    u = pr(t, PHYS, OUTRO - 0.4); z = 2 ** (u * 6)
    for lev in range(6):
        sp = 400 / 2 ** lev * z
        if sp < 18 or sp > 3000: continue
        al = cl((sp - 18) / 60) * 0.35
        x = 540 - math.floor(540 / sp) * sp - sp
        while x < OW + sp: d.rect(x - 1, 0, x + 1, OH, fill=A(CYAN, al)); x += sp
        y = 960 - math.floor(960 / sp) * sp - sp
        while y < OH + sp: d.rect(0, y - 1, OW, y + 1, fill=A(CYAN, al)); y += sp
    turtle(d, 540, 1150, 130 * (1 + 0.1 * math.sin(t * 3)), t, 0.3, "sus")
    stamp(d, t, PHYS_HIT, "空间能无限切吗？", 540, 460, 110, WHITE)
    d.text(540, 640, "物理学：还没有定论", 60, A(CYAN, ease(pr(t, PHYS_HIT + 0.8, PHYS_HIT + 1.1))), k=1)
    for i in range(10):
        uu = (t * 0.4 + i / 10) % 1
        d.text((i * 263) % 1000 + 40, 1800 - uu * 1500, "?", 50 + i % 3 * 20, A(YEL, 0.5 * math.sin(uu * math.pi)), k=1)

def bubble(d, x, y, s, side, col, tcol, a, size=52):
    if a <= 0: return
    w = d.tlen(s, size, 1) + 70; x0 = x if side < 0 else x - w
    d.rect(x0, y - 55, x0 + w, y + 55, fill=A(col, a), r=40)
    tx = x0 + 30 if side < 0 else x0 + w - 30
    d.poly([(tx, y + 40), (tx - side * -1 * 0 + (20 if side < 0 else -20), y + 85), (tx + (40 if side < 0 else -40), y + 45)], A(col, a))
    d.text(x0 + w / 2, y, s, size, A(tcol, a), k=1)
def popk(t, t0): return back(pr(t, t0, t0 + 0.2))
def s_end(t, d):
    grad(d, NAVY, NAVY2); stars(d, t, 0.5)
    zeno(d, 170, 640, 120, t, "sus")
    bubble(d, 300, 500, "所以到底追不追得上？", -1, ZEN, WHITE, min(1, popk(t, BUBS[0])), 50)
    ach(d, 900, 950, 120, t, 0.0, "proud")
    bubble(d, 780, 780, "早追上了，第 11.1 秒", 1, ACH, WHITE, min(1, popk(t, BUBS[1])), 50)
    turtle(d, 180, 1230, 90, t, 0.0, "sad")
    bubble(d, 310, 1100, "我只是……步数多", -1, SH, WHITE, min(1, popk(t, BUBS[2])), 50)
    d.text(540, 1700, "Aristotle, Physics VI.9, 239b", 28, A(WHITE, 0.6), k=0)
    d.text(540, 1740, "Cauchy, Cours d'analyse, 1821", 28, A(WHITE, 0.6), k=0)
    d.text(540, 1780, "数字为示意：阿基里斯 10 米/秒，乌龟 1 米/秒，领先 100 米", 26, A(WHITE, 0.5), k=0)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

def subs(t, d):
    if t >= OUTRO: return
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            lines = wrap(d, s, 56, 900)
            for j, ln in enumerate(lines):
                y = 1620 + (j - (len(lines) - 1) / 2) * 84
                w = d.tlen(ln, 56)
                d.rect(540 - w / 2 - 24, y - 42, 540 + w / 2 + 24, y + 42, fill=A((8, 10, 20), 0.82 * al), r=16)
                d.text(540, y, ln, 56, A(WHITE, al))
            break
def brand(t, d):
    d.rect(50, 80, 300, 128, fill=A((255, 255, 255), 0.16), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(WHITE, 1))
    d.rect(740, 80, 1030, 128, fill=A(CYAN, 0.95), r=24); d.text(885, 104, "科普 · 芝诺的乌龟", 26, A(NAVY, 1), k=1)

SECS = [(0, HOOK_END, s_hook), (SETUP, STEPS[0], s_setup), (STEPS[0], STEPS_END, s_steps), (TENSE, REAL, s_tense), (REAL, WHY, s_real),
        (WHY, CAKE, s_why), (CAKE, HIST, s_cake), (HIST, PHYS, s_hist), (PHYS, OUTRO, s_phys), (OUTRO, 99, s_end)]
CUTS = [HOOK_END, RULE, STEPS[0], TENSE, NEVER, REAL_HIT, WHY, SUM, CAKE, HIST, PHYS, OUTRO]
def cam(t):
    z = 1.0 + 0.06 * pulse(t, HITS, 7)
    for a, b in RISERS:
        if a <= t < b: z += 0.08 * eio(pr(t, a, b))
    if TENSE <= t < SIL0: z += 0.1 * pr(t, TENSE, SIL0)
    amp = 26 * pulse(t, [HOOK_HIT, REAL_HIT], 4) + 6 * pulse(t, HITS, 6)
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
