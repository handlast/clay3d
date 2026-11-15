# 黏土定格风 3D 动物：纯 CPU（numba）渲染研究

日期：2026-11-15 · 环境：aarch64、2 核、无 GPU、单条命令 ≤120 s · Python 3.12、numba 0.68

> 能直接跑的代码在 `<local>`（单 pass 原型，含全部 SDF/材质函数）和 `clay_fast.py`（4-pass 提速版 + 脏矩形）。下面的代码片段都摘自这两个文件，已实测能跑。`g_clay3d.py` 没有改动。

---

## 0. 结论与推荐路线

**推荐路线：继续用 numba SDF 光线步进，不换引擎。按 `clay_fast.py` 的 4-pass 结构重写渲染核心，以 720×1280 渲染、放大到 1080×1920 输出，动画 on twos。**

- **脸盘问题的根源**：粉色脸盘是一个单独的椭球，放在硬边小组里再用 `min` 和头拼起来，所以侧脸时会露出“贴片”的厚度和边缘。改法是把脸盘做成**头表面上的颜色区域**（“涂色”图元：只按 3D 距离改颜色，外加约 0.006 的软边微鼓）。颜色区域本身在 3D 空间里，所以头转多少度都贴着表面。眼珠用小 k 嵌进头里；嘴、鼻孔、眯眼和耳窝用 smooth subtraction **刻进去**，刻痕内壁换成深色。实测 yaw = −0.8 rad 的侧脸也很自然。
- **塑料感**：做了几处改动，一起去掉塑料感：wrap 漫反射，明暗交界带加一圈红晕（SSS 近似），往表面内侧探 SDF 估厚度来算透光，黏土用宽而弱的高光（指数约 6，配 Schlick 菲涅尔），眼珠单独用窄而亮的高光。另外在线性空间做光照，用 ACES 色调映射加 gamma 2.2，半影偏暖。
- **条纹**：原来的 `bump()` 是正弦叠加，所以一定会出条纹。换成整数哈希 value noise 做的 fbm（每个八度旋转并放大 2 倍），再加上随机分布的指纹按压点（凹坑 + 同心脊纹，像素过大时脊纹自动淡出）。细节**只在求法线时加入**，不参与光线步进，所以几乎不额外耗时，也不会让步进出问题。
- **速度**（都是实测，同一个三猴测试场景，2 线程）：

| 版本 | 540×960 | 720×1280 | 1080×1920 |
|---|---|---|---|
| 现有 g_clay3d.py（CLAYTEST，含后期） | 4.52 s | – | – |
| 新着色·单 pass（clay_proto.render，parallel） | 2.94 s | – | – |
| **新着色·4-pass（clay_fast）** | **1.63 s** | **2.91 s** | **6.98 s** |
| 4-pass，远景（相机拉远） | – | 1.61 s | – |
| 后期（ACES+景深+柔光+暗角，输出 1080×1920） | 0.5 s | – | 1.45 s |

估算一条 15 s 的视频：24 fps、on twos，共 180 次渲染。按 720×1280 计算，每帧约 2.9 s 渲染 + 0.5–1.4 s 后期，合计约 **12–13 分钟**；每条命令可以跑约 25 帧，大约 8 条命令跑完。

- **现成引擎的结论**：Blender 不在考虑之列。mitsuba3 能装，但只有 scalar 变体能用，而且需要网格；pyrender、moderngl 和 taichi 在这台机器上都用不了（见第 5 节）。都不如现在这条路线。

---

## 1. SDF 角色造型

### 1.1 smooth-min 带颜色混合（IQ）
IQ 归一化后的 quadratic smin：参数 k 正好等于融合区的最大加厚量（距离单位）。它同时返回第二个形状的混合权重，可以拿来混颜色或材质。
来源：https://iquilezles.org/articles/smin/ （“Mix factor”一节：`(a<b) ? vec2(a-s,m) : vec2(b-s,1.0-m)`）

```python
@nb.njit(fastmath=True, cache=True)
def smin_w(a, b, k):
    # IQ quadratic smin，返回 (值, b 的混合权重)
    if k <= 0.0:
        return (a, 0.0) if a < b else (b, 1.0)
    h = 1.0 - min(abs(a - b) / (4.0 * k), 1.0)
    w = h * h; m = w * 0.5; s = w * k
    if a < b:
        return a - s, m
    return b - s, 1.0 - m
# smooth subtraction（刻进去）: d = -smin(-d, di, k)   即 smax(d, -di)
```
IQ 指出 CD 族（quadratic/cubic 等）的 smin 永远**不会高估距离**，可以放心用于步进。
注意 smin 不满足结合律，图元的顺序会影响结果（同一篇文章的 Properties 一节）。

### 1.2 椭球距离：用 IQ 的梯度归一化版本
原代码用的是 `(|p/r|-1)*min(r)`，这个下界很松，会导致步数多、阴影过大、AO 不准。改用第二种做法：
来源：https://iquilezles.org/articles/ellipsoids/ 、https://iquilezles.org/articles/distfunctions/

```python
if t == 0:   # 椭球：k0*(k0-1)/k1
    px, py, pz = x - f[0], y - f[1], z - f[2]
    k0 = math.sqrt((px/f[3])**2 + (py/f[4])**2 + (pz/f[5])**2)
    k1 = math.sqrt((px/(f[3]*f[3]))**2 + (py/(f[4]*f[4]))**2 + (pz/(f[5]*f[5]))**2)
    return k0 * (k0 - 1.0) / (k1 + 1e-12)
```

### 1.3 五官贴合曲面、脸盘跟着头转
思路参考 IQ《Happy Jumping》（https://www.shadertoy.com/view/3lsSzf ）：评论区贴出的嘴部写法是 `d = sdEllipsoid(...); res.w = 0.3+0.7*clamp(d*150,0,1); res.x = smax(res.x, -d, 0.02)`，也就是用 smax 把嘴**刻**进头里，同时把这个距离当遮蔽系数。注意：该 shader 的许可证禁止复用它的代码，这里只借鉴思路。

每个图元多带一个 `mode` 字段：

| mode | 作用 | 用在 |
|---|---|---|
| 0 并（smin） | 几何 + 颜色按 smin 权重混合 | 身体、头、口鼻鼓包、眼珠（k≈0.004，“嵌入”） |
| 1 刻（smooth subtraction） | 挖凹，凹槽内壁换成刻痕颜色 | 嘴、鼻孔、眯眼弧线、耳窝 |
| 2 涂色 | **不改形状**，只按 3D 距离软边改颜色，并整体鼓起 `inflate`（取 max） | 脸盘、肚皮、腮红 |

```python
# map_full 内部（每组）：
for i in range(G0[gi], G1[gi]):
    mode = PI[i, 1]; di = sd_prim(PI[i, 0], PF[i], x, y, z); k = PF[i, 7]
    if mode == 0:
        d, w = smin_w(d, di, k)
    elif mode == 1:                                   # 刻：smax(d, -di)
        d2, w = smin_w(-d, di, k); d = -d2
        w = min(1.0, max(0.0, 1.0 - di / (2.0*k + 1e-6))); w = w*w   # 刻痕内壁着刻痕色
    else:                                             # 涂色：颜色区域长在表面上
        w = min(1.0, max(0.0, 0.5 - di / (2.0*k))); w = w*w*(3 - 2*w)
        infl = max(infl, w * PF[i, 6])                # 像压上去的一层薄泥片；取 max，重叠处不会叠出棱
    cr += (PF[i, 8] - cr) * w; cg += (PF[i, 9] - cg) * w; cb += (PF[i, 10] - cb) * w; gl += (PF[i, 11] - gl) * w
d -= infl
```
- 涂色图元**不进**光线步进的快速路径（`map_geo` 直接 `continue`），只在算颜色和法线时参与，所以几乎不额外耗时。
- 脸盘的形状 = 涂色椭球和头表面的交线。猴脸用两个眼区涂色加一个下巴区涂色，拼出心形脸。涂色椭球放在头前方，大小要能切到头表面。
- 一开始 inflate 是逐个相减，叠加处会出现一圈“棱”；改成取 max 后就消失了（实测）。
- 眼珠要够凸（z 半径 0.045，前端露出头面约 0.02），否则 smin 权重小于 0.5，眼睛会变成灰色糊团（实测踩过这个坑）。
- 头和身体分两组，组间也用 smin（`kjoin=0.03`）连接，脖子处是平滑过渡，不再有折痕。

---

## 2. 黏土材质着色

### 2.1 光照配置
- **线性空间 + 材质反照率不要太亮**：IQ 建议漫反射颜色在 0.2 左右，要更亮就加灯，别提高材质亮度；gamma 只在最后做一次。阴影半影上色用 `pow(sha, vec3(1,1.2,1.5))`，主光**不乘** AO。来源：https://iquilezles.org/articles/outdoorslighting/ 。代码里颜色在 `prim()` 时就做了 `(c/255)**2.2`。
- **wrap lighting + 明暗交界红晕**：来源 GPU Gems 第 16 章，https://developer.nvidia.com/gpugems/gpugems/part-iii-materials/chapter-16-real-time-approximations-subsurface-scattering 。核心是 `(N·L+wrap)/(1+wrap)`，交界带用 `smoothstep(0,sw,x)*smoothstep(2sw,sw,x)` 叠一点红色。
- **厚度透光**：沿 −n 往表面内侧探两次 SDF。实心处 `d≈-h`，所以贡献约为 0；薄处（耳朵、手）贡献为正。再乘上逆光因子。这一步是我自己的近似，思路同上文 16.3 节的“光在物体里走过的距离”。
- **高光**：参考《Happy Jumping》页面上能看到的一行：`pow(dot(nor,hal),8) * dif * (0.04+0.96*pow(1+dot(hal,rd),5))`，即低指数 + Schlick 菲涅尔。黏土用宽而弱的高光，眼珠用 `gloss=1`，指数 96，亮度高。

```python
# pass_shade 里的核心（每像素；sh/ao/thin 来自 light_terms）
wrap = 0.3
q = (ndl + wrap) / (1 + wrap); dif = max(0.0, q)
sct = min(1.0, max(0.0, q / 0.3)) * min(1.0, max(0.0, (0.6 - q) / 0.3))     # 交界带
fre = 0.04 + 0.96 * (1.0 - max(0.0, -(hx*dx + hy*dy + hz*dz))) ** 5
pw = 6.0 + 90.0 * gl                                                         # 黏土宽高光 / 眼珠窄高光
spec = (0.10 + 1.6 * gl) * ndh ** pw * max(ndl, 0.0) * fre * 6.0
sky = 0.5 + 0.5 * ny; bounce = max(0.0, -ny) * 0.5 + 0.15; rim = (1.0 - ndv) ** 3
back = max(0.0, -(dx*L[0] + dy*L[1] + dz*L[2]))
for c in range(3):
    alb = (cr, cg, cb)[c]
    shc = sh ** (1.0, 1.2, 1.5)[c]                                          # 半影偏暖
    v  = alb * (1.0, 0.86, 0.70)[c] * 2.3 * dif * shc                       # 暖主光
    v += alb * (0.30, 0.10, 0.04)[c] * sct * 1.2 * (0.4 + 0.6 * shc)       # SSS 红晕
    v += alb * (0.42, 0.48, 0.60)[c] * sky * ao * 0.55                      # 冷天光
    v += alb * (0.55, 0.40, 0.28)[c] * bounce * ao * 0.45                   # 地面暖反射
    v += alb * (1.0, 0.75, 0.55)[c] * rim * 0.22 * ao                       # 轮廓光
    v += alb * (1.0, 0.45, 0.30)[c] * thin * (0.35 + 0.65 * back) * 0.8    # 透光
    v += spec * (1.0, 0.95, 0.88)[c] * shc
    img[j, i, c] = v
```

### 2.2 软阴影（IQ 改进版：带内半影）
来源：https://iquilezles.org/articles/rmshadows/ （“Another improvement”：允许光线穿进物体，最后用 −1..1 的 smoothstep）
```python
res = 1.0; st = 0.015; wsz = 0.12                     # wsz = 光源大小，越大越软
for s in range(36):
    hh = map_geo(ox + L[0]*st, oy + L[1]*st, oz + L[2]*st, PI, PF, GR, G0, G1, gm)
    res = min(res, hh / (wsz * st))
    st += min(max(hh, 0.012), 0.25)
    if res < -1.0 or st > 3.0: break
res = max(res, -1.0)
sh = 0.25 * (1.0 + res) * (1.0 + res) * (2.0 - res)
```

### 2.3 指纹 / 捏痕：不规则、无条纹
- fbm 的写法：G=0.5，每个八度频率 ×2，并用 IQ 那个旋转矩阵打散方向（`mat3(0,1.6,1.2,-1.6,0.72,-0.96,-1.2,-0.96,1.28)`）。来源：https://iquilezles.org/articles/fbm/ 、https://iquilezles.org/articles/fbmsdf/
- 2×2×2 邻格随机球（只看 8 个角）的写法也来自 fbmsdf 的 `sdBase`。我用同样的格子来放“指纹按压点”。
- 分层做法参考了 blender-procedural-clay（https://github.com/ignaciojsoler/blender-procedural-clay ）：低频 Noise 做大块不平、Voronoi 做小坑、高频做颗粒，指纹 = 凹坑 + 凸边 + 脊纹，“脊纹只在近处可见，远处淡出而不是闪烁”，每个定格拍重新取一次噪声 = boil。joebinns/clay（https://github.com/joebinns/clay ）的做法类似：指纹凹痕 + Voronoi 压平法线 + Perlin 起伏。

```python
@nb.njit(fastmath=True, inline='always', cache=True)
def hash3(i, j, k):
    h = (i * 374761393 + j * 668265263 + k * 1274126177) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h = h ^ (h >> 16)
    return (h & 0xFFFFFF) / 16777215.0

@nb.njit(fastmath=True, cache=True)
def vnoise(x, y, z):                     # value noise，-1..1，各向同性
    ix, iy, iz = math.floor(x), math.floor(y), math.floor(z)
    fx, fy, fz = x - ix, y - iy, z - iz
    ux, uy, uz = fx*fx*(3-2*fx), fy*fy*(3-2*fy), fz*fz*(3-2*fz)
    i, j, k = int(ix), int(iy), int(iz)
    a = hash3(i,j,k); b = hash3(i+1,j,k); c = hash3(i,j+1,k); d = hash3(i+1,j+1,k)
    e = hash3(i,j,k+1); f = hash3(i+1,j,k+1); g = hash3(i,j+1,k+1); h = hash3(i+1,j+1,k+1)
    x1 = a+(b-a)*ux; x2 = c+(d-c)*ux; x3 = e+(f-e)*ux; x4 = g+(h-g)*ux
    y1 = x1+(x2-x1)*uy; y2 = x3+(x4-x3)*uy
    return (y1+(y2-y1)*uz)*2.0 - 1.0

@nb.njit(fastmath=True, cache=True)
def fbm3(x, y, z, octaves):
    t = 0.0; a = 0.5
    for _ in range(octaves):
        t += a * vnoise(x, y, z)
        nx = 1.60*y + 1.20*z; ny = -1.60*x + 0.72*y - 0.96*z; nz = -1.20*x - 0.96*y + 1.28*z
        x, y, z = nx + 1.7, ny + 9.2, nz + 3.1          # 旋转+×2+平移，打散轴向
        a *= 0.5
    return t

@nb.njit(fastmath=True, cache=True)
def fingerprint(x, y, z, pix):          # pix = 当前像素在世界里的尺寸（≈ pixang*t）
    cs = 0.16; ix, iy, iz = int(math.floor(x/cs)), int(math.floor(y/cs)), int(math.floor(z/cs))
    v = 0.0; period = 0.0075
    ridge_w = min(1.0, max(0.0, (period / (pix + 1e-9) - 2.0) / 2.0))   # 脊纹 < 2px 时淡出（防摩尔纹）
    for di in range(2):
        for dj in range(2):
            for dk in range(2):
                ci, cj, ck = ix+di, iy+dj, iz+dk
                if hash3(ci, cj, ck+77) > 0.45: continue                  # 约 45% 的格子有指纹
                cx = (ci + hash3(ci,cj,ck) - 0.5)*cs; cy = (cj + hash3(ci+11,cj,ck) - 0.5)*cs; cz = (ck + hash3(ci,cj+23,ck) - 0.5)*cs
                R = (0.45 + 0.35*hash3(ci+5,cj+7,ck))*cs
                dx, dy, dz = x-cx, y-cy, z-cz
                r = math.sqrt(dx*dx + dy*dy*1.6 + dz*dz)
                if r < R:
                    q = r/R; fall = (1-q*q)*(1-q*q)
                    v += -0.6*fall                                                       # 按压凹坑
                    v += 0.18*fall*math.cos(6.2831*r/period + 7*hash3(ci,cj,ck+3))*ridge_w  # 同心脊纹
    return v

@nb.njit(fastmath=True, cache=True)
def clay_detail(x, y, z, pix, seed):    # 只加在“求法线”的 SDF 上；seed 每个定格拍 +1 = boil
    x += seed*0.37; y += seed*0.21; z -= seed*0.29
    lump  = fbm3(x*7.0, y*7.0, z*7.0, 3)                                   # 手捏的大块不平
    grain = vnoise(x*160.0, y*160.0, z*160.0)                              # 细颗粒
    return lump*0.0035 + grain*0.00025*min(1.0, 0.004/(pix+1e-9)) + fingerprint(x, y, z, pix)*0.0012
# map_full 末尾： best += clay_detail(...) * (1.0 - min(gloss,1)*0.9)   # 眼珠不加
```
IQ 在 fbmsdf 一文里提醒：把噪声直接加到 SDF 上，得到的已经不是 SDF，振幅一大就会坏。这里振幅不到 4 mm，而且只用于法线，不进步进，所以没有这个问题。实测 nodetail 只省 0.13 s。

### 2.4 色彩分级（后期）
ACES 拟合曲线（Narkowicz，CC0/MIT）：`(x*(2.51x+0.03))/(x*(2.43x+0.59)+0.14)`，后面接 gamma 2.2。来源：https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/ 。作者在 2026 年的评论里说这条曲线对比度偏强；如果觉得太硬，可以把曝光调到 0.7–0.85。
```python
img = np.maximum(img, 0) * 0.85
img = np.clip((img*(2.51*img+0.03)) / (img*(2.43*img+0.59)+0.14), 0, 1) ** (1/2.2)
# 景深 / 柔光的大半径模糊放到 1/4 分辨率做：sigma 24 在 1080×1920 上要十几秒，降采样后只要约 0.3 s
sm = cv2.resize(img, (W//4, H//4), interpolation=cv2.INTER_AREA)
up = lambda a: cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)
b2 = up(cv2.GaussianBlur(sm, (0, 0), 2.3)); glow = up(cv2.GaussianBlur(sm, (0, 0), 6))
img = img*0.9 + glow*0.1                                   # 柔光（屏幕空间“扩散”，GPU Gems 16.4 的思路）
g = img.mean(2, keepdims=True); img = g + (img-g)*1.12     # 饱和度
img = img*np.array([1.02,1.0,0.96]) + np.array([0.012,0.006,0.0])   # 暖调 + 抬黑
```

---

## 3. 提速：做了哪些，各值多少（540×960，2 线程，单 pass 版做消融）

| 去掉的部分 | 耗时 | 说明 |
|---|---|---|
| 全开（单 pass） | 2.94 s | |
| 去阴影 | 1.84 s | **阴影最贵，占约 37%** |
| 去 AO | 2.64 s | AO 占 0.3 s |
| 去表面细节 | 2.81 s | 指纹 / fbm 只进法线，只占 0.13 s |
| 去厚度透光 | 2.80 s | 0.14 s |
| 关逐射线包围球剔除 | 3.57 s | 剔除省 0.63 s（−18%） |
| 关过松弛（ω=1.5） | 2.84 s | **过松弛没有收益**（反而慢约 3%），不采用 |
| 六次中心差分法线（替代四面体） | 3.21 s | 四面体法线省 0.27 s |
| 只做主光线 + 法线 | 1.25 s | 下限参考 |

过松弛的来源：Keinert et al. 2014, *Enhanced Sphere Tracing*，https://kev.town/raymarching-toolkit/media/enhanced_sphere_tracing.pdf （ω∈[1,2)，相邻两个包围球不重叠时回退）。论文里 GPU 上能快 10–20%。这个场景几乎全是近处的大圆物体，所以收益为零。
四面体法线来源：https://iquilezles.org/articles/normalsSDF/ （4 次求值，中心差分精度）。同一篇文章还建议 eps 按像素在世界里的尺寸取，代码里用的是 `e = max(0.0008, pix*0.7)`。

### 3.1 采纳的结构：`clay_fast.py`（4 个 pass）
1. **pass_primary**：先用包围球做逐射线剔除，再走快速 SDF（不带颜色、涂色和细节）步进，命中后算一次完整 SDF（颜色）加四面体法线。结果写进 G-buffer（P、N、C、T）。
2. **pass_light**：只在 2×2 格点上算阴影、AO 和厚度。阴影光线也先和包围球求交，只看会挡到的组。
3. **pass_fill**：其余像素看四个格点的深度（相差 < 2%）和法线（夹角余弦 > 0.9），都相近就做双线性插值；否则（轮廓、接缝）补算。效果相当于深度感知的双边上采样。
4. **pass_shade**：纯逐像素着色，不再求 SDF。

结果：540×960 从 2.94 s 降到 **1.63 s**（−45%）。和单 pass 版的平均像素差是 0.74/255，肉眼看不出。

```python
from clay_fast import Renderer, screen_rect
r = Renderer(720, 1280)                       # 缓冲常驻，帧间复用
img, dep = r.frame(cam, tgt, fov, L, PI, PF, GR, G0, G1, seed=pose)          # 整帧
rect = screen_rect(cam, tgt, fov, 720, 1280, [(cx, cy, cz, rad)])           # 只有某只猴子在动
img, dep = r.frame(cam, tgt, fov, L, PI, PF, GR, G0, G1, seed=pose, rect=rect)  # 只重算矩形，其余沿用上一帧
```

### 3.2 帧间复用静态背景（脏矩形），实测
- 远景 720×1280 整帧 1.61 s。只有一只猴子动时（矩形占画面 29%）为 1.03 s；三只都动（40%）为 1.22 s。
- 收益有限，原因是耗时主要花在角色像素上，背景（墙、地）本来就便宜。适合的场景是：大部分角色静止，只有一两只在说话或动作。前提是相机不动，**一旦加了相机微晃就必须整帧重算**，所以定格风格里可以只在镜头切换时晃动，或者干脆不晃（见第 4 节）。
- 阴影会落到矩形外：`screen_rect` 已经放大 15% 并加了 padding。如果光源很低，要把地面投影点也放进 spheres。

### 3.3 其他要点
- **把场景数组作为参数传给内核**（`PI, PF, GR, G0, G1`）。现在的 `g_clay3d.py` 用全局数组，numba 会在 JIT 时把它们**冻结成常量**，动画每帧改姿态时要么结果不变，要么得重新编译（实测 JIT 要 5–8 s）。传参后加 `cache=True`，编译结果会落盘复用。
- `prange` 必须配合 `@nb.njit(parallel=True)` 才会并行。我的原型一开始漏了，结果单线程 7.08 s，并行后 2.94 s（2 核约 2.4 倍）。
- 快速路径和完整路径分开：步进、阴影、AO 只用 `map_geo`（不带颜色、涂色和细节），颜色和细节只在命中点和法线求值时算。
- 组包围球的距离本身就是下界：`bd > best` 时直接 `best = min(best, bd)` 后跳过。
- 背面跳过阴影：`N·L < −0.35` 时阴影直接取 0（wrap 光照在这里已经是 0）。
- 低分辨率渲染加三次插值放大：540→1080 会软一些、轮廓有锯齿，720→1080 明显好很多。最后的景深和柔光也会掩盖一部分。

### 3.4 分辨率估算（4-pass，三猴近景，最重的情况）
| 渲染分辨率 | 渲染 | 后期（输出 1080×1920） | 每帧合计 | 15 s 视频（on twos，180 帧） |
|---|---|---|---|---|
| 540×960 | 1.63 s | ~0.5 s | ~2.1 s | ~6.5 分钟 |
| **720×1280（推荐）** | 2.91 s | ~0.6–1.4 s | ~3.5–4.3 s | ~11–13 分钟 |
| 1080×1920 | 6.98 s | 1.45 s | ~8.4 s | ~25 分钟 |
远景（角色更小）大约再快 45%：720×1280 只要 1.61 s。

---

## 4. 定格感
- **On twos**：24 fps 输出，每个姿势保持 2 帧，渲染量减半。angrypenguinpng/blender-claymation-skill 的做法是 12 fps on twos、关键帧用 CONSTANT 插值，再加逐帧 boil 和灯光闪烁。它的 `Boil` 类默认抖动幅度是位置 ±0.00025 m、旋转 ±0.004 rad（真实米制微缩场景）。来源：https://github.com/angrypenguinpng/blender-claymation-skill/blob/main/scripts/claylib.py 。blender-procedural-clay 建议只渲染保持帧，再用 ffmpeg 补齐：`-framerate 8 ... -vf fps=24`。
- **Boil（逐拍微变）**，已实测，见 `boil_demo.py` 和 `boil_demo.mp4`：
```python
for pose in range(n_poses):
    PF = PF0.copy()
    PF[:, 0:3] += rng.normal(0, 0.0012, (len(PF), 3)) * (PI[:, 2:3] > 0)          # 角色图元位置微抖（墙地不抖）
    ell = PI[:, 0] == 0
    PF[ell, 3:6] *= 1 + rng.normal(0, 0.006, (ell.sum(), 3)) * (PI[ell, 2:3] > 0)  # 椭球半径 ±0.6%：泥被手碰过
    cam = cam0 + rng.normal(0, 0.004, 3); tgt = tgt0 + rng.normal(0, 0.002, 3)     # 相机微晃（会破坏脏矩形复用）
    img, dep = r.frame(cam, tgt, fov, L, PI, PF, GR, G0, G1, seed=float(pose))     # seed 变 = 指纹/颗粒换位置
    out = post(img * (1 + rng.normal(0, 0.015)), dep, focus)                        # 灯光 ±1.5% 闪烁
    frames += [out, out]                                                            # on twos
```
  实测 540×960 渲染 6 拍（含后期）共 11.9 s。差分图 `boil_diff.png` 显示整个表面纹理和轮廓都有细微跳动。
- 建议：boil 的幅度眼睛周围要小一些，不然表情会“抖神”。可以给五官图元单独设一半幅度。

---

## 5. 现成开源方案：实测
| 方案 | 安装 | 能否离屏 CPU 渲染 | 实测 | 结论 |
|---|---|---|---|---|
| **mitsuba3** 3.9.1（+ drjit 1.5.0） | `pip install --target <local> mitsuba` **成功**，有 aarch64 wheel，占用约 182 MB | `scalar_rgb` 能用。`llvm_ad_rgb` 设置 `DRJIT_LIBLLVM_PATH=/lib/aarch64-linux-gnu/libLLVM.so.19.1` 后 drjit 的基本运算正常，但一渲染（连官方 Cornell box 都不行）就 **Illegal instruction 崩溃** | scalar_rgb：路径追踪球 + 地面，270×480、16 spp 用 1.4 s；540×960、32 spp 用 **8.3 s**，而且有噪点 | 不推荐：不支持 SDF（得先网格化），CPU 路径追踪噪点重、速度慢，向量化的 LLVM 后端在这台机器上崩溃 |
| pyrender 0.1.45 | 能装，纯 Python | **不能**：`PYOPENGL_PLATFORM=egl` 报 “Unable to load EGL library”，`osmesa` 报 “OSMesa: cannot open shared object”。系统里只有 libGL、libGLX、swrast_dri，没有 libEGL 和 libOSMesa | – | 不可用 |
| moderngl 5.13 | aarch64 / py3.12 只有源码包，编译时报 **`No such file or directory: 'g++'`**（沙盒没有编译器） | – | – | 不可用 |
| taichi | `pip download taichi` 报 **No matching distribution**（没有 aarch64 / py3.12 的 wheel） | – | – | 不可用 |
| Blender | 按题意不可用 | – | – | – |

测试脚本是 `mi_test.py`，输出图是 `mi_scalar_rgb.png`。mitsuba 和 drjit 仍留在 `<local>`，不需要的话可以删掉：`rm -rf <local>* <local>*`。

---

## 6. 迁移到 g_clay3d.py 的清单（建议顺序）
1. 场景数组改成参数传入，并加 `cache=True`。图元表增加 `mode / k / gloss` 字段，按 `clay_proto.build()` 的布局：PI = `(type, mode, group)`，PF = `a(3) b(3) r k col(3) gloss`。
2. `sd_prim` 的椭球换成 IQ v2；替换 `smin_w`；拆成 `map_geo` 和 `map_full` 两条路径。
3. `monkey()` 里的脸盘、肚皮、腮红改成 mode 2（涂色），嘴、鼻孔、眯眼、耳窝改成 mode 1（刻），眼珠用 mode 0 的小 k 嵌入。头和身体分两组，组间 `kjoin=0.03`。
4. 删掉正弦 `bump()`，换成 `clay_detail()`，只在法线求值时加。
5. 渲染核心换成 `clay_fast.Renderer` 的 4 个 pass，着色换成第 2.1 节的代码，后期换成第 2.4 节的代码（大半径模糊放到 1/4 分辨率）。
6. 渲染 720×1280，放大到 1080×1920；动画 on twos，boil 的 seed 跟着拍号走。

## 7. 来源（均为本次实际打开过的页面）
- IQ smooth minimum：https://iquilezles.org/articles/smin/
- IQ 椭球距离：https://iquilezles.org/articles/ellipsoids/
- IQ SDF 函数和运算（smooth subtraction、椭球下界、位移的注意事项）：https://iquilezles.org/articles/distfunctions/
- IQ SDF 法线（四面体）：https://iquilezles.org/articles/normalsSDF/
- IQ 软阴影（改进版和内半影版）：https://iquilezles.org/articles/rmshadows/
- IQ fBM SDF 细节：https://iquilezles.org/articles/fbmsdf/
- IQ fBM：https://iquilezles.org/articles/fbm/
- IQ 三灯户外光照（线性空间、反照率约 0.2、半影上色、主光不乘 AO）：https://iquilezles.org/articles/outdoorslighting/
- IQ《Happy Jumping》Shadertoy（smax 刻嘴、高光公式；许可证禁止复用代码）：https://www.shadertoy.com/view/3lsSzf
- GPU Gems 第 16 章，次表面散射近似（wrap 光照、交界红晕、厚度）：https://developer.nvidia.com/gpugems/gpugems/part-iii-materials/chapter-16-real-time-approximations-subsurface-scattering
- Keinert et al. 2014, Enhanced Sphere Tracing：https://kev.town/raymarching-toolkit/media/enhanced_sphere_tracing.pdf
- Narkowicz ACES 拟合曲线：https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/
- blender-procedural-clay（分层噪声、指纹、boil）：https://github.com/ignaciojsoler/blender-procedural-clay
- joebinns/clay（Unity 黏土 shader 拆解）：https://github.com/joebinns/clay
- blender-claymation-skill claylib.py（12 fps on twos、Boil 参数）：https://github.com/angrypenguinpng/blender-claymation-skill/blob/main/scripts/claylib.py

## 8. 本目录产物
- `clay_proto.py`：完整的 SDF、材质和单 pass 渲染原型，可以直接运行：`python3 clay_proto.py 540 960 [noshadow …]`
- `clay_fast.py`：4-pass 提速版、`Renderer` 和脏矩形 `screen_rect`
- `bench.py`（消融）、`bench_fast.py`、`bench_wide.py`（分辨率和脏矩形）、`boil_demo.py`、`mi_test.py`
- 效果图：`fast_1080x1920.png`（近景，1080 原生）、`fast_720x1280.png`、`wide_720x1280.png`（远景）、`proto_540x960_full.png`；定格演示：`boil_demo.mp4`、`boil_diff.png`
- `v_*.png`、`G_test_small.png` 是检查用的缩略图或裁切，可以删除
