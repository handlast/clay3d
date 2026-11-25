# 《动物打工人 No.01》新增黏土资产 → clay3d 仓库对应目录

本目录 `macaque3d/clay/` 与仓库 `clay3d-repo/` 同结构，把各子目录里的文件原样拷到仓库同名目录即可（不要拷 `__pycache__/`）。
每个模块开头都有同一段引导代码：把「仓库根」和「仓库根/engine」加进 sys.path（按文件自身位置推算，不写死绝对路径），
另外可用环境变量 `CLAY_ENGINE_DIR` 指定 clay_proto.py 所在目录（本地 staging 时指向 ../research）。

| 文件 | 进仓库 | 内容 |
|---|---|---|
| engine/clay_build.py | engine/ | `arr()` 打包 PRIMS/GROUPS 为 render() 数组，`reset()` 清场景 |
| characters/macaque_poses.py | characters/ | `monkey2()`：Q 版阿萨姆猕猴扩展版（y 偏移、转头 hyaw、歪头 hroll、squash、工牌 badge、表情 happy/angry/wow/look/worry），`POSE` 手臂姿势表、`to_local()` 手伸到世界坐标点、`armlerp()` 姿势过渡 |
| props/basics.py | props/ | `backdrop()` 背景墙、`floor()` 地板 |
| props/jungle_plants.py | props/ | `tree()` 树、`vine()` 藤（可摆）、`bush()` 灌木、`fern()` 蕨（草地即 floor 换绿色） |
| props/links.py | props/ | `link()` 直线关系线、`arc_link()` 拱形关系线（按 k 长出） |
| props/charts.py | props/ | `stopwatch()` 秒表、`bar()` 柱状图立柱、`steps()` 台阶 |
| props/office_props.py | props/ | `desk()` 办公桌、`mug()` 咖啡杯 |
| scenes/jungle.py | scenes/ | `jungle(t)` 丛林场景；直接运行出样张 jungle_G.png |
| renders/jungle_G.png、renders/office_set_G.png | renders/ | 两个场景脚本在仓库结构下直接运行出的样张（已验证无需任何环境变量即可 import 仓库 engine/clay_proto.py） |
| scenes/office_set.py | scenes/ | `office(t, wall)` 办公室布景（可换墙色、走动挂钟）；直接运行出样张 office_set_G.png |

不进仓库（作品专用）：`macaque3d/film.py`（13 个镜头 + 2D 字幕层）、`world.py`（作品内兼容层）、`cues.py / lines.py / vo.py / music.py / render.sh / cover.py`。
`engine/clay_proto.py` 没有改动。
