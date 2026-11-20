# 熊蜂巢道具（动物打工人 No.04，2026-11-20）
#  brood()     育雏团：蜡质底座 + 蜡杯 + 白胖幼虫（睡脸）+ 一小撮卵；n_larva / n_egg 可变，每只幼虫有自己的“出生”时间（≥0.3 s 弹入，不会一帧冒出）
#  honey_pot() 蜜罐（蜡杯 + 琥珀色蜜面，亮面）
#  lab_box()   实验室小蜂巢：底板 + 12 条棱（胶囊）+ 可选盖子 & 锁，正面敞开好拍到里面
#  flower()    野花（茎 + 五瓣 + 花心），野外场景用
#  thermo_cam() 热成像相机（橙色机身 + 大镜头 + 屏幕）
# 返回值里给出幼虫/卵的世界坐标，供 2D 热成像图层和标签定位
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
from clay_proto import prim, group

WAX = (214, 150, 66); WAX_D = (186, 120, 50); WAX_L = (236, 186, 100)
LARVA = (252, 248, 236); INKC = (30, 20, 22); BLUSH = (255, 150, 150); EGG = (255, 252, 240)
HONEY = (236, 150, 30)

def _back(x):
    x = max(0.0, min(1.0, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# 幼虫在育雏团上的位置（局部，单位=s）：x, z, 朝向, 大小
LARVA_POS = [(-0.2, 0.12, 0.4, 1.0), (0.18, 0.16, -0.5, 0.95), (0.0, -0.08, 0.1, 1.05), (-0.32, -0.12, 0.9, 0.85),
             (0.33, -0.1, -1.0, 0.9), (-0.1, 0.26, 0.0, 0.8), (0.12, -0.26, 0.6, 0.85), (-0.38, 0.12, 1.2, 0.75),
             (0.4, 0.14, -1.3, 0.75), (-0.2, -0.3, 0.3, 0.8), (0.28, -0.32, -0.6, 0.78), (0.0, 0.34, 0.2, 0.72)]

def brood(x, z, s=1.0, t=0.0, n_larva=5, n_egg=6, wig=1.0, born=None, y=0.0, faces=True, seed=0):
    """born: 每只幼虫的出生时间列表（None=都已在）；返回 {'top','center','larvae':[(pos, r)], 'eggs': pos}"""
    if s < 0.02: return None
    def W(px, py, pz): return [x + px * s, y + py * s, z + pz * s]
    g = group(W(0, 0.2, 0), 0.75 * s, 0.03 * s)
    prim(0, 0, W(0, 0.1, 0), [0.52 * s, 0.2 * s, 0.44 * s], 0, 0.0, WAX_D, 0.2, g)            # 蜡底座
    for i in range(6):                                                                       # 蜡疙瘩（凹凸）
        a = i * 1.05 + seed
        prim(0, 0, W(math.cos(a) * 0.36, 0.17, math.sin(a) * 0.3), [0.17 * s, 0.12 * s, 0.17 * s], 0, 0.06 * s, WAX, 0.25, g)
    out = {"top": W(0, 0.45, 0), "center": W(0, 0.25, 0), "larvae": [], "eggs": None}
    # 卵：一个蜡杯里一小撮白色长圆卵
    if n_egg > 0:
        ex, ez = 0.3, 0.22
        prim(0, 0, W(ex, 0.27, ez), [0.13 * s, 0.07 * s, 0.11 * s], 0, 0.03 * s, WAX_L, 0.25, g)
        prim(0, 1, W(ex, 0.33, ez), [0.09 * s, 0.05 * s, 0.07 * s], 0, 0.01 * s, WAX_D, 0.25, g)
        ge = group(W(ex, 0.33, ez), 0.14 * s, 0.0)
        for k in range(n_egg):
            a = k * 2.4; r = 0.035 * math.sqrt(k)
            prim(0, 0, W(ex + math.cos(a) * r, 0.33, ez + math.sin(a) * r), [0.022 * s, 0.03 * s, 0.022 * s], 0, 0.0, EGG, 0.6, ge)
        out["eggs"] = W(ex, 0.34, ez)
    # 幼虫：白胖 C 形（三段球），睡脸
    for i in range(min(n_larva, len(LARVA_POS))):
        lx, lz, yaw, sc = LARVA_POS[i]
        k = 1.0
        if born is not None and i < len(born):
            k = _back((t - born[i]) / 0.35) if t >= born[i] else 0.0
            k = min(k, 1.15)
        if k <= 0.02: continue
        r = 0.085 * sc * k
        br = 1 + 0.06 * wig * math.sin(t * 2.2 + i * 1.7)                                  # 呼吸起伏
        cyw, syw = math.cos(yaw), math.sin(yaw)
        def L(px, py, pz): return W(lx + px * cyw + pz * syw, py, lz - px * syw + pz * cyw)
        base = 0.3
        gl = group(L(0, base + 0.08, 0), (0.2 * sc * k + 0.02) * s, 0.0)
        segs = [(-0.07, base + 0.02, -0.02, 0.9), (0.0, base + 0.07, 0.0, 1.0), (0.06, base + 0.03, 0.05, 0.85)]
        for (px, py, pz, rr) in segs:
            prim(0, 0, L(px * sc * k, py + (py - base) * (k - 1), pz * sc * k), [r * rr * br * s, r * rr * 0.92 * br * s, r * rr * br * s], 0, 0.03 * r * s, LARVA, 0.45, gl)
        if faces and k > 0.6:   # 睡脸：两条小弧 + 腮红（在中间那段朝前的一面）
            fy = base + 0.08 + 0.0
            for sx in (-1, 1):
                prim(1, 0, W(lx + sx * 0.03 * sc, fy + 0.012 * sc, lz + r * 0.95), W(lx + sx * 0.012 * sc, fy + 0.004 * sc, lz + r * 1.0),
                     0.006 * s * sc, 0.001 * s, INKC, 0.8, gl)
                prim(0, 2, W(lx + sx * 0.05 * sc, fy - 0.012, lz + r * 0.92), [0.018 * sc * s] * 3, 0.002 * s, 0.006 * s, BLUSH, 0.2, gl)
        out["larvae"].append((W(lx, base + 0.07, lz), r * s))
    return out

def honey_pot(x, z, s=1.0, y=0.0, level=1.0):
    def W(px, py, pz): return [x + px * s, y + py * s, z + pz * s]
    g = group(W(0, 0.14, 0), 0.25 * s, 0.0)
    prim(0, 0, W(0, 0.1, 0), [0.17 * s, 0.13 * s, 0.17 * s], 0, 0.0, WAX, 0.25, g)
    prim(0, 1, W(0, 0.22, 0), [0.12 * s, 0.07 * s, 0.12 * s], 0, 0.012 * s, WAX_D, 0.25, g)
    if level > 0.02:
        prim(0, 0, W(0, 0.12 + 0.06 * level, 0), [0.115 * s, 0.03 * s, 0.115 * s], 0, 0.01 * s, HONEY, 0.95, g)
    return {"top": W(0, 0.25, 0)}

def lab_box(x, z, w=0.9, h=0.6, d=0.7, y=0.0, col=(170, 210, 230), lid=0.0, lock=False, base=(236, 236, 228)):
    g = group([x, y + h / 2, z], math.sqrt(w * w + h * h + d * d) / 2 + 0.1, 0.0)
    prim(2, 0, [x, y + 0.03, z], [w / 2, 0.03, d / 2], 0.02, 0.0, base, 0.2, g)
    r = 0.025
    xs, ys, zs = (x - w / 2, x + w / 2), (y + 0.03, y + h), (z - d / 2, z + d / 2)
    for X in xs:
        for Z in zs: prim(1, 0, [X, ys[0], Z], [X, ys[1], Z], r, 0.0, col, 0.5, g)
    for Y in ys:
        for Z in zs: prim(1, 0, [xs[0], Y, Z], [xs[1], Y, Z], r, 0.0, col, 0.5, g)
        for X in xs: prim(1, 0, [X, Y, zs[0]], [X, Y, zs[1]], r, 0.0, col, 0.5, g)
    if lid > 0.01:   # 盖子（从上方落下）
        ly = y + h + 0.03 + (1 - lid) * 1.5
        prim(2, 0, [x, ly, z], [w / 2 + 0.02, 0.025, d / 2 + 0.02], 0.02, 0.0, col, 0.5, g)
        if lock:
            prim(2, 0, [x, ly - 0.08, z + d / 2 + 0.04], [0.07, 0.06, 0.03], 0.02, 0.0, (250, 200, 50), 0.8, g)
            prim(1, 0, [x - 0.04, ly - 0.02, z + d / 2 + 0.04], [x + 0.04, ly - 0.02, z + d / 2 + 0.04], 0.02, 0.0, (220, 220, 230), 0.8, g)
    return {"top": [x, y + h + 0.1, z], "front": [x, y + h / 2, z + d / 2]}

def flower(x, z, s=1.0, petal=(255, 140, 170), t=0.0, ph=0.0):
    sw = 0.04 * math.sin(t * 1.5 + ph)
    def W(px, py, pz): return [x + px * s, py * s, z + pz * s]
    g = group(W(sw, 0.5, 0), 0.35 * s, 0.0)
    prim(1, 0, W(0, 0, 0), W(sw, 0.62, 0), 0.03 * s, 0.0, (90, 170, 80), 0.2, g)
    prim(0, 0, W(0.08, 0.28, 0.02), [0.09 * s, 0.03 * s, 0.05 * s], 0, 0.03 * s, (110, 186, 90), 0.2, g)
    for k in range(5):
        a = k * 2 * math.pi / 5
        prim(0, 0, W(sw + math.cos(a) * 0.1, 0.66 + math.sin(a) * 0.1, 0.0), [0.075 * s, 0.075 * s, 0.03 * s], 0, 0.02 * s, petal, 0.3, g)
    prim(0, 0, W(sw, 0.66, 0.03), [0.06 * s] * 3, 0, 0.01 * s, (255, 210, 60), 0.4, g)
    return {"top": W(sw, 0.8, 0)}

def thermo_cam(x, z, s=1.0, y=0.0, yaw=0.0, rec=1.0, body=(255, 128, 40)):
    cy, sy = math.cos(yaw), math.sin(yaw)
    def T(px, py, pz): return [x + (px * cy + pz * sy) * s, y + py * s, z + (-px * sy + pz * cy) * s]
    g = group(T(0, 0.55, 0), 0.75 * s, 0.0)
    for a in (0.0, 2.1, 4.2):
        prim(1, 0, T(0, 0.5, 0), T(math.cos(a) * 0.28, 0.0, math.sin(a) * 0.28), 0.025 * s, 0.01 * s, (60, 60, 70), 0.4, g)
    prim(2, 0, T(0, 0.68, 0), [0.2 * s, 0.15 * s, 0.17 * s], 0.06 * s, 0.0, body, 0.35, g)
    prim(1, 0, T(0, 0.68, 0.12), T(0, 0.68, 0.32), 0.11 * s, 0.02 * s, (46, 50, 62), 0.5, g)
    prim(0, 0, T(0, 0.68, 0.31), [0.075 * s] * 3, 0, 0.004 * s, (150, 60, 160), 1.0, g)     # 锗镜头（紫色反光）
    prim(0, 0, T(0.12, 0.86, 0.06), [0.032 * s * rec + 0.001] * 3, 0, 0.004 * s, (255, 50, 50), 0.9, g)
    return {"lens": T(0, 0.68, 0.36), "top": T(0, 0.9, 0)}
