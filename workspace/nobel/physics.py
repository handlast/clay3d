import math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

W, H, FPS, DUR = 1920, 1080, 30, 30.0
N = int(FPS * DUR)
CJK = "/workspace/work/nobel/NotoSerifSC.otf"
LAT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
GOLD = (222, 184, 98); GOLD_L = (255, 230, 160); WHITE = (240, 240, 245)
BLUE = (90, 190, 255); RED = (255, 110, 90); ICE = (170, 215, 240)
random.seed(3)
fc = {}
def F(size, lat=False):
    k = (size, lat)
    if k not in fc: fc[k] = ImageFont.truetype(LAT if lat else CJK, size)
    return fc[k]
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def prog(t, a, b): return clamp((t - a) / (b - a))
def lerp(a, b, k): return a + (b - a) * k

g = Image.radial_gradient("L").resize((W * 2, W * 2)).crop((W // 2, W - H // 2, W // 2 + W, W - H // 2 + H))
BG = ImageOps.colorize(g, black=(22, 26, 50), white=(4, 5, 12)).convert("RGBA")
stars = [(random.uniform(0, W), random.uniform(0, H), random.uniform(0.8, 2.6), random.uniform(0, 6.28)) for _ in range(160)]

def new(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))
def fade(img, a):
    if a >= 0.999: return img
    al = img.getchannel("A").point(lambda v: int(v * a)); img.putalpha(al); return img
def glow(img, r=10):
    b = img.filter(ImageFilter.GaussianBlur(r)); b.alpha_composite(img); return b

SCENES = [(0, 5), (5, 10), (10, 15.5), (15.5, 22), (22, 26.5), (26.5, 30)]
CAPS = ["", "中微子：宇宙中最“害羞”的粒子", "为什么要追中微子？", "哈尔岑的点子：把南极冰盖变成望远镜",
        "2013 年：第一次抓到宇宙高能中微子", ""]

def caption(d, text, y=985):
    if text: d.text((W // 2, y), text, font=F(46), fill=WHITE, anchor="mm")

# ---------- scene 1: the prize
def s1(t, L):
    d = ImageDraw.Draw(L)
    a = ease(prog(t, 0.2, 1.0)); dy = 30 * (1 - a)
    d.text((W // 2, 300 + dy), "2026 诺贝尔物理学奖", font=F(64), fill=GOLD + (int(255 * a),), anchor="mm")
    b = ease(prog(t, 0.8, 1.6)); dy = 30 * (1 - b)
    d.text((W // 2, 460 + dy), "弗朗西斯 · 哈尔岑", font=F(130), fill=GOLD_L + (int(255 * b),), anchor="mm")
    d.text((W // 2, 580 + dy), "FRANCIS HALZEN  ·  University of Wisconsin–Madison", font=F(32, True), fill=GOLD + (int(255 * b),), anchor="mm")
    c = ease(prog(t, 1.8, 2.6))
    d.line((W // 2 - 420 * c, 660, W // 2 + 420 * c, 660), fill=GOLD + (200,), width=2)
    d.text((W // 2, 740), "表彰他对“冰立方”中微子天文台的决定性贡献，", font=F(46), fill=WHITE + (int(255 * c),), anchor="mm")
    d.text((W // 2, 810), "以及发现来自宇宙深处的高能中微子", font=F(46), fill=WHITE + (int(255 * c),), anchor="mm")

# ---------- scene 2: shy neutrino
nu = [(random.uniform(0, 1), random.uniform(330, 820), random.uniform(0.7, 1.3)) for _ in range(70)]
def s2(t, L):
    d = ImageDraw.Draw(L)
    a = ease(prog(t, 0.0, 0.6))
    # block of matter
    d.rounded_rectangle((900, 300, 1180, 850), radius=20, fill=(120, 120, 140, int(110 * a)), outline=(180, 180, 200, int(200 * a)), width=3)
    d.text((1040, 280), "物质（地球、你的身体……）", font=F(34), fill=(200, 200, 215, int(255 * a)), anchor="mb")
    P = new(); pd = ImageDraw.Draw(P)
    for x0, y, sp in nu:
        x = 780 + ((x0 + t * 0.55 * sp) % 1.0) * 520
        if not (330 < y < 820): continue
        pd.ellipse((x - 5, y - 5, x + 5, y + 5), fill=GOLD_L + (int(230 * a),))
        pd.line((x - 60, y, x - 6, y), fill=GOLD + (int(90 * a),), width=3)
    L.alpha_composite(glow(P, 6))
    b = ease(prog(t, 1.0, 1.8))
    for i, s in enumerate(["不带电", "几乎没有质量", "几乎从不与物质相撞"]):
        bb = ease(prog(t, 1.0 + i * 0.4, 1.8 + i * 0.4))
        d.text((150, 450 + i * 110), "• " + s, font=F(50), fill=GOLD_L + (int(255 * bb),), anchor="lm")
    c = ease(prog(t, 2.6, 3.4))
    d.text((1590, 520), "每秒约", font=F(40), fill=WHITE + (int(255 * c),), anchor="mm")
    d.text((1590, 600), "650 亿个", font=F(80), fill=GOLD_L + (int(255 * c),), anchor="mm")
    d.text((1590, 690), "太阳中微子穿过你的指甲盖", font=F(34), fill=WHITE + (int(255 * c),), anchor="mm")

# ---------- scene 3: why neutrinos
SRC = (330, 520); EARTH = (1600, 520)
def bez(p0, p1, p2, k):
    return ((1 - k) ** 2 * p0[0] + 2 * (1 - k) * k * p1[0] + k * k * p2[0], (1 - k) ** 2 * p0[1] + 2 * (1 - k) * k * p1[1] + k * k * p2[1])
def s3(t, L):
    d = ImageDraw.Draw(L)
    a = ease(prog(t, 0.0, 0.6))
    G = new(); gd = ImageDraw.Draw(G)
    gd.ellipse((SRC[0] - 70, SRC[1] - 40, SRC[0] + 70, SRC[1] + 40), fill=(255, 210, 140, int(200 * a)))
    gd.ellipse((SRC[0] - 22, SRC[1] - 22, SRC[0] + 22, SRC[1] + 22), fill=(255, 255, 230, int(255 * a)))
    gd.ellipse((EARTH[0] - 55, EARTH[1] - 55, EARTH[0] + 55, EARTH[1] + 55), fill=(60, 130, 220, int(255 * a)))
    L.alpha_composite(glow(G, 18))
    d.text((SRC[0], SRC[1] + 90), "宇宙“粒子加速器”", font=F(34), fill=WHITE + (int(255 * a),), anchor="mt")
    d.text((SRC[0], SRC[1] + 135), "（活动星系、恒星爆炸…）", font=F(28), fill=(190, 190, 205, int(255 * a)), anchor="mt")
    d.text((EARTH[0], EARTH[1] + 80), "地球", font=F(34), fill=WHITE + (int(255 * a),), anchor="mt")
    # magnetic field arcs
    d.text((980, 400), "~ 星际磁场 ~", font=F(28), fill=(170, 160, 255, int(200 * a)), anchor="mm")
    # proton: curved, misses
    kp = ease(prog(t, 0.8, 2.6))
    pts = [bez(SRC, (900, 120), (1400, 160), i / 40 * kp) for i in range(41)]
    if kp > 0:
        d.line(pts, fill=RED + (230,), width=5)
        x, y = pts[-1]; d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=RED + (255,))
    b = ease(prog(t, 1.6, 2.3))
    d.text((1000, 110), "质子（带电）被磁场弯折 → 找不到来源", font=F(36), fill=RED + (int(255 * b),), anchor="mm")
    # neutrino: straight
    kn = ease(prog(t, 2.2, 3.8))
    if kn > 0:
        x = lerp(SRC[0] + 30, EARTH[0] - 60, kn)
        d.line((SRC[0] + 30, SRC[1], x, SRC[1]), fill=GOLD_L + (240,), width=5)
        P = new(); ImageDraw.Draw(P).ellipse((x - 12, SRC[1] - 12, x + 12, SRC[1] + 12), fill=GOLD_L + (255,)); L.alpha_composite(glow(P, 8))
    c = ease(prog(t, 3.0, 3.7))
    d.text((960, 790), "中微子（不带电）走直线 → 直接指向源头", font=F(40), fill=GOLD_L + (int(255 * c),), anchor="mm")

# ---------- scene 4: IceCube
IX0, IX1, ISURF, IBOT = 180, 1080, 240, 860
STRX = [IX0 + 90 + i * 80 for i in range(10)]
SENS = [(x, y) for x in STRX for y in range(440, 850, 34)]
HIT = (600, 640)
def s4(t, L):
    d = ImageDraw.Draw(L)
    a = ease(prog(t, 0.0, 0.7))
    d.rectangle((IX0, ISURF, IX1, IBOT), fill=(120, 170, 210, int(60 * a)))
    d.line((IX0, ISURF, IX1, ISURF), fill=(235, 245, 255, int(255 * a)), width=4)
    d.text((IX0 + 10, ISURF - 12), "南极冰面", font=F(30), fill=ICE + (int(255 * a),), anchor="lb")
    d.text((IX1 + 15, 440), "1450 米", font=F(26), fill=ICE + (int(220 * a),), anchor="lm")
    d.text((IX1 + 15, 840), "2450 米", font=F(26), fill=ICE + (int(220 * a),), anchor="lm")
    ks = ease(prog(t, 0.4, 1.6))
    for x in STRX:
        y1 = ISURF + (850 - ISURF) * ks
        d.line((x, ISURF, x, y1), fill=(200, 220, 235, 110), width=2)
    # neutrino from below and light cone
    kn = prog(t, 1.8, 2.8)
    start = (960, IBOT)
    if 0 < kn:
        x = lerp(start[0], HIT[0], min(kn, 1)); y = lerp(start[1], HIT[1], min(kn, 1))
        d.line((start[0], start[1], x, y), fill=GOLD_L + (200,), width=4)
    kl = prog(t, 2.8, 4.2)
    lit = new(); ld = ImageDraw.Draw(lit)
    if kl > 0:
        dx, dy = HIT[0] - start[0], HIT[1] - start[1]; n = math.hypot(dx, dy); dx, dy = dx / n, dy / n
        tip = (HIT[0] + dx * 380 * kl, HIT[1] + dy * 380 * kl)
        px, py = -dy, dx; w = 160 * kl
        ld.polygon([HIT, (tip[0] + px * w, tip[1] + py * w), (tip[0] - px * w, tip[1] - py * w)], fill=BLUE + (int(90 * (1 - 0.4 * kl)),))
        d.line((HIT[0], HIT[1], tip[0], tip[1]), fill=(200, 235, 255, 230), width=3)
    for (x, y) in SENS:
        if y > ISURF + (850 - ISURF) * ks: continue
        on = 0.0
        if kl > 0:
            dist = math.hypot(x - HIT[0], y - HIT[1])
            on = clamp((kl * 420 - dist) / 60) * (1 - 0.3 * prog(t, 5.5, 6.5))
        col = tuple(int(lerp(c0, c1, on)) for c0, c1 in zip((150, 170, 190), (130, 220, 255)))
        r = 5 + 4 * on
        ld.ellipse((x - r, y - r, x + r, y + r), fill=col + (255,))
    L.alpha_composite(glow(lit, 7))
    # facts
    facts = [("1988", "年提出构想"), ("1 立方公里", "冰下探测体积"), ("5160 个", "光传感器 · 86 根线缆"), ("2011", "年全面建成")]
    for i, (big, small) in enumerate(facts):
        b = ease(prog(t, 1.0 + i * 0.5, 1.7 + i * 0.5))
        y = 330 + i * 140 + 20 * (1 - b)
        d.text((1220, y), big, font=F(64), fill=GOLD_L + (int(255 * b),), anchor="lm")
        d.text((1220, y + 58), small, font=F(32), fill=WHITE + (int(255 * b),), anchor="lm")
    c = ease(prog(t, 2.9, 3.5))
    d.text((630, 900), "中微子撞上原子核 → 发出蓝光 → 被传感器记录", font=F(34), fill=(160, 220, 255, int(255 * c)), anchor="mm")

# ---------- scene 5: discovery
def s5(t, L):
    d = ImageDraw.Draw(L)
    a = ease(prog(t, 0.0, 0.7))
    d.text((520, 450), "2013", font=F(200, True), fill=GOLD_L + (int(255 * a),), anchor="mm")
    b = ease(prog(t, 0.6, 1.3))
    d.text((520, 600), "首次报告宇宙高能中微子证据", font=F(44), fill=WHITE + (int(255 * b),), anchor="mm")
    d.text((520, 665), "随后数据确认了这一发现", font=F(36), fill=(200, 200, 215, int(255 * b)), anchor="mm")
    # galaxy + incoming arrows
    c = ease(prog(t, 1.2, 2.2))
    G = new(); gd = ImageDraw.Draw(G)
    cx, cy = 1450, 420
    gd.ellipse((cx - 150, cy - 55, cx + 150, cy + 55), fill=(200, 170, 255, int(120 * c)))
    gd.ellipse((cx - 70, cy - 28, cx + 70, cy + 28), fill=(240, 220, 255, int(200 * c)))
    gd.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=(255, 255, 240, int(255 * c)))
    L.alpha_composite(glow(G, 20))
    d.text((cx, cy - 95), "活动星系 NGC 1068", font=F(36), fill=(220, 205, 255, int(255 * c)), anchor="mm")
    d.text((cx, cy - 50 - 100), "可能的中微子源", font=F(26), fill=(190, 180, 220, int(255 * c)), anchor="mm")
    for i in range(6):
        k = prog(t, 1.8 + i * 0.25, 2.8 + i * 0.25)
        if k <= 0: continue
        ox = cx + (i - 2.5) * 30
        y = lerp(cy + 60, 820, k)
        d.line((ox, cy + 60, ox, y), fill=GOLD_L + (150,), width=3)
        d.ellipse((ox - 6, y - 6, ox + 6, y + 6), fill=GOLD_L + (255,))
    d.line((1250, 830, 1650, 830), fill=(235, 245, 255, int(255 * c)), width=4)
    d.text((1450, 850), "冰立方", font=F(32), fill=ICE + (int(255 * c),), anchor="mt")

# ---------- scene 6: why it matters
def s6(t, L):
    d = ImageDraw.Draw(L)
    a = ease(prog(t, 0.0, 0.8)); dy = 25 * (1 - a)
    d.text((W // 2, 380 + dy), "开辟了一种全新的天文学", font=F(100), fill=GOLD_L + (int(255 * a),), anchor="mm")
    b = ease(prog(t, 0.6, 1.4))
    d.line((W // 2 - 450 * b, 480, W // 2 + 450 * b, 480), fill=GOLD + (200,), width=2)
    d.text((W // 2, 570), "用中微子，看见光和其他粒子看不到的宇宙", font=F(50), fill=WHITE + (int(255 * b),), anchor="mm")
    c = ease(prog(t, 1.2, 2.0))
    d.text((W // 2, 680), "—— 中微子天文学", font=F(40), fill=GOLD + (int(255 * c),), anchor="mm")

FUNCS = [s1, s2, s3, s4, s5, s6]

def frame(i):
    t = i / FPS
    im = BG.copy()
    S = new(); sd = ImageDraw.Draw(S)
    for x, y, r, ph in stars:
        al = int(120 + 100 * math.sin(t * 2 + ph))
        sd.ellipse((x - r, y - r, x + r, y + r), fill=(255, 240, 210, al))
    im.alpha_composite(S)
    for k, ((a, b), fn) in enumerate(zip(SCENES, FUNCS)):
        if a - 0.01 <= t < b + 0.01:
            L = new(); fn(t - a, L)
            cd = ImageDraw.Draw(L); caption(cd, CAPS[k])
            alpha = ease(prog(t, a, a + 0.5)) * (1 - ease(prog(t, b - 0.45, b))) if k < 5 else ease(prog(t, a, a + 0.5))
            if k == 0: alpha = 1 - ease(prog(t, b - 0.45, b))
            im.alpha_composite(fade(L, alpha))
    # header tag + progress
    O = new(); od = ImageDraw.Draw(O)
    if t > 5:
        od.text((70, 60), "2026 诺贝尔物理学奖", font=F(30), fill=GOLD + (200,), anchor="lm")
    od.rectangle((0, H - 6, int(W * t / DUR), H), fill=GOLD + (180,))
    im.alpha_composite(O)
    if t < 0.4: im = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), im, t / 0.4)
    if t > DUR - 0.6: im = Image.blend(im, Image.new("RGBA", (W, H), (0, 0, 0, 255)), (t - (DUR - 0.6)) / 0.6)
    return im.convert("RGB")

OUT = "/workspace/work/nobel/nobel_physics_2026_30s.mp4"
cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-f", "lavfi", "-i",
       "aevalsrc='0.10*(sin(2*PI*110*t)+0.7*sin(2*PI*164.81*t)+0.5*sin(2*PI*220*t)+0.35*sin(2*PI*277.18*t)*(0.5+0.5*sin(2*PI*0.1*t)))*(1+0.15*sin(2*PI*0.25*t))':s=44100:d=30",
       "-af", "afade=t=in:d=2,afade=t=out:st=27.5:d=2.5", "-shortest",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT]
if sys.argv[1:]:
    for s in sys.argv[1:]: frame(int(float(s) * FPS)).save(f"/workspace/work/nobel/p_{s}.png")
else:
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(N): pr.stdin.write(frame(i).tobytes())
    pr.stdin.close(); pr.wait(); print("exit", pr.returncode)
