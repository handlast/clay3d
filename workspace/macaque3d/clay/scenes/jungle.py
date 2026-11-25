# 场景：丛林（背景墙 + 远景树团 + 草地 + 两棵树 + 两条会摆的藤）
# 独立运行：python3 jungle.py  → 渲染一张 720×1280 样张（含三只猴）到当前目录
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # 仓库根（engine/ characters/ props/ scenes/ 的上一级）
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):   # CLAY_ENGINE_DIR 优先（最后插到最前）
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
from clay_proto import prim, group
from props.basics import backdrop, floor
from props.jungle_plants import tree, vine, bush, fern

def jungle(t=0.0, sky=(178, 218, 196), ground=(132, 176, 88), far=True):
    backdrop(sky, z=-3.2, wx=5.5, wy=4.0)
    if far:   # 远景树团，压在背景墙上
        g = group((0, 1.4, -3.0), 4.5)
        for i, (xx, yy, r) in enumerate([(-2.2, 1.2, 0.9), (-1.2, 1.5, 0.8), (0.0, 1.3, 0.9), (1.2, 1.6, 0.85), (2.3, 1.2, 0.9), (-0.6, 0.6, 0.7), (0.8, 0.6, 0.7)]):
            prim(0, 0, [xx, yy, -3.0], [r, r * 0.8, 0.25], 0, 0.15, ((108, 168, 120), (96, 156, 112), (120, 180, 130))[i % 3], 0.1, g)
    floor(ground, z=-0.3, wx=5.5, wz=3.5)
    tree(-1.55, -1.5, 2.8, 1.0, 1); tree(1.6, -1.7, 3.0, 1.0, 2)
    vine(-0.9, -1.2, 3.6, 2.0, 1, 0.04 * math.sin(t * 1.3)); vine(0.95, -1.3, 3.6, 2.3, 2, 0.04 * math.sin(t * 1.1 + 1))


if __name__ == "__main__":
    import time, numpy as np, cv2, clay_proto as cp
    from clay_build import arr, reset
    from characters.macaque_poses import monkey2
    reset(); jungle(0.0); bush(-1.15, 0.5, 0.9, 1); fern(1.2, 0.9, 1.0, -0.4, 2)
    monkey2(-0.5, -0.3, 0.8, 0.75, "angry", armL="fist", armR="fist"); monkey2(0.15, -0.35, 0.8, -0.75, "angry", armL="fist", armR="fist")
    monkey2(0.5, 0.6, 0.72, -0.3, "wow", hyaw=-0.8)
    PI, PF, GR, G0, G1 = arr()
    cam, tgt = np.array([0.0, 1.3, 5.2]), np.array([0.0, 0.45, 0.0])
    L = np.array([-0.55, 0.75, 0.55]); L /= np.linalg.norm(L)
    img = np.zeros((1280, 720, 3)); dep = np.zeros((1280, 720)); t0 = time.time()
    cp.render(720, 1280, 0, 720, 0, 1280, cam, tgt, math.radians(44), L, PI, PF, GR, G0, G1, img, dep, np.ones(7, np.int64), 0.0)
    cv2.imwrite("jungle_G.png", cp.post(img, dep, 5.0)[..., ::-1]); print("render", round(time.time() - t0, 1), "s -> jungle_G.png")
