# Q 版小丑鱼 clownfish()：大头圆身、三道白环（涂色球串成环，转身也贴着身体）、大眼（白眼球 + 黑瞳 + 高光点）
#  - 只用球/胶囊图元（与朝向无关），所以 yaw/pitch 任意转都不变形
#  - 表情 look / happy / wow / angry / worry / fierce(皱眉咧嘴，“加班守家”)；look 可给瞳孔方向 gaze=(gx, gy)
#  - 动作：tail 尾巴摆动(-1..1)、flap 胸鳍扇动(-1..1)、squash 压扁、y 上下浮动、pitch 抬头低头、tie 领带（打工人）
#  - 面部清晰度（2026-11-16 规则）：眼/嘴/眉的泥条加粗、明暗对比强；返回 face 中心和半径，供 engine/clay_face.py 做脸部超采样
# 返回 dict：head / face / top / tail / mouth 世界坐标 + face_r（脸部半径，世界单位）
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
from clay_proto import prim, group

ORANGE = (255, 122, 34); ORANGE_D = (232, 92, 22); FINC = (255, 150, 60)
WHITE_B = (252, 250, 242); EYEW = (255, 255, 252); INKC = (20, 14, 16); MOUTHC = (110, 24, 36)
BLUSHC = (255, 96, 110); BROW = (120, 44, 14); TIEC = (40, 70, 160); TIEK = (30, 52, 128)

def clownfish(x, z, s=1.0, yaw=0.0, expr="look", y=0.0, tail=0.0, flap=0.0, squash=0.0, pitch=0.0,
              gaze=(0.0, 0.0), tie=False, mouth_open=0.0, helmet=0.0,
              body=ORANGE, fin=FINC, bands=True):
    if s < 0.02: return None
    cy, sy = math.cos(yaw), math.sin(yaw); cp_, sp_ = math.cos(pitch), math.sin(pitch)
    C0 = 0.55                                     # 身体中心高度（局部）
    def T(px, py, pz):
        py = C0 + (py - C0) * (1 - squash); px = px * (1 + squash * 0.5); pz = pz * (1 + squash * 0.3)
        qy, qz = C0 + (py - C0) * cp_ - pz * sp_, (py - C0) * sp_ + pz * cp_        # 抬头/低头（绕 x）
        px, py, pz = px * s, qy * s, qz * s
        return [x + px * cy + pz * sy, y + py, z - px * sy + pz * cy]
    def S(g, mode, c, r, k, col, gl=0.3, infl=0.0):
        prim(0, mode, T(*c), [r * s, r * s, r * s], infl * s, k * s, col, gl, g)
    def Cp(g, mode, a, b, r, k, col, gl=0.3):
        prim(1, mode, T(*a), T(*b), r * s, k * s, col, gl, g)
    g = group(T(0, C0, -0.1), 0.95 * s, 0.0)
    # ---- 身体：大圆头 + 收窄的尾柄
    S(g, 0, (0, C0, 0.04), 0.36, 0.0, body)
    Cp(g, 0, (0, C0 - 0.01, -0.06), (0, C0 + 0.01, -0.32), 0.25, 0.08, body)
    Cp(g, 0, (0, C0, -0.3), (0, C0, -0.5), 0.13, 0.08, body)
    # ---- 三道白环：沿身体截面一圈涂色小球（软边）
    def band(zc, rad, w, n=12):
        for i in range(n):
            a = 2 * math.pi * i / n
            S(g, 2, (math.cos(a) * rad, C0 + math.sin(a) * rad, zc), w, 0.012, WHITE_B, 0.3, 0.006)
    if bands: band(-0.02, 0.352, 0.105, 16)              # 眼后头环（正面看是两侧白边）
    if bands: band(-0.29, 0.245, 0.09, 12)               # 身体中环
    if bands: band(-0.50, 0.125, 0.06, 8)                # 尾柄环
    # ---- 鳍：背鳍、胸鳍(扇动)、尾鳍(摆动)、腹鳍
    Cp(g, 0, (0, C0 + 0.33, 0.0), (0, C0 + 0.40, -0.18), 0.05, 0.05, fin)
    Cp(g, 0, (0, C0 + 0.40, -0.18), (0, C0 + 0.30, -0.40), 0.045, 0.05, fin)
    for sx in (-1, 1):
        f = flap * sx
        Cp(g, 0, (sx * 0.30, C0 - 0.08, 0.02), (sx * (0.47 + 0.05 * f), C0 - 0.12 + 0.10 * flap, -0.10), 0.055, 0.03, fin)
        Cp(g, 0, (sx * 0.12, C0 - 0.32, -0.05), (sx * 0.17, C0 - 0.44, -0.16), 0.04, 0.03, fin)
    tw = 0.16 * tail
    for dy, zz in ((0.20, -0.80), (0.0, -0.76), (-0.20, -0.80)):
        Cp(g, 0, (0, C0, -0.52), (tw, C0 + dy, zz), 0.075, 0.05, fin)
    if bands: S(g, 2, (tw * 1.05, C0, -0.84), 0.12, 0.02, WHITE_B, 0.3, 0.004)        # 尾鳍白边
    # ---- 脸（全部加粗：眼球 0.115、瞳孔 0.07、嘴 0.028、眉 0.032）
    ex0, ey0, ez0 = 0.15, C0 + 0.08, 0.30
    gx, gy = gaze
    for sx in (-1, 1):
        ex = sx * ex0
        S(g, 2, (sx * 0.22, C0 - 0.08, 0.27), 0.06, 0.015, BLUSHC, 0.2, 0.004)          # 腮红
        if expr == "happy":     # ^ ^ 眯眼：两段粗泥条
            Cp(g, 0, (ex - 0.06, ey0 - 0.015, ez0 + 0.025), (ex, ey0 + 0.03, ez0 + 0.05), 0.026, 0.0015, INKC, 0.8)
            Cp(g, 0, (ex, ey0 + 0.03, ez0 + 0.05), (ex + 0.06, ey0 - 0.015, ez0 + 0.025), 0.026, 0.0015, INKC, 0.8)
            continue
        er = 0.125 if expr == "wow" else 0.115
        S(g, 0, (ex, ey0, ez0), er, 0.0015, EYEW, 0.55)                                   # 白眼球（k 很小：眼白边缘清楚，不和身体颜色糊在一起）
        pr_ = 0.05 if expr == "wow" else 0.072
        px_, py_ = ex + 0.035 * gx, ey0 + 0.03 * gy - (0.008 if expr in ("angry", "fierce") else 0.0)
        S(g, 0, (px_, py_, ez0 + er * 0.78), pr_, 0.001, INKC, 1.0)                        # 黑瞳（亮面）
        S(g, 2, (px_ - 0.025, py_ + 0.03, ez0 + er * 0.78 + pr_ * 0.8), 0.022, 0.002, (255, 255, 255), 1.0, 0.003)   # 高光点
        if expr in ("angry", "fierce"):     # 怒眉：外高内低
            Cp(g, 0, (ex + sx * 0.08, ey0 + 0.16, ez0 + 0.02), (ex - sx * 0.06, ey0 + 0.105, ez0 + 0.09), 0.032, 0.008, BROW, 0.4)
        if expr == "worry":                 # 八字眉：外低内高
            Cp(g, 0, (ex + sx * 0.08, ey0 + 0.12, ez0 + 0.04), (ex - sx * 0.06, ey0 + 0.17, ez0 + 0.06), 0.03, 0.008, BROW, 0.4)
    my, mz = C0 - 0.13, 0.372
    if expr == "wow" or mouth_open > 0.3:           # O 形嘴：刻洞
        o = 0.055 + 0.03 * max(mouth_open, 1.0 if expr == "wow" else 0.0)
        S(g, 1, (0, my - 0.02, mz + 0.005), o, 0.008, MOUTHC)
    elif expr == "angry":                            # 咬牙：宽扁刻槽
        Cp(g, 1, (-0.075, my, mz - 0.01), (0.075, my, mz - 0.01), 0.035, 0.006, MOUTHC)
    elif expr == "worry":                            # 下撇嘴
        Cp(g, 1, (-0.065, my - 0.03, mz - 0.015), (0.0, my + 0.005, mz + 0.0), 0.03, 0.005, MOUTHC)
        Cp(g, 1, (0.0, my + 0.005, mz + 0.0), (0.065, my - 0.03, mz - 0.015), 0.03, 0.005, MOUTHC)
    elif expr == "fierce":                           # 咧嘴笑（有干劲）：宽 U 形，下沿加深
        prim(0, 1, T(0, my - 0.012, mz + 0.0), [0.085 * s, 0.05 * s, 0.06 * s], 0.0, 0.004 * s, MOUTHC, 0.3, g)   # 张大的笑嘴（D 形）
        Cp(g, 0, (-0.06, my + 0.03, mz + 0.012), (0.06, my + 0.03, mz + 0.012), 0.012, 0.004, (255, 250, 240), 0.5)   # 上牙一条白边
    else:                                            # 微笑
        Cp(g, 1, (-0.075, my + 0.015, mz - 0.02), (0.0, my - 0.025, mz + 0.005), 0.03, 0.005, MOUTHC)
        Cp(g, 1, (0.0, my - 0.025, mz + 0.005), (0.075, my + 0.015, mz - 0.02), 0.03, 0.005, MOUTHC)
    if tie:   # 工牌：身体侧面挂一张小白卡（涂色挂绳 + 薄卡片），不放在嘴下面（会像舌头）
        for sx in (-1, 1):
            Cp(g, 2, (sx * 0.2, C0 + 0.27, -0.12), (sx * 0.33, C0 - 0.12, -0.16), 0.02, 0.008, TIEC, 0.3)
        S(g, 0, (0.34, C0 - 0.17, -0.17), 0.075, 0.01, (250, 250, 244), 0.3)
    if helmet > 0.02:   # 黄色安全帽（“加班”梗）：单独一组，按 helmet 0..1 缩放渐入
        hs = s * helmet
        gh = group(T(0, C0 + 0.36, 0.02), 0.32 * hs, 0.0)
        hc = T(0, C0 + 0.30 + 0.06 * helmet, 0.02)
        prim(0, 0, hc, [0.25 * hs, 0.17 * hs, 0.25 * hs], 0, 0.0, (255, 206, 40), 0.5, gh)
        prim(0, 0, T(0, C0 + 0.30 + 0.06 * helmet - 0.01, 0.10), [0.3 * hs, 0.035 * hs, 0.3 * hs], 0, 0.03 * hs, (255, 196, 30), 0.5, gh)
        prim(1, 0, T(0, C0 + 0.43 + 0.06 * helmet, -0.12), T(0, C0 + 0.48 + 0.06 * helmet, 0.12), 0.03 * hs, 0.03 * hs, (255, 220, 80), 0.5, gh)
    return {"head": T(0, C0 + 0.05, 0.05), "face": T(0, C0 + 0.0, 0.30), "top": T(0, C0 + 0.48, 0.0),
            "tail": T(tw, C0, -0.78), "mouth": T(0, my, mz + 0.03), "face_r": 0.30 * s}
