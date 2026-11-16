# clay3d · 程序化 3D 黏土动画

用 Python + numba 做 SDF 光线步进，渲染出黏土定格风格的 3D 画面。不用建模软件，不用 GPU。这是抖音「动物打工人」系列的画风引擎。

![office](renders/office_G.png)

## 目录
- `engine/`：渲染内核（`clay_build.py` 打包场景数组）。`clay_proto.py` 包含图元、平滑并集与雕刻、黏土着色（wrap 光、SSS、指纹凹凸）、软阴影、AO、景深后期；`clay_fast.py` 是 Renderer 类；`clay_face.py` 脸部 2× 超采样、脸不进景深；`clearance.py` 穿模约束（角色与其他物体的 SDF 间距、自动让位轨迹）。
- `characters/`：角色（Q 版大头猴、Q 版小丑鱼）。
- `scenes/`：场景，`office.py` 办公室样张、`office_set.py` 可动办公室布景、`jungle.py` 丛林、`reef.py` 珊瑚礁海底。
- `props/`：道具（办公、图表、丛林植物、海葵与体温计、水下摄像机）。
- `demos/`：定格抖动（on twos boil）演示。
- `renders/`：样张与成片截图（`animal_worker_01_*` = 动物打工人 No.01，`animal_worker_03_*` = No.03）。
- `docs/`：技术调研。

## 运行
```bash
pip install numba numpy opencv-python
cd scenes && python3 office.py   # 720×1280 渲染后放大到 1080×1920，CPU 约 6 s/帧
```
