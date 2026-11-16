# 海葵 anemone()：矮胖柱体 + 口盘 + 三圈触手（每根触手 = 胶囊 + 圆头），随水流摆动
#  - bleach 0..1：健康彩色 → 白化（触手失去共生藻变白，柱体只变淡一点，符合 Radianthus magnifica 白化时柱体常保留颜色）
#    每根触手有自己的变白时间（spread>0 时从一侧扫过去），颜色连续插值，不会一帧突变
#  - face=True：柱体正面 Q 版小脸（look / worry / happy / sick），眼嘴泥条加粗；返回 face 中心/半径供脸部超采样
#  - 触手按扇区分组（各自包围球），减少光线步进代价
# 返回 dict：face / top / center / face_r
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
from clay_proto import prim, group

COL_H = (196, 64, 132); COL_B = (232, 186, 206)          # 柱体：健康 / 白化
TEN_H = (70, 186, 160); TEN_B = (246, 244, 236)          # 触手
TIP_H = (214, 150, 236); TIP_B = (255, 254, 250)         # 触手尖
DISC_H = (120, 200, 120); DISC_B = (240, 236, 226)
INKC = (24, 14, 22); MOUTHC = (110, 24, 50); EYEW = (255, 255, 252); BLUSH = (255, 120, 150)

def _mix(a, b, k): return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))
def _sm(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

RINGS = [(0.14, 6, 0.0), (0.30, 10, 0.3), (0.46, 14, 0.1)]   # 半径、根数、角度偏移

def anemone(x, z, s=1.0, bleach=0.0, t=0.0, face=False, expr="look", spread=0.0, droop=0.0, sway=1.0, seed=0):
    """bleach: 整体白化进度；spread>0 时按触手从左(-x)到右逐根变白，扫过宽度 spread（进度单位）
    droop: 0..1 触手无力下垂（生病）"""
    if s < 0.02: return None
    def W(px, py, pz): return [x + px * s, py * s, z + pz * s]
    # 柱体 + 口盘
    kb = _sm(bleach)
    gc = group(W(0, 0.22, 0), 0.62 * s, 0.0)
    prim(0, 0, W(0, 0.2, 0), [0.56 * s, 0.27 * s, 0.5 * s], 0, 0.0, _mix(COL_H, COL_B, 0.55 * kb), 0.3, gc)
    prim(0, 0, W(0, 0.40, -0.02), [0.5 * s, 0.07 * s, 0.44 * s], 0, 0.06 * s, _mix(DISC_H, DISC_B, kb), 0.3, gc)
    an = {"center": W(0, 0.3, 0), "top": W(0, 0.95, 0)}
    if face:
        fy, fz = 0.2, 0.47
        for sx in (-1, 1):
            ex = sx * 0.15
            prim(0, 2, W(sx * 0.27, fy - 0.07, fz + 0.01), [0.06 * s] * 3, 0.004 * s, 0.015 * s, BLUSH, 0.2, gc)
            if expr == "happy":
                prim(1, 0, W(ex - 0.055, fy, fz + 0.05), W(ex, fy + 0.04, fz + 0.07), 0.024 * s, 0.004 * s, INKC, 0.8, gc)
                prim(1, 0, W(ex, fy + 0.04, fz + 0.07), W(ex + 0.055, fy, fz + 0.05), 0.024 * s, 0.004 * s, INKC, 0.8, gc)
                continue
            if expr == "sick":      # 晕乎乎：X 眼太吓人，用半闭眼（眼球 + 上眼皮压下）
                prim(0, 0, W(ex, fy + 0.02, fz + 0.02), [0.085 * s] * 3, 0, 0.0015 * s, EYEW, 0.55, gc)
                prim(0, 0, W(ex, fy + 0.0, fz + 0.02 + 0.07), [0.045 * s] * 3, 0, 0.001 * s, INKC, 1.0, gc)
                prim(1, 0, W(ex - 0.09, fy + 0.07, fz + 0.06), W(ex + 0.09, fy + 0.07, fz + 0.06), 0.04 * s, 0.01 * s, _mix(COL_H, COL_B, 0.55 * kb), 0.3, gc)
            else:
                prim(0, 0, W(ex, fy + 0.02, fz + 0.02), [0.085 * s] * 3, 0, 0.0015 * s, EYEW, 0.55, gc)
                prim(0, 0, W(ex, fy + 0.02, fz + 0.02 + 0.068), [0.05 * s] * 3, 0, 0.001 * s, INKC, 1.0, gc)
                prim(0, 2, W(ex - 0.018, fy + 0.045, fz + 0.12), [0.016 * s] * 3, 0.002 * s, 0.004 * s, (255, 255, 255), 1.0, gc)
            if expr in ("worry", "sick"):
                prim(1, 0, W(ex + sx * 0.08, fy + 0.11, fz + 0.04), W(ex - sx * 0.05, fy + 0.15, fz + 0.06), 0.022 * s, 0.006 * s, (120, 30, 70), 0.4, gc)
        if expr in ("worry", "sick"):
            prim(1, 1, W(-0.06, fy - 0.12, fz + 0.04), W(0.0, fy - 0.09, fz + 0.05), 0.022 * s, 0.005 * s, MOUTHC, 0.3, gc)
            prim(1, 1, W(0.0, fy - 0.09, fz + 0.05), W(0.06, fy - 0.12, fz + 0.04), 0.022 * s, 0.005 * s, MOUTHC, 0.3, gc)
        else:
            prim(1, 1, W(-0.06, fy - 0.08, fz + 0.04), W(0.0, fy - 0.115, fz + 0.05), 0.022 * s, 0.005 * s, MOUTHC, 0.3, gc)
            prim(1, 1, W(0.0, fy - 0.115, fz + 0.05), W(0.06, fy - 0.08, fz + 0.04), 0.022 * s, 0.005 * s, MOUTHC, 0.3, gc)
        an["face"] = W(0, fy, fz + 0.06); an["face_r"] = 0.24 * s
    # 触手：按扇区分组
    tents = []
    for ri, (rr, n, off) in enumerate(RINGS):
        for i in range(n):
            a = 2 * math.pi * (i + off) / n + seed * 0.37
            tents.append((rr, a, ri, i))
    NSEC = 6
    secs = [[] for _ in range(NSEC)]
    for tt in tents:
        k = int(((tt[1] % (2 * math.pi)) / (2 * math.pi)) * NSEC) % NSEC
        secs[k].append(tt)
    for k, lst in enumerate(secs):
        if not lst: continue
        ac = 2 * math.pi * (k + 0.5) / NSEC
        g = group(W(math.cos(ac) * 0.4, 0.62, math.sin(ac) * 0.4), 0.62 * s, 0.0)
        for rr, a, ri, i in lst:
            bx, bz = math.cos(a) * rr, math.sin(a) * rr * 0.9
            if face and bz > 0.25 and abs(bx) < 0.3 and ri == 2: bz -= 0.05     # 前排让开小脸
            ph = a * 3.1 + ri * 1.7 + seed
            sw = sway * (0.05 * math.sin(t * 2.2 + ph) + 0.025 * math.sin(t * 3.7 + ph * 1.3))
            L = 0.36 + 0.07 * ri
            ca, sa = math.cos(a), math.sin(a) * 0.9
            out = 0.06 + 0.10 * ri + droop * (0.10 + 0.08 * ri)          # 向外张开；生病时更塌
            up = 1.0 - 0.55 * droop
            # 三段：先向外、再向上弯（像手指），末段是彩色指尖
            p0 = (bx, 0.40, bz)
            p1 = (bx + ca * out * 0.6 + sw * 0.3, 0.40 + L * 0.38 * up, bz + sa * out * 0.6)
            p2 = (bx + ca * out * 1.0 + sw * 0.7, 0.40 + L * 0.72 * up, bz + sa * out * 1.0)
            p3 = (bx + ca * out * 1.15 + sw * 1.0, 0.40 + L * 1.0 * up - 0.05 * droop, bz + sa * out * 1.15)
            if spread > 0: kb_i = _sm(bleach * (1 + spread) - spread * (bx + 0.7) / 1.4)
            else: kb_i = kb
            ct = _mix(TEN_H, TEN_B, kb_i); cti = _mix(TIP_H, TIP_B, kb_i); gl_ = 0.35 + 0.2 * kb_i
            r0 = 0.040 * s
            prim(1, 0, W(*p0), W(*p1), r0, 0.008 * s, ct, gl_, g)
            prim(1, 0, W(*p1), W(*p2), r0 * 0.95, 0.008 * s, ct, gl_, g)
            prim(1, 0, W(*p2), W(*p3), r0 * 0.92, 0.02 * s, cti, gl_ + 0.1, g)
    return an

def thermometer(x, y, z, s=1.0, level=0.5, tilt=0.0):
    """体温计（玻璃白管 + 红色液柱 + 红球），level 0..1；tilt 为在 xy 平面里偏离竖直的角度（弧度，正=向右倒）"""
    dx, dy = math.sin(tilt), math.cos(tilt)
    g = group([x + dx * 0.25 * s, y + dy * 0.25 * s, z], 0.4 * s, 0.0)
    prim(1, 0, [x, y, z], [x + dx * 0.5 * s, y + dy * 0.5 * s, z], 0.05 * s, 0.0, (240, 246, 250), 0.7, g)
    prim(0, 0, [x - dx * 0.02 * s, y - dy * 0.02 * s, z], [0.08 * s] * 3, 0, 0.02 * s, (236, 60, 56), 0.6, g)
    h = max(0.02, 0.45 * level)
    prim(1, 2, [x, y, z + 0.04 * s], [x + dx * h * s, y + dy * h * s, z + 0.04 * s], 0.032 * s, 0.006 * s, (236, 60, 56), 0.6, g)
