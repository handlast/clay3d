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

def bubble_txt(d, t, t0, x, y, s, col, size=70, tail=-1):
    k = popk(t, t0, "bouncy")
    if k <= 0: return
    sz = int(size * min(1.1, k)); w = d.tlen(s, sz, 1) + 60
    d.rect(x - w / 2, y - sz * 0.85, x + w / 2, y + sz * 0.85, fill=A(WHITE, 0.97), r=sz * 0.6)
    d.poly([(x + tail * 30, y + sz * 0.7), (x + tail * 80, y + sz * 1.5), (x + tail * 70, y + sz * 0.7)], A(WHITE, 0.97))
    d.text(x, y, s, sz, A(col, 1), k=1)
# ---------------- scenes ----------------
def ramp(t, a, b): return E.ease_in_out_sine(pr(t, a, b))
def garden(d, t, top=(70, 120, 80), bot=(24, 50, 34), ground=1350):
    flatbg(d, top, bot, t, False)
    d.rect(0, ground, 1080, 1920, fill=A((70, 52, 40), 1))
    for i in range(10):
        rv = random.Random(i); d.circ(rv.uniform(0, 1080), ground + rv.uniform(20, 500), rv.uniform(10, 30), fill=A((90, 70, 52), 1))
def check(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 18 * s_, y), (x - 4 * s_, y + 14 * s_), (x + 20 * s_, y - 14 * s_)], A(WHITE, a), 8 * s_)
def xmark(d, x, y, r, col, a=1.0, k=1.0):
    if k <= 0: return
    d.circ(x, y, r * min(1, k), fill=A(col, a)); s_ = r * min(1, k) / 40
    d.line([(x - 15 * s_, y - 15 * s_), (x + 15 * s_, y + 15 * s_)], A(WHITE, a), 8 * s_); d.line([(x - 15 * s_, y + 15 * s_), (x + 15 * s_, y - 15 * s_)], A(WHITE, a), 8 * s_)
def heart(d, x, y, r, col, a=1.0):
    d.circ(x - r * 0.5, y - r * 0.2, r * 0.55, fill=A(col, a)); d.circ(x + r * 0.5, y - r * 0.2, r * 0.55, fill=A(col, a))
    d.poly([(x - r * 1.02, y - 0.05 * r), (x + r * 1.02, y - 0.05 * r), (x, y + r * 1.1)], A(col, a))
def puddle(d, x, y, w, a=1.0): d.ell(x, y, w, w * 0.18, A((90, 170, 240), 0.85 * a))
def arrow_up(d, x, y0, y1, col, a=1.0, w=14):
    d.line([(x, y0), (x, y1 + 30)], A(col, a), w); d.poly([(x - 34, y1 + 40), (x + 34, y1 + 40), (x, y1)], A(col, a))

def screen(d, *a, **k): pass
def night(d, t, top=(10, 14, 40), bot=(40, 40, 90)): flatbg(d, top, bot, t, False); stars(d, t)
def s_hook(t, d):
    night(d, t)
    if t < 0.3: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - t / 0.3)))
    shower(d, t, 40, 1.6, 640, 300, a=1.0)
    mountains(d, (16, 20, 44), 1180)
    person(d, 540, 860, 1.0, t, face="shock")
    k = popk(t, 0.4, "bouncy")
    if k > 0: tag(d, 540, 330, "每分钟几千颗", GOLD, min(1, k), 56)
def s_q(t, d):
    t0 = T["q"]
    night(d, t); leo(d, 380, 640, 1.2, ap(t, t0 + 0.2, 0.4))
    ptag(d, t, t0 + 0.6, 540, 360, "狮子座", GOLD, 52)
    k = popk(t, t0 + 1.4, "bouncy")
    if k > 0:
        d.rect(300, 920, 780, 1110, fill=A((250, 246, 234), min(1, k)), r=28)
        d.text(540, 950, "11月18日", 52, A(NAVYT, min(1, k)), k=1); d.text(540, 1030, "08:00 极大", 46, A((220, 90, 60), min(1, k)), k=1)
def s_who(t, d):
    t0 = T["who"]
    night(d, t, (16, 10, 50), (50, 30, 90))
    u = ease(pr(t, t0, t0 + 3.5)); cx_ = 820 - 500 * u
    comet(d, cx_, 640, 1.0, t, ang=0.15)
    rv = random.Random(2)
    for i in range(40):
        x = cx_ + 60 + rv.uniform(0, 600) * u + 40; y = 640 + rv.uniform(-60, 120)
        if x < 1100: d.circ(x, y, rv.uniform(3, 7), fill=A(DUST, 0.8))
    ptag(d, t, t0 + 1.4, 760, 900, "尘埃", DUST, 44)
def s_sperm(t, d):
    t0 = T["sperm"]
    night(d, t)
    d.ell(540, 760, 420, 200, A(WHITE, 0.0)); d.arc(540, 760, 420, 200, 0, 360, A((120, 140, 200), 0.6), 4)
    sun(d, 260, 760, 0.6, t)
    u = pr(t, t0, t0 + 3.6); ang = math.pi + u * 2 * math.pi
    cx_, cy_ = 540 + 420 * math.cos(ang), 760 + 200 * math.sin(ang)
    comet(d, cx_, cy_, 0.5, t, ang=math.atan2(cy_ - 760, cx_ - 260))
    k = popk(t, t0 + 0.8, "bouncy")
    if k > 0: tag(d, 540, 380, "每 33 年一圈", GOLD, min(1, k), 52)
def s_egg(t, d):
    t0 = T["egg"]
    night(d, t)
    dim = 1 - 0.5 * pr(t, SIL0, SIL0 + 0.1)
    rv = random.Random(9)
    for i in range(90): d.circ(rv.uniform(0, 1080), 760 + rv.uniform(-140, 140), rv.uniform(3, 7), fill=A(DUST, 0.7 * dim))
    u = ease(pr(t, t0 + 0.2, t0 + 4.4)); earth(d, 160 + 260 * u, 760, 1.0, t, a=dim)
    if t < SIL0: ptag(d, t, t0 + 1.0, 540, 480, "11月 · 每年一次", WHITE, 40)
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (90, 80, 200), (30, 20, 90))
    if t > t0: sparks(d, 540, 760, t, t0, 30, 900, (255, 240, 200), 1, 3, 0.9)
    earth(d, 540, 820, 1.6, t, face="shock")
    rv = random.Random(4)
    for i in range(10):
        u = ((t - t0) * 2.2 + rv.random()) % 1; y = 560 - 380 * (1 - u); x = 300 + rv.uniform(0, 480)
        streak(d, x, y + 160, math.pi / 2, 160, 1 - u * 0.5, w=6)
    k = popk(t, t0 + 0.4, "bouncy")
    if k > 0: tag(d, 540, 400, "71 公里/秒", WHITE, min(1, k), 100)
def s_how(t, d):
    t0 = T["how"]
    night(d, t); mountains(d, (16, 20, 44), 1250)
    u = ease(pr(t, t0 + 0.2, t0 + 0.7))
    streak(d, 300 + 500 * u, 300 + 400 * u, math.atan2(400, 500), 640 * u, 1, w=8)
    tr = pr(t, t0 + 0.8, t0 + 4.0)
    if tr > 0:
        for i in range(30):
            v = i / 30; x = 300 + 500 * v; y = 300 + 400 * v + math.sin(v * 6 + tr * 3) * 30 * tr
            d.circ(x, y, 8, fill=A((150, 230, 200), 0.6 * (1 - tr * 0.6)))
        ptag(d, t, t0 + 1.0, 760, 880, "发光余迹", (150, 230, 200), 44)
    tag(d, 540, 1000, "年度最快", GOLD, ap(t, t0 + 0.4), 44)
def s_xray(t, d):
    t0 = T["xray"]
    night(d, t)
    rv = random.Random(3)
    for i in range(60): d.circ(rv.uniform(0, 1080), 520 + rv.uniform(-50, 50), 4, fill=A(DUST, 0.4))
    tag(d, 160, 440, "旧尘埃", DUST, 1, 32)
    k = ap(t, t0 + 0.6, 0.4)
    for i in range(220): d.circ(rv.uniform(0, 1080), 900 + rv.uniform(-60, 60), 5, fill=A((255, 240, 200), 0.9 * k))
    ptag(d, t, t0 + 1.0, 180, 800, "新鲜密集", (255, 240, 200), 32)
    u = ease(pr(t, t0 + 1.2, t0 + 3.8)); earth(d, 540, 900 - 0 * u + (1 - u) * -300 + 0, 0.6, t, face="shock" if u > 0.7 else "happy")
def s_swim(t, d):
    t0 = T["swim"]
    night(d, t)
    shower(d, t, 60, 2.2, 540, 260, seed=12)
    mountains(d, (16, 20, 44), 1250)
    k = popk(t, t0 + 0.2, "bouncy")
    if k > 0: tag(d, 540, 900, "1966 · 15 分钟", GOLD, min(1, k), 52)
def s_gene(t, d):
    t0 = T["gene"]
    night(d, t)
    for i in range(15):
        kk = popk(t, t0 + 0.3 + i * 0.1)
        if kk > 0: streak(d, 260 + (i % 5) * 140, 420 + (i // 5) * 170, 0.8, 90 * min(1, kk), 1, w=5)
    ptag(d, t, t0 + 2.0, 540, 1000, "约 15 颗 / 小时", WHITE, 50)
    ptag(d, t, t0 + 2.4, 540, 1090, "理想天空 · 理论值", GOLD, 32)
def s_why(t, d):
    t0 = T["why"]
    night(d, t); mountains(d, (16, 20, 44), 1250)
    shower(d, t, 3, 0.6, 640, 300, seed=21)
    person(d, 540, 880, 1.0, t, face="look")
    ptag(d, t, t0 + 0.5, 540, 380, "郊外 8–12 颗", (150, 230, 200), 46)
    ptag(d, t, t0 + 1.4, 540, 470, "城里 2–4 颗", (200, 200, 220), 36)
def s_order(t, d):
    t0 = T["order"]
    k = pr(t, t0, t0 + 4.0)
    flatbg(d, mix((10, 14, 40), (60, 90, 160), k), mix((40, 40, 90), (250, 170, 120), k), t, False); stars(d, t, 1 - k)
    mountains(d, (16, 20, 44), 1250)
    leo(d, 300 + 200 * k, 760 - 300 * k, 0.8, 1 - 0.5 * k)
    hrs = 2 + int(4 * k)
    d.rect(330, 900, 750, 1060, fill=A((250, 246, 234), 1), r=24)
    d.text(540, 935, f"18日 凌晨 {hrs}:00", 48, A(NAVYT, 1), k=1)
    ptag(d, t, t0 + 0.8, 540, 380, "越往后越多", GOLD, 46)
def s_card(t, d):
    flatbg(d, (30, 30, 80), (12, 12, 34), t, False)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    comet(d, cx_ + 60, cy_ - 160, 0.6, t, a=a_, ang=0.2)
    d.text(cx_, cy_ + 10, "流星雨＝地球穿过彗星尘埃", 42, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("狮子座：每秒 71 公里", "今年每小时约 15 颗", "18日凌晨看，越近天亮越多")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 120 + i * 78, s_, 38, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    night(d, t)
    comet(d, 760, 420, 0.7, t, ang=-0.4)
    earth(d, 400, 860, 1.2, t)
    shower(d, t, 10, 1.2, 400, 700, seed=5)
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 285, "北京日报 2026-11-01 · NASA Leonids", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 330, "IMO 2026 预报 · Planetary Society", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "几千颗", "q": "8点", "who": "尘埃", "sperm": "33年", "egg": "11月", "reveal": "71公里", "how": "最快",
      "xray": "流星暴", "swim": "几千颗", "gene": "15颗", "why": "8到12颗", "order": "越往后越多", "end": "迎面撞上"}
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
    s = "Vibe 知识大赏 · 怪奇天象"; w = d.tlen(s, 28, 1) + 50
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
    img = Image.new("RGB", (W, H), (20, 40, 30)); d = D(img); key = None
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/lo_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/lo_sheet.png")
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
