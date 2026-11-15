# 丛林植物：tree 树（树干+枝+6 团树冠）、vine 藤（可摆动 sway）、bush 灌木、fern 蕨叶
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # 仓库根（engine/ characters/ props/ scenes/ 的上一级）
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):   # CLAY_ENGINE_DIR 优先（最后插到最前）
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
import numpy as np
from clay_proto import prim, group

LEAF1, LEAF2, LEAF3, TRUNK = (88, 160, 80), (120, 186, 96), (64, 130, 72), (140, 96, 62)
def tree(x, z, h=2.6, crown=0.9, seed=0):
    rng = np.random.default_rng(seed)
    g = group((x, h * 0.55, z), h * 0.55 + crown)
    prim(1, 0, [x, -0.05, z], [x + 0.08, h, z], 0.16, 0.0, TRUNK, 0.15, g)
    prim(1, 0, [x + 0.04, h * 0.6, z], [x + 0.5 * (1 if seed % 2 else -1), h * 0.85, z + 0.1], 0.07, 0.06, TRUNK, 0.15, g)
    for i in range(6):
        a = i / 6 * 2 * math.pi + seed
        rr = crown * (0.45 + 0.15 * rng.random())
        prim(0, 0, [x + math.cos(a) * crown * 0.55, h + math.sin(a) * crown * 0.35 + 0.1, z + 0.15 * math.sin(a * 2)], [rr, rr * 0.8, rr * 0.7], 0, 0.06,
             (LEAF1, LEAF2, LEAF3)[i % 3], 0.2, g)
    return g
def vine(x, z, y0=3.4, y1=1.8, seed=0, sway=0.0):
    g = group((x, (y0 + y1) / 2, z), (y0 - y1) / 2 + 0.25)
    n = 6; pts = []
    for i in range(n + 1):
        u = i / n; pts.append([x + 0.06 * math.sin(u * 5 + seed) + sway * u * u, y0 + (y1 - y0) * u, z])
    for i in range(n):
        prim(1, 0, pts[i], pts[i + 1], 0.025, 0.02, (96, 140, 60), 0.2, g)
    for i in range(1, n + 1, 2):
        sx = 1 if i % 4 == 1 else -1
        p = pts[i]
        prim(0, 0, [p[0] + sx * 0.08, p[1], p[2] + 0.02], [0.09, 0.05, 0.03], 0, 0.02, LEAF2, 0.25, g)
    return g
def bush(x, z, s=1.0, seed=0, col=None):
    g = group((x, 0.25 * s, z), 0.75 * s)
    for i in range(4):
        a = i * 1.7 + seed
        prim(0, 0, [x + math.cos(a) * 0.3 * s, 0.22 * s + 0.08 * s * (i % 2), z + math.sin(a) * 0.15 * s], [0.3 * s, 0.26 * s, 0.24 * s], 0, 0.05 * s,
             col or (LEAF1, LEAF2, LEAF3)[i % 3], 0.2, g)
    return g
def fern(x, z, s=1.0, ang=0.0, seed=0):
    g = group((x, 0.35 * s, z), 0.7 * s)
    for i in range(5):
        a = ang + (i - 2) * 0.45
        tip = [x + math.sin(a) * 0.55 * s, 0.6 * s - 0.1 * abs(i - 2) * s, z + 0.1 * s]
        prim(0, 0, [(x + tip[0]) / 2, (0.05 + tip[1]) / 2 + 0.05, z + 0.05 * s], [0.08 * s + abs(math.sin(a)) * 0.2 * s, 0.25 * s, 0.035 * s], 0, 0.02,
             LEAF2 if i % 2 else LEAF1, 0.25, g)
    return g
