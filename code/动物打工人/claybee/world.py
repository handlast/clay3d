# 《动物打工人 No.04》3D 黏土世界：直接用仓库 work/clay3d-repo（engine/ characters/ props/ scenes/）
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.environ.get("CLAY_REPO") or os.path.normpath(os.path.join(_HERE, "..", "clay3d-repo"))
for _p in (_REPO, os.path.join(_REPO, "engine")):
    if _p not in sys.path: sys.path.insert(0, _p)
import clay_proto as cp
import clay_face as cf
from clay_build import arr, reset
from characters.bumblebee import bumblebee
from props.hive_props import brood, honey_pot, lab_box, flower, thermo_cam
from props.anemone import thermometer
from props.office_props import desk, mug
from scenes.hive import hive, meadow
from props.basics import backdrop, floor
