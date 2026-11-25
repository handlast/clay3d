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
def sea(d, t, top=SEA1, bot=SEA2): flatbg(d, top, bot, t, False); bubbles(d, t)
def s_hook(t, d):
    flatbg(d, (120, 40, 50), (50, 16, 30), t, False)
    if t < 0.3: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - t / 0.3)))
    fall = E.ease_in_out_sine(pr(t, 1.3, 1.9))
    d.rect(250, 1120, 830, 1150, fill=A((90, 50, 40), 1), r=12)
    # plate with fugu sashimi
    d.ell(700, 1100, 120, 30, A((240, 240, 245), 1))
    for i in range(5): d.ell(640 + i * 30, 1092, 26, 12, A((250, 240, 235), 0.9))
    face = "chew" if t < 1.3 else "dead"
    dragongod(d, 440, 760, 1.25, t, face=face, fall=fall)
    if t < 1.3:
        u = pr(t, 0.2, 0.7); d.ell(lerp(700, 470, u), lerp(1092, 760, u), 26, 12, A((250, 240, 235), 1 - pr(t, 0.7, 0.8)))
    k = popk(t, 1.9, "bouncy")
    if k > 0: tag(d, 540, 360, "龙神 0 : 1 河豚", GOLD, min(1, k), 58)
def s_q(t, d):
    t0 = T["q"]
    sea(d, t, (40, 110, 150), (10, 40, 80))
    puffer(d, 540, 620, 2.4, t, puff=0.0)
    for i in range(7):
        k = popk(t, t0 + 0.6 + i * 0.18)
        if k > 0:
            x = 330 + i * 70; y = 1000 + (i % 2) * 50
            egg_f(d, x, y, 30 * min(1.2, k), skull=True)
    ptag(d, t, t0 + 1.4, 540, 1130, "卵里有河豚毒素 TTX", TTXM, 40, tc=WHITE)
def s_who(t, d):
    t0 = T["who"]
    sea(d, t)
    larva(d, 540, 740, 2.6, t, glow=TTXM)
    k = popk(t, t0 + 0.8, "bouncy")
    if k > 0:
        d.text(800, 520, "?", 160, A(GOLD, min(1, k)), k=1)
    ptag(d, t, t0 + 1.2, 540, 1030, "2026 新研究", WHITE, 40)
def s_sperm(t, d):
    t0 = T["sperm"]
    sea(d, t)
    gulp = pr(t, t0 + 1.4, t0 + 1.8)
    predator(d, 330, 760, 1.0, t, kind="gir", mouth=0.8 * (1 - gulp) + 0.2, flip=1, face="hungry")
    lx = lerp(820, 480, ease(pr(t, t0 + 0.2, t0 + 1.6)))
    if gulp < 1: larva(d, lx, 780, 0.9, t, glow=TTXM, flip=-1, face="scared")
    if gulp >= 1: ptag(d, t, t0 + 2.0, 330, 560, "咕嘟", WHITE, 44)
    tag(d, 540, 1040, "剧毒 TTX 宝宝", TTXM, ap(t, t0 + 0.3), 40, tc=WHITE)
def s_egg(t, d):
    t0 = T["egg"]
    sea(d, t)
    dim = 1 - 0.45 * pr(t, SIL0, SIL0 + 0.15)
    predator(d, 330, 760, 1.0, t, kind="gir", mouth=0.9, flip=1, a=dim)
    lx = lerp(820, 500, ease(pr(t, t0 + 0.2, t0 + 3.6)))
    larva(d, lx, 780, 0.9, t, glow=TDTG, flip=-1, a=dim)
    tag(d, 540, 1040, "几乎无毒 TDT 宝宝", TDTG, ap(t, t0 + 0.3) * dim, 40)
def s_reveal(t, d):
    t0 = BIG2
    rays(d, t, (60, 170, 140), (12, 60, 70))
    if t > t0: sparks(d, 600, 760, t, t0, 30, 900, (200, 255, 220), 1, 3, 0.9)
    predator(d, 400, 820, 1.7, t, kind="gir", mouth=0.9, face="yuck", flip=1)
    u = ease(pr(t, t0, t0 + 0.5)); larva(d, lerp(640, 900, u), lerp(840, 560, u), 1.4, t, glow=TDTG, flip=1)
    k = popk(t, t0 + 0.1, "bouncy")
    if k > 0: tag(d, 540, 400, "呸！", WHITE, min(1, k), 120)
def s_how(t, d):
    t0 = T["how"]
    sea(d, t, (30, 90, 90), (8, 34, 44))
    d.circ(540, 760, 260, fill=A(TDTG, 0.12))
    larva(d, 540, 760, 4.2, t)
    rv = random.Random(8)
    for i in range(46):
        kk = ap(t, t0 + 0.4 + i * 0.04, 0.2)
        if kk > 0:
            ang = rv.uniform(0, 2 * math.pi); rr = rv.uniform(0.6, 0.98)
            d.circ(540 + math.cos(ang) * 190 * rr, 760 + math.sin(ang) * 150 * rr, 9, fill=A(TDTG, kk))
    ptag(d, t, t0 + 1.6, 540, 1060, "表皮", TDTG, 44)
def s_xray(t, d):
    t0 = T["xray"]
    sea(d, t)
    predator(d, 540, 760, 1.3, t, kind="gir", mouth=0.6, face="yuck" if t > t0 + 1.2 else "hungry", flip=1)
    k = popk(t, t0 + 1.0, "bouncy")
    if k > 0: bubble_txt(d, t, t0 + 1.0, 540, 480, "苦！难吃！", NAVYT, 56)
    u = ease(pr(t, t0 + 1.4, t0 + 2.0)); larva(d, lerp(720, 920, u), lerp(780, 980, u), 0.9, t, glow=TDTG)
def s_swim(t, d):
    t0 = T["swim"]
    sea(d, t, (60, 110, 120), (20, 50, 60))
    d.rect(0, 1150, OW, 1300, fill=A((200, 180, 140), 0.5))
    predator(d, 540, 1000, 1.2, t, kind="flo", mouth=0.5, face="yuck", flip=1)
    for i, (c, lab) in enumerate(((TTXM, "TTX"), (TDTG, "TDT"))):
        x = 330 + i * 420; kk = popk(t, t0 + 0.4 + i * 0.5)
        if kk > 0:
            larva(d, x, 560, 0.9, t, glow=c); tag(d, x, 700, lab, c, min(1, kk), 36, tc=WHITE if i == 0 else NAVYT)
            check(d, x, 440, 34, TDTG, min(1, kk))
    ptag(d, t, t0 + 1.4, 540, 340, "两种都吐", GOLD, 44)
def s_gene(t, d):
    t0 = T["gene"]
    sea(d, t, (20, 50, 100), (6, 20, 50))
    rv = random.Random(4)
    for i in range(14): larva(d, rv.uniform(200, 880), rv.uniform(620, 920), 0.5, t + i)
    for i, (c, lab, x) in enumerate(((TTXM, "剧毒", 320), (TDTG, "难吃警报", 760))):
        kk = popk(t, t0 + 0.3 + i * 0.9, "bouncy")
        if kk > 0:
            s_ = min(1, kk)
            d.poly([(x - 110 * s_, 420), (x + 110 * s_, 420), (x + 110 * s_, 520), (x, 600 * s_ + 420 * (1 - s_)), (x - 110 * s_, 520)], A(c, 0.9))
            d.text(x, 470, lab, 40, A(WHITE if i == 0 else NAVYT, s_), k=1)
    ptag(d, t, t0 + 2.4, 540, 1040, "第 1 道 + 第 2 道", WHITE, 40)
def s_why(t, d):
    t0 = T["why"]
    sea(d, t, (40, 100, 140), (10, 40, 70))
    for i in range(4):
        r = 60 + ((t - t0) * 120 + i * 70) % 280
        d.arc(260, 760, r, r, -40, 40, A(TDTG, 0.6 * (1 - r / 340)), 6)
    d.circ(200, 760, 26, fill=A(TDTG, 0.9))
    u = ease(pr(t, t0 + 0.3, t0 + 3.0)); puffer(d, lerp(820, 560, u), 760, 1.4, t, face="love", flip=-1)
    if t > t0 + 1.5: heart(d, 640, 560, 30 + 6 * math.sin(t * 8), (255, 120, 150), 1)
    ptag(d, t, t0 + 0.6, 540, 1040, "河豚闻 TDT：香", TDTG, 40)
def s_order(t, d):
    t0 = T["order"]
    sea(d, t)
    larva(d, 540, 700, 2.4, t, glow=TDTG)
    k = popk(t, t0 + 0.4, "bouncy")
    if k > 0:
        d.rect(600 - 10, 520, 820, 600, fill=A((250, 246, 234), min(1, k)), r=16)
        d.text(705, 538, "难吃", 40, A((220, 70, 60), min(1, k)), k=1)
    ptag(d, t, t0 + 1.2, 540, 1020, "吐出来 = 活下来", GOLD, 46)
def s_card(t, d):
    flatbg(d, (20, 70, 100), (8, 28, 44), t, False)
    k = popk(t, T["card"] + 0.1, "smooth")
    if k <= 0: return
    w, h = 720 * (0.8 + 0.2 * k), 900 * (0.8 + 0.2 * k); cx_, cy_ = 540, 780; a_ = ap(t, T["card"] + 0.1)
    d.rect(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2, fill=A((250, 246, 234), a_), r=36)
    tag(d, cx_, cy_ - h / 2 + 70, "一句话学会", GOLD, a_, 32)
    larva(d, cx_, cy_ - 170, 1.4, t, a=a_, glow=TDTG)
    d.text(cx_, cy_ + 10, "河豚宝宝有两道防线", 44, A(NAVYT, a_), k=1)
    for i, s_ in enumerate(("剧毒 TTX：毒倒一部分天敌", "几乎无毒的 TDT：一尝就吐", "都来自河豚妈妈")):
        kk = ap(t, at("card", 1.5 + i * 1.6), 0.25)
        if kk > 0: d.text(cx_, cy_ + 120 + i * 78, s_, 38, A((70, 70, 90), kk), k=1)
def s_end(t, d):
    t0 = T["end"]
    flatbg(d, (120, 40, 50), (50, 16, 30), t, False)
    sp = pr(t, t0 + 0.6, t0 + 1.0)
    dragongod(d, 440, 760, 1.25, t, face="spit" if sp > 0 else "chew")
    if sp > 0: u = ease(sp); d.ell(lerp(470, 820, u), lerp(760, 600, u), 26, 12, A((250, 240, 235), 1))
    ptag(d, t, t0 + 1.0, 760, 480, "呸", WHITE, 50)
    ra = ap(t, t0 + 2.0, 0.3)
    if ra > 0:
        d.rect(150, 250, 930, 400, fill=A((6, 8, 20), 0.6 * ra), r=20)
        d.text(540, 285, "Kaneko et al. 2026 · iScience", 26, A(WHITE, 0.95 * ra), k=1)
        d.text(540, 330, "龙神吃河豚为《无职转生》粉丝梗", 24, A(WHITE, 0.85 * ra), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

# ---------------- captions ----------------
HL = {"hook": "河豚", "q": "卵里", "who": "不全是剧毒", "sperm": "吞下去", "egg": "TDT", "reveal": "就吐", "how": "全身",
      "xray": "吐出来", "swim": "都吐", "gene": "两道防线", "why": "靠近", "order": "能活", "end": "读档"}
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
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/fg_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=6, thumb_w=300, labels=[f"{x:.1f}" for x in ts]).save("/tmp/fg_sheet.png")
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
