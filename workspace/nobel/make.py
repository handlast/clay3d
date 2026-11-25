import math, random, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

W, H, FPS, DUR = 1920, 1080, 30, 10.0
N = int(FPS * DUR)
FONT = "/workspace/work/nobel/NotoSerifSC.otf"
LAT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
GOLD = (222, 184, 98)
GOLD_L = (255, 230, 160)
random.seed(7)

def f(path, size): return ImageFont.truetype(path, size)
F_TITLE = f(FONT, 150); F_SUB = f(LAT, 40); F_CAT = f(FONT, 64); F_CATEN = f(LAT, 26)
F_BIG = f(FONT, 120); F_LINE = f(FONT, 50); F_RING = f(LAT, 30)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def prog(t, a, b): return clamp((t - a) / (b - a))

# background: deep navy radial gradient
g = Image.radial_gradient("L").resize((W * 2, W * 2)).crop((W // 2, W - H // 2 - 0, W // 2 + W, W - H // 2 + H))
BG = ImageOps.colorize(g, black=(26, 28, 52), white=(4, 5, 12)).convert("RGBA")

# medal
def make_medal(R):
    s = R * 2
    m = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    rg = Image.radial_gradient("L").resize((s, s))
    gold = ImageOps.colorize(rg, black=(255, 228, 150), white=(150, 105, 35)).convert("RGBA")
    mask = Image.new("L", (s, s), 0); ImageDraw.Draw(mask).ellipse((0, 0, s - 1, s - 1), fill=255)
    m.paste(gold, (0, 0), mask)
    d = ImageDraw.Draw(m)
    for r, w in ((R - 8, 6), (R - 70, 3)):
        d.ellipse((R - r, R - r, R + r, R + r), outline=(120, 82, 25, 255), width=w)
    # ring text
    text = "ALFRED NOBEL  •  1833 – 1896  •  "
    n = len(text); rr = R - 40
    for i, ch in enumerate(text):
        ang = -90 + 360 * i / n
        ci = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
        ImageDraw.Draw(ci).text((25, 25), ch, font=F_RING, fill=(110, 75, 20, 255), anchor="mm")
        ci = ci.rotate(-(ang + 90), resample=Image.BICUBIC)
        x = R + rr * math.cos(math.radians(ang)); y = R + rr * math.sin(math.radians(ang))
        m.alpha_composite(ci, (int(x - 25), int(y - 25)))
    # center: stylized laurel + "N"
    d.text((R, R + 6), "N", font=f(LAT, int(R * 0.9)), fill=(125, 85, 25, 255), anchor="mm")
    return m
MEDAL = make_medal(260)

particles = [dict(x=random.uniform(0, W), y=random.uniform(0, H), r=random.uniform(1.5, 4.5),
                  v=random.uniform(15, 60), a=random.uniform(60, 200), ph=random.uniform(0, 6.28)) for _ in range(140)]

CATS = [("物理学", "Physics"), ("化学", "Chemistry"), ("生理学或医学", "Physiology or Medicine"),
        ("文学", "Literature"), ("和平", "Peace"), ("经济学", "Economic Sciences")]

def text_layer(draw_fn):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(L)); return L

def with_alpha(img, a):
    if a >= 1: return img
    r, g_, b, al = img.split(); al = al.point(lambda v: int(v * a)); return Image.merge("RGBA", (r, g_, b, al))

def frame(i):
    t = i / FPS
    im = BG.copy()
    # particles
    P = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(P)
    for p in particles:
        y = (p["y"] - p["v"] * t) % H; x = p["x"] + 12 * math.sin(t * 0.8 + p["ph"])
        a = int(p["a"] * (0.6 + 0.4 * math.sin(t * 3 + p["ph"])))
        pd.ellipse((x - p["r"], y - p["r"], x + p["r"], y + p["r"]), fill=GOLD_L + (a,))
    im.alpha_composite(P.filter(ImageFilter.GaussianBlur(1.2)))

    # ---- scene 1: medal + title (0 - 3.4s)
    s1 = ease(prog(t, 0.0, 1.2)) * (1 - ease(prog(t, 3.0, 3.5)))
    if s1 > 0:
        sc = 0.6 + 0.4 * ease(prog(t, 0.0, 1.4))
        R = int(260 * sc)
        md = MEDAL.resize((R * 2, R * 2), Image.LANCZOS)
        # shine sweep
        sh = Image.new("RGBA", md.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        sx = -R * 2 + 4 * R * prog(t, 0.8, 2.2)
        sd.polygon([(sx, 0), (sx + R * 0.35, 0), (sx + R * 0.35 - R * 0.8, R * 2), (sx - R * 0.8, R * 2)], fill=(255, 255, 255, 90))
        sh = sh.filter(ImageFilter.GaussianBlur(12))
        sh.putalpha(Image.composite(sh.getchannel("A"), Image.new("L", md.size, 0), md.getchannel("A")))
        md.alpha_composite(sh)
        # glow
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((W // 2 - R - 40, 380 - R - 40, W // 2 + R + 40, 380 + R + 40), fill=GOLD + (70,))
        im.alpha_composite(with_alpha(glow.filter(ImageFilter.GaussianBlur(50)), s1))
        im.alpha_composite(with_alpha(md, s1), (W // 2 - R, 380 - R))
        ta = ease(prog(t, 1.0, 1.9)) * (1 - ease(prog(t, 3.0, 3.5)))
        dy = int(30 * (1 - ease(prog(t, 1.0, 1.9))))
        if ta > 0:
            L = text_layer(lambda d: (d.text((W // 2, 790 + dy), "诺 贝 尔 奖", font=F_TITLE, fill=GOLD_L, anchor="mm"),
                                      d.text((W // 2, 905 + dy), "T H E   N O B E L   P R I Z E", font=F_SUB, fill=GOLD, anchor="mm")))
            im.alpha_composite(with_alpha(L, ta))

    # ---- scene 2: six categories (3.4 - 7.6s)
    if 3.3 < t < 7.8:
        out = 1 - ease(prog(t, 7.2, 7.7))
        hd = ease(prog(t, 3.4, 4.0)) * out
        L = text_layer(lambda d: (d.text((W // 2, 170), "六 大 奖 项", font=F_LINE, fill=GOLD_L, anchor="mm"),
                                  d.line((W // 2 - 300 * hd, 225, W // 2 + 300 * hd, 225), fill=GOLD, width=2)))
        im.alpha_composite(with_alpha(L, hd))
        for k, (zh, en) in enumerate(CATS):
            a = ease(prog(t, 3.7 + k * 0.32, 4.3 + k * 0.32)) * out
            if a <= 0: continue
            col, row = k % 3, k // 3
            cx = W // 2 + (col - 1) * 560; cy = 440 + row * 330 + int(40 * (1 - a))
            def dr(d, cx=cx, cy=cy, zh=zh, en=en):
                d.rounded_rectangle((cx - 250, cy - 120, cx + 250, cy + 120), radius=18, outline=GOLD + (200,), width=2, fill=(255, 220, 140, 14))
                d.text((cx, cy - 22), zh, font=F_CAT, fill=GOLD_L, anchor="mm")
                d.text((cx, cy + 60), en, font=F_CATEN, fill=GOLD, anchor="mm")
            im.alpha_composite(with_alpha(text_layer(dr), a))

    # ---- scene 3: closing (7.6 - 10s)
    a3 = ease(prog(t, 7.7, 8.4)) * (1 - ease(prog(t, 9.4, 10.0)))
    if a3 > 0:
        dy = int(25 * (1 - ease(prog(t, 7.7, 8.5))))
        la = ease(prog(t, 8.2, 8.9))
        L = text_layer(lambda d: (d.text((W // 2, 430 + dy), "自 1901 年起", font=F_BIG, fill=GOLD_L, anchor="mm"),
                                  d.line((W // 2 - 380 * la, 545, W // 2 + 380 * la, 545), fill=GOLD, width=2)))
        im.alpha_composite(with_alpha(L, a3))
        a4 = ease(prog(t, 8.4, 9.1)) * (1 - ease(prog(t, 9.4, 10.0)))
        L2 = text_layer(lambda d: d.text((W // 2, 640), "表彰为人类带来最大福祉的人", font=F_LINE, fill=GOLD, anchor="mm"))
        im.alpha_composite(with_alpha(L2, a4))

    # global fade-in
    if t < 0.4:
        im = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), im, t / 0.4)
    return im.convert("RGB")

cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-f", "lavfi", "-i",
       "aevalsrc='0.12*(sin(2*PI*130.81*t)+0.8*sin(2*PI*196*t)+0.6*sin(2*PI*261.63*t)+0.4*sin(2*PI*329.63*t))*(1+0.1*sin(2*PI*0.5*t))':s=44100:d=10",
       "-af", "afade=t=in:d=1.5,afade=t=out:st=8.5:d=1.5", "-shortest",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "/workspace/work/nobel/nobel_10s.mp4"]
import sys
only = sys.argv[1:] 
if only:
    for s in only: frame(int(float(s) * FPS)).save(f"/workspace/work/nobel/test_{s}.png")
else:
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(N): pr.stdin.write(frame(i).tobytes())
    pr.stdin.close(); pr.wait(); print("exit", pr.returncode)
