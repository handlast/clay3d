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

## Vibe知识大赏 作品归档（2026-11 新增）
抖音「Vibe知识大赏」全部作品的代码、可复用模块和最终音频也归档在本仓库。上面的黏土引擎目录（engine/ characters/ scenes/ props/ demos/ renders/ docs/）保持原样，归档内容放在下面四个新的顶层目录里：

- `INDEX.md`：作品索引，每个作品一行（作品名、中文片名、系列、日期、代码与音频路径）。
- `code/<系列>/<作品名>/`：每条片子的脚本（cues、film、music、cover、publish、script 等 .py/.sh/.md/.json，以及字幕和旁白文本）。系列：`新物种`、`动物打工人`、`超级士兵`、`脑洞-植物`（即「脑洞/植物」）、`其他`。脚本里的 `/workspace/...` 绝对路径是制作环境的路径，换环境运行时要改。
- `models/`：从各作品里抽出来的可复用 2D 角色、2.5D 场景和渲染底座（说明见 `models/README.md`）。黏土 3D 模块不在这里重复，直接用上面的 engine/ 等目录。
- `audio/<作品名>/`：最终 BGM 与旁白（FLAC 无损）。中间切片、旧版、音效分轨不收录。
- `shared/`：共用工具（采样器、爆音自检）、调研文档、画风样张。第三方音色库（Salamander、GeneralUser GS）和 Piper 模型不收录，来源与许可写在 `shared/README.md`。

不收录：成片 mp4、png 截图与帧图、segs 分段、tests、`__pycache__`、纹理 / 模拟缓存（.npy/.npz）、字体文件、论文全文。
