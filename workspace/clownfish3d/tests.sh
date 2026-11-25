#!/bin/bash
# 后台：每镜一帧（含脸部 2× 裁切）+ 穿模高风险时段连续 6 拍小样；每条命令 ≤8 帧，走渲染锁
cd /workspace/work/clownfish3d; export PYTHONPATH=/workspace/.pylib
run() { flock /tmp/render.lock timeout 115 python3 film.py faces "$@"; }
run 1.6 4.8 9.6 14.0 17.0
run 20.0 24.5 28.6 33.5
run 39.0 44.6 51.0 57.5
run 1.0 1.07 1.13 1.2 1.27 1.33
run 24.0 24.07 24.13 24.2 24.27 24.33
run 28.4 28.47 28.53 28.6 28.67 28.73
run 28.8 28.87 28.93 29.0 29.07 29.13
run 33.0 33.07 33.13 33.2 33.27 33.33
echo TESTS_DONE
