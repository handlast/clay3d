# 场景：办公室布景（墙色可换 + 涂色窗户 + 走动的挂钟 + 盆栽 + 地板），不含桌子和角色
# 独立运行：python3 office_set.py → 样张 office_set_G.png
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # 仓库根（engine/ characters/ props/ scenes/ 的上一级）
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):   # CLAY_ENGINE_DIR 优先（最后插到最前）
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
from clay_proto import prim, group

def office(t=0.0, wall=(150, 196, 176)):
    gw = group((0, 1.6, -1.95), 4.6)
    prim(2, 0, [0, 1.6, -1.95], [4.0, 2.4, 0.2], 0.08, 0, wall, 0.1, gw)
    prim(2, 2, [-0.75, 2.05, -1.75], [0.48, 0.42, 0.03], 0.0, 0.01, (238, 236, 220), 0.1, gw)
    prim(2, 2, [-0.75, 2.05, -1.75], [0.42, 0.36, 0.035], 0.0, 0.006, (150, 210, 245), 0.3, gw)
    prim(2, 2, [-0.75, 2.05, -1.75], [0.012, 0.36, 0.04], 0.0, 0.004, (238, 236, 220), 0.1, gw)
    prim(2, 2, [-0.75, 2.05, -1.75], [0.42, 0.012, 0.04], 0.0, 0.004, (238, 236, 220), 0.1, gw)
    prim(0, 2, [-0.93, 2.22, -1.75], [0.13, 0.06, 0.05], 0, 0.01, (255, 255, 255), 0.1, gw)
    gf = group((0, -0.1, 0), 5.0)
    prim(2, 0, [0, -0.1, 0], [4.0, 0.1, 3.5], 0.05, 0, (176, 128, 88), 0.1, gf)
    gc = group((0.78, 2.4, -1.7), 0.32)
    prim(0, 0, [0.78, 2.4, -1.72], [0.24, 0.24, 0.06], 0, 0.0, (236, 110, 90), 0.2, gc)
    prim(0, 0, [0.78, 2.4, -1.68], [0.19, 0.19, 0.04], 0, 0.02, (250, 246, 232), 0.2, gc)
    a = t * 0.8
    prim(1, 0, [0.78, 2.4, -1.64], [0.78 + 0.13 * math.sin(a), 2.4 + 0.13 * math.cos(a), -1.64], 0.016, 0.004, (40, 30, 26), 0.4, gc)
    prim(1, 0, [0.78, 2.4, -1.64], [0.86, 2.36, -1.64], 0.016, 0.004, (40, 30, 26), 0.4, gc)
    gp = group((-1.25, 0.6, -1.2), 0.8)
    prim(2, 0, [-1.25, 0.2, -1.2], [0.2, 0.22, 0.2], 0.06, 0, (226, 132, 84), 0.15, gp)
    for i, (dx, dy, dz, sx) in enumerate([(0, 0.62, 0, 0.12), (-0.14, 0.55, 0.02, 0.1), (0.14, 0.52, 0.03, 0.1), (0.05, 0.78, -0.02, 0.09), (-0.08, 0.72, 0.06, 0.09)]):
        prim(0, 0, [-1.25 + dx, dy, -1.2 + dz], [sx, sx * 2.0, sx * 0.7], 0, 0.03, (96, 168, 84) if i % 2 else (120, 186, 96), 0.2, gp)


if __name__ == "__main__":
    import time, numpy as np, cv2, clay_proto as cp
    from clay_build import arr, reset
    from characters.macaque_poses import monkey2
    from props.office_props import desk, mug
    reset(); office(0.0, wall=(176, 206, 232)); desk(); mug(-0.33, 0.6)
    for x, e in ((-0.52, "look"), (0.0, "wow"), (0.52, "happy")): monkey2(x, 0.0, 0.82, -x * 0.6, e, y=0.2, badge=True)
    PI, PF, GR, G0, G1 = arr()
    cam, tgt = np.array([0.0, 1.35, 4.4]), np.array([0.0, 0.8, 0.0])
    L = np.array([-0.55, 0.75, 0.55]); L /= np.linalg.norm(L)
    img = np.zeros((1280, 720, 3)); dep = np.zeros((1280, 720)); t0 = time.time()
    cp.render(720, 1280, 0, 720, 0, 1280, cam, tgt, math.radians(44), L, PI, PF, GR, G0, G1, img, dep, np.ones(7, np.int64), 0.0)
    cv2.imwrite("office_set_G.png", cp.post(img, dep, 4.4)[..., ::-1]); print("render", round(time.time() - t0, 1), "s -> office_set_G.png")
