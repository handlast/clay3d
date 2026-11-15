# Q 版阿萨姆猕猴 monkey2：clay_proto.monkey 的扩展版（不改原接口）
#  - y 偏移、整体缩放入场（s→0 时不生成）、squash 压扁
#  - 头部转向 hyaw / 歪头 hroll；表情 happy / angry / wow / look / worry(八字眉)
#  - 手臂姿势 POSE（rest/up/wave/groom/fist/out）、任意局部坐标、to_local() 把手伸到世界坐标点、armlerp() 姿势过渡
#  - badge=True 戴工牌（挂绳涂色 + 薄卡片）
# 返回 dict：head / top / badge / chest 的世界坐标，供 2D 层投影贴字
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # 仓库根（engine/ characters/ props/ scenes/ 的上一级）
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):   # CLAY_ENGINE_DIR 优先（最后插到最前）
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
import clay_proto as cp
from clay_proto import prim, group, FUR, FURD, FACE, BLUSH, INK, WHT, MOUTH

BADGE_C = (250, 250, 244); LANY = (70, 130, 220); GOLDC = (255, 196, 60)
POSE = {   # 手的局部坐标（sx 镜像）
    "rest":  (0.20, 0.17, 0.20),
    "up":    (0.5, 0.92, 0.22),
    "wave":  (0.40, 0.95, 0.18),
    "groom": (0.10, 0.52, 0.48),
    "fist":  (0.22, 0.62, 0.34),
    "out":   (0.42, 0.40, 0.22),
}
def _hand(p, sx):
    if isinstance(p, str): p = POSE[p]
    if len(p) == 4: return (p[0], p[1], p[2])          # 已是局部坐标（由世界坐标换算）
    return (sx * p[0], p[1], p[2])
def to_local(x, y, z, s, yaw, w):
    """世界坐标 -> monkey2 局部坐标（用于手伸到别的猴子身上）"""
    dx, dy, dz = w[0] - x, w[1] - y, w[2] - z
    cy, sy = math.cos(yaw), math.sin(yaw)
    px = dx * cy - dz * sy; pz = dx * sy + dz * cy
    return (px / s, dy / s, pz / s, 1)

def monkey2(x, z, s=1.0, yaw=0.0, expr="look", y=0.0, hyaw=0.0, hroll=0.0, armL="rest", armR="rest", badge=False, squash=0.0):
    """返回 dict：头中心、工牌中心（世界坐标），供 2D 层投影贴字"""
    if s < 0.02: return None
    cy, sy = math.cos(yaw), math.sin(yaw)
    hy = 0.88
    ch, sh_ = math.cos(hyaw), math.sin(hyaw); cr, sr = math.cos(hroll), math.sin(hroll)
    def T(px, py, pz, head=False):
        if head:   # 头部绕自身中心先歪头(roll, 绕 z)再转头(yaw, 绕 y)
            qx, qy = px * cr - (py - hy) * sr, px * sr + (py - hy) * cr + hy
            px, py = qx, qy
            px, pz = px * ch + pz * sh_, -px * sh_ + pz * ch
        py = py * (1 - squash) if not head else py - (hy * squash)
        px, py, pz = px * s, py * s, pz * s
        return [x + px * cy + pz * sy, y + py, z - px * sy + pz * cy]
    def E(g, mode, c, r, k, col, gl=0.25, inflate=0.0, head=False):
        prim(0, mode, T(*c, head=head), [r[0] * s, r[1] * s, r[2] * s], inflate * s, k * s, col, gl, g)
    def C(g, mode, a, b, r, k, col, gl=0.25, head=False):
        prim(1, mode, T(*a, head=head), T(*b, head=head), r * s, k * s, col, gl, g)
    body = group(T(0, 0.62, 0.05), 0.9 * s, 0.0)
    E(body, 0, (0, 0.32, 0), (0.30, 0.34, 0.26), 0.0, FUR)
    E(body, 2, (0, 0.28, 0.2), (0.17, 0.2, 0.12), 0.012, FACE, inflate=0.004)
    for sx in (-1, 1):
        E(body, 0, (sx * 0.15, 0.05, 0.16), (0.11, 0.06, 0.13), 0.04, FACE)              # 脚
        arm = armL if sx < 0 else armR
        hx, hy_, hz = _hand(arm, sx)
        C(body, 0, (sx * 0.25, 0.45, 0.02), (hx, hy_, hz), 0.07, 0.03, FUR)
        E(body, 0, (hx, hy_, hz), (0.065, 0.06, 0.06), 0.02, FACE)                      # 手掌
    if badge:   # 工牌：挂绳(涂色) + 卡片(薄圆角盒，轻微融入)
        for sx in (-1, 1):
            C(body, 2, (sx * 0.14, 0.6, 0.17), (sx * 0.035, 0.43, 0.262), 0.018, 0.008, LANY)
        bc = T(0, 0.36, 0.272)
        prim(2, 0, bc, [0.085 * s, 0.1 * s, 0.012 * s], 0.02 * s, 0.006 * s, BADGE_C, 0.3, body)
        prim(2, 2, T(0, 0.425, 0.285), [0.085 * s, 0.03 * s, 0.02 * s], 0.0, 0.004 * s, LANY, 0.3, body)
    # ---- 头（与 clay_proto.monkey 相同造型，可转头）
    E(body, 0, (0, hy, 0), (0.36, 0.33, 0.31), 0.03, FUR, head=True)
    E(body, 0, (0, hy + 0.27, -0.04), (0.16, 0.07, 0.14), 0.03, FURD, head=True)
    for sx in (-1, 1):
        E(body, 0, (sx * 0.36, hy + 0.03, -0.03), (0.1, 0.1, 0.06), 0.02, FURD, head=True)
        E(body, 1, (sx * 0.40, hy + 0.03, 0.03), (0.055, 0.06, 0.04), 0.012, FACE, head=True)
    for sx in (-1, 1):
        E(body, 2, (sx * 0.1, hy + 0.04, 0.26), (0.15, 0.15, 0.12), 0.008, FACE, inflate=0.006, head=True)
    E(body, 2, (0, hy - 0.1, 0.25), (0.24, 0.13, 0.12), 0.008, FACE, inflate=0.006, head=True)
    E(body, 0, (0, hy - 0.11, 0.25), (0.14, 0.085, 0.08), 0.03, FACE, head=True)
    for sx in (-1, 1):
        E(body, 2, (sx * 0.19, hy - 0.08, 0.26), (0.05, 0.035, 0.05), 0.012, BLUSH, head=True)
        ex, ey, ez = sx * 0.1, hy + 0.04, 0.29
        if expr == "happy":
            C(body, 0, (ex - 0.045, ey - 0.01, ez + 0.012), (ex, ey + 0.02, ez + 0.02), 0.016, 0.003, INK, gl=0.8, head=True)
            C(body, 0, (ex, ey + 0.02, ez + 0.02), (ex + 0.045, ey - 0.01, ez + 0.012), 0.016, 0.003, INK, gl=0.8, head=True)
        else:
            rr = 0.06 if expr == "wow" else 0.05
            E(body, 0, (ex, ey, ez), (rr, rr * 1.12, 0.045), 0.004, INK, gl=1.0, head=True)
        if expr == "angry":
            C(body, 0, (ex + sx * 0.06, ey + 0.1, ez + 0.0), (ex - sx * 0.04, ey + 0.065, ez + 0.02), 0.018, 0.008, FURD, head=True)
        if expr == "worry":   # 八字眉
            C(body, 0, (ex + sx * 0.06, ey + 0.065, ez + 0.0), (ex - sx * 0.04, ey + 0.1, ez + 0.02), 0.016, 0.008, FURD, head=True)
    for sx in (-1, 1):
        E(body, 1, (sx * 0.022, hy - 0.085, 0.335), (0.011, 0.009, 0.02), 0.004, INK, head=True)
    if expr in ("angry", "wow", "worry"):
        E(body, 1, (0, hy - 0.16, 0.33), (0.055 if expr == "angry" else 0.03, 0.03, 0.04), 0.006, MOUTH, head=True)
    else:
        C(body, 1, (-0.045, hy - 0.14, 0.32), (0.0, hy - 0.162, 0.33), 0.008, 0.004, MOUTH, head=True)
        C(body, 1, (0.0, hy - 0.162, 0.33), (0.045, hy - 0.14, 0.32), 0.008, 0.004, MOUTH, head=True)
    return {"head": T(0, hy + 0.05, 0.0, head=True), "top": T(0, hy + 0.42, 0.0, head=True), "badge": T(0, 0.36, 0.3), "chest": T(0, 0.45, 0.1)}


def armlerp(a, b, k, sx=1):
    """两种手臂姿势之间平滑过渡（smoothstep），避免定格里手臂一拍跳变；返回可直接传给 armL/armR 的元组"""
    pa, pb = POSE[a], POSE[b]; k = max(0.0, min(1.0, k)); k = k * k * (3 - 2 * k)
    return tuple(pa[i] + (pb[i] - pa[i]) * k for i in range(3))
