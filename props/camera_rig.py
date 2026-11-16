# 水下摄像机 camcorder()：圆角机身 + 镜头筒 + 遮光罩 + 红色录制灯 + 三脚架（全部球/胶囊/盒，可放任意位置）
#  yaw 只影响镜头朝向（机身盒是轴对齐的，yaw 取小角度 ±0.5 以内看起来最自然）
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
from clay_proto import prim, group

def camcorder(x, z, s=1.0, yaw=0.0, rec=1.0, h=0.55, body=(70, 76, 96)):
    cy, sy = math.cos(yaw), math.sin(yaw)
    def T(px, py, pz): return [x + (px * cy + pz * sy) * s, py * s, z + (-px * sy + pz * cy) * s]
    g = group(T(0, h * 0.6, 0), (h + 0.35) * s, 0.0)
    for a in (0.0, 2.1, 4.2):     # 三脚架
        prim(1, 0, T(0, h - 0.05, 0), T(math.cos(a) * 0.28, 0.0, math.sin(a) * 0.28), 0.025 * s, 0.01 * s, (60, 60, 70), 0.4, g)
    prim(2, 0, T(0, h + 0.12, 0), [0.17 * s, 0.13 * s, 0.22 * s], 0.06 * s, 0.0, body, 0.35, g)
    prim(1, 0, T(0, h + 0.12, 0.18), T(0, h + 0.12, 0.34), 0.1 * s, 0.02 * s, (46, 50, 62), 0.5, g)
    prim(1, 1, T(0, h + 0.12, 0.30), T(0, h + 0.12, 0.40), 0.065 * s, 0.01 * s, (20, 24, 36), 0.9, g)
    prim(0, 0, T(0, h + 0.12, 0.29), [0.06 * s] * 3, 0, 0.004 * s, (90, 160, 230), 1.0, g)        # 玻璃镜片
    prim(0, 0, T(0.09, h + 0.27, 0.12), [0.035 * s * rec + 0.001] * 3, 0, 0.004 * s, (255, 50, 50), 0.9, g)   # 录制灯
