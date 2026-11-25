# 示意图道具：stopwatch 秒表（指针角度 ang）、bar 柱状图立柱、steps 台阶（地位阶梯）
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # 仓库根（engine/ characters/ props/ scenes/ 的上一级）
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):   # CLAY_ENGINE_DIR 优先（最后插到最前）
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
from clay_proto import prim, group

def stopwatch(x, y, z, s, ang):
    g = group((x, y + 0.08 * s, z), 0.62 * s)
    prim(0, 0, [x, y, z], [0.5 * s, 0.5 * s, 0.16 * s], 0, 0, (236, 96, 80), 0.35, g)
    prim(0, 0, [x, y, z + 0.06 * s], [0.42 * s, 0.42 * s, 0.13 * s], 0, 0.02 * s, (252, 248, 236), 0.25, g)
    prim(1, 0, [x, y + 0.5 * s, z], [x, y + 0.6 * s, z], 0.07 * s, 0.02 * s, (236, 96, 80), 0.35, g)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        prim(0, 2, [x + math.sin(a) * 0.34 * s, y + math.cos(a) * 0.34 * s, z + 0.18 * s], [0.022 * s, 0.022 * s, 0.05 * s], 0, 0.006 * s, (120, 100, 90), 0.2, g)
    prim(1, 0, [x, y, z + 0.19 * s], [x + math.sin(ang) * 0.3 * s, y + math.cos(ang) * 0.3 * s, z + 0.19 * s], 0.025 * s, 0.01 * s, (40, 34, 34), 0.5, g)
    prim(0, 0, [x, y, z + 0.19 * s], [0.04 * s, 0.04 * s, 0.03 * s], 0, 0.01 * s, (236, 96, 80), 0.4, g)

def bar(x, z, w, h, d, col):
    if h < 0.01: return
    g = group((x, h / 2, z), math.sqrt(w * w + (h / 2) ** 2 + d * d) + 0.05)
    prim(2, 0, [x, h / 2, z], [w, h / 2, d], 0.04, 0, col, 0.25, g)


def steps(x0, z, n=3, w=0.42, hstep=0.32, col=((236, 206, 150), (226, 186, 120), (255, 214, 110))):
    for i in range(n):
        h = hstep * (i + 1)
        g = group((x0 + i * w * 2, h / 2, z), math.sqrt(w * w + (h / 2) ** 2 + 0.36) + 0.05)
        prim(2, 0, [x0 + i * w * 2, h / 2, z], [w, h / 2, 0.55], 0.05, 0, col[i % len(col)], 0.2, g)

