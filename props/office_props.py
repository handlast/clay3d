# 办公室小道具：desk 办公桌（抽屉涂色+把手）、mug 咖啡杯
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # 仓库根（engine/ characters/ props/ scenes/ 的上一级）
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):   # CLAY_ENGINE_DIR 优先（最后插到最前）
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
from clay_proto import prim, group

def desk(x=0.0, z=0.52, w=1.25):
    gd = group((x, 0.24, z), w + 0.3)
    prim(2, 0, [x, 0.24, z], [w, 0.23, 0.3], 0.05, 0, (236, 206, 150), 0.15, gd)
    for sx in (-0.7, 0, 0.7):
        if abs(sx) < w - 0.2:
            prim(2, 2, [x + sx, 0.24, z + 0.3], [0.22, 0.12, 0.02], 0.0, 0.008, (218, 182, 122), 0.1, gd)
            prim(1, 0, [x + sx - 0.07, 0.27, z + 0.315], [x + sx + 0.07, 0.27, z + 0.315], 0.018, 0.01, (120, 90, 60), 0.4, gd)
def mug(x, z, y=0.47):
    gm = group((x, y + 0.08, z), 0.2)
    prim(1, 0, [x, y + 0.03, z], [x, y + 0.11, z], 0.065, 0.0, (240, 92, 80), 0.35, gm)
    prim(1, 1, [x, y + 0.13, z], [x, y + 0.23, z], 0.05, 0.005, (90, 50, 30), 0.3, gm)
    prim(0, 0, [x + 0.08, y + 0.075, z], [0.035, 0.04, 0.015], 0, 0.01, (240, 92, 80), 0.35, gm)

