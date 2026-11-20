# Q 版熊蜂 bumblebee()（动物打工人 No.04，2026-11-20）——东方熊蜂 Bombus impatiens 的黏土办公室版
#  - 直立 Q 版：大头（黑头壳 + 雄蜂黄脸，蜂后/工蜂黑脸）、黄色毛茸茸胸部、黑色腹部 + 第一节黄环（impatiens 的特征）
#  - 白眼球 + 黑瞳 + 高光（2026-11-16 面部清晰度规则：五官泥条加粗、k 很小、对比强）；返回 face / face_r 供 engine/clay_face.py 超采样
#  - role: "male"（黄脸、长触角、工牌）、"queen"（大一号、黑脸、小金冠）、"worker"（小一号、黑脸）
#  - 表情 look / happy / wow / worry / proud / sleepy / shy / angry；gaze=(gx, gy) 瞳孔方向；mouth_open 0..1
#  - 动作：lie 0..1 = 孵卵姿势（身体前倾趴平、腹部贴住育雏团，头仍抬起看镜头）；wing 翅膀扇动 -1..1（飞行时由调用方给快速交替值）
#          arms=(左, 右) 抬手 -1..1；squash 压扁；pitch 额外点头；badge 工牌（返回卡片中心，2D 字由调用方按投影贴）
#  - 只用球 / 胶囊 / 轴对齐椭球（近球形）图元：小角度 yaw 不变形；翅膀是贴在背后的扁椭球，yaw 取 ±0.6 以内
#  - lod=True：远景小蜂（无高光、无工牌、少腿），用于一个画面里十几只蜂
# 返回 dict：face / face_r / top / head / thorax / abdomen / badge / badge_n / hand_l / hand_r
import os, sys, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "engine"), _ROOT, os.environ.get("CLAY_ENGINE_DIR")):
    if _p and os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
from clay_proto import prim, group

YEL = (252, 196, 52); YEL_D = (232, 168, 36); BLK = (50, 42, 48); BLK_L = (74, 64, 70)
FACE_M = (255, 214, 84)                       # 雄蜂黄脸（impatiens 雄蜂唇基/颜面黄毛）
EYEW = (255, 255, 252); INKC = (18, 12, 16); MOUTHC = (120, 30, 40); BLUSHC = (255, 120, 120)
WINGC = (200, 228, 252); LEGC = (44, 36, 42); GOLD = (255, 200, 40); BADGE = (250, 250, 244); LANY = (230, 70, 60)

def bumblebee(x, z, s=1.0, yaw=0.0, expr="look", y=0.0, role="male", lie=0.0, wing=0.0, arms=(0.0, 0.0),
              squash=0.0, pitch=0.0, gaze=(0.0, 0.0), mouth_open=0.0, badge=True, lod=False, hp=None, blush=True):
    if s < 0.02: return None
    if role == "queen": s *= 1.25
    elif role == "worker": s *= 0.86
    cy, sy = math.cos(yaw), math.sin(yaw)
    PIV = 0.70                                        # 身体前倾的支点（胸部高度：趴下时腹部向后平伸）
    a_b = lie * 1.15 + pitch * 0.4                    # 身体前倾角
    a_h = (pitch if hp is None else hp) - lie * 0.3   # 头的点头角（趴下时头抬起看镜头）
    def rot(px, py, pz, a, cyv, czv):
        ca, sa = math.cos(a), math.sin(a)
        dy, dz = py - cyv, pz - czv
        return px, cyv + dy * ca - dz * sa, czv + dy * sa + dz * ca
    def W(px, py, pz):                                # 局部 → 世界（压扁 + yaw + 缩放）
        py = py * (1 - squash); px = px * (1 + squash * 0.5); pz = pz * (1 + squash * 0.3)
        px, py, pz = px * s, py * s, pz * s
        return [x + px * cy + pz * sy, y + py, z - px * sy + pz * cy]
    def TB(px, py, pz):                               # 身体（绕支点前倾，趴下时整体略降低）
        px, py, pz = rot(px, py, pz, a_b, PIV, 0.0)
        return W(px, py - lie * 0.22, pz)
    _nx, _ny, _nz = rot(0, 0.98, 0.0, a_b, PIV, 0.0); _ny -= lie * 0.22     # 颈部（身体前倾后的局部位置）
    def TH(px, py, pz):                               # 头：绕颈部点头，再跟着颈部平移
        px, py, pz = rot(px, py, pz, a_h, 0.98, 0.0)
        return W(px + _nx, py + _ny - 0.98, pz + _nz)
    def E(T_, g, mode, c, r, k, col, gl=0.3, infl=0.0):
        rr = r if isinstance(r, (list, tuple)) else (r, r, r)
        prim(0, mode, T_(*c), [rr[0] * s, rr[1] * s, rr[2] * s], infl * s, k * s, col, gl, g)
    def C(T_, g, mode, a, b, r, k, col, gl=0.3):
        prim(1, mode, T_(*a), T_(*b), r * s, k * s, col, gl, g)
    gb = group(TB(0, 0.62, 0.0), 0.95 * s, 0.0)
    # ---- 腹部：黑 + 第一节黄环（涂色带）
    E(TB, gb, 0, (0, 0.36, -0.06), (0.34, 0.37, 0.35), 0.0, BLK, 0.25)
    E(TB, gb, 2, (0, 0.58, -0.04), (0.36, 0.11, 0.37), 0.04, YEL, 0.25, 0.006)
    E(TB, gb, 2, (0, 0.1, -0.08), (0.12, 0.08, 0.12), 0.03, BLK_L, 0.3, 0.004)        # 腹尖略亮
    # ---- 胸部：黄色绒毛球（胸中央有一块黑斑，impatiens 特征）
    E(TB, gb, 0, (0, 0.78, 0.0), (0.27, 0.22, 0.26), 0.06, YEL, 0.2)
    if not lod: E(TB, gb, 2, (0, 0.86, -0.12), (0.12, 0.09, 0.12), 0.03, BLK_L, 0.2, 0.004)
    # ---- 腿：前腿=手（抬手 arms）、中腿短、后腿=脚
    al, ar = arms
    hand = {}
    for sx, aa in ((-1, al), (1, ar)):
        sh = (sx * 0.22, 0.80, 0.10)
        hx, hy, hz = sx * (0.40 + 0.06 * aa), 0.60 + 0.42 * aa, 0.20 + 0.04 * (1 - abs(aa))
        el = (sx * 0.36, 0.72 + 0.12 * aa, 0.16)
        C(TB, gb, 0, sh, el, 0.05, 0.02, LEGC, 0.3)
        C(TB, gb, 0, el, (hx, hy, hz), 0.045, 0.02, LEGC, 0.3)
        E(TB, gb, 0, (hx, hy, hz), 0.06, 0.02, YEL_D, 0.3)                            # 黄色小“手套”（花粉刷）
        hand["hand_l" if sx < 0 else "hand_r"] = TB(hx, hy, hz)
        if not lod:
            C(TB, gb, 0, (sx * 0.24, 0.66, 0.02), (sx * 0.42, 0.46, 0.06), 0.035, 0.02, LEGC, 0.3)   # 中腿
        C(TB, gb, 0, (sx * 0.15, 0.14, 0.06), (sx * 0.19, 0.02, 0.12), 0.045, 0.02, LEGC, 0.3)      # 后腿
        E(TB, gb, 0, (sx * 0.19, 0.02, 0.16), (0.07, 0.04, 0.09), 0.02, LEGC, 0.3)
    # ---- 工牌：挂绳 + 白卡（挂在胸前偏右，不挡嘴）
    bc = None
    if badge and not lod and role == "male":
        for sx in (-1, 1):
            C(TB, gb, 2, (sx * 0.16, 0.95, 0.1), (0.08 + sx * 0.03, 0.72, 0.25), 0.022, 0.008, LANY, 0.3)
        prim(2, 0, TB(0.1, 0.66, 0.27), [0.11 * s, 0.085 * s, 0.014 * s], 0.012 * s, 0.0, BADGE, 0.35, gb)
        prim(2, 2, TB(0.1, 0.725, 0.285), [0.11 * s, 0.022 * s, 0.01 * s], 0.0, 0.004 * s, LANY, 0.35, gb)
        bc = TB(0.1, 0.65, 0.29)
    # ---- 翅膀：背后两对扁椭球（站立时竖在背后，趴下时平铺在腹上）
    gw = group(TB(0, 0.9, -0.25) if lie < 0.5 else W(0, 0.78, -0.42), 0.75 * s, 0.0)
    fl = wing
    for sx in (-1, 1):
        for j, (wx, wy, rx, ry) in enumerate(((0.30, 1.02, 0.17, 0.25), (0.22, 0.86, 0.12, 0.17))):
            yy = wy + 0.08 * fl * (1 if j == 0 else 0.6)
            rxx = rx * (1 - 0.25 * abs(fl)); ryy = ry * (1 - 0.35 * abs(fl))
            ryy2 = ryy * (1 - lie) + 0.03 * lie; rz = 0.03 * (1 - lie) + ryy * lie
            pu = TB(sx * (wx + 0.04 * fl), yy, -0.24)                                  # 站立：竖在背后
            pl = W(sx * (0.17 + 0.05 * j), 0.80 - 0.04 * j + 0.03 * fl, -0.36 - 0.16 * j)  # 趴下：平铺在腹部上方
            c = [pu[i] * (1 - lie) + pl[i] * lie for i in range(3)]
            prim(0, 0, c, [rxx * s, ryy2 * s, rz * s], 0, 0.0, WINGC, 0.95, gw)
    # ---- 头
    gh = group(TH(0, 1.1, 0.04), 0.48 * s, 0.0)
    E(TH, gh, 0, (0, 1.1, 0.02), (0.31, 0.29, 0.29), 0.0, BLK, 0.3)
    if role == "male":
        E(TH, gh, 2, (0, 1.03, 0.24), (0.21, 0.17, 0.12), 0.03, FACE_M, 0.3, 0.008)
    # 触角（雄蜂更长），末端小球
    al_ = 1.25 if role == "male" else 1.0
    for sx in (-1, 1):
        r0 = (sx * 0.09, 1.34, 0.14); r1 = (sx * 0.17, 1.34 + 0.16 * al_, 0.2); r2 = (sx * (0.17 + 0.14 * al_), 1.34 + 0.15 * al_, 0.28)
        C(TH, gh, 0, r0, r1, 0.024, 0.01, BLK, 0.3); C(TH, gh, 0, r1, r2, 0.022, 0.01, BLK, 0.3)
        E(TH, gh, 0, r2, 0.04, 0.01, BLK_L, 0.4)
    if role == "queen":   # 小金冠
        for k in range(5):
            a = -0.9 + k * 0.45
            E(TH, gh, 0, (math.sin(a) * 0.15, 1.47 + 0.04 * (k % 2), 0.06 + math.cos(a) * 0.05), 0.05, 0.02, GOLD, 0.8)
        C(TH, gh, 0, (-0.17, 1.40, 0.06), (0.17, 1.40, 0.06), 0.05, 0.03, GOLD, 0.8)
    ex0, ey0, ez0 = 0.13, 1.14, 0.25
    gx, gy = gaze
    if lod:
        for sx in (-1, 1): E(TH, gh, 0, (sx * ex0, ey0, ez0 + 0.02), 0.07, 0.002, INKC, 1.0)
    else:
        for sx in (-1, 1):
            ex = sx * ex0
            if blush: E(TH, gh, 2, (sx * 0.2, 1.0, 0.25), (0.055, 0.04, 0.04), 0.012, BLUSHC, 0.2, 0.003)
            if expr in ("happy", "proud"):         # ^ ^ 眯眼：粗泥条
                C(TH, gh, 0, (ex - 0.055, ey0 - 0.015, ez0 + 0.03), (ex, ey0 + 0.03, ez0 + 0.05), 0.024, 0.0015, INKC, 0.8)
                C(TH, gh, 0, (ex, ey0 + 0.03, ez0 + 0.05), (ex + 0.055, ey0 - 0.015, ez0 + 0.03), 0.024, 0.0015, INKC, 0.8)
                continue
            if expr == "sleepy":                   # 一条下弧线
                C(TH, gh, 0, (ex - 0.055, ey0 + 0.01, ez0 + 0.04), (ex, ey0 - 0.02, ez0 + 0.05), 0.022, 0.0015, INKC, 0.8)
                C(TH, gh, 0, (ex, ey0 - 0.02, ez0 + 0.05), (ex + 0.055, ey0 + 0.01, ez0 + 0.04), 0.022, 0.0015, INKC, 0.8)
                continue
            er = 0.112 if expr == "wow" else 0.1
            E(TH, gh, 0, (ex, ey0, ez0), er, 0.0015, EYEW, 0.55)
            pr_ = 0.045 if expr == "wow" else 0.062
            px_, py_ = ex + 0.032 * gx, ey0 + 0.028 * gy - (0.01 if expr in ("worry", "shy") else 0.0)
            E(TH, gh, 0, (px_, py_, ez0 + er * 0.8), pr_, 0.001, INKC, 1.0)
            E(TH, gh, 2, (px_ - 0.022, py_ + 0.026, ez0 + er * 0.8 + pr_ * 0.8), 0.02, 0.002, (255, 255, 255), 1.0, 0.003)
            if expr == "worry" or expr == "shy":
                C(TH, gh, 0, (ex + sx * 0.07, ey0 + 0.13, ez0 + 0.04), (ex - sx * 0.05, ey0 + 0.165, ez0 + 0.06), 0.026, 0.006, INKC, 0.4)
            if expr == "angry":
                C(TH, gh, 0, (ex + sx * 0.07, ey0 + 0.17, ez0 + 0.03), (ex - sx * 0.05, ey0 + 0.12, ez0 + 0.08), 0.028, 0.006, INKC, 0.4)
        my, mz = 0.98, 0.288                             # 嘴必须贴在头壳表面（z≈0.28）上刻，否则刻不进去
        mo = max(mouth_open, 1.0 if expr == "wow" else 0.0)
        if mo > 0.3:                                # O 形 / 张嘴：刻洞
            E(TH, gh, 1, (0, my - 0.015, mz), (0.05 + 0.025 * mo, 0.04 + 0.03 * mo, 0.06), 0.006, MOUTHC)
        elif expr in ("worry", "angry"):
            C(TH, gh, 1, (-0.06, my - 0.025, mz - 0.01), (0.0, my + 0.005, mz + 0.005), 0.026, 0.005, MOUTHC)
            C(TH, gh, 1, (0.0, my + 0.005, mz + 0.005), (0.06, my - 0.025, mz - 0.01), 0.026, 0.005, MOUTHC)
        elif expr == "sleepy":
            E(TH, gh, 1, (0, my - 0.01, mz), (0.03, 0.022, 0.05), 0.005, MOUTHC)
        elif expr == "proud":                       # 大笑 D 形 + 白牙
            prim(0, 1, TH(0, my - 0.01, mz), [0.075 * s, 0.045 * s, 0.06 * s], 0.0, 0.004 * s, MOUTHC, 0.3, gh)
            C(TH, gh, 0, (-0.05, my + 0.022, mz + 0.012), (0.05, my + 0.022, mz + 0.012), 0.011, 0.003, (255, 250, 240), 0.5)
        else:                                       # 微笑
            C(TH, gh, 1, (-0.065, my + 0.012, mz - 0.015), (0.0, my - 0.025, mz + 0.008), 0.027, 0.005, MOUTHC)
            C(TH, gh, 1, (0.0, my - 0.025, mz + 0.008), (0.065, my + 0.012, mz - 0.015), 0.027, 0.005, MOUTHC)
    out = {"face": TH(0, 1.08, 0.26), "face_r": 0.31 * s, "top": TH(0, 1.62, 0.1), "head": TH(0, 1.1, 0.02),
           "thorax": TB(0, 0.78, 0.0), "abdomen": TB(0, 0.36, -0.06), "badge": bc, "badge_n": TB(0.1, 0.65, 1.0), "s": s}
    out.update(hand)
    return out
