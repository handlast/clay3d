# 基础道具：背景墙 backdrop、地板 floor（各自一个大包围球组）
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # 仓库根（engine/ characters/ props/ scenes/ 的上一级）
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):   # CLAY_ENGINE_DIR 优先（最后插到最前）
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
from clay_proto import prim, group

def backdrop(col, z=-2.6, y=2.0, wx=4.5, wy=3.6):
    g = group((0, y, z), math.hypot(wx, wy) + 0.3)
    prim(2, 0, [0, y, z], [wx, wy, 0.2], 0.08, 0, col, 0.1, g); return g
def floor(col, y=-0.1, z=0.0, wx=4.5, wz=3.5):
    g = group((0, y, z), math.hypot(wx, wz) + 0.2)
    prim(2, 0, [0, y, z], [wx, 0.1, wz], 0.05, 0, col, 0.1, g); return g

