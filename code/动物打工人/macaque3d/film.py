# 《动物打工人 No.01》阿萨姆猕猴：爱看朋友的猴子 — G 系列真 3D 黏土（clay_proto.render/post），on twos + boil
# 用法: python3 film.py test 0.5 3.2 ...   |  python3 film.py render i0 i1 out.mp4
import sys, math, subprocess, time, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world as Wd
from world import monkey2, cp
import easing as E
from cues import *

OW, OH, FPS = 1080, 1920, 30
RW, RH = 720, 1280
FOV = math.radians(44)
LIGHT = np.array([-0.55, 0.75, 0.55]); LIGHT /= np.linalg.norm(LIGHT)
FLAGS = np.array([1, 1, 1, 1, 1, 1, 1], np.int64)

def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def pr(t, a, b): return cl((t - a) / (b - a))
def ease(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return x * x * (3 - 2 * x)
def lerp(a, b, k): return a + (b - a) * k
def back(x): x = cl(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def grow(t, t0, d=0.4): return back(pr(t, t0, t0 + d)) if t >= t0 else 0.0     # 入场：0→1 带一点回弹，≥0.3 s
def hop(t, t0, d=0.45, h=0.25): u = pr(t, t0, t0 + d); return h * math.sin(math.pi * u) if 0 < u < 1 else 0.0
def V(*a): return np.array(a, float)
def armlerp(a, b, k, sx):
    """两种手臂姿势之间平滑过渡（避免定格里手臂一拍跳变）"""
    pa, pb = Wd.POSE[a], Wd.POSE[b]; k = eio(k)
    return tuple(lerp(pa[i], pb[i], k) for i in range(3))

# ================================================================== 3D 镜头（每个返回 cam, tgt, focus点, anchors）
def push(c, g, k):   # 沿视线推近 k（≤6%）
    c, g = V(*c), V(*g); return g + (c - g) * (1 - k)

def sh_hook(t):
    Wd.reset(); Wd.jungle(t)
    Wd.bush(-1.15, 0.5, 0.9, 1); Wd.fern(1.2, 0.9, 1.0, -0.4, 2)
    b1 = abs(math.sin(t * 9.0)) * 0.07; b2 = abs(math.sin(t * 9.0 + 1.6)) * 0.07
    jab = 0.06 * math.sin(t * 9.0)
    A = monkey2(-0.62, -0.35, 0.8, 0.75, "angry", y=b1, armL="fist", armR=(0.22, 0.66, 0.36 + jab), hroll=0.1 * math.sin(t * 9))
    B = monkey2(0.08, -0.4, 0.8, -0.75, "angry", y=b2, armL=(0.22, 0.66, 0.36 - jab), armR="fist", hroll=-0.1 * math.sin(t * 9 + 1.6))
    Wt = monkey2(0.5, 0.65, 0.72, -0.3, "wow", y=0.02 * math.sin(t * 5), hyaw=-0.8 + 0.06 * math.sin(t * 3))
    c = push((0.0, 1.3, 5.2), (0.0, 0.45, 0.0), 0.05 * eio(pr(t, 0, BIG1)))
    return c, V(0.0, 0.45, 0.0), V(-0.1, 0.7, 0.0), {"A": A, "B": B, "W": Wt}

def sh_reveal(t):
    t0 = T["reveal"]; Wd.reset(); Wd.jungle(t)
    Wd.fern(-1.1, 0.6, 1.0, 0.4, 3); Wd.bush(1.2, 0.2, 0.8, 4)
    G1, G2 = groom_pair(t, 0.15, -0.55, 0.82)
    Wt = monkey2(-0.42, 0.45, 0.7, 0.1, "happy" if t > t0 + 0.4 else "wow", hyaw=0.3, y=hop(t, t0 + 0.1, 0.4, 0.12))
    c = push((0.0, 1.2, 4.4), (0.05, 0.5, -0.2), 0.05 * eio(pr(t, t0, T["who"])))
    return c, V(0.05, 0.5, -0.2), V(0.1, 0.7, -0.4), {"G1": G1, "G2": G2, "W": Wt}

def groom_pair(t, xc, z, s):
    """G1(左) 给 G2(右) 理毛：手在 G2 肩背上来回梳；G2 眯眼歪头享受"""
    st = math.sin(t * 7.0)
    x1, x2 = xc - 0.36 * s / 0.82, xc + 0.3 * s / 0.82
    y1 = 0.15 * s
    tgt = (x2 - 0.2 * s + 0.03 * st * s, (0.62 + 0.08 * st) * s, z + 0.12 * s)
    G1 = monkey2(x1, z, s, 0.9, "happy", y=0.0, armR=Wd.to_local(x1, 0.0, z, s, 0.9, tgt), armL="rest", hyaw=-0.35)
    G2 = monkey2(x2, z + 0.05, s, -0.15, "happy", hroll=0.22 + 0.04 * st, hyaw=-0.25, squash=0.015 * (1 + st))
    return G1, G2

WHO_X = [(-0.6, 0.0), (-0.3, 0.4), (0.0, -0.05), (0.3, 0.4), (0.6, 0.0)]
WHO_E = ["look", "happy", "wow", "look", "happy"]
def sh_who(t):
    t0 = T["who"]; Wd.reset(); Wd.jungle(t, sky=(186, 220, 200))
    Wd.bush(-1.25, -0.6, 1.0, 5); Wd.bush(1.3, -0.5, 1.0, 6)
    an = {}
    for i, ((x, z), ex) in enumerate(zip(WHO_X, WHO_E)):
        k = grow(t, t0 + 0.15 + i * 0.22, 0.4)
        an[i] = monkey2(x, z, 0.55 * k, -x * 0.3, ex, badge=True, hyaw=0.25 * math.sin(t * 1.5 + i), y=hop(t, t0 + 2.6 + i * 0.12, 0.35, 0.08))
    c = push((0.0, 1.35, 5.0), (0.0, 0.5, 0.0), 0.05 * eio(pr(t, t0, T["timer"])))
    return c, V(0.0, 0.5, 0.0), V(0, 0.5, 0.2), an

def sh_timer(t):
    t0 = T["timer"]; Wd.reset()
    Wd.backdrop((250, 216, 150), z=-2.2); Wd.floor((232, 180, 110))
    hy = 0.55 * math.sin((t - t0) * 2.2)
    Wt = monkey2(-0.25, 0.25, 0.85, 0.3, "look", hyaw=hy, armR="out")
    ang = (t - t0) * 4.0
    Wd.stopwatch(0.5, 0.5, -0.2, 0.5 * grow(t, t0 + 0.1, 0.45), ang)
    c = push((0.05, 1.2, 4.3), (0.05, 0.62, 0.0), 0.05 * eio(pr(t, t0, T["q"])))
    return c, V(0.05, 0.62, 0.0), V(-0.2, 0.8, 0.2), {"W": Wt}

def sh_q(t):
    t0 = T["q"]; Wd.reset(); Wd.office(t)
    Wd.desk(); Wd.mug(-0.33, 0.6)
    a = monkey2(-0.52, 0.0, 0.82, 0.35, "look", y=0.2, hyaw=0.45 * math.sin((t - t0) * 2.5), badge=True)
    b = monkey2(0.0, 0.05, 0.82, 0.0, "wow", y=0.2 + hop(t, t0 + 1.2, 0.4, 0.08), badge=True)
    c_ = monkey2(0.52, 0.0, 0.82, -0.35, "look", y=0.2, hyaw=-0.45 * math.sin((t - t0) * 2.5 + 1), badge=True)
    c = push((0.0, 1.35, 4.4), (0.0, 0.8, 0.0), 0.05 * eio(pr(t, t0, BIG2)))
    return c, V(0.0, 0.8, 0.0), V(0, 0.95, 0.1), {"a": a, "b": b, "c": c_}

FR = [(-0.75, 0.05), (0.75, 0.05), (-0.42, -0.95), (0.42, -0.95)]
def net_scene(t, t0, thick):
    Wd.backdrop((255, 228, 204), z=-2.6); Wd.floor((240, 196, 150))
    Wt = monkey2(0.0, 0.1, 0.85, 0.0, "happy", armL="up", armR="up", y=hop(t, t0 + 0.05, 0.45, 0.15))
    an = {"W": Wt}
    for i, (x, z) in enumerate(FR):
        an[i] = monkey2(x, z, 0.68, -x * 0.7, "happy" if i % 2 == 0 else "look", hyaw=-x * 0.35, y=0.02 * math.sin(t * 4 + i))
    p = Wt["top"]
    for i, (x, z) in enumerate(FR):
        q = an[i]["top"]
        k = ease(pr(t, t0 + 0.25 + i * 0.18, t0 + 0.75 + i * 0.18)) if thick == 0 else 1.0
        Wd.arc_link(Wt["head"], an[i]["head"], 0.02 + thick, Wd.GOLDC, k, 0.55 + 0.1 * (i // 2))
    return an

def sh_big2(t):
    t0 = BIG2; Wd.reset()
    an = net_scene(t, t0, 0.0)
    c = push((0.0, 2.4, 4.5), (0.0, 0.3, -0.3), 0.05 * eio(pr(t, t0, T["bond"])))
    return c, V(0.0, 0.3, -0.3), V(0, 0.8, 0.0), an

def sh_bond(t):
    t0 = T["bond"]; Wd.reset()
    an = net_scene(t, t0, 0.022 * ease(pr(t, t0 + 0.5, t0 + 1.6)))
    c = push((0.7, 1.9, 3.7), (-0.1, 0.35, -0.35), 0.05 * eio(pr(t, t0, T["rank"])))
    return c, V(-0.1, 0.35, -0.35), V(0, 0.85, 0.0), an

STX = [-0.74, -0.12, 0.5]; STH = [0.32, 0.64, 0.96]
def sh_rank(t):
    t0 = T["rank"]; Wd.reset(); Wd.office(t, wall=(176, 206, 232))
    Wd.steps(-0.74, -0.2, 3, 0.31, 0.32)
    j1, j2 = t0 + 0.5, t0 + 1.5
    def pos(tt):
        if tt < j1: return STX[0], STH[0]
        if tt < j1 + 0.45: u = eio(pr(tt, j1, j1 + 0.45)); return lerp(STX[0], STX[1], u), lerp(STH[0], STH[1], u) + 0.35 * math.sin(math.pi * u)
        if tt < j2: return STX[1], STH[1]
        if tt < j2 + 0.45: u = eio(pr(tt, j2, j2 + 0.45)); return lerp(STX[1], STX[2], u), lerp(STH[1], STH[2], u) + 0.35 * math.sin(math.pi * u)
        return STX[2], STH[2]
    x, y = pos(t)
    top = t > j2 + 0.45; ku = pr(t, j2 + 0.45, j2 + 0.85)
    Wt = monkey2(x, -0.15, 0.62, -0.15, "happy" if top else "look", y=y, badge=True, armL=armlerp("rest", "up", ku, -1), armR=armlerp("rest", "up", ku, 1))
    c = push((0.0, 1.6, 4.6), (0.0, 1.0, -0.2), 0.05 * eio(pr(t, t0, T["mate"])))
    return c, V(0.0, 1.0, -0.2), V(x, y + 0.4, -0.15), {"W": Wt}

def sh_mate(t):
    t0 = T["mate"]; Wd.reset()
    Wd.backdrop((250, 210, 218), z=-2.4); Wd.floor((236, 182, 190))
    k = ease(pr(t, t0 + 0.2, t0 + 1.2))
    h1, h2 = 0.75 * k + 0.02, 0.90 * k + 0.02
    Wd.bar(-0.42, -0.2, 0.26, h1, 0.26, (196, 186, 222)); Wd.bar(0.42, -0.2, 0.26, h2, 0.26, (255, 200, 80))
    a = monkey2(-0.42, -0.2, 0.55, 0.1, "look", y=h1 - 0.02)
    b = monkey2(0.42, -0.2, 0.55, -0.1, "happy", y=h2 - 0.02 + hop(t, t0 + 1.5, 0.4, 0.1), armL=armlerp("rest", "up", pr(t, t0 + 1.5, t0 + 1.9), -1), armR=armlerp("rest", "up", pr(t, t0 + 1.5, t0 + 1.9), 1))
    c = push((0.0, 1.4, 4.6), (0.0, 0.8, -0.2), 0.05 * eio(pr(t, t0, T["fight"])))
    return c, V(0.0, 0.8, -0.2), V(0, 0.9, -0.2), {"a": a, "b": b, "h1": h1, "h2": h2}

def fight_pair(t, x0=0.0, z=0.0, s=0.88):
    b1 = abs(math.sin(t * 9.0)) * 0.07; b2 = abs(math.sin(t * 9.0 + 1.6)) * 0.07; jab = 0.06 * math.sin(t * 9.0)
    A = monkey2(x0 - 0.32, z, s, 0.85, "angry", y=b1, armL="fist", armR=(0.22, 0.66, 0.36 + jab), hroll=0.1 * math.sin(t * 9))
    B = monkey2(x0 + 0.32, z - 0.05, s, -0.85, "angry", y=b2, armL=(0.22, 0.66, 0.36 - jab), armR="fist", hroll=-0.1 * math.sin(t * 9 + 1.6))
    return A, B

def sh_fight(t):
    t0 = T["fight"]; Wd.reset(); Wd.jungle(t, sky=(200, 214, 196))
    Wd.bush(-1.2, 0.3, 0.9, 7)
    A, B = fight_pair(t, -0.12, -0.35, 0.8)
    Wt = monkey2(0.5, 0.6, 0.72, -0.3, "wow", hyaw=-0.75, y=0.02 * math.sin(t * 5))
    c = push((0.15, 1.15, 4.3), (0.0, 0.5, -0.1), 0.05 * eio(pr(t, t0, T["why"])))
    return c, V(0.0, 0.5, -0.1), V(0.1, 0.8, 0.0), {"A": A, "B": B, "W": Wt}

WAT = [(-0.82, -0.15, 0.55), (0.82, -0.15, -0.55), (-0.52, 0.75, 0.45), (0.52, 0.75, -0.45)]
def sh_why(t):
    t0 = T["why"]; Wd.reset(); Wd.jungle(t, sky=(196, 220, 204))
    A, B = fight_pair(t, 0.0, -0.75, 0.75)
    an = {"A": A, "B": B}
    for i, (x, z, yw) in enumerate(WAT):
        turn = eio(pr(t, t0 + 0.3 + i * 0.35, t0 + 0.6 + i * 0.35))
        ex = "wow" if turn > 0.5 else "look"
        hyaw = lerp(-yw * 0.6, yw * 1.25, turn) if abs(x) < 0.7 else lerp(-yw * 0.3, yw * 1.1, turn)
        an[i] = monkey2(x, z, 0.62, -yw * 0.3, ex, hyaw=hyaw, y=hop(t, t0 + 0.6 + i * 0.35, 0.3, 0.06), squash=0.0)
    c = push((0.0, 1.6, 5.0), (0.0, 0.5, -0.2), 0.05 * eio(pr(t, t0, T["card"])))
    return c, V(0.0, 0.5, -0.2), V(0, 0.7, -0.2), an

def sh_card(t):
    t0 = T["card"]; Wd.reset(); Wd.office(t, wall=(206, 196, 232))
    Wd.desk(0.0, 0.55, 0.95); Wd.mug(0.45, 0.62)
    Wt = monkey2(-0.05, 0.05, 0.9, 0.0, "look", y=0.2, badge=True, hroll=0.15 * math.sin((t - t0) * 1.8), hyaw=0.2 * math.sin((t - t0) * 1.1))
    c = push((0.0, 1.2, 3.4), (0.0, 1.45, 0.0), 0.04 * eio(pr(t, t0, T["end"])))
    return c, V(0.0, 1.45, 0.0), V(0, 1.0, 0.1), {"W": Wt}

def sh_end(t):
    t0 = T["end"]; Wd.reset(); Wd.jungle(t)
    A, B = fight_pair(t, -0.62, -0.9, 0.7)
    G1, G2 = groom_pair(t, 0.62, -0.9, 0.7)
    u = t - t0
    hy = -0.7 if u < 1.4 else (0.7 if u < 2.9 else 0.0)
    hy = lerp(0, -0.7, eio(pr(u, 0.2, 0.6))) if u < 1.4 else (lerp(-0.7, 0.7, eio(pr(u, 1.4, 1.8))) if u < 2.9 else lerp(0.7, 0.0, eio(pr(u, 2.9, 3.3))))
    Wt = monkey2(0.0, 0.45, 0.8, 0.0, "happy" if u > 3.2 else "look", hyaw=hy, armR=armlerp("rest", "wave", pr(u, 3.3, 3.7), 1), y=hop(t, t0 + 3.3, 0.4, 0.1))
    c = push((0.0, 1.35, 5.0), (0.0, 0.5, -0.2), 0.05 * eio(pr(t, t0, DUR)))
    return c, V(0.0, 0.5, -0.2), V(0, 0.9, 0.4), {"A": A, "B": B, "G1": G1, "G2": G2, "W": Wt}

# ================================================================== 渲染
def render3d(fn, tp, pose):
    cam, tgt, fpt, an = fn(tp)
    PI, PF, GR, G0, G1 = Wd.arr()
    rng = np.random.default_rng(1000 + pose)                     # boil：每拍一个种子
    mov = (GR[PI[:, 2], 3] < 2.0)[:, None]                      # 大背景/地板不抖
    PF[:, 0:3] += rng.normal(0, 0.0012, (len(PF), 3)) * mov
    camj = cam + rng.normal(0, 0.004, 3); tgtj = tgt + rng.normal(0, 0.002, 3)
    img = np.zeros((RH, RW, 3)); dep = np.zeros((RH, RW))
    cp.render(RW, RH, 0, RW, 0, RH, camj, tgtj, FOV, LIGHT, PI, PF, GR, G0, G1, img, dep, FLAGS, float(pose % 97))
    out = cp.post(img * (1 + rng.normal(0, 0.012)), dep, float(np.linalg.norm(cam - fpt)))
    return out, (camj, tgtj), an

def project(p, ct):
    cam, tgt = ct; f = tgt - cam; f /= np.linalg.norm(f)
    r = np.array([-f[2], 0.0, f[0]]); r /= np.linalg.norm(r); u = np.cross(r, f)
    d = np.array(p, float) - cam; z = d @ f
    tn = math.tan(FOV / 2)
    sx = (d @ r) / z / (tn * RW / RH); sy = (d @ u) / z / tn
    return ((sx + 1) / 2 * OW, (1 - sy) / 2 * OH)

# ================================================================== 2D UI（无黑描边）
_FD = os.environ.get("CLAY_FONT_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flytrap")   # Noto Sans SC 子集
FONTS = [os.path.join(_FD, "NotoSansSC-Bold.otf"), os.path.join(_FD, "NotoSansSC-Black.otf")]
_fc = {}
def F(size, k=1):
    if (size, k) not in _fc: _fc[(size, k)] = ImageFont.truetype(FONTS[k], max(4, int(size)))
    return _fc[(size, k)]
def A(c, a): return tuple(c[:3]) + (int(255 * cl(a)),)
WHITE = (250, 250, 244); GOLD = (255, 200, 60); RED = (236, 84, 70); GREEN = (96, 186, 96); NAVY = (24, 30, 52); PINK = (255, 120, 150); DARK = (14, 18, 30)
class D:
    def __init__(s, img): s.img = img; s.d = ImageDraw.Draw(img, "RGBA")
    def rect(s, x0, y0, x1, y1, fill, r=0): s.d.rounded_rectangle((x0, y0, x1, y1), radius=min(r, (x1 - x0) / 2, (y1 - y0) / 2), fill=fill)
    def circ(s, x, y, r, fill): s.d.ellipse((x - r, y - r, x + r, y + r), fill=fill)
    def poly(s, pts, fill): s.d.polygon(pts, fill=fill)
    def line(s, pts, fill, w): s.d.line(pts, fill=fill, width=int(w), joint="curve")
    def tlen(s, t, size, k=1): return s.d.textlength(t, font=F(size, k))
    def text(s, x, y, t, size, fill, anchor="mm", k=1):
        al = fill[3] if len(fill) > 3 else 255
        if al <= 2: return
        if al >= 253: s.d.text((x, y), t, font=F(size, k), fill=fill[:3], anchor=anchor); return
        b = [int(v) for v in s.d.textbbox((x, y), t, font=F(size, k), anchor=anchor)]; b[2] += 2; b[3] += 2
        m = Image.new("L", (b[2] - b[0], b[3] - b[1]), 0)
        ImageDraw.Draw(m).text((x - b[0], y - b[1]), t, font=F(size, k), fill=al, anchor=anchor)
        s.img.paste(fill[:3], tuple(b), m)

def tag(d, x, y, s, col, a=1.0, size=44, tc=NAVY, k=1.0):
    if a <= 0.01 or k <= 0.01: return
    size = int(size * (0.6 + 0.4 * k)); w = d.tlen(s, size) + size * 1.0
    d.rect(x - w / 2, y - size * 0.8, x + w / 2, y + size * 0.8, A(col, 0.95 * a), r=size * 0.8)
    d.text(x, y, s, size, A(tc, a))
def ptag(d, t, t0, x, y, s, col, size=44, tc=NAVY, t1=None):
    if t < t0: return
    k = max(0.0, E.spring_at(t, t0, 0, 1, "snappy")); a = cl((t - t0) / 0.15)
    if t1 is not None: a *= 1 - pr(t, t1 - 0.2, t1)
    tag(d, x, y + (1 - min(k, 1)) * 24, s, col, a, size, tc, min(1.1, k))
def bigword(d, t, t0, x, y, s, col, size=120, t1=None, bgc=DARK):
    if t < t0: return
    k = max(0.0, E.spring_at(t, t0, 0, 1, "bouncy")); a = cl((t - t0) / 0.12)
    if t0 <= 0.0: a = 1.0; k = 0.75 + 0.25 * k                 # 第 0 帧就要有大字
    if t1 is not None: a *= 1 - pr(t, t1 - 0.2, t1)
    sz = int(size * (0.55 + 0.45 * min(1.15, k)))
    w = d.tlen(s, sz) + 60
    d.rect(x - w / 2, y - sz * 0.72, x + w / 2, y + sz * 0.72, A(bgc, 0.5 * a), r=sz * 0.4)
    d.text(x, y, s, sz, A(col, a))
def heart(d, x, y, r, col, a=1.0):
    if a <= 0.01 or r < 1: return
    d.circ(x - r * 0.5, y - r * 0.2, r * 0.56, A(col, a)); d.circ(x + r * 0.5, y - r * 0.2, r * 0.56, A(col, a))
    d.poly([(x - r * 1.02, y - 0.05 * r), (x + r * 1.02, y - 0.05 * r), (x, y + r * 1.05)], A(col, a))
def hearts(d, x, y, t, t0, n=7, col=PINK, spread=220, dur=1.6):
    for j in range(n):
        u = (t - t0 - j * 0.07) / dur
        if 0 <= u < 1:
            ang = -math.pi / 2 + (j - (n - 1) / 2) * 0.42
            rr = spread * ease(u)
            heart(d, x + math.cos(ang) * rr, y + math.sin(ang) * rr - 60 * u, 26 * (1 - 0.3 * u) * min(1, u * 6), col, (1 - u) ** 0.7)
def dashed(d, p, q, col, a, w=6, dash=22, k=1.0):
    L = math.dist(p, q) * k
    if L < 2 or a <= 0.01: return
    ux, uy = (q[0] - p[0]) / math.dist(p, q), (q[1] - p[1]) / math.dist(p, q)
    s = 0.0
    while s < L:
        e = min(L, s + dash); d.line([(p[0] + ux * s, p[1] + uy * s), (p[0] + ux * e, p[1] + uy * e)], A(col, a), w); s += dash * 1.8
def arrow_up(d, x, y, h, col, a=1.0, w=26):
    if h > w * 1.2: d.rect(x - w / 2, y - h + w * 1.2, x + w / 2, y, A(col, a), r=w / 3)
    d.poly([(x - w * 1.4, y - h + w * 1.4), (x, y - h - w * 0.6), (x + w * 1.4, y - h + w * 1.4)], A(col, a))
def ring(d, x, y, t, t0, col=GOLD, maxr=360):
    u = (t - t0) / 0.7
    if 0 <= u < 1:
        for j in range(3):
            r = 40 + (u + j * 0.1) * maxr
            d.d.ellipse((x - r, y - r, x + r, y + r), outline=A(col, (1 - u) * (1 - j * 0.3)), width=max(1, 9 - j * 3))

# ---- 每个镜头的 2D 层（t 为实际时间，P(p) 把 3D 点投到 1080×1920）
def ui_hook(t, d, P, an):
    bigword(d, t, 0.0, 540, 420, "猴子吃瓜", WHITE, 140, t1=BIG1)
    ax, ay = P(an["A"]["top"]); bx, by = P(an["B"]["top"])
    mx, my = (ax + bx) / 2, min(ay, by) - 40
    wx, wy = P(an["W"]["head"])
    dashed(d, (wx - 40, wy - 10), (mx + 30, my + 70), WHITE, 0.8 * cl((t - 1.0) / 0.3), 6, 20, ease(pr(t, 1.0, 1.5)))
def ui_reveal(t, d, P, an):
    t0 = T["reveal"]
    g1 = P(an["G1"]["top"]); g2 = P(an["G2"]["top"]); mx, my = (g1[0] + g2[0]) / 2, min(g1[1], g2[1]) - 30
    ring(d, mx, my + 120, t, t0, GOLD, 380)
    hearts(d, mx, my + 40, t, t0 + 0.05, 9); hearts(d, mx, my + 40, t, t0 + 1.6, 5, PINK, 160)
    ptag(d, t, t0 + 0.7, mx, my - 40, "理毛", WHITE, 46)
    wx, wy = P(an["W"]["head"])
    dashed(d, (wx + 30, wy - 20), (mx, my + 110), GOLD, 0.85, 6, 20, ease(pr(t, t0 + 0.9, t0 + 1.4)))
def ui_who(t, d, P, an):
    t0 = T["who"]
    n = int(round(46 * ease(pr(t, t0 + 0.2, t0 + 2.6))))
    a = cl((t - t0) / 0.25)
    d.rect(370, 330, 710, 530, A(DARK, 0.5 * a), r=50)
    d.text(500, 430, f"{n}", 170, A(GOLD, a)); d.text(650, 462, "只", 60, A(WHITE, a))
def ui_timer(t, d, P, an):
    t0 = T["timer"]
    a = cl((t - t0 - 0.2) / 0.3)
    rows = [("理毛", GREEN, -0.4), ("打架", RED, -0.05)]
    for j, (lab, col, dl) in enumerate(rows):
        y = 420 + j * 100; k = ease(pr(t, t0 + 0.8 + dl, t0 + 3.2 + dl))
        if a <= 0: continue
        d.rect(220, y - 34, 860, y + 34, A(DARK, 0.45 * a), r=34)
        d.text(290, y, lab, 38, A(WHITE, a))
        d.rect(362, y - 18, 362 + 470 * k, y + 18, A(col, a), r=18)
def ui_q(t, d, P, an):
    t0 = T["q"]
    for i, k in enumerate(["a", "b", "c"]):
        x, y = P(an[k]["top"]); tt = t0 + 0.5 + i * 0.25
        if t >= tt:
            kk = max(0.0, E.spring_at(t, tt, 0, 1, "bouncy")); bob = 8 * math.sin((t - tt) * 5 + i)
            d.text(x, y - 40 + bob, "?", int(90 * min(1.1, kk)), A(GOLD, cl((t - tt) / 0.15)))
def ui_big2(t, d, P, an):
    t0 = BIG2
    wx, wy = P(an["W"]["top"])
    ring(d, wx, wy + 150, t, t0, GOLD, 420)
    hearts(d, wx, wy, t, t0 + 0.05, 9, GOLD, 260)
    bigword(d, t, t0, 540, 400, "爱看朋友的猴子！", GOLD, 110)
def ui_bond(t, d, P, an):
    t0 = T["bond"]
    ptag(d, t, t0 + 0.1, 540, 360, "第 1 年", WHITE, 52)
    wx, wy = P(an["W"]["head"])
    hearts(d, wx, wy - 120, t, t0 + 0.7, 5, PINK, 180)
def ui_rank(t, d, P, an):
    t0 = T["rank"]
    ptag(d, t, t0 + 0.1, 540, 320, "第 2 年", WHITE, 52)
    x, y = P(an["W"]["top"])
    for i, tt in enumerate([t0 + 0.5, t0 + 1.5]):
        if tt < t < tt + 0.6: ring(d, x, y + 160, t, tt + 0.3, WHITE, 200)
    arrow_up(d, 250, 1100, 300 * ease(pr(t, t0 + 0.4, t0 + 2.2)) + 1, GOLD, cl((t - t0 - 0.4) / 0.2), 30)
def ui_mate(t, d, P, an):
    t0 = T["mate"]
    a_ = cl((t - t0) / 0.3)
    xa, ya = P((-0.42, 0.0, 0.1)); xb, yb = P((0.42, 0.0, 0.1))
    ya2 = P((-0.42, an["h1"] * 0.5, 0.08))[1]; yb2 = P((0.42, an["h2"] * 0.5, 0.08))[1]
    tag(d, xa, min(ya2, 1180), "地位低", WHITE, a_, 38)
    tag(d, xb, min(yb2, 1180), "地位高", WHITE, a_, 38)
    tp = P(an["b"]["head"]) if an["b"] else (700, 800)
    bigword(d, t, t0 + 1.4, 540, 400, "+20%", GOLD, 130)
    hearts(d, tp[0], tp[1] - 40, t, t0 + 1.5, 7, PINK, 130); hearts(d, tp[0], tp[1] - 40, t, t0 + 2.8, 5, PINK, 110)
def ui_fight(t, d, P, an):
    t0 = T["fight"]
    ax, ay = P(an["A"]["top"]); bx, by = P(an["B"]["top"]); mx, my = (ax + bx) / 2, min(ay, by) - 40
    if t > t0 + 2.0:
        a = cl((t - t0 - 2.0) / 0.2)
        d.rect(200, 330, 880, 500, A(DARK, 0.5 * a), r=40)
        d.text(345, 415, "看吵架", 72, A(WHITE, a))
        k = back(pr(t, t0 + 2.2, t0 + 2.6))
        d.text(540, 415, "≠", int(110 * k) + 1, A(GOLD, a), k=0)
        d.text(735, 415, "地位高", 72, A(WHITE, a))
def ui_why(t, d, P, an):
    t0 = T["why"]
    ax, ay = P(an["A"]["head"]); bx, by = P(an["B"]["head"]); mx, my = (ax + bx) / 2, (ay + by) / 2
    for i in range(4):
        tt = t0 + 0.6 + i * 0.35
        hx, hy = P(an[i]["head"])
        dashed(d, (hx, hy - 20), (mx, my), WHITE, 0.75 * cl((t - tt) / 0.2), 5, 18, ease(pr(t, tt, tt + 0.4)))
    for i in range(4):
        tt = t0 + 0.8 + i * 0.35; hx, hy = P(an[i]["top"])
        if t >= tt: d.text(hx, hy - 30 + 6 * math.sin((t - tt) * 6), "!", int(70 * min(1.1, max(0.0, E.spring_at(t, tt, 0, 1, "bouncy")))) + 1, A(GOLD, cl((t - tt) / 0.15)))
def ui_card(t, d, P, an):
    t0 = T["card"]; a = cl((t - t0 - 0.1) / 0.3) * (1 - pr(t, T["end"] - 0.25, T["end"])); dy = 30 * (1 - ease(pr(t, t0 + 0.1, t0 + 0.5)))
    if a <= 0: return
    d.rect(200, 290 + dy, 880, 650 + dy, A(WHITE, 0.94 * a), r=44)
    d.rect(380, 320 + dy, 700, 384 + dy, A(GOLD, a), r=32); d.text(540, 352 + dy, "一句话学会", 38, A(NAVY, a))
    d.text(540, 470 + dy, "这是“有关联”", 64, A(NAVY, a))
    d.text(540, 560 + dy, "不是“看了就升职”", 58, A(RED, a))
def ui_end(t, d, P, an):
    t0 = T["end"]
    ptag(d, t, t0 + 0.8, 360, 420, "爱看吵架", RED, 52, WHITE)
    ptag(d, t, t0 + 1.2, 720, 420, "爱看好朋友", GREEN, 52, WHITE)
    if t > DUR - 0.6: d.rect(0, 0, OW, OH, A((0, 0, 0), pr(t, DUR - 0.6, DUR)))

HL = {"hook": "爱看吵架", "reveal": "好朋友", "who": "46只公猴", "timer": "看了多久", "q": "混得更好", "big2": "爱看朋友",
      "bond": "更铁", "rank": "更高", "mate": "约20%", "fight": "没关系", "why": "卷进去", "card": "有关联", "end": "围观猴"}
def subs(t, d):
    for a, b, s, key in SUBS:
        if key in ("card", "big2"): continue
        if a <= t < b:
            ee = E.enter_exit(t, max(a, 0), b, 0.3, 0.12, rise=18, s0=0.96)
            al = ee["alpha"] if a > 0 else (1 - pr(t, b - 0.12, b))
            if al <= 0.01: return
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70 + ee["dy"] * (a > 0)
            w = max(d.tlen(x, 54) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 70 + 46, A((10, 16, 28), 0.8 * al), r=22)
            hw = HL.get(key)
            for i, x in enumerate(ls):
                yy = y0 + i * 70
                if hw and hw in x:
                    j = x.index(hw); xx = 540 - d.tlen(x, 54) / 2
                    for p_, c_ in [(x[:j], WHITE), (hw, GOLD), (x[j + len(hw):], WHITE)]:
                        if p_: d.text(xx, yy, p_, 54, A(c_, al), anchor="lm"); xx += d.tlen(p_, 54)
                else: d.text(540, yy, x, 54, A(WHITE, al))
            break
def brand(t, d):
    s = "动物打工人 No.01"; w = d.tlen(s, 30) + 56
    d.rect(540 - w / 2, 150, 540 + w / 2, 204, A((20, 16, 30), 0.55), r=27); d.text(540, 177, s, 30, A(WHITE, 1))
    d.text(540, 234, "Vibe 知识大赏 · 爱看朋友的猴子", 24, A((250, 250, 240), 0.85), k=0)

SF = {n: globals()["sh_" + n] for n in NAMES}; UF = {n: globals()["ui_" + n] for n in NAMES}
SECS = [(-1.0, nxt(n), SF[n], UF[n], n) if i == 0 else (T[n], (99 if i == len(NAMES) - 1 else nxt(n)), SF[n], UF[n], n) for i, n in enumerate(NAMES)]
HARD = {BIG1, BIG2}
XF = 0.3
def shot_at(t): return next(i for i, s in enumerate(SECS) if s[0] <= t < s[1])
_cache = {}
def world(idx, tp, pose):
    key = (idx, round(tp, 4), pose)
    if key not in _cache:
        if len(_cache) > 6: _cache.clear()
        _cache[key] = render3d(SECS[idx][2], tp, pose)
    return _cache[key]
def frame(fi):
    t = fi / FPS; pose = fi // 2; tp = pose * 2 / FPS
    idx = shot_at(t)
    if SECS[idx][0] > tp: tp = t                          # 镜头起点落在奇数帧：该帧单独渲染，切点与音乐对齐
    img, ct, an = world(idx, tp, pose)
    a = SECS[idx][0]
    img = img.copy()
    if idx > 0 and a not in HARD and tp < a + XF:          # 软切：和上一镜头最后一拍叠化
        pimg, _, _ = world(idx - 1, a - 2 / FPS, int(round((a - 2 / FPS) * FPS)) // 2)
        k = E.ease_in_out_sine(cl((t - a) / XF))
        img = (pimg.astype(np.float32) * (1 - k) + img.astype(np.float32) * k).astype(np.uint8)
    # 大重音：冲击变焦 4% + 抖 8px（只两处）
    z = 1.0; sx = sy = 0.0
    for h in HARD:
        if h <= t < h + 0.6:
            u = t - h; z += 0.04 * math.exp(-u * 6); amp = 8 * math.exp(-u * 7)
            sx += amp * math.sin(u * 70); sy += amp * math.cos(u * 53)
    if z > 1.0005 or abs(sx) > 0.3:
        M = np.array([[z, 0, OW / 2 * (1 - z) + sx], [0, z, OH / 2 * (1 - z) + sy]], np.float32)
        img = cv2.warpAffine(img, M, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    pil = Image.fromarray(img); d = D(pil)
    P = lambda p: project(p, ct)
    if idx > 0 and a not in HARD and tp < a + XF:          # 软切：上一镜头的 2D 层也一起叠化（不让字/标签一帧消失）
        _, pct, pan = world(idx - 1, a - 2 / FPS, int(round((a - 2 / FPS) * FPS)) // 2)
        prev = pil.copy(); SECS[idx - 1][3](t, D(prev), lambda p: project(p, pct), pan)
        SECS[idx][3](t, d, P, an)
        pil = Image.blend(prev, pil, E.ease_in_out_sine(cl((t - a) / XF))); d = D(pil)
    else:
        SECS[idx][3](t, d, P, an)
    for h in HARD:
        if h <= t < h + 0.1: d.rect(0, 0, OW, OH, A(WHITE, 0.5 * (1 - (t - h) / 0.1)))
    brand(t, d); subs(t, d)
    return pil

if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]:
            t0 = time.time(); fi = int(round(float(ts) * FPS)); fi -= fi % 2
            frame(fi).save(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"test_{float(ts):05.2f}.png")); print(ts, round(time.time() - t0, 1), flush=True)
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                              "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", out], stdin=subprocess.PIPE)
        t0 = time.time()
        for i in range(i0, i1):
            p.stdin.write(np.asarray(frame(i)).tobytes())
            if i % 10 == 0: print("frame", i, round(time.time() - t0, 1), flush=True)
        p.stdin.close(); p.wait(); print("done", i0, i1, round(time.time() - t0, 1), flush=True)
