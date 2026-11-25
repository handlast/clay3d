#!/bin/bash
# 后台：逐镜穿模约束（选方向 → 逐拍需求 → 包络 → 写 clear_track.json），再逐镜复查
cd /workspace/work/clownfish3d; export PYTHONPATH=/workspace/.pylib
for n in ${@:-big1 where cam q big2 care guard fight calm card end}; do nice -n 5 python3 film.py clr $n >> clear_log.txt 2>&1; done
for n in hook ${@:-big1 where cam q big2 care guard fight calm card end}; do nice -n 5 python3 film.py clrv $n >> clear_log.txt 2>&1; done
echo ALL_CLR_DONE >> clear_log.txt
