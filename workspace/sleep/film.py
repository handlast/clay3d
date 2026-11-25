import sys, subprocess
from doodle import *
from cues import *
PURP = (150, 90, 170); GREENS = (60, 150, 80); RED = (220, 60, 50)
def tired_at(t): return cl((t - DAY0 + 2) / 26, 0, 1.0)

def daypage(d, t, n, x=880, y=300):
    box(d, x - 110, y - 100, x + 110, y + 110, t, RED, 10, 1, 900, fill=WHITE)
    d.rect(x - 110, y - 100, x + 110, y - 50, fill=A(RED, 1))
    d.text(x, y - 74, "DAY", 32, A(WHITE, 1), k=1); d.text(x, y + 30, str(n), 110, A(INKC, 1), k=1)

def s_hook(t, d):
    paper(d, t)
    k = pop(t, HOOK_HIT)
    wob = math.sin(t * 2) * 6
    stick(d, 540 + wob, 1400, 200, t, "stand", hat=False, hair=True, tired=0.9, mood="o")
    for j in range(3):  # zzz denied
        zx = 760 + j * 50; zy = 900 - j * 60 - (t * 40) % 40
        dtext(d, zx, zy, "Z", 60 - j * 10, PURP, 0.8, t, 10 + j)
    ink(d, [(720, 760), (900, 960)], t, RED, 12, 1, 15)
    dtext(d, 540, 300, "如果 11 天不睡觉", 96, INKC, 1, t, 1)
    if k > 0: d.text(540, 480, "264 小时", int(200 * (0.6 + 0.4 * k)) + 1, A(RED, min(1, k * 1.5)), k=1)
    if t > 1.8: dtext(d, 540, 650, "真有人试过", 66, INKC, ease(pr(t, 1.8, 2.1)), t, 2)

def s_who(t, d):
    paper(d, t)
    k = pop(t, WHO_HIT)
    stick(d, 400, 1420, 200, t, "up", hat=False, hair=True, mood="ok")
    stick(d, 820, 1420, 150, t, "stand", hat=False, mood="ok", seed=40)  # scientist
    box(d, 760, 1100, 880, 1180, t, INKC, 6, 1, 41, fill=WHITE)
    d.text(820, 1140, "睡眠专家", 26, A(INKC, 1), k=1)
    dtext(d, 540, 330, "1964 · 17 岁", 96, INKC, min(1, k * 1.5), t, 3)
    dtext(d, 540, 480, "Randy Gardner", 80, GREENS, min(1, k * 1.5), t, 4)

def day_scene(k, t, d, ts, tb):
    hit = tb <= t < tb + 0.4; after = t >= tb
    tr = tired_at(t); px, py, s = 380, 1430, 180
    sway = math.sin(t * (1.5 + k * 0.3)) * 6 * (1 + k)
    pose = "zap" if hit else "stand"
    mood = {0: "o", 1: "sad", 2: "o", 3: "o", 4: "sad", 5: "sad", 6: "sad", 7: "ok", 8: "sad"}[k]
    if k == 0 and after:
        stick(d, px + sway + 26, py, s, t, pose, hat=False, hair=True, tired=tr, mood=mood, col=(170, 180, 210), seed=77)
    stick(d, px + sway, py, s, t, pose, hat=False, hair=True, tired=tr, mood=mood)
    hx, hy = px + sway, py - 2.25 * s
    def bub(txt, a=1.0, x=760, y=820, size=54):
        w_ = d.tlen(txt, size) + 60
        d.rect(x - w_ / 2, y - 60, x + w_ / 2, y + 60, fill=A(WHITE, a), r=40)
        ink(d, [(x - w_ / 2 + 40, y + 55), (hx + 60, hy - 30)], t, INKC, 6, a, 950)
        d.text(x, y, txt, size, A(INKC, a), k=1)
    a = ease(pr(t, tb, tb + 0.3))
    if k == 0 and after:
        for sx in (-1, 1): ring(d, hx + sx * 22, hy - 4, 26, t, RED, 6, a, 960 + sx)
    if k == 1 and after: bub("吃葡萄不吐…葡吐萄…", a, 680, 800)
    if k == 2:  # sign becomes person
        sx = 800
        ink(d, [(sx, 1430), (sx, 1000)], t, (120, 120, 130), 14, 1, 970)
        d.rect(sx - 110, 880, sx + 110, 1010, fill=A((60, 150, 90), 1), r=12)
        if after:
            d.circ(sx - 40, 935, 12, fill=A(WHITE, 1)); d.circ(sx + 40, 935, 12, fill=A(WHITE, 1))
            d.arc(sx, 960, 40, 22, 20, 160, A(WHITE, 1), 7)
            wv = math.sin(t * 8) * 0.4
            ink(d, [(sx + 110, 950), (sx + 190, 880 + 40 * wv)], t, INKC, 9, a, 971)
            dtext(d, sx + 10, 790, "嗨！", 60, INKC, a, t, 972)
        else: d.text(sx, 945, "STOP", 50, A(WHITE, 1), k=1)
    if k == 3 and after:
        d.poly([(640, 1450), (1000, 1450), (900, 900), (820, 900)], A((220, 200, 150), a))
        for j in range(5):
            tx = 600 + j * 110 + (j % 2) * 40; ty = 1300 - j * 70
            ink(d, [(tx, ty + 110), (tx, ty)], t, WOOD, 10, a, 980 + j)
            d.poly([(tx - 60, ty + 40), (tx + 60, ty + 40), (tx, ty - 120)], A((90, 160, 90), a))
    if k == 4:
        ring(d, 780, 1100, 70, t, (200, 60, 60), 8, 1, 990, fill=(230, 80, 70)); ink(d, [(780, 1030), (790, 990)], t, WOOD, 8, 1, 991)
        if after: bub("这个…叫啥来着？", a, 760, 820)
    if k == 5 and after:
        bub("呜…啦…窝…", a, 720, 800)
        for j in range(3):
            fa = a * (1 - pr(t, tb + 0.6 + j * 0.4, tb + 0.9 + j * 0.4))
            dtext(d, 640 + j * 130, 1050, ["钥匙", "作业", "名字"][j], 48, INKC, fa, t, 995 + j)
    if k == 6 and after: bub("我刚才想说的是……", a, 700, 800)
    if k == 7:
        # radio (paranoia) + pinball WIN
        box(d, 640, 900, 800, 1000, t, INKC, 8, 1, 1000, fill=(200, 170, 120)); ring(d, 690, 950, 30, t, INKC, 6, 1, 1001)
        if after:
            d.circ(750, 935, 8, fill=A(RED, 1)); d.circ(780, 935, 8, fill=A(RED, 1)); dtext(d, 720, 850, "?!", 50, RED, a, t, 1002)
        if t > tb + 1.2:
            b = ease(pr(t, tb + 1.2, tb + 1.5))
            box(d, 780, 1100, 1000, 1430, t, INKC, 9, b, 1003, fill=(120, 100, 200))
            d.text(890, 1170, "WIN", 60, A((255, 220, 60), b), k=1)
            for j in range(3): d.circ(830 + j * 40, 1300 + 30 * math.sin(t * 6 + j), 12, fill=A(WHITE, b))
    if k == 8 and after:
        nums = ["100", "93", "86", "79", "72", "65"]
        box(d, 600, 760, 1020, 1240, t, (60, 110, 80), 10, 1, 1010, fill=(70, 120, 90))
        for j, nn in enumerate(nums):
            if t > tb + j * 0.28: d.text(700 + (j % 2) * 200, 830 + (j // 2) * 120, nn, 64, A(WHITE, 1), k=1)
        if t > tb + 1.9: d.text(810, 1190, "……?", 64, A((255, 220, 60), 1), k=1)

def s_days(t, d):
    paper(d, t)
    k = min(8, int((t - DAY0) / DDUR)); ts = DAY0 + k * DDUR; tb = DHITS[k]
    day_scene(k, t, d, ts, tb)
    kk = pop(t, ts, 0.2)
    daypage(d, t, DAYS[k])
    txt = DTXT[k][1]
    if t > tb: dtext(d, 470, 470, txt if len(txt) < 12 else txt[:txt.index('，')] if '，' in txt else txt, 64, RED, ease(pr(t, tb, tb + 0.2)), t, 600 + k)
    # 264h progress bar
    hrs = (DAYS[k] - 1 + pr(t, ts, ts + DDUR)) * 24
    d.rect(140, 600, 940, 640, fill=A((220, 215, 200), 1), r=20); d.rect(140, 600, 140 + 800 * min(1, hrs / 264), 640, fill=A(PURP, 1), r=20)
    d.text(540, 690, f"已清醒 {int(hrs)} 小时", 40, A(INKC, 1), k=1)

def s_sleep(t, d):
    paper(d, t)
    d.rect(0, 0, OW, OH, fill=A((40, 50, 100), 0.25 * ease(pr(t, SLEEP, SLEEP + 0.5))))
    box(d, 180, 1250, 900, 1400, t, INKC, 10, 1, 1100, fill=(240, 200, 200)); box(d, 180, 1180, 360, 1260, t, INKC, 8, 1, 1101, fill=WHITE)
    ring(d, 300, 1170, 60, t, INKC, 9, 1, 1102, fill=PAPER)
    for sx in (-1, 1): d.arc(300 + sx * 22, 1170, 14, 8, 0, 180, A(INKC, 1), 5)
    for j in range(4):
        zt = (t * 0.8 + j * 0.25) % 1
        dtext(d, 400 + zt * 300 + j * 20, 1100 - zt * 400, "Z", int(50 + zt * 60), PURP, 1 - zt, t, 1103 + j)
    k = pop(t, SLEEP_HIT)
    if k > 0: d.text(540, 420, "14 小时 46 分", int(130 * (0.6 + 0.4 * k)) + 1, A(PURP, min(1, k * 1.5)), k=1)
    dtext(d, 540, 280, "终于睡了", 80, INKC, 1, t, 1110)

def s_guin(t, d):
    paper(d, t)
    k = pop(t, GUIN_HIT)
    stick(d, 540, 1400, 170, t, "stand", hat=False, hair=True, mood="ok")
    if k > 0:
        d.rect(120, 330, 960, 640, fill=A(RED, min(1, k)), r=30)
        d.text(540, 420, "吉尼斯：不收了", int(90 * (0.6 + 0.4 * k)) + 1, A(WHITE, min(1, k * 1.5)), k=1)
        d.text(540, 550, "1997 年起，因为太危险", int(56 * (0.6 + 0.4 * k)) + 1, A(WHITE, min(1, k * 1.5)), k=1)
    ring(d, 540, 1000, 260, t, RED, 16, ease(pr(t, GUIN_HIT + 0.3, GUIN_HIT + 0.6)), 1200)
    ink(d, [(356, 816), (724, 1184)], t, RED, 16, ease(pr(t, GUIN_HIT + 0.3, GUIN_HIT + 0.6)), 1201)
    dtext(d, 540, 1520, "别学", 90, RED, ease(pr(t, GUIN_HIT + 0.8, GUIN_HIT + 1.1)), t, 1202)

def bubble(d, x, y, s, side, col, tcol, a, size=50):
    w = d.tlen(s, size) + 70; x0 = x - w if side > 0 else x
    d.rect(x0, y - size * 1.1, x0 + w, y + size * 1.1, fill=A(col, a), r=40); d.text(x0 + w / 2, y, s, size, A(tcol, a), k=1)
def s_end(t, d):
    paper(d, t)
    d.rect(0, 160, 1080, 260, fill=A(INKC, 1)); d.text(540, 210, "同学群（48）", 44, A(WHITE, 0.95), k=1)
    d.text(540, 380, "明天这样说 ↓", 80, A(RED, ease(pr(t, OUTRO, OUTRO + 0.3))), k=1)
    if t > BUB1: bubble(d, 1010, 640, "有人 11 天没睡觉", 1, (120, 220, 120), (20, 40, 20), min(1, pop(t, BUB1)), 56)
    if t > BUB1 + 0.6: bubble(d, 1010, 830, "第 4 天把路牌看成了人", 1, (120, 220, 120), (20, 40, 20), min(1, pop(t, BUB1 + 0.6)), 56)
    if t > BUB2: bubble(d, 70, 1020, "那我熬夜打游戏算啥", -1, (90, 100, 130), WHITE, min(1, pop(t, BUB2)), 54)
    if t > BUB2 + 0.7: bubble(d, 1010, 1210, "算你在慢慢变成他", 1, (120, 220, 120), (20, 40, 20), min(1, pop(t, BUB2 + 0.7)), 52)
    d.text(540, 1780, "Ross 1965, Arch Neurol 12:399 · Coren 1998, Psychiatric Times", 24, A(INKC, 0.75), k=0)
    d.text(540, 1815, "Gulevich et al. 1966, Arch Gen Psychiatry · Guinness World Records", 24, A(INKC, 0.75), k=0)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

SECS = [(0, HOOK_END, s_hook), (WHO, DAY0, s_who), (DAY0, SLEEP, s_days), (SLEEP, GUIN, s_sleep), (GUIN, OUTRO, s_guin), (OUTRO, 99, s_end)]
CUTS = [HOOK_END, DAY0, SLEEP, GUIN, OUTRO] + [DAY0 + k * DDUR for k in range(1, 9)]
def cam(t):
    z = 1.0 + 0.06 * pulse(t, HITS, 7)
    for a, b in RISERS:
        if a <= t < b: z += 0.08 * eio(pr(t, a, b))
    rot = tired_at(t) if DAY0 <= t < SLEEP else 0
    amp = 22 * pulse(t, [HOOK_HIT, DHITS[2]], 4) + 8 * pulse(t, HITS, 6)
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx + math.sin(t * 1.3) * 18 * rot, 960 + sy
def frame(t):
    img = Image.new("RGB", (W, H), PAPER); d = D(img)
    for a, b, sf in SECS:
        if a <= t < b: sf(t, d); break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    # blink: eyelids close briefly more often as fatigue grows
    if DAY0 <= t < SLEEP:
        tr = tired_at(t); per = 4.0 - 2.5 * tr; ph = (t % per) / per
        if ph > 1 - 0.06 * (1 + tr):
            u = math.sin(math.pi * (ph - (1 - 0.06 * (1 + tr))) / (0.06 * (1 + tr)))
            d.rect(0, 0, OW, OH * 0.5 * u, fill=A((40, 50, 90), 0.85)); d.rect(0, OH * (1 - 0.5 * u), OW, OH, fill=A((40, 50, 90), 0.85))
    for c in CUTS:
        if c <= t < c + 0.08: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.5 * (1 - (t - c) / 0.08)))
    if SILENCES[0][0] <= t < SILENCES[0][1]: d.rect(0, 0, OW, OH, fill=A((40, 50, 90), 0.5))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.1f}.png")
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
