# 关系连线：link 直线（从 p 长向 q）、arc_link 拱形线（中点抬高，按 k 长出）
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # 仓库根（engine/ characters/ props/ scenes/ 的上一级）
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):   # CLAY_ENGINE_DIR 优先（最后插到最前）
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
from clay_proto import prim, group
GOLDC = (255, 196, 60)

def link(p, q, r, col=GOLDC, k=1.0):
    """关系连线：从 p 长向 q（k=0..1），两端圆头"""
    if k <= 0.01 or r <= 0.002: return
    e = [p[i] + (q[i] - p[i]) * k for i in range(3)]
    c = [(p[i] + e[i]) / 2 for i in range(3)]; L = math.dist(p, e) / 2 + r
    g = group(c, L + 0.02)
    prim(1, 0, p, e, r, 0.0, col, 0.55, g)


def arc_link(p, q, r, col=GOLDC, k=1.0, lift=0.35, n=8):
    """拱形关系线：p→q 的二次贝塞尔（中点抬高 lift），按 k 从 p 端长出来"""
    if k <= 0.01 or r <= 0.002: return
    m = [(p[i] + q[i]) / 2 for i in range(3)]; m[1] += lift
    def B(u): return [(1 - u) ** 2 * p[i] + 2 * u * (1 - u) * m[i] + u * u * q[i] for i in range(3)]
    pts = [B(k * j / n) for j in range(n + 1)]
    c = [sum(pt[i] for pt in pts) / len(pts) for i in range(3)]
    R = max(math.dist(c, pt) for pt in pts) + r + 0.02
    g = group(c, R)
    for j in range(n):
        prim(1, 0, pts[j], pts[j + 1], r, 0.0, col, 0.55, g)

