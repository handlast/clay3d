# 《动物打工人 No.03》公司的“房子”生病了，小丑鱼加班守家？— G 系列真 3D 黏土（海底办公室），on twos + boil
# 面部永不糊：engine/clay_face.py —— 脸部区域在 2× 输出分辨率超采样贴回，景深 CoC/柔光/水雾在脸部蒙版内强制为 0，对焦点=主角脸
# 用法: python3 film.py test 0.5 3.2 ...   |  python3 film.py faces 0.5 3.2 ...（脸部放大 2× 自检） |  python3 film.py render i0 i1 out.mp4
import sys, math, subprocess, time, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world as Wd
from world import cp, cf, clownfish, anemone
import easing as E
from cues import *
import json
import clearance as CL                 # 穿模约束（clay3d-repo/engine/clearance.py）
from scenes.reef import LAST as REEF_LAST

# ---- 穿模约束：每条鱼记下自己的图元区间；渲染时按预计算的抬升轨迹 clear_track.json 平移（python3 film.py clr <镜号>）
MARGIN = 0.03                          # 鱼身与海葵触手/珊瑚/岩石/沙地/道具的最小 SDF 间距（世界单位，鱼宽约 0.3）
_FISH = []
def clownfish(*a, **k):
    r, rng = CL.owned(Wd.clownfish, *a, **k)
    _FISH.append((rng, r) if r is not None else None)
    return r
CLR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clear_track.json")
CLR = json.load(open(CLR_PATH)) if os.path.exists(CLR_PATH) else {}
def run_shot(name, fn, t, apply=True):
    _FISH.clear()
    out = fn(t)
    tr = CLR.get(name)
    if apply and tr:
        for i, f in enumerate(_FISH):
            if f is None or i >= len(tr["d"]): continue
            d = float(np.interp(t, tr["ts"], tr["d"][i]))
            v = np.array(tr["dir"][i], float); v /= np.linalg.norm(v)
            if d > 1e-4: CL.translate(f[0], v * d, f[1])
    return out

HERE = os.path.dirname(os.path.abspath(__file__))
OW, OH, FPS = 1080, 1920, 30
RW, RH = 720, 1280
FOV = math.radians(44)
LIGHT = np.array([-0.5, 0.8, 0.5]); LIGHT /= np.linalg.norm(LIGHT)
FLAGS = np.array([1, 1, 1, 1, 1, 1, 1], np.int64)
FOG = ((70, 160, 205), 1.2, 5.0, 0.38)          # 水下雾：焦平面后 1.2 起，5.0 内渐进，最多 38%

def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def pr(t, a, b): return cl((t - a) / (b - a))
def ease(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return x * x * (3 - 2 * x)
def lerp(a, b, k): return a + (b - a) * k
def back(x): x = cl(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def grow(t, t0, d=0.4): return back(pr(t, t0, t0 + d)) if t >= t0 else 0.0     # 入场 ≥0.3 s
def hop(t, t0, d=0.45, h=0.25): u = pr(t, t0, t0 + d); return h * math.sin(math.pi * u) if 0 < u < 1 else 0.0
def V(*a): return np.array(a, float)
def push(c, g, k): c, g = V(*c), V(*g); return g + (c - g) * (1 - k)
def swim(t, ph=0.0, sp=1.0): return dict(tail=math.sin(t * 7 * sp + ph), flap=math.sin(t * 9 * sp + ph * 1.3))
def warp(t, t1, k, ramp=0.3):
    """相位连续的变速：t1 之后摆动速度在 ramp 秒内平滑变成 k 倍（直接改 sp 会让 sin(t·sp) 相位一帧跳变 = 尾巴抽一下）"""
    if t <= t1: return t
    x = t - t1
    if x < ramp: return t1 + x + (k - 1) * x * x / (2 * ramp)
    return t1 + ramp + (k - 1) * ramp / 2 + k * (x - ramp)
def bob(t, ph=0.0, a=0.03): return a * math.sin(t * 2.6 + ph)
SF_S = 0.44                                         # 主角小丑鱼尺寸

# ================================================================== 镜头（返回 cam, tgt, 对焦点, anchors）
def sh_hook(t):
    Wd.reset(); Wd.reef(t, bubbles=8)
    kb = eio(pr(t, 0.05, 2.6))
    A = anemone(-0.12, -0.45, 1.0, kb, t, face=True, expr="look" if t < 1.0 else "worry", spread=0.8)
    wow = t > 1.1
    F = clownfish(0.36, 0.35, SF_S, -0.55 + 0.2 * eio(pr(t, 1.0, 1.3)), "wow" if wow else "look", y=0.42 + bob(t) + hop(t, 1.1, 0.4, 0.08),
                  gaze=(-0.9, 0.2) if not wow else (0, 0), **swim(t))
    P = clownfish(-0.36, 0.5, 0.34, 0.7, "wow" if t > 1.4 else "look", y=0.62 + bob(t, 1.5), gaze=(0.8, 0.3) if t < 1.4 else (0, 0), **swim(t, 2.0))
    c = push((0.05, 0.95, 3.7), (0.0, 0.32, -0.3), 0.05 * eio(pr(t, 0, BIG1)))
    return c, V(0.0, 0.32, -0.3), F["face"], {"A": A, "F": F, "P": P}

def sh_big1(t):
    t0 = BIG1; Wd.reset(); Wd.reef(t, bubbles=6, kelp=False)
    A = anemone(0.0, -0.25, 1.0, 1.0, t, face=True, expr="worry", droop=0.35 * eio(pr(t, t0, t0 + 1.5)))
    lv = 0.35 + 0.6 * ease(pr(t, t0 + 0.3, t0 + 2.2))
    Wd.thermometer(0.0, 0.08, 0.3, 0.5, lv, tilt=1.95 + 0.05 * math.sin(t * 3))
    F = clownfish(0.3, 0.38, 0.36, -0.95, "worry", y=0.42 + bob(t), gaze=(-0.8, -0.2), **swim(t, 0, 0.7))
    c = push((0.1, 0.62, 2.9), (0.05, 0.12, -0.25), 0.05 * eio(pr(t, t0, T["where"])))
    return c, V(0.05, 0.12, -0.25), A["face"], {"A": A, "F": F, "lv": lv}

REEF4 = [(-0.75, -1.0, 0.6, 1.0), (0.75, -1.1, 0.6, 0.0), (-0.4, 0.35, 0.5, 0.0), (0.45, 0.25, 0.5, 1.0)]
def sh_where(t):
    t0 = T["where"]; Wd.reset(); Wd.reef(t, bubbles=12)
    an = {}
    for i, (x, z, s, b) in enumerate(REEF4):
        an[i] = anemone(x, z, s, b, t, face=False, seed=i + 1)
        an["f%d" % i] = clownfish(x + 0.1 * s, z + 0.35 * s, 0.3 * s / 0.62, -0.4, "worry" if b > 0.5 else "look",
                                  y=0.75 * s + bob(t, i * 1.7), **swim(t, i))
    c = push((0.0, 2.2, 4.9), (0.0, 0.05, -0.4), 0.05 * eio(pr(t, t0, T["cam"])))
    return c, V(0.0, 0.05, -0.4), an["f3"]["face"], an

FAM = [(-0.1, 0.6, 0.42, 0.0, 0.42), (0.3, 0.5, 0.35, 1.1, 0.55), (0.55, 0.74, 0.28, 2.3, 0.12)]     # 一家三口拉开间距（原来身体互相重叠），x/y/尺寸/相位/z     # 一家三口拉开间距（原来身体互相重叠）
def sh_cam(t):
    t0 = T["cam"]; Wd.reset(); Wd.reef(t, bubbles=6)
    A = anemone(0.4, -0.6, 0.85, 0.0, t, face=False, seed=2)
    Wd.camcorder(-0.42, 0.55, 0.7, 0.55, rec=0.5 + 0.5 * math.sin(t * 6), h=0.45)
    an = {"A": A}
    for i, (x, yy, s, ph, fz) in enumerate(FAM):
        k = grow(t, t0 + 0.2 + i * 0.25, 0.45)
        an[i] = clownfish(x, fz, s * k, -0.45, "happy" if i == 1 else "look", y=yy + bob(t, ph), **swim(t, ph))
    c = push((-0.05, 0.95, 3.6), (0.1, 0.3, -0.2), 0.05 * eio(pr(t, t0, T["q"])))
    return c, V(0.1, 0.3, -0.2), (an[0]["face"] if an[0] else [-0.02, 0.65, 0.15]), an     # 第一条鱼弹入前对焦在它将出现的位置

def sh_q(t):
    t0 = T["q"]; Wd.reset(); Wd.reef(t, bubbles=6)
    A = anemone(0.0, -0.6, 1.0, 1.0, t, face=False, droop=0.35, seed=4)
    gx = math.sin((t - t0) * 2.4)
    F = clownfish(0.0, 0.62, 0.5, 0.0, "look", y=0.5 + bob(t), gaze=(gx, 0.1), **swim(t, 0, 0.6))      # 停在海葵前方（原 z=0.35 尾巴插进触手）
    c = push((0.0, 0.85, 2.9), (0.0, 0.48, 0.1), 0.05 * eio(pr(t, t0, BIG2)))      # 鱼前移到海葵前方后，镜头退一点，问号不压品牌条
    return c, V(0.0, 0.48, 0.1), F["face"], {"A": A, "F": F}

def sh_big2(t):
    t0 = BIG2; Wd.reset(); Wd.reef(t, bubbles=8)
    A = anemone(0.0, -0.75, 1.0, 1.0, t, face=False, droop=0.3, seed=4)
    hm = cl(back(pr(t, t0 + 0.05, t0 + 0.45)), 0, 1.15)
    F = clownfish(0.0, 0.35, 0.52, 0.25 * math.sin((t - t0) * 2.0), "fierce", y=0.42 + hop(t, t0, 0.5, 0.16) + bob(t),
                  helmet=min(1.0, hm), squash=-0.08 * math.exp(-max(0, t - t0) * 6) if t > t0 else 0.0, **swim(t, 0, 1.6))
    c = push((0.0, 0.62, 2.75), (0.0, 0.62, 0.0), 0.05 * eio(pr(t, t0, T["care"])))
    return c, V(0.0, 0.62, 0.0), F["face"], {"A": A, "F": F}

def sh_care(t):
    t0 = T["care"]; Wd.reset(); Wd.reef(t, bubbles=10)
    A = anemone(0.0, -0.55, 1.0, 1.0, t, face=False, droop=0.25, seed=4)
    F = clownfish(0.38, 0.05, 0.4, -0.85, "fierce", y=0.78 + bob(t), helmet=1.0, tail=math.sin(t * 9), flap=math.sin(t * 22))
    nib = 0.06 * max(0.0, math.sin((t - t0) * 5.0))
    P = clownfish(-0.36 + nib, 0.0, 0.34, 0.9, "happy", y=0.9 + bob(t, 1.0), **swim(t, 1.0))
    c = push((0.0, 1.15, 3.4), (0.0, 0.45, -0.3), 0.05 * eio(pr(t, t0, T["guard"])))
    return c, V(0.0, 0.45, -0.3), F["face"], {"A": A, "F": F, "P": P}

DAMSEL = dict(body=(70, 118, 226), fin=(255, 206, 60), bands=False)
def sh_guard(t):
    t0 = T["guard"]; Wd.reset(); Wd.reef(t, bubbles=6)
    A = anemone(0.3, -0.7, 0.9, 1.0, t, face=False, droop=0.2, seed=4)
    u = t - t0
    ix = lerp(-1.25, -0.45, ease(pr(u, 0.0, 1.1))) - 1.8 * eio(pr(u, 1.7, 2.9))     # 入侵者游进来，再被赶出画面
    I = clownfish(ix, 0.2, 0.36, lerp(1.2, -1.4, eio(pr(u, 1.5, 1.85))), "look" if u < 1.5 else "wow", y=0.6 + bob(t, 2) + 0.06 * eio(pr(u, 1.5, 1.85)),
                  **DAMSEL, **swim(warp(t, t0 + 1.6, 2.0), 2))       # 掉头 0.35 s 平滑转身（原来一帧翻转）
    hx = lerp(0.4, 0.02, ease(pr(u, 1.0, 1.6))) + 0.3 * eio(pr(u, 2.4, 3.4))          # 冲到入侵者跟前停住（不顶进它身体）
    F = clownfish(hx, 0.3, 0.44, -1.1, "angry" if u > 0.8 else "look", y=0.55 + bob(t), helmet=1.0, **swim(warp(warp(t, t0 + 0.8, 2.0), warp(t0 + 2.4, t0 + 0.8, 2.0), 0.5), 0))
    c = push((0.0, 0.95, 3.5), (0.0, 0.32, -0.2), 0.05 * eio(pr(t, t0, T["fight"])))
    return c, V(0.0, 0.32, -0.2), F["face"], {"A": A, "F": F, "I": I}

def fight_pair(t, x0=0.0, z=0.3, s=0.42, y=0.55, helmet=1.0):
    b = abs(math.sin(t * 5.0))
    A_ = clownfish(x0 - 0.2 - 0.06 * b, z, s, 1.25, "angry", y=y + 0.04 * b, helmet=helmet, **swim(t, 0, 1.5))
    B_ = clownfish(x0 + 0.2 + 0.06 * b, z - 0.05, s * 0.85, -1.25, "angry", y=y + 0.04 * (1 - b), **swim(t, 1, 1.5))
    return A_, B_

def sh_fight(t):
    t0 = T["fight"]; Wd.reset(); Wd.reef(t, bubbles=6, kelp=False)
    A = anemone(0.0, -0.75, 1.0, 1.0, t, face=False, droop=0.25, seed=4)
    F, G = fight_pair(t, 0.0, 0.25, 0.4, 0.5)
    c = push((0.0, 0.95, 3.3), (0.0, 0.52, 0.0), 0.05 * eio(pr(t, t0, T["calm"])))
    return c, V(0.0, 0.52, 0.0), F["face"], {"A": A, "F": F, "G": G}

def sh_calm(t):
    t0 = T["calm"]; Wd.reset(); Wd.reef(t, bubbles=6)
    L_ = anemone(-0.55, -0.5, 0.6, 0.0, t, face=False, seed=1)
    R_ = anemone(0.55, -0.5, 0.6, 1.0, t, face=False, droop=0.25, seed=4)
    a1 = clownfish(-0.7, 0.0, 0.28, 0.6, "happy", y=0.62 + bob(t), **swim(t))
    a2 = clownfish(-0.4, 0.05, 0.24, -0.6, "happy", y=0.66 + bob(t, 1.4), **swim(t, 1.2))
    b1, b2 = fight_pair(t, 0.48, 0.0, 0.28, 0.6, helmet=0.0)
    c = push((0.0, 1.3, 4.5), (0.0, 0.2, -0.3), 0.05 * eio(pr(t, t0, T["know"])))
    return c, V(0.0, 0.2, -0.3), a1["face"], {"L": L_, "R": R_, "a1": a1, "a2": a2, "b1": b1, "b2": b2}

def algae(t, t0, n=14):
    """小藻类：黄绿小泥球从触手里飘出、上升、缩小消失（每颗自己的时间，≥0.5 s 渐变）"""
    for i in range(n):
        h = (math.sin(i * 12.99) * 437.5) % 1.0
        ts = t0 + 0.8 + i * 0.16
        u = pr(t, ts, ts + 2.4)
        if u <= 0 or u >= 1: continue
        r = 0.035 * math.sin(math.pi * u) ** 0.5
        a = i * 2.4
        x = math.cos(a) * (0.25 + 0.2 * h) + 0.08 * math.sin(t * 2 + i)
        z = -0.4 + math.sin(a) * 0.3
        y = 0.85 + u * 1.3
        g = cp.group((x, y, z), r * 1.3)
        cp.prim(0, 0, [x, y, z], [r, r, r], 0, 0.0, (150, 170, 60), 0.4, g)

def sh_know(t):
    t0 = T["know"]; Wd.reset(); Wd.reef(t, bubbles=4, kelp=False)
    kb = eio(pr(t, t0 + 1.0, t0 + 3.6))
    A = anemone(0.0, -0.4, 1.0, kb, t, face=True, expr="look" if kb < 0.5 else "worry", spread=0.5, seed=4)
    algae(t, t0)
    c = push((0.0, 0.9, 3.1), (0.0, 0.42, -0.4), 0.05 * eio(pr(t, t0, T["card"])))
    return c, V(0.0, 0.42, -0.4), A["face"], {"A": A}

def sh_card(t):
    t0 = T["card"]; Wd.reset(); Wd.reef(t, bubbles=8)
    A = anemone(-0.2, -0.6, 0.9, 1.0, t, face=True, expr="look", droop=0.2, seed=4)
    F = clownfish(0.4, 0.25, 0.4, -0.7, "look", y=0.62 + bob(t), helmet=1.0, gaze=(-0.7, 0.4), tail=math.sin(t * 9), flap=math.sin(t * 20))
    c = push((0.05, 0.95, 3.4), (0.05, 0.3, -0.3), 0.05 * eio(pr(t, t0, T["end"])))
    return c, V(0.05, 0.3, -0.3), F["face"], {"A": A, "F": F}

def sh_end(t):
    t0 = T["end"]; Wd.reset(); Wd.reef(t, bubbles=8)
    A = anemone(0.0, -0.75, 1.0, 1.0, t, face=True, expr="happy", droop=0.15, seed=4)
    u = t - t0
    F = clownfish(0.0, 0.35, 0.52, 0.2 * math.sin(u * 1.5), "happy" if u > 0.5 else "look", y=0.45 + bob(t) + hop(t, t0 + 2.6, 0.45, 0.1),
                  helmet=1.0, tail=math.sin(t * 7), flap=math.sin(warp(t, t0 + 2.5, 1.55) * 9) * (0.4 + 0.6 * eio(pr(u, 2.5, 2.8))))
    c = push((0.0, 0.75, 2.8), (0.0, 0.4, 0.0), 0.05 * eio(pr(t, t0, DUR)))
    return c, V(0.0, 0.4, 0.0), F["face"], {"A": A, "F": F}

# ================================================================== 渲染（脸部超采样 + 脸不进景深）
def faces_of(an):
    out = []
    for v in an.values():
        if isinstance(v, dict) and "face" in v: out.append((v["face"], v["face_r"]))
        elif isinstance(v, tuple):
            for w in v:
                if isinstance(w, dict) and "face" in w: out.append((w["face"], w["face_r"]))
    return out

def render3d(fn, tp, pose):
    cam, tgt, fpt, an = run_shot(fn.__name__[3:], fn, tp)
    PI, PF, GR, G0, G1 = Wd.arr()
    rng = np.random.default_rng(1000 + pose)                     # boil：每拍一个种子（定格，不逐帧）
    mov = (GR[PI[:, 2], 3] < 2.0)[:, None]
    PF[:, 0:3] += rng.normal(0, 0.0010, (len(PF), 3)) * mov
    camj = cam + rng.normal(0, 0.003, 3); tgtj = tgt + rng.normal(0, 0.0015, 3)
    img, dep, mask, info = cf.render_faces(RW, RH, OW, OH, camj, tgtj, FOV, LIGHT, PI, PF, GR, G0, G1, FLAGS, float(pose % 97),
                                           faces_of(an), ss=2.0)
    focus = float(np.linalg.norm(camj - np.asarray(fpt)))
    out = cf.post_faces(img * (1 + rng.normal(0, 0.01)), dep, focus, mask, fog=FOG)
    return out, (camj, tgtj), an, info

def project(p, ct):
    x, y, z = cf.project(p, ct[0], ct[1], FOV, OW, OH); return x, y

# ================================================================== 2D UI（无黑描边）
_FD = os.environ.get("CLAY_FONT_DIR") or os.path.join(HERE, "..", "flytrap")
FONTS = [os.path.join(_FD, "NotoSansSC-Bold.otf"), os.path.join(_FD, "NotoSansSC-Black.otf")]
_fc = {}
def F_(size, k=1):
    if (size, k) not in _fc: _fc[(size, k)] = ImageFont.truetype(FONTS[k], max(4, int(size)))
    return _fc[(size, k)]
def A(c, a): return tuple(c[:3]) + (int(255 * cl(a)),)
WHITE = (250, 250, 244); GOLD = (255, 200, 60); RED = (236, 84, 70); GREEN = (96, 186, 96); NAVY = (24, 30, 52); PINK = (255, 120, 150)
DARK = (10, 30, 52); ORG = (255, 140, 50); CYAN = (120, 220, 240)
class D:
    def __init__(s, img): s.img = img; s.d = ImageDraw.Draw(img, "RGBA")
    def rect(s, x0, y0, x1, y1, fill, r=0): s.d.rounded_rectangle((x0, y0, x1, y1), radius=min(r, (x1 - x0) / 2, (y1 - y0) / 2), fill=fill)
    def circ(s, x, y, r, fill): s.d.ellipse((x - r, y - r, x + r, y + r), fill=fill)
    def poly(s, pts, fill): s.d.polygon(pts, fill=fill)
    def line(s, pts, fill, w): s.d.line(pts, fill=fill, width=int(w), joint="curve")
    def tlen(s, t, size, k=1): return s.d.textlength(t, font=F_(size, k))
    def text(s, x, y, t, size, fill, anchor="mm", k=1):
        al = fill[3] if len(fill) > 3 else 255
        if al <= 2: return
        if al >= 253: s.d.text((x, y), t, font=F_(size, k), fill=fill[:3], anchor=anchor); return
        b = [int(v) for v in s.d.textbbox((x, y), t, font=F_(size, k), anchor=anchor)]; b[2] += 2; b[3] += 2
        m = Image.new("L", (b[2] - b[0], b[3] - b[1]), 0)
        ImageDraw.Draw(m).text((x - b[0], y - b[1]), t, font=F_(size, k), fill=al, anchor=anchor)
        s.img.paste(fill[:3], tuple(b), m)

def tag(d, x, y, s, col, a=1.0, size=44, tc=NAVY, k=1.0):
    if a <= 0.01 or k <= 0.01: return
    size = int(size * (0.6 + 0.4 * k)); w = d.tlen(s, size) + size * 1.0
    x = cl(x, 180 + w / 2, 900 - w / 2)                         # 安全区
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
    if t0 <= 0.0: a = 1.0; k = 0.75 + 0.25 * k
    if t1 is not None: a *= 1 - pr(t, t1 - 0.2, t1)
    sz = int(size * (0.55 + 0.45 * min(1.15, k)))
    w = min(d.tlen(s, sz) + 60, 760)
    d.rect(x - w / 2, y - sz * 0.72, x + w / 2, y + sz * 0.72, A(bgc, 0.5 * a), r=sz * 0.4)
    d.text(x, y, s, sz, A(col, a))
def ring(d, x, y, t, t0, col=GOLD, maxr=360):
    u = (t - t0) / 0.7
    if 0 <= u < 1:
        for j in range(3):
            r = 40 + (u + j * 0.1) * maxr
            d.d.ellipse((x - r, y - r, x + r, y + r), outline=A(col, (1 - u) * (1 - j * 0.3)), width=max(1, 9 - j * 3))
def arrow_up(d, x, y, h, col, a=1.0, w=26):
    if h > w * 1.2: d.rect(x - w / 2, y - h + w * 1.2, x + w / 2, y, A(col, a), r=w / 3)
    d.poly([(x - w * 1.4, y - h + w * 1.4), (x, y - h - w * 0.6), (x + w * 1.4, y - h + w * 1.4)], A(col, a))
def wavy(d, x0, x1, y, t, col, a, amp=10, w=7, ph=0.0):
    if a <= 0.01: return
    pts = [(x, y + amp * math.sin((x - x0) / 38 + t * 6 + ph)) for x in np.linspace(x0, x1, 40)]
    d.line(pts, A(col, a), w)
def mark(d, t, tt, x, y, s, col=GOLD, size=90):
    if t < tt: return
    kk = max(0.0, E.spring_at(t, tt, 0, 1, "bouncy")); bb = 8 * math.sin((t - tt) * 5)
    d.text(x, y + bb, s, int(size * min(1.1, kk)) + 1, A(col, cl((t - tt) / 0.15)))

def ui_hook(t, d, P, an):
    bigword(d, t, 0.0, 540, 400, "家变白了！", WHITE, 150, t1=BIG1)
    fx, fy = P(an["F"]["top"]); mark(d, t, 1.15, fx + 20, fy - 30, "!", GOLD, 110)
    px, py = P(an["P"]["top"]); mark(d, t, 1.45, px, py - 20, "!", GOLD, 80)
def ui_big1(t, d, P, an):
    t0 = BIG1
    for j in range(3):   # 热浪：顶部三条红橙波浪线，逐条淡入
        wavy(d, 230, 850, 330 + j * 52, t, (255, 120 + 30 * j, 70), 0.85 * cl((t - t0 - 0.2 - j * 0.2) / 0.3), 12, 8, j * 1.3)
    ax, ay = P(an["A"]["top"]); ring(d, ax, ay + 120, t, t0, WHITE, 380)
def ui_where(t, d, P, an):
    t0 = T["where"]; a = cl((t - t0 - 0.2) / 0.3)
    if a <= 0: return
    m = 3 + int(cl((t - t0 - 0.9) / 3.0) * 4.999)
    d.rect(330, 300, 750, 560, A(WHITE, 0.94 * a), r=40); d.rect(330, 300, 750, 380, A(RED, a), r=40); d.rect(330, 350, 750, 380, A(RED, a))
    d.text(540, 340, "2023", 52, A(WHITE, a))
    k = back(pr(t, t0 + 0.9 + (m - 3) * 0.75, t0 + 1.2 + (m - 3) * 0.75)) if m > 3 else 1.0
    d.text(540, 470, f"{m}月", int(120 * (0.7 + 0.3 * k)), A(NAVY, a))
    hy = 540 - 210 * ease(pr(t, t0 + 0.8, t0 + 4.2))        # 日历右侧小温度计上涨
    d.rect(795, 320, 835, 540, A(WHITE, 0.85 * a), r=20); d.rect(795, hy, 835, 540, A(RED, a), r=20); d.circ(815, 552, 32, A(RED, a))
def ui_cam(t, d, P, an):
    t0 = T["cam"]; a = cl((t - t0) / 0.3)
    if (t * 2) % 2 < 1.4: d.circ(240, 330, 16, A(RED, a))
    d.text(300, 330, "REC", 40, A(WHITE, a))
    n = int(round(23 * ease(pr(t, t0 + 0.3, t0 + 2.4))))
    d.rect(560, 290, 860, 380, A(DARK, 0.55 * a), r=40); d.text(710, 335, f"{n} 个家", 58, A(GOLD, a))
    for i in range(23):         # 23 个小鱼点一个一个冒出来（每个 0.3 s 弹入）
        tt = t0 + 0.3 + i * 0.09
        if t < tt: break
        k = min(1.0, back(pr(t, tt, tt + 0.3))); x = 250 + (i % 12) * 52; y = 440 + (i // 12) * 56
        d.circ(x, y, 17 * k, A(ORG, a)); d.rect(x - 4 * k, y - 16 * k, x + 4 * k, y + 16 * k, A(WHITE, a))
def ui_q(t, d, P, an):
    t0 = T["q"]; fx, fy = P(an["F"]["top"])
    mark(d, t, t0 + 0.5, fx - 120, fy - 10, "?", GOLD, 100); mark(d, t, t0 + 0.8, fx + 120, fy - 40, "?", GOLD, 80)
def ui_big2(t, d, P, an):
    t0 = BIG2; fx, fy = P(an["F"]["top"])
    ring(d, fx, fy + 120, t, t0, GOLD, 420)
    bigword(d, t, t0, 540, 380, "加班守家！", GOLD, 140)
def ui_care(t, d, P, an):
    t0 = T["care"]; fx, fy = P(an["F"]["face"]); px, py = P(an["P"]["face"])
    for j in range(3):          # 扇出的水流：弧形短线往海葵方向流
        u = ((t - t0) * 1.6 + j / 3) % 1.0
        x = fx - 120 - u * 160; aa = 0.8 * math.sin(math.pi * u) * cl((t - t0 - 0.3) / 0.3)
        wavy(d, x - 50, x + 50, fy - 30 + j * 40, t, CYAN, aa, 6, 6, j)
    ptag(d, t, t0 + 0.6, fx, fy - 170, "扇水", CYAN, 46)
    ptag(d, t, t0 + 1.3, px, py - 150, "打扫", WHITE, 46)
def ui_guard(t, d, P, an):
    t0 = T["guard"]; fx, fy = P(an["F"]["top"])
    mark(d, t, t0 + 0.85, fx + 30, fy - 20, "!", RED, 100)
    if t > t0 + 1.8:
        a = cl((t - t0 - 1.8) / 0.25)
        tag(d, 640, 380, "保卫", GOLD, a, 56)
        arrow_up(d, 760, 420, 90 * ease(pr(t, t0 + 1.9, t0 + 2.4)) + 1, GOLD, a, 22)
def ui_fight(t, d, P, an):
    t0 = T["fight"]
    ax, ay = P(an["F"]["top"]); bx, by = P(an["G"]["top"]); mx, my = (ax + bx) / 2, min(ay, by) - 30
    for j in range(5):          # 吵架火花
        u = ((t - t0) * 2.2 + j / 5) % 1.0; ang = j * 1.256 + 0.4
        r = 30 + 90 * u; d.circ(mx + math.cos(ang) * r, my + 60 + math.sin(ang) * r * 0.6, 14 * (1 - u), A(GOLD, (1 - u) * cl((t - t0) / 0.3)))
    if t > t0 + 1.0:
        n = int(round(215 * ease(pr(t, t0 + 1.0, t0 + 2.6))))
        bigword(d, t, t0 + 1.0, 540, 380, f"+{n}%", RED, 150)
def ui_calm(t, d, P, an):
    t0 = T["calm"]
    lx, ly = P(an["L"]["top"]); rx, ry = P(an["R"]["top"])
    ptag(d, t, t0 + 0.2, max(300, lx), 420, "没白化", GREEN, 50, WHITE)
    ptag(d, t, t0 + 0.6, min(780, rx), 420, "白化", WHITE, 50)
def ui_know(t, d, P, an):
    t0 = T["know"]; a = cl((t - t0 - 0.1) / 0.3) * (1 - pr(t, T["card"] - 0.25, T["card"])); dy = 30 * (1 - ease(pr(t, t0 + 0.1, t0 + 0.5)))
    if a <= 0: return
    d.rect(195, 270 + dy, 885, 640 + dy, A(WHITE, 0.94 * a), r=44)
    d.rect(380, 300 + dy, 700, 364 + dy, A(GOLD, a), r=32); d.text(540, 332 + dy, "一句话学会", 38, A(NAVY, a))
    d.text(540, 440 + dy, "白化：海葵身体里的", 58, A(NAVY, a))
    d.text(540, 540 + dy, "小藻类跑光了，就变白了", 52, A(RED, a))
def ui_card(t, d, P, an):
    t0 = T["card"]; ax, ay = P(an["A"]["top"])
    mark(d, t, t0 + 0.4, ax, ay - 10, "?", GOLD, 150)
    a = cl((t - t0 - 2.5) / 0.3)
    if a > 0:
        d.rect(300, 330, 780, 400, A(DARK, 0.55 * a), r=35)
        k = ((t - t0 - 2.5) * 0.4) % 1.0
        d.rect(310, 340, 310 + 460 * (0.15 + 0.85 * k), 390, A(CYAN, a), r=25)
        d.text(540, 365, "研究中…", 40, A(WHITE, a))
def ui_end(t, d, P, an):
    t0 = T["end"]
    ptag(d, t, t0 + 1.2, 540, 335, "评论区说说", GOLD, 56)
    if t > DUR - 0.6: d.rect(0, 0, OW, OH, A((0, 0, 0), pr(t, DUR - 0.6, DUR)))

HL = {"hook": "变白了", "big1": "白化", "where": "很热", "cam": "23个", "q": "偷懒", "big2": "加班守家",
      "care": "一点没少", "guard": "变多了", "fight": "215%", "calm": "没有变多", "card": "还在研究", "end": "好员工"}
NOSUB = ("know",)
def subs(t, d):
    for a, b, s, key in SUBS:
        if key in NOSUB: continue
        if a <= t < b:
            ee = E.enter_exit(t, max(a, 0), b, 0.3, 0.12, rise=18, s0=0.96)
            al = ee["alpha"] if a > 0 else (1 - pr(t, b - 0.12, b))
            if al <= 0.01: return
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70 + ee["dy"] * (a > 0)
            w = max(d.tlen(x, 54) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 70 + 46, A((8, 22, 40), 0.8 * al), r=22)
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
    s = "动物打工人 No.03"; w = d.tlen(s, 30) + 56
    d.rect(540 - w / 2, 150, 540 + w / 2, 204, A((10, 24, 40), 0.55), r=27); d.text(540, 177, s, 30, A(WHITE, 1))
    d.text(540, 234, "Vibe 知识大赏 · 小丑鱼加班守家", 24, A((250, 250, 240), 0.85), k=0)

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
LAST_INFO = []
def frame(fi):
    t = fi / FPS; pose = fi // 2; tp = pose * 2 / FPS
    idx = shot_at(t)
    if SECS[idx][0] > tp: tp = t
    img, ct, an, info = world(idx, tp, pose)
    LAST_INFO[:] = info
    a = SECS[idx][0]
    img = img.copy()
    soft = idx > 0 and a not in HARD and tp < a + XF
    if soft:
        pimg, _, _, _ = world(idx - 1, a - 2 / FPS, int(round((a - 2 / FPS) * FPS)) // 2)
        k = E.ease_in_out_sine(cl((t - a) / XF))
        img = (pimg.astype(np.float32) * (1 - k) + img.astype(np.float32) * k).astype(np.uint8)
    z = 1.0; sx = sy = 0.0
    for h in HARD:
        if h <= t < h + 0.6:
            u = t - h; z += 0.04 * math.exp(-u * 6); amp = 8 * math.exp(-u * 7)
            sx += amp * math.sin(u * 70); sy += amp * math.cos(u * 53)
    if z > 1.0005 or abs(sx) > 0.3:
        M = np.array([[z, 0, OW / 2 * (1 - z) + sx], [0, z, OH / 2 * (1 - z) + sy]], np.float32)
        img = cv2.warpAffine(img, M, (OW, OH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    pil = Image.fromarray(img); d = D(pil)
    P = lambda p: project(p, ct)
    if soft:
        _, pct, pan, _ = world(idx - 1, a - 2 / FPS, int(round((a - 2 / FPS) * FPS)) // 2)
        prev = pil.copy(); SECS[idx - 1][3](t, D(prev), lambda p: project(p, pct), pan)
        SECS[idx][3](t, d, P, an)
        pil = Image.blend(prev, pil, E.ease_in_out_sine(cl((t - a) / XF))); d = D(pil)
    else:
        SECS[idx][3](t, d, P, an)
    for h in HARD:
        if h <= t < h + 0.1: d.rect(0, 0, OW, OH, A(WHITE, 0.5 * (1 - (t - h) / 0.1)))
    brand(t, d); subs(t, d)
    return pil

def shot_times(name):
    idx = NAMES.index(name); a, b = max(0.0, SECS[idx][0]), min(SECS[idx][1], DUR)
    ts = set()
    for fi in range(int(round(a * FPS)), int(round(b * FPS))):
        t = fi / FPS; tp = (fi // 2) * 2 / FPS
        if SECS[idx][0] > tp: tp = t
        ts.add(round(tp, 4))
    if idx + 1 < len(NAMES) and SECS[idx + 1][0] not in HARD:       # 下一镜叠化时要用本镜的最后一拍
        ts.add(round(SECS[idx + 1][0] - 2 / FPS, 4))
    return sorted(ts)

DIRS = {"up": (0, 1, 0), "+x": (1, 0, 0), "-x": (-1, 0, 0), "+z": (0, 0, 1), "-z": (0, 0, -1),
        "up+x": (1, 1, 0), "up-x": (-1, 1, 0), "up+z": (0, 1, 1), "up-z": (0, 1, -1)}
def _scene_fish(name, t, apply):
    run_shot(name, SF[name], t, apply=apply)
    fish = list(_FISH); skip = [f[0] for f in fish if f] + [REEF_LAST.get("bubbles", (0, 0))]
    return fish, CL.obstacles(skip)

def clr_dirs(name, every=6):
    """第 1 步：每条鱼选一个固定的让位方向（整镜不变 → 轨迹连续）：各方向所需最大位移最小者；竖直向上优先（差 30% 以内取向上）"""
    ts = shot_times(name)[::every]; need = {}
    for t in ts:
        fish, obs = _scene_fish(name, t, False)
        for i, f in enumerate(fish):
            if f is None: continue
            P = CL.hull_points(f[0]); ob = CL.near(obs, P.mean(0), 1.8)
            if CL.clearance(P, ob) >= MARGIN + 0.02: continue
            for k, v in DIRS.items():
                need.setdefault(i, {}).setdefault(k, []).append(CL.need_lift(P, ob, MARGIN + 0.01, v))
    nf = max((len(_FISH),)); out = []
    for i in range(nf):
        if i not in need: out.append("up"); continue
        mx = {k: max(v) for k, v in need[i].items()}
        best = min(mx, key=mx.get)
        out.append("up" if mx["up"] <= mx[best] * 1.3 + 0.01 else best)
        print(f"  {name} 鱼{i}: " + " ".join(f"{k}={v:.2f}" for k, v in mx.items()) + f" → {out[-1]}", flush=True)
    return out

def clr_scan(name, dirs, apply=False):
    """第 2 步：逐拍算每条鱼沿自己方向需要的位移（apply=True 时为验证：间距与鱼-鱼间距）"""
    rows = []
    for t in shot_times(name):
        fish, obs = _scene_fish(name, t, apply)
        cl_, nd = [], []
        for i, f in enumerate(fish):
            if f is None: cl_.append(None); nd.append(0.0); continue
            P = CL.hull_points(f[0]); ob = CL.near(obs, P.mean(0), 1.8)
            cl_.append(round(CL.clearance(P, ob), 4))
            nd.append(0.0 if apply else round(CL.need_lift(P, ob, MARGIN, DIRS[dirs[i] if i < len(dirs) else "up"]), 4))
        pg = []
        for i in range(len(fish)):
            for j in range(i + 1, len(fish)):
                if fish[i] and fish[j]: pg.append((i, j, round(CL.pair_gap(fish[i][0], fish[j][0]), 4)))
        rows.append(dict(t=t, cl=cl_, need=nd, pair=pg))
    return rows

def clr_build(name, dirs, rows):
    ts = [r["t"] for r in rows]; nf = max(len(r["need"]) for r in rows)
    d = [CL.envelope(ts, [r["need"][i] if i < len(r["need"]) else 0.0 for r in rows]).round(4).tolist() for i in range(nf)]
    return dict(ts=ts, dir=[list(DIRS[dirs[i] if i < len(dirs) else "up"]) for i in range(nf)], dirn=dirs, d=d)

def clr_report(name, rows, tag):
    nf = max(len(r["cl"]) for r in rows)
    mins = [min((r["cl"][i] for r in rows if i < len(r["cl"]) and r["cl"][i] is not None), default=None) for i in range(nf)]
    needs = [max((r["need"][i] for r in rows if i < len(r["need"])), default=0) for i in range(nf)]
    pmin = {}
    for r in rows:
        for i, j, g in r["pair"]: pmin[f"{i}-{j}"] = min(pmin.get(f"{i}-{j}", 9), g)
    print(name, tag, f"{len(rows)} 拍  最小间距/鱼:", mins, " 位移:", needs, " 鱼-鱼:", pmin, flush=True)
    return mins, pmin

if __name__ == "__main__" and sys.argv[1] in ("clr", "clrv"):
    # python3 film.py clr <镜号...>  → 选方向 + 逐拍需求 + 包络，写入 clear_track.json；python3 film.py clrv <镜号...> → 套用后复查
    os.makedirs(os.path.join(HERE, "clear_raw"), exist_ok=True)
    for name in sys.argv[2:]:
        t0 = time.time()
        if sys.argv[1] == "clr":
            CLR.pop(name, None)
            dirs = clr_dirs(name); rows = clr_scan(name, dirs)
            tr = clr_build(name, dirs, rows); clr_report(name, rows, "原始")
            allc = json.load(open(CLR_PATH)) if os.path.exists(CLR_PATH) else {}
            allc[name] = tr; json.dump(allc, open(CLR_PATH, "w"))
        else:
            rows = clr_scan(name, CLR.get(name, {}).get("dirn", []), apply=True)
            m, p = clr_report(name, rows, "复查")
            bad = [x for x in m if x is not None and x < MARGIN - 0.004]
            print("  ", "通过" if not bad else f"未通过 {bad}", f"{time.time() - t0:.0f}s", flush=True)
        json.dump(rows, open(os.path.join(HERE, "clear_raw", f"{name}_{sys.argv[1]}.json"), "w"))
    sys.exit(0)

if __name__ == "__main__":
    if sys.argv[1] in ("test", "faces"):
        for ts in sys.argv[2:]:
            t0 = time.time(); fi = int(round(float(ts) * FPS)); fi -= fi % 2
            im = frame(fi); im.save(os.path.join(HERE, "tests", f"test_{float(ts):05.2f}.png"))
            if sys.argv[1] == "faces":   # 脸部裁出放大 2×（无插值放大，看真实像素）
                arr_ = np.asarray(im)
                for j, b in enumerate(LAST_INFO):
                    Image.fromarray(cf.face_crop(arr_, b, 2)).save(os.path.join(HERE, "tests", f"face_{float(ts):05.2f}_{j}.png"))
            print(ts, round(time.time() - t0, 1), LAST_INFO, flush=True)
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                              "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", out], stdin=subprocess.PIPE)
        t0 = time.time()
        for i in range(i0, i1):
            p.stdin.write(np.asarray(frame(i)).tobytes())
            if i % 10 == 0: print("frame", i, round(time.time() - t0, 1), flush=True)
        p.stdin.close(); p.wait(); print("done", i0, i1, round(time.time() - t0, 1), flush=True)
