import math, sys, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1920, 1080
S = 1.5
SW, SH = int(W*S), int(H*S)
FPS = 30
DUR = 34.0
F_BOLD = "/workspace/work/flytrap/NotoSansSC-Bold.otf"
F_BLACK = "/workspace/work/flytrap/NotoSansSC-Black.otf"
_fc = {}
def font(sz, black=False):
    k = (sz, black)
    if k not in _fc: _fc[k] = ImageFont.truetype(F_BLACK if black else F_BOLD, int(sz*S))
    return _fc[k]

GOLD = (222, 184, 110); WHITE = (240, 240, 240); GRAY = (150, 150, 155)
RED = (235, 60, 60); BLUE = (70, 160, 255); CYAN = (120, 220, 255)
BG1 = (46, 48, 53); BG2 = (22, 23, 26)

# voice line timing (start, end, text)
LINES = [
 (0.4, 8.35, "光遗传怎么研究抑郁？第一步，用病毒载体，|把光敏蛋白的基因送进特定神经元。"),
 (8.7, 16.1, "蓝光一照，通道打开，正离子涌入，神经元立刻放电；|光一关，放电就停。"),
 (16.6, 23.0, "在抑郁模型小鼠脑内，植入光纤，|精确激活奖赏环路里的多巴胺神经元。"),
 (23.3, 26.5, "小鼠的抑郁样行为随即改善。"),
 (27.0, 32.4, "光遗传让科学家能逐条测试：|到底是哪条环路，在驱动疾病。"),
]
T_S2, T_S3, T_S4, T_S5 = 8.55, 16.45, 23.15, 26.8
LIGHT_ON, LIGHT_OFF = 9.1, 13.4

def P(x, y): return (x*S, y*S)
def cl(v, a=0, b=1): return max(a, min(b, v))
def ease(v): v = cl(v); return v*v*(3-2*v)
def eob(v):
    v = cl(v); c1 = 1.70158; c3 = c1+1
    return 1 + c3*(v-1)**3 + c1*(v-1)**2
def lerp(a, b, t): return a + (b-a)*t
def mix(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))
def rgba(c, a): return (c[0], c[1], c[2], int(255*cl(a)))

_bg = None
def background():
    global _bg
    if _bg is None:
        g = Image.new("RGB", (2, 2)); g.putpixel((0, 0), BG1); g.putpixel((1, 0), mix(BG1, BG2, .5))
        g.putpixel((0, 1), mix(BG1, BG2, .5)); g.putpixel((1, 1), BG2)
        _bg = g.resize((SW, SH), Image.BILINEAR)
    return _bg.copy()

def text(img, xy, s, sz, col, a=1.0, anchor="la", black=False):
    if a <= 0.01: return
    f = font(sz, black)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).text(P(*xy), s, font=f, fill=int(255*cl(a)), anchor=anchor)
    img.paste(col, (0, 0), m)

def circle(d, x, y, r, fill=None, outline=None, w=1):
    d.ellipse([P(x-r, y-r), P(x+r, y+r)], fill=fill, outline=outline, width=int(w*S) if outline else 0)

def glow(img, x, y, r, col, a):
    if a <= 0.01: return
    lay = Image.new("RGB", img.size, (0, 0, 0))
    dd = ImageDraw.Draw(lay)
    circle(dd, x, y, r, fill=tuple(int(c*a) for c in col))
    lay = lay.filter(ImageFilter.GaussianBlur(r*S*0.5))
    from PIL import ImageChops
    img.paste(ImageChops.add(img, lay))

def header(img, d, t, title):
    text(img, (60, 30), "光遗传学 · 机制演示", 30, WHITE)
    a = ease((t % 100))
    text(img, (60, 110), title, 50, WHITE)
    d.line([P(60, 185), P(330, 185)], fill=GOLD, width=int(3*S))

def subtitle(img, d, t):
    for s, e, txt in LINES:
        if s - .15 <= t <= e + .25:
            a = min(ease((t-s+.15)/.2), ease((e+.25-t)/.2))
            parts = txt.split("|")
            # pick part by progress (proportional to length)
            tot = sum(len(p) for p in parts); acc = 0; cur = parts[-1]
            prog = (t - s)/(e - s)
            for p in parts:
                acc += len(p)
                if prog <= acc/tot: cur = p; break
            f = font(40)
            bw = d.textlength(cur, font=f)/S
            d.rounded_rectangle([P(W/2-bw/2-28, 968), P(W/2+bw/2+28, 1036)], radius=int(14*S), fill=(0, 0, 0, int(150*a)))
            text(img, (W/2, 1002), cur, 40, WHITE, a, "mm")

# ---------------- neuron drawing ----------------
random.seed(3)
DEND = []
for k in range(7):
    ang = math.radians(100 + k*38 + random.uniform(-8, 8))
    L = random.uniform(150, 230)
    br = [(ang + random.uniform(-.5, .5), random.uniform(.4, .7)) for _ in range(2)]
    DEND.append((ang, L, br))

def neuron(d, cx, cy, r, col, a=1.0, axon=True):
    c = rgba(col, a)
    for ang, L, br in DEND:
        if axon and abs(math.cos(ang)) > .95 and math.cos(ang) > 0: continue
        x2, y2 = cx + math.cos(ang)*L, cy + math.sin(ang)*L
        d.line([P(cx, cy), P(x2, y2)], fill=c, width=int(14*S))
        for b, f in br:
            bx, by = cx + math.cos(ang)*L*f, cy + math.sin(ang)*L*f
            d.line([P(bx, by), P(bx + math.cos(b)*70, by + math.sin(b)*70)], fill=c, width=int(8*S))
    if axon:
        d.line([P(cx, cy), P(cx+560, cy+30)], fill=c, width=int(16*S))
        for k in range(4):
            x = cx + 140 + k*105
            d.rounded_rectangle([P(x, cy+30*(x-cx)/560-17), P(x+80, cy+30*(x-cx)/560+17)], radius=int(16*S), fill=rgba((90, 95, 110), a))
    circle(d, cx, cy, r, fill=c)

def channel(d, x, y, op, sc=1.0, a=1.0):
    # a little pore: two subunits that separate when open
    gap = 4 + 10*op
    w, h = 16*sc, 34*sc
    col = rgba(mix(GOLD, CYAN, op), a)
    d.rounded_rectangle([P(x-gap/2-w, y-h/2), P(x-gap/2, y+h/2)], radius=int(6*S*sc), fill=col)
    d.rounded_rectangle([P(x+gap/2, y-h/2), P(x+gap/2+w, y+h/2)], radius=int(6*S*sc), fill=col)

def aav(d, x, y, r, rot, a=1.0):
    pts = [P(x + r*math.cos(rot + k*math.pi/3), y + r*math.sin(rot + k*math.pi/3)) for k in range(6)]
    d.polygon(pts, fill=rgba((200, 90, 200), a), outline=rgba((255, 170, 255), a), width=int(3*S))
    for k in range(6):
        d.line([P(x, y), pts[k][0]/S*S and P(x + r*math.cos(rot+k*math.pi/3), y + r*math.sin(rot+k*math.pi/3))], fill=rgba((255, 170, 255), a*.6), width=int(2*S))

def helix(d, x, y, L, ph, a, col=(255, 210, 120)):
    n = 40
    for s in (0, math.pi):
        pts = [P(x + L*i/n - L/2, y + 14*math.sin(i/n*4*math.pi + ph + s)) for i in range(n+1)]
        d.line(pts, fill=rgba(col, a), width=int(4*S))

# ---------------- scenes ----------------
CH_ANG = [math.radians(a) for a in (200, 240, 290, 330, 20, 160, 120, 60)]
def s1(img, d, t):
    header(img, d, t, "第一步：把“光开关”装进神经元")
    cx, cy, r = 1000, 560, 120
    neuron(d, cx, cy, r, (110, 116, 135))
    circle(d, cx-10, cy+5, 46, fill=(80, 84, 100))  # nucleus
    # virus flies in from left
    p = ease((t-0.6)/2.6)
    vx, vy = lerp(250, cx-r+10, p), lerp(380, cy-20, p) + 30*math.sin(t*3)*(1-p)
    va = 1 - ease((t-3.3)/.5)
    aav(d, vx, vy, 42, t*1.2, va)
    if t < 3.4: text(img, (vx, vy-70), "病毒载体 AAV", 30, (255, 170, 255), va*ease((t-.6)/.4), "mm")
    # gene enters nucleus
    gp = ease((t-3.3)/1.2)
    if t > 3.2:
        gx = lerp(cx-r+10, cx-10, gp)
        helix(d, gx, cy+5, 70, t*5, cl((t-3.2)/.3))
        glow(img, cx-10, cy+5, 70, (255, 200, 90), .5*ease((t-4.2)/.5)*(0.7+0.3*math.sin(t*6)))
        text(img, (cx-10, cy-200), "光敏蛋白基因（如ChR2）", 30, GOLD, ease((t-3.6)/.4), "mm")
    # channels pop onto membrane
    for k, ang in enumerate(CH_ANG):
        tp = 5.4 + k*.22
        sc = eob((t-tp)/.35)
        if sc > 0:
            x, y = cx + (r+2)*math.cos(ang), cy + (r+2)*math.sin(ang)
            channel(d, x, y, 0, sc*.9)
    text(img, (cx+170, cy+150), "膜上长出光敏通道", 34, CYAN, ease((t-6.4)/.4), "lm")

def s2(img, d, t):
    lt = t - T_S2
    header(img, d, t, "第二步：用光控制放电")
    # membrane band
    my = 470
    d.rectangle([P(0, my-38), P(W, my+38)], fill=(70, 74, 88))
    for x in range(0, W, 26):
        circle(d, x+13, my-30, 10, fill=(120, 126, 145)); circle(d, x+13, my+30, 10, fill=(120, 126, 145))
    text(img, (60, my-90), "细胞外", 28, GRAY); text(img, (60, my+70), "细胞内", 28, GRAY)
    on = ease((t-LIGHT_ON)/.25) * (1 - ease((t-LIGHT_OFF)/.25))
    xs = [520, 820, 1120, 1420]
    # light beam
    if on > 0:
        lay = Image.new("RGB", img.size, (0, 0, 0)); dd = ImageDraw.Draw(lay)
        dd.polygon([P(900, 190), P(1060, 190), P(1600, my), P(360, my)], fill=tuple(int(c*.38*on) for c in BLUE))
        lay = lay.filter(ImageFilter.GaussianBlur(18*S))
        from PIL import ImageChops
        img.paste(ImageChops.add(img, lay))
        text(img, (1090, 230), "蓝光 约470 nm", 32, CYAN, on, "lm")
    for x in xs: channel(d, x, my, on, 1.4)
    # ions
    random.seed(7)
    for i in range(60):
        x0 = random.choice(xs); ph = random.random()
        sp = 1.1
        u = ((t*sp + ph) % 1.0)
        # outside ions jitter, when open they stream down
        ox = x0 + random.uniform(-130, 130)
        if on > .3:
            k = u
            x = lerp(ox, x0, ease(k*2)); y = lerp(300, my+150, k)
            if k > .5: x = x0 + (k-.5)*random.uniform(-200, 200)
        else:
            x = ox + 8*math.sin(t*3+i); y = 290 + random.uniform(-40, 70)
        circle(d, x, y, 15, fill=(235, 90, 80))
        text(img, (x, y), "+", 24, WHITE, 1, "mm", True)
    text(img, (1500, 300), "正离子", 30, (255, 140, 130), 1, "lm")
    # voltage trace
    bx, by, bw, bh = 560, 640, 800, 230
    d.rounded_rectangle([P(bx, by), P(bx+bw, by+bh)], radius=int(16*S), fill=(15, 16, 19), outline=(70, 70, 76), width=int(2*S))
    text(img, (bx+18, by+14), "膜电位", 26, GRAY)
    span = 7.6
    pts = []
    for i in range(400):
        tt = T_S2 + span*i/399
        if tt > t: break
        v = 0
        if LIGHT_ON+.15 < tt < LIGHT_OFF:
            ph = ((tt - LIGHT_ON - .15) % .42)
            v = math.exp(-((ph-.05)/.025)**2) - .25*math.exp(-((ph-.13)/.05)**2)
        pts.append(P(bx+20+(bw-40)*i/399, by+bh*0.72 - v*bh*0.55))
    if len(pts) > 1: d.line(pts, fill=GOLD, width=int(3*S))
    # light bar under trace
    lx0 = bx+20+(bw-40)*(LIGHT_ON-T_S2)/span; lx1 = bx+20+(bw-40)*(LIGHT_OFF-T_S2)/span
    if t > LIGHT_ON:
        d.rectangle([P(lx0, by+bh-22), P(min(lx1, bx+20+(bw-40)*(t-T_S2)/span), by+bh-12)], fill=BLUE)
    text(img, (bx+bw+40, by+70), "光开 → 放电", 36, GOLD, ease((t-LIGHT_ON-.6)/.3), "lm")
    text(img, (bx+bw+40, by+140), "光关 → 停止", 36, WHITE, ease((t-LIGHT_OFF-.4)/.3), "lm")

def mouse_head(d, a=1.0):
    col = rgba((95, 100, 115), a)
    # head/body side outline
    d.ellipse([P(420, 330), P(1500, 900)], fill=col)
    d.polygon([P(1450, 520), P(1720, 640), P(1460, 760)], fill=col)
    circle(d, 1660, 640, 16, fill=rgba((235, 120, 140), a))
    circle(d, 1250, 360, 95, fill=col); circle(d, 1250, 360, 60, fill=rgba((200, 130, 150), a))
    circle(d, 1440, 590, 12, fill=rgba((20, 20, 24), a))

def brain_pts():
    return [P(620, 470), P(760, 410), P(950, 395), P(1150, 420), P(1290, 480), P(1330, 560), P(1260, 640), P(1100, 680), P(900, 690), P(720, 660), P(600, 590)]
VTA = (860, 600); NAC = (1180, 560); PFC = (1290, 500)
def s3(img, d, t):
    lt = t - T_S3
    header(img, d, t, "第三步：在抑郁模型小鼠中激活奖赏环路")
    mouse_head(d)
    d.polygon(brain_pts(), fill=(160, 140, 165), outline=(200, 180, 205), width=int(3*S))
    # fiber
    fp = ease((lt-.6)/1.2)
    fy = lerp(250, VTA[1]-25, fp)
    d.line([P(VTA[0], 250), P(VTA[0], fy)], fill=(210, 210, 220), width=int(10*S))
    d.rectangle([P(VTA[0]-22, 225), P(VTA[0]+22, 270)], fill=(80, 80, 90))
    text(img, (VTA[0]+40, 250), "光纤", 32, WHITE, ease((lt-.6)/.4), "lm")
    on = ease((lt-2.2)/.3)
    glow(img, VTA[0], VTA[1], 60, BLUE, on*(.8+.2*math.sin(t*12)))
    circle(d, VTA[0], VTA[1], 22, fill=mix((200, 120, 60), GOLD, on))
    circle(d, NAC[0], NAC[1], 26, fill=(200, 120, 60))
    text(img, (VTA[0], 760), "VTA 多巴胺神经元", 32, GOLD, ease((lt-1.4)/.4), "mm")
    text(img, (NAC[0], 760), "伏隔核（奖赏）", 30, GOLD, ease((lt-1.8)/.4), "mm")
    # projection arc
    arc = [(lerp(VTA[0], NAC[0], u), lerp(VTA[1], NAC[1], u) - 90*math.sin(math.pi*u)) for u in [i/40 for i in range(41)]]
    d.line([P(*p) for p in arc], fill=(230, 170, 90), width=int(6*S))
    if on > 0:
        for k in range(3):
            u = ((t*1.4 + k/3) % 1)
            x, y = arc[int(u*40)]
            glow(img, x, y, 22, GOLD, on)
            circle(d, x, y, 9, fill=(255, 240, 200))
        glow(img, NAC[0], NAC[1], 50, GOLD, on*.6*(0.6+0.4*math.sin(t*9)))

def mouse_icon(d, x, y, sc, col, curl):
    # simple side-view mouse; curl 1 = hunched, 0 = stretched/active
    bw = 150*sc*(1-.25*curl); bh = 85*sc*(1+.2*curl)
    d.ellipse([P(x-bw, y-bh), P(x+bw, y+bh)], fill=col)
    hx = x + bw*.95; hy = y - bh*.2 + 20*curl*sc
    circle(d, hx, hy, 52*sc, fill=col); circle(d, hx-10*sc, hy-48*sc, 26*sc, fill=col)
    circle(d, hx+20*sc, hy-8*sc, 6*sc, fill=(20, 20, 24))
    tail = [P(x-bw + 10, y + 20*sc)]
    for i in range(1, 12):
        tail.append(P(x-bw - i*16*sc, y + 20*sc - 30*sc*math.sin(i/3 + curl)))
    d.line(tail, fill=col, width=int(5*S*sc))

def s4(img, d, t):
    lt = t - T_S4
    header(img, d, t, "结果：抑郁样行为改善")
    # left: light off
    mouse_icon(d, 560, 520, 1.0, (110, 112, 125), 1)
    text(img, (560, 690), "光关：蜷缩、少动", 34, GRAY, 1, "mm")
    a = ease((lt-.5)/.4)
    jump = abs(math.sin(t*6))*25*a
    mouse_icon(d, 1330, 520 - jump, 1.0, mix((110, 112, 125), GOLD, a), 1-a)
    glow(img, 1330, 470, 40, BLUE, a*.7)
    text(img, (1330, 690), "光开：主动挣扎、探索", 34, GOLD, a, "mm")
    text(img, (W/2, 520), "→", 80, WHITE, ease((lt-.2)/.3), "mm", True)
    text(img, (W-60, 900), "Tye et al., Nature 2013 · 小鼠实验", 24, GRAY, ease(lt/.5), "rm")

NODES = {"前额叶": (700, 380), "伏隔核": (1050, 330), "VTA": (1350, 520), "杏仁核": (850, 640), "海马": (1180, 700), "缰核": (1500, 340)}
EDGES = [("前额叶", "伏隔核"), ("VTA", "伏隔核"), ("杏仁核", "前额叶"), ("海马", "伏隔核"), ("缰核", "VTA"), ("杏仁核", "海马"), ("前额叶", "VTA")]
def s5(img, d, t):
    lt = t - T_S5
    header(img, d, t, "意义：逐条测试，找出致病环路")
    active = int(lt/0.9) % len(EDGES) if lt < 5.4 else 1
    for i, (a_, b_) in enumerate(EDGES):
        (x1, y1), (x2, y2) = NODES[a_], NODES[b_]
        on = (i == active)
        d.line([P(x1, y1), P(x2, y2)], fill=GOLD if on else (85, 88, 98), width=int((8 if on else 4)*S))
        if on:
            u = (lt*1.5) % 1
            glow(img, lerp(x1, x2, u), lerp(y1, y2, u), 20, CYAN, 1)
    for n, (x, y) in NODES.items():
        hl = any(n in EDGES[active] for _ in [0])
        circle(d, x, y, 40, fill=(200, 120, 60) if hl else (120, 124, 140))
        text(img, (x, y+62), n, 30, WHITE, ease(lt/.4), "mm")
    if lt > 5.4:
        a = ease((lt-5.4)/.4)
        text(img, (W/2, 845), "目前仍以动物研究为主", 34, RED, a, "mm")

SCENES = [(0, s1), (T_S2, s2), (T_S3, s3), (T_S4, s4), (T_S5, s5)]
def frame(t):
    img = background()
    d = ImageDraw.Draw(img, "RGBA")
    idx = max(i for i, (s, _) in enumerate(SCENES) if t >= s)
    SCENES[idx][1](img, d, t)
    d = ImageDraw.Draw(img, "RGBA")
    # crossfade flash at cuts
    for s, _ in SCENES[1:]:
        if 0 <= t - s < .3:
            d.rectangle([0, 0, SW, SH], fill=(22, 23, 26, int(255*(1-(t-s)/.3))))
    if t > DUR - .6:
        d.rectangle([0, 0, SW, SH], fill=(22, 23, 26, int(255*ease((t-DUR+.6)/.6))))
    subtitle(img, d, t)
    text(img, (W-40, H-40), "", 20, GRAY)
    return img.resize((W, H), Image.LANCZOS)

if __name__ == "__main__":
    if sys.argv[1] == "test":
        for a in sys.argv[2:]:
            frame(float(a)).save(f"test_{a}.png")
    else:
        i0, i1 = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs("frames", exist_ok=True)
        for i in range(i0, i1):
            frame(i/FPS).save(f"frames/{i:05d}.png", compress_level=1)
