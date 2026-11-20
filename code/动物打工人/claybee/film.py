# 《动物打工人 No.04》被说只会吃白饭的雄熊蜂，半夜给宝宝保温？— G 系列真 3D 黏土（蜂巢办公室），on twos + boil
# 面部永不糊：engine/clay_face.py —— 脸部区域 2× 超采样贴回，景深 CoC/柔光在脸部蒙版内强制为 0，对焦点=主角脸
# 热成像镜头：在 2D 后期里按“亮度 + 热源高斯”算温度场，套红白色热成像色表（白=最热）；夜景整体冷蓝调色
# 用法: python3 film.py test 0.5 3.2 ... | python3 film.py faces 0.5 3.2 ...（脸部放大 2× 自检） | python3 film.py render i0 i1 out.mp4
import sys, math, subprocess, time, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world as Wd
from world import cp, cf, bumblebee, brood
import easing as E
from cues import *

HERE = os.path.dirname(os.path.abspath(__file__))
OW, OH, FPS = 1080, 1920, 30
RW, RH = 600, 1066
FOV = math.radians(44)
LIGHT = np.array([-0.5, 0.8, 0.5]); LIGHT /= np.linalg.norm(LIGHT)
FLAGS = np.array([1, 1, 1, 1, 1, 1, 1], np.int64)

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
def bob(t, ph=0.0, a=0.02): return a * math.sin(t * 2.6 + ph)
def flapw(t): return math.sin(t * 47.0)          # 飞行翅膀：on twos 下也是交替的快拍
def breathe(t, ph=0.0): return 0.012 * math.sin(t * 2.4 + ph)

# ================================================================== 镜头（返回 cam, tgt, 对焦点, anchors；anchors['_st'] = 调色/热成像）
def sh_hook(t):
    Wd.reset(); Wd.hive(t, extra=("board",))
    Wd.honey_pot(0.32, 0.62, 0.95)
    chew = abs(math.sin(t * 7.0))
    dip = max(0.0, math.sin(t * 3.6))
    M = bumblebee(-0.2, 0.35, 0.82, 0.18, "happy" if (t % 1.4) < 0.7 else "look", y=hop(t, 0.0, 0.4, 0.06) + breathe(t),
                  arms=(-0.1, 0.25 + 0.6 * dip), mouth_open=0.5 * chew, squash=-0.05 * math.exp(-t * 8))
    k = eio(pr(t, 1.2, 1.7))
    W1 = bumblebee(0.5, -0.85, 0.68, -0.35, "angry" if t > 1.4 else "look", role="worker", arms=(0.0, 0.7 * k), gaze=(-0.8, -0.1))
    W2 = bumblebee(0.95, -1.05, 0.68, -0.5, "worry", role="worker", arms=(0.4 * k, 0.0), gaze=(-0.8, 0.0))
    c = push((0.1, 1.15, 3.85), (0.18, 0.58, -0.2), 0.05 * eio(pr(t, 0, T["myth"])))
    return c, V(0.18, 0.58, -0.2), M["face"], {"M": M, "W1": W1, "W2": W2, "_st": {}}

def sh_myth(t):
    t0 = T["myth"]; u = t - t0; Wd.reset(); Wd.hive(t, extra=("door",))
    k = eio(pr(u, 0.4, 4.6))
    M = bumblebee(lerp(0.05, -0.75, k), lerp(0.3, -1.55, k), 0.68, lerp(0.1, 0.5, k), "happy", y=lerp(0.0, 0.85, k) + 0.05 * math.sin(u * 5),
                  wing=flapw(t) if u > 0.25 else 0.0, arms=(0.5, 0.5), pitch=-0.1)
    c = push((-0.25, 1.35, 4.1), (-0.45, 1.0, -0.8), 0.05 * eio(pr(t, t0, T["night"])))
    return c, V(-0.45, 1.0, -0.8), M["face"], {"M": M, "_st": {}}

BROOD_N = (0.3, -0.35)
def sh_night(t):
    t0 = T["night"]; u = t - t0; Wd.reset(); Wd.hive(t, extra=("moon",))
    B = brood(BROOD_N[0], BROOD_N[1], 1.0, t)
    k = eio(pr(u, 0.0, 2.6))
    step = abs(math.sin(u * 6.0)) * (1 - pr(u, 2.4, 2.7))
    M = bumblebee(lerp(-1.2, -0.42, k), 0.15, 0.66, 0.35, "look", y=0.035 * step, gaze=(0.9, -0.2), arms=(0.35, 0.35),
                  squash=0.03 * step)
    c = push((0.05, 1.25, 3.7), (0.05, 0.58, -0.3), 0.05 * eio(pr(t, t0, T["q"])))
    return c, V(0.05, 0.58, -0.3), M["face"], {"M": M, "B": B, "_st": {"night": 1.0}}

def sh_q(t):
    t0 = T["q"]; u = t - t0; Wd.reset(); Wd.hive(t, extra=("moon",))
    B = brood(0.5, -0.35, 1.0, t)
    gx = 0.9 if u < 0.9 else lerp(0.9, 0.0, eio(pr(u, 0.9, 1.2)))
    M = bumblebee(-0.12, 0.3, 0.8, 0.3, "look" if u < 1.0 else "wow", gaze=(gx, -0.2 if u < 0.9 else 0.0), arms=(0.3, 0.3), y=breathe(t))
    c = push((0.1, 1.15, 3.25), (0.12, 0.72, -0.1), 0.05 * eio(pr(t, t0, BIG2)))
    return c, V(0.05, 0.8, 0.0), M["face"], {"M": M, "B": B, "_st": {"night": 1.0}}

def incub(t, x=0.0, z=0.0, s=0.72, bs=1.15, expr="happy", shiver=0.0, yaw=0.0):
    """雄蜂趴在育雏团上孵卵（腹部贴住宝宝），返回 (bee, brood)"""
    B = brood(x, z - 0.05, bs, t)
    jx = shiver * 0.006 * math.sin(t * 61.0)
    M = bumblebee(x + jx, z + 0.05, s, yaw, expr, lie=1.0, y=0.3 * bs + 0.02 + breathe(t) * 0.5, arms=(-0.3, -0.3))
    return M, B

def hot_of(M, B, kb=1.0, kl=0.55):
    """热源：雄蜂胸部（最热）、腹部、被捂热的幼虫"""
    th = [M["thorax"][i] + (M["abdomen"][i] - M["thorax"][i]) * 0.6 for i in range(3)]
    h = [(th, 0.24 * M["s"], 1.0 * kb), (M["abdomen"], 0.3 * M["s"], 0.55 * kb), (M["head"], 0.3 * M["s"], 0.42 * kb, True)]
    for p, r in B["larvae"]: h.append((p, r * 1.4, kl))
    h.append((B["center"], 0.45, 0.2))
    return h

def sh_big2(t):
    t0 = BIG2; u = t - t0; Wd.reset(); Wd.hive(t, extra=("moon",))
    M, B = incub(t, 0.0, 0.0, 0.72, 1.15, "proud" if u < 1.6 else "sleepy", shiver=1.0, yaw=0.6)
    c = push((0.75, 1.3, 3.25), (-0.08, 0.6, -0.05), 0.05 * eio(pr(t, t0, T["know"])))
    return c, V(-0.08, 0.6, -0.05), M["face"], {"M": M, "B": B, "_st": {"night": 1.0, "thermal": 1.0, "hot": hot_of(M, B)}}

def sh_know(t):
    t0 = T["know"]; u = t - t0; Wd.reset(); Wd.hive(t, extra=("moon",))
    M, B = incub(t, 0.35, -0.2, 0.68, 1.1, "sleepy", shiver=1.0, yaw=0.55)
    C = Wd.thermo_cam(-0.62, 0.75, 0.8, yaw=0.75, rec=0.5 + 0.5 * math.sin(t * 6))
    wipe = 1 - eio(pr(u, 0.5, 2.3))                     # 热成像扫描线：从右往左扫过去（屏幕 x 比例）
    c = push((-0.05, 1.45, 3.7), (0.05, 0.62, -0.15), 0.05 * eio(pr(t, t0, T["temp"])))
    return c, V(0.05, 0.62, -0.15), M["face"], {"M": M, "B": B, "C": C, "_st": {"night": 1.0, "thermal": 1.0, "wipe": wipe, "hot": hot_of(M, B)}}

def sh_temp(t):
    t0 = T["temp"]; u = t - t0; Wd.reset(); Wd.hive(t, extra=("moon",))
    M, B = incub(t, 0.0, 0.0, 0.72, 1.15, "happy", shiver=1.0)
    lv = 0.3 + 0.5 * ease(pr(u, 0.6, 3.2))
    th = M["thorax"]
    Wd.thermometer(th[0] + 0.5, 0.25, th[2] + 0.25, 0.8, lv, tilt=-0.12 + 0.03 * math.sin(t * 3))
    c = push((0.3, 1.2, 2.75), (0.12, 0.6, 0.0), 0.05 * eio(pr(t, t0, T["muscle"])))
    return c, V(0.12, 0.6, 0.0), M["face"], {"M": M, "B": B, "lv": lv, "_st": {"night": 0.6}}

def sh_muscle(t):
    t0 = T["muscle"]; Wd.reset(); Wd.hive(t, extra=("moon",))
    M, B = incub(t, 0.0, 0.0, 0.72, 1.15, "proud", shiver=1.6, yaw=0.35)
    c = push((1.0, 1.35, 3.0), (0.05, 0.78, -0.05), 0.05 * eio(pr(t, t0, T["exp"])))
    return c, V(0.05, 0.78, -0.05), M["face"], {"M": M, "B": B, "_st": {"night": 0.6}}

LAB_BG = (206, 226, 232); LAB_FL = (176, 186, 196)
BOXES = [(-0.47, 0.95, -0.35, 0), (0.47, 0.95, -0.35, 1), (-0.47, 0.0, 0.0, 3), (0.47, 0.0, 0.0, 5)]
def box_bees(t, bx, by, bz, n, t_in, s=0.27, eggs=None):
    an = {}
    Q = bumblebee(bx - 0.17, bz - 0.05, s, 0.2, "look", role="queen", y=by + 0.06, lod=True)
    an["Q"] = Q
    spots = [(0.12, 0.12), (0.26, -0.12), (0.05, -0.17), (0.3, 0.12), (0.17, 0.0)]
    for i in range(n):
        k = grow(t, t_in + i * 0.12, 0.4)
        if k <= 0.02: continue
        dx, dz = spots[i]
        an["m%d" % i] = bumblebee(bx + dx, bz + dz, s * 0.82 * k, -0.2, "look", y=by + 0.06, lod=True)
    return an

def sh_exp(t):
    t0 = T["exp"]; Wd.reset()
    Wd.backdrop(LAB_BG); Wd.floor(LAB_FL)
    g = Wd.cp.group((0, 0.9, -0.35), 1.3)
    Wd.cp.prim(2, 0, [0, 0.9, -0.35], [1.05, 0.04, 0.42], 0.02, 0.0, (236, 236, 228), 0.2, g)      # 搁板
    an = {}
    for j, (bx, by, bz, n) in enumerate(BOXES):
        Wd.lab_box(bx, bz, 0.84, 0.62, 0.6, y=by)
        an.update({f"{j}{k}": v for k, v in box_bees(t, bx, by, bz, n, t0 + 0.6 + j * 0.45).items()})
    c = push((0.0, 1.05, 4.9), (0.0, 0.36, -0.1), 0.05 * eio(pr(t, t0, T["start"])))
    return c, V(0.0, 0.36, -0.1), an["0Q"]["face"], {**an, "_st": {}}

from film_times import DAY_R, DAY_L     # 右（5 只雄蜂）第 6 天开工、左（只有蜂后）第 15 天开工（镜头内秒数）
def sh_start(t):
    t0 = T["start"]; u = t - t0; Wd.reset()
    Wd.backdrop(LAB_BG); Wd.floor(LAB_FL)
    an = {}
    for side, bx, n, tday in ((0, -0.5, 0, DAY_L), (1, 0.5, 5, DAY_R)):
        Wd.lab_box(bx, 0.0, 0.88, 0.62, 0.62)
        bb = box_bees(t, bx, 0.0, 0.0, n, -9, s=0.3)
        an.update({f"{side}{k}": v for k, v in bb.items()})
        ke = grow(t, t0 + tday, 0.4)
        if ke > 0.02:
            an[f"E{side}"] = brood(bx - 0.17, 0.2, 0.36 * min(ke, 1.1), t, n_larva=0, n_egg=6, y=0.06)
    c = push((0.0, 1.15, 4.6), (0.0, 0.22, 0.0), 0.05 * eio(pr(t, t0, T["brood"])))
    return c, V(0.0, 0.22, 0.0), an["1Q"]["face"], {**an, "_st": {}}

def sh_brood(t):
    t0 = T["brood"]; Wd.reset(); Wd.hive(t)
    bl = [t0 + 0.3 + i * 0.22 for i in range(6)]
    br = [t0 + 0.3 + i * 0.17 for i in range(10)]
    L_ = brood(-0.52, 0.0, 0.78, t, n_larva=6, n_egg=4, born=bl, seed=1)
    R_ = brood(0.52, 0.0, 0.95, t, n_larva=10, n_egg=6, born=br, seed=2)
    Mq = bumblebee(0.0, -1.0, 0.5, 0.0, "happy", role="queen")
    c = push((0.0, 1.75, 3.7), (0.0, 0.22, -0.25), 0.05 * eio(pr(t, t0, T["lab"])))
    return c, V(0.0, 0.22, -0.25), (R_["top"] if True else None), {"L": L_, "R": R_, "Q": Mq, "_st": {}}

def sh_lab(t):
    t0 = T["lab"]; u = t - t0; Wd.reset()
    Wd.backdrop(LAB_BG); Wd.floor(LAB_FL)
    lid = eio(pr(u, 0.3, 0.9))
    Bx = Wd.lab_box(0.0, 0.0, 1.5, 1.05, 0.95, lid=lid, lock=u > 0.6)
    B = brood(0.35, -0.15, 0.6, t, n_larva=4, n_egg=4)
    Q = bumblebee(0.42, -0.3, 0.42, -0.2, "look", role="queen", y=0.06)
    push_ = 0.5 + 0.5 * math.sin(u * 4.0)
    M = bumblebee(-0.3, 0.12, 0.55, 0.1, "worry", y=0.06, arms=(0.75 + 0.1 * push_, 0.75 + 0.1 * push_), gaze=(0.0, 0.3))
    c = push((0.0, 1.0, 3.1), (0.0, 0.55, 0.0), 0.05 * eio(pr(t, t0, T["wild"])))
    return c, V(0.0, 0.55, 0.0), M["face"], {"M": M, "Q": Q, "B": B, "X": Bx, "_st": {}}

FLOWERS = [(-0.95, -0.6, 1.0, (255, 140, 170)), (0.95, -0.9, 1.1, (180, 150, 255)), (-0.6, 0.6, 0.8, (255, 220, 90)),
           (0.75, 0.45, 0.85, (255, 150, 120)), (-1.4, -1.3, 1.2, (255, 255, 255)), (1.4, -1.5, 1.2, (255, 170, 210))]
def sh_wild(t):
    t0 = T["wild"]; u = t - t0; Wd.reset()
    Wd.meadow(t, hole=(0.15, -0.35))
    for i, (fx, fz, fs, col) in enumerate(FLOWERS): Wd.flower(fx, fz, fs, col, t, i)
    a = u * 1.3
    M = bumblebee(0.15 + 0.55 * math.sin(a), -0.35 + 0.35 * math.cos(a) + 0.2, 0.55, 0.35 * math.cos(a), "look",
                  y=0.75 + 0.08 * math.sin(u * 3.0), wing=flapw(t), arms=(0.4, 0.4), gaze=(-math.cos(a) * 0.5, -0.4))
    c = push((0.0, 1.7, 3.9), (0.05, 0.5, -0.3), 0.05 * eio(pr(t, t0, T["end"])))
    return c, V(0.05, 0.5, -0.3), M["face"], {"M": M, "_st": {}}

def sh_end(t):
    t0 = T["end"]; u = t - t0; Wd.reset(); Wd.hive(t, extra=("board",))
    up = eio(pr(u, 0.7, 1.0))
    M = bumblebee(0.0, 0.3, 0.85, 0.0, "proud" if u > 0.7 else "wow", y=hop(t, t0 + 0.75, 0.45, 0.1) + breathe(t), arms=(0.75 * up, 0.75 * up))
    Q = bumblebee(0.72, -0.55, 0.62, -0.4, "happy", role="queen")
    cl_ = abs(math.sin(u * 7.0)) * pr(u, 0.9, 1.1)
    W1 = bumblebee(-0.75, -0.6, 0.66, 0.4, "happy", role="worker", arms=(0.55 + 0.2 * cl_, 0.55 + 0.2 * cl_))
    c = push((0.0, 1.2, 3.6), (0.0, 0.8, -0.1), 0.05 * eio(pr(t, t0, T["ask"])))
    return c, V(0.0, 0.8, -0.1), M["face"], {"M": M, "Q": Q, "W1": W1, "_st": {}}

def sh_ask(t):
    t0 = T["ask"]; u = t - t0; Wd.reset(); Wd.hive(t, extra=("board",))
    wv = math.sin(u * 6.0)
    M = bumblebee(0.0, 0.3, 0.9, -0.1, "happy" if u > 0.4 else "look", y=breathe(t), arms=(-0.1, 0.7 + 0.2 * wv), gaze=(0, 0))
    Wd.honey_pot(-0.55, 0.55, 0.9)
    c = push((0.0, 1.3, 3.15), (0.0, 0.72, 0.0), 0.05 * eio(pr(t, t0, DUR)))
    return c, V(0.0, 0.72, 0.0), M["face"], {"M": M, "_st": {}}

# ================================================================== 渲染（脸部超采样 + 脸不进景深）+ 调色 / 热成像
def faces_of(an, fpt=None):
    """脸部超采样：主角（对焦脸）+ _st['faces'] 里点名的角色；远处/景深外的配角不超采样（省时，且不是要看清的脸）"""
    out = []; keep = set(an.get("_st", {}).get("faces", ()))
    for k, v in an.items():
        if k.startswith("_"): continue
        if isinstance(v, dict) and "face" in v and "face_r" in v:
            if k == "M" or k in keep or (fpt is not None and np.allclose(v["face"], fpt)): out.append((v["face"], v["face_r"]))
    return out

def project(p, ct):
    x, y, z = cf.project(p, ct[0], ct[1], FOV, OW, OH); return x, y

def _lut():
    stops = [(0.0, (16, 6, 40)), (0.25, (70, 16, 120)), (0.45, (190, 30, 70)), (0.62, (240, 80, 30)), (0.78, (255, 170, 30)),
             (0.9, (255, 240, 120)), (1.0, (255, 255, 255))]
    xs = np.linspace(0, 1, 256); out = np.zeros((256, 3), np.float32)
    for c in range(3): out[:, c] = np.interp(xs, [s[0] for s in stops], [s[1][c] for s in stops])
    return out
LUT = _lut()
def thermal(img, ct, hot, fmask=None):
    lum = img.astype(np.float32).mean(2) / 255.0
    temp = 0.06 + 0.46 * lum
    H, W = lum.shape
    bl = np.zeros_like(temp); fm = np.zeros_like(temp) if fmask is None else fmask.astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for item in hot:
        p, r, I = item[:3]; onface = len(item) > 3 and item[3]
        x, y, z = cf.project(p, ct[0], ct[1], FOV, OW, OH)
        if z <= 0.1: continue
        rp = r / z / math.tan(FOV / 2) * OH / 2
        x0, x1 = int(max(0, x - rp * 3)), int(min(W, x + rp * 3)); y0, y1 = int(max(0, y - rp * 3)), int(min(H, y + rp * 3))
        if x1 <= x0 or y1 <= y0: continue
        d2 = ((xx[y0:y1, x0:x1] - x) ** 2 + (yy[y0:y1, x0:x1] - y) ** 2) / (rp * rp)
        blob = I * 0.6 * np.exp(-d2 * 1.6)
        if onface: temp[y0:y1, x0:x1] += blob
        else: bl[y0:y1, x0:x1] += blob
    temp = np.clip(temp + bl * (1 - 0.9 * fm), 0, 1)        # 身体热斑不盖住脸（脸只按头部温度 + 亮度细节显示，五官可读）
    return LUT[(temp * 255).astype(np.int32)]

def grade(img, st, ct, fmask=None):
    out = img.astype(np.float32)
    nk = st.get("night", 0.0)
    if nk > 0:
        out = out * (1 - nk) + (out * np.array([0.44, 0.52, 0.86], np.float32) + np.array([6, 10, 30], np.float32)) * nk
    tk = st.get("thermal", 0.0)
    if tk > 0:
        th = thermal(np.clip(out, 0, 255), ct, st.get("hot", []), fmask)
        m = np.full((OH, OW), tk, np.float32)
        if "wipe" in st:
            xw = st["wipe"] * OW
            m = (np.clip((np.arange(OW, dtype=np.float32) - xw) / 6.0, 0, 1)[None, :] * np.ones((OH, 1), np.float32)) * tk
        out = out * (1 - m[..., None]) + th * m[..., None]
    return np.clip(out, 0, 255).astype(np.uint8)

def render3d(fn, tp, pose):
    cam, tgt, fpt, an = fn(tp)
    PI, PF, GR, G0, G1 = Wd.arr()
    rng = np.random.default_rng(1000 + pose)                     # boil：每拍一个种子（定格，不逐帧）
    mov = (GR[PI[:, 2], 3] < 2.0)[:, None]
    PF[:, 0:3] += rng.normal(0, 0.0008, (len(PF), 3)) * mov
    camj = cam + rng.normal(0, 0.0025, 3); tgtj = tgt + rng.normal(0, 0.0012, 3)
    img, dep, mask, info = cf.render_faces(RW, RH, OW, OH, camj, tgtj, FOV, LIGHT, PI, PF, GR, G0, G1, FLAGS, float(pose % 97),
                                           faces_of(an, fpt), ss=2.0)
    focus = float(np.linalg.norm(camj - np.asarray(fpt)))
    out = cf.post_faces(img * (1 + rng.normal(0, 0.01)), dep, focus, mask)
    out = grade(out, an.get("_st", {}), (camj, tgtj), mask)
    return out, (camj, tgtj), an, info

# ================================================================== 2D UI（无黑描边）
_FD = os.environ.get("CLAY_FONT_DIR") or os.path.join(HERE, "..", "flytrap")
FONTS = [os.path.join(_FD, "NotoSansSC-Bold.otf"), os.path.join(_FD, "NotoSansSC-Black.otf")]
_fc = {}
def F_(size, k=1):
    if (size, k) not in _fc: _fc[(size, k)] = ImageFont.truetype(FONTS[k], max(4, int(size)))
    return _fc[(size, k)]
def A(c, a): return tuple(c[:3]) + (int(255 * cl(a)),)
WHITE = (250, 250, 244); GOLD = (255, 200, 60); RED = (236, 84, 70); GREEN = (96, 186, 96); NAVY = (24, 30, 52); PINK = (255, 120, 150)
DARK = (34, 22, 14); ORG = (255, 140, 50); CYAN = (120, 220, 240); HONEY = (250, 176, 40)
class D:
    def __init__(s, img): s.img = img; s.d = ImageDraw.Draw(img, "RGBA")
    def rect(s, x0, y0, x1, y1, fill, r=0): s.d.rounded_rectangle((x0, y0, x1, y1), radius=max(0, min(r, (x1 - x0) / 2, (y1 - y0) / 2)), fill=fill)
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
    x = cl(x, 180 + w / 2, 900 - w / 2)
    d.rect(x - w / 2, y - size * 0.8, x + w / 2, y + size * 0.8, A(col, 0.95 * a), r=size * 0.8)
    d.text(x, y, s, size, A(tc, a))
def ptag(d, t, t0, x, y, s, col, size=44, tc=NAVY, t1=None):
    if t < t0: return
    k = max(0.0, E.spring_at(t, t0, 0, 1, "snappy")); a = cl((t - t0) / 0.3)
    if t1 is not None: a *= 1 - pr(t, t1 - 0.3, t1)
    tag(d, x, y + (1 - min(k, 1)) * 24, s, col, a, size, tc, min(1.1, k))
def bigword(d, t, t0, x, y, s, col, size=120, t1=None, bgc=DARK):
    if t < t0: return
    k = max(0.0, E.spring_at(t, t0, 0, 1, "bouncy")); a = cl((t - t0) / 0.12)
    if t0 <= 0.0: a = 1.0; k = 0.8 + 0.2 * k
    if t1 is not None: a *= 1 - pr(t, t1 - 0.3, t1)
    sz = int(size * (0.55 + 0.45 * min(1.15, k)))
    w = min(d.tlen(s, sz) + 60, 720)
    d.rect(x - w / 2, y - sz * 0.72, x + w / 2, y + sz * 0.72, A(bgc, 0.55 * a), r=sz * 0.4)
    d.text(x, y, s, sz, A(col, a))
def ring(d, x, y, t, t0, col=GOLD, maxr=360):
    u = (t - t0) / 0.7
    if 0 <= u < 1:
        for j in range(3):
            r = 40 + (u + j * 0.1) * maxr
            d.d.ellipse((x - r, y - r, x + r, y + r), outline=A(col, (1 - u) * (1 - j * 0.3)), width=max(1, 9 - j * 3))
def mark(d, t, tt, x, y, s, col=GOLD, size=90, t1=None):
    if t < tt: return
    kk = max(0.0, E.spring_at(t, tt, 0, 1, "bouncy")); bb = 8 * math.sin((t - tt) * 5)
    a = cl((t - tt) / 0.3)
    if t1 is not None: a *= 1 - pr(t, t1 - 0.3, t1)
    d.text(x, y + bb, s, int(size * min(1.1, kk)) + 1, A(col, a))
def heart(d, x, y, r, col, a):
    if a <= 0.01: return
    d.circ(x - r * 0.5, y - r * 0.2, r * 0.55, A(col, a)); d.circ(x + r * 0.5, y - r * 0.2, r * 0.55, A(col, a))
    d.poly([(x - r * 1.02, y - r * 0.05), (x + r * 1.02, y - r * 0.05), (x, y + r * 1.0)], A(col, a))
def wavy(d, x0, x1, y, t, col, a, amp=10, w=7, ph=0.0):
    if a <= 0.01: return
    pts = [(x, y + amp * math.sin((x - x0) / 38 + t * 6 + ph)) for x in np.linspace(x0, x1, 40)]
    d.line(pts, A(col, a), w)
def heatwaves(d, x, y, t, a, n=3, h=120, col=(255, 150, 60)):
    for j in range(n):
        u = ((t * 0.9) + j / n) % 1.0
        xx = x + (j - (n - 1) / 2) * 46
        pts = [(xx + 10 * math.sin(v * 9 + t * 5 + j), y - u * h - v * 60) for v in np.linspace(0, 1, 12)]
        d.line(pts, A(col, a * math.sin(math.pi * u)), 7)
def badge2d(d, x, y, s, text, a=1.0, flip=1.0, w0=None):
    """放大的 2D 工牌（挂在 3D 工牌的投影位置上）：白卡 + 红色顶条 + 名字；flip 0..1 = 横向翻转缩放"""
    if a <= 0.01: return
    w = (w0 or (d.tlen(text, 40 * s) + 50 * s)) * max(0.04, abs(flip)); h = 92 * s
    x = cl(x, 180 + w / 2, 900 - w / 2)
    d.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, A(WHITE, a), r=12 * s)
    d.rect(x - w / 2, y - h / 2, x + w / 2, y - h / 2 + 20 * s, A(RED, a), r=8 * s)
    if abs(flip) > 0.35: d.text(x, y + 10 * s, text, int(40 * s * min(1, abs(flip) * 1.2)), A(NAVY, a))
    return x

def ui_hook(t, d, P, an):
    bigword(d, t, 0.0, 540, 420, "干饭王", GOLD, 170, t1=2.6)
    M = an["M"]
    if M["badge"] is not None:
        bx, by = P(M["badge"]); k = cl(back(pr(t, 0.6, 1.0)))
        if t > 0.6:
            aa = cl((t - 0.6) / 0.3); px_, py_ = bx + 210, by - 170
            d.line([(bx, by), (bx + 150, by), (px_, py_ + 46)], A(WHITE, 0.85 * aa), 5)
            badge2d(d, px_, py_, 1.3 * max(0.05, k), "实习生", aa)
    for j in range(3):          # 蜂蜜滴：从勺/手往嘴里飞（连续轨迹）
        u = ((t * 1.1) + j / 3) % 1.0
        hx, hy = P(M["hand_r"]); fx, fy = P(M["face"])
        x = lerp(hx, fx, u); y = lerp(hy, fy + 30, u) - 60 * math.sin(math.pi * u)
        d.circ(x, y, 13 * math.sin(math.pi * u) + 1, A(HONEY, 0.9 * math.sin(math.pi * u)))
    wx, wy = P(an["W1"]["top"])
    mark(d, t, 1.5, wx - 30, wy - 30, "!", RED, 90)
def ui_myth(t, d, P, an):
    t0 = T["myth"]; a = cl((t - t0 - 0.2) / 0.3)
    if a > 0:
        dy = 30 * (1 - ease(pr(t, t0 + 0.2, t0 + 0.6)))
        d.rect(250, 280 + dy, 830, 620 + dy, A((252, 244, 222), 0.95 * a), r=30)
        d.rect(250, 280 + dy, 830, 350 + dy, A((150, 110, 70), a), r=30); d.rect(250, 320 + dy, 830, 350 + dy, A((150, 110, 70), a))
        d.text(540, 316 + dy, "老课本", 40, A(WHITE, a))
        d.text(540, 410 + dy, "雄蜂的工作：", 46, A(NAVY, a))
        a1 = cl((t - t0 - 1.0) / 0.3); a2 = cl((t - t0 - 2.0) / 0.3)
        d.text(540, 480 + dy, "① 找对象", 50, A(RED, a * a1))
        d.text(540, 555 + dy, "② ……没了", 46, A((120, 110, 100), a * a2))
    fx, fy = P(an["M"]["face"])
    for j in range(4):          # 飞出去时冒小爱心（每颗自己的时间，≥0.3 s 淡入淡出）
        tt = t0 + 0.8 + j * 0.7; u = pr(t, tt, tt + 1.4)
        if 0 < u < 1: heart(d, fx + 60 + 30 * math.sin(j * 2.1), fy - 40 - 120 * u, 22, PINK, math.sin(math.pi * u))
def ui_night(t, d, P, an):
    t0 = T["night"]; a = cl((t - t0) / 0.3)
    d.rect(200, 300, 380, 380, A((20, 30, 70), 0.7 * a), r=24); d.text(290, 341, "2:00", 48, A(CYAN, a))
    bx, by = P(an["B"]["top"])
    for j in range(3):
        u = ((t - t0) * 0.5 + j / 3) % 1.0
        d.text(bx + 40 + 50 * u + 20 * j, by - 50 - 160 * u, "z", int(36 + 30 * u), A(CYAN, a * math.sin(math.pi * u)))
    fx, fy = P(an["M"]["face"])
    for j in range(3):          # 踮脚：脚边小星点
        u = ((t - t0) * 1.6 + j / 3) % 1.0
        d.circ(fx - 60 - 40 * u, fy + 330 - 20 * j, 7 * (1 - u), A(WHITE, (1 - u) * 0.7 * a))
def ui_q(t, d, P, an):
    t0 = T["q"]; fx, fy = P(an["M"]["top"])
    mark(d, t, t0 + 0.15, fx - 130, fy + 10, "?", GOLD, 110); mark(d, t, t0 + 0.45, fx + 120, fy - 30, "?", GOLD, 90)
def ui_big2(t, d, P, an):
    t0 = BIG2; fx, fy = P(an["M"]["thorax"])
    ring(d, fx, fy, t, t0, WHITE, 420)
    bigword(d, t, t0, 540, 400, "暖宝宝上线", (255, 250, 230), 120, bgc=(60, 10, 40))
def ui_know(t, d, P, an):
    t0 = T["know"]; a = cl((t - t0 - 0.1) / 0.3) * (1 - pr(t, T["temp"] - 0.3, T["temp"])); dy = 30 * (1 - ease(pr(t, t0 + 0.1, t0 + 0.5)))
    xw = an["_st"]["wipe"] * OW
    if 0.0 < an["_st"]["wipe"] < 1.0: d.rect(xw - 4, 0, xw + 4, OH, A(WHITE, 0.8))
    if a <= 0: return
    d.rect(195, 260 + dy, 885, 600 + dy, A(WHITE, 0.94 * a), r=44)
    d.rect(380, 290 + dy, 700, 354 + dy, A(GOLD, a), r=32); d.text(540, 322 + dy, "一句话学会", 38, A(NAVY, a))
    d.text(540, 430 + dy, "热成像：拍下热量", 60, A(NAVY, a))
    d.text(540, 525 + dy, "越白越热", 60, A(RED, a))
    for i in range(40):          # 色标：冷（紫）→ 热（白）
        c = LUT[int(i / 39 * 255)]
        d.rect(846, 1180 - i * 11, 880, 1180 - i * 11 + 12, A(tuple(int(v) for v in c), a))
    d.text(863, 715, "热", 34, A(WHITE, a)); d.text(863, 1225, "冷", 34, A(WHITE, a))
def ui_temp(t, d, P, an):
    t0 = T["temp"]; tx, ty = P(an["M"]["thorax"])
    a = cl((t - t0) / 0.3)
    v = 31.0 + 3.8 * ease(pr(t, t0 + 0.6, t0 + 3.2))
    heatwaves(d, tx, ty - 60, t, a * pr(t, t0 + 0.8, t0 + 1.4))
    d.rect(345, 300, 735, 470, A(DARK, 0.6 * a), r=40)
    col = tuple(int(lerp(c1, c2, pr(v, 31, 34.8))) for c1, c2 in zip(CYAN, RED))
    d.text(540, 385, f"{v:.1f}℃", 100, A(col, a))
    ptag(d, t, t0 + 0.3, 262, 385, "平时", CYAN, 36, NAVY, t1=t0 + 3.2)
    ptag(d, t, t0 + 3.2, 815, 385, "保温时", RED, 36, WHITE)
def ui_muscle(t, d, P, an):
    t0 = T["muscle"]; a = cl((t - t0 - 0.2) / 0.3)
    tx, ty = P(an["M"]["thorax"])
    cx, cy, R = 745, 600, 130
    if a > 0:
        d.line([(tx, ty), (cx, ty), (cx, cy + R)], A(WHITE, 0.8 * a), 6)
        d.circ(cx, cy, R + 10, A(WHITE, 0.95 * a)); d.circ(cx, cy, R, A((255, 226, 150), a))
        ph = (t * 9.0) % 2.0 < 1.0      # 两组飞行肌交替收缩（上下 / 前后）
        k1, k2 = (1.0, 0.7) if ph else (0.7, 1.0)
        d.rect(cx - 110 * k2, cy - 32, cx + 110 * k2, cy + 32, A((220, 70, 80), a), r=30)
        d.rect(cx - 30, cy - 120 * k1, cx + 30, cy + 120 * k1, A((236, 110, 100), a), r=26)
        heatwaves(d, cx, cy - 90, t, a, 3, 90, (255, 120, 40))
    ptag(d, t, t0 + 0.6, 745, 425, "飞行肌", RED, 46, WHITE)
def ui_exp(t, d, P, an):
    t0 = T["exp"]
    for j, (bx, by, bz, n) in enumerate(BOXES):
        x, y = P([bx, by + 0.75, bz])
        ptag(d, t, t0 + 0.6 + j * 0.45, x, y, f"+{n}", GOLD if n else WHITE, 48)
    a = cl((t - t0 - 0.2) / 0.3)
    d.rect(370, 300, 710, 380, A(DARK, 0.5 * a), r=40); d.text(540, 340, "共 75 巢", 48, A(WHITE, a))
def odo(d, x, y, v, col, a, size=96):
    d.text(x, y, v, size, A(col, a))
def ui_start(t, d, P, an):
    t0 = T["start"]; a = cl((t - t0) / 0.3)
    for side, bx, tday, nd in ((0, -0.5, DAY_L, 15), (1, 0.5, DAY_R, 6)):
        x, y = P([bx, 0.95, 0.0])
        dd = min(nd, int(nd * pr(t, t0 + 0.3, t0 + tday)) + (1 if t >= t0 + tday else 0))
        dd = min(dd, nd)
        d.rect(x - 130, y - 70, x + 130, y + 70, A(DARK, 0.55 * a), r=30)
        done = t >= t0 + tday
        odo(d, x, y - 2, f"第{max(dd, 1)}天", GOLD if done else WHITE, a, 64)
        if done: mark(d, t, t0 + tday, x, y - 120, "下蛋!", GREEN, 56)
        xb, yb = P([bx + 0.3, 0.7, 0.31])
        ptag(d, t, t0 + 0.2, xb, yb, "+0" if side == 0 else "+5", WHITE if side == 0 else GOLD, 36)
def ui_brood(t, d, P, an):
    t0 = T["brood"]; a = cl((t - t0) / 0.3)
    for key, v, col, tg in (("L", 32.5, WHITE, "+0"), ("R", 49.1, GOLD, "+5")):
        x, y = P(an[key]["top"])
        vv = v * ease(pr(t, t0 + 0.3, t0 + 2.2))
        d.rect(x - 120, y - 230, x + 120, y - 130, A(DARK, 0.55 * a), r=30); d.text(x, y - 180, f"{vv:.1f}", 70, A(col, a))
        ptag(d, t, t0 + 0.2, x, y - 300, tg, col, 40)
    bigword(d, t, t0 + 2.6, 540, 360, "×1.5", RED, 120)
def ui_lab(t, d, P, an):
    t0 = T["lab"]; a = cl((t - t0 - 0.9) / 0.3)
    x0, y0 = P([-0.75, 0.05, 0.475]); x1, y1 = P([0.75, 1.05, 0.475])     # 透明前壁：几道玻璃反光
    if a > 0:
        for j in range(3):
            xx = lerp(x0, x1, 0.15 + j * 0.3)
            d.line([(xx, y1 + 40), (xx + 90, y1 + 160)], A(WHITE, 0.45 * a), 10)
    b = cl((t - t0 - 1.4) / 0.3)            # 工蜂图标 + 斜杠（巢里没有工蜂）
    if b > 0:
        cx, cy = 300, 360
        d.circ(cx, cy, 78, A(WHITE, 0.9 * b)); d.circ(cx, cy + 14, 32, A((50, 42, 48), b)); d.circ(cx, cy - 26, 24, A((50, 42, 48), b))
        d.rect(cx - 30, cy + 2, cx + 30, cy + 20, A(GOLD, b), r=8)
        d.line([(cx - 55, cy - 55), (cx + 55, cy + 55)], A(RED, b), 14)
    fx, fy = P(an["M"]["top"])
    mark(d, t, t0 + 1.0, fx + 80, fy - 10, "!", RED, 80)
def ui_wild(t, d, P, an):
    t0 = T["wild"]
    mark(d, t, t0 + 0.3, 790, 400, "?", GOLD, 130); mark(d, t, t0 + 0.7, 620, 330, "?", WHITE, 100)
    a = cl((t - t0 - 1.0) / 0.3)
    if a > 0:      # 时钟图标：指针转圈（能待多久？）
        cx, cy = 300, 420; d.circ(cx, cy, 70, A(WHITE, 0.95 * a)); d.circ(cx, cy, 58, A((255, 244, 220), a))
        ang = (t - t0) * 4.0
        d.line([(cx, cy), (cx + 44 * math.sin(ang), cy - 44 * math.cos(ang))], A(NAVY, a), 9)
        d.line([(cx, cy), (cx + 28 * math.sin(ang / 12), cy - 28 * math.cos(ang / 12))], A(NAVY, a), 11)
def ui_end(t, d, P, an):
    t0 = T["end"]; M = an["M"]; u = t - t0
    if M["badge"] is not None:
        bx, by = P(M["badge"])
        f = math.cos(math.pi * eio(pr(u, 0.4, 0.9)))
        txt = "实习生" if f > 0 else "育婴室保温员"
        px_, py_ = 540, 430; aa = cl(u / 0.3)
        d.line([(bx, by), (800, by), (800, py_), (730, py_)], A(WHITE, 0.85 * aa), 5)
        badge2d(d, px_, py_, 1.5, txt, aa, flip=f, w0=lerp(220, 380, eio(pr(u, 0.4, 0.9))))
        if u > 0.9: ring(d, px_, py_, t, t0 + 0.9, GOLD, 300)
    for j in range(14):          # 彩纸（每片自己的轨迹，渐隐）
        tt = t0 + 0.9 + (j % 5) * 0.08; v = pr(t, tt, tt + 2.2)
        if 0 < v < 1:
            x = 540 + (j - 6.5) * 50 + 60 * math.sin(j * 1.7 + v * 4); y = 300 + v * 700
            d.rect(x - 9, y - 5, x + 9, y + 5, A([GOLD, PINK, CYAN, GREEN][j % 4], math.sin(math.pi * v)), r=3)
def ui_ask(t, d, P, an):
    t0 = T["ask"]
    ptag(d, t, t0 + 1.2, 540, 380, "评论区说说", GOLD, 56)
    if t > DUR - 0.6: d.rect(0, 0, OW, OH, A((0, 0, 0), pr(t, DUR - 0.6, DUR)))

HL = {"hook": "吃白饭", "myth": "找对象", "night": "育婴室", "q": "干嘛", "big2": "保温", "temp": "34.8度", "muscle": "抖着发热",
      "exp": "0、1、3或5只", "start": "6天多", "brood": "大约一半", "lab": "实验室", "wild": "还不确定", "end": "转正啦", "ask": "涨工资"}
NOSUB = ("know",)
def subs(t, d):
    for a, b, s, key in SUBS:
        if key in NOSUB: continue
        if a <= t < b:
            ee = E.enter_exit(t, max(a, 0), b, 0.3, 0.12, rise=18, s0=0.96)
            al = ee["alpha"] if a > 0 else (1 - pr(t, b - 0.12, b))
            if al <= 0.01: return
            ls = s.split("|"); n = len(ls); y0 = 1340 - (n - 1) * 70 + ee["dy"] * (a > 0)
            w = max(d.tlen(x, 54) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 70 + 46, A((30, 20, 12), 0.8 * al), r=22)
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
    s = "动物打工人 No.04"; w = d.tlen(s, 30) + 56
    d.rect(540 - w / 2, 150, 540 + w / 2, 204, A((40, 26, 12), 0.55), r=27); d.text(540, 177, s, 30, A(WHITE, 1))
    d.text(540, 234, "Vibe 知识大赏 · 熊蜂保温员", 24, A((250, 250, 240), 0.85), k=0)

SF = {n: globals()["sh_" + n] for n in NAMES}; UF = {n: globals()["ui_" + n] for n in NAMES}
SECS = [(-1.0 if i == 0 else T[n], (99 if i == len(NAMES) - 1 else nxt(n)), SF[n], UF[n], n) for i, n in enumerate(NAMES)]
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
        if h > 0 and h <= t < h + 0.1: d.rect(0, 0, OW, OH, A(WHITE, 0.5 * (1 - (t - h) / 0.1)))
    brand(t, d); subs(t, d)
    return pil

if __name__ == "__main__":
    if sys.argv[1] in ("test", "faces"):
        os.makedirs(os.path.join(HERE, "tests"), exist_ok=True)
        for ts in sys.argv[2:]:
            t0 = time.time(); fi = int(round(float(ts) * FPS)); fi -= fi % 2
            im = frame(fi); im.save(os.path.join(HERE, "tests", f"test_{float(ts):05.2f}.png"))
            if sys.argv[1] == "faces":
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
