# 场景：海底“办公室”（珊瑚礁）——背景水墙 + 沙地 + 珊瑚石 + 摇摆海草 + 连续上升的气泡
#  - 气泡：每个气泡有自己的出生/消亡时间，尺寸 0→1→0 渐变 ≥0.4 s，不会一帧冒出或消失（防闪烁规则）
#  - 全部由 t 连续驱动，无逐帧随机
#  - office=True 时加一张珊瑚石“办公桌” + 咖啡杯（打工人梗）
# 独立运行：python3 reef.py → 样张 reef_G.png
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
from clay_proto import prim, group
import clay_proto as _cp
LAST = {}          # 最近一次 reef() 的图元区间：LAST['bubbles'] = (p0, p1)（穿模检查时气泡不算障碍）

WATER = (64, 156, 206); SAND = (238, 214, 168)
CORALS = [(-1.45, -1.1, 0.42, (246, 132, 120)), (1.5, -1.2, 0.38, (176, 128, 220)), (-0.95, -1.7, 0.3, (255, 196, 90)),
          (1.05, -1.75, 0.34, (120, 200, 190)), (-1.8, -0.2, 0.3, (236, 120, 170)), (1.85, -0.3, 0.32, (255, 170, 90))]
KELP = [(-1.25, -1.45, 5, 0.0), (1.3, -1.5, 6, 1.3), (-1.7, -0.9, 4, 2.1), (1.75, -0.95, 5, 0.7)]

def bubble_list(t, n=10, x0=-1.6, x1=1.6, z0=-1.6, z1=0.6, rise=0.35, H=3.2, seed=3):
    """返回 [(x,y,z,r)]：每个气泡周期性上升，周期两端尺寸平滑到 0"""
    out = []
    for i in range(n):
        h1 = math.sin(i * 12.9898 + seed * 78.233) * 43758.5453; h1 -= math.floor(h1)
        h2 = math.sin(i * 39.346 + seed * 11.135) * 24634.6345; h2 -= math.floor(h2)
        h3 = math.sin(i * 73.156 + seed * 52.235) * 12345.6789; h3 -= math.floor(h3)
        per = H / (rise * (0.7 + 0.6 * h3))
        u = ((t + h1 * per) / per) % 1.0
        r = (0.035 + 0.04 * h2) * min(1.0, u / 0.12) * min(1.0, (1 - u) / 0.12)    # 两端 ≥0.12 周期渐变（周期 6–15 s → ≥0.7 s）
        if r < 0.004: continue
        x = x0 + (x1 - x0) * h1 + 0.06 * math.sin(t * 2.0 + i)
        z = z0 + (z1 - z0) * h2
        out.append((x, 0.1 + u * H, z, r))
    return out

def reef(t=0.0, water=WATER, sand=SAND, bubbles=10, office=False, kelp=True, corals=True, seed=3):
    gw = group((0, 2.0, -2.6), 5.0)
    prim(2, 0, [0, 2.0, -2.6], [4.5, 3.6, 0.2], 0.08, 0, water, 0.1, gw)
    gf = group((0, -0.1, 0), 5.0)
    prim(2, 0, [0, -0.1, 0], [4.5, 0.1, 3.5], 0.05, 0, sand, 0.1, gf)
    for i in range(7):   # 沙地小起伏（涂色深浅斑）
        a = i * 2.4 + seed
        prim(0, 2, [math.sin(a) * 1.6, -0.02, -0.4 + math.cos(a * 1.3) * 1.0], [0.4, 0.05, 0.3], 0.006, 0.06, (226, 196, 146), 0.1, gf)
    if corals:
        for j, (cx, cz, r, col) in enumerate(CORALS):
            g = group((cx, r * 0.9, cz), r * 1.9)
            prim(0, 0, [cx, r * 0.5, cz], [r, r * 0.75, r * 0.85], 0, 0.0, col, 0.25, g)
            for k in range(3):
                a = k * 2.1 + j
                prim(0, 0, [cx + math.cos(a) * r * 0.55, r * (1.0 + 0.25 * k), cz + math.sin(a) * r * 0.4], [r * 0.42] * 3, 0, r * 0.25, col, 0.25, g)
    if kelp:
        for (kx, kz, n, ph) in KELP:
            g = group((kx, n * 0.17, kz), n * 0.2 + 0.3)
            px, py = kx, 0.0
            for k in range(n):
                sw = 0.09 * math.sin(t * 1.6 + ph + k * 0.6) * (k + 1) / n
                nx, ny = kx + sw * (k + 1) * 0.6, py + 0.32
                prim(1, 0, [px, py, kz], [nx, ny, kz], 0.07 - 0.006 * k, 0.04, (84, 170, 96) if k % 2 else (104, 188, 110), 0.25, g)
                px, py = nx, ny
    _b0 = len(_cp.PRIMS)
    for (bx, by, bz, br) in bubble_list(t, bubbles, seed=seed):
        g = group((bx, by, bz), br * 1.2)
        prim(0, 0, [bx, by, bz], [br, br, br], 0, 0.0, (214, 238, 252), 1.0, g)
    LAST['bubbles'] = (_b0, len(_cp.PRIMS))
    if office:
        gd = group((0.0, 0.25, 0.55), 1.5)
        prim(0, 0, [0.0, 0.18, 0.55], [1.05, 0.22, 0.32], 0, 0.0, (236, 170, 150), 0.2, gd)
        prim(2, 0, [0.0, 0.40, 0.55], [1.05, 0.04, 0.32], 0.04, 0.05, (246, 196, 176), 0.2, gd)
        gm = group((0.62, 0.55, 0.62), 0.2)
        prim(1, 0, [0.62, 0.47, 0.62], [0.62, 0.56, 0.62], 0.065, 0.0, (240, 92, 80), 0.35, gm)
        prim(1, 1, [0.62, 0.58, 0.62], [0.62, 0.68, 0.62], 0.05, 0.005, (90, 50, 30), 0.3, gm)

if __name__ == "__main__":
    import time, numpy as np, cv2, clay_proto as cp
    from clay_build import arr, reset
    from characters.clownfish import clownfish
    from props.anemone import anemone
    reset(); reef(1.0, office=False)
    anemone(-0.1, -0.5, 1.0, 0.0, 1.0, face=True)
    clownfish(0.5, 0.4, 0.7, -0.5, "happy", y=0.4, tie=True)
    PI, PF, GR, G0, G1 = arr()
    cam, tgt = np.array([0.0, 1.3, 4.4]), np.array([0.0, 0.7, 0.0])
    L = np.array([-0.55, 0.75, 0.55]); L /= np.linalg.norm(L)
    img = np.zeros((1280, 720, 3)); dep = np.zeros((1280, 720)); t0 = time.time()
    cp.render(720, 1280, 0, 720, 0, 1280, cam, tgt, math.radians(44), L, PI, PF, GR, G0, G1, img, dep, np.ones(7, np.int64), 0.0)
    cv2.imwrite("reef_G.png", cp.post(img, dep, 4.2)[..., ::-1]); print("render", round(time.time() - t0, 1), "s -> reef_G.png")
