
# ================= backgrounds =================
SKIES = {"night": ((14, 18, 44), (52, 30, 74)), "day": ((120, 180, 230), (210, 230, 220)), "dusk": ((60, 30, 80), (240, 130, 70)), "rain": ((70, 86, 104), (130, 146, 150))}
def grad(d, top, bot, y0=0, y1=OH, n=48):
    for i in range(n):
        ya = lerp(y0, y1, i / n); yb = lerp(y0, y1, (i + 1) / n) + 1
        d.rect(-50, ya, OW + 50, yb, fill=A(mix(top, bot, i / (n - 1)), 1))
rnd = random.Random(3)
GRASS = [(rnd.uniform(-40, 1120), rnd.uniform(0.6, 1.0), rnd.uniform(0, 6)) for _ in range(70)]
MINI = [(rnd.uniform(40, 1040), rnd.uniform(1180, 1300), rnd.uniform(40, 80)) for _ in range(7)]
def bog(d, t, tod="night", wind=0.0, minis=True, horizon=1150):
    top, bot = SKIES[tod]; grad(d, top, bot, 0, horizon)
    if tod == "night":
        d.circ(930, 200, 48, fill=A((245, 240, 210), 1))
        for i in range(40):
            sx_, sy_ = (i * 263) % 1080, (i * 151) % 900
            d.circ(sx_, sy_, 2 + (i % 3), fill=A(WHITE, 0.4 + 0.4 * math.sin(t * 3 + i)))
    elif tod == "dusk": d.circ(540, horizon - 60, 160, fill=A((255, 190, 100), 0.9))
    elif tod == "day": d.circ(860, 300, 80, fill=A((255, 245, 200), 1))
    if tod in ("day", "rain"):
        for i in range(4):
            cx_ = ((i * 330 + t * 40) % 1500) - 200; cy_ = 260 + i * 90
            for j in range(3): d.ell(cx_ + j * 70, cy_ - (j % 2) * 30, 90, 50, A(WHITE if tod == "day" else (170, 180, 190), 0.8))
    hill = mix(top, (10, 20, 14), 0.75)
    d.poly([(-50, horizon)] + [(x, horizon - 90 - 60 * math.sin(x / 170) - 30 * math.sin(x / 61)) for x in range(-50, 1131, 30)] + [(1130, horizon)], A(hill, 1))
    grad(d, (34, 58, 34), (14, 26, 16), horizon, OH, 20)
    for i in range(5): d.ell(150 + i * 230, horizon + 120 + (i % 2) * 90, 120, 18, A(mix(top, bot, 0.5), 0.35))
    if minis:
        for (mx, my, ms) in MINI: trap(d, mx, my, ms, 0.6 + 0.3 * math.sin(t * 2 + mx), "sleep" if tod == "night" else "open", 0.85, stem=False)
    for (gx, gs, ph) in GRASS:
        sway = (math.sin(t * 2 + ph) * 12 + wind * 70) * gs
        d.line([(gx, OH), (gx + sway * 0.5, OH - 160 * gs), (gx + sway, OH - 260 * gs)], A((40, 90, 44), 1), 7)
    if tod == "night":
        for i in range(3):
            fx_ = ((i * 400 + t * 60) % 1500) - 200
            d.ell(fx_, horizon - 20 + i * 40, 320, 40, A((200, 210, 230), 0.08))

def flesh_bg(d, t):
    grad(d, (120, 16, 40), (60, 8, 24))
    for j in range(16):
        for i in range(9):
            x = i * 130 + (j % 2) * 65; y = j * 130 + 40
            d.circ(x, y, 22, fill=A((170, 40, 70), 0.6)); d.circ(x - 6, y - 6, 7, fill=A((230, 110, 130), 0.5))

def rays(d, t, c1, c2, n=18, cx=540, cy=900):
    grad(d, c2, mix(c2, (0, 0, 0), 0.4))
    rot = t * 0.6
    for i in range(n):
        a0 = rot + i * 2 * math.pi / n; a1 = a0 + math.pi / n
        d.poly([(cx, cy), (cx + math.cos(a0) * 2000, cy + math.sin(a0) * 2000), (cx + math.cos(a1) * 2000, cy + math.sin(a1) * 2000)], A(c1, 1))

def grid_bg(d, t, col=(10, 30, 22)):
    grad(d, col, mix(col, (0, 0, 0), 0.5))
    for x in range(0, 1081, 90): d.line([(x, 0), (x, OH)], A((60, 140, 90), 0.25), 2)
    for y in range(0, 1921, 90): d.line([(0, y), (OW, y)], A((60, 140, 90), 0.25), 2)

def vignette(d, k):
    if k <= 0: return
    for i in range(10):
        m = 40 * i
        d.rect(-m, -m, OW + m, OH + m, outline=A((0, 0, 0), 0.12 * k), w=120)

# ================= scenes: world(t,d) + ui(t,d) =================
def w_hook(t, d):
    bog(d, t, "night")
    op = snap_op(t, HOOK_SNAP)
    face = "peek" if t < HOOK_SNAP else ("chomp" if t < HOOK_SNAP + 0.5 else "happy")
    fx = lerp(180, 540, ease(pr(t, -0.3, 0.1))); fy = lerp(500, 990, ease(pr(t, -0.3, 0.1)))
    trap(d, 540, 900, 360, op, face, 1, look=0.3 if t < HOOK_SNAP else 0, flyin=lambda: fly(d, fx, fy, 80, 1, t, scared=t > 0.25))
    rings(d, 540, 900, t, [HOOK_SNAP], YEL, 1, 600)
def u_hook(t, d):
    a = 1 - pr(t, 2.45, 2.6)
    k = back(pr(t, 0.0, 0.2)) * (1 + 0.15 * pulse(t, [HOOK_SNAP], 6))
    d.text(540, 330, "它会数数", int(150 * (0.6 + 0.4 * k)), A(YEL, a), k=1)
    for i, h in enumerate(HOOK_TOUCH):
        if h <= t < HOOK_SNAP + 0.3: d.text(860, 600, str(i + 1), 130, A(WHITE, a * (1 - pr(t, HOOK_SNAP, HOOK_SNAP + 0.3))), k=1)
    flash(d, t, [HOOK_SNAP], YEL, 0.35)

def w_rule1(t, d):  # macro: trigger hair
    flesh_bg(d, t)
    bx, by, tx, ty = 540, 1450, 560, 520
    d.ell(bx, by + 30, 120, 40, A((90, 10, 30), 1))
    d.poly([(bx - 46, by), (bx + 46, by), (bx + 18, by - 160), (tx + 6, ty), (tx - 6, ty), (bx - 18, by - 160)], A((250, 200, 170), 1))
    d.ell(bx, by - 160, 30, 16, A((220, 160, 130), 1))
    lit = pulse(t, [T1], 2.5)
    if lit > 0.02:
        u = pr(t, T1, T1 + 0.6)
        yy = lerp(ty, by, u); d.circ(lerp(tx, bx, u), yy, 30, fill=A(YEL, lit))
        for j in range(3):
            rr = 80 + (t - T1) * 900 + j * 90
            if t >= T1: d.circ(bx, by, rr, outline=A(YEL, 0.6 * lit * (1 - j * 0.3)), w=10)
    # fly leg
    reach = ease(pr(t, 3.0, T1)) * (1 - ease(pr(t, FORGET, FORGET + 0.6)))
    lx, ly = lerp(1250, tx + 30, reach), lerp(80, ty - 30, reach)
    d.line([(1300, -100), (lerp(1300, 900, reach), lerp(-100, 260, reach)), (lx, ly)], A(FLYC, 1), 26)
    d.line([(lx, ly), (lx - 40, ly + 20)], A(FLYC, 1), 12); d.line([(lx, ly), (lx - 20, ly + 45)], A(FLYC, 1), 12)
    for k in range(6):
        px, py = lerp(1300, 900, reach) + (lx - lerp(1300, 900, reach)) * k / 6, lerp(-100, 260, reach) + (ly - lerp(-100, 260, reach)) * k / 6
        d.line([(px, py), (px + 22, py - 30)], A(FLYC, 1), 5)
def u_rule1(t, d):
    a = win(t, 2.6, 9.0, 0.2, 0.2)
    d.text(300, 1300, "感觉毛", 44, A(WHITE, a * ease(pr(t, 3.0, 3.4))))
    if T1 <= t < FORGET + 0.4:
        fa = a * (1 - pr(t, FORGET, FORGET + 0.4))
        bignum(d, t, 1, T1, a=fa); g = pr(t, T1, FORGET)
        d.arc(540, 330, 150, 150, -90, -90 + 360 * (1 - g), A(CYAN, fa), 12)
        d.text(540, 520, "30 秒内", 40, A(CYAN, fa))
        d.text(800, 760, "电信号", 44, A(YEL, fa * ease(pr(t, T1 + 0.2, T1 + 0.5))))
    if t > FORGET: d.text(540, 330, "忘了", 120, A(WHITE, a * ease(pr(t, FORGET, FORGET + 0.3))), k=1)

def w_rule2(t, d):
    bog(d, t, "night", minis=False)
    op = snap_op(t, SNAP2)
    face = "peek" if t < T2[0] else "smug" if t < SNAP2 else "chomp" if t < SNAP2 + 0.5 else "happy"
    trap(d, 540, 930, 330, op, face, 1, flyin=lambda: fly(d, 560, 1030, 75, 1, t, flap=False, scared=t > T2[1] - 0.2))
    rings(d, 540, 1040, t, T2, YEL, 1, 260)
def u_rule2(t, d):
    if t >= T2[1]: bignum(d, t, 2, T2[1])
    elif t >= T2[0]: bignum(d, t, 1, T2[0])
    flash(d, t, [SNAP2], YEL, 0.3)

def w_count(t, d):  # x-ray inside the shut trap
    grad(d, (40, 6, 16), (8, 2, 6))
    p = pulse(t, [T3, T4], 7); rr = pr(t, RISER[0], RISER[1])
    sx, sy = shake(t, 10 * p + 3 + 10 * rr, 50)
    cx, cy = 540 + sx, 900 + sy
    d.ell(cx, cy, 470, 330, A((120, 20, 44), 1)); d.ell(cx, cy, 440, 300, A((170, 36, 64), 1))
    n = 1 if t < T3 else 2 if t < T4 else 3
    rows = [(cx + i * 70 - 315, cy + j * 70 - 175) for j in range(6) for i in range(10)]
    for k, (gx, gy) in enumerate(rows):
        if ((gx - cx) / 440) ** 2 + ((gy - cy) / 300) ** 2 > 0.8: continue
        lit = (k * 7 % 10) < (0 if t < T3 else 4 if t < T4 else 8)
        d.circ(gx, gy, 14, fill=A(DIGEST if lit else (210, 90, 110), 0.9 if lit else 0.5))
    fx, fy = cx + 60 * math.sin(t * 7), cy + 30 * math.cos(t * 9)
    fly(d, fx, fy, 110, 1, t, scared=True)
    d.ell(cx, cy - 330, 480, 70, A((52, 112, 52), 1)); d.ell(cx, cy + 330, 480, 70, A((52, 112, 52), 1))
    for i in range(11):
        tx = cx - 440 + i * 88
        d.poly([(tx - 18, cy - 290), (tx + 18, cy - 290), (tx, cy - 220)], A(GREEN_L, 1))
        d.poly([(tx + 26, cy + 290), (tx + 62, cy + 290), (tx + 44, cy + 220)], A(GREEN_L, 1))
    vignette(d, 0.4 + rr)
def u_count(t, d):
    a = win(t, 12.0, 19.5, 0.1, 0.05); rr = pr(t, RISER[0], RISER[1])
    if t < T3: d.text(540, 330, "2", 230, A(YEL, a), k=1); d.text(540, 1300, "透视：夹子里面", 40, A(MUTE, a))
    elif t < T4:
        bignum(d, t, 3, T3); d.text(540, 520, "腺体开始造消化酶", 48, A(DIGEST, a * ease(pr(t, T3 + 0.2, T3 + 0.5))), k=1)
    else: bignum(d, t, 4, T4, col=mix(YEL, RED, rr))
    if rr > 0: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), 0.55 * rr))

def w_burst(t, d):
    p = pulse(t, [BURST + i * BEAT for i in range(8)], 8)
    beat = int((t - BURST) / BEAT)
    rays(d, t, (40, 120, 50) if beat % 2 else (120, 30, 50), (14, 40, 20))
    trap(d, 540, 980, 340 * (1 + 0.04 * p), 0.0, "evil", 1)
    for i in range(9):
        u = ((t - BURST) * 0.9 + i * 0.29) % 1
        d.ell(250 + i * 72, lerp(990, 1240, u), 14, 22, A(DIGEST, 1 - u))
def u_burst(t, d):
    a = win(t, BURST, 24.0, 0.01, 0.2)
    p = pulse(t, [BURST + i * BEAT for i in range(8)], 8)
    k = back(pr(t, BURST, BURST + 0.25))
    big = lerp(760, 260, ease(pr(t, BURST + 0.3, BURST + 1.0))); yy = lerp(900, 330, ease(pr(t, BURST + 0.3, BURST + 1.0)))
    d.text(540, yy, "5", int(big * (0.5 + 0.5 * k) * (1 + 0.05 * p)), A(YEL, a), k=1)
    d.text(540, 560, "开饭！", 84, A(DIGEST, a * ease(pr(t, BURST + 0.9, BURST + 1.2))), k=1)
    if t < BURST + 0.12: d.rect(0, 0, OW, OH, fill=A(WHITE, 1 - pr(t, BURST, BURST + 0.12)))

def w_wind(t, d):
    gust = pulse(t, [WIND[0]], 1.5) if t >= WIND[0] - 0.3 else 0
    bog(d, t, "rain", wind=gust)
    face = "peek" if any(h <= t < h + 1.0 for h in WIND) else "sleep"
    trap(d, 540, 900, 300, 1.0, face, 1)
    for i in range(60):  # rain
        rx = (i * 97 + t * 200) % 1180 - 50; ry = (i * 211 + t * 1600) % 2000 - 80
        d.line([(rx, ry), (rx - 10, ry + 46)], A((200, 220, 240), 0.35), 3)
    u = pr(t, WIND[0] - 0.6, WIND[0] + 0.5)
    for i in range(5):
        yy = 700 + i * 70; x0 = lerp(-400, 1300, u) - i * 70
        d.line([(x0, yy), (x0 + 300, yy - 12)], A(WHITE, 0.7 * (1 - abs(u - 0.5) * 2)), 7)
    dy = lerp(380, 1000, eio(pr(t, WIND[1] - 0.6, WIND[1])))
    if WIND[1] - 0.6 < t < WIND[1] + 0.05: d.ell(560, dy, 26, 38, A(WATER, 1))
    rings(d, 540, 1000, t, WIND, CYAN, 1, 180)
def u_wind(t, d):
    a = win(t, 24.0, 30.0, 0.2, 0.2)
    for h, lbl in zip(WIND, ("风", "雨滴")):
        if h <= t < h + 1.2:
            q = a * (1 - pr(t, h + 0.8, h + 1.2)); bignum(d, t, 1, h, a=q); d.text(540, 520, lbl + "：只碰 1 下", 48, A(WHITE, q), k=1)
    if t > 28.0:
        d.text(540, 380, "不合", 140, A(WHITE, a * ease(pr(t, 28.0, 28.3))), k=1)
        for i in range(3):
            zu = ((t - 28) * 0.8 + i * 0.33) % 1
            d.text(800 + zu * 80, 620 - zu * 160, "z", int(44 + 30 * zu), A(WHITE, a * (1 - zu)), k=1)

FLOOD_HITS = [FLOOD[0] + k * (FLOOD[1] - FLOOD[0]) / 30 for k in range(30)]
def w_flood(t, d):  # oscilloscope of action potentials
    grid_bg(d, t)
    y0 = 950; x_now = 900; speed = 260
    pts = []
    for xx in range(0, 1081, 6):
        tt = t - (x_now - xx) / speed; v = 0
        for h in FLOOD_HITS + [BURST]:
            dt = tt - h
            if 0 <= dt < 0.25: v = max(v, math.exp(-((dt - 0.03) / 0.03) ** 2) - 0.25 * math.exp(-((dt - 0.12) / 0.05) ** 2))
        pts.append((xx, y0 - v * 380))
    d.line(pts, A((120, 255, 150), 1), 7)
    d.circ(x_now, pts[x_now // 6][1], 14, fill=A(WHITE, 1))
    trap(d, 210, 1320, 150, 0.0, "evil", 1, stem=False)
    lvl = pr(t, FLOOD[0], FLOOD[1])
    d.rect(860, 1040, 980, 1360, outline=A(WHITE, 1), w=5, r=18); d.rect(866, 1354 - 310 * lvl, 974, 1354, fill=A(DIGEST, 1), r=14)
def u_flood(t, d):
    a = win(t, FLOOD[0], FLOOD[1], 0.2, 0.2)
    n = 5 + sum(1 for h in FLOOD_HITS if h <= t)
    d.text(540, 330, str(n), int(220 * (1 + 0.06 * pulse(t, FLOOD_HITS, 14))), A(YEL, a), k=1)
    d.text(540, 480, "每挣扎一下 = 一次电信号", 44, A((120, 255, 150), a), k=1)
    d.text(920, 1405, "消化液", 36, A(DIGEST, a))

def w_pump(t, d):  # cell membrane
    grad(d, (10, 40, 50), (4, 16, 24))
    for band in (860, 1010):
        for i in range(28):
            x = i * 40 + 10; d.circ(x, band, 17, fill=A((240, 200, 120), 1))
        d.rect(-10, band + 16 if band == 860 else band - 40, OW + 10, band + 40 if band == 860 else band - 16, fill=A((200, 160, 90), 0.6))
    for px in (270, 540, 810):
        d.rect(px - 50, 820, px + 50, 1050, fill=A((90, 200, 220), 1), r=36); d.rect(px - 14, 830, px + 14, 1040, fill=A((10, 40, 50), 1), r=10)
    for k in range(18):
        u = ((t - PUMP[0]) * 0.7 + k / 18) % 1; px = (270, 540, 810)[k % 3]
        y = lerp(560, 1340, u); x = px + (1 - min(1, abs(y - 935) / 200)) * 0 + (60 * math.sin(k + y / 90) if abs(y - 935) > 140 else 0)
        d.circ(x, y, 24, fill=A(YEL, 1)); d.text(x, y, "+", 30, A(BG, 1), k=1)
    trap(d, 170, 540, 110, 0.0, "happy", 1, stem=False)
def u_pump(t, d):
    a = win(t, PUMP[0], PUMP[1], 0.2, 0.2)
    d.text(540, 330, "吸收泵 开启", 90, A(CYAN, a * ease(pr(t, PUMP[0] + 0.1, PUMP[0] + 0.4))), k=1)
    d.text(830, 560, "猎物里的钠离子", 36, A(YEL, a)); d.text(860, 1300, "进入植物细胞", 38, A(WHITE, a))

def w_end(t, d):
    bog(d, t, "dusk")
    op = snap_op(t, LAST_SNAP)
    face = "wink" if 40.8 < t < 41.6 else ("chomp" if t >= LAST_SNAP else "open")
    trap(d, 540, 900, 320, op, face, 1)
def u_end(t, d):
    a = ease(pr(t, OUTRO, OUTRO + 0.3))
    d.text(540, 300, "你刚才", 84, A(WHITE, a), k=1); d.text(540, 420, "数到几了？", 110, A(YEL, a), k=1)
    d.text(540, 1500, "Böhm et al., Current Biology 26:286 (2016)", 30, A(WHITE, a), k=2)
    flash(d, t, [LAST_SNAP], YEL, 0.3)
    if t > DUR - 0.3: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.3, DUR)))

SECS = [(0, 2.6, w_hook, u_hook), (2.6, 9.0, w_rule1, u_rule1), (9.0, 12.0, w_rule2, u_rule2), (12.0, 19.5, w_count, u_count),
        (20.0, 24.0, w_burst, u_burst), (24.0, 30.0, w_wind, u_wind), (30.0, 35.0, w_flood, u_flood), (35.0, 39.0, w_pump, u_pump), (39.0, 45.0, w_end, u_end)]
CUTS = [2.6, 9.0, 12.0, 24.0, 30.0, 35.0, 39.0]

def cam(t):
    z, cx, cy = 1.0, 540, 960
    if t < 2.6: z = lerp(1.3, 1.0, ease(pr(t, 0, 0.5))) + 0.18 * pulse(t, [HOOK_SNAP], 5); cy = 900
    elif t < 9.0: z = lerp(1.0, 1.15, eio(pr(t, 2.6, 9.0))) + 0.08 * pulse(t, [T1], 5); cy = lerp(1000, 800, eio(pr(t, 2.6, 9.0)))
    elif t < 12: z = lerp(1.0, 1.12, eio(pr(t, 9, 10.5))) + 0.2 * pulse(t, [SNAP2], 5); cy = 940
    elif t < 19.5: z = lerp(1.0, 1.3, eio(pr(t, 12, 19.5))) + 0.05 * pulse(t, [T3, T4], 6); cy = 900
    elif BURST <= t < 24: z = 1.0 + 0.06 * pulse(t, [BURST + i * BEAT for i in range(8)], 7)
    elif t < 30: z = 1.12; cx = lerp(420, 660, eio(pr(t, 24, 30))); cy = 940
    elif t < 35: z = 1.0 + 0.03 * pulse(t, FLOOD_HITS, 14)
    elif t < 39: z = lerp(1.25, 1.0, ease(pr(t, 35, 36)))
    else: z = lerp(1.5, 1.0, eio(pr(t, 39, 41))) + 0.12 * pulse(t, [LAST_SNAP], 5); cy = lerp(880, 960, eio(pr(t, 39, 41)))
    return z, cx, cy

BURST_HITS = [BURST + i * BEAT for i in range(8)]
def frame(t):
    img = Image.new("RGB", (W, H), BG)
    d = D(img)
    ui = None
    for a, b, wf, uf in SECS:
        if a <= t < b: wf(t, d); ui = uf
    if SILENCE[0] <= t < SILENCE[1]: img = Image.new("RGB", (W, H), (0, 0, 0)); d = D(img); ui = None
    z, cx, cy = cam(t)
    if abs(z - 1) > 1e-3 or cx != 540 or cy != 960:
        cw, ch = W / z, H / z
        x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
        img = img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    if ui: ui(t, d)
    for c in CUTS:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.7 * (1 - (t - c) / 0.1)))
    if not (SILENCE[0] <= t < SILENCE[1]): brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)

if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.1f}.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for i in range(i0, i1): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); p.wait()
