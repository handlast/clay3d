# 可移植到「PIL 逐帧 + cam(t)」的 11 个动画手法

> 研究对象：ManimCommunity/manim、3b1b/manim（manimgl）、motion-canvas/motion-canvas、remotion-dev/remotion。
> 下文每条引用的 URL 都是本次实际打开并读过源码的页面（raw 源文件）。
> 配套代码：`/workspace/work/research/anim_kit.py`（第 1–4、7、8 条的核心函数；文中第 5–11 条的代码块也已在沙盒里用 numpy + Pillow 跑过冒烟测试，能出图）。
> 约定：画布 1080×1920、30fps；`cam(t)` 返回 `(z, cx, cy)`，和现有 `film.py` 的顺序一致；世界坐标 → 屏幕坐标公式为 `sx = (x - cx) * z + 540`，`sy = (y - cy) * z + 960`。

## 先看结论：现在的画面为什么"静"，哪几条最该先上

| 观感问题 | 对应手法 | 优先级 |
|---|---|---|
| 角色居中不动、镜头单一 | ② 帧矩形相机 + 自动构图、③ 跟随焦点、⑪ 分层视差 | 先做 |
| 转场靠硬切 | ⑤ match cut 延续物体、⑥ 擦除 / 滑动 / 穿越式转场、④ morph | 先做 |
| 元素一起冒出来，没有节奏 | ⑦ LaggedStart 错峰入场、⑧ 描线绘制 | 其次 |
| 重点不突出 | ⑨ 聚焦遮罩、Indicate、Circumscribe | 其次 |
| 数字干巴巴 | ⑩ 数值滚动与里程表 | 按需 |
| 所有运动的手感 | ① 缓动、弹簧、多关键帧工具箱 | 地基，其他条都要用 |

幅度约束（用户的硬规则）在每条里都写进了默认参数：
- 镜头抖动：大重音约 8px，卡点约 1.5px。
- 冲击变焦 ≤4%，卡点变焦约 1.5%。
- 每个镜头的慢推 / 慢拉建议 ≤6–8%。
- 转场里的缩放 ≤6%。
- 全程不用黑色描边，也不用偏移投影字。高亮一律靠同色系提亮、发光（glow）和压暗背景。

---

## ① 缓动、弹簧、多关键帧插值工具箱（地基）

**解决的问题**：线性或单一 ease 的运动显得机械。"弹一下"的入场如果靠手调，每次都不一样。一段运动要分几拍时，只能写一串 if。

**源项目怎么做**
- Manim 的 `rate_functions`：
  - `smooth` 是归一化的 sigmoid（inflection=10）。
  - `there_and_back` 走 0→1→0，Indicate 的"来回"就是它。
  - `running_start` 先往回拉再冲出去。
  - `squish_rate_func(func, a, b)` 把一条曲线压进 [a, b] 时间窗，窗外保持 0 或 1。
  - URL：https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/utils/rate_functions.py
- Motion Canvas 的 `timingFunctions.ts`：一整套 easings.net 曲线（`easeInOutCubic`、`createEaseOutBack(s)` 等），可调参数做成工厂函数。
  - URL：https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/packages/core/src/tweening/timingFunctions.ts
- Remotion 的 `spring()` / `springCalculation()`：
  - 用真实的质量-弹簧-阻尼模型逐帧推进：`zeta = damping / (2*sqrt(k*m))`，`omega0 = sqrt(k/m)`。欠阻尼和临界阻尼各有一个闭式解。
  - 默认参数是 `damping=10, mass=1, stiffness=100`，算下来 ζ=0.5，会过冲约 15%。
  - `overshootClamping` 可以把超过 1 的部分截掉。
  - URL：https://raw.githubusercontent.com/remotion-dev/remotion/main/packages/core/src/spring/spring-utils.ts 和 https://raw.githubusercontent.com/remotion-dev/remotion/main/packages/core/src/spring/index.ts
- Remotion 的 `interpolate(input, inputRange, outputRange, {easing, extrapolateLeft/Right})`：多关键帧、每段各自的 easing、两端可以 `clamp`。
  - URL：https://raw.githubusercontent.com/remotion-dev/remotion/main/packages/core/src/interpolate.ts

**PIL 移植**：全部写成 t 的纯函数，不带状态，所以多进程分段渲染时每个进程算出来的结果都一样。

```python
import math
def clamp01(x): return 0.0 if x < 0 else 1.0 if x > 1 else x
def lerp(a, b, u): return a + (b - a) * u
def ease_io_cubic(t):
    t = clamp01(t); return 4*t**3 if t < .5 else 1 - (-2*t + 2)**3 / 2
def squish(f, a, b):                       # Manim squish_rate_func
    return lambda t: f(0.0 if t < a else 1.0 if t > b else (t - a) / (b - a))
def spring(t, stiffness=100, damping=10, mass=1, clamp=False):
    """Remotion spring 的闭式解，0→1，t 单位为秒"""
    if t <= 0: return 0.0
    w0 = math.sqrt(stiffness / mass); z = damping / (2 * math.sqrt(stiffness * mass))
    if z < 1:
        w1 = w0 * math.sqrt(1 - z*z)
        x = 1 - math.exp(-z*w0*t) * (math.cos(w1*t) + z*w0/w1 * math.sin(w1*t))
    else:
        x = 1 - math.exp(-w0*t) * (1 + w0*t)          # 临界阻尼：不过冲
    return min(x, 1.0) if clamp else x
def kf(t, times, values, easings=None):
    """Remotion interpolate：多关键帧，两端 clamp，values 可以是元组"""
    if t <= times[0]: return values[0]
    if t >= times[-1]: return values[-1]
    i = max(j for j in range(len(times) - 1) if times[j] <= t)
    u = (easings[i] if easings else ease_io_cubic)((t - times[i]) / (times[i+1] - times[i]))
    a, b = values[i], values[i+1]
    return tuple(lerp(x, y, u) for x, y in zip(a, b)) if isinstance(a, tuple) else lerp(a, b, u)
```

**用法建议**
- 角色和道具的 pop 入场：`spring(t-t0, 180, 14)`，ζ≈0.52，有弹性。
- 相机：一律用 ζ≥1（`damping ≥ 2*sqrt(stiffness)`），不过冲，满足"镜头幅度小"。
- 想停一下再走（hold）：在 `kf` 里连写两个相同的值。
- 实测：默认弹簧在第 10 帧达到峰值 1.155，第 30 帧回到 1.002。

---

## ② 帧矩形相机：推、拉、平移 + 自动构图（auto_zoom）

**解决的问题**：角色永远在画面正中、构图不变。想让两个物体同框时，只能手算 zoom 和中心。

**源项目怎么做**
- Manim 的 `MovingCamera`：
  - 相机就是场景里的一个矩形 `frame`。移动或缩放这个矩形就等于推拉摇移，`frame.animate.move_to(...).set(width=...)` 可以直接当动画播放。
  - `auto_zoom(mobjects, margin)` 先求所有目标的包围盒，再按"宽或高谁先顶满"决定 `set(width=…)` 还是 `set(height=…)`。
  - URL：https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/camera/moving_camera.py
- 3b1b manimgl 的 `CameraFrame.get_view_matrix()`：
  - 视图矩阵 = 平移(-center) → 旋转 → 除以 `scale = frame_height / FRAME_HEIGHT`，相机本身也只是一个可插值的 Mobject。
  - `reorient(..., center=, height=)` 一次设好中心和取景高度。
  - URL：https://raw.githubusercontent.com/3b1b/manim/master/manimlib/camera/camera_frame.py
- Motion Canvas 的 `Camera`：
  - `zoom` 内部存成 `scale = 1/zoom`。`tweenZoom` 插值的是 1/zoom（取景框大小），不是 zoom 本身。
  - `centerOn(node, duration, easeInOutCubic)`、`reset()` 默认都用 easeInOutCubic。
  - URL：https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/packages/2d/src/lib/components/Camera.ts

**PIL 移植**
1. `cam(t)` 改成"镜头关键帧表 + kf 插值"，然后在上面叠加现有的冲击变焦和小抖动。
2. 构图用 `auto_frame()`：给它主体和标签的 bbox，它算出 `(z, cx, cy)`，并且只用抖音安全区（x 180–900，y 120–1440）。
3. 变焦在 log 空间插值（`exp(lerp(log z0, log z1, u))`），推和拉的速度感会对称。MC 选择对 1/zoom 插值，出发点相同。
4. 现在的 `film.py` 是对整帧做 `resize(box=...)` 裁切，而且把中心夹在画布内。所以只能放大（z≥1），平移也撞不出画布边缘。两种改法：
   - 世界层多渲染 overscan 边距，比如每边多 120px。
   - 或者让场景函数直接用 `to_screen()` 在世界坐标里绘制。矢量重绘不会因放大而发虚，推近特写时更清晰。

```python
SAFE = (180, 120, 900, 1440)                   # 抖音安全区
def auto_frame(boxes, margin=80, zmin=1.0, zmax=1.08):
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
    sw, sh = SAFE[2] - SAFE[0], SAFE[3] - SAFE[1]
    z = min(sw / (x1 - x0 + 2*margin), sh / (y1 - y0 + 2*margin))   # 谁先顶满听谁的
    z = max(zmin, min(zmax, z))                                       # 变焦幅度上限
    scx, scy = (SAFE[0] + SAFE[2]) / 2, (SAFE[1] + SAFE[3]) / 2
    return (z, (x0 + x1)/2 - (scx - 540)/z, (y0 + y1)/2 - (scy - 960)/z)

SHOTS = [(0.0, (1.00, 540, 960)),
         (2.4, (1.05, 540, 900)),                        # 慢推 5%
         (5.0, auto_frame([HERO_BOX, LABEL_BOX])),       # 主角和标签同框
         (8.0, (1.00, 600, 960))]                        # 轻拉回 + 右移 60px
def cam(t):
    ts = [s[0] for s in SHOTS]; vs = [s[1] for s in SHOTS]
    z, cx, cy = kf(t, ts, vs)
    z *= 1 + 0.015 * pulse(t, HITS, 7) + 0.04 * pulse(t, [HOOK_HIT, BIG2], 3)
    sx, sy = shake(t, 8 * pulse(t, [HOOK_HIT, BIG2], 5) + 1.5 * pulse(t, HITS, 8), 40)
    return z, cx + sx, cy + sy
```

---

## ③ 跟随焦点：死区 + 临界阻尼的"摄影师"相机

**解决的问题**：主体移动时相机要么不动，主体跑出画面；要么死死锁定，背景整片平移很晕。

**源项目怎么做**
- Motion Canvas 的 `Camera.centerOn(node)`：先取节点的世界坐标，再补间相机位置。
- `followCurve(curve, duration, timing)`：让相机沿一条曲线按 timing 走，`getPointAtPercentage(timing(v))`。
  - URL：https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/packages/2d/src/lib/components/Camera.ts
- 平滑用 Remotion `springCalculation` 的物理模型，取 ζ=1（临界阻尼）：最快回到目标，而且不过冲。
  - URL：https://raw.githubusercontent.com/remotion-dev/remotion/main/packages/core/src/spring/spring-utils.ts

**PIL 移植**
- 带状态的弹簧会破坏并行渲染的确定性。解法是在模块导入时一次性逐帧积分出整条相机轨迹，存成数组，`cam(t)` 只查表。每个进程算出的轨迹完全一样。
- 加一个"死区"：主体在中心 ±60px 内相机不动，这正是"幅度小"的关键。

```python
import numpy as np
def build_follow_track(target_fn, dur, stiffness=40.0, dead=60.0, fps=30):
    n = int(dur * fps) + 1; w0 = np.sqrt(stiffness); dt = 1 / fps
    pos = np.array(target_fn(0.0), float); vel = np.zeros(2); out = np.zeros((n, 2))
    for i in range(n):
        tgt = np.array(target_fn(i * dt), float); d = tgt - pos; dist = np.linalg.norm(d)
        goal = pos if dist < dead else tgt - d / dist * dead       # 死区：只追出界的部分
        vel += (w0*w0 * (goal - pos) - 2*w0*vel) * dt              # zeta = 1
        pos += vel * dt; out[i] = pos
    return out

FOLLOW = build_follow_track(lambda t: hero_pos(t + 0.15), DUR)   # +0.15s 前瞻
def cam(t):
    cx, cy = FOLLOW[min(int(round(t * 30)), len(FOLLOW) - 1)]
    return 1.03, cx, cy
```

**参数提示**：`stiffness` 30–60 跟得比较稳。前瞻 0.1–0.2 秒能让主体前方留出空间（lead room），画面更像有人在掌镜。

---

## ④ 形状 Morph：点对应插值（Transform 的核心）

**解决的问题**：A 物体变成 B 物体时只能淡入淡出或硬切，因果关系断掉。例如"种子 → 果实"、"细胞 → 圆点图标"。

**源项目怎么做**
- Manim 的 `Transform.begin()` 会先调用 `mobject.align_data(target_copy)`，再在每帧调用 `interpolate(start, target, alpha, path_func)`。
  - URL：https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/animation/transform.py
- `VMobject.align_points()` 让两边的子路径数量相同，每条子路径的点数也相同：
  - 短的一方用 `insert_n_curves_to_point_list` → `bezier_remap` 均匀细分曲线来补点。
  - 子路径少的一方补"退化成一个点的空路径"，所以多出来的部件会从一个点长出来或者缩成一个点。
  - 颜色用 `align_rgbas` 和 `interpolate_color` 一起插值。
  - URL：https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/mobject/types/vectorized_mobject.py
- `path_along_arc(arc_angle)`：每个点沿圆弧走而不是走直线。圆心 = 起点和终点的中点 + `cross(axis, v/2)/tan(arc/2)`，`ClockwiseTransform` 就是 `path_arc=-π`。
  - URL：https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/utils/paths.py

**PIL 移植**：用多边形（几十到几百个点）代替贝塞尔曲线，步骤如下：
1. 两个形状都按弧长重采样成 N 点。
2. 统一环绕方向（看有向面积的符号）。
3. 找一个循环偏移 k，让对应点的距离平方和最小，避免形状"拧麻花"。
4. 插值，可选走弧线路径。

```python
def resample(poly, n):
    p = np.asarray(poly, float); q = np.vstack([p, p[:1]])
    seg = np.linalg.norm(np.diff(q, axis=0), axis=1); cum = np.r_[0, np.cumsum(seg)]
    s = np.linspace(0, cum[-1], n, endpoint=False); i = np.searchsorted(cum, s, 'right') - 1
    u = ((s - cum[i]) / np.maximum(seg[i], 1e-9))[:, None]
    return q[i] * (1 - u) + q[i + 1] * u
def area(p): return 0.5 * np.sum(p[:,0]*np.roll(p[:,1],-1) - np.roll(p[:,0],-1)*p[:,1])
def align_shapes(a, b, n=180):
    A, B = resample(a, n), resample(b, n)
    if np.sign(area(A)) != np.sign(area(B)): B = B[::-1]
    k = min(range(n), key=lambda k: np.sum((A - np.roll(B, -k, 0))**2))
    return A, np.roll(B, -k, 0)
def morph(A, B, u, arc=0.0):                    # arc≠0 时等价于 Manim path_along_arc
    if abs(arc) < 1e-3: return A + (B - A) * u
    v = B - A; c = A + v/2 + np.stack([-v[:,1], v[:,0]], 1) / 2 / np.tan(arc/2)
    ca, sa = np.cos(arc*u), np.sin(arc*u); r = A - c
    return c + np.stack([r[:,0]*ca - r[:,1]*sa, r[:,0]*sa + r[:,1]*ca], 1)
# 每帧：pts = morph(A, B, smooth(u), arc=0.6); d.polygon([tuple(p) for p in pts], fill=lerp_rgb(c0, c1, u))
```

**细节**
- 高光、眼睛这类内部部件单独配对插值，参考 `align_points` 的子路径对齐。没有配对的部件"缩成一点"，配合 alpha 淡出。
- 多部件对应可以按极角排序后一一配对。
- 1.5 倍超采样画多边形，边缘就足够顺滑。

---

## ⑤ Match cut / 跨镜头延续同一物体（ReplacementTransform、TransformMatchingShapes）

**解决的问题**：换场景时观众的视线断了。要让同一个主角（或同一个数字、图标）在镜头 A 的末尾"飞"到镜头 B 里的位置和尺寸，只有背景在换。这是 3b1b 视频里最典型的"连续感"来源。

**源项目怎么做**
- `ReplacementTransform(a, b)`：结束后场景里用 b 替换 a（`replace_mobject_with_target_in_scene=True`）。
- `FadeTransform`：起点和终点各放一份，彼此 `ghost_to` 对方的位置和尺寸，然后交叉淡化。适合形状差别大、硬 morph 很难看的情况。
  - URL：https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/animation/transform.py
- `TransformMatchingShapes` 和 `TransformMatchingAbstractBase`：给每个子部件算一个 key（形状哈希，或 tex 字符串）。key 相同的部件做 `Transform`；源里独有的部件 `FadeOut(target_position=…)`，朝目标方向淡出；目标里独有的部件 `FadeIn` 进来。`key_map` 可以手动指定配对。
  - URL：https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/animation/transform_matching_parts.py

**PIL 移植**
1. 每个镜头函数接收一个参数 `draw_hero=False`，可以不画主角。
2. 每个镜头另外导出主角在屏幕坐标下的状态（已经过该镜头自己的 cam）。
3. 转场窗口里：背景用⑥的擦除或交叉过渡；主角画在最上层，在两个状态之间插值，形状不同时再叠加④的 morph。
4. 部件级匹配（字幕关键词、图标组件）按 key 处理：相同的部件移动，不同的部件淡出淡入。

```python
def hero_state_A(t): return dict(x=540, y=1150, s=1.00, rot=0,  col=(255, 120, 80))
def hero_state_B(t): return dict(x=380, y=640,  s=0.55, rot=-8, col=(255, 150, 90))
def match_cut(t, t0, dur, shotA, shotB, draw_hero):
    u = (t - t0) / dur
    a, b = shotA(t, draw_hero=False), shotB(t, draw_hero=False)    # 两边背景都渲染
    img = wipe(a, b, squish(ease_io_cubic, .15, .85)(u))           # 见第 ⑥ 条
    k = spring(t - t0, 120, 22)                                    # zeta≈1，不过冲
    sa, sb = hero_state_A(t0), hero_state_B(t0 + dur)
    st = {key: (tuple(int(lerp(p, q, k)) for p, q in zip(sa[key], sb[key]))
                if key == "col" else lerp(sa[key], sb[key], k)) for key in sa}
    draw_hero(img, **st)                                          # 主角在顶层，不被切断
    return img

def match_parts(src, dst, u):          # src/dst: {key: (x, y)}，部件级 TransformMatching
    for key in src.keys() & dst.keys():
        yield key, tuple(lerp(p, q, u) for p, q in zip(src[key], dst[key])), 1.0
    for key in src.keys() - dst.keys(): yield key, src[key], 1 - u        # 只在源里：淡出
    for key in dst.keys() - src.keys(): yield key, dst[key], u            # 只在目标里：淡入
```

**提示**
- 主角在过渡中可以轻微放大 3–5% 再落位（`there_and_back` 叠一点），会更有"被镜头接住"的感觉。
- 文字关键词（例如"生长素"）在字幕和知识卡之间用 `match_parts` 飞过去，比重新出现更容易跟住。

---

## ⑥ 非硬切的场景转场：擦除、滑动、"穿越"式小推进

**解决的问题**：硬切加白闪只能用一两次，全片都这样会显得生硬。

**源项目怎么做**
- Motion Canvas 的 `zoomInTransition(area, duration=0.6)`：
  - 新场景从 `area` 的大小放大到全屏，透明度在进度 0.1–0.5 之间从 0 升到 1。
  - 旧场景同时放大，透明度在 0.5–0.9 之间从 1 降到 0。
  - timing 用 `easeInOutCubic(v*v)`：前段更慢，后段更冲。
  - URL：https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/packages/core/src/transitions/zoomInTransition.ts
- `slideTransition(direction, 0.6)`：旧场景平移到 `-2*offset`，新场景从 `+2*offset` 移到 0。
  - URL：https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/packages/core/src/transitions/slideTransition.ts
  - 目录：https://api.github.com/repos/motion-canvas/motion-canvas/contents/packages/core/src/transitions
- Remotion 的 `wipe()`：
  - 用 CSS `clipPath: polygon(...)` 按进度裁切，8 个方向，对角方向用三角形，所以 `p*2`。
  - 进入的场景用 `makePolygonIn`，离开的场景用 `makePolygonOut`。
  - URL：https://raw.githubusercontent.com/remotion-dev/remotion/main/packages/transitions/src/presentations/wipe.tsx

**PIL 移植**
- 转场窗口里两个镜头各渲染一帧，用 L 蒙版合成。
- 擦除边缘用一条亮色光带（主题色、glow），不用黑边。
- "穿越式"转场照 MC 的透明度时间窗来做，但缩放压到 ≤6%，满足变焦小的要求。

```python
from PIL import Image, ImageDraw, ImageFilter
def wipe(a, b, p, direction="from-left", soft=24, edge_col=(255, 220, 120)):
    m = Image.new("L", a.size, 0); d = ImageDraw.Draw(m); w, h = a.size
    if direction == "from-left":   d.rectangle((0, 0, p * w, h), fill=255)
    if direction == "from-bottom": d.rectangle((0, h - p * h, w, h), fill=255)
    if direction == "from-top-left": d.polygon([(0, 0), (2*p*w, 0), (0, 2*p*h)], fill=255)  # Remotion 对角三角形
    m = m.filter(ImageFilter.GaussianBlur(soft))
    out = Image.composite(b, a, m)
    if 0 < p < 1 and direction == "from-left":                        # 亮色光带，不是黑边
        ImageDraw.Draw(out, "RGBA").rectangle((p*w - 6, 0, p*w + 6, h), fill=edge_col + (150,))
    return out

def zoom_through(a, b, v, s=0.06):          # MC zoomInTransition，缩放被限制在 6%
    v2 = ease_io_cubic(v * v)
    def scaled(img, k):
        cw, ch = img.width / k, img.height / k; x0, y0 = (img.width - cw) / 2, (img.height - ch) / 2
        return img.resize(img.size, Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    A = scaled(a, 1 + s * v2); B = scaled(b, 1 + s * (1 - v2))
    ab = clamp01((v - 0.1) / 0.4)                                    # 新场景 0.1–0.5 淡入
    return Image.blend(A, B, ab)

def slide(a, b, v, dy=1920):                # MC slideTransition（竖屏：向上推）
    k = ease_io_cubic(v); out = Image.new("RGB", a.size)
    out.paste(a, (0, int(-dy * k))); out.paste(b, (0, int(dy * (1 - k)))); return out
```

**提示**
- 模糊蒙版很耗时：在 1/4 分辨率上画蒙版和模糊，再 `resize` 回原尺寸，速度能快 10 倍以上。
- 转场只有 0.4–0.6 秒，双倍渲染的成本可以接受。

---

## ⑦ LaggedStart：错峰入场（涟漪、多米诺）

**解决的问题**：一组元素（种子、数据点、图标、字）同时冒出来，没有节奏，眼睛也不知道先看哪里。

**源项目怎么做**
- Manim 的 `AnimationGroup.build_animations_with_timings()`：
  - 第 i 个动画的开始时间 = 前面各个 `run_time * lag_ratio` 的累加。
  - 组的总时长固定后，每个子动画的时长会等比缩放（"This does not influence the total runtime"）。
  - `LaggedStart` 的默认 `lag_ratio=0.05`，`Succession` 等于 lag 1.0。
  - `LaggedStartMap` 的例子是对一组点做 `there_and_back` 变色，形成黄色涟漪。
  - URL：https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/animation/composition.py
- Motion Canvas 的 `sequence(delay, ...tasks)`：每隔固定的 delay 启动下一个任务，不等上一个结束，最后 `join` 全部任务。
  - URL：https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/packages/core/src/flow/sequence.ts

**PIL 移植**

```python
def lagged(t, n, run_time, lag=0.15):
    """返回 n 个局部进度 0..1；总时长固定为 run_time（Manim 语义）"""
    d = run_time / (1 + lag * (n - 1))                 # 单个子动画时长
    return [clamp01((t - i * lag * d) / d) for i in range(n)]

def seq_start(i, t0, delay=0.08): return t0 + i * delay # MC sequence 语义：固定间隔

# 用法：种子按到中心的距离排序 → 从中心向外的涟漪
order = sorted(range(len(seeds)), key=lambda i: dist(seeds[i], CENTER))
us = lagged(t - T["seeds"], len(seeds), 1.2, lag=0.12)
for rank, i in enumerate(order):
    u = us[rank]
    if u <= 0: continue
    s = spring(u * 0.8, 200, 16)                       # 每颗弹出来
    draw_seed(d, seeds[i], scale=s, alpha=clamp01(u * 3))
```

**提示**
- 每一颗的出现可以绑一个轻音效（pop、木鱼），和"卡点别处处砸重音"的规则一致。music.py 读同一份 `lagged` 的开始时间表就能对齐。
- 字幕逐字出现时可以参考 Manim `Write` 的默认值：`lag_ratio = min(4/字数, 0.2)`。

---

## ⑧ 描线绘制：Create / DrawBorderThenFill / Write / ShowPassingFlash

**解决的问题**：图示（箭头、路径、示意线、坐标轴、圆圈）"啪"一下就在那里，缺少"正在讲解"的过程感。

**源项目怎么做**
- Manim 的 `Create`：`_get_bounds(alpha) = (0, alpha)`，再交给 `pointwise_become_partial(start, a, b)` 截出曲线的 [a, b] 段。
- `DrawBorderThenFill`：
  - 用 `integer_interpolate(0, 2, alpha)` 把时间分成两半。前半段画轮廓（只有描边、没有填充的副本按比例显示），后半段从轮廓插值到填充好的成品。
  - rate 函数是 `double_smooth`。
- `Write` 继承 DrawBorderThenFill，按子部件数量自动设 `run_time`（少于 15 个部件为 1 秒，否则 2 秒）和 `lag_ratio=min(4/n, 0.2)`。
  - URL：https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/animation/creation.py
- `ShowPassingFlash`：`upper = alpha*(1+tw)`，`lower = upper - tw`，只显示一条在路径上"流过"的光段。
  - URL：https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/animation/indication.py
- 截取的实现在 `VMobject.pointwise_become_partial`，按曲线索引加残差截取贝塞尔段。
  - URL：https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/mobject/types/vectorized_mobject.py
- Motion Canvas 的 `Curve.start` / `Curve.end`（0..1 的百分比）：按弧长裁切路径，用来做"线条出现在屏幕上"，箭头会跟着末端走。
  - URL：https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/packages/2d/src/lib/components/Curve.ts

**PIL 移植**
- 线条：按弧长截取折线，末端可以加箭头和一个亮点。
- 填充形状：前半段用同色系的浅色描边描出轮廓，后半段填充色淡入，描边同时淡出。最终画面没有任何描边，符合"禁止黑色描边"。
- 文字：Pillow 拿不到字形轮廓，改用"软边擦除"模拟书写，每个字一个蒙版，再用 lagged 错开。

```python
def partial(points, a, b):                      # = pointwise_become_partial / Curve.start,end
    p = np.asarray(points, float); seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    cum = np.r_[0, np.cumsum(seg)]; L = cum[-1]
    def at(s):
        i = min(np.searchsorted(cum, s, 'right') - 1, len(seg) - 1)
        u = (s - cum[i]) / max(seg[i], 1e-9); return tuple(p[i] * (1 - u) + p[i+1] * u)
    return [at(a*L)] + [tuple(q) for q, c in zip(p, cum) if a*L < c < b*L] + [at(b*L)]
def passing_bounds(u, tw=0.3):                  # ShowPassingFlash
    up = u * (1 + tw); return max(up - tw, 0.0), min(up, 1.0)

def draw_border_then_fill(d, poly, u, fill, light):     # light = 提亮的同色，不用黑色
    closed = list(poly) + [poly[0]]
    if u < 0.5:
        d.line(partial(closed, 0, smooth(u * 2)), fill=light, width=8, joint="curve")
    else:
        k = smooth(u * 2 - 1)
        d.polygon(poly, fill=fill + (int(255 * k),))
        d.line(closed, fill=light + (int(255 * (1 - k)),), width=8, joint="curve")

def write_text(img, x, y, text, font, col, u, lag=None):  # 逐字软擦除
    n = len(text); lag = lag or min(4 / n, 0.2)
    for i, (ch, uu) in enumerate(zip(text, lagged(u, n, 1.0, lag))):
        if uu <= 0: continue
        cx = x + font.getlength(text[:i]); w = int(font.getlength(ch)) + 4
        m = Image.new("L", (w, font.size + 20), 0)
        ImageDraw.Draw(m).text((0, 0), ch, font=font, fill=255)
        ramp = Image.new("L", m.size, 0)                        # 从左到右推进的软边擦除
        ImageDraw.Draw(ramp).rectangle((0, 0, int(uu * (w + 12)) - 6, m.size[1]), fill=255)
        ramp = ramp.filter(ImageFilter.GaussianBlur(4))
        img.paste(col, (int(cx), y), ImageChops.multiply(m, ramp))  # from PIL import ImageChops
```

---

## ⑨ 聚焦遮罩与高亮：FocusOn / Indicate / Circumscribe / Flash

**解决的问题**：画面元素一多，观众不知道这句字幕说的是哪个东西。

**源项目怎么做**（全部在 `indication.py`）
- `FocusOn(point, opacity=0.2, color=GREY)`：一个半径约等于整个画面的圆点，`Transform` 收缩到目标点，透明度从 0 升到 0.2。效果是"聚光灯收拢"。
- `Indicate(scale_factor=1.2, color=YELLOW, rate_func=there_and_back)`：放大并变色，再回到原样。
- `Circumscribe(shape=Rectangle|Circle, time_width=0.3, buff=SMALL_BUFF)`：在外框（`SurroundingRectangle`，或 `Circle.surround`）上跑一段 `ShowPassingFlash`。也可以用 `fade_in` / `fade_out` 改成 `Create` 加 `FadeOut`。
- `Flash(num_lines=12, flash_radius, line_length)`：12 条放射短线，每条各跑一段 ShowPassingFlash。
- `Wiggle`：缩放用 `there_and_back`，旋转用 `wiggle(alpha, n)`。
- URL：https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/animation/indication.py

**PIL 移植**
- 聚焦遮罩：整屏铺一层带背景色调的深色（不是纯黑），挖一个羽化圆洞，洞的半径用弹簧收拢。
- Indicate：放大 6–8%，颜色提亮，叠一层 glow。
- Circumscribe：在圆角外框路径上跑 `passing_bounds` 光段，画成两层（宽而淡的 glow + 细而亮的芯）。全程不用黑边。

```python
def spotlight(img, cx, cy, r, dim=0.55, tint=(14, 18, 34), feather=40, q=4):
    w, h = img.size[0] // q, img.size[1] // q                  # 低分辨率做蒙版，提速
    m = Image.new("L", (w, h), int(255 * dim))
    ImageDraw.Draw(m).ellipse(((cx - r)/q, (cy - r)/q, (cx + r)/q, (cy + r)/q), fill=0)
    m = m.filter(ImageFilter.GaussianBlur(feather / q)).resize(img.size, Image.BILINEAR)
    return Image.composite(Image.new("RGB", img.size, tint), img, m)

def focus_on(img, t, t0, cx, cy, r_end=180):                   # FocusOn：大圆收拢
    k = spring(t - t0, 90, 19)                                 # 临界阻尼附近
    return spotlight(img, cx, cy, lerp(1400, r_end, k), dim=0.55 * clamp01((t - t0) / 0.3))

def indicate_scale(t, t0, dur=0.6, amt=0.07):                  # Indicate：there_and_back
    return 1 + amt * there_and_back((t - t0) / dur)

def circumscribe(d, box, t, t0, dur=0.9, col=(255, 225, 120), buff=24):
    x0, y0, x1, y1 = box[0]-buff, box[1]-buff, box[2]+buff, box[3]+buff
    path = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    a, b = passing_bounds(clamp01((t - t0) / dur), tw=0.35)
    if b <= a: return
    seg = partial(path, a, b)
    d.line(seg, fill=col + (70,), width=26, joint="curve")    # 外层 glow
    d.line(seg, fill=col + (255,), width=8, joint="curve")    # 亮芯
```

**提示**：聚焦遮罩里的 `tint` 用当前场景背景色压暗约 60%，不要用纯黑，否则和"禁止黑色描边"的审美冲突。字幕层要画在遮罩之上（UI 层，见⑪）。

---

## ⑩ 数值滚动计数（ChangingDecimal）与里程表式滚轮

**解决的问题**：数据段只是把数字摆在屏幕上，没有动作。按工作流规则，每个数字都要配画面动作。

**源项目怎么做**
- Manim 的 `ChangingDecimal(decimal_mob, number_update_func)`：每帧 `set_value(number_update_func(rate_func(alpha)))`。
- `ChangeDecimalToValue` 就是对起止值做线性插值，再套 rate_func。
- URL：https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/animation/numbers.py
- Remotion 的 `interpolate(..., {easing, extrapolateRight:'clamp'})` 也可以直接拿来驱动数值；`posterize` 选项能按步长量化输入，适合"跳着数"。
  - URL：https://raw.githubusercontent.com/remotion-dev/remotion/main/packages/core/src/interpolate.ts

**PIL 移植**
- 等宽数字格：每一位都在宽度为"最宽数字"的格子里居中绘制。Noto Sans SC 的数字不是等宽的，不这样做数字跳动时整行会左右抖。
- 里程表：个位随小数部分连续滚动；更高位只在低位接近进位时（本位小数部分 >0.9）才滚。每一位画在自己的裁切格里。
- 跨数量级（例如 1→100 万）在 log 空间插值，每个量级停留的时间相同。这是我的补充，不是源项目的 API。

```python
def count_value(t, t0, dur, v0, v1, log=False):
    u = 1 - (1 - clamp01((t - t0) / dur)) ** 3                 # ease-out：先快后稳
    return math.exp(lerp(math.log(v0), math.log(v1), u)) if log else lerp(v0, v1, u)

def odometer(img, x, y, value, ndig, font, col, pad=10):
    cw = int(max(font.getlength(c) for c in "0123456789")) + pad; ch = font.size + 2 * pad
    for k in range(ndig):                                      # k=0 是个位
        f = (value / 10**k) % 1.0
        dgt = int(value // 10**k) % 10
        roll = f if k == 0 else clamp01(f * 10 - 9)            # 高位只在进位前一刻滚
        roll = smooth(roll)
        cell = Image.new("L", (cw, ch), 0); dc = ImageDraw.Draw(cell)
        for j, num in ((0, dgt), (1, (dgt + 1) % 10)):
            yy = pad + (j - roll) * ch
            dc.text((cw / 2, yy + font.size / 2), str(num), font=font, fill=255, anchor="mm")
        img.paste(col, (int(x + (ndig - 1 - k) * cw), int(y)), cell)
```

**提示**：整数变化的那一帧（`int(v)` 和上一帧不同）可以导出给 music.py 放一个 tick 音效，数字和声音就自然卡在一起。数字本身不加阴影或描边，靠字号、颜色和背后的柔光圆来突出。

---

## ⑪ 分层视差 + 固定 UI 层（fix_in_frame）

**解决的问题**：相机平移时整张画面像一张纸在滑，没有纵深。另外，字幕和品牌胶囊不应该跟着相机动。

**源项目怎么做**
- 3b1b manimgl 的 `Mobject.fix_in_frame()`：给物体打上 `is_fixed_in_frame=1.0` 的 uniform，渲染时这类物体不经过 `CameraFrame` 的视图矩阵，固定在屏幕上。3b1b 用它做标题和公式这类 HUD。
  - URL：https://raw.githubusercontent.com/3b1b/manim/master/manimlib/mobject/mobject.py
  - 视图矩阵：https://raw.githubusercontent.com/3b1b/manim/master/manimlib/camera/camera_frame.py
- Motion Canvas 的 `Camera`：`transformContext()` 对 `scene` 子树套上相机矩阵的逆变换，相机之外的节点不受影响。`Camera.Stage` 用 `clip` 的 Rect 包住相机。
  - URL：https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/packages/2d/src/lib/components/Camera.ts
- 说明：这几个项目都没有现成的"视差" API。下面的深度系数 k 是在"相机矩阵只作用于部分图层"这一机制上的推广，属于我的移植设计。

**PIL 移植**：每层有一个深度系数 k：
- 远景 0.2–0.5，主体 1.0，前景 1.2–1.4，UI 为 0，等价于 fix_in_frame。
- 每层的相机 = 把全局相机的位移和变焦按 k 缩小或放大。
- 静态的远景层渲染一次后缓存（overscan 尺寸），每帧只需要裁切和缩放，比现在逐帧重画背景还省时间。

```python
LAYERS = [("sky", 0.25), ("hills", 0.55), ("world", 1.0), ("leaves_fg", 1.3)]
OVR = 160                                                   # 每边 overscan
def layer_cam(cam, k):
    z, cx, cy = cam
    return 1 + (z - 1) * k, 540 + (cx - 540) * k, 960 + (cy - 960) * k

def crop_layer(layer, cam):                                 # layer: RGBA，尺寸 (W+2*OVR, H+2*OVR)
    z, cx, cy = cam; cw, ch = 1080 / z, 1920 / z
    x0 = cx + OVR - cw / 2; y0 = cy + OVR - ch / 2
    return layer.resize((1080, 1920), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

def frame(t):
    c = cam(t); img = Image.new("RGB", (1080, 1920), BG)
    for name, k in LAYERS:
        lay = CACHE.get(name) or render_layer(name, t)       # 静态层缓存
        piece = crop_layer(lay, layer_cam(c, k))
        img.paste(piece, (0, 0), piece)                      # RGB 底图 + RGBA 层的 alpha 当蒙版
    d = D(img); brand(t, d); subs(t, d)                      # k=0：UI 固定在屏幕上
    return img
```

**幅度提示**
- 相机水平平移 60px 时，远景（k=0.25）只动 15px，前景（k=1.3）动 78px。变化小但纵深明显，不需要加大镜头运动幅度。
- 前景层可以放半透明的叶子或颗粒，稍微虚化（预先模糊一次后缓存）。
- 冲击抖动只作用在 k≥1 的层上，远景基本不抖，观感更稳。

---

## 落地建议（和现有工作流对齐）

1. 把 `anim_kit.py` 的通用函数并进各作品的 `film.py` 公共区：
   - 缓动、spring、kf、lagged、partial、passing_bounds、resample / align_shapes / morph、auto_frame、build_follow_track。
   - 时间点一律从 `cues.py` 的 `T[key]`、`at(key, 拍)` 取，改字以后时间轴照样自适应。
2. `cam(t)` 拆成三层：
   - 镜头关键帧（②）或跟随轨迹（③）。
   - 现有的冲击变焦和小抖动，参数不变：8px / 1.5px，4% / 1.5%。
   - 每段的慢推，≤6%。
3. 硬切的分配：全片最多保留 2 处白闪（0 秒、BIG2）。其余换场：
   - 有共同主体的用 ⑤ match cut；
   - 换环境的用 ⑥ 擦除或滑动；
   - 进入微观层面的用 ⑥ zoom_through（≤6%）配合 ④ morph。
4. 每条字幕对应一个屏上动作：
   - 讲到哪个部件就 ⑨ Circumscribe 或聚焦；
   - 讲数据就 ⑩ 滚动；
   - 讲过程就 ⑧ 描线。
5. 渲染成本：
   - 模糊类效果（遮罩、擦除软边、glow）在 1/4 分辨率上做；
   - 视差静态层缓存；
   - 转场窗口双倍渲染只占 0.4–0.6 秒。
   - 2 核沙盒按 render.sh 的分段方式跑即可。

## 本次实际打开的源码页面

- Manim：
  - https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/camera/moving_camera.py
  - https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/animation/transform.py
  - https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/animation/transform_matching_parts.py
  - https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/animation/composition.py
  - https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/animation/creation.py
  - https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/animation/indication.py
  - https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/animation/numbers.py
  - https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/utils/rate_functions.py
  - https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/utils/paths.py
  - https://raw.githubusercontent.com/ManimCommunity/manim/main/manim/mobject/types/vectorized_mobject.py
- 3b1b manimgl：
  - https://raw.githubusercontent.com/3b1b/manim/master/manimlib/camera/camera_frame.py
  - https://raw.githubusercontent.com/3b1b/manim/master/manimlib/mobject/mobject.py
- Motion Canvas：
  - https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/packages/2d/src/lib/components/Camera.ts
  - https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/packages/2d/src/lib/components/Curve.ts
  - https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/packages/core/src/flow/sequence.ts
  - https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/packages/core/src/tweening/timingFunctions.ts
  - https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/packages/core/src/transitions/zoomInTransition.ts
  - https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/packages/core/src/transitions/slideTransition.ts
  - https://api.github.com/repos/motion-canvas/motion-canvas/contents/packages/core/src/transitions
- Remotion：
  - https://raw.githubusercontent.com/remotion-dev/remotion/main/packages/core/src/spring/index.ts
  - https://raw.githubusercontent.com/remotion-dev/remotion/main/packages/core/src/spring/spring-utils.ts
  - https://raw.githubusercontent.com/remotion-dev/remotion/main/packages/core/src/interpolate.ts
  - https://raw.githubusercontent.com/remotion-dev/remotion/main/packages/transitions/src/presentations/wipe.tsx

未覆盖的部分：
- 没有看 3b1b 的具体视频或其场景代码仓库（3b1b/videos），"3b1b 的做法"只依据 manimgl 引擎源码。
- 视差（⑪）、里程表（⑩）、match cut 的分层合成（⑤）是基于上述机制推出来的移植设计，源项目里没有同名 API。
