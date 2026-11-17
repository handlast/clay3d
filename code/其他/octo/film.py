import sys, subprocess, math, random
from chars import *
from cues import *

def popk(t, t0, preset="snappy"): return max(0.0, E.spring_at(t, t0, 0, 1, preset)) if t >= t0 else 0.0
def ap(t, t0, d=0.12): return cl((t - t0) / d)
def tag(d, x, y, s, col, a=1.0, size=40, tc=NAVYT):
    if a <= 0.01: return
    w = d.tlen(s, size, 1) + 44
    d.rect(x - w / 2, y - size * 0.78, x + w / 2, y + size * 0.78, fill=A(col, 0.95 * a), r=size * 0.6)
    d.text(x, y, s, size, A(tc, a), k=1)
def ptag(d, t, t0, x, y, s, col, size=40, tc=NAVYT):
    k = popk(t, t0)
    if k > 0: tag(d, x, y + (1 - min(k, 1)) * 30, s, col, ap(t, t0), int(size * (0.6 + 0.4 * k)), tc)
def title(d, t, t0, s, y=330, size=110, col=WHITE):
    k = popk(t, t0, "heavy")
    if k > 0: d.text(540, y + (1 - k) * 40, s, int(size * (0.85 + 0.15 * k)), A(col, ap(t, t0)), k=1)
def slamtxt(d, t, t0, s, y, size, col):
    if t < t0: return
    d.text(540, y, s, int(size * E.slam(t, t0, 0.28, 1.8)), A(col, ap(t, t0, 0.06)), k=1)
def arrow(d, x0, y0, x1, y1, col, a=1.0, w=12):
    L = math.hypot(x1 - x0, y1 - y0) + 1e-6; ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    bx, by = x1 - ux * w * 2.4, y1 - uy * w * 2.4
    d.line([(x0, y0), (bx, by)], A(col, a), w); d.poly([(bx + nx * w * 1.6, by + ny * w * 1.6), (x1, y1), (bx - nx * w * 1.6, by - ny * w * 1.6)], A(col, a))
def cross(d, x, y, s, k, col, a=1.0):
    if k <= 0: return
    d.line([(x - s, y - s), (x - s + 2 * s * min(1, k * 2), y - s + 2 * s * min(1, k * 2))], A(col, a), s * 0.3)
    if k > 0.5: d.line([(x + s, y - s), (x + s - 2 * s * (k - 0.5) * 2, y - s + 2 * s * (k - 0.5) * 2)], A(col, a), s * 0.3)
def _unused_blink(t, t0, n=4, per=0.32):
    """blinking glow envelope: n flashes starting t0"""
    if t < t0: return 0.0
    u = (t - t0) / per; i = int(u)
    if i >= n: return 0.0
    f = u - i
    return math.exp(-f * 2.4) * (1 - 0.1 * i)
def zap(d, x, y, t, t0, col=WHITE, maxr=300, a=1.0):
    u = (t - t0) / 0.7
    if 0 <= u < 1:
        for j in range(3):
            rr_ = 30 + (u + j * 0.1) * maxr
            d.circ(x, y, rr_, outline=A(col, a * (1 - u) * (1 - j * 0.3)), w=10 - j * 3)

# ---------------- scenes ----------------
def stepbadge(d, t, t0, n, col=GOLD, x=540, y=330, total=3):
    for i in range(total):
        xx = x + (i - (total - 1) / 2) * 130
        on = i < n
        d.circ(xx, y, 50, fill=A(col if on else (60, 80, 110), 1))
        d.text(xx, y, str(i + 1), 54, A(NAVYT if on else (140, 160, 190), 1), k=1)
    k = popk(t, t0, "bouncy")
    if k > 0 and n > 0:
        xx = x + (n - 1 - (total - 1) / 2) * 130
        d.circ(xx, y, 50 + 30 * (1 - min(1, k)), outline=A(WHITE, 0.8 * (1 - min(1, k))), w=8)
def rampv(t, a, b): return E.ease_in_out_sine(pr(t, a, b))
def s_hook(t, d):
    sea(d, t, (20, 90, 140), (6, 30, 60))
    boxrig(d, t, 170)
    # whole 3-step squeeze in ~1.6 s
    e1 = rampv(t, -0.2, 0.3); e2 = rampv(t, 0.2, 0.6); b = rampv(t, 0.55, 1.3)
    ext = [0, 0, e1, e1, e2, e2, 0, 0]
    escape(d, t, 0.85, 170, ext, b, mood="sus" if t < 0.5 else ("scream" if t < 1.3 else "proud"))
    slamtxt(d, t, -0.2, "啵！", 380, 200, OCT_L)
    if t > 1.2: ptag(d, t, 1.2, 540, 560, "3 步出狱", GOLD, 60)
def s_q(t, d):
    sea(d, t)
    octo(d, 540, 1000, 1.3, t, mood="sus", look=math.sin(t * 2))
    kk = popk(t, T["q"] + 0.05, "bouncy")
    if kk > 0: d.text(540, 520, "?", int(300 * (0.6 + 0.4 * kk)), A(OCT_L, ap(t, T["q"])), k=1)
def s_reveal(t, d):
    rays(d, t, (255, 170, 140), (220, 90, 90))
    k = min(1.1, popk(t, BIG2, "bouncy"))
    octo(d, 540, 1000, 1.5 * (0.6 + 0.4 * k), t, mood="proud")
    slamtxt(d, t, BIG2, "先腕后头", 360, 160, WHITE)
    ptag(d, t, at("reveal", 2), 540, 520, "固定套路", NAVYT, 48, tc=WHITE)
def s_soft(t, d):
    sea(d, t, (30, 60, 100), (10, 20, 44))
    sq = 1 + 0.35 * math.sin((t - T["soft"]) * 3)
    octo(d, 540, 980, 1.2, t, mood="happy", sqx=sq, sqy=1 / sq)
    ptag(d, t, at("soft", 0.4), 540, 330, "软软软", OCT_L, 80)
    if t > at("soft", 4): ptag(d, t, at("soft", 4), 540, 470, "但有硬的", WHITE, 56)
def s_brain(t, d):
    sea(d, t, (30, 40, 80), (10, 12, 34))
    bv = ease(pr(t, at("brain", 0.3), at("brain", 1.5)))
    octo(d, 540, 1000, 1.6, t, mood="chill", brainvis=bv)
    if bv > 0.5:
        arrow(d, 820, 760, 660, 950, WHITE, ap(t, at("brain", 1.5)), 12)
        ptag(d, t, at("brain", 1.5), 820, 700, "软骨", CART, 56)
def s_eyes(t, d):
    sea(d, t, (30, 40, 80), (10, 12, 34))
    octo(d, 540, 1040, 1.8, t, mood="chill", brainvis=0.4)
    k = ease(pr(t, at("eyes", 0.5), at("eyes", 2)))
    if k > 0:
        x0, x1 = 540 - 104 * 1.0 * 1.8 * 0.56, 540 + 104 * 1.8 * 0.56
        y = 1040 - 18 * 1.8 - 90
        xm = lerp(540, x1, k); xl = lerp(540, x0, k)
        d.line([(xl, y), (xm, y)], A(GOLD, 1), 10)
        for xx in (xl, xm): d.line([(xx, y - 26), (xx, y + 26)], A(GOLD, 1), 10)
    ptag(d, t, at("eyes", 2.2), 540, 760, "两眼间距", GOLD, 56)
    if t > at("eyes", 4): ptag(d, t, at("eyes", 4), 540, 330, "≈ 软骨宽度", WHITE, 64)
def s_box(t, d):
    sea(d, t, (20, 60, 100), (6, 20, 44))
    hole = 150 if t < at("box", 5) else 110
    boxrig(d, t, hole)
    ptag(d, t, at("box", 0.3), 540, 330, "亚克力盒", ACR, 64)
    k = popk(t, at("box", 2), "bouncy")
    if k > 0:
        ht, hb = HY - hole / 2, HY + hole / 2
        d.line([(WX + 40, ht), (WX + 40, hb)], A(GOLD, 1), 8)
        tag(d, WX + 210, HY, "略大" if t < at("box", 5) else "略小", GOLD, ap(t, at("box", 2)), 48)
def s_who(t, d):
    sea(d, t, (30, 70, 110), (8, 24, 50))
    for i in range(3):
        kk = popk(t, at("who", 0.3 + i * 0.4), "bouncy")
        if kk > 0: octo(d, 280 + i * 260, 760, 0.55 * min(1, kk), t + i, mood="happy")
    for i in range(4):
        kk = popk(t, at("who", 2 + i * 0.4), "bouncy")
        if kk > 0: octo(d, 200 + i * 230, 1150, 0.5 * min(1, kk), t + i, mood="chill", col=MAYA, colD=MAYA_D, colL=MAYA_L)
    ptag(d, t, at("who", 0.3), 540, 520, "普通章鱼 ×3", OCT_L, 48)
    ptag(d, t, at("who", 2), 540, 975, "玛雅章鱼 ×4", MAYA_L, 48)
def s_big(t, d):
    sea(d, t, (20, 60, 100), (6, 20, 44))
    boxrig(d, t, 170)
    escape(d, t, 0.85, 170, None, 0, mood="sus", look=1)
    ptag(d, t, at("big", 0.3), 540, 330, "宽孔", GOLD, 80)
    if t > at("big", 2): ptag(d, t, at("big", 2), 540, 460, "三步走", WHITE, 60)
def s_s1(t, d):
    sea(d, t, (20, 60, 100), (6, 20, 44)); boxrig(d, t, 170)
    e = rampv(t, at("s1", 0.3), at("s1", 3))
    escape(d, t, 0.85, 170, [0, 0, 0, e, e * 0.8, 0, 0, 0], 0, mood="sus", look=1)
    stepbadge(d, t, T["s1"], 1)
    if e > 0.5: ptag(d, t, at("s1", 2.5), 860, 760, "1~2 条", WHITE, 40)
def s_s2(t, d):
    sea(d, t, (20, 60, 100), (6, 20, 44)); boxrig(d, t, 170)
    e = rampv(t, at("s2", 0.3), at("s2", 3))
    escape(d, t, 0.85, 170, [0, 0, e * 0.9, 1, 0.8, e, 0, 0], 0, mood="happy", look=1)
    stepbadge(d, t, T["s2"], 2)
    if e > 0.5: ptag(d, t, at("s2", 2.5), 860, 760, "再来几条", WHITE, 40)
def s_s3(t, d):
    sea(d, t, (20, 60, 100), (6, 20, 44)); boxrig(d, t, 170)
    push = pr(t, at("s3", 0.5), at("s3", 2))
    b = rampv(t, at("s3", 2), at("s3", 4.2))
    ext = [0, 0, 0.9, 1, 0.8, 1, 0, 0]
    hx, hy = escape(d, t, 0.85, 170, ext, b, mood="scream" if 0.2 < b < 0.8 else ("proud" if b >= 0.8 else "sus"), look=1)
    stepbadge(d, t, T["s3"], 3)
    if push > 0 and b < 0.3:
        for j in range(3): arrow(d, WX + 60, 700 + j * 200, WX + 20, 700 + j * 200, GOLD, push, 10)
        ptag(d, t, at("s3", 0.6), 860, 600, "撑！", GOLD, 56)
    if b > 0.2: slamtxt(d, t, at("s3", 2.2), "拽！", 480, 170, WHITE)
def s_fast(t, d):
    sea(d, t, (40, 80, 120), (10, 26, 50))
    octo(d, 760, 1060, 0.9, t, mood="proud")
    cx_, cy_ = 400, 900
    d.circ(cx_, cy_, 160, fill=A((248, 244, 230), 1)); d.rect(cx_ - 26, cy_ - 210, cx_ + 26, cy_ - 160, fill=A(OCT, 1), r=10)
    ang = -math.pi / 2 + pr(t, T["fast"], at("fast", 3)) * 2 * math.pi * 0.08
    d.line([(cx_, cy_), (cx_ + 120 * math.cos(ang), cy_ + 120 * math.sin(ang))], A(NAVYT, 1), 12)
    slamtxt(d, t, at("fast", 0.5), "几秒", 400, 170, GOLD)
def s_small(t, d):
    sea(d, t, (60, 40, 90), (20, 10, 40)); boxrig(d, t, 110)
    escape(d, t, 0.85, 110, None, 0, mood="sus", look=1)
    ptag(d, t, at("small", 0.3), 540, 330, "窄孔", (255, 130, 110), 80, tc=WHITE)
    if t > at("small", 2): ptag(d, t, at("small", 2), 540, 460, "第 4 步", WHITE, 60)
def s_s4a(t, d):
    sea(d, t, (60, 40, 90), (20, 10, 40)); boxrig(d, t, 110)
    ext = [rampv(t, at("s4a", 0.2 + i * 0.35), at("s4a", 1.6 + i * 0.35)) for i in range(8)]
    escape(d, t, 0.85, 110, ext, 0, mood="happy", look=1)
    stepbadge(d, t, T["s4a"], 3, total=4)
    n = sum(1 for e in ext if e > 0.6)
    d.text(860, 1180, f"{n}/8", 60, A(WHITE, 0.9), k=1)
def s_s4b(t, d):
    sea(d, t, (60, 40, 90), (20, 10, 40)); boxrig(d, t, 110)
    b = rampv(t, at("s4b", 0.4), at("s4b", 4.6))
    hx, hy = escape(d, t, 0.85, 110, [1] * 8, b, mood="scream" if b < 0.85 else "proud", look=1)
    stepbadge(d, t, T["s4b"], 4, total=4)
    if 0.25 < b < 0.75: ptag(d, t, at("s4b", 1.5), 860, 600, "挤……", WHITE, 48)
    if b > 0.9: slamtxt(d, t, at("s4b", 4.6), "出来了！", 480, 120, GOLD)
def s_maya(t, d):
    sea(d, t, (40, 70, 80), (14, 28, 36)); boxrig(d, t, 110)
    hx = 380
    octo(d, 380, HY + 40, 0.85, t, mood="chill" if t < at("maya", 3) else "sus", col=MAYA, colD=MAYA_D, colL=MAYA_L, look=1 if t < at("maya", 2.5) else -1)
    if t > at("maya", 3): bubble(d, 380, 640, "不钻", popk(t, at("maya", 3), "bouncy"), size=48)
    ptag(d, t, at("maya", 0.3), 540, 330, "玛雅章鱼", MAYA_L, 70)
def s_why(t, d):
    grad(d, (60, 120, 150), (20, 50, 70))
    d.poly([(-40, 1300)] + [(x, 1260 + 20 * math.sin(x / 80)) for x in range(-40, 1121, 40)] + [(1120, 2000), (-40, 2000)], A(SAND, 1))
    for i, (x, w) in enumerate(((180, 200), (820, 240))): d.ell(x, 1240, w, 120, A(ROCKC, 1))
    octo(d, 560, 1080, 0.8, t, mood="chill", col=MAYA, colD=MAYA_D, colL=MAYA_L)
    ptag(d, t, at("why", 0.3), 540, 330, "沙地 + 岩石", SAND, 64)
    if t > at("why", 2.5): stamp(d, t, at("why", 2.5), "推测", 540, 480, 100, (255, 150, 60))
def s_robot(t, d):
    grad(d, (40, 50, 70), (14, 18, 30))
    boxrig(d, t, 150)
    b = (t - T["robot"]) * 0.18 % 1
    # soft robot: grey octo-like blob with LED eyes
    escape(d, t, 0.8, 150, [cl(b * 3 - i * 0.2) for i in range(8)], cl(b * 2 - 0.9), mood="happy", col=(170, 186, 204), colD=(120, 134, 156), colL=(220, 230, 240), look=1)
    ptag(d, t, at("robot", 0.3), 540, 330, "软体机器人", MINT, 64, tc=NAVYT)
    if t > at("robot", 3): ptag(d, t, at("robot", 3), 540, 460, "团队的期望", WHITE, 44)
def s_card(t, d):
    grad(d, (30, 80, 110), (8, 30, 50))
    for i in range(12): d.circ(540, 860, 120 + i * 120, outline=A(WHITE, 0.04), w=30)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 690 * (0.8 + 0.2 * k), 980 * (0.8 + 0.2 * k); cx_, cy_ = 540, 840; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 80, "一句话学会", GOLD, a_, 32)
    octo(d, cx_, cy_ - 170, 0.5, t, mood="proud", a=a_)
    d.text(cx_, cy_ + 10, "章鱼钻孔：腕先出，头最后", 40, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("宽孔3步：1~2条腕→再几条→撑住一拽", "窄孔4步：所有腕先出→再挤头和外套膜", "尺子：两眼间距≈最硬的脑部软骨", "玛雅章鱼遇到窄孔通常不钻")):
        kk = popk(t, at("card", 1.2 + i * 1.6))
        if kk > 0: d.text(cx_, cy_ + 110 + i * 66, s_, 31, A((70, 70, 90), ap(t, at("card", 1.2 + i * 1.6))), k=1)
def s_end(t, d):
    sea(d, t, (20, 90, 140), (6, 30, 60)); boxrig(d, t, 170)
    t0 = at("end", 0.5)
    e1 = rampv(t, t0, t0 + 0.6); e2 = rampv(t, t0 + 0.6, t0 + 1.2); b = rampv(t, t0 + 1.3, t0 + 2.4)
    escape(d, t, 0.85, 170, [0, 0, e1, e1, e2, e2, 0, 0], b, mood="proud" if b > 0.8 else "sus", look=1)
    if b < 0.8: ptag(d, t, T["end"] + 0.05, 540, 300, "腕先出", OCT_L, 90)
    else: slamtxt(d, t, t0 + 2.4, "头最后！", 300, 130, GOLD)
    ra = ap(t, at("end", 5), 0.3)
    if ra > 0:
        d.rect(170, 395, 910, 505, fill=A((6, 20, 40), 0.6 * ra), r=20)
        d.text(540, 428, "Xin 等 2026 · J. Exp. Biol.", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 472, "实验室测试：3只普通章鱼 + 4只玛雅章鱼", 25, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "三步", "q": "挤出去", "reveal": "先出腕", "soft": "硬的", "brain": "软骨", "eyes": "两眼间距", "box": "略大或略小", "who": "玛雅章鱼",
      "big": "三步走", "s1": "一两条腕", "s2": "几条腕", "s3": "一把拽出", "fast": "几秒", "small": "加一步", "s4a": "所有腕", "s4b": "外套膜",
      "maya": "理都不理", "why": "推测", "robot": "软体机器人", "end": "头最后"}
def subs(t, d):
    for a, b, s, key in SUBS:
        if a <= t < b:
            ee = E.enter_exit(t, max(a, 0), b, 0.3, 0.12, rise=18, s0=0.96)
            al = ee["alpha"] if a > 0 else (1 - pr(t, b - 0.12, b))
            if al <= 0.01: return
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70 + ee["dy"] * (a > 0)
            w = max(d.tlen(x, 54, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 70 + 46, fill=A((6, 14, 26), 0.82 * al), r=22)
            hw = HL.get(key)
            for i, x in enumerate(ls):
                yy = y0 + i * 70
                if hw and hw in x:
                    j = x.index(hw); parts = [(x[:j], WHITE), (hw, GOLD), (x[j + len(hw):], WHITE)]
                    xx = 540 - d.tlen(x, 54, 1) / 2
                    for p_, c_ in parts:
                        if p_: d.text(xx, yy, p_, 54, A(c_, al), anchor="lm", k=1); xx += d.tlen(p_, 54, 1)
                else: d.text(540, yy, x, 54, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 怪奇动物"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)

SF = {n: globals()["s_" + n] for n in NAMES}
SECS = [(-1, HOOKCUT, s_hook, "hook")] + [(T[n], nxt(n), SF[n], n) for n in NAMES[1:]]
SECS = [(a, (99 if i == len(SECS) - 1 else b), f, n) for i, (a, b, f, n) in enumerate(SECS)]
def cam(t):
    z = 1.0 + 0.04 * pulse(t, [HOOK_HIT, BIG2], 3)
    for a, b, f, n in SECS:
        if a <= t < b: z += 0.03 * eio(pr(t, max(a, 0), min(b, DUR))); break
    sx, sy = shake(t, 8 * pulse(t, [HOOK_HIT, BIG2], 5), 40)
    return z, 540 + sx, 900 + sy
def frame(t, fi=0):
    img = Image.new("RGB", (W, H), (6, 20, 40)); d = D(img); key = None
    for a, b, sf, n in SECS:
        if a <= t < b: sf(t, d); key = n; break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.5 * (1 - (t - c) / 0.1)))
    brand(t, d); subs(t, d)
    out = img.resize((OW, OH), Image.LANCZOS)
    out = E.vignette(out, 0.2); out = E.grain(out, 0.03, seed=fi)
    return out
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/oc_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/oc_sheet.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                              "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", out], stdin=subprocess.PIPE)
        last = None; errs = 0
        for i in range(i0, i1):
            try: last = frame(i / FPS, i).tobytes()
            except Exception as e: errs += 1; print('ERR', i, e, file=sys.stderr)
            if last: p.stdin.write(last)
        p.stdin.close(); p.wait(); print('errs', errs, file=sys.stderr)
