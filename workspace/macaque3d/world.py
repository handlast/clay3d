# 《动物打工人 No.01》3D 黏土世界：兼容层。图元已拆进 clay/（与 GitHub 仓库 clay3d 同结构：engine/ characters/ props/ scenes/）
# 这里只负责把 clay/ 放上 sys.path 并统一导出，film.py 仍可 `import world as Wd`。不写死绝对路径：
#   引擎 clay_proto.py 的位置依次找：环境变量 CLAY_ENGINE_DIR → clay/engine/ → 本目录旁边的 ../research/
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
_CLAY = os.path.join(_HERE, "clay")
if not os.environ.get("CLAY_ENGINE_DIR") and not os.path.exists(os.path.join(_CLAY, "engine", "clay_proto.py")):
    os.environ["CLAY_ENGINE_DIR"] = os.path.normpath(os.path.join(_HERE, "..", "research"))
for _p in (_CLAY, os.path.join(_CLAY, "engine"), os.environ.get("CLAY_ENGINE_DIR")):
    if _p and _p not in sys.path: sys.path.insert(0, _p)
import clay_proto as cp
from clay_build import arr, reset
from characters.macaque_poses import monkey2, to_local, armlerp, POSE, BADGE_C, LANY, GOLDC
from props.basics import backdrop, floor
from props.jungle_plants import tree, vine, bush, fern, LEAF1, LEAF2, LEAF3, TRUNK
from props.links import link, arc_link
from props.charts import stopwatch, bar, steps
from props.office_props import desk, mug
from scenes.jungle import jungle
from scenes.office_set import office
