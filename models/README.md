# models/ · 可复用的角色、场景、引擎模块（各作品抽出）

这里放从各作品里抽出来、可以复用的模块。原文件仍完整保留在 `code/<系列>/<作品名>/` 里，那份才是能直接跑的；这里只是按类型归拢，方便查找。

**黏土 3D（clay3d）引擎不在这里**：它在仓库根目录的 `engine/`、`characters/`、`props/`、`scenes/`，这里不重复复制。

## characters/
- `<作品>_chars.py`：2D 扁平卡通角色（Pillow 逐帧绘制，带表情）。`frog_chars.py` 和 mantis、webbug 两个作品里的 chars.py 完全相同，只放了一份。
- `mantis_mchars.py`：螳螂专用角色。
- `ghostfrog_chars.py`：叶中幽灵蛙（Oreobates foliaspectrum）——正面坐姿 + 俯视两种视角、可分半上色的双色虹膜 `iris()`、落叶堆、树蕨/竹子、头灯科学家、牛与牛蹄印、卵/蝌蚪/一元硬币。
- 黏土 3D 角色在 `characters/`（根目录）：`macaque_poses.py`（Q 版大头猴）、`clownfish.py`（Q 版小丑鱼）。

## scenes/
- `macaque3d_world.py`：动物打工人 No.01 的黏土场景装配，依赖根目录 `scenes/office_set.py`、`scenes/jungle.py`。
- `bridge_world.py` / `zhanshou_world.py` / `border_world.py`：蚂蚁剧情的 2.5D 微距渲染器（透视地面、道具、蚂蚁、景深、调色），三个版本各不相同。
- `bridge_scene.py` / `zhanshou_scene.py`：《断桥》《斩首》共用的场景件（蚂蚁记录、叶桥、水沟、雨、字幕叠加）。
- 黏土场景在根目录 `scenes/`：`office.py`、`office_set.py`、`jungle.py`、`reef.py`。

## props/
- 这次没有新增道具；黏土道具都在根目录 `props/`：`basics.py`、`charts.py`、`jungle_plants.py`、`links.py`、`office_props.py`、`anemone.py`、`camera_rig.py`。

## engine/
- `flat2d_base.py`：2D 扁平风通用底座（画布、字体、配色、字幕）。50 多个作品里都是同一份。
- `fx.py`：2D 特效（粒子、抖动、闪白等），也是 50 多个作品共用的同一份；`fx_v1.py` 是早期版（germ、horse、mimosa、roach 用）。
- `easing.py`：缓动与运动辅助函数（Manim / Motion Canvas 手法蒸馏）。
- `doodle_base.py` + `doodle.py`：简笔画风底座（「如果」系列，以及 dance、ufo 用的 base）。
- `grape_base.py`、`york_base.py`：葡萄、超级士兵 No.02 的变体底座。
- `ant_tex.py`：程序化地面纹理（混凝土、泥、沙、土，结果缓存为 .npy，缓存文件不入库，运行时自动重新生成）。
- `bridge_ant_sim.py`、`border_ant_sim.py`：阿根廷蚁的群体行为模拟（移动、接触、打斗、撤退）。
- `border_maps.py`：《无声的边境》地图绘制。
