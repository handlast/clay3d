# 不渲染，只投影各镜头锚点（脸/顶）到 1080×1920，检查构图与安全区
import sys, numpy as np
import film as Fm
for n in Fm.NAMES:
    t = Fm.T[n] + 1.2
    idx = Fm.shot_at(t); c, g, fp, an = Fm.SECS[idx][2](t)
    out = []
    for k, v in an.items():
        if isinstance(v, dict) and "face" in v:
            x, y = Fm.project(v["face"], (c, g)); out.append(f"{k}:({x:.0f},{y:.0f})")
        elif isinstance(v, tuple):
            for j, w in enumerate(v):
                if isinstance(w, dict): x, y = Fm.project(w["face"], (c, g)); out.append(f"{k}{j}:({x:.0f},{y:.0f})")
    print(f"{n:6s}", " ".join(out))
