# 场景数组打包：把 clay_proto.PRIMS / GROUPS 打包成 render() 需要的数组；reset() 清空场景
# 用法：from clay_build import arr, reset   （engine/ 在 sys.path 上即可）
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # 仓库根（engine/ characters/ props/ scenes/ 的上一级）
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):   # CLAY_ENGINE_DIR 优先（最后插到最前）
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
import numpy as np
import clay_proto as cp

def arr():
    P = cp.PRIMS; n = len(P)
    PI = np.zeros((n, 3), np.int32); PF = np.zeros((n, 12))
    for i, (t, mode, a, b, r, k, c, gl, g) in enumerate(P):
        PI[i] = (t, mode, g); PF[i] = a + b + [r, k] + c + [gl]
    GR = np.array(cp.GROUPS, np.float64)
    G0 = np.zeros(len(GR), np.int32); G1 = np.zeros(len(GR), np.int32)
    for gi in range(len(GR)):
        idx = np.where(PI[:, 2] == gi)[0]; G0[gi], G1[gi] = idx.min(), idx.max() + 1
    return PI, PF, GR, G0, G1

def reset():
    cp.PRIMS.clear(); cp.GROUPS.clear()

